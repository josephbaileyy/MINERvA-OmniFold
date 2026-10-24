"""Controls for s1_assemble and s1_controls (S1-DECLARATION.md section 5), on synthetic products and the committed
H2 definition: the 16-cell map and its digests, MAT mean-centring (a common offset cancels; CV centring would not),
the constraint-weighted Flux block, the X01 rescale per pT bin, the seed block, the model combination, the exact
universe set (Rvp1pi refused, a missing universe refused), the estimator and source checks, and an end-to-end
assembly whose blocks are recomputed by hand. No real data are read."""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s1_assemble as sa  # noqa: E402
import s1_controls as sc  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DEFINITION = REPO / "nd-unfolding/pv-ladder/readouts/h2_definition.json"
N = 65856


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def meta(schema, seed=42, **extra):
    m = {"schema": schema, "config": "R", "capacity": None, "iters": 5, "estimator_seed": seed,
         "estimator_params": [{"n_estimators": 100, "num_leaves": 8, "random_state": seed}] * 3,
         "refinement": {"classifier_params": {"n_estimators": 400, "num_leaves": 31, "random_state": seed + 3}},
         "input_npz_sha256": sa.INPUT_NPZ_SHA256, "bkg_dump_sha256": sa.BKG_SHA256}
    m.update(extra)
    return m


def save(path: Path, x, m):
    np.savez_compressed(path, xsec_flat=np.asarray(x, float), shape=np.array(sa.s1.fine_shape()), meta=json.dumps(m))


BANK = "/bank"


def weight_sha(tag, k):
    return hashlib.sha256(f"{tag}_{k}".encode()).hexdigest()


def universe_meta(band, idx=0):
    keys = ("wt", "wr", "bkgw", "denom_nd" if band in sa.DETECTOR_BANDS else "tdw")
    tag = f"{band}_{idx}"
    extra = {"universe": f"{band}:{idx}", "bank": BANK, "bank_weight_sha256": {k: weight_sha(tag, k) for k in keys},
             "alignment": {"sentinel_rows": 2801}}
    if band == sa.FLUX:
        extra.update(flux_universe_file="flux.root", universe_info={"flux_ratio_mean": 1.0})
    return meta("s5p-universe/1", **extra)


