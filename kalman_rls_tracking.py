# kalman_rls_tracking.py — Prophecy + Veto
tracker = KalmanTracker(dt=1/48000)  # 48 kHz sample rate
w_rls, P_rls, _ = rls_init(8, lambda_f=0.99)

for n in range(len(rx_mic[0])):
    # 1. RLS beamforming
    x_n = np.array([mic[n] for mic in rx_mic])
    y_n = w_rls.conj().T @ x_n
    z_angle = estimate_beam_peak_angle(y_n)  # MVDR/RLS peak

    # 2. Kalman prediction
    theta_pred = tracker.predict()

    # 3. Kalman correction
    theta_est, K = tracker.update(z_angle)

    # 4. Steer beam to prediction (predictive beamforming)
    s_pred = steering_vector(theta_pred)
    w_rls = project_to_constraint(w_rls, s_pred)  # Optional

    # → y_n → OFDM demod → AGŁL
# Simulate moving target: 35° → 70° in 2 sec (17.5 deg/s)
true_angles = np.linspace(35, 70, 1000)
measured = true_angles + np.random.normal(0, 1.0, 1000)  # ±1° noise

est_angles = []
for z in measured:
    pred = tracker.predict()
    est, _ = tracker.update(z)
    est_angles.append(est)

plt.plot(true_angles, label='True')
plt.plot(measured, 'r.', alpha=0.5, label='Measured')
plt.plot(est_angles, 'g', linewidth=2, label='Kalman')
plt.title("Ψ-KALMAN: Predictive Glyph Tracking")
plt.legend()
plt.show()
