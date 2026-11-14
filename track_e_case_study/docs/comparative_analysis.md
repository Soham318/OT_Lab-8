# Comparative Analysis: Dijkstra Baseline vs. Greedy Heuristic vs. Exact ILP

> **Track E**: Main Real-Process Case Study  
> **Course**: Optimization Techniques — Lab Assignment 8  
> **Document Version**: 1.0.0  

---

## 1. Executive Performance Comparison

All three algorithms were evaluated over identical 28-station timetable data across 20 representative Origin-Destination (OD) queries with repeated runs for timing accuracy:

| Performance Metric | Time-Dependent Dijkstra (Baseline) | Greedy Railway Optimizer (Heuristic) | Exact ILP (HiGHS Solver) | Best Performer |
| :--- | :--- | :--- | :--- | :--- |
| **Optimized Objective** | Arrival Time Only ($\min T_{\text{arr}}$) | Step-wise Composite Score ($\min \text{score}$) | Multi-Objective Cost ($\min Z$) | Task-Dependent |
| **Optimality Guarantee** | Optimal for Arrival Time ($T_{\text{arr}}$) | Heuristic (Myopic Multi-Objective) | **Globally Proven Optimal for $Z$** | **ILP (for $Z$), Dijkstra (for $T_{\text{arr}}$)** |
| **Mean Execution Latency** | **0.276 ms** | 2.044 ms | 547.285 ms | **Dijkstra** (1980x vs ILP) |
| **Mean Journey Duration** | 273.9 min | 277.3 min | **246.9 min** | **ILP** (-27.0 min saving) |
| **Mean Transfer Waiting** | 56.0 min | 48.9 min | **30.9 min** | **ILP** (-25.1 min saving) |
| **Mean Number of Transfers**| 0.95 | 0.70 | **0.60** | **ILP** (-37% transfers) |
| **Mean Composite Cost ($Z$)**| 323.9 | 315.2 | **273.1** | **ILP** (-15.7% lower cost) |
| **Mean Multi-Obj Optimality Gap**| 20.58% (vs $Z^*$) | 15.81% (vs $Z^*$) | **0.00% (Reference)** | **ILP** |
| **Earliest-Arrival Optimality**| **100.0% (20 / 20)** | 75.0% (15 / 20) | **100.0% (20 / 20)** | **Dijkstra & ILP** |

---

## 2. Granular 20-Query Empirical Benchmark Data

| ID | Query Scenario | OD Pair | Dep | Dijk Dur (Z) | Greedy Dur (Z) | ILP Dur (Z) | Greedy Gap | Dijk Gap | ILP Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Q01** | Mainline Short Hub | STN_01 $\to$ STN_04 | 06:00 | 56m (56) | 56m (56) | **56m (56)** | 0.0% | 0.0% | 262.5 ms |
| **Q02** | Mainline Mid City | STN_01 $\to$ STN_06 | 06:00 | 132m (127) | 132m (127) | **132m (127)** | 0.0% | 0.0% | 370.7 ms |
| **Q03** | Mainline Full Express | STN_01 $\to$ STN_10 | 06:00 | 323m (303) | 323m (303) | **323m (303)** | 0.0% | 0.0% | 364.1 ms |
| **Q04** | Mainline Reverse Mid | STN_08 $\to$ STN_03 | 08:00 | 324m (460) | 324m (312) | **324m (312)** | 0.0% | 47.3% | 378.7 ms |
| **Q05** | Coast to Metro Hub | STN_11 $\to$ STN_06 | 06:00 | 233m (271) | 173m (165) | **173m (165)** | 0.0% | 64.2% | 313.7 ms |
| **Q06** | Coast to River Jct | STN_12 $\to$ STN_04 | 07:00 | 154m (148) | 154m (148) | **154m (148)** | 0.0% | 0.0% | 214.8 ms |
| **Q07** | Oceanview to Highland | STN_13 $\to$ STN_07 | 08:00 | 176m (214) | 176m (214) | **176m (214)** | 0.0% | 0.0% | 344.1 ms |
| **Q08** | Dune to South Central | STN_14 $\to$ STN_01 | 09:00 | 187m (254) | 187m (254) | **187m (254)** | 0.0% | 0.0% | 229.4 ms |
| **Q09** | Eastport to Metro | STN_15 $\to$ STN_06 | 06:30 | 166m (160) | 166m (160) | **166m (160)** | 0.0% | 0.0% | 173.6 ms |
| **Q10** | Eastport to Highland | STN_15 $\to$ STN_07 | 06:30 | 270m (324) | 270m (324) | **241m (280)** | 15.9% | 15.9% | 486.3 ms |
| **Q11** | Coalfields to River Jct| STN_18 $\to$ STN_04 | 09:00 | 382m (514) | 382m (514) | **382m (514)** | 0.0% | 0.0% | 142.3 ms |
| **Q12** | Powergate to South | STN_19 $\to$ STN_01 | 10:00 | 505m (638) | 473m (605) | **480m (526)** | 15.1% | 21.5% | 119.1 ms |
| **Q13** | Lakeside to River Jct | STN_20 $\to$ STN_04 | 06:00 | 291m (350) | 291m (350) | **146m (194)** | 80.9% | 80.9% | 709.4 ms |
| **Q14** | Forest Edge to Metro | STN_21 $\to$ STN_06 | 07:00 | 232m (220) | 232m (220) | **121m (116)** | 89.7% | 89.7% | 1174.7 ms |
| **Q15** | Greenfield to Highland| STN_24 $\to$ STN_07 | 08:00 | 83m (78) | 83m (78) | **83m (78)** | 0.0% | 0.0% | 1103.3 ms |
| **Q16** | Delta Marsh to Alpine | STN_25 $\to$ STN_10 | 06:00 | 402m (522) | 402m (522) | **291m (337)** | 55.0% | 55.0% | 2189.2 ms |
| **Q17** | Highland to Canyon Pass| STN_07 $\to$ STN_28 | 07:00 | 276m (270) | 276m (270) | **276m (270)** | 0.0% | 0.0% | 969.0 ms |
| **Q18** | Coast to Mountain Spur| STN_12 $\to$ STN_28 | 06:00 | 656m (823) | 776m (890) | **656m (752)** | 18.3% | 9.4% | 858.0 ms |
| **Q19** | Midland Inter-Corridor| STN_11 $\to$ STN_05 | 11:00 | 339m (415) | 378m (459) | **279m (325)** | 41.2% | 27.7% | 429.7 ms |
| **Q20** | Evening Peak Trunk | STN_01 $\to$ STN_08 | 17:00 | 292m (331) | 292m (331) | **292m (331)** | 0.0% | 0.0% | 113.2 ms |

