r"""
Parameterized Quantum Circuits (PQC) Module
Track C: Quantum Optimization
Assignment 8 - Optimize Anything

Demonstrates:
  1. Parameterized single-qubit rotation gates (Rx, Ry, Rz).
  2. Multi-qubit entangling gates (CNOT / CX, CZ).
  3. Layered Hardware-Efficient Ansatz (HEA) architectures.
  4. Parameter binding, statevector simulation, and shot-based measurement sampling.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector


class HardwareEfficientAnsatz:
    """
    Hardware-Efficient Parameterized Quantum Circuit (PQC).
    Architecture:
      - Initial rotation layer: Ry(theta) and Rz(phi) on all qubits.
      - Alternating entangling blocks: CNOTs between adjacent qubits (linear/circular).
      - Repeat for L layers, followed by a final rotation layer.
    """

    def __init__(
        self,
        num_qubits: int = 4,
        num_layers: int = 2,
        entanglement: str = "linear",
        rotation_blocks: Tuple[str, ...] = ("ry", "rz")
    ):
        if num_qubits < 1:
            raise ValueError("num_qubits must be >= 1.")
        if num_layers < 0:
            raise ValueError("num_layers must be >= 0.")

        self.num_qubits = num_qubits
        self.num_layers = num_layers
        self.entanglement = entanglement.lower()
        self.rotation_blocks = rotation_blocks

        # Number of parameters:
        # Each layer has (num_qubits * len(rotation_blocks)) parameters, plus final layer
        rots_per_qubit = len(self.rotation_blocks)
        self.num_params = num_qubits * rots_per_qubit * (num_layers + 1)
        self.params = ParameterVector("theta", self.num_params)

        self._circuit = self._build_circuit()

    def _build_circuit(self) -> QuantumCircuit:
        qc = QuantumCircuit(self.num_qubits)
        param_idx = 0

        # Layer 0 ... num_layers - 1
        for layer in range(self.num_layers):
            # Rotations
            for q in range(self.num_qubits):
                for rot in self.rotation_blocks:
                    p = self.params[param_idx]
                    param_idx += 1
                    if rot == "rx":
                        qc.rx(p, q)
                    elif rot == "ry":
                        qc.ry(p, q)
                    elif rot == "rz":
                        qc.rz(p, q)

            # Entangling block
            if self.num_qubits > 1:
                if self.entanglement == "linear":
                    for q in range(self.num_qubits - 1):
                        qc.cx(q, q + 1)
                elif self.entanglement == "circular":
                    for q in range(self.num_qubits - 1):
                        qc.cx(q, q + 1)
                    qc.cx(self.num_qubits - 1, 0)
                elif self.entanglement == "full":
                    for q1 in range(self.num_qubits):
                        for q2 in range(q1 + 1, self.num_qubits):
                            qc.cx(q1, q2)

        # Final rotation layer
        for q in range(self.num_qubits):
            for rot in self.rotation_blocks:
                p = self.params[param_idx]
                param_idx += 1
                if rot == "rx":
                    qc.rx(p, q)
                elif rot == "ry":
                    qc.ry(p, q)
                elif rot == "rz":
                    qc.rz(p, q)

        return qc

    @property
    def circuit(self) -> QuantumCircuit:
        return self._circuit

    @property
    def depth(self) -> int:
        return self._circuit.depth()

    def bind(self, theta_values: np.ndarray) -> QuantumCircuit:
        """Bind numerical array of parameters to circuit."""
        theta_arr = np.asarray(theta_values, dtype=np.float64).ravel()
        if len(theta_arr) != self.num_params:
            raise ValueError(
                f"Parameter length mismatch: expected {self.num_params}, got {len(theta_arr)}."
            )
        param_dict = {self.params[i]: theta_arr[i] for i in range(self.num_params)}
        return self._circuit.assign_parameters(param_dict)

    def get_statevector(self, theta_values: np.ndarray) -> Statevector:
        """Compute exact statevector |psi(theta)>."""
        bound_qc = self.bind(theta_values)
        return Statevector(bound_qc)

    def sample_counts(
        self,
        theta_values: np.ndarray,
        shots: int = 1024,
        seed: Optional[int] = None
    ) -> Dict[str, int]:
        """Sample discrete bitstring measurement counts using statevector probabilities."""
        sv = self.get_statevector(theta_values)
        if seed is not None:
            probs = np.abs(sv.data) ** 2
            probs = probs / np.sum(probs)
            rng = np.random.RandomState(seed)
            indices = rng.choice(len(probs), size=shots, p=probs)
            counts: Dict[str, int] = {}
            for idx in indices:
                b_str = f"{idx:0{self.num_qubits}b}"
                counts[b_str] = counts.get(b_str, 0) + 1
            return counts
        return sv.sample_counts(shots=shots)


class ParameterizedAnsatz(HardwareEfficientAnsatz):
    """Alias for backwards compatibility and clarity."""
    pass
