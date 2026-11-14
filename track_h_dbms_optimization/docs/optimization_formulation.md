# Track H: Mathematical Formulation of Index Selection

## 1. Problem Definition: The Index Selection Problem (ISP)

In modern database management systems, adding secondary B-tree indexes substantially accelerates data retrieval queries by reducing full table scans ($O(N)$) to logarithmic index traversals ($O(\log N)$). However, secondary indexes incur substantial trade-offs:
1. **Secondary Storage Footprint**: Each index builds an independent B-tree structure requiring storage pages.
2. **Write Overhead**: Every `INSERT`, `UPDATE`, or `DELETE` on the indexed table requires maintaining all corresponding index B-trees.
3. **Diminishing Returns & Redundancy**: If multiple candidate indexes can satisfy the same query filter or sort predicate, their performance benefits are non-additive (the query optimizer chooses only the most efficient access path).

The **Index Selection Problem (ISP)** is formulated as a discrete constrained optimization problem (a generalized 0-1 Knapsack / Maximum Coverage problem): given a candidate pool of secondary indexes, find a subset that maximizes total weighted workload performance improvement subject to a hard physical storage budget $S_{\max}$.

---

## 2. Mathematical Formulation

Let:
- $\mathcal{I} = \{1, 2, \dots, m\}$ be the set of $m$ candidate secondary indexes.
- $c_i \in \mathbb{R}^+$ be the physical storage footprint (in Megabytes) required by candidate index $i$.
- $\mathcal{Q} = \{1, 2, \dots, n\}$ be the representative database query workload.
- $w_q \in \mathbb{R}^+$ be the operational execution frequency weight of query $q \in \mathcal{Q}$.
- $C_q \subseteq \mathcal{I}$ be the subset of candidate indexes capable of accelerating query $q$.
- $b_{q,i} \in \mathbb{R}^+$ be the latency reduction (benefit score) achieved by query $q$ when evaluated using candidate index $i$.
- $S_{\max} \in \mathbb{R}^+$ be the maximum allowable secondary index storage budget (in MB).

### 2.1 Decision Variables
We define binary selection decision variables for each candidate index:
$$
x_i \in \{0, 1\} \quad \forall i \in \mathcal{I}
$$
where:
$$
x_i = \begin{cases} 
1 & \text{if candidate index } i \text{ is constructed and maintained,} \\
0 & \text{otherwise.}
\end{cases}
$$

### 2.2 Objective Function
The query optimizer selects at most one secondary access path (or covering index) for a given query table scan. Therefore, if multiple chosen indexes $i \in X \cap C_q$ apply to query $q$, the effective benefit is non-additive and governed by the best available index:
$$
B(q, X) = \max_{i \in C_q} (b_{q,i} \cdot x_i)
$$
The global objective is to maximize total workload performance improvement:
$$
\max_{X \subseteq \mathcal{I}} Z(X) = \sum_{q \in \mathcal{Q}} w_q B(q, X)
$$

### 2.3 Storage Budget Constraint
The aggregate storage consumed by all chosen indexes cannot exceed the designated threshold:
$$
\sum_{i \in \mathcal{I}} c_i x_i \le S_{\max}
$$

---

## 3. Integer Linear Programming (ILP) Linearization

The objective function $\max (b_{q,i} x_i)$ is non-linear. To solve it using standard Mixed-Integer Linear Programming (MILP) solvers, we linearize the problem by introducing auxiliary binary decision variables:
$$
y_{q,i} \in \{0, 1\} \quad \forall q \in \mathcal{Q}, \; i \in C_q
$$
where $y_{q,i} = 1$ indicates that index $i$ is actively assigned to accelerate query $q$.

### 3.1 Linear ILP Model
$$
\max \sum_{q \in \mathcal{Q}} \sum_{i \in C_q} w_q b_{q,i} y_{q,i}
$$
subject to:

1. **Index Activation Coupling**: An index can only be assigned to a query if that index is physically constructed:
   $$
   y_{q,i} \le x_i \quad \forall q \in \mathcal{Q}, \; i \in C_q
   $$

2. **Single Primary Index Allocation**: At most one candidate index can provide the primary access path benefit for query $q$:
   $$
   \sum_{i \in C_q} y_{q,i} \le 1 \quad \forall q \in \mathcal{Q}
   $$

3. **Storage Budget Constraint**:
   $$
   \sum_{i \in \mathcal{I}} c_i x_i \le S_{\max}
   $$

4. **Integrality Constraints**:
   $$
   x_i \in \{0, 1\} \quad \forall i \in \mathcal{I}
   $$
   $$
   0 \le y_{q,i} \le 1 \quad \forall q \in \mathcal{Q}, \; i \in C_q
   $$
   *(Note: Due to the coupling constraints and the objective maximization structure, the integrality of $y_{q,i}$ is naturally enforced when $x_i \in \{0, 1\}$.)*

We solve this system to global optimality using the HiGHS branch-and-cut solver accessed via `scipy.optimize.milp`.

---

## 4. Greedy Marginal Benefit Selection Heuristic

As a practical baseline for database tuning advisors, we implement the standard Greedy Benefit-to-Cost heuristic with dynamic marginal recalculation:

### 4.1 Algorithmic Procedure
1. Initialize the selected index set $S_0 = \emptyset$, current storage $C = 0$, and step $k = 0$.
2. In each iteration $k$, evaluate all unselected candidate indexes $i \in \mathcal{I} \setminus S_k$ satisfying $C + c_i \le S_{\max}$:
   - Compute current workload benefit $B(S_k)$.
   - Compute hypothetical benefit if index $i$ is added: $B(S_k \cup \{i\})$.
   - Calculate marginal gain:
     $$
     \Delta B(i \mid S_k) = B(S_k \cup \{i\}) - B(S_k)
     $$
   - Calculate benefit-to-cost efficiency ratio:
     $$
     R(i \mid S_k) = \frac{\Delta B(i \mid S_k)}{c_i}
     $$
3. Select index $i^*$ that maximizes $R(i \mid S_k)$.
4. If $\Delta B(i^* \mid S_k) \le 0$ or no index fits within the remaining budget, terminate.
5. Update $S_{k+1} = S_k \cup \{i^*\}$, $C \leftarrow C + c_{i^*}$, and repeat.

---

## 5. Theoretical Comparison & Approximation Bounds

| Attribute | Greedy Heuristic | Exact Binary ILP | Exhaustive Search |
| :--- | :--- | :--- | :--- |
| **Algorithmic Class** | Myopic Greedy Approximation | Branch-and-Cut (HiGHS) | Combinatorial Enumeration |
| **Worst-Case Complexity** | $O(m^2 \cdot |\mathcal{Q}|)$ | Exponential $O(2^m)$ worst-case, fast in practice | Exact $O(2^m \cdot |\mathcal{Q}|)$ |
| **Storage Compliance** | Strictly Guaranteed ($\le S_{\max}$) | Strictly Guaranteed ($\le S_{\max}$) | Strictly Guaranteed ($\le S_{\max}$) |
| **Optimality Guarantee** | $\ge (1 - 1/e) \approx 63.2\%$ on submodular instances | $100\%$ Globally Optimal | $100\%$ Globally Optimal |
| **Double-Counting Protection** | Handled via Dynamic Marginal Gains | Handled via $\sum_{i \in C_q} y_{q,i} \le 1$ Coupling | Handled via Set Benefit Function |
| **Observed Gap ($S_{\max}=3.0$ MB)** | **$6.92\%$ Optimality Gap** | **$0.00\%$ Optimality Gap** | **$0.00\%$ (Ground Truth)** |

