# Track B: Discrete Optimization

> **Assignment 8**: Optimize Anything — 14-Day Vibe-Coding Challenge  
> **Repository Module**: `track_b_discrete_optimization/`  
> **Status**: Complete & Verified (7/7 Automated Unit Tests Passing)

---

## 1. Module Overview

Track B provides a rigorous, self-contained combinatorial optimization benchmark suite evaluating five foundational discrete paradigms on the 0/1 Knapsack Problem:
1. **Greedy Optimization Heuristic**: Value-to-weight density ratio sorting with formal proof and demonstration of a $27.27\%$ suboptimality gap on a pathological counterexample.
2. **Integer Linear Programming (ILP)**: Exact binary program solved via SciPy's HiGHS solver (`scipy.optimize.milp`), scaling up to $N=200$ items.
3. **Branch-and-Bound**: Transparent tree search implementing continuous Linear Programming (LP) relaxation upper bounds (Dantzig rule), recording branching decisions, bounds, and pruning events.
4. **Dynamic Programming (DP)**: Exact 2D state-space table with recurrence relations, base cases, and full backtracking item reconstruction.
5. **QUBO & Ising Model**: Classical quadratic unconstrained binary Hamiltonian formulation with logarithmic slack variable expansion, exact spin mapping ($s_i = 2x_i - 1$), penalty coefficient bounds ($P > \max v_i$), and exhaustive ground-state verification.

---

## 2. Directory Layout

```
track_b_discrete_optimization/
├── docs/
│   ├── methodology.md            # Detailed mathematical formulations & derivations
│   ├── experimental_analysis.md  # Multi-instance empirical benchmarks (N=3 to 200)
│   └── viva_questions.md         # 16 academic viva defense Q&As
├── experiments/
│   ├── run_discrete_comparison.py # Benchmarking all 5 paradigms across problem scales
│   └── run_qubo_penalty_study.py  # Critical penalty multiplier phase transition study
├── plots/
│   ├── 01_objective_value_comparison.png
│   ├── 02_runtime_vs_problem_size.png
│   ├── 03_greedy_optimality_gap.png
│   └── 04_qubo_penalty_and_energy_landscape.png
├── results/
│   ├── discrete_comparison_results.json
│   ├── discrete_comparison_summary.csv
│   ├── discrete_comparison_report.md
│   ├── qubo_penalty_study_results.json
│   └── qubo_penalty_study_summary.csv
├── src/
│   ├── __init__.py
│   ├── problem.py                # KnapsackProblem instance generator & validator
│   ├── greedy_solver.py          # Value-to-weight efficiency ratio heuristic
│   ├── ilp_solver.py             # Binary MILP solver via SciPy HiGHS
│   ├── branch_and_bound.py       # Transparent tree search with Dantzig LP bounds
│   ├── dp_solver.py              # 2D DP table with backtracking reconstruction
│   ├── qubo_ising.py             # QUBO matrix, penalty slack bits, and Ising spin conversion
│   └── visualize_results.py      # Matplotlib figure generation
└── tests/
    └── test_discrete_optimizers.py # 7 automated unit tests
```

---

## 3. Quickstart & Verification Commands

All experiments and tests can be executed directly from the project root directory:

### Run Unit Tests (100% Pass Rate Required)
```bash
python -m unittest discover -s track_b_discrete_optimization/tests -v
```

### Run Benchmarks & Experiments
```bash
# 1. Benchmark all methods across problem sizes (N=3 to 200)
python -m track_b_discrete_optimization.experiments.run_discrete_comparison

# 2. Run QUBO penalty phase transition study
python -m track_b_discrete_optimization.experiments.run_qubo_penalty_study
```

### Regenerate Visualizations
```bash
python -m track_b_discrete_optimization.src.visualize_results
```

---

## 4. Key Benchmark Results

| Method | Optimality | Complexity | Runtime ($N=200$) | Key Characteristic |
| :--- | :--- | :--- | :--- | :--- |
| **Greedy Heuristic** | Approximate | $\mathcal{O}(n \log n)$ | **0.59 ms** | Ultrafast; $27.27\%$ gap on counterexample, $<1.2\%$ on random instances |
| **Branch-and-Bound** | Exact Optimal | Worst-case $\mathcal{O}(2^n)$ | — (tested to $N=50$) | Tight Dantzig LP bounds solve $N=50$ in **0.70 ms** ($17\times$ faster than DP) |
| **Dynamic Programming**| Exact Optimal | $\mathcal{O}(n W)$ | 1055.9 ms | Exact 2D table; pseudo-polynomial memory trade-off |
| **ILP (HiGHS)** | Exact Optimal | Branch-and-Cut | **484.2 ms** | Industrial scalability up to $N=200$; handles arbitrary real weights |
| **QUBO Exhaustive** | Exact Optimal | Classical $\mathcal{O}(2^N)$ | — (tested to $N=8$) | Proves energy parity with Ising model ($< 10^{-10}$) and $P > \max v_i$ boundary |

