# Track B: Discrete Optimization Benchmark Report

> **Assignment 8**: Optimize Anything | **Track B**: Discrete & Combinatorial

### Benchmark Results Summary Table

| Instance | N | Solver | Total Value | Weight / Cap | Feasible | Optimality Gap (%) | Runtime (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GreedyCounterexample** | 3 | ILP (HiGHS) | 220.0 | 50 / 50 (100.0%) | Yes | 0.00% | 34.109 |
| **GreedyCounterexample** | 3 | Greedy Heuristic | 160.0 | 30 / 50 (60.0%) | Yes | 27.27% | 0.046 |
| **GreedyCounterexample** | 3 | Dynamic Programming | 220.0 | 50 / 50 (100.0%) | Yes | 0.00% | 0.174 |
| **GreedyCounterexample** | 3 | Branch-and-Bound | 220.0 | 50 / 50 (100.0%) | Yes | 0.00% | 0.228 |
| **GreedyCounterexample** | 3 | QUBO Exhaustive | 220.0 | 50 / 50 (100.0%) | Yes | 0.00% | 5.140 |
| **Bench_N5** | 5 | ILP (HiGHS) | 344.0 | 37 / 40 (92.5%) | Yes | 0.00% | 19.567 |
| **Bench_N5** | 5 | Greedy Heuristic | 344.0 | 37 / 40 (92.5%) | Yes | 0.00% | 0.032 |
| **Bench_N5** | 5 | Dynamic Programming | 344.0 | 37 / 40 (92.5%) | Yes | 0.00% | 0.214 |
| **Bench_N5** | 5 | Branch-and-Bound | 344.0 | 37 / 40 (92.5%) | Yes | 0.00% | 0.158 |
| **Bench_N5** | 5 | QUBO Exhaustive | 344.0 | 37 / 40 (92.5%) | Yes | 0.00% | 13.611 |
| **Bench_N10** | 10 | ILP (HiGHS) | 498.0 | 92 / 92 (100.0%) | Yes | 0.00% | 9.302 |
| **Bench_N10** | 10 | Greedy Heuristic | 492.0 | 83 / 92 (90.22%) | Yes | 1.21% | 0.027 |
| **Bench_N10** | 10 | Dynamic Programming | 498.0 | 92 / 92 (100.0%) | Yes | 0.00% | 0.487 |
| **Bench_N10** | 10 | Branch-and-Bound | 498.0 | 92 / 92 (100.0%) | Yes | 0.00% | 0.220 |
| **Bench_N15** | 15 | ILP (HiGHS) | 884.0 | 173 / 173 (100.0%) | Yes | 0.00% | 10.069 |
| **Bench_N15** | 15 | Greedy Heuristic | 850.0 | 160 / 173 (92.49%) | Yes | 3.85% | 0.045 |
| **Bench_N15** | 15 | Dynamic Programming | 884.0 | 173 / 173 (100.0%) | Yes | 0.00% | 1.937 |
| **Bench_N15** | 15 | Branch-and-Bound | 884.0 | 173 / 173 (100.0%) | Yes | 0.00% | 0.243 |
| **Bench_N20** | 20 | ILP (HiGHS) | 1252.0 | 220 / 226 (97.35%) | Yes | 0.00% | 56.762 |
| **Bench_N20** | 20 | Greedy Heuristic | 1224.0 | 207 / 226 (91.59%) | Yes | 2.24% | 0.058 |
| **Bench_N20** | 20 | Dynamic Programming | 1252.0 | 220 / 226 (97.35%) | Yes | 0.00% | 3.925 |
| **Bench_N20** | 20 | Branch-and-Bound | 1252.0 | 220 / 226 (97.35%) | Yes | 0.00% | 0.569 |
| **Bench_N30** | 30 | ILP (HiGHS) | 1813.0 | 308 / 310 (99.35%) | Yes | 0.00% | 69.651 |
| **Bench_N30** | 30 | Greedy Heuristic | 1810.0 | 310 / 310 (100.0%) | Yes | 0.17% | 0.097 |
| **Bench_N30** | 30 | Dynamic Programming | 1813.0 | 308 / 310 (99.35%) | Yes | 0.00% | 4.864 |
| **Bench_N30** | 30 | Branch-and-Bound | 1813.0 | 308 / 310 (99.35%) | Yes | 0.00% | 0.559 |
| **Bench_N50** | 50 | ILP (HiGHS) | 2994.0 | 457 / 457 (100.0%) | Yes | 0.00% | 16.020 |
| **Bench_N50** | 50 | Greedy Heuristic | 2994.0 | 457 / 457 (100.0%) | Yes | 0.00% | 0.077 |
| **Bench_N50** | 50 | Dynamic Programming | 2994.0 | 457 / 457 (100.0%) | Yes | 0.00% | 12.239 |
| **Bench_N50** | 50 | Branch-and-Bound | 2994.0 | 457 / 457 (100.0%) | Yes | 0.00% | 0.703 |
| **Bench_N100** | 100 | ILP (HiGHS) | 6165.0 | 1019 / 1019 (100.0%) | Yes | 0.00% | 96.816 |
| **Bench_N100** | 100 | Greedy Heuristic | 6157.0 | 1015 / 1019 (99.61%) | Yes | 0.13% | 0.310 |
| **Bench_N100** | 100 | Dynamic Programming | 6165.0 | 1019 / 1019 (100.0%) | Yes | 0.00% | 210.521 |
| **Bench_N200** | 200 | ILP (HiGHS) | 12182.0 | 2073 / 2073 (100.0%) | Yes | 0.00% | 484.170 |
| **Bench_N200** | 200 | Greedy Heuristic | 12164.0 | 2068 / 2073 (99.76%) | Yes | 0.15% | 0.595 |
| **Bench_N200** | 200 | Dynamic Programming | 12182.0 | 2073 / 2073 (100.0%) | Yes | 0.00% | 1055.897 |
