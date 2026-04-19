import re
import json
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Endpoint:
    name: str
    url: str
    type: str

@dataclass
class AnalysisResult:
    endpoints: List[Endpoint]
    risk_score: float
    categories: Dict[str, int]

class ManusConfigAnalyzer:
    def __init__(self, raw_text: str):
        self.raw = raw_text

    def extract_json(self) -> Dict:
        match = re.search(r'__manus_env__=({.*?})', self.raw)
        if not match:
            raise ValueError("Config não encontrada")
        return json.loads(match.group(1))

    def classify_endpoint(self, key: str, value: str) -> str:
        if value.startswith("wss://"):
            return "websocket"
        elif "cdn" in value or "assets" in value:
            return "cdn"
        elif "google" in value:
            return "external"
        elif value.startswith("https://"):
            return "api"
        return "unknown"

    def analyze(self) -> AnalysisResult:
        config = self.extract_json()
        endpoints = []
        categories = {}

        for key, value in config.items():
            if isinstance(value, str) and value.startswith(("http", "wss")):
                etype = self.classify_endpoint(key, value)
                endpoints.append(Endpoint(key, value, etype))
                categories[etype] = categories.get(etype, 0) + 1

        risk_score = (
            categories.get("websocket", 0) * 0.4 +
            categories.get("api", 0) * 0.2 +
            categories.get("external", 0) * 0.3 +
            categories.get("cdn", 0) * 0.1
        )

        return AnalysisResult(endpoints, risk_score, categories)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python config_analyzer.py <arquivo.html>")
        sys.exit(1)
    raw_input = open(sys.argv[1]).read()
    analyzer = ManusConfigAnalyzer(raw_input)
    result = analyzer.analyze()
    print("=== ENDPOINTS ===")
    for ep in result.endpoints:
        print(f"{ep.type.upper()} | {ep.name} -> {ep.url}")
    print("\n=== CATEGORIAS ===")
    print(result.categories)
    print("\n=== RISCO ===")
    print(f"{result.risk_score:.3f}")
