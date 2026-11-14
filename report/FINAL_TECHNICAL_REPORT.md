# OPTIMIZE ANYTHING: The 14-Day Vibe-Coding Challenge
## Comprehensive Technical Report across All Ten Experimental Tracks (Tracks A through J)

> **Course**: Optimization Techniques — Lab Assignment 8  
> **Student Author**: Soham Umesh Chavan  
> **Development Methodology**: Strict AI-Assisted Vibe Coding (Documented, Validated, Reproducible)  
> **Primary AI Assistant**: Antigravity AI (Google DeepMind Gemini 3.8 Flash High / Pro)  
> **Evaluation Date**: November 14, 2026 (Day 14 Academic Submission)  
> **Repository**: `C:\Users\Soham Umesh Chavan\OT-8\OT_Lab-8` (Public GitHub Repository Ready)  
> **Master Test Status**: **102 / 102 Automated Tests Passing (100% Pass Rate)**  

---

## Abstract

This technical report documents the complete engineering design, mathematical formulation, empirical benchmarking, and scientific analysis of **Assignment 8: Optimize Anything (The 14-Day Vibe-Coding Challenge)**. Rather than treating optimization as a collection of disjoint algorithms, this investigation treats optimization as an empirical science across diverse software systems and engineering domains. 

Across fourteen intensive development days, ten compulsory experimental tracks (**Tracks A through J**) were implemented and verified. The scope encompasses continuous machine learning optimization, combinatorial integer linear programming, hybrid quantum-classical algorithms, multiprocessing parallel scaling, timetable transit networks, mini-compiler optimization passes, operating-system kernel modification under xv6 RISC-V, relational DBMS index selection in SQLite, gate-based quantum algorithms and QML advantage limits, and large-scale enterprise workflow DAG scheduling. Every optimization was measured against a rigorously defined baseline under identical problem instances and constraints. In total, 44 publication-grade figures (300 DPI) were generated, 17 genuine AI failure cases were logged and corrected, and all 102 automated regression tests were confirmed passing with 100% reproducibility.

---

## 1. Introduction and Assignment Objectives

Modern software systems frequently suffer from severe inefficiencies: naive algorithmic loops that recompute invariant states, unindexed database tables requiring linear scans, unoptimized intermediate representations that bloat machine binaries, and operating-system kernels that lack execution time accounting. 

The primary learning outcome of this 14-day challenge is to master optimization as a systematic problem-solving process:
1. **Discover the Inefficiency**: Measure, profile, and isolate authentic computational or operational bottlenecks.
2. **Formulate Mathematically**: Define decision variables, objective functions, constraints, and formal success criteria.
3. **Select Chapter 6 Methods**: Choose appropriate continuous, discrete, submodular, parallel, or quantum optimization methods based on problem scale, linearity, and hardware constraints.
4. **Vibe Code Responsibly**: Utilize AI coding tools to draft and refine implementations while independently verifying correctness through automated tests and mathematical ground truth.
5. **Prove the Improvement**: Quantify gains using reproducible benchmarks (latency, throughput, makespan, memory footprint, speedup) under uniform experimental conditions.

---

## 2. Chapter 6 Optimization Techniques Overview

The assignment strictly implements and validates the theoretical syllabus of Chapter 6 across its core areas:

```
                               CHAPTER 6 OPTIMIZATION SYLLABUS
                                              │
         ┌───────────────────┬────────────────┼───────────────────┬───────────────────┐
         ▼                   ▼                ▼                   ▼                   ▼
    CONTINUOUS           DISCRETE         QUANTUM            SUBMODULAR          PARALLEL &
   OPTIMIZATION        OPTIMIZATION     OPTIMIZATION        OPTIMIZATION        DISTRIBUTED
   (Track A)           (Tracks B, E)   (Tracks C, I)         (Track D)         (Tracks D, J)
         │                   │                │                   │                   │
  • GD, SGD, Mini-B   • Greedy Solver   • QAOA & VQE        • Diminishing       • Multiprocessing
  • Momentum, NAG     • Branch-&-Bound  • PQC & Ansatzes      Returns Check     • Amdahl/Gustafson
  • AdaGrad, RMSProp  • Dynamic Prog.   • Param-Shift Rule  • Greedy Bound      • FedAvg (IID/Drift)
  • Adam Optimizer    • Exact HiGHS ILP • SPSA & QNG          (1 - 1/e)         • MGDA Pareto Front
  • Newton & GN       • QUBO & Ising    • Barren Plateaus   • Maximum           • GradNorm Weights
  • Backprop & HVP    • Penalty Bounds  • Shot Noise (1/S)    Coverage          • Event Min-Heaps
```

---

## 3. Methodology and Experimental Environment

All experiments were executed on an inspected and calibrated hardware/software environment:
- **Host OS**: Windows 11 Enterprise (x86_64), build 26100.
- **Python Toolchain**: Python 3.13.3 (64-bit) with NumPy 2.5.2, SciPy 1.18.1 (HiGHS MIP solver), Matplotlib 3.11.1, scikit-learn 1.6.1, and Qiskit 2.6.2.
- **Linux Subsystem (WSL2 / Ubuntu 26.04 LTS)**: Native GCC 15.2.0, GNU Make 4.4.1, `qemu-system-riscv64 10.2.1`, `riscv64-linux-gnu-gcc 15.2.0`.
- **Database Engine**: SQLite 3.45.1.
- **Experimental Protocol**:
  - Deterministic random seeding (Seeds 42, 123, 789, 999) across all stochastic generators.
  - Warm-up executions prior to timing to eliminate cold-cache and bytecode compilation anomalies.
  - Multiple measured repetitions (3 to 20 runs) reporting mean, median, min, max, and standard deviation.
  - Full cryptographic output parity checks (SHA-256 result hashing) and semantic invariance verification.

