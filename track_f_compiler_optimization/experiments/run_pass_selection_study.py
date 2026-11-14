r"""Experiment 2: Compiler Pass Selection Decision Model Benchmark.

Evaluates:
- Binary Integer Linear Programming (BILP) formulation for compiler pass selection
- Pass selection under varying compile-time budgets B in {2.0, 4.0, 6.0, 8.0, 10.0}
- Verification of SciPy MILP optimality against exhaustive enumeration (2^5 = 32 subsets)
- Trade-off between compilation latency and generated code performance
"""

import csv
import json
import os
import sys
from typing import Any, Dict, List

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath("."))

from track_f_compiler_optimization.src.pass_selector import PassSelectionProblem


def run_pass_selection_study() -> List[Dict[str, Any]]:
    print("=" * 70)
    print("RUNNING EXPERIMENT 2: Compiler Pass Selection Optimization Problem")
    print("=" * 70)

    problem = PassSelectionProblem()

    budgets = [2.0, 4.0, 6.0, 8.0, 11.0]
    results = []

    for budget in budgets:
        print(f"\n--- Compile-Time Budget: {budget:.1f} ---")

        # 1. Solve via SciPy MILP
        milp_sol = problem.solve_milp(compile_time_budget=budget)

        # 2. Solve via Exhaustive Enumeration
        exh_sol = problem.solve_exhaustive(compile_time_budget=budget)

        # Verify optimality parity
        val_diff = abs(milp_sol["net_objective_value"] - exh_sol["best_value"])
        optimality_confirmed = val_diff < 1e-4

        selected_str = "+".join(milp_sol["selected_passes"]) if milp_sol["selected_passes"] else "None"

        print(f"  Selected Passes:   {selected_str}")
        print(f"  Compile Cost:      {milp_sol['total_compile_cost']:.1f} / {budget:.1f}")
        print(f"  Runtime Benefit:   {milp_sol['total_runtime_benefit']:.1f}")
        print(f"  Size Benefit:      {milp_sol['total_size_benefit']:.1f}")
        print(f"  Net Objective:     {milp_sol['net_objective_value']:.2f}")
        print(f"  MILP vs Exact Gap: {val_diff:.4e} (Optimal: {optimality_confirmed})")

        results.append({
            "budget": budget,
            "selected_passes": milp_sol["selected_passes"],
            "selected_binary": milp_sol["chosen_binary"],
            "compile_cost": round(milp_sol["total_compile_cost"], 2),
            "runtime_benefit": round(milp_sol["total_runtime_benefit"], 2),
            "size_benefit": round(milp_sol["total_size_benefit"], 2),
            "net_objective_value": round(milp_sol["net_objective_value"], 2),
            "exhaustive_best_value": round(exh_sol["best_value"], 2),
            "optimality_confirmed": optimality_confirmed,
        })

    os.makedirs("track_f_compiler_optimization/results", exist_ok=True)
    json_path = "track_f_compiler_optimization/results/pass_selection_results.json"
    csv_path = "track_f_compiler_optimization/results/pass_selection_summary.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Budget", "SelectedPasses", "CompileCost", "RuntimeBenefit",
            "SizeBenefit", "NetObjective", "ExhaustiveOptimal", "OptimalityConfirmed",
        ])
        for r in results:
            writer.writerow([
                r["budget"], "+".join(r["selected_passes"]), r["compile_cost"],
                r["runtime_benefit"], r["size_benefit"], r["net_objective_value"],
                r["exhaustive_best_value"], r["optimality_confirmed"],
            ])

    print(f"\n[DONE] Saved pass selection results to {json_path} and {csv_path}")
    return results


if __name__ == "__main__":
    run_pass_selection_study()

