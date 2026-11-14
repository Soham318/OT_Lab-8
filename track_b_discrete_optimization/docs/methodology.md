# Track B: Discrete Optimization — Methodology & Mathematical Formulations

> **Course**: Optimization Techniques (CS / AI)  
> **Assignment 8**: Optimize Anything — 14-Day Vibe-Coding Challenge  
> **Module**: Track B — Discrete & Combinatorial Optimization

---

## 1. Problem Formulation: The 0/1 Knapsack Problem

The 0/1 Knapsack problem is an archetype of combinatorial optimization and an NP-hard problem. Given a set of $n$ distinct items, each item $i \in \{1, \dots, n\}$ is characterized by:
- A non-negative value (profit or utility): $v_i \ge 0$
- A strictly positive weight: $w_i > 0$
- A knapsack maximum weight capacity: $W > 0$

We define binary decision variables:
$$x_i \in \{0, 1\}, \quad \forall i \in \{1, \dots, n\}$$
where $x_i = 1$ denotes that item $i$ is packed into the knapsack, and $x_i = 0$ denotes that it is excluded.

### Mathematical Program
$$\text{Maximize } Z = \sum_{i=1}^n v_i x_i$$
$$\text{Subject to: } \sum_{i=1}^n w_i x_i \le W$$
$$x_i \in \{0, 1\}, \quad \forall i \in \{1, \dots, n\}$$

---

## 2. Greedy Optimization Heuristic

### 2.1 Algorithmic Formulation
The canonical greedy heuristic evaluates the marginal value density (efficiency ratio) of each item:
$$r_i = \frac{v_i}{w_i}, \quad i \in \{1, \dots, n\}$$

1. **Sort**: Reorder items in descending order of efficiency:
   $$r_{\pi(1)} \ge r_{\pi(2)} \ge \dots \ge r_{\pi(n)}$$
2. **Pack**: Initialize cumulative weight $W_{\text{curr}} = 0$, cumulative value $V_{\text{curr}} = 0$.
3. **Iterate**: For $k = 1, \dots, n$:
   $$\text{If } W_{\text{curr}} + w_{\pi(k)} \le W \implies x_{\pi(k)} = 1, \quad W_{\text{curr}} \leftarrow W_{\text{curr}} + w_{\pi(k)}, \quad V_{\text{curr}} \leftarrow V_{\text{curr}} + v_{\pi(k)}$$
   $$\text{Else } x_{\pi(k)} = 0$$

### 2.2 Complexity
- Sorting: $\mathcal{O}(n \log n)$
- Linear scan: $\mathcal{O}(n)$
- Total Time: $\mathcal{O}(n \log n)$, Total Space: $\mathcal{O}(n)$

### 2.3 Suboptimality & Counterexample Proof
Greedy density selection fails to find the global optimum because it ignores item combinations and can leave fragmented, unusable capacity.
**Constructed Counterexample**:
Let $W = 50$:
- Item 0: $v_0 = 60, w_0 = 10 \implies r_0 = 6.0$
- Item 1: $v_1 = 100, w_1 = 20 \implies r_1 = 5.0$
- Item 2: $v_2 = 120, w_2 = 30 \implies r_2 = 4.0$

Greedy selection:
1. Picks Item 0: $W_{\text{curr}} = 10$, remaining capacity $= 40$.
2. Picks Item 1: $W_{\text{curr}} = 30$, remaining capacity $= 20$.
3. Examines Item 2: requires weight 30, but remaining capacity is only 20. Cannot fit.
- **Greedy Output**: Items $\{0, 1\}$, Total Value $= 160$, Total Weight $= 30$.
- **Global Optimum**: Items $\{1, 2\}$, Total Value $= 100 + 120 = 220$, Total Weight $= 20 + 30 = 50 \le 50$.
- **Optimality Gap**:
  $$\text{Gap} = \frac{220 - 160}{220} = 27.27\%$$

---

## 3. Exact Integer Linear Programming (ILP) via SciPy HiGHS

### 3.1 Standard Form
The exact binary program is cast into the standard matrix form solved by `scipy.optimize.milp` using the state-of-the-art HiGHS solver:
$$\text{Minimize } c^T x$$
$$\text{Subject to } \mathbf{0} \le A x \le b$$
$$l \le x \le u, \quad x_i \in \mathbb{Z}$$

