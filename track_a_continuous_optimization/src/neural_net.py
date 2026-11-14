"""
Neural Network and Decoupled Backpropagation Module
Track A: Continuous Optimization
Assignment 8 - Optimize Anything

Demonstrates:
  1. Forward propagation and loss computation on a 2-layer MLP.
  2. Decoupled Analytical Backpropagation: Gradient computation is mathematically
     separated from optimizer parameter update rules.
  3. Numerical Gradient Verification: Finite-difference gradient checking validating
     analytical derivatives to within 1e-6 error tolerance.
  4. Integration with first-order optimizers (GD, Momentum, RMSProp, Adam).
"""

from typing import Dict, List, Optional, Tuple
import numpy as np


def sigmoid(z: np.ndarray) -> np.ndarray:
    """Numerically stable sigmoid activation."""
    return np.where(z >= 0, 1.0 / (1.0 + np.exp(-z)), np.exp(z) / (1.0 + np.exp(z)))


def sigmoid_derivative(a: np.ndarray) -> np.ndarray:
    """Derivative of sigmoid with respect to its output a = sigmoid(z)."""
    return a * (1.0 - a)


class TwoLayerMLP:
    """
    Two-layer Multi-Layer Perceptron (Input -> Hidden -> Output):
      z1 = X @ W1 + b1
      a1 = sigmoid(z1)
      z2 = a1 @ W2 + b2
      y_pred = sigmoid(z2) (or linear for regression)
    Loss: Binary Cross-Entropy or Mean Squared Error (MSE).
    """

    def __init__(
        self,
        input_dim: int = 2,
        hidden_dim: int = 4,
        output_dim: int = 1,
        loss_type: str = "mse",
        seed: int = 42
    ):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.loss_type = loss_type

        rng = np.random.RandomState(seed)
        # Xavier / Glorot initialization
        w1_scale = np.sqrt(2.0 / (input_dim + hidden_dim))
        w2_scale = np.sqrt(2.0 / (hidden_dim + output_dim))

        self.W1 = rng.randn(input_dim, hidden_dim) * w1_scale
        self.b1 = np.zeros((1, hidden_dim))
        self.W2 = rng.randn(hidden_dim, output_dim) * w2_scale
        self.b2 = np.zeros((1, output_dim))

    def get_params_vector(self) -> np.ndarray:
        """Flatten all parameters into a 1D vector."""
        return np.concatenate([
            self.W1.ravel(),
            self.b1.ravel(),
            self.W2.ravel(),
            self.b2.ravel()
        ])

    def set_params_vector(self, theta: np.ndarray):
        """Unflatten a 1D parameter vector into weights and biases."""
        idx = 0
        w1_size = self.input_dim * self.hidden_dim
        self.W1 = theta[idx : idx + w1_size].reshape((self.input_dim, self.hidden_dim))
        idx += w1_size

        b1_size = self.hidden_dim
        self.b1 = theta[idx : idx + b1_size].reshape((1, self.hidden_dim))
        idx += b1_size

        w2_size = self.hidden_dim * self.output_dim
        self.W2 = theta[idx : idx + w2_size].reshape((self.hidden_dim, self.output_dim))
        idx += w2_size

        b2_size = self.output_dim
        self.b2 = theta[idx : idx + b2_size].reshape((1, self.output_dim))

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Forward pass caching intermediate activations."""
        z1 = X @ self.W1 + self.b1
        a1 = sigmoid(z1)
        z2 = a1 @ self.W2 + self.b2
        y_pred = sigmoid(z2) if self.loss_type == "bce" else z2

        cache = {"X": X, "z1": z1, "a1": a1, "z2": z2, "y_pred": y_pred}
        return y_pred, cache

    def compute_loss(self, y_pred: np.ndarray, y_true: np.ndarray) -> float:
        """Compute scalar loss value."""
        N = len(y_true)
        if self.loss_type == "mse":
            return float(0.5 * np.mean((y_pred - y_true)**2))
        elif self.loss_type == "bce":
            eps = 1e-12
            p = np.clip(y_pred, eps, 1.0 - eps)
            return float(-np.mean(y_true * np.log(p) + (1.0 - y_true) * np.log(1.0 - p)))
        raise ValueError(f"Unknown loss type: {self.loss_type}")

    def backward(self, cache: Dict[str, np.ndarray], y_true: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Analytical Backpropagation:
        Computes exact partial derivatives with respect to all layer parameters.
        Notice: This function ONLY computes gradients. It does NOT update parameters.
        """
        X = cache["X"]
        a1 = cache["a1"]
        y_pred = cache["y_pred"]
        N = len(y_true)

        # Output error delta2
        if self.loss_type == "mse":
            # L = 0.5/N * ||y_pred - y_true||^2, with y_pred = z2
            delta2 = (y_pred - y_true) / N
        elif self.loss_type == "bce":
            # For BCE with sigmoid output, dL/dz2 = (y_pred - y_true) / N
            delta2 = (y_pred - y_true) / N
        else:
            raise ValueError(f"Unknown loss: {self.loss_type}")

        # Gradients for Layer 2
        dW2 = a1.T @ delta2
        db2 = np.sum(delta2, axis=0, keepdims=True)

        # Backpropagate error to hidden layer
        delta1 = (delta2 @ self.W2.T) * sigmoid_derivative(a1)

        # Gradients for Layer 1
        dW1 = X.T @ delta1
        db1 = np.sum(delta1, axis=0, keepdims=True)

        return {"W1": dW1, "b1": db1, "W2": dW2, "b2": db2}

    def get_gradients_vector(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Execute forward + backward pass and return flattened gradient vector."""
        y_pred, cache = self.forward(X)
        grads = self.backward(cache, y)
        return np.concatenate([
            grads["W1"].ravel(),
            grads["b1"].ravel(),
            grads["W2"].ravel(),
            grads["b2"].ravel()
        ])

    def check_gradients_numerical(self, X: np.ndarray, y: np.ndarray, eps: float = 1e-5) -> float:
        """
        Independent numerical gradient verification using centered finite differences:
            grad_num[i] = (Loss(theta + eps * e_i) - Loss(theta - eps * e_i)) / (2 * eps)
        Returns the relative L2 error norm:
            ||grad_analytical - grad_num|| / (||grad_analytical|| + ||grad_num||)
        """
        theta = self.get_params_vector()
        analytical_grad = self.get_gradients_vector(X, y)
        numerical_grad = np.zeros_like(theta)

        for i in range(len(theta)):
            theta_plus = np.array(theta, copy=True)
            theta_plus[i] += eps
            self.set_params_vector(theta_plus)
            y_pred_plus, _ = self.forward(X)
            loss_plus = self.compute_loss(y_pred_plus, y_pred_plus * 0 + y)

            theta_minus = np.array(theta, copy=True)
            theta_minus[i] -= eps
            self.set_params_vector(theta_minus)
            y_pred_minus, _ = self.forward(X)
            loss_minus = self.compute_loss(y_pred_minus, y_pred_minus * 0 + y)

            numerical_grad[i] = (loss_plus - loss_minus) / (2.0 * eps)

        # Restore original parameters
        self.set_params_vector(theta)

        rel_error = np.linalg.norm(analytical_grad - numerical_grad) / (
            np.linalg.norm(analytical_grad) + np.linalg.norm(numerical_grad) + 1e-12
        )
        return float(rel_error)

    def train_with_optimizer(
        self,
        X: np.ndarray,
        y: np.ndarray,
        optimizer_class,
        learning_rate: float = 0.05,
        max_iters: int = 500
    ) -> List[float]:
        """Train MLP using decoupled optimizer instance."""
        def loss_wrapper(theta_vec: np.ndarray) -> float:
            self.set_params_vector(theta_vec)
            pred, _ = self.forward(X)
            return self.compute_loss(pred, y)

        def grad_wrapper(theta_vec: np.ndarray) -> np.ndarray:
            self.set_params_vector(theta_vec)
            return self.get_gradients_vector(X, y)

        opt = optimizer_class(learning_rate=learning_rate, max_iters=max_iters)
        theta_init = self.get_params_vector()
        res = opt.minimize(loss_wrapper, grad_wrapper, theta_init)
        self.set_params_vector(res.x_final)
        return res.history_loss

