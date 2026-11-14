"""
Comprehensive Benchmark Runner
Track J: Real-World Codebase Optimization

Conducts rigorous empirical benchmarking comparing:
  - Naive Baseline Scheduler: O(V^3) with redundant graph traversals
  - Chapter 6 Optimized DP Scheduler: O((V+E) log V) with backward memoization & heap queue

Evaluates across 4 standard input scales:
  1. Small: 50 tasks, ~150 edges
  2. Medium: 250 tasks, ~1,500 edges
  3. Large: 1,000 tasks, ~8,000 edges
  4. Extra-Large: 2,500 tasks, ~23,000 edges

Measures:
  - Latency: mean, median, min, max, std dev (over multiple repetitions)
  - Memory: peak memory usage via tracemalloc
  - Speedup ratio
  - Makespan optimality (C_max)
  - Complete schedule validity (precedence & worker non-overlap)

Exports:
  - track_j_real_world_optimization/results/benchmark_results.json
  - track_j_real_world_optimization/results/benchmark_results.csv
"""

import os
import sys
import time
import json
import csv
import statistics
import tracemalloc
from typing import Dict, List, Any, Tuple

from track_j_real_world_optimization.src.workflow_models import (
    ResourceCluster, WorkflowSchedule, validate_schedule_correctness
)
from track_j_real_world_optimization.src.dag_parser import WorkflowDAG
from track_j_real_world_optimization.src.dataset_generator import (
    DATA_DIR, generate_standard_benchmark_datasets
)
from track_j_real_world_optimization.src.baseline_scheduler import NaiveWorkflowScheduler
from track_j_real_world_optimization.src.optimized_scheduler import OptimizedWorkflowScheduler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def benchmark_scheduler(
    scheduler_cls,
    dag: WorkflowDAG,
    cluster: ResourceCluster,
    warmup_runs: int = 1,
    measured_runs: int = 5
) -> Dict[str, Any]:
    """
    Run warmup and measured repetitions for a scheduler on a given DAG.
    Captures timing statistics, peak memory, makespan, and validation status.
    """
    # 1. Warm-up runs (discarded)
    for _ in range(warmup_runs):
        sched_obj = scheduler_cls(dag, cluster)
        _ = sched_obj.schedule()

    # 2. Measured repetitions
    times: List[float] = []
    schedules: List[WorkflowSchedule] = []

    for _ in range(measured_runs):
        t0 = time.perf_counter()
        sched_obj = scheduler_cls(dag, cluster)
        sched = sched_obj.schedule()
        t1 = time.perf_counter()
        times.append(t1 - t0)
        schedules.append(sched)

    # 3. Memory profiling run via tracemalloc
    tracemalloc.start()
    sched_obj = scheduler_cls(dag, cluster)
    final_sched = sched_obj.schedule()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # 4. Schedule validity verification
    is_valid, error_list = validate_schedule_correctness(dag.tasks, cluster, final_sched)

    return {
        "runs": measured_runs,
        "mean_time_s": statistics.mean(times),
        "median_time_s": statistics.median(times),
        "min_time_s": min(times),
        "max_time_s": max(times),
        "std_time_s": statistics.stdev(times) if len(times) > 1 else 0.0,
        "peak_memory_kb": round(peak_mem / 1024.0, 2),
        "makespan": round(final_sched.makespan, 4),
        "is_valid": is_valid,
        "error_count": len(error_list),
        "errors": error_list[:5]
    }

