# Track B: Discrete Optimization — Day 5 Prompt & Interaction Log

> **Date**: Day 5  
> **Course**: Optimization Techniques — Assignment 8  
> **Module**: Track B (Discrete Optimization & QUBO)  
> **AI Coding Agent**: Antigravity AI (Gemini 3.8 Flash / Pro)  
> **Status**: Successfully Completed & Fully Verified

---

## 1. Prompt Record

### User Instruction (Day 5)
The user directed the agent to continue working in the existing repository with the following instructions:
1. Strictly **DO NOT** execute Git commit, push, pull, merge, rebase, reset, or history-rewriting commands. User handles Git personally.
2. Preserve all existing Track A and Track E files and results.
3. Conduct Track A final audit addressing:
   - Analytical minima of quadratic functions and explanation of negative minimum values.
   - Stopping criteria for Momentum on Rosenbrock (final gradient norm and objective value).
   - Verification of the mini-batch variance experiment's sampling procedure and empirical variance calculation.
   - Verification of Fisher information and Hessian-vector product implementations against numerical checks.
   - Documentation of iteration limits, learning rates, stopping tolerances, and initial conditions.
4. Implement Track B under `track_b_discrete_optimization/`:
   - A. Greedy optimization (with local selection rule and documented suboptimal counterexample).
   - B. Integer Linear Programming using binary decision variables and SciPy's HiGHS solver (`milp`).
   - C. Transparent Branch-and-Bound (showing branching, Dantzig LP bounds, and pruning conditions).
   - D. Dynamic Programming for 0/1 Knapsack (state definition, recurrence, base cases, backtracking reconstruction, time/space complexity).
   - E. QUBO and Ising model formulation (binary slack variables, penalty terms, penalty coefficient selection rule $P > \max v_i$, spin conversion $s_i = 2x_i - 1$, classical exhaustive verification).
5. Experiments: Multi-instance benchmark across problem scales ($N \in [3, 200]$) and QUBO penalty sensitivity study; generate 4 publication-ready plots.
6. Automated unit tests covering Greedy feasibility, counterexample, ILP optimality, B&B agreement, DP agreement, QUBO exhaustive search, Ising energy parity, and invalid inputs.
7. Documentation: `methodology.md`, `experimental_analysis.md`, `viva_questions.md` ($\ge 15$ Q&As), `README.md`, and updates to root tracking files.

---

## 2. Track A Final Audit Resolutions

1. **Analytical Quadratic Minimum Value**:
   - The canonical quadratic form is $f(x) = \frac{1}{2} x^T A x - b^T x$.
   - The gradient is $\nabla f(x) = A x - b$, yielding the stationary point $x^* = A^{-1} b$.
   - The minimum value is $f(x^*) = \frac{1}{2} (A^{-1} b)^T A (A^{-1} b) - b^T (A^{-1} b) = -\frac{1}{2} b^T A^{-1} b$.
   - Since $A$ is positive-definite, $A^{-1}$ is positive-definite, which implies $-\frac{1}{2} b^T A^{-1} b < 0$ whenever $b \neq \mathbf{0}$.
   - The negative minimum values (e.g. $-2.140573$ for Convex Quadratic, $-0.891778$ for Strongly Convex) are mathematically exact and intentional.

2. **Stopping Criteria for Momentum on Rosenbrock**:
   - Maximum iterations: `max_iters = 1000`.
   - The optimizer reached the iteration budget of 1000 with final objective value $2.13 \times 10^{-8}$ (rounded to 0.000000 in report tables) and final gradient norm $1.19 \times 10^{-4}$.
   - Because $1.19 \times 10^{-4} > 1.0 \times 10^{-6}$ (stopping tolerance), `converged` was accurately recorded as `False`.

3. **Mini-Batch Variance Sampling Procedure**:
   - In `run_noisy_study.py`, the empirical gradient variance was updated to simulate explicit draws: for each of 200 mini-batches, $B$ independent noise samples $\xi_i \sim \mathcal{N}(0, \sigma^2 I)$ are generated and averaged: $\bar{\xi} = \frac{1}{B} \sum_{i=1}^B \xi_i$.
   - The empirical variance across batches matched theoretical predictions ($\mathrm{Var} = \sigma^2 / B$) with $< 2\%$ relative deviation.

4. **Curvature Numerical Checks**:
   - Implemented `CurvatureApproximations.numerical_hessian(grad_fn, x, eps=1e-5)` using centered differences.
   - Enhanced `test_10_hessian_vector_product_accuracy` to verify that both Pearlmutter's HVP and the full numerical Hessian match the analytical Hessian to within $10^{-5}$ relative Frobenius norm.

---

## 3. Implementation Log: Track B (Discrete Optimization)

