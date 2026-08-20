#!/usr/bin/env python3
"""Tests for remedy (A)'s wrapper, `mii_adopt_unified_5d_stamped.py`.

WHAT THESE TESTS DO AND DO NOT ESTABLISH, stated first because the boundary is the most useful thing
in this file. `import ROOT` raises `ModuleNotFoundError` on the lane-B host, so the wrapper's ROOT
path -- `_read_int_scalars`, `_read_double_scalar`, `_read_diagonal`, `_stamp_output` -- is not
exercised against REAL PyROOT here.

**A ROOT DOUBLE *IS* PROVIDED, and the paragraph that used to sit here said the opposite.** It is
`_FakeROOTModule` below, and it arrived in round 2 for a measured reason: without it those four
functions had ZERO coverage and five of lane C's ROOT-path mutations were uncatchable, including
deleting the entire TOCTOU closure call from `main`. This docstring denied that any double existed
for a day AFTER the double was added -- the same stale caveat as the wrapper's own `:43`, in the file
that contains the double, and the denial is quoted only in `BEN-510`'s long form because a file that
reproduces the false sentence to disown it cannot be swept for it (`BEN-482`). Corrected 2026-08-20;
see `BEN-510`, whose
mechanism is this one's sibling: **a caveat is a claim, and it must be pinned by a check or it rots
in the direction that flatters the suite.**

WHAT IS STILL TRUE, and it is the half worth keeping: the three properties that would need proving --
that a `RECREATE`d-and-closed file reopens `UPDATE`, that new `TParameter` keys are accepted on
reopen, and that `TFile.Open` re-points the global current directory -- are properties of PyROOT. The
double MODELS the third and CONFIRMS NONE of them, and if PyROOT differs these tests still pass and
the wrapper can still be wrong. What IS proved here is every decision the wrapper makes: which argv
the child gets, which keys are derived, when the cross-member refusal fires and when it must not, and
that the pinned bytes are untouched.

The preconditions the specification asserts are RE-DERIVED here rather than trusted -- including one
the specification gets wrong (`docs/orchestration/pending/README-...md:57` says `diag_comb` is at
`:135`; it is at `:128`, which is what the preserved patch says).
"""
import ast
import hashlib
import json
import os
import pathlib
import sys
import unittest

ND = pathlib.Path(__file__).resolve().parents[1]
REPO = ND.parent
if str(ND) not in sys.path:
    sys.path.insert(0, str(ND))

import mii_adopt_unified_5d_stamped as W          # noqa: E402
import mii_root_payload_classes as classes        # noqa: E402


class PreconditionsAreVerifiedNotTrusted(unittest.TestCase):
    """C listed four preconditions before ruling §25. A ruling's preconditions are exactly the kind of
    claim that is true when written and copied forward untested, so each is re-derived from source."""

    ADOPT = ND / "adopt_unified_5d.py"

    def setUp(self):
        self.src = self.ADOPT.read_text()
        self.lines = self.src.split("\n")

    def test_main_is_importable_and_guarded(self):
        """`def main()` at :72 guarded by `__main__` at :229 -- the import form's precondition. Verified
        with `ast` rather than grep so a `main` inside a class or a string cannot satisfy it."""
        tree = ast.parse(self.src)
        mains = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"]
        self.assertEqual(len(mains), 1)
        self.assertEqual(mains[0].lineno, 72, "the ruling cites :72")
        guards = [n for n in tree.body if isinstance(n, ast.If)
                  and "__main__" in ast.dump(n.test)]
        self.assertEqual(len(guards), 1)
        self.assertEqual(guards[0].lineno, 229, "the ruling cites :229")

    def test_the_output_is_RECREATEd_and_CLOSED_so_a_later_UPDATE_is_a_POST_STEP(self):
        """The precondition the whole wrapper design rests on. If the writer left the file open, or
        never closed it, reopening `UPDATE` would not be a legitimate post-step."""
        self.assertIn('ROOT.TFile.Open(args.out, "RECREATE")', self.lines[168], "cited as :169")
        self.assertEqual(self.lines[224].strip(), "fo.Close()", "cited as :225")

    def test_diag_comb_IS_AT_128_which_is_the_PATCH_and_NOT_the_README(self):
        """THE SPECIFICATION DISAGREES WITH ITSELF ABOUT THIS LINE AND ONE OF THE TWO IS WRONG.

        `PENDING-...patch` says `diag_comb` is already in memory at `:128`; the README beside it says
        `:135`. At HEAD it is `:128`, so the patch is right and the README is wrong. Pinned here because
        a line number in a specification is the class of claim that rots first, and because the README
        is the file a reader of `docs/orchestration/pending/` opens.
        """
        hits = [i + 1 for i, l in enumerate(self.lines) if l.startswith("    diag_comb = ")]
        self.assertEqual(hits, [128])

    def test_the_pinned_bytes_still_match_the_receipt_and_the_WRAPPER_CHECKS_IT(self):
        """The reason this wrapper exists at all, in both directions: the binding is intact, and the
        wrapper refuses to run against bytes that do not match it."""
        rec = json.loads((REPO / "docs/orchestration/state"
                          / "ben106-stamp-verify-active-56695424.json").read_text())
        self.assertEqual(rec["implementation"], "nd-unfolding/adopt_unified_5d.py")
        digest = hashlib.sha256(self.ADOPT.read_bytes()).hexdigest()
        self.assertEqual(digest, rec["implementation_sha256"],
                         "if this fails, somebody edited the receipt-bound writer -- which is the one "
                         "thing §25 forbids and the reason the wrapper was built")
        self.assertEqual(W.assert_pinned_writer_is_intact(), digest)

    def test_the_wrapper_REFUSES_bytes_that_do_not_match_the_binding(self):
        """A guard gets a test that it FIRES. Fed a real file whose digest is not the receipt's, the
        wrapper must refuse rather than run the subprocess -- otherwise the entire "it executes the
        bytes the receipt names" argument is decoration."""
        other = ND / "mii_root_payload_classes.py"     # a real file, wrong bytes
        with self.assertRaises(SystemExit) as cm:
            W.assert_pinned_writer_is_intact(writer=str(other))
        # it must refuse on the NAME first, which is the more specific finding
        self.assertIn("binds", str(cm.exception))
        # and on the DIGEST when the name matches -- exercised through a copy under the right basename
        import shutil, tempfile
        d = tempfile.mkdtemp()
        try:
            fake = os.path.join(d, "adopt_unified_5d.py")
            shutil.copyfile(self.ADOPT, fake)
            with open(fake, "a") as fh:
                fh.write("\n# one byte of drift\n")
            with self.assertRaises(SystemExit) as cm2:
                W.assert_pinned_writer_is_intact(writer=fake)
            msg = str(cm2.exception)
            self.assertIn("do NOT match the receipt binding", msg)
            self.assertIn("Do not update the digest", msg)
        finally:
            shutil.rmtree(d)

    def test_the_module_imports_WITHOUT_ROOT(self):
        """The structural requirement that makes every other test in this file possible: no ROOT import
        at module scope. A module-level `import ROOT` would make the pure logic untestable on any host
        without ROOT, which is every host a lane develops on."""
        tree = ast.parse((ND / "mii_adopt_unified_5d_stamped.py").read_text())
        top = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        names = {a.name for n in top if isinstance(n, ast.Import) for a in n.names}
        self.assertNotIn("ROOT", names)
        # THE SIDE-EFFECT HALF NEEDS A SUBPROCESS AND MY FIRST VERSION GOT THIS WRONG. It asserted
        # `"ROOT" not in sys.modules`, which is a statement about the WHOLE PYTEST SESSION, not about
        # this module: a sibling suite installs a ROOT stub, so the assertion passed on the file alone
        # and FAILED in the full run -- order-dependent, and measuring the wrong subject. A fresh
        # interpreter is the only instrument that can answer "does importing THIS module pull in ROOT".
        import subprocess
        r = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, %r); import mii_adopt_unified_5d_stamped as m; "
             "print('ROOT' in sys.modules)" % str(ND)],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "False",
                         "importing the wrapper must not pull in ROOT, or the pure logic is untestable "
                         "on every host a lane develops on")


class TheGroupMapIsDerived(unittest.TestCase):

    def test_groups_come_from_the_policy_table(self):
        g = W.leg_groups()
        self.assertEqual(g["g1"], ("sweep_bank_5d", 42))
        self.assertEqual(g["g2"], ("unified_throw_cov", 1000))

    def test_a_REGROUPED_leg_FAILS_CLOSED_rather_than_relabelling_a_seed(self):
        """A guard gets a test that it fires. `_g1`/`_g2` go into a citable artifact, so an upstream
        re-grouping must error rather than silently stamp the wrong group name."""
        with self.assertRaises(SystemExit) as cm:
            W.leg_groups({"sweep_bank_5d": ("g2", 42), "unified_throw_cov": ("g2", 1000)})
        self.assertIn("coherence group", str(cm.exception))
        with self.assertRaises(SystemExit) as cm2:
            W.leg_groups({"unified_throw_cov": ("g2", 1000)})
        self.assertIn("no entry for", str(cm2.exception))


