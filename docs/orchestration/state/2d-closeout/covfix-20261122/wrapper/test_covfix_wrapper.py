"""Tests for covfix_wrapper.py.

HARD RULES these tests keep: Keychain items are covfix-test-<random>-* only, created and deleted here, and
COVFIX_FORBID_REAL_KEYCHAIN is set so the real covfix-* prefix refuses; ssh, salloc and srun are local stubs and
nothing leaves this machine (git runs with no global or system config, file transport only); every seal digest is a
synthetic one built here, so no test is a launch.

    python3 -W error::ResourceWarning -m unittest -v test_covfix_wrapper
"""
import contextlib
import hashlib
import io
import json
import os
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import covfix_wrapper as cw  # noqa: E402

os.environ[cw.FORBID_REAL_ENV] = "1"
os.environ.update({"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1", "GIT_ALLOW_PROTOCOL": "file",
                   "GIT_TERMINAL_PROMPT": "0"})
PREFIXES = []
TMP = tempfile.mkdtemp(prefix="covfix-wrapper-test-")
REF = os.path.join(HERE, "reference_role.py")
REL = "docs/orchestration/state/2d-closeout/covfix-20261122/consumption/RECORD.jsonl"


def new_prefix() -> str:
    p = f"covfix-test-{secrets.token_hex(4)}-"
    PREFIXES.append(p)
    return p