### Step 1: Core Algorithm Modules
- `track_b_discrete_optimization/src/problem.py`: `KnapsackProblem`, `KnapsackSolution`, `create_known_counterexample()`, `generate_random_instance()`.
- `track_b_discrete_optimization/src/greedy_solver.py`: Efficiency density ratio heuristic $r_i = v_i / w_i$ with $\mathcal{O}(n \log n)$ sorting.
- `track_b_discrete_optimization/src/ilp_solver.py`: Binary Integer Linear Programming via `scipy.optimize.milp` with HiGHS.
- `track_b_discrete_optimization/src/branch_and_bound.py`: Transparent depth-first Branch-and-Bound with Dantzig fractional LP relaxation upper bounds.
- `track_b_discrete_optimization/src/dp_solver.py`: 2D Dynamic Programming table $DP[i, w]$ with backtracking reconstruction.
- `track_b_discrete_optimization/src/qubo_ising.py`: QUBO Hamiltonian with binary slack variables, exact Ising spin mapping ($s_i = 2x_i - 1$), penalty selection $P > \max v_i$, and exhaustive classical ground-state solver.

### Step 2: Automated Unit Testing
- Created `track_b_discrete_optimization/tests/test_discrete_optimizers.py`.
- 7 test cases covering all requirements:
  - `test_01_greedy_feasibility_and_counterexample`: Feasibility and 27.27% gap on counterexample.
  - `test_02_ilp_optimality_on_manual_instance`: Exact match on hand-calculated 4-item problem.
  - `test_03_branch_and_bound_agreement_with_ilp`: Exact agreement across random seeds.
  - `test_04_dp_agreement_with_ilp`: Exact agreement across random seeds.
  - `test_05_qubo_exhaustive_and_constraint_satisfaction`: Feasibility and optimality on small instance.
  - `test_06_qubo_to_ising_conversion_energy_parity`: Exact energy parity ($< 10^{-6}$) between QUBO and Ising models across random binary states.
  - `test_07_invalid_inputs_handling`: Exception validation on negative/empty parameters.

### Step 3: Experimental Benchmarking
- `run_discrete_comparison.py`: Benchmarked 5 algorithms across 9 problem scales ($N \in [3, 200]$); output JSON, CSV, and markdown reports.
- `run_qubo_penalty_study.py`: Evaluated penalty factor $\alpha \in [0.05, 5.0]$; demonstrated the sharp phase transition at $\alpha = 1.0$ ($P = \max v_i$) from infeasible overpacking to exact global optimality.

### Step 4: Visualizations & Documentation
- `visualize_results.py`: Rendered 4 publication figures in `plots/`:
  - `01_objective_value_comparison.png`
  - `02_runtime_vs_problem_size.png`
  - `03_greedy_optimality_gap.png`
  - `04_qubo_penalty_and_energy_landscape.png`
- Authored `docs/methodology.md`, `docs/experimental_analysis.md`, `docs/viva_questions.md` (16 Q&As), and `README.md`.
- Updated root `README.md`, `docs/CHAPTER_6_COVERAGE_CHECKLIST.md`, and `docs/14_DAY_ROADMAP_TRACKER.md`.

---

## 4. Real Observed Engineering Bugs & Solutions

During Day 5 implementation, two genuine engineering issues occurred and were automatically resolved:

1. **LaTeX Math Escaped Backslash Warning**:
   - *Issue*: Python 3.13 raised `SyntaxWarning: invalid escape sequence '\s'` and `'\i'` in docstrings containing mathematical notation in `problem.py` and `qubo_ising.py`.
   - *Fix*: Prefixed all docstrings containing backslashes with raw string literals `r"""..."""`.

2. **QUBO-to-Ising Matrix Representation Mismatch**:
   - *Issue*: `test_06_qubo_to_ising_conversion_energy_parity` failed with `AssertionError: 25.0 != 825.0 (800.0 difference)`.
   - *Root Cause*: In `build_qubo_matrix`, the off-diagonal entries were placed symmetrically ($Q_{ij} = Q_{ji} = 2 P a_i a_j$), while `qubo_to_ising` and the test energy evaluation assumed an upper-triangular matrix where the pair coefficient $2 P a_i a_j$ appears only once ($i < j$). This caused the pair penalty terms to be doubled in the Ising conversion.
   - *Fix*: Standardized $Q$ to a strictly upper-triangular matrix with $Q_{ij} = 2 P a_i a_j$ for $i < j$ and $Q_{ji} = 0$, with corresponding spin coupling $J_{ij} = J_{ji} = Q_{ij}/4$ and local fields $h_i = Q_{ii}/2 + \sum_{j \neq i} Q_{\min(i,j), \max(i,j)}/4$. Rerunning `test_06` confirmed exact numerical energy parity ($< 10^{-10}$ difference).

---

## 5. Verification Checklist
- Track A tests passing: **11/11 OK (0.094s)**
- Track B tests passing: **7/7 OK (0.767s)**
- Track E tests passing: **19/19 OK (1.458s)**
- Total repository unit tests passing: **37/37 OK (100% pass rate)**
- Git operations: **Zero git commit or push commands executed**.

