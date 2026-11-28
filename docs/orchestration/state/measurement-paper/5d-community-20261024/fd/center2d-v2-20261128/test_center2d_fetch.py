"""Tests for the CENTER2D fetch: the remote reader on a fake tree (O_NOATIME injected by the harness only, since macOS has
none, and the 16 paths re-rooted into a temp dir), the verifier, and the wrapper's local gates in --check-only mode.
Nothing here connects anywhere. run: python3 -I -B test_center2d_fetch.py
"""
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REMOTE = os.path.join(HERE, "center2d_fetch_remote.py")
VERIFY = os.path.join(HERE, "center2d_fetch_verify.py")
WRAPPER = os.path.join(HERE, "center2d_fetch.sh")
DRIVER = os.path.join(HERE, "center2d.py")
FENCE = os.path.join(HERE, "center2d_fence.py")
FAMILIES = "cov2d t2a rpd precharge_c geanttw_ oofvc_ covfix_ ibuchi_ ptmc_ rdx_ center2d"
INJECT = ("import os, sys; os.O_NOATIME = 0; ns = {'__name__': 'remote'}; p = %r; "
          "exec(compile(open(p).read(), p, 'exec'), ns); root = sys.argv[1]; "
          "ns['FILES'] = [(n, root + '/' + n) for n, _ in ns['FILES']]; sys.exit(ns['main'](['remote']))" % REMOTE)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def labels():
    ns = {"__name__": "remote"}
    with open(REMOTE) as f:
        exec(compile(f.read(), REMOTE, "exec"), ns)
    return [n for n, _ in ns["FILES"]]


