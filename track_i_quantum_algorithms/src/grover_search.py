"""
Grover's Search Algorithm (Manual Elementary Gate Construction)
Track I: Quantum Algorithms and Quantum Machine Learning

Problem:
  Locate a unique marked item omega in an unsorted search space of size N = 2^n.

Complexity:
  Classical unstructured search: O(N) queries on average (N/2 evaluations).
  Quantum Grover search: O(sqrt(N)) queries with quadratic speedup (provably optimal).

Optimal Iteration Count:
  R = round(pi/4 * sqrt(N/M)) for M marked items.
  For N=4 (n=2, M=1): R = 1 iteration (achieves 100% success probability).
  For N=8 (n=3, M=1): R = 2 iterations (achieves ~94.5% success probability).
"""

import math
from typing import Dict, Any, List, Optional
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from track_i_quantum_algorithms.src.utils import simulate_circuit, get_circuit_metrics, export_circuit_diagram, get_statevector_probabilities

def create_elementary_oracle(num_qubits: int, target: str) -> QuantumCircuit:
    """
    Construct Phase Oracle U_omega = I - 2|omega><omega| using elementary gates.
    Applies a negative sign (-1) strictly to the basis state |omega>.
    """
    qc = QuantumCircuit(num_qubits, name=f"Oracle_{target}")

    # Flip qubits where target has '0' so that target maps to |11...1>
    # Note: Qiskit index 0 is rightmost bit in standard string representation
    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            qc.x(i)

    # Multi-controlled Z gate: flips phase of |11...1>
    if num_qubits == 2:
        qc.cz(0, 1)
    elif num_qubits == 3:
        # Multi-controlled Z via H + CCX + H on target wire
        qc.h(2)
        qc.ccx(0, 1, 2)
        qc.h(2)
    elif num_qubits == 4:
        qc.h(3)
        qc.mcx([0, 1, 2], 3)
        qc.h(3)
    else:
        # General multi-controlled phase flip
        qc.h(num_qubits - 1)
        qc.mcx(list(range(num_qubits - 1)), num_qubits - 1)
        qc.h(num_qubits - 1)

    # Undo X flips
    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            qc.x(i)

    return qc

def create_elementary_diffuser(num_qubits: int) -> QuantumCircuit:
    """
    Construct Grover Diffusion Operator U_s = 2|s><s| - I using elementary gates:
    U_s = H^(tensor n) X^(tensor n) (MCZ) X^(tensor n) H^(tensor n).
    Performs reflection (inversion) about the mean state |s>.
    """
    qc = QuantumCircuit(num_qubits, name="Diffuser")

    # 1. H on all qubits
    for i in range(num_qubits):
        qc.h(i)

    # 2. X on all qubits
    for i in range(num_qubits):
        qc.x(i)

    # 3. Multi-controlled Z gate on |11...1>
    if num_qubits == 2:
        qc.cz(0, 1)
    elif num_qubits == 3:
        qc.h(2)
        qc.ccx(0, 1, 2)
        qc.h(2)
    elif num_qubits == 4:
        qc.h(3)
        qc.mcx([0, 1, 2], 3)
        qc.h(3)
    else:
        qc.h(num_qubits - 1)
        qc.mcx(list(range(num_qubits - 1)), num_qubits - 1)
        qc.h(num_qubits - 1)

    # 4. X on all qubits
    for i in range(num_qubits):
        qc.x(i)

    # 5. H on all qubits
    for i in range(num_qubits):
        qc.h(i)

    return qc

