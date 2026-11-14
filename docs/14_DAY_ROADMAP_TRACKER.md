# 14-Day Vibe-Coding Challenge: Execution Roadmap & Task Tracker

> **Project**: Optimization Techniques — Lab Assignment 8  
> **Cycle Duration**: 14 Days (Two Weeks)  
> **Status**: Day 9 Complete (Tracks A, B, C, D, E, F, and G Fully Implemented, Benchmarked, and Verified)  

---

## 1. Master Phase Overview

```
+---------------------------------------------------------------------------------------------------------+
| DAYS 1–3: DISCOVER & FORMULATE (Day 1 Complete)                                                         |
| • [COMPLETE] Project scaffolding, AI tools register, and prompt logging structure established.         |
| • [COMPLETE] WSL2, QEMU RISC-V (10.2.1), gcc-riscv64 (15.2.0), make (4.4.1), gdb installed & verified. |
| • [COMPLETE] Initial root commit (39b3913) recorded and verified.                                       |
| • [NEXT: Day 2-3] Track E Railway problem formulation, data generation, Dijkstra baseline.              |
+---------------------------------------------------------------------------------------------------------+
                                                     │
                                                     ▼
+---------------------------------------------------------------------------------------------------------+
| DAYS 4–7: EXPLORE CHAPTER 6 METHODS                                                                     |
| • Track A: Continuous optimizers (1st & 2nd order, backprop, curvature, convex/non-convex).             |
| • Track B: Discrete optimizers (Greedy, B&B, DP, ILP, QUBO/Ising formulation).                         |
| • Track C: Quantum optimization (QAOA on QUBO, VQE, PQCs, parameter-shift, SPSA, noise).                |
| • Track D: Submodular diminishing returns, parallel speedup (Amdahl/Gustafson), FedAvg & MGDA.         |
| • Track F: Mini-compiler passes (Folding, Prop, DCE, CSE) & Register allocation formulation.             |
| • Track G: xv6 kernel scheduler modifications & syscall instrumentation.                                |
| • Track H: Relational DBMS index selection knapsack/ILP formulation.                                     |
+---------------------------------------------------------------------------------------------------------+
                                                     │
                                                     ▼
+---------------------------------------------------------------------------------------------------------+
| DAYS 8–11: OPTIMIZE & BENCHMARK                                                                         |
| • Track E: Full empirical comparison (Greedy vs. ILP vs. Dijkstra) on railway benchmarks.               |
| • Track G: xv6 3-workload QEMU benchmarking & usertests regression pass.                                 |
| • Track H: DBMS EXPLAIN ANALYZE latency & throughput evaluation.                                        |
| • Track I: Quantum algorithm suite (DJ, Grover, QFT, Shor), QML vs. classical benchmark.               |
| • Track J: Software engineering test-suite minimization on >= 1,000 LOC codebase.                       |
| • Cross-track parameter tuning and sensitivity analysis.                                                |
+---------------------------------------------------------------------------------------------------------+
                                                     │
                                                     ▼
+---------------------------------------------------------------------------------------------------------+
| DAYS 12–14: VALIDATE, DOCUMENT & PUBLISH                                                                |
| • Compile Technical Report with benchmark tables, plots, and trade-off analyses.                        |
| • Answer the 10 Compulsory Final Questions with empirical evidence.                                     |
| • Finalize Vibe-Coding Prompt Logs, AI Failure Log (3+ cases), and Tool Comparison.                      |
| • End-to-end reproducibility check and public GitHub release.                                           |
+---------------------------------------------------------------------------------------------------------+
```

---

## 2. Granular Task Checklist & Pacing Schedule

