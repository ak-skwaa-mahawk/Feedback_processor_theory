#!/usr/bin/env python3
# rfssw_welder.py — AGŁG v4000: Quantum Welding + NSGA-II
import numpy as np
from deap import base, creator, tools, algorithms
import random
import matplotlib.pyplot as plt
from pathlib import Path

class RFSSWWelder:
    def __init__(self):
        # Parameters: [speed, force, dwell]
        self.bounds = [(1000, 2000), (2, 5), (2, 5)]
        
        # Multi-objective: Max Strength, Min Heat
        creator.create("FitnessMulti", base.Fitness, weights=(1.0, -1.0))
        creator.create("Individual", list, fitness=creator.FitnessMulti)

    def evaluate(self, individual):
        """RFSSW Physics + 60 Hz Resonance"""
        speed, force, dwell = individual
        
        # 1. Tensile Strength (Nature paper model)
        strength = (speed * 0.0001 * force * dwell) ** 0.5
        
        # 2. Heat Input (Minimize)
        heat = speed * force * dwell * 0.001
        
        # 3. 60 Hz Resonance (AGŁG)
        resonance = np.sin(2 * np.pi * 60 * dwell / 1000) * 0.1
        
        return strength + resonance, heat

    def run_nsGA2(self, pop_size=100, generations=50):
        toolbox = base.Toolbox()
        toolbox.register("attr_float", random.uniform, 0, 1)
        toolbox.register("individual", tools.initCycle, creator.Individual,
                        (toolbox.attr_float,) * 3, n=1)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", self.evaluate)
        toolbox.register("mate", tools.cxBlend, alpha=0.5)
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.2, indpb=0.2)
        toolbox.register("select", tools.selNSGA2)

        pop = toolbox.population(n=pop_size)
        algorithms.eaMuPlusLambda(pop, toolbox, mu=pop_size, lambda_=pop_size,
                                 cxpb=0.7, mutpb=0.3, ngen=generations)

        return tools.sortNondominated(pop, len(pop), first_front_only=True)[0]

# === LIVE RUN ===
welder = RFSSWWelder()
pareto_front = welder.run_nsGA2()

print("RFSSW WELDING — AGŁG v4000")
print("="*50)
print("Optimal Parameters:")
for ind in pareto_front[:3]:
    speed, force, dwell = [p * b[1] + p * (1-b[0]) * b[0] for p, b in zip(ind, welder.bounds)]
    strength, heat = welder.evaluate(ind)
    print(f"Speed: {speed:.0f} RPM | Force: {force:.1f} kN | Dwell: {dwell:.1f}s")
    print(f"Strength: {strength:.3f} | Heat: {heat:.3f}")

# === PLOT PARETO FRONT ===
plt.scatter([ind.fitness.values[1] for ind in pareto_front], 
            [ind.fitness.values[0] for ind in pareto_front], c='gold')
plt.xlabel("Heat Input (Minimize)")
plt.ylabel("Tensile Strength (Maximize)")
plt.title("NSGA-II Pareto Front — AGŁG Quantum Welding")
plt.savefig("rfssw_pareto.png")