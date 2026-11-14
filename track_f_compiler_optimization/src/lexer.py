"""Lexical Analyzer (Lexer) for the Mini-Compiler.

Converts raw source code into a stream of tokens, tracking line and column numbers.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class TokenType(Enum):
    # Literals and Identifiers
    NUMBER = auto()
    IDENT = auto()

    # Keywords
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    PRINT = auto()

    # Arithmetic Operators
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()

    # Assignment
    ASSIGN = auto()

    # Comparison Operators
    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()

    # End of File
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, L{self.line}:C{self.column})"


KEYWORDS = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "print": TokenType.PRINT,
}


class LexerError(Exception):
    """Raised when an unrecognized character or malformed token is encountered."""
    pass


class Lexer:
    """Lexical analyzer breaking input source text into tokens."""

    def __init__(self, source_code: str):
        self.source = source_code
        self.pos = 0
        self.line = 1
        self.col = 1
        self.length = len(source_code)

    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        if idx < self.length:
            return self.source[idx]
        return ""

    def _advance(self) -> str:
        if self.pos < self.length:
            ch = self.source[self.pos]
            self.pos += 1
            if ch == "\n":
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            return ch
        return ""

    def tokenize(self) -> List[Token]:
        tokens = []

        while self.pos < self.length:
            ch = self._peek()

            # Skip whitespace
            if ch in (" ", "\t", "\r", "\n"):
                self._advance()
                continue

            # Skip single-line comments (# or //)
            if ch == "#" or (ch == "/" and self._peek(1) == "/"):
                while self.pos < self.length and self._peek() != "\n":
                    self._advance()
                continue

            start_line = self.line
            start_col = self.col

            # Numbers
            if ch.isdigit():
                num_str = ""
                while self._peek().isdigit():
                    num_str += self._advance()
                tokens.append(Token(TokenType.NUMBER, int(num_str), start_line, start_col))
                continue

            # Identifiers and Keywords
            if ch.isalpha() or ch == "_":
                ident_str = ""
                while self._peek().isalnum() or self._peek() == "_":
                    ident_str += self._advance()
                tok_type = KEYWORDS.get(ident_str, TokenType.IDENT)
                tokens.append(Token(tok_type, ident_str, start_line, start_col))
                continue

            # Two-character comparison operators
            if ch == "=" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.EQ, "==", start_line, start_col))
                continue
            if ch == "!" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.NE, "!=", start_line, start_col))
                continue
            if ch == "<" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.LE, "<=", start_line, start_col))
                continue
            if ch == ">" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.GE, ">=", start_line, start_col))
                continue

            # Single-character tokens
            if ch == "=":
                self._advance()
                tokens.append(Token(TokenType.ASSIGN, "=", start_line, start_col))
            elif ch == "+":
                self._advance()
                tokens.append(Token(TokenType.PLUS, "+", start_line, start_col))
            elif ch == "-":
                self._advance()
                tokens.append(Token(TokenType.MINUS, "-", start_line, start_col))
            elif ch == "*":
                self._advance()
                tokens.append(Token(TokenType.MUL, "*", start_line, start_col))
            elif ch == "/":
                self._advance()
                tokens.append(Token(TokenType.DIV, "/", start_line, start_col))
            elif ch == "%":
                self._advance()
                tokens.append(Token(TokenType.MOD, "%", start_line, start_col))
            elif ch == "<":
                self._advance()
                tokens.append(Token(TokenType.LT, "<", start_line, start_col))
            elif ch == ">":
                self._advance()
                tokens.append(Token(TokenType.GT, ">", start_line, start_col))
            elif ch == "(":
                self._advance()
                tokens.append(Token(TokenType.LPAREN, "(", start_line, start_col))
            elif ch == ")":
                self._advance()
                tokens.append(Token(TokenType.RPAREN, ")", start_line, start_col))
            elif ch == "{":
                self._advance()
                tokens.append(Token(TokenType.LBRACE, "{", start_line, start_col))
            elif ch == "}":
                self._advance()
                tokens.append(Token(TokenType.RBRACE, "}", start_line, start_col))
            elif ch == ";":
                self._advance()
                tokens.append(Token(TokenType.SEMICOLON, ";", start_line, start_col))
            else:
                raise LexerError(
                    f"Unexpected character '{ch}' at line {self.line}, column {self.col}"
                )

        tokens.append(Token(TokenType.EOF, None, self.line, self.col))
        return tokens