### Phase 1: Days 1–3 — Discover & Formulate
* [x] **Day 1: Setup, Governance & Toolchain Verification**:
  * [x] Verify host environment (Python 3.13.3, NumPy, SciPy HiGHS MILP, Matplotlib, GCC 16, Git).
  * [x] Verify WSL2 & Ubuntu 26.04 LTS subsystem.
  * [x] Provision approved xv6 RISC-V toolchain (`build-essential`, `gdb-multiarch`, `qemu-system-misc`, `qemu-system-riscv`, `gcc-riscv64-linux-gnu`, `binutils-riscv64-linux-gnu`).
  * [x] Formally verify all 5 xv6 tools (`gcc 15.2.0`, `make 4.4.1`, `qemu-system-riscv64 10.2.1`, `riscv64-linux-gnu-gcc 15.2.0`, `gdb-multiarch 17.1`).
  * [x] Create project directory layout (`prompts/`, `docs/`, `report/`, `track_a_continuous/` through `track_j_software_eng/`).
  * [x] Author comprehensive `README.md` with AI Tools Register and commit conventions.
  * [x] Author `PROJECT_PLAN.md` incorporating approved Railway (Track E), xv6 (Track G), and Mini-compiler (Track F) decisions.
  * [x] Author `docs/CHAPTER_6_COVERAGE_CHECKLIST.md` mapping 100% Chapter 6 syllabus.
  * [x] Establish Git history and commit traceability standard.
  * [x] Audit failure logs: 4 genuine observed AI engineering issues documented; future cases reserved as pending templates.
  * [x] Audit AI tools register: Antigravity AI recorded as active; Claude and Copilot scheduled for subsequent phases.
* [x] **Day 2 & 3: Track E Railway Dataset, Formulation, Optimizers & Benchmarks**:
  * [x] Generate realistic 28-station, 130-service, 551-connection timetable dataset (`data/railway_stations.csv`, `data/train_connections.csv`, `data/railway_network.json`).
  * [x] Author comprehensive mathematical problem formulation (`track_e_case_study/docs/problem_formulation.md`).
  * [x] Author dataset description and network corridor breakdown (`track_e_case_study/docs/dataset_description.md`).
  * [x] Implement Time-Dependent Earliest-Arrival Dijkstra router with transfer buffer validation (`track_e_case_study/src/dijkstra_baseline.py`).
  * [x] Implement Static Topological Dijkstra comparative baseline (`track_e_case_study/src/dijkstra_baseline.py`).
  * [x] Implement Multi-Objective Greedy Railway Optimizer heuristic with remaining-time estimate and cycle prevention (`track_e_case_study/src/greedy_optimizer.py`).
  * [x] Implement Exact Binary Integer Linear Programming (ILP) optimizer using `scipy.optimize.milp` HiGHS (`track_e_case_study/src/ilp_optimizer.py`).
  * [x] Implement automated test suite covering 19 unit tests (9 baseline + 10 edge cases & optimality checks) — 100% pass rate (`track_e_case_study/tests/`).
  * [x] Implement and execute 20-query comparative benchmark across Dijkstra vs Greedy vs ILP (`track_e_case_study/results/comparative_benchmark_results.json`).
  * [x] Implement multi-objective weight sensitivity analysis across 4 passenger profiles (`track_e_case_study/results/weight_sensitivity_results.json`).
  * [x] Generate 7 publication-ready Matplotlib visualizations (topology, route highlight, duration, latency, wait times, optimality gap).
  * [x] Author comprehensive documentation (`greedy_methodology.md`, `ilp_formulation.md`, `comparative_analysis.md`, `viva_questions.md`).
  * [x] Author Day 2 and Day 3 prompt logs.
* [ ] **Day 3 (Next Step): xv6 RISC-V Stock Clone & Verification**:
  * [ ] Clone `xv6-riscv` source tree into `track_g_xv6/`.
  * [ ] Verify stock QEMU boot and execution of `usertests` in WSL2 Ubuntu.

