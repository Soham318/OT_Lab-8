# Assignment 8: OPTIMIZE ANYTHING — The 14-Day Vibe-Coding Challenge

> **Course**: Optimization Techniques  
> **Approach**: Strict AI-Assisted Vibe Coding (Documented & Reproducible)  
> **Scope**: 10 Compulsory Tracks (A through J) & Full Chapter 6 Syllabus Coverage  
> **Repository**: Public GitHub Repository & Comprehensive Technical Report  

---

## 1. Executive Overview

This repository houses the complete empirical deliverables for **Assignment 8: Optimize Anything (14-Day Vibe-Coding Challenge)**. The challenge approaches optimization not merely as code implementation, but as an applied science: discovering inefficiencies, translating processes into formal mathematical formulations (decision variables, objective functions, constraints), applying exact and heuristic optimization techniques from Chapter 6, and proving measurable gains through rigorous, reproducible experimentation.

All ten tracks (**Tracks A to J**) are compulsory and structured as focused, verifiable experiments:
* **Track A**: **Continuous Optimization** (First-order, second-order, curvature approximations, landscape topology).  
  * *Status*: **Complete (Day 4)** — Implemented 8 first-order optimizers (GD, SGD, Mini-batch, Momentum, NAG, AdaGrad, RMSProp, Adam) and 2 second-order optimizers (spectral Levenberg-Marquardt Newton, Gauss-Newton); decoupled 2-layer MLP backpropagation verified against finite differences to $4.00 \times 10^{-12}$ error; evaluated across 5 landscapes (Convex, Strongly Convex, Rastrigin, Rosenbrock, NLLS); step-size sensitivity sweep and stochastic noise variance reduction ($\mathcal{O}(\sigma^2/B)$) verified; 11/11 unit tests passing (100%), 6 publication-ready plots generated in `track_a_continuous_optimization/plots/`, and 16 academic viva Q&As documented.
* **Track B**: **Discrete Optimization & QUBO** (Combinatorial selection, ILP, Branch-and-Bound, DP, QUBO/Ising formulation).  
  * *Status*: **Complete (Day 5)** — Implemented 5 discrete paradigms: Greedy density heuristic (with formal 27.27% gap counterexample), transparent Branch-and-Bound (with Dantzig continuous LP bounds), exact 2D Dynamic Programming with backtracking, and exact Integer Linear Programming via SciPy HiGHS; formulated QUBO with binary slack variables, proved exact Ising spin mapping ($s_i = 2x_i - 1$) and critical penalty boundary ($P > \max v_i$); benchmarked across 9 instances up to $N=200$; 7/7 automated tests passing (100%), 4 publication-ready figures generated in `track_b_discrete_optimization/plots/`, and 16 academic viva Q&As documented.
* **Track C**: **Quantum Optimization** (QAOA, VQE, PQCs, parameter-shift, SPSA, QNG, barren plateaus, noise).  
  * *Status*: **Complete (Day 6)** — Implemented Parameterized Quantum Circuits (hardware-efficient ansatzes with $R_y, R_z, CX$), QAOA on Max-Cut across depths $p \in \{1, 2, 3\}$ achieving $100\%$ approximation ratio on 4-node cycle, VQE on TFIM ($0.47\%$ error) and Heisenberg XXZ ($1.30\%$ error) vs exact Hermitian matrix diagonalization, exact parameter-shift rule ($3.86 \times 10^{-11}$ error vs finite differences), SPSA optimizer under shot noise ($23.2\times$ faster runtime, 2 circuits/step), Fubini-Study QNG with Levenberg-Marquardt regularization, finite shot noise scaling ($\mathcal{O}(1/S)$), and Barren Plateau exponential variance decay ($\mathcal{O}(2^{-n})$ across $n \in [2, 7]$ qubits); 8/8 automated unit tests passing (100%), 5 publication-ready plots generated in `track_c_quantum_optimization/plots/`, and 16 academic viva Q&As documented.
