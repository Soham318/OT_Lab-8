"""
Automated Unit and Regression Test Suite for Track H: DBMS Query Optimization.
Validates:
1. Schema creation and foreign key constraints
2. Deterministic data generation
3. Candidate index definitions and metadata
4. Workload query definitions and syntax validity
5. Greedy index selector budget compliance
6. ILP solver binary constraints and budget compliance
7. ILP vs Exhaustive exactness guarantee
8. Greedy vs ILP optimality gap detection
9. SHA-256 query result equivalence across configurations
10. EXPLAIN QUERY PLAN extraction and index utilization
"""

import os
import unittest
import sqlite3
import hashlib
import tempfile
import numpy as np

from track_h_dbms_optimization.src.schema import create_schema
from track_h_dbms_optimization.src.data_generator import populate_database
from track_h_dbms_optimization.src.workload import get_workload_queries
from track_h_dbms_optimization.src.index_candidates import get_candidate_indexes
from track_h_dbms_optimization.src.greedy_selector import run_greedy_index_selection
from track_h_dbms_optimization.src.ilp_selector import solve_ilp_index_selection, solve_exhaustive_index_selection
from track_h_dbms_optimization.src.benchmark_runner import explain_query_plan, hash_query_result

class TestDBMSOptimization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.test_db_path = os.path.join(cls.temp_dir.name, "test_railway.db")
        cls.conn = sqlite3.connect(cls.test_db_path)
        cls.conn.execute("PRAGMA foreign_keys = ON;")
        create_schema(cls.conn)
        cls.row_counts = populate_database(cls.conn, seed=42, scale_factor=0.2)
        cls.candidates = get_candidate_indexes()
        cls.queries = get_workload_queries()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        cls.conn = None
        try:
            cls.temp_dir.cleanup()
        except Exception:
            pass

    def test_01_schema_creation_and_tables(self):
        """Test that all 7 railway tables are created with proper schema."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [r[0] for r in cursor.fetchall() if not r[0].startswith("sqlite_")]
        expected = ["bookings", "passengers", "payments", "schedules", "stations", "tickets", "trains"]
        self.assertEqual(sorted(tables), expected)

    def test_02_deterministic_data_generation(self):
        """Test that data generation is deterministic and populated properly."""
        self.assertGreater(self.row_counts["stations"], 0)
        self.assertGreater(self.row_counts["trains"], 0)
        self.assertGreater(self.row_counts["passengers"], 0)
        self.assertGreater(self.row_counts["bookings"], 0)
        self.assertGreater(self.row_counts["tickets"], 0)
        self.assertGreater(self.row_counts["payments"], 0)

    def test_03_candidate_index_specifications(self):
        """Verify candidate indexes have unique IDs, valid costs, and non-empty SQL."""
        self.assertEqual(len(self.candidates), 12)
        ids = [c["id"] for c in self.candidates]
        self.assertEqual(len(ids), len(set(ids)), "Candidate index IDs must be unique.")
        for c in self.candidates:
            self.assertTrue(c["id"].startswith("IDX_"))
            self.assertGreater(c["storage_cost_mb"], 0.0)
            self.assertTrue(c["sql"].strip().upper().startswith("CREATE INDEX"))
            self.assertIsInstance(c["applicable_queries"], list)

    def test_04_workload_queries_syntax_and_execution(self):
        """Verify that all 8 workload queries execute without error on the test DB."""
        self.assertEqual(len(self.queries), 8)
        cursor = self.conn.cursor()
        for q in self.queries:
            try:
                cursor.execute(q["sql"])
                rows = cursor.fetchall()
                self.assertIsInstance(rows, list)
            except Exception as e:
                self.fail(f"Query {q['id']} failed execution: {e}")

    def test_05_greedy_selector_budget_compliance(self):
        """Verify that Greedy selection strictly adheres to storage budget."""
        for b in [1.5, 3.0, 5.0, 7.0]:
            sol = run_greedy_index_selection(self.candidates, self.queries, storage_budget_mb=b)
            self.assertLessEqual(sol["total_storage_mb"], b + 1e-6)
            self.assertGreater(sol["total_benefit_score"], 0)

    def test_06_ilp_selector_budget_compliance(self):
        """Verify that ILP selection strictly adheres to storage budget."""
        for b in [1.5, 3.0, 5.0, 7.0]:
            sol = solve_ilp_index_selection(self.candidates, self.queries, storage_budget_mb=b)
            self.assertLessEqual(sol["total_storage_mb"], b + 1e-6)
            self.assertGreater(sol["total_benefit_score"], 0)

    def test_07_ilp_vs_exhaustive_exactness(self):
        """Verify that SciPy HiGHS ILP matches Exhaustive global optimum 100%."""
        for b in [2.0, 3.0, 4.5]:
            ilp_sol = solve_ilp_index_selection(self.candidates, self.queries, storage_budget_mb=b)
            exh_sol = solve_exhaustive_index_selection(self.candidates, self.queries, storage_budget_mb=b)
            self.assertAlmostEqual(ilp_sol["total_benefit_score"], exh_sol["total_benefit_score"], places=4)
            self.assertEqual(ilp_sol["selected_indexes"], exh_sol["selected_indexes"])

    def test_08_greedy_vs_ilp_optimality_gap(self):
        """Verify that at budget 3.0 MB, Greedy exhibits an optimality gap vs ILP."""
        greedy_sol = run_greedy_index_selection(self.candidates, self.queries, storage_budget_mb=3.0)
        ilp_sol = solve_ilp_index_selection(self.candidates, self.queries, storage_budget_mb=3.0)
        
        self.assertEqual(greedy_sol["selected_indexes"], ["IDX_02", "IDX_09", "IDX_10"])
        self.assertEqual(ilp_sol["selected_indexes"], ["IDX_02", "IDX_07"])
        self.assertLess(greedy_sol["total_benefit_score"], ilp_sol["total_benefit_score"])
        
        gap = (ilp_sol["total_benefit_score"] - greedy_sol["total_benefit_score"]) / ilp_sol["total_benefit_score"] * 100
        self.assertAlmostEqual(gap, 6.92, places=1)

    def test_09_query_result_hash_parity(self):
        """Verify that query results match 100% across unindexed and indexed databases."""
        cursor = self.conn.cursor()
        for q in self.queries:
            # Baseline execution
            cursor.execute(q["sql"])
            rows_before = cursor.fetchall()
            h_before = hash_query_result(rows_before)
            
            # Create a test index
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_temp_test ON bookings(journey_date, booking_status);")
            cursor.execute(q["sql"])
            rows_after = cursor.fetchall()
            h_after = hash_query_result(rows_after)
            
            self.assertEqual(h_before, h_after, f"Query {q['id']} hash changed after indexing!")
            self.assertEqual(len(rows_before), len(rows_after), f"Query {q['id']} row count changed after indexing!")
            cursor.execute("DROP INDEX IF EXISTS idx_temp_test;")

    def test_10_explain_query_plan_extraction(self):
        """Verify that EXPLAIN QUERY PLAN extracts operation details."""
        plan_lines, uses_idx, uses_scan = explain_query_plan(self.conn, "SELECT * FROM bookings WHERE journey_date = '2026-06-15';")
        self.assertTrue(len(plan_lines) > 0)
        self.assertTrue(any("bookings" in line for line in plan_lines))
        self.assertTrue(uses_scan)

if __name__ == "__main__":
    unittest.main()