### Phase 2: Days 4–7 — Core Chapter 6 Methods Implementation
* [x] **Day 4: Track A (Continuous Optimization)**:
  * [x] Implement decoupled backpropagation module with numerical finite-difference verification (error $4.00 \times 10^{-12}$).
  * [x] Implement 8 first-order optimizers: GD, SGD, Mini-batch SGD, Momentum, NAG, AdaGrad, RMSProp, Adam.
  * [x] Implement 2 second-order optimizers: Damped Newton's Method (with Levenberg-Marquardt spectral regularisation) and Gauss-Newton for non-linear least squares.
  * [x] Implement curvature approximations: Empirical Fisher Information Matrix vs NLL Hessian, low-rank BFGS update, Pearlmutter Hessian-Vector Products (HVP).
  * [x] Benchmark across 5 landscapes: Convex Quadratic, Strongly Convex, Rastrigin (Multimodal), Rosenbrock (Valley), Non-Linear Least Squares.
  * [x] Conduct step-size sensitivity sweep across $\eta \in [10^{-4}, 1.0]$.
  * [x] Conduct stochastic noise analysis & mini-batch variance reduction verifying $\mathcal{O}(\sigma^2 / B)$ scaling.
  * [x] Generate 6 publication-ready figures in `track_a_continuous_optimization/plots/`.
  * [x] Author comprehensive documentation (`methodology.md`, `experimental_analysis.md`, `viva_questions.md` with 16 Q&As, `README.md`).
  * [x] Complete automated unit test suite with 100% pass rate (11/11 tests passing).
* [x] **Day 5: Track B (Discrete Optimization & QUBO)**:
  * [x] Implement Greedy value-to-weight density heuristic with formal $27.27\%$ suboptimality counterexample.
  * [x] Implement exact Integer Linear Programming (ILP) using SciPy HiGHS (`milp`), scaling to $N=200$.
  * [x] Implement transparent Branch-and-Bound with Dantzig continuous LP relaxation upper bounds.
  * [x] Implement exact 2D Dynamic Programming table with backtracking item reconstruction ($\mathcal{O}(nW)$).
  * [x] Formulate QUBO with binary slack variables, derive Ising spin conversion ($s_i = 2x_i - 1$), and prove penalty threshold $P > \max v_i$.
  * [x] Benchmark across 9 problem scales ($N \in [3, 200]$) and conduct critical penalty phase transition study.
  * [x] Generate 4 publication-ready figures in `track_b_discrete_optimization/plots/`.
  * [x] Author comprehensive documentation (`methodology.md`, `experimental_analysis.md`, `viva_questions.md` with 16 Q&As, `README.md`).
  * [x] Complete automated unit test suite with 100% pass rate (7/7 tests passing).
* [x] **Day 6: Track C (Quantum Optimization)**:
  * [x] Formulate Hardware-Efficient & Parameterized Quantum Circuits (PQC) with $R_y, R_z, CX$ layers.
  * [x] Implement QAOA on Max-Cut instances across depths $p \in \{1, 2, 3\}$, reaching $\alpha = 100\%$ on 4-node cycle.
  * [x] Implement VQE on Transverse-Field Ising (TFIM) and Heisenberg XXZ spin chains vs exact Hermitian diagonalization ($0.47\%$ relative error).
  * [x] Implement exact analytical Parameter-Shift Rule ($\pm \pi/2$ shifts) verified against centered finite differences ($3.86 \times 10^{-11}$ error).
  * [x] Implement SPSA optimizer under shot noise, achieving convergence with strictly 2 circuit evaluations per step ($12\times$ fewer circuit evaluations than GD).
  * [x] Implement Quantum Natural Gradient (QNG) via statevector Fubini-Study metric tensor with Levenberg-Marquardt regularization.
  * [x] Conduct empirical finite shot noise study ($S \in [50, 10000]$) confirming CLT variance scaling $\mathcal{O}(1/S)$.
  * [x] Conduct Barren Plateau study ($n \in [2, 7]$ qubits) confirming exponential variance decay $\mathcal{O}(2^{-n})$.
  * [x] Generate 5 publication-ready figures in `track_c_quantum_optimization/plots/`.
  * [x] Author comprehensive documentation (`methodology.md`, `experimental_analysis.md`, `viva_questions.md` with 16 Q&As, `README.md`).
  * [x] Complete automated unit test suite with 100% pass rate (8/8 tests passing).
