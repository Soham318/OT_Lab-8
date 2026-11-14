"""
Storage Budget Sweep Experiment for Track H DBMS Index Selection.
Sweeps storage budgets B from 1.0 MB to 10.0 MB and compares:
1. Greedy Marginal Benefit Selection
2. Exact Integer Linear Programming (SciPy HiGHS)
3. Exhaustive Combinatorial Search (2^12 = 4096 subsets)

Records score, storage used, optimality gaps, and solver execution times.
"""

import os
import json
import csv
import time
from track_h_dbms_optimization.src.index_candidates import get_candidate_indexes
from track_h_dbms_optimization.src.workload import get_workload_queries
from track_h_dbms_optimization.src.greedy_selector import run_greedy_index_selection
from track_h_dbms_optimization.src.ilp_selector import solve_ilp_index_selection, solve_exhaustive_index_selection

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_budget_sweep():
    candidates = get_candidate_indexes()
    queries = get_workload_queries()

    budgets = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0, 10.0]
    sweep_results = []

    print("=" * 85)
    print(f"{'Budget (MB)':<12} | {'Greedy (Score / MB)':<22} | {'ILP (Score / MB)':<22} | {'Gap (%)':<8} | {'Matches Opt?':<12}")
    print("=" * 85)

    csv_rows = []

    for b in budgets:
        # Solve Greedy
        t0 = time.perf_counter()
        g_sol = run_greedy_index_selection(candidates, queries, b)
        g_time = (time.perf_counter() - t0) * 1000

        # Solve ILP
        t1 = time.perf_counter()
        i_sol = solve_ilp_index_selection(candidates, queries, b)
        i_time = (time.perf_counter() - t1) * 1000

        # Solve Exhaustive
        t2 = time.perf_counter()
        e_sol = solve_exhaustive_index_selection(candidates, queries, b)
        e_time = (time.perf_counter() - t2) * 1000

        opt_score = e_sol["total_benefit_score"]
        g_score = g_sol["total_benefit_score"]
        i_score = i_sol["total_benefit_score"]

        gap_pct = 0.0
        if opt_score > 0:
            gap_pct = ((opt_score - g_score) / opt_score) * 100.0

        ilp_matches_opt = (abs(i_score - opt_score) < 1e-4)

        g_str = f"{g_score:.0f} / {g_sol['total_storage_mb']:.1f} MB"
        i_str = f"{i_score:.0f} / {i_sol['total_storage_mb']:.1f} MB"
        match_str = "YES" if ilp_matches_opt else "NO"

        print(f"{b:<12.1f} | {g_str:<22} | {i_str:<22} | {gap_pct:<8.2f} | {match_str:<12}")

        record = {
            "budget_mb": b,
            "greedy": {
                "indexes": g_sol["selected_indexes"],
                "score": g_score,
                "storage_mb": g_sol["total_storage_mb"],
                "runtime_ms": round(g_time, 3)
            },
            "ilp": {
                "indexes": i_sol["selected_indexes"],
                "score": i_score,
                "storage_mb": i_sol["total_storage_mb"],
                "runtime_ms": round(i_time, 3)
            },
            "exhaustive": {
                "indexes": e_sol["selected_indexes"],
                "score": opt_score,
                "storage_mb": e_sol["total_storage_mb"],
                "runtime_ms": round(e_time, 3)
            },
            "optimality_gap_pct": round(gap_pct, 2),
            "ilp_verified_exact": ilp_matches_opt
        }
        sweep_results.append(record)

        csv_rows.append([
            b,
            g_score, g_sol["total_storage_mb"], ";".join(g_sol["selected_indexes"]), round(g_time, 2),
            i_score, i_sol["total_storage_mb"], ";".join(i_sol["selected_indexes"]), round(i_time, 2),
            opt_score, e_sol["total_storage_mb"], ";".join(e_sol["selected_indexes"]), round(e_time, 2),
            round(gap_pct, 2), ilp_matches_opt
        ])

    print("=" * 85)

    # Save JSON
    json_path = os.path.join(RESULTS_DIR, "budget_sweep_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sweep_results, f, indent=2)
    print(f"\n[INFO] Sweep JSON saved to: {json_path}")

    # Save CSV
    csv_path = os.path.join(RESULTS_DIR, "budget_sweep_results.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Budget_MB",
            "Greedy_Score", "Greedy_Storage_MB", "Greedy_Indexes", "Greedy_Runtime_ms",
            "ILP_Score", "ILP_Storage_MB", "ILP_Indexes", "ILP_Runtime_ms",
            "Opt_Score", "Opt_Storage_MB", "Opt_Indexes", "Opt_Runtime_ms",
            "Optimality_Gap_Pct", "ILP_Verified_Exact"
        ])
        writer.writerows(csv_rows)
    print(f"[INFO] Sweep CSV saved to: {csv_path}")

    return sweep_results

if __name__ == "__main__":
    run_budget_sweep()
