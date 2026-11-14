# Track D: Parallel and Distributed Optimization — Mathematical Methodology

> **Course**: Optimization Techniques — Assignment 8  
> **Module**: `track_d_parallel_distributed_optimization/`  
> **Scope**: Submodular Maximization, Multiprocessing Parallelism, Amdahl/Gustafson Laws, Federated Learning (FedAvg), Multi-Objective Optimization (MGDA), and Multi-Task Balancing (GradNorm).

---

## 1. Submodular Optimization (Maximum Coverage)

### 1.1 Mathematical Definition & Properties
Let $V = \{0, 1, \dots, m-1\}$ be a finite ground set. A set function $f: 2^V \to \mathbb{R}$ is **submodular** if for all subsets $A \subseteq B \subseteq V$ and every element $e \in V \setminus B$:
$$f(A \cup \{e\}) - f(A) \ge f(B \cup \{e\}) - f(B)$$
This formalizes the **diminishing returns property**: the marginal gain $\Delta(e \mid S) \equiv f(S \cup \{e\}) - f(S)$ obtained by adding element $e$ to a set $S$ strictly decreases or remains constant as the base set grows larger.

Equivalent formulations include:
1. **Submodular Inequality**: For all $A, B \subseteq V$:
   $$f(A \cap B) + f(A \cup B) \le f(A) + f(B)$$
2. **Monotonicity**: $f$ is monotone non-decreasing if for all $A \subseteq B$:
   $$f(A) \le f(B)$$
3. **Normalized**: $f(\emptyset) = 0$.

### 1.2 The Maximum Coverage Problem
Given a universe of elements $\mathcal{U} = \{0, 1, \dots, n-1\}$, a collection of subsets $\mathcal{S} = \{S_0, S_1, \dots, S_{m-1}\}$ where each $S_i \subseteq \mathcal{U}$, and a cardinality budget $k \le m$:
$$\max_{A \subseteq \{0, \dots, m-1\}, |A| \le k} f(A) \equiv \left| \bigcup_{i \in A} S_i \right|$$
Maximum coverage is NP-hard (by reduction from Set Cover), monotone non-decreasing, and submodular.

### 1.3 The Greedy Selection Algorithm & Approximation Guarantee
- **Algorithm**:
  1. Initialize $A_0 = \emptyset$, covered set $C_0 = \emptyset$.
  2. For $t = 1, 2, \dots, k$:
     $$S^* = \arg\max_{S_i \in \mathcal{S} \setminus A_{t-1}} |S_i \setminus C_{t-1}|$$
     $$A_t = A_{t-1} \cup \{S^*\}, \quad C_t = C_{t-1} \cup S^*$$
- **Theoretical Guarantee (Nemhauser, Wolsey, & Fisher, 1978)**:
  For any monotone submodular function $f$ with $f(\emptyset) = 0$ under a cardinality constraint $|A| \le k$, the greedy algorithm produces a solution $A_{\text{greedy}}$ satisfying:
  $$f(A_{\text{greedy}}) \ge \left(1 - \frac{1}{e}\right) f(A^*) \approx 0.6321 \cdot f(A^*)$$
  where $A^*$ is the globally optimal subset.
- **Proof Sketch**:
  Let $A^* = \{o_1, \dots, o_k\}$. At step $t$, the optimal solution covers at least $f(A^*) - f(A_{t-1})$ remaining elements across its $k$ subsets. By the pigeonhole principle and submodularity, at least one subset must achieve a marginal gain of at least $\frac{1}{k} (f(A^*) - f(A_{t-1}))$. Hence:
  $$f(A_t) - f(A_{t-1}) \ge \frac{1}{k} (f(A^*) - f(A_{t-1})) \implies (f(A^*) - f(A_t)) \le \left(1 - \frac{1}{k}\right) (f(A^*) - f(A_{t-1}))$$
  Unrolling for $k$ steps:
  $$f(A^*) - f(A_k) \le \left(1 - \frac{1}{k}\right)^k (f(A^*) - f(A_0)) \le e^{-1} f(A^*)$$
  $$\therefore f(A_k) \ge \left(1 - \frac{1}{e}\right) f(A^*)$$

---

## 2. Parallel Computing & Multiprocessing Scaling

