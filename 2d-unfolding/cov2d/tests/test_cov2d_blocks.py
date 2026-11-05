"""cov2d_blocks: the blocks at a truth through the rollup's imported functions, the director's R6 tests (the per-band
dict's key set; the per-band blocks summing to the total), the C_model and C_model- construction and its control
(R3), section 9.8, and the O_NOATIME redirect of the rollup's reads. root_6_28 (the rollup imports PyROOT).
Expected values are computed here by hand: 1/4 dd^T for a two-point band, ddof-1 covariances, the carried forms.
    cd 2d-unfolding/cov2d/tests && python -B -m unittest -v test_cov2d_blocks
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import cov2d as c  # noqa: E402

try:
    import ROOT  # noqa: F401
    import cov2d_blocks as cb  # noqa: E402
    cb.rollup()
    HAVE = True
except Exception:  # pragma: no cover
    HAVE = False

N = 205


def fixture(seed=3):
    r = np.random.default_rng(seed)
    x_R = r.uniform(1.0, 2.0, N)
    x_T = x_R * r.uniform(0.8, 1.2, N)
    rep = np.zeros(224, bool)
    rep[np.sort(r.choice(224, N, replace=False))] = True
    bands = {b: x_T + 0.05 * r.standard_normal((c.BANDS[b], N)) for b in c.ORDER}
    for b in c.LATERAL_BANDS:
        bands[b] = x_T + 0.05 * r.standard_normal((2, N))
    minos_x = x_T + 0.05 * r.standard_normal((2, N))
    w = r.uniform(0.5, 1.5, 100)
    X_rep = x_T + 0.03 * r.standard_normal((300, N))
    A = r.standard_normal((N, 4))
    C08_R = A @ A.T * 1e-4
    S = r.standard_normal((3, N)) * 0.02
    C_model = sum(np.outer(s, s) for s in S)
    C_minus = sum(np.outer(s, s) for s in S[1:])
    return dict(x_T=x_T, rep=rep, bands=bands, minos_x=minos_x, w=w, X_rep=X_rep, x_R=x_R, C08_R=C08_R,
                C_model=C_model, C_minus=C_minus)


def drifted_norm(real):
    """universe_block with its normalization entry off by one part in 1e6 and its total re-summed to match, so only the
    norm check can refuse."""
    def fake(*a):
        blocks, _ = real(*a)
        blocks = dict(blocks)
        blocks[cb.NORM_KEY] = blocks[cb.NORM_KEY] * (1 + 1e-6)
        tot = np.zeros_like(blocks[cb.NORM_KEY])
        for k in blocks:
            tot += blocks[k]
        return blocks, tot
    return fake


def quarter(X):
    d = X[0] - X[1]
    return 0.25 * np.outer(d, d)


@unittest.skipUnless(HAVE, "needs PyROOT (the rollup imports it)")
class Assemble(unittest.TestCase):
    def setUp(self):
        self.f = fixture()
        self.out = cb.assemble(self.f["x_T"], self.f["rep"], self.f["bands"], self.f["minos_x"], self.f["w"],
                               self.f["X_rep"], self.f["x_R"], self.f["C08_R"], self.f["C_model"], self.f["C_minus"])

    def test_r6_key_set_is_38_universe_5_lateral_and_the_norm(self):
        keys = set(self.out["blocks"])
        self.assertEqual(len(keys), 44)
        self.assertEqual(keys, set(c.ORDER) | set(c.LATERAL_BANDS) | {cb.NORM_KEY})
        self.assertEqual(len(c.ORDER), 38)

    def test_r6_blocks_sum_to_the_functions_total(self):
        ro = cb.rollup()
        blocks, tot = ro.universe_block(cb.CellsT(self.f["rep"], self.f["x_T"]), self.f["bands"], self.f["w"],
                                        self.f["minos_x"])
        s = np.zeros_like(tot)
        for b in blocks:
            s += blocks[b]
        np.testing.assert_array_equal(s, tot)
        np.testing.assert_allclose(self.out["C_univ"] + self.out["C_lat"] + self.out["C_norm"], tot, rtol=1e-12,
                                   atol=1e-15)

    def test_refuses_a_drifted_dict_layout(self):
        ro = cb.rollup()
        real = ro.universe_block
        cases = {
            "extra key": lambda *a: (dict(real(*a)[0], extra=np.zeros((N, N))), real(*a)[1]),
            "missing band": lambda *a: ({k: v for k, v in real(*a)[0].items() if k != "MaRES"}, real(*a)[1]),
            "total off": lambda *a: (real(*a)[0], real(*a)[1] + 1e-9),
            "norm drifted, total consistent": drifted_norm(real),
        }
        for name, fake in cases.items():
            with self.subTest(name), mock.patch.object(ro, "universe_block", fake), self.assertRaises(c.Refusal):
                cb.assemble(self.f["x_T"], self.f["rep"], self.f["bands"], self.f["minos_x"], self.f["w"],
                            self.f["X_rep"], self.f["x_R"], self.f["C08_R"], self.f["C_model"])

    def test_norm_is_built_from_x_hat_T_once(self):
        v = 0.014 * self.f["x_T"]
        np.testing.assert_array_equal(self.out["C_norm"], np.outer(v, v))
        self.assertNotIn(cb.NORM_KEY, [b for b in c.ORDER])

    def test_pair_band_and_minos_x01(self):
        np.testing.assert_allclose(self.out["blocks"]["MaRES"], quarter(self.f["bands"]["MaRES"]), rtol=1e-12)
        np.testing.assert_allclose(self.out["blocks"]["Muon_Energy_MINOS"], quarter(self.f["minos_x"]), rtol=1e-12)
        self.assertFalse(np.allclose(self.out["blocks"]["Muon_Energy_MINOS"],
                                     quarter(self.f["bands"]["Muon_Energy_MINOS"])))
        lat = sum(quarter(self.f["minos_x"] if b == "Muon_Energy_MINOS" else self.f["bands"][b])
                  for b in c.LATERAL_BANDS)
        np.testing.assert_allclose(self.out["C_lat"], lat, rtol=1e-12, atol=1e-16)   # sum order differs; entries ~1e-3

    def test_flux_band_is_weighted(self):
        X, w = self.f["bands"][c.FLUX], self.f["w"]
        p = w / w.sum()
        m = p @ X
        want = (X - m).T @ ((X - m) * p[:, None])
        np.testing.assert_allclose(self.out["blocks"][c.FLUX], want, rtol=1e-10, atol=1e-16)

    def test_stat_c08_and_model_forms(self):
        X = self.f["X_rep"]
        d = X - X.mean(axis=0)
        np.testing.assert_allclose(self.out["C_stat"], d.T @ d / (X.shape[0] - 1), rtol=1e-12, atol=1e-16)
        r = self.f["x_T"] / self.f["x_R"]
        np.testing.assert_allclose(self.out["C08"], np.diag(r) @ self.f["C08_R"] @ np.diag(r), rtol=1e-12, atol=1e-20)
        xt = self.f["x_T"]
        np.testing.assert_allclose(self.out["C_model_abs"], np.diag(xt) @ self.f["C_model"] @ np.diag(xt), rtol=1e-12)
        np.testing.assert_allclose(self.out["C_T_minus"] - (self.out["C_T"] - self.out["C_model_abs"]),
                                   np.diag(xt) @ self.f["C_minus"] @ np.diag(xt), rtol=1e-10, atol=1e-15)

    def test_section_9_8(self):
        chk = self.out["section_9_8"]
        self.assertTrue(chk["pass"])
        self.assertEqual(chk["ndf"], N)
        bad = cb.psd_checks(-np.eye(4) * 1e-3 + np.diag([1.0, 1.0, 1.0, 0.0]))
        self.assertFalse(bad["pass"])
        asym = np.eye(4)
        asym[0, 1] = 1e-6
        self.assertFalse(cb.psd_checks(asym)["pass"])
        low = np.diag([1.0, 1.0, 1e-14, 0.0])
        self.assertEqual(cb.psd_checks(low)["ndf"], 2)


@unittest.skipUnless(HAVE, "needs PyROOT (the rollup imports it)")
class NullOnTheRealPath(unittest.TestCase):
    """The auditor's Q1, as a test: assemble -> re2c_rollup.universe_block -> build_repair.wcov feeding the real
    cov2d_null.null_at_T; each law's covariance must be its band's block (check_matched) for C_T and for C_T-."""
    def regimes(self):
        r = np.random.default_rng(11)
        yield "unit", fixture()
        f = fixture()
        scale = 1e-39 * 10 ** r.uniform(0, 3, N)            # physical scale, cells spanning three decades
        for k in ("x_T", "minos_x", "X_rep", "x_R"):
            f[k] = f[k] * scale
        f["bands"] = {b: v * scale for b, v in f["bands"].items()}
        f["C08_R"] = f["C08_R"] * np.outer(scale, scale)
        yield "physical", f
        f = fixture()
        f["w"] = np.exp(2.0 * r.standard_normal(100))        # lognormal Flux weights, sigma 2
        yield "lognormal flux", f
        f = fixture()
        f["bands"] = {b: v * 1.3 for b, v in f["bands"].items()}   # a 30% common offset on every universe
        f["minos_x"] = f["minos_x"] * 1.3
        yield "offset", f

    def test_check_matched_on_every_regime(self):
        import cov2d_null as cn
        for name, f in self.regimes():
            with self.subTest(name):
                out = cb.assemble(f["x_T"], f["rep"], f["bands"], f["minos_x"], f["w"], f["X_rep"], f["x_R"],
                                  f["C08_R"], f["C_model"], f["C_minus"])
                res = cn.null_at_T(out, f["bands"], f["minos_x"], f["w"], n_mc=2_000)
                self.assertLessEqual(res["null"]["match_rel"], 1e-12)
                self.assertLessEqual(res["null_minus"]["match_rel"], 1e-12)


@unittest.skipUnless(HAVE, "needs PyROOT (the rollup imports it)")
class CModel(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True)
        p.start()
        self.addCleanup(p.stop)

    def test_full_construction_reproduces_the_pinned_sha_and_minus_takes_two_vertices(self):
        C, minus, rec = cb.c_model()
        self.assertTrue(rec["full_matrix_sha256_ok"])
        M = json.loads(cb.CMODEL_JSON.read_text())
        S = np.asarray(M["S"])
        idx = [M["vertices"].index(v) for v in ("nuwro", "gibuu")]
        want = np.zeros((S.shape[1],) * 2)
        for k in idx:
            want += np.outer(S[k], S[k])
        np.testing.assert_array_equal(minus, want)
        self.assertEqual(rec["minus_label"], "constructed from the committed shift matrix, not a named part-C product")
        self.assertEqual(len(rec["cells"]), 205)

    def test_a_changed_file_or_matrix_refuses(self):
        with tempfile.TemporaryDirectory() as td:
            M = json.loads(cb.CMODEL_JSON.read_text())
            p = Path(td) / "cmodel_2d.json"
            p.write_text(json.dumps(M))
            with self.assertRaises(c.Refusal):         # not the pinned file
                cb.c_model(p)
            M["S"][1][0] += 1e-9
            p.write_text(json.dumps(M))
            with self.assertRaises(c.Refusal):         # the full construction no longer gives C_model's sha
                cb.c_model(p, want_sha=None)


class NoatimeInputs(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True)
        p.start()
        self.addCleanup(p.stop)
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.d = Path(self.td.name)
        (self.d / "bf").mkdir()
        for pl in ("P1", "P2"):
            for kind in ("MC", "Data"):
                (self.d / "bf" / f"runEventLoop{kind}_{pl}.root").write_bytes(f"{kind}{pl}".encode())
        (self.d / "constraint.txt").write_text("Flux 0 1.0\n")
        import hashlib
        self.sha = hashlib.sha256(b"Flux 0 1.0\n").hexdigest()
        self.ro = types.SimpleNamespace(BF=str(self.d / "bf"), BR=types.SimpleNamespace(PLAYLISTS=["P1", "P2"]),
                                        PIN={"constraint": (str(self.d / "constraint.txt"), self.sha)})

    def test_copies_and_repoints_every_read(self):
        import cov2d_blocks as cbm
        out = self.d / "copies"
        rec = cbm.noatime_inputs(self.ro, out, {"constraint": self.ro.PIN["constraint"]})
        self.assertEqual(self.ro.BF, str(out / "baseline_flux"))
        self.assertEqual((Path(self.ro.BF) / "runEventLoopData_P2.root").read_bytes(), b"DataP2")
        self.assertTrue(self.ro.PIN["constraint"][0].startswith(str(out)))
        self.assertEqual(Path(self.ro.PIN["constraint"][0]).read_text(), "Flux 0 1.0\n")
        self.assertEqual(rec["constraint"], self.sha)
        self.assertEqual(len([k for k in rec if k.endswith(".root")]), 4)

    def test_a_wrong_pin_refuses(self):
        import cov2d_blocks as cbm
        with self.assertRaises(c.Refusal):
            cbm.noatime_inputs(self.ro, self.d / "copies", {"constraint": (self.ro.PIN["constraint"][0], "0" * 64)})


@unittest.skipUnless(HAVE, "needs PyROOT (main imports it)")
class Control95Main(unittest.TestCase):
    """The director's ruling (i), 2026-11-05: control95's main end to end on a fixture, through the real rollup's
    flux_weights, its plain open() of the constraint (re2c_rollup.py:221) included, with the open audit guarding a tmp
    tree that holds every input. Stubbed: the MAT environment, ROOT.TFile.Open (the flux MnvH1D's error bands) and part
    B's arithmetic (Cells, x01, section_9_5, c_model). Only noatime_inputs keeps the rollup's reads off that tree."""
    def setUp(self):
        import collections
        import hashlib
        import ROOT
        import cov2d_blocks as cbm
        self.cbm, ro = cbm, cbm.rollup()
        self.noatime = bool(getattr(os, "O_NOATIME", 0))     # Linux; macOS has none, so its reads move atime
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.d = Path(self.td.name).resolve()
        g = self.g = self.d / "guarded"
        (g / "bf").mkdir(parents=True)
        (self.d / "tmp").mkdir()
        w = np.linspace(0.5, 1.5, 100)

        def put(rel, data):
            path = g / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            return str(path), hashlib.sha256(data).hexdigest()
        self.pins = {
            "constraint": put("constraint.txt", "".join(f"Flux {i} {x!r}\n" for i, x in enumerate(w)).encode()),
            "vl175_build_json": put("build.json", json.dumps({"numbers": {"weights": {
                "sum": float(w.sum()), "n_eff": float(w.sum() ** 2 / (w ** 2).sum())}}}).encode()),
            "vl175_minos_npz": put("minos.npz", b"minos"),
            "flux_mefhc": put("bf_mefhc.root", b"mefhc")}
        for pl in ro.BR.PLAYLISTS:
            for kind in ("MC", "Data"):
                put(f"bf/runEventLoop{kind}_{pl}.root", f"{kind}{pl}".encode())
        sums = {f"U_{b}_{i}/xsec.root": "x" for b in c.ORDER for i in range(c.BANDS[b])}
        for lab in ("ER", "S3_MuonEnergyMINOS0", "S3_MuonEnergyMINOS1"):
            sums[f"{lab}/xsec.root"] = put(f"ns/out/{lab}/xsec.root", lab.encode())[1]
        f = fixture(5)
        npz_path = g / "production_cov.npz"
        np.savez(npz_path, universe=np.eye(N))
        cm = put("cmodel_2d.json", b"{}")[0]
        cells = [int(i) for i in np.flatnonzero(f["rep"])]

        class FakeCells:
            def __init__(self, er):
                self.rep, self.x = f["rep"], f["x_R"]

            def vec(self, path):
                return f["x_R"]

        class Hist:        # the flux MnvH1D: three pT bins, a Flux band with the constraint's weights, MINOS hists
            def GetNbinsX(self):
                return 3

            def GetBinContent(self, i):
                return 1.0 + i

            def GetVertErrorBand(self, band):
                return types.SimpleNamespace(GetUnivWgts=lambda: list(w), GetHist=lambda u: Hist())
        self.opened = []

        def fake_open(name, *a, **k):
            self.opened.append(os.path.realpath(str(name)))
            return types.SimpleNamespace(
                Get=lambda key: types.SimpleNamespace(GetVal=lambda: 1e20) if key == "POTUsed" else Hist(),
                Close=lambda: None)
        for target, attr, value in (
                (os, "O_NOATIME", getattr(os, "O_NOATIME", 0)), (cbm, "AUDIT", None), (ROOT.TFile, "Open", fake_open),
                (cbm.OpenAudit.__init__, "__defaults__", ((str(g),),)), (cbm, "GUARDED", (str(g),)),
                (cbm, "pinned_mat_environment", lambda: {"stub": "the pinned MAT environment"}),
                (cbm, "PARTB_NPZ", (str(npz_path), hashlib.sha256(npz_path.read_bytes()).hexdigest())),
                (cbm, "CMODEL_JSON", Path(cm)), (cbm, "c_model", lambda: (np.eye(N), None, {"cells": cells})),
                (cbm, "section_9_5", lambda *a: {"pass": True, "worst": 0.0}),
                (ro, "BF", str(g / "bf")), (ro, "NS_R", str(g / "ns")), (ro, "partb_sums", lambda: sums),
                (ro, "Cells", FakeCells), (ro, "x01", lambda cells_, paths, phi, tag: np.zeros(N)),
                (ro, "CHECKS", collections.OrderedDict())):
            p = mock.patch.object(target, attr, value, create=(attr == "O_NOATIME"))
            p.start()
            self.addCleanup(p.stop)
        p = mock.patch.dict(ro.PIN, self.pins)
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(sys, "path", [str(HERE.parents[2] / "nd-unfolding")] + sys.path)   # the stubbed MAT step's
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.dict(os.environ, {"TMPDIR": str(self.d / "tmp")})
        p.start()
        self.addCleanup(p.stop)
        self.addCleanup(lambda: cbm.AUDIT is not None and cbm.AUDIT.uninstall())   # main never uninstalls it

    def test_main_reads_every_rollup_input_through_noatime_copies(self):
        out = self.d / "c95.json"
        with mock.patch("sys.stdout", new=types.SimpleNamespace(write=lambda s: None, flush=lambda: None)):
            code = self.cbm.main(["control95", "--out", str(out)])
        rec = json.loads(out.read_text())
        self.assertEqual(rec["open_audit"]["refused"], [])
        self.assertEqual({k: rec["inputs"][k] for k in self.pins}, {k: v[1] for k, v in self.pins.items()})
        self.assertEqual(len([k for k in rec["inputs"] if k.startswith(str(self.g / "bf"))]),
                         2 * len(self.cbm.rollup().BR.PLAYLISTS))
        self.assertTrue(self.opened)
        self.assertFalse([n for n in self.opened if n.startswith(str(self.g))])    # the rollup read only the copies
        if self.noatime:
            self.assertEqual((code, rec["verdict"], rec["stop"]), (0, "PASS", []))
        else:
            self.assertEqual([x for x in rec["stop"] if not x.startswith("atime moved")], [])


@unittest.skipUnless(HAVE, "needs PyROOT (the rollup imports it)")
class Section95(unittest.TestCase):
    """The control's plumbing on arrays: part B's labels, the comparison against production_cov.npz's keys."""
    def setUp(self):
        f = fixture(7)
        sums = {f"U_{b}_{i}/xsec.root": "x" for b in c.ORDER for i in range(c.BANDS[b])}
        sums.update({"ER/xsec.root": "x"})
        self.labels = cb.partb_labels(sums)
        vecs = {}
        r = np.random.default_rng(11)
        for b, labs in self.labels["universe"].items():
            for l in labs:
                vecs[l] = f["x_R"] + 0.05 * r.standard_normal(N)
        for l in self.labels["lateral"].values():
            vecs[l] = f["x_R"] + 0.05 * r.standard_normal(N)
        for l in self.labels["replica"]:
            vecs[l] = f["x_R"] + 0.03 * r.standard_normal(N)
        self.vec, self.f = vecs.__getitem__, f
        ro = cb.rollup()
        bands = {b: np.stack([vecs[l] for l in labs]) for b, labs in self.labels["universe"].items()}
        for b in c.LATERAL_BANDS:
            bands[b] = np.stack([vecs[self.labels["lateral"][f"{b}_{i}"]] for i in (0, 1)])
        blocks, tot = ro.universe_block(cb.CellsT(f["rep"], f["x_R"]), bands, f["w"], f["minos_x"])
        X = np.stack([vecs[l] for l in self.labels["replica"]])
        self.npz = {"universe": tot, "stat": np.cov(X, rowvar=False), "cells_x_EU": f["x_R"],
                    **{f"band_{b}": m for b, m in blocks.items()}}

    def run95(self, npz):
        return cb.section_9_5(self.vec, self.labels, self.f["minos_x"], self.f["w"], self.f["x_R"], self.f["rep"], npz)

    def test_labels_are_part_bs(self):
        self.assertEqual(sum(len(v) for v in self.labels["universe"].values()), 175)
        self.assertEqual(self.labels["lateral"]["Muon_Energy_MINOS_1"], "S3_MuonEnergyMINOS1")
        self.assertEqual(self.labels["replica"][0], "S1_001")
        self.assertEqual(self.labels["replica"][-1], "S1_300")

    def test_reproduces_and_passes(self):
        out = self.run95(self.npz)
        self.assertTrue(out["pass"], out)
        self.assertEqual(out["worst"], 0.0)
        self.assertEqual(len(out["bands"]), 44)

    def test_a_changed_band_or_stat_or_cells_fails(self):
        for key, change in (("band_MaRES", lambda m: m * (1 + 1e-9)), ("stat", lambda m: m * (1 + 1e-9)),
                            ("cells_x_EU", lambda m: m * (1 + 1e-15))):
            with self.subTest(key):
                npz = dict(self.npz, **{key: change(self.npz[key])})
                self.assertFalse(self.run95(npz)["pass"])

    def test_a_missing_band_key_fails(self):
        npz = {k: v for k, v in self.npz.items() if k != "band_GEANT_Pion"}
        out = self.run95(npz)
        self.assertFalse(out["pass"])
        self.assertEqual(out["missing_in_npz"], ["band_GEANT_Pion"])


class Audit(unittest.TestCase):
    """The director's open audit: a read of an unredirected guarded path is refused; sanctioned reads pass."""
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.d = Path(self.td.name).resolve()
        (self.d / "guarded").mkdir()
        (self.d / "guarded" / "f.txt").write_text("x")
        (self.d / "free.txt").write_text("y")
        import cov2d_blocks as cbm
        self.cbm = cbm
        self.audit = cbm.OpenAudit(guarded=(str(self.d / "guarded"),)).install()
        self.addCleanup(self.audit.uninstall)
        p = mock.patch.object(cbm, "AUDIT", self.audit)
        p.start()
        self.addCleanup(p.stop)
        q = mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True)
        q.start()
        self.addCleanup(q.stop)

    def test_unredirected_guarded_reads_are_refused(self):
        import io as io_
        g = self.d / "guarded" / "f.txt"
        for how, fn in (("open", lambda: open(g)), ("io.open", lambda: io_.open(g)),
                        ("Path.read_text", lambda: g.read_text()), ("os.open", lambda: os.open(g, os.O_RDONLY)),
                        ("np.load", lambda: np.load(g))):
            with self.subTest(how), self.assertRaises(c.Refusal):
                fn()
        self.assertGreaterEqual(len(self.audit.refused), 5)

    def test_sanctioned_noatime_reads_and_free_paths_pass_and_are_logged(self):
        data, _ = self.cbm.read_noatime(self.d / "guarded" / "f.txt")
        self.assertEqual(data, b"x")
        self.assertEqual((self.d / "free.txt").read_text(), "y")
        paths = [p for _, p, _ in self.audit.log]
        self.assertIn(str(self.d / "free.txt"), paths)
        self.assertIn(str(self.d / "guarded" / "f.txt"), paths)
        self.assertEqual(self.audit.refused, [])

    def test_counts_guarded_opens(self):
        g = self.d / "guarded" / "f.txt"
        self.cbm.read_noatime(g)
        self.cbm.read_noatime(g)
        (self.d / "free.txt").read_text()
        n = self.audit.counts()
        self.assertEqual((n["guarded_opens_total"], n["guarded_opens_distinct"]), (2, 1))

    def test_uninstall_restores(self):
        import builtins
        self.audit.uninstall()
        self.assertEqual((self.d / "guarded" / "f.txt").read_text(), "x")   # no audit now
        self.assertIsNot(builtins.open, None)

    @unittest.skipUnless(HAVE, "needs PyROOT")
    def test_tfile_open_is_audited(self):
        import ROOT
        a2 = self.cbm.OpenAudit(guarded=(str(self.d / "guarded"),)).install(ROOT)
        self.addCleanup(a2.uninstall)
        with self.assertRaises(c.Refusal):
            ROOT.TFile.Open(str(self.d / "guarded" / "x.root"), "RECREATE")

    def test_bypass_scan_fires_on_each_bypass_and_not_on_the_real_modules(self):
        f = self.d / "bad.py"
        f.write_text("import subprocess\nimport os\nfrom paths import CV_PATH\nos.system('x')\n"
                     "import ROOT\nROOT.TFile('a.root')\n")
        hits = self.cbm.bypass_scan([f])[str(f)]
        self.assertEqual(len(hits), 4, hits)
        if HAVE:
            real = self.cbm.bypass_scan(self.cbm.scan_targets(self.cbm.rollup()))
            self.assertEqual({k: v for k, v in real.items() if v}, {})
            self.assertEqual(len(real), 5)


