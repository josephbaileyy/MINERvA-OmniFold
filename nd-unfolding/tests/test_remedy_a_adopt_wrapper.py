#!/usr/bin/env python3
"""Tests for remedy (A)'s wrapper, `mii_adopt_unified_5d_stamped.py`.

WHAT THESE TESTS DO AND DO NOT ESTABLISH, stated first because the boundary is the most useful thing
in this file. `import ROOT` raises `ModuleNotFoundError` on the lane-B host, so the wrapper's ROOT
path -- `_read_scalars`, `_read_diagonal`, `_stamp_output`, and `main` from the child launch onward --
IS NOT EXERCISED HERE AT ALL. No ROOT double is provided, deliberately: the three properties that
would need proving (a `RECREATE`d-and-closed file reopens `UPDATE`; new `TParameter` keys are accepted
on reopen; `TFile.Open` re-points the global current directory) are properties of PyROOT, and a stub
that cannot do what PyROOT does would be evidence about the stub. What IS proved here is every
decision the wrapper makes: which argv the child gets, which keys are derived, when the cross-member
refusal fires and when it must not, and that the pinned bytes are untouched.

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
    """

    def test_a_matching_trace_passes(self):
        import math
        self.assertTrue(W.assert_diag_matches_sqrt_tr_old(4.0, math.sqrt(4.0)))

    def test_a_DIFFERENT_MATRIX_is_refused(self):
        with self.assertRaises(SystemExit) as cm:
            W.assert_diag_matches_sqrt_tr_old(4.0, 3.0)
        self.assertIn("not the matrix this product was built from", str(cm.exception))

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


class TheROOTPathIsMarkedUNVERIFIED(unittest.TestCase):
    """A CLAIM ABOUT WHAT IS NOT ESTABLISHED IS STILL A CLAIM, so it gets a test too.

    These assert the DECLARATION, not the behaviour. They exist because the single most likely way this
    wrapper does damage is a later reader taking a green suite as evidence that the ROOT writes work.
    """

    def test_the_module_says_so_where_the_ROOT_code_is(self):
        src = (ND / "mii_adopt_unified_5d_stamped.py").read_text()
        self.assertIn("WHAT IS *NOT* ESTABLISHED", src)
        self.assertIn("CLUSTER-UNVERIFIED, EVERY LINE", src)
        for fn in ("_read_scalars", "_read_diagonal", "_stamp_output"):
            self.assertIn(f"def {fn}", src)
            self.assertIn("CLUSTER-UNVERIFIED", src.split(f"def {fn}")[1][:600],
                          f"{fn}'s own docstring must carry the marker; a banner scrolls away")

    def test_the_STAMP_COVERAGE_row_distinguishes_CAPABILITY_from_DEMONSTRATION(self):
        how = classes.STAMP_COVERAGE["mii_adopt_unified_5d_stamped.py"]["how"]
        self.assertIn("CLUSTER-UNVERIFIED", how)
        self.assertIn("2026-08-20", how, "and the claim is dated, since it is meant to expire")

    def test_ROOT_really_is_unavailable_here(self):
        """The premise of every caveat above. If this ever fails, the ROOT path can be tested for real
        and these caveats must be re-derived rather than kept."""
        try:
            import ROOT  # noqa: F401
        except ModuleNotFoundError:
            return
        self.skipTest("ROOT IS AVAILABLE on this host -- the wrapper's ROOT path is now testable and "
                      "the CLUSTER-UNVERIFIED markers in the module must be revisited, not trusted.")


if __name__ == "__main__":
    unittest.main()
