# Track D: Parallel and Distributed Optimization — Experimental Analysis

> **Course**: Optimization Techniques — Assignment 8  
> **Module**: `track_d_parallel_distributed_optimization/`  
> **Verification Status**: 100% Reproducible from raw data in `results/`  
> **Host Environment**: Windows 11, 12 Logical Cores, Python 3.13.3

---

## 1. Submodular Maximization: Maximum Coverage Benchmark

### 1.1 Experimental Configuration
The Maximum Coverage problem was benchmarked across seven synthetic problem scales with element universes ranging from $U=20$ to $U=500$ and subset collections from $m=10$ to $m=80$. On the first four instances ($m \le 20, k \le 4$), exhaustive combinatorial search was executed to evaluate exact optimality gaps.

### 1.2 Quantitative Benchmark Results

| Instance | Universe Size $U$ | Subsets $m$ | Budget $k$ | Greedy Coverage | Greedy Fraction | Greedy Runtime | Exact Coverage | Exact Runtime | Optimality Gap | $(1 - 1/e)$ Bound | Bound Satisfied? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tiny-10** | 20 | 10 | 3 | **13** | 65.0% | 0.02 ms | 14 | 0.06 ms | **7.14%** | 8.85 | **True** |
| **Small-14** | 40 | 14 | 3 | **25** | 62.5% | 0.02 ms | 25 | 0.24 ms | **0.00%** | 15.80 | **True** |
| **Medium-18** | 60 | 18 | 4 | **49** | 81.7% | 0.04 ms | 49 | 3.63 ms | **0.00%** | 30.97 | **True** |
| **Borderline-20** | 80 | 20 | 4 | **53** | 66.2% | 0.07 ms | 55 | 6.98 ms | **3.64%** | 34.77 | **True** |
| **Large-35** | 150 | 35 | 6 | **122** | 81.3% | 0.19 ms | *Omit* | *Omit* | *N/A* | *N/A* | *N/A* |
| **XLarge-50** | 300 | 50 | 8 | **265** | 88.3% | 0.60 ms | *Omit* | *Omit* | *N/A* | *N/A* | *N/A* |
| **Scale-80** | 500 | 80 | 10 | **472** | 94.4% | 2.15 ms | *Omit* | *Omit* | *N/A* | *N/A* | *N/A* |

### 1.3 Key Theoretical & Empirical Findings
1. **Universal Guarantee Adherence**: On all verifiable instances, the greedy coverage strictly exceeds the Nemhauser-Wolsey $(1 - 1/e) f^*$ lower bound (e.g., $13 \ge 8.85$, $25 \ge 15.80$, $49 \ge 30.97$, $53 \ge 34.77$).
2. **Empirical Optimality Near 100%**: The average observed optimality gap across small instances was only **$2.70\%$**, with Greedy matching the exact combinatorial optimum ($0.0\%$ gap) on Small-14 and Medium-18.
3. **Combinatorial vs. Polynomial Scaling**: While exact search runtime grows exponentially from $0.06$ ms ($C(10, 3) = 120$) to $6.98$ ms ($C(20, 4) = 4,845$), Greedy executes in just $0.07$ ms. On Scale-80 ($C(80, 10) \approx 1.6 \times 10^{12}$ combinations, computationally impossible for brute force), Greedy finds a $94.4\%$ coverage subset in **2.15 ms**.

---

## 2. Parallel Computing: Multiprocessing Scaling

### 2.1 Compute-Bound Benchmark Setup
A heavy numerical workload (transcendental functions, vector powers, square roots, and exponentiation) was partitioned into independent tasks and evaluated sequentially and across worker counts $P \in [1, 2, 4, 8]$ using persistent process pools.
- **Small Workload**: 16 chunks ($2.4 \times 10^6$ total floating point elements)
- **Medium Workload**: 32 chunks ($4.8 \times 10^6$ total floating point elements)
- **Large Workload**: 48 chunks ($7.2 \times 10^6$ total floating point elements)

### 2.2 Numerical Performance Results (Mean $\pm$ Std across 3 Trials)

