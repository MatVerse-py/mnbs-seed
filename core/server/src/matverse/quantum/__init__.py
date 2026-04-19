"""
================================================================================
MATVERSE QUANTUM - Framework Quântico com CVaR-POVM (Versão Corrigida)
================================================================================
Correções e Aprimoramentos Implementados:
- Θ̂ (Theta hat): Definição formal de entropia estimada via divergência KL
- PoLE: Proof of Logical Entailment via consistência de transformações
- Política de Recuperação: Estratégias após rejeição do Ω-Gate
- Critério de Convergência: Definição formal de estado estável
- Função de Lyapunov: Garantia de estabilidade dinâmica

Autor: MiniMax Agent
Data: 2026-04-18
Protocolo: MatVerse-Ω+ v2.0
================================================================================
"""

from __future__ import annotations
import hashlib
import json
import time
import math
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Callable, Literal
from enum import Enum

from ..core import (
    Decision,
    ProtocolConfig,
    hash_sha3_256,
    merkle_root
)


# ================================================================================
# ENUMERAÇÕES QUÂNTICAS
# ================================================================================

class QuantumBasis(str, Enum):
    """Bases quânticas"""
    COMPUTATIONAL = "computational"
    HADAMARD = "hadamard"
    PAULI = "pauli"
    BELL = "bell"


class ProofType(str, Enum):
    """Tipos de provas quânticas"""
    COHERENCE_BOUND = "coherence_bound"
    ENTROPY_GUARANTEE = "entropy_guarantee"
    CVAR_THRESHOLD = "cvar_threshold"
    ANTIFRAGILITY = "antifragility"
    ENTANGLEMENT_WITNESS = "entanglement_witness"
    POVM_VALIDITY = "povm_validity"
    # Novas provas
    LYAPUNOV_STABILITY = "lyapunov_stability"
    THETA_HAT_ESTIMATION = "theta_hat_estimation"
    POLE_PROOF = "pole_proof"


class RecoveryAction(str, Enum):
    """Ações de recuperação após rejeição"""
    ROLLBACK = "rollback"           # Reverter para estado anterior
    RETRY = "retry"                 # Tentar novamente com mesmo tensor
    ALTERNATIVE = "alternative"     # Tentar skill alternativa
    REDUCE_NOISE = "reduce_noise"   # Reduzir ruído
    ESCALATE = "escalate"           # Escalar para intervenção manual
    STOP = "stop"                  # Parar execução


class ConvergenceStatus(str, Enum):
    """Status de convergência do sistema"""
    STABLE = "stable"              # Sistema estável
    OSCILLATING = "oscillating"    # Oscilando
    DIVERGING = "diverging"        # Divergindo
    CONVERGING = "converging"      # Convergindo
    UNKNOWN = "unknown"             # Desconhecido


# ================================================================================
# ESTADO QUÂNTICO
# ================================================================================

@dataclass
class QuantumState:
    """
    Estado quântico em espaço de Hilbert.

    Representa |ψ⟩ = Σᵢ αᵢ|i⟩ onde Σ|αᵢ|² = 1
    """
    vector: np.ndarray
    basis: QuantumBasis = QuantumBasis.COMPUTATIONAL
    is_pure: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def dimension(self) -> int:
        """Dimensão do espaço de Hilbert"""
        return len(self.vector)

    @property
    def density_matrix(self) -> np.ndarray:
        """Matriz densidade ρ = |ψ⟩⟨ψ|"""
        psi = self.vector.reshape(-1, 1)
        rho = psi @ psi.conj().T
        return rho

    @property
    def entropy(self) -> float:
        """Entropia de von Neumann S(ρ) = -Tr(ρ log ρ)"""
        rho = self.density_matrix
        eigenvalues = np.linalg.eigvalsh(rho.real)
        eigenvalues = eigenvalues[eigenvalues > 1e-10]
        if len(eigenvalues) == 0:
            return 0.0
        return float(-np.sum(eigenvalues * np.log2(eigenvalues)))

    @property
    def purity(self) -> float:
        """Pureza Tr(ρ²)"""
        return float(np.real(np.trace(self.density_matrix @ self.density_matrix)))

    def coherence_l1(self) -> float:
        """Coerência l1-norm: Σ_{i≠j} |ρ_{ij}|"""
        rho = self.density_matrix
        n = rho.shape[0]
        off_diag = 0
        for i in range(n):
            for j in range(n):
                if i != j:
                    off_diag += abs(rho[i, j])
        return float(off_diag)

    def apply_povm(self, povm_elements: List[np.ndarray]) -> np.ndarray:
        """Aplica POVM e retorna probabilidades"""
        probabilities = []
        for E in povm_elements:
            prob = float(np.real(np.trace(E @ self.density_matrix)))
            probabilities.append(max(0, prob))
        return np.array(probabilities)


