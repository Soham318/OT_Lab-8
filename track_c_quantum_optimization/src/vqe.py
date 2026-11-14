r"""
Variational Quantum Eigensolver (VQE)
Track C: Quantum Optimization
Assignment 8 - Optimize Anything

Mathematical Formulation:
  Variational Principle:
      E(\theta) = <\psi(\theta) | H | \psi(\theta)> >= E_0
  Ground State Estimation:
      E_0 = \min_{\theta} <\psi(\theta) | H | \psi(\theta)>
  Exact Diagonalization:
      E_exact = \min(\lambda(H)) via Hermitian eigenvalue decomposition.
"""

from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy.optimize import minimize

from qiskit.quantum_info import Statevector, SparsePauliOp
from track_c_quantum_optimization.src.circuits import HardwareEfficientAnsatz


@dataclass
class VQEResult:
    """Stores full metrics of a VQE ground state energy estimation."""
    hamiltonian_name: str
    num_qubits: int
    ansatz_layers: int
    num_parameters: int
    vqe_energy: float
    exact_ground_energy: float
    energy_error: float
    relative_error: float
    optimal_parameters: np.ndarray
    optimization_iterations: int
    execution_time_ms: float
    energy_history: List[float] = field(default_factory=list)


class VQESolver:
    """
    Variational Quantum Eigensolver (VQE).
    Finds the minimum eigenvalue of a Hamiltonian using parameterized quantum circuits
    and classical optimization.
    """

    def __init__(
        self,
        hamiltonian: SparsePauliOp,
        num_qubits: int,
        ansatz_layers: int = 2,
        entanglement: str = "linear",
        name: str = "VQE Solver"
    ):
        self.hamiltonian = hamiltonian
        self.num_qubits = num_qubits
        self.ansatz_layers = ansatz_layers
        self.name = name

        # Hardware-efficient ansatz
        self.ansatz = HardwareEfficientAnsatz(
            num_qubits=num_qubits,
            num_layers=ansatz_layers,
            entanglement=entanglement,
            rotation_blocks=("ry", "rz")
        )

        # Exact ground truth eigenvalue via Hermitian matrix diagonalization
        self.exact_energy = self._compute_exact_ground_energy()

    def _compute_exact_ground_energy(self) -> float:
        """Exact diagonalization of the Hamiltonian matrix."""
        H_mat = self.hamiltonian.to_matrix()
        eigenvals = np.linalg.eigvalsh(H_mat)
        return float(np.min(eigenvals))

    @classmethod
    def create_transverse_field_ising(
        cls,
        num_qubits: int = 4,
        J: float = 1.0,
        g: float = 0.5,
        ansatz_layers: int = 2
    ) -> "VQESolver":
        r"""
        Transverse-Field Ising Model (TFIM):
            H = - J \sum_{i=0}^{n-2} Z_i Z_{i+1} - g \sum_{i=0}^{n-1} X_i
        """
        pauli_list = []
        # ZZ coupling
        for i in range(num_qubits - 1):
            term = ["I"] * num_qubits
            term[i] = "Z"
            term[i + 1] = "Z"
            pauli_list.append(("".join(term), -J))

        # Transverse X field
        for i in range(num_qubits):
            term = ["I"] * num_qubits
            term[i] = "X"
            pauli_list.append(("".join(term), -g))

        H = SparsePauliOp.from_list(pauli_list).simplify()
        return cls(H, num_qubits, ansatz_layers=ansatz_layers, name="TFIM")

    @classmethod
    def create_heisenberg_xxz(
        cls,
        num_qubits: int = 4,
        J: float = 1.0,
        delta: float = 0.5,
        ansatz_layers: int = 2
    ) -> "VQESolver":
        r"""
        Heisenberg XXZ Spin Chain:
            H = \sum_{i=0}^{n-2} J (X_i X_{i+1} + Y_i Y_{i+1} + \Delta Z_i Z_{i+1})
        """
        pauli_list = []
        for i in range(num_qubits - 1):
            for pauli, coeff in [("X", J), ("Y", J), ("Z", J * delta)]:
                term = ["I"] * num_qubits
                term[i] = pauli
                term[i + 1] = pauli
                pauli_list.append(("".join(term), coeff))

        H = SparsePauliOp.from_list(pauli_list).simplify()
        return cls(H, num_qubits, ansatz_layers=ansatz_layers, name="Heisenberg-XXZ")

    def evaluate_energy(self, theta: np.ndarray) -> float:
        """Compute exact expectation value <psi(theta) | H | psi(theta)>."""
        sv = self.ansatz.get_statevector(theta)
        return float(sv.expectation_value(self.hamiltonian).real)

    def optimize(
        self,
        method: str = "COBYLA",
        max_iters: int = 150,
        seed: int = 42
    ) -> VQEResult:
        """
        Execute classical parameter optimization to estimate minimum eigenvalue.
        """
        t0 = time.perf_counter()
        rng = np.random.RandomState(seed)
        theta_0 = rng.uniform(-np.pi, np.pi, size=self.ansatz.num_params)

        energy_history: List[float] = []

        def cost_fn(theta_vec: np.ndarray) -> float:
            e = self.evaluate_energy(theta_vec)
            energy_history.append(e)
            return e

        res = minimize(
            cost_fn,
            theta_0,
            method=method,
            options={"maxiter": max_iters, "disp": False}
        )

        opt_theta = res.x
        vqe_e = self.evaluate_energy(opt_theta)
        err = abs(vqe_e - self.exact_energy)
        rel_err = err / (abs(self.exact_energy) + 1e-12)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return VQEResult(
            hamiltonian_name=self.name,
            num_qubits=self.num_qubits,
            ansatz_layers=self.ansatz_layers,
            num_parameters=self.ansatz.num_params,
            vqe_energy=float(vqe_e),
            exact_ground_energy=float(self.exact_energy),
            energy_error=float(err),
            relative_error=float(rel_err),
            optimal_parameters=opt_theta,
            optimization_iterations=len(energy_history),
            execution_time_ms=elapsed_ms,
            energy_history=energy_history
        )
