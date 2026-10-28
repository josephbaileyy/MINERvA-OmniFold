"""Controls for fd_flux_boot (FD-FLUX-BOOT-DECLARATION.md section 6), on synthetic matrices and on G-DIAG's synthetic
Stage G tree with 100 synthetic weighted Flux universes whose block is S1's rule applied to them. No real prediction,
covariance or data value is read; the committed records are read only for their digests (CommittedPins).

* Pure: the identity replicate is S1's rule; the correlation swap keeps S1's variances bit for bit and takes the
  replicate's correlations; chi2 and the band by hand; the seed's index matrix is the declared one; and the spread of
  the weighted estimator follows 1/n_eff (the declaration's section 4).
* End to end, as invoked (-I -B, cwd outside nd-unfolding): every band, correlation and uniform chi2 recomputed here
  by an independent loop; the identity reproduces Stage G; GiBUU on its eight cells; no key p anywhere.
* Each control B0-B5 refuses on its own planted defect, with nothing written; the real script refuses synthetic
  records at D0."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
sys.path.insert(1, str(Path(__file__).resolve().parent))
import fd_flux_boot as FB  # noqa: E402
import fd_g_compare as G  # noqa: E402
import s1_assemble as sa  # noqa: E402
from test_fd_g_compare import digest, run_isolated  # noqa: E402
from test_fd_g_diag import DiagTree  # noqa: E402
from test_fd_g_followup import find_p  # noqa: E402

REPO = ND.parent
FD = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024"
CONTROLS = ["D0", "D1", "D2", "D3", "D4", "D5", "B0", "B1", "B2", "B3", "B4", "B5", "B6"]


def heavy_weights(n=100, seed=3, target=19.0):
    """Positive weights whose n_eff is close to target (S1's is 19.06): lognormal, its width solved for."""
    z = np.random.default_rng(seed).normal(size=n)
    lo, hi = 0.0, 5.0
    for _ in range(60):
        s = (lo + hi) / 2
        w = np.exp(s * z)
        lo, hi = (s, hi) if FB.n_eff(w) > target else (lo, s)
    return np.exp(s * z)


def wcov(X, w):
    """An independent weighted covariance: sum_u w_u (x_u - mu)(x_u - mu)^T / sum w, mu the weighted mean."""
    mu = np.average(X, axis=0, weights=w)
    return np.einsum("u,ui,uj->ij", w, X - mu, X - mu) / w.sum()


def quad(d, M):
    return float(d @ np.linalg.inv(M) @ d)


class BootTree(DiagTree):
    """G-DIAG's tree with its flux block replaced by S1's rule on 100 synthetic weighted universes, which are written
    as S1_Flux_<u>.npz (constant within each cell, so U @ xsec_flat is the universe's cell integrals), with a
    constraint file and S1's readout meta recording both."""

    def __init__(self, root, seed=0, scale=1e-39):
        super().__init__(root, seed=seed, scale=scale)
        # amendment 1: the real flux block's regime (correlations 0.913-0.998, lambda_min 2.19e-7 and lambda_max
        # 2.08e-2 relative to f, n_eff 19.06; FD-FLUX-BOOT-DECLARATION-AMENDMENT-1.md section 2); Regime pins it
        rng = np.random.default_rng(seed + 200)
        common = rng.normal(0, 0.0325, 100)
        tilt = rng.normal(0, 0.0092, 100)
        x16 = np.linspace(-1, 1, 16)
        rel = common[:, None] + tilt[:, None] * x16[None, :] + rng.normal(0, 0.00093, (100, 16))
        self.Xint = self.f * (1 + rel)                      # each universe's cell integrals
        self.w = heavy_weights()
        self.universe_fine = [self.fine_of(x) for x in self.Xint]
        self.X = np.array([self.U @ v for v in self.universe_fine])
        # amendment 1 (review): S1's block differs from its rebuild in the last bits, as the real one does (up to 27
        # ulp, 1.75e-15 of its largest entry), so B2 and B6 carry a non-zero difference through the swap
        self.rebuild = sa.mat_cov(self.X, self.w)
        k = np.random.default_rng(seed + 300).integers(-27, 28, (16, 16))
        k = np.triu(k) + np.triu(k, 1).T
        self.blocks["band:Flux"] = self.rebuild + k * np.spacing(np.abs(self.rebuild))
        self.Ce = sum(self.blocks[k] for k in sorted(self.blocks))
        self.Ct = self.Ce + self.Cma

    def fine_of(self, cells):
        volc = self.U.sum(axis=1)
        return np.where(self.fm >= 0, (cells / volc)[np.clip(self.fm, 0, None)], 2.2e-41)

    def write(self, mutate=None, role="adopted", g_mutate=None, s1_mutate=None, universe_mutate=None,
              constraint_lines=None):
        super().write(mutate, role=role, g_mutate=g_mutate)
        R = self.root
        self.flux = R / "flux"
        self.flux.mkdir()
        rec = {}
        for u, x in enumerate(self.universe_fine):
            meta = {"schema": "s5p-universe/1", "universe": f"Flux:{u}"}
            arr = {"xsec_flat": x, "shape": np.array([1]), "meta": json.dumps(meta)}
            if universe_mutate:
                arr = universe_mutate(u, arr) or arr
            if arr is False:
                continue
            p = self.flux / f"S1_Flux_{u}.npz"
            np.savez_compressed(p, **arr)
            rec[p.name] = digest(p)
        self.constraint = R / "constraint.txt"
        lines = constraint_lines or (["MaRES 0 1.5"] + [f"Flux {u} {w!r}" for u, w in enumerate(self.w)]
                                     + ["Flux 100 9.0", "Flux 101 9.0"])
        self.constraint.write_text("\n".join(lines) + "\n")
        rec["constraint"] = digest(self.constraint)
        s1j = json.loads((R / "s1_assembly.json").read_text())
        s1j["meta"] = {"inputs_sha256": rec, "flux_weights": {"sum": float(self.w.sum()), "n_eff": FB.n_eff(self.w)}}
        if s1_mutate:
            s1_mutate(s1j)
        p = R / "s1_assembly.json"
        p.write_text(json.dumps(s1j))
        self.bpins = {**self.dpins, "s1_json": digest(p), "constraint": digest(self.constraint)}
        self.bargv = self.dargv[:-2] + ["--flux-dir", str(self.flux), "--flux-constraint", str(self.constraint),
                                        "--out-json", str(self.out / "boot.json")]
        return self

    def config(self):
        return {"nd": str(ND), "pins": self.bpins, "predictions": self.predictions, "argv": self.bargv}


WRAPPER = r"""
import json, sys
cfg = json.load(open(sys.argv[1]))
sys.path.insert(0, cfg["nd"])
import fd_g_compare as g
import fd_flux_boot as m
import s1_assemble as sa
m.PINS = cfg["pins"]
sa.CONSTRAINT_SHA256 = cfg["pins"]["constraint"]
g.PREDICTIONS = tuple(dict(p, meta=tuple(p["meta"])) for p in cfg["predictions"])
sys.argv = ["fd_flux_boot.py"] + cfg["argv"]
raise SystemExit(m.main(cfg["argv"]))
"""


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpc = Path(tempfile.mkdtemp(prefix="fd-fb-c-"))
        cls.tree = BootTree(cls.tmpc / "t").write()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpc, ignore_errors=True)

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd-fb-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        out = self.tree.out / "boot.json"
        if out.exists():
            out.unlink()

    def fresh(self, **kw):
        return BootTree(self.tmp / "t").write(**kw)

    def run_module(self, tree):
        cfg, w = self.tmp / "cfg.json", self.tmp / "wrapper.py"
        cfg.write_text(json.dumps(tree.config()))
        w.write_text(WRAPPER)
        return run_isolated([str(w), str(cfg)])

    def run_inproc(self, tree):
        with mock.patch("sys.stdout"), mock.patch.object(sa, "CONSTRAINT_SHA256", tree.bpins["constraint"]):
            return FB.run(FB.build_args(tree.bargv), tree.bpins, tree.predictions)

    def assertStops(self, tree, control, why=""):
        with self.assertRaises(SystemExit) as cm:
            self.run_inproc(tree)
        self.assertIn(f"FAIL control {control}:", str(cm.exception.code))
        self.assertIn(why, str(cm.exception.code))
        self.assertFalse((tree.out / "boot.json").exists(), "a refused run wrote its readout")


