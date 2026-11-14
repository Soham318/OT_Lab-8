#!/usr/bin/env python3
"""
Automated unit and integration test suite for Track G: xv6 Kernel Modifications.
Validates build artifacts, patch completeness, and benchmark log invariants.
"""

import os
import unittest

class TestXv6KernelAccounting(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.xv6_dir = os.path.join(self.base_dir, "xv6-riscv")
        self.results_dir = os.path.join(self.base_dir, "results")
        self.plots_dir = os.path.join(self.base_dir, "plots")
        self.patches_dir = os.path.join(self.base_dir, "patches")

    def test_01_build_artifacts_exist(self):
        """Verify that the compiled kernel and filesystem image exist."""
        kernel_path = os.path.join(self.xv6_dir, "kernel", "kernel")
        fs_path = os.path.join(self.xv6_dir, "fs.img")
        self.assertTrue(os.path.exists(kernel_path), f"Kernel binary missing at {kernel_path}")
        self.assertTrue(os.path.exists(fs_path), f"Filesystem image missing at {fs_path}")
        self.assertGreater(os.path.getsize(kernel_path), 100000)
        self.assertGreater(os.path.getsize(fs_path), 500000)

    def test_02_patch_file_integrity(self):
        """Verify that the patch diff exists and contains kernel syscall modifications."""
        patch_path = os.path.join(self.patches_dir, "0001_cputime_accounting.patch")
        self.assertTrue(os.path.exists(patch_path), f"Patch missing at {patch_path}")
        with open(patch_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("SYS_getcputime", content)
        self.assertIn("sys_getcputime", content)
        self.assertIn("cputime", content)

    def test_03_workload_logs_exist_and_non_empty(self):
        """Verify that all empirical workload test logs exist and captured results."""
        expected_logs = [
            "workload_cpu_intensive.txt",
            "workload_short.txt",
            "workload_concurrent.txt",
            "test_cputime_results.txt"
        ]
        for log_name in expected_logs:
            log_path = os.path.join(self.results_dir, log_name)
            self.assertTrue(os.path.exists(log_path), f"Log missing: {log_name}")
            with open(log_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertGreater(len(content), 50, f"Log too short: {log_name}")

    def test_04_test_cputime_validation_checks_passed(self):
        """Verify that all 5 validation checks in test_cputime passed."""
        log_path = os.path.join(self.results_dir, "test_cputime_results.txt")
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Test 1 PASS", content)
        self.assertIn("Test 2 PASS", content)
        self.assertIn("Test 3 PASS", content)
        self.assertIn("Test 4 PASS", content)
        self.assertIn("Test 5 PASS", content)
        self.assertIn("ALL test_cputime VALIDATION CHECKS PASSED", content)

    def test_05_cpu_workload_duty_cycle(self):
        """Verify CPU-intensive workload achieved high duty cycle without hangs."""
        log_path = os.path.join(self.results_dir, "workload_cpu_intensive.txt")
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("CPU duty = 100%", content)
        self.assertIn("CPU-Intensive Workload Completed Successfully", content)

    def test_06_short_workload_quantization(self):
        """Verify short workload demonstrated timer tick quantization."""
        log_path = os.path.join(self.results_dir, "workload_short.txt")
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Trials with 0 ticks: 5 / 5", content)
        self.assertIn("Granularity Findings", content)

    def test_07_concurrent_workload_parallelism(self):
        """Verify concurrent workload demonstrated SMP parallel execution."""
        log_path = os.path.join(self.results_dir, "workload_concurrent.txt")
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Parallel execution ratio:", content)
        self.assertIn("Concurrent Workload Completed Successfully", content)

    def test_08_plots_generated(self):
        """Verify all 4 publication figures are generated."""
        expected_plots = [
            "01_workload_cputime_vs_walltime.png",
            "02_concurrent_smp_accounting.png",
            "03_timer_tick_quantization_error.png",
            "04_active_vs_sleeping_accounting.png"
        ]
        for plot_name in expected_plots:
            plot_path = os.path.join(self.plots_dir, plot_name)
            self.assertTrue(os.path.exists(plot_path), f"Plot missing: {plot_name}")
            self.assertGreater(os.path.getsize(plot_path), 5000)

if __name__ == "__main__":
    unittest.main()

