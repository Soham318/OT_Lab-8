"""Automated Test Suite for Track F: Compiler Optimization.

Covers:
1. Lexer and parser correctness & operator precedence
2. Syntax error detection (LexerError, ParserError)
3. Semantic analysis and undefined variable error detection (SemanticError)
4. Three-Address-Code IR generation
5. Independent optimization pass verification:
   - Constant Folding (CF)
   - Constant Propagation (CP)
   - Strength Reduction (SR)
   - Common Subexpression Elimination (CSE)
   - Dead Code Elimination (DCE)
6. Pipeline interactions and fixpoint convergence
7. Pass selection BILP optimization model vs. exhaustive search
8. Semantic execution parity between unoptimized and optimized IR
9. Complex control-flow, while loops, and observable side-effect preservation
"""

import unittest
from track_f_compiler_optimization.src.compiler import MiniCompiler
from track_f_compiler_optimization.src.ir import IRInstruction
from track_f_compiler_optimization.src.lexer import Lexer, LexerError
from track_f_compiler_optimization.src.optimizer import (
    CommonSubexpressionEliminationPass,
    CompilerOptimizer,
    ConstantFoldingPass,
    ConstantPropagationPass,
    DeadCodeEliminationPass,
    StrengthReductionPass,
)
from track_f_compiler_optimization.src.parser import Parser, ParserError
from track_f_compiler_optimization.src.pass_selector import PassSelectionProblem
from track_f_compiler_optimization.src.semantic_analyzer import SemanticAnalyzer, SemanticError


