"""
Master Regression Test Runner Across All Ten Tracks (A through J)
Tracks A through J verification suite.
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.abspath("."))

TEST_SUITES = {
    "Track A: Continuous Optimization": "track_a_continuous_optimization.tests.test_continuous_optimizers",
    "Track B: Discrete Optimization & QUBO": "track_b_discrete_optimization.tests.test_discrete_optimizers",
    "Track C: Quantum Optimization": "track_c_quantum_optimization.tests.test_quantum_optimization",
    "Track D: Parallel & Distributed": "track_d_parallel_distributed_optimization.tests.test_parallel_distributed",
    "Track E1: Railway Dijkstra Baseline": "track_e_case_study.tests.test_dijkstra_baseline",
    "Track E2: Railway Greedy & ILP": "track_e_case_study.tests.test_optimizers",
    "Track F: Compiler Optimization": "track_f_compiler_optimization.tests.test_compiler",
    "Track G: xv6 Kernel Modifications": "track_g_xv6_kernel.tests.test_xv6_kernel",
    "Track H: DBMS Query Optimization": "track_h_dbms_optimization.tests.test_dbms_optimization",
    "Track I: Quantum Algorithms & QML": "track_i_quantum_algorithms.tests.test_quantum_algorithms",
    "Track J: Real-World Workflow Optimization": "track_j_real_world_optimization.tests.test_codebase_optimization",
}

def run_all_regression_tests():
    loader = unittest.TestLoader()
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0

    print("=" * 80)
    print("MASTER REGRESSION TEST SUITE (TRACKS A THROUGH J)")
    print("=" * 80)
    print(f"{'Track Name':<42} | {'Tests':<5} | {'Passed':<6} | {'Failed':<6} | {'Time':<8} | {'Status'}")
    print("-" * 80)

    start_time_all = time.perf_counter()

    for track_name, module_name in TEST_SUITES.items():
        try:
            suite = loader.loadTestsFromName(module_name)
        except Exception as e:
            print(f"{track_name:<42} | ERROR LOADING: {e}")
            continue

        n_tests = suite.countTestCases()
        t0 = time.perf_counter()
        runner = unittest.TextTestRunner(stream=open(os.devnull, "w"), verbosity=0)
        res = runner.run(suite)
        t_elapsed = time.perf_counter() - t0

        n_fail = len(res.failures)
        n_err = len(res.errors)
        n_pass = n_tests - n_fail - n_err

        total_tests += n_tests
        total_passed += n_pass
        total_failed += n_fail
        total_errors += n_err

        status = "PASS" if res.wasSuccessful() else "FAIL"
        print(f"{track_name:<42} | {n_tests:<5} | {n_pass:<6} | {n_fail + n_err:<6} | {t_elapsed:<7.3f}s | {status}")

    total_time = time.perf_counter() - start_time_all
    print("-" * 80)
    print(f"{'CONSOLIDATED TOTAL':<42} | {total_tests:<5} | {total_passed:<6} | {total_failed + total_errors:<6} | {total_time:<7.3f}s | {'ALL PASS (100%)' if total_failed + total_errors == 0 else 'FAIL'}")
    print("=" * 80)

    return total_failed + total_errors == 0

if __name__ == "__main__":
    success = run_all_regression_tests()
    sys.exit(0 if success else 1)
