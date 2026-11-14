r"""Compiler Pass Selection Optimization Problem.

Formulates compiler pass selection as a Binary Integer Linear Program (BILP):
    \max_{x \in \{0, 1\}^m} \sum_{i=1}^m \left( w_{rt} B_i^{rt} + w_{sz} B_i^{sz} \right) x_i - \sum_{i=1}^m w_{cmp} C_i^{cmp} x_i
    \text{subject to } \sum_{i=1}^m C_i^{cmp} x_i \le C_{budget}
                     \text{and dependency constraints between passes.}

Candidate Passes:
    0: CF (Constant Folding)
    1: CP (Constant Propagation)
    2: SR (Strength Reduction)
    3: CSE (Common Subexpression Elimination)
    4: DCE (Dead Code Elimination)
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


class PassSelectionProblem:
    """Mathematical optimization model for compiler pass selection."""

    PASS_KEYS = ["CF", "CP", "SR", "CSE", "DCE"]
    PASS_NAMES = {
        "CF": "Constant Folding",
        "CP": "Constant Propagation",
        "SR": "Strength Reduction",
        "CSE": "Common Subexpression Elimination",
        "DCE": "Dead Code Elimination",
    }

    def __init__(
        self,
        runtime_benefits: Optional[Dict[str, float]] = None,
        size_benefits: Optional[Dict[str, float]] = None,
        compile_costs: Optional[Dict[str, float]] = None,
        w_runtime: float = 1.0,
        w_size: float = 0.5,
        w_compile: float = 0.2,
    ):
        # Default empirical profile (relative units)
        self.runtime_benefits = runtime_benefits or {
            "CF": 12.0,
            "CP": 10.0,
            "SR": 8.0,
            "CSE": 15.0,
            "DCE": 5.0,
        }
        self.size_benefits = size_benefits or {
            "CF": 8.0,
            "CP": 4.0,
            "SR": 3.0,
            "CSE": 10.0,
            "DCE": 14.0,
        }
        self.compile_costs = compile_costs or {
            "CF": 1.5,
            "CP": 2.0,
            "SR": 1.0,
            "CSE": 3.5,
            "DCE": 2.5,
        }
        self.w_runtime = w_runtime
        self.w_size = w_size
        self.w_compile = w_compile

    def compute_objective_coefficients(self) -> np.ndarray:
        """Net score for each pass: w_rt * B_rt + w_sz * B_sz - w_cmp * C_cmp."""
        coeffs = []
        for key in self.PASS_KEYS:
            net_score = (
                self.w_runtime * self.runtime_benefits[key]
                + self.w_size * self.size_benefits[key]
                - self.w_compile * self.compile_costs[key]
            )
            coeffs.append(net_score)
        return np.array(coeffs, dtype=float)

    def solve_milp(self, compile_time_budget: float = 7.0) -> Dict[str, Any]:
        """Solve Pass Selection via SciPy MILP.

        Constraints:
            1. Total compile time <= compile_time_budget
            2. Constant Folding synergy with Constant Propagation: x_CF - x_CP <= 0.5
               (CP strongly enables CF to find constants)
        """
        n_passes = len(self.PASS_KEYS)
        # SciPy minimizes, so negate objective for maximization
        net_coeffs = self.compute_objective_coefficients()
        c = -net_coeffs

        # Constraint 1: Compile time budget sum C_i * x_i <= compile_time_budget
        cost_row = [self.compile_costs[k] for k in self.PASS_KEYS]

        A = [cost_row]
        lhs = [0.0]
        rhs = [compile_time_budget]

        # Constraint 2: Synergy/dependency: Constant Propagation enhances CF
        # If CF is selected without CP, its utility is dampened (modeled as x_CF <= x_CP + 0.5)
        # i.e., x_CF - x_CP <= 0
        dep_row = [0.0] * n_passes
        dep_row[self.PASS_KEYS.index("CF")] = 1.0
        dep_row[self.PASS_KEYS.index("CP")] = -1.0
        A.append(dep_row)
        lhs.append(-np.inf)
        rhs.append(0.0)  # CF requires CP

        constraints = LinearConstraint(A, lhs, rhs)
        bounds = Bounds(lb=np.zeros(n_passes), ub=np.ones(n_passes))
        integrality = np.ones(n_passes)  # strictly binary integers

        res = milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints)

        if not res.success:
            raise RuntimeError(f"MILP solver failed: {res.status}")

        chosen_binary = np.round(res.x).astype(int)
        selected_passes = [self.PASS_KEYS[i] for i, b in enumerate(chosen_binary) if b == 1]
        total_compile_cost = sum(self.compile_costs[k] for k in selected_passes)
        total_runtime_benefit = sum(self.runtime_benefits[k] for k in selected_passes)
        total_size_benefit = sum(self.size_benefits[k] for k in selected_passes)
        net_objective = float(-res.fun)

        return {
            "solver": "scipy_milp",
            "compile_time_budget": compile_time_budget,
            "chosen_binary": chosen_binary.tolist(),
            "selected_passes": selected_passes,
            "total_compile_cost": total_compile_cost,
            "total_runtime_benefit": total_runtime_benefit,
            "total_size_benefit": total_size_benefit,
            "net_objective_value": net_objective,
        }

    def solve_exhaustive(self, compile_time_budget: float = 7.0) -> Dict[str, Any]:
        """Exhaustively enumerate all 2^5 = 32 pass subsets to verify global optimality."""
        n_passes = len(self.PASS_KEYS)
        best_val = -float("inf")
        best_subset = []
        best_binary = []

        all_evaluations = []

        for mask in range(1 << n_passes):
            binary = [(mask >> i) & 1 for i in range(n_passes)]
            passes = [self.PASS_KEYS[i] for i, b in enumerate(binary) if b == 1]

            cost = sum(self.compile_costs[k] for k in passes)
            if cost > compile_time_budget:
                continue

            # Check dependency: CF requires CP
            has_cf = "CF" in passes
            has_cp = "CP" in passes
            if has_cf and not has_cp:
                continue

            val = sum(
                (
                    self.w_runtime * self.runtime_benefits[k]
                    + self.w_size * self.size_benefits[k]
                    - self.w_compile * self.compile_costs[k]
                )
                for k in passes
            )

            all_evaluations.append({
                "passes": passes,
                "cost": cost,
                "value": val,
            })

            if val > best_val:
                best_val = val
                best_subset = passes
                best_binary = binary

        return {
            "solver": "exhaustive_search",
            "compile_time_budget": compile_time_budget,
            "best_binary": best_binary,
            "selected_passes": best_subset,
            "best_value": best_val,
            "total_feasible_subsets": len(all_evaluations),
        }
