

- State: \(x_t \in \mathbb{R}^n\) — Walker state (pose, velocities, internal controller state).  
- Observation: \(ot = H xt\), with \(H \in \mathbb{R}^{m \times n}\) (linearized sensor map).  
- Reference: \(r_t \in \mathbb{R}^m\) — desired gait/metric profile (could be Vault‑supplied).  
- Error: \(et = rt - o_t\).  
- Feedback correction: linear gain \(K \in \mathbb{R}^{n \times m}\).  
- Vault‑gated Floor: gradient step on energy \(E(x)\) with state‑dependent step size \(\alpha(x)\) coming from Vault.

We’ll derive the Jacobian of:
\[
\Phi(x) = \text{Floor}\big(\mathcal{C}(x)\big)
\]
around a Floor point \(x^\star\).

---

1. Define the concrete operators

1.1 Feedback correction \(\mathcal{C}\)

Take:
\[
o = Hx,\quad e = r - Hx
\]

Feedback step:
\[
\tilde{x} = \mathcal{C}(x) = x + K e = x + K(r - Hx)
\]

So:
\[
\mathcal{C}(x) = x + K r - K H x = (I - K H)x + K r
\]

This is affine; its Jacobian is constant:
\[
J_{\mathcal{C}}(x) = \frac{\partial \mathcal{C}}{\partial x} = I - K H
\]

---

1.2 Vault‑gated Floor

Let the Floor be implemented as a single gradient step on \(E(x)\) with a state‑dependent step size \(\alpha(x)\) provided by Vault:

\[
\text{Floor}(z) = z - \alpha(z)\,\nabla E(z)
\]

Here:

- \(z = \tilde{x} = \mathcal{C}(x)\)  
- \(\alpha: \mathbb{R}^n \to \mathbb{R}\) is scalar, smooth (Vault gate)  
- \(E: \mathbb{R}^n \to \mathbb{R}\) is smooth energy

So the full FPT update is:
\[
\Phi(x) = \text{Floor}(\mathcal{C}(x)) = \mathcal{C}(x) - \alpha(\mathcal{C}(x))\,\nabla E(\mathcal{C}(x))
\]

Let:
\[
z = \mathcal{C}(x)
\]
\[
\Phi(x) = z - \alpha(z)\,\nabla E(z)
\]

We want \(J_\Phi(x) = \dfrac{\partial \Phi}{\partial x}\).

---

2. Jacobian of the Floor operator

First compute the Jacobian of:
\[
F(z) := z - \alpha(z)\,\nabla E(z)
\]

Then:
\[
\Phi(x) = F(\mathcal{C}(x))
\]

So:
\[
J\Phi(x) = JF(z)\,J_{\mathcal{C}}(x)
\]

2.1 Differentiate \(F(z)\)

Write:
\[
F(z) = z - \alpha(z)\,\nabla E(z)
\]

Take differential:
\[
dF = dz - d\big(\alpha(z)\,\nabla E(z)\big)
\]

Use product rule on the second term. Let:

- \(\alpha(z)\) is scalar  
- \(\nabla E(z) \in \mathbb{R}^n\)

Then:
\[
d\big(\alpha(z)\,\nabla E(z)\big)
= (d\alpha)\,\nabla E(z) + \alpha(z)\,d(\nabla E(z))
\]

Now:

- \(d\alpha = \nabla \alpha(z)^\top dz\) (scalar)  
- \(d(\nabla E(z)) = HE(z)\,dz\), where \(HE(z)\) is the Hessian of \(E\) at \(z\), an \(n \times n\) matrix.

So:
\[
d\big(\alpha(z)\,\nabla E(z)\big)
= \big(\nabla \alpha(z)^\top dz\big)\,\nabla E(z) + \alpha(z)\,H_E(z)\,dz
\]

Rewriting:
\[
d\big(\alpha(z)\,\nabla E(z)\big)
= \big[\nabla E(z)\,\nabla \alpha(z)^\top + \alpha(z)\,H_E(z)\big]\,dz
\]

Therefore:
\[
dF = dz - \big[\nabla E(z)\,\nabla \alpha(z)^\top + \alpha(z)\,H_E(z)\big]\,dz
\]