class TheChildArgv(unittest.TestCase):

    def test_the_three_paths_are_passed_ONCE_and_forwarded_verbatim(self):
        argv = W.build_child_argv("u.root", "c.root", "o.root",
                                  extras=["--prod", "p.root", "--cv-centered"],
                                  python="PY", writer="WRITER")
        self.assertEqual(argv, ["PY", "WRITER",
                                "--uthrow", "u.root", "--combined", "c.root", "--out", "o.root",
                                "--prod", "p.root", "--cv-centered"])

    def test_a_SMUGGLED_out_in_the_passthrough_is_REFUSED(self):
        """THE GUARD FIRES. argparse keeps the LAST occurrence, so `--out` in the tail would redirect
        the child while this process stamped the original file -- success reported against a product
        nobody wrote, with no exception anywhere."""
        for bad in (["--out", "elsewhere.root"], ["--out=elsewhere.root"],
                    ["--uthrow", "x.root"], ["--combined=y.root"]):
            with self.subTest(bad=bad):
                with self.assertRaises(SystemExit) as cm:
                    W.build_child_argv("u", "c", "o", extras=bad)
                self.assertIn("re-specify path(s) this wrapper owns", str(cm.exception))

    def test_the_NARROWING_does_NOT_fire_on_legitimate_passthrough(self):
        """A narrowing gets a test that it does NOT fire. `--prod` and `--cv-centered` are the writer's
        own flags and must pass through untouched; a guard that also refused them would make the
        cv-centered product unbuildable through the wrapper -- i.e. would silently drop one of the two
        citable roots."""
        self.assertTrue(W.refuse_conflicting_passthrough(
            ["--prod", "products/5d/x.root", "--cv-centered"]))
        self.assertTrue(W.refuse_conflicting_passthrough([]))
        # and a value that merely CONTAINS an owned flag's name is not an occurrence of it
        self.assertTrue(W.refuse_conflicting_passthrough(["--prod", "dir/--out.root"]))

    def test_the_passthrough_split_is_the_LITERAL_double_dash(self):
        a = W.parse_args(["--uthrow", "u", "--combined", "c", "--out", "o",
                          "--", "--prod", "p.root", "--cv-centered"])
        self.assertEqual(a.extras, ["--prod", "p.root", "--cv-centered"])
        self.assertEqual((a.uthrow, a.combined, a.out), ("u", "c", "o"))
        self.assertEqual(W.parse_args(["--uthrow", "u", "--combined", "c", "--out", "o"]).extras, [])

    def test_a_FORGOTTEN_double_dash_FAILS_LOUDLY_and_does_NOT_DROP_the_flag(self):
        """MEASURED, AND IT CORRECTED MY FIRST DESIGN: with `argparse.REMAINDER` and no `--`,
        `--cv-centered` is rejected outright -- the `--` was never optional. The behaviour is kept LOUD
        on purpose. A silently dropped `--cv-centered` would build the MEAN-centered matrix and write it
        to the CV-centered product's path, and those two roots differ in nothing except payload and the
        `centering_convention` string -- so the swap is invisible to every equality check the comparator
        performs on configuration."""
        with self.assertRaises(SystemExit) as cm:
            W.parse_args(["--uthrow", "u", "--combined", "c", "--out", "o", "--cv-centered"])
        self.assertEqual(cm.exception.code, 2)
        with self.assertRaises(SystemExit) as cm2:
            W.parse_args(["--uthrow", "u", "--combined", "c", "--out", "o", "stray"])
        self.assertIn("must follow a literal", str(cm2.exception))


class TheStampedKeys(unittest.TestCase):

    G1 = {"estimator_seed": 1242, "est_seed_offset": 1200, "est_seed_offset_declared": 1}
    G2 = {"estimator_seed": 2200, "est_seed_offset": 1200, "est_seed_offset_declared": 1}

    def test_the_exact_key_value_list_for_a_declared_member(self):
        self.assertEqual(W.stamp_pairs(self.G1, self.G2, 1, 1200), [
            ("est_seed_offset_declared", 1),
            ("est_seed_offset", 1200),
            ("upstream_estimator_seed_g1_checked", 1),
            ("upstream_estimator_seed_g1", 1242),
            ("upstream_estimator_seed_g2_checked", 1),
            ("upstream_estimator_seed_g2", 2200),
        ])

    def test_NO_SINGLE_estimator_seed_KEY_IS_EVER_PRODUCED_and_that_is_VL141(self):
        """VL141: this product mixes a g1 seed (42+k) with a g2 one (1000+k), so a single
        `estimator_seed` key would be the exact false quotable claim the row exists to correct. Asserted
        over the key set rather than over one input, because the defect is a spelling that must not
        exist at all."""
        for legs in ((self.G1, self.G2), ({}, {}), (self.G1, {}), ({}, self.G2)):
            with self.subTest(legs=legs):
                keys = [k for k, _ in W.stamp_pairs(legs[0], legs[1], 1, 1200)]
                self.assertNotIn("estimator_seed", keys)

    def test_an_ABSENT_upstream_seed_is_a_READABLE_STATE_not_a_missing_key(self):
        """`adopt_unified_5d.py:193-196`'s precedent: an absent key cannot distinguish "the leg did not
        carry it" from "this build predates the propagation", and a criterion phrased over the seed
        passes vacuously on either."""
        pairs = dict(W.stamp_pairs({}, self.G2, 0, 0))
        self.assertEqual(pairs["upstream_estimator_seed_g1_checked"], 0)
        self.assertNotIn("upstream_estimator_seed_g1", pairs)
        self.assertEqual(pairs["upstream_estimator_seed_g2_checked"], 1)
        self.assertEqual(pairs["upstream_estimator_seed_g2"], 2200)

    def test_an_UNDECLARED_run_still_stamps_BOTH_offset_keys(self):
        """declared=0 must be written, not omitted: it is the state that says "nothing can be concluded
        about which member this is", and omitting it makes that indistinguishable from an old build."""
        pairs = dict(W.stamp_pairs(self.G1, self.G2, 0, 0))
        self.assertEqual(pairs["est_seed_offset_declared"], 0)
        self.assertEqual(pairs["est_seed_offset"], 0)

    def test_the_STAMPED_KEYS_ARE_EXACTLY_what_the_CLASS_TABLE_classifies(self):
        """THE COUPLING THAT MAKES THE TABLE FLIP FALSIFIABLE, in both directions.

        An unclassified key makes `compare()` FAIL with "NOT IN THE ARCHIVE KEY MAP"; a classified key
        nobody writes makes `compare()` FAIL with "ABSENT FROM MEMBER (PROVENANCE, MANDATORY)". So the
        two sets must be equal, and this is the test that would have caught either drift.
        """
        table = set(classes.ADOPTED_UTHROW)
        wrapper = set(W.STAMPED_SCALAR_KEYS) | {W.STAMPED_HISTOGRAM_KEY}
        pinned_writer_keys = {
            "hCov_combined5d_total_uthrow", "hInflation_g", "sqrt_tr_old", "sqrt_tr_new",
            "upstream_fixed_seed_null_norm", "upstream_joint_mean_shift_norm", "upstream_n_throws",
            "fixed_seed_null_norm_checked", "joint_mean_shift_norm_checked", "n_throws_checked",
            "centering_convention", "uthrow_source", "combined_source"}
        self.assertEqual(table, wrapper | pinned_writer_keys,
                         "ADOPTED_UTHROW must be exactly what the two writers between them emit")
        self.assertEqual(wrapper & pinned_writer_keys, set(),
                         "and the two writers must not both claim the same key -- ROOT would append a "
                         "second cycle rather than replace one")

    def test_every_key_the_WRAPPER_adds_has_an_ARCHIVE_KEY_MAP_row(self):
        """THE ONE THAT WOULD HAVE REDDENED THE FIRST CLUSTER RUN FOR A REASON UNRELATED TO THE WRAPPER.

        `compare():522-526` FAILS a member-only key with no map row. Generalises
        `test_the_ARCHIVE_KEY_MAP_covers_every_key_the_writers_added`, which covered the throw root only
        -- the adopted root's new keys were in NO test.
        """
        for k in sorted(set(W.STAMPED_SCALAR_KEYS) | {W.STAMPED_HISTOGRAM_KEY}):
            with self.subTest(key=k):
                self.assertIn(k, classes.ARCHIVE_KEY_MAP, f"{k} has no dated map row")
                self.assertIn("landed", classes.ARCHIVE_KEY_MAP[k])
        # and the dated excuses must survive the map's own checker against the archive's date
        self.assertGreater(classes.assert_absence_excuses_are_dated((2026, 7, 14)), 0)

    def test_an_UNCLASSIFIED_stamp_is_REFUSED_before_it_reaches_ROOT(self):
        """The guard inside `stamp_pairs` fires. Simulated by shrinking the declared key tuple, which is
        what a future lane adding a key without a table row would effectively do."""
        saved = W.STAMPED_SCALAR_KEYS
        W.STAMPED_SCALAR_KEYS = tuple(k for k in saved if k != "upstream_estimator_seed_g1")
        try:
            with self.assertRaises(SystemExit) as cm:
                W.stamp_pairs(self.G1, self.G2, 1, 1200)
            self.assertIn("does not classify", str(cm.exception))
        finally:
            W.STAMPED_SCALAR_KEYS = saved


