# Compulsory Final Assignment Questions & Evidence-Based Answers
**Assignment**: Optimization Techniques — Lab Assignment 8 ("OPTIMIZE ANYTHING: The 14-Day Vibe-Coding Challenge")  
**Course**: Optimization Techniques  
**Source of Truth**: Official Assignment 8 PDF (Section 11, Pages 6–7)  
**Author**: Soham Umesh Chavan  
**Audit & Submission Date**: November 14, 2026 (Day 13 Final Audit)  

---

### Question 1: What process did you choose, and what evidence showed that it needed optimization?

**Answer**:  
For our primary case study (**Track E**), we selected **passenger railway routing and transfer optimization over a time-dependent timetable network** (28 physical stations, 551 elementary train connections, across 10 regional corridors).

**Empirical Evidence of Inefficiency**:
1. **The "Hurry Up and Wait" Flaw in Standard Shortest Path Algorithms**: Real passenger rail systems operate on discrete schedules with mandatory platform transfer buffers ($\Delta_{\text{min}} \in [10, 20]$ minutes). Standard routing heuristics (such as static Dijkstra or pure Earliest-Arrival algorithms) aggressively board the very first departing service. On benchmark query Q05 (`STN_11` $\to$ `STN_06`), Earliest-Arrival Dijkstra boards a regional shuttle at 06:00, forcing an intermediate transfer at Dune Plains and arriving at 09:53 (total duration: **233 minutes**, with 1 transfer and 56 minutes of idle platform waiting).
2. **Computational Evidence from Profiling**: In **Track J** (real-world enterprise workflow DAG scheduling), profiling a legacy baseline scheduler on 250 tasks revealed that **99.04% of CPU execution time** was consumed by redundant graph reachability traversals (`_collect_all_descendants` and `_collect_all_ancestors`), executing over 1.75 million function calls, 889,000 list pops, and 236,000 dictionary lookups for a single 250-task DAG schedule.
3. **Database & Kernel Inefficiencies**: In **Track H**, unindexed transactional queries (e.g. Q8) required sequential table scans over 36,000 rows in SQLite taking 1.26 ms; in **Track G**, the stock xv6 RISC-V kernel lacked per-process CPU execution time accounting, preventing scheduling fairness monitoring and CPU time tracking.

---

### Question 2: How did you formulate the objective function and constraints?

**Answer**:  
In Track E, the problem was formulated as a discrete multi-objective network flow Binary Integer Linear Program (BILP):

1. **Decision Variables**:
   - $x_c \in \{0, 1\}$: Binary indicator whether elementary train connection $c \in C$ is traversed.
   - $y_{c_1, c_2} \in \{0, 1\}$: Binary indicator whether incoming connection $c_1$ transfers directly to outgoing connection $c_2 \in C$ at an interchange station.
2. **Composite Objective Function**:
   $$\min Z = \alpha \sum_{c \in C} \tau(c) x_c + \beta \sum_{(c_1, c_2) \in T} w(c_1, c_2) y_{c_1, c_2} + \gamma \sum_{(c_1, c_2) \in T} \delta_{\text{srv}}(c_1, c_2) y_{c_1, c_2}$$
   where $\tau(c)$ is in-vehicle travel time, $w(c_1, c_2)$ is transfer waiting time, $\delta_{\text{srv}}(c_1, c_2) = 1$ if changing train services (else 0 for through-trains), with empirically validated passenger disutility weights $\alpha = 1.0, \beta = 1.5, \gamma = 30.0$.
3. **Constraints**:
   - **Flow Conservation**: At every physical station $s \in S$, total incoming flow equals total outgoing flow, except at origin $s_{\text{orig}}$ (net outflow $+1$) and destination $s_{\text{dest}}$ (net inflow $+1$).
   - **Connection Linking**: $\sum_{c_2} y_{c_1, c_2} = x_{c_1}$ and $\sum_{c_1} y_{c_1, c_2} = x_{c_2}$.
   - **Temporal Buffer & Feasibility**: Transfer set $T$ strictly enforces that outgoing connection departs at or after incoming arrival plus station transfer buffer:
     $$\text{dep\_time}(c_2) \ge \text{arr\_time}(c_1) + \Delta_{\text{min}}(\text{arr\_stn}(c_1))$$
   - **Query Departure Window**: Origin connection departure must satisfy $\text{dep\_time}(c) \ge t_{\text{query}}$.
   - **Transfer Count Bound**: Total transfers $\sum y_{c_1, c_2} \delta_{\text{srv}} \le K_{\max} = 4$.

