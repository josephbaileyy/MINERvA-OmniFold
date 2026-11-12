"""COV2D-G2R's jobs (addendum J1): the tables, every generated argv through the patched driver's REAL parser, the
job-side checks, the order, the charge gate at 110, the environment test's comparison on real ROOT files, the
products TSV, and the four shell scripts run end to end against stub cluster commands (sbatch, sacct, scontrol, srun,
omnifold_py310 and the MAT setup), so no path of theirs is reachable only on the cluster untested.
    cd 2d-unfolding/cov2d/g2r/tests && python -B -m unittest -v test_g2r_jobs
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
G2R = HERE.parent
JOBS = G2R / "jobs"
REPO = HERE.parents[3]
sys.path[:0] = [str(JOBS), str(G2R.parent), str(G2R.parent / "jobs"), str(G2R.parent / "tests")]
import cov2d as c  # noqa: E402
import cov2d_jobs as cj  # noqa: E402
import g2r_jobs as gj  # noqa: E402
from deploy_fixture import GIT  # noqa: E402

try:
    import ROOT  # noqa: F401
    HAVE_ROOT = True
except Exception:  # pragma: no cover
    HAVE_ROOT = False

BANK = {f"{b}:{i}" for b in c.ORDER for i in range(c.BANDS[b])}


def rows_of(job=None, role=None, point=None):
    return [r for r in gj.runs() if (job is None or r["job"] == job) and (role is None or r["role"] == role)
            and (point is None or r["point"] == point)]


class Tables(unittest.TestCase):
    def test_counts_roles_and_points(self):
        rs = gj.runs()
        self.assertEqual(len(rs), 2 + 175 + 2 + 350)
        self.assertEqual(len({r["label"] for r in rs}), len(rs))
        self.assertEqual({r["universe"] for r in rows_of(role="g2r", point="data")}, BANK)
        for t in ("G18", "AR23"):
            self.assertEqual(sorted(r["universe"] for r in rows_of(point=t)), sorted(BANK))
        self.assertEqual([r["universe"] for r in rows_of(role="off")], list(gj.OFF))
        self.assertEqual([r["role"] for r in rows_of(job="envtest")], ["pre", "post"])

    def test_data_rows_are_part_bs_j2_rows_plus_the_map(self):
        pb = {gj.universe_of(r[5]): r for r in gj.partb_rows() if r[0].startswith("J2")}
        for r in rows_of(role="g2r", point="data"):
            p = pb[r["universe"]]
            self.assertEqual(r["args"], p[5] + " --miss-map $MAP")
            self.assertEqual((r["job"], r["lane"], r["cpus"]), ("D_U" + p[0][2:], "D_U" + p[1][2:], int(p[3])))
            self.assertNotIn("--data-file", r["args"])

    def test_off_reruns_are_part_bs_rows_exactly_at_the_end_of_d_ud_2(self):
        pb = {gj.universe_of(r[5]): r for r in gj.partb_rows() if r[0].startswith("J2")}
        lane = [r for r in gj.runs() if r["lane"] == "D_Ud.2"]
        self.assertEqual([r["universe"] for r in lane[-2:]], list(gj.OFF))
        for r in lane[-2:]:
            self.assertEqual(r["args"], pb[r["universe"]][5])
            self.assertNotIn("$MAP", r["args"])
        self.assertEqual(len(lane), 23)

    def test_tune_rows_are_cov2ds_universe_rows_plus_the_map(self):
        for t in ("G18", "AR23"):
            want = [r for r in cj.pack(cj.runs_of(t), t)[0] if r["kind"] == "universe"]
            got = rows_of(point=t)
            self.assertEqual(len(got), 175)
            for w, g in zip(want, got):
                self.assertEqual(g["args"], " ".join(w["args"]) + " --miss-map $MAP")
                self.assertEqual((g["job"], g["lane"], g["cpus"]), (w["job"], w["lane"], w["cpus"]))
                self.assertIn(f"$D/data_{c.REALIZATION_SEED[t]}.root", g["args"])

    def test_envtest_rows_are_part_bs_mares_0_both_unpatched(self):
        pb = {gj.universe_of(r[5]): r for r in gj.partb_rows() if r[0].startswith("J2")}
        for r in rows_of(job="envtest"):
            self.assertEqual(r["args"], pb["MaRES:0"][5])
            self.assertEqual(r["est_s"], gj.ENVTEST_EST_S)

    def test_limits_and_the_price(self):
        lim = {j["job"]: j["limit"] for j in gj.jobs(gj.runs())}
        self.assertEqual(lim["prepare"], "02:00:00")
        self.assertEqual(lim["envtest"], "01:04:00")
        self.assertEqual(lim["D_Ud"], "09:18:00")
        for j in ("D_Ua", "D_Ub", "D_Uc", "G18_Ua", "G18_Ud", "AR23_Ua", "AR23_Ud"):
            self.assertEqual(lim[j], "08:54:00", j)
        self.assertEqual(len(lim), 14)
        after = sum(cj.hms(v) for k, v in lim.items() if k not in ("envtest", "prepare")) / 3600
        self.assertAlmostEqual(after, 3 * 8.9 + 9.3 + 8 * 8.9)
        self.assertLessEqual(after, gj.CAP_NODE_H)

    def test_part_bs_table_is_read_at_its_digest_and_must_be_the_bank(self):
        with mock.patch.object(gj, "PARTB_RUNS", (gj.PARTB_RUNS[0], "0" * 64)):
            with self.assertRaises(c.Refusal):
                gj.runs()
        rows = gj.partb_rows()
        j2 = [i for i, r in enumerate(rows) if r[0].startswith("J2")]
        with mock.patch.object(gj, "partb_rows", lambda: [r for i, r in enumerate(rows) if i != j2[-1]]):
            with self.assertRaises(c.Refusal):
                gj.runs()

    def test_written_tables_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            rec = gj.tables(Path(td))
            self.assertEqual(rec["runs"], 529)
            back = gj.read_runs(Path(td) / "runs_g2r.tsv")
            self.assertEqual([r["label"] for r in back], [r["label"] for r in gj.runs()])
            self.assertEqual(gj.read_limits(Path(td) / "jobs_g2r.tsv")["D_Ud"], "09:18:00")
            (Path(td) / "bad.tsv").write_text("x\ty\n")
            with self.assertRaises(c.Refusal):
                gj.read_runs(Path(td) / "bad.tsv")
            with self.assertRaises(c.Refusal):
                gj.read_limits(Path(td) / "bad.tsv")


@unittest.skipUnless(HAVE_ROOT, "PyROOT")
class RealParser(unittest.TestCase):
    """Every generated line through the patched re2_driver.main's own argparse; the run stops at parse_args."""
    def test_every_line_parses(self):
        sys.path.insert(0, str(REPO / "2d-unfolding" / "re2"))
        import re2_driver
        env = {"$UNI": "/x/uni.root", "$FLUXU": "/x/fu.root", "$MC": "/x/mc.root", "$MAP": "/x/map.npz", "$D": "/x/d"}

        class Stop(Exception):
            pass
        seen = []
        real = argparse.ArgumentParser.parse_args

        def capture(self, args=None, namespace=None):
            seen.append(real(self, args, namespace))
            raise Stop
        rs = gj.runs()
        for r in rs:
            line = r["args"]
            for k, v in env.items():
                line = line.replace(k, v)
            argv = ["re2_driver.py", *shlex.split(line), "--out", "/x/out.root"]
            with mock.patch.object(sys, "argv", argv), mock.patch.object(argparse.ArgumentParser, "parse_args", capture):
                with self.assertRaises(Stop):
                    re2_driver.main()
            ns = seen[-1]
            self.assertEqual((ns.seed, ns.iters, ns.estimator, ns.universe), (42, 5, "lgbm", r["universe"]))
            self.assertEqual(ns.miss_map, "/x/map.npz" if r["role"] == "g2r" else None, r["label"])
            if r["point"] == "data":
                self.assertIsNone(ns.data_file)
            else:
                self.assertEqual(ns.data_file, f"/x/d/data_{c.REALIZATION_SEED[r['point']]}.root")
        self.assertEqual(len(seen), len(rs))


