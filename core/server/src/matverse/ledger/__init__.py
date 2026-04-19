"""
MatVerse Ledger - Ledger Imutável com Tensor XAI 7D
================================================================================
Implementação do ledger com:
- Tensor XAI 7D: A, T, C, E, N, S, Ψ
- Merkle Tree para verificação
- Skills Operadoras
- RESULTADO canônico

Autor: MiniMax Agent
================================================================================
"""

from __future__ import annotations
import hashlib
import json
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum

from ..core import (
    Decision,
    ProtocolConfig,
    hash_sha256,
    hash_sha3_256,
    merkle_root,
    verify_merkle_proof,
    CanonicalResult
)


# ================================================================================
# ENUMERAÇÕES
# ================================================================================

class SkillType(str, Enum):
    """Tipos de Skills Operadoras"""
    REPO_DISCOVERY = "repo_discovery"
    CODE_NAVIGATION = "code_navigation"
    PR_REVIEW = "pr_review"
    ISSUE_MANAGEMENT = "issue_management"
    ENGINEERING_COPILOT = "engineering_copilot"
    SETUP_ORGANIZATION = "setup_organization"


class TensorClassification(str, Enum):
    """Classificação H/M/L"""
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"


# ================================================================================
# TENSOR XAI 7D
# ================================================================================

@dataclass
class TensorXAI7D:
    """
    Tensor 7-Dimensional para Explicabilidade XAI.

    Dimensões:
    - A (Accuracy): Precisão do modelo [0.0, 1.0]
    - T (Truthfulness): Veracidade [0.0, 1.0]
    - C (Completeness): Completude [0.0, 1.0]
    - E (Explainability): Explicabilidade [0.0, 1.0]
    - N (Novelty): Novidade [0.0, 1.0]
    - S (Stability): Estabilidade [0.0, 1.0]
    - Ψ (Coherence): Coerência [0.0, 1.0]
    """
    # Valores normalizados
    A: float = 0.0
    T: float = 0.0
    C: float = 0.0
    E: float = 0.0
    N: float = 0.0
    S: float = 0.0
    PSI: float = 0.0

    # Desvios
    sigma_A: float = 0.05
    sigma_T: float = 0.07
    sigma_C: float = 0.10
    sigma_E: float = 0.07
    sigma_N: float = 0.06
    sigma_S: float = 0.06
    sigma_PSI: float = 0.09

    @property
    def classification(self) -> Dict[str, TensorClassification]:
        """Classifica cada dimensão H/M/L"""
        result = {}
        dims = {
            'A': self.A, 'T': self.T, 'C': self.C, 'E': self.E,
            'N': self.N, 'S': self.S, 'PSI': self.PSI
        }
        for dim, val in dims.items():
            if val >= 0.85:
                result[dim] = TensorClassification.HIGH
            elif val >= 0.5:
                result[dim] = TensorClassification.MEDIUM
            else:
                result[dim] = TensorClassification.LOW
        return result

    def compute_coherence(self) -> float:
        """Ψ = média ponderada das dimensões"""
        weights = {
            'A': 0.20, 'T': 0.20, 'C': 0.15, 'E': 0.15,
            'N': 0.10, 'S': 0.10
        }
        return sum(w * getattr(self, d) for d, w in weights.items())

    def compute_policy_score(self) -> float:
        """Xi = 0.40·T + 0.30·PSI + 0.30·S"""
        return 0.40 * self.T + 0.30 * self.PSI + 0.30 * self.S

    def compute_cvar(self, alpha: float = 0.95) -> float:
        """CVaR-α: média das α piores dimensões"""
        values = [self.A, self.T, self.C, self.E, self.N, self.S, self.PSI]
        sorted_vals = sorted(values)
        cutoff_idx = int(len(sorted_vals) * (1 - alpha))
        return float(np.mean(sorted_vals[:cutoff_idx + 1]))

    def hash(self) -> str:
        """Hash SHA-256 do tensor"""
        data = {
            'A': self.A, 'T': self.T, 'C': self.C, 'E': self.E,
            'N': self.N, 'S': self.S, 'PSI': self.PSI,
            'sigma': [
                self.sigma_A, self.sigma_T, self.sigma_C,
                self.sigma_E, self.sigma_N, self.sigma_S, self.sigma_PSI
            ]
        }
        return hash_sha256(json.dumps(data, sort_keys=True))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tensor': {
                'A': self.A, 'T': self.T, 'C': self.C,
                'E': self.E, 'N': self.N, 'S': self.S, 'PSI': self.PSI
            },
            'sigma': {
                'A': self.sigma_A, 'T': self.sigma_T, 'C': self.sigma_C,
                'E': self.sigma_E, 'N': self.sigma_N, 'S': self.sigma_S,
                'PSI': self.sigma_PSI
            },
            'classification': {k: v.value for k, v in self.classification.items()},
            'hash': self.hash()
        }


# ================================================================================
# SKILLS OPERADORAS
# ================================================================================

@dataclass
class SkillAction:
    """Ação de skill"""
    name: str
    description: str
    enabled: bool = True


