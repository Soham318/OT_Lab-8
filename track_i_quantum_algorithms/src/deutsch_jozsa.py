"""
Deutsch-Jozsa Algorithm Implementation
Track I: Quantum Algorithms and Quantum Machine Learning

Problem:
  Given a boolean function f: {0, 1}^n -> {0, 1} promised to be either constant
  (f(x) is constant for all x) or balanced (f(x) = 0 for half of inputs and 1 for the other half),
  determine whether f is constant or balanced with a single query.

Complexity:
  Classical deterministic: O(2^(n-1) + 1) queries in the worst case.
  Quantum: O(1) query using phase kickback and Hadamard interference.
"""

from typing import Dict, Any, Tuple
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from track_i_quantum_algorithms.src.utils import simulate_circuit, get_circuit_metrics, export_circuit_diagram

def create_dj_oracle(num_qubits: int, oracle_type: str = "balanced", constant_val: int = 0) -> QuantumCircuit:
    """
    Construct quantum oracle U_f |x>|y> = |x>|y ^ f(x)>.
    num_qubits: number of input qubits (ancilla is qubit index num_qubits).
    """
    total_qubits = num_qubits + 1
    oracle = QuantumCircuit(total_qubits, name=f"Oracle_{oracle_type}")
    ancilla = num_qubits

    if oracle_type == "constant":
        if constant_val == 1:
            oracle.x(ancilla)
        # If constant_val == 0, identity (no gates needed)
    elif oracle_type == "balanced":
        # Balanced oracle using CNOTs from input qubits to ancilla
        # Example: f(x) = x_0 (or alternating parity)
        oracle.cx(0, ancilla)
    elif oracle_type == "balanced_multi":
        # Multi-qubit balanced parity: f(x) = x_0 ^ x_1 ...
        for q in range(min(num_qubits, 2)):
            oracle.cx(q, ancilla)
    else:
        raise ValueError(f"Unknown oracle_type: {oracle_type}. Must be 'constant' or 'balanced'.")

    return oracle

def build_deutsch_jozsa_circuit(num_qubits: int, oracle_type: str = "balanced", constant_val: int = 0) -> QuantumCircuit:
    """
    Construct the complete Deutsch-Jozsa quantum circuit.
    Registers:
      - Input register: n qubits
      - Ancilla register: 1 qubit initialized to |->
      - Classical register: n bits for measuring the input register
    """
    qr_in = QuantumRegister(num_qubits, "x")
    qr_anc = QuantumRegister(1, "anc")
    cr = ClassicalRegister(num_qubits, "c")
    qc = QuantumCircuit(qr_in, qr_anc, cr)

    # 1. Initialize ancilla qubit to |1> then apply H to make |->
    qc.x(qr_anc[0])
    qc.h(qr_anc[0])

    # 2. Apply Hadamard to all input qubits to generate uniform superposition
    for q in range(num_qubits):
        qc.h(qr_in[q])

    qc.barrier()

    # 3. Apply Oracle
    oracle = create_dj_oracle(num_qubits, oracle_type, constant_val)
    qc.compose(oracle, inplace=True)

    qc.barrier()

    # 4. Apply Hadamard to all input qubits
    for q in range(num_qubits):
        qc.h(qr_in[q])

    # 5. Measure input register
    qc.measure(qr_in, cr)

    return qc

def run_deutsch_jozsa(num_qubits: int, oracle_type: str = "balanced", constant_val: int = 0, shots: int = 1024) -> Dict[str, Any]:
    """
    Execute Deutsch-Jozsa algorithm on the local simulator and classify the oracle.
    """
    qc = build_deutsch_jozsa_circuit(num_qubits, oracle_type, constant_val)
    counts = simulate_circuit(qc, shots=shots)
    metrics = get_circuit_metrics(qc)

    # All zeros bitstring '0' * n signifies CONSTANT
    zero_string = "0" * num_qubits
    zero_count = counts.get(zero_string, 0)
    zero_fraction = zero_count / shots

    classified = "constant" if zero_fraction > 0.9 else "balanced"
    export_circuit_diagram(qc, f"deutsch_jozsa_{oracle_type}_{num_qubits}q")

    return {
        "algorithm": "Deutsch-Jozsa",
        "num_qubits": num_qubits,
        "oracle_type": oracle_type,
        "constant_val": constant_val,
        "classification": classified,
        "is_correct": (classified == oracle_type),
        "zero_state_fraction": round(zero_fraction, 4),
        "counts": counts,
        "metrics": metrics
    }
