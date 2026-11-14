"""
Comparative Visualizations Suite
Track E: Railway Route and Transfer Optimization
Assignment 8 - Optimize Anything

Generates 4 publication-ready 300 DPI Matplotlib figures:
1. track_e_case_study/plots/04_journey_duration_comparison.png
2. track_e_case_study/plots/05_algorithm_latency_comparison.png
3. track_e_case_study/plots/06_waiting_time_and_transfers_comparison.png
4. track_e_case_study/plots/07_solution_quality_optimality_gap.png
"""

import json
import os
import tempfile
from typing import Dict, List

os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "matplotlib")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def load_benchmark_data() -> Dict:
    json_path = os.path.join(RESULTS_DIR, "comparative_benchmark_results.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Benchmark results missing at {json_path}. Run benchmark_comparison.py first.")
    with open(json_path, mode="r", encoding="utf-8") as f:
        return json.load(f)


def plot_04_journey_duration_comparison(data: Dict, output_path: str):
    """Plot grouped bar chart of total journey duration across all 20 queries."""
    queries = data["query_results"]
    q_labels = [f"Q{q['query_id']:02d}" for q in queries]
    dijk_dur = [q["dijkstra"]["journey_dur_min"] for q in queries]
    greedy_dur = [q["greedy"]["journey_dur_min"] for q in queries]
    ilp_dur = [q["ilp"]["journey_dur_min"] for q in queries]

    x = np.arange(len(q_labels))
    width = 0.26

    fig, ax = plt.subplots(figsize=(14, 6.5), dpi=300)

    r1 = ax.bar(x - width, dijk_dur, width, label="Time-Dependent Dijkstra (Baseline)", color="#1f77b4", alpha=0.85, edgecolor="black")
    r2 = ax.bar(x, greedy_dur, width, label="Greedy Heuristic", color="#ff7f0e", alpha=0.85, edgecolor="black")
    r3 = ax.bar(x + width, ilp_dur, width, label="Exact ILP (HiGHS)", color="#2ca02c", alpha=0.9, edgecolor="black")

    ax.set_title("Journey Duration Comparison Across 20 Benchmark Queries", fontsize=13, weight="bold", pad=12)
    ax.set_ylabel("Total Journey Duration (Minutes)", fontsize=11, weight="bold")
    ax.set_xlabel("Benchmark Query Identifier", fontsize=11, weight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(q_labels, fontsize=9)
    ax.legend(loc="upper left", frameon=True, fontsize=9.5)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"  Plot 4 saved: {output_path}")


def plot_05_algorithm_latency_comparison(data: Dict, output_path: str):
    """Plot execution latency comparison on log scale demonstrating runtime vs optimality trade-off."""
    queries = data["query_results"]
    q_labels = [f"Q{q['query_id']:02d}" for q in queries]
    dijk_lat = [q["dijkstra"]["latency_ms"] for q in queries]
    greedy_lat = [q["greedy"]["latency_ms"] for q in queries]
    ilp_lat = [q["ilp"]["latency_ms"] for q in queries]

    x = np.arange(len(q_labels))
    width = 0.26

    fig, ax = plt.subplots(figsize=(14, 6.5), dpi=300)

    ax.bar(x - width, dijk_lat, width, label=f"Dijkstra (Mean: {np.mean(dijk_lat):.3f} ms)", color="#1f77b4", alpha=0.85, edgecolor="black")
    ax.bar(x, greedy_lat, width, label=f"Greedy (Mean: {np.mean(greedy_lat):.3f} ms)", color="#ff7f0e", alpha=0.85, edgecolor="black")
    ax.bar(x + width, ilp_lat, width, label=f"Exact ILP (Mean: {np.mean(ilp_lat):.1f} ms)", color="#2ca02c", alpha=0.85, edgecolor="black")

    ax.set_yscale("log")
    ax.set_title("Algorithmic Execution Latency Comparison (Logarithmic Scale)", fontsize=13, weight="bold", pad=12)
    ax.set_ylabel("Execution Latency (Milliseconds, Log Scale)", fontsize=11, weight="bold")
    ax.set_xlabel("Benchmark Query Identifier", fontsize=11, weight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(q_labels, fontsize=9)
    ax.legend(loc="upper left", frameon=True, fontsize=9.5)
    ax.grid(True, axis="y", which="both", linestyle="--", alpha=0.4)

    # Annotation of speedup
    speedup_dijk_vs_ilp = np.mean(ilp_lat) / np.mean(dijk_lat)
    ax.text(
        0.70, 0.85,
        f"Speedup Factors:\n• Dijkstra is ~{speedup_dijk_vs_ilp:.0f}x faster than ILP\n• Greedy is ~{np.mean(ilp_lat)/np.mean(greedy_lat):.0f}x faster than ILP",
        transform=ax.transAxes,
        fontsize=9.5,
        weight="bold",
        bbox=dict(boxstyle="round,pad=0.5", fc="#ffffdd", ec="#ccccaa", lw=1.0)
    )

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"  Plot 5 saved: {output_path}")


