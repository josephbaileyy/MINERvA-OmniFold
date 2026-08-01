"""J28/J29 flux-universe normalization: the port, and the post-hoc rescale.

WHAT THE BUGS WERE
------------------
  * J28 -- three ND/5D kernels (`compare_unified_throw._xsec_for_weights`,
    `unified_throw_cov_5d._xsec_for_weights_5d`, `sweep_bank_5d.do_run`) applied a
    PPFX universe's event reweights and then divided by the CV flux integral
    Phi_CV instead of that universe's own Phi_u. They are three separate
    implementations, so a fix to one kernel does not reach the others.
  * J29 -- the ND driver remaps the 15-bin FPS pT grid onto the 14-bin reference
    flux histogram for CV, but its universe loop asked the histogram for bin
    `b+1` directly. For the `[4.5,30]` bin that reads the overflow, the `>0`
    validity test fails, and the scale silently stays at 1.

Both failures are silent by construction: the wrong answer is a plausible number,
never an exception. So every test here pairs "the fixed path is right" with "the
unfixed behaviour is refused", and the fixture flux values are chosen so that CV
and universe are distinguishable in every bin -- a fixture where Phi_u == Phi_CV
would pass against the bug.

Login-safe: synthetic arrays, no ROOT, no /pscratch, no unfolding. `flux_universe`
takes its ROOT import inside the reader and accepts an `.npz` carrying the same
`hFluxCV`/`hFluxUniv` arrays, which is what the synthetic slabs below drive.
"""
import ast
import contextlib
import glob
import io
import os
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ND)

import flux_universe as fu                 # noqa: E402
import rescale_flux_universes as rfu       # noqa: E402
from uq_math import joint_throw_covariance, mat_covariance   # noqa: E402
from xsec_nd import extract_cross_section_nd                 # noqa: E402

# The frozen 14-bin reference pT grid (2d-unfolding PT_EDGES) and the 15-bin FPS
# extension. Hard-coded rather than imported because unfold_2d_omnifold_unbinned
# pulls in ROOT; test_ref_edges_match_the_2d_grid re-derives them from the source
# so this copy cannot drift.
REF_PT_EDGES = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
                         0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50], float)
FPS_PT_EDGES = np.append(REF_PT_EDGES, 30.0)
N_REF = len(REF_PT_EDGES) - 1          # 14
N_UNIV = 6


def make_flux_table(n_ref=N_REF, n_univ=N_UNIV, seed=7):
    """CV flux + per-universe flux, every universe differing in every bin.

    Spread ~ +-8%, comparable to the real PPFX band, and deliberately never 1.0:
    a universe that equalled CV somewhere would hide exactly the bin the bug left
    at CV.
    """
    rng = np.random.default_rng(seed)
    phi_cv = 2.0e-5 * (1.0 + 0.01 * np.arange(n_ref))
    offsets = rng.uniform(0.04, 0.08, size=(n_univ, n_ref))
    signs = np.where(rng.random((n_univ, n_ref)) < 0.5, -1.0, 1.0)
    phi_univ = phi_cv[None, :] * (1.0 + signs * offsets)
    return phi_cv, phi_univ


def write_flux_npz(path, phi_cv, phi_univ):
    """Store as the TH2D does, [n_ref x n_univ], so the reader's transpose is used."""
    np.savez(path, hFluxCV=phi_cv, hFluxUniv=np.asarray(phi_univ).T)
    return path


def legacy_universe_scale(phi_cv, phi_univ, uidx, n_target):
    """The pre-fix ND-driver loop, verbatim, for regression comparison.

    `scale = ones(n_target)`, then `unf/cvf` per analysis bin `b` read straight
    out of reference bin `b+1`, skipped when either is non-positive. Reading past
    the histogram is the overflow, i.e. 0.
    """
    scale = np.ones(n_target)
    for b in range(n_target):
        cvf = phi_cv[b] if b < len(phi_cv) else 0.0
        unf = phi_univ[uidx][b] if b < phi_univ.shape[1] else 0.0
        if cvf > 0 and unf > 0:
            scale[b] = unf / cvf
    return scale


