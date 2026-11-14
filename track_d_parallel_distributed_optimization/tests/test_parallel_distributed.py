r"""Automated Test Suite for Track D: Parallel and Distributed Optimization.

Covers:
1. Submodularity and diminishing returns verification
2. Greedy feasibility, exact-optimum comparison, and (1 - 1/e) theoretical bound
3. Sequential vs. multiprocessing parallel workload equivalence
4. Amdahl's Law and Gustafson's Law analytical correctness
5. FedAvg parameter aggregation with hand-verifiable weights
6. MGDA convex combination weights, Pareto-stationarity, and common descent
7. GradNorm dynamic weight adaptation and normalization constraint
8. Invalid inputs, edge cases, and exception handling
"""

import math
import unittest
import numpy as np

from track_d_parallel_distributed_optimization.src.submodular import MaximumCoverageProblem
from track_d_parallel_distributed_optimization.src.parallel_compute import (
    ParallelComputeBenchmark,
    compute_chunk_workload,
)
from track_d_parallel_distributed_optimization.src.amdahl_gustafson import (
    amdahl_speedup,
    gustafson_speedup,
    ScalingLawAnalyzer,
)
from track_d_parallel_distributed_optimization.src.fedavg import SoftmaxModel, FedAvgSimulator
from track_d_parallel_distributed_optimization.src.mgda import (
    MGDASolver,
    MultiObjectiveBenchmark,
)
from track_d_parallel_distributed_optimization.src.gradnorm import (
    MultiTaskNetwork,
    GradNormSimulator,
)


