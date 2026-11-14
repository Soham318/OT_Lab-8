r"""Experiment 1: Compiler Benchmark Suite.

Evaluates unoptimized vs. optimized IR across 5 representative benchmark programs:
1. Arithmetic-Heavy: Constant folding, propagation & strength reduction
2. Redundant Expressions: Common subexpression elimination (CSE)
3. Dead Code: Dead assignments, unread variables & unreachable branches (DCE)
4. Loop-Heavy: Repetitive loop executions with redundant expressions
5. Combined Pipeline: Comprehensive multi-stage workload

Measures:
- IR instruction count reduction
- Execution step count reduction (virtual machine cycles)
- Wall-clock execution time reduction
- Compile-time pass overhead vs. runtime speedup
- Strict output parity verification
"""

import csv
import json
import os
import sys
import time
from typing import Any, Dict, List

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath("."))

from track_f_compiler_optimization.src.compiler import MiniCompiler


BENCHMARK_PROGRAMS = {
    "arithmetic_heavy": """
        # Constant folding, propagation, and strength reduction
        c1 = 100 * 2;
        c2 = 50 + 25 * 4;
        base = c1 + c2;
        
        # Strength reduction targets
        x = base * 2;
        y = x * 1;
        z = y + 0;
        w = z * 0;
        
        result = x + y + z + w;
        print(result);
    """,

    "repeated_expressions": """
        # Common Subexpression Elimination benchmark
        a = 15;
        b = 27;
        
        # Subexpressions (a * b) and (a + b) repeated multiple times
        term1 = (a * b) + (a + b);
        term2 = (a * b) - (a + b);
        term3 = (a * b) + (a + b);
        term4 = (a * b) * 2;
        
        final_val = term1 + term2 + term3 + term4;
        print(final_val);
    """,

    "dead_assignments": """
        # Dead Code Elimination benchmark
        x = 42;
        dead1 = x * 10 + 500;
        dead2 = dead1 * dead1;
        
        active = x + 8;
        
        # Dead conditional block (never taken)
        if (0) {
            dead_branch = active * 999;
            print(dead_branch);
        }
        
        final_active = active * 2;
        print(final_active);
    """,

    "loop_heavy": """
        # Loop computation with redundant calculations inside iterations
        total = 0;
        k = 1;
        limit = 200;
        
        while (k <= limit) {
            # Redundant invariant arithmetic and duplicate expressions
            invariant = 10 * 5 + 2;
            dup1 = k * 3;
            dup2 = k * 3;
            total = total + dup1 + dup2 + invariant;
            k = k + 1;
        }
        print(total);
    """,

    "combined_pipeline": """
        # Comprehensive realistic program combining all optimization targets
        scale = 4 * 5;
        offset = 100 / 2;
        
        total = 0;
        idx = 0;
        max_idx = 100;
        
        while (idx < max_idx) {
            # Common subexpression
            e1 = idx * scale;
            e2 = idx * scale;
            
            # Dead temporary
            dead_temp = e1 * 0 + 9999;
            
            # Strength reduction
            step = e1 + e2 + (offset * 2);
            total = total + step;
            idx = idx + 1;
        }
        
        print(total);
    """,
}


