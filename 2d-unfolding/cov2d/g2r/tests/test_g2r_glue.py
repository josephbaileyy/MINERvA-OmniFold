"""COV2D-G2R's glue, run locally (the director's sweep after B1: no path may be reachable only on the cluster without
a test that has run it).

    python3 -B 2d-unfolding/cov2d/g2r/tests/test_g2r_glue.py

* ``Prepare``: g2r_prepare.main end to end on placeholder files, with uproot replaced by a stand-in that serves numpy
  columns (uproot is not installed here; the real parse is the cluster-environment test's). It covers the block sizes,
  the merged count, G5, the map, G11's four universes, the 175 per-universe checks, the identity count, the map npz,
  the record, the atime ledger, and the refusals (a missing per-playlist file is the director's STOP, rc 7; a wrong
  size is INVALID, rc 5; no overwrite).
* ``PhaseTune``: g2r_readout.phase_tune end to end on the REAL committed AR23 inputs (blocks_AR23.npz, null_AR23.json,
  score_AR23.json, E_AR23.npz and C2's record, each read at its digest), with 175 small ROOT products whose
  provenance names the map and the realization and whose cell vectors are blocks_AR23.npz's own universe rows (so
  C_T' = C_T). Only Run's MAT-environment check, deploy_head and E_R's cells (pscratch) are stood in. It shows on real
  data: G7 reproduces the committed grade; G6 reproduces the committed blocks to 1e-12 (here, under numpy 2.4, not
  bitwise: about 6e-21 of the largest element in C_univ, the BLAS's rounding); the null rebuilt at C_T' equals
  the committed null_AR23.json (the auditor's n4); the regrade reproduces the committed verdict, counts and ndf; and
  the tune eps is 0.
"""
from __future__ import annotations

import contextlib
import hashlib
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
G2R = HERE.parent
COV2D = G2R.parent
REPO = COV2D.parents[1]
sys.path[:0] = [str(G2R), str(HERE), str(COV2D), str(COV2D / "tests"), str(REPO / "nd-unfolding"),
                str(REPO / "2d-unfolding" / "re2" / "partc")]
import g2r  # noqa: E402
import test_g2r as tg  # noqa: E402


# ------------------------------------------------------------------------------------------------ a stand-in uproot
class FakeTree:
    """Serves named numpy columns. A universe column not given explicitly is the identity universe: on the signal
    tree w_truth_<u> = w_truth and w_reco_<u> = w_reco (the misses then carry the proxy), on the truth tree
    w_truth_<u> = w_truth."""
    def __init__(self, cols: dict, explicit: dict):
        self.cols, self.explicit = cols, explicit
        self.num_entries = len(next(iter(cols.values())))

    def col(self, k):
        if k in self.cols:
            return self.cols[k]
        if k in self.explicit:
            return self.explicit[k]
        if k.startswith("w_truth_"):
            return self.cols["w_truth"]
        if k.startswith("w_reco_"):
            return self.cols["w_reco"]
        raise KeyError(k)

    def arrays(self, cols, library="np"):
        assert library == "np"
        return {k: np.asarray(self.col(k)) for k in cols}


class FakeParam:
    def __init__(self, v):
        self.v = v

    def member(self, name):
        assert name == "fVal"
        return self.v


class FakeFile:
    def __init__(self, items: dict):
        self.items = items

    def __getitem__(self, k):
        return self.items[k]

    def get(self, k):
        return self.items.get(k)


def fake_uproot(registry: dict):
    m = types.ModuleType("uproot")
    m.open = lambda fh: registry[os.path.realpath(getattr(fh, "name", fh))]
    return m


@contextlib.contextmanager
def plain_open_noatime(rc):
    """macOS has no O_NOATIME: open plainly and put the atime back, as tests/noatime_emu.py does for COV2D."""
    def opener(path):
        t = os.stat(path).st_atime_ns
        fh = open(path, "rb")
        real_close = fh.close

        def close():
            real_close()
            os.utime(path, ns=(t, os.stat(path).st_mtime_ns))
        fh.close = close
        return fh
    with mock.patch.object(rc, "open_noatime", opener):
        yield


