# Track I: Quantum Algorithms and Quantum Machine Learning

Track I of the 14-Day Optimization Challenge implements foundational quantum algorithms, discrete combinatorial optimization mappings, and supervised Quantum Machine Learning using Python and Qiskit 2.6.2.

---

## 1. Executive Summary

- **Simulation Environment**: Local statevector simulation using `qiskit.quantum_info.Statevector` and `qiskit.primitives.StatevectorSampler` (zero external hardware or cloud dependencies).
- **Core Algorithms Implemented & Validated**:
  1. **Deutsch-Jozsa Algorithm**: Distinguishes constant from balanced boolean oracles in a single query ($O(1)$ vs classical $O(2^{n-1}+1)$).
  2. **Bernstein-Vazirani Algorithm**: **Manually constructed from elementary gates** ($H, X, CX$); recovers hidden secret bitstrings ($101$, $1101$) with $100\%$ deterministic probability on a single query ($O(1)$ vs classical $O(n)$).
  3. **Grover's Search Algorithm**: **Manually constructed from elementary gates** (Phase Oracle + Diffuser); achieves provable quadratic speedup ($O(\sqrt{N})$), reaching $100.0\%$ target probability on $N=4$ ($R=1$) and $94.43\%$ on $N=8$ ($R=2$), demonstrating amplitude amplification and over-rotation.
  4. **Quantum Fourier Transform (QFT) & Inverse QFT**: $O(n^2)$ gate synthesis using Hadamards, controlled-phase rotations, and SWAP gates. Reversibility verified to machine precision ($\|U_{\text{IQFT}} U_{\text{QFT}} - I\|_2 < 6.96 \times 10^{-16}$).
  5. **Quantum Phase Estimation (QPE)**: Estimates unitary eigenvalue phases using controlled-$U^{2^j}$ operations and Inverse QFT. Recovers dyadic phases ($\theta = 0.375, 0.250, 0.125$) with $0.000000$ error.
  6. **Shor's Factoring Algorithm**: Complete period-finding pipeline factoring $N = 15$ with base $a = 7$. Recovers period $r = 4$ via Continued Fractions and extracts non-trivial prime factors $[3, 5]$ ($3 \times 5 = 15$).
  7. **Quantum Annealing & QUBO Demonstration**: Maps a 4-variable constrained selection problem to an Ising spin glass Hamiltonian. Exhaustive search and classical Simulated Annealing both converge to the global ground state `1001` with minimum energy $-8.0$.
  8. **Quantum Machine Learning (VQC) vs. Classical ML**: Evaluated on the Iris dataset (Classes 0 & 1, 2 features). Classical Logistic Regression achieves $100\%$ accuracy in $3.32 \text{ ms}$; Quantum VQC achieves $93.3\%$ accuracy in $938.00 \text{ ms}$ ($282.5\times$ slower on CPU), empirically confirming that classical simulation of quantum systems incurs severe computational overhead without speedup on small tabular data.

---

## 2. Directory Layout

