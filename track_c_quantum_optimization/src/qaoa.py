r"""
Quantum Approximate Optimization Algorithm (QAOA) for Max-Cut
Track C: Quantum Optimization
Assignment 8 - Optimize Anything

Mathematical Formulation:
  Graph G = (V, E) with weights w_{uv}.
  Cost Hamiltonian:
      H_C = \sum_{(u, v) \in E} \frac{w_{uv}}{2} (I - Z_u Z_v)
  Mixer Hamiltonian:
      H_M = \sum_{u \in V} X_u
  QAOA Circuit:
      |\psi(\gamma, \beta)> = \prod_{l=1}^p \left( e^{-i \beta_l H_M} e^{-i \gamma_l H_C} \right) |+>^{\otimes n}
  Approximation Ratio:
      \alpha = <\psi | H_C | \psi> / C_max
"""

from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy.optimize import minimize

from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector, SparsePauliOp


@dataclass
class QAOAResult:
    """Stores full metrics of a QAOA optimization run."""
    graph_num_nodes: int
    graph_num_edges: int
    p_depth: int
    optimal_gamma: np.ndarray
    optimal_beta: np.ndarray
    expected_cut_value: float
    best_sampled_cut: float
    best_bitstring: str
    classical_max_cut: float
    classical_optimal_bitstrings: List[str]
    approximation_ratio: float
    execution_time_ms: float
    optimization_iterations: int
    cost_history: List[float] = field(default_factory=list)


class QAOAMaxCutSolver:
    """
    QAOA Solver for the Max-Cut problem on an arbitrary undirected graph.
    Supports arbitrary circuit depth p and classical parameter optimization.
    """

    def __init__(
        self,
        num_nodes: int,
        edges: List[Tuple[int, int, float]],
        p: int = 1
    ):
        if num_nodes < 2:
            raise ValueError("Graph must contain at least 2 nodes.")
        if p < 1:
            raise ValueError("QAOA depth p must be >= 1.")

        self.num_nodes = num_nodes
        self.edges = [(int(u), int(v), float(w)) for u, v, w in edges]
        self.p = p

        # Construct exact Pauli Cost Hamiltonian
        self.cost_hamiltonian = self._build_cost_hamiltonian()
        self.classical_max_cut, self.classical_best_bitstrings = self._solve_classical_exact()

    def _build_cost_hamiltonian(self) -> SparsePauliOp:
        r"""
        H_C = sum_{(u,v) \in E} (w_{uv}/2) * (I - Z_u Z_v)
        """
        pauli_list = []
        for u, v, w in self.edges:
            # Identity term
            pauli_list.append(("I" * self.num_nodes, 0.5 * w))
            # Z_u Z_v term
            z_term = ["I"] * self.num_nodes
            z_term[u] = "Z"
            z_term[v] = "Z"
            pauli_list.append(("".join(z_term), -0.5 * w))

        return SparsePauliOp.from_list(pauli_list).simplify()

    def _solve_classical_exact(self) -> Tuple[float, List[str]]:
        """Compute exact ground truth Max-Cut via exhaustive search."""
        max_cut = -1.0
        best_bitstrings = []
        for b in range(1 << self.num_nodes):
            bits = [(b >> i) & 1 for i in range(self.num_nodes)]
            cut = sum(w for u, v, w in self.edges if bits[u] != bits[v])
            b_str = "".join(str(bit) for bit in reversed(bits))
            if cut > max_cut:
                max_cut = cut
                best_bitstrings = [b_str]
            elif cut == max_cut:
                best_bitstrings.append(b_str)
        return float(max_cut), best_bitstrings

    def compute_cut_value(self, bitstring: str) -> float:
        """Evaluate cut value for a binary bitstring."""
        # Qiskit bitstring order is reversed (q_{n-1} ... q_0)
        bits = [int(ch) for ch in reversed(bitstring)]
        return float(sum(w for u, v, w in self.edges if bits[u] != bits[v]))

    def build_qaoa_circuit(self, gamma: np.ndarray, beta: np.ndarray) -> QuantumCircuit:
        """Construct QAOA circuit for specific parameter values."""
        qc = QuantumCircuit(self.num_nodes)

        # Initial equal superposition: |+>^{\otimes n}
        qc.h(range(self.num_nodes))

        # p alternating layers
        for l in range(self.p):
            g = float(gamma[l])
            b = float(beta[l])

            # 1. Cost Unitary: e^{-i \gamma_l H_C}
            for u, v, w in self.edges:
                # e^{i (\gamma w / 2) Z_u Z_v} via CX - Rz - CX
                qc.cx(u, v)
                qc.rz(-g * w, v)
                qc.cx(u, v)

            # 2. Mixer Unitary: e^{-i \beta_l H_M} = \prod Rx(2 \beta)
            for u in range(self.num_nodes):
                qc.rx(2.0 * b, u)

        return qc

    def evaluate_expected_cut(self, theta: np.ndarray) -> float:
        """Compute expected cut value <psi | H_C | psi>."""
        gamma = theta[:self.p]
        beta = theta[self.p:]
        qc = self.build_qaoa_circuit(gamma, beta)
        sv = Statevector(qc)
        exp_val = sv.expectation_value(self.cost_hamiltonian).real
        return float(exp_val)

    def optimize(
        self,
        method: str = "COBYLA",
        max_iters: int = 100,
        seed: int = 42
    ) -> QAOAResult:
        """
        Execute classical optimization of QAOA variational parameters.
        Maximizes expected cut <H_C> by minimizing -<H_C>.
        """
        t0 = time.perf_counter()
        rng = np.random.RandomState(seed)

        # Initial parameter guess
        init_gamma = rng.uniform(0.0, np.pi, size=self.p)
        init_beta = rng.uniform(0.0, np.pi / 2.0, size=self.p)
        theta_0 = np.concatenate([init_gamma, init_beta])

        cost_history: List[float] = []

        def loss(theta_vec: np.ndarray) -> float:
            exp_cut = self.evaluate_expected_cut(theta_vec)
            cost_history.append(exp_cut)
            return -exp_cut  # Minimize negative cut

        res = minimize(
            loss,
            theta_0,
            method=method,
            options={"maxiter": max_iters, "disp": False}
        )

        opt_theta = res.x
        opt_gamma = opt_theta[:self.p]
        opt_beta = opt_theta[self.p:]

        expected_cut = self.evaluate_expected_cut(opt_theta)

        # Sample bitstrings from final statevector
        final_qc = self.build_qaoa_circuit(opt_gamma, opt_beta)
        final_sv = Statevector(final_qc)
        counts = final_sv.sample_counts(shots=2048)

        best_sample_cut = -1.0
        best_bitstring = ""
        for b_str in counts:
            cut_val = self.compute_cut_value(b_str)
            if cut_val > best_sample_cut:
                best_sample_cut = cut_val
                best_bitstring = b_str

        approx_ratio = (expected_cut / self.classical_max_cut) if self.classical_max_cut > 0 else 1.0
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return QAOAResult(
            graph_num_nodes=self.num_nodes,
            graph_num_edges=len(self.edges),
            p_depth=self.p,
            optimal_gamma=opt_gamma,
            optimal_beta=opt_beta,
            expected_cut_value=float(expected_cut),
            best_sampled_cut=float(best_sample_cut),
            best_bitstring=best_bitstring,
            classical_max_cut=self.classical_max_cut,
            classical_optimal_bitstrings=self.classical_best_bitstrings,
            approximation_ratio=float(approx_ratio),
            execution_time_ms=elapsed_ms,
            optimization_iterations=len(cost_history),
            cost_history=cost_history
        )
