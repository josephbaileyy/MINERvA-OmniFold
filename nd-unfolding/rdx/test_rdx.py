"""RDX tests (RDX-DECLARATION.md rev 3 §2): C1's patch, C3's widened regressor, C2's sidecar and C4's checkers.

    python3 -m unittest -v nd-unfolding/rdx/test_rdx.py
"""
from __future__ import annotations

import hashlib
import json
import math
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


# ---------------------------------------------------------------- C2, the sidecar's rows


import types  # noqa: E402

if "ROOT" not in sys.modules:  # und imports ROOT at load; the collector itself never calls it
    class _Any:
        def __getattr__(self, k):
            return _Any()

        def __call__(self, *a, **k):
            return _Any()

    _root = types.ModuleType("ROOT")
    _root.__getattr__ = lambda k: _Any()
    sys.modules["ROOT"] = _root
sys.path.insert(0, str(ROOT / "2d-unfolding"))
import rdx_common as RC  # noqa: E402
import rdx_dump as DP  # noqa: E402
import rdx_truthx_npz as TN  # noqa: E402
import rdx_truthx_rows as TR  # noqa: E402
import unfold_2d_omnifold_unbinned as u2d  # noqa: E402
import unfold_nd_omnifold_unbinned as und  # noqa: E402

EX_T = [und.EXTRA_AXES[x]["truth"] for x in DP.AXES]
EX_R = [und.EXTRA_AXES[x]["reco"] for x in DP.AXES]
BOUNDS = (u2d.PT_EDGES[0], u2d.PT_EDGES[-1], u2d.PZ_EDGES[0], u2d.PZ_EDGES[-1])
POT = 0.2205


class FakeTree:
    """The TTree surface collect_signal_nd uses, over in-memory columns."""

    def __init__(self, cols):
        self.cols, self.bound = cols, {}

    def GetName(self):
        return "mc_signal_reco"

    def GetBranch(self, name):
        return name in self.cols

    def SetBranchAddress(self, name, buf):
        self.bound[name] = buf
        return 0

    def GetEntries(self):
        return len(self.cols["MC"])

    def GetEntry(self, i):
        for k, b in self.bound.items():
            b[0] = self.cols[k][i]


def signal_columns(seed=11, n=4000, run0=110000):
    """Rows built to hit every branch of the kept-row walk: bad weights, non-finite truth, -9999 truth sentinels,
    out-of-phase-space truth with and without a reco pass, and reco outside the box."""
    rng = np.random.default_rng(seed)
    c = {"MC": rng.uniform(-0.2, 5.0, n), "MC_pz": rng.uniform(1.0, 70.0, n), "sim": rng.uniform(-0.2, 5.0, n),
         "sim_pz": rng.uniform(1.0, 70.0, n), "sim_pass": (rng.random(n) < 0.7).astype(np.uint8),
         "w_truth": rng.uniform(0.1, 3.0, n), "w_reco": rng.uniform(0.1, 3.0, n)}
    for nm in EX_T + EX_R:
        c[nm] = rng.uniform(0.0, 2.0, n)
    k = rng.choice(n, 60, replace=False)
    c["MC"][k[:10]] = -9999.0          # truth sentinel rows (finite: dropped by phase space unless reco passes)
    c["MC_pz"][k[10:20]] = np.nan      # non-finite truth
    c[EX_T[1]][k[20:30]] = np.inf
    c["w_truth"][k[30:40]] = -1.0      # bad weights
    c["w_reco"][k[40:50]] = 2e4
    c["sim"][k[50:60]] = -9999.0       # miss-like reco
    for i, nm in enumerate(RC.TRUTHX):
        c[nm] = rng.uniform(1.0, 100.0, n) * (i + 1)
    c["truthx_run"] = run0 + rng.integers(0, 3, n)
    c["truthx_subrun"] = rng.integers(0, 50, n)
    c["truthx_evt"] = np.arange(n)
    return c


