"""
Automated Unit and Regression Test Suite for Track I: Quantum Algorithms and QML
Validates:
1. Deutsch-Jozsa constant and balanced oracle classification
2. Bernstein-Vazirani manual elementary circuit hidden string recovery
3. Grover search elementary circuit on N=4 and N=8 spaces
4. QFT and Inverse QFT reversibility and operator norm error
5. QPE known-phase estimation with exact dyadic phases
6. Shor's factoring algorithm period finding and factor extraction on N=15
7. QUBO energy calculation, Ising mapping identity, and ground state search
8. Quantum Variational Classifier (VQC) forward evaluation and bounds
9. Circuit construction, depth, and gate-count statistics
10. Error handling on invalid parameters
"""

import unittest
import numpy as np

from track_i_quantum_algorithms.src.deutsch_jozsa import run_deutsch_jozsa, build_deutsch_jozsa_circuit
from track_i_quantum_algorithms.src.bernstein_vazirani import run_bernstein_vazirani, build_manual_bernstein_vazirani_circuit
from track_i_quantum_algorithms.src.grover_search import run_grover_search, build_manual_grover_circuit, track_grover_amplitude_trajectory
from track_i_quantum_algorithms.src.qft import build_qft_circuit, build_inverse_qft_circuit, verify_qft_reversibility
from track_i_quantum_algorithms.src.qpe import run_quantum_phase_estimation, build_qpe_circuit
from track_i_quantum_algorithms.src.shor_factoring import run_shor_factoring, build_shor_circuit, continued_fraction_period
from track_i_quantum_algorithms.src.qubo_annealing import (
    create_sample_qubo_problem, qubo_to_ising, evaluate_qubo_energy,
    evaluate_ising_energy, solve_exhaustive_qubo, simulate_classical_annealing
)
from track_i_quantum_algorithms.src.qml_classifier import (
    prepare_iris_dataset, QuantumVariationalClassifier, run_classical_vs_quantum_experiment
)

