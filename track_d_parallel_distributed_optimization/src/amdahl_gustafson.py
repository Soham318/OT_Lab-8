r"""Amdahl's Law and Gustafson's Law Modeling & Analysis Module.

Provides theoretical formulations, numerical evaluations, curve fitting,
and empirical comparisons for:
- Amdahl's Law (Strong Scaling, Fixed Problem Size):
      S(N) = \frac{1}{(1 - P) + P / N}
- Gustafson-Barsis's Law (Weak Scaling, Scaled Problem Size):
      S(N) = N - (1 - P)(N - 1) = (1 - P) + P \cdot N
"""

from typing import Any, Dict, List, Tuple
import numpy as np
from scipy.optimize import curve_fit


def amdahl_speedup(num_workers: np.ndarray | float, parallel_fraction: float) -> np.ndarray | float:
    r"""Compute theoretical speedup according to Amdahl's Law (Strong Scaling).

    Formula:
        S(N) = \frac{1}{(1 - P) + P / N}

    Args:
        num_workers: Processor / worker count N (>= 1).
        parallel_fraction: Fraction of program that can be parallelized P in [0, 1].

    Returns:
        Theoretical speedup S(N).
    """
    if not (0.0 <= parallel_fraction <= 1.0):
        raise ValueError(f"parallel_fraction must be in [0, 1], got {parallel_fraction}")

    N = np.asarray(num_workers, dtype=float)
    if np.any(N < 1.0):
        raise ValueError("num_workers must be >= 1")

    s = 1.0 - parallel_fraction  # serial fraction
    denom = s + (parallel_fraction / N)
    return 1.0 / denom


def gustafson_speedup(num_workers: np.ndarray | float, parallel_fraction: float) -> np.ndarray | float:
    r"""Compute theoretical speedup according to Gustafson's Law (Weak Scaling).

    Formula:
        S(N) = N - (1 - P)(N - 1) = (1 - P) + P * N

    Args:
        num_workers: Processor / worker count N (>= 1).
        parallel_fraction: Parallel fraction of scaled workload P in [0, 1].

    Returns:
        Theoretical scaled speedup S(N).
    """
    if not (0.0 <= parallel_fraction <= 1.0):
        raise ValueError(f"parallel_fraction must be in [0, 1], got {parallel_fraction}")

    N = np.asarray(num_workers, dtype=float)
    if np.any(N < 1.0):
        raise ValueError("num_workers must be >= 1")

    s = 1.0 - parallel_fraction
    return N - s * (N - 1.0)


class ScalingLawAnalyzer:
    """Analyzer comparing theoretical scaling predictions against measured empirical performance."""

    @staticmethod
    def fit_amdahl_fraction(
        measured_workers: List[int], measured_speedups: List[float]
    ) -> Tuple[float, float, float]:
        r"""Fit empirical speedups to Amdahl's Law using non-linear least squares.

        Returns:
            (estimated_parallel_fraction, estimated_serial_fraction, r_squared)
        """
        x_data = np.asarray(measured_workers, dtype=float)
        y_data = np.asarray(measured_speedups, dtype=float)

        if len(x_data) < 2:
            raise ValueError("Need at least 2 data points to fit Amdahl fraction")

        def model(N, p):
            return 1.0 / ((1.0 - p) + (p / N))

        # Initial guess p=0.8
        popt, _ = curve_fit(model, x_data, y_data, p0=[0.8], bounds=(0.0, 1.0))
        p_est = float(popt[0])
        s_est = 1.0 - p_est

        # Compute R^2
        residuals = y_data - model(x_data, p_est)
        ss_res = float(np.sum(residuals ** 2))
        ss_tot = float(np.sum((y_data - np.mean(y_data)) ** 2))
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 1.0

        return p_est, s_est, r2

    @staticmethod
    def generate_theoretical_curves(
        max_workers: int = 32,
        parallel_fractions: List[float] = [0.5, 0.75, 0.9, 0.95, 0.99],
    ) -> Dict[str, Any]:
        """Generate curve points for multi-curve Amdahl and Gustafson comparison."""
        workers = np.arange(1, max_workers + 1, dtype=float)
        amdahl_curves = {}
        gustafson_curves = {}

        for p in parallel_fractions:
            p_key = f"P={int(p*100)}%"
            amdahl_curves[p_key] = [float(val) for val in amdahl_speedup(workers, p)]
            gustafson_curves[p_key] = [float(val) for val in gustafson_speedup(workers, p)]

        # Asymptotic Amdahl limits: S_max = 1 / (1 - P)
        asymptotic_limits = {
            f"P={int(p*100)}%": (1.0 / (1.0 - p)) if p < 1.0 else float("inf")
            for p in parallel_fractions
        }

        return {
            "worker_counts": [int(w) for w in workers],
            "parallel_fractions": parallel_fractions,
            "amdahl_curves": amdahl_curves,
            "gustafson_curves": gustafson_curves,
            "asymptotic_limits": asymptotic_limits,
        }

    @staticmethod
    def comparative_summary(
        p_est: float, s_est: float, max_tested_workers: int
    ) -> Dict[str, Any]:
        """Produce a structured theoretical analysis of scaling limits."""
        amdahl_asymptote = 1.0 / s_est if s_est > 0 else float("inf")
        predicted_amdahl_max = float(amdahl_speedup(max_tested_workers, p_est))
        predicted_gustafson_max = float(gustafson_speedup(max_tested_workers, p_est))

        return {
            "estimated_parallel_fraction": p_est,
            "estimated_serial_fraction": s_est,
            "theoretical_asymptotic_speedup": amdahl_asymptote,
            "predicted_amdahl_speedup_at_max": predicted_amdahl_max,
            "predicted_gustafson_speedup_at_max": predicted_gustafson_max,
            "interpretation": (
                f"With an estimated serial fraction of {s_est:.2%}, Amdahl's Law caps the maximum "
                f"attainable speedup at {amdahl_asymptote:.2f}x under strong scaling regardless of "
                f"core count. In contrast, Gustafson's Law predicts weak-scaling speedup of "
                f"{predicted_gustafson_max:.2f}x at {max_tested_workers} workers when problem "
                "size expands proportionally."
            ),
        }

