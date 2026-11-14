r"""
Visualization Module for Track C: Quantum Optimization
Generates 5 publication-ready figures using Matplotlib:
  1. plots/01_qaoa_objective_convergence.png
  2. plots/02_qaoa_approximation_ratio_vs_depth.png
  3. plots/03_vqe_energy_convergence.png
  4. plots/04_parameter_shift_vs_finite_difference.png
  5. plots/05_shot_noise_and_barren_plateaus.png
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


def plot_01_qaoa_objective_convergence():
    """Figure 1: QAOA expected cut value convergence vs optimization iteration."""
    json_path = os.path.join(RESULTS_DIR, "qaoa_benchmark_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    for idx, run in enumerate(data):
        graph = run["graph"]
        p = run["p_depth"]
        hist = run.get("cost_history", [])
        if hist:
            ax.plot(
                hist,
                label=f"{graph} (p={p}, Max={run['classical_max_cut']:.1f})",
                color=colors[idx % len(colors)],
                linewidth=2.0
            )

    ax.set_title("QAOA Variational Optimization: Expected Cut Convergence", fontsize=13, fontweight="bold")
    ax.set_xlabel("Iteration (Downsampled)", fontsize=11)
    ax.set_ylabel(r"Expected Cut Value $\langle \psi(\gamma, \beta) | H_C | \psi(\gamma, \beta) \rangle$", fontsize=11)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(fontsize=9, loc="lower right")
    plt.tight_layout()

    out_file = os.path.join(PLOTS_DIR, "01_qaoa_objective_convergence.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_02_qaoa_approximation_ratio_vs_depth():
    """Figure 2: QAOA approximation ratio alpha vs circuit depth p."""
    json_path = os.path.join(RESULTS_DIR, "qaoa_benchmark_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)

    graphs = sorted(list(set(r["graph"] for r in data)))
    markers = ["o", "s", "^"]
    colors = ["#1f77b4", "#d62728"]

    for idx, g_name in enumerate(graphs):
        g_runs = [r for r in data if r["graph"] == g_name]
        g_runs = sorted(g_runs, key=lambda x: x["p_depth"])
        p_vals = [r["p_depth"] for r in g_runs]
        ratios = [r["approximation_ratio"] * 100.0 for r in g_runs]

        ax.plot(
            p_vals,
            ratios,
            marker=markers[idx % len(markers)],
            linewidth=2.2,
            markersize=8,
            color=colors[idx % len(colors)],
            label=f"{g_name}"
        )
        for p, r in zip(p_vals, ratios):
            ax.text(p, r + 1.2, f"{r:.1f}%", ha="center", fontsize=9, fontweight="bold")

    ax.axhline(100.0, color="black", linestyle="--", alpha=0.7, label="Exact Optimal (100%)")
    ax.set_title(r"QAOA Approximation Ratio $\alpha$ vs Circuit Depth $p$", fontsize=13, fontweight="bold")
    ax.set_xlabel("QAOA Depth p", fontsize=11)
    ax.set_ylabel(r"Approximation Ratio $\alpha = \langle H_C \rangle / C_{\max}$ (%)", fontsize=11)
    ax.set_ylim(45, 108)
    ax.set_xticks([1, 2, 3])
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(fontsize=10, loc="lower right")
    plt.tight_layout()

    out_file = os.path.join(PLOTS_DIR, "02_qaoa_approximation_ratio_vs_depth.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_03_vqe_energy_convergence():
    """Figure 3: VQE ground state energy convergence vs exact diagonalization."""
    json_path = os.path.join(RESULTS_DIR, "vqe_benchmark_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

    for idx, model_type in enumerate(["TFIM", "Heisenberg"]):
        ax = axes[idx]
        matching_runs = [r for r in data if model_type in r["model_name"]]
        colors = ["#1f77b4", "#ff7f0e"]

        for c_idx, run in enumerate(matching_runs):
            hist = run.get("energy_history", [])
            exact_e = run["exact_energy"]
            name = run["model_name"]
            err_pct = run["relative_error_pct"]

            ax.plot(
                hist,
                label=f"{name} (VQE: {run['vqe_energy']:.3f}, RelErr: {err_pct:.2f}%)",
                color=colors[c_idx % len(colors)],
                linewidth=2.0
            )
            ax.axhline(exact_e, color=colors[c_idx % len(colors)], linestyle="--", alpha=0.7)

        ax.set_title(f"VQE Convergence: {model_type} Spin Chain", fontsize=12, fontweight="bold")
        ax.set_xlabel("Iteration (Downsampled)", fontsize=11)
        ax.set_ylabel(r"Energy $\langle \psi(\theta) | H | \psi(\theta) \rangle$", fontsize=11)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(fontsize=9, loc="upper right")

    plt.tight_layout()
    out_file = os.path.join(PLOTS_DIR, "03_vqe_energy_convergence.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_04_parameter_shift_vs_finite_difference():
    """Figure 4: Parameter-Shift vs Finite Differences & SPSA Optimization."""
    json_path = os.path.join(RESULTS_DIR, "gradient_study_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

    # Left: Gradient norms Parameter-Shift vs Finite Difference across points
    ax_grad = axes[0]
    points = data.get("point_evaluations", [])
    p_ids = [p["point_id"] for p in points]
    ps_norms = [p["norm_parameter_shift"] for p in points]
    fd_norms = [p["norm_finite_diff"] for p in points]

    x = np.arange(len(p_ids))
    width = 0.35
    ax_grad.bar(x - width/2, ps_norms, width, label="Parameter-Shift Rule", color="#1f77b4", alpha=0.85)
    ax_grad.bar(x + width/2, fd_norms, width, label="Finite Differences", color="#2ca02c", alpha=0.85)

    ax_grad.set_title("Gradient Norms: Parameter-Shift vs Finite Differences", fontsize=12, fontweight="bold")
    ax_grad.set_xlabel("Test Circuit Evaluation Point", fontsize=11)
    ax_grad.set_ylabel(r"Gradient L2 Norm $\|\nabla \langle H \rangle\|_2$", fontsize=11)
    ax_grad.set_xticks(x)
    ax_grad.set_xticklabels([f"P{i}" for i in p_ids])
    ax_grad.grid(axis="y", linestyle=":", alpha=0.6)
    ax_grad.legend(fontsize=10)

    # Right: SPSA vs Parameter-Shift GD under noise
    ax_spsa = axes[1]
    noisy = data.get("noisy_optimization", {})
    spsa_hist = noisy.get("spsa_history", [])
    gd_hist = noisy.get("gd_history", [])

    ax_spsa.plot(spsa_hist, "o-", color="#d62728", label=f"SPSA (2 evals/step, {noisy.get('spsa_runtime_ms', 0):.0f}ms)", linewidth=2.0)
    ax_spsa.plot(gd_hist, "s-", color="#1f77b4", label=f"Param-Shift GD (24 evals/step, {noisy.get('gd_runtime_ms', 0):.0f}ms)", linewidth=2.0)

    ax_spsa.set_title("Noisy Optimization: SPSA vs Standard Gradient Descent", fontsize=12, fontweight="bold")
    ax_spsa.set_xlabel("Step (x4)", fontsize=11)
    ax_spsa.set_ylabel(r"Noisy Observable Expectation $\langle H \rangle$", fontsize=11)
    ax_spsa.grid(True, linestyle=":", alpha=0.6)
    ax_spsa.legend(fontsize=10)

    plt.tight_layout()
    out_file = os.path.join(PLOTS_DIR, "04_parameter_shift_vs_finite_difference.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_05_shot_noise_and_barren_plateaus():
    """Figure 5: Shot Noise Variance Scaling & Barren Plateau Gradient Variance Decay."""
    json_path = os.path.join(RESULTS_DIR, "noise_barren_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

    # Left: Shot noise variance vs shots S
    ax_shot = axes[0]
    shot_data = data.get("shot_noise_study", [])
    shots = [r["shots"] for r in shot_data]
    variances = [r["variance"] for r in shot_data]
    theo_factors = [(1.0 / s) * (variances[0] * shots[0]) for s in shots]

    ax_shot.plot(shots, variances, "o-", color="#1f77b4", linewidth=2.0, markersize=7, label=r"Empirical Variance $\mathrm{Var}[\hat{E}_S]$")
    ax_shot.plot(shots, theo_factors, "k--", linewidth=1.8, label=r"Theoretical $O(1/S)$ Scaling")
    ax_shot.set_title(r"Shot Noise: Variance Scaling $\mathrm{Var} \propto 1/S$", fontsize=12, fontweight="bold")
    ax_shot.set_xlabel("Measurement Shots S (log scale)", fontsize=11)
    ax_shot.set_ylabel(r"Expectation Variance $\mathrm{Var}[\hat{E}]$ (log scale)", fontsize=11)
    ax_shot.set_xscale("log")
    ax_shot.set_yscale("log")
    ax_shot.grid(True, which="both", linestyle=":", alpha=0.6)
    ax_shot.legend(fontsize=10)

    # Right: Barren Plateau gradient variance vs qubit count n
    ax_barren = axes[1]
    barren_data = data.get("barren_plateau_study", [])
    qubits = [r["num_qubits"] for r in barren_data]
    grad_vars = [r["gradient_variance"] for r in barren_data]
    theo_2n = [r["theoretical_2_minus_n"] * (grad_vars[0] / barren_data[0]["theoretical_2_minus_n"]) for r in barren_data]

    ax_barren.plot(qubits, grad_vars, "s-", color="#d62728", linewidth=2.0, markersize=7, label=r"Empirical $\mathrm{Var}[\partial_{\theta_0} \langle H \rangle]$")
    ax_barren.plot(qubits, theo_2n, "k--", linewidth=1.8, label=r"Theoretical $O(2^{-n})$ Scaling")
    ax_barren.set_title(r"Barren Plateau: Gradient Variance $\mathrm{Var} \propto 2^{-n}$", fontsize=12, fontweight="bold")
    ax_barren.set_xlabel("Number of Qubits n", fontsize=11)
    ax_barren.set_ylabel(r"Gradient Variance (log scale)", fontsize=11)
    ax_barren.set_yscale("log", base=2)
    ax_barren.grid(True, which="both", linestyle=":", alpha=0.6)
    ax_barren.legend(fontsize=10)

    plt.tight_layout()
    out_file = os.path.join(PLOTS_DIR, "05_shot_noise_and_barren_plateaus.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def generate_all_plots():
    os.makedirs(PLOTS_DIR, exist_ok=True)
    print("Generating Track C Visualizations...")
    plot_01_qaoa_objective_convergence()
    plot_02_qaoa_approximation_ratio_vs_depth()
    plot_03_vqe_energy_convergence()
    plot_04_parameter_shift_vs_finite_difference()
    plot_05_shot_noise_and_barren_plateaus()
    print("All 5 figures generated successfully in track_c_quantum_optimization/plots/")


if __name__ == "__main__":
    generate_all_plots()

