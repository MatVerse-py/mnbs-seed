"""
MatVerse Motor - Motor de Conversão e Troca de Estados
================================================================================
Pipeline: PRIMORDIAL → SVCA → MNB → MOTOR → LEDGER

Autor: MiniMax Agent
================================================================================
"""

from __future__ import annotations
import time
import copy
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum

from ..core import Decision


# ================================================================================
# ENUMERAÇÕES
# ================================================================================

class MotorState(str, Enum):
    """Estados do motor de conversão"""
    GENESIS = "GENESIS"
    PRIMORDIAL = "PRIMORDIAL"
    SVCA = "SVCA"
    MNB = "MNB"
    MOTOR = "MOTOR"
    LEDGER = "LEDGER"
    ARCHIVED = "ARCHIVED"


class EventType(str, Enum):
    """Tipos de eventos"""
    ADVANCE = "ADVANCE"
    ARCHIVE = "ARCHIVE"
    RESET = "RESET"
    PROCESS = "PROCESS"
    VALIDATE = "VALIDATE"


# ================================================================================
# TRANSIÇÃO DE ESTADO
# ================================================================================

@dataclass
class StateTransition:
    """Transição de estado"""
    from_state: MotorState
    to_state: MotorState
    event: EventType
    guard: str
    action: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ================================================================================
# MÁQUINA DE ESTADOS
# ================================================================================

class StateMachine:
    """
    Máquina de estados para o motor de conversão.

    Pipeline: PRIMORDIAL → SVCA → MNB → MOTOR → LEDGER

    Características:
    - Determinística
    - Auditável
    - Revertível (até certo ponto)
    """

    # Ordem dos estados
    STATE_ORDER = [
        MotorState.GENESIS,
        MotorState.PRIMORDIAL,
        MotorState.SVCA,
        MotorState.MNB,
        MotorState.MOTOR,
        MotorState.LEDGER
    ]

    def __init__(self, initial_state: MotorState = MotorState.GENESIS):
        self.current_state = initial_state
        self.transitions: List[StateTransition] = []
        self.history: List[MotorState] = [initial_state]
        self._hooks: Dict[str, List[Callable]] = {
            'on_enter': [],
            'on_exit': [],
            'on_transition': []
        }

    def transition(
        self,
        event: EventType,
        guard: str = "true",
        action: str = ""
    ) -> Tuple[bool, Optional[MotorState]]:
        """
        Executa transição de estado.

        Args:
            event: Evento que dispara
            guard: Condição de guarda
            action: Ação a executar

        Returns:
            (sucesso, próximo_estado)
        """
        from_state = self.current_state
        to_state = self._compute_next_state(event)

        if to_state is None:
            return False, None

        # Executa transição
        transition = StateTransition(
            from_state=from_state,
            to_state=to_state,
            event=event,
            guard=guard,
            action=action
        )

        # Hooks
        for hook in self._hooks['on_exit']:
            hook(from_state)

        self.transitions.append(transition)
        self.current_state = to_state
        self.history.append(to_state)

        for hook in self._hooks['on_enter']:
            hook(to_state)

        return True, to_state

    def _compute_next_state(self, event: EventType) -> Optional[MotorState]:
        """Determina próximo estado"""
        if event == EventType.ARCHIVE:
            return MotorState.ARCHIVED
        elif event == EventType.RESET:
            return MotorState.GENESIS
        elif event == EventType.ADVANCE:
            try:
                idx = self.STATE_ORDER.index(self.current_state)
                if idx < len(self.STATE_ORDER) - 1:
                    return self.STATE_ORDER[idx + 1]
            except ValueError:
                pass

        return None

    def add_hook(
        self,
        hook_type: str,
        callback: Callable[[Any], None]
    ):
        """Adiciona hook de callback"""
        if hook_type in self._hooks:
            self._hooks[hook_type].append(callback)

    def get_history(self) -> List[MotorState]:
        """Retorna histórico de estados"""
        return copy.deepcopy(self.history)

    def can_transition(self, event: EventType) -> bool:
        """Verifica se transição é possível"""
        return self._compute_next_state(event) is not None

    def get_state_index(self) -> int:
        """Índice do estado atual"""
        try:
            return self.STATE_ORDER.index(self.current_state)
        except ValueError:
            return -1

    def progress_percentage(self) -> float:
        """Percentual de progresso no pipeline"""
        idx = self.get_state_index()
        if idx < 0:
            return 0.0
        return (idx / (len(self.STATE_ORDER) - 1)) * 100


