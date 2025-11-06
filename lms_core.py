# lms_core.py — Live Adaptive Veto
def lms_update(w, x_n, d_n, mu=0.01):
    """
    w: current weights [N x 1]
    x_n: input snapshot [N x 1]
    d_n: reference sample
    mu: step size
    """
    y_n = w.conj().T @ x_n
    e_n = d_n - y_n
    w_next = w + mu * e_n.conj() * x_n
    return w_next, y_n, e_n