@dataclass
class SkillOperator:
    """Operador de skill genérico"""
    skill_type: SkillType
    name: str
    description: str
    actions: List[SkillAction] = field(default_factory=list)
    enabled: bool = True

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'skill': self.skill_type.value,
            'status': 'implemented',
            'actions': [a.name for a in self.actions if a.enabled]
        }


# Skills pré-definidas
def get_repo_discovery_skill() -> SkillOperator:
    return SkillOperator(
        skill_type=SkillType.REPO_DISCOVERY,
        name="Repo Discovery",
        description="Mapear contexto de repositórios GitHub",
        actions=[
            SkillAction("check_repo_initialized", "Verificar se repo existe"),
            SkillAction("get_repo", "Obter metadados do repo"),
            SkillAction("search_branches", "Buscar branches"),
            SkillAction("fetch_commit", "Obter commit"),
        ]
    )


def get_pr_review_skill() -> SkillOperator:
    return SkillOperator(
        skill_type=SkillType.PR_REVIEW,
        name="PR Review",
        description="Revisão de Pull Requests",
        actions=[
            SkillAction("get_pr_info", "Obter info do PR"),
            SkillAction("get_pr_diff", "Obter diff"),
            SkillAction("fetch_pr_comments", "Obter comentários"),
        ]
    )


# ================================================================================
# TRILHA
# ================================================================================

@dataclass
class Trilha:
    """
    Trilha: Unidade atômica do ledger.

    Campos:
    - trilha_id: Identificador único
    - timestamp: Momento de criação
    - tensor: Tensor XAI 7D
    - decision: Decisão do Ω-Gate
    - skill: Skill usada
    - prev_hash: Hash da trilha anterior
    - hash: Hash desta trilha
    """
    trilha_id: str
    timestamp: float
    tensor: TensorXAI7D
    decision: Decision
    skill_used: Optional[SkillType]
    prev_hash: str
    hash: str
    omega_metrics: Dict[str, float] = field(default_factory=dict)
    merkle_proof: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        tensor: TensorXAI7D,
        decision: Decision,
        skill: Optional[SkillType],
        prev_hash: str,
        omega_metrics: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'Trilha':
        """Factory para criar trilha"""
        trilha_id = f"TRILHA_{int(time.time()*1000)}"
        timestamp = time.time()

        # Calcula hash
        hash_data = {
            'trilha_id': trilha_id,
            'timestamp': timestamp,
            'tensor_hash': tensor.hash(),
            'decision': decision.value,
            'skill': skill.value if skill else None,
            'prev_hash': prev_hash
        }
        hash_value = hash_sha3_256(json.dumps(hash_data, sort_keys=True))

        return cls(
            trilha_id=trilha_id,
            timestamp=timestamp,
            tensor=tensor,
            decision=decision,
            skill_used=skill,
            prev_hash=prev_hash,
            hash=hash_value,
            omega_metrics=omega_metrics,
            metadata=metadata or {}
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'trilha_id': self.trilha_id,
            'timestamp': self.timestamp,
            'tensor': self.tensor.to_dict(),
            'decision': self.decision.value,
            'skill_used': self.skill_used.value if self.skill_used else None,
            'prev_hash': self.prev_hash,
            'hash': self.hash,
            'omega_metrics': self.omega_metrics,
            'merkle_proof': self.merkle_proof,
            'metadata': self.metadata
        }


# ================================================================================
# MERKLE TREE
# ================================================================================

class MerkleTree:
    """Árvore Merkle para verificação de integridade"""

    def __init__(self):
        self.leaves: List[str] = []
        self.root: str = ""

    def build(self, data_list: List[str]) -> str:
        """Constrói árvore"""
        if not data_list:
            self.root = ""
            return ""

        self.leaves = [hash_sha256(d) for d in data_list]

        if len(self.leaves) % 2 == 1:
            self.leaves.append(self.leaves[-1])

        current = self.leaves[:]
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1]
                combined = left + right
                next_level.append(hash_sha256(combined))
            current = next_level
            if len(current) % 2 == 1:
                current.append(current[-1])

        self.root = current[0]
        return self.root

    def add_leaf(self, data: str) -> str:
        """Adiciona folha"""
        self.leaves.append(hash_sha256(data))
        return self.build([str(l) for l in self.leaves])

    def get_root(self) -> str:
        return self.root


# ================================================================================
# LEDGER IMUTÁVEL
# ================================================================================

