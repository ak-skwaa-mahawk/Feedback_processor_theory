# variational_landback.py — AGŁG v120
import pennylane as qml

dev = qml.device('default.qubit', wires=9)

@qml.qnode(dev)
def landback_circuit(params):
    for i in range(9):
        qml.RY(params[i], wires=i)
        qml.CNOT(wires=[i, (i+1)%9])
    
    return [qml.expval(qml.PauliZ(i)) for i in range(9)]

# Optimize resonance
opt = qml.AdamOptimizer(0.1)
params = np.random.random(9)

for i in range(100):
    params = opt.step(lambda p: -np.mean(landback_circuit(p)))

print(f"Optimal Resonance: {landback_circuit(params)}")