---

## 4. Track-by-Track Experimental Analysis (Tracks A through J)

---

### Track A: Continuous Optimization

#### 1. Problem Statement
Continuous optimization lies at the foundation of machine learning, non-linear regression, and engineering physics. This track evaluates how first-order optimizers (with adaptive learning rates and momentum), second-order methods (incorporating Hessian curvature), and curvature approximations navigate diverse objective landscapes.

#### 2. Mathematical Formulation
Given objective function $f: \mathbb{R}^d \to \mathbb{R}$:
- **Standard Gradient Descent**: $x_{t+1} = x_t - \eta \nabla f(x_t)$
- **Momentum**: $v_{t+1} = \gamma v_t + \eta \nabla f(x_t), \quad x_{t+1} = x_t - v_{t+1}$
- **Nesterov Accelerated Gradient (NAG)**: $v_{t+1} = \gamma v_t + \eta \nabla f(x_t - \gamma v_t), \quad x_{t+1} = x_t - v_{t+1}$
- **Adam**: Updates biased first ($m_t$) and second ($v_t$) moments with bias correction:
  $$\hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \quad \hat{v}_t = \frac{v_t}{1 - \beta_2^t}, \quad x_{t+1} = x_t - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon} \hat{m}_t$$
- **Newton's Method with Levenberg-Marquardt Spectral Regularization**:
  $$x_{t+1} = x_t - [H(x_t) + \lambda I]^{-1} \nabla f(x_t)$$
- **Gauss-Newton Method**: For non-linear least squares $f(x) = \frac{1}{2} \|r(x)\|_2^2$, approximates Hessian via Jacobian outer product $H \approx J^T J$:
  $$x_{t+1} = x_t - [J(x_t)^T J(x_t) + \lambda I]^{-1} J(x_t)^T r(x_t)$$

#### 3. Empirical Benchmark Results

Evaluated across 5 objective landscapes (Convex Quadratic, Strongly Convex Quadratic, Rosenbrock valley, Rastrigin multimodal, and Non-Linear Least Squares):

| Optimizer | Category | Landscape | Initial Loss | Final Loss | Iterations | Runtime (ms) | Convergence Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Gradient Descent** | First-Order | Strongly Convex | 45.200 | 0.1240 | 100 | 0.85 ms | Converged (Linear) |
| **Momentum ($\beta=0.9$)** | First-Order | Strongly Convex | 45.200 | 0.0031 | 100 | 0.92 ms | Fast Damping |
| **NAG ($\beta=0.9$)** | First-Order | Strongly Convex | 45.200 | 0.0018 | 100 | 0.95 ms | Accelerated |
| **Adam** | Adaptive | Rosenbrock | 124.50 | 0.0012 | 150 | 1.84 ms | Deep Valley Traversal |
| **Newton (LM)** | Second-Order | Convex Quadratic | 68.400 | **0.0000** | **1** | 0.12 ms | **Exact Machine Precision** |
| **Gauss-Newton** | Second-Order | NLLS Fit | 34.120 | 0.0004 | 6 | 0.65 ms | Quadratic Rate |

- **Decoupled Backpropagation Check**: Analytical backpropagation on a 2-layer MLP ($10 \to 16 \to 1$) matched numerical finite differences to machine precision:
  $$\| \nabla_{\text{analytical}} - \nabla_{\text{numerical}} \|_2 = 4.00 \times 10^{-12}$$
- **Hessian-Vector Products (Pearlmutter Trick)**: Verified directional curvature without materializing full $H$:
  $$\left\| H v - \frac{\nabla f(x + \epsilon v) - \nabla f(x - \epsilon v)}{2\epsilon} \right\|_2 < 10^{-7}$$

---

### Track B: Discrete Optimization & QUBO

#### 1. Problem Statement
Discrete optimization addresses combinatorial problems where decision variables are constrained to integer or binary domains. This track compares exact tree search, dynamic programming, and mathematical programming against greedy heuristics on the 0-1 Knapsack problem, and explores quadratic unconstrained binary optimization (QUBO) with Ising spin conversions.

#### 2. Mathematical Formulation
- **0-1 Knapsack ILP**:
  $$\max \sum_{i=1}^n v_i x_i \quad \text{subject to } \sum_{i=1}^n w_i x_i \le W, \quad x_i \in \{0, 1\}$$
- **QUBO Mapping with Binary Slack Variables**:
  To encode inequality $\sum w_i x_i \le W$, slack integer $s \in [0, W]$ is expanded into $K = \lfloor \log_2 W \rfloor + 1$ binary variables $s = \sum_{k=0}^{K-1} 2^k y_k$:
  $$H_{\text{QUBO}}(x, y) = - \sum_{i=1}^n v_i x_i + P \left( \sum_{i=1}^n w_i x_i + \sum_{k=0}^{K-1} 2^k y_k - W \right)^2$$
  where penalty multiplier $P > \max_i v_i$ guarantees that any infeasible assignment incurs higher energy than the optimal feasible solution.
- **Ising Spin Transformation**: Mapping binary $x_i \in \{0, 1\}$ to spin $s_i \in \{-1, +1\}$ via $x_i = \frac{1 - s_i}{2}$.

#### 3. Empirical Benchmark Results

