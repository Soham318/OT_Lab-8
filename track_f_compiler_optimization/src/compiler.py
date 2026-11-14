"""High-level Compiler Driver and Pipeline Orchestrator.

Integrates Lexer, Parser, Semantic Analyzer, IR Generator, Optimizer,
and Virtual Machine execution into a unified interface.
"""

from typing import Any, Dict, List, Optional, Tuple
from track_f_compiler_optimization.src.ast_nodes import ProgramNode
from track_f_compiler_optimization.src.interpreter import IRInterpreter
from track_f_compiler_optimization.src.ir import IRInstruction, pretty_print_ir
from track_f_compiler_optimization.src.ir_generator import IRGenerator
from track_f_compiler_optimization.src.lexer import Lexer
from track_f_compiler_optimization.src.optimizer import CompilerOptimizer
from track_f_compiler_optimization.src.parser import Parser
from track_f_compiler_optimization.src.semantic_analyzer import SemanticAnalyzer


class MiniCompiler:
    """End-to-end compiler pipeline for the mini-language."""

    def __init__(self, optimizer: Optional[CompilerOptimizer] = None):
        self.semantic_analyzer = SemanticAnalyzer()
        self.ir_generator = IRGenerator()
        self.optimizer = optimizer or CompilerOptimizer()
        self.interpreter = IRInterpreter()

    def compile(
        self, source_code: str, optimize: bool = True
    ) -> Tuple[ProgramNode, List[IRInstruction], List[IRInstruction], Optional[Dict[str, Any]]]:
        """Compile source code through Lexer, Parser, Semantics, IR Gen, and Optimizer.

        Returns:
            (ast, unoptimized_ir, optimized_ir, optimization_report)
        """
        # 1. Lexing
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()

        # 2. Parsing
        parser = Parser(tokens)
        ast = parser.parse()

        # 3. Semantic Analysis
        self.semantic_analyzer.analyze(ast)

        # 4. IR Generation
        unoptimized_ir = self.ir_generator.generate(ast)

        # 5. Optimization
        if optimize:
            opt_report = self.optimizer.optimize(unoptimized_ir)
            optimized_ir = opt_report["optimized_ir"]
        else:
            optimized_ir = list(unoptimized_ir)
            opt_report = None

        return ast, unoptimized_ir, optimized_ir, opt_report

    def run_source(self, source_code: str, optimize: bool = True) -> Dict[str, Any]:
        """Compile and execute source code, returning execution metrics and outputs."""
        ast, unopt_ir, opt_ir, opt_report = self.compile(source_code, optimize=optimize)
        target_ir = opt_ir if optimize else unopt_ir

        exec_res = self.interpreter.execute(target_ir)
        exec_res["ir_instruction_count"] = len(target_ir)
        exec_res["optimized"] = optimize
        exec_res["optimization_report"] = opt_report
        exec_res["ir_text"] = pretty_print_ir(target_ir)

        return exec_res

