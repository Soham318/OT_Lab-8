# Track F: Mini-Language Specification

> **Course**: Optimization Techniques — Assignment 8  
> **Module**: `track_f_compiler_optimization/`  
> **Dialect**: Imperative Integer Mini-Language (`MiniLang`)

---

## 1. Lexical Grammar

### 1.1 Character Set & Comments
- Source files are encoded in standard UTF-8 text.
- Whitespace characters (spaces, tabs, newlines `\r`, `\n`) act as token separators and are otherwise ignored.
- **Single-line comments**: Comments begin with `#` or `//` and extend to the end of the line.

### 1.2 Tokens
```ebnf
digit          = "0" | "1" | ... | "9" ;
letter         = "a" | ... | "z" | "A" | ... | "Z" | "_" ;
identifier     = letter , { letter | digit } ;
integer        = digit , { digit } ;

keyword        = "if" | "else" | "while" | "print" ;
arith_op       = "+" | "-" | "*" | "/" | "%" ;
rel_op         = "==" | "!=" | "<" | "<=" | ">" | ">=" ;
assign_op      = "=" ;
delimiter      = "(" | ")" | "{" | "}" | ";" ;
```

---

## 2. Syntax Grammar (EBNF)

```ebnf
program        = { statement } , EOF ;

statement      = assign_stmt
               | print_stmt
               | if_stmt
               | while_stmt
               | block_stmt
               | ";" ;

assign_stmt    = identifier , "=" , expression , [ ";" ] ;
print_stmt     = "print" , ( "(" , expression , ")" | expression ) , [ ";" ] ;
if_stmt        = "if" , "(" , expression , ")" , block_stmt , [ "else" , ( if_stmt | block_stmt ) ] ;
while_stmt     = "while" , "(" , expression , ")" , block_stmt ;
block_stmt     = "{" , { statement } , "}" ;

expression     = equality ;
equality       = relational , { ( "==" | "!=" ) , relational } ;
relational     = additive , { ( "<" | "<=" | ">" | ">=" ) , additive } ;
additive       = multiplicative , { ( "+" | "-" ) , multiplicative } ;
multiplicative = unary , { ( "*" | "/" | "%" ) , unary } ;
unary          = ( "+" | "-" ) , unary | primary ;
primary        = integer | identifier | "(" , expression , ")" ;
```

---

## 3. Operator Precedence & Associativity

All binary operators are left-associative. Precedence from lowest to highest:

| Precedence Level | Operators | Description | Associativity |
| :---: | :---: | :---: | :---: |
| **1 (Lowest)** | `==`, `!=` | Equality comparisons | Left-to-right |
| **2** | `<`, `<=`, `>`, `>=` | Relational ordering comparisons | Left-to-right |
| **3** | `+`, `-` | Addition and Subtraction | Left-to-right |
| **4** | `*`, `/`, `%` | Multiplication, Integer Division, Modulo | Left-to-right |
| **5** | unary `+`, `-` | Unary sign inversion | Right-to-left |
| **6 (Highest)** | `(...)`, literals | Parentheses and primary operands | N/A |

---

## 4. Type System & Semantics

1. **Primitive Types**: The language supports a single primitive data type: **signed 64-bit integers** ($\mathbb{Z}$).
2. **Boolean Representation**: Comparisons evaluate to `1` for `true` and `0` for `false`. Conditional statements (`if`, `while`) treat `0` as false and any non-zero value as true.
3. **Variable Semantics**:
   - Variables are statically declared upon their first assignment.
   - Using a variable prior to assignment raises a compile-time `SemanticError`.
   - Variable scope is function-global across the compiled compilation unit.
4. **Division Semantics**: Division `/` performs truncated integer division (equivalent to Python `//`). Division or modulo by zero raises a runtime `InterpreterRuntimeError`.
5. **Side Effects**: The `print` statement emits an integer value to the observable output stream. Pure arithmetic statements produce no observable side effects beyond environment mutation.

---

## 5. Scope & Explicit Limitations

To maintain a self-contained, demonstrable mini-compiler, the following advanced language features are intentionally omitted:
- **No Functions or Recursion**: All programs execute as a single main body block.
- **No Floating-Point Arithmetic**: Integer arithmetic only.
- **No Heap or Pointers**: Variables reside in a flat symbolic register/environment table.
- **No Arrays or Strings**: Only scalar integer variables are supported.

