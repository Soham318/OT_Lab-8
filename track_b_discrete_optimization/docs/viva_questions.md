# Track B: Discrete Optimization — Academic Viva Defense Questions & Model Answers

> **Course**: Optimization Techniques (CS / AI)  
> **Assignment 8**: Optimize Anything — 14-Day Vibe-Coding Challenge  
> **Module**: Track B Viva Examination Preparation (16 Core Academic Questions)

---

### Q1. Why is the 0/1 Knapsack Problem classified as NP-hard, yet it can be solved in $\mathcal{O}(nW)$ time using Dynamic Programming?
**Model Answer:**
The $\mathcal{O}(nW)$ time complexity of Dynamic Programming is **pseudo-polynomial**, not polynomial.
In computational complexity theory, the input size of an integer instance is proportional to the number of *bits* required to encode the numbers. For a knapsack capacity $W$, the number of bits needed to represent $W$ is $L = \lceil \log_2(W + 1) \rceil$. Therefore, $W = 2^L$.
Expressing the runtime in terms of the input length $L$:
$$\mathcal{O}(n W) = \mathcal{O}(n \cdot 2^L)$$
This shows that the running time is actually exponential in the binary length of the input. If $W$ is large (e.g. $W = 10^{12}$, requiring only 40 bits of storage), an $\mathcal{O}(nW)$ algorithm requires $10^{14}$ operations, making it completely intractable. Thus, the 0/1 Knapsack problem is weakly NP-hard.

---

### Q2. Explain the local selection rule in the Greedy Knapsack heuristic and prove why it can produce a suboptimal solution.
**Model Answer:**
The greedy heuristic computes the value-to-weight density ratio:
$$r_i = \frac{v_i}{w_i}$$
Items are sorted such that $r_1 \ge r_2 \ge \dots \ge r_n$. The local selection rule iteratively packs items with the highest remaining $r_i$ if they fit within the remaining capacity $W - W_{\text{curr}}$.

**Suboptimality Proof by Counterexample**:
Consider an instance with capacity $W = 50$:
- Item 0: $v_0 = 60, w_0 = 10 \implies r_0 = 6.0$
- Item 1: $v_1 = 100, w_1 = 20 \implies r_1 = 5.0$
- Item 2: $v_2 = 120, w_2 = 30 \implies r_2 = 4.0$

Greedy packs Item 0 ($w=10$, remaining 40) and Item 1 ($w=20$, remaining 20). Item 2 requires weight 30, so it cannot fit.
- Greedy Solution: Items $\{0, 1\}$, Total Value $= 160$, Total Weight $= 30$.
- Global Optimum: Items $\{1, 2\}$, Total Value $= 100 + 120 = 220$, Total Weight $= 20 + 30 = 50 \le 50$.
- Optimality Gap: $\frac{220 - 160}{220} = 27.27\%$.
Greedy fails because it makes an irrevocable local commitment to high-density items that consume fractional capacity, leaving stranded, unusable slack that prevents higher-valued bulk items from being packed.

---

### Q3. How does Dantzig's continuous LP relaxation provide an upper bound for Branch-and-Bound?
**Model Answer:**
In the 0/1 Knapsack problem, decision variables are strictly binary: $x_i \in \{0, 1\}$.
The continuous LP relaxation relaxes the integrality constraint to $x_i \in [0, 1]$ (the Fractional Knapsack problem).
Because the feasible region of the continuous relaxation strictly contains the discrete feasible set ($\{0, 1\}^n \subset [0, 1]^n$), the supremum of the objective over the relaxed set is a valid upper bound for the discrete program:
$$\max_{x \in [0, 1]^n, w^T x \le W} v^T x \ge \max_{x \in \{0, 1\}^n, w^T x \le W} v^T x$$

Dantzig (1957) proved that the fractional knapsack problem is solved optimally in $\mathcal{O}(n \log n)$ time by the greedy density rule, taking whole items until the capacity is nearly full and then taking a fractional slice $\frac{C_{\text{rem}}}{w_m}$ of the critical item $m$. This upper bound $\text{UB} = V_{\text{curr}} + \sum v_j + \frac{C_{\text{rem}}}{w_m} v_m$ allows Branch-and-Bound to safely prune any branch whose $\text{UB} \le V_{\text{best}}$.

---

