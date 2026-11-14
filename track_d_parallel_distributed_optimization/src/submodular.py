r"""Submodular Optimization Module: Maximum Coverage Problem.

Implements monotone submodular set function maximization under a cardinality constraint:
    max_{A \subseteq S, |A| \le k} f(A) = |\bigcup_{i \in A} S_i|

Provides:
- Diminishing returns property verification: f(A \cup {e}) - f(A) >= f(B \cup {e}) - f(B) for A \subseteq B
- Greedy selection algorithm with (1 - 1/e) approximation guarantee
- Exhaustive combinatorial baseline for exact optimality benchmarking
"""

import itertools
import math
import time
from typing import Any, Dict, List, Set, Tuple
import numpy as np


class MaximumCoverageProblem:
    r"""Maximum Coverage problem representation and solvers.

    Given a universe of elements U = {0, 1, ..., n-1} and a collection of
    subsets S = {S_0, S_1, ..., S_{m-1}}, choose at most k subsets to maximize
    the number of covered elements:
        f(A) = | \bigcup_{i \in A} S_i |
    """

    def __init__(self, universe_size: int, subsets: List[Set[int]]):
        if universe_size <= 0:
            raise ValueError(f"universe_size must be positive, got {universe_size}")
        if not subsets:
            raise ValueError("subsets list cannot be empty")

        self.universe_size = universe_size
        self.subsets = [set(s) for s in subsets]
        self.num_subsets = len(self.subsets)

        # Validate elements in subsets
        for idx, s in enumerate(self.subsets):
            for elem in s:
                if not (0 <= elem < universe_size):
                    raise ValueError(
                        f"Element {elem} in subset {idx} is outside universe [0, {universe_size-1}]"
                    )

    def evaluate(self, selected_indices: Set[int] | List[int]) -> int:
        """Evaluate coverage function f(A) = |Union_{i in A} S_i|."""
        if not selected_indices:
            return 0
        covered: Set[int] = set()
        for idx in selected_indices:
            if not (0 <= idx < self.num_subsets):
                raise ValueError(f"Subset index {idx} out of range [0, {self.num_subsets-1}]")
            covered.update(self.subsets[idx])
        return len(covered)

    def marginal_gain(self, candidate_idx: int, current_selection: Set[int]) -> int:
        """Compute marginal gain Delta(e | A) = f(A U {e}) - f(A)."""
        if not (0 <= candidate_idx < self.num_subsets):
            raise ValueError(f"Candidate index {candidate_idx} out of range")
        if candidate_idx in current_selection:
            return 0
        current_covered: Set[int] = set()
        for idx in current_selection:
            current_covered.update(self.subsets[idx])
        # Elements in candidate not already covered
        new_elements = self.subsets[candidate_idx] - current_covered
        return len(new_elements)

    def check_diminishing_returns(
        self, candidate_e: int, set_A: Set[int], set_B: Set[int]
    ) -> Tuple[bool, int, int]:
        """Verify diminishing returns: A subset of B => Delta(e|A) >= Delta(e|B).

        Returns:
            (satisfies_property, delta_A, delta_B)
        """
        if not set_A.issubset(set_B):
            raise ValueError("set_A must be a subset of set_B")
        if candidate_e in set_B:
            raise ValueError("candidate_e cannot already be in set_B")

        delta_A = self.marginal_gain(candidate_e, set_A)
        delta_B = self.marginal_gain(candidate_e, set_B)
        satisfies = delta_A >= delta_B
        return satisfies, delta_A, delta_B

    def verify_submodularity(
        self, num_samples: int = 100, seed: int = 42
    ) -> Tuple[bool, float]:
        """Empirically test diminishing returns across random subsets A subset of B.

        Returns:
            (is_submodular, compliance_rate)
        """
        rng = np.random.default_rng(seed)
        all_indices = list(range(self.num_subsets))
        valid_checks = 0
        total_checks = 0

        for _ in range(num_samples):
            # Sample random subset B
            k_b = rng.integers(1, max(2, self.num_subsets))
            b_list = list(rng.choice(all_indices, size=k_b, replace=False))
            set_B = set(b_list)

            # Sample random subset A subset of B
            if len(set_B) > 0:
                k_a = rng.integers(0, len(set_B))
                set_A = set(rng.choice(list(set_B), size=k_a, replace=False))
            else:
                set_A = set()

            # Choose candidate e not in B
            available_candidates = [idx for idx in all_indices if idx not in set_B]
            if not available_candidates:
                continue

            e = rng.choice(available_candidates)
            satisfies, _, _ = self.check_diminishing_returns(e, set_A, set_B)
            total_checks += 1
            if satisfies:
                valid_checks += 1

        compliance_rate = valid_checks / total_checks if total_checks > 0 else 1.0
        return (compliance_rate == 1.0), compliance_rate

    def solve_greedy(self, k: int) -> Dict[str, Any]:
        """Solve Maximum Coverage using the classic Greedy heuristic.

        At each step t in {1, ..., k}:
            e^* = argmax_{e not in A} Delta(e | A)
            A <- A U {e^*}

        Returns dictionary with solution details.
        """
        if k <= 0 or k > self.num_subsets:
            raise ValueError(f"k must be in range [1, {self.num_subsets}], got {k}")

        start_time = time.perf_counter()
        selected: Set[int] = set()
        covered: Set[int] = set()
        marginal_gains: List[int] = []
        coverage_history: List[int] = [0]

        for step in range(k):
            best_subset = -1
            best_gain = -1

            for candidate in range(self.num_subsets):
                if candidate in selected:
                    continue
                gain = len(self.subsets[candidate] - covered)
                if gain > best_gain:
                    best_gain = gain
                    best_subset = candidate

            if best_subset == -1 or best_gain <= 0:
                # No more positive coverage gains possible
                break

            selected.add(best_subset)
            covered.update(self.subsets[best_subset])
            marginal_gains.append(best_gain)
            coverage_history.append(len(covered))

        runtime_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "selected_subsets": sorted(list(selected)),
            "coverage_count": len(covered),
            "coverage_fraction": len(covered) / self.universe_size,
            "cardinality": len(selected),
            "k_limit": k,
            "marginal_gains": marginal_gains,
            "coverage_history": coverage_history,
            "runtime_ms": runtime_ms,
        }

    def solve_exact(self, k: int) -> Dict[str, Any]:
        """Solve Maximum Coverage exactly via exhaustive combinatorial search over C(m, k).

        Only recommended for small instances (e.g. m <= 22, k <= 5).
        """
        if k <= 0 or k > self.num_subsets:
            raise ValueError(f"k must be in range [1, {self.num_subsets}], got {k}")

        num_combinations = math.comb(self.num_subsets, k)
        if num_combinations > 250_000:
            raise ValueError(
                f"Combinatorial space C({self.num_subsets}, {k}) = {num_combinations} "
                "is too large for brute force enumeration (> 250,000)."
            )

        start_time = time.perf_counter()
        best_coverage = -1
        best_combination: Tuple[int, ...] = ()

        for combo in itertools.combinations(range(self.num_subsets), k):
            covered: Set[int] = set()
            for idx in combo:
                covered.update(self.subsets[idx])
            cov_len = len(covered)
            if cov_len > best_coverage:
                best_coverage = cov_len
                best_combination = combo
                if best_coverage == self.universe_size:
                    # Early exit if 100% universe coverage achieved
                    break

        runtime_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "optimal_subsets": list(best_combination),
            "optimal_coverage": best_coverage,
            "coverage_fraction": best_coverage / self.universe_size,
            "k_limit": k,
            "combinations_evaluated": num_combinations,
            "runtime_ms": runtime_ms,
        }

    @staticmethod
    def theoretical_bound(exact_optimal_value: float) -> float:
        """Theoretical lower bound for greedy on monotone submodular functions: (1 - 1/e) * f^*."""
        return (1.0 - 1.0 / math.e) * exact_optimal_value

    @classmethod
    def create_synthetic_instance(
        cls,
        universe_size: int = 100,
        num_subsets: int = 20,
        density: float = 0.15,
        seed: int = 42,
    ) -> "MaximumCoverageProblem":
        """Generate a reproducible synthetic Maximum Coverage problem instance."""
        rng = np.random.default_rng(seed)
        subsets: List[Set[int]] = []

        for _ in range(num_subsets):
            # Each subset contains each element with probability equal to density
            mask = rng.random(universe_size) < density
            chosen = set(np.where(mask)[0])
            if not chosen:
                # Guarantee non-empty
                chosen.add(int(rng.integers(0, universe_size)))
            subsets.append(chosen)

        return cls(universe_size, subsets)

