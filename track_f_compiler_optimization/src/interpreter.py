"""Virtual Machine / Interpreter for Three-Address-Code IR.

Executes IR instructions, verifies program semantics, records output values,
and tracks cycle/step execution counts and wall-clock execution time.
"""

import time
from typing import Any, Dict, List, Optional, Tuple
from track_f_compiler_optimization.src.ir import IRInstruction, is_constant, to_constant_value


class InterpreterRuntimeError(Exception):
    """Raised during runtime execution (e.g. division by zero, unassigned variable)."""
    pass


class IRInterpreter:
    """Executes Three-Address-Code IR instructions in an isolated environment."""

    def __init__(self, max_steps: int = 500_000):
        self.max_steps = max_steps
        self.env: Dict[str, int] = {}
        self.output: List[int] = []
        self.step_count = 0

    def _resolve(self, operand: Optional[str]) -> int:
        if operand is None:
            raise InterpreterRuntimeError("Cannot resolve None operand")
        if is_constant(operand):
            return to_constant_value(operand)
        if operand not in self.env:
            raise InterpreterRuntimeError(f"Variable or temporary '{operand}' read before assignment")
        return self.env[operand]

    def execute(
        self, instructions: List[IRInstruction], initial_env: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Execute IR instruction sequence.

        Returns:
            Dictionary containing:
            - output: list of printed integers
            - final_env: state of variables
            - step_count: total executed instruction count
            - execution_time_ms: elapsed wall-clock runtime
        """
        self.env = initial_env.copy() if initial_env else {}
        self.output = []
        self.step_count = 0

        # Build label index map
        label_map: Dict[str, int] = {}
        for idx, inst in enumerate(instructions):
            if inst.op == "LABEL":
                if inst.result in label_map:
                    raise InterpreterRuntimeError(f"Duplicate label: {inst.result}")
                label_map[inst.result] = idx

        pc = 0
        n_instructions = len(instructions)
        start_time = time.perf_counter()

        while pc < n_instructions:
            if self.step_count >= self.max_steps:
                raise InterpreterRuntimeError(
                    f"Execution exceeded safety limit of {self.max_steps} steps (possible infinite loop)"
                )

            inst = instructions[pc]
            self.step_count += 1
            op = inst.op.upper()

            if op == "LABEL":
                pc += 1

            elif op == "JUMP":
                if inst.result not in label_map:
                    raise InterpreterRuntimeError(f"Jump to undefined label: {inst.result}")
                pc = label_map[inst.result]

            elif op == "JUMP_IF_FALSE":
                cond_val = self._resolve(inst.arg1)
                if cond_val == 0:
                    if inst.result not in label_map:
                        raise InterpreterRuntimeError(f"Jump to undefined label: {inst.result}")
                    pc = label_map[inst.result]
                else:
                    pc += 1

            elif op == "JUMP_IF_TRUE":
                cond_val = self._resolve(inst.arg1)
                if cond_val != 0:
                    if inst.result not in label_map:
                        raise InterpreterRuntimeError(f"Jump to undefined label: {inst.result}")
                    pc = label_map[inst.result]
                else:
                    pc += 1

            elif op == "PRINT":
                val = self._resolve(inst.arg1)
                self.output.append(val)
                pc += 1

            elif op == "ASSIGN":
                val = self._resolve(inst.arg1)
                self.env[inst.result] = val
                pc += 1

            elif op in ("ADD", "SUB", "MUL", "DIV", "MOD"):
                v1 = self._resolve(inst.arg1)
                v2 = self._resolve(inst.arg2)
                if op == "ADD":
                    res = v1 + v2
                elif op == "SUB":
                    res = v1 - v2
                elif op == "MUL":
                    res = v1 * v2
                elif op == "DIV":
                    if v2 == 0:
                        raise InterpreterRuntimeError("Division by zero in IR execution")
                    res = v1 // v2
                elif op == "MOD":
                    if v2 == 0:
                        raise InterpreterRuntimeError("Modulo by zero in IR execution")
                    res = v1 % v2
                self.env[inst.result] = res
                pc += 1

            elif op in ("CMP_EQ", "CMP_NE", "CMP_LT", "CMP_LE", "CMP_GT", "CMP_GE"):
                v1 = self._resolve(inst.arg1)
                v2 = self._resolve(inst.arg2)
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
                self.env[inst.result] = res
                pc += 1

            else:
                raise InterpreterRuntimeError(f"Unknown IR opcode: {inst.op}")

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "output": list(self.output),
            "final_env": dict(self.env),
            "step_count": self.step_count,
            "execution_time_ms": elapsed_ms,
        }

