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
import pwd
import secrets
import shlex
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
for _k in [k for k in os.environ if k.startswith("GIT_")]:
    del os.environ[_k]                     # no inherited repository, template, config or hook selection
PREFIXES = []
TMP = tempfile.mkdtemp(prefix="covfix-wrapper-test-")
os.makedirs(os.path.join(TMP, "git-template"))
os.environ.update({"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1", "GIT_ALLOW_PROTOCOL": "file",
                   "GIT_TERMINAL_PROMPT": "0", "GIT_TEMPLATE_DIR": os.path.join(TMP, "git-template"),
                   "GIT_CEILING_DIRECTORIES": TMP})
REF = os.path.join(HERE, "reference_role.py")
KEYFILE = os.path.join(TMP, "id_test")
CERTFILE = os.path.join(TMP, "id_test-cert.pub")
for _p in (KEYFILE, CERTFILE):
    with open(_p, "w") as _f:
        _f.write("not a real key\n")
REMOTE_ENV = os.path.join(TMP, "remote-env.json")      # what a remote login session would provide the command
# Only the names the stub remote needs, never the caller's whole environment (which may hold tokens).
REMOTE_ENV_KEYS = ("PATH", "HOME", "TMPDIR", "LANG", cw.FORBID_REAL_ENV, "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM",
                   "GIT_ALLOW_PROTOCOL", "GIT_TERMINAL_PROMPT", "GIT_TEMPLATE_DIR", "GIT_CEILING_DIRECTORIES")
with open(REMOTE_ENV, "w") as _f:
    json.dump({k: os.environ[k] for k in REMOTE_ENV_KEYS if k in os.environ}, _f)
KNOWN_HOSTS = os.path.join(pwd.getpwuid(os.getuid()).pw_dir, ".ssh", "known_hosts")
HOST_FILES = ("-o", f"UserKnownHostsFile={KNOWN_HOSTS}", "-o", "GlobalKnownHostsFile=/dev/null")


