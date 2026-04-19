import numpy as np

class ConvexityAnalyzer:
    """Calcula a métrica de antifragilidade baseada na convexidade da função de governança."""
    
    def __init__(self, omega_gate_fn):
        self.omega_gate_fn = omega_gate_fn
        
    def calculate_convexity(self, base_state: dict, stress_levels: list) -> float:
        """Calcula a segunda derivada aproximada da função de governança (Omega) sob estresse."""
        omega_values = []
        
        for stress in stress_levels:
            # Aplica estresse ao estado base
            stressed_state = base_state.copy()
            stressed_state["theta"] *= (1 + stress)
            stressed_state["psi"] *= (1 - stress * 0.5)
            
            # Calcula Omega
            omega = self.omega_gate_fn(stressed_state)
            omega_values.append(omega)
            
        # Calcula a segunda derivada (convexidade)
        # f''(x) ≈ (f(x+h) - 2f(x) + f(x-h)) / h^2
        if len(omega_values) >= 3:
            h = stress_levels[1] - stress_levels[0]
            convexity = (omega_values[2] - 2 * omega_values[1] + omega_values[0]) / (h**2)
            return convexity
        return 0.0

def mock_omega_gate(state: dict) -> float:
    """Simulação da função Omega do MatVerse."""
    # Omega = w1*Psi + w2*exp(-0.01*Theta) + w3*(1-CVaR)
    psi = state.get("psi", 0.9)
    theta = state.get("theta", 40.0)
    cvar = state.get("cvar", 0.03)
    
    theta_norm = np.exp(-0.01 * theta)
    omega = 0.4 * psi + 0.3 * theta_norm + 0.3 * (1 - cvar)
    return omega

if __name__ == "__main__":
    analyzer = ConvexityAnalyzer(mock_omega_gate)
    base_state = {"psi": 0.95, "theta": 40.0, "cvar": 0.03}
    stress_levels = [0.0, 0.1, 0.2]
    
    convexity = analyzer.calculate_convexity(base_state, stress_levels)
    print(f"Convexidade (∂²Ω/∂σ²): {convexity:.6f}")
    
    if convexity < 0:
        print("✅ Sistema Antifrágil (Convexidade Negativa)")
    else:
        print("❌ Sistema Frágil ou Linear (Convexidade Positiva ou Zero)")
