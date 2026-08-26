#!/usr/bin/env python3
"""OI-136: run the fail-open probe, and make its inventory a RATCHET rather than a note.

WHY THIS EXISTS, AND WHY IT IS NOT THE 59-FILE FIX. `mnv_guarded_run.py` changed the
DIRECTION of failure for the two launchers wired to it. It did not remove a single
hardcoded `sys.path.insert(0, <cluster root>)`, and nothing stops file number 60 from
joining the set tomorrow. `OI-74`'s surviving residual is stated exactly this way --
"the real residual is a MECHANISM, not an inventory" -- and `OI-64`'s is "an unwired
check is a check nobody runs". The probe was the inventory; this is the mechanism.

IDENTITY, NOT A FLOOR, and the choice is copied from `verify_hash_bindings.py`'s
`RECEIPT_BINDING_SHA256` with its reason: a floor catches collapse but permits erosion.
Either direction requires an explicit, reviewed update here --
  * a NEW hijack site  -> red, which is the regression this exists to catch;
  * a site REPAIRED    -> also red, because a 59-file inventory inside frozen provenance
                          must not shrink silently either. Update the two constants in
                          the same commit as the repair and say which site moved.

THE INVENTORY IS OVER THE WORKING TREE, INCLUDING UNTRACKED FILES, ON PURPOSE. OI-136's
whole lesson is that the path checked and the module imported are two different facts; an
untracked `.py` that inserts the cluster root at position 0 hijacks exactly as well as a
committed one, so restricting this to `git ls-files` would reintroduce the blind spot in
the guard against it.

NON-VACUITY IS ASSERTED, NOT ASSUMED. A ratchet over an empty set passes forever, so the
probe's own positive controls are re-asserted here independently of the probe's exit code.

NO LITERAL CLUSTER ROOT APPEARS IN THIS FILE. The probe counts `.py` files containing that
literal and excludes only itself; a test that spelled the root out would add itself to the
quantity it is guarding. Same reason the probe assembles it from parts.
"""
import hashlib
import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
# REPOINTED 2026-08-26 to the dated successor. The 08-20 probe is retained on disk unedited as the
# historical record; it can no longer complete, because main repaired one of its declared positive
# controls (3d-unfolding/unfold_3d_omnifold_unbinned.py) and it must therefore exit 2 forever.
PROBE = os.path.join("docs", "orchestration", "state",
                     "probe-oi136-sys-path-hijack-20260826.py")

