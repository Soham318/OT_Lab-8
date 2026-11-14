# Track I: Empirical Experimental Analysis & Benchmark Results

## 1. Experimental Methodology & Rigorous Controls

All quantum experiments in Track I were executed under strict empirical controls to ensure complete scientific reproducibility:
- **Host Platform**: Windows 11 Enterprise, Python 3.13.3 64-bit, Qiskit 2.6.2, NumPy 2.5.2, SciPy 1.18.1, scikit-learn 1.6.1.
- **Hardware Architecture**: Multi-core x86_64 host with NVMe SSD backing.
- **Random Seed**: Fixed pseudo-random seed `42` across all circuit samplers, synthetic splits, and optimizers.
- **Simulation Engine**: Local statevector simulation using `qiskit.quantum_info.Statevector` for exact amplitude calculations and `qiskit.primitives.StatevectorSampler` for 1024-shot discrete measurement sampling.
- **Data Integrity**: Circuit ASCII diagrams, depth, gate counts, and raw measurement counts exported directly to [`circuits/`](file:///c:/Users/Soham%20Umesh%20Chavan/OT-8/OT_Lab-8/track_i_quantum_algorithms/circuits/) and [`results/`](file:///c:/Users/Soham%20Umesh%20Chavan/OT-8/OT_Lab-8/track_i_quantum_algorithms/results/).

---

## 2. Empirical Execution Results by Algorithm

### 2.1 Deutsch-Jozsa Algorithm
Evaluated on 3 input qubits ($2^3 = 8$ function inputs) plus 1 ancilla qubit (4 qubits total, circuit depth: 4 to 5):
- **Constant 0 Oracle**: Measured bitstring `'000'` with count $1024/1024$ ($100.0\%$ fraction). Classification: **Constant** (**PASS**).
- **Constant 1 Oracle**: Measured bitstring `'000'` with count $1024/1024$ ($100.0\%$ fraction). Classification: **Constant** (**PASS**).
- **Balanced Oracle**: Measured bitstring `'001'` with count $1024/1024$ ($0.0\%$ zero-state fraction). Classification: **Balanced** (**PASS**).
- **Complexity Advantage**: Solved in strictly 1 query, whereas a deterministic classical algorithm requires $2^{3-1} + 1 = 5$ queries in the worst case.

### 2.2 Bernstein-Vazirani Algorithm (Manual Elementary Circuit)
Constructed manually using elementary $H$, $X$, and $CX$ gates without high-level library abstractions:
- **Target `'101'`** (3 input qubits + 1 ancilla): Circuit depth = 6, total gates = 10 ($H: 6, CX: 2, X: 1, \text{meas}: 3$).
  - Measured bitstring: `'101'` with count $1024/1024$ (**100% deterministic success**).
- **Target `'1101'`** (4 input qubits + 1 ancilla): Circuit depth = 7, total gates = 13 ($H: 8, CX: 3, X: 1, \text{meas}: 4$).
  - Measured bitstring: `'1101'` with count $1024/1024$ (**100% deterministic success**).
- **Complexity Advantage**: Classical querying requires $n$ queries (querying $1000, 0100, 0010, 0001$); Bernstein-Vazirani solves it in 1 query ($n\times$ query reduction).

### 2.3 Grover's Search Algorithm (Manual Elementary Circuit)
Constructed manually using elementary gates ($H, X, CZ, CCX$) for both the phase oracle and the diffuser:
- **$N = 4$ ($n = 2$ qubits, Target `'10'`)**:
  - Optimal iterations: $R = \lfloor \frac{\pi}{4} \sqrt{4} \rfloor = 1$.
  - Circuit depth = 7, total gates = 10.
  - Measured bitstring: `'10'` with count $1024/1024$ (**100.0% success probability**).
- **$N = 8$ ($n = 3$ qubits, Target `'101'`)**:
  - Optimal iterations: $R = \lfloor \frac{\pi}{4} \sqrt{8} \rfloor = 2$.
  - Circuit depth = 17, total gates = 24.
  - Measured bitstring: `'101'` with count $967/1024$ (**$94.43\%$ success probability**).
  - Background noise counts: `'000': 9, '001': 6, '010': 10, '011': 7, '100': 6, '110': 10, '111': 9` (each $\approx 0.7\%$).
- **Amplitude Trajectory & Over-Rotation Analysis** ([`plots/01_grover_probability_amplification.png`](file:///c:/Users/Soham%20Umesh%20Chavan/OT-8/OT_Lab-8/track_i_quantum_algorithms/plots/01_grover_probability_amplification.png)):
  - Iteration 0: $P(\omega) = 1/4 = 0.250$
  - Iteration 1: $P(\omega) = 1.000$ (Optimal Peak)
  - Iteration 2: $P(\omega) = 0.250$ (Over-rotation back to uniform)
  - Iteration 3: $P(\omega) = 0.000$ (Complete destructive cancellation)

### 2.4 Quantum Fourier Transform (QFT) & Inverse QFT
Evaluated for reversibility and unitary norm error across small registers ($n \in \{2, 3, 4\}$ qubits):
- **2-qubit QFT**: Depth = 4, Gates = 4 ($H: 2, CP: 1, SWAP: 1$). Operator error: $3.33 \times 10^{-16}$.
- **3-qubit QFT**: Depth = 7, Gates = 7 ($H: 3, CP: 3, SWAP: 1$). Operator error: $5.00 \times 10^{-16}$.
- **4-qubit QFT**: Depth = 10, Gates = 12 ($H: 4, CP: 6, SWAP: 2$). Operator error: $6.96 \times 10^{-16}$.
- **Max State Error**: Fidelity error across computational basis states bounded by $< 10^{-15}$, proving exact mathematical reversibility.

### 2.5 Quantum Phase Estimation (QPE)
Evaluated with 3 counting qubits ($2^3 = 8$) and target register in eigenstate $|1\rangle$:
- **Case 1: Dyadic Phase $\theta = 0.375 = 3/8$**:
  - Measured counting register state: `'110'` (ordered bits: `'011'`, integer 3).
  - Measured phase: $\hat{\theta} = 3/8 = 0.375$.
  - Phase error: $|\hat{\theta} - \theta| = \mathbf{0.000000}$ (**100% Exact Match**).
  - Success fraction: $1024/1024$ shots ($100.0\%$).
- **Case 2: Dyadic Phase $\theta = 0.250 = 1/4$**:
  - Measured counting register state: `'010'` (integer 2).
  - Measured phase: $\hat{\theta} = 2/8 = 0.250$.
  - Phase error: $\mathbf{0.000000}$ (**100% Exact Match**).

### 2.6 Shor's Factoring Algorithm ($N = 15, a = 7$)
Evaluated using 3 counting qubits and 4 target qubits (7 qubits total):
- Modular multiplications: $7^1 \equiv 7$, $7^2 \equiv 4$, $7^4 \equiv 1 \pmod{15}$.
- Measurement spectrum:
  - Phase $0.00$ ($0/1$): count $268$ ($26.2\%$) $\to r = 1$ (trivial)
  - Phase $0.25$ ($1/4$): count $247$ ($24.1\%$) $\to r = 4$
  - Phase $0.50$ ($1/2$): count $247$ ($24.1\%$) $\to r = 2$
  - Phase $0.75$ ($3/4$): count $262$ ($25.6\%$) $\to r = 4$
- Continued fractions post-processing on non-zero phases $0.25$ and $0.75$ extracts period $r = 4$.
- Classical GCD factor extraction:
  $$\gcd(7^{4/2} - 1, 15) = \gcd(48, 15) = \mathbf{3}$$
  $$\gcd(7^{4/2} + 1, 15) = \gcd(50, 15) = \mathbf{5}$$
  Non-trivial prime factors extracted: $\mathbf{[3, 5]}$ ($3 \times 5 = 15$).

### 2.7 QUBO / Ising Annealing Demonstration
Evaluated on a 4-variable constrained selection problem:
- **QUBO vs Ising Identity**: Proved exact energy equivalence across all 16 states (maximum difference $= 0.0$).
- **Exhaustive Ground State**: Binary state `'1001'` with minimum energy $E^* = \mathbf{-8.0}$.
- **Simulated Classical Annealing**: Metropolis-Hastings annealing over 500 steps converged to `'1001'` with energy $-8.0$, discovering the guaranteed global optimum (**PASS**).

### 2.8 Quantum Machine Learning vs. Classical Machine Learning
Evaluated on the Iris dataset (Classes 0 & 1, 2 normalized features, 70 train, 30 test):
- **Classical Logistic Regression**:
  - Test Accuracy: **$100.0\%$**, Test F1: **$1.0000$**, Training Latency: **$3.32 \text{ ms}$**.
- **Quantum Variational Classifier (VQC)**:
  - Test Accuracy: **$93.3\%$**, Test F1: **$0.9286$**, Training Latency: **$938.00 \text{ ms}$** ($282.5\times$ slower).
  - Circuit depth = 9, Qubits = 2, Total gates = 14, Optimizer iterations = 35 COBYLA steps, Circuit evaluations = 2,450.

---

## 3. Comprehensive Computational Conclusions

1. **Gate Parity & Coherence**: The exact analytical reversibility of QFT and deterministic recovery in Deutsch-Jozsa and Bernstein-Vazirani confirm that statevector simulation accurately reflects ideal unitary quantum evolution in the zero-noise limit.
2. **Phase Estimation Precision**: QPE functions with perfect fidelity when the target phase is an exact dyadic fraction of the counting register capacity ($2^t \theta \in \mathbb{Z}$).
3. **Simulation vs Hardware Duality**: Quantum algorithms offer exponential and polynomial asymptotic advantages on physical quantum hardware ($O((\log N)^3)$ for Shor, $O(\sqrt{N})$ for Grover). However, executing these algorithms on a classical CPU incurs exponential memory $O(2^n)$ and time overhead, demonstrating that classical simulators serve solely as functional verification tools rather than vehicles for physical quantum speedup.
