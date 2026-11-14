r"""
Visualization Module for Track A: Continuous Optimization
Generates 6 publication-ready figures using Matplotlib:
  1. plots/01_convex_convergence_comparison.png
  2. plots/02_non_convex_trajectories.png
  3. plots/03_step_size_sensitivity.png
  4. plots/04_noise_and_minibatch_variance.png
  5. plots/05_second_order_gauss_newton.png
  6. plots/06_neural_net_loss_curves.png
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


def plot_01_convex_convergence():
    """Figure 1: Convergence comparison on Convex & Strongly Convex Quadratic."""
    json_path = os.path.join(RESULTS_DIR, "landscape_comparison_results.json")
    if not os.path.exists(json_path):
        print(f"Warning: {json_path} not found.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
    colors = {
        "Batch GD": "#1f77b4",
        "SGD": "#aec7e8",
        "Mini-Batch GD": "#17becf",
        "Momentum": "#ff7f0e",
        "NAG": "#2ca02c",
        "AdaGrad": "#9467bd",
        "RMSProp": "#8c564b",
        "Adam": "#d62728",
        "Newton's Method": "#000000"
    }

    for idx, land_name in enumerate(["Convex Quadratic", "Strongly Convex"]):
        ax = axes[idx]
        land_runs = [r for r in data if r.get("landscape") == land_name]
        if not land_runs:
            continue
        
        # Sub-records
        runs = land_runs[0].get("results", [])
        for r in runs:
            opt = r["optimizer"]
            hist = r.get("history_loss", [])
            if not hist:
                continue
            
            # Subsample or plot
            iters = np.linspace(0, len(hist) - 1, len(hist))
            lw = 2.5 if opt in ["Newton's Method", "Adam", "NAG"] else 1.5
            ls = "--" if opt == "Newton's Method" else "-"
            ax.plot(iters, hist, label=opt, color=colors.get(opt, "gray"), linewidth=lw, linestyle=ls)

        ax.set_title(f"Convergence: {land_name}", fontsize=13, fontweight="bold")
        ax.set_xlabel("Iteration", fontsize=11)
        ax.set_ylabel(r"Objective Value $f(x)$", fontsize=11)
        ax.set_yscale("symlog", linthresh=1e-3)
        ax.grid(True, linestyle=":", alpha=0.6)
        if idx == 0:
            ax.legend(loc="upper right", fontsize=8, ncol=2)

    plt.tight_layout()
    out_file = os.path.join(PLOTS_DIR, "01_convex_convergence_comparison.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_02_non_convex_trajectories():
    """Figure 2: Non-Convex Trajectories on Rosenbrock and Rastrigin."""
    json_path = os.path.join(RESULTS_DIR, "landscape_comparison_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
    
    # Left: Rosenbrock loss curve
    ax_rosen = axes[0]
    rosen_runs = [r for r in data if r.get("landscape") == "Rosenbrock (Valley)"]
    if rosen_runs:
        for r in rosen_runs[0].get("results", []):
            opt = r["optimizer"]
            hist = r.get("history_loss", [])
            if hist:
                ax_rosen.plot(hist, label=opt, alpha=0.85, linewidth=1.8 if opt in ["Momentum", "Newton's Method", "Adam"] else 1.0)
        ax_rosen.set_title("Rosenbrock Curved Valley: Loss Trajectory", fontsize=12, fontweight="bold")
        ax_rosen.set_xlabel("Iteration", fontsize=11)
        ax_rosen.set_ylabel(r"$f(x, y)$", fontsize=11)
        ax_rosen.set_yscale("log")
        ax_rosen.grid(True, linestyle=":", alpha=0.6)
        ax_rosen.legend(fontsize=8, ncol=2)

    # Right: Rastrigin Multimodal loss curve
    ax_rast = axes[1]
    rast_runs = [r for r in data if r.get("landscape") == "Rastrigin (Multimodal)"]
    if rast_runs:
        for r in rast_runs[0].get("results", []):
            opt = r["optimizer"]
            hist = r.get("history_loss", [])
            if hist:
                ax_rast.plot(hist, label=opt, alpha=0.85, linewidth=1.8 if opt in ["Adam", "AdaGrad", "RMSProp"] else 1.0)
        ax_rast.set_title("Rastrigin Multimodal: Escape & Trapping", fontsize=12, fontweight="bold")
        ax_rast.set_xlabel("Iteration", fontsize=11)
        ax_rast.set_ylabel(r"$f(x)$", fontsize=11)
        ax_rast.grid(True, linestyle=":", alpha=0.6)
        ax_rast.legend(fontsize=8, ncol=2)

    plt.tight_layout()
    out_file = os.path.join(PLOTS_DIR, "02_non_convex_trajectories.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_03_step_size_sensitivity():
    """Figure 3: Step-Size Sensitivity Analysis across Learning Rates."""
    json_path = os.path.join(RESULTS_DIR, "step_size_sensitivity_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
    sweeps = data.get("sweeps", {})
    lrs = data.get("learning_rates", [])

    for idx, (land_name, opt_dict) in enumerate(sweeps.items()):
        if idx >= 2:
            break
        ax = axes[idx]
        for opt_name, runs in opt_dict.items():
            losses = []
            for r in runs:
                val = r["final_loss"]
                # Clip diverged for clean plotting
                losses.append(min(val, 1e4))
            ax.plot(lrs, losses, marker="o", label=opt_name, linewidth=1.8)

        ax.set_title(f"Step-Size Sensitivity: {land_name}", fontsize=12, fontweight="bold")
        ax.set_xlabel(r"Learning Rate $\eta$", fontsize=11)
        ax.set_ylabel(r"Final Objective Value", fontsize=11)
        ax.set_xscale("log")
        ax.set_yscale("symlog", linthresh=1e-2)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(fontsize=9)

    plt.tight_layout()
    out_file = os.path.join(PLOTS_DIR, "03_step_size_sensitivity.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_04_noise_and_minibatch_variance():
    """Figure 4: Stochastic Noise & Mini-Batch Variance Scaling."""
    json_path = os.path.join(RESULTS_DIR, "stochastic_noise_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

    # Left: Noise std vs final loss variability
    ax_noise = axes[0]
    n_sweep = data.get("noise_sweep", [])
    sigmas = [item["noise_std"] for item in n_sweep]
    mean_losses = [item["mean_final_loss"] for item in n_sweep]
    std_losses = [item["std_final_loss"] for item in n_sweep]

    ax_noise.errorbar(sigmas, mean_losses, yerr=std_losses, fmt="-o", color="#d62728", ecolor="black", capsize=4, label="SGD Mean Loss +/- 1 std")
    ax_noise.set_title(r"Stochastic Noise $\sigma$ vs. Final Loss Stability", fontsize=12, fontweight="bold")
    ax_noise.set_xlabel(r"Noise Standard Deviation $\sigma$", fontsize=11)
    ax_noise.set_ylabel(r"Final Objective $f(x)$", fontsize=11)
    ax_noise.grid(True, linestyle=":", alpha=0.6)
    ax_noise.legend(fontsize=10)

    # Right: Mini-batch size vs Gradient Variance (Empirical vs Theoretical O(sigma^2 / B))
    ax_batch = axes[1]
    b_sweep = data.get("batch_sweep", [])
    batches = [item["batch_size"] for item in b_sweep]
    theo_var = [item["theoretical_var"] for item in b_sweep]
    emp_var = [item["empirical_var"] for item in b_sweep]

    ax_batch.plot(batches, theo_var, "k--", label=r"Theoretical $\sigma^2 / B$", linewidth=2.0)
    ax_batch.plot(batches, emp_var, "s-", color="#1f77b4", label="Empirical Variance", linewidth=2.0, markersize=7)
    ax_batch.set_title(r"Mini-Batch Variance Reduction: $O(\sigma^2 / B)$", fontsize=12, fontweight="bold")
    ax_batch.set_xlabel("Batch Size B", fontsize=11)
    ax_batch.set_ylabel(r"Gradient Variance $\mathrm{Var}(\bar{g})$", fontsize=11)
    ax_batch.set_xscale("log", base=2)
    ax_batch.set_yscale("log", base=10)
    ax_batch.grid(True, linestyle=":", alpha=0.6)
    ax_batch.legend(fontsize=10)

    plt.tight_layout()
    out_file = os.path.join(PLOTS_DIR, "04_noise_and_minibatch_variance.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_05_second_order_gauss_newton():
    """Figure 5: Second-Order Newton & Gauss-Newton Convergence."""
    json_path = os.path.join(RESULTS_DIR, "landscape_comparison_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

    # Left: Quadratic convergence of Newton's method on Convex Quadratic vs first-order
    ax_newton = axes[0]
    cvx_runs = [r for r in data if r.get("landscape") == "Convex Quadratic"]
    if cvx_runs:
        for r in cvx_runs[0].get("results", []):
            opt = r["optimizer"]
            if opt in ["Newton's Method", "Adam", "Batch GD", "NAG"]:
                hist = r.get("history_loss", [])
                if hist:
                    lw = 2.5 if opt == "Newton's Method" else 1.5
                    ax_newton.plot(hist, label=opt, linewidth=lw)
        ax_newton.set_title("Second-Order: Quadratic vs Linear Convergence", fontsize=12, fontweight="bold")
        ax_newton.set_xlabel("Iteration", fontsize=11)
        ax_newton.set_ylabel(r"$f(x) - f^*$", fontsize=11)
        ax_newton.set_yscale("log")
        ax_newton.grid(True, linestyle=":", alpha=0.6)
        ax_newton.legend(fontsize=10)

    # Right: Non-Linear Least Squares Gauss-Newton vs Adam baseline
    ax_gn = axes[1]
    nls_runs = [r for r in data if r.get("landscape") == "Non-Linear Least Squares"]
    if nls_runs:
        for r in nls_runs[0].get("results", []):
            opt = r["optimizer"]
            hist = r.get("history_loss", [])
            if hist:
                lw = 2.5 if "Gauss-Newton" in opt else 1.5
                ax_gn.plot(hist, label=opt, linewidth=lw)
        ax_gn.set_title("Non-Linear Least Squares: Gauss-Newton vs Adam", fontsize=12, fontweight="bold")
        ax_gn.set_xlabel("Iteration", fontsize=11)
        ax_gn.set_ylabel(r"Sum of Squared Residuals $S(\beta)$", fontsize=11)
        ax_gn.set_yscale("log")
        ax_gn.grid(True, linestyle=":", alpha=0.6)
        ax_gn.legend(fontsize=10)

    plt.tight_layout()
    out_file = os.path.join(PLOTS_DIR, "05_second_order_gauss_newton.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def plot_06_neural_net_loss_curves():
    """Figure 6: Decoupled Neural Network Backpropagation Training Curves."""
    json_path = os.path.join(RESULTS_DIR, "neural_net_results.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    runs = data.get("training_runs", [])
    grad_err = data.get("gradient_check_relative_error", 0.0)

    plt.figure(figsize=(9, 5), dpi=300)
    colors = {
        "Batch GD": "#1f77b4",
        "Momentum": "#ff7f0e",
        "RMSProp": "#2ca02c",
        "Adam": "#d62728"
    }

    for r in runs:
        name = r["optimizer"]
        hist = r.get("history_loss", [])
        acc = r.get("accuracy", 0.0)
        plt.plot(hist, label=f"{name} (Final Acc: {acc*100:.0f}%)", color=colors.get(name, "gray"), linewidth=2.0)

    plt.title(f"Decoupled 2-Layer MLP on XOR (Analytical vs Num Grad Err: {grad_err:.2e})", fontsize=12, fontweight="bold")
    plt.xlabel("Iteration / Epoch", fontsize=11)
    plt.ylabel("Mean Squared Error Loss", fontsize=11)
    plt.yscale("log")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(fontsize=10, loc="upper right")
    plt.tight_layout()

    out_file = os.path.join(PLOTS_DIR, "06_neural_net_loss_curves.png")
    plt.savefig(out_file)
    plt.close()
    print(f"  Saved: {out_file}")


def generate_all_plots():
    os.makedirs(PLOTS_DIR, exist_ok=True)
    print("Generating Track A Visualizations...")
    plot_01_convex_convergence()
    plot_02_non_convex_trajectories()
    plot_03_step_size_sensitivity()
    plot_04_noise_and_minibatch_variance()
    plot_05_second_order_gauss_newton()
    plot_06_neural_net_loss_curves()
    print("All 6 figures generated successfully in track_a_continuous_optimization/plots/")


if __name__ == "__main__":
    generate_all_plots()