Mapping:
- Cost vector: $c = -v \in \mathbb{R}^n$ (converting maximization to minimization)
- Constraint matrix: $A = w^T \in \mathbb{R}^{1 \times n}$
- Upper bound: $b = [W]$
- Lower bound: $\mathbf{0}$
- Variable bounds: $l_i = 0, u_i = 1, \forall i$
- Integrality vector: $\mathbf{1}_n$ (indicating binary integer variables)

### 3.2 HiGHS Solver Dynamics
HiGHS applies presolve reductions, Gomory mixed-integer cuts, and LP branch-and-cut to guarantee global optimality within a specified optimality tolerance ($\text{mip\_gap} \le 10^{-4}$).

---

## 4. Branch-and-Bound with Dantzig LP Relaxation

### 4.1 Principle
Branch-and-Bound traverses an implicit binary search tree over decision variables $x_1, \dots, x_n$ while using continuous Linear Programming (LP) relaxations to prune subtrees that cannot contain a solution superior to the best known incumbent $V_{\text{best}}$.

### 4.2 Dantzig Fractional Knapsack Upper Bound
At any node $k$ in the tree with partial assignment $x_1, \dots, x_{k-1}$, current weight $W_{\text{curr}}$, and current value $V_{\text{curr}}$:
Let remaining capacity be $C_{\text{rem}} = W - W_{\text{curr}}$.
Sorting remaining items $k \dots n$ descending by efficiency ratio $r_i = v_i / w_i$, we greedily fill capacity with whole items until item $m$ exceeds $C_{\text{rem}}$. We then take a fractional portion of critical item $m$:
$$\text{Upper Bound (UB)} = V_{\text{curr}} + \sum_{j=k}^{m-1} v_j + \left( \frac{C_{\text{rem}} - \sum_{j=k}^{m-1} w_j}{w_m} \right) v_m$$
Because continuous LP relaxation expands the feasible region ($x_i \in [0, 1]$ instead of $\{0, 1\}$), the optimal fractional value is a strict upper bound:
$$Z_{\text{fractional}}^* \ge Z_{\text{integer}}^*$$

### 4.3 Pruning Rules
1. **Infeasibility Pruning**: If $W_{\text{curr}} > W$, the branch violates the capacity constraint $\implies$ prune.
2. **Bound Pruning**: If $\text{UB} \le V_{\text{best}}$, the subtree cannot yield a solution better than the best already found $\implies$ prune.

---

## 5. Dynamic Programming Formulation

### 5.1 State & Recurrence
For integer weights $w_i \in \mathbb{Z}^+$ and integer capacity $W \in \mathbb{Z}^+$:
- **State Definition**: $DP[i, w]$ represents the maximum value achievable considering a subset of the first $i$ items with capacity at most $w \in \{0, \dots, W\}$.
- **Recurrence Relation**:
  $$DP[i, w] = \begin{cases} DP[i-1, w] & \text{if } w < w_i \\ \max\left( DP[i-1, w], \, DP[i-1, w - w_i] + v_i \right) & \text{if } w \ge w_i \end{cases}$$
- **Base Cases**:
  $$DP[0, w] = 0, \quad \forall w \in \{0, \dots, W\}$$
  $$DP[i, 0] = 0, \quad \forall i \in \{0, \dots, n\}$$

### 5.2 Backtracking Reconstruction
Starting from cell $(n, W)$:
For $i = n, n-1, \dots, 1$:
$$\text{If } DP[i, w] \neq DP[i-1, w] \implies x_i = 1, \quad w \leftarrow w - w_i$$
$$\text{Else } x_i = 0$$

### 5.3 Complexity
- **Time**: $\mathcal{O}(n W)$ (pseudo-polynomial in numerical magnitude of $W$)
- **Space**: $\mathcal{O}(n W)$ (table storage)

---

## 6. QUBO & Ising Model Formulations

### 6.1 Penalty Transformation
In Quadratic Unconstrained Binary Optimization (QUBO), the objective is to minimize an unconstrained quadratic polynomial over binary variables $z \in \{0, 1\}^N$:
$$\text{Minimize } H_{\text{QUBO}}(z) = z^T Q z + C_0$$

