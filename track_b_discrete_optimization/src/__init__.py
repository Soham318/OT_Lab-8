"""
Track B: Discrete Optimization
Assignment 8: Optimize Anything
Algorithms:
  - Greedy Density Heuristic (greedy_solver.py)
  - Integer Linear Programming (ilp_solver.py) via SciPy HiGHS
  - Branch-and-Bound with LP Relaxation (branch_and_bound.py)
  - Dynamic Programming with Backtracking (dp_solver.py)
  - QUBO & Ising Model Formulation (qubo_ising.py)
"""

from track_b_discrete_optimization.src.problem import KnapsackProblem, KnapsackSolution
from track_b_discrete_optimization.src.greedy_solver import GreedyKnapsackSolver
from track_b_discrete_optimization.src.ilp_solver import ILPKnapsackSolver
from track_b_discrete_optimization.src.branch_and_bound import BranchAndBoundSolver
from track_b_discrete_optimization.src.dp_solver import DPKnapsackSolver
from track_b_discrete_optimization.src.qubo_ising import QUBOKnapsackSolver, IsingModel

__all__ = [
    "KnapsackProblem",
    "KnapsackSolution",
    "GreedyKnapsackSolver",
    "ILPKnapsackSolver",
    "BranchAndBoundSolver",
    "DPKnapsackSolver",
    "QUBOKnapsackSolver",
    "IsingModel"
]

