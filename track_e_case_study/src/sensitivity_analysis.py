"""
Multi-Objective Weight Sensitivity Analysis
Track E: Railway Route and Transfer Optimization
Assignment 8 - Optimize Anything

Evaluates how changing the objective weights (alpha, beta, gamma) affects:
  - Route selection
  - Number of transfers
  - Total journey duration
  - Transfer waiting time
"""

import json
import os
from typing import Dict, List

from .graph import load_network_from_data
from .greedy_optimizer import GreedyRailwayOptimizer
from .ilp_optimizer import ILPRailwayOptimizer

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def run_weight_sensitivity_study() -> Dict:
    """Run sensitivity analysis across 4 passenger preference profiles."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    network = load_network_from_data()

    profiles = [
        {"name": "Pure Duration Minimizer", "alpha": 1.0, "beta": 0.5, "gamma": 0.0},
        {"name": "Standard Balanced", "alpha": 1.0, "beta": 1.5, "gamma": 30.0},
        {"name": "Transfer-Averse (Luggage)", "alpha": 1.0, "beta": 2.0, "gamma": 75.0},
        {"name": "Fast Speed Commuter", "alpha": 2.0, "beta": 0.5, "gamma": 10.0}
    ]

    test_queries = [
        {"orig": "STN_11", "dest": "STN_06", "dep": 360, "desc": "Westport Bay to Metro Interchange"},
        {"orig": "STN_15", "dest": "STN_07", "dep": 390, "desc": "Eastport to Highland Junction"},
        {"orig": "STN_01", "dest": "STN_08", "dep": 1020, "desc": "South Central to Northgate City"},
    ]

    results = []

    for q in test_queries:
        query_entry = {"query": q, "profiles": []}
        for prof in profiles:
            ilp = ILPRailwayOptimizer(
                network,
                alpha=prof["alpha"],
                beta=prof["beta"],
                gamma=prof["gamma"]
            )
            res = ilp.solve(q["orig"], q["dest"], q["dep"])
            prof_record = {
                "profile_name": prof["name"],
                "weights": {"alpha": prof["alpha"], "beta": prof["beta"], "gamma": prof["gamma"]},
                "found": res.found,
                "departure_hhmm": res.departure_hhmm,
                "arrival_hhmm": res.arrival_hhmm,
                "total_journey_min": res.total_journey_time_min,
                "travel_time_min": res.total_travel_time_min,
                "waiting_time_min": res.total_waiting_time_min,
                "num_transfers": res.num_transfers,
                "service_sequence": [leg.service_name for leg in res.legs]
            }
            query_entry["profiles"].append(prof_record)
        results.append(query_entry)

    out_path = os.path.join(RESULTS_DIR, "weight_sensitivity_results.json")
    with open(out_path, mode="w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Weight sensitivity study completed: {out_path}")
    return results


if __name__ == "__main__":
    run_weight_sensitivity_study()

