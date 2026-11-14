r"""
Greedy Knapsack Solver
Track B: Discrete Optimization
Assignment 8 - Optimize Anything

Heuristic:
  Sorts items by value-to-weight density ratio:
      r_i = v_i / w_i
  Iteratively packs items with highest density until no further items fit.
Time Complexity: O(n log n)
Space Complexity: O(n)
"""

import time
import numpy as np
from track_b_discrete_optimization.src.problem import KnapsackProblem, KnapsackSolution


class GreedyKnapsackSolver:
    """
    Greedy Value-to-Weight Density Heuristic Solver.
    Demonstrates polynomial-time approximation for discrete combinatorial knapsack.
    """

    def __init__(self, name: str = "Greedy Density Heuristic"):
        self.name = name

    def solve(self, problem: KnapsackProblem) -> KnapsackSolution:
        """
        Execute greedy density heuristic:
          1. Calculate efficiency ratios r_i = v_i / w_i.
          2. Sort items descending by r_i.
          3. Pack items greedily while weight <= capacity.
        """
        t0 = time.perf_counter()
        n = problem.n_items
        ratios = problem.values / problem.weights

        # Sort indices descending by ratio (breaking ties by larger value)
        sorted_indices = sorted(
            range(n),
            key=lambda i: (ratios[i], problem.values[i]),
            reverse=True
        )

        selected = np.zeros(n, dtype=int)
        current_weight = 0.0
        current_value = 0.0

        for idx in sorted_indices:
            w_i = problem.weights[idx]
            v_i = problem.values[idx]
            if current_weight + w_i <= problem.capacity:
                selected[idx] = 1
                current_weight += w_i
                current_value += v_i

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return KnapsackSolution(
            solver_name=self.name,
            selected_items=selected,
            total_value=current_value,
            total_weight=current_weight,
            capacity=problem.capacity,
            is_feasible=current_weight <= problem.capacity,
            execution_time_ms=elapsed_ms,
            extra_metadata={
                "sorted_ratios": [float(ratios[i]) for i in sorted_indices],
                "packed_order": [int(i) for i in sorted_indices if selected[i] == 1],
                "remaining_capacity": float(problem.capacity - current_weight)
            }
        )