class TheCrossMemberRefusal(unittest.TestCase):
    """A guard gets a test that it FIRES, and a narrowing gets a test that it does NOT."""

    def test_it_FIRES_on_two_different_members_legs(self):
        with self.assertRaises(SystemExit) as cm:
            W.assert_legs_are_one_member({"est_seed_offset": 1200}, {"est_seed_offset": 0}, 1, 1200)
        msg = str(cm.exception)
        self.assertIn("DIFFERENT MEMBERS", msg)
        self.assertIn("1200", msg)
        self.assertIn("carries 0", msg, "and it must name BOTH numbers, not just report a mismatch")

    def test_it_FIRES_when_THIS_PROCESS_relabels_another_members_covariance(self):
        with self.assertRaises(SystemExit) as cm:
            W.assert_legs_are_one_member({"est_seed_offset": 0}, {"est_seed_offset": 0}, 1, 1200)
        self.assertIn("Refusing to relabel", str(cm.exception))

    def test_it_FIRES_on_the_G2_ONLY_case_THE_SPECIFICATION_MISSES(self):
        """THE SPECIFICATION'S SECOND REFUSAL READS ONLY THE COMBINED LEG (`_o1`).

        So a run whose combined leg predates the stamp (offset absent) and whose THROW leg carries a
        different member's offset passes the preserved patch untouched. That is a hole in the direction
        the check acts, which is exactly what a guard's test is for. Closed here, and this test is the
        proof it is closed rather than a claim that it is.
        """
        with self.assertRaises(SystemExit) as cm:
            W.assert_legs_are_one_member({}, {"est_seed_offset": 0}, 1, 1200)
        self.assertIn("g2 leg", str(cm.exception))

    def test_it_does_NOT_fire_on_one_member(self):
        """The narrowing's own test. A wrapper that refused a legitimate single-member product would
        make the member axis unbuildable, which is a worse failure than the one being guarded."""
        self.assertTrue(W.assert_legs_are_one_member(
            {"est_seed_offset": 1200}, {"est_seed_offset": 1200}, 1, 1200))

    def test_it_does_NOT_fire_when_NOTHING_IS_DECLARED(self):
        """An undeclared run cannot be relabelling anything -- it makes no claim about membership. The
        offsets both being 0 is the archive-shaped case and must pass."""
        self.assertTrue(W.assert_legs_are_one_member(
            {"est_seed_offset": 0}, {"est_seed_offset": 0}, 0, 0))
        # and legs with NO stamps at all are uninformative, not wrong
        self.assertTrue(W.assert_legs_are_one_member({}, {}, 0, 0))

    def test_a_leg_that_ran_UNHOOKED_is_caught_by_its_BASELINE(self):
        """Independent of the offset agreement: a leg that never went through a hooked launcher stamps
        its BASELINE seed, which is indistinguishable from k=0 -- unless this process declares a
        non-zero k, in which case a baseline-valued seed is provably wrong."""
        g = W.leg_groups()
        with self.assertRaises(SystemExit) as cm:
            W.assert_seeds_match_their_baselines(
                {"estimator_seed": 42}, {"estimator_seed": 2200}, 1, 1200, g)
        self.assertIn("g1 leg's estimator_seed is 42", str(cm.exception))
        self.assertTrue(W.assert_seeds_match_their_baselines(
            {"estimator_seed": 1242}, {"estimator_seed": 2200}, 1, 1200, g))

    def test_the_baseline_check_is_SILENT_when_nothing_is_declared(self):
        """It cannot conclude anything from an undeclared run, so it must not try. Returns False to say
        "did not run" rather than True to say "passed" -- those are different answers."""
        self.assertFalse(W.assert_seeds_match_their_baselines(
            {"estimator_seed": 42}, {"estimator_seed": 1000}, 0, 0, W.leg_groups()))


class TheDiagonalIsTiedToTheProduct(unittest.TestCase):
    """THE HAZARD THE WRAPPER FORM INTRODUCES AND THE IN-FILE EDIT DID NOT HAVE.

    The in-file edit wrote `diag_comb` from the same read that produced `sqrt_tr_old`. The wrapper
    re-reads the combined intermediate after the child has exited, so the file could have changed in
    between and `hDiagCombinedOld` would be a different matrix's diagonal shipped inside this product.

    *** THIS CLASS IS WHERE D1 GOT IN, AND THE ADMISSION BELONGS HERE RATHER THAN ONLY IN A COMMIT
    MESSAGE. *** Every test here hands the assertion a FLOAT built with `math.sqrt`, while `main`
    obtained the same argument through an `int()`-coercing reader -- so the function was tested
    exclusively on values its own caller could not produce, and the suite had no power in either
    direction. Worse, one of these tests PINNED THE FALSE ACCUSATION: it asserted the message said the
    combined intermediate "is not the matrix this product was built from", which made the accusatory
    wording a REQUIREMENT of the suite. A test can hold a defect in place, and this one did.
    The producer-derived replacements are in `D1_TheAnchorIsReadAsADoubleThroughTheProducer`; these
    remain as unit coverage of the arithmetic, with their scope now stated.
    """

    def test_a_matching_trace_passes(self):
        import math
        self.assertTrue(W.assert_diag_matches_sqrt_tr_old(4.0, math.sqrt(4.0)))

    def test_a_DISAGREEMENT_is_refused_WITHOUT_BLAMING_AN_INPUT_FILE(self):
        """Renamed from `test_a_DIFFERENT_MATRIX_is_refused`, because the old name asserted the
        conclusion the message is not entitled to draw: a trace mismatch does not establish that the
        matrix differs, and two of the three causes leave every input file intact."""
        with self.assertRaises(SystemExit) as cm:
            W.assert_diag_matches_sqrt_tr_old(4.0, 3.0)
        msg = str(cm.exception)
        self.assertIn("DISAGREE", msg)
        self.assertIn("does NOT establish which side is wrong", msg)
        self.assertNotIn("not the matrix this product was built from", msg)

    def test_an_ABSENT_anchor_is_refused_rather_than_skipped(self):
        """No `sqrt_tr_old` means no tie at all, and an untied diagonal inside a citable product is
        worse than no diagonal: a reader cannot tell it is untied."""
        with self.assertRaises(SystemExit) as cm:
            W.assert_diag_matches_sqrt_tr_old(4.0, None)
        self.assertIn("unanchored", str(cm.exception))

    def test_the_tolerance_is_RELATIVE_and_tight(self):
        """A float64 round-trip through sqrt must pass; 1e-6 of drift must not. The 5D traces are ~1e-76,
        so an absolute tolerance would accept everything."""
        import math
        t = 5.8077e-38 ** 2
        self.assertTrue(W.assert_diag_matches_sqrt_tr_old(t, math.sqrt(t)))
        with self.assertRaises(SystemExit):
            W.assert_diag_matches_sqrt_tr_old(t * (1 + 1e-6), math.sqrt(t))