class Check(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True)
        p.start()
        self.addCleanup(p.stop)
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        d = Path(self.td.name)
        for n, b in (("uni.root", b"uni"), ("mc.root", b"mc"), ("fu.root", b"fu"), ("map.npz", b"map")):
            (d / n).write_bytes(b)
        (d / "d").mkdir()
        self.real = f"data_{c.REALIZATION_SEED['G18']}.root"
        (d / "d" / self.real).write_bytes(b"real")
        gj.tables(d / "t")
        s = os.stat(d / "uni.root")
        for patch in (mock.patch.object(cj, "UNI_STAT", f"{s.st_size} {int(s.st_mtime)} {s.st_ino}"),
                      mock.patch.dict(cj.PINS, {"$MC": hashlib.sha256(b"mc").hexdigest(),
                                                "$FLUXU": hashlib.sha256(b"fu").hexdigest()}),
                      mock.patch.object(gj, "committed_data_sha",
                                        lambda t: {self.real: hashlib.sha256(b"real").hexdigest()})):
            patch.start()
            self.addCleanup(patch.stop)
        self.d = d
        self.map_sha = hashlib.sha256(b"map").hexdigest()
        self.env = {"$UNI": str(d / "uni.root"), "$MC": str(d / "mc.root"), "$FLUXU": str(d / "fu.root"),
                    "$MAP": str(d / "map.npz"), "$D": str(d / "d")}

    def run_check(self, job, map_sha="default"):
        return gj.check(self.d / "t" / "runs_g2r.tsv", job, self.map_sha if map_sha == "default" else map_sha, self.env)

    def test_clean_jobs_pass(self):
        for job in ("envtest", "D_Ua", "D_Ud", "G18_Ua"):
            self.assertEqual(self.run_check(job)["problems"], [], job)
        self.assertIn(self.env["$MAP"], self.run_check("D_Ua")["checked"])
        self.assertNotIn(self.env["$MAP"], self.run_check("envtest")["checked"])
        self.assertIn(str(self.d / "d" / self.real), self.run_check("G18_Ua")["checked"])

    def test_the_map_must_be_the_committed_one(self):
        self.assertTrue(any("committed prepare" in p for p in self.run_check("D_Ua", "0" * 64)["problems"]))
        self.assertTrue(any("no committed map" in p for p in self.run_check("D_Ua", None)["problems"]))
        (self.d / "map.npz").unlink()
        self.assertTrue(any("map.npz is missing" in p for p in self.run_check("D_Ua")["problems"]))

    def test_uni_and_pins(self):
        with mock.patch.object(cj, "UNI_STAT", "1 2 3"):
            self.assertTrue(any("$UNI stat" in p for p in self.run_check("D_Ub")["problems"]))
        with mock.patch.dict(cj.PINS, {"$MC": "0" * 64}):
            self.assertTrue(any("$MC sha256" in p for p in self.run_check("D_Ub")["problems"]))
        with mock.patch.dict(cj.PINS, {"$FLUXU": "0" * 64}):
            self.assertTrue(any("$FLUXU sha256" in p for p in self.run_check("envtest")["problems"]))

    def test_the_realization_g8(self):
        (self.d / "d" / self.real).write_bytes(b"changed")
        self.assertTrue(any("(G8)" in p for p in self.run_check("G18_Ub")["problems"]))
        (self.d / "d" / self.real).unlink()
        self.assertTrue(any("regeneration is its own connect" in p for p in self.run_check("G18_Ub")["problems"]))
        with mock.patch.object(gj, "committed_data_sha", lambda t: {}):
            self.assertTrue(any("not in G18's step-B record" in p for p in self.run_check("G18_Ub")["problems"]))

    def test_a_job_with_no_runs_or_mixed_points(self):
        with self.assertRaises(c.Refusal):
            self.run_check("prepare")
        rows = (self.d / "t" / "runs_g2r.tsv").read_text().splitlines()
        rows[-1] = rows[-1].replace("\tAR23\t", "\tdata\t")
        (self.d / "t" / "runs_g2r.tsv").write_text("\n".join(rows) + "\n")
        self.assertTrue(any("mixes points" in p for p in self.run_check("AR23_Ud")["problems"]))


class CommittedStepB(unittest.TestCase):
    def test_the_committed_records_name_each_realization(self):
        for t in ("G18", "AR23"):
            self.assertRegex(gj.committed_data_sha(t)[f"data_{c.REALIZATION_SEED[t]}.root"], "^[0-9a-f]{64}$")


