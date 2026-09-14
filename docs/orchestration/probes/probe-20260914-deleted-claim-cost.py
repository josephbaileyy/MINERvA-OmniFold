"""REVIEWER PROBE: is the stated cost of violating premise (B) the WHOLE cost?

The record says an outside deletion makes a claimed product read as unclaimed, so the clause
REFUSES -- fails closed. True for clause 7. This asks what a deletion does to clause 10, the
O_EXCL duplicate guard, in the state the design itself distinguishes: claim present, product ABSENT
(an attempt that died before publishing).
"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_z_campaign_ownership import CampaignFixture  # noqa: E402
import z_precursor as ZP  # noqa: E402


class WhatADeletedClaimActuallyCosts(CampaignFixture):
    def test_A_product_PRESENT_then_claim_deleted(self):
        self.run_task("block", 4)                      # claim + product + record
        os.unlink(os.path.join(self.paths["claims"], ZP.claim_name("block", 4)))
        try:
            self.own("block", 4)
            print("\n    product PRESENT  -> ADMITTED (no refusal)")
        except Exception as e:
            first = str(e).strip().splitlines()[0][:110]
            print(f"\n    product PRESENT  -> REFUSES: {first}")

    def test_B_product_ABSENT_then_claim_deleted_is_the_interesting_one(self):
        self.own("block", 4)                           # claim only: died before publishing
        product = self.product_path("block", 4)
        self.assertFalse(os.path.exists(product), "fixture: no product should exist yet")
        os.unlink(os.path.join(self.paths["claims"], ZP.claim_name("block", 4)))
        try:
            self.own("block", 4)
            print("    product ABSENT   -> ADMITTED: a fresh attempt runs as if it were the FIRST,")
            print("                        bypassing campaign-recover and its per-retry approval")
        except Exception as e:
            first = str(e).strip().splitlines()[0][:110]
            print(f"    product ABSENT   -> REFUSES: {first}")


if __name__ == "__main__":
    unittest.main(verbosity=0)
