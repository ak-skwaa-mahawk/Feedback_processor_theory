
---

1. Concrete system recap in math form

State:
\[
x =
\begin{bmatrix}
q \\ \dot{q} \\ \tau{\text{int}} \\ \Gamma{\text{bias}}
\end{bmatrix}
\in \mathbb{R}^4
\]

Observation (linearized):
\[
o =
\begin{bmatrix}
oq \\ o{\dot{q}}
\end{bmatrix}
=
H x
\quad\text{with}\quad
H =
\begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & 0
\end{bmatrix}
\]

Reference:
\[
r =
\begin{bmatrix}
q{\text{target}} \\ \dot{q}{\text{target}}
\end{bmatrix}
\]

Error:
\[
e = r - Hx =
\begin{bmatrix}
q_{\text{target}} - q \\
\dot{q}_{\text{target}} - \dot{q}
\end{bmatrix}
\]

Feedback gain:
\[
K =
\begin{bmatrix}
k{11} & k{12} \\
k{21} & k{22} \\
k_{31} & 0      \\
0      & k_{42}
\end{bmatrix}
\in \mathbb{R}^{4\times 2}
\]

Quadratic energy:
\[
E(x) = \tfrac{1}{2}(x - x^\star)^\top M (x - x^\star)
\]

In your implementation, the Floor target is:
\[
x^\star =
\begin{bmatrix}
q{\text{target}} \\ \dot{q}{\text{target}} \\ 0 \\ 0
\end{bmatrix}
\]

and \(M\) is diagonal:
\[
M = \operatorname{diag}(mq, m{\dot{q}}, m\tau, m\gamma)
\]

So:
\[
\nabla E(x) = M(x - x^\star),\quad
H_E(x) = M
\]

Vault step size:
\[
\alpha^\star = \alpha(x^\star) = \texttt{alpha\_star}
\]

---

2. Feedback operator Jacobian \(J_{\mathcal{C}}\)

Feedback step:
\[
\tilde{x} = \mathcal{C}(x) = x + K(r - Hx)
\]

Write explicitly:
\[
\mathcal{C}(x) = x + K r - K H x
\Rightarrow
\mathcal{C}(x) = (I - K H)x + K r
\]

With
\[
H =
\begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & 0
\end{bmatrix}
\]

we get:
\[
K H =
\begin{bmatrix}
k{11} & k{12} & 0 & 0 \\
k{21} & k{22} & 0 & 0 \\
k_{31} & 0      & 0 & 0 \\
0      & k_{42} & 0 & 0
\end{bmatrix}
\]

So:
\[
J_{\mathcal{C}} = I - K H =
\begin{bmatrix}
1 - k{11} & -k{12}    & 0 & 0 \\
-k{21}    & 1 - k{22} & 0 & 0 \\
-k_{31}    & 0          & 1 & 0 \\
0          & -k_{42}    & 0 & 1
\end{bmatrix}
\]

This is the linearization of your “C-step” block.

---

3. Floor operator Jacobian \(J_F\)

Floor step (with constant \(\alpha^\star\)):
\[
F(z) = z - \alpha^\star \nabla E(z)
\]

Since \(\nabla E(z) = M(z - x^\star)\) and \(H_E = M\) is constant:
\[
J_F(z) = I - \alpha^\star M
\]

At the Floor \(z^\star = x^\star\), this is exactly:
\[
J_F^\star = I - \alpha^\star M
= \operatorname{diag}(1 - \alpha^\star m_q,\,
                      1 - \alpha^\star m_{\dot{q}},\,
                      1 - \alpha^\star m_\tau,\,
                      1 - \alpha^\star m_\gamma)
\]

---

4. Full FPT Jacobian \(J_\Phi\)

\[
\Phi(x) = F(\mathcal{C}(x))
\Rightarrow
J\Phi(x^\star) = JF^\star\,J_{\mathcal{C}}
\]

Multiply:

\[
J_\Phi(x^\star) =
\begin{bmatrix}
(1 - \alpha^\star mq)(1 - k{11}) & (1 - \alpha^\star mq)(-k{12}) & 0 & 0 \\
(1 - \alpha^\star m{\dot{q}})(-k{21}) & (1 - \alpha^\star m{\dot{q}})(1 - k{22}) & 0 & 0 \\
(1 - \alpha^\star m\tau)(-k{31}) & 0 & (1 - \alpha^\star m_\tau) & 0 \\
0 & (1 - \alpha^\star m\gamma)(-k{42}) & 0 & (1 - \alpha^\star m_\gamma)
\end{bmatrix}
\]

You then intentionally decouple axes by:

- Choosing \(k{12}, k{21}, k{31}, k{42}\) small enough that cross‑terms are negligible for stability checks, and  
- Checking each diagonal “axis” as if it were scalar.

That yields the scalar effective eigenvalues you coded:

- Position axis:
  \[
  \lambdaq \approx (1 - \alpha^\star mq)(1 - k_{11})
  \]
- Velocity axis:
  \[
  \lambda{\dot{q}} \approx (1 - \alpha^\star m{\dot{q}})(1 - k_{22})
  \]
- Integrator axis:
  \[
  \lambda\tau = 1 - \alpha^\star m\tau
  \]
- Resonance bias axis:
  \[
  \lambda\gamma = 1 - \alpha^\star m\gamma
  \]

Your verifyfptcontraction is exactly checking:
\[
|\lambda_q| < 1,\quad
|\lambda_{\dot{q}}| < 1,\quad
|\lambda_\tau| < 1,\quad
|\lambda_\gamma| < 1
\]

which is a componentwise sufficient condition for:
\[
\rho(J_\Phi(x^\star)) < 1
\]

in the decoupled approximation.

---

5. What you’ve actually built

- The C code is a direct implementation of the Jacobian‑based contraction test.  
- alphastar and the \(m\bullet\) terms control Floor curvature and descent strength.  
- \(k{11}, k{22}\) control feedback stiffness on \(q, \dot{q}\).  
- The inequalities in verifyfptcontraction are literally the Lyapunov/contraction conditions from the earlier derivation, specialized to your 4D Walker + Vault system.

 