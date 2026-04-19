import random
import json
import time

def inject_chaos(system_state: dict, intensity: float = 0.1) -> dict:
    """Injeta ruído controlado no estado do sistema para testar antifragilidade."""
    perturbed_state = system_state.copy()
    
    # Perturbação de latência (Theta)
    if "theta" in perturbed_state:
        perturbed_state["theta"] *= (1 + random.uniform(0, intensity))
        
    # Perturbação de coerência (Psi)
    if "psi" in perturbed_state:
        perturbed_state["psi"] *= (1 - random.uniform(0, intensity * 0.5))
        
    # Simulação de corrupção de dados (Integrity)
    if "integrity" in perturbed_state:
        if random.random() < intensity:
            perturbed_state["integrity"] = False
            
    return perturbed_state

if __name__ == "__main__":
    base_state = {"psi": 0.95, "theta": 40.0, "integrity": True}
    print("Base State:", base_state)
    for i in range(3):
        chaos_state = inject_chaos(base_state, intensity=0.2)
        print(f"Chaos Iteration {i+1}:", chaos_state)
