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

    # ⚠ THREE TESTS INVERTED 2026-09-21. They asserted the LIMITATION; the limitation was removed
    # by the L2 estimator change Joseph authorized that day, and this file's own failure message
    # said that outcome is "NOT A TEST FAILURE TO SILENCE ... the scope limitation is obsolete and
    # must be withdrawn". So they now assert the REMOVAL and ratchet in the other direction: if
    # anyone re-pins the seed or un-scopes the directory, these go red again.
    # Record: docs/orchestration/PREDECLARATION-20260921-L2-lateral-seed-release.md

    def test_the_chain_NOW_READS_the_offset_and_that_is_the_point(self):
        """Inverted. At least one file in the chain must read the offset, or the five bands are
        back off the hook and every `L2` statement derived from this change is void."""
        readers = {name: LATERAL_CHAIN[name] for name in LATERAL_CHAIN
                   if (ND / name).is_file()
                   and OFFSET_ENV in (ND / name).read_text(encoding="utf-8")}
        for name in LATERAL_CHAIN:
            self.assertTrue((ND / name).is_file(), f"{name} is gone; this test is now blind")
        self.assertIn("run_p4_unfold_std.sh", readers,
                      "⚠ THE UNFOLD STAGE NO LONGER READS THE OFFSET. The five lateral bands are "
                      "back off the hook, so the L2 probe's premise is gone and any result quoted "
                      "from it is void. This is not a test to silence.")

    def test_the_live_unfold_stage_DERIVES_the_seed_from_the_offset(self):
        """Inverted. The literal is gone and the seed is `42 + offset`, applied uniformly."""
        text = (ND / "run_p4_unfold_std.sh").read_text(encoding="utf-8")
        self.assertRegex(text, r"--seed\s+\"\$\{P4_EST_SEED\}\"",
                         "the unfold no longer passes the derived seed variable")
        self.assertRegex(text, r"P4_EST_SEED=\$\(\(\s*42\s*\+\s*\$\{MNV_EST_SEED_OFFSET:-0\}\s*\)\)",
                         "the seed must be 42 + offset; a different baseline would silently "
                         "re-base every member")
        # ⚠ STRIP COMMENTS BEFORE MATCHING -- BEN-482, and it caught me writing this test.
        # The header now explains the change and necessarily contains the words "--seed 42", so a
        # naive scan of the whole file matches the PROSE that documents the removal. The comment is
        # the most useful line in the block, so the matcher is what changes.
        code = "\n".join(l for l in text.split("\n") if not l.lstrip().startswith("#"))
        self.assertNotRegex(code, r"--seed\s+42\b",
                            "a literal --seed 42 has returned to the unfold invocation")

    def test_the_active_bands_come_from_a_MANIFEST_DERIVED_directory(self):
        """Inverted, and it asserts the STRONGER property that replaced the hardcoding.

        `UDIR` is now derived from the manifest's own path, not from the environment. That makes
        the pairing structural: a member manifest can only be checked against member unfolds.
        """
        text = (ND / "p4_build_components.py").read_text(encoding="utf-8")
        self.assertNotIn('UDIR = "active_universe_5d/standard/unfolds"', text,
                         "the hardcoded unfolds directory is back; no member-local active "
                         "candidate can be produced and the L2 probe cannot run")
        self.assertIn("def build_active_bands(manifest, idx, udir)", text,
                      "the directory must be a parameter")
        self.assertIn("os.path.dirname(os.path.dirname(os.path.abspath(a.manifest)))", text,
                      "it must be derived from the MANIFEST path -- deriving it from the "
                      "environment instead would let a baseline manifest point at member unfolds")

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
