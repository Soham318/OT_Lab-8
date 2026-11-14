# Track F: Compiler Optimization Methodology & Pass Selection Formulation

> **Course**: Optimization Techniques — Assignment 8  
> **Module**: `track_f_compiler_optimization/`  
> **Scope**: Constant Folding, Constant Propagation, Strength Reduction, Common Subexpression Elimination, Dead Code Elimination, Pipeline Fixpoint Convergence, and BILP Pass Selection.

---

## 1. Classical Optimization Passes

Every optimization pass implements the method `run(instructions: List[IRInstruction]) -> List[IRInstruction]`, transforming a list of Three-Address-Code instructions while strictly preserving program semantics.

---

### 1.1 Constant Folding (CF)
* **Transformation**: Evaluates arithmetic expressions, comparisons, and conditional branches at compile time whenever all operands are known integer literals.
* **Algebraic Rules**:
  - `t0 = c1 + c2` $\implies$ `t0 = (c1 + c2)`
  - `t0 = c1 * c2` $\implies$ `t0 = (c1 * c2)`
  - `if not 0 goto L` $\implies$ `goto L` (branch unconditionally taken)
  - `if not 1 goto L` $\implies$ `[eliminated]` (branch never taken)
* **Before-and-After IR Example**:
  ```text
  --- BEFORE CF ---
      t0 = 4 * 5
      t1 = t0 + 2
      x = t1

  --- AFTER CF ---
      t0 = 20
      t1 = t0 + 2
      x = t1
  ```
* **Semantic Preservation**: Integer arithmetic on compile-time literals mirrors target runtime operations exactly (including truncated integer division and modulo).

---

### 1.2 Constant Propagation (CP)
* **Transformation**: Replaces variable and temporary references with known constant values computed earlier in the current basic block.
* **Basic Block Invariants**:
  - Maintains a local map `constants: Dict[str, str]` of variables known to hold constant values.
  - When an instruction assigns `x = constant`, `constants[x] = constant` is recorded.
  - When an instruction defines `x` with a non-constant expression, `x` is purged from `constants`.
  - All constants are purged at basic block boundaries (`LABEL`, `JUMP`, `JUMP_IF_FALSE`) because control flow can arrive from multiple predecessors with divergent values.
* **Before-and-After IR Example**:
  ```text
  --- BEFORE CP ---
      a = 10
      t0 = a + 5
      b = t0

  --- AFTER CP ---
      a = 10
      t0 = 10 + 5
      b = t0
  ```
* **Synergy with CF**: When CP replaces `a` with `10`, the subsequent instruction `t0 = 10 + 5` becomes eligible for Constant Folding, evaluating directly to `t0 = 15`.

---

### 1.3 Strength Reduction (SR)
* **Transformation**: Replaces computationally expensive operators (e.g., multiplication) with algebraically equivalent, cheaper operations (e.g., addition or identity assignment).
* **Target Transformations**:
  - $x \times 2 \implies x + x$ (addition requires fewer CPU execution cycles than integer multiplication).
  - $x \times 1 \implies x$ (multiplicative identity).
  - $x \times 0 \implies 0$ (zero annihilation).
  - $x + 0 \implies x$ and $x - 0 \implies x$ (additive identity).
  - $x / 1 \implies x$ (division identity).
* **Before-and-After IR Example**:
  ```text
  --- BEFORE SR ---
      t0 = y * 2
      t1 = z * 1
      t2 = w * 0

  --- AFTER SR ---
      t0 = y + y
      t1 = z
      t2 = 0
  ```

---

### 1.4 Common Subexpression Elimination (CSE)
* **Transformation**: Identifies identical subexpressions $(op, arg1, arg2)$ evaluated multiple times within a basic block and reuses the earlier computed result.
* **Commutativity Canonicalization**:
  - For commutative operators (`ADD`, `MUL`, `CMP_EQ`, `CMP_NE`), operands are normalized lexicographically: $(op, \min(a, b), \max(a, b))$.
  - An expression $x + y$ matches $y + x$.
* **Invalidation Mechanism**:
  - If any subsequent instruction overwrites variable $x$, all cached expressions in the available expression table referencing $x$ as an operand are immediately evicted.
* **Before-and-After IR Example**:
  ```text
  --- BEFORE CSE ---
      t0 = a + b
      x = t0
      t1 = a + b
      y = t1

  --- AFTER CSE ---
      t0 = a + b
      x = t0
      t1 = t0
      y = t1
  ```

---

### 1.5 Dead Code Elimination (DCE)
* **Transformation**: Eliminates instructions whose results are never read downstream and removes unreachable basic blocks.
* **Liveness Analysis**:
  - Traverses the instruction list to collect the set of all variables read by downstream instructions (`get_used_vars()`).
  - Observable outputs (e.g. `PRINT`) and control-flow jumps are strictly marked live.
  - Any pure instruction (`is_pure() == True`) whose destination `result` is never read in the program is deleted.
  - Any instruction sequence following an unconditional `JUMP` up to the next destination `LABEL` is deleted as unreachable dead code.
