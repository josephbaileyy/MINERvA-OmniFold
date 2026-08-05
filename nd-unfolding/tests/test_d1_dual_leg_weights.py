#!/usr/bin/env python3
"""D1 (2026-08-04): the two OmniFold legs carry their own MC weight.

Audit finding B-4 asked whether the step-1 reco leg was fed `w_reco` or `w_truth`. It was fed
`w_truth`. Job 56320955 measured the two differing on all 20,573,521 `pass_reco` rows, and decision
D1 resolved it: step 1 consumes `w_reco`, step 2 and every truth-space quantity consume `w_truth`.

THESE ARE THE MUTATION TESTS D1 requirement 5 asks for. The point is not that the code runs; it is
that perturbing ONE leg moves ONLY what that leg is supposed to drive. A test that merely checked
"R is finite" would have passed throughout the entire period B-4 was active.

The engine wiring is checked by source inspection rather than by running MultiFold, following the
idiom in test_b4_gating.TheGateActuallyCallsThePredicate: exercising it needs TensorFlow and the
frozen dump, and a hand-built stub would only prove the test agrees with itself.
"""
import importlib.util
import os
import sys
import unittest

import numpy as np

PET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pet")
if PET not in sys.path:
    sys.path.insert(0, PET)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fullevent_fps_dataloader as fed          # noqa: E402


