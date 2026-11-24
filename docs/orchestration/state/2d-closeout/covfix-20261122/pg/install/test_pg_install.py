"""Tests for pg-install-g2111a.py (B2) on a stub tarball: no cluster, no SciSoft download.

Run: python3 -I -B test_pg_install.py -v   (from this directory)
"""
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


I = load("pg_install", HERE / "pg-install-g2111a.py")
BR = load("build_record", HERE.parent / "record" / "build_record.py")
Q = "genie_xsec/v3_04_00/NULL/Q"
ENTRIES = [("genie_xsec", "dir", None), ("genie_xsec/v3_04_00", "dir", None), ("genie_xsec/v3_04_00/NULL", "dir", None),
           (Q, "dir", None), (f"{Q}/data", "dir", None), (f"{Q}/data/gxspl-NUsmall.xml", "file", b"<spl/>\n" * 100),
           (f"{Q}/data/gxspl-FNALsmall.xml", "sym", "gxspl-NUsmall.xml"), (f"{Q}/data/README", "file", b"readme\n"),
           (f"{Q}/ups", "dir", None), (f"{Q}/ups/genie_xsec.table", "file", b"table\n")]


def make_tar(path, entries):
    with tarfile.open(path, "w:bz2") as tf:
        for name, kind, x in entries:
            ti = tarfile.TarInfo(name)
            if kind == "file":
                ti.size, ti.mode = len(x), 0o644
                tf.addfile(ti, io.BytesIO(x))
                continue
            ti.type = {"dir": tarfile.DIRTYPE, "sym": tarfile.SYMTYPE}[kind]
            ti.mode = 0o755
            if kind == "sym":
                ti.linkname = x
            tf.addfile(ti)


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Install(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="pgi-", dir="/tmp")))
        self.addCleanup(self.clean)
        self.tar = self.tmp / "src.tar.bz2"
        make_tar(self.tar, ENTRIES)
        self.members = BR.members(str(self.tar))
        self.dbc = self.tmp / "dbconfig"
        self.dbc.write_text("FILE = DBCONFIG\n")
        self.root = self.tmp / "scratch/covfix-pg/products"

    def clean(self):
        for d, _, _ in os.walk(self.tmp):
            os.chmod(d, 0o755)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def install(self, tar=None, **kw):
        src = tar or self.tar

        def fetch(url, out):
            shutil.copy(src, out)
            return 0
        args = dict(root=str(self.root), url="https://x/t.tar.bz2", tarball_sha=sha(self.tar.read_bytes()),
                    members=self.members, dbconfig_src=str(self.dbc), dbconfig_sha=sha(self.dbc.read_bytes()),
                    ident=lambda: {"pass": True}, fetch=fetch, scratch=str(self.tmp / "scratch") + "/")
        args.update(kw)
        return I.install(**args)

    def test_go(self):
        r = self.install()
        self.assertEqual(r["verdict"], "GO", r["stops"])
        self.assertEqual(sorted(os.listdir(self.root)), [".upsfiles", "genie_xsec"])   # the download is gone
        self.assertEqual(I.check_tree(str(self.root), self.members, readonly=True), [])
        self.assertEqual((self.root / ".upsfiles/dbconfig").read_text(), "FILE = DBCONFIG\n")
        self.assertEqual(os.readlink(self.root / f"{Q}/data/gxspl-FNALsmall.xml"), "gxspl-NUsmall.xml")
        for p in (self.root / f"{Q}/data/README", self.root / f"{Q}/data", self.root / ".upsfiles/dbconfig"):
            self.assertFalse(os.lstat(p).st_mode & 0o222, p)
        self.assertIn("install_utc", r)

    def test_a_changed_download_is_removed_and_stops(self):
        bad = self.tmp / "bad.tar.bz2"
        make_tar(bad, ENTRIES[:-1])
        r = self.install(tar=bad)
        self.assertEqual(r["verdict"], "STOP")
        self.assertIn("the download's sha256 differs", r["stops"][0])
        self.assertEqual(os.listdir(self.root / "dl"), [])

    def test_a_member_that_differs_from_its_pin_extracts_nothing(self):
        for i, change in enumerate((lambda m: m[f"{Q}/data/README"].update(sha256="0" * 64),
                                    lambda m: m.pop(f"{Q}/ups/genie_xsec.table"),
                                    lambda m: m.update({f"{Q}/data/extra": {"type": "file", "sha256": "0" * 64}}),
                                    lambda m: m[f"{Q}/data/gxspl-FNALsmall.xml"].update(target="README"),
                                    lambda m: m[f"{Q}/data"].update(type="file"))):
            with self.subTest(i):
                self.clean()
                self.setUp()
                m = json.loads(json.dumps(self.members))
                change(m)
                try:
                    r = self.install(members=m)
                except Exception as e:                       # a crash is not a refusal
                    self.fail(f"install crashed: {type(e).__name__}: {e}")
                self.assertEqual(r["verdict"], "STOP")
                self.assertTrue(r["scan_problems"])
                self.assertFalse((self.root / "genie_xsec").exists())

    def test_a_stray_file_in_the_product_stops(self):
        def fetch(url, out):
            shutil.copy(self.tar, out)
            (self.root / "stray").write_text("x")             # something else writes into the product directory
            return 0
        r = self.install(fetch=fetch)
        self.assertEqual(r["verdict"], "STOP")
        self.assertTrue(any("holds" in p for p in r["tree_problems"]), r["tree_problems"])

    def test_dbconfig_must_be_the_pinned_one(self):
        r = self.install(dbconfig_sha="0" * 64)
        self.assertEqual(r["verdict"], "STOP")
        self.assertIn("dbconfig differs from the pin", r["stops"][0])
        self.assertFalse((self.root / ".upsfiles").exists())

    def test_refusals_write_nothing(self):
        for name, kw in (("identity", dict(ident=lambda: {"pass": False})), ("no dbconfig pin", dict(dbconfig_sha=None)),
                         ("not on scratch", dict(scratch="/pscratch/"))):
            with self.subTest(name):
                r = self.install(**kw)
                self.assertEqual(r["verdict"], "STOP")
                self.assertFalse(self.root.exists())
        self.root.mkdir(parents=True)
        r = self.install()
        self.assertIn("already exists", r["stops"][0])
        self.assertEqual(os.listdir(self.root), [])

    def test_check_tree_finds_changes(self):
        self.assertEqual(self.install()["verdict"], "GO")
        d = self.root / f"{Q}/data"
        os.chmod(d, 0o755)
        (d / "ModelConfiguration.xml").write_text("x")
        os.chmod(d / "README", 0o644)
        probs = I.check_tree(str(self.root), self.members, readonly=True)
        self.assertTrue(any(p.startswith("extra: ") for p in probs))
        self.assertTrue(any(p.endswith("README: writable") for p in probs))
        (d / "README").write_text("other\n")
        self.assertTrue(any("README: sha256 differs" in p for p in I.check_tree(str(self.root), self.members, False)))


