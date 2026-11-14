# Track D: Parallel and Distributed Optimization — Comprehensive Viva Q&A Guide

> **Course**: Optimization Techniques — Assignment 8  
> **Module**: `track_d_parallel_distributed_optimization/`  
> **Topic**: Submodular Optimization, Parallel Computing, Scaling Laws, Federated Learning, Multi-Objective MGDA, and GradNorm.

---

### Q1: What is a submodular set function, and what does the "diminishing returns" property mean mathematically?
**Answer:**  
A set function $f: 2^V \to \mathbb{R}$ defined on a finite ground set $V$ is submodular if for all subsets $A \subseteq B \subseteq V$ and every element $e \in V \setminus B$:
$$f(A \cup \{e\}) - f(A) \ge f(B \cup \{e\}) - f(B)$$
The term $\Delta(e \mid S) \equiv f(S \cup \{e\}) - f(S)$ is the **marginal gain** of adding element $e$ to set $S$. The diminishing returns property states that adding an element to a smaller set $A$ yields an equal or greater marginal increase than adding that same element to a larger superset $B$. Submodular functions are the discrete combinatorial analogue of concave continuous functions.

---

### Q2: How is the Maximum Coverage problem formulated, and why is it NP-hard?
**Answer:**  
Given a universe $\mathcal{U} = \{0, \dots, n-1\}$, a collection of subsets $\mathcal{S} = \{S_0, \dots, S_{m-1}\}$ with $S_i \subseteq \mathcal{U}$, and a cardinality constraint $k \le m$:
$$\max_{A \subseteq \{0, \dots, m-1\}, |A| \le k} f(A) \equiv \left| \bigcup_{i \in A} S_i \right|$$
Maximum Coverage is NP-hard by reduction from the Set Cover decision problem. If we could solve Maximum Coverage in polynomial time for any $k$, we could find the minimum set cover by testing $k = 1, 2, \dots, m$ sequentially until $f(A) = |\mathcal{U}|$.

---

### Q3: What is the theoretical approximation guarantee of the Greedy algorithm for monotone submodular maximization under a cardinality constraint?
**Answer:**  
The Greedy algorithm achieves an approximation ratio of:
$$f(A_{\text{greedy}}) \ge \left(1 - \frac{1}{e}\right) f(A^*) \approx 0.6321 \cdot f(A^*)$$
where $A^*$ is the optimal subset of size $k$. Proven by Nemhauser, Wolsey, and Fisher (1978), this bound is mathematically optimal: unless $\text{P} = \text{NP}$, no polynomial-time algorithm can achieve an approximation ratio strictly greater than $(1 - 1/e)$ (Feige, 1998).

---

### Q4: Provide a sketch of the proof for the $(1 - 1/e)$ greedy submodular approximation guarantee.
**Answer:**  
Let $A_{t-1}$ be the greedy set of size $t-1$, and let $A^* = \{o_1, \dots, o_k\}$ be the optimal set. The optimal set covers at least $f(A^*) - f(A_{t-1})$ elements not yet covered by $A_{t-1}$. By submodularity and the pigeonhole principle:
$$\sum_{i=1}^k [f(A_{t-1} \cup \{o_i\}) - f(A_{t-1})] \ge f(A_{t-1} \cup A^*) - f(A_{t-1}) \ge f(A^*) - f(A_{t-1})$$
At least one element $o_i$ must yield a marginal gain $\ge \frac{1}{k} (f(A^*) - f(A_{t-1}))$. Because Greedy picks the element with the maximum possible marginal gain:
$$f(A_t) - f(A_{t-1}) \ge \frac{1}{k} (f(A^*) - f(A_{t-1}))$$
Rearranging gives the remaining suboptimality:
$$(f(A^*) - f(A_t)) \le \left(1 - \frac{1}{k}\right) (f(A^*) - f(A_{t-1}))$$
Applying this recurrence for all $k$ steps:
$$f(A^*) - f(A_k) \le \left(1 - \frac{1}{k}\right)^k (f(A^*) - f(\emptyset)) \le e^{-1} f(A^*)$$
$$\therefore f(A_k) \ge \left(1 - \frac{1}{e}\right) f(A^*)$$

---

