"""Compiler Optimization Passes for Three-Address-Code IR.

Implements five classical compiler optimization passes:
1. Constant Folding (CF)
2. Constant Propagation (CP)
3. Strength Reduction (SR)
4. Common Subexpression Elimination (CSE)
5. Dead Code Elimination (DCE)

Includes pass pipeline orchestrator with fixpoint convergence and per-pass instrumentation.
"""

import copy
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from track_f_compiler_optimization.src.ir import (
    IRInstruction,
    is_constant,
    to_constant_value,
)


class ConstantFoldingPass:
    """Evaluates constant arithmetic, comparisons, and constant conditional jumps."""

    name = "ConstantFolding"

    def run(self, instructions: List[IRInstruction]) -> List[IRInstruction]:
        optimized: List[IRInstruction] = []

        for inst in instructions:
            op = inst.op.upper()

            # Binary arithmetic folding
            if op in ("ADD", "SUB", "MUL", "DIV", "MOD") and is_constant(inst.arg1) and is_constant(inst.arg2):
                v1 = to_constant_value(inst.arg1)
                v2 = to_constant_value(inst.arg2)
                res = None
                if op == "ADD":
                    res = v1 + v2
                elif op == "SUB":
                    res = v1 - v2
                elif op == "MUL":
                    res = v1 * v2
                elif op == "DIV" and v2 != 0:
                    res = v1 // v2
                elif op == "MOD" and v2 != 0:
                    res = v1 % v2

                if res is not None:
                    optimized.append(IRInstruction(op="ASSIGN", arg1=str(res), result=inst.result))
                    continue

            # Binary comparison folding
            if op in ("CMP_EQ", "CMP_NE", "CMP_LT", "CMP_LE", "CMP_GT", "CMP_GE") and is_constant(inst.arg1) and is_constant(inst.arg2):
                v1 = to_constant_value(inst.arg1)
                v2 = to_constant_value(inst.arg2)
                res = None
                if op == "CMP_EQ":
                    res = 1 if v1 == v2 else 0
                elif op == "CMP_NE":
                    res = 1 if v1 != v2 else 0
                elif op == "CMP_LT":
                    res = 1 if v1 < v2 else 0
                elif op == "CMP_LE":
                    res = 1 if v1 <= v2 else 0
                elif op == "CMP_GT":
                    res = 1 if v1 > v2 else 0
                elif op == "CMP_GE":
                    res = 1 if v1 >= v2 else 0

                optimized.append(IRInstruction(op="ASSIGN", arg1=str(res), result=inst.result))
                continue

            # Constant conditional branch folding
            if op == "JUMP_IF_FALSE" and is_constant(inst.arg1):
                cond_val = to_constant_value(inst.arg1)
                if cond_val == 0:
                    # Branch is unconditionally taken
                    optimized.append(IRInstruction(op="JUMP", result=inst.result))
                else:
                    # Branch is never taken -> omit instruction
                    pass
                continue

            if op == "JUMP_IF_TRUE" and is_constant(inst.arg1):
                cond_val = to_constant_value(inst.arg1)
                if cond_val != 0:
                    optimized.append(IRInstruction(op="JUMP", result=inst.result))
                else:
                    pass
                continue

            optimized.append(inst)

        return optimized


class ConstantPropagationPass:
    """Propagates known constant values to downstream uses within basic blocks."""

    name = "ConstantPropagation"

    def run(self, instructions: List[IRInstruction]) -> List[IRInstruction]:
        optimized: List[IRInstruction] = []
        # Local constants mapping variable/temporary -> constant literal string
        constants: Dict[str, str] = {}

        for inst in instructions:
            # Clear constants map across basic block boundaries (labels and jumps)
            if inst.op in ("LABEL", "JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE"):
                constants.clear()
                optimized.append(inst)
                continue

            new_arg1 = inst.arg1
            new_arg2 = inst.arg2

            # Propagate to arg1
            if inst.arg1 is not None and inst.arg1 in constants:
                new_arg1 = constants[inst.arg1]

            # Propagate to arg2
            if inst.arg2 is not None and inst.arg2 in constants:
                new_arg2 = constants[inst.arg2]

            new_inst = IRInstruction(op=inst.op, arg1=new_arg1, arg2=new_arg2, result=inst.result)
            optimized.append(new_inst)

            # Record or invalidate constants defined by this instruction
            if new_inst.result is not None:
                if new_inst.op == "ASSIGN" and is_constant(new_inst.arg1):
                    constants[new_inst.result] = new_inst.arg1
                else:
                    # Reassigned non-constant value: invalidate
                    constants.pop(new_inst.result, None)

        return optimized


