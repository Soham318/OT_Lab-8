r"""Experiment 1: Submodular Optimization Benchmark (Maximum Coverage).

Evaluates:
- Monotone submodular greedy selection vs exact brute-force optimum
- Optimality gap and verification of (1 - 1/e) theoretical bound (~63.2%)
- Runtime and coverage scaling across universe size U and subset count m
"""

import csv
import json
import os
import sys
import time
from typing import Any, Dict, List
import numpy as np

# Ensure project root is on sys.path for direct script execution
sys.path.insert(0, os.path.abspath("."))

from track_d_parallel_distributed_optimization.src.submodular import MaximumCoverageProblem


def run_submodular_benchmarks() -> List[Dict[str, Any]]:
    print("=" * 70)
    print("RUNNING EXPERIMENT 1: Submodular Optimization (Maximum Coverage)")
    print("=" * 70)

    # Benchmark instance configurations
    # First 4 instances are small enough for exact combinatorial enumeration
    # Remaining instances scale up to demonstrate greedy efficiency
    configs = [
        {"name": "Tiny-10", "universe": 20, "subsets": 10, "k": 3, "exact": True},
        {"name": "Small-14", "universe": 40, "subsets": 14, "k": 3, "exact": True},
        {"name": "Medium-18", "universe": 60, "subsets": 18, "k": 4, "exact": True},
        {"name": "Borderline-20", "universe": 80, "subsets": 20, "k": 4, "exact": True},
        {"name": "Large-35", "universe": 150, "subsets": 35, "k": 6, "exact": False},
        {"name": "XLarge-50", "universe": 300, "subsets": 50, "k": 8, "exact": False},
        {"name": "Scale-80", "universe": 500, "subsets": 80, "k": 10, "exact": False},
    ]

    results = []

    for idx, cfg in enumerate(configs, 1):
        print(f"\n[{idx}/{len(configs)}] Instance: {cfg['name']} (U={cfg['universe']}, m={cfg['subsets']}, k={cfg['k']})")
        prob = MaximumCoverageProblem.create_synthetic_instance(
            universe_size=cfg["universe"],
            num_subsets=cfg["subsets"],
            density=0.18,
            seed=42 + idx,
        )

        # 1. Greedy Solution
        greedy_res = prob.solve_greedy(cfg["k"])
        cov_greedy = greedy_res["coverage_count"]
        frac_greedy = greedy_res["coverage_fraction"]
        time_greedy = greedy_res["runtime_ms"]

        exact_val = None
        exact_time = None
        opt_gap = None
        theo_bound = None
        bound_satisfied = None

        if cfg["exact"]:
            # 2. Exact Brute Force Solution
            exact_res = prob.solve_exact(cfg["k"])
            exact_val = exact_res["optimal_coverage"]
            exact_time = exact_res["runtime_ms"]
            theo_bound = MaximumCoverageProblem.theoretical_bound(exact_val)

            opt_gap = (exact_val - cov_greedy) / exact_val if exact_val > 0 else 0.0
            bound_satisfied = (cov_greedy >= theo_bound)

            print(f"  Greedy Cov: {cov_greedy}/{cfg['universe']} ({frac_greedy:.1%}) in {time_greedy:.2f} ms")
            print(f"  Exact  Cov: {exact_val}/{cfg['universe']} ({exact_val/cfg['universe']:.1%}) in {exact_time:.2f} ms")
            print(f"  Gap: {opt_gap:.2%} | (1-1/e) Bound: {theo_bound:.1f} | Bound Satisfied: {bound_satisfied}")
        else:
            print(f"  Greedy Cov: {cov_greedy}/{cfg['universe']} ({frac_greedy:.1%}) in {time_greedy:.2f} ms (Exact skipped)")

        results.append({
            "name": cfg["name"],
            "universe_size": cfg["universe"],
            "num_subsets": cfg["subsets"],
            "cardinality_k": cfg["k"],
            "has_exact": cfg["exact"],
            "greedy_coverage": cov_greedy,
            "greedy_fraction": round(frac_greedy, 4),
            "greedy_runtime_ms": round(time_greedy, 3),
            "exact_coverage": exact_val,
            "exact_runtime_ms": round(exact_time, 3) if exact_time is not None else None,
            "optimality_gap_pct": round(opt_gap * 100.0, 2) if opt_gap is not None else None,
            "theoretical_1_minus_1_over_e_bound": round(theo_bound, 2) if theo_bound is not None else None,
            "bound_satisfied": bound_satisfied,
            "marginal_gains": greedy_res["marginal_gains"],
            "coverage_history": greedy_res["coverage_history"],
        })

    # Save to results/
    os.makedirs("track_d_parallel_distributed_optimization/results", exist_ok=True)
    json_path = "track_d_parallel_distributed_optimization/results/submodular_benchmark_results.json"
    csv_path = "track_d_parallel_distributed_optimization/results/submodular_benchmark_summary.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name", "Universe", "Subsets", "k", "GreedyCoverage", "GreedyFraction",
            "GreedyRuntimeMs", "ExactCoverage", "ExactRuntimeMs", "OptimalityGapPct",
            "TheoreticalBound", "BoundSatisfied",
        ])
        for r in results:
            writer.writerow([
                r["name"], r["universe_size"], r["num_subsets"], r["cardinality_k"],
                r["greedy_coverage"], r["greedy_fraction"], r["greedy_runtime_ms"],
                r["exact_coverage"] if r["exact_coverage"] is not None else "N/A",
                r["exact_runtime_ms"] if r["exact_runtime_ms"] is not None else "N/A",
                r["optimality_gap_pct"] if r["optimality_gap_pct"] is not None else "N/A",
                r["theoretical_1_minus_1_over_e_bound"] if r["theoretical_1_minus_1_over_e_bound"] is not None else "N/A",
                r["bound_satisfied"] if r["bound_satisfied"] is not None else "N/A",
            ])

    print(f"\n[DONE] Saved raw results to {json_path} and {csv_path}")
    return results


if __name__ == "__main__":
    run_submodular_benchmarks()