Similar formal mathematical models were constructed for Track B (Knapsack ILP & QUBO), Track F (Compiler Pass Selection BILP), Track H (Index Selection ISP Knapsack), and Track J (DAG Makespan & Scheduler Latency Optimization).

---

### Question 3: Which Chapter 6 methods did you test, and why were they appropriate for their respective experiments?

**Answer**:  
Every method taught in Chapter 6 was tested in its mathematically natural domain:

1. **First- & Second-Order Continuous Optimizers (Track A)**:
   - *Tested*: GD, SGD, Mini-Batch SGD, Momentum, NAG, AdaGrad, RMSProp, Adam, Newton's Method, Gauss-Newton, and Decoupled Backpropagation.
   - *Suitability*: Continuous parameter optimization on neural loss surfaces, ill-conditioned quadratics, and non-convex benchmark landscapes (Rosenbrock, Rastrigin).
2. **Combinatorial Exact Solvers & Heuristics (Tracks B, E, F, H)**:
   - *Tested*: Greedy Heuristic, Branch-and-Bound, Dynamic Programming, and Integer Linear Programming (ILP via HiGHS).
   - *Suitability*: Discrete decision problems with hard constraints (0-1 Knapsack, timetable flow, compiler pass selection, database index selection).
3. **QUBO and Ising Spin Glasses (Tracks B, C, I)**:
   - *Tested*: Binary-to-spin mapping ($s_i = 2x_i - 1$), quadratic penalty expansions, QAOA ($p \in \{1, 2, 3\}$), and VQE.
   - *Suitability*: Formulating NP-hard combinatorial problems (Max-Cut, Knapsack) for hybrid quantum-classical algorithms.
4. **Submodular Optimization (Track D)**:
   - *Tested*: Diminishing returns property verification and Greedy Selection with $(1 - 1/e)$ approximation guarantee on Maximum Coverage.
5. **Parallel & Distributed Algorithms (Track D)**:
   - *Tested*: Multiprocessing worker pools (Amdahl's & Gustafson's Laws), Federated Learning (FedAvg with IID/Non-IID clients), MGDA (Pareto-stationarity), and GradNorm (gradient norm balancing).
6. **Dynamic Programming with Memoization (Tracks B, J)**:
   - *Tested*: Backward critical-path potential memoization $V(i) = d_i + \max V(j)$ on DAG scheduling, reducing complexity from $O(V^3)$ to $O((V+E)\log V)$.

---

### Question 4: How did the optimized solution compare with the baseline?

**Answer**:  
The table below highlights measured baseline-versus-optimized improvements across our primary experimental tracks:

| Track / Domain | Baseline Method | Optimized Method | Measured Performance Gain | Solution Quality Impact |
| :--- | :--- | :--- | :---: | :---: |
| **Track E (Railway)** | Earliest-Arrival Dijkstra | Exact HiGHS ILP | Mean duration: 273.9 $\to$ **246.9 min** (-27.0 min); transfers: 0.95 $\to$ **0.60** (-37%) | Multi-objective cost $Z$: 323.9 $\to$ **273.1** (-15.7% lower passenger disutility) |
| **Track J (Workflow DAG)** | Legacy Naive Scheduler $O(V^3)$ | Chapter 6 DP Scheduler $O((V+E)\log V)$ | **$12.54\times$** (Small) $\to$ **$8,212.89\times$** (XLarge) speedup (79.77s $\to$ 0.0097s) | Makespan improved by **$1.91\% - 14.84\%$**; 100% schedule validity |
| **Track H (DBMS)** | Unindexed Full Table Scans | Exact HiGHS Index Selection | Transactional PNR Query Q8: 1.26 ms $\to$ **0.11 ms** (**$11.92\times$ faster**) | 100% SHA-256 result hash parity across all queries |
| **Track F (Compiler)** | Unoptimized 3AC IR Code | 5-Pass Fixpoint Pipeline | Dynamic VM steps reduced by up to **95.0%**; runtime speedup up to **$24.2\times$** | 100% semantic output parity across all benchmark programs |
| **Track D (Parallel)** | Single-Process Execution | Multiprocessing Worker Pool | Speedup up to **$3.94\times$** on 8 cores ($E_P = 49.3\%$, Amdahl serial fraction $\hat{s} = 14.36\%$) | Numerical result parity error = 0.00000 |
| **Track G (xv6 OS)** | Stock xv6 without CPU Tracking | `getcputime()` Kernel Accounting | Per-process CPU time tracking with **zero sleeping overhead**; concurrent SMP speedup **$1.87\times$** on 3 cores | 100% passing on targeted test suite |

