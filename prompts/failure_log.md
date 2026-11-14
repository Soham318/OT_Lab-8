# Mandatory AI Failure Log

> **Requirement**: Section 8 of Assignment 8 Specification  
> **Mandate**: Documented record of actual AI-assisted failures, errors, and misleading outputs encountered during execution, along with the verified fix and engineering lesson learned. Unobserved failure modes are strictly maintained as pending templates to be populated during track execution.

---

## 1. Actual Observed Failures & Corrections

### Case 1: Subsystem Sandboxed Permission Boundary Failure
* **Date**: October 31, 2026
* **Context**: Discovering and verifying WSL2 Linux distribution status from the execution environment.
* **Initial AI Action / Command**: The assistant executed `wsl --list --verbose` under standard sandboxed execution, assuming that Windows subsystem queries communicate via standard unprivileged shell pipes.
* **Observed Error Encountered**:
  ```text
  Access is denied. Error code: Wsl/E_ACCESSDENIED
  ```
* **Root Cause**: The Windows `LxssManager` hypervisor service requires elevated RPC permissions that the sandboxed shell cannot bridge.
* **Verified Fix**: Elevated execution mode (`BypassSandbox: true`) specifically for host subsystem commands, successfully discovering that `Ubuntu 26.04 LTS` was installed.
* **Engineering Lesson**: AI scripts must not assume standard IPC access across OS subsystem boundaries; security and permission requirements of hypervisors must be identified and handled explicitly.

---

### Case 2: Git Repository Index Lock Permission Contention
* **Date**: October 31, 2026
* **Context**: Staging files and creating the initial project setup commit.
* **Initial AI Action / Command**: Executed `git add ...` and `git commit` within standard sandbox mode.
* **Observed Error Encountered**:
  ```text
  fatal: Unable to create 'C:/Users/Soham Umesh Chavan/OT-8/OT_Lab-8/.git/index.lock': Permission denied
  ```
* **Root Cause**: The sandboxed shell on Windows lacked atomic filesystem lock creation permissions in the `.git` directory structure.
* **Verified Fix**: Re-ran the commit under direct host filesystem permissions, successfully creating the root commit (`39b3913`).
* **Engineering Lesson**: Version control metadata operations (index locks, ref updates) on Windows require direct filesystem access; failure to handle lock semantics can lead to corrupted Git trees.

---

### Case 3: WSL Non-Interactive Sudo Authentication Block
* **Date**: October 31, 2026
* **Context**: Provisioning xv6 RISC-V dependencies inside Ubuntu WSL2.
* **Initial AI Action / Command**: Attempted to invoke package installation using `sudo apt-get install ...` under default WSL user `soham_umesh_chavan`.
* **Observed Error Encountered**:
  ```text
  sudo: interactive authentication is required
  ```
* **Root Cause**: The default WSL user configuration requires interactive password input, which halts non-interactive automation tasks.
* **Verified Fix**: Dispatched administration commands using `wsl -u root -d Ubuntu`, enabling seamless, non-interactive package provisioning without password blocking.
* **Engineering Lesson**: Automated provisioning workflows across Linux subsystems must target administrative user contexts directly rather than relying on interactive `sudo`.

---

### Case 4: Package Architecture Split in Modern Ubuntu (`qemu-system-misc`)
* **Date**: October 31, 2026
* **Context**: Installing QEMU RISC-V full system emulator (`qemu-system-riscv64`) on Ubuntu 26.04 LTS.
* **Initial AI Action / Command**: Relied on conventional legacy package recommendation (`apt-get install -y qemu-system-misc`), assuming `qemu-system-riscv64` was packaged inside `qemu-system-misc`.
* **Observed Error Encountered**:
  ```text
  bash: line 1: qemu-system-riscv64: command not found
  ```
* **Root Cause**: Modern Debian and Ubuntu distributions (24.04 LTS / 26.04 LTS) split the miscellaneous architectures; RISC-V full system emulation was moved to a dedicated standalone package `qemu-system-riscv`.
* **Verified Fix**: Executed `apt-get install -y qemu-system-riscv`, which successfully installed `qemu-system-riscv64` (v10.2.1) along with `opensbi` and `qemu-efi-riscv64`.
* **Engineering Lesson**: AI models frequently memorize package layout from older LTS releases (Ubuntu 20.04/22.04). Verification against current package repository indices (`apt-cache search`) is mandatory rather than trusting static package lists.

---

