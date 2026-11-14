# Track I: Quantum Fundamentals & Gate Mechanics

## 1. Qubit State Representation & Superposition

In classical computing, a bit exists deterministically in state $0$ or $1$. A quantum bit (qubit) is a two-level quantum system existing as a normalized state vector in a two-dimensional complex Hilbert space $\mathcal{H}_2 \cong \mathbb{C}^2$:
$$
|\psi\rangle = \alpha |0\rangle + \beta |1\rangle = \alpha \begin{pmatrix} 1 \\ 0 \end{pmatrix} + \beta \begin{pmatrix} 0 \\ 1 \end{pmatrix}
$$
where $\alpha, \beta \in \mathbb{C}$ are complex probability amplitudes satisfying the normalization constraint (Born rule):
$$
|\alpha|^2 + |\beta|^2 = 1
$$
Here, $|\alpha|^2$ represents the probability of measuring state $|0\rangle$, and $|\beta|^2$ represents the probability of measuring state $|1\rangle$.

### 1.1 The Bloch Sphere
Any pure single-qubit state can be parameterized on the surface of a unit sphere in $\mathbb{R}^3$ (the Bloch sphere):
$$
|\psi\rangle = \cos\left(\frac{\theta}{2}\right) |0\rangle + e^{i \phi} \sin\left(\frac{\theta}{2}\right) |1\rangle
$$
where $\theta \in [0, \pi]$ represents the polar angle and $\phi \in [0, 2\pi)$ represents the azimuthal phase angle.

---

## 2. Elementary Quantum Gates

Quantum gates are unitary operators ($U^\dagger U = U U^\dagger = I$) acting on state vectors, preserving inner products and probability normalization.

### 2.1 Single-Qubit Gates
1. **Pauli-X (NOT Gate)**:
   $$X = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \quad X |0\rangle = |1\rangle, \quad X |1\rangle = |0\rangle$$
2. **Pauli-Z (Phase Flip)**:
   $$Z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}, \quad Z |0\rangle = |0\rangle, \quad Z |1\rangle = -|1\rangle$$
3. **Hadamard Gate (Superposition Creation)**:
   $$H = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}, \quad H |0\rangle = |+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}, \quad H |1\rangle = |-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$$
4. **Phase Shift Gates**:
   $$P(\phi) = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\phi} \end{pmatrix}, \quad S = P\left(\frac{\pi}{2}\right), \quad T = P\left(\frac{\pi}{4}\right)$$
5. **Parameterized Rotation Gates**:
   $$R_x(\theta) = \exp\left(-i \frac{\theta}{2} X\right), \quad R_y(\theta) = \exp\left(-i \frac{\theta}{2} Y\right), \quad R_z(\theta) = \exp\left(-i \frac{\theta}{2} Z\right)$$

### 2.2 Multi-Qubit Gates
1. **Controlled-NOT (CNOT / CX)**:
   Applies an $X$ gate to the target qubit if and only if the control qubit is in state $|1\rangle$:
   $$CX |c\rangle |t\rangle = |c\rangle |t \oplus c\rangle, \quad CX = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & 1 & 0 \end{pmatrix}$$
2. **Controlled-Phase (CP)**:
   Applies phase $e^{i\theta}$ strictly when both control and target qubits are in state $|11\rangle$:
   $$CP(\theta) = \text{diag}(1, 1, 1, e^{i\theta})$$
3. **Controlled-Z (CZ)**:
   Symmetric phase flip: $CZ |11\rangle = -|11\rangle$, leaving $|00\rangle, |01\rangle, |10\rangle$ unchanged.
4. **SWAP Gate**:
   Exchanges the quantum states of two wires: $SWAP |a\rangle |b\rangle = |b\rangle |a\rangle$.
5. **Toffoli Gate (CCX)**:
   Controlled-controlled-NOT gate: flips the target qubit if and only if both control qubits are $|1\rangle$. Universally classical and quantum.

---

## 3. The Phase Kickback Phenomenon

Phase kickback is the core quantum mechanical mechanism powering Deutsch-Jozsa, Bernstein-Vazirani, Grover's search, and Quantum Phase Estimation.

### Mathematical Derivation:
Suppose a controlled unitary $C-U$ acts on a control qubit $|c\rangle$ and a target register in an eigenstate $|\psi\rangle$ of $U$ with eigenvalue $e^{i\theta}$:
$$
U |\psi\rangle = e^{i\theta} |\psi\rangle
$$
1. Let the control qubit be prepared in a superposition:
   $$
   |\text{control}\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}
   $$
2. The joint initial state is:
   $$
   |\Psi_0\rangle = \left(\frac{|0\rangle + |1\rangle}{\sqrt{2}}\right) \otimes |\psi\rangle = \frac{1}{\sqrt{2}} |0\rangle |\psi\rangle + \frac{1}{\sqrt{2}} |1\rangle |\psi\rangle
   $$
3. Applying controlled-$U$ leaves the $|0\rangle |\psi\rangle$ component unchanged, but applies $U$ to the $|1\rangle |\psi\rangle$ component:
   $$
   C-U |\Psi_0\rangle = \frac{1}{\sqrt{2}} |0\rangle |\psi\rangle + \frac{1}{\sqrt{2}} |1\rangle (U |\psi\rangle) = \frac{1}{\sqrt{2}} |0\rangle |\psi\rangle + \frac{e^{i\theta}}{\sqrt{2}} |1\rangle |\psi\rangle
   $$
4. Factoring out the target eigenstate $|\psi\rangle$:
   $$
   C-U |\Psi_0\rangle = \left(\frac{|0\rangle + e^{i\theta} |1\rangle}{\sqrt{2}}\right) \otimes |\psi\rangle
   $$
**Key Insight**: The eigenvalue phase factor $e^{i\theta}$ has been "kicked back" into the state of the *control* qubit, while the target register remains completely unchanged!

---

## 4. Multi-Qubit Entanglement & Hilbert Space Growth

For an $n$-qubit quantum computer, the joint state resides in the tensor product space:
$$
\mathcal{H} = \mathcal{H}_2^{\otimes n} \cong \mathbb{C}^{2^n}
$$
A general pure state requires $2^n$ complex amplitudes:
$$
|\Psi\rangle = \sum_{x \in \{0, 1\}^n} c_x |x\rangle, \quad \sum_{x} |c_x|^2 = 1
$$
- At $n = 3$ qubits: 8 complex numbers ($64$ bytes).
- At $n = 10$ qubits: 1,024 complex numbers ($16$ KB).
- At $n = 30$ qubits: $1,073,741,824$ complex numbers ($16$ GB RAM).
- At $n = 50$ qubits: $1.125 \times 10^{15}$ complex numbers ($16$ Petabytes RAM).

This exponential state space scaling is the fundamental origin of both quantum computational power on physical hardware and the severe bottleneck of classical simulators on classical CPUs.