def with_border_rows(c: dict) -> dict:
    """Append rows whose muon angle sits within a few ulps of the 20-degree cut, inside the box, reco-failing."""
    theta = u2d.MAX_MUON_THETA_RAD
    pz = np.linspace(2.0, 12.0, 40)
    pt0 = pz * math.tan(theta)
    pts = np.concatenate([pt0, np.nextafter(pt0, 0), np.nextafter(pt0, 9), np.nextafter(np.nextafter(pt0, 9), 9)])
    pzs = np.tile(pz, 4)
    n = len(pts)
    out = {k: np.concatenate([np.asarray(v), np.asarray(v)[:n]]) for k, v in c.items()}
    out["MC"][-n:], out["MC_pz"][-n:] = pts, pzs
    out["sim_pass"][-n:] = 0
    out["w_truth"][-n:] = out["w_reco"][-n:] = 1.0
    for nm in EX_T:
        out[nm][-n:] = 0.5
    out["truthx_evt"][-n:] = np.arange(n) + 10**6
    return out


class KeptRows(unittest.TestCase):
    def test_the_replica_equals_the_collector_row_for_row(self):
        c = signal_columns()
        sig = und.collect_signal_nd(FakeTree(c), [dict(und.EXTRA_AXES[x], name=x) for x in DP.AXES], *BOUNDS, POT,
                                    use_weights=True)
        ent, arr = DP.kept_walk(c, EX_T, EX_R, BOUNDS, POT, u2d.in_truth_phase_space)
        self.assertTrue(0 < len(ent) < len(c["MC"]))
        gen = np.column_stack([sig["truth_pt"], sig["truth_pz"], *sig["truth_extras"]]).astype(np.float32)
        reco = np.column_stack([sig["reco_pt"], sig["reco_pz"], *sig["reco_extras"]]).astype(np.float32)
        for k, v in (("MCgen", gen), ("MCreco", reco), ("pass_reco", sig["pass_reco"]),
                     ("pass_truth", sig["pass_truth"]), ("w_truth", sig["w_truth"]), ("w_reco", sig["w_reco"])):
            self.assertTrue(np.array_equal(arr[k], v), k)
        self.assertTrue(np.array_equal(arr["MCgen"][:, 0], np.asarray(c["MC"])[ent].astype(np.float32)))

    def test_the_vectorized_walk_equals_the_loop_bitwise(self):
        c = with_border_rows(signal_columns())
        ent0, arr0 = DP.kept_walk(c, EX_T, EX_R, BOUNDS, POT, u2d.in_truth_phase_space)
        ent1, arr1 = DP.kept_walk_np(c, EX_T, EX_R, BOUNDS, POT, u2d.in_truth_phase_space, u2d.MAX_MUON_THETA_RAD)
        self.assertTrue(np.array_equal(ent0, ent1))
        for k in arr0:
            self.assertEqual(arr0[k].dtype, arr1[k].dtype, k)
            self.assertTrue(np.array_equal(arr0[k], arr1[k]), k)

    def test_rows_at_the_angle_cut_are_decided_by_the_reference_function(self):
        c = with_border_rows(signal_columns())
        theta = u2d.MAX_MUON_THETA_RAD

        def flipped(pt, pz, *box):  # disagrees with arctan2 on the border rows, as a last-bit libm difference would
            ok = u2d.in_truth_phase_space(pt, pz, *box)
            return (not ok) if ok is not None and abs(math.atan2(pt, pz) - theta) <= DP.BORDER else ok

        ent0, arr0 = DP.kept_walk(c, EX_T, EX_R, BOUNDS, POT, flipped)
        ent1, arr1 = DP.kept_walk_np(c, EX_T, EX_R, BOUNDS, POT, flipped, theta)
        self.assertTrue(np.array_equal(ent0, ent1))
        self.assertTrue(np.array_equal(arr0["pass_truth"], arr1["pass_truth"]))
        plain, _ = DP.kept_walk_np(c, EX_T, EX_R, BOUNDS, POT, u2d.in_truth_phase_space, theta)
        self.assertFalse(np.array_equal(ent1, plain))  # the border rows are present and do matter

    def test_a_replica_that_differs_from_the_npz_refuses(self):
        c = signal_columns()
        _, arr = DP.kept_walk(c, EX_T, EX_R, BOUNDS, POT, u2d.in_truth_phase_space)
        DP.check_against_npz(arr, arr)
        for k in ("MCgen", "w_truth", "pass_reco"):
            with self.subTest(k):
                bad = dict(arr)
                bad[k] = np.roll(arr[k], 1, axis=0)
                with self.assertRaises(DP.DumpError):
                    DP.check_against_npz(bad, arr)
        bad = dict(arr, MCgen=arr["MCgen"].astype(np.float64))
        with self.assertRaises(DP.DumpError):
            DP.check_against_npz(bad, arr)

    def test_the_dump_uses_the_vectorized_walk(self):
        src = (HERE / "rdx_dump.py").read_text()
        main = src[src.index("def main("):]
        self.assertIn("theta_max=u2d.MAX_MUON_THETA_RAD", main)

    def test_the_playlist_index_and_its_refusals(self):
        per = [np.array([1, 1, 2]), np.array([5, 6])]
        self.assertTrue(np.array_equal(DP.playlist_index(np.array([2, 5, 1, 6]), per), [0, 1, 0, 1]))
        with self.assertRaises(DP.DumpError):
            DP.playlist_index(np.array([1]), [np.array([1]), np.array([1])])
        with self.assertRaises(DP.DumpError):
            DP.playlist_index(np.array([9]), per)


