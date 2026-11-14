# Track A: Continuous Optimization — Academic Viva Defense Questions & Model Answers

> **Course**: Optimization Techniques (CS / AI)  
> **Assignment 8**: Optimize Anything — 14-Day Vibe-Coding Challenge  
> **Module**: Track A Viva Examination Preparation (16 Core Academic Questions)

---

### Q1. What is the fundamental theoretical difference between first-order and second-order optimization methods?
**Model Answer:**
First-order methods (e.g., Gradient Descent, SGD, Adam) approximate the objective function locally using a first-order Taylor expansion:
$$f(x + \Delta x) \approx f(x) + \nabla f(x)^T \Delta x$$
They compute only directional slope information, making updates proportional to the negative gradient $-\eta \nabla f(x)$. Their per-iteration computational complexity is $\mathcal{O}(d)$, but their convergence rate is at best linear ($\mathcal{O}(1/t)$ or $\mathcal{O}(1/t^2)$ with Nesterov acceleration).

Second-order methods (e.g., Newton-Raphson, Gauss-Newton) construct a local quadratic model incorporating curvature via the Hessian matrix:
$$f(x + \Delta x) \approx f(x) + \nabla f(x)^T \Delta x + \frac{1}{2} \Delta x^T \nabla^2 f(x) \Delta x$$
Setting the gradient of this approximation to zero yields the step $\Delta x = -[\nabla^2 f(x)]^{-1} \nabla f(x)$. Second-order methods exhibit **quadratic convergence** ($\|e_{t+1}\| \le M \|e_t\|^2$), doubling the number of significant correct digits each iteration. However, they incur $\mathcal{O}(d^2)$ memory and $\mathcal{O}(d^3)$ computational inversion cost.

---

### Q2. Why does standard Newton's method fail or behave erratically on non-convex landscapes, and how does Levenberg-Marquardt spectral damping resolve this?
**Model Answer:**
Standard Newton's method solves $\nabla^2 f(x) \Delta x = -\nabla f(x)$. If the Hessian $\nabla^2 f(x)$ has negative eigenvalues (e.g. near saddle points or concave regions), the Newton step points in an **ascent** direction rather than a descent direction, causing divergence or convergence to local maxima. Furthermore, if the Hessian is near-singular ($\det \nabla^2 f \approx 0$), the step length $\|\Delta x\|$ explodes.

Levenberg-Marquardt spectral damping modifies the linear system to:
$$(\nabla^2 f(x) + \lambda_t I) \Delta x = -\nabla f(x)$$
By computing the minimum eigenvalue $\lambda_{\min}$, we select $\lambda_t = \max(0, -\lambda_{\min} + \delta)$ with $\delta > 0$. This ensures:
1. The regularized matrix $H_{\text{reg}} = \nabla^2 f(x) + \lambda_t I$ is strictly positive definite ($\lambda_i(H_{\text{reg}}) \ge \delta > 0$).
2. The step is guaranteed to be a descent direction: $\nabla f(x)^T \Delta x = -\nabla f(x)^T H_{\text{reg}}^{-1} \nabla f(x) < 0$.
3. When curvature is degenerate, the method smoothly transitions into gradient descent with step size $1/\lambda_t$.

---

### Q3. Explain the Gauss-Newton approximation for non-linear least squares. Why does it omit the second derivative of the residuals?
**Model Answer:**
For non-linear least squares $S(\beta) = \frac{1}{2} \sum_{i=1}^m r_i(\beta)^2$, the exact Hessian is:
$$\nabla^2 S(\beta) = J(\beta)^T J(\beta) + \sum_{i=1}^m r_i(\beta) \nabla^2 r_i(\beta)$$
where $J(\beta)$ is the Jacobian of residuals. Gauss-Newton drops the second term $\sum r_i(\beta) \nabla^2 r_i(\beta)$, approximating $\nabla^2 S \approx J^T J$. This omission is theoretically justified by two conditions:
1. **Small Residual Assumption**: Near the optimal solution of a well-specified model, the residuals $r_i(\beta^*) \approx 0$, making the second term negligible.
2. **Near-Linear Residuals**: If the residuals $r_i(\beta)$ are approximately affine in the parameter neighbourhood, $\nabla^2 r_i(\beta) \approx \mathbf{0}$.

