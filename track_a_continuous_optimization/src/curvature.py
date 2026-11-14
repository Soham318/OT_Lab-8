"""
Curvature Approximations and Second-Order Acceleration
Track A: Continuous Optimization
Assignment 8 - Optimize Anything

Implements and numerically evaluates:
  1. Fisher Information Matrix (Empirical Fisher vs True Hessian of NLL)
  2. Diagonal and Low-Rank Curvature Approximations (Diagonal Hessian & BFGS secant updates)
  3. Hessian-Vector Products (HVP) via Pearlmutter's finite-difference directional derivative
"""

from typing import Callable, Dict, Tuple
import numpy as np


class CurvatureApproximations:
    """
    Theoretical and practical numerical approximations to the Hessian matrix.
    """

    @staticmethod
    def empirical_fisher_matrix(
        X: np.ndarray,
        y: np.ndarray,
        theta: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Computes the Empirical Fisher Information Matrix for Binary Logistic Regression:
            P(y = 1 | x; theta) = sigma(x^T theta)
        Per-sample log-likelihood gradient:
            g_i = (y_i - sigma(x_i^T theta)) * x_i
        Empirical Fisher:
            F_emp = (1/N) * sum_{i=1}^N g_i * g_i^T
        True Hessian of Negative Log-Likelihood (NLL):
            H_true = (1/N) * sum_{i=1}^N p_i * (1 - p_i) * x_i * x_i^T

        Returns:
            F_emp: Empirical Fisher Matrix (d x d)
            H_true: True Hessian Matrix (d x d)
            spectral_diff: ||F_emp - H_true||_2
        """
        N, d = X.shape
        logits = X @ theta
        p = 1.0 / (1.0 + np.exp(-np.clip(logits, -25.0, 25.0)))

        # Per-sample gradients
        g_samples = (y - p)[:, np.newaxis] * X  # (N, d)
        F_emp = (g_samples.T @ g_samples) / N

        # True Hessian of NLL
        weights = p * (1.0 - p)  # (N,)
        H_true = (X.T @ (weights[:, np.newaxis] * X)) / N

        spectral_diff = float(np.linalg.norm(F_emp - H_true, ord=2))
        return F_emp, H_true, spectral_diff

    @staticmethod
    def diagonal_hessian_approximation(H: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Extracts diagonal curvature: D = diag(diag(H)).
        Storage: O(d) instead of O(d^2).
        Inversion cost: O(d) instead of O(d^3).
        Returns D and the Frobenius approximation error ||H - D||_F / ||H||_F.
        """
        diag_elements = np.diag(H)
        D = np.diag(diag_elements)
        rel_error = float(np.linalg.norm(H - D, ord="fro") / (np.linalg.norm(H, ord="fro") + 1e-12))
        return D, rel_error

    @staticmethod
    def bfgs_low_rank_update(
        B_k: np.ndarray,
        s_k: np.ndarray,
        y_k: np.ndarray
    ) -> np.ndarray:
        """
        BFGS Rank-2 Secant Hessian Approximation Update:
            B_{k+1} = B_k - (B_k s_k s_k^T B_k) / (s_k^T B_k s_k) + (y_k y_k^T) / (y_k^T s_k)
        Where:
            s_k = x_{k+1} - x_k (step vector)
            y_k = grad_{k+1} - grad_k (gradient change vector)
        Maintains positive-definiteness if y_k^T s_k > 0 (curvature condition).
        """
        ys = float(y_k @ s_k)
        if ys <= 1e-10:
            # Skip update if curvature condition is not satisfied
            return B_k

        Bs = B_k @ s_k
        sBs = float(s_k @ Bs)
        if sBs <= 1e-10:
            return B_k

        term1 = np.outer(Bs, Bs) / sBs
        term2 = np.outer(y_k, y_k) / ys
        return B_k - term1 + term2

    @staticmethod
    def hessian_vector_product(
        grad_fn: Callable[[np.ndarray], np.ndarray],
        x: np.ndarray,
        v: np.ndarray,
        eps: float = 1e-5
    ) -> np.ndarray:
        """
        Pearlmutter's finite-difference Hessian-Vector Product (HVP):
            H v = lim_{eps -> 0} (grad(x + eps * v) - grad(x - eps * v)) / (2 * eps)
        Computes the exact directional curvature without ever forming or storing
        the full d x d Hessian matrix!
        Memory complexity: O(d) instead of O(d^2).
        """
        v_norm = np.linalg.norm(v)
        if v_norm == 0:
            return np.zeros_like(x)

        # Scale eps adaptively
        h = eps * max(1.0, float(np.linalg.norm(x))) / v_norm
        g_plus = grad_fn(x + h * v)
        g_minus = grad_fn(x - h * v)
        return (g_plus - g_minus) / (2.0 * h)

