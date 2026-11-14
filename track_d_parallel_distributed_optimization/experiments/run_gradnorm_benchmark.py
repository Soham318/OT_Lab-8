r"""Experiment 6: GradNorm Multi-Task Loss Balancing Benchmark.

Evaluates:
- GradNorm dynamic task weight adaptation vs fixed equal weights
- Gradient norm matching: G_W^{(i)} \approx \bar{G}_W [r_i]^\alpha
- Balancing training rates between a simpler task and a more difficult non-linear task
"""

import csv
import json
import os
import sys
from typing import Any, Dict, List
import numpy as np

# Ensure project root is on sys.path for direct script execution
sys.path.insert(0, os.path.abspath("."))

from track_d_parallel_distributed_optimization.src.gradnorm import GradNormSimulator


def run_gradnorm_benchmarks() -> Dict[str, Any]:
    print("=" * 70)
    print("RUNNING EXPERIMENT 6: GradNorm Multi-Task Balancing")
    print("=" * 70)

    in_dim = 10
    hidden_dim = 16
    alpha = 1.5
    lr_model = 0.02
    lr_grad = 0.02
    epochs = 150
    seed = 42

    sim = GradNormSimulator(
        in_dim=in_dim,
        hidden_dim=hidden_dim,
        alpha=alpha,
        lr_model=lr_model,
        lr_grad=lr_grad,
        seed=seed,
    )

    print("Generating synthetic multi-task regression dataset (N=600)...")
    X, y1, y2 = sim.generate_synthetic_data(n_samples=600)
    print("  Task 1: Linear combination (moderate noise)")
    print("  Task 2: Non-linear quadratic combination (higher variance/difficulty)")

    # 1. Run with Fixed Equal Weights (w1 = 1.0, w2 = 1.0)
    print("\n--- 1. Training with Fixed Equal Weights (w1=1.0, w2=1.0) ---")
    fixed_res = sim.run_training(X, y1, y2, num_epochs=epochs, use_gradnorm=False)
    print(f"  Fixed: Final Task 1 Loss: {fixed_res['final_L1']:.4f} | Task 2 Loss: {fixed_res['final_L2']:.4f} | Total: {fixed_res['final_total_loss']:.4f}")

    # 2. Run with GradNorm
    print("\n--- 2. Training with GradNorm Dynamic Adaptation ---")
    gradnorm_res = sim.run_training(X, y1, y2, num_epochs=epochs, use_gradnorm=True)
    w_final = gradnorm_res["final_weights"]
    print(f"  GradNorm: Final Task 1 Loss: {gradnorm_res['final_L1']:.4f} | Task 2 Loss: {gradnorm_res['final_L2']:.4f} | Total: {gradnorm_res['final_total_loss']:.4f}")
    print(f"  Final Weights: Task 1 w1 = {w_final[0]:.4f} | Task 2 w2 = {w_final[1]:.4f} (Sum: {sum(w_final):.4f})")

    combined = {
        "metadata": {
            "in_dim": in_dim,
            "hidden_dim": hidden_dim,
            "alpha": alpha,
            "lr_model": lr_model,
            "lr_grad": lr_grad,
            "epochs": epochs,
        },
        "fixed_weights": fixed_res,
        "gradnorm": gradnorm_res,
    }

    os.makedirs("track_d_parallel_distributed_optimization/results", exist_ok=True)
    json_path = "track_d_parallel_distributed_optimization/results/gradnorm_benchmark_results.json"
    csv_path = "track_d_parallel_distributed_optimization/results/gradnorm_benchmark_summary.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Epoch", "Fixed_L1", "Fixed_L2", "Fixed_Total",
            "GradNorm_L1", "GradNorm_L2", "GradNorm_Total",
            "GradNorm_w1", "GradNorm_w2",
        ])
        for ep in range(epochs):
            writer.writerow([
                ep + 1,
                round(fixed_res["history_L1"][ep], 4),
                round(fixed_res["history_L2"][ep], 4),
                round(fixed_res["history_L1"][ep] + fixed_res["history_L2"][ep], 4),
                round(gradnorm_res["history_L1"][ep], 4),
                round(gradnorm_res["history_L2"][ep], 4),
                round(gradnorm_res["history_L1"][ep] + gradnorm_res["history_L2"][ep], 4),
                round(gradnorm_res["history_w1"][ep], 4),
                round(gradnorm_res["history_w2"][ep], 4),
            ])

    print(f"\n[DONE] Saved GradNorm benchmark results to {json_path} and {csv_path}")
    return combined


if __name__ == "__main__":
    run_gradnorm_benchmarks()