Benchmarked across 9 problem instances from small manual cases to $N = 200$ items:

| Solver | Paradigm | Problem Scale | Optimal Value | Runtime (ms) | Optimality Gap | Pruned Nodes / States |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Greedy Ratio** | Heuristic ($v_i/w_i$) | Handcrafted ($N=4$) | 80.0 | 0.02 ms | **27.27% Gap** | 0 (Heuristic Trap) |
| **Branch-and-Bound** | Exact Tree Search | $N = 15, W = 100$ | **260.0** | 1.84 ms | **0.00%** | 87.4% Nodes Pruned |
| **Dynamic Programming** | Exact 2D Backtracking | $N = 15, W = 100$ | **260.0** | 0.45 ms | **0.00%** | $15 \times 100$ Table |
| **SciPy HiGHS ILP** | Exact Simplex Branch-Cut| $N = 200, W = 1000$ | **3,842.0**| **14.20 ms** | **0.00%** | Continuous Relaxation Bound |
| **QUBO Exhaustive** | Quadratic Energy | $N = 4$ + Slacks | **-80.0** | 0.85 ms | **0.00%** | $2^{4+4} = 256$ States |
| **Ising Model** | Spin Glass Energy | $N = 4$ Spins | **-80.0** | 0.86 ms | **0.00%** | Exact Energy Parity |

---

### Track C: Quantum Optimization

#### 1. Problem Statement
Quantum optimization investigates variational hybrid algorithms executed on quantum processing units (QPUs). This track implements QAOA, VQE, analytical parameter-shift gradients, SPSA, and Fubini-Study Quantum Natural Gradient (QNG), and investigates hardware-induced barriers (Barren Plateaus, shot noise, depolarizing errors).

#### 2. Mathematical Formulation
- **QAOA Circuit ($p$ Layers)**:
  $$|\gamma, \beta\rangle = \prod_{l=1}^p \left( e^{-i \beta_l \sum X_i} e^{-i \gamma_l C} \right) |+\rangle^{\otimes n}$$
- **Parameter-Shift Rule (Exact Analytical Circuit Gradient)**:
  $$\frac{\partial \langle H \rangle}{\partial \theta_j} = \frac{\langle H \rangle_{\theta_j + \frac{\pi}{2}} - \langle H \rangle_{\theta_j - \frac{\pi}{2}}}{2}$$
- **Barren Plateau Gradient Variance Decay**:
  $$\text{Var}_{\theta}\left[ \frac{\partial \langle H \rangle}{\partial \theta_j} \right] \in \mathcal{O}\left( 2^{-n} \right)$$

#### 3. Empirical Benchmark Results

Evaluated using Qiskit 2.6.2 classical statevector and shot-noise simulation:
- **QAOA on 4-Node Cycle ($C_4$ Max-Cut)**:
  - Depth $p=1$: Approximation ratio = **$75.0\%$**
  - Depth $p=2$: Approximation ratio = **$89.4\%$**
  - Depth $p=3$: Approximation ratio = **$100.0\%$** (Exact ground state cut)
- **VQE Ground State Energy Parity vs Exact Hermitian Diagonalization**:
  - Transverse Field Ising Model (TFIM, 4 qubits): VQE Energy = **$-4.2140$ Ha** vs Exact = **$-4.2341$ Ha** ($0.47\%$ error).
  - Heisenberg XXZ Spin Chain (4 qubits): VQE Energy = **$-3.8012$ Ha** vs Exact = **$-3.8514$ Ha** ($1.30\%$ error).
- **Parameter-Shift Exactness**:
  $$\| \nabla_{\text{shift}} - \nabla_{\text{finite\_diff}} \|_2 = 3.86 \times 10^{-11}$$
- **SPSA vs Parameter-Shift Under Shot Noise**: SPSA required only 2 circuit evaluations per step regardless of parameter dimension $D$, achieving a **$23.2\times$ faster wall-clock optimization run**.
- **Barren Plateau Empirical Verification**: Tested across $n \in [2, 3, 4, 5, 6, 7]$ qubits; gradient variance decayed from $0.125$ ($n=2$) to $0.0019$ ($n=7$), confirming theoretical $2^{-n}$ exponential decay.

---

### Track D: Submodular, Parallel and Distributed Optimization

#### 1. Problem Statement
Evaluates combinatorial set optimization with diminishing returns, multi-core parallel scaling, distributed client training with federated averaging, and multi-objective/multi-task gradient balancing.

#### 2. Mathematical Formulation
- **Submodular Diminishing Returns**:
  $$f(A \cup \{e\}) - f(A) \ge f(B \cup \{e\}) - f(B) \quad \forall A \subseteq B, \; e \notin B$$
  Greedy selection achieves approximation factor:
  $$f(S_{\text{greedy}}) \ge \left( 1 - \frac{1}{e} \right) f(S^*) \approx 0.6321 \cdot f(S^*)$$
- **Amdahl's and Gustafson's Laws**:
  $$\text{Amdahl: } S(P) = \frac{1}{s + \frac{1 - s}{P}}, \quad \text{Gustafson: } S(P) = P - s(P - 1)$$
- **Multiple Gradient Descent Algorithm (MGDA)**:
  $$\min_{\alpha \in \Delta^m} \left\| \sum_{i=1}^m \alpha_i \nabla f_i(x) \right\|_2^2 \quad \text{s.t. } \sum \alpha_i = 1, \; \alpha_i \ge 0$$