class Prepare(unittest.TestCase):
    def setUp(self):
        import cov2d_receipt as rc
        import g2r_prepare as gp
        self.gp, self.rc = gp, rc
        self.td = tempfile.TemporaryDirectory()
        d = Path(self.td.name)
        blocks = ((40, 12), (30, 9), (20, 0))
        self.S, self.T, self.blk, self.U = tg.synthetic(blocks=blocks, seed=5)
        self.uni = d / "uni.root"
        self.uni.write_bytes(b"x" * 1234)
        self.blocks = []
        reg = {}
        explicit_s = {"w_truth_MaRES_0": self.U["varied"][0], "w_reco_MaRES_0": self.U["varied"][1],
                      "w_truth_VecFFCCQEshape_1": self.U["last"][0], "w_reco_VecFFCCQEshape_1": self.U["last"][1]}
        explicit_t = {"w_truth_MaRES_0": self.U["varied"][2], "w_truth_VecFFCCQEshape_1": self.U["last"][2]}
        o = 0
        for k, (name, n, m) in enumerate(self.blk):
            p = d / f"{name}.root"
            p.write_bytes(b"b")
            sl = slice(o, o + n)
            reg[str(p.resolve())] = FakeFile({
                "mc_signal_reco": FakeTree({kk: v[sl] for kk, v in self.S.items()}, {}),
                "mc_truth_denom": FakeTree({kk: v[sl] for kk, v in self.T.items()}, {}),
                "nTruthOnlyMisses": FakeParam(m)})
            self.blocks.append(str(p))
            o += n
        reg[str(self.uni.resolve())] = FakeFile({
            "mc_signal_reco": FakeTree(dict(self.S), explicit_s), "mc_truth_denom": FakeTree(dict(self.T), explicit_t),
            "nTruthOnlyMisses": FakeParam(sum(m for _, _, m in self.blk))})
        self.patches = contextlib.ExitStack()
        self.patches.enter_context(mock.patch.dict(sys.modules, {"uproot": fake_uproot(reg)}))
        self.patches.enter_context(mock.patch.object(gp, "UNI_SIZE", 1234))
        self.patches.enter_context(plain_open_noatime(rc))
        self.out = d / "out"

    def tearDown(self):
        self.patches.close()
        self.td.cleanup()

    def main(self, *extra_blocks):
        import io
        from contextlib import redirect_stdout
        with redirect_stdout(io.StringIO()):
            return self.gp.main(["--omnifile", str(self.uni), "--blocks", *self.blocks, *extra_blocks,
                                 "--out", str(self.out)])

    def test_the_prepare_end_to_end(self):
        self.assertEqual(self.main(), 0)
        rec = json.loads((self.out / "g2r_prepare.json").read_text())
        self.assertEqual(rec["verdict"], "PASS")
        self.assertTrue(rec["G5"]["pass"])
        self.assertEqual(sorted(rec["G11"]), ["Flux:0", "Flux:87", "MaRES:0", "VecFFCCQEshape:1"])
        self.assertTrue(all(v["equal"] for v in rec["G11"].values()))
        self.assertEqual(len(rec["universes"]), 175)
        self.assertFalse(rec["universes"]["MaRES:0"]["identity"])
        self.assertFalse(rec["universes"]["VecFFCCQEshape:1"]["identity"])
        self.assertEqual(rec["identity_universes"]["count"], 173)
        self.assertEqual(rec["atime"]["moved"], [])
        z = np.load(self.out / "g2r_map.npz")
        miss, truth, _ = g2r.build_map(self.S, self.T, self.blk)
        np.testing.assert_array_equal(z["miss_rows"], miss)
        np.testing.assert_array_equal(z["truth_rows"], truth)
        self.assertEqual(str(z["omnifile"]), os.path.realpath(self.uni))
        self.assertEqual(rec["map_npz_sha256"], hashlib.sha256((self.out / "g2r_map.npz").read_bytes()).hexdigest())
        with self.assertRaises(SystemExit):
            self.main()                                        # no overwrite

    def test_a_missing_per_playlist_file_is_the_directors_stop(self):
        self.assertEqual(self.main(str(Path(self.td.name) / "gone.root")), self.gp.RC_STOP_BLOCKS)
        rec = json.loads((self.out / "g2r_prepare.json").read_text())
        self.assertEqual(rec["verdict"], "STOP")

    def test_the_real_block_sizes_refuse_unequal_trees(self):
        import cov2d_receipt as rc
        p = Path(self.td.name) / "odd.root"
        p.write_bytes(b"o")
        reg = {str(p.resolve()): FakeFile({"mc_signal_reco": FakeTree({"MC": np.zeros(3)}, {}),
                                           "mc_truth_denom": FakeTree({"MC": np.zeros(4)}, {}),
                                           "nTruthOnlyMisses": FakeParam(1)})}
        with mock.patch.dict(sys.modules, {"uproot": fake_uproot(reg)}), \
                self.assertRaisesRegex(g2r.Refusal, "mc_signal_reco 3 != mc_truth_denom 4"):
            self.gp.block_sizes([str(p)])

    def test_a_wrong_merged_count_is_invalid(self):
        uni = sys.modules["uproot"].open(str(self.uni))
        uni.items["nTruthOnlyMisses"] = FakeParam(10 ** 6)
        self.assertEqual(self.main(), self.gp.RC_INVALID)
        self.assertIn("merged nTruthOnlyMisses", json.loads((self.out / "g2r_prepare.json").read_text())["why"])

    def test_a_wrong_size_is_invalid(self):
        with mock.patch.object(self.gp, "UNI_SIZE", 999):
            self.assertEqual(self.main(), self.gp.RC_INVALID)
        self.assertIn("G5", json.loads((self.out / "g2r_prepare.json").read_text())["why"])


