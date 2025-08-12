import hashlib
import json
import time
from typing import Any, Dict, List

def _hash_dict(d: Dict[str, Any]) -> str:
    s = json.dumps(d, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode()).hexdigest()

class Block:
    def __init__(self, index: int, previous_hash: str, timestamp: float, data: Dict[str, Any], nonce: int = 0):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_dict = {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "nonce": self.nonce,
        }
        return _hash_dict(block_dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "nonce": self.nonce,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, block_dict: Dict[str, Any]) -> "Block":
        b = cls(
            index=block_dict["index"],
            previous_hash=block_dict["previous_hash"],
            timestamp=block_dict["timestamp"],
            data=block_dict["data"],
            nonce=block_dict.get("nonce", 0),
        )
        assert b.hash == block_dict.get("hash", b.hash), "Block hash mismatch"
        return b

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = [self.create_genesis_block()]

    def create_genesis_block(self) -> Block:
        return Block(0, "0", time.time(), {"type": "genesis", "msg": "Genesis Block"})

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, new_block: Block) -> None:
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def total_score(self) -> float:
        s = 0.0
        for b in self.chain:
            if isinstance(b.data, dict) and b.data.get("type") == "PoO-TSP":
                s += float(b.data.get("score", 0.0))
        return s

    @staticmethod
    def better_chain(a: "Blockchain", b: "Blockchain") -> "Blockchain":
        sa, sb = a.total_score(), b.total_score()
        if sb > sa:
            return b
        if sb < sa:
            return a
        return b if len(b.chain) > len(a.chain) else a
