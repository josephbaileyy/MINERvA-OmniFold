"""Tests of flux1_delete.py on a fixture tree (macOS or Linux). Run: python3 -B test_delete.py.
The module's constants are replaced by the fixture's (built with step A's own listing code); its logic is unchanged.
An audit hook records every os.remove/os.rmdir/shutil.rmtree, so each STOP case can show that nothing was removed."""
import contextlib
import hashlib
import importlib.util
import io
import os
import stat
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REMOVED = []


def hook(event, args):
    if event in ("os.remove", "os.rmdir", "shutil.rmtree", "os.unlink"):
        REMOVED.append((event, os.fsdecode(args[0]) if args and isinstance(args[0], (str, bytes)) else args))


sys.addaudithook(hook)


def load():
    spec = importlib.util.spec_from_file_location("fd", os.path.join(HERE, "flux1_delete.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def w(p, data):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(data)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def build(top, m):
    """A miniature of the root, and constants for it in the module m."""
    root, orig = os.path.join(top, "root"), os.path.join(top, "originals")
    files = {
        "clone/a/x.py": b"x" * 9, "clone/README": b"r",
        "run/original-inputs/aa-dump.npz": b"D" * 40, "run/original-inputs/bb-repo.txt": b"R" * 4,
        "run/mat-data/P/data/flux.root": b"F" * 20,
        "run/flux-factors-1A.npz": b"N" * 7, "run/flux-extract.json": b"{}", "run/prestage.json": b"{1}",
        ".rpd-private/h/prestage.json": b"{p}",
        "job.out": b"job", "run/flux-custody.json": b"c", "run/staged/config.json": b"cfg", "tools/f.py": b"t",
    }
    for r, b in files.items():
        w(os.path.join(root, r), b)
    os.makedirs(os.path.join(root, "run/tmp"))
    w(os.path.join(orig, "dump.npz"), b"D" * 40)
    w(os.path.join(orig, "flux.root"), b"F" * 20)
    m.ROOT = root
    entries, _ = m.listing(root, getattr(os, "O_NOATIME", 0))
    m.TREE_ENTRIES = len(entries)
    m.TREE_SHA = sha(m.canon(entries).encode())
    m.CLONE_SHA = sha(m.canon([e for e in entries if e[0] == "clone" or e[0].startswith("clone/")]).encode())
    m.STAGED = {r: sha(files[r]) for r in ("run/original-inputs/aa-dump.npz", "run/original-inputs/bb-repo.txt",
                                            "run/mat-data/P/data/flux.root")}
    m.ORIGINALS = {}
    for r, o in (("run/original-inputs/aa-dump.npz", "dump.npz"), ("run/mat-data/P/data/flux.root", "flux.root")):
        st = os.lstat(os.path.join(orig, o))
        m.ORIGINALS[r] = (os.path.join(orig, o), st.st_size, st.st_mtime_ns)
    m.RECORDS = {r: sha(files[r]) for r in ("job.out", "run/flux-custody.json", "run/staged/config.json",
                                            "tools/f.py")}
    m.DELETE_FILES = ["job.out", "run/flux-custody.json"]
    m.DELETE_TREES = ["clone", "run/original-inputs", "run/mat-data", "run/staged", "run/tmp", "tools"]
    m.KEEP_AFTER = sorted(["run", "run/flux-factors-1A.npz", "run/flux-extract.json", "run/prestage.json",
                           ".rpd-private", ".rpd-private/h", ".rpd-private/h/prestage.json"])
    return root, orig


def run(m, root):
    buf = io.StringIO()
    del REMOVED[:]
    with contextlib.redirect_stdout(buf):
        rc = m.main(root=root, require_login=False, noatime=getattr(os, "O_NOATIME", 0), originals=m.ORIGINALS)
    return rc, buf.getvalue()


def names(root):
    out = []
    for d, ds, fs in os.walk(root):
        for n in ds + fs:
            out.append(os.path.relpath(os.path.join(d, n), root))
    return sorted(out)


class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.m = load()
        self.root, self.orig = build(self.tmp.name, self.m)
        self.before = names(self.root)

    def tearDown(self):
        for d, ds, fs in os.walk(self.tmp.name):
            os.chmod(d, 0o755)
        self.tmp.cleanup()

    def stopped(self, rc, out, msg):
        self.assertEqual(rc, 4, out)
        self.assertIn(msg, out)
        self.assertEqual(REMOVED, [], "something was removed on a STOP")
        self.assertEqual(names(self.root), self.before)

    def test_happy_path_keeps_exactly_the_kept_set(self):
        rc, out = run(self.m, self.root)
        self.assertEqual(rc, 0, out)
        self.assertIn("DELETE :: DONE", out)
        self.assertEqual(names(self.root), self.m.KEEP_AFTER)
        self.assertIn("original committed in git", out)          # bb-repo.txt has no pscratch original
        self.assertTrue(os.path.exists(os.path.join(self.orig, "dump.npz")))   # originals untouched

    def test_changed_byte_in_a_staged_copy_stops(self):
        w(os.path.join(self.root, "run/original-inputs/aa-dump.npz"), b"D" * 39 + b"d")
        self.before = names(self.root)
        self.stopped(*run(self.m, self.root), "DIFFERS from")

    def test_missing_original_stops(self):
        os.remove(os.path.join(self.orig, "dump.npz"))
        rc, out = run(self.m, self.root)
        self.assertEqual(rc, 4, out)
        self.assertIn("MISSING", out)
        self.assertEqual([r for r in REMOVED if r[1].startswith(self.root)], [])
        self.assertEqual(names(self.root), self.before)

    def test_original_with_moved_mtime_stops(self):
        p = os.path.join(self.orig, "flux.root")
        st = os.stat(p)
        os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns + 10**9))
        self.stopped(*run(self.m, self.root), "CHANGED")

    def test_extra_entry_changes_the_listing_and_stops(self):
        w(os.path.join(self.root, "run/new.txt"), b"")
        self.before = names(self.root)
        self.stopped(*run(self.m, self.root), "the tree is not step A's")

    def test_changed_record_stops(self):
        w(os.path.join(self.root, "run/flux-custody.json"), b"C")
        self.before = names(self.root)
        self.stopped(*run(self.m, self.root), "record run/flux-custody.json sha256")

    def test_off_login_node_stops(self):
        buf = io.StringIO()
        del REMOVED[:]
        with contextlib.redirect_stdout(buf):
            rc = self.m.main(root=self.root, require_login=True, noatime=getattr(os, "O_NOATIME", 0),
                             originals=self.m.ORIGINALS)
        self.stopped(rc, buf.getvalue(), "STOP: not a login node")

    def test_symlinked_root_stops(self):
        link = os.path.join(self.tmp.name, "rootlink")
        os.symlink(self.root, link)
        self.stopped(*run(self.m, link), "missing or not a directory")

    def test_a_failed_removal_returns_9(self):
        os.chmod(os.path.join(self.root, "clone/a"), stat.S_IRUSR | stat.S_IXUSR)
        rc, out = run(self.m, self.root)
        self.assertEqual(rc, 9, out)
        self.assertIn("removal errors", out)

    def test_a_wrong_kept_set_returns_8(self):
        self.m.KEEP_AFTER = self.m.KEEP_AFTER + ["run/expected-but-absent"]
        rc, out = run(self.m, self.root)
        self.assertEqual(rc, 8, out)
        self.assertIn("NOT the kept set", out)


