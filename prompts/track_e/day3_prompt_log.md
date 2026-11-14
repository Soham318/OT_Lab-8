# Day 3 Prompt Log: Track E Railway Route and Transfer Optimization (Greedy + ILP)

> **Track**: Track E — Main Real-Process Case Study  
> **Date**: November 14, 2026  
> **Tool**: Antigravity AI (Gemini 3.8 Flash High)  
> **Status**: Completed & Verified (19/19 Tests Pass, 20 Benchmark Queries Executed)  

---

## 1. Original User Prompt

```text
DAY 3 – DIRECT IMPLEMENTATION
TRACK E: RAILWAY ROUTE AND TRANSFER OPTIMIZATION
GREEDY HEURISTIC + INTEGER LINEAR PROGRAMMING

You are continuing the existing OT_Lab-8 project.
Act as a senior optimization engineer and autonomous AI coding agent.

IMPORTANT:
- Directly implement all tasks.
- Do not repeatedly ask me for permission for routine operations.
- Reuse the existing Day 2 implementation.
- Do not rebuild the project from scratch.
- Do not delete existing files or results.
- Run and verify all implementations.
- Fix errors automatically.
- Do not fabricate results.
- Do not commit or push anything. I will handle Git operations.

REFERENCE: Read the original Assignment 8 PDF and existing Track E documentation.
TODAY'S OBJECTIVE: Implement and compare:
1. Time-dependent Dijkstra baseline.
2. Greedy optimization heuristic.
3. Exact Integer Linear Programming (ILP).
All three approaches must solve the same railway routing problem under equivalent constraints.

STEP 1 – REVIEW EXISTING IMPLEMENTATION
STEP 2 – GREEDY OPTIMIZATION (greedy_optimizer.py, configurable weights, heuristic explanation)
STEP 3 – INTEGER LINEAR PROGRAMMING (ilp_optimizer.py, scipy.optimize.milp, HiGHS, time-expanded network, binary variables, flow conservation)
STEP 4 – OBJECTIVE CONSISTENCY (Weighted multi-objective consistency, sensitivity study)
STEP 5 – EXPERIMENTAL COMPARISON (20 representative queries, metrics table, repeated runs, optimality gap)
STEP 6 – EDGE CASE TESTING (10 new tests, counterexample proof, manual graph verification)
STEP 7 – VISUALIZATIONS (4 new plots: journey duration, latency log-scale, waiting & transfers, optimality gap)
STEP 8 – DOCUMENTATION (greedy_methodology.md, ilp_formulation.md, comparative_analysis.md)
STEP 9 – VIVA PREPARATION (viva_questions.md with >= 15 questions and model answers)
STEP 10 – FINAL VERIFICATION (Run entire test suite, verify reproducibility, prompt log)
```

---

## 2. Work Performed

1. **Greedy Multi-Objective Router (`track_e_case_study/src/greedy_optimizer.py`)**:
   * Implemented multi-objective heuristic evaluating immediate step cost plus remaining travel time estimate ($h(v)$).
   * Enforced station-specific platform transfer buffers ($\Delta_{\text{min}}$) and maximum transfer count budget.
   * Built-in cycle prevention using station path history tracking.
2. **Exact Binary Integer Linear Program (`track_e_case_study/src/ilp_optimizer.py`)**:
   * Formulated binary network flow model on time-expanded connections ($x_c \in \{0, 1\}$) and transfers ($y_{c_1, c_2} \in \{0, 1\}$).
   * Interfaced with `scipy.optimize.milp` using the state-of-the-art HiGHS branch-and-cut solver.
   * Implemented exact flow conservation at origin, destination, and intermediate junction nodes.
   * Enforced transfer buffers during matrix generation, avoiding non-linear constraints.
   * Handled infeasibility, timeouts, and automated solution reconstruction with parameter verification.
3. **Multi-Objective Weight Sensitivity Analysis (`track_e_case_study/src/sensitivity_analysis.py`)**:
   * Evaluated 4 passenger preference profiles (Pure Duration, Standard Balanced, Transfer-Averse, Fast Speed Commuter), demonstrating Pareto trade-offs between direct and connecting services.