* **Track D**: **Submodular, Parallel & Distributed Optimization** (Submodular coverage, multiprocessing scaling, Amdahl/Gustafson laws, FedAvg, MGDA, GradNorm).  
  * *Status*: **Complete (Day 7)** — Implemented monotone submodular Maximum Coverage with diminishing returns verification and $(1 - 1/e) \approx 63.2\%$ bound guarantee vs exact combinatorial enumeration (average gap $2.70\%$); high-compute multiprocessing scaling across worker counts $P \in [1, 2, 4, 8]$ achieving $3.94\times$ speedup on 8 cores ($E_P = 49.3\%$) with zero parity error; fitted Amdahl's Law ($\hat{s} = 14.36\%$, $\hat{P} = 85.64\%$, $R^2 = 0.9973$) and Gustafson's Law ($27.55\times$ projected at 32 cores); simulated Federated Averaging across 5 edge clients comparing Centralized ($0.0494$), IID ($0.0495$), and Non-IID label skew (drift $0.0485$, $132.8$ KB payload); implemented Multiple Gradient Descent Algorithm (MGDA) solving min-norm problem on the simplex to reach Pareto-stationary front at $(1.0, 0.0)$; implemented GradNorm dynamic task loss balancing, reducing harder task error by $14.1\%$ and total multi-task loss by $11.9\%$; 8/8 automated unit tests passing (100%), 6 publication-ready figures generated in `track_d_parallel_distributed_optimization/plots/`, and 16 academic viva Q&As documented.
* **Track E (Main Case Study)**: **Railway Route and Transfer Optimization** (Multi-objective journey & transfer wait minimization via Binary ILP, Greedy heuristic, and Dijkstra baseline).  
  * *Status*: **Complete (Days 2 & 3)** — 28-station timetable dataset generated (`data/`), mathematical formulation documented (`track_e_case_study/docs/`), Time-Dependent Dijkstra baseline, Greedy heuristic router, and Exact HiGHS Binary ILP implemented; 19/19 automated tests passing, 20-query comparative benchmark executed, weight sensitivity analyzed, and 7 publication-ready visualizations generated (`track_e_case_study/plots/`).
* **Track F**: **Compiler Optimization** (Mini-compiler pipeline, 5 iterative fixpoint passes, BILP pass selection, execution speedup & code size benchmarking).  
  * *Status*: **Complete (Day 8)** — Implemented full self-contained mini-compiler (`MiniLang`) including Lexer (with source line/col tracking), LL(1) recursive descent Parser, AST definitions, Semantic Analyzer (declaration-before-use symbol table), linear 3-Address Code (3AC) generator, and cycle-accurate 3AC Virtual Machine interpreter; implemented 5 optimization passes (Constant Folding, Constant Propagation, Strength Reduction, Common Subexpression Elimination, and Dead Code Elimination) wrapped in a fixpoint iteration pipeline; formulated Compiler Pass Selection as a Binary Integer Linear Programming (BILP) decision problem solved via `scipy.optimize.milp` HiGHS solver and verified against exhaustive combinatorial search ($0.00\%$ optimality gap); benchmarked across 5 representative workloads achieving up to $95.5\%$ code reduction, 600 dynamic cycles eliminated in loops, and up to $22.7\times$ execution speedup with 100% semantic output parity; 11/11 automated unit tests passing (100%), 4 publication-ready figures generated in `track_f_compiler_optimization/plots/`, and 16 academic viva Q&As documented.
* **Track G**: **xv6 Operating-System Feature Modification & Accounting** (Per-process CPU runtime accounting via `getcputime()` syscall, timer interrupt instrumentation, multi-workload benchmarks).  
  * *Status*: **Complete (Day 9)** — Cloned and inspected official MIT `xv6-riscv` kernel (`fa2ddcb7ca87a77af579380a6eafd5aff163b44f`); implemented per-process CPU runtime accounting by extending `struct proc` with `uint64 cputime;` initialized in `allocproc()` and reset in `freeproc()`; instrumented `usertrap()` and `kerneltrap()` in `kernel/trap.c` to charge ticks to active processes strictly upon timer interrupts (`which_dev == 2`); exposed feature to user space via new thread-safe system call `getcputime()` (`SYS_getcputime 23`); authored automated validation test suite `test_cputime` (5/5 checks passed: initial sanity, monotonicity, compute accumulation, fork isolation, sleeping state isolation); implemented and evaluated 3 empirical workloads: CPU-intensive (100% duty cycle), short burst (timer quantization error), and concurrent SMP (4 workers on 3 cores achieving $1.87\times$ multi-core speedup); verified regression stability against xv6 `usertests`; generated standalone git patch (`patches/0001_cputime_accounting.patch`), 4 publication-ready figures in `track_g_xv6_kernel/plots/`, and 16 academic viva Q&As documented.
