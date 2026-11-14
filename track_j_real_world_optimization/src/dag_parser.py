"""
DAG Parser and Graph Representation Module
Track J: Real-World Codebase Optimization

Features:
  1. Adjacency list graph representation of computational workflow tasks.
  2. Cycle detection and topological ordering using Kahn's algorithm.
  3. Predecessor and successor indexing for fast dependency queries.
  4. DAG validation and serialization (to/from JSON).
"""

from typing import Dict, List, Set, Optional, Tuple, Any
import json
from track_j_real_world_optimization.src.workflow_models import Task

class WorkflowDAG:
    """Represents a Directed Acyclic Graph (DAG) of workflow tasks."""

    def __init__(self, name: str = "Workflow"):
        self.name = name
        self.tasks: Dict[int, Task] = {}
        self.children: Dict[int, List[int]] = {}  # parent -> children
        self.parents: Dict[int, List[int]] = {}   # child -> parents

    def add_task(self, task: Task) -> None:
        """Add a task to the DAG."""
        if task.task_id in self.tasks:
            raise ValueError(f"Task with ID {task.task_id} already exists in DAG.")
        self.tasks[task.task_id] = task
        if task.task_id not in self.children:
            self.children[task.task_id] = []
        if task.task_id not in self.parents:
            self.parents[task.task_id] = []

        # Connect dependencies
        for p_id in task.dependencies:
            self.add_dependency(p_id, task.task_id)

    def add_dependency(self, parent_id: int, child_id: int) -> None:
        """Add a directed edge parent_id -> child_id."""
        if parent_id not in self.children:
            self.children[parent_id] = []
        if child_id not in self.parents:
            self.parents[child_id] = []

        if child_id not in self.children[parent_id]:
            self.children[parent_id].append(child_id)
        if parent_id not in self.parents[child_id]:
            self.parents[child_id].append(parent_id)

    @property
    def num_tasks(self) -> int:
        return len(self.tasks)

    @property
    def num_edges(self) -> int:
        return sum(len(c) for c in self.children.values())

    def get_in_degrees(self) -> Dict[int, int]:
        """Compute the in-degree (number of immediate parents) for every task."""
        return {t_id: len(self.parents.get(t_id, [])) for t_id in self.tasks}

    def get_root_tasks(self) -> List[int]:
        """Return tasks with no incoming dependencies (in-degree 0)."""
        return [t_id for t_id, task in self.tasks.items() if len(self.parents.get(t_id, [])) == 0]

    def get_leaf_tasks(self) -> List[int]:
        """Return tasks with no outgoing dependencies (out-degree 0)."""
        return [t_id for t_id, task in self.tasks.items() if len(self.children.get(t_id, [])) == 0]

    def get_topological_order(self) -> List[int]:
        """
        Compute a valid topological sort using Kahn's algorithm.
        Raises ValueError if a cycle is detected.
        """
        in_degrees = self.get_in_degrees()
        ready_queue = [t_id for t_id, deg in in_degrees.items() if deg == 0]
        topo_order: List[int] = []

        while ready_queue:
            # Deterministic ordering by task_id
            ready_queue.sort()
            cur = ready_queue.pop(0)
            topo_order.append(cur)

            for child in self.children.get(cur, []):
                in_degrees[child] -= 1
                if in_degrees[child] == 0:
                    ready_queue.append(child)

        if len(topo_order) != len(self.tasks):
            raise ValueError(
                f"Cycle detected in WorkflowDAG '{self.name}'. "
                f"Only {len(topo_order)} of {len(self.tasks)} tasks could be sorted."
            )

        return topo_order

    def to_dict(self) -> Dict[str, Any]:
        """Serialize DAG to dictionary."""
        return {
            "name": self.name,
            "tasks": [task.to_dict() for task in self.tasks.values()]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowDAG":
        """Deserialize DAG from dictionary."""
        dag = cls(name=data.get("name", "Workflow"))
        for t_dict in data["tasks"]:
            task = Task.from_dict(t_dict)
            dag.add_task(task)
        return dag

    def to_json_file(self, filepath: str) -> None:
        """Write DAG to JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_json_file(cls, filepath: str) -> "WorkflowDAG":
        """Load DAG from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
