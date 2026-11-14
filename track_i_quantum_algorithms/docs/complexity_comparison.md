# Track I: Complexity & Computational Scaling Analysis

## 1. Master Algorithmic Complexity Comparison Table

The table below contrasts the classical problem-solving approaches with their corresponding quantum algorithms, establishing theoretical complexity bounds, circuit requirements, classical simulator execution costs, and real-world NISQ hardware constraints.

| Algorithm | Classical Approach | Classical Complexity | Quantum Algorithm | Theoretical Quantum Complexity | Circuit Requirements | Classical Simulator Cost | Practical Limitations on Physical Hardware |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Deutsch-Jozsa** | Sequential deterministic evaluation | $O(2^{n-1} + 1)$ queries | Deutsch-Jozsa Algorithm | $O(1)$ query | $n + 1$ qubits, depth $O(n)$, $O(n)$ gates ($H, X, CX$) | $O(2^n)$ statevector space, $O(n \cdot 2^n)$ time | Sensitive to ancilla phase decoherence and gate infidelities |
| **Bernstein-Vazirani** | Unit vector queries $e_i$ | $O(n)$ queries | Bernstein-Vazirani Algorithm | $O(1)$ query | $n + 1$ qubits, depth $O(1)$ parallel, $O(n)$ gates | $O(2^n)$ statevector space, $O(n \cdot 2^n)$ time | Multi-qubit CNOT crosstalk errors on dense hardware topologies |
| **Grover's Search** | Unstructured linear search | $O(N) = O(2^n)$ queries ($N/2$ average) | Grover Amplitude Amplification | $O(\sqrt{N}) = O(2^{n/2})$ queries | $n$ qubits, $R = \lfloor \frac{\pi}{4}\sqrt{N} \rfloor$ iterations, depth $O(\sqrt{N} \cdot n)$ | $O(2^n)$ statevector space, $O(\sqrt{N} \cdot 2^n)$ time | Accumulation of coherent phase errors during repeated iterations; over-rotation |
| **Quantum Fourier Transform (QFT)** | Fast Fourier Transform (FFT) | $O(N \log N) = O(n \cdot 2^n)$ operations | Quantum Fourier Transform (QFT) | $O(n^2)$ quantum gates | $n$ qubits, depth $O(n)$, $n(n+1)/2$ gates ($H, CP, SWAP$) | $O(2^n)$ matrix multiplication, $O(n^2 \cdot 2^n)$ time | Small controlled-phase rotations ($\theta = 2\pi/2^k$) drop below hardware control noise floor for large $k$ |
| **Quantum Phase Estimation (QPE)** | Power iteration / matrix diagonalization | $O(2^{3n})$ classical operations | Phase Estimation via Inverse QFT | $O(t^2 + t \cdot \text{Cost}(U))$ operations | $t$ counting + $m$ target qubits, depth $O(t^2 + t \cdot \text{depth}(U))$ | $O(2^{t+m})$ statevector space, exponential CPU time | Requires deep coherent circuits for high precision $t$; vulnerable to $T_1/T_2$ relaxation |
| **Shor's Factoring** | General Number Field Sieve (GNFS) | $O(\exp(c (\ln N)^{1/3} (\ln \ln N)^{2/3}))$ (Sub-exponential) | Shor's Order-Finding Algorithm | $O((\log N)^3)$ quantum gate steps (Polynomial) | $2 \lceil \log_2 N \rceil + 3$ qubits, depth $O((\log N)^3)$ | $O(2^{2 \log N})$ exponential memory; strictly unscalable on CPU beyond $N \approx 20$ | Requires millions of physical qubits with Quantum Error Correction (surface code thresholds); unavailable on NISQ |
| **QUBO / Ising Optimization** | Branch-and-Cut, Dynamic Programming | $O(2^n)$ worst-case (NP-hard) | Quantum Annealing / Adiabatic Evolution | $O(\text{poly}(n))$ if spectral gap $\Delta_{\min} = \Omega(1/n^c)$ | $n$ physical flux qubits, analog coupler graph | $O(2^n)$ classical state matrix, exponential Monte Carlo | Hardware sparse connectivity (Chimera/Pegasus) requires minor embedding with physical qubit overhead; thermal noise |
| **Quantum Machine Learning (VQC)** | Classical Logistic Regression / SVM | $O(d \cdot M)$ training time, instantaneous inference | Variational Quantum Classifier (PQC) | Heuristic optimization on parameterized Hilbert space | $d$ qubits, $L$ layers, $O(d \cdot L)$ parameters | $O(2^d \cdot M \cdot \text{iters})$ state evaluations; $\sim 280\times$ slower on CPU | Barren plateaus (exponential gradient vanish $\text{Var}[\partial_\theta \mathcal{L}] \sim 2^{-n}$), shot noise, finite sampling variance |

