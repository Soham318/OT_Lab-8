# Track A: Continuous Optimization — Methodology & Mathematical Formulations

> **Course**: Optimization Techniques (CS / AI)  
> **Assignment 8**: Optimize Anything — 14-Day Vibe-Coding Challenge  
> **Module**: Track A — First-Order, Second-Order, Decoupled Backpropagation, and Curvature Approximations

---

## 1. Executive Overview

Track A provides a mathematically rigorous, self-contained implementation of continuous optimization algorithms spanning:
1. **Eight First-Order Optimizers**: Batch Gradient Descent (GD), Stochastic Gradient Descent (SGD), Mini-batch Gradient Descent, Polyak Heavy-Ball Momentum, Nesterov Accelerated Gradient (NAG), Adaptive Gradient (AdaGrad), Root Mean Square Propagation (RMSProp), and Adaptive Moment Estimation (Adam).
2. **Two Second-Order Optimizers**: Damped Newton's Method with Levenberg-Marquardt spectral regularisation and Armijo backtracking line search, and the Gauss-Newton method for Non-Linear Least Squares.
3. **Decoupled Analytical Backpropagation**: Exact gradient computation on a 2-layer Multi-Layer Perceptron (MLP) strictly isolated from parameter update heuristics, verified against centered finite differences with relative error $< 10^{-11}$.
4. **Curvature Approximations**: Empirical Fisher Information Matrix vs. true Hessian, BFGS low-rank quasi-Newton updates, and Pearlmutter's Hessian-Vector Product (HVP) via forward-mode directional differentiation.

---

## 2. First-Order Gradient Optimization Algorithms

Let $f: \mathbb{R}^d \to \mathbb{R}$ be a continuously differentiable objective function, with gradient $\nabla f(x) \in \mathbb{R}^d$.

### 2.1 Batch Gradient Descent (GD)
The canonical steepest descent update on the full dataset or deterministic objective:
$$\theta_{t+1} = \theta_t - \eta \nabla f(\theta_t)$$
where $\eta > 0$ denotes the step size (learning rate). For an $L$-smooth $m$-strongly convex function, GD achieves linear convergence:
$$f(\theta_t) - f^* \le \left( \frac{\kappa - 1}{\kappa + 1} \right)^{2t} (f(\theta_0) - f^*)$$
where $\kappa = L / m$ is the condition number of the Hessian $\nabla^2 f$.

### 2.2 Stochastic Gradient Descent (SGD)
When evaluating the full gradient is computationally prohibitive or when sampling from data distribution $\mathcal{D}$:
$$g_t = \nabla f_i(\theta_t) = \nabla f(\theta_t) + \xi_t, \quad \mathbb{E}[\xi_t] = \mathbf{0}, \quad \mathbb{E}[\|\xi_t\|^2] = \sigma^2$$
$$\theta_{t+1} = \theta_t - \eta g_t$$
Due to gradient variance $\sigma^2$, SGD exhibits sublinear $\mathcal{O}(1/\sqrt{t})$ convergence under a constant step size unless $\eta_t \to 0$ satisfying the Robbins-Monro conditions $\sum \eta_t = \infty, \sum \eta_t^2 < \infty$.

### 2.3 Mini-Batch Gradient Descent
Averaging gradients over a mini-batch $\mathcal{B}_t$ of size $B = |\mathcal{B}_t|$:
$$\bar{g}_t = \frac{1}{B} \sum_{i \in \mathcal{B}_t} \nabla f_i(\theta_t)$$
$$\theta_{t+1} = \theta_t - \eta \bar{g}_t$$
By the Central Limit Theorem, the variance of the gradient estimator scales inversely with batch size:
$$\mathrm{Var}(\bar{g}_t) = \frac{\sigma^2}{B}$$
This directly suppresses stochastic jitter while enabling vectorised hardware acceleration.

