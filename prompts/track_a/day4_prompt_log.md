# Track A: Continuous Optimization — Day 4 Prompt & Interaction Log

> **Date**: Day 4  
> **Course**: Optimization Techniques — Assignment 8  
> **Module**: Track A (Continuous Optimization)  
> **AI Coding Agent**: Antigravity AI (Gemini 3.8 Flash / Pro)  
> **Status**: Successfully Completed & Fully Verified

---

## 1. Prompt Record

### User Instruction (Day 4)
The user instructed the autonomous AI coding agent to implement Day 4: Track A: Continuous Optimization with the following constraints:
1. Preserve all existing Track E work; do not overwrite or delete existing working files.
2. Audit Day 3 Track E (consistency of objective functions, feasibility constraints, ILP agreement, optimality gap calculation, reproducibility).
3. Implement practical Track A continuous optimization under `track_a_continuous_optimization/`:
   - 8 first-order gradient methods: Batch GD, SGD, Mini-batch GD, Momentum, NAG, AdaGrad, RMSProp, Adam.
   - 2 second-order methods: Damped Newton's Method with Levenberg-Marquardt spectral regularisation and Gauss-Newton for non-linear least squares.
   - Decoupled analytical backpropagation on a 2-layer MLP with finite-difference numerical verification ($< 10^{-6}$ error).
   - Curvature approximations: Empirical Fisher Information vs. NLL Hessian, Low-rank BFGS update, Pearlmutter Hessian-Vector Products (HVP).
4. Run empirical experiments across $\ge 3$ objective landscapes (Convex Quadratic, Strongly Convex Quadratic, Rastrigin Multimodal, Rosenbrock Valley, Non-Linear Least Squares).
5. Conduct step-size sensitivity study ($\eta$ sweep) and stochastic noise analysis ($\sigma$ sweep, mini-batch variance reduction $B \in [1, 4, 16, 64]$).
6. Author complete documentation: `docs/methodology.md`, `docs/experimental_analysis.md`, `docs/viva_questions.md` ($\ge 15$ Q&As), `README.md`.
7. Generate publication-ready Matplotlib plots in `plots/`.
8. Complete automated test suite with 100% pass rate.
9. Strictly **DO NOT** run git commit or push; user handles Git operations personally.

---

## 2. Implementation & Execution Log

### Step 1: Track E Audit
- Executed `python -m unittest discover -s track_e_case_study/tests -v`.
- Result: 19/19 tests passed in 1.66s.
- Confirmed objective function alignment ($Z = \alpha \cdot T_{\text{travel}} + \beta \cdot T_{\text{wait}} + \gamma \cdot N_{\text{transfers}}$), feasibility rules, exact agreement between ILP objective and reconstructed itinerary, and optimality gap formulations.

### Step 2: Implementation of Mathematical Landscapes & Optimizers
- Created `track_a_continuous_optimization/src/landscapes.py`:
  - `ConvexQuadratic`, `StronglyConvexQuadratic`, `RastriginNonConvex`, `RosenbrockNonConvex`, `SaddlePointLandscape`, `NonLinearLeastSquaresProblem`.
- Created `track_a_continuous_optimization/src/optimizers.py`:
  - `BatchGradientDescent`, `StochasticGradientDescent`, `MiniBatchGradientDescent`, `MomentumOptimizer`, `NesterovAcceleratedGradient`, `AdaGrad`, `RMSProp`, `Adam`.
- Created `track_a_continuous_optimization/src/second_order.py`:
  - `NewtonsMethod` (Armijo backtracking + Levenberg-Marquardt spectral damping $\lambda_t = \max(0, -\lambda_{\min} + \delta)$).
  - `GaussNewtonMethod` (approximating $\nabla^2 S \approx J^T J$).
- Created `track_a_continuous_optimization/src/neural_net.py`:
  - `TwoLayerMLP` with strictly decoupled analytical backpropagation and centered finite-difference verification `check_gradients_numerical()`.
- Created `track_a_continuous_optimization/src/curvature.py`:
  - `CurvatureApproximations` implementing `empirical_fisher_matrix()`, `diagonal_hessian_approximation()`, `bfgs_low_rank_update()`, and `hessian_vector_product()`.

