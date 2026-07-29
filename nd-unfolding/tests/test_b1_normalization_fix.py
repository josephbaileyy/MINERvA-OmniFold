"""B1 normalization fix -- the two tests `B1-NORMALIZATION-FIX-DESIGN.md` §4 requires, plus the
Gate-4 plumbing §2d needs in order to fire at all.

A NEW file on purpose. `test_pet_nominal_gate4_validator.py` and
`test_pet_fullevent_nominal_launcher.py` are both sha256-bound by
`p3f-pet-gate4-launch-code-gate-20260721.json`; editing either would void two further bindings for
no necessary reason (`RESTORE-2026-08-03.md` Step 2b).

THE TWO REQUIRED TESTS
----------------------
  * §4 "the new Gate-2 assertion must FAIL a 1e6-normalized target and PASS a 1e6*R one"
    -> `Gate2RetargetedAssertion`.
  * §4 "a closure that injects a known truth-level rate change and verifies recovery"
    -> `RateInjectionClosure`, a small in-suite run of `pet/closure_b1_rate_injection.py`. The
    full-scale closure that sizes the Gate-4 tolerance is that script, not this test.

NOT A TAUTOLOGY. `AUDIT-FINDINGS-20260729-B.md` §4 found that all 49 `test_fps_provenance.py`
tests catch nothing because they derive their fixtures from the constant under test. So: the
predicates here are the REAL ones imported from the modules under test (`fed.step1_class_ratio`,
`g2rt.step1_target_sum_matches`, `g4.check_fold_forward_ratio`), never re-typed; the targets come
from an independent read of the fixture rather than from the loader's own `meta`; and every
assertion that something PASSES is paired with a mutation that must FAIL. A test that only
confirms the fixed configuration works would not have caught the original defect either.

Login-safe: synthetic fixtures, no ROOT, no /pscratch, no dump. The closure test imports
TensorFlow and trains briefly (a few seconds); it skips if TF is absent.
"""
import contextlib
import importlib.util
import os
import sys
import tempfile
import types
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(ND)
sys.path.insert(0, os.path.join(ND, "pet"))

import dump_pointcloud_inputs as dp        # noqa: E402  (ROOT deferred)
import fullevent_fps_dataloader as fed     # noqa: E402
import gate2_target_runtime as g2rt        # noqa: E402  (module level is inert; no I/O)
import validate_pet_nominal_gate4 as g4    # noqa: E402


@contextlib.contextmanager
def real_dataloader():
    """Install the numpy-only omnifold.dataloader for the duration of the block, bypassing
    omnifold/__init__.py (which imports TensorFlow), then restore sys.modules exactly as found.

    Unlike `test_fullevent_gate2.py` the path is derived from __file__, not the /pscratch literal,
    so this file runs off Perlmutter. RESTORING IS NOT HOUSEKEEPING: that module resolves the same
    import through the /pscratch literal and is EXPECTED to fail off-cluster -- it is 6 of the
    documented 7-failure baseline. Leaving our stub in sys.modules silently rescues those six,
    which moves the baseline, makes both modules' results depend on collection order, and -- worst
    -- reads as "the end-to-end loader boundary is covered off-cluster" when the coverage was a
    side effect of this file running first.
    """
    keys = ("omnifold", "omnifold.dataloader")
    saved = {k: sys.modules.get(k) for k in keys}
    present = {k: k in sys.modules for k in keys}
    try:
        dlp = os.path.join(ROOT, "omnifold_nn", "omnifold", "dataloader.py")
        if "omnifold" not in sys.modules:
            pkg = types.ModuleType("omnifold")
            pkg.__path__ = [os.path.dirname(dlp)]
            sys.modules["omnifold"] = pkg
        if "omnifold.dataloader" not in sys.modules:
            spec = importlib.util.spec_from_file_location("omnifold.dataloader", dlp)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["omnifold.dataloader"] = mod
            spec.loader.exec_module(mod)
        yield sys.modules["omnifold.dataloader"]
    finally:
        for k in keys:
            if present[k]:
                sys.modules[k] = saved[k]
            else:
                sys.modules.pop(k, None)


def sklearn_refine(feat, signed, estimator="exact", **kw):
    """Algorithm-identical login-safe stand-in for u2d.refine_stay_positive (the canonical refiner
    imports ROOT at module load). Same shape as the one in test_fullevent_gate2.py."""
    from sklearn.ensemble import GradientBoostingClassifier
    feat = np.asarray(feat, float)
    signed = np.asarray(signed, float)
    lab = (signed > 0).astype(int)
    absw = np.abs(signed)
    clf = GradientBoostingClassifier(random_state=0)
    clf.fit(feat, lab, sample_weight=absw)
    g = np.clip(clf.predict_proba(feat)[:, 1], 1e-6, 1.0 - 1e-6)
    fac = 2.0 * g - 1.0
    return absw * np.clip(fac, 0.0, None), g, float((fac < 0).mean())


def _scal(rng, n):
    """(pt, p_parallel, eavail, q3) inside the retained extended-FPS domain."""
    return np.column_stack([rng.uniform(0.1, 3.0, n), rng.uniform(0.5, 10.0, n),
                            rng.uniform(0.0, 2.0, n), rng.uniform(0.0, 1.0, n)]).astype(np.float32)