### Q4. Describe the two pruning conditions in Branch-and-Bound. How do they prevent an exhaustive $2^n$ search?
**Model Answer:**
At any node in the search tree:
1. **Infeasibility Pruning (Pruning by Infeasibility)**:
   If the cumulative weight of the currently selected items exceeds capacity ($W_{\text{curr}} > W$), the node and all its descendants are physically infeasible because item weights are strictly non-negative ($w_i > 0$). The subtree is immediately pruned.
2. **Bound Pruning (Pruning by Optimality / Dominance)**:
   The LP relaxation upper bound $\text{UB}$ is computed for the subtree. If $\text{UB} \le V_{\text{best}}$ (where $V_{\text{best}}$ is the value of the best feasible discrete solution discovered so far), no integer assignment in this subtree can possibly surpass the current incumbent. The entire branch is pruned.

In our experiments, Branch-and-Bound solved an $N=50$ instance ($2^{50} \approx 1.12 \times 10^{15}$ states) by exploring fewer than 200 nodes, reducing the active search space by over 13 orders of magnitude.

---

### Q5. What is the state definition and recurrence relation for the 0/1 Knapsack Dynamic Programming table?
**Model Answer:**
- **State Definition**: Let $DP[i, w]$ be the maximum total value that can be achieved using a subset of the first $i$ items ($i \in \{0, \dots, n\}$) with total weight not exceeding $w \in \{0, \dots, W\}$.
- **Recurrence Relation**:
  $$DP[i, w] = \begin{cases} DP[i-1, w] & \text{if } w < w_i \\ \max\left( DP[i-1, w], \, DP[i-1, w - w_i] + v_i \right) & \text{if } w \ge w_i \end{cases}$$
- **Interpretation**: At item $i$, we face an optimal substructure choice:
  1. *Exclude item $i$*: The value is simply $DP[i-1, w]$.
  2. *Include item $i$*: Requires spending $w_i$ capacity, leaving $w - w_i$ capacity for the first $i-1$ items, yielding value $DP[i-1, w - w_i] + v_i$.
  The principle of optimality guarantees that the maximum of these two alternatives is the global optimum for state $(i, w)$.

---

### Q6. How does backtracking reconstruction extract the optimal item combination from a DP table?
**Model Answer:**
After filling the table up to $DP[n, W]$, we trace decisions backwards from $(n, W)$ to $(0, 0)$:
1. Set current capacity pointer $w = W$.
2. For $i = n$ down to 1:
   - Compare $DP[i, w]$ with $DP[i-1, w]$.
   - If $DP[i, w] \neq DP[i-1, w]$, item $i$ must have been included to produce the value increase. We set $x_i = 1$ and decrement capacity: $w \leftarrow w - w_i$.
   - If $DP[i, w] == DP[i-1, w]$, item $i$ was excluded. We set $x_i = 0$ and $w$ remains unchanged.
3. This reconstruction takes $\mathcal{O}(n)$ time and extracts the exact binary decision vector $x^* \in \{0, 1\}^n$.

---

### Q7. What is a QUBO model, and why can constraints not be directly expressed in it?
**Model Answer:**
QUBO stands for **Quadratic Unconstrained Binary Optimization**. Its standard mathematical form is:
$$\min_{z \in \{0, 1\}^N} z^T Q z + C_0$$
QUBO is defined strictly on an unconstrained binary domain. Constraints (such as $\sum w_i x_i \le W$) cannot be imposed directly as linear inequalities because the optimization domain is purely $\{0, 1\}^N$ without constraint boundaries.
To enforce constraints, they must be converted into quadratic penalty terms and added directly into the objective function, transforming the problem into an unconstrained energy minimization:
$$H_{\text{total}}(z) = H_{\text{objective}}(z) + P \cdot H_{\text{constraint}}(z)$$
where $P > 0$ is a penalty coefficient.

---

### Q8. How do binary slack variables convert an inequality constraint ($\le W$) into a QUBO equality constraint?
**Model Answer:**
The knapsack constraint is an inequality: $\sum_{i=1}^n w_i x_i \le W$.
QUBO penalties require squared equality forms $[g(x)]^2 = 0$.
To bridge this, we introduce integer slack $s \in [0, W]$ such that:
$$\sum_{i=1}^n w_i x_i + s = W$$
Because QUBO only accepts binary variables, $s$ is expanded into a binary representation using powers of two:
$$s = \sum_{k=0}^K c_k y_k, \quad y_k \in \{0, 1\}, \quad c_k \in \{1, 2, 4, 8, \dots\}$$
where $K = \lfloor \log_2 W \rfloor$.
The inequality is now an exact linear equality over binary variables:
$$\sum_{i=1}^n w_i x_i + \sum_{k=0}^K c_k y_k - W = 0$$
Squaring this expression yields the quadratic penalty:
$$H_{\text{pen}} = P \left( \sum_{i=1}^n w_i x_i + \sum_{k=0}^K c_k y_k - W \right)^2$$

