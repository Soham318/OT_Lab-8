r"""Multiple Gradient Descent Algorithm (MGDA) Module.

Implements MGDA (Désidéri 2012; Sener & Koltun, NeurIPS 2018) for multi-objective optimization:
    \min_{x \in \mathbb{R}^d} (f_1(x), f_2(x), ..., f_m(x))

Solves the minimum-norm problem on the convex hull of gradients:
    \min_{\alpha \in \Delta^m} \left\| \sum_{i=1}^m \alpha_i \nabla f_i(x) \right\|_2^2
    \text{subject to } \sum_{i=1}^m \alpha_i = 1, \alpha_i \ge 0

At a Pareto-stationary point x^*:
    \min_{\alpha \in \Delta^m} \left\| \sum_{i=1}^m \alpha_i \nabla f_i(x^*) \right\|_2 = 0
"""

from typing import Any, Callable, Dict, List, Tuple
import numpy as np
from scipy.optimize import minimize


class MultiObjectiveBenchmark:
    """Canonical multi-objective test functions with analytical gradients."""

    @staticmethod
    def conflicting_quadratics(x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        r"""Two conflicting convex quadratics with distinct minimizers at (-1, 0) and (+1, 0).

        f_1(x) = (x_1 - 1)^2 + x_2^2
        f_2(x) = (x_1 + 1)^2 + x_2^2

        Pareto front: x_2 = 0, -1 <= x_1 <= 1.
        """
        x1, x2 = x[0], x[1]
        f1 = (x1 - 1.0) ** 2 + x2 ** 2
        f2 = (x1 + 1.0) ** 2 + x2 ** 2

        g1 = np.array([2.0 * (x1 - 1.0), 2.0 * x2], dtype=float)
        g2 = np.array([2.0 * (x1 + 1.0), 2.0 * x2], dtype=float)

        return np.array([f1, f2]), np.vstack([g1, g2])

    @staticmethod
    def scaled_conflicting(x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        r"""Imbalanced-scale multi-objective function testing scale invariance.

        f_1(x) = 10 * x_1^2 + x_2^2
        f_2(x) = 0.1 * (x_1 - 2)^2 + (x_2 - 2)^2
        """
        x1, x2 = x[0], x[1]
        f1 = 10.0 * (x1 ** 2) + (x2 ** 2)
        f2 = 0.1 * ((x1 - 2.0) ** 2) + ((x2 - 2.0) ** 2)

        g1 = np.array([20.0 * x1, 2.0 * x2], dtype=float)
        g2 = np.array([0.2 * (x1 - 2.0), 2.0 * (x2 - 2.0)], dtype=float)

        return np.array([f1, f2]), np.vstack([g1, g2])


class MGDASolver:
    """Multiple Gradient Descent Algorithm solver for multi-objective optimization."""

    @staticmethod
    def find_min_norm_element_2d(g1: np.ndarray, g2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        r"""Analytical solution to the 2-objective min-norm problem on simplex.

        min_{\alpha in [0, 1]} ||\alpha g_1 + (1 - \alpha) g_2||^2

        Returns:
            (alpha_weights, combined_gradient)
        """
        diff = g1 - g2
        denom = float(np.dot(diff, diff))

        if denom < 1e-12:
            # Gradients are identical
            alpha = 0.5
        else:
            # Derivative of alpha^2 ||g1 - g2||^2 + 2 alpha (g1 - g2)^T g2 + ||g2||^2
            alpha = float(np.dot(g2 - g1, g2) / denom)
            alpha = max(0.0, min(1.0, alpha))

        weights = np.array([alpha, 1.0 - alpha], dtype=float)
        combined_grad = alpha * g1 + (1.0 - alpha) * g2
        return weights, combined_grad

    @staticmethod
    def find_min_norm_element_general(gradients: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        r"""Solve min-norm quadratic program on the simplex for m >= 2 objectives:
            min_{\alpha} \alpha^T (G G^T) \alpha
            s.t. \sum \alpha_i = 1, \alpha_i >= 0
        """
        m = len(gradients)
        if m == 2:
            return MGDASolver.find_min_norm_element_2d(gradients[0], gradients[1])

        # Gram matrix G G^T
        gram = gradients @ gradients.T

        def objective(alpha):
            return 0.5 * float(alpha @ gram @ alpha)

        def grad_obj(alpha):
            return gram @ alpha

        bounds = [(0.0, 1.0) for _ in range(m)]
        constraints = {"type": "eq", "fun": lambda a: np.sum(a) - 1.0, "jac": lambda a: np.ones(m)}
        init_alpha = np.full(m, 1.0 / m)

        res = minimize(
            objective,
            init_alpha,
            jac=grad_obj,
            bounds=bounds,
            constraints=constraints,
            method="SLSQP",
            options={"ftol": 1e-12, "disp": False},
        )
        alpha_opt = res.x
        combined_grad = np.sum(alpha_opt[:, None] * gradients, axis=0)
        return alpha_opt, combined_grad

    def optimize_mgda(
        self,
        objective_fn: Callable[[np.ndarray], Tuple[np.ndarray, np.ndarray]],
        initial_x: np.ndarray,
        lr: float = 0.05,
        max_iters: int = 200,
        tol: float = 1e-5,
    ) -> Dict[str, Any]:
        """Run MGDA descent until Pareto-stationarity or max iterations."""
        x = initial_x.astype(float).copy()
        trajectory = [x.copy()]
        f_history = []
        grad_norm_history = []
        alpha_history = []

        for step in range(max_iters):
            f_vals, grads = objective_fn(x)
            f_history.append(f_vals.copy())

            alphas, combined_grad = self.find_min_norm_element_general(grads)
            norm_g = float(np.linalg.norm(combined_grad))
            grad_norm_history.append(norm_g)
            alpha_history.append(alphas.copy())

            if norm_g <= tol:
                # Pareto stationary point reached
                break

            # Descent step: common descent direction is -combined_grad
            x -= lr * combined_grad
            trajectory.append(x.copy())

        final_f, _ = objective_fn(x)
        f_history.append(final_f.copy())

        return {
            "method": "MGDA",
            "final_x": x,
            "final_objectives": final_f,
            "trajectory": np.array(trajectory),
            "f_history": np.array(f_history),
            "grad_norm_history": grad_norm_history,
            "alpha_history": np.array(alpha_history),
            "iterations": len(grad_norm_history),
            "pareto_stationary": (grad_norm_history[-1] <= tol),
        }

    def optimize_weighted_sum(
        self,
        objective_fn: Callable[[np.ndarray], Tuple[np.ndarray, np.ndarray]],
        initial_x: np.ndarray,
        weights: np.ndarray,
        lr: float = 0.05,
        max_iters: int = 200,
        tol: float = 1e-5,
    ) -> Dict[str, Any]:
        """Run standard scalarized weighted-sum gradient descent: min sum lambda_i f_i(x)."""
        x = initial_x.astype(float).copy()
        trajectory = [x.copy()]
        f_history = []
        grad_norm_history = []

        norm_weights = np.asarray(weights, dtype=float) / np.sum(weights)

        for step in range(max_iters):
            f_vals, grads = objective_fn(x)
            f_history.append(f_vals.copy())

            # Scalarized gradient
            weighted_grad = np.sum(norm_weights[:, None] * grads, axis=0)
            norm_g = float(np.linalg.norm(weighted_grad))
            grad_norm_history.append(norm_g)

            if norm_g <= tol:
                break

            x -= lr * weighted_grad
            trajectory.append(x.copy())

        final_f, _ = objective_fn(x)
        f_history.append(final_f.copy())

        return {
            "method": f"WeightedSum_{norm_weights[0]:.2f}_{norm_weights[1]:.2f}",
            "weights": norm_weights,
            "final_x": x,
            "final_objectives": final_f,
            "trajectory": np.array(trajectory),
            "f_history": np.array(f_history),
            "grad_norm_history": grad_norm_history,
            "iterations": len(grad_norm_history),
        }