class NodeLaunch(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="pgl-", dir="/tmp")))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.L = load("pg_node_launch", HERE / "pg-node-launch.py")
        self.script = self.tmp / "pg-install-g2111a.py"
        self.script.write_text("print('hi')\n")
        self.sha = sha(self.script.read_bytes())

    def launch(self, body, sha_=None, script=None):
        s = self.tmp / "ssh"
        s.write_text(f"#!/bin/sh\necho \"$@\" > {self.tmp}/args\ncat > {self.tmp}/stdin\n{body}\n")
        s.chmod(0o755)
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return self.L.main([str(script or self.script), sha_ or self.sha], ssh=str(s))

    def emit(self, rec, rc):
        f = self.tmp / f"r{len(list(self.tmp.iterdir()))}.txt"
        f.write_text("x\nPG-RESULT " + json.dumps(rec) + "\n")
        return f"cat {f}; exit {rc}"

    def test_receipts(self):
        out = Path(str(self.script) + ".out")
        go = {"schema": "covfix-pg-install/1", "verdict": "GO", "stops": []}
        self.assertEqual(self.launch(self.emit(go, 0)), 0)
        self.assertEqual((self.tmp / "stdin").read_bytes(), self.script.read_bytes())
        for i, (rec, rc) in enumerate(((dict(go, schema="covfix-pg-replay/1"), 0), (dict(go, stops=["x"]), 0),
                                       (dict(go, verdict="STOP"), 3), (go, 3), ({"verdict": "GO"}, 0))):
            with self.subTest(i):
                out.unlink()
                self.assertEqual(self.launch(self.emit(rec, rc)), 4)
        out.unlink()
        self.assertEqual(self.launch(self.emit(dict(go, verdict="STOP", stops=["x"]), 3)), 3)

    def test_refusals_and_options(self):
        self.assertEqual(self.launch("exit 0", sha_="0" * 64), 5)
        other = self.tmp / "other.py"
        other.write_text("x")
        self.assertEqual(self.launch("exit 0", sha_=sha(b"x"), script=other), 5)        # not a reviewed node script
        Path(str(self.script) + ".out").write_text("old")
        self.assertEqual(self.launch("exit 0"), 5)
        PL = load("pg_probe_launch", HERE.parent / "probe" / "pg-probe-launch.py")
        self.assertEqual((self.L.SSH_OPTS, self.L.REMOTE, self.L.HOST), (PL.SSH_OPTS, PL.REMOTE, PL.HOST))