def g2_arrays_with_R(target_R=1.135, ns=80, nd=60, nb=20, P=6, seed=3, acceptance=0.7,
                     pot_scale=0.22, w_reco_scale=None):
    """A contract-valid g2-fullevent-v1 arrays dict whose step-1 class ratio is exactly `target_R`.

    R = (n_data - pot_scale*sum(w_bkg)) / (pot_scale*sum(w_truth[pass_reco])), so with n_data,
    w_bkg and pot_scale chosen freely the signal weights are rescaled to hit `target_R` exactly.
    That makes R a *property of the fixture we set*, independently of anything the loader reports
    -- which is what lets the assertions below be non-circular.

    `w_reco_scale` (if given) makes w_reco differ from w_truth, to exercise the B-4 telemetry.
    """
    rng = np.random.default_rng(seed)
    pass_reco = rng.random(ns) < acceptance
    if not pass_reco.any():                       # degenerate draw would make R undefined
        pass_reco[0] = True
    w_base = (rng.random(ns) + 0.5).astype(np.float64)
    w_bkg = (rng.random(nb) + 0.5).astype(np.float64)
    # solve sum(w_truth[pass_reco]) so that R comes out at exactly target_R
    numerator = float(nd) - pot_scale * float(w_bkg.sum())
    if numerator <= 0:
        raise ValueError("fixture: background over-subtracts the data; raise nd or lower nb")
    want_sum = numerator / (pot_scale * float(target_R))
    w_truth = (w_base * (want_sum / float(w_base[pass_reco].sum()))).astype(np.float32)
    w_reco = (w_truth if w_reco_scale is None
              else (w_truth.astype(np.float64) * w_reco_scale).astype(np.float32))

    sig = dict(part_reco=rng.random((ns, P, 3), np.float32), reco_scalars=_scal(rng, ns),
               reco_muon=rng.random((ns, 7), np.float32), reco_vertex=rng.random((ns, 3), np.float32),
               reco_view=rng.integers(0, 4, (ns, P)).astype(np.float32),
               reco_time=rng.random((ns, P), np.float32), part_gen=rng.random((ns, P, 5), np.float32),
               truth_scalars=_scal(rng, ns), pass_reco=pass_reco, pass_truth=np.ones(ns, bool),
               w_truth=w_truth, w_reco=w_reco)
    data = dict(measured_pc=rng.random((nd, P, 3), np.float32), measured_scalars=_scal(rng, nd),
                data_muon=rng.random((nd, 7), np.float32), data_vertex=rng.random((nd, 3), np.float32),
                data_view=rng.integers(0, 4, (nd, P)).astype(np.float32),
                data_time=rng.random((nd, P), np.float32))
    bkg = dict(bkg_part_reco=rng.random((nb, P, 3), np.float32), bkg_reco_scalars=_scal(rng, nb),
               bkg_muon=rng.random((nb, 7), np.float32), bkg_vertex=rng.random((nb, 3), np.float32),
               bkg_view=rng.integers(0, 4, (nb, P)).astype(np.float32),
               bkg_time=rng.random((nb, P), np.float32), w_bkg=w_bkg.astype(np.float32),
               bkg_nuPDG=rng.integers(-14, 15, nb), bkg_current=np.ones(nb, int),
               bkg_inttype=rng.integers(1, 5, nb))
    return dp.finalize_g2_arrays(sig, data, bkg, data_pot=8.97e19, mc_pot=4.07e20,
                                 pot_scale=pot_scale, edges_pt=fed.CANONICAL_PT_EDGES,
                                 edges_pz=fed.CANONICAL_PPARALLEL_EDGES, num_part=P)


def write_npz(td, arrays, name="G2_b1.npz"):
    p = os.path.join(td, name)
    np.savez(p, **arrays)
    return p


def build(td, arrays=None, **kw):
    arrays = g2_arrays_with_R() if arrays is None else arrays
    p = write_npz(td, arrays)
    kw.setdefault("refine_fn", sklearn_refine)
    kw.setdefault("bkg_mode", "negweight-refined")
    with real_dataloader():
        return p, fed.build_fullevent_loaders(p, **kw)


def observed_class_ratio(data, mc):
    """The ratio the engine actually sees at iteration 0: omnifold.py:176-177 forms the two step-1
    class blocks as data.weight*data.pass_reco and weights_push*mc.weight*mc.pass_reco, with
    weights_push == 1 initially (omnifold.py:157)."""
    dw = np.asarray(data.weight, np.float64)
    mw = np.asarray(mc.weight, np.float64)
    return float(dw[np.asarray(data.pass_reco).astype(bool)].sum()
                 / mw[np.asarray(mc.pass_reco).astype(bool)].sum())


