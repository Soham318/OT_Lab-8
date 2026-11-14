# Track F: Mini-Compiler Architecture & IR Design

> **Course**: Optimization Techniques — Assignment 8  
> **Module**: `track_f_compiler_optimization/`  
> **Pipeline**: Source Code $\to$ Tokens $\to$ AST $\to$ Semantic Validation $\to$ Three-Address-Code IR $\to$ Optimization Passes $\to$ Virtual Machine Execution

---

## 1. Compiler Pipeline Overview

```
+------------------------------------------------------------------------------------+
|                               MINI-COMPILER PIPELINE                               |
+------------------------------------------------------------------------------------+
                                          │
                                          ▼
                                 [ Source Code Text ]
                                          │
                                          ▼ (Lexer)
                                   [ Token Stream ]
                                          │
                                          ▼ (Recursive Descent Parser)
                           [ Abstract Syntax Tree (AST) ]
                                          │
                                          ▼ (Semantic Analyzer: Symbol Table Check)
                           [ Semantically Validated AST ]
                                          │
                                          ▼ (IR Generator)
                     [ Raw Three-Address-Code (3AC) IR List ]
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    │                                           │
                    ▼ (Unoptimized Path)                        ▼ (Compiler Optimizer)
        [ Unoptimized 3AC IR ]                      ┌───────────────────────────────┐
                    │                               │ 1. Constant Propagation (CP)  │
                    │                               │ 2. Constant Folding (CF)      │
                    │                               │ 3. Strength Reduction (SR)    │
                    │                               │ 4. Common Subexpression (CSE) │
                    │                               │ 5. Dead Code Elimination (DCE)│
                    │                               │ Fixpoint Iteration Loop       │
                    │                               └───────────────────────────────┘
                    │                                           │
                    │                                           ▼
                    │                               [ Optimized 3AC IR ]
                    │                                           │
                    └─────────────────────┬─────────────────────┘
                                          │
                                          ▼ (Virtual Machine / Interpreter)
                          [ Program Execution & Output Stream ]
                                          │
                                          ▼
                           [ Execution Metrics & Verification ]
```

---

## 2. Stage-by-Stage Architecture

### 2.1 Lexical Analyzer (`src/lexer.py`)
- Reads raw UTF-8 source code sequentially via character lookahead (`_peek(offset)`).
- Categorizes character sequences into strong tokens (`Token(type, value, line, column)`).
- Identifies single and multi-character operators (`==`, `!=`, `<=`, `>=`), keywords (`if`, `else`, `while`, `print`), identifiers, and integer constants.
- Strips comments and whitespace while tracking exact line and column numbers.

### 2.2 Recursive Descent Parser (`src/parser.py`)
- Implements predictive LL(1) recursive descent parsing without backtracking.
- Builds an Abstract Syntax Tree (AST) constructed from dataclass nodes defined in `src/ast_nodes.py`:
  - `ProgramNode`, `BlockNode`, `AssignNode`, `PrintNode`, `IfNode`, `WhileNode`, `BinaryOpNode`, `NumberNode`, `VariableNode`.
- Enforces grammar rules and operator precedence (Relational $\to$ Additive $\to$ Multiplicative $\to$ Unary $\to$ Primary).

### 2.3 Semantic Analyzer (`src/semantic_analyzer.py`)
- Walks the AST prior to code generation.
- Enforces declaration-before-use semantics: variables read on right-hand sides must have been assigned previously.
- Prevents runtime `NameError` exceptions by rejecting undefined variable reads at compile time with descriptive `SemanticError`.

### 2.4 Three-Address-Code (3AC) Generator (`src/ir_generator.py`)
- Flattens high-level AST trees into a linear instruction sequence where each instruction operates on at most two source operands and produces one destination result.
- Generates synthetic temporaries (`t0`, `t1`, `t2`, ...) for subexpression evaluation.
- Generates jump labels (`L_while_start0`, `L_while_end1`, `L_else2`, `L_endif3`) for conditional branches and loops.

### 2.5 Compiler Optimization Pipeline (`src/optimizer.py`)
- Operates directly on the 3AC instruction sequence.
- Manages an iterative pipeline executing five classical optimization passes until **fixpoint convergence** ($IR_{t+1} == IR_t$).

### 2.6 Virtual Machine Interpreter (`src/interpreter.py`)
- Directly executes 3AC instruction lists in an isolated environment.
- Pre-indexes label positions into a $O(1)$ dictionary lookup table.
- Maintains an evaluation environment `env: Dict[str, int]` mapping variables and temporaries to 64-bit integer values.
- Captures `print` outputs in an observable output buffer for exact output parity verification.
- Enforces an execution step limit (`max_steps = 500,000`) to guarantee safety against accidental infinite loops.

---

## 3. Three-Address-Code (3AC) Instruction Set

Every instruction is represented by `IRInstruction(op, arg1, arg2, result)`:

| Opcode | `arg1` | `arg2` | `result` | Description | Text Representation |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `ASSIGN` | Source (var/const) | `None` | Dest var | Direct value assignment | `x = t0` or `x = 42` |
| `ADD` | Left operand | Right operand | Dest var | Binary addition | `t0 = a + b` |
| `SUB` | Left operand | Right operand | Dest var | Binary subtraction | `t0 = a - b` |
| `MUL` | Left operand | Right operand | Dest var | Binary multiplication | `t0 = a * b` |
| `DIV` | Left operand | Right operand | Dest var | Truncated integer division | `t0 = a / b` |
| `MOD` | Left operand | Right operand | Dest var | Integer remainder | `t0 = a % b` |
| `CMP_EQ` | Left operand | Right operand | Dest var | Equality comparison (1 or 0) | `t0 = a == b` |
| `CMP_NE` | Left operand | Right operand | Dest var | Non-equality comparison | `t0 = a != b` |
| `CMP_LT` | Left operand | Right operand | Dest var | Less-than comparison | `t0 = a < b` |
| `CMP_LE` | Left operand | Right operand | Dest var | Less-than-or-equal comparison | `t0 = a <= b` |
| `CMP_GT` | Left operand | Right operand | Dest var | Greater-than comparison | `t0 = a > b` |
| `CMP_GE` | Left operand | Right operand | Dest var | Greater-than-or-equal comparison | `t0 = a >= b` |
| `LABEL` | `None` | `None` | Label name | Symbolic jump destination | `L0:` |
| `JUMP` | `None` | `None` | Target label | Unconditional branch | `goto L0` |
| `JUMP_IF_FALSE` | Condition var | `None` | Target label | Branch if condition is 0 | `if not t0 goto L1` |
| `JUMP_IF_TRUE` | Condition var | `None` | Target label | Branch if condition != 0 | `if t0 goto L1` |
| `PRINT` | Source (var/const) | `None` | `None` | Observable output emission | `print t0` |