class TheROOTPathsSCOPEIsRecordedACCURATELY(unittest.TestCase):
    """A CLAIM ABOUT WHAT IS NOT ESTABLISHED IS STILL A CLAIM, so it gets a test too -- AND SO DOES
    ITS RETRACTION.

    THESE TESTS CHANGED DIRECTION ON 2026-08-20 AND THAT IS THE POINT. They used to assert that the
    module DECLARED its ROOT path unexecuted. Job `57294218` executed it (`1b9e074c`, RUNS.tsv
    `REMEDYA-SMOKE-PASS`), which made the declaration FALSE -- and a green suite that pins a false
    caveat is worse than no caveat, because it converts a stale sentence into a requirement. So the
    pins now assert (a) that the execution is recorded, (b) that the four things it did NOT establish
    are recorded beside it, and (c) that the retracted sentence CANNOT COME BACK.

    They still assert the DECLARATION, not the behaviour. Nothing here is evidence about ROOT.
    """

    #: The exact sentence job 57294218 falsified. Pinned as a NEGATIVE so a future edit cannot
    #: reintroduce it -- `BEN-510`: a test can assert the observable that IS the defect.
    RETRACTED = "have never been executed"

    def test_the_module_says_so_where_the_ROOT_code_is(self):
        src = (ND / "mii_adopt_unified_5d_stamped.py").read_text()
        self.assertIn("WHAT IS *NOT* ESTABLISHED", src)
        self.assertIn("CLUSTER-EXECUTED ONCE, SCOPE IN THE HEADER", src)
        self.assertNotIn("CLUSTER-UNVERIFIED", src,
                         "the blanket marker is now false: job 57294218 executed every function it "
                         "named. Correct the claim; do not keep a marker the suite has to defend.")
        self.assertNotIn(self.RETRACTED, src, f"{self.RETRACTED!r} was falsified by job 57294218")
        for fn in ("_read_int_scalars", "_read_double_scalar", "_read_diagonal", "_stamp_output"):
            self.assertIn(f"def {fn}", src)
            self.assertIn("CLUSTER-EXECUTED", src.split(f"def {fn}")[1][:600],
                          f"{fn}'s own docstring must carry the marker; a banner scrolls away")

    def test_the_EXECUTION_is_traceable_to_a_job_and_a_committed_receipt(self):
        """A capability claim that names no receipt is the thing this campaign keeps filing. The job
        id AND the commit AND the ledger row must all be in the module, so a reader can re-derive the
        claim instead of trusting the paragraph that makes it."""
        src = (ND / "mii_adopt_unified_5d_stamped.py").read_text()
        for token in ("57294218", "1b9e074c", "REMEDYA-SMOKE-PASS"):
            self.assertIn(token, src, f"the execution claim must name {token}")

    def test_the_FOUR_things_that_job_did_NOT_establish_are_all_recorded(self):
        """The half that matters. Each of these is a way a reader could over-read a PASS, and the
        second is the whole purpose of remedy (A): the identity check has never seen a present seed."""
        src = (ND / "mii_adopt_unified_5d_stamped.py").read_text()
        block = src.split("WHAT THAT JOB DOES *NOT* ESTABLISH")[1][:2600]
        self.assertIn("NOTHING IS ADOPTED", block)
        self.assertIn("NEVER SEEN A PRESENT SEED", block)
        self.assertIn("ABSENCE, NOT A PASS", block)
        self.assertIn("NO DECLARED MEMBER HAS RUN", block)
        self.assertIn("NO REFUSAL BRANCH", block)

    def test_the_STAMP_COVERAGE_row_distinguishes_CAPABILITY_from_DEMONSTRATION(self):
        how = classes.STAMP_COVERAGE["mii_adopt_unified_5d_stamped.py"]["how"]
        self.assertIn("CLUSTER-EXECUTED", how)
        self.assertNotIn("CLUSTER-UNVERIFIED", how,
                         "the row must not still say unverified after job 57294218")
        self.assertNotIn("never run", how)
        self.assertIn("2026-08-20", how, "and the claim is dated, since it is meant to expire")
        self.assertIn("ABSENCE", how,
                      "the row must carry the scope, not just the flipped boolean: _checked=0 on "
                      "both legs is absence, and a reader of `stamps: True` needs that beside it")

    def test_the_ROOT_availability_PREMISE_is_no_longer_asserted_ANYWHERE(self):
        """WHAT THIS REPLACES, AND WHY IT IS NOT JUST A DELETION. The retired test skipped itself
        whenever `import ROOT` SUCCEEDED, with a message telling the reader the markers "must be
        revisited, not trusted". On every ROOT-capable host -- which is every host that can actually
        run this wrapper -- it therefore reported SKIPPED and its instruction was never carried out;
        the caveat it guarded stayed green for three days on hosts where it was already false. A test
        whose finding is delivered as a skip is a finding nobody reads. This asserts the conclusion
        instead: the module must not condition anything on ROOT being unavailable here."""
        src = (ND / "mii_adopt_unified_5d_stamped.py").read_text()
        self.assertNotIn("EVERY ROOT-TOUCHING PATH IN THIS FILE IS CLUSTER-UNVERIFIED", src)
        self.assertIn("no longer a fact about this file", src,
                      "the lane-B host's ModuleNotFoundError must be scoped TO THAT HOST")


# =====================================================================================================
# ROUND 2, after lane C's verification came back FAIL. Everything below exists because of a defect the
# 34 tests above did not have the power to catch in either direction.
# =====================================================================================================

class _FakeParam:
    """A `TParameter` stand-in. ONE METHOD, AND THAT IS THE POINT.

    WHAT THIS ESTABLISHES: what the wrapper does with the value `GetVal()` returns. The D1 defect lived
    entirely on this side of the boundary -- `int()` applied to a float -- so this is the producer whose
    contract matters, and it is a one-line contract.
    WHAT IT DOES NOT ESTABLISH: anything about PyROOT. It does not show that a `TParameter("double")`
    read off a real file returns a Python float, that `Write()` reaches disk, or that a key is findable
    after a reopen. Those are PyROOT's properties and no fake can speak to them.
    """

    def __init__(self, value):
        self._v = value
        self._name = None
        self.written = False

    def GetVal(self):
        return self._v

    def Write(self):
        self.written = True
        _FAKE_ROOT.current._keys[self._name] = self          # ROOT writes into the current directory
        return 1


class _FakeTH1D:
    def __init__(self, name, title, nbins, lo, hi):
        self.name, self.title, self.nbins = name, title, nbins
        self.contents = {}
        self.written = False

    def SetBinContent(self, i, v):
        self.contents[i] = v

    def Write(self):
        self.written = True
        _FAKE_ROOT.current._keys[self.name] = self
        return 1


class _FakeTH2D:
    """Square, diagonal-only. `_read_diagonal` uses GetNbinsX + GetBinContent(i,i) and nothing else."""

    def __init__(self, diag):
        self._d = list(diag)

    def GetNbinsX(self):
        return len(self._d)

    def GetBinContent(self, i, j):
        return self._d[i - 1] if i == j else 0.0


class _FakeTFile:
    """A `TFile` stand-in that RECORDS ITS OWN OPEN/CLOSE EVENTS, which is lane C's N4.

    `_path` is stamped on by `_FakeROOTModule.__init__`, so a file object knows which path it is
    reachable under and a close can be attributed. `Close()` appends to the module's event log rather
    than only setting a flag: the wrapper's stated discipline is an ORDERING ("every read completes
    and closes BEFORE the output is opened") and a per-file boolean cannot express an ordering. C
    removed `f.Close()` from `_read_diagonal` and all 50 tests stayed green precisely because the only
    observable was a flag nobody read.
    """

    def __init__(self, keys, writable=True, zombie=False):
        self._keys = dict(keys)
        self._writable, self._zombie = writable, zombie
        self.closed = False
        self._path = None

    def Get(self, k):
        return self._keys.get(k)          # None is falsy, which is how the wrapper tests presence

    def IsZombie(self):
        return self._zombie

    def IsWritable(self):
        return self._writable

    def cd(self):
        _FAKE_ROOT.current = self
        return True

    def Close(self):
        self.closed = True
        if _FAKE_ROOT is not None:
            _FAKE_ROOT.events.append(("close", self._path))


class _FakeROOTModule:
    """Minimal `ROOT` stand-in, installed into `sys.modules` for the duration of a test.

    IT MODELS TWO DOCUMENTED BEHAVIOURS AND VERIFIES NEITHER: that `Open` re-points the current
    directory, and that `Write()` lands in the current directory. They are modelled so that the
    wrapper's OWN discipline (read-then-close before opening the output; `fo.cd()` before writing) is
    exercised against something -- not so that ROOT's semantics are established. If PyROOT differs,
    these tests still pass and the wrapper can still be wrong. That is stated here rather than
    discovered later.
    """

    kError = 0

    def __init__(self, files):
        self.files = dict(files)          # path -> _FakeTFile
        for _p, _f in self.files.items():
            _f._path = _p                 # so a Close() can be ATTRIBUTED, not merely counted
        self.current = None
        self.opened = []                  # (path, mode)
        self.events = []                  # ("open", path, mode) | ("close", path), IN ORDER
        self.gErrorIgnoreLevel = 0
        outer = self

        class _TFile:
            @staticmethod
            def Open(path, mode=""):
                outer.opened.append((path, mode))
                outer.events.append(("open", path, mode))
                f = outer.files.get(path)
                if f is None:
                    return None
                outer.current = f
                return f
        self.TFile = _TFile

    def leaked(self):
        """Paths opened and never closed, IN ORDER. The observable N4 needed and did not have."""
        out = []
        for e in self.events:
            if e[0] == "open" and e[1] in self.files:
                out.append(e[1])
            elif e[0] == "close" and e[1] in out:
                out.remove(e[1])
        return out

    def open_while_unclosed(self):
        """(path, still_open) for every open issued while an EARLIER open had not been closed.

        This is the wrapper's read-then-close discipline stated as a property rather than as prose:
        `adopt_unified_5d.py:97-102` records that `TFile.Open` re-points ROOT's global current
        directory, so a second open with a first still live is the exact configuration in which a
        later `Write()` lands in the wrong file. MODELLED, NOT CONFIRMED -- see this class's docstring.
        """
        live, bad = [], []
        for e in self.events:
            if e[0] == "open":
                if live:
                    bad.append((e[1], tuple(live)))
                if e[1] in self.files:
                    live.append(e[1])
            elif e[1] in live:
                live.remove(e[1])
        return bad

    def TParameter(self, kind):
        def _make(name, value):
            p = _FakeParam(value)
            p._name, p._kind = name, kind
            return p
        return _make

    def TH1D(self, *a):
        return _FakeTH1D(*a)


