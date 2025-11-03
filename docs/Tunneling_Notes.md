## Drude metal (frequency sweep)

We model dispersive metals with the Drude permittivity:

\[
\varepsilon_r(\omega) = \varepsilon_{\infty} - \frac{\omega_p^2}{\omega^2 + i \gamma \omega}
\]

Then compute the complex index \( \tilde{n}=\sqrt{\varepsilon_r \mu_r} \) and
use a single-layer transfer matrix at normal incidence to get the film
transmittance \(T\). Endpoint:

- `POST /tunnel/drude`
- `POST /tunnel/plot` with `model="drude"` and `f_min_Hz/f_max_Hz` for frequency sweeps.
## Metal-Film (Skin-Depth) Tunneling
For an ohmic conductor with conductivity σ at angular frequency ω,
the skin depth is \( \delta = \sqrt{2 / (\mu \sigma \omega)} \).
For a film of thickness \( t \), transmission magnitude is approximated by
\( T \approx e^{-2 t / \delta} \).

> At higher optical frequencies, replace this RF model with complex ε(ω)
> (Drude/Lorentz) for accurate results. Our API keeps the RF/ohmic case simple
> for design intuition and ARC blending.
# Tunneling Channels in ARC

We implement three families of near-field / forbidden-region transport:

- **Quantum barrier (rectangular)**: \(T \approx e^{-2\kappa d}\), \(\kappa=\sqrt{2m(V_0-E)}/\hbar\).
- **FTIR evanescent coupling**: \(T \propto e^{-2\kappa d}\), \(\kappa=k_0\sqrt{n_1^2 \sin^2\theta - n_2^2}\).
- **Waveguide below cutoff (TE10)**: \(T \approx e^{-2\alpha L}\), \(\alpha=\sqrt{(\pi/a)^2 - (n 2\pi/\lambda_0)^2}\).

ARC blend: \(R' = R_{\text{free}} + \alpha_{\text{blend}} T\).  
Pass criterion: \( (R' - A) \ge C \).