class Generated(unittest.TestCase):
    """The committed flux1_delete.py: its constants are consistent with each other and with step A."""

    def test_constants(self):
        m = load()
        self.assertEqual(m.TREE_SHA, "6e9a273506598728091867436ef2fa562f3418f9726175d2d43bfb0ddce6ee89")
        self.assertEqual(m.TREE_ENTRIES, 24422)
        self.assertEqual(len(m.STAGED), 69)
        self.assertEqual(len(m.ORIGINALS), 64)
        self.assertEqual(len(m.RECORDS), 37)
        keep = [r for r in m.KEEP_AFTER if not r.startswith(".rpd-private") and r != "run"]
        self.assertEqual(sorted(keep), sorted(["run/flux-factors-%s.npz" % p for p in
                                               "1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P".split()]
                                              + ["run/flux-extract.json", "run/prestage.json"]))
        doomed = set(m.DELETE_FILES) | {t for t in m.DELETE_TREES}
        for k in m.KEEP_AFTER:
            self.assertFalse(k in doomed or any(k.startswith(t + "/") for t in m.DELETE_TREES), k)
        for r in list(m.STAGED) + list(m.RECORDS):
            self.assertTrue(r in m.DELETE_FILES or any(r.startswith(t + "/") for t in m.DELETE_TREES), r)
        self.assertEqual(m.ROOT, "/pscratch/sd/j/josephrb/rpd-reco-flux-20261111")


if __name__ == "__main__":
    unittest.main(verbosity=2)
