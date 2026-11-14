"""
Quantum Machine Learning vs. Classical Machine Learning Module
Track I: Quantum Algorithms and Quantum Machine Learning

Demonstration:
  Binary classification on Iris dataset (Setosa vs Versicolor, 2 normalized features).
  Compares:
    1. Classical Logistic Regression
    2. Quantum Variational Classifier (VQC) with ZZ-feature map and Parameterized Quantum Circuit (PQC)

Honest Academic Evaluation:
  - Compares accuracy, precision, recall, F1-score, and wall-clock training time.
  - Transparently highlights the computational overhead of simulating quantum circuits on classical CPUs.
  - Explains why classical simulation does not demonstrate quantum speedup or superiority.
"""

import time
from typing import Dict, Any, Tuple, List
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from scipy.optimize import minimize

from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector
from track_i_quantum_algorithms.src.utils import get_circuit_metrics, export_circuit_diagram

def prepare_iris_dataset(test_size: float = 0.3, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Load and preprocess the Iris dataset for binary classification (Class 0: Setosa vs Class 1: Versicolor).
    Uses 2 features (sepal length and petal length), normalized to [0, pi] for angle encoding.
    """
    X_raw, y_raw = load_iris(return_X_y=True)
    mask = y_raw < 2
    # Select features 0 (sepal length) and 2 (petal length)
    X = X_raw[mask][:, [0, 2]]
    y = y_raw[mask] # labels in {0, 1}

    scaler = MinMaxScaler(feature_range=(0.0, np.pi))
    X_norm = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_norm, y, test_size=test_size, random_state=random_state, stratify=y
    )
    return X_train, X_test, y_train, y_test

def build_qml_circuit_template(num_layers: int = 1) -> Tuple[QuantumCircuit, ParameterVector, ParameterVector]:
    """
    Construct the combined Feature Map + Variational Ansatz template.
    num_qubits = 2 (for 2 features).
    """
    qc = QuantumCircuit(2, name="QML_VQC")
    x_params = ParameterVector("x", 2)
    # Each layer has 4 rotation parameters (Ry, Rz on 2 qubits), plus 4 for final layer
    num_theta = 4 * (num_layers + 1)
    theta_params = ParameterVector("theta", num_theta)

    # 1. Feature Map: Angle encoding + ZZ entanglement
    qc.ry(x_params[0], 0)
    qc.ry(x_params[1], 1)
    qc.cx(0, 1)
    qc.rz(x_params[0] * x_params[1], 1)
    qc.cx(0, 1)

    qc.barrier()

    # 2. Variational PQC Ansatz
    idx = 0
    for l in range(num_layers):
        qc.ry(theta_params[idx], 0); idx += 1
        qc.ry(theta_params[idx], 1); idx += 1
        qc.rz(theta_params[idx], 0); idx += 1
        qc.rz(theta_params[idx], 1); idx += 1
        qc.cx(0, 1)

    # Final rotation layer
    qc.ry(theta_params[idx], 0); idx += 1
    qc.ry(theta_params[idx], 1); idx += 1
    qc.rz(theta_params[idx], 0); idx += 1
    qc.rz(theta_params[idx], 1); idx += 1

    return qc, x_params, theta_params

class QuantumVariationalClassifier:
    """
    Variational Quantum Classifier for 2-feature binary classification.
    Predicts expectation value <Z_0> in [-1, +1].
    Maps <Z_0> >= 0 to Class 1, <Z_0> < 0 to Class 0.
    """
    def __init__(self, num_layers: int = 1, max_iter: int = 40, seed: int = 42):
        self.num_layers = num_layers
        self.max_iter = max_iter
        self.seed = seed
        self.circuit_template, self.x_params, self.theta_params = build_qml_circuit_template(num_layers)
        self.num_weights = len(self.theta_params)
        self.weights = None
        self.eval_count = 0

    def _predict_single_sample(self, x: np.ndarray, theta: np.ndarray) -> float:
        """Evaluate expectation <Z_0> on a single 2D feature vector."""
        param_dict = {}
        param_dict[self.x_params[0]] = x[0]
        param_dict[self.x_params[1]] = x[1]
        for i in range(self.num_weights):
            param_dict[self.theta_params[i]] = theta[i]

        bound_qc = self.circuit_template.assign_parameters(param_dict)
        sv = Statevector(bound_qc)
        probs = np.abs(sv.data) ** 2
        # <Z_0> = P(q0=0) - P(q0=1)
        # In Qiskit, index 0 is |00>, index 1 is |01>, index 2 is |10>, index 3 is |11>
        # q0 corresponds to the rightmost bit: |00> has q0=0, |10> has q0=0; |01> has q0=1, |11> has q0=1.
        p_q0_zero = probs[0] + probs[2]
        p_q0_one = probs[1] + probs[3]
        return float(p_q0_zero - p_q0_one)

    def _loss_function(self, theta: np.ndarray, X: np.ndarray, y_target: np.ndarray) -> float:
        """Mean squared error loss between <Z_0> and target labels y in {-1, +1}."""
        self.eval_count += 1
        # Convert {0, 1} targets to {-1, +1}
        # Class 1 -> +1, Class 0 -> -1
        y_signed = 2.0 * y_target - 1.0
        preds = np.array([self._predict_single_sample(x, theta) for x in X])
        mse = float(np.mean((preds - y_signed) ** 2))
        return mse

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
        """Train variational weights using COBYLA optimizer."""
        rng = np.random.RandomState(self.seed)
        init_theta = rng.uniform(-np.pi, np.pi, size=self.num_weights)
        self.eval_count = 0

        t0 = time.perf_counter()
        res = minimize(
            self._loss_function,
            init_theta,
            args=(X_train, y_train),
            method="COBYLA",
            options={"maxiter": self.max_iter, "disp": False}
        )
        train_time_s = time.perf_counter() - t0
        self.weights = res.x

        return {
            "converged": res.success,
            "final_loss": round(float(res.fun), 4),
            "iterations": int(res.nfev),
            "train_time_s": round(float(train_time_s), 3),
            "circuit_evaluations": int(self.eval_count * len(X_train))
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict binary class labels in {0, 1}."""
        preds_signed = np.array([self._predict_single_sample(x, self.weights) for x in X])
        # If <Z_0> >= 0 -> Class 1, else Class 0
        return np.where(preds_signed >= 0.0, 1, 0)

def run_classical_vs_quantum_experiment() -> Dict[str, Any]:
    """
    Run side-by-side benchmark of Classical Logistic Regression vs Quantum VQC.
    """
    X_train, X_test, y_train, y_test = prepare_iris_dataset(test_size=0.3, random_state=42)

    # 1. Classical Model: Logistic Regression
    t0_c = time.perf_counter()
    clf = LogisticRegression(random_state=42)
    clf.fit(X_train, y_train)
    c_train_time = (time.perf_counter() - t0_c) * 1000.0 # ms

    c_train_preds = clf.predict(X_train)
    c_test_preds = clf.predict(X_test)

    c_metrics = {
        "model": "Classical Logistic Regression",
        "train_accuracy": float(accuracy_score(y_train, c_train_preds)),
        "test_accuracy": float(accuracy_score(y_test, c_test_preds)),
        "test_precision": float(precision_score(y_test, c_test_preds, zero_division=0)),
        "test_recall": float(recall_score(y_test, c_test_preds, zero_division=0)),
        "test_f1": float(f1_score(y_test, c_test_preds, zero_division=0)),
        "training_time_ms": round(c_train_time, 2),
        "parameters_count": int(clf.coef_.size + clf.intercept_.size)
    }

    # 2. Quantum Model: Variational Quantum Classifier (VQC)
    vqc = QuantumVariationalClassifier(num_layers=1, max_iter=35, seed=42)
    vqc_train_res = vqc.fit(X_train, y_train)

    q_train_preds = vqc.predict(X_train)
    q_test_preds = vqc.predict(X_test)

    q_circuit_metrics = get_circuit_metrics(vqc.circuit_template)
    export_circuit_diagram(vqc.circuit_template, "qml_variational_classifier")

    q_metrics = {
        "model": "Quantum Variational Classifier (VQC)",
        "train_accuracy": float(accuracy_score(y_train, q_train_preds)),
        "test_accuracy": float(accuracy_score(y_test, q_test_preds)),
        "test_precision": float(precision_score(y_test, q_test_preds, zero_division=0)),
        "test_recall": float(recall_score(y_test, q_test_preds, zero_division=0)),
        "test_f1": float(f1_score(y_test, q_test_preds, zero_division=0)),
        "training_time_s": vqc_train_res["train_time_s"],
        "training_time_ms": round(vqc_train_res["train_time_s"] * 1000.0, 2),
        "parameters_count": vqc.num_weights,
        "circuit_depth": q_circuit_metrics["depth"],
        "num_qubits": q_circuit_metrics["num_qubits"],
        "total_gates": q_circuit_metrics["total_gates"],
        "optimizer_iterations": vqc_train_res["iterations"],
        "total_circuit_evaluations": vqc_train_res["circuit_evaluations"],
        "final_train_loss": vqc_train_res["final_loss"]
    }

    return {
        "dataset": "Iris (Setosa vs. Versicolor, 2 features)",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "classical": c_metrics,
        "quantum": q_metrics,
        "comparison_analysis": (
            f"Both Classical Logistic Regression and the Quantum VQC achieved {c_metrics['test_accuracy']*100:.1f}% "
            f"and {q_metrics['test_accuracy']*100:.1f}% test accuracy on the linearly separable Iris subset. "
            f"However, the classical model trained in {c_metrics['training_time_ms']:.2f} ms, whereas simulating "
            f"the quantum circuit on CPU required {q_metrics['training_time_ms']:.2f} ms "
            f"({q_metrics['training_time_ms']/max(0.1, c_metrics['training_time_ms']):.1f}x slower). "
            f"This empirically demonstrates that classical simulation of quantum machine learning incurs substantial "
            f"computational overhead without conferring a computational advantage on small tabular datasets."
        )
    }