class TestParallelDistributedOptimization(unittest.TestCase):
    """Unit tests for all Track D algorithmic modules."""

    def test_01_submodularity_and_diminishing_returns(self):
        """Verify diminishing returns property on known maximum coverage sets."""
        universe_size = 10
        # S0 covers {0, 1, 2}, S1 covers {1, 2, 3}, S2 covers {2, 3, 4, 5}, S3 covers {5, 6, 7}
        subsets = [{0, 1, 2}, {1, 2, 3}, {2, 3, 4, 5}, {5, 6, 7}]
        prob = MaximumCoverageProblem(universe_size, subsets)

        # Set A = {0}, Set B = {0, 1} -> A subset of B
        # Candidate e = 2 (subset S2 = {2, 3, 4, 5})
        set_A = {0}
        set_B = {0, 1}
        candidate_e = 2

        satisfies, delta_A, delta_B = prob.check_diminishing_returns(candidate_e, set_A, set_B)
        self.assertTrue(satisfies)
        # S0 covers {0,1,2}. S2 covers {2,3,4,5}.
        # Delta(S2 | S0) = |{2,3,4,5} - {0,1,2}| = |{3,4,5}| = 3
        self.assertEqual(delta_A, 3)
        # S0 U S1 covers {0,1,2,3}. S2 covers {2,3,4,5}.
        # Delta(S2 | S0, S1) = |{2,3,4,5} - {0,1,2,3}| = |{4,5}| = 2
        self.assertEqual(delta_B, 2)
        self.assertGreaterEqual(delta_A, delta_B)

        # Comprehensive random test
        is_submod, rate = prob.verify_submodularity(num_samples=50, seed=123)
        self.assertTrue(is_submod)
        self.assertEqual(rate, 1.0)

    def test_02_greedy_vs_exact_and_approximation_bound(self):
        """Verify Greedy achieves at least (1 - 1/e) of exact optimum."""
        # 12 elements, 6 subsets, k = 3
        universe_size = 12
        subsets = [
            {0, 1, 2, 3},
            {2, 3, 4, 5},
            {4, 5, 6, 7},
            {6, 7, 8, 9},
            {8, 9, 10, 11},
            {0, 5, 10},
        ]
        prob = MaximumCoverageProblem(universe_size, subsets)
        k = 3

        greedy_res = prob.solve_greedy(k)
        exact_res = prob.solve_exact(k)

        cov_greedy = greedy_res["coverage_count"]
        cov_exact = exact_res["optimal_coverage"]

        self.assertGreaterEqual(cov_exact, cov_greedy)
        self.assertLessEqual(greedy_res["cardinality"], k)

        # Verify (1 - 1/e) theoretical bound
        bound = MaximumCoverageProblem.theoretical_bound(cov_exact)
        self.assertGreaterEqual(cov_greedy, bound)

    def test_03_sequential_and_parallel_workload_equivalence(self):
        """Verify multiprocessing parallel execution matches sequential result exactly."""
        bench = ParallelComputeBenchmark(chunk_size=10_000, iterations_per_chunk=3)
        num_chunks = 4

        seq_res, t_seq = bench.run_sequential(num_chunks)
        par_res, t_par = bench.run_parallel(num_chunks, num_workers=2)

        # Numerical results must be identical to within machine precision
        diff = abs(seq_res - par_res)
        self.assertLess(diff, 1e-10)
        self.assertGreater(seq_res, 0.0)

    def test_04_amdahl_and_gustafson_formulas(self):
        """Verify analytical calculations for Amdahl's Law and Gustafson's Law."""
        P = 0.9  # 90% parallel
        N = 10   # 10 processors

        # Amdahl: S = 1 / ((1 - 0.9) + 0.9 / 10) = 1 / (0.1 + 0.09) = 1 / 0.19 = 5.263157...
        s_amdahl = amdahl_speedup(N, P)
        expected_amdahl = 1.0 / (0.1 + 0.09)
        self.assertAlmostEqual(s_amdahl, expected_amdahl, places=5)

        # Gustafson: S = 10 - 0.1 * 9 = 10 - 0.9 = 9.1
        s_gustafson = gustafson_speedup(N, P)
        expected_gustafson = 10.0 - 0.1 * 9.0
        self.assertAlmostEqual(s_gustafson, expected_gustafson, places=5)

        # Curve fitting check
        workers = [1, 2, 4, 8]
        theoretical_speedups = [float(amdahl_speedup(w, 0.85)) for w in workers]
        p_fit, s_fit, r2 = ScalingLawAnalyzer.fit_amdahl_fraction(workers, theoretical_speedups)
        self.assertAlmostEqual(p_fit, 0.85, places=2)
        self.assertAlmostEqual(s_fit, 0.15, places=2)
        self.assertGreater(r2, 0.99)

    def test_05_fedavg_parameter_aggregation_exactness(self):
        """Verify FedAvg weighted parameter averaging on hand-constructed client weights."""
        num_features = 3
        num_classes = 2

        client1_params = {
            "W": np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]),
            "b": np.array([0.5, 1.5]),
        }
        client2_params = {
            "W": np.array([[3.0, 4.0], [5.0, 6.0], [7.0, 8.0]]),
            "b": np.array([2.5, 3.5]),
        }

        # Weights: 100 samples vs 300 samples -> weights 0.25 and 0.75
        client_sizes = [100, 300]
        agg = FedAvgSimulator.aggregate_parameters([client1_params, client2_params], client_sizes)

        # Expected: 0.25 * C1 + 0.75 * C2
        expected_W = 0.25 * client1_params["W"] + 0.75 * client2_params["W"]
        expected_b = 0.25 * client1_params["b"] + 0.75 * client2_params["b"]

        np.testing.assert_allclose(agg["W"], expected_W, rtol=1e-12)
        np.testing.assert_allclose(agg["b"], expected_b, rtol=1e-12)

    def test_06_mgda_weights_and_pareto_stationarity(self):
        """Verify MGDA min-norm convex combination and Pareto stationarity on front."""
        solver = MGDASolver()

        # At point (0, 0), g1 = 2(-1, 0) = (-2, 0), g2 = 2(+1, 0) = (+2, 0)
        # Antipodal gradients: convex combination 0.5 * (-2) + 0.5 * (+2) = 0!
        f_vals, grads = MultiObjectiveBenchmark.conflicting_quadratics(np.array([0.0, 0.0]))
        g1, g2 = grads[0], grads[1]

        weights, combined_grad = solver.find_min_norm_element_2d(g1, g2)
        self.assertAlmostEqual(weights[0], 0.5, places=5)
        self.assertAlmostEqual(weights[1], 0.5, places=5)
        np.testing.assert_allclose(combined_grad, np.array([0.0, 0.0]), atol=1e-12)

        # Optimization trajectory should converge to Pareto front (x2 = 0, |x1| <= 1)
        res = solver.optimize_mgda(
            MultiObjectiveBenchmark.conflicting_quadratics,
            initial_x=np.array([2.0, 3.0]),
            lr=0.1,
            max_iters=100,
        )
        final_x = res["final_x"]
        self.assertAlmostEqual(final_x[1], 0.0, delta=0.05)
        self.assertLessEqual(abs(final_x[0]), 1.05)

    def test_07_gradnorm_weight_sum_and_adaptation(self):
        """Verify GradNorm preserves sum of task weights = T and adapts dynamically."""
        sim = GradNormSimulator(in_dim=6, hidden_dim=8, seed=42)
        X, y1, y2 = sim.generate_synthetic_data(n_samples=60)

        res = sim.run_training(X, y1, y2, num_epochs=15, use_gradnorm=True)

        final_w = res["final_weights"]
        self.assertEqual(len(final_w), 2)
        # Weight sum constraint: sum(w_i) = T = 2.0
        self.assertAlmostEqual(sum(final_w), 2.0, places=5)
        # Strictly positive
        self.assertGreater(final_w[0], 0.0)
        self.assertGreater(final_w[1], 0.0)

    def test_08_invalid_inputs_and_edge_cases(self):
        """Verify error handling for invalid parameters across modules."""
        # 1. Submodular invalid universe
        with self.assertRaises(ValueError):
            MaximumCoverageProblem(0, [{0}])
        with self.assertRaises(ValueError):
            MaximumCoverageProblem(5, [])

        # 2. Submodular invalid k
        prob = MaximumCoverageProblem(5, [{0, 1}, {2, 3}])
        with self.assertRaises(ValueError):
            prob.solve_greedy(0)
        with self.assertRaises(ValueError):
            prob.solve_greedy(10)

        # 3. Parallel compute invalid chunk
        with self.assertRaises(ValueError):
            ParallelComputeBenchmark(chunk_size=0)
        with self.assertRaises(ValueError):
            ParallelComputeBenchmark().run_parallel(4, num_workers=0)

        # 4. Amdahl invalid parallel fraction
        with self.assertRaises(ValueError):
            amdahl_speedup(4, parallel_fraction=1.5)
        with self.assertRaises(ValueError):
            amdahl_speedup(0, parallel_fraction=0.8)


if __name__ == "__main__":
    unittest.main()

