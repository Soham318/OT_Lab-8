# Track I: Algorithm Implementations & Circuit Architecture

## 1. Overview of Implemented Quantum Algorithms

Track I implements seven core quantum algorithms and optimization paradigms plus a quantum machine learning classifier. Every algorithm is executed on a local statevector simulator using Qiskit 2.6.2 and verified against exact mathematical benchmarks.

| Algorithm | Problem / Purpose | Circuit Approach | Local Simulator | Validation Method |
| :--- | :--- | :--- | :--- | :--- |
| **Deutsch-Jozsa** | Distinguish constant from balanced boolean functions | Phase kickback with $H^{\otimes n}$ interference | Qiskit `Statevector` & Sampler | All-zeros bitstring fraction ($1.0$ vs $0.0$) |
| **Bernstein-Vazirani** | Recover hidden secret bitstring $s \in \{0, 1\}^n$ | **Manual elementary gate** CNOT oracle | Qiskit `StatevectorSampler` | 100% bitstring match on single shot |
| **Grover's Search** | Unstructured database search for marked state | **Manual elementary gate** phase oracle & diffuser | Qiskit `StatevectorSampler` | Amplitude trajectory peak ($100\%$ at $N=4$, $94.5\%$ at $N=8$) |
| **QFT & IQFT** | Basis transformation between time & frequency domains | Controlled-Phase rotations & SWAP gates | Qiskit `Operator` / `Statevector` | $QFT^\dagger QFT = I$ operator norm error ($< 10^{-15}$) |
| **Phase Estimation (QPE)** | Estimate eigenvalue phase $\theta$ for unitary $U$ | Controlled-$U^{2^j}$ + Inverse QFT | Qiskit `StatevectorSampler` | Exact binary match for dyadic phases ($\theta = 0.375$) |
| **Shor's Factoring** | Factor composite integer $N = p \cdot q$ ($N = 15$) | Modular exponentiation $a^x \pmod N$ + QPE + Continued Fractions | Qiskit `StatevectorSampler` | Prime factor recovery: $[3, 5]$ ($3 \times 5 = 15$) |
| **QUBO / Ising Annealing** | Solve combinatorial energy minimization | Ising spin mapping + Simulated Annealing | NumPy Matrix Vector / Metropolis | Exact match with Exhaustive Combinatorial ground state |
| **Quantum Classifier (VQC)**| Supervised binary classification on Iris | ZZ feature map + Parameterized Ansatz (PQC) | Qiskit `Statevector` + SciPy COBYLA | Test Accuracy, Precision, Recall, F1 vs Logistic Regression |

---

## 2. Deutsch-Jozsa Algorithm

### 2.1 Problem Statement
Given an oracle $f: \{0, 1\}^n \to \{0, 1\}$ promised to be either:
- **Constant**: $f(x) = c \in \{0, 1\}$ for all $x$.
- **Balanced**: $f(x) = 0$ for exactly $2^{n-1}$ inputs, and $f(x) = 1$ for the remaining $2^{n-1}$ inputs.
Determine whether $f$ is constant or balanced.

### 2.2 Mathematical Mechanism
1. Prepare input register in $|0\rangle^{\otimes n}$ and ancilla in $|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$.
2. Apply $H^{\otimes n}$ to the input register:
   $$
   |\psi_1\rangle = \frac{1}{\sqrt{2^n}} \sum_{x \in \{0, 1\}^n} |x\rangle |-\rangle
   $$
3. Query the oracle $U_f |x\rangle |y\rangle = |x\rangle |y \oplus f(x)\rangle$. Through phase kickback:
   $$
   |\psi_2\rangle = \frac{1}{\sqrt{2^n}} \sum_{x} (-1)^{f(x)} |x\rangle |-\rangle
   $$
4. Apply $H^{\otimes n}$ to the input register:
   $$
   |\psi_3\rangle = \sum_{y \in \{0, 1\}^n} \left[ \frac{1}{2^n} \sum_{x \in \{0, 1\}^n} (-1)^{f(x) + x \cdot y} \right] |y\rangle |-\rangle
   $$
5. For $y = 0^{\otimes n}$, the amplitude is:
   $$
   C_0 = \frac{1}{2^n} \sum_{x} (-1)^{f(x)}
   $$
   - If $f$ is constant: $(-1)^{f(x)} = \pm 1$ everywhere $\implies C_0 = \pm 1 \implies P(0^{\otimes n}) = 1.0$.
   - If $f$ is balanced: exactly half the terms are $+1$ and half are $-1 \implies C_0 = 0 \implies P(0^{\otimes n}) = 0.0$.

---

## 3. Bernstein-Vazirani Algorithm (Manual Elementary Circuit)

