r"""
Discrete Optimization Comparison Benchmark
Track B: Discrete Optimization
Assignment 8 - Optimize Anything

Systematic empirical comparison of:
  1. Greedy Value-to-Weight Heuristic
  2. Branch-and-Bound (with Dantzig LP relaxation upper bounds)
  3. Dynamic Programming (2D table with exact backtracking)
  4. Integer Linear Programming (SciPy HiGHS binary solver)
  5. QUBO & Ising Model (Classical exhaustive enumeration on small instances)

Problem sizes: N \in [5, 10, 15, 20, 30, 50, 100, 200]
"""

import json
import os
import sys
import time
from typing import Dict, List, Any
import numpy as np

from track_b_discrete_optimization.src.problem import KnapsackProblem, KnapsackSolution
from track_b_discrete_optimization.src.greedy_solver import GreedyKnapsackSolver
from track_b_discrete_optimization.src.ilp_solver import ILPKnapsackSolver
from track_b_discrete_optimization.src.branch_and_bound import BranchAndBoundSolver
from track_b_discrete_optimization.src.dp_solver import DPKnapsackSolver
from track_b_discrete_optimization.src.qubo_ising import QUBOKnapsackSolver

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def run_discrete_benchmarks() -> Dict[str, Any]:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print("Running Track B Discrete Optimization Benchmarks...")

    # Problem instance configurations across small, medium, and large scales
    problem_sizes = [5, 10, 15, 20, 30, 50, 100, 200]
    instances: List[KnapsackProblem] = []

    # Also include the known counterexample as an explicit test case
    instances.append(KnapsackProblem.create_known_counterexample())

    for n in problem_sizes:
        prob = KnapsackProblem.generate_random_instance(
            n_items=n,
            capacity_ratio=0.45,
            max_value=120.0,
            max_weight=40.0,
            seed=100 + n,
            name=f"Bench_N{n}"
        )
        instances.append(prob)

    greedy_solver = GreedyKnapsackSolver()
    ilp_solver = ILPKnapsackSolver(time_limit_sec=30.0)
    bb_solver = BranchAndBoundSolver(max_nodes=150000)
    dp_solver = DPKnapsackSolver()
    qubo_solver = QUBOKnapsackSolver(penalty_multiplier=2.0)

    all_records = []
    csv_rows = []

    for prob in instances:
        n = prob.n_items
        print(f"  Evaluating instance '{prob.name}' (N={n}, Capacity={prob.capacity:.0f})...")

        # 1. Exact ILP baseline (reference truth)
        sol_ilp = ilp_solver.solve(prob)
        opt_val = sol_ilp.total_value

        solvers_to_run = [("ILP (HiGHS)", sol_ilp)]

        # 2. Greedy Heuristic (always run)
        sol_greedy = greedy_solver.solve(prob)
        solvers_to_run.append(("Greedy Heuristic", sol_greedy))

        # 3. Dynamic Programming (always run, integer weights)
        sol_dp = dp_solver.solve(prob)
        solvers_to_run.append(("Dynamic Programming", sol_dp))

        # 4. Branch-and-Bound (run for N <= 50 to avoid combinatorial explosion)
        if n <= 50:
            sol_bb = bb_solver.solve(prob)
            solvers_to_run.append(("Branch-and-Bound", sol_bb))

        # 5. QUBO Exhaustive Enumeration (run for N <= 8 to keep total variables <= 14)
        if n <= 8:
            sol_qubo = qubo_solver.solve(prob)
            solvers_to_run.append(("QUBO Exhaustive", sol_qubo))

        instance_results = []
        for solver_name, sol in solvers_to_run:
            # Optimality gap calculation
            if opt_val > 0 and sol.is_feasible:
                gap = max(0.0, float((opt_val - sol.total_value) / opt_val * 100.0))
            else:
                gap = 100.0 if not sol.is_feasible else 0.0

            sol.optimality_gap_percent = gap
            cap_util = float(sol.total_weight / prob.capacity * 100.0) if prob.capacity > 0 else 0.0

            rec = {
                "instance": prob.name,
                "n_items": n,
                "capacity": prob.capacity,
                "solver": solver_name,
                "total_value": float(sol.total_value),
                "total_weight": float(sol.total_weight),
                "capacity_utilization_pct": round(cap_util, 2),
                "is_feasible": bool(sol.is_feasible),
                "optimality_gap_pct": round(gap, 3),
                "execution_time_ms": round(float(sol.execution_time_ms), 4),
                "selected_items_count": len(sol.selected_indices)
            }
            instance_results.append(rec)
            csv_rows.append(rec)

        all_records.append({
            "instance": prob.name,
            "n_items": n,
            "capacity": prob.capacity,
            "optimal_value": opt_val,
            "results": instance_results
        })

    # Save JSON results
    json_path = os.path.join(RESULTS_DIR, "discrete_comparison_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2)

    # Save CSV results
    csv_path = os.path.join(RESULTS_DIR, "discrete_comparison_summary.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("Instance,N_Items,Capacity,Solver,TotalValue,TotalWeight,CapUtilPct,IsFeasible,OptimalityGapPct,RuntimeMs,SelectedCount\n")
        for r in csv_rows:
            f.write(f'"{r["instance"]}",{r["n_items"]},{r["capacity"]:.1f},"{r["solver"]}",{r["total_value"]:.2f},{r["total_weight"]:.2f},{r["capacity_utilization_pct"]:.2f},{r["is_feasible"]},{r["optimality_gap_pct"]:.3f},{r["execution_time_ms"]:.4f},{r["selected_items_count"]}\n')

    # Save Markdown Report
    md_path = os.path.join(RESULTS_DIR, "discrete_comparison_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Track B: Discrete Optimization Benchmark Report\n\n")
        f.write("> **Assignment 8**: Optimize Anything | **Track B**: Discrete & Combinatorial\n\n")
        f.write("### Benchmark Results Summary Table\n\n")
        f.write("| Instance | N | Solver | Total Value | Weight / Cap | Feasible | Optimality Gap (%) | Runtime (ms) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for r in csv_rows:
            feas_str = "Yes" if r["is_feasible"] else "No"
            f.write(f'| **{r["instance"]}** | {r["n_items"]} | {r["solver"]} | {r["total_value"]:.1f} | {r["total_weight"]:.0f} / {r["capacity"]:.0f} ({r["capacity_utilization_pct"]}%) | {feas_str} | {r["optimality_gap_pct"]:.2f}% | {r["execution_time_ms"]:.3f} |\n')

    print(f"Discrete benchmark completed:\n  JSON: {json_path}\n  CSV:  {csv_path}\n  MD:   {md_path}")
    return {"records": all_records, "csv_rows": csv_rows}


if __name__ == "__main__":
    run_discrete_benchmarks()