class RefGridRemap(unittest.TestCase):
    """flux_ref_index / flux_on_target_grid -- the one mapping CV and universes share."""

    def test_identity_when_grids_agree(self):
        phi_cv, _ = make_flux_table()
        got = fu.flux_on_target_grid(phi_cv, REF_PT_EDGES, REF_PT_EDGES)
        np.testing.assert_array_equal(got, phi_cv)
        np.testing.assert_array_equal(
            fu.flux_ref_index(REF_PT_EDGES, REF_PT_EDGES), np.arange(N_REF))

    def test_fps_extended_bin_takes_the_last_reference_bin(self):
        """J29: the 15th bin must inherit reference bin 13, not stay at CV."""
        idx = fu.flux_ref_index(FPS_PT_EDGES, REF_PT_EDGES)
        self.assertEqual(len(idx), len(FPS_PT_EDGES) - 1)
        np.testing.assert_array_equal(idx[:N_REF], np.arange(N_REF))
        self.assertEqual(idx[-1], N_REF - 1)

    def test_remap_is_a_centre_lookup_not_a_clipped_bin_index(self):
        """On the FPS grid `clip(arange(15), 0, 13)` happens to equal the centre
        lookup, so that grid alone cannot tell a real remap from a bin-index
        shortcut. Split every reference bin in two: now bin k must map to
        reference bin k//2, which no index-clipping scheme produces."""
        split = np.unique(np.concatenate(
            [REF_PT_EDGES, 0.5 * (REF_PT_EDGES[:-1] + REF_PT_EDGES[1:])]))
        idx = fu.flux_ref_index(split, REF_PT_EDGES)
        np.testing.assert_array_equal(idx, np.repeat(np.arange(N_REF), 2))
        self.assertFalse(np.array_equal(
            idx, np.clip(np.arange(len(split) - 1), 0, N_REF - 1)))
        phi_cv, _ = make_flux_table()
        np.testing.assert_allclose(
            fu.flux_on_target_grid(phi_cv, split, REF_PT_EDGES),
            np.repeat(phi_cv, 2))

    def test_missing_ref_edges_fails_closed_on_a_length_mismatch(self):
        phi_cv, _ = make_flux_table()
        with self.assertRaises(RuntimeError) as ctx:
            fu.flux_on_target_grid(phi_cv, FPS_PT_EDGES, None)
        self.assertIn("15", str(ctx.exception))

    def test_ref_edges_inconsistent_with_the_values_is_refused(self):
        phi_cv, _ = make_flux_table()
        with self.assertRaises(RuntimeError):
            fu.flux_on_target_grid(phi_cv, REF_PT_EDGES, REF_PT_EDGES[:-3])


class ReadTable(unittest.TestCase):

    def test_npz_round_trip_is_universe_major(self):
        phi_cv, phi_univ = make_flux_table()
        with tempfile.TemporaryDirectory() as td:
            path = write_flux_npz(os.path.join(td, "f.npz"), phi_cv, phi_univ)
            cv, un = fu.read_flux_universe_table(path)
        np.testing.assert_allclose(cv, phi_cv)
        self.assertEqual(un.shape, (N_UNIV, N_REF))
        np.testing.assert_allclose(un, phi_univ)

    def test_missing_file_fails_closed(self):
        with self.assertRaises(RuntimeError) as ctx:
            fu.read_flux_universe_table("/nonexistent/flux.npz")
        self.assertIn("Task #70", str(ctx.exception))

    def test_missing_histogram_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "f.npz")
            np.savez(path, hFluxCV=np.ones(N_REF))
            with self.assertRaises(RuntimeError) as ctx:
                fu.read_flux_universe_table(path)
        self.assertIn("hFluxUniv", str(ctx.exception))


class UniverseBins(unittest.TestCase):

    def setUp(self):
        self.phi_cv, self.phi_univ = make_flux_table()
        self._td = tempfile.TemporaryDirectory()
        self.path = write_flux_npz(os.path.join(self._td.name, "flux.npz"),
                                   self.phi_cv, self.phi_univ)
        self.addCleanup(self._td.cleanup)

    def test_returns_the_universes_own_integral(self):
        for u in range(N_UNIV):
            got = fu.flux_universe_bins(self.path, u, REF_PT_EDGES, self.phi_cv)
            np.testing.assert_allclose(got, self.phi_univ[u])
            self.assertFalse(np.allclose(got, self.phi_cv))

    def test_fps_grid_scales_every_bin_including_the_extended_one(self):
        """J29 regression: the fixed path and the pre-fix loop must disagree, and
        only in the extended bin -- the pre-fix loop left that one at CV."""
        cv_fps = fu.flux_on_target_grid(self.phi_cv, FPS_PT_EDGES, REF_PT_EDGES)
        for u in range(N_UNIV):
            fixed = fu.flux_universe_bins(self.path, u, FPS_PT_EDGES, cv_fps,
                                          ref_edges=REF_PT_EDGES)
            legacy = cv_fps * legacy_universe_scale(self.phi_cv, self.phi_univ, u,
                                                    len(FPS_PT_EDGES) - 1)
            # the 14 reference bins agree; the FPS bin does not
            np.testing.assert_allclose(fixed[:N_REF], legacy[:N_REF])
            self.assertAlmostEqual(legacy[-1], cv_fps[-1],
                                   msg="pre-fix loop should have left the FPS bin at CV")
            self.assertNotAlmostEqual(fixed[-1], cv_fps[-1])
            self.assertAlmostEqual(fixed[-1], self.phi_univ[u][N_REF - 1])

    def test_universe_index_out_of_range(self):
        with self.assertRaises(RuntimeError) as ctx:
            fu.flux_universe_bins(self.path, N_UNIV, REF_PT_EDGES, self.phi_cv)
        self.assertIn("out of range", str(ctx.exception))

    def test_cv_from_a_different_flux_production_is_refused(self):
        with self.assertRaises(RuntimeError) as ctx:
            fu.flux_universe_bins(self.path, 0, REF_PT_EDGES, self.phi_cv * 1.05)
        self.assertIn("same flux production", str(ctx.exception))

    def test_tiny_cv_drift_within_tolerance_is_accepted(self):
        nudged = self.phi_cv * (1.0 + 1e-9)
        fu.flux_universe_bins(self.path, 0, REF_PT_EDGES, nudged)

    def test_zero_universe_integral_fails_closed(self):
        broken = self.phi_univ.copy()
        broken[2, -1] = 0.0
        with tempfile.TemporaryDirectory() as td:
            path = write_flux_npz(os.path.join(td, "f.npz"), self.phi_cv, broken)
            with self.assertRaises(RuntimeError) as ctx:
                fu.flux_universe_bins(path, 2, REF_PT_EDGES, self.phi_cv)
        self.assertIn("non-positive", str(ctx.exception))


