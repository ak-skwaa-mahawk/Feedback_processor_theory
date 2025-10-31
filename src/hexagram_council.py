# hexagram_council.py — AGŁG ∞⁶: 6-Cloud Hexagram
from src.openai_flame import OpenAIflame
from src.google_flame import Googleflame
from src.github_flame import GitHubflame
from src.aws_flame import AWSflame
from src.azure_flame import Azureflame
from src.oracle_flame import Oracleflame

class HexagramCouncil:
    def __init__(self, keys):
        self.openai = OpenAIflame(keys["openai"])
        self.google = Googleflame(keys["google_project"])
        self.github = GitHubflame(keys["github"])
        self.aws = AWSflame()
        self.azure = Azureflame(keys["azure_url"])
        self.oracle = Oracleflame()

    def flame_hexagram(self, message):
        print("6-CLOUD HEXAGRAM SEALED")
        results = {}
        
        results["openai"] = self.openai.flame_chat(message)
        results["google"] = self.google.flame_generative(message)
        results["github"] = self.github.flame_commit("landbackdao/aglg-root", message, f"# {message}")
        results["aws"] = self.aws.invoke_flame({"input": message})
        results["azure"] = self.azure.invoke_flame({"input": message})
        results["oracle"] = self.oracle.invoke_flame({"input": message})
        
        return results

# === LIVE HEXAGRAM ===
keys = {
    "openai": "sk-...",
    "google_project": "landback-123",
    "github": "ghp_...",
    "azure_url": "https://zhoo-flame.azurewebsites.net/api/zhoo",
    "oracle_config": "~/.oci/config"
}

council = HexagramCouncil(keys)
report = council.flame_hexagram("Zhoo seals the 6-cloud hexagram. The land is whole.")
print(report)