# Track F: Compiler Optimization — Comprehensive Viva Q&A Guide

> **Course**: Optimization Techniques — Assignment 8  
> **Module**: `track_f_compiler_optimization/`  
> **Topic**: Lexing, Parsing, Semantic Analysis, Three-Address-Code IR, Optimization Passes, and Pass Selection Optimization.

---

### Q1: What are the primary phases of a compiler, and how are they decoupled?
**Answer:**  
A modern compiler decouples into three distinct modules:
1. **Frontend**: Language-specific. Performs Lexical Analysis (tokenization), Syntax Analysis (parsing AST), and Semantic Analysis (type checking, symbol tables).
2. **Middle-end (Optimizer)**: Language-independent and machine-independent. Operates on an Intermediate Representation (IR). Applies data-flow and loop optimization passes (Constant Folding, Propagation, CSE, DCE, Loop Invariant Code Motion).
3. **Backend**: Machine-specific. Translates optimized IR into target machine code (e.g., x86, ARM, RISC-V), performing instruction selection, register allocation, and instruction scheduling.  
*Decoupling Benefit*: For $N$ source languages and $M$ target architectures, an intermediate representation requires $N$ frontends and $M$ backends ($N + M$ components) rather than $N \times M$ separate compilers.

---

### Q2: Why do compilers optimize on an Intermediate Representation (IR) rather than directly on the Abstract Syntax Tree (AST)?
**Answer:**  
- **Linearized Control Flow**: ASTs are hierarchical trees with nested control structures (`if`, `while`). An IR such as Three-Address-Code (3AC) linearizes control flow into explicit jump instructions and basic block labels, making graph-based control flow analysis (CFGs) and dominator tree calculations straightforward.
- **Explicit Temporary Storage**: ASTs represent nested operations implicitly in sub-trees. Three-Address-Code makes every intermediate value explicit via named temporaries (`t0`, `t1`), which enables precise variable liveness analysis, register allocation, and subexpression caching.
- **Language Independence**: Optimization passes written for an IR can be reused across any programming language that compiles to that IR.

---

### Q3: What is Three-Address-Code (3AC), and what invariants does it enforce?
**Answer:**  
Three-Address-Code is a linearized intermediate representation where every instruction contains at most one operator and at most three address references (two source operands and one destination result):
$$\text{result} = \text{arg}_1 \text{ op } \text{arg}_2$$
- **Invariants**:
  1. Complex expressions are decomposed into sequential binary operations using temporary variables: $a + b + c \implies t_0 = a + b; \quad t_1 = t_0 + c$.
  2. Control flow is represented solely by explicit conditional branches (`JUMP_IF_FALSE arg, label`) and unconditional jumps (`JUMP label`).
  3. Every instruction has clearly defined definition sets ($\text{def}$) and use sets ($\text{use}$).

---

### Q4: Explain the Constant Folding transformation and its semantic preservation rules.
**Answer:**  
- **Transformation**: Evaluates operations whose operands are known compile-time constants:
  $$t_0 = c_1 \text{ op } c_2 \implies t_0 = \text{eval}(c_1 \text{ op } c_2)$$
  It also folds constant conditional jumps: `JUMP_IF_FALSE 0, L` becomes an unconditional `JUMP L`, while `JUMP_IF_FALSE 1, L` is eliminated as a dead branch.
- **Semantic Preservation**: Compile-time evaluation must strictly mimic target runtime semantics (e.g., signed integer overflow, truncated integer division, and modulo). If an operation would cause a runtime exception (e.g. division by zero), the compiler must not fold it into an arbitrary constant.

---

### Q5: How does Constant Propagation operate within a basic block, and why must local constants be invalidated across labels?
**Answer:**  
- **Mechanism**: Maintains a dictionary `constants: Dict[str, str]` mapping variable/temporary names to literal constants. Whenever an instruction reads variable $x$ and $x \in \text{constants}$, $x$ is drop-in replaced by its constant literal.
- **Invalidation**: When variable $x$ is reassigned a non-constant value, $x$ is removed from `constants`.
- **Label Invalidation**: At basic block boundaries (`LABEL`), control flow can arrive from multiple preceding program paths with divergent values (e.g. from the end of a loop or an alternate `else` branch). Unless global reaching-definitions or SSA form is computed, local constant tables must be flushed at every label to prevent invalid assumptions.

