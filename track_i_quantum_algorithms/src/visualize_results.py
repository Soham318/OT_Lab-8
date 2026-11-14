"""
Visualization Module for Track I: Quantum Algorithms and QML
Generates 5 publication-quality figures:
1. 01_grover_probability_amplification.png (Grover probability vs iterations)
2. 02_qpe_phase_distribution.png (QPE measurement counts & phase estimation)
3. 03_shor_period_measurement.png (Shor modular exponentiation period peaks)
4. 04_qubo_energy_spectrum.png (QUBO / Ising energy landscape & ground state)
5. 05_qml_vs_classical_comparison.png (QML vs Classical metrics & training time)
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["MPLCONFIGDIR"] = os.path.join(BASE_DIR, "results", ".matplotlib_cache")
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = os.path.join(BASE_DIR, "results")
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# Aesthetic palette
PALETTE = {
    "primary": "#1E88E5",    # Vivid Blue
    "secondary": "#D81B60",  # Magenta / Berry
    "accent": "#004D40",     # Deep Teal
    "highlight": "#FFC107",  # Amber
    "ground": "#2E7D32",     # Forest Green
    "dark": "#263238"        # Slate Dark
}

def plot_grover_amplification():
    """Plot 1: Grover Search Target Probability vs Iterations (N=4 and N=8)."""
    from track_i_quantum_algorithms.src.grover_search import track_grover_amplitude_trajectory

    traj_2q = track_grover_amplitude_trajectory(num_qubits=2, target="10", max_iterations=4)
    traj_3q = track_grover_amplitude_trajectory(num_qubits=3, target="101", max_iterations=5)

    iters_2q = [item["iteration"] for item in traj_2q]
    probs_2q = [item["target_probability"] for item in traj_2q]

    iters_3q = [item["iteration"] for item in traj_3q]
    probs_3q = [item["target_probability"] for item in traj_3q]

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

    ax.plot(iters_2q, probs_2q, marker="o", linewidth=2.4, color=PALETTE["secondary"],
            label="N = 4 (n = 2 qubits, Target '10')", markersize=8)
    ax.plot(iters_3q, probs_3q, marker="s", linewidth=2.4, color=PALETTE["primary"],
            label="N = 8 (n = 3 qubits, Target '101')", markersize=8)

    # Highlight optimal points
    ax.annotate("Optimal: 100% at R=1\n(N=4)", xy=(1, probs_2q[1]), xytext=(1.2, 0.85),
                arrowprops=dict(facecolor=PALETTE["secondary"], shrink=0.08, width=1.5, headwidth=6),
                fontsize=9.5, fontweight="bold", color=PALETTE["secondary"],
                bbox=dict(boxstyle="round,pad=0.3", fc="#FCE4EC", ec=PALETTE["secondary"], lw=1))

    ax.annotate("Optimal: 94.5% at R=2\n(N=8)", xy=(2, probs_3q[2]), xytext=(2.3, 0.82),
                arrowprops=dict(facecolor=PALETTE["primary"], shrink=0.08, width=1.5, headwidth=6),
                fontsize=9.5, fontweight="bold", color=PALETTE["primary"],
                bbox=dict(boxstyle="round,pad=0.3", fc="#E3F2FD", ec=PALETTE["primary"], lw=1))

    ax.set_xlabel("Grover Iteration Count $R$", fontsize=11, fontweight="bold")
    ax.set_ylabel(r"Target State Probability $|\langle \omega | \psi_R \rangle|^2$", fontsize=11, fontweight="bold")
    ax.set_title("Track I: Grover Amplitude Amplification and Over-Rotation Trajectory", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylim(-0.05, 1.1)
    ax.set_xticks(range(0, 6))
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(fontsize=11, loc="lower right", framealpha=0.95)

    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "01_grover_probability_amplification.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[INFO] Plot 1 saved to: {out_path}")

def plot_qpe_distribution(results_data):
    """Plot 2: QPE Measurement Counts and Phase Peak for Theta = 0.375."""
    qpe_res = results_data["quantum_phase_estimation"]["theta_0.375"]
    counts = qpe_res["dominant_bitstring_counts"]

    # Sort bitstrings
    sorted_bits = sorted(counts.keys())
    counts_vals = [counts[b] for b in sorted_bits]

    # Convert to phase labels
    labels = []
    for b in sorted_bits:
        val = int(b[::-1], 2) / 8.0
        labels.append(f"{b}\n(φ={val:.3f})")

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    bars = ax.bar(labels, counts_vals, color=PALETTE["primary"], edgecolor="black", linewidth=0.8, width=0.5)

    # Highlight peak
    for i, b in enumerate(sorted_bits):
        val = int(b[::-1], 2) / 8.0
        if abs(val - 0.375) < 1e-4:
            bars[i].set_color(PALETTE["ground"])
            ax.text(bars[i].get_x() + bars[i].get_width()/2.0, counts_vals[i] + 15,
                    f"Peak: 100%\n(φ = 3/8 = 0.375)", ha="center", va="bottom",
                    fontsize=10, fontweight="bold", color=PALETTE["ground"])

    ax.set_xlabel("Measured Bitstring (and Inferred Phase $\\phi$)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Measurement Counts (out of 1024 shots)", fontsize=11, fontweight="bold")
    ax.set_title("Track I: Quantum Phase Estimation Measurement Distribution (Target $\\theta = 0.375$)", fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "02_qpe_phase_distribution.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[INFO] Plot 2 saved to: {out_path}")

def plot_shor_period_measurement(results_data):
    """Plot 3: Shor's Algorithm Measurement Distribution for N=15, a=7."""
    shor_res = results_data["shor_factoring"]
    counts = shor_res["measurement_counts"]

    sorted_bits = sorted(counts.keys(), key=lambda b: int(b[::-1], 2))
    counts_vals = [counts[b] for b in sorted_bits]
    phases = [f"{b}\n(φ={int(b[::-1], 2)/8:.2f})" for b in sorted_bits]

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    bars = ax.bar(phases, counts_vals, color=PALETTE["secondary"], edgecolor="black", linewidth=0.8, width=0.5)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, h + 8, f"{h}\n({h/1024*100:.1f}%)",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xlabel("Counting Register State (Measured Phase $\\phi = s/r$)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Measurement Counts (1024 Shots)", fontsize=11, fontweight="bold")
    ax.set_title("Track I: Shor's Period-Finding Measurement Spectrum ($N=15, a=7, r=4$)", fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.set_ylim(0, 340)

    # Note extracted factors
    ax.text(0.5, 0.88, "Phases {0.25, 0.75} -> Period r = 4\nExtracted Non-Trivial Factors: [3, 5]",
            transform=ax.transAxes, ha="center", fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", fc="#E8F5E9", ec=PALETTE["ground"], lw=1.2))

    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "03_shor_period_measurement.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[INFO] Plot 3 saved to: {out_path}")

def plot_qubo_energy_spectrum(results_data):
    """Plot 4: QUBO & Ising Energy Landscape Across All 16 States."""
    qubo_res = results_data["qubo_annealing"]
    spectrum = qubo_res["exhaustive"]["energy_spectrum"]

    states = [item["bitstring"] for item in spectrum]
    energies = [item["energy"] for item in spectrum]

    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    colors = [PALETTE["ground"] if i == 0 else PALETTE["primary"] for i in range(len(states))]
    bars = ax.bar(states, energies, color=colors, edgecolor="black", linewidth=0.8, width=0.6)

    # Highlight ground state
    ax.annotate(f"Global Ground State: '1001'\nMinimum Energy: {energies[0]:.1f}",
                xy=(0, energies[0]), xytext=(1.2, energies[0] - 2.5),
                arrowprops=dict(facecolor=PALETTE["ground"], shrink=0.08, width=1.5, headwidth=6),
                fontsize=10, fontweight="bold", color=PALETTE["ground"],
                bbox=dict(boxstyle="round,pad=0.3", fc="#E8F5E9", ec=PALETTE["ground"], lw=1))

    ax.set_xlabel("Binary Spin Configuration $(x_0, x_1, x_2, x_3)$", fontsize=11, fontweight="bold")
    ax.set_ylabel("QUBO / Ising Energy $E(x)$", fontsize=11, fontweight="bold")
    ax.set_title("Track I: Combinatorial Energy Spectrum & Global Ground State", fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.xticks(rotation=45, ha="right", fontsize=9.5, fontweight="bold")

    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "04_qubo_energy_spectrum.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[INFO] Plot 4 saved to: {out_path}")

def plot_qml_comparison(qml_data):
    """Plot 5: Side-by-Side Comparison of Classical vs Quantum Machine Learning."""
    c = qml_data["classical"]
    q = qml_data["quantum"]

    metrics = ["Test Accuracy", "Test Precision", "Test Recall", "Test F1-Score"]
    c_vals = [c["test_accuracy"] * 100, c["test_precision"] * 100, c["test_recall"] * 100, c["test_f1"] * 100]
    q_vals = [q["test_accuracy"] * 100, q["test_precision"] * 100, q["test_recall"] * 100, q["test_f1"] * 100]

    x = np.arange(len(metrics))
    width = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300, gridspec_kw={'width_ratios': [1.3, 1]})

    # Subplot 1: Classification Performance
    rects1 = ax1.bar(x - width/2, c_vals, width, label="Classical Logistic Regression", color=PALETTE["primary"], edgecolor="black", linewidth=0.7)
    rects2 = ax1.bar(x + width/2, q_vals, width, label="Quantum Variational Classifier (VQC)", color=PALETTE["secondary"], edgecolor="black", linewidth=0.7)

    ax1.set_ylabel("Score (%)", fontsize=11, fontweight="bold")
    ax1.set_title("Classification Performance (Iris 2-Class)", fontsize=12, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics, fontsize=10, fontweight="bold")
    ax1.set_ylim(0, 115)
    ax1.grid(axis="y", linestyle="--", alpha=0.5)
    ax1.legend(fontsize=10, loc="lower right")

    for bar in rects1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 1.5, f"{yval:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    for bar in rects2:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 1.5, f"{yval:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    # Subplot 2: Wall-Clock Training Time (Log Scale)
    models = ["Classical\n(Logistic Regression)", "Quantum VQC\n(CPU Simulator)"]
    times_ms = [c["training_time_ms"], q["training_time_ms"]]
    bars3 = ax2.bar(models, times_ms, color=[PALETTE["primary"], PALETTE["secondary"]], edgecolor="black", linewidth=0.8, width=0.5)
    ax2.set_ylabel("Training Time (milliseconds, log scale)", fontsize=11, fontweight="bold")
    ax2.set_yscale("log")
    ax2.set_title("Computational Training Latency", fontsize=12, fontweight="bold")
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars3:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval * 1.25, f"{yval:.1f} ms",
                 ha="center", va="bottom", fontsize=10, fontweight="bold")

    # Annotate slowdown factor
    slowdown = q["training_time_ms"] / max(0.1, c["training_time_ms"])
    ax2.text(0.5, 0.45, f"Simulation Overhead:\n{slowdown:.1f}x Slower on CPU",
             transform=ax2.transAxes, ha="center", fontsize=10.5, fontweight="bold", color=PALETTE["secondary"],
             bbox=dict(boxstyle="round,pad=0.3", fc="#FCE4EC", ec=PALETTE["secondary"], lw=1))

    plt.suptitle("Track I: Empirical Comparison of Classical Machine Learning vs. Quantum VQC", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "05_qml_vs_classical_comparison.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[INFO] Plot 5 saved to: {out_path}")

def generate_all_track_i_plots():
    algo_file = os.path.join(RESULTS_DIR, "algorithm_summary.json")
    qml_file = os.path.join(RESULTS_DIR, "qml_benchmark_results.json")

    with open(algo_file, "r", encoding="utf-8") as f:
        algo_data = json.load(f)

    with open(qml_file, "r", encoding="utf-8") as f:
        qml_data = json.load(f)

    plot_grover_amplification()
    plot_qpe_distribution(algo_data)
    plot_shor_period_measurement(algo_data)
    plot_qubo_energy_spectrum(algo_data)
    plot_qml_comparison(qml_data)
    print("\n[SUCCESS] All 5 publication-quality Track I plots generated in plots/.")

if __name__ == "__main__":
    generate_all_track_i_plots()
