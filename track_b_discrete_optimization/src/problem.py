r"""
Knapsack Problem Definition and Solution Data Structures
Track B: Discrete Optimization
Assignment 8 - Optimize Anything
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import numpy as np


@dataclass
class KnapsackSolution:
    """Standardized representation of a discrete optimization solution."""
    solver_name: str
    selected_items: np.ndarray  # Binary vector {0, 1}^n
    total_value: float
    total_weight: float
    capacity: float
    is_feasible: bool
    execution_time_ms: float
    optimality_gap_percent: Optional[float] = None
    extra_metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def selected_indices(self) -> List[int]:
        return [int(i) for i, x in enumerate(self.selected_items) if x == 1]


class KnapsackProblem:
    r"""
    0/1 Knapsack Problem Instance:
        Maximize \sum_{i=1}^n v_i x_i
        Subject to \sum_{i=1}^n w_i x_i <= W
                   x_i \in {0, 1}
    """

    def __init__(
        self,
        values: np.ndarray,
        weights: np.ndarray,
        capacity: float,
        name: str = "KnapsackInstance"
    ):
        v = np.asarray(values, dtype=np.float64)
        w = np.asarray(weights, dtype=np.float64)

        if len(v) != len(w):
            raise ValueError(f"Values length ({len(v)}) must match weights length ({len(w)}).")
        if len(v) == 0:
            raise ValueError("Knapsack instance must contain at least one item.")
        if np.any(v < 0):
            raise ValueError("Item values must be non-negative.")
        if np.any(w <= 0):
            raise ValueError("Item weights must be strictly positive.")
        if capacity < 0:
            raise ValueError("Knapsack capacity must be non-negative.")

        self.values = v
        self.weights = w
        self.capacity = float(capacity)
        self.n_items = len(v)
        self.name = name

    def is_feasible(self, selection: np.ndarray) -> bool:
        """Check if binary selection vector satisfies capacity constraint."""
        sel = np.asarray(selection, dtype=np.float64)
        total_w = float(np.sum(sel * self.weights))
        return total_w <= self.capacity + 1e-9

    def evaluate(self, selection: np.ndarray) -> Tuple[float, float, bool]:
        """Compute (total_value, total_weight, is_feasible)."""
        sel = np.asarray(selection, dtype=np.float64)
        val = float(np.sum(sel * self.values))
        w = float(np.sum(sel * self.weights))
        feas = w <= self.capacity + 1e-9
        return val, w, feas

    @classmethod
    def create_known_counterexample(cls) -> "KnapsackProblem":
        """
        Classic counterexample where density-based Greedy fails to find global optimum.
        Capacity: W = 50
        Items:
          Item 0: v=60,  w=10 -> density = 6.0
          Item 1: v=100, w=20 -> density = 5.0
          Item 2: v=120, w=30 -> density = 4.0
        Greedy chooses Item 0 + Item 1: value = 160, weight = 30.
        Optimal chooses Item 1 + Item 2: value = 220, weight = 50.
        Optimality gap: (220 - 160) / 220 = 27.27%.
        """
        values = np.array([60.0, 100.0, 120.0])
        weights = np.array([10.0, 20.0, 30.0])
        capacity = 50.0
        return cls(values, weights, capacity, name="GreedyCounterexample")

    @classmethod
    def generate_random_instance(
        cls,
        n_items: int = 10,
        capacity_ratio: float = 0.5,
        max_value: float = 100.0,
        max_weight: float = 50.0,
        seed: int = 42,
        name: Optional[str] = None
    ) -> "KnapsackProblem":
        """Generate reproducible random Knapsack problem instance."""
        rng = np.random.RandomState(seed)
        weights = rng.randint(5, int(max_weight) + 1, size=n_items).astype(np.float64)
        # Correlated values to ensure non-trivial combinatorial hardness
        noise = rng.uniform(0.8, 1.2, size=n_items)
        values = np.round(weights * 1.5 * noise + rng.uniform(5, max_value, size=n_items))
        values = np.maximum(values, 1.0)

        total_weight = float(np.sum(weights))
        capacity = np.round(total_weight * capacity_ratio)
        instance_name = name or f"Random_N{n_items}_Seed{seed}"
        return cls(values, weights, capacity, name=instance_name)
