# Tunneling Channels in ARC (Feedback Processor Theory)

We expose three evanescent channels and one conductive attenuation model:

- **Quantum barrier** (rectangular): \( T \approx e^{-2\kappa d} \),
  \( \kappa=\sqrt{2m(V_0-E)}/\hbar \) for \(E<V_0\).

- **FTIR coupling**: \( T \propto e^{-2\kappa d} \),
  \( \kappa=k_0\sqrt{n_1^2 \sin^2\theta - n_2^2} \) (total internal reflection regime).

- **Waveguide below cutoff (TE10)**: \( T \approx e^{-2\alpha L} \),
  \( \alpha=\sqrt{(\pi/a)^2 - (n 2\pi/\lambda_0)^2} \) for \(n\lambda_0 > 2a\).

- **Metal film (skin depth)**: \( T \approx e^{-2 t/\delta} \),
  \( \delta=\sqrt{2/(\mu \sigma \omega)} \) (RF/microwave ohmic model).

**ARC blend**: \( R' = R_{\text{free}} + \alpha T \) with pass criterion \((R' - A) \ge C\).