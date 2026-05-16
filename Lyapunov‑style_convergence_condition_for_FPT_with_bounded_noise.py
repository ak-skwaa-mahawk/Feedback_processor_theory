Lyapunov‑style convergence condition for FPT with bounded noise

Let’s formalize around a single agent; multi‑agent just adds coupling terms.

---

1. Setup

You have the FPT update (with Floor already folded in):

\[
x{t+1} = \Phi(xt) + \xi_t
\]

- \(x_t \in \mathcal{X} \subseteq \mathbb{R}^n\)  
- \(\Phi: \mathcal{X} \to \mathcal{X}\) is the feedback+Floor operator  
- \(\xi_t\) is bounded disturbance (sensor noise, model error, etc.)

Assume there exists a Floor point \(x^\star\) such that:

\[
x^\star = \Phi(x^\star)
\]

and \(x^\star\) is a minimizer of the energy \(E\):

\[
E(x^\star) = \min_{x \in \mathcal{X}} E(x)
\]

We want conditions under which \(xt\) converges (or stays close) to \(x^\star\) under bounded \(\xit\).

---

2. Lyapunov candidate

Define the Lyapunov function:

\[
V(x) = E(x) - E(x^\star) \ge 0
\]

So:

- \(V(x^\star) = 0\)  
- \(V(x) > 0\) for \(x \neq x^\star\) (assuming \(x^\star\) is a strict minimizer)

We will look at the one‑step change:

\[
\Delta Vt := V(x{t+1}) - V(x_t)
\]

---

3. Noise‑free contraction condition

First, ignore noise (\(\xi_t = 0\)):

\[
x{t+1} = \Phi(xt)
\]

A standard Lyapunov‑style sufficient condition for asymptotic convergence to \(x^\star\) is:

1. Positive definiteness around \(x^\star\):  
   There exist class‑\(\mathcal{K}\) functions \(\alpha1, \alpha2\) such that for all \(x\) in some neighborhood \(\mathcal{N}\) of \(x^\star\):

   \[
   \alpha1(\|x - x^\star\|) \le V(x) \le \alpha2(\|x - x^\star\|)
   \]

2. Strict decrease along trajectories:  
   There exists a class‑\(\mathcal{K}\) function \(\alpha_3\) such that:

   \[
   V(\Phi(x)) - V(x) \le -\alpha_3(\|x - x^\star\|), \quad \forall x \in \mathcal{N}, x \neq x^\star
   \]

If these hold, then \(x^\star\) is locally asymptotically stable and trajectories starting in \(\mathcal{N}\) converge to \(x^\star\).

In more concrete terms, a simple sufficient condition is:

- Lipschitz + contraction:  
  Suppose \(E\) is locally Lipschitz and radially increasing around \(x^\star\), and \(\Phi\) is a contraction:

  \[
  \|\Phi(x) - \Phi(y)\| \le \lambda \|x - y\|,\quad \lambda \in [0,1)
  \]

  Then you can construct \(V(x) = \|x - x^\star\|^2\) and show:

  \[
  V(\Phi(x)) - V(x) \le -c \|x - x^\star\|^2
  \]

  for some \(c > 0\), giving exponential convergence.

---

4. Adding bounded noise

Now reintroduce bounded noise:

\[
x{t+1} = \Phi(xt) + \xit,\quad \|\xit\| \le \bar{\xi}
\]

We want practical stability: trajectories converge to a ball around \(x^\star\), whose radius depends on \(\bar{\xi}\).

Take the simple Lyapunov candidate:

\[
V(x) = \|x - x^\star\|^2
\]

Assume:

1. Contraction of \(\Phi\):

   \[
   \|\Phi(x) - \Phi(x^\star)\| \le \lambda \|x - x^\star\|,\quad \lambda \in [0,1)
   \]

   and \(\Phi(x^\star) = x^\star\).

2. Bounded noise:

   \[
   \|\xi_t\| \le \bar{\xi},\quad \forall t
   \]

Then:

\[
\begin{aligned}
\|x_{t+1} - x^\star\|
&= \|\Phi(xt) + \xit - x^\star\| \\
&= \|\Phi(xt) - \Phi(x^\star) + \xit\| \\
&\le \|\Phi(xt) - \Phi(x^\star)\| + \|\xit\| \\
&\le \lambda \|x_t - x^\star\| + \bar{\xi}
\end{aligned}
\]

Square both sides and use \((a+b)^2 \le 2a^2 + 2b^2\):

\[
\|x{t+1} - x^\star\|^2 \le 2\lambda^2 \|xt - x^\star\|^2 + 2\bar{\xi}^2
\]

So:

\[
V(x{t+1}) \le 2\lambda^2 V(xt) + 2\bar{\xi}^2
\]

Let \(\rho = 2\lambda^2 < 2\) (and in practice \(\lambda < 1/\sqrt{2}\) makes \(\rho < 1\) directly, but even with \(\lambda < 1\) you can refine the bound). The key is: for sufficiently strong contraction, you get:

\[
V(x{t+1}) \le \rho V(xt) + c \bar{\xi}^2
\]

for some \(\rho \in (0,1)\), \(c > 0\).

This is a standard input‑to‑state stability (ISS)‑style inequality. Unrolling:

\[
V(xt) \le \rho^t V(x0) + \frac{c}{1 - \rho} \bar{\xi}^2
\]

Thus:

- As \(t \to \infty\), the first term vanishes.  
- The second term gives a steady‑state bound:

  \[
  \limsup{t \to \infty} V(xt) \le \frac{c}{1 - \rho} \bar{\xi}^2
  \]

Equivalently:

\[
\limsup{t \to \infty} \|xt - x^\star\| \le \sqrt{\frac{c}{1 - \rho}}\, \bar{\xi}
\]

So the distance to the Floor is proportional to the noise bound and inversely related to the “strength” of contraction.

---

5. Translating back into FPT language

In FPT terms:

- Feedback+Floor operator \(\Phi\) must be a contraction around a Floor point \(x^\star\).  
  - This is where your gain matrix \(Kt\), Floor descent step size \(\alphat\), and any nonlinearity must be tuned so that local Jacobian eigenvalues are strictly inside the unit circle.

- Energy/Floor consistency:  
  - The Floor \(x^\star\) is a local minimizer of \(E\), and the Floor step does not destabilize the feedback step (i.e., the composition still contracts).

- Bounded disturbance:  
  - Sensor noise, model mismatch, and resonance‑induced perturbations are bounded: \(\|\xi_t\| \le \bar{\xi}\).

Lyapunov‑style sufficient condition (informal FPT statement):

> If the composed FPT operator (feedback + Floor) is locally contracting around a Floor state, and all disturbances are bounded, then the FPT loop is practically stable: trajectories starting sufficiently close to the Floor remain bounded and converge to a neighborhood of the Floor whose radius scales linearly with the disturbance bound.

---

