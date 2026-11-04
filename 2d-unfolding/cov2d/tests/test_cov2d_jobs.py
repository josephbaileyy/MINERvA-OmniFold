"""cov2d_jobs: the run tables (counts, labels, seeds, data files, part B's packing and limit rule), every generated
argv through re2_driver's REAL parser (PyROOT env), and the job-side input checks on synthetic files.
    cd 2d-unfolding/cov2d/tests && python -B -m unittest -v test_cov2d_jobs
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "jobs"))
import cov2d as c  # noqa: E402
import cov2d_jobs as cj  # noqa: E402

try:
    import ROOT  # noqa: F401
    HAVE_ROOT = True
except Exception:  # pragma: no cover
    HAVE_ROOT = False


class Tables(unittest.TestCase):
    def setUp(self):
        self.runs = cj.runs_of("G18")
        self.rows, self.jobs = cj.pack(self.runs, "G18")

    def test_counts_and_labels(self):
        kinds = [r["kind"] for r in self.runs]
        self.assertEqual({k: kinds.count(k) for k in set(kinds)},
                         {"central": 1, "universe": 175, "lateral": 10, "replica": 300, "toy": 300})
        self.assertEqual(len(self.runs), 786)
        self.assertEqual(len({r["label"] for r in self.runs}), 786)
        self.assertEqual(len(self.jobs), 11)
        self.assertEqual(sum(j["runs"] for j in self.jobs), 786)

    def test_toys_read_their_own_file_and_everything_else_reads_d_T(self):
        for r in self.runs:
            df = r["args"][r["args"].index("--data-file") + 1]
            if r["kind"] == "toy":
                self.assertEqual(df, f"$D/data_{r['label'].rsplit('_', 1)[1]}.root")
            else:
                self.assertEqual(df, "$D/data_5721000.root")
        seeds = [int(r["label"].rsplit("_", 1)[1]) for r in self.runs if r["kind"] == "toy"]
        self.assertEqual(seeds, list(range(5_720_000, 5_720_300)))
        self.assertEqual(cj.runs_of("AR23")[0]["args"][-1], "$D/data_5731000.root")

    def test_universes_are_the_bank_and_replicas_seeds_1_to_300(self):
        u = [r["args"][r["args"].index("--universe") + 1] for r in self.runs if r["kind"] == "universe"]
        self.assertEqual(u, [f"{b}:{i}" for b in c.ORDER for i in range(c.BANDS[b])])
        b = [int(r["args"][r["args"].index("--bootstrap-seed") + 1]) for r in self.runs if r["kind"] == "replica"]
        self.assertEqual(b, list(range(1, 301)))

    def test_packing_is_part_bs(self):
        layout = {j["job"]: (j["lanes"], j["lane_cpus"], j["runs"]) for j in self.jobs}
        self.assertEqual(layout["G18_Ua"], (2, 128, 44))
        self.assertEqual(layout["G18_Ud"], (2, 128, 43))
        self.assertEqual(layout["G18_L"], (2, 128, 11))
        self.assertEqual(layout["G18_Ba"], (4, 64, 100))
        self.assertEqual(layout["G18_Tc"], (4, 64, 100))
        self.assertTrue(all(j["limit"] < "12:00:00" for j in self.jobs))

    def test_limit_rule_reproduces_part_bs_limits(self):
        # partb_jobs.tsv: J1 866 -> 00:25:00, J2a 25300 -> 08:54:00, J3 8390 -> 03:02:00, J4a 23000 -> 08:06:00
        for longest, want in ((866, "00:25:00"), (25300, "08:54:00"), (8390, "03:02:00"), (23000, "08:06:00")):
            self.assertEqual(cj.limit_of(longest), want)

    def test_written_tables(self):
        with tempfile.TemporaryDirectory() as td:
            rec = cj.tables("G18", Path(td))
            self.assertEqual((rec["runs"], rec["jobs"]), (786, 11))
            rows = [ln.split("\t") for ln in (Path(td) / "runs_G18.tsv").read_text().splitlines()]
            self.assertEqual(rows[0], ["job", "lane", "label", "cpus", "script", "args", "est_s"])
            self.assertEqual(len(rows), 787)


@unittest.skipUnless(HAVE_ROOT, "re2_driver imports PyROOT")
class RealParser(unittest.TestCase):
    """Every generated line through re2_driver.main's own argparse (the memory: a generated argv must pass the real
    parser). parse_args is captured and the run stops there."""
    def test_every_line_parses(self):
        sys.path.insert(0, str(HERE.parents[1] / "re2"))
        import re2_driver
        env = {"$CV": "/x/cv.root", "$UNI": "/x/uni.root", "$FLUXU": "/x/fu.root", "$MC": "/x/mc.root",
               "$ACT": "/x/act", "$D": "/x/d"}

        class Stop(Exception):
            pass
        seen = []
        real = argparse.ArgumentParser.parse_args

        def capture(self, args=None, namespace=None):
            ns = real(self, args, namespace)
            seen.append(ns)
            raise Stop
        for truth in ("G18", "AR23"):
            for r in cj.runs_of(truth):
                line = " ".join(r["args"])
                for k, v in env.items():
                    line = line.replace(k, v)
                argv = ["re2_driver.py", *shlex.split(line), "--out", "/x/out.root"]
                with mock.patch.object(sys, "argv", argv), mock.patch.object(argparse.ArgumentParser, "parse_args",
                                                                             capture):
                    with self.assertRaises(Stop):
                        re2_driver.main()
                ns = seen[-1]
                self.assertTrue(ns.data_file.startswith("/x/d/data_"))
                self.assertEqual((ns.seed, ns.iters, ns.estimator), (42, 5, "lgbm"))
                if r["kind"] == "universe":
                    self.assertEqual(ns.universe, r["args"][r["args"].index("--universe") + 1])
        self.assertEqual(len(seen), 2 * 786)


class Check(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True)
        p.start()
        self.addCleanup(p.stop)
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        d = Path(self.td.name)
        (d / "act").mkdir()
        (d / "d").mkdir()
        files = {"cv.root": b"cv", **{f"act/{f}": f.encode() for f in cj.LATERAL_FILES}}
        stat_lines = []
        for rel, data in files.items():
            (d / rel).write_bytes(data)
            stat_lines.append(f"{hashlib.sha256(data).hexdigest()} 1 2 3 {d / rel}")
        (d / "inputs.stat").write_text("\n".join(stat_lines) + "\n")
        pb = []
        for s in [c.REALIZATION_SEED["G18"], *c.TOY_SEEDS["G18"]]:
            (d / "d" / f"data_{s}.root").write_bytes(str(s).encode())
            pb.append({"path": str(d / "d" / f"data_{s}.root"), "sha256": hashlib.sha256(str(s).encode()).hexdigest()})
        (d / "pseudo_b.json").write_text(json.dumps({"files": pb}))
        (d / "mc.root").write_bytes(b"mc")
        (d / "fu.root").write_bytes(b"fu")
        (d / "uni.root").write_bytes(b"uni")
        self.d = d
        self.env = {"$CV": str(d / "cv.root"), "$ACT": str(d / "act"), "$UNI": str(d / "uni.root"),
                    "$MC": str(d / "mc.root"), "$FLUXU": str(d / "fu.root"), "$D": str(d / "d")}
        cj.tables("G18", d / "t")
        self.pins = mock.patch.dict(cj.PINS, {"$MC": hashlib.sha256(b"mc").hexdigest(),
                                              "$FLUXU": hashlib.sha256(b"fu").hexdigest()})
        self.pins.start()
        self.addCleanup(self.pins.stop)

    def run_check(self, job):
        return cj.check(self.d / "t" / "runs_G18.tsv", job, self.d / "inputs.stat", self.d / "pseudo_b.json", self.env)

    def test_a_clean_lateral_job_and_toy_job_pass(self):
        for job in ("G18_L", "G18_Ta"):
            rec = self.run_check(job)
            self.assertEqual(rec["problems"], [], job)
        self.assertIn(self.env["$ACT"] + "/" + cj.LATERAL_FILES[0], self.run_check("G18_L")["checked"])

    def test_a_changed_staged_copy_stops(self):
        (self.d / "act" / cj.LATERAL_FILES[3]).write_bytes(b"changed")
        self.assertTrue(any("!= staged" in p for p in self.run_check("G18_L")["problems"]))

    def test_a_purged_staged_copy_stops_with_no_restage(self):
        (self.d / "cv.root").unlink()
        self.assertTrue(any("purged" in p for p in self.run_check("G18_Ba")["problems"]))

    def test_a_changed_data_file_stops(self):
        (self.d / "d" / "data_5720005.root").write_bytes(b"x")
        self.assertTrue(any("data_5720005" in p for p in self.run_check("G18_Ta")["problems"]))

    def test_uni_stat_and_pins(self):
        rec = self.run_check("G18_Ua")          # the fixture's $UNI is not part B's file
        self.assertTrue(any("$UNI stat" in p for p in rec["problems"]))
        with mock.patch.dict(cj.PINS, {"$MC": "0" * 64}):
            self.assertTrue(any("$MC sha256" in p for p in self.run_check("G18_Ta")["problems"]))


class Gate(unittest.TestCase):
    def test_spent_held_and_the_cap(self):
        limits = {"G18_Ua": "08:54:00", "G18_L": "03:20:00", "pseudo_G18": "03:00:00"}
        psv = ("1|cov2d-pseudo_G18|COMPLETED|7200|1\n2|cov2d-G18_Ua|RUNNING|100|1\n3|other|COMPLETED|99999|1\n")
        g = cj.gate(psv, limits, "G18_L")
        self.assertAlmostEqual(g["spent"], 2.0)
        self.assertAlmostEqual(g["held"], 8.9)
        self.assertAlmostEqual(g["total"], 2.0 + 8.9 + 3 + 20 / 60)
        self.assertTrue(g["pass"])
        big = "".join(f"{i}|cov2d-G18_Ua|COMPLETED|{3600 * 160}|1\n" for i in range(1))
        self.assertFalse(cj.gate(big, limits, "G18_Ua")["pass"])     # 160 spent + 8.9 > 165.8


class DryRun(unittest.TestCase):
    """The real job script with DRYRUN=1: its lanes print every run of the job, with $vars expanded."""
    def test_the_lateral_job_prints_its_11_runs_in_2_lanes(self):
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            cj.tables("G18", Path(td) / "tables")
            env = dict(os.environ, C=str(HERE.parents[2]), M="x", TRUTH="G18", JOB="G18_L", DRYRUN="1", COV2D_O=td)
            r = subprocess.run(["bash", str(HERE.parent / "jobs" / "cov2d_job.sbatch")], env=env, capture_output=True,
                               text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            lines = [ln for ln in r.stdout.splitlines() if ln.startswith("srun ")]
            self.assertEqual(len(lines), 11)
            self.assertEqual(sum(" X_G18:" in ln for ln in lines), 1)
            self.assertTrue(all(f"--data-file {td}/pseudo/G18/b/data_5721000.root" in ln for ln in lines))
            self.assertTrue(all("/pscratch/sd/j/josephrb/cov2d-inputs-20261104/" in ln for ln in lines))
            self.assertTrue(all(ln.startswith("srun -c 128 ") for ln in lines))


if __name__ == "__main__":
    unittest.main()
