"""
Continuous Gradient-Based Optimizers
Track A: Continuous Optimization
Assignment 8 - Optimize Anything

Implements:
  1. Batch Gradient Descent (GD)
  2. Stochastic Gradient Descent (SGD)
  3. Mini-Batch Gradient Descent
  4. Momentum (Polyak's Heavy Ball)
  5. Nesterov Accelerated Gradient (NAG)
  6. AdaGrad
  7. RMSProp
  8. Adam
"""

from dataclasses import dataclass, field
import time
from typing import Callable, List, Optional, Tuple
import numpy as np


@dataclass
class OptimizerResult:
    optimizer_name: str
    x_final: np.ndarray
    f_final: float
    iterations: int
    converged: bool
    history_loss: List[float] = field(default_factory=list)
    history_grad_norm: List[float] = field(default_factory=list)
    execution_time_ms: float = 0.0
    final_grad_norm: float = 0.0
    status_message: str = "Success"


class BaseOptimizer:
    """Base class for first-order gradient optimizers."""

    def __init__(
        self,
        learning_rate: float = 0.01,
        max_iters: int = 1000,
        tol: float = 1e-6,
        noise_std: float = 0.0,
        seed: int = 42
    ):
        if learning_rate <= 0:
            raise ValueError("learning_rate must be strictly positive.")
        if max_iters <= 0:
            raise ValueError("max_iters must be strictly positive.")
        if tol < 0:
            raise ValueError("tol must be non-negative.")

        self.lr = learning_rate
        self.max_iters = max_iters
        self.tol = tol
        self.noise_std = noise_std
        self.rng = np.random.RandomState(seed)

    def _noisy_gradient(self, grad_fn: Callable[[np.ndarray], np.ndarray], x: np.ndarray) -> np.ndarray:
        g = grad_fn(x)
        if self.noise_std > 0.0:
            noise = self.rng.normal(0.0, self.noise_std, size=g.shape)
            return g + noise
        return g