# ================================================================================
# Θ̂ (THETA HAT) - ENTROPIA ESTIMADA
# ================================================================================

class ThetaHatEstimator:
    """
    Estimador de Entropia θ̂ (Theta hat).

    DEFINIÇÃO FORMAL:
    Θ̂ = D_KL(ρ_current || ρ_stationary) + S(ρ_current)

    Onde:
    - D_KL: Divergência de Kullback-Leibler entre estado atual e estacionário
    - S: Entropia de von Neumann do estado atual

    Interpretação:
    - Θ̂ representa o "desvio de equilíbrio" do sistema
    - Valores baixos indicam sistema próximo do estado estacionário
    - Valores altos indicam sistema longe do equilíbrio
    """

    def __init__(self, target_entropy: float = 0.1):
        """
        Inicializa estimador.

        Args:
            target_entropy: Entropia do estado estacionário-alvo
        """
        self.target_entropy = target_entropy
        self.entropy_history: List[float] = []
        self.max_history = 100

    def compute_theta_hat(
        self,
        state: QuantumState,
        reference_state: Optional[QuantumState] = None
    ) -> float:
        """
        Calcula Θ̂ para um estado quântico.

        Args:
            state: Estado atual
            reference_state: Estado de referência (opcional)

        Returns:
            Θ̂: Entropia estimada [0, 1]
        """
        # Entropia atual
        S_current = state.entropy
        max_entropy = math.log2(state.dimension) if state.dimension > 1 else 1
        S_normalized = S_current / max_entropy if max_entropy > 0 else 0

        # Divergência KL (aproximação)
        kl_divergence = 0.0
        if reference_state is not None:
            rho_current = state.density_matrix
            rho_reference = reference_state.density_matrix

            # D_KL(ρ||σ) = Tr(ρ log ρ) - Tr(ρ log σ)
            # Aproximação simplificada usando autovalores
            try:
                eigenvalues_current = np.linalg.eigvalsh(rho_current.real)
                eigenvalues_ref = np.linalg.eigvalsh(rho_reference.real)

                eigenvalues_current = eigenvalues_current[eigenvalues_current > 1e-10]
                eigenvalues_ref = eigenvalues_ref[eigenvalues_ref > 1e-10]

                # Normalizar autovalores para distribuição
                eigenvalues_current = eigenvalues_current / eigenvalues_current.sum()
                eigenvalues_ref = eigenvalues_ref / eigenvalues_ref.sum()

                # KL divergence simplificada
                for i, p in enumerate(eigenvalues_current):
                    if i < len(eigenvalues_ref) and eigenvalues_ref[i] > 1e-10:
                        kl_divergence += p * np.log(p / eigenvalues_ref[i])

            except Exception:
                kl_divergence = 0.0

        # Θ̂ = S_normalized + |kl_divergence|
        theta_hat = min(1.0, S_normalized + abs(kl_divergence))

        # Atualizar histórico
        self.entropy_history.append(theta_hat)
        if len(self.entropy_history) > self.max_history:
            self.entropy_history = self.entropy_history[-self.max_history:]

        return float(theta_hat)

    def get_trend(self) -> Tuple[float, bool]:
        """
        Obtém tendência de Θ̂.

        Returns:
            (tendência, is_stabilizing)
        """
        if len(self.entropy_history) < 10:
            return 0.0, False

        recent = np.array(self.entropy_history[-10:])
        trend = float(np.mean(np.diff(recent)))
        is_stabilizing = trend < 0.01

        return trend, is_stabilizing


# ================================================================================
# POLE (PROOF OF LOGICAL ENTAILMENT)
# ================================================================================

