"""
Experiment Runner: Quantum Machine Learning vs. Classical Machine Learning
Track I: Quantum Algorithms and Quantum Machine Learning

Compares:
1. Classical Logistic Regression
2. Quantum Variational Classifier (VQC) with ZZ-feature map and PQC
Evaluated on Iris binary classification (Setosa vs Versicolor).
"""

import os
import json
import csv
from track_i_quantum_algorithms.src.qml_classifier import run_classical_vs_quantum_experiment

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_qml_experiment():
    print("=" * 80)
    print("RUNNING QML VS CLASSICAL ML BENCHMARK EXPERIMENT")
    print("=" * 80)

    res = run_classical_vs_quantum_experiment()

    print("\n--- Benchmark Results ---")
    c = res["classical"]
    q = res["quantum"]
    print(f"Dataset: {res['dataset']} ({res['train_samples']} train, {res['test_samples']} test)")
    print(f"Classical Logistic Regression: Acc = {c['test_accuracy']*100:.1f}%, F1 = {c['test_f1']:.4f}, Time = {c['training_time_ms']:.2f} ms")
    print(f"Quantum Variational Classifier: Acc = {q['test_accuracy']*100:.1f}%, F1 = {q['test_f1']:.4f}, Time = {q['training_time_ms']:.2f} ms")
    print(f"Circuit Depth: {q['circuit_depth']}, Qubits: {q['num_qubits']}, Gates: {q['total_gates']}, Iterations: {q['optimizer_iterations']}")
    print("\nAcademic Analysis:")
    print(res["comparison_analysis"])

    # Save to JSON
    json_path = os.path.join(RESULTS_DIR, "qml_benchmark_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, default=lambda o: int(o) if isinstance(o, (np.integer, int)) else float(o) if isinstance(o, (np.floating, float)) else str(o))
    print(f"\n[INFO] QML Results JSON saved to: {json_path}")

    # Save to CSV
    csv_path = os.path.join(RESULTS_DIR, "qml_benchmark_results.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Model", "Train_Accuracy", "Test_Accuracy", "Test_Precision", "Test_Recall", "Test_F1", "Train_Time_ms", "Parameters", "Qubits", "Circuit_Depth"])
        writer.writerow([c["model"], c["train_accuracy"], c["test_accuracy"], c["test_precision"], c["test_recall"], c["test_f1"], c["training_time_ms"], c["parameters_count"], 0, 0])
        writer.writerow([q["model"], q["train_accuracy"], q["test_accuracy"], q["test_precision"], q["test_recall"], q["test_f1"], q["training_time_ms"], q["parameters_count"], q["num_qubits"], q["circuit_depth"]])
    print(f"[INFO] QML Results CSV saved to: {csv_path}")

    return res

if __name__ == "__main__":
    run_qml_experiment()
