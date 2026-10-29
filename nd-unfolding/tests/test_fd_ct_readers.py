"""Controls for fd_ct_readers (FD-CT-READERS-DECLARATION.md section 3), on a synthetic tree of every input the three
readers read and on the committed H2 definition. No real product, covariance or data value is read.

* Each reader's readout is recomputed here by an independent route: explicit loops over fine cells for 5A's
  footprints, plain numpy for 3a's shifts and 4C's chi2 and percentiles.
* Each refusing control refuses on a one-entry defect, by its message, with nothing written.
* Nothing written carries f or an absolute cell value (the tool's guard, and a planted leak is refused).
* The module runs as declared (-I -B, cwd outside nd-unfolding), and the real pins refuse the synthetic tree."""
import contextlib
import copy
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
import fd_ct_readers as ct  # noqa: E402
import fd_f0_regrade as F  # noqa: E402
import s1_assemble as sa  # noqa: E402

REPO = ND.parent
DEFINITION = ND / "pv-ladder/readouts/h2_definition.json"
STATE = REPO / "docs/orchestration/state"
N = F.N_FINE
N_CAL = 40
# 19 2D cells outside the term's support, laid out as the measured binning's (FD-CT-READERS-DECLARATION.md section 1)
UNSUPPORTED = (144, 160, 161, 176, 177, 178, 192, 193, 194, 195, 196, 208, 209, 210, 211, 212, 213, 214, 215)

try:
    from scipy.stats import chi2 as _chi2
except ImportError:  # pragma: no cover
    _chi2 = None


