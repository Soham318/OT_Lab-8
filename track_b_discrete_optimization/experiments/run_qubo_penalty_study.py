r"""
QUBO Penalty Sensitivity and Feasibility Study
Track B: Discrete Optimization
Assignment 8 - Optimize Anything

Investigates the effect of the constraint penalty coefficient:
    P = \alpha * max(v_i)
across \alpha \in [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 5.0]

Demonstrates the phase transition between:
  1. Under-penalized regime (\alpha < 1.0):
     Penalty is insufficient to suppress invalid states; ground state violates capacity!
  2. Safe penalized regime (\alpha >= 1.0):
     Constraint violation incurs penalty strictly greater than any item value gain;
     ground state is guaranteed feasible and matches exact discrete optimum.
"""

import json
import os
import sys
from typing import Dict, List, Any
import numpy as np

from track_b_discrete_optimization.src.problem import KnapsackProblem
from track_b_discrete_optimization.src.qubo_ising import QUBOKnapsackSolver
from track_b_discrete_optimization.src.ilp_solver import ILPKnapsackSolver

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def run_penalty_study() -> Dict[str, Any]:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print("Running Track B QUBO Penalty Sensitivity Study...")

    # Define a clean 4-item problem with capacity W = 9
    # Items:
    # 0: v=30, w=3
    # 1: v=45, w=4
    # 2: v=40, w=4
    # 3: v=55, w=6
    # Max value = 55. Capacity = 9.
    # Feasible optimal: {1, 2} -> w=8, v=85, or {0, 3} -> w=9, v=85
    values = np.array([30.0, 45.0, 40.0, 55.0])
    weights = np.array([3.0, 4.0, 4.0, 6.0])
    capacity = 9.0
    problem = KnapsackProblem(values, weights, capacity, name="QUBOPenaltyInstance")

    ilp = ILPKnapsackSolver()
    sol_ilp = ilp.solve(problem)
    true_opt_value = sol_ilp.total_value

    alpha_factors = [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0, 1.25, 1.5, 2.0, 3.0, 5.0]
    results = []
    csv_rows = []

    for alpha in alpha_factors:
        solver = QUBOKnapsackSolver(penalty_multiplier=alpha)
        Q, const_offset, slacks, P = solver.build_qubo_matrix(problem)
        N_vars = Q.shape[0]
        total_states = 1 << N_vars

        best_energy = float("inf")
        best_z = None
        infeasible_count = 0

        for state_int in range(total_states):
            z = np.array([(state_int >> bit) & 1 for bit in range(N_vars)], dtype=np.float64)
            energy = solver.evaluate_qubo_energy(Q, const_offset, z)

            # Check if this state's item assignment is feasible
            x = z[:problem.n_items]
            val, w, feas = problem.evaluate(x)
            if not feas:
                infeasible_count += 1

            if energy < best_energy:
                best_energy = energy
                best_z = z

        # Analyze ground state
        x_opt = best_z[:problem.n_items]
        val, w, feas = problem.evaluate(x_opt)
        violation = max(0.0, w - capacity)

        record = {
            "alpha": alpha,
            "penalty_P": round(P, 2),
            "is_feasible": bool(feas),
            "weight_violation": round(float(violation), 2),
            "decoded_value": round(float(val), 2),
            "decoded_weight": round(float(w), 2),
            "capacity": capacity,
            "true_optimal_value": true_opt_value,
            "matches_optimal": bool(feas and abs(val - true_opt_value) < 1e-4),
            "ground_state_energy": round(float(best_energy), 4)
        }
        results.append(record)
        csv_rows.append(record)
        status_str = "FEASIBLE (OPTIMAL)" if record["matches_optimal"] else ("VIOLATION" if not feas else "SUBOPTIMAL")
        print(f"  alpha={alpha:4.2f} (P={P:6.2f}) | W={w:4.1f}/{capacity} | Feasible={feas} | Decoded Val={val:5.1f} | {status_str}")

    # Save output
    json_path = os.path.join(RESULTS_DIR, "qubo_penalty_study_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"instance": problem.name, "results": results}, f, indent=2)

    csv_path = os.path.join(RESULTS_DIR, "qubo_penalty_study_summary.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("Alpha,PenaltyP,IsFeasible,WeightViolation,DecodedValue,DecodedWeight,Capacity,MatchesOptimal,GroundEnergy\n")
        for r in csv_rows:
            f.write(f'{r["alpha"]},{r["penalty_P"]},{r["is_feasible"]},{r["weight_violation"]},{r["decoded_value"]},{r["decoded_weight"]},{r["capacity"]},{r["matches_optimal"]},{r["ground_state_energy"]}\n')

    print(f"Penalty study completed:\n  JSON: {json_path}\n  CSV:  {csv_path}")
    return {"results": results}


if __name__ == "__main__":
    run_penalty_study()

