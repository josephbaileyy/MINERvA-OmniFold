"""Controls for fd_f0_regrade (FD-F0-DECLARATION.md section 5), on a synthetic tree of every input F0 reads and on the
committed records. No real product, covariance or data value is read.

* The tool runs as declared, ``env -u PYTHONPATH <python> -I -B``, from a cwd outside nd-unfolding (the S1 lesson,
  test_s1_scripts_isolated.py): the real script to its first control, and the module end to end on the synthetic tree.
* Ruling 6: nothing the run writes or prints carries f, an absolute cell value or f - g. The scan here is the test's
  own: it is built from the fixture's construction, not from the tool's guard, and it reads stdout, stderr, the readout
  JSON and the per-experiment table. A run in O(1) units shows the guard does not lean on the 1e-30 floor alone, and
  planted leaks of each kind are refused with nothing written.
* Each of controls 0-8 refuses on a one-entry defect, and the grades are recomputed here by hand."""
import copy
import hashlib
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
import fd_f0_regrade as F  # noqa: E402
import s1_assemble as sa  # noqa: E402

REPO = ND.parent
DEFINITION = ND / "pv-ladder/readouts/h2_definition.json"
STATE = REPO / "docs/orchestration/state"
FD = STATE / "measurement-paper/5d-community-20261024"
N = F.N_FINE

try:
    from scipy.stats import chi2 as _chi2
except ImportError:  # pragma: no cover
    _chi2 = None


