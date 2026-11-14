r"""Experiment 4: Federated Averaging (FedAvg) Distributed Optimization Benchmark.

Evaluates:
- Centralized Training vs FedAvg IID vs FedAvg Non-IID
- Evaluation loss and accuracy across communication rounds
- Client parameter drift / model divergence
- Inter-client communication cost volume
"""

import csv
import json
import os
import sys
from typing import Any, Dict, List
import numpy as np

# Ensure project root is on sys.path for direct script execution
sys.path.insert(0, os.path.abspath("."))

from track_d_parallel_distributed_optimization.src.fedavg import FedAvgSimulator


def run_fedavg_benchmarks() -> Dict[str, Any]:
    print("=" * 70)
    print("RUNNING EXPERIMENT 4: Federated Learning (FedAvg) Simulation")
    print("=" * 70)

    num_features = 16
    num_classes = 4
    num_clients = 5
    local_epochs = 5
    learning_rate = 0.05
    num_rounds = 25
    seed = 42

    sim = FedAvgSimulator(
        num_features=num_features,
        num_classes=num_classes,
        num_clients=num_clients,
        local_epochs=local_epochs,
        learning_rate=learning_rate,
        seed=seed,
    )

    print(f"Generating synthetic classification dataset (N=1,200, d={num_features}, classes={num_classes})...")
    X_train, y_train, X_test, y_test = sim.generate_synthetic_dataset(num_samples=1200, test_fraction=0.2)
    print(f"  Train samples: {len(y_train)} | Test samples: {len(y_test)}")

    # 1. Centralized Baseline
    print("\n--- 1. Running Centralized Training Baseline ---")
    centralized_res = sim.run_centralized(X_train, y_train, X_test, y_test, num_rounds=num_rounds)
    print(f"  Centralized Final Loss: {centralized_res['final_loss']:.4f} | Accuracy: {centralized_res['final_accuracy']:.2%}")

    # 2. FedAvg with IID Data
    print("\n--- 2. Running FedAvg with IID Partitions ---")
    iid_partitions = sim.partition_data_iid(X_train, y_train)
    fedavg_iid_res = sim.run_fedavg(
        iid_partitions, X_test, y_test, num_rounds=num_rounds, mode_label="fedavg_iid"
    )
    print(f"  FedAvg IID Final Loss:  {fedavg_iid_res['final_loss']:.4f} | Accuracy: {fedavg_iid_res['final_accuracy']:.2%}")
    print(f"  Total Data Transferred: {fedavg_iid_res['total_communication_bytes'] / 1024:.1f} KB")

    # 3. FedAvg with Non-IID Label Skew
    print("\n--- 3. Running FedAvg with Non-IID Label Skew ---")
    non_iid_partitions = sim.partition_data_non_iid(X_train, y_train)
    fedavg_non_iid_res = sim.run_fedavg(
        non_iid_partitions, X_test, y_test, num_rounds=num_rounds, mode_label="fedavg_non_iid"
    )
    print(f"  FedAvg Non-IID Loss:    {fedavg_non_iid_res['final_loss']:.4f} | Accuracy: {fedavg_non_iid_res['final_accuracy']:.2%}")
    print(f"  Final Client Drift:     {fedavg_non_iid_res['divergence_history'][-1]:.4f}")

    combined = {
        "metadata": {
            "num_features": num_features,
            "num_classes": num_classes,
            "num_clients": num_clients,
            "local_epochs": local_epochs,
            "num_rounds": num_rounds,
            "learning_rate": learning_rate,
        },
        "centralized": centralized_res,
        "fedavg_iid": fedavg_iid_res,
        "fedavg_non_iid": fedavg_non_iid_res,
    }

    os.makedirs("track_d_parallel_distributed_optimization/results", exist_ok=True)
    json_path = "track_d_parallel_distributed_optimization/results/fedavg_benchmark_results.json"
    csv_path = "track_d_parallel_distributed_optimization/results/fedavg_benchmark_summary.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Round", "CentralizedLoss", "CentralizedAcc",
            "FedAvgIIDLoss", "FedAvgIIDAcc", "FedAvgIIDDrift",
            "FedAvgNonIIDLoss", "FedAvgNonIIDAcc", "FedAvgNonIIDDrift",
        ])
        for r in range(num_rounds):
            writer.writerow([
                r + 1,
                round(centralized_res["loss_history"][r], 4),
                round(centralized_res["accuracy_history"][r], 4),
                round(fedavg_iid_res["loss_history"][r], 4),
                round(fedavg_iid_res["accuracy_history"][r], 4),
                round(fedavg_iid_res["divergence_history"][r], 4),
                round(fedavg_non_iid_res["loss_history"][r], 4),
                round(fedavg_non_iid_res["accuracy_history"][r], 4),
                round(fedavg_non_iid_res["divergence_history"][r], 4),
            ])

    print(f"\n[DONE] Saved FedAvg results to {json_path} and {csv_path}")
    return combined


if __name__ == "__main__":
    run_fedavg_benchmarks()
