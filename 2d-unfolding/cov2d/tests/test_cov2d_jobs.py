"""cov2d_jobs: the run tables (counts, labels, seeds, data files, part B's packing and limit rule), every generated
argv through re2_driver's REAL parser (PyROOT env), and the job-side input checks on synthetic files.
    cd 2d-unfolding/cov2d/tests && python -B -m unittest -v test_cov2d_jobs
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import shlex
import subprocess
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
               "$ACT": "/x/act", "$D": "/x/d", "$K2A": "/x/d/data_2a.root"}

        class Stop(Exception):
            pass
        seen = []
        real = argparse.ArgumentParser.parse_args

        def capture(self, args=None, namespace=None):
            ns = real(self, args, namespace)
            seen.append(ns)
            raise Stop
        for truth in ("G18", "AR23", "pilot"):
            for r in (cj.pilot()[0] if truth == "pilot" else cj.runs_of(truth)):
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
        self.assertEqual(len(seen), 2 * 786 + 8)


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
    def test_ar23s_jobs_read_the_rerun_directory(self):
        # A2: AR23's pseudo-data rerun writes a new directory; every AR23 unfold reads its data files from there
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            cj.tables("AR23", Path(td) / "tables")
            env = dict(os.environ, C=str(HERE.parents[2]), M="x", TRUTH="AR23", JOB="AR23_L", DRYRUN="1", COV2D_O=td)
            r = subprocess.run(["bash", str(HERE.parent / "jobs" / "cov2d_job.sbatch")], env=env, capture_output=True,
                               text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            lines = [ln for ln in r.stdout.splitlines() if ln.startswith("srun ")]
            self.assertEqual(len(lines), 11)
            self.assertTrue(all(f"--data-file {td}/pseudo/AR23-a2/b/data_5731000.root" in ln for ln in lines))

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


class Pilot(unittest.TestCase):
    def test_eight_runs_three_lanes_and_2a_file(self):
        rows, jobs = cj.pilot()
        self.assertEqual([r["label"] for r in rows], ["P912_L_BeamAngleX_0", "L_G18_BeamAngleX_0", "P912_U_MaRES_0",
                                                       "P2b_ER", "X_G18", "T_G18_5720000", "B_G18_001", "U_G18_Flux_0"])
        cpus = {r["label"]: r["cpus"] for r in rows}
        # each control at its part B reference's CPU count: ER 64 (J1), S3_BeamAngleX0 128 (J3), U_MaRES_0 128 (J2b)
        self.assertEqual((cpus["P2b_ER"], cpus["P912_L_BeamAngleX_0"], cpus["P912_U_MaRES_0"]), (64, 128, 128))
        self.assertEqual(jobs[0]["limit"], "01:41:00")
        self.assertLessEqual(cj.hms(jobs[0]["limit"]), 2 * 3600)
        for r in rows:
            df = r["args"][r["args"].index("--data-file") + 1]
            self.assertEqual(df == "$K2A", r["label"].startswith("P"))
        p2b = next(r for r in rows if r["label"] == "P2b_ER")["args"]
        self.assertEqual(p2b[:-2], cj.argv("central", "x")[:-2])      # E_R's argv (partb_runs.tsv:2)

    def test_dvs_rate_reads_the_same_prefix(self):
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True):
            a, b = Path(td) / "a", Path(td) / "b"
            a.write_bytes(b"x" * 5000)
            b.write_bytes(b"x" * 4000 + b"y" * 1000)
            rec = cj.dvs_rate(str(a), str(b), 4000)
            self.assertEqual((rec["staged"]["bytes"], rec["cfs"]["bytes"]), (4000, 4000))
            self.assertTrue(rec["prefix_equal"])
            self.assertFalse(cj.dvs_rate(str(a), str(b), 4500)["prefix_equal"])
            self.assertIn("staging is complete", rec["declared_departure"])

    def test_pilot_dry_run_reads_g18_data(self):
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            cj.tables("pilot", Path(td) / "tables")
            env = dict(os.environ, C=str(HERE.parents[2]), M="x", TRUTH="pilot", DATA_TRUTH="G18", JOB="pilot",
                       DRYRUN="1", COV2D_O=td)
            r = subprocess.run(["bash", str(HERE.parent / "jobs" / "cov2d_job.sbatch")], env=env, capture_output=True,
                               text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            lines = [ln for ln in r.stdout.splitlines() if ln.startswith("srun ")]
            self.assertEqual(len(lines), 8)
            self.assertEqual(sum("/pscratch/sd/j/josephrb/cov2d-2a/writer_control.root" in ln for ln in lines), 3)
            self.assertEqual(sum(f"{td}/pseudo/G18/b/data_" in ln for ln in lines), 5)


class A2Pseudo(unittest.TestCase):
    """COV2D addendum A2: the pseudo-data limits, the directory map both job scripts use, and the B9-form deletion."""
    def test_limits(self):
        self.assertEqual(cj.PSEUDO_LIMITS, {"G18": "03:00:00", "AR23": "04:00:00"})
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cj.main(["pseudo-limit", "--truth", "AR23"]), 0)
        self.assertEqual(out.getvalue().strip(), "04:00:00")

    def test_pseudo_dir_through_the_real_env_script(self):
        import subprocess
        env = dict(os.environ, C=str(HERE.parents[2]), COV2D_O="/o")
        r = subprocess.run(["bash", "-c", f"source {HERE.parent / 'jobs' / 'cov2d_env.sh'}; pseudo_dir G18; pseudo_dir AR23"],
                           env=env, capture_output=True, text=True)
        self.assertEqual(r.stdout.split(), ["/o/pseudo/G18", "/o/pseudo/AR23-a2"])

    def test_staged_copies_are_deleted_with_b9_rows_unless_their_stat_moved(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            recs = []
            for step, names in (("a", ["uni_u.root", "cv_c.root"]), ("b", ["er_x.root"])):
                staged = {}
                for n in names:
                    f = d / step / "stage" / n
                    f.parent.mkdir(parents=True, exist_ok=True)
                    f.write_bytes(n.encode())
                    st = os.stat(f)
                    staged[n] = {"path": str(f), "sha256": n * 2, "stat": {"size": st.st_size, "mtime": int(st.st_mtime),
                                                                            "inode": st.st_ino}}
                (d / step / "rec.json").write_text(json.dumps({"staged": staged}))
                recs.append(d / step / "rec.json")
            moved = d / "a" / "stage" / "cv_c.root"
            os.utime(moved, (1, 1))                       # its mtime no longer what staging recorded
            kept = cj.delete_staged(recs, d / "deletions.tsv", "step B PASS")
            rows = (d / "deletions.tsv").read_text().splitlines()
            self.assertEqual(rows[0], cj.DELETIONS_HEADER)
            self.assertEqual(kept, 1)
            self.assertTrue(moved.exists())
            self.assertFalse((d / "a" / "stage" / "uni_u.root").exists() or (d / "b" / "stage" / "er_x.root").exists())
            got = {Path(r.split("\t")[1]).name: r.split("\t") for r in rows[1:]}
            self.assertEqual({k: v[6] for k, v in got.items()}, {"uni_u.root": "yes", "cv_c.root": "no", "er_x.root": "yes"})
            self.assertEqual(got["er_x.root"][2], "er_x.rooter_x.root")
            self.assertEqual(got["er_x.root"][7], "step B PASS")


class Order(unittest.TestCase):
    """J1: COV2D-DECLARATION.md:40 and section 10 steps 5-6, enforced at submission. These records are hand-written
    and test the sequence only, with an M that is not a commit: that each writer emits what order() reads is tested on
    the writer's own record (test_cov2d_pseudo_write, test_cov2d_pilot: the final audit's F1)."""
    M = "sequence-test-not-a-commit"

    def rec(self, ok=True, M=None, **kw):
        return {"verdict": "PASS" if ok else "STOP", "M": M or self.M, **kw}

    def committed(self, g18=False, ar23=False, pilot=False):
        return {cj.PSEUDO_RECORD.format(truth="G18"): self.rec() if g18 else None,
                cj.PSEUDO_RECORD.format(truth="AR23"): self.rec() if ar23 else None,
                cj.PILOT_RECORD: self.rec(reprice_classes=[]) if pilot else None}

    def test_the_sequence(self):
        o = cj.order
        self.assertEqual(o("pseudo", "G18", self.committed(), set(), self.M), [])
        self.assertTrue(o("pilot", "pilot", self.committed(), set(), self.M))                 # needs G18's PASS
        self.assertEqual(o("pilot", "pilot", self.committed(g18=True), set(), self.M), [])
        self.assertTrue(o("pseudo", "AR23", self.committed(g18=True), set(), self.M))         # needs the pilot
        self.assertEqual(o("pseudo", "AR23", self.committed(g18=True, pilot=True), set(), self.M), [])
        self.assertTrue(o("G18_Ua", "G18", self.committed(g18=True, pilot=True), set(), self.M))   # needs AR23's too
        self.assertEqual(o("G18_Ua", "G18", self.committed(True, True, True), set(), self.M), [])
        self.assertTrue(o("G18_Ta", "G18", self.committed(True, True, True), {"G18_Ua"}, self.M))  # universes first
        self.assertEqual(o("G18_Ta", "G18", self.committed(True, True, True), set(cj.UNIVERSE_JOBS), self.M), [])

    def test_a_record_for_another_commit_or_not_pass_does_not_count(self):
        c_ = self.committed(True, True, True)
        c_[cj.PILOT_RECORD] = self.rec(M="x" * 40, reprice_classes=[])
        self.assertTrue(cj.order("G18_Ua", "G18", c_, set(), self.M))
        c_[cj.PILOT_RECORD] = self.rec(ok=False, reprice_classes=[])
        self.assertTrue(cj.order("G18_Ua", "G18", c_, set(), self.M))

    def test_a_pilot_needing_repricing_opens_nothing_after_it(self):
        # F2: a PASS with a REPRICE class, or with none recorded, admits no job after the pilot
        for rp in (["universe"], None):
            c_ = self.committed(True, True, True)
            c_[cj.PILOT_RECORD] = self.rec(reprice_classes=rp) if rp else self.rec()
            for job, truth in (("pseudo", "AR23"), ("G18_Ua", "G18"), ("AR23_Ta", "AR23")):
                with self.subTest(rp=rp, job=job):
                    self.assertTrue(any("REPRICE" in x for x in cj.order(job, truth, c_, set(cj.UNIVERSE_JOBS), self.M)))

    def test_gate_refuses_an_unknown_cov2d_job(self):
        with self.assertRaises(c.Refusal):
            cj.gate("1|cov2d-mystery|COMPLETED|100|1\n", {"G18_L": "03:20:00"}, "G18_L")

    def test_uni_stat(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "u"
            p.write_bytes(b"x")
            self.assertIn("part B's DTN record", cj.uni_stat_problem(str(p)))


class SubmitBinding(unittest.TestCase):
    """The director's F3: cov2d_submit.sh reads binding 2 from origin/main, after a fetch, and requires it to name M,
    the deploy's HEAD. Fixture: an "origin" repository whose first commit is the code commit M and whose main carries
    a later commit adding the binding, and a deploy cloned from it and checked out at M. The deploy's
    cov2d_env.sh is a stub that prints a marker and exits, so reaching it means every binding check passed."""
    BIND = "docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-BINDING-2.md"
    OLD_BLOB = "03ad296e3a39be50d654e15b8819e6fa6e910ae6"     # the script as audited (the defect)
    PAST = "PAST-THE-BINDING-CHECKS"

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.d = Path(self.td.name)

    def git(self, *args, cwd=None):
        from deploy_fixture import GIT
        r = subprocess.run(GIT + (["-C", str(cwd)] if cwd else []) + list(args), capture_output=True, text=True,
                           check=True)
        return r.stdout.strip()

    def world(self, names=None, text=None):
        """origin (main: M, then a binding naming ``names`` unless it is None) and the deploy at M; returns M.
        ``text``, if given, maps M to the binding's whole text instead."""
        o = self.d / "origin"
        o.mkdir()
        self.git("init", "-q", str(o))
        self.git("symbolic-ref", "HEAD", "refs/heads/main", cwd=o)
        env = o / "2d-unfolding/cov2d/jobs/cov2d_env.sh"
        env.parent.mkdir(parents=True)
        env.write_text(f"echo {self.PAST}\nexit 0\n")
        self.git("add", ".", cwd=o)
        self.git("commit", "-q", "-m", "code", cwd=o)
        M = self.git("rev-parse", "HEAD", cwd=o)
        if names is not None or text:
            b = o / self.BIND
            b.parent.mkdir(parents=True)
            b.write_text(text(M) if text else
                         f"# COV2D binding 2\n\n**M = `{M if names == 'M' else names}`** (PR head `0123abcd`).\n"
                         + ("" if names == "M" else f"\nThe audited head was `{M}`.\n"))
            self.git("add", ".", cwd=o)
            self.git("commit", "-q", "-m", "binding 2", cwd=o)
        self.git("clone", "-q", str(o), str(self.d / "deploy"))
        self.git("checkout", "-q", "--detach", M, cwd=self.d / "deploy")
        return M

    def submit(self, M, script=None):
        script = script or HERE.parent / "jobs" / "cov2d_submit.sh"
        r = subprocess.run(["bash", str(script), str(self.d / "deploy"), M, "G18", "pseudo"], capture_output=True,
                           text=True)
        return r.returncode, r.stdout + r.stderr

    def test_admits_when_origin_mains_binding_names_M(self):
        M = self.world("M")
        self.assertFalse((self.d / "deploy" / self.BIND).exists())    # the deploy at M cannot hold its own binding
        rc, out = self.submit(M)
        self.assertEqual(rc, 0, out)
        self.assertIn(self.PAST, out)

    def test_refuses_a_binding_naming_another_commit(self):
        M = self.world("f" * 40)
        rc, out = self.submit(M)
        self.assertEqual(rc, 2)
        self.assertIn("does not name", out)
        self.assertNotIn(self.PAST, out)

    def test_refuses_M_cited_only_off_the_M_line(self):
        # world() cites the full M on a later line whenever the M line names another commit
        M = self.world("e" * 40)
        self.assertIn(f"`{M}`", (self.d / "origin" / self.BIND).read_text())
        rc, out = self.submit(M)
        self.assertEqual(rc, 2)
        self.assertIn("does not name", out)
        self.assertNotIn(self.PAST, out)

    def test_binding_1s_own_text_binds_its_M_line_only(self):
        # the format the director's bindings use, from the real COV2D-BINDING-1.md: M on its M line (:5) binds; M
        # cited in backticks off that line (here in place of the declaration's sha256 at :4) does not
        real = (HERE.parents[2] / self.BIND.replace("BINDING-2", "BINDING-1")).read_text()
        m1 = "dec97852f8da840c855777fa3d2179d6548252ee"
        other = "0328c916d2c763c4529d3541fe05f430f7b2e6e4937f7749660cb3da06c6fbb6"
        self.assertIn(f"**M = `{m1}`**", real)
        self.assertIn(other, real)
        M = self.world(text=lambda M: real.replace(m1, M))
        rc, out = self.submit(M)
        self.assertEqual(rc, 0, out)
        self.td.cleanup()
        self.td = tempfile.TemporaryDirectory()
        self.d = Path(self.td.name)
        M = self.world(text=lambda M: real.replace(other, M))
        rc, out = self.submit(M)
        self.assertEqual(rc, 2)
        self.assertIn("does not name", out)

    def test_refuses_when_origin_main_has_no_binding(self):
        M = self.world(None)
        rc, out = self.submit(M)
        self.assertEqual(rc, 2)
        self.assertIn("binding 2 is not on origin/main", out)

    def test_refuses_a_failed_fetch_even_with_a_good_binding_already_fetched(self):
        M = self.world("M")                     # the clone's origin/main already holds a binding naming M
        self.git("remote", "set-url", "origin", str(self.d / "nowhere"), cwd=self.d / "deploy")
        rc, out = self.submit(M)
        self.assertEqual(rc, 2)
        self.assertIn("the fetch of origin main failed", out)
        self.assertNotIn(self.PAST, out)

    def test_refuses_a_dirty_deploy_or_a_head_other_than_M(self):
        M = self.world("M")
        rc, out = self.submit("f" * 40)
        self.assertEqual(rc, 2)
        self.assertIn("is not a clean checkout", out)
        (self.d / "deploy" / "untracked").write_text("x")
        rc, out = self.submit(M)
        self.assertEqual(rc, 2)
        self.assertIn("is not a clean checkout", out)

    def test_the_audited_script_refuses_even_the_correct_setup(self):
        # the test reaches the defect: blob 03ad296e grepped the deploy's own tree, which never holds a binding naming
        # its own HEAD, so it refused every submission
        old = self.d / "old_submit.sh"
        old.write_text(subprocess.run(["git", "-C", str(HERE), "cat-file", "-p", self.OLD_BLOB], capture_output=True,
                                      text=True, check=True).stdout)
        M = self.world("M")
        rc, out = self.submit(M, old)
        self.assertEqual(rc, 2)
        self.assertIn("binding 2 does not name", out)
        self.assertNotIn(self.PAST, out)


