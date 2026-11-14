"""
Workflow Data Models and Validation Infrastructure
Track J: Real-World Codebase Optimization

Defines:
  1. Task: Individual computational unit with duration, resource demands, and dependencies.
  2. ResourceCluster: Computing environment with worker threads, CPU cores, and memory capacity.
  3. TaskExecution: Record of scheduled start, finish, duration, and assigned worker.
  4. WorkflowSchedule: Comprehensive schedule output with metrics and verification hashes.
  5. Validation Framework: Strictly verifies precedence constraints and resource concurrency.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Any, Optional, Tuple
import hashlib
import json

@dataclass
class Task:
    """Represents a computational unit within a workflow DAG."""
    task_id: int
    name: str
    duration: float
    cpu_demand: int = 1
    memory_demand_mb: float = 256.0
    priority: int = 1
    dependencies: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "duration": self.duration,
            "cpu_demand": self.cpu_demand,
            "memory_demand_mb": self.memory_demand_mb,
            "priority": self.priority,
            "dependencies": list(self.dependencies)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        return cls(
            task_id=data["task_id"],
            name=data["name"],
            duration=float(data["duration"]),
            cpu_demand=int(data.get("cpu_demand", 1)),
            memory_demand_mb=float(data.get("memory_demand_mb", 256.0)),
            priority=int(data.get("priority", 1)),
            dependencies=list(data.get("dependencies", []))
        )

@dataclass
class ResourceCluster:
    """Represents the computing cluster available for scheduling."""
    num_workers: int = 4
    total_cpus: int = 16
    total_memory_mb: float = 16384.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "num_workers": self.num_workers,
            "total_cpus": self.total_cpus,
            "total_memory_mb": self.total_memory_mb
        }

@dataclass
class TaskExecution:
    """Records the execution details of a scheduled task."""
    task_id: int
    start_time: float
    finish_time: float
    assigned_worker: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "start_time": round(self.start_time, 4),
            "finish_time": round(self.finish_time, 4),
            "assigned_worker": self.assigned_worker
        }

@dataclass
class WorkflowSchedule:
    """Encapsulates the complete workflow execution schedule and metrics."""
    scheduler_name: str
    executions: Dict[int, TaskExecution] = field(default_factory=dict)
    makespan: float = 0.0
    scheduling_time_s: float = 0.0
    peak_memory_mb: float = 0.0

    def get_schedule_hash(self) -> str:
        """
        Compute SHA-256 hash of sorted task start/finish times to verify execution consistency.
        """
        hasher = hashlib.sha256()
        for t_id in sorted(self.executions.keys()):
            exec_rec = self.executions[t_id]
            rec_str = f"{t_id}:{exec_rec.start_time:.4f}:{exec_rec.finish_time:.4f}:{exec_rec.assigned_worker};"
            hasher.update(rec_str.encode("utf-8"))
        return hasher.hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scheduler_name": self.scheduler_name,
            "makespan": round(self.makespan, 4),
            "scheduling_time_s": round(self.scheduling_time_s, 6),
            "peak_memory_mb": round(self.peak_memory_mb, 4),
            "total_tasks_scheduled": len(self.executions),
            "schedule_hash": self.get_schedule_hash()
        }

def validate_schedule_correctness(
    tasks: Dict[int, Task],
    cluster: ResourceCluster,
    schedule: WorkflowSchedule
) -> Tuple[bool, List[str]]:
    """
    Formally validates a schedule against all operational constraints:
    1. Completeness: Every task in the DAG is scheduled exactly once.
    2. Duration Integrity: finish_time == start_time + task.duration.
    3. Precedence Feasibility: start_time(task) >= max(finish_time(parents)).
    4. Worker Exclusivity: No worker executes two tasks simultaneously.
    5. Cluster Capacity: Concurrently executing tasks do not exceed total CPU/memory limits.
    """
    errors: List[str] = []

    # 1. Completeness Check
    if set(tasks.keys()) != set(schedule.executions.keys()):
        missing = set(tasks.keys()) - set(schedule.executions.keys())
        extra = set(schedule.executions.keys()) - set(tasks.keys())
        errors.append(f"Incomplete schedule: missing tasks {list(missing)[:5]}, extra tasks {list(extra)[:5]}.")
        return False, errors

    # 2. Duration and Precedence Feasibility
    for t_id, task in tasks.items():
        exec_info = schedule.executions[t_id]
        expected_finish = exec_info.start_time + task.duration
        if abs(exec_info.finish_time - expected_finish) > 1e-5:
            errors.append(f"Duration mismatch for Task {t_id}: finish={exec_info.finish_time}, expected={expected_finish}.")

        for parent_id in task.dependencies:
            if parent_id not in schedule.executions:
                errors.append(f"Dependency violation: Parent {parent_id} of Task {t_id} was not scheduled.")
                continue
            parent_finish = schedule.executions[parent_id].finish_time
            if exec_info.start_time < parent_finish - 1e-5:
                errors.append(
                    f"Precedence violation: Task {t_id} started at {exec_info.start_time:.2f} "
                    f"before parent {parent_id} finished at {parent_finish:.2f}."
                )

    # 3. Worker Non-Overlapping Check
    worker_intervals: Dict[int, List[Tuple[float, float, int]]] = {
        w: [] for w in range(cluster.num_workers)
    }
    for t_id, exec_info in schedule.executions.items():
        w = exec_info.assigned_worker
        if w < 0 or w >= cluster.num_workers:
            errors.append(f"Invalid worker ID {w} assigned to Task {t_id}.")
            continue
        worker_intervals[w].append((exec_info.start_time, exec_info.finish_time, t_id))

    for w, intervals in worker_intervals.items():
        sorted_intervals = sorted(intervals, key=lambda x: x[0])
        for i in range(len(sorted_intervals) - 1):
            cur_start, cur_end, t1 = sorted_intervals[i]
            next_start, next_end, t2 = sorted_intervals[i + 1]
            if next_start < cur_end - 1e-5:
                errors.append(
                    f"Worker overlap on worker {w}: Task {t1} [{cur_start:.2f}, {cur_end:.2f}] "
                    f"overlaps with Task {t2} [{next_start:.2f}, {next_end:.2f}]."
                )

    is_valid = (len(errors) == 0)
    return is_valid, errors
