"""Three-Address-Code (3AC) Intermediate Representation (IR).

Defines instructions, operands, string representations, and analysis helpers.
"""

from dataclasses import dataclass
from typing import List, Optional, Set


@dataclass
class IRInstruction:
    """A single Three-Address-Code instruction.

    Format: result = arg1 op arg2, or control flow / side effect opcodes.
    """
    op: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    result: Optional[str] = None

    def __repr__(self) -> str:
        op = self.op.upper()

        if op == "LABEL":
            return f"{self.result}:"

        if op == "JUMP":
            return f"goto {self.result}"

        if op == "JUMP_IF_FALSE":
            return f"if not {self.arg1} goto {self.result}"

        if op == "JUMP_IF_TRUE":
            return f"if {self.arg1} goto {self.result}"

        if op == "PRINT":
            return f"print {self.arg1}"

        if op == "ASSIGN":
            return f"{self.result} = {self.arg1}"

        # Binary arithmetic and comparison operators
        op_symbol_map = {
            "ADD": "+",
            "SUB": "-",
            "MUL": "*",
            "DIV": "/",
            "MOD": "%",
            "CMP_EQ": "==",
            "CMP_NE": "!=",
            "CMP_LT": "<",
            "CMP_LE": "<=",
            "CMP_GT": ">",
            "CMP_GE": ">=",
        }
        sym = op_symbol_map.get(op, op)
        return f"{self.result} = {self.arg1} {sym} {self.arg2}"

    def is_pure(self) -> bool:
        """True if instruction has no observable side effects (not print, not jump, not label)."""
        return self.op not in ("LABEL", "JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE", "PRINT")

    def is_branch_or_label(self) -> bool:
        """True if instruction alters control flow or marks a jump target."""
        return self.op in ("LABEL", "JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE")

    def get_defined_var(self) -> Optional[str]:
        """Return the variable or temporary defined by this instruction."""
        if self.is_pure() and self.result is not None:
            return self.result
        return None

    def get_used_vars(self) -> Set[str]:
        """Return set of variable and temporary names read by this instruction."""
        used = set()
        for arg in (self.arg1, self.arg2):
            if arg is not None and not is_constant(arg):
                used.add(arg)
        return used


def is_constant(val: Optional[str]) -> bool:
    """Check if operand string represents an integer constant."""
    if val is None:
        return False
    if val.startswith("-") and val[1:].isdigit():
        return True
    return val.isdigit()


def to_constant_value(val: str) -> int:
    """Parse integer literal string."""
    return int(val)


def pretty_print_ir(instructions: List[IRInstruction]) -> str:
    """Format instructions into clean human-readable assembly-like text."""
    lines = []
    for inst in instructions:
        if inst.op == "LABEL":
            lines.append(f"{inst.result}:")
        else:
            lines.append(f"    {inst}")
    return "\n".join(lines)

