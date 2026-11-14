# Track F: Compiler Optimization — Empirical Experimental Analysis

> **Course**: Optimization Techniques — Assignment 8  
> **Module**: `track_f_compiler_optimization/`  
> **Verification Status**: 100% Reproducible from raw data in `results/`  
> **Environment**: Windows 11, Python 3.13.3, NumPy 2.5.2, SciPy 1.18.1

---

## 1. Benchmark Suite Description

To evaluate compiler optimization effectiveness across diverse computing patterns, five representative programs were constructed:
1. **`arithmetic_heavy`**: Deeply nested arithmetic expressions, constant folding opportunities ($100 \times 2, 50 + 25 \times 4$), constant propagation, strength reduction ($x \times 2 \to x + x, x \times 1 \to x, w \times 0 \to 0$).
2. **`repeated_expressions`**: Multiple redundant evaluations of subexpressions $(a \times b)$ and $(a + b)$ within identical basic blocks, targeted by Common Subexpression Elimination (CSE).
3. **`dead_assignments`**: Heavy dead computations ($x \times 10 + 500, \text{dead}_1 \times \text{dead}_1$) and an unreachable conditional branch (`if (0)`), targeted by Dead Code Elimination (DCE).
4. **`loop_heavy`**: A 200-iteration while loop containing invariant arithmetic and duplicate expressions inside the loop body, testing dynamic cycle reduction.
5. **`combined_pipeline`**: A realistic 100-iteration algorithm combining scaling factors, common subexpressions, dead variables, and strength reduction.

---

## 2. Quantitative Benchmark Results

All execution times and step counts are averaged over 10 repeated trials on unoptimized vs. optimized IR:

| Benchmark Program | Unopt IR Count | Opt IR Count | IR Size Reduction (%) | Unopt Exec Steps | Opt Exec Steps | Dynamic Step Reduction (%) | Unopt Time (ms) | Opt Time (ms) | Runtime Speedup | Compile Overhead (ms) | Output Parity Verified? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`arithmetic_heavy`** | 20 | **1** | **-95.0%** | 20 | **1** | **-95.0%** | 0.0094 | 0.0004 | **24.24x** | 0.266 | **True** ([2100]) |
| **`repeated_expressions`** | 22 | **1** | **-95.5%** | 22 | **1** | **-95.5%** | 0.0089 | 0.0004 | **22.21x** | 0.165 | **True** ([2067]) |
| **`dead_assignments`** | 16 | **5** | **-68.8%** | 13 | **5** | **-61.5%** | 0.0055 | 0.0014 | **3.99x** | 0.089 | **True** ([100]) |
| **`loop_heavy`** | 22 | **19** | **-13.6%** | 3408 | **2808** | **-17.6%** | 1.2872 | 0.9168 | **1.40x** | 0.169 | **True** ([131000]) |
| **`combined_pipeline`** | 28 | **23** | **-17.9%** | 1912 | **1610** | **-15.8%** | 0.6789 | 0.5182 | **1.31x** | 0.170 | **True** ([208000]) |

---

## 3. In-Depth Analysis of Program Transformations

### 3.1 Collapse of Entire Computations to Single Instructions
In both `arithmetic_heavy` and `repeated_expressions`, the unoptimized programs consisted of 20 to 22 Three-Address-Code instructions. Through synergistic fixpoint iteration:
1. **Iteration 1**: Constant Propagation replaced variables with known constants; Constant Folding evaluated arithmetic operations ($100 \times 2 \to 200$, $25 \times 4 \to 100$).
2. **Iteration 2**: The folded constants propagated into downstream sum expressions, reducing the final output assignment to an immediate constant.
3. **Iteration 3**: Dead Code Elimination identified that intermediate variables (`c1`, `c2`, `base`, `x`, `y`, `z`, `w`) were never used downstream, pruning them all.
4. **Final Result**: The entire program collapsed into a single `print 2100` instruction, achieving a **$95.0\%$ code size reduction** and a **$24.24\times$ execution speedup** while maintaining 100% semantic identity.

### 3.2 Loop Optimization and Dynamic Step Reductions
In `loop_heavy`, the program executes 200 loop iterations. 
- The unoptimized loop body computed `invariant = 10 * 5 + 2` and duplicate terms `dup1 = k * 3`, `dup2 = k * 3` on every single iteration.
- The optimizer folded `invariant` to constant `52`, eliminated the redundant calculation of `dup2` via CSE, and pruned dead variables via DCE.
- **Dynamic Impact**: This eliminated 3 instructions per iteration. Over 200 iterations, total executed virtual machine steps dropped from **3,408 to 2,808** (saving **600 dynamic cycles**, a **$17.6\%$ cycle reduction**), accelerating wall-clock execution time by **$1.40\times$**.

---

## 4. Compiler Pass Selection Optimization (BILP Model)

### 4.1 Budget-Constrained Optimization Results
The Binary Integer Linear Program was solved across five compilation time budgets $C_{\text{budget}} \in [2.0, 11.0]$ using SciPy MILP and compared against exhaustive combinatorial enumeration (32 subsets):

| Compilation Budget $C_{\text{budget}}$ | Selected Optimization Passes | Total Compile Cost | Runtime Benefit | Code Size Benefit | Net Objective Score | Exhaustive Best Value | Optimality Gap |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2.0** | CP | 2.0 | 10.0 | 4.0 | **11.60** | 11.60 | **0.0000e+00** |
| **4.0** | CF + CP | 3.5 | 22.0 | 12.0 | **27.30** | 27.30 | **0.0000e+00** |
| **6.0** | CF + CP + DCE | 6.0 | 27.0 | 26.0 | **38.80** | 38.80 | **0.0000e+00** |
| **8.0** | CF + CP + SR + CSE | 8.0 | 45.0 | 25.0 | **55.90** | 55.90 | **0.0000e+00** |
| **11.0** | CF + CP + SR + CSE + DCE (All) | 10.5 | 50.0 | 39.0 | **67.40** | 67.40 | **0.0000e+00** |

### 4.2 Trade-Off Insights
- **Low Budget ($C \le 4.0$)**: The optimizer selects Constant Propagation and Constant Folding first, as they offer the highest return on investment ($27.30$ net score for only $3.5$ compile latency).
- **Medium Budget ($C = 6.0$)**: Adding Dead Code Elimination boosts the code size reduction benefit from $12.0 \to 26.0$.
- **High Budget ($C \ge 8.0$)**: High-overhead passes such as Common Subexpression Elimination ($C_{\text{CSE}} = 3.5$) become feasible, unlocking major runtime improvements.
- **Optimality**: SciPy MILP achieved $0.00\%$ optimality gap across all budgets, verifying the mathematical formulation against exhaustive search.

---

## 5. Compile-Time Overhead vs. Runtime Amortization

- Compilation overhead across all benchmark programs averaged **$0.17$ ms** (ranging from $0.05$ ms to $0.27$ ms).
- For short-lived single-run scripts, compilation overhead exceeds execution savings.
- However, for programs executing repeatedly in production or running compute-dense loops (e.g. `loop_heavy` running for thousands of iterations), the one-time compile investment ($0.17$ ms) pays for itself within a single execution run.