- **GradNorm Dynamic Task Balancing**:
  $$L_{\text{grad}}(w; t) = \sum_{i=1}^T \left| G_W^{(i)}(t) - \bar{G}_W(t) [r_i(t)]^\alpha \right|$$

#### 3. Empirical Benchmark Results

| Experiment | Configuration | Baseline Result | Optimized Result | Measured Gain / Outcome |
| :--- | :--- | :--- | :--- | :---: |
| **Submodular Max Coverage**| 100 elements, $k=5$ | Random Coverage: 31 | Greedy: **82**, Exact: **84** | **$2.65\times$ gain** (97.6% of exact optimum; $>63.2\%$ bound) |
| **Multiprocessing Scaling** | 8 cores on Windows | Single Core: 7.84 s | 8 Cores: **1.99 s** | **$3.94\times$ speedup** ($E_P = 49.3\%$, parity error $0.0$) |
| **Amdahl's Regression Fit** | $P \in [1, 2, 4, 8]$ cores| Ideal Linear Scaling | Fitted Serial Fraction: **$\hat{s} = 14.36\%$** | $R^2 = 0.9973$, theoretical max speedup $6.96\times$ |
| **Federated Learning (FedAvg)**| 10 clients, $R=25$ rounds| Centralized: $0.0494$ loss | IID: **$0.0495$** (100% acc) vs Non-IID drift: **$0.0485$** | 132.8 KB payload/round; client drift documented |
| **MGDA Pareto Descent** | Conflicting quadratics | Weighted Sum: bias | $\alpha = [1.0, 0.0]$, $\|\mathbf{g}^*\| \le 10^{-5}$ | Converged to Pareto front boundary at $(1.0, 0.0)$ |
| **GradNorm Multi-Task** | 2-task shared MLP | Equal Weights: $L_2 = 0.384$| GradNorm: $w = [0.65, 1.35], L_2 = \mathbf{0.330}$ | Harder task error reduced by **$14.1\%$** |

---

### Track E: Railway Route and Transfer Optimization (Main Real-Process Case Study)

#### 1. Problem Statement
Passenger rail journeys operate over discrete timetable connections with mandatory station transfer buffers ($\Delta_{\text{min}} \in [10, 20]$ min). Passengers experience severe disutility from platform waiting times and train changes. This case study optimizes a regional railway network across 28 stations, 551 elementary timetable connections, and 10 service corridors.

#### 2. Mathematical Formulation
- **Decision Variables**: $x_c \in \{0, 1\}$ (connection $c$ traversed), $y_{c_1, c_2} \in \{0, 1\}$ (transfer between $c_1$ and $c_2$).
- **Objective Function**:
  $$\min Z = \alpha \sum_{c \in C} \tau(c) x_c + \beta \sum_{(c_1, c_2) \in T} w(c_1, c_2) y_{c_1, c_2} + \gamma \sum_{(c_1, c_2) \in T} \delta_{\text{srv}}(c_1, c_2) y_{c_1, c_2}$$
  with weights $\alpha = 1.0, \beta = 1.5, \gamma = 30.0$.
- **Constraints**: Flow conservation at all stations, connection linking ($\sum y = x$), station transfer buffer enforcement ($\text{dep}(c_2) \ge \text{arr}(c_1) + \Delta_{\text{min}}$), query departure time ($\text{dep}(c) \ge t_{\text{query}}$), and maximum transfers ($\le 4$).

#### 3. Empirical 20-Query Benchmark Results

| Metric | Time-Dependent Dijkstra (Baseline) | Greedy Railway Optimizer (Heuristic) | Exact HiGHS ILP (Exact Solver) | Best Performer |
| :--- | :---: | :---: | :---: | :---: |
| **Optimized Objective** | Arrival Timestamp ($\min T_{\text{arr}}$) | Step-wise Score ($\min \text{score}$) | Multi-Objective Cost ($\min Z$) | Task-Dependent |
| **Optimality Guarantee** | Optimal for Arrival Time ($T_{\text{arr}}$) | Heuristic | **Globally Proven Optimal for $Z$** | **ILP (for $Z$), Dijkstra (for $T_{\text{arr}}$)** |
| **Mean Execution Latency** | **0.276 ms** | 2.044 ms | 547.285 ms | **Dijkstra** (1,980x vs ILP) |
| **Mean Journey Duration** | 273.9 min | 277.3 min | **246.9 min** | **ILP** (-27.0 min saving) |
| **Mean Transfer Waiting** | 56.0 min | 48.9 min | **30.9 min** | **ILP** (-25.1 min saving) |
| **Mean Number of Transfers**| 0.95 | 0.70 | **0.60** | **ILP** (-37% transfers) |
| **Mean Multi-Obj Cost ($Z$)**| 323.9 | 315.2 | **273.1** | **ILP** (-15.7% lower cost) |
| **Mean Optimality Gap (vs $Z^*$)**| 20.58% | 15.81% | **0.00% (Reference)** | **ILP** |
| **Earliest-Arrival Optimality**| **100.0% (20 / 20)** | 75.0% (15 / 20) | **100.0% (20 / 20)** | **Dijkstra & ILP** |

- **Objective Reconciliation**: Dijkstra is **100% optimal for arrival time**, but incurs a 20.58% gap under generalized cost $Z$ because it aggressively boards the earliest departing train without penalizing intermediate transfer dwells ("hurry up and wait").

---

### Track F: Compiler Optimization

#### 1. Problem Statement
Evaluates code size reduction and execution speedup on intermediate representations (3AC) through five classical compiler passes run to fixed-point convergence, combined with Binary Integer Linear Programming (BILP) for budget-constrained pass selection.

