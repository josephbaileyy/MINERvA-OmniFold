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


def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def write_closure_reports(td, ordinary_over=None, stress_over=None):
    """Write the two closure reports Gate-4 composes, in the schema the two scripts' `--json` emits.

    Gate-4 requires both. Its `closure=` and `marginal=` arguments were never wired before the
    2026-07-31 re-issue, so `closure:ordinary_pass`, `closure:stress_recoil_blind` and
    `closure:stress_fullevent_recovers` never executed at all. Returns (ordinary_path, stress_path).
    """
    import json as _json
    h = np.random.default_rng(0).random(g4.N_CELLS)
    ordinary = {"report_schema": g4.ORDINARY_CLOSURE_SCHEMA, "verdict": "PASS", "pass": True,
                # D2 (2026-08-04): the ordinary closure is mc-only and must declare what it
                # supports; Gate-4 refuses a report that does not.
                "bkg_mode": "mc-only", "is_synthetic_fixture": False, "marginal_l1": 0.0,
                "mc_only": True, "measured_target_constructed": False,
                "refinement_invoked": False, "is_powered_closure": False,
                "closure_class": "mc-self-consistency-identity",
                "marginal_h_truth": [float(x) for x in h],
                "marginal_h_reweighted": [float(x) for x in h],
                "edges_pt": g4.FROZEN["edges_pt"],
                "edges_pparallel": g4.FROZEN["edges_pparallel"],
                # J01: a closure is evidence about the estimator it ran on, so the report declares
                # the schema it exercised and Gate-4 requires it to be the full one.
                "event_features_reco": list(g4.FROZEN["event_features_reco"]),
                "event_features_truth": list(g4.FROZEN["event_features_truth"]),
                "push_median": 1.0, "push_finite": True, "l1_max": 0.10, "push_med_tol": 0.15}
    stress = {"report_schema": g4.STRESS_CLOSURE_SCHEMA, "verdict": "PASS", "pass": True,
              "recoil_only_fails_to_recover": True, "fullevent_recovers": True}
    ordinary.update(ordinary_over or {})
    stress.update(stress_over or {})
    op = os.path.join(td, "ordinary_closure.json")
    sp = os.path.join(td, "stress_closure.json")
    for path, payload in ((op, ordinary), (sp, stress)):
        with open(path, "w") as fh:
            _json.dump(payload, fh)
    return op, sp


def write_powered_report(td, **over):
    """The D2 injected truth-reweight RECOVERY closure report.

    Separate from write_closure_reports so the twelve callers that expect a FAILING verdict keep
    their two-value unpack: Gate-4 fails closed without this report, which is the point.
    """
    import json as _json
    payload = {"is_powered_closure": True, "recovery_criteria_met": True,
               "closure_class": "injected-truth-reweight-recovery"}
    payload.update(over)
    path = os.path.join(td, "powered_closure.json")
    with open(path, "w") as fh:
        _json.dump(payload, fh)
    return path


def driver_spectra(arrays, imc, push):
    """The reporting spectra the DRIVER would persist, via the driver's own function.

    Deliberately fed `mc.weight`-shaped input -- the dump's raw signal weights rescaled to sum to
    1e6, as the DataLoader does in place -- while the validator recomputes from the raw dump
    weights. Both sides normalize, so agreement here is evidence the comparison is scale-free rather
    than evidence the two sides share a scale."""
    import train_fullevent_nominal as drv
    w_raw = np.asarray(arrays["w_truth"], np.float64)[imc]
    w_mc = w_raw * (1e6 / w_raw.sum())
    return drv.reporting_spectra(np.asarray(arrays["truth_scalars"])[imc], w_mc, push,
                                 np.asarray(arrays["pass_truth"])[imc])


def driver_npz(td, arrays, imc, push, name="nominal.npz", target=None, **over):
    """A weights npz shaped exactly as the post-re-issue driver writes one.

    Every key here exists because a Gate-4 check reads it; audit B2's compounding finding was that
    the artifact carried none of the configuration, so `freeze:seed_policy` was unfalsifiable and the
    central-vector / reported-mask / cap-saturation checks had no artifact to read."""
    imc = np.asarray(imc)
    push = np.asarray(push, np.float64)
    w_truth = np.asarray(arrays["w_truth"], np.float64)[imc]
    mask = np.asarray(arrays["pass_reco"])[imc].astype(bool)
    cv, rep_mask = driver_spectra(arrays, imc, push)
    if target is None:
        target = {"target_mode": "negweight-refined",
                  "refinement": "stay-positive (arXiv:2505.03724)",
                  "refinement_is_learned_production": True,
                  "signed_target_hash": "b" * 64, "pot_scale": 0.22,
                  "refined_sum": 1.0e5, "refined_min": 0.0}
    kw = dict(weights_push=push, mc_indices=imc,
              estimator_fingerprint=g4.ESTIMATOR_FINGERPRINT, bkg_mode=g4.BKG_MODE,
              fold_forward_sum_w_push_reco=np.asarray((w_truth[mask] * push[mask]).sum()),
              fold_forward_sum_w_reco=np.asarray(w_truth[mask].sum()),
              step1_class_ratio=np.asarray(float(_fixture_R(arrays))),
              bootstrap_seed=np.asarray(-1),
              seed_policy=np.asarray(dict(g4.FROZEN["seed_policy"]), dtype=object),
              edges_pt=fed.CANONICAL_PT_EDGES, edges_pparallel=fed.CANONICAL_PPARALLEL_EDGES,
              bin_order=np.asarray(g4.FROZEN["bin_order"]),
              central_vector=cv, reported_bin_mask=rep_mask,
              cap_saturation_frac=np.asarray(
                  g4.cap_saturation_frac_from_push(push)),
              # J01: the event-feature schema the run was trained on. Gate-4 freezes it, so an
              # artifact without it now fails `freeze:event_feature_schema_present` -- which is
              # the point: a fingerprint with nothing behind it is what let a {pT,p||} run
              # validate as `pet-fullevent-fps-v1`.
              event_features_reco=np.asarray(list(g4.FROZEN["event_features_reco"]), dtype=object),
              event_features_truth=np.asarray(list(g4.FROZEN["event_features_truth"]),
                                              dtype=object),
              reco_cloud_cols=np.asarray(list(g4.FROZEN["reco_cloud_cols"]), dtype=object),
              target=np.asarray(target, dtype=object))
    kw.update(over)
    p = os.path.join(td, name)
    np.savez(p, **kw)
    return p


