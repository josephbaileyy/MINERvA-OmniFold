#!/usr/bin/env python3
"""Tests of PILOT-FB's copy connect (pfb_copy_remote.py, pfb_copy_launch.sh; PILOT-FB-BINDING-1 addendum C1, ruling 3
step 3): the copy run locally against a scratch root with a stub sacct and test pins, its refusals, the laptop verify,
and the launcher's checks. Each guard in the direction it acts and in the other."""
import ast
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ND = Path(__file__).resolve().parents[1]
REMOTE = ND / "pfb_copy_remote.py"
LAUNCH = ND / "pfb_copy_launch.sh"
sys.path.insert(0, str(ND))
import pfb_copy_remote as C  # noqa: E402
import fb_pilot_analyze as A  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.d = Path(self._t.name).resolve()
        self.stage = self.d / "stage"
        self.stage.mkdir()
        (self.stage / "smoke-receipt.json").write_text("{}")
        self.a0 = self.d / "rs1" / "runs" / "A0"
        self.a0.mkdir(parents=True)
        self.deploy = self.d / "deploy"
        (self.deploy / Path(C.SIGMA_REL).parent).mkdir(parents=True)
        pins = {}
        for n in C.A0_PINS:
            p = self.a0 / n
            p.write_bytes(n.encode() * 7)
            pins[n] = hashlib.sha256(p.read_bytes()).hexdigest()
        sig = self.deploy / C.SIGMA_REL
        sig.write_text('{"sigma_rel_pct": [1.0]}')
        pins[C.SIGMA_NAME] = hashlib.sha256(sig.read_bytes()).hexdigest()
        for p in list(self.a0.iterdir()) + [sig]:  # atime after mtime, so a relatime platform leaves it alone
            mt = p.stat().st_mtime_ns
            os.utime(p, ns=(mt + 10 ** 12, mt))
        (self.d / "pins.json").write_text(json.dumps(pins))
        self.pins = pins
        self.bin = self.d / "bin"
        self.bin.mkdir()
        self.sacct("")

    def tearDown(self):
        self._t.cleanup()

    def sacct(self, rows: str, rc: int = 0):
        s = self.bin / "sacct"
        s.write_text(f"#!/bin/bash\nprintf '%b' {json.dumps(rows)}\nexit {rc}\n")
        s.chmod(0o755)

    def run_copy(self, deploy=None, **env):
        e = {**os.environ, "PFB_COPY_TEST_ROOT": str(self.d), "PATH": f"{self.bin}:{os.environ['PATH']}", **env}
        with open(REMOTE, "rb") as src:
            return subprocess.run([sys.executable, "-", str(deploy or self.deploy)], stdin=src, capture_output=True, env=e)

    def assert_nothing_written(self):
        self.assertEqual(sorted(p.name for p in self.stage.iterdir()), ["smoke-receipt.json"])


