r"""Visualization Module for Track F: Compiler Optimization.

Generates 4 publication-ready figures in track_f_compiler_optimization/plots/:
1. 01_ir_instruction_count_before_vs_after.png
2. 02_runtime_before_vs_after.png
3. 03_code_size_reduction.png
4. 04_compile_time_overhead_vs_runtime_savings.png
"""

import json
import os
import matplotlib.pyplot as plt
import numpy as np


def set_plot_style():
    """Apply standard clean academic plotting style."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "legend.fontsize": 9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "figure.titlesize": 13,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "axes.grid": True,
        "grid.alpha": 0.4,
        "grid.linestyle": "--",
    })


def plot_01_ir_counts(res_dir: str, plot_dir: str):
    """Figure 1: IR Instruction Count Before vs After Optimization."""
    json_path = os.path.join(res_dir, "compiler_benchmark_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    names = [d["name"] for d in data]
    unopt_counts = [d["unoptimized_ir_count"] for d in data]
    opt_counts = [d["optimized_ir_count"] for d in data]

    x = np.arange(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 4.8))
    rects1 = ax.bar(x - width/2, unopt_counts, width, label="Unoptimized IR (3AC)", color="#d62728", alpha=0.85)
    rects2 = ax.bar(x + width/2, opt_counts, width, label="Optimized IR (Fixpoint)", color="#2ca02c", alpha=0.85)

    ax.set_ylabel("IR Instruction Count")
    ax.set_title("Three-Address-Code (3AC) Instruction Count Before vs. After Optimization")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15, ha="right")
    ax.legend(loc="upper right")

    # Add count labels on top of bars
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h}", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8)
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h}", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    out_file = os.path.join(plot_dir, "01_ir_instruction_count_before_vs_after.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_02_runtime(res_dir: str, plot_dir: str):
    """Figure 2: Execution Time and Step Count Before vs After."""
    json_path = os.path.join(res_dir, "compiler_benchmark_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    names = [d["name"] for d in data]
    unopt_steps = [d["unoptimized_steps"] for d in data]
    opt_steps = [d["optimized_steps"] for d in data]
    speedups = [d["runtime_speedup"] for d in data]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    # Left: Step counts
    x = np.arange(len(names))
    width = 0.35
    ax1.bar(x - width/2, unopt_steps, width, label="Unoptimized Steps", color="#1f77b4", alpha=0.85)
    ax1.bar(x + width/2, opt_steps, width, label="Optimized Steps", color="#2ca02c", alpha=0.85)
    ax1.set_ylabel("Execution Steps / Cycles (Log Scale)")
    ax1.set_yscale("log")
    ax1.set_title("Virtual Machine Execution Steps (Cycles)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=15, ha="right")
    ax1.legend(loc="upper left")

    # Right: Runtime speedup
    bars = ax2.bar(x, speedups, color="#ff7f0e", width=0.5, alpha=0.85)
    ax2.axhline(1.0, ls="--", color="black", lw=1.2, label="1.0x Baseline")
    ax2.set_ylabel("Execution Speedup ($T_{\\mathrm{unopt}} / T_{\\mathrm{opt}}$)")
    ax2.set_title("Runtime Execution Speedup")
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, rotation=15, ha="right")
    ax2.legend(loc="upper left")

    for bar in bars:
        h = bar.get_height()
        ax2.annotate(f"{h:.1f}x", xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    out_file = os.path.join(plot_dir, "02_runtime_before_vs_after.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_03_code_size_reduction(res_dir: str, plot_dir: str):
    """Figure 3: Code Size / Instruction Reduction Percentage."""
    json_path = os.path.join(res_dir, "compiler_benchmark_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    names = [d["name"] for d in data]
    ir_red = [d["ir_reduction_pct"] for d in data]
    step_red = [d["step_reduction_pct"] for d in data]

    x = np.arange(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 4.8))
    rects1 = ax.bar(x - width/2, ir_red, width, label="IR Code Size Reduction (%)", color="#9467bd", alpha=0.85)
    rects2 = ax.bar(x + width/2, step_red, width, label="Execution Cycle Reduction (%)", color="#17becf", alpha=0.85)

    ax.set_ylabel("Percentage Reduction (%)")
    ax.set_title("Code Size & Dynamic Execution Cycle Reduction")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15, ha="right")
    ax.set_ylim([0, 110])
    ax.legend(loc="upper right")

    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8)
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    out_file = os.path.join(plot_dir, "03_code_size_reduction.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_04_pass_selection_and_overhead(res_dir: str, plot_dir: str):
    """Figure 4: Pass Selection Optimization & Compile Overhead vs Savings."""
    pass_json = os.path.join(res_dir, "pass_selection_results.json")
    bench_json = os.path.join(res_dir, "compiler_benchmark_results.json")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    # Left: Pass Selection BILP Budget Frontier
    if os.path.exists(pass_json):
        with open(pass_json, "r", encoding="utf-8") as f:
            pass_data = json.load(f)

        budgets = [d["budget"] for d in pass_data]
        net_objs = [d["net_objective_value"] for d in pass_data]
        costs = [d["compile_cost"] for d in pass_data]
        pass_labels = ["+".join(d["selected_passes"]) for d in pass_data]

        ax1.plot(budgets, net_objs, "o-", color="#2b5c8f", lw=2, markersize=7, label="Net Optimization Score")
        ax1.plot(budgets, costs, "s--", color="#d62728", lw=1.8, markersize=6, label="Actual Compilation Cost")

        ax1.set_xlabel("Compile-Time Budget ($C_{\\mathrm{budget}}$)")
        ax1.set_ylabel("Optimization Score / Compilation Cost")
        ax1.set_title("Compiler Pass Selection (BILP Solution Frontier)")
        ax1.legend(loc="upper left")

        for i, txt in enumerate(pass_labels):
            ax1.annotate(txt, (budgets[i], net_objs[i]), textcoords="offset points", xytext=(0, 8),
                         ha="center", fontsize=7, rotation=10)

    # Right: Compile Overhead vs Runtime Savings
    if os.path.exists(bench_json):
        with open(bench_json, "r", encoding="utf-8") as f:
            b_data = json.load(f)

        names = [d["name"] for d in b_data]
        compile_ms = [d["compile_overhead_ms"] for d in b_data]
        saved_ms = [max(0.0, d["unoptimized_time_ms"] - d["optimized_time_ms"]) for d in b_data]

        x = np.arange(len(names))
        width = 0.35
        ax2.bar(x - width/2, compile_ms, width, label="Compile Overhead (ms)", color="#7f7f7f", alpha=0.85)
        ax2.bar(x + width/2, saved_ms, width, label="Runtime Saved / Run (ms)", color="#2ca02c", alpha=0.85)

        ax2.set_ylabel("Time (ms)")
        ax2.set_title("Compile Overhead vs. Runtime Savings per Run")
        ax2.set_xticks(x)
        ax2.set_xticklabels(names, rotation=15, ha="right")
        ax2.legend(loc="upper right")

    plt.tight_layout()
    out_file = os.path.join(plot_dir, "04_compile_time_overhead_vs_runtime_savings.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def main():
    res_dir = "track_f_compiler_optimization/results"
    plot_dir = "track_f_compiler_optimization/plots"
    os.makedirs(plot_dir, exist_ok=True)
    set_plot_style()

    print("Generating Track F Visualizations...")
    plot_01_ir_counts(res_dir, plot_dir)
    plot_02_runtime(res_dir, plot_dir)
    plot_03_code_size_reduction(res_dir, plot_dir)
    plot_04_pass_selection_and_overhead(res_dir, plot_dir)
    print("All 4 figures generated successfully in track_f_compiler_optimization/plots/")


if __name__ == "__main__":
    main()

