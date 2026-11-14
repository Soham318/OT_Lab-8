r"""
Quantum Gradient Methods: Parameter-Shift Rule & SPSA
Track C: Quantum Optimization
Assignment 8 - Optimize Anything

Mathematical Formulation:
  1. Parameter-Shift Rule:
     For unitary U(\theta) = exp(-i (\theta/2) P) where P is a Pauli generator (P^2 = I):
         \frac{\partial <H>}{\partial \theta_j} = \frac{<H>(\theta + (\pi/2) e_j) - <H>(\theta - (\pi/2) e_j)}{2}
     This is an EXACT analytical quantum derivative.

  2. Centered Finite-Difference Baseline:
         \frac{\partial <H>}{\partial \theta_j} \approx \frac{<H>(\theta + \epsilon e_j) - <H>(\theta - \epsilon e_j)}{2 \epsilon}

  3. Simultaneous Perturbation Stochastic Approximation (SPSA):
     Evaluates only 2 noisy circuit calls per step, perturbing all parameters simultaneously:
         \Delta_k \in {-1, +1}^d
         g_k = \frac{f(\theta + c_k \Delta_k) - f(\theta - c_k \Delta_k)}{2 c_k} \Delta_k
         \theta_{k+1} = \theta_k - a_k g_k
"""

from typing import Callable, Dict, List, Optional, Tuple, Any
import numpy as np


class ParameterShiftGradient:
    """
    Computes exact analytical quantum gradients using the Parameter-Shift Rule
    and compares against finite differences.
    """

    @staticmethod
    def compute_gradient(
        energy_fn: Callable[[np.ndarray], float],
        theta: np.ndarray,
        shift: float = np.pi / 2.0
    ) -> np.ndarray:
        """
        Exact Parameter-Shift Rule:
            grad[j] = (f(theta + shift * e_j) - f(theta - shift * e_j)) / (2 * sin(shift))
        For shift = pi/2, denominator is 2 * sin(pi/2) = 2.
        """
        d = len(theta)
        grad = np.zeros(d, dtype=np.float64)
        denom = 2.0 * np.sin(shift)

        for j in range(d):
            theta_plus = np.array(theta, copy=True)
            theta_plus[j] += shift
            f_plus = energy_fn(theta_plus)

            theta_minus = np.array(theta, copy=True)
            theta_minus[j] -= shift
            f_minus = energy_fn(theta_minus)

            grad[j] = (f_plus - f_minus) / denom

        return grad

    @staticmethod
    def compute_finite_difference(
        energy_fn: Callable[[np.ndarray], float],
        theta: np.ndarray,
        eps: float = 1e-5
    ) -> np.ndarray:
        """Centered numerical finite-difference gradient."""
        d = len(theta)
        grad = np.zeros(d, dtype=np.float64)

        for j in range(d):
            theta_plus = np.array(theta, copy=True)
            theta_plus[j] += eps
            f_plus = energy_fn(theta_plus)

            theta_minus = np.array(theta, copy=True)
            theta_minus[j] -= eps
            f_minus = energy_fn(theta_minus)

            grad[j] = (f_plus - f_minus) / (2.0 * eps)

        return grad


class SPSAOptimizer:
    """
    Simultaneous Perturbation Stochastic Approximation (SPSA).
    Spall (1998) 2-measurement stochastic gradient optimization.
    Extremely efficient in quantum regimes with shot noise.
    """

    def __init__(
        self,
        a: float = 0.2,
        c: float = 0.1,
        alpha: float = 0.602,
        gamma: float = 0.101,
        A: Optional[float] = None,
        max_iters: int = 150,
        seed: int = 42
    ):
        self.a = a
        self.c = c
        self.alpha = alpha
        self.gamma = gamma
        self.A = A if A is not None else 0.1 * max_iters
        self.max_iters = max_iters
        self.rng = np.random.RandomState(seed)

    def optimize(
        self,
        cost_fn: Callable[[np.ndarray], float],
        theta_init: np.ndarray
    ) -> Tuple[np.ndarray, float, List[float]]:
        """
        Execute SPSA optimization:
            Takes only 2 function evaluations per iteration!
        """
        theta = np.array(theta_init, dtype=np.float64, copy=True)
        d = len(theta)
        history = [cost_fn(theta)]

        for k in range(self.max_iters):
            # Gains
            a_k = self.a / ((self.A + k + 1.0) ** self.alpha)
            c_k = self.c / ((k + 1.0) ** self.gamma)

            # Random Bernoulli perturbation direction Delta \in {-1, +1}^d
            delta = self.rng.choice([-1.0, 1.0], size=d)

            # 2 function calls
            theta_plus = theta + c_k * delta
            theta_minus = theta - c_k * delta

            y_plus = cost_fn(theta_plus)
            y_minus = cost_fn(theta_minus)

            # Gradient estimate: g_k = ((y_plus - y_minus) / (2 * c_k)) * delta^{-1}
            # Since delta_i in {-1, 1}, 1 / delta_i = delta_i
            g_k = ((y_plus - y_minus) / (2.0 * c_k)) * delta

            # Update parameters
            theta = theta - a_k * g_k
            history.append(cost_fn(theta))

        return theta, history[-1], history