---

### Q9. What is the mathematical condition for choosing the penalty coefficient $P$ in a QUBO knapsack formulation?
**Model Answer:**
The penalty multiplier $P$ must balance two competing forces:
1. If $P$ is too small, an infeasible state that packs an extra item with value $v_k$ and exceeds capacity by $\delta \ge 1$ incurs penalty $P \delta^2 \ge P$. If $v_k > P$, the net energy is lower than the feasible optimum, causing the unconstrained minimizer to select an infeasible solution.
2. If $P$ is excessively large, numerical conditioning suffers, and the energy landscape becomes dominated by steep penalty canyons that obscure the relative differences among feasible states.

**Exact Theoretical Bound**:
To guarantee that any constraint violation ($\delta \ge 1$) incurs a penalty strictly greater than any potential objective gain:
$$P > \max_{1 \le i \le n} v_i$$
In practice, setting $P = 1.5 \times \max_i v_i$ or $P = 2.0 \times \max_i v_i$ guarantees that every infeasible state has strictly higher energy than the global feasible optimum.

---

### Q10. Derive the transformation from binary QUBO variables $z_i \in \{0, 1\}$ to Ising spin variables $s_i \in \{-1, +1\}$.
**Model Answer:**
The linear mapping between binary variables $z_i$ and Ising spins $s_i$ is:
$$z_i = \frac{s_i + 1}{2} \iff s_i = 2 z_i - 1$$
Substituting this into a quadratic term $z_i z_j$:
$$z_i z_j = \left( \frac{s_i + 1}{2} \right) \left( \frac{s_j + 1}{2} \right) = \frac{s_i s_j + s_i + s_j + 1}{4}$$
For a diagonal term $z_i$ (since $z_i^2 = z_i$):
$$z_i = \frac{s_i + 1}{2}$$
Given $E_{\text{QUBO}}(z) = \sum_i Q_{ii} z_i + \sum_{i < j} Q_{ij} z_i z_j + C_0$:
$$H_{\text{Ising}}(s) = \sum_{i < j} J_{ij} s_i s_j + \sum_i h_i s_i + C_{\text{Ising}}$$
where:
$$J_{ij} = \frac{Q_{ij}}{4}, \quad h_i = \frac{Q_{ii}}{2} + \sum_{j \neq i} \frac{Q_{\min(i,j), \max(i,j)}}{4}$$
$$C_{\text{Ising}} = C_0 + \sum_i \frac{Q_{ii}}{2} + \sum_{i < j} \frac{Q_{ij}}{4}$$
This proves that QUBO and Ising models are mathematically isomorphic under affine coordinate transformation.

---

### Q11. Why does Integer Linear Programming (ILP) scale to hundreds of items while classical exhaustive enumeration of QUBO fails beyond 20 variables?
**Model Answer:**
- **Classical Exhaustive QUBO**: Evaluates all $2^N$ combinations. For $N=20$, $2^{20} \approx 10^6$ evaluations (manageable in seconds). For $N=40$, $2^{40} \approx 10^{12}$ evaluations (days). For $N=100$, $2^{100} \approx 1.27 \times 10^{30}$ evaluations (physically impossible).
- **ILP (HiGHS Branch-and-Cut)**: Employs polyhedral combinatorics:
  1. *Presolve*: Eliminates redundant variables and tightens bounds.
  2. *Cutting Planes*: Generates Gomory and knapsack cover cuts that slice away fractional non-integer vertices from the LP relaxation polytope without cutting any integer points.
  3. *LP Duality*: Solves continuous relaxations via the Simplex method in fractions of a millisecond, providing tight bounds that prune massive portions of the search space.
  Consequently, ILP solves 200-variable knapsack problems in under 500 ms without examining more than a tiny fraction of the state space.

---

