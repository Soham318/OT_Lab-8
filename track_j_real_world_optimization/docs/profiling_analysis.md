# Empirical Profiling and Bottleneck Identification
**Track J: Real-World Codebase Optimization**  
**Tools**: Python standard `cProfile`, `pstats`, and `tracemalloc`

---

## 1. Profiling Methodology & Instrumentation

To identify the exact computational bottlenecks in the workflow scheduling engine, rigorous profiling was conducted under identical hardware and software conditions:
- **Operating System**: Windows 11 Enterprise (x86_64)
- **Runtime**: Python 3.13.3
- **Workload**: Medium Benchmark Workflow DAG ($V = 250$ tasks, $E = 1,564$ edges, 15 layers)
- **Cluster**: 4 homogeneous worker nodes ($W = 4$)
- **Deterministic Seed**: 42

The profiling harness (`src/profiler_runner.py`) uses:
1. `cProfile.Profile()` to record function call counts, primitive calls, per-call execution time, and cumulative execution time.
2. `pstats.Stats` sorted by `cumulative` time to isolate the most expensive code paths.
3. `tracemalloc` to track peak heap allocations and memory churn.

---

## 2. Baseline Profiling Results (Unoptimized Implementation)

### Summary Statistics
- **Total Function Calls**: **1,757,054**
- **Cumulative Execution Time**: **2.20467 seconds**
- **Peak Memory Allocation**: **77.5 KB**
- **Schedule Correctness**: Valid (Makespan = 2122.58 s, 0 violations)

### Cumulative Time Breakdown (Top Hotspots)

From `results/original_profiling.txt`:

| Rank | Function / Method | Filename : Line | Cumulative Time (s) | % of Total Time | Call Count | Per-Call Time ($\mu$s) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **1** | `schedule()` | `baseline_scheduler.py:112` | **2.205** | 100.0% | 1 | 2,204,670 |
| **2** | `compute_dynamic_priority` | `baseline_scheduler.py:77` | **1.154** | **52.3%** | 31,375 | 36.8 |
| **3** | `_collect_all_descendants` | `baseline_scheduler.py:91` | **1.150** | **52.2%** | 31,375 | 36.7 |
| **4** | `is_task_ready` | `baseline_scheduler.py:35` | **1.030** | **46.7%** | 31,375 | 32.8 |
| **5** | `_collect_all_ancestors` | `baseline_scheduler.py:46` | **1.018** | **46.2%** | 31,375 | 32.4 |
| **6** | `<method 'pop' of 'list'>` | Built-in | 0.285 | 12.9% | 889,992 | 0.32 |
| **7** | `<method 'get' of 'dict'>` | Built-in | 0.089 | 4.0% | 236,053 | 0.38 |
| **8** | `<method 'add' of 'set'>` | Built-in | 0.082 | 3.7% | 258,231 | 0.32 |

### Root-Cause Diagnosis

The profiling evidence reveals an overwhelming bottleneck:
1. **99.0% of Total Runtime** is concentrated inside two functions:
   - `_collect_all_descendants` (52.3%)
   - `_collect_all_ancestors` (46.7%)
2. Over **31,375 invocations** of graph reachability occur for a graph of only 250 tasks!
   - In each scheduling step $k \in \{1, \dots, V\}$, the algorithm iterates over all remaining unscheduled tasks ($|U| \approx V - k$).
   - For every unscheduled candidate task, it performs two full graph BFS traversals: one upward to check ancestors, and one downward to sum descendant task durations.
3. List `pop` was executed **889,992 times** and dictionary lookups **236,053 times** solely to maintain BFS queues for these redundant traversals.

---

## 3. Optimized DP Profiling Results (Chapter 6 Implementation)

### Summary Statistics
- **Total Function Calls**: **7,629** (a **99.57% reduction** in calls!)
- **Cumulative Execution Time**: **0.01055 seconds** (a **209.04x speedup**)
- **Peak Memory Allocation**: **81.0 KB**
- **Schedule Correctness**: Valid (Makespan = 2076.18 s, 0 violations)

### Cumulative Time Breakdown (Optimized Profile)

From `results/optimized_profiling.txt`:

| Rank | Function / Method | Filename : Line | Cumulative Time (s) | % of Total Time | Call Count | Per-Call Time ($\mu$s) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **1** | `schedule()` | `optimized_scheduler.py:75` | **0.0105** | 100.0% | 1 | 10,546 |
| **2** | `_precompute_critical_path_potentials` | `optimized_scheduler.py:42` | **0.0006** | 5.7% | 1 | 600 |
| **3** | `heappop` / `heappush` | Built-in | 0.0004 | 3.8% | 1,000 | 0.40 |
| **4** | Dictionary & Set Lookups | Built-in | 0.0003 | 2.8% | 4,200 | 0.07 |

---

## 4. Comparative Profiling Summary

| Metric | Baseline (Naive $O(V^3)$) | Optimized (DP $O((V+E)\log V)$) | Delta / Improvement |
| :--- | :---: | :---: | :---: |
| **Total Function Calls** | 1,757,054 calls | 7,629 calls | **-99.57% calls** |
| **Execution Time** | 2.20467 s | 0.01055 s | **209.04x Speedup** |
| **Redundant Graph Traversals** | 31,375 traversals | 1 backward DP pass | **-99.997% traversals** |
| **List Pop Operations** | 889,992 pops | 0 BFS pops (heap only) | **Eliminated BFS queues** |
| **Peak Memory Allocation** | 77.5 KB | 81.0 KB | +3.5 KB (+4.5% overhead) |
| **Schedule Validity** | 100% Valid (0 errors) | 100% Valid (0 errors) | **Zero Regression** |
| **Schedule Makespan** | 2122.58 s | 2076.18 s | **-46.40 s (-2.18% better)** |

### Architectural Conclusion
By applying Chapter 6 Dynamic Programming (memoizing downstream critical path values in a single $O(V + E)$ pass) and maintaining state incrementally via in-degree tracking and binary min-heaps, we completely eliminated the 99% graph traversal overhead while maintaining 100% schedule validity and slightly improving the makespan.