def write_npz(path: Path, arr: dict):
    np.savez(path, MCgen=arr["MCgen"], MCreco=arr["MCreco"], pass_reco=arr["pass_reco"],
             pass_truth=arr["pass_truth"], w_truth=arr["w_truth"], w_reco=arr["w_reco"])


class Pipeline(unittest.TestCase):
    """C2's build and C4's per-row join on a two-playlist toy, with D6's two mutants run through the sidecar."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        d = Path(self.td.name)
        self.per = {"1A": signal_columns(3, 1500, 110000), "1B": signal_columns(4, 1200, 120000)}
        self.merged = {k: np.concatenate([self.per["1A"][k], self.per["1B"][k]]) for k in self.per["1A"]}
        self.paths = {"merged": d / "merged.root", "1A": d / "1A.root", "1B": d / "1B.root"}
        self.files = {str(self.paths["merged"]): self.merged, str(self.paths["1A"]): self.per["1A"],
                      str(self.paths["1B"]): self.per["1B"]}
        _, self.arr = DP.kept_walk(self.merged, EX_T, EX_R, BOUNDS, POT, u2d.in_truth_phase_space)
        self.npz = d / "lat.npz"
        write_npz(self.npz, self.arr)
        self.side = d / "truthx.npz"
        self.meta = DP.build(self.paths["merged"], self.npz, [("1A", self.paths["1A"]), ("1B", self.paths["1B"])],
                             self.side, self.reader, BOUNDS, POT, u2d.in_truth_phase_space, EX_T, EX_R)

    def tearDown(self):
        self.td.cleanup()

    def reader(self, path, tree, cols):
        return {k: np.asarray(self.files[str(path)][k]) for k in cols}

    def resave(self, **kw):
        with np.load(self.side, allow_pickle=False) as s:
            out = {k: s[k] for k in s.files}
        out.update(kw)
        np.savez(self.side, **out)

    def test_the_sidecar_joins_back_to_every_playlist_row(self):
        self.assertEqual(self.meta["rows"], len(self.arr["MCgen"]))
        with np.load(self.side) as s:
            self.assertEqual(s["truthx"].dtype, np.float64)
            self.assertEqual(s["mc_id"].dtype, np.int64)
            self.assertEqual(set(s["mc_id"][:, 0].tolist()), {0, 1})
        res = TN.check(self.npz, self.side, self.reader)
        self.assertEqual(res["verdict"], "PASS", res["failures"])
        self.assertEqual(sum(v["joined"] for v in res["per_playlist"].values()), len(self.arr["MCgen"]))

    def test_the_vectorized_build_joins_too(self):
        side = Path(self.td.name) / "truthx_np.npz"
        meta = DP.build(self.paths["merged"], self.npz, [("1A", self.paths["1A"]), ("1B", self.paths["1B"])], side,
                        self.reader, BOUNDS, POT, u2d.in_truth_phase_space, EX_T, EX_R, theta_max=u2d.MAX_MUON_THETA_RAD)
        self.assertEqual(meta["walk"], "vectorized (kept_walk_np)")
        with np.load(side) as a, np.load(self.side) as b:
            self.assertTrue(np.array_equal(a["truthx"], b["truthx"]))
            self.assertTrue(np.array_equal(a["mc_id"], b["mc_id"]))
        self.assertEqual(TN.check(self.npz, side, self.reader)["verdict"], "PASS")

    def test_mutant_d6a_truthx_offset_by_one_row_fails_the_join(self):
        with np.load(self.side) as s:
            tx = s["truthx"]
        self.resave(truthx=np.roll(tx, 1, axis=0))
        res = TN.check(self.npz, self.side, self.reader)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("truthx_enu" in f for f in res["failures"]))

    def test_mutant_d6b_mask_on_truthx_alone_fails_the_join(self):
        # truthx taken through a different row selection (the collector's mask dropped, a same-sized subset
        # of all rows instead), with mc_id left on the npz's rows: count and marginals plausible, association lost
        c, n = self.merged, len(self.arr["MCgen"])
        tx_all = np.column_stack([np.asarray(c[k], np.float64) for k in RC.TRUTHX])
        self.resave(truthx=tx_all[:n])
        res = TN.check(self.npz, self.side, self.reader)
        self.assertEqual(res["verdict"], "FAIL")

    def test_a_sidecar_for_another_npz_or_with_duplicate_ids_refuses(self):
        other = Path(self.td.name) / "other.npz"
        write_npz(other, dict(self.arr, w_truth=self.arr["w_truth"] * 2))
        with self.assertRaises(RC.CheckError):
            TN.check(other, self.side, self.reader)
        with np.load(self.side) as s:
            mc = s["mc_id"].copy()
        mc[1] = mc[0]
        self.resave(mc_id=mc)
        res = TN.check(self.npz, self.side, self.reader)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertIn("mc_id values are not unique", res["failures"])

    def test_a_weight_or_coordinate_mismatch_fails_the_join(self):
        self.files[str(self.paths["1B"])] = dict(self.per["1B"], w_truth=self.per["1B"]["w_truth"] * (1 + 1e-12))
        res = TN.check(self.npz, self.side, self.reader)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("w_truth" in f for f in res["failures"]))

    def test_the_build_refuses_an_npz_the_replica_does_not_reproduce(self):
        other = Path(self.td.name) / "other.npz"
        write_npz(other, dict(self.arr, w_reco=self.arr["w_reco"] * 2))
        with self.assertRaises(DP.DumpError):
            DP.build(self.paths["merged"], other, [("1A", self.paths["1A"]), ("1B", self.paths["1B"])],
                     Path(self.td.name) / "t3.npz", self.reader, BOUNDS, POT, u2d.in_truth_phase_space, EX_T, EX_R)

    def test_the_build_refuses_to_overwrite_and_refuses_a_non_finite_truthx(self):
        with self.assertRaises(DP.DumpError):
            DP.build(self.paths["merged"], self.npz, [("1A", self.paths["1A"]), ("1B", self.paths["1B"])], self.side,
                     self.reader, BOUNDS, POT, u2d.in_truth_phase_space, EX_T, EX_R)
        ent, _ = DP.kept_walk(self.merged, EX_T, EX_R, BOUNDS, POT, u2d.in_truth_phase_space)
        self.merged["truthx_vtx_y"] = self.merged["truthx_vtx_y"].copy()
        self.merged["truthx_vtx_y"][ent[3]] = np.nan
        with self.assertRaises(DP.DumpError):
            DP.build(self.paths["merged"], self.npz, [("1A", self.paths["1A"]), ("1B", self.paths["1B"])],
                     Path(self.td.name) / "t2.npz", self.reader, BOUNDS, POT, u2d.in_truth_phase_space, EX_T, EX_R)


# ---------------------------------------------------------------- C4, the omnifile checks


def omni(seed=7, n_den=500, miss_frac=0.3):
    rng = np.random.default_rng(seed)
    den = {"truthx_run": np.full(n_den, 110000), "truthx_subrun": rng.integers(0, 9, n_den),
           "truthx_evt": np.arange(n_den)}
    for i, k in enumerate(RC.TRUTHX):
        den[k] = rng.uniform(1.0, 50.0, n_den) * (i + 1)
    pick = rng.permutation(n_den)
    sig = {k: np.asarray(v)[pick] for k, v in den.items()}
    miss = rng.random(n_den) < miss_frac
    sig["sim"] = np.where(miss, -9999.0, rng.uniform(0, 4, n_den))
    sig["sim_pass"] = np.where(miss, 0, 1).astype(np.uint8)
    return sig, den


class TruthxRows(unittest.TestCase):
    def test_the_rows_check_passes_and_counts(self):
        sig, den = omni()
        r = TR.check(sig, den)
        self.assertEqual(r["verdict"], "PASS", r["failures"])
        self.assertEqual(r["counts"]["partnerless_rows"], 0)
        self.assertEqual(r["counts"]["matched_rows"], 500)
        self.assertGreater(r["counts"]["matched_miss_rows"], 0)

    def test_a_zeroed_miss_row_a_partnerless_row_and_a_bad_enu_fail(self):
        sig, den = omni()
        z = {k: np.array(v, copy=True) for k, v in sig.items()}
        m = np.flatnonzero(z["sim"] == -9999.0)[0]
        z["truthx_vtx_x"][m] = 0.0  # the KNOWN_ISSUES #12 symptom D1 fixes
        self.assertEqual(TR.check(z, den)["verdict"], "FAIL")
        z = {k: np.array(v, copy=True) for k, v in sig.items()}
        z["truthx_evt"][0] = 10**6
        self.assertEqual(TR.check(z, den)["verdict"], "FAIL")
        z = {k: np.array(v, copy=True) for k, v in sig.items()}
        d2 = {k: np.array(v, copy=True) for k, v in den.items()}
        j = int(np.flatnonzero(d2["truthx_evt"] == z["truthx_evt"][0])[0])
        z["truthx_enu"][0] = d2["truthx_enu"][j] = 0.0
        self.assertEqual(TR.check(z, d2)["verdict"], "FAIL")

    def test_duplicate_identities_refuse(self):
        sig, den = omni()
        den["truthx_evt"] = den["truthx_evt"].copy()
        den["truthx_evt"][1] = den["truthx_evt"][0]
        den["truthx_subrun"] = den["truthx_subrun"].copy()
        den["truthx_subrun"][1] = den["truthx_subrun"][0]
        with self.assertRaises(RC.CheckError):
            TR.check(sig, den)


class Keys(unittest.TestCase):
    def test_packing_and_lookup(self):
        k = RC.pack([1, 2, 2], [0, 5, 5], [7, 8, 9])
        self.assertEqual(len(set(k.tolist())), 3)
        sk, order = RC.index_of(k, "t")
        self.assertTrue(np.array_equal(RC.lookup(sk, order, RC.pack([2, 3], [5, 0], [9, 0])), [2, -1]))
        with self.assertRaises(RC.CheckError):
            RC.pack([1], [1 << RC.SUB_BITS], [0])
        with self.assertRaises(RC.CheckError):
            RC.index_of(RC.pack([1, 1], [0, 0], [3, 3]), "t")


# ---------------------------------------------------------------- C4, alignment and provenance

import difflib  # noqa: E402

sys.path.insert(0, str(ROOT / "publication/w2"))
import rdx_align as AL  # noqa: E402
import rdx_provenance as PV  # noqa: E402


def same(a, b):
    a, b = np.asarray(a), np.asarray(b)
    if a.shape != b.shape:
        return False
    return bool(np.array_equal(a, b, equal_nan=np.issubdtype(a.dtype, np.floating)))


def omnifile_dicts():
    ref = {"mc_signal_reco": {"n": 3, "cols": {"MC": np.array([1.0, np.nan, 2.0]), "sim_pass": np.array([1, 0, 1])},
                              "skipped": ["part_gen_E"]},
           "mc_truth_denom": {"n": 2, "cols": {"MC": np.array([1.0, 2.0])}, "skipped": []},
           "mc_background": {"n": 1, "cols": {"w_bkg": np.array([0.5])}, "skipped": []},
           "data": {"n": 1, "cols": {"measured": np.array([3.0])}, "skipped": []}}
    pat = {t: {"n": v["n"], "cols": dict(v["cols"]), "skipped": list(v["skipped"])} for t, v in ref.items()}
    for t in RC.C1_TREES:
        for b in RC.C1_BRANCHES:
            pat[t]["cols"][b] = np.ones(pat[t]["n"])
    return ref, pat


class Align(unittest.TestCase):
    def test_equal_with_exactly_c1s_extras_passes(self):
        ref, pat = omnifile_dicts()
        r = AL.compare(ref, pat, same)
        self.assertEqual(r["verdict"], "PASS", r["failures"])

    def test_the_align_refusals(self):
        cases = {}
        ref, pat = omnifile_dicts()
        pat["mc_signal_reco"]["cols"]["MC"] = np.array([1.0, np.nan, 2.0000001])
        cases["value"] = (ref, pat)
        ref, pat = omnifile_dicts()
        del pat["mc_truth_denom"]["cols"]["truthx_evt"]
        cases["missing extra"] = (ref, pat)
        ref, pat = omnifile_dicts()
        pat["mc_background"]["cols"]["truthx_enu"] = np.ones(1)
        cases["extra on another tree"] = (ref, pat)
        ref, pat = omnifile_dicts()
        del pat["data"]["cols"]["measured"]
        cases["reference branch missing"] = (ref, pat)
        ref, pat = omnifile_dicts()
        pat["data"]["n"] = 2
        cases["entries"] = (ref, pat)
        ref, pat = omnifile_dicts()
        del pat["data"]
        cases["trees"] = (ref, pat)
        for what, (a, b) in cases.items():
            with self.subTest(what):
                self.assertEqual(AL.compare(a, b, same)["verdict"], "FAIL")


class Provenance(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        d = Path(self.td.name)
        self.canon, self.synced, self.lib = d / "canon", d / "synced", d / "lib"
        for root in (self.canon, self.synced):
            for rel in PV.PINS:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
        self.lib.mkdir()
        self.contents = {rel: f"content of {rel}\n".encode() for rel in PV.PINS}
        self.pins = {rel: hashlib.sha256(b).hexdigest() for rel, b in self.contents.items()}
        for rel, b in self.contents.items():
            (self.canon / rel).write_bytes(b)
            (self.synced / rel).write_bytes(b)
        (self.synced / "extra.h").write_bytes(b"x\n")
        (self.lib / "libMAT.so").write_bytes(b"mat")
        (self.lib / "libUnfold.so").write_bytes(b"unf")
        rows = ["# deploy DEPLOY.sha256 0"] + [f"{self.pins[r]}  src_base/{r}" for r in PV.PINS]
        rows += [f"{sha(self.lib / n)}  /opt/lib/{n}" for n in ("libMAT.so", "libUnfold.so")]
        rows += ["0123456789abcdef0123456789abcdef  /x/bld_base/runEventLoopOmniFold"]
        self.man = d / "MANIFEST.sha256"
        self.man.write_text("\n".join(rows) + "\n")
        self.saved = PV.PINS
        PV.PINS = dict(self.pins)

    def tearDown(self):
        PV.PINS = self.saved
        self.td.cleanup()

    def test_a_matching_build_passes_and_lists_the_synced_difference(self):
        r = PV.check(self.man, self.canon, self.lib, self.synced)
        self.assertEqual(r["verdict"], "PASS", r["failures"])
        self.assertEqual(r["synced_vs_s0_src_base"]["only_in_synced"], ["extra.h"])

    def test_a_changed_pin_or_library_or_a_missing_library_fails(self):
        (self.canon / "cuts/MaxPzMu.h").write_bytes(b"changed\n")
        self.assertEqual(PV.check(self.man, self.canon, self.lib, self.synced)["verdict"], "FAIL")
        (self.canon / "cuts/MaxPzMu.h").write_bytes(self.contents["cuts/MaxPzMu.h"])
        (self.lib / "libMAT.so").write_bytes(b"rebuilt")
        self.assertEqual(PV.check(self.man, self.canon, self.lib, self.synced)["verdict"], "FAIL")
        (self.lib / "libMAT.so").write_bytes(b"mat")
        (self.lib / "libUnfold.so").unlink()
        self.assertEqual(PV.check(self.man, self.canon, self.lib, self.synced)["verdict"], "FAIL")

    def test_the_declared_pins_are_build_mp1_s0s(self):
        text = (ROOT / "measurement-paper/phase1/mp1/build_mp1_s0.sh").read_text()
        for rel, pin in self.saved.items():
            self.assertIn(f"[{rel}]={pin}", text)


# ---------------------------------------------------------------- C1, the event-loop patch


SRC = ROOT / "MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp"
PATCH = HERE / "runEventLoopOmniFold-truthx.patch"
GATES = ("dumpTruthx", "haveTruthx", 'getenv("MNV101_DUMP_TRUTHX") != nullptr && getenv("MNV101_DUMP_POINTCLOUD")')
ALLOWED = [re.compile(x) for x in (
    r"^\s*$", r"^\s*//", r"^\s*[{}]\s*$",
    r'^\s*const bool dumpTruthx = \(getenv\("MNV101_DUMP_TRUTHX"\) != nullptr\);$',
    r"^\s*double rdx_enu = 0\.0, rdx_vtx_x = 0\.0, rdx_vtx_y = 0\.0, rdx_vtx_z = 0\.0, rdx_kep = 0\.0;$",
    r"^\s*int    rdx_run = 0, rdx_subrun = 0, rdx_evt = 0;$",
    r"^\s*double miss_rdx_enu = 0\.0, miss_rdx_vtx_x = 0\.0, miss_rdx_vtx_y = 0\.0,$",
    r"^\s*miss_rdx_vtx_z = 0\.0, miss_rdx_kep = 0\.0;$",
    r"^\s*int    miss_rdx_run = 0, miss_rdx_subrun = 0, miss_rdx_evt = 0;$",
    r'^\s*const bool haveTruthx = \(getenv\("MNV101_DUMP_TRUTHX"\) != nullptr &&$',
    r'^\s*sigOut->GetBranch\("truthx_enu"\) != nullptr\);$',
    r"^\s*if\((dumpTruthx|haveTruthx)\)\s*\{?$",
    r'^\s*"mc_run", "mc_subrun", "mc_nthEvtInFile",$',
    r'^\s*("truthx_[a-z_]+",\s*)+$', r'^\s*("truthx_[a-z_]+",\s*)*"truthx_[a-z_]+"\};$',
    r"^\s*double rdx_enu, rdx_vtx_x, rdx_vtx_y, rdx_vtx_z, rdx_kep;$",
    r'^\s*if\(getenv\("MNV101_DUMP_TRUTHX"\) != nullptr && getenv\("MNV101_DUMP_POINTCLOUD"\) != nullptr\)$',
    r"^inline double RdxLeadingProtonKE\(const CVUniverse\* u\)$",
)]


def patched_text(src_text: str, patch_text: str) -> str:
    with tempfile.TemporaryDirectory() as d:
        Path(d, "runEventLoopOmniFold.cpp").write_text(src_text)
        Path(d, "p.patch").write_text(patch_text)
        r = subprocess.run(["patch", "-p1", "--forward", "-s", "-i", "p.patch"], cwd=d, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"patch failed: {r.stdout}{r.stderr}")
        return Path(d, "runEventLoopOmniFold.cpp").read_text()


def ungated_added_lines(orig: str, new: str) -> list[str]:
    """Added lines that are neither inside a gated block, the KE helper or a declared declaration."""
    a, b = orig.splitlines(), new.splitlines()
    added = set()
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if tag in ("insert", "replace"):
            added.update(range(j1, j2))
    stack, prev, bad = [], "", []
    for j, line in enumerate(b):
        raw = line.split("//")[0]
        code = re.sub(r'"(\\.|[^"\\])*"', '""', raw)  # braces counted outside string literals
        header = (raw.split("{")[0].strip() or prev) if "{" in code else None
        if j in added:
            ok = (any(g in h for h in stack for g in GATES) or any("RdxLeadingProtonKE" in h for h in stack)
                  or any(p.match(line) for p in ALLOWED))
            if not ok:
                bad.append(line)
        for ch in code:
            if ch == "{":
                stack.append(header if header is not None else prev)
            elif ch == "}" and stack:
                stack.pop()
        if raw.strip():
            prev = raw.strip()
    return bad


class Patch(unittest.TestCase):
    def test_the_tracked_source_is_s0s_pin_and_the_patch_applies_to_it(self):
        self.assertEqual(sha(SRC), PV.PINS["runEventLoopOmniFold.cpp"])
        new = patched_text(SRC.read_text(), PATCH.read_text())
        for b in RC.C1_BRANCHES:  # two trees' Branch, the bind, explicitNames (+ the GetBranch probe for enu)
            self.assertEqual(new.count(f'"{b}"'), 5 if b == "truthx_enu" else 4, b)

    def test_every_added_line_is_gated_or_a_declared_declaration(self):
        orig = SRC.read_text()
        self.assertEqual(ungated_added_lines(orig, patched_text(orig, PATCH.read_text())), [])

    def test_an_ungated_fill_is_caught(self):
        orig = SRC.read_text()
        new = patched_text(orig, PATCH.read_text())
        bad = new.replace("    if(dumpTruthx)\n    {\n      rdx_enu = truthCV->GetEnuTrue();",
                          "    rdx_enu = truthCV->GetEnuTrue();\n    if(dumpTruthx)\n    {", 1)
        self.assertNotEqual(bad, new)
        self.assertTrue(ungated_added_lines(orig, bad))

    def test_the_patch_fills_denom_reco_and_miss_rows_and_refuses_both_gates(self):
        new = patched_text(SRC.read_text(), PATCH.read_text())
        for stmt in ("rdx_enu = truthCV->GetEnuTrue();", "rdx_enu = recoCV->GetEnuTrue();",
                     "rdx_kep = RdxLeadingProtonKE(truthCV);", "rdx_kep = RdxLeadingProtonKE(recoCV);",
                     "tde.rdx_enu = rdx_enu; tde.rdx_vtx_x = rdx_vtx_x; tde.rdx_vtx_y = rdx_vtx_y;",
                     "tde.rdx_vtx_z = rdx_vtx_z; tde.rdx_kep = rdx_kep;",
                     "miss_rdx_enu = tde.rdx_enu; miss_rdx_vtx_x = tde.rdx_vtx_x;",
                     "miss_rdx_vtx_y = tde.rdx_vtx_y; miss_rdx_vtx_z = tde.rdx_vtx_z;", "miss_rdx_kep = tde.rdx_kep;",
                     "miss_rdx_run = tde.id_run; miss_rdx_subrun = tde.id_subrun;", "miss_rdx_evt = tde.id_nth;",
                     "if(pdg[i] == 2212 && E[i] - 938.272 > best) best = E[i] - 938.272;",
                     "rdx_run = key_run; rdx_subrun = key_subrun; rdx_evt = key_nth;"):
            self.assertEqual(new.count(stmt), 1, stmt)
        fill = new[new.index("      if(dumpTruthx){"):new.index("rdx_enu = recoCV->GetEnuTrue();")]
        self.assertIn("CVUniverse::SetTruth(true);", fill)
        names = new[new.index("const std::set<std::string> explicitNames"):]
        names = names[:names.index("};")]
        for b in RC.C1_BRANCHES:
            self.assertIn(f'"{b}"', names)
        refuse = new[new.index('if(getenv("MNV101_DUMP_TRUTHX") != nullptr && getenv("MNV101_DUMP_POINTCLOUD")'):]
        self.assertIn("return badCmdLine;", refuse[:refuse.index("}")])

    def test_the_patch_removes_only_the_explicit_names_line(self):
        removed = [ln for ln in PATCH.read_text().splitlines() if ln.startswith("-") and not ln.startswith("---")]
        self.assertEqual(removed, ['-        "mc_run", "mc_subrun", "mc_nthEvtInFile"};'])


if __name__ == "__main__":
    unittest.main()
