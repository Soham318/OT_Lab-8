# Track D: Parallel and Distributed Optimization

> **Assignment 8**: Optimize Anything — 14-Day Vibe-Coding Challenge  
> **Repository Module**: `track_d_parallel_distributed_optimization/`  
> **Status**: Complete & Verified (8/8 Automated Unit Tests Passing)  
> **Platform**: Windows 11 (12 Logical Cores), Python 3.13.3, NumPy 2.5.2, SciPy 1.18.1

---

## 1. Module Overview

Track D implements a comprehensive parallel, distributed, submodular, and multi-objective optimization suite covering six foundational paradigms:

1. **Submodular Optimization (Maximum Coverage)**: Monotone submodular set function maximization under a cardinality constraint $k$, proving and verifying the diminishing returns property, the $(1 - 1/e) \approx 63.2\%$ Nemhauser-Wolsey approximation guarantee, and comparing against exact brute-force search.
2. **Parallel Computing & Multiprocessing**: High-intensity compute workloads evaluated sequentially and across worker counts $P \in [1, 2, 4, 8]$ using persistent process pools on Windows, measuring execution time, speedup $S_P$, parallel efficiency $E_P$, and exact floating-point result parity.
3. **Amdahl's Law vs. Gustafson's Law**: Mathematical modeling, asymptotic bounds, non-linear least squares curve fitting ($R^2 = 0.9973$) extracting the empirical serial fraction ($s = 14.36\%$), and comparing strong scaling vs. weak scaling.
4. **Federated Averaging (FedAvg)**: Decentralized machine learning simulation across edge clients comparing Centralized Training vs. FedAvg IID vs. FedAvg Non-IID (label skew), quantifying client parameter drift and communication costs.
5. **Multiple Gradient Descent Algorithm (MGDA)**: Multi-objective optimization on the convex hull of gradients via quadratic programming on the simplex, proving common descent directions and identifying Pareto-stationary frontiers without scalar trade-off weights.
6. **GradNorm Multi-Task Balancing**: Dynamic gradient norm balancing across heterogeneous tasks in a shared-representation neural network, adapting task weights based on relative inverse training rates $r_i(t)$.

---

## 2. Directory Layout

```
track_d_parallel_distributed_optimization/
├── docs/
│   ├── methodology.md            # Detailed mathematical formulations, derivations & proofs
│   ├── experimental_analysis.md  # Comprehensive empirical results across all 6 areas
│   └── viva_questions.md         # 16 academic viva defense Q&As with rigorous explanations
├── experiments/
│   ├── run_submodular_benchmark.py       # Maximum Coverage scaling vs exact brute-force
│   ├── run_parallel_benchmark.py         # Multiprocessing scaling across P in {1, 2, 4, 8}
│   ├── run_amdahl_gustafson_study.py     # Theoretical curves & empirical least-squares fit
│   ├── run_fedavg_benchmark.py           # FedAvg simulation (Centralized vs IID vs Non-IID)
│   ├── run_mgda_benchmark.py             # MGDA vs Weighted Sum multi-objective optimization
│   └── run_gradnorm_benchmark.py         # GradNorm dynamic task weight balancing
├── plots/
│   ├── 01_submodular_greedy_vs_exact.png
│   ├── 02_runtime_vs_problem_size.png
│   ├── 03_theoretical_amdahl_gustafson.png
│   ├── 04_measured_parallel_speedup_efficiency.png
│   ├── 05_fedavg_training_iid_vs_non_iid.png
│   └── 06_mgda_and_gradnorm_balancing.png
├── results/
│   ├── submodular_benchmark_results.json / .csv
│   ├── parallel_benchmark_results.json / .csv
│   ├── amdahl_gustafson_results.json / .csv
│   ├── fedavg_benchmark_results.json / .csv
│   ├── mgda_benchmark_results.json / .csv
│   └── gradnorm_benchmark_results.json / .csv
├── src/
│   ├── __init__.py
│   ├── submodular.py             # MaximumCoverageProblem representation & solvers
│   ├── parallel_compute.py       # Multiprocessing benchmark harness
│   ├── amdahl_gustafson.py       # Scaling law equations & non-linear least squares fit
│   ├── fedavg.py                 # SoftmaxModel, client partitioning & FedAvg aggregator
│   ├── mgda.py                   # Multi-objective benchmarks & MGDASolver
│   ├── gradnorm.py               # MultiTaskNetwork & GradNormSimulator
│   └── visualize_results.py      # Publication-ready Matplotlib figure generator
└── tests/
    ├── __init__.py
    └── test_parallel_distributed.py # 8 automated unit tests
```