### Step 3: Automated Unit Testing
- Created `track_a_continuous_optimization/tests/test_continuous_optimizers.py`.
- 11 unit tests covering all 10 optimizers, finite-difference gradient checking, Fisher vs. Hessian divergence, BFGS secant property, and HVP accuracy.
- Result: **11/11 tests passed in 0.062s**.

### Step 4: Experimental Benchmarking
- Executed `run_landscape_comparison.py`: Benchmarked all 10 optimizers across 5 landscapes; generated JSON, CSV, and markdown reports.
- Executed `run_sensitivity_study.py`: Evaluated learning rates $\eta \in [10^{-4}, 1.0]$; captured stable and divergent regimes.
- Executed `run_noisy_study.py`: Evaluated noise levels $\sigma \in [0.0, 1.0]$ and batch sizes $B \in [1, 4, 16, 64]$; verified $\mathrm{Var}(\bar{g}) = \sigma^2 / B$.
- Executed `run_neural_net_experiment.py`: Verified analytical vs. numerical gradient error of **$4.00 \times 10^{-12}$**; demonstrated Adam and Momentum escaping XOR plateau to reach 100% accuracy.

### Step 5: Visualizations & Documentation
- Executed `visualize_results.py`: Generated 6 publication-ready figures in `track_a_continuous_optimization/plots/`.
- Authored `docs/methodology.md`, `docs/experimental_analysis.md`, `docs/viva_questions.md` (16 questions), and `README.md`.
- Updated `docs/CHAPTER_6_COVERAGE_CHECKLIST.md`, `docs/14_DAY_ROADMAP_TRACKER.md`, and root `README.md`.

---

## 3. Real Observed Engineering Bugs & Solutions

During Day 4 implementation, the following genuine engineering issues occurred and were automatically resolved:

1. **LaTeX Math Escaped Backslash Warning**:
   - *Issue*: Python 3.13 raised `SyntaxWarning: invalid escape sequence '\e'` in docstrings containing LaTeX math expressions (e.g. `\eta`, `\epsilon`, `\in`).
   - *Fix*: Prefixed all docstrings containing backslashes with raw string literals `r"""..."""`.

2. **Empirical Fisher vs. Hessian Identity at the Origin**:
   - *Issue*: An initial unit test asserted that $F_{\text{emp}}$ and $H_{\text{NLL}}$ must have a non-zero difference at $\theta = \mathbf{0}$. However, in binary logistic regression with uniform predictions ($p_i = 0.5$), $(y_i - p_i)^2 = 0.25$ and $p_i(1 - p_i) = 0.25$, making the empirical Fisher and Hessian mathematically identical at $\mathbf{0}$.
   - *Fix*: Updated the unit test to verify that $\|F_{\text{emp}} - H_{\text{NLL}}\| \equiv 0$ at $\theta = \mathbf{0}$, and that they strictly diverge ($\|F_{\text{emp}} - H_{\text{NLL}}\| > 0$) at $\theta \neq \mathbf{0}$.

3. **Rosenbrock Parameter Signature**:
   - *Issue*: `RosenbrockNonConvex` takes no arguments in `__init__`, but `run_sensitivity_study.py` passed keyword arguments `(a=1.0, b=100.0)`, throwing a `TypeError`.
   - *Fix*: Updated the call in `run_sensitivity_study.py` to `RosenbrockNonConvex()`.

4. **Optimizer Keyword Argument Uniformity**:
   - *Issue*: `run_noisy_study.py` called `StochasticGradientDescent(lr=0.01)` and `MiniBatchGradientDescent(lr=0.01)`, but `BaseOptimizer` accepts `learning_rate`.
   - *Fix*: Standardized parameter passing to `learning_rate=...` across all experimental scripts.

5. **Matplotlib Font Cache Building Delay**:
   - *Issue*: The first execution of `visualize_results.py` spawned a background task while building font caches.
   - *Fix*: Explicitly configured `matplotlib.use('Agg')` and waited for task completion, ensuring all 6 figures were successfully rendered.

---

## 4. Verification Check
- All Track E tests passing: **19/19 OK (1.66s)**
- All Track A tests passing: **11/11 OK (0.062s)**
- Git operations: **Zero git commit or push commands executed**.

