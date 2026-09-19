"""Tests for the R4 branch manifest.

The load-bearing ones check that the manifest is CONSISTENT WITH GREGOR'S OWN
ARITHMETIC rather than with my transcription of it: 16 conditioning columns is a
number his code computes, and if the manifest's decomposition does not reproduce
it, the manifest is describing a different model.
"""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import r4_manifest as r4


class Enumeration(unittest.TestCase):
    def test_the_typed_set_is_the_twenty_one_the_contract_enumerated(self):
        self.assertEqual(len(r4.TYPED_OBJECT_BRANCHES), 21)
        self.assertEqual(len(set(r4.TYPED_OBJECT_BRANCHES)), 21)

    def test_the_globals_decompose_the_way_his_code_computes_them(self):
        """10 base + 6 energy sums, and the 10 as 7 + 3."""
        self.assertEqual(len(r4.GLOBAL_COLUMNS), 16)
        self.assertEqual(len(r4.ENERGY_SUM_PIDS), 6)
        base = len(r4.GLOBAL_COLUMNS) - len(r4.ENERGY_SUM_PIDS)
        self.assertEqual(base, 10)

    def test_every_global_source_branch_says_what_it_feeds(self):
        for name, entry in r4.GLOBAL_SOURCE_BRANCHES.items():
            with self.subTest(branch=name):
                self.assertTrue(entry["feeds"], f"{name} feeds nothing")
                self.assertTrue(entry["via"], f"{name} has no reading function")

    def test_the_energy_sums_need_no_branch_outside_the_typed_set(self):
        """They are sums over the typed objects' own E and PID."""
        self.assertIn("prong_part_E", r4.TYPED_OBJECT_BRANCHES)
        self.assertIn("prong_part_pid", r4.TYPED_OBJECT_BRANCHES)
        self.assertIn("MasterAnaDev_BlobTotalE", r4.TYPED_OBJECT_BRANCHES)

    def test_the_photon_kinematics_are_NOT_already_covered(self):
        """The typed set has gamma*_direction; the invariant mass needs px,py,pz,E.

        This is the substantive addition the earlier enumeration missed: the
        contract listed `gamma1_direction`, and Gregor's diphoton mass reads
        `gamma1_px/py/pz/E`. Those are different branches.
        """
        for needed in ("gamma1_px", "gamma1_E", "gamma2_pz"):
            self.assertIn(needed, r4.GLOBAL_SOURCE_BRANCHES)
            self.assertNotIn(needed, r4.TYPED_OBJECT_BRANCHES)

    def test_the_manifest_counts_each_branch_once(self):
        total = r4.total_new_branches()
        self.assertEqual(
            total,
            len(set(r4.TYPED_OBJECT_BRANCHES) | set(r4.GLOBAL_SOURCE_BRANCHES)
                | set(r4.MUON_COUNT_SOURCE_BRANCHES)))
        self.assertGreaterEqual(total, 21)


class Requirements(unittest.TestCase):
    def test_symmetry_is_stated_as_a_requirement_not_an_aspiration(self):
        self.assertIn("EVERY inventory", r4.SYMMETRY_REQUIREMENT)
        self.assertEqual(set(r4.INVENTORIES),
                         {"mc_signal_reco", "mc_background", "data"})

    def test_preservation_forbids_reselection(self):
        self.assertIn("never re-selects", r4.PRESERVATION_REQUIREMENT)

    def test_the_manifest_is_serializable_for_a_receipt(self):
        import json
        blob = json.dumps(r4.manifest())
        self.assertIn("ol_num_cond", blob)
        self.assertGreater(len(blob), 1000)


if __name__ == "__main__":
    unittest.main()


class HisKeyLists(unittest.TestCase):
    """What he builds from, and where our tuples cannot supply it."""

    def test_his_prong_key_is_absent_from_our_tuples(self):
        """Measured: `prong_part_dEdXMean` is not a branch; `prong_dEdXMean` is."""
        self.assertIn(r4.HIS_KEY_NOT_IN_OUR_TUPLES, r4.HIS_PRONG_KEYS)
        self.assertNotIn(r4.HIS_KEY_NOT_IN_OUR_TUPLES, r4.TYPED_OBJECT_BRANCHES)
        self.assertIn(r4.OUR_SUBSTITUTE, r4.TYPED_OBJECT_BRANCHES)

    def test_the_substitution_is_declared_as_unverified(self):
        self.assertIn("NOT VERIFIED", r4.SUBSTITUTION_STATUS)

    def test_branches_he_does_not_use_are_named(self):
        for name in r4.IN_OUR_MANIFEST_BUT_NOT_HIS:
            self.assertIn(name, r4.TYPED_OBJECT_BRANCHES)
            self.assertNotIn(name, r4.HIS_BLOB_KEYS)

    def test_his_blob_keys_are_all_in_our_manifest(self):
        for key in r4.HIS_BLOB_KEYS:
            self.assertIn(key, r4.TYPED_OBJECT_BRANCHES)
