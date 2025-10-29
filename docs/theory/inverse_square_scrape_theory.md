from src.adversarial_defense.isst_defense import ISSTDefense
result = ISSTDefense().robust_predict(x_adv, model)
print(result["glyph"])