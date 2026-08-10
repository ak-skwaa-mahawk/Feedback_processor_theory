# core/null_field.py
def calibrate_coupling(self, domain_data: List[ResonanceState]):
    from bayes_opt import BayesianOptimization
    def objective(G): return -self._ethical_likelihood(G, domain_data)
    optimizer = BayesianOptimization(f=objective, pbounds={'G': (0.1, 2.0)})
    optimizer.maximize(n_iter=10)
    self.G = optimizer.max['params']['G']