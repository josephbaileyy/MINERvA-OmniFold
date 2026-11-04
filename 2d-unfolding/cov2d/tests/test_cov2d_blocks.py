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


if __name__ == "__main__":
    unittest.main()
