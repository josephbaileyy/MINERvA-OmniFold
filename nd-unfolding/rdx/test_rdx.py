"""RDX tests (RDX-DECLARATION.md rev 3 §2): C1's patch, C3's widened regressor, C2's sidecar and C4's checkers.

    python3 -m unittest -v nd-unfolding/rdx/test_rdx.py
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ND = HERE.parent
ROOT = ND.parent
for p in (str(HERE), str(ND / "rsn"), str(ND / "pv-ladder"), str(ND)):
    if p not in sys.path:
        sys.path.insert(0, p)
import omnifold_nn_core as onc  # noqa: E402
import pvl_lib as L  # noqa: E402
import rdx_unfold as UF  # noqa: E402

REWEIGHT = onc._reweight
LO = np.array([L.FINE[a][0] for a in L.AXES5])
HI = np.array([min(L.FINE[a][-1], c) for a, c in zip(L.AXES5, (4.5, 20.0, 3.0, 2.0, 3.0))])


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------- stubs for the loop


class StubClf:
    def __init__(self, **kw):
        self.params = dict(kw)

    def get_params(self):
        return dict(self.params)

    def fit(self, X, y, sample_weight=None):
        X, y = np.asarray(X), np.asarray(y)
        w = np.ones(len(y)) if sample_weight is None else np.asarray(sample_weight, float)
        self.cut = float(np.median(X[:, 0]))
        lo = X[:, 0] < self.cut
        self.p = [float(w[m & (y == 1)].sum() / w[m].sum()) for m in (lo, ~lo)]
        return self

    def predict_proba(self, X):
        p = np.where(np.asarray(X)[:, 0] < self.cut, self.p[0], self.p[1])
        return np.column_stack([1 - p, p])


class StubReg(StubClf):
    """Records every fit's and predict's X and sample weight; predicts from the LAST column, so widening shows."""
    fits: list = []
    preds: list = []

    def fit(self, X, y, sample_weight=None):
        X = np.asarray(X)
        StubReg.fits.append({"X": X.copy(), "w": None if sample_weight is None else np.array(sample_weight)})
        w = np.ones(len(y)) if sample_weight is None else np.asarray(sample_weight, float)
        lo = X[:, -1] < np.median(X[:, -1])
        self.m = [float((w * np.asarray(y))[s].sum() / w[s].sum()) if s.any() else 1.0 for s in (lo, ~lo)]
        self.cut = float(np.median(X[:, -1]))
        return self

    def predict(self, X):
        X = np.asarray(X)
        StubReg.preds.append({"X": X.copy()})
        return np.where(X[:, -1] < self.cut, self.m[0], self.m[1])


def stub_make(kind, nvars, seed=None):
    return StubClf(), StubClf(), StubReg()


def loop_unfold(d, cols, seed, threads, iters):
    _, wpush = onc.omnifold_loop(d["MCgen"], d["MCreco"], d["measured"], d["pass_reco"], d["pass_truth"],
                                 np.ones(len(d["measured"]), bool), iters, kind="lgbm", MCgen_weights=d["w_truth"],
                                 MCreco_weights=d["w_reco"], measured_weights=d["measured_weights"], seed=seed,
                                 verbose=False)
    return wpush, []


def toy(seed=5, n=3000):
    rng = np.random.default_rng(seed)
    gen = LO + (HI - LO) * rng.random((n, 5))
    reco = gen * rng.normal(1.0, 0.05, (n, 5))
    pt = rng.random(n) < 0.9
    pr = rng.random(n) < (0.4 + 0.5 * (gen[:, 0] / HI[0]))
    w = rng.uniform(0.3, 3.0, n)
    meas = LO + (HI - LO) * rng.random((1500, 5)) ** 1.2
    tx = np.column_stack([rng.uniform(1e3, 2e4, n), rng.normal(0, 400, n), rng.normal(0, 400, n),
                          rng.uniform(5980, 8422, n), rng.exponential(200.0, n)]).astype(np.float64)
    return {"MCgen": gen, "MCreco": reco, "pass_truth": pt, "pass_reco": pr, "w_truth": w, "w_reco": w * 1.1,
            "measured": meas, "measured_weights": np.ones(1500)}, tx


class Loop(unittest.TestCase):
    def setUp(self):
        self.saved = (onc.make_estimators, onc._reweight)
        onc.make_estimators = stub_make
        StubReg.fits, StubReg.preds = [], []

    def tearDown(self):
        onc.make_estimators, onc._reweight = self.saved


# ---------------------------------------------------------------- C3, the widened regressor


class WideRegressor(Loop):
    def test_the_wide_regressor_sees_truthx_aligned_to_the_loops_fit_and_predict_rows(self):
        d, tx = toy()
        ev = {}
        UF.instrument(loop_unfold, ev, False, False, tx)(d, None, 42, 32, 3)
        m = d["pass_truth"]
        pr = d["pass_reco"][m]
        gen = d["MCgen"][m]
        self.assertEqual(len(StubReg.fits), 3)
        self.assertEqual(len(StubReg.preds), 3)
        for f in StubReg.fits:
            self.assertEqual(f["X"].shape[1], 10)
            self.assertTrue(np.array_equal(f["X"][:, :5], gen[pr]))
            self.assertTrue(np.array_equal(f["X"][:, 5:], tx[m][pr]))
        for p in StubReg.preds:
            self.assertTrue(np.array_equal(p["X"][:, :5], gen[~pr]))
            self.assertTrue(np.array_equal(p["X"][:, 5:], tx[m][~pr]))
        self.assertEqual((ev["fit_calls"], ev["predict_calls"]), (3, 3))
        self.assertIs(onc.make_estimators, stub_make)
        self.assertIs(onc._reweight, REWEIGHT)

    def test_without_truthx_the_wrapper_reproduces_the_plain_loop_and_widening_changes_it(self):
        d, tx = toy()
        plain, _ = loop_unfold(d, None, 42, 32, 3)
        same, _ = UF.instrument(loop_unfold, {}, False, False, None)(d, None, 42, 32, 3)
        self.assertTrue(np.array_equal(plain, same))
        self.assertTrue(all(f["X"].shape[1] == 5 for f in StubReg.fits))
        wide, _ = UF.instrument(loop_unfold, {}, False, False, tx)(d, None, 42, 32, 3)
        self.assertFalse(np.array_equal(plain, wide))

    def test_the_weight_composes_with_the_wide_regressor(self):
        d, tx = toy()
        UF.instrument(loop_unfold, {}, True, False, tx)(d, None, 42, 32, 2)
        m = d["pass_truth"]
        pr = d["pass_reco"][m]
        wt = d["w_truth"][m][pr]
        self.assertTrue(np.array_equal(StubReg.fits[0]["w"], wt))  # w_push is ones before the first iteration
        self.assertEqual(StubReg.fits[0]["X"].shape[1], 10)

    def test_a_sidecar_with_the_wrong_row_count_refuses(self):
        d, tx = toy()
        with self.assertRaises(UF.RdxError) as cm:
            UF.instrument(loop_unfold, {}, False, False, tx[:-1])(d, None, 42, 32, 2)
        self.assertIn("rows", str(cm.exception))

    def test_a_loop_that_predicts_on_other_rows_refuses(self):
        d, tx = toy()

        def bad_loop(dd, cols, seed, threads, iters):
            out = loop_unfold(dd, cols, seed, threads, iters)
            onc.make_estimators("lgbm", 5)[2].predict(np.zeros((3, 5)))
            return out

        with self.assertRaises(UF.RdxError):
            UF.instrument(bad_loop, {}, False, False, tx)(d, None, 42, 32, 2)

    def test_the_transfer_probe_uses_rdx_mask_and_the_widened_rows(self):
        d, tx = toy()
        plain, _ = UF.instrument(loop_unfold, {}, False, False, tx)(d, None, 42, 32, 2)
        StubReg.fits = []
        ev = {}
        out, _ = UF.instrument(loop_unfold, ev, False, True, tx)(d, None, 42, 32, 2)
        self.assertTrue(np.array_equal(plain, out))
        m = d["pass_truth"]
        pr = d["pass_reco"][m]
        n = int(pr.sum())
        mk = UF.mask_of(n, 1)
        probe = StubReg.fits[2]
        self.assertEqual(probe["X"].shape, (n - int(mk.sum()), 10))
        self.assertTrue(np.array_equal(probe["X"][:, 5:], tx[m][pr][~mk]))
        self.assertEqual([r["iteration"] for r in ev["transfer_records"]], [0, 1])
        self.assertEqual((UF.TRANSFER_SEED, UF.TRANSFER_FRACTION), (20261112, 0.2))
        self.assertFalse(np.array_equal(UF.mask_of(n, 1), np.random.default_rng([20261111, 1]).random(n) < 0.2))


class Permutation(unittest.TestCase):
    def test_the_permutation_is_joint_seeded_and_deterministic(self):
        _, tx = toy()
        a, b = UF.permuted(tx, 20261113), UF.permuted(tx, 20261113)
        self.assertTrue(np.array_equal(a, b))
        idx = np.random.default_rng(20261113).permutation(len(tx))
        self.assertTrue(np.array_equal(a, tx[idx]))
        self.assertFalse(np.array_equal(a, tx))
        self.assertFalse(np.array_equal(a, UF.permuted(tx, 20261114)))
        self.assertTrue(np.array_equal(np.sort(a[:, 0]), np.sort(tx[:, 0])))


def write_sidecar(dirpath: Path, tx, npz_sha, names=UF.TRUTHX_NAMES, schema=UF.SIDECAR_SCHEMA):
    p = Path(dirpath) / "truthx.npz"
    np.savez(p, truthx=tx, truthx_names=np.array(names), mc_id=np.zeros((len(tx), 4), np.int64),
             meta=json.dumps({"schema": schema, "npz_sha256": npz_sha}))
    return p


class Sidecar(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.dir = Path(self.td.name)
        self.npz = self.dir / "inputs.npz"
        np.savez(self.npz, MCgen=np.zeros((4, 5), np.float32))
        self.tx = np.arange(20, dtype=np.float64).reshape(4, 5) + 1.0

    def tearDown(self):
        self.td.cleanup()

    def test_a_good_sidecar_loads(self):
        p = write_sidecar(self.dir, self.tx, sha(self.npz))
        tx, meta = UF.load_sidecar(p, sha(p), self.npz)
        self.assertTrue(np.array_equal(tx, self.tx))
        self.assertEqual(meta["schema"], UF.SIDECAR_SCHEMA)

    def test_the_sidecar_refusals(self):
        good = sha(self.npz)
        cases = {
            "sidecar sha": (self.tx, good, UF.TRUTHX_NAMES, UF.SIDECAR_SCHEMA, "0" * 64),
            "npz": (self.tx, "1" * 64, UF.TRUTHX_NAMES, UF.SIDECAR_SCHEMA, None),
            "columns": (self.tx, good, UF.TRUTHX_NAMES[::-1], UF.SIDECAR_SCHEMA, None),
            "schema": (self.tx, good, UF.TRUTHX_NAMES, "other/1", None),
            "float64": (self.tx.astype(np.float32), good, UF.TRUTHX_NAMES, UF.SIDECAR_SCHEMA, None),
            "finite": (np.where(self.tx == 7.0, np.nan, self.tx), good, UF.TRUTHX_NAMES, UF.SIDECAR_SCHEMA, None),
        }
        for what, (tx, npz_sha, names, schema, override) in cases.items():
            with self.subTest(what):
                sub = self.dir / what.replace(" ", "_")
                sub.mkdir()
                p = write_sidecar(sub, tx, npz_sha, names, schema)
                with self.assertRaises(UF.RdxError):
                    UF.load_sidecar(p, override or sha(p), self.npz)


class Arguments(unittest.TestCase):
    def test_the_argument_refusals(self):
        bad = [
            ["--regressor-features", "wide"],
            ["--regressor-features", "std", "--truthx-sidecar", "x.npz", "--expect-truthx-sha256", "0" * 64],
            ["--regressor-features", "std", "--truthx-permute", "20261113"],
            ["--regressor-features", "wide", "--truthx-sidecar", "x.npz"],
            ["--regressor-features", "std", "--truth", "q3"],
        ]
        for argv in bad:
            with self.subTest(argv=argv):
                with self.assertRaises(UF.RdxError):
                    UF.main(argv)


if __name__ == "__main__":
    unittest.main()
