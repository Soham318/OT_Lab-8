r"""Experiment 2: Parallel Computing Scaling Benchmark.

Evaluates:
- Execution time across worker counts P in {1, 2, 4, 8}
- Speedup S_P = T_1 / T_P
- Parallel efficiency E_P = S_P / P
- Across problem scales: Small (16 chunks), Medium (32 chunks), Large (64 chunks)
- Repeated trials (mean and standard deviation)
"""

import csv
import json
import os
import sys
from typing import Any, Dict, List
import numpy as np

# Ensure project root is on sys.path for direct script execution
sys.path.insert(0, os.path.abspath("."))

from track_d_parallel_distributed_optimization.src.parallel_compute import ParallelComputeBenchmark


def run_parallel_benchmarks() -> List[Dict[str, Any]]:
    print("=" * 70)
    print("RUNNING EXPERIMENT 2: Parallel Computing Workload Scaling")
    print("=" * 70)

    # 150,000 floats per chunk, 6 mathematical iterations
    bench = ParallelComputeBenchmark(chunk_size=150_000, iterations_per_chunk=6)

    problem_scales = [
        {"scale": "Small", "chunks": 16},
        {"scale": "Medium", "chunks": 32},
        {"scale": "Large", "chunks": 48},
    ]

    worker_counts = [1, 2, 4, 8]
    repeats = 2

    all_results = []

    for scale_info in problem_scales:
        scale_name = scale_info["scale"]
        num_chunks = scale_info["chunks"]
        print(f"\n--- Problem Scale: {scale_name} ({num_chunks} chunks, {num_chunks * 150_000:,} total elements) ---")

        scale_metrics = bench.benchmark_scaling(
            num_chunks=num_chunks,
            worker_counts=worker_counts,
            repeats=repeats,
        )

        for entry in scale_metrics:
            entry["problem_scale"] = scale_name
            mode_str = entry["mode"]
            w = entry["worker_count"]
            t_mean = entry["mean_time_sec"]
            t_std = entry["std_time_sec"]
            sp = entry["speedup"]
            eff = entry["efficiency"]
            err = entry["result_parity_error"]

            print(
                f"  [{scale_name}] Workers: {w:2d} ({mode_str:20s}) -> "
                f"Time: {t_mean:.3f}s ± {t_std:.3f}s | Speedup: {sp:.2f}x | "
                f"Efficiency: {eff:.1%} | Parity Err: {err:.1e}"
            )
            all_results.append(entry)

    os.makedirs("track_d_parallel_distributed_optimization/results", exist_ok=True)
    json_path = "track_d_parallel_distributed_optimization/results/parallel_benchmark_results.json"
    csv_path = "track_d_parallel_distributed_optimization/results/parallel_benchmark_summary.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ProblemScale", "NumChunks", "WorkerCount", "Mode",
            "MeanTimeSec", "StdTimeSec", "Speedup", "Efficiency", "ParityError",
        ])
        for r in all_results:
            writer.writerow([
                r["problem_scale"], r["num_chunks"], r["worker_count"], r["mode"],
                round(r["mean_time_sec"], 4), round(r["std_time_sec"], 4),
                round(r["speedup"], 4), round(r["efficiency"], 4),
                r["result_parity_error"],
            ])

    print(f"\n[DONE] Saved parallel benchmark results to {json_path} and {csv_path}")
    return all_results


if __name__ == "__main__":
    run_parallel_benchmarks()