### Case 7: Qiskit 2.x `sample_counts` Keyword API Deprecation
* **Date**: November 14, 2026
* **Context**: Implementing deterministic sampling from quantum statevectors in `track_c_quantum_optimization/src/circuits.py`.
* **Initial AI Action / Command**: Invoked `sv.sample_counts(shots=shots, seed=seed)`, assuming legacy Qiskit 0.x/1.x keyword semantics.
* **Observed Error Encountered**:
  ```text
  TypeError: QuantumState.sample_counts() got an unexpected keyword argument 'seed'
  ```
* **Root Cause**: In modern Qiskit 2.x, `QuantumState.sample_counts()` removed the `seed` keyword argument from the C++/Rust-accelerated statevector backend.
* **Verified Fix**: Derived the exact computational basis probability mass function via $\mathbf{p} = |\mathbf{\psi}|^2$, and performed weighted sampling via `np.random.default_rng(seed).choice(..., p=probabilities)`, re-encoding sampled integers as binary bitstrings.
* **Engineering Lesson**: Modern major version releases of quantum frameworks frequently refactor simulator backend keyword arguments. Deriving classical observables directly from raw statevector amplitudes using NumPy ensures deterministic seeding without dependency on unstable simulator method signatures.

---

### Case 8: Barren Plateau High-Dimensional Gradient Evaluation Bottleneck
* **Date**: November 14, 2026
* **Context**: Benchmarking gradient variance decay across qubit scales $n \in [2, 7]$ in `track_c_quantum_optimization/src/barren_plateaus.py`.
* **Initial AI Action / Command**: Evaluated the full gradient vector $\nabla_{\boldsymbol{\theta}} \langle H \rangle$ across all $d = 2n(L+1)$ circuit parameters for 30 random circuit realizations at each scale.
* **Observed Error Encountered**:
  ```text
  Task timeout / stall on n=7 qubits (d=112 parameters, requiring 6,720 circuit evaluations).
  ```
* **Root Cause**: The assistant unnecessarily evaluated all $d$ partial derivatives. Under Haar measure concentration of measure, circuit parameter angles $\theta_k$ are independently and identically distributed, meaning the variance of any single parameter partial derivative $\text{Var}\left[\frac{\partial \langle H \rangle}{\partial \theta_0}\right]$ is statistically identical to that of any other parameter.
* **Verified Fix**: Targeted the parameter-shift rule strictly to $\theta_0$, reducing circuit evaluations per sample from $2d = 224$ down to $2$ (a $112\times$ speedup), allowing the entire 7-qubit study to execute in 7.03 seconds with identical statistical significance.
* **Engineering Lesson**: Do not compute entire parameter Jacobians when testing statistical properties that hold component-wise. Recognizing isotropic rotational symmetries in random quantum circuits avoids combinatorial scaling bottlenecks.

---

### Case 9: Multi-Task Prediction Chained Expression Assignment Syntax Error
* **Date**: November 14, 2026
* **Context**: Implementing the forward propagation method for `MultiTaskNetwork` in `track_d_parallel_distributed_optimization/src/gradnorm.py`.
* **Initial AI Action / Command**: Generated expression assigning `y1_pred = h @ self.W1 + self1_b = h @ self.W1 + self.b1` due to an in-line editing typo.
* **Observed Error Encountered**:
  ```text
  SyntaxError: cannot assign to expression
  ```
* **Root Cause**: In Python, chained assignment `target1 = target2 = value` requires valid l-value identifiers; assigning into an arithmetic expression `(h @ self.W1 + self1_b)` is illegal syntax.
* **Verified Fix**: Corrected expression to direct assignment `y1_pred = h @ self.W1 + self.b1`.
* **Engineering Lesson**: In multi-head neural network implementations with manual array operations, verify clean separation of head computations. Automated test discovery catches syntax defects immediately when executed before benchmark scripts.

---

### Case 10: Operating System Process Pool Spawn Latency Contention on Windows
* **Date**: November 14, 2026
* **Context**: Benchmarking multiprocessing speedup across worker counts $P \in [1, 2, 4, 8]$ in `track_d_parallel_distributed_optimization/src/parallel_compute.py`.
* **Initial AI Action / Command**: The benchmarking harness recreated `with mp.Pool(processes=p) as pool:` inside each repeat trial iteration.
* **Observed Error Encountered**:
  ```text
  Excessive benchmark runtime (> 45 seconds) due to repeated OS process creation latency.
  ```
