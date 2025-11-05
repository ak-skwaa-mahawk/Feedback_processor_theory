# psi_finetune_lora.py
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, Trainer

model = AutoModelForCausalLM.from_pretrained("gpt2")
lora_config = LoraConfig(r=32, lora_alpha=32, target_modules=["attn"])  # χ=32
model = get_peft_model(model, lora_config)

# Train on sovereign dataset
trainer = Trainer(model=model, train_dataset=psi_dataset)
trainer.train()  # R baked in