---

## 2. Why Classical Simulation Does NOT Demonstrate Quantum Speedup

A frequent misconception in applied quantum computing is that running a quantum algorithm on a classical simulator demonstrates "quantum speedup." In reality, simulating a quantum algorithm on a classical CPU is **exponentially slower** than running a classical algorithm directly.

### 2.1 The Mathematical Mechanism of Classical Simulation
A quantum state of $n$ qubits is a complex vector in $\mathbb{C}^{2^n}$:
$$
|\psi\rangle = \sum_{x=0}^{2^n - 1} c_x |x\rangle
$$
1. **Memory Complexity ($O(2^n)$)**:
   To represent the state $|\psi\rangle$, a classical simulator must allocate $2^n$ double-precision complex numbers ($16$ bytes per amplitude).
   - $n = 10 \implies 1,024 \text{ amplitudes} \approx 16 \text{ KB}$
   - $n = 20 \implies 1,048,576 \text{ amplitudes} \approx 16 \text{ MB}$
   - $n = 30 \implies 1,073,741,824 \text{ amplitudes} \approx 16 \text{ GB}$
   - $n = 40 \implies 1.099 \times 10^{12} \text{ amplitudes} \approx 17.6 \text{ Terabytes}$
   - $n = 50 \implies 1.125 \times 10^{15} \text{ amplitudes} \approx 18 \text{ Petabytes}$ (exceeding world supercomputer RAM).
2. **Computational Time Complexity ($O(G \cdot 2^n)$)**:
   Every single-qubit quantum gate $U$ acting on qubit $k$ corresponds to updating all $2^n$ amplitudes via tensor product matrix multiplication:
   $$
   |\psi'\rangle = (I \otimes \dots \otimes U \otimes \dots \otimes I) |\psi\rangle
   $$
   This requires $O(2^n)$ arithmetic operations per gate. For a circuit with $G$ gates, the classical simulation time scales as:
   $$
   T_{\text{classical}}(\text{sim}) = \mathcal{O}(G \cdot 2^n)
   $$

### 2.2 Contrast with Physical Quantum Hardware
On physical quantum hardware:
- The quantum state is physically embodied by microscopic physical quantum systems (superconducting transmon circuits, trapped ions, or photonic modes).
- Nature performs the state evolution via continuous Schrödinger equation dynamics in physical real-time ($t_{\text{gate}} \approx 10 - 100 \text{ nanoseconds}$).
- The circuit execution time on a physical quantum processor scales as:
  $$
  T_{\text{quantum}}(\text{hardware}) = \mathcal{O}(\text{circuit depth})
  $$
  independent of the $2^n$ state dimension.

### 2.3 Empirical Evidence from Track I
In our empirical QML experiment ([`experiments/run_qml_comparison.py`](file:///c:/Users/Soham%20Umesh%20Chavan/OT-8/OT_Lab-8/track_i_quantum_algorithms/experiments/run_qml_comparison.py)):
- Classical Logistic Regression trained on the Iris dataset in **$3.32 \text{ ms}$**.
- Simulating the 2-qubit Quantum Variational Classifier on the CPU required **$938.00 \text{ ms}$** (**$282.5\times$ slower**).
- Both achieved comparable test classification accuracy ($100\%$ vs $93.3\%$).
This proves that on classical hardware, simulating quantum mechanics introduces an enormous simulation overhead. Genuine quantum computational advantage can only be realized on physical, fault-tolerant quantum hardware where physical coherence and microscopic state superposition bypass classical matrix-vector multiplication.
