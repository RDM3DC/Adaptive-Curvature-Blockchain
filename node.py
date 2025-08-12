import time
from typing import Dict, Any, List, Optional
from blockchain import Blockchain, Block
from tsp_instances import generate_random_instance, TSPInstance
from tsp_verifier import score_submission

class TSPPool:
    def __init__(self):
        self.instances: Dict[str, TSPInstance] = {}
        self.best_cost: Dict[str, float] = {}
        self.target_score: float = 0.02

    def new_instance(self, n: int = 30) -> TSPInstance:
        inst = generate_random_instance(n=n)
        self.instances[inst.instance_id] = inst
        return inst

    def get(self, instance_id: str) -> Optional[TSPInstance]:
        return self.instances.get(instance_id)

    def update_best(self, instance_id: str, cost: float) -> None:
        cur = self.best_cost.get(instance_id, float("inf"))
        if cost < cur:
            self.best_cost[instance_id] = cost

    def retarget(self, success: bool) -> None:
        if success:
            self.target_score *= 1.05
        else:
            self.target_score *= 0.95
        self.target_score = max(0.005, min(self.target_score, 0.2))

class Node:
    def __init__(self):
        self.blockchain = Blockchain()
        self.tsp_pool = TSPPool()

    def create_poo_block(self, instance: TSPInstance, tour: List[int]) -> Dict[str, Any]:
        result = score_submission(instance, tour)
        if not result["valid"]:
            return {"accepted": False, "reason": result["reason"]}

        score = result["score"]
        meets = score >= self.tsp_pool.target_score

        data = {
            "type": "PoO-TSP",
            "instance_id": instance.instance_id,
            "n": len(instance.points),
            "tour": tour,
            "cost": result["cost"],
            "baseline_cost": result["baseline_cost"],
            "delta": result["delta"],
            "score": score,
            "difficulty": self.tsp_pool.target_score,
            "accepted_at": time.time(),
        }

        if meets:
            new_block = Block(
                self.blockchain.get_latest_block().index + 1,
                self.blockchain.get_latest_block().hash,
                time.time(),
                data,
            )
            self.blockchain.add_block(new_block)
            self.tsp_pool.update_best(instance.instance_id, result["cost"])
            self.tsp_pool.retarget(success=True)
            return {"accepted": True, "block": new_block.to_dict()}
        else:
            self.tsp_pool.retarget(success=False)
            return {
                "accepted": False,
                "reason": f"Score {score:.4f} below target {self.tsp_pool.target_score:.4f}",
                "payload": data
            }