### Q5: How does multiprocessing in Python differ between Windows and Linux, and what precautions are necessary?
**Answer:**  
- **Linux** uses `fork()`, which duplicates the parent process's memory space via copy-on-write without re-importing modules.
- **Windows** does not support `fork()`; it uses `spawn`, launching a fresh Python interpreter for each worker process and re-importing the main script.
- **Precautions**:
  1. Entry points must be protected with `if __name__ == '__main__':` to prevent infinite recursive process spawning.
  2. Functions dispatched to worker pools must be defined at the module top level so they can be pickled.
  3. Worker pools should be instantiated once and reused across trials to avoid paying the operating system's $~0.35$s process creation latency on every iteration.

---

### Q6: Define Speedup and Parallel Efficiency. Why does efficiency decay as worker counts increase?
**Answer:**  
- **Speedup**: $S_P = \frac{T_1}{T_P}$, where $T_1$ is single-core sequential execution time, and $T_P$ is parallel time on $P$ worker processes.
- **Parallel Efficiency**: $E_P = \frac{S_P}{P} = \frac{T_1}{P \cdot T_P}$.
- **Causes of Efficiency Decay**:
  1. **IPC Overhead**: Pickling task arguments and serializing return values across inter-process pipes.
  2. **Memory Bus Saturation**: Multiple cores contending for shared RAM bandwidth and L3 cache lines.
  3. **Load Imbalance**: Variations in task execution times causing faster workers to idle.
  4. **Operating System Scheduling**: Context switching and thread migration overhead across hardware hyperthreads.

---

### Q7: State Amdahl's Law and explain the physical significance of the serial fraction $s$.
**Answer:**  
Amdahl's Law models strong scaling (fixed total problem size). If fraction $P$ of a program is parallelizable and fraction $s = 1 - P$ is strictly serial:
$$S_{\text{Amdahl}}(N) = \frac{1}{s + \frac{1 - s}{N}} = \frac{1}{(1 - P) + \frac{P}{N}}$$
As processor count $N \to \infty$:
$$\lim_{N \to \infty} S_{\text{Amdahl}}(N) = \frac{1}{s} = \frac{1}{1 - P}$$
The serial fraction $s$ represents the unparallelizable bottleneck (e.g., initial disk I/O, IPC synchronization, final result reduction). Even if $s = 0.05$ (95% parallel), the maximum possible speedup can never exceed $1 / 0.05 = 20\times$, regardless of how many thousands of cores are provisioned.

---

### Q8: How does Gustafson-Barsis's Law differ from Amdahl's Law?
**Answer:**  
- **Amdahl's Law** assumes a **fixed workload** (Strong Scaling): as $N$ increases, the work per processor decreases, causing serial overhead to dominate.
- **Gustafson's Law** assumes a **scaled workload** (Weak Scaling): as processor count $N$ increases, the problem size is expanded proportionally to fully utilize the parallel hardware.
- **Formula**:
  $$S_{\text{Gustafson}}(N) = N - (1 - P)(N - 1) = s + P \cdot N$$
- Under Gustafson's Law, speedup grows linearly with $N$ with slope $P$. In empirical benchmarks on 32 cores with $P = 85.6\%$, Amdahl predicts a capped speedup of $5.87\times$, while Gustafson predicts a scaled speedup of $27.55\times$.

---

### Q9: How can empirical speedup data be used to estimate a system's serial fraction?
**Answer:**  
Using non-linear least squares regression (e.g., Levenberg-Marquardt via `scipy.optimize.curve_fit`), empirical measurements $(N_i, S_i)$ are fitted to the parameterized model:
$$S(N) = \frac{1}{(1 - P) + \frac{P}{N}}$$
The optimization minimizes $\sum_i (S_i - S_{\text{model}}(N_i, P))^2$ subject to $P \in [0, 1]$. In our experiments on the Large workload, fitting yielded $\hat{P} = 0.8564$ ($R^2 = 0.9973$), establishing an effective empirical serial fraction $\hat{s} = 14.36\%$.

---

