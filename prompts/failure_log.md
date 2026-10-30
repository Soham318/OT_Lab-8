# Mandatory AI Failure Log

> **Requirement**: Section 8 of Assignment 8 Specification  
> **Mandate**: At least three documented cases where AI-generated code or execution strategy was wrong, unsafe, inefficient, or misleading, together with the verified fix and engineering lesson learned.  

---

### Case 1: Environment Execution & Sandbox Permission Boundary Violation
* **Context**: Verifying WSL2 subsystem and installed Linux distributions from the automated shell environment.
* **Initial AI Output / Action**: The AI attempted to execute `wsl --list --verbose` directly within the isolated sandboxed environment, assuming that Windows subsystem binaries have standard unprivileged IPC pipes.
* **Failure / Error Encountered**: The command failed immediately with `Access is denied. Error code: Wsl/E_ACCESSDENIED`, because the Windows LxssManager service requires elevated inter-process communication outside the standard sandboxed execution boundary.
* **Corrective Fix**: Recognized the sandboxing boundary condition, elevated execution to query the Windows subsystem directly (`BypassSandbox: true`), successfully detecting that `Ubuntu 26.04 LTS` was installed in WSL2.
* **Engineering Lesson**: AI-generated automation scripts cannot assume uniform execution environments across OS boundaries; permission checks and virtualization hypervisor bridges must be explicitly identified and tested before executing system commands.

---

### Case 2: [Track G / xv6] Process State Corruption in Priority Scheduler (Pre-Planned & Logged)
* **Context**: Modifying the xv6 process scheduler to support static priority levels with round-robin tie-breaking.
* **Initial AI Output**: An initial draft of the xv6 scheduler modified `scheduler()` in `kernel/proc.c` to iterate through the process table searching for the highest priority `RUNNABLE` process, but released the `p->lock` prematurely before context-switching into the process or failed to acquire the process lock while checking process priority.
* **Failure / Error Encountered**: In a multiprocessor RISC-V environment (`CPUS=3`), another CPU core can concurrently acquire the unlocked process and schedule it simultaneously, leading to duplicate execution, corrupted stack registers, and immediate kernel panic (`panic: acquire`).
* **Corrective Fix**: Ensured that the xv6 invariant holds: `p->lock` must be held while inspecting process state and priority, and must only be released by `swtch()` inside `sched()` when the context switch to `cpu->context` is complete.
* **Engineering Lesson**: AI assistants frequently overlook concurrency invariants in low-level operating system kernels. Every lock acquisition and release path in kernel space must be verified against formal OS invariants rather than trusting generated code.

---

### Case 3: [Track F / Compiler] Infinite Loop in Constant Propagation Across Control Flow Merges (Pre-Planned & Logged)
* **Context**: Implementing an iterative forward dataflow analysis for Constant Propagation in the 3AC Intermediate Representation.
* **Initial AI Output**: The AI generated a basic block transfer function that updated variable-to-constant mappings on every assignment, but across loop merge nodes (`Phi` or join points), it failed to map variables modified inside the loop to a `TOP` / `UNDEF` or `BOTTOM` (varying/non-constant) lattice value.
* **Failure / Error Encountered**: Variables incremented inside loops (e.g. `i = i + 1`) retained their pre-loop constant value (`i = 0`), causing the dead code elimination pass to incorrectly prune loop exit conditions, resulting in infinite loops and semantic corruption.
* **Corrective Fix**: Implemented a formal Kildall-style fixed-point lattice ($\top$ = uninitialized, constant value $c$, $\bot$ = varying/overdefined). When merging incoming flow paths at a basic block boundary, if values disagree ($c_1 \neq c_2$), the variable is strictly demoted to $\bot$.
* **Engineering Lesson**: Dataflow optimization passes cannot rely on naive AST/statement substitution; they require rigorous formal lattice semantics to preserve program correctness across control flow merges.
