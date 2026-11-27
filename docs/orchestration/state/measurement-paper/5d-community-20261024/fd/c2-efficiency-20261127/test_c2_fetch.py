"""Tests for the C2-EFF fetch: the remote reader on a fake tree (O_NOATIME injected by the harness only, since macOS has
none), the verifier, and the wrapper's local gates in --check-only mode. Nothing here connects anywhere.

run: python3 -I -B test_c2_fetch.py
"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REMOTE = os.path.join(HERE, "c2_fetch_remote.py")
VERIFY = os.path.join(HERE, "c2_fetch_verify.py")
WRAPPER = os.path.join(HERE, "c2_fetch.sh")
PREFIX = "/pscratch/sd/j/josephrb/ref-c2c1-20261106/read-2/inputs/"
KS = [1, 2, 3, 4, 5, 10, 15, 20]
INJECT = ("import os, sys; os.O_NOATIME = 0; sys.argv = ['c2_fetch_remote.py', sys.argv[1], sys.argv[2]]; "
          "p = %r; exec(compile(open(p).read(), p, 'exec'))" % REMOTE)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def npz_bytes(name, ks=KS, shape=(8, 224)):
    buf = io.BytesIO()
    rng = np.random.default_rng(abs(hash(name)) % 2**32)
    np.savez_compressed(buf, ks=np.array(ks), xsec=rng.random(shape) * 1e-39,
                        meta=json.dumps({"unit": name}))
    return buf.getvalue()


class Tree:
    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="c2eff-test-")
        self.units = os.path.join(self.root, "units")
        self.inputs = os.path.join(self.root, "inputs")
        os.mkdir(self.units)
        os.mkdir(self.inputs)
        names = ["c2_replica_b%d" % b for b in range(1, 301)] + ["c2_central"]
        for n in names:
            b = npz_bytes(n)
            with open(os.path.join(self.units, n + ".npz"), "wb") as f:
                f.write(b)
            with open(os.path.join(self.units, n + ".done"), "w") as f:
                f.write(json.dumps({"unit": n, "verdict": "PASS", "sha256": sha(b), "root_sha256": "x"}) + "\n")
        lines = []
        for i in range(1, 302):
            b = os.urandom(100 + i)
            with open(os.path.join(self.inputs, "%03d_xsec.root" % i), "wb") as f:
                f.write(b)
            lines.append("%d %s%03d_xsec.root\n" % (len(b), PREFIX, i))
        self.listing = os.path.join(self.root, "listing.txt")
        with open(self.listing, "w") as f:
            f.write("".join(lines))
        with open(os.path.join(self.units, "c2_central.npz"), "rb") as f:
            self.central = sha(f.read())
        self.out = os.path.join(self.root, "out")
        os.mkdir(self.out)
        self.freeze_atimes()

    def freeze_atimes(self):
        """Harness only: macOS has no O_NOATIME, so give every file an atime after its mtime (relatime-style hosts then
        leave it alone on a read). The reader's own atime check is unchanged and still runs."""
        for d in (self.units, self.inputs):
            for n in os.listdir(d):
                p = os.path.join(d, n)
                st = os.lstat(p)
                os.utime(p, ns=(st.st_mtime_ns + 3600 * 10**9, st.st_mtime_ns), follow_symlinks=False)

    def remote(self, inject=True):
        cmd = [sys.executable, "-I", "-B", "-c", INJECT, self.units, self.inputs] if inject else \
            [sys.executable, "-I", "-B", REMOTE, self.units, self.inputs]
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with open(os.path.join(self.out, "fetch.tar"), "wb") as f:
            f.write(r.stdout)
        return r

    def verify(self):
        r = subprocess.run([sys.executable, "-I", "-B", VERIFY, self.out, self.listing, self.central],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return r.returncode, r.stdout.decode().strip().splitlines()[-1]

    def close(self):
        shutil.rmtree(self.root)


def rewrite_tar(path, mutate):
    with tarfile.open(path, "r:") as t:
        members = [(m, t.extractfile(m).read()) for m in t]
    members = mutate(members)
    with tarfile.open(path, "w:", format=tarfile.PAX_FORMAT) as t:
        for m, b in members:
            ti = tarfile.TarInfo(m.name)
            ti.size = len(b)
            t.addfile(ti, io.BytesIO(b))


class Fetch(unittest.TestCase):
    def setUp(self):
        self.t = Tree()

    def tearDown(self):
        self.t.close()

    def ok_remote(self):
        self.t.freeze_atimes()
        r = self.t.remote()
        self.assertEqual(r.returncode, 0, r.stderr.decode())
        self.assertEqual(r.stderr.decode().strip().splitlines()[-1], "FETCH-DONE 903 files")

    def test_good_tree_fetches_and_verifies(self):
        self.ok_remote()
        rc, last = self.t.verify()
        self.assertEqual((rc, last), (0, "VERIFY OK 903"))
        with open(os.path.join(self.t.out, "SHA256SUMS")) as f:
            self.assertEqual(len(f.readlines()), 903)

    def test_no_o_noatime_refuses(self):
        r = self.t.remote(inject=False)
        self.assertEqual(r.returncode, 9)
        self.assertIn("O_NOATIME is not available", r.stderr.decode())

    def test_a_read_that_moves_atime_is_caught(self):
        for d in (self.t.units, self.t.inputs):
            for n in os.listdir(d):
                p = os.path.join(d, n)
                st = os.lstat(p)
                os.utime(p, ns=(st.st_mtime_ns - 10**9, st.st_mtime_ns))
        r = self.t.remote()
        self.assertEqual(r.returncode, 9)
        self.assertIn("atime moved", r.stderr.decode())
        self.assertNotIn(b"MANIFEST.tsv", r.stdout)

    def test_missing_file_refuses_before_any_tar(self):
        os.remove(os.path.join(self.t.inputs, "150_xsec.root"))
        r = self.t.remote()
        self.assertEqual(r.returncode, 9)
        self.assertEqual(r.stdout, b"")

    def test_symlink_refuses(self):
        p = os.path.join(self.t.units, "c2_replica_b7.done")
        os.rename(p, p + ".real")
        os.symlink(p + ".real", p)
        r = self.t.remote()
        self.assertEqual(r.returncode, 9)
        self.assertIn("not a regular file", r.stderr.decode())

    def test_empty_file_refuses(self):
        open(os.path.join(self.t.inputs, "001_xsec.root"), "wb").close()
        self.assertEqual(self.t.remote().returncode, 9)

    def test_bad_argv_refuses(self):
        r = subprocess.run([sys.executable, "-I", "-B", "-c", INJECT.replace(
            "sys.argv[1], sys.argv[2]]", "sys.argv[1]]"), self.t.units, self.t.inputs],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(r.returncode, 9)

    def test_missing_manifest_refuses(self):
        self.ok_remote()
        rewrite_tar(os.path.join(self.t.out, "fetch.tar"), lambda ms: [x for x in ms if x[0].name != "MANIFEST.tsv"])
        rc, last = self.t.verify()
        self.assertEqual(rc, 9)
        self.assertIn("no MANIFEST", last)

    def test_tampered_member_refuses(self):
        self.ok_remote()
        def mut(ms):
            return [(m, (b[:-1] + bytes([b[-1] ^ 1])) if m.name == "inputs/007_xsec.root" else b) for m, b in ms]
        rewrite_tar(os.path.join(self.t.out, "fetch.tar"), mut)
        rc, last = self.t.verify()
        self.assertEqual(rc, 9)
        self.assertIn("differs from the remote manifest", last)

    def test_unexpected_member_refuses(self):
        self.ok_remote()
        class M:
            name = "units/extra.npz"
        rewrite_tar(os.path.join(self.t.out, "fetch.tar"), lambda ms: ms + [(M, b"x")])
        rc, last = self.t.verify()
        self.assertEqual(rc, 9)
        self.assertIn("unexpected tar member", last)

    def test_duplicate_member_refuses(self):
        self.ok_remote()
        rewrite_tar(os.path.join(self.t.out, "fetch.tar"), lambda ms: ms + [ms[0]])
        self.assertEqual(self.t.verify()[0], 9)

    def test_moved_atime_refuses(self):
        self.ok_remote()
        def mut(ms):
            out = []
            for m, b in ms:
                if m.name == "MANIFEST.tsv":
                    lines = b.decode().splitlines()
                    p = lines[5].split("\t")
                    p[4] = str(int(p[4]) + 1)
                    lines[5] = "\t".join(p)
                    b = ("\n".join(lines) + "\n").encode()
                out.append((m, b))
            return out
        rewrite_tar(os.path.join(self.t.out, "fetch.tar"), mut)
        rc, last = self.t.verify()
        self.assertEqual(rc, 9)
        self.assertIn("atime moved", last)

    def test_failed_done_marker_refuses(self):
        p = os.path.join(self.t.units, "c2_replica_b42.done")
        d = json.load(open(p))
        d["verdict"] = "FAIL"
        open(p, "w").write(json.dumps(d))
        self.ok_remote()
        rc, last = self.t.verify()
        self.assertEqual(rc, 9)
        self.assertIn("c2_replica_b42", last)

    def test_done_sha_mismatch_refuses(self):
        p = os.path.join(self.t.units, "c2_replica_b9.done")
        d = json.load(open(p))
        d["sha256"] = "0" * 64
        open(p, "w").write(json.dumps(d))
        self.ok_remote()
        self.assertEqual(self.t.verify()[0], 9)

    def test_central_sha_mismatch_refuses(self):
        self.ok_remote()
        self.t.central = "f" * 64
        rc, last = self.t.verify()
        self.assertEqual(rc, 9)
        self.assertIn("committed one", last)

    def test_listing_size_mismatch_refuses(self):
        with open(self.t.listing) as f:
            lines = f.readlines()
        size, p = lines[10].split()
        lines[10] = "%d %s\n" % (int(size) + 1, p)
        with open(self.t.listing, "w") as f:
            f.writelines(lines)
        self.ok_remote()
        rc, last = self.t.verify()
        self.assertEqual(rc, 9)
        self.assertIn("committed listing", last)

    def test_wrong_ks_refuses(self):
        n = "c2_replica_b3"
        b = npz_bytes(n, ks=[1, 2, 3, 4, 5, 10, 15, 25])
        open(os.path.join(self.t.units, n + ".npz"), "wb").write(b)
        open(os.path.join(self.t.units, n + ".done"), "w").write(
            json.dumps({"unit": n, "verdict": "PASS", "sha256": sha(b)}))
        self.ok_remote()
        rc, last = self.t.verify()
        self.assertEqual(rc, 9)
        self.assertIn("ks", last)

    def test_nonfinite_xsec_refuses(self):
        n = "c2_replica_b4"
        buf = io.BytesIO()
        x = np.ones((8, 224))
        x[5, 17] = np.nan
        np.savez_compressed(buf, ks=np.array(KS), xsec=x, meta="{}")
        b = buf.getvalue()
        open(os.path.join(self.t.units, n + ".npz"), "wb").write(b)
        open(os.path.join(self.t.units, n + ".done"), "w").write(
            json.dumps({"unit": n, "verdict": "PASS", "sha256": sha(b)}))
        self.ok_remote()
        self.assertEqual(self.t.verify()[0], 9)

    def test_existing_files_dir_refuses(self):
        self.ok_remote()
        os.mkdir(os.path.join(self.t.out, "files"))
        self.assertEqual(self.t.verify()[0], 9)


class Wrapper(unittest.TestCase):
    def run_w(self, *args):
        r = subprocess.run(["bash", WRAPPER, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return r.returncode, r.stdout.decode()

    def test_check_only_passes_local_gates_and_never_connects(self):
        out = os.path.join(tempfile.mkdtemp(prefix="c2eff-w-"), "o")
        rc, txt = self.run_w(out, "--check-only")
        self.assertEqual(rc, 0, txt)
        self.assertIn("check-only: every local gate passed; no connect made", txt)
        self.assertFalse(os.path.exists(out))

    def test_unknown_mode_refuses(self):
        rc, txt = self.run_w("/nonexistent/o", "--go")
        self.assertEqual(rc, 2)

    def test_tampered_helper_refuses(self):
        d = tempfile.mkdtemp(prefix="c2eff-w-")
        for f in (WRAPPER, REMOTE, VERIFY):
            shutil.copy(f, d)
        with open(os.path.join(d, "c2_fetch_remote.py"), "a") as f:
            f.write("\n# tampered\n")
        r = subprocess.run(["bash", os.path.join(d, "c2_fetch.sh"), os.path.join(d, "o"), "--check-only"],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(r.returncode, 3)
        self.assertIn("c2_fetch_remote.py is not", r.stdout.decode())


if __name__ == "__main__":
    unittest.main(verbosity=2)
