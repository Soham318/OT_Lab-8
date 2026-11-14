"""
Comprehensive Benchmark Runner for Railway Reservation DBMS Query Optimization.
Evaluates Baseline, Greedy, and ILP database configurations, recording:
- Query Execution Plans (EXPLAIN QUERY PLAN)
- Per-query latencies (mean, median, min, max) across repeated runs
- Workload runtime and throughput (QPS)
- Physical database and index storage footprint
- SHA-256 cryptographic checksums of query results verifying 100% equivalence
"""

import os
import shutil
import sqlite3
import time
import hashlib
import json
import csv
import numpy as np

from track_h_dbms_optimization.src.schema import create_schema
from track_h_dbms_optimization.src.data_generator import populate_database
from track_h_dbms_optimization.src.workload import get_workload_queries
from track_h_dbms_optimization.src.index_candidates import get_candidate_indexes
from track_h_dbms_optimization.src.greedy_selector import run_greedy_index_selection
from track_h_dbms_optimization.src.ilp_selector import solve_ilp_index_selection, solve_exhaustive_index_selection

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def generate_base_database(db_path, seed=42):
    """Create and populate base railway database."""
    if os.path.exists(db_path):
        os.remove(db_path)

    print(f"Creating base railway database at: {db_path}")
    conn = sqlite3.connect(db_path)
    create_schema(conn)
    row_counts = populate_database(conn, seed=seed, scale_factor=0.6)
    conn.close()
    size_mb = os.path.getsize(db_path) / (1024 * 1024)
    print(f"Base database generated: {size_mb:.2f} MB ({row_counts})")
    return size_mb, row_counts

def apply_indexes_to_db(db_path, index_ids, candidate_indexes):
    """Apply selected candidate indexes to database."""
    index_map = {idx["id"]: idx for idx in candidate_indexes}
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    applied = []
    t_start = time.perf_counter()
    for idx_id in index_ids:
        idx = index_map[idx_id]
        cursor.execute(idx["sql"])
        applied.append(idx["name"])
    conn.commit()
    cursor.execute("ANALYZE;") # Re-analyze database so query planner sees new indexes
    conn.commit()
    conn.close()

    creation_time_s = time.perf_counter() - t_start
    return applied, creation_time_s

def explain_query_plan(conn, sql):
    """Capture EXPLAIN QUERY PLAN tree from SQLite."""
    cursor = conn.cursor()
    cursor.execute(f"EXPLAIN QUERY PLAN {sql}")
    rows = cursor.fetchall()
    # Format plan lines
    plan_lines = [f"selectid={r[0]} order={r[1]} from={r[2]} detail={r[3]}" for r in rows]
    # Check if index was used
    uses_index = any("INDEX" in r[3] for r in rows)
    uses_scan = any("SCAN" in r[3] for r in rows)
    return plan_lines, uses_index, uses_scan

def hash_query_result(rows):
    """Compute SHA-256 hash of query result set to verify result equivalence."""
    hasher = hashlib.sha256()
    for row in rows:
        hasher.update(str(row).encode("utf-8"))
    return hasher.hexdigest()