_FAKE_ROOT = None


class _WithFakeROOT:
    """Install the fake for one test. `mii_adopt_unified_5d_stamped` imports ROOT lazily INSIDE each
    function, which is what makes injection through `sys.modules` possible at all."""

    def __init__(self, files):
        self.files = files

    def __enter__(self):
        global _FAKE_ROOT
        _FAKE_ROOT = _FakeROOTModule(self.files)
        self._saved = sys.modules.get("ROOT")
        sys.modules["ROOT"] = _FAKE_ROOT
        return _FAKE_ROOT

    def __exit__(self, *e):
        global _FAKE_ROOT
        if self._saved is None:
            sys.modules.pop("ROOT", None)
        else:
            sys.modules["ROOT"] = self._saved
        _FAKE_ROOT = None
        return False


#: THE REAL VALUE, from VL1 via lane C. The whole D1 defect is that `int()` of this is 0.
VL1_SQRT_TR_OLD = 4.357790406860002e-38


class D1_TheAnchorIsReadAsADoubleThroughTheProducer(unittest.TestCase):
    """LANE C's D1, AND THE REASON MY FIRST 34 TESTS HAD NO POWER HERE.

    `TheDiagonalIsTiedToTheProduct` handed `assert_diag_matches_sqrt_tr_old` a `math.sqrt(...)` -- a
    FLOAT -- while `main` obtained the same argument through a reader that coerced it with `int()`. The
    assertion was therefore tested on a value its own caller could never produce, and C's mutation
    *fixing* the defect left all 34 tests green: no power in either direction.

    THE FIXTURE IS BUILT FROM THE PRODUCER. Every test here starts from the bytes-side value and reaches
    the assertion the way `main` does, through the reader, so the coercion is INSIDE the circuit under
    test rather than outside it.
    """

    def test_int_of_the_real_anchor_IS_ZERO_which_is_the_whole_defect(self):
        """Stated as an arithmetic fact first, so the rest of the class is not arguing about it."""
        self.assertEqual(int(VL1_SQRT_TR_OLD), 0)
        self.assertNotEqual(VL1_SQRT_TR_OLD, 0.0)

    def test_the_DOUBLE_READER_returns_the_value_UNNARROWED(self):
        with _WithFakeROOT({"out.root": _FakeTFile({"sqrt_tr_old": _FakeParam(VL1_SQRT_TR_OLD)})}):
            v = W._read_double_scalar("out.root", "sqrt_tr_old")
        self.assertIsInstance(v, float)
        self.assertEqual(v, VL1_SQRT_TR_OLD, "no narrowing, no rounding, no coercion")

    def test_the_INT_READER_REFUSES_the_anchor_instead_of_TRUNCATING_it(self):
        """THE GUARD THAT KILLS THE CLASS RATHER THAN THE INSTANCE. A future caller reaching for the
        wrong reader gets an error naming the key; the old reader returned 0 and carried on."""
        with _WithFakeROOT({"out.root": _FakeTFile({"sqrt_tr_old": _FakeParam(VL1_SQRT_TR_OLD)})}):
            with self.assertRaises(SystemExit) as cm:
                W._read_int_scalars("out.root", ("sqrt_tr_old",))
        msg = str(cm.exception)
        self.assertIn("sqrt_tr_old", msg)
        self.assertIn("NON-INTEGRAL", msg)
        self.assertIn("_read_double_scalar", msg, "and it must name the reader to use instead")

    def test_the_INT_READER_still_reads_GENUINE_INTS(self):
        """The narrowing gets a test that it does NOT fire: all three identity keys are TParameter(int)
        and must come back as ints, including the legitimate 0."""
        keys = {"estimator_seed": _FakeParam(1242), "est_seed_offset": _FakeParam(1200),
                "est_seed_offset_declared": _FakeParam(1)}
        with _WithFakeROOT({"c.root": _FakeTFile(keys)}):
            got = W._read_int_scalars("c.root", W.LEG_IDENTITY_KEYS)
        self.assertEqual(got, {"estimator_seed": 1242, "est_seed_offset": 1200,
                              "est_seed_offset_declared": 1})
        with _WithFakeROOT({"c.root": _FakeTFile({"est_seed_offset": _FakeParam(0)})}):
            self.assertEqual(W._read_int_scalars("c.root", ("est_seed_offset", "absent")),
                             {"est_seed_offset": 0, "absent": None})

    def test_the_ASSERTION_REFUSES_an_INT_ANCHOR_and_BLAMES_THIS_WRAPPER(self):
        """The second line of defence, and the direction of the accusation is the point. An int-typed
        anchor is a defect in this wrapper; the message must say so instead of comparing and then
        blaming an input file."""
        with self.assertRaises(SystemExit) as cm:
            W.assert_diag_matches_sqrt_tr_old(1.9e-75, 0)
        msg = str(cm.exception)
        self.assertIn("TRUNCATED TO ZERO", msg)
        self.assertIn("not in any input file", msg)
        with self.assertRaises(SystemExit):
            W.assert_diag_matches_sqrt_tr_old(1.9e-75, True)   # bool is an int in Python

    def test_the_FULL_PRODUCER_CHAIN_at_the_REAL_MAGNITUDE_PASSES(self):
        """THE TEST WHOSE ABSENCE WAS THE DEFECT. Value -> reader -> assertion, at 4.36e-38.

        Under the old coercion this raises; it is the direct regression test for D1 and the one C's M1
        mutation would flip.
        """
        n = 5
        diag = [VL1_SQRT_TR_OLD ** 2 / n] * n
        with _WithFakeROOT({"out.root": _FakeTFile({"sqrt_tr_old": _FakeParam(VL1_SQRT_TR_OLD)}),
                            "c.root": _FakeTFile({"hCov_combined5d_total": _FakeTH2D(diag)})}):
            anchor = W._read_double_scalar("out.root", "sqrt_tr_old")
            raw, _clipped = W._read_diagonal("c.root")
        self.assertTrue(W.assert_diag_matches_sqrt_tr_old(float(raw.sum()), anchor))


class _MainWithStubbedChild:
    """The `main`-level fixture, as a MIXIN rather than a base class carrying tests.

    Round 3 needed two more `main`-scope classes (N4's ordering, Q3's message). Inheriting from the
    class below would have re-run its five tests inside each of them -- three copies of every result,
    which is how a suite comes to report power it does not have. A mixin shares the fixture and shares
    no assertions. It is also the only copy of the stub set: a second `_files` would drift.
    """

    def _files(self, anchor, diag, out_keys=None):
        out = dict(out_keys or {})
        out["sqrt_tr_old"] = _FakeParam(anchor)
        legs = {"estimator_seed": _FakeParam(1242), "est_seed_offset": _FakeParam(1200),
                "est_seed_offset_declared": _FakeParam(1)}
        legs2 = dict(legs, estimator_seed=_FakeParam(2200))
        return {"o.root": _FakeTFile(out),
                "c.root": _FakeTFile(dict(legs, hCov_combined5d_total=_FakeTH2D(diag))),
                "u.root": _FakeTFile(legs2)}

    def _run(self, files, env_offset="1200"):
        import subprocess as sp
        saved_call, saved_exists = sp.call, os.path.exists
        saved_env = os.environ.get("MNV_EST_SEED_OFFSET")
        calls = []
        sp.call = lambda argv, *a, **k: calls.append(argv) or 0
        os.path.exists = lambda p: True if p == "o.root" else saved_exists(p)
        if env_offset is None:
            os.environ.pop("MNV_EST_SEED_OFFSET", None)
        else:
            os.environ["MNV_EST_SEED_OFFSET"] = env_offset
        try:
            with _WithFakeROOT(files) as R:
                W.main(["--uthrow", "u.root", "--combined", "c.root", "--out", "o.root"])
            return calls, R
        finally:
            sp.call, os.path.exists = saved_call, saved_exists
            if saved_env is None:
                os.environ.pop("MNV_EST_SEED_OFFSET", None)
            else:
                os.environ["MNV_EST_SEED_OFFSET"] = saved_env


