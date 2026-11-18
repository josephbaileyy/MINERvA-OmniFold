#!/usr/bin/env python3
"""Tests of RDX's read-only fetch (rdx_fetch_remote.py, rdx_fetch_launch.sh; RDX-BINDING-1 addendum J7): the fetch run
locally against a scratch root with a stub sacct, the unpack's refusals, and the launcher's checks. Each guard in the
direction it acts and in the other."""
import ast
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REMOTE = HERE / "rdx_fetch_remote.py"
LAUNCH = HERE / "rdx_fetch_launch.sh"
sys.path.insert(0, str(HERE))
import rdx_fetch_remote as F  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.d = Path(self._t.name)
        self.root = self.d / "out"
        for rel in F.FILES:
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(hashlib.sha256(rel.encode()).digest() * 3)
            mt = p.stat().st_mtime_ns  # atime after mtime, so a relatime-style platform (the laptop) leaves it alone
            os.utime(p, ns=(mt + 10 ** 12, mt))
        self.bin = self.d / "bin"
        self.bin.mkdir()
        self.sacct("")

    def tearDown(self):
        self._t.cleanup()

    def sacct(self, rows: str, rc: int = 0):
        s = self.bin / "sacct"
        s.write_text(f"#!/bin/bash\nprintf '%s' {json.dumps(rows)}\nexit {rc}\n")
        s.chmod(0o755)

    def fetch(self):
        env = {**os.environ, "RDX_FETCH_TEST_ROOT": str(self.root), "PATH": f"{self.bin}:{os.environ['PATH']}"}
        with open(REMOTE, "rb") as src:
            return subprocess.run([sys.executable, "-"], stdin=src, capture_output=True, env=env)

    def tar_with(self, mutate=None, manifest_edit=None, extra=None, drop=None) -> Path:
        """A fetch's tar, with the manifest marked O_NOATIME (the laptop has none) and an optional defect."""
        r = self.fetch()
        self.assertEqual(r.returncode, 0, r.stderr)
        members = {}
        with tarfile.open(fileobj=io.BytesIO(r.stdout), mode="r:") as tf:
            for m in tf.getmembers():
                members[m.name] = tf.extractfile(m).read()
        man = json.loads(members["manifest.json"])
        man["o_noatime"] = True
        if manifest_edit:
            manifest_edit(man)
        members["manifest.json"] = json.dumps(man).encode()
        if mutate:
            members[mutate] = members[mutate] + b"x"
        if drop:
            members.pop(drop)
        if extra:
            members[extra] = b"x"
        out = self.d / "f.tar"
        with tarfile.open(out, "w") as tf:
            for n, b in members.items():
                info = tarfile.TarInfo(n)
                info.size = len(b)
                tf.addfile(info, io.BytesIO(b))
        return out

    def unpack(self, tar: Path):
        dest = self.d / f"dest{len(list(self.d.glob('dest*')))}"
        dest.mkdir()
        return subprocess.run([sys.executable, str(REMOTE), "unpack", str(tar), str(dest)], capture_output=True, text=True), dest