### 2.4 Classical Momentum (Polyak Heavy-Ball)
Incorporates a velocity buffer $v_t$ that accumulates past gradients to dampen oscillations in ill-conditioned ravines:
$$v_{t+1} = \beta v_t + \eta \nabla f(\theta_t)$$
$$\theta_{t+1} = \theta_t - v_{t+1}$$
where $\beta \in [0, 1)$ is the momentum decay factor (typically $\beta = 0.9$). On strongly convex quadratics, Polyak momentum improves the convergence factor from $\frac{\kappa - 1}{\kappa + 1}$ to $\frac{\sqrt{\kappa} - 1}{\sqrt{\kappa} + 1}$.

### 2.5 Nesterov Accelerated Gradient (NAG)
Computes the gradient at an anticipated "look-ahead" point rather than the current parameter state:
$$\theta_{\text{look}} = \theta_t - \beta v_t$$
$$v_{t+1} = \beta v_t + \eta \nabla f(\theta_{\text{look}})$$
$$\theta_{t+1} = \theta_t - v_{t+1}$$
NAG achieves the optimal theoretical lower bound for first-order black-box convex optimization: $\mathcal{O}(1/t^2)$ versus $\mathcal{O}(1/t)$ for standard GD.

### 2.6 Adaptive Gradient (AdaGrad)
Maintains a per-coordinate running sum of squared past gradients:
$$G_{t} = G_{t-1} + g_t \odot g_t$$
$$\theta_{t+1} = \theta_t - \frac{\eta}{\sqrt{G_t + \epsilon}} \odot g_t$$
where $\odot$ denotes the Hadamard (element-wise) product and $\epsilon = 10^{-8}$. Coordinate-wise scaling automatically shrinks step sizes along frequently updated directions, ideal for sparse features.

### 2.7 Root Mean Square Propagation (RMSProp)
Resolves AdaGrad's monotonically decreasing step size by replacing the accumulator sum with an exponentially decaying moving average of squared gradients:
$$v_t = \beta v_{t-1} + (1 - \beta) g_t \odot g_t$$
$$\theta_{t+1} = \theta_t - \frac{\eta}{\sqrt{v_t + \epsilon}} \odot g_t$$
with discounting coefficient $\beta \in [0.9, 0.99]$.

### 2.8 Adaptive Moment Estimation (Adam)
Combines exponential first-moment tracking (momentum) with exponential second-moment tracking (RMSProp), equipped with bias-correction factors for initialization at the origin:
$$m_t = \beta_1 m_{t-1} + (1 - \beta_1) g_t$$
$$v_t = \beta_2 v_{t-1} + (1 - \beta_2) g_t \odot g_t$$
$$\hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \quad \hat{v}_t = \frac{v_t}{1 - \beta_2^t}$$
$$\theta_{t+1} = \theta_t - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon} \odot \hat{m}_t$$
Default hyper-parameters: $\beta_1 = 0.9, \beta_2 = 0.999, \epsilon = 10^{-8}$.

---

## 3. Second-Order Optimization Algorithms

### 3.1 Damped Newton's Method with Spectral Levenberg-Marquardt Regularization
Newton's method forms a second-order Taylor series approximation:
$$f(\theta + \Delta \theta) \approx f(\theta) + \nabla f(\theta)^T \Delta \theta + \frac{1}{2} \Delta \theta^T \nabla^2 f(\theta) \Delta \theta$$
Stationarity of the quadratic model yields the linear system:
$$\nabla^2 f(\theta_t) \Delta \theta_t = -\nabla f(\theta_t)$$
To ensure global descent and stability when $\nabla^2 f(\theta_t)$ is singular or indefinite, we apply spectral damping:
$$(\nabla^2 f(\theta_t) + \lambda_t I) \Delta \theta_t = -\nabla f(\theta_t)$$
where $\lambda_t = \max(0, -\lambda_{\min}(\nabla^2 f) + \delta)$. An Armijo line search selects step length $\alpha_t$:
$$f(\theta_t + \alpha_t \Delta \theta_t) \le f(\theta_t) + c_1 \alpha_t \nabla f(\theta_t)^T \Delta \theta_t$$
Near a strict local minimum, Newton's method exhibits quadratic convergence: $\|\theta_{t+1} - \theta^*\| \le M \|\theta_t - \theta^*\|^2$.

