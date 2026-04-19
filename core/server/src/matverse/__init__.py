"""
MatVerse Monorepo - Módulo Principal
================================================================================
Arquitetura consolidada:
- MatVerse-Ω+: Framework quântico com CVaR-POVM
- Tensor XAI 7D: Explicabilidade multidimensional
- Ledger Imutável: Integridade com Merkle
- Skills Operadoras: GitHub Actions
- Motor de Estados: PRIMORDIAL→SVCA→MNB→MOTOR→LEDGER

Autor: MiniMax Agent
Versão: 1.0.0
================================================================================
"""

from .core import (
    # Tipos base
    HashTypes,
    Decision,
    ProtocolVersion,

    # Interfaces
    LedgerEntry,
    GenesisArtifact,
    OmegaGateInterface,

    # Utilitários
    hash_sha256,
    hash_sha3_256,
    merkle_root,
    verify_merkle_proof,

    # Configurações
    DEFAULT_CONFIG,
    ProtocolConfig
)

__version__ = "1.0.0"
__all__ = [
    "HashTypes",
    "Decision",
    "ProtocolVersion",
    "LedgerEntry",
    "GenesisArtifact",
    "OmegaGateInterface",
    "hash_sha256",
    "hash_sha3_256",
    "merkle_root",
    "verify_merkle_proof",
    "DEFAULT_CONFIG",
    "ProtocolConfig"
]
