"""Abstract Syntax Tree (AST) Node Definitions for the Mini-Compiler."""

from dataclasses import dataclass
from typing import List, Optional


class ASTNode:
    """Base class for all AST nodes."""
    pass


@dataclass
class NumberNode(ASTNode):
    """Integer literal node."""
    value: int


@dataclass
class VariableNode(ASTNode):
    """Variable reference node."""
    name: str


@dataclass
class BinaryOpNode(ASTNode):
    """Binary arithmetic or comparison operator node."""
    op: str  # '+', '-', '*', '/', '%', '==', '!=', '<', '<=', '>', '>='
    left: ASTNode
    right: ASTNode


@dataclass
class AssignNode(ASTNode):
    """Variable assignment statement."""
    target: str
    value: ASTNode


@dataclass
class PrintNode(ASTNode):
    """Print statement emitting an evaluated expression."""
    expression: ASTNode


@dataclass
class BlockNode(ASTNode):
    """Sequence of statements enclosed in braces."""
    statements: List[ASTNode]


@dataclass
class IfNode(ASTNode):
    """Conditional statement with optional else branch."""
    condition: ASTNode
    true_branch: BlockNode
    false_branch: Optional[BlockNode] = None


@dataclass
class WhileNode(ASTNode):
    """While loop statement."""
    condition: ASTNode
    body: BlockNode


@dataclass
class ProgramNode(ASTNode):
    """Top-level program node containing statement list."""
    statements: List[ASTNode]

