# Track C: Quantum Optimization

> **Assignment 8**: Optimize Anything — 14-Day Vibe-Coding Challenge  
> **Repository Module**: `track_c_quantum_optimization/`  
> **Status**: Complete & Verified (8/8 Automated Unit Tests Passing)  
> **Simulation Environment**: Local Quantum Simulator (`Qiskit 2.6.2`, Statevector simulation; no quantum hardware claimed)

---

## 1. Module Overview

Track C implements a comprehensive, self-contained quantum optimization experimental suite investigating Variational Quantum Algorithms (VQAs), hybrid classical-quantum loops, quantum gradient techniques, and foundational NISQ trainability limitations:

1. **Parameterized Quantum Circuits (PQC)**: Hardware-efficient ansatzes with alternating single-qubit rotations ($R_y, R_z$) and entanglement ($CX$ linear ladders), tracking parameter counts and circuit depth.
2. **Quantum Approximate Optimization Algorithm (QAOA)**: Max-Cut Hamiltonian encoding ($H_C = \sum \frac{w}{2}(I - ZZ)$, $H_M = \sum X$), multi-depth scaling ($p \in \{1, 2, 3\}$), parameter optimization via COBYLA, and approximation ratio bounds.
3. **Variational Quantum Eigensolver (VQE)**: Ground-state estimation on Transverse-Field Ising (TFIM) and Heisenberg XXZ spin models, rigorously compared against exact classical Hermitian matrix diagonalization.
4. **Quantum Gradients**: Exact analytical parameter-shift rule ($\pm \pi/2$ macroscopic displacement) compared against centered finite differences, and Simultaneous Perturbation Stochastic Approximation (SPSA) for 2-circuit-evaluation optimization under shot noise.
5. **Quantum Natural Gradient (QNG)**: Fubini-Study metric tensor $g_{ij}(\boldsymbol{\theta})$ implementation with Levenberg-Marquardt regularization on the quantum state manifold.
6. **Noise & Barren Plateaus**: Empirical validation of finite measurement shot noise variance decay ($\mathcal{O}(1/S)$) and exponential gradient variance decay ($\mathcal{O}(2^{-n})$ across $n \in [2, 7]$ qubits) demonstrating Haar measure concentration.

---

## 2. Directory Layout

```
track_c_quantum_optimization/
├── docs/
│   ├── methodology.md            # Mathematical formulations, circuit diagrams & derivations
│   ├── experimental_analysis.md  # Detailed empirical results across QAOA, VQE, and noise studies
│   └── viva_questions.md         # 16 academic viva defense Q&As with rigorous explanations
├── experiments/
│   ├── run_qaoa_benchmark.py     # Multi-depth QAOA on 4-node cycle and 5-node graphs
│   ├── run_vqe_benchmark.py      # VQE on TFIM & Heisenberg XXZ (3 & 4 qubits) vs Exact Diagonalization
│   ├── run_gradient_study.py     # Parameter-shift vs finite-difference vs SPSA under noise
│   └── run_noise_and_barren_plateaus.py # Shot noise scaling and Barren Plateau variance decay
├── plots/
│   ├── 01_qaoa_objective_convergence.png
│   ├── 02_qaoa_approximation_ratio_vs_depth.png
│   ├── 03_vqe_energy_convergence.png
│   ├── 04_parameter_shift_vs_finite_difference.png
│   └── 05_shot_noise_and_barren_plateaus.png
├── results/
│   ├── qaoa_benchmark_results.json / .csv
│   ├── vqe_benchmark_results.json / .csv
│   ├── gradient_study_results.json / .csv
│   ├── noise_barren_results.json / .csv
│   └── *.md (Markdown reports)
├── src/
│   ├── __init__.py
│   ├── circuits.py               # Hardware-efficient & parameterized ansatz builders
│   ├── qaoa.py                   # QAOA Max-Cut solver & Hamiltonian builders
│   ├── vqe.py                    # VQE solver & spin chain Hamiltonians
│   ├── gradients.py              # Parameter-shift rule, finite diff, and SPSA optimizer
│   ├── qng.py                    # Fubini-Study metric tensor & QNG optimizer
│   ├── barren_plateaus.py        # Shot noise & barren plateau measurement routines
│   └── visualize_results.py      # Publication-ready Matplotlib plot generator
└── tests/
    ├── __init__.py
    └── test_quantum_optimization.py # 8 automated unit tests
```

---

## 3. Quickstart & Verification Commands

All experiments and tests are executed from the repository root:

### Run Unit Tests
```bash
python -m unittest discover -s track_c_quantum_optimization/tests -v
```
*(Expected: 8 tests passing in ~0.5s)*

### Run Benchmarks
```bash
# 1. Multi-depth QAOA Benchmark
python track_c_quantum_optimization/experiments/run_qaoa_benchmark.py

# 2. VQE Spin Chains vs Exact Diagonalization
python track_c_quantum_optimization/experiments/run_vqe_benchmark.py

# 3. Quantum Gradients & SPSA under Noise
python track_c_quantum_optimization/experiments/run_gradient_study.py

# 4. Shot Noise & Barren Plateau Scaling Study
python track_c_quantum_optimization/experiments/run_noise_and_barren_plateaus.py
```

### Regenerate Visualizations
```bash
python -m track_c_quantum_optimization.src.visualize_results
```

---

## 4. Key Experimental Findings

| Experiment | Key Metric / Result | Theoretical Benchmark |
| :--- | :--- | :--- |
| **QAOA 4-Node Cycle** | $\alpha = 0.750$ ($p=1$) $\to$ $\alpha = 1.000$ ($p=3$) | Converges to classical optimal cut ($4.0$) |
| **QAOA 5-Node Graph** | $\alpha = 0.595$ ($p=1$) $\to$ $\alpha = 0.758$ ($p=2$) | Sub-linear depth scaling due to graph frustration |
| **VQE TFIM Ground State** | $E_{\text{VQE}} = -2.9948$ ($n=3$, $0.47\%$ error) | $E_{\text{exact}} = -3.0090$ via exact diagonalization |
| **VQE Heisenberg XXZ** | $E_{\text{VQE}} = -5.1623$ ($n=4$, $4.83\%$ error) | $E_{\text{exact}} = -5.4243$ via exact diagonalization |
| **Parameter-Shift Exactness** | Gradient error vs centered finite differences = **$3.86 \times 10^{-11}$** | Analytically exact for single-qubit generator gates |
| **SPSA under Noise** | Converges in $200$ circuits ($23.2\times$ faster runtime) | Evaluates strictly 2 circuits/step vs $2d=24$ for GD |
| **Shot Noise Scaling** | Variance decays as $\mathcal{O}(1/S)$ across $S \in [50, 10000]$ | Empirical $\sigma(S)$ tracks theoretical $1/\sqrt{S}$ |
| **Barren Plateau Decay** | Variance drops from $0.158$ ($n=2$) to $0.0033$ ($n=7$) | Matches exponential $\mathcal{O}(2^{-n})$ Haar decay |

---

## 5. Scope & Limitations

1. **Simulation Bounds:** All simulations employ statevector and shot-based simulation on classical hardware using Qiskit. No execution on physical quantum processing units (QPUs) is claimed.
2. **Qubit Scalability:** Statevector simulation incurs an exponential $\mathcal{O}(2^n)$ classical memory footprint, limiting practical exact simulation to $n \le 20$ qubits.
3. **Ansatz Expressibility:** Hardware-efficient ansatzes demonstrate excellent performance on TFIM, but exhibit non-negligible error on strongly correlated Heisenberg XXZ chains without deep multi-layer entanglement.

