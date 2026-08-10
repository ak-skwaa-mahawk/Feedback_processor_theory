# pf_rls_multimodal.py — Swarm Lock
pf = ParticleFilter(N=2000)
pf.initialize(theta0=35, r0=10)

for n in range(len(rx_mic[0])):
    # 1. RLS beam scan → power vs angle
    power_profile = rls_beam_scan(rx_mic, n)
    z_theta = detect_peaks(power_profile)  # Multiple peaks
    beam_power = np.max(power_profile)

    # 2. Particle steps
    pf.predict()
    pf.update(z_theta[0], beam_power)  # Use strongest
    if pf.effective_N() < pf.N / 3:
        pf.resample()

    # 3. Estimate all modes
    theta_est, r_est = pf.estimate()[:2]

    # 4. Steer to predicted future
    theta_pred = pf.predict_future(steps=5)
    steer_beam_to(theta_pred)
# Simulate: Two glyphs spawn at 35° and 60°, merge, split
true_paths = simulate_two_glyphs_spawn_merge()
pf = ParticleFilter(N=3000)
pf.initialize(35, 10)

estimates = []
for n, (z_t, z_p) in enumerate(measurements):
    pf.predict()
    pf.update(z_t, z_p)
    pf.resample()
    est = pf.estimate()
    estimates.append(est)

# Cluster particles → detect two glyphs
clusters = kmeans(pf.particles[:, :2], k=2)