class D1_MainSucceedsOnARealAnchorAndTheRefusalAccusesNobody(_MainWithStubbedChild, unittest.TestCase):
    """`main` end to end, with the child stubbed. Covers C's M4 (the TOCTOU closure call deleted from
    `main` outright) and M5 (the unclipped diagonal stamped), neither of which any pure-function test
    can reach -- both are facts about `main`'s call graph."""

    def test_main_COMPLETES_at_the_REAL_5D_MAGNITUDE_and_stamps_all_seven_keys(self):
        """THE HEADLINE REGRESSION. C's finding was "the wrapper cannot succeed on any real product";
        this is that sentence turned into a test, at VL1's own value."""
        n = 4
        diag = [VL1_SQRT_TR_OLD ** 2 / n] * n
        files = self._files(VL1_SQRT_TR_OLD, diag)
        calls, R = self._run(files)
        self.assertEqual(len(calls), 1, "the pinned writer must be invoked exactly once")
        self.assertIn("adopt_unified_5d.py", calls[0][1])
        landed = files["o.root"]._keys
        for k in W.STAMPED_SCALAR_KEYS:
            self.assertIn(k, landed, f"{k} did not land")
        self.assertIn(W.STAMPED_HISTOGRAM_KEY, landed)
        self.assertEqual(landed["est_seed_offset"].GetVal(), 1200)
        self.assertEqual(landed["upstream_estimator_seed_g1"].GetVal(), 1242)
        self.assertEqual(landed["upstream_estimator_seed_g2"].GetVal(), 2200)
        # and the output was reopened UPDATE, after both inputs were read
        self.assertEqual(R.opened[-1], ("o.root", "UPDATE"))

    def test_main_STAMPS_THE_CLIPPED_DIAGONAL_not_the_raw_one(self):
        """C's M5. A negative diagonal entry must reach the artifact as 0. The anchor is built from the
        RAW trace, because that is what `adopt_unified_5d.py:127` traces -- so this also pins that the
        two are deliberately different quantities rather than an oversight."""
        import math
        diag = [3e-76, -1e-76, 5e-76, 2e-76]
        anchor = math.sqrt(sum(diag))
        files = self._files(anchor, diag)
        self._run(files)
        h = files["o.root"]._keys[W.STAMPED_HISTOGRAM_KEY]
        self.assertEqual(h.nbins, 4)
        self.assertEqual(h.contents[2], 0.0, "the negative entry must be CLIPPED in the artifact")
        self.assertEqual(h.contents[1], 3e-76)
        self.assertEqual(h.contents[3], 5e-76)
        self.assertTrue(h.written)

    def test_main_ACTUALLY_CALLS_the_TOCTOU_closure(self):
        """C's M4: the closure I advertise as the compensating benefit for the extra 0.915 GB read could
        be DELETED FROM `main` and the whole suite stayed green. The only way to catch a deleted call is
        to make a mismatch reach `main` and require the refusal."""
        diag = [1e-76] * 4
        files = self._files(VL1_SQRT_TR_OLD, diag)       # anchor^2 = 1.9e-75, trace = 4e-76: mismatch
        with self.assertRaises(SystemExit) as cm:
            self._run(files)
        self.assertIn("DISAGREE", str(cm.exception))
        self.assertEqual(files["o.root"]._keys.keys() & set(W.STAMPED_SCALAR_KEYS), set(),
                         "and it must refuse BEFORE writing anything")

    def test_the_REFUSAL_DOES_NOT_ACCUSE_THE_41GB_INTERMEDIATE(self):
        """LANE C's SECOND HALF OF D1, AND IT IS THE PART THAT COULD HAVE COST 2.087 TiB.

        The old message ended "The combined intermediate is not the matrix this product was built from",
        and the coercion defect made that the wrapper's DEFAULT output on every real product -- a false
        corruption finding aimed at the one artifact that cannot be cheaply regenerated. The message must
        report a DISAGREEMENT, put this wrapper first among the causes, and forbid acting on it.
        """
        diag = [1e-76] * 4
        with self.assertRaises(SystemExit) as cm:
            self._run(self._files(VL1_SQRT_TR_OLD, diag))
        msg = str(cm.exception)
        self.assertIn("DISAGREE", msg)
        self.assertIn("does NOT establish which side is wrong", msg)
        self.assertIn("DO NOT DELETE, REGENERATE OR RE-STAGE", msg)
        # ============================== BEN-510 FIRED ON ITS OWN FILING ==============================
        # This line read `assertIn("NOTHING HAS BEEN WRITTEN", msg)` and lane C's Q3(a) residual is that
        # the sentence is TRUE OF THE STAMP AND FALSE OF THE PRODUCT. So fixing the message REQUIRED
        # editing this assertion -- the second time in two rounds that a defect was a requirement of the
        # green suite, and it happened while filing the finding about it. The replacement asserts the
        # PROPERTY (the message must not claim nothing was written, and must say what does exist)
        # instead of the sentence, which is the check `BEN-510` carries.
        self.assertNotIn("NOTHING HAS BEEN WRITTEN", msg)
        self.assertIn("EXISTS", msg, "it must say the child's product exists")
        self.assertIn("(1) THIS WRAPPER", msg, "this wrapper must be the FIRST cause listed")
        for accusation in ("is not the matrix this product was built from",
                           "refusing to write hDiagCombinedOld from it"):
            self.assertNotIn(accusation, msg, "the old accusation must be gone, not softened")

    def test_main_reads_the_ANCHOR_with_the_DOUBLE_reader(self):
        """The call-site regression for D1, asserted at the call site rather than inferred from a pass:
        `main` must not route the anchor through the int reader again."""
        src = (ND / "mii_adopt_unified_5d_stamped.py").read_text()
        body = src.split("def main(")[1]
        self.assertIn("_read_double_scalar(a.out, TRACE_ANCHOR_KEY)", body)
        self.assertNotIn("_read_int_scalars(a.out", body)


class TheStampWriteDecisions(unittest.TestCase):
    """C's M6 (double-stamp refusal deleted), M7 (read-back deleted) and M8 (read-only guard deleted).

    These are decisions `_stamp_output` makes given what the file object answers, so they are testable
    against the fake -- but ONLY as decisions. See `_FakeROOTModule` for what that does and does not
    establish: nothing here shows a real reopen works, only that the wrapper reacts correctly to the
    answers PyROOT's API is documented to give.
    """

    PAIRS = [("est_seed_offset_declared", 1), ("est_seed_offset", 1200)]
    DIAG = [1.0, 2.0]

    def test_a_READ_ONLY_reopen_is_REFUSED(self):
        f = _FakeTFile({}, writable=False)
        with _WithFakeROOT({"o.root": f}):
            with self.assertRaises(SystemExit) as cm:
                W._stamp_output("o.root", self.PAIRS, self.DIAG)
        self.assertIn("cannot reopen", str(cm.exception))
        self.assertEqual(f._keys, {}, "and nothing may be attempted against it")

    def test_a_ZOMBIE_reopen_is_REFUSED(self):
        with _WithFakeROOT({"o.root": _FakeTFile({}, zombie=True)}):
            with self.assertRaises(SystemExit) as cm:
                W._stamp_output("o.root", self.PAIRS, self.DIAG)
        self.assertIn("cannot reopen", str(cm.exception))

    def test_a_SECOND_STAMP_is_REFUSED_rather_than_appending_a_CYCLE(self):
        """ROOT appends a new cycle instead of replacing a key, so a re-run would leave two answers to
        one question inside a citable artifact. This is the guard firing."""
        f = _FakeTFile({"est_seed_offset": _FakeParam(999)})
        with _WithFakeROOT({"o.root": f}):
            with self.assertRaises(SystemExit) as cm:
                W._stamp_output("o.root", self.PAIRS, self.DIAG)
        msg = str(cm.exception)
        self.assertIn("already carries", msg)
        self.assertIn("est_seed_offset", msg)
        self.assertEqual(f._keys["est_seed_offset"].GetVal(), 999, "and the existing key is untouched")

    def test_a_FAILED_WRITE_is_CAUGHT_BY_THE_READ_BACK_not_reported_as_success(self):
        """`adopt_unified_5d.py:212-219` records the writer printing "provenance stamped" while all nine
        writes had silently failed into a read-only file. The read-back is the whole defence, so it gets
        a test in which the writes silently land somewhere else."""
        sink = _FakeTFile({})

        class _Deaf(_FakeTFile):
            """`cd()` lands on a DIFFERENT directory -- BEN-106's exact hazard, modelled. The writes all
            "succeed" and none of them reach the file the wrapper thinks it opened."""

            def cd(self):
                _FAKE_ROOT.current = sink
                return True
        f = _Deaf({})
        with _WithFakeROOT({"o.root": f}):
            with self.assertRaises(SystemExit) as cm:
                W._stamp_output("o.root", self.PAIRS, self.DIAG)
        self.assertEqual(f._keys, {}, "the target file got nothing")
        self.assertIn("est_seed_offset", sink._keys, "and the writes went somewhere else entirely")
        msg = str(cm.exception)
        self.assertIn("did not land", msg)
        self.assertIn("est_seed_offset", msg)

    def test_the_HAPPY_PATH_writes_every_key_and_the_histogram(self):
        """The narrowing's own direction: with a writable file and working writes, none of the three
        guards may fire."""
        f = _FakeTFile({})
        with _WithFakeROOT({"o.root": f}):
            self.assertTrue(W._stamp_output("o.root", self.PAIRS, self.DIAG))
        self.assertEqual(f._keys["est_seed_offset"].GetVal(), 1200)
        self.assertEqual(f._keys[W.STAMPED_HISTOGRAM_KEY].contents, {1: 1.0, 2: 2.0})
        self.assertTrue(f.closed, "and the file is closed on the way out")


