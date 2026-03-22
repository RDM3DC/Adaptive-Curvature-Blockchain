from __future__ import annotations

from blockchain import Block, Blockchain
from node import Node
from tsp_instances import TSPInstance


def _square_instance() -> TSPInstance:
    return TSPInstance(
        "square-4",
        [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)],
    )


def test_total_score_counts_only_poo_tsp_blocks() -> None:
    chain = Blockchain()
    chain.add_block(Block(1, chain.get_latest_block().hash, 1.0, {"type": "PoO-TSP", "score": 0.25}))
    chain.add_block(Block(2, chain.get_latest_block().hash, 2.0, {"type": "tx_bundle", "count": 1}))

    assert chain.total_score() == 0.25


def test_better_chain_prefers_score_then_length() -> None:
    chain_a = Blockchain()
    chain_b = Blockchain()

    chain_a.add_block(Block(1, chain_a.get_latest_block().hash, 1.0, {"type": "PoO-TSP", "score": 0.10}))
    chain_b.add_block(Block(1, chain_b.get_latest_block().hash, 1.0, {"type": "PoO-TSP", "score": 0.20}))

    assert Blockchain.better_chain(chain_a, chain_b) is chain_b

    chain_c = Blockchain()
    chain_d = Blockchain()
    chain_c.add_block(Block(1, chain_c.get_latest_block().hash, 1.0, {"type": "PoO-TSP", "score": 0.10}))
    chain_d.add_block(Block(1, chain_d.get_latest_block().hash, 1.0, {"type": "PoO-TSP", "score": 0.10}))
    chain_d.add_block(Block(2, chain_d.get_latest_block().hash, 2.0, {"type": "tx_bundle", "count": 0}))

    assert Blockchain.better_chain(chain_c, chain_d) is chain_d


def test_node_create_poo_block_accepts_when_target_met() -> None:
    node = Node()
    node.tsp_pool.target_score = 0.0
    instance = _square_instance()
    result = node.create_poo_block(instance, [0, 1, 2, 3])

    assert result["accepted"] is True
    assert len(node.blockchain.chain) == 2


def test_node_create_poo_block_rejects_invalid_tour() -> None:
    node = Node()
    instance = _square_instance()
    result = node.create_poo_block(instance, [0, 1, 1, 3])

    assert result == {"accepted": False, "reason": "Tour must be a permutation of 0..n-1"}