"""
Testes do MatVerse Monorepo
"""

import sys
sys.path.insert(0, '/workspace/extracted_matverse/matverse_monorepo/src')

from matverse.core import (
    hash_sha256, hash_sha3_256, merkle_root,
    Decision, ProtocolConfig
)
from matverse.quantum import (
    QuantumState, CVaRPOVMFramework,
    QuantumProofEngine, ProofType
)
from matverse.ledger import (
    TensorXAI7D, ImmutableLedger,
    LedgerFacade, SkillType
)
from matverse.motor import (
    StateMachine, MotorState, EventType,
    ConversionMotor
)
from matverse.skills import (
    SkillRegistry, RepoDiscoverySkill
)


def test_hash_functions():
    """Testa funções de hash"""
    data = {"test": "value"}
    h1 = hash_sha256(data)
    h2 = hash_sha3_256(data)
    assert len(h1) == 64
    assert len(h2) == 64
    print("✓ Hash functions")


def test_merkle_root():
    """Testa raiz Merkle"""
    data = ["a", "b", "c", "d"]
    root = merkle_root(data)
    assert len(root) == 64
    print("✓ Merkle root")


def test_tensor_xai():
    """Testa Tensor XAI 7D"""
    tensor = TensorXAI7D(
        A=0.88, T=0.84, C=0.80, E=0.83,
        N=0.82, S=0.86, PSI=0.83
    )
    assert hasattr(tensor, 'hash')
    assert 0.7 < tensor.compute_coherence() < 0.8
    assert 0.3 < tensor.compute_policy_score() < 0.5
    print("✓ Tensor XAI 7D")


def test_quantum_state():
    """Testa estado quântico"""
    import numpy as np
    vector = np.array([1.0, 0.0], dtype=complex)
    state = QuantumState(vector=vector)
    assert state.dimension == 2
    assert state.entropy == 0.0  # Estado puro
    print("✓ Quantum state")


def test_cvar_povm():
    """Testa framework CVaR-POVM"""
    framework = CVaRPOVMFramework(alpha=0.95, n_qubits=2)
    assert framework.dimension == 4
    print("✓ CVaR-POVM framework")


def test_quantum_proofs():
    """Testa motor de provas quânticas"""
    engine = QuantumProofEngine()
    state = engine.create_state(n_qubits=2)
    proofs = engine.generate_all_proofs(state)
    assert len(proofs) >= 3
    print("✓ Quantum proofs engine")


def test_state_machine():
    """Testa máquina de estados"""
    sm = StateMachine()
    assert sm.current_state == MotorState.GENESIS

    success, _ = sm.transition(EventType.ADVANCE, "guard", "action")
    assert success
    assert sm.current_state == MotorState.PRIMORDIAL
    print("✓ State machine")


def test_conversion_motor():
    """Testa motor de conversão"""
    motor = ConversionMotor()
    success, result = motor.process_event(
        EventType.PROCESS,
        {"psi": 0.9, "cvar": 0.02}
    )
    assert success
    print("✓ Conversion motor")


def test_ledger():
    """Testa ledger imutável"""
    ledger = ImmutableLedger("test_ledger")
    initial_count = len(ledger.trilhas)

    from matverse.core import Decision
    tensor = TensorXAI7D(
        A=0.88, T=0.84, C=0.80, E=0.83,
        N=0.82, S=0.86, PSI=0.83
    )
    ledger.add_trilha(
        tensor=tensor,
        decision=Decision.PASS,
        skill=SkillType.REPO_DISCOVERY
    )

    assert len(ledger.trilhas) == initial_count + 1
    valid, _ = ledger.verify_chain()
    assert valid
    print("✓ Immutable ledger")


def test_ledger_facade():
    """Testa facade do ledger"""
    facade = LedgerFacade("test_facade")
    result = facade.record_tensor(
        A=0.88, T=0.84, C=0.80, E=0.83,
        N=0.82, S=0.86, PSI=0.83,
        skill=SkillType.PR_REVIEW
    )
    assert result['decision'] == 'PASS'
    print("✓ Ledger facade")


def test_skills():
    """Testa skills"""
    skill = RepoDiscoverySkill()
    result = skill.execute({})
    assert result['skill'] == 'repo_discovery'
    assert 'objective' in result
    print("✓ Skills operators")


def test_skill_registry():
    """Testa registro de skills"""
    skills = SkillRegistry.get_all()
    assert len(skills) >= 5
    print("✓ Skill registry")


def test_resultado_canonico():
    """Testa resultado canônico"""
    facade = LedgerFacade("test_resultado")
    facade.record_tensor(
        A=0.88, T=0.84, C=0.80, E=0.83,
        N=0.82, S=0.86, PSI=0.83
    )
    resultado = facade.get_resultado()
    assert 'Ohash' in resultado
    assert 'merkle_root' in resultado
    print("✓ Resultado canônico")


if __name__ == "__main__":
    print("=" * 50)
    print("MatVerse Monorepo - Testes")
    print("=" * 50)

    tests = [
        test_hash_functions,
        test_merkle_root,
        test_tensor_xai,
        test_quantum_state,
        test_cvar_povm,
        test_quantum_proofs,
        test_state_machine,
        test_conversion_motor,
        test_ledger,
        test_ledger_facade,
        test_skills,
        test_skill_registry,
        test_resultado_canonico
    ]

    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")

    print("=" * 50)
    print(f"Resultados: {passed}/{len(tests)} testes passados")
    print("=" * 50)
