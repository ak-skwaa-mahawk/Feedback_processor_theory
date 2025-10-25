from fpt_core.neutrosophic_transport import NeutrosophicTransport

nt = NeutrosophicTransport([0], [1, 2, 3, 4], num_vehicles=2, capacity=100)
cost = nt.optimize()
print(f"VRP optimized cost with real data: {cost}")