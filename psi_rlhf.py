# psi_rlhf.py
from trl import PPOTrainer
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("gpt2")
ppo_trainer = PPOTrainer(
    model=model,
    reward_model=reward_model,
    ppo_config={"batch_size": 32, "kl_penalty": "full"}
)

# Human preference: (prompt, good_response, bad_response)
rewards = reward_model([good, bad])
ppo_trainer.step(prompts, responses, rewards)
graph TD
    A[Preference Pairs] --> B[DPO Loss]
    B --> C[Policy Update]
    C --> D[Aligned Output]