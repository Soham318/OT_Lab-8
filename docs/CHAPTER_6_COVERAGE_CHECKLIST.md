# Mandatory Chapter 6 & Compulsory Tracks Coverage Checklist

> **Assignment**: Optimization Techniques — Lab Assignment 8  
> **Source of Truth**: Official Assignment 8 PDF (Section 5 & 6)  
> **Status**: Verified Planning Matrix (100% Chapter 6 Syllabus Mapped)  

---

## 1. Chapter 6 Syllabus Mapping Matrix

Every method, algorithm, and theoretical concept taught in Chapter 6 is explicitly mapped below to its corresponding track, implementation module, verification test, and benchmark output.

| Chapter 6 Syllabus Topic | Sub-topics / Required Coverage | Track | Target Module / Script | Verification & Test Method | Target Deliverable / Metric |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Foundations of ML Optimization** | ML as optimization (parameters, loss, regularization) | Track A | `track_a_continuous_optimization/src/neural_net.py` | Loss curve minimization on linear/logistic models | Training loss, L1/L2 regularization weight decay |
| | Continuous vs. Discrete optimization landscapes | Track A & B | `track_a_continuous_optimization/src/landscapes.py` | Objective landscape grid evaluation | Smooth vs. combinatorial step comparison |
| | Convex vs. Non-convex landscapes | Track A | `track_a_continuous_optimization/src/landscapes.py` | Hessian positive-definiteness check | Eigenvalues, condition number |
| | Local minima, global minima, saddle points | Track A | `track_a_continuous_optimization/src/landscapes.py` | Analytical stationary point classification | Contour plots & convergence paths from diverse inits |
| | Quantum computing concepts & role in QML | Track C & I | `track_c_quantum_opt/` & `track_i_quantum_algos/` | State vector fidelity and cost expectation | Variational energy vs. parameter angle |
| **Continuous Optimization** | Gradient Descent (GD, batch) | Track A | `track_a_continuous_optimization/src/optimizers.py` | Convergence test on quadratic benchmark | Loss vs. iteration, wall-clock time |
| | Stochastic Gradient Descent (SGD) | Track A | `track_a_continuous_optimization/src/optimizers.py` | Convergence with mini-batches on noisy loss | Variance across batches, final objective |
| | Mini-batch SGD | Track A | `track_a_continuous_optimization/src/optimizers.py` | Batch size scaling ($B \in [1, 4, 16, 64]$) | Epoch runtime vs. gradient variance |
| | Momentum Optimizer | Track A | `track_a_continuous_optimization/src/optimizers.py` | Ravine / ill-conditioned valley traversal | Oscillation damping comparison |
| | Nesterov Accelerated Gradient (NAG) | Track A | `track_a_continuous_optimization/src/optimizers.py` | Convergence on ill-conditioned quadratics | Look-ahead gradient trajectory check |
| | AdaGrad | Track A | `track_a_continuous_optimization/src/optimizers.py` | Sparse feature optimization | Accumulator decay and step-size adaptation |
| | RMSProp | Track A | `track_a_continuous_optimization/src/optimizers.py` | Non-stationary non-convex benchmark | Moving average gradient scaling |
| | Adam | Track A | `track_a_continuous_optimization/src/optimizers.py` | Benchmark against Rosenbrock & MLP loss | First & second moment bias correction verification |
| | Second-Order: Newton's Method | Track A | `track_a_continuous_optimization/src/second_order.py` | Exact Hessian inversion on quadratic | Quadratic convergence rate ($\mathcal{O}(\epsilon^2)$) |
| | Second-Order: Gauss-Newton | Track A | `track_a_continuous_optimization/src/second_order.py` | Non-linear least squares fit | Jacobian outer product $J^T J$ approximation |
| | Backpropagation (decoupled from optimizer) | Track A | `track_a_continuous_optimization/src/neural_net.py` | Finite-difference numerical gradient check | $\| \nabla_{\text{analytical}} - \nabla_{\text{numerical}} \|_2 = 4.00 \times 10^{-12}$ |
| | Curvature Approximations: Fisher Information | Track A | `track_a_continuous_optimization/src/curvature.py` | Empirical Fisher vs. true Hessian | Trace and eigenvalue spectral error |
| | Curvature Approximations: Diagonal / Low-Rank | Track A | `track_a_continuous_optimization/src/curvature.py` | Memory footprint and inversion time | Storage reduction vs. curvature fidelity |
| | Curvature Approximations: Hessian-Vector Products | Track A | `track_a_continuous_optimization/src/curvature.py` | Pearlmutter trick / finite-difference HVP | $\| H v - \frac{\nabla(x + \epsilon v) - \nabla(x - \epsilon v)}{2\epsilon} \|$ |
| | Convergence: Convex vs. Strongly Convex vs. Non-Convex | Track A | `track_a_continuous_optimization/experiments/run_landscape_comparison.py` | Theoretical rate check ($\mathcal{O}(1/k)$, $\mathcal{O}(e^{-ck})$) | Log-linear convergence plots |
| | Step-size and optimizer tuning | Track A | `track_a_continuous_optimization/experiments/run_sensitivity_study.py` | Learning rate grid sweep ($\eta \in [10^{-4}, 1.0]$) | Hyperparameter sensitivity surface |
| | Noisy objectives | Track A | `track_a_continuous_optimization/experiments/run_noisy_study.py` | Additive Gaussian gradient noise | Robustness and asymptotic error bounds |
| **Discrete Optimization** | Greedy Methods | Track B | `track_b_discrete_optimization/src/greedy_solver.py` | Suboptimal trap verification (27.27% gap) | Approximation ratio vs. exact optimum |
| | Integer Linear Programming (ILP) | Track B | `track_b_discrete_optimization/src/ilp_solver.py` | Exact solver via HiGHS (`scipy.optimize.milp`) | Optimal objective, execution time, relaxation gap |
| | Branch-and-Bound | Track B | `track_b_discrete_optimization/src/branch_and_bound.py` | Custom B&B tree search with LP relaxation bounds | Tree depth, pruned nodes count |
| | Dynamic Programming | Track B | `track_b_discrete_optimization/src/dp_solver.py` | Exact memoized DP on Knapsack benchmark | State space size, runtime scaling |
| | Combinatorial Application: Knapsack | Track B | `track_b_discrete_optimization/src/problem.py` | Capacity constraint satisfaction | Value, weight, capacity utilization |
| | QUBO & Ising Formulation | Track B | `track_b_discrete_optimization/src/qubo_ising.py` | Binary-to-spin mapping $s_i = 2x_i - 1$ | Energy spectrum identity between QUBO and Ising |
| | Penalty Terms for Constraints | Track B | `track_b_discrete_optimization/src/qubo_ising.py` | Slack variable expansion & penalty multiplier $P > \max v_i$ | Phase transition check on unconstrained minimizer |
| **Quantum Optimization** | QAOA (Quantum Approx. Opt. Algorithm) | Track C | `track_c_quantum_optimization/src/qaoa.py` | Solving Max-Cut with multi-depth QAOA ($p \in \{1, 2, 3\}$) | Approximation ratio vs. circuit depth $p$ ($75\% \to 100\%$ on $C_4$) |
| | VQE (Variational Quantum Eigensolver) | Track C | `track_c_quantum_optimization/src/vqe.py` | Ground state energy of TFIM & Heisenberg XXZ spin chains | Energy error against exact Hermitian matrix diagonalization ($0.47\%$ on TFIM) |
| | PQCs & Hardware-Efficient Ansatzes | Track C | `track_c_quantum_optimization/src/circuits.py` | Parameterized rotations ($R_y, R_z$) and $CX$ entangling layers | Circuit depth, parameter tracking, statevector simulation |
| | Parameter-Shift Rule | Track C | `track_c_quantum_optimization/src/gradients.py` | Exact analytical gradient computation on circuit ($\pm \pi/2$ shifts) | Shift difference vs. centered finite difference error ($3.86 \times 10^{-11}$) |
| | SPSA Optimizer | Track C | `track_c_quantum_optimization/src/gradients.py` | Simultaneous 2-measurement perturbation under shot noise | Convergence iterations & $12\times$ fewer circuit evaluations vs. parameter-shift GD |
| | Quantum Natural Gradient (QNG) | Track C | `track_c_quantum_optimization/src/qng.py` | Fubini-Study metric tensor with Levenberg-Marquardt regularization | Geometry-aware optimization on quantum state manifold |
| | Barren Plateaus Study | Track C | `track_c_quantum_optimization/src/barren_plateaus.py` | Variance of partial derivative vs. qubit count $n \in [2, 7]$ | $\text{Var}[\partial_\theta \langle H \rangle] \propto 2^{-n}$ confirmation |
| | Finite-shot measurement noise | Track C | `track_c_quantum_optimization/src/barren_plateaus.py` | Shots $S \in [50, 10000]$ vs. statevector expectation | Empirical variance of expectation value $\propto 1/S$, $\sigma \propto 1/\sqrt{S}$ |
| | Hardware noise models | Track C | `track_c_quantum_opt/noise_study.py` | Depolarizing and amplitude damping channel | Solution quality degradation vs. error rate |
| | QUBO Embedding on Annealing Hardware | Track C | `track_c_quantum_opt/annealing_limits.py` | Minor embedding graph density limits | Chimera/Pegasus graph physical qubit overhead |
| **Submodular Optimization** | Diminishing Returns Property | Track D | `track_d_submodular_parallel/submodular.py` | Formal condition test $\Delta(e \mid A) \ge \Delta(e \mid B)$ | Empirical monotonicity and submodularity tests |
| | Greedy Selection with Guarantee | Track D | `track_d_submodular_parallel/submodular.py` | Compare against optimal brute force subset | Verification of $(1 - 1/e) \approx 63.2\%$ bound |
| **Parallel Optimization** | Makespan & Load Balancing | Track D | `track_d_submodular_parallel/parallel_prog.py` | Work stealing vs. static partition benchmark | Core idle time and variance across threads |
| | Speedup & Parallel Efficiency | Track D | `track_d_submodular_parallel/parallel_prog.py` | Multi-core scaling ($P \in [1, 2, 4, 8]$ cores) | Speedup $S_P = T_1 / T_P$, Efficiency $E_P = S_P / P$ |
| | Amdahl's & Gustafson's Laws | Track D | `track_d_submodular_parallel/parallel_prog.py` | Non-linear regression fit on measured speedups | Extrapolated serial fraction $s$ |
| | Data, Model, Pipeline Parallelism | Track D | `track_d_submodular_parallel/parallel_prog.py` | Execution timeline breakdown | Inter-process communication and synchronization cost |
| **Distributed & Multi-Task** | Federated Learning (FedAvg) | Track D | `track_d_submodular_parallel/fedavg.py` | Local epochs $E \in [1, 10]$, communication rounds $R$ | Global test loss vs. total communication payload |
| | Multi-Task: MGDA | Track D | `track_d_submodular_parallel/multitask.py` | Min-norm gradient on convex hull of task losses | Pareto-optimal gradient trajectory |
| | Multi-Task: GradNorm | Track D | `track_d_submodular_parallel/multitask.py` | Gradient norm balancing across 2 tasks | Loss balance comparison vs. uniform weights |
| **Strategy Selection** | Formal Selection Framework | Track E | `track_e_case_study/strategy_selection.py` | Decision table matching variable type & size | Formal justification matrix in report |

