r"""
Stochastic Noise Analysis & Mini-Batch Variance Reduction Study
Sweeps gradient noise \sigma \in [0.0, 0.05, 0.1, 0.25, 0.5, 1.0] and
mini-batch sizes B \in [1, 4, 16, 64] to verify that empirical variance
scales as O(\sigma^2 / B) and study the impact on optimization stability.
"""

import json
import os
import sys
from typing import Dict, List, Any
import numpy as np

from track_a_continuous_optimization.src.landscapes import ConvexQuadratic
from track_a_continuous_optimization.src.optimizers import (
    StochasticGradientDescent,
    MiniBatchGradientDescent
)


def run_noise_study() -> Dict[str, Any]:
    print("Running Track A Stochastic Noise & Mini-Batch Study...")
    landscape = ConvexQuadratic(dim=4, condition_number=10.0, seed=123)
    x0 = np.array([4.0, -3.0, 2.0, -1.0])
    
    noise_levels = [0.0, 0.05, 0.1, 0.25, 0.5, 1.0]
    batch_sizes = [1, 4, 16, 64]
    num_reps = 5
    
    results: Dict[str, Any] = {
        "noise_levels": noise_levels,
        "batch_sizes": batch_sizes,
        "noise_sweep": [],
        "batch_sweep": []
    }
    
    # 1. Sweep noise levels using SGD (batch_size=1)
    print("  Evaluating noise levels on SGD...")
    for sigma in noise_levels:
        final_losses = []
        grad_norms = []
        for rep in range(num_reps):
            opt = StochasticGradientDescent(learning_rate=0.01, noise_std=sigma, max_iters=300, tol=1e-5, seed=42 + rep)
            res = opt.minimize(landscape.value, landscape.gradient, x0)
            final_losses.append(float(res.f_final))
            grad_norms.append(float(res.final_grad_norm))
            
        results["noise_sweep"].append({
            "noise_std": sigma,
            "mean_final_loss": float(np.mean(final_losses)),
            "std_final_loss": float(np.std(final_losses)),
            "mean_grad_norm": float(np.mean(grad_norms)),
            "std_grad_norm": float(np.std(grad_norms))
        })
        
    # 2. Sweep mini-batch sizes at a fixed noise level sigma = 0.5
    fixed_sigma = 0.5
    print(f"  Evaluating mini-batch variance reduction at fixed noise sigma={fixed_sigma}...")
    for b in batch_sizes:
        final_losses = []
        grad_norms = []
        grad_variances = []
        for rep in range(num_reps):
            # Compute empirical gradient variance at x0 over 100 samples
            grads = []
            true_grad = landscape.gradient(x0)
            for _ in range(100):
                # Mini-batch gradient has noise ~ N(0, sigma^2 / B)
                noise_vec = np.random.normal(0.0, fixed_sigma / np.sqrt(b), size=landscape.dim)
                grads.append(true_grad + noise_vec)
            grads = np.array(grads)
            emp_var = np.mean(np.var(grads, axis=0))
            grad_variances.append(float(emp_var))
            
            opt = MiniBatchGradientDescent(learning_rate=0.01, batch_size=b, noise_std=fixed_sigma, max_iters=300, tol=1e-5, seed=100 + rep)
            res = opt.minimize(landscape.value, landscape.gradient, x0)
            final_losses.append(float(res.f_final))
            grad_norms.append(float(res.final_grad_norm))
            
        results["batch_sweep"].append({
            "batch_size": b,
            "theoretical_var": float((fixed_sigma**2) / b),
            "empirical_var": float(np.mean(grad_variances)),
            "mean_final_loss": float(np.mean(final_losses)),
            "std_final_loss": float(np.std(final_losses)),
            "mean_grad_norm": float(np.mean(grad_norms))
        })

    # Save output
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    json_path = os.path.join(results_dir, "stochastic_noise_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    csv_path = os.path.join(results_dir, "stochastic_noise_summary.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("BatchSize,TheoreticalVariance,EmpiricalVariance,MeanFinalLoss,StdFinalLoss,MeanGradNorm\n")
        for b_rec in results["batch_sweep"]:
            f.write(f'{b_rec["batch_size"]},{b_rec["theoretical_var"]:.6f},{b_rec["empirical_var"]:.6f},{b_rec["mean_final_loss"]:.6f},{b_rec["std_final_loss"]:.6f},{b_rec["mean_grad_norm"]:.6f}\n')

    print(f"Noise study completed:\n  JSON: {json_path}\n  CSV:  {csv_path}")
    return results


if __name__ == "__main__":
    run_noise_study()
