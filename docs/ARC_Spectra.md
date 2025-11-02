# Earth Spectra: Electrodynamics ↔ Thermal Emission

This note anchors the **Attenuation → Return** model in measurable physics.

- **Attenuation**: absorption/scattering of incoming solar radiation by the atmosphere/surface.
- **Return**: Earth’s outgoing radiation (longwave IR), plus ELF resonance fields.

## 1) Thermal Emission (Planck, T ≈ 288 K)

Earth’s broadband IR emission follows Planck’s law with peak near **~10 μm**.

![Planck 288 K](figures/earth_thermal_planck_288K.svg)

- Wien peak: `λ_max ≈ 2.8978e-3 / T ≈ 10 μm` for `T=288 K`.
- Outgoing Longwave Radiation (OLR) integrates to ~239 W/m² at the Top of Atmosphere.

## 2) Planetary Electrodynamics (Conceptual Spectrum)

Earth–ionosphere cavity supports **Schumann resonances** at ≈ 7.83, 14.1, 20.3, 26.0, 33.0 Hz.  
Thermal IR sits at ~`3×10^13 Hz` (~10 μm). Plotted together on a log axis:

![Electrodynamic + Thermal](figures/earth_electrodynamic_thermal_spectrum.svg)

- **ELF resonances** (lightning-driven) = the planet’s “heartbeat.”
- **Thermal IR** = the planet’s radiative “glow.”

## Mapping to Resonance Mesh

- **Attenuation** (A): interaction with the medium (air/helio/vac).
- **Return** (R): radiative and field emission back to space.
- **Criterion (C)**: threshold for coherence/harmony.  
  In our ARC API, `passes = (R - A) >= C`.

> Interpretation: When **return ≥ attenuation + C**, the signal maintains identity through the medium (coherence).

## References (conceptual)
- Planck’s Law, Stefan–Boltzmann, Wien’s displacement.
- Schumann resonance fundamentals (ELF cavity modes).