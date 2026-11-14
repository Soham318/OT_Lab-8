# Academic Viva Defense: xv6 Kernel Optimization & Feature Modification

> **Track**: Track G — Operating System Optimization  
> **Topic**: Per-Process CPU Runtime Accounting in xv6-riscv  
> **Scope**: 16 Comprehensive Viva Questions & In-Depth Technical Answers

---

### Q1: What is the architectural difference between global system uptime and per-process CPU runtime?
**Answer**:  
Global system uptime (`ticks` in xv6) tracks total elapsed wall-clock timer interrupts since the kernel booted, incremented once per tick regardless of what is executing. In contrast, per-process CPU runtime (`p->cputime`) tracks only the active CPU execution time consumed by a specific process. If a process is blocked waiting for I/O or sleeping via `pause()`, global uptime continues to advance, but the process's CPU runtime remains constant.

---

### Q2: How are timer interrupts generated and routed in xv6 on RISC-V?
**Answer**:  
In QEMU RISC-V `virt` machines, timer interrupts are driven by the hardware `mtime` register. In supervisor mode, supervisor timer interrupts are scheduled by writing the target threshold to `stimecmp` via `w_stimecmp(r_time() + 1000000)`. When `r_time()` exceeds `stimecmp`, a supervisor timer interrupt (`scause = 0x8000000000000005L`) is triggered. In `trap.c`, `devintr()` claims this interrupt and delegates to `clockintr()`.

---

### Q3: What is the exact timer tick frequency in xv6-riscv, and what does one tick represent in physical time?
**Answer**:  
In `clockintr()`, the timer interval is set to $1,000,000$ clock cycles. Because QEMU's RISC-V hardware clock runs at 10 MHz ($10,000,000$ cycles per second), the timer interrupt period is:
$$T = \frac{1,000,000 \text{ cycles}}{10,000,000 \text{ cycles/sec}} = 0.10 \text{ seconds} = 100 \text{ ms}$$
Thus, timer ticks occur at approximately **10 Hz** (10 interrupts per second). One timer tick represents roughly 100 milliseconds of elapsed CPU time.

---

### Q4: Why is it mathematically incorrect to claim millisecond precision when multiplying ticks by 100?
**Answer**:  
Multiplying discrete timer ticks by 100 converts the scale to milliseconds but does not change the underlying measurement resolution. A process that runs for 5 milliseconds will register 0 ticks ($0 \times 100 = 0$ ms), while a process running for 105 milliseconds may register either 1 or 2 ticks (100 ms or 200 ms). Because the measurement is quantized to 100 ms boundaries, claiming millisecond precision is deceptive; reporting in raw timer ticks accurately reflects the 100 ms quantization error.

---

### Q5: How does xv6 isolate CPU accounting between user-mode execution and kernel-mode system call execution?
**Answer**:  
When a timer interrupt fires, the CPU traps into either `usertrap()` (if the interrupt occurred while executing in user mode) or `kerneltrap()` (if the interrupt occurred while executing kernel code on behalf of a process). By accounting for `p->cputime++` in both `usertrap()` and `kerneltrap()`, our implementation captures both user-level compute time and kernel-level system call execution time, attributing both to the calling process.

---

### Q6: Why does calling `pause(10)` not increase the process's `cputime` counter?
**Answer**:  
When a process invokes `pause(10)`, it calls `sleep(&ticks, &tickslock)`. The kernel transitions the process state to `p->state = SLEEPING` and calls `sched()` to yield the CPU. While sleeping, the process is removed from the CPU and is not scheduled by `scheduler()`. When timer interrupts occur, `myproc()` on that core is either running another process or idle. Consequently, `usertrap()` and `kerneltrap()` are never invoked for the sleeping process, ensuring zero CPU ticks are charged during sleep.

---

### Q7: What locking invariants must be respected when reading or modifying `p->cputime`?
**Answer**:  
In xv6, `p->lock` protects the process control block against concurrent access across SMP cores. When reading `p->cputime` in `sys_getcputime()`, acquiring `p->lock` (`acquire(&p->lock)`) ensures a memory barrier and synchronized state read. When writing `p->cputime++`, the update is executed on the specific CPU core currently executing `myproc()`, avoiding race conditions with other cores.

---

### Q8: What happens to `p->cputime` when a process calls `fork()`?
**Answer**:  
In `kfork()` (`kernel/proc.c`), the child process is allocated via `allocproc()`. In our implementation, `allocproc()` explicitly initializes `p->cputime = 0;`. Therefore, the child does not inherit the parent's accumulated CPU runtime. Each child begins with its own clean accounting slate, matching standard POSIX `times()` and `getrusage()` behavior.

---

