r"""
VQE Benchmark on Transverse Ising & Heisenberg Spin Models
Track C: Quantum Optimization
Assignment 8 - Optimize Anything

Evaluates VQE convergence against exact diagonalization on:
  1. Transverse-Field Ising Model (TFIM) (3 and 4 qubits)
  2. Heisenberg XXZ Spin Chain (3 and 4 qubits)
"""

import json
import os
import sys
import time
from typing import Dict, List, Any
import numpy as np

from track_c_quantum_optimization.src.vqe import VQESolver

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def run_vqe_experiments() -> Dict[str, Any]:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print("Running Track C VQE Ground State Benchmarks...")

    benchmarks = [
        ("TFIM (3 Qubits)", lambda: VQESolver.create_transverse_field_ising(num_qubits=3, J=1.0, g=0.8, ansatz_layers=1)),
        ("TFIM (4 Qubits)", lambda: VQESolver.create_transverse_field_ising(num_qubits=4, J=1.0, g=0.8, ansatz_layers=1)),
        ("Heisenberg-XXZ (3 Qubits)", lambda: VQESolver.create_heisenberg_xxz(num_qubits=3, J=1.0, delta=0.5, ansatz_layers=1)),
        ("Heisenberg-XXZ (4 Qubits)", lambda: VQESolver.create_heisenberg_xxz(num_qubits=4, J=1.0, delta=0.5, ansatz_layers=1))
    ]

    all_records = []
    csv_rows = []

    for name, factory in benchmarks:
        print(f"  Evaluating {name}...")
        vqe = factory()
        res = vqe.optimize(method="BFGS", max_iters=150, seed=42)

        rec = {
            "model_name": name,
            "num_qubits": res.num_qubits,
            "ansatz_layers": res.ansatz_layers,
            "num_parameters": res.num_parameters,
            "vqe_energy": round(res.vqe_energy, 6),
            "exact_energy": round(res.exact_ground_energy, 6),
            "energy_error": round(res.energy_error, 6),
            "relative_error_pct": round(res.relative_error * 100.0, 4),
            "runtime_ms": round(res.execution_time_ms, 2),
            "iterations": res.optimization_iterations,
            "energy_history": [round(e, 4) for e in res.energy_history[::max(1, len(res.energy_history)//25)]]
        }
        all_records.append(rec)
        csv_rows.append(rec)
        print(f"    Exact E={res.exact_ground_energy:.4f} | VQE E={res.vqe_energy:.4f} | Rel Error={res.relative_error*100:.2f}% | Runtime={res.execution_time_ms:.1f}ms")

    # Save output
    json_path = os.path.join(RESULTS_DIR, "vqe_benchmark_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2)

    csv_path = os.path.join(RESULTS_DIR, "vqe_benchmark_summary.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("Model,NumQubits,Layers,NumParams,VQEEnergy,ExactEnergy,AbsError,RelErrorPct,RuntimeMs,Iterations\n")
        for r in csv_rows:
            f.write(f'"{r["model_name"]}",{r["num_qubits"]},{r["ansatz_layers"]},{r["num_parameters"]},{r["vqe_energy"]},{r["exact_energy"]},{r["energy_error"]},{r["relative_error_pct"]},{r["runtime_ms"]},{r["iterations"]}\n')

    print(f"VQE benchmark completed:\n  JSON: {json_path}\n  CSV:  {csv_path}")
    return {"results": all_records}


if __name__ == "__main__":
    run_vqe_experiments()

