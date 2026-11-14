r"""
Integer Linear Programming (ILP) Knapsack Solver
Track B: Discrete Optimization
Assignment 8 - Optimize Anything

Solves 0/1 Knapsack using SciPy's HiGHS MILP solver:
    Minimize   - \sum_{i=1}^n v_i x_i
    Subject to   0 <= \sum_{i=1}^n w_i x_i <= W
                 x_i \in {0, 1}
"""

import time
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from track_b_discrete_optimization.src.problem import KnapsackProblem, KnapsackSolution


class ILPKnapsackSolver:
    """
    Exact Integer Linear Programming (ILP) Solver using SciPy HiGHS.
    Guarantees mathematically provable global optimality within solver tolerance.
    """

    def __init__(self, time_limit_sec: float = 60.0, name: str = "ILP Solver (SciPy HiGHS)"):
        self.time_limit_sec = time_limit_sec
        self.name = name

    def solve(self, problem: KnapsackProblem) -> KnapsackSolution:
        """
        Solve Knapsack using HiGHS binary MILP:
          c = -problem.values (for maximization)
          A = problem.weights.reshape(1, -1)
          lb = 0, ub = problem.capacity
          integrality = 1 (binary integer variables)
          bounds = [0, 1]
        """
        t0 = time.perf_counter()
        n = problem.n_items

        c = -problem.values
        A = problem.weights.reshape(1, -1)
        constraints = LinearConstraint(A, lb=0.0, ub=problem.capacity)
        integrality = np.ones(n, dtype=int)  # 1 for integer/binary
        bounds = Bounds(lb=np.zeros(n), ub=np.ones(n))

        options = {
            "time_limit": self.time_limit_sec,
            "presolve": True
        }

        res = milp(
            c=c,
            integrality=integrality,
            bounds=bounds,
            constraints=constraints,
            options=options
        )

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        if not res.success:
            # Handle infeasible or timeout
            return KnapsackSolution(
                solver_name=self.name,
                selected_items=np.zeros(n, dtype=int),
                total_value=0.0,
                total_weight=0.0,
                capacity=problem.capacity,
                is_feasible=False,
                execution_time_ms=elapsed_ms,
                extra_metadata={
                    "status": res.status,
                    "message": res.message,
                    "mip_node_count": getattr(res, "mip_node_count", None),
                    "mip_gap": getattr(res, "mip_gap", None)
                }
            )

        # Round binary solutions
        x_sol = np.round(res.x).astype(int)
        total_val, total_w, feas = problem.evaluate(x_sol)

        return KnapsackSolution(
            solver_name=self.name,
            selected_items=x_sol,
            total_value=total_val,
            total_weight=total_w,
            capacity=problem.capacity,
            is_feasible=feas,
            execution_time_ms=elapsed_ms,
            optimality_gap_percent=0.0,  # Exact optimal
            extra_metadata={
                "status": res.status,
                "message": res.message,
                "mip_node_count": getattr(res, "mip_node_count", None),
                "mip_gap": getattr(res, "mip_gap", 0.0)
            }
        )