class StrengthReductionPass:
    """Replaces expensive algebraic operations with cheaper equivalents."""

    name = "StrengthReduction"

    def run(self, instructions: List[IRInstruction]) -> List[IRInstruction]:
        optimized: List[IRInstruction] = []

        for inst in instructions:
            op = inst.op.upper()

            # Multiply by 2 -> Add with self (x * 2 -> x + x)
            if op == "MUL":
                if inst.arg2 == "2" and not is_constant(inst.arg1):
                    optimized.append(IRInstruction(op="ADD", arg1=inst.arg1, arg2=inst.arg1, result=inst.result))
                    continue
                if inst.arg1 == "2" and not is_constant(inst.arg2):
                    optimized.append(IRInstruction(op="ADD", arg1=inst.arg2, arg2=inst.arg2, result=inst.result))
                    continue

                # Multiply by 1 -> Assign (x * 1 -> x)
                if inst.arg2 == "1":
                    optimized.append(IRInstruction(op="ASSIGN", arg1=inst.arg1, result=inst.result))
                    continue
                if inst.arg1 == "1":
                    optimized.append(IRInstruction(op="ASSIGN", arg1=inst.arg2, result=inst.result))
                    continue

                # Multiply by 0 -> Assign 0 (x * 0 -> 0)
                if inst.arg1 == "0" or inst.arg2 == "0":
                    optimized.append(IRInstruction(op="ASSIGN", arg1="0", result=inst.result))
                    continue

            # Addition identities (x + 0 -> x)
            if op == "ADD":
                if inst.arg2 == "0":
                    optimized.append(IRInstruction(op="ASSIGN", arg1=inst.arg1, result=inst.result))
                    continue
                if inst.arg1 == "0":
                    optimized.append(IRInstruction(op="ASSIGN", arg1=inst.arg2, result=inst.result))
                    continue

            # Subtraction identity (x - 0 -> x)
            if op == "SUB":
                if inst.arg2 == "0":
                    optimized.append(IRInstruction(op="ASSIGN", arg1=inst.arg1, result=inst.result))
                    continue

            # Division by 1 (x / 1 -> x)
            if op == "DIV":
                if inst.arg2 == "1":
                    optimized.append(IRInstruction(op="ASSIGN", arg1=inst.arg1, result=inst.result))
                    continue

            optimized.append(inst)

        return optimized


class CommonSubexpressionEliminationPass:
    """Detects repeated expressions within basic blocks and reuses computed results."""

    name = "CommonSubexpressionElimination"

    def run(self, instructions: List[IRInstruction]) -> List[IRInstruction]:
        optimized: List[IRInstruction] = []
        # Maps expression signature (op, arg1, arg2) -> temporary or variable holding result
        available_exprs: Dict[Tuple[str, str, str], str] = {}

        for inst in instructions:
            # Control flow boundaries reset available expressions
            if inst.op in ("LABEL", "JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE"):
                available_exprs.clear()
                optimized.append(inst)
                continue

            op = inst.op.upper()

            # Only pure binary operators qualify for CSE
            if op in ("ADD", "SUB", "MUL", "DIV", "MOD", "CMP_EQ", "CMP_NE", "CMP_LT", "CMP_LE", "CMP_GT", "CMP_GE"):
                # Canonicalize symmetric commutative operators
                arg1, arg2 = inst.arg1, inst.arg2
                if op in ("ADD", "MUL", "CMP_EQ", "CMP_NE") and arg1 > arg2:
                    arg1, arg2 = arg2, arg1

                key = (op, arg1, arg2)

                if key in available_exprs:
                    # Reuse existing result
                    prev_var = available_exprs[key]
                    optimized.append(IRInstruction(op="ASSIGN", arg1=prev_var, result=inst.result))
                    continue
                else:
                    optimized.append(inst)
                    if inst.result is not None:
                        available_exprs[key] = inst.result

                # Invalidate any expressions referencing the newly defined variable
                if inst.result is not None:
                    def_var = inst.result
                    stale_keys = [k for k in available_exprs if k[1] == def_var or k[2] == def_var]
                    for sk in stale_keys:
                        del available_exprs[sk]
            else:
                optimized.append(inst)
                # Assignment also invalidates expressions containing overwritten variable
                if inst.result is not None:
                    def_var = inst.result
                    stale_keys = [k for k in available_exprs if k[1] == def_var or k[2] == def_var]
                    for sk in stale_keys:
                        del available_exprs[sk]

        return optimized


