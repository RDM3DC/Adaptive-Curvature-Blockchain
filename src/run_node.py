from flask import Flask, jsonify, request
from blockchain import Block
from node import Node
import time
import requests
import argparse
import numpy as np

app = Flask(__name__)

node = Node()
nodes = set()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    complexity = np.random.uniform(1, 100)
    curvature_value = node.perform_optimization(complexity)
    block_data = f"Block | Curvature: {curvature_value:.4f}"
    new_block = node.create_block(block_data)

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
        'chain': [block.to_dict() for block in node.blockchain.chain],
        'length': len(node.blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/register_node', methods=['POST'])
def register_node():
    json_data = request.get_json()
    nodes_to_add = json_data.get('nodes', [])
    for node_url in nodes_to_add:
        nodes.add(node_url)
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
    global node
    longest_chain = node.blockchain.chain
    max_length = len(longest_chain)

    for node_url in nodes:
        try:
            response = requests.get(f"{node_url}/get_chain")
            if response.status_code == 200:
                length = response.json().get('length', 0)
                chain = response.json().get('chain', [])
                if length > max_length:
                    longest_chain = [Block.from_dict(b) for b in chain]
                    max_length = length
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to node {node_url}: {e}")

    node.blockchain.chain = longest_chain
    return jsonify({
        'message': 'Chain updated',
        'length': max_length,
        'chain': [block.to_dict() for block in longest_chain]
    }), 200

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the blockchain node.')
    parser.add_argument('--port', type=int, default=5002, help='Port to run the node on')
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port, debug=True)
