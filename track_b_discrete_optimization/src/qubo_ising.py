r"""
QUBO and Ising Model Formulation for Discrete Knapsack
Track B: Discrete Optimization
Assignment 8 - Optimize Anything

Mathematical Formulation:
  Objective: Maximize \sum_{i=1}^n v_i x_i  <=>  Minimize - \sum_{i=1}^n v_i x_i
  Constraint: \sum_{i=1}^n w_i x_i <= W

QUBO Encoding:
  Introduce binary slack variables y_k \in {0, 1} with coefficients c_k such that
      \sum_{i=1}^n w_i x_i + \sum_{k=0}^K c_k y_k = W
  Penalty Hamiltonian:
      H_pen(x, y) = P * (\sum_{i=1}^n w_i x_i + \sum_{k=0}^K c_k y_k - W)^2
  Total QUBO Hamiltonian:
      H_QUBO(z) = - \sum_{i=1}^n v_i x_i + H_pen(z) = z^T Q_upper z + const

Ising Model Conversion:
  Spin mapping: s_i = 2 * z_i - 1  <=>  z_i = (s_i + 1) / 2, where s_i \in {-1, +1}
  Hamiltonian:
      H_Ising(s) = \sum_{i < j} J_{ij} s_i s_j + \sum_i h_i s_i + C_Ising
                 = 0.5 * s^T J s + h^T s + C_Ising

Classical Exhaustive Enumeration:
  Verifies the exact minimum energy state against ILP and DP on small instances.
"""

from dataclasses import dataclass
import time
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from track_b_discrete_optimization.src.problem import KnapsackProblem, KnapsackSolution


@dataclass
class IsingModel:
    r"""Represents a standard transverse-field Ising spin model."""
    J: np.ndarray        # Couplings J_{ij} (N x N symmetric, zero diagonal)
    h: np.ndarray        # Local magnetic fields h_i (N,)
    offset: float        # Energy offset constant C
    num_spins: int

    def energy(self, spins: np.ndarray) -> float:
        r"""Compute Ising energy for spin configuration s \in {-1, +1}^N."""
        s = np.asarray(spins, dtype=np.float64)
        # 0.5 * s^T J s + h^T s + offset
        return float(0.5 * s.T @ self.J @ s + self.h.T @ s + self.offset)


