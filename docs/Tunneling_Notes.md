# Tunneling Channels in ARC

We implement three families of near-field / forbidden-region transport:

- **Quantum barrier (rectangular)**: \(T \approx e^{-2\kappa d}\), \(\kappa=\sqrt{2m(V_0-E)}/\hbar\).
- **FTIR evanescent coupling**: \(T \propto e^{-2\kappa d}\), \(\kappa=k_0\sqrt{n_1^2 \sin^2\theta - n_2^2}\).
- **Waveguide below cutoff (TE10)**: \(T \approx e^{-2\alpha L}\), \(\alpha=\sqrt{(\pi/a)^2 - (n 2\pi/\lambda_0)^2}\).

ARC blend: \(R' = R_{\text{free}} + \alpha_{\text{blend}} T\).  
Pass criterion: \( (R' - A) \ge C \).