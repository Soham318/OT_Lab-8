# Environment Verification & Setup Guide

> **Project**: Optimization Techniques — Lab Assignment 8 (OT_Lab-8)  
> **Verification Date**: October 31, 2026  
> **Target Platforms**: Windows 11 (Host) + WSL2 (Ubuntu 26.04 LTS) for xv6 RISC-V  

---

## 1. Automated Environment Verification Summary

The development environment was inspected via automated diagnostics. Below is the comprehensive status of all required runtimes, compilers, and toolchains.

### 1.1 Host Environment (Windows 11)

| Component | Status | Detected Version | Details & Capabilities |
| :--- | :--- | :--- | :--- |
| **Python** | **INSTALLED** | `Python 3.13.3` | System Python located at `AppData/Local/Programs/Python/Python313/` |
| **pip** | **INSTALLED** | `pip 25.0.1` | Package installer available |
| **NumPy** | **INSTALLED** | Verified | Core tensor and numerical linear algebra engine |
| **SciPy** | **INSTALLED** | Verified | Contains `scipy.optimize.milp` (HiGHS solver) & `linprog` |
| **Matplotlib** | **INSTALLED** | Verified | Plotting and visualization suite |
| **SQLite3** | **INSTALLED** | Built-in | Relational database engine for Track H DBMS benchmarks |
| **GCC (Host)** | **INSTALLED** | `gcc 16.1.0` (MSYS2) | Host C/C++ compiler |
| **Git** | **INSTALLED** | `git 2.44+` | Version control & commit traceability |
| **WSL2 Subsystem**| **INSTALLED** | WSL2 Active | Windows Subsystem for Linux operational |

### 1.2 Linux Subsystem (WSL2 / Ubuntu)

| Component | Status | Detected Version | Notes |
| :--- | :--- | :--- | :--- |
| **Ubuntu Distro** | **INSTALLED** | `Ubuntu 26.04 LTS` | Registered WSL2 distribution |
| **Git (WSL)** | **INSTALLED** | `/usr/bin/git` | Available inside Ubuntu |
| **Make (WSL)** | **MISSING** | Not found in `$PATH` | Required to build xv6-riscv kernel |
| **GCC (Native WSL)**| **MISSING** | Not found in `$PATH` | `build-essential` needed |
| **RISC-V GCC Toolchain** | **MISSING** | Not found in `$PATH` | `gcc-riscv64-linux-gnu` needed for cross-compiling xv6 |
| **QEMU RISC-V** | **MISSING** | Not found in `$PATH` | `qemu-system-misc` (`qemu-system-riscv64`) needed to run xv6 |

---

## 2. Identified Missing Dependencies & Action Required

In accordance with your explicit instruction (*"First verify whether WSL2, Ubuntu, QEMU and the required RISC-V toolchain are actually installed and working. Do not assume they are available. If something is missing, provide installation instructions and wait for my approval"*), the following components must be installed prior to running Track G (xv6).

### 2.1 WSL2 Ubuntu: xv6 RISC-V Build & Simulation Prerequisites

Inside your WSL2 Ubuntu terminal, run the following command (or grant approval for us to execute it via WSL):

```bash
sudo apt-get update && sudo apt-get install -y \
    build-essential \
    gdb-multiarch \
    qemu-system-misc \
    gcc-riscv64-linux-gnu \
    binutils-riscv64-linux-gnu
```

#### What this command installs:
1. `build-essential`: Installs `make`, `gcc`, and core compilation utilities.
2. `qemu-system-misc`: Provides the `qemu-system-riscv64` emulator to execute the compiled xv6 kernel.
3. `gcc-riscv64-linux-gnu` & `binutils-riscv64-linux-gnu`: The 64-bit RISC-V cross-compiler and assembler required to build the xv6 kernel on x86_64 Ubuntu.

### 2.2 Host Python Environment Recommendations

To streamline the remaining tracks:
1. **Tracks A, B, D, E, F, H, J**: Fully supported by currently verified packages (`numpy`, `scipy`, `matplotlib`, `sqlite3`).
   * Optional helper libraries that enhance plotting and graph manipulation:
     ```bash
     pip install networkx pandas tabulate
     ```
2. **Tracks C & I (Quantum Simulation Strategy)**:
   * **Self-Contained Statevector & Density-Matrix Quantum Simulator**:  
     Because Python 3.13 is very recent, some compiled C-extensions for Qiskit or PennyLane occasionally exhibit build conflicts on Windows. To guarantee **100% deterministic reproducibility across any machine without installation failures**, we have engineered a pure-NumPy quantum simulation engine (`track_c_quantum_opt/core/` and `track_i_quantum_algos/core/`) that computes exact statevectors, supports arbitrary unitary gates, parameterized rotation gates ($R_x, R_y, R_z$), shot-noise Poisson sampling, depolarizing error channels, and analytical parameter-shift gradient computation.
   * If desired, standard Qiskit / PennyLane packages can also be installed alongside:
     ```bash
     pip install qiskit pennylane
     ```

---

## 3. Verification Commands (Run After Installation)

Once the WSL packages are installed, verify the toolchain with:

```bash
# Verify inside WSL2:
wsl -d Ubuntu -- bash -c "riscv64-linux-gnu-gcc --version && qemu-system-riscv64 --version && make --version"
```

Expected output:
* `riscv64-linux-gnu-gcc (Ubuntu ...) x.x.x`
* `QEMU emulator version x.x.x (qemu-system-riscv64)`
* `GNU Make x.x`