The primary practical advantage is computational: calculating $J^T J$ requires only first derivatives of $r_i$, eliminating the need to evaluate $m$ distinct $p \times p$ second-derivative Hessian tensors, while guaranteeing that $J^T J$ is always positive semi-definite.

---

### Q4. How does Polyak Heavy-Ball momentum differ from Nesterov Accelerated Gradient (NAG)?
**Model Answer:**
Both methods use a velocity vector $v_t$ to dampen oscillations, but evaluate gradients at different points:
- **Polyak Heavy-Ball**: Computes the gradient at the current position $\theta_t$:
  $$v_{t+1} = \beta v_t + \eta \nabla f(\theta_t), \quad \theta_{t+1} = \theta_t - v_{t+1}$$
- **Nesterov Accelerated Gradient**: Applies the momentum step *first* to reach an anticipated "look-ahead" point $\theta_{\text{look}} = \theta_t - \beta v_t$, and evaluates the gradient there:
  $$v_{t+1} = \beta v_t + \eta \nabla f(\theta_t - \beta v_t), \quad \theta_{t+1} = \theta_t - v_{t+1}$$

**Theoretical Consequence**: Polyak momentum acts as a simple low-pass filter on past gradients. NAG acts as a predictive controller: if the momentum is carrying the parameters uphill or towards an overshoot, $\nabla f(\theta_{\text{look}})$ detects the rising slope in advance and applies an opposing corrective brake. This improves the theoretical convergence rate on convex functions from $\mathcal{O}(1/t)$ to the optimal lower complexity bound $\mathcal{O}(1/t^2)$.

---

### Q5. What is the condition number of an objective function, and how does it dictate gradient descent convergence?
**Model Answer:**
For a twice-differentiable function, the condition number $\kappa$ is defined as the ratio of the largest to smallest eigenvalues of the Hessian matrix:
$$\kappa = \frac{\lambda_{\max}(\nabla^2 f)}{\lambda_{\min}(\nabla^2 f)} = \frac{L}{\mu}$$
where $L$ is the Lipschitz constant of the gradient and $\mu$ is the strong convexity parameter.

For standard Gradient Descent with optimal step size $\eta = \frac{2}{L + \mu}$, the error contraction per step is bounded by:
$$\|x_{t+1} - x^*\|_2 \le \left( \frac{\kappa - 1}{\kappa + 1} \right) \|x_t - x^*\|_2$$
- If $\kappa \approx 1$ (spherical contours), $\frac{\kappa - 1}{\kappa + 1} \approx 0$, and convergence occurs in a single step.
- If $\kappa \gg 1$ (ill-conditioned, elongated valleys like Rosenbrock), $\frac{\kappa - 1}{\kappa + 1} \to 1$, forcing tiny step sizes to prevent transverse oscillations across steep canyon walls, causing severe slowing along the longitudinal ridge.

---

### Q6. Why was AdaGrad's accumulator modified by RMSProp, and how does Adam build upon both?
**Model Answer:**
- **AdaGrad's Flaw**: AdaGrad accumulates squared gradients monotonically: $G_t = G_{t-1} + g_t^2$. Because every term is non-negative, $G_t$ grows unbounded. Consequently, the effective learning rate $\frac{\eta}{\sqrt{G_t} + \epsilon}$ decays prematurely to zero, halting learning early before reaching minima in non-convex neural net landscapes.
- **RMSProp's Solution**: Replaces the indefinite sum with an exponentially decaying moving average: $v_t = \beta v_{t-1} + (1 - \beta) g_t^2$. This allows $v_t$ to adapt dynamically to recent gradient magnitudes rather than the entire historical trajectory.
- **Adam's Synthesis**: Combines RMSProp's adaptive second-moment scaling ($v_t$) with Polyak's first-moment velocity ($m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t$). Additionally, Adam introduces analytical **bias-correction factors** ($\hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \hat{v}_t = \frac{v_t}{1 - \beta_2^t}$) to counteract the zero-initialization bias in early iterations when $m_0 = \mathbf{0}, v_0 = \mathbf{0}$.

---

### Q7. Explain the mathematical relationship between the Empirical Fisher Information Matrix and the Hessian of the Negative Log-Likelihood.
**Model Answer:**
Let $\ell_i(\theta) = -\log p(y_i \mid x_i, \theta)$ be the sample negative log-likelihood.
- The **True Hessian** is the average second derivative:
  $$H(\theta) = \frac{1}{N} \sum_{i=1}^N \nabla_\theta^2 \ell_i(\theta)$$