def plot_06_waiting_time_and_transfers(data: Dict, output_path: str):
    """Plot transfer waiting time and total transfer count across algorithms."""
    summary = data["aggregate_summary"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)

    algos = ["Dijkstra\n(Baseline)", "Greedy\nHeuristic", "Exact ILP\n(HiGHS)"]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    # Subplot 1: Waiting Time
    avg_waits = [summary["dijkstra"]["avg_wait_min"], summary["greedy"]["avg_wait_min"], summary["ilp"]["avg_wait_min"]]
    bars1 = ax1.bar(algos, avg_waits, color=colors, width=0.5, edgecolor="black", alpha=0.85)
    ax1.set_ylabel("Average Transfer Waiting Time (Minutes)", fontsize=10.5, weight="bold")
    ax1.set_title("Mean Transfer Waiting Time Across Queries", fontsize=11.5, weight="bold", pad=10)
    ax1.grid(True, axis="y", linestyle="--", alpha=0.4)
    for b in bars1:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width() / 2.0, h + 1.2, f"{h:.1f} min", ha="center", weight="bold", fontsize=9.5)

    # Subplot 2: Transfers Count
    avg_xfers = [summary["dijkstra"]["avg_transfers"], summary["greedy"]["avg_transfers"], summary["ilp"]["avg_transfers"]]
    bars2 = ax2.bar(algos, avg_xfers, color=colors, width=0.5, edgecolor="black", alpha=0.85)
    ax2.set_ylabel("Average Number of Transfers", fontsize=10.5, weight="bold")
    ax2.set_title("Mean Interchange Transfers Count", fontsize=11.5, weight="bold", pad=10)
    ax2.grid(True, axis="y", linestyle="--", alpha=0.4)
    for b in bars2:
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width() / 2.0, h + 0.02, f"{h:.2f}", ha="center", weight="bold", fontsize=9.5)

    plt.suptitle("Interchange Inconvenience Metrics: Platform Waiting vs. Transfer Reductions", fontsize=13, weight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"  Plot 6 saved: {output_path}")


def plot_07_solution_quality_optimality_gap(data: Dict, output_path: str):
    """Plot optimality gap (%) of Dijkstra and Greedy against proven optimal ILP."""
    queries = data["query_results"]
    q_labels = [f"Q{q['query_id']:02d}" for q in queries]
    dijk_gaps = [q["dijkstra"]["optimality_gap_pct"] for q in queries]
    greedy_gaps = [q["greedy"]["optimality_gap_pct"] for q in queries]

    x = np.arange(len(q_labels))
    width = 0.38

    fig, ax = plt.subplots(figsize=(14, 6.5), dpi=300)

    ax.bar(x - width / 2.0, dijk_gaps, width, label="Dijkstra Optimality Gap (%)", color="#1f77b4", alpha=0.85, edgecolor="black")
    ax.bar(x + width / 2.0, greedy_gaps, width, label="Greedy Optimality Gap (%)", color="#ff7f0e", alpha=0.85, edgecolor="black")

    ax.axhline(0.0, color="#2ca02c", linestyle="-", linewidth=2.5, label="Exact ILP Proven Optimum (0.0% Gap Reference)")

    ax.set_title("Solution Quality & Optimality Gap Relative to Proven Optimal ILP", fontsize=13, weight="bold", pad=12)
    ax.set_ylabel("Suboptimality Gap (%) Relative to ILP", fontsize=11, weight="bold")
    ax.set_xlabel("Benchmark Query Identifier", fontsize=11, weight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(q_labels, fontsize=9)
    ax.legend(loc="upper left", frameon=True, fontsize=9.5)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"  Plot 7 saved: {output_path}")


def generate_all_comparative_plots():
    os.makedirs(PLOTS_DIR, exist_ok=True)
    data = load_benchmark_data()

    plot4_path = os.path.join(PLOTS_DIR, "04_journey_duration_comparison.png")
    plot_04_journey_duration_comparison(data, plot4_path)

    plot5_path = os.path.join(PLOTS_DIR, "05_algorithm_latency_comparison.png")
    plot_05_algorithm_latency_comparison(data, plot5_path)

    plot6_path = os.path.join(PLOTS_DIR, "06_waiting_time_and_transfers_comparison.png")
    plot_06_waiting_time_and_transfers(data, plot6_path)

    plot7_path = os.path.join(PLOTS_DIR, "07_solution_quality_optimality_gap.png")
    plot_07_solution_quality_optimality_gap(data, plot7_path)

    print("All 4 comparative plots generated successfully in track_e_case_study/plots/")


if __name__ == "__main__":
    generate_all_comparative_plots()
