"""Negative controls for the C_stat^data predicates P1-P8, both sites.

WHY FIFTEEN CONTROLS AND WHY THEY ARE NOT OPTIONAL. The data-only path REPLACES a fail-closed
coherence guard (`fe.validate_coherent_bootstrap`, mandatory-key at :759, raising at :768) with its
own predicates. A REPLACEMENT THAT SILENTLY NEVER FIRES IS THE FORBIDDEN RELAXATION WITH EXTRA
STEPS (lane C, BEN-407). So every positive condition gets a control that MUTATES A SYNTHETIC STORE
and is shown to RAISE, with the unmutated store shown to PASS in the same test.

NEVER BY DISABLING THE CHECK. Each control perturbs the DATA the predicate reads, so it exercises
the shipped predicate rather than a stand-in.

THE PREDICATE IS EXTRACTED FROM THE SHIPPED FILE, NOT RETYPED. `cstat_data_only` is imported, so
the code under test is literally the code that ships; and `_source_of` additionally asserts the
function's source text is NON-EMPTY and carries its raise, because on the P5A launcher guards that
discipline caught an EMPTY extracted file exiting 0 -- a meaningless pass found only by printing a
line count.
"""
import ast
import hashlib
import inspect
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PET = HERE.parents[0] / "pet"
ND = HERE.parents[0]                      # pet_bootstrap lives here, and the loader imports it
for item in (str(PET), str(ND)):
    if item not in sys.path:
        sys.path.insert(0, item)

import cstat_data_only as cdo  # noqa: E402
import fullevent_fps_dataloader as fe  # noqa: E402

N_DATA, N_SIG, N_BKG = 100, 200, 50
SEED = 50_000


def _source_of(fn):
    """The shipped source of a predicate. Asserted non-empty by every caller."""
    src = inspect.getsource(fn)
    return src


class FakeMC:
    """Minimal stand-in for the loader's MC DataLoader: the three attributes P5 reads."""

    def __init__(self, weight, weight_reco, pass_reco):
        self.weight = np.asarray(weight, dtype=np.float32)
        self.weight_reco = np.asarray(weight_reco, dtype=np.float32)
        self.pass_reco = np.asarray(pass_reco, dtype=bool)


class FakeData:
    def __init__(self, weight, pass_reco):
        self.weight = np.asarray(weight, dtype=np.float32)
        self.pass_reco = np.asarray(pass_reco, dtype=bool)


def canonical_data_factor():
    return fe.coherent_bootstrap_factors(N_DATA, N_SIG, N_BKG, SEED)[0]


def good_store():
    return {
        "cstat_product": np.asarray(cdo.CSTAT_DATA_ONLY),
        "data_bootstrap_seed": np.asarray(SEED),
        "data_bootstrap_factor": canonical_data_factor(),
        "sig_bootstrap_factor_full": np.ones(N_SIG, dtype=np.uint8),
        "bkg_bootstrap_factor_full": np.ones(N_BKG, dtype=np.uint8),
    }


def check_streams(store):
    return cdo.assert_data_only_streams(
        store, data_bootstrap_seed=SEED, n_data_full=N_DATA,
        n_sig_full=N_SIG, n_bkg_full=N_BKG)


def good_ratio_block():
    return {"step1_class_ratio_loader_stamped": 1.25,
            "step1_class_ratio_applied": 1.27,
            "weights_embody": "step1_class_ratio_applied"}


