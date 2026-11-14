r"""Federated Averaging (FedAvg) Simulation Module.

Implements the canonical FedAvg algorithm (McMahan et al., AISTATS 2017)
for distributed optimization across decentralized edge clients:
    \theta_{t+1} = \sum_{k=1}^K \frac{n_k}{n} \theta_{t+1}^k

Compares:
1. Centralized Training (ideal baseline with pooled data)
2. FedAvg with IID Client Partitions
3. FedAvg with Non-IID Label-Skewed Client Partitions

Tracks:
- Global evaluation loss and accuracy across communication rounds
- Client drift / parameter divergence ||\theta^k - \theta_global||
- Inter-client communication payload volume
"""

import copy
from typing import Any, Dict, List, Tuple
import numpy as np


class SoftmaxModel:
    """Multiclass Logistic / Softmax Regression Classifier."""

    def __init__(self, num_features: int, num_classes: int, seed: int = 42):
        self.num_features = num_features
        self.num_classes = num_classes
        rng = np.random.default_rng(seed)
        # Xavier/He normal initialization
        self.W = rng.normal(0.0, 0.1, size=(num_features, num_classes))
        self.b = np.zeros(num_classes)

    def get_parameters(self) -> Dict[str, np.ndarray]:
        """Return a copy of the model parameters."""
        return {"W": self.W.copy(), "b": self.b.copy()}

    def set_parameters(self, params: Dict[str, np.ndarray]) -> None:
        """Load parameter dictionary."""
        self.W = params["W"].copy()
        self.b = params["b"].copy()

    def get_flat_parameters(self) -> np.ndarray:
        """Flatten parameters into 1D vector."""
        return np.concatenate([self.W.ravel(), self.b.ravel()])

    def count_parameters(self) -> int:
        """Total number of scalar parameters."""
        return self.W.size + self.b.size

    def forward(self, X: np.ndarray) -> np.ndarray:
        """Compute softmax class probabilities."""
        logits = X @ self.W + self.b
        # Numerically stable softmax
        logits_shifted = logits - np.max(logits, axis=1, keepdims=True)
        exp_logits = np.exp(logits_shifted)
        return exp_logits / np.sum(exp_logits, axis=1, keepdims=True)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
        """Compute cross-entropy loss and classification accuracy."""
        n_samples = len(y)
        probs = self.forward(X)
        # Avoid log(0)
        eps = 1e-12
        correct_logprobs = -np.log(probs[np.arange(n_samples), y] + eps)
        loss = float(np.mean(correct_logprobs))
        preds = np.argmax(probs, axis=1)
        accuracy = float(np.mean(preds == y))
        return loss, accuracy

    def train_step(self, X: np.ndarray, y: np.ndarray, lr: float) -> float:
        """Perform one batch of gradient descent."""
        n_samples = len(y)
        probs = self.forward(X)

        # Gradient of categorical cross-entropy with softmax
        probs[np.arange(n_samples), y] -= 1.0
        grad_W = (X.T @ probs) / n_samples
        grad_b = np.sum(probs, axis=0) / n_samples

        self.W -= lr * grad_W
        self.b -= lr * grad_b
        return float(np.linalg.norm(grad_W) + np.linalg.norm(grad_b))


