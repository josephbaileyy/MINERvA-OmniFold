#!/usr/bin/env python3
"""Tests for ``ibub_unit.py`` (IBUB-DECLARATION.md sections 3, 5 and 8). Each mechanism fires on its defect and stays
silent on the clean case.

**Config (pure, against the real config.json):**
- E_R's argv equals REF-C2C1's and COV2D's toy argv;
- the thread environment equals cov2d_env.sh's four variables;
- every pin equals the record it is taken from: the declaration, the code, the reference marker, `$K2A`,
  pseudo_b and the blocks;
- C-G2R's forbidden set is exactly the set of options G2R amendment 1 added. It is read from both blobs, the toys' blob
  being checked by its sha256 first.

**Pure:**
- the unit parser;
- C-G2R in both spellings;
- the comparison behind C-REP;
- `stage` and `preflight` on temporary inputs;
- `refcheck`, the barrier, on synthetic markers.

**The driver:** E_R's real driver, in-process, on RE-2's own synthetic omnifile (`test_re2_driver.write_fixture`),
with two OmniFold iterations, as `test_ref_c2c1` runs it:
- `central`, `central_df` (whose data file holds the omnifile's own data tree, as `$K2A` holds `$CV`'s) and a toy
  (other data) all pass every control;
- `central_df` equals `central`, and the toy differs from it;
- the data copy is deleted;
- a data file off its pin is refused with no products;
- a perturbed reference fails C-REP;
- `--miss-map` is refused before the driver runs;
- another CPU count or NUMEXPR value is refused.

Needs PyROOT, numpy, LightGBM and scikit-learn. IBU runs through `ref_c2c1.dagostini` here; RooUnfold's equality to it
is REF-C2C1's C-ROO test. Run it pinned, as RE-2's suite says.
    cd 2d-unfolding/ibub && python -B -m unittest -v test_ibub_unit
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "2d-unfolding" / "re2" / "tests"))
sys.path.insert(0, str(REPO / "2d-unfolding" / "cov2d" / "jobs"))
import ibub_unit as iu  # noqa: E402
rc, c = iu.rc, iu.c

try:
    import lightgbm  # noqa: F401
    import ROOT  # noqa: F401
    HAVE_DRIVER = True
except Exception:  # pragma: no cover
    HAVE_DRIVER = False

# macOS has no O_NOATIME; substitute an inert flag, as test_ref_c2c1 does (the code refuses where it is absent)
NOATIME_SUB = mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True)
NOATIME_SUB.start()
REAL = iu.load_config()
HEAD = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
BOUND = {"job": "61900001", "deploy_head": HEAD}
ENV = {"SLURM_JOB_ID": BOUND["job"], "IBUB_M": HEAD}     # what the job exports for every unit
SRUN_OK = {"central": 0, "central_df": 0}                # each reference srun step's status, as the job waited for it


def write_unit_products(d: Path, name: str, kind: str, *, job=None, deploy=None, verdict="PASS", arrays=None,
                        meta_unit=None):
    """A unit's products as run_unit writes them: an npz whose meta names the unit, kind, job and deploy; the root;
    and the marker with both digests."""
    job, deploy = job or BOUND["job"], deploy or BOUND["deploy_head"]
    arrays = arrays if arrays is not None else {"ks": np.array([5, 10]), "xsec": np.ones((2, 224)), "T": np.ones(224),
                                                 "y": np.ones(224)}
    meta = {"unit": meta_unit or name, "kind": kind, "slurm_job": job, "deploy_head": deploy}
    np.savez(d / f"{name}.npz", **arrays, meta=json.dumps(meta))
    (d / f"{name}.root").write_bytes(name.encode() + b"-root")
    (d / f"{name}.done").write_text(json.dumps({"unit": name, "kind": kind, "verdict": verdict, "job": job,
                                                "deploy_head": deploy, "sha256": rc.sha256(d / f"{name}.npz"),
                                                "root_sha256": rc.sha256(d / f"{name}.root")}))


def gnu_time_file(path: Path, wall: str = "3:36.74", status: int = 0) -> Path:
    path.write_text(f"\tElapsed (wall clock) time (h:mm:ss or m:ss): {wall}\n\tExit status: {status}\n")
    return path
TOY_BLOB_SHA256 = "938c53c5a018d20f5b148f6bdc2949e987a60085c5d0b7913ccdd5bb438b5a3b"   # score records' code.driverSha256
COV2D_M = "a60547692df5f963e428cdfe4661fc51ab785b7b"   # COV2D's bulk deploy (receipts-cov2d/a2/bulk/README.md)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def options(src: str) -> set:
    return set(re.findall(r"add_argument\(\s*\"(--[a-z0-9-]+)\"", src))


class Config(unittest.TestCase):
    def test_argv_is_e_rs_and_cov2ds_toy_argv(self):
        ref = json.loads((REPO / "2d-unfolding/ref_c2c1/config.json").read_text())
        self.assertEqual(REAL["e_r"]["argv"], ref["e_r"]["argv"])
        import cov2d_jobs
        toy = cov2d_jobs.argv("toy", "DATA")
        self.assertEqual(toy[-2:], ["--data-file", "DATA"])
        self.assertEqual(REAL["e_r"]["argv"], toy[:-2])
        self.assertEqual(REAL["e_r"]["cpus"], 64)

    def test_thread_environment_is_cov2d_envs(self):
        text = (REPO / "2d-unfolding/cov2d/jobs/cov2d_env.sh").read_text()
        line = next(ln for ln in text.splitlines() if "OMP_NUM_THREADS=" in ln and ln.strip().startswith("export"))
        env = dict(t.split("=", 1) for t in line.split("#")[0].split()[1:])
        self.assertEqual(REAL["e_r"]["thread_env"], env)

    def test_every_pin_equals_its_record(self):
        iu.check_code(REAL)
        self.assertEqual(REAL["declaration_sha256"], rc.sha256(REPO / REAL["declaration"]))
        marker = json.loads((REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/"
                             "receipts-ref-c2c1/step2/units-centrals/c2_central.done").read_text())
        self.assertEqual(REAL["refs"]["c2_central"]["sha256"], marker["sha256"])
        import cov2d_jobs
        self.assertEqual(REAL["refs"]["k2a"]["sha256"], cov2d_jobs.PINS["$K2A"])
        self.assertEqual(REAL["refs"]["k2a"]["path"], "/pscratch/sd/j/josephrb/cov2d-2a/writer_control.root")
        ref = json.loads((REPO / "2d-unfolding/ref_c2c1/config.json").read_text())["inputs"]
        self.assertEqual({k: REAL["inputs"][k] for k in ("CV_source", "CV_sha256", "MC_source", "MC_sha256")},
                         {k: ref[k] for k in ("CV_source", "CV_sha256", "MC_source", "MC_sha256")})
        self.assertEqual((REAL["inputs"]["lib_source"], REAL["inputs"]["lib_sha256"]),
                         (ref["roounfold_lib"], ref["roounfold_lib_sha256"]))
        for t in ("G18", "AR23"):
            self.assertEqual(len(iu.toy_shas(REAL, t)), 300)
            r = REAL["cov2d_records"][t]
            self.assertEqual(r["blocks_sha256"], rc.sha256(REPO / r["blocks"]))
            self.assertEqual(r["score_sha256"], rc.sha256(REPO / r["score"]))
            null = json.loads((REPO / r["blocks"]).with_name(f"null_{t}.json").read_text())
            self.assertEqual(r["truth_xsec_sha256"], null["inventory"]["truth_xsec_npz"]["sha256"])
            score = json.loads((REPO / r["score"]).read_text())
            self.assertEqual(score["code"]["driverSha256"], TOY_BLOB_SHA256)   # the toys' OmniFold blob (section 3)
        self.assertEqual(int(iu.reported_cells(REAL).sum()), 205)
        self.assertEqual(REAL["toys"]["AR23"]["dir"], "/pscratch/sd/j/josephrb/cov2d-run-20261104/pseudo/AR23-a2/b")

    def test_g2r_forbidden_set_is_exactly_the_amendments_new_options(self):
        try:
            old = subprocess.run(["git", "-C", str(REPO), "show", f"{COV2D_M}:2d-unfolding/re2/re2_driver.py"],
                                 capture_output=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("no git checkout with COV2D's deploy commit")
        self.assertEqual(sha(old), TOY_BLOB_SHA256)          # the blob the toys ran
        new = (REPO / "2d-unfolding/re2/re2_driver.py").read_text()
        self.assertEqual(sha(new.encode()), REAL["code_sha256"]["2d-unfolding/re2/re2_driver.py"])
        self.assertEqual(options(new) - options(old.decode()), set(REAL["g2r_forbidden_options"]))
        self.assertEqual(options(old.decode()) - options(new), set())


class Pure(unittest.TestCase):
    def test_parse_unit(self):
        self.assertEqual(iu.parse_unit("central")["name"], "central")
        self.assertEqual(iu.parse_unit("central_df")["kind"], "central_df")
        self.assertEqual(iu.parse_unit("toy:G18:5720299"),
                         {"kind": "toy", "name": "toy_G18_5720299", "tune": "G18", "seed": 5720299})
        for bad in ("toy:G18:5720300", "toy:AR23:5720000", "toy:X:1", "er", "c2_central", "toy:G18"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                iu.parse_unit(bad)

    def test_c_g2r_refuses_the_amendments_option_in_either_spelling(self):
        cfg = copy.deepcopy(REAL)
        iu.resolve_argv(cfg, None)
        self.assertEqual(iu.resolve_argv(cfg, Path("/x/d.root"))[-2:], ["--data-file", "/x/d.root"])
        for extra in (["--miss-map", "m.npz"], ["--miss-map=m.npz"]):
            bad = copy.deepcopy(cfg)
            bad["e_r"]["argv"] = cfg["e_r"]["argv"] + extra
            with self.subTest(extra=extra), self.assertRaises(iu.GateFailure):
                iu.resolve_argv(bad, None)

    def test_compare_is_on_the_205_cells_and_every_k(self):
        rep = iu.reported_cells(REAL)
        rng = np.random.default_rng(2)
        a = {"ks": np.array([5, 10]), "xsec": rng.uniform(1, 2, (2, 224)), "T": rng.uniform(1, 2, 224),
             "y": rng.uniform(1, 2, 224)}
        self.assertTrue(iu.compare(a, copy.deepcopy(a), rep, 1e-8)["pass"])
        for key, idx in (("xsec", (0, int(np.flatnonzero(rep)[0]))), ("T", 3), ("y", 7)):
            b = copy.deepcopy(a)
            b[key][idx] *= 1 + 1e-6
            with self.subTest(key=key):
                self.assertFalse(iu.compare(a, b, rep, 1e-8)["pass"])
        b = copy.deepcopy(a)
        b["xsec"][1, int(np.flatnonzero(~rep)[0])] *= 2          # an unreported cell is not compared
        self.assertTrue(iu.compare(a, b, rep, 1e-8)["pass"])
        b = copy.deepcopy(a)
        b["ks"] = np.array([5, 20])
        self.assertFalse(iu.compare(a, b, rep, 1e-8)["pass"])
        self.assertEqual(iu.max_rel(np.array([1.0, 0.0]), np.array([1.0, 0.0])), 0.0)
        self.assertEqual(iu.max_rel(np.array([1.0, 1e-30]), np.array([1.0, 0.0])), float("inf"))

    def tmp(self) -> Path:
        d = Path(tempfile.mkdtemp()).resolve()                # the namespace check compares real paths
        self.addCleanup(shutil.rmtree, d, True)
        return d

    def test_stage_copies_checks_and_makes_read_only(self):
        d = self.tmp()
        cfg = copy.deepcopy(REAL)
        cfg["namespace"] = str(d)
        cfg["staging"]["root"] = str(d / "stage")
        for k in ("CV", "MC", "lib"):
            (d / f"src_{k}").write_bytes(f"bytes of {k}".encode())
            cfg["inputs"][f"{k}_source"] = str(d / f"src_{k}")
            cfg["inputs"][f"{k}_sha256"] = sha(f"bytes of {k}".encode())
        self.assertEqual(iu.stage(cfg), 0)
        for k, p in iu.staged(cfg).items():
            self.assertEqual(p.read_bytes(), f"bytes of {k}".encode())
            self.assertFalse(os.stat(p).st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
        self.assertEqual(json.loads((d / "stage" / "stage.json").read_text())["verdict"], "PASS")
        self.assertEqual(iu.check_inputs(cfg), {k: cfg["inputs"][f"{k}_sha256"] for k in ("CV", "MC", "lib")})
        out = copy.deepcopy(cfg)                              # a staging root outside the namespace is refused
        out["staging"]["root"] = str(d.parent / (d.name + "-elsewhere") / "stage")
        with self.assertRaises(iu.GateFailure):
            iu.stage(out)
        self.assertFalse(Path(out["staging"]["root"]).exists())
        bad = copy.deepcopy(cfg)
        bad["staging"]["root"] = str(d / "stage2")
        bad["inputs"]["MC_sha256"] = "0" * 64
        self.assertEqual(iu.stage(bad), iu.RC_GATE)
        self.assertFalse(iu.staged(bad)["MC"].exists())        # a copy off its pin is deleted
        with self.assertRaises((iu.GateFailure, OSError)):     # main() refuses either, with RC_GATE
            iu.check_inputs(bad)

    def preflight_tree(self):
        d = self.tmp()
        cfg = copy.deepcopy(REAL)
        for k in ("c2_central", "k2a"):
            (d / k).write_bytes(k.encode())
            cfg["refs"][k].update(path=str(d / k), sha256=sha(k.encode()))
        for t in ("G18", "AR23"):
            files = [{"seed": s, "role": "toy", "sha256": "0" * 64, "path": str(d / t / f"data_{s}.root")}
                     for s in c.TOY_SEEDS[t]]
            (d / t).mkdir()
            for f in files:
                Path(f["path"]).write_bytes(b"x")
            raw = json.dumps({"verdict": "PASS", "files": files}).encode()
            (d / f"pb_{t}.json").write_bytes(raw)
            cfg["toys"][t].update(dir=str(d / t), pseudo_b=str(d / f"pb_{t}.json"), pseudo_b_sha256=sha(raw))
        return d, cfg

    def test_preflight_checks_both_references_and_the_600_files(self):
        d, cfg = self.preflight_tree()
        self.assertEqual(iu.preflight(cfg), 0)
        (d / "AR23" / "data_5730123.root").unlink()
        self.assertEqual(iu.preflight(cfg), iu.RC_STOP)
        d, cfg = self.preflight_tree()
        (d / "k2a").write_bytes(b"other")
        self.assertEqual(iu.preflight(cfg), iu.RC_STOP)
        d, cfg = self.preflight_tree()
        (d / "c2_central").unlink()
        self.assertEqual(iu.preflight(cfg), iu.RC_STOP)

    def test_toy_shas_refuses_a_record_off_its_pin_or_short_of_a_seed(self):
        d, cfg = self.preflight_tree()
        self.assertEqual(len(iu.toy_shas(cfg, "G18")), 300)
        bad = copy.deepcopy(cfg)
        bad["toys"]["G18"]["pseudo_b_sha256"] = "0" * 64
        with self.assertRaises(iu.GateFailure):
            iu.toy_shas(bad, "G18")
        rec = json.loads((d / "pb_G18.json").read_text())
        rec["files"] = rec["files"][:-1]
        raw = json.dumps(rec).encode()
        (d / "pb_G18.json").write_bytes(raw)
        cfg["toys"]["G18"]["pseudo_b_sha256"] = sha(raw)
        with self.assertRaises(iu.GateFailure):
            iu.toy_shas(cfg, "G18")

    def refs(self, d: Path, *, df_verdict="PASS", walls=("3:20.00", "3:30.00"), status=(0, 0), df_scale=1.0,
             job=BOUND["job"]):
        """Two reference units in d, and each one's srun-step /usr/bin/time file; returns (rep, times)."""
        rep = iu.reported_cells(REAL)
        rng = np.random.default_rng(5)
        base = {"ks": np.array([5, 10]), "xsec": rng.uniform(1, 2, (2, 224)), "T": rng.uniform(1, 2, 224),
                "y": rng.uniform(1, 2, 224)}
        times = {}
        for i, (u, v, scale) in enumerate((("central", "PASS", 1.0), ("central_df", df_verdict, df_scale))):
            write_unit_products(d, u, u, job=job, verdict=v, arrays=dict(base, xsec=base["xsec"] * scale))
            times[u] = gnu_time_file(d / f"{u}.time", walls[i], status[i])
        return rep, times

    def test_refcheck_is_the_barrier(self):
        d = self.tmp()
        rep, times = self.refs(d)
        self.assertEqual(iu.refcheck(dict(REAL, namespace=str(d)), d, rep, BOUND, times, SRUN_OK), 0)
        self.assertEqual(json.loads((d / "refcheck.json").read_text())["verdict"], "PASS")
        rec = json.loads((d / "refcheck.json").read_text())
        self.assertEqual((rec["job"], rec["deploy_head"]), (BOUND["job"], BOUND["deploy_head"]))   # the receipt's binding
        self.assertEqual(rec["units"]["central"]["npz_sha256"], rc.sha256(d / "central.npz"))      # it records the digests
        # the codex read r2, item 2: GNU time reads 0 but the enclosing srun step failed: no barrier
        for u in iu.REFERENCE_UNITS:
            d2 = self.tmp()
            rep2, times2 = self.refs(d2)
            with self.subTest(srun_failed=u):
                self.assertEqual(iu.refcheck(dict(REAL, namespace=str(d2)), d2, rep2, BOUND, times2, {**SRUN_OK, u: 1}), iu.RC_STOP)
                self.assertFalse(json.loads((d2 / "refcheck.json").read_text())["units"][u]["pass"])
        d2 = self.tmp()                                           # a planted refcheck.json is never replaced
        rep2, times2 = self.refs(d2)
        (d2 / "refcheck.json").symlink_to(d2 / "elsewhere.json")
        with self.assertRaises(OSError):
            iu.refcheck(dict(REAL, namespace=str(d2)), d2, rep2, BOUND, times2, SRUN_OK)
        self.assertFalse((d2 / "elsewhere.json").exists())
        self.assertEqual(rec["units"]["central"]["step_wall_s"], 200.0)       # the full step's wall, from time -v
        cases = {"df_failed": dict(df_verdict="FAIL"), "df_differs": dict(df_scale=1 + 1e-6),
                 # the codex read, blocker 3: the re-price trigger reads the full srun step's wall time
                 "slow step": dict(walls=("3:20.00", "4:31.26")), "step failed": dict(status=(0, 1)),
                 # blocker 4: references from another job are never accepted
                 "another job": dict(job="61800000")}
        for tag, kw in cases.items():
            d = self.tmp()
            rep, times = self.refs(d, **kw)
            with self.subTest(case=tag):
                self.assertEqual(iu.refcheck(dict(REAL, namespace=str(d)), d, rep, BOUND, times, SRUN_OK), iu.RC_STOP)
        d = self.tmp()
        rep, times = self.refs(d)
        np.savez(d / "central.npz", ks=np.array([5, 10]))        # bytes off the marker's digest
        self.assertEqual(iu.refcheck(dict(REAL, namespace=str(d)), d, rep, BOUND, times, SRUN_OK), iu.RC_STOP)
        d = self.tmp()
        rep, times = self.refs(d)
        (d / "central_df.done").unlink()
        self.assertEqual(iu.refcheck(dict(REAL, namespace=str(d)), d, rep, BOUND, times, SRUN_OK), iu.RC_STOP)
        d = self.tmp()                                            # the agy code read 2, finding 6: the root's digest too
        rep, times = self.refs(d)
        (d / "central.root").write_bytes(b"other")
        self.assertEqual(iu.refcheck(dict(REAL, namespace=str(d)), d, rep, BOUND, times, SRUN_OK), iu.RC_STOP)
        d = self.tmp()                                            # a reference step with no time record
        rep, times = self.refs(d)
        del times["central_df"]
        self.assertEqual(iu.refcheck(dict(REAL, namespace=str(d)), d, rep, BOUND, times, SRUN_OK), iu.RC_STOP)
        for bad in ("", '{"verdict": "PA', '"PASS"'):          # finding 4: a malformed marker is never PASS
            d = self.tmp()
            rep, times = self.refs(d)
            (d / "central.done").write_text(bad)
            with self.subTest(marker=bad):
                self.assertEqual(iu.refcheck(dict(REAL, namespace=str(d)), d, rep, BOUND, times, SRUN_OK), iu.RC_STOP)
        d = self.tmp()                                            # a marker naming the other reference
        rep, times = self.refs(d)
        m = json.loads((d / "central.done").read_text())
        (d / "central.done").write_text(json.dumps(dict(m, unit="central_df")))
        self.assertEqual(iu.refcheck(dict(REAL, namespace=str(d)), d, rep, BOUND, times, SRUN_OK), iu.RC_STOP)


