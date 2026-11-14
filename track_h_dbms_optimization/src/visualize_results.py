"""
Visualization Module for Track H DBMS Query Optimization.
Generates 4 publication-quality plots:
1. 01_query_latency_comparison.png (Grouped bar chart of query latencies across configurations)
2. 02_workload_runtime_and_throughput.png (Workload total time & QPS throughput)
3. 03_storage_overhead_vs_latency_reduction.png (Storage budget vs benefit Pareto frontier)
4. 04_query_plan_scan_vs_index_breakdown.png (SCAN TABLE vs SEARCH USING INDEX operations)
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["MPLCONFIGDIR"] = os.path.join(BASE_DIR, "results", ".matplotlib_cache")
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# Styling palette
COLORS = {
    "baseline": "#D9534F", # Red / Coral
    "greedy": "#F0AD4E",   # Amber / Orange
    "ilp": "#2E7D32",      # Forest Green
    "opt": "#1976D2",      # Blue
    "accent": "#4A148C"    # Deep Purple
}

def plot_query_latencies(benchmark_data):
    """Plot 1: Grouped bar chart comparing Baseline, Greedy, and ILP per-query latencies."""
    baseline_res = benchmark_data["configurations"]["baseline"]["query_results"]
    greedy_res = benchmark_data["configurations"]["greedy"]["query_results"]
    ilp_res = benchmark_data["configurations"]["ilp"]["query_results"]

    q_ids = [f"Q{i}" for i in range(1, 9)]
    b_lats = [baseline_res[q]["mean_ms"] for q in q_ids]
    g_lats = [greedy_res[q]["mean_ms"] for q in q_ids]
    i_lats = [ilp_res[q]["mean_ms"] for q in q_ids]

    x = np.arange(len(q_ids))
    width = 0.26

    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    rects1 = ax.bar(x - width, b_lats, width, label="Baseline (No Indexes)", color=COLORS["baseline"], alpha=0.9, edgecolor="black", linewidth=0.7)
    rects2 = ax.bar(x, g_lats, width, label="Greedy Selected (2.9 MB)", color=COLORS["greedy"], alpha=0.9, edgecolor="black", linewidth=0.7)
    rects3 = ax.bar(x + width, i_lats, width, label="ILP Selected (2.9 MB)", color=COLORS["ilp"], alpha=0.9, edgecolor="black", linewidth=0.7)

    ax.set_ylabel("Execution Time (milliseconds)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Workload Query", fontsize=12, fontweight="bold")
    ax.set_title("Track H: Per-Query Mean Latency Comparison Across Indexing Configurations", fontsize=14, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(q_ids, fontsize=11, fontweight="bold")
    ax.legend(fontsize=11, framealpha=0.95, loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Annotate significant speedup on Q8
    q8_idx = 7
    ilp_q8_speedup = b_lats[q8_idx] / i_lats[q8_idx]
    ax.annotate(f"ILP Speedup:\n{ilp_q8_speedup:.1f}x faster",
                xy=(x[q8_idx] + width, i_lats[q8_idx]),
                xytext=(x[q8_idx] + width - 0.2, 5.0),
                arrowprops=dict(facecolor=COLORS["accent"], shrink=0.08, width=1.5, headwidth=6),
                fontsize=9, fontweight="bold", color=COLORS["accent"],
                bbox=dict(boxstyle="round,pad=0.3", fc="#EDE7F6", ec=COLORS["accent"], lw=1))

    # Annotate Q4 speedup on Greedy
    q4_idx = 3
    greedy_q4_speedup = b_lats[q4_idx] / g_lats[q4_idx]
    ax.annotate(f"Greedy:\n{greedy_q4_speedup:.1f}x faster",
                xy=(x[q4_idx], g_lats[q4_idx]),
                xytext=(x[q4_idx] - 0.35, 4.0),
                arrowprops=dict(facecolor="#BF360C", shrink=0.08, width=1.5, headwidth=6),
                fontsize=9, fontweight="bold", color="#BF360C",
                bbox=dict(boxstyle="round,pad=0.3", fc="#FBE9E7", ec="#BF360C", lw=1))

    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "01_query_latency_comparison.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[INFO] Plot 1 saved to: {out_path}")

def plot_workload_runtime_and_throughput(benchmark_data):
    """Plot 2: Total Workload Execution Time and QPS Throughput."""
    cfg_names = ["Baseline\n(No Indexes)", "Greedy\n(2.9 MB)", "ILP\n(2.9 MB)"]
    configs = [
        benchmark_data["configurations"]["baseline"],
        benchmark_data["configurations"]["greedy"],
        benchmark_data["configurations"]["ilp"]
    ]

    total_runtimes_ms = [sum(res["mean_ms"] for res in cfg["query_results"].values()) for cfg in configs]
    qps_values = [cfg["throughput_qps"] for cfg in configs]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)

    # Subplot 1: Total Runtime
    bars1 = ax1.bar(cfg_names, total_runtimes_ms, color=[COLORS["baseline"], COLORS["greedy"], COLORS["ilp"]],
                    edgecolor="black", linewidth=0.8, width=0.55)
    ax1.set_ylabel("Total Workload Execution Time (ms)", fontsize=11, fontweight="bold")
    ax1.set_title("Total Workload Execution Time", fontsize=13, fontweight="bold")
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 1.2, f"{yval:.1f} ms",
                 ha="center", va="bottom", fontsize=10, fontweight="bold")

    # Subplot 2: Throughput (QPS)
    bars2 = ax2.bar(cfg_names, qps_values, color=[COLORS["baseline"], COLORS["greedy"], COLORS["ilp"]],
                    edgecolor="black", linewidth=0.8, width=0.55)
    ax2.set_ylabel("Workload Throughput (Queries / Sec)", fontsize=11, fontweight="bold")
    ax2.set_title("Overall Query Throughput (QPS)", fontsize=13, fontweight="bold")
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 1.5, f"{yval:.1f} QPS",
                 ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.suptitle("Track H: End-to-End Workload Performance and Throughput", fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "02_workload_runtime_and_throughput.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[INFO] Plot 2 saved to: {out_path}")

def plot_storage_vs_benefit_frontier(sweep_data):
    """Plot 3: Storage budget vs workload benefit score across budgets showing Pareto frontier."""
    budgets = [item["budget_mb"] for item in sweep_data]
    g_scores = [item["greedy"]["score"] for item in sweep_data]
    i_scores = [item["ilp"]["score"] for item in sweep_data]
    g_storage = [item["greedy"]["storage_mb"] for item in sweep_data]
    i_storage = [item["ilp"]["storage_mb"] for item in sweep_data]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    # Left: Benefit vs Budget Limit
    ax1.plot(budgets, i_scores, marker="o", linewidth=2.2, color=COLORS["ilp"], label="Exact ILP / Optimal Frontier", markersize=6)
    ax1.plot(budgets, g_scores, marker="s", linewidth=1.8, linestyle="--", color=COLORS["greedy"], label="Greedy Heuristic", markersize=6)
    ax1.set_xlabel("Storage Budget Limit $S_{max}$ (MB)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Workload Benefit Score", fontsize=11, fontweight="bold")
    ax1.set_title("Optimization Objective Value vs. Storage Budget", fontsize=12, fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(fontsize=10, loc="lower right")

    # Annotate budget 3.0 MB gap
    ax1.annotate("6.92% Optimality Gap\nat Budget = 3.0 MB",
                 xy=(3.0, 6520), xytext=(3.5, 5200),
                 arrowprops=dict(facecolor="red", shrink=0.08, width=1.5, headwidth=6),
                 fontsize=9, fontweight="bold", color="red",
                 bbox=dict(boxstyle="round,pad=0.3", fc="#FFEBEE", ec="red", lw=1))

    # Right: Optimality Gap (%) vs Budget
    gaps = [item["optimality_gap_pct"] for item in sweep_data]
    bars = ax2.bar(budgets, gaps, width=0.35, color="#D32F2F", alpha=0.85, edgecolor="black", linewidth=0.7)
    ax2.set_xlabel("Storage Budget Limit $S_{max}$ (MB)", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Greedy Optimality Gap (%)", fontsize=11, fontweight="bold")
    ax2.set_title("Greedy Heuristic Optimality Gap vs. Exact ILP", fontsize=12, fontweight="bold")
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax2.text(bar.get_x() + bar.get_width()/2.0, h + 0.15, f"{h:.1f}%",
                     ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#B71C1C")

    plt.suptitle("Track H: Storage-Benefit Pareto Frontier & Heuristic Approximation Gap", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "03_storage_overhead_vs_latency_reduction.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[INFO] Plot 3 saved to: {out_path}")

def plot_query_plan_breakdown():
    """Plot 4: Proportion and count of SCAN TABLE vs SEARCH TABLE USING INDEX."""
    baseline_plan_file = os.path.join(RESULTS_DIR, "baseline_plans.json")
    greedy_plan_file = os.path.join(RESULTS_DIR, "greedy_plans.json")
    ilp_plan_file = os.path.join(RESULTS_DIR, "ilp_plans.json")

    def analyze_plans(filename):
        with open(filename, "r", encoding="utf-8") as f:
            plans = json.load(f)
        scans = 0
        searches = 0
        for qid, plan_lines in plans.items():
            for line in plan_lines:
                if "SCAN" in line:
                    scans += 1
                elif "SEARCH" in line:
                    searches += 1
        return scans, searches

    b_scans, b_searches = analyze_plans(baseline_plan_file)
    g_scans, g_searches = analyze_plans(greedy_plan_file)
    i_scans, i_searches = analyze_plans(ilp_plan_file)

    categories = ["Baseline\n(No Indexes)", "Greedy\n(2.9 MB)", "ILP\n(2.9 MB)"]
    scans = [b_scans, g_scans, i_scans]
    searches = [b_searches, g_searches, i_searches]

    x = np.arange(len(categories))
    width = 0.45

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    p1 = ax.bar(categories, scans, width, label="SCAN TABLE (Full Table Scan)", color="#E57373", edgecolor="black", linewidth=0.8)
    p2 = ax.bar(categories, searches, width, bottom=scans, label="SEARCH TABLE (B-Tree Index Search)", color="#81C784", edgecolor="black", linewidth=0.8)

    ax.set_ylabel("Execution Plan Operator Count", fontsize=11, fontweight="bold")
    ax.set_title("Track H: SQLite Query Planner Operator Breakdown (EXPLAIN QUERY PLAN)", fontsize=13, fontweight="bold", pad=15)
    ax.legend(fontsize=10.5, loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for i in range(len(categories)):
        tot = scans[i] + searches[i]
        pct_idx = (searches[i] / tot * 100) if tot > 0 else 0
        ax.text(x[i], tot + 0.3, f"{searches[i]}/{tot} Indexed\n({pct_idx:.0f}%)",
                ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "04_query_plan_scan_vs_index_breakdown.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[INFO] Plot 4 saved to: {out_path}")

def generate_all_plots():
    bench_file = os.path.join(RESULTS_DIR, "benchmark_comparison.json")
    sweep_file = os.path.join(RESULTS_DIR, "budget_sweep_results.json")

    with open(bench_file, "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)

    with open(sweep_file, "r", encoding="utf-8") as f:
        sweep_data = json.load(f)

    plot_query_latencies(benchmark_data)
    plot_workload_runtime_and_throughput(benchmark_data)
    plot_storage_vs_benefit_frontier(sweep_data)
    plot_query_plan_breakdown()
    print("\n[SUCCESS] All 4 publication-quality plots generated in plots/.")

if __name__ == "__main__":
    generate_all_plots()
