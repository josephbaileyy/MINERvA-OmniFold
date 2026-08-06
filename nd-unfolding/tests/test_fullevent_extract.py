"""The full-event extractor (AUDIT-FINDINGS-20260731 J02).

`extract_fullevent_fps.py` is new, so there is no prior behaviour to preserve and every test here
is about a specific way the extraction can be wrong while looking right:

  * coverage -- a cross section binned over the 2M training subsample instead of the 49.2M
    inventory, which is J02's own failure and is invisible in the output;
  * provenance -- extracting against a different dump, a bootstrap replica, or a result trained on
    the reduced cross-check schema;
  * input space -- a step-2 model fed inputs normalized differently from the ones it was trained
    on, which returns confident wrong weights and cannot be detected downstream;
  * the arithmetic -- against `xsec_nd.extract_cross_section_nd` on a hand-computable case.

Login-safe. The push stage needs TensorFlow and a trained checkpoint and is not exercised here;
what IS exercised is every guard around it plus the extraction arithmetic, with ROOT-dependent
`unfold_2d_omnifold_unbinned` replaced by a stub carrying the two constants the extractor reads
from it (the flux histogram loader and the fiducial nucleon count). `flux_universe` and `xsec_nd`
are the REAL modules -- the flux remap is the piece J29 lives in and stubbing it would test
nothing.
"""
import contextlib
import inspect
import os
import sys
import tempfile
import types
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(ND)
for _p in (os.path.join(ND, "pet"), ND):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fullevent_fps_dataloader as fed        # noqa: E402
import extract_fullevent_fps as ex            # noqa: E402

PT_REF_EDGES = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
                0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]     # u2d.PT_EDGES, 14 bins
N_NUCLEONS = 3.2352943296224835e30


@contextlib.contextmanager
def stub_u2d(flux_value=1.0e-5):
    """Stand in for `unfold_2d_omnifold_unbinned`, which imports ROOT at module load.

    Only the three names the extractor reads are provided, and `load_flux_bins` asserts it was
    asked for the REFERENCE grid rather than the analysis grid -- passing the FPS edges straight
    to the flux loader is the mistake the bin-centre remap exists to prevent."""
    mod = types.ModuleType("unfold_2d_omnifold_unbinned")
    mod.PT_EDGES = list(PT_REF_EDGES)
    mod.TRACKER_FIDUCIAL_N_NUCLEONS = N_NUCLEONS

    def load_flux_bins(mc_path, hist_name, pt_edges):
        assert list(pt_edges) == list(PT_REF_EDGES), "flux must be loaded on its OWN grid"
        return np.full(len(PT_REF_EDGES) - 1, float(flux_value)), None

    mod.load_flux_bins = load_flux_bins
    saved = sys.modules.get("unfold_2d_omnifold_unbinned")
    present = "unfold_2d_omnifold_unbinned" in sys.modules
    sys.modules["unfold_2d_omnifold_unbinned"] = mod
    try:
        yield mod
    finally:
        if present:
            sys.modules["unfold_2d_omnifold_unbinned"] = saved
        else:
            sys.modules.pop("unfold_2d_omnifold_unbinned", None)


def tiny_dump(td, n=500, seed=0, name="G2.npz"):
    """A minimal g2-fullevent-v1 npz with only what the xsec stage reads."""
    rng = np.random.default_rng(seed)
    ts = np.column_stack([rng.uniform(0.1, 3.0, n), rng.uniform(1.0, 20.0, n),
                          rng.uniform(0, 2, n), rng.uniform(0, 2, n)]).astype(np.float32)
    path = os.path.join(td, name)
    np.savez(path,
             edges_0=fed.CANONICAL_PT_EDGES, edges_1=fed.CANONICAL_PPARALLEL_EDGES,
             truth_scalars=ts, w_truth=(rng.random(n) + 0.5).astype(np.float32),
             pass_truth=np.ones(n, bool), pass_reco=rng.random(n) < 0.6,
             data_pot=np.asarray(1.0e20))
    return path, n


