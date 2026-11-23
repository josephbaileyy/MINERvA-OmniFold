"""Tests for covfix_wrapper.py.

HARD RULES these tests keep: Keychain items are covfix-test-<random>-* only, created and deleted here, and
COVFIX_FORBID_REAL_KEYCHAIN is set so the real covfix-* prefix refuses; ssh, salloc and srun are local stubs and
nothing leaves this machine; every seal digest is a synthetic one built here, so no test is a launch.

    python3 -m unittest -v test_covfix_wrapper
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
PREFIXES = []
TMP = tempfile.mkdtemp(prefix="covfix-wrapper-test-")
# gpg-agent's socket lives in the home directory and a macOS socket path is capped near 104 bytes, so the
# throwaway GNUPGHOME gets a short /tmp path rather than one under TMP.
GNUPGHOME = tempfile.mkdtemp(prefix="cfxg", dir="/tmp")
os.chmod(GNUPGHOME, 0o700)
os.environ["GNUPGHOME"] = GNUPGHOME
REF = os.path.join(HERE, "reference_role.py")


def new_prefix() -> str:
    p = f"covfix-test-{secrets.token_hex(4)}-"
    PREFIXES.append(p)
    return p


def delete_items(prefix: str) -> None:
    assert prefix.startswith("covfix-test-"), prefix
    for item in cw.ITEMS:
        subprocess.run([cw.SECURITY, "delete-generic-password", "-s", prefix + item, "-a", cw.ACCOUNT],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def tearDownModule():
    for p in PREFIXES:
        delete_items(p)
    subprocess.run(["gpgconf", "--homedir", GNUPGHOME, "--kill", "gpg-agent"], capture_output=True)
    shutil.rmtree(TMP, ignore_errors=True)
    shutil.rmtree(GNUPGHOME, ignore_errors=True)


def slurp(path, mode="r"):
    with open(path, mode) as f:
        return f.read()


def run_main(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = cw.main(list(argv))
    return rc, out.getvalue(), err.getvalue()


def git(cwd, *args):
    r = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True)
    assert r.returncode == 0, (args, r.stderr)
    return r.stdout


STUB_SSH = r'''#!{python}
import json, os, subprocess, sys
here = {here!r}
host, command = sys.argv[1], sys.argv[2]
with open(os.path.join(here, "ssh-log.jsonl"), "a") as f:
    f.write(json.dumps({{"argv": sys.argv, "env": dict(os.environ)}}) + "\n")
mode = open(os.path.join(here, "ssh-mode")).read().strip() if os.path.exists(os.path.join(here, "ssh-mode")) else ""
if mode == "down":
    sys.exit(255)
if "covfix-hash-end" not in command:
    # a launch: record what the pushed mirror held at the moment the binary started
    r = subprocess.run(["git", "--git-dir", {bare!r}, "cat-file", "blob", "covfix-consumption:" + {rel!r}],
                       capture_output=True, text=True)
    with open(os.path.join(here, "at-launch.txt"), "w") as f:
        f.write(r.stdout)
    if mode == "drop-link":
        sys.stdin.read()
        sys.exit(255)
if mode == "no-end" and "covfix-hash-end" in command:
    r = subprocess.run(["bash", "-c", command], stdout=subprocess.PIPE)
    sys.stdout.write("".join(r.stdout.decode().splitlines(keepends=True)[:-1]))
    sys.exit(r.returncode)
if mode == "rc1" and "covfix-hash-end" in command:
    subprocess.run(["bash", "-c", command])
    sys.exit(1)
sys.exit(subprocess.run(["bash", "-c", command]).returncode)
'''

STUB_ALLOC = r'''#!/bin/bash
# stub salloc/srun: drop "--exclusive -N 1", exec the rest with stdin forwarded
[ "$1" = "--exclusive" ] && [ "$2" = "-N" ] && [ "$3" = "1" ] || {{ echo "stub {name}: unexpected flags $*" >&2; exit 64; }}
shift 3
exec "$@"
'''

REL = "docs/orchestration/state/2d-closeout/covfix-20261122/consumption/RECORD.jsonl"


class Rig:
    """One isolated campaign: test Keychain items, a synthetic seal, a bare 'origin', a mirror worktree, stubs."""

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
        ssh = os.path.join(self.bin, "ssh")
        with open(ssh, "w") as f:
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
            cmd = (f"{self.bin}/salloc --exclusive -N 1 {self.bin}/srun --exclusive -N 1 {sys.executable} {REF} "
                   f"--role {role} --sealed {self.seal['seal_root']} {flags.get(role, '')}")
            roles[role] = {"command": cmd, "binary": REF, "binary_sha256": cw.sha256_file(REF)}
        self.cfg = {
            "record_dir": os.path.join(self.root, "record"),
            "keychain_prefix": self.prefix,
            "ssh": [ssh], "host": "stub-login",
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

    def run(self, role, **kw):
        argv = ["run", "--config", self.config, "--config-sha256", kw.get("config_sha", self.config_sha),
                "--role", role]
        if role == "pg-connect":
            argv += ["--commitment", kw.get("commitment", self.commitment())]
        else:
            argv += ["--seal-digest", kw.get("seal", self.seal["seal_digest"]),
                     "--freeze-digest", kw.get("freeze", self.seal["freeze_digest"])]
        return run_main(*argv)

    def events(self):
        return cw.Record(self.cfg["record_dir"]).lines()

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

    def test_generate_refuses_if_any_single_item_exists(self):
        kc = cw.Keychain(new_prefix())
        kc.add("salt", "ab" * 32)
        self.assertEqual(cw.generate(kc), "exists")
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

    def test_partial_generate_failure_reports_counts_without_values(self):
        kc = cw.Keychain(new_prefix())
        real_add = cw.Keychain.add

        def add(self, item, value):
            if item == "salt":
                raise cw.Stop(cw.ERROR, "boom")
            return real_add(self, item, value)

        with mock.patch.object(cw.Keychain, "add", add):
            with self.assertRaises(cw.Stop) as cm:
                cw.generate(kc)
        self.assertIn("created 2 of 3", str(cm.exception))
        self.assertNotIn(kc.read("passphrase"), str(cm.exception))


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
        k, k2 = "1" * 64, "2" * 64
        ev = [{"seq": 0, "key": k, "role": "pv-writer", "event": "spent", "freeze": "f" * 64},
              {"seq": 1, "key": k2, "role": "pv-writer", "event": "break"}]
        self.assertIsNotNone(cw.blocked(ev, k, "pv-writer"))
        self.assertIsNone(cw.blocked(ev, k, "pv-readout"))
        self.assertIsNotNone(cw.blocked(ev, k2, "pv-readout"))
        self.assertIsNone(cw.blocked(ev, "3" * 64, "pv-writer"))
        self.assertEqual(cw.bound_freeze(ev, k), "f" * 64)
        self.assertIsNone(cw.bound_freeze(ev, k2))

    def test_markers_are_absorbed_into_the_chain(self):
        self.rec.mark_uncertain("4" * 64, "pv-readout")
        self.rec.mark_uncertain("4" * 64, "pv-readout")
        self.assertEqual(self.rec.markers(), [("4" * 64, "pv-readout")])
        self.rec.lock()
        try:
            self.rec.absorb_markers()
            self.rec.absorb_markers()
        finally:
            self.rec.unlock()
        ev = self.rec.lines()
        self.assertEqual([(e["event"], e["role"]) for e in ev], [("uncertain", "pv-readout")])

    def test_unreadable_marker_is_terminal(self):
        with open(os.path.join(self.dir, "UNCERTAIN-junk"), "w") as f:
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

    def test_missing_keys(self):
        path = os.path.join(TMP, "partial.json")
        with open(path, "w") as f:
            json.dump({"record_dir": "x"}, f)
        with self.assertRaises(cw.Stop):
            cw.load_config(path, cw.sha256_file(path))


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

    def test_no_secret_in_any_argv_env_record_or_output(self):
        rig = Rig()
        rc, out, err = rig.run("pv-writer")
        self.assertEqual(rc, 0, err)
        rc2, out2, err2 = rig.run("pg-connect")
        self.assertEqual(rc2, 0, err2)
        blobs = [json.dumps(rig.ssh_log()), out, err, out2, err2, rig.remote_record().decode(),
                 slurp(rig.config)]
        for dirpath, _, files in os.walk(rig.root):
            if "/.git" in dirpath or dirpath.endswith(".git") or "origin.git" in dirpath or "gnupg" in dirpath:
                continue
            for f in files:
                blobs.append(slurp(os.path.join(dirpath, f), "rb").decode("latin-1"))
        for s in rig.secrets():
            for b in blobs:
                self.assertNotIn(s, b)

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

    def test_a_changed_freeze_cannot_create_a_fresh_role(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        with open(rig.cfg["freeze_file"], "a") as f:
            f.write(f"{cw.sha256_file(rig.cfg['freeze_file'])}  extra.txt\n")
        new_freeze = cw.sha256_file(rig.cfg["freeze_file"])
        rc, _, err = rig.run("pv-writer", freeze=new_freeze)
        self.assertEqual(rc, cw.TERMINAL, err)
        rc, _, err = rig.run("pv-readout", freeze=new_freeze)
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("bound to freeze", err)

    def test_crash_after_decrypt_is_terminal_with_no_retry(self):
        rig = Rig(role_flags={"pv-writer": "--fail-after-decrypt"})
        rc, out, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL)
        self.assertEqual([e["event"] for e in rig.events()], ["spent", "terminal"])
        self.assertEqual(rig.run("pv-writer")[0], cw.TERMINAL)

    def test_a_dropped_link_after_the_spend_is_terminal(self):
        rig = Rig()
        rig.set_ssh_mode("drop-link")
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual([e["event"] for e in rig.events()], ["spent", "terminal"])

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
        rig.set_ssh_mode("")
        self.assertEqual(rig.run("pv-writer")[0], 0)

    def test_an_altered_ciphertext_is_a_break_that_stops_every_role(self):
        rig = Rig()
        ct = os.path.join(rig.seal["seal_root"], "synthetic-truth-u0.json.gpg")
        with open(ct, "ab") as f:
            f.write(b"\0")
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("BREAK", err)
        self.assertEqual([e["event"] for e in rig.events()], ["break"])
        self.assertIn(b'"break"', rig.remote_record())
        self.assertFalse(os.path.exists(os.path.join(rig.root, "at-launch.txt")))
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
        rc, _, err = rig.run("pv-readout")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("P2-FREEZE", err)

    def test_seal_or_freeze_file_off_its_pinned_digest_is_a_break(self):
        for which in ("seal", "freeze"):
            rig = Rig()
            rc, _, err = rig.run("pv-writer", **{which: "e" * 64})
            self.assertEqual(rc, cw.TERMINAL, err)
            self.assertIn("pinned digest", err)

    def test_incomplete_hashing_refuses_without_a_break(self):
        for mode in ("no-end", "rc1"):
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

    def test_hashing_accounts_for_every_path(self):
        d = tempfile.mkdtemp(dir=TMP)
        with open(os.path.join(d, "a b"), "w") as f:
            f.write("x")
        # the stub ssh is bash -c '...' stub <host> <remote>: $1 is the host, $2 the remote command
        got, missing = cw.Cluster(["bash", "-c", 'exec bash -c "$2"', "stub"], "h").hash_files(d, ["a b", "gone"])
        self.assertEqual(got, {"a b": hashlib.sha256(b"x").hexdigest()})
        self.assertEqual(missing, {"gone"})

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
        self.assertFalse(os.path.exists(os.path.join(rig.root, "at-launch.txt")))
        self.assertEqual(cw.Record(rig.cfg["record_dir"]).markers(), [(rig.seal["seal_digest"], "pv-writer")])
        git(rig.wt, "remote", "set-url", "--push", "origin", rig.bare)
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("already consumed", err)
        self.assertEqual(rig.run("pv-readout")[0], 0)
        self.assertIn(b'"uncertain"', rig.remote_record())

    def test_a_remote_blob_mismatch_is_an_uncertain_spend(self):
        rig = Rig()
        with mock.patch.object(cw, "git_blob_sha", return_value="0" * 40):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertFalse(os.path.exists(os.path.join(rig.root, "at-launch.txt")))
        self.assertTrue(cw.Record(rig.cfg["record_dir"]).markers())

    def test_a_lock_failure_is_an_uncertain_spend(self):
        rig = Rig()
        with mock.patch.object(cw.Record, "lock", side_effect=OSError("held")):
            rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual(cw.Record(rig.cfg["record_dir"]).markers(), [(rig.seal["seal_digest"], "pv-writer")])
        self.assertEqual(rig.run("pv-writer")[0], cw.TERMINAL)

    def test_a_restored_older_record_is_detected(self):
        rig = Rig()
        recpath = os.path.join(rig.cfg["record_dir"], "RECORD.jsonl")
        self.assertEqual(rig.run("pv-writer")[0], 0)
        os.unlink(recpath)
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("not an extension of the pushed mirror", err)

    def test_a_restored_record_is_caught_by_history_even_if_the_branch_is_rewound(self):
        rig = Rig()
        recpath = os.path.join(rig.cfg["record_dir"], "RECORD.jsonl")
        self.assertEqual(rig.run("pv-writer")[0], 0)
        os.unlink(recpath)
        first = git(rig.wt, "rev-list", "--max-parents=0", "HEAD").strip()
        git(rig.wt, "tag", "keep-history", "HEAD")
        git(rig.wt, "reset", "-q", "--hard", first)
        git(rig.wt, "push", "-q", "-f", "origin", "HEAD:refs/heads/covfix-consumption")
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

    def test_pg_connect_frame_and_commitment(self):
        rig = Rig()
        rc, _, err = rig.run("pg-connect", commitment="f" * 64)
        self.assertEqual(rc, cw.REFUSED, err)
        self.assertIn("commitment", err)
        self.assertEqual(rig.events(), [])
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
            return 0

        with mock.patch.object(cw.Cluster, "launch", launch):
            self.assertEqual(rig.run("pg-connect")[0], 0)
            self.assertEqual(rig.run("pv-writer")[0], 0)
        pw, base, _ = rig.secrets()
        self.assertEqual(seen, [f"{pw}\n{base}\n".encode(), f"{pw}\n".encode()])

    def test_launch_zeroes_its_frame(self):
        frame = bytearray(b"abc\n")
        c = cw.Cluster(["true"], "h")
        self.assertEqual(c.launch("x", frame), 0)
        self.assertEqual(frame, bytearray(4))

    def test_bad_digest_arguments(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer", seal="xyz")[0], cw.REFUSED)
        self.assertEqual(rig.run("pg-connect", commitment="")[0], cw.REFUSED)


class RevealTests(unittest.TestCase):
    def reveal(self, rig, *extra, commitment=None):
        return run_main("reveal", "--config", rig.config, "--config-sha256", rig.config_sha,
                        "--seal-digest", rig.seal["seal_digest"], "--commitment", commitment or rig.commitment(),
                        *extra)

    def test_reveal_waits_for_the_readout(self):
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

    def test_after_stop_and_a_wrong_commitment(self):
        rig = Rig()
        rc, out, err = self.reveal(rig, "--after-stop", "ST1 construction finding", commitment="a" * 64)
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertEqual(out, "")
        rc, out, err = self.reveal(rig, "--after-stop", "  ")
        self.assertEqual(rc, cw.REFUSED)
        rc, out, err = self.reveal(rig, "--after-stop", "ST1 construction finding")
        self.assertEqual(rc, 0, err)
        self.assertIn("after stop: ST1", rig.events()[-1]["detail"])


class StatusTests(unittest.TestCase):
    def test_status(self):
        rig = Rig()
        self.assertEqual(rig.run("pv-writer")[0], 0)
        rc, out, _ = run_main("status", "--config", rig.config, "--config-sha256", rig.config_sha)
        self.assertEqual(rc, 0)
        self.assertEqual(out.count('"event"'), 2)
        self.assertIn("markers: []", out)


FAKE_SECURITY = r'''#!/bin/bash
# a stand-in for /usr/bin/security: mode file beside it picks the misbehaviour
mode=$(cat "$(dirname "$0")/mode")
case "$1" in
  -i) cat >/dev/null; exit 0 ;;
  find-generic-password)
    case "$mode" in
      rc1) exit 1 ;;
      nonascii) [ "${@: -1}" = "-w" ] && printf '\xff\n'; exit 0 ;;
      other) [ "${@: -1}" = "-w" ] && echo 00; exit 0 ;;
    esac ;;
esac
exit 0
'''


class FailureBranchTests(unittest.TestCase):
    """The refusal and failure branches the line trace found unexecuted by the tests above."""

    def fake_security(self, mode):
        d = tempfile.mkdtemp(dir=TMP)
        path = os.path.join(d, "security")
        with open(path, "w") as f:
            f.write(FAKE_SECURITY)
        os.chmod(path, 0o755)
        with open(os.path.join(d, "mode"), "w") as f:
            f.write(mode)
        return cw.Keychain("covfix-test-fake-", security=path)

    def test_keychain_odd_answers(self):
        with self.assertRaises(ValueError):
            cw.Keychain("covfix-test-").service("password")
        with self.assertRaises(cw.Stop) as cm:
            self.fake_security("rc1").exists("salt")
        self.assertEqual(cm.exception.code, cw.ERROR)
        with self.assertRaises(cw.Stop) as cm:
            self.fake_security("nonascii").read("salt")
        self.assertIn("not ASCII", str(cm.exception))
        with self.assertRaises(cw.Stop) as cm:
            self.fake_security("other").add("salt", "ab" * 32)
        self.assertIn("does not read back", str(cm.exception))

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
        self.assertEqual(cw.Cluster(["sh", "-c", "exit 0"], "h").launch("x", frame), 0)
        self.assertEqual(frame.count(0), len(frame))

    def test_launch_kills_its_child_on_an_interrupt(self):
        c = cw.Cluster(["sh", "-c", "sleep 5"], "h")
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

    def test_a_spend_that_lost_the_race_is_consumed_without_a_marker(self):
        rig = Rig()
        ctx = cw.Context(rig.cfg)
        ctx.record.ensure_dir()
        ev = {"event": "spent", "key": "5" * 64, "role": "pv-writer"}
        ctx.commit_event(dict(ev), "m")
        with self.assertRaises(cw.Consumed):
            ctx.commit_event(dict(ev), "m")
        self.assertEqual(ctx.record.markers(), [])

    def test_a_malformed_seal_file_that_matches_its_digest_is_a_break(self):
        rig = Rig()
        with open(rig.cfg["seal_file"], "w") as f:
            f.write("not a checksum line\n")
        rc, _, err = rig.run("pv-writer", seal=cw.sha256_file(rig.cfg["seal_file"]))
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("BREAK", err)

    def test_a_break_whose_record_fails_says_so(self):
        rig = Rig()
        git(rig.wt, "remote", "set-url", "--push", "origin", os.path.join(rig.root, "no-such.git"))
        with open(os.path.join(rig.seal["seal_root"], "PG-MANIFEST.json.gpg"), "ab") as f:
            f.write(b"\0")
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL, err)
        self.assertIn("recording the break failed", err)

    def test_an_outcome_that_cannot_be_mirrored_is_terminal(self):
        rig = Rig()
        real = cw.Mirror.publish
        n = []

        def publish(self, data, message):
            n.append(1)
            if len(n) == 2:
                raise cw.Stop(cw.REFUSED, "push refused")
            return real(self, data, message)

        with mock.patch.object(cw.Mirror, "publish", publish):
            rc, out, err = rig.run("pv-writer")
        self.assertEqual(rc, cw.TERMINAL)
        self.assertIn("was not mirrored", err)
        self.assertEqual(rig.run("pv-writer")[0], cw.TERMINAL)

    def test_the_first_spend_creates_the_mirror_branch(self):
        rig = Rig()
        subprocess.run(["git", "--git-dir", rig.bare, "update-ref", "-d", "refs/heads/covfix-consumption"], check=True)
        rc, _, err = rig.run("pv-writer")
        self.assertEqual(rc, 0, err)
        self.assertIn(b'"completed"', rig.remote_record())

    def test_synthetic_seal_round_trip_failure_and_cli(self):
        kc = cw.Keychain(new_prefix())
        cw.generate(kc)
        real = cw.gpg_run

        def gpg(argv, pw, payload, g="gpg", env=None):
            out = real(argv, pw, payload, g, env)
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

    def test_a_product_off_its_manifest_hash_refuses(self):
        rig = Rig()
        pw = rig.kc.read("passphrase")
        sealed = rig.seal["seal_root"]
        bad = {"products": {"synthetic-truth-u0.json": "0" * 64}}
        with open(os.path.join(sealed, "PG-MANIFEST.json.gpg"), "wb") as f:
            f.write(cw.gpg_run(cw.GPG_ENCRYPT, pw, json.dumps(bad).encode()))
        r = subprocess.run([sys.executable, REF, "--role", "pv-writer", "--sealed", sealed],
                           input=(pw + "\n").encode(), capture_output=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(b"does not reproduce", r.stderr)

    def test_wrong_passphrase_fails_in_gpg(self):
        rig = Rig()
        r = subprocess.run([sys.executable, REF, "--role", "pv-readout", "--sealed", rig.seal["seal_root"]],
                           input=(secrets.token_hex(32) + "\n").encode(), capture_output=True)
        self.assertEqual(r.returncode, cw.TERMINAL)


if __name__ == "__main__":
    unittest.main()