### Q9: Trace the complete execution path when a user program calls `getcputime()`.
**Answer**:  
1. **User Call**: Application executes `getcputime()`.
2. **User Stub**: `user/usys.S` loads `23` (`SYS_getcputime`) into register `a7` and executes `ecall`.
3. **Hardware Trap**: Hardware elevates privilege to supervisor mode and jumps to `stvec` (`trampoline.S`).
4. **Trampoline**: `uservec` saves registers to `p->trapframe` and calls `usertrap()`.
5. **Trap Handler**: `usertrap()` calls `syscall()`.
6. **Syscall Dispatch**: `syscall()` retrieves `num = p->trapframe->a7` and invokes `sys_getcputime()`.
7. **Syscall Function**: `sys_getcputime()` acquires `p->lock`, reads `p->cputime`, releases `p->lock`, and returns the value.
8. **Return Path**: The return value is stored in `p->trapframe->a0`. `usertrap()` invokes `prepare_return()`, restoring user registers and executing `sret`.
9. **User Return**: Control returns to user code with the tick count in register `a0`.

---

### Q10: How does xv6 prevent priority inversion or process starvation in its default scheduler?
**Answer**:  
xv6 uses a simple Round-Robin scheduler. Each CPU core continuously loops through the `proc[]` table from index 0 to `NPROC-1`. Any process in `RUNNABLE` state is allocated the CPU for at most one timer tick (100 ms). Because every runnable process is serviced in cyclic order and timer interrupts force preemption via `yield()`, no process can starve another indefinitely.

---

### Q11: In the concurrent workload (`conc_workload`), why did total child CPU ticks exceed elapsed wall-clock time?
**Answer**:  
QEMU was configured with 3 SMP cores (`-smp 3`). When 4 concurrent worker processes were spawned, up to 3 worker processes ran simultaneously on cores 0, 1, and 2. Because multiple cores burned CPU cycles concurrently, the sum of their individual CPU runtimes was 15 ticks, while only 8 wall-clock ticks elapsed. This resulted in a parallel execution ratio of:
$$\frac{15 \text{ CPU ticks}}{8 \text{ Wall ticks}} = 1.87\times$$
demonstrating true hardware parallelism on SMP.

---

### Q12: What is the limitation of periodic timer-based accounting for short execution bursts?
**Answer**:  
Periodic sampling exhibits quantization error. If a process executes for 2 milliseconds between two consecutive timer interrupts, neither interrupt occurs while the process is running on the CPU. As a result, the kernel records 0 CPU ticks, completely missing the execution burst. Conversely, if an interrupt happens to land during that 2 ms window, the process is charged a full 100 ms tick. This sampling variance makes timer-tick accounting inaccurate for sub-tick workloads.

---

### Q13: How could high-resolution CPU accounting be implemented in RISC-V without periodic sampling?
**Answer**:  
High-resolution accounting can be implemented by reading the 64-bit hardware cycle counter register (`rdcycle` / `time` CSR) at each process context switch:
1. When switching into process $P$ in `scheduler()`, record $t_{\text{start}} = \text{rdcycle}()$.
2. When switching out of process $P$ in `swtch()`, record $t_{\text{end}} = \text{rdcycle}()$.
3. Accumulate $\Delta \text{cycles} = t_{\text{end}} - t_{\text{start}}$ into `p->cycles`.
This provides cycle-level precision ($100$ ns resolution on a 10 MHz clock) without quantization error.

---

### Q14: What was the root cause of the `DIRSIZ` assertion failure encountered during `mkfs`?
**Answer**:  
In `kernel/fs.h`, xv6 directory entries are fixed 16-byte structs containing a 2-byte inode number and a 14-byte filename buffer (`#define DIRSIZ 14`). When `concurrent_workload` (19 characters) was added to `UPROGS`, `mkfs.c` asserted `strlen(shortname) <= DIRSIZ` and aborted. The fix was renaming the workload to `conc_workload` (13 characters), ensuring the filename fits within the 14-character directory entry boundary.

---

### Q15: What runtime overhead is introduced by our CPU accounting modifications?
**Answer**:  
The accounting modification adds an integer increment `p->cputime++` inside `usertrap()` and `kerneltrap()` only when a timer interrupt occurs. Since timer interrupts occur only 10 times per second per core, this instruction executes 10 times per second. Compared to the millions of instructions executed per second by each core, the overhead is $< 0.0001\%$, which is mathematically imperceptible.

---

### Q16: How does process-level CPU accounting lay the groundwork for advanced scheduling algorithms (e.g. MLFQ or Stride Scheduling)?
**Answer**:  
Advanced schedulers require feedback regarding each process's CPU consumption:
- In **Multilevel Feedback Queues (MLFQ)**: Processes that exhaust their CPU tick allotment are demoted to lower-priority queues, while I/O-bound processes remain in high-priority queues.
- In **Stride / Fair Schedulers**: Each process advances its virtual runtime or pass value proportional to $\text{runtime} / \text{tickets}$.
`p->cputime` provides the empirical execution measurement necessary to calculate dynamic priority adjustments and maintain scheduling fairness.