def digest(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def fake(*k) -> str:
    return hashlib.sha256("/".join(k).encode()).hexdigest()


EST = [{"n_estimators": 100, "num_leaves": 8, "random_state": 42, "bin_construct_sample_cnt": F.ALL_ROWS,
        "deterministic": True, "force_row_wise": True, "subsample": 1.0, "colsample_bytree": 1.0}] * 3
REF = {"ran": True, "classifier_params": {"n_estimators": 400, "num_leaves": 31, "random_state": 45,
                                          "bin_construct_sample_cnt": F.ALL_ROWS, "deterministic": True}}


def data_meta(npz, bkg, **extra):
    m = {"schema": "s5p-numerics/1", "config": "R", "capacity": None, "iters": 5, "estimator_seed": 42,
         "estimator_params": copy.deepcopy(EST), "refinement": copy.deepcopy(REF), "construction": "data",
         "truth": "nominal", "bootstrap_seed": None, "jitter_seed": None, "coords": "float32",
         "input_npz_sha256": npz, "bkg_dump_sha256": bkg}
    m.update(extra)
    return m


def cal_meta(hyp, seed, flux):
    m = {"iters": 5, "estimator_params": copy.deepcopy(EST), "refinement": copy.deepcopy(REF),
         "code_sha256": {"candidate": "R", "candidate_refine_override": {"n_estimators": 400, "num_leaves": 31},
                         "s5p_nullexp.py": F.NULLEXP_PROD[0]},
         "input_npz_sha256": F.INPUT_NPZ_SHA256, "bkg_dump_sha256": F.BKG_SHA256,
         "schema": "s5p-null-experiment/1", "config": "R", "capacity": None, "hypothesis": {"sha256": hyp},
         "alternative": None, "pseudo_seed": seed, "development": {"expectation": False, "mc_fraction": "half"},
         "nuisance_draw": {"flux": flux, "model": {}, "detector": {}}}
    return m


class Tree:
    """Every input of the three readers, built from known cell integrals."""

    def __init__(self, root: Path, seed=0, scale=1e-39):
        self.root, self.scale = root, scale
        self.rng = rng = np.random.default_rng(seed)
        self.fm = sa.fine_map(DEFINITION)
        self.U = sa.functional_matrix(self.fm)
        self.volc = self.U.sum(axis=1)
        # the (e) central value at fine level; f = U @ x_central
        self.xc = np.where(self.fm >= 0, rng.uniform(0.5, 1.5, N), 0.3) * scale
        self.f = self.U @ self.xc
        ff = np.outer(self.f, self.f)
        A = rng.normal(size=(40, 16))
        self.Ce = (0.004 ** 2 * (np.cov(A, rowvar=False) + np.eye(16)) + np.outer(*(2 * [rng.normal(0, 0.04, 16)]))
                   + np.full((16, 16), 0.014 ** 2)) * ff
        self.Ce = (self.Ce + self.Ce.T) / 2
        S = rng.normal(0, 0.02, (3, 16))
        self.Cma = (S.T @ S) * ff
        self.Ct = self.Ce + self.Cma
        self.species = {p: np.outer(v, v) for p, v in zip(ct.PRIMARY, rng.normal(0, 0.015, (4, 16)) * self.f)}
        self.Cr = sum(self.species.values())
        self.xtalk = np.outer(*(2 * [rng.normal(0, 0.01, 16) * self.f]))

    def cellwise(self, X, filler=0.4):
        """A fine array whose cell integrals are exactly X."""
        return np.where(self.fm >= 0, (X / self.volc)[np.clip(self.fm, 0, None)], filler * self.scale)

    # ---------------------------------------------------------------- shared records
    def write_common(self, Cr_override=None, Ctr_override=None, f_override=None):
        R = self.root
        R.mkdir(parents=True, exist_ok=True)
        self.s1 = R / "s1_assembly.npz"
        self.s1.unlink(missing_ok=True)
        np.savez_compressed(self.s1, f=self.f if f_override is None else f_override, U=self.U.astype(np.float32),
                            C_e=self.Ce, C_model_abs=self.Cma, C_total=self.Ct)
        self.cresp = R / "cresp.npz"
        self.cresp.unlink(missing_ok=True)
        Cr = self.Cr if Cr_override is None else Cr_override
        np.savez_compressed(self.cresp, C_resp=Cr, C_total_resp=self.Ct + Cr if Ctr_override is None else Ctr_override,
                            **{f"C_resp_{p}": v for p, v in self.species.items()}, C_resp_xtalk=self.xtalk)
        self.pins = {**ct.PINS, "s1_npz": digest(self.s1), "cresp": digest(self.cresp)}
        self.out = R / "out"
        self.out.mkdir(exist_ok=True)
        return self

    def common_argv(self, name):
        return ["--definition", str(DEFINITION), "--s1-npz", str(self.s1), "--cresp", str(self.cresp),
                "--out-json", str(self.out / f"{name}.json")]

    # ---------------------------------------------------------------- 3a
    def write_recoil(self, positive=True, meta_extra=None):
        d = self.root / "w2b/unf"
        d.mkdir(parents=True, exist_ok=True)
        rng = self.rng
        self.Z = self.f * (1 + rng.normal(0, 0.01, 16))
        self.sm, self.sp = rng.normal(-0.03, 0.01, 16), rng.normal(0.03, 0.01, 16)
        self.X = {"rrzero": self.Z, "rr0": self.Z * (1 + self.sm), "rr1": self.Z * (1 + self.sp)}
        if not positive:
            self.X["rr1"] = self.X["rr1"].copy()
            self.X["rr1"][3] = -abs(self.X["rr1"][3])
        self.w2b = {}
        for v, X in self.X.items():
            p = d / f"w2b_{v}_b-_j-.npz"
            m = data_meta(fake(v, "npz"), fake(v, "bkg"), **((meta_extra or {}).get(v, {})))
            np.savez_compressed(p, xsec_flat=self.cellwise(X), shape=np.array(sa.s1.fine_shape()), meta=json.dumps(m))
            self.w2b[v] = (digest(p), fake(v, "npz"), fake(v, "bkg"), ct.W2B[v][3])
        self.argv_recoil = ["recoil", *self.common_argv("recoil"), "--w2b-unf", str(d)]
        return self

    # ---------------------------------------------------------------- 4C
    def write_chi2(self):
        R, rng = self.root, self.rng
        self.s5p = R / "s5p"
        self.weights = rng.uniform(0.3, 2.0, 100)
        delta = rng.normal(0, 0.03, (100, 16))
        self.cal = {}
        for name, cal, hyp in ct.CAL:
            d = self.s5p / "runs/prod/cal" / cal
            d.mkdir(parents=True, exist_ok=True)
            b = rng.normal(0, 0.01, 16)
            T = self.f * rng.uniform(0.9, 1.1, 16)
            items = []
            for s in range(1200000, 1200000 + N_CAL):
                u = int(rng.integers(0, 100))
                Xt = T * (1 + rng.normal(0, 1e-3, 16))
                r = b + delta[u] + rng.normal(0, 0.006, 16)
                p = d / f"cal_{cal}_s{s}.npz"
                np.savez_compressed(p, xsec_flat=self.cellwise(Xt * (1 + r)), xtrue_flat=self.cellwise(Xt),
                                    meta=json.dumps(cal_meta(hyp, s, u)))
                items.append((p, u))
            self.cal[name] = items
        self.write_chi2_records()
        return self

    def write_chi2_records(self, beff_scale=1.0):
        R = self.root
        sums = R / "SHA256SUMS.txt"
        sums.write_text("".join(f"{digest(p)}  {p.relative_to(self.s5p)}\n" for items in self.cal.values() for p, _ in items))
        con = R / "constraint.txt"
        con.write_text("".join(f"Flux {i} {w!r}\n" for i, w in enumerate(self.weights)) + "Other 0 1.0\n")
        beff = {}
        for name, items in self.cal.items():
            w = self.weights[[u for _, u in items]]
            beff[name] = float(w.sum() ** 2 / (w ** 2).sum()) * beff_scale
        f0b = R / "fd_f0b_readout.json"
        f0b.write_text(json.dumps({"controls": {"offset_control_7": {"B_eff_calibration": beff}}}))
        self.constraint_sha = digest(con)
        self.pins.update(s5p_sums=digest(sums), f0b_readout=digest(f0b))
        self.argv_chi2 = ["chi2", *self.common_argv("chi2"), "--s5p-sums", str(sums), "--s5p-root", str(self.s5p),
                          "--f0b-readout", str(f0b), "--flux-constraint", str(con)]

    def chi2_patches(self):
        return [mock.patch.dict(F.COUNTS, {"cal": {c: N_CAL for _, c, _ in ct.CAL}}),
                mock.patch.object(sa, "CONSTRAINT_SHA256", self.constraint_sha)]

    # ---------------------------------------------------------------- 5A
    def write_period(self, e=(0.53, 0.30, 0.17), gsum_defect=0.0, cpl_defect=0.0, e_ripple=0.0, json_npz=None,
                     central_scale=1.0, prior_schema="s5p-mc-truth-pred/1"):
        R, rng = self.root, self.rng
        self.support = np.array([c for c in range(14 * 16) if c not in UNSUPPORTED])
        n2 = self.support.size
        self.e = dict(zip(ct.PERIODS, e))
        gA, gB = rng.normal(0, 0.02, n2), rng.normal(0, 0.03, n2)
        gC = -(self.e["PA"] * gA + self.e["PB"] * gB) / self.e["PC"]
        self.g = {"PA": gA, "PB": gB, "PC": gC + gsum_defect * (np.arange(n2) == 5)}
        m = rng.uniform(0.8, 1.2, n2)
        self.r = {X: (1 + self.g[X]) * m for X in ct.PERIODS}
        x = rng.uniform(1, 2, n2) * self.scale
        V2 = sum(v * v for v in self.e.values())
        self.k = V2 / (1 - V2)
        C_PL = self.k * sum(self.e[X] * np.outer(x * self.g[X], x * self.g[X]) for X in ct.PERIODS)
        C_PL = C_PL * (1 + cpl_defect * (np.arange(n2)[:, None] == 0))
        ev = {X: np.full(n2, self.e[X]) for X in ct.PERIODS}
        ev["PA"] = ev["PA"] * (1 + e_ripple * (np.arange(n2) == 2))
        npz = R / "playlist_term.npz"
        npz.unlink(missing_ok=True)
        np.savez(npz, C_PL=C_PL, cells=self.support, x=x, **{f"g_{X}": self.g[X] for X in ct.PERIODS},
                 **{f"e_{X}": ev[X] for X in ct.PERIODS}, **{f"r_{X}": self.r[X] for X in ct.PERIODS})
        pj = R / "playlist_term.json"
        pj.write_text(json.dumps({"npz": {"sha256": json_npz or digest(npz)}}))
        central = R / "data_b-_j-.npz"
        np.savez_compressed(central, xsec_flat=self.xc * central_scale, shape=np.array(sa.s1.fine_shape()),
                            meta=json.dumps(data_meta(sa.INPUT_NPZ_SHA256, sa.BKG_SHA256)))
        self.xp = np.where(self.fm >= 0, rng.uniform(0.2, 2.0, N), 0.1) * self.scale
        prior = R / "mnvtune_v1_xsec5d.npz"
        np.savez(prior, xsec_flat=self.xp, meta_json=json.dumps({"schema": prior_schema}),
                 **{f"edges_{a}": np.asarray(sa.s1.FINE[a]) for a in sa.s1.AXES})
        self.pins.update(playlist_npz=digest(npz), playlist_json=digest(pj), central=digest(central), prior=digest(prior))
        self.argv_period = ["period", *self.common_argv("period"), "--playlist-npz", str(npz), "--playlist-json", str(pj),
                            "--central", str(central), "--prior", str(prior)]
        return self


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd-ct-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def tree(self, **kw):
        return Tree(self.tmp / "tree", **kw).write_common()

    def run_tool(self, t, argv, extra=()):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.ExitStack() as st:
            st.enter_context(mock.patch.dict(ct.PINS, t.pins))
            st.enter_context(mock.patch.dict(ct.W2B, getattr(t, "w2b", ct.W2B)))
            for p in extra:
                st.enter_context(p)
            st.enter_context(contextlib.redirect_stdout(out))
            st.enter_context(contextlib.redirect_stderr(err))
            try:
                rc = ct.main(argv)
            except SystemExit as e:
                rc = e.code
        self.stdout, self.stderr = out.getvalue(), err.getvalue() + out.getvalue()
        return rc

    def readout(self, t, name):
        return json.loads((t.out / f"{name}.json").read_text())

    def assertRefuses(self, t, argv, msg, extra=(), rc=1):
        self.assertEqual(self.run_tool(t, argv, extra), rc, self.stderr)
        self.assertIn(msg, self.stderr)
        self.assertFalse(any(t.out.iterdir()), "a refused run wrote something")


def keys_anywhere(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from keys_anywhere(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from keys_anywhere(v)


# ------------------------------------------------------------------------------------------------ pure


class Pure(unittest.TestCase):
    def test_chi2_quantiles(self):
        self.assertAlmostEqual(ct.chi2_quantile(0.95, 16), 26.2962, places=3)
        self.assertAlmostEqual(ct.chi2_quantile(0.95, 8), 15.5073, places=3)
        if _chi2 is not None:
            for q in (0.05, 0.16, 0.5, 0.68, 0.84, 0.95):
                for n in (8, 16):
                    self.assertAlmostEqual(ct.chi2_quantile(q, n), float(_chi2.ppf(q, n)), places=8)

    def test_weighted_percentiles_with_equal_weights_are_the_inverted_cdf(self):
        v = np.random.default_rng(3).normal(size=101)
        got = ct.weighted_percentiles(v, np.ones(101), ct.PERCENTILES)
        want = [float(np.sort(v)[int(np.ceil(p / 100 * 101)) - 1]) for p in ct.PERCENTILES]
        self.assertEqual(got, want)

    def test_weighted_percentiles_follow_the_weights(self):
        v, w = np.array([1.0, 2.0, 3.0]), np.array([0.1, 0.1, 0.8])
        self.assertEqual(ct.weighted_percentiles(v, w, (16.0, 50.0)), [2.0, 3.0])

    def test_the_declared_constants(self):
        self.assertEqual(ct.PERCENTILES, (5.0, 16.0, 50.0, 84.0, 95.0))
        self.assertEqual(ct.EXTRAPOLATED, 0.10)
        self.assertEqual(ct.PERIODS, ("PA", "PB", "PC"))
        self.assertEqual({v: s for v, (*_, s) in ct.W2B.items()}, {"rr0": 0.96, "rr1": 1.04, "rrzero": 1.0})

    def test_cal_is_f0s_five_calibration_truths(self):
        self.assertEqual([c for _, c, _ in ct.CAL], list(F.COUNTS["cal"]))
        self.assertEqual(len({h for _, _, h in ct.CAL}), 5)


# ------------------------------------------------------------------------------------------------ 3a


class Recoil(Base):
    def test_end_to_end_recomputed_by_hand(self):
        t = self.tree().write_recoil()
        self.assertEqual(self.run_tool(t, t.argv_recoil), 0, self.stderr)
        r = self.readout(t, "recoil")
        Z, X = t.X["rrzero"], t.X
        d = (X["rr1"] - X["rr0"]) / (2 * Z)
        np.testing.assert_allclose(r["shift_minus"], X["rr0"] / Z - 1, rtol=1e-9, atol=1e-15)
        np.testing.assert_allclose(r["shift_plus"], X["rr1"] / Z - 1, rtol=1e-9, atol=1e-15)
        np.testing.assert_allclose(r["half_span"], d, rtol=1e-9, atol=1e-15)
        sr = np.sqrt(np.diag(t.Cr)) / t.f
        sm = np.sqrt(np.diag(t.Ct + t.Cr)) / t.f
        np.testing.assert_allclose(r["sigma_rel"]["C_resp"], sr, rtol=1e-12)
        np.testing.assert_allclose(r["abs_half_span_over_sigma"]["C_total_resp"], np.abs(d) / sm, rtol=1e-9)
        Mrel = (t.Ct + t.Cr) / np.outer(t.f, t.f)
        self.assertAlmostEqual(r["half_span_quadratic_form"]["C_total_resp"], float(d @ np.linalg.solve(Mrel, d)), places=6)
        # in-span fraction by an independent route: least squares on the four species directions
        dirs = np.array([np.linalg.eigh(v / np.outer(t.f, t.f))[1][:, -1] for v in t.species.values()]).T
        coef, *_ = np.linalg.lstsq(dirs, d, rcond=None)
        p = dirs @ coef
        self.assertAlmostEqual(r["fraction_of_half_span_in_C_resp_span"]["value"], float(p @ p / (d @ d)), places=9)
        self.assertEqual(r["fraction_of_half_span_in_C_resp_span"]["C_resp_rank"], 4)
        self.assertEqual(r["scales"], {"rr0": 0.96, "rr1": 1.04, "rrzero": 1.0})
        self.assertEqual(r["labels"]["not_citable_for"], ct.LABELS["not_citable_for"])

    def test_refuses_a_product_whose_digest_is_not_recorded(self):
        t = self.tree().write_recoil()
        t.w2b["rr0"] = ("0" * 64,) + t.w2b["rr0"][1:]
        self.assertRefuses(t, t.argv_recoil, "FAIL control R0: W2b rr0")

    def test_refuses_a_product_made_on_another_dump(self):
        t = self.tree().write_recoil(meta_extra={"rr1": {"input_npz_sha256": fake("other")}})
        t.w2b["rr1"] = (digest(t.root / "w2b/unf/w2b_rr1_b-_j-.npz"),) + t.w2b["rr1"][1:]
        self.assertRefuses(t, t.argv_recoil, "FAIL control R0: w2b_rr1_b-_j-.npz: input_npz_sha256")

    def test_refuses_a_non_positive_integral(self):
        t = self.tree().write_recoil(positive=False)
        self.assertRefuses(t, t.argv_recoil, "FAIL control R1 every W2b cell integral is positive")

    def test_refuses_a_C_resp_that_is_not_its_species_sum(self):
        t = Tree(self.tmp / "tree")
        t.write_common(Cr_override=t.Cr + t.xtalk).write_recoil()
        self.assertRefuses(t, t.argv_recoil, "FAIL control S C_resp is the sum of its four primary species")

    def test_refuses_a_C_total_resp_that_is_not_C_total_plus_C_resp(self):
        t = Tree(self.tmp / "tree")
        t.write_common(Ctr_override=t.Ct + 1.001 * t.Cr).write_recoil()
        self.assertRefuses(t, t.argv_recoil, "FAIL control S C_total_resp = S1's C_total + C_resp")

    def test_refuses_another_s1_assembly(self):
        t = self.tree().write_recoil()
        t.pins["s1_npz"] = "0" * 64
        self.assertRefuses(t, t.argv_recoil, "FAIL control S: S1 assembly")

    def test_refuses_to_overwrite(self):
        t = self.tree().write_recoil()
        (t.out / "recoil.json").write_text("{}")
        self.assertEqual(self.run_tool(t, t.argv_recoil), 1)
        self.assertIn("refusing to overwrite", self.stderr)

    def test_the_guard_refuses_a_planted_absolute_value(self):
        t = self.tree().write_recoil()
        with mock.patch.object(ct, "rel_sigma", lambda C, f: f):
            self.assertRefuses(t, t.argv_recoil, "REFUSED leak guard", rc=3)

    def test_nothing_written_carries_f_or_a_cell_integral(self):
        t = self.tree().write_recoil()
        self.run_tool(t, t.argv_recoil)
        text = (t.out / "recoil.json").read_text()
        for v in np.concatenate([t.f, *t.X.values()]):
            self.assertNotIn(repr(float(v)), text)


# ------------------------------------------------------------------------------------------------ 4C


class Chi2(Base):
    def setUp(self):
        super().setUp()
        self.t = self.tree().write_chi2()

    def test_end_to_end_recomputed_by_hand(self):
        t = self.t
        self.assertEqual(self.run_tool(t, t.argv_chi2, t.chi2_patches()), 0, self.stderr)
        r = self.readout(t, "chi2")
        ff = np.outer(t.f, t.f)
        mats = {"C_total_resp": (t.Ct + t.Cr) / ff, "C_e": t.Ce / ff}
        for name, items in t.cal.items():
            rs, ws = [], []
            for p, u in items:
                with np.load(p) as z:
                    rs.append((t.U @ z["xsec_flat"]) / (t.U @ z["xtrue_flat"]) - 1)
                ws.append(t.weights[u])
            rs, ws = np.array(rs), np.array(ws)
            rec = r["truths"][name]
            self.assertEqual(rec["n_experiments"], N_CAL)
            self.assertEqual(set(rec["matrices"]["C_e"]), {"all16", "gibuu8"} if name == "A7_gibuu" else {"all16"})
            for mn, M in mats.items():
                for cn, idx in (("all16", list(range(16))), ("gibuu8", list(F.GIBUU_CELLS))):
                    if cn not in rec["matrices"][mn]:
                        continue
                    Mi, ri = M[np.ix_(idx, idx)], rs[:, idx]
                    Minv = np.linalg.inv(Mi)
                    b = (ws[:, None] * ri).sum(0) / ws.sum()
                    c2t = np.einsum("ij,jk,ik->i", ri, Minv, ri)
                    c2c = np.einsum("ij,jk,ik->i", ri - b, Minv, ri - b)
                    got = rec["matrices"][mn][cn]
                    self.assertAlmostEqual(got["about_truth"]["weighted"]["mean"], float(ws @ c2t / ws.sum()), places=8)
                    self.assertAlmostEqual(got["about_weighted_mean"]["unweighted"]["mean"], float(c2c.mean()), places=8)
                    np.testing.assert_allclose(list(got["about_truth"]["unweighted"]["percentiles"].values()),
                                               np.percentile(c2t, ct.PERCENTILES), rtol=1e-9)
                    o = np.argsort(c2t)
                    cum = np.cumsum(ws[o]) / ws.sum()
                    med = float(c2t[o][np.argmax(cum >= 0.5)])
                    self.assertAlmostEqual(got["about_truth"]["weighted"]["percentiles"]["50.0"], med, places=10)
                    np.testing.assert_allclose(list(got["about_truth"]["reference_chi2"]["percentiles"].values()),
                                               [ct.chi2_quantile(p / 100, len(idx)) for p in ct.PERCENTILES], rtol=1e-12)
                    self.assertAlmostEqual(got["chi2_of_weighted_mean_bias"], float(b @ Minv @ b), places=8)
                    sd = np.sqrt((ws[:, None] * (ri - b) ** 2).sum(0) / ws.sum())
                    np.testing.assert_allclose(got["width_ratio"], sd / np.sqrt(np.diag(Mi)), rtol=1e-9)
        keys = set(keys_anywhere(r))
        self.assertNotIn("p", keys)
        self.assertFalse([k for k in keys if "share" in k or "tail" in k or "above" in k], "a tail fraction is written")

    def test_refuses_a_b_eff_that_is_not_f0bs(self):
        t = self.t
        t.write_chi2_records(beff_scale=1 + 1e-9)
        self.assertRefuses(t, t.argv_chi2, "FAIL control C2 A7_mnvtune: B_eff", t.chi2_patches())

    def test_refuses_a_product_changed_after_its_manifest(self):
        t = self.t
        p, u = t.cal["A7_gibuu"][11]
        with np.load(p) as z:
            arr = {k: z[k] for k in z.files}
        arr["xsec_flat"] = arr["xsec_flat"] * (1 + 1e-9)
        np.savez_compressed(p, **arr)
        self.assertRefuses(t, t.argv_chi2, f"FAIL control C0: A7_gibuu {p}: sha256", t.chi2_patches())

    def test_refuses_an_unlisted_product(self):
        t = self.t
        p, u = t.cal["A7_nuwro"][0]
        shutil.copy(p, p.with_name("cal_NuWro_21_09_s1299999.npz"))
        self.assertRefuses(t, t.argv_chi2, "FAIL control C0:", t.chi2_patches())

    def test_refuses_a_product_at_another_hypothesis(self):
        t = self.t
        p, u = t.cal["A7_genie_mec"][3]
        with np.load(p) as z:
            arr = {k: z[k] for k in z.files}
        m = json.loads(str(arr.pop("meta")))
        m["hypothesis"]["sha256"] = F.HYP["genie_cv"]
        np.savez_compressed(p, **arr, meta=json.dumps(m))
        t.write_chi2_records()
        self.assertRefuses(t, t.argv_chi2, "FAIL control C1: cal_GENIE_2_12_10_MEC", t.chi2_patches())

    def test_refuses_a_count_other_than_declared(self):
        t = self.t
        ps = [mock.patch.dict(F.COUNTS, {"cal": {**{c: N_CAL for _, c, _ in ct.CAL}, "GiBUU_2019": N_CAL + 1}}),
              t.chi2_patches()[1]]
        self.assertRefuses(t, t.argv_chi2, "FAIL control C1: GiBUU_2019: 40 products, 41 declared", ps)

    def test_refuses_a_non_positive_truth_integral(self):
        t = self.t
        p, u = t.cal["A7_genie_cv"][7]
        with np.load(p) as z:
            arr = {k: z[k] for k in z.files}
        xt = arr["xtrue_flat"].copy()
        xt[t.fm == 4] *= -1.0
        arr["xtrue_flat"] = xt
        np.savez_compressed(p, **arr)
        t.write_chi2_records()
        self.assertRefuses(t, t.argv_chi2, "FAIL control C3: A7_genie_cv: a truth integral is not positive", t.chi2_patches())

    def test_refuses_another_s5p_manifest(self):
        t = self.t
        t.pins["s5p_sums"] = "0" * 64
        self.assertRefuses(t, t.argv_chi2, "FAIL control C0: s5p archive sums", t.chi2_patches())


# ------------------------------------------------------------------------------------------------ 5A


class Period(Base):
    def hand(self, t, x):
        """Footprint weights by explicit accumulation over fine cells."""
        shape = sa.s1.fine_shape()
        vol = sa.s1.fine_volume()
        sup = set(int(c) for c in t.support)
        pos = {int(c): k for k, c in enumerate(t.support)}
        om, outside = np.zeros((16, t.support.size)), np.zeros(16)
        tot, ins = np.zeros(16), np.zeros(16)
        acc = [dict() for _ in range(16)]
        for i in np.flatnonzero(t.fm >= 0):
            R = int(t.fm[i])
            ipt, ipz = np.unravel_index(i, shape)[:2]
            c2 = int(ipt) * 16 + int(ipz)
            w = x[i] * vol[i]
            tot[R] += w
            if c2 in sup:
                ins[R] += w
                acc[R][c2] = acc[R].get(c2, 0.0) + w
        for R in range(16):
            for c2, w in acc[R].items():
                om[R, pos[c2]] = w / ins[R]
            outside[R] = (tot[R] - ins[R]) / tot[R]
        return om, outside

    def test_end_to_end_recomputed_by_hand(self):
        t = self.tree().write_period()
        self.assertEqual(self.run_tool(t, t.argv_period), 0, self.stderr)
        r = self.readout(t, "period")
        sm = np.sqrt(np.diag((t.Ct + t.Cr) / np.outer(t.f, t.f)))
        for vn, x in (("central", t.xc), ("prior", t.xp)):
            om, outside = self.hand(t, x)
            g = {X: om @ t.g[X] for X in ct.PERIODS}
            rr = {X: om @ t.r[X] for X in ct.PERIODS}
            C = t.k * sum(t.e[X] * np.outer(g[X], g[X]) for X in ct.PERIODS)
            Sref = sum(np.outer(t.e[X] * (rr[X] / rr["PA"] - 1), t.e[X] * (rr[X] / rr["PA"] - 1)) for X in ("PB", "PC"))
            v = r["variants"][vn]
            for X in ct.PERIODS:
                np.testing.assert_allclose(v["g"][X], g[X], rtol=1e-9, atol=1e-15)
            np.testing.assert_allclose(v["C_PL16_rel"], C, rtol=1e-9, atol=1e-18)
            np.testing.assert_allclose(v["sigma_rel"]["S_ref16"], np.sqrt(np.diag(Sref)), rtol=1e-9)
            np.testing.assert_allclose(v["sigma_ratio_to_C_total_resp"], np.sqrt(np.diag(C)) / sm, rtol=1e-9)
            np.testing.assert_allclose(v["weight_outside_2d_support"], outside, rtol=1e-9, atol=1e-15)
            self.assertEqual(v["extrapolated_cells"], [f"R{c:02d}" for c in range(16) if outside[c] > ct.EXTRAPOLATED])
            self.assertLessEqual(v["rank"], 2)
            self.assertAlmostEqual(v["trace_share"], float(np.trace(C) / np.trace((t.Ct + t.Cr) / np.outer(t.f, t.f) + C)), places=12)
        # the synthetic support leaves R08-R15 partly outside, and R00-R07 wholly inside
        self.assertEqual(r["variants"]["central"]["weight_outside_2d_support"][:8], [0.0] * 8)
        self.assertTrue(all(v > 0 for v in r["variants"]["central"]["weight_outside_2d_support"][8:]))
        self.assertAlmostEqual(r["constants"]["k"], t.k, places=14)

    def test_refuses_a_stored_C_PL_that_is_not_rebuilt(self):
        t = self.tree().write_period(cpl_defect=1e-9)
        self.assertRefuses(t, t.argv_period, "FAIL control P0 C_PL rebuilt from k, e, x and g")

    def test_refuses_offsets_that_do_not_cancel(self):
        t = self.tree().write_period(gsum_defect=1e-9)
        self.assertRefuses(t, t.argv_period, "FAIL control P0 sum_X e_X g_X = 0 on every cell")

    def test_refuses_an_e_that_varies_by_cell(self):
        t = self.tree().write_period(e_ripple=1e-9)
        self.assertRefuses(t, t.argv_period, "FAIL control P0 e_X is constant over cells")

    def test_refuses_a_json_that_names_another_npz(self):
        t = self.tree().write_period(json_npz="0" * 64)
        self.assertRefuses(t, t.argv_period, "FAIL control P0 the committed playlist_term.json names this npz")

    def test_refuses_a_central_value_that_is_not_s1s_f(self):
        t = self.tree().write_period(central_scale=1 + 1e-9)
        self.assertRefuses(t, t.argv_period, "FAIL control P1 the central value's cell integrals are S1's f")

    def test_refuses_a_prior_of_another_schema(self):
        t = self.tree().write_period(prior_schema="s5p-mc-truth-pred/0")
        self.assertRefuses(t, t.argv_period, "FAIL control P2 the prior is MnvTune v1's")

    def test_p3_refuses_a_cell_with_no_weight_on_the_support(self):
        t = self.tree().write_period()
        x = t.xc.copy()
        x[t.fm == 9] = 0.0
        with self.assertRaises(F.Stop) as cm:
            ct.footprint(t.U, t.fm, x, t.support)
        self.assertIn("FAIL control P3: R09", str(cm.exception.code))

    def test_p4_refuses_offsets_that_do_not_cancel_on_the_cells(self):
        t = self.tree().write_period()
        om, outside = ct.footprint(t.U, t.fm, t.xc, t.support)
        z = {f"g_{X}": t.g[X] for X in ct.PERIODS}
        z.update({f"r_{X}": t.r[X] for X in ct.PERIODS})
        S = {"M": t.Ct + t.Cr, "ff": np.outer(t.f, t.f)}
        ct.period_variant(om, outside, z, t.e, t.k, S)          # passes as built
        z["g_PC"] = z["g_PC"] + 1e-6
        with self.assertRaises(F.Stop) as cm:
            ct.period_variant(om, outside, z, t.e, t.k, S)
        self.assertIn("FAIL control P4: sum_X e_X g_X,R", str(cm.exception.code))

    def test_nothing_written_carries_f(self):
        t = self.tree().write_period()
        self.run_tool(t, t.argv_period)
        text = (t.out / "period.json").read_text()
        for v in t.f:
            self.assertNotIn(repr(float(v)), text)


# ------------------------------------------------------------------------------------------------ as invoked


class Invocation(Base):
    def run_isolated(self, args):
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        with tempfile.TemporaryDirectory(prefix="fd-ct-cwd-") as cwd:
            return subprocess.run([sys.executable, "-I", "-B", *args], cwd=cwd, env=env, capture_output=True,
                                  text=True, timeout=600)

    def test_the_module_as_invoked(self):
        t = self.tree().write_recoil()
        cfg = self.tmp / "cfg.json"
        cfg.write_text(json.dumps({"nd": str(ND), "pins": t.pins, "w2b": t.w2b, "argv": t.argv_recoil}))
        w = self.tmp / "wrap.py"
        w.write_text("import json, sys\ncfg = json.load(open(sys.argv[1]))\nsys.path.insert(0, cfg['nd'])\n"
                     "import fd_ct_readers as m\nm.PINS.update(cfg['pins'])\n"
                     "m.W2B.clear(); m.W2B.update({k: tuple(v) for k, v in cfg['w2b'].items()})\n"
                     "sys.argv = ['fd_ct_readers.py'] + cfg['argv']\nraise SystemExit(m.main(cfg['argv']))\n")
        r = self.run_isolated([str(w), str(cfg)])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("PASS control R1", r.stdout)
        self.assertEqual(json.loads(r.stdout.strip().splitlines()[-1])["sha256"], digest(t.out / "recoil.json"))

    def test_the_real_pins_refuse_the_synthetic_tree(self):
        t = self.tree().write_recoil()
        r = self.run_isolated([str(ND / "fd_ct_readers.py"), *t.argv_recoil])
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("FAIL control R0: W2b rr0", r.stderr)
        self.assertFalse(any(t.out.iterdir()))


class CommittedPins(unittest.TestCase):
    def test_the_committed_records_match_the_pins(self):
        self.assertEqual(digest(STATE / "s5p/archive/SHA256SUMS-s5p-archive-20261006.txt"), ct.PINS["s5p_sums"])
        self.assertEqual(digest(STATE / "measurement-paper/5d-community-20261024/fd/readout/fd_f0b_readout.json"),
                         ct.PINS["f0b_readout"])
        self.assertEqual(digest(STATE / "2d-closeout/playlist-term/outputs/playlist_term.json"), ct.PINS["playlist_json"])
        pj = json.loads((STATE / "2d-closeout/playlist-term/outputs/playlist_term.json").read_text())
        self.assertEqual(pj["npz"]["sha256"], ct.PINS["playlist_npz"])

    def test_the_w2b_pins_are_the_w2b_reports(self):
        text = (REPO / "publication/w2/W2B-REPORT-20261006.md").read_text()
        for v, (sha, *_rest) in ct.W2B.items():
            self.assertIn(f"`unf/w2b_{v}_b-_j-.npz` `{sha}`", text)

    def test_the_prior_and_central_pins_are_the_records(self):
        import fd_g_compare as G
        self.assertEqual(next(p["sha256"] for p in G.PREDICTIONS if p["name"] == "mnvtune_v1"), ct.PINS["prior"])
        decl = (STATE / "measurement-paper/5d-community-20261024/S1-DECLARATION.md").read_text()
        self.assertIn(ct.PINS["central"][:8], decl)
        bk = json.loads((STATE / "measurement-paper/5d-community-20261024/fd/readout/fd_f0b_readout.json").read_text())
        self.assertEqual(set(bk["controls"]["offset_control_7"]["B_eff_calibration"]), {n for n, _, _ in ct.CAL})


if __name__ == "__main__":
    unittest.main()