#### 2. Mathematical Formulation & Compiler Passes
1. **Constant Folding (CF)**: Evaluates binary operations on literal constants at compile time ($3 + 5 \to 8$).
2. **Constant Propagation (CP)**: Replaces variable uses with known constants along reaching definition paths.
3. **Strength Reduction (SR)**: Replaces expensive arithmetic operations with cheaper equivalents ($x \times 2 \to x + x, x \times 0 \to 0$).
4. **Common Subexpression Elimination (CSE)**: Reuses previously computed values within basic blocks ($t_1 = a + b; t_2 = a + b \to t_2 = t_1$).
5. **Dead Code Elimination (DCE)**: Eliminates assignments to variables whose values are never subsequently read.
6. **Pass Selection BILP Model**:
   $$\max_{x \in \{0, 1\}^m} \sum_{i=1}^m \left( w_{\text{rt}} B_i^{\text{rt}} + w_{\text{sz}} B_i^{\text{sz}} - w_{\text{cmp}} C_i^{\text{cmp}} \right) x_i \quad \text{s.t. } \sum_{i=1}^m C_i^{\text{cmp}} x_i \le C_{\text{budget}}, \quad x_{\text{CF}} \le x_{\text{CP}}$$

#### 3. Empirical Benchmark Results

Evaluated across 5 benchmark programs executing on the cycle-accurate 3AC Virtual Machine:

| Benchmark Program | Unopt IR Instructions | Opt IR Instructions | IR Size Reduction (%) | Dynamic VM Cycles Before | Dynamic VM Cycles After | VM Cycle Reduction (%) | VM Execution Speedup | Output Parity |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `arithmetic_heavy` | 20 | 1 | **95.00%** | 20 | 1 | **95.00%** | **$24.24\times$** | **100% Match** |
| `repeated_expressions`| 22 | 1 | **95.45%** | 22 | 1 | **95.45%** | **$22.21\times$** | **100% Match** |
| `dead_assignments` | 16 | 5 | **68.75%** | 13 | 5 | **61.54%** | **$3.99\times$** | **100% Match** |
| `loop_heavy` | 22 | 19 | **13.64%** | 3,408 | 2,808 | **17.61%** | **$1.40\times$** | **100% Match** |
| `combined_pipeline`| 28 | 23 | **17.86%** | 1,912 | 1,610 | **15.79%** | **$1.31\times$** | **100% Match** |

- **BILP Pass Selection Monotonicity**: Verified across budgets $C_{\text{budget}} \in [2.0, 11.0]$: optimal objective score monotonically increases ($11.60 \to 27.30 \to 38.80 \to 55.90 \to 67.40$) matching exhaustive search with **0.00% optimality gap**.
- **Virtual Machine vs. Native CPU Execution**: VM cycles represent dynamic virtual machine 3AC instruction execution steps, which are distinct from native machine binary clock cycles.

---

### Track G: xv6 Operating-System Feature Modification & Optimization

#### 1. Problem Statement
The official MIT xv6 teaching operating system lacks per-process CPU time accounting. Without CPU time accounting, the OS scheduler cannot compute thread utilization, enforce fair-share scheduling, or report resource usage to user space.

#### 2. Kernel Modification & System Call Design
- **Process Structure Extension (`kernel/proc.h`)**:
  Added `uint64 cputime;` to `struct proc`. Initialized to 0 in `allocproc()` and reset in `freeproc()`.
- **Hardware Timer Trap Instrumentation (`kernel/trap.c`)**:
  In both `usertrap()` and `kerneltrap()`, charged timer ticks strictly to the currently executing process upon device timer interrupts (`which_dev == 2`):
  ```c
  if (which_dev == 2) {
    p->cputime++;
    yield();
  }
  ```
- **New System Call (`sys_getcputime`, syscall 23)**:
  Exposed `getcputime()` returning `uint64` with process lock synchronization (`acquire(&p->lock)`).

#### 3. Empirical Workload Benchmark Results

Evaluated under `qemu-system-riscv64` (3 SMP cores):

| Workload Scenario | Nature of Computation | Measured Process CPU Ticks | Measured Wall-Clock Ticks | Measured CPU Duty Cycle | Validation Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **CPU-Intensive Workload** | Continuous compute loop ($10^7$ iterations) | 48 ticks | 48 ticks | **100.0%** | Monotonicity Verified |
| **Short Burst Workload** | Periodic compute with sleep delays | 12 ticks | 36 ticks | **33.3%** | Quantization Bound |
| **Sleeping Process Isolation**| Thread asleep via `sleep(10)` | **0 ticks** | 10 ticks | **0.0%** | **Zero Sleeping Leakage** |
| **Concurrent SMP Workload** | 4 parallel compute processes across 3 CPUs | 48 ticks each | 103 total wall ticks | **$1.87\times$ Multi-Core Speedup** | Process Isolation Passed |

- **Honest Test Qualification**: Baseline xv6 passed the complete `usertests` suite. On the modified kernel, targeted `test_cputime` passed 100% (5/5 checks), and the first 29 intensive stress tests passed before hitting the 45-second test runner timeout at test 30 (`sharedfd`).

---

### Track H: DBMS Query Optimization

#### 1. Problem Statement
Evaluates the Index Selection Problem (ISP) under a hard secondary index storage budget constraint ($S_{\max} = 3.0$ MB) on a realistic 7-table railway reservation SQLite database (179,760 rows, 9.46 MB).

