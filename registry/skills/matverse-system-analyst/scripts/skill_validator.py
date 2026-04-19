import os
import re
from dataclasses import dataclass
from typing import List

@dataclass
class SkillRisk:
    name: str
    risk_level: str
    issues: List[str]

class SkillAnalyzer:
    def __init__(self, skill_paths):
        self.paths = skill_paths

    def load_skill(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def analyze(self):
        results = []
        for path in self.paths:
            content = self.load_skill(path)
            issues = []
            if re.search(r"http[s]?://", content):
                issues.append("external_call")
            if re.search(r"exec\(|eval\(", content):
                issues.append("dynamic_execution")
            if re.search(r"token|secret|key", content, re.IGNORECASE):
                issues.append("possible_secret")
            if re.search(r"subprocess|os\.system", content):
                issues.append("shell_execution")
            risk = self.classify(issues)
            results.append(SkillRisk(name=os.path.basename(path), risk_level=risk, issues=issues))
        return results

    def classify(self, issues):
        if "shell_execution" in issues or "dynamic_execution" in issues:
            return "CRITICAL"
        if "external_call" in issues:
            return "HIGH"
        if "possible_secret" in issues:
            return "MEDIUM"
        return "LOW"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python skill_validator.py <arquivo.skill> ...")
        sys.exit(1)
    analyzer = SkillAnalyzer(sys.argv[1:])
    results = analyzer.analyze()
    for r in results:
        print(f"\n=== {r.name} ===")
        print("RISK:", r.risk_level)
        print("ISSUES:", r.issues)
