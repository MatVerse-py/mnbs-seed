import hashlib
import json
import numpy as np
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SimulationInput:
    N: int
    T: int
    seed: int
    psi_star: float
    p_tail: float

@dataclass
class SimulationResult:
    survival: int
    trajectory: list
    hash: str
    timestamp: str

class GTHDLProofEngine:
    def simulate(self, inp: SimulationInput):
        np.random.seed(inp.seed)
        psi = np.random.uniform(0.5, 0.9, inp.N)
        trajectory = []
        for t in range(inp.T):
            shocks = np.random.exponential(0.01, inp.N)
            tail = (np.random.rand(inp.N) < inp.p_tail)
            shocks += tail * np.random.exponential(0.1, inp.N)
            psi = psi - 0.002 * psi - shocks
            psi = np.clip(psi, 0, 1)
            trajectory.append(psi.mean())
        survival = int((psi > inp.psi_star).sum())
        return survival, trajectory

    def hash_result(self, data):
        raw = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(raw).hexdigest()

    def run(self, inp: SimulationInput) -> SimulationResult:
        survival, trajectory = self.simulate(inp)
        payload = {"input": asdict(inp), "survival": survival, "trajectory": trajectory}
        h = self.hash_result(payload)
        return SimulationResult(survival=survival, trajectory=trajectory, hash=h, timestamp=datetime.utcnow().isoformat())

class LocalMerkleLedger:
    def __init__(self):
        self.chain = []

    def add(self, result: SimulationResult):
        prev_hash = self.chain[-1]["hash"] if self.chain else "0"
        entry = {"prev": prev_hash, "data": asdict(result)}
        entry_hash = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
        entry["hash"] = entry_hash
        self.chain.append(entry)

    def verify(self):
        for i in range(1, len(self.chain)):
            prev = self.chain[i-1]["hash"]
            if self.chain[i]["prev"] != prev:
                return False
        return True

if __name__ == "__main__":
    engine = GTHDLProofEngine()
    ledger = LocalMerkleLedger()
    inp = SimulationInput(N=200, T=200, seed=42, psi_star=0.2, p_tail=0.04)
    result = engine.run(inp)
    ledger.add(result)
    print("HASH:", result.hash)
    print("VALID:", ledger.verify())