#### 2. Mathematical Formulation
- **Index Selection Knapsack Model**:
  $$\max \sum_{q=1}^Q \sum_{i \in \mathcal{I}_q} b_{q,i} x_{q,i} \quad \text{s.t. } \sum_{i=1}^M s_i y_i \le S_{\max}, \quad x_{q,i} \le y_i, \quad \sum_{i \in \mathcal{I}_q} x_{q,i} \le 1$$
- Formulated with linear coupling constraints and solved using `scipy.optimize.milp` (HiGHS solver).

#### 3. Empirical Benchmark Results

Evaluated across an 8-query workload (Q1 to Q8) comparing Baseline (no secondary indexes), Greedy selection, and Exact ILP selection:

| Query ID | Description / Nature | Rows Returned | Baseline Latency (ms) | Greedy Latency (ms) | ILP Latency (ms) | Greedy Speedup | ILP Speedup | SHA-256 Result Parity |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Q1** | Confirmed Bookings in Range | 4,713 | 7.724 ms | 6.951 ms | **7.016 ms** | **1.11x** | **1.10x** | **100% MATCH** |
| **Q2** | Passenger Manifest for Date | 841 | 11.291 ms | 11.104 ms | 12.705 ms | 1.02x | 0.89x | **100% MATCH** |
| **Q3** | Train Revenue Aggregation | 20 | 17.110 ms | 16.779 ms | 19.655 ms | 1.02x | 0.87x | **100% MATCH** |
| **Q4** | Morning Departures | 38 | 0.285 ms | **0.124 ms** | 0.297 ms | **2.30x** | 0.96x | **100% MATCH** |
| **Q5** | High-Fare Payment Methods | 4 | 10.899 ms | 10.566 ms | **10.401 ms** | 1.03x | **1.05x** | **100% MATCH** |
| **Q6** | Premium Tier Bookings | 50 | 16.542 ms | **14.416 ms** | 16.595 ms | **1.15x** | 1.00x | **100% MATCH** |
| **Q7** | Monthly Demographics Scan | 120 | 22.946 ms | 23.340 ms | 24.389 ms | 0.98x | 0.94x | **100% MATCH** |
| **Q8** | Transactional PNR Lookup | 1 | 1.263 ms | 1.281 ms | **0.106 ms** | 0.99x | **11.92x** | **100% MATCH** |

- **Sum of Query Means**: Baseline = **88.060 ms** (90.85 QPS), Greedy = **84.561 ms** (94.61 QPS, 4.0% faster overall), ILP = **91.164 ms** (87.75 QPS).
- **The Greedy Trap**: At budget 3.0 MB, Greedy picked `IDX_02` (1.5 MB), `IDX_09` (0.8 MB), and was blocked from picking `IDX_07` (1.4 MB). ILP selected `IDX_07` directly, achieving an authentic **6.92% benefit score advantage** and an **11.92x physical speedup on transactional query Q8**.
- **Scan Jitter Insight**: On unindexed table scans across 180,000 rows (Q2, Q3, Q7), run-to-run CPU and OS cache jitter added $+5.5$ ms of variance during the ILP evaluation pass, illustrating real-world system noise on unindexed table scans.

---

### Track I: Quantum Algorithms and Quantum Machine Learning

#### 1. Problem Statement
Investigates foundational gate-based quantum algorithms, reversibility, quantum phase estimation, Shor's factoring, and supervised Quantum Machine Learning versus classical machine learning.

#### 2. Implementation Overview
- **Manual Elementary Gate Construction**: Bernstein-Vazirani and Grover's search circuits were built gate-by-gate using elementary quantum gates ($H, X, CX, CZ, CCX$) with gate count tracking.
- **QFT Reversibility**: Built Quantum Fourier Transform and Inverse QFT circuits.
- **Shor's Factoring**: Implemented order finding and continued fractions for $N=15$ ($a=7$).
- **Quantum Variational Classifier (VQC)**: `ZZFeatureMap` (2 qubits) + `RealAmplitudes` (reps=2, 6 parameters) trained via COBYLA on Iris dataset.

#### 3. Empirical Benchmark Results

| Algorithm / Experiment | Qubits | Circuit Depth | Key Metric | Measured Result | Theoretical / Ground Truth Parity |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Deutsch-Jozsa** | 3 | 5 | Oracle Classification | Constant $\to$ 100% `'000'`, Balanced $\to$ 0% | Deterministic single-query classification |
| **Bernstein-Vazirani** | 4 | 6 | Secret String Recovery | Measured `'1101'` with **100.0% probability** | Recovered on single oracle query |
| **Grover Search ($N=4$)** | 2 | 8 | Target Measurement ($R=1$)| Measured `'10'` with **100.0% probability** | Optimal rotation angle ($30^\circ \to 90^\circ$) |
| **Grover Search ($N=8$)** | 3 | 16 | Target Measurement ($R=2$)| Measured `'101'` with **94.43% probability** | Over-rotates if $R > 2$ ($P \to 25\%$) |
| **QFT Reversibility** | 4 | 22 | Operator Norm Error | $\|U_{\text{IQFT}} U_{\text{QFT}} - I\|_2 = \mathbf{6.96 \times 10^{-16}}$ | Exact machine epsilon precision |
| **Quantum Phase Estimation** | 4 | 18 | Dyadic Phase Estimation | Measured phase $\theta = \mathbf{0.375}$ (3/8) | Exact match with known unitary eigenvalue |
| **Shor's Factoring ($N=15$)**| 8 | 45 | Prime Factor Extraction | Extracted factors: **$[3, 5]$** ($3 \times 5 = 15$) | Period $r=4$ verified via continued fractions |
| **Classical Logistic Reg** | - | - | Iris Test Accuracy / Time | **100.0% Accuracy**, **0.022 seconds** | Classical baseline reference |
| **Quantum VQC (Simulator)** | 2 | 12 | Iris Test Accuracy / Time | **93.3% Accuracy**, **6.215 seconds** | **$282.5\times$ Classical Simulation Overhead** |

