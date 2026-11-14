"""
Bernstein-Vazirani Algorithm (Elementary Gate Construction)
Track I: Quantum Algorithms and Quantum Machine Learning

Problem:
  Find a hidden secret bitstring s in {0, 1}^n given an oracle computing the
  inner-product modulo 2: f_s(x) = s . x (mod 2) = XOR_{i=0}^{n-1} (s_i * x_i).

Complexity:
  Classical deterministic: Exactly n queries required (querying unit basis vectors e_i).
  Quantum: Exactly 1 query using phase kickback and Hadamard interference.

Circuit Design:
  Constructed MANUALLY using elementary quantum gates (H, X, CNOT, Measure).
"""

from typing import Dict, Any, List
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from track_i_quantum_algorithms.src.utils import simulate_circuit, get_circuit_metrics, export_circuit_diagram

def get_elementary_gate_explanations(secret: str) -> List[Dict[str, str]]:
    """
    Detailed gate-by-gate explanations describing the purpose of every elementary gate.
    """
    n = len(secret)
    explanations = [
        {
            "gate": "X(ancilla)",
            "purpose": "Flips the ancilla qubit from |0> to |1> so the subsequent Hadamard produces the |- > state."
        },
        {
            "gate": "H(ancilla)",
            "purpose": "Transforms ancilla |1> into |-> = (|0> - |1>)/sqrt(2), enabling phase kickback (-1)^f(x)."
        }
    ]
    for i in range(n):
        explanations.append({
            "gate": f"H(q[{i}])",
            "purpose": f"Creates an equal superposition (|0> + |1>)/sqrt(2) on input qubit {i}."
        })
    for i, bit in enumerate(secret):
        if bit == "1":
            explanations.append({
                "gate": f"CNOT(control=q[{i}], target=ancilla)",
                "purpose": f"Applies conditional phase kickback for bit position {i} because secret[{i}] == '1'."
            })
    for i in range(n):
        explanations.append({
            "gate": f"H(q[{i}])",
            "purpose": f"Interferes the kicked phases; constructively interferes to |secret[{i}]> and destructively cancels the opposite basis state."
        })
    for i in range(n):
        explanations.append({
            "gate": f"Measure(q[{i}] -> c[{i}])",
            "purpose": f"Collapses input qubit {i} into the classical measurement register."
        })
    return explanations

def build_manual_bernstein_vazirani_circuit(secret: str) -> QuantumCircuit:
    """
    Construct the Bernstein-Vazirani circuit manually using elementary gates.
    """
    n = len(secret)
    qr_in = QuantumRegister(n, "q")
    qr_anc = QuantumRegister(1, "anc")
    cr = ClassicalRegister(n, "c")
    qc = QuantumCircuit(qr_in, qr_anc, cr, name=f"BV_Manual_{secret}")

    # Step 1: Prepare Ancilla in |->
    qc.x(qr_anc[0])
    qc.h(qr_anc[0])

    # Step 2: Initialize Input Register to uniform superposition
    for i in range(n):
        qc.h(qr_in[i])

    qc.barrier()

    # Step 3: Elementary Oracle Construction
    # Qiskit orders bitstrings from right-to-left: bitstring[0] corresponds to q[n-1] or q[0]
    # We follow standard index mapping: secret[i] corresponds to qr_in[i].
    for i, bit in enumerate(reversed(secret)):
        if bit == "1":
            qc.cx(qr_in[i], qr_anc[0])

    qc.barrier()

    # Step 4: Final Hadamard Transform on Input Register
    for i in range(n):
        qc.h(qr_in[i])

    # Step 5: Measurement of Input Register
    for i in range(n):
        qc.measure(qr_in[i], cr[i])

    return qc

def run_bernstein_vazirani(secret: str, shots: int = 1024) -> Dict[str, Any]:
    """
    Execute manual Bernstein-Vazirani circuit on simulator and recover secret bitstring.
    """
    n = len(secret)
    qc = build_manual_bernstein_vazirani_circuit(secret)
    counts = simulate_circuit(qc, shots=shots)
    metrics = get_circuit_metrics(qc)
    gate_explanations = get_elementary_gate_explanations(secret)

    # Recover the most frequent bitstring
    measured_secret = max(counts, key=counts.get)
    success_fraction = counts.get(secret, 0) / shots

    diagram_path = export_circuit_diagram(qc, f"bernstein_vazirani_{secret}")

    return {
        "algorithm": "Bernstein-Vazirani",
        "secret_target": secret,
        "measured_secret": measured_secret,
        "is_correct": (measured_secret == secret),
        "success_fraction": round(success_fraction, 4),
        "counts": counts,
        "num_qubits": n + 1,
        "circuit_depth": metrics["depth"],
        "total_gates": metrics["total_gates"],
        "gate_counts": metrics["gate_counts"],
        "gate_explanations": gate_explanations,
        "diagram_file": diagram_path
    }
