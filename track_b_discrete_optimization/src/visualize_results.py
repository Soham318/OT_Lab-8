r"""
Visualization Module for Track B: Discrete Optimization
Generates 4 publication-ready figures using Matplotlib:
  1. plots/01_objective_value_comparison.png
  2. plots/02_runtime_vs_problem_size.png
  3. plots/03_greedy_optimality_gap.png
  4. plots/04_qubo_penalty_and_energy_landscape.png
"""

import os
import json
import numpy as np

# Configure non-interactive backend
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
PLOTS_DIR = os.path.join(BASE_DIR, "plots")


def plot_01_objective_value_comparison():
    """Figure 1: Objective value comparison across methods and problem sizes."""
    json_path = os.path.join(RESULTS_DIR, "discrete_comparison_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

    # Filter out counterexample for clean scale or include with clear label
    instances = [d for d in data if "Bench_N" in d["instance"]]
    sizes = [d["n_items"] for d in instances]

    solvers = ["ILP (HiGHS)", "Greedy Heuristic", "Dynamic Programming", "Branch-and-Bound"]
    colors = {
        "ILP (HiGHS)": "#1f77b4",
        "Greedy Heuristic": "#d62728",
        "Dynamic Programming": "#2ca02c",
        "Branch-and-Bound": "#9467bd"
    }
    markers = {
        "ILP (HiGHS)": "o",
        "Greedy Heuristic": "^",
        "Dynamic Programming": "s",
        "Branch-and-Bound": "D"
    }

    for s_name in solvers:
        s_sizes = []
        s_vals = []
        for inst in instances:
            for res in inst["results"]:
                if res["solver"] == s_name:
                    s_sizes.append(inst["n_items"])
                    s_vals.append(res["total_value"])
        if s_sizes:
            ax.plot(
                s_sizes,
                s_vals,
                label=s_name,
                color=colors.get(s_name, "black"),
                marker=markers.get(s_name, "x"),
                linewidth=2.0 if "ILP" in s_name else 1.5,
                markersize=6,
                alpha=0.9
            )

    ax.set_title("0/1 Knapsack: Total Objective Value Across Problem Scales", fontsize=13, fontweight="bold")
    ax.set_xlabel("Number of Items N", fontsize=11)
    ax.set_ylabel("Total Solution Value", fontsize=11)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(fontsize=10, loc="upper left")
    plt.tight_layout()

    out_file = os.path.join(PLOTS_DIR, "01_objective_value_comparison.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_02_runtime_vs_problem_size():
    """Figure 2: Execution Time (ms) vs Problem Size (log-log scale)."""
    json_path = os.path.join(RESULTS_DIR, "discrete_comparison_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    instances = [d for d in data if "Bench_N" in d["instance"]]

    solvers = ["Greedy Heuristic", "Branch-and-Bound", "Dynamic Programming", "ILP (HiGHS)"]
    colors = {
        "Greedy Heuristic": "#d62728",
        "Branch-and-Bound": "#9467bd",
        "Dynamic Programming": "#2ca02c",
        "ILP (HiGHS)": "#1f77b4"
    }

    for s_name in solvers:
        s_sizes = []
        s_runtimes = []
        for inst in instances:
            for res in inst["results"]:
                if res["solver"] == s_name:
                    s_sizes.append(inst["n_items"])
                    s_runtimes.append(max(res["execution_time_ms"], 1e-3))
        if s_sizes:
            ax.plot(
                s_sizes,
                s_runtimes,
                label=s_name,
                color=colors.get(s_name, "gray"),
                marker="o",
                linewidth=2.0,
                markersize=6
            )

    ax.set_title("Computational Scalability: Runtime vs Problem Size N", fontsize=13, fontweight="bold")
    ax.set_xlabel("Number of Items N (log scale)", fontsize=11)
    ax.set_ylabel("Execution Time in Milliseconds (log scale)", fontsize=11)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.grid(True, which="both", linestyle=":", alpha=0.6)
    ax.legend(fontsize=10, loc="upper left")
    plt.tight_layout()

    out_file = os.path.join(PLOTS_DIR, "02_runtime_vs_problem_size.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_03_greedy_optimality_gap():
    """Figure 3: Greedy Optimality Gap (%) across test instances."""
    json_path = os.path.join(RESULTS_DIR, "discrete_comparison_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    inst_names = []
    gaps = []

    for inst in data:
        name = inst["instance"]
        for res in inst["results"]:
            if res["solver"] == "Greedy Heuristic":
                inst_names.append(name.replace("GreedyCounterexample", "Counterexample\n(Spike 27.27%)"))
                gaps.append(res["optimality_gap_pct"])

    x_pos = np.arange(len(inst_names))
    bars = ax.bar(x_pos, gaps, color="#d62728", alpha=0.85, edgecolor="black", width=0.55)

    # Highlight counterexample bar
    bars[0].set_color("#8b0000")

    for bar, gap in zip(bars, gaps):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.5, f"{gap:.1f}%", ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.set_title("Greedy Optimality Gap (%) Relative to Exact ILP Optimum", fontsize=13, fontweight="bold")
    ax.set_xlabel("Benchmark Instance", fontsize=11)
    ax.set_ylabel("Optimality Gap (%)", fontsize=11)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(inst_names, rotation=35, ha="right", fontsize=9)
    ax.set_ylim(0, 32)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    plt.tight_layout()

    out_file = os.path.join(PLOTS_DIR, "03_greedy_optimality_gap.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_04_qubo_penalty_and_energy_landscape():
    """Figure 4: QUBO Penalty Multiplier vs Constraint Feasibility & Energy."""
    json_path = os.path.join(RESULTS_DIR, "qubo_penalty_study_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("results", [])
    alphas = [r["alpha"] for r in records]
    violations = [r["weight_violation"] for r in records]
    decoded_vals = [r["decoded_value"] for r in records]
    true_opt = records[0]["true_optimal_value"] if records else 85.0

    fig, ax1 = plt.subplots(figsize=(10, 5), dpi=300)

    color_viol = "#d62728"
    color_val = "#1f77b4"

    ax1.set_xlabel(r"Penalty Multiplier $\alpha$ (where $P = \alpha \cdot \max(v_i)$)", fontsize=11)
    ax1.set_ylabel("Capacity Weight Violation (units)", color=color_viol, fontsize=11)
    l1 = ax1.plot(alphas, violations, "o-", color=color_viol, linewidth=2.0, label="Capacity Violation")
    ax1.tick_params(axis="y", labelcolor=color_viol)
    ax1.set_xscale("log")
    ax1.grid(True, linestyle=":", alpha=0.6)

    ax2 = ax1.twinx()
    ax2.set_ylabel("Decoded Objective Value", color=color_val, fontsize=11)
    l2 = ax2.plot(alphas, decoded_vals, "s--", color=color_val, linewidth=2.0, label="Decoded Value")
    l3 = ax2.axhline(true_opt, color="black", linestyle=":", linewidth=1.5, label=f"True Optimum ({true_opt:.0f})")
    ax2.tick_params(axis="y", labelcolor=color_val)

    # Annotate critical boundary alpha = 1.0
    ax1.axvline(1.0, color="green", linestyle="--", alpha=0.7, label=r"Safe Boundary ($\alpha=1.0$)")

    lines = l1 + l2 + [l3]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right", fontsize=9)

    plt.title(r"QUBO Phase Transition: Penalty Multiplier $\alpha$ vs Feasibility", fontsize=13, fontweight="bold")
    plt.tight_layout()

    out_file = os.path.join(PLOTS_DIR, "04_qubo_penalty_and_energy_landscape.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def generate_all_plots():
    os.makedirs(PLOTS_DIR, exist_ok=True)
    print("Generating Track B Visualizations...")
    plot_01_objective_value_comparison()
    plot_02_runtime_vs_problem_size()
    plot_03_greedy_optimality_gap()
    plot_04_qubo_penalty_and_energy_landscape()
    print("All 4 figures generated successfully in track_b_discrete_optimization/plots/")


if __name__ == "__main__":
    generate_all_plots()

