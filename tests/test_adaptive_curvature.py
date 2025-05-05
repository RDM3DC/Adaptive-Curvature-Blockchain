import unittest
from src.adaptive_curvature import AdaptiveCurvature

class TestAdaptiveCurvature(unittest.TestCase):
    def test_curvature_update(self):
        ac = AdaptiveCurvature()
        initial_curvature = ac.curvature
        updated_curvature = ac.update_curvature(5, 2)
        self.assertNotEqual(initial_curvature, updated_curvature)
        self.assertGreater(updated_curvature, initial_curvature)

if __name__ == '__main__':
    unittest.main()
