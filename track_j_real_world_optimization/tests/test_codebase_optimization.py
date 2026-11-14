"""
Unit and Integration Test Suite
Track J: Real-World Codebase Optimization

Covers 10 comprehensive test cases:
  1. Data model instantiation, validation, and JSON serialization.
  2. DAG representation, in/out-degree tracking, Kahn's topological sort.
  3. Cost analyzer forward/backward dynamic programming and critical path lower bounds.
  4. Naive baseline scheduler execution and schedule validity check.
  5. Chapter 6 Optimized DP scheduler execution and schedule validity check.
  6. Schedule correctness parity: all tasks executed, no resource collisions, precedence preserved.
  7. Performance speedup verification on 250 tasks (speedup > 10x).
  8. Theoretical lower bound adherence (makespan >= max(LB_CP, LB_res)).
  9. Edge-case topologies: single-node DAG, disconnected parallel tasks, linear pipeline.
  10. Cyclic graph error detection and graceful handling.
"""

import unittest
import time
from track_j_real_world_optimization.src.workflow_models import (
    Task, ResourceCluster, TaskExecution, WorkflowSchedule, validate_schedule_correctness
)
from track_j_real_world_optimization.src.dag_parser import WorkflowDAG
from track_j_real_world_optimization.src.cost_analyzer import WorkflowCostAnalyzer
from track_j_real_world_optimization.src.dataset_generator import generate_layered_workflow_dag
from track_j_real_world_optimization.src.baseline_scheduler import NaiveWorkflowScheduler
from track_j_real_world_optimization.src.optimized_scheduler import OptimizedWorkflowScheduler

