"""
Publication-Quality Visualization Generator
Track J: Real-World Codebase Optimization

Generates 4 figures (300 DPI, modern publication styling):
  1. plots/01_execution_time_comparison.png: Logarithmic latency comparison (Baseline vs Optimized)
  2. plots/02_speedup_scaling_curve.png: Empirical speedup curve vs task count
  3. plots/03_profiling_bottleneck_breakdown.png: cProfile cumulative time bottleneck breakdown
  4. plots/04_memory_footprint_scaling.png: Peak memory footprint scaling across problem scales
"""

import os
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# Set styling
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 11,
    "figure.titlesize": 14,
    "lines.linewidth": 2.2,
    "lines.markersize": 7,
    "axes.grid": True,
    "grid.alpha": 0.35,
    "grid.linestyle": "--"
})

def plot_execution_time_comparison(benchmark_data: dict):
    """Plot 1: Log-scale execution time comparison across problem scales."""
    scales = ["small", "medium", "large", "xlarge"]
    tasks = [benchmark_data[s]["tasks"] for s in scales]
    labels = [f"{s.capitalize()}\n(N={t})" for s, t in zip(scales, tasks)]

    base_times = [benchmark_data[s]["baseline"]["mean_time_s"] for s in scales]
    opt_times = [benchmark_data[s]["optimized"]["mean_time_s"] for s in scales]
    base_std = [benchmark_data[s]["baseline"]["std_time_s"] for s in scales]
    opt_std = [benchmark_data[s]["optimized"]["std_time_s"] for s in scales]

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    x = np.arange(len(scales))
    width = 0.35

    rects1 = ax.bar(x - width/2, base_times, width, yerr=base_std, capsize=4,
                    label="Baseline Scheduler O(V³)", color="#e74c3c", alpha=0.9, edgecolor="black")
    rects2 = ax.bar(x + width/2, opt_times, width, yerr=opt_std, capsize=4,
                    label="Optimized DP Scheduler O((V+E) log V)", color="#2ecc71", alpha=0.9, edgecolor="black")

    ax.set_ylabel("Execution Time (seconds, log scale)")
    ax.set_title("Workflow Scheduler Latency: Baseline vs Chapter 6 Optimized DP", pad=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_yscale("log")
    ax.legend(frameon=True, loc="upper left")

    # Add value annotations
    for i in range(len(scales)):
        ax.text(x[i] - width/2, base_times[i] * 1.3, f"{base_times[i]:.3f}s",
                ha="center", va="bottom", fontsize=8.5, fontweight="semibold")
        ax.text(x[i] + width/2, opt_times[i] * 1.3, f"{opt_times[i]:.4f}s",
                ha="center", va="bottom", fontsize=8.5, fontweight="semibold")

    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "01_execution_time_comparison.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {out_path}")

def plot_speedup_scaling_curve(benchmark_data: dict):
    """Plot 2: Speedup scaling curve vs task count."""
    scales = ["small", "medium", "large", "xlarge"]
    tasks = [benchmark_data[s]["tasks"] for s in scales]
    speedups = [benchmark_data[s]["speedup_mean"] for s in scales]

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.plot(tasks, speedups, marker="o", color="#3498db", linewidth=2.5, markersize=8, label="Empirical Speedup Ratio")

    for t, s in zip(tasks, speedups):
        ax.annotate(f"{s:,.1f}x",
                    xy=(t, s),
                    xytext=(0, 10),
                    textcoords="offset points",
                    ha="center",
                    fontsize=9.5,
                    fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="#ecf0f1", edgecolor="#bdc3c7", alpha=0.9))

    ax.set_xlabel("Number of Tasks in Workflow DAG (N)")
    ax.set_ylabel("Speedup Ratio (Baseline Time / Optimized Time)")
    ax.set_title("Empirical Speedup Scaling vs Workflow Problem Size", pad=12, fontweight="bold")
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.legend(frameon=True, loc="upper left")

    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "02_speedup_scaling_curve.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {out_path}")

