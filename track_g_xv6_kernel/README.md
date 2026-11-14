# Track G: xv6 Kernel Feature Modification & CPU Runtime Accounting

> **Course**: Optimization Techniques — Lab Assignment 8 (Day 9)  
> **Subsystem**: xv6-riscv Operating System Kernel  
> **Kernel Version**: MIT xv6-riscv (`fa2ddcb7ca87a77af579380a6eafd5aff163b44f`)  
> **Architecture**: 64-bit RISC-V (RV64GC), 3 SMP Cores, 128 MB RAM, QEMU `virt` machine

---

## 1. Overview

Track G implements **per-process CPU runtime accounting** in the MIT xv6-riscv operating system kernel. The feature tracks CPU execution time associated with each process across timer interrupts in both user and kernel modes, exposing this information to user-space applications through a newly implemented system call: `getcputime()`.

### Key Deliverables & Achievements
1. **Kernel Data Structure**: Extended `struct proc` with `uint64 cputime;` to track active execution ticks.
2. **Interrupt Accounting**: Instrumented `usertrap()` and `kerneltrap()` in `kernel/trap.c` to charge ticks to `myproc()` strictly on timer interrupts (`which_dev == 2`).
3. **New System Call**: Implemented `SYS_getcputime (23)` with thread-safe kernel handler `sys_getcputime()` and assembly stub in `user/usys.S`.
4. **Validation Test Suite**: Created `user/test_cputime.c` verifying initial sanity, monotonicity, compute accumulation, fork isolation, and sleeping isolation.
5. **Three Workloads**:
   - `cpu_workload`: Compute-heavy integer hashing measuring active CPU duty cycle ($100\%$).
   - `short_workload`: Sub-quantum burst benchmark demonstrating timer quantization ($0$ ticks for $<1$ ms tasks).
   - `conc_workload`: 4-process concurrent benchmark demonstrating SMP timesharing ($1.87\times$ multi-core speedup on 3 cores).
6. **Regression Invariance**: Verified that baseline `usertests` pass without regression.
7. **Complete Documentation & Patch**: Provided full architecture analysis, experimental evaluation, 16 viva Q&As, publication plots, and standalone git patch (`patches/0001_cputime_accounting.patch`).

---

## 2. Directory Layout

```text
track_g_xv6_kernel/
├── README.md                                    # This document
├── run_workload.py                              # Automated QEMU driver with non-blocking execution
├── xv6-riscv/                                   # Full kernel source tree
│   ├── kernel/
│   │   ├── proc.h / proc.c                      # cputime field, allocproc & freeproc initialization
│   │   ├── trap.c                               # Timer interrupt accounting (which_dev == 2)
│   │   ├── syscall.h / syscall.c                # SYS_getcputime definition & table dispatch
│   │   └── sysproc.c                            # sys_getcputime() handler
│   ├── user/
│   │   ├── user.h / usys.pl                     # User declaration & stub generation
│   │   ├── test_cputime.c                       # Automated kernel verification test suite
│   │   ├── cpu_workload.c                       # Workload 1: CPU-intensive arithmetic
│   │   ├── short_workload.c                     # Workload 2: Short burst quantization
│   │   └── conc_workload.c                      # Workload 3: Concurrent multi-process SMP
│   └── Makefile                                 # Build configuration with space-handling & UPROGS
├── docs/
│   ├── kernel_architecture.md                   # xv6 processes, trap handling, timers, scheduling
│   ├── implementation.md                        # Code modifications, design choices, DIRSIZ limit
│   ├── experimental_analysis.md                 # Baseline vs modified results, workloads, overhead
│   └── viva_questions.md                        # 16 academic viva defense Q&As
├── results/
│   ├── workload_cpu_intensive.txt               # Raw output from Workload 1
│   ├── workload_short.txt                       # Raw output from Workload 2
│   ├── workload_concurrent.txt                  # Raw output from Workload 3
│   └── test_cputime_results.txt                 # Raw output from test_cputime validation
├── plots/
│   ├── 01_workload_cputime_vs_walltime.png      # CPU ticks vs wall ticks across workloads
│   ├── 02_concurrent_smp_accounting.png         # Worker distribution & 187% SMP duty cycle
│   ├── 03_timer_tick_quantization_error.png     # Quantization error at 10 Hz tick rate
│   └── 04_active_vs_sleeping_accounting.png     # Active vs sleeping state isolation
├── patches/
│   └── 0001_cputime_accounting.patch            # Standalone diff containing all xv6 modifications
├── src/
│   └── visualize_results.py                     # Generator for all 4 plots
└── tests/
    └── test_xv6_kernel.py                       # Python unit test suite (8/8 tests pass)
```

---

## 3. Quickstart: Building & Running

### Prerequisites
WSL2 Ubuntu 26.04 LTS with:
- `gcc-riscv64-linux-gnu`
- `qemu-system-riscv`
- `make`
- `python3`

### Build the Kernel
```bash
cd track_g_xv6_kernel/xv6-riscv
make clean
make -j$(nproc)
```

### Run Automated Validation Test
```bash
python3 ../run_workload.py test_cputime
```

### Run Workloads
```bash
python3 ../run_workload.py cpu_workload
python3 ../run_workload.py short_workload
python3 ../run_workload.py conc_workload
```

### Run Python Regression Suite
```bash
python -m unittest discover -s track_g_xv6_kernel/tests -v
```

---

## 4. Key Empirical Findings

1. **Active Compute Tracking**: A compute-bound task running uninterrupted achieves **$100\%$ CPU duty cycle** (`cputime == uptime`).
2. **Sleeping Process Isolation**: Calling `pause(10)` causes 10 wall-clock ticks to elapse, but **$0$ CPU ticks** are charged to the process, proving sleeping processes do not accumulate CPU time.
3. **SMP Parallelism**: In `conc_workload`, 4 worker processes across 3 cores accumulated 15 CPU ticks within 8 wall-clock ticks, demonstrating a **$1.87\times$ parallel execution speedup**.
4. **Quantization Limit**: Tasks completing in $< 1$ ms register $0$ ticks due to the 100 ms periodic timer interval.

