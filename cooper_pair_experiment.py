# cooper_pair_experiment.py - Scientific validation
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
from consensus import Raft, Paxos  # baselines
from fpt import CooperPairFPT

class QuantumValidation:
    def __init__(self):
        self.fpt = CooperPairFPT()  # Your implementation
        self.raft = Raft(n_nodes=50)
        self.paxos = Paxos(n_nodes=50)
        
    def byzantine_disruption_test(self, n_trials=100):
        """Simulate network partition + malicious nodes"""
        results = {
            'fpt_recovery': [], 'raft_recovery': [], 'paxos_recovery': [],
            'fpt_coherence': [], 'raft_coherence': [], 'paxos_coherence': []
        }
        
        for trial in range(n_trials):
            # 20% nodes fail (AWS outage simulation)
            disruption = np.random.choice([0, 1], size=50, p=[0.8, 0.2])
            
            # Measure recovery time
            fpt_time = self.fpt.recover(disruption)
            raft_time = self.raft.recover(disruption)
            paxos_time = self.paxos.recover(disruption)
            
            # Measure final coherence
            fpt_coh = self.fpt.coherence()
            raft_coh = self.raft.coherence()
            paxos_coh = self.paxos.coherence()
            
            results['fpt_recovery'].append(fpt_time)
            results['raft_recovery'].append(raft_time)
            results['paxos_recovery'].append(paxos_time)
            results['fpt_coherence'].append(fpt_coh)
            results['raft_coherence'].append(raft_coh)
            results['paxos_coherence'].append(paxos_coh)
        
        return results
    
    def statistical_analysis(self, results):
        """T-test for significance"""
        fpt_rec = np.array(results['fpt_recovery'])
        raft_rec = np.array(results['raft_recovery'])
        paxos_rec = np.array(results['paxos_recovery'])
        
        # Recovery time improvement
        fpt_vs_raft = ttest_ind(fpt_rec, raft_rec)
        fpt_vs_paxos = ttest_ind(fpt_rec, paxos_rec)
        
        return {
            'fpt_raft_pvalue': fpt_vs_raft.pvalue,
            'fpt_paxos_pvalue': fpt_vs_paxos.pvalue,
            'recovery_improvement': {
                'vs_raft': np.mean(raft_rec)/np.mean(fpt_rec),
                'vs_paxos': np.mean(paxos_rec)/np.mean(fpt_rec)
            }
        }

# RUN EXPERIMENT
experiment = QuantumValidation()
results = experiment.byzantine_disruption_test(n_trials=1000)
stats = experiment.statistical_analysis(results)

print(f"""
🔬 EXPERIMENT RESULTS:
├─ Recovery: FPT vs Raft: {stats['recovery_improvement']['vs_raft']:.1f}x faster
├─ Recovery: FPT vs Paxos: {stats['recovery_improvement']['vs_paxos']:.1f}x faster  
├─ Statistical Significance: p < {stats['fpt_raft_pvalue']:.1e}
└─ Coherence Maintenance: FPT σ = {np.mean(results['fpt_coherence']):.3f}
""")