CONTRACT = {
    "multifold_name": "fe_nominal_nominal",
    "weights_folder": "/nowhere/w_nominal",
    "step2_checkpoint": "/nowhere/w_nominal/OmniFold_fe_nominal_nominal_iter1_step2.weights.h5",
    "pet_arch": {"num_feat_gen": 8, "num_evt": 2, "num_part": 12, "num_transformer": 2,
                 "num_heads": 2, "projection_dim": 32, "local": True, "K": 3,
                 "coord_idx": [5, 6, 7]},
    "event_features_reco": list(fed.DEFAULT_EVT_FEATURES),
    "event_features_truth": list(fed.DEFAULT_TRUTH_EVT_FEATURES),
    "reco_cloud_cols": list(fed.RECO_CLOUD_COLS),
    "truth_norm_mean": [1.0, 6.0], "truth_norm_std": [0.5, 3.0],
    "reco_norm_mean": [1.0] * len(fed.DEFAULT_EVT_FEATURES),
    "reco_norm_std": [1.0] * len(fed.DEFAULT_EVT_FEATURES),
}


def weights_npz(td, name="nominal.npz", contract=CONTRACT, **over):
    kw = dict(weights_push=np.ones(10), mc_indices=np.arange(10),
              estimator_fingerprint=ex.ESTIMATOR_FINGERPRINT,
              bootstrap_seed=np.asarray(-1),
              inputs_path=np.asarray(os.path.join(td, "G2.npz")),
              inputs_sha256=np.asarray("a" * 64),
              inference_contract=np.asarray(contract, dtype=object))
    kw.update(over)
    p = os.path.join(td, name)
    np.savez(p, **kw)
    return p


# ============================================================================================
class PushCoverage(unittest.TestCase):
    """J02's coverage half, stated as the recoil path already states it."""

    def test_ordered_full_range_passes(self):
        self.assertEqual(ex.validate_push_coverage(np.ones(100), np.arange(100), 100), [])

    def test_a_training_subsample_is_rejected(self):
        idx = np.sort(np.random.default_rng(0).choice(100, 40, replace=False))
        problems = ex.validate_push_coverage(np.ones(40), idx, 100)
        self.assertTrue(any("coverage" in p for p in problems), problems)

    def test_a_full_but_unordered_index_is_rejected(self):
        """Same length, same set, wrong order -- the one a length check cannot see, and the one
        that silently pairs every push weight with the wrong event."""
        idx = np.random.default_rng(1).permutation(100)
        problems = ex.validate_push_coverage(np.ones(100), idx, 100)
        self.assertTrue(any("ordered full-sample range" in p for p in problems), problems)

    def test_nonfinite_and_negative_are_rejected(self):
        w = np.ones(10); w[3] = np.nan
        self.assertTrue(any("non-finite" in p
                            for p in ex.validate_push_coverage(w, np.arange(10), 10)))
        w = np.ones(10); w[3] = -1.0
        self.assertTrue(any("negative" in p
                            for p in ex.validate_push_coverage(w, np.arange(10), 10)))


class InferenceContract(unittest.TestCase):
    def test_a_pre_j01_artifact_is_refused_by_name(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "old.npz")
            np.savez(p, weights_push=np.ones(4), mc_indices=np.arange(4),
                     estimator_fingerprint=ex.ESTIMATOR_FINGERPRINT)
            with self.assertRaises(SystemExit) as cm:
                ex.read_inference_contract(p)
            self.assertIn("inference_contract", str(cm.exception))
            self.assertIn("normalization", str(cm.exception))

    def test_a_bootstrap_replica_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            p = weights_npz(td, bootstrap_seed=np.asarray(77))
            with self.assertRaises(SystemExit) as cm:
                ex.read_inference_contract(p)
            self.assertIn("bootstrap_seed=77", str(cm.exception))

    def test_a_reduced_schema_result_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            c = dict(CONTRACT, event_features_reco=list(fed.REDUCED_EVT_FEATURES))
            p = weights_npz(td, contract=c)
            with self.assertRaises(SystemExit) as cm:
                ex.read_inference_contract(p)
            self.assertIn("CROSS-CHECK ONLY", str(cm.exception))

    def test_a_wrong_fingerprint_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            p = weights_npz(td, estimator_fingerprint=np.asarray("pet-reduced-fps-cross"))
            with self.assertRaises(SystemExit):
                ex.read_inference_contract(p)

    def test_a_contract_missing_the_normalization_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            c = {k: v for k, v in CONTRACT.items() if k != "truth_norm_mean"}
            p = weights_npz(td, contract=c)
            with self.assertRaises(SystemExit) as cm:
                ex.read_inference_contract(p)
            self.assertIn("truth_norm_mean", str(cm.exception))

    def test_a_different_dump_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            p = weights_npz(td)
            c = ex.read_inference_contract(p)
            with self.assertRaises(SystemExit) as cm:
                ex._assert_same_dump(c, os.path.join(td, "SOMETHING_ELSE.npz"))
            self.assertIn("not the dump this result was trained on", str(cm.exception))
            ex._assert_same_dump(c, os.path.join(td, "restaged", "G2.npz"))   # basename matches


