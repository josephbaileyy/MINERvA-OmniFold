"""Controls for the 5B block's audit (FD-CT-5B-AUDIT-DECLARATION.md section 9), on synthetic trees built by the 5B and
readers' fixtures: S1's assembly with every block, C_resp, C_model's vertices, the 5A inputs and readout, 2D's draws,
and a 5B run directory whose periods readout is made by fd_ct_periods itself.

* Each stop clause decides in both directions: a planted case fires it and a case beside it does not.
* Each refusing control refuses on a one-entry defect, by its message, with nothing written.
* The identities of sections 3.1 and 6 are tested on planted inputs, and the written statistics are recomputed here by
  explicit loops.
* Nothing written carries f or an absolute cell value, and a planted leak is refused."""
import contextlib
import io
import json
import math
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
sys.path.insert(1, str(ND / "tests"))
import fd_ct_5b_audit as au  # noqa: E402
import fd_ct_periods as cp  # noqa: E402
import fd_ct_readers as ct  # noqa: E402
import s1_assemble as sa  # noqa: E402
import test_fd_ct_periods as TP  # noqa: E402
import test_fd_ct_readers as TR  # noqa: E402

digest = TR.digest
quiet = TP.quiet
E = {P: TP.E_RAW[P] / sum(TP.E_RAW.values()) for P in cp.PER}


