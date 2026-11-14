"""
Baseline Unoptimized Workflow Scheduler (Legacy Naive Implementation)
Track J: Real-World Codebase Optimization

Algorithmic Characteristics:
  - Naive greedy scheduling without incremental state tracking.
  - In each scheduling step, iterates over all unscheduled tasks.
  - Repeatedly performs recursive graph traversals to verify ancestor completion.
  - Dynamically recalculates remaining subtree work from scratch for every candidate.
  - High algorithmic complexity: O(V^2 * (V + E)) ~ O(V^3).
  - Demonstrates a severe computational bottleneck under cProfile profiling.
"""

import time
from typing import Dict, List, Set, Optional, Tuple
from track_j_real_world_optimization.src.workflow_models import (
    Task, ResourceCluster, TaskExecution, WorkflowSchedule
)
from track_j_real_world_optimization.src.dag_parser import WorkflowDAG

class NaiveWorkflowScheduler:
    """
    Naive baseline workflow scheduler with intentional computational bottlenecks:
    - O(V^3) total scheduling complexity due to repeated full-graph re-evaluations.
    """

    def __init__(self, dag: WorkflowDAG, cluster: ResourceCluster):
        self.dag = dag
        self.cluster = cluster
        self.unscheduled_tasks: Set[int] = set(dag.tasks.keys())
        self.completed_tasks: Set[int] = set()
        self.worker_available_time: List[float] = [0.0] * cluster.num_workers
        self.executions: Dict[int, TaskExecution] = {}

    def is_task_ready(self, task_id: int) -> bool:
        """
        BOTTLENECK 1: Naively checks dependency readiness by traversing all
        dependencies and recursively checking ancestor sets repeatedly from scratch.
        """
        task = self.dag.tasks[task_id]
        # Linear scan over task dependencies
        for p_id in task.dependencies:
            if p_id not in self.completed_tasks:
                return False

        # Additional redundant ancestor validation check common in unoptimized code
        ancestors = self._collect_all_ancestors(task_id)
        for a_id in ancestors:
            if a_id not in self.completed_tasks:
                return False
        return True

    def _collect_all_ancestors(self, task_id: int) -> Set[int]:
        """Recursive graph traversal to gather all ancestors."""
        ancestors: Set[int] = set()
        stack = list(self.dag.parents.get(task_id, []))
        while stack:
            cur = stack.pop()
            if cur not in ancestors:
                ancestors.add(cur)
                stack.extend(self.dag.parents.get(cur, []))
        return ancestors

    def compute_dynamic_priority(self, task_id: int) -> float:
        """
        BOTTLENECK 2: Naively computes task priority by recursively traversing
        the entire forward subgraph to calculate total downstream subtree work.
        Executed repeatedly for every ready task in every scheduling cycle!
        """
        descendants = self._collect_all_descendants(task_id)
        subtree_work = sum(self.dag.tasks[d_id].duration for d_id in descendants)
        base_priority = self.dag.tasks[task_id].priority
        return float(base_priority * 1000.0 + subtree_work)

    def _collect_all_descendants(self, task_id: int) -> Set[int]:
        """Recursive graph traversal to gather all descendants."""
        descendants: Set[int] = set()
        stack = list(self.dag.children.get(task_id, []))
        while stack:
            cur = stack.pop()
            if cur not in descendants:
                descendants.add(cur)
                stack.extend(self.dag.children.get(cur, []))
        return descendants

    def find_earliest_worker(self) -> Tuple[int, float]:
        """Linear scan across workers to find earliest available worker slot."""
        earliest_time = float("inf")
        best_worker = 0
        for w in range(self.cluster.num_workers):
            if self.worker_available_time[w] < earliest_time:
                earliest_time = self.worker_available_time[w]
                best_worker = w
        return best_worker, earliest_time

    def schedule(self) -> WorkflowSchedule:
        """
        Main execution loop for naive scheduler.
        Repeatedly scans unscheduled set, checks readiness, sorts by dynamic priority,
        and assigns to the earliest available worker.
        """
        t_start = time.perf_counter()

        while self.unscheduled_tasks:
            # 1. Scan ALL unscheduled tasks to find ready candidates
            ready_candidates: List[int] = []
            for t_id in list(self.unscheduled_tasks):
                if self.is_task_ready(t_id):
                    ready_candidates.append(t_id)

            if not ready_candidates:
                raise RuntimeError(
                    f"Deadlock detected in NaiveScheduler: {len(self.unscheduled_tasks)} "
                    f"tasks remain unscheduled but none are ready."
                )

            # 2. Sort ready candidates by expensive dynamic subtree priority
            ready_candidates.sort(
                key=lambda tid: (self.compute_dynamic_priority(tid), -tid),
                reverse=True
            )

            # 3. Pick highest priority task
            chosen_task_id = ready_candidates[0]
            chosen_task = self.dag.tasks[chosen_task_id]

            # 4. Find earliest available worker
            worker_id, worker_free_time = self.find_earliest_worker()

            # 5. Compute actual start time (must be >= worker free time AND >= max parent finish)
            parent_finishes = [
                self.executions[p_id].finish_time for p_id in chosen_task.dependencies
            ]
            earliest_parent_ready = max(parent_finishes) if parent_finishes else 0.0
            actual_start = max(worker_free_time, earliest_parent_ready)
            actual_finish = actual_start + chosen_task.duration

            # 6. Record execution and update state
            exec_record = TaskExecution(
                task_id=chosen_task_id,
                start_time=actual_start,
                finish_time=actual_finish,
                assigned_worker=worker_id
            )
            self.executions[chosen_task_id] = exec_record
            self.worker_available_time[worker_id] = actual_finish

            self.unscheduled_tasks.remove(chosen_task_id)
            self.completed_tasks.add(chosen_task_id)

        t_elapsed = time.perf_counter() - t_start
        total_makespan = max(exec_rec.finish_time for exec_rec in self.executions.values()) if self.executions else 0.0

        return WorkflowSchedule(
            scheduler_name="NaiveBaselineScheduler",
            executions=self.executions,
            makespan=total_makespan,
            scheduling_time_s=t_elapsed
        )