class Hardening(unittest.TestCase):
    """The codex read's blockers 2-6 and 8, each as a test."""

    def tmp(self) -> Path:
        d = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, d, True)
        return d

    def test_gnu_time_reads_the_full_steps_wall_and_status(self):
        d = self.tmp()
        self.assertEqual(iu.gnu_time(gnu_time_file(d / "a", "3:36.74")), {"wall_s": 216.74, "exit_status": 0})
        self.assertEqual(iu.gnu_time(gnu_time_file(d / "b", "1:02:03.5", 6)), {"wall_s": 3723.5, "exit_status": 6})
        (d / "c").write_text("garbage")
        self.assertEqual(iu.gnu_time(d / "c"), {"wall_s": None, "exit_status": None})
        self.assertEqual(iu.gnu_time(d / "absent"), {"wall_s": None, "exit_status": None})

    def test_a_nonfinite_value_never_passes_a_comparison(self):
        """Blocker 6: a NaN in a later K, in T or in y, and a NaN or inf anywhere in C-ROO's or C-FILL's operands."""
        rep = iu.reported_cells(REAL)
        rng = np.random.default_rng(3)
        a = {"ks": np.array([5, 10, 15]), "xsec": rng.uniform(1, 2, (3, 224)), "T": rng.uniform(1, 2, 224),
             "y": rng.uniform(1, 2, 224)}
        g = int(np.flatnonzero(rep)[4])
        for key, idx in (("xsec", (2, g)), ("T", 5), ("y", 9)):
            for bad in (np.nan, np.inf):
                b = copy.deepcopy(a)
                b[key][idx] = bad
                with self.subTest(key=key, value=bad):
                    got = iu.compare(a, b, rep, 1e-8)
                    self.assertFalse(got["pass"])
                    self.assertEqual(max(got["xsec_max_rel"], got["T_max_rel"], got["y_max_rel"]), float("inf"))
        x = np.ones(4)
        self.assertEqual(iu.max_abs_rel(np.array([1, np.nan, 1, 1.0]), x), float("inf"))
        self.assertEqual(iu.max_abs_rel(x, np.array([1, 1, np.inf, 1.0])), float("inf"))
        self.assertEqual(iu.max_rel(np.array([1, 1, np.nan, 1.0]), x), float("inf"))
        self.assertEqual(iu.max_abs_rel(x, x), 0.0)

    def test_binding_needs_this_job_and_the_deploy_head(self):
        with mock.patch.dict(os.environ, ENV):
            self.assertEqual(iu.binding(), BOUND)
        for env in ({"IBUB_M": "0" * 40}, {"SLURM_JOB_ID": ""}, {"SLURM_JOB_ID": "12a"}, {"IBUB_M": "HEAD"}):
            with self.subTest(env=env), mock.patch.dict(os.environ, {**ENV, **env}), self.assertRaises(iu.GateFailure):
                iu.binding()

    def test_inside_refuses_a_path_or_symlink_out_of_the_namespace(self):
        d = self.tmp()
        cfg = dict(copy.deepcopy(REAL), namespace=str(d / "ns"))
        (d / "ns" / "units").mkdir(parents=True)
        (d / "other").mkdir()
        self.assertEqual(iu.inside(cfg, d / "ns" / "units"), d / "ns" / "units")
        (d / "ns" / "link").symlink_to(d / "other")
        for bad in (d / "other", d / "ns" / "link", d / "ns" / ".." / "other"):
            with self.subTest(path=bad), self.assertRaises(iu.GateFailure):
                iu.inside(cfg, bad)
        (d / "alias").symlink_to(d / "ns")                    # the namespace itself may not be a symlink
        with self.assertRaises(iu.GateFailure):
            iu.inside(dict(cfg, namespace=str(d / "alias")), d / "alias" / "units")

    def complete_tree(self, d: Path, *, job=BOUND["job"]):
        """600 toy units, the two references and their barrier receipt, all this job's (as run_unit and refcheck
        write them)."""
        for t in ("G18", "AR23"):
            for s_ in c.TOY_SEEDS[t]:
                write_unit_products(d, f"toy_{t}_{s_}", "toy", job=job)
        units = {}
        for u in iu.REFERENCE_UNITS:
            write_unit_products(d, u, u, job=job)
            units[u] = {"pass": True, "srun_rc": 0, "npz_sha256": rc.sha256(d / f"{u}.npz"),
                        "root_sha256": rc.sha256(d / f"{u}.root")}
        (d / "refcheck.json").write_text(json.dumps({"verdict": "PASS", "job": job, "deploy_head": BOUND["deploy_head"],
                                                     "units": units}))

    def test_complete_checks_the_exact_marker_set_and_its_binding(self):
        d = self.tmp()
        self.complete_tree(d)
        self.assertEqual(iu.complete(REAL, d, BOUND), 0)
        cases = {
            "a missing marker": lambda d: (d / "toy_AR23_5730100.done").unlink(),
            "a FAIL marker": lambda d: (d / "toy_G18_5720003.done").write_text(json.dumps(
                dict(json.loads((d / "toy_G18_5720003.done").read_text()), verdict="FAIL"))),
            "another job's marker": lambda d: (d / "toy_G18_5720004.done").write_text(json.dumps(
                dict(json.loads((d / "toy_G18_5720004.done").read_text()), job="61800000"))),
            "a product off its digest": lambda d: (d / "toy_G18_5720005.npz").write_bytes(b"other"),
            "an undeclared marker": lambda d: (d / "toy_G18_9999999.done").write_text("{}"),
            "no barrier receipt": lambda d: (d / "refcheck.json").unlink(),
            "another job's barrier": lambda d: (d / "refcheck.json").write_text(json.dumps(
                dict(json.loads((d / "refcheck.json").read_text()), job="61800000"))),
            # the codex read r2, item 2: a PASS barrier must carry two passing references at their current digests
            "a barrier whose reference failed": lambda d: (d / "refcheck.json").write_text(json.dumps(
                dict(json.loads((d / "refcheck.json").read_text()), units={
                    **json.loads((d / "refcheck.json").read_text())["units"],
                    "central_df": {**json.loads((d / "refcheck.json").read_text())["units"]["central_df"], "pass": False}}))),
            "a reference changed after the barrier": lambda d: write_unit_products(
                d, "central", "central", arrays={"ks": np.array([5]), "xsec": np.ones((1, 224)), "T": np.ones(224),
                                                 "y": np.ones(224)}),
            "a toy whose npz meta names another unit": lambda d: write_unit_products(
                d, "toy_G18_5720009", "toy", meta_unit="toy_G18_5720010"),
            "a toy whose products are gone": lambda d: [(d / "toy_AR23_5730001.npz").unlink(),
                                                         (d / "toy_AR23_5730001.root").unlink()],
            "a symlinked barrier": lambda d: [(d / "refcheck.json").rename(d / "rc.json"),
                                              (d / "refcheck.json").symlink_to(d / "rc.json")],
            "a barrier that is not JSON": lambda d: (d / "refcheck.json").write_text("{not json"),
            "a barrier that is not an object": lambda d: (d / "refcheck.json").write_text('["PASS"]'),
        }
        for tag, defect in cases.items():
            d = self.tmp()
            self.complete_tree(d)
            defect(d)
            with self.subTest(case=tag):
                self.assertEqual(iu.complete(REAL, d, BOUND), 1)


