import os
import re
import json

class SkillOptimizer:
    """Otimiza o conteúdo de SKILL.md para eficiência de tokens e clareza semântica."""
    
    def __init__(self, skill_path: str):
        self.skill_path = skill_path
        self.skill_md_path = os.path.join(skill_path, "SKILL.md")
        
    def analyze_efficiency(self) -> dict:
        """Analisa a eficiência da skill (tamanho vs. densidade de informação)."""
        if not os.path.exists(self.skill_md_path):
            return {"error": "SKILL.md not found"}
            
        with open(self.skill_md_path, "r") as f:
            content = f.read()
            
        word_count = len(content.split())
        script_count = len(os.listdir(os.path.join(self.skill_path, "scripts"))) if os.path.exists(os.path.join(self.skill_path, "scripts")) else 0
        
        # Métrica heurística de densidade
        density = (script_count * 100) / word_count if word_count > 0 else 0
        
        return {
            "word_count": word_count,
            "script_count": script_count,
            "info_density": density,
            "status": "OPTIMIZED" if density > 0.5 else "VERBOSE"
        }

    def suggest_refactoring(self):
        """Sugere mover seções longas para referências."""
        print(f"🔍 Analisando {self.skill_md_path}...")
        metrics = self.analyze_efficiency()
        print(f"📊 Métricas: {json.dumps(metrics, indent=2)}")
        
        if metrics.get("word_count", 0) > 1000:
            print("⚠️ Sugestão: Mover seções de documentação extensas para a pasta 'references/'.")

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/skills/matverse-system-analyst"
    optimizer = SkillOptimizer(path)
    optimizer.suggest_refactoring()