class EngineReweighterShim(unittest.TestCase):
    """The shim runs the ENGINE's reweight, so it has to satisfy everything that method touches.

    Checked by reading `MultiFold.reweight`'s source for `self.<attr>` rather than by running it
    (that needs TensorFlow). If the engine grows a new `self.` dependency, this fails and names
    it -- which is the whole risk of calling a method on a hand-built instance."""

    def test_the_shim_supplies_every_attribute_reweight_reads(self):
        src_path = os.path.join(ROOT, "omnifold_nn", "omnifold", "omnifold.py")
        src = open(src_path).read()
        start = src.index("    def reweight(self")
        end = src.index("\n    def ", start + 10)
        body = src[start:end]
        import re
        needed = set(re.findall(r"self\.([A-Za-z_][A-Za-z_0-9]*)", body))
        supplied = set(inspect.getsource(ex._engine_reweighter).split("of.")[1:])
        supplied = {s.split()[0].split("=")[0].strip() for s in supplied}
        missing = needed - supplied
        self.assertFalse(missing,
                         f"MultiFold.reweight reads self.{sorted(missing)} and the extractor's "
                         "shim does not supply it")

    def test_the_shim_does_not_reimplement_the_f3_transform(self):
        """CLM-008 F3: one shared implementation, or training and extraction disagree in the
        saturation tail. A local `np.exp(np.clip(...))` here would be the second one."""
        src = inspect.getsource(ex)
        self.assertNotIn("REWEIGHT_LOGIT_CAP", src)
        self.assertNotIn("np.clip(logit", src)


class RowStream(unittest.TestCase):
    """The chunk loop's correctness AND the reason it exists.

    `np.load(npz)[key]` materializes the whole member on every index, and `mmap_mode` is silently
    ignored for npz files, so the obvious `d["part_gen"][lo:hi]` inside a chunk loop decompresses
    the entire 49.2M-row cloud once per chunk -- slower and more memory-hungry than not chunking at
    all, while looking exactly like chunking."""

    def _npz(self, td):
        import zipfile
        a = np.arange(120, dtype=np.float32).reshape(10, 4, 3)
        b = np.arange(50, dtype=np.float32).reshape(10, 5)
        p = os.path.join(td, "s.npz")
        np.savez_compressed(p, part_gen=a, truth_scalars=b)
        return zipfile.ZipFile(p), a, b

    def test_sequential_reads_reconstruct_the_member_exactly(self):
        with tempfile.TemporaryDirectory() as td:
            zf, a, b = self._npz(td)
            s = ex._RowStream(zf, "part_gen")
            self.assertEqual(s.n_rows, 10)
            self.assertEqual(tuple(s.shape), a.shape)
            got = np.concatenate([s.read(3), s.read(3), s.read(4)])
            np.testing.assert_array_equal(got, a)
            s.close()
            s2 = ex._RowStream(zf, "truth_scalars")
            np.testing.assert_array_equal(np.concatenate([s2.read(1), s2.read(9)]), b)
            s2.close()

    def test_reading_past_the_end_fails_closed(self):
        """A silently short final chunk would leave the tail of w_push at whatever np.empty gave
        it -- finite, plausible, and wrong."""
        with tempfile.TemporaryDirectory() as td:
            zf, _a, _b = self._npz(td)
            s = ex._RowStream(zf, "part_gen")
            with self.assertRaises(SystemExit) as cm:
                s.read(11)
            self.assertIn("truncated", str(cm.exception))
            s.close()

    def test_mmap_mode_is_not_relied_on(self):
        """Documenting the trap in an executable form: np.load(mmap_mode=...) on an npz returns an
        NpzFile whose members are ordinary in-memory arrays, so it buys nothing here."""
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "m.npz")
            np.savez_compressed(p, a=np.arange(10))
            with np.load(p, mmap_mode="r") as d:
                self.assertNotIsInstance(d["a"], np.memmap)
            self.assertNotIn("mmap_mode", inspect.getsource(ex.reweight_full_inventory))

    def test_off_acceptance_rows_are_pinned_to_one_like_runstep2(self):
        """FINDING-20260802-extractor-pass-truth-mask: the full-inventory pass must pin
        `pass_truth == False` rows to exactly 1.0, because `MultiFold.RunStep2` does
        (`omnifold.py:203-205`). Without it the two passes disagree on every off-acceptance row by
        construction and `check_subsample_agreement` fails closed on a CORRECT result -- measured at
        max rel dev 9.655e-01 on Delta 20778127.

        Structural, in the idiom of the mmap test above: a behavioural version needs a trained
        step-2 model and a point-cloud fixture, so it could only live in a GPU integration test,
        which is precisely where this defect already hid for a month.
        """
        src = inspect.getsource(ex.reweight_full_inventory)
        self.assertIn("np.ones(n", src,
                      "out must be initialized to ones; np.empty leaves unwritten rows as garbage")
        self.assertNotIn("np.empty(n", src)
        self.assertIn("pass_truth[lo:hi]", src,
                      "each chunk must be masked by pass_truth, not assigned wholesale")

    def test_the_pin_reports_whether_it_was_vacuous(self):
        """A guard that cannot distinguish "no off-acceptance rows existed" from "they all agreed"
        reads as evidence when it is not. The telemetry must say which."""
        src = inspect.getsource(ex.reweight_full_inventory)
        for key in ("n_off_acceptance_pinned", "subsample_agreement_is_vacuous"):
            self.assertIn(key, src)


