# 20-Query Comparative Benchmark: Dijkstra vs. Greedy vs. Exact ILP

> **Multi-Objective Cost**: $Z = 1.0\cdot T_{\text{travel}} + 1.5\cdot T_{\text{wait}} + 30.0\cdot N_{\text{transfers}}$
> **Dataset**: 28 Stations, 551 Timetable Connections | **Repetitions**: 5 per query

## 1. Aggregate Performance Summary

| Performance Dimension | Dijkstra (Baseline) | Greedy Heuristic | Exact ILP (HiGHS) |
| :--- | :--- | :--- | :--- |
| **Optimality Guarantee** | Heuristic (Earliest Arr) | Heuristic (Greedy) | **Globally Proven Optimal** |
| **Mean Execution Latency** | **0.276 ms** | 2.044 ms | 547.285 ms |
| **Mean Journey Duration** | 273.9 min | 277.3 min | **246.9 min** |
| **Mean Waiting Time** | 56.0 min | 48.9 min | **30.9 min** |
| **Mean Transfers Count** | 0.95 | 0.70 | **0.60** |
| **Mean Composite Cost ($Z$)** | 323.9 | 315.2 | **273.1** |
| **Mean Optimality Gap** | 20.58% | 15.81% | **0.00% (Reference)** |
| **Proven Optimal Count** | 0 / 20 | 0 / 20 | **20 / 20 (100%)** |

## 2. Granular Query-by-Query Comparison

| ID | Query Scenario | OD Pair | Dep | Dijk Dur (Z) | Greedy Dur (Z) | ILP Dur (Z) | Greedy Gap | Dijk Gap | ILP Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Q01 | Mainline Short Hub | STN_01 -> STN_04 | 06:00 | 56m (56) | 56m (56) | **56m (56)** | 0.0% | 0.0% | 262.5 ms |
| Q02 | Mainline Mid City | STN_01 -> STN_06 | 06:00 | 132m (127) | 132m (127) | **132m (127)** | 0.0% | 0.0% | 370.7 ms |
| Q03 | Mainline Full Express | STN_01 -> STN_10 | 06:00 | 323m (303) | 323m (303) | **323m (303)** | 0.0% | 0.0% | 364.1 ms |
| Q04 | Mainline Reverse Mid | STN_08 -> STN_03 | 08:00 | 324m (460) | 324m (312) | **324m (312)** | 0.0% | 47.3% | 378.7 ms |
| Q05 | Coast to Metro Hub | STN_11 -> STN_06 | 06:00 | 233m (271) | 173m (165) | **173m (165)** | 0.0% | 64.2% | 313.7 ms |
| Q06 | Coast to River Jct | STN_12 -> STN_04 | 07:00 | 154m (148) | 154m (148) | **154m (148)** | 0.0% | 0.0% | 214.8 ms |
| Q07 | Oceanview to Highland | STN_13 -> STN_07 | 08:00 | 176m (214) | 176m (214) | **176m (214)** | 0.0% | 0.0% | 344.1 ms |
| Q08 | Dune to South Central | STN_14 -> STN_01 | 09:00 | 187m (254) | 187m (254) | **187m (254)** | 0.0% | 0.0% | 229.4 ms |
| Q09 | Eastport to Metro | STN_15 -> STN_06 | 06:30 | 166m (160) | 166m (160) | **166m (160)** | 0.0% | 0.0% | 173.6 ms |
| Q10 | Eastport to Highland | STN_15 -> STN_07 | 06:30 | 270m (324) | 270m (324) | **241m (280)** | 15.9% | 15.9% | 486.3 ms |
| Q11 | Coalfields to River Jct | STN_18 -> STN_04 | 09:00 | 382m (514) | 382m (514) | **382m (514)** | 0.0% | 0.0% | 142.3 ms |
| Q12 | Powergate to South Central | STN_19 -> STN_01 | 10:00 | 505m (638) | 473m (605) | **480m (526)** | 15.1% | 21.5% | 119.1 ms |
| Q13 | Lakeside to River Jct | STN_20 -> STN_04 | 06:00 | 291m (350) | 291m (350) | **146m (194)** | 80.9% | 80.9% | 709.4 ms |
| Q14 | Forest Edge to Metro | STN_21 -> STN_06 | 07:00 | 232m (220) | 232m (220) | **121m (116)** | 89.7% | 89.7% | 1174.7 ms |
| Q15 | Greenfield to Highland | STN_24 -> STN_07 | 08:00 | 83m (78) | 83m (78) | **83m (78)** | 0.0% | 0.0% | 1103.3 ms |
| Q16 | Delta Marsh to Alpine | STN_25 -> STN_10 | 06:00 | 402m (522) | 402m (522) | **291m (337)** | 55.0% | 55.0% | 2189.2 ms |
| Q17 | Highland to Canyon Pass | STN_07 -> STN_28 | 07:00 | 276m (270) | 276m (270) | **276m (270)** | 0.0% | 0.0% | 969.0 ms |
| Q18 | Coast to Mountain Spur | STN_12 -> STN_28 | 06:00 | 656m (823) | 776m (890) | **656m (752)** | 18.3% | 9.4% | 858.0 ms |
| Q19 | Midland Inter-Corridor | STN_11 -> STN_05 | 11:00 | 339m (415) | 378m (459) | **279m (325)** | 41.2% | 27.7% | 429.7 ms |
| Q20 | Evening Peak Trunk | STN_01 -> STN_08 | 17:00 | 292m (331) | 292m (331) | **292m (331)** | 0.0% | 0.0% | 113.2 ms |