class Units(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="s1-assemble-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_fine_map_reproduces_the_committed_digest(self):
        fm = sa.fine_map(DEFINITION)
        self.assertEqual(fm.size, N)
        self.assertEqual(sorted(set(fm[fm >= 0])), list(range(16)))
        self.assertEqual(hashlib.sha256(fm.astype("<i4").tobytes()).hexdigest(), sa.FINE_MAP_SHA256)

    def test_fine_map_refuses_a_changed_definition(self):
        d = json.loads(DEFINITION.read_text())
        d["h2_to_reporting_cell"][0], d["h2_to_reporting_cell"][1] = d["h2_to_reporting_cell"][1], 3
        p = self.tmp / "h2.json"
        p.write_text(json.dumps(d))
        with self.assertRaises(SystemExit):
            sa.fine_map(p)
        with mock.patch.object(sa, "DEFINITION_SHA256", digest(p)), self.assertRaises(SystemExit):
            sa.fine_map(p)   # the file digest passes; the fine-map digest does not

    def test_mean_centring_cancels_a_common_offset(self):
        rng = np.random.default_rng(2)
        x0, x1 = rng.uniform(1, 2, 16), rng.uniform(1, 2, 16)
        C = sa.mat_cov(np.array([x0, x1]))
        np.testing.assert_allclose(C, np.outer(x0 - x1, x0 - x1) / 4, rtol=1e-12)
        np.testing.assert_allclose(sa.mat_cov(np.array([x0 + 0.3, x1 + 0.3])), C, rtol=1e-12)
        cv = (x0 + x1) / 2 - 0.3
        cv_centred = (np.outer(x0 - cv, x0 - cv) + np.outer(x1 - cv, x1 - cv)) / 2
        self.assertGreater(np.abs(cv_centred - C).max(), 1e-3)

    def test_weighted_flux_block_is_mat_calccovmx(self):
        rng = np.random.default_rng(3)
        X, w = rng.normal(size=(100, 16)), rng.uniform(0, 5, 100)
        mu = (w[:, None] * X).sum(0) / w.sum()
        want = sum(wi * np.outer(x - mu, x - mu) for wi, x in zip(w, X)) / w.sum()
        np.testing.assert_allclose(sa.mat_cov(X, w), want, rtol=1e-12)
        np.testing.assert_allclose(sa.mat_cov(X, np.ones(100)), sa.mat_cov(X), rtol=1e-12)

    def test_flux_weights_parse_in_universe_order(self):
        rng = np.random.default_rng(4)
        vals = rng.uniform(0, 3, 105)
        lines = [f"Flux {i} {vals[i]!r}" for i in rng.permutation(105)] + ["Other 0 1.0", "# comment"]
        p = self.tmp / "c.txt"
        p.write_text("\n".join(lines) + "\n")
        with mock.patch.object(sa, "CONSTRAINT_SHA256", digest(p)):
            np.testing.assert_array_equal(sa.flux_weights(p), vals[:100])
        with self.assertRaises(SystemExit):
            sa.flux_weights(p)   # wrong digest

    def test_x01_rescales_each_pt_bin_and_checks_the_flux(self):
        flux = np.linspace(1, 2, 14)
        scale = np.vstack([np.linspace(0.99, 1.0, 14), np.linspace(1.0, 1.01, 14)])
        p = self.tmp / "m.npz"
        np.savez(p, phi_cv=flux, scale=scale)
        with mock.patch.object(sa, "X01_SHA256", digest(p)):
            got = sa.x01_scale(p, flux)
            np.testing.assert_array_equal(got, scale)
            pti = sa.pt_index()
            x = np.ones(N)
            y = x * got[1][pti]
            shape = sa.s1.fine_shape()
            np.testing.assert_array_equal(y.reshape(shape)[5], np.full(shape[1:], scale[1][5]))
            with self.assertRaises(SystemExit):
                sa.x01_scale(p, flux * 1.0000001)

    def test_seed_block_and_model_combination(self):
        rng = np.random.default_rng(5)
        means = rng.normal(size=(5, 16))
        np.testing.assert_allclose(sa.seed_block(means), np.cov(means.T, ddof=1), rtol=1e-12)
        f, C = rng.uniform(1, 2, 16), np.cov(rng.normal(size=(40, 16)).T)
        np.testing.assert_allclose(sa.model_abs(f, C), np.diag(f) @ C @ np.diag(f), rtol=1e-12)

    def write_universes(self, d: Path, skip=None, extra=()):
        d.mkdir(exist_ok=True)
        for b, n in sa.EXPECT.items():
            for i in range(n):
                if (b, i) != skip:
                    (d / f"S1_{b}_{i}.npz").write_bytes(b"")
        for name in extra:
            (d / name).write_bytes(b"")

    def test_universe_set_is_exact(self):
        self.write_universes(self.tmp / "u", extra=["S1_CV.npz"])
        bands = sa.universe_bands([self.tmp / "u"], "S1")
        self.assertEqual(sum(len(v) for v in bands.values()), 175)
        self.assertEqual(len(bands), 38)
        self.write_universes(self.tmp / "v", skip=("Flux", 57))
        with self.assertRaises(SystemExit):
            sa.universe_bands([self.tmp / "v"], "S1")
        self.write_universes(self.tmp / "w", extra=["S1_Rvp1pi_0.npz"])
        with self.assertRaises(SystemExit):
            sa.universe_bands([self.tmp / "w"], "S1")

    def test_estimator_and_source_checks(self):
        p = self.tmp / "S1_MaRES_0.npz"
        save(p, np.ones(N), universe_meta("MaRES"))
        sa.check_universe(p, "MaRES")
        for bad in ({"capacity": "400,31"}, {"iters": 10},
                    {"refinement": {"classifier_params": {"n_estimators": 400, "num_leaves": 31, "random_state": 42}}},
                    {"estimator_params": [{"n_estimators": 400, "num_leaves": 31, "random_state": 42}] * 3},
                    {"input_npz_sha256": "x"}):
            save(p, np.ones(N), {**universe_meta("MaRES"), **bad})
            with self.assertRaises(SystemExit, msg=str(bad)):
                sa.check_universe(p, "MaRES")
        q = self.tmp / "S1_GEANT_Pion_0.npz"
        save(q, np.ones(N), universe_meta("MaRES"))   # bank (tdw) weights for a detector band
        with self.assertRaises(SystemExit):
            sa.check_universe(q, "GEANT_Pion")
        r = self.tmp / "S1_Flux_0.npz"
        save(r, np.ones(N), {**universe_meta(sa.FLUX), "flux_universe_file": None})
        with self.assertRaises(SystemExit):
            sa.check_universe(r, sa.FLUX)
        # weight provenance: the recorded digests must be the manifest's (bank) or the receipt's (detector)
        save(p, np.ones(N), universe_meta("MaRES"))
        good = {f"{BANK}/MaRES_0_{k}.npy": weight_sha("MaRES_0", k) for k in ("wt", "wr", "tdw", "bkgw")}
        sa.check_universe(p, "MaRES", good, {})
        with self.assertRaises(SystemExit):
            sa.check_universe(p, "MaRES", {**good, f"{BANK}/MaRES_0_wr.npy": "f" * 64}, {})
        save(q, np.ones(N), universe_meta("GEANT_Pion"))
        sa.check_universe(q, "GEANT_Pion", {}, {f"GEANT_Pion_0_{k}.npy": weight_sha("GEANT_Pion_0", k) for k in ("wt", "wr", "denom_nd", "bkgw")})
        with self.assertRaises(SystemExit):
            sa.check_universe(q, "GEANT_Pion", {}, {})

    def test_controls_finite_gate(self):
        p = self.tmp / "x.npz"
        save(p, np.ones(N), meta("s5p-numerics/1"))
        self.assertEqual(sc.gate_finite(p), (True, ""))
        x = np.ones(N)
        x[7] = -1e-30
        save(p, x, meta("s5p-numerics/1"))
        self.assertFalse(sc.gate_finite(p)[0])
        x[7] = np.nan
        save(p, x, meta("s5p-numerics/1"))
        self.assertFalse(sc.gate_finite(p)[0])


class Gates(unittest.TestCase):
    """s1_controls' cv, central and denominator gates pass on agreeing inputs and stop on a one-entry difference."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="s1-gates-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.x = 1.0 + (np.arange(N) % 5)

    def run_gate(self, argv):
        with mock.patch("sys.stdout"):
            return sc.main(argv)

    def test_cv_and_central(self):
        t, x = self.tmp, self.x
        save(t / "c.npz", x, meta("s5p-numerics/1"))
        save(t / "cv.npz", x, universe_meta("MaRES"))
        self.assertEqual(self.run_gate(["cv", "--cv", str(t / "cv.npz"), "--central", str(t / "c.npz")]), 0)
        y = x.copy()
        y[11] = np.nextafter(y[11], 9)
        save(t / "cv2.npz", y, universe_meta("MaRES"))
        self.assertEqual(self.run_gate(["cv", "--cv", str(t / "cv2.npz"), "--central", str(t / "c.npz")]), 1)
        save(t / "r.npz", x, {})
        save(t / "p5.npz", x, {})
        args = ["central", "--central", str(t / "c.npz"), "--data-r", str(t / "r.npz"), "--p5", str(t / "p5.npz")]
        with mock.patch.multiple(sc, CENTRAL_SHA256=digest(t / "c.npz"), DATA_R_SHA256=digest(t / "r.npz"),
                                 P5_SHA256=digest(t / "p5.npz")):
            self.assertEqual(self.run_gate(args), 0)
            save(t / "p5.npz", y, {})
            self.assertEqual(self.run_gate(args), 1)   # the P5 digest no longer matches, and the arrays differ
        self.assertEqual(self.run_gate(args), 1)       # the real digests are not these synthetic files

    def test_denominator(self):
        t = self.tmp
        shape = sa.s1.fine_shape()
        dn = np.ones(shape)
        np.savez(t / "inputs.npz", denom_nd=dn, **{f"edges_{i}": np.asarray(sa.s1.FINE[k], float) for i, k in enumerate(sa.s1.AXES)})
        (t / "bank").mkdir()
        (t / "dump").mkdir()
        np.savez(t / "bank" / "cv.npz", td=np.zeros(1))
        for tag in sc.GEANT:
            np.save(t / "bank" / f"{tag}_tdw.npy", np.ones(3))
            np.save(t / "dump" / f"{tag}_denom_nd.npy", dn)
        fake = mock.MagicMock()
        fake.denominator.side_effect = lambda bank_cv, tdw, edges: np.ones(shape)
        args = ["denominator", "--inputs-npz", str(t / "inputs.npz"), "--bank", str(t / "bank"), "--dump", str(t / "dump")]
        with mock.patch.dict(sys.modules, {"s5p_universe": fake}), mock.patch.object(sa, "INPUT_NPZ_SHA256", digest(t / "inputs.npz")):
            self.assertEqual(self.run_gate(args), 0)
            fake.denominator.side_effect = lambda bank_cv, tdw, edges: np.full(shape, 1 + 1e-8)
            self.assertEqual(self.run_gate(args), 1)       # the total moves by 1e-8 > 1e-9
            sign = np.where(np.arange(dn.size).reshape(shape) % 2 == 0, 1.0, -1.0)
            fake.denominator.side_effect = lambda bank_cv, tdw, edges: 1 + 5e-4 * sign
            self.assertEqual(self.run_gate(args), 0)       # bin-edge migration: total kept, 5e-4 per cell
            fake.denominator.side_effect = lambda bank_cv, tdw, edges: 1 + 2e-3 * sign
            self.assertEqual(self.run_gate(args), 1)       # 2e-3 per cell exceeds the measured bound


class EndToEnd(unittest.TestCase):
    """A full synthetic assembly: 50 replicas, 175 universes, 10 laterals, 80 seed products, C_model; every block
    recomputed by hand from the same arrays."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="s1-e2e-"))
        t = cls.tmp
        rng = np.random.default_rng(6)
        cls.cv = 1.0 + (np.arange(N) % 7)
        shape = sa.s1.fine_shape()
        cls.flux = np.linspace(1.0, 2.0, shape[0])
        np.savez(t / "inputs.npz", flux=cls.flux)
        cls.scale = np.vstack([np.linspace(0.97, 0.9995816, shape[0]), np.linspace(1.00466854, 1.04, shape[0])])  # varies in pT
        np.savez(t / "x01.npz", phi_cv=cls.flux, scale=cls.scale)
        vals = rng.uniform(0.1, 3, 100)
        (t / "c.txt").write_text("\n".join(f"Flux {i} {v!r}" for i, v in enumerate(vals)) + "\n")
        cls.w = vals
        cls.patch = mock.patch.multiple(sa, INPUT_NPZ_SHA256=digest(t / "inputs.npz"), X01_SHA256=digest(t / "x01.npz"),
                                        CONSTRAINT_SHA256=digest(t / "c.txt"))
        cls.patch.start()
        for d in ("data", "seed", "uni", "lat"):
            (t / d).mkdir()
        NONE = {"bootstrap_seed": None, "jitter_seed": None}
        save(t / "data" / "data_b-_j-.npz", cls.cv, meta("s5p-numerics/1", **NONE, coords="float32"))
        cls.boot = {}
        for b in range(1, 51):
            cls.boot[b] = cls.cv * (1 + 0.01 * rng.normal())
            save(t / "data" / f"data_b{b}_j{100 + b}.npz", cls.boot[b],
                 meta("s5p-numerics/1", bootstrap_seed=b, jitter_seed=100 + b, coords="float64"))
        cls.seed = {42: [cls.boot[b] for b in range(1, 21)]}
        for s in (45, 48, 51, 54):
            cls.seed[s] = []
            for b in range(1, 21):
                x = cls.cv * (1 + 0.01 * rng.normal())
                cls.seed[s].append(x)
                save(t / "seed" / f"S1seed{s}_b{b}_j{100 + b}.npz", x,
                     meta("s5p-numerics/1", seed=s, bootstrap_seed=b, jitter_seed=100 + b, coords="float64"))
        cls.uni = {}
        for band, n in sa.EXPECT.items():
            cls.uni[band] = []
            for i in range(n):
                x = cls.cv * (1 + 0.02 * rng.normal())
                cls.uni[band].append(x)
                save(t / "uni" / f"S1_{band}_{i}.npz", x, universe_meta(band, i))
        save(t / "uni" / "S1_CV.npz", cls.cv, universe_meta("MaRES"))
        cls.lat = {}
        for band in sa.LATERAL_BANDS:
            cls.lat[band] = []
            for i in (0, 1):
                x = cls.cv * (1 + (0.03 if i else -0.01))
                cls.lat[band].append(x)
                save(t / "lat" / f"lat_{band}_{i}_b-_j-.npz", x, {**meta("s5p-numerics/1", **NONE), "input_npz_sha256": "lateral"})
        A = rng.normal(size=(3, 16)) * 0.05
        cls.C_model = A.T @ A
        cls.U = sa.functional_matrix(sa.fine_map(DEFINITION))
        f = cls.U @ cls.cv
        np.savez(t / "cmodel.npz", C_model=cls.C_model, C_abs=cls.C_model * np.outer(f, f))
        data = [t / "data" / "data_b-_j-.npz"] + [t / "data" / f"data_b{b}_j{100 + b}.npz" for b in range(1, 51)]
        (t / "inventory.sha256").write_text("".join(f"{digest(q)}  {q}\n" for q in data))
        cls.data = data
        lats = sorted((t / "lat").glob("*.npz"))
        bank = [(weight_sha(f"{b}_{i}", k), f"{BANK}/{b}_{i}_{k}.npy") for b, n in sa.EXPECT.items()
                if b not in sa.DETECTOR_BANDS for i in range(n) for k in ("wt", "wr", "tdw", "bkgw")]
        (t / "receipt.json").write_text(json.dumps({"files_sha256": {
            f"{b}_{i}_{k}.npy": weight_sha(f"{b}_{i}", k) for b in sa.DETECTOR_BANDS for i in range(2)
            for k in ("wt", "wr", "denom_nd", "bkgw")}}))
        cls.man_lines = {"lat": [f"{digest(q)}  {q}\n" for q in lats], "bank": [f"{s}  {q}\n" for s, q in bank],
                         "receipt": [f"{digest(t / 'receipt.json')}  {t / 'receipt.json'}\n"]}
        cls.inv_lines = {str(q): f"{digest(q)}  {q}\n" for q in data}
        (t / "manifest.txt").write_text("".join(sum(cls.man_lines.values(), [])))
        cls.patch_c = mock.patch.object(sa, "CENTRAL_SHA256", digest(t / "data" / "data_b-_j-.npz"))
        cls.patch_c.start()
        argv = ["--definition", str(DEFINITION), "--inputs-npz", str(t / "inputs.npz"),
                "--central", str(t / "data" / "data_b-_j-.npz"), "--data-dir", str(t / "data"),
                "--seed-dir", str(t / "seed"), "--seed-tag", "S1seed", "--universe-dir", str(t / "uni"),
                "--universe-tag", "S1", "--lateral-dir", str(t / "lat"), "--x01", str(t / "x01.npz"),
                "--flux-constraint", str(t / "c.txt"), "--cmodel", str(t / "cmodel.npz"),
                "--cmodel-sha256", digest(t / "cmodel.npz"), "--cmodel-key", "C_model", "--cmodel-abs-key", "C_abs",
                "--inventory", str(t / "inventory.sha256"), "--manifest", str(t / "manifest.txt"),
                "--detector-receipt", str(t / "receipt.json"), "--out", str(t / "s1.npz")]
        cls.argv = argv
        try:
            cls.rc = sa.main(argv)
        finally:
            cls.patch.stop()
            cls.patch_c.stop()
        cls.z = np.load(t / "s1.npz", allow_pickle=False)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_blocks_recomputed_by_hand(self):
        z, U = self.z, self.U
        self.assertEqual(self.rc, 0)
        f = U @ self.cv
        np.testing.assert_allclose(z["f"], f, rtol=1e-12)
        np.testing.assert_allclose(z["C_stat"], np.cov(np.array([U @ self.boot[b] for b in range(1, 51)]).T, ddof=1), rtol=1e-10)
        X = np.array([U @ x for x in self.uni["Flux"]])
        mu = (self.w[:, None] * X).sum(0) / self.w.sum()
        np.testing.assert_allclose(z["C_band_Flux"], ((X - mu).T * self.w) @ (X - mu) / self.w.sum(), rtol=1e-10)
        X = np.array([U @ x for x in self.uni["2p2h"]])
        np.testing.assert_allclose(z["C_band_2p2h"], np.cov(X.T, bias=True), rtol=1e-10)
        pti = np.unravel_index(np.arange(N), sa.s1.fine_shape())[0]   # independent of sa.pt_index
        m = [U @ (self.lat[sa.MINOS][i] * self.scale[i][pti]) for i in (0, 1)]
        np.testing.assert_allclose(z["C_lat_Muon_Energy_MINOS"], np.outer(m[0] - m[1], m[0] - m[1]) / 4, rtol=1e-10)
        b = [U @ self.lat["BeamAngleX"][i] for i in (0, 1)]
        np.testing.assert_allclose(z["C_lat_BeamAngleX"], np.outer(b[0] - b[1], b[0] - b[1]) / 4, rtol=1e-10)
        means = np.array([np.mean([U @ x for x in self.seed[s]], axis=0) for s in sa.SEEDS])
        np.testing.assert_allclose(z["C_seed"], np.cov(means.T, ddof=1), rtol=1e-10)
        np.testing.assert_allclose(z["C_normalization"], np.outer(0.014 * f, 0.014 * f), rtol=1e-12)
        np.testing.assert_allclose(z["C_model_abs"], self.C_model * np.outer(f, f), rtol=1e-12)
        blocks = [k for k in z.files if k.startswith(("C_stat", "C_band_", "C_lat_", "C_normalization", "C_seed"))]
        self.assertEqual(len(blocks), 1 + 38 + 5 + 1 + 1)
        np.testing.assert_allclose(z["C_e"], sum(z[k] for k in blocks), rtol=1e-12)
        np.testing.assert_allclose(z["C_total"], z["C_e"] + z["C_model_abs"], rtol=1e-12)
        meta_ = json.loads(str(z["meta"]))
        self.assertEqual(meta_["cells"], [f"R{c:02d}" for c in range(16)])
        self.assertIn("Rvp1pi", meta_["not_included"])
        ro = json.loads((self.tmp / "s1.json").read_text())
        np.testing.assert_allclose(ro["relative_sigma"]["C_total"], np.sqrt(np.diag(z["C_total"])) / f, rtol=1e-12)
        np.testing.assert_allclose(ro["relative_sigma"]["flux"], np.sqrt(np.diag(z["C_band_Flux"])) / f, rtol=1e-12)
        self.assertAlmostEqual(sum(ro["trace_share"].values()), 1.0, places=12)

    def test_refuses_an_interrupted_product(self):
        d = self.tmp / "u2"
        d.mkdir()
        for b, n in sa.EXPECT.items():
            for i in range(n):
                (d / f"S1_{b}_{i}.npz").write_bytes(b"")
        (d / "S1_Flux_3.npz.partial-77.npz").write_bytes(b"")
        with self.assertRaises(SystemExit):
            sa.universe_bands([d], "S1")

    def rerun(self, **swap):
        argv = list(self.argv)
        for k, v in swap.items():
            argv[argv.index(k) + 1] = v
        with mock.patch.multiple(sa, INPUT_NPZ_SHA256=digest(self.tmp / "inputs.npz"), X01_SHA256=digest(self.tmp / "x01.npz"),
                                 CONSTRAINT_SHA256=digest(self.tmp / "c.txt"),
                                 CENTRAL_SHA256=digest(self.tmp / "data" / "data_b-_j-.npz")):
            return sa.main(argv)

    def test_refuses_to_overwrite(self):
        with self.assertRaises(SystemExit) as e:
            self.rerun()
        self.assertIn("overwrite", str(e.exception))

    def refused(self, why, **swap):
        with self.assertRaises(SystemExit, msg=str(swap)) as e:
            self.rerun(**swap, **{"--out": str(self.tmp / "other.npz")})
        self.assertIn(why, str(e.exception))

    def test_each_listed_input_is_checked_separately(self):
        t = self.tmp
        for drop, why in ((str(self.data[0]), "central"), (str(self.data[7]), "bootstrap replica")):
            inv = t / f"inv-{why.replace(' ', '_')}.txt"
            inv.write_text("".join(v for k, v in self.inv_lines.items() if k != drop))
            self.refused(why, **{"--inventory": str(inv)})
        for keep, why in ((("bank", "receipt"), "lateral"), (("lat", "bank"), "detector-dump receipt")):
            man = t / f"man-{why.split()[0]}.txt"
            man.write_text("".join(sum((self.man_lines[k] for k in keep), [])))
            self.refused(why, **{"--manifest": str(man)})

    def test_filename_must_match_the_metadata(self):
        t = self.tmp
        d = t / "data-swapped"
        shutil.copytree(t / "data", d)
        p = d / "data_b7_j107.npz"
        z = np.load(p, allow_pickle=False)
        m = json.loads(str(z["meta"]))
        save(p, z["xsec_flat"], {**m, "jitter_seed": 108})
        inv = t / "inv-swapped.txt"
        inv.write_text("".join(f"{digest(q)}  {q}\n" for q in sorted(d.glob("data_b*.npz"))))
        self.refused("jitter_seed", **{"--data-dir": str(d), "--central": str(d / "data_b-_j-.npz"), "--inventory": str(inv)})
        s = t / "seed-swapped"
        shutil.copytree(t / "seed", s)
        q = s / "S1seed48_b3_j103.npz"
        z = np.load(q, allow_pickle=False)
        save(q, z["xsec_flat"], {**json.loads(str(z["meta"])), "bootstrap_seed": 4})
        self.refused("bootstrap_seed", **{"--seed-dir": str(s)})
        with mock.patch("sys.stdout"), mock.patch.object(sa, "INPUT_NPZ_SHA256", digest(t / "inputs.npz")):
            self.assertEqual(sc.main(["seeds", "--dir", str(s), "--tag", "S1seed", "--seed", "48"]), 1)
            self.assertEqual(sc.main(["seeds", "--dir", str(t / "seed"), "--tag", "S1seed", "--seed", "48"]), 0)

    def test_refuses_unlisted_inputs_and_swapped_model_keys(self):
        empty = self.tmp / "empty.txt"
        empty.write_text("")
        for swap, why in (({"--inventory": str(empty)}, "is not in its manifest"),
                          ({"--manifest": str(empty)}, "is not in its manifest"),
                          ({"--cmodel-abs-key": "C_model"}, "absolute matrix")):
            with self.assertRaises(SystemExit, msg=str(swap)) as e:
                self.rerun(**swap, **{"--out": str(self.tmp / "other.npz")})
            self.assertIn(why, str(e.exception))

if __name__ == "__main__":
    unittest.main()