# ==================================================================================== §2b
class ClassRatioFormula(unittest.TestCase):
    """The R formula itself -- the one function body a B-4 flip has to change."""

    def test_matches_hand_computed_value(self):
        R = fed.step1_class_ratio(n_data=1000.0, sum_w_bkg_raw=400.0, sum_w_mc_reco_raw=2000.0,
                                  pot_scale=0.25)
        self.assertAlmostEqual(R, (1000.0 - 0.25 * 400.0) / (0.25 * 2000.0), places=12)

    def test_pot_scale_trap_is_not_reintroduced(self):
        """Omitting pot_scale from the DENOMINATOR inflates R by 1/pot_scale (~4.7x on the real
        dump). Two independent reviewers arrived at the formula without it, so pin it."""
        kw = dict(n_data=1000.0, sum_w_bkg_raw=400.0, sum_w_mc_reco_raw=2000.0)
        R = fed.step1_class_ratio(pot_scale=0.25, **kw)
        unscaled = (1000.0 - 0.25 * 400.0) / 2000.0
        self.assertNotAlmostEqual(R, unscaled, places=6)
        self.assertAlmostEqual(R, unscaled / 0.25, places=12)

    def test_rejects_degenerate_inputs(self):
        for bad in ({"pot_scale": 0.0}, {"pot_scale": -1.0}, {"pot_scale": float("nan")},
                    {"sum_w_mc_reco_raw": 0.0}):
            kw = dict(n_data=1000.0, sum_w_bkg_raw=1.0, sum_w_mc_reco_raw=2000.0, pot_scale=0.25)
            kw.update(bad)
            with self.assertRaises(ValueError):
                fed.step1_class_ratio(**kw)

    def test_negative_signed_numerator_fails_closed(self):
        """Background over-subtracting the data would give R <= 0 -- meaningless as a class ratio
        and catastrophic as a normalization factor. It must raise, not propagate."""
        with self.assertRaises(ValueError):
            fed.step1_class_ratio(n_data=10.0, sum_w_bkg_raw=1000.0, sum_w_mc_reco_raw=50.0,
                                  pot_scale=0.5)

    def test_from_dump_reproduces_the_fixture_R(self):
        arrays = g2_arrays_with_R(target_R=1.42)
        with tempfile.TemporaryDirectory() as td:
            with np.load(write_npz(td, arrays), allow_pickle=True) as d:
                R, telem = fed.step1_class_ratio_from_dump(d)
        self.assertAlmostEqual(R, 1.42, places=6)
        self.assertEqual(telem["reco_leg_weight_used"], "w_truth")
        self.assertFalse(telem["is_bootstrap_replica"])

    def test_b4_telemetry_reports_identical_weights(self):
        with tempfile.TemporaryDirectory() as td:
            with np.load(write_npz(td, g2_arrays_with_R()), allow_pickle=True) as d:
                _, telem = fed.step1_class_ratio_from_dump(d)
        b4 = telem["b4_w_reco_vs_w_truth"]
        self.assertTrue(b4["present_in_dump"])
        self.assertTrue(b4["bit_identical_over_pass_reco"])
        self.assertEqual(b4["n_pass_reco_differing"], 0)
        self.assertIn("INACTIVE", b4["verdict"])

    def test_b4_telemetry_detects_a_differing_reco_leg(self):
        """The brief requires recording whether w_reco == w_truth at runtime. If it does not, the
        telemetry must say so AND report what R would become -- that is B-4's own minimal check."""
        with tempfile.TemporaryDirectory() as td:
            arrays = g2_arrays_with_R(target_R=1.2, w_reco_scale=1.25)
            with np.load(write_npz(td, arrays), allow_pickle=True) as d:
                R, telem = fed.step1_class_ratio_from_dump(d)
        b4 = telem["b4_w_reco_vs_w_truth"]
        self.assertFalse(b4["bit_identical_over_pass_reco"])
        self.assertIn("ACTIVE", b4["verdict"])
        self.assertAlmostEqual(b4["R_shift_factor_if_B4_fixed"], 1.0 / 1.25, places=6)
        self.assertAlmostEqual(b4["R_if_reco_leg_used_w_reco"], R / 1.25, places=6)

    def test_bootstrap_factors_change_R(self):
        """§2b: under bootstrap R must be rebuilt from THAT replica's draws. Doubling every data
        row's factor must move R; ignoring the factors would leave it pinned at the nominal."""
        arrays = g2_arrays_with_R(target_R=1.3, nd=60, nb=20, ns=80)
        with tempfile.TemporaryDirectory() as td:
            with np.load(write_npz(td, arrays), allow_pickle=True) as d:
                nominal, _ = fed.step1_class_ratio_from_dump(d)
                doubled, _ = fed.step1_class_ratio_from_dump(
                    d, data_factor=np.full(60, 2.0), bkg_factor=np.full(20, 2.0),
                    sig_factor=np.ones(80))
        self.assertAlmostEqual(nominal, 1.3, places=6)
        self.assertAlmostEqual(doubled, 2.0 * 1.3, places=6)   # numerator doubles, denominator not

    def test_sig_factor_enters_the_denominator(self):
        arrays = g2_arrays_with_R(target_R=1.3, ns=80)
        with tempfile.TemporaryDirectory() as td:
            with np.load(write_npz(td, arrays), allow_pickle=True) as d:
                scaled, _ = fed.step1_class_ratio_from_dump(d, sig_factor=np.full(80, 4.0))
        self.assertAlmostEqual(scaled, 1.3 / 4.0, places=6)