class ImmutableLedger:
    """
    Ledger Imutável com Tensor XAI 7D.

    Invariantes:
    - h_i = SHA3-256(h_{i-1} || trilha_i)
    - Replay(L) = L
    - LedgerHead(R_t) = MerkleRoot
    """

    def __init__(self, name: str = "matverse_ledger"):
        self.name = name
        self.trilhas: List[Trilha] = []
        self.merkle_tree = MerkleTree()
        self.skills: Dict[SkillType, SkillOperator] = {
            SkillType.REPO_DISCOVERY: get_repo_discovery_skill(),
            SkillType.PR_REVIEW: get_pr_review_skill(),
        }
        self._create_genesis()

    def _create_genesis(self):
        """Cria bloco gênese"""
        genesis_tensor = TensorXAI7D(
            A=1.0, T=1.0, C=1.0, E=1.0,
            N=0.0, S=1.0, PSI=1.0
        )

        genesis = Trilha.create(
            tensor=genesis_tensor,
            decision=Decision.PASS,
            skill=None,
            prev_hash="GENESIS",
            omega_metrics={'genesis': True},
            metadata={'type': 'genesis'}
        )

        self.trilhas.append(genesis)
        self.merkle_tree.add_leaf(genesis.hash)

    def add_trilha(
        self,
        tensor: TensorXAI7D,
        decision: Decision,
        skill: Optional[SkillType] = None,
        omega_metrics: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Trilha:
        """Adiciona trilha ao ledger"""
        prev_hash = self.trilhas[-1].hash if self.trilhas else "GENESIS"

        trilha = Trilha.create(
            tensor=tensor,
            decision=decision,
            skill=skill,
            prev_hash=prev_hash,
            omega_metrics=omega_metrics or {},
            metadata=metadata
        )

        self.trilhas.append(trilha)
        self.merkle_tree.add_leaf(trilha.hash)

        return trilha

    def verify_chain(self) -> Tuple[bool, List[str]]:
        """Verifica integridade da cadeia"""
        errors = []

        for i in range(1, len(self.trilhas)):
            if self.trilhas[i].prev_hash != self.trilhas[i-1].hash:
                errors.append(f"Cadeia quebrada no índice {i}")

        return len(errors) == 0, errors

    def get_resultado(self) -> CanonicalResult:
        """Retorna RESULTADO canônico"""
        if not self.trilhas:
            return CanonicalResult(
                Ohash="", policy_hash="", data_hash="", merkle_root=""
            )

        ohash = hash_sha3_256(
            (self.name + str(self.trilhas[0].timestamp)).encode()
        )

        policy_data = {
            'omega_threshold': 0.8,
            'psi_threshold': 0.85,
            'cvar_threshold': 0.05
        }
        policy_hash = hash_sha256(json.dumps(policy_data, sort_keys=True))

        tensor_hashes = [t.tensor.hash() for t in self.trilhas]
        data_hash = hash_sha256(json.dumps(tensor_hashes, sort_keys=True))

        return CanonicalResult(
            Ohash=ohash,
            policy_hash=policy_hash,
            data_hash=data_hash,
            merkle_root=self.merkle_tree.get_root(),
            ledger_head=self.trilhas[-1].to_dict(),
            total_entries=len(self.trilhas),
            genesis_timestamp=self.trilhas[0].timestamp,
            last_timestamp=self.trilhas[-1].timestamp
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Estatísticas do ledger"""
        decisions = {}
        for t in self.trilhas:
            d = t.decision.value
            decisions[d] = decisions.get(d, 0) + 1

        return {
            'total_trilhas': len(self.trilhas),
            'decisions': decisions,
            'pass_rate': decisions.get('PASS', 0) / len(self.trilhas)
                        if self.trilhas else 0,
            'merkle_root': self.merkle_tree.get_root()[:32] + "...",
            'genesis': self.trilhas[0].hash[:16] + "..." if self.trilhas else None
        }


# ================================================================================
# FACADE
# ================================================================================

class LedgerFacade:
    """Fachada simplificada para o ledger"""

    def __init__(self, name: str = "tensor_xai_ledger"):
        self.ledger = ImmutableLedger(name)

    def record_tensor(
        self,
        A: float, T: float, C: float, E: float,
        N: float, S: float, PSI: float,
        skill: Optional[SkillType] = None,
        decision: Decision = Decision.PASS,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Registra tensor XAI 7D"""
        tensor = TensorXAI7D(A=A, T=T, C=C, E=E, N=N, S=S, PSI=PSI)
        trilha = self.ledger.add_trilha(
            tensor=tensor,
            decision=decision,
            skill=skill,
            omega_metrics={'psi': tensor.compute_coherence()},
            metadata=metadata
        )
        return trilha.to_dict()

    def verify(self) -> Dict[str, Any]:
        """Verifica integridade"""
        valid, errors = self.ledger.verify_chain()
        return {
            'valid': valid,
            'errors': errors,
            'merkle_root': self.ledger.merkle_tree.get_root()
        }

    def get_resultado(self) -> Dict[str, Any]:
        """Resultado canônico"""
        return self.ledger.get_resultado().to_dict()

    def get_stats(self) -> Dict[str, Any]:
        """Estatísticas"""
        return self.ledger.get_statistics()


# ================================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enumerações
    "SkillType",
    "TensorClassification",

    # Tensor
    "TensorXAI7D",

    # Skills
    "SkillAction",
    "SkillOperator",

    # Trilha
    "Trilha",

    # Merkle
    "MerkleTree",

    # Ledger
    "ImmutableLedger",
    "LedgerFacade"
]