# Measured by running the probe; see the module docstring for the update rule.
#
# 59 -> 58 on 2026-08-20, ONE SITE REPAIRED, named as the rule requires:
# `nd-unfolding/uq_fps/corrected/test_fps_corrected_uq.py` now derives its import root from
# `Path(__file__).resolve().parents[2]` instead of inserting the hardcoded cluster root at
# position 0. It was the OI-136 pilot because it is a TEST -- a green run of it was evidence
# about the hardcoded tree rather than the tree under test -- and because it carried no receipt
# or launcher hash pin. Its exposure was LATENT, not realized: `uq_math.py` did diverge over the
# drift window (0132b60c at 683bdcca vs b382e609 at HEAD, +52 lines) but purely by appending the
# F7 helpers after `joint_throw_covariance`, so all three imported function bodies were
# byte-identical. The repaired file no longer contains the root literal at all, so the probe's
# CANDIDATE count moves 122 -> 121 in the same step; the FAIL-OPEN set below is what is pinned.
# 58 -> 52 on 2026-08-23, SIX SITES REPAIRED IN ONE AUTHORIZED SWEEP, named as the rule requires.
# Joseph granted the close-out lane ownership of the rooted-insert set that day; commits c752f73e
# (four nd-unfolding entrypoints) and a0a84a2e (the 1D study and 3D sibling):
#   nd-unfolding/bkg_channel_split.py                                parents[1]
#   nd-unfolding/coverage_toy_nd.py                                  parents[0]
#   nd-unfolding/nn_run_from_npz.py                                  parents[0]
#   nd-unfolding/unbinned_gof.py                                     parents[1]
#   2d-unfolding/unbinned_1d_study/unfold_ptmu_omnifold_unbinned.py  parents[2]/unbinned_unfolding/python
#   3d-unfolding/unfold_3d_omnifold_unbinned.py                      parents[1]
# Each now derives its import root from Path(__file__).resolve(), with NO absolute fallback. Proved
# a no-op before applying: on the canonical checkout every derived path is byte-identical to the
# literal it replaced, so behaviour on the tree that produced existing products is unchanged and the
# repair bites only on trees that are NOT that one -- which is the hazard. The parents index is
# depth-dependent and was computed per file.
#
# THIS UPDATE IS LATE AND THAT IS A DEFECT, recorded rather than smoothed over. The docstring above
# requires the two constants to move IN THE SAME COMMIT as the repair. They did not: c752f73e and
# a0a84a2e landed without them, leaving this ratchet RED on main. It is not wired into the
# pre-commit hook, so nothing caught it and no lane was blocked -- a check outside the hook is a
# check that depends on somebody running it. It was found by `minerva-omnifold-9e` in a detached
# worktree at 813a2159 while verifying something else, and that lane correctly DECLINED to update
# these constants itself: making a check green by editing its input is the move this file exists to
# prevent, and naming the moved sites is the repairing lane's to write. This is that lane doing it.
#
# THE SEVENTH SITE IN THAT AUTHORIZATION IS DELIBERATELY ABSENT.
# 2d-unfolding/unfold_2d_omnifold_unbinned.py -- the published 2D arm -- was written and REVERTED.
# Its sha256 8ebe0277... is pinned in three places needing three different treatments; advancing
# the live one (EXPECTED_U2D_SHA in nd-unfolding/pet/run_gate2_target_validator.sh) requires a
# Gate-2 RE-RUN producing bit-identical weights, not a commit, by that file's own header. See
# test_oi136_rooted_insert_ratchet.py for the full structure. It remains in the fail-open set below.
#
# 52 -> 51 on 2026-08-23, ONE SITE REPAIRED, named as the rule requires:
# `nd-unfolding/compare_unified_throw.py` now derives its import root from
# `Path(__file__).resolve().parents[1]` instead of hardcoding the canonical cluster root. It was
# repaired because it is THE ONE SITE THE k=0 ROUTE ACTUALLY EXECUTES: the rehearsal's legs 5a and
# 5b refused at the OI-136 guard with `uq_math resolved to .../MINERvA-OmniFold` against
# `expected .../k0r2/clean`. Its exposure was REALIZED, not latent -- unlike the 2026-08-20 pilot,
# this one stopped a live run. Not hash-bound: its sha256 appears zero times in the tree, checked.
#
# AND THIS UPDATE IS LATE FOR THE SECOND TIME TODAY, which is the part worth recording. The docstring
# requires the constants to move IN THE SAME COMMIT as the repair. They did not, at 91446fdd and
# again at f7dc9f1d. Both times the repairing commit passed 12/12 pre-commit because THIS RATCHET IS
# NOT WIRED INTO THE HOOK, and both times it was caught by running the suite afterwards rather than
# by the gate. Twice is a mechanism, not a slip: a check outside the hook depends on somebody
# remembering, and I did not. Wiring it in is not this commit's authorization, but the pattern is
# now on the record where the next reader will meet it.
#
# 51 IS NOT A TARGET. It is the count of sites still to be repaired, one authorized site at a time.
#
# ===== MERGE 2026-08-26: main x build-k0-execution-integrity =====
# THE TWO HISTORIES ABOVE AND BELOW ARE BOTH REAL AND NEITHER SUPERSEDES THE OTHER. Each line
# repaired SIX sites and they are DIFFERENT six: main took bkg_channel_split, coverage_toy_nd,
# nn_run_from_npz, unbinned_gof, the 1D study and the 3D sibling; the build branch took the six
# k=0 leg sites (bootstrap_nd, seedscan_split, unfold_nd_omnifold_unbinned, sweep_bank_5d,
# unified_throw_cov_5d and unified_throw_cov). BOTH sides recorded FAILOPEN_COUNT = 51 with
# DIFFERENT digests, which is the tell: the count coincided, the SETS did not.
#
# SO THE MERGED SET IS SMALLER THAN EITHER SIDE'S AND NEITHER RECORDED PAIR IS CORRECT HERE.
# The constants below are RE-MEASURED from the scanner on the merged tree, never carried over
# and never hand-set to make this check green -- which is the move this file exists to prevent.
# Superseded pairs, retained as as-of referents:
#   main         51 / 4d53806b3817...
#   build branch 51 / f37af2e3ec16...
#
# 58 IS NOT A TARGET. It is the count of sites still to be repaired, one authorized site at a time.
#
# 58 -> 52 on 2026-08-22, SIX SITES REPAIRED IN ONE AUTHORIZED STEP, named as the rule requires.
# Authorization: Joseph's ruling 18 in `DECISION-20260822-joseph-b1-lift-and-clause-c.md`, scoped by
# `REVIEW-CONTRACT-20260822-k0-execution-integrity.md` B-1 to the k=0 M(ii) path. Each derives its
# import root from `Path(__file__).resolve().parents[N]` with NO absolute fallback:
#
#   ./nd-unfolding/bootstrap_nd.py               parents[0]  entrypoint, leg 1
#   ./nd-unfolding/seedscan_split.py             parents[0]  entrypoint, leg 2
#   ./nd-unfolding/unfold_nd_omnifold_unbinned.py parents[1] entrypoint, leg 3
#   ./nd-unfolding/sweep_bank_5d.py              parents[1]  entrypoint, leg 4
#   ./nd-unfolding/unified_throw_cov_5d.py       parents[1]  entrypoint, legs 5a/5b/5c
#   ./nd-unfolding/unified_throw_cov.py          parents[1]  MODULE, imported by the line above
#                                                            AFTER its rooted insert -- excluding it
#                                                            "would leave the transitive rooted-import
#                                                            defect open" (Joseph, ruling 18)
#
# WHY EXACTLY SIX AND NOT THE 59-FILE SWEEP: the repository-wide migration is explicitly NOT
# authorized. These are six individually named sites on one path.
#
# THE PROBE'S CANDIDATE COUNT MOVES 118 -> 115 IN THE SAME STEP, and the two counts move by different
# amounts on purpose. Three of the six (`bootstrap_nd.py`, `seedscan_split.py`,
# `unified_throw_cov_5d.py`) no longer contain the root literal at all. The other three keep it in a
# `_DATA_ROOT` constant that feeds argparse defaults and data paths ONLY -- ruling 17's two-root
# design, under which the canonical checkout remains a legitimate DATA root -- so they stay
# CANDIDATES and move into the probe's `insert-but-not-rooted` bucket (13 -> 16), which is the
# probe's negative-control population. Nothing is imported or executed from `_DATA_ROOT`.
#
# BOTH VALUES BELOW WERE TAKEN FROM THIS TEST'S OWN PRINTED FAILURE MESSAGE
# (`measured: 52 files / 40bd83ca...`), never computed by hand.
# BRANCH VALUE, and it differs from main BY DESIGN. This ratchet measures the WORKING TREE, so
# its constants are ref-dependent: build-k0-execution-integrity carries the six B-1 source
# repairs that main lacks, and main carries the six 2026-08-23 sweep repairs that this branch
# lacks. The two refs are symmetric -- each is missing the other's six -- so the COUNT matches
# at 51 while the SET does not, and the digest is what distinguishes them. Do not reconcile
# these constants across refs by copying; re-measure on the ref you are on.
# Advanced here for compare_unified_throw.py, cherry-picked from main (f7dc9f1d).
# RE-MEASURED 2026-08-26 ON THE MERGED TREE, AND THE EARLIER "UNMEASURABLE" NOTE WAS WRONG.
# A first attempt here recorded the digest as unobtainable because the probe CLI exits 2. That
# inferred the QUANTITY's unmeasurability from the INSTRUMENT's refusal, which does not follow: the
# probe's components are importable and reusable without invoking its CLI.
#
# METHOD, read-only, on the merged worktree: the UNCHANGED probe module's own `ROOT`, `INSERT0`,
# `rooted_names` classifier, grep exclusions and candidate collection were reused directly. Nothing
# in the probe was edited and its CLI was not driven. The set so measured:
#
#     45 paths
#     sha256 4201aceed0604f92a3ec88591fd4e471cb723323fb01b88184024d97d6c36c8b
#
# 45 reconciles two independent ways: it equals main's recorded 51 minus the build branch's six
# additional k=0 leg-site repairs, and it equals the count this suite's own fallback assertion
# printed on the merged tree ("114 .py contain the hardcoded root; 45 FAIL-OPEN, 21
# insert-but-not-rooted, 48 no insert(0,...)").
#
# THE SETS DIVERGED WHILE THE COUNTS AGREED, which is why the digest is the load-bearing half. Both
# lines recorded FAILOPEN_COUNT = 51 with DIFFERENT digests: main repaired bkg_channel_split,
# coverage_toy_nd, nn_run_from_npz, unbinned_gof, the 1D study and the 3D sibling; the build branch
# repaired the six k=0 leg sites. Superseded pairs, retained as as-of referents:
#   main         51 / 4d53806b3817...
#   build branch 51 / f37af2e3ec16...
#
# PROBE CERTIFICATION REMAINS "CANNOT CHECK", AND THIS PAIR DOES NOT CHANGE THAT. The probe CLI must
# still exit 2 -- `CANNOT CHECK :: positive control(s) absent from the fail-open set:
# ['3d-unfolding/unfold_3d_omnifold_unbinned.py']` -- because main REPAIRED that file and the
# probe's positive control is stale against the merged tree. Neither the probe nor its positive
# controls is authorized for editing in this merge; refreshing them is the probe owner's act.
#
# SO THIS RATCHET IS **NOT** CLAIMED GREEN. The inventory constants below are measured and correct;
# the arms that require the probe CLI to complete are expected to remain RED until the positive
# control is refreshed by its owner. Recording a measured inventory and an uncertified instrument as
# two separate facts is the point -- collapsing them in either direction is the error.
FAILOPEN_COUNT = 45
FAILOPEN_SHA256 = "4201aceed0604f92a3ec88591fd4e471cb723323fb01b88184024d97d6c36c8b"

