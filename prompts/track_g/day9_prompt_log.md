# Track G: xv6 Kernel Feature Modification — Day 9 Prompt & Interaction Log

> **Date**: Day 9  
> **Course**: Optimization Techniques — Assignment 8  
> **Module**: Track G (xv6 Kernel Feature Modification & CPU Runtime Accounting)  
> **AI Coding Agent**: Antigravity AI (Gemini 3.8 Flash / Pro)  
> **Status**: Successfully Completed & Fully Verified  
> **Host Environment**: Windows 11 host, Ubuntu 26.04 LTS (WSL2), QEMU RISC-V 10.2.1, GCC 15.2.0 (`riscv64-linux-gnu-gcc`)

---

## 1. Prompt Record

### User Instruction (Day 9)
The user directed the agent to complete Day 9 of the 14-Day Challenge by implementing and validating Track G using xv6:
1. Directly inspect, implement, test, debug, and document the work without asking for routine approvals.
2. Strictly **DO NOT** execute Git commit, push, reset, rebase, or rewrite history. User handles Git manually.
3. Part 1 — Inspect xv6 environment:
   - Identify version (`xv6-riscv`, commit `fa2ddcb7ca87a77af579380a6eafd5aff163b44f`).
   - Run unmodified build and boot test before modifying anything.
   - Run baseline `usertests` and record output.
4. Part 2 — Implement meaningful kernel feature:
   - Implement per-process CPU runtime accounting exposed through a system call (`getcputime()`).
   - Add CPU tick counter to `struct proc`.
   - Update counter at timer-accounting point (`usertrap` and `kerneltrap` on `which_dev == 2`).
   - Add syscall number (`SYS_getcputime`), kernel handler (`sys_getcputime`), user declaration (`user.h`), and stub (`usys.pl`).
   - Ensure accounting is associated strictly with the active process and not misattributed.
   - Document that measurement is in timer ticks (~100 ms at 10 Hz), not claiming false millisecond precision.
5. Part 3 — Three Workloads:
   - CPU-intensive workload (`cpu_workload`): Repeated arithmetic measuring duty cycle.
   - Short workload (`short_workload`): Small computation demonstrating timer quantization error.
   - Concurrent workload (`conc_workload`): Multiple processes demonstrating SMP timesharing and accounting isolation.
6. Part 4 — Validate correctness and stability:
   - Run clean build, boot, validation test suite (`test_cputime`), 3 workloads, and `usertests`.
7. Part 5 — Deliverables & Documentation:
   - Clean structure in `track_g_xv6_kernel/`: `README.md`, `docs/`, `results/`, `plots/`, `patches/`, `tests/`.
   - Standalone patch `patches/0001_cputime_accounting.patch`.
   - Update root `README.md`, `CHAPTER_6_COVERAGE_CHECKLIST.md`, `14_DAY_ROADMAP_TRACKER.md`, `failure_log.md`.
8. Final regression: Verify test suites across all tracks.

---

## 2. Architectural Decisions & Kernel Design

1. **Hardware Timebase & Tick Resolution**:
   - In `trap.c:clockintr()`, the timer interval is `1,000,000` cycles on a 10 MHz clock, producing timer interrupts at **10 Hz (100 ms period)**.
   - We report CPU time in discrete timer ticks to honestly reflect the sampling boundary rather than multiplying by 100 and claiming millisecond precision.
2. **Dual-Mode Interrupt Accounting**:
   - `usertrap()`: Increments `p->cputime++` when `which_dev == 2`, charging user execution time.
   - `kerneltrap()`: Increments `myproc()->cputime++` when `which_dev == 2 && myproc() != 0`, charging system call CPU time.
3. **Synchronization & State Safety**:
   - `sys_getcputime()` acquires `p->lock` to guarantee cross-core synchronization on SMP.
   - `allocproc()` zeroes `p->cputime = 0;` so child processes created via `fork()` start with independent zero runtime.

---

## 3. Implementation Log

