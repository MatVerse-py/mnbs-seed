import os
import json
import sys
from typing import Dict, List

def check_environment() -> Dict:
    """Valida o ambiente para deploy soberano MatVerse."""
    results = {
        "git_status": "NOT_FOUND",
        "secrets_leak": "CLEAN",
        "artifacts_found": [],
        "risk_score": 0.0
    }
    
    # Check for .git exposure
    if os.path.exists(".git"):
        results["git_status"] = "EXPOSED"
        results["risk_score"] += 0.5
        
    # Check for common secret patterns in files
    secret_patterns = ["API_KEY", "SECRET", "TOKEN", "PASSWORD"]
    for root, _, files in os.walk("."):
        if ".git" in root: continue
        for file in files:
            if any(p in file.upper() for p in secret_patterns):
                results["secrets_leak"] = "POTENTIAL_LEAK"
                results["risk_score"] += 0.3
                break
                
    # Check for artifacts
    if any(f.endswith(".apk") for f in os.listdir(".")):
        results["artifacts_found"].append("ANDROID_APK")
    if any(f.endswith(".zip") for f in os.listdir(".")):
        results["artifacts_found"].append("ZIP_ARCHIVE")
        
    return results

if __name__ == "__main__":
    report = check_environment()
    print(json.dumps(report, indent=2))