class FedAvgSimulator:
    """Simulator orchestrating federated learning rounds among local edge clients."""

    def __init__(
        self,
        num_features: int = 16,
        num_classes: int = 4,
        num_clients: int = 5,
        local_epochs: int = 5,
        learning_rate: float = 0.05,
        seed: int = 42,
    ):
        self.num_features = num_features
        self.num_classes = num_classes
        self.num_clients = num_clients
        self.local_epochs = local_epochs
        self.learning_rate = learning_rate
        self.seed = seed

    def generate_synthetic_dataset(
        self, num_samples: int = 1200, test_fraction: float = 0.2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Generate well-separated multi-class Gaussian clusters."""
        rng = np.random.default_rng(self.seed)
        samples_per_class = num_samples // self.num_classes

        X_list, y_list = [], []
        # Class centers in feature space
        centers = rng.normal(0.0, 2.0, size=(self.num_classes, self.num_features))

        for c in range(self.num_classes):
            X_c = rng.normal(centers[c], 1.0, size=(samples_per_class, self.num_features))
            y_c = np.full(samples_per_class, c, dtype=int)
            X_list.append(X_c)
            y_list.append(y_c)

        X = np.vstack(X_list)
        y = np.concatenate(y_list)

        # Shuffle
        perm = rng.permutation(len(y))
        X, y = X[perm], y[perm]

        split_idx = int(len(y) * (1.0 - test_fraction))
        return X[:split_idx], y[:split_idx], X[split_idx:], y[split_idx:]

    def partition_data_iid(
        self, X: np.ndarray, y: np.ndarray
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Partition data uniformly at random across all clients."""
        rng = np.random.default_rng(self.seed + 1)
        indices = rng.permutation(len(y))
        splits = np.array_split(indices, self.num_clients)
        return [(X[split], y[split]) for split in splits]

    def partition_data_non_iid(
        self, X: np.ndarray, y: np.ndarray
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Create pathological non-IID label skew.

        Each client receives primarily samples from a specific subset of classes.
        """
        rng = np.random.default_rng(self.seed + 2)
        client_data: List[List[int]] = [[] for _ in range(self.num_clients)]

        # Group indices by class
        for c in range(self.num_classes):
            c_indices = np.where(y == c)[0]
            rng.shuffle(c_indices)
            # Assign class c predominantly to (c % num_clients) and ((c + 1) % num_clients)
            primary_client = c % self.num_clients
            secondary_client = (c + 1) % self.num_clients

            n_c = len(c_indices)
            split_70 = int(0.70 * n_c)
            split_90 = int(0.90 * n_c)

            client_data[primary_client].extend(c_indices[:split_70])
            client_data[secondary_client].extend(c_indices[split_70:split_90])

            # Remainder uniformly distributed to prevent total emptiness
            remainder = c_indices[split_90:]
            rem_splits = np.array_split(remainder, self.num_clients)
            for k in range(self.num_clients):
                client_data[k].extend(rem_splits[k])

        partitions = []
        for k in range(self.num_clients):
            idx = np.array(client_data[k], dtype=int)
            rng.shuffle(idx)
            partitions.append((X[idx], y[idx]))

        return partitions

    @staticmethod
    def aggregate_parameters(
        client_parameters: List[Dict[str, np.ndarray]], client_weights: List[int]
    ) -> Dict[str, np.ndarray]:
        """Perform FedAvg weighted aggregation: theta_global = sum (n_k / n) * theta_k."""
        total_samples = sum(client_weights)
        if total_samples <= 0:
            raise ValueError("Total client samples must be positive")

        aggregated = {
            "W": np.zeros_like(client_parameters[0]["W"]),
            "b": np.zeros_like(client_parameters[0]["b"]),
        }

        for params, n_k in zip(client_parameters, client_weights):
            fraction = n_k / total_samples
            aggregated["W"] += fraction * params["W"]
            aggregated["b"] += fraction * params["b"]

        return aggregated

    def run_centralized(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        num_rounds: int = 20,
    ) -> Dict[str, Any]:
        """Centralized learning baseline on all data pooled together."""
        model = SoftmaxModel(self.num_features, self.num_classes, seed=self.seed)
        loss_history = []
        acc_history = []

        # In each round, run equivalent total gradient steps: local_epochs steps
        for round_idx in range(num_rounds):
            for _ in range(self.local_epochs):
                model.train_step(X_train, y_train, self.learning_rate)
            loss, acc = model.evaluate(X_test, y_test)
            loss_history.append(loss)
            acc_history.append(acc)

        return {
            "mode": "centralized",
            "loss_history": loss_history,
            "accuracy_history": acc_history,
            "final_loss": loss_history[-1],
            "final_accuracy": acc_history[-1],
        }

    def run_fedavg(
        self,
        client_partitions: List[Tuple[np.ndarray, np.ndarray]],
        X_test: np.ndarray,
        y_test: np.ndarray,
        num_rounds: int = 20,
        mode_label: str = "fedavg_iid",
    ) -> Dict[str, Any]:
        """Execute FedAvg communication rounds with local client training and aggregation."""
        global_model = SoftmaxModel(self.num_features, self.num_classes, seed=self.seed)
        client_sizes = [len(y_k) for _, y_k in client_partitions]

        loss_history = []
        acc_history = []
        divergence_history = []

        bytes_per_param = 8  # float64
        num_params = global_model.count_parameters()
        # Round trip: broadcast global weights + upload local weights for all clients
        bytes_per_round = 2 * self.num_clients * num_params * bytes_per_param
        total_communication_bytes = 0

        for r in range(num_rounds):
            current_global_params = global_model.get_parameters()
            updated_client_params = []
            flat_global = global_model.get_flat_parameters()
            drift_sum = 0.0

            # Local training on each client
            for k in range(self.num_clients):
                X_k, y_k = client_partitions[k]
                local_model = SoftmaxModel(self.num_features, self.num_classes, seed=self.seed)
                local_model.set_parameters(current_global_params)

                for _ in range(self.local_epochs):
                    local_model.train_step(X_k, y_k, self.learning_rate)

                updated_params = local_model.get_parameters()
                updated_client_params.append(updated_params)

                flat_local = local_model.get_flat_parameters()
                drift_sum += float(np.linalg.norm(flat_local - flat_global))

            # Server aggregation
            new_global_params = self.aggregate_parameters(updated_client_params, client_sizes)
            global_model.set_parameters(new_global_params)

            # Global evaluation
            loss, acc = global_model.evaluate(X_test, y_test)
            loss_history.append(loss)
            acc_history.append(acc)
            divergence_history.append(drift_sum / self.num_clients)
            total_communication_bytes += bytes_per_round

        return {
            "mode": mode_label,
            "loss_history": loss_history,
            "accuracy_history": acc_history,
            "divergence_history": divergence_history,
            "final_loss": loss_history[-1],
            "final_accuracy": acc_history[-1],
            "total_communication_bytes": total_communication_bytes,
            "bytes_per_round": bytes_per_round,
            "num_clients": self.num_clients,
            "num_rounds": num_rounds,
        }

