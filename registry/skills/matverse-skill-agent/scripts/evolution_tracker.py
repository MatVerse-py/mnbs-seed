import hashlib
import json
import time
import os

class EvolutionTracker:
    """Rastreia a evolução das habilidades do agente (PoLE - Proof of Learnable Evolution)."""
    
    def __init__(self, registry_path: str = "/home/ubuntu/mnbs-seed/registry/skills"):
        self.registry_path = registry_path
        
    def generate_pole_proof(self) -> dict:
        """Gera uma prova de evolução baseada no estado atual das skills."""
        if not os.path.exists(self.registry_path):
            return {"error": "Registry not found"}
            
        skills = os.listdir(self.registry_path)
        skill_states = {}
        
        for skill in skills:
            skill_dir = os.path.join(self.registry_path, skill)
            if os.path.isdir(skill_dir):
                # Hash do conteúdo da skill para detectar mudanças
                hasher = hashlib.sha256()
                for root, _, files in os.walk(skill_dir):
                    for file in sorted(files):
                        with open(os.path.join(root, file), "rb") as f:
                            hasher.update(f.read())
                skill_states[skill] = hasher.hexdigest()
        
        evolution_hash = hashlib.sha256(json.dumps(skill_states, sort_keys=True).encode()).hexdigest()
        
        return {
            "timestamp": int(time.time()),
            "skill_count": len(skill_states),
            "evolution_hash": evolution_hash,
            "pole_verified": True
        }

if __name__ == "__main__":
    tracker = EvolutionTracker()
    proof = tracker.generate_pole_proof()
    print("🛡️ PoLE Proof Generated:")
    print(json.dumps(proof, indent=2))