class RatioTable(unittest.TestCase):

    def setUp(self):
        self.phi_cv, self.phi_univ = make_flux_table()
        self._td = tempfile.TemporaryDirectory()
        self.bank = os.path.join(self._td.name, "bank")
        os.makedirs(self.bank)
        self.path = write_flux_npz(os.path.join(self._td.name, "flux.npz"),
                                   self.phi_cv, self.phi_univ)
        self.addCleanup(self._td.cleanup)

    def test_table_matches_per_universe_ratios(self):
        table = fu.flux_universe_ratio_table(self.path, REF_PT_EDGES, self.phi_cv)
        self.assertEqual(table.shape, (N_UNIV, N_REF))
        np.testing.assert_allclose(table, self.phi_univ / self.phi_cv[None, :])

    def test_table_on_the_fps_grid_carries_the_extended_bin(self):
        cv_fps = fu.flux_on_target_grid(self.phi_cv, FPS_PT_EDGES, REF_PT_EDGES)
        table = fu.flux_universe_ratio_table(self.path, FPS_PT_EDGES, cv_fps,
                                             ref_edges=REF_PT_EDGES)
        self.assertEqual(table.shape, (N_UNIV, len(FPS_PT_EDGES) - 1))
        self.assertFalse(np.any(np.isclose(table[:, -1], 1.0)))
        np.testing.assert_allclose(table[:, -1], table[:, N_REF - 1])

    def test_banked_table_is_preferred_over_the_file(self):
        banked = np.full((N_UNIV, N_REF), 1.5)
        np.save(os.path.join(self.bank, fu.BANKED_RATIO_NAME), banked)
        got = fu.resolve_flux_ratio_table(
            n_pt=N_REF, n_flux=N_UNIV, bank=self.bank, universe_file=self.path,
            pt_edges=REF_PT_EDGES, cv_flux_bins=self.phi_cv)
        np.testing.assert_allclose(got, banked)

    def test_falls_back_to_the_file_when_the_bank_has_no_table(self):
        got = fu.resolve_flux_ratio_table(
            n_pt=N_REF, n_flux=N_UNIV, bank=self.bank, universe_file=self.path,
            pt_edges=REF_PT_EDGES, cv_flux_bins=self.phi_cv)
        np.testing.assert_allclose(got, self.phi_univ / self.phi_cv[None, :])

    def test_all_ones_table_is_refused_as_the_bug_itself(self):
        np.save(os.path.join(self.bank, fu.BANKED_RATIO_NAME), np.ones((N_UNIV, N_REF)))
        with self.assertRaises(RuntimeError) as ctx:
            fu.resolve_flux_ratio_table(
                n_pt=N_REF, n_flux=N_UNIV, bank=self.bank, universe_file=None)
        self.assertIn("J28", str(ctx.exception))

    def test_wrong_pt_binning_in_the_bank_is_refused(self):
        np.save(os.path.join(self.bank, fu.BANKED_RATIO_NAME),
                np.full((N_UNIV, N_REF + 1), 1.02))
        with self.assertRaises(RuntimeError) as ctx:
            fu.resolve_flux_ratio_table(
                n_pt=N_REF, n_flux=N_UNIV, bank=self.bank, universe_file=None)
        self.assertIn("pT bins", str(ctx.exception))

    def test_no_bank_and_no_file_fails_closed(self):
        with self.assertRaises(RuntimeError) as ctx:
            fu.resolve_flux_ratio_table(n_pt=N_REF, bank=self.bank, universe_file=None)
        self.assertIn("refusing", str(ctx.exception))


