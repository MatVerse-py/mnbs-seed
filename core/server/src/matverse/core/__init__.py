"""
MatVerse Core - Tipos e Interfaces Fundamentais
================================================================================
Fornece tipos base, interfaces e utilitários para toda a arquitetura.

Autor: MiniMax Agent
================================================================================
"""

from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Protocol, runtime_checkable
from enum import Enum
from abc import ABC, abstractmethod


# ================================================================================
# ENUMERAÇÕES
# ================================================================================

class HashTypes(str, Enum):
    """Tipos de hash suportados"""
    SHA256 = "sha256"
    SHA3_256 = "sha3_256"
    BLAKE2B = "blake2b"


class Decision(str, Enum):
    """Decisões do Ω-Gate"""
    PASS = "PASS"
    BLOCK = "BLOCK"
    CONDITIONAL = "CONDITIONAL"
    PENDING = "PENDING"


class ProtocolVersion(str, Enum):
    """Versões do protocolo MatVerse"""
    V1_0 = "1.0.0"
    OMEGA_PLUS = "Ω+"
    TENSOR_XAI = "tensor_xai"


# ================================================================================
# CONFIGURAÇÕES
# ================================================================================

@dataclass(frozen=True)
class ProtocolConfig:
    """Configuração do protocolo MatVerse"""
    # Limiares do Ω-Gate
    omega_threshold: float = 0.8
    psi_threshold: float = 0.85
    cvar_threshold: float = 0.05

    # Pesos da fórmula Ω
    w_psi: float = 0.4
    w_theta: float = 0.3
    w_cvar: float = 0.2
    w_pole: float = 0.1

    # Hash
    hash_type: HashTypes = HashTypes.SHA3_256

    # Ledger
    merkle_enabled: bool = True
    genesis_timestamp: Optional[float] = None

    def __post_init__(self):
        if self.genesis_timestamp is None:
            object.__setattr__(self, 'genesis_timestamp', time.time())


# Configuração padrão
DEFAULT_CONFIG = ProtocolConfig()


# ================================================================================
# INTERFACES (Protocol)
# ================================================================================

@runtime_checkable
class LedgerEntry(Protocol):
    """Interface para entradas do ledger"""
    @property
    def entry_id(self) -> str: ...
    @property
    def hash(self) -> str: ...
    @property
    def prev_hash(self) -> str: ...
    @property
    def timestamp(self) -> float: ...
    def to_dict(self) -> Dict[str, Any]: ...


@runtime_checkable
class GenesisArtifact(Protocol):
    """Interface para artefatos de gênese"""
    @property
    def ohash(self) -> str: ...
    @property
    def genesis_time(self) -> float: ...
    @property
    def policy_hash(self) -> str: ...


@runtime_checkable
class OmegaGateInterface(Protocol):
    """Interface para implementação de Ω-Gate"""
    def evaluate(self, state: Dict[str, Any]) -> Tuple[Decision, Dict[str, float]]: ...
    def get_metrics(self) -> Dict[str, float]: ...


# ================================================================================
# CLASSES ABSTRATAS
# ================================================================================

class BaseGenesisArtifact(ABC):
    """Classe base para artefatos de gênese"""

    @abstractmethod
    def compute_ohash(self) -> str:
        """Computa hash de identidade (Ohash)"""
        pass

    @abstractmethod
    def compute_policy_hash(self) -> str:
        """Computa hash da política"""
        pass


# ================================================================================
# UTILITÁRIOS DE HASH
# ================================================================================

def hash_sha256(data: str | Dict[str, Any]) -> str:
    """Gera hash SHA-256"""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()


def hash_sha3_256(data: str | Dict[str, Any]) -> str:
    """Gera hash SHA3-256"""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha3_256(data.encode()).hexdigest()


def hash_blake2b(data: str | Dict[str, Any]) -> str:
    """Gera hash BLAKE2b"""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    return hashlib.blake2b(data.encode()).hexdigest()


