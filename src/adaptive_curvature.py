import numpy as np

class AdaptiveCurvature:
    def __init__(self, alpha=10, delta=0.1, epsilon=0.01):
        self.alpha = alpha
        self.delta = delta
        self.epsilon = epsilon
        self.curvature = 1.0

    def update_curvature(self, satisfaction_score, unsatisfaction_penalty):
        adjustment = (self.delta * satisfaction_score**2) / (1 + self.alpha * unsatisfaction_penalty)
        self.curvature += adjustment - self.epsilon * self.curvature
        return self.curvature
