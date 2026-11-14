"""
Second-Order and Curvature-Based Optimizers
Track A: Continuous Optimization
Assignment 8 - Optimize Anything

Implements:
  1. Newton's Method (with Levenberg-Marquardt spectral damping for non-convex Hessians)
  2. Gauss-Newton Method (for non-linear least squares problems approximating H \approx J^T J)
"""

from dataclasses import dataclass
import time
from typing import Callable, List, Optional, Tuple
import numpy as np

from .optimizers import OptimizerResult


class NewtonsMethod:
    """
    Classical and Regularized Newton's Method:
        delta_x = - (H(x_t) + lambda * I)^{-1} * grad(x_t)
        x_{t+1} = x_t + alpha * delta_x
    Features:
      - Quadratic local convergence rate near local minima: ||x_{t+1} - x*|| = O(||x_t - x*||^2).
      - Levenberg-Marquardt spectral regularization: adds lambda * I when Hessian is non-positive-definite
        or near saddle points, gracefully interpolating between pure Newton step and gradient descent.
      - Armijo backtracking line search to ensure sufficient decrease.
    """

    def __init__(
        self,
        damping: float = 1e-4,
        max_iters: int = 100,
        tol: float = 1e-7,
        use_line_search: bool = True
    ):
        self.damping = damping
        self.max_iters = max_iters
        self.tol = tol
        self.use_line_search = use_line_search

    def minimize(
        self,
        value_fn: Callable[[np.ndarray], float],
        grad_fn: Callable[[np.ndarray], np.ndarray],
        hess_fn: Callable[[np.ndarray], np.ndarray],
        x_init: np.ndarray
    ) -> OptimizerResult:
        x = np.array(x_init, dtype=np.float64, copy=True)
        dim = len(x)
        history_loss = []
        history_grad_norm = []
        converged = False

        t0 = time.perf_counter()
        for it in range(self.max_iters):
            val = value_fn(x)
            g = grad_fn(x)
            gnorm = float(np.linalg.norm(g))

            history_loss.append(val)
            history_grad_norm.append(gnorm)

            if gnorm < self.tol:
                converged = True
                break

            H = hess_fn(x)
            # Regularize Hessian if ill-conditioned or negative eigenvalues exist
            # Eigenvalue decomposition check
            try:
                min_eig = np.min(np.linalg.eigvalsh(H))
            except np.linalg.LinAlgError:
                min_eig = -1.0

            curr_damping = self.damping
            if min_eig <= 1e-6:
                curr_damping += abs(min_eig) + 0.1

            H_reg = H + curr_damping * np.eye(dim)

            try:
                # Solve H_reg * delta_x = -g
                delta_x = np.linalg.solve(H_reg, -g)
            except np.linalg.LinAlgError:
                # Fallback to gradient direction
                delta_x = -g

            # Armijo line search
            step_size = 1.0
            if self.use_line_search:
                c1 = 1e-4
                for _ in range(15):
                    x_candidate = x + step_size * delta_x
                    if value_fn(x_candidate) <= val + c1 * step_size * float(g.T @ delta_x):
                        break
                    step_size *= 0.5

            x = x + step_size * delta_x

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return OptimizerResult(
            optimizer_name="Newton's Method",
            x_final=x,
            f_final=value_fn(x),
            iterations=len(history_loss),
            converged=converged,
            history_loss=history_loss,
            history_grad_norm=history_grad_norm,
            execution_time_ms=elapsed_ms,
            final_grad_norm=float(np.linalg.norm(grad_fn(x))),
            status_message="Converged" if converged else "Max iterations reached"
        )


class GaussNewtonMethod:
    r"""
    Gauss-Newton Method for Non-Linear Least Squares:
        Objective: f(x) = 0.5 * ||r(x)||_2^2
        Residuals: r(x) \in R^N
        Jacobian: J(x) = dr / dx \in R^{N x d}
        Gradient: grad(x) = J(x)^T * r(x)
        Gauss-Newton Approximation: H \approx J(x)^T * J(x)
        Step: (J^T J + lambda * I) * delta_x = - J^T r
    Key property: Discards the second-order derivative term sum_i r_i * d^2 r_i,
    providing quadratic convergence near zero-residual solutions without computing second derivatives!
    """

    def __init__(
        self,
        damping: float = 1e-4,
        max_iters: int = 100,
        tol: float = 1e-7,
        use_line_search: bool = True
    ):
        self.damping = damping
        self.max_iters = max_iters
        self.tol = tol
        self.use_line_search = use_line_search

    def minimize(
        self,
        residual_fn: Callable[[np.ndarray], np.ndarray],
        jacobian_fn: Callable[[np.ndarray], np.ndarray],
        x_init: np.ndarray
    ) -> OptimizerResult:
        x = np.array(x_init, dtype=np.float64, copy=True)
        dim = len(x)
        history_loss = []
        history_grad_norm = []
        converged = False

        def value_fn(x_eval: np.ndarray) -> float:
            r = residual_fn(x_eval)
            return float(0.5 * np.sum(r**2))

        t0 = time.perf_counter()
        for it in range(self.max_iters):
            r = residual_fn(x)
            val = float(0.5 * np.sum(r**2))
            J = jacobian_fn(x)
            g = J.T @ r
            gnorm = float(np.linalg.norm(g))

            history_loss.append(val)
            history_grad_norm.append(gnorm)

            if gnorm < self.tol:
                converged = True
                break

            # Approximate Hessian: J^T J
            H_gn = J.T @ J
            H_reg = H_gn + self.damping * np.eye(dim)

            try:
                delta_x = np.linalg.solve(H_reg, -g)
            except np.linalg.LinAlgError:
                delta_x = -g

            # Armijo line search
            step_size = 1.0
            if self.use_line_search:
                c1 = 1e-4
                for _ in range(15):
                    x_candidate = x + step_size * delta_x
                    if value_fn(x_candidate) <= val + c1 * step_size * float(g.T @ delta_x):
                        break
                    step_size *= 0.5

            x = x + step_size * delta_x

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        final_g = jacobian_fn(x).T @ residual_fn(x)
        return OptimizerResult(
            optimizer_name="Gauss-Newton Method",
            x_final=x,
            f_final=value_fn(x),
            iterations=len(history_loss),
            converged=converged,
            history_loss=history_loss,
            history_grad_norm=history_grad_norm,
            execution_time_ms=elapsed_ms,
            final_grad_norm=float(np.linalg.norm(final_g)),
            status_message="Converged" if converged else "Max iterations reached"
        )