def _load_dataloader():
    """Import the vendored DataLoader module directly.

    Deliberately NOT `from omnifold.dataloader import DataLoader`: the package __init__ pulls in
    TensorFlow, which is absent from the ROOT-side interpreter and is not needed to test weight
    bookkeeping.
    """
    path = os.path.join(REPO, "omnifold_nn", "omnifold", "dataloader.py")
    spec = importlib.util.spec_from_file_location("_d1_dataloader", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.DataLoader


class FakeDump(dict):
    @property
    def files(self):
        return list(self.keys())


def dump(*, n_sig=80, n_bkg=20, n_data=60, seed=5):
    rng = np.random.default_rng(seed)
    w_truth = (rng.random(n_sig) + 0.5).astype(np.float64)
    pass_reco = rng.random(n_sig) < 0.7
    d = FakeDump({
        "w_truth": w_truth,
        "w_reco": w_truth.copy(),
        "pass_reco": pass_reco,
        "w_bkg": (rng.random(n_bkg) + 0.5).astype(np.float64),
        "pot_scale": np.asarray(0.25),
        "measured_scalars": rng.random((n_data, 4)).astype(np.float32),
    })
    return d, pass_reco


# ============================================================ mutating the legs independently
class LegMutationMovesOnlyItsOwnQuantity(unittest.TestCase):

    def test_perturbing_the_reco_leg_moves_R(self):
        """R's denominator IS the reco leg, so scaling it must scale R inversely."""
        d, _ = dump()
        R0, t0 = fed.step1_class_ratio_from_dump(d)
        d["w_reco"] = d["w_reco"] * 1.25
        R1, t1 = fed.step1_class_ratio_from_dump(d)
        self.assertAlmostEqual(R1, R0 / 1.25, places=9)
        # ...and the truth leg is untouched, so the legacy value does not move
        self.assertAlmostEqual(t1["sum_w_truth_pass_reco_raw"],
                               t0["sum_w_truth_pass_reco_raw"], places=9)
        self.assertAlmostEqual(t1["b4_w_reco_vs_w_truth"]["R_if_reco_leg_used_w_truth"],
                               t0["b4_w_reco_vs_w_truth"]["R_if_reco_leg_used_w_truth"], places=9)

    def test_perturbing_the_truth_leg_leaves_R_alone(self):
        """The mutation that would have been invisible pre-D1 and is the whole point of the split:
        the truth leg must NOT reach R."""
        d, _ = dump()
        R0, t0 = fed.step1_class_ratio_from_dump(d)
        d["w_truth"] = d["w_truth"] * 3.0
        R1, t1 = fed.step1_class_ratio_from_dump(d)
        self.assertAlmostEqual(R1, R0, places=12)
        self.assertAlmostEqual(t1["sum_w_reco_pass_reco_raw"],
                               t0["sum_w_reco_pass_reco_raw"], places=9)
        # the truth-leg bookkeeping DOES move, so the test is not passing by reading nothing
        self.assertAlmostEqual(t1["sum_w_truth_pass_reco_raw"],
                               3.0 * t0["sum_w_truth_pass_reco_raw"], places=9)
        self.assertAlmostEqual(t1["b4_w_reco_vs_w_truth"]["R_if_reco_leg_used_w_truth"],
                               t0["b4_w_reco_vs_w_truth"]["R_if_reco_leg_used_w_truth"] / 3.0,
                               places=9)

    def test_reco_leg_perturbation_outside_pass_reco_does_not_reach_R(self):
        """R sums over pass_reco only. Without this, a denominator that quietly summed every row
        would still satisfy the two tests above."""
        d, pass_reco = dump()
        R0, _ = fed.step1_class_ratio_from_dump(d)
        wr = d["w_reco"].copy()
        wr[~pass_reco] += 17.0
        d["w_reco"] = wr
        R1, _ = fed.step1_class_ratio_from_dump(d)
        self.assertAlmostEqual(R1, R0, places=12)
        self.assertTrue((~pass_reco).any(), "fixture must contain rejected rows to be meaningful")


# ============================================================ the DataLoader's weight bookkeeping
class DataLoaderCarriesBothLegs(unittest.TestCase):

    def setUp(self):
        self.DataLoader = _load_dataloader()
        rng = np.random.default_rng(11)
        self.n = 400
        self.reco = rng.normal(size=(self.n, 3)).astype(np.float32)
        self.gen = rng.normal(size=(self.n, 3)).astype(np.float32)
        self.pr = rng.random(self.n) < 0.6
        self.pg = rng.random(self.n) < 0.8
        self.wt = (rng.random(self.n) + 0.5).astype(np.float64)
        # a MINOS-efficiency-shaped factor: strictly sub-unity, as measured on the production dump
        self.eff = rng.uniform(0.93, 0.998, self.n)
        self.wr = (self.wt * self.eff).astype(np.float64)
        self.FAC = 1_000_000

    def _mk(self, **kw):
        return self.DataLoader(reco=self.reco, gen=self.gen, pass_reco=self.pr, pass_gen=self.pg,
                              normalize=True, normalization_factor=self.FAC, **kw)

    def test_absent_reco_leg_reproduces_the_historical_path_exactly(self):
        """Backward compatibility is load-bearing: the 2D publication path and every recoil-only
        consumer pass a single `weight`, and must be untouched byte-for-byte."""
        dl = self._mk(weight=self.wt.copy())
        ref = self.wt.copy()
        ref *= (self.FAC / np.sum(ref[self.pr])).astype(np.float32)
        self.assertTrue(np.array_equal(dl.weight, ref))
        self.assertIsNone(dl.weight_reco)

    def test_normalization_constant_is_derived_from_the_reco_leg(self):
        """The leg that reaches the factor must be the one step 1 consumes, because that is the leg
        whose sum forms R's denominator and hence the measured side's 1e6*R."""
        dl = self._mk(weight=self.wt.copy(), weight_reco=self.wr.copy())
        self.assertAlmostEqual(float(dl.weight_reco[dl.pass_reco].sum()), self.FAC, delta=1.0)
        shift = self.wt[self.pr].sum() / self.wr[self.pr].sum()
        self.assertGreater(shift, 1.0, "the fixture's reco leg must be the smaller one")
        self.assertAlmostEqual(float(dl.weight[dl.pass_reco].sum()) / (self.FAC * shift),
                               1.0, places=5)

    def test_per_event_ratio_survives_normalization(self):
        """Option A. One common constant, so the per-event reco/truth ratio -- a physical
        MINOS-efficiency factor -- is preserved. Renormalizing the legs separately would multiply it
        by sum(w_truth)/sum(w_reco) and it would no longer be an efficiency."""
        dl = self._mk(weight=self.wt.copy(), weight_reco=self.wr.copy())
        got = np.asarray(dl.weight_reco) / np.asarray(dl.weight)
        self.assertTrue(np.allclose(got, self.eff, rtol=1e-6))
        self.assertLess(got.max(), 1.0)

    def test_step2_is_scale_invariant_under_that_constant(self):
        """Why Option A costs step 2 nothing: both of its classes carry `weight`, so any common
        constant cancels in the ratio it learns."""
        dl = self._mk(weight=self.wt.copy(), weight_reco=self.wr.copy())
        pull = np.random.default_rng(3).uniform(0.7, 1.4, self.n)
        norm = ((np.asarray(dl.weight) * pull * dl.pass_gen).sum()
                / (np.asarray(dl.weight) * dl.pass_gen).sum())
        raw = ((self.wt * pull * self.pg).sum() / (self.wt * self.pg).sum())
        self.assertAlmostEqual(norm, raw, places=9)

    def test_bootstrap_applies_one_draw_to_both_legs(self):
        """Independent draws would decorrelate the reco and truth views of one MC event and smear
        the migration matrix (2D_OMNIFOLD_REFERENCE.md bootstrap invariant 2)."""
        np.random.seed(17)
        dl = self._mk(weight=self.wt.copy(), weight_reco=self.wr.copy(), bootstrap=True)
        w, wr = np.asarray(dl.weight), np.asarray(dl.weight_reco)
        self.assertTrue(np.array_equal(w == 0, wr == 0))
        self.assertGreater(int((w == 0).sum()), 0, "the draw must actually zero some rows")
        alive = w != 0
        self.assertTrue(np.allclose(wr[alive] / w[alive], self.eff[alive], rtol=1e-6))

    def test_mismatched_leg_lengths_fail_closed(self):
        with self.assertRaises(AssertionError):
            self._mk(weight=self.wt.copy(), weight_reco=self.wr[:-5].copy())


# ============================================================ the engine actually splits the legs
class EngineWiring(unittest.TestCase):
    """A split the loader performs but the engine ignores is no split at all."""

    def setUp(self):
        with open(os.path.join(REPO, "omnifold_nn", "omnifold", "omnifold.py")) as fh:
            self.src = fh.read()

    def _body(self, name):
        """The method's CODE, comments stripped.

        Stripping matters: the leg assignments carry comments naming the other leg to explain why
        they are not used there, and a substring check against the raw source matches those and
        reports a regression that has not happened.
        """
        start = self.src.index(f"def {name}(")
        nxt = self.src.find("\n    def ", start + 1)
        raw = self.src[start:(nxt if nxt != -1 else len(self.src))]
        out = []
        for line in raw.splitlines():
            if line.lstrip().startswith("#"):
                continue
            out.append(line.split("#", 1)[0] if "#" in line else line)
        return "\n".join(out)

    def test_step1_consumes_the_reco_leg(self):
        body = self._body("RunStep1")
        self.assertIn("self.mc_weight_reco", body)
        self.assertNotIn("self.weights_push*self.mc.weight", body,
                         "RunStep1 is back on the truth leg; B-4 has regressed")

    def test_step2_consumes_the_truth_leg(self):
        body = self._body("RunStep2")
        self.assertIn("self.mc.weight", body)
        self.assertNotIn("mc_weight_reco", body,
                         "RunStep2 must stay on the truth leg; putting the reco leg here moves the "
                         "B-4 defect from step 1 to step 2 rather than fixing it")

    def test_reco_leg_falls_back_to_the_single_weight_contract(self):
        """So a loader that supplies only `weight` -- the 2D path -- keeps working."""
        self.assertIn('getattr(self.mc, "weight_reco", None)', self.src)
        self.assertIn("self.mc_weight_reco = self.mc.weight", self.src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
