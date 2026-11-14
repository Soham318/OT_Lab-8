"""
Greedy Index Selection Algorithm for Railway Reservation DBMS.
Ranks candidate indexes by marginal benefit per unit storage cost,
re-evaluating marginal gains at each step to prevent double-counting.
"""

def compute_workload_benefit(selected_index_ids, candidate_indexes, queries):
    """
    Compute total weighted workload benefit for a given set of selected indexes.
    Prevents double-counting: each query achieves max benefit among available applicable indexes.
    """
    index_map = {idx["id"]: idx for idx in candidate_indexes}
    total_weighted_benefit = 0.0

    for q in queries:
        q_id = q["id"]
        w = q["weight"]
        # Find best applicable benefit among selected indexes
        max_b = 0.0
        for idx_id in selected_index_ids:
            idx = index_map[idx_id]
            if q_id in idx["applicable_queries"]:
                b = idx["base_benefits_ms"].get(q_id, 0.0)
                if b > max_b:
                    max_b = b
        total_weighted_benefit += w * max_b

    return total_weighted_benefit

def run_greedy_index_selection(candidate_indexes, queries, storage_budget_mb):
    """
    Greedy heuristic for index selection under a storage budget constraint.
    Iteratively selects candidate with highest marginal benefit-to-cost ratio.
    """
    index_map = {idx["id"]: idx for idx in candidate_indexes}
    selected = set()
    current_storage = 0.0
    selection_history = []

    available = set(index_map.keys())

    while available:
        best_candidate = None
        best_ratio = -1.0
        best_marginal_gain = 0.0
        best_cost = 0.0

        current_benefit = compute_workload_benefit(selected, candidate_indexes, queries)

        for cand_id in list(available):
            cand = index_map[cand_id]
            cost = cand["storage_cost_mb"]

            # Feasibility check
            if current_storage + cost > storage_budget_mb:
                continue

            # Calculate marginal benefit
            trial_selected = selected | {cand_id}
            new_benefit = compute_workload_benefit(trial_selected, candidate_indexes, queries)
            marginal_gain = new_benefit - current_benefit

            if cost > 0:
                ratio = marginal_gain / cost
            else:
                ratio = 0.0

            if ratio > best_ratio:
                best_ratio = ratio
                best_candidate = cand_id
                best_marginal_gain = marginal_gain
                best_cost = cost

        # If no feasible candidate with positive gain exists, terminate
        if best_candidate is None or best_marginal_gain <= 0:
            break

        selected.add(best_candidate)
        available.remove(best_candidate)
        current_storage += best_cost

        step_record = {
            "step": len(selection_history) + 1,
            "selected_index": best_candidate,
            "index_name": index_map[best_candidate]["name"],
            "marginal_benefit": round(best_marginal_gain, 2),
            "storage_cost_mb": round(best_cost, 2),
            "ratio": round(best_ratio, 2),
            "cumulative_storage_mb": round(current_storage, 2),
            "cumulative_benefit": round(compute_workload_benefit(selected, candidate_indexes, queries), 2)
        }
        selection_history.append(step_record)

    total_benefit = compute_workload_benefit(selected, candidate_indexes, queries)

    return {
        "method": "Greedy",
        "selected_indexes": sorted(list(selected)),
        "selected_names": [index_map[i]["name"] for i in sorted(list(selected))],
        "total_storage_mb": round(current_storage, 2),
        "storage_budget_mb": storage_budget_mb,
        "total_benefit_score": round(total_benefit, 2),
        "steps": selection_history
    }