class Copy(Base):
    def test_the_pins_are_rs1s_and_the_sigma_receipts(self):
        self.assertEqual(C.A0_PINS, {n: s for n, s in A.rs1_pins(A.RS1_SUMS).items()
                                     if n in {A.name("rs1_A0", None)} | {A.name("rs1_A0", j) for j in A.SEEDS}})
        self.assertEqual(len(C.A0_PINS), 21)
        import rounding_mechanism_analyze as ra
        self.assertEqual(C.SIGMA_SHA256, ra.SIGMA_RECEIPT_SHA256)
        self.assertEqual(C.SIGMA_REL, A.SIGMA_REL)
        self.assertEqual((C.STAGE_DECLARED, str(C.A0_DIR_DECLARED)), (A.STAGE_DECLARED, str(A.RS1_A0_ORIGINALS)))

    def test_a_clear_copy_makes_plain_new_files_inside_the_stage(self):
        before = {p.name: p.stat() for p in self.a0.iterdir()}
        r = self.run_copy()
        self.assertEqual(r.returncode, 0, r.stderr)
        man = json.loads(r.stdout)
        self.assertEqual(len(man["files"]), 22)
        self.assertEqual(sorted(p.name for p in (self.stage / "a0-refs").iterdir()), sorted(C.A0_PINS))
        for n in C.A0_PINS:
            q = self.stage / "a0-refs" / n
            st = os.lstat(q)
            self.assertTrue(q.is_file() and not q.is_symlink() and st.st_nlink == 1)
            self.assertNotEqual((st.st_dev, st.st_ino), (before[n].st_dev, before[n].st_ino), "a new inode")
            self.assertEqual(q.read_bytes(), (self.a0 / n).read_bytes())
            self.assertEqual(before[n].st_atime_ns, (self.a0 / n).stat().st_atime_ns, "the source's atime is unchanged")
            self.assertIsNone(A.stage_copy_problem(q, self.stage, (self.a0 / n,)), "the analysis accepts the copy")
        self.assertIsNone(A.stage_copy_problem(self.stage / C.SIGMA_NAME, self.stage, (self.deploy / C.SIGMA_REL,)))
        self.assertTrue(all(not f["moved"] and not f["problems"] for f in man["files"]))
        self.assertEqual(sorted(p.name for p in self.stage.iterdir()), ["a0-refs", C.SIGMA_NAME, "smoke-receipt.json"],
                         "nothing but the copies is written")

    def test_the_stage_must_be_the_smokes_and_hold_no_copies(self):
        (self.stage / "smoke-receipt.json").unlink()
        r = self.run_copy()
        self.assertEqual(r.returncode, 2)
        self.assertIn("lacks the smoke's receipt", r.stderr.decode())
        self.assertEqual(list(self.stage.iterdir()), [])
        (self.stage / "smoke-receipt.json").symlink_to(self.d / "pins.json")
        self.assertIn("not a plain file", self.run_copy().stderr.decode())
        (self.stage / "smoke-receipt.json").unlink()
        (self.stage / "smoke-receipt.json").write_text("{}")
        (self.stage / "a0-refs").mkdir()
        r = self.run_copy()
        self.assertEqual(r.returncode, 2)
        self.assertIn("already holds a0-refs", r.stderr.decode())
        (self.stage / "a0-refs").rmdir()
        r = self.run_copy(deploy="relative/deploy")
        self.assertEqual(r.returncode, 2)
        self.assert_nothing_written()

    def test_a_source_off_its_pin_or_a_link_refuses_before_any_write(self):
        n = sorted(C.A0_PINS)[3]
        (self.a0 / n).write_bytes(b"changed")
        r = self.run_copy()
        self.assertEqual(r.returncode, 4, r.stderr)
        self.assertIn("not at its pin", r.stderr.decode())
        self.assert_nothing_written()
        (self.a0 / n).unlink()
        real = self.d / "elsewhere.npz"
        real.write_bytes(n.encode() * 7)
        (self.a0 / n).symlink_to(real)
        r = self.run_copy()
        self.assertEqual(r.returncode, 5, r.stderr)
        self.assertIn("not a regular file", r.stderr.decode())
        self.assert_nothing_written()
        (self.a0 / n).unlink()
        r = self.run_copy()
        self.assertEqual(r.returncode, 5)
        self.assertIn("no source", r.stderr.decode())
        self.assert_nothing_written()

    def test_the_fence_refuses_before_any_write(self):
        for rows in ("61|pfb_run|RUNNING\n", "62|cov2d_x|COMPLETING\n", "63|ibukt-a|PENDING\n", "64|bad row\n"):
            self.sacct(rows)
            r = self.run_copy()
            self.assertEqual((r.returncode, r.stdout), (9, b""), rows)
            self.assert_nothing_written()
        self.sacct("65|pfb_run|COMPLETED\n66|other|RUNNING\n")
        self.assertEqual(self.run_copy().returncode, 0)

    def test_a_moved_source_refuses_before_any_write(self):
        target = self.a0 / sorted(C.A0_PINS)[5]
        st = target.stat()
        real_fdopen = os.fdopen

        def fdopen(fd, mode="r", *a, **k):
            fh = real_fdopen(fd, mode, *a, **k)
            if "b" not in mode or os.fstat(fd).st_ino != target.stat().st_ino:
                return fh

            class Tear:
                def __enter__(self_):
                    return self_

                def __exit__(self_, *exc):
                    fh.close()

                def fileno(self_):
                    return fh.fileno()

                def read(self_):
                    data = fh.read()
                    os.utime(target, ns=(st.st_atime_ns, st.st_mtime_ns + 10 ** 9))
                    return data
            return Tear()

        out = io.StringIO()
        with mock.patch.dict(os.environ, {"PFB_COPY_TEST_ROOT": str(self.d), "PATH": f"{self.bin}:{os.environ['PATH']}"}), \
                mock.patch.object(C, "STAGE", str(self.stage)), mock.patch.object(C, "A0_DIR", str(self.a0)), \
                mock.patch.object(C, "TEST", str(self.d)), mock.patch.object(C.os, "fdopen", fdopen), \
                mock.patch.object(sys, "stdout", out), self.assertRaises(SystemExit) as cm:
            C.copy(str(self.deploy))
        self.assertEqual(cm.exception.code, 8)
        self.assert_nothing_written()

    def test_the_remote_script_is_python_3_6_and_runs_no_job(self):
        ast.parse(REMOTE.read_text(), feature_version=(3, 6))
        text = REMOTE.read_text()
        for word in ('"sbatch"', '"srun"', '"salloc"', '"squeue"'):
            self.assertNotIn(word, text)
        self.assertIn('cmd = ["sacct",', text)


