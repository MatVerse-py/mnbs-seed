# MatVerse Monorepo - Arquitetura Consolidada

**Versão:** 1.0.0
**Protocolo:** MatVerse-Ω+ com Tensor XAI 7D

---

## Visão Geral

Este monorepo consolida a arquitetura MatVerse com os seguintes módulos:

| Módulo | Descrição |
|--------|-----------|
| `matverse.core` | Tipos, interfaces e utilitários fundamentais |
| `matverse.quantum` | Framework quântico CVaR-POVM com Ω-Gate |
| `matverse.ledger` | Ledger imutável com Tensor XAI 7D |
| `matverse.motor` | Motor de conversão de estados |
| `matverse.skills` | Skills operadoras para GitHub Actions |

---

## Arquitetura Formal

### Invariantes do Sistema

```
h_i = SHA3-256(h_{i-1} || trilha_i)
RESULTADO := ⟨Ohash, policy_hash, data_hash, merkle_root⟩ + LedgerHead(R_t)
Replay(L) = L (idempotência)
```

### Fórmula Ω-Gate

```
Ω = 0.4·Ψ + 0.3·Θ̂ + 0.2·(1−CVaR) + 0.1·PoLE

PASS ⟺ Ω ≥ 0.8 ∧ Ψ ≥ 0.85 ∧ CVaR ≤ 0.05
```

### Tensor XAI 7D

| Dimensão | Descrição | Limiar H |
|----------|-----------|----------|
| A | Accuracy (Precisão) | ≥0.85 |
| T | Truthfulness (Veracidade) | ≥0.85 |
| C | Completeness (Completude) | ≥0.85 |
| E | Explainability (Explicabilidade) | ≥0.85 |
| N | Novelty (Novidade) | ≥0.85 |
| S | Stability (Estabilidade) | ≥0.85 |
| Ψ | Coherence (Coerência) | ≥0.85 |

---

## Instalação

```bash
# Clonar repositório
git clone <repo>
cd matverse_monorepo

# Instalar dependências
pip install numpy pydantic cryptography

# Ou com Poetry
poetry install
```

---

## Uso Rápido

### Ledger com Tensor XAI 7D

```python
from matverse.ledger import LedgerFacade, SkillType, TensorXAI7D

# Cria facade
ledger = LedgerFacade("meu_ledger")

# Registra tensor
result = ledger.record_tensor(
    A=0.88, T=0.84, C=0.80, E=0.83,
    N=0.82, S=0.86, PSI=0.83,
    skill=SkillType.REPO_DISCOVERY
)

print(f"Trilha: {result['trilha_id']}")
print(f"Decisão: {result['decision']}")

# Verifica integridade
verify = ledger.verify()
print(f"Válido: {verify['valid']}")

# Obtém resultado canônico
resultado = ledger.get_resultado()
print(f"Ohash: {resultado['Ohash'][:32]}...")
```

### Framework Quântico CVaR-POVM

```python
from matverse.quantum import (
    QuantumProofEngine,
    QuantumState,
    QuantumBasis
)

# Cria motor de provas
engine = QuantumProofEngine()

# Cria estado quântico
state = engine.create_state(n_qubits=4)

# Gera provas
proofs = engine.generate_all_proofs(state)

for proof in proofs:
    print(f"{proof.proof_type.value}: {proof.value:.4f} (holds={proof.holds})")
```

### Motor de Conversão de Estados

```python
from matverse.motor import (
    ConversionMotor,
    StateMachine,
    EventType
)

# Cria motor
motor = ConversionMotor()

# Processa evento
success, result = motor.process_event(
    EventType.ADVANCE,
    {'psi': 0.9, 'cvar': 0.02}
)

print(f"Estado: {motor.state_machine.current_state.value}")
print(f"Progresso: {motor.state_machine.progress_percentage():.1f}%")
```

---

## Estrutura do Projeto

```
matverse_monorepo/
├── src/matverse/
│   ├── __init__.py          # Módulo principal
│   ├── core/                # Tipos e interfaces
│   │   └── __init__.py
│   ├── quantum/             # Framework quântico
│   │   └── __init__.py
│   ├── ledger/              # Ledger imutável
│   │   └── __init__.py
│   ├── motor/               # Motor de estados
│   │   └── __init__.py
│   └── skills/              # Skills GitHub
│       └── __init__.py
├── tests/                   # Testes
├── docs/                    # Documentação
├── scripts/                 # Scripts utilitários
├── config/                  # Configurações
├── pyproject.toml          # Configuração Poetry
└── README.md               # Este arquivo
```

---

## Skills Operadoras (GitHub Actions)

| Skill | Ações | Objetivo |
|-------|-------|----------|
| `RepoDiscovery` | `check_repo_initialized`, `get_repo`, `search_branches` | Mapear contexto de repositórios |
| `CodeNavigation` | `search`, `fetch_file`, `fetch_blob` | Navegar e compreender código |
| `PRReview` | `get_pr_info`, `get_pr_diff`, `fetch_pr_comments` | Revisão de PRs e análise de risco |
| `IssueManagement` | `list_recent_issues`, `fetch_issue`, `search_issues` | Triagem e priorização |
| `EngineeringCopilot` | `get_users_recent_prs`, `get_profile` | Copiloto de engenharia pessoal |
| `SetupOrganization` | `list_repositories`, `get_repo_collaborator_permission` | Mapear ecossistema |

---

## RESULTADO Canônico

```python
{
    'Ohash': '<hash de identidade>',
    'policy_hash': '<hash da política Ω-Gate>',
    'data_hash': '<hash dos tensores>',
    'merkle_root': '<raiz Merkle>',
    'LedgerHead': '<última trilha>',
    'total_entries': <número de trilhas>,
    'genesis_timestamp': <timestamp gênese>,
    'last_timestamp': <timestamp última trilha>
}
```

---

## Configuração

```python
from matverse.core import ProtocolConfig

config = ProtocolConfig(
    omega_threshold=0.8,    # Limiar Ω
    psi_threshold=0.85,     # Limiar Ψ
    cvar_threshold=0.05,     # Limiar CVaR
    w_psi=0.4,              # Peso Ψ
    w_theta=0.3,            # Peso Θ̂
    w_cvar=0.2,             # Peso CVaR
    w_pole=0.1              # Peso PoLE
)
```

---

## Testes

```bash
# Executar testes
pytest tests/

# Com cobertura
pytest tests/ --cov=src/matverse
```

---

## Referências

- **MatVerse Protocol**: Sistema de governança com Ω-Gate fail-closed
- **CVaR-POVM**: Conditional Value at Risk como medição quântica
- **Tensor XAI 7D**: Framework de explicabilidade multidimensional
- **Merkle Tree**: Verificação de integridade por árvore hash
- **Skills UMJAM**: Operadores GitHub Actions

---

**Autor:** MiniMax Agent
**Licença:** MIT
