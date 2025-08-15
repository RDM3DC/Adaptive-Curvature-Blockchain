Adaptive‑Curvature‑Blockchain (ACB) — Proof‑of‑Optimization (PoO) with TSP

ACB replaces wasteful Proof‑of‑Work with Proof‑of‑Optimization: miners earn blocks by submitting better solutions to real optimization problems.
This starter network uses the Traveling Salesman Problem (TSP) as the useful work and scores each block by how much the submitted tour improves over a baseline.
•Consensus: chain with higher cumulative optimization score wins (tie → longer chain).
•Difficulty: auto‑tunes (ARP‑style) based on recent success rate.
•Verifier: recomputes TSP tour cost, checks validity (permutation of all cities).

⸻

Features
•🧠 Useful work: TSP tour improvements mint blocks (PoO‑TSP blocks).
•⚖️ Scoring: score = (baseline_cost − cost) / baseline_cost ∈ [0, 1].
•📈 Consensus: prefers higher total PoO score across the chain.
•🛠️ Difficulty retarget: increases when solutions succeed, decreases when they fail.
•🌐 Multi‑node: register peers and run /consensus to converge on the best chain.
•🔌 Pluggable solver: bring your own TSP solver; the node only verifies and scores.

⸻

Repo Layout

.
├── blockchain.py         # Block + Blockchain (score-aware consensus comparator)
├── node.py               # Node, TSP pool, difficulty retarget, block creation
├── run_node.py           # Flask API server (endpoints below)
├── tsp_instances.py      # Random Euclidean TSP instance generator + cost
├── tsp_baselines.py      # Baseline tour (Nearest Neighbor)
├── tsp_verifier.py       # Tour validation + scoring against baseline
└── requirements.txt      # flask, requests, numpy

⸻

Quickstart

1) Install

```
python -m venv .venv
source .venv/bin/activate        # or: .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2) Run a node

```
python run_node.py --port 5002
```

Optional: run a second node as a peer:

```
python run_node.py --port 5003
```

Register peers (from 5002, add 5003):

```
curl -X POST http://localhost:5002/register_node \
  -H "Content-Type: application/json" \
  -d '{"nodes": ["http://localhost:5003"]}'
```

⸻

API

GET /status

Node health + difficulty.

Response

```
{
  "height": 1,
  "total_score": 0.0,
  "difficulty": 0.02,
  "peers": ["http://localhost:5003"]
}
```

⸻

GET /get_chain

Full chain + cumulative score.

Response

```
{
  "chain": [ { "index": 0, "data": {"type": "genesis", "msg": "Genesis Block"}, "...": "..." } ],
  "length": 1,
  "total_score": 0.0
}
```

⸻

POST /get_instance

Create a new TSP instance.

Body

```
{ "n": 30 }   // optional (default 30)
```

Response

```
{
  "instance_id": "rand-30-123456789",
  "points": [[0.12,0.90],[0.55,0.48], ...]   // n pairs in [0,1]^2
}
```

⸻

POST /submit_poo_tsp

Submit a tour for scoring and block minting.

Body

```
{
  "instance_id": "rand-30-123456789",
  "tour": [0, 1, 2, ..., 29]   // permutation of 0..n-1
}
```

202 Accepted (below target)

```
{
  "accepted": false,
  "reason": "Score 0.0123 below target 0.0200",
  "payload": {
    "type": "PoO-TSP",
    "instance_id": "rand-30-123456789",
    "n": 30,
    "cost": 4.321,
    "baseline_cost": 4.374,
    "delta": 0.053,
    "score": 0.0121,
    "difficulty": 0.02,
    "accepted_at": 1723500000.123
  }
}
```

200 OK (minted block)

```
{
  "accepted": true,
  "block": {
    "index": 1,
    "previous_hash": "...",
    "timestamp": 1723500123.456,
    "data": {
      "type": "PoO-TSP",
      "instance_id": "rand-30-123456789",
      "n": 30,
      "tour": [ ... ],
      "cost": 4.200,
      "baseline_cost": 4.374,
      "delta": 0.174,
      "score": 0.0398,
      "difficulty": 0.0209,
      "accepted_at": 1723500123.450
    },
    "nonce": 0,
    "hash": "..."
  }
}
```

⸻

GET /consensus

Fetch peers’ chains and adopt the best one:
1.Higher total PoO score
2.Tie‑break by length

Response

```
{
  "message": "Consensus complete",
  "height": 5,
  "total_score": 0.124
}
```

⸻

Minimal Client Example (Python)

This script:
1.Gets an instance
2.Builds a naive tour (Nearest Neighbor example logic)
3.Submits it for scoring

Tip: Replace build_tour(points) with your advanced solver to mint blocks reliably.

```
import requests, math, random

NODE = "http://localhost:5002"

def build_tour(points):
    n = len(points)
    remaining = set(range(n))
    tour = [0]
    remaining.remove(0)

    def dist(i, j):
        (x1, y1), (x2, y2) = points[i], points[j]
        return math.hypot(x1 - x2, y1 - y2)

    cur = 0
    while remaining:
        nxt = min(remaining, key=lambda j: dist(cur, j))
        tour.append(nxt)
        remaining.remove(nxt)
        cur = nxt
    return tour

# 1) get an instance
r = requests.post(f"{NODE}/get_instance", json={"n": 30})
inst = r.json()
instance_id, points = inst["instance_id"], inst["points"]

# 2) build a tour with your solver
tour = build_tour(points)

# 3) submit
resp = requests.post(f"{NODE}/submit_poo_tsp", json={"instance_id": instance_id, "tour": tour})
print(resp.status_code, resp.json())
```

⸻

Difficulty Retargeting (ARP‑style)
•Success (block minted): increase target score by ~5% (harder).
•Fail (below target): decrease target score by ~5% (easier).
•Clamp: [0.005, 0.20] to keep tasks feasible.

This keeps throughput steady while encouraging meaningful improvements.

⸻

Bring Your Own Solver

The node is solver‑agnostic: it verifies and scores submissions.
Use any method (heuristics, NH‑ARP, Curve‑Memory, LKH, SA/GA, RL/LLM, etc.).
Higher improvement → higher block score → stronger chain.

⸻

Multi‑Node Demo
1.Start two nodes:

```
python run_node.py --port 5002
python run_node.py --port 5003
```

2.Register peers:

```
curl -X POST http://localhost:5002/register_node \
  -H "Content-Type: application/json" \
  -d '{"nodes": ["http://localhost:5003"]}'
```

3.Mine (submit solutions) on both nodes, then:

```
curl http://localhost:5002/consensus
```

⸻

Roadmap
•✅ TSP PoO prototype (this repo)
•⏭️ Wallets & signatures (tx auth)
•⏭️ Persistence (disk/DB)
•⏭️ Anti‑dup novelty (Curve‑Memory‑based)
•⏭️ Additional problem types (graph cuts, routing, energy minima)
•⏭️ NFT layer (mint solution‑NFTs with metadata/art)

⸻

License

MIT (or your preferred license)

⸻

Acknowledgements

This project integrates our ARP/Curve‑Memory work with blockchain consensus to create a science‑positive network. Special thanks to collaborators and reviewers exploring PoO as a practical path to useful decentralized compute.

⸻