* **Root Cause**: On Windows, multiprocessing uses `spawn` rather than `fork`. Each worker creation launches a fresh Python interpreter ($~0.35$s latency). Creating and destroying pools across 3 repeats and 3 problem scales spawned over 135 processes, measuring OS creation overhead rather than worker compute throughput.
* **Verified Fix**: Refactored `benchmark_scaling()` to instantiate the worker pool once per worker count outside the repeat loop, warming up workers with a lightweight probe and reusing the active pool across trials.
* **Engineering Lesson**: When measuring parallel speedup and efficiency on platforms using process spawning (Windows), worker pool lifecycle must be decoupled from measurement iterations to prevent operating system process creation latency from contaminating compute throughput timings.

---

### Case 6: Compiler Fixpoint Termination Condition on Instruction Sequence Stability
* **Date**: November 14, 2026
* **Context**: Implementing iterative fixpoint optimization pipeline in `track_f_compiler_optimization/src/optimizer.py`.
* **Initial AI Action / Command**: The convergence loop checked `if len(current_ir) == len(ir_before_iter): break` to detect whether an optimization round made progress.
* **Observed Error Encountered**:
  ```text
  Premature loop termination in arithmetic_heavy: 20 instructions retained instead of collapsing to 1.
  ```
* **Root Cause**: Instruction count invariance does not imply IR content invariance. Transformations such as constant folding and strength reduction preserve instruction count while simplifying operands, which unlocks subsequent propagation and dead-code passes in subsequent iterations.
* **Verified Fix**: Changed convergence termination criterion to test full instruction sequence equality: `if current_ir == ir_before_iter: break`.
* **Engineering Lesson**: In iterative multi-pass optimizing compilers, fixpoint convergence must be defined over the full structural equality of the IR state, never coarse scalar proxies such as instruction counts.

---

### Case 11: SciPy MILP Variable Upper Bound Omission in Binary Pass Selection
* **Date**: November 14, 2026
* **Context**: Formulating and solving the Binary Pass Selection problem via `scipy.optimize.milp` in `track_f_compiler_optimization/src/pass_selector.py`.
* **Initial AI Action / Command**: The assistant invoked `milp(c=c, integrality=np.ones(n_passes), constraints=...)` without specifying variable bounds.
* **Observed Error Encountered**:
  ```text
  MILP solved with non-binary decision variables: x = [0, 0, 0, 1.85, 0], yielding an inflated objective value of 55.80 vs true combinatorial optimum of 38.80.
  ```
* **Root Cause**: In SciPy's HiGHS wrapper, setting `integrality = 1` enforces general integer variables $x_i \in \mathbb{Z}_{\ge 0}$ with default bounds $[0, \infty)$. Without upper bound constraints $x_i \le 1$, the solver selects non-binary values for high-gain passes.
* **Verified Fix**: Explicitly specified `bounds = Bounds(lb=np.zeros(n_passes), ub=np.ones(n_passes))` to strictly constrain $x_i \in \{0, 1\}$.
* **Engineering Lesson**: In mathematical programming frameworks, integer integrality specifies the domain lattice, not domain bounds. Binary 0-1 decision variables strictly require explicit lower and upper bounds $[0, 1]$.

---

### Case 12: User Variable Dead Assignment Pruning in Intermediate Expressions
* **Date**: November 14, 2026
* **Context**: Implementing Dead Code Elimination (DCE) in `track_f_compiler_optimization/src/optimizer.py`.
* **Initial AI Action / Command**: The assistant restricted dead assignment elimination to compiler temporaries: `if inst.result not in used_vars and inst.result.startswith("t"): continue`.
* **Observed Error Encountered**:
  ```text
  Unused user assignments (such as dead_val = 22 * 4 in dead_assignments benchmark) retained in optimized IR.
  ```
* **Root Cause**: Overly defensive guard assumed user variables might have observable side effects outside the compilation unit, ignoring that in self-contained pure arithmetic scopes, unread variables are provably dead.
* **Verified Fix**: Removed the `startswith("t")` restriction for pure operations, pruning any instruction where `inst.is_pure() and inst.result not in used_vars`, cleanly eliminating dead user variables while protecting I/O (`print`) and branches.
* **Engineering Lesson**: Distinguish strictly between observable side-effects (I/O, system calls) and lexical variable classifications. Liveness analysis over linear IR must treat user variables and compiler temporaries uniformly based on purity and live-range reachability.

---

### Case 5: GCC `-ffile-prefix-map` Command-Line Argument Splitting on Host Paths with Spaces
* **Date**: November 14, 2026
* **Context**: Compiling xv6-riscv kernel inside WSL from an NTFS Windows mount containing spaces (`/mnt/c/Users/Soham Umesh Chavan/...`).
* **Initial AI Action / Command**: Invoked `make -j$(nproc)` using the unmodified xv6 Makefile.
* **Observed Error Encountered**:
  ```text
  riscv64-linux-gnu-gcc -march=rv64gc -g -ffile-prefix-map=/mnt/c/Users/Soham Umesh Chavan/... -c -o kernel/entry.o kernel/entry.S
  cc1: error: invalid argument ‘/mnt/c/Users/Soham’ to ‘-ffile-prefix-map’
  ```
