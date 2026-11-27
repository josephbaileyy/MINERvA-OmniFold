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
JOB = "4242"

try:
    import ROOT  # noqa: F401
    HAVE_ROOT = True
except Exception:  # pragma: no cover
    HAVE_ROOT = False


def sacct(job_el=756, nodes=2, steps=None, job_state="COMPLETED", step_state="COMPLETED", extra=()):
    """The default is the scoped timing (t_R = 704 s, a 756 s pilot), which PROCEEDs, so a negative test STOPs only on
    the defect it plants."""
    steps = steps or {**{u: 700 for u in PILOT}, "p_R_b1": 704}
    lines = [f"{JOB}|ptmc_pilot|{job_state}|0:0|{job_el}|{nodes}|s|e", f"{JOB}.batch|batch|COMPLETED|0:0|{job_el}|1|s|e",
             f"{JOB}.extern|extern|COMPLETED|0:0|{job_el}|2|s|e"]
    lines += [f"{JOB}.{i}|{u}|{step_state}|0:0|{el}|1|s|e" for i, (u, el) in enumerate(steps.items())]
    return "\n".join(lines + list(extra)) + "\n"


def products():
    import test_ptmc_score as TS
    return TS.Products(delta_scale=0.05)


def run(text, prod, recheck=None):
    out = Path(tempfile.mkdtemp())
    s = out / "sacct.txt"
    s.write_text(text)
    argv = ["--sacct", str(s), "--jobid", JOB, "--units", str(prod.units), "--rows", str(prod.rows), "--out", str(out)]
    if recheck is not None:
        argv += ["--recheck", str(recheck)]
    rc = PP.main(argv)
    dec = out / "decision.json"
    return rc, (json.loads(dec.read_text()) if dec.exists() else None), out


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT (the hand-made units)")
class PilotPost(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = products()

    def test_scoped_timing_proceeds_with_the_capped_limit(self):
        """At the scoped t_R = 704 s and a 756 s pilot on 2 nodes, L is the cap's: (45000 - 1512) // 300 = 144."""
        rc, d, out = run(sacct(), self.p)
        self.assertEqual(rc, 0, d)
        self.assertEqual(d["o_s"], 52)
        self.assertEqual(d["pilot_node_s"], 1512)
        self.assertEqual(d["time_limit_minutes"], 144)
        self.assertEqual((out / "time_limit_minutes").read_text().strip(), "144")
        self.assertTrue(all(d["cross_unit"][k] for k in ("C-NORM", "C-FIX", "C-MOVE-seed1", "C-SUPPORT-table")))

    def test_codex_float_case_proceeds(self):
        """codex r1 #5: pilot 1500 s, t_R 750 s, longest step 1364 s: the exact cap allows 140 minutes, which meets the
        floor; the float version gave 139.999... and STOPped."""
        steps = {**{u: 1364 for u in PILOT}, "p_R_b1": 750}
        rc, d, _ = run(sacct(job_el=1500, steps=steps), self.p)
        self.assertEqual(rc, 0, d)
        self.assertEqual(d["time_limit_minutes"], 140)

    def test_projection_rule_flag(self):
        rc, d, _ = run(sacct(job_el=840, steps={u: 830 for u in PILOT}), self.p)
        self.assertEqual(rc, 6)
        self.assertFalse(d["rules"]["projection_within_11.5"])
        # between 11.5 and 12.0 node-h: 1650 + 5 x 8160 = 42450 node-s (11.79 node-h) is over the 11.5 STOP
        rc, d, _ = run(sacct(job_el=825, steps={u: 815 for u in PILOT}), self.p)
        self.assertEqual(rc, 6)
        self.assertEqual(d["projection_node_s"], 42450)
        self.assertFalse(d["rules"]["projection_within_11.5"])

    def test_limit_below_the_floor_stops(self):
        rc, d, _ = run(sacct(job_el=800, steps={u: 792 for u in PILOT}), self.p)
        self.assertEqual(rc, 6)
        self.assertTrue(d["rules"]["projection_within_11.5"])
        self.assertFalse(d["rules"]["limit_covers_1.1x_runtime"])

    def test_accounting_defects_stop(self):
        bad = [sacct(step_state="FAILED"), sacct(job_state="TIMEOUT"), sacct(nodes=3),
               sacct(steps={u: 700 for u in PILOT[:-1]}),
               sacct(extra=["999.0|p_off_c|COMPLETED|0:0|700|1|s|e"]),  # a foreign job's row
               sacct(extra=["999.batch|batch|COMPLETED|0:0|700|1|s|e"]),  # a foreign job's housekeeping row
               sacct().replace(f"{JOB}.0|p_off_c|COMPLETED|0:0|700|1|", f"{JOB}.0|p_off_c|COMPLETED|0:0|700|2|"),
               sacct(extra=["garbled"]), sacct(steps={u: 0 for u in PILOT}),
               sacct(steps={**{u: 700 for u in PILOT}, "p_R_b1": 900})]  # a step longer than its job
        for text in bad:
            rc, d, out = run(text, self.p)
            self.assertEqual(rc, 6, (text, d))
            self.assertFalse((out / "PROCEED").exists())

    def test_unit_defects_stop(self):
        q = products()
        z = dict(np.load(q.units / "p_R_c.npz"))
        m = json.loads(str(z["meta"]))
        m["controls"].pop("C-COUPLE")
        z["meta"] = json.dumps(m)
        q.rewrite_unit("p_R_c", z)
        rc, d, _ = run(sacct(), q)
        self.assertEqual(rc, 6)
        self.assertIn("C-COUPLE", d["units"]["p_R_c"])
        q = products()
        (q.units / "p_off_b2.root").write_bytes(b"altered")
        rc, d, _ = run(sacct(), q)
        self.assertEqual(rc, 6)

    def meta_defect(self, unit, change):
        q = products()
        z = dict(np.load(q.units / f"{unit}.npz"))
        m = json.loads(str(z["meta"]))
        change(m)
        z["meta"] = json.dumps(m)
        q.rewrite_unit(unit, z)
        return run(sacct(), q)

    def test_receipt_defects_stop(self):
        """unit_receipt (shared with the scorer): each planted meta defect fails its unit."""
        cases = {"non-finite extraction arguments": ("p_off_b3", lambda m: m.update(extract_args_finite=False)),
                 "controls ['C-EXTRA']": ("p_off_b4", lambda m: m["controls"].update({"C-EXTRA": {"pass": False}})),
                 "meta identity": ("p_off_b5", lambda m: m.update(bootstrap_seed=6))}
        for why, (unit, change) in cases.items():
            rc, d, out = self.meta_defect(unit, change)
            self.assertEqual(rc, 6, why)
            self.assertEqual(d["units"][unit], why)
            self.assertFalse((out / "PROCEED").exists())

    def test_cross_unit_defects_stop(self):
        """Each pilot-computable cross-unit control STOPs on its own defect."""
        rc, d, _ = self.meta_defect("p_off_b2", lambda m: m.update(extract_args_sha256="0" * 64))
        self.assertEqual(rc, 6)
        self.assertFalse(d["rules"]["C-NORM"])
        rc, d, _ = self.meta_defect("p_R_c", lambda m: m["support"].update(n_seeds=199))
        self.assertEqual(rc, 6)
        self.assertFalse(d["rules"]["C-SUPPORT-table"])
        import ptmc_score as S
        with mock.patch.object(S, "fix_equal", return_value={"axes": True, "contents": False}):
            rc, d, _ = run(sacct(), self.p)
        self.assertEqual(rc, 6)
        self.assertFalse(d["rules"]["C-FIX"])

    def test_seed1_fill_duplicate_stops(self):
        q = products()
        z = dict(np.load(q.units / "p_R_b1.npz"))
        for k in ("fill_entry", "fill_pt", "fill_pz", "fill_w"):
            z[k] = np.concatenate([z[k], z[k][:1]])
        q.rewrite_unit("p_R_b1", z)
        rc, d, _ = run(sacct(), q)
        self.assertEqual(rc, 6)
        self.assertFalse(d["rules"]["C-MOVE-seed1"])

    def test_recheck_requires_the_same_limit(self):
        rc, d, out = run(sacct(), self.p)
        self.assertEqual(rc, 0)
        rc2, _, _ = run(sacct(), self.p, recheck=out / "decision.json")
        self.assertEqual(rc2, 0)
        rc3, _, _ = run(sacct(job_el=1050), self.p, recheck=out / "decision.json")  # L = 143 (a PROCEED), not 144
        self.assertEqual(rc3, 6)

    def test_rerun_refuses(self):
        rc, d, out = run(sacct(), self.p)
        self.assertEqual(PP.main(["--sacct", str(out / "sacct.txt"), "--jobid", JOB, "--units", str(self.p.units),
                                  "--rows", str(self.p.rows), "--out", str(out)]), 2)


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

    def test_mandatory_absent_and_symlinked_parent_fail(self):
        (self.ref / "read-2" / "inputs" / "001_xsec.root").unlink()
        rc, out = self.stage()
        self.assertEqual(rc, 5)
        self.assertFalse((out / "manifest.json").exists())
        self.setUp()
        real = self.ref / "units"
        moved = self.ref / "units_real"
        real.rename(moved)
        real.symlink_to(moved)
        rc, out = self.stage()
        self.assertEqual(rc, 5)

    def test_a_source_changed_during_its_copy_fails(self):
        sys.path.insert(0, str(self.T.tree() / "2d-unfolding" / "ref_c2c1"))
        import ref_c2c1 as C  # the module object ptmc_stage_d4 imports
        orig = C.copy_noatime

        def copy_then_touch(src, dst):
            d = orig(src, dst)
            if Path(src).name == "c2_replica_b9.npz":
                Path(src).write_bytes(b"grown during the copy")
            return d
        with mock.patch.object(C, "copy_noatime", copy_then_touch):
            rc, out = self.stage()
        self.assertEqual(rc, 5)
        self.assertFalse((out / "manifest.json").exists())

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