* **Before-and-After IR Example**:
  ```text
  --- BEFORE DCE ---
      t_dead = 1 + 2
      x = 10
      goto L_target
      unreachable_var = 999
  L_target:
      print x

  --- AFTER DCE ---
      x = 10
      goto L_target
  L_target:
      print x
  ```

---

## 2. Pipeline Fixpoint Convergence

Compiler passes interact synergistically:
1. **Constant Propagation** exposes constant operands $\to$ **Constant Folding** evaluates them to literals.
2. **Constant Folding** on conditional branches turns `if not 0 goto L` into unconditional jumps $\to$ **Dead Code Elimination** prunes the unvisited false branch.
3. **Common Subexpression Elimination** turns duplicate calculations into copy assignments $\to$ **Dead Code Elimination** removes redundant intermediate temporaries.

To capture all cascading opportunities, `CompilerOptimizer.optimize()` runs the pass sequence iteratively:
$$\text{Pipeline Cycle}: \quad \text{CP} \longrightarrow \text{CF} \longrightarrow \text{SR} \longrightarrow \text{CSE} \longrightarrow \text{DCE}$$
* **Fixpoint Termination Criterion**: The loop terminates when the output instruction list is identical to the input list ($IR_{t+1} == IR_t$), ensuring no further transformations are possible.

---

## 3. Mathematical Formulation: Compiler Pass Selection Problem

### 3.1 The Compiler Decision Problem
Modern production compilers (e.g., GCC, LLVM) offer dozens of optimization passes. Enabling every pass indiscriminately incurs severe compile-time overhead (slow developer feedback and CI/CD pipelines) and can sometimes bloat code size. The **Pass Selection Problem** asks: *which subset of compiler optimization passes should be enabled to maximize performance under a bounded compilation budget?*

### 3.2 Decision Variables
Let $m = 5$ be the number of candidate optimization passes:
$$\mathcal{P} = \{\text{CF}, \text{CP}, \text{SR}, \text{CSE}, \text{DCE}\}$$
Define binary decision variables:
$$x_i \in \{0, 1\} \quad \forall i \in \mathcal{P}$$
where $x_i = 1$ if pass $i$ is included in the compilation pipeline, and $0$ otherwise.

### 3.3 Multi-Objective Parameters
For each pass $i \in \mathcal{P}$:
- $B_i^{\text{rt}} \ge 0$: Estimated runtime execution speedup benefit.
- $B_i^{\text{sz}} \ge 0$: Estimated code size / instruction count reduction benefit.
- $C_i^{\text{cmp}} > 0$: Compilation latency cost (wall-clock compile time overhead).

### 3.4 Objective Function
We define a composite objective balancing runtime improvement and code size reduction against compilation latency:
$$\max_{\mathbf{x} \in \{0, 1\}^m} Z(\mathbf{x}) = \sum_{i \in \mathcal{P}} \left( w_{\text{rt}} B_i^{\text{rt}} + w_{\text{sz}} B_i^{\text{sz}} - w_{\text{cmp}} C_i^{\text{cmp}} \right) x_i$$
where $w_{\text{rt}}, w_{\text{sz}}, w_{\text{cmp}} \ge 0$ are user-specified preference weights.

### 3.5 Constraints
1. **Compilation Time Budget**: Total compilation cost must not exceed allowable threshold $C_{\text{budget}}$:
   $$\sum_{i \in \mathcal{P}} C_i^{\text{cmp}} x_i \le C_{\text{budget}}$$
2. **Pass Synergy & Dependency Constraints**:
   Constant Folding achieves its primary benefit when Constant Propagation is enabled to supply constant operands. We enforce the dependency:
   $$x_{\text{CF}} \le x_{\text{CP}} \iff x_{\text{CF}} - x_{\text{CP}} \le 0$$
   (Constant Folding cannot be selected unless Constant Propagation is also active).

### 3.6 Solution via Binary Integer Linear Programming (BILP)
The problem is solved using `scipy.optimize.milp` with bounds $\mathbf{x} \in [0, 1]^m$ and integrality $\mathbf{1}$. In our experiments, solving across budgets $C_{\text{budget}} \in [2.0, 11.0]$ yielded solutions that matched exhaustive combinatorial enumeration across all $2^5 = 32$ subsets with **$0.00\%$ optimality gap**.

### 3.7 Honest Theoretical Limitation: Phase Ordering vs. Pass Selection
> [!IMPORTANT]
> A static 0/1 binary decision model selects *which* passes to enable, but does NOT model **pass ordering** (the sequence in which passes are executed, e.g., $\text{CP} \to \text{CF}$ vs. $\text{CF} \to \text{CP}$) or **pass repetition** (running passes multiple times until fixpoint). Finding the globally optimal compilation sequence in the presence of phase ordering interactions is a non-linear, non-commutative combinatorial problem typically addressed via genetic algorithms or reinforcement learning. Our formulation models pass subset selection under resource budgets.

