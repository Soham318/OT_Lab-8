"""
Quantum Utilities and Simulation Helpers for Track I.
Supports:
- Local statevector simulation and shot-based sampling via Qiskit primitives
- Circuit metrics extraction (depth, gate counts, qubit counts)
- Circuit diagram export (ASCII text and Matplotlib figures)
- Analytical bitstring probability computation
"""

import os
from typing import Dict, Any, Optional
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIRCUITS_DIR = os.path.join(BASE_DIR, "circuits")
os.makedirs(CIRCUITS_DIR, exist_ok=True)

def simulate_circuit(
    qc: QuantumCircuit,
    shots: int = 1024,
    seed: Optional[int] = 42
) -> Dict[str, int]:
    """
    Simulate a quantum circuit and return bitstring measurement counts.
    Supports circuits with or without classical measurement operations.
    """
    # If the circuit already contains measurement operations, use StatevectorSampler
    has_measurements = any(inst.operation.name == "measure" for inst in qc.data)

    if has_measurements:
        sampler = StatevectorSampler(default_shots=shots, seed=seed)
        job = sampler.run([(qc,)])
        res = job.result()[0]
        # Locate the bitstring data container
        data_keys = list(res.data.keys())
        if not data_keys:
            return {}
        counts_dict = res.data[data_keys[0]].get_counts()
        return {str(k): int(v) for k, v in counts_dict.items()}
    else:
        # Use exact Statevector sampling with reproducible RNG
        sv = Statevector(qc)
        probs = np.abs(sv.data) ** 2
        probs = probs / np.sum(probs)
        rng = np.random.RandomState(seed)
        indices = rng.choice(len(probs), size=shots, p=probs)
        n_qubits = qc.num_qubits
        counts: Dict[str, int] = {}
        for idx in indices:
            b_str = f"{idx:0{n_qubits}b}"
            counts[b_str] = counts.get(b_str, 0) + 1
        return counts

def get_statevector_probabilities(qc: QuantumCircuit) -> Dict[str, float]:
    """Compute exact analytical measurement probabilities |<b|psi>|^2 for all basis states."""
    # Circuit must not have measurements for statevector calculation
    pure_qc = qc.copy()
    pure_qc.data = [inst for inst in pure_qc.data if inst.operation.name != "measure"]
    sv = Statevector(pure_qc)
    probs = np.abs(sv.data) ** 2
    n_qubits = pure_qc.num_qubits
    return {f"{i:0{n_qubits}b}": float(probs[i]) for i in range(len(probs))}

def get_circuit_metrics(qc: QuantumCircuit) -> Dict[str, Any]:
    """Extract depth, gate counts, qubit counts, and total operations from a QuantumCircuit."""
    ops = dict(qc.count_ops())
    # Exclude measurement and barrier from gate count metrics if desired, but report both
    total_gates = sum(v for k, v in ops.items() if k not in ["measure", "barrier"])
    return {
        "num_qubits": qc.num_qubits,
        "num_clbits": qc.num_clbits,
        "depth": qc.depth(),
        "total_gates": total_gates,
        "gate_counts": ops
    }

def export_circuit_diagram(qc: QuantumCircuit, filename: str) -> str:
    """Save ASCII diagram of the quantum circuit to the circuits/ directory."""
    text_diagram = qc.draw(output="text")
    filepath = os.path.join(CIRCUITS_DIR, f"{filename}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(text_diagram))
    return filepath