Factor \(dz\):
\[
dF = \Big(I - \nabla E(z)\,\nabla \alpha(z)^\top - \alpha(z)\,H_E(z)\Big)\,dz
\]

So the Jacobian of \(F\) at \(z\) is:
\[
JF(z) = I - \nabla E(z)\,\nabla \alpha(z)^\top - \alpha(z)\,HE(z)
\]

- \(I\) is \(n \times n\)  
- \(\nabla E(z)\,\nabla \alpha(z)^\top\) is rank‑1 outer product  
- \(H_E(z)\) is the Hessian

---

3. Chain rule: Jacobian of \(\Phi\)

Recall:

\[
z = \mathcal{C}(x),\quad J_{\mathcal{C}}(x) = I - K H
\]
\[
JF(z) = I - \nabla E(z)\,\nabla \alpha(z)^\top - \alpha(z)\,HE(z)
\]

Then:
\[
J\Phi(x) = JF(z)\,J_{\mathcal{C}}(x)
\]
\[
J\Phi(x) = \Big(I - \nabla E(z)\,\nabla \alpha(z)^\top - \alpha(z)\,HE(z)\Big)\,(I - K H)
\]
with \(z = \mathcal{C}(x)\).

This is the general Jacobian of your concrete FPT loop (Walker + Vault‑gated Floor) at state \(x\).

---

4. Evaluate at a Floor point \(x^\star\)

Let \(x^\star\) be a fixed point of \(\Phi\) and a Floor of \(E\):

- \(x^\star = \Phi(x^\star)\)  
- \(\nabla E(x^\star) = 0\)

At \(x^\star\), we also have \(z^\star = \mathcal{C}(x^\star)\). For a consistent design, you typically want \(z^\star = x^\star\) (feedback doesn’t move you at the Floor), which implies:
\[
\mathcal{C}(x^\star) = x^\star \quad \Rightarrow \quad (I - K H)x^\star + K r = x^\star
\]
\[
\Rightarrow\quad K(r - H x^\star) = 0
\]
i.e. the error is zero or lies in the nullspace of \(K\).

Assume \(z^\star = x^\star\). Then at \(x^\star\):

- \(\nabla E(z^\star) = \nabla E(x^\star) = 0\)  
- So the rank‑1 term vanishes: \(\nabla E(z^\star)\,\nabla \alpha(z^\star)^\top = 0\)

Thus:
\[
JF(z^\star) = I - \alpha(z^\star)\,HE(z^\star)
\]

And:
\[
J\Phi(x^\star) = \big(I - \alpha(z^\star)\,HE(z^\star)\big)\,(I - K H)
\]

Since \(z^\star = x^\star\), we can write:
\[
J\Phi(x^\star) = \big(I - \alpha^\star HE^\star\big)\,(I - K H)
\]
where:

- \(\alpha^\star = \alpha(x^\star)\)  
- \(HE^\star = HE(x^\star)\)

This is the local linearization of your FPT loop around the Floor.

---

5. Using this Jacobian for convergence conditions

The Lyapunov/contraction condition from before becomes:

> All eigenvalues of \(J_\Phi(x^\star)\) must lie strictly inside the unit circle.

That is:
\[
\rho\big(J_\Phi(x^\star)\big) < 1
\]
where \(\rho(\cdot)\) is spectral radius.

Given:
\[
J\Phi(x^\star) = \big(I - \alpha^\star HE^\star\big)\,(I - K H)
\]

you can now:

- Treat \(H_E^\star\) as the curvature of your Vault energy at the Floor.  
- Treat \(K H\) as the effective feedback gain from Walker sensors to state.  
- Tune \(\alpha^\star\) (Vault step size) and \(K\) (Walker feedback) so that the product is contractive.

For example, in a simplified 1D case (\(n = 1\), scalar everything):

- Let \(HE^\star = hE > 0\), \(K H = k_h\), \(\alpha^\star = \alpha\).  
- Then:
  \[
  J\Phi(x^\star) = (1 - \alpha hE)(1 - k_h)
  \]
- Convergence requires:
  \[
  |(1 - \alpha hE)(1 - kh)| < 1
  \]

You can generalize this to diagonalizable \(H_E^\star\) and \(K H\) to get explicit inequalities on eigenvalues.

---

