# Baseline Methodology: Time-Dependent Earliest-Arrival Routing Algorithm

> **Track E**: Main Real-Process Case Study  
> **Course**: Optimization Techniques — Lab Assignment 8  
> **Document Version**: 1.0.0  

---

## 1. Static vs. Time-Dependent Dijkstra: Theoretical Foundation

### 1.1 Why Standard Dijkstra Fails on Scheduled Rail Networks
Standard Dijkstra's algorithm computes shortest paths on a static weighted graph $G = (V, E, w)$ where edge weights $w(u, v)$ are constant scalar values representing distance or fixed traversal cost.

In scheduled public transit and railway networks, edge traversal cost is **not constant**; it is an intrinsically **time-dependent step function**:
$$c(u, v, t) = \min \big\{\text{arr\_time}(c) - t \;\big|\; c \in C_{u \to v}, \, \text{dep\_time}(c) \ge t + \Delta(u)\big\}$$

If an ordinary static Dijkstra algorithm is applied using static minimum link runtimes:
1. It ignores whether a train actually runs at the passenger's arrival time.
2. It assumes instantaneous transfers without waiting, producing physically impossible "teleportation" routes.
3. It cannot enforce station-specific minimum transfer buffers $\Delta_{\text{min}}(s)$.

### 1.2 The Time-Dependent Earliest-Arrival Principle
The **Time-Dependent Earliest-Arrival Dijkstra (TDEAD)** algorithm maintains a label $\tau(v)$ representing the earliest possible arrival time at station $v$, given an initial departure at or after $t_{\text{query}}$ from $s_{\text{orig}}$.

Because rail timetables on track segments satisfy the **FIFO (First-In, First-Out)** property (a train departing later cannot arrive earlier than an earlier train on the same segment), greedy label-setting remains provably optimal for minimizing arrival time.

---

## 2. Algorithmic Architecture

### 2.1 State Representation
Each priority queue state is defined by a 5-tuple:
$$(\text{current\_time}, \, \text{station\_id}, \, \text{incoming\_service\_id}, \, \text{accumulated\_wait}, \, \text{transfers})$$

Where:
* $\text{current\_time}$: Earliest arrival time at `station_id`.
* `incoming_service_id`: The train service used to reach `station_id` (`None` at origin).
* `accumulated_wait`: Total minutes spent waiting at interchange stations.
* `transfers`: Total number of physical service switches performed.

### 2.2 Transfer Feasibility Logic
When evaluating outgoing connections $c \in C$ from current station $u$:
1. **Departure Window**: The train must depart at or after the traveler's ready time:
   $$t_{\text{ready}} = \begin{cases} t_{\text{query}} & \text{if } u = s_{\text{orig}} \text{ and } \text{incoming\_service} = \text{None} \\ \text{current\_time} & \text{if } \text{srv}(c) = \text{incoming\_service} \text{ (passenger stays on same train)} \\ \text{current\_time} + \Delta_{\text{min}}(u) & \text{if } \text{srv}(c) \neq \text{incoming\_service} \text{ (interchange transfer)} \end{cases}$$
2. **Waiting Time Calculation**:
   $$w = \text{dep\_time}(c) - \text{current\_time}$$
   If $\text{srv}(c) = \text{incoming\_service}$, the dwell time at the intermediate station is treated as in-vehicle dwell (not an interchange transfer).
   If $\text{srv}(c) \neq \text{incoming\_service}$, $w$ is recorded as an interchange transfer wait.

### 2.3 Route Reconstruction
To reconstruct the concrete passenger itinerary:
* Each connection traversal stores a predecessor pointer:
  $$\text{parent}[v] = (u, \, c, \, \text{dep\_time}, \, \text{arr\_time}, \, \text{wait\_time})$$
* Once $s_{\text{dest}}$ is dequeued from the priority queue, the path is backtracked from $s_{\text{dest}}$ to $s_{\text{orig}}$, yielding an ordered list of connection legs, intermediate transfer stations, transfer wait durations, and train names.

---

## 3. Metrics Calculated by the Baseline

1. **Total Journey Duration**:
   $$\text{Duration} = t_{\text{arrival}}(s_{\text{dest}}) - t_{\text{departure}}(s_{\text{orig}})$$
2. **Total In-Vehicle Travel Time**:
   $$T_{\text{ride}} = \sum_{c \in \text{path}} \tau(c)$$
3. **Total Transfer Waiting Time**:
   $$W_{\text{transfer}} = \sum_{i = 1}^{k} \big(\text{dep\_time}(c_{i+1}) - \text{arr\_time}(c_i)\big) \quad \text{for } \text{srv}(c_{i+1}) \neq \text{srv}(c_i)$$
4. **Number of Transfers**:
   $$N_{\text{transfers}} = \big|\{i \mid \text{srv}(c_{i+1}) \neq \text{srv}(c_i)\}\big|$$
5. **Execution Latency**: Wall-clock CPU time in milliseconds to solve the query.

