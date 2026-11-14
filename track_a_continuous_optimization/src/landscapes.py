"""
Optimization Objective Functions and Landscapes
Track A: Continuous Optimization
Assignment 8 - Optimize Anything

Provides:
  1. Convex Quadratic Function (ill-conditioned, controllable condition number)
  2. Strongly Convex Regularized Quadratic Function
  3. Non-Convex Functions:
     - Rastrigin Function (highly multimodal with dense local minima)
     - Rosenbrock Function (ill-conditioned banana valley)
     - Saddle Point Function (hyperbolic paraboloid with indefinite Hessian)
  4. Non-Linear Least Squares Problem (with analytical residuals & Jacobian for Gauss-Newton)
"""

from dataclasses import dataclass
from typing import Callable, Optional, Tuple
import numpy as np


class ConvexQuadratic:
    """
    Convex Quadratic Landscape:
        f(x) = 0.5 * x^T A x - b^T x
    Gradient:
        grad(x) = A x - b
    Hessian:
        H(x) = A
    """

    def __init__(self, dim: int = 10, condition_number: float = 10.0, seed: int = 42):
        self.dim = dim
        self.condition_number = condition_number
        rng = np.random.RandomState(seed)

        # Generate orthogonal Q
        H_rand = rng.randn(dim, dim)
        Q, _ = np.linalg.qr(H_rand)

        # Eigenvalues linearly spaced between 1.0 and condition_number
        eigenvals = np.linspace(1.0, condition_number, dim)
        self.A = Q @ np.diag(eigenvals) @ Q.T
        # Symmetrize
        self.A = 0.5 * (self.A + self.A.T)

        self.b = rng.randn(dim)
        self.x_opt = np.linalg.solve(self.A, self.b)
        self.f_opt = 0.5 * self.x_opt.T @ self.A @ self.x_opt - self.b.T @ self.x_opt

    def value(self, x: np.ndarray) -> float:
        return float(0.5 * x.T @ self.A @ x - self.b.T @ x)

    def gradient(self, x: np.ndarray) -> np.ndarray:
        return self.A @ x - self.b

    def hessian(self, x: np.ndarray) -> np.ndarray:
        return self.A


class StronglyConvexQuadratic:
    """
    Strongly Convex Quadratic Landscape:
        f(x) = 0.5 * x^T A x - b^T x + 0.5 * mu * ||x||_2^2
    Strong convexity parameter: mu + min_eig(A)
    """

    def __init__(self, dim: int = 10, mu: float = 2.0, condition_number: float = 5.0, seed: int = 42):
        self.dim = dim
        self.mu = mu
        base = ConvexQuadratic(dim=dim, condition_number=condition_number, seed=seed)
        self.A = base.A + mu * np.eye(dim)
        self.b = base.b
        self.x_opt = np.linalg.solve(self.A, self.b)
        self.f_opt = 0.5 * self.x_opt.T @ self.A @ self.x_opt - self.b.T @ self.x_opt

    def value(self, x: np.ndarray) -> float:
        return float(0.5 * x.T @ self.A @ x - self.b.T @ x)

    def gradient(self, x: np.ndarray) -> np.ndarray:
        return self.A @ x - self.b

    def hessian(self, x: np.ndarray) -> np.ndarray:
        return self.A


class RastriginNonConvex:
    """
    Rastrigin Multimodal Non-Convex Benchmark:
        f(x) = 10 * d + sum_{i=1}^d (x_i^2 - 10 * cos(2 * pi * x_i))
    Global Minimum: x* = [0, ..., 0]^T with f(x*) = 0.
    Dense grid of local minima surrounding the global basin.
    """

    def __init__(self, dim: int = 2):
        self.dim = dim
        self.x_opt = np.zeros(dim)
        self.f_opt = 0.0

    def value(self, x: np.ndarray) -> float:
        return float(10.0 * self.dim + np.sum(x**2 - 10.0 * np.cos(2.0 * np.pi * x)))

    def gradient(self, x: np.ndarray) -> np.ndarray:
        return 2.0 * x + 20.0 * np.pi * np.sin(2.0 * np.pi * x)

    def hessian(self, x: np.ndarray) -> np.ndarray:
        diag = 2.0 + 40.0 * (np.pi**2) * np.cos(2.0 * np.pi * x)
        return np.diag(diag)


