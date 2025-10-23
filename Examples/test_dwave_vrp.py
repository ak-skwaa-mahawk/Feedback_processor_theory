from neutrosophic_transport import NeutrosophicTransport

nt = NeutrosophicTransport([0], [1, 2, 3, 4])
cost = nt.optimize_leap()
print(f"D-Wave optimized cost: {cost}")