### Q12. How does the choice of knapsack capacity ratio $W / \sum w_i$ influence the empirical hardness of the problem?
**Model Answer:**
The capacity ratio $\rho = \frac{W}{\sum w_i}$ defines the packing constraint tightness:
- If $\rho \ge 1.0$, all items fit; the problem is trivial ($x_i = 1, \forall i$).
- If $\rho \le 0.1$, only a few small items fit; greedy density heuristics and branch-and-bound find the optimum almost immediately.
- The **phase boundary of maximal hardness** typically occurs near $\rho \approx 0.4 - 0.5$ with strongly correlated weights and values ($v_i = w_i + c$). Here:
  - Many diverse item combinations have nearly identical total weights close to $W$.
  - The continuous LP relaxation bound is extremely close to the integer optimum, making bound-based pruning less decisive and forcing algorithms to explore deeper into the tree.

---

### Q13. Explain the difference between weakly NP-hard and strongly NP-hard problems. Where does Knapsack stand?
**Model Answer:**
- A problem is **weakly NP-hard** if it can be solved by an algorithm whose running time is polynomial in the number of items $n$ and the numerical magnitude of the input data (e.g. $W$), such as pseudo-polynomial Dynamic Programming $\mathcal{O}(nW)$. If all input numbers are bounded by a polynomial in $n$ ($W \le p(n)$), the problem is solvable in true polynomial time.
- A problem is **strongly NP-hard** if it remains NP-hard even when all input numbers are bounded by a polynomial in $n$ (or encoded in unary). Such problems cannot have pseudo-polynomial time algorithms unless $P = NP$ (e.g., Traveling Salesperson Problem, 3-Partition, Vertex Cover).
- The 0/1 Knapsack Problem is **weakly NP-hard**.

---

### Q14. What is a Knapsack Cover Cut, and how do modern MILP solvers use it?
**Model Answer:**
A set of items $C \subseteq \{1, \dots, n\}$ is a **cover** if their combined weight exceeds capacity:
$$\sum_{j \in C} w_j > W$$
A cover is a **minimal cover** if removing any item makes the remaining weight $\le W$.
Because all items in $C$ cannot be packed simultaneously, any feasible binary solution must satisfy the **cover inequality**:
$$\sum_{j \in C} x_j \le |C| - 1$$
Modern MILP solvers (like HiGHS) solve the LP relaxation. If the fractional LP solution violates a cover inequality, the solver adds the cover cut as a new linear constraint. This slices off the fractional point and tightens the LP relaxation polytope towards the convex hull of integer solutions, drastically accelerating Branch-and-Bound convergence.

---

### Q15. In your empirical benchmarks, why did Branch-and-Bound execute faster than Dynamic Programming on instances up to $N=50$?
**Model Answer:**
In our experiments at $N=50, W=457$:
- **Dynamic Programming**: Took **12.24 ms** because it must systematically fill every cell of the $(51) \times (458)$ table (23,358 operations and memory writes).
- **Branch-and-Bound**: Took **0.703 ms** (over $17\times$ faster).
**Reason**: Branch-and-Bound does not compute solutions for every sub-capacity $w \in [0, W]$. By sorting items by efficiency, the greedy Dantzig LP upper bound computed at the root node was very close to the true integer optimum. Consequently, after exploring just a few dozen promising branches, $V_{\text{best}}$ was already optimal, and bound pruning instantly pruned thousands of remaining branches, requiring fewer than 200 node evaluations.

---

### Q16. How does your Track B implementation satisfy the compulsory requirements of Assignment 8?
**Model Answer:**
Track B satisfies 100% of the discrete optimization syllabus requirements:
1. **Greedy Heuristic**: Implemented value-to-weight density sorting with documented counterexample proving a $27.27\%$ optimality gap.
2. **Exact ILP**: Formulated binary decision program and solved using SciPy HiGHS (`milp`).
3. **Branch-and-Bound**: Transparent tree search implementing Dantzig continuous LP upper bounds, recording branching decisions and pruning events.
4. **Dynamic Programming**: Implemented 2D DP table with recurrence relation, base cases, and exact backtracking reconstruction.
5. **QUBO & Ising Models**: Formulated quadratic objective with binary slack variables, derived the exact analytical spin mapping $s_i = 2x_i - 1$, proved the critical penalty condition $P > \max(v_i)$, and verified energy parity $< 10^{-10}$.
6. **Multi-Scale Benchmarks**: Tested across 9 instances from $N=3$ to $N=200$ with 4 publication-ready plots and automated unit tests.