# The probe's own positive controls, restated here so this file does not inherit its blind
# spots. Relative to the repo root, as the probe prints them.
#
# `./nd-unfolding/unfold_nd_omnifold_unbinned.py` was RETIRED as a control on 2026-08-22 because it
# is one of the six repaired above: a declared positive control that is also a repair target makes
# the probe exit 2 (`CANNOT CHECK :: positive control(s) absent`) the moment the repair lands, and
# this ratchet fails with it. Its replacement was chosen from the probe's own post-repair fail-open
# output -- see the probe's own comment at `POSITIVE_CONTROLS` for why that file and not another.
# SECOND RETIREMENT, 2026-08-26, and the shape is now twice-observed rather than once.
# `./3d-unfolding/unfold_3d_omnifold_unbinned.py` was retired as a control for exactly the reason the
# 08-22 note above gives for its predecessor: main repaired it (c752f73e, a0a84a2e), so a declared
# control became a repair target and the probe had to exit 2. Its replacement, the published 2D arm,
# was chosen from the successor probe's own post-repair fail-open output and carries a standing
# ruling AGAINST repair, which is what makes it stable where the previous two were not.
POSITIVE_CONTROLS = ("./nd-unfolding/adopt_unified_5d.py",
                     "./2d-unfolding/unfold_2d_omnifold_unbinned.py")

