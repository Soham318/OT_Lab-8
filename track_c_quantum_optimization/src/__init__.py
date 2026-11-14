"""
Track C: Quantum Optimization
Assignment 8 - Optimize Anything
Modules:
  - circuits.py: Parameterized Quantum Circuits (PQCs) & Hardware-Efficient Ansatzes
  - qaoa.py: Quantum Approximate Optimization Algorithm (QAOA) for Max-Cut
  - vqe.py: Variational Quantum Eigensolver (VQE)
  - gradients.py: Parameter-Shift Rule & SPSA Optimizers
  - qng.py: Quantum Natural Gradient (QNG) with Fubini-Study Metric Tensor
  - barren_plateaus.py: Shot Noise and Barren Plateau Analysis
"""

from track_c_quantum_optimization.src.circuits import ParameterizedAnsatz, HardwareEfficientAnsatz
from track_c_quantum_optimization.src.qaoa import QAOAMaxCutSolver, QAOAResult
from track_c_quantum_optimization.src.vqe import VQESolver, VQEResult
from track_c_quantum_optimization.src.gradients import ParameterShiftGradient, SPSAOptimizer
from track_c_quantum_optimization.src.qng import QuantumNaturalGradient

__all__ = [
    "ParameterizedAnsatz",
    "HardwareEfficientAnsatz",
    "QAOAMaxCutSolver",
    "QAOAResult",
    "VQESolver",
    "VQEResult",
    "ParameterShiftGradient",
    "SPSAOptimizer",
    "QuantumNaturalGradient"
]

