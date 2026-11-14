# Track J: Real-World Codebase Optimization
**Enterprise Workflow DAG Scheduling and Resource Allocation Engine**  
**Course**: Optimization Techniques (14-Day Vibe-Coding Challenge — Day 12)  
**Author**: Soham Umesh Chavan  
**Status**: 100% COMPLETE & VERIFIED

---

## 1. Executive Summary

Track J implements, profiles, mathematically formulates, and optimizes an authentic $\ge 1,000$-line software engineering system modeling an enterprise Directed Acyclic Graph (DAG) workflow scheduling engine (akin to Apache Airflow, Prefect, and Ray Workflows).

Using standard Python profiling tools (`cProfile`, `pstats`, and `tracemalloc`), we identified that **99.0% of scheduling execution time** in the legacy baseline was consumed by redundant graph reachability queries. We replaced this $O(V^3)$ bottleneck with a **Chapter 6 Dynamic Programming (DP)** memoization algorithm, incremental in-degree dependency tracking, and binary priority-queue event scheduling, reducing algorithmic complexity to $O((V+E)\log V)$ and achieving empirical speedups ranging from **$11.2\times$ on small workflows up to $7,311\times$ on extra-large workflows** with 100% schedule validity.

---

## 2. Directory Structure

```
track_j_real_world_optimization/
├── src/
│   ├── workflow_models.py           # Domain models, dataclasses, formal validator
│   ├── dag_parser.py                # Graph representation, Kahn's topological sort
│   ├── dataset_generator.py         # Layered workflow synthesis across 4 scales
│   ├── cost_analyzer.py             # Forward/backward DP, EST/EFT/LST/LFT, bounds
│   ├── baseline_scheduler.py        # Legacy unoptimized O(V^3) scheduler
│   ├── optimized_scheduler.py       # Chapter 6 DP-memoized O((V+E)log V) scheduler
│   ├── profiler_runner.py           # cProfile, pstats, tracemalloc runner
│   ├── benchmark_runner.py          # Multi-scale empirical benchmark suite
│   └── visualize_results.py         # Publication-grade plotting module (300 DPI)
├── tests/
│   └── test_codebase_optimization.py # 10 unit & integration test cases (100% PASS)
├── data/                            # Synthetic JSON workflow datasets (50 to 2,500 tasks)
├── results/                         # Profiling dumps (.pstats, .txt) and benchmark outputs (.json, .csv)
├── plots/                           # 4 publication-quality visualization figures
└── docs/
    ├── codebase_analysis.md         # Architecture, modular decomposition, CLOC audit
    ├── profiling_analysis.md        # cProfile call graphs and bottleneck breakdown
    ├── optimization_formulation.md  # Formal mathematical optimization model & proofs
    ├── experimental_analysis.md     # Multi-scale latency, memory, and scaling curves
    ├── viva_questions.md            # 16 in-depth academic viva defense Q&As
    └── README.md                    # Module documentation
```

---

## 3. Algorithmic Transformation (Chapter 6 Optimization)

| Feature | Legacy Baseline (`NaiveWorkflowScheduler`) | Chapter 6 Optimized (`OptimizedWorkflowScheduler`) |
| :--- | :--- | :--- |
| **Downstream Potential** | Unmemoized BFS per candidate: $O(V^2(V+E))$ | Backward DP memoization pass: $O(V+E)$ |
| **Dependency Resolution** | Recursive ancestor check per candidate: $O(V^2(V+E))$ | Incremental in-degree tracking: $O(V+E)$ |
| **Task Selection** | Linear scan across unscheduled set: $O(V^2)$ | Binary priority min-heap (`heapq`): $O(V \log V)$ |
| **Worker Assignment** | Linear scan over worker list: $O(V \cdot W)$ | Min-heap over worker timelines: $O(V \log W)$ |
| **Total Complexity** | **$O(V^3)$** | **$O((V + E)\log V)$** |

---

## 4. Key Empirical Benchmark Findings

Measured on Windows 11 Enterprise (Python 3.13.3) across 4 standard scales:

| Scale | Tasks ($V$) | Edges ($E$) | Baseline Mean Latency | Optimized Mean Latency | Empirical Speedup | Schedule Validity | Makespan Improvement |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Small** | 50 | 157 | 0.001684 s | 0.000134 s | **$12.54\times$** | 100% Valid (0 err) | -14.84% makespan |
| **Medium** | 250 | 1,564 | 0.088873 s | 0.000675 s | **$131.72\times$** | 100% Valid (0 err) | -3.90% makespan |
| **Large** | 1,000 | 8,118 | 3.958761 s | 0.003462 s | **$1,143.39\times$** | 100% Valid (0 err) | -1.91% makespan |
| **XLarge** | 2,500 | 22,919 | 79.771658 s | 0.009713 s | **$8,212.89\times$** | 100% Valid (0 err) | -2.70% makespan |

---

## 5. Quickstart & Verification Commands

### Run Unit and Integration Tests
```bash
python -m unittest track_j_real_world_optimization/tests/test_codebase_optimization.py -v
```

### Run Profiler Harness
```bash
python -m track_j_real_world_optimization.src.profiler_runner
```

### Run Multi-Scale Benchmark Suite
```bash
python -m track_j_real_world_optimization.src.benchmark_runner
```

### Generate Publication Plots
```bash
python -m track_j_real_world_optimization.src.visualize_results
```