### 2.1 Multiprocessing Architecture on Windows
Unlike Unix-based systems which use `fork()`, Python on Windows creates new worker processes via `spawn`. Under `spawn`:
1. A fresh Python interpreter is launched for each worker.
2. The entry-point module is re-imported (requiring top-level picklable functions and `if __name__ == '__main__':` guards).
3. To eliminate per-trial process creation latency ($~0.35$s per worker), persistent worker pools (`mp.Pool(processes=P)`) are maintained across repeated benchmark iterations.

### 2.2 Metrics: Speedup and Efficiency
For a compute workload executing in time $T_1$ sequentially on 1 core and $T_P$ on $P$ worker processes:
1. **Speedup**:
   $$S_P = \frac{T_1}{T_P}$$
2. **Parallel Efficiency**:
   $$E_P = \frac{S_P}{P} = \frac{T_1}{P \cdot T_P} \in [0, 1]$$
   Ideal linear scaling yields $S_P = P$ and $E_P = 1.0$ ($100\%$). In real physical systems, inter-process communication (IPC) serialization, cache contention, operating system scheduling, and memory bus saturation degrade efficiency as $P$ increases.

---

## 3. Amdahl's Law vs. Gustafson's Law

### 3.1 Amdahl's Law (Strong Scaling / Fixed-Size Workload)
Amdahl's Law (1967) assumes that the total workload size remains fixed as processor count $N$ increases.
Let $P \in [0, 1]$ be the parallelizable fraction of the workload, and $s = 1 - P$ be the strictly serial fraction:
$$T(N) = s \cdot T_1 + \frac{P \cdot T_1}{N}$$
Dividing $T_1$ by $T(N)$ gives the theoretical speedup:
$$S_{\text{Amdahl}}(N) = \frac{1}{(1 - P) + \frac{P}{N}} = \frac{1}{s + \frac{1 - s}{N}}$$
- **Asymptotic Bound**:
  $$\lim_{N \to \infty} S_{\text{Amdahl}}(N) = \frac{1}{1 - P} = \frac{1}{s}$$
  *Example*: If a program is $90\%$ parallel ($s = 0.10$), the maximum theoretical speedup is strictly capped at $1 / 0.10 = 10\times$, even on an infinitely large supercomputer.

### 3.2 Gustafson-Barsis's Law (Weak Scaling / Scaled-Size Workload)
Gustafson and Barsis (1988) noted that in scientific computing, researchers scale the problem size proportionally with the available processor count $N$.
Assuming a parallel machine executes scaled work in time $T_N = s + P = 1$, the time required on a single sequential processor would be $T_1 = s + P \cdot N$.
$$S_{\text{Gustafson}}(N) = \frac{s + P \cdot N}{s + P} = s + P \cdot N = (1 - P) + P \cdot N = 1 + (N - 1)P = N - (1 - P)(N - 1)$$
- **Implication**: Speedup scales linearly with processor count $N$, provided the problem size is expanded to keep worker cores saturated.

### 3.3 Non-Linear Least Squares Fitting
Empirical speedup measurements $S_{\text{meas}}(N)$ are fitted to Amdahl's Law via Levenberg-Marquardt least squares:
$$\min_{P \in [0, 1]} \sum_{i=1}^K \left( S_{\text{meas}}(N_i) - \frac{1}{(1 - P) + P / N_i} \right)^2$$
yielding an empirical estimate of the serial fraction $\hat{s} = 1 - \hat{P}$.

---

## 4. Federated Averaging (FedAvg)

### 4.1 Federated Optimization Problem
In decentralized machine learning, $K$ edge clients collect local datasets $\mathcal{D}_k = \{(x_{k, i}, y_{k, i})\}_{i=1}^{n_k}$. The global objective minimizes the sample-weighted empirical risk:
$$\min_{\boldsymbol{\theta}} f(\boldsymbol{\theta}) = \sum_{k=1}^K \frac{n_k}{n} F_k(\boldsymbol{\theta}), \quad \text{where } n = \sum_{k=1}^K n_k$$
and $F_k(\boldsymbol{\theta}) = \frac{1}{n_k} \sum_{i=1}^{n_k} \ell(\boldsymbol{\theta}; x_{k, i}, y_{k, i})$ is the local loss function.