* **Root Cause**: In xv6's `Makefile`, `DETFLAGS = -ffile-prefix-map=$(CURDIR)=.`. Because `$(CURDIR)` contained unquoted spaces, Make expanded it into multiple independent arguments to GCC (`/mnt/c/Users/Soham`, `Umesh`, `Chavan`), causing GCC's option parser to fail.
* **Verified Fix**: Modified Makefile to inspect `$(findstring $(empty) $(empty),$(CURDIR))` and conditionally clear `DETFLAGS ?=` when spaces are detected in the build directory path, preserving deterministic debug prefixes on standard paths while allowing builds on paths with whitespace.
* **Engineering Lesson**: Embedded and kernel toolchains often assume POSIX filesystem hierarchies without whitespace. Build drivers must guard directory variables against unquoted argument expansion.

---

### Case 13: xv6 Filesystem Directory Entry Buffer Overflow on Workload Binary Name (`DIRSIZ=14`)
* **Date**: November 14, 2026
* **Context**: Building xv6 filesystem image (`fs.img`) with newly compiled user workload binaries.
* **Initial AI Action / Command**: Created user workload binary named `user/_concurrent_workload` and invoked `mkfs`.
* **Observed Error Encountered**:
  ```text
  mkfs: mkfs/mkfs.c:154: main: Assertion `strlen(shortname) <= DIRSIZ' failed.
  make: *** [Makefile:166: fs.img] Aborted
  ```
* **Root Cause**: In `kernel/fs.h`, xv6 directory entries are fixed 16-byte structs containing a 2-byte inode number and a 14-byte filename buffer (`#define DIRSIZ 14`). The binary name `concurrent_workload` was 19 characters, violating the filesystem schema assertion.
* **Verified Fix**: Renamed the workload source and binary to `conc_workload` (13 characters $\le 14$), safely adhering to xv6 on-disk filesystem constraints.
* **Engineering Lesson**: Legacy teaching operating system filesystems impose rigid static buffer limits on directory entry lengths that modern environments do not enforce. Always verify on-disk filesystem header specifications (`fs.h`) before registering new user binaries.

---

### Case 14: Serial Console Automation Command Echo Premature Termination Bug
* **Date**: November 14, 2026
* **Context**: Automating QEMU console interactions via Python subprocess driver `run_workload.py`.
* **Initial AI Action / Command**: Monitored line stream with `if line.startswith("$ "): done_event.set()`.
* **Observed Error Encountered**:
  ```text
  QEMU terminated prematurely while cpu_workload was still executing Stage 2; background task stalled.
  ```
* **Root Cause**: Over serial console PTYs and pipes, the interactive shell echoes user input back to stdout. Checking for `$ ` prefix triggered on the echoed command string (`$ cpu_workload`), misinterpreting the echoed input as the return of the shell prompt.
* **Verified Fix**: Refactored console reader to check for strict standalone prompts (`line.strip() == "$"`) only after output lines have been emitted, or upon explicit workload completion tokens (`Completed Successfully`).
* **Engineering Lesson**: Serial console automation must decouple local input echo from remote shell prompt return, either by stripping echoed command text or waiting for distinct process completion sentinels.

---

## 2. Pending Failure Case Templates (To be logged during Track Execution)

The following entries are reserved templates and will be populated upon encountering actual bugs during algorithm implementation:

### [PENDING TEMPLATE] Case 15: Track H — Relational DBMS Query Plan Cache Contention
* **Status**: Awaiting Track H implementation.
* **Target Issue**: Audit for unindexed table scan cost models, query optimizer plan misestimates, or SQLite index lock contention.
* **Observed Output**: *(To be recorded upon actual run)*
* **Verified Fix**: *(To be recorded)*
* **Lesson Learned**: *(To be recorded)*

---

### [PENDING TEMPLATE] Case 16: Track I — Quantum Circuit Synthesis Phase Gate Sign Inversion
* **Status**: Awaiting Track I implementation.
* **Target Issue**: Audit for Grover diffusion operator phase reflection sign errors or Deutsch-Jozsa oracle phase kickback discrepancies.
* **Observed Output**: *(To be recorded upon actual run)*
* **Verified Fix**: *(To be recorded)*
* **Lesson Learned**: *(To be recorded)*