class DeadCodeEliminationPass:
    """Removes unused assignments and unreachable instructions after jumps."""

    name = "DeadCodeElimination"

    def run(self, instructions: List[IRInstruction]) -> List[IRInstruction]:
        # Pass A: Remove unreachable code blocks after unconditional jumps
        reachable: List[IRInstruction] = []
        is_dead_block = False

        for inst in instructions:
            if inst.op == "LABEL":
                is_dead_block = False
                reachable.append(inst)
            elif is_dead_block:
                # Discard unreachable instruction
                continue
            elif inst.op == "JUMP":
                reachable.append(inst)
                is_dead_block = True
            else:
                reachable.append(inst)

        # Pass B: Remove redundant jump to immediate next label (e.g. goto L1; L1:)
        cleaned_jumps: List[IRInstruction] = []
        n_reach = len(reachable)
        for i in range(n_reach):
            inst = reachable[i]
            if inst.op == "JUMP" and i + 1 < n_reach:
                next_inst = reachable[i + 1]
                if next_inst.op == "LABEL" and next_inst.result == inst.result:
                    # Redundant jump immediately preceding destination label
                    continue
            cleaned_jumps.append(inst)

        # Pass C: Backward liveness analysis for dead temporaries and unused variables
        # Collect all variables that are read downstream
        used_vars: Set[str] = set()
        for inst in cleaned_jumps:
            used_vars.update(inst.get_used_vars())

        optimized: List[IRInstruction] = []
        for inst in cleaned_jumps:
            # If instruction defines a variable or temporary that is never used anywhere in the program, prune it
            if inst.is_pure() and inst.result is not None:
                if inst.result not in used_vars:
                    continue

            optimized.append(inst)

        return optimized


class CompilerOptimizer:
    """Manages pass execution pipelines and fixpoint optimization convergence."""

    AVAILABLE_PASSES = {
        "CF": ConstantFoldingPass,
        "CP": ConstantPropagationPass,
        "SR": StrengthReductionPass,
        "CSE": CommonSubexpressionEliminationPass,
        "DCE": DeadCodeEliminationPass,
    }

    def __init__(self, enabled_pass_keys: Optional[List[str]] = None):
        if enabled_pass_keys is None:
            # Standard classical compilation pass order
            self.pass_keys = ["CP", "CF", "SR", "CSE", "DCE"]
        else:
            self.pass_keys = enabled_pass_keys

    def optimize(
        self, instructions: List[IRInstruction], max_iterations: int = 10
    ) -> Dict[str, Any]:
        """Apply selected passes iteratively until reaching fixpoint."""
        current_ir = list(instructions)
        initial_count = len(current_ir)
        pass_metrics: List[Dict[str, Any]] = []

        start_time = time.perf_counter()

        for iteration in range(max_iterations):
            ir_before_iter = list(current_ir)

            for key in self.pass_keys:
                pass_cls = self.AVAILABLE_PASSES[key]
                pass_instance = pass_cls()

                t0 = time.perf_counter()
                count_before = len(current_ir)
                current_ir = pass_instance.run(current_ir)
                count_after = len(current_ir)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0

                pass_metrics.append({
                    "iteration": iteration + 1,
                    "pass_key": key,
                    "pass_name": pass_instance.name,
                    "instructions_before": count_before,
                    "instructions_after": count_after,
                    "reduction": count_before - count_after,
                    "runtime_ms": elapsed_ms,
                })

            if current_ir == ir_before_iter:
                # Fixpoint reached: instruction sequence is completely stable
                break

        total_compile_ms = (time.perf_counter() - start_time) * 1000.0
        final_count = len(current_ir)

        return {
            "initial_instruction_count": initial_count,
            "final_instruction_count": final_count,
            "instructions_reduced": initial_count - final_count,
            "reduction_fraction": (initial_count - final_count) / initial_count if initial_count > 0 else 0.0,
            "total_compile_time_ms": total_compile_ms,
            "pass_metrics": pass_metrics,
            "optimized_ir": current_ir,
        }