class SubsampleAgreement(unittest.TestCase):
    def test_agreement_passes_within_the_nondeterminism_floor(self):
        rng = np.random.default_rng(0)
        full = rng.random(200) + 0.5
        idx = np.sort(rng.choice(200, 60, replace=False))
        ref = full[idx] * (1.0 + rng.normal(0, 1e-5, 60))       # float32/GPU-scale jitter
        c = {"_subsample_indices": idx, "_subsample_push": ref}
        got = ex.check_subsample_agreement(full, c, tol=1e-3)
        self.assertTrue(got["checked"])
        self.assertLess(got["max_rel_dev"], 1e-3)

    def test_a_real_disagreement_fails_closed(self):
        """This is the guard that makes the whole reweight-all pass falsifiable: without it, a
        model rebuilt at the wrong architecture, or fed a re-derived normalization, produces
        plausible weights and nothing anywhere notices."""
        rng = np.random.default_rng(0)
        full = rng.random(200) + 0.5
        idx = np.sort(rng.choice(200, 60, replace=False))
        ref = full[idx] * 1.05                                   # 5%: not a float32 artifact
        c = {"_subsample_indices": idx, "_subsample_push": ref}
        with self.assertRaises(SystemExit) as cm:
            ex.check_subsample_agreement(full, c, tol=1e-3)
        self.assertIn("not the one that produced this result", str(cm.exception))

    def test_absent_reference_is_reported_not_silently_skipped(self):
        got = ex.check_subsample_agreement(np.ones(5), {})
        self.assertFalse(got["checked"])
        self.assertIn("reason", got)


