#!/usr/bin/env python3
"""The five ACTIVE lateral bands of `C_Z` are produced at a FIXED estimator seed, by design.

WHY THIS TEST EXISTS. The cause-3 campaign varies `MNV_EST_SEED_OFFSET` across seven hooked
launchers and measures how much `C_Z` moves. A reader of a MET result will take it to mean "the
estimator seed does not move this covariance". For five of the 45 bands that statement is true for
a reason that has nothing to do with the measurement: **the offset hook cannot reach them.**

`z_build` reads the five bands of `z_contract.LATERAL_BANDS` from the `active` source --
`hCov_active5d_*` -- which `p4_build_components.build_active_bands` derives from ten endpoint
unfolds under `active_universe_5d/standard/unfolds`. Those unfolds are produced by
`run_p4_unfold_std.sh`, which passes a **literal `--seed 42`** on both MAT endpoints of every band,
with its own stated reason: *"FIXED --seed 42 (MAT +/- cancels CV)"*. Fixing the seed on both
endpoints is what makes the endpoint DIFFERENCE a systematic shift rather than a shift plus
estimator noise, so it is deliberate.

**The consequence is a SCOPE LIMIT ON ANY GRADE, and it is Joseph's to weigh, not this lane's to
change** -- moving those unfolds onto the offset hook is a material change to the estimator, which
is reserved. This file makes the fact executable so that a later lane cannot assume the laterals
vary, and so that the limitation cannot be quietly dropped from a scope statement.
"""
import re
import sys
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
if str(ND) not in sys.path:
    sys.path.insert(0, str(ND))

import z_contract as zc            # noqa: E402

OFFSET_ENV = "MNV_EST_SEED_OFFSET"

#: The chain from `z_build`'s `active` source back to an estimator seed. Named, with what each is.
LATERAL_CHAIN = {
    "run_p4_standard.sh": "the driver that orchestrates the standard P4 stages",
    "run_p4_unfold_std.sh": "stage 2 -- the ten endpoint unfolds the active bands come from",
    "run_p4_merge_audit_std.sh": "stage 1 -- the merges those unfolds consume",
    "p4_evidence.py": "stage 3 -- the evidence manifest the builder digests against",
    "p4_build_components.py": "stage 4 -- builds hCov_active5d_* from the ten endpoints",
    "run_active_lateral_unfolds_interactive.sh": "the retired interactive predecessor",
}


class TheOffsetHookCannotReachTheLateralBands(unittest.TestCase):
    def test_the_five_lateral_bands_are_the_detector_and_muon_families(self):
        """Pin WHICH bands this concerns, so a partition change is visible here."""
        self.assertEqual(sorted(zc.LATERAL_BANDS),
                         ["BeamAngleX", "BeamAngleY", "MuonResolution",
                          "Muon_Energy_MINERvA", "Muon_Energy_MINOS"])

    def test_no_file_in_the_chain_reads_the_offset(self):
        offenders = {}
        for name in LATERAL_CHAIN:
            p = ND / name
            self.assertTrue(p.is_file(), f"{name} is gone; this test is now blind")
            if OFFSET_ENV in p.read_text(encoding="utf-8"):
                offenders[name] = LATERAL_CHAIN[name]
        self.assertEqual(
            offenders, {},
            "⚠ THE SITUATION HAS CHANGED, AND THAT IS NOT A TEST FAILURE TO SILENCE. A file in "
            f"the active-lateral chain now reads {OFFSET_ENV}: {offenders}. Either the lateral "
            "bands have been put on the offset hook -- in which case the scope limitation "
            "recorded for the cause-3 grade is obsolete and must be withdrawn -- or something "
            "reads the variable for another purpose. Decide which, then update this test.")

    def test_the_live_unfold_stage_pins_the_seed_as_a_LITERAL(self):
        text = (ND / "run_p4_unfold_std.sh").read_text(encoding="utf-8")
        self.assertRegex(text, r"--seed\s+42\b",
                         "the live P4 unfold stage no longer pins seed 42 as a literal")
        self.assertNotRegex(text, r"--seed\s+[\"']?\$",
                            "the seed is now a variable; the pinning claim needs re-measuring")

    def test_the_active_bands_come_from_a_directory_that_is_not_member_scoped(self):
        """`build_active_bands` hardcodes its directory, so there is no member-local variant."""
        text = (ND / "p4_build_components.py").read_text(encoding="utf-8")
        self.assertIn('UDIR = "active_universe_5d/standard/unfolds"', text,
                      "if UDIR became a parameter, a member-local active candidate may now be "
                      "producible and the limitation should be re-examined")

    def test_z_build_really_does_take_the_lateral_bands_from_ACTIVE(self):
        """The premise of the whole limitation: if it read them from `support`, they WOULD vary."""
        text = (ND / "z_build.py").read_text(encoding="utf-8")
        self.assertIn('sources["active"].read(p4.candidate_band_key(band)', text)
        self.assertIn("for band in contract.LATERAL_BANDS", text)

    def test_the_limitation_is_recorded_where_a_reader_will_find_it(self):
        doc = (ND.parent / "docs" / "orchestration" /
               "EVIDENCE-20260919-lateral-bands-are-seed-pinned.md")
        self.assertTrue(doc.is_file(), "the measurement must be committed, not only tested")
        text = doc.read_text(encoding="utf-8")
        for band in zc.LATERAL_BANDS:
            self.assertIn(band, text)
        self.assertIn("material change to the estimator", text.lower(),
                      "the record must say whose act unpinning the seed would be")


if __name__ == "__main__":
    unittest.main()