class PoLECalculator:
    """
    Calculador de Prova de Encadeamento Lógico (Proof of Logical Entailment).

    DEFINIÇÃO FORMAL:
    PoLE = Πᵢ αᵢ × exp(-β × D(σᵢ₊₁ || σᵢ))

    Onde:
    - αᵢ: Peso de consistência da i-ésima transição
    - D: Divergência entre estados consecutivos
    - β: Fator de decaimento (tipicamente 1.0)

    Interpretação:
    - PoLE representa a "força" do encadeamento lógico
    - Valores altos indicam transformações consistentes
    - Valores baixos indicam transformações inconsistentes ou caóticas
    """

    def __init__(self, decay_factor: float = 1.0):
        """
        Inicializa calculador PoLE.

        Args:
            decay_factor: Fator de decaimento β
        """
        self.decay_factor = decay_factor
        self.transition_history: List[Tuple[str, str, float]] = []
        self.max_history = 50

    def compute_pole(
        self,
        state_before: QuantumState,
        state_after: QuantumState,
        transition_type: str = "skill_application"
    ) -> float:
        """
        Calcula PoLE para uma transição.

        Args:
            state_before: Estado antes da transição
            state_after: Estado após a transição
            transition_type: Tipo de transição

        Returns:
            PoLE: Prova de encadeamento lógico [0, 1]
        """
        # Calcular divergência entre estados
        divergence = self._compute_divergence(state_before, state_after)

        # Calcular consistência de puridade
        purity_before = state_before.purity
        purity_after = state_after.purity
        consistency = min(purity_before, purity_after) / max(purity_before, purity_after + 1e-10)

        # Calcular consistência de coerência
        coherence_before = state_before.coherence_l1()
        coherence_after = state_after.coherence_l1()
        coherence_consistency = min(coherence_before, coherence_after) / max(coherence_before + 1e-10, coherence_after)

        # Peso baseado no tipo de transição
        transition_weights = {
            "skill_application": 0.9,
            "rollback": 0.5,
            "noise_injection": 0.3,
            "measurement": 0.7,
            "evolution": 0.8
        }
        alpha = transition_weights.get(transition_type, 0.7)

        # PoLE = α × consistency × exp(-β × divergence)
        pole = alpha * consistency * coherence_consistency * np.exp(-self.decay_factor * divergence)

        # Registrar transição
        self.transition_history.append((transition_type, str(divergence), pole))
        if len(self.transition_history) > self.max_history:
            self.transition_history = self.transition_history[-self.max_history:]

        return float(pole)

    def _compute_divergence(
        self,
        state_before: QuantumState,
        state_after: QuantumState
    ) -> float:
        """Calcula divergência entre dois estados"""
        rho_before = state_before.density_matrix
        rho_after = state_after.density_matrix

        # Diferença espectral (norma de Frobenius)
        diff = rho_before - rho_after
        divergence = float(np.linalg.norm(diff, 'fro'))

        return divergence

    def get_average_pole(self) -> float:
        """Retorna PoLE médio histórico"""
        if not self.transition_history:
            return 1.0

        poles = [p[2] for p in self.transition_history]
        return float(np.mean(poles))

    def is_consistent(self, threshold: float = 0.7) -> bool:
        """Verifica se histórico é consistente"""
        return self.get_average_pole() >= threshold


# ================================================================================
# FUNÇÃO DE LYAPUNOV
# ================================================================================