class TestCodebaseOptimization(unittest.TestCase):
    """Test suite for Track J Real-World Workflow Scheduling and Optimization."""

    def setUp(self):
        self.cluster = ResourceCluster(num_workers=4, total_cpus=16, total_memory_mb=16384.0)

    def test_01_task_and_cluster_models(self):
        """Test task and cluster model instantiation, serialization, and round-trip parsing."""
        task = Task(
            task_id=1,
            name="ETL_Ingest",
            duration=12.5,
            cpu_demand=2,
            memory_demand_mb=1024.0,
            priority=5,
            dependencies=[10, 11]
        )
        task_dict = task.to_dict()
        reconstructed = Task.from_dict(task_dict)
        self.assertEqual(task.task_id, reconstructed.task_id)
        self.assertEqual(task.duration, reconstructed.duration)
        self.assertEqual(task.dependencies, reconstructed.dependencies)

        cluster_dict = self.cluster.to_dict()
        self.assertEqual(cluster_dict["num_workers"], 4)

    def test_02_dag_parser_topological_sort(self):
        """Test DAG structure, dependency addition, and Kahn's topological sort."""
        dag = WorkflowDAG(name="SimplePipeline")
        t1 = Task(1, "Stage1", 10.0, 1, 512.0, 1, [])
        t2 = Task(2, "Stage2_A", 15.0, 1, 512.0, 1, [1])
        t3 = Task(3, "Stage2_B", 20.0, 1, 512.0, 1, [1])
        t4 = Task(4, "Stage3", 5.0, 1, 512.0, 1, [2, 3])

        dag.add_task(t1)
        dag.add_task(t2)
        dag.add_task(t3)
        dag.add_task(t4)
        dag.add_dependency(1, 2)
        dag.add_dependency(1, 3)
        dag.add_dependency(2, 4)
        dag.add_dependency(3, 4)

        topo = dag.get_topological_order()
        self.assertEqual(len(topo), 4)
        self.assertEqual(topo[0], 1)
        self.assertEqual(topo[-1], 4)
        self.assertEqual(dag.get_in_degrees()[4], 2)

    def test_03_cost_analyzer_critical_path(self):
        """Test critical path calculation and theoretical lower bound computation."""
        dag = WorkflowDAG(name="CP_Test")
        # 1 (dur 10) -> 2 (dur 20) -> 4 (dur 10) => length 40
        # 1 (dur 10) -> 3 (dur 5)  -> 4 (dur 10) => length 25
        dag.add_task(Task(1, "T1", 10.0, 1, 512.0, 1, []))
        dag.add_task(Task(2, "T2", 20.0, 1, 512.0, 1, [1]))
        dag.add_task(Task(3, "T3", 5.0, 1, 512.0, 1, [1]))
        dag.add_task(Task(4, "T4", 10.0, 1, 512.0, 1, [2, 3]))
        dag.add_dependency(1, 2)
        dag.add_dependency(1, 3)
        dag.add_dependency(2, 4)
        dag.add_dependency(3, 4)

        analyzer = WorkflowCostAnalyzer(dag)
        bounds = analyzer.compute_critical_path_bounds()
        cp_bound = bounds["critical_path_length"]
        res_bound = bounds["total_work_units"] / self.cluster.num_workers

        self.assertAlmostEqual(cp_bound, 40.0, places=2)
        # Total work = 10 + 20 + 5 + 10 = 45. On 4 workers, res_bound = 45 / 4 = 11.25
        self.assertAlmostEqual(res_bound, 11.25, places=2)

    def test_04_baseline_scheduler_validity(self):
        """Test baseline scheduler execution and schedule validity check."""
        dag = generate_layered_workflow_dag(num_tasks=40, num_layers=5, edge_density=0.2, seed=123)
        scheduler = NaiveWorkflowScheduler(dag, self.cluster)
        schedule = scheduler.schedule()

        self.assertEqual(len(schedule.executions), 40)
        is_valid, errors = validate_schedule_correctness(dag.tasks, self.cluster, schedule)
        self.assertTrue(is_valid, f"Baseline schedule failed validation: {errors}")
        self.assertGreater(schedule.makespan, 0.0)

    def test_05_optimized_scheduler_validity(self):
        """Test Chapter 6 optimized DP scheduler execution and schedule validity."""
        dag = generate_layered_workflow_dag(num_tasks=100, num_layers=8, edge_density=0.2, seed=456)
        scheduler = OptimizedWorkflowScheduler(dag, self.cluster)
        schedule = scheduler.schedule()

        self.assertEqual(len(schedule.executions), 100)
        is_valid, errors = validate_schedule_correctness(dag.tasks, self.cluster, schedule)
        self.assertTrue(is_valid, f"Optimized schedule failed validation: {errors}")
        self.assertGreater(schedule.makespan, 0.0)

    def test_06_schedule_correctness_parity(self):
        """Verify that both schedulers satisfy 100% of constraints on the same workload."""
        dag = generate_layered_workflow_dag(num_tasks=60, num_layers=6, edge_density=0.25, seed=789)

        base_sched = NaiveWorkflowScheduler(dag, self.cluster).schedule()
        opt_sched = OptimizedWorkflowScheduler(dag, self.cluster).schedule()

        # Both must schedule exactly 60 tasks
        self.assertEqual(len(base_sched.executions), 60)
        self.assertEqual(len(opt_sched.executions), 60)

        # Both must pass all validation checks
        b_valid, b_err = validate_schedule_correctness(dag.tasks, self.cluster, base_sched)
        o_valid, o_err = validate_schedule_correctness(dag.tasks, self.cluster, opt_sched)

        self.assertTrue(b_valid, f"Baseline invalid: {b_err}")
        self.assertTrue(o_valid, f"Optimized invalid: {o_err}")

    def test_07_optimized_speedup(self):
        """Verify that Optimized scheduler delivers substantial speedup (> 10x) on 250 tasks."""
        dag = generate_layered_workflow_dag(num_tasks=250, num_layers=15, edge_density=0.25, seed=42)

        t0 = time.perf_counter()
        _ = NaiveWorkflowScheduler(dag, self.cluster).schedule()
        t_base = time.perf_counter() - t0

        t0 = time.perf_counter()
        _ = OptimizedWorkflowScheduler(dag, self.cluster).schedule()
        t_opt = time.perf_counter() - t0

        speedup = t_base / t_opt if t_opt > 0 else 1.0
        self.assertGreater(speedup, 10.0, f"Expected speedup > 10x, got {speedup:.2f}x")

    def test_08_critical_path_optimality_bound(self):
        """Verify that scheduled makespans never violate the theoretical lower bound."""
        dag = generate_layered_workflow_dag(num_tasks=50, num_layers=5, edge_density=0.3, seed=999)
        analyzer = WorkflowCostAnalyzer(dag)
        lb = analyzer.compute_theoretical_lower_bound(self.cluster)

        opt_sched = OptimizedWorkflowScheduler(dag, self.cluster).schedule()
        self.assertGreaterEqual(opt_sched.makespan + 1e-6, lb)

    def test_09_edge_cases(self):
        """Test corner cases: single task, disconnected tasks, linear chain."""
        # 1. Single task DAG
        dag1 = WorkflowDAG(name="SingleTask")
        dag1.add_task(Task(1, "Solo", 5.0, 1, 256.0, 1, []))
        s1 = OptimizedWorkflowScheduler(dag1, self.cluster).schedule()
        self.assertAlmostEqual(s1.makespan, 5.0, places=2)

        # 2. Fully disconnected tasks (embarrassingly parallel)
        dag2 = WorkflowDAG(name="Disconnected")
        for i in range(1, 9):
            dag2.add_task(Task(i, f"Indep_{i}", 10.0, 1, 256.0, 1, []))
        s2 = OptimizedWorkflowScheduler(dag2, self.cluster).schedule()
        # 8 tasks of duration 10 on 4 workers = 20.0 seconds
        self.assertAlmostEqual(s2.makespan, 20.0, places=2)

        # 3. Linear chain (strictly sequential)
        dag3 = WorkflowDAG(name="LinearChain")
        dag3.add_task(Task(1, "L1", 4.0, 1, 256.0, 1, []))
        dag3.add_task(Task(2, "L2", 6.0, 1, 256.0, 1, [1]))
        dag3.add_task(Task(3, "L3", 8.0, 1, 256.0, 1, [2]))
        dag3.add_dependency(1, 2)
        dag3.add_dependency(2, 3)
        s3 = OptimizedWorkflowScheduler(dag3, self.cluster).schedule()
        self.assertAlmostEqual(s3.makespan, 18.0, places=2)

    def test_10_cycle_rejection(self):
        """Test that cyclic graphs are detected and handled properly."""
        dag = WorkflowDAG(name="CyclicGraph")
        dag.add_task(Task(1, "C1", 5.0, 1, 256.0, 1, [2]))
        dag.add_task(Task(2, "C2", 5.0, 1, 256.0, 1, [1]))
        dag.add_dependency(1, 2)
        dag.add_dependency(2, 1)

        with self.assertRaises(ValueError):
            _ = dag.get_topological_order()

if __name__ == "__main__":
    unittest.main()