def delete_items(prefix: str) -> None:
    assert prefix.startswith("covfix-test-"), prefix
    for item in cw.ITEMS:
        subprocess.run([cw.SECURITY, "delete-generic-password", "-s", prefix + item, "-a", cw.ACCOUNT,
                        cw.login_keychain()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def tearDownModule():
    for p in PREFIXES:
        delete_items(p)
    shutil.rmtree(TMP, ignore_errors=True)


def slurp(path, mode="r"):
    with open(path, mode) as f:
        return f.read()


def run_main(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = cw.main(list(argv))
    return rc, out.getvalue(), err.getvalue()


def ssh_stub(body: str) -> str:
    """A stand-in ssh that drops its options, takes <host> <command>, and runs body (or the command if body is
    "RUN") under bash, with stdin forwarded."""
    d = tempfile.mkdtemp(dir=TMP)
    path = os.path.join(d, "ssh")
    with open(path, "w") as f:
        f.write("#!/bin/bash\nwhile [ \"${1#-}\" != \"$1\" ]; do [ \"$1\" = -o ] && shift; shift; done\n"
                "host=$1; cmd=$2\n" + ('exec bash -c "$cmd"\n' if body == "RUN" else body + "\n"))
    os.chmod(path, 0o755)
    return path


def git(cwd, *args):
    r = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True)
    assert r.returncode == 0, (args, r.stderr)
    return r.stdout


STUB_SSH = r'''#!{python}
import json, os, subprocess, sys
here = {here!r}
args = sys.argv[1:]
opts = []
while args and args[0].startswith("-"):
    n = 2 if args[0] == "-o" else 1
    opts += args[:n]
    args = args[n:]
host, command = args[0], args[1]
with open(os.path.join(here, "ssh-log.jsonl"), "a") as f:
    f.write(json.dumps({{"argv": sys.argv, "opts": opts, "env": dict(os.environ)}}) + "\n")
mp = os.path.join(here, "ssh-mode")
mode = open(mp).read().strip() if os.path.exists(mp) else ""
if mode == "down":
    sys.exit(255)
hashing = "covfix-hash-end" in command
if not hashing:
    # a launch: record what the pushed mirror held at the moment the binary started
    r = subprocess.run(["git", "--git-dir", {bare!r}, "cat-file", "blob", "covfix-consumption:" + {rel!r}],
                       capture_output=True, text=True)
    with open(os.path.join(here, "at-launch.txt"), "w") as f:
        f.write(r.stdout)
    if mode == "drop-link":
        sys.stdin.read()
        sys.exit(255)
    if mode == "exit0-unread":
        sys.exit(0)
if mode == "no-end" and hashing:
    r = subprocess.run(["bash", "-c", command], stdout=subprocess.PIPE)
    sys.stdout.write("".join(r.stdout.decode().splitlines(keepends=True)[:-1]))
    sys.exit(r.returncode)
if mode == "junk" and hashing:
    r = subprocess.run(["bash", "-c", command], stdout=subprocess.PIPE)
    sys.stdout.write("a stray line\n" + r.stdout.decode())
    sys.exit(r.returncode)
if mode == "rc1" and hashing:
    subprocess.run(["bash", "-c", command])
    sys.exit(1)
if mode == "extra" and hashing:
    r = subprocess.run(["bash", "-c", command], stdout=subprocess.PIPE)
    sys.stdout.write("covfix-missing invented\n" + r.stdout.decode())
    sys.exit(r.returncode)
sys.exit(subprocess.run(["bash", "-c", command]).returncode)
'''

STUB_ALLOC = r'''#!/bin/bash
# stub salloc/srun: drop "--exclusive -N 1", exec the rest with stdin forwarded
[ "$1" = "--exclusive" ] && [ "$2" = "-N" ] && [ "$3" = "1" ] || {{ echo "stub {name}: unexpected flags $*" >&2; exit 64; }}
shift 3
exec "$@"
'''


class Rig:
    """One isolated campaign: test Keychain items, a synthetic seal, a bare 'origin', a mirror worktree, stubs,
    and a role config whose binding pins the synthetic digests and the commitment."""

    def __init__(self, role_flags=None):
        self.root = tempfile.mkdtemp(dir=TMP)
        self.prefix = new_prefix()
        self.kc = cw.Keychain(self.prefix)
        assert cw.generate(self.kc) == "created"
        self.bin = os.path.join(self.root, "bin")
        os.makedirs(self.bin)
        self.bare = os.path.join(self.root, "origin.git")
        subprocess.run(["git", "init", "-q", "--bare", self.bare], check=True)
        self.wt = os.path.join(self.root, "mirror")
        subprocess.run(["git", "init", "-q", "-b", "covfix-consumption", self.wt], check=True)
        with open(os.path.join(self.wt, "README"), "w") as f:
            f.write("mirror\n")
        git(self.wt, "add", "README")
        git(self.wt, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "init")
        git(self.wt, "remote", "add", "origin", self.bare)
        git(self.wt, "push", "-q", "origin", "HEAD:refs/heads/covfix-consumption")
        with open(os.path.join(self.bin, "ssh"), "w") as f:
            f.write(STUB_SSH.format(python=sys.executable, here=self.root, bare=self.bare, rel=REL))
        for name in ("salloc", "srun"):
            with open(os.path.join(self.bin, name), "w") as f:
                f.write(STUB_ALLOC.format(name=name))
        for name in ("ssh", "salloc", "srun"):
            os.chmod(os.path.join(self.bin, name), 0o755)
        self.seal = cw.synthetic_seal(self.kc, os.path.join(self.root, "synthetic"))
        flags = role_flags or {}
        roles = {}
        for role in cw.ROLES:
            launcher = ([f"{self.bin}/salloc", "--exclusive", "-N", "1", f"{self.bin}/srun", "--exclusive", "-N", "1"]
                        if role != "pg-connect" else [])
            roles[role] = {"launcher": launcher, "binary": REF, "binary_sha256": cw.sha256_file(REF),
                           "args": ["--role", role, "--sealed", self.seal["seal_root"], *flags.get(role, [])]}
        self.cfg = {
            "record_dir": os.path.join(self.root, "record"),
            "keychain_prefix": self.prefix,
            "ssh": [os.path.join(self.bin, "ssh")], "host": "stub-login",
            "binding": {"commitment": self.commitment(), "seal_digest": self.seal["seal_digest"],
                        "freeze_digest": self.seal["freeze_digest"]},
            "seal_file": os.path.join(self.root, "synthetic", "PG-SEAL.sha256"),
            "seal_root": self.seal["seal_root"],
            "freeze_file": os.path.join(self.root, "synthetic", "P2-FREEZE.sha256"),
            "freeze_root": self.seal["freeze_root"],
            "mirror": {"worktree": self.wt, "path": REL, "remote": "origin", "branch": "covfix-consumption"},
            "roles": roles,
        }
        self.write_config()

    def write_config(self):
        self.config = os.path.join(self.root, "roles.json")
        with open(self.config, "w") as f:
            json.dump(self.cfg, f, indent=1, sort_keys=True)
        self.config_sha = cw.sha256_file(self.config)

    def commitment(self):
        return cw.commitment_digest(int(self.kc.read("seed-base")), self.kc.read("salt"))

    def argv(self, role, **kw):
        argv = ["run", "--config", self.config, "--config-sha256", kw.get("config_sha", self.config_sha),
                "--role", role]
        if role == "pg-connect":
            argv += ["--commitment", kw.get("commitment", self.cfg["binding"]["commitment"])]
        else:
            argv += ["--seal-digest", kw.get("seal", self.cfg["binding"]["seal_digest"]),
                     "--freeze-digest", kw.get("freeze", self.cfg["binding"]["freeze_digest"])]
        return argv

    def run(self, role, **kw):
        return run_main(*self.argv(role, **kw))

    def events(self):
        return cw.Record(self.cfg["record_dir"]).lines()

    def markers(self):
        return cw.Record(self.cfg["record_dir"]).markers()

    def remote_record(self):
        r = subprocess.run(["git", "--git-dir", self.bare, "cat-file", "blob", f"covfix-consumption:{REL}"],
                           capture_output=True)
        return r.stdout if r.returncode == 0 else b""

    def ssh_log(self):
        path = os.path.join(self.root, "ssh-log.jsonl")
        if not os.path.exists(path):
            return []
        with open(path) as f:
            return [json.loads(x) for x in f]

    def set_ssh_mode(self, mode):
        with open(os.path.join(self.root, "ssh-mode"), "w") as f:
            f.write(mode)

    def launched(self):
        return os.path.exists(os.path.join(self.root, "at-launch.txt"))

    def secrets(self):
        return [self.kc.read(i) for i in cw.ITEMS]


# ------------------------------------------------------------------------------------------------------------

class KeychainTests(unittest.TestCase):
    def test_real_prefix_is_forbidden_under_the_test_guard(self):
        with self.assertRaises(cw.Stop) as cm:
            cw.Keychain("covfix-")
        self.assertEqual(cm.exception.code, cw.ERROR)

    def test_real_prefix_is_accepted_without_the_guard_but_never_queried_here(self):
        with mock.patch.dict(os.environ, {cw.FORBID_REAL_ENV: ""}):
            self.assertEqual(cw.Keychain("covfix-").service("salt"), "covfix-salt")

    def test_prefix_shapes(self):
        for bad in ("covfix", "covfix-x-", "other-", "covfix-test", "covfix-testx-", "covfix-test-A-"):
            with self.assertRaises(cw.Stop, msg=bad):
                cw.Keychain(bad)
        for good in ("covfix-test-", "covfix-synth-", "covfix-test-ab12-"):
            cw.Keychain(good)

    def test_every_call_names_the_login_keychain(self):
        kc = cw.Keychain(new_prefix())
        self.assertTrue(kc.keychain.endswith("login.keychain-db"), kc.keychain)
        calls = []
        real_run = subprocess.run

        def spy(argv, *a, **k):
            calls.append((list(argv), k.get("input")))
            return real_run(argv, *a, **k)

        with mock.patch.object(cw.subprocess, "run", spy):
            cw.generate(kc)
            kc.read("salt")
        for argv, inp in calls:
            if argv[1] == "find-generic-password":
                self.assertEqual(argv[-1] if argv[-1] != "-w" else argv[-2], kc.keychain)
                self.assertEqual(argv[-1], kc.keychain)
            if argv == [cw.SECURITY, "-i"]:
                self.assertTrue(inp.decode().rstrip("\n").endswith(" " + kc.keychain))

    def test_generate_creates_then_refuses_and_never_overwrites(self):
        kc = cw.Keychain(new_prefix())
        calls = []
        real_run = subprocess.run

        def spy(argv, *a, **k):
            calls.append(list(argv))
            return real_run(argv, *a, **k)

        with mock.patch.object(cw.subprocess, "run", spy):
            self.assertEqual(cw.generate(kc), "created")
        values = [kc.read(i) for i in cw.ITEMS]
        for argv in calls:
            for v in values:
                self.assertFalse(any(v in arg for arg in argv), f"secret on argv: {argv[:3]}")
        self.assertTrue(any(argv == [cw.SECURITY, "-i"] for argv in calls))
        self.assertEqual(cw.generate(kc), "exists")
        self.assertEqual([kc.read(i) for i in cw.ITEMS], values)
        pw, base, salt = values
        self.assertRegex(pw, r"^[0-9a-f]{64}$")
        self.assertRegex(salt, r"^[0-9a-f]{64}$")
        self.assertTrue(cw.SEED_BASE_LO <= int(base) < cw.SEED_BASE_HI)
        self.assertNotEqual(pw, salt)

    def test_generate_cli_prints_only_created_or_exists(self):
        p = new_prefix()
        rc, out, err = run_main("generate", "--keychain-prefix", p)
        self.assertEqual((rc, out, err), (0, "created\n", ""))
        rc, out, err = run_main("generate", "--keychain-prefix", p)
        self.assertEqual((rc, out, err), (0, "exists\n", ""))

    def test_a_partial_set_is_an_error_that_names_items_and_changes_nothing(self):
        kc = cw.Keychain(new_prefix())
        kc.add("salt", "ab" * 32)
        with self.assertRaises(cw.Stop) as cm:
            cw.generate(kc)
        self.assertEqual(cm.exception.code, cw.ERROR)
        self.assertIn("present salt", str(cm.exception))
        self.assertIn("missing passphrase, seed-base", str(cm.exception))
        self.assertNotIn("ab" * 32, str(cm.exception))
        self.assertFalse(kc.exists("passphrase"))
        self.assertEqual(kc.read("salt"), "ab" * 32)

    def test_add_refuses_a_duplicate(self):
        kc = cw.Keychain(new_prefix())
        kc.add("salt", "cd" * 32)
        with self.assertRaises(cw.Stop) as cm:
            kc.add("salt", "ef" * 32)
        self.assertIn("already exists", str(cm.exception))
        self.assertEqual(kc.read("salt"), "cd" * 32)

    def test_add_rejects_values_that_could_inject_security_commands(self):
        kc = cw.Keychain(new_prefix())
        for bad in ("ab cd", "ab\nquit", "AB", ""):
            with self.assertRaises(ValueError):
                kc.add("salt", bad)

    def test_read_of_a_missing_item_refuses(self):
        with self.assertRaises(cw.Stop) as cm:
            cw.Keychain(new_prefix()).read("passphrase")
        self.assertEqual(cm.exception.code, cw.REFUSED)

    def test_a_failed_add_reports_what_the_keychain_now_holds_without_values(self):
        kc = cw.Keychain(new_prefix())
        real_add = cw.Keychain.add

        def add(self, item, value):
            if item == "salt":
                real_add(self, item, value)          # created, then the read-back "fails"
                raise cw.Stop(cw.ERROR, "boom")
            return real_add(self, item, value)

        with mock.patch.object(cw.Keychain, "add", add):
            with self.assertRaises(cw.Stop) as cm:
                cw.generate(kc)
        self.assertIn("now holds 3 of 3", str(cm.exception))
        for item in cw.ITEMS:
            self.assertNotIn(kc.read(item), str(cm.exception))


class CommitmentTests(unittest.TestCase):
    def test_encoding_is_decimal_colon_hex_without_newline(self):
        salt = "ab" * 32
        want = hashlib.sha256(b"1234567890:" + salt.encode()).hexdigest()
        self.assertEqual(cw.commitment_digest(1234567890, salt), want)

    def test_bad_inputs_refuse(self):
        for base, salt in ((999_999_999, "ab" * 32), (2_000_000_000, "ab" * 32), (1_000_000_000, "AB" * 32),
                           (1_000_000_000, "ab" * 31)):
            with self.assertRaises(cw.Stop):
                cw.commitment_digest(base, salt)

    def test_seed_base_bounds(self):
        self.assertEqual(cw.parse_seed_base("1000000000"), 1_000_000_000)
        self.assertEqual(cw.parse_seed_base("1999999999"), 1_999_999_999)
        for bad in ("999999999", "2000000000", "01000000000", "1e9", " 1000000000", "-1000000000"):
            with self.assertRaises(cw.Stop, msg=bad):
                cw.parse_seed_base(bad)

    def test_the_task_seed_bound_holds(self):
        top = cw.SEED_BASE_HI + cw.TUNE_STRIDE * (cw.N_TUNES - 1) + cw.MAX_TASK_INDEX
        self.assertEqual(top, 2_000_019_999)
        self.assertLess(top, 2**31 - 1)

    def test_cli_commitment_matches(self):
        p = new_prefix()
        kc = cw.Keychain(p)
        cw.generate(kc)
        rc, out, _ = run_main("commitment", "--keychain-prefix", p)
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), cw.commitment_digest(int(kc.read("seed-base")), kc.read("salt")))


