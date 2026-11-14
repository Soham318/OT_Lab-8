r"""Parallel Computing Benchmark Module.

Implements compute-bound parallel workloads evaluated sequentially and across
multiple processes using Python's multiprocessing pool on Windows.

Measures:
- Execution time across worker counts P in {1, 2, 4, 8}
- Speedup S_P = T_1 / T_P
- Parallel Efficiency E_P = S_P / P
- Numerical equivalence between sequential and multi-process execution
"""

import multiprocessing as mp
import time
from typing import Any, Dict, List, Tuple
import numpy as np


def compute_chunk_workload(args: Tuple[int, int, int]) -> float:
    """Top-level worker function compatible with Windows multiprocessing spawn.

    Args:
        args: Tuple of (chunk_id, chunk_size, iterations)

    Returns:
        Accumulated floating point result.
    """
    chunk_id, chunk_size, iterations = args
    # Deterministic seed per chunk to guarantee exact reproducibility
    rng = np.random.default_rng(chunk_id * 7919 + 42)
    data = rng.standard_normal(chunk_size)

    total_acc = 0.0
    for _ in range(iterations):
        # Heavy mathematical transformation (transcendental functions + power + root)
        transformed = np.sin(data) ** 2 + np.cos(data) ** 2 + np.sqrt(np.abs(data)) + np.exp(-0.01 * data ** 2)
        total_acc += float(np.sum(transformed))

    return total_acc


class ParallelComputeBenchmark:
    """Benchmark harness comparing sequential vs. multiprocessing parallel workloads."""

    def __init__(self, chunk_size: int = 150_000, iterations_per_chunk: int = 8):
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        if iterations_per_chunk <= 0:
            raise ValueError(f"iterations_per_chunk must be positive, got {iterations_per_chunk}")

        self.chunk_size = chunk_size
        self.iterations_per_chunk = iterations_per_chunk

    def generate_task_payloads(self, num_chunks: int) -> List[Tuple[int, int, int]]:
        """Generate parameter tuples for each chunk."""
        if num_chunks <= 0:
            raise ValueError(f"num_chunks must be positive, got {num_chunks}")
        return [(i, self.chunk_size, self.iterations_per_chunk) for i in range(num_chunks)]

    def run_sequential(self, num_chunks: int) -> Tuple[float, float]:
        """Execute all chunks sequentially on a single core.

        Returns:
            (aggregated_result, elapsed_time_seconds)
        """
        payloads = self.generate_task_payloads(num_chunks)
        start_time = time.perf_counter()
        results = [compute_chunk_workload(p) for p in payloads]
        elapsed = time.perf_counter() - start_time
        return float(sum(results)), elapsed

    def run_parallel(self, num_chunks: int, num_workers: int) -> Tuple[float, float]:
        """Execute chunks across num_workers processes using multiprocessing.Pool.

        Returns:
            (aggregated_result, elapsed_time_seconds)
        """
        if num_workers <= 0:
            raise ValueError(f"num_workers must be positive, got {num_workers}")

        payloads = self.generate_task_payloads(num_chunks)
        start_time = time.perf_counter()

        with mp.Pool(processes=num_workers) as pool:
            results = pool.map(compute_chunk_workload, payloads)

        elapsed = time.perf_counter() - start_time
        return float(sum(results)), elapsed

    def benchmark_scaling(
        self,
        num_chunks: int = 32,
        worker_counts: List[int] = [1, 2, 4, 8],
        repeats: int = 3,
    ) -> List[Dict[str, Any]]:
        """Run repeated trials across various worker counts and measure speedup and efficiency.

        Reuses persistent worker pools across repeats to measure true parallel compute
        throughput rather than operating system process spawn latency.

        Returns:
            List of metrics dictionaries for each worker configuration.
        """
        payloads = self.generate_task_payloads(num_chunks)

        # 1. Sequential baseline
        seq_times = []
        seq_results = []
        for _ in range(repeats):
            t0 = time.perf_counter()
            res = [compute_chunk_workload(p) for p in payloads]
            elapsed = time.perf_counter() - t0
            seq_times.append(elapsed)
            seq_results.append(float(sum(res)))

        baseline_time_mean = float(np.mean(seq_times))
        baseline_time_std = float(np.std(seq_times))
        baseline_result = seq_results[0]

        summary: List[Dict[str, Any]] = []

        summary.append({
            "worker_count": 1,
            "mode": "sequential",
            "num_chunks": num_chunks,
            "mean_time_sec": baseline_time_mean,
            "std_time_sec": baseline_time_std,
            "speedup": 1.0,
            "efficiency": 1.0,
            "result_parity_error": 0.0,
        })

        for p in worker_counts:
            p_times = []
            p_results = []

            # Reuse pool across repeats to isolate compute throughput
            with mp.Pool(processes=p) as pool:
                # Warm-up call (1 small task) to ensure workers are spawned
                pool.map(compute_chunk_workload, [(0, 1000, 1)])

                for _ in range(repeats):
                    t0 = time.perf_counter()
                    res = pool.map(compute_chunk_workload, payloads)
                    elapsed = time.perf_counter() - t0
                    p_times.append(elapsed)
                    p_results.append(float(sum(res)))

            mean_p = float(np.mean(p_times))
            speedup_p = baseline_time_mean / mean_p if mean_p > 0 else 0.0
            efficiency_p = speedup_p / p
            parity_err = abs(p_results[0] - baseline_result)

            summary.append({
                "worker_count": p,
                "mode": "multiprocessing_pool",
                "num_chunks": num_chunks,
                "mean_time_sec": mean_p,
                "std_time_sec": float(np.std(p_times)),
                "speedup": speedup_p,
                "efficiency": efficiency_p,
                "result_parity_error": parity_err,
            })

        return summary