### Q10: What is the Federated Optimization objective function, and how does Federated Averaging (FedAvg) optimize it?
**Answer:**  
Given $K$ clients, each possessing local dataset $\mathcal{D}_k$ of size $n_k$:
$$\min_{\boldsymbol{\theta}} f(\boldsymbol{\theta}) = \sum_{k=1}^K \frac{n_k}{n} F_k(\boldsymbol{\theta}), \quad \text{where } n = \sum_{k=1}^K n_k, \quad F_k(\boldsymbol{\theta}) = \frac{1}{n_k} \sum_{i \in \mathcal{D}_k} \ell(\boldsymbol{\theta}; x_i, y_i)$$
FedAvg optimizes this iteratively over communication rounds:
1. Server broadcasts global weights $\boldsymbol{\theta}_t$ to clients.
2. Each client runs $E$ local epochs of SGD on its local dataset $\mathcal{D}_k$: $\boldsymbol{\theta}_{t+1}^k \leftarrow \boldsymbol{\theta}_t - \eta \sum \nabla F_k$.
3. Clients upload updated weights $\boldsymbol{\theta}_{t+1}^k$ to the server.
4. Server computes the sample-weighted average: $\boldsymbol{\theta}_{t+1} = \sum_{k=1}^K \frac{n_k}{n} \boldsymbol{\theta}_{t+1}^k$.

---

### Q11: What is "client drift" in Federated Learning, and why does it occur on Non-IID data?
**Answer:**  
Client drift refers to local client models diverging away from the global optimal parameter vector during local training epochs.
- In **IID data**, each client's local loss surface is statistically identical: $\mathbb{E}[\nabla F_k(\boldsymbol{\theta})] = \nabla f(\boldsymbol{\theta})$, so local updates point toward the global optimum.
- In **Non-IID data** (e.g., label skew where Client 1 only has Class 0 and Client 2 only has Class 1), local minima diverge: $\boldsymbol{\theta}_k^* \neq \boldsymbol{\theta}^*$. Local SGD pulls models toward client-specific optima. When the server averages these drifted models, the resulting update can cause loss oscillations, slower convergence, and degraded test accuracy.

---

### Q12: Define Pareto Optimality and Pareto Stationarity for multi-objective optimization.
**Answer:**  
For multi-objective problem $\min_{\mathbf{x}} (f_1(\mathbf{x}), \dots, f_m(\mathbf{x}))$:
- **Pareto Dominance**: A point $\mathbf{x}$ dominates $\mathbf{y}$ ($\mathbf{x} \prec \mathbf{y}$) if $\forall i: f_i(\mathbf{x}) \le f_i(\mathbf{y})$ and $\exists j: f_j(\mathbf{x}) < f_j(\mathbf{y})$.
- **Pareto Optimality**: $\mathbf{x}^*$ is Pareto optimal if no $\mathbf{x}$ dominates $\mathbf{x}^*$.
- **Pareto Stationarity**: A point $\mathbf{x}^*$ is Pareto stationary if the convex hull of its individual objective gradients contains the zero vector:
  $$\mathbf{0} \in \text{conv}(\nabla f_1(\mathbf{x}^*), \dots, \nabla f_m(\mathbf{x}^*)) \iff \exists \boldsymbol{\alpha} \in \Delta^m \text{ s.t. } \sum_{i=1}^m \alpha_i \nabla f_i(\mathbf{x}^*) = \mathbf{0}$$
  where $\Delta^m = \{\boldsymbol{\alpha} \ge 0 \mid \sum \alpha_i = 1\}$. Pareto stationarity is the first-order necessary condition for multi-objective optimality.

---

### Q13: How does the Multiple Gradient Descent Algorithm (MGDA) find a common descent direction?
**Answer:**  
At any point $\mathbf{x}$, MGDA solves the minimum-norm problem on the convex hull of gradients:
$$\boldsymbol{\alpha}^* = \arg\min_{\boldsymbol{\alpha} \in \Delta^m} \left\| \sum_{i=1}^m \alpha_i \nabla f_i(\mathbf{x}) \right\|_2^2$$
Let $\mathbf{g}^* = \sum_{i=1}^m \alpha_i^* \nabla f_i(\mathbf{x})$:
1. If $\|\mathbf{g}^*\|_2 = 0$, $\mathbf{x}$ is Pareto stationary (descent terminates).
2. If $\|\mathbf{g}^*\|_2 > 0$, the vector $\mathbf{d} = -\mathbf{g}^*$ is guaranteed to be a descent direction for *all* objectives simultaneously:
   $$\langle \nabla f_i(\mathbf{x}), \mathbf{d} \rangle \le -\|\mathbf{g}^*\|_2^2 < 0 \quad \forall i \in \{1, \dots, m\}$$
   Taking step $\mathbf{x} \leftarrow \mathbf{x} + \eta \mathbf{d}$ decreases every objective without requiring manual tuning of scalar trade-off weights.

---