4. **20-Query Empirical Benchmark Suite (`track_e_case_study/src/benchmark_comparison.py`)**:
   * Benchmarked 20 representative Origin-Destination queries spanning all 5 network corridors across morning peak, mid-day, and evening peak hours with repeated runs.
   * Computed average journey duration, waiting time, transfer counts, latency, and optimality gaps.
5. **Comprehensive Edge Case Test Suite (`track_e_case_study/tests/test_optimizers.py`)**:
   * Implemented 10 unit test cases including direct routes, transfer limits, infeasible queries, timeout handling, itinerary consistency, and hand-calculated 2-route branch-and-bound verification.
   * Created a formal 3-station counterexample proving greedy suboptimality (Greedy chooses 150m path; ILP chooses 70m path).
6. **Comparative Visualizations (`track_e_case_study/src/visualize_comparison.py`)**:
   * Generated 4 publication-ready 300 DPI figures: journey duration comparison, execution latency on log scale, waiting time & transfers comparison, and optimality gap percentage.
7. **Documentation & Viva Defense**:
   * Authored `greedy_methodology.md`, `ilp_formulation.md`, `comparative_analysis.md`, and `viva_questions.md` (16 questions with academic answers).
   * Updated `track_e_case_study/README.md`, root `README.md`, `CHAPTER_6_COVERAGE_CHECKLIST.md`, and `14_DAY_ROADMAP_TRACKER.md`.

---

## 3. Files Created or Modified

### Files Created:
* `track_e_case_study/src/greedy_optimizer.py`
* `track_e_case_study/src/ilp_optimizer.py`
* `track_e_case_study/src/benchmark_comparison.py`
* `track_e_case_study/src/sensitivity_analysis.py`
* `track_e_case_study/src/visualize_comparison.py`
* `track_e_case_study/tests/test_optimizers.py`
* `track_e_case_study/docs/greedy_methodology.md`
* `track_e_case_study/docs/ilp_formulation.md`
* `track_e_case_study/docs/comparative_analysis.md`
* `track_e_case_study/docs/viva_questions.md`
* `track_e_case_study/results/comparative_benchmark_results.json`
* `track_e_case_study/results/comparative_benchmark_summary.md`
* `track_e_case_study/results/weight_sensitivity_results.json`
* `track_e_case_study/plots/04_journey_duration_comparison.png`
* `track_e_case_study/plots/05_algorithm_latency_comparison.png`
* `track_e_case_study/plots/06_waiting_time_and_transfers_comparison.png`
* `track_e_case_study/plots/07_solution_quality_optimality_gap.png`
* `prompts/track_e/day3_prompt_log.md`

### Files Modified:
* `track_e_case_study/src/__init__.py`
* `track_e_case_study/README.md`
* `README.md`
* `docs/CHAPTER_6_COVERAGE_CHECKLIST.md`
* `docs/14_DAY_ROADMAP_TRACKER.md`

---

## 4. Errors Encountered and Corrections

1. **Typing Import Error in `visualize_comparison.py`**:
   * *Error*: `NameError: name 'Dict' is not defined` when running visualization script.
   * *Fix*: Added `from typing import Dict, List` at the top of the file. Reran script with 100% success.
2. **Docstring Escape Sequence Warning in `ilp_optimizer.py`**:
   * *Error*: Python 3.13 threw a SyntaxWarning on `\i` inside a LaTeX math formula in the module docstring.
   * *Fix*: Prefixed the docstring with `r"""` to treat LaTeX backslashes as raw literals.

---

## 5. Actual Experimental Results (Aggregate)

Across 20 representative queries:
* **Time-Dependent Dijkstra**: Mean latency = 0.276 ms; Mean journey duration = 273.9 min; Mean wait = 56.0 min; Mean transfers = 0.95; Optimality gap = **20.58%**.
* **Greedy Heuristic**: Mean latency = 2.044 ms; Mean journey duration = 277.3 min; Mean wait = 48.9 min; Mean transfers = 0.70; Optimality gap = **15.81%**.
* **Exact ILP (HiGHS)**: Mean latency = 547.285 ms; Mean journey duration = **246.9 min**; Mean wait = **30.9 min**; Mean transfers = **0.60**; Optimality gap = **0.00% (Reference)**.
* **Proven Optimal Rate**: **20/20 (100%)** of queries solved to proven global optimality.

