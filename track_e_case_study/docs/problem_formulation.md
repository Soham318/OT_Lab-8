# Mathematical Formulation: Railway Route and Transfer Optimization

> **Track E**: Main Real-Process Case Study  
> **Course**: Optimization Techniques — Lab Assignment 8  
> **Document Version**: 1.0.0  
> **Author**: Autonomous Senior Software Engineer & Optimization Researcher  

---

## 1. Executive Summary & Problem Overview

In modern passenger rail transportation, route planning involves much more than finding the shortest geographical distance between two points. Because passenger trains operate on strict, discrete time schedules, a physical route is only actionable if consecutive train services are timetable-compatible and allow sufficient passenger transfer buffers.

The **Railway Route and Transfer Optimization Problem** seeks an optimal passenger itinerary from a designated origin station $s_{\text{orig}}$ to a destination station $s_{\text{dest}}$, departing at or after a requested query departure time $t_{\text{query}}$. The optimization must balance three distinct, often conflicting criteria:
1. **Total Journey Time**: Elapsed wall-clock time from journey start to final destination arrival.
2. **Transfer Waiting Time**: Idle time spent at intermediate interchange stations between connecting trains.
3. **Number of Transfers**: Total interchanges between different train services, which incur friction, fatigue, platform traversal effort, and risk of missed connections.

---

## 2. Timetable Network Representation

The railway timetable is modeled as a directed, time-dependent network. Let $S = \{s_1, s_2, \dots, s_N\}$ denote the set of physical railway stations.

A scheduled train trip comprises elementary, non-stop timetable segments called **connections**:
$$c = \big(\text{dep\_stn}(c), \, \text{arr\_stn}(c), \, \text{dep\_time}(c), \, \text{arr\_time}(c), \, \text{srv}(c), \, \text{dist}(c)\big)$$

Where:
* $\text{dep\_stn}(c), \text{arr\_stn}(c) \in S$ are the departure and arrival stations.
* $\text{dep\_time}(c), \text{arr\_time}(c) \in [0, 1440)$ are scheduled departure and arrival times (in minutes from midnight).
* $\text{srv}(c)$ is the unique identifier of the train service operating connection $c$.
* $\text{dist}(c) > 0$ is the track distance in kilometers.
* The elementary travel time is given by $\tau(c) = \text{arr\_time}(c) - \text{dep\_time}(c) > 0$.

Let $C = \{c_1, c_2, \dots, c_M\}$ denote the complete set of all scheduled connections across the 24-hour planning horizon.

---

## 3. Sets and Indices

| Symbol | Mathematical Definition | Physical Description |
| :--- | :--- | :--- |
| $S$ | $\{s_1, s_2, \dots, s_N\}$ | Set of all railway stations ($N = 28$). |
| $C$ | $\{c_1, c_2, \dots, c_M\}$ | Set of all scheduled elementary train connections ($M = 551$). |
| $R$ | $\{r_1, r_2, \dots, r_K\}$ | Set of train routes / service corridors ($K = 10$). |
| $s_{\text{orig}} \in S$ | Designated scalar | Journey origin station. |
| $s_{\text{dest}} \in S$ | Designated scalar | Journey destination station ($s_{\text{dest}} \neq s_{\text{orig}}$). |
| $t_{\text{query}} \in [0, 1440)$ | Scalar (minutes) | Earliest allowable departure time from origin. |
| $T$ | $\subseteq C \times C$ | Set of all physically and temporally feasible transfers: |