| Problem Scale | Worker Count $P$ | Execution Mode | Wall-Clock Time (s) | Speedup $S_P$ | Parallel Efficiency $E_P$ | Parity Error |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **Small (16 chunks)** | 1 | Sequential Baseline | $0.638 \pm 0.004$ | $1.00\times$ | 100.0% | $0.0$ |
| | 1 | Multiprocessing Pool | $0.637 \pm 0.011$ | $1.00\times$ | 100.1% | $0.0$ |
| | 2 | Multiprocessing Pool | $0.359 \pm 0.007$ | $1.78\times$ | 88.9% | $0.0$ |
| | 4 | Multiprocessing Pool | $0.258 \pm 0.014$ | $2.47\times$ | 61.8% | $0.0$ |
| | 8 | Multiprocessing Pool | $0.218 \pm 0.041$ | $2.93\times$ | 36.6% | $0.0$ |
| **Medium (32 chunks)** | 1 | Sequential Baseline | $1.316 \pm 0.026$ | $1.00\times$ | 100.0% | $0.0$ |
| | 1 | Multiprocessing Pool | $1.470 \pm 0.004$ | $0.90\times$ | 89.5% | $0.0$ |
| | 2 | Multiprocessing Pool | $0.832 \pm 0.002$ | $1.58\times$ | 79.1% | $0.0$ |
| | 4 | Multiprocessing Pool | $0.500 \pm 0.017$ | $2.63\times$ | 65.8% | $0.0$ |
| | 8 | Multiprocessing Pool | $0.374 \pm 0.019$ | $3.52\times$ | 44.0% | $0.0$ |
| **Large (48 chunks)** | 1 | Sequential Baseline | $2.138 \pm 0.063$ | $1.00\times$ | 100.0% | $0.0$ |
| | 1 | Multiprocessing Pool | $2.296 \pm 0.006$ | $0.93\times$ | 93.1% | $0.0$ |
| | 2 | Multiprocessing Pool | $1.212 \pm 0.027$ | **$1.76\times$** | **88.2%** | $0.0$ |
| | 4 | Multiprocessing Pool | $0.737 \pm 0.032$ | **$2.90\times$** | **72.5%** | $0.0$ |
| | 8 | Multiprocessing Pool | $0.542 \pm 0.033$ | **$3.94\times$** | **49.3%** | $0.0$ |

### 2.3 Detailed Efficiency Breakdown
1. **Mathematical Result Parity**: The absolute difference between sequential and parallel outputs is strictly **$0.0 \times 10^0$** across all tests, proving deterministic correctness.
2. **Workload Sizing & Amortization**: Larger workloads achieve superior parallel efficiency at high core counts ($49.3\%$ efficiency at 8 cores for Large vs $36.6\%$ for Small). This demonstrates that amortizing IPC and dispatch overhead requires adequate computational density per chunk.
3. **Real-World Bottlenecks**: As worker count increases from $P=2$ to $P=8$, memory bus saturation and CPU cache contention limit speedup to $3.94\times$ (rather than theoretical $8.0\times$).

---

## 3. Amdahl's Law vs. Gustafson's Law Modeling

### 3.1 Empirical Non-Linear Least Squares Fit
Fitting the measured Large workload speedups to Amdahl's Law $S(N) = \frac{1}{(1 - P) + P / N}$:
- **Estimated Parallel Fraction $\hat{P}$**: **$0.8564$** ($85.64\%$)
- **Estimated Serial Fraction $\hat{s}$**: **$0.1436$** ($14.36\%$)
- **Goodness of Fit ($R^2$)**: **$0.9973$** (exceptional agreement with empirical data)

### 3.2 Theoretical Scaling Comparison

| Worker Count $N$ | Measured Speedup | Fitted Amdahl (Fixed Workload) | Gustafson Scaled Speedup ($P=85.6\%$) | Ideal Linear ($100\%$) |
| :---: | :---: | :---: | :---: | :---: |
| 1 | 1.00x | 1.00x | 1.00x | 1.00x |
| 2 | 1.76x | 1.75x | 1.86x | 2.00x |
| 4 | 2.90x | 2.80x | 3.57x | 4.00x |
| 8 | 3.94x | 3.99x | 6.99x | 8.00x |
| 16 | *Predicted* | 5.07x | 13.85x | 16.00x |
| 32 | *Predicted* | 5.87x | 27.55x | 32.00x |
| $\infty$ | *Asymptote* | **6.97x** | $\infty$ | $\infty$ |

### 3.3 Core Takeaways
- **Amdahl's Strong-Scaling Bottleneck**: Even with an $85.6\%$ parallel codebase, the $14.4\%$ serial fraction (IPC data pickling, master thread reduction, OS thread sync) bounds the maximum possible speedup to $6.97\times$ under strong scaling.
- **Gustafson's Weak-Scaling Power**: When problem size scales proportionally with processors, Gustafson's Law predicts a $27.55\times$ speedup on 32 cores, demonstrating that scaling data size overcomes Amdahl's law in production environments.

---

## 4. Federated Averaging (FedAvg) Simulation

