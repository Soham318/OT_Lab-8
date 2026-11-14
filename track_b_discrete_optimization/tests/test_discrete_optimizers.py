r"""
Unit Tests for Track B: Discrete Optimization
Assignment 8 - Optimize Anything

Tests:
  1. Greedy feasibility and known suboptimal counterexample.
  2. ILP optimality on a small manually verifiable instance.
  3. Branch-and-Bound agreement with ILP.
  4. Dynamic Programming agreement with ILP.
  5. QUBO exhaustive enumeration and constraint satisfaction.
  6. Binary-to-Ising energy parity and spin conversion correctness.
  7. Invalid input handling.
"""

import unittest
import numpy as np

from track_b_discrete_optimization.src.problem import KnapsackProblem
from track_b_discrete_optimization.src.greedy_solver import GreedyKnapsackSolver
from track_b_discrete_optimization.src.ilp_solver import ILPKnapsackSolver
from track_b_discrete_optimization.src.branch_and_bound import BranchAndBoundSolver
from track_b_discrete_optimization.src.dp_solver import DPKnapsackSolver
from track_b_discrete_optimization.src.qubo_ising import QUBOKnapsackSolver, IsingModel


class TestDiscreteOptimizers(unittest.TestCase):

    def setUp(self):
        self.greedy = GreedyKnapsackSolver()
        self.ilp = ILPKnapsackSolver()
        self.bb = BranchAndBoundSolver()
        self.dp = DPKnapsackSolver()
        self.qubo = QUBOKnapsackSolver(penalty_multiplier=2.0)

    def test_01_greedy_feasibility_and_counterexample(self):
        """Verify Greedy produces feasible solution and demonstrates known suboptimal gap."""
        problem = KnapsackProblem.create_known_counterexample()
        sol_greedy = self.greedy.solve(problem)
        sol_ilp = self.ilp.solve(problem)

        self.assertTrue(sol_greedy.is_feasible)
        self.assertTrue(sol_ilp.is_feasible)

        # In known counterexample: Greedy chooses {0, 1} with value 160
        # Optimal (ILP) chooses {1, 2} with value 220
        self.assertEqual(sol_greedy.total_value, 160.0)
        self.assertEqual(sol_greedy.total_weight, 30.0)
        self.assertEqual(sol_ilp.total_value, 220.0)
        self.assertEqual(sol_ilp.total_weight, 50.0)

        # Calculate optimality gap
        gap = (sol_ilp.total_value - sol_greedy.total_value) / sol_ilp.total_value
        self.assertAlmostEqual(gap, 0.272727, places=4)
        self.assertGreater(sol_ilp.total_value, sol_greedy.total_value)

    def test_02_ilp_optimality_on_manual_instance(self):
        """Verify ILP on hand-calculated 4-item instance."""
        # Items:
        # 0: v=10, w=5
        # 1: v=40, w=4
        # 2: v=30, w=6
        # 3: v=50, w=3
        # Capacity: W = 10
        # Feasible combinations:
        # {1, 3}: w = 4 + 3 = 7 <= 10, value = 40 + 50 = 90
        # {0, 1}: w = 9 <= 10, value = 50
        # {1, 2}: w = 10 <= 10, value = 70
        # {0, 2}: w = 11 > 10 (infeasible)
        # {0, 3}: w = 8 <= 10, value = 60
        # Hand-calculated global optimum: {1, 3} with value 90.0, weight 7.0
        values = np.array([10.0, 40.0, 30.0, 50.0])
        weights = np.array([5.0, 4.0, 6.0, 3.0])
        capacity = 10.0
        problem = KnapsackProblem(values, weights, capacity, name="HandCalculated4")

        sol = self.ilp.solve(problem)
        self.assertTrue(sol.is_feasible)
        self.assertEqual(sol.total_value, 90.0)
        self.assertEqual(sol.total_weight, 7.0)
        self.assertEqual(sol.selected_indices, [1, 3])

    def test_03_branch_and_bound_agreement_with_ilp(self):
        """Verify Branch-and-Bound matches ILP on non-trivial instances."""
        for seed in [10, 42, 99]:
            problem = KnapsackProblem.generate_random_instance(n_items=12, seed=seed)
            sol_ilp = self.ilp.solve(problem)
            sol_bb = self.bb.solve(problem)

            self.assertTrue(sol_bb.is_feasible)
            self.assertEqual(sol_bb.total_value, sol_ilp.total_value, f"B&B failed on seed {seed}")
            self.assertLessEqual(sol_bb.total_weight, problem.capacity)

    def test_04_dp_agreement_with_ilp(self):
        """Verify Dynamic Programming matches ILP on integer instances."""
        for seed in [7, 55, 123]:
            problem = KnapsackProblem.generate_random_instance(n_items=15, seed=seed)
            sol_ilp = self.ilp.solve(problem)
            sol_dp = self.dp.solve(problem)

            self.assertTrue(sol_dp.is_feasible)
            self.assertEqual(sol_dp.total_value, sol_ilp.total_value, f"DP failed on seed {seed}")
            self.assertLessEqual(sol_dp.total_weight, problem.capacity)

    def test_05_qubo_exhaustive_and_constraint_satisfaction(self):
        """Verify QUBO exhaustive search finds global optimum and satisfies constraints."""
        # Small 4-item instance for tractable enumeration
        values = np.array([20.0, 30.0, 15.0, 40.0])
        weights = np.array([3.0, 5.0, 2.0, 6.0])
        capacity = 8.0
        problem = KnapsackProblem(values, weights, capacity, name="QUBOSmall4")

        sol_ilp = self.ilp.solve(problem)
        sol_qubo = self.qubo.solve(problem)

        self.assertTrue(sol_qubo.is_feasible)
        self.assertEqual(sol_qubo.total_value, sol_ilp.total_value)
        self.assertLessEqual(sol_qubo.total_weight, capacity)
        self.assertEqual(sol_qubo.selected_items.tolist(), sol_ilp.selected_items.tolist())

    def test_06_qubo_to_ising_conversion_energy_parity(self):
        """Verify mathematical equivalence between QUBO energy and Ising Hamiltonian."""
        values = np.array([12.0, 25.0, 18.0])
        weights = np.array([2.0, 4.0, 3.0])
        capacity = 5.0
        problem = KnapsackProblem(values, weights, capacity, name="IsingParityTest")

        Q, offset, slacks, P = self.qubo.build_qubo_matrix(problem)
        ising = self.qubo.qubo_to_ising(Q, offset)

        N_vars = Q.shape[0]
        # Test 20 random binary state vectors
        rng = np.random.RandomState(42)
        for _ in range(20):
            z = rng.randint(0, 2, size=N_vars).astype(np.float64)
            # QUBO energy via evaluation method
            qubo_e = self.qubo.evaluate_qubo_energy(Q, offset, z)
            # Ising energy: s_i = 2 * z_i - 1
            spins = 2.0 * z - 1.0
            ising_e = ising.energy(spins)

            self.assertAlmostEqual(
                qubo_e,
                ising_e,
                places=6,
                msg=f"Energy parity failed: QUBO={qubo_e}, Ising={ising_e}"
            )

    def test_07_invalid_inputs_handling(self):
        """Verify proper validation of invalid parameters."""
        # Mismatched lengths
        with self.assertRaises(ValueError):
            KnapsackProblem(values=[10, 20], weights=[5], capacity=10)

        # Empty instance
        with self.assertRaises(ValueError):
            KnapsackProblem(values=[], weights=[], capacity=10)

        # Negative values
        with self.assertRaises(ValueError):
            KnapsackProblem(values=[-5, 10], weights=[2, 3], capacity=10)

        # Non-positive weights
        with self.assertRaises(ValueError):
            KnapsackProblem(values=[10, 20], weights=[0, 3], capacity=10)

        # Negative capacity
        with self.assertRaises(ValueError):
            KnapsackProblem(values=[10, 20], weights=[2, 3], capacity=-1)

        # Intractable QUBO
        large_problem = KnapsackProblem.generate_random_instance(n_items=25)
        with self.assertRaises(ValueError):
            self.qubo.solve(large_problem)


if __name__ == "__main__":
    unittest.main()