class Refusals(unittest.TestCase):
    """Each refusal of the gates fires on its defect (the line trace's uncovered branches)."""

    def tmp(self) -> Path:
        d = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, d, True)
        return d

    def test_check_code_refuses_a_changed_file(self):
        cfg = copy.deepcopy(REAL)
        cfg["code_sha256"]["2d-unfolding/ref_c2c1/ref_c2c1.py"] = "0" * 64
        with self.assertRaises(iu.GateFailure):
            iu.check_code(cfg)

    def test_check_inputs_refuses_outside_the_root_and_off_its_pin(self):
        d = self.tmp()
        cfg = copy.deepcopy(REAL)
        cfg["staging"]["root"] = str(d / "stage")
        (d / "stage").mkdir()
        (d / "elsewhere").write_bytes(b"x")
        for k in ("CV", "MC", "lib"):
            (d / "stage" / k).write_bytes(k.encode())
            cfg["staging"][k] = k
            cfg["inputs"][f"{k}_sha256"] = sha(k.encode())
        self.assertEqual(set(iu.check_inputs(cfg)), {"CV", "MC", "lib"})
        out = copy.deepcopy(cfg)
        out["staging"]["MC"] = "../elsewhere"
        with self.assertRaises(iu.GateFailure):
            iu.check_inputs(out)
        pin = copy.deepcopy(cfg)
        pin["inputs"]["lib_sha256"] = "0" * 64
        with self.assertRaises(iu.GateFailure):
            iu.check_inputs(pin)

    def pb(self, d: Path, rec: dict) -> dict:
        raw = json.dumps(rec).encode()
        (d / "pb.json").write_bytes(raw)
        cfg = copy.deepcopy(REAL)
        cfg["toys"]["G18"].update(dir=str(d), pseudo_b=str(d / "pb.json"), pseudo_b_sha256=sha(raw))
        return cfg

    def test_toy_shas_refuses_a_failed_record_and_a_file_outside_its_directory(self):
        d = self.tmp()
        files = [{"seed": s, "role": "toy", "sha256": "0" * 64, "path": str(d / f"data_{s}.root")}
                 for s in c.TOY_SEEDS["G18"]]
        self.assertEqual(len(iu.toy_shas(self.pb(d, {"verdict": "PASS", "files": files}), "G18")), 300)
        with self.assertRaises(iu.GateFailure):
            iu.toy_shas(self.pb(d, {"verdict": "STOP", "files": files}), "G18")
        moved = copy.deepcopy(files)
        moved[10]["path"] = str(d / "other" / Path(moved[10]["path"]).name)
        with self.assertRaises(iu.GateFailure):
            iu.toy_shas(self.pb(d, {"verdict": "PASS", "files": moved}), "G18")

    def test_reported_cells_refuses_a_record_off_its_pin_or_of_another_shape(self):
        d = self.tmp()
        cfg = copy.deepcopy(REAL)
        cfg["cells"]["blocks_sha256"] = "0" * 64
        with self.assertRaises(iu.GateFailure):
            iu.reported_cells(cfg)
        np.savez(d / "b.npz", rep=np.ones(224, bool))
        cfg["cells"].update(blocks=str(d / "b.npz"), blocks_sha256=rc.sha256(d / "b.npz"))
        with self.assertRaises(iu.GateFailure):
            iu.reported_cells(cfg)

    def test_a_failed_data_copy_leaves_nothing_behind(self):
        d = self.tmp()
        cfg = copy.deepcopy(REAL)
        cfg["namespace"] = str(d)
        cfg["staging"]["root"] = str(d / "stage")
        cfg["refs"]["k2a"].update(path=str(d / "k2a.root"), sha256=sha(b"k2a"))
        (d / "k2a.root").write_bytes(b"k2a")

        def partial(src, dest):          # writes part of the copy, then fails, as an I/O error would
            Path(dest).write_bytes(b"k2")
            raise OSError("disk full")
        with mock.patch.object(rc, "copy_noatime", partial), self.assertRaises(OSError):
            iu.stage_data(cfg, iu.parse_unit("central_df"), {})
        self.assertEqual(list(iu.data_dir(cfg).glob("*")), [])
        dest, got = iu.stage_data(cfg, iu.parse_unit("central_df"), {})     # and a rerun is not blocked
        self.assertEqual(got, sha(b"k2a"))
        dest.unlink()

    def test_a_symlinked_data_dir_cannot_take_the_copy_out_of_the_namespace(self):
        d = self.tmp()
        cfg = dict(copy.deepcopy(REAL), namespace=str(d / "ns"))
        cfg["staging"] = dict(cfg["staging"], root=str(d / "ns" / "stage"))
        cfg["refs"]["k2a"].update(path=str(d / "k2a.root"), sha256=sha(b"k2a"))
        (d / "k2a.root").write_bytes(b"k2a")
        (d / "ns" / "stage").mkdir(parents=True)
        (d / "elsewhere").mkdir()
        (d / "ns" / "stage" / "data").symlink_to(d / "elsewhere")
        with self.assertRaises(iu.GateFailure):
            iu.stage_data(cfg, iu.parse_unit("central_df"), {})
        self.assertEqual(list((d / "elsewhere").iterdir()), [])

    def test_write_contained_refuses_a_symlink_an_existing_file_and_a_path_outside(self):
        d = self.tmp()
        cfg = dict(copy.deepcopy(REAL), namespace=str(d / "ns"))
        (d / "ns").mkdir()
        iu.write_contained(cfg, d / "ns" / "a.json", b"one")
        self.assertEqual((d / "ns" / "a.json").read_bytes(), b"one")
        with self.assertRaises(FileExistsError):                  # exclusive: never replaced
            iu.write_contained(cfg, d / "ns" / "a.json", b"two")
        (d / "ns" / "link.json").symlink_to(d / "target.json")
        with self.assertRaises(OSError):                          # O_NOFOLLOW (and O_EXCL): never written through
            iu.write_contained(cfg, d / "ns" / "link.json", b"x")
        with self.assertRaises(OSError):
            iu.write_contained(cfg, d / "ns" / "link.json", b"x", exclusive=False)
        self.assertFalse((d / "target.json").exists())
        with self.assertRaises(iu.GateFailure):
            iu.write_contained(cfg, d / "outside.json", b"x")
        self.assertFalse((d / "outside.json").exists())
        real = os.write                                        # agy read 5: a short write(2) is completed, not dropped
        with mock.patch.object(os, "write", lambda fd, b: real(fd, bytes(b[:3]))):
            iu.write_contained(cfg, d / "ns" / "long.bin", b"0123456789")
        self.assertEqual((d / "ns" / "long.bin").read_bytes(), b"0123456789")
        with mock.patch.object(os, "write", lambda fd, b: 0), self.assertRaises(OSError):
            iu.write_contained(cfg, d / "ns" / "stuck.bin", b"x")

    def test_marker_ok_needs_identity_digests_and_embedded_provenance(self):
        d = self.tmp()
        write_unit_products(d, "toy_G18_5720001", "toy")
        self.assertEqual(iu.marker_ok(d, "toy_G18_5720001", BOUND, "toy"), (True, "ok"))
        cases = {
            "another job": lambda: write_unit_products(d, "toy_G18_5720001", "toy", job="61800000"),
            "a FAIL verdict": lambda: write_unit_products(d, "toy_G18_5720001", "toy", verdict="FAIL"),
            "meta names another unit": lambda: write_unit_products(d, "toy_G18_5720001", "toy", meta_unit="toy_G18_5720002"),
            "the npz gone": lambda: (d / "toy_G18_5720001.npz").unlink(),
            "the root changed": lambda: (d / "toy_G18_5720001.root").write_bytes(b"other"),
            "another kind": lambda: write_unit_products(d, "toy_G18_5720001", "central"),
        }
        for tag, defect in cases.items():
            write_unit_products(d, "toy_G18_5720001", "toy")
            defect()
            with self.subTest(case=tag):
                self.assertFalse(iu.marker_ok(d, "toy_G18_5720001", BOUND, "toy")[0])
        write_unit_products(d, "toy_G18_5720001", "toy")         # an npz at its digest whose meta is unreadable
        (d / "toy_G18_5720001.npz").write_bytes(b"not an npz")
        m = json.loads((d / "toy_G18_5720001.done").read_text())
        (d / "toy_G18_5720001.done").write_text(json.dumps(dict(m, sha256=rc.sha256(d / "toy_G18_5720001.npz"))))
        self.assertIn("not readable", iu.marker_ok(d, "toy_G18_5720001", BOUND, "toy")[1])
        write_unit_products(d, "toy_G18_5720001", "toy")         # only the marker names another job (its meta is ours)
        m = json.loads((d / "toy_G18_5720001.done").read_text())
        (d / "toy_G18_5720001.done").write_text(json.dumps(dict(m, job="61800000")))
        self.assertFalse(iu.marker_ok(d, "toy_G18_5720001", BOUND, "toy")[0])
        write_unit_products(d, "toy_G18_5720001", "toy")         # a marker naming another unit
        m = json.loads((d / "toy_G18_5720001.done").read_text())
        (d / "toy_G18_5720001.done").write_text(json.dumps(dict(m, unit="toy_G18_5720002")))
        self.assertFalse(iu.marker_ok(d, "toy_G18_5720001", BOUND, "toy")[0])

    def test_resolve_argv_refuses_an_unresolved_variable(self):
        cfg = copy.deepcopy(REAL)
        cfg["e_r"]["argv"] = cfg["e_r"]["argv"] + ["--flux-universe-file", "$FLUXU"]
        with self.assertRaises(iu.GateFailure):
            iu.resolve_argv(cfg, None)

    def test_read_reference_reads_its_pin_and_refuses_another(self):
        d = self.tmp()
        np.savez(d / "ref.npz", ks=np.array([5, 10]), xsec=np.ones((2, 224)), T=np.ones(224), y=np.ones(224))
        cfg = copy.deepcopy(REAL)
        cfg["refs"]["c2_central"].update(path=str(d / "ref.npz"), sha256=rc.sha256(d / "ref.npz"))
        got = iu.read_reference(cfg)
        self.assertEqual(sorted(got), ["T", "ks", "xsec", "y"])
        cfg["refs"]["c2_central"]["sha256"] = "0" * 64
        with self.assertRaises(iu.GateFailure):
            iu.read_reference(cfg)

    def test_max_rel_of_two_shapes_is_infinite(self):
        self.assertEqual(iu.max_rel(np.ones(3), np.ones(4)), float("inf"))

    def test_preflight_stops_on_an_empty_toy_file(self):
        d, cfg = Pure.preflight_tree(self)
        (d / "G18" / "data_5720007.root").write_bytes(b"")
        self.assertEqual(iu.preflight(cfg), iu.RC_STOP)

    def test_main_dispatches_and_refuses(self):
        d, cfg = Pure.preflight_tree(self)
        cfg["namespace"] = str(d)
        cfg["staging"]["root"] = str(d / "stage")
        with mock.patch.object(iu, "load_config", lambda path=None: cfg), mock.patch.dict(os.environ, ENV):
            self.assertEqual(iu.main(["preflight"]), 0)
            self.assertEqual(iu.main(["run", "--unit", "er", "--out", str(d / "u")]), iu.RC_GATE)
            self.assertEqual(iu.main(["run", "--unit", "central", "--unit", "central", "--out", str(d / "u")]),
                             iu.RC_GATE)
            self.assertEqual(iu.main(["refcheck", "--out", str(d)]), iu.RC_STOP)   # no reference units there
            self.assertEqual(iu.main(["run", "--unit", "central", "--out", str(d.parent)]), iu.RC_GATE)   # off $N
            self.assertEqual(iu.main(["refcheck", "--out", str(d), "--time", "er=x"]), iu.RC_GATE)
            self.assertEqual(iu.main(["refcheck", "--out", str(d), "--step-rc", "central=x"]), iu.RC_GATE)
            stage_cfg = copy.deepcopy(cfg)
            for k in ("CV", "MC", "lib"):
                (d / f"s_{k}").write_bytes(k.encode())
                stage_cfg["inputs"].update({f"{k}_source": str(d / f"s_{k}"), f"{k}_sha256": sha(k.encode())})
        with mock.patch.object(iu, "load_config", lambda path=None: stage_cfg), mock.patch.dict(os.environ, ENV):
            self.assertEqual(iu.main(["stage"]), 0)
            # a run whose staged inputs pass reaches the driver loader; a missing reference is refused there
            stage_cfg["refs"]["c2_central"]["path"] = str(d / "absent.npz")
            self.assertEqual(iu.main(["run", "--unit", "central", "--out", str(d / "u")]), iu.RC_GATE)
        self.assertFalse((d / "u").exists())

    def test_c_g2r_refuses_before_the_driver_is_imported(self):
        """Blocker 8: main() checks every unit's argv before rc.load_driver, in both spellings."""
        d, cfg = Pure.preflight_tree(self)
        cfg["namespace"] = str(d)
        cfg["staging"]["root"] = str(d / "stage")
        for extra in (["--miss-map", "m.npz"], ["--miss-map=m.npz"]):
            bad = copy.deepcopy(cfg)
            bad["e_r"]["argv"] = cfg["e_r"]["argv"] + extra
            loads = []
            with self.subTest(extra=extra), mock.patch.object(iu, "load_config", lambda path=None: bad), \
                    mock.patch.dict(os.environ, ENV), mock.patch.object(rc, "load_driver", lambda: loads.append(1)), \
                    mock.patch.object(iu, "check_inputs", side_effect=AssertionError("inputs were read")):
                self.assertEqual(iu.main(["run", "--unit", "toy:G18:5720001", "--out", str(d / "u")]), iu.RC_GATE)
                self.assertEqual(loads, [])

    def test_main_runs_complete_bound_to_this_job(self):
        d, cfg = Pure.preflight_tree(self)
        cfg["namespace"] = str(d)
        with mock.patch.object(iu, "load_config", lambda path=None: cfg), mock.patch.dict(os.environ, ENV):
            self.assertEqual(iu.main(["complete", "--out", str(d)]), 1)        # an empty directory is not complete
            Hardening.complete_tree(self, d)
            self.assertEqual(iu.main(["complete", "--out", str(d)]), 0)

    def test_main_refuses_another_deploy_or_no_job(self):
        d, cfg = Pure.preflight_tree(self)
        cfg["namespace"] = str(d)
        for env in ({"IBUB_M": "0" * 40}, {"SLURM_JOB_ID": ""}):
            with self.subTest(env=env), mock.patch.object(iu, "load_config", lambda path=None: cfg), \
                    mock.patch.dict(os.environ, {**ENV, **env}):
                self.assertEqual(iu.main(["run", "--unit", "central", "--out", str(d / "u")]), iu.RC_GATE)
                self.assertEqual(iu.main(["complete", "--out", str(d)]), iu.RC_GATE)


