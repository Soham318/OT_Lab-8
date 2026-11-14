#!/usr/bin/env python3
"""
Visualization script for Track G: xv6 Kernel CPU Accounting.
Generates publication-ready figures in track_g_xv6_kernel/plots/.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Styling
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.titlesize": 14,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.autolayout": True,
    "axes.grid": True,
    "grid.alpha": 0.3
})

def plot_workload_comparisons():
    """Plot 1: CPU Ticks vs Wall-Clock Ticks across Workloads."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    workloads = [
        "CPU-Intensive\n(Run 1)",
        "CPU-Intensive\n(Run 2)",
        "CPU-Intensive\n(Run 3)",
        "Short Burst\n(Sub-tick)",
        "Concurrent SMP\n(4 Workers)"
    ]
    
    cpu_ticks = [7, 6, 6, 0, 15]
    wall_ticks = [7, 6, 6, 0, 8]
    
    x = np.arange(len(workloads))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, cpu_ticks, width, label="Process CPU Time (ticks)", color="#2563EB", edgecolor="black", alpha=0.9)
    rects2 = ax.bar(x + width/2, wall_ticks, width, label="Elapsed Wall-Clock (ticks)", color="#F59E0B", edgecolor="black", alpha=0.9)
    
    ax.set_ylabel("Timer Ticks (~100 ms per tick)")
    ax.set_title("xv6 Process CPU Accounting vs. Wall-Clock Duration Across Workloads")
    ax.set_xticks(x)
    ax.set_xticklabels(workloads)
    ax.legend(frameon=True, loc="upper left")
    
    # Add value annotations
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h}", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontweight="bold")
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h}", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontweight="bold")

    ax.annotate("187% SMP Utilization\n(Sum of 4 Cores > Wall Time)",
                xy=(4, 15), xytext=(3.2, 12),
                arrowprops=dict(facecolor="black", shrink=0.08, width=1, headwidth=6),
                bbox=dict(boxstyle="round,pad=0.4", fc="#FEF3C7", ec="#D97706", lw=1.2),
                fontsize=9)
    
    out_path = os.path.join(OUTPUT_DIR, "01_workload_cputime_vs_walltime.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")

