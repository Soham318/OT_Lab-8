"""
Shor's Factoring Algorithm Demonstration (Factoring N = 15)
Track I: Quantum Algorithms and Quantum Machine Learning

Problem:
  Factor an odd composite integer N = p * q into its non-trivial prime factors.

Complexity:
  Classical best (General Number Field Sieve - GNFS):
    Sub-exponential: O(exp((c + o(1)) * (ln N)^(1/3) * (ln ln N)^(2/3))).
  Quantum (Shor's Algorithm):
    Polynomial time: O((log N)^2 * (log log N) * (log log log N)) ~ O((log N)^3).
    Provides an exponential speedup, threatening RSA cryptography on fault-tolerant hardware.

Pipeline Stages:
  1. Classical Preprocessing: Check parity, prime power tests, select coprime base a in (1, N).
  2. Quantum Period Finding:
     - Initialize counting register (t qubits) and target register (4 qubits for N=15).
     - Apply modular exponentiation: |k>|y> -> |k> |(a^k * y) mod N>.
     - Apply Inverse QFT to counting register to extract phase s/r.
  3. Classical Post-Processing:
     - Use Continued Fractions expansion to convert measured phase phi into rational fraction s/r.
     - Extract period r.
     - If r is even and a^(r/2) != -1 (mod N), compute candidate factors:
       gcd(a^(r/2) - 1, N) and gcd(a^(r/2) + 1, N).
"""

import math
import fractions
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import UnitaryGate
from track_i_quantum_algorithms.src.qft import build_inverse_qft_circuit
from track_i_quantum_algorithms.src.utils import simulate_circuit, get_circuit_metrics, export_circuit_diagram

def build_modular_multiplication_gate(a_power: int, N: int = 15) -> UnitaryGate:
    """
    Construct unitary permutation operator U for multiplication by a_power modulo N:
    U |y> = |(a_power * y) mod N> for y coprime to N, and identity otherwise.
    For N=15, dimension is 16x16 (4 qubits).
    """
    dim = 16
    U_mat = np.zeros((dim, dim), dtype=complex)
    for y in range(dim):
        if y < N and math.gcd(y, N) == 1:
            target = (a_power * y) % N
        else:
            target = y
        U_mat[target, y] = 1.0
    return UnitaryGate(U_mat, label=f"*{a_power} mod {N}")

def build_shor_circuit(a: int = 7, N: int = 15, num_counting_qubits: int = 3) -> QuantumCircuit:
    """
    Construct the quantum period-finding circuit for f(x) = a^x mod N.
    """
    t = num_counting_qubits
    qr_count = QuantumRegister(t, "count")
    qr_target = QuantumRegister(4, "target")
    cr = ClassicalRegister(t, "meas")
    qc = QuantumCircuit(qr_count, qr_target, cr, name=f"Shor_{N}_base_{a}")

    # Step 1: Initialize target register to |1> (0001)
    qc.x(qr_target[0])

    # Step 2: Initialize counting register to uniform superposition
    for i in range(t):
        qc.h(qr_count[i])

    qc.barrier()

    # Step 3: Apply Controlled Modular Exponentiation gates
    # Control qubit j controls multiplication by a^(2^j) mod N
    for j in range(t):
        power = (a ** (2 ** j)) % N
        u_gate = build_modular_multiplication_gate(power, N)
        cu_gate = u_gate.control(1)
        qc.append(cu_gate, [qr_count[j]] + list(qr_target))

    qc.barrier()

    # Step 4: Apply Inverse QFT to counting register
    iqft = build_inverse_qft_circuit(t, swap_registers=False)
    qc.compose(iqft, qubits=qr_count, inplace=True)

    qc.barrier()

    # Step 5: Measure counting register
    qc.measure(qr_count, cr)

    return qc

def continued_fraction_period(phase: float, N: int) -> int:
    """
    Use continued fractions to find the best rational approximation s/r with r < N.
    """
    if phase == 0.0:
        return 1
    frac = fractions.Fraction(phase).limit_denominator(N)
    return frac.denominator

def run_shor_factoring(a: int = 7, N: int = 15, num_counting_qubits: int = 3, shots: int = 1024) -> Dict[str, Any]:
    """
    Execute full Shor's algorithm pipeline to factor composite integer N:
    1. Classical checks
    2. Quantum period finding
    3. Classical factor extraction
    """
    # Classical validation
    if N % 2 == 0:
        return {"status": "Trivial", "factors": [2, N // 2], "method": "Even check"}
    if math.gcd(a, N) != 1:
        g = math.gcd(a, N)
        return {"status": "Lucky Guess", "factors": [g, N // g], "method": "Classical GCD"}

    qc = build_shor_circuit(a=a, N=N, num_counting_qubits=num_counting_qubits)
    counts = simulate_circuit(qc, shots=shots)
    metrics = get_circuit_metrics(qc)

    diagram_path = export_circuit_diagram(qc, f"shor_{N}_base_{a}")

    # Process all measurement outcomes
    t = num_counting_qubits
    outcomes = []
    discovered_factors = set()

    for bitstring, count in counts.items():
        ordered_bits = bitstring[::-1]
        int_val = int(ordered_bits, 2)
        phase = int_val / (2.0 ** t)
        r = continued_fraction_period(phase, N)

        # Check if r is candidate period (a^r = 1 mod N)
        is_valid_period = (pow(a, r, N) == 1) if r > 0 else False
        factors_found = []

        if is_valid_period and r % 2 == 0:
            half_power = pow(a, r // 2, N)
            if half_power != N - 1: # Not congruent to -1 mod N
                f1 = math.gcd(half_power - 1, N)
                f2 = math.gcd(half_power + 1, N)
                for f in [f1, f2]:
                    if 1 < f < N and N % f == 0:
                        factors_found.append(f)
                        discovered_factors.add(f)

        outcomes.append({
            "bitstring": bitstring,
            "int_val": int_val,
            "phase": phase,
            "extracted_period": r,
            "is_valid_period": is_valid_period,
            "counts": count,
            "factors_found": factors_found
        })

    # Sort discovered factors
    factors_list = sorted(list(discovered_factors))
    if len(factors_list) == 1:
        other_factor = N // factors_list[0]
        if other_factor not in factors_list:
            factors_list.append(other_factor)
            factors_list.sort()

    is_success = (len(factors_list) >= 2 and (factors_list[0] * factors_list[1] == N))

    return {
        "algorithm": "Shor's Factoring Algorithm",
        "composite_N": N,
        "chosen_base_a": a,
        "true_period": 4, # 7^4 = 2401 = 1 mod 15
        "num_counting_qubits": t,
        "target_qubits": 4,
        "total_qubits": t + 4,
        "is_successful": is_success,
        "extracted_factors": factors_list,
        "measurement_counts": counts,
        "detailed_outcomes": outcomes,
        "circuit_depth": metrics["depth"],
        "total_gates": metrics["total_gates"],
        "diagram_file": diagram_path,
        "simulation_notes": (
            "Classical simulation of Shor's algorithm on a CPU stores the full 2^(t+4) statevector, "
            "scaling exponentially O(2^n). On physical fault-tolerant quantum hardware, the quantum state "
            "exists in Hilbert space without classical memory explosion, delivering genuine O((log N)^3) speedup."
        )
    }
