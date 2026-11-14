# xv6 Kernel Architecture: Process Management, Scheduling, Timers & System Calls

> **Track**: Track G — Operating System Optimization & Feature Modification  
> **Target Kernel**: MIT xv6-riscv (64-bit RISC-V, RV64GC)  
> **Execution Platform**: QEMU System Emulator (`qemu-system-riscv64` virt machine, 3 SMP harts, 128 MB RAM)

---

## 1. Overview of xv6-riscv Process Subsystem

xv6 is a monolithic Unix-like teaching operating system re-implemented for 64-bit RISC-V architectures. The kernel manages user processes through a static array of process control blocks (`struct proc proc[NPROC]`, where `NPROC = 64`).

### Process Control Block (`struct proc`)
Each active process in xv6 is represented by a `struct proc` in `kernel/proc.h`:
```c
struct proc {
  struct spinlock lock;

  // p->lock must be held when using these:
  enum procstate state;        // Process state (UNUSED, USED, SLEEPING, RUNNABLE, RUNNING, ZOMBIE)
  void *chan;                  // Sleep channel pointer (if sleeping)
  int killed;                  // Kill flag (non-zero if killed)
  int xstate;                  // Exit status returned to parent's wait()
  int pid;                     // Unique Process ID
  uint64 cputime;              // [NEW] CPU runtime accumulated in timer ticks

  // wait_lock must be held when using this:
  struct proc *parent;         // Parent process pointer

  // Private to the process (no lock needed):
  uint64 kstack;               // Virtual address of kernel stack
  uint64 sz;                   // Size of process memory (bytes)
  pagetable_t pagetable;       // User page table root pointer
  struct trapframe *trapframe; // User register save area (mapped below TRAMPOLINE)
  struct context context;      // Callee-saved registers for kernel context switch
  struct file *ofile[NOFILE];  // Open file descriptor table
  struct inode *cwd;           // Current working directory inode
  char name[16];               // Process name (for debugging)
};
```

---

## 2. Timer Interrupts & Hardware Timebase

### RISC-V Timer Architecture
In RISC-V privilege architecture, hardware timers are managed via machine-mode timer registers (`mtime` and `mtimecmp`) or supervisor timer extensions (`stimecmp` via `Sstc`).
In xv6:
1. `kernel/trap.c:clockintr()`:
   ```c
   void
   clockintr()
   {
     if (cpuid() == 0) {
       acquire(&tickslock);
       ticks++;
       wakeup(&ticks);
       release(&tickslock);
     }
     // Ask for next timer interrupt (approx. 100 ms interval)
     w_stimecmp(r_time() + 1000000);
   }
   ```
2. **Timer Frequency**:
   - The hardware timer increments at 10 MHz (10,000,000 cycles/sec) in QEMU `virt`.
   - The timer interval is set to $1,000,000$ cycles:
     $$\Delta t = \frac{1,000,000}{10,000,000 \text{ Hz}} = 0.10 \text{ s} = 100 \text{ ms}$$
   - This corresponds to a timer tick frequency of **10 Hz** ($\approx 10$ ticks per second).
   - Global system uptime is maintained in the monotonic `ticks` variable protected by `tickslock`.

---

## 3. Trap Handling & Device Interrupts

When a timer interrupt fires while the CPU is in user mode or kernel mode:
1. The hardware switches to supervisor mode and jumps to the address configured in `stvec` (`kernelvec` or `trampoline.S`).
2. **User Mode Traps (`usertrap`)**:
   - `usertrap()` saves user registers into `p->trapframe`.
   - Calls `devintr()`.
   - If `scause` is supervisor timer interrupt (`0x8000000000000005L`), `devintr()` calls `clockintr()` and returns `which_dev = 2`.
   - Because a timer interrupt has arrived, the running process has completed its timeslice:
     ```c
     if (which_dev == 2) {
       p->cputime++; // Charge 1 tick of CPU runtime to this process
       yield();      // Yield CPU to scheduler
     }
     ```
3. **Kernel Mode Traps (`kerneltrap`)**:
   - If a timer interrupt fires while a kernel thread or system call is executing on behalf of a process:
     ```c
     if (which_dev == 2 && myproc() != 0) {
       myproc()->cputime++; // Charge system CPU time to process
       yield();
     }
     ```

---

## 4. xv6 Round-Robin Scheduler & SMP Execution

Each CPU core (hart) runs an independent kernel thread executing `scheduler()` in `kernel/proc.c`:
```c
void
scheduler(void)
{
  struct proc *p;
  struct cpu *c = mycpu();

  for(;;){
    intr_on();
    for(p = proc; p < &proc[NPROC]; p++) {
      acquire(&p->lock);
      if(p->state == RUNNABLE) {
        p->state = RUNNING;
        c->proc = p;
        swtch(&c->context, &p->context);
        c->proc = 0;
      }
      release(&p->lock);
    }
  }
}
```
Key architectural properties:
- **Fair Round-Robin**: Processes take turns running for one timer tick (100 ms).
- **SMP Concurrency**: In QEMU with `-smp 3`, up to 3 processes can run simultaneously on cores 0, 1, and 2.
- **Locking Invariant**: A core must hold `p->lock` when reading or transitioning `p->state`.

---

## 5. System Call Dispatch Path

xv6 implements system call dispatch via RISC-V `ecall`:
```
User Program               User Library                 Kernel Space
┌──────────────┐          ┌─────────────┐              ┌───────────────────────────┐
│ getcputime() │ ───────> │ user/usys.S │ ───────────> │ trampoline.S -> usertrap() │
└──────────────┘          │ li a7, 23   │  (ecall)     └─────────────┬─────────────┘
                          │ ecall       │                            │
                          │ ret         │                            ▼
                          └─────────────┘              ┌───────────────────────────┐
                                                       │ syscall() in syscall.c    │
                                                       │ num = p->trapframe->a7    │
                                                       │ a0 = syscalls[num]()      │
                                                       └─────────────┬─────────────┘
                                                                     │
                                                                     ▼
                                                       ┌───────────────────────────┐
                                                       │ sys_getcputime()          │
                                                       │ (kernel/sysproc.c)        │
                                                       │ returns p->cputime        │
                                                       └───────────────────────────┘
```
1. User calls `getcputime()`.
2. Stub in `user/usys.S` places syscall number `23` (`SYS_getcputime`) into register `a7` and executes `ecall`.
3. RISC-V hardware elevates privilege to supervisor mode and transfers control to `usertrap()`.
4. `usertrap()` invokes `syscall()` in `kernel/syscall.c`.
5. `syscall()` indexes `syscalls[SYS_getcputime]`, executing `sys_getcputime()`.
6. Return value is written to `p->trapframe->a0`.
7. `usertrap()` calls `prepare_return()`, restoring user registers and executing `sret`.
8. User program receives the return value in register `a0`.