class BatchGradientDescent(BaseOptimizer):
    """
    Standard Batch Gradient Descent:
        x_{t+1} = x_t - eta * grad(x_t)
    """

    def minimize(
        self,
        value_fn: Callable[[np.ndarray], float],
        grad_fn: Callable[[np.ndarray], np.ndarray],
        x_init: np.ndarray
    ) -> OptimizerResult:
        x = np.array(x_init, dtype=np.float64, copy=True)
        history_loss = []
        history_grad_norm = []
        converged = False

        t0 = time.perf_counter()
        for it in range(self.max_iters):
            val = value_fn(x)
            g = self._noisy_gradient(grad_fn, x)
            gnorm = float(np.linalg.norm(g))

            history_loss.append(val)
            history_grad_norm.append(gnorm)

            if gnorm < self.tol:
                converged = True
                break

            x = x - self.lr * g

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return OptimizerResult(
            optimizer_name="Batch Gradient Descent",
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


class StochasticGradientDescent(BaseOptimizer):
    """
    Stochastic Gradient Descent (SGD):
    Applies unbiased stochastic noisy gradient estimates simulating single-sample draws.
    """

    def __init__(self, learning_rate: float = 0.01, max_iters: int = 1000, tol: float = 1e-6, noise_std: float = 0.1, seed: int = 42):
        super().__init__(learning_rate=learning_rate, max_iters=max_iters, tol=tol, noise_std=max(noise_std, 1e-4), seed=seed)

    def minimize(
        self,
        value_fn: Callable[[np.ndarray], float],
        grad_fn: Callable[[np.ndarray], np.ndarray],
        x_init: np.ndarray
    ) -> OptimizerResult:
        x = np.array(x_init, dtype=np.float64, copy=True)
        history_loss = []
        history_grad_norm = []
        converged = False

        t0 = time.perf_counter()
        for it in range(self.max_iters):
            val = value_fn(x)
            true_g = grad_fn(x)
            stoch_g = self._noisy_gradient(grad_fn, x)
            gnorm = float(np.linalg.norm(true_g))

            history_loss.append(val)
            history_grad_norm.append(gnorm)

            if gnorm < self.tol:
                converged = True
                break

            # Diminishing step size for stochastic convergence: eta_t = eta_0 / sqrt(1 + t)
            step_lr = self.lr / np.sqrt(1.0 + 0.005 * it)
            x = x - step_lr * stoch_g

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return OptimizerResult(
            optimizer_name="Stochastic Gradient Descent (SGD)",
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


class MiniBatchGradientDescent(BaseOptimizer):
    """
    Mini-Batch Gradient Descent:
    Averages gradient estimates over mini-batches of size B to reduce variance.
    """

    def __init__(self, learning_rate: float = 0.01, batch_size: int = 16, max_iters: int = 1000, tol: float = 1e-6, noise_std: float = 0.2, seed: int = 42):
        super().__init__(learning_rate=learning_rate, max_iters=max_iters, tol=tol, noise_std=noise_std, seed=seed)
        self.batch_size = max(1, batch_size)

    def minimize(
        self,
        value_fn: Callable[[np.ndarray], float],
        grad_fn: Callable[[np.ndarray], np.ndarray],
        x_init: np.ndarray
    ) -> OptimizerResult:
        x = np.array(x_init, dtype=np.float64, copy=True)
        history_loss = []
        history_grad_norm = []
        converged = False

        t0 = time.perf_counter()
        for it in range(self.max_iters):
            val = value_fn(x)
            true_g = grad_fn(x)
            gnorm = float(np.linalg.norm(true_g))

            history_loss.append(val)
            history_grad_norm.append(gnorm)

            if gnorm < self.tol:
                converged = True
                break

            # Mini-batch gradient: average of B noisy samples
            # Variance decreases as 1 / B
            batch_noise = self.rng.normal(0.0, self.noise_std / np.sqrt(self.batch_size), size=x.shape)
            batch_g = true_g + batch_noise

            x = x - self.lr * batch_g

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return OptimizerResult(
            optimizer_name="Mini-Batch Gradient Descent",
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


class MomentumOptimizer(BaseOptimizer):
    """
    Polyak's Heavy Ball Momentum:
        v_{t+1} = beta * v_t + eta * grad(x_t)
        x_{t+1} = x_t - v_{t+1}
    Dampens oscillations in narrow valleys / ill-conditioned directions.
    """

    def __init__(self, learning_rate: float = 0.01, beta: float = 0.9, max_iters: int = 1000, tol: float = 1e-6, noise_std: float = 0.0, seed: int = 42):
        super().__init__(learning_rate=learning_rate, max_iters=max_iters, tol=tol, noise_std=noise_std, seed=seed)
        self.beta = beta

    def minimize(
        self,
        value_fn: Callable[[np.ndarray], float],
        grad_fn: Callable[[np.ndarray], np.ndarray],
        x_init: np.ndarray
    ) -> OptimizerResult:
        x = np.array(x_init, dtype=np.float64, copy=True)
        v = np.zeros_like(x)
        history_loss = []
        history_grad_norm = []
        converged = False

        t0 = time.perf_counter()
        for it in range(self.max_iters):
            val = value_fn(x)
            g = self._noisy_gradient(grad_fn, x)
            gnorm = float(np.linalg.norm(g))

            history_loss.append(val)
            history_grad_norm.append(gnorm)

            if gnorm < self.tol:
                converged = True
                break

            v = self.beta * v + self.lr * g
            x = x - v

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return OptimizerResult(
            optimizer_name="Momentum",
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


class NesterovAcceleratedGradient(BaseOptimizer):
    """
    Nesterov Accelerated Gradient (NAG):
        grad_lookahead = grad(x_t - beta * v_t)
        v_{t+1} = beta * v_t + eta * grad_lookahead
        x_{t+1} = x_t - v_{t+1}
    Uses look-ahead gradient computation to anticipate momentum trajectory.
    """

    def __init__(self, learning_rate: float = 0.01, beta: float = 0.9, max_iters: int = 1000, tol: float = 1e-6, noise_std: float = 0.0, seed: int = 42):
        super().__init__(learning_rate=learning_rate, max_iters=max_iters, tol=tol, noise_std=noise_std, seed=seed)
        self.beta = beta

    def minimize(
        self,
        value_fn: Callable[[np.ndarray], float],
        grad_fn: Callable[[np.ndarray], np.ndarray],
        x_init: np.ndarray
    ) -> OptimizerResult:
        x = np.array(x_init, dtype=np.float64, copy=True)
        v = np.zeros_like(x)
        history_loss = []
        history_grad_norm = []
        converged = False

        t0 = time.perf_counter()
        for it in range(self.max_iters):
            val = value_fn(x)
            # Lookahead point
            x_lookahead = x - self.beta * v
            g_lookahead = self._noisy_gradient(grad_fn, x_lookahead)
            gnorm = float(np.linalg.norm(grad_fn(x)))

            history_loss.append(val)
            history_grad_norm.append(gnorm)

            if gnorm < self.tol:
                converged = True
                break

            v = self.beta * v + self.lr * g_lookahead
            x = x - v

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return OptimizerResult(
            optimizer_name="Nesterov Accelerated Gradient (NAG)",
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


class AdaGrad(BaseOptimizer):
    """
    AdaGrad Optimizer:
        G_{t+1} = G_t + g_t^2
        x_{t+1} = x_t - (eta / (sqrt(G_{t+1}) + eps)) * g_t
    Adapts learning rate per coordinate; highly effective on sparse features.
    """

    def __init__(self, learning_rate: float = 0.1, eps: float = 1e-8, max_iters: int = 1000, tol: float = 1e-6, noise_std: float = 0.0, seed: int = 42):
        super().__init__(learning_rate=learning_rate, max_iters=max_iters, tol=tol, noise_std=noise_std, seed=seed)
        self.eps = eps

    def minimize(
        self,
        value_fn: Callable[[np.ndarray], float],
        grad_fn: Callable[[np.ndarray], np.ndarray],
        x_init: np.ndarray
    ) -> OptimizerResult:
        x = np.array(x_init, dtype=np.float64, copy=True)
        G = np.zeros_like(x)
        history_loss = []
        history_grad_norm = []
        converged = False

        t0 = time.perf_counter()
        for it in range(self.max_iters):
            val = value_fn(x)
            g = self._noisy_gradient(grad_fn, x)
            gnorm = float(np.linalg.norm(g))

            history_loss.append(val)
            history_grad_norm.append(gnorm)

            if gnorm < self.tol:
                converged = True
                break

            G += g**2
            x = x - (self.lr / (np.sqrt(G) + self.eps)) * g

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return OptimizerResult(
            optimizer_name="AdaGrad",
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


class RMSProp(BaseOptimizer):
    """
    RMSProp Optimizer:
        v_{t+1} = rho * v_t + (1 - rho) * g_t^2
        x_{t+1} = x_t - (eta / (sqrt(v_{t+1}) + eps)) * g_t
    Solves AdaGrad's diminishing learning rate problem using exponential moving average.
    """

    def __init__(self, learning_rate: float = 0.01, rho: float = 0.9, eps: float = 1e-8, max_iters: int = 1000, tol: float = 1e-6, noise_std: float = 0.0, seed: int = 42):
        super().__init__(learning_rate=learning_rate, max_iters=max_iters, tol=tol, noise_std=noise_std, seed=seed)
        self.rho = rho
        self.eps = eps

    def minimize(
        self,
        value_fn: Callable[[np.ndarray], float],
        grad_fn: Callable[[np.ndarray], np.ndarray],
        x_init: np.ndarray
    ) -> OptimizerResult:
        x = np.array(x_init, dtype=np.float64, copy=True)
        v = np.zeros_like(x)
        history_loss = []
        history_grad_norm = []
        converged = False

        t0 = time.perf_counter()
        for it in range(self.max_iters):
            val = value_fn(x)
            g = self._noisy_gradient(grad_fn, x)
            gnorm = float(np.linalg.norm(g))

            history_loss.append(val)
            history_grad_norm.append(gnorm)

            if gnorm < self.tol:
                converged = True
                break

            v = self.rho * v + (1.0 - self.rho) * (g**2)
            x = x - (self.lr / (np.sqrt(v) + self.eps)) * g

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return OptimizerResult(
            optimizer_name="RMSProp",
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


class Adam(BaseOptimizer):
    """
    Adaptive Moment Estimation (Adam):
        m_{t+1} = beta1 * m_t + (1 - beta1) * g_t
        v_{t+1} = beta2 * v_t + (1 - beta2) * g_t^2
        m_hat = m_{t+1} / (1 - beta1^{t+1})
        v_hat = v_{t+1} / (1 - beta2^{t+1})
        x_{t+1} = x_t - (eta / (sqrt(v_hat) + eps)) * m_hat
    Combines momentum (first moment) with RMSProp (second raw moment) plus bias correction.
    """

    def __init__(
        self,
        learning_rate: float = 0.01,
        beta1: float = 0.9,
        beta2: float = 0.999,
        eps: float = 1e-8,
        max_iters: int = 1000,
        tol: float = 1e-6,
        noise_std: float = 0.0,
        seed: int = 42
    ):
        super().__init__(learning_rate=learning_rate, max_iters=max_iters, tol=tol, noise_std=noise_std, seed=seed)
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps

    def minimize(
        self,
        value_fn: Callable[[np.ndarray], float],
        grad_fn: Callable[[np.ndarray], np.ndarray],
        x_init: np.ndarray
    ) -> OptimizerResult:
        x = np.array(x_init, dtype=np.float64, copy=True)
        m = np.zeros_like(x)
        v = np.zeros_like(x)
        history_loss = []
        history_grad_norm = []
        converged = False

        t0 = time.perf_counter()
        for it in range(1, self.max_iters + 1):
            val = value_fn(x)
            g = self._noisy_gradient(grad_fn, x)
            gnorm = float(np.linalg.norm(g))

            history_loss.append(val)
            history_grad_norm.append(gnorm)

            if gnorm < self.tol:
                converged = True
                break

            m = self.beta1 * m + (1.0 - self.beta1) * g
            v = self.beta2 * v + (1.0 - self.beta2) * (g**2)

            # Bias correction
            m_hat = m / (1.0 - self.beta1**it)
            v_hat = v / (1.0 - self.beta2**it)

            x = x - (self.lr / (np.sqrt(v_hat) + self.eps)) * m_hat

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return OptimizerResult(
            optimizer_name="Adam",
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

