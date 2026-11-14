# 14-Day Vibe-Coding Challenge: Execution Roadmap & Task Tracker

> **Project**: Optimization Techniques — Lab Assignment 8  
> **Cycle Duration**: 14 Days (Two Weeks)  
> **Status**: Day 6 Complete (Tracks A, B, C, and E Fully Implemented, Benchmarked, and Verified)  

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
* [ ] **Track D (Submodular, Parallel & Distributed)**:
  * [ ] Implement submodular utility function; empirically test diminishing returns and $(1 - 1/e)$ bound.
  * [ ] Implement multiprocessing parallel execution with work stealing; fit Amdahl's and Gustafson's Laws.
  * [ ] Implement FedAvg distributed training across local epochs $E$ and communication rounds $R$.
  * [ ] Implement MGDA and GradNorm on a two-task model.
* [ ] **Track F (Mini-Compiler First Passes)**:
  * [ ] Implement Lexer, AST Parser, and 3AC Intermediate Representation (IR).
  * [ ] Implement Constant Folding and Constant Propagation passes.
  * [ ] Implement Dead Code Elimination (DCE) and Common Subexpression Elimination (CSE).
  * [ ] Formulate Register Allocation as an optimization problem (Chaitin Greedy vs. ILP).
* [ ] **Track G (xv6 Kernel Modification)**:
  * [ ] Clone xv6-riscv repository into `track_g_xv6/`.
  * [ ] Modify kernel scheduler (`proc.c`, `proc.h`) to implement Priority / Stride scheduling.
  * [ ] Add `getpinfo()` system call and write user-level benchmark harnesses.
* [ ] **Track H (DBMS Optimization Formulation)**:
  * [ ] Generate synthetic TPC-H relational dataset in SQLite/PostgreSQL.
  * [ ] Formulate Index Selection as a 0-1 Knapsack / ILP problem.

### Phase 3: Days 8–11 — Optimization, Tuning & Deep Benchmarks
* [ ] **Track E (Main Case Study Execution)**:
  * [ ] Implement Greedy Earliest-Arrival / Minimum Transfer Waiting heuristic.
  * [ ] Implement exact Multi-Objective ILP solver via HiGHS.
  * [ ] Execute comparative benchmarks (Dijkstra vs. Greedy vs. ILP) across multiple network scales.
  * [ ] Analyze trade-offs (journey duration, transfer wait time, execution runtime).
* [ ] **Track G (xv6 Benchmarking & Validation)**:
  * [ ] Compile modified kernel under QEMU RISC-V in WSL2.
  * [ ] Execute 3 distinct workloads (CPU-burst, I/O-interactive, high-concurrency).
  * [ ] Validate 100% pass on xv6 `usertests`.
  * [ ] Generate clean `xv6_opt.patch`.
* [ ] **Track H (DBMS Benchmark Execution)**:
  * [ ] Compare Greedy vs. ILP index selection vs. default optimizer.
  * [ ] Measure `EXPLAIN QUERY PLAN`, latency, throughput, and disk footprint; verify result parity.
* [ ] **Track I (Quantum Algorithms & QML)**:
  * [ ] Implement and simulate Deutsch-Jozsa, Bernstein-Vazirani, Grover, QFT, QPE, Shor, Quantum Annealing.
  * [ ] Train Variational Quantum Classifier vs. Classical MLP on identical dataset.
  * [ ] Compare Grover query speedup vs classical search; analyze simulation overhead and noise limitations.
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
