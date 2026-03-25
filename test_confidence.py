import unittest
from memory.confidece import calculate_confidence

class TestConfidenceLogic(unittest.TestCase):
    def test_calculate_confidence_levels(self):
        # Test 100 iterations to check random range
        for _ in range(100):
            retention = 0.5
            conf, label = calculate_confidence(retention)
            
            # Check range: 0.5 ± 0.15 -> 0.35 to 0.65
            self.assertTrue(0.35 <= conf <= 0.65)
            self.assertTrue(0.0 <= conf <= 1.0)
            
            # Check labels
            if conf >= 0.8:
                self.assertEqual(label, "High Confidence")
            elif conf >= 0.6:
                self.assertEqual(label, "Medium Confidence")
            elif conf >= 0.4:
                self.assertEqual(label, "Low Confidence")
            elif conf >= 0.3:
                self.assertEqual(label, "Very Low Confidence")
            else:
                self.assertEqual(label, "Confused")

    def test_clamping(self):
        # Test upper clamp
        retention = 1.0
        conf, label = calculate_confidence(retention)
        self.assertTrue(conf <= 1.0)
        
        # Test lower clamp
        retention = 0.0
        conf, label = calculate_confidence(retention)
        self.assertTrue(conf >= 0.0)

if __name__ == '__main__':
    unittest.main()
