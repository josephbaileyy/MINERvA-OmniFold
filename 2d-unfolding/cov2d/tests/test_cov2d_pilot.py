"""cov2d_pilot: part B's wall per run from its committed ledger, the REPRICE rule, and the readout end to end on
synthetic outputs (PyROOT): a PASS, a (2b) failure that is (c)'s second STOP, a missing part B product (INVALID).
    cd 2d-unfolding/cov2d/tests && python -B -m unittest -v test_cov2d_pilot
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import cov2d_pilot as cp  # noqa: E402

try:
    import ROOT
    ROOT.gROOT.SetBatch(True)
    ROOT.TH1.AddDirectory(False)
    HAVE = True
except Exception:  # pragma: no cover
    HAVE = False


class Walls(unittest.TestCase):
    def test_partb_wall_per_run_from_the_committed_ledger(self):
        led = (cp.RE2RUN / "partb_readout" / "ledger.tsv").read_text()
        jobs = (cp.RE2RUN / "partb_jobs.tsv").read_text()
        b = cp.partb_wall_per_run(led, jobs)
        el = {r[1].replace("re2b-", ""): int(r[6]) for r in (ln.split("\t") for ln in led.splitlines()[1:])}
        pf = 300                                                        # every part B job declared preflight_s = 300
        self.assertAlmostEqual(b["central"], (el["J1"] - pf) * 3 / 3)   # J1: 4 lanes, 3 runs; run time only
        self.assertAlmostEqual(b["lateral"], (el["J3"] - pf) * 2 / 10)  # J3: 2 lanes, 10 runs
        self.assertAlmostEqual(b["replica"], sum((el[j] - pf) * 4 / 100 for j in ("J4a", "J4b", "J4c")) / 3)
        self.assertAlmostEqual(b["universe"], sum((el[j] - pf) * 2 / r for j, r in
                                                  (("J2a", 44), ("J2b", 44), ("J2c", 44), ("J2d", 43))) / 4)
        self.assertEqual(b["toy"], b["central"])

    def test_the_64_cpu_universe_is_not_a_measurement(self):
        base = {"central": 900.0, "toy": 900.0, "lateral": 1700.0, "replica": 900.0, "universe": 1000.0}
        r = cp.reprice("U_G18_Flux_0\t0\t9999\t0\nP912_U_MaRES_0\t0\t1100\t0\n", base)
        self.assertEqual(r["universe"]["pilot_s"], 1100)

    def test_reprice(self):
        base = {"central": 900.0, "toy": 900.0, "lateral": 1700.0, "replica": 900.0, "universe": 1000.0}
        walls = "X_G18\t0\t1100\t0\nT_G18_5720000\t0\t1200\t0\nL_G18_a\t0\t1600\t0\nB_G18_001\t0\t5000\t1\n"
        r = cp.reprice(walls, base)
        self.assertFalse(r["central"]["reprice"])                 # 1100 <= 1125
        self.assertTrue(r["toy"]["reprice"])                      # 1200 > 1125
        self.assertNotIn("replica", r)                            # a failed run is not a wall

    def test_classes(self):
        for lab, k in (("P912_L_BeamAngleX_0", "lateral"), ("P912_U_MaRES_0", "universe"), ("P2b_ER", "central"),
                       ("U_G18_Flux_0", "universe"), ("T_G18_5720000", "toy")):
            self.assertEqual(cp.class_of(lab), k)


@unittest.skipUnless(HAVE, "needs PyROOT")
class Readout(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True)
        p.start()
        self.addCleanup(p.stop)
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.d = Path(self.td.name)
        r = np.random.default_rng(1)
        x = r.uniform(1, 2, (14, 16))
        x.ravel()[r.choice(224, 19, replace=False)] = 0.0
        self.x = x

    def th2(self, path: Path, a: np.ndarray):
        path.parent.mkdir(parents=True, exist_ok=True)
        f = ROOT.TFile.Open(str(path), "RECREATE")
        h = ROOT.TH2D("hXSec2D", "", 14, 0, 14, 16, 0, 16)
        for i in range(14):
            for j in range(16):
                h.SetBinContent(i + 1, j + 1, float(a[i, j]))
        h.Write("hXSec2D")
        f.Close()

    def build(self, mine_off=0.0, drop_partb=None, drop_run=None):
        ns = self.d / "partb"
        sums = {}
        for lab in ("ER", "U_MaRES_0", "S3_BeamAngleX0"):
            if lab == drop_partb:
                continue
            self.th2(ns / "out" / lab / "xsec.root", self.x)
            sums[f"{lab}/xsec.root"] = hashlib.sha256((ns / "out" / lab / "xsec.root").read_bytes()).hexdigest()
        O = self.d / "run"
        lines, walls = [], []
        for lab in cp.PILOT_LABELS:
            self.th2(O / "out" / lab / "xsec.root", self.x * (1 + (mine_off if lab == "P2b_ER" else 0.0)))
            if lab != drop_run:
                lines.append(f"{hashlib.sha256((O / 'out' / lab / 'xsec.root').read_bytes()).hexdigest()}  {lab}/xsec.root")
            w = 9000 if lab == "L_G18_BeamAngleX_0" else 500
            walls.append(f"{lab}\t0\t{w}\t{1 if lab == drop_run else 0}")
        (O / "SHA256SUMS.pilot.1").write_text("\n".join(lines) + "\n")
        (O / "walls.pilot.1.tsv").write_text("\n".join(walls) + "\n")
        (O / "logs").mkdir()
        (O / "logs" / "dvs-rate-1.json").write_text(json.dumps({"cfs": {"MB_per_s": 9.5}}))
        import cov2d_pseudo_write as pw
        import re2c_rollup as ro
        er_sha = sums.get("ER/xsec.root", "0" * 64)
        for patch in (mock.patch.object(ro, "partb_sums", lambda: sums), mock.patch.object(ro, "NS_R", str(ns)),
                      mock.patch.dict(pw.PINS, {"er": (str(ns / "out/ER/xsec.root"), er_sha)})):
            patch.start()
            self.addCleanup(patch.stop)
        return O

    def run_readout(self, O):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = cp.main(["--o", str(O), "--out", str(self.d / "pilot.json")])
        return code, json.loads((self.d / "pilot.json").read_text())

    def test_pass(self):
        code, rec = self.run_readout(self.build())
        self.assertEqual((code, rec["verdict"]), (0, "PASS"))
        self.assertTrue(all(v["pass"] and v["bitwise_224"] for v in rec["controls"].values()))
        self.assertEqual(rec["reprice_classes"], ["lateral"])    # 9000 s against part B's J3 wall per run
        self.assertEqual(rec["dvs_rate"]["cfs"]["MB_per_s"], 9.5)

    def test_2b_failure_is_the_second_stop(self):
        code, rec = self.run_readout(self.build(mine_off=1e-7))
        self.assertEqual((code, rec["verdict"]), (3, "STOP"))
        self.assertFalse(rec["controls"]["2b"]["pass"])
        self.assertIn("second STOP", rec["consequence"])

    def test_within_1e_8_passes(self):
        code, rec = self.run_readout(self.build(mine_off=5e-9))
        self.assertEqual(rec["verdict"], "PASS")
        self.assertFalse(rec["controls"]["2b"]["bitwise_224"])

    def test_a_failed_run_of_any_class_is_invalid(self):
        for lab in ("X_G18", "T_G18_5720000", "B_G18_001", "U_G18_Flux_0", "L_G18_BeamAngleX_0"):
            with self.subTest(lab):
                self.tearDown_patches()
                code, rec = self.run_readout(self.build(drop_run=lab))
                self.assertEqual(rec["verdict"], "INVALID")
                self.assertTrue(any(lab in x for x in rec["invalid"]))

    def tearDown_patches(self):
        import shutil
        for p in (self.d / "partb", self.d / "run"):
            shutil.rmtree(p, ignore_errors=True)

    def test_missing_partb_product_is_invalid(self):
        code, rec = self.run_readout(self.build(drop_partb="U_MaRES_0"))
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertTrue(any("U_MaRES_0" in x for x in rec["invalid"]))


if __name__ == "__main__":
    unittest.main()