* **Track H**: **DBMS Query Optimization & Index Selection** (Relational railway database, Index Selection Problem formulated as 0-1 Knapsack / Set Packing, Greedy vs Exact SciPy HiGHS ILP, query plans & benchmark).  
  * *Status*: **Complete (Day 10)** — Implemented realistic 7-table national railway reservation SQLite database (179,760 rows, 9.46 MB); formulated Index Selection Problem (ISP) as a discrete constrained optimization problem with linear coupling constraints; evaluated representative 8-query workload (Q1 to Q8) spanning range filters, multi-table joins, aggregations, subqueries, and point lookups; benchmarked 12 candidate secondary single and composite B-tree indexes; demonstrated an authentic $6.92\%$ optimality gap in the Greedy heuristic at $S_{\max} = 3.0$ MB (`['IDX_02', 'IDX_09', 'IDX_10']` vs optimal `['IDX_02', 'IDX_07']`), proven exact against combinatorial exhaustive search across 14 budgets ($0.00\%$ ILP gap); measured an $11.45\times$ speedup on transactional lookup Q8 under ILP via B-tree index seek ($1.26$ ms $\to 0.11$ ms); verified 100% query result equivalence using SHA-256 cryptographic hashing; 10/10 automated tests passing (100%), 4 publication-ready figures generated in `track_h_dbms_optimization/plots/`, and 15 academic viva Q&As documented.
