# Track G Implementation Details: Per-Process CPU Runtime Accounting

> **System Call**: `getcputime(void)`  
> **Syscall Number**: `SYS_getcputime (23)`  
> **Accounting Metric**: Hardware timer ticks ($\approx 100$ ms per tick at 10 Hz)  
> **Target Kernel**: MIT xv6-riscv

---

## 1. Summary of Changes

The implementation required modifying 7 existing kernel and user-space files, creating 4 new user programs, and adding Makefile support:

| File Modified / Created | Component | Purpose of Modification |
| :--- | :--- | :--- |
| `kernel/proc.h` | Kernel Data Structures | Added `uint64 cputime;` to `struct proc`. |
| `kernel/proc.c` | Process Lifecycle | Initialized `p->cputime = 0;` in `allocproc()` and reset in `freeproc()`. |
| `kernel/trap.c` | Interrupt Accounting | Incremented `p->cputime++` in `usertrap()` and `kerneltrap()` upon timer interrupts (`which_dev == 2`). |
| `kernel/syscall.h` | System Call Definitions | Defined `#define SYS_getcputime 23`. |
| `kernel/syscall.c` | Syscall Dispatcher | Registered `extern uint64 sys_getcputime(void);` and mapped `[SYS_getcputime] = sys_getcputime`. |
| `kernel/sysproc.c` | Syscall Implementation | Implemented `sys_getcputime()` returning `p->cputime` under `p->lock`. |
| `user/user.h` | User-space Header | Declared user-visible prototype `int getcputime(void);`. |
| `user/usys.pl` | Assembly Stub Generator | Added `entry("getcputime");` generating assembly stub in `user/usys.S`. |
| `Makefile` | Build Driver | Added new user programs to `UPROGS` and handled spaces in build directories for `DETFLAGS`. |
| `user/test_cputime.c` | Verification Test Suite | 5 automated tests: sanity, monotonicity, compute accumulation, fork isolation, sleep isolation. |
| `user/cpu_workload.c` | Workload 1 | CPU-intensive arithmetic benchmark comparing CPU runtime against wall-clock time. |
| `user/short_workload.c` | Workload 2 | Sub-quantum burst benchmark demonstrating timer quantization error. |
| `user/conc_workload.c` | Workload 3 | 4-process concurrent benchmark demonstrating SMP multi-core timesharing and accounting isolation. |

---

## 2. Key Design Decisions

### A. Measurement Unit: Timer Ticks vs. Milliseconds
- The xv6 timer interrupt frequency is determined by `w_stimecmp(r_time() + 1000000)` in `kernel/trap.c:clockintr()`.
- On the QEMU `virt` machine with a 10 MHz clock, $1,000,000$ cycles corresponds to:
  $$\text{Period } T = \frac{1,000,000}{10,000,000 \text{ cycles/sec}} = 0.10 \text{ seconds} = 100 \text{ milliseconds}$$
- Because timer interrupts occur strictly at 10 Hz, **we deliberately report process CPU runtime in units of timer ticks**, rather than multiplying by 100 and claiming millisecond precision.
- Stating the measurement in ticks honestly communicates the resolution boundary of periodic timer sampling.

### B. Accounting Point: User Mode & Kernel Mode
- **User Mode (`usertrap`)**: When a timer interrupt fires while a user program is executing, the CPU was running user instructions for process `p`. We increment `p->cputime++` before calling `yield()`.
- **Kernel Mode (`kerneltrap`)**: When a timer interrupt fires while the kernel is executing a system call on behalf of process `p`, that core was burning CPU cycles servicing the process. We increment `myproc()->cputime++` before calling `yield()`.
- This provides unified accounting for both user computation and system call execution overhead.

### C. Concurrency, Atomicity & Locking
- In `sys_getcputime()`:
  ```c
  uint64
  sys_getcputime(void)
  {
    struct proc *p = myproc();
    uint64 ct;

    if (p == 0)
      return -1;

    acquire(&p->lock);
    ct = p->cputime;
    release(&p->lock);

    return ct;
  }
  ```
- While 64-bit integer loads and stores are atomic on 64-bit RISC-V (`ld`/`sd`), acquiring `p->lock` guarantees memory barrier semantics across SMP cores, ensuring consistent state across cores.

### D. Child Process Initialization
- In Unix semantics (such as `getrusage()` or `times()`), child processes start with zero accumulated CPU time.
- By zeroing `p->cputime = 0;` inside `allocproc()`, newly created processes via `fork()` always begin with independent runtime accounting.

---

## 3. Directory Filename Limit Handling (`DIRSIZ = 14`)

During initial workload testing, `mkfs` aborted with:
```text
mkfs: mkfs/mkfs.c:154: main: Assertion `strlen(shortname) <= DIRSIZ' failed.
```
- In `kernel/fs.h`, xv6 directory entries are fixed-size structures with `#define DIRSIZ 14`.
- The initial filename `concurrent_workload` was 19 characters, exceeding `DIRSIZ`.
- We renamed the file and binary to `conc_workload` (13 characters $\le 14$), adhering strictly to the filesystem format.

