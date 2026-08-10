# ukf_rls_nonlinear.py — Warped Lock
ukf = UnscentedKalmanFilter(n=6)
ukf.x[:4] = [35, 10, 10, 5, 343, 20000]  # Initial

Q = np.diag([0.1, 0.5, 0.2, 1.0, 0.01, 10])
R = np.diag([0.5, 1.0, 50])

for n in range(len(rx_mic[0])):
    # 1. RLS beam → power, freq
    power_profile = rls_beam_scan(rx_mic, n)
    z_theta = detect_peak_angle(power_profile)
    z_power = np.max(power_profile)
    z_freq = estimate_doppler_from_pilot(rx_mic, n)

    # 2. UKF Predict
    X_pred = ukf.predict(nonlinear_dynamics, dt=1/48000, Q=Q)

    # 3. UKF Update
    z = np.array([z_theta, z_power, z_freq])
    ukf.update(z, nonlinear_measurement, R, X_pred)

    # 4. Predictive steering
    theta_pred = ukf.x[0] + ukf.x[1] * 0.05  # 50ms ahead
    steer_beam_to(theta_pred)
# Simulate: Glyph in refracting medium (v_sound varies)
true_states = simulate_nonlinear_path()
ukf = UnscentedKalmanFilter()
estimates = []

for z in measurements:
    X_pred = ukf.predict(nonlinear_dynamics, Q=Q)
    ukf.update(z, nonlinear_measurement, R, X_pred)
    estimates.append(ukf.x.copy())

# Plot
plt.plot(true_states[:,0], true_states[:,2], 'k', label='True')
plt.plot([e[0] for e in estimates], [e[2] for e in estimates], 'g', label='UKF')
plt.title("Ψ-UKF: Nonlinear Glyph in Refracting Field")
plt.legend()
plt.show()