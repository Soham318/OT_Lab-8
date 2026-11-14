"""
Exact Binary Integer Linear Programming (ILP) Index Selection for Railway Reservation DBMS.
Solves the discrete index selection problem using SciPy's HiGHS MILP solver and
validates results against exhaustive combinatorial enumeration.
"""

import itertools
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from track_h_dbms_optimization.src.greedy_selector import compute_workload_benefit

def solve_ilp_index_selection(candidate_indexes, queries, storage_budget_mb):
    """
    Formulate and solve Index Selection as a Binary ILP:
    Decision variables:
      x_i in {0, 1} for i in {0, ..., m-1}: whether candidate index i is created.
      z_{j, i} in {0, 1} for query j and applicable index i: whether query j uses index i.

    Objective:
      Maximize sum_{j} w_j * sum_{i in A(j)} B_{j, i} * z_{j, i}

    Constraints:
      1. sum_{i} C_i * x_i <= S_max (Storage budget)
      2. sum_{i in A(j)} z_{j, i} <= 1 for each query j (At most one dominant index per query)
      3. z_{j, i} <= x_i for each query j and applicable index i (Index must be built to be used)
      4. x_i in {0, 1}, z_{j, i} in {0, 1}
    """
    m = len(candidate_indexes)
    index_map = {idx["id"]: (k, idx) for k, idx in enumerate(candidate_indexes)}

    # Enumerate query-index pairs (j, i) where index i applies to query j
    pairs = []
    for q_idx, q in enumerate(queries):
        q_id = q["id"]
        for idx_k, idx in enumerate(candidate_indexes):
            if q_id in idx["applicable_queries"]:
                b = idx["base_benefits_ms"].get(q_id, 0.0)
                if b > 0:
                    pairs.append((q_idx, idx_k, q["weight"], b))

    p_count = len(pairs)
    total_vars = m + p_count

    # Objective: SciPy milp minimizes c^T * v, so negate for maximization
    c = np.zeros(total_vars)
    for p_idx, (q_idx, idx_k, w, b) in enumerate(pairs):
        var_idx = m + p_idx
        c[var_idx] = - (w * b) # Negated for minimization

    # Constraints:
    rows = []
    lhs = []
    rhs = []

    # 1. Storage budget: sum_{i=0}^{m-1} C_i * x_i <= S_max
    budget_row = np.zeros(total_vars)
    for i in range(m):
        budget_row[i] = candidate_indexes[i]["storage_cost_mb"]
    rows.append(budget_row)
    lhs.append(0.0)
    rhs.append(float(storage_budget_mb))

    # 2. Query assignment: sum_{i in A(j)} z_{j, i} <= 1 for each query j
    for q_idx, q in enumerate(queries):
        q_row = np.zeros(total_vars)
        has_pair = False
        for p_idx, (pq_idx, idx_k, w, b) in enumerate(pairs):
            if pq_idx == q_idx:
                q_row[m + p_idx] = 1.0
                has_pair = True
        if has_pair:
            rows.append(q_row)
            lhs.append(0.0)
            rhs.append(1.0)

    # 3. Usage coupling: z_{j, i} - x_i <= 0
    for p_idx, (q_idx, idx_k, w, b) in enumerate(pairs):
        c_row = np.zeros(total_vars)
        c_row[m + p_idx] = 1.0
        c_row[idx_k] = -1.0
        rows.append(c_row)
        lhs.append(-np.inf)
        rhs.append(0.0)

    A = np.array(rows)
    constraints = LinearConstraint(A, lhs, rhs)

    # Integrality: all variables are binary (1)
    integrality = np.ones(total_vars)
    bounds = Bounds(lb=np.zeros(total_vars), ub=np.ones(total_vars))

    res = milp(c=c, integrality=integrality, constraints=constraints, bounds=bounds)

    if not res.success:
        raise RuntimeError(f"MILP solver failed: {res.status} - {res.message}")

    solution_vars = np.round(res.x).astype(int)
    x_solution = solution_vars[:m]

    selected_ids = [candidate_indexes[i]["id"] for i in range(m) if x_solution[i] == 1]
    total_cost = sum(candidate_indexes[i]["storage_cost_mb"] for i in range(m) if x_solution[i] == 1)
    total_benefit = compute_workload_benefit(selected_ids, candidate_indexes, queries)

    return {
        "method": "Exact ILP (HiGHS)",
        "selected_indexes": sorted(selected_ids),
        "selected_names": [candidate_indexes[i]["name"] for i in range(m) if x_solution[i] == 1],
        "total_storage_mb": round(total_cost, 2),
        "storage_budget_mb": storage_budget_mb,
        "total_benefit_score": round(total_benefit, 2),
        "solver_status": res.message
    }

def solve_exhaustive_index_selection(candidate_indexes, queries, storage_budget_mb):
    """
    Exhaustively enumerate all 2^m subsets to determine the guaranteed global optimum.
    """
    m = len(candidate_indexes)
    all_ids = [idx["id"] for idx in candidate_indexes]
    cost_map = {idx["id"]: idx["storage_cost_mb"] for idx in candidate_indexes}
    name_map = {idx["id"]: idx["name"] for idx in candidate_indexes}

    best_subset = []
    best_benefit = -1.0
    best_cost = 0.0

    # Test all possible combinations
    for r in range(m + 1):
        for combo in itertools.combinations(all_ids, r):
            cost = sum(cost_map[i] for i in combo)
            if cost <= storage_budget_mb:
                benefit = compute_workload_benefit(combo, candidate_indexes, queries)
                if benefit > best_benefit:
                    best_benefit = benefit
                    best_subset = combo
                    best_cost = cost

    return {
        "method": "Exhaustive Combinatorial",
        "selected_indexes": sorted(list(best_subset)),
        "selected_names": [name_map[i] for i in sorted(list(best_subset))],
        "total_storage_mb": round(best_cost, 2),
        "storage_budget_mb": storage_budget_mb,
        "total_benefit_score": round(best_benefit, 2)
    }

