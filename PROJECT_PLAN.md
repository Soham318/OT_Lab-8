# PROJECT PLAN: OPTIMIZE ANYTHING (14-Day Vibe-Coding Challenge)

> **Document Version**: 1.0.0  
> **Repository**: `OT_Lab-8`  
> **Course**: Optimization Techniques  
> **Status**: Approved Architecture & Experimental Specifications  

---

## 1. Master Architectural Design

This project implements the complete, compulsory 10-track optimization suite (Tracks A to J) as prescribed by the Assignment 8 specification. Every track is treated as an empirical experiment: starting from a rigorous baseline, formulating optimization models mathematically, applying specific Chapter 6 algorithms, testing correctness, and quantifying performance gains with reproducible benchmarks.

```
+---------------------------------------------------------------------------------------------------+
|                                 OT_LAB-8 EXPERIMENTAL ARCHITECTURE                               |
+---------------------------------------------------------------------------------------------------+
|  [Foundations & Core Algorithms]                   [Domain & Systems Tracks]                      |
|  - Track A: Continuous Optimization                - Track E: Railway Transfer Optimization (MAIN)|
|  - Track B: Discrete & QUBO/Ising                  - Track F: Mini-Compiler (4 Passes + ILP Alloc)|
|  - Track C: Quantum Opt (QAOA, VQE, QNG)          - Track G: xv6 RISC-V Scheduler in WSL2/QEMU   |
|  - Track D: Submodular, Parallel, FedAvg, MGDA    - Track H: DBMS Index/Join Knapsack/ILP        |
|  - Track I: Quantum Algorithms & QML vs Classical - Track J: SE Codebase Test-Suite Minimization  |
+---------------------------------------------------------------------------------------------------+
|  [Cross-Cutting Infrastructure]                                                                   |
|  - Vibe-Coding Protocol: AI Tools Register, Failure Log (3+ cases), Two-Tool Comparison           |
|  - Commit Traceability: [AI:antigravity], [AI:claude], [AI:copilot], [MANUAL:fix]                 |
|  - Verification Suites: Automated regression testing, semantic equivalence, usertests             |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Track E: Main Real-Process Case Study (Railway Route & Transfer Optimization)

### 2.1 Problem Identification & Real-World Inefficiency
Passenger rail journeys across dense networks frequently suffer from suboptimal connection choices. Existing journey planners typically optimize for either raw physical distance or single-train duration, leading to:
1. High transfer waiting times (buffer inefficiencies).
2. Unreliable connections causing missed trains.
3. Excessive transfers resulting in passenger fatigue and elevated delay risk.

### 2.2 Mathematical Formulation

Let the railway timetable network be represented as a time-expanded directed graph $G = (V, E)$, where:
* Nodes $v = (s, t) \in V$ represent station $s$ at time $t$.
* Edges $e = (u, v) \in E_{\text{ride}}$ represent a train trip between adjacent stations departing at $t_{\text{dep}}(u)$ and arriving at $t_{\text{arr}}(v)$.
* Edges $e = (u_1, u_2) \in E_{\text{transfer}}$ represent a physical transfer at station $s$ between incoming train service $k_1$ arriving at $t_1$ and outgoing train service $k_2$ departing at $t_2$, requiring $t_2 - t_1 \ge \Delta_{\text{min}}(s)$.

#### Decision Variables:
* $x_e \in \{0, 1\}$: Binary variable indicating whether edge $e \in E$ is included in the passenger's itinerary.
* $y_{s, k_1, k_2} \in \{0, 1\}$: Binary variable indicating a transfer at station $s$ between train service $k_1$ and train service $k_2$.

#### Objective Function:
Minimize a composite multi-objective cost function:
$$\min Z = \alpha \sum_{e \in E_{\text{ride}}} \tau(e) x_e + \beta \sum_{e \in E_{\text{transfer}}} w(e) x_e + \gamma \sum_{s, k_1, k_2} y_{s, k_1, k_2}$$

Where:
* $\tau(e)$: Train travel runtime along edge $e$.
* $w(e) = t_{\text{dep}}(v) - t_{\text{arr}}(u)$: Transfer waiting time at the interchange station.
* $\alpha, \beta, \gamma \ge 0$: Weighting parameters trading off in-vehicle time, waiting time, and transfer penalty.

#### Constraints:
1. **Flow Conservation**:
   $$\sum_{e \in \delta^+(v)} x_e - \sum_{e \in \delta^-(v)} x_e = \begin{cases} 1 & \text{if } v = v_{\text{origin}} \\ -1 & \text{if } v = v_{\text{destination}} \\ 0 & \text{otherwise} \end{cases}$$
2. **Transfer Minimum Buffer**:
   $$w(e) \ge \Delta_{\text{min}}(s) \quad \forall e \in E_{\text{transfer}}$$
3. **Maximum Transfers Allowed**:
   $$\sum_{s, k_1, k_2} y_{s, k_1, k_2} \le K_{\text{max}}$$
4. **Binary Integrality**:
   $$x_e \in \{0, 1\}, \quad y_{s, k_1, k_2} \in \{0, 1\}$$

### 2.3 Experimental Comparison
1. **Baseline**: Standard Dijkstra Shortest Path algorithm on the static topological graph (minimizing distance or nominal travel time without timetable/transfer awareness).
2. **Method 1 (Greedy Heuristic)**: Time-dependent Earliest-Arrival / Minimum Transfer Waiting Greedy search.
3. **Method 2 (Integer Linear Programming - ILP)**: Exact branch-and-cut optimization using HiGHS (`scipy.optimize.milp`).
4. **Evaluation Metrics**:
   * Total journey time (minutes).
   * Transfer wait time (minutes).
   * Total number of transfers.
   * Algorithm execution time (ms).
   * Optimality gap (%) between Greedy and ILP.
   * Scalability across network sizes ($N \in [20, 200]$ stations, $K \in [50, 1000]$ train runs).

---

## 3. Track G: xv6 Operating-System Optimization

### 3.1 Environment & Platform
* **Platform**: WSL2 with Ubuntu 26.04 LTS running `qemu-system-riscv64`.
* **Kernel Codebase**: MIT xv6 RISC-V (`xv6-riscv`).

### 3.2 Optimization Scope & Design
* **Primary Feature**: **Priority / Stride Scheduler**.
  * Stock xv6 implements a naive Round-Robin (RR) scheduler iterating through the `proc` array under a global process table lock.
  * Optimization: Implement priority-based scheduling with stride allocation, where processes are assigned tickets/priorities, and dynamic priority aging is introduced to prevent starvation of low-priority tasks.
  * Instrument kernel with a new system call: `sys_getpinfo(struct pstat *ps)` to collect process turnaround times, CPU ticks consumed, and context switch counts.
* **Secondary Feature (Full Credit)**: **Buffer Cache Optimization**.
  * Replace the linear singly-linked buffer cache search in `bio.c` with a hashed bucket structure and a 2-Queue / LRU eviction scheme to reduce disk block lookup lock contention.
* **Evaluation Workloads**:
  1. *CPU-bound burst workload*: Intensive compute loops measuring proportional CPU allocation matching assigned priorities.
  2. *I/O-intensive mixed workload*: Interactive/yielding processes evaluating response time and latency.
  3. *High-concurrency worker workload*: Multiprocess fork stress test measuring context switch overhead and scheduler scalability.
* **Verification**:
  * Clean boot under QEMU.
  * 100% pass on xv6 `usertests`.
  * Exportable diff file: `xv6_scheduler_opt.patch`.

---

## 4. Track F: Compiler Optimization

### 4.1 Architecture
A fully self-contained, modular mini-compiler implemented in clean, dependency-free Python:
1. **Lexer**: Tokenizes source code into identifiers, keywords, operators, and literals.
2. **Parser**: Recursive-descent parser producing an Abstract Syntax Tree (AST).
3. **IR Generator**: Emits a 3-Address Code (3AC) Quadruple Intermediate Representation: `(OP, ARG1, ARG2, RESULT)`.
4. **Code Generator**: Generates executable virtual machine bytecode or assembly-like instructions.

### 4.2 Four Optimization Passes (Full Credit)
1. **Constant Folding**: Evaluates constant expressions at compile time (e.g., `x = 3 * 7 + 4` $\rightarrow$ `x = 25`).
2. **Constant Propagation**: Forward-propagates constant values through basic blocks and across definitions until re-assigned.
3. **Dead Code Elimination (DCE)**: Identifies unused variable assignments and unreachable basic blocks via def-use chains.
4. **Common Subexpression Elimination (CSE)**: Identifies redundant computations using local and global available expressions analysis.

### 4.3 Chapter 6 Optimization Formulation
* **Problem**: **Register Allocation via Graph Coloring**.
* Formulate interference graph register allocation:
  * Interference graph $G = (V, E)$ where variables live simultaneously share an edge.
  * Formulated and solved using both a **Greedy Chaitin-style Kempe heuristic** and an **Integer Linear Programming (ILP)** formulation minimizing memory spill costs subject to $K$ available hardware registers.
* **Verification**:
  * Output semantic preservation across unoptimized and optimized code runs.
  * Benchmark reductions in instruction count, IR statement count, and register spill overhead.

---

## 5. Detailed Design for Tracks A, B, C, D, H, I, J

### Track A: Continuous Optimization
* **Algorithms**: Gradient Descent, SGD, Mini-batch SGD, Momentum, Nesterov Accelerated Gradient (NAG), AdaGrad, RMSProp, Adam, Newton's Method, Gauss-Newton.
* **Architecture**: Modular gradient computation (Backpropagation) cleanly decoupled from optimizer update rules.
* **Curvature Approximations**: Empirical Fisher Information Matrix, diagonal Hessian approximation, and Hessian-Vector Products (Pearlmutter's method).
* **Landscape Benchmark**:
  * Convex & strongly convex: Multidimensional quadratic loss $f(x) = \frac{1}{2} x^T A x - b^T x$.
  * Non-convex: Beale function / Rosenbrock valley with known saddle points and local minima.
* **Studies**: Step-size sensitivity curves and convergence behavior under Gaussian gradient noise.

### Track B: Discrete Optimization & QUBO
* **Problem**: Combinatorial Resource Allocation & Maximum Cut (Max-Cut).
* **Methods**:
  * Exact: Branch-and-Bound, Dynamic Programming (for 0-1 Knapsack sub-problem), ILP (via SciPy HiGHS).
  * Heuristic: Greedy heuristic.
* **QUBO / Ising Formulation**:
  * Formulate Max-Cut as a Quadratic Unconstrained Binary Optimization problem:
    $$\min x^T Q x \iff \max \sum_{(u, v) \in E} \frac{1 - s_u s_v}{2}, \quad s_i \in \{-1, +1\}$$
  * Solve classically via simulated annealing and exact enumeration to establish the rigorous baseline for Track C.

### Track C: Quantum Optimization
* **Methods**:
  * Quantum Approximate Optimization Algorithm (QAOA) solving the Track B Max-Cut QUBO.
  * Variational Quantum Eigensolver (VQE) finding ground-state energy of a molecule / spin chain.
  * Parameterized Quantum Circuits (PQCs) and Quantum Neural Networks (QNNs).
* **Gradients**: Parameter-shift rule vs. SPSA (Simultaneous Perturbation Stochastic Approximation) vs. Quantum Natural Gradient (QNG using Fubini-Study metric).
* **Empirical Studies**:
  * Finite measurement shot noise ($S \in [100, 10000]$ vs. exact statevector).
  * Hardware depolarizing noise model.
  * Barren plateau phenomenon: Variance of gradients decaying exponentially $\mathcal{O}(2^{-n})$ as qubit count $n \in [2, 10]$ and circuit depth scale.

### Track D: Submodular, Parallel & Distributed Optimization
* **Submodular**: Sensor placement / Influence maximization. Formally verify submodularity:
  $$f(A \cup \{e\}) - f(A) \ge f(B \cup \{e\}) - f(B), \quad \forall A \subseteq B$$
  Measure greedy $(1 - 1/e) \approx 63.2\%$ approximation bound.
* **Parallel Program Optimization**: Multiprocessing task scheduling with work stealing vs. static partitioning; quantify speedup, parallel efficiency, and curve-fit to Amdahl's and Gustafson's Laws.
* **Distributed (Federated Learning)**: FedAvg vs. Centralized training across varying local epochs $E \in [1, 10]$ and communication rounds $R$.
* **Multi-Task Optimization**: Multiple Gradient Descent Algorithm (MGDA) and GradNorm vs. equal task weighting on a multi-objective loss landscape.

### Track H: DBMS Optimization
* **System**: Relational DBMS (SQLite / PostgreSQL) with documented synthetic TPC-H benchmark tables.
* **Formulation**: Index Selection formulated as a 0-1 Knapsack / ILP problem under storage budget constraints:
  $$\max \sum_{i} \Delta \text{Cost}(q_j, I_i) x_i \quad \text{s.t.} \quad \sum_i \text{Size}(I_i) x_i \le B_{\text{storage}}$$
* **Comparison**: Greedy Index Selection vs. ILP Selection vs. Unindexed Baseline.
* **Measurements**: `EXPLAIN QUERY PLAN` cost estimates, actual execution latency, throughput, and disk footprint; guarantee 100% query result equivalence.

### Track I: Quantum Algorithms & QML Advantage
* **Simulated Algorithms**: Deutsch-Jozsa, Bernstein-Vazirani, Grover's Search, Quantum Fourier Transform (QFT), Quantum Phase Estimation (QPE), Shor's period finding, and Quantum Annealing.
* **From-Scratch Circuits**: Implement gate-level circuits for Deutsch-Jozsa and Grover's search from first principles.
* **QML vs. Classical**: Variational Classifier vs. Classical Logistic Regression/MLP on identical synthetic classification data (report accuracy, parameters, training time, circuit calls).
* **Complexity Advantage**: Grover query count ($\mathcal{O}(\sqrt{N})$) vs. classical linear search ($\mathcal{O}(N)$) contrasted against wall-clock simulation time.
* **Honest Negative Analysis**: Discussion of quantum state preparation bottleneck, simulation overhead, and noise vulnerabilities.

### Track J: Software-Engineering Optimization
* **Problem**: Test-Suite Minimization & Regression Selection on a codebase $\ge 1,000$ LOC.
* **Formulation**: Minimum Set Cover problem formulated as an ILP:
  $$\min \sum_{t \in T} c_t x_t \quad \text{s.t.} \quad \sum_{t: c_{t, m} = 1} x_t \ge 1 \quad \forall m \in M, \quad x_t \in \{0, 1\}$$
* **Comparison**: Greedy test selection vs. ILP test selection vs. full test suite.
* **Metrics**: Test execution time, code statement coverage preservation, and test reduction percentage.

---

## 6. Verification and Validation Strategy

1. **Unit & Regression Testing**: Every algorithm module has an associated test case in `tests/`.
2. **Deterministic Reproducibility**: Fixed random seeds used across all stochastic optimizers (SGD, SPSA, Simulated Annealing).
3. **Semantic Equivalence Checks**:
   * Compiler: Executing unoptimized vs optimized code on diverse test vectors.
   * DBMS: Comparing query output hashes between unindexed and indexed runs.
   * xv6: Standard test harness execution (`usertests`).