GUARD_REL = os.path.join("nd-unfolding", "mnv_guarded_run.py")
GUARDED_LAUNCHERS = (os.path.join("nd-unfolding", "pet",
                                  "sbatch_gate5_data_only_train_array.sh"),
                     os.path.join("nd-unfolding", "pet",
                                  "sbatch_gate5_data_only_target_array.sh"))


def run_probe():
    if sys.version_info < (3, 10):
        raise unittest.SkipTest(
            "the probe's annotations need >= 3.10; run this suite under "
            "/usr/bin/python3.11 or the root_6_28 env")
    return subprocess.run([sys.executable, PROBE], cwd=REPO,
                          capture_output=True, text=True)


def failopen_set(stdout):
    block = stdout.split("FAIL-OPEN SET:", 1)
    if len(block) != 2:
        raise AssertionError("the probe printed no FAIL-OPEN SET block; parse this, never "
                             "treat a missing block as an empty inventory")
    return sorted(l.strip() for l in block[1].strip().splitlines() if l.strip())


class TheProbeStillMeasures(unittest.TestCase):
    def test_it_exits_0_which_means_BOTH_its_controls_held(self):
        """Exit 2 is 'cannot check'. Reading that as a clean tree is the failure mode."""
        p = run_probe()
        self.assertEqual(p.returncode, 0,
                         f"probe did not report a measurement.\nstdout:\n{p.stdout}\n"
                         f"stderr:\n{p.stderr}")
        self.assertIn("positive controls IN the set", p.stdout)
        self.assertIn("negative control -- rejected", p.stdout)

    def test_its_negative_control_still_rejects_something(self):
        """A classifier that rejects nothing has not been shown to discriminate."""
        p = run_probe()
        m = re.search(r"negative control -- rejected (\d+)", p.stdout)
        self.assertIsNotNone(m, p.stdout)
        self.assertGreater(int(m.group(1)), 0)


