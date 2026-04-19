from dataclasses import dataclass
from typing import Dict, Any
import re

@dataclass
class ExecutionContext:
    skill: str
    agent: str
    input_data: Dict[str, Any]

@dataclass
class GateResult:
    allowed: bool
    reason: str

class OmegaGate:
    def __init__(self):
        self.block_patterns = [r"exec\(", r"os\.system", r"subprocess", r"rm\s+-rf"]
        self.required_fields = ["intent", "source"]

    def validate_structure(self, ctx: ExecutionContext) -> GateResult:
        for field in self.required_fields:
            if field not in ctx.input_data:
                return GateResult(False, f"missing_field:{field}")
        return GateResult(True, "ok")

    def validate_content(self, ctx: ExecutionContext) -> GateResult:
        raw = str(ctx.input_data)
        for pattern in self.block_patterns:
            if re.search(pattern, raw):
                return GateResult(False, "neycsec01")
        return GateResult(True, "ok")

    def validate_agent(self, ctx: ExecutionContext) -> GateResult:
        if "untrusted" in ctx.agent.lower():
            return GateResult(False, "agent_not_allowed")
        return GateResult(True, "ok")

    def evaluate(self, ctx: ExecutionContext) -> GateResult:
        checks = [self.validate_structure(ctx), self.validate_content(ctx), self.validate_agent(ctx)]
        for c in checks:
            if not c.allowed:
                return c
        return GateResult(True, "approved")

if __name__ == "__main__":
    gate = OmegaGate()
    ctx = ExecutionContext(
        skill="matverse-pipeline",
        agent="OIA-core",
        input_data={"intent": "process_asset", "source": "api", "payload": "safe_data"}
    )
    result = gate.evaluate(ctx)
    print(result)