def get_grover_gate_explanations(num_qubits: int, target: str) -> List[Dict[str, str]]:
    """Detailed gate-by-gate explanations of Grover circuit components."""
    return [
        {
            "stage": "Initialization (H^n)",
            "purpose": "Creates equal superposition |s> = 1/sqrt(N) sum_x |x> across all 2^n basis states."
        },
        {
            "stage": "Oracle Bit Flipping (X)",
            "purpose": f"Inverts bits where target={target} has '0', mapping |{target}> to |11...1>."
        },
        {
            "stage": "Multi-Controlled Phase Flip (MCZ)",
            "purpose": "Applies a phase factor of -1 to the |11...1> state (phase kickback on target)."
        },
        {
            "stage": "Oracle Bit Unflipping (X)",
            "purpose": "Restores original computational basis mapping for all non-target states."
        },
        {
            "stage": "Diffuser Basis Change (H^n + X^n)",
            "purpose": "Rotates coordinate frame such that equal superposition |s> aligns with |11...1>."
        },
        {
            "stage": "Diffuser Phase Flip (MCZ)",
            "purpose": "Applies -1 phase to the uniform mean component, implementing 2|s><s| - I."
        },
        {
            "stage": "Diffuser Restoration (X^n + H^n)",
            "purpose": "Rotates coordinate frame back to computational basis, amplifying target amplitude."
        },
        {
            "stage": "Measurement",
            "purpose": "Collapses the wave function; marked state observed with amplified probability."
        }
    ]

def build_manual_grover_circuit(
    num_qubits: int,
    target: str,
    iterations: Optional[int] = None
) -> QuantumCircuit:
    """
    Construct the complete Grover search circuit manually using elementary gates.
    """
    if len(target) != num_qubits:
        raise ValueError(f"Target length {len(target)} must match num_qubits {num_qubits}.")

    if iterations is None:
        iterations = max(1, math.floor((math.pi / 4.0) * math.sqrt(2**num_qubits)))

    qr = QuantumRegister(num_qubits, "q")
    cr = ClassicalRegister(num_qubits, "c")
    qc = QuantumCircuit(qr, cr, name=f"Grover_{num_qubits}q_target_{target}")

    # Step 1: Initialize all qubits to equal superposition
    for i in range(num_qubits):
        qc.h(i)

    # Step 2: Apply Grover Iterations (Oracle + Diffuser)
    oracle = create_elementary_oracle(num_qubits, target)
    diffuser = create_elementary_diffuser(num_qubits)

    for it in range(iterations):
        qc.barrier()
        qc.compose(oracle, inplace=True)
        qc.barrier()
        qc.compose(diffuser, inplace=True)

    qc.barrier()
    # Step 3: Measurement
    qc.measure(qr, cr)

    return qc

def track_grover_amplitude_trajectory(num_qubits: int, target: str, max_iterations: int = 4) -> List[Dict[str, Any]]:
    """
    Track exact analytical probability of target state vs non-target states across iterations.
    """
    trajectory = []
    for it in range(max_iterations + 1):
        qc = build_manual_grover_circuit(num_qubits, target, iterations=it)
        probs = get_statevector_probabilities(qc)
        target_prob = probs.get(target, 0.0)
        trajectory.append({
            "iteration": it,
            "target_probability": round(target_prob, 4),
            "target_amplitude": round(math.sqrt(target_prob), 4),
            "other_probability": round(1.0 - target_prob, 4)
        })
    return trajectory

def run_grover_search(
    num_qubits: int,
    target: str,
    iterations: Optional[int] = None,
    shots: int = 1024
) -> Dict[str, Any]:
    """
    Execute manual Grover circuit on local simulator and measure target bitstring.
    """
    if iterations is None:
        iterations = max(1, math.floor((math.pi / 4.0) * math.sqrt(2**num_qubits)))

    qc = build_manual_grover_circuit(num_qubits, target, iterations=iterations)
    counts = simulate_circuit(qc, shots=shots)
    metrics = get_circuit_metrics(qc)

    measured_target = max(counts, key=counts.get)
    target_counts = counts.get(target, 0)
    success_rate = target_counts / shots

    diagram_path = export_circuit_diagram(qc, f"grover_{num_qubits}q_{target}")
    trajectory = track_grover_amplitude_trajectory(num_qubits, target, max_iterations=min(4, 2**num_qubits))

    return {
        "algorithm": "Grover's Search",
        "num_qubits": num_qubits,
        "search_space_size": 2**num_qubits,
        "target": target,
        "iterations": iterations,
        "measured_target": measured_target,
        "is_correct": (measured_target == target),
        "success_rate": round(success_rate, 4),
        "counts": counts,
        "circuit_depth": metrics["depth"],
        "total_gates": metrics["total_gates"],
        "gate_counts": metrics["gate_counts"],
        "trajectory": trajectory,
        "gate_explanations": get_grover_gate_explanations(num_qubits, target),
        "diagram_file": diagram_path
    }
