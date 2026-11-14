r"""
QAOA Multi-Depth Benchmark on Max-Cut
Track C: Quantum Optimization
Assignment 8 - Optimize Anything

Evaluates QAOA across circuit depths p \in {1, 2, 3} on:
  1. 4-node Cycle Graph
  2. 5-node Random Graph
Compares approximation ratio \alpha, expected cut, sampled cut, and classical optimum.
"""

import json
import os
import sys
import time
from typing import Dict, List, Any
import numpy as np

from track_c_quantum_optimization.src.qaoa import QAOAMaxCutSolver

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def run_qaoa_experiments() -> Dict[str, Any]:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print("Running Track C QAOA Multi-Depth Max-Cut Benchmarks...")

    # Problem 1: 4-node cycle graph
    edges_4cycle = [(0, 1, 1.0), (1, 2, 1.0), (2, 3, 1.0), (3, 0, 1.0)]

    # Problem 2: 5-node connected graph
    edges_5node = [
        (0, 1, 1.0), (1, 2, 1.0), (2, 3, 1.0), (3, 4, 1.0), (4, 0, 1.0),
        (0, 2, 1.5), (1, 3, 1.5)
    ]

    benchmarks = [
        ("4-Node Cycle", 4, edges_4cycle, [1, 2, 3]),
        ("5-Node Graph", 5, edges_5node, [1, 2])
    ]

    all_records = []
    csv_rows = []

    for graph_name, num_nodes, edges, depths in benchmarks:
        print(f"  Evaluating '{graph_name}' (N={num_nodes}, |E|={len(edges)})...")
        for p in depths:
            qaoa = QAOAMaxCutSolver(num_nodes=num_nodes, edges=edges, p=p)
            res = qaoa.optimize(method="COBYLA", max_iters=100, seed=42)

            rec = {
                "graph": graph_name,
                "num_nodes": num_nodes,
                "num_edges": len(edges),
                "p_depth": p,
                "num_parameters": 2 * p,
                "expected_cut": round(res.expected_cut_value, 4),
                "best_sampled_cut": round(res.best_sampled_cut, 4),
                "best_bitstring": res.best_bitstring,
                "classical_max_cut": round(res.classical_max_cut, 4),
                "approximation_ratio": round(res.approximation_ratio, 4),
                "runtime_ms": round(res.execution_time_ms, 2),
                "iterations": res.optimization_iterations,
                "cost_history": [round(c, 4) for c in res.cost_history[::max(1, len(res.cost_history)//25)]]
            }
            all_records.append(rec)
            csv_rows.append(rec)
            print(f"    p={p} | Expected Cut={res.expected_cut_value:.3f} | Approx Ratio={res.approximation_ratio*100:.1f}% | Runtime={res.execution_time_ms:.1f}ms")

    # Save output
    json_path = os.path.join(RESULTS_DIR, "qaoa_benchmark_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2)

    csv_path = os.path.join(RESULTS_DIR, "qaoa_benchmark_summary.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("Graph,NumNodes,NumEdges,PDepth,NumParams,ExpectedCut,SampledCut,BestBitstring,ClassicalMaxCut,ApproxRatioPct,RuntimeMs,Iterations\n")
        for r in csv_rows:
            f.write(f'"{r["graph"]}",{r["num_nodes"]},{r["num_edges"]},{r["p_depth"]},{r["num_parameters"]},{r["expected_cut"]},{r["best_sampled_cut"]},"{r["best_bitstring"]}",{r["classical_max_cut"]},{r["approximation_ratio"]*100:.2f},{r["runtime_ms"]},{r["iterations"]}\n')

    print(f"QAOA benchmark completed:\n  JSON: {json_path}\n  CSV:  {csv_path}")
    return {"results": all_records}


if __name__ == "__main__":
    run_qaoa_experiments()

