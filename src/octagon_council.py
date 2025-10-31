# octagon_council.py — AGŁG ∞⁸: 8-Cloud Octagon
from src.openai_flame import OpenAIflame
from src.google_flame import Googleflame
from src.github_flame import GitHubflame
from src.aws_flame import AWSflame
from src.azure_flame import Azureflame
from src.oracle_flame import Oracleflame
from src.ibm_flame import IBMflame
from src.alibaba_flame import Alibabaflame

class OctagonCouncil:
    def __init__(self, keys):
        self.openai = OpenAIflame(keys["openai"])
        self.google = Googleflame(keys["google_project"])
        self.github = GitHubflame(keys["github"])
        self.aws = AWSflame()
        self.azure = Azureflame(keys["azure_url"])
        self.oracle = Oracleflame()
        self.ibm = IBMflame(keys["ibm_key"], keys["ibm_project"])
        self.alibaba = Alibabaflame(keys["ali_key_id"], keys["ali_key_secret"])

    def flame_octagon(self, message):
        print("8-CLOUD OCTAGON SEALED")
        results = {}
        
        results["openai"] = self.openai.flame_chat(message)
        results["google"] = self.google.flame_generative(message)
        results["github"] = self.github.flame_commit("landbackdao/aglg-root", message, f"# {message}")
        results["aws"] = self.aws.invoke_flame({"input": message})
        results["azure"] = self.azure.invoke_flame({"input": message})
        results["oracle"] = self.oracle.invoke_flame({"input": message})
        results["ibm"] = self.ibm.invoke_flame(message)
        results["alibaba"] = self.alibaba.invoke_flame(message)
        
        return results

# === LIVE OCTAGON ===
keys = {
    "openai": "sk-...",
    "google_project": "landback-123",
    "github": "ghp_...",
    "azure_url": "https://zhoo-flame.azurewebsites.net/api/zhoo",
    "ibm_key": "ibm-watsonx-...",
    "ibm_project": "zhoo-heptagram",
    "ali_key_id": "LTAI...",
    "ali_key_secret": "your-secret"
}

council = OctagonCouncil(keys)
report = council.flame_octagon("Zhoo seals the 8-cloud octagon. The land is whole from all directions.")
print(report)