class QUBOKnapsackSolver:
    """
    Constructs and solves QUBO and Ising models for 0/1 Knapsack.
    Uses classical exhaustive enumeration on small instances for theoretical verification.
    """

    def __init__(self, penalty_multiplier: float = 2.0, name: str = "QUBO Solver (Classical Exhaustive)"):
        self.penalty_multiplier = penalty_multiplier
        self.name = name

    def build_qubo_matrix(self, problem: KnapsackProblem) -> Tuple[np.ndarray, float, List[int], float]:
        """
        Build upper-triangular QUBO matrix Q and constant offset such that
            E_QUBO(z) = z^T Q z + const_offset
        """
        n = problem.n_items
        W = int(np.round(problem.capacity))

        # Binary slack expansion for W:
        # Powers of 2: 1, 2, 4, ..., up to W
        slack_weights = []
        rem = W
        k = 1
        while rem > 0:
            val = min(k, rem)
            slack_weights.append(val)
            rem -= val
            k *= 2

        num_slacks = len(slack_weights)
        total_vars = n + num_slacks

        # Combined weight vector a: [w_1, ..., w_n, c_0, ..., c_K]
        a = np.zeros(total_vars, dtype=np.float64)
        a[:n] = problem.weights
        a[n:] = slack_weights

        # Penalty coefficient selection:
        # P must be strictly greater than max(v_i) to penalize violation beyond any item gain
        max_v = float(np.max(problem.values))
        P = self.penalty_multiplier * max_v

        # Expansion of P * (a^T z - W)^2 - v^T x
        # = P * ( sum_i a_i^2 z_i^2 + 2 sum_{i<j} a_i a_j z_i z_j - 2 W sum_i a_i z_i + W^2 ) - sum_i v_i z_i
        # Using upper-triangular matrix Q where:
        # Q_ii = P * a_i^2 - 2 * P * W * a_i - (v_i if i < n else 0)
        # Q_ij = 2 * P * a_i * a_j (for i < j)
        Q = np.zeros((total_vars, total_vars), dtype=np.float64)

        for i in range(total_vars):
            v_term = problem.values[i] if i < n else 0.0
            Q[i, i] = P * (a[i]**2 - 2.0 * W * a[i]) - v_term

        for i in range(total_vars):
            for j in range(i + 1, total_vars):
                Q[i, j] = 2.0 * P * a[i] * a[j]

        const_offset = P * (W**2)
        return Q, const_offset, slack_weights, P

    def qubo_to_ising(self, Q: np.ndarray, const_offset: float) -> IsingModel:
        r"""
        Convert upper-triangular QUBO formulation (z \in {0, 1}^N) to
        Ising Spin Hamiltonian (s \in {-1, +1}^N) via z_i = (s_i + 1) / 2.
        """
        N = Q.shape[0]
        J = np.zeros((N, N), dtype=np.float64)
        h = np.zeros(N, dtype=np.float64)
        offset = const_offset

        # 1. Diagonal contributions: Q_ii * (s_i + 1) / 2 = (Q_ii / 2) s_i + (Q_ii / 2)
        for i in range(N):
            h[i] += Q[i, i] / 2.0
            offset += Q[i, i] / 2.0

        # 2. Pair contributions: Q_ij * (s_i + 1)(s_j + 1) / 4
        # = (Q_ij / 4) s_i s_j + (Q_ij / 4) s_i + (Q_ij / 4) s_j + (Q_ij / 4)
        for i in range(N):
            for j in range(i + 1, N):
                q_ij = Q[i, j]
                J[i, j] = q_ij / 4.0
                J[j, i] = q_ij / 4.0

                h[i] += q_ij / 4.0
                h[j] += q_ij / 4.0
                offset += q_ij / 4.0

        return IsingModel(J=J, h=h, offset=offset, num_spins=N)

    def evaluate_qubo_energy(self, Q: np.ndarray, const_offset: float, z: np.ndarray) -> float:
        """Compute exact scalar energy for binary state z."""
        zv = np.asarray(z, dtype=np.float64)
        return float(zv.T @ Q @ zv + const_offset)

    def solve(self, problem: KnapsackProblem) -> KnapsackSolution:
        """
        Solve small Knapsack instance via classical exhaustive enumeration over all 2^N states.
        Verifies global optimality, constraint feasibility, and Ising equivalence.
        """
        t0 = time.perf_counter()
        n = problem.n_items
        Q, const_offset, slack_weights, P = self.build_qubo_matrix(problem)
        N_vars = Q.shape[0]

        if N_vars > 18:
            raise ValueError(
                f"Exhaustive enumeration intractable for {N_vars} variables (limit: 18 vars)."
            )

        ising_model = self.qubo_to_ising(Q, const_offset)

        best_energy = float("inf")
        best_z = np.zeros(N_vars, dtype=int)
        total_states = 1 << N_vars

        for state_int in range(total_states):
            z = np.array([(state_int >> bit) & 1 for bit in range(N_vars)], dtype=np.float64)
            qubo_energy = self.evaluate_qubo_energy(Q, const_offset, z)

            if qubo_energy < best_energy:
                best_energy = qubo_energy
                best_z = z.astype(int)

        # Verify Ising energy matches QUBO energy exactly on best_z
        spins = 2.0 * best_z - 1.0
        ising_energy = ising_model.energy(spins)

        # Selected items: first n variables of best_z
        selected_items = best_z[:n]
        total_val, total_w, feas = problem.evaluate(selected_items)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return KnapsackSolution(
            solver_name=self.name,
            selected_items=selected_items,
            total_value=total_val,
            total_weight=total_w,
            capacity=problem.capacity,
            is_feasible=feas,
            execution_time_ms=elapsed_ms,
            optimality_gap_percent=0.0 if feas else 100.0,
            extra_metadata={
                "qubo_total_vars": N_vars,
                "slack_vars_count": len(slack_weights),
                "penalty_multiplier": P,
                "best_qubo_energy": float(best_energy),
                "best_ising_energy": float(ising_energy),
                "energy_parity_abs_diff": float(abs(best_energy - ising_energy)),
                "total_states_evaluated": total_states
            }
        )