def benchmark_database_config(config_name, db_path, queries, warmup_runs=1, measured_runs=5):
    """
    Benchmark an SQLite configuration across the query workload.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query_results = {}
    total_measured_time = 0.0
    total_query_executions = 0

    print(f"\n--- Benchmarking Configuration: {config_name} ---")

    for q in queries:
        q_id = q["id"]
        q_name = q["name"]
        sql = q["sql"]

        # 1. Capture query execution plan
        plan_lines, uses_index, uses_scan = explain_query_plan(conn, sql)

        # 2. Warm-up run
        for _ in range(warmup_runs):
            cursor.execute(sql)
            _ = cursor.fetchall()

        # 3. Measured runs
        latencies_ms = []
        result_rows = None

        for _ in range(measured_runs):
            t0 = time.perf_counter()
            cursor.execute(sql)
            result_rows = cursor.fetchall()
            t1 = time.perf_counter()
            latencies_ms.append((t1 - t0) * 1000.0)

        mean_lat = float(np.mean(latencies_ms))
        median_lat = float(np.median(latencies_ms))
        min_lat = float(np.min(latencies_ms))
        max_lat = float(np.max(latencies_ms))
        std_lat = float(np.std(latencies_ms))

        # 4. Result integrity verification
        row_count = len(result_rows)
        res_hash = hash_query_result(result_rows)

        query_results[q_id] = {
            "name": q_name,
            "type": q["type"],
            "weight": q["weight"],
            "mean_ms": round(mean_lat, 3),
            "median_ms": round(median_lat, 3),
            "min_ms": round(min_lat, 3),
            "max_ms": round(max_lat, 3),
            "std_ms": round(std_lat, 3),
            "row_count": row_count,
            "result_hash": res_hash,
            "uses_index": uses_index,
            "uses_scan": uses_scan,
            "plan": plan_lines
        }

        total_measured_time += sum(latencies_ms) / 1000.0
        total_query_executions += measured_runs

        print(f"  {q_id} ({q_name[:30]}): Mean = {mean_lat:6.2f} ms | Median = {median_lat:6.2f} ms | Rows = {row_count:5d} | Uses Index: {uses_index}")

    conn.close()

    db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
    throughput_qps = total_query_executions / total_measured_time if total_measured_time > 0 else 0.0

    return {
        "config_name": config_name,
        "db_size_mb": round(db_size_mb, 2),
        "total_measured_time_s": round(total_measured_time, 3),
        "throughput_qps": round(throughput_qps, 2),
        "query_results": query_results
    }

def run_complete_dbms_study(storage_budget_mb=6.0):
    """
    Run full DBMS query optimization study:
    1. Generate Base DB
    2. Solve Index Selection with Greedy & ILP
    3. Benchmark Baseline, Greedy, and ILP databases
    4. Save results to JSON and CSV
    """
    queries = get_workload_queries()
    candidates = get_candidate_indexes()

    # 1. Base database path
    base_db = os.path.join(DATA_DIR, "railway_baseline.db")
    greedy_db = os.path.join(DATA_DIR, "railway_greedy.db")
    ilp_db = os.path.join(DATA_DIR, "railway_ilp.db")

    base_size_mb, row_counts = generate_base_database(base_db, seed=42)

    # 2. Solve index selection
    print("\n--- Solving Index Selection Problem ---")
    greedy_sol = run_greedy_index_selection(candidates, queries, storage_budget_mb)
    ilp_sol = solve_ilp_index_selection(candidates, queries, storage_budget_mb)
    exhaustive_sol = solve_exhaustive_index_selection(candidates, queries, storage_budget_mb)

    print(f"Greedy Selected ({greedy_sol['total_storage_mb']} MB): {greedy_sol['selected_indexes']} (Score: {greedy_sol['total_benefit_score']})")
    print(f"ILP Selected    ({ilp_sol['total_storage_mb']} MB): {ilp_sol['selected_indexes']} (Score: {ilp_sol['total_benefit_score']})")
    print(f"Exhaustive Opt  ({exhaustive_sol['total_storage_mb']} MB): {exhaustive_sol['selected_indexes']} (Score: {exhaustive_sol['total_benefit_score']})")

    opt_gap = (ilp_sol['total_benefit_score'] - greedy_sol['total_benefit_score']) / ilp_sol['total_benefit_score'] * 100.0 if ilp_sol['total_benefit_score'] > 0 else 0.0
    print(f"Greedy Optimality Gap vs ILP: {opt_gap:.2f}%")

    # 3. Create Greedy DB copy and apply indexes
    shutil.copyfile(base_db, greedy_db)
    greedy_applied, greedy_idx_time = apply_indexes_to_db(greedy_db, greedy_sol["selected_indexes"], candidates)

    # 4. Create ILP DB copy and apply indexes
    shutil.copyfile(base_db, ilp_db)
    ilp_applied, ilp_idx_time = apply_indexes_to_db(ilp_db, ilp_sol["selected_indexes"], candidates)

    # 5. Benchmark each configuration
    baseline_bench = benchmark_database_config("Baseline (No Secondary Indexes)", base_db, queries)
    greedy_bench = benchmark_database_config(f"Greedy Indexes ({greedy_sol['total_storage_mb']} MB)", greedy_db, queries)
    ilp_bench = benchmark_database_config(f"ILP Indexes ({ilp_sol['total_storage_mb']} MB)", ilp_db, queries)

    # 6. Verify Result Equivalence
    print("\n--- Verifying Query Result Parity Across Configurations ---")
    all_matched = True
    for q in queries:
        q_id = q["id"]
        h_base = baseline_bench["query_results"][q_id]["result_hash"]
        h_greedy = greedy_bench["query_results"][q_id]["result_hash"]
        h_ilp = ilp_bench["query_results"][q_id]["result_hash"]

        if h_base == h_greedy == h_ilp:
            print(f"  {q_id}: PASS - 100% Result Hash Match ({h_base[:12]}...)")
        else:
            all_matched = False
            print(f"  {q_id}: FAIL - Result Mismatch! Base={h_base[:8]}, Greedy={h_greedy[:8]}, ILP={h_ilp[:8]}")

    if not all_matched:
        raise RuntimeError("Query result mismatch detected across database configurations!")

    # 7. Package and save results
    study_results = {
        "dataset_rows": row_counts,
        "storage_budget_mb": storage_budget_mb,
        "selection_algorithms": {
            "greedy": greedy_sol,
            "ilp": ilp_sol,
            "exhaustive": exhaustive_sol,
            "greedy_optimality_gap_pct": round(opt_gap, 2)
        },
        "configurations": {
            "baseline": baseline_bench,
            "greedy": greedy_bench,
            "ilp": ilp_bench
        }
    }

    # Save JSON results
    json_path = os.path.join(RESULTS_DIR, "benchmark_comparison.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(study_results, f, indent=2)
    print(f"\n[INFO] Benchmark comparison saved to: {json_path}")

    # Save CSV comparison
    csv_path = os.path.join(RESULTS_DIR, "benchmark_comparison.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Query_ID", "Query_Name", "Baseline_Mean_ms", "Greedy_Mean_ms", "ILP_Mean_ms",
                         "Greedy_Speedup", "ILP_Speedup", "Baseline_Index", "Greedy_Index", "ILP_Index"])
        for q in queries:
            qid = q["id"]
            b_lat = baseline_bench["query_results"][qid]["mean_ms"]
            g_lat = greedy_bench["query_results"][qid]["mean_ms"]
            i_lat = ilp_bench["query_results"][qid]["mean_ms"]
            g_sp = b_lat / g_lat if g_lat > 0 else 1.0
            i_sp = b_lat / i_lat if i_lat > 0 else 1.0
            writer.writerow([
                qid, q["name"], b_lat, g_lat, i_lat,
                round(g_sp, 2), round(i_sp, 2),
                baseline_bench["query_results"][qid]["uses_index"],
                greedy_bench["query_results"][qid]["uses_index"],
                ilp_bench["query_results"][qid]["uses_index"]
            ])
    print(f"[INFO] CSV comparison saved to: {csv_path}")

    # Save query plans
    for cfg_key, bench_data in [("baseline", baseline_bench), ("greedy", greedy_bench), ("ilp", ilp_bench)]:
        plan_dict = {qid: data["plan"] for qid, data in bench_data["query_results"].items()}
        plan_file = os.path.join(RESULTS_DIR, f"{cfg_key}_plans.json")
        with open(plan_file, "w", encoding="utf-8") as f:
            json.dump(plan_dict, f, indent=2)

    return study_results

if __name__ == "__main__":
    run_complete_dbms_study(storage_budget_mb=3.0)