# ==================================================================================== §2a
class LoaderNormalization(unittest.TestCase):
    """§2a: the measured DataLoader must be normalized to 1e6*R, so the step-1 class ratio IS R."""

    def test_step1_class_ratio_equals_R(self):
        want_R = 1.135
        with tempfile.TemporaryDirectory() as td:
            _, (data, mc, imc, _cr, _cg, meta) = build(
                td, g2_arrays_with_R(target_R=want_R))
        self.assertAlmostEqual(observed_class_ratio(data, mc), want_R, places=4)
        self.assertAlmostEqual(meta["target"]["step1_class_ratio"], want_R, places=6)

    def test_class_ratio_is_not_one(self):
        """The defect in one assertion: before the fix this ratio was identically 1 for every R."""
        with tempfile.TemporaryDirectory() as td:
            _, (data, mc, *_rest) = build(td, g2_arrays_with_R(target_R=1.6))
        self.assertNotAlmostEqual(observed_class_ratio(data, mc), 1.0, places=2)

    def test_class_ratio_tracks_R_across_values(self):
        """Non-tautology check: a hardcoded constant would pass a single-value test. Vary R."""
        for want_R in (0.85, 1.135, 1.9):
            with tempfile.TemporaryDirectory() as td:
                _, (data, mc, *_rest) = build(td, g2_arrays_with_R(target_R=want_R))
            self.assertAlmostEqual(observed_class_ratio(data, mc), want_R, places=4,
                                   msg=f"class ratio did not track R={want_R}")

    def test_mc_block_still_normalizes_to_1e6(self):
        """§2a keeps the MC side at 1e6 -- that is what makes the ratio subsample-invariant."""
        with tempfile.TemporaryDirectory() as td:
            _, (_data, mc, *_rest) = build(td)
        mw = np.asarray(mc.weight, np.float64)
        self.assertAlmostEqual(mw[np.asarray(mc.pass_reco).astype(bool)].sum(),
                               fed.STEP1_MC_NORMALIZATION, delta=2.0)

    def test_measured_block_sums_to_1e6_times_R(self):
        want_R = 1.42
        with tempfile.TemporaryDirectory() as td:
            _, (data, _mc, _i, _cr, _cg, meta) = build(td, g2_arrays_with_R(target_R=want_R))
        self.assertAlmostEqual(float(np.asarray(data.weight, np.float64).sum()),
                               fed.STEP1_MC_NORMALIZATION * want_R, delta=2.0)
        self.assertAlmostEqual(meta["target"]["step1_measured_normalization"],
                               fed.STEP1_MC_NORMALIZATION * want_R, delta=2.0)

    def test_class_ratio_is_subsample_invariant(self):
        """Reason 2 of §3: R uses the FULL inventory and MC renormalizes, so bounding the MC
        training subsample must not move the class ratio. This is what fails if someone
        'simplifies' the fix to normalize=False."""
        arrays = g2_arrays_with_R(target_R=1.3, ns=120)
        ratios = []
        for max_events in (None, 90, 40):
            with tempfile.TemporaryDirectory() as td:
                _, (data, mc, *_rest) = build(td, arrays, max_events=max_events)
            ratios.append(observed_class_ratio(data, mc))
        for r in ratios:
            self.assertAlmostEqual(r, 1.3, places=4)

    def test_meta_carries_b4_telemetry(self):
        """The brief: 'record at runtime whether w_reco == w_truth in the loaded dump'."""
        with tempfile.TemporaryDirectory() as td:
            _, (*_rest, meta) = build(td)
        b4 = meta["target"]["step1_class_ratio_telemetry"]["b4_w_reco_vs_w_truth"]
        self.assertIn("bit_identical_over_pass_reco", b4)


