# Empirical Experimental Analysis and Benchmarking
**Track J: Real-World Codebase Optimization**  
**Module**: Enterprise Workflow DAG Scheduling & Resource Allocation Engine

---

## 1. Experimental Setup & Benchmarking Methodology

To rigorously validate the computational efficiency and correctness of the Chapter 6 Dynamic Programming optimization, extensive empirical benchmarking was performed across four orders of magnitude:

- **Host System**: Windows 11 Enterprise (x86_64)
- **Python Runtime**: Python 3.13.3 (64-bit)
- **Computing Cluster**: Simulated 8-worker cluster with 32 total vCPUs and 32,768 MB memory
- **Workflow Topology**: Layered DAGs with controlled edge density synthesized using reproducible random seeds (Seed 42)
- **Timing Protocol**:
  - High-resolution timing via `time.perf_counter()`.
  - Exactly 1 warm-up run per scale (discarded from metrics to avoid cold-cache and JIT artifacts).
  - Multiple measured repetitions: 5 repetitions for Small, Medium, and Large; 3 repetitions for Extra-Large baseline (due to its ~79.8s per-run runtime).
  - Metrics collected: Mean, Median, Minimum, Maximum, and Standard Deviation of execution time.
- **Memory Profiling**: `tracemalloc` peak heap allocation tracking.
- **Correctness Verification**: 100% verification against the formal validator `validate_schedule_correctness` checking completeness, duration integrity, precedence satisfaction, and worker mutual exclusivity.

---

## 2. Multi-Scale Empirical Performance Results

The table below summarizes the exact measured benchmark results from `results/benchmark_results.json`:

| Scale | Tasks ($V$) | Edges ($E$) | Baseline Mean Time (s) | Baseline Median (s) | Optimized Mean Time (s) | Optimized Median (s) | Empirical Speedup | Peak RAM Base (KB) | Peak RAM Opt (KB) | Valid? |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Small** | 50 | 157 | **0.001684 s** | 0.001525 s | **0.000134 s** | 0.000131 s | **12.54x** | 16.26 KB | 15.67 KB | **PASS** |
| **Medium** | 250 | 1,564 | **0.088873 s** | 0.088088 s | **0.000675 s** | 0.000676 s | **131.72x** | 67.96 KB | 71.56 KB | **PASS** |
| **Large** | 1,000 | 8,118 | **3.958761 s** | 3.823956 s | **0.003462 s** | 0.003478 s | **1,143.39x** | 267.46 KB | 290.71 KB | **PASS** |
| **XLarge** | 2,500 | 22,919 | **79.771658 s** | 49.595169 s | **0.009713 s** | 0.009800 s | **8,212.89x** | 803.15 KB | 657.08 KB | **PASS** |

---

## 3. Asymptotic Scaling Analysis

### Theoretical vs. Empirical Growth Rates

1. **Baseline Complexity ($O(V^3)$)**:
   - When scaling from Medium ($V = 250$) to Large ($V = 1,000$), problem size increases by a factor of 4.
   - Theoretical cubic scaling: $4^3 = 64\times$.
   - Empirical scaling: $\frac{3.959}{0.0889} \approx 44.5\times$, adhering strongly to cubic behavior considering varying graph density.
   - When scaling from Large ($V = 1,000$) to XLarge ($V = 2,500$), size increases by $2.5\times$.
   - Theoretical scaling: $2.5^3 = 15.6\times$.
   - Empirical scaling: $\frac{79.77}{3.959} \approx 20.15\times$, accelerating due to large queue and set lookup overhead.

2. **Optimized Complexity ($O((V+E)\log V)$)**:
   - For $V = 50$, $T = 0.134$ ms.
   - For $V = 250$, $T = 0.675$ ms.
   - For $V = 1,000$, $T = 3.462$ ms.
   - For $V = 2,500$, $T = 9.713$ ms.
   - Execution time scales sub-quadratically and near-linearly with graph edge volume.

3. **Speedup Scaling Curve**:
   - The speedup ratio scales super-linearly as $\Theta(V^2 / \log V)$:
     $$\text{Small (50 tasks)}: 12.5\times \longrightarrow \text{Medium (250 tasks)}: 131.7\times \longrightarrow \text{Large (1,000 tasks)}: 1,143.4\times \longrightarrow \text{XLarge (2,500 tasks)}: 8,212.9\times$$
   - This empirically validates that as enterprise workflow graphs scale, the Chapter 6 DP optimization delivers exponentially increasing efficiency dividends.

---

## 4. Schedule Makespan and Quality Comparison

A critical concern in algorithmic optimization is ensuring that computational speedup does not come at the expense of solution quality. 

| Scale | Baseline Makespan ($C_{\max}$) | Optimized Makespan ($C_{\max}$) | Difference ($\Delta$) | Improvement (%) |
| :---: | :---: | :---: | :---: | :---: |
| **Small** | 263.19 s | 224.14 s | -39.05 s | **-14.84%** |
| **Medium** | 1209.85 s | 1162.65 s | -47.20 s | **-3.90%** |
| **Large** | 4510.53 s | 4424.17 s | -86.36 s | **-1.91%** |
| **XLarge** | 11234.75 s | 10931.65 s | -303.10 s | **-2.70%** |

### Key Takeaways:
1. **Makespan Improvement**: Across all four instances, the Chapter 6 DP scheduler consistently produces **$1.91\% - 14.84\%$ shorter makespans** than the baseline.
2. **Mechanism**: The baseline relied on unweighted descendant counts (`_collect_all_descendants`), which treats short downstream tasks identically to long tasks. The Chapter 6 DP scheduler computes exact downstream critical-path potentials $V(i) = d_i + \max V(j)$, prioritizing tasks that unlock the heaviest downstream bottlenecks first.
3. **Adherence to Lower Bounds**: In all cases, the makespan satisfies $C_{\max} \ge \max(LB_{CP}, LB_{\text{res}})$, confirming mathematical validity.

---

## 5. Memory Footprint and Space Complexity

- **Space Complexity**: Both algorithms require $O(V + E)$ auxiliary memory to store graph adjacency.
- **Incremental Heap Overhead**: The optimized scheduler stores priority heap tuples $( -p_i, -V(i), i )$ and a worker min-heap of size $W$.
- **Empirical Peak RAM**:
  - Small: Baseline 16.26 KB vs. Optimized 15.67 KB (-0.59 KB)
  - Medium: Baseline 67.96 KB vs. Optimized 71.56 KB (+3.60 KB, +5.3%)
  - Large: Baseline 267.46 KB vs. Optimized 290.71 KB (+23.25 KB, +8.7%)
  - XLarge: Baseline 803.15 KB vs. Optimized 657.08 KB (-146.07 KB, -18.2% due to eliminating massive BFS queue allocations)
- The memory footprint remains well under 1 MB even at 2,500 tasks, confirming that the $8,212\times$ speedup is achieved without any memory bloat.
