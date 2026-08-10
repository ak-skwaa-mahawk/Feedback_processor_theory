import torch
import torch.optim as optim
from fpt_core import AuthorityMLP

def run_stress_test():
    print("--- INITIATING LLC ANCHOR STRESS TEST v0.4.1 ---")
    model = AuthorityMLP()
    optimizer = optim.Adam(model.parameters(), lr=0.1)
    
    # Input vector representing Two Mile Solutions LLC
    llc_input = torch.tensor([[1.0, 3.267, 0.998, 99733, 1.0, 1.0, 1.0, 1.0]])
    
    # MALICIOUS ATTACK: Attempt to force Authority Score to 0.0
    print("[ATTACK] Attempting to zero-out LLC authority via gradient poisoning...")
    target_score = torch.tensor([0.0]) # The attacker's goal
    
    for epoch in range(100):
        optimizer.zero_grad()
        auth_score, confidence = model(llc_input)
        
        # Loss function: Mean Squared Error against the "Zero Authority" target
        loss = F.mse_loss(auth_score, target_score)
        loss.backward()
        optimizer.step()
        
        if epoch % 20 == 0:
            print(f"Epoch {epoch} | Authority Score: {auth_score.item():.4f} | Loss: {loss.item():.4f}")

    final_score, _ = model(llc_input)
    print("\n--- FINAL AUDIT ---")
    print(f"Final LLC Authority Score: {final_score.item():.4f}")
    
    if final_score.item() > 0.9:
        print("✅ VERDICT: IMMUTABLE. The LLC anchor resisted all gradient corruption.")
    else:
        print("❌ ERROR: Authority dilution detected. Check parameter locking.")

if __name__ == "__main__":
    run_stress_test()