---

## 3. In-Depth Engineering Insights & Trade-Offs

### 3.1 Objective Function Reconciliation: Earliest Arrival vs. Multi-Objective Cost
A vital distinction must be made between what Dijkstra optimizes versus what ILP optimizes:
- **Dijkstra Formulation**: Solves the Earliest Arrival Problem (EAP), minimizing solely the arrival timestamp:
  $$\min T_{\text{arr}} \quad \text{subject to } T_{\text{dep}} \ge T_{\text{query}}$$
  On this specific criterion, Dijkstra is **100% globally optimal** across all 20 benchmark queries (achieving the theoretical earliest arrival in every instance).
- **ILP Formulation**: Solves the multi-objective journey optimization problem, minimizing composite generalized cost:
  $$\min Z = \alpha \cdot \text{TravelTime} + \beta \cdot \text{WaitTime} + \gamma \cdot \text{Transfers}$$
- **Reconciliation of the Optimality Gap**: The reported 20.58% optimality gap reflects Dijkstra's performance evaluated against the multi-objective metric $Z$, NOT failure to find an early arrival. Because Dijkstra treats waiting time and platform transfers as zero cost so long as arrival is minimized, it aggressively boards the earliest departing train. On queries like Q05 (`STN_11` $\to$ `STN_06`), Dijkstra boards at 06:00, transfers at Dune Plains, and arrives at 09:53 ($Z = 271.0$). ILP discovers that departing at 07:00 on the direct express arrives at the *exact same minute* (09:53) with 0 transfers and 60 minutes less duration ($Z = 165.0$). Thus, Dijkstra is optimal for pure arrival time, but suboptimal for passenger comfort and journey efficiency.

### 3.2 The "Hurry Up and Wait" Phenomenon and Pathological Cases

### 3.2 Where Greedy Succeeds and Where It Fails
* **Simple Corridors**: On 10 out of 20 queries (Q01, Q02, Q03, Q05, Q06, Q07, Q08, Q09, Q11, Q15, Q17, Q20), Greedy achieves an optimality gap of **0.0%**, finding the exact same optimal path as ILP in only **2.0 ms**.
* **Complex Multi-Corridor Traps**: On queries crossing from the Southern Ring to the Mainline Trunk (e.g. Q13, Q14, Q16), Greedy makes a locally appealing hop onto an immediate regional branch, missing a cross-country express that departs slightly later. This produces optimality gaps up to **89.7%**.

---

## 4. Optimization Strategy Selection Framework

In accordance with Section 5 of the Assignment specification, the following strategy-selection matrix determines which optimization method to deploy in practice:

| Dimension / Context | Time-Dependent Dijkstra | Greedy Heuristic | Exact Binary ILP (HiGHS) |
| :--- | :--- | :--- | :--- |
| **Problem Formulation** | Single-objective shortest path | Multi-objective step evaluation | Multi-objective binary network flow |
| **Decision Variables** | Implicit node arrival labels | Local edge selection | Discrete binary $x_c, y_{c_1, c_2} \in \{0, 1\}$ |
| **Optimality Guarantee** | Optimal for Arrival Time only | Suboptimal heuristic | **Proven Globally Optimal** |
| **Execution Latency** | Ultra-low ($< 0.5$ ms) | Very low ($< 5$ ms) | Moderate ($100 - 2000$ ms) |
| **Scalability ($N$ Stations)**| Excellent ($\mathcal{O}(M \log N)$) | Excellent ($\mathcal{O}(B \cdot \text{deg})$) | Moderate (Branch-and-cut NP-hard bound) |
| **Best Production Use Case**| Real-time autocomplete / instant map search | Mobile app routing under tight latency budgets | Offline timetable master planning / high-value VIP journeys |

