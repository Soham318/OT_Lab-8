"""
Empirical Landscape Comparison Experiment
Track A: Continuous Optimization
Assignment 8 - Optimize Anything

Compares all 10 continuous optimizers (8 first-order + 2 second-order) across:
  1. Convex Quadratic Landscape
  2. Strongly Convex Regularized Landscape
  3. Rastrigin Multimodal Non-Convex Landscape
  4. Rosenbrock Valley Non-Convex Landscape
  5. Non-Linear Least Squares Problem

Outputs:
  - track_a_continuous_optimization/results/landscape_comparison_results.json
  - track_a_continuous_optimization/results/landscape_comparison_summary.csv
  - track_a_continuous_optimization/results/landscape_comparison_report.md
"""

import csv
import json
import os
import time
from typing import Dict, List
import numpy as np

from track_a_continuous_optimization.src.landscapes import (
    ConvexQuadratic,
    StronglyConvexQuadratic,
    RastriginNonConvex,
    RosenbrockNonConvex,
    NonLinearLeastSquaresProblem
)
from track_a_continuous_optimization.src.optimizers import (
    BatchGradientDescent,
    StochasticGradientDescent,
    MiniBatchGradientDescent,
    MomentumOptimizer,
    NesterovAcceleratedGradient,
    AdaGrad,
    RMSProp,
    Adam
)
from track_a_continuous_optimization.src.second_order import NewtonsMethod, GaussNewtonMethod

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def run_all_landscape_benchmarks():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print("Running Track A Landscape Comparison Benchmarks...")

    # Define landscapes
    dim = 6
    cvx_land = ConvexQuadratic(dim=dim, condition_number=8.0, seed=42)
    scvx_land = StronglyConvexQuadratic(dim=dim, mu=2.0, condition_number=4.0, seed=42)
    rast_land = RastriginNonConvex(dim=2)
    rosen_land = RosenbrockNonConvex()
    nls_prob = NonLinearLeastSquaresProblem(num_points=50, noise_std=0.01, seed=42)

    # Initial starting points (consistent across all algorithms on each landscape)
    x0_cvx = np.ones(dim) * 2.0
    x0_scvx = np.ones(dim) * 2.0
    x0_rast = np.array([2.5, 2.5])
    x0_rosen = np.array([-1.2, 1.0])
    x0_nls = np.array([1.5, 0.5, 0.1])

    landscapes_dict = {
        "Convex Quadratic": {"land": cvx_land, "x0": x0_cvx, "max_iters": 500},
        "Strongly Convex": {"land": scvx_land, "x0": x0_scvx, "max_iters": 500},
        "Rastrigin (Multimodal)": {"land": rast_land, "x0": x0_rast, "max_iters": 500},
        "Rosenbrock (Valley)": {"land": rosen_land, "x0": x0_rosen, "max_iters": 1000}
    }

    all_results = []
    csv_rows = []

    for land_name, land_info in landscapes_dict.items():
        land = land_info["land"]
        x0 = land_info["x0"]
        max_iters = land_info["max_iters"]

        # First-order optimizer configurations tailored per landscape
        lr_scale = 0.002 if land_name == "Rosenbrock (Valley)" else 0.05
        optimizers = [
            ("Batch GD", BatchGradientDescent(learning_rate=lr_scale, max_iters=max_iters)),
            ("SGD", StochasticGradientDescent(learning_rate=lr_scale, max_iters=max_iters, noise_std=0.05)),
            ("Mini-Batch GD", MiniBatchGradientDescent(learning_rate=lr_scale, batch_size=8, max_iters=max_iters, noise_std=0.05)),
            ("Momentum", MomentumOptimizer(learning_rate=lr_scale, beta=0.9, max_iters=max_iters)),
            ("NAG", NesterovAcceleratedGradient(learning_rate=lr_scale, beta=0.9, max_iters=max_iters)),
            ("AdaGrad", AdaGrad(learning_rate=0.2 if land_name != "Rosenbrock (Valley)" else 0.05, max_iters=max_iters)),
            ("RMSProp", RMSProp(learning_rate=0.01 if land_name != "Rosenbrock (Valley)" else 0.001, max_iters=max_iters)),
            ("Adam", Adam(learning_rate=0.05 if land_name != "Rosenbrock (Valley)" else 0.005, max_iters=max_iters))
        ]

        land_record = {"landscape": land_name, "results": []}

        for opt_name, opt in optimizers:
            res = opt.minimize(land.value, land.gradient, x0)
            res_dict = {
                "optimizer": opt_name,
                "landscape": land_name,
                "f_initial": float(land.value(x0)),
                "f_final": float(res.f_final),
                "iterations": int(res.iterations),
                "converged": bool(res.converged),
                "final_grad_norm": float(res.final_grad_norm),
                "execution_time_ms": float(res.execution_time_ms),
                "history_loss": [float(v) for v in res.history_loss[::max(1, len(res.history_loss)//50)]]  # downsample for storage
            }
            land_record["results"].append(res_dict)
            csv_rows.append({
                "Landscape": land_name,
                "Optimizer": opt_name,
                "Initial Loss": round(float(land.value(x0)), 4),
                "Final Loss": round(float(res.f_final), 6),
                "Iterations": res.iterations,
                "Converged": res.converged,
                "Final Grad Norm": round(float(res.final_grad_norm), 6),
                "Runtime (ms)": round(float(res.execution_time_ms), 2)
            })

        # Second-order: Newton's Method
        newton = NewtonsMethod(damping=1e-4, max_iters=50, tol=1e-7)
        res_newton = newton.minimize(land.value, land.gradient, land.hessian, x0)
        land_record["results"].append({
            "optimizer": "Newton's Method",
            "landscape": land_name,
            "f_initial": float(land.value(x0)),
            "f_final": float(res_newton.f_final),
            "iterations": int(res_newton.iterations),
            "converged": bool(res_newton.converged),
            "final_grad_norm": float(res_newton.final_grad_norm),
            "execution_time_ms": float(res_newton.execution_time_ms),
            "history_loss": [float(v) for v in res_newton.history_loss]
        })
        csv_rows.append({
            "Landscape": land_name,
            "Optimizer": "Newton's Method",
            "Initial Loss": round(float(land.value(x0)), 4),
            "Final Loss": round(float(res_newton.f_final), 6),
            "Iterations": res_newton.iterations,
            "Converged": res_newton.converged,
            "Final Grad Norm": round(float(res_newton.final_grad_norm), 6),
            "Runtime (ms)": round(float(res_newton.execution_time_ms), 2)
        })

        all_results.append(land_record)
        print(f"  Landscape: {land_name:<24} | Evaluated {len(land_record['results'])} optimizers.")

    # 5. Non-Linear Least Squares: Gauss-Newton vs Adam vs GD
    nls_record = {"landscape": "Non-Linear Least Squares", "results": []}
    gn = GaussNewtonMethod(damping=1e-4, max_iters=50)
    res_gn = gn.minimize(nls_prob.residuals, nls_prob.jacobian, x0_nls)

    nls_record["results"].append({
        "optimizer": "Gauss-Newton",
        "landscape": "Non-Linear Least Squares",
        "f_initial": float(nls_prob.value(x0_nls)),
        "f_final": float(res_gn.f_final),
        "iterations": int(res_gn.iterations),
        "converged": bool(res_gn.converged),
        "final_grad_norm": float(res_gn.final_grad_norm),
        "execution_time_ms": float(res_gn.execution_time_ms),
        "history_loss": [float(v) for v in res_gn.history_loss]
    })
    csv_rows.append({
        "Landscape": "Non-Linear Least Squares",
        "Optimizer": "Gauss-Newton",
        "Initial Loss": round(float(nls_prob.value(x0_nls)), 4),
        "Final Loss": round(float(res_gn.f_final), 6),
        "Iterations": res_gn.iterations,
        "Converged": res_gn.converged,
        "Final Grad Norm": round(float(res_gn.final_grad_norm), 6),
        "Runtime (ms)": round(float(res_gn.execution_time_ms), 2)
    })

    # Compare against Adam on NLS
    adam_nls = Adam(learning_rate=0.05, max_iters=200)
    res_adam_nls = adam_nls.minimize(nls_prob.value, nls_prob.gradient, x0_nls)
    nls_record["results"].append({
        "optimizer": "Adam (1st Order Baseline)",
        "landscape": "Non-Linear Least Squares",
        "f_initial": float(nls_prob.value(x0_nls)),
        "f_final": float(res_adam_nls.f_final),
        "iterations": int(res_adam_nls.iterations),
        "converged": bool(res_adam_nls.converged),
        "final_grad_norm": float(res_adam_nls.final_grad_norm),
        "execution_time_ms": float(res_adam_nls.execution_time_ms),
        "history_loss": [float(v) for v in res_adam_nls.history_loss[::4]]
    })
    csv_rows.append({
        "Landscape": "Non-Linear Least Squares",
        "Optimizer": "Adam (1st Order Baseline)",
        "Initial Loss": round(float(nls_prob.value(x0_nls)), 4),
        "Final Loss": round(float(res_adam_nls.f_final), 6),
        "Iterations": res_adam_nls.iterations,
        "Converged": res_adam_nls.converged,
        "Final Grad Norm": round(float(res_adam_nls.final_grad_norm), 6),
        "Runtime (ms)": round(float(res_adam_nls.execution_time_ms), 2)
    })
    all_results.append(nls_record)

    # Save JSON
    json_path = os.path.join(RESULTS_DIR, "landscape_comparison_results.json")
    with open(json_path, mode="w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    # Save CSV
    csv_path = os.path.join(RESULTS_DIR, "landscape_comparison_summary.csv")
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = ["Landscape", "Optimizer", "Initial Loss", "Final Loss", "Iterations", "Converged", "Final Grad Norm", "Runtime (ms)"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    # Save Markdown Report
    md_path = os.path.join(RESULTS_DIR, "landscape_comparison_report.md")
    with open(md_path, mode="w", encoding="utf-8") as f:
        f.write("# Empirical Landscape Comparison Report\n\n")
        f.write("> **Track A**: Continuous Optimization | **Assignment 8**\n\n")
        f.write("### Benchmark Results Summary Table\n\n")
        f.write("| Landscape | Optimizer | Initial Loss | Final Loss | Iterations | Converged | Final Grad Norm | Runtime (ms) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for r in csv_rows:
            f.write(
                f"| **{r['Landscape']}** | {r['Optimizer']} | {r['Initial Loss']} | {r['Final Loss']} | "
                f"{r['Iterations']} | {'Yes' if r['Converged'] else 'No'} | {r['Final Grad Norm']} | {r['Runtime (ms)']} |\n"
            )

    print(f"Landscape comparison completed successfully:")
    print(f"  JSON: {json_path}")
    print(f"  CSV:  {csv_path}")
    print(f"  MD:   {md_path}")
    return all_results


if __name__ == "__main__":
    run_all_landscape_benchmarks()