class RescaleIsExact(unittest.TestCase):
    """The premise of the whole post-hoc tool: dividing the saved xsec by r_u
    reproduces the xsec that would have come out of a correctly-normalized run,
    to machine precision, without re-unfolding."""

    def setUp(self):
        self.shape = (N_REF, 4, 3)
        rng = np.random.default_rng(11)
        self.counts = rng.uniform(0, 500, size=self.shape)
        self.comp = rng.uniform(0.2, 0.9, size=self.shape)
        self.edges = [REF_PT_EDGES,
                      np.linspace(1.5, 20.0, self.shape[1] + 1),
                      np.linspace(0.0, 2.0, self.shape[2] + 1)]
        self.phi_cv, self.phi_univ = make_flux_table()

    def _xsec(self, flux):
        x, _ = extract_cross_section_nd(self.counts, self.comp, flux, 1.2e20,
                                        3.2e30, self.edges)
        return x.ravel(order="C")

    def test_dividing_by_r_u_reproduces_the_phi_u_extraction(self):
        """Exact in exact arithmetic; in floating point the two routes differ only
        by the last bits of Phi_CV * (Phi_u/Phi_CV) != Phi_u, hence rtol=1e-13 and
        not a loose physics tolerance."""
        for u in range(N_UNIV):
            r_u = self.phi_univ[u] / self.phi_cv
            saved_wrong = self._xsec(self.phi_cv)          # what the bug produced
            correct = self._xsec(self.phi_univ[u])          # what it should have been
            divisor = fu.flat_flux_divisor(r_u, self.shape)
            np.testing.assert_allclose(saved_wrong / divisor, correct,
                                       rtol=1e-13, atol=0)

    def test_divisor_is_constant_within_a_pt_slice(self):
        r_u = self.phi_univ[0] / self.phi_cv
        d = fu.flat_flux_divisor(r_u, self.shape).reshape(self.shape, order="C")
        for i in range(self.shape[0]):
            self.assertEqual(len(np.unique(d[i])), 1)
            self.assertAlmostEqual(float(d[i].flat[0]), r_u[i])

    def test_divisor_rejects_a_mismatched_or_invalid_ratio(self):
        with self.assertRaises(ValueError):
            fu.flat_flux_divisor(np.ones(N_REF + 2), self.shape)
        bad = np.ones(N_REF)
        bad[3] = 0.0
        with self.assertRaises(ValueError):
            fu.flat_flux_divisor(bad, self.shape)


# --------------------------------------------------------------------------- slabs
KNOBS = ["MaCCQE", "MaRES", "LowQ2"]