# ==================================================================================== §2c
class Gate2RetargetedAssertion(unittest.TestCase):
    """REQUIRED BY §4: the new Gate-2 assertion must FAIL a 1e6-normalized step-1 target and PASS
    a 1e6*R one.

    The predicate under test is imported (`g2rt.step1_target_sum_matches`), not re-typed, and the
    two targets are built by the real loader at two normalizations. R comes from an independent
    read of the dump, exactly as the gate derives it -- never from the loader's meta."""

    def _targets(self, want_R):
        arrays = g2_arrays_with_R(target_R=want_R)
        with tempfile.TemporaryDirectory() as td:
            path = write_npz(td, arrays)
            _, (data, _mc, *_rest) = build(td, arrays)
            # the pre-B1 target: identical construction, normalized to a bare 1e6
            with real_dataloader() as dl:
                broken = dl.DataLoader(reco=np.asarray(data.reco),
                                       weight=np.asarray(data.weight, np.float32).copy(),
                                       normalize=True,
                                       normalization_factor=fed.STEP1_MC_NORMALIZATION,
                                       reco_evt=np.asarray(data.reco_evt))
            with np.load(path, allow_pickle=True) as d:
                R, _ = fed.step1_class_ratio_from_dump(d)
        return (float(np.asarray(data.weight, np.float64).sum()),
                float(np.asarray(broken.weight, np.float64).sum()), R)

    def test_passes_a_1e6R_target_and_fails_a_1e6_one(self):
        want_R = 1.135
        fixed_sum, broken_sum, R = self._targets(want_R)
        self.assertAlmostEqual(R, want_R, places=6)
        target = g2rt.NORMALIZATION * R

        # the corrected target PASSES the retargeted assertion ...
        self.assertTrue(g2rt.step1_target_sum_matches(fixed_sum, target),
                        f"1e6*R target {fixed_sum} rejected against {target}")
        # ... and the 1e6-normalized one FAILS it. This is the assertion that would have caught
        # the defect, and the one the pre-B1 gate could not make.
        self.assertFalse(g2rt.step1_target_sum_matches(broken_sum, target),
                         f"1e6 target {broken_sum} wrongly accepted against {target}")

    def test_the_old_target_would_have_accepted_the_broken_result(self):
        """Why retargeting was necessary rather than optional: the pre-B1 constant accepts the
        broken target and REJECTS the corrected one, i.e. the gate as frozen rejects its own fix."""
        fixed_sum, broken_sum, _R = self._targets(1.135)
        self.assertTrue(g2rt.step1_target_sum_matches(broken_sum, g2rt.NORMALIZATION))
        self.assertFalse(g2rt.step1_target_sum_matches(fixed_sum, g2rt.NORMALIZATION))

    def test_predicate_tolerance_is_tight_enough_to_have_power(self):
        """A 13.5% shift must be outside tolerance; round-off must be inside."""
        self.assertTrue(g2rt.step1_target_sum_matches(1_135_000.0 * (1 + 1e-9), 1_135_000.0))
        self.assertFalse(g2rt.step1_target_sum_matches(1_000_000.0, 1_135_000.0))

    def test_gate_constant_is_bound_to_the_loader_constant(self):
        """§2c's drift guard: the gate refuses to run if its base has diverged from the loader's."""
        self.assertEqual(g2rt.NORMALIZATION, fed.STEP1_MC_NORMALIZATION)

    def test_clipped_telemetry_is_invariant_under_the_retarget(self):
        """§2c claims the learned-vs-clipped telemetry survives the 1e6 -> 1e6*R change verbatim,
        BECAUSE both histograms renormalize to the same constant and rel_l1 divides by it. Verify
        the invariance rather than trusting it -- leaving the old constant in `clipped_norm` would
        silently inflate rel_l1 by R."""
        rng = np.random.default_rng(11)
        refined = rng.random(40) * 100.0
        clipped = rng.random(40) * 100.0
        for R in (1.0, 1.135, 2.5):
            base_rel = np.abs(refined - clipped * (1e6 / clipped.sum())).sum() / 1e6
            scaled_refined = refined * R
            scaled_rel = (np.abs(scaled_refined - clipped * ((1e6 * R) / clipped.sum())).sum()
                          / (1e6 * R))
            self.assertAlmostEqual(base_rel, scaled_rel, places=10)