### 4.2 The FedAvg Protocol (McMahan et al., 2017)
In each communication round $r = 1, \dots, R$:
1. **Server Broadcast**: The central server transmits the current global model weights $\boldsymbol{\theta}_r$ to all clients $k \in \{1, \dots, K\}$.
2. **Local Client Computation**: Each client initializes local model $\boldsymbol{\theta}_{r, 0}^k = \boldsymbol{\theta}_r$ and performs $E$ local epochs of gradient descent with learning rate $\eta$:
   $$\boldsymbol{\theta}_{r, e+1}^k = \boldsymbol{\theta}_{r, e}^k - \eta \nabla F_k(\boldsymbol{\theta}_{r, e}^k)$$
3. **Client Upload**: Clients transmit their updated parameter vectors $\boldsymbol{\theta}_{r, E}^k$ back to the central server.
4. **Server Aggregation**: The server computes a weighted average proportional to local data volume:
   $$\boldsymbol{\theta}_{r+1} = \sum_{k=1}^K \frac{n_k}{n} \boldsymbol{\theta}_{r, E}^k$$

### 4.3 Client Drift in Non-IID Regimes
- **IID Data**: When data are identically and independently distributed across clients, $\mathbb{E}[\nabla F_k(\boldsymbol{\theta})] = \nabla f(\boldsymbol{\theta})$. Local gradients point toward the global minimum, and FedAvg exhibits rapid convergence near centralized rates.
- **Non-IID Label Skew**: When clients possess distinct label distributions, local minima diverge: $\boldsymbol{\theta}_k^* \neq \boldsymbol{\theta}^*$. Local updates pull models toward local client optima, inducing **client drift**:
  $$\text{Drift}(r) = \frac{1}{K} \sum_{k=1}^K \| \boldsymbol{\theta}_{r, E}^k - \boldsymbol{\theta}_r \|_2$$
  This causes loss oscillations and asymptotic suboptimality unless mitigated by smaller learning rates or proximal terms (e.g., FedProx).

---

## 5. Multiple Gradient Descent Algorithm (MGDA)

### 5.1 Multi-Objective Optimization & Pareto Stationarity
Consider optimizing $m$ competing objective functions simultaneously:
$$\min_{\mathbf{x} \in \mathbb{R}^d} \mathbf{F}(\mathbf{x}) = (f_1(\mathbf{x}), f_2(\mathbf{x}), \dots, f_m(\mathbf{x}))$$
- **Pareto Dominance**: A point $\mathbf{x}$ dominates $\mathbf{y}$ ($\mathbf{x} \prec \mathbf{y}$) if $f_i(\mathbf{x}) \le f_i(\mathbf{y})$ for all $i$ and $f_j(\mathbf{x}) < f_j(\mathbf{y})$ for at least one $j$.
- **Pareto Optimality**: A point $\mathbf{x}^*$ is Pareto optimal if no point dominates it.
- **Pareto Stationarity**: A necessary condition for Pareto optimality (analogous to $\nabla f(\mathbf{x}) = \mathbf{0}$ in scalar optimization). A point $\mathbf{x}^*$ is Pareto stationary if the convex hull of its gradients contains the origin:
  $$\mathbf{0} \in \text{conv}(\nabla f_1(\mathbf{x}^*), \dots, \nabla f_m(\mathbf{x}^*)) \iff \exists \boldsymbol{\alpha} \in \Delta^m \text{ s.t. } \sum_{i=1}^m \alpha_i \nabla f_i(\mathbf{x}^*) = \mathbf{0}$$
  where $\Delta^m = \{\boldsymbol{\alpha} \in \mathbb{R}^m \mid \sum \alpha_i = 1, \alpha_i \ge 0\}$.

### 5.2 MGDA Min-Norm Simplex Formulation (Désidéri, 2012)
At any point $\mathbf{x}$, MGDA seeks the minimum-norm vector in the convex hull of gradients:
$$\boldsymbol{\alpha}^* = \arg\min_{\boldsymbol{\alpha} \in \Delta^m} \left\| \sum_{i=1}^m \alpha_i \nabla f_i(\mathbf{x}) \right\|_2^2$$
Let $\mathbf{g}^* = \sum_{i=1}^m \alpha_i^* \nabla f_i(\mathbf{x})$.
1. If $\|\mathbf{g}^*\|_2 = 0$, $\mathbf{x}$ is Pareto stationary; no direction can decrease one objective without increasing another.
2. If $\|\mathbf{g}^*\|_2 > 0$, the descent direction $\mathbf{d} = -\mathbf{g}^*$ is a **common descent direction**:
   $$\langle \nabla f_i(\mathbf{x}), \mathbf{d} \rangle \le -\|\mathbf{g}^*\|_2^2 < 0 \quad \forall i \in \{1, \dots, m\}$$
   Taking a step $\mathbf{x} \leftarrow \mathbf{x} + \eta \mathbf{d}$ strictly decreases ALL objectives simultaneously!