---

### Question 5: What trade-offs, failures, or limitations did you discover?

**Answer**:  
1. **Computational Latency vs. Solution Quality in Track E**:
   - Earliest-Arrival Dijkstra executes in **0.28 ms** (1,980x faster than ILP), making it ideal for instant autocomplete, but incurs a 20.58% optimality gap under generalized passenger cost $Z$.
   - Exact ILP achieves globally optimal itineraries ($Z^* = 273.1$), but takes **547.3 ms** on average, making it suitable for offline timetable master planning or VIP trip generation, but unsuitable for high-frequency interactive search.
2. **Greedy Myopic Traps in Track B and Track H**:
   - In Track B, Greedy fell into a **27.27% optimality gap** on knapsack selection because high value-to-weight ratio items consumed capacity without yielding high absolute value.
   - In Track H, Greedy fell into a **6.92% optimality gap** at budget $S_{\max} = 3.0$ MB: it picked `IDX_09` (0.8 MB), leaving 0.7 MB remaining and preventing the selection of `IDX_07` (1.4 MB). Exact ILP selected `IDX_07` directly, achieving an 11.92x speedup on transactional queries.
3. **Hardware Noise & Barren Plateaus in Quantum Optimization (Tracks C, I)**:
   - As circuit depth and qubit count scale ($n \in [2, 7]$), quantum gradient variance decayed exponentially as $\mathcal{O}(2^{-n})$, confirming the theoretical Barren Plateau phenomenon.
   - Simulating quantum algorithms on classical CPUs incurred massive overhead: Quantum VQC took **$282.5\times$ longer** to train than Classical Logistic Regression on Iris while achieving lower test accuracy (93.3% vs. 100.0%).
4. **Run-to-Run System Noise on Large Table Scans in Track H**:
   - While ILP sped up targeted queries by 11.92x, run-to-run CPU and operating system scheduling jitter across unindexed 180,000-row table scans (Q2, Q3, Q7) added $\pm 2.8$ ms of variance, masking targeted gains in the total aggregate sum.

---

### Question 6: What evidence demonstrates that your results are correct and reproducible?

**Answer**:  
1. **Automated Test Suite**: 102 automated tests across 11 test modules execute cleanly in 3.222 seconds with **100% pass rate** (0 errors, 0 failures).
2. **Deterministic Seeding & Clean Data Pipelines**:
   - Random generators across all tracks are fixed with deterministic seeds (Seed 42, 123, 999).
   - Datasets are persisted as structured JSON/CSV files in `data/` and `results/`.
3. **Formal Invariant & Ground Truth Verification**:
   - *Track A*: Analytical gradients verified against finite differences ($\|\nabla_{\text{anal}} - \nabla_{\text{num}}\| = 4.00 \times 10^{-12}$).
   - *Track C*: VQE ground-state energy verified against exact Hermitian matrix diagonalization ($0.47\%$ error on TFIM).
   - *Track E & F & H*: Exact ILP solutions verified against exhaustive combinatorial enumeration across all feasible subsets (0.00% gap).
   - *Track H & F*: 100% output parity verified via SHA-256 result hashes and interpreter output matching.
   - *Track J*: Automated formal schedule validator (`validate_schedule_correctness`) checks completeness, duration integrity, precedence feasibility, and worker non-concurrency on every schedule (0 violations across all 4 scales).

