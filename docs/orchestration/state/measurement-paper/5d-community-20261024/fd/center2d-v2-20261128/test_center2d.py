"""Tests for center2d.py. Synthetic inputs for the algebra, the rules and the data part (TH2Ds written by uproot);
the committed pre-G2R blocks only for the controls (C-FLUX, C-ID, C-RECON), never for a reading, so no CENTER2D number
is computed before the binding. run: python3 -I -B test_center2d.py
"""
import importlib.util
import json
import os
import shutil
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("center2d", os.path.join(HERE, "center2d.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
RNG = np.random.default_rng(20261128)
SETS = m.band_sets()
WEIGHT, LATERAL, NU, FLUX = SETS


def spd(n, rank=None, scale=1.0):
    A = RNG.normal(size=(n, rank or n))
    return scale * (A @ A.T) / (rank or n)


class Algebra(unittest.TestCase):
    def test_identity_is_exact_for_any_weights(self):
        for n_u, w in ((2, None), (3, None), (100, RNG.random(100) + 0.1)):
            X = RNG.normal(size=(n_u, 7)) + 5
            w = np.ones(n_u) if w is None else w
            x0 = RNG.normal(size=7) + 5
            b = m.centre(X, w) - x0
            self.assertLess(m.amax(m.v_nom(X, w, x0) - m.wcov(X, w) - np.outer(b, b)), 1e-12)

    def test_wcov_is_build_repairs_formula(self):
        X, w = RNG.normal(size=(5, 4)), RNG.random(5)
        mu = (w[:, None] * X).sum(0) / w.sum()
        want = sum(wi * np.outer(x - mu, x - mu) for wi, x in zip(w, X)) / w.sum()
        self.assertLess(m.amax(m.wcov(X, w) - want), 1e-14)

    def test_scaled_uses_the_total_for_a_null_block(self):
        self.assertAlmostEqual(m.scaled(1e-20, 1e-3, 1.0) / 1e-17, 1.0, 12)
        self.assertEqual(m.scaled(1e-20, 1e-15, 1.0), 1e-20)


class Rules(unittest.TestCase):
    def test_labels_at_the_boundaries(self):
        self.assertEqual(m.label(0.0099, [0.099, 0.05, 0.01]), "NEGLIGIBLE")
        self.assertEqual(m.label(0.01, [0.099, 0.05, 0.01]), "INTERMEDIATE")
        self.assertEqual(m.label(0.0, [0.0, 0.10, 0.0]), "APPRECIABLE")
        self.assertEqual(m.label(0.5, [0.0, 0.0, 0.1000001]), "APPRECIABLE")

    def test_no_non_empty_band_refuses(self):
        with self.assertRaisesRegex(m.Stop, "C-FINITE"):
            m.label(0.0, [None, None, None])

    def test_empty_rank_bands_are_ignored(self):
        self.assertEqual(m.label(0.001, [0.05, 0.02, None]), "NEGLIGIBLE")
        self.assertEqual(m.label(0.001, [0.05, None, None]), "NEGLIGIBLE")
        self.assertEqual(m.label(0.001, [0.2, None, None]), "APPRECIABLE")

    def test_rank_slices(self):
        self.assertEqual([s for _, _, s in m.rank_slices(205)], [slice(0, 73), slice(73, 139), slice(139, 205)])
        self.assertEqual([s for _, _, s in m.rank_slices(120)], [slice(0, 73), slice(73, 120), None])
        self.assertEqual([s for _, _, s in m.rank_slices(140)][2], slice(139, 140))
        self.assertEqual([s for _, _, s in m.rank_slices(139)][2], None)
        self.assertEqual([s for _, _, s in m.rank_slices(50)], [slice(0, 50), None, None])


class Readings(unittest.TestCase):
    def test_analytic_diagonal_case(self):
        n = 205
        lam = np.linspace(10.0, 1.0, n)
        C = np.diag(lam)
        b = np.zeros(n)
        b[0] = 1.0                                   # adds 1/10 along rank 1 only
        ctl = {}
        r = m.readings({"x": b}, {"x": np.ones(n)}, np.ones(n), C, 2 * C, np.arange(n), ctl, "t")
        self.assertEqual(r["ndf"], n)
        self.assertAlmostEqual(r["R1"]["trace_share"], 1.0 / lam.sum(), 15)
        self.assertAlmostEqual(r["R1"]["trace_share_of_C_sys"], 0.5 / lam.sum(), 15)
        self.assertAlmostEqual(r["R2"]["max"], 0.1, 15)
        self.assertEqual(r["R2"]["max_cell_globalid"], 0)
        self.assertAlmostEqual(r["R3"]["rank_band_means"][0], 0.1 / 73, 15)
        self.assertEqual(r["R3"]["rank_band_means"][1:], [0.0, 0.0])
        self.assertAlmostEqual(r["R3"]["max_r"], 0.1, 15)
        self.assertEqual(r["R3"]["max_r_rank"], 1)
        self.assertAlmostEqual(r["R4"]["epsilon"], 0.1, 14)
        self.assertAlmostEqual(r["R3"]["overall_mean"], r["R3"]["overall_mean_via_pinv"], 14)
        self.assertEqual(r["label_if_decided"], "NEGLIGIBLE")
        self.assertTrue(all(v["pass"] for v in ctl.values()))

    def test_per_band_contributions_add_and_attribution(self):
        n = 30
        C = spd(n, scale=4.0)
        rng = np.random.default_rng(5)
        offs = {f"b{i}": rng.normal(size=n) * 0.1 * 3.0 ** i for i in range(6)}
        ctl = {}
        r = m.readings(offs, {k: np.ones(n) for k in offs}, np.ones(n) * 3, C, C, np.arange(n), ctl, "t")
        self.assertTrue(ctl["C-ADD:t"]["pass"])
        self.assertEqual(r["R5"]["top5"]["trace_share"][0], "b5")
        loo = r["R5"]["leave_one_band_out"]["b5"]
        self.assertAlmostEqual(loo["trace_share"], r["R1"]["trace_share"] - r["R5"]["per_band"]["b5"]["trace_share"], 15)
        self.assertEqual(r["rank_bands"], [[1, 30], [74, None], [140, None]])
        self.assertEqual(r["R3"]["rank_band_means"][1:], [None, None])
        json.dumps(r, allow_nan=False)

    def test_singular_c_drops_the_null_ranks(self):
        n = 205
        C = spd(n, rank=120)
        ctl = {}
        r = m.readings({"a": RNG.normal(size=n) * 0.01}, {"a": np.ones(n)}, np.ones(n), C, C, np.arange(n), ctl, "t")
        self.assertEqual(r["ndf"], 120)
        self.assertIsNone(r["R3"]["rank_band_means"][2])
        self.assertEqual(r["rank_bands"][2], [140, None])

    def test_label_reads_carry_the_realization_sentence(self):
        self.assertIn("can fall on either side", m.LABEL_READS["NEGLIGIBLE"])
        self.assertIn("not separable", m.LABEL_READS["APPRECIABLE"])

    def test_psd_refuses(self):
        with self.assertRaisesRegex(m.Stop, "C-PSD"):
            m.psd({}, "x", np.array([[1.0, 0.5], [0.4, 1.0]]))
        with self.assertRaisesRegex(m.Stop, "C-PSD"):
            m.psd({}, "x", np.array([[1.0, 2.0], [2.0, 1.0]]))

    def test_psd_refuses_a_negative_definite_matrix(self):
        with self.assertRaisesRegex(m.Stop, "C-PSD"):
            m.psd({}, "x", -np.eye(3))
        with self.assertRaisesRegex(m.Stop, "C-PSD"):
            m.psd({}, "x", -np.eye(3), positive=True)

    def test_psd_positive_needs_a_positive_diagonal(self):
        A = np.diag([1.0, 2.0, 0.0])
        m.psd({}, "m", A)
        with self.assertRaisesRegex(m.Stop, "C-PSD"):
            m.psd({}, "c", A, positive=True)

    def test_a_zero_m_passes_psd(self):
        ctl = {}
        m.psd(ctl, "m", np.zeros((3, 3)))
        self.assertTrue(ctl["C-PSD:m"]["pass"])

    def test_r6_is_null_when_a_cell_has_zero_band_variance(self):
        n = 30
        C = np.eye(n)
        b = np.full(n, 0.01)
        v = np.ones(n)
        v[4] = 0.0
        r = m.readings({"a": b}, {"a": v}, np.ones(n) * 2, C, C, np.arange(n), {}, "t")["R6"]["a"]
        self.assertIsNone(r["median_abs_b_over_sigma_band"])
        self.assertEqual((r["cells_with_zero_band_variance"], r["of_which_b_is_zero"], r["of_which_b_is_nonzero"]),
                         (1, 0, 1))
        self.assertAlmostEqual(r["median_abs_b_over_sigma_band_positive_variance_cells_only"], 0.01, 15)
        self.assertAlmostEqual(r["median_abs_b_over_x0"], 0.005, 15)
        r2 = m.readings({"a": b}, {"a": np.ones(n)}, np.ones(n) * 2, C, C, np.arange(n), {}, "t")["R6"]["a"]
        self.assertAlmostEqual(r2["median_abs_b_over_sigma_band"], 0.01, 15)

    def test_r6_refuses_a_zero_x0(self):
        n = 5
        x0 = np.ones(n)
        x0[2] = 0.0
        with self.assertRaisesRegex(m.Stop, "C-FINITE"):
            m.readings({"a": np.ones(n) * 0.1}, {"a": np.ones(n)}, x0, np.eye(n), np.eye(n), np.arange(n), {}, "t")

    def test_top5_keys_name_the_declared_bands(self):
        n = 205
        r = m.readings({"a": np.ones(n) * 0.01}, {"a": np.ones(n)}, np.ones(n), np.eye(n), np.eye(n), np.arange(n),
                       {}, "t")
        self.assertEqual(sorted(r["R5"]["top5"]), ["ranks_140_ndf", "ranks_1_73", "ranks_74_139", "trace_share"])

    def test_c_add_catches_a_wrong_sum(self):
        n = 10
        C = np.eye(n)
        orig = m.np.einsum
        m.np.einsum = lambda *a: orig(*a) * (1 + 1e-9)
        try:
            with self.assertRaisesRegex(m.Stop, "C-ADD"):
                m.readings({"a": np.ones(n)}, {"a": np.ones(n)}, np.ones(n), C, C, np.arange(n), {}, "t")
        finally:
            m.np.einsum = orig


def fake_blocks(perturb=None):
    """A blocks_<T>.npz-shaped dict built with center2d's own algebra (synthetic, consistent)."""
    n = m.NCELL
    x0 = RNG.random(n) + 1.0
    w = m.npz(m.pinned("blocks_AR23"))["w_flux"]
    B = {"x_T": x0, "x_R": x0, "rep": np.r_[np.ones(n), np.zeros(224 - n)].astype(np.int64), "w_flux": w,
         "minos_x": x0 + RNG.normal(size=(2, n)) * 0.02}
    for b in WEIGHT + LATERAL:
        B[f"band__{b}"] = x0 + RNG.normal(size=(NU[b], n)) * 0.01
    vm = {b: m.wcov(B["minos_x"] if b == m.MINOS else B[f"band__{b}"], w if b == FLUX else np.ones(NU[b]))
          for b in WEIGHT + LATERAL}
    B["C_univ"] = sum(vm[b] for b in sorted(WEIGHT))
    B["C_lat"] = sum(vm[b] for b in sorted(LATERAL))
    for k in ("C_norm", "C_stat", "C08", "C_model_abs"):
        B[k] = spd(n, scale=1e-4)
    B["C_T"] = sum(B[k] for k in m.BLOCK_KEYS[1:])
    if perturb:
        perturb(B)
    return B


class Tune(unittest.TestCase):
    def test_synthetic_tune_passes_every_control(self):
        ctl = {}
        r = m.tune_core(fake_blocks(), SETS, ctl, "t")
        self.assertTrue(ctl and all(v["pass"] for v in ctl.values()))
        for k in ("C-X0:t:mask", "C-FINITE:t", "C-FLUX:t", "C-ID:t", "C-RECON:t:C_univ", "C-RECON:t:C_lat", "C-RECON:t:C_T_sum_of_blocks",
                  "C-PSD:C:t", "C-PSD:M:t", "C-ADD:t"):
            self.assertIn(k, ctl)
        self.assertIn(r["label_if_decided"], m.LABEL_READS)

    def test_wrong_flux_weights_refuse(self):
        def p(B):
            B["w_flux"] = B["w_flux"] * 1.0000001
        with self.assertRaisesRegex(m.Stop, "C-FLUX"):
            m.tune_controls(fake_blocks(p), SETS, {}, "t")

    def test_missing_band_refuses(self):
        def p(B):
            del B["band__MaRES"]
        with self.assertRaisesRegex(m.Stop, "C-FINITE"):
            m.tune_controls(fake_blocks(p), SETS, {}, "t")

    def test_wrong_mask_refuses(self):
        def p(B):
            B["rep"] = np.ones(224, dtype=np.int64)
        with self.assertRaisesRegex(m.Stop, "C-X0"):
            m.tune_controls(fake_blocks(p), SETS, {}, "t")

    def test_an_inconsistent_offset_fails_c_id(self):
        orig = m.centre
        m.centre = lambda X, w: orig(X, w) * (1 + 1e-9)
        try:
            with self.assertRaisesRegex(m.Stop, "C-ID"):
                m.tune_controls(fake_blocks(), SETS, {}, "t")
        finally:
            m.centre = orig

    def test_wrong_universe_count_refuses(self):
        def p(B):
            B["band__2p2h"] = B["band__2p2h"][:2]
        with self.assertRaisesRegex(m.Stop, "C-FINITE"):
            m.tune_controls(fake_blocks(p), SETS, {}, "t")


class PartTune(unittest.TestCase):
    """part_tune on a fetched blocks_g2r file, against a stand-in for the committed blocks."""

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="center2d-pt-")
        self.B = fake_blocks()
        self.orig = m.pinned
        buf = os.path.join(self.d, "B.npz")
        np.savez(buf, **self.B)
        with open(buf, "rb") as f:
            self.Bbytes = f.read()
        m.pinned = lambda name: self.Bbytes if name.startswith("blocks_") else self.orig(name)

    def tearDown(self):
        m.pinned = self.orig
        shutil.rmtree(self.d)

    def run_tune(self, mutate=None, fetch_ok=True):
        G = {k: np.array(v, copy=True) for k, v in self.B.items()}
        if mutate:
            mutate(G)
        p = os.path.join(self.d, "G.npz")
        np.savez(p, **G)
        lab = "g2r/blocks_g2r_AR23.npz"
        return m.part_tune("AR23", SETS, {lab: {"pass": fetch_ok}}, {lab: p})

    def test_equal_blocks_pass_with_a_descriptive_label_only(self):
        r = self.run_tune()
        self.assertEqual(r["status"], "OK", r.get("stop"))
        self.assertIsNone(r["label"])
        self.assertIn(r["descriptive_label"], m.LABEL_READS)
        for k in ("C-FETCH:T:AR23", "C-X0:T:AR23", "C-FLUX:T:AR23:equal", "C-RECON:T:AR23:laterals_kept"):
            self.assertTrue(r["controls"][k]["pass"])

    def test_failed_fetch_stops(self):
        r = self.run_tune(fetch_ok=False)
        self.assertEqual(r["status"], "STOP")
        self.assertIn("C-FETCH", r["stop"])

    def test_changed_x_t_stops(self):
        def mut(G):
            G["x_T"][5] *= 1 + 1e-15
        self.assertIn("C-X0", self.run_tune(mut)["stop"])

    def test_changed_lateral_stops(self):
        def mut(G):
            G["band__BeamAngleX"][0, 2] *= 1 + 1e-15
        self.assertIn("C-RECON:T:AR23:laterals_kept", self.run_tune(mut)["stop"])

    def test_an_unreadable_fetched_file_is_a_stop_not_a_crash(self):
        lab = "g2r/blocks_g2r_AR23.npz"
        p = os.path.join(self.d, "junk.npz")
        with open(p, "wb") as f:
            f.write(b"not an npz")
        r = m.part_tune("AR23", SETS, {lab: {"pass": True}}, {lab: p})
        self.assertEqual(r["status"], "STOP")

    def test_changed_flux_weights_stop(self):
        def mut(G):
            G["w_flux"][3] *= 1 + 1e-15
        self.assertIn("C-FLUX:T:AR23:equal", self.run_tune(mut)["stop"])


class CommittedControls(unittest.TestCase):
    """Director's requirement 2: on the committed pre-G2R blocks the C-RECON, C-ID and C-FLUX tolerances are reached,
    and a deliberate 1e-9 change makes C-RECON fail. Controls only: no reading is computed here."""

    def test_controls_pass_on_the_committed_blocks(self):
        for T in m.TUNES:
            ctl = {}
            m.tune_controls(m.npz(m.pinned(f"blocks_{T}")), SETS, ctl, f"R:{T}")
            self.assertTrue(all(v["pass"] for v in ctl.values()), ctl)
            print(f"\n  {T}: " + "; ".join(f"{k} {v.get('rel', v.get('worst_rel', ''))}" for k, v in ctl.items()))

    def test_a_1e9_change_to_one_universe_fails_c_recon(self):
        B = m.npz(m.pinned("blocks_G18"))
        B["band__MaRES"] = B["band__MaRES"].copy()
        B["band__MaRES"][0, 100] *= 1 + 1e-9
        with self.assertRaisesRegex(m.Stop, "C-RECON:R:G18:C_univ"):
            m.tune_controls(B, SETS, {}, "R:G18")

    def test_a_1e9_change_to_minos_x_fails_c_recon(self):
        B = m.npz(m.pinned("blocks_AR23"))
        B["minos_x"] = B["minos_x"].copy()
        B["minos_x"][1, 3] *= 1 + 1e-9
        with self.assertRaisesRegex(m.Stop, "C-RECON:R:AR23:C_lat"):
            m.tune_controls(B, SETS, {}, "R:AR23")

    def test_flux_weights_reproduce_the_logged_values(self):
        ctl = {}
        m.flux_check(ctl, "x", m.npz(m.pinned("blocks_G18"))["w_flux"])
        self.assertTrue(ctl["C-FLUX:x"]["pass"])


def write_th2(path, vals):
    import uproot
    with uproot.recreate(path) as f:
        f["hXSec2D"] = (vals, m.PT_EDGES, m.PZ_EDGES)


class Data(unittest.TestCase):
    """The data part end to end on synthetic files laid out as the fetch writes them."""

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="center2d-t-")
        n = m.NCELL
        B = m.npz(m.pinned("blocks_AR23"))
        rep = np.asarray(B["rep"]).astype(bool)
        self.w = B["w_flux"]
        er = np.zeros(224)
        er[rep] = RNG.random(n) + 1.0
        x0 = er[rep]
        self.er = os.path.join(self.d, "er.root")
        write_th2(self.er, er.reshape(m.NPT, m.NPZ))
        self.paths = {}
        lat = {}
        for L in m.S3_LABELS:
            for u in (0, 1):
                full = np.zeros(224)
                full[rep] = x0 * (1 + RNG.normal(size=n) * 0.01)
                p = os.path.join(self.d, f"S3_{L}{u}.root")
                write_th2(p, full.reshape(m.NPT, m.NPZ))
                self.paths[f"partb/S3_{L}{u}.root"] = p
                lat[(L, u)] = full.reshape(m.NPT, m.NPZ)
        scale = 1 + RNG.normal(size=(2, m.NPT)) * 0.01
        minos_x = np.stack([(lat[("MuonEnergyMINOS", u)] * scale[u][:, None]).ravel()[rep] for u in (0, 1)])
        new = {b: x0 + RNG.normal(size=(NU[b], n)) * 0.01 for b in WEIGHT}
        old = {b: x0 + RNG.normal(size=(NU[b], n)) * 0.01 for b in WEIGHT}
        wt = lambda b: self.w if b == FLUX else np.ones(NU[b])  # noqa: E731
        s5 = {f"band_{b}": m.wcov(old[b], wt(b)) for b in WEIGHT}
        for L in m.S3_LABELS:
            b = m.S3_BAND[L]
            X = minos_x if b == m.MINOS else np.stack([lat[(L, u)].ravel()[rep] for u in (0, 1)])
            s5[f"band_{b}"] = m.wcov(X, np.ones(2))
        v = 0.014 * x0
        s5[f"band_{m.NORM_KEY}"] = np.outer(v, v)
        universe = sum(s5[k] for k in sorted(s5))
        Q = universe + spd(n, scale=1e-4)
        C_un = sum(m.wcov(new[b], wt(b)) for b in sorted(WEIGHT))
        C_uo = sum(s5[f"band_{b}"] for b in sorted(WEIGHT))
        files = {
            "g2r/data_g2r.npz": dict(C_new=Q - C_uo + C_un, C_univ_new=C_un, C_univ_old=C_uo,
                                     **{f"band__{b}": new[b] for b in WEIGHT}),
            "partc/cov2d_Q_205.npz": dict(Q=Q, x=x0, universe=universe),
            "partc/production_cov.npz": s5,
            "c04/minos_rescaled.npz": dict(scale=scale),
        }
        for k, arrs in files.items():
            p = os.path.join(self.d, k.replace("/", "_"))
            np.savez(p, **arrs)
            self.paths[k] = p if p.endswith(".npz") else p + ".npz"
        self.fst = {k: {"pass": True} for k in m.DATA_FILES}

    def tearDown(self):
        shutil.rmtree(self.d)

    def run_data(self):
        orig = m.sha_file
        m.sha_file = lambda p: m.ER_SHA if p == self.er else orig(p)
        try:
            return m.part_data(SETS, self.fst, self.paths, self.er)
        finally:
            m.sha_file = orig

    def test_consistent_synthetic_data_passes_every_control(self):
        r = self.run_data()
        self.assertEqual(r["status"], "OK", r.get("stop"))
        self.assertIn(r["label"], m.LABEL_READS)
        names = set(r["controls"])
        for k in ("C-FETCH:D", "C-PIN:D", "C-X0:D", "C-FLUX:D", "C-ID:D", "C-RECON:D:C_univ_new", "C-RECON:D:C_new",
                  "C-RECON:D:C_univ_old", "C-RECON:D:S5R_bands_sum_to_Q_universe", "C-RECON:D:lateral:Muon_Energy_MINOS",
                  "C-PSD:C:D", "C-PSD:M:D", "C-ADD:D"):
            self.assertIn(k, names)

    def test_a_failed_data_fetch_stops_part_d(self):
        self.fst["partb/S3_BeamAngleY1.root"] = {"pass": False}
        r = self.run_data()
        self.assertEqual(r["status"], "STOP")
        self.assertIn("C-FETCH", r["stop"])

    def test_wrong_minos_scale_fails_c_recon(self):
        p = self.paths["c04/minos_rescaled.npz"]
        s = np.load(p)["scale"] * (1 + 1e-9)
        np.savez(p, scale=s)
        r = self.run_data()
        self.assertEqual(r["status"], "STOP")
        self.assertIn("C-RECON:D:lateral:Muon_Energy_MINOS", r["stop"])

    def test_c_new_off_by_1e9_fails(self):
        p = self.paths["g2r/data_g2r.npz"]
        z = dict(np.load(p))
        z["C_new"] = z["C_new"] * (1 + 1e-9)
        np.savez(p, **z)
        r = self.run_data()
        self.assertEqual(r["status"], "STOP")
        self.assertIn("C-RECON:D:C_new", r["stop"])

    def test_x0_not_er_fails_c_x0(self):
        p = self.paths["partc/cov2d_Q_205.npz"]
        z = dict(np.load(p))
        z["x"] = z["x"] * (1 + 1e-15)
        np.savez(p, **z)
        r = self.run_data()
        self.assertEqual(r["status"], "STOP")
        self.assertIn("C-X0", r["stop"])

    def test_wrong_er_file_refuses(self):
        r = m.part_data(SETS, self.fst, self.paths, self.er)
        self.assertEqual(r["status"], "STOP")
        self.assertIn("C-PIN", r["stop"])