# ------------------------------------------------------------------------------------------------ pure


class Pure(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(5)
        self.X = 1 + rng.normal(0, 0.03, (100, 1)) + rng.normal(0, 0.01, (100, 16))
        self.w = heavy_weights()

    def test_the_identity_replicate_is_s1s_rule_and_an_independent_weighted_covariance(self):
        C = FB.replicate_block(self.X, self.w, np.arange(100))
        np.testing.assert_array_equal(C, sa.mat_cov(self.X, self.w))
        np.testing.assert_allclose(C, wcov(self.X, self.w), rtol=1e-12)

    def test_a_replicate_carries_each_drawn_universes_weight(self):
        i = np.random.default_rng(1).integers(0, 100, 100)
        np.testing.assert_allclose(FB.replicate_block(self.X, self.w, i), wcov(self.X[i], self.w[i]), rtol=1e-12)
        self.assertFalse(np.allclose(FB.replicate_block(self.X, self.w, i), wcov(self.X[i], np.ones(100)), rtol=1e-6))

    def test_the_correlation_swap_keeps_s1s_variances_and_takes_the_replicates_correlations(self):
        C0 = wcov(self.X, self.w)
        Cs = wcov(self.X[::-1][:60], self.w[:60])
        out = FB.correlation_swap(Cs, C0)
        np.testing.assert_array_equal(np.diag(out), np.diag(C0))
        r = lambda C: C / np.sqrt(np.outer(np.diag(C), np.diag(C)))
        np.testing.assert_allclose(r(out), r(Cs), rtol=1e-12)
        np.testing.assert_allclose(out, out.T, rtol=0, atol=0)

    def test_chi2s_is_stage_gs_compare_in_absolute_units_and_none_when_not_positive_definite(self):
        rng = np.random.default_rng(2)
        f = rng.uniform(1, 3, 16) * 1e-39
        g = f * (1 + rng.normal(0, 0.05, 16))
        Vg = (0.01 * g) ** 2
        A = rng.normal(size=(30, 16))
        C = (A.T @ A / 30 * 1e-3 + 1e-4 * np.eye(16)) * np.outer(f, f)
        cells = [0, 1, 2, 3, 8, 9, 10, 11]
        t, s = FB.chi2s(f, g, Vg, C, cells)
        ref = G.compare(f, g, Vg, C, cells, "x")
        self.assertEqual((t, s), (ref["total"]["chi2"], ref["shape_only"]["chi2"]))
        i = np.asarray(cells)
        M = C[np.ix_(i, i)] + np.diag(Vg[i])
        self.assertAlmostEqual(t, quad((f - g)[i], M), delta=1e-9 * t)
        self.assertAlmostEqual(s, quad((f - g)[i], M + 100 * np.outer(f[i], f[i])), delta=1e-8 * s)
        self.assertIsNone(FB.chi2s(f, g, Vg, C - 5 * np.diag(np.diag(C)), cells))

    def test_band_percentiles_and_halves(self):
        v = np.arange(1, 2001, dtype=float)
        b = FB.band(v)
        self.assertEqual(list(b["percentiles"]), ["2.5", "16", "50", "84", "97.5"])
        self.assertAlmostEqual(b["percentiles"]["50"], 1000.5)
        self.assertAlmostEqual(b["percentiles"]["16"], 1 + 0.16 * 1999)
        self.assertEqual((b["min"], b["max"]), (1.0, 2000.0))
        self.assertAlmostEqual(b["halves"][0]["50"], 500.5)
        self.assertAlmostEqual(b["halves"][1]["50"], 1500.5)
        self.assertNotIn("basic", b)
        c = FB.band(v, centre=900.0)
        for q in FB.PERCENTILES:
            self.assertAlmostEqual(c["basic"][f"{q:g}"], 1800.0 - c["percentiles"][f"{100 - q:g}"])
        self.assertAlmostEqual(c["basic"]["16"], 1800.0 - (1 + 0.84 * 1999))
        self.assertAlmostEqual(c["offset_median_minus_centre"], 1000.5 - 900.0)

    def test_the_seed_gives_the_declared_index_matrix(self):
        idx = FB.indices()
        self.assertEqual(idx.shape, (2000, 100))
        self.assertEqual((FB.SEED, FB.B_REPLICATES, FB.N_UNIVERSES), (20261027, 2000, 100))
        self.assertEqual(FB.index_digest(idx), FB.INDEX_SHA256)
        self.assertNotEqual(FB.index_digest(FB.indices(seed=FB.SEED + 1)), FB.INDEX_SHA256)

    def test_the_spread_follows_one_over_n_eff(self):
        """Section 4: under this resampling the weighted mean's bootstrap sd is its linearized value
        sqrt(sum w^2 (x - mu)^2) / sum w (ratio 1), and that is sigma / sqrt(n_eff) when the residuals do not follow
        the weights. So the heavy weights (n_eff about 19) widen the spread by about sqrt(100 / 19) over equal weights."""
        idx = FB.indices()
        X = np.random.default_rng(8).normal(0, 1, (100, 16))
        heavy, flat = self.w, np.ones(100)
        self.assertAlmostEqual(FB.n_eff(heavy), 19.0, delta=0.3)
        for w in (heavy, flat):
            got = FB.mean_spread(X, w, idx)
            r = np.asarray(got["delta_method_ratio"])
            self.assertTrue(np.all(np.abs(r - 1) < 0.12), r)
            mu = np.average(X, axis=0, weights=w)
            sw = np.sqrt(np.average((X - mu) ** 2, axis=0, weights=w))
            sd = np.std([np.average(X[i], axis=0, weights=w[i]) for i in idx], axis=0, ddof=1)
            np.testing.assert_allclose(got["sd_over_sigma_w_root_n_eff"], sd / (sw / np.sqrt(FB.n_eff(w))), rtol=1e-10)
        sd = lambda w: np.std([np.average(X[i, 0], weights=w[i]) for i in idx], ddof=1)
        ratio = sd(heavy) / sd(flat)
        self.assertGreater(ratio, 0.7 * np.sqrt(100 / 19))
        self.assertLess(ratio, 1.3 * np.sqrt(100 / 19))


# ------------------------------------------------------------------------------------------------ end to end


def by_hand(tree):
    """An independent loop: every replicate's block from wcov, each variant swapped for the flux group in the reported
    relative matrix, each prediction's total and shape-only chi2 by inverse; and the uniform block."""
    ff = np.outer(tree.f, tree.f)
    C0 = tree.blocks["band:Flux"]
    rest = (tree.Ct + tree.Cx - C0) / ff
    out = {v: {} for v in FB.VARIANTS}
    uni = {}
    corr = []
    Cu = wcov(tree.X, np.ones(100))
    idx = FB.indices()
    for spec in tree.predictions:
        name = spec["name"]
        cells = list(G.GIBUU_CELLS) if name == "gibuu" else list(range(16))
        i = np.asarray(cells)
        p = tree.preds[name]
        gc = p["g"][i]
        Vg = np.diag(p["relvar"][i] * gc ** 2 / tree.f[i] ** 2)
        d = (tree.f[i] - gc) / tree.f[i]
        one = np.ones((len(i), len(i)))
        for v in FB.VARIANTS:
            tot, sh = [], []
            for ib in idx:
                Cs = wcov(tree.X[ib], tree.w[ib])
                if v == "correlation":
                    s0, ss = np.sqrt(np.diag(C0)), np.sqrt(np.diag(Cs))
                    Cs = Cs / np.outer(ss, ss) * np.outer(s0, s0)
                M = rest[np.ix_(i, i)] + (Cs / ff)[np.ix_(i, i)] + Vg
                tot.append(quad(d, M))
                sh.append(quad(d, M + 100 * one))
            out[v][name] = (np.array(tot), np.array(sh))
        M = rest[np.ix_(i, i)] + (Cu / ff)[np.ix_(i, i)] + Vg
        uni[name] = (quad(d, M), quad(d, M + 100 * one))
    rc = lambda C: C[4, 8] / np.sqrt(C[4, 4] * C[8, 8])
    rep = {v: [] for v in FB.VARIANTS}
    for ib in idx:
        Cs = wcov(tree.X[ib], tree.w[ib])
        corr.append(rc(Cs))
        s0, ss = np.sqrt(np.diag(C0)), np.sqrt(np.diag(Cs))
        for v, Cv in (("correlation", Cs / np.outer(ss, ss) * np.outer(s0, s0)), ("block", Cs)):
            rep[v].append(rc(rest + Cv / ff))
    return out, uni, np.array(corr), {v: np.array(x) for v, x in rep.items()}, rc(rest + C0 / ff)


def corr_s1(tree):
    C0 = tree.blocks["band:Flux"]
    return C0[4, 8] / np.sqrt(C0[4, 4] * C0[8, 8])


class Regime(Base):
    def test_the_fixtures_flux_block_is_in_the_real_blocks_regime(self):
        """Amendment 1: correlations about 0.913-0.998 with top ones at or above 0.97, lambda_min about 2e-7 relative
        to f, n_eff about 19, as the real block measured (the amendment's section 2)."""
        tree = self.tree
        C = tree.blocks["band:Flux"] / np.outer(tree.f, tree.f)
        r = C / np.sqrt(np.outer(np.diag(C), np.diag(C)))
        off = r[~np.eye(16, dtype=bool)]
        e = np.linalg.eigvalsh(C)
        self.assertGreaterEqual(off.max(), 0.997)
        self.assertTrue(0.90 <= off.min() <= 0.93, off.min())
        self.assertTrue(1e-7 <= e[0] <= 5e-7, e[0])
        self.assertTrue(1.5e-2 <= e[-1] <= 3e-2, e[-1])
        self.assertAlmostEqual(FB.n_eff(tree.w), 19.0, delta=0.3)
        C0, C1 = tree.blocks["band:Flux"], tree.rebuild
        ulp = np.abs(C1 - C0) / np.spacing(np.abs(C0))
        self.assertFalse(np.array_equal(C1, C0))
        self.assertLessEqual(ulp.max(), 28)
        self.assertGreaterEqual(ulp.max(), 20)


class EndToEnd(Base):
    def test_run_as_invoked_and_recomputed_by_hand(self):
        tree = self.tree
        r = self.run_module(tree)
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        for c in CONTROLS:
            self.assertIn(f"PASS control {c} ", r.stdout)
        out = json.loads((tree.out / "boot.json").read_text())
        self.assertEqual(out["schema"], "fd-flux-boot-readout/1")
        self.assertEqual(out["controls_passed"], CONTROLS)
        self.assertEqual(find_p(out), [])
        self.assertEqual(out["non_finite_written_as_null"], 0)
        self.assertEqual(out["constants"]["replicates"], 2000)
        self.assertEqual(out["constants"]["index_sha256"], FB.INDEX_SHA256)
        self.assertEqual(out["constants"]["reported_matrix"], "C_total + C_resp + V_g")
        g = {p["name"]: p for p in json.loads(tree.g_readout.read_text())["predictions"]}
        hand, uni, corr, rep, rep_s1 = by_hand(tree)
        for name, rec in out["identity"].items():
            self.assertEqual(rec["chi2_stage_g"], g[name]["total"]["chi2"])
            self.assertEqual(rec["shape_only_stage_g"], g[name]["shape_only"]["chi2"])
            # amendment 1: at least 100 x inside B2's 1e-10, on this platform's BLAS (run on a login node too)
            self.assertLessEqual(rec["relative_difference"], 1e-12, name)
        for v in FB.VARIANTS:
            for name, rec in out["bands"][v].items():
                cells = list(G.GIBUU_CELLS) if name == "gibuu" else list(range(16))
                self.assertEqual(rec["cells"], [f"R{c:02d}" for c in cells])
                self.assertEqual(rec["ndf"], len(cells))
                for key, vals in (("total", hand[v][name][0]), ("shape_only", hand[v][name][1])):
                    want = np.percentile(vals, FB.PERCENTILES)
                    got = [rec[key]["percentiles"][f"{q:g}"] for q in FB.PERCENTILES]
                    np.testing.assert_allclose(got, want, rtol=1e-9)
                    np.testing.assert_allclose([rec[key]["min"], rec[key]["max"]], [vals.min(), vals.max()], rtol=1e-9)
                    np.testing.assert_allclose([rec[key]["halves"][1]["50"]], [np.median(vals[1000:])], rtol=1e-9)
                    centre = rec["chi2_stage_g"] if key == "total" else rec["shape_only_stage_g"]
                    np.testing.assert_allclose([rec[key]["basic"][f"{q:g}"] for q in FB.PERCENTILES],
                                               2 * centre - np.percentile(vals, [100 - q for q in FB.PERCENTILES]),
                                               rtol=1e-9)
                    self.assertAlmostEqual(rec[key]["offset_median_minus_centre"], np.median(vals) - centre,
                                           delta=1e-9 * centre)
            self.assertNotEqual(out["bands"][v]["genie_cv"]["total"]["percentiles"]["16"],
                                out["bands"][v]["genie_cv"]["total"]["percentiles"]["84"])
        for name, (t, s) in uni.items():
            self.assertAlmostEqual(out["uniform"]["predictions"][name]["chi2"], t, delta=1e-9 * t)
            self.assertAlmostEqual(out["uniform"]["predictions"][name]["shape_only"], s, delta=1e-9 * s)
        np.testing.assert_allclose(out["correlation_band"]["flux_block"]["percentiles"]["50"], np.median(corr), rtol=1e-9)
        for v in FB.VARIANTS:
            got = out["correlation_band"][f"reported_matrix_{v}"]["percentiles"]
            np.testing.assert_allclose([got[f"{q:g}"] for q in FB.PERCENTILES], np.percentile(rep[v], FB.PERCENTILES),
                                       rtol=1e-9)
        self.assertAlmostEqual(out["correlation_s1"]["reported_matrix"], rep_s1, delta=1e-12)
        self.assertAlmostEqual(out["correlation_s1"]["flux_block"], corr_s1(tree), delta=1e-12)
        self.assertAlmostEqual(out["n_eff"]["s1"], FB.n_eff(tree.w), places=12)
        mu = np.average(tree.X, axis=0, weights=tree.w)
        sw = np.sqrt(np.average((tree.X - mu) ** 2, axis=0, weights=tree.w))
        sd = np.std([np.average(tree.X[i], axis=0, weights=tree.w[i]) for i in FB.indices()], axis=0, ddof=1)
        np.testing.assert_allclose(list(out["n_eff"]["sd_over_sigma_w_root_n_eff"].values()),
                                   sd / (sw / np.sqrt(FB.n_eff(tree.w))), rtol=1e-9)
        self.assertNotIn("n_eff_replicate", out["n_eff"])
        self.assertIn("that the chi2 is insensitive to the flux correlations", out["labels"]["not_citable_for"])
        self.assertTrue(out["labels"]["band"].startswith("estimation uncertainty, not sensitivity"))
        lines = [ln for ln in r.stdout.splitlines() if ln.startswith("[3D]")]
        self.assertEqual(len(lines), 1 + 2 * 5 + 1)
        self.assertIn(FB.LABEL, lines[0])

    def test_the_identity_is_stage_gs_compare_on_the_declared_swap_bit_for_bit(self):
        """Amendment 1 (review): the identity record is compare() on C_total + C_resp + (C1 - C0), exactly, with C1 the
        rebuild and C0 S1's block, which differ in the last bits here as on real inputs."""
        tree = self.tree
        self.assertEqual(self.run_inproc(tree), 0)
        out = json.loads((tree.out / "boot.json").read_text())
        with mock.patch("sys.stdout"):
            x = FB.D.load(FB.build_args(tree.bargv), tree.bpins, tree.predictions)
        M = (tree.Ct + tree.Cx) + (sa.mat_cov(tree.X, tree.w) - tree.blocks["band:Flux"])
        for spec in tree.predictions:
            cells, g, Vg = x.integ[spec["name"]]
            ref = G.compare(x.f, g, Vg, M, list(cells), "hand")
            rec = out["identity"][spec["name"]]
            self.assertEqual(rec["chi2_rebuilt"], ref["total"]["chi2"], spec["name"])
            self.assertEqual(rec["shape_only_rebuilt"], ref["shape_only"]["chi2"], spec["name"])

    def test_the_two_variants_differ_and_the_correlation_one_keeps_variances(self):
        tree = self.tree
        self.assertEqual(self.run_inproc(tree), 0)
        out = json.loads((tree.out / "boot.json").read_text())
        a, b = (out["bands"][v]["nuwro"]["total"]["percentiles"]["50"] for v in FB.VARIANTS)
        self.assertNotAlmostEqual(a, b, delta=1e-6 * a)

    def test_refuses_to_overwrite(self):
        tree = self.tree
        (tree.out / "boot.json").write_text("{}")
        with self.assertRaises(SystemExit) as cm:
            self.run_inproc(tree)
        self.assertIn("refusing to overwrite", str(cm.exception.code))
        self.assertEqual((tree.out / "boot.json").read_text(), "{}")


# ------------------------------------------------------------------------------------------------ controls


class Controls(Base):
    def test_b0_a_universe_whose_digest_is_not_s1s(self):
        tree = self.fresh()
        p = tree.flux / "S1_Flux_7.npz"
        with np.load(p) as z:
            arr = {k: z[k] for k in z.files}
        arr["xsec_flat"] = arr["xsec_flat"] * (1 + 1e-9)
        np.savez_compressed(p, **arr)
        self.assertStops(tree, "B0", "S1_Flux_7.npz sha256")

    def test_b0_a_universe_named_for_another(self):
        def swap(u, arr):
            if u == 3:
                arr["meta"] = json.dumps({"schema": "s5p-universe/1", "universe": "Flux:4"})
        self.assertStops(self.fresh(universe_mutate=swap), "B0", "S1_Flux_3.npz is Flux:4")

    def test_b0_a_missing_universe(self):
        tree = self.fresh()
        (tree.flux / "S1_Flux_99.npz").unlink()
        self.assertStops(tree, "B0", "S1_Flux_99.npz missing")

    def test_b0_s1_records_another_number_of_universes(self):
        self.assertStops(self.fresh(s1_mutate=lambda j: j["meta"]["inputs_sha256"].pop("S1_Flux_50.npz")), "B0",
                         "S1_Flux_50.npz sha256")

    def test_b0_s1_records_a_101st_universe(self):
        tree = self.fresh(s1_mutate=lambda j: j["meta"]["inputs_sha256"].update({"S1_Flux_100.npz": "2" * 64}))
        self.assertStops(tree, "B0", "S1 records 101")

    def test_b0_the_constraint_file_is_not_the_pin_or_s1s(self):
        tree = self.fresh()
        tree.bpins["constraint"] = "0" * 64
        with self.assertRaises(SystemExit) as cm, mock.patch("sys.stdout"):
            FB.run(FB.build_args(tree.bargv), tree.bpins, tree.predictions)
        self.assertIn("FAIL control B0: the constraint file is the pin", str(cm.exception.code))
        tree = self.fresh(s1_mutate=lambda j: j["meta"]["inputs_sha256"].update(constraint="1" * 64))
        self.assertStops(tree, "B0", "the constraint file is the pin and the one S1 recorded")

    def test_b0_the_weights_are_not_s1s(self):
        tree = self.fresh(s1_mutate=lambda j: j["meta"]["flux_weights"].update(n_eff=j["meta"]["flux_weights"]["n_eff"] * (1 + 1e-9)))
        self.assertStops(tree, "B0", "n_eff")

    def test_b0_too_few_flux_weights(self):
        lines = [f"Flux {u} 1.0" for u in range(99)]
        self.assertStops(self.fresh(constraint_lines=lines), "B0", "usable Flux weights")

    def test_b1_the_block_rebuilt_without_the_weights(self):
        tree = self.tree
        with mock.patch.object(FB, "replicate_block", lambda X, w, i: sa.mat_cov(X[i])):
            self.assertStops(tree, "B1", "rebuilt from the universes")

    def test_b2_a_shape_only_chi2_that_is_not_stage_gs(self):
        tree = self.tree
        real = FB.chi2s
        with mock.patch.object(FB, "chi2s", lambda *a: (real(*a)[0], real(*a)[0])):
            self.assertStops(tree, "B2", "reproduces Stage G")

    def test_b3_another_index_matrix(self):
        tree = self.tree
        with mock.patch.object(FB, "indices", lambda: np.random.default_rng(1).integers(0, 100, (2000, 100))):
            self.assertStops(tree, "B3", "index matrix")

    def test_b4_a_replicate_with_a_non_positive_variance(self):
        tree = self.tree
        real = FB.replicate_block

        def bad(X, w, i):
            C = real(X, w, i)
            if not np.array_equal(i, np.arange(100)):
                C = C.copy()
                C[5, 5] = -C[5, 5]
            return C
        with mock.patch.object(FB, "replicate_block", bad):
            self.assertStops(tree, "B4", "flux variance is not positive")

    def test_b4_an_indefinite_swapped_matrix(self):
        tree = self.tree
        real = FB.replicate_block

        def bad(X, w, i):
            C = real(X, w, i)
            if not np.array_equal(i, np.arange(100)):
                s = np.sqrt(np.diag(C))
                C = np.outer(s, s) * 3.0
                np.fill_diagonal(C, s ** 2)
            return C
        with mock.patch.object(FB, "replicate_block", bad):
            self.assertStops(tree, "B4", "positive definite")

    def test_b4_an_indefinite_uniform_matrix_refuses(self):
        tree = self.tree
        real = sa.mat_cov

        def bad(X, w=None):
            C = real(X, w)
            if w is None:
                s = np.sqrt(np.diag(C))
                C = np.outer(s, s) * 3.0
                np.fill_diagonal(C, s ** 2)
            return C
        with mock.patch.object(FB.sa, "mat_cov", bad):
            self.assertStops(tree, "B4", "uniform")

    def test_b6_a_swap_that_scales_the_difference_by_one_plus_1e_6(self):
        """A swap error too small for B2 (the identity's difference is a few ulp) or B4 (every matrix stays positive
        definite): only the matrix-level check sees it, on the replicates."""
        tree = self.tree
        with mock.patch.object(FB, "swapped", lambda Cg, C, C0: Cg + (1 + 1e-6) * (C - C0)):
            self.assertStops(tree, "B6", "C_resp + its flux block")

    def test_gross_swap_errors_refuse_before_b6(self):
        tree = self.tree
        with mock.patch.object(FB, "swapped", lambda Cg, C, C0: Cg + 2 * (C - C0)):
            self.assertStops(tree, "B4", "positive definite")
        with mock.patch.object(FB, "swapped", lambda Cg, C, C0: Cg - tree.Cx + (C - C0)):
            self.assertStops(tree, "B2", "reproduces Stage G")

    def test_b5_a_swap_that_moves_a_variance_by_one_ulp(self):
        tree = self.tree
        real = FB.correlation_swap

        def bad(Cs, C0):
            out = real(Cs, C0)
            out[2, 2] = np.nextafter(out[2, 2], np.inf)
            return out
        with mock.patch.object(FB, "correlation_swap", bad):
            self.assertStops(tree, "B5", "bit for bit")


class Invocation(Base):
    def test_the_real_script_reaches_d0_and_refuses_synthetic_records(self):
        r = run_isolated([str(ND / "fd_flux_boot.py"), *self.tree.bargv])
        self.assertEqual(r.returncode, 1, r.stderr[-2000:])
        self.assertIn("FAIL control D0:", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_every_input_is_required(self):
        argv = self.tree.bargv
        for k in ("--flux-dir", "--flux-constraint"):
            i = argv.index(k)
            r = run_isolated([str(ND / "fd_flux_boot.py"), *argv[:i], *argv[i + 2:]])
            self.assertEqual(r.returncode, 2, r.stderr)
            self.assertIn(k, r.stderr)


class CommittedPins(unittest.TestCase):
    def test_the_pins_are_s1s_committed_records(self):
        s1 = FD / "s1/readout/s1_assembly.json"
        self.assertEqual(digest(s1), FB.PINS["s1_json"])
        meta = json.loads(s1.read_text())["meta"]
        self.assertEqual(meta["inputs_sha256"]["constraint"], FB.PINS["constraint"])
        self.assertEqual(round(meta["flux_weights"]["n_eff"], 2), 19.06)
        self.assertEqual(round(meta["flux_weights"]["sum"], 3), 211.012)
        flux = FD / "s1/readout/s1_assembly"
        for u in range(100):
            name = f"S1_Flux_{u}.npz"
            self.assertEqual(digest(flux / name), meta["inputs_sha256"][name], name)

    def test_the_stage_g_pins_are_g_diags(self):
        for k, v in FB.D.PINS.items():
            self.assertEqual(FB.PINS[k], v)
        self.assertEqual(digest(FD / "fd/readout/fd_g_readout.json"), FB.PINS["g_readout"])


if __name__ == "__main__":
    unittest.main()
