r"""GradNorm Module for Dynamic Task Balancing in Multi-Task Learning.

Implements GradNorm (Chen et al., ICML 2018):
Balances gradient norms of shared network parameters across heterogeneous tasks
to equalize effective learning paces:
    L_{total}(t) = \sum_{i=1}^T w_i(t) L_i(t)

GradNorm updates task weights w_i(t) by matching gradient norms G_W^{(i)}(t)
to target norms \bar{G}_W(t) [r_i(t)]^\alpha:
    L_{grad}(w) = \sum_{i=1}^T | G_W^{(i)}(t) - \bar{G}_W(t) [r_i(t)]^\alpha |
"""

from typing import Any, Dict, List, Tuple
import numpy as np


class MultiTaskNetwork:
    """Two-task neural network with shared representation and task-specific heads.

    Architecture:
        x -> [W_shared, b_shared] -> ReLU -> h
        h -> [W_1, b_1] -> y1_hat
        h -> [W_2, b_2] -> y2_hat
    """

    def __init__(
        self,
        in_dim: int = 10,
        hidden_dim: int = 16,
        out_dim1: int = 1,
        out_dim2: int = 1,
        seed: int = 42,
    ):
        self.in_dim = in_dim
        self.hidden_dim = hidden_dim
        self.out_dim1 = out_dim1
        self.out_dim2 = out_dim2

        rng = np.random.default_rng(seed)
        # Shared layer
        self.W_shared = rng.normal(0.0, 0.2, size=(in_dim, hidden_dim))
        self.b_shared = np.zeros(hidden_dim)

        # Head 1
        self.W1 = rng.normal(0.0, 0.2, size=(hidden_dim, out_dim1))
        self.b1 = np.zeros(out_dim1)

        # Head 2
        self.W2 = rng.normal(0.0, 0.2, size=(hidden_dim, out_dim2))
        self.b2 = np.zeros(out_dim2)

    def forward(
        self, X: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Forward pass.

        Returns:
            (h, h_preact, y1_pred, y2_pred)
        """
        h_preact = X @ self.W_shared + self.b_shared
        h = np.maximum(0.0, h_preact)  # ReLU
        y1_pred = h @ self.W1 + self.b1
        y2_pred = h @ self.W2 + self.b2
        return h, h_preact, y1_pred, y2_pred

    def compute_task_losses_and_shared_grads(
        self, X: np.ndarray, y1: np.ndarray, y2: np.ndarray
    ) -> Tuple[float, float, np.ndarray, np.ndarray, Dict[str, np.ndarray]]:
        """Compute MSE loss for each task and exact analytical gradients.

        Returns:
            (L1, L2, grad_W_shared_task1, grad_W_shared_task2, head_grads)
        """
        n_samples = len(X)
        h_preact = X @ self.W_shared + self.b_shared
        h = np.maximum(0.0, h_preact)
        y1_pred = h @ self.W1 + self.b1
        y2_pred = h @ self.W2 + self.b2

        # Task 1 MSE loss and gradients
        diff1 = y1_pred - y1
        L1 = float(0.5 * np.mean(diff1 ** 2))
        grad_out1 = diff1 / n_samples
        grad_W1 = h.T @ grad_out1
        grad_b1 = np.sum(grad_out1, axis=0)

        dh1 = grad_out1 @ self.W1.T
        dh1_preact = dh1 * (h_preact > 0.0)
        grad_W_shared_1 = X.T @ dh1_preact
        grad_b_shared_1 = np.sum(dh1_preact, axis=0)

        # Task 2 MSE loss and gradients
        diff2 = y2_pred - y2
        L2 = float(0.5 * np.mean(diff2 ** 2))
        grad_out2 = diff2 / n_samples
        grad_W2 = h.T @ grad_out2
        grad_b2 = np.sum(grad_out2, axis=0)

        dh2 = grad_out2 @ self.W2.T
        dh2_preact = dh2 * (h_preact > 0.0)
        grad_W_shared_2 = X.T @ dh2_preact
        grad_b_shared_2 = np.sum(dh2_preact, axis=0)

        head_grads = {
            "grad_W1": grad_W1,
            "grad_b1": grad_b1,
            "grad_W2": grad_W2,
            "grad_b2": grad_b2,
            "grad_b_shared_1": grad_b_shared_1,
            "grad_b_shared_2": grad_b_shared_2,
        }

        return L1, L2, grad_W_shared_1, grad_W_shared_2, head_grads

    def apply_gradients(
        self,
        grad_W_shared: np.ndarray,
        grad_b_shared: np.ndarray,
        head_grads: Dict[str, np.ndarray],
        lr: float,
    ) -> None:
        """Apply gradient update to shared layers and heads."""
        self.W_shared -= lr * grad_W_shared
        self.b_shared -= lr * grad_b_shared
        self.W1 -= lr * head_grads["grad_W1"]
        self.b1 -= lr * head_grads["grad_b1"]
        self.W2 -= lr * head_grads["grad_W2"]
        self.b2 -= lr * head_grads["grad_b2"]


class GradNormSimulator:
    """Simulator comparing GradNorm dynamic weight adaptation against fixed uniform weights."""

    def __init__(
        self,
        in_dim: int = 10,
        hidden_dim: int = 16,
        alpha: float = 1.5,
        lr_model: float = 0.02,
        lr_grad: float = 0.02,
        seed: int = 42,
    ):
        self.in_dim = in_dim
        self.hidden_dim = hidden_dim
        self.alpha = alpha
        self.lr_model = lr_model
        self.lr_grad = lr_grad
        self.seed = seed

    def generate_synthetic_data(
        self, n_samples: int = 500
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate inputs and two synthetic tasks with distinct scales and non-linearities."""
        rng = np.random.default_rng(self.seed)
        X = rng.standard_normal((n_samples, self.in_dim))

        # Task 1: linear combination with moderate noise
        y1 = np.sum(X[:, :5], axis=1, keepdims=True) + rng.normal(0, 0.1, size=(n_samples, 1))

        # Task 2: quadratic non-linear combination with higher variance (harder task)
        y2 = np.sum(X[:, 5:] ** 2, axis=1, keepdims=True) + rng.normal(0, 0.2, size=(n_samples, 1))

        return X, y1, y2

    def run_training(
        self,
        X: np.ndarray,
        y1: np.ndarray,
        y2: np.ndarray,
        num_epochs: int = 150,
        use_gradnorm: bool = True,
    ) -> Dict[str, Any]:
        """Run multi-task training using either GradNorm or Fixed Uniform weights."""
        model = MultiTaskNetwork(self.in_dim, self.hidden_dim, seed=self.seed)

        # Initial weights: T=2 tasks, sum(w) = 2.0
        weights = np.array([1.0, 1.0], dtype=float)

        # Record initial loss for relative inverse training rate calculation
        init_L1, init_L2, _, _, _ = model.compute_task_losses_and_shared_grads(X, y1, y2)
        L_initial = np.array([init_L1, init_L2], dtype=float)

        history_L1 = []
        history_L2 = []
        history_w1 = []
        history_w2 = []
        history_gradnorm_diff = []

        for epoch in range(num_epochs):
            L1, L2, gW1, gW2, head_grads = model.compute_task_losses_and_shared_grads(X, y1, y2)
            losses = np.array([L1, L2], dtype=float)

            history_L1.append(L1)
            history_L2.append(L2)
            history_w1.append(float(weights[0]))
            history_w2.append(float(weights[1]))

            # Unweighted gradient norms of shared layer W_shared
            norm1 = float(np.linalg.norm(gW1))
            norm2 = float(np.linalg.norm(gW2))
            unweighted_norms = np.array([norm1, norm2], dtype=float)

            # Weighted gradient norms: G_W^{(i)} = w_i * ||grad_W L_i||
            G_W = weights * unweighted_norms
            mean_G_W = float(np.mean(G_W))

            if use_gradnorm and epoch > 0:
                # Relative inverse training rate
                loss_ratios = losses / np.maximum(L_initial, 1e-12)
                mean_loss_ratio = float(np.mean(loss_ratios))
                r = loss_ratios / max(mean_loss_ratio, 1e-12)

                # Target gradient norm: G_target^{(i)} = mean_G * (r_i)^alpha
                target_G = mean_G_W * (r ** self.alpha)

                # Gradient of L_grad = sum |G_W^{(i)} - target_G^{(i)}| wrt w_i
                # dL_grad / dw_i = sign(G_W^{(i)} - target_G^{(i)}) * ||grad_W L_i||
                diff = G_W - target_G
                history_gradnorm_diff.append(float(np.sum(np.abs(diff))))
                d_weights = np.sign(diff) * unweighted_norms

                # Update weights
                weights -= self.lr_grad * d_weights
                # Ensure strictly positive
                weights = np.maximum(weights, 0.01)
                # Renormalize to sum(w) = T = 2.0
                weights = 2.0 * (weights / np.sum(weights))
            else:
                history_gradnorm_diff.append(0.0)

            # Combined weighted gradient update for model parameters
            total_grad_W_shared = weights[0] * gW1 + weights[1] * gW2
            total_grad_b_shared = (
                weights[0] * head_grads["grad_b_shared_1"]
                + weights[1] * head_grads["grad_b_shared_2"]
            )

            # Scale head gradients by their respective task weights
            scaled_heads = {
                "grad_W1": weights[0] * head_grads["grad_W1"],
                "grad_b1": weights[0] * head_grads["grad_b1"],
                "grad_W2": weights[1] * head_grads["grad_W2"],
                "grad_b2": weights[1] * head_grads["grad_b2"],
            }

            model.apply_gradients(total_grad_W_shared, total_grad_b_shared, scaled_heads, self.lr_model)

        final_L1, final_L2, _, _, _ = model.compute_task_losses_and_shared_grads(X, y1, y2)

        return {
            "mode": "gradnorm" if use_gradnorm else "fixed_equal_weights",
            "history_L1": history_L1,
            "history_L2": history_L2,
            "history_w1": history_w1,
            "history_w2": history_w2,
            "history_gradnorm_diff": history_gradnorm_diff,
            "final_L1": final_L1,
            "final_L2": final_L2,
            "final_total_loss": final_L1 + final_L2,
            "final_weights": weights.tolist(),
        }