### 3.1 Problem Statement
Find a hidden $n$-bit secret string $s \in \{0, 1\}^n$ given a black-box evaluating:
$$
f_s(x) = s \cdot x \pmod 2 = \bigoplus_{i=0}^{n-1} s_i x_i
$$

### 3.2 Manual Elementary Gate Design
The circuit is constructed completely from elementary gates ($H, X, CX$):
```text
     ┌───┐           ┌───┐┌─┐
q_0: ┤ H ├────────■──┤ H ├┤M├
     ├───┤        │  ├───┤└╥┘┌─┐
q_1: ┤ H ├────────┼──┤ H ├─╫─┤M├
     ├───┤        │  ├───┤ ║ └╥┘┌─┐
q_2: ┤ H ├─■──────┼──┤ H ├─╫──╫─┤M├
     ├───┤┌┴─┐┌───┴─┐└───┘ ║  ║ └╥┘
anc: ┤ X ├┤H ├┤ X   ├──────╫──╫──╫─
     └───┘└──┘└─────┘      ║  ║  ║ 
c: 3/══════════════════════╩══╩══╩═
                           0  1  2 
```

### 3.3 Gate-by-Gate Functionality
1. **$X(\text{ancilla})$**: Inverts ancilla from $|0\rangle$ to $|1\rangle$.
2. **$H(\text{ancilla})$**: Converts $|1\rangle$ to $|-\rangle$, arming the phase kickback target.
3. **$H(q_i)$**: Puts each input qubit into equal superposition.
4. **$CX(q_i, \text{ancilla})$ for each bit $s_i = 1$**: Implements $s \cdot x$ modulation. If $s_i = 1$, the state receives a relative $\pi$ phase shift when $x_i = 1$.
5. **$H(q_i)$**: Interferes the kicked phases. Due to constructive interference, the wave function collapses strictly to $|s\rangle$:
   $$
   H^{\otimes n} \left( \frac{1}{\sqrt{2^n}} \sum_x (-1)^{s \cdot x} |x\rangle \right) = |s\rangle
   $$
6. **Measurement**: Returns the full secret bitstring $s$ in a single query with $100\%$ probability!

---

## 4. Grover's Search Algorithm (Manual Elementary Circuit)

### 4.1 Problem Statement
Given an unstructured search space of $N = 2^n$ items and an oracle $f(x)$ marking target state $|\omega\rangle$, locate $\omega$.

### 4.2 Manual Elementary Construction
- **Phase Oracle $U_\omega = I - 2|\omega\rangle\langle\omega|$**:
  - Inverts the bits where $\omega_i = 0$ using $X$ gates.
  - Applies a multi-controlled phase flip ($MCZ$) to the $|11\dots1\rangle$ state. For $n=3$, this is realized using elementary gates: $H(q_2) + CCX(q_0, q_1, q_2) + H(q_2)$.
  - Restores the original basis by reapplying $X$ gates.
- **Diffuser (Inversion about the Mean) $U_s = 2|s\rangle\langle s| - I$**:
  - $H^{\otimes n} X^{\otimes n} (MCZ) X^{\otimes n} H^{\otimes n}$.

### 4.3 Geometric 2D Rotation & Optimal Iteration Bound
The state space can be decomposed into a 2D plane spanned by the target state $|\omega\rangle$ and the uniform superposition of non-target states $|s'\rangle = \frac{1}{\sqrt{N-1}} \sum_{x \ne \omega} |x\rangle$.
The initial state is:
$$
|s\rangle = \sin(\theta) |\omega\rangle + \cos(\theta) |s'\rangle, \quad \sin(\theta) = \frac{1}{\sqrt{N}}
$$
Each Grover iteration rotates the state vector towards $|\omega\rangle$ by angle $2\theta$:
$$
G^R |s\rangle = \sin((2R + 1)\theta) |\omega\rangle + \cos((2R + 1)\theta) |s'\rangle
$$
To maximize the probability $\sin^2((2R + 1)\theta) \approx 1$, we require $(2R + 1)\theta \approx \frac{\pi}{2}$:
$$
R = \left\lfloor \frac{\pi}{4 \theta} \right\rfloor \approx \left\lfloor \frac{\pi}{4} \sqrt{N} \right\rfloor
$$
- For $N=4$ ($n=2$): $R = \lfloor \frac{\pi}{4} \times 2 \rfloor = 1$ iteration $\implies$ **100% exact probability**!
- For $N=8$ ($n=3$): $R = \lfloor \frac{\pi}{4} \sqrt{8} \rfloor = 2$ iterations $\implies$ **94.5% probability**!
- **Over-rotation**: If additional iterations are applied beyond $R^*$, the state vector rotates past $|\omega\rangle$, and success probability declines (empirically confirmed in `plots/01_grover_probability_amplification.png`).

