# Track E Viva Preparation & Theoretical Defense Guide

> **Course**: Optimization Techniques — Lab Assignment 8  
> **Topic**: Railway Route and Transfer Optimization (Track E Case Study)  
> **Scope**: 16 Core Theoretical & Experimental Defense Questions with Model Answers  

---

### Q1: Why is ordinary static Dijkstra unsuitable for scheduled railway networks?
**Answer**:  
Standard Dijkstra assumes static edge weights $w(u, v)$ that represent a fixed scalar cost (distance or fixed duration). In scheduled public transit, edge traversal costs are intrinsically **time-dependent step functions**:
$$c(u, v, t) = \min \big\{\text{arr}(c) - t \mid c \in C_{u \to v}, \, \text{dep}(c) \ge t + \Delta(u)\big\}$$
Applying static Dijkstra with minimum link runtimes assumes instantaneous "teleportation" connections without platform waiting and completely fails to enforce station-specific transfer buffers $\Delta_{\text{min}}(s)$, underestimating real travel times by 30% to 65%.

---

### Q2: What is the FIFO property, and why does it guarantee that Time-Dependent Dijkstra finds the earliest arrival time?
**Answer**:  
The FIFO (First-In, First-Out) or non-overtaking property asserts that for any edge $(u, v)$ and departure times $t_1 \le t_2$:
$$t_1 + c(u, v, t_1) \le t_2 + c(u, v, t_2)$$
On physical railway segments between adjacent stations, trains cannot overtake each other. Because the arrival time function is monotonically non-decreasing with respect to departure time, subpaths of optimal paths remain optimal, satisfying Bellman's principle of optimality and guaranteeing that greedy label-setting finds the exact earliest arrival time in polynomial time $\mathcal{O}(|C| \log |S|)$.

---

### Q3: Why does Earliest-Arrival Dijkstra fail to optimize a composite multi-objective function?
**Answer**:  
Earliest-Arrival Dijkstra has a single-minded objective: minimize the arrival timestamp at the destination $t_{\text{dest}}$. It is completely indifferent to when the traveler departs or how many transfers they endure. Consequently, it often boards the very first departing slow train, transfers multiple times, and arrives at the destination at the exact same minute that a direct express train departing 1 hour later would have arrived. Under a multi-objective cost function that penalizes in-vehicle duration, waiting time, and transfer counts, Dijkstra suffers an average optimality gap of 20.58%.

---

### Q4: How is the railway routing problem formulated as a Binary Integer Linear Program (ILP)?
**Answer**:  
The problem is modeled over a time-expanded network using two classes of binary decision variables:
1. $x_c \in \{0, 1\}$ for each candidate timetable connection leg $c \in C_{\text{cand}}$.
2. $y_{c_1, c_2} \in \{0, 1\}$ for each feasible transition/transfer $(c_1, c_2) \in T_{\text{cand}}$ where $c_1.\text{to} = c_2.\text{from}$ and $c_2.\text{dep} \ge c_1.\text{arr} + \Delta_{\text{min}}$.

The objective minimizes total composite cost:
$$\min Z = \alpha \sum \tau(c) x_c + \beta \sum w(c_1, c_2) y_{c_1, c_2} + \gamma \sum \delta_{\text{xfer}}(c_1, c_2) y_{c_1, c_2}$$
Subject to flow conservation, origin departure balance, destination arrival balance, and transfer bounds.

---

### Q5: How do the flow conservation constraints link connections $x_c$ with transfers $y_{c_1, c_2}$?
**Answer**:  
For every intermediate connection $c$ traversed ($x_c = 1$):
* **Forward Linking**: It must transition to exactly one outgoing connection $c_2$:
  $$\sum_{c_2: (c, c_2) \in T} y_{c, c_2} = x_c \quad (\forall c \text{ with } c.\text{to} \neq s_{\text{dest}})$$
* **Backward Linking**: It must be preceded by exactly one incoming connection $c_1$:
  $$\sum_{c_1: (c_1, c) \in T} y_{c_1, c} = x_c \quad (\forall c \text{ with } c.\text{from} \neq s_{\text{orig}})$$
These constraints ensure the active variables form a single contiguous, unbroken path from origin to destination.

---

### Q6: How does the ILP enforce minimum transfer buffers $\Delta_{\text{min}}$ without non-linear constraints?
**Answer**:  
Instead of using non-linear constraints or big-$M$ formulations, transfer buffers are enforced **a priori during graph construction**. A transition variable $y_{c_1, c_2}$ is only instantiated in the model if:
$$c_2.\text{dep} - c_1.\text{arr} \ge \Delta_{\text{min}}(c_1.\text{to})$$
Any transition violating the station buffer is omitted from the index set $T_{\text{cand}}$, rendering it mathematically impossible for the solver to select an invalid connection.

---

### Q7: Why is the exact ILP computationally slower than Dijkstra and Greedy?
**Answer**:  
Time-Dependent Dijkstra has polynomial complexity $\mathcal{O}(|C| \log |S|)$, solving in $< 0.3$ ms.  
The Binary ILP is NP-hard in the worst case. Although HiGHS uses advanced presolve, LP relaxation, and branch-and-cut, it must solve a series of continuous linear programs, generate cutting planes, and perform tree search over hundreds of discrete binary variables, resulting in an average latency of ~547 ms.

