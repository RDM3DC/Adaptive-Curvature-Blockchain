from flask import Flask, jsonify, request
from blockchain import Block, Blockchain
from node import Node
import argparse
import requests

app = Flask(__name__)
node = Node()
peers = set()

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "height": len(node.blockchain.chain),
        "total_score": node.blockchain.total_score(),
        "difficulty": node.tsp_pool.target_score,
        "peers": list(peers)
    }), 200

@app.route("/get_chain", methods=["GET"])
def get_chain():
    return jsonify({
        "chain": [b.to_dict() for b in node.blockchain.chain],
        "length": len(node.blockchain.chain),
        "total_score": node.blockchain.total_score(),
    }), 200

@app.route("/register_node", methods=["POST"])
def register_node():
    data = request.get_json(force=True)
    for url in data.get("nodes", []):
        peers.add(url)
    return jsonify({"message": "Peers added", "peers": list(peers)}), 201

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
    parser.add_argument("--port", type=int, default=5002)
    args = parser.parse_args()
    app.run(host="0.0.0.0", port=args.port, debug=True)