class LaneWalls(unittest.TestCase):
    """J3: the script's own lane(), with srun stubbed to fail only the first run: each run keeps its own rc."""
    def test_each_run_records_its_own_rc(self):
        import subprocess
        script = (HERE.parent / "jobs" / "cov2d_job.sbatch").read_text()
        lane = script[script.index("lane() {"):script.index("pids=\"\"")]
        with tempfile.TemporaryDirectory() as td:
            runs = Path(td) / "runs.tsv"
            runs.write_text("job\tlane\tlabel\tcpus\tscript\targs\test_s\n"
                            + "".join(f"J\tJ.1\tr{i}\t4\tre2\t--x {i}\t1\n" for i in (1, 2, 3)))
            harness = f"""
O={td}; JOB=J; RUNS={runs}; C={td}; mkdir -p "$O/logs" "$O/out" "$O/inventory"
command -v sha256sum > /dev/null || sha256sum() {{ shasum -a 256 "$@"; }}   # macOS lacks sha256sum
srun() {{ local out; while [ $# -gt 0 ]; do [ "$1" = --out ] && out=$2; [ "$1" = --job-name=r1 ] && return 1; shift; done
         mkdir -p "$(dirname "$out")"; echo x > "$out"; }}
{lane}
lane J.1
"""
            subprocess.run(["bash", "-c", harness], capture_output=True, text=True)
            walls = [ln.split("\t") for ln in (Path(td) / "walls.J.1.tsv").read_text().splitlines()]
            self.assertEqual([(w[0], w[3]) for w in walls], [("r1", "1"), ("r2", "0"), ("r3", "0")])


if __name__ == "__main__":
    unittest.main()
