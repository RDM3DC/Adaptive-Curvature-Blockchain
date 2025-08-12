from typing import Dict, List, Tuple
from tsp_instances import TSPInstance
from tsp_baselines import nearest_neighbor

def verify_tour(instance: TSPInstance, tour: List[int]) -> Tuple[bool, str]:
    n = len(instance.points)
    if len(tour) != n:
        return False, "Tour length mismatch"
    if sorted(tour) != list(range(n)):
        return False, "Tour must be a permutation of 0..n-1"
    return True, "ok"

def score_submission(instance: TSPInstance, tour: List[int]) -> Dict:
    ok, msg = verify_tour(instance, tour)
    if not ok:
        return {"valid": False, "reason": msg}
    cost = instance.tour_cost(tour)
    baseline_tour = nearest_neighbor(instance, 0)
    baseline_cost = instance.tour_cost(baseline_tour)
    delta = max(0.0, baseline_cost - cost)
    score = delta / baseline_cost if baseline_cost > 0 else 0.0
    return {
        "valid": True,
        "cost": cost,
        "baseline_cost": baseline_cost,
        "delta": delta,
        "score": score,
        "baseline_tour": baseline_tour
    }
