r"""
Quantum Gradient Comparison: Parameter-Shift vs Finite-Difference vs SPSA
Track C: Quantum Optimization
Assignment 8 - Optimize Anything

Evaluates:
  1. Exactness of Parameter-Shift Rule vs Centered Finite Differences:
     ||grad_PS - grad_FD|| / ||grad_PS||
  2. Evaluation budget scaling: 2d (Parameter-Shift) vs 2 (SPSA) calls per iteration.
  3. Noisy optimization trajectory comparing SPSA with standard Gradient Descent.
"""

import json
import os
import sys
import time
from typing import Dict, List, Any
import numpy as np

from qiskit.quantum_info import Statevector, SparsePauliOp
from track_c_quantum_optimization.src.circuits import HardwareEfficientAnsatz
from track_c_quantum_optimization.src.gradients import ParameterShiftGradient, SPSAOptimizer

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def run_gradient_comparison() -> Dict[str, Any]:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print("Running Track C Quantum Gradient Study...")

    ansatz = HardwareEfficientAnsatz(num_qubits=3, num_layers=1, rotation_blocks=("ry", "rz"))
    num_params = ansatz.num_params  # 3 * 2 * 2 = 12 params

    # Observable H = Z_0 Z_1 + Z_1 Z_2 + X_0
    H = SparsePauliOp.from_list([
        ("ZZI", 1.0),
        ("IZZ", 1.0),
        ("XII", 0.5)
    ]).simplify()

    def energy_fn(theta: np.ndarray) -> float:
        sv = ansatz.get_statevector(theta)
        return float(sv.expectation_value(H).real)

    # 1. Parameter-shift vs Finite-difference comparison across 10 random states
    rng = np.random.RandomState(42)
    gradient_comparisons = []
    rel_errors = []

    for point_idx in range(10):
        theta = rng.uniform(-np.pi, np.pi, size=num_params)
        grad_ps = ParameterShiftGradient.compute_gradient(energy_fn, theta)
        grad_fd = ParameterShiftGradient.compute_finite_difference(energy_fn, theta, eps=1e-5)

        norm_ps = float(np.linalg.norm(grad_ps))
        norm_diff = float(np.linalg.norm(grad_ps - grad_fd))
        rel_err = norm_diff / (norm_ps + 1e-10)
        rel_errors.append(rel_err)

        gradient_comparisons.append({
            "point_id": point_idx,
            "norm_parameter_shift": round(norm_ps, 6),
            "norm_finite_diff": round(float(np.linalg.norm(grad_fd)), 6),
            "l2_difference": round(norm_diff, 8),
            "relative_error": round(rel_err, 8)
        })

    mean_rel_err = float(np.mean(rel_errors))
    print(f"  Parameter-Shift vs Finite-Difference Mean Relative Error: {mean_rel_err:.2e}")

    # 2. SPSA vs Gradient Descent on Noisy Landscape (simulating shot noise sigma=0.05)
    noise_std = 0.05
    noise_rng = np.random.RandomState(99)

    def noisy_energy_fn(theta: np.ndarray) -> float:
        clean = energy_fn(theta)
        return clean + float(noise_rng.normal(0.0, noise_std))

    theta_init = rng.uniform(-np.pi, np.pi, size=num_params)
    init_val = energy_fn(theta_init)

    # A. SPSA (2 function evaluations per iteration)
    spsa = SPSAOptimizer(a=0.25, c=0.1, max_iters=100, seed=42)
    t0_spsa = time.perf_counter()
    opt_spsa, final_spsa, hist_spsa = spsa.optimize(noisy_energy_fn, theta_init)
    t_spsa_ms = (time.perf_counter() - t0_spsa) * 1000.0

    # B. Standard GD via Parameter Shift (2 * num_params = 24 evaluations per iteration)
    theta_gd = np.array(theta_init, copy=True)
    hist_gd = [noisy_energy_fn(theta_gd)]
    lr = 0.05
    t0_gd = time.perf_counter()
    for _ in range(100):
        g = ParameterShiftGradient.compute_gradient(noisy_energy_fn, theta_gd)
        theta_gd = theta_gd - lr * g
        hist_gd.append(noisy_energy_fn(theta_gd))
    t_gd_ms = (time.perf_counter() - t0_gd) * 1000.0

    results = {
        "num_qubits": 3,
        "num_parameters": num_params,
        "mean_gradient_rel_error": mean_rel_err,
        "point_evaluations": gradient_comparisons,
        "noisy_optimization": {
            "initial_energy": round(init_val, 6),
            "spsa_final_energy": round(energy_fn(opt_spsa), 6),
            "spsa_runtime_ms": round(t_spsa_ms, 2),
            "spsa_circuit_evals": 2 * 100,
            "gd_final_energy": round(energy_fn(theta_gd), 6),
            "gd_runtime_ms": round(t_gd_ms, 2),
            "gd_circuit_evals": 2 * num_params * 100,
            "spsa_history": [round(float(v), 4) for v in hist_spsa[::4]],
            "gd_history": [round(float(v), 4) for v in hist_gd[::4]]
        }
    }

    # Save output
    json_path = os.path.join(RESULTS_DIR, "gradient_study_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    csv_path = os.path.join(RESULTS_DIR, "gradient_study_summary.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("PointID,NormParameterShift,NormFiniteDiff,L2Diff,RelError\n")
        for p in gradient_comparisons:
            f.write(f'{p["point_id"]},{p["norm_parameter_shift"]},{p["norm_finite_diff"]},{p["l2_difference"]},{p["relative_error"]}\n')

    print(f"Gradient study completed:\n  JSON: {json_path}\n  CSV:  {csv_path}")
    return results


if __name__ == "__main__":
    run_gradient_comparison()

