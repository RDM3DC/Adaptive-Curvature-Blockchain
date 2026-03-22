# Adaptive-Curvature-Blockchain

Adaptive-Curvature-Blockchain is a research prototype for proof-of-optimization consensus. Instead of proof-of-work, nodes score Traveling Salesman Problem submissions and mint blocks when a tour improves enough over a baseline heuristic.

## Project Purpose

- Demonstrate a simple useful-work blockchain loop
- Compare chains by cumulative optimization score instead of pure length
- Explore ARP-style difficulty retargeting around solver success rate

This repository is currently a small script-first prototype, not a production blockchain implementation.

## What It Does Today

- Generates Euclidean TSP instances
- Scores submitted tours against a nearest-neighbor baseline
- Mints `PoO-TSP` blocks when score meets the current target
- Retargets the acceptance threshold after success or failure
- Exposes a Flask HTTP API for local experiments
- Resolves consensus by higher total score, then longer chain

## Repository Layout

```text
blockchain.py      Core block and chain logic
node.py            Node state, TSP pool, difficulty retargeting
run_node.py        Flask API entry point
tsp_instances.py   Random TSP instance generation and cost evaluation
tsp_baselines.py   Baseline nearest-neighbor solver
tsp_verifier.py    Tour validation and score computation
src/               Small reusable experiment modules
tests/             Unit and smoke tests
```

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

If you prefer the legacy path, `pip install -r requirements.txt` still works for runtime dependencies.

## Run

Start a node:

```powershell
python run_node.py --port 5002
```

Start a second node:

```powershell
python run_node.py --port 5003
```

Register the peer from the first node:

```powershell
curl -X POST http://localhost:5002/register_node -H "Content-Type: application/json" -d '{"nodes": ["http://localhost:5003"]}'
```

## Test and Lint

```powershell
pytest
ruff check blockchain.py node.py run_node.py tsp_baselines.py tsp_instances.py tsp_verifier.py tests/test_adaptive_curvature.py tests/test_blockchain_core.py
```

## Dependencies

- `flask` for the HTTP API
- `requests` for peer consensus calls
- `numpy` for numeric utilities used elsewhere in the repo
- `ecdsa` and `gunicorn` for related runtime/deployment experiments already referenced by the project

## API Overview

- `GET /status` returns current height, total score, difficulty, pending transactions, and peers
- `GET /get_chain` returns the full chain and cumulative score
- `POST /get_instance` creates a new random TSP instance
- `POST /submit_poo_tsp` validates and scores a tour submission
- `POST /register_node` registers peers for consensus
- `GET /consensus` adopts the better peer chain
- `POST /add_transaction` and `GET /mine_block` support the transaction bundle path used by related experiments

## Minimal Example

```python
import math
import requests

NODE = "http://localhost:5002"


def build_tour(points):
    remaining = set(range(len(points)))
    tour = [0]
    remaining.remove(0)
    current = 0

    def distance(i, j):
        (x1, y1), (x2, y2) = points[i], points[j]
        return math.hypot(x1 - x2, y1 - y2)

    while remaining:
        nxt = min(remaining, key=lambda j: distance(current, j))
        tour.append(nxt)
        remaining.remove(nxt)
        current = nxt
    return tour


instance = requests.post(f"{NODE}/get_instance", json={"n": 30}).json()
tour = build_tour(instance["points"])
response = requests.post(
    f"{NODE}/submit_poo_tsp",
    json={"instance_id": instance["instance_id"], "tour": tour},
)
print(response.status_code, response.json())
```

## Current Limitations

- Consensus is a prototype and does not include adversarial-network protections
- Blocks are not proof-of-work mined; `nonce` is effectively inert
- Persistence is in-memory only; restarting a node resets chain state
- TSP scoring is deterministic but intentionally simplistic
- There is no packaging split between the script entry points and the experimental `src` module namespace yet
- This repo should be treated as research code, not production infrastructure

## License

This repository is released under the [MIT License](LICENSE).
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