class ATree:
    """A full synthetic audit input set. g_X is planted through r_X = 1 + c_X + pattern_X with sum_X e_X (c + pattern)
    = 0, so that m = 1 and g_X = r_X - 1 exactly."""

    def __init__(self, root: Path, seed=5, pattern=None, intercept=(0.0, -0.03, 0.05), noise=0.004, replica=None):
        self.root = root
        self.pt = TP.PTree(root, seed=seed)
        self.t = self.pt.t
        self.rng = np.random.default_rng(seed + 900)
        self.f = self.pt.f
        self.write_blocks()
        if pattern is None:
            pattern = {"PB": self.rng.normal(0, 0.01, 16), "PC": self.rng.normal(0, 0.012, 16)}
        c = dict(zip(cp.PER, intercept))
        g = {X: c[X] + pattern.get(X, 0.0) for X in ("PB", "PC")}
        g["PA"] = -(E["PB"] * g["PB"] + E["PC"] * g["PC"]) / E["PA"]
        self.g = g
        for X in cp.PER:
            self.pt.r[X] = 1.0 + g[X]
            self.pt.X[X] = self.pt.T[X] * self.pt.r[X]
            self.pt.d[X] = [self.rng.normal(0, noise, 16) for _ in cp.BOOT[X]] if replica is None else replica(X)
        self.write_5a()
        self.write_5b()

    # ------------------------------------------------------------ S1, C_resp and C_model with every block
    def write_blocks(self):
        t, rng, f = self.t, self.rng, self.f
        ff = np.outer(f, f)
        rel = {}
        for b in ["Flux", "2p2h", *sa.DETECTOR_BANDS, *[f"knob{i:02d}" for i in range(au.N_BANDS - 6)]]:
            if b == "Flux":
                # normalization-dominated, full rank, as S1's 100 weighted flux universes
                rel[f"band:{b}"] = np.cov(rng.normal(0, 0.01, (40, 16)), rowvar=False) + np.full((16, 16), 0.034 ** 2)
            elif b == "2p2h":
                V = rng.normal(0, 0.01, (2, 16))
                rel[f"band:{b}"] = V.T @ V
            else:
                v = rng.normal(0, 0.008, 16)
                rel[f"band:{b}"] = np.outer(v, v)
        for b in sa.LATERAL_BANDS:
            v = rng.normal(0, 0.01, 16)
            rel[f"lat:{b}"] = np.outer(v, v)
        rel["normalization"] = np.full((16, 16), 0.014 ** 2)
        rel["seed"] = np.zeros((16, 16))
        rel["stat"] = np.diag(rng.uniform(0.0015, 0.0035, 16) ** 2)
        self.rel = rel
        self.S = rng.normal(0, 0.02, (3, 16))
        t.Ce = sum(rel.values()) * ff
        t.Cma = (self.S.T @ self.S) * ff
        t.Ct = t.Ce + t.Cma
        t.write_common()
        names = sorted(rel)
        np.savez_compressed(t.s1, f=f, U=t.U.astype(np.float32), C_e=t.Ce, C_model_abs=t.Cma, C_total=t.Ct,
                            C_model_frac=self.S.T @ self.S, meta=json.dumps({"blocks": names}),
                            **{"C_" + b.replace(":", "_"): rel[b] * ff for b in names})
        t.pins["s1_npz"] = digest(t.s1)
        self.cmodel = self.root / "cmodel_5d.json"
        self.cmodel.write_text(json.dumps({"vertices": list(au.VERTICES), "S": self.S.tolist()}))

    # ------------------------------------------------------------ 5A: inputs, 2D draws, readout
    def write_5a(self):
        t, rng = self.t, self.rng
        t.write_period(e=tuple(E[X] for X in cp.PER))
        self.support = t.support
        n2 = self.support.size
        self.paths, self.store = {}, {}
        tt = {X: rng.uniform(0.5, 1.5, n2) for X in cp.PER}
        roles, runs = {}, {}
        d2 = {X: [rng.normal(0, 0.01, n2) for _ in range(10)] for X in cp.PER}
        s43 = {X: rng.normal(0, 0.003, n2) for X in cp.PER}
        for X in cp.PER:
            roles[X] = {"boot": []}
            for tag, rr in [("s42", t.r[X]), ("s43", t.r[X] * (1 + s43[X]))] + \
                           [(f"b{i + 1:02d}", t.r[X] * (1 + d2[X][i])) for i in range(10)]:
                p = self.root / "2d" / f"pu_{X}_{tag}" / "xsec.root"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(f"{X} {tag}".encode())
                self.store[str(p)] = {"x": rr * tt[X], "t": tt[X]}
                runs[str(p)] = {"sha256": digest(p)}
                if tag.startswith("b"):
                    roles[X]["boot"].append(str(p))
                else:
                    roles[X][tag] = str(p)
        self.analysis = self.root / "analysis.json"
        self.analysis.write_text(json.dumps({"_roles": roles, "_runs": runs}))
        # 2D's own noise share, computed here by its own route (playlist_term.py, DESIGN section 4)
        z = np.load(self.root / "s1" / "playlist_term.npz")
        V2 = sum(E[X] ** 2 for X in cp.PER)
        k = V2 / (1 - V2)
        Nb = np.zeros((n2, n2))
        for i in range(10):
            mm = sum(E[X] * d2[X][i] for X in cp.PER)
            for X in cp.PER:
                v = math.sqrt(k * E[X]) * z["x"] * (d2[X][i] - mm)
                Nb += np.outer(v, v) / 10
        self.share = float(np.median(np.diag(Nb) / np.diag(z["C_PL"])))
        self.d2, self.s43, self.k2 = d2, s43, k
        pj = self.root / "s1" / "playlist_term.json"
        pj.write_text(json.dumps({"npz": {"sha256": digest(self.root / "s1" / "playlist_term.npz")},
                                  "report": {"noise_share": {"boot": {"median_cell_variance_share": self.share}}}}))
        t.pins["playlist_json"] = digest(pj)
        with mock.patch.dict(ct.PINS, t.pins):
            rc, _, err = quiet(ct.main, t.argv_period)
        assert rc == 0, err
        self.readout_5a = t.out / "period.json"

    # ------------------------------------------------------------ 5B: run directory and periods readout
    def write_5b(self):
        pt = self.pt
        pt.write()
        pt.readout_5a = self.readout_5a
        self.p5a = mock.patch.object(cp, "READOUT_5A_SHA256", digest(self.readout_5a))
        with contextlib.ExitStack() as st:
            for p in [*pt.patches(), self.p5a]:
                st.enter_context(p)
            (pt.B / "control").mkdir(exist_ok=True)
            rc, _, err = quiet(cp.main, pt.control_argv())
            assert rc == 0, err
            pt.write_periods()
            rc, _, err = quiet(cp.main, pt.periods_argv())
            assert rc == 0, err
        self.readout_5b = self.root / "out" / "periods.json"

    def patches(self, readout_5b=None, analysis=None):
        return [*self.pt.patches(), mock.patch.object(cp, "READOUT_5A_SHA256", digest(self.readout_5a)),
                mock.patch.object(au, "READOUT_5B_SHA256", digest(readout_5b or self.readout_5b)),
                mock.patch.object(au, "CMODEL_JSON_SHA256", digest(self.cmodel)),
                mock.patch.object(au, "ANALYSIS_2D_SHA256", digest(analysis or self.analysis)),
                mock.patch.object(au, "load_2d", lambda p, cells: {k: v.copy() for k, v in self.store[p].items()})]

    def argv(self, out=None, readout_5b=None, analysis=None):
        t = self.t
        return ["--definition", str(TP.DEFINITION), "--s1-npz", str(t.s1), "--cresp", str(t.cresp),
                "--cmodel-json", str(self.cmodel), "--b5", str(self.pt.B),
                "--readout-5b", str(readout_5b or self.readout_5b), "--readout-5a", str(self.readout_5a),
                "--playlist-npz", str(self.root / "s1" / "playlist_term.npz"),
                "--playlist-json", str(self.root / "s1" / "playlist_term.json"),
                "--analysis-2d", str(analysis or self.analysis), "--central", str(self.root / "s1" / "data_b-_j-.npz"),
                "--out-json", str(out or self.root / "audit.json")]

    def run(self, extra=(), **kw):
        with contextlib.ExitStack() as st:
            for p in [*self.patches(kw.get("readout_5b"), kw.get("analysis")), *extra]:
                st.enter_context(p)
            rc, out, err = quiet(au.main, self.argv(**kw))
        self.stdout, self.stderr = out, err
        return rc

    def readout(self):
        return json.loads((self.root / "audit.json").read_text())


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ct5b-audit-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def tree(self, **kw):
        for p in list(self.tmp.iterdir()):
            shutil.rmtree(p) if p.is_dir() else p.unlink()
        (self.tmp / "out").mkdir()
        return ATree(self.tmp, **kw)