---

## 3. Quickstart & Verification Commands

All experiments and tests are executed from the repository root:

### Run Automated Unit Tests
```bash
python -m unittest discover -s track_d_parallel_distributed_optimization/tests -v
```
*(Expected: 8 tests passing in ~0.35s)*

### Run Benchmarks
```bash
# 1. Submodular Greedy vs Exact Maximum Coverage
python track_d_parallel_distributed_optimization/experiments/run_submodular_benchmark.py

# 2. Parallel Computing Scaling (Multiprocessing Pool)
python track_d_parallel_distributed_optimization/experiments/run_parallel_benchmark.py

# 3. Amdahl's Law vs Gustafson's Law Study & Fit
python track_d_parallel_distributed_optimization/experiments/run_amdahl_gustafson_study.py

# 4. Federated Averaging (Centralized vs IID vs Non-IID)
python track_d_parallel_distributed_optimization/experiments/run_fedavg_benchmark.py

# 5. Multi-Objective MGDA vs Weighted Sum
python track_d_parallel_distributed_optimization/experiments/run_mgda_benchmark.py

# 6. GradNorm Dynamic Multi-Task Balancing
python track_d_parallel_distributed_optimization/experiments/run_gradnorm_benchmark.py
```

### Regenerate Visualizations
```bash
python -m track_d_parallel_distributed_optimization.src.visualize_results
```

---

## 4. Key Experimental Findings

| Experiment | Key Metric / Result | Theoretical Benchmark |
| :--- | :--- | :--- |
| **Submodular Coverage** | Greedy gap $\le 7.14\%$ (0.0% on 2 instances) | Strictly satisfies $(1 - 1/e) \approx 63.2\%$ bound |
| **Combinatorial Scalability** | Greedy solves $U=500, m=80$ in **2.15 ms** | Exact brute force $C(80, 10) \approx 1.6 \times 10^{12}$ impossible |
| **Multiprocessing Speedup** | Speedup = **$3.94\times$** on 8 workers (Large) | Parity error = $0.0$, runtime reduced from 2.14s to 0.54s |
| **Amdahl Curve Fit** | Serial fraction $\hat{s} = 14.36\%$, $\hat{P} = 85.64\%$ | Non-linear fit $R^2 = 0.9973$, theoretical cap $6.97\times$ |
| **FedAvg Convergence** | Final Loss: Centralized $0.0494$ vs IID $0.0495$ | Near-identical performance, $132.8$ KB payload |
| **Non-IID Client Drift** | Final Drift: $0.0485$ (over $5\times$ higher than IID) | Model achieves 100% test accuracy despite label skew |
| **MGDA Pareto Discovery** | Reaches Pareto front at $(1.0, 0.0)$ with $\|\mathbf{g}^*\| \le 10^{-5}$ | Common descent direction decreases both active losses |
| **GradNorm Multi-Task** | Task 2 error reduced by **$14.1\%$** ($1.96 \to 1.69$) | Task weights adapt dynamically from $(1, 1) \to (0.65, 1.35)$ |

---

## 5. Scope & Limitations

1. **Multiprocessing Communication Overhead**: Inter-process communication on Windows uses IPC pipes (`spawn`), incurring pickling overhead. For small chunk sizes ($< 50,000$ operations), IPC overhead exceeds compute time, causing speedups $< 1.0\times$. Chunk sizes must be adequately compute-dense to amortize dispatch cost.
2. **Federated Learning Network Simulation**: The FedAvg experiment simulates decentralized client communication on a single local machine without real socket network latency, packet loss, or client dropouts.
3. **MGDA Scalability**: While closed-form for 2 objectives, solving the min-norm simplex problem for $m \ge 10$ objectives requires quadratic programming (e.g. Frank-Wolfe), which can increase per-step optimization overhead in very high task dimensions.

