r"""
Shot Noise and Barren Plateau Analysis
Track C: Quantum Optimization
Assignment 8 - Optimize Anything

Mathematical Formulation:
  1. Shot Noise Variance Scaling:
     By the Central Limit Theorem, the empirical variance of shot-based expectation values:
         \operatorname{Var}[\hat{E}_S] = \frac{\sigma^2}{S}
     where S is the number of projective measurement shots.

  2. Barren Plateau Phenomenon (McClean et al., 2018):
     For random Haar-like parameterized circuits, the gradient variance decays exponentially
     with the number of qubits:
         \operatorname{Var}_{\theta}\left[ \frac{\partial \langle H \rangle}{\partial \theta_k} \right] \in \mathcal{O}(2^{-n})
     leading to exponentially vanishing gradients and flat optimization landscapes.
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from qiskit.quantum_info import Statevector, SparsePauliOp
from track_c_quantum_optimization.src.circuits import HardwareEfficientAnsatz
from track_c_quantum_optimization.src.gradients import ParameterShiftGradient


class ShotNoiseStudy:
    """
    Evaluates the effect of finite measurement shot budgets on expectation value variance.
    """

    @staticmethod
    def evaluate_shot_noise(
        num_qubits: int = 3,
        shots_list: List[int] = [50, 200, 1000, 5000, 20000],
        num_trials: int = 30,
        seed: int = 42
    ) -> List[Dict[str, Any]]:
        ansatz = HardwareEfficientAnsatz(num_qubits=num_qubits, num_layers=1)
        rng = np.random.RandomState(seed)
        theta_fixed = rng.uniform(-np.pi, np.pi, size=ansatz.num_params)

        # Observable: H = Z_0 Z_1 + X_2
        H_list = [("Z" * 2 + "I" * (num_qubits - 2), 1.0)]
        if num_qubits >= 3:
            term = ["I"] * num_qubits
            term[2] = "X"
            H_list.append(("".join(term), 0.5))
        H = SparsePauliOp.from_list(H_list).simplify()

        sv = ansatz.get_statevector(theta_fixed)
        exact_e = float(sv.expectation_value(H).real)

        results = []
        for s in shots_list:
            trial_estimates = []
            for rep in range(num_trials):
                counts = sv.sample_counts(shots=s)
                # Compute expectation value from bitstring sample counts for diagonal Z-terms
                # Approximate energy from counts
                # To be general: estimate using sample probabilities
                est_val = 0.0
                for b_str, count in counts.items():
                    # Qiskit bitstring order: q_{n-1} ... q_0
                    bits = [int(ch) for ch in reversed(b_str)]
                    z0 = 1.0 - 2.0 * bits[0]
                    z1 = 1.0 - 2.0 * bits[1]
                    # Sample observable eigenvalue
                    sample_eig = z0 * z1
                    est_val += (count / s) * sample_eig
                trial_estimates.append(est_val)

            mean_est = float(np.mean(trial_estimates))
            var_est = float(np.var(trial_estimates))
            std_est = float(np.std(trial_estimates))
            err_est = float(abs(mean_est - exact_e))

            results.append({
                "shots": s,
                "exact_expectation": round(exact_e, 6),
                "mean_estimate": round(mean_est, 6),
                "variance": round(var_est, 8),
                "std_deviation": round(std_est, 6),
                "absolute_error": round(err_est, 6),
                "theoretical_scaling_factor": round(1.0 / np.sqrt(s), 6)
            })

        return results


class BarrenPlateauStudy:
    """
    Empirical demonstration of the Barren Plateau phenomenon:
    Exponential vanishing of gradient variance as qubit count n increases.
    """

    @staticmethod
    def run_qubit_variance_scaling(
        qubit_range: List[int] = [2, 3, 4, 5, 6, 7],
        num_samples: int = 35,
        seed: int = 42
    ) -> List[Dict[str, Any]]:
        rng = np.random.RandomState(seed)
        results = []

        for n in qubit_range:
            # Random deep hardware-efficient ansatz (layers = n to approximate 2-design)
            layers = max(2, n)
            ansatz = HardwareEfficientAnsatz(num_qubits=n, num_layers=layers, entanglement="linear")

            # Local observable: H = Z_0 Z_1
            H_term = ["I"] * n
            H_term[0] = "Z"
            H_term[1] = "Z"
            H = SparsePauliOp.from_list([("".join(H_term), 1.0)])

            def energy_fn(theta_vec: np.ndarray) -> float:
                sv = ansatz.get_statevector(theta_vec)
                return float(sv.expectation_value(H).real)

            # Sample random parameter configurations uniformly from [-pi, pi]
            gradients_param0 = []
            for rep in range(num_samples):
                theta_rand = rng.uniform(-np.pi, np.pi, size=ansatz.num_params)
                # Compute partial derivative specifically for parameter 0 via parameter-shift
                # (Evaluates only 2 circuits instead of 2 * num_params)
                theta_plus = np.array(theta_rand, copy=True)
                theta_plus[0] += np.pi / 2.0
                theta_minus = np.array(theta_rand, copy=True)
                theta_minus[0] -= np.pi / 2.0

                g0 = (energy_fn(theta_plus) - energy_fn(theta_minus)) / 2.0
                gradients_param0.append(float(g0))

            grad_mean = float(np.mean(gradients_param0))
            grad_var = float(np.var(gradients_param0))

            results.append({
                "num_qubits": n,
                "circuit_layers": layers,
                "num_parameters": ansatz.num_params,
                "circuit_depth": ansatz.depth,
                "num_samples": num_samples,
                "gradient_mean": round(grad_mean, 8),
                "gradient_variance": float(grad_var),
                "theoretical_2_minus_n": float(2.0 ** (-n))
            })

        return results
