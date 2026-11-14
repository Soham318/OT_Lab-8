r"""
Step-Size Sensitivity Study
Sweeps learning rates \eta across first-order optimizers (GD, Momentum, RMSProp, Adam)
on Convex Quadratic and Non-Convex Rosenbrock landscapes.
"""

import json
import os
import sys
from typing import Dict, List, Any
import numpy as np

from track_a_continuous_optimization.src.landscapes import (
    ConvexQuadratic,
    RosenbrockNonConvex
)
from track_a_continuous_optimization.src.optimizers import (
    BatchGradientDescent,
    MomentumOptimizer,
    RMSProp,
    Adam
)


def run_sensitivity_sweep() -> Dict[str, Any]:
    print("Running Track A Step-Size Sensitivity Experiment...")
    learning_rates = [0.0001, 0.001, 0.005, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0]
    
    landscapes = [
        ("Convex Quadratic", ConvexQuadratic(dim=4, condition_number=25.0, seed=42), np.array([5.0, -4.0, 3.0, -2.0])),
        ("Rosenbrock (Valley)", RosenbrockNonConvex(), np.array([-1.2, 1.0]))
    ]
    
    optimizer_factories = [
        ("Batch GD", lambda lr: BatchGradientDescent(learning_rate=lr, max_iters=400, tol=1e-5)),
        ("Momentum", lambda lr: MomentumOptimizer(learning_rate=lr, beta=0.9, max_iters=400, tol=1e-5)),
        ("RMSProp", lambda lr: RMSProp(learning_rate=lr, beta=0.9, epsilon=1e-8, max_iters=400, tol=1e-5)),
        ("Adam", lambda lr: Adam(learning_rate=lr, beta1=0.9, beta2=0.999, epsilon=1e-8, max_iters=400, tol=1e-5))
    ]
    
    results: Dict[str, Any] = {
        "learning_rates": learning_rates,
        "sweeps": {}
    }
    
    for l_name, landscape, x0 in landscapes:
        results["sweeps"][l_name] = {}
        for opt_name, factory in optimizer_factories:
            results["sweeps"][l_name][opt_name] = []
            for lr in learning_rates:
                try:
                    opt = factory(lr)
                    res = opt.minimize(landscape.value, landscape.gradient, x0)
                    final_loss = float(res.f_final)
                    is_nan_or_inf = np.isnan(final_loss) or np.isinf(final_loss) or abs(final_loss) > 1e8
                    
                    record = {
                        "lr": lr,
                        "final_loss": 1e8 if is_nan_or_inf else final_loss,
                        "iterations": int(res.iterations),
                        "converged": bool(res.converged) and not is_nan_or_inf,
                        "diverged": bool(is_nan_or_inf),
                        "final_grad_norm": 1e8 if is_nan_or_inf else float(res.final_grad_norm)
                    }
                except Exception as e:
                    record = {
                        "lr": lr,
                        "final_loss": 1e8,
                        "iterations": 400,
                        "converged": False,
                        "diverged": True,
                        "final_grad_norm": 1e8,
                        "error": str(e)
                    }
                results["sweeps"][l_name][opt_name].append(record)
        print(f"  Completed sensitivity sweep for: {l_name}")

    # Output paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    json_path = os.path.join(results_dir, "step_size_sensitivity_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    csv_path = os.path.join(results_dir, "step_size_sensitivity_summary.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("Landscape,Optimizer,LearningRate,FinalLoss,Iterations,Converged,Diverged\n")
        for l_name, opt_dict in results["sweeps"].items():
            for opt_name, runs in opt_dict.items():
                for run in runs:
                    f.write(f'"{l_name}","{opt_name}",{run["lr"]},{run["final_loss"]:.6e},{run["iterations"]},{run["converged"]},{run["diverged"]}\n')

    print(f"Sensitivity study completed:\n  JSON: {json_path}\n  CSV:  {csv_path}")
    return results


if __name__ == "__main__":
    run_sensitivity_sweep()