### 5.3 Closed-Form Analytical Solution for $m=2$ Objectives
For two gradients $\mathbf{g}_1 = \nabla f_1, \mathbf{g}_2 = \nabla f_2$:
$$\min_{\alpha \in [0, 1]} \|\alpha \mathbf{g}_1 + (1 - \alpha) \mathbf{g}_2\|^2$$
Differentiating with respect to $\alpha$ and setting to zero:
$$\alpha = \frac{(\mathbf{g}_2 - \mathbf{g}_1)^T \mathbf{g}_2}{\|\mathbf{g}_1 - \mathbf{g}_2\|^2} = \frac{\|\mathbf{g}_2\|^2 - \mathbf{g}_1^T \mathbf{g}_2}{\|\mathbf{g}_1 - \mathbf{g}_2\|^2}$$
Clamped to the unit simplex:
$$\alpha^* = \max\left(0, \min\left(1, \frac{\|\mathbf{g}_2\|^2 - \mathbf{g}_1^T \mathbf{g}_2}{\|\mathbf{g}_1 - \mathbf{g}_2\|^2}\right)\right)$$

---

## 6. GradNorm: Multi-Task Loss Balancing

### 6.1 Motivation: Gradient Imbalances in Multi-Task Learning
In multi-task neural networks with shared representation parameters $\mathbf{W}$ and task-specific heads, the total loss is a weighted sum:
$$L_{\text{total}}(t) = \sum_{i=1}^T w_i(t) L_i(t)$$
Standard uniform weighting ($w_i = 1$) fails when tasks have disparate loss scales or learning dynamics: the easiest task or the task with the largest gradient magnitude dominates the shared representation, starving more challenging tasks.

### 6.2 The GradNorm Algorithm (Chen et al., ICML 2018)
GradNorm dynamically tunes task weights $w_i(t)$ at each training step $t$:
1. **Compute Shared Gradient Norms**:
   $$G_{\mathbf{W}}^{(i)}(t) = \| \nabla_{\mathbf{W}} (w_i(t) L_i(t)) \|_2 = w_i(t) \| \nabla_{\mathbf{W}} L_i(t) \|_2$$
2. **Compute Average Gradient Norm**:
   $$\bar{G}_{\mathbf{W}}(t) = \frac{1}{T} \sum_{i=1}^T G_{\mathbf{W}}^{(i)}(t)$$
3. **Compute Relative Inverse Training Rate**:
   $$\tilde{L}_i(t) = \frac{L_i(t)}{L_i(0)}, \quad r_i(t) = \frac{\tilde{L}_i(t)}{\frac{1}{T} \sum_{j=1}^T \tilde{L}_j(t)}$$
   $r_i(t) > 1$ signifies that task $i$ is training slower than average (lagging task).
4. **Target Gradient Norm**:
   $$G_{\text{target}}^{(i)}(t) = \bar{G}_{\mathbf{W}}(t) \cdot [r_i(t)]^\alpha$$
   where $\alpha > 0$ (typically $\alpha = 1.5$) governs the strength of restoring forces.
5. **GradNorm Loss & Weight Update**:
   $$L_{\text{grad}}(w_1, \dots, w_T) = \sum_{i=1}^T \left| G_{\mathbf{W}}^{(i)}(t) - G_{\text{target}}^{(i)}(t) \right|$$
   Updating $w_i$ via gradient descent on $L_{\text{grad}}$:
   $$\frac{\partial L_{\text{grad}}}{\partial w_i} = \text{sign}\left(G_{\mathbf{W}}^{(i)}(t) - G_{\text{target}}^{(i)}(t)\right) \cdot \| \nabla_{\mathbf{W}} L_i(t) \|_2$$
   $$w_i(t+1) = w_i(t) - \eta_{\text{grad}} \frac{\partial L_{\text{grad}}}{\partial w_i}$$
6. **Renormalization Constraint**:
   $$w_i(t+1) \leftarrow T \cdot \frac{w_i(t+1)}{\sum_{j=1}^T w_j(t+1)}$$
   guaranteeing $\sum_{i=1}^T w_i = T$ and preventing weight explosion or collapse.