RP = load("pg_replay", HERE / "pg-replay-g2111a.py")
EA = load("embed_archive", HERE / "embed_archive.py")
DRIVER = """#!/bin/bash
[ "$1" = --workdir ] || exit 2
echo "[replay] stub $PG_STUB_RC"
printf '{"pass": %s, "checks": {"x": true}, "spline_opened": {}, "gated": {}}' "${PG_STUB_PASS:-true}" > "$2/replay.json"
exit ${PG_STUB_RC:-0}
"""


class Replay(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="pgr-", dir="/tmp")))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        r = self.repo = self.tmp / "repo"
        (r / "3d-unfolding/genie").mkdir(parents=True)
        (r / "3d-unfolding/genie/pg_replay.sh").write_text(DRIVER)
        (r / "3d-unfolding/genie/pg_replay.sh").chmod(0o755)
        (r / "3d-unfolding/genie/gen5d_v3.py").write_text("x = 1\n")
        (r / "setup_salloc_env.sh").write_text("true\n")
        git = ["git", "-C", str(r), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(git[:3] + ["init", "-q"], check=True)
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-qm", "c"], check=True)
        self.paths = ["3d-unfolding/genie", "setup_salloc_env.sh"]
        self.commit = subprocess.run(git[:3] + ["rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        self.data, self.blobs = EA.build(self.commit, r, self.paths)
        self.seen = []

    def run_replay(self, data=None, blobs=None, env=None, **kw):
        import base64

        def run(argv, **k):
            self.seen.append(argv)
            k["env"] = dict(k["env"], **(env or {}))
            return subprocess.run(argv[5:], **k)                 # without nice and timeout, which macOS lacks
        import datetime as dt
        self.calls = getattr(self, "calls", 0) + 1                # a distinct replay directory per call
        args = dict(now=dt.datetime(2026, 11, 25, 0, 0, self.calls, tzinfo=dt.timezone.utc),
                    parent=str(self.tmp / "scratch"), archive_b64=base64.b64encode(data or self.data).decode(),
                    archive_sha=sha(self.data), blobs=self.blobs if blobs is None else blobs, commit=self.commit,
                    ident=lambda: {"pass": True}, run=run, home=str(self.tmp))
        args.update(kw)
        return RP.replay(**args)

    def assert_stop(self, r, text):
        self.assertEqual(r["verdict"], "STOP", r)
        self.assertTrue(any(text in x for x in r["stops"]), r["stops"])

    def test_go(self):
        r = self.run_replay()
        self.assertEqual(r["verdict"], "GO", r["stops"])
        self.assertEqual(r["n_files_checked"], 3)
        self.assertEqual(self.seen[0][:5], ["/usr/bin/nice", "-n", "19", "/usr/bin/timeout", str(RP.WALL_CAP_S)])
        self.assertEqual(r["driver_lines"], ["[replay] stub "])
        self.assertTrue(r["replay"]["pass"])
        self.assertEqual(sorted(os.listdir(r["replay_dir"])), ["deploy", "driver.log", "run", "tmp"])

    def test_the_archive_and_the_blobs(self):
        import gzip
        import tarfile as tf_
        bad = gzip.compress(b"x" * 100)
        r = self.run_replay(data=bad)
        self.assert_stop(r, "the archive differs from its pin")
        self.assertFalse((self.tmp / "scratch").exists())                         # nothing written
        r = self.run_replay(blobs=dict(self.blobs, **{"3d-unfolding/genie/gen5d_v3.py": "0" * 40}))
        self.assert_stop(r, "blob differs")
        r = self.run_replay(blobs=dict(self.blobs, **{"extra.txt": "0" * 40}))
        self.assert_stop(r, "missing: extra.txt")
        bl = dict(self.blobs)
        bl.pop("setup_salloc_env.sh")
        r = self.run_replay(blobs=bl)
        self.assert_stop(r, "is not a pinned blob")
        buf = io.BytesIO()
        with tf_.open(fileobj=buf, mode="w") as t:
            ti = tf_.TarInfo("3d-unfolding/genie/link")
            ti.type, ti.linkname = tf_.SYMTYPE, "/etc/passwd"
            t.addfile(ti)
        lnk = gzip.compress(buf.getvalue())
        r = self.run_replay(data=lnk, archive_sha=sha(lnk))
        self.assert_stop(r, "neither a directory nor a regular file")
        for d in (self.tmp / "scratch").iterdir():
            self.assertFalse((d / "driver.log").exists())                        # the driver never ran

    def test_refusals_and_driver_failures(self):
        import datetime as dt
        now = dt.datetime(2026, 11, 24, 12, 0, 0, tzinfo=dt.timezone.utc)
        (self.tmp / "scratch/replay-20261124T120000Z").mkdir(parents=True)
        self.assert_stop(self.run_replay(now=now), "already exists")
        self.assert_stop(self.run_replay(ident=lambda: {"pass": False}), "identity")
        self.assert_stop(self.run_replay(commit="", archive_b64=""), "not embedded")
        self.assert_stop(self.run_replay(env={"PG_STUB_RC": "4"}), "exited 4")
        self.assert_stop(self.run_replay(env={"PG_STUB_PASS": "false"}), "did not all pass")

    def test_embed_refuses_links(self):
        (self.repo / "3d-unfolding/genie/l").symlink_to("gen5d_v3.py")
        git = ["git", "-C", str(self.repo), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-qm", "l"], check=True)
        with self.assertRaises(SystemExit):
            EA.build("HEAD", self.repo, self.paths)


class Constants(unittest.TestCase):
    def test_embedded_members_are_the_records(self):
        rec = json.loads((HERE.parent / "record/G2111a-members.json").read_text())
        self.assertEqual(I.MEMBERS, rec)
        self.assertEqual(I.TARBALL_SHA256, rec["tarball_sha256"])
        self.assertTrue(I.URL.endswith("/" + rec["tarball"]))
        self.assertEqual(I.ROOT, "/pscratch/sd/j/josephrb/covfix-pg/products")
        import sys
        sys.path.insert(1, str(HERE.parents[6] / "3d-unfolding/genie"))
        import pg_verify
        self.assertEqual(I.ROOT, pg_verify.PRIVATE_PRODUCTS)
        self.assertIsNone(I.DBCONFIG_SHA256)                       # filled only from the director's pin


if __name__ == "__main__":
    unittest.main()