class RosenbrockNonConvex:
    """
    Rosenbrock Non-Convex Curved Valley:
        f(x, y) = (1 - x)^2 + 100 * (y - x^2)^2
    Global Minimum: x* = [1, 1]^T, f(x*) = 0.
    """

    def __init__(self):
        self.dim = 2
        self.x_opt = np.array([1.0, 1.0])
        self.f_opt = 0.0

    def value(self, x: np.ndarray) -> float:
        x0, x1 = x[0], x[1]
        return float((1.0 - x0)**2 + 100.0 * (x1 - x0**2)**2)

    def gradient(self, x: np.ndarray) -> np.ndarray:
        x0, x1 = x[0], x[1]
        g0 = -2.0 * (1.0 - x0) - 400.0 * x0 * (x1 - x0**2)
        g1 = 200.0 * (x1 - x0**2)
        return np.array([g0, g1])

    def hessian(self, x: np.ndarray) -> np.ndarray:
        x0, x1 = x[0], x[1]
        h00 = 2.0 - 400.0 * x1 + 1200.0 * x0**2
        h01 = -400.0 * x0
        h10 = -400.0 * x0
        h11 = 200.0
        return np.array([[h00, h01], [h10, h11]])


class SaddlePointLandscape:
    """
    Saddle Point (Hyperbolic Paraboloid):
        f(x_1, x_2) = x_1^2 - x_2^2
    Stationary point: (0, 0), where gradient is 0, but Hessian has eigenvalues +2 and -2.
    """

    def __init__(self):
        self.dim = 2
        self.x_opt = np.array([0.0, 0.0])
        self.f_opt = 0.0

    def value(self, x: np.ndarray) -> float:
        return float(x[0]**2 - x[1]**2)

    def gradient(self, x: np.ndarray) -> np.ndarray:
        return np.array([2.0 * x[0], -2.0 * x[1]])

    def hessian(self, x: np.ndarray) -> np.ndarray:
        return np.array([[2.0, 0.0], [0.0, -2.0]])


class NonLinearLeastSquaresProblem:
    """
    Non-Linear Least Squares fitting problem:
        Model: y_i = a * exp(-b * t_i) + c
        Residuals: r_i(x) = model(t_i; x) - y_i,  where x = [a, b, c]^T
        Objective: f(x) = 0.5 * sum r_i(x)^2 = 0.5 * ||r(x)||_2^2
    Jacobian:
        J_{i0} = exp(-b * t_i)
        J_{i1} = -a * t_i * exp(-b * t_i)
        J_{i2} = 1.0
    Gradient:
        grad(x) = J(x)^T r(x)
    Gauss-Newton Curvature:
        H_GN = J(x)^T J(x)
    """

    def __init__(self, num_points: int = 50, noise_std: float = 0.02, seed: int = 42):
        self.dim = 3
        rng = np.random.RandomState(seed)
        self.t = np.linspace(0.0, 2.0, num_points)
        self.true_params = np.array([2.5, 1.2, 0.5])
        # Generate synthetic noisy observations
        clean_y = self.true_params[0] * np.exp(-self.true_params[1] * self.t) + self.true_params[2]
        self.y = clean_y + rng.normal(0.0, noise_std, size=num_points)

    def residuals(self, x: np.ndarray) -> np.ndarray:
        a, b, c = x[0], x[1], x[2]
        model_pred = a * np.exp(-b * self.t) + c
        return model_pred - self.y

    def jacobian(self, x: np.ndarray) -> np.ndarray:
        a, b, c = x[0], x[1], x[2]
        N = len(self.t)
        J = np.zeros((N, 3))
        exp_bt = np.exp(-b * self.t)
        J[:, 0] = exp_bt
        J[:, 1] = -a * self.t * exp_bt
        J[:, 2] = 1.0
        return J

    def value(self, x: np.ndarray) -> float:
        r = self.residuals(x)
        return float(0.5 * np.sum(r**2))

    def gradient(self, x: np.ndarray) -> np.ndarray:
        r = self.residuals(x)
        J = self.jacobian(x)
        return J.T @ r

    def gauss_newton_hessian(self, x: np.ndarray) -> np.ndarray:
        J = self.jacobian(x)
        return J.T @ J