$$T = \Big\{(c, c') \in C \times C \;\Big|\; \text{arr\_stn}(c) = \text{dep\_stn}(c'), \; \text{dep\_time}(c') \ge \text{arr\_time}(c) + \Delta_{\text{min}}(\text{arr\_stn}(c))\Big\}$$

Where $\Delta_{\text{min}}(s)$ is the minimum transfer buffer required at station $s$.

---

## 4. Input Parameters

| Parameter | Unit | Description |
| :--- | :--- | :--- |
| $\tau(c)$ | Minutes | In-vehicle travel duration of connection $c$: $\tau(c) = \text{arr\_time}(c) - \text{dep\_time}(c)$. |
| $\Delta_{\text{min}}(s)$ | Minutes | Station-specific minimum buffer required to traverse platforms (typically $10 \le \Delta_{\text{min}}(s) \le 20$). |
| $w(c, c')$ | Minutes | Transfer waiting time between connection $c$ and $c'$: $w(c, c') = \text{dep\_time}(c') - \text{arr\_time}(c)$. |
| $\delta_{\text{srv}}(c, c')$ | Binary | Service change indicator: $\delta_{\text{srv}}(c, c') = 1$ if $\text{srv}(c) \neq \text{srv}(c')$, else $0$ (staying on same train). |
| $\alpha \ge 0$ | Weight | Relative importance penalty on in-vehicle travel time. |
| $\beta \ge 0$ | Weight | Relative penalty on transfer waiting time (empirically passengers perceive wait time $1.5\times$ to $2.5\times$ more negatively than in-vehicle time). |
| $\gamma \ge 0$ | Penalty / Weight | Fixed cognitive penalty per physical transfer (disutility of luggage handling and platform navigation). |
| $K_{\text{max}}$ | Integer | Maximum allowable number of transfers per itinerary. |

---

## 5. Decision Variables

* **Connection Traversal Indicator**:
  $$x_c \in \{0, 1\} \quad \forall c \in C$$
  $x_c = 1$ if elementary connection $c$ is included in the passenger itinerary; $0$ otherwise.

* **Connection Sequence / Transfer Indicator**:
  $$y_{c, c'} \in \{0, 1\} \quad \forall (c, c') \in T$$
  $y_{c, c'} = 1$ if connection $c$ is immediately succeeded by connection $c'$ in the passenger itinerary; $0$ otherwise.

* **Journey Boundary Variables**:
  * $t_{\text{start}} \in [0, 1440)$: Departure time of the first traversed connection from $s_{\text{orig}}$.
  * $t_{\text{end}} \in [0, 1440)$: Arrival time of the final traversed connection at $s_{\text{dest}}$.

---

## 6. Multi-Objective Analysis & Formulation

### 6.1 Trade-Off Between Objectives

1. **Total Journey Time ($T_{\text{journey}} = t_{\text{end}} - t_{\text{start}}$)**:
   Measures pure wall-clock velocity. A traveler wants to reach their destination as early as possible.
2. **Transfer Waiting Time ($W = \sum_{(c, c') \in T} w(c, c') y_{c, c'}$)**:
   Measures idle delay at intermediate stations. A route with 2 hours total duration including 50 minutes waiting on a cold platform is perceived far worse than a route with 2 hours continuous movement.
3. **Number of Transfers ($N_{\text{transfers}} = \sum_{(c, c') \in T} \delta_{\text{srv}}(c, c') y_{c, c'}$)**:
   Direct measure of passenger inconvenience. Even if an itinerary with 3 transfers arrives 2 minutes earlier than a direct train, human travelers overwhelmingly prefer the direct service.

### 6.2 Primary vs. Secondary Criteria Justification

* **Primary Objective**: **Earliest Arrival / Minimum Total Journey Duration**. The ultimate goal of transport is getting the traveler to their destination in the shortest calendar time.
* **Secondary Regularizers**: Transfer wait time penalty $\beta$ and fixed transfer penalty $\gamma$. These act as Pareto regularization terms to prune paths that achieve marginally earlier arrivals at the cost of excessive or stressful transfers.

### 6.3 Composite Objective Function

$$\min Z = \alpha \sum_{c \in C} \tau(c) x_c + \beta \sum_{(c, c') \in T} w(c, c') y_{c, c'} + \gamma \sum_{(c, c') \in T} \delta_{\text{srv}}(c, c') y_{c, c'}$$

With standard normalized weights:
* $\alpha = 1.0$ (baseline travel duration)
* $\beta = 1.5$ (psychological wait penalty multiplier)
* $\gamma = 30.0$ (equivalent to 30 minutes of travel disutility per physical transfer)

---

## 7. Mathematical Constraints

### 7.1 Flow Conservation on the Timetable Network

For every connection $c \in C$:
1. If $c$ departs from $s_{\text{orig}}$, it can either be the initial leg or preceded by an incoming connection.
2. If $c$ arrives at $s_{\text{dest}}$, it can either be the terminal leg or followed by an outgoing connection.
3. For any intermediate connection traversed, it must have exactly one predecessor and one successor in the itinerary:

$$\sum_{c' : (c', c) \in T} y_{c', c} = x_c \quad \forall c \in C \text{ with } \text{dep\_stn}(c) \neq s_{\text{orig}}$$

$$\sum_{c' : (c, c') \in T} y_{c, c'} = x_c \quad \forall c \in C \text{ with } \text{arr\_stn}(c) \neq s_{\text{dest}}$$

### 7.2 Boundary Conditions (Origin and Destination)

Exactly one initial connection departs from $s_{\text{orig}}$ at or after $t_{\text{query}}$:
$$\sum_{c \in C : \text{dep\_stn}(c) = s_{\text{orig}}, \, \text{dep\_time}(c) \ge t_{\text{query}}} \Big(x_c - \sum_{c' : (c', c) \in T} y_{c', c}\Big) = 1$$

Exactly one terminal connection arrives at $s_{\text{dest}}$:
$$\sum_{c \in C : \text{arr\_stn}(c) = s_{\text{dest}}} \Big(x_c - \sum_{c' : (c, c') \in T} y_{c, c'}\Big) = 1$$

No connection may depart prior to the requested query time:
$$x_c = 0 \quad \forall c \in C \text{ with } \text{dep\_stn}(c) = s_{\text{orig}} \text{ and } \text{dep\_time}(c) < t_{\text{query}}$$

### 7.3 Transfer Feasibility & Minimum Buffer

By construction of the feasible transfer set $T$, every transfer $(c, c') \in T$ strictly satisfies:
$$\text{dep\_time}(c') - \text{arr\_time}(c) \ge \Delta_{\text{min}}(\text{arr\_stn}(c)) \quad \forall (c, c') \in T$$
Any pair violating this buffer is omitted from $T$, rendering $y_{c, c'} = 0$ implicitly.

### 7.4 Transfer Bound Constraint

To prevent itineraries with unmanageable switching:
$$\sum_{(c, c') \in T} \delta_{\text{srv}}(c, c') y_{c, c'} \le K_{\text{max}}$$
Where $K_{\text{max}}$ is typically set to $3$ or $4$.

### 7.5 Integrality Constraints

$$x_c \in \{0, 1\} \quad \forall c \in C$$
$$y_{c, c'} \in \{0, 1\} \quad \forall (c, c') \in T$$

---

## 8. Algorithmic Complexity & Theoretical Properties

1. **Static Dijkstra Inapplicability**:
   Ordinary Dijkstra assumes static edge costs $d(u, v)$ invariant to arrival time. In a scheduled railway network, the time to traverse from $u$ to $v$ is a non-linear step function of the arrival time at $u$:
   $$\text{cost}(u, v \mid t) = \min_{c \in C_{u \to v}, \, \text{dep\_time}(c) \ge t + \Delta} \big(\text{arr\_time}(c) - t\big)$$
   Therefore, standard Dijkstra on a static topological graph cannot solve this problem without either **Time-Expanded Graph** expansion or a **Time-Dependent Earliest-Arrival** label-setting algorithm.

2. **FIFO (First-In, First-Out) / Non-Overtaking Property**:
   On a single rail route, trains rarely overtake each other between adjacent stations. The time-dependent earliest-arrival problem satisfies the FIFO property on elementary arcs, which guarantees that a greedy/Dijkstra label-setting procedure finds the exact earliest arrival time at every reachable station in polynomial time $\mathcal{O}(|C| \log |S|)$.

---

## 9. Assumptions and Scope

1. **Deterministic Schedule**: All trains adhere to their scheduled timetables without stochastic delay distributions.
2. **24-Hour Horizon**: Departures and arrivals operate within a single calendar day $[0, 1440)$ minutes.
3. **Platform Independence**: Minimum transfer buffers $\Delta_{\text{min}}(s)$ represent the station-wide upper bound required to switch platforms at station $s$.

