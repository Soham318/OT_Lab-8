# Track F: Compiler Optimization

> **Assignment 8**: Optimize Anything — 14-Day Vibe-Coding Challenge  
> **Repository Module**: `track_f_compiler_optimization/`  
> **Status**: Complete & Verified (11/11 Automated Unit Tests Passing)  
> **Platform**: Windows 11, Python 3.13.3, NumPy 2.5.2, SciPy 1.18.1

---

## 1. Module Overview

Track F implements a self-contained, demonstrable mini-compiler and optimization pass pipeline for an imperative integer programming language (`MiniLang`). The system supports variables, arithmetic operations, conditionals (`if`/`else`), loops (`while`), and observable `print` output:

1. **Frontend**:
   - **Lexer** (`src/lexer.py`): Converts source text into tokens, tracking line/column locations and stripping comments (`#`, `//`).
   - **Parser** (`src/parser.py`): Recursive descent LL(1) parser enforcing standard operator precedence and constructing typed AST nodes.
   - **Semantic Analyzer** (`src/semantic_analyzer.py`): Builds symbol tables, verifies integer types, and enforces declaration-before-use (catching undefined variables).
2. **Intermediate Representation (IR)**:
   - **3AC Generator** (`src/ir_generator.py`): Translates AST into linearized Three-Address-Code (`IRInstruction`) with temporaries (`t0`, `t1`) and jump labels.
   - **Virtual Machine Interpreter** (`src/interpreter.py`): Executes 3AC instructions, tracking cycle step counts and elapsed runtime with safety step limits.
3. **Five Compiler Optimization Passes** (`src/optimizer.py`):
   - **Constant Folding (CF)**: Evaluates compile-time constant arithmetic, comparisons, and conditional branches.
   - **Constant Propagation (CP)**: Propagates constant literals across variables within basic blocks.
   - **Strength Reduction (SR)**: Replaces expensive operations ($x \times 2 \to x + x$, $x \times 1 \to x$, $x \times 0 \to 0$, $x / 1 \to x$).
   - **Common Subexpression Elimination (CSE)**: Canonicalizes commutative operations and reuses previously computed subexpressions.
   - **Dead Code Elimination (DCE)**: Backward liveness analysis pruning unread temporaries and unreachable code blocks while preserving observable side effects.
4. **Fixpoint Optimization Pipeline**: Iteratively applies passes until the instruction sequence stabilizes ($IR_{t+1} == IR_t$).
5. **Pass Selection Optimization Model** (`src/pass_selector.py`): Formulates compiler pass selection under compilation budgets as a Binary Integer Linear Program (BILP), solved via SciPy MILP (`scipy.optimize.milp`) and verified against exhaustive combinatorial search.

---

## 2. Directory Layout

```
track_f_compiler_optimization/
├── docs/
│   ├── language_specification.md    # Formal EBNF grammar, operators, and types
│   ├── compiler_architecture.md     # Pipeline flow, 3AC instruction set, and VM design
│   ├── optimization_methodology.md  # Pass transformations, before/after IR, and BILP model
│   ├── experimental_analysis.md     # Detailed benchmarks across 5 representative programs
│   └── viva_questions.md            # 16 academic viva defense Q&As
├── experiments/
│   ├── run_compiler_benchmarks.py   # 5-program benchmark suite (unopt vs opt)
│   └── run_pass_selection_study.py  # SciPy MILP pass selection across budget thresholds
├── plots/
│   ├── 01_ir_instruction_count_before_vs_after.png
│   ├── 02_runtime_before_vs_after.png
│   ├── 03_code_size_reduction.png
│   └── 04_compile_time_overhead_vs_runtime_savings.png
├── results/
│   ├── compiler_benchmark_results.json / .csv
│   └── pass_selection_results.json / .csv
├── src/
│   ├── __init__.py
│   ├── ast_nodes.py                 # Dataclass AST definitions
│   ├── compiler.py                  # High-level pipeline driver
│   ├── interpreter.py               # 3AC Virtual Machine / Interpreter
│   ├── ir.py                        # Three-Address-Code instruction structure
│   ├── ir_generator.py              # AST-to-3AC code generator
│   ├── lexer.py                     # Tokenizer with line/col tracking
│   ├── optimizer.py                 # CF, CP, SR, CSE, DCE passes & pipeline
│   ├── parser.py                    # Recursive descent parser
│   ├── pass_selector.py             # BILP Pass Selection optimization model
│   ├── semantic_analyzer.py         # Type checking & scope validation
│   └── visualize_results.py         # Publication-ready Matplotlib figure generator
└── tests/
    ├── __init__.py
    └── test_compiler.py             # 11 automated unit tests
```

---

## 3. Quickstart & Verification Commands

All experiments and tests are executed from the repository root:

### Run Automated Unit Tests
```bash
python -m unittest discover -s track_f_compiler_optimization/tests -v
```
*(Expected: 11 tests passing in ~0.02s)*

### Run Benchmarks
```bash
# 1. Compiler Benchmark Suite (Unoptimized vs. Optimized IR)
python track_f_compiler_optimization/experiments/run_compiler_benchmarks.py

# 2. Compiler Pass Selection BILP Study
python track_f_compiler_optimization/experiments/run_pass_selection_study.py
```

### Regenerate Visualizations
```bash
python -m track_f_compiler_optimization.src.visualize_results
```

---

## 4. Key Experimental Findings

| Benchmark Program | Unopt IR Count | Opt IR Count | Code Size Reduction | Dynamic Cycle Reduction | Execution Speedup | Compile Overhead | Output Parity |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`arithmetic_heavy`** | 20 | **1** | **-95.0%** | **-95.0%** | **24.24x** | 0.266 ms | **Verified** ([2100]) |
| **`repeated_expressions`** | 22 | **1** | **-95.5%** | **-95.5%** | **22.21x** | 0.165 ms | **Verified** ([2067]) |
| **`dead_assignments`** | 16 | **5** | **-68.8%** | **-61.5%** | **3.99x** | 0.089 ms | **Verified** ([100]) |
| **`loop_heavy`** | 22 | **19** | **-13.6%** | **-17.6%** (600 cycles) | **1.40x** | 0.169 ms | **Verified** ([131000]) |
| **`combined_pipeline`** | 28 | **23** | **-17.9%** | **-15.8%** (302 cycles) | **1.31x** | 0.170 ms | **Verified** ([208000]) |

- **Pass Selection Model**: SciPy MILP achieved **$0.00\%$ optimality gap** across all compile-time budgets compared to exhaustive search over all 32 pass subsets.
- **Semantic Equivalence**: 100% output parity verified across all unoptimized vs. optimized executions.

---

## 5. Scope & Limitations

1. **Instruction Set Scope**: Designed for scalar 64-bit integer computation. Does not implement floating-point arithmetic, heap pointers, structs, or functions.
2. **Local vs. Global CSE**: Common Subexpression Elimination operates within basic blocks. Global CSE across the complete control-flow graph would require global value numbering or SSA form.
3. **Phase Ordering**: The BILP model optimizes binary pass presence under compile-time budgets, but does not solve the non-commutative pass sequencing (phase ordering) problem.