# ================================================================ algebra


class Algebra(unittest.TestCase):
    def test_a_period_common_factor_leaves_the_block_unchanged(self):
        rng = np.random.default_rng(1)
        r = {X: 1 + rng.normal(0, 0.03, 16) for X in cp.PER}
        eps = rng.normal(0, 0.05, 16)
        C0, g0 = au.p_block(r, E)
        C1, g1 = au.p_block({X: r[X] * (1 + eps) for X in cp.PER}, E)
        np.testing.assert_allclose(C1, C0, rtol=0, atol=1e-12 * np.abs(C0).max())
        for X in cp.PER:
            np.testing.assert_allclose(g1[X], g0[X], atol=1e-12)
        # a period-dependent factor is not cancelled
        C2, _ = au.p_block({X: r[X] * (1 + (X == "PC") * eps) for X in cp.PER}, E)
        self.assertGreater(np.abs(C2 - C0).max(), 1e-6)

    def test_ov_in_both_directions(self):
        rng = np.random.default_rng(2)
        V = rng.normal(size=(2, 16))
        P = V.T @ V
        self.assertAlmostEqual(au.ov(P, P)["OV"], 1.0, places=12)
        self.assertAlmostEqual(au.ov(P, 3 * P)["OV"], 1.0, places=12)
        Q, _ = np.linalg.qr(np.column_stack([V.T, rng.normal(size=(16, 3))]))
        w = Q[:, 2]                                    # orthogonal to P's plane
        self.assertLess(au.ov(P, np.outer(w, w))["OV"], 1e-12)
        # by hand: half of P's variance along its first mode only
        lam, U = np.linalg.eigh(P)
        u1 = U[:, -1]
        B = 0.5 * lam[-1] * np.outer(u1, u1)
        self.assertAlmostEqual(au.ov(P, B)["OV"], 0.5 * lam[-1] / lam.sum(), places=10)

    def test_identification_by_hand(self):
        rng = np.random.default_rng(3)
        d = rng.normal(0, 0.01, 16)
        sig = {X: rng.uniform(0.002, 0.006, 16) for X in cp.PER}
        g = {X: 0.02 + 1.5 * d + rng.normal(0, 0.003, 16) for X in cp.PER}
        out = au.identify(g, sig, [d])
        for X in cp.PER:
            w = 1 / sig[X] ** 2
            A = np.column_stack([np.ones(16), d])
            W = np.diag(w)
            coef = np.linalg.solve(A.T @ W @ A, A.T @ W @ g[X])
            c1 = float((g[X] - A @ coef) @ W @ (g[X] - A @ coef))
            c0m = float(w @ g[X] / w.sum())
            c0 = float(w @ (g[X] - c0m) ** 2)
            self.assertAlmostEqual(out[X]["E"], 1 - c1 / c0, places=10)
            self.assertAlmostEqual(out[X]["a"][0], coef[1], places=10)

    def test_o_fires_and_stays_silent(self):
        rng = np.random.default_rng(4)
        d = rng.normal(0, 0.01, 16)
        sig = {X: np.full(16, 0.002) for X in cp.PER}
        base = {X: rng.normal(0, 0.0005, 16) for X in cp.PER}
        at = lambda a: {X: 0.03 + a * d + base[X] for X in cp.PER}  # noqa: E731
        self.assertTrue(au.fires_o(au.identify(at(1.5), sig, [d])))
        self.assertTrue(au.fires_o(au.identify(at(-1.9), sig, [d])))
        self.assertFalse(au.fires_o(au.identify(at(2.1), sig, [d])), "the amplitude bound")
        orth = rng.normal(0, 0.01, 16)
        self.assertFalse(au.fires_o(au.identify({X: 0.03 + orth for X in cp.PER}, sig, [d])))
        # one period explained is not enough
        g = at(1.5)
        g["PC"] = 0.03 + orth
        self.assertFalse(au.fires_o(au.identify(g, sig, [d])))

    def test_the_clauses_at_their_thresholds(self):
        row = lambda e_, a_: {"E": e_, "a": [a_]}  # noqa: E731
        self.assertTrue(au.fires_o({"PA": row(0, 9), "PB": row(0.5, 2.0), "PC": row(0.5, -2.0)}))
        self.assertFalse(au.fires_o({"PA": row(1, 0), "PB": row(0.4999, 1.0), "PC": row(0.9, 1.0)}))
        self.assertFalse(au.fires_o({"PA": row(1, 0), "PB": row(0.9, 1.0), "PC": row(0.9, -2.001)}))
        self.assertFalse(au.fires_o({"PA": row(1, 0), "PB": row(0.9, 2.001), "PC": row(0.9, 1.0)}))
        self.assertEqual(au.decide([], 0.5, 0.5)["which"], [])
        self.assertEqual(au.decide([], 0.5001, 0.5)["which"], ["N"])
        self.assertEqual(au.decide([], 0.1, 0.4999)["which"], ["R"])
        d = au.decide(["band:x#1"], 0.1, 0.9)
        self.assertEqual((d["which"], d["stop"]), (["O"], True))
        self.assertFalse(au.decide([], 0.1, 0.9)["stop"])
        self.assertEqual(au.decide(["a"], 0.6, 0.1)["which"], ["O", "N", "R"])

    def test_a_uniform_candidate_has_no_shape(self):
        w = np.random.default_rng(5).uniform(1, 3, 16)
        self.assertLess(au.shape_norm_ratio(np.full(16, 0.014), w), au.UNIFORM_REL)
        self.assertGreater(au.shape_norm_ratio(np.arange(16.0), w), 0.1)

    def test_the_chi2_bound_is_attained_along_the_top_mode(self):
        rng = np.random.default_rng(6)
        A = rng.normal(size=(30, 16))
        M = np.cov(A, rowvar=False) + np.eye(16)
        V = rng.normal(size=(2, 16)) * 0.7
        P = V.T @ V
        lt = au.whitened_eigs(P, M)
        L = np.linalg.cholesky(M)
        Pt = np.linalg.solve(L, np.linalg.solve(L, P).T).T
        lam, W = np.linalg.eigh(Pt)
        v = L @ W[:, -1]
        c0 = float(v @ np.linalg.solve(M, v))
        c1 = float(v @ np.linalg.solve(M + P, v))
        self.assertAlmostEqual(1 - c1 / c0, lt[0] / (1 + lt[0]), places=10)
        for _ in range(20):
            v = rng.normal(size=16)
            c0, c1 = float(v @ np.linalg.solve(M, v)), float(v @ np.linalg.solve(M + P, v))
            self.assertLessEqual(1 - c1 / c0, lt[0] / (1 + lt[0]) + 1e-12)

    def test_nu_eff_and_the_interval(self):
        e = {"PA": 0.5334, "PB": 0.2945, "PC": 0.1721}
        V2 = sum(v * v for v in e.values())
        s3 = sum(v ** 3 for v in e.values())
        self.assertAlmostEqual(au.nu_eff(e), (1 - V2) ** 2 / (V2 - 2 * s3 + V2 ** 2), places=12)
        self.assertAlmostEqual(au.nu_eff({X: 1 / 3 for X in cp.PER}), 2.0, places=12)
        lo, hi = au.sigma_interval(au.nu_eff(e))
        self.assertLess(lo, 1.0)
        self.assertGreater(hi, 2.0)
        self.assertAlmostEqual(au.chi2_q95(15), 24.99579013972862, places=8)

    def test_the_beta_tail_by_integration(self):
        # P(Beta(1/2, 7) >= 1/2) = int_0^{1/2} (1 - y)^(-1/2) y^6 dy / B(1/2, 7), with y = 1 - x
        y = np.linspace(0, 0.5, 200001)
        num = np.trapz((1 - y) ** -0.5 * y ** 6, y)
        B = math.gamma(0.5) * math.gamma(7) / math.gamma(7.5)
        self.assertAlmostEqual(num / B, au.BETA_TAIL, places=9)

    def test_rank_two_span(self):
        rng = np.random.default_rng(7)
        r = {X: 1 + rng.normal(0, 0.03, 16) for X in cp.PER}
        C, g = au.p_block(r, E)
        Q = au.basis(C)
        self.assertEqual(Q.shape[1], 2)
        for X in cp.PER:
            self.assertLess(au.outside_share(Q, g[X]), 1e-20)