class ExtractionArithmetic(unittest.TestCase):
    def test_completeness_is_the_reco_and_truth_fraction(self):
        edges = [np.array([0.0, 1.0, 2.0]), np.array([0.0, 10.0])]
        pt = np.array([0.5, 0.5, 0.5, 1.5])
        pp = np.array([5.0, 5.0, 5.0, 5.0])
        w = np.array([1.0, 1.0, 2.0, 5.0])
        pass_truth = np.ones(4, bool)
        pass_reco = np.array([True, False, True, False])
        comp, denom, numer = fed_completeness(pt, pp, w, pass_truth, pass_reco, edges)
        self.assertAlmostEqual(float(denom[0, 0]), 4.0)
        self.assertAlmostEqual(float(numer[0, 0]), 3.0)
        self.assertAlmostEqual(float(comp[0, 0]), 0.75)
        self.assertAlmostEqual(float(comp[1, 0]), 0.0)      # nothing passes reco there

    def test_an_empty_denominator_leaves_the_cell_at_zero(self):
        edges = [np.array([0.0, 1.0, 2.0]), np.array([0.0, 10.0])]
        comp, denom, _ = fed_completeness(np.array([0.5]), np.array([5.0]), np.array([1.0]),
                                          np.array([True]), np.array([True]), edges)
        self.assertEqual(float(denom[1, 0]), 0.0)
        self.assertEqual(float(comp[1, 0]), 0.0)

    def test_xsec_matches_the_shared_nd_helper(self):
        """The extraction must equal `xsec_nd.extract_cross_section_nd` on the same inputs -- it
        is a port of PETxsec5D, not a second formula."""
        from xsec_nd import extract_cross_section_nd
        import flux_universe
        with tempfile.TemporaryDirectory() as td:
            path, n = tiny_dump(td)
            push = np.random.default_rng(3).random(n) + 0.5
            with stub_u2d(flux_value=2.5e-5):
                xsec, telem = ex.extract_xsec(path, push, "unused.root", "hFlux")
            with np.load(path) as d:
                ts = np.asarray(d["truth_scalars"], np.float64)
                w = np.asarray(d["w_truth"], np.float64)
                pt_m = np.asarray(d["pass_truth"]).astype(bool)
                pr_m = np.asarray(d["pass_reco"]).astype(bool)
                edges = [np.asarray(d["edges_0"], float), np.asarray(d["edges_1"], float)]
                pot = float(np.asarray(d["data_pot"]).item())
            coords = np.column_stack([ts[:, 0], ts[:, 1]])
            counts, _ = np.histogramdd(coords[pt_m], bins=edges, weights=(w * push)[pt_m])
            comp, _, _ = ex.completeness_2d(ts[:, 0], ts[:, 1], w, pt_m, pr_m, edges)
            flux = flux_universe.flux_on_target_grid(
                np.full(len(PT_REF_EDGES) - 1, 2.5e-5), edges[0],
                np.asarray(PT_REF_EDGES, float))
            want, _ = extract_cross_section_nd(counts, comp, flux, pot, N_NUCLEONS, edges,
                                               flux_axis=0)
            np.testing.assert_allclose(xsec, want, rtol=0, atol=0)
            self.assertEqual(telem["shape"], [15, 19])
            # PETxsec5D's comp_rescale is deliberately NOT carried over, and the telemetry has to
            # say so rather than leave a reader to assume the 5D anchoring applied here too.
            self.assertTrue(telem["completeness_anchor"].startswith("NONE"))

    def test_the_extended_pt_bin_gets_a_flux_not_a_silent_one(self):
        """J29's failure mode, on the CV side: the [4.5,30] FPS bin has no reference flux bin of
        its own. It must ride the bin-centre remap (clamped to the last reference bin), not be
        left at a scale of 1 -- which would inflate that bin's cross section by ~1/flux."""
        import flux_universe
        flux = flux_universe.flux_on_target_grid(
            np.full(len(PT_REF_EDGES) - 1, 2.5e-5),
            np.asarray(fed.CANONICAL_PT_EDGES, float), np.asarray(PT_REF_EDGES, float))
        self.assertEqual(flux.shape, (len(fed.CANONICAL_PT_EDGES) - 1,))
        self.assertAlmostEqual(float(flux[-1]), 2.5e-5)      # NOT 1.0, NOT 0.0

    def test_a_non_fps_grid_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            path, n = tiny_dump(td)
            with np.load(path) as d:
                arrays = {k: np.asarray(d[k]) for k in d.files}
            arrays["edges_0"] = np.linspace(0.0, 4.5, 16)     # paper-ish, not the FPS grid
            p2 = os.path.join(td, "bad_grid.npz")
            np.savez(p2, **arrays)
            with stub_u2d():
                with self.assertRaises(ValueError) as cm:
                    ex.extract_xsec(p2, np.ones(n), "unused.root", "hFlux")
            self.assertIn("FPS-GUARD", str(cm.exception))

    def test_misaligned_push_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            path, n = tiny_dump(td)
            with stub_u2d():
                with self.assertRaises(SystemExit) as cm:
                    ex.extract_xsec(path, np.ones(n - 1), "unused.root", "hFlux")
            self.assertIn("row-aligned", str(cm.exception))

    def test_total_xsec_is_the_bin_volume_weighted_sum(self):
        edges = [np.array([0.0, 2.0]), np.array([0.0, 5.0])]
        self.assertAlmostEqual(ex.total_xsec_2d(np.array([[3.0]]), edges), 30.0)


def fed_completeness(*a, **k):
    return ex.completeness_2d(*a, **k)


if __name__ == "__main__":
    unittest.main()