### 4.1 Benchmark Setup
- Synthetic 4-class Gaussian classification ($N=1,200$, 16 features, $80/20$ train/test split).
- 5 decentralized edge clients, 25 communication rounds, 5 local epochs per round ($\eta = 0.05$).
- Compared: Centralized Training vs FedAvg IID vs FedAvg Non-IID (label skew).

### 4.2 Benchmark Results Summary

| Model / Paradigm | Final Test Loss | Final Test Accuracy | Final Client Drift $\|\boldsymbol{\theta}_k - \boldsymbol{\theta}_{\text{global}}\|_2$ | Total Communication Volume |
| :--- | :---: | :---: | :---: | :---: |
| **Centralized Baseline** | **0.0494** | **100.00%** | $0.0000$ (Single node) | 0 KB |
| **FedAvg (IID Partitions)** | **0.0495** | **100.00%** | $0.0094$ | 132.8 KB |
| **FedAvg (Non-IID Label Skew)** | **0.0559** | **100.00%** | **0.0485** | 132.8 KB |

### 4.3 Observations on Non-IID Client Drift
- **IID Parity**: FedAvg with IID client data achieves nearly identical loss ($0.0495$ vs $0.0494$) and identical accuracy ($100\%$) to centralized training.
- **Client Drift Impact**: Under non-IID label skew, local client parameter divergence rises to $0.0485$ (over $5\times$ higher than IID). While the global model ultimately learns all classes, the loss exhibits minor early-round oscillations before converging.

---

## 5. Multi-Objective Optimization: MGDA vs. Weighted Sum

### 5.1 Conflicting Quadratics Problem
Evaluated on:
$$f_1(x) = (x_1 - 1)^2 + x_2^2, \quad f_2(x) = (x_1 + 1)^2 + x_2^2$$
From initial point $\mathbf{x}_0 = (2.5, 3.0)$. The Pareto front is the line segment between $(-1, 0)$ and $(+1, 0)$ along $x_2 = 0$.

### 5.2 Comparative Results

| Method | Weights $\boldsymbol{\lambda}$ | Final Coordinates $(x_1, x_2)$ | Final Loss $(f_1, f_2)$ | Iterations | Pareto Stationary? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **MGDA (Min-Norm Descent)** | Dynamic $\boldsymbol{\alpha}^*$ | **(1.0000, 0.0000)** | (0.0000, 4.0000) | 129 | **Yes** ($\|\mathbf{g}^*\| \le 10^{-5}$) |
| **Weighted Sum (Balanced)** | $(0.5, 0.5)$ | (0.0000, 0.0000) | (1.0000, 1.0000) | 104 | Yes |
| **Weighted Sum (Imbalanced 1)** | $(0.8, 0.2)$ | (0.6000, 0.0000) | (0.1600, 2.5600) | 115 | Yes |
| **Weighted Sum (Imbalanced 2)** | $(0.2, 0.8)$ | (-0.6000, 0.0000) | (2.5600, 0.1600) | 121 | Yes |

### 5.3 Key Insight
Standard scalarized weighted sums require manually guessing fixed trade-off coefficients $\lambda_i$. In contrast, MGDA computes the minimum-norm convex combination $\boldsymbol{\alpha}^*$ on the fly, guaranteeing descent along directions that simultaneously decrease all active objectives until reaching the Pareto frontier.

---

## 6. GradNorm: Multi-Task Learning Loss Balancing

### 6.1 Multi-Task Setup
A 2-task network with shared hidden layer (16 units) evaluated on synthetic multi-task regression (Task 1: linear; Task 2: quadratic non-linear with higher variance). Trained for 150 epochs.

### 6.2 Quantitative Results

| Training Strategy | Final Task 1 Loss | Final Task 2 Loss | Final Total Loss | Final Weights $(w_1, w_2)$ | Error Reduction on Task 2 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Fixed Equal Weights** | **0.0932** | 1.9643 | 2.0575 | $(1.0000, 1.0000)$ | Baseline |
| **GradNorm Dynamic Balancing** | 0.1247 | **1.6875** | **1.8122** | $(0.6496, 1.3504)$ | **-14.1%** |

### 6.3 Mechanistic Explanation
1. **Dynamic Task Weight Steering**: Because Task 2 is non-linear and harder to train, its relative inverse training rate $r_2(t) > 1$. GradNorm automatically elevated $w_2$ from $1.0 \to 1.3504$, while relaxing $w_1$ down to $0.6496$ (maintaining $w_1 + w_2 = 2.0$).
2. **Superior Generalization**: By allocating greater gradient magnitude to the struggling task, GradNorm reduced Task 2 error by **$14.1\%$** and overall multi-task loss by **$11.9\%$**, preventing the simple linear task from monopolizing the shared representation.