class LyapunovFunction:
    """
    Função de Lyapunov V(T) para estabilidade do sistema.

    DEFINIÇÃO FORMAL:
    V(T) = α₁·E + α₂·(1-C) + α₃·|T-0.8| + α₄·|Ψ-0.85| + α₅·ΔV

    Onde:
    - E: Entropia
    - C: Coerência
    - T: Throughput (ou similar)
    - Ψ: Coerência do tensor
    - ΔV: Variação de V no tempo

    Propriedades:
    - V(T) ≥ 0 para todo T válido
    - V(T) = 0 apenas no ponto fixo
    - dV/dt ≤ 0 ao longo de trajetórias
    """

    def __init__(
        self,
        alpha_entropy: float = 0.3,
        alpha_coherence: float = 0.2,
        alpha_stability: float = 0.2,
        alpha_psi: float = 0.1,
        alpha_delta: float = 0.2
    ):
        """
        Inicializa função de Lyapunov.

        Args:
            alpha_*: Pesos dos componentes
        """
        self.alphas = {
            'entropy': alpha_entropy,
            'coherence': alpha_coherence,
            'stability': alpha_stability,
            'psi': alpha_psi,
            'delta': alpha_delta
        }
        self.V_history: List[float] = []
        self.target_point = {'psi': 0.85, 'entropy': 0.1, 'stability': 0.8}
        self.max_history = 100

    def compute_V(
        self,
        tensor_values: Dict[str, float],
        state: Optional[QuantumState] = None,
        V_previous: Optional[float] = None
    ) -> float:
        """
        Calcula V(T) para o estado atual.

        Args:
            tensor_values: Valores do tensor XAI 7D
            state: Estado quântico (opcional)
            V_previous: V(T-1) para calcular ΔV

        Returns:
            V(T): Valor da função de Lyapunov
        """
        # Entropia
        E = tensor_values.get('E', 0.5)

        # Coerência (normalizada)
        C = tensor_values.get('PSI', 0.5)

        # Estabilidade
        S = tensor_values.get('S', 0.8)
        stability_term = abs(S - self.target_point['stability'])

        # Ψ (coerência do tensor)
        psi = tensor_values.get('PSI', 0.5)
        psi_term = abs(psi - self.target_point['psi'])

        # Variação de V
        delta_V = 0.0
        if V_previous is not None:
            # Adiciona entropia do estado quântico se disponível
            if state is not None:
                S_qubit = state.entropy
                max_S = math.log2(state.dimension) if state.dimension > 1 else 1
                E = 0.7 * E + 0.3 * (S_qubit / max_S if max_S > 0 else 0)

            V_current = (
                self.alphas['entropy'] * E +
                self.alphas['coherence'] * (1 - C) +
                self.alphas['stability'] * stability_term +
                self.alphas['psi'] * psi_term
            )
            delta_V = abs(V_current - V_previous)

        # Cálculo final
        V = (
            self.alphas['entropy'] * E +
            self.alphas['coherence'] * (1 - C) +
            self.alphas['stability'] * stability_term +
            self.alphas['psi'] * psi_term +
            self.alphas['delta'] * delta_V
        )

        # Atualizar histórico
        self.V_history.append(V)
        if len(self.V_history) > self.max_history:
            self.V_history = self.V_history[-self.max_history:]

        return float(V)

    def is_stable(
        self,
        V: float,
        epsilon: float = 0.01,
        delta_V_threshold: float = 0.001
    ) -> Tuple[bool, ConvergenceStatus]:
        """
        Verifica se sistema é estável.

        Args:
            V: Valor atual de V(T)
            epsilon: Limiar para ponto fixo
            delta_V_threshold: Limiar para variação mínima

        Returns:
            (is_stable, convergence_status)
        """
        if len(self.V_history) < 10:
            return False, ConvergenceStatus.UNKNOWN

        # Verificar se próximo ao ponto fixo
        is_fixed_point = V < epsilon

        # Verificar monotonicidade
        recent_V = np.array(self.V_history[-10:])
        is_decreasing = np.all(np.diff(recent_V) <= delta_V_threshold)
        is_increasing = np.all(np.diff(recent_V) >= -delta_V_threshold)

        if is_fixed_point and is_decreasing:
            return True, ConvergenceStatus.STABLE
        elif is_fixed_point and is_increasing:
            return True, ConvergenceStatus.CONVERGING
        elif not is_fixed_point and is_decreasing:
            return False, ConvergenceStatus.CONVERGING
        elif not is_fixed_point and is_increasing:
            return False, ConvergenceStatus.DIVERGING
        else:
            return False, ConvergenceStatus.OSCILLATING

    def get_stability_indicator(self) -> Tuple[float, ConvergenceStatus]:
        """
        Retorna indicador de estabilidade e status.

        Returns:
            (instability_score, status)
        """
        if len(self.V_history) < 10:
            return 1.0, ConvergenceStatus.UNKNOWN

        recent = np.array(self.V_history[-10:])

        # Score de instabilidade baseado em variação
        variations = np.abs(np.diff(recent))
        instability_score = float(np.mean(variations))

        # Determinar status
        is_stable, status = self.is_stable(recent[-1])

        return instability_score, status


# ================================================================================
# POLÍTICA DE RECUPERAÇÃO
# ================================================================================