---

## 5. Quantum Fourier Transform & Inverse QFT

### 5.1 Mathematical Definition
$$
\text{QFT} |j\rangle = \frac{1}{\sqrt{N}} \sum_{k=0}^{N-1} e^{2\pi i j k / N} |k\rangle
$$
In product representation across individual qubits:
$$
|j_1 \dots j_n\rangle \mapsto \frac{1}{\sqrt{2^n}} \left(|0\rangle + e^{2\pi i 0.j_n} |1\rangle\right) \left(|0\rangle + e^{2\pi i 0.j_{n-1} j_n} |1\rangle\right) \dots \left(|0\rangle + e^{2\pi i 0.j_1 \dots j_n} |1\rangle\right)
$$

### 5.2 Circuit Architecture
For wire $i = 0, \dots, n-1$:
1. Apply $H$ to wire $i$.
2. For each subsequent wire $j = i+1, \dots, n-1$:
   Apply controlled-phase rotation $CP\left(\frac{2\pi}{2^{j - i + 1}}\right)$.
3. Reverse qubit order using $\lfloor n/2 \rfloor$ SWAP gates.

### 5.3 Numerical Reversibility Verification
Using `verify_qft_reversibility()`, we compute the operator norm difference:
$$
\| U_{\text{IQFT}} U_{\text{QFT}} - I \|_2 \le 6.96 \times 10^{-16}
$$
confirming exact mathematical reversibility down to IEEE-754 floating point precision.

---

## 6. Quantum Phase Estimation (QPE)

### 6.1 Purpose & Circuit
Given unitary $U$ with unknown eigenvalue $U |\psi\rangle = e^{2\pi i \theta} |\psi\rangle$, estimate $\theta \in [0, 1)$ to $t$ bits of precision.
1. Counting register initialized to $H^{\otimes t} |0\rangle^{\otimes t} = \frac{1}{\sqrt{2^t}} \sum_{k=0}^{2^t-1} |k\rangle$.
2. Target register initialized to eigenstate $|\psi\rangle$.
3. Controlled operations apply $C-U^{2^j}$ for $j = 0, \dots, t-1$, producing state:
   $$
   \frac{1}{\sqrt{2^t}} \sum_{k=0}^{2^t-1} e^{2\pi i \theta k} |k\rangle |\psi\rangle
   $$
4. Applying Inverse QFT transforms the phase Fourier series back to computational basis states:
   $$
   \text{IQFT} \left( \frac{1}{\sqrt{2^t}} \sum_k e^{2\pi i \theta k} |k\rangle \right) = |2^t \theta\rangle
   $$
For dyadic phase $\theta = 0.375 = 3/8$, with $t=3$ counting qubits, $2^3 \times 0.375 = 3$. Measurement returns integer 3 (`'110'` in reversed Qiskit notation) with **100% deterministic probability**.

---

## 7. Shor's Factoring Algorithm ($N = 15$)

### 7.1 Reduction of Factoring to Order Finding
To factor composite integer $N = 15$:
1. Choose a coprime base $a \in (1, N)$ such that $\gcd(a, N) = 1$. Let $a = 7$.
2. Find the period $r$ of the modular exponentiation function $f(x) = 7^x \pmod{15}$:
   - $7^0 \equiv 1$
   - $7^1 \equiv 7$
   - $7^2 = 49 \equiv 4$
   - $7^3 = 28 \equiv 13$
   - $7^4 = 91 \equiv 1 \pmod{15}$.
   Thus, the true period is $r = 4$.
3. Because $r = 4$ is even and $7^{4/2} = 7^2 = 4 \not\equiv -1 \pmod{15}$, non-trivial factors are:
   $$
   \gcd(7^{4/2} - 1, 15) = \gcd(3, 15) = 3
   $$
   $$
   \gcd(7^{4/2} + 1, 15) = \gcd(5, 15) = 5
   $$
   Factoring is complete: $15 = 3 \times 5$.

### 7.2 Quantum Circuit Execution
The quantum period-finding circuit uses 3 counting qubits and 4 target qubits (7 qubits total):
- Modular multiplications by $a^{2^j} \pmod{15}$ are applied conditionally.
- Measurements yield counting register states with phases:
  - $\phi = 0/4 = 0.0$
  - $\phi = 1/4 = 0.25$
  - $\phi = 2/4 = 0.50$
  - $\phi = 3/4 = 0.75$
- Applying the Continued Fractions expansion to measured phases $0.25$ and $0.75$ yields denominator $r = 4$, successfully recovering factors $[3, 5]$ with 100% correctness.