class RootLoader(unittest.TestCase):
    """load_2d on a synthetic ROOT file, against the formula by hand (cluster only: needs ROOT)."""

    def setUp(self):
        try:
            import ROOT  # noqa: F401
        except Exception:
            self.skipTest("ROOT not importable")
        self.tmp = Path(tempfile.mkdtemp(prefix="ct5b-root-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def write(self, path, pz=ct.PZ_2D):
        import ROOT
        from array import array
        rng = np.random.default_rng(8)
        pt_e, pz_e = array("d", ct.PT_2D), array("d", pz)
        f = ROOT.TFile(str(path), "RECREATE")
        vals = {}
        for nm in ("hXSec2D", "hTruth2D", "hOFCompleteness2D"):
            h = ROOT.TH2D(nm, nm, len(pt_e) - 1, pt_e, len(pz_e) - 1, pz_e)
            v = rng.uniform(0.5, 1.5, (14, 16))
            v[0, 0] = 0.0 if nm == "hOFCompleteness2D" else v[0, 0]
            for i in range(14):
                for j in range(16):
                    h.SetBinContent(i + 1, j + 1, float(v[i, j]))
            h.Write()
            vals[nm] = v
        hf = ROOT.TH1D("hFlux_pt", "", 14, pt_e)
        phi = rng.uniform(1, 2, 14)
        for i in range(14):
            hf.SetBinContent(i + 1, float(phi[i]))
        hf.Write()
        ROOT.TParameter("double")("dataPOT", 1.1e21).Write()
        ROOT.TParameter("double")("nNucleons", 3.2e30).Write()
        f.Close()
        return vals, phi

    def test_x_and_t_by_the_formula(self):
        p = self.tmp / "xsec.root"
        v, phi = self.write(p)
        cells = np.array([c for c in range(14 * 16) if c not in TR.UNSUPPORTED])
        out = au.load_2d(str(p), cells)
        dpt, dpz = np.diff(ct.PT_2D), np.diff(ct.PZ_2D)
        c = v["hOFCompleteness2D"]
        denom = c * phi[:, None] * 3.2e30 * 1.1e21 * dpt[:, None] * dpz[None, :]
        with np.errstate(divide="ignore", invalid="ignore"):
            t = np.where(c > 0, v["hTruth2D"] / denom * 1e4, 0.0)
        np.testing.assert_allclose(out["x"], v["hXSec2D"].ravel()[cells], rtol=1e-15)
        np.testing.assert_allclose(out["t"], t.ravel()[cells], rtol=1e-12)

    def test_refuses_another_grid(self):
        p = self.tmp / "xsec.root"
        self.write(p, pz=tuple(np.asarray(ct.PZ_2D) * 1.01))
        with self.assertRaises(au.f0.Stop):
            au.load_2d(str(p), np.arange(10))


# ================================================================ the reader end to end


class Audit(Base):
    def test_runs_and_is_recomputed_by_hand(self):
        t = self.tree()
        self.assertEqual(t.run(), 0, t.stderr)
        o = t.readout()
        self.assertEqual(o["schema"], "fd-ct-5b-audit/1")
        P = np.asarray(json.loads(t.readout_5b.read_text())["C_PL5D"]["C_PL5D_rel"])
        # replica blocks and N's statistic, by loops
        meds = []
        for k in range(10):
            r = {X: t.pt.r[X] * (1 + t.pt.d[X][k]) for X in cp.PER}
            m = sum(E[X] * r[X] for X in cp.PER)
            V2 = sum(v * v for v in E.values())
            Ck = np.zeros((16, 16))
            for X in cp.PER:
                gg = r[X] / m - 1
                Ck += V2 / (1 - V2) * E[X] * np.outer(gg, gg)
            meds.append(np.median(np.sqrt(np.diag(Ck))))
            Q = au.basis(P)
            self.assertAlmostEqual(o["item4_rank_two"]["plane_retention"][k],
                                   float(np.trace(Q @ Q.T @ Ck) / np.trace(Ck)), places=8)
        s_med = np.std(meds, ddof=1) / np.median(np.sqrt(np.diag(P)))
        self.assertAlmostEqual(o["item2_stability"]["s_med"], s_med, places=8)
        sc = o["stop_condition"]
        self.assertEqual(sc["stop"], sc["O"] or sc["N"] or sc["R"])
        self.assertFalse(sc["stop"], sc)
        self.assertEqual(o["item4_rank_two"]["rank"], 2)
        self.assertIn("[5B audit] O False", t.stdout)
        # 5A's noise from 2D's draws, by loops: sigma^2 = mean_k (om h_k)^2 + (om h_s)^2 / 2
        om = ct.footprint(t.t.U, t.t.fm, t.t.xc, t.support)[0]
        for X in cp.PER:
            hb = [t.d2[X][i] - sum(E[Y] * t.d2[Y][i] for Y in cp.PER) for i in range(10)]
            hs = t.s43[X] - sum(E[Y] * t.s43[Y] for Y in cp.PER)
            want = np.sqrt(np.mean([(om @ h) ** 2 for h in hb], axis=0) + (om @ hs) ** 2 / 2)
            np.testing.assert_allclose(o["item3_5a_vs_5b"]["periods"][X]["sigma_5A"], want, rtol=1e-6)
        # OV for every group is in [0, 1], and the whole matrix covers P's modes (P is smaller than M)
        for G, v in o["item1_overlap"]["OV"].items():
            self.assertGreaterEqual(v["OV"], 0)
            self.assertLessEqual(v["OV"], 1 + 1e-12)
        idf = o["item1_overlap"]["identification"]
        self.assertGreater(idf["n_candidates"], 40)
        self.assertIn("normalization#1", idf["uniform_excluded"])
        names = {r_["candidate"] for r_ in idf["candidates"]}
        self.assertTrue({"band:Flux#2", "band:2p2h#2", "C_model:nuwro#1", "C_resp:em#1"} <= names)
        self.assertFalse([n for n in names if n.endswith("#4")])
        # the 1% cut, by hand on the flux block: every mode at or above it is a candidate, up to three
        lam = np.sort(np.linalg.eigvalsh(t.rel["band:Flux"]))[::-1]
        want = min(3, int(np.sum(lam >= 0.01 * lam.sum())))
        self.assertEqual(len([n for n in names if n.startswith("band:Flux#")]), want)
        self.assertFalse([n for n in names if n.startswith(("stat", "seed"))])
        self.assertAlmostEqual(idf["look_elsewhere"]["if_PB_PC_patterns_identical"], idf["n_candidates"] * au.BETA_TAIL)
        k = sum(v * v for v in E.values()) / (1 - sum(v * v for v in E.values()))
        self.assertAlmostEqual(o["item1_overlap"]["noise_vs_stat"]["expected_under_poisson_sqrt_2k"], math.sqrt(2 * k))
        # 5A against 5B: the uniform share and the E_avail contrast, by hand
        i3 = o["item3_5a_vs_5b"]
        u = np.full(16, 1 / 4)
        self.assertAlmostEqual(i3["uniform_share"]["5B"], float(u @ P @ u / np.trace(P)), places=10)
        g5b = {X: np.asarray(json.loads(t.readout_5b.read_text())["g_vs_5A"]["periods"][X]["g_5b"]) for X in cp.PER}
        g5a = {X: np.asarray(json.loads(t.readout_5a.read_text())["variants"]["central"]["g"][X]) for X in cp.PER}
        dl = g5b["PC"] - g5a["PC"]
        self.assertAlmostEqual(i3["periods"]["PC"]["ea_contrast"]["pz_lo"]["low_minus_high"],
                               dl[[0, 8]].mean() - dl[[2, 3, 10, 11]].mean(), places=12)
        self.assertAlmostEqual(i3["periods"]["PB"]["ea_contrast"]["pz_hi"]["low_minus_high"],
                               (g5b["PB"] - g5a["PB"])[[4, 12]].mean() - (g5b["PB"] - g5a["PB"])[[6, 7, 15]].mean(),
                               places=12)
        # the debiased block: P - floor, its negative eigenvalues zeroed
        Cn = np.zeros((16, 16))
        for kk in range(10):
            h = {X: t.pt.d[X][kk] - sum(E[Y] * t.pt.d[Y][kk] for Y in cp.PER) for X in cp.PER}
            Cn += k * sum(E[X] * np.outer(h[X], h[X]) for X in cp.PER) / 10
        lam, V = np.linalg.eigh(P - Cn)
        Pd = (V * np.clip(lam, 0, None)) @ V.T
        np.testing.assert_allclose(o["item2_stability"]["debiased"]["sigma_over_P_sigma"],
                                   np.sqrt(np.diag(Pd)) / np.sqrt(np.diag(P)), rtol=1e-6)

    def test_o_fires_on_a_planted_detector_pattern(self):
        probe = self.tree()
        lam, v = au.modes(probe.rel["band:GEANT_Pion"], 1)[0]
        d = math.sqrt(lam) * v
        t = self.tree(pattern={"PB": 1.5 * d, "PC": -1.2 * d})
        self.assertEqual(t.run(), 0, t.stderr)
        sc = t.readout()["stop_condition"]
        self.assertTrue(sc["O"], t.readout()["item1_overlap"]["identification"]["best_per_group"].get("detector"))
        self.assertIn("band:GEANT_Pion#1", sc["O_decided_by"])
        self.assertTrue(sc["stop"])

    def test_o_stays_silent_beyond_the_amplitude_bound(self):
        probe = self.tree()
        lam, v = au.modes(probe.rel["band:GEANT_Pion"], 1)[0]
        d = math.sqrt(lam) * v
        t = self.tree(pattern={"PB": 2.6 * d, "PC": -2.4 * d})
        self.assertEqual(t.run(), 0, t.stderr)
        self.assertNotIn("band:GEANT_Pion#1", t.readout()["stop_condition"]["O_decided_by"])

    def test_n_is_silent_when_the_noise_is_as_large_as_the_offsets(self):
        # a property of the frozen clause, recorded for the director: replica noise of 5% per cell, the size of the
        # planted offsets, inflates every replica block alike, so the SD of their median sigma stays below half of it
        t = self.tree(noise=0.05)
        self.assertEqual(t.run(), 0, t.stderr)
        sc = t.readout()["stop_condition"]
        self.assertFalse(sc["N"], sc)
        self.assertGreater(sc["N_statistic"], 0.2)

    def test_n_fires_when_the_replica_blocks_size_is_unstable(self):
        rng = np.random.default_rng(12)
        amp = [0.0, 0.3] * 5            # half the replicas carry no noise, half a noise far above the offsets
        t = self.tree(replica=lambda X: [rng.normal(0, a, 16) for a in amp])
        self.assertEqual(t.run(), 0, t.stderr)
        sc = t.readout()["stop_condition"]
        self.assertTrue(sc["N"], sc)
        self.assertGreater(sc["N_statistic"], 0.5)

    def test_r_fires_alone_on_a_rotated_plane(self):
        probe = self.tree()
        rng = np.random.default_rng(11)
        # replicas whose offsets carry a large pattern orthogonal to the observed plane, the same in every replica:
        # the replica blocks' size is stable (N silent) but their plane is not the observed one (R fires)
        gB, gC = probe.g["PB"], probe.g["PC"]
        Q, _ = np.linalg.qr(np.column_stack([gB, gC, rng.normal(size=(16, 2))]))
        q1, q2 = 0.3 * Q[:, 2], 0.3 * Q[:, 3]
        fixed = {"PB": q1, "PC": q2}
        fixed["PA"] = -(E["PB"] * q1 + E["PC"] * q2) / E["PA"]
        t = self.tree(replica=lambda X: [fixed[X] + rng.normal(0, 1e-4, 16) for _ in range(10)])
        self.assertEqual(t.run(), 0, t.stderr)
        sc = t.readout()["stop_condition"]
        self.assertTrue(sc["R"], sc)
        self.assertLess(sc["R_statistic"], 0.5)

    def test_n_and_r_stay_silent_on_small_noise(self):
        t = self.tree(noise=0.0005)
        self.assertEqual(t.run(), 0, t.stderr)
        sc = t.readout()["stop_condition"]
        self.assertFalse(sc["N"] or sc["R"], sc)
        self.assertGreater(sc["R_statistic"], 0.95)

    def test_a_planted_leak_is_refused(self):
        t = self.tree()
        real = au.item3

        def leaky(*a, **k):
            o = real(*a, **k)
            o["leak"] = t.pt.X["PB"].tolist()     # a 5B period unfold's absolute cell integrals
            return o

        self.assertEqual(t.run([mock.patch.object(au, "item3", leaky)]), 3, t.stderr)
        self.assertFalse((t.root / "audit.json").exists())

    def test_refuses_an_existing_output(self):
        t = self.tree()
        (t.root / "audit.json").write_text("{}")
        self.assertEqual(t.run(), 1)
        self.assertIn("refusing to overwrite", t.stderr)


class Refusals(Base):
    def assertRefuses(self, t, msg, extra=(), **kw):
        self.assertEqual(t.run(extra, **kw), 1, t.stderr)
        self.assertIn(msg, t.stderr)
        self.assertFalse((t.root / "audit.json").exists())

    def test_a_5b_readout_at_another_digest(self):
        t = self.tree()
        self.assertRefuses(t, "5B readout", [mock.patch.object(au, "READOUT_5B_SHA256", "0" * 64)])

    def test_a_tampered_committed_block(self):
        t = self.tree()
        ro = json.loads(t.readout_5b.read_text())
        ro["C_PL5D"]["C_PL5D_rel"][3][3] *= 1 + 1e-9
        bad = t.root / "tampered.json"
        bad.write_text(json.dumps(ro))
        self.assertRefuses(t, "C_PL,5D rebuilt from the unfolds equals the committed one", readout_5b=bad)

    def test_a_tampered_noise_sigma(self):
        t = self.tree()
        ro = json.loads(t.readout_5b.read_text())
        ro["g_vs_5A"]["periods"]["PC"]["g_5b_noise_sigma"][5] *= 1 + 1e-9
        bad = t.root / "tampered.json"
        bad.write_text(json.dumps(ro))
        self.assertRefuses(t, "g_X and its noise sigma", readout_5b=bad)

    def test_an_extra_replica(self):
        t = self.tree()
        shutil.copy(cp.unf_path(t.pt.B, "PB", 2001), t.pt.B / "unf" / "PB" / "5b_PB_b2011_j-.npz")
        self.assertRefuses(t, "PB: the unfold directory holds")

    def test_a_replaced_unfold(self):
        t = self.tree()
        p = cp.unf_path(t.pt.B, "PC", 3004)
        z = dict(np.load(p, allow_pickle=True))
        z["xsec_flat"] = z["xsec_flat"] * (1 + 1e-6)
        np.savez(p, **z)
        self.assertRefuses(t, "PC b3004: the unfold is not the one the 5B readout read")

    def test_another_band_count(self):
        t = self.tree()
        self.assertRefuses(t, "bands", [mock.patch.object(au, "N_BANDS", 37)])

    def test_blocks_that_do_not_sum_to_c_e(self):
        # load_blocks directly: a rewritten assembly has another digest, which A0 refuses first
        t = self.tree()
        z = dict(np.load(t.t.s1, allow_pickle=False))
        z["C_band_knob03"] = z["C_band_knob03"] * 1.001
        np.savez_compressed(t.t.s1, **z)
        a = au.build_args(t.argv())
        U = sa.functional_matrix(sa.fine_map(TP.DEFINITION))
        with mock.patch.dict(ct.PINS, {**t.t.pins, "s1_npz": digest(t.t.s1)}), \
                mock.patch.object(au, "CMODEL_JSON_SHA256", digest(t.cmodel)):
            rc, out, err = quiet(lambda: au.load_blocks(a, ct.common(a, U)))
        self.assertEqual(rc, "FAIL control A2: C_e is the sum of S1's blocks: differs")

    def test_another_cmodel(self):
        t = self.tree()
        cj = json.loads(t.cmodel.read_text())
        cj["S"][1][4] *= 1.01
        t.cmodel.write_text(json.dumps(cj))
        self.assertRefuses(t, "S^T S is C_model_frac")

    def test_a_2d_draw_not_at_its_digest(self):
        t = self.tree()
        A = json.loads(t.analysis.read_text())
        p = A["_roles"]["PB"]["boot"][3]
        A["_runs"][p]["sha256"] = "0" * 64
        bad = t.root / "analysis-bad.json"
        bad.write_text(json.dumps(A))
        self.assertRefuses(t, "not at its analysis.json digest", analysis=bad)

    def test_a_2d_seed42_r_that_is_not_the_npz(self):
        t = self.tree()
        p = json.loads(t.analysis.read_text())["_roles"]["PA"]["s42"]
        t.store[p]["x"] = t.store[p]["x"] * (1 + 1e-9)
        self.assertRefuses(t, "2D's seed-42 r = x / t equals")

    def test_the_2d_noise_share_not_reproduced(self):
        t = self.tree()
        p = json.loads(t.analysis.read_text())["_roles"]["PC"]["boot"][0]
        t.store[p]["x"] = t.store[p]["x"] * (1 + 0.05)
        self.assertRefuses(t, "2D's committed bootstrap noise share")

    def test_a_5a_projection_that_does_not_reproduce_the_committed_g(self):
        t = self.tree()
        real = ct.footprint
        self.assertRefuses(t, "5A's g, reprojected", [mock.patch.object(
            ct, "footprint", lambda *a, **k: (real(*a, **k)[0] * 1.001, *real(*a, **k)[1:]))])

    def test_another_ea_cell_set(self):
        t = self.tree()
        self.assertRefuses(t, "E_avail cell sets", [mock.patch.object(au, "EA_LOW", (0, 4, 8))])


if __name__ == "__main__":
    unittest.main()
