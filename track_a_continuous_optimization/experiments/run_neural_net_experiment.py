r"""
Neural Network Decoupled Backpropagation Experiment
Trains a 2-layer MLP on non-linear XOR data using decoupled optimizers
(Batch GD, Momentum, RMSProp, Adam) and validates analytical gradients
via finite-difference numerical gradient checking.
"""

import json
import os
import sys
from typing import Dict, List, Any
import numpy as np

from track_a_continuous_optimization.src.neural_net import TwoLayerMLP
from track_a_continuous_optimization.src.optimizers import (
    BatchGradientDescent,
    MomentumOptimizer,
    RMSProp,
    Adam
)


def run_neural_net_study() -> Dict[str, Any]:
    print("Running Track A Neural Network Decoupled Backprop Experiment...")
    
    # Non-linear XOR dataset
    X = np.array([
        [0.0, 0.0],
        [0.0, 1.0],
        [1.0, 0.0],
        [1.0, 1.0]
    ])
    y = np.array([
        [0.0],
        [1.0],
        [1.0],
        [0.0]
    ])
    
    # 1. Gradient check verification
    mlp_check = TwoLayerMLP(input_dim=2, hidden_dim=4, output_dim=1, loss_type="mse", seed=42)
    grad_error = mlp_check.check_gradients_numerical(X, y, eps=1e-5)
    print(f"  Analytical vs Numerical Finite-Difference Gradient Error: {grad_error:.2e}")
    
    # 2. Train with each optimizer
    optimizers_to_test = [
        ("Batch GD", BatchGradientDescent, 0.2, 1000),
        ("Momentum", MomentumOptimizer, 0.1, 1000),
        ("RMSProp", RMSProp, 0.02, 1000),
        ("Adam", Adam, 0.05, 1000)
    ]
    
    results: Dict[str, Any] = {
        "gradient_check_relative_error": float(grad_error),
        "training_runs": []
    }
    
    for name, opt_cls, lr, max_iters in optimizers_to_test:
        mlp = TwoLayerMLP(input_dim=2, hidden_dim=4, output_dim=1, loss_type="mse", seed=100)
        
        # Initial predictions and loss
        pred_init, _ = mlp.forward(X)
        initial_loss = mlp.compute_loss(pred_init, y)
        
        history_loss = mlp.train_with_optimizer(X, y, opt_cls, learning_rate=lr, max_iters=max_iters)
        
        pred_final, _ = mlp.forward(X)
        final_loss = mlp.compute_loss(pred_final, y)
        
        # Accuracy: round predictions to 0 or 1
        predicted_classes = (pred_final >= 0.5).astype(int)
        accuracy = float(np.mean(predicted_classes == y))
        
        print(f"  {name:10s} | Init Loss: {initial_loss:.4f} -> Final Loss: {final_loss:.6f} | Acc: {accuracy*100:.1f}%")
        
        results["training_runs"].append({
            "optimizer": name,
            "learning_rate": lr,
            "max_iters": max_iters,
            "initial_loss": float(initial_loss),
            "final_loss": float(final_loss),
            "accuracy": float(accuracy),
            "history_loss": [float(l) for l in history_loss]
        })

    # Save output
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    json_path = os.path.join(results_dir, "neural_net_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    csv_path = os.path.join(results_dir, "neural_net_summary.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("Optimizer,LearningRate,MaxIters,InitialLoss,FinalLoss,Accuracy\n")
        for r in results["training_runs"]:
            f.write(f'{r["optimizer"]},{r["learning_rate"]},{r["max_iters"]},{r["initial_loss"]:.6f},{r["final_loss"]:.6f},{r["accuracy"]*100:.1f}%\n')

    print(f"Neural net experiment completed:\n  JSON: {json_path}\n  CSV:  {csv_path}")
    return results


if __name__ == "__main__":
    run_neural_net_study()

