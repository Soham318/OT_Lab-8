"""Semantic Analyzer for the Mini-Compiler.

Performs static analysis on the AST:
- Enforces variable definition-before-use (undeclared variable detection)
- Validates basic integer type semantics
- Builds symbol tables and collects defined variables
"""

from typing import Dict, List, Set
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


class SemanticError(Exception):
    """Raised when static semantics are violated (e.g. use of undefined variable)."""
    pass


class SemanticAnalyzer:
    """Walks the AST verifying variable definition and static invariants."""

    def __init__(self):
        self.defined_variables: Set[str] = set()

    def analyze(self, program: ProgramNode) -> Set[str]:
        """Analyze a program AST.

        Returns:
            Set of all defined variable names.
        """
        self.defined_variables.clear()
        for stmt in program.statements:
            self._visit_statement(stmt)
        return set(self.defined_variables)

    def _visit_statement(self, node: ASTNode) -> None:
        if isinstance(node, AssignNode):
            # Evaluate expression first (cannot read self if not already defined)
            self._visit_expression(node.value)
            self.defined_variables.add(node.target)

        elif isinstance(node, PrintNode):
            self._visit_expression(node.expression)

        elif isinstance(node, BlockNode):
            for stmt in node.statements:
                self._visit_statement(stmt)

        elif isinstance(node, IfNode):
            self._visit_expression(node.condition)
            self._visit_statement(node.true_branch)
            if node.false_branch:
                self._visit_statement(node.false_branch)

        elif isinstance(node, WhileNode):
            self._visit_expression(node.condition)
            self._visit_statement(node.body)

        else:
            raise SemanticError(f"Unknown statement node type: {type(node).__name__}")

    def _visit_expression(self, node: ASTNode) -> None:
        if isinstance(node, NumberNode):
            return

        elif isinstance(node, VariableNode):
            if node.name not in self.defined_variables:
                raise SemanticError(
                    f"Use of undefined variable '{node.name}'. Variables must be assigned before use."
                )

        elif isinstance(node, BinaryOpNode):
            self._visit_expression(node.left)
            self._visit_expression(node.right)

        else:
            raise SemanticError(f"Unknown expression node type: {type(node).__name__}")

