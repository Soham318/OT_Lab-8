# Track E: Railway Route and Transfer Optimization (Main Case Study)

> **Course**: Optimization Techniques — Lab Assignment 8  
> **Status**: Day 2 Baseline Implementation Complete  
> **Approach**: Multi-Objective Time-Dependent Passenger Routing & Transfer Buffer Scheduling  

---

## 1. Executive Summary

This directory contains the primary real-process case study for **Assignment 8**: **Railway Route and Transfer Optimization**. 

Passenger railway networks operate on fixed, discrete timetables where journey viability depends not only on physical track connectivity, but crucially on **temporal synchronization** and **interchange buffer feasibility**. Standard static graph algorithms (such as Dijkstra on spatial edge weights) fail fundamentally because traversal costs are time-dependent step functions and transfers require mandatory station-specific dwell buffers.

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
│   ├── generate_dataset.py             # Reproducible 28-station timetable generator
│   ├── benchmark_baseline.py           # Multi-query latency and duration benchmark harness
│   └── visualize_network.py            # Matplotlib network topology and breakdown plots
├── tests/
│   └── test_dijkstra_baseline.py       # 9 compulsory unit tests covering all operational edge cases
├── docs/
│   ├── problem_formulation.md          # Full mathematical formulation (sets, variables, constraints)
│   ├── dataset_description.md          # Network topology, corridor breakdown, and CSV/JSON schema
│   └── baseline_methodology.md         # Time-dependent vs. static Dijkstra comparison & FIFO analysis
├── results/
│   ├── baseline_benchmark_results.json # Structured benchmark JSON metrics
│   └── baseline_benchmark_summary.md   # Tabulated benchmark report
└── plots/
    ├── 01_railway_network_topology.png # 28-station network map with corridors & junctions
    ├── 02_example_journey_route.png    # Traversed path highlight for multi-transfer itinerary
    └── 03_journey_time_breakdown.png   # Travel vs. waiting time stacked breakdown + latency
```

---

## 3. Quick Start & Execution Guide

### 3.1 Generate Dataset
Generates `data/railway_stations.csv`, `data/train_connections.csv`, and `data/railway_network.json`:
```bash
python track_e_case_study/src/generate_dataset.py
```

### 3.2 Run Automated Tests
Executes the 9 compulsory scenario tests:
```bash
python -m unittest track_e_case_study.tests.test_dijkstra_baseline
```

### 3.3 Execute Performance Benchmarks
Runs 10 representative queries across peak and off-peak windows with 50 repetitions each:
```bash
python -m track_e_case_study.src.benchmark_baseline
```

### 3.4 Generate Visualizations
Produces high-resolution PNG plots in `track_e_case_study/plots/`:
```bash
python -m track_e_case_study.src.visualize_network
```

---

## 4. Measured Baseline Results (Actual Benchmark Data)

| Query Scenario | Category | OD Pair | Query Dep | Actual Dep-Arr | Journey Duration | In-Vehicle | Wait Time | Transfers | Mean Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Mainline Short Direct** | Direct | STN_01 $\to$ STN_04 | 06:00 | 06:00 - 06:56 | 56m (0.9h) | 56m | 0m | 0 | 0.014 ms |
| **Mainline Trunk Express** | Direct | STN_01 $\to$ STN_10 | 06:00 | 06:00 - 11:23 | 323m (5.4h) | 303m | 0m | 0 | 0.180 ms |
| **Western Coastal to Metro Hub** | 1-Transfer | STN_11 $\to$ STN_06 | 06:00 | 06:00 - 09:53 | 233m (3.9h) | 199m | 28m | 1 | 0.058 ms |
| **Eastern Industrial to Highland**| 1-Transfer | STN_15 $\to$ STN_07 | 06:30 | 06:30 - 11:00 | 270m (4.5h) | 203m | 61m | 1 | 0.048 ms |
| **Southern Ring to River Jct** | 1-Transfer | STN_20 $\to$ STN_04 | 06:00 | 06:43 - 11:34 | 291m (4.8h) | 215m | 70m | 1 | 0.091 ms |
| **Cross-Network Coast-to-Mountain**| Multi-Transfer | STN_12 $\to$ STN_28 | 06:00 | 06:40 - 17:36 | 656m (10.9h) | 475m | 172m | 3 | 0.371 ms |
| **Cross-Network South-to-East** | Multi-Transfer | STN_21 $\to$ STN_18 | 07:00 | 07:33 - 16:24 | 531m (8.8h) | 377m | 139m | 2 | 0.329 ms |
| **Southern Spur to Northern Peak** | Multi-Transfer | STN_25 $\to$ STN_10 | 06:00 | 06:41 - 13:23 | 402m (6.7h) | 251m | 141m | 2 | 0.244 ms |

---

## 5. Next Steps for Optimization (Phase 2 & 3)

With the baseline firmly established and verified:
1. **Multi-Objective Greedy Heuristic**: Implement a Pareto-weighting greedy search balancing earliest arrival against high transfer waiting buffers.
2. **Integer Linear Programming (ILP)**: Formulate the time-expanded connection network as a binary ILP solved via HiGHS (`scipy.optimize.milp`) to prove global optimality and quantify the optimality gap against the baseline and greedy heuristic.