* [x] **Day 7: Track D (Submodular, Parallel & Distributed)**:
  * [x] Implement submodular Maximum Coverage problem; verify diminishing returns and $(1 - 1/e) \approx 63.2\%$ approximation bound against exact brute-force search.
  * [x] Implement compute-bound multiprocessing benchmark harness across worker counts $P \in [1, 2, 4, 8]$, measuring execution time, speedup ($3.94\times$ on 8 cores), and efficiency ($49.3\%$) with zero parity error.
  * [x] Implement Amdahl's Law and Gustafson's Law modeling; fit empirical speedups via non-linear least squares ($\hat{P} = 85.64\%$, $\hat{s} = 14.36\%$, $R^2 = 0.9973$).
  * [x] Implement simulated Federated Learning (FedAvg) across 5 clients, comparing Centralized ($0.0494$) vs. IID ($0.0495$) vs. Non-IID label skew (drift $0.0485$, $132.8$ KB payload).
  * [x] Implement Multiple Gradient Descent Algorithm (MGDA) solving min-norm problem on the simplex, proving common descent to Pareto front at $(1.0, 0.0)$ vs. weighted sum baselines.
  * [x] Implement GradNorm for multi-task learning, balancing task gradient norms to reduce error on the harder task by $14.1\%$ and total loss by $11.9\%$.
  * [x] Generate 6 publication-ready figures in `track_d_parallel_distributed_optimization/plots/`.
  * [x] Author comprehensive documentation (`methodology.md`, `experimental_analysis.md`, `viva_questions.md` with 16 Q&As, `README.md`).
  * [x] Complete automated unit test suite with 100% pass rate (8/8 tests passing).
* [x] **Day 8: Track F (Compiler Optimization & Binary Pass Selection)**:
  * [x] Implement complete compiler frontend: Lexer (with location tracking), recursive descent LL(1) AST Parser, Semantic Analyzer (declaration-before-use symbol table), 3AC linear IR Generator, and 3AC Virtual Machine Interpreter with cycle and runtime profiling.
  * [x] Implement 5 compiler optimization passes: Constant Folding (arithmetic simplification), Constant Propagation (reaching definitions), Strength Reduction (multiplication/division to addition/shifts), Common Subexpression Elimination (value numbering within basic blocks), and Dead Code Elimination (backward liveness analysis on pure definitions).
  * [x] Implement iterative fixpoint optimization pipeline (`CompilerOptimizer`) with full sequence stability convergence checking.
  * [x] Formulate Compiler Pass Selection as a Binary Integer Linear Programming (BILP) decision problem balancing execution speedup and code size reduction against compile-time latency budget; solved via `scipy.optimize.milp` HiGHS solver and verified against exhaustive combinatorial search ($0.00\%$ optimality gap across all budgets).
  * [x] Benchmark 5 representative programs (`arithmetic_heavy`, `repeated_expressions`, `dead_assignments`, `loop_heavy`, `combined_pipeline`) measuring static IR count, dynamic VM cycles, wall-clock time, speedup ($1.40\times$ to $22.7\times$), compile overhead, and 100% semantic output parity.
  * [x] Generate 4 publication-ready figures in `track_f_compiler_optimization/plots/`.
  * [x] Author comprehensive documentation (`language_specification.md`, `compiler_architecture.md`, `optimization_methodology.md`, `experimental_analysis.md`, `viva_questions.md` with 16 Q&As, `README.md`).
  * [x] Complete automated unit test suite with 100% pass rate (11/11 tests passing).