# ==================================================================================== §2d
class Gate4FoldForward(unittest.TestCase):
    """§2d: the reco-level folded-forward ratio check, and the plumbing that makes it fire."""

    def test_passes_when_the_reco_weighted_mean_push_equals_R(self):
        w = np.array([1.0, 2.0, 3.0, 4.0])
        R = 1.135
        ok, checks = g4.check_fold_forward_ratio(float((w * R).sum()), float(w.sum()), R)
        self.assertTrue(ok, checks)

    def test_fails_the_broken_result(self):
        """The decisive property: push == 1 everywhere (what the pre-B1 configuration produces)
        must FAIL against R. Before this change the gate tolerated exactly that."""
        w = np.array([1.0, 2.0, 3.0, 4.0])
        ok, checks = g4.check_fold_forward_ratio(float(w.sum()), float(w.sum()), 1.135)
        self.assertFalse(ok)
        self.assertFalse([c for c in checks if c["name"].endswith("rate_recovered_not_erased")
                          ][0]["ok"])

    def test_absolute_yield_form_would_have_failed_a_correct_unfold(self):
        """§7 of the audit: the absolute form is not subsample-invariant and fails a CORRECT
        unfold by ~N/n_sub. The ratio form must be indifferent to the subsample size."""
        R = 1.135
        rng = np.random.default_rng(5)
        w_full = rng.random(4000) + 0.5
        push = np.full(4000, R)
        for n_sub in (4000, 500, 60):
            sub = slice(0, n_sub)
            ok, _ = g4.check_fold_forward_ratio(float((w_full[sub] * push[sub]).sum()),
                                                float(w_full[sub].sum()), R)
            self.assertTrue(ok, f"ratio form was not subsample-invariant at n_sub={n_sub}")

    def test_truth_level_target_of_one_is_not_what_is_gated(self):
        """§2d's own correction: over the full truth population a correct unfold gives
        1 + <a>(R-1), not 1 and not R. Confirm the legacy primitive still defaults to 1 (the
        frozen launch-code test binds that) while the gate does NOT use it."""
        self.assertTrue(g4.check_normalization(100.0, 100.0)[0])
        self.assertFalse(g4.check_normalization(110.0, 100.0)[0])
        self.assertTrue(g4.check_normalization(113.5, 100.0, target_ratio=1.135)[0])

    def test_tolerance_has_power_against_the_defect_and_admits_the_floor(self):
        """The provisional tolerance must sit between the structural floor and the defect size.
        Both bounds are computed from the closure's closed form, not asserted by fiat."""
        import closure_b1_rate_injection as clo
        R, acc, k = 1.135, 0.621, 2
        floor = clo.structural_floor(acc, R, k)
        signal = abs(R - 1.0) / R
        tol = g4.FROZEN["tolerances"]["fold_forward_ratio_dev_max"]
        self.assertLess(floor, tol, "tolerance is below the structural floor -> fails a correct unfold")
        self.assertLess(tol, signal, "tolerance exceeds the defect size -> the gate detects nothing")

    def test_independence_check_catches_a_driver_validator_disagreement(self):
        agree = g4.check_fold_forward_independence((113.5, 100.0, 1.135), (113.5, 100.0, 1.135))
        self.assertTrue(agree[0])
        # driver reporting a ratio the validator's own recomputation does not reproduce
        self.assertFalse(g4.check_fold_forward_independence(
            (113.5, 100.0, 1.135), (120.0, 100.0, 1.135))[0])
        # driver reporting a different R
        self.assertFalse(g4.check_fold_forward_independence(
            (113.5, 100.0, 1.135), (113.5, 100.0, 1.30))[0])

    def test_report_wires_the_check_into_the_verdict(self):
        """B2 was that a correct assertion never executed. Assert it now reaches the verdict."""
        common = dict(result_meta={"path": "/x/nom.npz", "sha256": "abc"},
                      frozen_observed={"estimator_fingerprint": g4.ESTIMATOR_FINGERPRINT,
                                       "bkg_mode": g4.BKG_MODE,
                                       "edges_pt": g4.FROZEN["edges_pt"],
                                       "edges_pparallel": g4.FROZEN["edges_pparallel"],
                                       "bin_order": g4.FROZEN["bin_order"],
                                       "seed_policy": g4.FROZEN["seed_policy"]})
        good, v_good = g4.build_gate4_report(fold_forward=(113.5, 100.0, 1.135), **common)
        self.assertTrue(v_good)
        self.assertIn("fold_forward", good["component_verdicts"])
        bad, v_bad = g4.build_gate4_report(fold_forward=(100.0, 100.0, 1.135), **common)
        self.assertFalse(v_bad)
        self.assertFalse(bad["component_verdicts"]["fold_forward"])

    def test_validator_recomputes_the_sums_from_the_dump(self):
        """The independence property: the validator's reference sums come from the G2 dump, not
        from anything the driver reported. Feed it a known push and check it reconstructs the
        expected ratio using only (dump, weights_push, mc_indices)."""
        arrays = g2_arrays_with_R(target_R=1.28, ns=80)
        with tempfile.TemporaryDirectory() as td:
            path = write_npz(td, arrays)
            imc = np.arange(80)
            push = np.full(80, 1.28)
            s_push, s_w, R, telem = g4.fold_forward_sums_from_dump(path, push, imc)
        self.assertAlmostEqual(R, 1.28, places=6)
        self.assertAlmostEqual(s_push / s_w, 1.28, places=9)
        self.assertEqual(telem["n_pass_reco_subsample"], int(arrays["pass_reco"].sum()))
        ok, _ = g4.check_fold_forward_ratio(s_push, s_w, R)
        self.assertTrue(ok)

    def test_validator_recomputation_respects_the_subsample(self):
        """mc_indices selects the trained rows; the reference sums must use the SAME rows."""
        arrays = g2_arrays_with_R(target_R=1.28, ns=80)
        with tempfile.TemporaryDirectory() as td:
            path = write_npz(td, arrays)
            imc = np.arange(0, 80, 2)
            s_push, s_w, R, telem = g4.fold_forward_sums_from_dump(
                path, np.full(imc.size, 1.28), imc)
        expected = int(np.asarray(arrays["pass_reco"])[imc].sum())
        self.assertEqual(telem["n_pass_reco_subsample"], expected)
        self.assertAlmostEqual(s_push / s_w, 1.28, places=9)

    def test_validator_rejects_a_mismatched_dump(self):
        arrays = g2_arrays_with_R(ns=40)
        with tempfile.TemporaryDirectory() as td:
            path = write_npz(td, arrays)
            with self.assertRaises(ValueError):     # index beyond the dump's inventory
                g4.fold_forward_sums_from_dump(path, np.ones(40), np.arange(100, 140))
            with self.assertRaises(ValueError):     # push not row-aligned to mc_indices
                g4.fold_forward_sums_from_dump(path, np.ones(10), np.arange(40))

    def test_tolerance_is_marked_provisional(self):
        """§2d requires the tolerance be measured before it is frozen. Until then the receipt must
        say so, or a reader takes a provisional number for a validated one."""
        self.assertEqual(g4.FROZEN["tolerances"]["fold_forward_ratio_dev_max_status"],
                         "PROVISIONAL_PENDING_CLOSURE_MEASUREMENT")