To encode the inequality constraint $\sum_{i=1}^n w_i x_i \le W$, we introduce binary slack variables $y_0, y_1, \dots, y_K \in \{0, 1\}$ with coefficients $c_k = 2^k$ ($K = \lfloor \log_2 W \rfloor$) such that:
$$\sum_{i=1}^n w_i x_i + \sum_{k=0}^K c_k y_k = W$$
We append a quadratic equality penalty with multiplier $P > 0$:
$$H_{\text{pen}}(x, y) = P \left( \sum_{i=1}^n w_i x_i + \sum_{k=0}^K c_k y_k - W \right)^2$$
Total Hamiltonian:
$$H_{\text{QUBO}}(z) = -\sum_{i=1}^n v_i x_i + P \left( \sum_{j=1}^N a_j z_j - W \right)^2$$
where $z = [x_1, \dots, x_n, y_0, \dots, y_K]^T$, $a = [w_1, \dots, w_n, c_0, \dots, c_K]^T$, and $N = n + K + 1$.

### 6.2 Expansion into Upper-Triangular Matrix $Q$
Expanding the quadratic penalty term:
$$\left( \sum_{j=1}^N a_j z_j - W \right)^2 = \sum_{j=1}^N a_j^2 z_j^2 + 2 \sum_{j < l} a_j a_l z_j z_l - 2 W \sum_{j=1}^N a_j z_j + W^2$$
Using the binary idempotency property $z_j^2 = z_j$:
$$= \sum_{j=1}^N (a_j^2 - 2 W a_j) z_j + 2 \sum_{j < l} a_j a_l z_j z_l + W^2$$
Merging with the linear objective $-\sum_{i=1}^n v_i z_i$:
- **Diagonal Elements ($j = l$)**:
  $$Q_{jj} = P(a_j^2 - 2 W a_j) - (v_j \text{ if } j \le n \text{ else } 0)$$
- **Off-Diagonal Elements ($j < l$)**:
  $$Q_{jl} = 2 P a_j a_l$$
- **Constant Offset**:
  $$C_0 = P W^2$$

### 6.3 Penalty Coefficient Selection Rule
If $P$ is too small, an infeasible state that packs an extra item with value $v_k$ and exceeds capacity by $\delta \ge 1$ will incur penalty $P \delta^2 = P$. If $v_k > P$, the net energy decreases, corrupting the unconstrained minimum.
Therefore, the penalty must strictly satisfy:
$$P > \max_{1 \le i \le n} v_i$$
Setting $P = \alpha \cdot \max_i v_i$ with $\alpha \ge 1.5$ guarantees that any constraint violation incurs an energy penalty exceeding any item profit, ensuring that the unconstrained global minimum of $H_{\text{QUBO}}$ is strictly feasible.

### 6.4 Conversion to Transverse Ising Spin Model
Ising spins take values $s_i \in \{-1, +1\}$.
The bijective mapping is:
$$z_i = \frac{s_i + 1}{2} \iff s_i = 2 z_i - 1$$
Substituting into $H_{\text{QUBO}}(z)$:
$$z_i = \frac{s_i + 1}{2}$$
$$z_i z_j = \frac{s_i s_j + s_i + s_j + 1}{4}$$
The Ising Hamiltonian is:
$$H_{\text{Ising}}(s) = \frac{1}{2} s^T J s + h^T s + C_{\text{Ising}}$$
where:
$$J_{ij} = J_{ji} = \frac{Q_{ij}}{4} \quad (\text{for } i \neq j)$$
$$h_i = \frac{Q_{ii}}{2} + \sum_{j \neq i} \frac{Q_{\min(i,j), \max(i,j)}}{4}$$
$$C_{\text{Ising}} = C_0 + \sum_{i=1}^N \frac{Q_{ii}}{2} + \sum_{i < j} \frac{Q_{ij}}{4}$$
For any binary state $z$ and corresponding spin vector $s = 2z - 1$:
$$H_{\text{Ising}}(s) \equiv H_{\text{QUBO}}(z)$$
demonstrating exact analytical parity.

