r"""
Branch-and-Bound Knapsack Solver
Track B: Discrete Optimization
Assignment 8 - Optimize Anything

Solves 0/1 Knapsack using transparent tree search with Linear Programming (LP)
relaxation upper bounds (Dantzig fractional knapsack).
Shows explicit branching decisions, bounding, and pruning events.
"""

import time
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from track_b_discrete_optimization.src.problem import KnapsackProblem, KnapsackSolution


class BranchAndBoundSolver:
    """
    Transparent Branch-and-Bound Solver for 0/1 Knapsack.
    Uses continuous LP relaxation upper bounds and best-first search.
    """

    def __init__(self, max_nodes: int = 100000, name: str = "Branch-and-Bound"):
        self.max_nodes = max_nodes
        self.name = name

    def solve(self, problem: KnapsackProblem) -> KnapsackSolution:
        t0 = time.perf_counter()
        n = problem.n_items

        # Pre-sort items in descending order of efficiency ratio for optimal bounding
        ratios = problem.values / problem.weights
        sorted_order = sorted(range(n), key=lambda i: ratios[i], reverse=True)
        v_sorted = problem.values[sorted_order]
        w_sorted = problem.weights[sorted_order]
        cap = problem.capacity

        best_val = 0.0
        best_assignment = np.zeros(n, dtype=int)

        # Statistics
        nodes_explored = 0
        pruned_by_bound = 0
        pruned_by_infeasibility = 0
        trace_log: List[Dict[str, Any]] = []

        def compute_lp_upper_bound(level: int, current_w: float, current_v: float) -> float:
            """Dantzig Fractional Knapsack continuous relaxation upper bound."""
            if current_w > cap:
                return -1.0  # Infeasible
            bound = current_v
            rem_cap = cap - current_w
            for j in range(level, n):
                if w_sorted[j] <= rem_cap:
                    bound += v_sorted[j]
                    rem_cap -= w_sorted[j]
                else:
                    # Take fractional slice of critical item
                    bound += (rem_cap / w_sorted[j]) * v_sorted[j]
                    break
            return bound

        # Stack node: (level, current_weight, current_value, partial_selection)
        # Using depth-first search (branching on inclusion first, then exclusion)
        initial_ub = compute_lp_upper_bound(0, 0.0, 0.0)
        stack = [(0, 0.0, 0.0, [], initial_ub)]

        while stack:
            if nodes_explored >= self.max_nodes:
                break

            level, curr_w, curr_v, selection, ub = stack.pop()
            nodes_explored += 1

            # Infeasibility prune
            if curr_w > cap:
                pruned_by_infeasibility += 1
                continue

            # Bound prune (cannot beat best known solution)
            if ub <= best_val:
                pruned_by_bound += 1
                continue

            # Leaf reached
            if level == n:
                if curr_v > best_val and curr_w <= cap:
                    best_val = curr_v
                    best_assignment = np.array(selection, dtype=int)
                continue

            # Log trace for first few nodes
            if len(trace_log) < 15:
                trace_log.append({
                    "node_id": nodes_explored,
                    "level": level,
                    "curr_weight": curr_w,
                    "curr_value": curr_v,
                    "upper_bound": round(ub, 2),
                    "best_value": round(best_val, 2)
                })

            # Branch 2: Exclude item level (x[level] = 0)
            ub_exclude = compute_lp_upper_bound(level + 1, curr_w, curr_v)
            if ub_exclude > best_val:
                stack.append((level + 1, curr_w, curr_v, selection + [0], ub_exclude))

            # Branch 1: Include item level (x[level] = 1)
            # Pushed second so it is popped first (greedy exploration)
            if curr_w + w_sorted[level] <= cap:
                next_w = curr_w + w_sorted[level]
                next_v = curr_v + v_sorted[level]
                ub_include = compute_lp_upper_bound(level + 1, next_w, next_v)
                if ub_include > best_val:
                    stack.append((level + 1, next_w, next_v, selection + [1], ub_include))

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # Unsort assignment back to original item indexing
        original_selection = np.zeros(n, dtype=int)
        for sorted_idx, orig_idx in enumerate(sorted_order):
            if sorted_idx < len(best_assignment):
                original_selection[orig_idx] = best_assignment[sorted_idx]

        total_val, total_w, feas = problem.evaluate(original_selection)

        return KnapsackSolution(
            solver_name=self.name,
            selected_items=original_selection,
            total_value=total_val,
            total_weight=total_w,
            capacity=problem.capacity,
            is_feasible=feas,
            execution_time_ms=elapsed_ms,
            optimality_gap_percent=0.0,
            extra_metadata={
                "nodes_explored": nodes_explored,
                "nodes_pruned_by_bound": pruned_by_bound,
                "nodes_pruned_by_infeasibility": pruned_by_infeasibility,
                "trace_sample": trace_log
            }
        )