class Verify(Base):
    def manifest(self):
        r = self.run_copy()
        self.assertEqual(r.returncode, 0, r.stderr)
        man = json.loads(r.stdout)
        man.update(stage=C.STAGE_DECLARED, a0_dir=C.A0_DIR_DECLARED, o_noatime=True)
        for f in man["files"]:  # the test pins are not the real ones; verify reads the real pins
            f["sha256"] = f["copy_sha256"] = (C.A0_PINS.get(f["name"]) or C.SIGMA_SHA256)
        return man

    def verify(self, man):
        p = self.d / "m.json"
        p.write_text(json.dumps(man))
        return subprocess.run([sys.executable, str(REMOTE), "verify", str(p)], capture_output=True, text=True)

    def test_verify_accepts_a_good_manifest_and_refuses_each_defect(self):
        man = self.manifest()
        self.assertEqual(self.verify(man).returncode, 0, self.verify(man).stderr)
        for edit, why in ((lambda m: m.update(stage="/tmp/stage"), "not the declared"),
                          (lambda m: m.update(o_noatime=False), "no O_NOATIME"),
                          (lambda m: m["fence_after"].update(clear=False), "fence"),
                          (lambda m: m["files"].pop(), "exactly the 22"),
                          (lambda m: m["files"][2].update(sha256="0" * 64), "not at its pin"),
                          (lambda m: m["files"][2].update(moved=["st_mtime_ns"]), "stat moved"),
                          (lambda m: m["files"][2].update(copy_inode=m["files"][2]["source_inode"]), "new inode"),
                          (lambda m: m["files"][2].update(copy_nlink=2), "new inode")):
            m = json.loads(json.dumps(man))
            edit(m)
            r = self.verify(m)
            self.assertEqual(r.returncode, 2, why)
            self.assertIn(why, r.stderr, why)


class Launcher(unittest.TestCase):
    def run_launch(self, *args):
        return subprocess.run(["bash", str(LAUNCH), *args], capture_output=True, text=True,
                              env={**os.environ, "PATH": "/usr/bin:/bin"})

    def test_the_launcher_pins_the_script_and_checks_its_arguments(self):
        text = LAUNCH.read_text()
        self.assertIn(f'SHA={hashlib.sha256(REMOTE.read_bytes()).hexdigest()}\n', text)
        dep = "/pscratch/sd/j/josephrb/pfb-deploy"
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_launch(d, "saul", dep).returncode, 9, "a login node name")
            for bad in ("/global/homes/j/josephrb/deploy", "relative", "/pscratch/sd/j/josephrb/../x",
                        "/pscratch/sd/j/josephrb/a b"):
                r = self.run_launch(d, "login27", bad)
                self.assertEqual(r.returncode, 9, bad)
                self.assertIn("is not an absolute /pscratch/sd/j/josephrb path", r.stdout, bad)
            Path(d, "x").write_text("x")
            self.assertEqual(self.run_launch(d, "login27", dep).returncode, 9, "a new empty directory")
        body = text.split("# Usage")[1]
        for word in ("sbatch", "srun", "salloc", "squeue", "/global/"):
            self.assertNotIn(word, body)
        hop = text.split("\nHOP=(", 1)[1].split(")", 1)[0]
        for opt in ("ControlPath=none", "StrictHostKeyChecking=yes", "UpdateHostKeys=no"):
            self.assertIn(opt, hop)
        self.assertIn('/usr/bin/python3 - $DEPLOY" < "$S"', text, "the script goes over stdin with the deploy")


if __name__ == "__main__":
    unittest.main()
