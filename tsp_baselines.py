from typing import List
from tsp_instances import TSPInstance

def nearest_neighbor(instance: TSPInstance, start: int = 0) -> List[int]:
    n = len(instance.points)
    unvisited = set(range(n))
    tour = [start]
    unvisited.remove(start)
    cur = start
    while unvisited:
        nxt = min(unvisited, key=lambda j: instance.distance(cur, j))
        tour.append(nxt)
        unvisited.remove(nxt)
        cur = nxt
    return tour