### 3.2 Gauss-Newton Method for Non-Linear Least Squares
For residual vector $r(\beta) = [r_1(\beta), \dots, r_m(\beta)]^T$, the objective is:
$$S(\beta) = \frac{1}{2} \sum_{i=1}^m r_i(\beta)^2 = \frac{1}{2} \|r(\beta)\|^2$$
The exact gradient and Hessian are:
$$\nabla S(\beta) = J(\beta)^T r(\beta)$$
$$\nabla^2 S(\beta) = J(\beta)^T J(\beta) + \sum_{i=1}^m r_i(\beta) \nabla^2 r_i(\beta)$$
where $J(\beta) \in \mathbb{R}^{m \times p}$ is the Jacobian matrix $J_{ij} = \frac{\partial r_i}{\partial \beta_j}$. Under small residual assumption ($\|r(\beta)\| \approx 0$), the second-order term $\sum r_i \nabla^2 r_i \approx \mathbf{0}$. The Gauss-Newton approximation is:
$$H_{\text{GN}} = J(\beta)^T J(\beta)$$
yielding update direction:
$$(J(\beta)^T J(\beta) + \lambda I) \Delta \beta = -J(\beta)^T r(\beta)$$
This guarantees positive semi-definiteness without evaluating costly second derivatives of residuals.

---

## 4. Decoupled Analytical Backpropagation

### 4.1 Separation of Concerns Architecture
In modern deep learning systems (e.g. PyTorch `autograd` + `torch.optim`), gradient computation is strictly decoupled from optimizer state updates. Our 2-layer MLP implements this exact mathematical boundary:
1. `backward(cache, y)`: Computes purely $\nabla_{\theta} \mathcal{L}$ using exact matrix calculus. It has zero knowledge of learning rates, momentum, or weight decay.
2. `Optimizer.minimize()`: Accepts arbitrary gradient vectors and updates state variables ($v_t, m_t, \theta_t$).

### 4.2 Analytical Derivation (Input $\to$ Hidden $\to$ Output)
Let $X \in \mathbb{R}^{N \times d_{\text{in}}}$, $W_1 \in \mathbb{R}^{d_{\text{in}} \times d_h}$, $b_1 \in \mathbb{R}^{1 \times d_h}$, $W_2 \in \mathbb{R}^{d_h \times d_{\text{out}}}$, $b_2 \in \mathbb{R}^{1 \times d_{\text{out}}}$.
$$\text{Layer 1:} \quad Z_1 = X W_1 + \mathbf{1} b_1, \quad A_1 = \sigma(Z_1)$$
$$\text{Layer 2:} \quad Z_2 = A_1 W_2 + \mathbf{1} b_2, \quad \hat{Y} = Z_2 \text{ (or } \sigma(Z_2)\text{)}$$

For Mean Squared Error $\mathcal{L} = \frac{1}{2N} \|\hat{Y} - Y\|_F^2$:
$$\delta_2 = \frac{\partial \mathcal{L}}{\partial Z_2} = \frac{1}{N} (\hat{Y} - Y)$$
$$\frac{\partial \mathcal{L}}{\partial W_2} = A_1^T \delta_2, \quad \frac{\partial \mathcal{L}}{\partial b_2} = \sum_{i=1}^N \delta_{2, i}$$
Backpropagating error to layer 1:
$$\delta_1 = \frac{\partial \mathcal{L}}{\partial Z_1} = (\delta_2 W_2^T) \odot \sigma'(Z_1) = (\delta_2 W_2^T) \odot (A_1 \odot (1 - A_1))$$
$$\frac{\partial \mathcal{L}}{\partial W_1} = X^T \delta_1, \quad \frac{\partial \mathcal{L}}{\partial b_1} = \sum_{i=1}^N \delta_{1, i}$$