def run_compiler_benchmarks() -> List[Dict[str, Any]]:
    print("=" * 70)
    print("RUNNING EXPERIMENT 1: Mini-Compiler Optimization Benchmark Suite")
    print("=" * 70)

    compiler = MiniCompiler()
    results = []

    for name, source_code in BENCHMARK_PROGRAMS.items():
        print(f"\n--- Benchmark: {name} ---")

        # Compile unoptimized and optimized
        ast, unopt_ir, opt_ir, opt_report = compiler.compile(source_code, optimize=True)

        unopt_count = len(unopt_ir)
        opt_count = len(opt_ir)
        count_reduction = unopt_count - opt_count
        count_red_pct = (count_reduction / unopt_count) * 100.0 if unopt_count > 0 else 0.0

        # Execute unoptimized (repeated for timing reliability)
        repeats = 10
        unopt_steps = 0
        unopt_times = []
        unopt_output = None

        for _ in range(repeats):
            res = compiler.interpreter.execute(unopt_ir)
            unopt_times.append(res["execution_time_ms"])
            unopt_steps = res["step_count"]
            unopt_output = res["output"]

        # Execute optimized
        opt_steps = 0
        opt_times = []
        opt_output = None

        for _ in range(repeats):
            res = compiler.interpreter.execute(opt_ir)
            opt_times.append(res["execution_time_ms"])
            opt_steps = res["step_count"]
            opt_output = res["output"]

        # Strict semantic verification
        parity_verified = (unopt_output == opt_output)
        if not parity_verified:
            raise RuntimeError(
                f"SEMANTIC MISMATCH in {name}! Unopt: {unopt_output} != Opt: {opt_output}"
            )

        mean_unopt_time = float(sum(unopt_times) / len(unopt_times))
        mean_opt_time = float(sum(opt_times) / len(opt_times))
        speedup = mean_unopt_time / mean_opt_time if mean_opt_time > 0 else 1.0
        step_reduction = unopt_steps - opt_steps
        step_red_pct = (step_reduction / unopt_steps) * 100.0 if unopt_steps > 0 else 0.0

        compile_overhead_ms = opt_report["total_compile_time_ms"]

        print(f"  IR Instructions: {unopt_count} -> {opt_count} (-{count_reduction}, -{count_red_pct:.1f}%)")
        print(f"  Execution Steps: {unopt_steps} -> {opt_steps} (-{step_reduction}, -{step_red_pct:.1f}%)")
        print(f"  Wall-Clock Time: {mean_unopt_time:.3f} ms -> {mean_opt_time:.3f} ms (Speedup: {speedup:.2f}x)")
        print(f"  Compile Overhead: {compile_overhead_ms:.3f} ms")
        print(f"  Output Parity:    {unopt_output} == {opt_output} -> {parity_verified}")

        results.append({
            "name": name,
            "unoptimized_ir_count": unopt_count,
            "optimized_ir_count": opt_count,
            "ir_reduction_count": count_reduction,
            "ir_reduction_pct": round(count_red_pct, 2),
            "unoptimized_steps": unopt_steps,
            "optimized_steps": opt_steps,
            "step_reduction_pct": round(step_red_pct, 2),
            "unoptimized_time_ms": round(mean_unopt_time, 4),
            "optimized_time_ms": round(mean_opt_time, 4),
            "runtime_speedup": round(speedup, 2),
            "compile_overhead_ms": round(compile_overhead_ms, 3),
            "output": unopt_output,
            "semantic_parity": parity_verified,
        })

    os.makedirs("track_f_compiler_optimization/results", exist_ok=True)
    json_path = "track_f_compiler_optimization/results/compiler_benchmark_results.json"
    csv_path = "track_f_compiler_optimization/results/compiler_benchmark_summary.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Program", "UnoptIRCount", "OptIRCount", "IRReductionPct",
            "UnoptSteps", "OptSteps", "StepReductionPct",
            "UnoptTimeMs", "OptTimeMs", "Speedup", "CompileOverheadMs", "SemanticParity",
        ])
        for r in results:
            writer.writerow([
                r["name"], r["unoptimized_ir_count"], r["optimized_ir_count"], r["ir_reduction_pct"],
                r["unoptimized_steps"], r["optimized_steps"], r["step_reduction_pct"],
                r["unoptimized_time_ms"], r["optimized_time_ms"], r["runtime_speedup"],
                r["compile_overhead_ms"], r["semantic_parity"],
            ])

    print(f"\n[DONE] Saved benchmark results to {json_path} and {csv_path}")
    return results


if __name__ == "__main__":
    run_compiler_benchmarks()

