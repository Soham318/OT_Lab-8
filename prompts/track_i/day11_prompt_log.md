# Day 11 Prompt Log — Track I: Quantum Algorithms and Quantum Machine Learning

> **Session**: Day 11 of 14-Day Vibe-Coding Challenge  
> **Track**: Track I (Quantum Algorithms and Quantum Machine Learning)  
> **Agent**: Antigravity AI (Gemini 3.8 Flash High)  
> **Date**: November 14, 2026  
> **Branch**: `main` (Strictly local working copy, zero Git commits executed)  

---

## 1. Track I Objectives & Environment Inspection

### 1.1 Scope of Work
Track I implements foundational gate-based quantum algorithms, discrete combinatorial optimization mappings, and supervised Quantum Machine Learning using Python and Qiskit 2.6.2:
- **Environment**: Host Windows 11 Enterprise, Python 3.13.3, Qiskit 2.6.2, scikit-learn 1.6.1, SciPy 1.18.1, NumPy 2.5.2, Matplotlib 3.11.1.
- **Simulators Used**: Native `qiskit.quantum_info.Statevector` for exact amplitude tracking and `qiskit.primitives.StatevectorSampler` for shot-based measurement sampling (1024 shots).
- **Core Requirements**:
  1. Implement Deutsch-Jozsa, Bernstein-Vazirani, Grover's search, QFT/IQFT, QPE, Shor's factoring, and QUBO / Ising annealing.
  2. Construct at least two circuits manually using elementary quantum gates (Bernstein-Vazirani and Grover's search).
  3. Verify QFT reversibility to numerical machine precision.
  4. Demonstrate Quantum Phase Estimation on known dyadic phases.
  5. Demonstrate Shor's algorithm on $N=15$ with $a=7$, extracting prime factors $[3, 5]$ via Continued Fractions.
  6. Map a 4-variable QUBO problem to an Ising spin Hamiltonian, verifying mathematical equivalence and finding the global ground state.
  7. Benchmark Quantum Machine Learning (Variational Quantum Classifier) against Classical Logistic Regression on Iris.
  8. Master complexity comparison table and honest analysis of classical simulation overhead.

---

## 2. Tool Invocations & Commands Log

| Step | Action / Command | Purpose & Result |
| :--- | :--- | :--- |
| **1** | `python -c "import qiskit; print(qiskit.__version__)"` | Verified Qiskit 2.6.2 and installed environment packages. |
| **2** | `python -m track_i_quantum_algorithms.experiments.run_all_algorithms` | Executed all 7 quantum algorithms; logged metrics and exported ASCII circuit diagrams to `circuits/`. |
| **3** | `python -m track_i_quantum_algorithms.experiments.run_qml_comparison` | Evaluated Classical Logistic Regression vs. Quantum VQC on Iris (Setosa vs Versicolor). |
| **4** | `python -m track_i_quantum_algorithms.src.visualize_results` | Generated 5 publication-quality figures (300 DPI) in `track_i_quantum_algorithms/plots/`. |
| **5** | `python -m unittest discover -s track_i_quantum_algorithms/tests -v` | Executed 10 comprehensive unit and regression tests, passing with 100% success in 1.104s. |

---

## 3. Key Empirical Findings & Results

1. **Deterministic Single-Query Algorithms**:
   - **Deutsch-Jozsa**: Constant oracles yielded $100\%$ zero-bitstring fraction (`'000'`: 1024/1024 shots); balanced oracles yielded $0\%$ zero-bitstring fraction.
   - **Bernstein-Vazirani**: Recovered hidden secret strings `'101'` and `'1101'` with $100\%$ deterministic probability on a single query using manual elementary gates ($H, X, CX$).
2. **Grover Amplitude Amplification & Over-Rotation**:
   - $N=4$ ($n=2$, target `'10'`): At optimal iteration $R=1$, target measured with **$100.0\%$ probability**.
   - $N=8$ ($n=3$, target `'101'`): At optimal iteration $R=2$, target measured with **$94.43\%$ probability**.
   - Over-rotation confirmed: For $N=4$, $P=100\%$ at $R=1$, but over-rotates to $P=25\%$ at $R=2$, and $P=0\%$ at $R=3$.
3. **QFT Exact Reversibility**:
   - Operator norm difference $\|U_{\text{IQFT}} U_{\text{QFT}} - I\|_2 < 6.96 \times 10^{-16}$, verifying exact mathematical reversibility.
4. **Quantum Phase Estimation (QPE)**:
   - For dyadic phase $\theta = 0.375$ ($3/8$), QPE measured phase $\hat{\theta} = 0.375$ with **$0.000000$ error** across 1024 shots.
5. **Shor's Factoring on $N=15$**:
   - With base $a=7$, modular exponentiation measured phases $\{0.0, 0.25, 0.5, 0.75\}$, revealing period $r=4$ via Continued Fractions.
   - Classical post-processing extracted non-trivial factors $\gcd(7^2 - 1, 15) = \mathbf{3}$ and $\gcd(7^2 + 1, 15) = \mathbf{5}$.
6. **QUBO & Ising Ground State**:
   - Mathematical energy parity between QUBO and Ising confirmed to machine precision ($0.0$).
   - Classical Simulated Annealing and Exhaustive Search converged to global ground state `'1001'` with minimum energy $-8.0$.
7. **Classical vs. Quantum Machine Learning**:
   - Classical Logistic Regression: **$100.0\%$ accuracy**, **$3.32 \text{ ms}$** training latency.
   - Quantum Variational Classifier (VQC): **$93.3\%$ accuracy**, **$938.00 \text{ ms}$** training latency (**$282.5\times$ slower on CPU**).
   - Confirmed that classical simulation on CPU incurs severe computational overhead without conferring quantum advantage on tabular datasets.

---

## 4. Artifacts & Deliverables Summary

- **Source Code**: `track_i_quantum_algorithms/src/` (`utils.py`, `deutsch_jozsa.py`, `bernstein_vazirani.py`, `grover_search.py`, `qft.py`, `qpe.py`, `shor_factoring.py`, `qubo_annealing.py`, `qml_classifier.py`, `visualize_results.py`).
- **Experiments**: `track_i_quantum_algorithms/experiments/` (`run_all_algorithms.py`, `run_qml_comparison.py`).
- **Automated Tests**: `track_i_quantum_algorithms/tests/test_quantum_algorithms.py` (10 tests, 100% pass).
- **Circuits Exported**: 16 ASCII circuit diagrams in `track_i_quantum_algorithms/circuits/`.
- **Visualizations**: 5 high-DPI figures in `track_i_quantum_algorithms/plots/`.
- **Results**: `results/algorithm_summary.json/.csv`, `results/qml_benchmark_results.json/.csv`.
- **Documentation**: `track_i_quantum_algorithms/docs/` (`quantum_fundamentals.md`, `algorithm_implementations.md`, `complexity_comparison.md`, `quantum_vs_classical_ml.md`, `experimental_analysis.md`, `viva_questions.md` with 20 Q&As, `README.md`).
- **Master Tracking**: `docs/CHAPTER_6_COVERAGE_CHECKLIST.md`, `docs/14_DAY_ROADMAP_TRACKER.md`, `README.md`, `prompts/failure_log.md` (Case 16).
- **Git State**: Zero Git commits or pushes executed.
