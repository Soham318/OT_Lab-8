# Environment Verification & Setup Guide

> **Project**: Optimization Techniques — Lab Assignment 8 (OT_Lab-8)  
> **Verification Date**: October 31, 2026 (Updated Post-Installation)  
> **Target Platforms**: Windows 11 (Host) + WSL2 (Ubuntu 26.04 LTS) for xv6 RISC-V  
> **Status**: 100% Core System & Toolchain Dependencies Installed and Verified  

---

## 1. Verified Environment Summary

### 1.1 Host Environment (Windows 11)

| Component | Status | Detected Version | Details & Capabilities |
| :--- | :--- | :--- | :--- |
| **Python** | **VERIFIED** | `Python 3.13.3` | System Python located at `AppData/Local/Programs/Python/Python313/` |
| **pip** | **VERIFIED** | `pip 25.0.1` | Package installer available |
| **NumPy** | **VERIFIED** | Available | Core tensor and numerical linear algebra engine |
| **SciPy** | **VERIFIED** | Available | Highs MILP solver (`scipy.optimize.milp`) & `linprog` verified |
| **Matplotlib** | **VERIFIED** | Available | Plotting and visualization suite |
| **SQLite3** | **VERIFIED** | Built-in | Relational database engine for Track H DBMS benchmarks |
| **GCC (Host)** | **VERIFIED** | `gcc 16.1.0` (MSYS2) | Host C/C++ compiler |
| **Git** | **VERIFIED** | `git 2.44+` | Commit traceability verified (Initial root commit: `39b3913`) |
| **WSL2 Subsystem**| **VERIFIED** | WSL2 Active | Windows Subsystem for Linux operational |

### 1.2 Linux Subsystem (WSL2 / Ubuntu 26.04 LTS)

| Component | Status | Verified Version | Binary Location | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Ubuntu Distro** | **VERIFIED** | `Ubuntu 26.04 LTS (resolute)` | WSL2 Default | xv6 RISC-V environment |
| **GCC (Native)** | **VERIFIED** | `gcc 15.2.0 (Ubuntu 15.2.0-16ubuntu1)` | `/usr/bin/gcc` | Host C compilation inside WSL |
| **GNU Make** | **VERIFIED** | `GNU Make 4.4.1` | `/usr/bin/make` | Kernel Makefile build driver |
| **QEMU RISC-V** | **VERIFIED** | `QEMU emulator 10.2.1` | `/usr/bin/qemu-system-riscv64` | xv6 hardware emulator |
| **RISC-V GCC** | **VERIFIED** | `riscv64-linux-gnu-gcc 15.2.0` | `/usr/bin/riscv64-linux-gnu-gcc` | 64-bit RISC-V cross-compiler |
| **RISC-V GDB** | **VERIFIED** | `GNU gdb 17.1 (Ubuntu 17.1-2ubuntu1)` | `/usr/bin/gdb-multiarch` | Kernel debugging & diagnostics |
| **Git (WSL)** | **VERIFIED** | `git 2.43+` | `/usr/bin/git` | Repository synchronization inside WSL |

---

## 2. Installation Record & Verification Diagnostics

On October 31, 2026, the approved xv6 RISC-V dependencies were provisioned inside Ubuntu WSL2:

```bash
# Executed provisioning command (as administrative user in WSL2):
wsl -u root -d Ubuntu -- bash -c "apt-get update && apt-get install -y build-essential gdb-multiarch qemu-system-misc qemu-system-riscv gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu"
```

### Verification Command Executed:
```bash
wsl -d Ubuntu -- bash -c "gcc --version | head -n 1; make --version | head -n 1; qemu-system-riscv64 --version | head -n 1; riscv64-linux-gnu-gcc --version | head -n 1; gdb-multiarch --version | head -n 1"
```

### Measured Diagnostic Output:
```text
gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0
GNU Make 4.4.1
QEMU emulator version 10.2.1 (Debian 1:10.2.1+ds-1ubuntu3.3)
riscv64-linux-gnu-gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0
GNU gdb (Ubuntu 17.1-2ubuntu1) 17.1
```

---

## 3. Remaining / Optional Dependencies

* **Host Python Enhancements** *(Optional, non-blocking)*:
  * `networkx`, `pandas`, `tabulate`: Can be installed on host Python if enhanced graph visualization or automated markdown table exports are desired (`pip install networkx pandas tabulate`).
* **Self-Contained Architecture Note**:
  * All optimization tracks (Tracks A, B, C, D, E, F, H, I, J) are engineered with zero mandatory external proprietary dependencies; core algorithms, linear programs, quantum statevector simulations, and graph routines run on verified standard libraries (`numpy`, `scipy`, `matplotlib`, `sqlite3`).