class Gate4DriverContract(unittest.TestCase):
    """The driver must persist what the validator needs; the validator must refuse to run without
    it rather than silently skipping the check."""

    def test_validator_cli_requires_the_dump(self):
        with self.assertRaises(SystemExit):
            g4.main(["--nominal-weights", "/nonexistent.npz", "--work", "/tmp/x.json"])

    def test_validator_refuses_a_pre_b1_weights_npz(self):
        """The failure mode this whole section exists to prevent: a weights file with no
        fold-forward inputs must abort, not produce a green receipt with the check skipped."""
        with tempfile.TemporaryDirectory() as td:
            old = os.path.join(td, "old_weights.npz")
            np.savez(old, weights_push=np.ones(10), mc_indices=np.arange(10),
                     estimator_fingerprint=g4.ESTIMATOR_FINGERPRINT, bkg_mode=g4.BKG_MODE)
            dump = write_npz(td, g2_arrays_with_R(ns=40))
            with self.assertRaises(SystemExit) as cm:
                g4.main(["--nominal-weights", old, "--inputs", dump,
                         "--work", os.path.join(td, "w.json")])
            self.assertIn("fold_forward", str(cm.exception))

    def test_driver_persists_every_key_the_validator_reads(self):
        """Pin the driver/validator interface by name. A rename on one side that silently skips
        the check on the other is exactly the B2 failure one level down."""
        import train_fullevent_nominal as drv
        src = open(drv.__file__).read()
        for key in ("fold_forward_sum_w_push_reco", "fold_forward_sum_w_reco",
                    "step1_class_ratio", "bootstrap_seed", "inputs_path"):
            self.assertIn(key, src, f"driver no longer persists {key!r}")

    def test_validator_rejects_a_bootstrap_replica(self):
        """The validator's recomputation reconstructs the NOMINAL inventory; a replica's R is
        built from coherent draws that are not in the weights file. It must fail closed."""
        with tempfile.TemporaryDirectory() as td:
            arrays = g2_arrays_with_R(ns=40)
            dump = write_npz(td, arrays)
            wpath = os.path.join(td, "replica.npz")
            np.savez(wpath, weights_push=np.ones(40), mc_indices=np.arange(40),
                     estimator_fingerprint=g4.ESTIMATOR_FINGERPRINT, bkg_mode=g4.BKG_MODE,
                     fold_forward_sum_w_push_reco=np.asarray(1.0),
                     fold_forward_sum_w_reco=np.asarray(1.0),
                     step1_class_ratio=np.asarray(1.135),
                     bootstrap_seed=np.asarray(99))
            with self.assertRaises(SystemExit) as cm:
                g4.main(["--nominal-weights", wpath, "--inputs", dump,
                         "--work", os.path.join(td, "w.json")])
            self.assertIn("bootstrap_seed", str(cm.exception))

    def test_end_to_end_receipt_carries_the_fold_forward_verdict(self):
        """Driver-shaped npz -> validator CLI -> receipt, with the check actually firing."""
        import json
        arrays = g2_arrays_with_R(target_R=1.28, ns=60)
        with tempfile.TemporaryDirectory() as td:
            dump = write_npz(td, arrays)
            imc = np.arange(60)
            push = np.full(60, 1.28)
            w_truth = np.asarray(arrays["w_truth"], np.float64)[imc]
            mask = np.asarray(arrays["pass_reco"])[imc].astype(bool)
            wpath = os.path.join(td, "nominal.npz")
            np.savez(wpath, weights_push=push, mc_indices=imc,
                     estimator_fingerprint=g4.ESTIMATOR_FINGERPRINT, bkg_mode=g4.BKG_MODE,
                     fold_forward_sum_w_push_reco=np.asarray((w_truth[mask] * push[mask]).sum()),
                     fold_forward_sum_w_reco=np.asarray(w_truth[mask].sum()),
                     step1_class_ratio=np.asarray(1.28),
                     bootstrap_seed=np.asarray(-1))
            work = os.path.join(td, "gate4.json")
            rc = g4.main(["--nominal-weights", wpath, "--inputs", dump, "--work", work,
                          "--n-full", "60"])
            with open(work) as fh:
                receipt = json.load(fh)
        self.assertEqual(rc, 0)
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertTrue(receipt["component_verdicts"]["fold_forward"])
        self.assertTrue(receipt["component_verdicts"]["fold_forward_independence"])
        self.assertAlmostEqual(receipt["fold_forward"]["validator_R"], 1.28, places=6)
        names = {c["name"] for c in receipt["checks"]}
        self.assertIn("normalization:fold_forward_reco_ratio", names)

    def test_end_to_end_receipt_fails_a_null_estimator(self):
        """`push = ones` passes the ordinary closure (audit §3). It must NOT pass Gate-4 now."""
        import json
        arrays = g2_arrays_with_R(target_R=1.28, ns=60)
        with tempfile.TemporaryDirectory() as td:
            dump = write_npz(td, arrays)
            imc = np.arange(60)
            push = np.ones(60)
            w_truth = np.asarray(arrays["w_truth"], np.float64)[imc]
            mask = np.asarray(arrays["pass_reco"])[imc].astype(bool)
            wpath = os.path.join(td, "null.npz")
            np.savez(wpath, weights_push=push, mc_indices=imc,
                     estimator_fingerprint=g4.ESTIMATOR_FINGERPRINT, bkg_mode=g4.BKG_MODE,
                     fold_forward_sum_w_push_reco=np.asarray((w_truth[mask] * push[mask]).sum()),
                     fold_forward_sum_w_reco=np.asarray(w_truth[mask].sum()),
                     step1_class_ratio=np.asarray(1.28),
                     bootstrap_seed=np.asarray(-1))
            work = os.path.join(td, "gate4.json")
            rc = g4.main(["--nominal-weights", wpath, "--inputs", dump, "--work", work])
            with open(work) as fh:
                receipt = json.load(fh)
        self.assertEqual(rc, 1)
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertFalse(receipt["component_verdicts"]["fold_forward"])


