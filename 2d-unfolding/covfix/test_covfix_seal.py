"""Tests for covfix_seal, covfix_pg and covfix_sealcheck (COVFIX-DECLARATION.md rev 11.4 section 4.2). Real gpg on
synthetic files; a fake generator stands in for tune-generator's command. No secret of the study is used.

  python3 -B -m unittest -v test_covfix_seal.py
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import covfix_pg as pg
import covfix_seal as cs
import covfix_sealcheck as sc

PW = "a" * 64                      # a synthetic passphrase
BASE = 1_234_567_890
FRAME = f"{PW}\n{BASE}\n".encode()
ATT = "0123456789abcdef0123456789abcdef"
GPG, GPGCONF = os.path.realpath(shutil.which("gpg")), os.path.realpath(shutil.which("gpgconf"))


def fsha(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tools(gpg=GPG, gpgconf=GPGCONF):
    return cs.Tools(gpg, gpgconf, fsha(gpg), fsha(gpgconf))


TOOLS = tools()
DECLARED_ENCRYPT = ("gpg --batch --yes --pinentry-mode loopback --passphrase-fd 3 --no-symkey-cache --symmetric "
                    "--cipher-algo AES256 --s2k-digest-algo SHA512 --force-mdc --compress-algo none")
DECLARED_DECRYPT = "gpg --batch --pinentry-mode loopback --passphrase-fd 3 --no-symkey-cache --decrypt"
SEED_RANGE = (1_000_000_000, 2_000_020_063)

GEN = r'''#!{py}
import json, os, sys, time
a = sys.argv
w = a[a.index("--workdir") + 1]
seeds = json.load(open(a[a.index("--seeds") + 1]))
mode = os.environ.get("FAKE_MODE", "ok")
open(os.path.join(w, "marker"), "w").write("ran")
os.makedirs(os.path.join(w, "out", "G21"), exist_ok=True)
open(os.path.join(w, "out", "G21", "ratio.json"), "w").write(json.dumps({{"f_MEC": 0.1234, "k": 1.07}}))
open(os.path.join(w, "env.json"), "w").write(json.dumps(sorted(os.environ)))
open(os.path.join(w, "tmpdir.txt"), "w").write(os.environ.get("TMPDIR", ""))
open(os.path.join(w, "seen_seeds.json"), "w").write(json.dumps(seeds))
open(os.path.join(w, "genie-mcjob-%d.status" % seeds["tunes"][1]["task_seeds"][6]), "w").write("done")
print("convert: f_MEC=0.1234 p=0.5 n_in_grid=42")
print("gevgen log line", file=sys.stderr)
products = {{"ok": ["out/G21/ratio.json"], "noproducts": None, "emptyproducts": [], "missingproduct": ["out/none"],
             "unsafeproduct": ["../x"], "dupproducts": ["out/G21/ratio.json", "out/G21/ratio.json"],
             "captureproduct": ["capture/stdout.log"]}}.get(mode, ["out/G21/ratio.json"])
if products is not None:
    open(os.path.join(w, "PRODUCTS.json"), "w").write(json.dumps(products))
tmp = os.path.join(os.environ.get("SPILL_ROOT", "/nonexistent"), "tmp")
if mode in ("leak", "faileak"):
    open(os.path.join(tmp, "leak.json"), "w").write(open(os.path.join(w, "out", "G21", "ratio.json")).read())
if mode == "benign":
    open(os.path.join(tmp, "harmless.log"), "w").write("nothing secret")
if mode == "seedleak":
    open(os.path.join(tmp, "old", "deep.log"), "w").write("seed %d" % seeds["tunes"][0]["task_seeds"][0])
if mode == "symlink":
    os.symlink("/etc/hosts", os.path.join(w, "link"))
if mode == "tmpmode":                  # pg_generate.sh's own check (lines 59-61): a real dir of this user's, mode 0700
    import stat
    st = os.lstat(os.environ["TMPDIR"])
    open(os.path.join(w, "tmpmode.json"), "w").write(json.dumps({{"dir": stat.S_ISDIR(st.st_mode),
        "mode": oct(stat.S_IMODE(st.st_mode)), "own": st.st_uid == os.getuid()}}))
if mode == "envset":
    open(os.path.join(w, "envset.json"), "w").write(json.dumps({{k: os.environ.get(k) for k in ("PG_DEPLOY_PIN", "COVFIX_TEST_SET")}}))
if mode == "mutate":
    open(sys.argv[0], "a").write("\n# changed\n")
if mode == "seeddir":
    dn = os.path.join(tmp, "run-%d" % seeds["tunes"][0]["task_seeds"][1], "inner")
    os.makedirs(dn)
    open(os.path.join(dn, "a.log"), "w").write("benign")
if mode == "seedlink":
    os.symlink("/nonexistent/%d" % seeds["tunes"][1]["task_seeds"][2], os.path.join(tmp, "plain-link"))
if mode == "sumsleak":                            # a sums file in $SCRATCH/tmp: a plaintext hash, no seed
    import hashlib
    r = open(os.path.join(w, "out", "G21", "ratio.json"), "rb").read()
    open(os.path.join(tmp, "PG-SHA256SUMS"), "w").write(hashlib.sha256(r).hexdigest() + "  ratio\n")
if mode == "orphan":
    import subprocess as sp
    sp.Popen([sys.executable, "-c", "import time, sys; time.sleep(1.5); open(sys.argv[1], 'w').write('late')",
              os.path.join(tmp, "late.txt")])
if mode == "overwritekeep":                       # same length, mtime restored: only ctime moves
    pre = os.path.join(tmp, "old", "pre.txt")
    st0 = os.stat(pre)
    open(pre, "w").write("s=%d" % seeds["tunes"][0]["task_seeds"][3])
    os.utime(pre, ns=(st0.st_atime_ns, st0.st_mtime_ns))
if mode == "lockedonly":                          # an unlistable directory and nothing else
    os.mkdir(os.path.join(tmp, "a-lockdir"))
    os.chmod(os.path.join(tmp, "a-lockdir"), 0)
if mode in ("unreadable", "unlistable"):
    if mode == "unreadable":
        open(os.path.join(tmp, "a-locked.bin"), "w").write("x")
        os.chmod(os.path.join(tmp, "a-locked.bin"), 0)
    else:
        os.mkdir(os.path.join(tmp, "a-lockdir"))
        os.chmod(os.path.join(tmp, "a-lockdir"), 0)
    open(os.path.join(tmp, "z-leak.txt"), "w").write("seed %d" % seeds["tunes"][1]["task_seeds"][4])
sys.exit(3 if mode in ("fail", "faileak") else 0)
'''


def write_gen(d: Path) -> Path:
    p = d / "gen.py"
    p.write_text(GEN.format(py=sys.executable))
    p.chmod(p.stat().st_mode | stat.S_IXUSR)
    return p


REQUIRED = [{"pattern": "out/G21/ratio.json", "count": 1}, {"pattern": "genie-mcjob-*.status", "count": 1}]


def write_spec(d: Path, gen: Path, sha: str | None = None, env_keep=("FAKE_MODE", "PATH", "SPILL_ROOT"),
               command0: str | None = None, required=None, env_set=None) -> Path:
    s = d / "spec.json"
    s.write_text(json.dumps({"command": [command0 or str(gen)],
                             "command_sha256": sha or hashlib.sha256(gen.read_bytes()).hexdigest(),
                             "tunes": ["G21_11a_00_000", "G18_02a_00_000"], "env_keep": list(env_keep),
                             "env_set": {} if env_set is None else env_set,
                             "required": REQUIRED if required is None else required}))
    return s


JOB_CG = "system.slice/slurmstepd.scope/job_1"


def fake_step(d: Path, extra_pids=(), cgroup_line="0::/" + JOB_CG + "/step_0/user/task_0", readable=True, others=None,
              parent_ppid=1):
    """A fake /proc and /sys/fs/cgroup in Slurm's cgroup v2 layout. The sealer's task cgroup (job_1/step_0/user/task_0)
    holds this process, its parent and any extra pids (an int, parent pid 1, or (pid, parent pid)). `others` maps a
    cgroup path under job_1 to such pids; None there makes a directory with no readable cgroup.procs."""
    proc, cg = d / "fakeproc", d / "fakecgroup"
    me, parent = os.getpid(), os.getppid()

    def put(pid, ppid, comm):
        (proc / str(pid)).mkdir(parents=True, exist_ok=True)
        (proc / str(pid) / "stat").write_text(f"{pid} (a b) S {ppid} 0 0\n")
        (proc / str(pid) / "comm").write_text(comm + "\n")
        if not os.path.lexists(proc / str(pid) / "exe"):
            os.symlink(f"/fake/bin/{comm}", proc / str(pid) / "exe")
        return pid

    def pids(xs):
        return [put(*(x if isinstance(x, tuple) else (x, 1)), "gevgen") for x in xs]

    put(me, parent, "python3")
    put(parent, parent_ppid, "sh")
    (proc / "self").mkdir(exist_ok=True)
    (proc / "self" / "cgroup").write_text(cgroup_line + "\n")
    own = cg / JOB_CG / "step_0" / "user" / "task_0"
    own.mkdir(parents=True, exist_ok=True)
    if readable:
        (own / "cgroup.procs").write_text("".join(f"{p}\n" for p in (me, parent, *pids(extra_pids))))
    for rel, xs in (others or {}).items():
        (cg / JOB_CG / rel).mkdir(parents=True, exist_ok=True)
        if xs is not None:
            (cg / JOB_CG / rel / "cgroup.procs").write_text("".join(f"{p}\n" for p in pids(xs)))
    for dirpath, _dirs, files in os.walk(cg / JOB_CG):              # every other cgroup dir has its (empty) procs
        if "cgroup.procs" not in files and Path(dirpath) != own and \
                os.path.relpath(dirpath, cg / JOB_CG) not in {k for k, v in (others or {}).items() if v is None}:
            (Path(dirpath) / "cgroup.procs").write_text("")
    return proc, cg


def published_problems(text: str, rels: list[str]) -> list[str]:
    """Any given path component, or any decimal token in the seed range, in published text."""
    comps = {c for r in rels for c in r.split("/")}
    out = []
    for tok in re.findall(r"[A-Za-z0-9_.\-]+", text):
        if tok in comps or tok.removesuffix(".gpg") in comps:
            out.append(f"path component {tok}")
    for m in re.finditer(r"(?<![0-9a-f])[0-9]{10}(?![0-9a-f])", text):
        if SEED_RANGE[0] <= int(m.group()) <= SEED_RANGE[1]:
            out.append(f"seed-range decimal {m.group()}")
    return out


def fake_tool(d: Path, body: str, name: str = "faketool.py") -> str:
    p = d / name
    p.write_text(f"#!{sys.executable}\n{body}")
    p.chmod(0o755)
    return os.path.realpath(p)


class Frame(unittest.TestCase):
    def test_pg_frame(self):
        self.assertEqual(cs.read_frame(FRAME, True), (PW, BASE))
        self.assertEqual(len(FRAME), cs.PG_FRAME_LEN)

    def test_pg_frame_refusals(self):
        for bad in (f"{PW.upper()}\n{BASE}\n", f"{PW}\n{BASE}", f"{PW}\n{BASE}\n\n", f"{PW}\n0{BASE}\n",
                    f"{PW[:-1]}\n{BASE}\n", f"{PW}\n999999999\n", f"{PW}\n2000000000\n", f"{PW}\n",
                    f"{PW}\n{BASE}0\n", f"{PW}\n{BASE}\n" + "x" * 100):
            with self.subTest(bad=bad[-14:]), self.assertRaises(cs.Refusal):
                cs.read_frame(bad.encode(), True)

    def test_pv_frame(self):
        self.assertEqual(cs.read_frame(f"{PW}\n".encode(), False), (PW, None))
        with self.assertRaises(cs.Refusal):
            cs.read_frame(FRAME, False)

    def test_seed_range_edges(self):
        self.assertEqual(cs.read_frame(f"{PW}\n1000000000\n".encode(), True)[1], 1_000_000_000)
        self.assertEqual(cs.read_frame(f"{PW}\n1999999999\n".encode(), True)[1], 1_999_999_999)


class Seeds(unittest.TestCase):
    def test_formula_and_alias(self):
        s = cs.task_seeds(BASE, ["A", "B"])["tunes"]
        self.assertEqual([t["u"] for t in s], [0, 1])
        self.assertEqual(s[0]["task_seeds"], [BASE + i for i in range(7)])
        self.assertEqual(s[0]["task_seeds"][0], BASE)                     # the declared alias (ruling on B1)
        self.assertEqual(s[1]["task_seeds"], [BASE + 10_000 + i for i in range(7)])

    def test_declared_maximum_is_below_the_limit(self):
        top = cs.task_seeds(1_999_999_999, ["A", "B"])["tunes"][1]["task_seeds"][-1]
        self.assertEqual(top, 2_000_010_005)
        self.assertLess(top, 2 ** 31 - 1)

    def test_limit_refused(self):
        with self.assertRaises(cs.Refusal):
            cs.task_seeds(2 ** 31 - 1 - 10_006, ["A", "B"])
        cs.task_seeds(2 ** 31 - 1 - 10_007, ["A", "B"])


class Gpg(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.d = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def test_declared_flags(self):
        self.assertEqual(" ".join(cs.GPG_ENCRYPT), DECLARED_ENCRYPT)
        self.assertEqual(" ".join(cs.GPG_DECRYPT), DECLARED_DECRYPT)

    def test_tools_must_be_absolute_executables(self):
        link = os.path.join(os.path.realpath(self.d), "gpg-link")
        os.symlink(GPG, link)                                              # the last component a link
        dlink = os.path.join(os.path.realpath(self.d), "bin-link")
        os.symlink(os.path.dirname(GPG), dlink)                            # a linked parent: O_NOFOLLOW cannot see it
        via = os.path.join(dlink, os.path.basename(GPG))
        cs.Tools(GPG, GPGCONF, fsha(GPG), fsha(GPGCONF))                    # the right pins: only the path can refuse
        for g in ("gpg", "/nonexistent/gpg", str(self.d), os.path.relpath(GPG), link, via):
            with self.subTest(g=g), self.assertRaises(cs.Refusal):
                cs.Tools(g, GPGCONF, fsha(GPG), fsha(GPGCONF))

    def test_tools_are_pinned_and_verified_before_every_exec(self):
        with self.assertRaises(cs.Refusal):
            cs.Tools(GPG, GPGCONF, "0" * 64, fsha(GPGCONF))                # a wrong pin: a STOP
        with self.assertRaises(cs.Refusal):
            cs.Tools(GPG, GPGCONF, fsha(GPG), "A" * 64)                    # a malformed pin
        with self.assertRaises(cs.Refusal):
            cs.Tools(GPG, GPG, fsha(GPG), fsha(GPG))                        # the same file twice
        link = self.d / "gpglink"
        link.symlink_to(GPG)
        with self.assertRaises(cs.Refusal):
            cs.Tools(str(link), GPGCONF, fsha(GPG), fsha(GPGCONF))          # not a resolved path
        g = fake_tool(self.d, "import sys\nsys.exit(0)\n", "fakegpg.py")
        t = tools(gpg=g)
        Path(g).write_text(Path(g).read_text() + "# changed after binding\n")
        with self.assertRaises(cs.Refusal) as e:
            cs.gpg_run(cs.GPG_ENCRYPT, PW, b"x", t)                       # re-hashed before the exec
        self.assertIn("pinned", str(e.exception))
        c = fake_tool(self.d, "import sys\nsys.exit(0)\n", "fakeconf.py")
        t = tools(gpgconf=c)
        Path(c).write_text(Path(c).read_text() + "# changed\n")
        with self.assertRaises(cs.Refusal) as e:
            cs.gpg_run(cs.GPG_ENCRYPT, PW, b"x", t)                       # gpgconf too: shutdown not confirmed
        self.assertIn("shutdown", str(e.exception))

    def test_round_trip_and_wrong_passphrase(self):
        ct = cs.gpg_run(cs.GPG_ENCRYPT, PW, b"payload", TOOLS)
        self.assertNotIn(b"payload", ct)
        self.assertEqual(cs.gpg_run(cs.GPG_DECRYPT, PW, ct, TOOLS), b"payload")
        with self.assertRaises(cs.Refusal):
            cs.gpg_run(cs.GPG_DECRYPT, "b" * 64, ct, TOOLS)

    def test_tampered_ciphertext_refused(self):
        ct = bytearray(cs.gpg_run(cs.GPG_ENCRYPT, PW, b"payload" * 100, TOOLS))
        ct[-5] ^= 0xFF
        with self.assertRaises(cs.Refusal):
            cs.gpg_run(cs.GPG_DECRYPT, PW, bytes(ct), TOOLS)

    def test_child_sees_exactly_fds_0_to_3_no_core_and_minimal_env(self):
        tool = fake_tool(self.d, "import os, resource, json, sys\n"
                                 "fds = []\nfor i in range(256):\n"
                                 "    try:\n        os.fstat(i); fds.append(i)\n    except OSError:\n        pass\n"
                                 "pw = os.read(3, 100)\n"
                                 "sys.stdout.write(json.dumps({'fds': fds, 'core': resource.getrlimit(resource.RLIMIT_CORE),"
                                 " 'env': sorted(os.environ), 'pw': pw.decode()}))\n")
        r, w = os.pipe()
        os.set_inheritable(r, True)
        os.set_inheritable(w, True)
        import resource
        soft, hard = resource.getrlimit(resource.RLIMIT_CORE)
        raised = hard == resource.RLIM_INFINITY or hard > 0
        if raised:
            resource.setrlimit(resource.RLIMIT_CORE, (1 << 20 if hard == resource.RLIM_INFINITY else hard, hard))
        try:
            out = json.loads(cs.gpg_run(cs.GPG_DECRYPT, PW, b"", tools(gpg=tool)))
        finally:
            os.close(r)
            os.close(w)
            resource.setrlimit(resource.RLIMIT_CORE, (soft, hard))
        self.assertEqual(out["fds"], [0, 1, 2, 3])
        self.assertEqual(out["core"], [0, 0])
        self.assertEqual(out["pw"], PW + "\n")
        self.assertTrue(set(out["env"]) <= {"PATH", "LC_ALL", "GNUPGHOME", "LC_CTYPE", "__CF_USER_TEXT_ENCODING"})

    def test_passphrase_pipe_on_fd_3(self):
        saved = os.dup(3) if self._fd_open(3) else None
        try:
            if saved is not None:
                os.close(3)
            ct = cs.gpg_run(cs.GPG_ENCRYPT, PW, b"fd3", TOOLS)            # os.pipe() now returns fd 3
            self.assertEqual(cs.gpg_run(cs.GPG_DECRYPT, PW, ct, TOOLS), b"fd3")
        finally:
            if saved is not None:
                os.dup2(saved, 3)
                os.close(saved)

    @staticmethod
    def _fd_open(fd):
        try:
            os.fstat(fd)
            return True
        except OSError:
            return False

    def test_gnupg_home_short_node_local_and_removed(self):
        made = []
        real = cs.new_gnupg_home

        def spy():
            h = real()
            made.append((h, stat.S_IMODE(os.stat(h).st_mode)))
            return h
        with tempfile.TemporaryDirectory() as home, \
                mock.patch.dict(os.environ, {"HOME": home, "TMPDIR": "/" + "x" * 120}), \
                mock.patch.object(cs, "new_gnupg_home", spy):
            cs.gpg_run(cs.GPG_DECRYPT, PW, cs.gpg_run(cs.GPG_ENCRYPT, PW, b"p", TOOLS), TOOLS)
            self.assertFalse(os.path.exists(os.path.join(home, ".gnupg")))
        for h, mode in made:
            self.assertLess(len(h), 80)
            self.assertEqual(mode, 0o700)
            self.assertTrue(h.startswith(("/dev/shm/", "/tmp/")))
            self.assertFalse(os.path.exists(h))

    def test_home_under_scratch_refused(self):
        with mock.patch.dict(os.environ, {"SCRATCH": "/"}), self.assertRaises(cs.Refusal):
            cs.new_gnupg_home()

    def test_long_home_refused(self):
        with mock.patch.object(cs.tempfile, "mkdtemp", return_value="/tmp/" + "y" * 80), \
                mock.patch.object(cs.os, "chmod"), mock.patch.object(cs.shutil, "rmtree") as rm:
            with self.assertRaises(cs.Refusal):
                cs.new_gnupg_home()
            rm.assert_called_once()

    def test_cleanup_survives_a_gpgconf_failure_and_unconfirmed_shutdown_or_removal_fails(self):
        homes = []
        real = cs.new_gnupg_home

        def spy():
            homes.append(real())
            return homes[-1]

        bad = tools(gpgconf=fake_tool(self.d, "import sys\nsys.exit(5)\n"))
        with mock.patch.object(cs, "new_gnupg_home", spy):
            with self.assertRaises(cs.Refusal) as e:
                cs.gpg_run(cs.GPG_ENCRYPT, PW, b"x", bad)                 # gpgconf exits 5: removed, then refused
            self.assertIn("shutdown", str(e.exception))
            with mock.patch.object(cs.subprocess, "run", side_effect=OSError("no gpgconf")), \
                    self.assertRaises(cs.Refusal) as e:
                cs.gpg_run(cs.GPG_ENCRYPT, PW, b"y", TOOLS)              # a launch error: removed, then refused
            self.assertIn("shutdown", str(e.exception))
        self.assertTrue(homes and not any(os.path.lexists(h) for h in homes))
        with mock.patch.object(cs.shutil, "rmtree"), self.assertRaises(cs.Refusal) as e:
            cs.gpg_run(cs.GPG_ENCRYPT, PW, b"z", TOOLS)
        self.assertIn("could not be removed", str(e.exception))

    def test_a_chmod_failure_still_removes_the_home(self):
        made = []
        real = cs.tempfile.mkdtemp

        def mk(*a, **k):
            made.append(real(*a, **k))
            return made[-1]

        with mock.patch.object(cs.tempfile, "mkdtemp", mk), \
                mock.patch.object(cs.os, "chmod", side_effect=PermissionError("no")), self.assertRaises(OSError):
            cs.new_gnupg_home()
        self.assertTrue(made and not os.path.lexists(made[0]))
        stuck = self.d / "stuck-home"
        stuck.mkdir()
        with mock.patch.object(cs.tempfile, "mkdtemp", return_value=str(stuck)), \
                mock.patch.object(cs.os, "chmod", side_effect=PermissionError("no")), \
                mock.patch.object(cs.shutil, "rmtree"), self.assertRaises(cs.Refusal) as e:
            cs.new_gnupg_home()                                           # a failure, and the home cannot be removed
        self.assertIn("could not be removed", str(e.exception))

    def test_an_unreadable_tool_is_refused(self):
        copy = self.d / "gpg-copy"
        shutil.copy2(GPG, copy)
        copy = os.path.realpath(copy)
        t = cs.Tools(copy, GPGCONF, fsha(copy), fsha(GPGCONF))
        os.chmod(copy, 0o100)                                             # executable, not readable
        try:
            with self.assertRaises(cs.Refusal) as e:
                t.verify(copy)
            self.assertIn("cannot be read", str(e.exception))
        finally:
            os.chmod(copy, 0o700)


class Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.d = Path(self._td.name)
        self.w = self.d / "w"
        self.w.mkdir()
        self.s = self.d / "sealed"

    def tearDown(self):
        for p in self.d.rglob("*"):
            try:
                if not p.is_symlink():
                    p.chmod(0o700)
            except OSError:
                pass
        self._td.cleanup()

    def files(self, **kw):
        for rel, data in kw.items():
            p = self.w / rel.replace("__", "/")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)


class Seal(Base):
    def test_seal_layout_manifest_and_seal_file(self):
        self.files(a=b"alpha", sub__b=b"beta")
        r = cs.seal(self.w, self.s, PW, TOOLS)
        self.assertEqual(r["n_products"], 2)
        self.assertEqual(list(r["hashes"]), ["p0001", "p0002"])
        man = json.loads(cs.gpg_run(cs.GPG_DECRYPT, PW, (self.s / "PG-MANIFEST.json.gpg").read_bytes(), TOOLS))
        self.assertEqual(man["products"], r["hashes"])
        self.assertEqual(sorted(man["paths"]), ["p0001", "p0002"])          # ids over a random permutation
        self.assertEqual({man["paths"][i]: h for i, h in r["hashes"].items()},
                         {"a": hashlib.sha256(b"alpha").hexdigest(), "sub/b": hashlib.sha256(b"beta").hexdigest()})
        for name, want in man["products"].items():                        # the reference role's loop
            plain = cs.gpg_run(cs.GPG_DECRYPT, PW, (self.s / (name + ".gpg")).read_bytes(), TOOLS)
            self.assertEqual(hashlib.sha256(plain).hexdigest(), want)
        text = (self.s / "PG-SEAL.sha256").read_text()
        self.assertEqual(text, r["seal_text"])
        self.assertEqual([ln.split("  ", 1)[1] for ln in text.splitlines()],
                         sorted(["p0001.gpg", "p0002.gpg", "PG-MANIFEST.json.gpg"]))
        self.assertEqual(sorted(os.listdir(self.s)), sorted(["p0001.gpg", "p0002.gpg", "PG-MANIFEST.json.gpg",
                                                             "PG-SEAL.sha256"]))
        self.assertNotIn(r["hashes"]["p0001"], text)
        self.assertEqual(cs.content_scan([self.s], set(r["hashes"].values())), [])
        self.assertTrue(cs.seal_check(self.s, text)["ok"])

    def test_break_on_a_product_round_trip_alone(self):
        self.files(a=b"alpha", b=b"beta")
        real = cs.gpg_run
        calls = {"n": 0}

        def fake(argv, pw, payload, tools):
            out = real(argv, pw, payload, tools)
            if argv is cs.GPG_DECRYPT:
                calls["n"] += 1
                if calls["n"] == 1:
                    return out + b"x"
            return out
        with mock.patch.object(cs, "gpg_run", fake), self.assertRaises(cs.Break):
            cs.seal(self.w, self.s, PW, TOOLS)

    def test_break_on_manifest_mismatch(self):
        self.files(a=b"alpha")
        real = cs.gpg_run
        calls = {"n": 0}

        def fake(argv, pw, payload, tools):
            out = real(argv, pw, payload, tools)
            if argv is cs.GPG_DECRYPT:
                calls["n"] += 1
                if calls["n"] == 2:
                    return out + b" "
            return out
        with mock.patch.object(cs, "gpg_run", fake), self.assertRaises(cs.Break):
            cs.seal(self.w, self.s, PW, TOOLS)

    def test_refusals(self):
        with self.assertRaises(cs.Refusal):
            cs.seal(self.w, self.s, PW, TOOLS)
        os.symlink("/etc/hosts", self.w / "l")
        with self.assertRaises(cs.Refusal) as e:
            cs.seal(self.w, self.d / "s3", PW, TOOLS)
        self.assertNotIn("l", str(e.exception).split())
        with self.assertRaises(cs.Refusal):
            cs.product_ids(10_000)
        self.assertEqual(cs.product_ids(2), ["p0001", "p0002"])

    def test_walk_errors_refuse(self):
        self.files(sub__a=b"x")
        (self.w / "sub").chmod(0)
        try:
            for f in (cs.enumerate_files, lambda p: cs.content_scan([p], set()), cs.delete_plaintext):
                with self.subTest(f=f), self.assertRaises(cs.Refusal):
                    f(self.w)
        finally:
            (self.w / "sub").chmod(0o700)

    def test_a_product_named_like_the_manifest_is_just_an_id(self):
        self.files(**{"PG-MANIFEST.json": b"x"})
        self.assertEqual(list(cs.seal(self.w, self.s, PW, TOOLS)["hashes"]), ["p0001"])

    def test_nothing_published_names_a_path_or_a_seed(self):
        seed = 1_999_999_999 + 10_006
        self.files(**{f"genie-mcjob-{seed}.status": b"s", "G18_02b_02_11b__gntp.1999999999.gst.root": b"g"})
        cs.seal(self.w, self.s, PW, TOOLS)
        rels = cs.enumerate_files(self.w)
        published = (self.s / "PG-SEAL.sha256").read_text() + "\n".join(cs.enumerate_files(self.s))
        self.assertEqual(published_problems(published, rels), [])
        self.assertTrue(published_problems(f"x genie-mcjob-{seed}.status", rels))
        self.assertTrue(published_problems("gntp.1999999999.gst.root", ["gntp.1999999999.gst.root"]))

    def test_existing_ciphertext_not_overwritten(self):
        self.files(a=b"alpha")
        self.s.mkdir()
        (self.s / "p0001.gpg").write_bytes(b"old")
        with self.assertRaises(FileExistsError):
            cs.seal(self.w, self.s, PW, TOOLS)

    def test_delete_plaintext(self):
        self.files(a=b"1", sub__deep__b=b"2")
        os.symlink("/etc/hosts", self.w / "l")
        os.symlink("/etc", self.w / "dl")
        self.assertEqual(cs.delete_plaintext(self.w), 4)
        self.assertEqual(list(self.w.iterdir()), [])
        self.assertTrue(Path("/etc/hosts").exists())

    def test_content_scan(self):
        self.files(a=b"alpha", b=b"beta")
        os.symlink(self.w / "b", self.w / "lnk")
        hits = cs.content_scan([self.w, self.d / "nowhere", self.w / "b"], {hashlib.sha256(b"beta").hexdigest()})
        self.assertEqual(hits, [str(self.w / "b"), str(self.w / "b")])

    def test_regular_read_refuses_a_directory(self):
        with self.assertRaises(cs.Refusal):
            cs.regular_read(self.w)
        (self.s / "sub").mkdir(parents=True)
        with self.assertRaises(cs.Refusal):
            cs._read_in_dir(self.s, "sub")                                # an entry that is a directory

    def test_content_scan_skips_a_special_root(self):
        fifo = self.d / "fifo"
        os.mkfifo(fifo)
        self.assertEqual(cs.content_scan([fifo], {"0" * 64}), [])


class SealCheck(Base):
    def sealed(self):
        self.files(a=b"alpha", b=b"beta")
        return cs.seal(self.w, self.s, PW, TOOLS)["seal_text"]

    def test_ok_missing_extra_mismatched(self):
        text = self.sealed()
        self.assertTrue(cs.seal_check(self.s, text)["ok"])
        (self.s / "p0009.gpg").write_bytes(b"e")
        r = cs.seal_check(self.s, text)
        self.assertEqual((r["ok"], r["extra"], r["extra_other"]), (False, ["p0009.gpg"], 0))
        os.remove(self.s / "p0009.gpg")
        (self.s / "notes.txt").write_text("x")                           # a non-.gpg extra fails too, unnamed
        r = cs.seal_check(self.s, text)
        self.assertEqual((r["ok"], r["extra"], r["extra_other"]), (False, [], 1))
        self.assertNotIn("notes", json.dumps(r))
        os.remove(self.s / "notes.txt")
        (self.s / "p0001.gpg").write_bytes(b"tampered")
        self.assertEqual(cs.seal_check(self.s, text)["mismatched"], ["p0001.gpg"])
        os.remove(self.s / "p0001.gpg")
        self.assertEqual(cs.seal_check(self.s, text)["missing"], ["p0001.gpg"])

    def test_symlinked_or_non_file_entries_fail(self):
        text = self.sealed()
        os.remove(self.s / "p0002.gpg")
        os.symlink(self.s / "p0001.gpg", self.s / "p0002.gpg")
        r = cs.seal_check(self.s, text)
        self.assertEqual((r["ok"], r["missing"], r["extra_other"]), (False, ["p0002.gpg"], 1))
        shutil.rmtree(self.s)
        text = self.sealed_again()
        (self.s / "emptydir").mkdir()                                    # an empty directory is an extra too
        r = cs.seal_check(self.s, text)
        self.assertEqual((r["ok"], r["extra_other"]), (False, 1))
        self.assertNotIn("emptydir", json.dumps(r))

    def sealed_again(self):
        for p in self.w.iterdir():
            p.unlink() if p.is_file() else shutil.rmtree(p)
        return self.sealed()

    def test_the_on_disk_index_must_be_the_seal(self):
        text = self.sealed()
        self.assertTrue(cs.seal_check(self.s, text)["index_ok"])
        (self.s / cs.SEAL_FILE).write_text(text + "\n")
        r = cs.seal_check(self.s, text)
        self.assertEqual((r["ok"], r["index_ok"]), (False, False))
        os.remove(self.s / cs.SEAL_FILE)
        r = cs.seal_check(self.s, text)
        self.assertEqual((r["ok"], r["index_ok"]), (False, False))

    def test_canonical_seal(self):
        h, m = "0" * 64, f"{'0' * 64}  PG-MANIFEST.json.gpg\n"
        for bad in ("nothex  p0001.gpg\n" + m, f"{h}  p0001.gpg\n{h}  p0001.gpg\n" + m, f"{h}  p0001.gpg\n",
                    m, f"{h}  p0002.gpg\n" + m, f"{h}  ../x.gpg\n" + m, f"{h}  p0001.gpg\n{h}  other.gpg\n" + m,
                    f"{h}  p0001\n" + m):
            with self.subTest(bad=bad[:30]), self.assertRaises(cs.Refusal):
                cs.parse_seal(bad)
        self.assertEqual(set(cs.parse_seal(f"{h}  p0001.gpg\n{h}  p0002.gpg\n" + m)),
                         {"p0001.gpg", "p0002.gpg", "PG-MANIFEST.json.gpg"})

    def test_cli(self):
        text = self.sealed()
        sf = self.d / "seal.txt"
        sf.write_text(text)
        sha = hashlib.sha256(text.encode()).hexdigest()
        out = io.StringIO()
        self.assertEqual(sc.main(["--sealed", str(self.s), "--seal-file", str(sf), "--seal-sha256", sha], out), 0)
        self.assertTrue(json.loads(out.getvalue())["ok"])
        out = io.StringIO()
        self.assertEqual(sc.main(["--sealed", str(self.s), "--seal-file", str(sf), "--seal-sha256", "0" * 64], out), 1)
        self.assertIn("pinned", json.loads(out.getvalue())["refused"])
        out = io.StringIO()
        self.assertEqual(sc.main(["--sealed", str(self.s), "--seal-file", str(self.d / "none"), "--seal-sha256", sha],
                                 out), 1)
        self.assertEqual(json.loads(out.getvalue())["refused"], "the seal file or the sealed dir cannot be read")
        bad = self.d / "bad.txt"
        bad.write_text("nonsense\n")
        out = io.StringIO()
        self.assertEqual(sc.main(["--sealed", str(self.s), "--seal-file", str(bad), "--seal-sha256",
                                  hashlib.sha256(b"nonsense\n").hexdigest()], out), 1)
        self.assertIn("malformed", json.loads(out.getvalue())["refused"])
        with self.assertRaises(SystemExit), mock.patch("sys.stderr", io.StringIO()):
            sc.main(["--sealed", str(self.s), "--seal-file", str(sf)], io.StringIO())       # the pin is required
        out = io.StringIO()
        self.assertEqual(sc.main(["--sealed", str(self.s), "--seal-file", str(sf), "--seal-sha256", sha.upper()],
                                 out), 1)


class Reader(Base):
    def sealed(self):
        self.files(a=b"alpha", sub__b=b"beta")
        return cs.parse_seal(cs.seal(self.w, self.s, PW, TOOLS)["seal_text"])

    def test_reads_through_the_seal(self):
        sm = self.sealed()
        man = cs.open_manifest(self.s, sm, PW, TOOLS)
        self.assertEqual(man.ids(), ["p0001", "p0002"])
        by_path = {man.path(i): i for i in man.ids()}                      # ids over a random permutation
        self.assertEqual(sorted(by_path), ["a", "sub/b"])
        self.assertEqual(man.sha256(by_path["sub/b"]), hashlib.sha256(b"beta").hexdigest())
        self.assertEqual(cs.read_product(self.s, sm, man, by_path["sub/b"], PW, TOOLS), b"beta")

    def test_tampered_bytes_break_before_any_decrypt(self):
        sm = self.sealed()
        man = cs.open_manifest(self.s, sm, PW, TOOLS)
        (self.s / "p0001.gpg").write_bytes(b"other bytes")
        with mock.patch.object(cs, "gpg_run") as g, self.assertRaises(cs.Break):
            cs.read_product(self.s, sm, man, "p0001", PW, TOOLS)
        g.assert_not_called()

    def test_missing_is_a_break_unreadable_or_linked_is_a_role_failure(self):
        sm = self.sealed()
        man = cs.open_manifest(self.s, sm, PW, TOOLS)
        os.remove(self.s / "p0001.gpg")
        with self.assertRaises(cs.Break):
            cs.read_product(self.s, sm, man, "p0001", PW, TOOLS)
        p = self.s / "p0002.gpg"
        p.chmod(0)
        try:
            with self.assertRaises(cs.Refusal) as e:
                cs.read_product(self.s, sm, man, "p0002", PW, TOOLS)
            self.assertNotIsInstance(e.exception, cs.Break)
        finally:
            p.chmod(0o600)
        os.rename(p, self.s / "real")
        os.symlink(self.s / "real", p)
        with self.assertRaises(cs.Refusal) as e:
            cs.read_product(self.s, sm, man, "p0002", PW, TOOLS)
        self.assertNotIsInstance(e.exception, cs.Break)

    def test_requests_outside_the_seal_or_manifest_are_role_failures(self):
        sm = self.sealed()
        man = cs.open_manifest(self.s, sm, PW, TOOLS)
        (self.s / "extra.gpg").write_bytes(b"present but unlisted")
        for call in (lambda: cs.read_ciphertext(self.s, sm, "extra.gpg"),
                     lambda: cs.read_product(self.s, sm, man, "p0009", PW, TOOLS)):
            with self.assertRaises(cs.Refusal) as e:
                call()
            self.assertNotIsInstance(e.exception, cs.Break)

    def test_manifest_schema(self):
        sm = self.sealed()
        with self.assertRaises(cs.Refusal):
            cs.open_manifest(self.s, sm, "b" * 64, TOOLS)
        with self.assertRaises(cs.Break):
            cs.open_manifest(self.s, dict(sm, **{"p0003.gpg": "0" * 64}), PW, TOOLS)
        good = {"products": {"p0001": "0" * 64}, "paths": {"p0001": "a"}}
        bads = [b"not json", json.dumps({"products": {}}).encode(), json.dumps([1]).encode(),
                b'{"products": {"p0001": "' + b"0" * 64 + b'"}, "paths": {"p0001": "a"}, "paths": {"p0001": "a"}}',
                json.dumps(dict(good, products=[["p0001", "0" * 64]])).encode(),
                json.dumps(dict(good, products={"p0001": "xyz"})).encode(),
                json.dumps(dict(good, paths={"p0001": "../a"})).encode(),
                json.dumps(dict(good, paths={"p0001": "/abs"})).encode(),
                json.dumps(dict(good, paths={"p0001": "a//b"})).encode(),
                json.dumps(dict(good, paths={"p0001": ""})).encode(),
                json.dumps(dict(good, paths={"p0001": "."})).encode(),
                json.dumps(dict(good, paths={"p0002": "a"})).encode()]
        for i, bad in enumerate(bads):
            with self.subTest(i=i):
                d = self.d / f"m{i}"
                d.mkdir()
                ct = cs.gpg_run(cs.GPG_ENCRYPT, PW, bad, TOOLS)
                (d / "PG-MANIFEST.json.gpg").write_bytes(ct)
                (d / "p0001.gpg").write_bytes(b"c")
                smap = {"PG-MANIFEST.json.gpg": hashlib.sha256(ct).hexdigest(), "p0001.gpg": "0" * 64}
                with self.assertRaises(cs.Break):
                    cs.open_manifest(d, smap, PW, TOOLS)

    def test_duplicate_manifest_paths_break(self):
        man = {"products": {"p0001": "0" * 64, "p0002": "1" * 64}, "paths": {"p0001": "a", "p0002": "a"}}
        ct = cs.gpg_run(cs.GPG_ENCRYPT, PW, json.dumps(man).encode(), TOOLS)
        d = self.d / "dup"
        d.mkdir()
        (d / "PG-MANIFEST.json.gpg").write_bytes(ct)
        smap = {"PG-MANIFEST.json.gpg": hashlib.sha256(ct).hexdigest(), "p0001.gpg": "0" * 64, "p0002.gpg": "0" * 64}
        with self.assertRaises(cs.Break):
            cs.open_manifest(d, smap, PW, TOOLS)

    def test_a_linked_seal_root_or_a_path_name_is_refused(self):
        sm = self.sealed()
        link = self.d / "sealed-link"
        link.symlink_to(self.s)
        with self.assertRaises(cs.Refusal) as e:
            cs.read_ciphertext(link, sm, "p0001.gpg")
        self.assertNotIsInstance(e.exception, cs.Break)
        with self.assertRaises(cs.Refusal):
            cs.read_ciphertext(self.s, dict(sm, **{"../w/a": "0" * 64}), "../w/a")

    def test_an_id_absent_from_the_manifest_is_refused_before_any_read(self):
        sm = self.sealed()
        man = cs.open_manifest(self.s, sm, PW, TOOLS)
        short = cs.SealedManifest({"p0001": man.sha256("p0001")}, {"p0001": man.path("p0001")})
        with mock.patch.object(cs, "read_ciphertext") as rc, mock.patch.object(cs, "gpg_run") as g, \
                self.assertRaises(cs.Refusal) as e:
            cs.read_product(self.s, sm, short, "p0002", PW, TOOLS)
        self.assertNotIsInstance(e.exception, cs.Break)
        rc.assert_not_called()
        g.assert_not_called()

    def test_plaintext_not_its_manifest_hash_is_a_break(self):
        sm = self.sealed()
        man = cs.open_manifest(self.s, sm, PW, TOOLS)
        bad = cs.SealedManifest({"p0001": "0" * 64, "p0002": man.sha256("p0002")},
                                {i: man.path(i) for i in man.ids()})
        with self.assertRaises(cs.Break):
            cs.read_product(self.s, sm, bad, "p0001", PW, TOOLS)


class PGBase(Base):
    def setUp(self):
        super().setUp()
        proc, cg = fake_step(self.d)
        for name, val in (("PROC", str(proc)), ("CGROUP_ROOT", str(cg))):
            pt = mock.patch.object(pg, name, val, create=True)
            pt.start()
            self.addCleanup(pt.stop)
        self.scratch = self.d / "scratch"
        (self.scratch / "tmp" / "old").mkdir(parents=True)
        (self.scratch / "tmp" / "old" / "pre.txt").write_text("pre-existing")

    def go(self, mode="ok", frame=FRAME, sha=None, attempt=ATT, env_keep=("FAKE_MODE", "PATH", "SPILL_ROOT"),
           sealed=None, command0=None, scratch=True, spec=None, workdir=None, spec_sha=None, **env):
        gen = write_gen(self.d)
        spec = spec or write_spec(self.d, gen, sha, env_keep, command0)
        spec_sha = spec_sha or (fsha(spec) if Path(spec).is_file() else "0" * 64)
        out = io.StringIO()
        base_env = {"FAKE_MODE": mode, "SECRETISH": "should-not-pass", "SPILL_ROOT": str(self.scratch)}
        if scratch:
            base_env["SCRATCH"] = str(self.scratch)
        with mock.patch.dict(os.environ, {**base_env, **env}):
            if not scratch:
                os.environ.pop("SCRATCH", None)
            rc = pg.main(["--covfix-attempt", attempt, "--workdir", str(workdir or self.w), "--sealed", str(sealed or self.s),
                          "--gen-spec", str(spec), "--gen-spec-sha256", spec_sha, "--gpg", GPG, "--gpgconf", GPGCONF,
                          "--gpg-sha256", fsha(GPG), "--gpgconf-sha256", fsha(GPGCONF)],
                         stdin=io.BytesIO(frame), stdout=out)
        return rc, out.getvalue()

    def summary(self, out):
        return json.loads(out.splitlines()[0])

    def unseal(self, rel):
        man = json.loads(cs.gpg_run(cs.GPG_DECRYPT, PW, (self.s / "PG-MANIFEST.json.gpg").read_bytes(), TOOLS))
        pid = {v: k for k, v in man["paths"].items()}[rel]
        return cs.gpg_run(cs.GPG_DECRYPT, PW, (self.s / (pid + ".gpg")).read_bytes(), TOOLS)


class PG(PGBase):
    def test_success(self):
        rc, out = self.go()
        self.assertEqual(rc, 0, out)
        lines = out.strip().splitlines()
        self.assertEqual(lines[-1], f"covfix-receipt {ATT}")
        s = self.summary(out)
        for k in ("synthetic_round_trip", "generation_rc0", "command_unchanged", "products_json", "workdir_empty",
                  "final_seal_check", "spills_removed"):
            self.assertIs(s[k], True, k)
        self.assertEqual((s["scratch_spills"], s["sealed_scan_hits"]), (0, 0))
        self.assertIn("task (u=0, i=0) = the seed base", s["seed_alias"])
        for secret in (PW, str(BASE), "f_MEC", "0.1234", "n_in_grid"):
            self.assertNotIn(secret, out)
        self.assertEqual(published_problems(out, ["genie-mcjob-%d.status" % (BASE + 10_006)]), [])
        self.assertEqual(list(self.w.iterdir()), [])
        self.assertIn(b"f_MEC=0.1234", self.unseal("capture/stdout.log"))
        self.assertIn(b"gevgen log line", self.unseal("capture/stderr.log"))
        self.assertEqual(self.unseal("capture/rc.txt"), b"0\n")
        self.assertEqual(json.loads(self.unseal("seeds.json")),
                         cs.task_seeds(BASE, ["G21_11a_00_000", "G18_02a_00_000"]))
        env = json.loads(self.unseal("env.json"))
        self.assertNotIn("SECRETISH", env)
        self.assertNotIn("SCRATCH", env)
        self.assertEqual(self.unseal("tmpdir.txt").decode(), str(Path(os.path.realpath(self.w)) / "tmp"))
        self.assertTrue(set(env) <= {"FAKE_MODE", "PATH", "TMPDIR", "SPILL_ROOT", "LC_CTYPE"}, env)
        self.assertTrue(cs.seal_check(self.s, (self.s / "PG-SEAL.sha256").read_text())["ok"])
        self.assertEqual(published_problems((self.s / "PG-SEAL.sha256").read_text(),
                                            ["genie-mcjob-%d.status" % (BASE + 10_006), "seeds.json", "capture"]), [])

    def test_workdir_left_nonempty_fails(self):
        real = cs.delete_plaintext

        def leave_one(w):
            ok = real(w)
            (Path(w) / "left").write_bytes(b"x")
            return ok

        with mock.patch.object(cs, "delete_plaintext", side_effect=leave_one):
            rc, out = self.go("ok")
        self.assertEqual(rc, 1)
        self.assertNotIn("covfix-receipt", out)
        self.assertFalse(self.summary(out)["workdir_empty"])

    def test_generation_failure_still_seals(self):
        rc, out = self.go("fail")
        self.assertEqual(rc, 1)
        self.assertNotIn("covfix-receipt", out)
        self.assertFalse(self.summary(out)["generation_rc0"])
        self.assertEqual(self.unseal("capture/rc.txt"), b"3\n")
        self.assertEqual(list(self.w.iterdir()), [])

    def test_products_json_validated(self):
        for mode in ("noproducts", "emptyproducts", "missingproduct", "unsafeproduct", "dupproducts"):
            with self.subTest(mode=mode):
                shutil.rmtree(self.s, ignore_errors=True)
                rc, out = self.go(mode)
                self.assertEqual(rc, 1)
                self.assertFalse(self.summary(out)["products_json"])

    def test_products_not_regular(self):
        (self.w / "d").mkdir()
        (self.w / "PRODUCTS.json").write_text(json.dumps(["d"]))
        self.assertFalse(pg.products_ok(self.w))
        (self.w / "PRODUCTS.json").write_text(json.dumps([1]))
        self.assertFalse(pg.products_ok(self.w))

    def test_command_changed_during_the_run(self):
        rc, out = self.go("mutate")
        self.assertEqual(rc, 1)
        self.assertFalse(self.summary(out)["command_unchanged"])

    def test_symlink_from_generator_is_refused_and_trapped(self):
        rc, out = self.go("symlink")
        self.assertEqual(rc, 1)
        s = self.summary(out)
        self.assertIn("non-regular", s["refused"])
        self.assertGreater(s["trap_deleted"], 0)
        self.assertEqual(list(self.w.iterdir()), [])

    def test_command_sha_mismatch_or_relative_does_not_run(self):
        rc, out = self.go(sha="0" * 64)
        self.assertEqual(rc, 1)
        self.assertIn("sha256", self.summary(out)["refused"])
        self.assertFalse((self.w / "marker").exists())
        self.assertFalse(self.s.exists())
        rc, out = self.go(command0="gen.py")
        self.assertIn("malformed", self.summary(out)["refused"])

    def test_frame_attempt_and_tools_refusals(self):
        rc, out = self.go(frame=f"{PW}\n".encode())
        self.assertEqual(rc, 1)
        self.assertFalse(self.summary(out)["frame_ok"])
        self.assertNotIn(PW, out)
        rc, out = self.go(frame=FRAME + b"x" * 500)
        self.assertFalse(self.summary(out)["frame_ok"])
        rc, out = self.go(attempt="XYZ")
        self.assertEqual(rc, 1)
        self.assertIn("32 lowercase hex", out)
        out = io.StringIO()
        rc = pg.main(["--covfix-attempt", ATT, "--workdir", str(self.w), "--sealed", str(self.s), "--gen-spec", "x",
                      "--gen-spec-sha256", "0" * 64, "--gpg", "gpg", "--gpgconf", GPGCONF, "--gpg-sha256", fsha(GPG),
                      "--gpgconf-sha256", fsha(GPGCONF)], stdin=io.BytesIO(FRAME), stdout=out)
        self.assertEqual(rc, 1)
        self.assertIn("absolute", out.getvalue())

    def test_dirs_refused(self):
        (self.w / "x").write_text("x")
        rc, out = self.go()
        self.assertIn("empty", self.summary(out)["refused"])
        os.remove(self.w / "x")
        self.s.mkdir()
        rc, out = self.go()
        self.assertIn("must not exist", self.summary(out)["refused"])
        self.s.rmdir()
        rc, out = self.go(sealed=self.w / "sealed")
        self.assertIn("disjoint", self.summary(out)["refused"])

    def test_scratch_required(self):
        rc, out = self.go(scratch=False)
        self.assertEqual(rc, 1)
        self.assertIn("SCRATCH", self.summary(out)["refused"])

    def test_synthetic_round_trip_failure_stops_before_generation(self):
        real = cs.gpg_run
        with mock.patch.object(cs, "gpg_run", lambda a, p, d, t: b"wrong" if a is cs.GPG_DECRYPT else real(a, p, d, t)):
            rc, out = self.go()
        self.assertIn("synthetic", self.summary(out)["refused"])
        self.assertFalse((self.w / "marker").exists())

    def test_break_exit_and_line(self):
        real = cs.gpg_run
        calls = {"n": 0}

        def fake(argv, pw, payload, tools):
            out = real(argv, pw, payload, tools)
            if argv is cs.GPG_DECRYPT:
                calls["n"] += 1
                if calls["n"] == 2:                                       # past the synthetic round trip
                    return out + b"x"
            return out
        with mock.patch.object(cs, "gpg_run", fake):
            rc, out = self.go()
        self.assertEqual(rc, 66)
        self.assertEqual(out.strip().splitlines()[-1], f"covfix-break {ATT}")
        self.assertEqual(list(self.w.iterdir()), [])

    def test_final_seal_check_is_a_break(self):
        with mock.patch.object(cs, "seal_check", return_value={"ok": False}):
            rc, out = self.go()
        self.assertEqual(rc, 66)
        self.assertTrue(self.summary(out)["integrity_break"])

    def test_plaintext_spill_is_caught_and_removed(self):
        rc, out = self.go("leak")
        s = self.summary(out)
        self.assertEqual(rc, 1)
        self.assertEqual((s["scratch_tmp_changed"], s["scratch_spills"], s["spills_removed"]), (1, 1, True))
        self.assertFalse((self.scratch / "tmp" / "leak.json").exists())
        self.assertTrue((self.scratch / "tmp" / "old" / "pre.txt").exists())

    def test_a_benign_scratch_change_is_scanned_but_not_a_spill(self):
        rc, out = self.go("benign")
        s = self.summary(out)
        self.assertEqual((rc, s["scratch_tmp_changed"], s["scratch_spills"]), (0, 1, 0))
        self.assertTrue((self.scratch / "tmp" / "harmless.log").exists())

    def test_seed_spill_at_depth_is_caught_and_removed(self):
        rc, out = self.go("seedleak")
        s = self.summary(out)
        self.assertEqual((rc, s["scratch_spills"]), (1, 1))
        self.assertFalse((self.scratch / "tmp" / "old" / "deep.log").exists())

    def test_trap_removes_spills_on_failure(self):
        with mock.patch.object(cs, "seal", side_effect=cs.Refusal("x")):
            rc, out = self.go("faileak")
        s = self.summary(out)
        self.assertEqual((rc, s["trap_spills_removed"]), (1, True))
        self.assertFalse((self.scratch / "tmp" / "leak.json").exists())
        self.assertEqual(list(self.w.iterdir()), [])

    def test_trap_failure_is_recorded(self):
        with mock.patch.object(cs, "seal", side_effect=cs.Refusal("x")), \
                mock.patch.object(cs, "delete_plaintext", side_effect=OSError("busy")):
            rc, out = self.go()
        self.assertEqual((rc, self.summary(out)["trap_deleted"]), (1, "failed"))

    def test_trap_spill_failure_still_deletes(self):
        with mock.patch.object(cs, "seal", side_effect=cs.Refusal("x")), \
                mock.patch.object(pg, "spill_hits", side_effect=OSError("io")):
            rc, out = self.go()
        s = self.summary(out)
        self.assertEqual((s["trap_spills_removed"], isinstance(s["trap_deleted"], int)), ("failed", True))
        self.assertEqual(list(self.w.iterdir()), [])                     # deletion still ran

    def test_termination_and_internal_error_use_fixed_codes(self):
        with mock.patch.object(pg.Generator, "run", side_effect=SystemExit(143)):
            rc, out = self.go()
        self.assertEqual((rc, self.summary(out)["refused"]), (1, "terminated"))
        with mock.patch.object(cs, "seal", side_effect=ValueError("/secret/path genie-mcjob-1234567890.status")):
            rc, out = self.go()
        self.assertEqual((rc, self.summary(out)["refused"]), (1, "internal error"))
        self.assertNotIn("secret", out)

    def test_sigterm_handler_is_installed_during_the_run(self):
        seen = []

        def spy(self_, spec, workdir, seeds):
            import signal as sg
            seen.append(sg.getsignal(sg.SIGTERM))
            raise SystemExit(143)
        with mock.patch.object(pg.Generator, "run", spy):
            self.go()
        self.assertEqual(seen, [pg._term])

    def test_sigterm_handler_raises(self):
        with self.assertRaises(SystemExit):
            pg._term(15, None)

    def test_generator_process_group_is_killed(self):
        g = pg.Generator()
        g.proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], start_new_session=True)
        p = g.proc
        g.kill()
        self.assertIsNotNone(p.returncode)
        g.kill()                                                          # already reaped: a no-op
        g.proc = mock.Mock(pid=999999, poll=mock.Mock(return_value=None), wait=mock.Mock())
        with mock.patch.object(pg.os, "killpg", side_effect=ProcessLookupError):
            g.kill()

    def test_scan_hit_in_sealed_fails(self):
        with mock.patch.object(cs, "content_scan", return_value=["/x"]):
            rc, out = self.go()
        self.assertEqual((rc, self.summary(out)["sealed_scan_hits"]), (1, 1))

    def test_spec_validation(self):
        gen = write_gen(self.d)
        good = json.loads(write_spec(self.d, gen).read_text())
        env = {"FAKE_MODE": "ok", "SPILL_ROOT": "x"}     # env_keep set, and env_set values equal to the inherited ones,
        with mock.patch.dict(os.environ, env):           # so each case below can refuse only by its own rule
            inherited = {"TMPDIR": os.environ.get("TMPDIR", "/x"), "PATH": os.environ["PATH"]}
            for ok in (good, {**good, "env_set": {"OK_NAME": "v", "_B2": ""}}):
                p = self.d / "ok.json"
                p.write_text(json.dumps(ok))
                self.assertEqual(pg.load_spec(p, fsha(p))["env_set"], ok["env_set"])
            for bad in ({**good, "extra": 1}, {**good, "tunes": ["one"]}, {**good, "command": []},
                        {**good, "env_keep": ["TMPDIR"]}, {**good, "command_sha256": "x"}, [1],
                        {**good, "command": ["rel/gen.py"]}, {k: v for k, v in good.items() if k != "env_set"},
                        {**good, "env_set": []}, {**good, "env_set": {"TMPDIR": inherited["TMPDIR"]}},
                        {**good, "env_set": {"PATH": inherited["PATH"]}},
                        {**good, "env_set": {"1X": "v"}}, {**good, "env_set": {"A=B": "v"}}, {**good, "env_set": {"": "v"}},
                        {**good, "env_set": {"OK_NAME": 1}}, {**good, "env_set": {"OK_NAME": "a\x00b"}}):
                with self.subTest(bad=str(bad)[:40]):
                    p = self.d / "bad.json"
                    p.write_text(json.dumps(bad))
                    with self.assertRaises(cs.Refusal):
                        pg.load_spec(p, fsha(p))
            with self.assertRaises(cs.Refusal):
                pg.load_spec(self.d / "absent.json", "0" * 64)
            p = self.d / "notjson.json"
            p.write_bytes(b"{not json")
            with self.assertRaisesRegex(cs.Refusal, "cannot be read"):    # at its pin, but not JSON
                pg.load_spec(p, fsha(p))
            p = self.d / "nocmd.json"
            p.write_text(json.dumps({**good, "command": [str(self.d / "absent")]}))
            with self.assertRaises(cs.Refusal):
                pg.load_spec(p, fsha(p))

    def test_snapshot_edge_cases(self):
        self.assertEqual(pg.snapshot(None), {})
        self.assertEqual(pg.snapshot(self.d / "absent"), {})
        os.symlink("/etc/hosts", self.scratch / "tmp" / "lnk")
        snap = pg.snapshot(self.scratch / "tmp")
        self.assertEqual(snap["lnk"][0], "l")
        self.assertEqual(snap["lnk"][2], "/etc/hosts")
        self.assertEqual(snap["old"][0], "d")
        self.assertTrue(pg.remove_verified(self.d, [("never-existed", ("f", 0, 0, 0), True)]))
        self.assertFalse(pg.remove_verified(self.scratch / "tmp", [("old", snap["old"], False)]))   # never an old dir
        self.assertTrue((self.scratch / "tmp" / "old").is_dir())
        os.mkfifo(self.scratch / "tmp" / "fifo")
        self.assertEqual(pg.snapshot(self.scratch / "tmp")["fifo"][0], "o")                  # a special entry
        (self.scratch / "tmp" / "stuck").write_text("x")
        with mock.patch.object(pg.os, "unlink", side_effect=PermissionError("no")):
            self.assertFalse(pg.remove_verified(self.scratch / "tmp", [("stuck", ("f", 0, 0, 0), True)]))

    def test_a_group_that_will_not_end_is_refused(self):
        with mock.patch.object(pg.os, "killpg", side_effect=PermissionError("no")), \
                mock.patch.object(pg, "GROUP_WAIT_S", 0), self.assertRaises(cs.Refusal):
            pg.end_group(999999)

    def test_an_unconfirmed_group_end_fails_the_run(self):
        with mock.patch.object(pg, "end_group", side_effect=cs.Refusal("the group did not end")):
            rc, out = self.go()
        s = self.summary(out)
        self.assertEqual((rc, s["group_ended"]), (1, "failed"))

    def test_a_seed_in_a_new_directory_name_is_caught_and_removed(self):
        rc, out = self.go("seeddir")
        s = self.summary(out)
        self.assertEqual((rc, s["spills_removed"]), (1, True))
        self.assertGreaterEqual(s["scratch_spills"], 1)
        self.assertEqual(sorted(p.name for p in (self.scratch / "tmp").iterdir()), ["old"])

    def test_a_seed_in_a_link_target_is_caught_and_removed(self):
        rc, out = self.go("seedlink")
        s = self.summary(out)
        self.assertEqual((rc, s["scratch_spills"], s["spills_removed"]), (1, 1, True))
        self.assertFalse(os.path.lexists(self.scratch / "tmp" / "plain-link"))

    def test_a_pg_owned_file_is_not_a_product(self):
        rc, out = self.go("captureproduct")
        self.assertEqual(rc, 1)
        self.assertFalse(self.summary(out)["products_json"])

    def test_an_orphan_of_the_generator_is_killed_before_the_seal(self):
        rc, out = self.go("orphan")
        self.assertEqual(rc, 0)
        time.sleep(2.5)
        self.assertFalse((self.scratch / "tmp" / "late.txt").exists())

    def test_a_missing_published_index_is_a_break(self):
        real = cs.seal

        def seal_then_drop(*a, **k):
            r = real(*a, **k)
            os.remove(Path(a[1]) / cs.SEAL_FILE)
            return r

        with mock.patch.object(cs, "seal", side_effect=seal_then_drop):
            rc, out = self.go()
        self.assertEqual(rc, cs.BREAK_RC)
        self.assertIn("covfix-break", out)

    def test_the_trap_stays_armed_through_the_scan(self):
        real, calls = pg.remove_verified, []

        def fail_first(*a):
            calls.append(a)
            if len(calls) == 1:
                raise OSError("io")                                      # the main path's removal fails
            return real(*a)                                              # the trap's removal is real

        with mock.patch.object(pg, "remove_verified", side_effect=fail_first):
            rc, out = self.go("leak")
        self.assertEqual(len(calls), 2)
        s = self.summary(out)
        self.assertEqual(rc, 1)
        self.assertIs(s["trap_spills_removed"], True)
        self.assertFalse((self.scratch / "tmp" / "leak.json").exists())   # found by the sealed hashes: W is gone


class Round3Findings(PGBase):
    """codex-school2 round 3 (af5fdd5b), PG findings 6, 8, 9 and the item-7 detector (the director's ruling)."""

    def test_f6_an_equal_length_overwrite_with_mtime_kept_is_a_spill(self):
        rc, out = self.go("overwritekeep")
        s = self.summary(out)
        self.assertEqual(rc, 1, out)
        self.assertGreaterEqual(s["scratch_spills"], 1)

    def test_f6_an_unreadable_entry_does_not_stop_the_scan_or_the_cleanup(self):
        rc, out = self.go("unreadable")
        s = self.summary(out)
        self.assertEqual(rc, 1, out)
        self.assertNotIn("refused", s)
        self.assertFalse((self.scratch / "tmp" / "z-leak.txt").exists())
        self.assertFalse(os.path.lexists(self.scratch / "tmp" / "a-locked.bin"))   # unverifiable: removed too

    def test_f6_an_unlistable_directory_fails_the_run_but_the_scan_goes_on(self):
        rc, out = self.go("unlistable")
        s = self.summary(out)
        os.chmod(self.scratch / "tmp" / "a-lockdir", 0o700)
        self.assertEqual(rc, 1, out)
        self.assertGreaterEqual(s["scratch_scan_errors"], 1)
        self.assertFalse((self.scratch / "tmp" / "z-leak.txt").exists())

    def test_f6_scan_errors_alone_fail_the_run(self):
        rc, out = self.go("lockedonly")
        os.chmod(self.scratch / "tmp" / "a-lockdir", 0o700)
        s = self.summary(out)
        self.assertEqual((rc, s["scratch_spills"]), (1, 0), out)
        self.assertGreaterEqual(s["scratch_scan_errors"], 1)

    def test_f6_an_lstat_error_is_collected_not_raised(self):
        (self.scratch / "tmp" / "gone.txt").write_text("x")
        real = os.lstat

        def flaky(p, *a, **k):
            if str(p).endswith("gone.txt"):
                raise FileNotFoundError(p)
            return real(p, *a, **k)

        errs = []
        with mock.patch.object(pg.os, "lstat", flaky):
            snap = pg.snapshot(self.scratch / "tmp", errs)
            with self.assertRaises(OSError):
                pg.snapshot(self.scratch / "tmp")
        self.assertEqual(len(errs), 1)
        self.assertNotIn("gone.txt", snap)

    def test_f6_the_trap_rescan_tolerates_an_unlistable_directory(self):
        real, calls = pg.remove_verified, []

        def false_first(*a):
            calls.append(a)
            return False if len(calls) == 1 else real(*a)

        with mock.patch.object(pg, "remove_verified", side_effect=false_first):
            rc, out = self.go("unlistable")
        os.chmod(self.scratch / "tmp" / "a-lockdir", 0o700)
        self.assertEqual(rc, 1)
        self.assertIs(self.summary(out)["trap_spills_removed"], True)
        self.assertFalse((self.scratch / "tmp" / "z-leak.txt").exists())

    def test_f6_a_removal_that_returns_false_keeps_the_trap_armed(self):
        real, calls = pg.remove_verified, []

        def false_first(*a):
            calls.append(a)
            return False if len(calls) == 1 else real(*a)

        with mock.patch.object(pg, "remove_verified", side_effect=false_first):
            rc, out = self.go("leak")
        self.assertEqual((rc, len(calls)), (1, 2))
        self.assertIs(self.summary(out)["trap_spills_removed"], True)
        self.assertFalse((self.scratch / "tmp" / "leak.json").exists())

    def test_f8_a_sigterm_during_the_agent_shutdown_still_removes_the_home(self):
        homes, real_home, real_run = [], cs.new_gnupg_home, cs.subprocess.run

        def spy():
            homes.append(real_home())
            return homes[-1]

        def term_then_run(*a, **k):
            os.kill(os.getpid(), signal.SIGTERM)
            return real_run(*a, **k)

        old = signal.signal(signal.SIGTERM, pg._term)
        try:
            with mock.patch.object(cs, "new_gnupg_home", spy), mock.patch.object(cs.subprocess, "run", term_then_run), \
                    self.assertRaises(SystemExit):
                cs.gpg_run(cs.GPG_ENCRYPT, PW, b"x", TOOLS)
        finally:
            signal.signal(signal.SIGTERM, old)
        self.assertTrue(homes and not any(os.path.lexists(h) for h in homes))

    def test_f8_a_gpg_run_installs_its_own_recorder_and_restores_the_handler(self):
        seen, real_run = [], cs.subprocess.run

        def spy(*a, **k):
            seen.append(signal.getsignal(signal.SIGTERM))
            return real_run(*a, **k)

        old = signal.signal(signal.SIGTERM, pg._term)
        try:
            with mock.patch.object(cs.subprocess, "run", spy):
                cs.gpg_run(cs.GPG_ENCRYPT, PW, b"v", TOOLS)
            after = signal.getsignal(signal.SIGTERM)
        finally:
            signal.signal(signal.SIGTERM, old)
        self.assertTrue(seen)
        for h in seen:
            self.assertTrue(callable(h) and h is not pg._term, h)
        self.assertIs(after, pg._term)

    def test_f8_off_the_main_thread_and_under_the_default_handler(self):
        import threading
        out = []
        th = threading.Thread(target=lambda: out.append(cs.gpg_run(cs.GPG_ENCRYPT, PW, b"t", TOOLS)))
        th.start()
        th.join()
        self.assertTrue(out and out[0])                                 # no handler to hold a SIGTERM there; it runs
        real_run = cs.subprocess.run

        held = []

        def term_then_run(*a, **k):
            h = signal.getsignal(signal.SIGTERM)
            if callable(h):                                             # only under gpg_run's recorder: SIG_DFL here
                held.append(h)                                          # would end the test process
                signal.raise_signal(signal.SIGTERM)                     # held by the recorder (not os.kill, which
            return real_run(*a, **k)                                    # the test patches)

        old = signal.signal(signal.SIGTERM, signal.SIG_DFL)
        try:
            with mock.patch.object(cs.subprocess, "run", term_then_run), mock.patch.object(cs.os, "kill") as kill:
                cs.gpg_run(cs.GPG_ENCRYPT, PW, b"u", TOOLS)
            self.assertTrue(held)
            kill.assert_called_once_with(os.getpid(), signal.SIGTERM)  # re-delivered to the default handler
        finally:
            signal.signal(signal.SIGTERM, old)

    def test_f9_a_missing_required_product_fails_the_run(self):
        gen = write_gen(self.d)
        for i, req in enumerate(([{"pattern": "out/gen5d/*.npz", "count": 1}],
                                 [{"pattern": "out/G21/*.json", "count": 2}],
                                 [{"pattern": "*seeds.json", "count": 1}])):        # 2 files match: exact counts
            with self.subTest(req=req):
                w = self.d / f"w{i}"
                w.mkdir()
                spec = write_spec(self.d, gen, required=req)
                rc, out = self.go(spec=spec, workdir=w, sealed=self.d / f"sealed{i}")
                s = self.summary(out)
                self.assertEqual(rc, 1, out)
                self.assertNotIn("refused", s)
                self.assertIs(s["required_products"], False)

    def test_f9_the_required_inventory_is_validated(self):
        gen = write_gen(self.d)
        with mock.patch.dict(os.environ, {"FAKE_MODE": "ok", "SPILL_ROOT": "x"}):  # env_keep set: each case refuses by its own rule
            ok = [{"pattern": "a/*.npz", "count": 1}, {"pattern": "b", "count": 2}]
            sp = write_spec(self.d, gen, required=ok)
            self.assertEqual(pg.load_spec(sp, fsha(sp))["required"], ok)
            for req in ([], [{"pattern": "../x", "count": 1}], [{"pattern": "a", "count": 0}], [{"pattern": "a"}],
                        [{"pattern": "/abs", "count": 1}], "x"):
                with self.subTest(req=req), self.assertRaises(cs.Refusal):
                    sp = write_spec(self.d, gen, required=req)
                    pg.load_spec(sp, fsha(sp))

    def test_f7_detector_a_clean_step_passes(self):
        self.assertEqual(pg.step_cgroup_check(), {"pids": 2, "ancestors": 1})

    def test_f7_detector_the_ancestor_chain_stops_at_the_first_gap(self):
        proc, cg = fake_step(self.d / "gap", extra_pids=((5001, 1),))
        parent = os.getppid()
        (proc / str(parent) / "stat").write_text(f"{parent} (sh) S 5000 0 0\n")      # its parent is outside the step
        (proc / "5000").mkdir()
        (proc / "5000" / "stat").write_text("5000 (x) S 5001 0 0\n")                 # whose parent is back inside
        with mock.patch.object(pg, "PROC", str(proc)), mock.patch.object(pg, "CGROUP_ROOT", str(cg)), \
                self.assertRaises(cs.Refusal):
            pg.step_cgroup_check()

    def test_f7_detector_a_reparented_escapee_is_caught(self):
        for i, ppid in enumerate((1, 31337, os.getpid())):         # init, a subreaper outside the step, the sealer
            with self.subTest(ppid=ppid):
                proc, cg = fake_step(self.d / f"esc{i}", extra_pids=((424250 + i, ppid),))
                with mock.patch.object(pg, "PROC", str(proc)), mock.patch.object(pg, "CGROUP_ROOT", str(cg)), \
                        self.assertRaises(cs.Refusal):
                    pg.step_cgroup_check()

    def test_f7_detector_an_extra_pid_in_the_step_refuses(self):
        proc, cg = fake_step(self.d / "x", extra_pids=(424242,))
        with mock.patch.object(pg, "PROC", str(proc)), mock.patch.object(pg, "CGROUP_ROOT", str(cg)), \
                self.assertRaises(cs.Refusal):
            pg.step_cgroup_check()

    def test_f7_detector_an_unreadable_or_v1_cgroup_is_a_stop(self):
        v2 = "0::/" + JOB_CG + "/step_0/user/task_0"
        for i, (kw, why) in enumerate((({"readable": False}, "cannot be read"),
                                       ({"cgroup_line": "4:memory:/slurm/job_1"}, "not a single cgroup v2 entry"),
                                       ({"cgroup_line": v2 + "\n4:memory:/slurm/job_1"},    # hybrid: a valid v2 path
                                        "not a single cgroup v2 entry"))):                  # plus a v1 line
            with self.subTest(kw=kw):
                proc, cg = fake_step(self.d / f"v{i}", **kw)
                with mock.patch.object(pg, "PROC", str(proc)), mock.patch.object(pg, "CGROUP_ROOT", str(cg)), \
                        self.assertRaisesRegex(cs.Refusal, why):
                    pg.step_cgroup_check()

    def test_f7_a_run_with_an_escaped_process_has_no_receipt(self):
        proc, cg = fake_step(self.d / "y", extra_pids=(424243,))
        with mock.patch.object(pg, "PROC", str(proc)), mock.patch.object(pg, "CGROUP_ROOT", str(cg)):
            rc, out = self.go()
        self.assertEqual(rc, 1, out)
        self.assertIn("cgroup", self.summary(out)["refused"])
        self.assertNotIn("covfix-receipt", out)


class Round4Findings(PGBase):
    """codex-school2 round 4 (6ba32779), PG items 7 and 8 with the director's widening: each reproduced first."""

    def detect(self, tag, **kw):
        proc, cg = fake_step(self.d / tag, **kw)
        with mock.patch.object(pg, "PROC", str(proc)), mock.patch.object(pg, "CGROUP_ROOT", str(cg)):
            return pg.step_cgroup_check()

    def test_r4_7_any_other_process_anywhere_in_the_job_refuses_with_its_inventory(self):
        for i, where in enumerate(("step_0/user/task_1",                # a sibling task
                                   "step_1/user/task_0",                # a sibling step (background srun, --overlap)
                                   "step_extern/user/task_0",           # pam_slurm_adopt's ssh, step_extern's sleep
                                   "step_extern",
                                   "step_0/slurm",                      # a slurmstepd that is not an ancestor
                                   "step_0/user/task_0/nested",         # a child cgroup of the sealer's own
                                   ".")):                               # the job cgroup itself
            with self.subTest(where=where):
                with self.assertRaises(cs.Refusal) as e:
                    self.detect(f"o{i}", others={where: [424300 + i]})
                self.assertEqual(e.exception.inventory, [{"cgroup": where, "pid": 424300 + i, "comm": "gevgen",
                                                          "exe": "/fake/bin/gevgen"}])

    def test_r4_7_an_ancestor_elsewhere_in_the_job_is_allowed(self):
        """A slurmstepd in step_0/slurm that is the wrapper's parent is in the contiguous ancestor chain."""
        self.assertEqual(self.detect("anc", parent_ppid=7000, others={"step_0/slurm": [(7000, 1)]}),
                         {"pids": 3, "ancestors": 2})

    def test_r4_7_an_unreadable_directory_or_no_job_cgroup_is_a_stop(self):
        with self.assertRaises(cs.Refusal):
            self.detect("u1", others={"step_1/user/task_0": None})      # no readable cgroup.procs
        proc, cg = fake_step(self.d / "u2", others={"step_2/user/task_0": []})
        locked = cg / JOB_CG / "step_2"
        locked.chmod(0)                                                 # a directory that cannot be listed
        try:
            with mock.patch.object(pg, "PROC", str(proc)), mock.patch.object(pg, "CGROUP_ROOT", str(cg)), \
                    self.assertRaises(cs.Refusal):
                pg.step_cgroup_check()
        finally:
            locked.chmod(0o755)
        for i, bad in enumerate(("job_x", "job_1a", "job_1_2")):         # job_ plus anything but digits is no job
            line = "0::/" + JOB_CG.replace("job_1", bad) + "/step_0/user/task_0"
            proc, cg = fake_step(self.d / f"nj{i}", cgroup_line=line)
            mine = cg / JOB_CG.replace("job_1", bad) / "step_0" / "user" / "task_0"
            mine.mkdir(parents=True)                                    # readable, so only the job rule can refuse
            (mine / "cgroup.procs").write_text(f"{os.getpid()}\n{os.getppid()}\n")
            with self.subTest(line=line), mock.patch.object(pg, "PROC", str(proc)), \
                    mock.patch.object(pg, "CGROUP_ROOT", str(cg)), self.assertRaisesRegex(cs.Refusal, "exactly one"):
                pg.step_cgroup_check()
        for line in ("0::/user.slice/user-1.slice/session-1.scope",
                     "0::/" + JOB_CG + "/step_0/job_2/task_0"):               # none, or two job cgroups
            with self.subTest(line=line), self.assertRaisesRegex(cs.Refusal, "exactly one"):
                self.detect("u3" + str(len(line)), cgroup_line=line)

    def test_r4_7_the_sealer_must_be_in_its_jobs_cgroups(self):
        proc, cg = fake_step(self.d / "absent")
        (cg / JOB_CG / "step_0" / "user" / "task_0" / "cgroup.procs").write_text(f"{os.getppid()}\n")
        with mock.patch.object(pg, "PROC", str(proc)), mock.patch.object(pg, "CGROUP_ROOT", str(cg)), \
                self.assertRaises(cs.Refusal):
            pg.step_cgroup_check()

    def test_r4_7_outside_a_job_or_with_a_stray_nothing_is_generated(self):
        """The wrapper runs pg-connect on its host with no allocation of its own. A sealer outside a Slurm job, or
        with a stray already in its job, is refused before the generator starts: no seed-bearing file reaches W."""
        for i, kw in enumerate(({"cgroup_line": "0::/user.slice/user-1.slice/session-1.scope"},
                                {"extra_pids": (424500,)})):
            w, s = self.d / f"prew{i}", self.d / f"pres{i}"
            w.mkdir()
            proc, cg = fake_step(self.d / f"pre{i}", **kw)
            with self.subTest(kw=kw), mock.patch.object(pg, "PROC", str(proc)), \
                    mock.patch.object(pg, "CGROUP_ROOT", str(cg)), \
                    mock.patch.object(pg.Generator, "run", side_effect=AssertionError("generated")) as run:
                rc, out = self.go(workdir=w, sealed=s)
                run.assert_not_called()
                self.assertEqual(rc, 1, out)
                self.assertIn("cgroup", self.summary(out)["refused"])
                self.assertNotIn("generation_rc0", self.summary(out))
                self.assertEqual(list(w.iterdir()), [])
                self.assertFalse(os.path.lexists(s))
                self.assertNotIn("covfix-receipt", out)

    def test_r4_7_an_unreadable_comm_or_exe_is_none_in_the_inventory(self):
        proc, cg = fake_step(self.d / "nocomm", others={"step_1": [424398]})
        (proc / "424398" / "comm").unlink()
        (proc / "424398" / "exe").unlink()
        with mock.patch.object(pg, "PROC", str(proc)), mock.patch.object(pg, "CGROUP_ROOT", str(cg)), \
                self.assertRaises(cs.Refusal) as e:
            pg.step_cgroup_check()
        self.assertEqual(e.exception.inventory, [{"cgroup": "step_1", "pid": 424398, "comm": None, "exe": None}])

    def test_r4_8_killing_a_child_that_is_already_gone_is_quiet(self):
        class Gone:
            def kill(self):
                raise ProcessLookupError()
        cs._kill(Gone())                                                # no exception

    def test_r4_7_a_run_records_the_inventory_and_has_no_receipt(self):
        proc, cg = fake_step(self.d / "inv", others={"step_extern/user/task_0": [424399]})
        with mock.patch.object(pg, "PROC", str(proc)), mock.patch.object(pg, "CGROUP_ROOT", str(cg)):
            rc, out = self.go()
        s = self.summary(out)
        self.assertEqual(rc, 1, out)
        self.assertEqual(s["step_cgroup_inventory"], [{"cgroup": "step_extern/user/task_0", "pid": 424399,
                                                       "comm": "gevgen", "exe": "/fake/bin/gevgen"}])
        self.assertNotIn("covfix-receipt", out)

    def _stubborn(self, real_popen):
        def popen(argv, **k):                                           # a gpg that ignores SIGTERM and hangs
            if k.get("pass_fds") != (3,):                               # not gpg (gpgconf, via subprocess.run)
                return real_popen(argv, **k)
            return real_popen([sys.executable, "-c", "import signal, time; signal.signal(signal.SIGTERM, "
                               "signal.SIG_IGN); time.sleep(20)"], stdin=k["stdin"], stdout=k["stdout"],
                              stderr=k["stderr"])
        return popen

    def test_r4_8_a_held_sigterm_kills_a_stubborn_gpg_within_the_bound(self):
        import threading
        homes, timeouts = [], []
        real_home, real_run, real_popen = cs.new_gnupg_home, cs.subprocess.run, cs.subprocess.Popen

        def spy_home():
            homes.append(real_home())
            return homes[-1]

        def spy_run(*a, **k):
            timeouts.append(k.get("timeout"))
            return real_run(*a, **k)

        main = threading.main_thread().ident
        timer = threading.Timer(0.5, signal.pthread_kill, (main, signal.SIGTERM))
        old = signal.signal(signal.SIGTERM, pg._term)
        try:
            with mock.patch.object(cs, "new_gnupg_home", spy_home), mock.patch.object(cs.subprocess, "run", spy_run), \
                    mock.patch.object(cs.subprocess, "Popen", self._stubborn(real_popen)), \
                    self.assertRaises(SystemExit):
                t0 = time.monotonic()
                timer.start()
                cs.gpg_run(cs.GPG_ENCRYPT, PW, b"x", TOOLS)
            held = time.monotonic() - t0 - 0.5
        finally:
            timer.cancel()
            signal.signal(signal.SIGTERM, old)
        self.assertLess(held, cs.SIGTERM_HOLD_BOUND_S)
        self.assertEqual(timeouts, [cs.GPGCONF_TIMEOUT_S])
        self.assertLessEqual(cs.GPGCONF_TIMEOUT_S, 10)
        self.assertLess(cs.GPGCONF_TIMEOUT_S, cs.SIGTERM_HOLD_BOUND_S)
        self.assertLess(cs.SIGTERM_HOLD_BOUND_S, 30)                    # Slurm's default KillWait
        self.assertTrue(homes and not any(os.path.lexists(h) for h in homes))

    def test_r4_8_the_home_goes_whatever_the_agent_shutdown_raises(self):
        homes, real_home = [], cs.new_gnupg_home

        def spy():
            homes.append(real_home())
            return homes[-1]

        with mock.patch.object(cs, "new_gnupg_home", spy), \
                mock.patch.object(cs.subprocess, "run", side_effect=RuntimeError("unexpected")), \
                self.assertRaises(RuntimeError):
            cs.gpg_run(cs.GPG_ENCRYPT, PW, b"x", TOOLS)
        self.assertTrue(homes and not any(os.path.lexists(h) for h in homes))

    def test_r4_8_a_sigterm_before_gpg_starts_kills_it_at_once(self):
        homes, real_home, real_popen = [], cs.new_gnupg_home, cs.subprocess.Popen

        def term_home():
            homes.append(real_home())
            signal.raise_signal(signal.SIGTERM)                         # held: gpg has not started yet
            return homes[-1]

        old = signal.signal(signal.SIGTERM, pg._term)
        try:
            with mock.patch.object(cs, "new_gnupg_home", term_home), \
                    mock.patch.object(cs.subprocess, "Popen", self._stubborn(real_popen)), \
                    self.assertRaises(SystemExit):
                t0 = time.monotonic()
                cs.gpg_run(cs.GPG_ENCRYPT, PW, b"x", TOOLS)
            held = time.monotonic() - t0
        finally:
            signal.signal(signal.SIGTERM, old)
        self.assertLess(held, cs.SIGTERM_HOLD_BOUND_S)
        self.assertTrue(homes and not any(os.path.lexists(h) for h in homes))


RATIO = json.dumps({"f_MEC": 0.1234, "k": 1.07}).encode()      # the fake generator's out/G21/ratio.json


class SeedBearing(PGBase):
    """The director's ruling of 2026-11-25 on seed-bearing artifacts (gevgen names outputs by the seed): a seed, and
    the hash of any seed-bearing file, never leave W except encrypted. Each test failed on the round-4 code first."""

    def stray(self, tag, comm="gevgen", exe="/fake/bin/gevgen"):
        """A fake job with one stray process in step_extern, its comm and exe as given."""
        proc, cg = fake_step(self.d / tag, others={"step_extern/user/task_0": [424500]})
        (proc / "424500" / "comm").write_text(comm + "\n")
        (proc / "424500" / "exe").unlink()
        os.symlink(exe, proc / "424500" / "exe")
        return proc, cg

    def go_stray(self, tag, **kw):
        """The stray joins the job during generation (a detached generator descendant), so the job check before
        generation passes and the one before the seal catches it."""
        proc, cg = self.stray(tag, **kw)
        procs = cg / JOB_CG / "step_extern" / "user" / "task_0" / "cgroup.procs"
        joined = procs.read_text()
        procs.write_text("")
        real = pg.Generator.run

        def run_then_join(self_, *a):
            rc = real(self_, *a)
            procs.write_text(joined)
            return rc
        with mock.patch.object(pg, "PROC", str(proc)), mock.patch.object(pg, "CGROUP_ROOT", str(cg)), \
                mock.patch.object(pg.Generator, "run", run_then_join):
            rc, out = self.go()
        self.assertIs(self.summary(out).get("generation_rc0"), True, out)  # it was the check before the seal
        return rc, out

    def assert_redacted(self, rc, out, *secrets):
        s = self.summary(out)
        self.assertEqual(rc, 1, out)
        self.assertIs(s["summary_leak_redacted"], True, out)
        self.assertEqual(s["step_cgroup_inventory"], 1)                # reduced to its count
        for secret in secrets:
            self.assertNotIn(secret.lower(), out.lower())
        self.assertNotIn("covfix-receipt", out)

    # M1: the summary leaves W, so it is scanned
    def test_m1_a_seed_in_a_strays_comm_is_redacted(self):
        seed = str(BASE + 10_003)
        self.assert_redacted(*self.go_stray("comm", comm=seed), seed)

    def test_m1_a_seed_in_a_strays_exe_is_redacted(self):
        seed = str(BASE + 1)
        self.assert_redacted(*self.go_stray("exe", exe=f"/opt/gevgen-{seed}/bin/gevgen"), seed)

    def test_m1_a_plaintext_hash_in_the_summary_is_redacted(self):
        """The step check runs before the seal, so the hash comes from the trap's hashes of W's files."""
        h = hashlib.sha256(RATIO).hexdigest()
        for tag, text in (("lower", h), ("upper", h.upper())):
            with self.subTest(tag):
                self.tearDown()
                self.setUp()
                self.assert_redacted(*self.go_stray("h" + tag, exe=f"/opt/{text}/gevgen"), h)

    def test_m1_an_exe_under_w_the_sealed_dir_or_scratch_is_a_fixed_token(self):
        for tag, root, token in (("w", lambda: self.w, "<workdir>"), ("s", lambda: self.s, "<sealed>"),
                                 ("x", lambda: self.scratch, "<scratch>")):
            with self.subTest(token):
                self.tearDown()
                self.setUp()
                rc, out = self.go_stray("t" + tag, exe=str(root() / "bin" / "gevgen"))
                s = self.summary(out)
                self.assertEqual(rc, 1, out)
                self.assertEqual(s["step_cgroup_inventory"], [{"cgroup": "step_extern/user/task_0", "pid": 424500,
                                                               "comm": "gevgen", "exe": token}])
                self.assertNotIn(self.d.name, out)                       # the run's unique temp dir name
                self.assertNotIn("summary_leak_redacted", s)

    def test_m1_the_guard_unit(self):
        h = hashlib.sha256(b"x").hexdigest()
        seeds = [str(BASE).encode()]
        self.assertEqual(pg.leak_guard(0, {"a": 1}, seeds, {h}), (0, {"a": 1}))
        for summ in ({"refused": "r", "step_cgroup_inventory": [{"comm": str(BASE)}, {"comm": "x"}]},
                     {"refused": "r", "step_cgroup_inventory": [{"exe": "/" + h.upper()}, {"comm": "x"}]}):
            rc, s = pg.leak_guard(0, summ, seeds, {h})
            self.assertEqual((rc, s), (1, {"refused": "r", "step_cgroup_inventory": 2, "summary_leak_redacted": True}))
        rc, s = pg.leak_guard(0, {"refused": "seed " + str(BASE)}, seeds, set())  # still a hit: a fixed summary
        self.assertEqual((rc, s), (1, {"refused": "the summary named a task seed or a plaintext hash",
                                       "summary_leak_redacted": True}))
        self.assertEqual(pg.leak_guard(66, {"x": str(BASE)}, seeds, set())[0], 66)    # a break stays a break

    # M2: a plaintext hash written as text in scratch is a spill
    def test_m2_a_sums_file_in_scratch_tmp_is_a_spill(self):
        rc, out = self.go("sumsleak")
        s = self.summary(out)
        self.assertEqual(rc, 1, out)
        self.assertEqual(s["scratch_spills"], 1)
        self.assertIs(s["spills_removed"], True)
        self.assertFalse(os.path.lexists(self.scratch / "tmp" / "PG-SHA256SUMS"))

    def test_m2_hash_text_in_a_name_or_upper_case_is_a_hit(self):
        h = hashlib.sha256(b"plain").hexdigest()
        root = self.scratch / "tmp"
        (root / f"x-{h}.txt").write_text("benign")
        (root / "upper.txt").write_text("sum " + h.upper() + "\n")
        (root / "inside.txt").write_text("abc" + h + "def")                 # inside a longer hex run
        (root / "clean.txt").write_text("sum " + "0" * 64 + "\n")
        entries = [(r, ("f",), True) for r in (f"x-{h}.txt", "upper.txt", "inside.txt", "clean.txt")]
        self.assertEqual([e[0] for e in pg.spill_hits(root, entries, {h}, [])],
                         [f"x-{h}.txt", "upper.txt", "inside.txt"])

    # (a): opaque ids over a CSPRNG permutation
    def test_a_ids_are_drawn_from_a_csprng(self):
        import secrets
        self.assertIsInstance(cs._RNG, secrets.SystemRandom)

    def test_a_id_order_is_independent_of_relpath_order(self):
        rels = ["a", "b", "c", "d", "e"]
        first = {r: 0 for r in rels}
        for _ in range(300):
            m = cs.assign_ids(rels)
            self.assertEqual(list(m), cs.product_ids(5))
            self.assertEqual(sorted(m.values()), rels)
            first[m["p0001"]] += 1
        self.assertTrue(all(25 <= n <= 95 for n in first.values()), first)   # expected 60 each

    def test_a_seal_follows_the_permutation_and_the_manifest_holds_it(self):
        class Reverse:
            def shuffle(self, x):
                x.reverse()
        self.files(a=b"alpha", sub__b=b"beta")
        with mock.patch.object(cs, "_RNG", Reverse()):
            r = cs.seal(self.w, self.s, PW, TOOLS)
        man = json.loads(cs.gpg_run(cs.GPG_DECRYPT, PW, (self.s / "PG-MANIFEST.json.gpg").read_bytes(), TOOLS))
        self.assertEqual(man["paths"], {"p0001": "sub/b", "p0002": "a"})
        self.assertEqual(r["hashes"]["p0001"], hashlib.sha256(b"beta").hexdigest())
        self.assertNotIn("sub/b", (self.s / "PG-SEAL.sha256").read_text())

    # (b): no compression, so a fixed-width text's ciphertext size is the same for every seed
    def test_b_a_fixed_width_logs_ciphertext_size_does_not_depend_on_the_seeds_digits(self):
        sizes = {}
        for seed in (1111111111, 1000000000, 1234567890, 1987654321, 1357913579, 1999999999):
            log = "".join(f"event {i:06d} seed {seed} status done\n" for i in range(400)).encode()
            sizes[seed] = len(cs.gpg_run(cs.GPG_ENCRYPT, PW, log, TOOLS))
        self.assertEqual(len(set(sizes.values())), 1, sizes)
        self.assertEqual(cs.GPG_ENCRYPT[-2:], ("--compress-algo", "none"))

    def test_b_the_probe_round_trip_uses_the_seal_argv(self):
        """Every encryption in a PG run, the synthetic round trip included, uses exactly cs.GPG_ENCRYPT."""
        argvs = []
        real = cs.gpg_run

        def spy(argv, *a, **k):
            argvs.append(tuple(argv))
            return real(argv, *a, **k)
        with mock.patch.object(cs, "gpg_run", spy):
            rc, out = self.go()
        self.assertEqual(rc, 0, out)
        enc = [a for a in argvs if "--symmetric" in a]
        self.assertGreater(len(enc), 2)                                   # the probe, each product, the manifest
        self.assertEqual(set(enc), {cs.GPG_ENCRYPT})
        self.assertEqual(argvs[0], cs.GPG_ENCRYPT)                        # the probe comes first

    # the gen-spec names no task seed
    def test_a_gen_spec_naming_a_task_seed_is_refused_before_generation(self):
        for tag, seed, escape in (("pattern", BASE, False), ("count", BASE + 10_006, False),
                                  ("escaped", BASE + 2, True)):
            with self.subTest(tag):
                self.tearDown()
                self.setUp()
                gen = write_gen(self.d)
                req = [{"pattern": f"gntp.{seed}.ghep.root", "count": 1}] if tag != "count" else \
                    [{"pattern": "gntp.*.ghep.root", "count": seed}]
                spec = write_spec(self.d, gen, required=req)
                if escape:
                    spec.write_text(spec.read_text().replace(str(seed), "".join(f"\\u{ord(c):04x}" for c in str(seed))))
                    self.assertNotIn(str(seed), spec.read_text())
                rc, out = self.go(spec=spec)
                s = self.summary(out)
                self.assertEqual(rc, 1, out)
                self.assertEqual(s["refused"], "the gen-spec names a task seed")
                self.assertNotIn("synthetic_round_trip", s)
                self.assertEqual(list(self.w.iterdir()), [])
                self.assertFalse(os.path.lexists(self.s))
                self.assertNotIn(str(seed), out)


class GenSpecPin(PGBase):
    """The director's rulings (i), (ii) and (iii) of 2026-11-25: the gen-spec's bytes are pinned by --gen-spec-sha256;
    every env_keep name must be set, none twice; env_set's literal values are set in the generator's environment, and
    an inherited different value refuses. Each failure refuses before the job check, with W untouched."""

    # the gen-spec pinned by its sha256 (ruling (ii))
    def nothing_ran(self, out, refused):
        s = self.summary(out)
        self.assertEqual(s["refused"], refused)
        self.assertIs(s["spec_ok"], False)
        self.assertNotIn("step_cgroup_pre", s)
        self.assertNotIn("synthetic_round_trip", s)
        self.assertEqual(list(self.w.iterdir()), [])
        self.assertFalse(os.path.lexists(self.s))
        self.assertNotIn("covfix-receipt", out)

    def test_ii_a_gen_spec_off_its_pin_is_refused_before_anything_runs(self):
        with mock.patch.object(pg.Generator, "run", side_effect=AssertionError("generated")) as run:
            rc, out = self.go(spec_sha="0" * 64)
        self.assertEqual(rc, 1, out)
        self.nothing_ran(out, "the gen-spec's sha256 is not its pin")
        run.assert_not_called()

    def test_ii_the_pin_must_be_64_lowercase_hex(self):
        gen = write_gen(self.d)
        sha = fsha(write_spec(self.d, gen))
        for bad in (sha.upper(), sha[:63], "x" * 64):
            with self.subTest(bad=bad[:8]):
                rc, out = self.go(spec_sha=bad)
                self.assertEqual(rc, 1, out)
                self.assertNotIn("covfix-receipt", out)
                self.assertEqual(list(self.w.iterdir()), [])
        out = io.StringIO()
        rc = pg.main(["--covfix-attempt", ATT, "--workdir", str(self.w), "--sealed", str(self.s), "--gen-spec",
                      str(self.d / "spec.json"), "--gen-spec-sha256", sha.upper(), "--gpg", GPG, "--gpgconf", GPGCONF,
                      "--gpg-sha256", fsha(GPG), "--gpgconf-sha256", fsha(GPGCONF)], stdin=io.BytesIO(FRAME), stdout=out)
        self.assertEqual(rc, 1)
        self.assertEqual(json.loads(out.getvalue()), {"refused": "the gen-spec pin must be 64 lowercase hex"})
        with self.assertRaises(SystemExit):                              # the pin is required
            pg.main(["--covfix-attempt", ATT, "--workdir", str(self.w), "--sealed", str(self.s), "--gen-spec",
                     str(self.d / "spec.json"), "--gpg", GPG, "--gpgconf", GPGCONF, "--gpg-sha256", fsha(GPG),
                     "--gpgconf-sha256", fsha(GPGCONF)], stdin=io.BytesIO(FRAME), stdout=io.StringIO())

    def test_ii_the_spec_is_parsed_from_the_bytes_it_hashed(self):
        gen = write_gen(self.d)
        sp = write_spec(self.d, gen)
        pinned = sp.read_bytes()
        swapped = json.dumps({**json.loads(pinned), "tunes": ["SWAPPED_A", "SWAPPED_B"]})
        real = hashlib.sha256

        def swap_after_hash(b=b""):                  # the file changes right after its bytes are hashed
            h = real(b)
            if b == pinned:
                sp.write_text(swapped)
            return h
        with mock.patch.dict(os.environ, {"FAKE_MODE": "ok", "SPILL_ROOT": "x"}), \
                mock.patch.object(pg.hashlib, "sha256", swap_after_hash):
            spec = pg.load_spec(sp, real(pinned).hexdigest())
        self.assertEqual(sp.read_text(), swapped)
        self.assertEqual(spec["tunes"], ["G21_11a_00_000", "G18_02a_00_000"])

    # literal values pinned in the gen-spec (the director's ruling (iii) of 2026-11-25)
    PIN = "0123456789abcdef0123456789abcdef01234567"

    def test_iii_an_inherited_value_that_differs_from_env_set_is_refused_before_anything_runs(self):
        gen = write_gen(self.d)
        spec = write_spec(self.d, gen, env_set={"PG_DEPLOY_PIN": self.PIN})
        with mock.patch.object(pg.Generator, "run", side_effect=AssertionError("generated")) as run:
            rc, out = self.go(spec=spec, PG_DEPLOY_PIN="f" * 40)
        self.assertEqual(rc, 1, out)
        self.nothing_ran(out, "an env_set variable is inherited with a different value")
        run.assert_not_called()
        self.assertNotIn("f" * 40, out)
        self.assertNotIn(self.PIN, out)

    def test_iii_env_set_values_reach_the_generator(self):
        for tag, inherited in (("absent", None), ("equal", self.PIN)):
            with self.subTest(tag), mock.patch.dict(os.environ):
                self.tearDown()
                self.setUp()
                os.environ.pop("PG_DEPLOY_PIN", None)
                os.environ.pop("COVFIX_TEST_SET", None)
                gen = write_gen(self.d)
                spec = write_spec(self.d, gen, env_set={"PG_DEPLOY_PIN": self.PIN, "COVFIX_TEST_SET": "a value"})
                extra = {} if inherited is None else {"PG_DEPLOY_PIN": inherited}
                rc, out = self.go(mode="envset", spec=spec, **extra)
                self.assertEqual(rc, 0, out)
                self.assertEqual(json.loads(self.unseal("envset.json")),
                                 {"PG_DEPLOY_PIN": self.PIN, "COVFIX_TEST_SET": "a value"})

    # every env_keep name present, none twice (ruling (i))
    def test_i_a_listed_env_keep_name_that_is_not_set_is_refused_before_anything_runs(self):
        for name in ("SLURM_JOB_ID", "SLURM_CPUS_ON_NODE", "COVFIX_TEST_UNSET"):
            with self.subTest(name), mock.patch.dict(os.environ):
                self.tearDown()
                self.setUp()
                os.environ.pop(name, None)
                with mock.patch.object(pg.Generator, "run", side_effect=AssertionError("generated")) as run:
                    rc, out = self.go(env_keep=("FAKE_MODE", "PATH", "SPILL_ROOT", name))
                self.assertEqual(rc, 1, out)
                self.nothing_ran(out, "an env_keep variable is not set")
                run.assert_not_called()

    def test_i_set_slurm_names_pass_and_reach_the_generator(self):
        rc, out = self.go(env_keep=("FAKE_MODE", "PATH", "SPILL_ROOT", "SLURM_JOB_ID", "SLURM_CPUS_ON_NODE"),
                          SLURM_JOB_ID="61935360", SLURM_CPUS_ON_NODE="256")
        self.assertEqual(rc, 0, out)
        env = json.loads(self.unseal("env.json"))
        self.assertTrue({"SLURM_JOB_ID", "SLURM_CPUS_ON_NODE"} <= set(env), env)    # env.json holds the names

    def test_i_an_env_keep_name_listed_twice_is_refused(self):
        with mock.patch.object(pg.Generator, "run", side_effect=AssertionError("generated")) as run:
            rc, out = self.go(env_keep=("FAKE_MODE", "PATH", "SPILL_ROOT", "PATH"))
        self.assertEqual(rc, 1, out)
        self.nothing_ran(out, "an env_keep variable is listed twice")
        run.assert_not_called()


class RehearsalContract(PGBase):
    """pg_generate.sh's contract with its parent (tune-generator, 3d-unfolding/genie/pg_generate.sh a6cdf3df): it refuses
    unless TMPDIR is W/tmp, a real directory of this user's at mode 0700 (the director's ruling of 2026-11-26)."""

    def test_w_tmp_is_mode_0700_under_umask_022(self):
        old = os.umask(0o022)
        try:
            rc, out = self.go(mode="tmpmode")
        finally:
            os.umask(old)
        self.assertEqual(rc, 0, out)
        self.assertEqual(json.loads(self.unseal("tmpmode.json")), {"dir": True, "mode": "0o700", "own": True})

    def test_private_dir_is_0700_whatever_the_umask(self):
        for i, mask in enumerate((0o022, 0o277, 0o000)):          # 0o277 strips the owner's own bits from mkdir's mode
            with self.subTest(umask=oct(mask)):
                p = self.d / f"priv{i}"
                old = os.umask(mask)
                try:
                    pg.private_dir(p)
                finally:
                    os.umask(old)
                st = os.lstat(p)
                self.assertTrue(stat.S_ISDIR(st.st_mode))
                self.assertEqual(stat.S_IMODE(st.st_mode), 0o700)
        with self.assertRaises(FileExistsError):                  # never reuses an existing directory
            pg.private_dir(self.d / "priv0")


class Decryptors(Base):
    """The director's rulings 3 and 4 of 2026-11-25: the decrypted manifest is seed-bearing (its paths and plaintext
    hashes), so it never prints, and PV's writers pass every output through publish_guard."""

    SEEDS = [1_234_567_890, 1_234_567_891, 1_234_577_890]
    H = hashlib.sha256(b"a seed-bearing trace").hexdigest()

    def man(self):
        return cs.SealedManifest({"p0001": self.H, "p0002": "1" * 64},
                                 {"p0001": "gntp.9876543210.ghep.root", "p0002": "out/G21/ratio.json"})

    def test_sm_prints_counts_only(self):
        m = self.man()
        for text in (repr(m), str(m), f"{m}", "%s" % (m,), str([m])):
            self.assertEqual(text.replace("[", "").replace("]", ""), "<SealedManifest: 2 products>")
            for secret in ("9876543210", "gntp", "ratio", self.H, "1" * 64):
                self.assertNotIn(secret, text)

    def test_sm_cannot_be_pickled_copied_or_dumped(self):
        import copy
        import pickle
        m = self.man()
        for call in (lambda: pickle.dumps(m), lambda: copy.copy(m), lambda: copy.deepcopy(m), lambda: json.dumps(m),
                     lambda: json.dumps({"m": m}), lambda: m["paths"], lambda: vars(m), lambda: list(m)):
            with self.assertRaises(TypeError):
                call()

    def test_sm_access_is_explicit(self):
        m = self.man()
        self.assertEqual(m.ids(), ["p0001", "p0002"])
        self.assertEqual((m.path("p0002"), m.sha256("p0001")), ("out/G21/ratio.json", self.H))
        self.assertEqual((len(m), "p0001" in m, "p0009" in m), (2, True, False))
        for call in (lambda: m.path("p0009"), lambda: m.sha256("p0009")):
            with self.assertRaises(cs.Refusal):
                call()
        self.assertEqual(cs.SealedManifest({"p0002": "1" * 64, "p0001": self.H}, {"p0002": "b", "p0001": "a"}).ids(),
                         ["p0001", "p0002"])

    def test_sm_is_read_only(self):
        m = self.man()
        with self.assertRaises(AttributeError):
            m.extra = 1
        with self.assertRaises(AttributeError):
            m._paths = {}
        with self.assertRaises(AttributeError):
            del m._paths
        m.ids().append("p0003")
        self.assertEqual(m.ids(), ["p0001", "p0002"])
        products, paths = {"p0001": self.H}, {"p0001": "a"}
        m2 = cs.SealedManifest(products, paths)
        products["p0002"], paths["p0001"] = "1" * 64, "changed"           # the caller's dicts, changed afterwards
        self.assertEqual((m2.ids(), m2.path("p0001")), (["p0001"], "a"))

    def test_read_product_takes_only_a_sealed_manifest(self):
        self.files(a=b"alpha")
        sm = cs.parse_seal(cs.seal(self.w, self.s, PW, TOOLS)["seal_text"])
        man = cs.open_manifest(self.s, sm, PW, TOOLS)
        self.assertIsInstance(man, cs.SealedManifest)
        plain = {"p0001": man.sha256("p0001"), "products": {"p0001": man.sha256("p0001")}, "paths": {"p0001": "a"}}
        with self.assertRaises(cs.Refusal):
            cs.read_product(self.s, sm, plain, "p0001", PW, TOOLS)
        self.assertEqual(cs.read_product(self.s, sm, man, "p0001", PW, TOOLS), b"alpha")

    # publish_guard
    def refused(self, data, seeds=SEEDS):
        with self.assertRaises(cs.Refusal) as e:
            cs.publish_guard(data, self.man(), seeds)
        self.assertEqual(str(e.exception), cs.PUBLISH_REFUSAL)          # a fixed message: never the secret

    def test_pg_a_seed_in_any_form_is_refused(self):
        s = self.SEEDS[2]
        for form in (str(s), "000" + str(s), f"{s:x}", f"{s:X}", f"0x{s:010x}", f"{s:#X}"):
            with self.subTest(form):
                self.refused(json.dumps({"toy": 3, "note": "run " + form}))
                self.refused(("run " + form).encode())                  # bytes too

    def test_pg_a_manifest_hash_or_a_seed_named_path_run_is_refused(self):
        self.refused("sha " + self.H)
        self.refused("sha " + self.H.upper())
        self.refused("x" + self.H[3:] + self.H[:3] + self.H)            # inside a longer hex run
        self.refused("trace 9876543210 done")                            # a 10+ digit run of a manifest relpath
        self.refused("trace 09876543210 done")

    def test_pg_a_clean_record_and_an_epoch_pass_with_the_seed_list(self):
        epoch = 1_790_000_000                                            # 2026-09: 10 digits, near the seed range
        rec = json.dumps({"truth": "u1", "toys": 300, "written_at": epoch, "file": "out/G21/ratio.json",
                          "sha256_of_published_table": "2" * 64})
        self.assertEqual(cs.publish_guard(rec, self.man(), self.SEEDS), rec)
        self.assertEqual(cs.publish_guard(rec.encode(), self.man(), self.SEEDS), rec.encode())

    def test_pg_with_no_seed_list_the_seed_range_is_the_fallback(self):
        """Fallback only: any 10-digit decimal in the seed range is refused, which refuses an epoch too."""
        self.refused("written_at 1790000000", seeds=None)
        self.refused("n 001234567999", seeds=None)                       # zero-padded
        self.refused("m 2147483646", seeds=None)                         # the largest value a seed can take
        self.refused("m 1000000000", seeds=None)                         # SEED_BASE_LO itself
        self.assertEqual(cs.publish_guard("n 999999999 m 2147483647", self.man(), None),
                         "n 999999999 m 2147483647")                       # just outside [SEED_BASE_LO, SEED_LIMIT)

    def test_pg_inputs_are_checked(self):
        for bad in ((b"x", {"products": {}, "paths": {}}, self.SEEDS), (b"x", self.man(), [True]),
                    (b"x", self.man(), ["1234567890"]), (b"x", self.man(), 1_234_567_890), (1, self.man(), None),
                    (b"x", self.man(), [])):                            # an empty list would disable the seed rule
            with self.subTest(bad=repr(bad[1:])), self.assertRaises(cs.Refusal):
                cs.publish_guard(*bad)

    # The director's ruling of 2026-11-25 on PG-PUBLISH-SHA256SUMS: a manifest hash passes only as the recomputed
    # sha256 of an export-allowlisted file published alongside; every other manifest hash still refuses.
    RATIO, EXTRA = b'{"ratio": 1.02}\n', b'{"note": "not exported"}\n'
    ALLOW = ["out/*/ratio.json"]

    def man2(self):
        return cs.SealedManifest({"p0001": self.H, "p0002": hashlib.sha256(self.RATIO).hexdigest(),
                                  "p0003": hashlib.sha256(self.EXTRA).hexdigest()},
                                 {"p0001": "out/G21/trace/open.txt", "p0002": "out/G21/ratio.json",
                                  "p0003": "out/G21/extra.json"})

    def sums(self, *bodies_rels):
        return "".join(f"{hashlib.sha256(b).hexdigest()}  {r}\n" for b, r in bodies_rels)

    def test_pg_an_allowlisted_published_files_hash_passes(self):
        text = self.sums((self.RATIO, "out/G21/ratio.json"))
        for data in (text, text.encode(), text.upper()):
            with self.subTest(type(data).__name__):
                self.assertEqual(cs.publish_guard(data, self.man2(), self.SEEDS,
                                                  published={"out/G21/ratio.json": self.RATIO}, allowlist=self.ALLOW),
                                 data)
        with self.assertRaises(cs.Refusal):                                # without the published file it refuses
            cs.publish_guard(text, self.man2(), self.SEEDS)

    def test_pg_a_trace_hash_still_refuses(self):
        ok = {"published": {"out/G21/ratio.json": self.RATIO}, "allowlist": self.ALLOW}
        for text in (self.sums((self.RATIO, "out/G21/ratio.json")) + f"{self.H}  out/G21/trace/open.txt\n",
                     "trace " + self.H.upper()):
            with self.subTest(text=text[-30:]), self.assertRaises(cs.Refusal):
                cs.publish_guard(text, self.man2(), self.SEEDS, **ok)
        with self.assertRaises(cs.Refusal):                                # a seed still refuses beside a passed hash
            cs.publish_guard(self.sums((self.RATIO, "out/G21/ratio.json")) + str(self.SEEDS[0]), self.man2(),
                             self.SEEDS, **ok)

    def test_pg_a_hash_of_a_file_outside_the_allowlist_refuses(self):
        text = self.sums((self.EXTRA, "out/G21/extra.json"))
        for published in ({"out/G21/ratio.json": self.RATIO},                # not published: still a sealed hash
                          {"out/G21/ratio.json": self.RATIO, "out/G21/extra.json": self.EXTRA}):  # published, not allowed
            with self.subTest(published=sorted(published)), self.assertRaises(cs.Refusal):
                cs.publish_guard(text, self.man2(), self.SEEDS, published=published, allowlist=self.ALLOW)

    def test_pg_the_exemption_is_recomputed_and_must_be_in_the_manifest(self):
        for published in ({"out/G21/ratio.json": self.RATIO + b" "},        # content that does not hash to its entry
                          {"out/G22/ratio.json": self.RATIO}):              # allowlisted, but not in the manifest
            with self.subTest(published=sorted(published)), self.assertRaises(cs.Refusal):
                cs.publish_guard("clean", self.man2(), self.SEEDS, published=published, allowlist=self.ALLOW)

    def test_pg_the_exemption_inputs_are_checked(self):
        pub = {"out/G21/ratio.json": self.RATIO}
        for kw in ({"published": pub}, {"allowlist": self.ALLOW}, {"published": pub, "allowlist": []},
                   {"published": {}, "allowlist": self.ALLOW}, {"published": pub, "allowlist": "out/*/ratio.json"},
                   {"published": {"out/G21/ratio.json": self.RATIO.decode()}, "allowlist": self.ALLOW},
                   {"published": pub, "allowlist": [""]}):
            with self.subTest(kw=sorted(kw)), self.assertRaises(cs.Refusal):
                cs.publish_guard("clean", self.man2(), self.SEEDS, **kw)


@unittest.skipUnless(hasattr(os, "O_NOATIME"), "O_NOATIME is Linux-only")
class NoAtime(unittest.TestCase):
    def test_product_reads_use_o_noatime(self):
        seen = []
        real = os.open

        def spy(path, flags, *a):
            seen.append(flags)
            return real(path, flags, *a)
        with tempfile.NamedTemporaryFile() as f, mock.patch.object(cs.os, "open", spy):
            cs.noatime_read(Path(f.name))
            cs.regular_read(Path(f.name))
        self.assertTrue(all(fl & os.O_NOATIME for fl in seen))


if __name__ == "__main__":
    unittest.main()
