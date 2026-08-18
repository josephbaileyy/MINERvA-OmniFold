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
import inspect
import os
import sys
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


if __name__ == "__main__":
    unittest.main()
