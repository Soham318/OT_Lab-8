"""
Synthetic Workflow Dataset Generator
Track J: Real-World Codebase Optimization

Generates realistic Directed Acyclic Graphs (DAGs) representing:
  - Multi-stage ETL data warehousing pipelines (Ingest -> Clean -> Join -> Aggregate -> Export)
  - Distributed machine learning pipelines (Feature Extract -> Partition -> Train -> Evaluate)
  - Microservice asynchronous call graphs

Produces reproducible benchmark instances across 4 standard scales:
  - Small: 50 tasks
  - Medium: 250 tasks
  - Large: 1,000 tasks
  - Extra Large: 2,500 tasks
"""

import os
import random
from typing import Dict, List, Optional
from track_j_real_world_optimization.src.workflow_models import Task, ResourceCluster
from track_j_real_world_optimization.src.dag_parser import WorkflowDAG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def generate_layered_workflow_dag(
    num_tasks: int = 250,
    num_layers: Optional[int] = None,
    edge_density: float = 0.25,
    seed: int = 42,
    name: str = "SyntheticWorkflow"
) -> WorkflowDAG:
    """
    Generate a layered DAG representing an enterprise workflow pipeline.
    Layering ensures acyclicity while providing controllable fan-out and fan-in topology.
    """
    rng = random.Random(seed)
    dag = WorkflowDAG(name=f"{name}_{num_tasks}t")

    if num_layers is None:
        # Heuristic: roughly sqrt(N) to 2*sqrt(N) layers
        num_layers = max(3, int(num_tasks ** 0.5 * 1.5))

    # Distribute tasks across layers
    tasks_per_layer = [1] * num_layers
    remaining = num_tasks - num_layers

    # Add random distribution with peak in middle layers
    weights = [min(l + 1, num_layers - l) for l in range(num_layers)]
    weight_sum = sum(weights)

    for l in range(num_layers):
        share = int(remaining * (weights[l] / weight_sum))
        tasks_per_layer[l] += share

    # Distribute any leftover tasks
    current_total = sum(tasks_per_layer)
    for l in range(num_tasks - current_total):
        tasks_per_layer[l % num_layers] += 1

    # Create task nodes layer by layer
    current_task_id = 1
    layer_task_ids: List[List[int]] = []

    for l in range(num_layers):
        layer_ids = []
        for _ in range(tasks_per_layer[l]):
            t_id = current_task_id
            current_task_id += 1
            # Task duration between 2.0 and 45.0 seconds
            dur = round(rng.uniform(2.0, 45.0), 2)
            cpus = rng.choice([1, 2, 4])
            mem = rng.choice([256.0, 512.0, 1024.0, 2048.0])
            prio = rng.randint(1, 10)
            t_name = f"Task_L{l:02d}_{t_id:04d}"

            task = Task(
                task_id=t_id,
                name=t_name,
                duration=dur,
                cpu_demand=cpus,
                memory_demand_mb=mem,
                priority=prio,
                dependencies=[]
            )
            dag.add_task(task)
            layer_ids.append(t_id)
        layer_task_ids.append(layer_ids)

    # Connect edges strictly from earlier layers to later layers (guaranteeing acyclicity)
    for l in range(num_layers - 1):
        cur_layer = layer_task_ids[l]
        next_layer = layer_task_ids[l + 1]

        # 1. Guarantee connectivity: every task in next_layer gets at least one parent in cur_layer
        for child_id in next_layer:
            parent_id = rng.choice(cur_layer)
            dag.add_dependency(parent_id, child_id)
            dag.tasks[child_id].dependencies.append(parent_id)

        # 2. Add cross-layer edges based on edge_density
        for parent_id in cur_layer:
            for child_id in next_layer:
                if child_id not in dag.children.get(parent_id, []):
                    if rng.random() < edge_density:
                        dag.add_dependency(parent_id, child_id)
                        dag.tasks[child_id].dependencies.append(parent_id)

        # 3. Occasional skip-layer connections (fan-out spanning 2 layers)
        if l + 2 < num_layers:
            skip_layer = layer_task_ids[l + 2]
            for parent_id in cur_layer:
                for child_id in skip_layer:
                    if rng.random() < (edge_density * 0.15):
                        dag.add_dependency(parent_id, child_id)
                        dag.tasks[child_id].dependencies.append(parent_id)

    # Sort dependencies for determinism
    for t in dag.tasks.values():
        t.dependencies = sorted(list(set(t.dependencies)))

    return dag

def generate_standard_benchmark_datasets() -> Dict[str, str]:
    """Generate and persist the 4 benchmark workflow instances."""
    configs = [
        ("small", 50, 6, 0.30),
        ("medium", 250, 15, 0.25),
        ("large", 1000, 30, 0.15),
        ("xlarge", 2500, 45, 0.10)
    ]
    saved_files = {}
    print("--- Generating Benchmark Workflow Datasets ---")
    for label, count, layers, density in configs:
        dag = generate_layered_workflow_dag(
            num_tasks=count, num_layers=layers, edge_density=density, seed=42, name=label
        )
        filepath = os.path.join(DATA_DIR, f"workflow_{label}.json")
        dag.to_json_file(filepath)
        saved_files[label] = filepath
        print(f"  [{label.upper():<6}] Tasks: {dag.num_tasks:5d} | Edges: {dag.num_edges:6d} -> {filepath}")

    return saved_files

if __name__ == "__main__":
    generate_standard_benchmark_datasets()
