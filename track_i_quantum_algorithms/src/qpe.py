"""
Quantum Phase Estimation (QPE) Implementation
Track I: Quantum Algorithms and Quantum Machine Learning

Problem:
  Given a unitary operator U and an eigenstate |psi> such that U |psi> = exp(2*pi*i*theta) |psi>,
  estimate the unknown phase theta in [0, 1) to t bits of precision.

Mathematical Formulation:
  1. Prepare counting register with t qubits in |0>^t and target register in |psi>.
  2. Apply H^(tensor t) to counting register: 1/sqrt(2^t) sum_{k=0}^{2^t-1} |k>.
  3. Apply controlled-U^(2^j) operations for j = 0, ..., t-1, creating the state:
     1/sqrt(2^t) sum_{k=0}^{2^t-1} exp(2*pi*i*theta*k) |k> |psi>.
  4. Apply Inverse Quantum Fourier Transform (IQFT) to counting register.
  5. Measure counting register; if 2^t * theta is an integer, output is exact bitstring with 100% probability.
     If theta is not dyadic, output peaks at floor(2^t * theta) and ceil(2^t * theta).

Complexity:
  Classical: Requires simulating matrix multiplication or power iterations O(2^n).
  Quantum: O(t^2 + t * Cost(U)) operations.
"""

import math
from typing import Dict, Any, Tuple, Optional
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from track_i_quantum_algorithms.src.qft import build_inverse_qft_circuit
from track_i_quantum_algorithms.src.utils import simulate_circuit, get_circuit_metrics, export_circuit_diagram

def build_qpe_circuit(
    num_counting_qubits: int,
    phase_theta: float,
    unitary_type: str = "phase_gate"
) -> QuantumCircuit:
    """
    Construct the Quantum Phase Estimation circuit.
    Uses target register initialized to eigenstate |1> of the Phase Gate P(2*pi*theta):
      P(phi) |1> = exp(i * phi) |1> = exp(2*pi*i*theta) |1>.
    """
    t = num_counting_qubits
    qr_count = QuantumRegister(t, "count")
    qr_target = QuantumRegister(1, "target")
    cr = ClassicalRegister(t, "meas")
    qc = QuantumCircuit(qr_count, qr_target, cr, name=f"QPE_{t}t_theta_{phase_theta:.3f}")

    # Step 1: Initialize target register to eigenstate |1>
    qc.x(qr_target[0])

    # Step 2: Apply Hadamard to counting register
    for i in range(t):
        qc.h(qr_count[i])

    qc.barrier()

    # Step 3: Apply Controlled-U^(2^j) operations
    # For unitary P(2*pi*theta), P(2*pi*theta)^(2^j) = P(2*pi * theta * 2^j)
    for j in range(t):
        angle = 2.0 * math.pi * phase_theta * (2.0 ** j)
        qc.cp(angle, qr_count[j], qr_target[0])

    qc.barrier()

    # Step 4: Apply Inverse QFT to counting register
    iqft = build_inverse_qft_circuit(t, swap_registers=False)
    qc.compose(iqft, qubits=qr_count, inplace=True)

    qc.barrier()

    # Step 5: Measure counting register
    qc.measure(qr_count, cr)

    return qc

def run_quantum_phase_estimation(
    num_counting_qubits: int = 3,
    phase_theta: float = 0.375,  # 3/8 = 0.011_2 in binary
    shots: int = 1024
) -> Dict[str, Any]:
    """
    Execute Quantum Phase Estimation on simulator and extract estimated phase.
    """
    t = num_counting_qubits
    qc = build_qpe_circuit(t, phase_theta)
    counts = simulate_circuit(qc, shots=shots)
    metrics = get_circuit_metrics(qc)

    # In Qiskit, bitstring is formatted as c[t-1]...c[0].
    # Since qr_count[0] corresponds to the 2^-1 MSB of phase theta in standard QPE,
    # the bits in order from MSB to LSB are c[0], c[1], ..., c[t-1].
    # Reversing the Qiskit bitstring string (bitstring[::-1]) places MSB at the left.
    measured_phases = {}
    for bitstring, count in counts.items():
        ordered_bits = bitstring[::-1]
        int_val = int(ordered_bits, 2)
        est_phase = int_val / (2.0 ** t)
        measured_phases[est_phase] = measured_phases.get(est_phase, 0) + count

    # Most probable phase
    most_likely_phase = max(measured_phases, key=measured_phases.get)
    max_counts = measured_phases[most_likely_phase]
    success_fraction = max_counts / shots
    phase_error = abs(most_likely_phase - phase_theta)

    diagram_path = export_circuit_diagram(qc, f"qpe_{t}q_theta_{phase_theta:.3f}")

    return {
        "algorithm": "Quantum Phase Estimation",
        "num_counting_qubits": t,
        "true_phase": phase_theta,
        "estimated_phase": most_likely_phase,
        "phase_error": round(phase_error, 6),
        "is_exact_match": bool(phase_error < 1e-4),
        "dominant_bitstring_counts": counts,
        "success_fraction": round(success_fraction, 4),
        "circuit_depth": metrics["depth"],
        "total_gates": metrics["total_gates"],
        "diagram_file": diagram_path
    }