---

### Q6: What is Strength Reduction, and why is $x \times 2 \implies x + x$ an optimization on modern hardware?
**Answer:**  
- **Definition**: Strength Reduction replaces a computationally expensive operation with an algebraically equivalent, cheaper operation.
- **Cycle Cost**: On physical CPU architectures (e.g., RISC-V or x86), an integer addition (`ADD`) has a latency of 1 clock cycle and can be dispatched across multiple execution ports. An integer multiplication (`MUL`), even with hardware multipliers, typically has a latency of 3 to 5 clock cycles.
- **Identities**:
  - $x \times 2 \implies x + x$ (or left shift $x \ll 1$)
  - $x \times 1 \implies x$, $x \times 0 \implies 0$
  - $x + 0 \implies x$, $x - 0 \implies x$
  - $x / 1 \implies x$

---

### Q7: Explain Common Subexpression Elimination (CSE) and how commutative operators are handled.
**Answer:**  
- **Mechanism**: Maintains a table of available expressions `available: Dict[Tuple[op, arg1, arg2], str]` within a basic block. If the same $(op, arg1, arg2)$ has already been computed into variable $t_{\text{prev}}$ and neither operand has been modified since, the redundant calculation is replaced with a simple assignment:
  $$t_{\text{curr}} = \text{arg}_1 \text{ op } \text{arg}_2 \implies t_{\text{curr}} = t_{\text{prev}}$$
- **Commutativity Canonicalization**: For commutative operations (`ADD`, `MUL`, `CMP_EQ`, `CMP_NE`), the order of operands is lexicographically sorted:
  $$\text{key} = (op, \min(a, b), \max(a, b))$$
  This ensures $x + y$ and $y + x$ map to the exact same hash key and are eliminated as common subexpressions.

---

### Q8: How does Dead Code Elimination (DCE) identify dead instructions, and how are side effects preserved?
**Answer:**  
- **Liveness Analysis**: DCE performs a backward scan over instructions to build the set of all variables read by downstream instructions (`used_vars`).
- **Pruning**: Any pure instruction (`is_pure() == True`) whose destination `result` is not present in `used_vars` is eliminated.
- **Side Effect Preservation**: Instructions with observable side effects (`PRINT`, system calls, memory stores) or control-flow operations (`JUMP`, `LABEL`) return `is_pure() == False`. They are never removed by DCE, even if they do not define a variable.

---

### Q9: What is "phase interaction", and how does Constant Propagation enable Dead Code Elimination?
**Answer:**  
Phase interaction occurs when the output of one optimization pass exposes new optimization opportunities for another pass:
1. `x = 42; dead = x * 10; print(x);`
2. **Constant Propagation** replaces $x$ in `x * 10` with `42`, producing `dead = 42 * 10;`.
3. **Constant Folding** evaluates `42 * 10` to `420`, producing `dead = 420;`.
4. Because `dead` is never read in `print(x)`, **Dead Code Elimination** detects that `dead` is dead and eliminates `dead = 420;` entirely.
Neither pass could have eliminated the dead computation alone; their cascaded interaction enabled complete optimization.

---

### Q10: How does the compiler optimizer achieve fixpoint convergence?
**Answer:**  
The optimizer loops through the pass sequence:
$$\text{CP} \to \text{CF} \to \text{SR} \to \text{CSE} \to \text{DCE}$$
At each iteration, it stores a snapshot of the instruction sequence. The loop terminates when the post-pipeline instruction list is identical to the pre-pipeline instruction list:
$$\text{Pipeline}(IR_t) == IR_t$$
This guarantees that all cascading optimization chains (e.g., constant propagation feeding folding feeding dead code elimination) are fully resolved before code generation.

---