def plot_concurrent_smp_scaling():
    """Plot 2: Concurrent Worker CPU Distribution on 3 SMP Cores."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    
    workers = ["Worker 0\n(15k iters)", "Worker 1\n(30k iters)", "Worker 2\n(45k iters)", "Worker 3\n(60k iters)"]
    ticks = [2, 3, 4, 6]
    colors = ["#3B82F6", "#10B981", "#8B5CF6", "#EC4899"]
    
    bars = ax1.bar(workers, ticks, color=colors, edgecolor="black", width=0.55)
    ax1.set_ylabel("CPU Ticks Recorded")
    ax1.set_title("Individual Worker CPU Runtime")
    for bar in bars:
        h = bar.get_height()
        ax1.annotate(f"{h} ticks", xy=(bar.get_x() + bar.get_width()/2, h),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontweight="bold")
    
    # Comparison of Aggregate CPU vs Wall Clock
    categories = ["Aggregate Worker CPU", "Elapsed Wall Time"]
    values = [sum(ticks), 8]
    bar_colors = ["#059669", "#D97706"]
    
    bars2 = ax2.bar(categories, values, color=bar_colors, edgecolor="black", width=0.45)
    ax2.set_ylabel("Timer Ticks")
    ax2.set_title("SMP Multicore Utilization (3 Cores)")
    for bar in bars2:
        h = bar.get_height()
        ax2.annotate(f"{h} ticks", xy=(bar.get_x() + bar.get_width()/2, h),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontweight="bold")
        
    ax2.annotate(f"Speedup Ratio = {sum(ticks)/8:.2f}x\n(187% CPU Utilization)",
                 xy=(0.5, 11), ha="center",
                 bbox=dict(boxstyle="round,pad=0.4", fc="#E0F2FE", ec="#0284C7", lw=1.2),
                 fontsize=10, fontweight="bold")
    
    out_path = os.path.join(OUTPUT_DIR, "02_concurrent_smp_accounting.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")

def plot_timer_granularity():
    """Plot 3: Timer Granularity & Quantization Error at 10 Hz (100 ms)."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    true_durations_ms = np.linspace(1, 500, 500)
    tick_period_ms = 100.0
    
    # In periodic sampling without phase lock:
    # Expected discrete ticks = floor(t / T) or ceil(t / T) depending on offset
    discrete_ticks = np.round(true_durations_ms / tick_period_ms)
    reconstructed_ms = discrete_ticks * tick_period_ms
    quantization_error_pct = np.abs(reconstructed_ms - true_durations_ms) / true_durations_ms * 100.0
    
    ax.plot(true_durations_ms, quantization_error_pct, color="#DC2626", lw=1.8, label="Quantization Error (%)")
    ax.axhline(0, color="gray", lw=0.8, linestyle="--")
    ax.axvline(100, color="#4B5563", lw=1.2, linestyle=":", label="100 ms Tick Boundary")
    ax.axvline(200, color="#4B5563", lw=1.2, linestyle=":")
    ax.axvline(300, color="#4B5563", lw=1.2, linestyle=":")
    
    ax.set_xlabel("True Execution Duration (milliseconds)")
    ax.set_ylabel("Measurement Quantization Error (%)")
    ax.set_title("xv6 Periodic Timer Quantization Error (10 Hz Tick Frequency)")
    ax.set_ylim(-5, 105)
    ax.legend(frameon=True, loc="upper right")
    
    ax.annotate("Sub-tick tasks (<100ms):\n100% Relative Error\n(0 or 1 tick recorded)",
                xy=(30, 95), xytext=(120, 80),
                arrowprops=dict(facecolor="black", shrink=0.08, width=1, headwidth=6),
                bbox=dict(boxstyle="round,pad=0.4", fc="#FEE2E2", ec="#B91C1C", lw=1.2),
                fontsize=9)
    
    out_path = os.path.join(OUTPUT_DIR, "03_timer_tick_quantization_error.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")

def plot_process_isolation_and_sleeping():
    """Plot 4: Active Execution vs. Sleeping State Accounting."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    states = ["Active Compute\n(10,000 iters)", "Sleeping State\n(pause(10) syscall)"]
    cputime_delta = [2, 0]
    uptime_delta = [2, 10]
    
    x = np.arange(len(states))
    width = 0.35
    
    r1 = ax.bar(x - width/2, cputime_delta, width, label="CPU Runtime Ticks", color="#10B981", edgecolor="black")
    r2 = ax.bar(x + width/2, uptime_delta, width, label="Elapsed Wall Ticks", color="#6B7280", edgecolor="black")
    
    ax.set_ylabel("Timer Ticks")
    ax.set_title("Active Compute vs. Sleeping State CPU Accounting")
    ax.set_xticks(x)
    ax.set_xticklabels(states)
    ax.legend(frameon=True, loc="upper left")
    
    for r in r1:
        h = r.get_height()
        ax.annotate(f"{h}", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontweight="bold")
    for r in r2:
        h = r.get_height()
        ax.annotate(f"{h}", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontweight="bold")
        
    ax.annotate("Verified Process Isolation:\nZero CPU ticks charged during sleep\n(CPU duty = 0%)",
                xy=(1, 0), xytext=(0.6, 5),
                arrowprops=dict(facecolor="black", shrink=0.08, width=1, headwidth=6),
                bbox=dict(boxstyle="round,pad=0.4", fc="#DCFCE7", ec="#15803D", lw=1.2),
                fontsize=9)
    
    out_path = os.path.join(OUTPUT_DIR, "04_active_vs_sleeping_accounting.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    plot_workload_comparisons()
    plot_concurrent_smp_scaling()
    plot_timer_granularity()
    plot_process_isolation_and_sleeping()
    print("All plots generated successfully.")