class SumfileTests(unittest.TestCase):
    def test_parse(self):
        d = "a" * 64
        self.assertEqual(cw.parse_sumfile(f"{d}  x/y.gpg\n# c\n\n{d} *z\n".encode(), "s"),
                         {"x/y.gpg": d, "z": d})

    def test_rejections(self):
        d = "a" * 64
        for bad in (f"{d}  /abs\n", f"{d}  a/../b\n", f"{d}  a//b\n", f"{d}  x\n{d}  x\n", "", f"{d[:-1]}  x\n",
                    f"{d}\tx\n", f"{d.upper()}  x\n"):
            with self.assertRaises(cw.Stop, msg=bad):
                cw.parse_sumfile(bad.encode(), "s")
        with self.assertRaises(cw.Stop):
            cw.parse_sumfile(b"\xff", "s")


class RecordTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(dir=TMP)
        os.rmdir(self.dir)
        self.rec = cw.Record(self.dir)
        self.rec.ensure_dir()

    def add(self, **ev):
        self.rec.lock()
        try:
            return self.rec.append({"key": "1" * 64, "role": "pv-writer", "event": "spent", **ev})
        finally:
            self.rec.unlock()

    def test_dir_is_created_700_and_a_loose_mode_refuses(self):
        self.assertEqual(stat.S_IMODE(os.stat(self.dir).st_mode), 0o700)
        os.chmod(self.dir, 0o750)
        with self.assertRaises(cw.Stop):
            self.rec.ensure_dir()

    def test_chain(self):
        self.add()
        self.add(event="completed")
        ev = self.rec.lines()
        self.assertEqual([e["seq"] for e in ev], [0, 1])
        self.assertEqual(ev[0]["prev"], cw.GENESIS)
        self.assertEqual(ev[1]["prev"], hashlib.sha256(self.rec.raw().splitlines()[0]).hexdigest())

    def test_tamper_truncation_and_gaps_are_terminal(self):
        self.add()
        self.add(event="completed")
        good = self.rec.raw()
        lines = good.splitlines(keepends=True)
        for bad in (good[:-1], lines[1], good.replace(b'"pv-writer"', b'"pv-readout"', 1), lines[0] + lines[0],
                    b"not json\n", good.replace(b'"completed"', b'"bogus"'), b"[1]\n",
                    good.replace(b'"key":"' + b"1" * 64, b'"key":"' + b"1" * 63, 1)):
            with self.assertRaises(cw.Stop, msg=bad) as cm:
                cw.Record.parse(bad)
            self.assertEqual(cm.exception.code, cw.TERMINAL)

    def test_append_needs_the_lock(self):
        with self.assertRaises(AssertionError):
            self.rec.append({"key": "1" * 64, "role": "pv-writer", "event": "spent"})

    def test_a_held_lock_times_out(self):
        other = cw.Record(self.dir)
        other.lock()
        try:
            with mock.patch.object(cw, "LOCK_TIMEOUT_S", 0.3):
                with self.assertRaises(OSError):
                    self.rec.lock()
        finally:
            other.unlock()

    def test_blocked_and_freeze_binding(self):
        k, k2, k3 = "1" * 64, "2" * 64, "3" * 64
        ev = [{"seq": 0, "key": k, "role": "pv-writer", "event": "spent", "freeze": "f" * 64},
              {"seq": 1, "key": k2, "role": "pv-writer", "event": "break"},
              {"seq": 2, "key": k3, "role": "reveal", "event": "reveal"}]
        self.assertIsNotNone(cw.blocked(ev, [], k, "pv-writer"))
        self.assertIsNone(cw.blocked(ev, [], k, "pv-readout"))
        self.assertIsNotNone(cw.blocked(ev, [], k2, "pv-readout"))
        self.assertIsNotNone(cw.blocked(ev, [], k3, "pv-writer"))
        self.assertIsNone(cw.blocked(ev, [], "4" * 64, "pv-writer"))
        self.assertIsNotNone(cw.blocked([], [("attempt", k, "pv-writer")], k, "pv-writer"))
        self.assertIsNone(cw.blocked([], [("attempt", k, "pv-writer")], k, "pv-readout"))
        self.assertIsNotNone(cw.blocked([], [("break", k, "seal")], k, "pv-readout"))
        self.assertEqual(cw.bound_freeze(ev, k), "f" * 64)
        self.assertIsNone(cw.bound_freeze(ev, k2))

    def test_markers_are_durable_once_and_absorbed_into_the_chain(self):
        self.assertTrue(self.rec.mark("uncertain", "4" * 64, "pv-readout"))
        self.assertFalse(self.rec.mark("uncertain", "4" * 64, "pv-readout"))
        self.rec.mark("break", "5" * 64, "seal")
        self.rec.mark("attempt", "6" * 64, "pv-writer")
        self.assertEqual(sorted(self.rec.markers()), [("attempt", "6" * 64, "pv-writer"), ("break", "5" * 64, "seal"),
                                                      ("uncertain", "4" * 64, "pv-readout")])
        self.rec.lock()
        try:
            self.rec.absorb_markers()
            self.rec.absorb_markers()
        finally:
            self.rec.unlock()
        got = sorted((e["event"], e["key"][0], e["role"]) for e in self.rec.lines())
        self.assertEqual(got, [("break", "5", "seal"), ("uncertain", "4", "pv-readout"), ("uncertain", "6", "pv-writer")])

    def test_unreadable_marker_is_terminal(self):
        with open(os.path.join(self.dir, "MARK-junk"), "w") as f:
            f.write("x\n")
        with self.assertRaises(cw.Stop):
            self.rec.markers()


