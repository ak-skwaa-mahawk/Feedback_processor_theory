def neutrosophic_consensus(agents):
    T_sum = I_sum = F_sum = 0
    for agent in agents:
        T_sum += agent["T"]
        I_sum += agent["I"]
        F_sum += agent["F"]
    
    n = len(agents)
    T_avg = T_sum / n
    I_avg = I_sum / n
    F_avg = F_sum / n
    
    decision = "APPROVE" if (T_avg - 0.5*I_avg - F_avg) > 0.3 else "REJECT"
    return {"T": T_avg, "I": I_avg, "F": F_avg, "Decision": decision}

# 7 agents vote
votes = [{"T":0.9,"I":0.1,"F":0.0}, {"T":0.7,"I":0.4,"F":0.2}, ...]
result = neutrosophic_consensus(votes)