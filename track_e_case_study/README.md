# Track E: Railway Route and Transfer Optimization (Main Case Study)

> **Course**: Optimization Techniques — Lab Assignment 8  
> **Status**: **Day 2 & Day 3 Implementation Complete** (Dijkstra Baseline + Greedy Heuristic + Exact HiGHS ILP)  
> **Scope**: Full Multi-Objective Time-Dependent Timetable Network Optimization  

---

## 1. Executive Summary

This directory contains the primary real-process case study for **Assignment 8**: **Railway Route and Transfer Optimization**. 

Passenger railway networks operate on fixed, discrete timetables where journey viability depends not only on physical track connectivity, but crucially on **temporal synchronization** and **interchange buffer feasibility**. Standard static graph algorithms fail fundamentally because traversal costs are time-dependent step functions and transfers require mandatory station-specific dwell buffers.

### Core Objectives:
1. **Minimize Total Journey Duration**: Minimize elapsed wall-clock time from departure to arrival.
2. **Minimize Transfer Waiting Time**: Penalize idle waiting time spent on interchange station platforms.
3. **Minimize Number of Transfers**: Reduce cognitive fatigue, luggage handling, and risk of missed connections.

---

## 2. Directory Layout

```text
track_e_case_study/
├── README.md                           # Master track documentation
├── src/
│   ├── __init__.py                     # Package export definitions
│   ├── graph.py                        # Station, Connection, and Timetable graph loader
│   ├── journey_result.py               # Itinerary representation and table formatter
│   ├── dijkstra_baseline.py            # Time-Dependent Earliest-Arrival Dijkstra + Static baseline
│   ├── greedy_optimizer.py             # Multi-objective Greedy heuristic router
│   ├── ilp_optimizer.py                # Exact Binary Integer Linear Programming (HiGHS)
│   ├── generate_dataset.py             # Reproducible 28-station timetable generator
│   ├── benchmark_baseline.py           # Baseline 10-query benchmark harness
│   ├── benchmark_comparison.py         # 20-query comparative benchmark (Dijkstra vs Greedy vs ILP)
│   ├── sensitivity_analysis.py         # Objective weight sensitivity evaluation
│   ├── visualize_network.py            # Network topology & route plots
│   └── visualize_comparison.py         # Comparative benchmark plots (4 figures)
├── tests/
│   ├── test_dijkstra_baseline.py       # 9 compulsory baseline unit tests
│   └── test_optimizers.py              # 10 comprehensive edge case & optimality tests
├── docs/
│   ├── problem_formulation.md          # Full mathematical formulation (sets, variables, constraints)
│   ├── dataset_description.md          # Network topology, corridor breakdown, and CSV/JSON schema
│   ├── baseline_methodology.md         # Time-dependent vs. static Dijkstra comparison & FIFO analysis
│   ├── greedy_methodology.md           # Greedy step mechanics & counterexample analysis
│   ├── ilp_formulation.md              # Exact binary network flow ILP formulation
│   ├── comparative_analysis.md         # Detailed 20-query benchmark analysis & trade-offs
│   └── viva_questions.md               # 16 comprehensive theoretical defense Q&As
├── results/
│   ├── baseline_benchmark_results.json # Baseline benchmark JSON
│   ├── baseline_benchmark_summary.md   # Baseline benchmark markdown
│   ├── comparative_benchmark_results.json # Full 20-query comparative benchmark data
│   ├── comparative_benchmark_summary.md   # Full 20-query tabulated markdown report
│   └── weight_sensitivity_results.json    # Objective weight sensitivity results
└── plots/
    ├── 01_railway_network_topology.png # 28-station network map with corridors & junctions
    ├── 02_example_journey_route.png    # Traversed path highlight for multi-transfer itinerary
    ├── 03_journey_time_breakdown.png   # Travel vs. waiting time stacked breakdown + latency
    ├── 04_journey_duration_comparison.png # 20-query journey duration comparison
    ├── 05_algorithm_latency_comparison.png # Execution latency log-scale comparison
    ├── 06_waiting_time_and_transfers_comparison.png # Platform wait and transfer count comparison
    └── 07_solution_quality_optimality_gap.png # Optimality gap (%) relative to proven ILP optimal
```

---

## 3. Quick Start & Execution Guide

### 3.1 Run Complete Test Suite (19 Tests)
```bash
python -m unittest discover -s track_e_case_study/tests -v
```

### 3.2 Run 20-Query Comparative Benchmark
```bash
python -m track_e_case_study.src.benchmark_comparison
```

### 3.3 Run Weight Sensitivity Analysis
```bash
python -m track_e_case_study.src.sensitivity_analysis
```

### 3.4 Generate All 7 Visualizations
```bash
python -m track_e_case_study.src.visualize_network
python -m track_e_case_study.src.visualize_comparison
```

---

## 4. Aggregate Empirical Performance Comparison (20 Queries)

| Performance Dimension | Dijkstra (Baseline) | Greedy Heuristic | Exact ILP (HiGHS) | Best Performer |
| :--- | :--- | :--- | :--- | :--- |
| **Optimality Guarantee** | Heuristic (Earliest Arr) | Heuristic (Greedy) | **Globally Proven Optimal** | **ILP** |
| **Mean Execution Latency** | **0.276 ms** | 2.044 ms | 547.285 ms | **Dijkstra** (1980x vs ILP) |
| **Mean Journey Duration** | 273.9 min | 277.3 min | **246.9 min** | **ILP** (-27.0 min saving) |
| **Mean Waiting Time** | 56.0 min | 48.9 min | **30.9 min** | **ILP** (-25.1 min saving) |
| **Mean Transfers Count** | 0.95 | 0.70 | **0.60** | **ILP** (-37% transfers) |
| **Mean Composite Cost ($Z$)** | 323.9 | 315.2 | **273.1** | **ILP** (-15.7% lower cost) |
| **Mean Optimality Gap** | 20.58% | 15.81% | **0.00% (Reference)** | **ILP** |
| **Proven Optimal Count** | 0 / 20 | 0 / 20 | **20 / 20 (100%)** | **ILP** |

---

## 5. Strategy Selection Framework

* **Time-Dependent Dijkstra**: Deploy for ultra-responsive consumer autocomplete / real-time search where sub-millisecond latency is mandatory and earliest arrival is the only goal.
* **Greedy Heuristic**: Deploy for resource-constrained mobile journey planners where multi-objective trade-offs are desired within a $< 5$ ms latency window.
* **Exact Binary ILP**: Deploy for master timetable scheduling, operational planning, and high-value journeys where global passenger utility maximization justifies a $\sim 500$ ms solve budget.