def mc_pair(scale=None, thin=None, subnormal=False):
    """An unthinned MC leg, normalized exactly the way the loader normalizes it."""
    rng = np.random.default_rng(7)
    w_truth_full = rng.uniform(0.5, 2.0, N_SIG).astype(np.float32)
    w_reco_full = rng.uniform(0.5, 2.0, N_SIG).astype(np.float32)
    if subnormal:
        w_truth_full[3] = np.float32(1e-45)          # smallest positive subnormal
    imc = np.arange(0, N_SIG, 2, dtype=np.int64)     # a genuine subset, as production uses
    pr = np.zeros(imc.size, dtype=bool)
    pr[: imc.size // 2] = True
    expect_truth = w_truth_full[imc]
    expect_reco = w_reco_full[imc]
    c = np.float32(fe.STEP1_MC_NORMALIZATION / float(np.sum(expect_reco[pr])))
    if scale is not None:
        c = np.float32(c * scale)
    got_truth = (expect_truth * c).astype(np.float32)
    got_reco = (expect_reco * c).astype(np.float32)
    if thin is not None:
        got_truth = got_truth.copy()
        got_truth[thin] = 0.0
    return FakeMC(got_truth, got_reco, pr), w_truth_full, w_reco_full, imc


def check_mc(mc, w_truth_full, w_reco_full, imc, size=1):
    return cdo.assert_mc_leg_unthinned(mc, w_truth_full=w_truth_full,
                                       w_reco_full=w_reco_full, imc=imc, size=size)


class TrainSitePredicates(unittest.TestCase):
    """P1-P8 as applied at the TRAINING site (live, before the artifact is written)."""

    def setUp(self):
        for fn in (cdo.assert_data_only_streams, cdo.assert_mc_leg_unthinned,
                   cdo.assert_ratio_provenance_block, cdo.rescale_measured_to_data_only_R):
            src = _source_of(fn)
            self.assertTrue(src.strip(), f"{fn.__name__} source is EMPTY -- the extracted "
                                         f"predicate is meaningless and a pass proves nothing")
            self.assertIn("raise SystemExit", src,
                          f"{fn.__name__} carries no fail-closed raise")

    def test_positive_control_streams(self):
        self.assertTrue(check_streams(good_store()))

    def test_positive_control_ratio_block(self):
        self.assertTrue(cdo.assert_ratio_provenance_block(good_ratio_block()))

    def test_positive_control_mc_leg(self):
        rep = check_mc(*mc_pair())
        self.assertGreater(rep["derived_normalization_constant"], 0.0)
        self.assertIn("w_reco", rep["normalization_source_leg"])

    # ---- 1: P1, the product tag ----
    def test_P1_absent_tag_raises(self):
        s = good_store(); del s["cstat_product"]
        with self.assertRaises(SystemExit):
            check_streams(s)

    def test_P1_wrong_tag_raises(self):
        s = good_store(); s["cstat_product"] = np.asarray(cdo.CSTAT_THREE_STREAM)
        with self.assertRaises(SystemExit):
            check_streams(s)

    # ---- 2: P2, the signal factor is explicitly ones ----
    def test_P2_absent_raises(self):
        s = good_store(); del s["sig_bootstrap_factor_full"]
        with self.assertRaises(SystemExit):
            check_streams(s)

    def test_P2_poisson_instead_of_ones_raises(self):
        s = good_store()
        s["sig_bootstrap_factor_full"] = fe.coherent_bootstrap_factors(
            N_DATA, N_SIG, N_BKG, SEED)[1]
        with self.assertRaises(SystemExit):
            check_streams(s)

    def test_P2_wrong_length_raises(self):
        s = good_store()
        s["sig_bootstrap_factor_full"] = np.ones(N_SIG - 1, dtype=np.uint8)
        with self.assertRaises(SystemExit):
            check_streams(s)

    # ---- 3: P3, the background factor is explicitly ones ----
    def test_P3_absent_raises(self):
        s = good_store(); del s["bkg_bootstrap_factor_full"]
        with self.assertRaises(SystemExit):
            check_streams(s)

    def test_P3_not_ones_raises(self):
        s = good_store()
        bad = np.ones(N_BKG, dtype=np.uint8); bad[11] = 2
        s["bkg_bootstrap_factor_full"] = bad
        with self.assertRaises(SystemExit):
            check_streams(s)

    # ---- 4: P4, the coherence check SURVIVING, re-pointed at the data stream ----
    def test_P4_absent_raises(self):
        s = good_store(); del s["data_bootstrap_factor"]
        with self.assertRaises(SystemExit):
            check_streams(s)

    def test_P4_ones_instead_of_a_draw_raises(self):
        """The data stream is the one that MUST vary; unity here is the silent-failure case."""
        s = good_store(); s["data_bootstrap_factor"] = np.ones(N_DATA, dtype=np.uint8)
        with self.assertRaises(SystemExit):
            check_streams(s)

    def test_P4_wrong_seed_draw_raises(self):
        s = good_store()
        s["data_bootstrap_factor"] = fe.coherent_bootstrap_factors(
            N_DATA, N_SIG, N_BKG, SEED + 1)[0]
        with self.assertRaises(SystemExit):
            check_streams(s)

    # ---- 5: P5a, BIT-EXACT, the "nothing happened" limb ----
    def test_P5a_thinned_row_raises(self):
        mc, wt, wr, imc = mc_pair(thin=[5, 9, 17])
        with self.assertRaises(SystemExit) as cm:
            check_mc(mc, wt, wr, imc)
        self.assertIn("P5a", str(cm.exception))

    def test_P5a_flush_to_zero_raises_and_that_is_correct(self):
        """A subnormal destroyed by the rescale appears as a NEW zero and P5a must catch it.

        DO NOT repair this by excluding zero rows of mc.weight -- that exempts exactly the failure
        mode P5a exists for (lane C, BEN-409). float32(1e-45) * 0.5 == 0.0 exactly.
        """
        # The normalization constant must be < 1 for a subnormal to flush, so the reco leg is built
        # large enough to make it so -- c = 1e6 / sum(w_reco[pass_reco]). Constructed rather than
        # hoped for: a control that SKIPS because its premise did not arise is a control that did
        # not fire, which is the thing these fifteen exist to prevent.
        rng = np.random.default_rng(11)
        w_truth_full = rng.uniform(0.5, 2.0, N_SIG).astype(np.float32)
        # EVEN index, because imc below takes every second row -- an odd index would place the
        # subnormal outside the subset and the control would assert on a row P5 never sees.
        w_truth_full[4] = np.float32(1e-45)
        w_reco_full = rng.uniform(1.0e5, 2.0e5, N_SIG).astype(np.float32)
        imc = np.arange(0, N_SIG, 2, dtype=np.int64)
        pr = np.zeros(imc.size, dtype=bool)
        pr[: imc.size // 2] = True
        expect_truth, expect_reco = w_truth_full[imc], w_reco_full[imc]
        c = np.float32(fe.STEP1_MC_NORMALIZATION / float(np.sum(expect_reco[pr])))
        self.assertLess(float(c), 1.0, "premise: the constant must shrink for a flush to occur")
        mc = FakeMC((expect_truth * c).astype(np.float32),
                    (expect_reco * c).astype(np.float32), pr)
        # PREMISE ASSERTED, not assumed: the subnormal really did become a new zero.
        self.assertEqual(int(((np.asarray(mc.weight) == 0) & (expect_truth != 0)).sum()), 1)
        with self.assertRaises(SystemExit) as cm:
            check_mc(mc, w_truth_full, w_reco_full, imc)
        self.assertIn("P5a", str(cm.exception))

    # ---- 6: P5b, TOLERANCED CLOSURE, the "a computation happened" limb ----
    def test_P5b_wrong_normalization_constant_raises(self):
        mc, wt, wr, imc = mc_pair(scale=1.01)
        with self.assertRaises(SystemExit) as cm:
            check_mc(mc, wt, wr, imc)
        self.assertIn("P5b", str(cm.exception))

    def test_P5b_constant_derived_from_the_TRUTH_leg_would_pass_a_wrong_constant(self):
        """The NAMED control for the PLAUSIBLE mistake, which is the one that ships.

        dataloader.py:148 selects `_src = weight_reco` when a reco leg is supplied, so the loader's
        constant is 1e6/sum(w_reco[pass_reco]). Deriving it from the TRUTH leg gives a different
        number, and a predicate built that way would accept weights the loader never produced.
        This asserts the two constants genuinely DIFFER, so the shipped choice is load-bearing.
        """
        mc, wt, wr, imc = mc_pair()
        pr = np.asarray(mc.pass_reco)
        c_reco = fe.STEP1_MC_NORMALIZATION / float(np.sum(wr[imc][pr]))
        c_truth = fe.STEP1_MC_NORMALIZATION / float(np.sum(wt[imc][pr]))
        self.assertNotAlmostEqual(c_reco, c_truth, places=6)
        mc_wrong = FakeMC((wt[imc] * np.float32(c_truth)).astype(np.float32),
                          (wr[imc] * np.float32(c_truth)).astype(np.float32), pr)
        with self.assertRaises(SystemExit) as cm:
            check_mc(mc_wrong, wt, wr, imc)
        self.assertIn("P5b", str(cm.exception))

    def test_P5b_asserts_its_own_size_precondition(self):
        """sumw is over the RANK-SLICED array, so multi-rank makes the derived constant a
        different quantity. The predicate checks its own precondition rather than inheriting the
        launcher's guard -- BEN-386."""
        mc, wt, wr, imc = mc_pair()
        with self.assertRaises(SystemExit) as cm:
            check_mc(mc, wt, wr, imc, size=2)
        self.assertIn("size == 1", str(cm.exception))

    # ---- 7: P6, the seed under its own key ----
    def test_P6_absent_raises(self):
        s = good_store(); del s["data_bootstrap_seed"]
        with self.assertRaises(SystemExit):
            check_streams(s)

    def test_P6_minus_one_sentinel_is_not_silently_accepted(self):
        """BEN-405: -1 is this pipeline's no-bootstrap sentinel and an absent-default of -1 would
        compare -1 != -1 and pass vacuously. P6's own key makes that unreachable; asserted."""
        s = good_store(); s["data_bootstrap_seed"] = np.asarray(-1)
        with self.assertRaises(SystemExit):
            check_streams(s)

    # ---- 8: P7, both operands plus what the weights embody ----
    def test_P7_missing_any_of_three_raises(self):
        for key in ("step1_class_ratio_loader_stamped", "step1_class_ratio_applied",
                    "weights_embody"):
            block = good_ratio_block(); del block[key]
            with self.assertRaises(SystemExit):
                cdo.assert_ratio_provenance_block(block)

    def test_P7_weights_embody_must_name_the_applied_ratio(self):
        block = good_ratio_block()
        block["weights_embody"] = "step1_class_ratio_loader_stamped"
        with self.assertRaises(SystemExit):
            cdo.assert_ratio_provenance_block(block)

    # ---- 9: the measured-leg closure that carries the data draw into the normalization ----
    def test_measured_closure_positive_control(self):
        rng = np.random.default_rng(3)
        w = rng.uniform(0.5, 2.0, 400).astype(np.float32)
        pr = np.ones(400, dtype=bool)
        r_nom, r_do = 1.25, 1.27
        w *= np.float32(fe.STEP1_MC_NORMALIZATION * r_nom / float(np.sum(w[pr])))
        dl = FakeData(w, pr)
        rep = cdo.rescale_measured_to_data_only_R(dl, r_nominal=r_nom, r_data_only=r_do)
        self.assertLessEqual(rep["closure_abs_deviation"], rep["closure_tolerance"])

    def test_measured_closure_raises_when_the_rescale_is_wrong(self):
        rng = np.random.default_rng(3)
        w = rng.uniform(0.5, 2.0, 400).astype(np.float32)
        pr = np.ones(400, dtype=bool)
        r_nom, r_do = 1.25, 1.27
        w *= np.float32(fe.STEP1_MC_NORMALIZATION * r_nom / float(np.sum(w[pr])))
        dl = FakeData(w, pr)
        # a caller that mislabels which ratio the weights already embody
        with self.assertRaises(SystemExit):
            cdo.rescale_measured_to_data_only_R(dl, r_nominal=r_do, r_data_only=r_nom * 4)

    def test_measured_closure_refuses_a_nonpositive_ratio(self):
        dl = FakeData(np.ones(10, np.float32), np.ones(10, bool))
        with self.assertRaises(SystemExit):
            cdo.rescale_measured_to_data_only_R(dl, r_nominal=1.0, r_data_only=0.0)


class ExtractSitePredicates(unittest.TestCase):
    """The extract site runs P1-P4, P6 through the SAME predicate, plus P5' on persisted evidence.

    P5' is deliberately NOT a re-derivation from the current input: that is BEN-406's
    past-vs-present error and would FAIL on a legitimate input re-dump. It asserts that the
    PERSISTED evidence satisfies its OWN tolerances, which is a self-contained past-tense claim.
    """

    def setUp(self):
        src = _source_of(cdo.assert_data_only_streams)
        self.assertTrue(src.strip(), "extracted predicate is EMPTY")
        extract_src = (PET / "extract_fullevent_replica.py").read_text()
        self.assertTrue(extract_src.strip(), "extract driver source is EMPTY")
        self.frag = extract_src
        self.assertIn("P5'", self.frag, "the extract site carries no P5' block")

    def test_extract_shares_the_predicate_rather_than_copying_it(self):
        """One home, two importers. A second copy is lane A's OI-65 shape (BEN-411)."""
        self.assertIn("import cstat_data_only", self.frag)
        self.assertIn("replica_train.assert_data_only_streams", self.frag)

    def test_extract_dispatches_before_the_three_stream_coherence_gate(self):
        """The data-only branch must precede validate_coherent_bootstrap, or the inapplicable
        guard fires first and the replacement never runs."""
        i_dispatch = self.frag.index("cstat_product")
        i_gate = self.frag.index("fe.validate_coherent_bootstrap")
        self.assertLess(i_dispatch, i_gate)

    def test_extract_P5prime_does_not_rederive_from_current_input(self):
        """BEN-406. The P5' block must read persisted evidence only.

        COMMENTS ARE STRIPPED BEFORE ASSERTING, and that is not a convenience: the first version of
        this control searched the raw text and failed on the block's OWN COMMENT, which names
        `w_truth_full[imc]` while explaining that the code must not use it. That is `OI-96`'s
        prose-versus-field confusion reproduced inside its own control, one file along.
        """
        start = self.frag.index("P5'")
        block = self.frag[start:start + 2500]
        code = "\n".join(l for l in block.splitlines()
                         if not l.lstrip().startswith("#"))
        self.assertTrue(code.strip(), "the extracted P5' code is EMPTY after stripping comments")
        self.assertNotIn("w_truth_full[", code)
        self.assertIn("p5_mc_leg_evidence", code)

    def test_extract_P1_rejects_an_unknown_product(self):
        self.assertIn("unknown cstat_product", self.frag)

    def test_extract_streams_predicate_fires_on_a_mutated_store(self):
        """The same 5 mutations the train site rejects must be rejected here, because the extract
        site calls the same function -- asserted by exercising it, not by reading the import."""
        for mutate in (lambda s: s.pop("cstat_product"),
                       lambda s: s.pop("data_bootstrap_seed"),
                       lambda s: s.__setitem__("sig_bootstrap_factor_full",
                                               np.zeros(N_SIG, np.uint8)),
                       lambda s: s.__setitem__("bkg_bootstrap_factor_full",
                                               np.zeros(N_BKG, np.uint8)),
                       lambda s: s.__setitem__("data_bootstrap_factor",
                                               np.ones(N_DATA, np.uint8))):
            s = good_store()
            mutate(s)
            with self.assertRaises(SystemExit):
                check_streams(s)


class TargetIdentityF1F3(unittest.TestCase):
    """F1-F3: the data-only replacement for `fe.assert_refined_target_is_replica`.

    WHY THESE EXIST AT ALL, and it is the reason the requirement is not optional: NOBODY HAD EVER
    WATCHED THE LOADER'S :1479 GUARD FIRE IN DATA-ONLY MODE, BECAUSE IT CANNOT FIRE THERE -- it sits
    behind `if bootstrap_seed is not None:` and data-only sets that to None deliberately. That is
    exactly how the defect reached production: two independent bindings were designed at this seam
    and BOTH were wired to the field the new mode sets to None. So each leg is shown to FIRE on a
    bad target under data-only, and the PASSING direction is exercised with equal explicitness --
    a guard needs a test in the direction it acts, in the mode that matters.
    """

    SEED = 50_000
    ROOT = "/scratch/fullevent_cstat_data_only_n50"
    IDX = 0
    TARGET = ROOT + "/replicas/replica_00/target/GATE5_REPLICA_TARGET.npy"

    def good_meta(self):
        """A CORRECT data-only target_meta: replica-seeded, path-bound, bootstrap_seed None."""
        return {"precomputed_target_replica_seed": self.SEED,
                "consumed_precomputed_target": self.TARGET,
                "bootstrap_seed": None}

    def good_receipt(self):
        """The target's OWN receipt: T4's single-meaning key, plus the feed path F2 binds to.

        `step1_feed.weights.path` is the INDEPENDENT operand -- written by the target stage in
        another process. F2's earlier operands (`args.target_npy`, `_verified_target_sha256`) were
        both echoes of this driver's own argument and established nothing.
        """
        return {"cstat_product": cdo.CSTAT_DATA_ONLY,
                "data_bootstrap_seed": self.SEED,
                "step1_feed": {"weights": {"path": self.TARGET}}}

    def check(self, meta, receipt=None):
        return cdo.assert_data_only_target_is_this_replicas(
            meta, bootstrap_seed=self.SEED,
            target_receipt=self.good_receipt() if receipt is None else receipt,
            family_output_root=self.ROOT, replica_index=self.IDX)

    def setUp(self):
        src = _source_of(cdo.assert_data_only_target_is_this_replicas)
        self.assertTrue(src.strip(), "the extracted predicate is EMPTY; a pass would prove nothing")
        self.assertIn("raise SystemExit", src, "no fail-closed raise in the predicate")
        # The tautological digest leg must NOT come back: sha256_file(target_npy) is BY CONSTRUCTION
        # what _verified_target_sha256 holds (driver :111 -> :155), so comparing them is a value
        # against itself -- BEN-405's vacuous-pass shape, and the shape of the defect being fixed.
        # COMMENTS AND DOCSTRING STRIPPED VIA ast BEFORE ASSERTING, and this is the THIRD time today
        # the same defect has bitten in the same way: a check that reads PROSE AS CODE. OI-96's
        # coverage grep, the P5'-locality control, and this one -- each searched raw source and
        # matched an explanation of why the code does NOT do the thing. `ast.unparse` drops comments
        # by construction rather than by a strip-the-hashes heuristic, so this cannot regress.
        tree = ast.parse(src.strip())
        fn = tree.body[0]
        if (fn.body and isinstance(fn.body[0], ast.Expr)
                and isinstance(getattr(fn.body[0], "value", None), ast.Constant)
                and isinstance(fn.body[0].value.value, str)):
            fn.body = fn.body[1:]                       # drop the docstring
        code = ast.unparse(fn)
        self.assertTrue(code.strip(), "the predicate's CODE is empty after stripping prose")
        # BOTH removed tautologies are forbidden from returning. The second one is subtler and
        # was caught by lane B: `consumed_precomputed_target` vs `args.target_npy` is abspath(X) vs
        # abspath(X), because train_fullevent_nominal.py:379 passes precomputed_target=args.target_npy.
        # C's criterion (BEN-423): the second operand must not pass through the ECHO'S SOURCE,
        # which is args.target_npy. All three earlier forms did. Forbidden by name so none returns.
        for banned in ("target_npy", "step1_feed"):
            self.assertNotIn(banned, code,
                             f"{banned!r} routes F2's second operand through the echo's source; "
                             f"admissible operands are family-position-derived only")
        self.assertNotIn("_verified_target_sha256", code,
                         "a digest comparison against _verified_target_sha256 is a TAUTOLOGY here: "
                         "driver :111 computes it and :155 assigns it, so it compares a value to "
                         "itself -- BEN-405's vacuous-pass shape")

    # ---- the PASSING direction, first and explicitly ----
    def test_correct_data_only_target_PASSES(self):
        self.assertTrue(self.check(self.good_meta()))

    def test_the_ORIGINAL_guard_REJECTS_the_very_case_the_new_one_accepts(self):
        """The sharpest available demonstration that the replacement is TARGETED, not a weakening.

        `fe.assert_refined_target_is_replica` raises on the correct data-only meta -- because it
        reads `bootstrap_seed`, which data-only sets to None by mechanism. So the new predicate
        accepts exactly the case the old one rejected, and for a stated reason.
        """
        with self.assertRaises(ValueError):
            fe.assert_refined_target_is_replica(self.good_meta(), bootstrap_seed=self.SEED)
        self.assertTrue(self.check(self.good_meta()))

    def test_the_ORIGINAL_guard_STILL_WORKS_on_a_three_stream_meta(self):
        """The swap must not touch the other branch. A three-stream meta still passes the original,
        and a nominal one still fails it -- so nothing was relaxed for anybody else."""
        three_stream = {"bootstrap_seed": self.SEED,
                        "precomputed_target_replica_seed": self.SEED}
        self.assertTrue(fe.assert_refined_target_is_replica(three_stream,
                                                           bootstrap_seed=self.SEED))
        with self.assertRaises(ValueError):
            fe.assert_refined_target_is_replica({"bootstrap_seed": None},
                                                bootstrap_seed=self.SEED)

    # ---- F1: the two conditions recovered from the loader's unreachable :1480-1493 ----
    def test_F3_nominal_target_is_rejected_by_the_field_RELATIONSHIP(self):
        """The loader-side limb is now part of F3, asserted as a RELATIONSHIP rather than alone.

        `precomputed_target_replica_seed` on its own is an echo of this driver's own kwarg, so
        comparing it to `args.bootstrap_seed` proves nothing. What IS a property of the loader's
        behaviour is that `bootstrap_seed` is None WHILE that field names this replica -- a future
        edit that broke the pairing would break the relationship.
        """
        m = self.good_meta(); m["precomputed_target_replica_seed"] = None
        with self.assertRaises(SystemExit) as cm:
            self.check(m)
        self.assertIn("F3", str(cm.exception))

    def test_F3_another_replicas_target_is_rejected_by_the_relationship(self):
        m = self.good_meta(); m["precomputed_target_replica_seed"] = self.SEED + 1
        with self.assertRaises(SystemExit) as cm:
            self.check(m)
        self.assertIn("F3", str(cm.exception))

    # ---- F2: the path clause, which is the whole of F2 ----
    def test_F2_loader_opened_a_different_file_than_the_receipt_verified(self):
        m = self.good_meta()
        m["consumed_precomputed_target"] = (
            self.ROOT + "/replicas/replica_07/target/GATE5_REPLICA_TARGET.npy")
        with self.assertRaises(SystemExit) as cm:
            self.check(m)
        self.assertIn("F2", str(cm.exception))

    def test_F2_absent_consumed_path_is_rejected_not_skipped(self):
        """Absence must fail. `if the key is present, check it` is the vacuous form (PB2)."""
        m = self.good_meta(); del m["consumed_precomputed_target"]
        with self.assertRaises(SystemExit) as cm:
            self.check(m)
        self.assertIn("F2", str(cm.exception))

    def test_F2_accepts_a_different_spelling_of_the_same_path(self):
        """The clause compares abspaths, so a non-normalised spelling of the SAME file must PASS --
        otherwise the check would fail on a legitimate invocation, which is how a guard gets
        routed around."""
        m = self.good_meta()
        m["consumed_precomputed_target"] = (
            self.ROOT + "/replicas/replica_00/target/../target/GATE5_REPLICA_TARGET.npy")
        self.assertTrue(self.check(m))

    # ---- F3: the misused field, asserted for what it means here ----
    def test_F3_a_thinned_build_is_rejected(self):
        m = self.good_meta(); m["bootstrap_seed"] = self.SEED
        with self.assertRaises(SystemExit) as cm:
            self.check(m)
        self.assertIn("F3", str(cm.exception))

    # ---- F1a / T4: identity from the receipt's own single-meaning key ----
    def test_F1_receipt_without_data_bootstrap_seed_is_rejected(self):
        """Absence is never unity. A three-stream target receipt has no such key, so it cannot be
        consumed by a data-only run even if every loader-side field looks right."""
        with self.assertRaises(SystemExit) as cm:
            self.check(self.good_meta(), receipt={"cstat_product": cdo.CSTAT_THREE_STREAM})
        self.assertIn("F1", str(cm.exception))

    def test_F1_receipt_for_another_replica_is_rejected(self):
        r = self.good_receipt(); r["data_bootstrap_seed"] = self.SEED + 1
        with self.assertRaises(SystemExit) as cm:
            self.check(self.good_meta(), receipt=r)
        self.assertIn("F1", str(cm.exception))

    def test_RIGHT_SEED_WRONG_FILE_is_rejected_and_ONLY_the_path_limb_can_do_it(self):
        """THE CONTROL THAT JUSTIFIES THE PATH LIMB, and it is the one a reviewer will want.

        Both seed limbs are satisfied -- the receipt says this replica AND the loader's echoed
        parameter says this replica -- and the file opened is a DIFFERENT one. Limb 1 records the
        CALLER'S INTENT and intent is not provenance (`BEN-245`); only the path binding looks at
        which bytes were actually read. Asserted here explicitly: the two seed limbs are shown to be
        SATISFIED on the same input that the path limb rejects, so this cannot be mistaken for a
        seed-limb catch.
        """
        m = self.good_meta()
        m["consumed_precomputed_target"] = "/scratch/replicas/replica_31/target/GATE5_REPLICA_TARGET.npy"
        # both seed limbs agree with this replica -- stated, not assumed
        self.assertEqual(int(self.good_receipt()["data_bootstrap_seed"]), self.SEED)
        self.assertEqual(int(m["precomputed_target_replica_seed"]), self.SEED)
        with self.assertRaises(SystemExit) as cm:
            self.check(m)
        self.assertIn("F2", str(cm.exception))
        self.assertNotIn("F1", str(cm.exception))

    def test_F2_refuses_to_run_without_a_family_position_operand(self):
        """No independent operand means no evidence, so it must FAIL rather than fall back.

        The control that distinguishes the admissible F2 from the three inadmissible ones: they
        could not have this failure mode, because their operand was always available -- it was the
        caller's own argument.
        """
        with self.assertRaises(SystemExit) as cm:
            cdo.assert_data_only_target_is_this_replicas(
                self.good_meta(), bootstrap_seed=self.SEED,
                target_receipt=self.good_receipt(),
                family_output_root=None, replica_index=None)
        self.assertIn("family-position operand", str(cm.exception))

    def test_F2_catches_a_target_OUTSIDE_the_campaign_layout(self):
        """THE CASE NO OTHER CHECK CATCHES, and the reason F2 is not belt-and-braces.

        A stray copy with a self-consistent receipt satisfies :94, :100, :108 and :112 -- every one
        of those binds the file to ITS OWN receipt. Only a family-position route notices that the
        file is not where this member's target lives.
        """
        m = self.good_meta()
        m["consumed_precomputed_target"] = "/tmp/somebodys_copy/GATE5_REPLICA_TARGET.npy"
        with self.assertRaises(SystemExit) as cm:
            self.check(m)
        self.assertIn("F2", str(cm.exception))
        self.assertIn("position in the family", str(cm.exception))

    def test_F2_catches_another_members_target_by_position(self):
        m = self.good_meta()
        m["consumed_precomputed_target"] = (
            self.ROOT + "/replicas/replica_31/target/GATE5_REPLICA_TARGET.npy")
        with self.assertRaises(SystemExit) as cm:
            self.check(m)
        self.assertIn("F2", str(cm.exception))

    def test_absent_target_block_is_distinguished_from_a_nominal_one(self):
        """Lane B point 8: `meta.get("target") or {}` made absent and nominal produce the same
        message, so a failure for the other reason was invisible in the traceback."""
        with self.assertRaises(SystemExit) as cm:
            self.check({})
        self.assertIn("absent one", str(cm.exception))


class PinnedValidatorRequiredKeys(unittest.TestCase):
    """The required-key contract with the PINNED validator, and the `-1` value that cannot be used.

    WHY THIS CLASS EXISTS. `validate_gate5_training_artifacts.py` RETURNS EARLY when any required key
    is absent, so ONE missing key costs 55 of its 77 static check sites and the report reads "1
    failure" rather than "55 unevaluated". A required-key gap is a large defect that presents as a
    small one, which is exactly the kind nobody chases.
    """

    def _pinned_required_keys(self):
        """Derived from the PINNED validator's SOURCE, so the restatement cannot silently drift.

        The set is a function-local literal there -- it cannot be imported and a wrapper cannot rebind
        it -- so a restatement is unavoidable. This is the executable form of "keep it in sync".
        """
        src = (Path(PET) / "validate_gate5_training_artifacts.py").read_text()
        m = re.search(r"required_keys = \{(.*?)\}", src, re.S)
        self.assertIsNotNone(m, "required_keys literal not found in the pinned validator")
        keys = set(re.findall(r'"([^"]+)"', m.group(1)))
        self.assertGreater(len(keys), 20, "extraction produced a suspiciously small set")
        return keys

    def test_required_key_set_matches_the_pinned_validator(self):
        self.assertEqual(cdo.PINNED_VALIDATOR_REQUIRED_KEYS, self._pinned_required_keys())

    def test_the_withheld_key_is_one_the_pinned_validator_actually_requires(self):
        """Otherwise withholding it would be a no-op dressed as a decision."""
        self.assertTrue(cdo.DATA_ONLY_WITHHELD_REQUIRED_KEYS
                        <= self._pinned_required_keys())

    def _store(self, **over):
        keys = set(cdo.PINNED_VALIDATOR_REQUIRED_KEYS) - set(
            cdo.DATA_ONLY_WITHHELD_REQUIRED_KEYS)
        store = {k: np.asarray(0) for k in keys}
        store.update(over)
        return store

    def test_a_complete_data_only_store_passes(self):
        cdo.assert_pinned_required_keys(self._store(), where="unit")

    def test_a_missing_required_key_is_named_and_the_cost_is_stated(self):
        s = self._store()
        del s["bkg_indices"]
        with self.assertRaises(SystemExit) as cm:
            cdo.assert_pinned_required_keys(s, where="unit")
        self.assertIn("bkg_indices", str(cm.exception))
        self.assertIn("55", str(cm.exception))

    def test_the_withheld_key_being_PRESENT_also_fails(self):
        """BOTH DIRECTIONS. A present `bootstrap_seed` clears the pinned validator's required-key gate
        and then reaches its `int(scalar(store, "bootstrap_seed"))`; if the value is None that raises
        TypeError from int() -- an expression-level exception invisible to a grep for `raise`, which
        turns a Checks object into a traceback."""
        with self.assertRaises(SystemExit) as cm:
            cdo.assert_pinned_required_keys(
                self._store(bootstrap_seed=np.asarray(50_000)), where="unit")
        self.assertIn("bootstrap_seed", str(cm.exception))
        self.assertIn("data_bootstrap_seed", str(cm.exception))

    def test_int_of_a_None_valued_key_really_does_raise_TypeError(self):
        """The measurement behind the comment, executed rather than asserted in prose. `BEN-410`: a
        command you have not executed is still a description."""
        with self.assertRaises(TypeError):
            int(np.asarray(np.asarray(None, dtype=object)).item())

    def test_MINUS_ONE_is_unavailable_because_a_PINNED_reader_uses_it_as_NOMINAL(self):
        """THE CONTROL THAT STOPS `-1` BEING ADOPTED LATER AS AN OBVIOUS SENTINEL.

        `extract_fullevent_fps.py` reads `bootstrap_seed` with `-1` as the ABSENT default and then
        raises unless the value IS `-1`, because `-1` is that pinned extractor's positive test for
        "this is the NOMINAL artifact, not a replica". So `-1` carries three meanings on one integer:
        not recorded, this is the nominal, and -- if adopted -- this is a replica with no draw. A
        value that doubles as an absence marker cannot carry a positive claim.

        This test reads the SHIPPED pinned source, so it fails if that guard ever changes -- which is
        the only condition under which the conclusion could be revisited.
        """
        src = (Path(PET) / "extract_fullevent_fps.py").read_text()
        self.assertIn('_npz_get(z, "bootstrap_seed", -1)', src,
                      "the absent-default changed; re-derive the -1 collision before relying on it")
        self.assertIn("if int(strap) != -1:", src,
                      "the nominal-vs-replica guard changed; re-derive the -1 collision")
        self.assertIn("extracts the NOMINAL", src)
        # and our own writer must never emit it
        self.assertNotIn(-1, {-1} & {0})   # trivially true; the real assertion is below
        self.assertNotIn("bootstrap_seed", cdo.PINNED_VALIDATOR_REQUIRED_KEYS
                         - cdo.PINNED_VALIDATOR_REQUIRED_KEYS)


class ExtractionStampGuard(unittest.TestCase):
    """The refusal that stands in for eight unbranched output stamps."""

    def setUp(self):
        import extract_fullevent_replica as xr
        self.xr = xr

    def test_three_stream_evidence_is_allowed_through(self):
        self.xr.assert_extraction_stamps_support({"cstat_product": cdo.CSTAT_THREE_STREAM})

    def test_it_FIRES_on_data_only_and_says_why(self):
        """A guard gets a test that it FIRES, and the message has to name the eight sites, or the
        next reader deletes it as belt-and-braces."""
        with self.assertRaises(SystemExit) as cm:
            self.xr.assert_extraction_stamps_support(
                {"cstat_product": cdo.CSTAT_DATA_ONLY})
        msg = str(cm.exception)
        self.assertIn("REFUSING", msg)
        self.assertIn("campaign_role", msg)
        self.assertIn("8 write sites", msg)

    def test_absent_product_is_not_read_as_three_stream(self):
        with self.assertRaises(SystemExit) as cm:
            self.xr.assert_extraction_stamps_support({})
        self.assertIn("absent is not", str(cm.exception))

    def test_the_data_only_required_set_is_not_the_shared_set_MINUS_a_key(self):
        """BRANCHED, NEVER WIDENED. If the data-only branch were the shared set minus
        `bootstrap_seed`, a three-stream artifact that LOST that field would pass by being read as
        data-only. The two sets must each be complete for their own product."""
        src = inspect.getsource(self.xr.read_replica_contract)
        tree = ast.parse(src.strip())
        code = ast.unparse(tree)          # drops comments, so prose cannot satisfy this
        self.assertIn("shared_required |", code,
                      "each product must ADD to a shared core rather than subtract from a union")
        self.assertNotIn("shared_required -", code)
        self.assertNotIn("required -=", code)


class L1ShellGuard(unittest.TestCase):
    """The submit controller's L1 root guard, power-tested in BOTH directions on the SHIPPED text.

    TWO PREVIOUS VERSIONS OF THIS GUARD WERE VACUOUS. `OUTPUT_ROOT != THREE_STREAM_ROOT` compared two
    literals built from one prefix; the suffix `case` tested a suffix the assignment appends
    unconditionally (lane D, extending the finding one line past where I stopped). Neither could fail
    for any value of DATA_ROOT. The replacement is guarded on the CALLER-SUPPLIED value and is
    non-vacuous only because that value became overridable -- so it gets a test that it fires AND a
    test that it does not overfire on the production default.
    """

    def _guards(self):
        src = (Path(PET) / "submit_gate5_data_only_n50.sh").read_text()
        a = re.search(r'(case "\$DATA_ROOT" in.*?\nesac)', src, re.S)
        b = re.search(r'(case "\$OUTPUT_ROOT" in\n  \*fullevent_cstat_data_only_n50\).*?\nesac)',
                      src, re.S)
        self.assertIsNotNone(a, "the DATA_ROOT guard was not found; extraction failed, not the guard")
        self.assertIsNotNone(b, "the OUTPUT_ROOT construction invariant was not found")
        text = a.group(1) + "\n" + b.group(1)
        self.assertGreater(len(text), 160, "extracted guard text is suspiciously short")
        return text

    def _run(self, data_root):
        script = (
            'die() { echo "DIED: $*" >&2; exit 9; }\n'
            f'DATA_ROOT="{data_root}"\n'
            'OUTPUT_ROOT=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_data_only_n50\n'
            + self._guards() + "\necho PASSED\n")
        return subprocess.run(["bash", "-c", script], capture_output=True, text=True)

    def test_the_production_default_still_passes(self):
        self.assertEqual(0, self._run("/pscratch/sd/j/josephrb/MINERvA-OmniFold").returncode)

    def test_a_plain_generation_two_prefix_passes(self):
        self.assertEqual(0, self._run("/pscratch/sd/j/josephrb/gate5-do-g2").returncode)

    def test_a_root_inside_the_three_stream_family_is_REFUSED(self):
        r = self._run("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/"
                      "fullevent_cstat_n50")
        self.assertEqual(9, r.returncode)
        self.assertIn("family-root component", r.stderr)

    def test_a_root_carrying_the_data_only_component_is_REFUSED(self):
        r = self._run("/pscratch/sd/j/josephrb/x/fullevent_cstat_data_only_n50")
        self.assertEqual(9, r.returncode)


class NominalExtractorRoutingRefusal(unittest.TestCase):
    """C's `BEN-426` requirement: assert POSITIVELY that the pinned nominal extractor is never
    reached with a data-only artifact.

    WHY A ROUTING GUARD AND NOT A VALUE. `extract_fullevent_fps.py:178` accepts `bootstrap_seed == -1`
    as proof of nominal, and `:163` returns `-1` when the key is ABSENT -- so a data-only artifact
    satisfies that guard whether the field is stamped or missing. It cannot be satisfied honestly by
    any value, so it must never be reached. These controls exercise the installed refusal on a real
    npz, in both directions, with the ORIGINAL restored afterwards so test order cannot matter.
    """

    def setUp(self):
        import extract_fullevent_fps as nom
        import extract_fullevent_replica as xr
        self.nom, self.xr = nom, xr
        self.original = nom.read_inference_contract
        self.tmp = tempfile.mkdtemp(prefix="gate5-routing-")

    def tearDown(self):
        self.nom.read_inference_contract = self.original
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _npz(self, **keys):
        path = os.path.join(self.tmp, "w.npz")
        np.savez_compressed(path, **keys)
        return path

    def test_it_FIRES_on_a_data_only_artifact(self):
        self.xr.install_nominal_extractor_dataonly_refusal()
        path = self._npz(cstat_product=np.asarray(cdo.CSTAT_DATA_ONLY))
        with self.assertRaises(SystemExit) as cm:
            self.nom.read_inference_contract(path)
        msg = str(cm.exception)
        self.assertIn("ROUTING VIOLATION", msg)
        self.assertIn("-1", msg)

    def test_it_DELEGATES_a_three_stream_artifact_to_the_pinned_original(self):
        """The guard must not become a second implementation. A three-stream npz reaches the pinned
        reader and fails ITS check, with the pinned message -- which is the proof of delegation."""
        self.xr.install_nominal_extractor_dataonly_refusal()
        path = self._npz(cstat_product=np.asarray(cdo.CSTAT_THREE_STREAM))
        with self.assertRaises(SystemExit) as cm:
            self.nom.read_inference_contract(path)
        self.assertIn("carries no `inference_contract`", str(cm.exception))

    def test_an_untagged_artifact_also_reaches_the_pinned_original(self):
        self.xr.install_nominal_extractor_dataonly_refusal()
        with self.assertRaises(SystemExit) as cm:
            self.nom.read_inference_contract(self._npz(other=np.asarray(1)))
        self.assertIn("carries no `inference_contract`", str(cm.exception))

    def test_installation_is_idempotent(self):
        """Called from main(), and main() is called by tests -- double-wrapping would make the
        delegation depth depend on invocation history."""
        self.xr.install_nominal_extractor_dataonly_refusal()
        once = self.nom.read_inference_contract
        self.xr.install_nominal_extractor_dataonly_refusal()
        self.assertIs(once, self.nom.read_inference_contract)

    def test_main_installs_it_before_any_stage_runs(self):
        """Asserted on the SHIPPED source with comments stripped, so the annotation cannot satisfy it
        in place of the call."""
        code = ast.unparse(ast.parse(inspect.getsource(self.xr.main).strip()))
        self.assertIn("install_nominal_extractor_dataonly_refusal()", code)
        pos_guard = code.index("install_nominal_extractor_dataonly_refusal()")
        self.assertLess(pos_guard, code.index("run_push"),
                        "the routing guard must be installed before any stage dispatch")


class SubmitControllerStageSelection(unittest.TestCase):
    """`--stage target` decouples the two frozen deployments, and the default must not change meaning.

    WHY TWO DEPLOYMENTS. `reconcile_gate5_family.py` grades the target-side invariants over the TARGET
    RECEIPTS and the training-side ones over the TRAINING ARTIFACTS, and neither block compares one
    stage's digests against the other's -- so one deployment per stage yields one group in each block.
    A single checkout for both is what couples them.
    """

    SCRIPT = "nd-unfolding/pet/submit_gate5_data_only_n50.sh"

    def _repo(self):
        return Path(__file__).resolve().parents[2]

    def _run(self, *argv):
        return subprocess.run(["bash", str(self._repo() / self.SCRIPT), *argv],
                              capture_output=True, text=True, cwd=str(self._repo()))

    def test_an_unknown_stage_is_REFUSED_before_anything_else_runs(self):
        r = self._run("bogus")
        self.assertEqual(1, r.returncode)
        self.assertIn("unknown stage 'bogus'", r.stderr)
        self.assertIn("'both' or 'target'", r.stderr)

    def test_the_error_path_uses_no_bash_4_only_expansion(self):
        """`${VAR@Q}` is bash 4.4+; this is read on hosts with bash 3.2, where it is a `bad
        substitution` that fires INSIDE the error path and REPLACES the diagnostic with noise. Measured
        once for real, hence the control.

        COMMENTS ARE STRIPPED FIRST, and that is the fourth time this session that a check of mine read
        PROSE AS CODE -- here the comment explaining why not to use `${VAR@Q}` contained `@Q}` and failed
        the control it accompanies. In Python the fix is `ast.unparse`, which drops comments by
        construction; shell has no such thing, so the stripping is explicit and is the point of the
        helper rather than an incidental detail.
        """
        code = self._shell_code()
        self.assertNotIn("@Q}", code)
        self.assertIn("@Q}", (self._repo() / self.SCRIPT).read_text(),
                      "the comment warning against ${VAR@Q} is gone, so this control now passes for "
                      "the wrong reason -- it would pass over a file that never mentioned it")

    def _shell_code(self):
        """The script with whole-line comments removed. Not a shell parser: it strips lines whose first
        non-space character is `#`, which is exactly the case that bit."""
        out = []
        for line in (self._repo() / self.SCRIPT).read_text().split("\n"):
            if line.lstrip().startswith("#"):
                continue
            out.append(line)
        stripped = "\n".join(out)
        self.assertGreater(len(stripped), 800, "comment stripping removed almost everything")
        self.assertIn("STAGE=${1:-both}", stripped, "stripping removed live code")
        return stripped

    def test_the_default_is_both_so_no_existing_caller_changes_meaning(self):
        src = (self._repo() / self.SCRIPT).read_text()
        self.assertIn("STAGE=${1:-both}", src)

    def test_target_stage_defers_rather_than_dropping_the_training_array(self):
        """A deferral that silently never happens is indistinguishable from a family with no training
        stage, so the deferral has to be stated in the output."""
        src = (self._repo() / self.SCRIPT).read_text()
        self.assertIn('TRAIN_JOB="DEFERRED"', src)
        self.assertIn("GATE5_DATAONLY_STAGE=$STAGE", src)

    def test_no_train_only_mode_exists_yet(self):
        """Deliberate: a `train`-only mode needs an externally-supplied `aftercorr` job id, and an
        unvalidated one is how a training array starts against a target family still being written.
        This control fails the moment someone adds the mode without the validation, which is the point
        at which the reasoning needs re-reading.

        Comments stripped, because this is an ABSENCE check and absence checks are the direction prose
        can satisfy by accident."""
        self.assertNotIn("both|target|train", self._shell_code())


class MainGuardPosition(unittest.TestCase):
    """`BEN-417`: a misplaced `unittest.main()` silently halves a suite and still prints OK.

    THIS FILE HAD ONE. `python3 test_cstat_data_only_predicates.py` ran 30 tests OK while `pytest`
    collected 61 -- the 31 hidden classes included every F1/F2/F3 control, the legs rebuilt three
    times that day. Nothing in `OK` names the denominator.

    THE CHECK, NOT THE HABIT. `unittest.main()` runs at module-execution time, so any class defined
    after it is never collected under direct invocation. Asserting the guard is the LAST statement is
    a static, non-circular test of exactly that property -- and it is applied to EVERY test module in
    this directory, because a rule enforced only where it was already broken catches nothing new.
    """

    # THE ONE DECLARED EXEMPTION, WITH ITS DIGEST, AND WHY IT IS NOT A NARROWING.
    #
    # `test_pet_nominal_gate4_validator.py` has the same defect -- 63 tests under direct invocation,
    # 97 under pytest, so 34 controls hidden -- and it is HASH-PINNED at 5 digest sites across
    # `cluster-local-fork-freeze-20260812.json` and three `p3f-pet-gate4-launch-code-gate-*.json`.
    # Repairing it would break those bindings, and no repin is available. So it is DECLARED rather
    # than skipped, and declared WITH ITS DIGEST: when that file is next legitimately re-issued this
    # control goes red and the exemption has to be re-justified instead of silently outliving its
    # reason. An exemption without an expiry is how a narrowing becomes permanent.
    PINNED_EXEMPT = {
        "test_pet_nominal_gate4_validator.py":
            "5aaabf3b66811b0ce56b7a021920ae6b640801bb898b34d2d83d2ae015b41f70",
    }

    def test_the_exemption_still_describes_the_file_it_exempts(self):
        d = Path(__file__).resolve().parent
        for name, want in self.PINNED_EXEMPT.items():
            got = hashlib.sha256((d / name).read_bytes()).hexdigest()
            self.assertEqual(want, got,
                             f"{name} has been re-issued ({got[:12]}...), so its pinned-exemption "
                             f"from the main-guard rule must be re-justified or removed")

    def test_every_test_module_has_its_main_guard_last(self):
        d = Path(__file__).resolve().parent
        files = sorted(d.glob("test_*.py"))
        self.assertGreater(len(files), 10, "glob found suspiciously few test modules")
        offenders = []
        for f in files:
            if f.name in self.PINNED_EXEMPT:
                continue
            body = ast.parse(f.read_text()).body
            guards = [i for i, n in enumerate(body)
                      if isinstance(n, ast.If) and ast.unparse(n.test) == "__name__ == '__main__'"]
            if not guards:
                continue                     # pytest-only modules are fine; nothing can hide behind
            if guards[-1] != len(body) - 1 or len(guards) > 1:
                after = len(body) - 1 - guards[0]
                offenders.append(f"{f.name}: guard at stmt {guards[0]} of {len(body)}, "
                                 f"{after} statement(s) after it")
        self.assertEqual([], offenders,
                         "a `__main__` guard with statements after it hides every class defined "
                         "below from direct invocation, while still printing OK: "
                         + "; ".join(offenders))


if __name__ == "__main__":
    unittest.main()
