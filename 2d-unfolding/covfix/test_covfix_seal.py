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
                    "--cipher-algo AES256 --s2k-digest-algo SHA512 --force-mdc")
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
if mode == "mutate":
    open(sys.argv[0], "a").write("\n# changed\n")
if mode == "seeddir":
    dn = os.path.join(tmp, "run-%d" % seeds["tunes"][0]["task_seeds"][1], "inner")
    os.makedirs(dn)
    open(os.path.join(dn, "a.log"), "w").write("benign")
if mode == "seedlink":
    os.symlink("/nonexistent/%d" % seeds["tunes"][1]["task_seeds"][2], os.path.join(tmp, "plain-link"))
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
               command0: str | None = None, required=None) -> Path:
    s = d / "spec.json"
    s.write_text(json.dumps({"command": [command0 or str(gen)],
                             "command_sha256": sha or hashlib.sha256(gen.read_bytes()).hexdigest(),
                             "tunes": ["G21_11a_00_000", "G18_02a_00_000"], "env_keep": list(env_keep),
                             "required": REQUIRED if required is None else required}))
    return s


def fake_step(d: Path, extra_pids=(), cgroup_line="0::/slurm/job1/step0", readable=True):
    """A fake /proc and /sys/fs/cgroup: the step holds this process, its parent and any extra pids."""
    proc, cg = d / "fakeproc", d / "fakecgroup"
    me, parent = os.getpid(), os.getppid()
    for pid, ppid in ((me, parent), (parent, 1)):
        (proc / str(pid)).mkdir(parents=True, exist_ok=True)
        (proc / str(pid) / "stat").write_text(f"{pid} (a b) S {ppid} 0 0\n")
    for x in extra_pids:                              # an int (parent pid 1) or (pid, parent pid)
        pid, ppid = x if isinstance(x, tuple) else (x, 1)
        (proc / str(pid)).mkdir(parents=True, exist_ok=True)
        (proc / str(pid) / "stat").write_text(f"{pid} (gevgen) S {ppid} 0 0\n")
    extra_pids = [x[0] if isinstance(x, tuple) else x for x in extra_pids]
    (proc / "self").mkdir(exist_ok=True)
    (proc / "self" / "cgroup").write_text(cgroup_line + "\n")
    step = cg / "slurm" / "job1" / "step0"
    step.mkdir(parents=True, exist_ok=True)
    if readable:
        (step / "cgroup.procs").write_text("".join(f"{p}\n" for p in (me, parent, *extra_pids)))
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
        self.assertEqual(r["hashes"], {"p0001": hashlib.sha256(b"alpha").hexdigest(),
                                       "p0002": hashlib.sha256(b"beta").hexdigest()})
        man = json.loads(cs.gpg_run(cs.GPG_DECRYPT, PW, (self.s / "PG-MANIFEST.json.gpg").read_bytes(), TOOLS))
        self.assertEqual(man, {"products": r["hashes"], "paths": {"p0001": "a", "p0002": "sub/b"}})
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
        self.assertEqual(man["paths"], {"p0001": "a", "p0002": "sub/b"})
        self.assertEqual(cs.read_product(self.s, sm, man, "p0002", PW, TOOLS), b"beta")

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
        short = dict(man, products={"p0001": man["products"]["p0001"]})
        with self.assertRaises(cs.Refusal) as e:
            cs.read_product(self.s, sm, short, "p0002", PW, TOOLS)
        self.assertNotIsInstance(e.exception, cs.Break)

    def test_plaintext_not_its_manifest_hash_is_a_break(self):
        sm = self.sealed()
        man = cs.open_manifest(self.s, sm, PW, TOOLS)
        bad = dict(man, products=dict(man["products"], p0001="0" * 64))
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
           sealed=None, command0=None, scratch=True, spec=None, workdir=None, **env):
        gen = write_gen(self.d)
        spec = spec or write_spec(self.d, gen, sha, env_keep, command0)
        out = io.StringIO()
        base_env = {"FAKE_MODE": mode, "SECRETISH": "should-not-pass", "SPILL_ROOT": str(self.scratch)}
        if scratch:
            base_env["SCRATCH"] = str(self.scratch)
        with mock.patch.dict(os.environ, {**base_env, **env}):
            if not scratch:
                os.environ.pop("SCRATCH", None)
            rc = pg.main(["--covfix-attempt", attempt, "--workdir", str(workdir or self.w), "--sealed", str(sealed or self.s),
                          "--gen-spec", str(spec), "--gpg", GPG, "--gpgconf", GPGCONF,
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
                      "--gpg", "gpg", "--gpgconf", GPGCONF, "--gpg-sha256", fsha(GPG),
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
        for bad in ({**good, "extra": 1}, {**good, "tunes": ["one"]}, {**good, "command": []},
                    {**good, "env_keep": ["TMPDIR"]}, {**good, "command_sha256": "x"}, [1],
                    {**good, "command": ["rel/gen.py"]}):
            with self.subTest(bad=str(bad)[:40]):
                p = self.d / "bad.json"
                p.write_text(json.dumps(bad))
                with self.assertRaises(cs.Refusal):
                    pg.load_spec(p)
        with self.assertRaises(cs.Refusal):
            pg.load_spec(self.d / "absent.json")
        p = self.d / "nocmd.json"
        p.write_text(json.dumps({**good, "command": [str(self.d / "absent")]}))
        with self.assertRaises(cs.Refusal):
            pg.load_spec(p)

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

    def test_f8_off_the_main_thread_and_under_the_default_handler(self):
        import threading
        out = []
        th = threading.Thread(target=lambda: out.append(cs.gpg_run(cs.GPG_ENCRYPT, PW, b"t", TOOLS)))
        th.start()
        th.join()
        self.assertTrue(out and out[0])                                 # no handler to hold a SIGTERM there; it runs
        real_run = cs.subprocess.run

        def term_then_run(*a, **k):
            signal.raise_signal(signal.SIGTERM)                         # held by gpg_run's recorder (not os.kill,
            return real_run(*a, **k)                                    # which the test patches)

        old = signal.signal(signal.SIGTERM, signal.SIG_DFL)
        try:
            with mock.patch.object(cs.subprocess, "run", term_then_run), mock.patch.object(cs.os, "kill") as kill:
                cs.gpg_run(cs.GPG_ENCRYPT, PW, b"u", TOOLS)
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
        for req in ([], [{"pattern": "../x", "count": 1}], [{"pattern": "a", "count": 0}], [{"pattern": "a"}],
                    [{"pattern": "/abs", "count": 1}], "x"):
            with self.subTest(req=req), self.assertRaises(cs.Refusal):
                pg.load_spec(write_spec(self.d, gen, required=req))

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
        for kw in ({"readable": False}, {"cgroup_line": "4:memory:/slurm/job1"},
                   {"cgroup_line": "0::/slurm/job1/step0\n4:memory:/slurm/job1"}):      # hybrid: not a single v2 entry
            with self.subTest(kw=kw):
                proc, cg = fake_step(self.d / str(len(kw)) / next(iter(kw)), **kw)
                with mock.patch.object(pg, "PROC", str(proc)), mock.patch.object(pg, "CGROUP_ROOT", str(cg)), \
                        self.assertRaises(cs.Refusal):
                    pg.step_cgroup_check()

    def test_f7_a_run_with_an_escaped_process_has_no_receipt(self):
        proc, cg = fake_step(self.d / "y", extra_pids=(424243,))
        with mock.patch.object(pg, "PROC", str(proc)), mock.patch.object(pg, "CGROUP_ROOT", str(cg)):
            rc, out = self.go()
        self.assertEqual(rc, 1, out)
        self.assertIn("cgroup", self.summary(out)["refused"])
        self.assertNotIn("covfix-receipt", out)


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
