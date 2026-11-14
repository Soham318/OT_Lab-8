r"""
Dynamic Programming Knapsack Solver
Track B: Discrete Optimization
Assignment 8 - Optimize Anything

Solves 0/1 Knapsack using classic 2D dynamic programming table with
exact backtracking reconstruction.

State Definition:
    DP[i, w]: Maximum value attainable using a subset of items {1, ..., i}
              with total weight not exceeding w.

Recurrence Relation:
    DP[i, w] = DP[i-1, w]                                    if w < w_i
    DP[i, w] = max(DP[i-1, w], DP[i-1, w - w_i] + v_i)       if w >= w_i

Base Cases:
    DP[0, w] = 0   for all w in [0, W]
    DP[i, 0] = 0   for all i in [0, n]

Complexity:
    Time Complexity:  O(n * W)  (Pseudo-polynomial)
    Space Complexity: O(n * W)
"""

import time
import numpy as np
from track_b_discrete_optimization.src.problem import KnapsackProblem, KnapsackSolution


class DPKnapsackSolver:
    """
    Exact Dynamic Programming Solver with Backtracking Reconstruction.
    Requires integer weights and integer capacity.
    """

    def __init__(self, name: str = "Dynamic Programming (Exact)"):
        self.name = name

    def solve(self, problem: KnapsackProblem) -> KnapsackSolution:
        t0 = time.perf_counter()
        n = problem.n_items
        W = int(np.round(problem.capacity))
        weights_int = np.round(problem.weights).astype(int)
        values = problem.values

        # Allocate (n + 1) x (W + 1) DP table
        dp_table = np.zeros((n + 1, W + 1), dtype=np.float64)

        # Populate DP table
        for i in range(1, n + 1):
            w_i = weights_int[i - 1]
            v_i = values[i - 1]
            for w in range(W + 1):
                if w < w_i:
                    dp_table[i, w] = dp_table[i - 1, w]
                else:
                    take = dp_table[i - 1, w - w_i] + v_i
                    skip = dp_table[i - 1, w]
                    dp_table[i, w] = take if take > skip else skip

        # Backtracking item reconstruction
        selected = np.zeros(n, dtype=int)
        curr_w = W
        for i in range(n, 0, -1):
            w_i = weights_int[i - 1]
            # If value differs from the row above, item i-1 was included
            if dp_table[i, curr_w] != dp_table[i - 1, curr_w]:
                selected[i - 1] = 1
                curr_w -= w_i

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        total_val, total_w, feas = problem.evaluate(selected)

        return KnapsackSolution(
            solver_name=self.name,
            selected_items=selected,
            total_value=total_val,
            total_weight=total_w,
            capacity=problem.capacity,
            is_feasible=feas,
            execution_time_ms=elapsed_ms,
            optimality_gap_percent=0.0,
            extra_metadata={
                "table_cells": (n + 1) * (W + 1),
                "dp_optimal_value": float(dp_table[n, W]),
                "memory_kb": round(((n + 1) * (W + 1) * 8) / 1024.0, 2)
            }
        )

