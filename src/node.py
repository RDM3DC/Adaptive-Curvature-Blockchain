from adaptive_curvature import AdaptiveCurvature
from blockchain import Blockchain, Block
import time
import numpy as np

class Node:
    def __init__(self):
        self.blockchain = Blockchain()
        self.curvature = AdaptiveCurvature()

    def perform_optimization(self, problem_complexity):
        satisfaction_score = np.random.uniform(0, problem_complexity)
        unsatisfaction_penalty = problem_complexity - satisfaction_score
        curvature = self.curvature.update_curvature(satisfaction_score, unsatisfaction_penalty)
        return curvature

    def create_block(self, data):
        latest_block = self.blockchain.get_latest_block()
        new_block = Block(latest_block.index + 1, latest_block.hash, time.time(), data)
        self.blockchain.add_block(new_block)
        return new_block