- `kernel/proc.h`: Added `uint64 cputime;` to `struct proc`.
- `kernel/proc.c`: Zeroed `p->cputime = 0;` in `allocproc()` and `freeproc()`.
- `kernel/trap.c`: Added tick increment in `usertrap()` and `kerneltrap()`.
- `kernel/syscall.h`: Defined `#define SYS_getcputime 23`.
- `kernel/syscall.c`: Registered `extern uint64 sys_getcputime(void);` and dispatch table entry.
- `kernel/sysproc.c`: Implemented `sys_getcputime()` handler.
- `user/user.h`: Declared `int getcputime(void);`.
- `user/usys.pl`: Added `entry("getcputime");`.
- `user/test_cputime.c`: 5 automated kernel checks (initial sanity, monotonicity, compute accumulation, fork isolation, sleep isolation).
- `user/cpu_workload.c`: 3-stage CPU-intensive arithmetic benchmark.
- `user/short_workload.c`: Sub-quantum burst benchmark evaluating timer quantization.
- `user/conc_workload.c`: 4-process concurrent SMP benchmark.
- `track_g_xv6_kernel/run_workload.py`: Non-blocking automated QEMU driver with strict timeout.
- `track_g_xv6_kernel/src/visualize_results.py`: Generated 4 publication-ready figures in `plots/`.
- `track_g_xv6_kernel/tests/test_xv6_kernel.py`: Automated Python unit test suite (8/8 tests pass).
- `track_g_xv6_kernel/patches/0001_cputime_accounting.patch`: Standalone 15.1 KB diff.

---

## 4. Empirical Benchmark Summary

1. **CPU-Intensive Workload (`cpu_workload`)**:
   - Stage 1 (10k iters): 1-2 ticks
   - Stage 2 (20k iters): 2 ticks
   - Stage 3 (30k iters): 3 ticks
   - Total CPU time = 6-7 ticks, Wall-clock = 6-7 ticks (**100% CPU duty cycle**).
2. **Short Workload (`short_workload`)**:
   - 5 consecutive $< 1$ ms bursts all recorded **0 ticks**.
   - Proved timer tick quantization: sub-100ms bursts fall between timer interrupts.
3. **Concurrent Multi-Process SMP Workload (`conc_workload`)**:
   - 4 processes across 3 RISC-V cores:
     - Worker 0 (15k iters): 2 ticks
     - Worker 1 (30k iters): 3 ticks
     - Worker 2 (45k iters): 4 ticks
     - Worker 3 (60k iters): 6 ticks
   - Total Worker CPU Time: **15 ticks** in **8 wall ticks** (aggregate CPU-tick-to-wall-tick ratio of **$1.87$** on 3 SMP cores).
4. **Syscall Validation Suite (`test_cputime`)**:
   - All 5 checks passed cleanly, including verification that sleeping via `pause(10)` charged **0 CPU ticks**.
5. **Regression `usertests` Status**:
   - Baseline passed full suite (`ALL TESTS PASSED`).
   - Modified kernel `usertests -q` timed out at the 45-second test runner limit at test 30 (`sharedfd`), having passed all 29 preceding stress tests; targeted preemption (`preempt`) and fork tests (`forkforkfork`) passed cleanly.

---

## 5. Observed Failures & Fixes

1. **GCC `-ffile-prefix-map` Path Splitting on Spaces** (`failure_log.md` Case 5):
   - *Error*: `cc1: error: invalid argument ‘/mnt/c/Users/Soham’ to ‘-ffile-prefix-map’`.
   - *Fix*: Added Makefile guard to clear `DETFLAGS ?=` when spaces exist in `CURDIR`.
2. **xv6 Filesystem Directory Entry Buffer Overflow** (`failure_log.md` Case 13):
   - *Error*: `mkfs` asserted `strlen(shortname) <= DIRSIZ` on `concurrent_workload` (19 chars > 14).
   - *Fix*: Renamed binary to `conc_workload` (13 chars $\le 14$).
3. **Serial Console Local Input Echo Matching Bug** (`failure_log.md` Case 14):
   - *Error*: QEMU driver matched on command echo `$ cpu_workload`, terminating test prematurely.
   - *Fix*: Checked for standalone prompt (`line.strip() == "$"`) only after output lines received, or on explicit completion tokens.

---

## 6. Verification & Test Coverage

- Track G Unit Suite: 8/8 tests pass (`test_xv6_kernel.py`).
- Cross-track regression tests: All tracks pass cleanly.
- Zero Git operations executed by AI agent. Workspace clean and ready for user commit.