- The **Empirical Fisher Information Matrix** is the average outer product of sample gradients:
  $$F_{\text{emp}}(\theta) = \frac{1}{N} \sum_{i=1}^N \nabla_\theta \ell_i(\theta) \nabla_\theta \ell_i(\theta)^T$$

By the Fisher Information Identity, when expectations are taken over the model distribution $p(y \mid x, \theta)$, the expected Fisher and expected Hessian are identical:
$$\mathbb{E}_{y \sim p(y \mid x, \theta)} [-\nabla_\theta^2 \log p(y \mid x, \theta)] = \mathbb{E}_{y \sim p(y \mid x, \theta)} [\nabla_\theta \log p(y \mid x, \theta) \nabla_\theta \log p(y \mid x, \theta)^T]$$

In our binary logistic regression experiment:
- At $\theta = \mathbf{0}$, predicted probabilities are uniform ($p_i = 0.5$). Since $(y_i - p_i)^2 = 0.25$ and $p_i(1 - p_i) = 0.25$, $F_{\text{emp}}(\mathbf{0})$ and $H(\mathbf{0})$ are **mathematically identical**.
- Away from $\theta = \mathbf{0}$, empirical sample residuals introduce differences. However, $F_{\text{emp}}$ is guaranteed to be positive semi-definite (as a sum of outer products), whereas the unregularized empirical Hessian can become indefinite.

---

### Q8. What is Pearlmutter's $\mathcal{R}\{\cdot\}$ technique for Hessian-Vector Products (HVP), and why is it crucial for scaling second-order methods?
**Model Answer:**
Explicitly forming a Hessian matrix for a neural network with $d = 10^7$ parameters would require storing $10^{14}$ floats (400 Terabytes), which is intractable. However, many optimization algorithms (such as Truncated Newton, Conjugate Gradient, and Natural Gradient) only require evaluating the matrix-vector product $H v$ for an arbitrary vector $v \in \mathbb{R}^d$.

Pearlmutter (1994) defined the operator:
$$\mathcal{R}_v \{ f(\theta) \} = \left. \frac{d}{d\epsilon} f(\theta + \epsilon v) \right|_{\epsilon=0}$$
Applying this operator to the gradient vector $\nabla f(\theta)$ yields:
$$\mathcal{R}_v \{ \nabla f(\theta) \} = \left. \frac{d}{d\epsilon} \nabla f(\theta + \epsilon v) \right|_{\epsilon=0} = \nabla^2 f(\theta) v$$
Numerically, this can be approximated using centered directional finite differences:
$$H v \approx \frac{\nabla f(\theta + \epsilon v) - \nabla f(\theta - \epsilon v)}{2\epsilon}$$
This computes $H v$ in $\mathcal{O}(d)$ time and memory using only two gradient evaluations, completely bypassing the instantiation of the $\mathcal{O}(d^2)$ Hessian matrix.

---

### Q9. What does "Decoupled Backpropagation" mean in modular deep learning design, and why is it preferable to hardcoding parameter updates inside layer methods?
**Model Answer:**
Decoupled backpropagation enforces strict separation between:
1. **Gradient Computation (Automatic Differentiation)**: Calculating exact analytical partial derivatives $\frac{\partial \mathcal{L}}{\partial W_l}, \frac{\partial \mathcal{L}}{\partial b_l}$ via the chain rule. This depends solely on layer architecture, activations, and loss functions.
2. **Parameter Update Mechanics (Optimizer)**: Applying algorithms such as SGD, Adam, or weight decay to advance parameters $\theta_{t+1} \leftarrow \theta_t + \Delta \theta_t$.