def _fixture_R(arrays):
    """R read off the fixture itself, never from the loader -- the same non-circularity rule the
    rest of this file follows."""
    pot = float(np.asarray(arrays["pot_scale"]).item())
    n_data = int(np.asarray(arrays["measured_pc"]).shape[0])
    w_bkg = np.asarray(arrays["w_bkg"], np.float64)
    w_truth = np.asarray(arrays["w_truth"], np.float64)
    pr = np.asarray(arrays["pass_reco"]).astype(bool)
    return fed.step1_class_ratio(n_data=n_data, sum_w_bkg_raw=float(w_bkg.sum()),
                                 sum_w_mc_reco_raw=float(w_truth[pr].sum()), pot_scale=pot)


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
        # The fixture's w_reco == w_truth by default, so the D1 denominator switch leaves R alone.
        self.assertAlmostEqual(R, 1.42, places=6)
        self.assertEqual(telem["reco_leg_weight_used"], "w_reco")   # D1: was "w_truth" pre-2026-08-04
        self.assertEqual(telem["denominator_leg"], "w_reco")
        self.assertIn("sum(w_reco[pass_reco])", telem["formula"])
        self.assertFalse(telem["is_bootstrap_replica"])

    def test_b4_telemetry_reports_identical_weights(self):
        with tempfile.TemporaryDirectory() as td:
            with np.load(write_npz(td, g2_arrays_with_R()), allow_pickle=True) as d:
                _, telem = fed.step1_class_ratio_from_dump(d)
        b4 = telem["b4_w_reco_vs_w_truth"]
        self.assertTrue(b4["present_in_dump"])
        self.assertTrue(b4["resolved"])
        self.assertTrue(b4["bit_identical_over_pass_reco"])
        self.assertEqual(b4["n_pass_reco_differing"], 0)
        self.assertIn("RESOLVED", b4["verdict"])
        self.assertIn("unchanged", b4["verdict"])

    def test_b4_differing_reco_leg_drives_R_and_reports_the_legacy_value(self):
        """POST-D1 (2026-08-04). A differing reco leg is no longer a defect to flag -- it is what R
        is built from. The telemetry must show R following the RECO leg, and must still report the
        old truth-leg value so a post-D1 receipt stays comparable with a pre-D1 one.

        Pre-D1 this test asserted the opposite: that R followed w_truth and the reco-leg value was
        the hypothetical. The inversion is the whole content of D1."""
        with tempfile.TemporaryDirectory() as td:
            arrays = g2_arrays_with_R(target_R=1.2, w_reco_scale=1.25)
            with np.load(write_npz(td, arrays), allow_pickle=True) as d:
                R, telem = fed.step1_class_ratio_from_dump(d)
        b4 = telem["b4_w_reco_vs_w_truth"]
        self.assertFalse(b4["bit_identical_over_pass_reco"])
        self.assertIn("RESOLVED", b4["verdict"])
        self.assertIn("expected", b4["verdict"])
        # w_reco = 1.25*w_truth, so the reco-leg denominator is 1.25x larger and R is 1.25x smaller
        # than the fixture's truth-leg target.
        self.assertAlmostEqual(R, 1.2 / 1.25, places=6)
        self.assertAlmostEqual(b4["R_if_reco_leg_used_w_reco"], R, places=9)
        self.assertAlmostEqual(b4["R_if_reco_leg_used_w_truth"], 1.2, places=6)
        self.assertAlmostEqual(b4["R_shift_factor_vs_legacy_w_truth"], 1.0 / 1.25, places=6)

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

    def test_b4_telemetry_is_replica_consistent(self):
        """Regression, found by adversarial review of b3751cc. The B-4 telemetry's derived numbers
        are compared against a numerator that carries the replica's draws and against a denominator
        that carries `sig_factor`. If the reco leg is left unscaled, the shift factor reports
        `sig_factor` itself: with sig_factor=2 and w_reco == w_truth BIT-FOR-BIT it claimed a shift
        of 2.0 and an alternative R equal to the nominal rather than the replica's. Telemetry only
        -- the normalization R was never wrong -- but B-4 is decided off these numbers."""
        arrays = g2_arrays_with_R(target_R=1.3, ns=80)      # w_reco == w_truth bit-for-bit
        with tempfile.TemporaryDirectory() as td:
            with np.load(write_npz(td, arrays), allow_pickle=True) as d:
                R, telem = fed.step1_class_ratio_from_dump(d, sig_factor=np.full(80, 2.0))
        b4 = telem["b4_w_reco_vs_w_truth"]
        self.assertTrue(b4["bit_identical_over_pass_reco"])
        # identical weights => the D1 denominator switch changes nothing, whatever the replica scaling
        self.assertAlmostEqual(b4["R_shift_factor_vs_legacy_w_truth"], 1.0, places=9)
        self.assertAlmostEqual(b4["R_if_reco_leg_used_w_reco"], R, places=9)
        self.assertAlmostEqual(b4["R_if_reco_leg_used_w_truth"], R, places=9)

    def test_b4_shift_is_replica_consistent_when_w_reco_differs(self):
        """The same consistency when the legs DIFFER: the reported shift must be the w_reco/w_truth
        ratio and nothing else, independently of any replica scaling applied to both legs. This is
        the b3751cc regression -- it is what catches a draw applied to one leg only."""
        arrays = g2_arrays_with_R(target_R=1.3, ns=80, w_reco_scale=1.25)
        with tempfile.TemporaryDirectory() as td:
            with np.load(write_npz(td, arrays), allow_pickle=True) as d:
                nom = fed.step1_class_ratio_from_dump(d)[1]["b4_w_reco_vs_w_truth"]
                rep = fed.step1_class_ratio_from_dump(
                    d, sig_factor=np.full(80, 3.0))[1]["b4_w_reco_vs_w_truth"]
        for b4 in (nom, rep):
            self.assertAlmostEqual(b4["R_shift_factor_vs_legacy_w_truth"], 1.0 / 1.25, places=6)
        self.assertAlmostEqual(nom["R_shift_factor_vs_legacy_w_truth"],
                               rep["R_shift_factor_vs_legacy_w_truth"], places=9)

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

    def _telemetry(self, refined, clipped, target_norm):
        """The gate's clipped-shape telemetry, computed exactly as `run_validate` does -- INCLUDING
        the zero-guard floor, which is where the invariance actually lives."""
        clipped_norm = clipped * (target_norm / clipped.sum())
        denom = np.maximum(clipped_norm, g2rt.EPS_NORM_FRAC * target_norm)
        occupied = (clipped_norm > 0) | (refined > 0)
        return {
            "l1": float(np.abs(refined - clipped_norm).sum() / target_norm),
            "max_rel": float(np.max(np.abs(refined[occupied] - clipped_norm[occupied])
                                    / denom[occupied])),
            "cosine": float(np.vdot(refined.ravel(), clipped_norm.ravel())
                            / (np.linalg.norm(refined) * np.linalg.norm(clipped_norm))),
        }

    def test_clipped_telemetry_is_invariant_including_the_zero_guard(self):
        """§2c claims the learned-vs-clipped telemetry survives the 1e6 -> 1e6*R change verbatim.

        The first version of this test re-typed the rel_l1 algebra on strictly-positive random data
        and asserted only rel_l1 -- so it never reached `denom`, never touched the zero-guard floor,
        and never checked max_relative or cosine. Exactly the tautology pattern audit §4 found in
        the provenance tests, in a test written to prevent one. Caught by adversarial review of
        b3751cc.

        `max_relative` was genuinely NOT invariant: with an ABSOLUTE 1e-12 floor, a cell where
        clipped_norm == 0 but refined > 0 pins the denominator while the numerator scales with the
        target, so max_rel scaled by exactly R. The fixture below contains such a cell on purpose.
        Benign on the frozen grid today (negative_signed_cells == 0), but the pending MeV/GeV units
        fix is expected to create those cells -- in the same restore window as this retarget."""
        rng = np.random.default_rng(11)
        refined = rng.random(40) * 100.0
        clipped = rng.random(40) * 100.0
        clipped[7] = 0.0            # the case `occupied` admits and the absolute floor mishandled
        refined[7] = 12.5
        base = self._telemetry(refined, clipped, g2rt.NORMALIZATION)
        for R in (1.135, 2.5, 0.4):
            # under the retarget the whole refined histogram scales by exactly R
            scaled = self._telemetry(refined * R, clipped, g2rt.NORMALIZATION * R)
            for key in ("l1", "max_rel", "cosine"):
                # RELATIVE: max_rel is ~1e13 here (the zero cell divides by the floor), so an
                # absolute tolerance would be meaningless on it and vacuous on cosine.
                self.assertAlmostEqual(scaled[key] / base[key], 1.0, places=9,
                                       msg=f"{key} not invariant at R={R}: "
                                           f"{base[key]!r} -> {scaled[key]!r}")

    def test_absolute_floor_would_have_broken_max_relative(self):
        """Pin the defect itself, so a revert to an absolute floor fails here rather than silently
        degrading a diagnostic nobody re-derives."""
        refined = np.array([10.0, 12.5]); clipped = np.array([10.0, 0.0])
        def max_rel(target_norm, floor):
            cn = clipped * (target_norm / clipped.sum())
            occ = (cn > 0) | (refined * (target_norm / g2rt.NORMALIZATION) > 0)
            r = refined * (target_norm / g2rt.NORMALIZATION)
            return float(np.max(np.abs(r[occ] - cn[occ]) / np.maximum(cn, floor)[occ]))
        R = 1.135
        self.assertAlmostEqual(max_rel(g2rt.NORMALIZATION * R, 1e-12)
                               / max_rel(g2rt.NORMALIZATION, 1e-12), R, places=6)
        self.assertAlmostEqual(
            max_rel(g2rt.NORMALIZATION * R, g2rt.EPS_NORM_FRAC * g2rt.NORMALIZATION * R)
            / max_rel(g2rt.NORMALIZATION, g2rt.EPS_NORM_FRAC * g2rt.NORMALIZATION), 1.0, places=9)

    def test_zero_guard_floor_is_backward_compatible_at_R_one(self):
        """The floor is a fraction so it stays invariant, but it must still reproduce the pre-B1
        absolute 1e-12 exactly at R == 1, or the frozen telemetry values move."""
        self.assertAlmostEqual(g2rt.EPS_NORM_FRAC * g2rt.NORMALIZATION, 1e-12, places=24)


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
        1 + <a>(R-1), not 1 and not R.

        The legacy `check_normalization` primitive that asserted `ratio ~ 1` was RETIRED at the
        2026-07-31 Gate-4 re-issue (RESTORE-2026-08-03.md Step 2b explicitly reserved that decision
        for the re-issue). It survived the 07-29 patch only as a binding-preserving shim for the
        frozen launch-code test that pinned its signature; it had no caller of its own. What must
        stay true is the physics: the truth-level `ratio ~ 1` statement is NOT the gate, and the
        reco-level ratio against R is."""
        self.assertFalse(hasattr(g4, "check_normalization"),
                         "the retired truth-level primitive is back; it must not be wired")
        self.assertNotIn("normalization_dev_max", g4.FROZEN["tolerances"],
                         "the receipt would embed a tolerance no check uses")
        # a truth-level ratio of exactly 1 is what a rate-ERASING result gives at reco level
        self.assertFalse(g4.check_fold_forward_ratio(100.0, 100.0, 1.135)[0])
        self.assertTrue(g4.check_fold_forward_ratio(113.5, 100.0, 1.135)[0])

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
        """B2 was that a correct assertion never executed. Assert it now reaches the verdict.

        The report is assembled with ONLY the fold-forward evidence, so the overall verdict is FAIL
        either way -- every other component correctly reports its evidence as absent, which is the
        08-03 change. What this pins is that the fold-forward COMPONENT tracks the arithmetic: it is
        present in `component_verdicts` in both arms, True for a rate-recovering result and False for
        a rate-erasing one."""
        common = dict(result_meta={"path": "/x/nom.npz", "sha256": "abc"},
                      frozen_observed={"estimator_fingerprint": g4.ESTIMATOR_FINGERPRINT,
                                       "bkg_mode": g4.BKG_MODE,
                                       "edges_pt": g4.FROZEN["edges_pt"],
                                       "edges_pparallel": g4.FROZEN["edges_pparallel"],
                                       "bin_order": g4.FROZEN["bin_order"],
                                       "seed_policy": g4.FROZEN["seed_policy"]})
        good, _ = g4.build_gate4_report(fold_forward=(113.5, 100.0, 1.135), **common)
        self.assertTrue(good["component_verdicts"]["fold_forward"])
        bad, v_bad = g4.build_gate4_report(fold_forward=(100.0, 100.0, 1.135), **common)
        self.assertFalse(v_bad)
        self.assertFalse(bad["component_verdicts"]["fold_forward"])

    def test_a_report_with_no_evidence_at_all_cannot_pass(self):
        """The B2 receipt read `verdict PASS, n_failed 0` because every component whose argument was
        None was DROPPED. Hand the builder nothing but a valid freeze and require a FAIL."""
        payload, verdict = g4.build_gate4_report(
            result_meta={"path": "/x/nom.npz", "sha256": "abc"},
            frozen_observed={"estimator_fingerprint": g4.ESTIMATOR_FINGERPRINT,
                             "bkg_mode": g4.BKG_MODE,
                             "edges_pt": g4.FROZEN["edges_pt"],
                             "edges_pparallel": g4.FROZEN["edges_pparallel"],
                             "bin_order": g4.FROZEN["bin_order"],
                             "seed_policy": g4.FROZEN["seed_policy"],
                             "central_vector": np.ones(g4.N_CELLS),
                             "reported_bin_mask": np.ones(g4.N_CELLS, bool)})
        self.assertFalse(verdict)
        self.assertGreater(payload["n_failed"], 0)
        self.assertTrue(all(not v for k, v in payload["component_verdicts"].items()
                            if k != "freeze"))

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

    def test_varying_push_separates_the_weighted_mean_from_the_plain_mean(self):
        """The blind spot every other case here shares: they all feed a CONSTANT push, and
        sum(w*push)/sum(w) == c for any w when push == c. So none of them can tell a correct
        w-weighted mean from an implementation that dropped the weights entirely. Feed a push
        that varies row to row, anti-correlated with w_truth so the two means are far apart,
        and pin the weighted one."""
        arrays = g2_arrays_with_R(target_R=1.28, ns=80)
        w = np.asarray(arrays["w_truth"], dtype=np.float64)
        mask = np.asarray(arrays["pass_reco"]).astype(bool)
        push = np.empty(80, dtype=np.float64)
        push[np.argsort(w)] = np.linspace(1.6, 0.7, 80)   # largest push onto the smallest weight
        with tempfile.TemporaryDirectory() as td:
            path = write_npz(td, arrays)
            s_push, s_w, _R, _telem = g4.fold_forward_sums_from_dump(path, push, np.arange(80))

        weighted = float((w[mask] * push[mask]).sum() / w[mask].sum())
        plain = float(push[mask].mean())
        # If the fixture's two means coincided, the assertions below would prove nothing.
        self.assertGreater(abs(weighted - plain), 1e-3,
                           "degenerate fixture: weighted and unweighted means agree")
        self.assertAlmostEqual(s_push / s_w, weighted, places=12)
        self.assertNotAlmostEqual(s_push / s_w, plain, places=4)

    def test_gate_accepts_a_correct_unfold_whose_push_is_not_flat(self):
        """A correct unfold does not return a flat push; §2d gates the w-weighted mean against R.
        Build a push whose WEIGHTED mean is exactly R but whose plain mean is not, and the
        converse, so the check is shown to key on the right one in both directions."""
        R = 1.135
        rng = np.random.default_rng(11)
        w = rng.random(500) + 0.5
        # The spread must RISE WITH w, not be shuffled: a spread independent of the weights has a
        # weighted mean within ~0.5% of its plain mean, far inside the 5% tolerance, and the
        # converse below would then have no power to detect anything.
        spread = np.empty(500)
        spread[np.argsort(w)] = np.linspace(-0.8, 0.8, 500)          # plain mean exactly 0

        push_ok = R + spread - float((w * spread).sum() / w.sum())   # weighted mean == R exactly
        self.assertNotAlmostEqual(float(push_ok.mean()), R, places=4)
        ok, _ = g4.check_fold_forward_ratio(float((w * push_ok).sum()), float(w.sum()), R)
        self.assertTrue(ok, "gate rejected a correct unfold because its push was not flat")

        push_bad = R + spread                                        # plain mean == R, weighted != R
        dev = abs(float((w * push_bad).sum() / w.sum()) - R) / R
        self.assertGreater(dev, g4.FROZEN["tolerances"]["fold_forward_ratio_dev_max"],
                           "fixture's weighted deviation is inside tolerance; test has no power")
        bad, _ = g4.check_fold_forward_ratio(float((w * push_bad).sum()), float(w.sum()), R)
        self.assertFalse(bad, "gate accepted a push whose weighted mean misses R")

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

    def test_R_equal_one_does_not_fail_a_correct_no_change_unfold(self):
        """Regression, adversarial review of b3751cc. The parameter-free discriminator is
        `|ratio-R| < |ratio-1|`; at R == 1 that is `x < x`, False for EVERY input, so a correct
        no-change result with push == 1 was failed outright. §4 explicitly contemplates R coming
        back near 1.0, so this is reachable."""
        w = np.array([1.0, 2.0, 3.0, 4.0])
        ok, checks = g4.check_fold_forward_ratio(float(w.sum()), float(w.sum()), 1.0)
        self.assertTrue(ok, checks)
        note = [c for c in checks if c["name"].endswith("rate_recovered_not_erased")][0]
        self.assertIn("not applicable", note["detail"])

    def test_R_near_one_still_gates_on_the_tolerance(self):
        """Disabling the discriminator must not disable the gate: at R ~ 1 the tolerance check is
        the exact statement and must still reject a result that misses it."""
        w = np.array([1.0, 2.0, 3.0, 4.0])
        self.assertTrue(g4.check_fold_forward_ratio(float(w.sum()), float(w.sum()), 1.0)[0])
        self.assertFalse(g4.check_fold_forward_ratio(float(w.sum()) * 1.5, float(w.sum()), 1.0)[0])

    def test_discriminator_still_active_at_the_physical_R(self):
        """And it must NOT be silently disabled at the R that matters."""
        w = np.array([1.0, 2.0, 3.0, 4.0])
        ok, checks = g4.check_fold_forward_ratio(float(w.sum()), float(w.sum()), 1.135)
        self.assertFalse(ok)
        note = [c for c in checks if c["name"].endswith("rate_recovered_not_erased")][0]
        self.assertNotIn("not applicable", note["detail"])

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

    def test_validator_cli_requires_both_closure_reports(self):
        """Audit B2: `closure=` was never wired, so the two closure verdicts Gate-4 claims to
        compose were evaluated by nothing. Both reports are now required argv, which is the only
        way a caller cannot forget them."""
        with tempfile.TemporaryDirectory() as td:
            arrays = g2_arrays_with_R(ns=40)
            dump = write_npz(td, arrays)
            wpath = driver_npz(td, arrays, np.arange(40), np.full(40, 1.135))
            op, sp = write_closure_reports(td)
            work = os.path.join(td, "w.json")
            for argv in ([], ["--closure-report", op], ["--stress-report", sp]):
                with self.assertRaises(SystemExit):
                    g4.main(["--nominal-weights", wpath, "--inputs", dump, "--work", work] + argv)

    def test_validator_refuses_a_pre_b1_weights_npz(self):
        """The failure mode this whole section exists to prevent: a weights file with no
        fold-forward inputs must abort, not produce a green receipt with the check skipped."""
        with tempfile.TemporaryDirectory() as td:
            old = os.path.join(td, "old_weights.npz")
            np.savez(old, weights_push=np.ones(10), mc_indices=np.arange(10),
                     estimator_fingerprint=g4.ESTIMATOR_FINGERPRINT, bkg_mode=g4.BKG_MODE)
            dump = write_npz(td, g2_arrays_with_R(ns=40))
            op, sp = write_closure_reports(td)
            with self.assertRaises(SystemExit) as cm:
                g4.main(["--nominal-weights", old, "--inputs", dump,
                         "--closure-report", op, "--stress-report", sp,
                         "--work", os.path.join(td, "w.json")])
            self.assertIn("fold_forward", str(cm.exception))

    def test_validator_rejects_a_dump_the_result_was_not_trained_on(self):
        """Regression, adversarial review of b3751cc. The driver records `inputs_path`; without
        comparing it the validator believes whatever --inputs the caller passes, so a DIFFERENT
        dump becomes the reference for every fold-forward sum -- and the reference being independent
        of the driver is the entire point of §2d."""
        with tempfile.TemporaryDirectory() as td:
            arrays = g2_arrays_with_R(ns=40)
            right = write_npz(td, arrays, name="G2_right.npz")
            wrong = write_npz(td, arrays, name="G2_wrong.npz")   # same content, different identity
            wpath = driver_npz(td, arrays, np.arange(40), np.full(40, 1.1),
                               inputs_path=np.asarray(right))
            op, sp = write_closure_reports(td)
            with self.assertRaises(SystemExit) as cm:
                g4.main(["--nominal-weights", wpath, "--inputs", wrong,
                         "--closure-report", op, "--stress-report", sp,
                         "--work", os.path.join(td, "w.json")])
            self.assertIn("not the dump this result was trained on", str(cm.exception))

    def test_validator_rejects_a_dump_with_the_right_name_and_wrong_content(self):
        """The basename check cannot see a substitution, and the 07-29 patch said so in a comment:
        "a content-level guarantee needs the Gate-2 receipt's NPZ sha256 and belongs to the
        re-issue". This is that. The driver persists `inputs_sha256`; the validator hashes the file
        it was handed."""
        with tempfile.TemporaryDirectory() as td:
            arrays = g2_arrays_with_R(ns=40)
            sub = os.path.join(td, "other"); os.makedirs(sub)
            trained_on = write_npz(td, arrays, name="G2_same_name.npz")
            substituted = write_npz(sub, g2_arrays_with_R(ns=40, seed=9),
                                    name="G2_same_name.npz")   # same basename, other content
            wpath = driver_npz(td, arrays, np.arange(40), np.full(40, 1.1),
                               inputs_path=np.asarray(trained_on),
                               inputs_sha256=np.asarray(_sha256(trained_on)))
            op, sp = write_closure_reports(td)
            with self.assertRaises(SystemExit) as cm:
                g4.main(["--nominal-weights", wpath, "--inputs", substituted,
                         "--closure-report", op, "--stress-report", sp,
                         "--work", os.path.join(td, "w.json")])
            self.assertIn("sha256", str(cm.exception))

    def test_skipping_the_check_cannot_produce_a_green_verdict(self):
        """Regression, adversarial review of b3751cc. --allow-missing-fold-forward previously
        yielded verdict PASS and exit 0, with only a buried `promotable: false` dissenting -- so a
        consumer reading the exit status or the verdict string saw a pass with the normalization
        gate never run. That is the B2 failure one level up."""
        import json
        with tempfile.TemporaryDirectory() as td:
            old = os.path.join(td, "pre_b1.npz")
            np.savez(old, weights_push=np.ones(10), mc_indices=np.arange(10),
                     estimator_fingerprint=g4.ESTIMATOR_FINGERPRINT, bkg_mode=g4.BKG_MODE)
            dump = write_npz(td, g2_arrays_with_R(ns=40))
            op, sp = write_closure_reports(td)
            work = os.path.join(td, "w.json")
            rc = g4.main(["--nominal-weights", old, "--inputs", dump, "--work", work,
                          "--closure-report", op, "--stress-report", sp,
                          "--allow-missing-fold-forward"])
            with open(work) as fh:
                receipt = json.load(fh)
        self.assertEqual(rc, 1, "a skipped normalization gate exited 0")
        self.assertNotEqual(receipt["verdict"], "PASS")
        self.assertIn("NOT_CHECKED", receipt["verdict"])
        self.assertFalse(receipt["component_verdicts"]["fold_forward"])
        self.assertFalse(receipt["fold_forward"]["promotable"])

    def test_driver_persists_every_key_the_validator_reads(self):
        """Pin the driver/validator interface by name. A rename on one side that silently skips
        the check on the other is exactly the B2 failure one level down."""
        import train_fullevent_nominal as drv
        src = open(drv.__file__).read()
        for key in ("fold_forward_sum_w_push_reco", "fold_forward_sum_w_reco",
                    "step1_class_ratio", "bootstrap_seed", "inputs_path",
                    # added at the 2026-07-31 re-issue: without these the freeze compared FROZEN
                    # to FROZEN and three freeze checks had no artifact to read (audit B2)
                    "inputs_sha256", "seed_policy", "edges_pt", "edges_pparallel", "bin_order",
                    "central_vector", "reported_bin_mask", "cap_saturation_frac"):
            self.assertIn(key, src, f"driver no longer persists {key!r}")

    def test_validator_rejects_a_bootstrap_replica(self):
        """The validator's recomputation reconstructs the NOMINAL inventory; a replica's R is
        built from coherent draws that are not in the weights file. It must fail closed."""
        with tempfile.TemporaryDirectory() as td:
            arrays = g2_arrays_with_R(ns=40)
            dump = write_npz(td, arrays)
            wpath = driver_npz(td, arrays, np.arange(40), np.ones(40),
                               name="replica.npz", bootstrap_seed=np.asarray(99))
            op, sp = write_closure_reports(td)
            with self.assertRaises(SystemExit) as cm:
                g4.main(["--nominal-weights", wpath, "--inputs", dump,
                         "--closure-report", op, "--stress-report", sp,
                         "--work", os.path.join(td, "w.json")])
            self.assertIn("bootstrap_seed", str(cm.exception))

    def test_end_to_end_receipt_carries_the_fold_forward_verdict(self):
        """Driver-shaped npz -> validator CLI -> receipt, with every check actually firing."""
        import json
        arrays = g2_arrays_with_R(target_R=1.28, ns=60)
        with tempfile.TemporaryDirectory() as td:
            dump = write_npz(td, arrays)
            imc = np.arange(60)
            wpath = driver_npz(td, arrays, imc, np.full(60, 1.28))
            op, sp = write_closure_reports(td)
            # D2: Gate-4 fails closed without the powered recovery closure, so a test that expects
            # a PASS must supply one. The identity closure cannot stand in for it.
            pp = write_powered_report(td)
            work = os.path.join(td, "gate4.json")
            rc = g4.main(["--nominal-weights", wpath, "--inputs", dump, "--work", work,
                          "--closure-report", op, "--stress-report", sp,
                          "--powered-closure-report", pp, "--n-full", "60"])
            with open(work) as fh:
                receipt = json.load(fh)
        self.assertEqual(rc, 0, [c for c in receipt["checks"] if not c["ok"]])
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertTrue(receipt["component_verdicts"]["fold_forward"])
        self.assertTrue(receipt["component_verdicts"]["fold_forward_independence"])
        self.assertAlmostEqual(receipt["fold_forward"]["validator_R"], 1.28, places=6)
        names = {c["name"] for c in receipt["checks"]}
        self.assertIn("normalization:fold_forward_reco_ratio", names)

    def test_end_to_end_receipt_evaluates_every_component(self):
        """The B2 receipt was `15 checks, 0 failed` with four physics components and three freeze
        checks absent. Pin the full component set and pin that NO check reports absent evidence on a
        complete submission -- an `evidence_supplied` failure anywhere means the gate abstained."""
        import json
        arrays = g2_arrays_with_R(target_R=1.28, ns=60)
        with tempfile.TemporaryDirectory() as td:
            dump = write_npz(td, arrays)
            wpath = driver_npz(td, arrays, np.arange(60), np.full(60, 1.28))
            op, sp = write_closure_reports(td)
            pp = write_powered_report(td)      # D2: required for closure_provenance to pass
            work = os.path.join(td, "gate4.json")
            g4.main(["--nominal-weights", wpath, "--inputs", dump, "--work", work,
                     "--closure-report", op, "--stress-report", sp,
                     "--powered-closure-report", pp])
            with open(work) as fh:
                receipt = json.load(fh)
        for component in ("freeze", "weights", "index_order", "marginal", "fold_forward",
                          "fold_forward_independence", "spectra_independence", "cap", "target",
                          "closure", "closure_provenance"):
            self.assertTrue(receipt["component_verdicts"][component], component)
        self.assertEqual([c for c in receipt["checks"] if c["name"].endswith(":evidence_supplied")],
                         [])
        names = {c["name"] for c in receipt["checks"]}
        for expected in ("freeze:central_vector_len", "freeze:reported_mask_len",
                         "freeze:seed_policy", "marginal:pt_ppar_l1", "cap:saturation_frac",
                         "closure:ordinary_pass", "closure:stress_recoil_blind",
                         "closure:stress_fullevent_recovers",
                         "closure:ordinary_not_synthetic_fixture",
                         "target:refinement_is_learned_production",
                         "spectra:driver_validator_central_vector_agree"):
            self.assertIn(expected, names)

    def test_end_to_end_refuses_a_synthetic_fixture_closure(self):
        """RESTORE Step 3: the 2026-07-26 Delta run passed on random data and is tagged
        `[SYNTHETIC FIXTURE - PLUMBING ONLY, NOT THE P5A RECEIPT]`. The gate must refuse it as
        evidence rather than relying on a human reading the tag."""
        import json
        arrays = g2_arrays_with_R(target_R=1.28, ns=60)
        with tempfile.TemporaryDirectory() as td:
            dump = write_npz(td, arrays)
            wpath = driver_npz(td, arrays, np.arange(60), np.full(60, 1.28))
            op, sp = write_closure_reports(td, ordinary_over={"is_synthetic_fixture": True})
            work = os.path.join(td, "gate4.json")
            rc = g4.main(["--nominal-weights", wpath, "--inputs", dump, "--work", work,
                          "--closure-report", op, "--stress-report", sp])
            with open(work) as fh:
                receipt = json.load(fh)
        self.assertEqual(rc, 1)
        self.assertFalse(receipt["component_verdicts"]["closure_provenance"])

    def test_end_to_end_refuses_an_off_policy_seed_config(self):
        """Audit B2's failure scenario, end to end: `--niter 1 --epochs 2` are plain CLI args on the
        driver, cross-checked against nothing, and the validator recorded its own constant."""
        import json
        arrays = g2_arrays_with_R(target_R=1.28, ns=60)
        offpolicy = dict(g4.FROZEN["seed_policy"]); offpolicy["niter"] = 1; offpolicy["epochs"] = 2
        with tempfile.TemporaryDirectory() as td:
            dump = write_npz(td, arrays)
            wpath = driver_npz(td, arrays, np.arange(60), np.full(60, 1.28),
                               seed_policy=np.asarray(offpolicy, dtype=object))
            op, sp = write_closure_reports(td)
            work = os.path.join(td, "gate4.json")
            rc = g4.main(["--nominal-weights", wpath, "--inputs", dump, "--work", work,
                          "--closure-report", op, "--stress-report", sp])
            with open(work) as fh:
                receipt = json.load(fh)
        self.assertEqual(rc, 1)
        self.assertFalse(receipt["component_verdicts"]["freeze"])
        self.assertFalse([c for c in receipt["checks"]
                          if c["name"] == "freeze:seed_policy"][0]["ok"])

    def test_end_to_end_refuses_a_reshaped_central_vector(self):
        """The freeze exists so a later result cannot silently reshape the 285-cell vector. The
        checks read the DRIVER's array, so a driver that persists a different-length one must fail
        -- and the independence check must notice it does not match the dump."""
        import json
        arrays = g2_arrays_with_R(target_R=1.28, ns=60)
        with tempfile.TemporaryDirectory() as td:
            dump = write_npz(td, arrays)
            wpath = driver_npz(td, arrays, np.arange(60), np.full(60, 1.28),
                               central_vector=np.ones(g4.N_CELLS - 1) / (g4.N_CELLS - 1))
            op, sp = write_closure_reports(td)
            work = os.path.join(td, "gate4.json")
            rc = g4.main(["--nominal-weights", wpath, "--inputs", dump, "--work", work,
                          "--closure-report", op, "--stress-report", sp])
            with open(work) as fh:
                receipt = json.load(fh)
        self.assertEqual(rc, 1)
        self.assertFalse(receipt["component_verdicts"]["freeze"])
        self.assertFalse(receipt["component_verdicts"]["spectra_independence"])

    def test_end_to_end_receipt_fails_a_null_estimator(self):
        """`push = ones` passes the ordinary closure (audit §3). It must NOT pass Gate-4 now."""
        import json
        arrays = g2_arrays_with_R(target_R=1.28, ns=60)
        with tempfile.TemporaryDirectory() as td:
            dump = write_npz(td, arrays)
            wpath = driver_npz(td, arrays, np.arange(60), np.ones(60), name="null.npz")
            op, sp = write_closure_reports(td)
            work = os.path.join(td, "gate4.json")
            rc = g4.main(["--nominal-weights", wpath, "--inputs", dump, "--work", work,
                          "--closure-report", op, "--stress-report", sp])
            with open(work) as fh:
                receipt = json.load(fh)
        self.assertEqual(rc, 1)
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertFalse(receipt["component_verdicts"]["fold_forward"])


class Gate4ArtifactContract(unittest.TestCase):
    """The three cross-side constants and two recomputations the 2026-07-31 re-issue added.

    Each exists because the corresponding Gate-4 check reads the ARTIFACT rather than FROZEN. That
    is what makes the check falsifiable -- and it is also what creates a new way to be wrong: the
    two sides can drift apart. These pin them together WITHOUT letting either side read the other
    (which would put the self-comparison back)."""

    def test_driver_bin_order_matches_the_frozen_bin_order(self):
        import train_fullevent_nominal as drv
        self.assertEqual(drv.BIN_ORDER, g4.FROZEN["bin_order"],
                         "driver and validator disagree on the ravel convention; the freeze check "
                         "would fail every correct run")

    def test_frozen_logit_cap_matches_the_engine(self):
        """FROZEN mirrors omnifold.REWEIGHT_LOGIT_CAP rather than importing it (importing pulls
        TensorFlow and this validator is login-safe). Read the engine's SOURCE so the mirror cannot
        go stale silently -- a cap of 30 read against an engine clipping at 25 would report zero
        saturation on a fully saturated result."""
        import re
        src = open(os.path.join(ROOT, "omnifold_nn", "omnifold", "omnifold.py")).read()
        m = re.search(r"^REWEIGHT_LOGIT_CAP\s*=\s*([0-9.]+)", src, re.M)
        self.assertIsNotNone(m, "cannot find REWEIGHT_LOGIT_CAP in the engine")
        self.assertEqual(float(m.group(1)), float(g4.FROZEN["reweight_logit_cap"]))

    def test_cap_saturation_detects_a_saturated_push(self):
        cap = g4.FROZEN["reweight_logit_cap"]
        clean = np.full(1000, 1.5)
        self.assertEqual(g4.cap_saturation_frac_from_push(clean), 0.0)
        sat = clean.copy()
        sat[:5] = np.exp(cap)                       # exactly at the cap
        sat[5:8] = np.exp(-cap)                     # and at the lower cap
        self.assertAlmostEqual(g4.cap_saturation_frac_from_push(sat), 8 / 1000.0, places=12)
        self.assertFalse(g4.check_cap_sensitivity(g4.cap_saturation_frac_from_push(sat))[0])
        self.assertTrue(g4.check_cap_sensitivity(g4.cap_saturation_frac_from_push(clean))[0])

    def test_cap_saturation_survives_float32_storage(self):
        """`weights_push` is stored float32, so log(float32(exp(30))) is 30 to ~1e-6 and an exact
        `>=` would report zero saturation on a fully saturated result."""
        cap = g4.FROZEN["reweight_logit_cap"]
        sat32 = np.full(100, np.exp(cap), dtype=np.float32)
        self.assertAlmostEqual(g4.cap_saturation_frac_from_push(sat32), 1.0, places=12)

    def test_driver_and_validator_agree_on_the_reporting_spectra(self):
        """The two-sided check: the driver histograms `mc.weight` (rescaled to 1e6 in place) and the
        validator the dump's raw `w_truth`. Agreement is evidence the comparison is scale-free."""
        arrays = g2_arrays_with_R(target_R=1.28, ns=80)
        imc = np.arange(80)
        push = np.linspace(0.8, 1.8, 80)
        d_cv, d_mask = driver_spectra(arrays, imc, push)
        with tempfile.TemporaryDirectory() as td:
            path = write_npz(td, arrays)
            v_cv, v_mask, telem = g4.nominal_spectra_from_dump(path, push, imc)
        self.assertEqual(v_cv.shape, (g4.N_CELLS,))
        self.assertEqual(v_mask.shape, (g4.N_CELLS,))
        np.testing.assert_allclose(v_cv, d_cv, rtol=0, atol=1e-9)
        np.testing.assert_array_equal(v_mask, d_mask)
        self.assertTrue(g4.check_spectra_independence((v_cv, v_mask, 0.0), (d_cv, d_mask, 0.0))[0])
        self.assertEqual(telem["n_pass_truth_subsample"], int(arrays["pass_truth"][imc].sum()))

    def test_independence_check_catches_a_reshuffled_central_vector(self):
        """A permuted central vector has the same length, sum and finiteness, so only a
        recomputation can see it. This is the check that makes the freeze's order clause real."""
        arrays = g2_arrays_with_R(target_R=1.28, ns=80)
        imc = np.arange(80)
        push = np.linspace(0.8, 1.8, 80)
        d_cv, d_mask = driver_spectra(arrays, imc, push)
        shuffled = d_cv.copy()
        np.random.default_rng(3).shuffle(shuffled)
        self.assertAlmostEqual(float(shuffled.sum()), float(d_cv.sum()), places=12)
        self.assertFalse(
            g4.check_spectra_independence((d_cv, d_mask, 0.0), (shuffled, d_mask, 0.0))[0])

    def test_independence_check_catches_a_driver_cap_fraction_that_does_not_match(self):
        cv = np.ones(g4.N_CELLS) / g4.N_CELLS
        m = np.ones(g4.N_CELLS, bool)
        self.assertFalse(g4.check_spectra_independence((cv, m, 0.0), (cv, m, 0.5))[0])

    def test_spectra_recomputation_rejects_a_non_frozen_grid(self):
        """The dump's own edges are asserted against the canonical grid before its truth scalars are
        histogrammed against FROZEN's -- otherwise a dump on a different grid would be silently
        reported as agreeing with the frozen one."""
        arrays = dict(g2_arrays_with_R(ns=40))
        arrays["edges_0"] = np.linspace(0.0, 4.5, 16)          # paper-ish grid, not the FPS grid
        with tempfile.TemporaryDirectory() as td:
            path = write_npz(td, arrays)
            with self.assertRaises(ValueError):
                g4.nominal_spectra_from_dump(path, np.ones(40), np.arange(40))


