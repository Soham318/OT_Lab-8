"""Intermediate Representation (IR) Code Generator.

Translates high-level AST into a linear sequence of Three-Address-Code instructions.
"""

from typing import List
from track_f_compiler_optimization.src.ast_nodes import (
    ASTNode,
    AssignNode,
    BinaryOpNode,
    BlockNode,
    IfNode,
    NumberNode,
    PrintNode,
    ProgramNode,
    VariableNode,
    WhileNode,
)
from track_f_compiler_optimization.src.ir import IRInstruction


class IRGenerator:
    """Traverses AST generating Three-Address-Code instructions with temporaries and labels."""

    def __init__(self):
        self.instructions: List[IRInstruction] = []
        self.temp_counter = 0
        self.label_counter = 0

    def new_temp(self) -> str:
        name = f"t{self.temp_counter}"
        self.temp_counter += 1
        return name

    def new_label(self, prefix: str = "L") -> str:
        name = f"{prefix}{self.label_counter}"
        self.label_counter += 1
        return name

    def generate(self, program: ProgramNode) -> List[IRInstruction]:
        """Generate IR instructions for an entire program."""
        self.instructions.clear()
        self.temp_counter = 0
        self.label_counter = 0

        for stmt in program.statements:
            self._gen_statement(stmt)

        return list(self.instructions)

    def _emit(self, op: str, arg1: str = None, arg2: str = None, result: str = None) -> None:
        self.instructions.append(IRInstruction(op=op, arg1=arg1, arg2=arg2, result=result))

    def _gen_statement(self, node: ASTNode) -> None:
        if isinstance(node, AssignNode):
            val_operand = self._gen_expression(node.value)
            self._emit("ASSIGN", arg1=val_operand, result=node.target)

        elif isinstance(node, PrintNode):
            expr_operand = self._gen_expression(node.expression)
            self._emit("PRINT", arg1=expr_operand)

        elif isinstance(node, BlockNode):
            for stmt in node.statements:
                self._gen_statement(stmt)

        elif isinstance(node, IfNode):
            cond_operand = self._gen_expression(node.condition)
            lbl_else = self.new_label("L_else")
            lbl_end = self.new_label("L_endif")

            if node.false_branch:
                self._emit("JUMP_IF_FALSE", arg1=cond_operand, result=lbl_else)
                self._gen_statement(node.true_branch)
                self._emit("JUMP", result=lbl_end)
                self._emit("LABEL", result=lbl_else)
                self._gen_statement(node.false_branch)
                self._emit("LABEL", result=lbl_end)
            else:
                self._emit("JUMP_IF_FALSE", arg1=cond_operand, result=lbl_end)
                self._gen_statement(node.true_branch)
                self._emit("LABEL", result=lbl_end)

        elif isinstance(node, WhileNode):
            lbl_start = self.new_label("L_while_start")
            lbl_end = self.new_label("L_while_end")

            self._emit("LABEL", result=lbl_start)
            cond_operand = self._gen_expression(node.condition)
            self._emit("JUMP_IF_FALSE", arg1=cond_operand, result=lbl_end)
            self._gen_statement(node.body)
            self._emit("JUMP", result=lbl_start)
            self._emit("LABEL", result=lbl_end)

        else:
            raise NotImplementedError(f"Unsupported statement type: {type(node).__name__}")

    def _gen_expression(self, node: ASTNode) -> str:
        """Returns the variable, constant, or temporary name holding the expression value."""
        if isinstance(node, NumberNode):
            return str(node.value)

        elif isinstance(node, VariableNode):
            return node.name

        elif isinstance(node, BinaryOpNode):
            left_op = self._gen_expression(node.left)
            right_op = self._gen_expression(node.right)
            temp = self.new_temp()

            op_map = {
                "+": "ADD",
                "-": "SUB",
                "*": "MUL",
                "/": "DIV",
                "%": "MOD",
                "==": "CMP_EQ",
                "!=": "CMP_NE",
                "<": "CMP_LT",
                "<=": "CMP_LE",
                ">": "CMP_GT",
                ">=": "CMP_GE",
            }
            ir_op = op_map.get(node.op)
            if not ir_op:
                raise ValueError(f"Unknown binary operator: {node.op}")

            self._emit(ir_op, arg1=left_op, arg2=right_op, result=temp)
            return temp

        else:
            raise NotImplementedError(f"Unsupported expression type: {type(node).__name__}")