class Order(unittest.TestCase):
    PASS_E = {gj.ENVTEST_RECORD: {"verdict": "PASS"}}

    def both(self, sha="s" * 64):
        return {gj.ENVTEST_RECORD: {"verdict": "PASS"}, gj.PREPARE_RECORD: {"verdict": "PASS", "map_npz_sha256": sha}}

    def test_the_sequence(self):
        self.assertEqual(gj.order("envtest", {}, set(), False, None), [])
        self.assertTrue(gj.order("prepare", {}, set(), False, None))
        self.assertEqual(gj.order("prepare", self.PASS_E, set(), False, None), [])
        self.assertTrue(gj.order("D_Ua", self.PASS_E, set(), False, None))
        self.assertEqual(gj.order("D_Ua", self.both(), set(), False, "s" * 64), [])
        for job in ("D_Ub", "D_Ud", "G18_Ua", "AR23_Ud"):
            self.assertTrue(any("first --miss-map" in n for n in gj.order(job, self.both(), set(), False, "s" * 64)))
            self.assertEqual(gj.order(job, self.both(), set(), True, "s" * 64), [])

    def test_each_job_once_and_records_must_pass(self):
        self.assertTrue(any("already submitted" in n for n in gj.order("envtest", {}, {"envtest"}, False, None)))
        bad = {gj.ENVTEST_RECORD: {"verdict": "INVALID"}}
        self.assertTrue(gj.order("prepare", bad, set(), False, None))
        self.assertTrue(any("not the committed" in n for n in gj.order("D_Ua", self.both(), set(), True, "t" * 64)))
        stop = {**self.both(), gj.PREPARE_RECORD: {"verdict": "STOP"}}
        self.assertTrue(gj.order("D_Ua", stop, set(), True, "s" * 64))

    def test_first_run_done(self):
        with tempfile.TemporaryDirectory() as td:
            o = Path(td)
            self.assertFalse(gj.first_run_done(o))
            (o / "walls.D_Ua.1.tsv").write_text("A_2p2h_0\t1\t2\t1\n")
            (o / "out" / "A_2p2h_0").mkdir(parents=True)
            (o / "out" / "A_2p2h_0" / "xsec.root").write_bytes(b"x")
            self.assertFalse(gj.first_run_done(o))                        # rc 1
            (o / "walls.D_Ua.2.tsv").write_text("A_BhtBY_1\t1\t2\t0\n")
            self.assertFalse(gj.first_run_done(o))                        # rc 0, no product
            (o / "walls.D_Ua.2.tsv").write_text("A_2p2h_0\t1\t2\t0\n")
            self.assertTrue(gj.first_run_done(o))


class Gate(unittest.TestCase):
    def setUp(self):
        self.lim = {j["job"]: j["limit"] for j in gj.jobs(gj.runs())}

    def test_spent_held_lag_and_the_cap(self):
        psv = ("1|cov2dg2r-envtest|COMPLETED|1800|1\n2|cov2dg2r-prepare|RUNNING|60|1\n"
               "3|cov2d-G18_Ua|COMPLETED|99999|1\n4|ll5d_pilot|RUNNING|5|1\n")
        g = gj.gate(psv + "\n  \n", self.lim, "prepare", {"1": "envtest"})
        self.assertAlmostEqual(g["spent"], 0.5)
        self.assertAlmostEqual(g["held"], 2.0)
        self.assertTrue(g["pass"])
        g = gj.gate("1|cov2dg2r-envtest|COMPLETED|1800|1\n", self.lim, "D_Ua", {"1": "envtest", "2": "prepare"})
        self.assertEqual(g["lagging_ids"], ["2"])                       # submitted, not yet in sacct: held at its limit
        self.assertAlmostEqual(g["held"], 2.0)

    def test_unknown_names_refuse_and_others_are_ignored(self):
        with self.assertRaises(c.Refusal):
            gj.gate("9|cov2dg2r-mystery|RUNNING|1|1\n", self.lim, "envtest", {})
        with self.assertRaises(c.Refusal):
            gj.gate("", self.lim, "nope", {})
        g = gj.gate("9|cov2d-AR23_Tc|RUNNING|1|1\n9|rdx_s1_1A|RUNNING|1|1\n", self.lim, "envtest", {})
        self.assertEqual((g["spent"], g["held"]), (0.0, 0.0))

    def test_the_cap_refuses(self):
        g = gj.gate("1|cov2dg2r-envtest|COMPLETED|%d|1\n" % (3600 * 109), self.lim, "envtest", {})
        self.assertFalse(g["pass"])

    def test_the_projection_is_a_stop_for_unfold_jobs_only(self):
        sub = {"1": "envtest", "2": "prepare"}
        ok = "1|cov2dg2r-envtest|COMPLETED|2700|1\n2|cov2dg2r-prepare|COMPLETED|3600|1\n"
        g = gj.gate(ok, self.lim, "D_Ua", sub)
        self.assertFalse(g["stop"])
        self.assertAlmostEqual(g["projection"], 0.75 + 1.0 + 107.2)
        g = gj.gate("1|cov2dg2r-envtest|COMPLETED|2700|1\n2|cov2dg2r-prepare|COMPLETED|7200|1\n", self.lim, "D_Ua", sub)
        self.assertAlmostEqual(g["projection"], 109.95)                 # 0.75 + 2.0 + 107.2: inside the cap
        self.assertFalse(g["stop"])
        big = "1|cov2dg2r-envtest|COMPLETED|2700|1\n2|cov2dg2r-prepare|COMPLETED|10800|1\n"
        g = gj.gate(big, self.lim, "D_Ua", sub)
        self.assertTrue(g["stop"])
        self.assertTrue(g["pass"])                                      # the job alone would fit: still a STOP
        self.assertFalse(gj.gate(big, self.lim, "prepare", {"1": "envtest"})["stop"])

    def test_the_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            gj.tables(d)
            (d / "s.psv").write_text("1|cov2dg2r-envtest|COMPLETED|2700|1\n2|cov2dg2r-prepare|COMPLETED|10800|1\n")
            (d / "sub.log").write_text("t M=x job=envtest id=1 limit=01:04:00\nt M=x job=prepare id=2 limit=02:00:00\n")
            args = ["gate", "--sacct", str(d / "s.psv"), "--tables", str(d), "--submissions", str(d / "sub.log")]
            with mock.patch("sys.stdout"):
                self.assertEqual(gj.main(args + ["--want", "D_Ua"]), 9)
                (d / "s.psv").write_text("1|cov2dg2r-envtest|COMPLETED|2700|1\n")
                self.assertEqual(gj.main(args + ["--want", "D_Ua"]), 0)
                (d / "s.psv").write_text("1|cov2dg2r-envtest|COMPLETED|%d|1\n" % (3600 * 105))
                self.assertEqual(gj.main(args + ["--want", "D_Ua"]), 9)
                (d / "sub.log").write_text("")
                self.assertEqual(gj.main(args + ["--want", "prepare"]), 0)
                (d / "s.psv").write_text("1|cov2dg2r-envtest|COMPLETED|%d|1\n" % (3600 * 109))
                self.assertEqual(gj.main(args + ["--want", "prepare"]), 3)
                self.assertEqual(gj.main(args + ["--want", "nope"]), 5)