**Advantages**:
- **Modularity & Reusability**: The same network forward/backward code can be paired with any optimizer (GD, NAG, Adam, L-BFGS) without touching layer definitions.
- **Verification Integrity**: Enables independent finite-difference checking of the backward pass alone before introducing optimizer state dynamics.
- **Architectural Parity**: Matches industry standards (e.g., PyTorch's separation of `loss.backward()` and `optimizer.step()`).

---

### Q10. How does finite-difference gradient checking work, and what relative error threshold indicates an error-free analytical implementation?
**Model Answer:**
Centered finite differences approximate the partial derivative with respect to coordinate $\theta_i$ using step size $\epsilon \approx 10^{-5}$:
$$g_{\text{num}, i} = \frac{\mathcal{L}(\theta + \epsilon e_i) - \mathcal{L}(\theta - \epsilon e_i)}{2\epsilon}$$
Centered differences have truncation error $\mathcal{O}(\epsilon^2)$, whereas forward differences have $\mathcal{O}(\epsilon)$.

The relative L2 error norm is computed as:
$$\text{RelError} = \frac{\|g_{\text{analytical}} - g_{\text{num}}\|_2}{\|g_{\text{analytical}}\|_2 + \|g_{\text{num}}\|_2 + 10^{-12}}$$
- $\text{RelError} < 10^{-7}$: Analytical gradient is correct (within floating-point precision limits).
- $\text{RelError} \in [10^{-4}, 10^{-6}]$: Possible minor bug or non-smooth activation kinks.
- $\text{RelError} > 10^{-3}$: Definite implementation bug in the chain rule or transpose dimensions.
Our implementation achieved **$4.00 \times 10^{-12}$**, confirming mathematical precision.

---

### Q11. Why does Mini-Batch Gradient Descent reduce gradient variance as $O(\sigma^2 / B)$? Prove this using basic probability.
**Model Answer:**
Let each sample gradient $g_i = \nabla f_i(\theta)$ be an independent, identically distributed random vector with mean $\mathbb{E}[g_i] = \nabla f(\theta)$ and covariance $\operatorname{Cov}(g_i) = \Sigma$ where $\operatorname{Tr}(\Sigma) = \sigma^2$.

The mini-batch gradient estimator is the sample average:
$$\bar{g} = \frac{1}{B} \sum_{i=1}^B g_i$$
By linearity of expectation:
$$\mathbb{E}[\bar{g}] = \frac{1}{B} \sum_{i=1}^B \mathbb{E}[g_i] = \nabla f(\theta) \quad (\text{unbiased})$$
By properties of variance for independent random variables:
$$\operatorname{Cov}(\bar{g}) = \operatorname{Cov}\left( \frac{1}{B} \sum_{i=1}^B g_i \right) = \frac{1}{B^2} \sum_{i=1}^B \operatorname{Cov}(g_i) = \frac{1}{B^2} (B \Sigma) = \frac{1}{B} \Sigma$$
Taking the trace:
$$\mathrm{Var}(\bar{g}) = \operatorname{Tr}(\operatorname{Cov}(\bar{g})) = \frac{\operatorname{Tr}(\Sigma)}{B} = \frac{\sigma^2}{B}$$
This proves that empirical variance decreases inversely with batch size $B$.

---

### Q12. On the XOR problem, why did Batch Gradient Descent stall at 50% accuracy while Momentum and Adam converged to 100%?
**Model Answer:**
XOR is a non-linearly separable problem requiring non-linear hidden representations. Its loss surface possesses a well-documented plateau/saddle point near the origin where the network outputs a constant prediction $\hat{y}_i \approx 0.5$, yielding a loss of $\approx 0.125$ and classification accuracy of 50%.

- **Batch GD Stalling**: At this plateau, gradients $\nabla \mathcal{L}$ become vanishingly small ($\|\nabla \mathcal{L}\| \approx 0$). Without inertia, Batch GD takes infinitesimal steps and terminates prematurely or stalls within the iteration budget.
- **Momentum & Adam Escape**:
  - Momentum's velocity buffer $v_t = \beta v_{t-1} + \eta g_t$ integrates past gradient vectors along consistent directions, building sufficient kinetic energy to traverse flat saddles.
  - Adam's coordinate scaling divides by $\sqrt{v_t} + \epsilon$. When gradients along plateau coordinates are uniformly small, $\sqrt{v_t}$ is also tiny, dynamically magnifying the effective step size $\frac{\eta}{\sqrt{v_t} + \epsilon}$, allowing rapid escape.

---

### Q13. What is the Secant Equation in Quasi-Newton methods, and how does the BFGS formula satisfy it?
**Model Answer:**
In Quasi-Newton methods, we seek an approximation $B_{k+1}$ to the inverse Hessian $H^{-1}$ that satisfies the **Secant Equation**:
$$B_{k+1} y_k = s_k$$
where $s_k = \theta_{k+1} - \theta_k$ is the parameter step and $y_k = \nabla f(\theta_{k+1}) - \nabla f(\theta_k)$ is the change in gradient.

The BFGS update is given by:
$$B_{k+1} = \left( I - \rho_k s_k y_k^T \right) B_k \left( I - \rho_k y_k s_k^T \right) + \rho_k s_k s_k^T, \quad \rho_k = \frac{1}{y_k^T s_k}$$
Multiplying by $y_k$:
$$B_{k+1} y_k = \left( I - \rho_k s_k y_k^T \right) B_k \left( y_k - \rho_k y_k (s_k^T y_k) \right) + \rho_k s_k (s_k^T y_k)$$
Since $\rho_k (s_k^T y_k) = 1$, the inner term $y_k - y_k = \mathbf{0}$, eliminating the left term entirely.
The right term simplifies to:
$$B_{k+1} y_k = \rho_k s_k (y_k^T s_k) = s_k$$
Thus, BFGS satisfies the secant equation exactly while maintaining positive definiteness whenever $y_k^T s_k > 0$.

---

### Q14. What are the Robbins-Monro conditions, and why are they necessary for Stochastic Gradient Descent to converge to a stationary point?
**Model Answer:**
For SGD with diminishing step sizes $\eta_t$, the Robbins-Monro conditions require:
1. $\sum_{t=1}^\infty \eta_t = \infty$ (Step sizes must not decay too quickly; the optimizer must be capable of traveling arbitrary distances to reach the optimum regardless of initial distance).
2. $\sum_{t=1}^\infty \eta_t^2 < \infty$ (Step sizes must decay sufficiently fast to extinguish stochastic variance $\sum \eta_t^2 \sigma^2 < \infty$ and prevent unbounded random walk oscillations).

If a constant step size $\eta$ is used, SGD does not converge to the exact stationary point $\nabla f(x^*) = 0$; instead, it enters a limit cycle or bounded variance ball centered around the optimum:
$$\mathbb{E}[\|x_t - x^*\|^2] \le \frac{\eta \sigma^2}{2\mu}$$

---

### Q15. In non-convex optimization, what is a strict saddle point, and which algorithms can efficiently escape it?
**Model Answer:**
A stationary point $x_0$ ($\nabla f(x_0) = \mathbf{0}$) is a **strict saddle point** if the Hessian $\nabla^2 f(x_0)$ has at least one strictly negative eigenvalue ($\lambda_{\min}(\nabla^2 f) < 0$). The corresponding eigenvector $v_{\text{neg}}$ defines a direction of negative curvature along which $f$ decreases.

- **Standard GD**: If initialized exactly on the stable manifold of the saddle point, GD remains stuck because $\nabla f(x_0) = \mathbf{0}$.
- **Perturbed GD / SGD**: Stochastic gradient noise introduces random perturbations along $v_{\text{neg}}$, allowing SGD to escape strict saddles almost surely in polynomial time (Ge et al., 2015).
- **Curvature / Trust-Region Methods**: Algorithms computing the minimum eigenvalue vector $v_{\text{neg}}$ can take an explicit step $\Delta x = -\operatorname{sgn}(\nabla f^T v_{\text{neg}}) v_{\text{neg}}$, directly descending along the negative curvature ridge.

---

### Q16. How does your Track A implementation directly satisfy the compulsory requirements of Assignment 8?
**Model Answer:**
Track A satisfies all core requirements of Chapter 6 / continuous optimization in the syllabus:
1. **Algorithmic Coverage**: Implements all 8 required first-order optimizers (Batch GD, SGD, Mini-batch, Momentum, NAG, AdaGrad, RMSProp, Adam) and 2 second-order optimizers (spectral Levenberg-Marquardt Newton, Gauss-Newton).
2. **Decoupled Architecture**: Strict mathematical isolation of forward/backward propagation from optimizer step logic, verified against finite differences to $4.00 \times 10^{-12}$ relative error.
3. **Curvature Approximations**: Empirical Fisher Information vs. NLL Hessian, BFGS low-rank updates, and Pearlmutter HVP.
4. **Empirical Benchmarking**: Systematic evaluation across 5 distinct mathematical landscapes with reproducible JSON, CSV, and markdown summaries.
5. **Sensitivity & Noise Studies**: Rigorous learning rate sweeps ($\eta$) and empirical proof of mini-batch variance decay $\mathcal{O}(\sigma^2/B)$.
6. **Publication Visualizations**: Six high-resolution plots generated via Matplotlib adhering to academic standards.

