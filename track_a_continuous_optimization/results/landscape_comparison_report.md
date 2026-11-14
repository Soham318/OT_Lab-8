# Empirical Landscape Comparison Report

> **Track A**: Continuous Optimization | **Assignment 8**

### Benchmark Results Summary Table

| Landscape | Optimizer | Initial Loss | Final Loss | Iterations | Converged | Final Grad Norm | Runtime (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Convex Quadratic** | Batch GD | 88.7637 | -2.140573 | 286 | Yes | 1e-06 | 2.92 |
| **Convex Quadratic** | SGD | 88.7637 | -2.140548 | 500 | No | 0.011736 | 9.15 |
| **Convex Quadratic** | Mini-Batch GD | 88.7637 | -2.140566 | 500 | No | 0.007628 | 7.55 |
| **Convex Quadratic** | Momentum | 88.7637 | -2.140573 | 323 | Yes | 1e-06 | 4.29 |
| **Convex Quadratic** | NAG | 88.7637 | -2.140573 | 166 | Yes | 1e-06 | 2.32 |
| **Convex Quadratic** | AdaGrad | 88.7637 | -2.09035 | 500 | No | 0.320155 | 9.05 |
| **Convex Quadratic** | RMSProp | 88.7637 | -2.139921 | 500 | No | 0.094271 | 9.35 |
| **Convex Quadratic** | Adam | 88.7637 | -2.140572 | 500 | No | 0.000594 | 10.75 |
| **Convex Quadratic** | Newton's Method | 88.7637 | -2.140573 | 3 | Yes | 0.0 | 0.21 |
| **Strongly Convex** | Batch GD | 71.1528 | -0.891778 | 93 | Yes | 1e-06 | 0.71 |
| **Strongly Convex** | SGD | 71.1528 | -0.89176 | 500 | No | 0.011672 | 9.55 |
| **Strongly Convex** | Mini-Batch GD | 71.1528 | -0.891773 | 500 | No | 0.006802 | 5.91 |
| **Strongly Convex** | Momentum | 71.1528 | -0.891778 | 302 | Yes | 1e-06 | 2.53 |
| **Strongly Convex** | NAG | 71.1528 | -0.891778 | 101 | Yes | 1e-06 | 1.09 |
| **Strongly Convex** | AdaGrad | 71.1528 | -0.891777 | 500 | No | 0.003281 | 4.96 |
| **Strongly Convex** | RMSProp | 71.1528 | -0.891355 | 500 | No | 0.06916 | 6.29 |
| **Strongly Convex** | Adam | 71.1528 | -0.891778 | 327 | Yes | 1e-06 | 6.21 |
| **Strongly Convex** | Newton's Method | 71.1528 | -0.891778 | 3 | Yes | 0.0 | 0.15 |
| **Rastrigin (Multimodal)** | Batch GD | 52.5 | 35.444592 | 500 | No | 92.561188 | 8.74 |
| **Rastrigin (Multimodal)** | SGD | 52.5 | 39.842462 | 500 | No | 70.244995 | 20.14 |
| **Rastrigin (Multimodal)** | Mini-Batch GD | 52.5 | 13.114455 | 500 | No | 51.511007 | 12.25 |
| **Rastrigin (Multimodal)** | Momentum | 52.5 | 122.161718 | 500 | No | 108.663499 | 8.37 |
| **Rastrigin (Multimodal)** | NAG | 52.5 | 462.502543 | 500 | No | 11.433817 | 19.56 |
| **Rastrigin (Multimodal)** | AdaGrad | 52.5 | 7.959662 | 9 | Yes | 0.0 | 0.16 |
| **Rastrigin (Multimodal)** | RMSProp | 52.5 | 7.959662 | 77 | Yes | 0.0 | 3.78 |
| **Rastrigin (Multimodal)** | Adam | 52.5 | 7.959662 | 319 | Yes | 0.0 | 17.73 |
| **Rastrigin (Multimodal)** | Newton's Method | 52.5 | 31.838488 | 6 | Yes | 0.0 | 0.53 |
| **Rosenbrock (Valley)** | Batch GD | 24.2 | 0.070695 | 1000 | No | 0.298944 | 9.9 |
| **Rosenbrock (Valley)** | SGD | 24.2 | 0.261933 | 1000 | No | 0.731057 | 10.84 |
| **Rosenbrock (Valley)** | Mini-Batch GD | 24.2 | 0.071054 | 1000 | No | 0.299903 | 7.19 |
| **Rosenbrock (Valley)** | Momentum | 24.2 | 0.0 | 1000 | No | 0.000119 | 4.9 |
| **Rosenbrock (Valley)** | NAG | 24.2 | 0.183834 | 1000 | No | 0.563818 | 6.87 |
| **Rosenbrock (Valley)** | AdaGrad | 24.2 | 3.2072 | 1000 | No | 2.089586 | 7.22 |
| **Rosenbrock (Valley)** | RMSProp | 24.2 | 2.375804 | 1000 | No | 2.785358 | 13.06 |
| **Rosenbrock (Valley)** | Adam | 24.2 | 3.137951 | 1000 | No | 2.112201 | 20.26 |
| **Rosenbrock (Valley)** | Newton's Method | 24.2 | 0.0 | 22 | Yes | 0.0 | 0.75 |
| **Non-Linear Least Squares** | Gauss-Newton | 7.6338 | 0.001948 | 6 | Yes | 0.0 | 0.47 |
| **Non-Linear Least Squares** | Adam (1st Order Baseline) | 7.6338 | 0.001949 | 200 | No | 0.000616 | 6.3 |