class TestCompilerOptimization(unittest.TestCase):
    """Unit tests for the mini-compiler frontend, IR, optimizer passes, and VM."""

    def setUp(self):
        self.compiler = MiniCompiler()

    def test_01_lexer_and_parser_precedence(self):
        """Verify that operator precedence (multiplication before addition) is properly parsed."""
        code = "x = 2 + 3 * 4;"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        # AST must be Program -> Assign(x, BinaryOp('+', 2, BinaryOp('*', 3, 4)))
        self.assertEqual(len(ast.statements), 1)
        assign_node = ast.statements[0]
        self.assertEqual(assign_node.target, "x")
        self.assertEqual(assign_node.value.op, "+")
        self.assertEqual(assign_node.value.left.value, 2)
        self.assertEqual(assign_node.value.right.op, "*")
        self.assertEqual(assign_node.value.right.left.value, 3)
        self.assertEqual(assign_node.value.right.right.value, 4)

    def test_02_syntax_errors_handled(self):
        """Verify that syntax errors raise descriptive ParserError or LexerError."""
        # Unrecognized character
        with self.assertRaises(LexerError):
            Lexer("x = @ + 5;").tokenize()

        # Missing closing parenthesis in while condition
        with self.assertRaises(ParserError):
            tokens = Lexer("while (x > 0 { x = x - 1; }").tokenize()
            Parser(tokens).parse()

        # Missing assignment expression
        with self.assertRaises(ParserError):
            tokens = Lexer("x = ;").tokenize()
            Parser(tokens).parse()

    def test_03_semantic_analyzer_undefined_variable(self):
        """Verify that using an uninitialized variable raises SemanticError."""
        code = "y = x + 10;"  # x is never defined
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        ast = Parser(tokens).parse()

        analyzer = SemanticAnalyzer()
        with self.assertRaises(SemanticError) as ctx:
            analyzer.analyze(ast)
        self.assertIn("undefined variable 'x'", str(ctx.exception))

    def test_04_ir_generation(self):
        """Verify generation of Three-Address-Code instructions."""
        code = """
        x = 5;
        if (x > 0) {
            print(x * 2);
        }
        """
        _, unopt_ir, _, _ = self.compiler.compile(code, optimize=False)
        self.assertGreater(len(unopt_ir), 3)

        opcodes = [inst.op for inst in unopt_ir]
        self.assertIn("ASSIGN", opcodes)
        self.assertIn("CMP_GT", opcodes)
        self.assertIn("JUMP_IF_FALSE", opcodes)
        self.assertIn("MUL", opcodes)
        self.assertIn("PRINT", opcodes)

    def test_05_constant_folding_pass(self):
        """Verify compile-time evaluation of constant expressions (4 * 5 + 2 -> 22)."""
        instructions = [
            IRInstruction(op="MUL", arg1="4", arg2="5", result="t0"),
            IRInstruction(op="ADD", arg1="t0", arg2="2", result="t1"),
            IRInstruction(op="ASSIGN", arg1="t1", result="x"),
        ]
        # First step folds 4 * 5 to 20
        pass_cf = ConstantFoldingPass()
        opt1 = pass_cf.run(instructions)
        self.assertEqual(opt1[0].op, "ASSIGN")
        self.assertEqual(opt1[0].arg1, "20")

        # Combining with propagation yields 20 + 2 -> 22
        pass_cp = ConstantPropagationPass()
        opt2 = pass_cp.run(opt1)
        opt3 = pass_cf.run(opt2)
        self.assertEqual(opt3[1].op, "ASSIGN")
        self.assertEqual(opt3[1].arg1, "22")

    def test_06_constant_propagation_pass(self):
        """Verify propagation of constants across basic blocks."""
        instructions = [
            IRInstruction(op="ASSIGN", arg1="10", result="a"),
            IRInstruction(op="ADD", arg1="a", arg2="5", result="t0"),
            IRInstruction(op="ASSIGN", arg1="t0", result="b"),
        ]
        pass_cp = ConstantPropagationPass()
        opt = pass_cp.run(instructions)
        # arg1 in ADD must be replaced with "10"
        self.assertEqual(opt[1].arg1, "10")

    def test_07_strength_reduction_pass(self):
        """Verify strength reduction transforms (x * 2 -> x + x, x * 1 -> x, x * 0 -> 0)."""
        instructions = [
            IRInstruction(op="MUL", arg1="y", arg2="2", result="t0"),
            IRInstruction(op="MUL", arg1="z", arg2="1", result="t1"),
            IRInstruction(op="MUL", arg1="w", arg2="0", result="t2"),
            IRInstruction(op="ADD", arg1="v", arg2="0", result="t3"),
        ]
        pass_sr = StrengthReductionPass()
        opt = pass_sr.run(instructions)

        self.assertEqual(opt[0].op, "ADD")
        self.assertEqual(opt[0].arg1, "y")
        self.assertEqual(opt[0].arg2, "y")

        self.assertEqual(opt[1].op, "ASSIGN")
        self.assertEqual(opt[1].arg1, "z")

        self.assertEqual(opt[2].op, "ASSIGN")
        self.assertEqual(opt[2].arg1, "0")

        self.assertEqual(opt[3].op, "ASSIGN")
        self.assertEqual(opt[3].arg1, "v")

    def test_08_common_subexpression_elimination_pass(self):
        """Verify detection and reuse of redundant expressions within basic blocks."""
        instructions = [
            IRInstruction(op="ADD", arg1="a", arg2="b", result="t0"),
            IRInstruction(op="ASSIGN", arg1="t0", result="x"),
            IRInstruction(op="ADD", arg1="a", arg2="b", result="t1"),  # redundant!
            IRInstruction(op="ASSIGN", arg1="t1", result="y"),
        ]
        pass_cse = CommonSubexpressionEliminationPass()
        opt = pass_cse.run(instructions)

        # Third instruction must become ASSIGN t0, None, t1
        self.assertEqual(opt[2].op, "ASSIGN")
        self.assertEqual(opt[2].arg1, "t0")

    def test_09_dead_code_elimination_pass(self):
        """Verify dead temporary removal and unreachable block elimination."""
        instructions = [
            IRInstruction(op="ADD", arg1="1", arg2="2", result="t_dead"),  # never used!
            IRInstruction(op="ASSIGN", arg1="10", result="x"),
            IRInstruction(op="JUMP", result="L_target"),
            IRInstruction(op="ASSIGN", arg1="999", result="unreachable_var"),  # unreachable!
            IRInstruction(op="LABEL", result="L_target"),
            IRInstruction(op="PRINT", arg1="x"),
        ]
        pass_dce = DeadCodeEliminationPass()
        opt = pass_dce.run(instructions)

        defined_results = [inst.result for inst in opt]
        self.assertNotIn("t_dead", defined_results)
        self.assertNotIn("unreachable_var", defined_results)

    def test_10_compiler_decision_model_milp_vs_exhaustive(self):
        """Verify that SciPy MILP pass selection produces optimal subset matching exhaustive search."""
        problem = PassSelectionProblem()
        budget = 6.0

        milp_sol = problem.solve_milp(compile_time_budget=budget)
        exh_sol = problem.solve_exhaustive(compile_time_budget=budget)

        self.assertAlmostEqual(milp_sol["net_objective_value"], exh_sol["best_value"], places=4)
        self.assertEqual(sorted(milp_sol["selected_passes"]), sorted(exh_sol["selected_passes"]))
        self.assertLessEqual(milp_sol["total_compile_cost"], budget)

    def test_11_original_vs_optimized_execution_parity(self):
        """Verify unoptimized and optimized code produce identical observable output."""
        code = """
        sum = 0;
        i = 1;
        while (i <= 10) {
            # Redundant arithmetic and dead computations
            dead_val = 4 * 5 + 2;
            c1 = i * 2;
            c2 = i * 2;
            sum = sum + c1 + c2;
            i = i + 1;
        }
        print(sum);
        """
        unopt_res = self.compiler.run_source(code, optimize=False)
        opt_res = self.compiler.run_source(code, optimize=True)

        self.assertEqual(unopt_res["output"], opt_res["output"])
        self.assertEqual(opt_res["output"], [220])
        self.assertLess(opt_res["ir_instruction_count"], unopt_res["ir_instruction_count"])


if __name__ == "__main__":
    unittest.main()

