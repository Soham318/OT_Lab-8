# Greedy Optimization Methodology: Railway Route and Transfer Selection

> **Track E**: Main Real-Process Case Study  
> **Course**: Optimization Techniques — Lab Assignment 8  
> **Document Version**: 1.0.0  

---

## 1. Overview & Architectural Motivation

In large-scale public transit systems, passengers and trip-planning applications require rapid query response times (typically $< 10$ milliseconds). Exact methods like branch-and-bound Integer Linear Programming (ILP) can be computationally expensive on dense multi-station networks.

The **Greedy Railway Route Optimizer** is a heuristic approach designed to find high-quality multi-objective itineraries quickly by making locally optimal decisions at each decision station.

---

## 2. Greedy Decision Mechanics

At each decision station $u$ reached at time $t_{\text{current}}$, having arrived via train service $S_{\text{in}}$, the greedy agent evaluates every immediately feasible outgoing timetable connection $c \in C_{\text{outgoing}}(u)$.

### 2.1 Step Feasibility & Transfer Logic
1. **Departure Window**:
   $$t_{\text{ready}} = \begin{cases} t_{\text{query}} & \text{if } u = s_{\text{orig}} \text{ (Initial departure)} \\ t_{\text{current}} & \text{if } \text{srv}(c) = S_{\text{in}} \text{ (Staying on same train)} \\ t_{\text{current}} + \Delta_{\text{min}}(u) & \text{if } \text{srv}(c) \neq S_{\text{in}} \text{ (Interchange transfer)} \end{cases}$$
2. **Cycle Prevention**: To prevent infinite looping or wasteful detours, candidate connections leading to stations already present in the active path history are pruned:
   $$c.\text{to\_station\_id} \notin \text{VisitedStations}$$
3. **Transfer Budget**: The cumulative number of transfers must not exceed $K_{\text{max}}$.

### 2.2 Local Evaluation Function
Each candidate connection $c$ is assigned a greedy score:
$$f(c) = \text{cost\_so\_far} + \Delta\text{cost}(c) + h(c.\text{to\_station\_id})$$

Where:
* $\Delta\text{cost}(c) = \alpha \cdot c.\text{duration\_min} + \beta \cdot \text{wait\_time}(c) + \gamma \cdot \delta_{\text{xfer}}(c)$
* $h(v)$ is an admissible Euclidean heuristic lower-bound estimate of the remaining travel time from station $v$ to destination $s_{\text{dest}}$:
  $$h(v) = \alpha \cdot \left(\frac{\text{HaversineDistance}(v, s_{\text{dest}})}{v_{\text{max\_speed}}}\right) \times 60$$
  With $v_{\text{max\_speed}} = 85.0\text{ km/h}$.

The algorithm selects the branch minimizing $f(c)$ and repeats until reaching the destination.

---

## 3. Why Greedy Does Not Guarantee Global Optimality

A fundamental principle in optimization theory is that **greedy choice properties do not hold on time-dependent discrete scheduling graphs**.

### 3.1 The Myopic Trap
Because train departures are discrete, a locally optimal connection that departs immediately or travels fast can arrive at an interchange station just minutes after a major connecting express has left, forcing the passenger to endure an extensive platform wait (e.g. 100+ minutes).

Conversely, an exact global method (such as ILP) will willingly choose a train departing later from the origin or traveling at a slightly slower speed if it synchronizes with a downstream express connection.

### 3.2 Concrete Counterexample Proof
Consider the 3-station network verified in `test_07_greedy_failure_on_known_counterexample`:
* **Station A $\to$ Station B $\to$ Station C** (Transfer buffer at B: 10 minutes).
* **Option 1 (Greedy Choice)**:
  * Leg 1 departs A at 10:00, arrives B at 10:20 (duration: 20 min). Locally appears optimal!
  * Next train from B to C does not depart until 12:00 (100 min wait!).
  * Total Journey Time: **150 minutes**.
* **Option 2 (Globally Optimal ILP Choice)**:
  * Leg 1 departs A at 10:30, arrives B at 10:55 (duration: 25 min).
  * Leg 2 departs B at 11:10 (buffer: 15 min $\ge 10$ min, wait: 15 min), arrives C at 11:40.
  * Total Journey Time: **70 minutes** (Over 50% faster!).

Greedy is trapped by Option 1's earlier departure and faster first leg, whereas ILP evaluates the global schedule and identifies Option 2.

---

## 4. Empirical Performance Profile

From our 20-query benchmark:
* **Mean Execution Time**: **2.04 ms** (vs. 547 ms for ILP — over $250\times$ faster).
* **Average Optimality Gap**: **15.81%** against the proven global optimum.
* **Transfers Count**: 0.70 transfers per trip (significantly better than Dijkstra's 0.95 because Greedy penalizes transfers via $\gamma = 30$).