### Q14: Derive the analytical closed-form solution for MGDA with $m=2$ objectives.
**Answer:**  
For two gradients $\mathbf{g}_1 = \nabla f_1$ and $\mathbf{g}_2 = \nabla f_2$, the objective is:
$$\min_{\alpha \in [0, 1]} \|\alpha \mathbf{g}_1 + (1 - \alpha) \mathbf{g}_2\|_2^2 = \min_{\alpha \in [0, 1]} \alpha^2 \|\mathbf{g}_1 - \mathbf{g}_2\|^2 + 2\alpha (\mathbf{g}_1 - \mathbf{g}_2)^T \mathbf{g}_2 + \|\mathbf{g}_2\|^2$$
Differentiating with respect to $\alpha$ and setting to zero:
$$2\alpha \|\mathbf{g}_1 - \mathbf{g}_2\|^2 + 2(\mathbf{g}_1 - \mathbf{g}_2)^T \mathbf{g}_2 = 0 \implies \alpha = \frac{(\mathbf{g}_2 - \mathbf{g}_1)^T \mathbf{g}_2}{\|\mathbf{g}_1 - \mathbf{g}_2\|^2} = \frac{\|\mathbf{g}_2\|^2 - \mathbf{g}_1^T \mathbf{g}_2}{\|\mathbf{g}_1 - \mathbf{g}_2\|^2}$$
Projecting onto $[0, 1]$:
$$\alpha^* = \max\left(0.0, \min\left(1.0, \frac{\|\mathbf{g}_2\|^2 - \mathbf{g}_1^T \mathbf{g}_2}{\|\mathbf{g}_1 - \mathbf{g}_2\|^2}\right)\right)$$
Then $\boldsymbol{\alpha}^* = (\alpha^*, 1 - \alpha^*)$ and $\mathbf{g}^* = \alpha^* \mathbf{g}_1 + (1 - \alpha^*) \mathbf{g}_2$.

---

### Q15: Why does fixed linear scalarization (Weighted Sum) fail on non-convex Pareto fronts, and how does MGDA overcome this?
**Answer:**  
The weighted sum method minimizes $F(\mathbf{x}) = \sum \lambda_i f_i(\mathbf{x})$ with fixed $\lambda_i \ge 0$.
- **Failure on Non-Convex Fronts**: For non-convex Pareto fronts, solutions in the concave indentations of the front can *never* be the minimizer of any linear supporting hyperplane, regardless of the choice of $\boldsymbol{\lambda}$.
- **Sensitivity to Scale**: A task with a gradient magnitude $10\times$ larger will completely dominate the search direction.
- **MGDA Advantage**: MGDA does not optimize a static linear scalarization. It dynamically recalculates the min-norm convex combination $\boldsymbol{\alpha}^*$ at each step, naturally adapting to the local geometry and stopping only when Pareto stationarity is achieved.

---

### Q16: Explain the GradNorm algorithm for multi-task learning. What is the target gradient norm, and why is the normalization constraint needed?
**Answer:**  
In a multi-task network with shared parameters $\mathbf{W}$, the loss is $L_{\text{total}} = \sum_{i=1}^T w_i(t) L_i(t)$.
1. **Target Gradient Norm**: GradNorm defines the target gradient norm for task $i$ as:
   $$G_{\text{target}}^{(i)}(t) = \bar{G}_{\mathbf{W}}(t) \cdot [r_i(t)]^\alpha$$
   where $\bar{G}_{\mathbf{W}}(t) = \frac{1}{T} \sum_i w_i(t) \|\nabla_{\mathbf{W}} L_i(t)\|_2$ is the average gradient norm, and $r_i(t) = \frac{L_i(t) / L_i(0)}{\frac{1}{T} \sum_j (L_j(t) / L_j(0))}$ is the **relative inverse training rate**. If task $i$ trains slowly relative to its start, $r_i(t) > 1$, which increases its target gradient norm.
2. **Weight Update**: Task weights $w_i$ are updated via gradient descent on $L_{\text{grad}} = \sum_i |G_{\mathbf{W}}^{(i)}(t) - G_{\text{target}}^{(i)}(t)|$.
3. **Normalization Constraint**: After each update, weights are rescaled:
   $$w_i(t+1) \leftarrow T \cdot \frac{w_i(t+1)}{\sum_{j=1}^T w_j(t+1)}$$
   This decouples task weighting from global learning rate scaling, ensuring $\sum_{i=1}^T w_i = T$ and preventing task weights from drifting to zero or blowing up to infinity.