class Fetch(Base):
    def test_a_clear_fence_streams_every_file_with_its_manifest(self):
        r = self.fetch()
        self.assertEqual(r.returncode, 0, r.stderr)
        with tarfile.open(fileobj=io.BytesIO(r.stdout), mode="r:") as tf:
            names = [m.name for m in tf.getmembers()]
            man = json.loads(tf.extractfile("manifest.json").read())
        self.assertEqual(names, list(F.FILES) + ["manifest.json"])
        self.assertEqual(len(F.FILES), 32)
        self.assertEqual(man["atime_moved"], [])
        self.assertTrue(all(x["atime_unchanged"] for x in man["files"]))
        self.assertEqual(man["files"][0]["sha256"], hashlib.sha256((self.root / F.FILES[0]).read_bytes()).hexdigest())

    def test_the_fence_refuses_before_any_output(self):
        for rows in ("61|rdx_s3_a|RUNNING\n", "62|pfb_run|PENDING\n", "63|cov2d_x|RUNNING\n", "64|ibukt-a|RUNNING\n"):
            self.sacct(rows)
            r = self.fetch()
            self.assertEqual(r.returncode, 9, rows)
            self.assertEqual(r.stdout, b"", "nothing is written before the fence passes")
        self.sacct("65|other_job|RUNNING\n")
        self.assertEqual(self.fetch().returncode, 0)
        self.sacct("", rc=1)
        r = self.fetch()
        self.assertEqual((r.returncode, r.stdout), (9, b""))

    def test_a_missing_file_refuses_before_any_output(self):
        (self.root / F.LOGS[1]).unlink()
        r = self.fetch()
        self.assertEqual((r.returncode, r.stdout), (4, b""))

    def test_no_o_noatime_refuses_outside_a_test(self):
        if hasattr(os, "O_NOATIME"):
            self.skipTest("this platform has O_NOATIME")
        env = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}"}
        env.pop("RDX_FETCH_TEST_ROOT", None)
        with open(REMOTE, "rb") as src:
            r = subprocess.run([sys.executable, "-"], stdin=src, capture_output=True, env=env)
        self.assertEqual((r.returncode, r.stdout), (3, b""))

    def test_the_remote_script_is_python_3_6(self):
        ast.parse(REMOTE.read_text(), feature_version=(3, 6))

    def test_the_declared_files(self):
        self.assertEqual(F.ROOT if not os.environ.get("RDX_FETCH_TEST_ROOT") else None,
                         "/pscratch/sd/j/josephrb/rdx-20261112b/out")
        self.assertEqual(F.LOGS, ("logs/rdx_s3_a_61478320.out", "logs/rdx_s3_b_61481240.out"))
        self.assertEqual(F.TASKS, tuple(ln.split("\t")[0] for ln in (HERE / "rdx_tasks.tsv").read_text().splitlines()
                                        if ln and not ln.startswith("#")))


class Unpack(Base):
    def test_a_good_tar_unpacks_exactly_the_files(self):
        r, dest = self.unpack(self.tar_with())
        self.assertEqual(r.returncode, 0, r.stderr)
        got = sorted(str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file())
        self.assertEqual(got, sorted(list(F.FILES) + ["manifest.json"]))
        self.assertEqual((dest / F.FILES[3]).read_bytes(), (self.root / F.FILES[3]).read_bytes())

    def test_unpack_refuses_every_defect(self):
        for kw, why in (({"mutate": F.FILES[0]}, "does not match its manifest"),
                        ({"extra": "products/X9.npz"}, "unexpected"),
                        ({"extra": "../escape"}, "unexpected"),
                        ({"drop": F.FILES[5]}, "missing members"),
                        ({"manifest_edit": lambda m: m.update(o_noatime=False)}, "no O_NOATIME"),
                        ({"manifest_edit": lambda m: m.update(atime_moved=["x"])}, "moved atime"),
                        ({"manifest_edit": lambda m: m["fence"].update(clear=False)}, "fence")):
            r, dest = self.unpack(self.tar_with(**kw))
            self.assertEqual(r.returncode, 2, kw)
            self.assertIn(why, r.stderr, kw)
            self.assertEqual(list(dest.iterdir()), [], "nothing is written on a refusal")

    def test_unpack_needs_a_new_empty_directory(self):
        tar = self.tar_with()
        dest = self.d / "full"
        dest.mkdir()
        (dest / "x").write_text("x")
        r = subprocess.run([sys.executable, str(REMOTE), "unpack", str(tar), str(dest)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


class Launcher(unittest.TestCase):
    def run_launch(self, *args):
        return subprocess.run(["bash", str(LAUNCH), *args], capture_output=True, text=True,
                              env={**os.environ, "PATH": "/usr/bin:/bin"})

    def test_the_launcher_pins_the_script_and_checks_its_arguments(self):
        sha = hashlib.sha256(REMOTE.read_bytes()).hexdigest()
        self.assertIn(f'SHA={sha}\n', LAUNCH.read_text())
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_launch(d, "saul").returncode, 9)
            Path(d, "x").write_text("x")
            self.assertEqual(self.run_launch(d, "login27").returncode, 9)
        text = LAUNCH.read_text()
        self.assertIn('/usr/bin/python3 -" < "$S"', text, "the script goes over stdin; nothing is staged on the cluster")
        self.assertNotIn("/dev/shm", text.split("# Usage")[1])
        self.assertNotIn("sbatch", text.split("# Usage")[1])
        self.assertNotIn('"squeue"', REMOTE.read_text(), "no command invokes squeue")
        self.assertIn('cmd = ["sacct",', REMOTE.read_text())


if __name__ == "__main__":
    unittest.main()
