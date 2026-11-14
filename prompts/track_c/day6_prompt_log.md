# Track C: Quantum Optimization — Day 6 Prompt & Interaction Log

> **Date**: Day 6  
> **Course**: Optimization Techniques — Assignment 8  
> **Module**: Track C (Quantum Optimization)  
> **AI Coding Agent**: Antigravity AI (Gemini 3.8 Flash / Pro)  
> **Status**: Successfully Completed & Fully Verified  
> **Quantum Simulator**: Local Statevector Simulator (`Qiskit 2.6.2`, no quantum hardware claimed)

---

## 1. Prompt Record

### User Instruction (Day 6)
The user directed the agent to continue working in the existing repository with the following instructions:
1. Strictly **DO NOT** execute Git commit, push, pull, merge, rebase, reset, or history-rewriting commands. User handles Git personally.
2. Preserve all existing Track A, B, and E implementations and results.
3. Use a local quantum simulator. First inspect installed dependencies and install only what is necessary.
4. Part 1 — Audit Track B QUBO:
   - Verify binary slack-variable encoding.
   - Verify penalty coefficient is mathematically sufficient for the encoded problem.
   - Derive a valid sufficient penalty bound ($P > \sum v_i$) or state limitations of chosen bound ($P > \max v_i$).
   - Exhaustively enumerate small instances and compare QUBO ground state with constrained knapsack optimum.
   - Verify binary-to-Ising energy equivalence.
   - Rerun Track B tests.
5. Part 2 — Implement Track C: Quantum Optimization:
   - A. Parameterized Quantum Circuits (rotations $R_x, R_y, R_z$, entanglement $CX$, depth, parameter count).
   - B. QAOA on Max-Cut (graph, cost Hamiltonian $H_C$, mixer $H_M$, depth $p \in \{1, 2, 3\}$, classical optimizer, comparison to classical optimum).
   - C. VQE on spin models (TFIM, Heisenberg XXZ, compare ground state energy to exact Hermitian diagonalization).
   - D. Parameter-shift rule vs centered finite differences vs SPSA under shot noise.
   - E. Quantum Natural Gradient (QNG) using Fubini-Study metric tensor with Levenberg-Marquardt regularization.
   - F. Empirical studies on finite measurement shot noise ($\mathcal{O}(1/S)$) and Barren Plateaus ($\mathcal{O}(2^{-n})$ across $n \in [2, 7]$ qubits).
6. Experiments: Multi-depth QAOA, VQE spin models, gradient comparison, and noise/barren plateaus; generate 5 publication-ready plots.
7. Automated unit tests covering ansatz construction, QAOA Max-Cut, VQE ground state, parameter-shift exactness, SPSA convergence, QNG metric tensor, shot noise variance, and invalid inputs.
8. Documentation: `methodology.md`, `experimental_analysis.md`, `viva_questions.md` ($\ge 15$ Q&As), `README.md`, and updates to root tracking files.

---

## 2. Track B QUBO Audit Resolutions

1. **Binary Slack Variable Expansion**:
   - For inequality constraint $\sum w_i x_i \le W$, slack $s \in [0, W]$ is expanded into $K = \lfloor \log_2 W \rfloor + 1$ binary variables:
     $$s = \sum_{k=0}^{K-2} 2^k y_k + \left(W - \sum_{k=0}^{K-2} 2^k\right) y_{K-1}$$
   - This exact binary representation preserves non-negative integer coverage without allowing slack values exceeding $W$.

2. **Penalty Coefficient Sufficiency Proof**:
   - *Local Heuristic Bound*: $P > \max_i v_i$. If adding item $j$ violates capacity by 1 unit, the net energy change is $\Delta E = -v_j + P(2 \cdot \text{slack} + 1) \ge -v_j + P > 0$. Thus, single-item overfill is penalized.
   - *Globally Sufficient Universal Bound*: $P > \sum_{i=1}^n v_i$. If an unconstrained selection includes all items with aggregate capacity violation $\Delta w \ge 1$, the penalty is $P(\Delta w)^2 \ge P$. Since $\sum v_i$ is the maximum possible objective value achievable, setting $P > \sum v_i$ guarantees that every infeasible bitstring has higher energy than the empty set (energy 0), making the global minimum unconditionally feasible.
   - Documented both bounds in `qubo_ising.py` and `track_b_discrete_optimization/docs/methodology.md`.

3. **Binary-to-Ising Spin Energy Parity**:
   - Re-verified transformation $s_i = 2x_i - 1 \iff x_i = \frac{1 + s_i}{2}$.
   - Verified across all $2^N$ states that $|H_{\text{Ising}}(\mathbf{s}) - E_{\text{QUBO}}(\mathbf{x})| < 10^{-10}$.
   - Track B test suite rerun: **7/7 tests passed cleanly**.

---

## 3. Implementation Log: Track C (Quantum Optimization)

### 3.1 Dependencies & Environment
- Inspected installed packages: Python 3.13.3 with NumPy 2.5.2, SciPy 1.18.1, Matplotlib 3.11.1. Qiskit was missing.
- Installed `qiskit==2.6.2` (including `rustworkx==0.18.1`, `dill==0.4.1`, `stevedore==5.10.0`) using `BypassSandbox: true`.
- Local statevector simulation verified working inside standard sandbox.

