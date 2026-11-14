# Track H: DBMS Query Optimization & Index Selection

Track H of the 14-Day Optimization Challenge implements physical Database Management System (DBMS) query optimization and secondary B-tree index selection using Python and SQLite.

---

## 1. Executive Summary

- **Problem Domain**: High-concurrency National Railway Reservation and Ticketing System.
- **Data Scale**: 7 relational tables, 179,760 records, 9.46 MB baseline database size.
- **Optimization Problem**: The **Index Selection Problem (ISP)** formulated as a discrete constrained optimization problem (0-1 Knapsack / Set Packing) maximizing workload benefit subject to a hard storage budget $S_{\max}$.
- **Algorithmic Methods**:
  1. **Baseline**: Unindexed SQLite database (sequential scans only).
  2. **Greedy Heuristic**: Marginal benefit-to-cost ratio selection with dynamic marginal gain re-evaluation.
  3. **Exact Binary ILP**: Solved to proven global optimality using `scipy.optimize.milp` with the HiGHS branch-and-cut solver.
  4. **Exhaustive Combinatorial Oracle**: Evaluated all $2^{12} = 4,096$ candidate subsets to verify ILP exactness.
- **Key Empirical Result**:
  - At $S_{\max} = 3.0$ MB, Greedy exhibits an authentic **$6.92\%$ optimality gap** by falling into a myopic trap (selecting two cheap low-impact indexes instead of one high-impact composite index).
  - ILP accelerates high-frequency transactional lookups (Q8) by **11.45x** (latency reduced from 1.26 ms to 0.11 ms) by transitioning the execution plan from a full table scan to a B-tree index search.
  - 100% query result parity verified across all configurations using cryptographic SHA-256 hashing.

---

## 2. Directory Layout

```text
track_h_dbms_optimization/
├── data/                               # Generated SQLite database instances
│   ├── railway_baseline.db             # Baseline database (no secondary indexes)
│   ├── railway_greedy.db               # Database with Greedy-selected indexes
│   └── railway_ilp.db                  # Database with ILP-selected indexes
├── docs/                               # Detailed technical documentation
│   ├── dbms_architecture.md            # SQLite engine, B-Tree storage, VDBE, and catalog stats
│   ├── optimization_formulation.md     # Mathematical ISP formulation, ILP linearization, and Greedy
│   ├── experimental_analysis.md        # Full benchmark results, latencies, speedups, and budget sweep
│   └── viva_questions.md               # 15 in-depth academic viva defense Q&As
├── experiments/                        # Experimental drivers
│   └── run_budget_sweep.py             # Sweeps storage budgets from 1.0 to 10.0 MB
├── plots/                              # 4 Publication-quality figures (300 DPI)
│   ├── 01_query_latency_comparison.png
│   ├── 02_workload_runtime_and_throughput.png
│   ├── 03_storage_overhead_vs_latency_reduction.png
│   └── 04_query_plan_scan_vs_index_breakdown.png
├── results/                            # Benchmark artifacts and execution plans
│   ├── baseline_plans.json             # EXPLAIN QUERY PLAN dumps for Baseline
│   ├── greedy_plans.json               # EXPLAIN QUERY PLAN dumps for Greedy
│   ├── ilp_plans.json                  # EXPLAIN QUERY PLAN dumps for ILP
│   ├── benchmark_comparison.json       # Full benchmark metrics in JSON
│   ├── benchmark_comparison.csv        # Tabular latency and speedup CSV
│   ├── budget_sweep_results.json       # Budget sweep metrics across 14 budgets
│   └── budget_sweep_results.csv        # Budget sweep tabular comparison
├── src/                                # Core implementation source code
│   ├── schema.py                       # Relational schema DDL (7 tables, PKs, FKs)
│   ├── data_generator.py               # Deterministic synthetic data generator (seed 42)
│   ├── workload.py                     # 8 representative queries (Q1 to Q8)
│   ├── index_candidates.py             # 12 candidate single and composite indexes
│   ├── greedy_selector.py              # Greedy index selection algorithm
│   ├── ilp_selector.py                 # Exact HiGHS ILP solver & exhaustive oracle
│   ├── benchmark_runner.py             # End-to-end benchmark driver & hash verification
│   └── visualize_results.py            # Generates all 4 publication-quality plots
└── tests/                              # Automated test suite
    └── test_dbms_optimization.py       # 10 comprehensive unit and regression tests
```

---

## 3. Quickstart & Verification Commands

### Run Full Benchmark Study
```bash
python -m track_h_dbms_optimization.src.benchmark_runner
```

### Run Storage Budget Sweep Experiment
```bash
python -m track_h_dbms_optimization.experiments.run_budget_sweep
```

### Generate Visualization Plots
```bash
python -m track_h_dbms_optimization.src.visualize_results
```

### Run Automated Test Suite
```bash
python -m unittest discover -s track_h_dbms_optimization/tests -v
```

---

## 4. Workload Query Summary

| Query ID | Name | Type | Key Predicates & Operations |
| :--- | :--- | :--- | :--- |
| **Q1** | Active Confirmed Bookings | Range & Filter | `journey_date BETWEEN ? AND ?`, `status = 'CONFIRMED'` |
| **Q2** | Passenger Manifest | Multi-Table Join | 3-table join (`passengers`, `tickets`, `bookings`) on `journey_date` |
| **Q3** | Train Revenue Aggregation | Multi-Table Group | Joins `bookings` and `trains`, `SUM(base_fare)`, `GROUP BY train_id` |
| **Q4** | Morning Station Departures | Range Filter & Sort | `station_id = ?`, `departure_time BETWEEN 360 AND 720` |
| **Q5** | High-Fare Payment Summary | Join & Filter | Joins `payments` and `bookings`, `amount_paid > 2500` |
| **Q6** | Premium Tier Passengers | Complex Subquery | Joins `passengers` (`PLATINUM`/`GOLD`), `COUNT(*) > 2` subquery |
| **Q7** | Demographics & Occupancy | Analytical Grouping | 3-table join, `GROUP BY travel_class, age_bracket` |
| **Q8** | Transactional PNR Lookup | Point Lookup | 5-table join pinpointing exact PNR itinerary and payment |

---

## 5. Verification & Correctness Highlights

- **100% SHA-256 Parity**: All 8 queries returned identical result rows across Baseline, Greedy, and ILP databases.
- **Exactness Check**: ILP solver matched Exhaustive Combinatorial search across all 14 budget levels ($0.00\%$ gap).
- **Heuristic Gap**: At budget $3.0$ MB, Greedy exhibited a $6.92\%$ optimality gap, demonstrating the theoretical limitations of local greedy heuristics.

