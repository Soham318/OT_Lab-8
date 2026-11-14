r"""
Unit Tests for Track C: Quantum Optimization
Assignment 8 - Optimize Anything

Tests:
  1. Circuit construction and valid parameter dimensions.
  2. QAOA cost Hamiltonian and bitstring objective consistency.
  3. QAOA result vs exact Max-Cut solution on a small graph.
  4. VQE energy vs exact diagonalization.
  5. Parameter-shift gradient correctness vs analytical & finite-difference.
  6. SPSA parameter updates and loss reduction.
  7. QNG Fubini-Study metric stability and regularization.
  8. Shot-noise variance scaling.
"""

import unittest
import numpy as np

from qiskit.quantum_info import Statevector, SparsePauliOp
from track_c_quantum_optimization.src.circuits import HardwareEfficientAnsatz
from track_c_quantum_optimization.src.qaoa import QAOAMaxCutSolver
from track_c_quantum_optimization.src.vqe import VQESolver
from track_c_quantum_optimization.src.gradients import ParameterShiftGradient, SPSAOptimizer
from track_c_quantum_optimization.src.qng import QuantumNaturalGradient
from track_c_quantum_optimization.src.barren_plateaus import ShotNoiseStudy


class TestQuantumOptimization(unittest.TestCase):

    def setUp(self):
        self.rng = np.random.RandomState(42)

    def test_01_circuit_construction_and_parameter_dimensions(self):
        """Verify HardwareEfficientAnsatz dimensions, parameter binding and statevector normalization."""
        ansatz = HardwareEfficientAnsatz(num_qubits=3, num_layers=2, entanglement="linear", rotation_blocks=("ry", "rz"))
        # 3 qubits * 2 rots * (2 + 1 layers) = 18 params
        self.assertEqual(ansatz.num_params, 18)
        self.assertGreater(ansatz.depth, 0)

        # Valid binding
        theta = self.rng.randn(18)
        sv = ansatz.get_statevector(theta)
        norm = np.linalg.norm(sv.data)
        self.assertAlmostEqual(norm, 1.0, places=6)

        # Invalid dimension raises ValueError
        with self.assertRaises(ValueError):
            ansatz.bind(np.array([1.0, 2.0]))

        # Invalid constructor args
        with self.assertRaises(ValueError):
            HardwareEfficientAnsatz(num_qubits=0)

    def test_02_qaoa_cost_hamiltonian_and_bitstring_consistency(self):
        """Verify <b | H_C | b> equals the classical cut value C(b) for every computational basis state."""
        # 3-node triangle graph with unit weights
        edges = [(0, 1, 1.0), (1, 2, 1.0), (0, 2, 1.0)]
        qaoa = QAOAMaxCutSolver(num_nodes=3, edges=edges, p=1)

        # For every 3-bit basis state
        for b_int in range(8):
            bits = [(b_int >> i) & 1 for i in range(3)]
            b_str = "".join(str(bit) for bit in reversed(bits))
            classical_cut = qaoa.compute_cut_value(b_str)

            # Basis statevector
            vec = np.zeros(8, dtype=complex)
            vec[b_int] = 1.0
            sv = Statevector(vec)
            quantum_cut = float(sv.expectation_value(qaoa.cost_hamiltonian).real)

            self.assertAlmostEqual(
                classical_cut,
                quantum_cut,
                places=6,
                msg=f"Discrepancy on bitstring {b_str}: classical={classical_cut}, quantum={quantum_cut}"
            )

    def test_03_qaoa_max_cut_vs_classical_optimum(self):
        """Verify QAOA finds high approximation ratio and discovers exact maximum cut."""
        # 4-node cycle graph: (0-1, 1-2, 2-3, 3-0)
        # Max-Cut is 4.0 (bipartite coloring: 0101 or 1010)
        edges = [(0, 1, 1.0), (1, 2, 1.0), (2, 3, 1.0), (3, 0, 1.0)]
        qaoa = QAOAMaxCutSolver(num_nodes=4, edges=edges, p=1)

        self.assertEqual(qaoa.classical_max_cut, 4.0)
        self.assertIn("0101", qaoa.classical_best_bitstrings)

        res = qaoa.optimize(method="COBYLA", max_iters=50, seed=42)
        self.assertGreaterEqual(res.approximation_ratio, 0.70)
        self.assertEqual(res.best_sampled_cut, 4.0)

    def test_04_vqe_energy_vs_exact_diagonalization(self):
        """Verify VQE obeys the variational principle E_VQE >= E_exact and converges within 2% error."""
        vqe = VQESolver.create_transverse_field_ising(num_qubits=3, J=1.0, g=0.8, ansatz_layers=1)
        res = vqe.optimize(method="BFGS", max_iters=150, seed=42)

        # Variational principle: E(theta) >= E_0 (within machine precision)
        self.assertGreaterEqual(res.vqe_energy, res.exact_ground_energy - 1e-6)
        # Convergence accuracy within 2%
        self.assertLess(res.relative_error, 0.02, f"VQE error too high: {res.relative_error}")

    def test_05_parameter_shift_gradient_correctness(self):
        """Verify Parameter-Shift Rule matches analytical and finite-difference gradients."""
        # Objective: f(theta) = <0| Ry^\dagger(theta) Z Ry(theta) |0> = cos(theta)
        # Derivative: d/d theta [cos(theta)] = -sin(theta)
        ansatz = HardwareEfficientAnsatz(num_qubits=1, num_layers=0, rotation_blocks=("ry",))
        H = SparsePauliOp.from_list([("Z", 1.0)])

        def energy_fn(theta_vec: np.ndarray) -> float:
            sv = ansatz.get_statevector(theta_vec)
            return float(sv.expectation_value(H).real)

        test_thetas = [0.2, 0.8, 1.5, 2.3]
        for t_val in test_thetas:
            theta = np.array([t_val])
            grad_ps = ParameterShiftGradient.compute_gradient(energy_fn, theta)[0]
            grad_fd = ParameterShiftGradient.compute_finite_difference(energy_fn, theta, eps=1e-5)[0]
            grad_exact = -np.sin(t_val)

            # Parameter shift matches exact analytical gradient
            self.assertAlmostEqual(grad_ps, grad_exact, places=5)
            # Parameter shift matches centered finite difference
            self.assertAlmostEqual(grad_ps, grad_fd, places=4)

    def test_06_spsa_parameter_updates_and_convergence(self):
        """Verify SPSA takes 2-measurement steps and successfully reduces cost."""
        # Simple quadratic cost function with known minimum at theta = [1.0, -1.0]
        def cost_fn(theta: np.ndarray) -> float:
            return float((theta[0] - 1.0)**2 + (theta[1] + 1.0)**2)

        theta_0 = np.array([4.0, -5.0])
        init_cost = cost_fn(theta_0)

        spsa = SPSAOptimizer(a=0.3, c=0.1, max_iters=60, seed=42)
        opt_theta, final_cost, history = spsa.optimize(cost_fn, theta_0)

        self.assertLess(final_cost, init_cost * 0.1)
        self.assertEqual(len(history), 61)

    def test_07_qng_metric_tensor_positive_semidefinite_and_regularized(self):
        """Verify Fubini-Study metric tensor is symmetric and regularized matrix is strictly positive definite."""
        ansatz = HardwareEfficientAnsatz(num_qubits=2, num_layers=1, rotation_blocks=("ry",))
        qng = QuantumNaturalGradient(ansatz=ansatz, learning_rate=0.05, regularization=1e-3)

        theta = np.array([0.5, -0.3, 0.8, -0.2])
        g = qng.compute_fubini_study_metric(theta)

        # Symmetry check
        self.assertTrue(np.allclose(g, g.T, atol=1e-7))

        # Regularized metric tensor eigenvalues strictly positive
        g_reg = g + 1e-3 * np.eye(len(theta))
        eigvals = np.linalg.eigvalsh(g_reg)
        self.assertTrue(np.all(eigvals > 0), f"Non-positive eigenvalues: {eigvals}")

    def test_08_shot_noise_variance_scaling(self):
        """Verify empirical variance decreases as shot count S increases."""
        results = ShotNoiseStudy.evaluate_shot_noise(
            num_qubits=2,
            shots_list=[50, 2000],
            num_trials=25,
            seed=42
        )
        var_low_shots = results[0]["variance"]
        var_high_shots = results[1]["variance"]

        self.assertGreater(var_low_shots, var_high_shots)
        self.assertLess(results[1]["std_deviation"], results[0]["std_deviation"])


if __name__ == "__main__":
    unittest.main()