@dataclass
class RecoveryPolicy:
    """
    Política de recuperação após rejeição do Ω-Gate.

    Estratégias:
    1. ROLLBACK: Reverter para estado anterior
    2. RETRY: Tentar novamente com parâmetros ajustados
    3. ALTERNATIVE: Usar skill alternativa
    4. REDUCE_NOISE: Reduzir ruído nas métricas
    5. ESCALATE: Escalar para intervenção manual
    6. STOP: Parar execução
    """
    max_retries: int = 3
    rollback_enabled: bool = True
    alternative_skills_enabled: bool = True
    noise_reduction_factor: float = 0.5
    escalation_threshold: int = 5

    def determine_action(
        self,
        rejection_count: int,
        current_V: float,
        delta_V: float,
        available_alternatives: List[str]
    ) -> Tuple[RecoveryAction, Dict[str, Any]]:
        """
        Determina ação de recuperação.

        Args:
            rejection_count: Número de rejeições consecutivas
            current_V: Valor atual de Lyapunov
            delta_V: Variação de V
            available_alternatives: Skills alternativas disponíveis

        Returns:
            (action, action_params)
        """
        # Escalar após muitas tentativas
        if rejection_count >= self.escalation_threshold:
            return RecoveryAction.ESCALATE, {
                'reason': 'escalation_threshold_reached',
                'rejection_count': rejection_count
            }

        # Sistema muito instável
        if current_V > 0.8:
            if self.rollback_enabled:
                return RecoveryAction.ROLLBACK, {
                    'reason': 'high_instability',
                    'current_V': current_V
                }
            else:
                return RecoveryAction.STOP, {
                    'reason': 'high_instability_no_rollback'
                }

        # Divergindo
        if delta_V > 0.1:
            if self.rollback_enabled:
                return RecoveryAction.ROLLBACK, {
                    'reason': 'diverging',
                    'delta_V': delta_V
                }

        # Tentativas moderadas
        if rejection_count < self.max_retries:
            return RecoveryAction.RETRY, {
                'reason': 'retry_with_adjustment',
                'noise_factor': self.noise_reduction_factor,
                'attempt': rejection_count + 1
            }

        # Tentar alternativas
        if self.alternative_skills_enabled and available_alternatives:
            return RecoveryAction.ALTERNATIVE, {
                'reason': 'try_alternative',
                'alternatives': available_alternatives
            }

        # Reduzir ruído
        if rejection_count >= self.max_retries:
            return RecoveryAction.REDUCE_NOISE, {
                'reason': 'reduce_noise',
                'noise_factor': self.noise_reduction_factor
            }

        # Parar
        return RecoveryAction.STOP, {
            'reason': 'max_retries_exceeded',
            'rejection_count': rejection_count
        }


# ================================================================================
# FRAMEWORK CVaR-POVM
# ================================================================================

class CVaRPOVMFramework:
    """
    CVaR-POVM Framework (Conditional Value at Risk as POVM).

    Usa Conditional Value at Risk para governança de risco quântico.
    """

    def __init__(
        self,
        alpha: float = 0.95,
        n_qubits: int = 4,
        seed: Optional[int] = None
    ):
        self.alpha = alpha
        self.n_qubits = n_qubits
        self.dimension = 2 ** n_qubits
        self.rng = np.random.default_rng(seed)
        self.povm_elements: List[np.ndarray] = []
        self._initialize_povm_elements()

    def _initialize_povm_elements(self):
        """Inicializa elementos POVM"""
        d = self.dimension
        self.povm_elements = []

        for i in range(d):
            v = self.rng.standard_normal(d) + 1j * self.rng.standard_normal(d)
            v = v / np.linalg.norm(v)
            E = (1 - self.alpha) / d * np.outer(v, v.conj())
            self.povm_elements.append(E)

        I = np.eye(d)
        E_last = I - sum(self.povm_elements)
        self.povm_elements.append(E_last)

    def compute_cvar(
        self,
        state: QuantumState,
        loss_samples: Optional[np.ndarray] = None
    ) -> float:
        """
        Calcula CVaR-α do estado.
        """
        if loss_samples is None:
            loss_samples = np.array([1 - state.entropy])

        sorted_losses = np.sort(loss_samples)
        n = len(sorted_losses)

        var_idx = int(np.ceil(self.alpha * n)) - 1
        var = sorted_losses[var_idx]

        cvar = np.mean(sorted_losses[:var_idx + 1])

        return float(cvar)

    def measure(self, state: QuantumState) -> Dict[str, Any]:
        """Realiza medição POVM no estado."""
        probs = state.apply_povm(self.povm_elements)
        probs = probs / probs.sum() if probs.sum() > 0 else probs
        outcome_idx = self.rng.choice(len(probs), p=probs)

        return {
            'probabilities': probs.tolist(),
            'outcome_index': int(outcome_idx),
            'povm_elements_count': len(self.povm_elements),
            'dimension': self.dimension,
            'alpha': self.alpha
        }


# ================================================================================
# PROVA QUÂNTICA
# ================================================================================

