"""Recursive Descent Parser for the Mini-Compiler.

Parses token stream into an Abstract Syntax Tree (AST) matching standard
operator precedence:
    Comparison < Additive < Multiplicative < Unary < Primary
"""

from typing import List, Optional
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
from track_f_compiler_optimization.src.lexer import Token, TokenType


class ParserError(Exception):
    """Raised when a syntax error is encountered during parsing."""
    pass


class Parser:
    """Constructs AST from a list of tokens via recursive descent."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _peek_type(self, offset: int = 0) -> TokenType:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx].type
        return TokenType.EOF

    def _advance(self) -> Token:
        tok = self._current()
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def _match(self, *expected_types: TokenType) -> bool:
        if self._current().type in expected_types:
            self._advance()
            return True
        return False

    def _consume(self, expected_type: TokenType, error_msg: str) -> Token:
        if self._current().type == expected_type:
            return self._advance()
        tok = self._current()
        raise ParserError(
            f"{error_msg} at line {tok.line}, column {tok.column}. Got {tok.type.name} ('{tok.value}')"
        )

    def parse(self) -> ProgramNode:
        """Parse complete program."""
        statements = []
        while self._current().type != TokenType.EOF:
            # Handle stray semicolons gracefully
            if self._match(TokenType.SEMICOLON):
                continue
            stmt = self._parse_statement()
            statements.append(stmt)
        return ProgramNode(statements=statements)

    def _parse_statement(self) -> ASTNode:
        tok = self._current()

        if tok.type == TokenType.PRINT:
            return self._parse_print_statement()
        elif tok.type == TokenType.IF:
            return self._parse_if_statement()
        elif tok.type == TokenType.WHILE:
            return self._parse_while_statement()
        elif tok.type == TokenType.LBRACE:
            return self._parse_block_statement()
        elif tok.type == TokenType.IDENT and self._peek_type(1) == TokenType.ASSIGN:
            return self._parse_assign_statement()
        else:
            raise ParserError(
                f"Unexpected token in statement: {tok.type.name} ('{tok.value}') at line {tok.line}, column {tok.column}"
            )

    def _parse_assign_statement(self) -> AssignNode:
        ident_tok = self._consume(TokenType.IDENT, "Expected variable name in assignment")
        self._consume(TokenType.ASSIGN, "Expected '=' in assignment")
        expr = self._parse_expression()
        self._match(TokenType.SEMICOLON)  # Semicolon is optional/consumed
        return AssignNode(target=ident_tok.value, value=expr)

    def _parse_print_statement(self) -> PrintNode:
        self._consume(TokenType.PRINT, "Expected 'print'")
        has_paren = self._match(TokenType.LPAREN)
        expr = self._parse_expression()
        if has_paren:
            self._consume(TokenType.RPAREN, "Expected ')' after print expression")
        self._match(TokenType.SEMICOLON)
        return PrintNode(expression=expr)

    def _parse_if_statement(self) -> IfNode:
        self._consume(TokenType.IF, "Expected 'if'")
        self._consume(TokenType.LPAREN, "Expected '(' after 'if'")
        cond = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after 'if' condition")
        true_block = self._parse_block_statement()

        false_block = None
        if self._match(TokenType.ELSE):
            if self._current().type == TokenType.IF:
                # else if -> wrap in block
                false_stmt = self._parse_if_statement()
                false_block = BlockNode(statements=[false_stmt])
            else:
                false_block = self._parse_block_statement()

        return IfNode(condition=cond, true_branch=true_block, false_branch=false_block)

    def _parse_while_statement(self) -> WhileNode:
        self._consume(TokenType.WHILE, "Expected 'while'")
        self._consume(TokenType.LPAREN, "Expected '(' after 'while'")
        cond = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after 'while' condition")
        body = self._parse_block_statement()
        return WhileNode(condition=cond, body=body)

    def _parse_block_statement(self) -> BlockNode:
        self._consume(TokenType.LBRACE, "Expected '{' to start block")
        statements = []
        while self._current().type not in (TokenType.RBRACE, TokenType.EOF):
            if self._match(TokenType.SEMICOLON):
                continue
            stmt = self._parse_statement()
            statements.append(stmt)
        self._consume(TokenType.RBRACE, "Expected '}' to close block")
        return BlockNode(statements=statements)

    def _parse_expression(self) -> ASTNode:
        return self._parse_equality()

    def _parse_equality(self) -> ASTNode:
        node = self._parse_relational()
        while self._current().type in (TokenType.EQ, TokenType.NE):
            op_tok = self._advance()
            right = self._parse_relational()
            node = BinaryOpNode(op=op_tok.value, left=node, right=right)
        return node

    def _parse_relational(self) -> ASTNode:
        node = self._parse_additive()
        while self._current().type in (TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            op_tok = self._advance()
            right = self._parse_additive()
            node = BinaryOpNode(op=op_tok.value, left=node, right=right)
        return node

    def _parse_additive(self) -> ASTNode:
        node = self._parse_multiplicative()
        while self._current().type in (TokenType.PLUS, TokenType.MINUS):
            op_tok = self._advance()
            right = self._parse_multiplicative()
            node = BinaryOpNode(op=op_tok.value, left=node, right=right)
        return node

    def _parse_multiplicative(self) -> ASTNode:
        node = self._parse_unary()
        while self._current().type in (TokenType.MUL, TokenType.DIV, TokenType.MOD):
            op_tok = self._advance()
            right = self._parse_unary()
            node = BinaryOpNode(op=op_tok.value, left=node, right=right)
        return node

    def _parse_unary(self) -> ASTNode:
        if self._current().type in (TokenType.PLUS, TokenType.MINUS):
            op_tok = self._advance()
            operand = self._parse_unary()
            if op_tok.type == TokenType.MINUS:
                # 0 - operand
                return BinaryOpNode(op="-", left=NumberNode(value=0), right=operand)
            return operand
        return self._parse_primary()

    def _parse_primary(self) -> ASTNode:
        tok = self._current()

        if tok.type == TokenType.NUMBER:
            self._advance()
            return NumberNode(value=tok.value)

        if tok.type == TokenType.IDENT:
            self._advance()
            return VariableNode(name=tok.value)

        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')' after parenthesized expression")
            return expr

        raise ParserError(
            f"Expected primary expression, got {tok.type.name} ('{tok.value}') at line {tok.line}, column {tok.column}"
        )

