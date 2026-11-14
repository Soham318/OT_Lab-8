r"""Experiment 5: Multiple Gradient Descent Algorithm (MGDA) Benchmark.

Evaluates:
- MGDA multi-objective optimization vs scalarized weighted sum baselines
- Conflicting gradient balancing and Pareto front discovery
- Convergence to Pareto-stationary points ||sum alpha_i grad f_i|| = 0
"""

import csv
import json
import os
import sys
from typing import Any, Dict, List
import numpy as np

# Ensure project root is on sys.path for direct script execution
sys.path.insert(0, os.path.abspath("."))

from track_d_parallel_distributed_optimization.src.mgda import (
    MGDASolver,
    MultiObjectiveBenchmark,
)


def run_mgda_benchmarks() -> Dict[str, Any]:
    print("=" * 70)
    print("RUNNING EXPERIMENT 5: Multi-Objective MGDA vs Weighted Sum")
    print("=" * 70)

    solver = MGDASolver()
    initial_x = np.array([2.5, 3.0], dtype=float)

    # 1. Conflicting Quadratics Benchmark
    # f1 = (x1 - 1)^2 + x2^2, f2 = (x1 + 1)^2 + x2^2
    # Pareto front: x2 = 0, -1 <= x1 <= 1
    print("\n--- 1. Conflicting Quadratics Problem ---")
    print(f"Initial x: {initial_x.tolist()}")

    mgda_res = solver.optimize_mgda(
        MultiObjectiveBenchmark.conflicting_quadratics,
        initial_x=initial_x,
        lr=0.05,
        max_iters=250,
    )
    print(f"  MGDA: Final x: {mgda_res['final_x'].round(4).tolist()} | Objectives: {mgda_res['final_objectives'].round(4).tolist()} | Iters: {mgda_res['iterations']}")

    # Baseline 1: Equal weights (0.5, 0.5)
    ws_equal = solver.optimize_weighted_sum(
        MultiObjectiveBenchmark.conflicting_quadratics,
        initial_x=initial_x,
        weights=np.array([0.5, 0.5]),
        lr=0.05,
        max_iters=250,
    )
    print(f"  WeightedSum (0.5/0.5): Final x: {ws_equal['final_x'].round(4).tolist()} | Objectives: {ws_equal['final_objectives'].round(4).tolist()}")

    # Baseline 2: Imbalanced weights (0.8, 0.2)
    ws_imb1 = solver.optimize_weighted_sum(
        MultiObjectiveBenchmark.conflicting_quadratics,
        initial_x=initial_x,
        weights=np.array([0.8, 0.2]),
        lr=0.05,
        max_iters=250,
    )
    print(f"  WeightedSum (0.8/0.2): Final x: {ws_imb1['final_x'].round(4).tolist()} | Objectives: {ws_imb1['final_objectives'].round(4).tolist()}")

    # Baseline 3: Imbalanced weights (0.2, 0.8)
    ws_imb2 = solver.optimize_weighted_sum(
        MultiObjectiveBenchmark.conflicting_quadratics,
        initial_x=initial_x,
        weights=np.array([0.2, 0.8]),
        lr=0.05,
        max_iters=250,
    )
    print(f"  WeightedSum (0.2/0.8): Final x: {ws_imb2['final_x'].round(4).tolist()} | Objectives: {ws_imb2['final_objectives'].round(4).tolist()}")

    # 2. Scaled Conflicting Problem
    print("\n--- 2. Scaled Conflicting Functions ---")
    init_scaled = np.array([3.0, -1.0])
    mgda_scaled = solver.optimize_mgda(
        MultiObjectiveBenchmark.scaled_conflicting,
        initial_x=init_scaled,
        lr=0.02,
        max_iters=250,
    )
    print(f"  MGDA Scaled: Final x: {mgda_scaled['final_x'].round(4).tolist()} | Objectives: {mgda_scaled['final_objectives'].round(4).tolist()}")

    def serialize_res(r: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "method": r["method"],
            "final_x": [round(float(v), 5) for v in r["final_x"]],
            "final_objectives": [round(float(v), 5) for v in r["final_objectives"]],
            "iterations": int(r["iterations"]),
            "trajectory": [[round(float(coord), 4) for coord in pt] for pt in r["trajectory"]],
            "f_history": [[round(float(v), 4) for v in pt] for pt in r["f_history"]],
            "grad_norm_history": [round(float(v), 5) for v in r["grad_norm_history"]],
            "alpha_history": (
                [[round(float(v), 4) for v in pt] for pt in r["alpha_history"]]
                if "alpha_history" in r
                else None
            ),
        }

    combined = {
        "conflicting_quadratics": {
            "initial_x": initial_x.tolist(),
            "mgda": serialize_res(mgda_res),
            "weighted_sum_05_05": serialize_res(ws_equal),
            "weighted_sum_08_02": serialize_res(ws_imb1),
            "weighted_sum_02_08": serialize_res(ws_imb2),
        },
        "scaled_conflicting": {
            "initial_x": init_scaled.tolist(),
            "mgda": serialize_res(mgda_scaled),
        },
    }

    os.makedirs("track_d_parallel_distributed_optimization/results", exist_ok=True)
    json_path = "track_d_parallel_distributed_optimization/results/mgda_benchmark_results.json"
    csv_path = "track_d_parallel_distributed_optimization/results/mgda_benchmark_summary.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Problem", "Method", "FinalX1", "FinalX2", "FinalF1", "FinalF2", "Iterations"])
        for prob_name, methods in [("ConflictingQuadratics", [mgda_res, ws_equal, ws_imb1, ws_imb2]), ("ScaledConflicting", [mgda_scaled])]:
            for m in methods:
                writer.writerow([
                    prob_name, m["method"],
                    round(float(m["final_x"][0]), 4), round(float(m["final_x"][1]), 4),
                    round(float(m["final_objectives"][0]), 4), round(float(m["final_objectives"][1]), 4),
                    m["iterations"],
                ])

    print(f"\n[DONE] Saved MGDA benchmark results to {json_path} and {csv_path}")
    return combined


if __name__ == "__main__":
    run_mgda_benchmarks()
