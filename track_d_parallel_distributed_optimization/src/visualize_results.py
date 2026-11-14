r"""Visualization Module for Track D: Parallel and Distributed Optimization.

Generates 6 publication-ready figures in track_d_parallel_distributed_optimization/plots/:
1. 01_submodular_greedy_vs_exact.png
2. 02_runtime_vs_problem_size.png
3. 03_theoretical_amdahl_gustafson.png
4. 04_measured_parallel_speedup_efficiency.png
5. 05_fedavg_training_iid_vs_non_iid.png
6. 06_mgda_and_gradnorm_balancing.png
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


def plot_01_submodular(res_dir: str, plot_dir: str):
    """Figure 1: Submodular Greedy vs Exact Optimum and Diminishing Returns."""
    json_path = os.path.join(res_dir, "submodular_benchmark_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    exact_data = [d for d in data if d["has_exact"]]

    names = [d["name"] for d in exact_data]
    exact_vals = [d["exact_coverage"] for d in exact_data]
    greedy_vals = [d["greedy_coverage"] for d in exact_data]
    theo_bounds = [d["theoretical_1_minus_1_over_e_bound"] for d in exact_data]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    # Left: Exact vs Greedy vs (1 - 1/e) bound
    x = np.arange(len(names))
    width = 0.25

    ax1.bar(x - width, exact_vals, width, label="Exact Optimal $f^*$", color="#2b5c8f")
    ax1.bar(x, greedy_vals, width, label="Greedy Solution $f(A_{\\mathrm{greedy}})$", color="#2ca02c")
    ax1.bar(x + width, theo_bounds, width, label="Theoretical Bound $(1 - 1/e)f^*$", color="#d62728", alpha=0.7)

    ax1.set_xlabel("Instance")
    ax1.set_ylabel("Covered Elements Count")
    ax1.set_title("Greedy vs. Exact Optimum (Submodular Coverage)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(names)
    ax1.legend(loc="upper left")

    # Right: Marginal Gain Decay (Diminishing Returns) for a selected instance
    selected_inst = data[3]  # Borderline-20
    gains = selected_inst["marginal_gains"]
    steps = np.arange(1, len(gains) + 1)

    ax2.plot(steps, gains, "o-", color="#8c564b", lw=2, markersize=7, label="Marginal Gain $\\Delta(S_t \\mid A_{t-1})$")
    ax2.set_xlabel("Greedy Selection Step $t$")
    ax2.set_ylabel("Marginal Coverage Gain")
    ax2.set_title(f"Diminishing Returns Property ({selected_inst['name']})")
    ax2.set_xticks(steps)
    ax2.legend(loc="upper right")

    plt.tight_layout()
    out_file = os.path.join(plot_dir, "01_submodular_greedy_vs_exact.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_02_runtime_scaling(res_dir: str, plot_dir: str):
    """Figure 2: Runtime vs Problem Size (Submodular and Parallel)."""
    sub_json = os.path.join(res_dir, "submodular_benchmark_results.json")
    par_json = os.path.join(res_dir, "parallel_benchmark_results.json")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    # Left: Submodular Greedy vs Exact Runtime
    if os.path.exists(sub_json):
        with open(sub_json, "r", encoding="utf-8") as f:
            sub_data = json.load(f)
        exact_entries = [d for d in sub_data if d["has_exact"]]
        names = [d["name"] for d in exact_entries]
        t_greedy = [d["greedy_runtime_ms"] for d in exact_entries]
        t_exact = [d["exact_runtime_ms"] for d in exact_entries]

        x = np.arange(len(names))
        ax1.plot(x, t_exact, "s-", color="#d62728", lw=2, markersize=6, label="Exact Search (Combinatorial)")
        ax1.plot(x, t_greedy, "o-", color="#1f77b4", lw=2, markersize=6, label="Greedy Heuristic (Polynomial)")
        ax1.set_yscale("log")
        ax1.set_xlabel("Problem Instance Scale")
        ax1.set_ylabel("Execution Time (ms, log scale)")
        ax1.set_title("Combinatorial Explosion vs. Greedy Scalability")
        ax1.set_xticks(x)
        ax1.set_xticklabels(names)
        ax1.legend(loc="upper left")

    # Right: Parallel Runtime across Scales
    if os.path.exists(par_json):
        with open(par_json, "r", encoding="utf-8") as f:
            par_data = json.load(f)

        colors = {"Small": "#1f77b4", "Medium": "#ff7f0e", "Large": "#2ca02c"}
        for scale in ["Small", "Medium", "Large"]:
            scale_entries = [d for d in par_data if d["problem_scale"] == scale and d["mode"] == "multiprocessing_pool"]
            if not scale_entries:
                continue
            workers = [d["worker_count"] for d in scale_entries]
            times = [d["mean_time_sec"] for d in scale_entries]
            ax2.plot(workers, times, "o-", color=colors[scale], lw=2, label=f"{scale} Workload")

        ax2.set_xlabel("Worker Count $P$")
        ax2.set_ylabel("Wall-Clock Execution Time (s)")
        ax2.set_title("Parallel Compute Wall-Clock Time")
        ax2.set_xticks([1, 2, 4, 8])
        ax2.legend(loc="upper right")

    plt.tight_layout()
    out_file = os.path.join(plot_dir, "02_runtime_vs_problem_size.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_03_theoretical_scaling(res_dir: str, plot_dir: str):
    """Figure 3: Theoretical Amdahl's Law vs Gustafson's Law."""
    json_path = os.path.join(res_dir, "amdahl_gustafson_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    theo = data["theoretical_curves"]
    workers = theo["worker_counts"]
    amdahl = theo["amdahl_curves"]
    gustafson = theo["gustafson_curves"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    colors = ["#7f7f7f", "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    # Left: Amdahl's Law (Strong Scaling)
    for idx, (p_key, curve) in enumerate(amdahl.items()):
        ax1.plot(workers, curve, "-", color=colors[idx], lw=2, label=f"{p_key}")
        asymptote = theo["asymptotic_limits"][p_key]
        if asymptote < 35:
            ax1.axhline(asymptote, ls=":", color=colors[idx], alpha=0.5)

    ax1.set_xlabel("Worker Count $N$")
    ax1.set_ylabel("Speedup $S(N)$")
    ax1.set_title("Amdahl's Law (Strong Scaling, Fixed Workload)")
    ax1.legend(loc="upper left")

    # Right: Gustafson's Law (Weak Scaling)
    for idx, (p_key, curve) in enumerate(gustafson.items()):
        ax2.plot(workers, curve, "-", color=colors[idx], lw=2, label=f"{p_key}")

    ax2.plot(workers, workers, "k--", lw=1.5, alpha=0.6, label="Ideal Linear")
    ax2.set_xlabel("Worker Count $N$")
    ax2.set_ylabel("Scaled Speedup $S(N)$")
    ax2.set_title("Gustafson's Law (Weak Scaling, Scaled Workload)")
    ax2.legend(loc="upper left")

    plt.tight_layout()
    out_file = os.path.join(plot_dir, "03_theoretical_amdahl_gustafson.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_04_measured_speedup_efficiency(res_dir: str, plot_dir: str):
    """Figure 4: Measured Speedup and Parallel Efficiency."""
    par_json = os.path.join(res_dir, "parallel_benchmark_results.json")
    amd_json = os.path.join(res_dir, "amdahl_gustafson_results.json")
    if not os.path.exists(par_json):
        return

    with open(par_json, "r", encoding="utf-8") as f:
        par_data = json.load(f)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    colors = {"Small": "#1f77b4", "Medium": "#ff7f0e", "Large": "#2ca02c"}

    for scale in ["Small", "Medium", "Large"]:
        scale_entries = [d for d in par_data if d["problem_scale"] == scale and d["mode"] == "multiprocessing_pool"]
        if not scale_entries:
            continue
        workers = [d["worker_count"] for d in scale_entries]
        speedups = [d["speedup"] for d in scale_entries]
        effs = [d["efficiency"] for d in scale_entries]

        ax1.plot(workers, speedups, "o-", color=colors[scale], lw=2, label=f"Measured: {scale}")
        ax2.plot(workers, effs, "s-", color=colors[scale], lw=2, label=f"Efficiency: {scale}")

    # Plot ideal linear speedup
    workers_ideal = [1, 2, 4, 8]
    ax1.plot(workers_ideal, workers_ideal, "k--", lw=1.5, alpha=0.7, label="Ideal Linear")
    ax2.axhline(1.0, ls="--", color="black", alpha=0.7, label="Ideal 100%")

    # Add fitted Amdahl curve if available
    if os.path.exists(amd_json):
        with open(amd_json, "r", encoding="utf-8") as f:
            amd_data = json.load(f)
        p_est = amd_data["empirical_fit"]["estimated_parallel_fraction"]
        fine_w = np.linspace(1, 8, 50)
        s_fit = 1.0 - p_est
        fit_speedup = 1.0 / (s_fit + p_est / fine_w)
        ax1.plot(fine_w, fit_speedup, ":", color="#d62728", lw=2, label=f"Amdahl Fit (P={p_est:.1%})")

    ax1.set_xlabel("Worker Count $P$")
    ax1.set_ylabel("Measured Speedup $S_P = T_1 / T_P$")
    ax1.set_title("Empirical Multiprocessing Speedup")
    ax1.set_xticks([1, 2, 4, 8])
    ax1.legend(loc="upper left")

    ax2.set_xlabel("Worker Count $P$")
    ax2.set_ylabel("Parallel Efficiency $E_P = S_P / P$")
    ax2.set_title("Empirical Parallel Efficiency")
    ax2.set_xticks([1, 2, 4, 8])
    ax2.set_ylim([0.0, 1.15])
    ax2.legend(loc="lower left")

    plt.tight_layout()
    out_file = os.path.join(plot_dir, "04_measured_parallel_speedup_efficiency.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_05_fedavg(res_dir: str, plot_dir: str):
    """Figure 5: FedAvg Training Curves (Centralized vs IID vs Non-IID)."""
    json_path = os.path.join(res_dir, "fedavg_benchmark_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cent = data["centralized"]
    iid = data["fedavg_iid"]
    non_iid = data["fedavg_non_iid"]

    rounds = np.arange(1, len(cent["loss_history"]) + 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    # Left: Evaluation Loss
    ax1.plot(rounds, cent["loss_history"], "k-", lw=2.2, label="Centralized (Ideal)")
    ax1.plot(rounds, iid["loss_history"], "o-", color="#1f77b4", lw=1.8, markersize=4, label="FedAvg (IID)")
    ax1.plot(rounds, non_iid["loss_history"], "s-", color="#d62728", lw=1.8, markersize=4, label="FedAvg (Non-IID)")

    ax1.set_xlabel("Communication Round")
    ax1.set_ylabel("Global Test Loss (Cross-Entropy)")
    ax1.set_title("FedAvg Convergence: IID vs. Non-IID")
    ax1.legend(loc="upper right")

    # Right: Test Accuracy & Client Drift
    ax2.plot(rounds, cent["accuracy_history"], "k--", lw=1.8, label="Centralized Accuracy")
    ax2.plot(rounds, iid["accuracy_history"], "o-", color="#1f77b4", lw=1.8, markersize=4, label="FedAvg IID Accuracy")
    ax2.plot(rounds, non_iid["accuracy_history"], "s-", color="#d62728", lw=1.8, markersize=4, label="FedAvg Non-IID Accuracy")

    ax2_twin = ax2.twinx()
    ax2_twin.plot(rounds, non_iid["divergence_history"], ":", color="#ff7f0e", lw=2, label="Non-IID Client Drift")
    ax2_twin.set_ylabel("Client Parameter Drift $\\|\\theta_k - \\theta_{\\mathrm{global}}\\|_2$", color="#ff7f0e")
    ax2_twin.tick_params(axis="y", labelcolor="#ff7f0e")
    ax2_twin.grid(False)

    ax2.set_xlabel("Communication Round")
    ax2.set_ylabel("Global Test Classification Accuracy")
    ax2.set_title("Test Accuracy & Client Parameter Divergence")
    ax2.set_ylim([0.0, 1.05])
    ax2.legend(loc="lower right")

    plt.tight_layout()
    out_file = os.path.join(plot_dir, "05_fedavg_training_iid_vs_non_iid.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_06_mgda_and_gradnorm(res_dir: str, plot_dir: str):
    """Figure 6: MGDA Multi-Objective Optimization & GradNorm Balancing."""
    mgda_json = os.path.join(res_dir, "mgda_benchmark_results.json")
    grad_json = os.path.join(res_dir, "gradnorm_benchmark_results.json")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    # Left: MGDA Trajectory vs Weighted Sum on Conflicting Quadratics
    if os.path.exists(mgda_json):
        with open(mgda_json, "r", encoding="utf-8") as f:
            mgda_data = json.load(f)["conflicting_quadratics"]

        # Pareto front line segment: x2 = 0, -1 <= x1 <= 1
        ax1.plot([-1, 1], [0, 0], "k-", lw=3.5, label="Pareto Front", zorder=3)
        ax1.plot([-1, 1], [0, 0], "k*", markersize=10, zorder=4)

        colors = {
            "mgda": "#2ca02c",
            "weighted_sum_05_05": "#1f77b4",
            "weighted_sum_08_02": "#ff7f0e",
            "weighted_sum_02_08": "#d62728",
        }
        labels = {
            "mgda": "MGDA (Descent to Front)",
            "weighted_sum_05_05": "Weighted Sum (0.5 / 0.5)",
            "weighted_sum_08_02": "Weighted Sum (0.8 / 0.2)",
            "weighted_sum_02_08": "Weighted Sum (0.2 / 0.8)",
        }

        for key, color in colors.items():
            entry = mgda_data[key]
            traj = np.array(entry["trajectory"])
            ax1.plot(traj[:, 0], traj[:, 1], ".-", color=color, lw=1.8, label=labels[key])
            ax1.plot(traj[0, 0], traj[0, 1], "ko", markersize=6)
            ax1.plot(traj[-1, 0], traj[-1, 1], "X", color=color, markersize=8)

        ax1.set_xlabel("$x_1$")
        ax1.set_ylabel("$x_2$")
        ax1.set_title("MGDA vs. Weighted-Sum Optimization Trajectory")
        ax1.legend(loc="upper left")

    # Right: GradNorm Task Weights Evolution
    if os.path.exists(grad_json):
        with open(grad_json, "r", encoding="utf-8") as f:
            grad_data = json.load(f)

        gn = grad_data["gradnorm"]
        epochs = np.arange(1, len(gn["history_w1"]) + 1)

        ax2.plot(epochs, gn["history_w1"], "-", color="#1f77b4", lw=2, label="Task 1 Weight $w_1$ (Simpler Task)")
        ax2.plot(epochs, gn["history_w2"], "-", color="#d62728", lw=2, label="Task 2 Weight $w_2$ (Harder Task)")
        ax2.axhline(1.0, ls="--", color="gray", alpha=0.6, label="Fixed Baseline ($w_1=w_2=1.0$)")

        ax2.set_xlabel("Training Epoch")
        ax2.set_ylabel("Dynamic Task Weight $w_i(t)$")
        ax2.set_title("GradNorm Dynamic Task Weight Adaptation")
        ax2.legend(loc="center right")

    plt.tight_layout()
    out_file = os.path.join(plot_dir, "06_mgda_and_gradnorm_balancing.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def main():
    res_dir = "track_d_parallel_distributed_optimization/results"
    plot_dir = "track_d_parallel_distributed_optimization/plots"
    os.makedirs(plot_dir, exist_ok=True)
    set_plot_style()

    print("Generating Track D Visualizations...")
    plot_01_submodular(res_dir, plot_dir)
    plot_02_runtime_scaling(res_dir, plot_dir)
    plot_03_theoretical_scaling(res_dir, plot_dir)
    plot_04_measured_speedup_efficiency(res_dir, plot_dir)
    plot_05_fedavg(res_dir, plot_dir)
    plot_06_mgda_and_gradnorm(res_dir, plot_dir)
    print("All 6 figures generated successfully in track_d_parallel_distributed_optimization/plots/")


if __name__ == "__main__":
    main()

