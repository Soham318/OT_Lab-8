# Day 10 Prompt Log — Track H: DBMS Query Optimization & Index Selection

> **Session**: Day 10 of 14-Day Vibe-Coding Challenge  
> **Track**: Track H (DBMS Query Optimization & Index Selection)  
> **Agent**: Antigravity AI (Gemini 3.8 Flash High)  
> **Date**: November 14, 2026  
> **Branch**: `main` (Strictly local working copy, zero Git commits executed)  

---

## 1. Day 9 Audit & Corrections Verification

Prior to commencing Track H, an audit of the Day 9 xv6 kernel implementation was performed and corrected:
1. **User Header Return Type Consistency**:
   - In `track_g_xv6_kernel/xv6-riscv/user/user.h`, line 25 was updated from `int getcputime(void);` to `uint64 getcputime(void);`, matching the kernel `sys_getcputime()` return type (`uint64`) and user assembly stub in `user/usys.pl`.
2. **Clarification of Concurrent SMP Metric**:
   - In `track_g_xv6_kernel/docs/experimental_analysis.md`, `track_g_xv6_kernel/README.md`, and `prompts/track_g/day9_prompt_log.md`, the 1.87 figure was explicitly documented as an *aggregate CPU-tick-to-wall-tick ratio* across cores rather than a single-threaded program wall-clock speedup.
3. **Honest `usertests` Documentation**:
   - Documented that the modified-kernel `usertests -q` run executed 29 tests cleanly before hitting the 45-second test runner timeout at test 30 (`sharedfd`).
4. **Removal of Unsubstantiated Overhead Claims**:
   - Removed unverified claims of `<5 ns` syscall latency and `<0.0001%` timer interrupt overhead.

---

## 2. Track H Objectives & Architecture

Track H implements a full-featured Database Management System (DBMS) query optimization and physical design study:
- **Relational Domain**: High-concurrency National Railway Reservation and Ticketing System across 7 tables (`stations`, `trains`, `schedules`, `passengers`, `bookings`, `tickets`, `payments`).
- **Scale**: Deterministic seed 42, 179,760 total rows, 9.46 MB raw SQLite database footprint.
- **Problem Formulation**: The **Index Selection Problem (ISP)** formulated as a discrete constrained optimization problem (0-1 Knapsack / Set Packing) with coupling constraints linearizing non-additive query benefits.
- **Workload**: 8 representative queries (Q1 to Q8) spanning range filters, multi-table joins, aggregations, subqueries, and point lookups.
- **Index Candidates**: 12 secondary single-column and composite B-tree indexes (`IDX_01` through `IDX_12`).
- **Paradigms Evaluated**:
  1. *Baseline*: Unindexed SQLite (primary key clustered scans only).
  2. *Greedy Heuristic*: Marginal benefit-to-cost ratio selection with dynamic gain re-evaluation.
  3. *Exact Binary ILP*: Solved via `scipy.optimize.milp` using the HiGHS branch-and-cut solver.
  4. *Exhaustive Combinatorial Oracle*: Evaluated all $2^{12} = 4,096$ candidate subsets to verify global optimality.

---

## 3. Tool Invocations & Commands Log

| Step | Action / Command | Purpose & Result |
| :--- | :--- | :--- |
| **1** | `python -m track_h_dbms_optimization.src.benchmark_runner` | Generated base database (9.46 MB, 179,760 rows), solved index selection at budget 3.0 MB, executed 5 timed runs per query, verified 100% SHA-256 result hash parity across Baseline, Greedy, and ILP. |
| **2** | `python -m track_h_dbms_optimization.experiments.run_budget_sweep` | Swept storage budgets from 1.0 to 10.0 MB across 14 discrete thresholds, demonstrating 6.92% Greedy gap at 3.0 MB and 100% ILP exactness against exhaustive search. |
| **3** | `python -m track_h_dbms_optimization.src.visualize_results` | Generated 4 publication-quality figures (300 DPI) in `track_h_dbms_optimization/plots/`. |
| **4** | `python -m unittest discover -s track_h_dbms_optimization/tests -v` | Executed 10 automated unit and regression tests, passing with 100% success in 0.530s. |

---

## 4. Key Empirical Findings

1. **Greedy Myopic Optimality Trap ($6.92\%$ Gap)**:
   - At budget $S_{\max} = 3.0$ MB, Greedy selected `['IDX_02', 'IDX_09', 'IDX_10']` (Storage: 2.9 MB, Score: **6,520.0**).
   - Exact ILP selected `['IDX_02', 'IDX_07']` (Storage: 2.9 MB, Score: **7,005.0**).
   - Exhaustive combinatorial search confirmed `['IDX_02', 'IDX_07']` is the guaranteed global optimum, proving an authentic $6.92\%$ gap in Greedy.
2. **11.45x Physical Speedup on Transactional Lookup (Q8)**:
   - Query Q8 (PNR itinerary lookup) latency dropped from **1.26 ms** (Baseline table scan) to **0.11 ms** (ILP B-tree index seek).
   - Greedy did not select `IDX_07` and remained stuck with a table scan executing in 1.28 ms.
3. **100% Semantic Correctness Parity**:
   - SHA-256 cryptographic hashes verified that query results were 100% identical across all three database instances.

---

## 5. Artifacts & Deliverables Summary

- **Source Code**: `track_h_dbms_optimization/src/` (`schema.py`, `data_generator.py`, `workload.py`, `index_candidates.py`, `greedy_selector.py`, `ilp_selector.py`, `benchmark_runner.py`, `visualize_results.py`).
- **Experiments**: `track_h_dbms_optimization/experiments/run_budget_sweep.py`.
- **Automated Tests**: `track_h_dbms_optimization/tests/test_dbms_optimization.py` (10 tests, 100% pass).
- **Visualizations**: 4 high-DPI figures in `track_h_dbms_optimization/plots/`.
- **Documentation**: `track_h_dbms_optimization/docs/` (`dbms_architecture.md`, `optimization_formulation.md`, `experimental_analysis.md`, `viva_questions.md` with 15 Q&As, `README.md`).
- **Master Tracking**: `docs/CHAPTER_6_COVERAGE_CHECKLIST.md`, `docs/14_DAY_ROADMAP_TRACKER.md`, `README.md`, `prompts/failure_log.md` (Case 15).
- **Git State**: Zero commits or pushes executed.