# =====================================================================================================
# ROUND 3, from lane C's PASS-WITH-SCOPE residuals. Nothing here is a new feature: each class pins a
# claim that was TRUE WHEN WRITTEN and had no test, which is the only reason it could go false.
# =====================================================================================================


def _fake_is_installable():
    """Derive -- do not grep -- whether this module actually installs a ROOT double.

    A `grep` for "sys.modules" would be a claim about this file's TEXT. Entering the context manager
    and observing `sys.modules["ROOT"]` is a claim about its BEHAVIOUR, and behaviour is what a reader
    of the wrapper's caveat is being told about. `BEN-482`: a regex over source cannot tell a call from
    prose about a call, and this file is now full of prose about the double.
    """
    before = sys.modules.get("ROOT")
    with _WithFakeROOT({}):
        installed = sys.modules.get("ROOT")
    return installed is not None and sys.modules.get("ROOT") is before


class TheCaveatMustAGREE_WITH_WHETHER_A_DOUBLE_EXISTS(unittest.TestCase):
    """LANE C's REQUIRED CORRECTION, TURNED INTO THE CHECK THAT WOULD HAVE CAUGHT IT.

    `mii_adopt_unified_5d_stamped.py:43` read "No ROOT test double is provided" for a day after the
    double landed -- and it was the SAME COMMIT that added the double which edited that paragraph, to
    rename the two readers, leaving the sentence its own change falsified. C's reason this is required
    rather than cosmetic: a reader who believes it concludes that 50 green tests are double-free pure
    logic, so the caveat overstates the suite in the direction that flatters it.

    WHY THIS IS NOT JUST ANOTHER SENTENCE ASSERTION (`BEN-510`). The property has a LIVE OPERAND ON
    BOTH SIDES: whether a double is installable is derived by installing one, and the name it must be
    called by is read off the class object rather than typed here, so renaming `_FakeROOTModule`
    FAILS this test instead of quietly rotting the paragraph. The residual is stated in `BEN-510`
    itself: the denial check below is still a substring, pointed at a safety property.
    """

    def _paragraph(self):
        src = (ND / "mii_adopt_unified_5d_stamped.py").read_text()
        self.assertIn("WHAT IS *NOT* ESTABLISHED", src)
        return src.split("WHAT IS *NOT* ESTABLISHED")[1].split('"""')[0]

    def test_the_double_is_INSTALLABLE_which_is_the_premise_of_this_class(self):
        self.assertTrue(_fake_is_installable(),
                        "if this fails the double is gone and the caveat must be re-derived, not kept")

    def test_the_caveat_NAMES_the_double_BY_ITS_LIVE_CLASS_NAME(self):
        para = self._paragraph()
        self.assertIn(_FakeROOTModule.__name__, para,
                      "the wrapper's WHAT IS *NOT* ESTABLISHED paragraph must name the double that "
                      "exists. Renaming the class without updating the paragraph lands here, which is "
                      "the point: the operand is the class object, not a string I typed twice.")

    def test_the_caveat_DOES_NOT_DENY_a_double_that_exists(self):
        """The negation direction. A safety-property substring assertion -- see `BEN-510`'s residual."""
        para = self._paragraph()
        for denial in ("No ROOT test double is provided", "No ROOT double is provided",
                       "no ROOT test double"):
            self.assertNotIn(denial, para,
                             f"the paragraph denies a double that {_FakeROOTModule.__name__} provides")

    def test_the_caveat_STILL_STATES_WHAT_THE_DOUBLE_DOES_NOT_ESTABLISH(self):
        """The valuable half of the old text. Correcting a falsehood must not delete the true part --
        a paragraph that admits a double and stops there is worse than the one C flagged."""
        para = self._paragraph()
        self.assertIn("CONFIRMS NEITHER", para)
        self.assertIn("these tests still pass and this wrapper can still be wrong", para)

    def test_THIS_FILES_OWN_DOCSTRING_carries_the_same_obligation(self):
        """It carried the identical false sentence and lane C did not cite it, because C cited the line
        it measured. The mechanism does not care which file it is in."""
        doc = __doc__ or ""
        self.assertNotIn("No ROOT double is provided", doc)
        self.assertIn(_FakeROOTModule.__name__, doc)


class N4_TheReadThenCloseDisciplineIsACTUALLY_EXERCISED(unittest.TestCase):
    """LANE C's N4, AND IT IS A DEFENCE-OF-THE-FAKE CLAIM RATHER THAN A COVERAGE STATISTIC.

    The wrapper's own comment in `main` says "EVERY READ COMPLETES AND CLOSES BEFORE THE OUTPUT IS
    OPENED", citing `adopt_unified_5d.py:97-102`'s measured warning that `TFile.Open` re-points ROOT's
    global current directory. Lane B's defence of the fake said that discipline was exercised. C
    measured: the `fo.cd()` half was, the close half was NOT -- `f.Close()` deleted from
    `_read_diagonal` left all 50 tests green. So the claim was standing on nothing.

    WHY A PER-FILE BOOLEAN WAS NEVER GOING TO CATCH IT: the discipline is an ORDERING between two
    files, and `_FakeTFile.closed` cannot express an ordering. The fake now records an EVENT LOG and
    these tests assert the order. MODELLED, NOT CONFIRMED: that a live read handle actually diverts a
    later `Write()` is PyROOT's property and no double establishes it.
    """

    def test_read_diagonal_CLOSES_THE_41GB_FILE_IT_OPENED(self):
        diag = [1e-76] * 4
        f = _FakeTFile({"hCov_combined5d_total": _FakeTH2D(diag)})
        with _WithFakeROOT({"c.root": f}) as R:
            W._read_diagonal("c.root")
        self.assertEqual(R.leaked(), [], "the combined intermediate was left open")
        self.assertIn(("close", "c.root"), R.events)

    def test_read_diagonal_CLOSES_IT_EVEN_WHEN_IT_REFUSES(self):
        """The refusal path is the one that matters most: it fires against the 41.44 GB file, and a
        leaked handle there is the wrapper holding open the artifact nobody may disturb."""
        with _WithFakeROOT({"c.root": _FakeTFile({})}) as R:      # no histogram -> _fail
            with self.assertRaises(SystemExit):
                W._read_diagonal("c.root")
        self.assertEqual(R.leaked(), [], "refusing must not leak the handle")

    def test_BOTH_SCALAR_READERS_CLOSE_TOO(self):
        keys = {"estimator_seed": _FakeParam(1242), "est_seed_offset": _FakeParam(1200),
                "est_seed_offset_declared": _FakeParam(1)}
        with _WithFakeROOT({"u.root": _FakeTFile(keys)}) as R:
            W._read_int_scalars("u.root", W.LEG_IDENTITY_KEYS)
        self.assertEqual(R.leaked(), [])
        with _WithFakeROOT({"o.root": _FakeTFile({"sqrt_tr_old": _FakeParam(VL1_SQRT_TR_OLD)})}) as R:
            W._read_double_scalar("o.root", "sqrt_tr_old")
        self.assertEqual(R.leaked(), [])


class N4_MainNeverHoldsTwoFilesOpenAtOnce(_MainWithStubbedChild, unittest.TestCase):
    """The same discipline at `main`'s scope, which is where the comment claiming it lives.

    Inherits `_files`/`_run` rather than re-deriving the stub set: a second copy of that fixture is a
    second thing to drift, and the campaign's own lesson is that a re-typed operand diverges silently.
    """

    def test_EVERY_READ_IS_CLOSED_BEFORE_THE_OUTPUT_IS_OPENED_FOR_UPDATE(self):
        n = 4
        diag = [VL1_SQRT_TR_OLD ** 2 / n] * n
        _calls, R = self._run(self._files(VL1_SQRT_TR_OLD, diag))
        self.assertEqual(R.open_while_unclosed(), [],
                         "an open was issued while an earlier file was still open -- the exact "
                         "configuration adopt_unified_5d.py:97-102 warns diverts a later Write()")
        idx_update = R.events.index(("open", "o.root", "UPDATE"))
        closes = {e[1] for e in R.events[:idx_update] if e[0] == "close"}
        for path in ("u.root", "c.root", "o.root"):
            self.assertIn(path, closes, f"{path} was still open when the output was reopened UPDATE")

    def test_THE_OUTPUT_IS_CLOSED_AT_THE_END_TOO(self):
        n = 4
        diag = [VL1_SQRT_TR_OLD ** 2 / n] * n
        _calls, R = self._run(self._files(VL1_SQRT_TR_OLD, diag))
        self.assertEqual(R.leaked(), [], "nothing may be left open when main returns")


