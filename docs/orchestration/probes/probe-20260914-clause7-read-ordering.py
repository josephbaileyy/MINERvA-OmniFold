"""INDEPENDENT REVIEWER PROBE -- deterministic demonstration of the clause-7 read ordering.

`verify_task_ownership` reads the CLAIMS at z_precursor.py:1432 and the PRODUCTS at :1439. A
sibling that creates its claim AND publishes its product between those two reads is absent from the
claims snapshot and present in the products snapshot, so `present_names - claimed_names` reports it
as an unclaimed foreign product and the innocent task refuses.

The wrapper below controls only WHEN the sibling completes -- it manufactures the interleaving the
way the interrupted-write arm manufactures a SIGKILL. No subject logic is modified.
"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_z_campaign_ownership import CampaignFixture  # noqa: E402
import z_precursor as ZP  # noqa: E402


class Clause7ReadOrderingRefusesACorrectlyBoundSibling(CampaignFixture):
    def test_a_sibling_completing_BETWEEN_the_two_reads_is_reported_as_FOREIGN(self):
        real = ZP.claimed_task_ids
        state = {"fired": False}

        def claims_then_sibling_completes(claims_dir, arm):
            out = real(claims_dir, arm)          # the snapshot the subject will use
            if not state["fired"] and arm == "block":
                state["fired"] = True
                # a CORRECTLY BOUND sibling finishes here: claim first, then publish -- the real
                # order, just landing inside the window between the subject's two reads.
                self.run_task("block", 5)
            return out

        ZP.claimed_task_ids = claims_then_sibling_completes
        try:
            with self.assertRaises(Exception) as caught:
                self.run_task("block", 3)
        finally:
            ZP.claimed_task_ids = real
        msg = str(caught.exception)
        self.assertIn("has CLAIMED", msg,
                      f"expected the clause-7 FOREIGN refusal, got: {msg[:300]}")
        sibling = self.campaign["body"]["arms"]["block"]["outputs"]["5"]
        self.assertIn(sibling, msg)
        print("\n    TASK 3 REFUSED BECAUSE OF ITS SIBLING TASK 5:")
        print("    " + msg.strip()[:320])
        print("    Sibling 5's claim EXISTS on disk:",
              os.path.exists(os.path.join(self.paths["claims"], ZP.claim_name("block", 5))))

    def test_CONTROL_the_same_sibling_completing_BEFORE_the_call_is_accepted(self):
        """The same sibling, same claim, same product -- completed before task 3 starts. If this
        also refused, the finding above would be about siblings in general and not about ordering."""
        self.run_task("block", 5)
        self.run_task("block", 3)          # must NOT raise
        print("\n    CONTROL: sibling 5 completed first -> task 3 succeeds. The difference is TIMING.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
