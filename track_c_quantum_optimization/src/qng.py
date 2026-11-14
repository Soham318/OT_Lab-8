r"""
Quantum Natural Gradient (QNG) Optimization
Track C: Quantum Optimization
Assignment 8 - Optimize Anything

Mathematical Formulation:
  Fubini-Study Metric Tensor (Real part of Quantum Geometric Tensor):
      g_{ij}(\theta) = \operatorname{Re}\left(
          \langle \partial_i \psi(\theta) \mid \partial_j \psi(\theta) \rangle
          - \langle \partial_i \psi(\theta) \mid \psi(\theta) \rangle
            \langle \psi(\theta) \mid \partial_j \psi(\theta) \rangle
      \right)

  QNG Parameter Update Rule:
      \theta_{t+1} = \theta_t - \eta (g(\theta_t) + \lambda I)^{-1} \nabla \langle H \rangle(\theta_t)

  Where:
      - \eta: Learning rate.
      - \lambda: Levenberg-Marquardt / Tikhonov regularization factor (stabilizing metric inversion).
      - \nabla <H>: Parameter-shift or analytical gradient.
"""

from typing import Callable, Dict, List, Optional, Tuple, Any
import numpy as np
from qiskit.quantum_info import Statevector
from track_c_quantum_optimization.src.circuits import HardwareEfficientAnsatz
from track_c_quantum_optimization.src.gradients import ParameterShiftGradient


class QuantumNaturalGradient:
    """
    Implements Quantum Natural Gradient (QNG) using the Fubini-Study Metric Tensor.
    Optimizes variational parameters along the Riemannian quantum state manifold.
    """

    def __init__(
        self,
        ansatz: HardwareEfficientAnsatz,
        learning_rate: float = 0.05,
        regularization: float = 1e-4,
        max_iters: int = 100
    ):
        self.ansatz = ansatz
        self.learning_rate = learning_rate
        self.regularization = regularization
        self.max_iters = max_iters

    def compute_fubini_study_metric(self, theta: np.ndarray, eps: float = 1e-5) -> np.ndarray:
        r"""
        Compute the d x d Fubini-Study metric tensor g_{ij}(theta).
        Uses centered finite differences on statevectors to obtain |\partial_i \psi>.
        """
        d = len(theta)
        psi_0 = self.ansatz.get_statevector(theta).data  # (2^n,) complex vector

        # Compute partial statevector derivatives
        d_psi = np.zeros((d, len(psi_0)), dtype=np.complex128)
        for i in range(d):
            theta_plus = np.array(theta, copy=True)
            theta_plus[i] += eps
            psi_plus = self.ansatz.get_statevector(theta_plus).data

            theta_minus = np.array(theta, copy=True)
            theta_minus[i] -= eps
            psi_minus = self.ansatz.get_statevector(theta_minus).data

            d_psi[i] = (psi_plus - psi_minus) / (2.0 * eps)

        # Inner products
        # overlap_0[i] = <psi_0 | d_psi_i>
        overlap_0 = np.conj(psi_0) @ d_psi.T  # (d,)

        # Metric tensor g_ij = Re( <d_psi_i | d_psi_j> - <d_psi_i | psi_0> <psi_0 | d_psi_j> )
        # D_matrix_ij = <d_psi_i | d_psi_j> = d_psi @ d_psi^\dagger
        D_matrix = np.conj(d_psi) @ d_psi.T  # (d, d)
        outer_overlap = np.outer(np.conj(overlap_0), overlap_0)  # (d, d)

        g = np.real(D_matrix - outer_overlap)
        # Symmetrize
        g = 0.5 * (g + g.T)
        return g

    def optimize(
        self,
        energy_fn: Callable[[np.ndarray], float],
        theta_init: np.ndarray
    ) -> Tuple[np.ndarray, float, List[float]]:
        """
        Execute Quantum Natural Gradient descent:
            theta_{t+1} = theta_t - eta * (g(theta_t) + lambda * I)^{-1} * grad(theta_t)
        """
        theta = np.array(theta_init, dtype=np.float64, copy=True)
        d = len(theta)
        history = [energy_fn(theta)]

        for t in range(self.max_iters):
            # Compute Euclidean gradient via parameter-shift rule
            grad = ParameterShiftGradient.compute_gradient(energy_fn, theta)

            # Compute Fubini-Study metric tensor
            g = self.compute_fubini_study_metric(theta)

            # Regularized metric inversion: (g + lambda * I)^{-1}
            g_reg = g + self.regularization * np.eye(d)
            try:
                nat_grad = np.linalg.solve(g_reg, grad)
            except np.linalg.LinAlgError:
                nat_grad = np.linalg.pinv(g_reg) @ grad

            # Parameter update
            theta = theta - self.learning_rate * nat_grad
            history.append(energy_fn(theta))

        return theta, history[-1], history