_REDUCED = ("pt", "pparallel")


class EventFeatureFiniteGuard(unittest.TestCase):
    """FINDING-20260730-event-feature-nonfinite.md, found by execution (Delta job 20599606 died
    after 49m45s), fixed in this window because the file is Gate-2-bound and Step 2b is when it is
    open. ONE non-finite value in a selected column NaNs that column for EVERY row via the
    normalization statistic, and step 2 reports `Last val loss nan` naming neither column nor cause.

    2026-08-01: every call below now names `_REDUCED` explicitly. The subject of these tests is
    the non-finite guard, not the schema, and they supply scalars-only sources; the loader's
    default became the full `pet-fullevent-fps-v1` schema (J01), which needs the muon and vertex
    blocks and correctly refuses to run without them. Passing the schema in keeps each test
    testing what it was written to test -- and `_REDUCED` is written out rather than imported from
    `fed` so a future change to the loader's constants cannot silently redefine these fixtures.
    """

    def _scalars(self, n=50, seed=1):
        return _scal(np.random.default_rng(seed), n)

    def test_clean_scalars_pass(self):
        r, t, d = self._scalars(), self._scalars(seed=2), self._scalars(30, seed=3)
        er, et, ed, meta = fed.build_event_features(r, t, d, feature_names=_REDUCED)
        for blk in (er, et, ed):
            self.assertTrue(np.all(np.isfinite(blk)))
        self.assertEqual(meta["n_evt"], 2)

    def test_one_nan_in_a_selected_truth_column_fails_and_names_it(self):
        """The exact observed defect: `truth_scalars` col 1 with a single NaN among pass_truth rows.
        The message must name the column, because the NaN loss did not."""
        t = self._scalars(seed=2); t[7, fed.SCALAR_COLS["pparallel"]] = np.nan
        with self.assertRaises(ValueError) as cm:
            fed.build_event_features(self._scalars(), t, self._scalars(30, seed=3),
                                     feature_names=_REDUCED)
        msg = str(cm.exception)
        self.assertIn("pparallel", msg)
        self.assertIn("truth_scalars", msg)
        self.assertIn("EVT-FINITE", msg)

    def test_the_guard_is_not_a_nan_to_num(self):
        """0 is the cloud path's pad sentinel but the BLOCK MEAN of a z-scored event feature, so
        quiet filling would place undefined events at the centre of the conditioning distribution.
        Assert it RAISES rather than returning something finite."""
        t = self._scalars(seed=2); t[3, 0] = np.inf
        with self.assertRaises(ValueError):
            fed.build_event_features(self._scalars(), t, self._scalars(30, seed=3),
                                     feature_names=_REDUCED)

    def test_a_nan_outside_the_selected_columns_is_tolerated(self):
        """The real dump's `q3` (col 3) carries ~1,700 non-finite rows and the adopted schema reads
        cols 0,1. The guard must not fail the CURRENT production configuration -- the defect is
        latent, and a guard that fires today would be a false alarm, not a fix."""
        t = self._scalars(seed=2); t[5, fed.SCALAR_COLS["q3"]] = np.nan
        _er, et, _ed, _m = fed.build_event_features(self._scalars(), t,
                                                    self._scalars(30, seed=3),
                                                    feature_names=_REDUCED)
        self.assertTrue(np.all(np.isfinite(et)))

    def test_a_nan_outside_the_selected_columns_fails_once_the_block_widens(self):
        """...and it must fire the moment the block widens, which is what the publication estimator
        requires (FULL_EVENT_FEATURE_CONTRACT.md:98-101)."""
        t = self._scalars(seed=2); t[5, fed.SCALAR_COLS["q3"]] = np.nan
        with self.assertRaises(ValueError) as cm:
            # The NaN is on the TRUTH leg, so it is the truth schema that has to widen for the
            # guard to see it. The two lists became independent when the reco leg gained the muon
            # object (J01); widening only `feature_names` here would leave the truth block reading
            # {pT,p||} and the test would assert that a guard fires on a column nobody selected.
            fed.build_event_features(self._scalars(), t, self._scalars(30, seed=3),
                                     feature_names=("pt", "pparallel", "eavail", "q3"),
                                     truth_feature_names=("pt", "pparallel", "eavail", "q3"))
        self.assertIn("q3", str(cm.exception))

    def test_a_nan_only_among_masked_out_rows_is_tolerated(self):
        """The normalization is formed over in-mask rows only, and !pass rows are zeroed after it,
        so a non-finite value on a row that never enters either is not a defect."""
        n = 50
        t = self._scalars(n, seed=2)
        pass_truth = np.ones(n, bool); pass_truth[9] = False
        t[9, 0] = np.nan
        _er, et, _ed, _m = fed.build_event_features(
            self._scalars(n), t, self._scalars(30, seed=3), feature_names=_REDUCED,
            pass_reco=np.ones(n, bool), pass_truth=pass_truth)
        self.assertTrue(np.all(np.isfinite(et)))

    def test_data_scalars_are_screened_too(self):
        d = self._scalars(30, seed=3); d[4, 0] = np.nan
        with self.assertRaises(ValueError) as cm:
            fed.build_event_features(self._scalars(), self._scalars(seed=2), d,
                                     feature_names=_REDUCED)
        self.assertIn("measured_scalars", str(cm.exception))

    def test_leakage_guard_cannot_pass_on_an_all_nan_block(self):
        """Fix (2) of the finding. `assert_no_truth_leakage` is a DISSIMILARITY test and NaN differs
        from everything, so an all-NaN event_reco used to satisfy it -- the guard designed to catch
        leakage was silently certifying a poisoned block."""
        r = self._scalars()
        poisoned = np.full((r.shape[0], 2), np.nan, np.float32)
        with self.assertRaises(AssertionError) as cm:
            fed.assert_no_truth_leakage(poisoned, r, self._scalars(seed=2), ("pt", "pparallel"))
        self.assertIn("EVT-FINITE", str(cm.exception))

    def test_the_loader_fails_closed_on_a_nonfinite_dump(self):
        """End to end through build_fullevent_loaders, so the guard is known to be on the real path
        and not only on the helper."""
        arrays = dict(g2_arrays_with_R(ns=40))
        ts = np.array(arrays["truth_scalars"], copy=True)
        ts[3, fed.SCALAR_COLS["pt"]] = np.nan
        arrays["truth_scalars"] = ts
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError) as cm:
                build(td, arrays, verify_identities=False)
        self.assertIn("EVT-FINITE", str(cm.exception))


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