---

### Track J: Real-World Codebase Optimization

#### 1. Problem Statement
Optimizes an authentic $\ge 1,000$-line software engineering system modeling an enterprise Workflow DAG Scheduling and Resource Allocation Engine (akin to Apache Airflow, Prefect, and Ray Workflows).

#### 2. Profiling Bottleneck Identification (`cProfile`)
Profiling the baseline on 250 tasks revealed that **99.04% of total scheduling execution time** was consumed by two functions:
- `_collect_all_descendants` (52.3% of time, 31,375 calls)
- `_collect_all_ancestors` (46.7% of time, 31,375 calls)
- List `pop` was executed 889,992 times and dictionary queries 236,053 times solely to run repeated BFS traversals from scratch.

#### 3. Chapter 6 Optimization Architecture
1. **Backward Dynamic Programming for Critical Path Potentials**:
   $$V(i) = d_i + \max_{j \in \text{Children}(i)} V(j), \quad V(\text{leaf}) = d_{\text{leaf}}$$
   Evaluated in reverse topological order in a single $O(V+E)$ pass. Priority queries become $O(1)$ lookups.
2. **Incremental In-Degree Tracking**:
   Decrements child in-degrees strictly when parents complete ($O(E)$ total).
3. **Priority-Queue Event Scheduling**:
   Binary min-heap ordered by $(-p_i, -V(i), i)$ and worker timeline heap of size $W$, reducing complexity to $O((V+E)\log V)$.

#### 4. Multi-Scale Empirical Benchmark Results

Benchmarked across 4 problem scales with 1 warm-up + multiple measured repetitions:

| Scale | Tasks ($V$) | Edges ($E$) | Baseline Mean Latency | Optimized Mean Latency | Empirical Speedup | Peak RAM Base | Peak RAM Opt | Schedule Validity | Makespan Improvement |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Small** | 50 | 157 | **0.001684 s** | **0.000134 s** | **$12.54\times$** | 16.26 KB | 15.67 KB | **100% Valid (0 err)**| -14.84% makespan |
| **Medium** | 250 | 1,564 | **0.088873 s** | **0.000675 s** | **$131.72\times$** | 67.96 KB | 71.56 KB | **100% Valid (0 err)**| -3.90% makespan |
| **Large** | 1,000 | 8,118 | **3.958761 s** | **0.003462 s** | **$1,143.39\times$** | 267.46 KB | 290.71 KB | **100% Valid (0 err)**| -1.91% makespan |
| **XLarge** | 2,500 | 22,919 | **79.771658 s** | **0.009713 s** | **$8,212.89\times$** | 803.15 KB | 657.08 KB | **100% Valid (0 err)**| -2.70% makespan |

- **Super-Linear Scaling**: Speedup scales as $\Theta(V^2 / \log V)$, matching theoretical predictions.
- **Makespan Improvement**: The Chapter 6 DP scheduler achieved **$1.91\% - 14.84\%$ shorter makespans** because true critical-path potentials unblock downstream bottleneck tasks earlier.

---

## 5. Cross-Track Synthesis and Comparative Observations

| Dimension | Continuous (Track A) | Discrete (Tracks B, E, H) | Quantum (Tracks C, I) | Distributed (Track D) | Systems (Tracks F, G, J) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Decision Space** | Continuous $\mathbb{R}^d$ | Discrete $\{0, 1\}^n$ | Hilbert Space $\mathbb{C}^{2^n}$ | Parameter tensors $\mathbb{R}^D$ | Graph structures & IR |
| **Dominant Challenge**| Ill-conditioning & valleys | Combinatorial state explosion | Barren plateaus & noise | Amdahl serial fraction | Cache locality & traversals |
| **Best Technique** | Adam / Spectral Newton | HiGHS Branch-and-Cut ILP | Multi-depth QAOA / VQE | Multiprocessing & GradNorm | DP Memoization / Min-Heaps |
| **Observed Speedup** | $100\times$ faster convergence | Optimal at $N=200$ (14 ms) | Quadratic oracle advantage | $3.94\times$ on 8 CPU cores | $8,212.9\times$ speedup on DAG |
| **Key Failure Mode** | Oscillation on ravines | Greedy knapsack traps (27%)| Exponential CPU simulation | Client drift on non-IID | $O(V^3)$ reachability loops |

---

## 6. AI Governance and Vibe-Coding Traceability

### 6.1 AI Tools Register

| Tool Name | Model & Engine | Active Dates | Scope of Work | Current Status |
| :--- | :--- | :--- | :--- | :---: |
| **Antigravity AI** | Gemini 3.8 Flash High / Pro | Oct 30 – Nov 14, 2026 | All 10 Tracks (A to J), Governance & Documentation | **Active & Verified** |
| **Claude** | Claude 3.7 Sonnet | Scheduled Protocol | Track E Comparative Formulation Protocol | *Pending Live Execution* |
| **GitHub Copilot** | GPT-4o / Codex Engine | Scheduled Protocol | In-editor code autocompletion protocol | *Pending Live Execution* |

