import math
import random
from typing import List, Tuple

Point = Tuple[float, float]
Tour = List[int]

class TSPInstance:
    def __init__(self, instance_id: str, points: List[Point]):
        self.instance_id = instance_id
        self.points = points

    def distance(self, i: int, j: int) -> float:
        (x1, y1) = self.points[i]
        (x2, y2) = self.points[j]
        return math.hypot(x1 - x2, y1 - y2)

    def tour_cost(self, tour: Tour) -> float:
        n = len(self.points)
        assert len(tour) == n, "Tour length must match number of points"
        seen = set(tour)
        assert len(seen) == n and min(tour) == 0 and max(tour) == n - 1, "Tour must be a permutation of 0..n-1"
        cost = 0.0
        for k in range(n):
            i = tour[k]
            j = tour[(k + 1) % n]
            cost += self.distance(i, j)
        return cost

def generate_random_instance(n: int = 30, seed: int | None = None) -> TSPInstance:
    rng = random.Random(seed)
    pts = [(rng.random(), rng.random()) for _ in range(n)]
    instance_id = f"rand-{n}-{rng.randrange(10**9)}"
    return TSPInstance(instance_id, pts)
