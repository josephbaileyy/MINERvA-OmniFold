import hashlib, os, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0, "/t"); import cov2d_stage as st
def sha(b): return hashlib.sha256(b).hexdigest()
class Stager(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp()); (self.d / "src").mkdir(); (self.d / "dst").mkdir()
        self.files = {f"f{i}.root": os.urandom(3_000_000 + i) for i in range(3)}
        for n, b in self.files.items(): (self.d / "src" / n).write_bytes(b)
    def manifest(self, wrong=None):
        m = self.d / "m.tsv"
        m.write_text("".join(f"{self.d/'src'/n}\t{self.d/'dst'/n}\t{('0'*64) if n == wrong else sha(b)}\n" for n, b in self.files.items()))
        return m
    def run_(self, m, rec):
        r = subprocess.run([sys.executable, "/t/cov2d_stage.py", str(m), str(rec), "2"], capture_output=True, text=True)
        return r.returncode, r.stdout
    def test_pass(self):
        rc, out = self.run_(self.manifest(), self.d / "rec")
        self.assertEqual(rc, 0, out); self.assertIn("STAGE PASS 3 of 3", out)
        rows = (self.d / "rec").read_text().split("\n")[:-1]
        self.assertEqual(len(rows), 3)
        for (n, b), row in zip(self.files.items(), rows):
            p = self.d / "dst" / n
            self.assertEqual(p.read_bytes(), b); self.assertEqual(oct(p.stat().st_mode & 0o777), "0o440")
            self.assertEqual(row.split()[0], sha(b)); self.assertEqual(row.split()[-1], str(p))
            self.assertFalse(Path(str(p) + ".partial").exists())
    def test_wrong_digest_fails_and_stays_partial(self):
        rc, out = self.run_(self.manifest(wrong="f1.root"), self.d / "rec")
        self.assertEqual(rc, 4, out); self.assertIn("STAGE FAIL 1 of 3", out)
        self.assertTrue((self.d / "dst" / "f1.root.partial").exists()); self.assertFalse((self.d / "dst" / "f1.root").exists())
        self.assertFalse((self.d / "rec").exists())
    def test_refuses_existing_destination_and_record(self):
        m = self.manifest(); (self.d / "dst" / "f0.root").write_bytes(b"x")
        rc, out = self.run_(m, self.d / "rec"); self.assertEqual(rc, 4); self.assertIn("REFUSE", out)
        (self.d / "dst" / "f0.root").unlink(); (self.d / "rec").write_text("")
        rc, out = self.run_(m, self.d / "rec"); self.assertEqual(rc, 4); self.assertIn("REFUSE", out)
    def test_refuses_a_bad_manifest(self):
        m = self.d / "m.tsv"; m.write_text("a\tb\tshort\n")
        rc, out = self.run_(m, self.d / "rec"); self.assertEqual(rc, 4); self.assertIn("REFUSE", out)
    def test_atime_moved_fails(self):
        src = self.d / "src" / "f0.root"; real = os.stat; calls = {"n": 0}
        class S:  # a stat result whose atime moves between the reads of the source
            def __init__(self, s, bump): self.s, self.bump = s, bump
            def __getattr__(self, k): return getattr(self.s, k) + (self.bump if k == "st_atime_ns" else 0)
        def fake(p, *a, **k):
            s = real(p, *a, **k)
            if str(p) == str(src):
                calls["n"] += 1; return S(s, calls["n"])
            return s
        with mock.patch.object(st.os, "stat", fake):
            ok, row, log = st.one(str(src), str(self.d / "dst" / "f0.root"), sha(self.files["f0.root"]))
        self.assertFalse(ok); self.assertIn("atime moved", log)
    def test_size_mismatch_and_changed_while_hashed_are_guards(self):
        # the copy is hashed after it is written: a wrong digest of a correct copy is refused (as above); here the
        # source grows after the copy, so sizes differ
        src = self.d / "src" / "f2.root"; real = os.stat
        def fake(p, *a, **k):
            s = real(p, *a, **k)
            if str(p) == str(src):
                class G:
                    def __getattr__(_, k): return getattr(s, k) + (1 if k == "st_size" else 0)
                return G()
            return s
        with mock.patch.object(st.os, "stat", fake):
            ok, row, log = st.one(str(src), str(self.d / "dst" / "f2.root"), sha(self.files["f2.root"]))
        self.assertFalse(ok); self.assertIn("size differs", log)
    def test_o_noatime_is_used_for_every_source_read(self):
        opened = []; real = os.open
        def spy(p, flags, *a):
            opened.append((str(p), flags)); return real(p, flags, *a)
        with mock.patch.object(st.os, "open", spy):
            st.one(str(self.d / "src" / "f0.root"), str(self.d / "dst" / "f0.root"), sha(self.files["f0.root"]))
        reads = [(p, f) for p, f in opened if not f & os.O_WRONLY]
        self.assertTrue(reads); self.assertTrue(all(f & os.O_NOATIME for _, f in reads), reads)
unittest.main(argv=["x", "-v"])