### Q11: How is the Compiler Pass Selection Problem formulated as a Binary Integer Linear Program (BILP)?
**Answer:**  
Let $x_i \in \{0, 1\}$ represent enabling pass $i \in \{\text{CF}, \text{CP}, \text{SR}, \text{CSE}, \text{DCE}\}$.
- **Objective**: Maximize net performance benefit:
  $$\max_{\mathbf{x} \in \{0, 1\}^m} \sum_{i=1}^m (w_{\text{rt}} B_i^{\text{rt}} + w_{\text{sz}} B_i^{\text{sz}} - w_{\text{cmp}} C_i^{\text{cmp}}) x_i$$
- **Budget Constraint**:
  $$\sum_{i=1}^m C_i^{\text{cmp}} x_i \le C_{\text{budget}}$$
- **Dependency Constraint**: Constant Folding relies on Constant Propagation:
  $$x_{\text{CF}} - x_{\text{CP}} \le 0$$
Solved using branch-and-bound via `scipy.optimize.milp` with bounds $[0, 1]^m$ and integrality constraints.

---

### Q12: What is the fundamental difference between Pass Selection and the Phase Ordering Problem?
**Answer:**  
- **Pass Selection** decides *which* subset of optimization passes to run under a resource budget (a 0/1 binary decision problem $\mathbf{x} \in \{0, 1\}^m$).
- **Phase Ordering** decides *the sequence* in which selected passes are applied (e.g., $\text{CP} \to \text{CF} \to \text{DCE}$ vs. $\text{DCE} \to \text{CP} \to \text{CF}$).
- **Non-Commutativity**: Compiler passes do not commute: applying pass $A$ before $B$ often produces different IR than applying $B$ before $A$. A static 0/1 BILP selects pass presence, but finding the optimal sequence is an NP-hard permutation search over $m!$ (or infinite if repetition is allowed) sequences.

---

### Q13: How does the compiler detect syntax errors versus semantic errors?
**Answer:**  
- **Syntax Errors**: Detected by the Lexer (unrecognized characters) or Parser (grammar violations, e.g. missing closing braces, unclosed parenthesis in `while (x > 0 { ... }`). They represent invalid grammatical structure and raise `ParserError` before an AST is formed.
- **Semantic Errors**: Detected by the Semantic Analyzer on a grammatically valid AST (e.g., reading variable $x$ before it is assigned: `y = x + 10;`). They represent invalid meaning/types and raise `SemanticError`.

---

### Q14: In our benchmark on `arithmetic_heavy`, why did instruction count drop from 20 to 1?
**Answer:**  
All initial expressions ($100 \times 2$, $50 + 25 \times 4$, etc.) depended solely on compile-time constant literals.
Through fixpoint iteration:
1. Constant Folding and Propagation evaluated every intermediate expression to known numbers.
2. The final arithmetic sum $x + y + z + w$ was folded to `2100`.
3. Dead Code Elimination determined that none of the intermediate variables (`c1`, `c2`, `base`, `x`, `y`, `z`, `w`) were read anywhere other than in the folded sum.
4. All intermediate assignments were pruned, leaving only `print 2100`.

---

### Q15: In `loop_heavy`, why did dynamic execution steps drop by 600 cycles while static IR only decreased by 3 instructions?
**Answer:**  
The loop executes 200 iterations at runtime. Inside the loop body, three instructions were eliminated:
1. The invariant expression `10 * 5 + 2` was folded to constant `52`.
2. The duplicate computation `dup2 = k * 3` was eliminated via Common Subexpression Elimination.
3. The dead temporary variable was pruned via Dead Code Elimination.
Eliminating 3 static instructions inside the loop body eliminated $3 \times 200 = 600$ dynamic execution steps during program runtime, demonstrating that optimizing loop bodies yields outsized runtime gains.

---

### Q16: How is semantic execution equivalence verified between unoptimized and optimized code?
**Answer:**  
The test harness compiles the exact same source code twice: once with `optimize=False` and once with `optimize=True`. Both IR streams are executed on identical virtual machine environments with identical inputs. The harness asserts that:
$$\text{output}_{\text{unoptimized}} == \text{output}_{\text{optimized}}$$
Across all benchmark programs, the observable print outputs ([2100], [2067], [100], [131000], [208000]) matched identically, proving 100% semantic preservation.

