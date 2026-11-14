r"""
Shot Noise and Barren Plateau Empirical Experiments
Track C: Quantum Optimization
Assignment 8 - Optimize Anything

Part A: Shot Noise Scaling (50 to 10,000 shots):
  Demonstrates empirical variance scaling Var ~ 1 / S.

Part B: Barren Plateau Scaling (2 to 7 qubits):
  Demonstrates exponential decay of gradient variance Var ~ O(2^{-n})
  in deep random hardware-efficient ansatzes.
"""

import json
import os
import sys
import time
from typing import Dict, List, Any
import numpy as np

from track_c_quantum_optimization.src.barren_plateaus import ShotNoiseStudy, BarrenPlateauStudy

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def run_noise_and_barren_experiments() -> Dict[str, Any]:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print("Running Track C Shot Noise & Barren Plateau Experiments...")

    # 1. Shot Noise Scaling Study
    print("  Evaluating Shot Noise across S in [50, 100, 250, 500, 1000, 2500, 5000, 10000]...")
    shots_list = [50, 100, 250, 500, 1000, 2500, 5000, 10000]
    shot_results = ShotNoiseStudy.evaluate_shot_noise(
        num_qubits=3,
        shots_list=shots_list,
        num_trials=40,
        seed=42
    )

    # 2. Barren Plateau Scaling Study
    print("  Evaluating Barren Plateau gradient variance across qubits n in [2, 3, 4, 5, 6, 7]...")
    qubit_range = [2, 3, 4, 5, 6, 7]
    barren_results = BarrenPlateauStudy.run_qubit_variance_scaling(
        qubit_range=qubit_range,
        num_samples=30,
        seed=100
    )

    for b in barren_results:
        print(f"    n={b['num_qubits']} | Layers={b['circuit_layers']} | NumParams={b['num_parameters']} | GradVar={b['gradient_variance']:.6e} | 2^(-n)={b['theoretical_2_minus_n']:.6e}")

    results = {
        "shot_noise_study": shot_results,
        "barren_plateau_study": barren_results
    }

    # Save output
    json_path = os.path.join(RESULTS_DIR, "noise_barren_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    csv_shot_path = os.path.join(RESULTS_DIR, "shot_noise_summary.csv")
    with open(csv_shot_path, "w", encoding="utf-8") as f:
        f.write("Shots,ExactExpectation,MeanEstimate,Variance,StdDeviation,AbsoluteError,Theoretical1OverSqrtS\n")
        for r in shot_results:
            f.write(f'{r["shots"]},{r["exact_expectation"]},{r["mean_estimate"]},{r["variance"]},{r["std_deviation"]},{r["absolute_error"]},{r["theoretical_scaling_factor"]}\n')

    csv_barren_path = os.path.join(RESULTS_DIR, "barren_plateau_summary.csv")
    with open(csv_barren_path, "w", encoding="utf-8") as f:
        f.write("NumQubits,CircuitLayers,NumParams,CircuitDepth,GradientVariance,Theoretical2MinusN\n")
        for r in barren_results:
            f.write(f'{r["num_qubits"]},{r["circuit_layers"]},{r["num_parameters"]},{r["circuit_depth"]},{r["gradient_variance"]:.8e},{r["theoretical_2_minus_n"]:.8e}\n')

    print(f"Noise & Barren study completed:\n  JSON: {json_path}\n  CSV (Shot): {csv_shot_path}\n  CSV (Barren): {csv_barren_path}")
    return results


if __name__ == "__main__":
    run_noise_and_barren_experiments()