def synth_slabs(td, shape, ratio, n_throws=24, n_slabs=3, seed=3):
    """Synthetic uthrow slabs in the on-disk contract do_throws/do_blockunits write.

    Built the way the BUG built them: each throw's rows are the correctly-normalized
    xsec multiplied back up by r_u, i.e. exactly what a Phi_CV-normalized run would
    have saved. That gives the tests a known truth to recover.
    """
    rng = np.random.default_rng(seed)
    nflat = int(np.prod(shape))
    n_univ = ratio.shape[0]
    x_cv = rng.uniform(1.0, 5.0, nflat)
    x_cv[: max(1, nflat // 20)] = 0.0            # a few unreported bins
    truth_throws, wrong_throws, ids, us = [], [], [], []
    per = n_throws // n_slabs
    for j in range(n_throws):
        u = int(rng.integers(n_univ))
        truth = x_cv * (1.0 + 0.02 * rng.standard_normal(nflat))
        wrong = truth * fu.flat_flux_divisor(ratio[u], shape)
        truth_throws.append(truth)
        wrong_throws.append(wrong)
        ids.append(j)
        us.append(u)
    tpaths = []
    for s in range(n_slabs):
        sl = slice(s * per, (s + 1) * per)
        p = os.path.join(td, f"uthrow_slab_{s}.npz")
        np.savez_compressed(p, xs=np.array(wrong_throws[sl]),
                            throws=np.array(ids[sl]), flux_u=np.array(us[sl]),
                            seed=np.int64(1000),
                            bands=np.array(KNOBS, dtype=object))
        tpaths.append(p)

    xs, labels, kinds, truth_block = [], [], [], []
    for b in KNOBS:
        for idx in ("0", "1"):
            v = x_cv * (1.0 + 0.03 * rng.standard_normal(nflat))
            xs.append(v); truth_block.append(v)      # knobs: CV flux is correct
            labels.append(f"{b}:{idx}"); kinds.append("knob")
    for u in range(n_univ):
        v = x_cv * (1.0 + 0.02 * rng.standard_normal(nflat))
        truth_block.append(v)
        xs.append(v * fu.flat_flux_divisor(ratio[u], shape))
        labels.append(f"flux{u}"); kinds.append("flux")
    bpath = os.path.join(td, "block_slab_0.npz")
    np.savez_compressed(bpath, xs=np.array(xs), labels=np.array(labels, dtype=object),
                        kinds=np.array(kinds, dtype=object), seed=np.int64(1000))
    return {"x_cv": x_cv, "throw_paths": tpaths, "block_path": bpath,
            "truth_throws": np.array(truth_throws), "truth_block": np.array(truth_block),
            "flux_u": np.array(us), "labels": labels, "kinds": kinds}


def synth_bank(td, shape, edges0, phi_cv, ratio):
    """Minimal bank: cv.npz geometry + the flux ratio table + flux weight stubs."""
    bank = os.path.join(td, "bank")
    os.makedirs(bank, exist_ok=True)
    kwargs = {f"edges_{i}": np.linspace(0.0, 1.0, n + 1) for i, n in enumerate(shape)}
    kwargs["edges_0"] = np.asarray(edges0, float)
    np.savez(os.path.join(bank, "cv.npz"), flux=phi_cv, **kwargs)
    np.save(os.path.join(bank, fu.BANKED_RATIO_NAME), ratio)
    for u in range(ratio.shape[0]):
        np.save(os.path.join(bank, f"sig_flux_t_{u}.npy"), np.ones(3))
    return bank


class RescaleTool(unittest.TestCase):

    def setUp(self):
        self.shape = (N_REF, 3, 2)
        self.phi_cv, self.phi_univ = make_flux_table()
        self.ratio = self.phi_univ / self.phi_cv[None, :]
        self._td = tempfile.TemporaryDirectory()
        self.td = self._td.name
        self.addCleanup(self._td.cleanup)
        self.fix = synth_slabs(self.td, self.shape, self.ratio)
        self.bank = synth_bank(self.td, self.shape, REF_PT_EDGES, self.phi_cv, self.ratio)
        self.divisors = {u: fu.flat_flux_divisor(self.ratio[u], self.shape)
                         for u in range(N_UNIV)}

    def test_throw_rows_recover_the_correctly_normalized_xsec(self):
        recovered = []
        for p in self.fix["throw_paths"]:
            with np.load(p, allow_pickle=True) as z:
                out, touched = rfu.rescale_throw_slab(z, self.divisors)
            self.assertEqual(touched, out.shape[0])
            recovered.append(out)
        np.testing.assert_allclose(np.concatenate(recovered), self.fix["truth_throws"],
                                   rtol=1e-12, atol=0)

    def test_a_throw_with_no_flux_universe_is_left_alone(self):
        p = os.path.join(self.td, "nofluxslab.npz")
        rows = np.arange(2 * int(np.prod(self.shape)), dtype=float).reshape(2, -1)
        np.savez(p, xs=rows, throws=np.array([0, 1]), flux_u=np.array([-1, -1]))
        with np.load(p, allow_pickle=True) as z:
            out, touched = rfu.rescale_throw_slab(z, self.divisors)
        self.assertEqual(touched, 0)
        np.testing.assert_array_equal(out, rows)

    def test_unknown_flux_id_fails_closed(self):
        p = os.path.join(self.td, "badid.npz")
        rows = np.ones((1, int(np.prod(self.shape))))
        np.savez(p, xs=rows, throws=np.array([0]), flux_u=np.array([N_UNIV + 3]))
        with np.load(p, allow_pickle=True) as z:
            with self.assertRaises(SystemExit):
                rfu.rescale_throw_slab(z, self.divisors)

    def test_block_flux_units_corrected_and_knob_endpoints_untouched(self):
        with np.load(self.fix["block_path"], allow_pickle=True) as z:
            out, touched = rfu.rescale_block_slab(z, self.divisors)
            original = np.asarray(z["xs"], float)
        self.assertEqual(touched, N_UNIV)
        np.testing.assert_allclose(out, self.fix["truth_block"], rtol=1e-12, atol=0)
        for i, kind in enumerate(self.fix["kinds"]):
            if kind == "knob":
                np.testing.assert_array_equal(out[i], original[i])

    def test_covariances_match_the_combine_estimators(self):
        rep = self.fix["x_cv"] > 0
        base = self.fix["x_cv"][rep]
        rows = [self.fix["truth_throws"]]
        blocks = [(self.fix["truth_block"], self.fix["labels"], self.fix["kinds"])]
        C_uni, ms, C_block, C_cross, C_flux, T = rfu.build_covariances(
            rows, blocks, base, rep)
        # independent recomputation with the same uq_math primitives combine uses
        want_uni, want_ms = joint_throw_covariance(self.fix["truth_throws"][:, rep], base)
        np.testing.assert_allclose(C_uni, want_uni)
        np.testing.assert_allclose(ms, want_ms)
        want_block = np.zeros_like(C_block)
        by_band = {}
        for x, label, kind in zip(self.fix["truth_block"], self.fix["labels"],
                                  self.fix["kinds"]):
            if kind == "knob":
                band, idx = label.rsplit(":", 1)
                by_band.setdefault(band, {})[idx] = x[rep]
        for band in by_band:
            want_block += mat_covariance(
                np.stack([by_band[band]["0"], by_band[band]["1"]]))
        want_flux = mat_covariance(np.asarray(
            [x[rep] for x, k in zip(self.fix["truth_block"], self.fix["kinds"])
             if k == "flux"]))
        want_block += want_flux
        np.testing.assert_allclose(C_block, want_block)
        np.testing.assert_allclose(C_flux, want_flux)
        np.testing.assert_allclose(C_cross, C_uni - C_block)
        self.assertEqual(T, self.fix["truth_throws"].shape[0])

    def test_inflation_g_matches_the_adopt_construction(self):
        rng = np.random.default_rng(5)
        A = rng.standard_normal((6, 6))
        C_uni = A @ A.T
        B = rng.standard_normal((6, 6))
        C_block = B @ B.T
        g = rfu.inflation_g(C_uni, C_block)
        vu = np.diag(C_uni)
        vb = np.diag(C_block)
        np.testing.assert_allclose(g, np.sqrt(np.maximum(vu, vb)) / np.sqrt(vb))
        self.assertTrue(np.all(g >= 1.0 - 1e-12))

    def test_cv_centered_g_adds_the_mean_shift(self):
        C_uni = np.diag([1.0, 4.0, 9.0])
        C_block = np.diag([1.0, 1.0, 1.0])
        ms = np.array([0.0, 3.0, 4.0])
        g = rfu.inflation_g(C_uni, C_block, mean_shift=ms)
        np.testing.assert_allclose(g, np.sqrt(np.maximum(
            np.diag(C_uni) + ms ** 2, np.diag(C_block))))
        self.assertGreater(g[1], rfu.inflation_g(C_uni, C_block)[1])

    def test_zero_block_variance_bin_keeps_g_at_one(self):
        g = rfu.inflation_g(np.diag([4.0, 1.0]), np.diag([0.0, 1.0]))
        self.assertEqual(g[0], 1.0)

    def test_rescaling_twice_would_double_correct_so_the_stamp_refuses_it(self):
        out = os.path.join(self.td, "out")
        self._run_cli(out_dir=out)
        # the corrected slabs are stamped; a second pass over them must refuse
        with self.assertRaises(SystemExit):
            self._run_cli(throw_glob=os.path.join(out, "uthrow_slab_*.npz"),
                          block_glob=os.path.join(out, "block_slab_*.npz"))

    def _run_cli(self, out_dir=None, throw_glob=None, block_glob=None, extra=()):
        argv = ["rescale_flux_universes.py",
                "--throw-slabs", throw_glob or os.path.join(self.td, "uthrow_slab_*.npz"),
                "--block-slabs", block_glob or os.path.join(self.td, "block_slab_*.npz"),
                "--bank", self.bank,
                "--cv", os.path.join(self.td, "x_cv.npy"),
                "--out-json", os.path.join(self.td, "summary.json"),
                *extra]
        if out_dir:
            argv += ["--out-dir", out_dir]
        np.save(os.path.join(self.td, "x_cv.npy"), self.fix["x_cv"])
        old = sys.argv
        sys.argv = argv
        try:
            with contextlib.redirect_stdout(io.StringIO()) as buf:
                rfu.main()
        finally:
            sys.argv = old
        return buf.getvalue()

    def test_end_to_end_cli_writes_stamped_exact_slabs(self):
        out = os.path.join(self.td, "corrected")
        log = self._run_cli(out_dir=out)
        self.assertIn("before -> after", log)
        got = []
        for p in sorted(glob.glob(os.path.join(out, "uthrow_slab_*.npz"))):
            with np.load(p, allow_pickle=True) as z:
                self.assertEqual(int(z["flux_normalized"]), 1)
                self.assertIn("flux_rescaled_from", z.files)
                self.assertEqual(int(z["seed"]), 1000)          # provenance preserved
                got.append(np.asarray(z["xs"], float))
        np.testing.assert_allclose(np.concatenate(got), self.fix["truth_throws"],
                                   rtol=1e-12, atol=0)

    def test_cli_summary_reports_before_and_after_from_the_same_estimators(self):
        import json
        self._run_cli()
        with open(os.path.join(self.td, "summary.json")) as fh:
            summary = json.load(fh)["results"]
        self.assertEqual(set(summary), {"before", "after"})
        for tag in ("before", "after"):
            for key in ("sqrt_tr_unified", "sqrt_tr_blocksum", "g_mean"):
                self.assertGreater(summary[tag][key], 0.0)
        # the correction is not a no-op on these slabs
        self.assertNotAlmostEqual(summary["before"]["sqrt_tr_unified"],
                                  summary["after"]["sqrt_tr_unified"])

    def test_cli_refuses_slabs_that_cite_no_flux_universe(self):
        empty = os.path.join(self.td, "novoid")
        os.makedirs(empty, exist_ok=True)
        nflat = int(np.prod(self.shape))
        np.savez(os.path.join(empty, "uthrow_slab_0.npz"),
                 xs=np.ones((2, nflat)), throws=np.array([0, 1]),
                 flux_u=np.array([-1, -1]), seed=np.int64(1000))
        np.savez(os.path.join(empty, "block_slab_0.npz"),
                 xs=np.ones((2, nflat)),
                 labels=np.array(["MaCCQE:0", "MaCCQE:1"], dtype=object),
                 kinds=np.array(["knob", "knob"], dtype=object), seed=np.int64(1000))
        with self.assertRaises(SystemExit):
            self._run_cli(throw_glob=os.path.join(empty, "uthrow_slab_*.npz"),
                          block_glob=os.path.join(empty, "block_slab_*.npz"))


class CombineRefusesUnstampedSlabs(unittest.TestCase):
    """unified_throw_cov._flux_normalized gates the pre-fix slabs out of a new
    adopted covariance -- the same shape as the existing estimator-seed gate."""

    def _load_predicate(self):
        src = open(os.path.join(ND, "unified_throw_cov.py")).read()
        tree = ast.parse(src)
        fn = next(n for n in tree.body
                  if isinstance(n, ast.FunctionDef) and n.name == "_flux_normalized")
        ns = {}
        exec(compile(ast.Module([fn], []), "<uthrow>", "exec"), ns)
        return ns["_flux_normalized"]

    def test_predicate_accepts_only_a_stamped_slab(self):
        pred = self._load_predicate()
        with tempfile.TemporaryDirectory() as td:
            unstamped = os.path.join(td, "a.npz")
            stamped = os.path.join(td, "b.npz")
            zeroed = os.path.join(td, "c.npz")
            np.savez(unstamped, xs=np.ones((1, 2)))
            np.savez(stamped, xs=np.ones((1, 2)), flux_normalized=np.int64(1))
            np.savez(zeroed, xs=np.ones((1, 2)), flux_normalized=np.int64(0))
            with np.load(unstamped) as z:
                self.assertFalse(pred(z))
            with np.load(stamped) as z:
                self.assertTrue(pred(z))
            with np.load(zeroed) as z:
                self.assertFalse(pred(z))


class KernelsTakeAFluxOverride(unittest.TestCase):
    """Static guard over the ND/5D extraction sites.

    J28's shape was that three separate implementations each hard-coded the CV
    flux, so fixing one did not fix the others. A test that only exercised one
    kernel would not have caught it. This walks the source of every site named in
    the finding and asserts the CV flux is no longer wired straight into
    `extract_cross_section_nd`.
    """

    KERNELS = [("compare_unified_throw.py", "_xsec_for_weights"),
               ("unified_throw_cov_5d.py", "_xsec_for_weights_5d")]
    SWEEPS = [("sweep_bank_5d.py", "do_run"), ("sweep_bank.py", "do_run")]

    @staticmethod
    def _func(fname, funcname):
        tree = ast.parse(open(os.path.join(ND, fname)).read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == funcname:
                return node
        raise AssertionError(f"{funcname} not found in {fname}")

    @staticmethod
    def _flux_arg(func):
        for node in ast.walk(func):
            if (isinstance(node, ast.Call)
                    and getattr(node.func, "id", None) == "extract_cross_section_nd"):
                return node.args[2]
        raise AssertionError("no extract_cross_section_nd call")

    @staticmethod
    def _is_cv_subscript(node):
        return (isinstance(node, ast.Subscript)
                and getattr(node.value, "id", None) in ("d", "cv")
                and getattr(node.slice, "value", None) == "flux")

    def test_kernels_accept_and_honour_a_flux_override(self):
        for fname, funcname in self.KERNELS:
            with self.subTest(kernel=fname):
                func = self._func(fname, funcname)
                names = [a.arg for a in func.args.args] + [
                    a.arg for a in func.args.kwonlyargs]
                self.assertIn("flux", names, f"{funcname} has no flux override")
                arg = self._flux_arg(func)
                self.assertFalse(self._is_cv_subscript(arg),
                                 f"{funcname} still passes the CV flux unconditionally")
                self.assertIsInstance(arg, ast.IfExp,
                                      f"{funcname} should fall back to CV only when "
                                      "flux is None")

    def test_sweep_runners_resolve_a_flux_universe(self):
        for fname, funcname in self.SWEEPS:
            with self.subTest(sweep=fname):
                func = self._func(fname, funcname)
                arg = self._flux_arg(func)
                self.assertFalse(self._is_cv_subscript(arg),
                                 f"{fname}:{funcname} still divides every universe by "
                                 "the CV flux")
                body = ast.dump(func)
                self.assertIn("flux_universe_bins", body,
                              f"{fname}:{funcname} never resolves Phi_u")
                self.assertIn("'Flux'", body.replace('"', "'"),
                              f"{fname}:{funcname} has no Flux-band branch")

    def test_throw_driver_passes_phi_u_for_every_flux_universe(self):
        tree = ast.parse(open(os.path.join(ND, "unified_throw_cov.py")).read())
        for funcname in ("do_throws", "do_blockunits"):
            with self.subTest(func=funcname):
                func = next(n for n in ast.walk(tree)
                            if isinstance(n, ast.FunctionDef) and n.name == funcname)
                calls = [n for n in ast.walk(func)
                         if isinstance(n, ast.Call)
                         and getattr(n.func, "id", None) == "_xsec_for_weights"]
                self.assertTrue(calls)
                self.assertTrue(
                    any(kw.arg == "flux" for c in calls for kw in c.keywords),
                    f"{funcname} never passes a per-universe flux")
                self.assertIn("_flux_for_universe", ast.dump(func))

    def test_nd_driver_uses_the_shared_remap_for_the_universe(self):
        """J29: the universe must go through flux_universe_bins with the CV's own
        reference edges, not a bare GetBinContent(b+1) loop."""
        src = open(os.path.join(ND, "unfold_nd_omnifold_unbinned.py")).read()
        self.assertIn("flux_universe_bins", src)
        self.assertIn("ref_edges=flux_ref_edges", src)
        # the histogram name may still appear in --flux-universe-file's help text;
        # what must be gone is the driver reading the histogram itself
        self.assertNotIn('Get("hFluxUniv")', src,
                         "the driver should no longer read the histogram directly")
        self.assertNotIn("GetBinContent(b + 1, uidx + 1)", src,
                         "the pre-fix direct bin index is still present (J29)")

    def test_pet_5d_kernel_accepts_a_flux_override(self):
        func = self._func("pet_systematics_5d.py", "xsec")
        self.assertIn("flux", [a.arg for a in func.args.args])
        self.assertIsInstance(self._flux_arg(func), ast.IfExp)
        src = open(os.path.join(ND, "pet_unified_throw_5d.py")).read()
        self.assertIn("flux=phi[u]", src)

    def test_bank_builder_no_longer_defaults_the_ratio_to_one(self):
        src = open(os.path.join(ND, "unified_throw.py")).read()
        self.assertIn("flux_universe_ratio_table", src)
        self.assertNotIn("fr = np.ones((N_FLUX", src)

    def test_ref_edges_match_the_2d_grid(self):
        """Keep the hard-coded fixture grid honest against 2d-unfolding."""
        src = open(os.path.join(os.path.dirname(ND), "2d-unfolding",
                                "unfold_2d_omnifold_unbinned.py")).read()
        tree = ast.parse(src)
        for node in tree.body:
            if (isinstance(node, ast.Assign)
                    and getattr(node.targets[0], "id", None) == "PT_EDGES"):
                np.testing.assert_allclose(ast.literal_eval(node.value), REF_PT_EDGES)
                return
        raise AssertionError("PT_EDGES not found in the 2D driver")


class SyntaxOfTouchedFiles(unittest.TestCase):
    """Every file this fix touched must at least parse and compile off-cluster;
    most of them cannot be imported here because they pull in ROOT."""

    FILES = ["flux_universe.py", "rescale_flux_universes.py", "unified_throw_cov.py",
             "unified_throw_cov_5d.py", "compare_unified_throw.py", "sweep_bank.py",
             "sweep_bank_5d.py", "unified_throw.py", "unfold_nd_omnifold_unbinned.py",
             "pet_systematics_5d.py", "pet_unified_throw_5d.py"]

    def test_all_touched_files_compile(self):
        for fname in self.FILES:
            with self.subTest(file=fname):
                path = os.path.join(ND, fname)
                compile(open(path).read(), path, "exec")

    def test_rescale_tool_cli_help_runs(self):
        proc = subprocess.run(
            [sys.executable, os.path.join(ND, "rescale_flux_universes.py"), "--help"],
            capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("--throw-slabs", proc.stdout)


if __name__ == "__main__":
    unittest.main()
