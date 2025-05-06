from flask import Flask, jsonify, request
from blockchain import Blockchain, Block
from adaptive_curvature import AdaptiveCurvature
import time
import requests

app = Flask(__name__)

blockchain = Blockchain()
curvature = AdaptiveCurvature()
nodes = set()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    latest_block = blockchain.get_latest_block()
    complexity = np.random.uniform(1, 100)
    curvature_value = curvature.update_curvature(np.random.uniform(0, complexity), complexity)
    block_data = f"Block | Curvature: {curvature_value:.4f}"
    new_block = Block(latest_block.index + 1, latest_block.hash, time.time(), block_data)
    blockchain.add_block(new_block)

    response = {
        'message': 'New block mined successfully',
        'index': new_block.index,
        'data': new_block.data,
        'hash': new_block.hash,
        'previous_hash': new_block.previous_hash,
        'timestamp': new_block.timestamp
    }
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': [block.to_dict() for block in blockchain.chain],
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/register_node', methods=['POST'])
def register_node():
    json_data = request.get_json()
    nodes_to_add = json_data.get('nodes', [])
    for node in nodes_to_add:
        nodes.add(node)
    response = {
        'message': 'Nodes added',
        'total_nodes': list(nodes)
    }
    return jsonify(response), 201

@app.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify({'nodes': list(nodes)}), 200

@app.route('/consensus', methods=['GET'])
def consensus():
    global blockchain
    longest_chain = blockchain.chain
    max_length = len(longest_chain)

    for node in nodes:
        response = requests.get(f"{node}/get_chain")
        if response.status_code == 200:
            length = response.json()['length']
            chain = response.json()['chain']
            if length > max_length:
                longest_chain = [Block.from_dict(b) for b in chain]
                max_length = length

    blockchain.chain = longest_chain
    return jsonify({
        'message': 'Chain updated',
        'length': max_length,
        'chain': [block.to_dict() for block in longest_chain]
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
