"""
Detailed Profiling Module for Track J: Real-World Codebase Optimization
Uses cProfile, pstats, and tracemalloc to analyze bottlenecks in:
1. Naive Baseline Scheduler
2. Optimized DP Scheduler
"""

import os
import cProfile
import pstats
import io
import tracemalloc
import json
from typing import Dict, Any

from track_j_real_world_optimization.src.dataset_generator import generate_layered_workflow_dag
from track_j_real_world_optimization.src.workflow_models import ResourceCluster, validate_schedule_correctness
from track_j_real_world_optimization.src.baseline_scheduler import NaiveWorkflowScheduler
from track_j_real_world_optimization.src.optimized_scheduler import OptimizedWorkflowScheduler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_profiling_session(num_tasks: int = 250) -> Dict[str, Any]:
    """
    Profile both schedulers on identical workflow instance using cProfile and tracemalloc.
    """
    print(f"Generating profiling workload with {num_tasks} tasks...")
    dag = generate_layered_workflow_dag(num_tasks=num_tasks, seed=42)
    cluster = ResourceCluster(num_workers=4)

    # -------------------------------------------------------------
    # 1. Profile Naive Baseline Scheduler
    # -------------------------------------------------------------
    print("\n--- Profiling Naive Baseline Scheduler ---")
    tracemalloc.start()
    baseline_profiler = cProfile.Profile()
    baseline_scheduler = NaiveWorkflowScheduler(dag, cluster)

    baseline_profiler.enable()
    baseline_schedule = baseline_scheduler.schedule()
    baseline_profiler.disable()

    base_curr, base_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Capture pstats text
    base_stream = io.StringIO()
    base_ps = pstats.Stats(baseline_profiler, stream=base_stream).sort_stats("cumulative")
    base_ps.print_stats(25)
    base_profile_text = base_stream.getvalue()

    # Save pstats binary and text
    base_pstats_path = os.path.join(RESULTS_DIR, "original_profiling.pstats")
    baseline_profiler.dump_stats(base_pstats_path)
    base_txt_path = os.path.join(RESULTS_DIR, "original_profiling.txt")
    with open(base_txt_path, "w", encoding="utf-8") as f:
        f.write(base_profile_text)
    print(f"  [SAVED] Baseline profile report: {base_txt_path}")

    # Validate correctness
    base_valid, base_errs = validate_schedule_correctness(dag.tasks, cluster, baseline_schedule)

    # -------------------------------------------------------------
    # 2. Profile Optimized DP Scheduler
    # -------------------------------------------------------------
    print("\n--- Profiling Optimized DP Scheduler ---")
    tracemalloc.start()
    opt_profiler = cProfile.Profile()
    opt_scheduler = OptimizedWorkflowScheduler(dag, cluster)

    opt_profiler.enable()
    opt_schedule = opt_scheduler.schedule()
    opt_profiler.disable()

    opt_curr, opt_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Capture pstats text
    opt_stream = io.StringIO()
    opt_ps = pstats.Stats(opt_profiler, stream=opt_stream).sort_stats("cumulative")
    opt_ps.print_stats(25)
    opt_profile_text = opt_stream.getvalue()

    # Save pstats binary and text
    opt_pstats_path = os.path.join(RESULTS_DIR, "optimized_profiling.pstats")
    opt_profiler.dump_stats(opt_pstats_path)
    opt_txt_path = os.path.join(RESULTS_DIR, "optimized_profiling.txt")
    with open(opt_txt_path, "w", encoding="utf-8") as f:
        f.write(opt_profile_text)
    print(f"  [SAVED] Optimized profile report: {opt_txt_path}")

    # Validate correctness
    opt_valid, opt_errs = validate_schedule_correctness(dag.tasks, cluster, opt_schedule)

    speedup = (
        baseline_schedule.scheduling_time_s / opt_schedule.scheduling_time_s
        if opt_schedule.scheduling_time_s > 0 else 1.0
    )

    summary = {
        "num_tasks": num_tasks,
        "num_edges": dag.num_edges,
        "baseline": {
            "scheduling_time_s": round(baseline_schedule.scheduling_time_s, 6),
            "makespan": round(baseline_schedule.makespan, 4),
            "peak_memory_kb": round(base_peak / 1024.0, 2),
            "is_valid": base_valid,
            "errors": base_errs
        },
        "optimized": {
            "scheduling_time_s": round(opt_schedule.scheduling_time_s, 6),
            "makespan": round(opt_schedule.makespan, 4),
            "peak_memory_kb": round(opt_peak / 1024.0, 2),
            "is_valid": opt_valid,
            "errors": opt_errs
        },
        "speedup_ratio": round(speedup, 2),
        "makespan_difference": round(abs(baseline_schedule.makespan - opt_schedule.makespan), 4)
    }

    json_path = os.path.join(RESULTS_DIR, "profiling_comparison.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[INFO] Profiling summary saved to: {json_path}")
    print(f"Speedup achieved on {num_tasks} tasks: {speedup:.2f}x faster!")

    return summary

if __name__ == "__main__":
    run_profiling_session(num_tasks=250)