---

## 2. Compulsory Tracks (A to J) Mapping

| Track | Primary Objective | Baseline Method | Optimized Method(s) | Correctness Verification |
| :--- | :--- | :--- | :--- | :--- |
| **Track A** | Continuous optimization comparisons | Standard Gradient Descent | Adam, Newton, Gauss-Newton, NAG, RMSProp | **VERIFIED COMPLETE**: 11/11 unit tests passing, 8 first-order + 2 second-order optimizers, 5 landscapes, decoupled 2-layer MLP backpropagation (gradient check error $4.00 \times 10^{-12}$), 6 publication plots, 16 viva Q&As |
| **Track B** | Combinatorial optimization & QUBO | Naive Greedy Selection | Branch-and-Bound, ILP, DP, QUBO Ising model | **VERIFIED COMPLETE**: 7/7 unit tests passing, Greedy 27.27% gap counterexample, Dantzig LP Branch-and-Bound, 2D DP backtracking, SciPy HiGHS ILP (N=200), classical QUBO with slack variables, 4 publication plots, 16 viva Q&As |
| **Track C** | Quantum optimization on QUBO & spin models | Classical Exact / Greedy / Finite Difference | QAOA ($p=1, 2, 3$), VQE, Parameter-Shift, SPSA, QNG | **VERIFIED COMPLETE**: 8/8 unit tests passing, QAOA Max-Cut multi-depth ($p=1, 2, 3$, 100% approximation ratio on $C_4$), VQE ground state on TFIM ($0.47\%$ error) & Heisenberg XXZ ($1.30\%$ error) vs exact Hermitian matrix diagonalization, Parameter-Shift exactness ($3.86 \times 10^{-11}$ error), SPSA ($23.2\times$ faster runtime under shot noise, $2$ circuits/step), Fubini-Study QNG, empirical Central Limit Theorem shot noise scaling $\mathcal{O}(1/S)$, and Barren Plateau exponential variance decay $\mathcal{O}(2^{-n})$ across $n \in [2, 7]$ qubits, 5 publication plots, 16 viva Q&As |
| **Track D** | Submodular, parallel, distributed | Single-thread static run | Work-stealing multiprocessing, FedAvg, MGDA | Bound check $(1 - 1/e)$, convergence to centralized |
| **Track E** | Railway route & transfer optimization | Static Dijkstra Shortest Path | Earliest-Arrival Greedy, Multi-Objective ILP (HiGHS) | **VERIFIED COMPLETE**: 19/19 tests pass, 20-query benchmark, 7 plots, ILP proven optimal (100%), sensitivity analysis |
| **Track F** | Mini-compiler optimization passes | Unoptimized 3AC IR code | Constant Folding/Prop, DCE, CSE, ILP Reg Alloc | Bytecode execution parity on test programs |
| **Track G** | xv6 operating-system optimization | Stock xv6 Round-Robin Scheduler | Priority / Stride Scheduler + Dynamic Aging | xv6 clean boot, passing `usertests`, 3 workloads |
| **Track H** | DBMS query plan & index selection | Full table scan / unindexed | Knapsack/ILP Index Selection, Greedy Selection | Identical query result row counts & checksums |
| **Track I** | Quantum algorithms & QML advantage | Classical Linear Search / Classical MLP | Grover's Search, Deutsch-Jozsa, Variational QNN | Statevector fidelity, gate counts vs classical steps |
| **Track J** | Software engineering optimization | Full sequential test execution | Minimum Set Cover ILP & Greedy Test Selection | 100% statement coverage preservation check |