def plot_profiling_bottleneck_breakdown():
    """Plot 3: cProfile cumulative time bottleneck breakdown for Baseline."""
    # From cProfile on 250 tasks:
    # _collect_all_descendants / compute_dynamic_priority: 1.154s (52.3%)
    # _collect_all_ancestors / is_task_ready: 1.030s (46.7%)
    # list pop / dict queries / loop overhead: 0.021s (1.0%)
    categories = [
        "Dynamic Priority Calculation\n(_collect_all_descendants)",
        "Readiness Verification\n(_collect_all_ancestors)",
        "Other Overhead\n(dict/list operations, loop control)"
    ]
    times = [1.154, 1.030, 0.021]
    percentages = [52.3, 46.7, 1.0]
    colors = ["#e74c3c", "#e67e22", "#95a5a6"]

    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    bars = ax.barh(categories, times, color=colors, edgecolor="black", height=0.55)

    for bar, pct, t in zip(bars, percentages, times):
        ax.text(t + 0.02, bar.get_y() + bar.get_height()/2, f"{t:.3f} s ({pct:.1f}%)",
                va="center", ha="left", fontsize=9.5, fontweight="bold")

    ax.set_xlim(0, 1.45)
    ax.set_xlabel("Cumulative CPU Execution Time (seconds)")
    ax.set_title("cProfile Execution Bottleneck Breakdown (Baseline Scheduler, N=250)", pad=12, fontweight="bold")
    ax.invert_yaxis()

    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "03_profiling_bottleneck_breakdown.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {out_path}")

def plot_memory_footprint_scaling(benchmark_data: dict):
    """Plot 4: Peak memory footprint scaling across problem scales."""
    scales = ["small", "medium", "large", "xlarge"]
    tasks = [benchmark_data[s]["tasks"] for s in scales]
    labels = [f"{s.capitalize()}\n(N={t})" for s, t in zip(scales, tasks)]

    base_mem = [benchmark_data[s]["baseline"]["peak_memory_kb"] for s in scales]
    opt_mem = [benchmark_data[s]["optimized"]["peak_memory_kb"] for s in scales]

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    x = np.arange(len(scales))
    width = 0.35

    rects1 = ax.bar(x - width/2, base_mem, width,
                    label="Baseline Scheduler", color="#9b59b6", alpha=0.9, edgecolor="black")
    rects2 = ax.bar(x + width/2, opt_mem, width,
                    label="Optimized DP Scheduler", color="#1abc9c", alpha=0.9, edgecolor="black")

    ax.set_ylabel("Peak Traced Memory (KB)")
    ax.set_title("Peak Memory Allocation Across Problem Scales (tracemalloc)", pad=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(frameon=True, loc="upper left")

    # Add text labels on top of bars
    for i in range(len(scales)):
        ax.text(x[i] - width/2, base_mem[i] + max(base_mem)*0.02, f"{base_mem[i]:.1f} KB",
                ha="center", va="bottom", fontsize=8.5, fontweight="semibold")
        ax.text(x[i] + width/2, opt_mem[i] + max(opt_mem)*0.02, f"{opt_mem[i]:.1f} KB",
                ha="center", va="bottom", fontsize=8.5, fontweight="semibold")

    # Leave room for annotations
    ax.set_ylim(0, max(max(base_mem), max(opt_mem)) * 1.18)

    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "04_memory_footprint_scaling.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {out_path}")

def generate_all_plots():
    """Load benchmark results and generate all 4 publication-quality plots."""
    json_path = os.path.join(RESULTS_DIR, "benchmark_results.json")
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found. Please run benchmark_runner.py first.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("--- Generating Publication Plots for Track J ---")
    plot_execution_time_comparison(data)
    plot_speedup_scaling_curve(data)
    plot_profiling_bottleneck_breakdown()
    plot_memory_footprint_scaling(data)
    print("All plots successfully generated in:", PLOTS_DIR)

if __name__ == "__main__":
    generate_all_plots()