class GpgTests(unittest.TestCase):
    def test_round_trip_and_wrong_passphrase(self):
        pw = secrets.token_hex(32)
        ct = cw.gpg_run(cw.GPG_ENCRYPT, pw, b"payload")
        self.assertNotIn(b"payload", ct)
        self.assertEqual(cw.gpg_run(cw.GPG_DECRYPT, pw, ct), b"payload")
        with self.assertRaises(cw.Stop):
            cw.gpg_run(cw.GPG_DECRYPT, secrets.token_hex(32), ct)

    def test_mdc_failure_refuses(self):
        pw = secrets.token_hex(32)
        ct = bytearray(cw.gpg_run(cw.GPG_ENCRYPT, pw, b"x" * 4096))
        ct[len(ct) // 2] ^= 0xFF
        with self.assertRaises(cw.Stop):
            cw.gpg_run(cw.GPG_DECRYPT, pw, bytes(ct))

    def test_fd3_works_when_fd3_is_already_taken(self):
        pw = secrets.token_hex(32)
        holder = None
        try:
            if not _fd_open(3):
                holder = os.open(os.devnull, os.O_RDONLY)
            self.assertTrue(_fd_open(3))
            ct = cw.gpg_run(cw.GPG_ENCRYPT, pw, b"abc")
            self.assertEqual(cw.gpg_run(cw.GPG_DECRYPT, pw, ct), b"abc")
        finally:
            if holder is not None:
                os.close(holder)

    def test_fd3_works_when_the_pipe_lands_on_fd3(self):
        # a fresh interpreter has only fds 0-2, so gpg_run's pipe read end is fd 3 itself (the other branch of child)
        code = ("import os, sys; sys.path.insert(0, sys.argv[1]); import covfix_wrapper as cw\n"
                "real = os.pipe; got = []\n"
                "def pipe():\n    p = real(); got.append(p[0]); return p\n"
                "os.pipe = pipe\n"
                "pw = '7' * 64\n"
                "assert cw.gpg_run(cw.GPG_DECRYPT, pw, cw.gpg_run(cw.GPG_ENCRYPT, pw, b'q')) == b'q'\n"
                "assert got[0] == 3, got\n"
                "print('fd3 ok')\n")
        r = subprocess.run([sys.executable, "-c", code, HERE], capture_output=True, text=True, close_fds=True)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "fd3 ok"), r.stderr)

    def test_an_ambient_gpg_conf_has_no_effect(self):
        home = tempfile.mkdtemp(prefix="cfxa", dir="/tmp")
        try:
            os.chmod(home, 0o700)
            with open(os.path.join(home, "gpg.conf"), "w") as f:
                f.write("armor\n")
            with mock.patch.dict(os.environ, {"GNUPGHOME": home}):
                ct = cw.gpg_run(cw.GPG_ENCRYPT, secrets.token_hex(32), b"abc")
            self.assertFalse(ct.startswith(b"-----BEGIN"))
        finally:
            shutil.rmtree(home, ignore_errors=True)

    def test_pinned_flags(self):
        self.assertEqual(" ".join(cw.GPG_ENCRYPT), "gpg --batch --yes --pinentry-mode loopback --passphrase-fd 3 "
                         "--no-symkey-cache --symmetric --cipher-algo AES256 --s2k-digest-algo SHA512 --force-mdc")
        self.assertEqual(" ".join(cw.GPG_DECRYPT), "gpg --batch --pinentry-mode loopback --passphrase-fd 3 "
                         "--no-symkey-cache --decrypt")


def _fd_open(fd):
    try:
        os.fstat(fd)
        return True
    except OSError:
        return False


class SyntheticSealTests(unittest.TestCase):
    def test_layout_and_no_plaintext(self):
        kc = cw.Keychain(new_prefix())
        cw.generate(kc)
        out = os.path.join(tempfile.mkdtemp(dir=TMP), "s")
        info = cw.synthetic_seal(kc, out)
        names = sorted(os.listdir(info["seal_root"]))
        self.assertEqual(names, ["PG-MANIFEST.json.gpg", "synthetic-truth-u0.json.gpg"])
        seal = cw.parse_sumfile(slurp(os.path.join(out, "PG-SEAL.sha256"), "rb"), "seal")
        self.assertEqual(sorted(seal), names)
        for n, d in seal.items():
            self.assertEqual(cw.sha256_file(os.path.join(info["seal_root"], n)), d)
        self.assertEqual(info["seal_digest"], cw.sha256_file(os.path.join(out, "PG-SEAL.sha256")))
        for dirpath, _, files in os.walk(out):
            for f in files:
                self.assertNotIn(b'"r_u"', slurp(os.path.join(dirpath, f), "rb"))
        with self.assertRaises(cw.Stop):
            cw.synthetic_seal(kc, out)

    def test_refuses_the_real_prefix(self):
        with mock.patch.dict(os.environ, {cw.FORBID_REAL_ENV: ""}):
            kc = cw.Keychain("covfix-")
        with mock.patch.object(kc, "read", side_effect=AssertionError("read the real Keychain")):
            with self.assertRaises(cw.Stop):
                cw.synthetic_seal(kc, os.path.join(TMP, "never"))


class ConfigTests(unittest.TestCase):
    def test_a_wrong_pin_refuses(self):
        rig = Rig()
        rc, _, err = rig.run("pv-writer", config_sha="0" * 64)
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertEqual(rig.ssh_log(), [])

    def test_missing_keys_and_unreadable_files(self):
        path = os.path.join(TMP, "partial.json")
        with open(path, "w") as f:
            json.dump({"record_dir": "x"}, f)
        with self.assertRaises(cw.Stop):
            cw.load_config(path, cw.sha256_file(path))
        with self.assertRaises(cw.Stop) as cm:
            cw.load_config(os.path.join(TMP, "nope.json"), "0" * 64)
        self.assertEqual(cm.exception.code, cw.ERROR)
        with open(path, "w") as f:
            f.write("{not json")
        with self.assertRaises(cw.Stop):
            cw.load_config(path, cw.sha256_file(path))

    def test_digests_must_equal_the_binding(self):
        rig = Rig()
        for kw in ({"seal": "e" * 64}, {"freeze": "e" * 64}, {"seal": "xyz"}):
            rc, _, err = rig.run("pv-writer", **kw)
            self.assertEqual(rc, cw.REFUSED, (kw, err))
            self.assertIn("binding", err)
        self.assertEqual(rig.run("pg-connect", commitment="")[0], cw.REFUSED)
        self.assertEqual(rig.events(), [])
        self.assertEqual(rig.ssh_log(), [])

    def test_pv_roles_need_an_exclusive_allocation_and_absolute_binary(self):
        rig = Rig()
        good = dict(rig.cfg["roles"]["pv-writer"])
        for change in ({"launcher": []}, {"launcher": good["launcher"][:1] + good["launcher"][2:]},
                       {"launcher": good["launcher"][:5] + good["launcher"][6:]}, {"binary": "reference_role.py"},
                       {"args": [1]}):
            rig.cfg["roles"]["pv-writer"] = {**good, **change}
            rig.write_config()
            rc, _, err = rig.run("pv-writer")
            self.assertEqual(rc, cw.ERROR, (change, err))
        rig.cfg["roles"]["pv-writer"] = {k: v for k, v in good.items() if k != "launcher"}
        rig.write_config()
        self.assertEqual(rig.run("pv-writer")[0], cw.ERROR)
        self.assertEqual(rig.events(), [])

    def test_pv_roles_need_the_seal_and_freeze_paths(self):
        rig = Rig()
        del rig.cfg["freeze_root"]
        rig.write_config()
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.ERROR, err)

    def test_the_command_is_built_from_the_structured_config(self):
        rig = Rig()
        cmd = cw.launch_command("pv-writer", rig.cfg["roles"]["pv-writer"])
        argv = subprocess.run(["python3", "-c", "import shlex,sys; print(shlex.split(sys.argv[1]))", cmd],
                              capture_output=True, text=True).stdout
        self.assertIn("'bash', '-c'", argv)
        self.assertIn(f"'{REF}', '{cw.sha256_file(REF)}', '--role', 'pv-writer'", argv)


# ------------------------------------------------------------------------------------------------------------

