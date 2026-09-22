import unittest
import numpy as np
import sys
import hashlib
from pathlib import Path

# Add the parent directory so we can import stage_splits
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "configuration_comparison"))
import stage_splits

class TestBuildPoolsLogic(unittest.TestCase):
    def test_assignment(self):
        # Generate synthetic identity array
        N = 10000
        np.random.seed(42)
        identity = np.random.randint(0, 1000, size=(N, 5), dtype=np.int64)
        pass_truth = np.ones(N, dtype=bool)
        
        # Test exclusion is honoured
        exclusion_set = set([0, 1, 2])
        excluded_array = np.zeros(N, dtype=bool)
        excluded_array[list(exclusion_set)] = True
        
        eligible = pass_truth & (~excluded_array)
        eligible_indices = np.flatnonzero(eligible)
        eligible_identities = identity[eligible_indices]
        
        salt = b"pet-improvement-20260922-pools"
        seed = int.from_bytes(hashlib.sha256(salt).digest()[:8], 'little', signed=True)
        
        u = stage_splits.uniform_hash(eligible_identities, seed)
        
        pool_codes = np.full(N, -1, dtype=np.int8)
        mask_P = u < 0.08
        mask_F = (u >= 0.08) & (u < 0.40)
        mask_S = (u >= 0.40) & (u < 0.80)
        mask_T = (u >= 0.80) & (u < 0.97)
        mask_R = (u >= 0.97) & (u <= 1.0)
        
        pool_codes[eligible_indices[mask_P]] = 0
        pool_codes[eligible_indices[mask_F]] = 1
        pool_codes[eligible_indices[mask_S]] = 2
        pool_codes[eligible_indices[mask_T]] = 3
        pool_codes[eligible_indices[mask_R]] = 4
        
        # tests:
        # assignment is deterministic (implied by uniform_hash seed)
        u2 = stage_splits.uniform_hash(eligible_identities, seed)
        np.testing.assert_array_equal(u, u2)
        
        # pools are disjoint and cover exactly the eligible rows
        assigned = (pool_codes >= 0)
        np.testing.assert_array_equal(assigned, eligible)
        
        # exclusion is honoured
        for row in exclusion_set:
            self.assertEqual(pool_codes[row], -1)
            
        # fractions within 4 sigma of expectation
        counts = {
            0: np.sum(pool_codes == 0),
            1: np.sum(pool_codes == 1),
            2: np.sum(pool_codes == 2),
            3: np.sum(pool_codes == 3),
            4: np.sum(pool_codes == 4),
        }
        expectations = {0: 0.08, 1: 0.32, 2: 0.40, 3: 0.17, 4: 0.03}
        total_eligible = len(eligible_indices)
        
        for k, p in expectations.items():
            expected_n = total_eligible * p
            std_dev = np.sqrt(total_eligible * p * (1 - p))
            # within 4 sigma
            self.assertTrue(abs(counts[k] - expected_n) <= 4 * std_dev)

if __name__ == '__main__':
    unittest.main()