def write_product(path: Path, scale=1.0, err=None, param=1.5, named=None, run_config=None):
    import ROOT
    f = ROOT.TFile(str(path), "RECREATE")
    h = ROOT.TH2D("hUnfold2D", "", 3, 0, 3, 2, 0, 2)
    for i in range(1, 4):
        for j in range(1, 3):
            h.SetBinContent(i, j, scale * (i + 10 * j) / 7.0)
            h.SetBinError(i, j, (err or 0.1) * i)
    h.Write()
    ROOT.TParameter("double")("potScale", param).Write()
    rc = {"out": str(path), "seed": 42, "universe": "MaRES:0", **(run_config or {})}
    names = {"runConfig": json.dumps(rc, sort_keys=True), "driverFile": str(path), "driverSha256": str(path),
             "fluxSource": "f", "omnifoldHelperSha256": "h", **(named or {})}
    for k, v in names.items():
        ROOT.TNamed(k, v).Write()
    f.Close()


@unittest.skipUnless(HAVE_ROOT, "PyROOT")
class EnvTest(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.d = Path(self.td.name)
        write_product(self.d / "pre.root")

    def cmp(self, **post):
        post.setdefault("run_config", {"miss_map": None})
        write_product(self.d / "post.root", **post)
        return gj.envtest(str(self.d / "pre.root"), str(self.d / "post.root"))

    def test_equal_products_pass_with_the_code_records_set_aside(self):
        rec = self.cmp()
        self.assertEqual(rec["verdict"], "PASS", rec["problems"])
        self.assertEqual((rec["histograms"], rec["parameters"]), (1, 1))

    def test_each_difference_is_invalid(self):
        cases = {"histogram": dict(scale=1.0 + 2 ** -52), "error": dict(err=0.1 + 1e-17),
                 "param": dict(param=1.5000000000000002), "named": dict(named={"fluxSource": "g"}),
                 "config": dict(run_config={"miss_map": None, "seed": 43}),
                 "flag on": dict(run_config={"miss_map": "/x/map.npz"}),
                 "g2r record": dict(named={"g2rMissMap": "{}"}),
                 "helper": dict(named={"omnifoldHelperSha256": "other"})}
        for name, kw in cases.items():
            self.assertEqual(self.cmp(**kw)["verdict"], "INVALID", name)

    def test_a_missing_histogram_and_an_unopenable_file(self):
        import ROOT
        f = ROOT.TFile(str(self.d / "post.root"), "RECREATE")
        ROOT.TNamed("runConfig", json.dumps({"miss_map": None})).Write()
        f.Close()
        self.assertTrue(any("histograms differ" in p for p in
                            gj.envtest(str(self.d / "pre.root"), str(self.d / "post.root"))["problems"]))
        (self.d / "junk.root").write_bytes(b"not root")
        with self.assertRaises(c.Refusal):
            gj.envtest(str(self.d / "pre.root"), str(self.d / "junk.root"))

    def test_the_cli(self):
        write_product(self.d / "post.root", run_config={"miss_map": None})
        out = self.d / "e.json"
        with mock.patch("sys.stdout"):
            self.assertEqual(gj.main(["envtest", "--pre", str(self.d / "pre.root"), "--post", str(self.d / "post.root"),
                                      "--out", str(out)]), 0)
        self.assertEqual(json.loads(out.read_text())["verdict"], "PASS")
        write_product(self.d / "post.root", scale=2.0, run_config={"miss_map": None})
        with mock.patch("sys.stdout"):
            self.assertEqual(gj.main(["envtest", "--pre", str(self.d / "pre.root"), "--post", str(self.d / "post.root"),
                                      "--out", str(out)]), 5)


class Products(unittest.TestCase):
    def test_rows_for_each_point(self):
        with tempfile.TemporaryDirectory() as td:
            o = Path(td)
            gj.tables(o / "tables")
            rs = gj.runs()
            sums = {}
            for r in rs:
                sums.setdefault(r["job"], []).append(f"{hashlib.sha256(r['label'].encode()).hexdigest()}  {r['label']}/xsec.root")
            for job, lines in sums.items():
                (o / f"SHA256SUMS.{job}.1").write_text("\n".join(lines) + "\n")
            data = gj.products(o / "tables" / "runs_g2r.tsv", o, "data")
            self.assertEqual(len(data), 177)
            self.assertEqual(sorted(r[3] for r in data).count("off"), 2)
            self.assertEqual(data[0][1], str(o / "out" / data[0][0] / "xsec.root"))
            self.assertEqual(len(gj.products(o / "tables" / "runs_g2r.tsv", o, "G18")), 175)
            with mock.patch("sys.stdout"):
                self.assertEqual(gj.main(["products", "--runs", str(o / "tables" / "runs_g2r.tsv"), "--o", str(o),
                                          "--point", "AR23", "--out", str(o / "p.tsv")]), 0)
            self.assertEqual(len((o / "p.tsv").read_text().splitlines()), 175)
            (o / "SHA256SUMS.extra.1").write_text("0" * 64 + "  A_2p2h_0/xsec.root\n")
            with self.assertRaises(c.Refusal):
                gj.products(o / "tables" / "runs_g2r.tsv", o, "data")
            (o / "SHA256SUMS.extra.1").unlink()
            (o / "SHA256SUMS.D_Ua.1").unlink()
            with self.assertRaises(c.Refusal):
                gj.products(o / "tables" / "runs_g2r.tsv", o, "data")


# ---------------------------------------------------------------------------------------------------------------
# The shell scripts, end to end against stubs. The stub directory stands in for $A (the MAT setup, $UNI, $MC, $FLUXU)
# and omnifold_py310; PATH carries stub sbatch, sacct, scontrol and srun. The stub python (a function the stub MAT
# setup defines) runs the real python for everything except the guarded driver run, which copies a fixture product.
# ---------------------------------------------------------------------------------------------------------------
STUB_SETUP = textwrap.dedent("""\
    python() {
        if [[ "$1" == */nd-unfolding/mnv_guarded_run.py ]]; then
            local out="" prev=""
            for a in "$@"; do [ "$prev" = "--out" ] && out=$a; prev=$a; done
            case "$out" in *E_post_*) cp "${STUB_PRODUCT_POST:-$STUB_PRODUCT}" "$out" ;; *) cp "$STUB_PRODUCT" "$out" ;; esac
            return "${STUB_RUN_RC:-0}"
        fi
        if [[ "$*" == *mat_environment* ]]; then echo '{"stub": true}'; return "${STUB_MATENV_RC:-0}"; fi
        if [[ "$*" == *" check "* ]]; then "$STUB_REALPY" "$STUB_DIR/stubcheck.py" "$@"; return; fi
        "$STUB_REALPY" "$@"
    }
    export -f python
""")
STUB_PY310 = textwrap.dedent("""\
    #!/usr/bin/env bash
    case "$*" in
        *run_check_mat_setup*) exit "${STUB_MATSETUP_RC:-0}" ;;
        *uni-stat*) echo "UNI-STAT ${STUB_UNISTAT:-PASS}"; [ "${STUB_UNISTAT:-PASS}" = PASS ] ;;
        *"import numpy, uproot"*) echo "python stub numpy stub uproot stub" ;;
        *g.PRE_M*) echo "$STUB_PRE_M" ;;
        *g2r_prepare.py*)
            out=""; prev=""; for a in "$@"; do [ "$prev" = "--out" ] && out=$a; prev=$a; done
            n=0; prev=""; on=0; for a in "$@"; do [ "$a" = "--blocks" ] && { on=1; continue; }; [ "$a" = "--out" ] && on=0; [ $on = 1 ] && n=$((n+1)); done
            mkdir -p "$out"; echo "{\\"blocks\\": $n}" > "$out/g2r_prepare.json"; echo map > "$out/g2r_map.npz"
            exit "${STUB_PREPARE_RC:-0}" ;;
        *) exec "$STUB_REALPY" "$@" ;;
    esac
""")
STUB_CHECK = textwrap.dedent("""\
    import hashlib, os, sys
    gj_path, args = sys.argv[2], sys.argv[3:]          # argv: stubcheck.py -B <g2r_jobs.py> check ...
    sys.path.insert(0, os.path.dirname(gj_path))
    import g2r_jobs as gj
    import cov2d_jobs as cj
    os.O_NOATIME = getattr(os, "O_NOATIME", 0)
    s = os.stat(os.environ["UNI"])
    cj.UNI_STAT = f"{s.st_size} {int(s.st_mtime)} {s.st_ino}"
    cj.PINS.update({"$MC": hashlib.sha256(open(os.environ["MC"], "rb").read()).hexdigest(),
                    "$FLUXU": hashlib.sha256(open(os.environ["FLUXU"], "rb").read()).hexdigest()})
    real = {n: hashlib.sha256(open(os.path.join(os.environ["STUB_DIR"], "cov2d-run/pseudo/G18/b", n), "rb").read()).hexdigest()
            for n in os.listdir(os.path.join(os.environ["STUB_DIR"], "cov2d-run/pseudo/G18/b"))}
    gj.committed_data_sha = lambda t: real
    if os.environ.get("STUB_CHECK_FAIL"):
        cj.PINS["$MC"] = "0" * 64
    sys.exit(gj.main(args))
""")
STUB_BIN = {
    "scontrol": '#!/usr/bin/env bash\necho "JobId=$SLURM_JOB_ID QOS=${STUB_QOS:-regular_1} TimeLimit=$STUB_LIMIT Partition=x"\n',
    "srun": '#!/usr/bin/env bash\nwhile [[ "$1" == -* ]]; do case "$1" in -c|-n) shift 2 ;; *) shift ;; esac; done\n"$@"\n',
    "sbatch": textwrap.dedent("""\
        #!/usr/bin/env bash
        n=$(( $(cat "$STUB_DIR/next_id" 2>/dev/null || echo 1000) + 1 )); echo $n > "$STUB_DIR/next_id"
        echo "$*" >> "$STUB_DIR/sbatch.log"; echo "${STUB_SBATCH_OUT:-$n;perlmutter}"
    """),
    "sacct": textwrap.dedent("""\
        #!/usr/bin/env bash
        if [[ " $* " == *" -j "* ]]; then
            id=""; prev=""; for a in "$@"; do [ "$prev" = "-j" ] && id=$a; prev=$a; done
            [ "${STUB_SACCT_LISTS:-1}" = 1 ] && echo "$id"; exit 0
        fi
        cat "$STUB_DIR/sacct.psv" 2>/dev/null; exit 0
    """),
    "sleep": "#!/usr/bin/env bash\nexit 0\n",
}


class Shell(unittest.TestCase):
    """A stub world: the deploy is this checkout's tree copied into a git repository (M), with origin/main carrying the
    binding's M_J1 line and the committed records."""
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        root = Path(cls.td.name)
        cls.root = root
        stub = root / "stub"
        (stub / "bin").mkdir(parents=True)
        for name, body in STUB_BIN.items():
            (stub / "bin" / name).write_text(body)
            (stub / "bin" / name).chmod(0o755)
        (stub / "py310").write_text(STUB_PY310)
        (stub / "py310").chmod(0o755)
        (stub / "stubcheck.py").write_text(STUB_CHECK)
        a = stub / "A" / "2d-unfolding"
        (a / "baseline_flux").mkdir(parents=True)
        (stub / "A" / "setup_salloc_env.sh").write_text(STUB_SETUP)
        for rel, b in (("runEventLoopOmniFold_MEFHC_universes_full.root", b"uni"),
                       ("baseline_flux/runEventLoopMC_MEFHC.root", b"mc"),
                       ("baseline_flux/flux_integral_universes_MEFHC.root", b"fu")):
            (a / rel).write_bytes(b)
        for p in "1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P".split():
            (a / f"runEventLoopOmniFold_{p}_universes_full.root").write_bytes(p.encode())
        g18 = stub / "cov2d-run" / "pseudo" / "G18" / "b"
        g18.mkdir(parents=True)
        (g18 / f"data_{c.REALIZATION_SEED['G18']}.root").write_bytes(b"real")
        prod, post = root / "product.root", root / "product_post.root"   # the pre-patch driver has no miss_map option
        if HAVE_ROOT:
            write_product(prod)
            write_product(post, run_config={"miss_map": None})
        else:  # pragma: no cover
            prod.write_bytes(b"product")
            post.write_bytes(b"product")
        cls.prod, cls.post = prod, post
        # the deploy: the files the scripts and g2r_jobs read, at M; origin/main adds the binding and records
        origin = root / "origin"
        keep = ["2d-unfolding/cov2d", "2d-unfolding/re2/re2_driver.py", "nd-unfolding/mnv_guarded_run.py",
                str(gj.PARTB_RUNS[0].relative_to(REPO))] + [cj.PSEUDO_RECORD.format(truth=t) for t in ("G18", "AR23")]
        for k in keep:
            src = REPO / k
            dst = origin / k
            if src.is_dir():
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        subprocess.run(GIT + ["init", "-q", str(origin)], check=True)
        subprocess.run(GIT + ["-C", str(origin), "symbolic-ref", "HEAD", "refs/heads/main"], check=True)
        subprocess.run(GIT + ["-C", str(origin), "add", "-A"], check=True)
        subprocess.run(GIT + ["-C", str(origin), "commit", "-q", "-m", "code"], check=True)
        cls.M = subprocess.run(["git", "-C", str(origin), "rev-parse", "HEAD"], capture_output=True, text=True,
                               check=True).stdout.strip()
        cls.origin = origin
        cls.bind = origin / "docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-G2R-BINDING-1.md"
        cls.bind.parent.mkdir(parents=True, exist_ok=True)
        cls.bind.write_text(f"# binding\n\n**M_J1 = `{cls.M}`**\n")
        cls.commit_origin("binding J1")
        cls.deploy = root / "deploy"
        subprocess.run(GIT + ["clone", "-q", str(origin), str(cls.deploy)], check=True)
        subprocess.run(GIT + ["-C", str(cls.deploy), "checkout", "-q", "--detach", cls.M], check=True)
        # the pre-patch deploy: a second clean checkout (PRE_M stands for its HEAD)
        cls.pre = root / "pre"
        subprocess.run(GIT + ["clone", "-q", str(origin), str(cls.pre)], check=True)
        subprocess.run(GIT + ["-C", str(cls.pre), "checkout", "-q", "--detach", cls.M], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    @classmethod
    def commit_origin(cls, msg):
        subprocess.run(GIT + ["-C", str(cls.origin), "add", "-A"], check=True)
        subprocess.run(GIT + ["-C", str(cls.origin), "commit", "-q", "-m", msg], check=True)

    def setUp(self):
        self.o = Path(tempfile.mkdtemp(dir=self.root))
        stub = self.root / "stub"
        for f in ("next_id", "sbatch.log", "sacct.psv"):
            (stub / f).unlink(missing_ok=True)
        self.env = {k: v for k, v in os.environ.items()
                    if k not in ("G2R_O", "G2R_TEST_STUB", "NERSC_HOST") and not k.startswith("SLURM_")}
        self.env.update(G2R_O=str(self.o), G2R_TEST_STUB=str(stub), STUB_DIR=str(stub), STUB_REALPY=sys.executable,
                        STUB_PRODUCT=str(self.prod), STUB_PRODUCT_POST=str(self.post), STUB_PRE_M=self.M, PATH=f"{stub / 'bin'}:{os.environ['PATH']}",
                        C=str(self.deploy), M=self.M, SLURM_JOB_ID="77")
        (self.o / "tables").mkdir()
        gj.tables(self.o / "tables")
        (self.o / "prepare").mkdir()
        (self.o / "prepare" / "g2r_map.npz").write_bytes(b"the map")
        self.env["MAPSHA"] = hashlib.sha256(b"the map").hexdigest()

    def sh(self, script, *args, **env):
        return subprocess.run(["bash", str(JOBS / script) if not script.startswith("/") else script, *args],
                              env={**self.env, **env}, capture_output=True, text=True)

    # --- g2r_env.sh
    def test_the_hooks_are_refused_on_a_nersc_machine(self):
        r = subprocess.run(["bash", "-c", f"C={self.deploy}; source {JOBS / 'g2r_env.sh'}; echo $O"],
                           env={**self.env, "NERSC_HOST": "perlmutter"}, capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("test hooks never run here", r.stdout)
        r = subprocess.run(["bash", "-c", f"C={self.deploy}; source {JOBS / 'g2r_env.sh'}; echo $O; g2r_data_dir G18;"
                                          " g2r_data_dir AR23; g2r_data_dir data; echo $P5_BLOCKS | wc -w; g2r_data_dir x"],
                           env=self.env, capture_output=True, text=True)
        out = r.stdout.split("\n")
        self.assertEqual(out[0], str(self.o))
        self.assertTrue(out[1].endswith("cov2d-run/pseudo/G18/b") and out[2].endswith("cov2d-run/pseudo/AR23-a2/b"))
        self.assertEqual((out[3], out[4].strip()), ("", "12"))
        self.assertEqual(r.returncode, 2)

    def test_without_hooks_the_paths_are_the_clusters(self):
        env = {k: v for k, v in self.env.items() if k not in ("G2R_O", "G2R_TEST_STUB")}
        r = subprocess.run(["bash", "-c", f"C={self.deploy}; source {JOBS / 'g2r_env.sh'}; echo $O; echo $UNI; echo $MAP"],
                           env=env, capture_output=True, text=True)
        self.assertEqual(r.stdout.split(), ["/pscratch/sd/j/josephrb/cov2d-g2r-20261112",
                                            "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/"
                                            "runEventLoopOmniFold_MEFHC_universes_full.root",
                                            "/pscratch/sd/j/josephrb/cov2d-g2r-20261112/prepare/g2r_map.npz"])

    # --- g2r_job.sbatch
    def test_dry_run_of_d_ud_prints_its_45_runs_with_the_off_reruns_unpatched(self):
        r = self.sh("g2r_job.sbatch", JOB="D_Ud", DRYRUN="1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        lines = [ln for ln in r.stdout.splitlines() if ln.startswith("srun")]
        self.assertEqual(len(lines), 45)
        off = [ln for ln in lines if ": " in ln and ln.split()[3].startswith("O_")]
        self.assertEqual(len(off), 2)
        self.assertTrue(all("--miss-map" not in ln for ln in off))
        self.assertTrue(all(f"--miss-map {self.o}/prepare/g2r_map.npz" in ln for ln in lines if ln not in off))

    def test_dry_run_of_a_tune_job_reads_its_realization(self):
        r = self.sh("g2r_job.sbatch", JOB="AR23_Ub", DRYRUN="1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        lines = [ln for ln in r.stdout.splitlines() if ln.startswith("srun")]
        self.assertEqual(len(lines), 44)
        self.assertTrue(all("cov2d-run/pseudo/AR23-a2/b/data_5731000.root" in ln for ln in lines))

    def test_the_job_script_refuses_the_envtest_and_prepare_and_mixed_points(self):
        for job in ("envtest", "prepare"):
            r = self.sh("g2r_job.sbatch", JOB=job, DRYRUN="1")
            self.assertEqual(r.returncode, 2)
            self.assertIn("has its own script", r.stdout)
        r = self.sh("g2r_job.sbatch", JOB="nope", DRYRUN="1")
        self.assertEqual(r.returncode, 2)

    def test_a_real_run_of_g18_ud_against_stubs(self):
        r = self.sh("g2r_job.sbatch", JOB="G18_Ud", STUB_LIMIT="08:54:00")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        sums = "".join(p.read_text() for p in sorted(self.o.glob("SHA256SUMS.G18_Ud.*")))
        self.assertEqual(len(sums.splitlines()), 43)
        walls = "".join(p.read_text() for p in sorted(self.o.glob("walls.G18_Ud.*.tsv")))
        self.assertTrue(all(ln.endswith("\t0") for ln in walls.splitlines()))
        # a second run refuses to overwrite, run by run, and exits 1
        r = self.sh("g2r_job.sbatch", JOB="G18_Ud", STUB_LIMIT="08:54:00")
        self.assertEqual(r.returncode, 1)
        self.assertIn("exists; not overwritten", r.stdout)

    def test_a_real_run_stops_on_a_failed_check_and_the_wrong_limit(self):
        r = self.sh("g2r_job.sbatch", JOB="D_Ua", MAPSHA="0" * 64, STUB_LIMIT="08:54:00")
        self.assertEqual(r.returncode, 4)
        self.assertIn("committed prepare record", r.stdout)
        r = self.sh("g2r_job.sbatch", JOB="D_Ub", MAPSHA="0" * 64, STUB_LIMIT="01:00:00")
        self.assertEqual(r.returncode, 2)
        self.assertIn("TimeLimit is not 08:54:00", r.stdout)

    def test_a_failed_run_is_recorded_and_the_lane_goes_on(self):
        r = self.sh("g2r_job.sbatch", JOB="G18_Uc", STUB_LIMIT="08:54:00", STUB_RUN_RC="3")
        self.assertEqual(r.returncode, 1)
        walls = "".join(p.read_text() for p in sorted(self.o.glob("walls.G18_Uc.*.tsv")))
        self.assertEqual(len(walls.splitlines()), 44)
        self.assertTrue(all(ln.endswith("\t1") for ln in walls.splitlines()))
        self.assertFalse(list(self.o.glob("SHA256SUMS.G18_Uc.*")))

    def test_a_dirty_deploy_is_refused(self):
        (self.deploy / "stray").write_text("x")
        try:
            r = self.sh("g2r_job.sbatch", JOB="G18_Ua", STUB_LIMIT="08:54:00")
            self.assertEqual(r.returncode, 2)
            self.assertIn("not a clean checkout", r.stdout)
        finally:
            (self.deploy / "stray").unlink()

    # --- g2r_envtest.sbatch
    @unittest.skipUnless(HAVE_ROOT, "PyROOT")
    def test_the_envtest_passes_and_refuses_a_rerun(self):
        os.symlink(self.pre, self.o / "deploy-pre")
        r = self.sh("g2r_envtest.sbatch", STUB_LIMIT="01:04:00")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rec = json.loads((self.o / "envtest" / "envtest.json").read_text())
        self.assertEqual(rec["verdict"], "PASS")
        self.assertEqual(len((self.o / "envtest" / "walls.tsv").read_text().splitlines()), 2)
        r = self.sh("g2r_envtest.sbatch", STUB_LIMIT="01:04:00")
        self.assertEqual(r.returncode, 3)

    @unittest.skipUnless(HAVE_ROOT, "PyROOT")
    def test_the_envtest_finds_a_difference_and_a_failed_run(self):
        os.symlink(self.pre, self.o / "deploy-pre")
        other = self.root / "other.root"
        write_product(other, scale=3.0, run_config={"miss_map": None})
        r = self.sh("g2r_envtest.sbatch", STUB_LIMIT="01:04:00", STUB_PRODUCT_POST=str(other))
        self.assertEqual(r.returncode, 5, r.stdout + r.stderr)
        shutil.rmtree(self.o / "envtest")
        r = self.sh("g2r_envtest.sbatch", STUB_LIMIT="01:04:00", STUB_RUN_RC="1")
        self.assertEqual(r.returncode, 6)
        self.assertFalse((self.o / "envtest" / "envtest.json").exists())

    def test_the_envtest_refuses_a_pre_deploy_not_at_pre_m(self):
        os.symlink(self.pre, self.o / "deploy-pre")
        r = self.sh("g2r_envtest.sbatch", STUB_LIMIT="01:04:00", STUB_PRE_M="0" * 40)
        self.assertEqual(r.returncode, 2)
        self.assertIn("deploy-pre is not a clean checkout", r.stdout)

    # --- g2r_prepare.sbatch
    def test_the_prepare_passes_its_rc_through(self):
        for want in (0, 5, 7, 8):
            o = Path(tempfile.mkdtemp(dir=self.root))
            (o / "tables").mkdir()
            gj.tables(o / "tables")
            r = self.sh("g2r_prepare.sbatch", STUB_LIMIT="02:00:00", STUB_PREPARE_RC=str(want), G2R_O=str(o))
            self.assertEqual(r.returncode, want, r.stdout + r.stderr)
            self.assertEqual(json.loads((o / "prepare" / "g2r_prepare.json").read_text())["blocks"], 12)
            self.assertIn("g2r_map.npz", r.stdout)

    def test_the_prepare_refuses(self):
        shutil.rmtree(self.o / "prepare")
        r = self.sh("g2r_prepare.sbatch", STUB_LIMIT="02:00:00", STUB_UNISTAT="FAIL")
        self.assertEqual(r.returncode, 4)
        r = self.sh("g2r_prepare.sbatch", STUB_LIMIT="01:00:00")
        self.assertEqual(r.returncode, 2)
        (self.o / "prepare").mkdir()
        r = self.sh("g2r_prepare.sbatch", STUB_LIMIT="02:00:00")
        self.assertEqual(r.returncode, 3)

    def test_the_preflight_refusals(self):
        env = {k: v for k, v in self.env.items() if k != "M"}
        r = subprocess.run(["bash", str(JOBS / "g2r_job.sbatch")], env={**env, "JOB": "G18_Ua", "STUB_LIMIT": "08:54:00"},
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("C and M must be exported", r.stdout)
        r = self.sh("g2r_job.sbatch", JOB="G18_Ua", STUB_LIMIT="08:54:00", STUB_MATSETUP_RC="1")
        self.assertEqual(r.returncode, 7)
        self.assertIn("not the pinned ones", r.stdout)
        r = self.sh("g2r_job.sbatch", JOB="G18_Ua", STUB_LIMIT="08:54:00", STUB_MATENV_RC="1")
        self.assertEqual(r.returncode, 7)
        self.assertIn("not the pinned MAT environment", r.stdout)
        r = self.sh("g2r_job.sbatch", JOB="G18_Ua", STUB_LIMIT="08:54:00", STUB_QOS="debug")
        self.assertEqual(r.returncode, 2)
        self.assertIn("QOS is not regular", r.stdout)

    def test_the_envtest_stops_on_its_limit_and_its_check(self):
        os.symlink(self.pre, self.o / "deploy-pre")
        r = self.sh("g2r_envtest.sbatch", STUB_LIMIT="00:31:00")
        self.assertEqual(r.returncode, 2)
        self.assertIn("TimeLimit is not 01:04:00", r.stdout)
        r = self.sh("g2r_envtest.sbatch", STUB_LIMIT="01:04:00", STUB_CHECK_FAIL="1")
        self.assertEqual(r.returncode, 4)
        self.assertIn("$MC sha256", r.stdout)
        self.assertFalse((self.o / "envtest").exists())

    def test_the_prepare_refuses_a_dirty_deploy(self):
        shutil.rmtree(self.o / "prepare")
        (self.deploy / "stray").write_text("x")
        try:
            r = self.sh("g2r_prepare.sbatch", STUB_LIMIT="02:00:00")
            self.assertEqual(r.returncode, 2)
            self.assertIn("not a clean checkout", r.stdout)
        finally:
            (self.deploy / "stray").unlink()

    # --- g2r_submit.sh
    def submit(self, job, M=None, **env):
        return self.sh("g2r_submit.sh", str(self.deploy), M or self.M, job, **env)

    def put_record(self, rel, rec):
        p = self.origin / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec))
        self.commit_origin(f"record {rel}")

    def drop_records(self):
        for rel in (gj.ENVTEST_RECORD, gj.PREPARE_RECORD):
            (self.origin / rel).unlink(missing_ok=True)
        self.commit_origin("drop records") if subprocess.run(
            ["git", "-C", str(self.origin), "status", "--porcelain"], capture_output=True, text=True).stdout else None

    def test_the_submission_sequence(self):
        self.addCleanup(self.drop_records)
        stub = self.root / "stub"
        r = self.submit("envtest")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("job=envtest id=1001 limit=01:04:00", (self.o / "submissions.log").read_text())
        self.assertIn("--job-name=cov2dg2r-envtest --time=01:04:00", (stub / "sbatch.log").read_text())
        self.assertIn("g2r_envtest.sbatch", (stub / "sbatch.log").read_text())
        self.assertEqual(self.submit("envtest").returncode, 3)                    # each job once
        self.assertEqual(self.submit("prepare").returncode, 3)                    # no committed envtest PASS
        self.put_record(gj.ENVTEST_RECORD, {"verdict": "PASS"})
        (stub / "sacct.psv").write_text("1001|cov2dg2r-envtest|COMPLETED|2700|1\n")
        r = self.submit("prepare")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.submit("D_Ua").returncode, 3)                       # no committed prepare PASS
        self.put_record(gj.PREPARE_RECORD, {"verdict": "PASS", "map_npz_sha256": "a" * 64})
        (stub / "sacct.psv").write_text("1001|cov2dg2r-envtest|COMPLETED|2700|1\n1002|cov2dg2r-prepare|COMPLETED|3600|1\n")
        r = self.submit("D_Ua")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("MAPSHA=" + "a" * 64, (stub / "sbatch.log").read_text().splitlines()[-1])
        self.assertEqual(self.submit("D_Ub").returncode, 3)                       # D_Ua's first run not done
        (self.o / "walls.D_Ua.1.tsv").write_text("A_2p2h_0\t1\t2\t0\n")
        (self.o / "out" / "A_2p2h_0").mkdir(parents=True)
        (self.o / "out" / "A_2p2h_0" / "xsec.root").write_bytes(b"x")
        (stub / "sacct.psv").write_text("1001|cov2dg2r-envtest|COMPLETED|2700|1\n1002|cov2dg2r-prepare|COMPLETED|10800|1\n"
                                        "1003|cov2dg2r-D_Ua|RUNNING|600|1\n")
        r = self.submit("D_Ub")
        self.assertEqual(r.returncode, 9, r.stdout + r.stderr)                    # the projection passes 110: STOP
        self.assertIn("STOP", r.stdout)
        (stub / "sacct.psv").write_text("1001|cov2dg2r-envtest|COMPLETED|2700|1\n1002|cov2dg2r-prepare|COMPLETED|3600|1\n"
                                        "1003|cov2dg2r-D_Ua|RUNNING|600|1\n")
        self.assertEqual(self.submit("D_Ub").returncode, 0)

    def test_the_submit_refusals(self):
        self.assertEqual(self.sh("g2r_submit.sh", str(self.deploy), self.M).returncode, 2)          # one job per call
        self.assertEqual(self.sh("g2r_submit.sh", str(self.deploy), self.M, "envtest", "prepare").returncode, 2)
        r = self.submit("envtest", M="0" * 40)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.submit("nope").returncode, 2)
        (self.o / "tables" / "jobs_g2r.tsv").write_text("changed\n")
        r = self.submit("envtest")
        self.assertEqual(r.returncode, 2)
        self.assertIn("is not this deploy's", r.stdout)

    def test_the_binding_must_name_m_on_its_m_j1_line(self):
        text = self.bind.read_text()
        self.bind.write_text(f"# binding\n\nthe audited head is `{self.M}`\n")
        self.commit_origin("binding without the M_J1 line")
        try:
            r = self.submit("envtest")
            self.assertEqual(r.returncode, 2)
            self.assertIn("M_J1 line", r.stdout)
        finally:
            self.bind.write_text(text)
            self.commit_origin("binding restored")

    def test_more_submit_refusals(self):
        (self.deploy / "stray").write_text("x")
        try:
            self.assertEqual(self.submit("envtest").returncode, 2)
        finally:
            (self.deploy / "stray").unlink()
        url = subprocess.run(["git", "-C", str(self.deploy), "remote", "get-url", "origin"], capture_output=True,
                             text=True, check=True).stdout.strip()
        subprocess.run(["git", "-C", str(self.deploy), "remote", "set-url", "origin", str(self.root / "nowhere")], check=True)
        try:
            r = self.submit("envtest")
            self.assertEqual(r.returncode, 2)
            self.assertIn("fetch of origin main failed", r.stdout)
        finally:
            subprocess.run(["git", "-C", str(self.deploy), "remote", "set-url", "origin", url], check=True)
        stub = self.root / "stub"
        (stub / "sacct.psv").write_text("9|cov2dg2r-envtest|COMPLETED|%d|1\n" % (3600 * 109))
        r = self.submit("envtest")
        self.assertEqual(r.returncode, 3)                                          # over the cap, not an unfold: refused
        self.assertIn("the gate refuses envtest", r.stdout)
        (stub / "sacct.psv").unlink()
        r = self.submit("envtest", STUB_SBATCH_OUT="sbatch: error: denied")
        self.assertEqual(r.returncode, 2)
        self.assertIn("returned no job id", r.stdout)

    def test_a_missing_binding_is_refused(self):
        text = self.bind.read_text()
        self.bind.unlink()
        self.commit_origin("binding removed")
        try:
            r = self.submit("envtest")
            self.assertEqual(r.returncode, 2)
            self.assertIn("binding 1 is not on origin/main", r.stdout)
        finally:
            self.bind.write_text(text)
            self.commit_origin("binding restored")

    def test_sacct_never_listing_the_id_is_rc_6(self):
        r = self.submit("envtest", STUB_SACCT_LISTS="0")
        self.assertEqual(r.returncode, 6)
        self.assertIn("did not list", r.stdout)


if __name__ == "__main__":
    unittest.main()
