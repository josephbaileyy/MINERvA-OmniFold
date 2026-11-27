"""Tests of PTMC's launch helpers: ptmc_pilot_post.py (section 7's rules) and ptmc_stage_d4.py (the D4 staging). The
first needs numpy only; the second needs the deploy tree (test_ptmc.tree) and so PyROOT.

  PTMC_PY=/path/python OMP_NUM_THREADS=1 python -B -m pytest -q -p no:cacheprovider test_launch.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import ptmc_pilot_post as PP  # noqa: E402

PILOT = PP.PILOT


def sacct(job_el=900, nodes=2, steps=None, job_state="COMPLETED", step_state="COMPLETED"):
    steps = steps or {u: 800 for u in PILOT}
    lines = [f"1|ptmc_pilot|{job_state}|0:0|{job_el}|{nodes}|s|e", "1.batch|batch|COMPLETED|0:0|900|1|s|e"]
    lines += [f"1.{i}|{u}|{step_state}|0:0|{el}|1|s|e" for i, (u, el) in enumerate(steps.items())]
    return "\n".join(lines) + "\n"


def units_dir(ok=True, coupled=True):
    d = Path(tempfile.mkdtemp())
    for u in PILOT:
        ctl = {"C-PAIR": {"pass": ok}}
        if u.endswith("_c"):
            ctl["C-COUPLE"] = {"pass": coupled}
        np.savez(d / f"{u}.npz", meta=json.dumps({"controls": ctl}))
        (d / f"{u}.done").write_text(json.dumps({"unit": u, "verdict": "PASS" if ok else "FAIL"}))
    return d


def run(text, units):
    out = Path(tempfile.mkdtemp())
    s = out / "sacct.txt"
    s.write_text(text)
    rc = PP.main(["--sacct", str(s), "--units", str(units), "--out", str(out)])
    return rc, json.loads((out / "decision.json").read_text()), out


class PilotPost(unittest.TestCase):
    def test_scoped_timing_proceeds_with_the_capped_limit(self):
        """At the scoped t_R = 704 s with a 0.42 node-h pilot (756 s on 2 nodes), the projection is about 10.2 node-h
        and L = min(1.5 x 7040 + o, (12.5 - pilot) / 5) is the cap's, about 2 h 25 min (the director's arithmetic)."""
        steps = {u: 700 for u in PILOT}
        steps["p_R_b1"] = 704
        rc, d, out = run(sacct(job_el=756, steps=steps), units_dir())
        self.assertEqual(rc, 0, d)
        self.assertEqual(d["verdict"], "PROCEED")
        self.assertAlmostEqual(d["pilot_node_h"], 0.42)
        self.assertAlmostEqual(d["o_s"], 52.0)
        self.assertAlmostEqual(d["projection_node_h"], 0.42 + 5 * (7040 + 52) / 3600)
        self.assertEqual(d["time_limit_minutes"], int((12.5 - 0.42) / 5 * 60))  # 144: the cap binds, not 1.5x
        self.assertEqual((out / "time_limit_minutes").read_text().strip(), "144")
        self.assertTrue((out / "PROCEED").exists())

    def test_projection_over_11_5_stops(self):
        steps = {u: 900 for u in PILOT}
        steps["p_R_b1"] = 900  # 5 x 10 x 900 s = 12.5 node-h
        rc, d, out = run(sacct(job_el=950, steps=steps), units_dir())
        self.assertEqual(rc, 6)
        self.assertFalse(d["rules"]["projection_within_11.5"])
        self.assertFalse((out / "PROCEED").exists())

    def test_projection_rule_flag(self):
        """A projection of about 12.0 node-h breaks the 11.5 rule itself (the floor also STOPs, being implied)."""
        steps = {u: 830 for u in PILOT}
        rc, d, _ = run(sacct(job_el=840, steps=steps), units_dir())
        self.assertEqual(rc, 6)
        self.assertGreater(d["projection_node_h"], 11.5)
        self.assertLess(d["projection_node_h"], 12.6)
        self.assertFalse(d["rules"]["projection_within_11.5"])

    def test_central_without_its_coupling_record_stops(self):
        d = units_dir()
        for u in ("p_off_c", "p_R_c"):
            np.savez(d / f"{u}.npz", meta=json.dumps({"controls": {"C-PAIR": {"pass": True}}}))
        rc, dec, out = run(sacct(), d)
        self.assertEqual(rc, 6)
        self.assertFalse((out / "PROCEED").exists())

    def test_limit_below_the_floor_stops(self):
        steps = {u: 792 for u in PILOT}
        # o = 8 s, pilot 0.444 node-h, runtime 7928 s: projection 11.455 <= 11.5, but L = 144 min < 1.1 x 132.1 min
        rc, d, out = run(sacct(job_el=800, steps=steps), units_dir())
        self.assertEqual(rc, 6)
        self.assertTrue(d["rules"]["projection_within_11.5"])
        self.assertFalse(d["rules"]["limit_covers_1.1x_runtime"])

    def test_failed_unit_step_or_coupling_stops(self):
        for units, text in ((units_dir(ok=False), sacct()), (units_dir(coupled=False), sacct()),
                            (units_dir(), sacct(step_state="FAILED")), (units_dir(), sacct(job_state="TIMEOUT"))):
            rc, d, out = run(text, units)
            self.assertEqual(rc, 6, d)
            self.assertFalse((out / "PROCEED").exists())
        missing = {u: 800 for u in PILOT[:-1]}
        rc, d, _ = run(sacct(steps=missing), units_dir())
        self.assertEqual(rc, 6)

    def test_garbled_sacct_and_rerun_refuse(self):
        rc, d, out = run("nonsense\n", units_dir())
        self.assertEqual(rc, 6)
        self.assertEqual(d["verdict"], "STOP")
        self.assertEqual(PP.main(["--sacct", str(out / "sacct.txt"), "--units", "x", "--out", str(out)]), 2)


try:
    import ROOT  # noqa: F401
    HAVE_ROOT = True
except Exception:  # pragma: no cover
    HAVE_ROOT = False


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT (the deploy tree's ref_c2c1)")
class StageD4(unittest.TestCase):
    def setUp(self):
        import test_ptmc as T
        import ptmc_stage_d4 as SD
        self.T, self.SD = T, SD
        self.ref = Path(tempfile.mkdtemp())
        (self.ref / "units").mkdir()
        (self.ref / "read-2" / "inputs").mkdir(parents=True)
        for src, name in SD.products(self.ref):
            src.write_bytes(name.encode())

    def stage(self):
        out = Path(tempfile.mkdtemp()) / "d4"
        with mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True):
            rc = self.SD.main(["--tree", str(self.T.tree()), "--out", str(out)], ref=self.ref)
        return rc, out

    def test_complete(self):
        rc, out = self.stage()
        self.assertEqual(rc, 0)
        m = json.loads((out / "manifest.json").read_text())
        self.assertEqual(len(m["copied"]), 1 + 200 + 1 + 201)
        self.assertEqual(m["absent"], [])
        self.assertEqual((out / "002_xsec.root").read_bytes(), b"002_xsec.root")

    def test_absent_is_recorded_and_a_symlink_fails(self):
        (self.ref / "units" / "c2_replica_b7.npz").unlink()
        rc, out = self.stage()
        self.assertEqual(rc, 0)
        m = json.loads((out / "manifest.json").read_text())
        self.assertEqual(m["absent"], [str(self.ref / "units" / "c2_replica_b7.npz")])
        self.assertFalse((out / "c2_replica_b7.npz").exists())
        (self.ref / "units" / "c2_replica_b8.npz").unlink()
        (self.ref / "units" / "c2_replica_b8.npz").symlink_to(self.ref / "units" / "c2_replica_b9.npz")
        rc, out = self.stage()
        self.assertEqual(rc, 5)
        self.assertFalse((out / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