---

### Question 7: How could the optimization approach be adapted if the scale, data, constraints, or hardware changed?

**Answer**:  
1. **Hyperscale Timetable Networks (Track E $\to$ Millions of Connections)**:
   - While HiGHS ILP solves 28 stations and 551 connections in 547 ms, on national networks (e.g. Deutsche Bahn or Indian Railways with $>10^5$ connections), pure ILP would encounter memory and branch-and-cut bottlenecks.
   - *Adaptation*: Implement a hybrid two-stage pipeline: use multi-criteria RAPTOR (Round-Based Public Transit Routing) or Transfer Patterns to prune 99.9% of irrelevant corridors, then solve a localized ILP over the Pareto-optimal candidate subgraph.
2. **High-Velocity Streaming Workflows (Track J $\to$ Real-Time Dynamic DAGs)**:
   - If tasks arrive dynamically with stochastic execution times rather than static durations, backward DP potentials must be adapted.
   - *Adaptation*: Maintain dynamic critical-path potentials using online Bellman-Ford updates on topological order, or integrate a reinforcement-learning dispatch policy trained on historical task execution variances.
3. **Enterprise DBMS Scaling (Track H $\to$ Distributed Cloud DBs)**:
   - For Petabyte-scale distributed data warehouses (e.g. Snowflake, BigQuery), secondary B-tree indexes are replaced by partitioning, clustering keys, and materialized views.
   - *Adaptation*: Reformulate the ISP knapsack objective to incorporate multi-tenant scan costs and cloud compute credit expenditure under monthly monetary budget constraints.
4. **Quantum Hardware Deployment (Track C, I $\to$ Physical QPUs)**:
   - Deploying on physical QPUs (e.g. IBM Eagle / Heron) requires error mitigation (Zero-Noise Extrapolation, dynamical decoupling) and hardware-aware transpilation to minimize SWAP gates on fixed coupling graphs (e.g. Heavy-Hex topology).

---

### Question 8: For the compiler, xv6 and DBMS tracks, which optimization did you implement, what OS or database concept did you learn from it, and how did you show that correctness was preserved?

**Answer**:  

1. **Compiler Optimization (Track F)**:
   - *Optimization*: 5 iterative optimization passes (Constant Folding, Constant Propagation, Strength Reduction, Common Subexpression Elimination, Dead Code Elimination) run to fixed-point convergence, combined with Binary Integer Linear Programming (BILP) for budget-constrained pass selection.
   - *Concept Learned*: Phase ordering non-commutativity and iterative fixpoint convergence (e.g., constant propagation enables constant folding, which in turn exposes dead code branches).
   - *Correctness Preservation*: Demonstrated 100% semantic output parity between unoptimized and optimized 3AC IR code on the VM interpreter across all 5 benchmark programs.
2. **xv6 Kernel Optimization (Track G)**:
   - *Optimization*: Per-process CPU execution time accounting via a new system call `sys_getcputime()` (syscall 23) instrumenting hardware timer traps in `usertrap()` and `kerneltrap()`.
   - *Concept Learned*: Low-level timer interrupt dispatching, process isolation, and re-entrant lock synchronization (`acquire(&p->lock)`) to prevent race conditions during trap handling across SMP cores.
   - *Correctness Preservation*: Verified clean compilation under `riscv64-linux-gnu-gcc`, clean multi-core boot under QEMU (3 CPUs), passing all 5 checks of `test_cputime`, passing the first 29 intensive stress tests of `usertests`, and confirming that sleeping processes accumulate zero CPU ticks.
3. **DBMS Query Optimization (Track H)**:
   - *Optimization*: Formulated the Index Selection Problem (ISP) as a 0-1 Knapsack / Maximum Coverage ILP under a strict secondary index storage budget ($S_{\max} = 3.0$ MB), solved via SciPy HiGHS.
   - *Concept Learned*: B-Tree index scan mechanics vs. sequential table scans, execution plan cost estimation in SQLite, and how knapsack capacity fragmentation traps greedy heuristics.
   - *Correctness Preservation*: Verified 100% SHA-256 result hash parity across all 8 workload queries between unindexed Baseline, Greedy-indexed, and ILP-indexed configurations.