class MatEnvironment(unittest.TestCase):
    """The control uses RPD's own mat_environment, imported (not copied), and a refusal propagates."""
    @classmethod
    def setUpClass(cls):
        nd = str(HERE.parents[2] / "nd-unfolding")
        if nd not in sys.path:
            sys.path.insert(0, nd)
    def test_it_is_rpds_function_and_a_refusal_propagates(self):
        import cov2d_blocks as cbm
        import fd_rpd_inputs as rpd
        with mock.patch.object(rpd, "mat_environment", side_effect=rpd.Refuse(7, "not pinned")) as m:
            with self.assertRaises(rpd.Refuse):
                cbm.pinned_mat_environment()
        m.assert_called_once_with()
        with mock.patch.object(rpd, "mat_environment", return_value={"ok": 1}):
            self.assertEqual(cbm.pinned_mat_environment(), {"ok": 1})

    def test_rpds_pins_are_the_six_scripts_and_libmat(self):
        import fd_rpd_inputs as rpd
        self.assertEqual(len(rpd.MAT_SETUP), 6)
        self.assertEqual(sorted(Path(p).name for p in rpd.MAT_SETUP),
                         ["setup.sh", "setup.sh", "setup_MAT-MINERvA.sh", "setup_MAT.sh", "setup_UnfoldUtils.sh",
                          "setup_salloc_env.sh"])
        self.assertEqual({Path(p).name for p in rpd.MAT_MAPPED}, {"libMAT.so"})
        self.assertEqual(Path(rpd.MAT_LINK[0]).name, "libMATDict.so")


if __name__ == "__main__":
    unittest.main()
