"""REVIEWER PROBE (final pass): the load-bearing middle leg of Finding 1's scoping.

The scoping says the module's own product removal cannot affect `present_names - claimed_names`,
because recovery PRESERVES the claim while moving the product. If that were false, the module's own
removal WOULD reach the difference and the products-monotone scoping would not hold.
"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_z_campaign_recovery import RecoveryFixture  # noqa: E402
import z_precursor as ZP  # noqa: E402


class RecoveryPreservesTheClaimAcrossTheProductMove(RecoveryFixture):
    def test_the_claim_SURVIVES_the_move_and_the_name_stays_in_claimed_names(self):
        contract = self.start_attempt()
        task = contract["task_id"]
        arm = contract["arm"]
        claim = os.path.join(self.paths["claims"], ZP.claim_name(arm, task))
        product = self.product_path(arm, task)
        self.assertTrue(os.path.exists(claim), "fixture: the claim must exist before recovery")
        self.assertTrue(os.path.exists(product), "fixture: a partial product must exist")
        before = ZP.claimed_task_ids(self.paths["claims"], arm)

        self.write_logs()
        self.recover()

        self.assertFalse(os.path.exists(product), "the product should have MOVED out of the arm dir")
        self.assertTrue(os.path.exists(claim),
                        "THE CLAIM WAS REMOVED BY RECOVERY -- the scoping's middle leg is false")
        after = ZP.claimed_task_ids(self.paths["claims"], arm)
        self.assertTrue(before <= after, f"the claims set shrank across recovery: {before - after}")
        self.assertIn(task, after)
        print(f"\n    claim preserved across the move: task {task} in claimed_task_ids "
              f"before={sorted(before)} after={sorted(after)}")
        print(f"    product moved out of arm dir: {not os.path.exists(product)}")


if __name__ == "__main__":
    unittest.main(verbosity=0)