def run_full_benchmark_suite() -> Dict[str, Any]:
    """Execute the comprehensive benchmark across all 4 scales."""
    # Ensure datasets exist
    datasets = {
        "small": os.path.join(DATA_DIR, "workflow_small.json"),
        "medium": os.path.join(DATA_DIR, "workflow_medium.json"),
        "large": os.path.join(DATA_DIR, "workflow_large.json"),
        "xlarge": os.path.join(DATA_DIR, "workflow_xlarge.json")
    }

    for scale, path in datasets.items():
        if not os.path.exists(path):
            print("Benchmark datasets not found. Generating...")
            generate_standard_benchmark_datasets()
            break

    cluster = ResourceCluster(num_workers=8, total_cpus=32, total_memory_mb=32768.0)

    # Execution plan:
    # Small: 1 warmup + 5 reps
    # Medium: 1 warmup + 5 reps
    # Large: 1 warmup + 5 reps
    # XLarge: 1 warmup + 3 reps (Baseline takes ~78s/run, 3 reps = ~234s)
    scale_configs = [
        ("small", 50, 1, 5, 1, 5),
        ("medium", 250, 1, 5, 1, 5),
        ("large", 1000, 1, 5, 1, 5),
        ("xlarge", 2500, 1, 3, 1, 5)
    ]

    all_results = {}
    csv_rows = []

    print("================================================================================")
    print("  CHAPTER 6 REAL-WORLD CODEBASE OPTIMIZATION BENCHMARK SUITE")
    print("================================================================================")
    print(f"{'Scale':<8} | {'Tasks':<5} | {'Edges':<6} | {'Base Mean (s)':<14} | {'Opt Mean (s)':<13} | {'Speedup':<9} | {'Makespan Base/Opt':<18} | {'Valid'}")
    print("--------------------------------------------------------------------------------")

    for scale_key, expected_tasks, base_warmup, base_reps, opt_warmup, opt_reps in scale_configs:
        path = datasets[scale_key]
        dag = WorkflowDAG.from_json_file(path)

        # Baseline benchmark
        base_res = benchmark_scheduler(
            NaiveWorkflowScheduler, dag, cluster,
            warmup_runs=base_warmup, measured_runs=base_reps
        )

        # Optimized benchmark
        opt_res = benchmark_scheduler(
            OptimizedWorkflowScheduler, dag, cluster,
            warmup_runs=opt_warmup, measured_runs=opt_reps
        )

        speedup_mean = base_res["mean_time_s"] / opt_res["mean_time_s"] if opt_res["mean_time_s"] > 0 else 1.0
        speedup_median = base_res["median_time_s"] / opt_res["median_time_s"] if opt_res["median_time_s"] > 0 else 1.0

        all_results[scale_key] = {
            "scale": scale_key,
            "tasks": dag.num_tasks,
            "edges": dag.num_edges,
            "baseline": base_res,
            "optimized": opt_res,
            "speedup_mean": round(speedup_mean, 2),
            "speedup_median": round(speedup_median, 2),
            "makespan_ratio": round(opt_res["makespan"] / base_res["makespan"], 4) if base_res["makespan"] > 0 else 1.0
        }

        print(
            f"{scale_key:<8} | {dag.num_tasks:<5} | {dag.num_edges:<6} | "
            f"{base_res['mean_time_s']:14.6f} | {opt_res['mean_time_s']:13.6f} | "
            f"{speedup_mean:8.1f}x | {base_res['makespan']:8.1f}/{opt_res['makespan']:8.1f} | "
            f"{'PASS' if base_res['is_valid'] and opt_res['is_valid'] else 'FAIL'}"
        )

        csv_rows.append({
            "scale": scale_key,
            "tasks": dag.num_tasks,
            "edges": dag.num_edges,
            "baseline_mean_time_s": f"{base_res['mean_time_s']:.6f}",
            "baseline_median_time_s": f"{base_res['median_time_s']:.6f}",
            "baseline_std_time_s": f"{base_res['std_time_s']:.6f}",
            "baseline_peak_memory_kb": f"{base_res['peak_memory_kb']:.2f}",
            "baseline_makespan": f"{base_res['makespan']:.4f}",
            "baseline_valid": base_res["is_valid"],
            "optimized_mean_time_s": f"{opt_res['mean_time_s']:.6f}",
            "optimized_median_time_s": f"{opt_res['median_time_s']:.6f}",
            "optimized_std_time_s": f"{opt_res['std_time_s']:.6f}",
            "optimized_peak_memory_kb": f"{opt_res['peak_memory_kb']:.2f}",
            "optimized_makespan": f"{opt_res['makespan']:.4f}",
            "optimized_valid": opt_res["is_valid"],
            "speedup_mean": f"{speedup_mean:.2f}",
            "speedup_median": f"{speedup_median:.2f}"
        })

    print("================================================================================")

    # Save JSON results
    json_path = os.path.join(RESULTS_DIR, "benchmark_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"Benchmark results JSON written to: {json_path}")

    # Save CSV results
    csv_path = os.path.join(RESULTS_DIR, "benchmark_results.csv")
    fieldnames = list(csv_rows[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"Benchmark results CSV written to: {csv_path}")

    return all_results

if __name__ == "__main__":
    run_full_benchmark_suite()