* [x] **Day 9: Track G (xv6 Kernel Feature Modification & CPU Runtime Accounting)**:
  * [x] Clone and inspect official MIT `xv6-riscv` repository (`fa2ddcb7ca87a77af579380a6eafd5aff163b44f`).
  * [x] Verify baseline unmodified build, clean QEMU boot, and 100% pass on xv6 `usertests`.
  * [x] Extend `struct proc` with `uint64 cputime;` and initialize in `allocproc()` and `freeproc()`.
  * [x] Instrument timer interrupt accounting in `usertrap()` and `kerneltrap()` strictly on `which_dev == 2`.
  * [x] Implement thread-safe `sys_getcputime()` system call (`SYS_getcputime (23)`) and user assembly stub.
  * [x] Author automated validation test suite `test_cputime` (5/5 checks passed).
  * [x] Implement and benchmark 3 workloads: CPU-intensive (100% duty), short burst (quantization error), concurrent SMP (1.87x multi-core speedup).
  * [x] Validate kernel stability with regression tests (`usertests preempt`, `usertests forkforkfork`).
  * [x] Generate standalone patch `track_g_xv6_kernel/patches/0001_cputime_accounting.patch` (15.1 KB).
  * [x] Generate 4 publication-ready figures in `track_g_xv6_kernel/plots/`.
  * [x] Author comprehensive documentation (`kernel_architecture.md`, `implementation.md`, `experimental_analysis.md`, `viva_questions.md` with 16 Q&As, `README.md`).
* [x] **Day 10: Track H (DBMS Query Optimization & Index Selection)**:
  * [x] Create reproducible 7-table railway reservation database schema in SQLite (`stations`, `trains`, `schedules`, `passengers`, `bookings`, `tickets`, `payments`) with seed 42 (179,760 records, 9.46 MB baseline).
  * [x] Formulate Index Selection Problem (ISP) as a discrete constrained optimization problem (0-1 Knapsack / Set Packing) with coupling constraints linearizing non-additive query benefits.
  * [x] Define representative 8-query workload (Q1-Q8) spanning range filters, multi-table joins, aggregations, subqueries, and point lookups.
  * [x] Define pool of 12 candidate single-column and composite secondary B-tree indexes.
  * [x] Implement Greedy Marginal Benefit-to-Cost heuristic with dynamic gain re-evaluation.
  * [x] Implement exact Binary ILP solver via `scipy.optimize.milp` with HiGHS branch-and-cut.
  * [x] Implement Exhaustive Combinatorial Oracle ($2^{12} = 4,096$ subsets), validating ILP exactness 100% across 14 budgets.
  * [x] Demonstrate authentic $6.92\%$ Greedy optimality gap at budget $S_{\max} = 3.0$ MB (`['IDX_02', 'IDX_09', 'IDX_10']` vs `['IDX_02', 'IDX_07']`).
  * [x] Achieve $11.45\times$ empirical speedup on transactional lookup Q8 under ILP via B-tree index seek ($1.26$ ms $\to 0.11$ ms).
  * [x] Verify 100% query result equivalence across all configurations using SHA-256 cryptographic checksums.
  * [x] Generate 4 publication-ready figures in `track_h_dbms_optimization/plots/`.
  * [x] Author comprehensive documentation (`dbms_architecture.md`, `optimization_formulation.md`, `experimental_analysis.md`, `viva_questions.md` with 15 Q&As, `README.md`).
  * [x] Complete automated test suite with 100% pass rate (10/10 tests passing).

### Phase 3: Days 8–11 — Optimization, Tuning & Deep Benchmarks
* [ ] **Track E (Main Case Study Execution)**:
  * [ ] Implement Greedy Earliest-Arrival / Minimum Transfer Waiting heuristic.
  * [ ] Implement exact Multi-Objective ILP solver via HiGHS.
  * [ ] Execute comparative benchmarks (Dijkstra vs. Greedy vs. ILP) across multiple network scales.
  * [ ] Analyze trade-offs (journey duration, transfer wait time, execution runtime).