# ---------------------------------------------------------------------------------------------- phase_tune, AR23
def write_product(path: Path, prov: dict):
    import ROOT
    f = ROOT.TFile.Open(str(path), "RECREATE")
    for k, v in prov.items():
        ROOT.TNamed(k, v).Write()
    f.Close()


class FakeCells:
    def __init__(self, rep, rows: dict):
        self.rep, self.rows = rep, rows

    def vec(self, path):
        return self.rows[Path(path).stem]


class PhaseTune(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import cov2d as c
        import cov2d_blocks as cb
        import cov2d_readout as crd
        import g2r_readout as gr
        cls.c, cls.crd, cls.gr = c, crd, gr
        T = "AR23"
        cls.td = tempfile.TemporaryDirectory()
        d = Path(cls.td.name)
        B = dict(np.load(gr.COMMITTED[T]["blocks"][0], allow_pickle=False))
        real = crd.data_shas(T)[c.REALIZATION_SEED[T]]
        map_sha = "m" * 64
        rows, lines = {}, []
        for b in c.ORDER:
            for i in range(c.BANDS[b]):
                lab = f"G_{T}_{b}_{i}"
                p = d / "prod" / f"{lab}.src.root"
                p.parent.mkdir(exist_ok=True)
                write_product(p, {"g2rMissMap": json.dumps({"sha256": map_sha, "universe": f"{b}:{i}"}),
                                  "dataFileSha256": real})
                rows[lab] = np.asarray(B[f"band__{b}"], np.float64)[i]
                lines.append("\t".join([lab, str(p), hashlib.sha256(p.read_bytes()).hexdigest(), "g2r", f"{b}:{i}"]))
        tsv = d / "products.tsv"
        tsv.write_text("\n".join(lines) + "\n")
        out = d / "out"
        out.mkdir()
        cells = FakeCells(B["rep"].astype(bool), rows)
        with contextlib.ExitStack() as st:
            st.enter_context(mock.patch.object(os, "O_NOATIME", 0, create=True))
            st.enter_context(mock.patch.object(cb, "pinned_mat_environment", lambda: {"stood_in": True}))
            st.enter_context(mock.patch.object(c, "deploy_head", lambda root: "TEST"))
            st.enter_context(mock.patch.object(crd.Run, "er_cells", lambda self: cells))
            cls.rec = gr.phase_tune(T, tsv, map_sha, out)
        cls.out, cls.B, cls.T = out, B, T
        cls.committed_null = json.loads(Path(gr.COMMITTED[T]["null"][0]).read_text())
        cls.committed_score = json.loads(Path(gr.COMMITTED[T]["score"][0]).read_text())

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_g7_and_g6_pass_on_the_committed_inputs(self):
        self.assertTrue(self.rec["G7"]["pass"], self.rec["G7"])
        self.assertTrue(self.rec["G6"]["pass"], self.rec["G6"])
        self.assertEqual(self.rec["controls_failed"], [])

    def test_the_null_rebuilt_at_c_t_prime_equals_the_committed_null(self):
        new = json.loads((self.out / f"null_g2r_{self.T}.json").read_text())
        for k in ("p_cell", "se_cell", "q_joint", "se_joint", "chi2_cut", "ndf"):
            self.assertEqual(new["null"][k], self.committed_null["null"][k], k)

    def test_the_regrade_reproduces_the_committed_reading(self):
        g, g0 = self.rec["grade"], self.committed_score["grade"]
        for k in ("verdict", "ndf", "counts", "joint_count", "k_joint", "flagged_cells"):
            self.assertEqual(g[k], g0[k], k)
        self.assertEqual(self.rec["verdict"], "UNDER-COVERS")
        self.assertLess(self.rec["tune_eps"]["eps"]["retained"]["eps"], 1e-10)   # rounding only (G6's record)
        self.assertEqual(self.rec["stop"], [])

    def test_the_blocks_npz_is_written_in_phase_ns_layout(self):
        z = np.load(self.out / f"blocks_g2r_{self.T}.npz")
        np.testing.assert_allclose(z["C_T"], self.B["C_T"], rtol=0, atol=1e-12 * np.abs(self.B["C_T"]).max())
        self.assertEqual(sorted(z.files), sorted(self.B.keys()))



class PhaseTuneTampered(unittest.TestCase):
    """G6 enforced: blocks_AR23.npz with C_univ moved by 1e-9 (C_T untouched, so G7 still passes) makes phase_tune
    write score_g2r_AR23.invalid.json with "G6 failed", before any corrected product is read or any null written."""

    def test_a_failing_g6_is_invalid_before_the_products(self):
        import cov2d as c
        import cov2d_blocks as cb
        import cov2d_readout as crd
        import g2r_readout as gr
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            B = dict(np.load(gr.COMMITTED["AR23"]["blocks"][0], allow_pickle=False))
            B["C_univ"] = B["C_univ"] * (1 + 1e-9)
            np.savez(d / "blocks.npz", **B)
            pins = dict(gr.COMMITTED["AR23"])
            pins["blocks"] = (d / "blocks.npz", hashlib.sha256((d / "blocks.npz").read_bytes()).hexdigest())
            out = d / "out"
            out.mkdir()
            tsv = d / "never_read.tsv"            # absent: reading it would raise
            with contextlib.ExitStack() as st:
                st.enter_context(mock.patch.object(os, "O_NOATIME", 0, create=True))
                st.enter_context(mock.patch.object(cb, "pinned_mat_environment", lambda: {"stood_in": True}))
                st.enter_context(mock.patch.object(c, "deploy_head", lambda root: "TEST"))
                st.enter_context(mock.patch.dict(gr.COMMITTED, {"AR23": pins}))
                rec = gr.phase_tune("AR23", tsv, "m" * 64, out)
            self.assertTrue(rec["G7"]["pass"])
            self.assertFalse(rec["G6"]["pass"])
            self.assertIn("G6 failed", rec["controls_failed"])
            self.assertEqual(rec["verdict"], "INVALID")
            self.assertTrue((out / "score_g2r_AR23.invalid.json").exists())
            self.assertFalse((out / "null_g2r_AR23.json").exists())


def phase_data_run(td, x_mismatch=False, budget_off=False, budget_digest_off=False):
    """phase_data on synthetic stand-ins (see PhaseData); the knobs plant one failure each."""
    import gzip
    import cov2d as c
    import cov2d_blocks as cb
    import cov2d_readout as crd
    import g2r_readout as gr
    import re2c_build_q as bq
    d = Path(td)
    ro = cb.rollup()
    rng = np.random.default_rng(77)
    n = 205
    x = rng.uniform(1, 2, n)
    w = rng.uniform(0.5, 1.5, 100)
    old = {b: x * (1 + 0.02 * rng.normal(size=(c.BANDS[b], n))) for b in c.ORDER}
    new = {b: (old[b] - x) * 1.2 + x for b in c.ORDER}
    s5 = {f"band_{b}": ro.band_cov(old[b], w if b == c.FLUX else None) for b in c.ORDER}
    F = np.vstack([np.ones(n), rng.uniform(0, 1, (30, n))])
    s5["functionals"] = F
    Q = sum(s5[f"band_{b}"] for b in sorted(c.ORDER)) + np.diag((0.01 * x) ** 2)
    np.savez(d / "s5.npz", **s5)
    np.savez(d / "q205.npz", Q=Q, x=x)
    m = bq.metrics(Q, x, F)
    if budget_off:
        m = dict(m, median_pct=m["median_pct"] * 1.01)
    budget = json.dumps({"Q": {"median_pct": m["median_pct"], "integral_sigma_pct": m["integral_sigma_pct"]}}).encode()
    outa = d / "outA"
    outa.mkdir()
    (outa / "budget_Q.json.gz").write_bytes(gzip.compress(budget))
    rows, lines = {}, []
    map_sha = "m" * 64
    prod = d / "prod"
    prod.mkdir()
    for b in c.ORDER:
        for i in range(c.BANDS[b]):
            rows[f"U_{b}_{i}"] = old[b][i]
            lab = f"G_U_{b}_{i}"
            p = prod / f"{lab}.src.root"
            write_product(p, {"g2rMissMap": json.dumps({"sha256": map_sha, "universe": f"{b}:{i}"})})
            rows[lab] = new[b][i]
            lines.append("\t".join([lab, str(p), hashlib.sha256(p.read_bytes()).hexdigest(), "g2r", f"{b}:{i}"]))
    for b, i in (("Flux", 3), ("MaRES", 1)):                 # the two override-off reruns, bitwise equal here
        lab = f"O_U_{b}_{i}"
        p = prod / f"{lab}.src.root"
        write_product(p, {"dataFileSha256": "unused"})
        rows[lab] = old[b][i]
        lines.append("\t".join([lab, str(p), hashlib.sha256(p.read_bytes()).hexdigest(), "off", f"{b}:{i}"]))
    tsv = d / "products.tsv"
    tsv.write_text("\n".join(lines) + "\n")
    
    class Cells:
        def __init__(self):
            self.x, self.rep = (x * 1.001 if x_mismatch else x), np.ones(n, bool)
    
        def vec(self, path):
            return rows[Path(path).stem]
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    out = d / "out"
    out.mkdir()
    with contextlib.ExitStack() as st:
        st.enter_context(mock.patch.object(os, "O_NOATIME", 0, create=True))
        st.enter_context(mock.patch.object(cb, "pinned_mat_environment", lambda: {"stood_in": True}))
        st.enter_context(mock.patch.object(c, "deploy_head", lambda root: "TEST"))
        st.enter_context(mock.patch.object(cb, "noatime_inputs", lambda *a, **k: {"stood_in": True}))
        st.enter_context(mock.patch.object(ro, "flux_weights", lambda: (w, None)))
        st.enter_context(mock.patch.object(ro, "partb_sums", lambda: {f"U_{b}_{i}/xsec.root": "d"
                                                                      for b in c.ORDER for i in range(c.BANDS[b])}))
        st.enter_context(mock.patch.object(cb, "rollup", lambda: ro))
        st.enter_context(mock.patch.object(crd.Run, "er_cells", lambda self: Cells()))
        st.enter_context(mock.patch.object(crd.Run, "copy", lambda self, src, want, name: Path(name)))
        st.enter_context(mock.patch.object(crd.Run, "watch", lambda self, path: None))
        st.enter_context(mock.patch.object(gr, "S5_NPZ", (str(d / "s5.npz"), sha(d / "s5.npz"))))
        st.enter_context(mock.patch.object(gr, "Q205_NPZ", (str(d / "q205.npz"), sha(d / "q205.npz"))))
        st.enter_context(mock.patch.object(gr, "OUTA", outa))
        st.enter_context(mock.patch.object(gr, "BUDGET_Q", "0" * 64 if budget_digest_off else hashlib.sha256(budget).hexdigest()))
        rec = gr.phase_data(tsv, map_sha, out)
    return rec, {"Q": Q, "new": new, "old": old, "s5": s5, "w": w, "ro": ro, "c": c, "out": out}


class PhaseData(unittest.TestCase):
    """g2r_readout.phase_data end to end on synthetic stand-ins for its pscratch inputs (S5_R, Q_R on the 205 cells,
    part B's 175 universe products, the flux weights) and a budget record made from them, each read at its own
    digest through the real read_pinned. It covers G10, G6 at the data, the corrected products, the readings, the
    noise floor and the record. The real values are the cluster's."""

    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.rec, k = phase_data_run(cls.td.name)
        cls.Q, cls.new, cls.old, cls.s5, cls.w, cls.ro, cls.c, cls.out = (k[n] for n in ("Q", "new", "old", "s5", "w",
                                                                                             "ro", "c", "out"))

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_the_controls_pass_and_the_record_is_written(self):
        self.assertEqual(self.rec["controls_failed"], [], self.rec)
        self.assertTrue(self.rec["G10"]["pass"])
        self.assertTrue(self.rec["G6"]["pass"])
        self.assertEqual(self.rec["verdict"], "PASS")
        self.assertTrue((self.out / "data_g2r.json").exists())

    def test_c_new_is_q_with_the_universe_block_replaced(self):
        c = self.c
        z = np.load(self.out / "data_g2r.npz")
        want = self.Q - sum(self.s5[f"band_{b}"] for b in sorted(c.ORDER)) + sum(
            self.ro.band_cov(self.new[b], self.w if b == c.FLUX else None) for b in sorted(c.ORDER))
        np.testing.assert_allclose(z["C_new"], want, rtol=0, atol=1e-12 * np.abs(want).max())
        self.assertGreater(self.rec["readings"]["eps"]["retained"]["eps"], 0)
        self.assertEqual(set(self.rec["readings"]["sigma"]), {"median_pct", "integral_sigma_pct"})

    def test_the_floor_is_zero_for_bitwise_reruns(self):
        self.assertEqual(self.rec["floor"]["bitwise_equal"], {"Flux:3": True, "MaRES:1": True})
        self.assertEqual(self.rec["floor"]["readings"]["eps"]["retained"]["eps"], 0.0)


class PhaseDataFailures(unittest.TestCase):
    """phase_data's refusals: E_R's cells not Q_R's x and a budget that does not reproduce make the record INVALID
    before any corrected product is read; a budget record off its digest refuses."""

    def test_x_mismatch_and_budget_off_are_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            rec, k = phase_data_run(td, x_mismatch=True, budget_off=True)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertIn("E_R's cells are not cov2d_Q_205.npz's x", rec["controls_failed"])
        self.assertIn("G10 failed", rec["controls_failed"])
        self.assertNotIn("readings", rec)

    def test_a_budget_off_its_digest_refuses(self):
        import cov2d as c
        with tempfile.TemporaryDirectory() as td, self.assertRaisesRegex(c.Refusal, "budget_Q.json"):
            phase_data_run(td, budget_digest_off=True)


class ReadoutCLI(unittest.TestCase):
    """g2r_readout.main's wiring: each phase gets its arguments, and the exit code is 0 for a reading, 5 for INVALID or
    STOP, 8 for an atime move."""

    def test_arguments_and_exit_codes(self):
        import g2r_readout as gr
        calls = []

        def tune(truth, tsv, sha, out):
            calls.append(("tune", truth, str(tsv), sha, out.name))
            return {"verdict": verdicts.pop(0), "controls_failed": [], "stop": [], "atime_moved": moved.pop(0)}

        def data(tsv, sha, out):
            calls.append(("data", str(tsv), sha, out.name))
            return {"verdict": verdicts.pop(0), "controls_failed": [], "stop": [], "atime_moved": moved.pop(0)}
        verdicts, moved = ["UNDER-COVERS", "INVALID", "COVERS", "PASS"], [[], [], ["/p"], []]
        with tempfile.TemporaryDirectory() as td, mock.patch.object(gr, "phase_tune", tune), \
                mock.patch.object(gr, "phase_data", data), contextlib.redirect_stdout(__import__("io").StringIO()):
            o = str(Path(td) / "o")
            self.assertEqual(gr.main(["tune", "--truth", "G18", "--products", "p.tsv", "--map-sha", "s", "--out", o]), 0)
            self.assertEqual(gr.main(["tune", "--truth", "AR23", "--products", "p.tsv", "--map-sha", "s", "--out", o]),
                             gr.RC_INVALID)
            self.assertEqual(gr.main(["tune", "--truth", "AR23", "--products", "p.tsv", "--map-sha", "s", "--out", o]),
                             gr.RC_ATIME)
            self.assertEqual(gr.main(["data", "--products", "q.tsv", "--map-sha", "t", "--out", o]), 0)
            with self.assertRaises(SystemExit):
                gr.main(["tune", "--truth", "X", "--products", "p.tsv", "--map-sha", "s", "--out", o])
        self.assertEqual(calls[0], ("tune", "G18", "p.tsv", "s", "o"))
        self.assertEqual(calls[-1], ("data", "q.tsv", "t", "o"))


class PhaseTuneRefusals(unittest.TestCase):
    """phase_tune refuses E that is not 300 x 205 in seed order, and E_R's cells that are not blocks_<T>.npz's."""

    def patches(self, st, d, pins=None, cells=None):
        import cov2d as c
        import cov2d_blocks as cb
        import cov2d_readout as crd
        import g2r_readout as gr
        st.enter_context(mock.patch.object(os, "O_NOATIME", 0, create=True))
        st.enter_context(mock.patch.object(cb, "pinned_mat_environment", lambda: {"stood_in": True}))
        st.enter_context(mock.patch.object(c, "deploy_head", lambda root: "TEST"))
        if pins is not None:
            st.enter_context(mock.patch.dict(gr.COMMITTED, {"AR23": pins}))
        if cells is not None:
            st.enter_context(mock.patch.object(crd.Run, "er_cells", lambda self: cells))
        return gr, c

    def test_a_bad_e_refuses(self):
        import g2r_readout as gr
        with tempfile.TemporaryDirectory() as td, contextlib.ExitStack() as st:
            d = Path(td)
            z = np.load(gr.COMMITTED["AR23"]["E"][0])
            np.savez(d / "E.npz", E=z["E"][:299], seeds=z["seeds"][:299])
            pins = dict(gr.COMMITTED["AR23"])
            pins["E"] = (d / "E.npz", hashlib.sha256((d / "E.npz").read_bytes()).hexdigest())
            gr, c = self.patches(st, d, pins=pins)
            with self.assertRaisesRegex(c.Refusal, "300 toys"):
                gr.phase_tune("AR23", d / "none.tsv", "m" * 64, d)

    def test_cells_that_differ_refuse(self):
        import g2r_readout as gr
        B = np.load(gr.COMMITTED["AR23"]["blocks"][0])
        rep = B["rep"].astype(bool).copy()
        rep[np.flatnonzero(rep)[0]] = False
        with tempfile.TemporaryDirectory() as td, contextlib.ExitStack() as st:
            d = Path(td)
            gr, c = self.patches(st, d, cells=FakeCells(rep, {}))
            with self.assertRaisesRegex(c.Refusal, "E_R's cells differ"):
                gr.phase_tune("AR23", d / "none.tsv", "m" * 64, d)


if __name__ == "__main__":
    unittest.main(verbosity=1)