def compute_hash(data: str | Dict[str, Any], hash_type: HashTypes = HashTypes.SHA3_256) -> str:
    """Computa hash com tipo especificado"""
    hashers = {
        HashTypes.SHA256: hash_sha256,
        HashTypes.SHA3_256: hash_sha3_256,
        HashTypes.BLAKE2B: hash_blake2b
    }
    return hashers[hash_type](data)


# ================================================================================
# MERKLE TREE UTILITIES
# ================================================================================

def merkle_root(data_list: List[str]) -> str:
    """
    Calcula raiz Merkle de lista de strings.

    Args:
        data_list: Lista de strings para calcular hashes

    Returns:
        Raiz Merkle (hash)
    """
    if not data_list:
        return ""

    # Calcula hashes das folhas
    hashes = [hash_sha256(d) for d in data_list]

    # Se número ímpar, duplica última folha
    if len(hashes) % 2 == 1:
        hashes.append(hashes[-1])

    # Constrói árvore
    while len(hashes) > 1:
        next_level = []
        for i in range(0, len(hashes), 2):
            left = hashes[i]
            right = hashes[i + 1]
            combined = left + right
            next_level.append(hash_sha256(combined))
        hashes = next_level

        # Garante número par de nós
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])

    return hashes[0]


def verify_merkle_proof(data: str, proof: List[str], root: str) -> bool:
    """
    Verifica prova Merkle.

    Args:
        data: Dado original
        proof: Lista de hashes de verificação
        root: Raiz Merkle esperada

    Returns:
        True se prova é válida
    """
    current_hash = hash_sha256(data)

    for sibling_hash in proof:
        # Combina com irmão
        current_hash = hash_sha256(current_hash + sibling_hash)

    return current_hash == root


# ================================================================================
# RESULTADO CANÔNICO
# ================================================================================

@dataclass
class CanonicalResult:
    """
    RESULTADO canônico do sistema.

    Fórmula:
    RESULTADO := ⟨Ohash, policy_hash, data_hash, merkle_root⟩ + LedgerHead(R_t)
    """
    Ohash: str
    policy_hash: str
    data_hash: str
    merkle_root: str
    ledger_head: Optional[Dict[str, Any]] = None
    total_entries: int = 0
    genesis_timestamp: Optional[float] = None
    last_timestamp: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'Ohash': self.Ohash,
            'policy_hash': self.policy_hash,
            'data_hash': self.data_hash,
            'merkle_root': self.merkle_root,
            'LedgerHead': self.ledger_head,
            'total_entries': self.total_entries,
            'genesis_timestamp': self.genesis_timestamp,
            'last_timestamp': self.last_timestamp
        }

    def verify(self) -> Tuple[bool, List[str]]:
        """Verifica integridade do resultado"""
        errors = []

        if not self.Ohash:
            errors.append("Ohash não definido")
        if not self.policy_hash:
            errors.append("policy_hash não definido")
        if not self.data_hash:
            errors.append("data_hash não definido")
        if not self.merkle_root:
            errors.append("merkle_root não definido")

        return len(errors) == 0, errors


# ================================================================================
# FACTORY
# ================================================================================

class HashFactory:
    """Fábrica de funções de hash"""

    @staticmethod
    def create(hasher_type: HashTypes = HashTypes.SHA3_256):
        """Cria função de hash"""
        return lambda data: compute_hash(data, hasher_type)


# ================================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enumerações
    "HashTypes",
    "Decision",
    "ProtocolVersion",

    # Configurações
    "ProtocolConfig",
    "DEFAULT_CONFIG",

    # Interfaces
    "LedgerEntry",
    "GenesisArtifact",
    "OmegaGateInterface",

    # Classes base
    "BaseGenesisArtifact",
    "CanonicalResult",

    # Utilitários
    "hash_sha256",
    "hash_sha3_256",
    "hash_blake2b",
    "compute_hash",
    "merkle_root",
    "verify_merkle_proof",
    "HashFactory"
]