# ================================================================================
# MOTOR DE CONVERSÃO
# ================================================================================

@dataclass
class MNBRecord:
    """Metrics Normalization Base"""
    event: str
    psi: float
    cvar: float
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConversionMotor:
    """
    Motor de conversão de estados.

    Responsabilidades:
    - Processar eventos
    - Normalizar métricas (MNB)
    - Aplicar Ω-Gate
    - Gerar transições
    """

    def __init__(self, state_machine: Optional[StateMachine] = None):
        self.state_machine = state_machine or StateMachine()
        self.mnb_records: List[MNBRecord] = []
        self.events_processed: int = 0

    def process_event(
        self,
        event: EventType,
        data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Processa evento.

        Args:
            event: Tipo de evento
            data: Dados do evento

        Returns:
            (sucesso, resultado)
        """
        self.events_processed += 1

        # Cria MNB
        mnb = MNBRecord(
            event=data.get('event', str(event)),
            psi=data.get('psi', 0.9),
            cvar=data.get('cvar', 0.02),
            timestamp=time.time(),
            metadata=data
        )
        self.mnb_records.append(mnb)

        # Determina guarda
        guard = "pass" if mnb.psi >= 0.85 and mnb.cvar <= 0.05 else "block"

        # Executa transição
        success, new_state = self.state_machine.transition(event, guard, str(event))

        return success, {
            'mnb': {
                'psi': mnb.psi,
                'cvar': mnb.cvar,
                'timestamp': mnb.timestamp
            },
            'previous_state': self.state_machine.history[-2].value
                             if len(self.state_machine.history) > 1 else None,
            'current_state': new_state.value if new_state else None,
            'guard': guard,
            'events_processed': self.events_processed
        }

    def create_mnb(
        self,
        event: str,
        psi: float,
        cvar: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MNBRecord:
        """Cria registro MNB"""
        record = MNBRecord(
            event=event,
            psi=max(psi, 0.0),
            cvar=max(cvar, 0.0),
            timestamp=time.time(),
            metadata=metadata or {}
        )
        self.mnb_records.append(record)
        return record

    def omega_gate(self, mnb: MNBRecord) -> Decision:
        """Avalia MNB no Ω-Gate"""
        if mnb.psi >= 0.85 and mnb.cvar <= 0.05:
            return Decision.PASS
        return Decision.BLOCK

    def get_statistics(self) -> Dict[str, Any]:
        """Estatísticas do motor"""
        return {
            'events_processed': self.events_processed,
            'mnb_records': len(self.mnb_records),
            'current_state': self.state_machine.current_state.value,
            'state_history': [s.value for s in self.state_machine.history],
            'progress': self.state_machine.progress_percentage()
        }


# ================================================================================
# PIPELINE ORQUESTRADOR
# ================================================================================

class PipelineOrchestrator:
    """
    Orquestrador de pipeline completo.

    Integra:
    - Motor de conversão
    - Ledger
    - Quantum proofs
    - Skills
    """

    def __init__(
        self,
        name: str = "matverse_pipeline",
        config: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.config = config or {}

        # Componentes
        self.motor = ConversionMotor()
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def execute(
        self,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executa pipeline completo.

        Args:
            input_data: Dados de entrada

        Returns:
            Resultado do pipeline
        """
        self.start_time = time.time()

        # Estágio 1: PROCESS
        result1, _ = self.motor.process_event(
            EventType.PROCESS,
            input_data
        )

        # Estágio 2: VALIDATE
        result2, _ = self.motor.process_event(
            EventType.VALIDATE,
            input_data
        )

        # Estágio 3: ADVANCE
        result3, _ = self.motor.process_event(
            EventType.ADVANCE,
            input_data
        )

        self.end_time = time.time()

        return {
            'pipeline': self.name,
            'status': 'complete',
            'stages': {
                'process': result1,
                'validate': result2,
                'advance': result3
            },
            'statistics': self.motor.get_statistics(),
            'duration_ms': (self.end_time - self.start_time) * 1000
        }


# ================================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enumerações
    "MotorState",
    "EventType",

    # Classes
    "StateTransition",
    "StateMachine",
    "MNBRecord",
    "ConversionMotor",
    "PipelineOrchestrator"
]