def digest(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


EST = [{"n_estimators": 100, "num_leaves": 8, "random_state": 42, "bin_construct_sample_cnt": F.ALL_ROWS,
        "deterministic": True, "force_row_wise": True, "subsample": 1.0, "colsample_bytree": 1.0,
        "subsample_for_bin": 200000}] * 3
REF = {"ran": True, "classifier_params": {"n_estimators": 400, "num_leaves": 31, "random_state": 45,
                                          "bin_construct_sample_cnt": F.ALL_ROWS, "deterministic": True}}
CODE = {"candidate": "R", "candidate_refine_override": {"n_estimators": 400, "num_leaves": 31}}


def base_meta(top_seed=True):
    """As the producers write it: s5n_pseudo and pvl_unfold record estimator_seed; s5p_nullexp (rows 4-6) does not."""
    return {**({"estimator_seed": 42} if top_seed else {}), "iters": 5, "estimator_params": copy.deepcopy(EST), "refinement": copy.deepcopy(REF),
            "code_sha256": dict(CODE), "input_npz_sha256": F.INPUT_NPZ_SHA256, "bkg_dump_sha256": F.BKG_SHA256}


SMALL = 3       # experiments per s5e, Stage 0c, f4 and power set
N_CAL = 60      # per calibration truth: the offset noise must be full rank and B_eff well above 16


def small_truths():
    out = []
    for t in F.TRUTHS:
        t = dict(t)
        if "seeds" in t:
            t["seeds"] = (t["seeds"][0], SMALL)
        out.append(t)
    return tuple(out)


def small_counts():
    return {"cal": {k: N_CAL for k in F.COUNTS["cal"]}, "pow": {k: SMALL for k in F.COUNTS["pow"]}, "f4": SMALL}


class Tree:
    """Every input of one F0 run, built from known cell integrals: per product the truth integrals Xt and the
    residuals r, so that the cell integrals of xsec_flat are exactly (1 + r) Xt."""

    def __init__(self, root: Path, scale=1e-39, seed=0, offset_shift=0.0):
        self.root, self.scale = root, scale
        rng = np.random.default_rng(seed)
        self.fm = sa.fine_map(DEFINITION)
        self.U = sa.functional_matrix(self.fm)
        self.volc = self.U.sum(axis=1)
        self.truths = small_truths()
        self.f = rng.uniform(4, 6, F.N_CELLS) * scale
        ff = np.outer(self.f, self.f)
        A = rng.normal(size=(40, F.N_CELLS))
        stat_rel = 0.003 ** 2 * (np.cov(A, rowvar=False) + np.eye(F.N_CELLS))
        v, w = rng.normal(0, 0.035, F.N_CELLS), rng.normal(0, 0.02, F.N_CELLS)
        rel = {"stat": stat_rel, "band:Flux": np.outer(v, v), "lat:BeamAngleX": np.outer(w, w),
               "normalization": np.full((F.N_CELLS, F.N_CELLS), 0.014 ** 2), "seed": 1e-8 * np.eye(F.N_CELLS)}
        self.blocks = {k: m * ff for k, m in rel.items()}
        self.Ce = sum(self.blocks.values())
        self.S = rng.normal(0, 0.02, (3, F.N_CELLS)) * np.array([[0.4], [1.0], [3.0]])
        self.Cmf = self.S.T @ self.S
        self.Cma = self.Cmf * ff
        self.Ct = self.Ce + self.Cma
        self.T0 = rng.uniform(4, 6, F.N_CELLS) * scale
        self.weights = rng.uniform(0.5, 1.5, 100)
        self.delta = rng.normal(0, 0.03, (100, F.N_CELLS))      # the flux universe's offset on r
        self.offset_shift = offset_shift
        self.rng = rng
        self.products = {}      # set name -> list of (path, meta, Xt, r)
        self.bias = {}
        self.build()

    # ---- products
    def arrays(self, Xt, r):
        a = np.where(self.fm >= 0, (Xt / self.volc)[np.clip(self.fm, 0, None)], 0.5 * self.scale)
        return a * np.where(self.fm >= 0, (1 + r)[np.clip(self.fm, 0, None)], 1.0), a

    def add(self, name, path, meta, Xt, r):
        self.products.setdefault(name, []).append([Path(path), meta, np.asarray(Xt, float), np.asarray(r, float)])

    def truth_set(self, name, d, prefix, seeds, meta_of, noise=0.004, flux=False, extra=0.0):
        b = self.rng.normal(0, 0.01, F.N_CELLS)
        Tt = self.T0 * (1 + self.rng.normal(0, 0.05, F.N_CELLS))
        self.bias[name] = b
        for s in seeds:
            Xt = Tt * (1 + self.rng.normal(0, 1e-3, F.N_CELLS))
            r = b + self.rng.normal(0, noise, F.N_CELLS)
            m = meta_of(s)
            if flux:
                u = int(self.rng.integers(0, 100))
                m["nuisance_draw"] = {"flux": u, "model": {}, "detector": {}}
                r = r + self.delta[u] + extra
            self.add(name, d / f"{prefix}_s{s}.npz", m, Xt, r)
        return Tt

    def build(self):
        R = self.root
        self.s5e, self.s0c, self.pvl = R / "s5e/assess", R / "stage0", R / "pvl"
        self.f4root, self.s5p = R / "s5p/runs/s3r/f4", R / "s5p"
        for t in self.truths:
            if t["row"] in (1, 2):
                d = self.s5e / t["set"] if t["row"] == 1 else self.s0c / "runs" / t["set"]

                def mo(s, t=t):
                    return {**base_meta(), "schema": "s5n-unfold/1", "config": "deterministic",
                            "bkg_mode": "negweight-refined", "no_background": False, **t["ident"], "pseudo_seed": s}
                self.truth_set(t["name"], d, f"{t['set']}_a1", range(t["seeds"][0], t["seeds"][0] + SMALL), mo)
            elif t["row"] == 3:
                for name, prod, ratio in (("closure_nuwro", t["product"], F.RATIO["closure_nuwro"]),
                                          ("floor", "L-5D-PV_e_closure_tune_v1", F.RATIO["floor"])):
                    m = {**base_meta(), "refinement": {"ran": False, "reason": "no negative weights (signal-only reference)"},
                         "schema": "pvl-unfold/1", "rung": "L-5D-PV", "arm": "e", "closure": True,
                         "features": ["pt", "pz", "eavail", "q3", "W"], "ratio_sha256": ratio}
                    r = self.rng.normal(0, 0.02 if name == "closure_nuwro" else 1e-5, F.N_CELLS)
                    self.bias[name] = r
                    self.add(name, self.pvl / f"{prod}.npz", m, self.T0 * (1 + self.rng.normal(0, 0.05, F.N_CELLS)), r)
            elif t["row"] == 4:
                def nm(s, t=t, kind="f4"):
                    m = {**base_meta(top_seed=False), "schema": "s5p-null-experiment/1", "config": "R", "capacity": None,
                         "hypothesis": {"sha256": F.HYP[t["d16"]]}, "alternative": None, "pseudo_seed": s}
                    m["code_sha256"]["s5p_nullexp.py"] = F.NULLEXP_F4[s % 2] if kind == "f4" else F.NULLEXP_PROD[0]
                    m["development"] = {"expectation": kind == "f4", "mc_fraction": "half"}
                    m["nuisance_draw"] = None
                    return m
                Tt = self.truth_set(t["name"], self.f4root / f"{t['f4']}_half", f"f4_{t['f4']}_half",
                                    range(970000, 970000 + SMALL), nm, noise=0.002)
                cal = self.s5p / "runs/prod/cal" / t["cal"]
                b = self.bias[t["name"]]
                shift = self.offset_shift if t["name"] == "A7_genie_cv" else 0.0
                for s in range(1200000, 1200000 + N_CAL):
                    u = int(self.rng.integers(0, 100))
                    m = nm(s, kind="cal")
                    m["nuisance_draw"] = {"flux": u, "model": {}, "detector": {}}
                    self.add("cal:" + t["name"], cal / f"cal_{t['cal']}_s{s}.npz", m,
                             Tt * (1 + self.rng.normal(0, 1e-3, F.N_CELLS)),
                             b + self.delta[u] + shift + self.rng.normal(0, 0.004, F.N_CELLS))
            else:
                ref = next(r for r in self.truths if r["name"] == t["ref"])
                tt, sha = F.ALT[t["alt"]]

                def pm(s, ref=ref, tt=tt, sha=sha):
                    m = {**base_meta(top_seed=False), "schema": "s5p-null-experiment/1", "config": "R", "capacity": None,
                         "hypothesis": {"sha256": F.HYP[ref["d16"]]}, "pseudo_seed": s,
                         "alternative": {"truth": tt, "amplitude": 1.0, "sha256": sha},
                         "development": {"expectation": False, "mc_fraction": "half"}}
                    m["code_sha256"]["s5p_nullexp.py"] = F.NULLEXP_PROD[0]
                    return m
                self.truth_set(t["name"], self.s5p / "runs/prod/pow" / t["pow"], f"pow_{t['pow']}",
                               range(1451000, 1451000 + SMALL), pm, flux=True)

    def write(self):
        return self.write_products().write_records()

    def write_products(self):
        if self.root.exists():
            shutil.rmtree(self.root)
        self.root.mkdir(parents=True)
        for items in self.products.values():
            for path, meta, Xt, r in items:
                path.parent.mkdir(parents=True, exist_ok=True)
                xs, xt = self.arrays(Xt, r)
                np.savez_compressed(path, xsec_flat=xs, xtrue_flat=xt, meta=json.dumps(meta))
        return self

    def write_records(self):
        """Manifests, records and pins, from the products as they are on disk."""
        R = self.root
        inv = R / "INVENTORY.sha256"
        inv.write_text("".join(f"{digest(p)}  {p}\n" for t in self.truths if t["row"] == 1
                               for p, *_ in self.products[t["name"]]) + f"{'0' * 64}  /elsewhere/other.npz\n")
        s0c = R / "products.sha256"
        s0c.write_text("".join(f"{digest(p)}  {p.relative_to(self.s0c)}\n" for p, *_ in self.products["stage0c_gibuu"]))
        s5p = R / "SHA256SUMS.txt"
        s5p.write_text("".join(f"{digest(p)}  {p.relative_to(self.s5p)}\n" for name, items in self.products.items()
                               if name.startswith("cal:") or name in {t["name"] for t in self.truths if t["row"] == 6}
                               for p, *_ in items))
        d16 = R / "d16"
        d16.mkdir()
        for t in self.truths:
            if t["row"] == 4:
                (d16 / f"D16-{t['d16']}.json").write_text(json.dumps({"inputs": [
                    {"a": str(p), "a_sha256": digest(p), "b": "q", "b_sha256": "0" * 64} for p, *_ in self.products[t["name"]]]}))
        con = R / "constraint.txt"
        con.write_text("".join(f"Flux {i} {w!r}\n" for i, w in enumerate(self.weights)) + "Other 0 1.0\n")
        s1n = R / "s1_assembly.npz"
        ff = np.outer(self.f, self.f)
        np.savez_compressed(s1n, f=self.f, U=self.U.astype(np.float32), C_e=self.Ce, C_model_frac=self.Cmf,
                            C_model_abs=self.Cma, C_total=self.Ct,
                            **{"C_" + k.replace(":", "_"): v for k, v in self.blocks.items()},
                            meta=json.dumps({"blocks": sorted(self.blocks)}))
        s1j = R / "s1_assembly.json"
        s1j.write_text(json.dumps({"assembly_sha256": digest(s1n), "relative_sigma": {
            "C_e": (np.sqrt(np.diag(self.Ce)) / self.f).tolist(), "C_total": (np.sqrt(np.diag(self.Ct)) / self.f).tolist()}}))
        cmn = R / "cmodel_5d.npz"
        np.savez(cmn, C_model=self.Cmf, S=self.S)
        cmj = R / "cmodel_5d.json"
        closure = self.products["closure_nuwro"][0]
        cmj.write_text(json.dumps({"vertices": list(F.VERTICES), "S": self.S.tolist(), "positive_control": {
            "reporting16": {"bias_cells": self.rel(closure).tolist()}}}))
        Ce_rel = self.Ce / ff
        table = {}
        for k, own in (("C_e", "all"), ("C_total", None), *((f"minus_{v}", v) for v in F.VERTICES)):
            M = Ce_rel if own == "all" else F.leave_out(Ce_rel, self.S, own)
            table[k] = F.sigma_summary(np.sqrt(np.diag(M)))
        floor = self.products["floor"][0]
        self.pins = {"s1_npz": digest(s1n), "s1_json": digest(s1j), "cmodel_npz": digest(cmn), "cmodel_json": digest(cmj),
                     "stage0_inventory": digest(inv), "stage0c_sums": digest(s0c), "s5p_sums": digest(s5p),
                     "d16": {t["d16"]: digest(d16 / f"D16-{t['d16']}.json") for t in self.truths if t["row"] == 4},
                     "closure": digest(closure[0]), "floor": digest(floor[0]),
                     "floor_max_abs": float(np.max(np.abs(self.rel(floor)))), "table_2_1": table}
        self.constraint_sha = digest(con)
        self.out = R / "out"
        self.out.mkdir()
        self.argv = ["--definition", str(DEFINITION), "--s1-npz", str(s1n), "--s1-json", str(s1j),
                     "--cmodel-npz", str(cmn), "--cmodel-json", str(cmj), "--flux-constraint", str(con),
                     "--d16-dir", str(d16), "--f4-root", str(self.f4root), "--stage0-inventory", str(inv),
                     "--s5e-assess", str(self.s5e), "--stage0c-sums", str(s0c), "--stage0c-root", str(self.s0c),
                     "--pvl-products", str(self.pvl), "--s5p-sums", str(s5p), "--s5p-root", str(self.s5p),
                     "--out-json", str(self.out / "readout.json"), "--out-npz", str(self.out / "table.npz")]
        return self

    def rel(self, item):
        """r as the tool computes it, from the integrals of the arrays actually written."""
        xs, xt = self.arrays(item[2], item[3])
        return (self.U @ xs) / (self.U @ xt) - 1

    def integrals(self):
        out = []
        for items in self.products.values():
            for item in items:
                xs, xt = self.arrays(item[2], item[3])
                out += [self.U @ xs, self.U @ xt]
        return np.array(out)

    def patches(self):
        return [mock.patch.object(F, "TRUTHS", self.truths), mock.patch.object(F, "COUNTS", small_counts()),
                mock.patch.object(sa, "CONSTRAINT_SHA256", self.constraint_sha)]

    def config(self, leak=None, disable_guard=False):
        return {"nd": str(ND), "pins": self.pins, "truths": self.truths, "counts": small_counts(),
                "constraint": self.constraint_sha, "argv": self.argv, "leak": leak, "disable_guard": disable_guard}


WRAPPER = r"""
import json, sys
cfg = json.load(open(sys.argv[1]))
sys.path.insert(0, cfg["nd"])
import numpy as np
import fd_f0_regrade as m
import s1_assemble as sa
pins = cfg["pins"]
pins["table_2_1"] = {k: tuple(v) for k, v in pins["table_2_1"].items()}
m.PINS, m.COUNTS, sa.CONSTRAINT_SHA256 = pins, cfg["counts"], cfg["constraint"]
m.TRUTHS = tuple(dict(t, seeds=tuple(t["seeds"])) if "seeds" in t else t for t in cfg["truths"])
leak = cfg["leak"]
if leak is not None:
    orig = m.grade
    def grade(*a, **k):
        out = orig(*a, **k)
        out["leak"] = leak
        return out
    m.grade = grade
if cfg["disable_guard"]:
    m.LeakGuard.check = lambda self, what, obj: None
sys.argv = ["fd_f0_regrade.py"] + cfg["argv"]
raise SystemExit(m.main(cfg["argv"]))
"""


def run_isolated(args, cwd=None, **kw):
    """``env -u PYTHONPATH <python> -I -B ...`` from a cwd outside nd-unfolding, as the declaration invokes it."""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    with tempfile.TemporaryDirectory(prefix="fd-f0-cwd-") as tmp:
        return subprocess.run([sys.executable, "-I", "-B", *args], cwd=cwd or tmp, env=env, capture_output=True,
                              text=True, timeout=600, **kw)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd-f0-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def tree(self, **kw):
        return Tree(self.tmp / "tree", **kw).write()

    def run_inproc(self, tree):
        with tree.patches()[0], tree.patches()[1], tree.patches()[2]:
            a = F.build_args(tree.argv)
            return F.run(a, tree.pins)

    def run_module(self, tree, leak=None, disable_guard=False):
        cfg = self.tmp / "cfg.json"
        cfg.write_text(json.dumps(tree.config(leak, disable_guard)))
        w = self.tmp / "wrapper.py"
        w.write_text(WRAPPER)
        return run_isolated([str(w), str(cfg)])

    def assertStops(self, tree, control):
        with self.assertRaises(SystemExit) as cm:
            self.run_inproc(tree)
        self.assertIn(f"FAIL control {control}:", str(cm.exception.code))
        self.assertFalse(any(tree.out.iterdir()), "a refused run wrote something")


# ------------------------------------------------------------------------------------------------ statistics


class Statistics(unittest.TestCase):
    def test_chi2_survival_is_exact_for_even_ndf(self):
        if _chi2 is None:
            self.skipTest("scipy not available")
        for ndf in (2, 8, 16):
            for x in (0.0, 0.5, 3.0, 7.9, 16.0, 20.09, 26.3, 32.0, 60.0, 200.0):
                self.assertAlmostEqual(F.chi2_sf_even(x, ndf), float(_chi2.sf(x, ndf)), delta=1e-12 + 1e-10 * _chi2.sf(x, ndf))
        self.assertAlmostEqual(F.chi2_sf_even(31.99992691, 16), 0.01, places=6)   # the 0.99 quantile of chi2_16
        with self.assertRaises(ValueError):
            F.chi2_sf_even(3.0, 7)

    def test_unweighted_mean_and_noise_of_the_mean(self):
        R = np.random.default_rng(1).normal(size=(20, 16))
        b, N, B = F.unweighted(R)
        np.testing.assert_allclose(b, R.mean(0), rtol=1e-14)
        Z = R - R.mean(0)
        np.testing.assert_allclose(N, Z.T @ Z / 19 / 20, rtol=1e-12)
        self.assertEqual(B, 20.0)

    def test_weighted_mean_is_the_ratio_estimator(self):
        rng = np.random.default_rng(2)
        R, w = rng.normal(size=(50, 16)), rng.uniform(0, 3, 50)
        b, N, Beff = F.weighted(R, w)
        want_b = (w[:, None] * R).sum(0) / w.sum()
        want_N = sum(wi ** 2 * np.outer(r - want_b, r - want_b) for wi, r in zip(w, R)) / w.sum() ** 2
        np.testing.assert_allclose(b, want_b, rtol=1e-13)
        np.testing.assert_allclose(N, want_N, rtol=1e-12)
        self.assertAlmostEqual(Beff, w.sum() ** 2 / (w ** 2).sum(), places=10)
        b1, N1, B1 = F.weighted(R, np.ones(50))
        np.testing.assert_allclose(N1, np.cov(R, rowvar=False, ddof=0) / 50, rtol=1e-12)
        self.assertAlmostEqual(B1, 50.0)

    def test_leave_out_and_grade(self):
        rng = np.random.default_rng(3)
        Ce = np.cov(rng.normal(size=(40, 16)), rowvar=False)
        S = rng.normal(size=(3, 16))
        np.testing.assert_allclose(F.leave_out(Ce, S, "nuwro"), Ce + np.outer(S[0], S[0]) + np.outer(S[2], S[2]), rtol=1e-13)
        np.testing.assert_allclose(F.leave_out(Ce, S, None), Ce + S.T @ S, rtol=1e-13)
        b, N = rng.normal(size=16), np.diag(rng.uniform(0.1, 1, 16))
        C = F.leave_out(Ce, S, "gibuu")
        g = F.grade(b, N, C)
        M = C + N
        self.assertAlmostEqual(g["chi2"], float(b @ np.linalg.solve(M, b)), places=9)
        np.testing.assert_allclose(g["z"], b / np.sqrt(np.diag(M)), rtol=1e-12)
        self.assertEqual(g["cells_abs_z_gt_2"], [f"R{c:02d}" for c in range(16) if abs(b[c] / np.sqrt(M[c, c])) > 2])
        g8 = F.grade(b, N, C, F.GIBUU_CELLS)
        idx = list(F.GIBUU_CELLS)
        self.assertEqual(g8["ndf"], 8)
        self.assertAlmostEqual(g8["chi2"], float(b[idx] @ np.linalg.solve(M[np.ix_(idx, idx)], b[idx])), places=9)
        big = F.grade(b * 1e3, N, C)
        self.assertEqual(big["p"], 0.0)
        self.assertTrue(big["p_below_floor"])
        self.assertTrue(big["p_lt_0.01"])


# ------------------------------------------------------------------------------------------------ the leak guard


class Guard(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(7)
        self.f = rng.uniform(4, 6, 16) * 1e-39
        self.Xt = rng.uniform(4, 6, (30, 16)) * 1e-39
        self.Xh = self.Xt * (1 + rng.normal(0, 0.01, (30, 16)))
        self.g = F.LeakGuard(self.f, [self.Xh, self.Xt])
        self.r = self.Xh / self.Xt - 1

    def test_silent_on_relative_outputs(self):
        self.assertEqual(self.g.count({"bias": self.r.mean(0).tolist(), "z": (self.r.mean(0) / 0.01).tolist(),
                                       "chi2": 17.2, "p": 0.37, "table": self.r, "line": "PASS control 6 3.2e-05"}), 0)

    def test_refuses_every_form_of_f_and_of_an_absolute_value(self):
        f, X = self.f, self.Xt[4]
        for what, v in (("f", f), ("an absolute integral", X), ("f - g", f - X), ("g - f", X - f),
                        ("f/g", f / X), ("g/f", X / f), ("f/g - 1", f / X - 1), ("g/f - 1", X / f - 1),
                        ("(f - g)/f = 1 - g/f", 1 - X / f), ("1 - f/g", 1 - f / X), ("-f/g", -f / X)):
            self.assertEqual(self.g.count({"v": v.tolist()}), 16, what)          # a cell-indexed vector
            self.assertEqual(self.g.count({"v": float(v[5])}), 1, what)          # a scalar
            self.assertGreater(self.g.count(f"note {float(v[5])!r}"), 0, what)  # inside a printed line
            arr = self.r.copy()
            arr[3] = v
            self.assertEqual(self.g.count({"r": arr}), 16, what)                 # a row of the table

    def test_any_absolute_magnitude_is_refused_even_if_unlisted(self):
        self.assertEqual(self.g.count([3.3e-41]), 1)
        self.assertEqual(self.g.count({"sigma_abs": (0.06 * self.f).tolist()}), 16)
        self.assertEqual(self.g.count([0.0, 1e-30, 2.5]), 0)

    def test_check_exits_3(self):
        with self.assertRaises(SystemExit) as cm:
            self.g.check("x", {"x": self.f.tolist()})
        self.assertEqual(cm.exception.code, 3)


# ------------------------------------------------------------------------------------------------ end to end


class EndToEnd(Base):
    def forbidden(self, tree):
        f, X = tree.f, tree.integrals()
        with np.errstate(divide="ignore"):
            V = np.concatenate([f, X.ravel(), (f - X).ravel(), (X - f).ravel(), (f / X).ravel(), (X / f).ravel(), (f / X - 1).ravel(),
                                (X / f - 1).ravel()])
        V = np.abs(V)        # either sign: 1 - X/f is (f - g)/f
        return np.sort(V[V != 0])

    def leaks(self, values, forbidden):
        a = np.abs(np.asarray([v for v in values if v != 0], float))
        if not a.size:
            return []
        i = np.clip(np.searchsorted(forbidden, a), 1, forbidden.size - 1)
        near = np.minimum(np.abs(a - forbidden[i - 1]) / np.abs(forbidden[i - 1]), np.abs(a - forbidden[i]) / np.abs(forbidden[i]))
        return list(a[(near < 1e-12) | (np.abs(a) < 1e-30)])

    def numbers(self, obj):
        if isinstance(obj, dict):
            return [x for k, v in obj.items() for x in self.numbers(k) + self.numbers(v)]
        if isinstance(obj, list):
            return [x for v in obj for x in self.numbers(v)]
        if isinstance(obj, bool) or obj is None:
            return []
        if isinstance(obj, (int, float)):
            return [float(obj)]
        if isinstance(obj, str):
            return [float(t) for t in F._NUM.findall(obj)]
        return []

    def check_run(self, tree):
        r = self.run_module(tree)
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        self.assertNotIn("ModuleNotFoundError", r.stderr)
        js = tree.out / "readout.json"
        readout = json.loads(js.read_text())
        forb = self.forbidden(tree)
        self.assertEqual(self.leaks(self.numbers(r.stdout) + self.numbers(r.stderr), forb), [], "stdout/stderr")
        self.assertEqual(self.leaks(self.numbers(readout), forb), [], "readout")
        with np.load(tree.out / "table.npz") as z:
            for k in z.files:
                if z[k].dtype.kind == "f":
                    self.assertEqual(self.leaks(z[k].ravel().tolist(), forb), [], k)
        self.assertEqual(sorted(p.name for p in tree.out.iterdir()), ["readout.json", "table.npz"])
        return r, readout

    def test_a_run_prints_no_f_no_absolute_value_and_no_f_minus_g(self):
        tree = self.tree()
        r, readout = self.check_run(tree)
        for c in (0, 1, 2, 3, 4, 5, 6, 7, 8):
            self.assertIn(f"PASS control {c} ", r.stdout)
        self.assertEqual(readout["schema"], "fd-f0-readout/1")
        self.assertEqual(readout["controls"]["passed"], [0, 1, 2, 3, 4, 5, 6, 8])
        self.assertTrue(readout["controls"]["offset_control_7"]["pass"])
        self.assertEqual(len(readout["truths"]), 18)
        tot = readout["triggers"]["all_graded"]
        self.assertEqual((tot["truths"], tot["cells"]), (18, 288))
        self.assertAlmostEqual(tot["gaussian_reference_cells"], 288 * 0.0455002638963584, places=9)
        self.assertAlmostEqual(tot["gaussian_reference_truths"], 0.18, places=12)
        by = readout["triggers"]["by_group"]
        self.assertEqual({k: v["truths"] for k, v in by.items()}, {"vertex-family": 14, "non-vertex": 2, "prior": 2})
        self.assertEqual({k: v["truths"] for k, v in by["vertex-family"]["by_family"].items()},
                         {"nuwro": 8, "genie_mec": 4, "gibuu": 2})
        self.assertEqual(sorted(json.loads(r.stdout.strip().splitlines()[-1])), ["readout_sha256", "table_sha256", "wrote"])
        self.assertEqual(readout["table_sha256"], digest(tree.out / "table.npz"))
        names = {"f", "x", "X", "x_true", "xtrue", "f_minus_g", "data"}
        self.assertFalse(names & set(readout))
        self.assertFalse(any(names & set(t) for t in readout["truths"]))

    def test_o1_units_rely_on_the_exact_match_not_the_floor(self):
        self.check_run(self.tree(scale=1.0, seed=5))

    def test_planted_leaks_are_refused_and_nothing_is_written(self):
        tree = self.tree()
        Xt = tree.products["W1"][1][2]
        X = tree.U @ tree.arrays(Xt, tree.products["W1"][1][3])[1]
        for what, v in (("f", tree.f.tolist()), ("one cell of f", float(tree.f[7])), ("an absolute value", X.tolist()),
                        ("f - g", (tree.f - X).tolist()), ("f/g - 1", (tree.f / X - 1).tolist()),
                        ("(f - g)/f", (1 - X / tree.f).tolist()),
                        ("f/g - 1 in one cell", float(tree.f[2] / X[2] - 1))):
            r = self.run_module(tree, leak=v)
            self.assertEqual(r.returncode, 3, (what, r.stderr[-2000:]))
            self.assertIn("REFUSED leak guard", r.stderr)
            self.assertEqual(list(tree.out.iterdir()), [], what)

    def test_negative_control_without_the_guard_the_leak_is_written_and_this_scan_finds_it(self):
        tree = self.tree()
        Xt = tree.products["A7_gibuu"][0][2]
        X = tree.U @ tree.arrays(Xt, tree.products["A7_gibuu"][0][3])[1]
        r = self.run_module(tree, leak=(tree.f / X - 1).tolist(), disable_guard=True)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        readout = json.loads((tree.out / "readout.json").read_text())
        self.assertGreaterEqual(len(self.leaks(self.numbers(readout), self.forbidden(tree))), 16)

    def test_grades_recomputed_by_hand(self):
        tree = self.tree(seed=11)
        with tree.patches()[0], tree.patches()[1], tree.patches()[2]:
            self.assertEqual(F.run(F.build_args(tree.argv), tree.pins), 0)
        readout = json.loads((tree.out / "readout.json").read_text())
        T = {t["name"]: t for t in readout["truths"]}
        ff = np.outer(tree.f, tree.f)
        Ce_rel, S = tree.Ce / ff, tree.S
        keep = lambda own: [j for j, v in enumerate(F.VERTICES) if v != own]  # noqa: E731
        R = {k: np.array([tree.rel(i) for i in v]) for k, v in tree.products.items()}
        w = tree.weights

        def wmean(Rk, flux):
            ww = w[flux]
            b = (ww[:, None] * Rk).sum(0) / ww.sum()
            Z = Rk - b
            return b, (Z.T * ww ** 2) @ Z / ww.sum() ** 2

        flux = {k: np.array([m["nuisance_draw"]["flux"] for _, m, *_ in v]) for k, v in tree.products.items()
                if v[0][1].get("nuisance_draw")}
        for name in ("W1", "q3", "A7_genie_cv", "A7_gibuu", "closure_nuwro", "P2g"):
            t = next(x for x in tree.truths if x["name"] == name)
            if t["row"] == 3:
                b, N = R[name][0], np.zeros((16, 16))
            elif t["row"] == 6:
                bw, Nw = wmean(R[name], flux[name])
                bc, Nc = wmean(R["cal:" + t["ref"]], flux["cal:" + t["ref"]])
                b4 = R[t["ref"]].mean(0)
                N4 = np.cov(R[t["ref"]], rowvar=False) / SMALL
                b, N = bw - (bc - b4), Nw + Nc + N4
            else:
                b, N = R[name].mean(0), np.cov(R[name], rowvar=False) / len(R[name])
            C = Ce_rel + S[keep(t["own"])].T @ S[keep(t["own"])]
            M = C + N
            np.testing.assert_allclose(T[name]["bias"], b, rtol=1e-9, atol=1e-15, err_msg=name)
            np.testing.assert_allclose(T[name]["grade"]["z"], b / np.sqrt(np.diag(M)), rtol=1e-8, err_msg=name)
            self.assertAlmostEqual(T[name]["grade"]["chi2"], float(b @ np.linalg.solve(M, b)), delta=1e-7 * T[name]["grade"]["chi2"])
            Cm = tree.blocks["stat"] / ff + S[keep(t["own"])].T @ S[keep(t["own"])]
            self.assertAlmostEqual(T[name]["model_only"]["chi2"], float(b @ np.linalg.solve(Cm + N, b)),
                                   delta=1e-7 * T[name]["model_only"]["chi2"])
            self.assertEqual("in_sample" in T[name], t["own"] is not None)
            self.assertEqual("p_parallel_lt_4p5" in T[name], t["own"] == "gibuu")
        self.assertEqual(T["q3"]["sensitivity"]["matrix"], "C_total minus nuwro")
        self.assertEqual(T["A7_genie_cv"]["sensitivity"]["matrix"], "C_total minus genie_mec")
        self.assertEqual(T["closure_nuwro"]["noise_sigma"], [0.0] * 16)
        # the offset control: O_MnvTune - O_GENIE CV against the sum of their noises
        O, NO = {}, {}
        for g in F.OFFSET_PAIR:
            bc, Nc = wmean(R["cal:" + g], flux["cal:" + g])
            O[g], NO[g] = bc - R[g].mean(0), Nc + np.cov(R[g], rowvar=False) / SMALL
        D = O["A7_mnvtune"] - O["A7_genie_cv"]
        oc = readout["controls"]["offset_control_7"]
        self.assertAlmostEqual(oc["chi2"], float(D @ np.linalg.solve(NO["A7_mnvtune"] + NO["A7_genie_cv"], D)), delta=1e-7 * oc["chi2"])
        self.assertEqual(len(oc["pairs_descriptive"]), 9)
        for g in [t["name"] for t in tree.truths if t["row"] == 4]:
            bc, Nc = wmean(R["cal:" + g], flux["cal:" + g])
            N4 = np.cov(R[g], rowvar=False) / SMALL
            self.assertAlmostEqual(oc["row4_noise_trace_share"][g], float(np.trace(N4) / np.trace(Nc + N4)), places=10)

    def test_a_failed_offset_control_leaves_row_6_ungraded(self):
        tree = self.tree(offset_shift=0.05)
        with tree.patches()[0], tree.patches()[1], tree.patches()[2]:
            self.assertEqual(F.run(F.build_args(tree.argv), tree.pins), 0)
        readout = json.loads((tree.out / "readout.json").read_text())
        self.assertFalse(readout["controls"]["offset_control_7"]["pass"])
        row6 = [t for t in readout["truths"] if t["row"] == 6]
        self.assertTrue(row6 and all(not t["graded"] and not t["listed"] and "offset control failed" in t["label"] for t in row6))
        tot = readout["triggers"]["all_graded"]
        self.assertEqual((tot["truths"], tot["cells"]), (12, 192))
        self.assertEqual(readout["triggers"]["by_group"]["vertex-family"]["truths"], 8)

    def test_refuses_to_overwrite(self):
        tree = self.tree()
        (tree.out / "readout.json").write_text("{}")
        with self.assertRaises(SystemExit):
            self.run_inproc(tree)


# ------------------------------------------------------------------------------------------------ controls 0-8


class Controls(Base):
    def resave(self, tree, name, i, **meta):
        tree.products[name][i][1] = {**tree.products[name][i][1], **meta}

    def test_control_0_f4_digest_before_anything_else(self):
        tree = self.tree()
        p = tree.products["A7_nuwro"][1][0]
        np.savez_compressed(p, xsec_flat=np.zeros(N), xtrue_flat=np.zeros(N), meta="{}")
        tree.argv[tree.argv.index("--s1-npz") + 1] = str(self.tmp / "absent.npz")   # control 0 must stop first
        self.assertStops(tree, 0)

    def test_control_0_unlisted_f4_product(self):
        tree = self.tree()
        shutil.copy(tree.products["A7_gibuu"][0][0], tree.f4root / "gibuu_cv_half" / "f4_gibuu_cv_half_s970099.npz")
        self.assertStops(tree, 0)

    def test_control_0_d16_record_pin(self):
        tree = self.tree()
        tree.pins["d16"]["genie_mec"] = "0" * 64
        self.assertStops(tree, 0)

    def test_control_1_product_digest(self):
        tree = self.tree()
        p = tree.products["cal:A7_genie_mec"][4][0]
        np.savez_compressed(p, xsec_flat=np.ones(N), xtrue_flat=np.ones(N), meta="{}")
        self.assertStops(tree, 1)

    def test_control_1_unlisted_product(self):
        tree = self.tree()
        shutil.copy(tree.products["W2"][0][0], tree.s5e / "W2" / "x_s804099.npz")
        self.assertStops(tree, 1)

    def test_control_1_record_pins(self):
        for key in ("s1_npz", "cmodel_json", "s5p_sums", "closure", "floor"):
            tree = self.tree()
            tree.pins[key] = "f" * 64
            self.assertStops(tree, 1)

    def test_control_2_meta(self):
        bad = [("W3", {"estimator_params": [dict(EST[0], n_estimators=200)] * 3}),
               ("nominal", {"config": "R"}),
               ("q3", {"amplitude": 1.0}),
               ("stage0c_gibuu", {"eavail_ratio_sha256": F.RATIO["W1"]}),
               ("A7_genie_cv", {"hypothesis": {"sha256": F.HYP["genie_mec"]}}),
               ("A7_mnvtune", {"development": {"expectation": False, "mc_fraction": "half"}}),
               ("cal:A7_nuwro", {"refinement": {"ran": True, "classifier_params": dict(REF["classifier_params"], random_state=42)}}),
               ("cal:A7_gibuu", {"nuisance_draw": {"flux": 100}}),
               ("P3g", {"alternative": {"truth": "ratio_nd", "amplitude": 1.0, "sha256": F.ALT["P1"][1]}}),
               ("P1r", {"code_sha256": dict(CODE, **{"s5p_nullexp.py": F.NULLEXP_F4[0]})}),
               ("closure_nuwro", {"refinement": REF}),
               ("W1", {"pseudo_seed": 803001}),
               ("cal:A7_mnvtune", {"estimator_seed": 42}),
               ("A7_nuwro", {"estimator_seed": 45})]
        for name, change in bad:
            tree = Tree(self.tmp / f"t-{name.replace(':', '_')}")
            self.resave(tree, name, 0, **change)
            tree.write()
            self.assertStops(tree, 2)
        for name in ("W2", "closure_nuwro"):     # producers that do record estimator_seed must carry it
            tree = Tree(self.tmp / f"t-noseed-{name}")
            tree.products[name][0][1].pop("estimator_seed")
            tree.write()
            self.assertStops(tree, 2)

    def test_control_2_array_length_and_dtype(self):
        for xs in (np.ones(N - 1), np.ones(N, np.float32)):
            tree = Tree(self.tmp / f"t2-{xs.size}-{xs.dtype}").write_products()
            p, meta, *_ = tree.products["P2r"][0]
            np.savez_compressed(p, xsec_flat=xs, xtrue_flat=np.ones(N), meta=json.dumps(meta))
            tree.write_records()
            self.assertStops(tree, 2)

    def test_control_3_counts(self):
        tree = self.tree()
        counts = small_counts()
        counts["cal"]["NuWro_21_09"] = N_CAL + 1
        with mock.patch.object(F, "TRUTHS", tree.truths), mock.patch.object(F, "COUNTS", counts), \
                mock.patch.object(sa, "CONSTRAINT_SHA256", tree.constraint_sha), self.assertRaises(SystemExit) as cm:
            F.run(F.build_args(tree.argv), tree.pins)
        self.assertIn("FAIL control 3:", str(cm.exception.code))

    def test_control_4_matrices(self):
        for mutate in ("block", "S", "table", "C_model_abs", "f", "sigma_json", "U"):
            tree = Tree(self.tmp / f"t4-{mutate}")
            if mutate == "block":
                tree.blocks["seed"] = tree.blocks["seed"] * 1.5
            if mutate == "C_model_abs":
                tree.Cma = tree.Cma * (1 + 1e-9)
            tree.write()
            if mutate in ("f", "U", "sigma_json"):
                s1n = Path(tree.argv[tree.argv.index("--s1-npz") + 1])
                s1j = Path(tree.argv[tree.argv.index("--s1-json") + 1])
                with np.load(s1n) as z:
                    d = {k: z[k] for k in z.files}
                if mutate == "f":
                    d["f"] = d["f"].copy()
                    d["f"][3] = -d["f"][3]
                if mutate == "U":
                    d["U"] = d["U"].copy()
                    d["U"][2, np.flatnonzero(d["U"][2])[0]] *= 2
                if mutate != "sigma_json":
                    np.savez_compressed(s1n, **d)
                j = json.loads(s1j.read_text())
                j["assembly_sha256"] = digest(s1n)
                if mutate == "sigma_json":
                    j["relative_sigma"]["C_total"][7] *= 1 + 1e-9
                s1j.write_text(json.dumps(j))
                tree.pins["s1_npz"], tree.pins["s1_json"] = digest(s1n), digest(s1j)
            if mutate == "S":
                cj = Path(tree.argv[tree.argv.index("--cmodel-json") + 1])
                d = json.loads(cj.read_text())
                d["S"][1][3] *= 1 + 1e-12
                cj.write_text(json.dumps(d))
                tree.pins["cmodel_json"] = digest(cj)
            if mutate == "table":
                tree.pins["table_2_1"] = dict(tree.pins["table_2_1"], minus_gibuu=(0.0, 0.0, 0.0))
            self.assertStops(tree, 4)

    def test_control_5_closure_bias(self):
        tree = self.tree()
        cj = Path(tree.argv[tree.argv.index("--cmodel-json") + 1])
        d = json.loads(cj.read_text())
        d["positive_control"]["reporting16"]["bias_cells"][9] += 1e-9
        cj.write_text(json.dumps(d))
        tree.pins["cmodel_json"] = digest(cj)
        self.assertStops(tree, 5)

    def test_control_6_floor(self):
        tree = self.tree()
        tree.pins["floor_max_abs"] += 1e-9
        self.assertStops(tree, 6)

    def test_control_8_truth_integral(self):
        tree = Tree(self.tmp / "t8")
        tree.products["P1g"][1][2][5] = -abs(tree.products["P1g"][1][2][5])
        tree.write()
        self.assertStops(tree, 8)


# ------------------------------------------------------------------------------------------------ F0b: the extra block


class ExtraBlockF0b(Base):
    """F0b (FD-F0b-DECLARATION.md): a declared covariance, pinned by digest, added to every matrix that carries C_e.
    Shown in both directions: with the block, every such grade is recomputed here against C + C_x and everything else
    equals F0's run on the same tree; without it, the readout is F0's, key for key against the committed F0 readout."""
    forbidden, leaks, numbers = EndToEnd.forbidden, EndToEnd.leaks, EndToEnd.numbers    # the test's own leak scan

    @staticmethod
    def resp(tree, seed=9):
        v = np.random.default_rng(seed).normal(0, 0.03, (4, F.N_CELLS)) * tree.f
        return v.T @ v

    @staticmethod
    def block(tree, C, key="C_resp", name="cresp"):
        p = tree.root / f"{name}.npz"
        np.savez(p, **{key: C})
        return ["--extra-block", str(p), "--extra-block-sha256", digest(p), "--extra-block-key", key,
                "--extra-block-name", "C_resp"]

    @staticmethod
    def argv_to(tree, extra, sub):
        """The tree's argv with ``extra`` before the outputs, writing to tree.root/<sub>."""
        out = tree.root / sub
        out.mkdir()
        return tree.argv[:-4] + extra + ["--out-json", str(out / "readout.json"), "--out-npz", str(out / "table.npz")], out

    def run_pair(self, tree, Cx):
        """F0 and F0b on the same tree; returns both readouts."""
        got = []
        for sub, extra in (("f0", []), ("f0b", self.block(tree, Cx))):
            argv, out = self.argv_to(tree, extra, sub)
            with tree.patches()[0], tree.patches()[1], tree.patches()[2]:
                self.assertEqual(F.run(F.build_args(argv), tree.pins), 0)
            got.append(json.loads((out / "readout.json").read_text()))
        return got

    def test_grades_recomputed_by_hand_and_everything_else_is_f0s(self):
        tree = self.tree(seed=11)
        Cx = self.resp(tree)
        f0, f0b = self.run_pair(tree, Cx)
        ff = np.outer(tree.f, tree.f)
        Ce_rel, S, Cx_rel = tree.Ce / ff, tree.S, Cx / ff
        keep = lambda own: [j for j, v in enumerate(F.VERTICES) if v != own]  # noqa: E731
        self.assertEqual((f0["schema"], f0b["schema"]), ("fd-f0-readout/1", "fd-f0b-readout/1"))
        self.assertEqual(f0b["extra_block"]["name"], "C_resp")
        np.testing.assert_allclose(f0b["extra_block"]["relative_sigma"], np.sqrt(np.diag(Cx_rel)), rtol=1e-12)
        self.assertEqual(f0b["labels"]["what"], f0["labels"]["what"] + " plus C_resp (F0b)")
        self.assertEqual(f0b["labels"]["grade_matrix"],
                         "F0b: C^(T) + C_resp, with the leave-out on C_model only; the in-sample, sensitivity and "
                         "eight-cell matrices also carry C_resp; the model-only matrix, with no C_e, is F0's")
        want = {"C_e": Ce_rel + Cx_rel}
        want.update({k: Ce_rel + S[keep(own)].T @ S[keep(own)] + Cx_rel
                     for k, own in (("C_total", None), *((f"minus_{v}", v) for v in F.VERTICES))})
        self.assertEqual(sorted(f0b["relative_sigma_plus_C_resp"]), sorted(want))
        for k, M in want.items():
            sig = np.sqrt(np.diag(M))
            np.testing.assert_allclose(f0b["relative_sigma_plus_C_resp"][k], sig, rtol=1e-10, err_msg=k)
            self.assertEqual(f0b["relative_sigma_plus_C_resp_summary_percent"][k],
                             [round(100 * float(v), 2) for v in (np.median(sig), sig.min(), sig.max())], k)
        self.assertEqual(f0b["relative_sigma"], f0["relative_sigma"])             # F0's sigma table is unchanged
        self.assertEqual(f0b["controls"], f0["controls"])                         # control 7 included: noise only
        A, B = {t["name"]: t for t in f0["truths"]}, {t["name"]: t for t in f0b["truths"]}
        counts = {}
        for t in tree.truths:
            a, b = A[t["name"]], B[t["name"]]
            for k in ("bias", "noise_sigma", "B_eff", "estimator", "graded", "group", "own_vertex", "model_only"):
                self.assertEqual(a[k], b[k], (t["name"], k))                      # model-only: no C_e, no C_resp
            self.assertEqual(b["grade_matrix"], a["grade_matrix"] + " + C_resp")
            bb = np.asarray(b["bias"])
            N = np.diag(np.asarray(b["noise_sigma"]) ** 2)                        # only the diagonal is published
            for key, C in [("grade", Ce_rel + S[keep(t["own"])].T @ S[keep(t["own"])] + Cx_rel)] + \
                    ([("in_sample", Ce_rel + S.T @ S + Cx_rel)] if t["own"] else []) + \
                    ([("sensitivity", Ce_rel + S[keep(t["sens"])].T @ S[keep(t["sens"])] + Cx_rel)] if t.get("sens") else []):
                g = b[key]
                # z needs only diag(C + N); the chi2, which needs the full noise matrix, is test_chi2_against_the_full_matrix
                np.testing.assert_allclose(g["z"], bb / np.sqrt(np.diag(C) + np.diag(N)), rtol=1e-8, err_msg=(t["name"], key))
                self.assertEqual(g["cells_abs_z_gt_2"], [f"R{c:02d}" for c in range(16) if abs(g["z"][c]) > 2])
                self.assertEqual(g["p_lt_0.01"], g["p"] < 0.01 or g["p_below_floor"])
            if t.get("sens"):
                self.assertEqual(b["sensitivity"]["matrix"], f"C_total minus {t['sens']} + C_resp")
            if t["own"] == "gibuu":
                Cg = Ce_rel + S[keep("gibuu")].T @ S[keep("gibuu")] + Cx_rel
                i = list(F.GIBUU_CELLS)
                np.testing.assert_allclose(b["p_parallel_lt_4p5"]["z"], bb[i] / np.sqrt(np.diag(Cg)[i] + np.diag(N)[i]), rtol=1e-8)
            if b["graded"]:
                c = counts.setdefault(t["group"], [0, 0])
                c[0] += len(b["grade"]["cells_abs_z_gt_2"])
                c[1] += int(b["grade"]["p_lt_0.01"])
        by = f0b["triggers"]["by_group"]
        self.assertEqual({k: [v["cells_abs_z_gt_2"], v["truths_p_lt_0.01"]] for k, v in by.items()}, counts)
        self.assertEqual({k: (v["truths"], v["cells"]) for k, v in by.items()},
                         {k: (v["truths"], v["cells"]) for k, v in f0["triggers"]["by_group"].items()})   # denominators

    def test_chi2_against_the_full_matrix(self):
        """The noise matrix is internal, so the chi2 is recomputed from the products: the same estimator as
        EndToEnd.test_grades_recomputed_by_hand, with C_resp added."""
        tree = self.tree(seed=11)
        Cx = self.resp(tree)
        _, f0b = self.run_pair(tree, Cx)
        T = {t["name"]: t for t in f0b["truths"]}
        ff = np.outer(tree.f, tree.f)
        Ce_rel, S, Cx_rel = tree.Ce / ff, tree.S, Cx / ff
        keep = lambda own: [j for j, v in enumerate(F.VERTICES) if v != own]  # noqa: E731
        R = {k: np.array([tree.rel(i) for i in v]) for k, v in tree.products.items()}
        for name in ("W1", "q3", "A7_genie_cv", "A7_gibuu", "closure_nuwro", "nominal"):
            t = next(x for x in tree.truths if x["name"] == name)
            if t["row"] == 3:
                b, N = R[name][0], np.zeros((16, 16))
            else:
                b, N = R[name].mean(0), np.cov(R[name], rowvar=False) / len(R[name])
            C = Ce_rel + S[keep(t["own"])].T @ S[keep(t["own"])] + Cx_rel
            x2 = float(b @ np.linalg.solve(C + N, b))
            self.assertAlmostEqual(T[name]["grade"]["chi2"], x2, delta=1e-7 * x2, msg=name)
            sf = F.chi2_sf_even(T[name]["grade"]["chi2"], 16)
            self.assertEqual(T[name]["grade"]["p"], sf if sf >= F.P_FLOOR else 0.0)
            Cm = tree.blocks["stat"] / ff + S[keep(t["own"])].T @ S[keep(t["own"])]
            xm = float(b @ np.linalg.solve(Cm + N, b))
            self.assertAlmostEqual(T[name]["model_only"]["chi2"], xm, delta=1e-7 * xm, msg=name)

    def test_a_zero_block_reproduces_f0_and_a_psd_block_only_lowers_grades(self):
        tree = self.tree(seed=3)
        f0, z0 = self.run_pair(tree, np.zeros((16, 16)))
        drop = lambda d: None if d is None else {k: v for k, v in d.items() if k != "matrix"}  # noqa: E731  (the name)
        for a, b in zip(f0["truths"], z0["truths"]):
            for k in ("grade", "model_only", "in_sample", "sensitivity", "p_parallel_lt_4p5"):
                self.assertEqual(drop(a.get(k)), drop(b.get(k)), (a["name"], k))
        self.assertEqual(f0["triggers"]["by_group"], z0["triggers"]["by_group"])
        tree2 = self.tree(seed=3)
        f0, f0b = self.run_pair(tree2, self.resp(tree2))
        for a, b in zip(f0["truths"], f0b["truths"]):
            self.assertLessEqual(b["grade"]["chi2"], a["grade"]["chi2"] * (1 + 1e-12), a["name"])  # PSD addition
            self.assertTrue(all(abs(zb) <= abs(za) * (1 + 1e-12) for za, zb in zip(a["grade"]["z"], b["grade"]["z"])))
            self.assertNotEqual(a["grade"]["chi2"], b["grade"]["chi2"])

    def test_without_the_option_the_readout_is_f0s_key_for_key(self):
        tree = self.tree(offset_shift=0.05)          # control 7 fails, as it did in the real F0 run
        f0, _ = self.run_pair(tree, self.resp(tree))
        real = json.loads((FD / "fd/readout/fd_f0_readout.json").read_text())
        self.assertEqual(sorted(f0), sorted(real))
        self.assertEqual(sorted(f0["labels"]), sorted(real["labels"]))
        self.assertEqual(f0["labels"]["what"], real["labels"]["what"])
        self.assertEqual(sorted(f0["controls"]), sorted(real["controls"]))
        RT = {t["name"]: t for t in real["truths"]}
        for t in f0["truths"]:
            self.assertEqual(sorted(t), sorted(RT[t["name"]]), t["name"])
            self.assertEqual(t["grade_matrix"], RT[t["name"]]["grade_matrix"], t["name"])
            for k in ("sensitivity",):
                if k in t:
                    self.assertEqual(t[k]["matrix"], RT[t["name"]][k]["matrix"])

    def test_stdout_with_and_without(self):
        tree = self.tree()
        for sub, extra, first in (("a", [], "[F0] non-vertex:"), ("b", self.block(tree, self.resp(tree)),
                                                                   "[F0] F0b: every grade matrix carries C_resp")):
            argv, out = self.argv_to(tree, extra, sub)
            cfg = self.tmp / f"cfg-{sub}.json"
            c = tree.config()
            c["argv"] = argv
            cfg.write_text(json.dumps(c))
            w = self.tmp / "wrapper.py"
            w.write_text(WRAPPER)
            r = run_isolated([str(w), str(cfg)])
            self.assertEqual(r.returncode, 0, r.stderr[-3000:])
            lines = [ln for ln in r.stdout.splitlines() if ln.startswith("[F0]")]
            self.assertTrue(lines[0].startswith(first), lines[0])
            self.assertEqual(len(lines), 4 + bool(extra))                   # three groups and the denominators
            self.assertIn(f"products and {8 + bool(extra)} records match", r.stdout)
            readout = json.loads((out / "readout.json").read_text())
            fb = self.forbidden(tree)                                           # the guard holds with the block
            self.assertEqual(self.leaks(self.numbers(readout) + self.numbers(r.stdout), fb), [])

    def test_a_planted_leak_is_refused_with_the_block(self):
        tree = self.tree()
        argv, out = self.argv_to(tree, self.block(tree, self.resp(tree)), "b")
        c = tree.config(leak=tree.f.tolist())
        c["argv"] = argv
        cfg = self.tmp / "cfg.json"
        cfg.write_text(json.dumps(c))
        (self.tmp / "wrapper.py").write_text(WRAPPER)
        r = run_isolated([str(self.tmp / "wrapper.py"), str(cfg)])
        self.assertEqual(r.returncode, 3, r.stderr[-2000:])
        self.assertEqual(list(out.iterdir()), [])

    def test_refusals(self):
        tree = self.tree()
        Cx = self.resp(tree)
        cases = {}
        e = self.block(tree, Cx, name="sha")
        e[3] = "a" * 64
        cases["1 digest"] = (e, "extra block")
        notpsd = Cx.copy()
        notpsd[0, 0] = -abs(Cx[0, 0])
        anti = np.triu(np.full((16, 16), 1e-3 * Cx.max()), 1)
        asym_psd = Cx + anti - anti.T                          # asymmetric, and PSD once symmetrized: only the
        self.assertGreaterEqual(np.linalg.eigvalsh((asym_psd + asym_psd.T) / 2 / np.outer(tree.f, tree.f)).min(),
                                -1e-12)                        # symmetry check can refuse it
        for k, (what, C, check) in enumerate((("asymmetric", asym_psd, "is symmetric"),
                                              ("not PSD", notpsd, "is positive semidefinite"),
                                              ("shape", Cx[:15, :15], "is a finite 16 x 16 matrix"),
                                              ("non-finite", np.where(np.eye(16) > 0, np.nan, Cx),
                                               "is a finite 16 x 16 matrix"))):
            cases[f"4 {what}"] = (self.block(tree, C, name=f"case{k}"), f"C_resp {check}")
        e = self.block(tree, Cx, key="other", name="case-key")
        e[e.index("--extra-block-key") + 1] = "C_resp"
        cases["4 key"] = (e, "no key 'C_resp'")
        for what, (e, check) in cases.items():
            argv, out = self.argv_to(tree, e, what.replace(" ", "-"))
            with tree.patches()[0], tree.patches()[1], tree.patches()[2], self.assertRaises(SystemExit, msg=what) as cm:
                F.run(F.build_args(argv), tree.pins)
            self.assertIn(f"FAIL control {what.split()[0]}:", str(cm.exception.code), what)
            self.assertIn(check, str(cm.exception.code), what)                 # the check that refused, by name
            self.assertEqual(list(out.iterdir()), [], what)

    def test_the_four_options_go_together(self):
        tree = self.tree()
        e = self.block(tree, self.resp(tree))
        parts = [(f"all but {e[i]}", e[:i] + e[i + 2:]) for i in range(0, 8, 2)] + [("name only", e[6:])]
        self.assertEqual(len(parts), 5)
        for what, part in parts:
            with self.assertRaises(SystemExit, msg=what) as cm, mock.patch("sys.stderr"):
                F.build_args(tree.argv + part)
            self.assertEqual(cm.exception.code, 2, what)
        self.assertEqual(F.build_args(tree.argv + e).extra_block_name, "C_resp")


# ------------------------------------------------------------------------------------------------ as invoked


class Invocation(Base):
    def test_help_under_isolation(self):
        r = run_isolated([str(ND / "fd_f0_regrade.py"), "--help"])
        self.assertNotIn("ModuleNotFoundError", r.stderr)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("usage:", r.stdout)

    def test_argparse_error_is_not_an_import_error(self):
        r = run_isolated([str(ND / "fd_f0_regrade.py")])
        self.assertNotIn("ModuleNotFoundError", r.stderr)
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_the_real_script_reaches_control_0_and_refuses_synthetic_records(self):
        tree = self.tree()
        r = run_isolated([str(ND / "fd_f0_regrade.py"), *tree.argv])
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("FAIL control 0:", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(list(tree.out.iterdir()), [])


# ------------------------------------------------------------------------------------------------ the committed pins


class CommittedPins(unittest.TestCase):
    def test_truth_identity_digests_are_the_committed_files(self):
        files = {F.HYP["mnvtune_v1"]: "s5p/ratios/nullsJ/null-mnvtune_v1-J.json",
                 **{F.HYP[k]: f"s5p/ratios/nullsF/null-{k}-F.json" for k in ("genie_cv", "genie_mec", "nuwro_cv", "gibuu_cv")},
                 F.ALT["P1"][1]: "s5p/ratios/altR/p1r-w3-nuwro-over-genie-pt-pz-eavail.json",
                 F.ALT["P2"][1]: "s5p/ratios/altR/p2r-d5-nuwro-over-genie-q3-given-eavail-w.json",
                 F.ALT["P3"][1]: "s5p/ratios/altR/p3r-w2-genie-mec-over-cv-eavailW.json",
                 F.RATIO["W1"]: "s5n/eavail-ratio-nuwro-over-genie.json",
                 F.RATIO["W2"]: "s5e/w2-genie-mec-over-cv-eavailW.json",
                 F.RATIO["W3"]: "s5e/w3-nuwro-over-genie-pt-pz-eavail.json",
                 F.RATIO["gibuu"]: "measurement-paper/5d-design-20261023/stage0/receipts-A/eavail-ratio-gibuu-over-genie-fluxfix.json"}
        for sha, rel in files.items():
            self.assertEqual(digest(STATE / rel), sha, rel)
        prep = dict(ln.split()[::-1] for ln in (ND / "pv-ladder/prep-SHA256SUMS").read_text().splitlines() if ln.strip())
        self.assertEqual(prep["./ratios/L-5D-PV/nuwro.json"], F.RATIO["closure_nuwro"])
        self.assertEqual(prep["./ratios/L-5D-PV/tune_v1.json"], F.RATIO["floor"])

    def test_record_pins(self):
        P = F.PINS
        self.assertEqual(digest(FD / "s1/readout/s1_assembly.json"), P["s1_json"])
        self.assertEqual(json.loads((FD / "s1/readout/s1_assembly.json").read_text())["assembly_sha256"], P["s1_npz"])
        cj = ND / "pv-ladder/readouts/cmodel_5d.json"
        self.assertEqual(digest(cj), P["cmodel_json"])
        c = json.loads(cj.read_text())
        self.assertEqual(c["inputs"]["products_sha256"]["L-5D-PV_e_closure_nuwro"], P["closure"])
        self.assertEqual(c["inputs"]["products_sha256"]["L-5D-PV_e_closure_tune_v1"], P["floor"])
        self.assertEqual(c["positive_control"]["reporting16"]["closure_floor_max_abs"], P["floor_max_abs"])
        self.assertEqual(tuple(c["vertices"]), F.VERTICES)
        self.assertEqual(digest(STATE / "measurement-paper/5d-design-20261023/stage0/INVENTORY.sha256"), P["stage0_inventory"])
        self.assertEqual(digest(STATE / "measurement-paper/5d-design-20261023/stage0/receipts-A/products.sha256"), P["stage0c_sums"])
        self.assertEqual(digest(STATE / "s5p/archive/SHA256SUMS-s5p-archive-20261006.txt"), P["s5p_sums"])
        for label, sha in P["d16"].items():
            self.assertEqual(digest(STATE / f"s5p/stage3/f4/D16-{label}.json"), sha)
        build = (STATE / "measurement-scoping/pv-ladder/BUILD-REPORT.md").read_text()
        self.assertIn(P["cmodel_npz"], build)

    def test_declared_counts_are_the_manifests(self):
        sums = sa.load_manifest(STATE / "s5p/archive/SHA256SUMS-s5p-archive-20261006.txt")
        for kind in ("cal", "pow"):
            for d, n in F.COUNTS[kind].items():
                self.assertEqual(sum(1 for p in sums if p.startswith(f"runs/prod/{kind}/{d}/") and p.endswith(".npz")), n, d)
        inv = sa.load_manifest(STATE / "measurement-paper/5d-design-20261023/stage0/INVENTORY.sha256")
        for t in F.TRUTHS:
            if t["row"] == 1:
                names = sorted(Path(p).name for p in inv if f"/runs/cand/assess/{t['set']}/" in p)
                s0, n = t["seeds"]
                self.assertEqual([int(x.rsplit("_s", 1)[1][:-4]) for x in names], list(range(s0, s0 + n)), t["name"])
        s0c = sa.load_manifest(STATE / "measurement-paper/5d-design-20261023/stage0/receipts-A/products.sha256")
        self.assertEqual(sum(1 for p in s0c if p.startswith("runs/new_gibuu/") and p.endswith(".npz")), 20)
        for label in F.PINS["d16"]:
            items = F.f4_inputs(STATE / "s5p/stage3/f4", Path("/"), label)
            self.assertEqual(sorted(int(p.stem.rsplit("_s", 1)[1]) for p, _ in items), list(F.F4_SEEDS))
        self.assertEqual(sum(1 for t in F.TRUTHS), 18)
        self.assertEqual(sum(F.COUNTS["cal"].values()) + sum(F.COUNTS["pow"].values()) + 80 + 120 + 20 + 2, 8545)

    def test_the_committed_f4_preserve_inventory_is_the_d16_records(self):
        inv = FD / "fd/F4-PRESERVE-INVENTORY.sha256"
        self.assertEqual(inv.read_text().splitlines(), F.f4_inventory_lines(STATE / "s5p/stage3/f4"))
        self.assertEqual(len(inv.read_text().splitlines()), 80)

    def test_the_committed_cresp_preserve_inventory_is_the_cresp_report(self):
        """F0b section 2.2: one line, the npz the C_resp report names, by the digest it records (CRESP-REPORT.md)."""
        lines = (FD / "fd/CRESP-PRESERVE-INVENTORY.sha256").read_text().splitlines()
        self.assertEqual(len(lines), 1)
        sha, path = lines[0].split("  ")
        rep = (STATE / "measurement-scoping/assigned-uncertainties/cresp/CRESP-REPORT.md").read_text()
        self.assertIn(f"`{path}`, sha256\n  `{sha}`", rep)
        self.assertEqual(path, "/pscratch/sd/j/josephrb/cresp-20261026/out/cresp.npz")
        self.assertRegex(sha, "^4d8b5797[0-9a-f]{56}$")

    def test_fd_plan_table_2_1_reproduces_from_the_committed_records(self):
        s1j = json.loads((FD / "s1/readout/s1_assembly.json").read_text())
        S = np.asarray(json.loads((ND / "pv-ladder/readouts/cmodel_5d.json").read_text())["S"], float)
        se = np.asarray(s1j["relative_sigma"]["C_e"], float)
        got = {"C_e": F.sigma_summary(se)}
        for k, own in (("C_total", None), *((f"minus_{v}", v) for v in F.VERTICES)):
            keep = [j for j, v in enumerate(F.VERTICES) if v != own]
            got[k] = F.sigma_summary(np.sqrt(se ** 2 + (S[keep] ** 2).sum(0)))
        self.assertEqual(got, F.PINS["table_2_1"])
        np.testing.assert_allclose(np.sqrt(se ** 2 + (S ** 2).sum(0)), s1j["relative_sigma"]["C_total"], rtol=1e-12)

    def test_gibuu_cells_are_the_p_parallel_below_4p5_cells(self):
        d = json.loads(DEFINITION.read_text())
        self.assertEqual(sorted(c["id"] for c in d["reporting_cells"] if c["box"]["pz"][1] <= 4.5), list(F.GIBUU_CELLS))
        self.assertTrue(all(c["box"]["pz"][0] >= 4.5 for c in d["reporting_cells"] if c["id"] not in F.GIBUU_CELLS))

    def test_truth_groups_are_the_plan_table(self):
        groups = {t["name"]: (t["group"], t["own"], t.get("sens")) for t in F.TRUTHS}
        self.assertEqual([n for n, g in groups.items() if g[0] == "prior"], ["nominal", "A7_mnvtune"])
        self.assertEqual({n: g[2] for n, g in groups.items() if g[0] == "non-vertex"}, {"q3": "nuwro", "A7_genie_cv": "genie_mec"})
        fam = {}
        for n, g in groups.items():
            if g[0] == "vertex-family":
                fam.setdefault(g[1], []).append(n)
        self.assertEqual(fam, {"nuwro": ["W1", "W3", "closure_nuwro", "A7_nuwro", "P1r", "P2r", "P1g", "P2g"],
                               "genie_mec": ["W2", "A7_genie_mec", "P3r", "P3g"], "gibuu": ["stage0c_gibuu", "A7_gibuu"]})


if __name__ == "__main__":
    unittest.main()
