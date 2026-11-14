"""
Quantum Fourier Transform (QFT) & Inverse QFT Module
Track I: Quantum Algorithms and Quantum Machine Learning

Mathematical Definition:
  The Quantum Fourier Transform maps a quantum state |j> in the computational basis
  to a superposition over all basis states |k>:
    QFT |j> = 1/sqrt(N) sum_{k=0}^{N-1} exp(2*pi*i*j*k / N) |k>
  where N = 2^n.

In product representation:
  |j_1 j_2 ... j_n> -> 1/sqrt(2^n) (|0> + e^(2*pi*i * 0.j_n) |1>) ... (|0> + e^(2*pi*i * 0.j_1...j_n) |1>)

Complexity:
  Classical Fast Fourier Transform (FFT): O(N log N) = O(n * 2^n) operations.
  Quantum Fourier Transform (QFT): O(n^2) quantum gates (exponential speedup in gate count!).
  Note: Amplitudes cannot be read out directly due to wave function collapse; QFT serves
        as a subroutine within Phase Estimation, Shor's algorithm, and Hamiltonian simulation.
"""

import math
from typing import Dict, Any, Tuple
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector
from track_i_quantum_algorithms.src.utils import get_circuit_metrics, export_circuit_diagram

def build_qft_circuit(num_qubits: int, swap_registers: bool = True) -> QuantumCircuit:
    """
    Construct the Quantum Fourier Transform circuit using elementary gates:
    Hadamards, Controlled-Phase (CP) rotations, and SWAP gates.
    """
    qc = QuantumCircuit(num_qubits, name=f"QFT_{num_qubits}q")

    for i in range(num_qubits):
        # 1. Hadamard on wire i
        qc.h(i)
        # 2. Controlled Phase gates from subsequent qubits
        for j in range(i + 1, num_qubits):
            k = j - i + 1
            theta = 2.0 * math.pi / (2.0 ** k)
            qc.cp(theta, j, i)

    # 3. Swap qubits to correct bit significance order
    if swap_registers:
        for i in range(num_qubits // 2):
            qc.swap(i, num_qubits - 1 - i)

    return qc

def build_inverse_qft_circuit(num_qubits: int, swap_registers: bool = True) -> QuantumCircuit:
    """
    Construct the Inverse Quantum Fourier Transform (QFT dagger) circuit.
    Reverses gate ordering and inverts phase rotation angles (theta -> -theta).
    """
    qft = build_qft_circuit(num_qubits, swap_registers=swap_registers)
    inv_qc = qft.inverse()
    inv_qc.name = f"IQFT_{num_qubits}q"
    return inv_qc

def verify_qft_reversibility(num_qubits: int) -> Dict[str, Any]:
    """
    Verify that IQFT * QFT = Identity matrix:
    U_{IQFT} @ U_{QFT} == I to numerical precision.
    """
    qft_qc = build_qft_circuit(num_qubits)
    iqft_qc = build_inverse_qft_circuit(num_qubits)

    combined_qc = QuantumCircuit(num_qubits)
    combined_qc.compose(qft_qc, inplace=True)
    combined_qc.compose(iqft_qc, inplace=True)

    op_combined = Operator(combined_qc).data
    identity = np.eye(2**num_qubits, dtype=complex)

    error = np.linalg.norm(op_combined - identity, ord=2)
    is_reversible = bool(error < 1e-10)

    # Test on arbitrary basis states
    test_state_errors = []
    for basis_idx in range(min(4, 2**num_qubits)):
        init_qc = QuantumCircuit(num_qubits)
        # Prepare basis state |basis_idx>
        b_str = f"{basis_idx:0{num_qubits}b}"
        for bit_pos, bit in enumerate(reversed(b_str)):
            if bit == "1":
                init_qc.x(bit_pos)
        init_qc.compose(combined_qc, inplace=True)
        sv = Statevector(init_qc)
        expected_sv = np.zeros(2**num_qubits, dtype=complex)
        expected_sv[basis_idx] = 1.0
        fidelity = float(np.abs(np.vdot(sv.data, expected_sv)) ** 2)
        test_state_errors.append(1.0 - fidelity)

    max_state_error = max(test_state_errors) if test_state_errors else 0.0

    export_circuit_diagram(qft_qc, f"qft_{num_qubits}q")
    export_circuit_diagram(iqft_qc, f"iqft_{num_qubits}q")

    return {
        "num_qubits": num_qubits,
        "is_reversible": is_reversible,
        "operator_error_norm": float(error),
        "max_state_error": float(max_state_error),
        "qft_metrics": get_circuit_metrics(qft_qc),
        "iqft_metrics": get_circuit_metrics(iqft_qc)
    }

def transform_state_vector_analytical(state_amplitudes: np.ndarray) -> np.ndarray:
    """
    Compute classical Discrete Fourier Transform matrix multiplication for exact verification.
    """
    n = len(state_amplitudes)
    dft_matrix = np.zeros((n, n), dtype=complex)
    for j in range(n):
        for k in range(n):
            dft_matrix[j, k] = np.exp(2j * np.pi * j * k / n) / np.sqrt(n)
    return dft_matrix @ state_amplitudes