```text
track_i_quantum_algorithms/
├── circuits/                           # Exported ASCII quantum circuit diagrams
│   ├── bernstein_vazirani_101.txt      # Manual elementary BV circuit
│   ├── bernstein_vazirani_1101.txt     # Manual elementary BV circuit (4 qubits)
│   ├── deutsch_jozsa_balanced_3q.txt   # Deutsch-Jozsa balanced oracle circuit
│   ├── deutsch_jozsa_constant_3q.txt   # Deutsch-Jozsa constant oracle circuit
│   ├── grover_2q_10.txt                # Manual elementary Grover circuit (N=4)
│   ├── grover_3q_101.txt               # Manual elementary Grover circuit (N=8)
│   ├── qft_2q.txt / qft_3q.txt         # Forward Quantum Fourier Transform
│   ├── iqft_2q.txt / iqft_3q.txt       # Inverse Quantum Fourier Transform
│   ├── qpe_3q_theta_0.375.txt          # Quantum Phase Estimation circuit
│   ├── shor_15_base_7.txt              # Shor period-finding circuit for N=15
│   └── qml_variational_classifier.txt  # ZZ feature map + PQC variational ansatz
├── docs/                               # Comprehensive academic documentation
│   ├── quantum_fundamentals.md         # Qubits, Bloch sphere, elementary gates, phase kickback
│   ├── algorithm_implementations.md    # Step-by-step mathematical derivations and circuit architecture
│   ├── complexity_comparison.md        # Master complexity table & classical simulation limits
│   ├── quantum_vs_classical_ml.md      # QML feature maps, PQC ansatz, and empirical comparison
│   ├── experimental_analysis.md        # Detailed benchmark measurements, gate statistics, and counts
│   └── viva_questions.md               # 20 rigorous academic viva defense Q&As
├── experiments/                        # Reproducible benchmark runners
│   ├── run_all_algorithms.py           # Executes all 7 quantum algorithms and logs summary metrics
│   └── run_qml_comparison.py           # Executes Classical vs. Quantum ML benchmark
├── plots/                              # 5 Publication-quality figures (300 DPI)
│   ├── 01_grover_probability_amplification.png
│   ├── 02_qpe_phase_distribution.png
│   ├── 03_shor_period_measurement.png
│   ├── 04_qubo_energy_spectrum.png
│   └── 05_qml_vs_classical_comparison.png
├── results/                            # Raw measurement counts and summary tables
│   ├── algorithm_summary.json / .csv   # Execution metrics for all 7 algorithms
│   └── qml_benchmark_results.json/.csv # QML vs. Classical classification metrics
├── src/                                # Modular algorithm implementations
│   ├── utils.py                        # Simulation helpers, metrics, and circuit exporter
│   ├── deutsch_jozsa.py                # Deutsch-Jozsa algorithm implementation
│   ├── bernstein_vazirani.py           # Manual elementary Bernstein-Vazirani circuit
│   ├── grover_search.py                # Manual elementary Grover search circuit
│   ├── qft.py                          # QFT and Inverse QFT circuits
│   ├── qpe.py                          # Quantum Phase Estimation
│   ├── shor_factoring.py               # Shor factoring pipeline for N=15
│   ├── qubo_annealing.py               # QUBO to Ising mapping & simulated annealing
│   ├── qml_classifier.py               # Quantum Variational Classifier vs Logistic Regression
│   └── visualize_results.py            # Generates all 5 publication plots
└── tests/                              # Automated test suite
    └── test_quantum_algorithms.py      # 10 comprehensive unit and regression tests
```

---

## 3. Quickstart & Verification Commands

### Run All 7 Quantum Algorithms
```bash
python -m track_i_quantum_algorithms.experiments.run_all_algorithms
```

### Run Classical vs. Quantum Machine Learning Benchmark
```bash
python -m track_i_quantum_algorithms.experiments.run_qml_comparison
```

### Generate Visualization Plots
```bash
python -m track_i_quantum_algorithms.src.visualize_results
```

### Run Automated Test Suite
```bash
python -m unittest discover -s track_i_quantum_algorithms/tests -v
```

---

## 4. Key Highlights & Scientific Takeaways

1. **Manual Circuit Synthesis**: Both Bernstein-Vazirani and Grover's search are built gate-by-gate using elementary single-qubit rotations ($H, X$), two-qubit entangling gates ($CX, CZ$), and multi-controlled Toffoli gates ($CCX$), providing transparent structural insight without black-box abstractions.
2. **Phase Kickback as a Universal Engine**: Evaluated how phase kickback simultaneously drives oracle evaluation in Deutsch-Jozsa, secret bit recovery in Bernstein-Vazirani, phase marking in Grover's search, and eigenvalue estimation in QPE.
3. **Honest Simulation Transparency**: Explicitly demonstrated why classical simulation on a CPU does **not** confer quantum speedup. Simulating $n$ qubits requires storing $2^n$ complex numbers and computing $O(G \cdot 2^n)$ matrix-vector updates, making quantum simulation on CPU over $280\times$ slower than classical machine learning.
