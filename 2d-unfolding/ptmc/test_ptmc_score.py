"""PTMC scorer tests on hand-made products (as REF-C2C1's reader tests do): a publication, its cells, E_R, the D4
baseline (REF's IBU central and replicas, Q_R's copies, the committed markers and readout), and the 7 + N units, at a
fixture scale (N = 12, rank 3; the scorer's declared constants are patched, never its CLI). They need PyROOT.

  PTMC_PY=/path/python OMP_NUM_THREADS=1 python -B -m pytest -q -p no:cacheprovider test_ptmc_score.py
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ptmc_lib as P  # noqa: E402
import test_ptmc as T  # noqa: E402  (the deploy tree, built once)

try:
    import ROOT  # noqa: F401
    HAVE_ROOT = True
except Exception:  # pragma: no cover
    HAVE_ROOT = False

PT, PZ = T.PT, T.PZ
KS = [1, 2, 3, 4, 5, 10, 15, 20]
N, RANK = 12, 3
ARGV = ["--omnifile", "/stage/cv.root", "--mcfile", "/stage/mc.root", "--iters", "5"]
ROWS_FILE_ARGS = ["--signal-convention", "minerva", "--oofvc-rows", "/stage/oofvc_rows.npz"]
THREADS = {"OMP_NUM_THREADS": "64", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write_root(path: Path, hists: dict, named: dict | None = None, params: dict | None = None):
    import ROOT
    f = ROOT.TFile.Open(str(path), "RECREATE")
    for name, v in hists.items():
        if len(v) == 14:  # a pT histogram (hFlux_pt), a TH1D as the driver writes it
            h = ROOT.TH1D(name, "", 14, np.asarray(PT, float))
            for i in range(14):
                h.SetBinContent(i + 1, float(v[i]))
        else:
            h = ROOT.TH2D(name, "", 14, np.asarray(PT, float), 16, np.asarray(PZ, float))
            for g in range(224):
                h.SetBinContent(g // 16 + 1, g % 16 + 1, float(v[g]))
        h.Write()
    for name, val in (params or {}).items():
        ROOT.TParameter("double")(name, float(val)).Write()
    for name, val in (named or {}).items():
        ROOT.TNamed(name, json.dumps(val, sort_keys=True)).Write()
    f.Close()


class Products:
    """Every product the scorer reads, hand-made, with the readings known."""

    def __init__(self, delta_scale: float, pub_class: str = "TH2D"):
        import ROOT
        rng = np.random.default_rng(7)
        self.tmp = Path(tempfile.mkdtemp(prefix="ptmc-score-"))
        self.units, self.d4, self.repo = self.tmp / "units", self.tmp / "d4", self.tmp / "repo"
        for d in (self.units, self.d4, self.repo):
            d.mkdir()
        self.tree = T.tree()
        sys.path.insert(0, str(self.tree / "2d-unfolding" / "uq"))
        import reported_cells as rc
        # the publication and its committed cells
        rep = np.ones(224, bool)
        rep[rng.choice(224, 19, replace=False)] = False
        paper = np.where(rep, rng.uniform(1, 3, 224), 0.0) * 1e-39
        sig = 0.03 * paper
        pub = self.d4 / "000_cov_ptpl_minerva_inclusive_6GeV.root"
        f = ROOT.TFile.Open(str(pub), "RECREATE")
        h = getattr(ROOT, pub_class)("pt_pl_cross_section", "", 14, np.asarray(PT, float), 16, np.asarray(PZ, float))
        for g in range(224):
            h.SetBinContent(g // 16 + 1, g % 16 + 1, paper[g])
        h.Write()
        for name, scale in (("TotalCovariance", 1.0), ("StatOnlyCovariance", 0.3)):
            m = ROOT.TMatrixD(224, 224)
            for g in np.flatnonzero(rep):
                m[int(g)][int(g)] = scale * sig[g] ** 2
            m.Write(name)
        f.Close()
        cells_dir = self.repo / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2/cells"
        cells_dir.mkdir(parents=True)
        fc = ROOT.TFile.Open(str(cells_dir / "cells.root"), "RECREATE")
        rc.identity_hist(rc.reported_indices(rep.reshape(rc.GRID_SHAPE))).Write()
        fc.Close()
        # E_R and the readout's chi2
        self.x_er = paper * (1 + 0.05 * rep)
        ref = {"params": {"n_estimators": 400}, "signed_sum": 100.0, "refined_sum": 99.0, "clipped_fraction": 0.01,
               "n_data": 10, "n_injected": 5}
        write_root(self.d4 / "001_xsec.root", {"hXSec2D": self.x_er}, {"re2Refinement": ref})
        d = self.x_er - paper
        m = rep
        c_pub = float(d[m] @ np.linalg.pinv(np.diag(sig[m] ** 2)) @ d[m])
        # the rows file (moved rows) and the background
        rows = {"entry": np.array([3, 8, 13, 21], np.int64), "reco_pt": np.array([0.2, 0.5, 1.2, 9.0]),
                "reco_pz": np.array([2.2, 5.5, 12.0, 30.0]), "true_pt": np.array([0.21, 0.52, 1.1, 2.0]),
                "true_pz": np.array([2.3, 5.4, 11.0, 29.0]), "w_reco": np.array([1.0, 2.0, 3.0, 4.0]),
                "w_truth": np.array([1.1, 2.1, 3.1, 4.1])}
        self.rows = self.tmp / "oofvc_rows.npz"  # the canonical argv names the staging root's oofvc_rows.npz
        np.savez(self.rows, **rows)
        pot = 0.5
        L = __import__("oofvc_lib", fromlist=["x"]) if False else None
        g = np.searchsorted(PT, rows["reco_pt"], side="right") - 1
        gz = np.searchsorted(PZ, rows["reco_pz"], side="right") - 1
        inside = (g >= 0) & (g < 14) & (gz >= 0) & (gz < 16)
        gid = np.where(inside, g * 16 + gz, -1)
        b_off = rng.uniform(5, 10, 224)
        removed = np.bincount(gid[inside], weights=rows["w_reco"][inside] * pot, minlength=224)
        b_r = b_off - removed
        app = rows["entry"][inside]
        counts = {"appended": int(inside.sum()), "outside": int((~inside).sum()), "dropped_appended_weight": 0,
                  "dropped_outside_weight": 0}
        # the fill record of p_off_b1 (seed-independent), and the R replicas' (moved entries removed)
        fe = np.array([1, 3, 5, 8, 9, 13, 14, 21, 30], np.int64)
        fpt = rng.uniform(0.1, 4.0, fe.size)
        fpz = rng.uniform(2.0, 50.0, fe.size)
        fw = rng.uniform(0.1, 1.0, fe.size)
        keep = ~np.isin(fe, rows["entry"])
        self.fill_off = {"fill_entry": fe, "fill_pt": fpt, "fill_pz": fpz, "fill_w": fw}
        self.fill_r = {k: v[keep] for k, v in self.fill_off.items()}
        inj_off = P.injected_entries({"entry": fe, "pt": fpt, "pz": fpz}, PT[0], PT[-1], PZ[0], PZ[-1])
        inj_r = P.injected_entries({"entry": fe[keep], "pt": fpt[keep], "pz": fpz[keep]}, PT[0], PT[-1], PZ[0], PZ[-1])
        fix_params = {"dataPOT": 1e20, "mcPOT": 2e20, "potScale": pot, "fluxIntegral_m2_per_POT": 1e-4,
                      "fluxIntegral_cm2_per_POT": 1.0, "nNucleons": 3e30}
        fix_h = {"hOFTruthDenom2D": rng.uniform(1, 2, 224), "hDataReco2D": rng.uniform(1, 2, 224),
                 "hFlux_pt": rng.uniform(1, 2, 14)}
        # Q_R and REF's IBU products, with REF's markers and readout
        noise = lambda: 0.005 * paper * rng.standard_normal(224)  # noqa: E731
        ibu_off_c = self.x_er * 1.02
        staged, marker_dir = {}, self.repo / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2"
        (marker_dir / "units-centrals").mkdir(parents=True)
        (marker_dir / "units-replicas" / "timeout" / "units").mkdir(parents=True)
        np.savez(self.d4 / "c2_central.npz", ks=np.array(KS), xsec=np.tile(ibu_off_c, (len(KS), 1)),
                 meta=json.dumps({"unit": "c2_central", "argv": ARGV}))
        (marker_dir / "units-centrals" / "c2_central.done").write_text(json.dumps(
            {"unit": "c2_central", "verdict": "PASS", "sha256": sha(self.d4 / "c2_central.npz"), "root_sha256": "x"}))
        self.q_r, self.ref_rep = {}, {}
        for b in range(1, N + 1):
            eb = self.x_er + noise()
            st = {"streams": "three", "unit_factors": False, "bootstrap_seed": b,
                  "seed_offsets": {"data": 0, "mc": 10_000_000, "bkg": 20_000_000},
                  "n": {"data": 10, "mc": 50, "bkg": 40}, "sum": {"data": 10.0 + b, "mc": 50.0 + b, "bkg": 30.0 + b}}
            p = self.d4 / P.staged_index(b)
            write_root(p, {"hXSec2D": eb}, {"p1Streams": st, "re2Refinement": ref})
            staged[f"/src/S1_{b:03d}"] = sha(p)
            cb = eb * 1.02 + 0.3 * noise()
            np.savez(self.d4 / f"c2_replica_b{b}.npz", ks=np.array(KS), xsec=np.tile(cb, (len(KS), 1)),
                     meta=json.dumps({"unit": f"c2_replica_b{b}",
                                      "argv": ARGV + ["--bootstrap-seed", str(b), "--bootstrap-streams", "three"]}))
            (marker_dir / "units-replicas" / "timeout" / "units" / f"c2_replica_b{b}.done").write_text(json.dumps(
                {"unit": f"c2_replica_b{b}", "verdict": "PASS", "sha256": sha(self.d4 / f"c2_replica_b{b}.npz"),
                 "root_sha256": "x"}))
            self.q_r[b], self.ref_rep[b] = (eb, st), cb
        dist_ibu = {str(k): 1.0 for k in KS}  # not compared: c2_central is present
        (marker_dir / "read-2").mkdir()
        (marker_dir / "read-2" / "readout.json").write_text(json.dumps({"staged_sha256": staged,
                                                                        "D_IBU_every_K": dist_ibu}))
        # the units
        runtime = {"python": "3.11", "numpy": "1", "ROOT": "6.28", "lightgbm": "4", "sklearn": "1"}
        import ptmc_score as S
        tree_files = {f: sha(self.tree / f) for f in S.TREE_FILES}
        own = {f: sha(HERE / f) for f in S.OWN_FILES}
        pins = {"tree": tree_files, "own": own, "rows": sha(self.rows), "join": "j" * 64, "roounfold_lib_sha256": "lib"}
        self.pins = self.tmp / "pins.json"
        self.pins.write_text(json.dumps(pins))
        tree_cfg = json.loads((self.tree / "2d-unfolding/ref_c2c1/config.json").read_text())
        delta = delta_scale * paper * rng.choice([-1.0, 1.0], 224)

        def unit(name, x_of, x_ibu, conv, b, root_extra=None, arrays=None, draw=None):
            argv = S.canonical_argv(tree_cfg, conv, b, self.rows)
            controls = {"C-FILL-IBU": {"pass": True}, "C-PAIR": {"pass": True}, "C-ROO": {"pass": True, "ran": True},
                        "C-DRAW-R": {"pass": True, **(draw or {})}, "C-COMP": {"pass": True}, "C-REFINE": {"pass": True}}
            if b is None:
                controls["C-COUPLE"] = {"pass": True}
                controls["C-SIM"] = {"pass": True, "covered": list(range(224))}
            if conv == "R":
                controls["C-MOVE-UNIT"] = {"pass": True}
            meta = {"schema": "ptmc-unit/1", "unit": name, "convention": conv, "bootstrap_seed": b, "argv": argv,
                    "ks": KS, "unfolder": "lib", "cpus": 64, "thread_env": THREADS, "runtime": runtime,
                    "runner_sha256": own["ptmc_run.py"], "lib_sha256": own["ptmc_lib.py"],
                    "code_sha256": tree_cfg["code_sha256"],
                    "inputs_sha256": {"CV": tree_cfg["inputs"]["CV_sha256"], "MC": tree_cfg["inputs"]["MC_sha256"]},
                    "controls": controls, "oofvc_counts": counts if conv == "R" else None,
                    "extract_args_sha256": "e" * 64, "extract_args_finite": True,
                    "grid": {"pt": [float(e) for e in PT], "pz": [float(e) for e in PZ]},
                    "support": {"pass": True, "n_seeds": 200, "failures": {}, "n_seed_cells": 0} if name == "p_R_c" else None,
                    "seconds": 1.0}
            arr = {"ks": np.array(KS), "xsec": np.tile(x_ibu, (len(KS), 1)), "completeness": np.ones(224),
                   "appended_entry": app if conv == "R" else np.zeros(0, np.int64),
                   "fill_entries": np.zeros(0, np.int64), "fill_entry": np.zeros(0, np.int64),
                   "fill_pt": np.zeros(0), "fill_pz": np.zeros(0), "fill_w": np.zeros(0),
                   "inj_entries": np.zeros(0, np.int64), **(arrays or {})}
            np.savez(self.units / f"{name}.npz", **arr, meta=json.dumps(meta))
            write_root(self.units / f"{name}.root", {"hXSec2D": x_of, **(root_extra or {}).get("h", {})},
                       (root_extra or {}).get("named"), (root_extra or {}).get("params"))
            (self.units / f"{name}.done").write_text(json.dumps(
                {"unit": name, "verdict": "PASS", "sha256": sha(self.units / f"{name}.npz"),
                 "root_sha256": sha(self.units / f"{name}.root")}))
        fixed = {"h": dict(fix_h), "params": fix_params}
        unit("p_off_c", self.x_er, ibu_off_c, "off", None,
             {"h": {**fix_h, "hBkgReco2D": b_off}, "params": fix_params},
             draw={"n_original": 50, "n_appended": 0})
        x_r = self.x_er * 1.01
        unit("p_R_c", x_r, x_r + delta, "R", None,
             {"h": {**fix_h, "hBkgReco2D": b_r}, "params": fix_params},
             draw={"n_original": 50, "n_appended": int(inside.sum())})
        for b in range(1, 6):
            eb, st = self.q_r[b]
            x_of = eb if b == 1 else eb + 1e-6 * noise()
            ibu = self.ref_rep[b] if b == 1 else self.ref_rep[b] + 1e-6 * noise()
            unit(f"p_off_b{b}", x_of, ibu, "off", b, {"named": {"re2Refinement": ref, "p1Streams": st},
                                                    "h": {"hOFTruthDenom2D": fix_h["hOFTruthDenom2D"]}},
                 arrays={**self.fill_off, "inj_entries": inj_off} if b == 1 else None)
        for b in range(1, N + 1):
            eb, st = self.q_r[b]
            xo = x_r + noise()
            xi = xo + delta + 0.3 * noise()
            unit(f"p_R_b{b}", xo, xi, "R", b, {"named": {"p1Streams": st},
                                               "h": {"hOFTruthDenom2D": fix_h["hOFTruthDenom2D"]}},
                 arrays={**self.fill_r, "inj_entries": inj_r},
                 draw={"n_data": st["n"]["data"], "data_sum": st["sum"]["data"], "n_original": st["n"]["mc"],
                       "original_sum": st["sum"]["mc"], "n_appended": int(inside.sum())})
        before = {"driver": tree_files["2d-unfolding/re2/re2_driver.py"],
                  "config": tree_files["2d-unfolding/ref_c2c1/config.json"],
                  "runner": tree_files["2d-unfolding/ref_c2c1/ref_c2c1.py"], "ptmc_run": own["ptmc_run.py"],
                  "ptmc_lib": own["ptmc_lib.py"], "rows": pins["rows"], "join_record": pins["join"],
                  "roounfold_lib": "lib"}
        self.write_pins = lambda: (self.units / "pins_all.json").write_text(json.dumps(
            {"pass": True, "before": before, "after": before, "outputs": {
                p.stem: {f"{p.stem}.npz": json.loads(p.read_text())["sha256"],
                         f"{p.stem}.root": json.loads(p.read_text())["root_sha256"]}
                for p in self.units.glob("p_*.done")}}))
        self.write_pins()
        # the D4 staging manifest: every product copied, none absent
        import ptmc_score as S
        man = {"schema": "ptmc-d4-stage/2", "ref_root": S.REF_ROOT,
               "copied": {p.name: {"sha256": sha(p)} for p in self.d4.iterdir()}, "absent": []}
        (self.d4 / "manifest.json").write_text(json.dumps(man))
        self.K = {"N": N, "RANK": RANK, "N_OFF": 5, "CELLS_SHA": sha(cells_dir / "cells.root"),
                  "E_R_SHA": sha(self.d4 / "001_xsec.root"), "PUB_SHA": sha(pub), "C_PUB": c_pub,
                  "NDF": int(rep.sum()), "COUNTS": counts, "SCAN": KS, "Q_R_SRC": "/src/S1_{b:03d}",
                  "READOUT_SHA": sha(marker_dir / "read-2" / "readout.json"),
                  "CENTRAL_MARKER_SHA": sha(marker_dir / "units-centrals" / "c2_central.done"),
                  "ROWS_SHA": sha(self.rows)}

    def mark_absent(self, name):
        """Remove a D4 product as the staging would record a clean source absence."""
        (self.d4 / name).unlink()
        m = json.loads((self.d4 / "manifest.json").read_text())
        del m["copied"][name]
        import ptmc_score as S
        m["absent"].append(S.d4_source(name))
        (self.d4 / "manifest.json").write_text(json.dumps(m))

    def rewrite_unit(self, name, z):
        np.savez(self.units / f"{name}.npz", **z)
        mk = json.loads((self.units / f"{name}.done").read_text())
        mk["sha256"] = sha(self.units / f"{name}.npz")
        (self.units / f"{name}.done").write_text(json.dumps(mk))
        self.write_pins()

    def score(self, rows=None):
        import ptmc_score as S
        out = self.tmp / f"score_{len(list(self.tmp.glob('score_*')))}.json"
        rows = rows or self.rows
        argv = ["--tree", str(self.tree), "--units", str(self.units), "--d4", str(self.d4), "--repo", str(self.repo),
                "--rows", str(rows), "--rows-sha256", sha(rows), "--pins", str(self.pins), "--out", str(out)]
        # the scorer runs as its own process in production: the tree's modules must resolve fresh, from the tree, and
        # an earlier test's import (another tree, in this one process) would fail its C-PINS check
        saved_path = list(sys.path)
        for m in ("ref_c2c1_read", "ref_c2c1", "oofvc_lib", "reported_cells"):
            sys.modules.pop(m, None)
        try:
            with mock.patch.dict(S.CONST, self.K):
                rc = S.main(argv)
        finally:
            sys.path[:] = saved_path
        rec = json.loads(out.read_text()) if out.exists() else json.loads((self.tmp / "STOP.json").read_text())
        return rc, rec


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class Scorer(unittest.TestCase):

    def test_differ_with_b_formed(self):
        p = Products(delta_scale=0.05)
        rc, rec = p.score()
        self.assertEqual(rc, 0, rec)
        self.assertEqual(rec["disposition"], "formed")
        self.assertEqual(rec["PTMC-R1"], "differ")
        self.assertIn(rec["PTMC-B"], P.WORDS)
        self.assertNotIn("held fixed", rec["statement"]["text"])
        for k in ("C-UNITS", "C-PINS", "C-CELLS", "C-PUB", "C-GRID", "C-FIX", "C-MOVE", "C-NORM", "C-BASE",
                  "C-REPOFF", "C-DRAW-R", "C-SHAPE"):
            self.assertTrue(rec["controls"][k]["pass"] if isinstance(rec["controls"][k], dict) and "pass" in
                            rec["controls"][k] else True, k)
        self.assertIn("C-PROTO", rec["printed_read_by_nothing"])
        self.assertEqual(len(rec["printed_read_by_nothing"]["suppressed_moved_support_cells_replicas"]), N)  # agy 8
        # B8: the bound values this score verified are recorded
        self.assertEqual(rec["pins"]["rows"], sha(p.rows))
        self.assertEqual(rec["pins"]["pin_manifest_sha256"], sha(p.pins))
        self.assertEqual(rec["pins"]["d4_manifest_sha256"], sha(p.d4 / "manifest.json"))
        self.assertEqual(set(rec["pins"]["tree"]), set(json.loads(p.pins.read_text())["tree"]))

    def test_a_renamed_rows_copy_scores_the_same(self):
        """Confirm read B14: the canonical argv names the bound staged rows path, not the local copy's basename."""
        p = Products(delta_scale=0.05)
        other = p.tmp / "same_bytes_renamed.npz"
        other.write_bytes(p.rows.read_bytes())
        rc, rec = p.score(rows=other)
        self.assertEqual(rc, 0, rec)
        self.assertEqual(rec["disposition"], "formed")

    def test_a_replica_with_another_denominator_stops(self):
        """C-DEN (confirm read B10): every unit's hOFTruthDenom2D must be the central's, bit for bit."""
        import ROOT
        p = Products(delta_scale=0.05)
        f = ROOT.TFile.Open(str(p.units / "p_R_b8.root"), "UPDATE")
        h = f.Get("hOFTruthDenom2D")
        h.SetBinContent(3, 4, h.GetBinContent(3, 4) * (1 + 1e-12))
        h.Write("", ROOT.TObject.kOverwrite)
        f.Close()
        mk = json.loads((p.units / "p_R_b8.done").read_text())
        mk["root_sha256"] = sha(p.units / "p_R_b8.root")
        (p.units / "p_R_b8.done").write_text(json.dumps(mk))
        p.write_pins()
        rc, rec = p.score()
        self.assertEqual(rc, 3, rec)
        self.assertIn("C-DEN", rec["why"])
        self.assertIn("p_R_b8", rec["why"])

    def test_fix_requires_the_drivers_class_and_grid(self):
        """B9: C-FIX's objects must be the class the driver writes, on section 2.5's finite edges, even when both
        files agree."""
        import ptmc_score as S
        axes = np.array([[float(e) for e in PT], [float(e) for e in PZ], [0.0, 1.0]], dtype=object)
        good = ("TH1", "TH2D", axes, np.ones(5), np.zeros(5))
        one = ("hOFTruthDenom2D",)
        self.assertTrue(S.fix_equal({one[0]: good}, {one[0]: good}, one)[one[0]])
        f = ("TH1", "TH2F", axes, np.ones(5), np.zeros(5))
        self.assertFalse(S.fix_equal({one[0]: f}, {one[0]: f}, one)[one[0]])
        nan_axes = np.array([[float(e) for e in PT[:-1]] + [float("nan")], [float(e) for e in PZ], [0.0, 1.0]],
                            dtype=object)
        n = ("TH1", "TH2D", nan_axes, np.ones(5), np.zeros(5))
        self.assertFalse(S.fix_equal({one[0]: n}, {one[0]: n}, one)[one[0]])
        par = ("TParameter", "TParameter<float>", 1.0)
        self.assertFalse(S.fix_equal({"potScale": par}, {"potScale": par}, ("potScale",))["potScale"])

    def test_finite_ratio(self):
        """codex 20: T/q95 is undefined only where q95 = 0 (a negative q95 still divides), and an overflowed quotient
        is undefined rather than Infinity."""
        import ptmc_score as S
        self.assertEqual(S.finite_ratio(3.0, 2.0), 1.5)
        self.assertEqual(S.finite_ratio(3.0, -2.0), -1.5)
        self.assertIsNone(S.finite_ratio(3.0, 0.0))
        self.assertIsNone(S.finite_ratio(1e308, 1e-308))
        self.assertIsNone(S.finite_ratio(float("nan"), 1.0))

    def test_the_publication_histogram_must_be_a_th2d(self):
        """codex 19: the publication's histogram is validated (class and axes) before it is flattened. The real
        000 (6c6dce72) is a TH2D, 16 p|| x 14 pT bins."""
        rc, rec = Products(delta_scale=0.05, pub_class="TH2F").score()
        self.assertEqual(rc, 3, rec)
        self.assertIn("is not a TH2D", rec["why"])

    def test_agree_when_delta_is_zero(self):
        p = Products(delta_scale=0.0)
        rc, rec = p.score()
        self.assertEqual(rc, 0, rec)
        self.assertIn(rec["PTMC-R1"], ("agree", "marginal"))

    def test_absent_replica_is_unavailable_and_corrupt_marker_stops(self):
        p = Products(delta_scale=0.05)
        p.mark_absent("c2_replica_b5.npz")
        rc, rec = p.score()
        self.assertEqual(rc, 0, rec)
        self.assertEqual(rec["disposition"], "unavailable")
        self.assertIsNone(rec["PTMC-B"])
        self.assertEqual(rec["statement"]["row"], 4)
        # section 3.3 item 3: the skipped checks are listed with their missing operands (codex 17)
        sk = {x["check"]: x["missing"] for x in rec["controls"]["C-D4"]["skipped"]}
        self.assertEqual(sk["the B arm (T, q95, max at K = 10 and 5) and C-PROTO"], ["c2_replica_b5.npz"])
        q = Products(delta_scale=0.05)
        np.savez(q.d4 / "c2_replica_b3.npz", ks=np.array(KS), xsec=np.zeros((len(KS), 224)), meta="{}")
        rc, rec = q.score()
        self.assertEqual(rc, 3)
        self.assertTrue(rec["stopped"])
        # staged faithfully (its staging digest agrees) but not REF's product (its marker disagrees): a mismatch, and
        # the STOP is the disposition's, naming the mismatched product (not an incidental failure downstream)
        m = json.loads((q.d4 / "manifest.json").read_text())
        m["copied"]["c2_replica_b3.npz"]["sha256"] = sha(q.d4 / "c2_replica_b3.npz")
        (q.d4 / "manifest.json").write_text(json.dumps(m))
        (q.tmp / "STOP.json").unlink()  # the scorer refuses to run over an earlier STOP
        rc, rec = q.score()
        self.assertEqual(rc, 3)
        self.assertIn("the disposition is STOP", rec["why"])
        self.assertIn("c2_replica_b3.npz", rec["why"])

    def test_duplicated_retained_fill_row_stops(self):
        """The confirm read's finding 3: a replica with a retained background row filled twice must STOP."""
        p = Products(delta_scale=0.05)
        z = dict(np.load(p.units / "p_R_b2.npz"))
        for k in ("fill_entry", "fill_pt", "fill_pz", "fill_w"):
            z[k] = np.concatenate([z[k], z[k][:1]])
        p.rewrite_unit("p_R_b2", z)
        rc, rec = p.score()
        self.assertEqual(rc, 3)
        self.assertIn("C-MOVE", rec["why"])

    def test_changed_retained_fill_value_stops(self):
        """C-MOVE compares every fill array exactly, not only the entry set: one retained row's pT changed STOPs."""
        p = Products(delta_scale=0.05)
        z = dict(np.load(p.units / "p_R_b2.npz"))
        z["fill_pt"] = np.asarray(z["fill_pt"]).copy()
        z["fill_pt"][0] += 1e-3
        p.rewrite_unit("p_R_b2", z)
        rc, rec = p.score()
        self.assertEqual(rc, 3)
        self.assertIn("C-MOVE: replica sets p_R_b2", rec["why"])

    def test_nan_in_a_unit_stops(self):
        p = Products(delta_scale=0.05)
        z = dict(np.load(p.units / "p_R_b4.npz"))
        z["xsec"] = z["xsec"].copy()
        z["xsec"][5, 7] = np.nan
        p.rewrite_unit("p_R_b4", z)
        rc, rec = p.score()
        self.assertEqual(rc, 3)


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class ScorerGates(unittest.TestCase):
    """One planted defect per gate (codex r1): each must STOP, with no reading."""

    def stops(self, p, frag=None):
        rc, rec = p.score()
        self.assertEqual(rc, 3, rec)
        self.assertTrue(rec.get("stopped"), rec)
        if frag:
            self.assertIn(frag, rec["why"])

    def test_pins_must_cover_every_unit(self):
        p = Products(delta_scale=0.05)
        d = json.loads((p.units / "pins_all.json").read_text())
        d["outputs"].pop("p_R_b3")
        (p.units / "pins_all.json").write_text(json.dumps(d))
        self.stops(p, "C-PINS")

    def test_extra_file_in_units(self):
        p = Products(delta_scale=0.05)
        (p.units / "p_R_b99.npz").write_bytes(b"x")
        self.stops(p, "C-UNITS: inventory")

    def test_non_canonical_argv(self):
        p = Products(delta_scale=0.05)
        z = dict(np.load(p.units / "p_R_b6.npz"))
        m = json.loads(str(z["meta"]))
        m["argv"] = m["argv"] + ["--iters", "7"]
        z["meta"] = json.dumps(m)
        p.rewrite_unit("p_R_b6", z)
        self.stops(p, "canonical")

    def test_a_units_effective_grid_must_be_the_declared_one(self):
        """agy 15 / codex 12: the edges the driver actually ran with (recorded per unit) are section 2.5's."""
        p = Products(delta_scale=0.05)
        z = dict(np.load(p.units / "p_R_b3.npz"))
        m = json.loads(str(z["meta"]))
        m["grid"]["pt"][-1] = 4.0
        z["meta"] = json.dumps(m)
        p.rewrite_unit("p_R_b3", z)
        self.stops(p, "C-GRID: p_R_b3")

    def test_missing_required_control(self):
        p = Products(delta_scale=0.05)
        z = dict(np.load(p.units / "p_R_b7.npz"))
        m = json.loads(str(z["meta"]))
        m["controls"].pop("C-REFINE")
        z["meta"] = json.dumps(m)
        p.rewrite_unit("p_R_b7", z)
        self.stops(p, "C-REFINE")

    def test_duplicate_ref_marker(self):
        p = Products(delta_scale=0.05)
        src = next(p.repo.rglob("c2_replica_b2.done"))
        dup = src.parent.parent / "copy" / "c2_replica_b2.done"
        dup.parent.mkdir(parents=True)
        dup.write_text(src.read_text())
        self.stops(p, "two markers")

    def test_duplicate_central_marker_anywhere(self):
        """B7: a second c2_central marker outside units-centrals is caught, not ignored."""
        p = Products(delta_scale=0.05)
        src = next(p.repo.rglob("c2_central.done"))
        dup = src.parent.parent / "units-replicas" / "c2_central.done"
        dup.write_text(src.read_text())
        self.stops(p, "two markers for c2_central")

    def test_a_symlink_among_the_fetched_files_stops(self):
        """B7: a fetched product that is a symlink (even to the right bytes) is refused."""
        p = Products(delta_scale=0.05)
        real = p.tmp / "real_b9.npz"
        (p.units / "p_R_b9.npz").rename(real)
        (p.units / "p_R_b9.npz").symlink_to(real)
        self.stops(p, "p_R_b9.npz is not a regular file")
        q = Products(delta_scale=0.05)
        real = q.tmp / "real_b4.npz"
        (q.d4 / "c2_replica_b4.npz").rename(real)
        (q.d4 / "c2_replica_b4.npz").symlink_to(real)
        self.stops(q, "c2_replica_b4.npz is not a regular file")

    def test_an_absence_record_must_name_the_declared_source(self):
        """B7: absence is matched by the full source path; a record naming the same basename elsewhere fails."""
        p = Products(delta_scale=0.05)
        p.mark_absent("c2_replica_b5.npz")
        m = json.loads((p.d4 / "manifest.json").read_text())
        m["absent"] = ["/elsewhere/units/c2_replica_b5.npz"]
        (p.d4 / "manifest.json").write_text(json.dumps(m))
        self.stops(p, "absence records that name no declared source")

    def test_a_staging_of_another_root_stops(self):
        """B7: the manifest must name the bound REF root, so its absence records are that root's."""
        p = Products(delta_scale=0.05)
        m = json.loads((p.d4 / "manifest.json").read_text())
        m["ref_root"] = "/pscratch/sd/j/josephrb/ref-c2c1-other"
        (p.d4 / "manifest.json").write_text(json.dumps(m))
        self.stops(p, "C-D4: the staging read")

    def test_fetched_file_outside_the_manifest(self):
        p = Products(delta_scale=0.05)
        (p.d4 / "stray.root").write_bytes(b"x")
        self.stops(p, "C-D4")

    def test_sim_coverage_by_index(self):
        p = Products(delta_scale=0.05)
        z = dict(np.load(p.units / "p_R_c.npz"))
        m = json.loads(str(z["meta"]))
        m["controls"]["C-SIM"]["covered"] = list(range(223))
        z["meta"] = json.dumps(m)
        p.rewrite_unit("p_R_c", z)
        self.stops(p, "C-SIM coverage")

    def test_repoff_runs_when_another_replica_is_absent(self):
        """codex r1 #17: an absent c2_replica_b5 must not switch off C-REPOFF on the accepted seed-1 pair."""
        p = Products(delta_scale=0.05)
        p.mark_absent("c2_replica_b5.npz")
        z = dict(np.load(p.units / "p_off_b1.npz"))
        z["xsec"] = z["xsec"] * 1.01
        p.rewrite_unit("p_off_b1", z)
        self.stops(p, "STOP")

    def test_draw_aggregate_runs_when_b_is_unavailable(self):
        p = Products(delta_scale=0.05)
        p.mark_absent("c2_replica_b5.npz")
        z = dict(np.load(p.units / "p_R_b9.npz"))
        m = json.loads(str(z["meta"]))
        m["controls"]["C-DRAW-R"]["data_sum"] += 1.0
        z["meta"] = json.dumps(m)
        p.rewrite_unit("p_R_b9", z)
        self.stops(p, "C-DRAW-R")

    def test_conditioning_guard_stops(self):
        """The binding's guard: an arm below lambda_r/lambda_1 = 1e-10 STOPs, whatever C-SHAPE says."""
        import ptmc_lib as PL
        p = Products(delta_scale=0.05)
        with mock.patch.object(PL, "conditioning", return_value={"ratio": 1e-12, "floor": 1e-10, "pass": False}):
            self.stops(p, "the conditioning guard")

    def test_unexpected_exception_is_a_stop(self):
        p = Products(delta_scale=0.05)
        z = dict(np.load(p.units / "p_R_c.npz"))
        z.pop("appended_entry")
        p.rewrite_unit("p_R_c", z)
        rc, rec = p.score()
        self.assertEqual(rc, 3)
        self.assertIn("KeyError", rec["why"])


if __name__ == "__main__":
    unittest.main()