---

### Q8: What is an "Optimality Gap", and how was it calculated in your experiments?
**Answer**:  
The optimality gap measures the percentage by which a heuristic solution exceeds the proven global minimum:
$$\text{Gap}_{\text{algo}} = \frac{Z_{\text{algo}} - Z_{\text{ILP}}^*}{Z_{\text{ILP}}^*} \times 100\%$$
Where $Z_{\text{ILP}}^*$ is the objective value proved optimal by HiGHS. Across 20 queries, Greedy achieved an average gap of 15.81%, while Dijkstra achieved an average gap of 20.58%.

---

### Q9: Why does the Greedy Heuristic produce suboptimal solutions on certain queries?
**Answer**:  
Greedy makes myopic decisions based on immediate step cost plus an admissible distance-to-destination heuristic $h(v)$. It lacks global foresight of downstream timetable synchronization. For instance, on queries from the Southern Ring to the Mainline (e.g. Q13, Q14), Greedy boards an immediate regional train that moves toward the destination but arrives at the interchange junction just after a fast cross-country express has departed, resulting in an 80%+ optimality gap.

---

### Q10: How does your Greedy algorithm prevent cycles and infinite loops?
**Answer**:  
The algorithm maintains an explicit history set `visited_stations` along each search path. Before expanding an outgoing connection $c$, it checks:
$$c.\text{to\_station\_id} \notin \text{visited\_stations}$$
If the destination station has already been visited along the active itinerary, the candidate branch is pruned immediately.

---

### Q11: What role do the weights $\alpha, \beta, \gamma$ play, and how were they chosen?
**Answer**:  
* $\alpha = 1.0$: Baseline weight on in-vehicle travel duration.
* $\beta = 1.5$: Penalty multiplier on transfer waiting time. Empirical transportation studies show passengers perceive waiting on platforms as $1.5\times$ to $2.0\times$ more burdensome than moving time.
* $\gamma = 30.0$: Fixed penalty equivalent to 30 minutes of travel time per transfer, reflecting the physical friction of luggage handling and platform navigation.

---

### Q12: Why was a synthetic dataset used instead of an arbitrary public GTFS feed?
**Answer**:  
1. **Full Ground-Truth Control**: A synthetic dataset with a fixed deterministic seed (`seed=42`) allows complete verification of every timetable connection, known transfer buffers, and reproducible counterexamples.
2. **Controlled Topology**: It incorporates 5 distinct corridors (Trunk, Coast, Industrial, Ring, Mountain Spur) with known bottleneck junctions to test both direct and multi-transfer routing under stress.
3. **Reproducibility**: External public feeds change frequently, have missing data, or require proprietary API keys. Synthetic generation ensures zero dependency failures across any evaluator's machine.

---

### Q13: Did the HiGHS solver prove global optimality in all your benchmark runs?
**Answer**:  
Yes. In all 20 evaluated benchmark queries, HiGHS terminated with `status = 0` (`Optimal`), with a relative duality gap $< 10^{-4}$, confirming that the reported itineraries are mathematically proven global optima.

---

### Q14: How does maximum transfer constraint $K_{\text{max}}$ affect problem feasibility?
**Answer**:  
$K_{\text{max}}$ imposes a hard upper bound:
$$\sum_{(c_1, c_2) \in T_{\text{cand}}} \delta_{\text{xfer}}(c_1, c_2) y_{c_1, c_2} \le K_{\text{max}}$$
In `test_06_max_transfer_constraint`, setting $K_{\text{max}} = 0$ on an OD pair between non-connected corridors (e.g. Eastport to Highland) correctly caused the solver to declare the problem infeasible, proving the constraint is active and enforced.

---

### Q15: How would this optimization system scale if the network grew to 1,000 stations and 50,000 connections?
**Answer**:  
* **Time-Dependent Dijkstra**: Scales logarithmically with stations; execution time would remain $< 50$ ms using priority queues.
* **Greedy Heuristic**: Bounded beam search would scale linearly with degree, remaining $< 100$ ms.
* **Exact ILP**: Full network ILP would become intractable ($> 100,000$ binary variables). To scale ILP to national networks, we would apply **geographic corridor corridor pruning**, **Connection-Scan Algorithm (CSA)** pre-filtering, or **Benders decomposition** to solve subproblems within a restricted spatio-temporal corridor.

---

### Q16: What is the primary takeaway from comparing Dijkstra, Greedy, and ILP?
**Answer**:  
Optimization is about trade-offs:
1. **Dijkstra** is fastest (0.28 ms) but suboptimal for multi-objective traveler satisfaction (20.6% gap).
2. **Greedy** provides an intermediate heuristic (2.0 ms, 15.8% gap) suitable for mobile applications.
3. **Exact ILP** achieves the best traveler experience (saving 27 min travel time, 25 min wait time, and 37% of transfers) at the cost of higher solve latency (547 ms), making it the gold standard for timetable planning and high-value journey optimization.