---

### Question 9: What advantages and limits of QML, quantum algorithms and parallel computing did your experiments reveal compared with classical computing?

**Answer**:  

1. **Algorithmic Advantage vs. Simulation Overhead**:
   - *Grover's Search*: Demonstrates quadratic query speedup $\mathcal{O}(\sqrt{N})$ over classical brute-force $\mathcal{O}(N)$ in oracle evaluations. On $N=4$ ($n=2$ qubits) at optimal iteration $R=1$, Grover achieved **$100.0\%$ target measurement probability**.
   - *Classical Simulation Limit*: Simulating statevectors on classical CPUs scales exponentially as $\mathcal{O}(2^n)$. In Track I, training a 2-qubit Quantum Variational Classifier on Iris required **282.5x more CPU time** than Classical Logistic Regression (6.21s vs. 0.022s) while achieving lower accuracy (93.3% vs. 100.0%).
2. **Noise, Barren Plateaus, and Measurement Costs**:
   - In Track C, measuring gradient variance across circuit widths $n \in [2, 7]$ confirmed that partial derivatives decay exponentially as $\text{Var}[\partial_\theta \langle H \rangle] \propto 2^{-n}$, rendering standard gradient descent ineffective on deep ansatzes without specialized initialization.
   - Finite measurement shot noise verified the Central Limit Theorem: expectation variance decays as $\mathcal{O}(1/S)$, requiring $\ge 10,000$ shots to achieve millihartree precision.
3. **Parallel Computing Reality (Track D vs. Quantum)**:
   - Unlike NISQ quantum simulators, multi-core classical parallelism delivered immediate, scalable speedups on real hardware: Python multiprocessing achieved up to **$3.94\times$ speedup** on 8 cores ($E_P = 49.3\%$).
   - Amdahl's Law non-linear regression fit revealed a serial bottleneck of $\hat{s} = 14.36\%$, proving that parallel speedup asymptotically plateaus at $1/\hat{s} \approx 6.96\times$ on this workload.

---

### Question 10: Which AI tools did you use, how did their outputs differ, and which AI-generated errors did you find and fix?

**Answer**:  

1. **AI Tools Used**:
   - **Antigravity AI (Gemini 3.8 Flash High / Pro)**: Primary active assistant across all 12 days. Used for architectural planning, LaTeX mathematical typing, code drafting, unit test generation, shell command dispatching, and report synthesis.
   - **Claude 3.7 Sonnet & GitHub Copilot**: Comparative protocols were established in `prompts/tool_comparison.md`; secondary live runs were marked pending to preserve strict academic honesty and avoid manufacturing artificial tool comparisons.
2. **Observed Differences in AI Output Behaviors**:
   - High-temperature code generation tends to invent plausible but non-existent API parameters (e.g., passing `name` instead of `label` to Qiskit's `UnitaryGate`, or assuming `scipy.optimize.milp` supports non-linear synergy terms directly).
   - In shell automation, AI tools frequently misinterpret serial console echo as shell prompt returns, or omit requisite typing imports (`Tuple`) in newly defined Python modules.
3. **Representative AI Failures Found and Corrected (from `prompts/failure_log.md`)**:
   - **Case 15 (Track H)**: Synthetic data generator hardcoded sample sizes ($15 \le \text{stops} \le 30$) when generating mini-test fixtures with only 10 stations, triggering `ValueError: Sample larger than population`. *Fix*: Dynamically clamped sample sizes based on station count.
   - **Case 16 (Track I)**: In Grover's search, using continuous rounding `round((pi/4)*sqrt(N))` rounded $1.57$ up to $2$ iterations for $N=4$, over-rotating the state vector past the target state and reducing success probability from 100% to 25%. *Fix*: Implemented strict floor bound $\lfloor \frac{\pi}{4}\sqrt{N} \rfloor$.
   - **Case 17 (Track J)**: Missing `Tuple` import in `workflow_models.py` triggered a `NameError` during import under Python 3.13 strict namespace validation. *Fix*: Added `Tuple` to typing imports and standardized dynamic in-degree method calls.