### 3.2 Core Modules Created
- `track_c_quantum_optimization/src/circuits.py`: Hardware-efficient ansatz $[R_y - R_z - CX]$ with ParameterVector binding, statevector evaluation, and deterministic probability sampling.
- `track_c_quantum_optimization/src/qaoa.py`: QAOA Max-Cut solver with Pauli cost Hamiltonian $H_C = \sum_{(u,v)} \frac{w}{2}(I - Z_u Z_v)$, mixer $H_M = \sum X_u$, and COBYLA classical optimization.
- `track_c_quantum_optimization/src/vqe.py`: VQE solver with TFIM ($Z_i Z_{i+1} + X_i$) and Heisenberg XXZ ($XX + YY + \Delta ZZ$) Hamiltonians, exact Hermitian matrix diagonalization (`np.linalg.eigvalsh`), and BFGS/COBYLA optimizers.
- `track_c_quantum_optimization/src/gradients.py`: Exact Parameter-Shift Rule ($\pm \pi/2$ macro displacement), centered finite differences, and SPSA optimizer (Spall 2-measurement rule).
- `track_c_quantum_optimization/src/qng.py`: Quantum Natural Gradient computing Fubini-Study metric tensor $g_{ij} = \text{Re}[\langle \partial_i \psi | \partial_j \psi \rangle - \langle \partial_i \psi | \psi \rangle \langle \psi | \partial_j \psi \rangle]$ with Levenberg-Marquardt regularization $(g + \lambda I)^{-1}$.
- `track_c_quantum_optimization/src/barren_plateaus.py`: Finite shot noise scaling study ($S \in [50, 10000]$) and Barren Plateau gradient variance decay across $n \in [2, 7]$ qubits.
- `track_c_quantum_optimization/src/visualize_results.py`: Publication-quality Matplotlib figures.

---

## 4. Empirical Benchmark Results

1. **QAOA Multi-Depth Scaling**:
   - 4-Node Cycle: $p=1 \to \alpha = 0.7500$ (runtime 91 ms), $p=2 \to \alpha = 0.9994$ (runtime 200 ms), $p=3 \to \alpha = 1.0000$ (runtime 222 ms). At $p=3$, QAOA discovers the true optimal cut $4.0$ with $100\%$ expectation.
   - 5-Node Graph: $p=1 \to \alpha = 0.5946$ (runtime 150 ms), $p=2 \to \alpha = 0.7581$ (runtime 1213 ms).
2. **VQE Ground State Accuracy vs Exact Diagonalization**:
   - TFIM (3 Qubits): $E_{\text{VQE}} = -2.9948$, $E_{\text{exact}} = -3.0090$ (**$0.47\%$ relative error**).
   - TFIM (4 Qubits): $E_{\text{VQE}} = -4.1064$, $E_{\text{exact}} = -4.1456$ (**$0.95\%$ relative error**).
   - Heisenberg XXZ (3 Qubits): $E_{\text{VQE}} = -3.3284$, $E_{\text{exact}} = -3.3723$ (**$1.30\%$ relative error**).
   - Heisenberg XXZ (4 Qubits): $E_{\text{VQE}} = -5.1623$, $E_{\text{exact}} = -5.4243$ (**$4.83\%$ relative error**).
3. **Quantum Gradient Comparisons**:
   - Parameter-Shift vs Centered Finite Differences: Mean relative error = **$3.86 \times 10^{-11}$**.
   - SPSA vs GD under shot noise ($S=500$): SPSA requires strictly 2 circuits/step ($200$ total vs $2,400$ for GD), executing in $146.8$ ms vs $3,404.9$ ms (**$23.2\times$ faster**) while reaching $93.4\%$ of optimal energy.
4. **Shot Noise & Barren Plateaus**:
   - Finite Shot Noise: Variance decays from $0.0198$ ($S=50$) down to $0.000112$ ($S=10000$), strictly matching theoretical $1/S$ decay and $\sigma \propto 1/\sqrt{S}$.
   - Barren Plateaus: Gradient variance decays exponentially across qubits:
     $n=2: 0.1579 \implies n=3: 0.0843 \implies n=4: 0.0400 \implies n=5: 0.0104 \implies n=6: 0.0076 \implies n=7: 0.0033$.
     Decay closely follows theoretical $\mathcal{O}(2^{-n})$ Haar measure bound.

---

## 5. Errors Encountered & Resolved (Recorded in Failure Log)

1. **Qiskit 2.x `sample_counts()` API Deprecation**:
   - Qiskit 2.x removed `seed` argument from `QuantumState.sample_counts()`.
   - Fix: Sampled directly from statevector probabilities $\mathbf{p} = |\boldsymbol{\psi}|^2$ with `np.random.default_rng(seed).choice()`. Logged as Case 7 in `failure_log.md`.
2. **Barren Plateau Gradient Evaluation Bottleneck**:
   - Initially computed full gradient $\nabla_{\boldsymbol{\theta}} \langle H \rangle$ ($d=112$ parameters for $n=7$, requiring $6,720$ circuit evaluations), stalling execution.
   - Fix: Optimized to evaluate partial derivative of parameter $\theta_0$ only via parameter shift ($2$ evaluations per circuit), achieving a $112\times$ speedup (runtime 7.03s). Logged as Case 8 in `failure_log.md`.
3. **LaTeX Escape Sequences in Docstrings**:
   - Backslashes in mathematical docstrings produced syntax warnings in Python 3.13.
   - Fix: Prefixed docstrings with raw string literal `r"""..."""`.

---

## 6. Verification Status

- Automated Unit Tests: **8/8 passed** in 0.51s (`track_c_quantum_optimization/tests/test_quantum_optimization.py`).
- Publication Plots Generated: 5 figures in `track_c_quantum_optimization/plots/`.
- Git Status: Clean working branch, **zero Git commits or pushes executed**.

