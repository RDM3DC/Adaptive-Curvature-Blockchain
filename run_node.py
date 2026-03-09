import os
from flask import Flask, jsonify, request
from blockchain import Block, Blockchain
from node import Node
import argparse
import requests

app = Flask(__name__)
node = Node()
peers = set()

# ---------------------------------------------------------------------------
# Home / health
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "node": "Adaptive-Curvature-Blockchain",
        "height": len(node.blockchain.chain),
        "pending": node.blockchain.pending_count(),
        "total_score": node.blockchain.total_score(),
    }), 200

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "height": len(node.blockchain.chain),
        "total_score": node.blockchain.total_score(),
        "difficulty": node.tsp_pool.target_score,
        "pending": node.blockchain.pending_count(),
        "peers": list(peers)
    }), 200

# ---------------------------------------------------------------------------
# Transaction pool & mining  (TopEquations certificate publishing)
# ---------------------------------------------------------------------------

@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    data = request.get_json(force=True)
    tx = data.get("transaction")
    if not tx:
        return jsonify({"error": "missing 'transaction' object"}), 400
    required = {"sender", "receiver", "amount", "type"}
    missing = required - set(tx.keys())
    if missing:
        return jsonify({"error": f"missing fields: {sorted(missing)}"}), 400
    # Attach the signature alongside the transaction data
    tx["signature"] = data.get("signature", "")
    idx = node.blockchain.add_transaction(tx)
    return jsonify({"message": "Transaction accepted", "pool_size": idx}), 201

@app.route("/mine_block", methods=["GET"])
@app.route("/mine", methods=["GET"])
def mine_block():
    if node.blockchain.pending_count() == 0:
        return jsonify({"message": "Nothing to mine", "height": len(node.blockchain.chain)}), 200
    block = node.blockchain.mine_pending_transactions()
    return jsonify({"message": "Block mined", "block": block.to_dict()}), 200

# ---------------------------------------------------------------------------
# Chain queries
# ---------------------------------------------------------------------------

@app.route("/get_chain", methods=["GET"])
@app.route("/chain", methods=["GET"])
def get_chain():
    return jsonify({
        "chain": [b.to_dict() for b in node.blockchain.chain],
        "length": len(node.blockchain.chain),
        "total_score": node.blockchain.total_score(),
    }), 200

# ---------------------------------------------------------------------------
# Peer management
# ---------------------------------------------------------------------------

@app.route("/register_node", methods=["POST"])
@app.route("/nodes/register", methods=["POST"])
def register_node():
    data = request.get_json(force=True)
    for url in data.get("nodes", []):
        peers.add(url)
    return jsonify({"message": "Peers added", "peers": list(peers)}), 201

# ---------------------------------------------------------------------------
# PoO-TSP routes (original consensus model)
# ---------------------------------------------------------------------------

@app.route("/get_instance", methods=["POST"])
def get_instance():
    data = request.get_json(force=True) if request.data else {}
    n = int(data.get("n", 30))
    inst = node.tsp_pool.new_instance(n=n)
    return jsonify({
        "instance_id": inst.instance_id,
        "points": inst.points
    }), 201

@app.route("/submit_poo_tsp", methods=["POST"])
def submit_poo_tsp():
    data = request.get_json(force=True)
    instance_id = data.get("instance_id")
    tour = data.get("tour")
    if not instance_id or tour is None:
        return jsonify({"error": "instance_id and tour required"}), 400

    inst = node.tsp_pool.get(instance_id)
    if inst is None:
        return jsonify({"error": "unknown instance_id"}), 404

    res = node.create_poo_block(inst, tour)
    return jsonify(res), 200 if res.get("accepted") else 202

@app.route("/consensus", methods=["GET"])
@app.route("/nodes/resolve", methods=["GET"])
def consensus():
    global node
    best_chain = node.blockchain
    for url in peers:
        try:
            r = requests.get(f"{url}/get_chain", timeout=3)
            if r.status_code == 200:
                payload = r.json()
                other = Blockchain()
                other.chain = [Block.from_dict(b) for b in payload["chain"]]
                best_chain = Blockchain.better_chain(best_chain, other)
        except Exception as e:
            print("Peer error:", e)

    if best_chain is not node.blockchain:
        node.blockchain = best_chain
    return jsonify({
        "message": "Consensus complete",
        "height": len(node.blockchain.chain),
        "total_score": node.blockchain.total_score()
    }), 200

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 5000)))
    args = parser.parse_args()
    app.run(host="0.0.0.0", port=args.port)