class Files(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="center2d-f-")

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_fetch_list_equals_the_remote_readers(self):
        s = importlib.util.spec_from_file_location("remote", os.path.join(HERE, "center2d_fetch_remote.py"))
        r = importlib.util.module_from_spec(s)
        s.loader.exec_module(r)
        self.assertEqual([tuple(x) for x in r.FILES], list(m.FETCH))
        self.assertEqual(r.N_FILES, m.N_FETCH)

    def test_expected_digests_cover_the_fetch(self):
        e = m.expected_digests()
        self.assertEqual(sorted(e), sorted(dict(m.FETCH)))
        self.assertEqual(e["g2r/data_g2r.npz"], "3b8cc7ceaef97c3dc6bbcd2c5cfdf853442c347e37e23f64eca54898d0e9eb4b")

    def test_fetched_refuses_without_the_verifier_line(self):
        with open(os.path.join(self.d, "verify.out"), "w") as f:
            f.write("VERIFY-REFUSED: x\n")
        with self.assertRaisesRegex(m.Stop, "C-FETCH"):
            m.fetched(self.d, {})

    def test_fetched_marks_a_bad_digest(self):
        exp = {lab: "0" * 64 for lab, _ in m.FETCH}
        with open(os.path.join(self.d, "verify.out"), "w") as f:
            f.write(f"VERIFY OK {m.N_FETCH}\n")
        os.makedirs(os.path.join(self.d, "files", "g2r"))
        with open(os.path.join(self.d, "SHA256SUMS"), "w") as f:
            f.writelines(f"{'0' * 64}  files/{lab}\n" for lab in exp)
        with open(os.path.join(self.d, "files", "g2r", "data_g2r.npz"), "wb") as f:
            f.write(b"x")
        st, _ = m.fetched(self.d, exp)
        self.assertFalse(st["g2r/data_g2r.npz"]["pass"])
        self.assertFalse(st["partc/cov2d_Q_205.npz"]["pass"])

    def test_main_refuses_an_existing_record(self):
        p = os.path.join(self.d, "r.json")
        open(p, "w").close()
        self.assertEqual(m.main(["rehearsal", "--out", p]), 2)

    def test_a_stopped_part_makes_the_record_a_stop(self):
        saved = (m.expected_digests, m.fetched, m.part_tune, m.part_data)
        m.expected_digests = lambda: {}
        m.fetched = lambda d, e: ({}, {})
        m.part_tune = lambda T, sets, fst, paths: {"status": "OK"}
        m.part_data = lambda sets, fst, paths, er: {"status": "STOP", "stop": "C-RECON: x"}
        try:
            p = os.path.join(self.d, "r.json")
            self.assertEqual(m.main(["main", self.d, "--out", p]), 3)
            with open(p) as f:
                rec = json.load(f)
            self.assertEqual((rec["status"], rec["stopped_parts"]), ("STOP", ["D"]))
        finally:
            m.expected_digests, m.fetched, m.part_tune, m.part_data = saved

    def test_a_non_finite_record_becomes_a_stop_record(self):
        p = os.path.join(self.d, "nan.json")
        rec = m.write({"schema": "center2d/1", "parts": {"D": {"status": "OK", "x": float("nan")}}}, p)
        self.assertEqual(rec["status"], "STOP")
        with open(p) as f:
            self.assertEqual(json.load(f)["status"], "STOP")

    def test_main_returns_3_when_the_record_had_to_become_a_stop(self):
        saved = (m.expected_digests, m.fetched, m.part_tune, m.part_data)
        m.expected_digests = lambda: {}
        m.fetched = lambda d, e: ({}, {})
        m.part_tune = lambda T, sets, fst, paths: {"status": "OK"}
        m.part_data = lambda sets, fst, paths, er: {"status": "OK", "readings": {"x": float("inf")}}
        try:
            p = os.path.join(self.d, "r2.json")
            self.assertEqual(m.main(["main", self.d, "--out", p]), 3)
            with open(p) as f:
                self.assertEqual(json.load(f)["status"], "STOP")
        finally:
            m.expected_digests, m.fetched, m.part_tune, m.part_data = saved

    def test_main_records_a_stop_for_a_missing_fetch(self):
        p = os.path.join(self.d, "r.json")
        self.assertEqual(m.main(["main", os.path.join(self.d, "none"), "--out", p]), 3)
        with open(p) as f:
            rec = json.load(f)
        self.assertEqual(rec["status"], "STOP")
        self.assertEqual(rec["noise_term"], "not separable, disclosed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