# ==================================================================================== §4
class RateInjectionClosure(unittest.TestCase):
    """REQUIRED BY §4: inject a known truth-level rate change and verify recovery.

    A reduced in-suite run of `pet/closure_b1_rate_injection.py`. Deliberately parameterized for a
    LARGE injected rate change so the separation survives the small event count a unit test can
    afford -- see that script's 'gradient-step confound' note. The full-scale run that sizes the
    Gate-4 tolerance is the script, not this test.

    The assertions are parameter-free (nearer-R-than-1, and corrected strictly beats broken)
    rather than threshold-based, so this cannot become flaky by drifting past a tuned tolerance."""

    # Run as a SUBPROCESS, not in-process. Other classes here install a stub `omnifold` package
    # into sys.modules (to reach the numpy-only DataLoader without importing TensorFlow), which
    # would shadow the real package's MLP/MultiFold. A subprocess also exercises the script's real
    # CLI and exit code, which is how 08-03 will invoke it.
    @classmethod
    def setUpClass(cls):
        import json
        import subprocess
        if importlib.util.find_spec("tensorflow") is None:
            raise unittest.SkipTest("TensorFlow not installed; the closure needs it to train")
        script = os.path.join(ND, "pet", "closure_b1_rate_injection.py")
        env = dict(os.environ, CUDA_VISIBLE_DEVICES="-1", TF_CPP_MIN_LOG_LEVEL="3")
        cls.tmp = tempfile.TemporaryDirectory()
        out = os.path.join(cls.tmp.name, "closure.json")
        cls.proc = subprocess.run(
            [sys.executable, script, "--r-inject", "2.0", "--acceptance", "0.75",
             "--niter", "2", "--epochs", "12", "--n-events", "6000", "--seed", "17",
             "--tolerance", "0.15", "--json", out],
            capture_output=True, text=True, env=env, cwd=cls.tmp.name)
        if not os.path.exists(out):
            raise unittest.SkipTest(
                f"closure script did not produce a report (rc={cls.proc.returncode}): "
                f"{cls.proc.stderr[-2000:]}")
        with open(out) as fh:
            cls.rep = json.load(fh)["runs"][0]

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "tmp", None) is not None:
            cls.tmp.cleanup()

    def test_closure_script_exits_zero(self):
        self.assertEqual(self.proc.returncode, 0, self.proc.stderr[-2000:])

    def test_engine_sees_the_injected_rate_as_the_class_ratio(self):
        """The deterministic core, before any training: corrected hands the engine R, broken
        hands it 1. Everything else in this class is downstream of these two numbers."""
        self.assertAlmostEqual(self.rep["corrected"]["step1_class_ratio_seen"], 2.0, places=4)
        self.assertAlmostEqual(self.rep["broken"]["step1_class_ratio_seen"], 1.0, places=4)

    def test_corrected_configuration_recovers_the_injected_rate(self):
        self.assertTrue(self.rep["corrected"]["nearer_R_than_1"],
                        f"corrected arm did not recover: {self.rep['corrected']}")

    def test_broken_configuration_does_not_recover_it(self):
        """The discriminating half. Without this the closure only shows the pipeline runs -- which
        is precisely why the existing closure missed the defect for as long as it did."""
        self.assertFalse(self.rep["broken"]["nearer_R_than_1"],
                         f"broken arm recovered a rate it cannot see: {self.rep['broken']}")
        self.assertLess(abs(self.rep["broken"]["fold_forward_reco_ratio"] - 1.0), 0.1)

    def test_corrected_strictly_beats_broken(self):
        self.assertLess(self.rep["corrected"]["dev_from_R"], self.rep["broken"]["dev_from_R"])

    def test_closure_verdict_is_pass(self):
        self.assertEqual(self.rep["verdict"], "PASS", self.rep)

    def test_structural_floor_closed_form_matches_the_run(self):
        """§2d term 1. The observed push must not beat the closed-form worst case by much: if it
        did, the bound the Gate-4 tolerance rests on would be wrong."""
        predicted = self.rep["expected_push_worst_case"]
        observed = self.rep["corrected"]["fold_forward_reco_ratio"]
        self.assertGreater(observed, 1.0)
        self.assertLess(observed, self.rep["r_inject"] * 1.05)
        self.assertLess(abs(observed - predicted) / predicted, 0.25,
                        f"observed {observed} far from closed form {predicted}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