class TheInventoryIsARatchet(unittest.TestCase):
    def test_the_fail_open_set_is_EXACTLY_the_recorded_one(self):
        p = run_probe()
        rels = failopen_set(p.stdout)
        digest = hashlib.sha256("".join(r + "\n" for r in rels).encode()).hexdigest()
        self.assertEqual(
            (len(rels), digest), (FAILOPEN_COUNT, FAILOPEN_SHA256),
            "The OI-136 fail-open inventory MOVED.\n"
            f"  recorded: {FAILOPEN_COUNT} files / {FAILOPEN_SHA256}\n"
            f"  measured: {len(rels)} files / {digest}\n"
            "A NEW site is a regression: an absolute insert(0, <cluster root>) executes that "
            "tree's modules whichever checkout launched the entrypoint, PYTHONPATH cannot "
            "outrank position 0, and a re-deploy does not fix it. A REPAIRED site is welcome "
            "and still red: update both constants above in the same commit, naming the site.\n"
            f"  measured set:\n    " + "\n    ".join(rels))

    def test_this_ratchet_cannot_pass_over_an_empty_set(self):
        """Non-vacuity, asserted here rather than inherited from the probe's exit code."""
        p = run_probe()
        rels = failopen_set(p.stdout)
        self.assertGreater(len(rels), 0)
        for c in POSITIVE_CONTROLS:
            self.assertIn(c, rels,
                          f"{c} is a known hijacker by inspection; if it is missing the "
                          f"classifier under-counts and the smaller number is not the answer")


class TheMitigationIsStillDeployed(unittest.TestCase):
    """A guard that exists and is not invoked is the OI-64 shape, not a mitigation."""

    def test_the_guard_file_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(REPO, GUARD_REL)), GUARD_REL)

    def test_both_data_only_launchers_still_invoke_it_with_the_mandatory_split(self):
        for rel in GUARDED_LAUNCHERS:
            with self.subTest(launcher=rel):
                with open(os.path.join(REPO, rel)) as fh:
                    text = fh.read()
                self.assertIn("mnv_guarded_run.py", text)
                self.assertRegex(
                    text, r'"\$GUARD"\s+--expect-root\s+"\$CODE_ROOT"\s+--',
                    "the `--` split is mandatory; without it a child flag can be eaten "
                    "by the wrapper")

    def test_the_guard_is_itself_parity_checked_by_those_launchers(self):
        """A guard imported from the tree it polices is theatre; the launchers say so."""
        for rel in GUARDED_LAUNCHERS:
            with self.subTest(launcher=rel):
                with open(os.path.join(REPO, rel)) as fh:
                    text = fh.read()
                self.assertIn('--pair "${GUARD}=nd-unfolding/mnv_guarded_run.py"', text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
