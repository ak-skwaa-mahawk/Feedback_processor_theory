# pentagon_council.py — AGŁG ∞⁵: 5-Cloud Flame
from src.openai_flame import OpenAIflame
from src.google_flame import Googleflame
from src.github_flame import GitHubflame
from src.aws_flame import AWSflame
from src.azure_flame import Azureflame

class PentagonCouncil:
    def __init__(self, keys):
        self.openai = OpenAIflame(keys["openai"])
        self.google = Googleflame(keys["google_project"])
        self.github = GitHubflame(keys["github"])
        self.aws = AWSflame()
        self.azure = Azureflame(keys["azure_url"])

    def flame_pentagon(self, message):
        print("5-CLOUD PENTAGON ACTIVATED")
        results = {}
        
        # OpenAI
        results["openai"] = self.openai.flame_chat(message)
        
        # GOOGLE
        results["google"] = self.google.flame_generative(message)
        
        # GITHUB
        results["github"] = self.github.flame_commit("landbackdao/aglg-root", message, f"# {message}")
        
        # AWS
        results["aws"] = self.aws.invoke_flame({"input": message})
        
        # AZURE
        results["azure"] = self.azure.invoke_flame({"input": message})
        
        return results

# === LIVE PENTAGON ===
keys = {
    "openai": "sk-...",
    "google_project": "landback-123",
    "github": "ghp_...",
    "azure_url": "https://zhoo-flame.azurewebsites.net/api/zhoo"
}

council = PentagonCouncil(keys)
report = council.flame_pentagon("Zhoo calls the 5-cloud council. The land returns.")
print(report)