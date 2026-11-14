"""
Critical Path and Workflow Cost Analyzer
Track J: Real-World Codebase Optimization

Calculates:
  1. Earliest Start Time (EST) and Earliest Finish Time (EFT) via forward topological DP.
  2. Latest Start Time (LST) and Latest Finish Time (LFT) via backward topological DP.
  3. Total Slack (LFT - EFT) and identifies Critical Path tasks (slack == 0).
  4. Theoretical makespan lower bounds:
     - LB_CP: Critical path duration lower bound (independent of worker count)
     - LB_RES: Total work / num_workers capacity lower bound
     - LB_MAX: max(LB_CP, LB_RES)
"""

from typing import Dict, List, Tuple, Any
from track_j_real_world_optimization.src.dag_parser import WorkflowDAG
from track_j_real_world_optimization.src.workflow_models import ResourceCluster

class WorkflowCostAnalyzer:
    """Computes critical paths, slacks, and makespan bounds on a WorkflowDAG."""

    def __init__(self, dag: WorkflowDAG):
        self.dag = dag
        self.topo_order = dag.get_topological_order()

    def compute_critical_path_bounds(self) -> Dict[str, Any]:
        """
        Forward topological DP to compute Earliest Finish Time (EFT)
        and find the maximum critical path length.
        """
        est: Dict[int, float] = {}
        eft: Dict[int, float] = {}

        for t_id in self.topo_order:
            task = self.dag.tasks[t_id]
            parents = self.dag.parents.get(t_id, [])
            if not parents:
                earliest = 0.0
            else:
                earliest = max(eft[p] for p in parents)
            est[t_id] = earliest
            eft[t_id] = earliest + task.duration

        critical_path_length = max(eft.values()) if eft else 0.0

        # Backward topological DP to compute Latest Start Time (LST)
        lft: Dict[int, float] = {}
        lst: Dict[int, float] = {}

        for t_id in reversed(self.topo_order):
            task = self.dag.tasks[t_id]
            children = self.dag.children.get(t_id, [])
            if not children:
                latest_finish = critical_path_length
            else:
                latest_finish = min(lst[c] for c in children)
            lft[t_id] = latest_finish
            lst[t_id] = latest_finish - task.duration

        # Compute slack and critical tasks
        slack: Dict[int, float] = {}
        critical_tasks: List[int] = []

        for t_id in self.dag.tasks:
            s = lft[t_id] - eft[t_id]
            slack[t_id] = round(max(0.0, s), 4)
            if slack[t_id] < 1e-4:
                critical_tasks.append(t_id)

        total_work = sum(t.duration for t in self.dag.tasks.values())

        return {
            "critical_path_length": round(critical_path_length, 4),
            "total_work_units": round(total_work, 4),
            "critical_tasks_count": len(critical_tasks),
            "critical_tasks": critical_tasks,
            "est": est,
            "eft": eft,
            "lst": lst,
            "lft": lft,
            "slack": slack
        }

    def compute_theoretical_lower_bound(self, cluster: ResourceCluster) -> float:
        """
        Compute theoretical makespan lower bound:
        LB = max( Critical_Path_Length, Total_Work / num_workers )
        """
        bounds = self.compute_critical_path_bounds()
        cp_len = bounds["critical_path_length"]
        total_work = bounds["total_work_units"]
        worker_bound = total_work / max(1, cluster.num_workers)
        return max(cp_len, worker_bound)