class Q1_TheIntReaderGuardIsVALUE_BASED(unittest.TestCase):
    """LANE C's Q1 RESIDUAL, RULED SAFE **WITH A TRIGGER** -- SO THE TRIGGER IS THIS CLASS.

    C's ruling: `float(raw) != int(raw)` discriminates on VALUE, not TYPE, so an integral-valued
    `double` still coerces silently. It is unreachable today because `_read_int_scalars` has two call
    sites and serves only `LEG_IDENTITY_KEYS`, all genuine `TParameter("int")`. **TRIGGER TO REVISIT: a
    third call site, or any key added to `LEG_IDENTITY_KEYS`.**

    LANE B's DECISION, RECORDED RATHER THAN MADE SILENTLY: the guard stays value-based. The complete
    fix asserts the object's ROOT class, no double in this repository can test a ROOT-class assertion,
    and an untested NARROWING on the only production path fails closed on every legitimate key if
    PyROOT's class string is not what I guessed -- turning a residual C ruled safe into a live outage.
    What IS done: `inf`/`nan` now fail closed NAMING THE KEY, and this class makes the trigger
    executable. A narrated trigger is read by the last person who needs it (`FINDINGS.md`'s block cell
    has gone stale twice for exactly this reason); a failing test is read by the first.
    """

    #: The call sites C measured, by the function each sits in. Derived from the AST, never grepped
    #: -- `BEN-482`: a regex cannot tell a call from the several paragraphs of prose about this call.
    EXPECTED_CALLERS = {"main"}
    EXPECTED_N_CALL_SITES = 2

    def _call_sites(self):
        tree = ast.parse((ND / "mii_adopt_unified_5d_stamped.py").read_text())
        sites = []
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(fn):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                        and node.func.id == "_read_int_scalars"):
                    sites.append(fn.name)
        return sites

    def test_the_int_reader_STILL_HAS_EXACTLY_TWO_CALL_SITES_BOTH_IN_MAIN(self):
        sites = self._call_sites()
        self.assertEqual(set(sites), self.EXPECTED_CALLERS)
        self.assertEqual(len(sites), self.EXPECTED_N_CALL_SITES,
                         "TRIGGER HIT (lane C, round 2): `_read_int_scalars`'s guard is VALUE-based, "
                         "so an integral-valued double passes it and is coerced silently. It was ruled "
                         "safe only because the reader served these call sites over keys known to be "
                         "TParameter ints. A new call site must either prove its keys are ints on the "
                         "bytes side or make the guard TYPE-based first. Do not just update this "
                         "number.")

    def test_LEG_IDENTITY_KEYS_IS_STILL_EXACTLY_THE_THREE_GENUINE_INT_KEYS(self):
        self.assertEqual(W.LEG_IDENTITY_KEYS,
                         ("estimator_seed", "est_seed_offset", "est_seed_offset_declared"),
                         "TRIGGER HIT: every key here is read through the VALUE-guarded int reader. A "
                         "fourth key must be shown to be a TParameter int at its producer "
                         "(sweep_bank_5d.py:285-287, analyze_universes_5d.py:277, "
                         "unified_throw_cov.py:545,550-551) before it is added.")

    def test_an_INF_FAILS_CLOSED_AND_NAMES_THE_KEY(self):
        """C measured an uncaught `OverflowError` naming nothing, in the wrapper whose entire D1 lesson
        is what a failure SAYS. The property asserted is NAMING, not wording."""
        with _WithFakeROOT({"c.root": _FakeTFile({"est_seed_offset": _FakeParam(float("inf"))})}):
            with self.assertRaises(SystemExit) as cm:
                W._read_int_scalars("c.root", ("est_seed_offset",))
        msg = str(cm.exception)
        self.assertIn("est_seed_offset", msg, "the message must name the KEY")
        self.assertIn("c.root", msg, "and the file it was read from")

    def test_a_NAN_FAILS_CLOSED_AND_NAMES_THE_KEY(self):
        with _WithFakeROOT({"c.root": _FakeTFile({"estimator_seed": _FakeParam(float("nan"))})}):
            with self.assertRaises(SystemExit) as cm:
                W._read_int_scalars("c.root", ("estimator_seed",))
        self.assertIn("estimator_seed", str(cm.exception))

    def test_a_NON_FINITE_READ_STILL_CLOSES_THE_FILE(self):
        """A new refusal is a new exit path, and an exit path that leaks a handle is a new defect."""
        with _WithFakeROOT({"c.root": _FakeTFile({"estimator_seed": _FakeParam(float("nan"))})}) as R:
            with self.assertRaises(SystemExit):
                W._read_int_scalars("c.root", ("estimator_seed",))
        self.assertEqual(R.leaked(), [])

    def test_THE_RESIDUAL_IS_STILL_REAL_AND_THIS_TEST_SAYS_SO(self):
        """An integral-valued double DOES still coerce. Asserted in the direction of the truth rather
        than left implicit, so nobody reads the two tests above as a claim that the class is closed."""
        with _WithFakeROOT({"c.root": _FakeTFile({"est_seed_offset": _FakeParam(3.0)})}):
            got = W._read_int_scalars("c.root", ("est_seed_offset",))
        self.assertEqual(got["est_seed_offset"], 3)
        self.assertIsInstance(got["est_seed_offset"], int)


class Q3_TheRefusalDistinguishesSTAMPfromPRODUCTandDISCRIMINATES(
        _MainWithStubbedChild, unittest.TestCase):
    """LANE C's Q3 RESIDUALS. The message was SAFE; these make it TRUE and DIAGNOSTIC.

    (a) "NOTHING HAS BEEN WRITTEN" is true of the stamp and FALSE of the product -- the child has
        already run and `--out`, ~892 MB, exists unstamped. A reader who believed it would go looking
        for a file that is already on disk.
    (b) No discriminator was offered for cause (3). C's own reasoning for why the message was safe
        anyway is that the prescribed action is correct under all three causes -- but a message that
        leaves the reader holding only the expensive hypothesis is how a do-not-delete banner
        eventually loses an argument. Both discriminators are READS.

    ASSERTED AS PROPERTIES WHERE POSSIBLE (`BEN-510`): that the stamp/product distinction is DRAWN,
    that a discriminator for (3) is OFFERED, that the banner SURVIVED. The substring assertions that
    remain are pointed at safety -- the accusation must be absent, the banner present -- which is the
    legitimate direction, and the brittleness is recorded in `BEN-510` rather than denied.
    """

    def _refusal(self):
        with self.assertRaises(SystemExit) as cm:
            self._run(self._files(VL1_SQRT_TR_OLD, [1e-76] * 4))
        return str(cm.exception)

    def test_it_DISTINGUISHES_THE_STAMP_FROM_THE_PRODUCT(self):
        msg = self._refusal()
        self.assertNotIn("NOTHING HAS BEEN WRITTEN", msg,
                         "false of the product: the child ran and --out exists")
        self.assertIn("NO STAMP HAS BEEN WRITTEN", msg)
        # the PROPERTY: the message must say the product EXISTS and is UNSTAMPED, in that order
        self.assertLess(msg.index("EXISTS"), msg.index("UNSTAMPED"))
        self.assertIn("--out", msg)

    def test_it_OFFERS_A_DISCRIMINATOR_FOR_CAUSE_3_AND_IT_IS_A_READ(self):
        msg = self._refusal()
        tail = msg[msg.index("(3)"):]
        self.assertIn("mtime", tail, "cause (3) must come with a way to kill or confirm it")
        self.assertIn("TO TELL (3)", tail)
        self.assertIn("re-run the child", tail)
        # and the discriminator must not itself invite a write
        for verb in ("delete", "regenerate", "re-stage", "truncate", "move"):
            self.assertNotIn(f"{verb} --combined", tail)

    def test_THE_BANNER_AND_THE_ORDERING_SURVIVED_BOTH_EDITS(self):
        """The regression that matters: an edit adding two paragraphs is exactly how a banner gets
        pushed out or a cause order gets shuffled."""
        msg = self._refusal()
        self.assertIn("DO NOT DELETE, REGENERATE OR RE-STAGE", msg)
        self.assertIn("41.44 GB", msg)
        self.assertIn("2.087 TiB", msg)
        self.assertLess(msg.index("(1) THIS WRAPPER"), msg.index("(2) --combined"))
        self.assertLess(msg.index("(2) --combined"), msg.index("(3) the combined intermediate changed"))
        for accusation in ("is not the matrix this product was built from",
                           "refusing to write hDiagCombinedOld from it"):
            self.assertNotIn(accusation, msg)

    def test_IT_STILL_REFUSES_BEFORE_WRITING_ANYTHING(self):
        files = self._files(VL1_SQRT_TR_OLD, [1e-76] * 4)
        with self.assertRaises(SystemExit):
            self._run(files)
        self.assertEqual(files["o.root"]._keys.keys() & set(W.STAMPED_SCALAR_KEYS), set())
        self.assertNotIn(W.STAMPED_HISTOGRAM_KEY, files["o.root"]._keys)


if __name__ == "__main__":
    unittest.main()