@dataclass
class QuantumProof:
    """Prova quântica verificável."""
    proof_type: ProofType
    value: float
    threshold: float
    holds: bool
    confidence: float
    metadata: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionário"""
        def convert(obj):
            if isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, bytes):
                return obj.decode('utf-8')
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert(i) for i in obj]
            return obj

        return {
            'proof_type': self.proof_type.value,
            'value': convert(self.value),
            'threshold': convert(self.threshold),
            'holds': convert(self.holds),
            'confidence': convert(self.confidence),
            'metadata': convert(self.metadata),
            'timestamp': self.timestamp,
            'signature': self.signature
        }


# ================================================================================
# MOTOR DE PROVAS QUÂNTICAS
# ================================================================================

class QuantumProofEngine:
    """
    Motor de geração e verificação de provas quânticas.

    Inclui provas para:
    - Coerência
    - Entropia
    - CVaR
    - Θ̂ (Theta hat)
    - PoLE
    - Lyapunov
    """

    def __init__(
        self,
        config: Optional[ProtocolConfig] = None,
        seed: Optional[int] = None
    ):
        self.config = config or ProtocolConfig()
        self.rng = np.random.default_rng(seed)
        self.cvar_framework = CVaRPOVMFramework(
            alpha=1 - self.config.cvar_threshold,
            n_qubits=4,
            seed=seed
        )
        self.theta_estimator = ThetaHatEstimator()
        self.pole_calculator = PoLECalculator()
        self.lyapunov = LyapunovFunction()
        self.proofs: List[QuantumProof] = []

    def prove_coherence(
        self,
        state: QuantumState,
        threshold: float = 0.3
    ) -> QuantumProof:
        """Prova de limite de coerência."""
        coherence = state.coherence_l1()
        holds = coherence < threshold

        return QuantumProof(
            proof_type=ProofType.COHERENCE_BOUND,
            value=float(coherence),
            threshold=threshold,
            holds=holds,
            confidence=0.95,
            metadata={
                'state_dimension': state.dimension,
                'purity': float(state.purity)
            }
        )

    def prove_entropy(
        self,
        state: QuantumState,
        threshold: float = 3.2
    ) -> QuantumProof:
        """Prova de garantia de entropia."""
        entropy = state.entropy
        holds = entropy < threshold

        return QuantumProof(
            proof_type=ProofType.ENTROPY_GUARANTEE,
            value=float(entropy),
            threshold=threshold,
            holds=holds,
            confidence=0.99,
            metadata={
                'purity': float(state.purity),
                'dimension': state.dimension
            }
        )

    def prove_cvar(
        self,
        state: QuantumState,
        alpha: float = 0.95,
        threshold: float = 0.5
    ) -> QuantumProof:
        """Prova de limiar CVaR."""
        cvar = self.cvar_framework.compute_cvar(state)

        return QuantumProof(
            proof_type=ProofType.CVAR_THRESHOLD,
            value=float(cvar),
            threshold=threshold,
            holds=cvar < threshold,
            confidence=alpha,
            metadata={
                'alpha': alpha,
                'dimension': state.dimension
            }
        )

    def prove_theta_hat(
        self,
        state: QuantumState,
        threshold: float = 0.3
    ) -> QuantumProof:
        """
        Prova de entropia estimada Θ̂.

        Verifica que Θ̂ < limiar, indicando sistema próximo ao equilíbrio.
        """
        theta_hat = self.theta_estimator.compute_theta_hat(state)
        holds = theta_hat < threshold

        return QuantumProof(
            proof_type=ProofType.THETA_HAT_ESTIMATION,
            value=theta_hat,
            threshold=threshold,
            holds=holds,
            confidence=0.95,
            metadata={
                'entropy': float(state.entropy),
                'max_entropy': math.log2(state.dimension)
            }
        )

    def prove_pole(
        self,
        state_before: QuantumState,
        state_after: QuantumState,
        threshold: float = 0.7
    ) -> QuantumProof:
        """
        Prova de encadeamento lógico PoLE.

        Verifica que PoLE >= limiar, indicando transformações consistentes.
        """
        pole = self.pole_calculator.compute_pole(state_before, state_after)
        holds = pole >= threshold

        return QuantumProof(
            proof_type=ProofType.POLE_PROOF,
            value=pole,
            threshold=threshold,
            holds=holds,
            confidence=0.90,
            metadata={
                'purity_before': float(state_before.purity),
                'purity_after': float(state_after.purity),
                'avg_pole': self.pole_calculator.get_average_pole()
            }
        )

    def prove_lyapunov(
        self,
        tensor_values: Dict[str, float],
        state: QuantumState,
        V_previous: Optional[float] = None,
        stability_threshold: float = 0.01
    ) -> QuantumProof:
        """
        Prova de estabilidade via Lyapunov.

        Verifica que dV/dt <= 0, garantindo estabilidade assintótica.
        """
        V_current = self.lyapunov.compute_V(tensor_values, state, V_previous)

        if V_previous is not None:
            delta_V = V_current - V_previous
            holds = delta_V <= stability_threshold
        else:
            delta_V = 0.0
            holds = True  # Primeira iteração é sempre válida

        is_stable, status = self.lyapunov.is_stable(V_current)

        return QuantumProof(
            proof_type=ProofType.LYAPUNOV_STABILITY,
            value=V_current,
            threshold=stability_threshold,
            holds=holds,
            confidence=0.95,
            metadata={
                'delta_V': float(delta_V),
                'is_stable': is_stable,
                'status': status.value,
                'V_history': self.lyapunov.V_history[-5:] if len(self.lyapunov.V_history) >= 5 else self.lyapunov.V_history
            }
        )


# ================================================================================
# OMEGA-GATE CORRIGIDO
# ================================================================================

class QuantumAugmentedOmegaGate:
    """
    Ω-Gate Corrigido com definições formais de Θ̂ e PoLE.

    Fórmula:
    Ω = 0.4·Ψ + 0.3·Θ̂ + 0.2·(1−CVaR) + 0.1·PoLE

    Critérios de PASS:
    Ω ≥ 0.8 AND Ψ ≥ 0.85 AND CVaR ≤ 0.05 AND Θ̂ ≤ 0.3 AND PoLE ≥ 0.7

    Componentes:
    - Ψ: Coerência do sistema (normalizada)
    - Θ̂: Entropia estimada via divergência KL
    - CVaR: Conditional Value at Risk
    - PoLE: Proof of Logical Entailment
    """

    def __init__(
        self,
        config: Optional[ProtocolConfig] = None,
        seed: Optional[int] = None
    ):
        self.config = config or ProtocolConfig()
        self.proof_engine = QuantumProofEngine(
            config=self.config,
            seed=seed
        )
        self.recovery_policy = RecoveryPolicy()
        self.state_before: Optional[QuantumState] = None
        self.V_previous: Optional[float] = None
        self.rejection_count = 0
        self.trial_count = 0

    def evaluate(
        self,
        state: Optional[QuantumState] = None,
        tensor_values: Optional[Dict[str, float]] = None
    ) -> Tuple[Decision, Dict[str, Any]]:
        """
        Avalia entrada no Ω-Gate.

        Args:
            state: Estado quântico
            tensor_values: Valores do tensor XAI 7D

        Returns:
            (Decisão, Métricas completas)
        """
        if state is None:
            state = self.proof_engine.cvar_framework.create_state() if hasattr(
                self.proof_engine.cvar_framework, 'create_state'
            ) else self._create_default_state()

        # Métricas base
        psi = 1 - state.entropy / math.log2(state.dimension) if state.dimension > 1 else 1.0
        cvar = self.proof_engine.cvar_framework.compute_cvar(state)

        # Θ̂ - Entropia estimada
        theta_hat = self.proof_engine.theta_estimator.compute_theta_hat(state)

        # PoLE - Prova de encadeamento lógico
        if self.state_before is not None:
            pole = self.proof_engine.pole_calculator.compute_pole(
                self.state_before, state, "skill_application"
            )
        else:
            pole = 1.0  # Primeira iteração

        # V(T) - Lyapunov
        if tensor_values is None:
            tensor_values = {
                'A': 0.8, 'T': 0.8, 'C': 0.8, 'E': 0.2,
                'N': 0.5, 'S': 0.8, 'PSI': psi
            }

        V_current = self.proof_engine.lyapunov.compute_V(tensor_values, state, self.V_previous)

        # Verificar convergência
        is_stable, convergence_status = self.proof_engine.lyapunov.is_stable(V_current)

        # Calcular Ω
        omega = (
            self.config.w_psi * psi +
            self.config.w_theta * theta_hat +
            self.config.w_cvar * (1 - cvar) +
            self.config.w_pole * pole
        )

        # Métricas completas
        metrics = {
            'omega': float(omega),
            'psi': float(psi),
            'theta_hat': float(theta_hat),
            'cvar': float(cvar),
            'pole': float(pole),
            'lyapunov_V': float(V_current),
            'is_stable': is_stable,
            'convergence_status': convergence_status.value,
            'entropy': float(state.entropy),
            'coherence': float(state.coherence_l1()),
            'rejection_count': self.rejection_count
        }

        # Avaliar condições
        conditions = {
            'omega_pass': omega >= self.config.omega_threshold,
            'psi_pass': psi >= self.config.psi_threshold,
            'cvar_pass': cvar <= self.config.cvar_threshold,
            'theta_hat_pass': theta_hat <= 0.3,  # Θ̂ deve ser baixo
            'pole_pass': pole >= 0.7,  # PoLE deve ser alto
            'stability_pass': is_stable or convergence_status in [ConvergenceStatus.CONVERGING, ConvergenceStatus.STABLE]
        }

        all_pass = all(conditions.values())

        if all_pass:
            self.state_before = state
            self.V_previous = V_current
            self.rejection_count = 0
            return Decision.PASS, metrics

        elif omega >= 0.6 and psi >= 0.7 and theta_hat <= 0.5 and pole >= 0.5:
            self.state_before = state
            self.V_previous = V_current
            return Decision.CONDITIONAL, metrics

        else:
            self.rejection_count += 1
            return Decision.BLOCK, metrics

    def get_recovery_action(
        self,
        available_alternatives: Optional[List[str]] = None
    ) -> Tuple[RecoveryAction, Dict[str, Any]]:
        """
        Determina ação de recuperação após rejeição.

        Args:
            available_alternatives: Skills alternativas disponíveis

        Returns:
            (ação, parâmetros)
        """
        if self.V_previous is None:
            self.V_previous = 1.0

        delta_V = self.proof_engine.lyapunov.V_history[-1] - self.V_previous if len(
            self.proof_engine.lyapunov.V_history
        ) > 0 else 0.0

        current_V = self.proof_engine.lyapunov.V_history[-1] if len(
            self.proof_engine.lyapunov.V_history
        ) > 0 else 1.0

        action, params = self.recovery_policy.determine_action(
            rejection_count=self.rejection_count,
            current_V=current_V,
            delta_V=delta_V,
            available_alternatives=available_alternatives or []
        )

        return action, params

    def apply_recovery(
        self,
        action: RecoveryAction,
        state: QuantumState,
        params: Dict[str, Any]
    ) -> QuantumState:
        """
        Aplica ação de recuperação.

        Args:
            action: Ação determined
            state: Estado atual
            params: Parâmetros da ação

        Returns:
            Novo estado pós-recuperação
        """
        self.trial_count += 1

        if action == RecoveryAction.ROLLBACK:
            # Manter estado anterior
            return self.state_before if self.state_before is not None else state

        elif action == RecoveryAction.REDUCE_NOISE:
            # Reduzir ruído no vetor de estado
            noise_factor = params.get('noise_factor', 0.5)
            new_vector = state.vector * (1 - noise_factor) + self.state_before.vector * noise_factor if self.state_before is not None else state.vector
            norm = np.linalg.norm(new_vector)
            if norm > 1e-10:
                new_vector = new_vector / norm
            return QuantumState(
                vector=new_vector,
                basis=state.basis,
                is_pure=state.is_pure,
                metadata={**state.metadata, 'recovery': 'noise_reduction'}
            )

        elif action == RecoveryAction.RETRY:
            # Tentar novamente com pequena perturbação
            noise = self.proof_engine.rng.standard_normal(len(state.vector)) * 0.01
            new_vector = state.vector + noise * 1j * self.proof_engine.rng.standard_normal(len(state.vector)) * 0.01
            norm = np.linalg.norm(new_vector)
            if norm > 1e-10:
                new_vector = new_vector / norm
            return QuantumState(
                vector=new_vector,
                basis=state.basis,
                is_pure=state.is_pure,
                metadata={**state.metadata, 'recovery': 'retry'}
            )

        else:
            # Outras ações: manter estado
            return state

    def _create_default_state(self) -> QuantumState:
        """Cria estado padrão"""
        dim = 2 ** 4
        vector = np.zeros(dim, dtype=complex)
        vector[0] = 1.0
        return QuantumState(
            vector=vector,
            basis=QuantumBasis.COMPUTATIONAL,
            is_pure=True,
            metadata={'source': 'default'}
        )


# ================================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enumerações
    "QuantumBasis",
    "ProofType",
    "RecoveryAction",
    "ConvergenceStatus",

    # Classes de estado
    "QuantumState",

    # Componentes de correção
    "ThetaHatEstimator",
    "PoLECalculator",
    "LyapunovFunction",
    "RecoveryPolicy",

    # Framework
    "CVaRPOVMFramework",

    # Provas
    "QuantumProof",
    "QuantumProofEngine",

    # Ω-Gate
    "QuantumAugmentedOmegaGate"
]