* **Track I**: **Quantum Algorithms and Quantum Machine Learning** (Deutsch-Jozsa, manual elementary Bernstein-Vazirani and Grover circuits, QFT/IQFT reversibility, QPE, Shor's factoring on $N=15$, QUBO/Ising annealing, Variational Quantum Classifier vs. Classical Logistic Regression).  
  * *Status*: **Complete (Day 11)** — Implemented 7 core quantum algorithms and discrete optimization mappings on Qiskit 2.6.2; synthesized Bernstein-Vazirani and Grover's search manually using elementary gates ($H, X, CX, CZ, CCX$) with gate-by-gate explanations, depth, and gate counts; verified Grover amplitude amplification and over-rotation ($100\%$ at $N=4$, $94.43\%$ at $N=8$); verified QFT & IQFT exact reversibility ($\|U_{\text{IQFT}} U_{\text{QFT}} - I\|_2 < 6.96 \times 10^{-16}$); verified QPE exact dyadic phase recovery ($\theta = 0.375$); executed complete Shor's factoring pipeline on $N=15$ ($a=7$), extracting prime factors $[3, 5]$ via Continued Fractions; mapped 4-variable QUBO to Ising spin Hamiltonian ($0.0$ parity error) and found global ground state `1001` (energy $-8.0$) via Simulated Annealing; benchmarked Quantum Variational Classifier (VQC) against Classical Logistic Regression on Iris (Classes 0 & 1, 2 features), achieving $93.3\%$ vs $100\%$ test accuracy with an honest empirical demonstration of $282.5\times$ classical simulation overhead on CPU ($938 \text{ ms}$ vs $3.32 \text{ ms}$); 10/10 automated tests passing (100%), 5 publication-ready figures generated in `track_i_quantum_algorithms/plots/`, and 20 academic viva Q&As documented.
* **Track J**: Software-Engineering Optimization (Codebase performance optimization on $\ge 1,000$ LOC, formulated with Chapter 6 methods, profiled bottlenecks, and measured trade-offs).

---

## 2. Strict Vibe-Coding & AI Disclosure

As mandated by Section 8 of the specification, all substantial code implementations, algorithmic derivations, and experimental scripts are developed through documented AI interactions. All code changes generated by AI tools are tracked with explicit commit prefixes (`[AI:tool-name]`), and manual human interventions/corrections are separately tagged.

### AI Tools Register

| Tool Name | Model & Engine | Active Period | Assigned Tracks | Scope of Work | Current Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Antigravity AI** | Gemini 3.8 Flash (High) / Pro | Oct 30 – Present | Tracks A–J | Architecture, environment verification, planning, checklists, test harness, code generation | **Active & Verified** |
| **Claude** | Claude 3.7 Sonnet | Scheduled (Phase 2) | Track E | Cross-validation, prompt comparison, edge-case vulnerability testing | *Pending Execution* |
| **GitHub Copilot** | GPT-4o / Codex engine | Scheduled (Phase 3) | Tracks G, H | In-editor autocompletion, kernel patch verification, SQL query plan synthesis | *Pending Execution* |

### Commit Traceability Convention
* `[AI:antigravity]` — Implementation generated via Antigravity assistant prompt.
* `[AI:claude]` — Implementation or analysis generated via Claude prompt.
* `[AI:copilot]` — In-line code assistance from GitHub Copilot.
* `[MANUAL:fix]` — Human developer correction, bug fix, or live verification patch.

### Prompt Logs & Traceability Files
* Full logs of prompts, model responses, revisions, and verification notes are located in [`prompts/`](prompts/):
  * Per-track prompt history: [`prompts/track_a/`](prompts/track_a/) through [`prompts/track_j/`](prompts/track_j/)
  * Failure Log (Actual observed errors, verified fixes & engineering lessons): [`prompts/failure_log.md`](prompts/failure_log.md)
  * Two-Tool Comparison Protocol & Baseline: [`prompts/tool_comparison.md`](prompts/tool_comparison.md)

---

## 3. Verified System & Environment Status

The development environment has been fully inspected and provisioned:
* **Host Platform (Windows 11)**:
  * Python `3.13.3` with verified `numpy`, `scipy` (including `scipy.optimize.milp` HiGHS solver), `matplotlib`, and `sqlite3`.
  * Host C Compiler: `gcc 16.1.0` (MSYS2).
  * Version Control: `git 2.44+` (Active repository, verified commits).
* **Linux Subsystem (WSL2 / Ubuntu 26.04 LTS)**:
  * Native GCC: `gcc 15.2.0`
  * Build Driver: `GNU Make 4.4.1`
  * Hardware Emulator: `qemu-system-riscv64 10.2.1`
  * Cross-Compiler: `riscv64-linux-gnu-gcc 15.2.0`
  * Cross-Debugger: `gdb-multiarch 17.1`

---

## 4. Repository Directory Structure

```text
OT_Lab-8/
├── README.md                                    # Master documentation and quickstart
├── PROJECT_PLAN.md                              # Comprehensive architectural specification
├── docs/
│   ├── CHAPTER_6_COVERAGE_CHECKLIST.md          # 100% Chapter 6 syllabus mapping
│   ├── ENVIRONMENT_VERIFICATION_AND_SETUP.md    # Environment verification & toolchain guide
│   └── 14_DAY_ROADMAP_TRACKER.md                # 14-day execution tracker and milestone sign-offs
├── prompts/                                     # Complete vibe-coding prompt transcripts
│   ├── failure_log.md                           # Documented AI bugs, hallucinations & fixes
│   ├── tool_comparison.md                       # Empirical comparison of two AI tools
│   └── track_{a..j}/                            # Prompts and responses per track
├── report/                                  # Comprehensive technical report workspace
├── track_a_continuous/                          # Track A: Continuous Optimization
├── track_b_discrete/                            # Track B: Discrete Optimization & QUBO
├── track_c_quantum_optimization/                # Track C: Quantum Optimization (QAOA, VQE)
├── track_d_parallel_distributed_optimization/   # Track D: Submodular, Parallel & FedAvg/MGDA
├── track_e_case_study/                          # Track E: Main Case Study (Railway Network)
├── track_f_compiler_optimization/               # Track F: Mini-Compiler & Pass Optimization
├── track_g_xv6_kernel/                          # Track G: xv6 RISC-V Kernel Optimization
├── track_h_dbms_optimization/                   # Track H: Relational DBMS Index/Query Optimization
├── track_i_quantum_algorithms/                 # Track I: Quantum Algorithms & QML Advantage
├── track_j_software_eng/                        # Track J: Software Engineering Optimization
├── data/                                        # Shared datasets (railway, benchmarks, queries)
├── scripts/                                     # Benchmark orchestration and verification scripts
└── tests/                                       # Independent correctness test suites
```

---

## 5. Key Links & Documentation

* **Architecture & Formulation**: [`PROJECT_PLAN.md`](PROJECT_PLAN.md)
* **Chapter 6 Syllabus Coverage Checklist**: [`docs/CHAPTER_6_COVERAGE_CHECKLIST.md`](docs/CHAPTER_6_COVERAGE_CHECKLIST.md)
* **Environment Verification & Setup Instructions**: [`docs/ENVIRONMENT_VERIFICATION_AND_SETUP.md`](docs/ENVIRONMENT_VERIFICATION_AND_SETUP.md)
* **14-Day Progress & Roadmap Tracker**: [`docs/14_DAY_ROADMAP_TRACKER.md`](docs/14_DAY_ROADMAP_TRACKER.md)
* **Vibe-Coding Failure Log**: [`prompts/failure_log.md`](prompts/failure_log.md)
* **AI Tool Comparison Study**: [`prompts/tool_comparison.md`](prompts/tool_comparison.md)

---

## 6. Verification & Academic Integrity Notice

In strict adherence to Section 10 of the assignment specification:
1. No optimization claim is made unless supported by measured empirical data.
2. Baselines, stopping criteria, hardware, and seeds are kept uniform and fair.
3. Quantum execution differentiates clearly between statevector simulation, shot-noise sampling, and noisy models.
4. Correctness of transformed code, modified query plans, and kernel states are independently tested with regression suites.
