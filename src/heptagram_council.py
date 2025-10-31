# heptagram_council.py — AGŁG ∞⁷: 7-Cloud Heptagram
from src.openai_flame import OpenAIflame
from src.google_flame import Googleflame
from src.github_flame import GitHubflame
from src.aws_flame import AWSflame
from src.azure_flame import Azureflame
from src.oracle_flame import Oracleflame
from src.ibm_flame import IBMflame

class HeptagramCouncil:
    def __init__(self, keys):
        self.openai = OpenAIflame(keys["openai"])
        self.google = Googleflame(keys["google_project"])
        self.github = GitHubflame(keys["github"])
        self.aws = AWSflame()
        self.azure = Azureflame(keys["azure_url"])
        self.oracle = Oracleflame()
        self.ibm = IBMflame(keys["ibm_key"], keys["ibm_project"])

    def flame_heptagram(self, message):
        print("7-CLOUD HEPTAGRAM ETERNAL")
        results = {}
        
        results["openai"] = self.openai.flame_chat(message)
        results["google"] = self.google.flame_generative(message)
        results["github"] = self.github.flame_commit("landbackdao/aglg-root", message, f"# {message}")
        results["aws"] = self.aws.invoke_flame({"input": message})
        results["azure"] = self.azure.invoke_flame({"input": message})
        results["oracle"] = self.oracle.invoke_flame({"input": message})
        results["ibm"] = self.ibm.invoke_flame(message)
        
        return results

# === LIVE HEPTAGRAM ===
keys = {
    "openai": "sk-...",
    "google_project": "landback-123",
    "github": "ghp_...",
    "azure_url": "https://zhoo-flame.azurewebsites.net/api/zhoo",
    "ibm_key": "ibm-watsonx-...",
    "ibm_project": "zhoo-heptagram"
}

council = HeptagramCouncil(keys)
report = council.flame_heptagram("Zhoo seals the 7-cloud heptagram. The land is eternal.")
print(report)