class Tree:
    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="center2d-fetch-")
        self.src = os.path.join(self.root, "src")
        self.exp = {}
        for n in labels():
            p = os.path.join(self.src, n)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            b = os.urandom(200 + len(n))
            with open(p, "wb") as f:
                f.write(b)
            self.exp[n] = sha(b)
        self.expected = os.path.join(self.root, "expected.tsv")
        self.write_expected()
        self.out = os.path.join(self.root, "out")
        os.mkdir(self.out)
        self.freeze_atimes()

    def write_expected(self):
        with open(self.expected, "w") as f:
            f.writelines(f"{n}\t{d}\t/pscratch/x/{n}\n" for n, d in self.exp.items())

    def files(self):
        for d, _, fs in os.walk(self.src):
            for n in fs:
                yield os.path.join(d, n)

    def freeze_atimes(self):
        """Harness only: macOS has no O_NOATIME, so give every file an atime after its mtime (relatime-style hosts then
        leave it alone on a read). The reader's own atime check is unchanged and still runs."""
        for p in self.files():
            st = os.lstat(p)
            os.utime(p, ns=(st.st_mtime_ns + 3600 * 10**9, st.st_mtime_ns), follow_symlinks=False)

    def remote(self, inject=True, argv_extra=()):
        cmd = [sys.executable, "-I", "-B", "-c", INJECT, self.src] if inject else \
            [sys.executable, "-I", "-B", REMOTE, *argv_extra]
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with open(os.path.join(self.out, "fetch.tar"), "wb") as f:
            f.write(r.stdout)
        return r

    def verify(self):
        r = subprocess.run([sys.executable, "-I", "-B", VERIFY, self.out, self.expected],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return r.returncode, r.stdout.decode().strip().splitlines()[-1]

    def close(self):
        shutil.rmtree(self.root)


def rewrite_tar(path, mutate):
    with tarfile.open(path, "r:") as t:
        members = [(m.name, t.extractfile(m).read()) for m in t]
    members = mutate(members)
    with tarfile.open(path, "w:", format=tarfile.PAX_FORMAT) as t:
        for name, b in members:
            ti = tarfile.TarInfo(name)
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
        self.assertEqual(r.stderr.decode().strip().splitlines()[-1], "FETCH-DONE 16 files")

    def test_sixteen_distinct_labels(self):
        self.assertEqual(len(set(labels())), 16)

    def test_good_tree_fetches_and_verifies(self):
        self.ok_remote()
        self.assertEqual(self.t.verify(), (0, "VERIFY OK 16"))
        with open(os.path.join(self.t.out, "SHA256SUMS")) as f:
            rows = [ln.split() for ln in f]
        self.assertEqual(len(rows), 16)
        for d, rel in rows:
            with open(os.path.join(self.t.out, rel), "rb") as f:
                self.assertEqual(sha(f.read()), d)
            self.assertEqual(d, self.t.exp[rel[len("files/"):]])

    def test_no_o_noatime_refuses(self):
        r = self.t.remote(inject=False)
        self.assertEqual(r.returncode, 9)
        self.assertIn("O_NOATIME is not available", r.stderr.decode())

    def test_arguments_refuse(self):
        r = subprocess.run([sys.executable, "-I", "-B", "-c", INJECT.replace("['remote']", "['remote', 'x']"),
                            self.t.src], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(r.returncode, 9)
        self.assertIn("usage", r.stderr.decode())

    def test_a_read_that_moves_atime_is_caught(self):
        for p in self.t.files():
            st = os.lstat(p)
            os.utime(p, ns=(st.st_mtime_ns - 10**9, st.st_mtime_ns))
        r = self.t.remote()
        self.assertEqual(r.returncode, 9)
        self.assertIn("atime moved", r.stderr.decode())
        self.assertNotIn(b"MANIFEST.tsv", r.stdout)

    def test_missing_file_refuses_before_any_tar(self):
        os.remove(os.path.join(self.t.src, "partb", "S3_MuonResolution1.root"))
        r = self.t.remote()
        self.assertEqual(r.returncode, 9)
        self.assertEqual(r.stdout, b"")

    def test_symlink_refuses(self):
        p = os.path.join(self.t.src, "g2r", "data_g2r.npz")
        os.rename(p, p + ".real")
        os.symlink(p + ".real", p)
        r = self.t.remote()
        self.assertEqual(r.returncode, 9)
        self.assertIn("not a regular file", r.stderr.decode())

    def test_empty_file_refuses(self):
        open(os.path.join(self.t.src, "c04", "minos_rescaled.npz"), "wb").close()
        self.assertEqual(self.t.remote().returncode, 9)

    def test_missing_manifest_refuses(self):
        self.ok_remote()
        rewrite_tar(os.path.join(self.t.out, "fetch.tar"), lambda ms: [x for x in ms if x[0] != "MANIFEST.tsv"])
        rc, last = self.t.verify()
        self.assertEqual(rc, 9)
        self.assertIn("no MANIFEST", last)

    def test_tampered_member_refuses(self):
        self.ok_remote()
        rewrite_tar(os.path.join(self.t.out, "fetch.tar"),
                    lambda ms: [(n, (b[:-1] + bytes([b[-1] ^ 1])) if n == "partc/cov2d_Q_205.npz" else b) for n, b in ms])
        rc, last = self.t.verify()
        self.assertEqual(rc, 9)
        self.assertIn("differs from the remote manifest", last)

    def test_committed_digest_mismatch_refuses(self):
        self.ok_remote()
        self.t.exp["g2r/blocks_g2r_G18.npz"] = "f" * 64
        self.t.write_expected()
        rc, last = self.t.verify()
        self.assertEqual(rc, 9)
        self.assertIn("is not the committed", last)

    def test_unexpected_member_refuses(self):
        self.ok_remote()
        rewrite_tar(os.path.join(self.t.out, "fetch.tar"), lambda ms: ms + [("g2r/extra.npz", b"x")])
        rc, last = self.t.verify()
        self.assertEqual(rc, 9)
        self.assertIn("unexpected tar member", last)

    def test_duplicate_member_refuses(self):
        self.ok_remote()
        rewrite_tar(os.path.join(self.t.out, "fetch.tar"), lambda ms: ms + [ms[0]])
        self.assertEqual(self.t.verify()[0], 9)

    def test_moved_atime_in_manifest_refuses(self):
        self.ok_remote()

        def mut(ms):
            out = []
            for n, b in ms:
                if n == "MANIFEST.tsv":
                    lines = b.decode().splitlines()
                    p = lines[5].split("\t")
                    p[4] = str(int(p[4]) + 1)
                    lines[5] = "\t".join(p)
                    b = ("\n".join(lines) + "\n").encode()
                out.append((n, b))
            return out
        rewrite_tar(os.path.join(self.t.out, "fetch.tar"), mut)
        rc, last = self.t.verify()
        self.assertEqual(rc, 9)
        self.assertIn("atime moved", last)

    def test_expected_with_a_path_label_refuses(self):
        self.ok_remote()
        k = next(iter(self.t.exp))
        self.t.exp["../escape"] = self.t.exp.pop(k)
        self.t.write_expected()
        rc, last = self.t.verify()
        self.assertEqual(rc, 9)
        self.assertIn("plain relative name", last)

    def test_short_expected_refuses(self):
        self.ok_remote()
        self.t.exp.pop(next(iter(self.t.exp)))
        self.t.write_expected()
        self.assertEqual(self.t.verify()[0], 9)

    def test_existing_files_dir_refuses(self):
        self.ok_remote()
        os.mkdir(os.path.join(self.t.out, "files"))
        self.assertEqual(self.t.verify()[0], 9)


class Fence(unittest.TestCase):
    """The director's fix: sacct without -s, refusing only on a fenced family's non-terminal State; squeue as is."""

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="center2d-fence-")

    def tearDown(self):
        shutil.rmtree(self.d)

    def fence(self, sacct, squeue=""):
        a, q = os.path.join(self.d, "sacct.txt"), os.path.join(self.d, "squeue.txt")
        with open(a, "w") as f:
            f.write(sacct)
        with open(q, "w") as f:
            f.write(squeue)
        r = subprocess.run([sys.executable, "-I", "-B", FENCE, FAMILIES, a, q], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        return r.returncode, r.stdout.decode().strip()

    def test_completed_oofvc_row_clears(self):
        self.assertEqual(self.fence("61990001|oofvc_r2_a|COMPLETED\n"), (0, "0"))

    def test_every_terminal_state_clears(self):
        rows = "".join(f"{i}|oofvc_x|{s}\n" for i, s in enumerate(
            ("COMPLETED", "FAILED", "CANCELLED", "CANCELLED by 12345", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL",
             "PREEMPTED", "BOOT_FAIL", "DEADLINE", "REVOKED")))
        self.assertEqual(self.fence(rows), (0, "0"))

    def test_running_or_pending_refuses(self):
        for st in ("RUNNING", "PENDING", "REQUEUED", "SUSPENDED", "COMPLETING"):
            self.assertEqual(self.fence(f"1|oofvc_r3|{st}\n"), (0, "1"), st)

    def test_unknown_state_refuses(self):
        self.assertEqual(self.fence("1|covfix_p1|SOMETHING_NEW\n"), (0, "1"))

    def test_family_match_is_case_insensitive_and_by_prefix(self):
        self.assertEqual(self.fence("1|COV2Dg2r-AR23|RUNNING\n"), (0, "1"))
        self.assertEqual(self.fence("1|xcov2d|RUNNING\n"), (0, "0"))

    def test_other_families_do_not_refuse(self):
        self.assertEqual(self.fence("1|evw5d_r2|RUNNING\n2|lgbm42|PENDING\n"), (0, "0"))

    def test_squeue_row_of_a_family_refuses_whatever_its_state(self):
        self.assertEqual(self.fence("", "77|ibuchi_x|PENDING\n"), (0, "1"))
        self.assertEqual(self.fence("", "77|other|RUNNING\n"), (0, "0"))
        self.assertEqual(self.fence("", "78|oofvc_x|COMPLETED\n"), (0, "1"))

    def test_malformed_row_refuses(self):
        self.assertEqual(self.fence("garbage\n"), (0, "1"))

    def test_unreadable_input_fails_closed(self):
        r = subprocess.run([sys.executable, "-I", "-B", FENCE, FAMILIES, os.path.join(self.d, "none"),
                            os.path.join(self.d, "none")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), b"")

    def test_wrapper_families_equal_the_tested_ones(self):
        with open(WRAPPER) as f:
            text = f.read()
        line = [ln for ln in text.splitlines() if ln.startswith("FAMILIES=")][0]
        self.assertEqual(line.strip(), f'FAMILIES="{FAMILIES}"')
        self.assertNotIn(" -s ", text.split("sacct -X", 1)[1].split("\n", 1)[0])


class Wrapper(unittest.TestCase):
    def run_w(self, *args, wrapper=WRAPPER):
        r = subprocess.run(["bash", wrapper, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return r.returncode, r.stdout.decode()

    def test_check_only_passes_local_gates_and_never_connects(self):
        out = os.path.join(tempfile.mkdtemp(prefix="center2d-w-"), "o")
        rc, txt = self.run_w(out, "--check-only")
        if rc == 4:
            self.skipTest(f"the NERSC cert gate refused (rc 4), so the cert, not the code, decided: {txt.strip()}")
        self.assertEqual(rc, 0, txt)
        self.assertIn("local gates passed", txt)
        self.assertIn("check-only: every local gate passed; no connect made", txt)
        self.assertFalse(os.path.exists(out))

    def test_unknown_mode_refuses(self):
        self.assertEqual(self.run_w("/nonexistent/o", "--go")[0], 2)

    def test_too_many_arguments_refuse(self):
        self.assertEqual(self.run_w("/nonexistent/o", "--check-only", "x")[0], 2)

    def test_tampered_helper_refuses(self):
        for name in ("center2d_fetch_remote.py", "center2d_fetch_verify.py", "center2d_fence.py", "center2d.py"):
            d = tempfile.mkdtemp(prefix="center2d-w-")
            for f in (WRAPPER, REMOTE, VERIFY, FENCE, DRIVER):
                shutil.copy(f, d)
            with open(os.path.join(d, name), "a") as f:
                f.write("\n# tampered\n")
            rc, txt = self.run_w(os.path.join(d, "o"), "--check-only", wrapper=os.path.join(d, "center2d_fetch.sh"))
            self.assertEqual(rc, 3, txt)
            self.assertIn(f"{name} is not", txt)
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main(verbosity=2)
