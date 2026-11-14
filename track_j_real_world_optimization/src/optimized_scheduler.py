"""
Optimized Workflow Scheduler (Chapter 6 Optimization Paradigm)
Track J: Real-World Codebase Optimization

Optimization Techniques Employed:
  1. Dynamic Programming with Backward Memoization:
     Precomputes exact downstream Critical Path potentials V(i) in a single O(V + E) pass:
     V(i) = duration_i + max_{j in children(i)} V(j).
     Completely eliminates redundant recursive subgraph traversals.
  2. Incremental In-Degree Dependency Tracking:
     Maintains O(1) in-degree state. When task i finishes, decrements in-degree of its
     immediate children; child is immediately ready when in-degree reaches 0.
     Total dependency resolution over entire run is strictly O(V + E).
  3. Priority-Queue (Min-Heap) Event Scheduling:
     Stores ready tasks in a binary heap ordered by (-Priority, -CP_Potential, Task_ID).
     Task retrieval and insertion take O(log K) time.
  4. Worker Timeline Min-Heap:
     Retrieves earliest available worker in O(log W) time.
  5. Total Algorithmic Complexity:
     Reduced from O(V^3) down to O((V + E) log V).
"""

import heapq
import time
from typing import Dict, List, Set, Optional, Tuple
from track_j_real_world_optimization.src.workflow_models import (
    Task, ResourceCluster, TaskExecution, WorkflowSchedule
)
from track_j_real_world_optimization.src.dag_parser import WorkflowDAG

class OptimizedWorkflowScheduler:
    """
    High-performance event-driven workflow scheduler with DP critical-path memoization
    and O(1) incremental dependency resolution.
    """

    def __init__(self, dag: WorkflowDAG, cluster: ResourceCluster):
        self.dag = dag
        self.cluster = cluster
        self.executions: Dict[int, TaskExecution] = {}

    def _compute_memoized_critical_path_potentials(self) -> Dict[int, float]:
        """
        Chapter 6 Dynamic Programming (Backward Topological Memoization):
        Computes maximum downstream path length V(i) for all tasks in O(V + E).
        V(i) = duration(i) + max_{j in children(i)} V(j).
        """
        topo_order = self.dag.get_topological_order()
        dp_potentials: Dict[int, float] = {}

        # Backward topological evaluation
        for t_id in reversed(topo_order):
            task = self.dag.tasks[t_id]
            children = self.dag.children.get(t_id, [])
            if not children:
                dp_potentials[t_id] = task.duration
            else:
                max_child_path = max(dp_potentials[c] for c in children)
                dp_potentials[t_id] = task.duration + max_child_path

        return dp_potentials

    def schedule(self) -> WorkflowSchedule:
        """
        Executes the optimized scheduling pipeline:
        1. DP backward pass to compute critical path potentials.
        2. Initialize incremental in-degree counters.
        3. Maintain ready tasks in a binary max-priority heap.
        4. Maintain worker availability in a min-heap.
        """
        t_start = time.perf_counter()

        # Step 1: Precompute DP potentials in O(V + E)
        cp_potentials = self._compute_memoized_critical_path_potentials()

        # Step 2: Initialize in-degree counters
        in_degrees = self.dag.get_in_degrees()

        # Step 3: Priority queue for ready tasks
        # Heap elements: (-base_priority, -cp_potential, task_id)
        ready_heap: List[Tuple[float, float, int]] = []
        for t_id, deg in in_degrees.items():
            if deg == 0:
                prio = self.dag.tasks[t_id].priority
                cp = cp_potentials[t_id]
                heapq.heappush(ready_heap, (-prio, -cp, t_id))

        # Step 4: Worker min-heap tracking (worker_free_time, worker_id)
        worker_heap: List[Tuple[float, int]] = [
            (0.0, w) for w in range(self.cluster.num_workers)
        ]
        heapq.heapify(worker_heap)

        # Step 5: Event-driven execution loop
        parent_finish_cache: Dict[int, float] = {}

        while ready_heap:
            # Extract highest-priority ready task in O(log K)
            neg_prio, neg_cp, chosen_task_id = heapq.heappop(ready_heap)
            chosen_task = self.dag.tasks[chosen_task_id]

            # Extract earliest available worker in O(log W)
            worker_free_time, worker_id = heapq.heappop(worker_heap)

            # Determine earliest time parents are complete
            parents = chosen_task.dependencies
            if not parents:
                earliest_parent_ready = 0.0
            else:
                earliest_parent_ready = max(parent_finish_cache[p] for p in parents)

            actual_start = max(worker_free_time, earliest_parent_ready)
            actual_finish = actual_start + chosen_task.duration

            # Record execution
            exec_record = TaskExecution(
                task_id=chosen_task_id,
                start_time=actual_start,
                finish_time=actual_finish,
                assigned_worker=worker_id
            )
            self.executions[chosen_task_id] = exec_record
            parent_finish_cache[chosen_task_id] = actual_finish

            # Return worker to heap with updated availability
            heapq.heappush(worker_heap, (actual_finish, worker_id))

            # Incremental in-degree updates for children in O(deg(chosen_task))
            for child_id in self.dag.children.get(chosen_task_id, []):
                in_degrees[child_id] -= 1
                if in_degrees[child_id] == 0:
                    child_prio = self.dag.tasks[child_id].priority
                    child_cp = cp_potentials[child_id]
                    heapq.heappush(ready_heap, (-child_prio, -child_cp, child_id))

        t_elapsed = time.perf_counter() - t_start
        total_makespan = max(exec_rec.finish_time for exec_rec in self.executions.values()) if self.executions else 0.0

        return WorkflowSchedule(
            scheduler_name="OptimizedDPScheduler",
            executions=self.executions,
            makespan=total_makespan,
            scheduling_time_s=t_elapsed
        )