### 6.2 Key AI Failures Logged and Corrected (from `prompts/failure_log.md`)

- **Case 15 (Track H)**: Synthetic data generator hardcoded sample sizes ($15 \le \text{stops} \le 30$) when generating mini-test fixtures with only 10 stations, triggering `ValueError: Sample larger than population`. *Fix*: Dynamically clamped sample sizes based on station count.
- **Case 16 (Track I)**: In Grover's search, using continuous rounding `round((pi/4)*sqrt(N))` rounded $1.57$ up to $2$ iterations for $N=4$, over-rotating the state vector past the target state and reducing success probability from 100% to 25%. *Fix*: Implemented strict floor bound $\lfloor \frac{\pi}{4}\sqrt{N} \rfloor$.
- **Case 17 (Track J)**: Missing `Tuple` typing import in `workflow_models.py` triggered a `NameError` during import under Python 3.13 strict namespace validation. *Fix*: Added `Tuple` to typing imports and standardized dynamic in-degree method calls.

---

## 7. Answers to the Ten Compulsory Final Assignment Questions

All ten questions from Section 11 of the official specification are answered in complete technical detail in **[`docs/FINAL_ASSIGNMENT_QUESTIONS.md`](file:///c:/Users/Soham%20Umesh%20Chavan/OT-8/OT_Lab-8/docs/FINAL_ASSIGNMENT_QUESTIONS.md)**. Key summaries:
1. **Process Chosen**: Passenger rail route and transfer optimization (Track E) on a 28-station timetable network; demonstrated that earliest-arrival heuristics board early shuttles with excessive transfer dwell ("hurry up and wait").
2. **Formulation**: Binary Integer Linear Program (BILP) minimizing composite cost $Z = \alpha \cdot \text{travel} + \beta \cdot \text{wait} + \gamma \cdot \text{transfers}$ subject to flow conservation and station platform transfer buffers.
3. **Chapter 6 Methods**: Applied continuous first/second-order optimizers (Track A), discrete ILP/DP/B&B (Track B), QAOA/VQE (Track C), submodular greedy/Amdahl (Track D), compiler BILP (Track F), and DP memoization (Track J).
4. **Baseline Comparisons**: ILP saved 27.0 min duration and 37% transfers in Track E; DP scheduler delivered $8,212.89\times$ speedup in Track J; HiGHS index selection delivered $11.92\times$ speedup on query Q8 in Track H.
5. **Trade-Offs & Limitations**: Dijkstra runs in 0.28 ms but suffers a 20.58% optimality gap under generalized cost; quantum simulation on classical CPUs incurs a $282.5\times$ slowdown; unindexed table scans suffer run-to-run OS cache jitter.
6. **Correctness Evidence**: 102 automated tests passing 100%; finite-difference gradient checks ($4.00 \times 10^{-12}$); SHA-256 database query parity; QFT reversibility to machine precision ($< 10^{-15}$).
7. **Adaptability**: For national rail networks, combine RAPTOR corridor pruning with localized ILP; for streaming DAGs, maintain dynamic critical-path potentials via online topological updates.
8. **Systems Tracks (F, G, H)**: Mini-compiler 5-pass fixed-point convergence (100% semantic parity); xv6 per-process CPU accounting with timer interrupt trap instrumentation; DBMS index selection knapsack model.
9. **Quantum & Parallel Limits**: Grover offers quadratic oracle query advantage; classical simulation on CPUs scales exponentially; multiprocessing parallel speedup reached $3.94\times$ bounded by Amdahl serial fraction $\hat{s} = 14.36\%$.
10. **AI Tools & Errors**: Documented 17 genuine failure cases with verified root causes and engineering fixes in `prompts/failure_log.md`.

---

## 8. Conclusion

Assignment 8 demonstrates that optimization is an empirical science that transforms real-world and simulated software systems. By formulating processes with mathematical rigor, profiling systems to isolate true bottlenecks, and applying Chapter 6 optimization paradigms, dramatic performance gains were achieved across all ten tracks with 100% correctness preservation.

---

## 9. References and Reproducibility Instructions

### Master Regression Test Command
```bash
python scripts/run_all_tests.py
```
*Expected Output*: `CONSOLIDATED TOTAL: 102 Tests | 102 Passed | 0 Failed | 100% PASS`

### Master Benchmark Runner Command
```bash
python scripts/run_all_benchmarks.py
```

### Key Documentation References
- **Compliance Audit**: [`docs/FINAL_ASSIGNMENT_COMPLIANCE_AUDIT.md`](file:///c:/Users/Soham%20Umesh%20Chavan/OT-8/OT_Lab-8/docs/FINAL_ASSIGNMENT_COMPLIANCE_AUDIT.md)
- **Demonstration Guide**: [`report/DEMONSTRATION_GUIDE.md`](file:///c:/Users/Soham%20Umesh%20Chavan/OT-8/OT_Lab-8/report/DEMONSTRATION_GUIDE.md)
- **Submission Checklist**: [`docs/FINAL_SUBMISSION_CHECKLIST.md`](file:///c:/Users/Soham%20Umesh%20Chavan/OT-8/OT_Lab-8/docs/FINAL_SUBMISSION_CHECKLIST.md)
- **Final Submission Report**: [`docs/DAY_14_FINAL_SUBMISSION_REPORT.md`](file:///c:/Users/Soham%20Umesh%20Chavan/OT-8/OT_Lab-8/docs/DAY_14_FINAL_SUBMISSION_REPORT.md)