@unittest.skipUnless(HAVE_DRIVER, "needs PyROOT and LightGBM")
class Driver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import ROOT
        import test_re2_driver as T2
        import test_re2_data_file as DF
        cls.td = Path(tempfile.mkdtemp()).resolve()
        stage = cls.td / "stage"
        stage.mkdir()
        omni, flux = stage / "fx.root", stage / "flux.root"
        T2.write_fixture(omni, flux)
        f = ROOT.TFile.Open(str(omni))
        pot = float(f.Get("dataPOTUsed").GetVal())
        f.Close()
        own = DF.read_data(omni)
        cls.k2a = cls.td / "k2a.root"                    # the omnifile's own data tree, as $K2A holds $CV's
        DF.write_data(cls.k2a, own, pot)
        toys = cls.td / "toys"
        toys.mkdir()
        rng = np.random.default_rng(8)
        keep = rng.uniform(size=own["measured"].size) < 0.8
        cls.seed = c.TOY_SEEDS["G18"][3]
        cls.toy = toys / f"data_{cls.seed}.root"
        DF.write_data(cls.toy, {k: v[keep] for k, v in own.items()}, pot)
        files = [{"seed": s, "role": "toy", "sha256": rc.sha256(cls.toy) if s == cls.seed else "0" * 64,
                  "path": str(toys / f"data_{s}.root")} for s in c.TOY_SEEDS["G18"]]
        raw = json.dumps({"verdict": "PASS", "files": files}).encode()
        (cls.td / "pb.json").write_bytes(raw)
        cfg = copy.deepcopy(REAL)
        cfg["namespace"] = str(cls.td)
        cfg["staging"].update(root=str(stage), CV=omni.name, MC=flux.name)
        cfg["e_r"]["argv"] = [("2" if x == "5" else x) for x in REAL["e_r"]["argv"]]     # --iters 2, as test_ref_c2c1
        cfg["e_r"]["cpus"] = rc.cpu_count()
        cfg["e_r"]["thread_env"] = {k: os.environ.get(k) for k in REAL["e_r"]["thread_env"]}
        cfg["toys"]["G18"].update(dir=str(toys), pseudo_b=str(cls.td / "pb.json"), pseudo_b_sha256=sha(raw))
        cfg["refs"]["k2a"].update(path=str(cls.k2a), sha256=rc.sha256(cls.k2a))
        cls.cfg = cfg
        cls.shas = {"G18": iu.toy_shas(cfg, "G18")}
        cls.rep = iu.reported_cells(REAL)
        cls.driver, cls.ohf = rc.load_driver()
        first = cls.td / "first"                          # the reference: an earlier central run (C-REP needs one)
        # no assertion here: a setup error would be a harness failure, so the outcome is a test's (the codex read r2)
        cls.first_rc = iu.run_unit(cls.driver, cls.ohf, cfg, iu.parse_unit("central"), first, shas=cls.shas,
                                   rep=cls.rep, ref=None, bound=BOUND, unfolder=rc.dagostini)
        z = np.load(first / "central.npz") if (first / "central.npz").exists() else None
        cls.ref = {k: z[k] for k in ("ks", "xsec", "T", "y")} if z is not None else {
            "ks": np.array([]), "xsec": np.zeros((0, 224)), "T": np.zeros(224), "y": np.zeros(224)}
        cls.out = cls.td / "units"
        cls.rcs = {u: cls.unit(u, cls.out) for u in ("central", "central_df", f"toy:G18:{cls.seed}")}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.td, True)

    @classmethod
    def unit(cls, spec, out, cfg=None, ref=None, bound=None):
        return iu.run_unit(cls.driver, cls.ohf, cfg or cls.cfg, iu.parse_unit(spec), out, shas=cls.shas, rep=cls.rep,
                           ref=cls.ref if ref is None else ref, bound=bound or BOUND, unfolder=rc.dagostini)

    def meta(self, name, out=None):
        return json.loads(str(np.load((out or self.out) / f"{name}.npz")["meta"]))

    def test_a_central_with_no_reference_fails_c_rep(self):
        self.assertEqual(self.first_rc, iu.RC_CONTROL)
        self.assertFalse(self.meta("central", self.td / "first")["controls"]["C-REP"]["pass"])

    def test_every_unit_passes_every_control(self):
        self.assertEqual(self.rcs, {"central": 0, "central_df": 0, f"toy:G18:{self.seed}": 0})
        want = {"central": {"C-G2R", "C-FILL", "C-ROO", "C-SIM", "C-DATA", "C-REP"},
                "central_df": {"C-G2R", "C-FILL", "C-ROO", "C-DATA", "C-REP-D"},
                f"toy_G18_{self.seed}": {"C-G2R", "C-FILL", "C-ROO", "C-DATA"}}
        for name, keys in want.items():
            m = self.meta(name)
            self.assertEqual(set(m["controls"]), keys)
            self.assertTrue(all(v["pass"] for v in m["controls"].values()), m["controls"])
            marker = json.loads((self.out / f"{name}.done").read_text())
            self.assertEqual((marker["verdict"], marker["unit"], marker["kind"]), ("PASS", name, m["kind"]))
            self.assertEqual((marker["tune"], marker["seed"]), (m["tune"], m["seed"]))
            self.assertEqual((marker["job"], marker["deploy_head"]), (BOUND["job"], BOUND["deploy_head"]))
            self.assertEqual((m["slurm_job"], m["deploy_head"]), (BOUND["job"], BOUND["deploy_head"]))

    def test_central_df_equals_central_and_the_toy_differs(self):
        a, b, t = (np.load(self.out / f"{n}.npz") for n in ("central", "central_df", f"toy_G18_{self.seed}"))
        self.assertTrue(iu.compare(a, b, self.rep, 1e-8)["pass"])
        self.assertFalse(iu.compare(a, t, self.rep, 1e-8)["pass"])
        self.assertEqual(self.meta("central_df")["data_sha256"], rc.sha256(self.k2a))
        self.assertEqual(self.meta(f"toy_G18_{self.seed}")["data_sha256"], self.shas["G18"][self.seed])
        self.assertIsNone(self.meta("central")["data_sha256"])
        self.assertEqual(self.meta(f"toy_G18_{self.seed}")["argv"][-2:],
                         ["--data-file", str(iu.data_dir(self.cfg) / f"toy_G18_{self.seed}.root")])

    def test_the_data_copies_are_deleted(self):
        self.assertEqual(list(iu.data_dir(self.cfg).glob("*.root")), [])

    def test_a_data_file_off_its_pin_is_refused_with_no_products(self):
        shas = {"G18": {**self.shas["G18"], self.seed: "0" * 64}}
        out = self.td / "offpin"
        rc_ = iu.run_unit(self.driver, self.ohf, self.cfg, iu.parse_unit(f"toy:G18:{self.seed}"), out, shas=shas,
                          rep=self.rep, ref=self.ref, bound=BOUND, unfolder=rc.dagostini)
        self.assertEqual(rc_, iu.RC_GATE)
        self.assertEqual(list(out.glob("*")), [])
        self.assertEqual(list(iu.data_dir(self.cfg).glob("*.root")), [])

    def test_a_perturbed_reference_fails_c_rep(self):
        ref = dict(self.ref, xsec=self.ref["xsec"] * (1 + 1e-6))
        out = self.td / "badref"
        self.assertEqual(self.unit("central_df", out, ref=ref), iu.RC_CONTROL)
        self.assertFalse(self.meta("central_df", out)["controls"]["C-REP-D"]["pass"])
        self.assertEqual(json.loads((out / "central_df.done").read_text())["verdict"], "FAIL")

    def test_an_unfolder_off_the_numpy_update_fails_c_roo(self):
        off = lambda M, T, y, ks: {k: v * (1 + 1e-6) for k, v in rc.dagostini(M, T, y, ks).items()}  # noqa: E731
        out = self.td / "croo"
        rc_ = iu.run_unit(self.driver, self.ohf, self.cfg, iu.parse_unit(f"toy:G18:{self.seed}"), out, shas=self.shas,
                          rep=self.rep, ref=self.ref, bound=BOUND, unfolder=off)
        self.assertEqual(rc_, iu.RC_CONTROL)
        self.assertFalse(self.meta(f"toy_G18_{self.seed}", out)["controls"]["C-ROO"]["pass"])

    def test_a_recorded_data_digest_other_than_the_staged_copys_fails_c_data(self):
        """The driver records the data file's digest itself (dataFileSha256); C-DATA compares it with the staged copy's.
        Here the driver records another digest for the data file only (the helper's and its own are untouched)."""
        real = self.driver.file_sha256
        data_dir = str(iu.data_dir(self.cfg))
        wrong = lambda p: "0" * 64 if str(p).startswith(data_dir) else real(p)   # noqa: E731
        out = self.td / "cdata"
        with mock.patch.object(self.driver, "file_sha256", wrong):
            self.assertEqual(self.unit(f"toy:G18:{self.seed}", out), iu.RC_CONTROL)
        c_data = self.meta(f"toy_G18_{self.seed}", out)["controls"]["C-DATA"]
        self.assertFalse(c_data["pass"])
        self.assertEqual(c_data["dataFileSha256"], "0" * 64)

    def test_a_unit_whose_controls_are_not_the_declared_set_writes_no_marker(self):
        out = self.td / "ctlset"
        with mock.patch.dict(iu.CONTROLS, {"toy": iu.CONTROLS["toy"] | {"C-EXTRA"}}):
            self.assertEqual(self.unit(f"toy:G18:{self.seed}", out), iu.RC_GATE)
        self.assertFalse((out / f"toy_G18_{self.seed}.done").exists())
        self.assertEqual(list(iu.data_dir(self.cfg).glob("*.root")), [])

    def test_miss_map_is_refused_before_the_driver(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["e_r"]["argv"] = cfg["e_r"]["argv"] + ["--miss-map", "m.npz"]
        out = self.td / "g2r"
        with mock.patch.object(rc, "run_driver", side_effect=AssertionError("the driver ran")):
            self.assertEqual(self.unit("central", out, cfg=cfg), iu.RC_GATE)
        self.assertFalse((out / "central.npz").exists())

    def test_another_cpu_count_or_numexpr_is_refused(self):
        for tag, change in (("cpus", lambda c_: c_["e_r"].update(cpus=rc.cpu_count() + 1)),
                            ("numexpr", lambda c_: c_["e_r"]["thread_env"].update(NUMEXPR_NUM_THREADS="999"))):
            cfg = copy.deepcopy(self.cfg)
            change(cfg)
            out = self.td / f"gate_{tag}"
            with self.subTest(gate=tag):
                self.assertEqual(self.unit("central", out, cfg=cfg), iu.RC_GATE)
                self.assertFalse(out.exists())

    def test_main_runs_a_lane_of_units_with_roounfold_as_the_unfolder(self):
        """main(): pins, staged inputs and reference read once, then each unit; RooUnfold is replaced by the numpy
        update it equals (C-ROO compares the two; REF-C2C1 proved the equality)."""
        cfg = copy.deepcopy(self.cfg)
        for k in ("CV", "MC"):
            cfg["inputs"][f"{k}_sha256"] = rc.sha256(iu.staged(cfg)[k])
        lib = iu.staged(cfg)["lib"]
        lib.write_bytes(b"not a library")
        self.addCleanup(lib.unlink)
        cfg["inputs"]["lib_sha256"] = rc.sha256(lib)
        np.savez(self.td / "ref.npz", **self.ref)
        cfg["refs"]["c2_central"].update(path=str(self.td / "ref.npz"), sha256=rc.sha256(self.td / "ref.npz"))
        out = self.td / "main"
        times = []
        for u in iu.REFERENCE_UNITS:                          # each reference step's /usr/bin/time file
            times += ["--time", f"{u}={gnu_time_file(self.td / f'{u}.time', '3:00.00')}", "--step-rc", f"{u}=0"]
        with mock.patch.object(iu, "load_config", lambda path=None: cfg), mock.patch.dict(os.environ, ENV), \
                mock.patch.object(rc, "load_driver", lambda: (self.driver, self.ohf)), \
                mock.patch.object(rc, "roounfold_bayes", lambda M, T, y, ks, lib_: rc.dagostini(M, T, y, ks)):
            self.assertEqual(iu.main(["run", "--unit", "central", "--unit", f"toy:G18:{self.seed}", "--out", str(out)]), 0)
            self.assertEqual(iu.main(["run", "--unit", "central_df", "--out", str(out)]), 0)
            self.assertEqual(iu.main(["refcheck", "--out", str(out), *times]), 0)
        self.assertEqual(json.loads((out / "refcheck.json").read_text())["verdict"], "PASS")
        self.assertEqual(self.meta(f"toy_G18_{self.seed}", out)["inputs_sha256"],
                         {k: cfg["inputs"][f"{k}_sha256"] for k in ("CV", "MC", "lib")})

    def test_a_malformed_marker_beside_products_is_not_overwritten(self):
        out = self.td / "malformed"
        out.mkdir()
        (out / "central.root").write_bytes(b"x")
        (out / "central.done").write_text("{trunc")
        self.assertEqual(self.unit("central", out), iu.RC_CONTROL)
        self.assertEqual((out / "central.root").read_bytes(), b"x")

    def test_a_pass_marker_without_its_products_or_naming_another_unit_is_not_skipped(self):
        """The codex read r2, item 2: a skip needs identity, both digests and the embedded provenance."""
        out = self.td / "skip"
        self.assertEqual(self.unit("central_df", out), 0)
        (out / "central_df.npz").unlink()
        self.assertEqual(self.unit("central_df", out), iu.RC_CONTROL)
        out2 = self.td / "skip2"
        self.assertEqual(self.unit("central_df", out2), 0)
        m = json.loads((out2 / "central_df.done").read_text())
        (out2 / "central_df.done").write_text(json.dumps(dict(m, unit="central")))
        self.assertEqual(self.unit("central_df", out2), iu.RC_CONTROL)

    def test_c_sim_finite_catches_a_nan_the_pinned_c_sim_drops(self):
        """The codex read r2, item 4: ref_c2c1.c_sim keeps a running max that drops a NaN at a later K."""
        cap = rc.run_driver(self.driver, self.ohf, iu.resolve_argv(self.cfg, None), self.td / "csim.root",
                            ibu={"unfolder": rc.dagostini, "ks": REAL["c2"]["scan"], "primary": 10},
                            staging=iu.staging_root(self.cfg))
        ks = REAL["c2"]["scan"]
        self.assertTrue(iu.c_sim_finite(self.driver, cap, ks))
        real = cap["real_extract"]

        def poisoned():
            calls = []

            def extract(h, *a, **k):              # call 0 is the reference; call 2 is the second K's extraction
                out = real(h, *a, **k)
                calls.append(1)
                if len(calls) == 3:
                    out.SetBinContent(5, 8, float("nan"))
                return out
            return extract
        def poisoned_reference():
            def extract(h, *a, **k):              # the reference (call 0) holds a NaN
                out = real(h, *a, **k)
                if not getattr(extract, "done", False):
                    out.SetBinContent(5, 8, float("nan"))
                    extract.done = True
                return out
            return extract
        self.assertFalse(iu.c_sim_finite(self.driver, dict(cap, real_extract=poisoned_reference()), ks))
        bad = dict(cap, real_extract=poisoned())
        self.assertTrue(rc.c_sim(self.driver, bad, rc.dagostini, ks, 1e-9)["pass"])     # the pinned check misses it
        self.assertFalse(iu.c_sim_finite(self.driver, dict(cap, real_extract=poisoned()), ks))

    def test_a_driver_output_that_is_not_a_regular_file_writes_no_marker(self):
        out = self.td / "notfile"
        real = iu.provenance

        def provenance_then_remove(path):          # the output disappears after the driver's own checks read it
            p = real(path)
            Path(path).unlink()
            return p
        with mock.patch.object(iu, "provenance", provenance_then_remove):
            self.assertEqual(self.unit("central_df", out), iu.RC_GATE)
        self.assertFalse((out / "central_df.done").exists())

    def test_a_pass_unit_is_skipped_only_for_this_job_and_deploy(self):
        """Blocker 4: a PASS marker from another job or deploy is refused, never accepted as done."""
        self.assertEqual(self.unit("central", self.out), 0)
        for other in ({"job": "61800000", "deploy_head": HEAD}, {"job": BOUND["job"], "deploy_head": "0" * 40}):
            with self.subTest(other=other):
                self.assertEqual(self.unit("central", self.out, bound=other), iu.RC_CONTROL)

    def test_a_pass_unit_is_skipped_and_a_failed_one_is_not_overwritten(self):
        self.assertEqual(self.unit("central", self.out), 0)
        out = self.td / "badref"
        if not (out / "central_df.done").exists():
            self.unit("central_df", out, ref=dict(self.ref, xsec=self.ref["xsec"] * 2))
        self.assertEqual(self.unit("central_df", out), iu.RC_CONTROL)


if __name__ == "__main__":
    unittest.main()
