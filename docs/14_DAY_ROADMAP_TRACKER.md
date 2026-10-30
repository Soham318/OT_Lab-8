# 14-Day Vibe-Coding Challenge: Execution Roadmap & Task Tracker

> **Project**: Optimization Techniques — Lab Assignment 8  
> **Cycle Duration**: 14 Days (Two Weeks)  
> **Status**: Days 1–3 In Progress (Setup & Architecture Complete)  

---

## 1. Master Phase Overview

```
+---------------------------------------------------------------------------------------------------------+
| DAYS 1–3: DISCOVER & FORMULATE                                                                          |
| • Track E Railway problem formulation, data generation, Dijkstra baseline.                              |
| • WSL2, QEMU, RISC-V toolchain verification & environment setup.                                        |
| • Project scaffolding, AI tools register, and prompt logging structure established.                     |
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
* [x] **Setup & Verification**:
  * [x] Verify host environment (Python 3.13, NumPy, SciPy, Matplotlib, GCC 16, Git).
  * [x] Verify WSL2 & Ubuntu status; identify missing RISC-V QEMU toolchain.
  * [x] Document environment verification and provide installation commands.
* [x] **Project Architecture & Governance**:
  * [x] Create project directory layout (`prompts/`, `docs/`, `report/`, `track_a_continuous/` through `track_j_software_eng/`).
  * [x] Author comprehensive `README.md` with AI Tools Register and commit conventions.
  * [x] Author `PROJECT_PLAN.md` incorporating all specific user decisions.
  * [x] Author `docs/CHAPTER_6_COVERAGE_CHECKLIST.md` mapping 100% Chapter 6 syllabus.
* [ ] **Track E Formulation & Baseline**:
  * [ ] Generate realistic railway timetable network dataset (`data/railway_network.json`).
  * [ ] Implement Dijkstra shortest path static baseline.
  * [ ] Formulate mathematical model (decision variables, multi-objective function, flow & buffer constraints).

### Phase 2: Days 4–7 — Core Chapter 6 Methods Implementation
* [ ] **Track A (Continuous)**:
  * [ ] Implement decoupled backpropagation module.
  * [ ] Implement GD, SGD, Mini-batch SGD, Momentum, NAG, AdaGrad, RMSProp, Adam.
  * [ ] Implement Newton's method and Gauss-Newton for non-linear regression.
  * [ ] Implement curvature approximations: Fisher Information Matrix, diagonal approximation, Hessian-vector products.
  * [ ] Benchmark on convex quadratic vs non-convex (saddle point / local minima) landscapes.
* [ ] **Track B (Discrete & QUBO)**:
  * [ ] Implement Greedy combinatorial solver, Branch-and-Bound, and Dynamic Programming.
  * [ ] Implement ILP solver using SciPy HiGHS.
  * [ ] Derive and implement Max-Cut QUBO and Ising spin formulation with constraint penalties.
* [ ] **Track C (Quantum Optimization)**:
  * [ ] Implement QAOA on the Track B Max-Cut QUBO model.
  * [ ] Implement VQE for Hamiltonian ground state energy estimation.
  * [ ] Implement gradient methods: Parameter-shift rule, SPSA, and Quantum Natural Gradient.
  * [ ] Conduct empirical studies on shot noise, depolarizing hardware noise, and barren plateaus.
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
  * [ ] Finalize `prompts/tool_comparison.md` comparing Antigravity AI vs. Claude/Copilot.
* [ ] **Reproducibility & Publication**:
  * [ ] Run end-to-end verification script (`scripts/run_all_benchmarks.py`).
  * [ ] Verify clean, reproducible execution from a fresh checkout.
  * [ ] Push to public GitHub repository.