def ssh_cfg(program):
    return {"program": program, "user": "tester", "identity_file": KEYFILE}
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
    "RUN") under bash, with stdin forwarded, in the PATH a remote session would have."""
    d = tempfile.mkdtemp(dir=TMP)
    path = os.path.join(d, "ssh")
    with open(path, "w") as f:
        f.write("#!/bin/bash\n" f"export PATH={shlex.quote(os.environ['PATH'])}\n"
                "while [ \"${1#-}\" != \"$1\" ]; do case \"$1\" in -o|-F|-i|-p|-l) shift;; esac; shift; done\n"
                "host=$1; cmd=$2\n" + ('exec bash -c "$cmd"\n' if body == "RUN" else body + "\n"))
    os.chmod(path, 0o755)
    return path


def stub_cluster(body: str):
    return cw.Cluster(ssh_cfg(ssh_stub(body)), "h")


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
    n = 2 if args[0] in ("-o", "-F", "-i", "-p", "-l") else 1
    opts += args[:n]
    args = args[n:]
host, command = args[0], args[1]
with open(os.path.join(here, "ssh-log.jsonl"), "a") as f:
    f.write(json.dumps({{"argv": sys.argv, "opts": opts, "env": dict(os.environ)}}) + "\n")
with open({remote_env!r}) as f:
    os.environ.clear()
    os.environ.update(json.load(f))                 # the remote session's own environment, as a login would give
xp = os.path.join(here, "remote-extra-env.json")    # a test's additions to that environment (e.g. a profile's SRUN_*)
if os.path.exists(xp):
    with open(xp) as f:
        os.environ.update(json.load(f))
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
# stub {name}: log its argv, require --exclusive -N 1 -n 1, refuse any Slurm I/O variable that is SET (even empty),
# drop the options up to the next command ({until}), and exec it with stdin
printf '%s\n' "{name} $*" >> {log}
{{ printf '== %s\n' "{name}"; env; }} >> {log}.env    # what this step and, after srun, the bound binary inherit
[ "$1 $2 $3 $4 $5" = "--exclusive -N 1 -n 1" ] || {{ echo "stub {name}: unexpected flags $*" >&2; exit 64; }}
for v in {io_vars}; do
    [ -z "${{!v+x}}" ] || {{ echo "stub {name}: inherited Slurm I/O setting $v" >&2; exit 65; }}
done
shift 5
while [ $# -gt 0 ] && [ "$(basename -- "$1")" != "{until}" ]; do shift; done
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
            f.write(STUB_SSH.format(python=sys.executable, here=self.root, bare=self.bare, rel=REL,
                                    remote_env=REMOTE_ENV))
        for name, until in (("salloc", "srun"), ("srun", "bash")):
            with open(os.path.join(self.bin, name), "w") as f:
                f.write(STUB_ALLOC.format(name=name, until=until, log=shlex.quote(os.path.join(self.root, "alloc.log")),
                                          io_vars=" ".join(cw.SLURM_IO_ENV)))
        for name in ("ssh", "salloc", "srun"):
            os.chmod(os.path.join(self.bin, name), 0o755)
        self.seal = cw.synthetic_seal(self.kc, os.path.join(self.root, "synthetic"))
        flags = role_flags or {}
        roles = {}
        for role in cw.ROLES:
            roles[role] = {"binary": REF, "binary_sha256": cw.sha256_file(REF),
                           "args": ["--role", role, *flags.get(role, [])]}
            roles[role]["slurm"] = {"salloc": f"{self.bin}/salloc", "srun": f"{self.bin}/srun",   # every role, pg-connect too
                                    "account": "m0000", "time": "0:30:00"}
        self.cfg = {
            "record_dir": os.path.join(self.root, "record"),
            "keychain_prefix": self.prefix,
            "ssh": ssh_cfg(os.path.join(self.bin, "ssh")), "host": "stub-login",
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
        return argv + list(kw.get("extra", []))

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

    def restore_empty(self):
        """As if the record directory were restored from a copy taken before the first spend."""
        d = self.cfg["record_dir"]
        for n in os.listdir(d):
            if n == "RECORD.jsonl" or n.startswith("MARK-"):
                os.unlink(os.path.join(d, n))

    def launched(self):
        return os.path.exists(os.path.join(self.root, "at-launch.txt"))

    def secrets(self):
        return [self.kc.read(i) for i in cw.ITEMS]

    def reseal(self, manifest_bytes):
        """Replace the sealed manifest with an encrypted manifest_bytes and re-pin the seal (list and binding)."""
        pw = self.kc.read("passphrase")
        root = self.seal["seal_root"]
        with open(os.path.join(root, "PG-MANIFEST.json.gpg"), "wb") as f:
            f.write(cw.gpg_run(cw.GPG_ENCRYPT, pw, manifest_bytes))
        with open(self.cfg["seal_file"], "w") as f:
            f.write("".join(f"{cw.sha256_file(os.path.join(root, n))}  {n}\n" for n in sorted(os.listdir(root))))
        self.cfg["binding"]["seal_digest"] = cw.sha256_file(self.cfg["seal_file"])
        self.write_config()


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

    def test_the_launch_is_one_exclusive_task_from_validated_fields(self):
        rig = Rig()
        good = json.loads(json.dumps(rig.cfg["roles"]["pv-writer"]))
        bad = [{"slurm": None}, {"slurm": {**good["slurm"], "ntasks": "2"}}, {"slurm": {**good["slurm"], "salloc": "sbatch"}},
               {"slurm": {**good["slurm"], "time": "1:00 --pty"}}, {"binary": "reference_role.py"},
               {"binary_sha256": "x"}, {"args": [1]}, {"args": "--role pv-writer"},
               {"args": ["--covfix-seal-root", "/elsewhere"]}]
        for change in bad:
            cfg = {**good, **change}
            if change.get("slurm") is None and "slurm" in change:
                del cfg["slurm"]
            rig.cfg["roles"]["pv-writer"] = cfg
            rig.write_config()
            rc, _, err = rig.run("pv-writer")
            self.assertEqual(rc, cw.ERROR, (change, err))
        self.assertEqual(rig.events(), [])
        self.assertEqual(rig.ssh_log(), [])

    def test_ssh_argv_is_built_from_the_closed_schema(self):
        home = tempfile.mkdtemp(dir=TMP)
        kh = os.path.join(home, ".ssh", "known_hosts")
        os.makedirs(os.path.dirname(kh))
        with mock.patch.object(cw, "home_dir", return_value=home):
            with self.assertRaises(cw.Stop, msg="a missing known_hosts"):
                cw.ssh_setup(ssh_cfg("/usr/bin/ssh"), "perlmutter.nersc.gov", True)
            os.symlink(KEYFILE, kh)
            with self.assertRaises(cw.Stop, msg="a symlinked known_hosts"):
                cw.ssh_setup(ssh_cfg("/usr/bin/ssh"), "perlmutter.nersc.gov", True)
            os.unlink(kh)
            shutil.copy(KEYFILE, kh)
            argv, env = cw.ssh_setup({**ssh_cfg("/usr/bin/ssh"), "certificate_file": CERTFILE},
                                     "perlmutter.nersc.gov", True)
        self.assertEqual(argv, ["/usr/bin/ssh", *cw.SSH_FORCED, "-o", f"UserKnownHostsFile={kh}",
                                "-o", "GlobalKnownHostsFile=/dev/null", "-l", "tester", "-i", KEYFILE,
                                "-o", f"CertificateFile={CERTFILE}"])
        self.assertEqual(argv[1:3], ["-F", "none"])
        self.assertEqual(env, {"HOME": home, "PATH": "/usr/bin:/bin", "LANG": "C"})
        self.assertEqual(cw.ssh_setup(ssh_cfg("/usr/bin/ssh"), "h", False)[1]["HOME"],
                         pwd.getpwuid(os.getuid()).pw_dir)
        good = ssh_cfg("/usr/bin/ssh")
        bad = [{**good, "options": ["-t"]}, {**good, "port": 22}, {k: v for k, v in good.items() if k != "user"},
               {**good, "user": "u; rm"}, {**good, "identity_file": "~/.ssh/nersc"},
               {**good, "identity_file": "relative/key"}, {**good, "identity_file": "/tmp/$HOME/k"},
               {**good, "identity_file": TMP}, {**good, "identity_file": "/etc/hosts"},
               {**good, "certificate_file": "/etc/hosts"}, {**good, "agent": "yes"},
               {**good, "program": "ssh"}, ["/usr/bin/ssh"]]
        for cfg in bad:
            with self.assertRaises(cw.Stop, msg=cfg):
                cw.ssh_setup(cfg, "perlmutter.nersc.gov", False)
        # existing files of this user, reached by a path that is not literal: refused before any lstat
        odd = os.path.join(TMP, "id_$HOME")
        shutil.copy(KEYFILE, odd)
        dotdot = os.path.join(TMP, "..", os.path.basename(TMP), "id_test")
        rel = os.path.relpath(KEYFILE)
        for path in (odd, dotdot, rel):
            self.assertTrue(os.path.isfile(path), path)
            with self.assertRaises(cw.Stop, msg=path) as c:
                cw.ssh_setup({**good, "identity_file": path}, "perlmutter.nersc.gov", False)
            self.assertIn("absolute, literal path", c.exception.args[-1], path)
        for host in ("", "a b", "h;id", "-oProxyCommand=x", "h.", None):
            with self.assertRaises(cw.Stop, msg=host):
                cw.ssh_setup(good, host, False)
        with self.assertRaises(cw.Stop):
            cw.ssh_setup({**good, "program": KEYFILE}, "h", True)       # the real items: /usr/bin/ssh only

    def test_an_agent_is_passed_only_when_declared(self):
        with mock.patch.dict(os.environ, {"SSH_AUTH_SOCK": "/tmp/agent.sock"}):
            self.assertNotIn("SSH_AUTH_SOCK", cw.ssh_setup(ssh_cfg("/usr/bin/ssh"), "h", False)[1])
            env = cw.ssh_setup({**ssh_cfg("/usr/bin/ssh"), "agent": True}, "h", False)[1]
            self.assertEqual(env["SSH_AUTH_SOCK"], "/tmp/agent.sock")
        with mock.patch.dict(os.environ, {"SSH_AUTH_SOCK": "$HOME/sock"}):
            with self.assertRaises(cw.Stop):
                cw.ssh_setup({**ssh_cfg("/usr/bin/ssh"), "agent": True}, "h", False)

    def test_pv_roles_need_the_seal_and_freeze_paths(self):
        rig = Rig()
        del rig.cfg["freeze_root"]
        rig.write_config()
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.ERROR, err)

    def test_the_command_is_built_from_the_structured_config(self):
        rig = Rig()
        import shlex
        argv = shlex.split(cw.launch_command("pv-writer", rig.cfg["roles"]["pv-writer"], ["--covfix-attempt", "a1"]))
        s, r = argv.index(f"{rig.bin}/salloc"), argv.index(f"{rig.bin}/srun")
        self.assertEqual(argv[s + 1:s + 6], ["--exclusive", "-N", "1", "-n", "1"])
        self.assertEqual(argv[r + 1:r + 6], ["--exclusive", "-N", "1", "-n", "1"])
        self.assertEqual(argv[s + 6:r], ["-J", "covfix_pv_writer", "-A", "m0000", "-t", "0:30:00"])
        self.assertEqual(argv[r + 6:r + 8], ["bash", "-c"])
        self.assertEqual(argv[0], "env")
        self.assertEqual(argv[1:s], [x for v in cw.SLURM_IO_ENV for x in ("-u", v)])
        self.assertEqual(argv[-6:], [REF, cw.sha256_file(REF), "--role", "pv-writer", "--covfix-attempt", "a1"])
        pg = shlex.split(cw.launch_command("pg-connect", rig.cfg["roles"]["pg-connect"], []))
        self.assertEqual(pg[:pg.index("bash")], [x if x != "covfix_pv_writer" else "covfix_pg_connect"
                                                 for x in argv[:argv.index("bash")]])   # the PV roles' allocation


# ------------------------------------------------------------------------------------------------------------

class PgConnectAllocationTests(unittest.TestCase):
    """cov2d, 2026-11-25: pg-connect had no allocation, so it would have run on the login host. Every role now launches
    through one exclusive node, and cov2d's four constraints hold for each: (1) a fixed argv, (2) no -J or --comment,
    and nothing derived from any input before the bound binary, (3) the frame only on srun's forwarded stdin, and (4)
    the Slurm I/O variables unset in the child's environment. The secrets are the rig's covfix-test-* stand-ins."""

    def alloc_log(self, rig):
        p = os.path.join(rig.root, "alloc.log")
        return open(p).read().splitlines() if os.path.exists(p) else []

    def test_1_every_role_gets_exactly_the_fixed_argv(self):
        rig = Rig()
        for role in cw.ROLES:
            extra = ["--covfix-attempt", "a1"]
            argv = shlex.split(cw.launch_command(role, rig.cfg["roles"][role], extra))
            self.assertEqual(argv, ["env", *[x for v in cw.SLURM_IO_ENV for x in ("-u", v)],
                                    f"{rig.bin}/salloc", "--exclusive", "-N", "1", "-n", "1", "-J", cw.JOB_NAMES[role],
                                    "-A", "m0000", "-t", "0:30:00",
                                    f"{rig.bin}/srun", "--exclusive", "-N", "1", "-n", "1",
                                    "bash", "-c", cw.EXEC_CHECK, "covfix-exec", REF, cw.sha256_file(REF),
                                    "--role", role, *extra], role)

    def test_1_pg_connect_without_a_valid_slurm_block_never_launches(self):
        rig = Rig()
        good = json.loads(json.dumps(rig.cfg["roles"]["pg-connect"]))
        for change in ({"slurm": None}, {"slurm": "salloc -N 1"}, {"slurm": {**good["slurm"], "salloc": "sbatch"}},
                       {"slurm": {**good["slurm"], "srun": "/usr/bin/ssh"}}, {"slurm": {**good["slurm"], "nodes": "2"}},
                       {"slurm": {**good["slurm"], "time": "1:00 --pty"}}):
            cfg = {**good, **change}
            if change.get("slurm", 0) is None:
                del cfg["slurm"]
            rig.cfg["roles"]["pg-connect"] = cfg
            rig.write_config()
            rc, _, err = rig.run("pg-connect")
            self.assertEqual(rc, cw.ERROR, (change, err))
        self.assertEqual(rig.events(), [])
        self.assertEqual(rig.ssh_log(), [])
        self.assertEqual(self.alloc_log(rig), [])

    def test_2_no_job_name_or_comment_and_no_input_before_the_binary(self):
        for key in ("job_name", "J", "-J", "comment", "name", "job-name"):
            rig = Rig()
            rig.cfg["roles"]["pg-connect"]["slurm"][key] = "covfix"
            rig.write_config()
            self.assertEqual(rig.run("pg-connect")[0], cw.ERROR, key)
            self.assertEqual(rig.ssh_log(), [], key)
        self.assertNotIn("-J", cw.SLURM_KEYS.values())
        self.assertFalse({"--job-name", "--comment"} & set(cw.SLURM_KEYS.values()))
        rig = Rig()
        self.assertEqual(rig.run("pg-connect")[0], 0)
        launches = [e for e in rig.ssh_log() if "covfix-hash-end" not in e["argv"][-1]]
        self.assertEqual(len(launches), 1)
        cmd = shlex.split(launches[0]["argv"][-1])
        head = cmd[:cmd.index("bash")]                       # everything Slurm sees, before the bound binary
        fixed = {"env", "-u", *cw.SLURM_IO_ENV, f"{rig.bin}/salloc", f"{rig.bin}/srun", "--exclusive", "-N", "-n", "1",
                 "-J", "covfix_pg_connect", "-A", "m0000", "-t", "0:30:00"}
        self.assertEqual(set(head) - fixed, set(), head)
        self.assertEqual([head[i + 1] for i, t in enumerate(head) if t == "-J"], ["covfix_pg_connect"])  # once, the constant
        self.assertFalse({"--job-name", "--comment"} & set(head))
        inputs = [rig.config_sha, rig.cfg["binding"]["commitment"], *rig.secrets()]
        for x in inputs:
            self.assertFalse(any(x in t for t in head), x[:8])
        log = self.alloc_log(rig)                            # what salloc and srun were actually given
        self.assertEqual([x.split() for x in log][0][:8], ["salloc", "--exclusive", "-N", "1", "-n", "1", "-J",
                                                          "covfix_pg_connect"])
        self.assertNotIn("-J", log[1].split())                # srun's step keeps the job's name
        for line in log:
            self.assertNotIn("--comment", line)
            self.assertNotIn("--job-name", line)
            for x in inputs:
                self.assertNotIn(x, line)

    def test_2_the_job_name_is_the_role_constant(self):
        """Director, 2026-11-25: -J covfix_<role> from a code constant, for every role, whatever the config and inputs."""
        self.assertEqual(cw.JOB_NAMES, {"pg-connect": "covfix_pg_connect", "pv-writer": "covfix_pv_writer",
                                        "pv-readout": "covfix_pv_readout"})
        rig = Rig()
        for role in cw.ROLES:
            for extra in ([], ["--covfix-attempt", "a1"], ["--covfix-attempt", "zz9"]):
                rcfg = json.loads(json.dumps(rig.cfg["roles"][role]))
                rcfg["args"] = [*rcfg["args"], "--name", "other"]
                rcfg["binary"] = "/elsewhere/other_binary"
                argv = shlex.split(cw.launch_command(role, rcfg, extra))
                s = argv.index(f"{rig.bin}/salloc")
                self.assertEqual(argv[s + 6:s + 8], ["-J", cw.JOB_NAMES[role]], (role, extra))
                self.assertEqual(argv.count("-J"), 1)

    def test_3_the_frame_reaches_the_binary_only_through_srun_stdin(self):
        rig = Rig()
        pw, base, salt = rig.secrets()
        rc, out, err = rig.run("pg-connect")
        self.assertEqual(rc, 0, err)                         # the reference role checked the frame it read on stdin
        log = self.alloc_log(rig)
        self.assertEqual([x.split()[0] for x in log], ["salloc", "srun"], log)   # stdin passed salloc, then srun
        for x in (pw, base, salt):
            for e in rig.ssh_log():
                self.assertFalse(any(x in a for a in e["argv"]), "a secret in ssh's argv")
                self.assertFalse(any(x in v for v in e["env"].values()), "a secret in ssh's environment")
            for line in log:
                self.assertNotIn(x, line, "a secret in salloc's or srun's argv")
        with open(os.path.join(rig.root, "alloc.log.env")) as f:   # cov2d's review: salloc's, srun's and the child's env
            envdump = f.read()
        self.assertEqual([x for x in envdump.splitlines() if x.startswith("== ")], ["== salloc", "== srun"])
        self.assertIn("PATH=", envdump)                      # a real dump, not an empty file
        for x in (pw, base, salt):
            self.assertNotIn(x, envdump, "a secret in salloc's, srun's or the child's environment")
        self.assertNotIn(pw, out + err)
        self.assertEqual(rig.events()[-1]["key"], rig.commitment())

    def test_4_slurm_io_variables_set_remotely_are_unset_for_the_child(self):
        rig = Rig()                                          # one campaign: pv-readout needs the pv-writer before it
        with open(os.path.join(rig.root, "remote-extra-env.json"), "w") as f:
            json.dump({v: "" if i % 2 else "/tmp/leak-%j" for i, v in enumerate(cw.SLURM_IO_ENV)}, f)
        for role in ("pg-connect", "pv-writer", "pv-readout"):
            before = len(self.alloc_log(rig))
            rc, _, err = rig.run(role)
            self.assertEqual(rc, 0, (role, err))
            self.assertEqual([x.split()[0] for x in self.alloc_log(rig)[before:]], ["salloc", "srun"], role)

    def test_4_control_without_env_unset_the_stub_refuses(self):
        """Not vacuous: the same remote variables, with the launcher's env -u removed, stop the run in the stub."""
        rig = Rig()
        with open(os.path.join(rig.root, "remote-extra-env.json"), "w") as f:
            json.dump({"SRUN_INPUT": "none"}, f)
        real = cw.launch_command

        def without_unset(role, rcfg, extra):
            argv = shlex.split(real(role, rcfg, extra))
            s = argv.index(rcfg["slurm"]["salloc"])
            return shlex.join(argv[s:])

        with mock.patch.object(cw, "launch_command", without_unset):
            rc, _, err = rig.run("pg-connect")
        self.assertNotEqual(rc, 0)
        self.assertIn("inherited Slurm I/O setting SRUN_INPUT", err + "".join(self.alloc_log(rig)) + str(rig.events()))


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

    def test_a_hostile_environment_never_reaches_ssh(self):
        rig = Rig()
        bogus = os.path.join(rig.root, "bogus-home")
        os.makedirs(os.path.join(bogus, ".ssh"))
        with open(os.path.join(bogus, ".ssh", "config"), "w") as f:
            f.write("Host *\n  ProxyCommand nc evil 22\n  PermitLocalCommand yes\n  LocalCommand cat\n")
        hostile = {"SSH_ASKPASS": "/tmp/reads-stdin", "SSH_ASKPASS_REQUIRE": "force", "DISPLAY": ":0",
                   "HOME": bogus, "SSH_AUTH_SOCK": "/tmp/agent.sock", "LD_PRELOAD": "/tmp/x.so",
                   "PATH": "/tmp/evil:" + os.environ["PATH"], "LANG": "xx_YY.UTF-8"}
        with mock.patch.dict(os.environ, hostile):
            self.assertEqual(rig.run("pv-writer")[0], 0)
        want_env = {"HOME": pwd.getpwuid(os.getuid()).pw_dir, "PATH": "/usr/bin:/bin", "LANG": "C"}
        want_argv = [os.path.join(rig.bin, "ssh"), *cw.SSH_FORCED, *HOST_FILES, "-l", "tester", "-i", KEYFILE,
                     "stub-login"]
        log = rig.ssh_log()
        self.assertGreaterEqual(len(log), 3)                 # the binary probe, the two lists, the launch
        for entry in log:
            # The stub is a Python script: at its own startup Python's PEP 538 locale coercion adds LC_CTYPE=C.UTF-8
            # (because LANG=C), and macOS adds __CF_USER_TEXT_ENCODING. Neither comes from the wrapper, whose exact
            # environment test_ssh_argv_is_built_from_the_closed_schema asserts on ssh_setup itself.
            env = {k: v for k, v in entry["env"].items()
                   if k != "__CF_USER_TEXT_ENCODING" and not (k == "LC_CTYPE" and v == "C.UTF-8")}
            self.assertEqual(env, want_env)
            self.assertEqual(entry["argv"][:-1], want_argv)

    def test_the_stub_remote_environment_holds_only_allowlisted_names(self):
        with open(REMOTE_ENV) as f:
            self.assertLessEqual(set(json.load(f)), set(REMOTE_ENV_KEYS))

    def test_ssh_never_gets_a_pty(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        for entry in rig.ssh_log():
            self.assertEqual(entry["opts"][:len(cw.SSH_FORCED)], list(cw.SSH_FORCED))

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
        with mock.patch.object(cw.Cluster, "launch", return_value=cw.LaunchResult(0, False, True, False, False)):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("frame not delivered", rig.events()[-1]["detail"])

    def test_a_confirmed_in_role_break_stops_the_seal(self):
        rig = Rig()
        rig.reseal(json.dumps({"products": {"synthetic-truth-u0.json": "0" * 64}}).encode())
        rc, out, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual(rig.events()[-1]["event"], "break")
        self.assertIn(("break", rig.cfg["binding"]["seal_digest"], "seal"), rig.markers())
        self.assertEqual(rig.run("pv-readout")[0], cw.TERMINAL)

    def test_a_malformed_authenticated_manifest_is_a_break(self):
        rig = Rig()
        rig.reseal(b"not json at all")
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual(rig.events()[-1]["event"], "break")

    def test_exit_66_without_the_attempts_break_line_is_only_terminal(self):
        rig = Rig()
        with mock.patch.object(cw.Cluster, "launch", return_value=cw.LaunchResult(66, False, False, False, False)):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual(rig.events()[-1]["event"], "terminal")
        self.assertNotIn("break", [k for k, _, _ in rig.markers()])

    def test_a_receipt_with_a_nonzero_exit_is_terminal(self):
        rig = Rig()
        with mock.patch.object(cw.Cluster, "launch", return_value=cw.LaunchResult(1, True, True, False, False)):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual(rig.events()[-1]["event"], "terminal")

    def test_no_receipt_is_terminal(self):
        rig = Rig(role_flags={"pv-writer": ["--no-receipt"]})
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("no receipt", rig.events()[-1]["detail"])

    def test_a_secret_echoed_by_the_task_is_redacted_and_terminal(self):
        rig = Rig(role_flags={"pv-writer": ["--echo-secret"]})
        r = subprocess.run([sys.executable, os.path.join(HERE, "covfix_wrapper.py"), *rig.argv("pv-writer")],
                           capture_output=True)
        self.assertEqual(r.returncode, cw.TERMINAL, r.stderr)
        pw = rig.kc.read("passphrase").encode()
        self.assertNotIn(pw, r.stdout + r.stderr)
        self.assertIn(b"[redacted]", r.stdout)
        self.assertIn("echoed a secret", rig.events()[-1]["detail"])

    def test_a_stop_recorded_during_the_spend_wins_over_the_launch(self):
        rig = Rig()
        real = cw.Context.commit_event

        def commit(self, event, message, absorb_exclude=None):
            real(self, event, message, absorb_exclude)
            if event["event"] == "spent":
                self.record.mark("break", event["key"], "seal")

        with mock.patch.object(cw.Context, "commit_event", commit):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertFalse(rig.launched())
        self.assertIn("stopped before launch", rig.events()[-1]["detail"])

    def test_an_outcome_over_a_restored_record_is_terminal(self):
        rig = Rig()
        recpath = os.path.join(rig.cfg["record_dir"], "RECORD.jsonl")
        real = cw.Cluster.launch

        def launch(self, *a):
            res = real(self, *a)
            os.unlink(recpath)                         # restored to empty while the task ran
            return res

        with mock.patch.object(cw.Cluster, "launch", launch):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("not mirrored", err)
        self.assertIn(b'"spent"', rig.remote_record())

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
            got, missing, unreadable = real(self, root, rels)
            if rels == ["other_role.py"]:
                got = {"other_role.py": cw.sha256_file(REF)}
            return got, missing, unreadable

        with mock.patch.object(cw.Cluster, "hash_files", hash_files):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertTrue(rig.events()[-1]["detail"].startswith(f"rc {cw.EXEC_MISMATCH_RC}"), rig.events()[-1])

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
            c = stub_cluster("RUN")
            got, missing, unreadable = c.hash_files(d, ["a b", "-", "gone", "locked/f"])
        finally:
            os.chmod(os.path.join(d, "locked"), 0o700)
        self.assertEqual(got, {"a b": hashlib.sha256(b"x").hexdigest(), "-": hashlib.sha256(b"dash").hexdigest()})
        self.assertEqual(missing, {"gone"})
        self.assertEqual(unreadable, {"locked/f"})

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
        real_publish, real_fetch = cw.Mirror.publish, cw.Mirror.fetch
        flag = []

        def publish(self, *a):
            flag.append(1)
            return real_publish(self, *a)

        def fetch(self, *a):
            data = real_fetch(self, *a)
            return data + b"tampered\n" if flag and data is not None else data

        with mock.patch.object(cw.Mirror, "publish", publish), mock.patch.object(cw.Mirror, "fetch", fetch):
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
        self.assertEqual(rig.run("pv-writer")[0], 0)
        rig.restore_empty()
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
        rig.restore_empty()
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
        self.assertIn("gone after it was published", err)
        for ref in git(rig.wt, "for-each-ref", "--format=%(refname)", "refs/covfix/seen/").split():
            git(rig.wt, "update-ref", "-d", ref)
        rc, _, err = rig.run("pv-readout")             # without the seen ref, the published refs still tell
        self.assertEqual(rc, cw.TERMINAL, err)

    def test_published_refs_keep_history_when_branch_and_seen_ref_are_rewound(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        self.assertTrue(git(rig.wt, "for-each-ref", "refs/covfix/published/").strip())
        rig.restore_empty()
        first = git(rig.wt, "rev-list", "--max-parents=0", "HEAD").strip()
        git(rig.wt, "reset", "-q", "--hard", first)
        git(rig.wt, "push", "-q", "-f", "origin", "HEAD:refs/heads/covfix-consumption")
        for ref in git(rig.wt, "for-each-ref", "--format=%(refname)", "refs/covfix/seen/").split():
            git(rig.wt, "update-ref", "-d", ref)
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("lacks", err)

    def test_a_line_reachable_only_through_a_merge_is_found(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        ident = ["-c", "user.name=t", "-c", "user.email=t@t"]
        git(rig.wt, "checkout", "-q", "-b", "side")
        with open(os.path.join(rig.wt, REL), "a") as f:
            f.write('{"hidden":"a spend that the merge drops"}\n')
        git(rig.wt, *ident, "commit", "-q", "-am", "side")
        git(rig.wt, "checkout", "-q", "covfix-consumption")
        git(rig.wt, *ident, "merge", "-q", "-s", "ours", "side", "-m", "merge keeping the older record")
        git(rig.wt, "branch", "-q", "-D", "side")
        git(rig.wt, "push", "-q", "origin", "HEAD:refs/heads/covfix-consumption")
        rc, _, err = rig.run("pv-readout")
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
        rc, _, err = rig2.run("pv-writer")              # the staged mirror path cannot mask the attempt
        self.assertEqual(rc, cw.TERMINAL, err)

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

        def launch(self, command, frame, attempt, redact):
            seen.append(bytes(frame))
            return cw.LaunchResult(0, True, True, False, False)

        with mock.patch.object(cw.Cluster, "launch", launch):
            self.assertEqual(rig.run("pg-connect")[0], 0)
            self.assertEqual(rig.run("pv-writer")[0], 0)
        pw, base, _ = rig.secrets()
        self.assertEqual(seen, [f"{pw}\n{base}\n".encode(), f"{pw}\n".encode()])

    def test_launch_zeroes_its_frame(self):
        frame = bytearray(b"abc\n")
        c = stub_cluster("cat >/dev/null; echo covfix-receipt a1")
        res = c.launch("x", frame, "a1", [])
        self.assertEqual((res.rc, res.delivered, res.receipt, res.echoed), (0, True, True, False))
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
        _, base, salt = rig.secrets()
        for bad in ("  ", "ST1 $(rm -rf)", "ST1 construction finding", salt, f"S{base}", "x" * 81):
            self.assertEqual(self.reveal(rig, "--after-stop", bad)[0], cw.REFUSED, bad)
        rc, out, err = self.reveal(rig, "--after-stop", "ST1-construction-finding")
        self.assertEqual(rc, 0, err)
        self.assertIn("after stop ST1-construction-finding", rig.events()[-1]["detail"])
        for role in ("pv-writer", "pg-connect"):
            rc, _, err = rig.run(role)
            self.assertEqual(rc, cw.TERMINAL, (role, err))

    def test_reveal_refuses_while_a_role_is_in_flight(self):
        rig = Rig()
        ctx = cw.Context(rig.cfg)
        ctx.record.ensure_dir()
        ctx.commit_event({"event": "spent", "key": rig.seal["seal_digest"], "role": "pv-writer"}, "m")
        rc, out, err = self.reveal(rig, "--after-stop", "ST2")
        self.assertEqual((rc, out), (cw.REFUSED, ""), err)
        self.assertIn("in flight", err)
        rc, out, err = self.reveal(rig, "--after-stop", "ST2", "--inflight-resolved", "DECISION-x")
        self.assertEqual(rc, 0, err)
        self.assertIn("resolved by DECISION-x", rig.events()[-1]["detail"])

    def test_the_commitment_and_seal_must_be_the_binding_and_reproduce(self):
        rig = Rig()
        rc, out, err = self.reveal(rig, "--after-stop", "stop", commitment="a" * 64)
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertEqual(out, "")
        rig.cfg["binding"]["commitment"] = "e" * 64
        rig.write_config()
        rc, out, err = self.reveal(rig, "--after-stop", "stop", commitment="e" * 64)
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
        for ssh, host in (([], "h"), (ssh_cfg("/usr/bin/ssh"), ""), ("ssh", "h")):
            with self.assertRaises(cw.Stop):
                cw.Cluster(ssh, host)
        for m in ({"worktree": "x"}, {"worktree": 1, "path": "p", "remote": "o", "branch": "b"}, []):
            with self.assertRaises(cw.Stop):
                cw.Mirror(m, "id")
        rig = Rig()
        del rig.cfg["roles"]["pv-readout"]
        rig.write_config()
        self.assertEqual(rig.run("pv-readout")[0], cw.ERROR)

    def test_launch_survives_a_binary_that_reads_nothing(self):
        frame = bytearray(b"x" * (1 << 20))
        res = stub_cluster("exit 0").launch("x", frame, "a", [])
        self.assertEqual((res.rc, res.delivered, res.receipt), (0, False, False))
        self.assertEqual(frame.count(0), len(frame))

    def test_launch_kills_its_child_on_an_interrupt(self):
        c = stub_cluster("sleep 5")
        real_wait = subprocess.Popen.wait
        calls = []

        def wait(self, *a, **k):
            calls.append(1)
            if len(calls) == 1:
                raise KeyboardInterrupt
            return real_wait(self, *a, **k)

        with mock.patch.object(subprocess.Popen, "wait", wait):
            with self.assertRaises(KeyboardInterrupt):
                c.launch("x", bytearray(b"y\n"), "a", [])
        self.assertEqual(len(calls), 2)

    def test_a_short_write_raises(self):
        d = tempfile.mkdtemp(dir=TMP)
        os.rmdir(d)
        rec = cw.Record(d)
        rec.ensure_dir()
        rec.lock()
        try:
            with mock.patch.object(cw.os, "write", return_value=0):
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
        ctx.check_mirror()                               # the ledger exists before any marker
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

        def append(self, event, expected=None):
            if event["event"] == "break":
                raise OSError("disk full")
            return real(self, event, expected)

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
        rc, _, err = rig.run("pv-readout")             # the writer's completion never reached the mirror
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("pushed record", err)

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


class Round3Tests(unittest.TestCase):
    """Behaviour added for the round-2 reads."""

    def test_altered_plus_unreadable_is_still_a_break(self):
        rig = Rig()
        with open(os.path.join(rig.seal["seal_root"], "synthetic-truth-u0.json.gpg"), "ab") as f:
            f.write(b"\0")
        ct = os.path.join(rig.seal["seal_root"], "PG-MANIFEST.json.gpg")
        os.chmod(ct, 0)
        try:
            rc, _, err = rig.run("pv-writer")
        finally:
            os.chmod(ct, 0o600)
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("altered", err)

    def test_nothing_found_under_the_root_refuses(self):
        rig = Rig()
        for n in os.listdir(rig.seal["seal_root"]):
            os.unlink(os.path.join(rig.seal["seal_root"], n))
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("unmounted", err)
        self.assertEqual(rig.events(), [])

    def test_an_off_binding_list_breaks_even_with_the_link_down(self):
        rig = Rig()
        rig.set_ssh_mode("down")
        with open(rig.cfg["seal_file"], "a") as f:
            f.write("# edited\n")
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn(("break", rig.seal["seal_digest"], "seal"), rig.markers())

    def test_an_attempt_marker_write_failure_spends_nothing(self):
        rig = Rig()
        real = cw.Record.mark

        def mark(self, kind, key, role):
            if kind == "attempt":
                raise OSError("read-only file system")
            return real(self, kind, key, role)

        with mock.patch.object(cw.Record, "mark", mark):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertEqual(rig.events(), [])
        self.assertFalse(rig.launched())

    def test_the_ledger_fixes_its_mirror(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        other = os.path.join(rig.root, "other.git")
        subprocess.run(["git", "init", "-q", "--bare", other], check=True)
        git(rig.wt, "remote", "set-url", "origin", other)
        rc, _, err = rig.run("pv-readout")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("not the ledger's", err)
        git(rig.wt, "remote", "set-url", "origin", rig.bare)
        os.unlink(os.path.join(rig.cfg["record_dir"], "LEDGER.json"))
        rc, _, err = rig.run("pv-readout")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("no LEDGER.json", err)

    def test_the_real_items_use_the_canonical_ledger_and_no_overrides(self):
        rig = Rig()
        with mock.patch.dict(os.environ, {cw.FORBID_REAL_ENV: ""}):
            with self.assertRaises(cw.Stop) as cm:
                cw.Context({**rig.cfg, "keychain_prefix": "covfix-"})
            self.assertIn("canonical ledger", str(cm.exception))
            with self.assertRaises(cw.Stop):
                cw.Context({**rig.cfg, "keychain_prefix": "covfix-", "record_dir": cw.REAL_RECORD_DIR,
                            "security": "/tmp/fake"})
            with self.assertRaises(cw.Stop):
                cw.Keychain("covfix-", security="/tmp/fake")

    def test_status_does_not_touch_the_keychain(self):
        rig = Rig()
        with mock.patch.object(cw, "login_keychain", side_effect=AssertionError("keychain touched")):
            rc, out, err = run_main("status", "--config", rig.config, "--config-sha256", rig.config_sha)
        self.assertEqual(rc, 0, err)

    def test_generate_reports_the_state_after_an_interrupt(self):
        kc = cw.Keychain(new_prefix())
        real = cw.Keychain.add

        def add(self, item, value):
            if item == "seed-base":
                raise KeyboardInterrupt
            return real(self, item, value)

        with mock.patch.object(cw.Keychain, "add", add):
            with self.assertRaises(cw.Stop) as cm:
                cw.generate(kc)
        self.assertIn("now holds 1 of 3 items (passphrase)", str(cm.exception))

    def test_core_dumps_are_off(self):
        code = ("import resource, sys; sys.path.insert(0, sys.argv[1]); import covfix_wrapper as cw; "
                "cw.main(['generate']); print(resource.getrlimit(resource.RLIMIT_CORE))")
        r = subprocess.run([sys.executable, "-c", code, HERE], capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "(0, 0)", r.stderr)

    def test_gpg_redacts_the_passphrase_from_its_errors(self):
        d = tempfile.mkdtemp(dir=TMP)
        shim = os.path.join(d, "gpg")
        with open(shim, "w") as f:
            f.write("#!/bin/bash\nread -r p <&3; echo \"leak $p\" >&2; exit 2\n")
        os.chmod(shim, 0o755)
        pw = secrets.token_hex(32)
        with self.assertRaises(cw.Stop) as cm:
            cw.gpg_run(cw.GPG_DECRYPT, pw, b"x", gpg=shim)
        self.assertNotIn(pw, str(cm.exception))
        self.assertIn("[redacted]", str(cm.exception))


class FreezeConflictTests(unittest.TestCase):
    """The director's ruling (2026-11-23): a freeze conflict is refused, spends nothing, and is recorded; two
    unresolved refusals on a seal block every role until a director ruling clears them."""

    def rebind(self, rig, extra_line):
        good = (rig.cfg["binding"]["freeze_digest"], slurp(rig.cfg["freeze_file"]))
        with open(rig.cfg["freeze_file"], "a") as f:
            f.write(extra_line)
        rig.cfg["binding"]["freeze_digest"] = cw.sha256_file(rig.cfg["freeze_file"])
        rig.write_config()
        return good

    def restore(self, rig, good):
        with open(rig.cfg["freeze_file"], "w") as f:
            f.write(good[1])
        rig.cfg["binding"]["freeze_digest"] = good[0]
        rig.write_config()

    def test_a_conflict_is_refused_recorded_and_pushed(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        bound = rig.seal["freeze_digest"]
        self.rebind(rig, f"{bound}  extra.txt\n")
        rc, _, err = rig.run("pv-readout")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("refused and recorded", err)
        e = rig.events()[-1]
        self.assertEqual((e["event"], e["role"], e["bound"], e["presented"]),
                         ("freeze-mismatch-refused", "pv-readout", bound, rig.cfg["binding"]["freeze_digest"]))
        self.assertIn(b"freeze-mismatch-refused", rig.remote_record())
        self.assertNotIn("pv-readout", [r for _, _, r in rig.markers()])

    def test_two_refusals_block_every_role_until_a_ruling(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        good = self.rebind(rig, f"{'a' * 64}  extra.txt\n")
        for _ in range(2):
            self.assertEqual(rig.run("pv-readout")[0], cw.REFUSED)
        self.restore(rig, good)
        rc, _, err = rig.run("pv-readout")            # the right freeze now waits for the ruling
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("unresolved freeze-mismatch", err)
        self.assertEqual(rig.run("pv-readout", extra=["--freeze-mismatch-resolved", "DECISION-x y"])[0], cw.REFUSED)
        rc, _, err = rig.run("pv-readout", extra=["--freeze-mismatch-resolved", "DECISION-20261123-freeze"])
        self.assertEqual(rc, 0, err)
        self.assertIn("ruling", [e["event"] for e in rig.events()])

    def test_a_ruling_with_nothing_to_resolve_refuses(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        rc, _, err = rig.run("pv-readout", extra=["--freeze-mismatch-resolved", "DECISION-x"])
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("nothing to resolve", err)
        rc, _, err = rig.run("pg-connect", extra=["--freeze-mismatch-resolved", "DECISION-x"])
        self.assertEqual(rc, cw.ERROR, err)

    def test_a_refusal_that_cannot_be_recorded_still_refuses_and_marks_nothing(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        self.rebind(rig, f"{'b' * 64}  extra.txt\n")
        git(rig.wt, "remote", "set-url", "--push", "origin", os.path.join(rig.root, "no-such.git"))
        rc, _, err = rig.run("pv-readout")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("recording the refusal failed", err)
        self.assertNotIn("pv-readout", [r for _, _, r in rig.markers()])

    def test_refusal_lines_neither_consume_nor_bind(self):
        k = "1" * 64
        ev = [{"seq": 0, "key": k, "role": "pv-readout", "event": "freeze-mismatch-refused",
               "presented": "a" * 64, "bound": "b" * 64}]
        self.assertIsNone(cw.blocked(ev, [], k, "pv-readout"))
        self.assertIsNone(cw.bound_freeze(ev, k))
        self.assertEqual(cw.unresolved_freeze_refusals(ev, k), 1)
        ev.append({"seq": 1, "key": k, "role": "ruling", "event": "ruling"})
        self.assertEqual(cw.unresolved_freeze_refusals(ev, k), 0)


class TraceGapTests(unittest.TestCase):
    """The branches the round-3 line trace found unexecuted."""

    def test_a_keychain_path_must_be_plain(self):
        with self.assertRaises(cw.Stop):
            cw.Keychain("covfix-test-", keychain="/tmp/a b")

    def test_generate_says_when_the_state_cannot_be_determined(self):
        kc = cw.Keychain(new_prefix())
        calls = []

        def exists(self, item):
            calls.append(item)
            if len(calls) > 3:
                raise cw.Stop(cw.ERROR, "security broke")
            return False

        with mock.patch.object(cw.Keychain, "exists", exists), \
                mock.patch.object(cw.Keychain, "add", side_effect=cw.Stop(cw.ERROR, "add broke")):
            with self.assertRaises(cw.Stop) as cm:
                cw.generate(kc)
        self.assertIn("could not be determined", str(cm.exception))

    def test_gpg_fd3_when_the_std_streams_were_closed(self):
        code = ("import os, sys; sys.path.insert(0, sys.argv[1]); import covfix_wrapper as cw\n"
                "assert not cw._fd_is_open(0)\n"
                "pw = '5' * 64\n"
                "ct = cw.gpg_run(cw.GPG_ENCRYPT, pw, b'z')\n"
                "assert cw.gpg_run(cw.GPG_DECRYPT, pw, ct) == b'z'\n"
                "assert not cw._fd_is_open(3)\n"
                "sys.stderr.write('closed ok\\n')\n")
        r = subprocess.run([sys.executable, "-c", code, HERE], capture_output=True, text=True,
                           preexec_fn=lambda: os.close(0))
        self.assertEqual((r.returncode, r.stderr.strip()), (0, "closed ok"), r.stderr)

    def test_config_shape_errors(self):
        with self.assertRaises(cw.Stop):
            cw.launch_command("pv-writer", ["not", "an", "object"], [])
        path = os.path.join(TMP, "shape.json")
        for body in ("[]", json.dumps({"record_dir": "x", "keychain_prefix": "p", "ssh": [], "host": "h",
                                       "mirror": {}, "roles": {}, "binding": "not an object"})):
            with open(path, "w") as f:
                f.write(body)
            with self.assertRaises(cw.Stop) as cm:
                cw.load_config(path, cw.sha256_file(path))
            self.assertEqual(cm.exception.code, cw.ERROR)

    def test_an_unreadable_ledger_file_is_terminal(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        with open(os.path.join(rig.cfg["record_dir"], "LEDGER.json"), "w") as f:
            f.write("{not json")
        rc, _, err = rig.run("pv-readout")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("unreadable", err)

    def _conflicting_rig(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        with open(rig.cfg["freeze_file"], "a") as f:
            f.write(f"{'c' * 64}  extra.txt\n")
        rig.cfg["binding"]["freeze_digest"] = cw.sha256_file(rig.cfg["freeze_file"])
        rig.write_config()
        return rig

    def test_recording_a_refusal_without_the_lock_or_with_a_write_error_refuses(self):
        rig = self._conflicting_rig()
        real_lock = cw.Record.lock
        n = []

        def lock(self):
            n.append(1)
            if len(n) == 1:                       # the refusal's own lock (the pre-check takes none)
                raise OSError("held")
            return real_lock(self)

        with mock.patch.object(cw.Record, "lock", lock):
            rc, _, err = rig.run("pv-readout")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("cannot take the record lock", err)
        with mock.patch.object(cw.Record, "append", side_effect=OSError("disk")):
            rc, _, err = rig.run("pv-readout")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("failed (OSError", err)
        self.assertNotIn("pv-readout", [r for _, _, r in rig.markers()])

    def test_a_lock_failure_whose_marker_also_fails_is_terminal(self):
        rig = Rig()
        with mock.patch.object(cw.Record, "lock", side_effect=OSError("held")), \
                mock.patch.object(cw.Record, "mark", side_effect=OSError("read-only")):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("nor mark", err)

    def test_a_break_whose_marker_cannot_be_written_still_records_the_line(self):
        rig = Rig()
        with open(os.path.join(rig.seal["seal_root"], "PG-MANIFEST.json.gpg"), "ab") as f:
            f.write(b"\0")
        real = cw.Record.mark

        def mark(self, kind, key, role):
            if kind == "break":
                raise OSError("read-only")
            return real(self, kind, key, role)

        with mock.patch.object(cw.Record, "mark", mark):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("break marker could not be written", err)
        self.assertEqual(rig.events()[-1]["event"], "break")

    def test_a_freeze_bound_by_a_concurrent_spend_is_caught_under_the_lock(self):
        rig = Rig()
        real = cw.Context.spend_checks
        n = []

        def checks(self, key, role, freeze):
            n.append(1)
            if len(n) == 2:                       # the locked re-check sees a freeze bound meanwhile
                raise cw.FreezeConflict(key, freeze, "d" * 64)
            return real(self, key, role, freeze)

        with mock.patch.object(cw.Context, "spend_checks", checks):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertEqual(rig.events()[-1]["event"], "freeze-mismatch-refused")
        self.assertFalse(rig.launched())


class Round4Tests(unittest.TestCase):
    """The round-3 confirm fixes (the director's list of ten)."""

    def test_reveal_rechecks_in_flight_under_the_lock(self):
        rig = Rig()
        commitment = rig.commitment()
        real = cw.Keychain.read
        n = []

        def read(self, item):
            n.append(item)
            if len(n) == 1:                       # between reveal's first check and its locked write
                other = cw.Context(rig.cfg)
                other.commit_event({"event": "spent", "key": rig.seal["seal_digest"], "role": "pv-writer"}, "m")
            return real(self, item)

        with mock.patch.object(cw.Keychain, "read", read):
            rc, out, err = run_main("reveal", "--config", rig.config, "--config-sha256", rig.config_sha,
                                    "--seal-digest", rig.seal["seal_digest"], "--commitment", commitment,
                                    "--after-stop", "ST1")
        self.assertEqual((rc, out), (cw.REFUSED, ""), err)
        self.assertIn("in flight", err)
        self.assertNotIn("reveal", [e["event"] for e in rig.events()])
        self.assertNotIn("reveal", [r for _, _, r in rig.markers()])

    def test_a_local_only_outcome_is_still_in_flight(self):
        rig = Rig()
        real = cw.Mirror.publish
        n = []

        def publish(self, data, message, seq):
            n.append(1)
            if len(n) == 2:
                raise cw.Stop(cw.REFUSED, "push refused")
            return real(self, data, message, seq)

        with mock.patch.object(cw.Mirror, "publish", publish):
            self.assertEqual(rig.run("pv-writer")[0], cw.TERMINAL)
        self.assertIn("completed", [e["event"] for e in rig.events()])      # local only
        rc, out, err = run_main("reveal", "--config", rig.config, "--config-sha256", rig.config_sha,
                                "--seal-digest", rig.seal["seal_digest"], "--commitment", rig.commitment(),
                                "--after-stop", "ST1")
        self.assertEqual((rc, out), (cw.REFUSED, ""), err)
        self.assertIn("in flight", err)

    def test_a_typed_break_with_an_echo_is_still_a_break(self):
        rig = Rig(role_flags={"pv-writer": ["--echo-secret"]})
        rig.reseal(json.dumps({"products": {"synthetic-truth-u0.json": "0" * 64}}).encode())
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        e = rig.events()[-1]
        self.assertEqual(e["event"], "break")
        self.assertIn("echoed a secret", e["detail"])

    def test_an_in_role_break_whose_marker_fails_still_records_the_line(self):
        rig = Rig()
        rig.reseal(json.dumps({"products": {"synthetic-truth-u0.json": "0" * 64}}).encode())
        real = cw.Record.mark

        def mark(self, kind, key, role):
            if kind == "break":
                raise OSError("read-only")
            return real(self, kind, key, role)

        with mock.patch.object(cw.Record, "mark", mark):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual(rig.events()[-1]["event"], "break")
        self.assertIn("could not be written", rig.events()[-1]["detail"])
        self.assertEqual(rig.run("pv-readout")[0], cw.TERMINAL)

    def test_a_shallow_mirror_is_refused(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        shallow = os.path.join(rig.root, "shallow")
        subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", "covfix-consumption", "file://" + rig.bare, shallow],
                       check=True)
        rig.cfg["mirror"]["worktree"] = shallow
        rig.write_config()
        rc, _, err = rig.run("pv-readout")
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("shallow", err)

    def test_a_record_changed_between_validation_and_append_is_terminal(self):
        rig = Rig()
        real = cw.Record.append
        recpath = os.path.join(rig.cfg["record_dir"], "RECORD.jsonl")

        def append(self, event, expected=None):
            if event["event"] == "spent":
                with open(recpath, "ab") as f:       # a writer that ignored the lock
                    f.write(b"")
                os.utime(recpath)
                with open(recpath, "wb") as f:
                    f.write(b"")
            return real(self, event, expected)

        self.assertEqual(rig.run("pv-writer")[0], 0)
        with mock.patch.object(cw.Record, "append", append):
            rc, _, err = rig.run("pv-readout")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("changed after it was validated", err)
        self.assertNotIn("pv-readout", slurp(os.path.join(rig.root, "at-launch.txt")))

    def test_a_same_role_uncertain_marker_before_launch_stops_it(self):
        rig = Rig()
        real = cw.Context.commit_event

        def commit(self, event, message, absorb_exclude=None, soft=False, gate=None):
            real(self, event, message, absorb_exclude, soft, gate)
            if event["event"] == "spent":
                self.record.mark("uncertain", event["key"], event["role"])

        with mock.patch.object(cw.Context, "commit_event", commit):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertFalse(rig.launched())
        self.assertIn("uncertain marker for pv-writer", rig.events()[-1]["detail"])

    def test_a_seal_list_without_the_manifest_is_a_break(self):
        rig = Rig()
        root = rig.seal["seal_root"]
        with open(rig.cfg["seal_file"], "w") as f:
            f.write(f"{cw.sha256_file(os.path.join(root, 'synthetic-truth-u0.json.gpg'))}  synthetic-truth-u0.json.gpg\n")
        rig.cfg["binding"]["seal_digest"] = cw.sha256_file(rig.cfg["seal_file"])
        rig.write_config()
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("does not list PG-MANIFEST.json.gpg", err)

    def test_inherited_slurm_io_settings_are_removed(self):
        rig = Rig()
        with mock.patch.dict(os.environ, {"SRUN_OUTPUT": "/tmp/leak-%j.out", "SRUN_INPUT": "none"}):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, 0, err)

    def test_gpg_gets_exactly_fds_0_to_3(self):
        d = tempfile.mkdtemp(dir=TMP)
        shim = os.path.join(d, "gpg")
        with open(shim, "w") as f:                 # Python, not bash: bash keeps its own fds 10-11 open
            f.write(f"#!{sys.executable} -I -S\nimport os\n"
                    "def is_open(i):\n    try:\n        os.fstat(i)\n        return True\n    except OSError:\n"
                    "        return False\n"
                    "print(*[i for i in range(3, 64) if is_open(i)])\n"
                    "p = os.read(3, 100).decode().strip()\n"
                    "print('pipe-ok' if len(p) == 64 else 'pipe-bad')\n")
        os.chmod(shim, 0o755)
        holder = None
        for occupy in (False, True):
            try:
                if occupy and not _fd_open(3):
                    holder = os.open(os.devnull, os.O_RDONLY)
                out = cw.gpg_run(cw.GPG_DECRYPT, "9" * 64, b"", gpg=shim)
            finally:
                if holder is not None:
                    os.close(holder)
                    holder = None
            self.assertEqual(out.decode().split(), ["3", "pipe-ok"], occupy)

    def test_gpg_fd3_with_stdout_closed_and_fd3_taken(self):
        code = ("import os, sys; sys.path.insert(0, sys.argv[1]); import covfix_wrapper as cw\n"
                "a = os.open(os.devnull, os.O_RDONLY)\n"
                "if not cw._fd_is_open(3): os.dup2(a, 3)\n"
                "os.close(1)\n"
                "pw = '4' * 64\n"
                "ok = cw.gpg_run(cw.GPG_DECRYPT, pw, cw.gpg_run(cw.GPG_ENCRYPT, pw, b'w')) == b'w'\n"
                "sys.stderr.write('combined ok\\n' if ok else 'bad\\n')\n")
        r = subprocess.run([sys.executable, "-c", code, HERE], capture_output=True, text=True)
        self.assertEqual(r.stderr.strip(), "combined ok", r.stderr)

    def test_the_real_ledger_branch_and_run_hooks_type(self):
        rig = Rig()
        with mock.patch.dict(os.environ, {cw.FORBID_REAL_ENV: ""}):
            with self.assertRaises(cw.Stop) as cm:
                cw.Context({**rig.cfg, "keychain_prefix": "covfix-", "record_dir": cw.REAL_RECORD_DIR})
            self.assertIn("covfix-ledger", str(cm.exception))
        rig.cfg["mirror"]["run_hooks"] = "no"
        rig.write_config()
        self.assertEqual(rig.run("pv-writer")[0], cw.ERROR)

    def test_a_compute_side_read_error_is_not_a_break(self):
        rig = Rig()
        pw = rig.kc.read("passphrase")
        ct = os.path.join(rig.seal["seal_root"], "synthetic-truth-u0.json.gpg")
        os.chmod(ct, 0)
        try:
            r = subprocess.run([sys.executable, REF, "--role", "pv-writer", "--covfix-attempt", "a3",
                                "--covfix-seal-root", rig.seal["seal_root"]], input=(pw + "\n").encode(),
                               capture_output=True)
            man = os.path.join(rig.seal["seal_root"], "PG-MANIFEST.json.gpg")
            os.chmod(ct, 0o600)
            os.chmod(man, 0)
            r2 = subprocess.run([sys.executable, REF, "--role", "pv-writer", "--covfix-attempt", "a3",
                                 "--covfix-seal-root", rig.seal["seal_root"]], input=(pw + "\n").encode(),
                                capture_output=True)
        finally:
            os.chmod(ct, 0o600)
            os.chmod(os.path.join(rig.seal["seal_root"], "PG-MANIFEST.json.gpg"), 0o600)
        for res in (r, r2):
            self.assertEqual(res.returncode, 1, res.stderr)
            self.assertNotIn(b"covfix-break", res.stdout)


class ConfirmBlockerTests(unittest.TestCase):
    """The three blockers of the round-4 confirm."""

    def reveal(self, rig, *extra):
        return run_main("reveal", "--config", rig.config, "--config-sha256", rig.config_sha,
                        "--seal-digest", rig.seal["seal_digest"], "--commitment", rig.cfg["binding"]["commitment"],
                        *extra)

    def test_a_terminal_readout_needs_a_ruling_before_reveal(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        rig.set_ssh_mode("drop-link")
        self.assertEqual(rig.run("pv-readout")[0], cw.TERMINAL)
        rig.set_ssh_mode("")
        self.assertIn(b'"terminal"', rig.remote_record())
        for extra in ((), ("--after-stop", "ST3"), ("--inflight-resolved", "DECISION-readout-ended")):
            rc, out, err = self.reveal(rig, *extra)
            self.assertEqual((rc, out), (cw.REFUSED, ""), (extra, err))
        rc, out, err = self.reveal(rig, "--after-stop", "ST3", "--inflight-resolved", "DECISION-readout-ended")
        self.assertEqual(rc, 0, err)

    def test_another_invocations_preflight_break_is_not_the_readouts_end(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        rig.set_ssh_mode("drop-link")
        self.assertEqual(rig.run("pv-readout")[0], cw.TERMINAL)
        rig.set_ssh_mode("")
        ctx = cw.Context(rig.cfg)                          # a second readout invocation's preflight break
        ctx.commit_event({"event": "break", "key": rig.seal["seal_digest"], "role": "pv-readout",
                          "detail": "preflight"}, "m")
        self.assertIn(b'"break"', rig.remote_record())
        for extra in ((), ("--after-stop", "ST3"), ("--inflight-resolved", "DECISION-readout-ended")):
            rc, out, err = self.reveal(rig, *extra)
            self.assertEqual((rc, out), (cw.REFUSED, ""), (extra, err))
        rc, out, err = self.reveal(rig, "--after-stop", "ST3", "--inflight-resolved", "DECISION-readout-ended")
        self.assertEqual(rc, 0, err)

    def test_the_readouts_own_break_is_a_confirmed_end(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        with mock.patch.object(cw.Cluster, "launch", return_value=cw.LaunchResult(cw.BREAK_RC, True, False, True, False)):
            self.assertEqual(rig.run("pv-readout")[0], cw.TERMINAL)
        rc, out, err = self.reveal(rig)
        self.assertEqual(rc, 0, err)

    def test_a_restore_after_the_write_cannot_change_what_is_published(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        recpath = os.path.join(rig.cfg["record_dir"], "RECORD.jsonl")
        older = slurp(recpath, "rb").splitlines(keepends=True)[0]       # the writer's spend only
        real = cw.fsync_dir
        state = {"done": False}

        def fsync_dir(path):
            real(path)
            if not state["done"] and b'"pv-readout"' in slurp(recpath, "rb") and b'"spent"' in slurp(recpath, "rb"):
                state["done"] = True
                with open(recpath, "wb") as f:                  # restored right after the readout's append
                    f.write(older)

        with mock.patch.object(cw, "fsync_dir", fsync_dir):
            rc, _, err = rig.run("pv-readout")
        self.assertTrue(state["done"])
        pushed = rig.remote_record()
        self.assertIn(b'"role":"pv-readout"', pushed)                  # the spend is durable in the mirror
        self.assertIn(b'"completed"', pushed.splitlines()[1])          # and the writer's completion was kept
        rc2, _, err2 = rig.run("pv-readout")
        self.assertEqual(rc2, cw.TERMINAL, err2)

    def test_a_fresh_mirror_checkout_and_a_restored_record_are_caught(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        recpath = os.path.join(rig.cfg["record_dir"], "RECORD.jsonl")
        older = slurp(recpath, "rb").splitlines(keepends=True)[0]
        fresh = os.path.join(rig.root, "fresh")
        subprocess.run(["git", "clone", "-q", "-b", "covfix-consumption", rig.bare, fresh], check=True)
        rig.cfg["mirror"]["worktree"] = fresh
        rig.write_config()
        for n in os.listdir(rig.cfg["record_dir"]):
            if n.startswith("MARK-"):
                os.unlink(os.path.join(rig.cfg["record_dir"], n))
        with open(recpath, "wb") as f:
            f.write(older)
        rc, _, err = rig.run("pv-readout")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("not an extension", err)
        self.assertFalse(b"pv-readout" in rig.remote_record())

    def test_the_lock_snapshot_is_what_every_locked_check_reads(self):
        d = tempfile.mkdtemp(dir=TMP)
        os.rmdir(d)
        rec = cw.Record(d)
        rec.ensure_dir()
        rec.lock()
        try:
            snap = rec.raw()
            with open(rec.path, "wb") as f:
                f.write(b"restored\n")
            self.assertEqual(rec.raw(), snap)
            with self.assertRaises(OSError):
                rec.append({"key": "1" * 64, "role": "pv-writer", "event": "spent"})
        finally:
            rec.unlock()
        self.assertEqual(rec.raw(), b"restored\n")


def protect(bare: str) -> None:
    """Make a local bare repo refuse what GitHub ruleset 27996874 ("covfix-ledger append-only") refuses on the real
    ledger branch: non-fast-forward updates and deletion. Creation and fast-forward pushes stay allowed."""
    for key in ("receive.denyNonFastForwards", "receive.denyDeletes"):
        subprocess.run(["git", "--git-dir", bare, "config", key, "true"], check=True)


def other_writer(rig) -> str:
    """A second clone of the rig's remote, standing in for any other writer."""
    d = tempfile.mkdtemp(dir=rig.root)
    subprocess.run(["git", "clone", "-q", "-b", "covfix-consumption", rig.bare, d], check=True, capture_output=True)
    return d


def remote_tip(rig) -> str:
    return subprocess.run(["git", "--git-dir", rig.bare, "rev-parse", "refs/heads/covfix-consumption"],
                          capture_output=True, text=True, check=True).stdout.strip()


def launches(rig) -> int:
    """How many times ssh was asked to start a bound binary (the only path on which the frame is sent)."""
    return sum("covfix-exec" in e["argv"][-1] for e in rig.ssh_log())


class LedgerProtectionTests(unittest.TestCase):
    """The wrapper under a remote that refuses non-fast-forward updates and deletion (ruleset 27996874 on
    covfix-ledger). The wrapper only ever creates the branch and pushes fast-forward; a refused push, a deletion or a
    rewind must fail closed with no launch, so no secret reaches a bound binary and nothing is decrypted."""

    def test_under_protection_the_first_push_creates_the_branch_and_later_pushes_fast_forward(self):
        rig = Rig()
        protect(rig.bare)
        subprocess.run(["git", "--git-dir", rig.bare, "update-ref", "-d", "refs/heads/covfix-consumption"], check=True)
        rc, _, err = rig.run("pv-writer")                       # creates the branch: allowed
        self.assertEqual(rc, 0, err)
        first = remote_tip(rig)
        rc, _, err = rig.run("pv-readout")                      # appends fast-forward: allowed
        self.assertEqual(rc, 0, err)
        second = remote_tip(rig)
        self.assertNotEqual(first, second)
        self.assertEqual(subprocess.run(["git", "--git-dir", rig.bare, "merge-base", "--is-ancestor", first, second])
                         .returncode, 0)
        self.assertEqual([(e["event"], e["role"]) for e in rig.events()],
                         [("spent", "pv-writer"), ("completed", "pv-writer"),
                          ("spent", "pv-readout"), ("completed", "pv-readout")])
        self.assertEqual(rig.remote_record(), slurp(os.path.join(rig.cfg["record_dir"], "RECORD.jsonl"), "rb"))

    def test_a_push_refused_as_non_fast_forward_fails_closed_before_launch(self):
        # Another writer appends between the wrapper's fetch and its push. The wrapper's push must be refused, with
        # or without the host's protection: it never forces.
        for protected in (True, False):
            with self.subTest(protected=protected):
                rig = Rig()
                if protected:
                    protect(rig.bare)
                self.assertEqual(rig.run("pv-writer")[0], 0)
                before = launches(rig)
                self.assertEqual(before, 1)
                other = other_writer(rig)
                real, raced = cw.Mirror.git, []

                def mgit(self, *args, check=True, input=None):
                    if "push" in args and not raced:
                        raced.append(1)
                        with open(os.path.join(other, "README"), "a") as f:
                            f.write("another writer\n")
                        git(other, "-c", "user.name=o", "-c", "user.email=o@o", "commit", "-q", "-am", "sibling")
                        git(other, "push", "-q", "origin", "HEAD:refs/heads/covfix-consumption")
                    return real(self, *args, check=check, input=input)

                with mock.patch.object(cw.Mirror, "git", mgit):
                    rc, _, err = rig.run("pv-readout")
                self.assertTrue(raced)
                self.assertEqual(rc, cw.TERMINAL, err)
                self.assertIn("uncertain", err)
                self.assertRegex(err, r"git [^:]*push failed")      # the remote refused the push itself
                self.assertEqual(launches(rig), before)
                self.assertEqual(remote_tip(rig), git(other, "rev-parse", "HEAD").strip())   # nothing overwritten
                self.assertNotIn(b'"pv-readout"', rig.remote_record())
                self.assertEqual(sorted(k for k, _, r in rig.markers() if r == "pv-readout"), ["attempt", "uncertain"])
                rc, _, err = rig.run("pv-readout")                 # the role stays blocked
                self.assertEqual(rc, cw.TERMINAL, err)
                self.assertEqual(launches(rig), before)

    def test_a_deletion_is_refused_and_a_bypassed_deletion_fails_closed_before_launch(self):
        rig = Rig()
        protect(rig.bare)
        self.assertEqual(rig.run("pv-writer")[0], 0)
        tip = remote_tip(rig)
        r = subprocess.run(["git", "-C", other_writer(rig), "push", "origin", "--delete", "covfix-consumption"],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("deletion prohibited", r.stderr)
        self.assertEqual(remote_tip(rig), tip)
        before = launches(rig)
        self.assertEqual(before, 1)                              # the pv-writer run launched once
        subprocess.run(["git", "--git-dir", rig.bare, "update-ref", "-d", "refs/heads/covfix-consumption"], check=True)
        rc, _, err = rig.run("pv-readout")                      # as if an admin had bypassed the rule
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("gone after it was published", err)
        self.assertEqual(launches(rig), before)
        self.assertNotIn("pv-readout", [e["role"] for e in rig.events()])

    def test_a_rewind_is_refused_and_a_bypassed_rewind_fails_closed_before_launch(self):
        rig = Rig()
        protect(rig.bare)
        self.assertEqual(rig.run("pv-writer")[0], 0)
        tip = remote_tip(rig)
        other = other_writer(rig)
        first = git(other, "rev-list", "--max-parents=0", "HEAD").strip()
        git(other, "reset", "-q", "--hard", first)
        r = subprocess.run(["git", "-C", other, "push", "-f", "origin", "HEAD:refs/heads/covfix-consumption"],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("non-fast-forward", r.stderr)
        self.assertEqual(remote_tip(rig), tip)
        before = launches(rig)
        self.assertEqual(before, 1)                              # the pv-writer run launched once
        subprocess.run(["git", "--git-dir", rig.bare, "update-ref", "refs/heads/covfix-consumption", first], check=True)
        rc, _, err = rig.run("pv-readout")                      # as if an admin had bypassed the rule
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("rewound", err)
        self.assertEqual(launches(rig), before)
        self.assertNotIn("pv-readout", [e["role"] for e in rig.events()])


class ReferenceRoleTests(unittest.TestCase):
    def test_malformed_frames_refuse(self):
        rig = Rig()
        pw = rig.kc.read("passphrase")
        for role, frame in (("pv-writer", pw + "\nextra\n"), ("pv-writer", pw), ("pg-connect", pw + "\n"),
                            ("pg-connect", pw + "\n123\n")):
            r = subprocess.run([sys.executable, REF, "--role", role, "--covfix-attempt", "a",
                                "--covfix-seal-root", rig.seal["seal_root"]], input=frame.encode(), capture_output=True)
            self.assertNotEqual(r.returncode, 0, (role, frame[-8:]))

    def test_a_product_off_its_manifest_hash_is_a_typed_break(self):
        rig = Rig()
        pw = rig.kc.read("passphrase")
        sealed = rig.seal["seal_root"]
        bad = {"products": {"synthetic-truth-u0.json": "0" * 64}}
        with open(os.path.join(sealed, "PG-MANIFEST.json.gpg"), "wb") as f:
            f.write(cw.gpg_run(cw.GPG_ENCRYPT, pw, json.dumps(bad).encode()))
        r = subprocess.run([sys.executable, REF, "--role", "pv-writer", "--covfix-attempt", "a9",
                            "--covfix-seal-root", sealed], input=(pw + "\n").encode(), capture_output=True)
        self.assertEqual(r.returncode, cw.BREAK_RC)
        self.assertIn(b"does not reproduce", r.stderr)
        self.assertEqual(r.stdout.strip().splitlines()[-1], b"covfix-break a9")

    def test_a_missing_manifest_or_product_is_a_typed_break(self):
        rig = Rig()
        pw = rig.kc.read("passphrase")
        sealed = rig.seal["seal_root"]
        for gone in ("synthetic-truth-u0.json.gpg", "PG-MANIFEST.json.gpg"):
            os.unlink(os.path.join(sealed, gone))
            r = subprocess.run([sys.executable, REF, "--role", "pv-writer", "--covfix-attempt", "a7",
                                "--covfix-seal-root", sealed], input=(pw + "\n").encode(), capture_output=True)
            self.assertEqual(r.returncode, cw.BREAK_RC, (gone, r.stderr))
            self.assertEqual(r.stdout.strip().splitlines()[-1], b"covfix-break a7")

    def test_wrong_passphrase_fails_in_gpg(self):
        rig = Rig()
        r = subprocess.run([sys.executable, REF, "--role", "pv-readout", "--covfix-attempt", "a",
                            "--covfix-seal-root", rig.seal["seal_root"]],
                           input=(secrets.token_hex(32) + "\n").encode(), capture_output=True)
        self.assertEqual(r.returncode, cw.TERMINAL)


if __name__ == "__main__":
    unittest.main()