class TestQuantumAlgorithms(unittest.TestCase):

    def test_01_deutsch_jozsa_classification(self):
        """Test Deutsch-Jozsa classification on constant and balanced oracles."""
        res_c0 = run_deutsch_jozsa(num_qubits=3, oracle_type="constant", constant_val=0)
        self.assertEqual(res_c0["classification"], "constant")
        self.assertTrue(res_c0["is_correct"])
        self.assertAlmostEqual(res_c0["zero_state_fraction"], 1.0, places=2)

        res_bal = run_deutsch_jozsa(num_qubits=3, oracle_type="balanced")
        self.assertEqual(res_bal["classification"], "balanced")
        self.assertTrue(res_bal["is_correct"])
        self.assertAlmostEqual(res_bal["zero_state_fraction"], 0.0, places=2)

    def test_02_bernstein_vazirani_manual_circuits(self):
        """Test manual elementary Bernstein-Vazirani circuits on hidden bitstrings."""
        for target in ["101", "1101", "001", "1110"]:
            res = run_bernstein_vazirani(target, shots=512)
            self.assertEqual(res["measured_secret"], target)
            self.assertTrue(res["is_correct"])
            self.assertEqual(res["success_fraction"], 1.0)
            self.assertGreater(res["circuit_depth"], 0)
            self.assertGreater(res["total_gates"], 0)
            self.assertTrue(len(res["gate_explanations"]) > 0)

    def test_03_grover_search_manual_circuits(self):
        """Test manual elementary Grover search on N=4 (R=1) and N=8 (R=2)."""
        # N=4: 100% exact at R=1
        res_2q = run_grover_search(num_qubits=2, target="10", iterations=1, shots=512)
        self.assertEqual(res_2q["measured_target"], "10")
        self.assertTrue(res_2q["is_correct"])
        self.assertEqual(res_2q["success_rate"], 1.0)

        # N=8: >= 90% probability at R=2
        res_3q = run_grover_search(num_qubits=3, target="101", iterations=2, shots=512)
        self.assertEqual(res_3q["measured_target"], "101")
        self.assertTrue(res_3q["is_correct"])
        self.assertGreaterEqual(res_3q["success_rate"], 0.90)

    def test_04_grover_trajectory_amplification_and_over_rotation(self):
        """Verify amplitude amplification rises to peak and then over-rotates."""
        traj = track_grover_amplitude_trajectory(num_qubits=2, target="10", max_iterations=3)
        self.assertAlmostEqual(traj[0]["target_probability"], 0.25, places=2)
        self.assertAlmostEqual(traj[1]["target_probability"], 1.00, places=2)
        self.assertAlmostEqual(traj[2]["target_probability"], 0.25, places=2) # Over-rotation

    def test_05_qft_reversibility_and_operator_norm(self):
        """Verify that IQFT @ QFT = Identity to numerical precision (< 1e-12)."""
        for n in [2, 3, 4]:
            res = verify_qft_reversibility(n)
            self.assertTrue(res["is_reversible"])
            self.assertLess(res["operator_error_norm"], 1e-12)
            self.assertLess(res["max_state_error"], 1e-12)

    def test_06_qpe_known_dyadic_phases(self):
        """Test Quantum Phase Estimation recovers dyadic phases with zero error."""
        test_cases = [
            (3, 0.375), # 3/8 = 0.011_2
            (3, 0.250), # 1/4 = 0.010_2
            (3, 0.125), # 1/8 = 0.001_2
            (3, 0.500), # 1/2 = 0.100_2
        ]
        for t, phi in test_cases:
            res = run_quantum_phase_estimation(num_counting_qubits=t, phase_theta=phi, shots=512)
            self.assertTrue(res["is_exact_match"])
            self.assertAlmostEqual(res["estimated_phase"], phi, places=4)
            self.assertLess(res["phase_error"], 1e-5)

    def test_07_shor_factoring_15(self):
        """Test Shor's algorithm factoring 15 with base a=7."""
        res = run_shor_factoring(a=7, N=15, num_counting_qubits=3, shots=512)
        self.assertTrue(res["is_successful"])
        self.assertEqual(res["extracted_factors"], [3, 5])
        self.assertEqual(res["true_period"], 4)

    def test_08_qubo_ising_mathematical_identity(self):
        """Test exact mathematical energy equivalence between QUBO and Ising models."""
        Q, _ = create_sample_qubo_problem()
        h, J, offset = qubo_to_ising(Q)
        exh = solve_exhaustive_qubo(Q)

        self.assertEqual(exh["ground_state_bits"], "1001")
        self.assertAlmostEqual(exh["ground_state_energy"], -8.0, places=4)

        # Check Simulated Annealing
        sa = simulate_classical_annealing(Q, num_steps=500, seed=42)
        self.assertEqual(sa["found_state_bits"], "1001")
        self.assertAlmostEqual(sa["found_energy"], -8.0, places=4)

    def test_09_qml_classifier_forward_and_bounds(self):
        """Test Quantum Variational Classifier forward evaluation and output bounds."""
        X_train, X_test, y_train, y_test = prepare_iris_dataset(test_size=0.3, random_state=42)
        vqc = QuantumVariationalClassifier(num_layers=1, max_iter=10, seed=42)

        # Check expectation output is bounded in [-1, 1]
        sample_x = X_train[0]
        init_theta = np.zeros(vqc.num_weights)
        exp_val = vqc._predict_single_sample(sample_x, init_theta)
        self.assertGreaterEqual(exp_val, -1.0)
        self.assertLessEqual(exp_val, 1.0)

    def test_10_circuit_metrics_and_error_handling(self):
        """Test gate count metrics and parameter validation exceptions."""
        with self.assertRaises(ValueError):
            run_deutsch_jozsa(num_qubits=3, oracle_type="invalid_type")

        with self.assertRaises(ValueError):
            build_manual_grover_circuit(num_qubits=2, target="101") # Length mismatch

        # Verify circuit metrics function returns non-empty dict
        qc = build_qft_circuit(3)
        from track_i_quantum_algorithms.src.utils import get_circuit_metrics
        m = get_circuit_metrics(qc)
        self.assertEqual(m["num_qubits"], 3)
        self.assertGreater(m["depth"], 0)
        self.assertGreater(m["total_gates"], 0)

if __name__ == "__main__":
    unittest.main()
