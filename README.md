# Adaptive Curvature Coin (ACC)

Adaptive Curvature Coin is an experimental cryptocurrency prototype that
explores a **Proof-of-Optimization (PoO)** style consensus mechanism.  Blocks
track a dynamic curvature value that adjusts according to simulated
optimization results.  The project currently demonstrates the core concepts and
exposes a simple REST API for interacting with a node.

## Features

- Basic blockchain with a longest-chain conflict resolution rule
- Adaptive curvature algorithm that updates after each mined block
- Flask-based API for mining and chain management
- Simple networking support for registering and syncing multiple nodes

## Installation

```bash
git clone <repo-url>
cd Adaptive-Curvature-Coin
python -m venv venv && source venv/bin/activate  # optional
pip install -r requirements.txt
```

## Running a Node

Launch a node on a chosen port (defaults to `5002`):

```bash
python src/run_node.py --port 5002
```

## API Endpoints

| Method | Endpoint       | Description |
|--------|----------------|-------------|
| GET    | `/mine_block`  | Simulate an optimization step and append a new block |
| GET    | `/get_chain`   | Retrieve the entire blockchain |
| POST   | `/register_node` | Register peer node URLs (JSON body: `{"nodes": ["http://host:port"]}`) |
| GET    | `/nodes`       | List registered peer nodes |
| GET    | `/consensus`   | Resolve conflicts by adopting the longest known chain |

## Multi-Node Example

1. Start two nodes on different ports:
   ```bash
   python src/run_node.py --port 5002
   python src/run_node.py --port 5003
   ```
2. Register one node with the other:
   ```bash
   curl -X POST http://localhost:5002/register_node \
        -H "Content-Type: application/json" \
        -d '{"nodes": ["http://localhost:5003"]}'
   ```
3. Trigger consensus so each node adopts the longest chain:
   ```bash
   curl http://localhost:5002/consensus
   ```

## Testing

Run the unit tests with:

```bash
pytest
```

## Roadmap

- Integrate real optimization problems for PoO
- Wallet system with key pairs and transaction signing
- Persist the blockchain to disk
- Enhanced validation and security checks

## Whitepaper

TODO: add a link to the project whitepaper.

## Contributing

Open source contributions are welcome!