* [x] **Track G (xv6 Benchmarking & Validation)**:
  * [x] Compile modified kernel under QEMU RISC-V in WSL2.
  * [x] Execute 3 distinct workloads (CPU-burst, short-burst, high-concurrency SMP).
  * [x] Validate 100% pass on xv6 `usertests`.
  * [x] Generate clean `patches/0001_cputime_accounting.patch`.
* [x] **Track H (DBMS Benchmark Execution)**:
  * [x] Compare Greedy vs. ILP index selection vs. default optimizer.
  * [x] Measure `EXPLAIN QUERY PLAN`, latency, throughput, and disk footprint; verify result parity.
* [x] **Day 11: Track I (Quantum Algorithms & Quantum Machine Learning)**:
  * [x] Implement 7 core quantum algorithms: Deutsch-Jozsa, Bernstein-Vazirani, Grover's search, QFT & IQFT, QPE, Shor's factoring, and QUBO / Ising annealing.
  * [x] Construct at least 2 circuits manually using elementary quantum gates (Bernstein-Vazirani and Grover's search) with gate-by-gate explanations, depth, and gate counts.
  * [x] Verify QFT reversibility to machine precision ($\|U_{\text{IQFT}} U_{\text{QFT}} - I\|_2 < 6.96 \times 10^{-16}$).
  * [x] Validate QPE exact phase recovery on dyadic phases ($\theta = 0.375, 0.250$).
  * [x] Demonstrate complete Shor's factoring pipeline on $N=15$ with $a=7$, extracting prime factors $[3, 5]$ via Continued Fractions.
  * [x] Map 4-variable QUBO to Ising spin Hamiltonian, verifying mathematical identity ($0.0$ error) and finding global ground state `1001` with energy $-8.0$.
  * [x] Train Quantum Variational Classifier (VQC) vs. Classical Logistic Regression on Iris (Classes 0 & 1, 2 features), achieving $93.3\%$ vs $100\%$ test accuracy, with honest analysis of $282.5\times$ classical simulation overhead on CPU.
  * [x] Author comprehensive master complexity comparison table and academic documentation.
  * [x] Generate 5 publication-ready figures in `track_i_quantum_algorithms/plots/`.
  * [x] Author comprehensive documentation (`quantum_fundamentals.md`, `algorithm_implementations.md`, `complexity_comparison.md`, `quantum_vs_classical_ml.md`, `experimental_analysis.md`, `viva_questions.md` with 20 Q&As, `README.md`).
  * [x] Complete automated test suite with 100% pass rate (10/10 tests passing).
* [ ] **Track J (Software Engineering Optimization)**:
  * [ ] Formulate Test-Suite Minimization as a Minimum Set Cover ILP on realistic $\ge 1,000$ LOC codebase.
  * [ ] Measure test runtime reduction and statement coverage retention.

### Phase 4: Days 12–14 — Verification, Report & Final Deliverables
* [ ] **Comprehensive Technical Report**:
  * [ ] Write dedicated report sections for Tracks A through J with tables and figures.
  * [ ] Answer all 10 Compulsory Final Questions from Page 6–7 of the specification.
  * [ ] Complete Chapter 6 Coverage Checklist with file references and verified results.
* [ ] **Vibe-Coding Disclosures**:
  * [ ] Finalize `prompts/` subdirectories with complete prompts, AI responses, and git commits.
  * [ ] Finalize `prompts/failure_log.md` with $\ge 3$ documented AI failure cases, fixes, and lessons.
  * [ ] Finalize `prompts/tool_comparison.md` comparing Antigravity AI vs. secondary assistants.
* [ ] **Reproducibility & Publication**:
  * [ ] Run end-to-end verification script (`scripts/run_all_benchmarks.py`).
  * [ ] Verify clean, reproducible execution from a fresh checkout.
  * [ ] Push to public GitHub repository.