class RunTests(unittest.TestCase):
    def test_writer_end_to_end_and_the_spend_precedes_the_launch(self):
        rig = Rig()
        rc, out, err = rig.run("pv-writer")
        self.assertEqual(rc, 0, err)
        self.assertIn("pv-writer completed", out)
        self.assertEqual([(e["event"], e["role"]) for e in rig.events()],
                         [("spent", "pv-writer"), ("completed", "pv-writer")])
        self.assertEqual(rig.events()[0]["freeze"], rig.seal["freeze_digest"])
        at_launch = slurp(os.path.join(rig.root, "at-launch.txt")).splitlines()
        self.assertEqual(len(at_launch), 1)
        self.assertEqual(json.loads(at_launch[0])["event"], "spent")
        self.assertEqual(rig.remote_record(), slurp(os.path.join(rig.cfg["record_dir"], "RECORD.jsonl"), "rb"))
        self.assertEqual(rig.markers(), [("attempt", rig.seal["seal_digest"], "pv-writer")])

    def test_ssh_never_gets_a_pty(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        for entry in rig.ssh_log():
            self.assertEqual(entry["opts"][:3], ["-T", "-o", "RequestTTY=no"])

    def test_no_secret_in_any_argv_env_record_or_output(self):
        rig = Rig()
        rc, out, err = rig.run("pv-writer")
        self.assertEqual(rc, 0, err)
        rc2, out2, err2 = rig.run("pg-connect")
        self.assertEqual(rc2, 0, err2)
        blobs = [json.dumps(rig.ssh_log()), out, err, out2, err2, rig.remote_record().decode(), slurp(rig.config)]
        for dirpath, _, files in os.walk(rig.root):
            if "/.git" in dirpath or dirpath.endswith(".git") or "origin.git" in dirpath:
                continue
            for f in files:
                blobs.append(slurp(os.path.join(dirpath, f), "rb").decode("latin-1"))
        for s in rig.secrets():
            for b in blobs:
                self.assertNotIn(s, b)

    def test_no_secret_on_the_processes_own_stdout_or_stderr(self):
        rig = Rig()
        script = os.path.join(HERE, "covfix_wrapper.py")
        outs = []
        for role in ("pg-connect", "pv-writer", "pv-readout"):
            r = subprocess.run([sys.executable, script, *rig.argv(role)], capture_output=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            outs += [r.stdout, r.stderr]
        r = subprocess.run([sys.executable, script, "reveal", "--config", rig.config, "--config-sha256",
                            rig.config_sha, "--seal-digest", rig.seal["seal_digest"], "--commitment",
                            rig.commitment()], capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        pw, base, salt = rig.secrets()
        for o in outs:
            for s in (pw, base, salt):
                self.assertNotIn(s.encode(), o)
        self.assertNotIn(pw.encode(), r.stdout + r.stderr)
        self.assertEqual(r.stdout, f"seed_base={base}\nsalt={salt}\n".encode())

    def test_a_spent_role_never_reruns(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        n = len(rig.ssh_log())
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL)
        self.assertIn("already consumed", err)
        self.assertEqual(len(rig.ssh_log()), n, "a consumed role must not touch the cluster")

    def test_readout_after_writer_with_the_same_freeze(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        rc, out, err = rig.run("pv-readout")
        self.assertEqual(rc, 0, err)
        self.assertEqual([e["event"] for e in rig.events()], ["spent", "completed", "spent", "completed"])

    def test_readout_needs_a_completed_writer(self):
        rig = Rig()
        rc, _, err = rig.run("pv-readout")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("completed pv-writer", err)
        rig2 = Rig(role_flags={"pv-writer": ["--fail-after-decrypt"]})
        self.assertEqual(rig2.run("pv-writer")[0], cw.TERMINAL)
        self.assertEqual(rig2.run("pv-readout")[0], cw.REFUSED)
        self.assertEqual(rig.events(), [])

    def test_a_changed_freeze_in_a_new_binding_cannot_create_a_fresh_role(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        with open(rig.cfg["freeze_file"], "a") as f:
            f.write(f"{cw.sha256_file(rig.cfg['freeze_file'])}  extra.txt\n")
        rig.cfg["binding"]["freeze_digest"] = cw.sha256_file(rig.cfg["freeze_file"])
        rig.write_config()
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        rc, _, err = rig.run("pv-readout")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("bound to freeze", err)

    def test_crash_after_decrypt_is_terminal_with_no_retry(self):
        for role in ("pv-writer", "pv-readout"):
            rig = Rig(role_flags={role: ["--fail-after-decrypt"]})
            if role == "pv-readout":
                self.assertEqual(rig.run("pv-writer")[0], 0)
            rc, out, err = rig.run(role)
            self.assertEqual(rc, cw.TERMINAL, (role, err))
            self.assertEqual(rig.events()[-1]["event"], "terminal")
            self.assertEqual(rig.run(role)[0], cw.TERMINAL)

    def test_a_dropped_link_after_the_spend_is_terminal(self):
        rig = Rig()
        rig.set_ssh_mode("drop-link")
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual([e["event"] for e in rig.events()], ["spent", "terminal"])

    def test_an_undelivered_frame_is_terminal_even_at_rc_0(self):
        rig = Rig()
        with mock.patch.object(cw.Cluster, "launch", return_value=(0, False)):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("frame not delivered", rig.events()[-1]["detail"])

    def test_a_confirmed_in_role_break_stops_the_seal(self):
        rig = Rig()
        pw = rig.kc.read("passphrase")
        sealed = rig.seal["seal_root"]
        with mock.patch.object(cw.Cluster, "launch", return_value=(cw.BREAK_RC, True)):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual(rig.events()[-1]["event"], "break")
        self.assertIn(("break", rig.seal["seal_digest"], "seal"), rig.markers())
        self.assertEqual(rig.run("pv-readout")[0], cw.TERMINAL)
        del pw, sealed

    def test_the_compute_side_hash_check_stops_a_swapped_binary(self):
        rig = Rig()
        real = cw.Cluster.hash_files
        fake = os.path.join(rig.root, "other_role.py")
        shutil.copy(REF, fake)
        with open(fake, "a") as f:
            f.write("# changed after the login-node hash\n")
        os.chmod(fake, 0o755)
        rig.cfg["roles"]["pv-writer"]["binary"] = fake
        rig.write_config()

        def hash_files(self, root, rels):
            got, missing = real(self, root, rels)
            if rels == ["other_role.py"]:
                got = {"other_role.py": cw.sha256_file(REF)}
            return got, missing

        with mock.patch.object(cw.Cluster, "hash_files", hash_files):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual(rig.events()[-1]["detail"], f"rc {cw.EXEC_MISMATCH_RC}")

    def test_interrupt_during_launch_is_recorded_terminal(self):
        rig = Rig()
        with mock.patch.object(cw.Cluster, "launch", side_effect=KeyboardInterrupt):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL)
        self.assertEqual(rig.events()[-1]["event"], "terminal")
        self.assertIn("interrupted", rig.events()[-1]["detail"])

    def test_ssh_down_before_the_spend_refuses_and_spends_nothing(self):
        rig = Rig()
        rig.set_ssh_mode("down")
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertEqual(rig.events(), [])
        self.assertEqual(rig.markers(), [])
        rig.set_ssh_mode("")
        self.assertEqual(rig.run("pv-writer")[0], 0)

    def test_an_altered_ciphertext_is_a_break_that_stops_every_role(self):
        rig = Rig()
        with open(os.path.join(rig.seal["seal_root"], "synthetic-truth-u0.json.gpg"), "ab") as f:
            f.write(b"\0")
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("BREAK", err)
        self.assertEqual([e["event"] for e in rig.events()], ["break"])
        self.assertIn(b'"break"', rig.remote_record())
        self.assertFalse(rig.launched())
        self.assertEqual(rig.run("pv-readout")[0], cw.TERMINAL)

    def test_a_missing_ciphertext_is_a_break(self):
        rig = Rig()
        os.unlink(os.path.join(rig.seal["seal_root"], "PG-MANIFEST.json.gpg"))
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual(rig.events()[0]["event"], "break")

    def test_an_altered_frozen_file_is_a_break(self):
        rig = Rig()
        with open(os.path.join(rig.seal["freeze_root"], "synthetic-frozen.txt"), "a") as f:
            f.write("x")
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("P2-FREEZE", err)

    def test_a_seal_or_freeze_file_off_the_binding_is_a_break(self):
        for which in ("seal_file", "freeze_file"):
            rig = Rig()
            with open(rig.cfg[which], "a") as f:
                f.write("# edited\n")
            rc, _, err = rig.run("pv-writer")
            self.assertEqual(rc, cw.TERMINAL, err)
            self.assertIn("pinned digest", err)

    def test_a_missing_local_list_refuses(self):
        rig = Rig()
        os.unlink(rig.cfg["freeze_file"])
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertEqual(rig.events(), [])

    def test_incomplete_or_contradictory_hashing_refuses_without_a_break(self):
        for mode in ("no-end", "rc1", "extra", "junk"):
            rig = Rig()
            rig.set_ssh_mode(mode)
            rc, _, err = rig.run("pv-writer")
            self.assertEqual(rc, cw.REFUSED, (mode, err))
            self.assertEqual(rig.events(), [])

    def test_an_unreadable_ciphertext_refuses_without_a_break(self):
        rig = Rig()
        ct = os.path.join(rig.seal["seal_root"], "PG-MANIFEST.json.gpg")
        os.chmod(ct, 0)
        try:
            rc, _, err = rig.run("pv-writer")
        finally:
            os.chmod(ct, 0o600)
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("unreadable", err)
        self.assertEqual(rig.events(), [])

    def test_hashing_types_every_path(self):
        d = tempfile.mkdtemp(dir=TMP)
        for name, body in (("a b", "x"), ("-", "dash")):
            with open(os.path.join(d, name), "w") as f:
                f.write(body)
        os.makedirs(os.path.join(d, "locked"))
        with open(os.path.join(d, "locked", "f"), "w") as f:
            f.write("y")
        os.chmod(os.path.join(d, "locked"), 0)
        try:
            c = cw.Cluster([ssh_stub("RUN")], "h")
            got, missing = c.hash_files(d, ["a b", "-", "gone"])
            with self.assertRaises(cw.Stop) as cm:
                c.hash_files(d, ["a b", "locked/f"])
        finally:
            os.chmod(os.path.join(d, "locked"), 0o700)
        self.assertEqual(got, {"a b": hashlib.sha256(b"x").hexdigest(), "-": hashlib.sha256(b"dash").hexdigest()})
        self.assertEqual(missing, {"gone"})
        self.assertEqual(cm.exception.code, cw.REFUSED)
        self.assertIn("unreadable", str(cm.exception))

    def test_a_missing_remote_root_refuses_without_a_break(self):
        rig = Rig()
        rig.cfg["seal_root"] = os.path.join(rig.root, "nowhere")
        rig.write_config()
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertEqual(rig.events(), [])

    def test_a_wrong_binary_refuses_and_spends_nothing(self):
        rig = Rig()
        rig.cfg["roles"]["pv-writer"]["binary_sha256"] = "0" * 64
        rig.write_config()
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertEqual(rig.events(), [])

    def test_a_push_failure_is_an_uncertain_spend_and_blocks_the_role(self):
        rig = Rig()
        git(rig.wt, "remote", "set-url", "--push", "origin", os.path.join(rig.root, "no-such.git"))
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("uncertain", err)
        self.assertFalse(rig.launched())
        kinds = sorted(k for k, _, r in rig.markers() if r == "pv-writer")
        self.assertEqual(kinds, ["attempt", "uncertain"])
        git(rig.wt, "remote", "set-url", "--push", "origin", rig.bare)
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("already consumed", err)
        self.assertEqual(rig.run("pv-readout")[0], cw.REFUSED)       # the writer never completed

    def test_a_remote_blob_mismatch_is_an_uncertain_spend(self):
        rig = Rig()
        with mock.patch.object(cw, "git_blob_sha", return_value="0" * 40):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertFalse(rig.launched())
        self.assertIn("uncertain", [k for k, _, _ in rig.markers()])

    def test_a_lock_failure_is_an_uncertain_spend(self):
        rig = Rig()
        with mock.patch.object(cw.Record, "lock", side_effect=OSError("held")):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual(rig.markers(), [("uncertain", rig.seal["seal_digest"], "pv-writer")])
        self.assertEqual(rig.run("pv-writer")[0], cw.TERMINAL)

    def test_an_interrupt_during_the_spend_leaves_the_role_blocked(self):
        rig = Rig()
        with mock.patch.object(cw.Mirror, "publish", side_effect=KeyboardInterrupt):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertFalse(rig.launched())
        self.assertEqual(rig.run("pv-writer")[0], cw.TERMINAL)

    def test_a_crash_between_marker_and_append_leaves_the_role_blocked(self):
        rig = Rig()
        with mock.patch.object(cw.Record, "append", side_effect=SystemExit("hard stop")):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual(rig.events(), [])
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("marker", err)

    def test_a_restored_older_record_is_detected(self):
        rig = Rig()
        recpath = os.path.join(rig.cfg["record_dir"], "RECORD.jsonl")
        self.assertEqual(rig.run("pv-writer")[0], 0)
        os.unlink(recpath)
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("not an extension of the pushed mirror", err)

    def test_a_record_restored_after_the_unlocked_check_is_caught_under_the_lock(self):
        rig = Rig()
        recpath = os.path.join(rig.cfg["record_dir"], "RECORD.jsonl")
        self.assertEqual(rig.run("pv-writer")[0], 0)
        real = cw.Record.lock
        saved = slurp(recpath, "rb")

        def lock(self):
            with open(recpath, "wb") as f:          # the restore lands after the preflight, before the lock
                f.write(b"")
            return real(self)

        try:
            with mock.patch.object(cw.Record, "lock", lock), \
                    mock.patch.object(cw.Context, "spend_checks", lambda *a: None):
                ctx = cw.Context(rig.cfg)
                with self.assertRaises(cw.Stop) as cm:
                    ctx.commit_event({"event": "spent", "key": rig.seal["seal_digest"], "role": "pv-writer"}, "m")
        finally:
            with open(recpath, "wb") as f:
                f.write(saved)
        self.assertIn("not an extension", str(cm.exception))

    def test_a_rewound_remote_branch_is_terminal(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        os.unlink(os.path.join(rig.cfg["record_dir"], "RECORD.jsonl"))
        first = git(rig.wt, "rev-list", "--max-parents=0", "HEAD").strip()
        git(rig.wt, "reset", "-q", "--hard", first)
        git(rig.wt, "push", "-q", "-f", "origin", "HEAD:refs/heads/covfix-consumption")
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("rewound", err)

    def test_a_deleted_remote_branch_is_terminal(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        subprocess.run(["git", "--git-dir", rig.bare, "update-ref", "-d", "refs/heads/covfix-consumption"], check=True)
        rc, _, err = rig.run("pv-readout")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("deleted", err)

    def test_published_refs_keep_history_when_branch_and_seen_ref_are_rewound(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        self.assertTrue(git(rig.wt, "for-each-ref", "refs/covfix/published/").strip())
        os.unlink(os.path.join(rig.cfg["record_dir"], "RECORD.jsonl"))
        first = git(rig.wt, "rev-list", "--max-parents=0", "HEAD").strip()
        git(rig.wt, "reset", "-q", "--hard", first)
        git(rig.wt, "push", "-q", "-f", "origin", "HEAD:refs/heads/covfix-consumption")
        git(rig.wt, "update-ref", "-d", "refs/covfix/seen/covfix-consumption")
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("lacks", err)

    def test_mirror_on_the_wrong_branch_or_dirty_refuses(self):
        rig = Rig()
        git(rig.wt, "checkout", "-q", "-b", "other")
        self.assertEqual(rig.run("pv-writer")[0], cw.REFUSED)
        git(rig.wt, "checkout", "-q", "covfix-consumption")
        os.makedirs(os.path.dirname(os.path.join(rig.wt, REL)), exist_ok=True)
        with open(os.path.join(rig.wt, REL), "w") as f:
            f.write("x\n")
        self.assertEqual(rig.run("pv-writer")[0], cw.REFUSED)
        self.assertEqual(rig.events(), [])

    def test_mirror_hooks_off_by_default_and_on_when_asked(self):
        rig = Rig()
        hooks = os.path.join(rig.root, "hooks")
        os.makedirs(hooks)
        with open(os.path.join(hooks, "pre-commit"), "w") as f:
            f.write("#!/bin/sh\nexit 1\n")
        os.chmod(os.path.join(hooks, "pre-commit"), 0o755)
        git(rig.wt, "config", "core.hooksPath", hooks)
        self.assertEqual(rig.run("pv-writer")[0], 0)
        rig2 = Rig()
        git(rig2.wt, "config", "core.hooksPath", hooks)
        rig2.cfg["mirror"]["run_hooks"] = True
        rig2.write_config()
        rc, _, err = rig2.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertFalse(rig2.launched())

    def test_pg_connect_frame_and_commitment(self):
        rig = Rig()
        rig.cfg["binding"]["commitment"] = "f" * 64
        rig.write_config()
        rc, _, err = rig.run("pg-connect")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("do not reproduce", err)
        self.assertEqual(rig.events(), [])
        rig.cfg["binding"]["commitment"] = rig.commitment()
        rig.write_config()
        rc, out, err = rig.run("pg-connect")
        self.assertEqual(rc, 0, err)
        self.assertEqual(rig.events()[0]["key"], rig.commitment())
        self.assertNotIn("freeze", rig.events()[0])
        self.assertEqual(rig.run("pg-connect")[0], cw.TERMINAL)

    def test_frames(self):
        rig = Rig()
        seen = []

        def launch(self, command, frame):
            seen.append(bytes(frame))
            return 0, True

        with mock.patch.object(cw.Cluster, "launch", launch):
            self.assertEqual(rig.run("pg-connect")[0], 0)
            self.assertEqual(rig.run("pv-writer")[0], 0)
        pw, base, _ = rig.secrets()
        self.assertEqual(seen, [f"{pw}\n{base}\n".encode(), f"{pw}\n".encode()])

    def test_launch_zeroes_its_frame(self):
        frame = bytearray(b"abc\n")
        c = cw.Cluster([ssh_stub("cat >/dev/null")], "h")
        self.assertEqual(c.launch("x", frame), (0, True))
        self.assertEqual(frame, bytearray(4))


class RevealTests(unittest.TestCase):
    def reveal(self, rig, *extra, commitment=None):
        return run_main("reveal", "--config", rig.config, "--config-sha256", rig.config_sha,
                        "--seal-digest", rig.seal["seal_digest"],
                        "--commitment", commitment or rig.cfg["binding"]["commitment"], *extra)

    def test_reveal_waits_for_the_readout_and_then_stops_the_seal(self):
        rig = Rig()
        rc, out, err = self.reveal(rig)
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertEqual(out, "")
        self.assertEqual(rig.run("pv-writer")[0], 0)
        self.assertEqual(self.reveal(rig)[0], cw.REFUSED)
        self.assertEqual(rig.run("pv-readout")[0], 0)
        rc, out, err = self.reveal(rig)
        self.assertEqual(rc, 0, err)
        _, base, salt = rig.secrets()
        self.assertEqual(out, f"seed_base={base}\nsalt={salt}\n")
        self.assertEqual(rig.events()[-1]["event"], "reveal")
        self.assertEqual(rig.events()[-1]["commitment"], rig.commitment())
        rc2, out2, _ = self.reveal(rig)
        self.assertEqual((rc2, out2), (0, out))
        self.assertEqual([e["event"] for e in rig.events()].count("reveal"), 2)

    def test_after_stop_records_a_stop_that_blocks_later_pv_roles(self):
        rig = Rig()
        self.assertEqual(self.reveal(rig, "--after-stop", "  ")[0], cw.REFUSED)
        self.assertEqual(self.reveal(rig, "--after-stop", "ST1 $(rm -rf)")[0], cw.REFUSED)
        rc, out, err = self.reveal(rig, "--after-stop", "ST1 construction finding (director ruling)")
        self.assertEqual(rc, 0, err)
        self.assertIn("after stop: ST1", rig.events()[-1]["detail"])
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("reveal", err)

    def test_the_commitment_and_seal_must_be_the_binding_and_reproduce(self):
        rig = Rig()
        rc, out, err = self.reveal(rig, "--after-stop", "stop", commitment="a" * 64)
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertEqual(out, "")
        rig.cfg["binding"]["commitment"] = "a" * 64
        rig.write_config()
        rc, out, err = self.reveal(rig, "--after-stop", "stop", commitment="a" * 64)
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual(out, "")
        self.assertEqual(rig.events(), [])


class StatusTests(unittest.TestCase):
    def test_status(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        rc, out, _ = run_main("status", "--config", rig.config, "--config-sha256", rig.config_sha)
        self.assertEqual(rc, 0)
        self.assertEqual(out.count('"event"'), 2)
        self.assertIn("markers: [('attempt'", out)


FAKE_SECURITY = r'''#!/bin/bash
# a stand-in for /usr/bin/security: the mode file beside it picks the misbehaviour
mode=$(cat "$(dirname "$0")/mode")
case "$1" in
  -i) cat >/dev/null; exit 0 ;;
  login-keychain) [ "$mode" = "nokeychain" ] && exit 1; echo '    "/tmp/fake keychain"'; exit 0 ;;
  find-generic-password)
    w=0; for a in "$@"; do [ "$a" = "-w" ] && w=1; done
    case "$mode" in
      rc1) exit 1 ;;
      nonascii) [ $w = 1 ] && printf '\xff\n'; exit 0 ;;
      other) [ $w = 1 ] && echo 00; exit 0 ;;
    esac ;;
esac
exit 0
'''


class FailureBranchTests(unittest.TestCase):
    """The refusal and failure branches the line trace found unexecuted by the tests above."""

    def fake_security(self, mode, keychain="/tmp/fake.keychain"):
        d = tempfile.mkdtemp(dir=TMP)
        path = os.path.join(d, "security")
        with open(path, "w") as f:
            f.write(FAKE_SECURITY)
        os.chmod(path, 0o755)
        with open(os.path.join(d, "mode"), "w") as f:
            f.write(mode)
        return cw.Keychain("covfix-test-fake-", security=path, keychain=keychain), path

    def test_keychain_odd_answers(self):
        with self.assertRaises(ValueError):
            cw.Keychain("covfix-test-").service("password")
        with self.assertRaises(cw.Stop) as cm:
            self.fake_security("rc1")[0].exists("salt")
        self.assertEqual(cm.exception.code, cw.ERROR)
        with self.assertRaises(cw.Stop) as cm:
            self.fake_security("nonascii")[0].read("salt")
        self.assertIn("not ASCII", str(cm.exception))
        with self.assertRaises(cw.Stop) as cm:
            self.fake_security("other")[0].add("salt", "ab" * 32)
        self.assertIn("does not read back", str(cm.exception))
        for mode in ("nokeychain", "other"):          # other: the fake prints a path with a space
            path = self.fake_security(mode)[1]
            with self.assertRaises(cw.Stop):
                cw.login_keychain(path)

    def test_config_shapes(self):
        with self.assertRaises(cw.Stop):
            cw.Cluster([], "h")
        with self.assertRaises(cw.Stop):
            cw.Mirror({"worktree": "x"})
        rig = Rig()
        del rig.cfg["roles"]["pv-readout"]
        rig.write_config()
        self.assertEqual(rig.run("pv-readout")[0], cw.ERROR)

    def test_launch_survives_a_binary_that_reads_nothing(self):
        frame = bytearray(b"x" * (1 << 20))
        self.assertEqual(cw.Cluster([ssh_stub("exit 0")], "h").launch("x", frame), (0, False))
        self.assertEqual(frame.count(0), len(frame))

    def test_launch_kills_its_child_on_an_interrupt(self):
        c = cw.Cluster([ssh_stub("sleep 5")], "h")
        real_wait = subprocess.Popen.wait
        calls = []

        def wait(self, *a, **k):
            calls.append(1)
            if len(calls) == 1:
                raise KeyboardInterrupt
            return real_wait(self, *a, **k)

        with mock.patch.object(subprocess.Popen, "wait", wait):
            with self.assertRaises(KeyboardInterrupt):
                c.launch("x", bytearray(b"y\n"))
        self.assertEqual(len(calls), 2)

    def test_a_short_write_raises(self):
        d = tempfile.mkdtemp(dir=TMP)
        os.rmdir(d)
        rec = cw.Record(d)
        rec.ensure_dir()
        rec.lock()
        try:
            with mock.patch.object(cw.os, "write", return_value=1):
                with self.assertRaises(OSError):
                    rec.append({"key": "1" * 64, "role": "pv-writer", "event": "spent"})
        finally:
            rec.unlock()

    def test_a_spend_that_lost_the_race_is_consumed_without_an_uncertain_marker(self):
        rig = Rig()
        ctx = cw.Context(rig.cfg)
        ctx.record.ensure_dir()
        ev = {"event": "spent", "key": "5" * 64, "role": "pv-writer"}
        ctx.commit_event(dict(ev), "m")
        with self.assertRaises(cw.Consumed):
            ctx.commit_event(dict(ev), "m")
        self.assertEqual(ctx.record.markers(), [("attempt", "5" * 64, "pv-writer")])

    def test_an_existing_attempt_marker_is_consumed(self):
        rig = Rig()
        ctx = cw.Context(rig.cfg)
        ctx.record.ensure_dir()
        ctx.record.mark("attempt", "7" * 64, "pv-writer")
        # as if the marker appeared after the spend checks ran: the O_EXCL create is the last word
        with mock.patch.object(cw.Context, "spend_checks", lambda self, *a: None):
            with self.assertRaises(cw.Consumed):
                ctx.commit_event({"event": "spent", "key": "7" * 64, "role": "pv-writer"}, "m")

    def test_a_malformed_seal_file_that_matches_the_binding_is_a_break(self):
        rig = Rig()
        with open(rig.cfg["seal_file"], "w") as f:
            f.write("not a checksum line\n")
        rig.cfg["binding"]["seal_digest"] = cw.sha256_file(rig.cfg["seal_file"])
        rig.write_config()
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("BREAK", err)

    def test_a_break_that_cannot_be_appended_still_stops_every_role(self):
        rig = Rig()
        with open(os.path.join(rig.seal["seal_root"], "PG-MANIFEST.json.gpg"), "ab") as f:
            f.write(b"\0")
        real = cw.Record.append

        def append(self, event):
            if event["event"] == "break":
                raise OSError("disk full")
            return real(self, event)

        with mock.patch.object(cw.Record, "append", append):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertNotIn("break", [e["event"] for e in rig.events()])
        rc, _, err = rig.run("pv-readout")             # another role: only the seal-wide marker can stop it here
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("break", err)

    def test_a_break_whose_record_fails_still_stops_the_seal(self):
        rig = Rig()
        git(rig.wt, "remote", "set-url", "--push", "origin", os.path.join(rig.root, "no-such.git"))
        ct = os.path.join(rig.seal["seal_root"], "PG-MANIFEST.json.gpg")
        good = slurp(ct, "rb")
        with open(ct, "ab") as f:
            f.write(b"\0")
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("recording the break failed", err)
        with open(ct, "wb") as f:                     # the ciphertext is put back
            f.write(good)
        git(rig.wt, "remote", "set-url", "--push", "origin", rig.bare)
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)

    def test_an_outcome_that_cannot_be_mirrored_is_terminal(self):
        rig = Rig()
        real = cw.Mirror.publish
        n = []

        def publish(self, data, message, seq):
            n.append(1)
            if len(n) == 2:
                raise cw.Stop(cw.REFUSED, "push refused")
            return real(self, data, message, seq)

        with mock.patch.object(cw.Mirror, "publish", publish):
            rc, out, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL)
        self.assertIn("was not mirrored", err)
        self.assertEqual(rig.run("pv-writer")[0], cw.TERMINAL)

    def test_an_absorb_failure_on_an_outcome_marks_the_role(self):
        rig = Rig()
        ctx = cw.Context(rig.cfg)
        ctx.record.ensure_dir()
        with mock.patch.object(cw.Record, "absorb_markers", side_effect=OSError("disk")):
            with self.assertRaises(OSError):
                ctx.commit_event({"event": "completed", "key": "8" * 64, "role": "pv-writer"}, "m")
        self.assertIn(("uncertain", "8" * 64, "pv-writer"), ctx.record.markers())

    def test_the_first_spend_creates_the_mirror_branch(self):
        rig = Rig()
        subprocess.run(["git", "--git-dir", rig.bare, "update-ref", "-d", "refs/heads/covfix-consumption"], check=True)
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, 0, err)
        self.assertIn(b'"completed"', rig.remote_record())

    def test_a_failed_fetch_refuses(self):
        rig = Rig()
        real = cw.Mirror.git

        def mgit(self, *args, check=True, input=None):
            if "fetch" in args:
                return subprocess.CompletedProcess(args, 1, b"", b"fatal: unable to access")
            return real(self, *args, check=check, input=input)

        with mock.patch.object(cw.Mirror, "git", mgit):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertEqual(rig.events(), [])

    def test_synthetic_seal_round_trip_failure_and_cli(self):
        kc = cw.Keychain(new_prefix())
        cw.generate(kc)
        real = cw.gpg_run

        def gpg(argv, pw, payload, g="gpg"):
            out = real(argv, pw, payload, g)
            return out + b"x" if "--decrypt" in argv else out

        with mock.patch.object(cw, "gpg_run", gpg):
            with self.assertRaises(cw.Stop) as cm:
                cw.synthetic_seal(kc, os.path.join(tempfile.mkdtemp(dir=TMP), "s"))
        self.assertIn("round trip", str(cm.exception))
        out = os.path.join(tempfile.mkdtemp(dir=TMP), "s")
        rc, text, _ = run_main("synthetic-seal", "--keychain-prefix", kc.prefix, "--out", out)
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(text)["seal_digest"], cw.sha256_file(os.path.join(out, "PG-SEAL.sha256")))

    def test_the_script_entry_point_refuses_the_real_prefix(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "covfix_wrapper.py"), "generate"], capture_output=True,
                           text=True)
        self.assertEqual(r.returncode, cw.ERROR)
        self.assertIn("forbidden", r.stderr)
        self.assertEqual(r.stdout, "")


class ReferenceRoleTests(unittest.TestCase):
    def test_malformed_frames_refuse(self):
        rig = Rig()
        pw = rig.kc.read("passphrase")
        for role, frame in (("pv-writer", pw + "\nextra\n"), ("pv-writer", pw), ("pg-connect", pw + "\n"),
                            ("pg-connect", pw + "\n123\n")):
            r = subprocess.run([sys.executable, REF, "--role", role, "--sealed", rig.seal["seal_root"]],
                               input=frame.encode(), capture_output=True)
            self.assertNotEqual(r.returncode, 0, (role, frame[-8:]))

    def test_a_product_off_its_manifest_hash_is_a_typed_break(self):
        rig = Rig()
        pw = rig.kc.read("passphrase")
        sealed = rig.seal["seal_root"]
        bad = {"products": {"synthetic-truth-u0.json": "0" * 64}}
        with open(os.path.join(sealed, "PG-MANIFEST.json.gpg"), "wb") as f:
            f.write(cw.gpg_run(cw.GPG_ENCRYPT, pw, json.dumps(bad).encode()))
        r = subprocess.run([sys.executable, REF, "--role", "pv-writer", "--sealed", sealed],
                           input=(pw + "\n").encode(), capture_output=True)
        self.assertEqual(r.returncode, cw.BREAK_RC)
        self.assertIn(b"does not reproduce", r.stderr)

    def test_wrong_passphrase_fails_in_gpg(self):
        rig = Rig()
        r = subprocess.run([sys.executable, REF, "--role", "pv-readout", "--sealed", rig.seal["seal_root"]],
                           input=(secrets.token_hex(32) + "\n").encode(), capture_output=True)
        self.assertEqual(r.returncode, cw.TERMINAL)


if __name__ == "__main__":
    unittest.main()