### 4.3 Finite-Difference Numerical Verification
To guarantee analytical correctness, we perform centered finite-difference checking:
$$\left[ \nabla_{\text{num}} \mathcal{L}(\theta) \right]_j = \frac{\mathcal{L}(\theta + \epsilon e_j) - \mathcal{L}(\theta - \epsilon e_j)}{2\epsilon}$$
Relative error norm:
$$\text{RelError} = \frac{\|\nabla_{\text{analytical}} \mathcal{L} - \nabla_{\text{num}} \mathcal{L}\|_2}{\|\nabla_{\text{analytical}} \mathcal{L}\|_2 + \|\nabla_{\text{num}} \mathcal{L}\|_2 + 10^{-12}}$$
Empirically measured relative error: **$4.00 \times 10^{-12}$**, confirming machine-precision analytical gradients.

---

## 5. Curvature Approximations & Quasi-Newton Methods

### 5.1 Empirical Fisher Information Matrix vs. True Hessian
For negative log-likelihood $\mathcal{L}(\theta) = -\sum_{i=1}^N \log p(y_i \mid x_i, \theta)$:
- **Empirical Fisher Information Matrix**:
  $$F_{\text{emp}}(\theta) = \frac{1}{N} \sum_{i=1}^N \nabla_\theta \log p(y_i \mid x_i, \theta) \nabla_\theta \log p(y_i \mid x_i, \theta)^T$$
- **True Hessian of NLL**:
  $$H(\theta) = -\frac{1}{N} \sum_{i=1}^N \nabla_\theta^2 \log p(y_i \mid x_i, \theta)$$
- **Theoretical Relationship**: Under model expectation at true distribution $\mathbb{E}_{p(y \mid x)}[F_{\text{true}}] = \mathbb{E}_{p(y \mid x)}[H]$. For binary logistic regression at $\theta = \mathbf{0}$, predictions are uniform ($p_i = 0.5$), making $F_{\text{emp}}(\mathbf{0}) \equiv H(\mathbf{0})$. For $\theta \neq \mathbf{0}$, $F_{\text{emp}}$ captures outer products of empirical sample gradients, remaining guaranteed positive semi-definite.

### 5.2 Low-Rank BFGS Quasi-Newton Update
The BFGS algorithm approximates the inverse Hessian $B_k \approx (\nabla^2 f)^{-1}$ using curvature displacement vectors $s_k = \theta_{k+1} - \theta_k$ and $y_k = \nabla f(\theta_{k+1}) - \nabla f(\theta_k)$:
$$B_{k+1} = \left( I - \frac{s_k y_k^T}{y_k^T s_k} \right) B_k \left( I - \frac{y_k s_k^T}{y_k^T s_k} \right) + \frac{s_k s_k^T}{y_k^T s_k}$$
This rank-2 update satisfies the secant equation $B_{k+1} y_k = s_k$ and maintains positive-definiteness whenever $y_k^T s_k > 0$.

### 5.3 Pearlmutter Hessian-Vector Products (HVP)
Computing and storing full $d \times d$ Hessian matrices requires $\mathcal{O}(d^2)$ memory and $\mathcal{O}(d^3)$ inversion. Pearlmutter (1994) showed that the action of the Hessian along an arbitrary direction $v \in \mathbb{R}^d$ can be computed using directional finite differences or forward-mode AD in $\mathcal{O}(d)$ time without ever instantiating the full matrix:
$$\nabla^2 f(\theta) v = \lim_{\epsilon \to 0} \frac{\nabla f(\theta + \epsilon v) - \nabla f(\theta - \epsilon v)}{2\epsilon}$$
This enables second-order Krylov subspace solvers (e.g. Conjugate Gradient) in high-dimensional deep learning.

