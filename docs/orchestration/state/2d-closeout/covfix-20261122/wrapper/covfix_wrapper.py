#!/usr/bin/env python3
"""The director's wrapper for COVFIX's secret-bearing roles (COVFIX-DECLARATION ST4, sec. 3.4, sec. 4.2).

  generate        create the passphrase, the PG seed base and the salt in the macOS login Keychain, never on argv;
  commitment      print sha256(seed base ':' salt-hex), the value published before PG generates (sec. 4.2);
  run             run one secret-bearing role (pg-connect, pv-writer, pv-readout) through ST4's consumption record:
                  verify the seal and the freeze, spend the role durably (attempt marker, append, fsync, commit,
                  push, verify the remote blob), and only then pipe the secrets into the bound binary's stdin;
  reveal          print the seed base and salt after PV's readout, once they reproduce the commitment;
  synthetic-seal  build a dummy sealed truth with the same flags, for the end-to-end test of sec. 3.4;
  status          print the consumption record and markers (they hold no secret).

THE SECRETS go from `security find-generic-password -w` (the login Keychain, /usr/bin/security) into this
process's memory and then into the stdin of ssh (no PTY), which hands them to salloc/srun, which forward stdin to
the one task. They are never written to a file, put in an argument vector or the environment, or printed; the
task's own output passes through this process and any secret in it is redacted (and the run is terminal).

THE BINDING. The role config is sha-pinned in the binding, and it pins the campaign's digests (`binding`:
commitment, seal_digest, freeze_digest). The digests given on the command line must equal them. The real items
use one canonical ledger, ~/director-tools/covfix, whose mirror identity is fixed at its first write.

THE INTERFACE cov2d's bound binaries must match:
  stdin, then EOF:   pg-connect  b"<passphrase: 64 lowercase hex>\\n<seed base: ASCII decimal>\\n"
                     pv-writer, pv-readout  b"<passphrase: 64 lowercase hex>\\n"
  arguments:         the config's args, then --covfix-attempt <32 hex>, and for the PV roles
                     --covfix-seal-root <dir> --covfix-freeze-root <dir> (the roots the wrapper verified)
  stdout, last line: b"covfix-receipt <attempt>" after the role's work succeeded (else the run is terminal), or
                     b"covfix-break <attempt>" with exit status 66 for a confirmed integrity break of its inputs,
                     manifest or chain (recorded as a break of the whole seal)
  never print a secret; gpg in a fresh empty GNUPGHOME with the passphrase on fd 3; no core dumps.
The salt never leaves this laptop before `reveal`.

EXIT CODES: 0 done; 2 REFUSED (nothing spent, fix and retry); 3 TERMINAL (the role or the seal is stopped);
4 usage or environment error before any record was touched.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import errno
import fcntl
import hashlib
import json
import os
import pwd
import re
import resource
import secrets
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time

OK, REFUSED, TERMINAL, ERROR = 0, 2, 3, 4
BREAK_RC = 66                          # a bound binary's exit status for a confirmed integrity break
EXEC_MISMATCH_RC = 86                  # the compute-side hash check of the bound binary failed

SECURITY = "/usr/bin/security"
ACCOUNT = "director"
REAL_PREFIX = "covfix-"
REAL_RECORD_DIR = "~/director-tools/covfix"
TEST_PREFIX_RE = re.compile(r"covfix-(test|synth)-(?:[a-z0-9]+-)?")
ITEMS = ("passphrase", "seed-base", "salt")
FORBID_REAL_ENV = "COVFIX_FORBID_REAL_KEYCHAIN"
KEYCHAIN_PATH = re.compile(r"/[A-Za-z0-9/._-]+")

# PG's seed base (sec. 4.2): tune u's task seed = base + 10_000*u + task index, u in {0, 1}. run_gevgen_v3.sh
# passes the seed to gevgen as both --seed and -r, so every task seed must stay below 2**31 - 1.
SEED_BASE_LO = 1_000_000_000
SEED_BASE_HI = 2_000_000_000          # exclusive
TUNE_STRIDE = 10_000
N_TUNES = 2
MAX_TASK_INDEX = 9_999                # cov2d confirms PG's task index < 10_000 for F1's pipeline
assert SEED_BASE_HI + TUNE_STRIDE * (N_TUNES - 1) + MAX_TASK_INDEX < 2**31 - 1, "seed range overflows int32"

HEX64 = re.compile(r"[0-9a-f]{64}")
STOP_ID = re.compile(r"[A-Za-z][A-Za-z0-9._-]{0,79}")      # a named stop or ruling, e.g. ST1 or DECISION-2026...
SECRET_LIKE = re.compile(r"[0-9a-f]{16}|[0-9]{9}")

GPG_ENCRYPT = ("gpg", "--batch", "--yes", "--pinentry-mode", "loopback", "--passphrase-fd", "3",
               "--no-symkey-cache", "--symmetric", "--cipher-algo", "AES256", "--s2k-digest-algo", "SHA512",
               "--force-mdc")
GPG_DECRYPT = ("gpg", "--batch", "--pinentry-mode", "loopback", "--passphrase-fd", "3", "--no-symkey-cache",
               "--decrypt")

ROLES = {
    # role: (what keys its consumption, does its frame carry the seed base)
    "pg-connect": ("commitment", True),
    "pv-writer": ("seal", False),
    "pv-readout": ("seal", False),
}
OUTCOMES = ("completed", "terminal", "break")
CONFIRMED_END = ("completed", "break")  # the task's own receipt or break line: it ended. `terminal` does not say so
# A refused freeze conflict and the director's ruling that clears such refusals spend nothing (director, 2026-11-23).
NON_CONSUMING = ("freeze-mismatch-refused", "ruling")
FREEZE_MISMATCH_LIMIT = 2             # this many unresolved refusals on one seal block every role until a ruling
EVENTS = ("spent", "uncertain", "reveal") + OUTCOMES + NON_CONSUMING
SEAL_WIDE = ("break", "reveal")       # events that stop every role of their key
MARK_KINDS = ("attempt", "uncertain", "break")
RECORD_NAME = "RECORD.jsonl"
LEDGER_NAME = "LEDGER.json"
LOCK_NAME = "LOCK"
LOCK_TIMEOUT_S = 10.0
GENESIS = "0" * 64

# ssh is set up from a CLOSED schema (director, 2026-11-23): the role config's "ssh" object may hold only these keys,
# and the wrapper builds the whole argv and the whole environment itself.
SSH_KEYS = {"program", "user", "identity_file", "certificate_file", "agent"}
SSH_PROGRAM = "/usr/bin/ssh"                 # the real items use exactly this client
SSH_FORCED = ("-F", "none",                  # no ssh_config file: no Host/Match block can add anything
              "-T", "-o", "RequestTTY=no",
              "-o", "StrictHostKeyChecking=yes",
              "-o", "BatchMode=yes", "-o", "PreferredAuthentications=publickey",
              "-o", "PasswordAuthentication=no", "-o", "KbdInteractiveAuthentication=no",
              "-o", "IdentitiesOnly=yes",
              "-o", "ControlMaster=no", "-o", "ControlPath=none",
              "-o", "NoHostAuthenticationForLocalhost=no", "-o", "PermitLocalCommand=no",
              "-o", "ProxyCommand=none", "-o", "ProxyJump=none")
SSH_USER = re.compile(r"[a-z_][a-z0-9_.-]{0,31}")
SSH_HOST = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?")
LITERAL_PATH = re.compile(r"/[A-Za-z0-9/._+-]+")   # absolute and literal: no ~, $, % or spaces
SLURM_VALUE = re.compile(r"[A-Za-z0-9_:.,=/-]{1,64}")
SLURM_KEYS = {"account": "-A", "qos": "-q", "constraint": "-C", "time": "-t"}
# Inherited Slurm I/O settings that could send the task's stdin or output anywhere but the wrapper's pipes.
# The job name of each role: a literal constant, never derived from config or input (director, 2026-11-25), so fences
# and sacct can recognize covfix jobs. The config cannot set -J (SLURM_KEYS has no job-name key).
JOB_NAMES = {"pg-connect": "covfix_pg_connect", "pv-writer": "covfix_pv_writer", "pv-readout": "covfix_pv_readout"}
SLURM_IO_ENV = ("SRUN_INPUT", "SRUN_OUTPUT", "SRUN_ERROR", "SLURM_STDINMODE", "SLURM_STDOUTMODE", "SLURM_STDERRMODE")
REAL_LEDGER_BRANCH = "covfix-ledger"
MANIFEST_CIPHERTEXT = "PG-MANIFEST.json.gpg"


class Stop(Exception):
    """A refusal or a terminal stop, with the exit code it maps to."""

    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


class Consumed(Stop):
    """The role was spent, stopped or marked before: terminal, and no new marker is needed."""

    def __init__(self, message: str):
        super().__init__(TERMINAL, message)


class GateRefusal(Stop):
    """A gate re-checked under the lock refused: nothing is written and no marker is made."""

    def __init__(self, message: str):
        super().__init__(REFUSED, message)


class FreezeConflict(Stop):
    """A freeze other than the one bound to the seal: refused, spends nothing, and is recorded."""

    def __init__(self, key: str, presented: str, bound: str):
        super().__init__(REFUSED, f"seal {key[:12]} is bound to freeze {bound[:12]}, not {presented[:12]}")
        self.key, self.presented, self.bound = key, presented, bound


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return sha256_bytes(f.read())


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fsync_dir(path: str) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        n = os.write(fd, view)
        if n <= 0:
            raise OSError("short write")
        view = view[n:]


def no_core_dumps() -> None:
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def str_list(x, what: str) -> list:
    if not isinstance(x, list) or not all(isinstance(i, str) for i in x):
        raise Stop(ERROR, f"{what} must be a JSON list of strings")
    return list(x)


# ----------------------------------------------------------------------------------------------------------
# Keychain
# ----------------------------------------------------------------------------------------------------------

def check_prefix(prefix: str) -> str:
    if prefix == REAL_PREFIX:
        if os.environ.get(FORBID_REAL_ENV):
            raise Stop(ERROR, f"the real Keychain prefix {REAL_PREFIX!r} is forbidden here ({FORBID_REAL_ENV})")
        return prefix
    if isinstance(prefix, str) and TEST_PREFIX_RE.fullmatch(prefix):
        return prefix
    raise Stop(ERROR, f"Keychain prefix {prefix!r} is neither {REAL_PREFIX!r} nor covfix-test-*/covfix-synth-*")


def home_dir() -> str:
    """This user's home directory from the password database, never the launch environment's HOME."""
    return pwd.getpwuid(os.getuid()).pw_dir


def base_env() -> dict:
    """The minimal environment the wrapper gives `security` and ssh: HOME from home_dir(), PATH=/usr/bin:/bin and
    LANG=C."""
    return {"HOME": home_dir(), "PATH": "/usr/bin:/bin", "LANG": "C"}


def login_keychain(security: str = SECURITY) -> str:
    r = subprocess.run([security, "login-keychain"], stdin=subprocess.DEVNULL, capture_output=True, text=True,
                       env=base_env())
    path = r.stdout.strip().strip('"')
    if r.returncode != 0 or not KEYCHAIN_PATH.fullmatch(path):
        raise Stop(ERROR, "cannot resolve the login Keychain to a plain path")
    return path


class Keychain:
    """The three director-held items, service names <prefix><item>, account 'director', in the LOGIN Keychain
    (every call names it). The real items always use /usr/bin/security and the resolved login Keychain."""

    def __init__(self, prefix: str, security: str = SECURITY, keychain: str | None = None):
        self.prefix = check_prefix(prefix)
        if self.prefix == REAL_PREFIX and (security != SECURITY or keychain is not None):
            raise Stop(ERROR, "the real Keychain items take no security or keychain override")
        self.security = security
        self.keychain = keychain or login_keychain(security)
        if not KEYCHAIN_PATH.fullmatch(self.keychain):
            raise Stop(ERROR, "the Keychain path must be plain (letters, digits, / . _ -)")

    def service(self, item: str) -> str:
        if item not in ITEMS:
            raise ValueError(item)
        return self.prefix + item

    def exists(self, item: str) -> bool:
        r = subprocess.run([self.security, "find-generic-password", "-s", self.service(item), "-a", ACCOUNT,
                            self.keychain], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, env=base_env())
        if r.returncode == 0:
            return True
        if r.returncode == 44:          # errSecItemNotFound
            return False
        raise Stop(ERROR, f"security find-generic-password exited {r.returncode} for {self.service(item)}")

    def read(self, item: str) -> str:
        r = subprocess.run([self.security, "find-generic-password", "-s", self.service(item), "-a", ACCOUNT, "-w",
                            self.keychain], stdin=subprocess.DEVNULL, capture_output=True, env=base_env())
        if r.returncode != 0:
            raise Stop(REFUSED, f"cannot read Keychain item {self.service(item)} (security exited {r.returncode})")
        try:
            return r.stdout.decode("ascii").rstrip("\n")
        except UnicodeDecodeError:
            raise Stop(REFUSED, f"Keychain item {self.service(item)} is not ASCII")

    def add(self, item: str, value: str) -> None:
        """Store a value via `security -i` on stdin, so it is never in any process's argv. Never overwrites."""
        if not re.fullmatch(r"[0-9a-f]+", value):
            raise ValueError("only lowercase hex or decimal values are stored")
        command = f"add-generic-password -s {self.service(item)} -a {ACCOUNT} -w {value} {self.keychain}\n"
        r = subprocess.run([self.security, "-i"], input=command.encode("ascii"), capture_output=True, env=base_env())
        if r.returncode != 0:
            raise Stop(ERROR, f"security -i add exited {r.returncode} for {self.service(item)}"
                              + (" (item already exists)" if r.returncode == 45 else ""))
        if self.read(item) != value:
            raise Stop(ERROR, f"Keychain item {self.service(item)} does not read back as written")


def parse_seed_base(text: str) -> int:
    if not re.fullmatch(r"[1-9][0-9]*", text):
        raise Stop(REFUSED, "the seed base is not ASCII decimal")
    base = int(text)
    if not SEED_BASE_LO <= base < SEED_BASE_HI:
        raise Stop(REFUSED, "the seed base is outside the documented range")
    return base


def check_hex64(text, what: str) -> str:
    if not isinstance(text, str) or not HEX64.fullmatch(text):
        raise Stop(REFUSED, f"the {what} is not 64 lowercase hex characters")
    return text


def commitment_digest(seed_base: int, salt_hex: str) -> str:
    """sec. 4.2: the seed base in ASCII decimal, one ':', the salt as 64 lowercase hex characters, no newline."""
    if not SEED_BASE_LO <= seed_base < SEED_BASE_HI:
        raise Stop(REFUSED, "the seed base is outside the documented range")
    check_hex64(salt_hex, "salt")
    return sha256_bytes(f"{seed_base}:{salt_hex}".encode("ascii"))


def generate(kc: Keychain) -> str:
    """Create all three items. 'exists' if all three are there; a partial set is an ERROR that names the items
    present (never their values) and changes nothing; any failure part-way reports what the Keychain holds."""
    present = [item for item in ITEMS if kc.exists(item)]
    if len(present) == len(ITEMS):
        return "exists"
    if present:
        raise Stop(ERROR, f"partial Keychain set: present {', '.join(present)}; missing "
                          f"{', '.join(i for i in ITEMS if i not in present)}. Nothing changed; the director decides")
    values = {
        "passphrase": secrets.token_hex(32),
        "seed-base": str(SEED_BASE_LO + secrets.randbelow(SEED_BASE_HI - SEED_BASE_LO)),
        "salt": secrets.token_hex(32),
    }
    for item in ITEMS:
        try:
            kc.add(item, values[item])
        except BaseException as e:
            try:
                now = [i for i in ITEMS if kc.exists(i)]
                state = f"the Keychain now holds {len(now)} of {len(ITEMS)} items ({', '.join(now) or 'none'})"
            except BaseException:
                state = "the Keychain's state could not be determined"
            raise Stop(ERROR, f"generate stopped at {item} ({type(e).__name__}: {e}); {state}")
    return "created"


# ----------------------------------------------------------------------------------------------------------
# gpg, with the passphrase on fd 3 through an internal pipe (sec. 4.2 point 2)
# ----------------------------------------------------------------------------------------------------------

def _fd_is_open(fd: int) -> bool:
    try:
        os.fstat(fd)
        return True
    except OSError:
        return False


def gpg_run(argv, passphrase: str, payload: bytes, gpg: str = "gpg") -> bytes:
    """Run gpg with the pinned argv in a fresh, empty, private GNUPGHOME (no ambient gpg.conf can change where the
    plaintext goes or how an integrity failure exits), passing only fds 0-2 and 3. Returns stdout only after gpg
    exited 0; its stderr is redacted of the passphrase before it goes into any message."""
    argv = [gpg, *argv[1:]]
    home = tempfile.mkdtemp(prefix="cfxg", dir="/tmp" if os.path.isdir("/tmp") else None)
    os.chmod(home, 0o700)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GPG") and k != "GNUPGHOME"}
    env["GNUPGHOME"] = home
    r0, w = os.pipe()
    try:
        write_all(w, passphrase.encode("ascii") + b"\n")
    finally:
        os.close(w)
    # Move the read end above stdio (>= 10, close-on-exec), so it can never collide with 0-2 in the child.
    r = fcntl.fcntl(r0, fcntl.F_DUPFD_CLOEXEC, 10)
    os.close(r0)
    temp3 = None
    try:
        if not _fd_is_open(3):
            temp3 = os.dup2(r, 3)                              # 3 is free here: the child inherits it as is
            keep, pre = (3,), None
        else:
            def pre():                                         # 3 is taken here: the child gets the pipe on 3
                os.dup2(r, 3)
                os.close(r)
            keep = (r, 3)
        try:
            p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 close_fds=True, pass_fds=keep, preexec_fn=pre, env=env)
        finally:
            os.close(r)
            if temp3 is not None:
                os.close(3)
        out, err = p.communicate(payload)
    finally:
        subprocess.run(["gpgconf", "--homedir", home, "--kill", "gpg-agent"], capture_output=True, env=env)
        shutil.rmtree(home, ignore_errors=True)
    if p.returncode != 0:
        msg = err.decode(errors="replace").replace(passphrase, "[redacted]").strip()[-300:]
        raise Stop(TERMINAL, f"gpg exited {p.returncode}: {msg}")
    return out


# ----------------------------------------------------------------------------------------------------------
# Checksum lists (PG-SEAL.sha256, P2-FREEZE.sha256)
# ----------------------------------------------------------------------------------------------------------

SUMLINE = re.compile(r"([0-9a-f]{64}) [ *](\S.*)")


def parse_sumfile(data: bytes, what: str) -> dict:
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError:
        raise Stop(TERMINAL, f"{what} is not ASCII")
    entries = {}
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        m = SUMLINE.fullmatch(line)
        if not m:
            raise Stop(TERMINAL, f"{what} line {n} is not '<sha256>  <path>'")
        digest, rel = m.groups()
        parts = rel.split("/")
        if rel.startswith("/") or ".." in parts or "\\" in rel or "" in parts:
            raise Stop(TERMINAL, f"{what} line {n}: path {rel!r} is not a plain relative path")
        if rel in entries:
            raise Stop(TERMINAL, f"{what} line {n}: {rel!r} is listed twice")
        entries[rel] = digest
    if not entries:
        raise Stop(TERMINAL, f"{what} lists no file")
    return entries


# ----------------------------------------------------------------------------------------------------------
# The cluster: hashing on a login node, and the launch
# ----------------------------------------------------------------------------------------------------------

ROOT_MISSING_RC = 97
HASH_END = "covfix-hash-end"

# Run under bash on the login node, one typed line per requested path. The file is opened by redirection (so a
# name like "-" is a file, never stdin). A path is MISSING only when stat says "No such file or directory"; any
# other failure (a permission error on the file or a parent, a directory) is UNREADABLE.
HASH_SCRIPT = ('export LC_ALL=C; while IFS= read -r -d "" f; do '
               'if h=$(sha256sum < "./$f" 2>/dev/null); then printf "%s  %s\\n" "${h%% *}" "$f"; '
               'else e=$(stat -- "./$f" 2>&1 >/dev/null); case "$e" in '
               '*"No such file or directory"*) printf "covfix-missing %s\\n" "$f";; '
               '*) printf "covfix-unreadable %s\\n" "$f";; esac; fi; done; '
               f'echo {HASH_END}')

# Wraps the bound binary inside the allocation: hash it on the compute node, then exec it with stdin untouched.
EXEC_CHECK = ('h=$(sha256sum < "$1") || exit 87; [ "${h%% *}" = "$2" ] || '
              '{ echo "covfix: the bound binary does not hash to its pin" >&2; exit ' + str(EXEC_MISMATCH_RC) + '; }; '
              'b=$1; shift 2; exec "$b" "$@"')


def own_regular_file(path, what: str) -> str:
    if not isinstance(path, str) or not LITERAL_PATH.fullmatch(path) or ".." in path.split("/"):
        raise Stop(ERROR, f"the ssh {what} must be an absolute, literal path")
    try:
        st = os.lstat(path)
    except OSError as e:
        raise Stop(ERROR, f"the ssh {what} {path} cannot be read ({e})")
    if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid():
        raise Stop(ERROR, f"the ssh {what} {path} must be a regular file owned by this user")
    return path


def ssh_setup(cfg, host, real: bool):
    """(argv, environment) for ssh, built entirely by the wrapper from the closed schema: the forced options, then the
    host-key files (this user's ~/.ssh/known_hosts as a literal path, the only trust anchor; no global file), then -l,
    -i and the certificate; the environment is HOME (this user's, from the password database), PATH=/usr/bin:/bin,
    LANG=C, and SSH_AUTH_SOCK only when the config declares an agent. Nothing else the launch environment holds
    reaches ssh."""
    if not isinstance(cfg, dict):
        raise Stop(ERROR, "the role config's ssh must be an object (program, user, identity_file, certificate_file, "
                          "agent)")
    extra = sorted(set(cfg) - SSH_KEYS)
    if extra:
        raise Stop(ERROR, f"the role config's ssh may not hold {extra}")
    if not isinstance(host, str) or not SSH_HOST.fullmatch(host):
        raise Stop(ERROR, "the role config's host must be a plain host name")
    program = cfg.get("program", SSH_PROGRAM)
    if real and program != SSH_PROGRAM:
        raise Stop(ERROR, f"the real items use {SSH_PROGRAM} only")
    if not isinstance(program, str) or not LITERAL_PATH.fullmatch(program):
        raise Stop(ERROR, "the ssh program must be an absolute, literal path")
    user = cfg.get("user")
    if not isinstance(user, str) or not SSH_USER.fullmatch(user):
        raise Stop(ERROR, "the role config's ssh user must be a plain user name")
    known_hosts = os.path.join(home_dir(), ".ssh", "known_hosts")
    if real:
        own_regular_file(known_hosts, "known_hosts file")
    elif not LITERAL_PATH.fullmatch(known_hosts) or ".." in known_hosts.split("/"):
        raise Stop(ERROR, "the ssh known_hosts file must be an absolute, literal path")
    # one user file, named literally: known_hosts2 and /etc/ssh/ssh_known_hosts{,2} are never consulted
    argv = [program, *SSH_FORCED, "-o", f"UserKnownHostsFile={known_hosts}", "-o", "GlobalKnownHostsFile=/dev/null",
            "-l", user, "-i", own_regular_file(cfg.get("identity_file"), "identity_file")]
    if cfg.get("certificate_file") is not None:
        argv += ["-o", f"CertificateFile={own_regular_file(cfg['certificate_file'], 'certificate_file')}"]
    agent = cfg.get("agent", False)
    if not isinstance(agent, bool):
        raise Stop(ERROR, "the role config's ssh agent must be true or false")
    env = base_env()
    if agent:
        sock = os.environ.get("SSH_AUTH_SOCK", "")
        if not LITERAL_PATH.fullmatch(sock):
            raise Stop(REFUSED, "the role config declares an ssh agent, but SSH_AUTH_SOCK is not a literal path")
        env["SSH_AUTH_SOCK"] = sock
    return argv, env


class LaunchResult:
    def __init__(self, rc, delivered: bool, receipt: bool, break_line: bool, echoed: bool):
        self.rc, self.delivered, self.receipt, self.break_line, self.echoed = rc, delivered, receipt, break_line, echoed


class Cluster:
    def __init__(self, ssh, host, real: bool = False):
        self.ssh_argv, self.env = ssh_setup(ssh, host, real)
        self.host = host

    def hash_files(self, root: str, rels):
        """(sha256 per relpath under root, confirmed-absent set, unreadable set), computed on the cluster.
        Anything short of exactly one typed answer per path is the link or the environment: REFUSED."""
        remote = f"cd -- {shlex.quote(root)} || exit {ROOT_MISSING_RC}; bash -c {shlex.quote(HASH_SCRIPT)}"
        r = subprocess.run([*self.ssh_argv, self.host, remote], input=b"".join(x.encode() + b"\0" for x in rels),
                           capture_output=True, env=self.env)
        if r.returncode == ROOT_MISSING_RC:
            raise Stop(REFUSED, f"remote root {root} does not exist; nothing spent")
        lines = r.stdout.decode("ascii", errors="replace").splitlines()
        if r.returncode != 0 or not lines or lines[-1] != HASH_END:
            raise Stop(REFUSED, f"hashing on {self.host} did not complete (rc {r.returncode}); nothing spent")
        got, missing, unreadable, seen = {}, set(), set(), []
        for line in lines[:-1]:
            m = SUMLINE.fullmatch(line)
            if m:
                got[m.group(2)] = m.group(1)
                seen.append(m.group(2))
            elif line.startswith("covfix-missing "):
                missing.add(line[len("covfix-missing "):])
                seen.append(line[len("covfix-missing "):])
            elif line.startswith("covfix-unreadable "):
                unreadable.add(line[len("covfix-unreadable "):])
                seen.append(line[len("covfix-unreadable "):])
            else:
                raise Stop(REFUSED, f"hashing on {self.host}: an unexpected line; nothing spent")
        if sorted(seen) != sorted(rels):
            raise Stop(REFUSED, f"hashing on {self.host}: {len(seen)} answers for {len(rels)} paths; nothing spent")
        return got, missing, unreadable

    def launch(self, command: str, frame: bytearray, attempt: str, redact) -> LaunchResult:
        """Run the task, write the frame unbuffered and zero it, and pass the task's stdout and stderr through,
        redacting any secret. The result says whether the frame was delivered, whether the last stdout line was the
        attempt's receipt or break line, and whether a secret was echoed."""
        p = subprocess.Popen([*self.ssh_argv, self.host, command], env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, bufsize=0)
        state = {"echoed": False, "last": b""}

        def pump(src, dst, track):
            for line in iter(src.readline, b""):
                clean = line
                for s in redact:
                    if s and s in clean:
                        clean = clean.replace(s, b"[redacted]")
                        state["echoed"] = True
                if track and line.strip():
                    state["last"] = line.strip()
                out = dst()
                if hasattr(out, "buffer"):
                    out.buffer.write(clean)
                else:
                    out.write(clean.decode(errors="replace"))
                out.flush()
        threads = [threading.Thread(target=pump, args=(p.stdout, lambda: sys.stdout, True), daemon=True),
                   threading.Thread(target=pump, args=(p.stderr, lambda: sys.stderr, False), daemon=True)]
        for t in threads:
            t.start()
        delivered = False
        try:
            try:
                view = memoryview(frame)
                while view:
                    view = view[p.stdin.write(view):]
                view.release()
                delivered = True
            except BrokenPipeError:
                pass
            finally:
                for i in range(len(frame)):
                    frame[i] = 0
                p.stdin.close()
            rc = p.wait()
            for t in threads:
                t.join()
        except BaseException:
            p.kill()
            p.wait()
            raise
        finally:
            for t in threads:
                t.join(timeout=5)
            p.stdout.close()
            p.stderr.close()
        last = state["last"]
        return LaunchResult(rc, delivered, last == f"covfix-receipt {attempt}".encode(),
                            last == f"covfix-break {attempt}".encode(), state["echoed"])


def launch_command(role: str, rcfg: dict, extra_args: list) -> str:
    """The remote command, built from the structured role config: for every role, pg-connect included, one exclusive
    node and one task (salloc and srun, both --exclusive -N 1 -n 1; salloc named by the role's constant JOB_NAMES
    entry; only account/qos/constraint/time added; the Slurm I/O variables unset), then the compute-side hash check, the bound binary, its args and the wrapper's own
    --covfix-* args. (cov2d, 2026-11-25: pg-connect had no allocation and would have run on the login host.)"""
    if not isinstance(rcfg, dict):
        raise Stop(ERROR, f"role config for {role} must be an object")
    binary, want = rcfg.get("binary"), rcfg.get("binary_sha256")
    if not isinstance(binary, str) or not binary.startswith("/"):
        raise Stop(ERROR, f"role config for {role}: the binary must be an absolute path")
    if not isinstance(want, str) or not HEX64.fullmatch(want):
        raise Stop(ERROR, f"role config for {role}: binary_sha256 must be 64 lowercase hex")
    args = str_list(rcfg.get("args", []), f"{role} args")
    if any(a.startswith("--covfix-") for a in args):
        raise Stop(ERROR, f"role config for {role}: --covfix-* arguments are the wrapper's own")
    slurm = rcfg.get("slurm")
    if not isinstance(slurm, dict):
        raise Stop(ERROR, f"{role} needs a slurm block (salloc, srun, account, qos, constraint, time)")
    salloc, srun = slurm.get("salloc", "salloc"), slurm.get("srun", "srun")
    if not all(isinstance(x, str) and x for x in (salloc, srun)) or \
            os.path.basename(salloc) != "salloc" or os.path.basename(srun) != "srun":
        raise Stop(ERROR, f"{role}: salloc and srun must name salloc and srun")
    opts = []
    for k, v in slurm.items():
        if k in ("salloc", "srun"):
            continue
        if k not in SLURM_KEYS or not isinstance(v, str) or not SLURM_VALUE.fullmatch(v):
            raise Stop(ERROR, f"{role}: slurm option {k!r} is not allowed or not plain")
        opts += [SLURM_KEYS[k], v]
    unset = [x for v in SLURM_IO_ENV for x in ("-u", v)]
    launcher = ["env", *unset, salloc, "--exclusive", "-N", "1", "-n", "1", "-J", JOB_NAMES[role], *opts,
                srun, "--exclusive", "-N", "1", "-n", "1"]
    return shlex.join([*launcher, "bash", "-c", EXEC_CHECK, "covfix-exec", binary, want, *args, *extra_args])


# ----------------------------------------------------------------------------------------------------------
# ST4's consumption record
# ----------------------------------------------------------------------------------------------------------

class Record:
    """Append-only, hash-chained JSON lines in a mode-700 directory, plus O_EXCL markers.

    Markers: MARK-attempt-<key12>-<role> is created, fsynced, BEFORE a spend is appended, so a crash or failure at
    any later point leaves the role blocked; MARK-uncertain-<key12>-<role> records a lock or write failure;
    MARK-break-<key12>-seal is created before a break is recorded, so a break that cannot be appended still stops
    every role of the seal. Markers are never removed; each is absorbed into the chain at the next locked write."""

    def __init__(self, directory: str):
        self.dir = os.path.realpath(os.path.expanduser(directory))
        self.path = os.path.join(self.dir, RECORD_NAME)
        self._lock_fd = None
        self.pinned = None          # under the lock: the record bytes read once, right after the lock was taken

    def ensure_dir(self) -> None:
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir, mode=0o700)
        st = os.stat(self.dir)
        if stat.S_IMODE(st.st_mode) != 0o700 or st.st_uid != os.getuid():
            raise Stop(REFUSED, f"{self.dir} must be mode 700 and owned by this user")

    def raw(self) -> bytes:
        """The record. Under the lock, the snapshot taken when the lock was acquired (and extended by our own
        appends), so every check in one locked transaction sees the same bytes."""
        return self.pinned if self.pinned is not None else self._read_file()

    def _read_file(self) -> bytes:
        try:
            with open(self.path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return b""

    @staticmethod
    def parse(data: bytes, what: str = "the consumption record") -> list:
        if data and not data.endswith(b"\n"):
            raise Stop(TERMINAL, f"{what} ends in a partial line (an uncertain write)")
        lines, prev = [], GENESIS
        for n, raw in enumerate(data.splitlines()):
            try:
                ev = json.loads(raw)
            except ValueError:
                raise Stop(TERMINAL, f"{what} line {n + 1} is not JSON")
            if not isinstance(ev, dict) or ev.get("seq") != n or ev.get("prev") != prev \
                    or ev.get("event") not in EVENTS or not HEX64.fullmatch(str(ev.get("key", ""))):
                raise Stop(TERMINAL, f"{what} line {n + 1} breaks the chain or the schema")
            lines.append(ev)
            prev = sha256_bytes(raw)
        return lines

    def lines(self) -> list:
        return self.parse(self.raw())

    def marker(self, kind: str, key: str, role: str) -> str:
        assert kind in MARK_KINDS
        return os.path.join(self.dir, f"MARK-{kind}-{key[:12]}-{role}")

    def mark(self, kind: str, key: str, role: str) -> bool:
        """Create a marker durably. True if this call created it, False if it already existed."""
        try:
            fd = os.open(self.marker(kind, key, role), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            return False
        try:
            write_all(fd, f"{kind} {key} {role} {utc_now()}\n".encode())
            os.fsync(fd)
        finally:
            os.close(fd)
        fsync_dir(self.dir)
        return True

    def markers(self) -> list:
        out = []
        for name in sorted(os.listdir(self.dir)):
            if name.startswith("MARK-"):
                with open(os.path.join(self.dir, name)) as f:
                    fields = f.read().split()
                if len(fields) < 3 or fields[0] not in MARK_KINDS or not HEX64.fullmatch(fields[1]):
                    raise Stop(TERMINAL, f"marker {name} is unreadable")
                out.append((fields[0], fields[1], fields[2]))
        return out

    def lock(self) -> None:
        fd = os.open(os.path.join(self.dir, LOCK_NAME), os.O_CREAT | os.O_RDWR, 0o600)
        deadline = time.monotonic() + LOCK_TIMEOUT_S
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self._lock_fd = fd
                self.pinned = self._read_file()
                return
            except OSError as e:
                if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN) or time.monotonic() > deadline:
                    os.close(fd)
                    raise
                time.sleep(0.2)

    def unlock(self) -> None:
        if self._lock_fd is not None:
            fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
            os.close(self._lock_fd)
            self._lock_fd = None
        self.pinned = None

    def append(self, event: dict, expected: bytes | None = None) -> bytes:
        """Append one chained line and fsync the file and the directory. Caller holds the lock. With `expected`, the
        record must still be exactly the bytes the caller validated (a restore that ignored the lock fails here)."""
        assert self._lock_fd is not None, "append without the lock"
        data = self.pinned
        actual = self._read_file()
        if actual != data or (expected is not None and actual != expected):
            raise OSError("the record changed after it was validated under the lock")
        lines = self.parse(data)
        prev = sha256_bytes(data.splitlines()[-1]) if lines else GENESIS
        ev = {"seq": len(lines), "prev": prev, "utc": utc_now(), **event}
        line = json.dumps(ev, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        fd = os.open(self.path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        try:
            write_all(fd, line)
            os.fsync(fd)
        finally:
            os.close(fd)
        fsync_dir(self.dir)
        # The bytes published are the validated snapshot plus this line, computed here: never a reread of the file,
        # which a restore after the write could have replaced.
        self.pinned = data + line
        return self.pinned

    def absorb_markers(self, exclude=None) -> None:
        """Under the lock: every marker the chain does not yet reflect becomes a record line (except `exclude`, the
        marker whose own event the caller is about to append)."""
        events = self.lines()
        for kind, key, role in self.markers():
            if (kind, key, role) == exclude:
                continue
            if kind == "break":
                if not any(e["key"] == key and e["event"] == "break" for e in events):
                    self.append({"event": "break", "key": key, "role": role, "detail": "from marker"})
            elif not any(e["key"] == key and e["role"] == role and e["event"] not in NON_CONSUMING
                         for e in events):
                self.append({"event": "uncertain", "key": key, "role": role, "detail": f"from {kind} marker"})
            events = self.lines()


def blocked(events, markers, key: str, role: str):
    """Why (key, role) may not be spent, or None. Any line or marker for the pair blocks it; a break or a reveal
    (line or marker) blocks every role of the seal; a reveal also blocks pg-connect for its commitment."""
    for e in events:
        if e["event"] in NON_CONSUMING:
            continue
        if e["key"] == key and (e["role"] == role or e["event"] in SEAL_WIDE):
            return f"record line seq {e.get('seq')}: {e['event']} {e['role']}"
        if role == "pg-connect" and e["event"] == "reveal" and e.get("commitment") == key:
            return f"record line seq {e.get('seq')}: the commitment was revealed"
    for kind, k, r in markers:
        if k == key and (r == role or kind == "break"):
            return f"{kind} marker for {r}"
    return None


def bound_freeze(events, key: str):
    for e in events:
        if e["key"] == key and e.get("freeze"):
            return e["freeze"]
    return None


def unresolved_freeze_refusals(events, key: str) -> int:
    """Freeze-mismatch refusals on the seal since its last director ruling."""
    last = max((e["seq"] for e in events if e["key"] == key and e["event"] == "ruling"), default=-1)
    return sum(1 for e in events if e["key"] == key and e["event"] == "freeze-mismatch-refused" and e["seq"] > last)


def confirmed_end(pushed, key: str, role: str, attempts) -> list:
    """The PUSHED outcome lines that confirm the end of one of these attempts of the role: `completed` or `break`
    carrying the attempt id of the spend. A wrapper preflight break (no attempt) or another invocation's line is not
    the end of this task."""
    attempts = {a for a in attempts if a}
    return [e for e in pushed if e["key"] == key and e["role"] == role and e["event"] in CONFIRMED_END
            and e.get("attempt") in attempts]


def spent_attempts(events, key: str, role: str) -> list:
    return [e.get("attempt") for e in events if e["key"] == key and e["role"] == role and e["event"] == "spent"]


def in_flight(events, key: str, pushed=None) -> list:
    """PV roles of the seal that were spent (locally) and whose spend has no confirmed end in the PUSHED record: a
    local-only outcome whose publication failed, a `terminal` outcome (a dropped link, a crash: the task's exit is not
    known), or a break that is not this attempt's own, is still in flight until a director ruling."""
    pushed = events if pushed is None else pushed
    out = []
    for role in ("pv-writer", "pv-readout"):
        attempts = spent_attempts(events, key, role)
        if attempts and any(not confirmed_end(pushed, key, role, [a]) for a in attempts):
            out.append(role)
    return out


# ----------------------------------------------------------------------------------------------------------
# The mirror: one path, committed and pushed on a dedicated branch of a git worktree
# ----------------------------------------------------------------------------------------------------------

class Mirror:
    """The record's mirror. Guards against a restored or rewound history:
    - every version ever published stays reachable from refs/covfix/published/<ledger id>/<seq>;
    - the remote tip is fetched to an immutable commit id and must descend from the last-seen one (else rewound,
      terminal); a vanished remote branch after any publication is terminal;
    - every version in any commit reachable from any ref (full history, no simplification) is scanned for lines
      the local record lacks.
    The remote should also forbid force pushes and deletion of the branch (a host setting, outside this tool)."""

    def __init__(self, cfg: dict, ledger_id: str):
        if not isinstance(cfg, dict) or not all(isinstance(cfg.get(k), str) and cfg.get(k)
                                                 for k in ("worktree", "path", "remote", "branch")):
            raise Stop(ERROR, "the mirror config needs string worktree, path, remote and branch")
        self.wt = os.path.expanduser(cfg["worktree"])
        self.rel, self.remote, self.branch = cfg["path"], cfg["remote"], cfg["branch"]
        self.ledger_id = ledger_id
        if not isinstance(cfg.get("run_hooks", False), bool):
            raise Stop(ERROR, "the mirror config's run_hooks must be true or false")
        self.hooks = [] if cfg.get("run_hooks", False) else ["-c", "core.hooksPath=/dev/null"]
        self.ident = ["-c", "user.name=director", "-c", "user.email=director@minerva-omnifold.invalid"]

    def git(self, *args, check=True, input=None):
        r = subprocess.run(["git", "-C", self.wt, *args], capture_output=True, input=input)
        if check and r.returncode != 0:
            raise Stop(REFUSED, f"git {' '.join(a for a in args[:3] if not a.startswith('core.'))} failed: "
                                f"{r.stderr.decode(errors='replace').strip()[-300:]}")
        return r

    @property
    def seen(self) -> str:
        return f"refs/covfix/seen/{self.ledger_id}"

    @property
    def published(self) -> str:
        return f"refs/covfix/published/{self.ledger_id}/"

    def remote_url(self) -> str:
        return self.git("remote", "get-url", self.remote).stdout.decode().strip()

    def preflight(self) -> None:
        if self.git("rev-parse", "--is-shallow-repository").stdout.decode().strip() != "false":
            raise Stop(REFUSED, "the mirror worktree is a shallow clone; its history cannot be scanned")
        head = self.git("symbolic-ref", "--short", "HEAD").stdout.decode().strip()
        if head != self.branch:
            raise Stop(REFUSED, f"mirror worktree is on {head!r}, not {self.branch!r}")
        if self.git("status", "--porcelain", "--", self.rel).stdout.strip():
            raise Stop(REFUSED, f"mirror path {self.rel} has uncommitted or staged changes")

    def blob_at(self, rev: str):
        """The record's bytes at a commit; None if the path is absent there; REFUSED if it is present but unreadable."""
        if not self.git("ls-tree", rev, "--", self.rel).stdout.strip():
            return None
        return self.git("cat-file", "blob", f"{rev}:{self.rel}").stdout

    def fetch(self, local_nonempty: bool) -> bytes | None:
        """Fetch the branch's tip to a commit id; return its mirrored record bytes, or None before the first publish."""
        seen = self.git("rev-parse", "-q", "--verify", self.seen, check=False)
        old = seen.stdout.decode().strip() if seen.returncode == 0 else None
        ls = self.git("ls-remote", "--heads", self.remote, self.branch).stdout.decode().split()
        if not ls:
            published = self.git("for-each-ref", "--count=1", self.published).stdout.strip()
            if old or published or local_nonempty:
                raise Stop(TERMINAL, f"the remote mirror branch {self.branch} is gone after it was published")
            return None
        incoming = f"refs/covfix/incoming/{self.ledger_id}"
        r = self.git(*self.hooks, "fetch", "-q", self.remote, f"+refs/heads/{self.branch}:{incoming}", check=False)
        if r.returncode != 0:
            raise Stop(REFUSED, f"git fetch of the mirror failed: {r.stderr.decode(errors='replace').strip()[-300:]}")
        tip = self.git("rev-parse", "--verify", f"{incoming}^{{commit}}").stdout.decode().strip()
        if old and self.git("merge-base", "--is-ancestor", old, tip, check=False).returncode != 0:
            raise Stop(TERMINAL, f"the remote mirror branch {self.branch} was rewound (what was seen is not an "
                                 "ancestor of its tip)")
        self.git("update-ref", self.seen, tip, *([old] if old else []))
        return self.blob_at(tip)

    def history(self) -> list:
        """Every version of the mirrored record in any commit reachable from any ref, merges included."""
        revs = self.git("rev-list", "--all", "--full-history", "--", self.rel).stdout.decode().split()
        out = []
        for rev in revs:
            blob = self.blob_at(rev)
            if blob is not None:
                out.append((rev, blob))
        return out

    def publish(self, data: bytes, message: str, seq: int) -> None:
        """Commit the record bytes, push, refetch, require the remote bytes to equal them, keep a published ref."""
        dest = os.path.join(self.wt, self.rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        self.git("add", "--", self.rel)
        self.git(*self.hooks, *self.ident, "commit", "-q", "-m", message, "--", self.rel)
        self.git(*self.hooks, "push", "-q", self.remote, f"HEAD:refs/heads/{self.branch}")
        if self.fetch(True) != data:
            raise Stop(TERMINAL, "the pushed mirror's record does not equal the local record")
        self.git("update-ref", f"{self.published}{seq:06d}", "HEAD", "")


# ----------------------------------------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------------------------------------

def load_config(path: str, pinned: str) -> dict:
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as e:
        raise Stop(ERROR, f"cannot read the role config: {e}")
    if sha256_bytes(data) != check_hex64(pinned, "pinned config sha256"):
        raise Stop(REFUSED, "the role config's sha256 is not the pinned one")
    try:
        cfg = json.loads(data)
    except ValueError:
        raise Stop(ERROR, "the role config is not JSON")
    if not isinstance(cfg, dict):
        raise Stop(ERROR, "the role config must be a JSON object")
    for k in ("record_dir", "keychain_prefix", "ssh", "host", "mirror", "roles", "binding"):
        if k not in cfg:
            raise Stop(ERROR, f"role config lacks {k!r}")
    if not isinstance(cfg["binding"], dict) or not isinstance(cfg["roles"], dict) \
            or not isinstance(cfg["record_dir"], str):
        raise Stop(ERROR, "role config: binding and roles must be objects, record_dir a string")
    return cfg


class Context:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        prefix = check_prefix(cfg["keychain_prefix"])
        self.record = Record(cfg["record_dir"])
        if prefix == REAL_PREFIX:
            if self.record.dir != os.path.realpath(os.path.expanduser(REAL_RECORD_DIR)):
                raise Stop(ERROR, f"the real items use the canonical ledger {REAL_RECORD_DIR} only")
            if "security" in cfg or "keychain" in cfg:
                raise Stop(ERROR, "the real items take no security or keychain override")
            if not isinstance(cfg.get("mirror"), dict) or cfg["mirror"].get("branch") != REAL_LEDGER_BRANCH:
                raise Stop(ERROR, f"the real ledger's mirror branch is {REAL_LEDGER_BRANCH} only")
        ledger_id = sha256_bytes(self.record.dir.encode())[:16]
        self.mirror = Mirror(cfg["mirror"], ledger_id)
        self.cluster = Cluster(cfg["ssh"], cfg["host"], prefix == REAL_PREFIX)
        self._kc = None
        self._remote_events = []

    @property
    def kc(self) -> Keychain:
        if self._kc is None:
            self._kc = Keychain(self.cfg["keychain_prefix"], self.cfg.get("security", SECURITY),
                                self.cfg.get("keychain"))
        return self._kc

    def pinned(self, name: str, given) -> str:
        """A campaign digest from the pinned binding; the command-line value must equal it."""
        want = check_hex64(self.cfg["binding"].get(name), f"binding's {name}")
        if given != want:
            raise Stop(REFUSED, f"--{name.replace('_', '-')} is not the binding's {name}")
        return want

    def check_ledger(self) -> None:
        """The mirror identity (remote URL, branch, path) is fixed at the ledger's first use."""
        ident = {"remote_url": self.mirror.remote_url(), "branch": self.mirror.branch, "path": self.mirror.rel}
        path = os.path.join(self.record.dir, LEDGER_NAME)
        try:
            with open(path) as f:
                have = json.load(f)
        except FileNotFoundError:
            if self.record.raw() or self.record.markers():
                raise Stop(TERMINAL, f"the ledger {self.record.dir} has records but no {LEDGER_NAME}")
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            try:
                write_all(fd, (json.dumps(ident, sort_keys=True) + "\n").encode())
                os.fsync(fd)
            finally:
                os.close(fd)
            fsync_dir(self.record.dir)
            return
        except ValueError:
            raise Stop(TERMINAL, f"{LEDGER_NAME} is unreadable")
        if have != ident:
            raise Stop(REFUSED, f"this config's mirror is not the ledger's ({LEDGER_NAME}: {have})")

    def check_mirror(self) -> None:
        """The pushed mirror must be a prefix of the local record, and no version in its history may hold a line
        the local record lacks (a restored older copy)."""
        self.mirror.preflight()
        self.check_ledger()
        local = self.record.raw()
        remote = self.mirror.fetch(bool(local))
        if remote is not None and not local.startswith(remote):
            raise Stop(TERMINAL, "the local record is not an extension of the pushed mirror (restored copy?)")
        self._remote_events = Record.parse(remote or b"", "the pushed mirror's record")
        local_lines = set(local.splitlines())
        for rev, blob in self.mirror.history():
            missing = [x for x in blob.splitlines() if x not in local_lines]
            if missing:
                raise Stop(TERMINAL, f"mirror commit {rev[:12]} holds {len(missing)} line(s) the local record "
                                     "lacks (restored copy?)")

    def local_checks(self, key: str, role: str) -> None:
        """Known local terminal states first, so no transport or mirror refusal can mask them."""
        why = blocked(self.record.lines(), self.record.markers(), key, role)
        if why:
            raise Consumed(f"{role} for {key[:12]} is already consumed ({why})")

    def spend_checks(self, key: str, role: str, freeze) -> None:
        """Every reason a spend of (key, role) is not allowed, read from the current record, markers and mirror."""
        events, markers = self.record.lines(), self.record.markers()
        why = blocked(events, markers, key, role)
        if why:
            raise Consumed(f"{role} for {key[:12]} is already consumed ({why})")
        if freeze:
            n = unresolved_freeze_refusals(events, key)
            if n >= FREEZE_MISMATCH_LIMIT:
                raise Stop(REFUSED, f"seal {key[:12]} has {n} unresolved freeze-mismatch refusals; every role waits "
                                    "for a director ruling (run --freeze-mismatch-resolved <ruling id>)")
            bound = bound_freeze(events, key)
            if bound and bound != freeze:
                raise FreezeConflict(key, freeze, bound)
        if role == "pv-readout":
            pushed = any(e["key"] == key and e["role"] == "pv-writer" and e["event"] == "completed"
                         for e in self._remote_events)
            if not pushed:
                raise Stop(REFUSED, f"pv-readout needs a completed pv-writer in the pushed record for seal {key[:12]}")

    def commit_event(self, event: dict, message: str, absorb_exclude=None, soft: bool = False, gate=None) -> None:
        """Lock; check the mirror against the local record; absorb markers; for a spend, check every spend
        condition and create the attempt marker; then append, fsync, commit, push, verify. Any failure after the
        attempt marker (or any failure writing a non-spend event) leaves the role marked, and is terminal."""
        key, role = event["key"], event["role"]
        spend = event["event"] == "spent"
        if soft:
            # A non-consuming line (a refused freeze conflict, a ruling): any failure refuses, marks nothing.
            assert event["event"] in NON_CONSUMING
            try:
                self.record.lock()
            except OSError as e:
                raise Stop(REFUSED, f"cannot take the record lock to record {event['event']} ({e})")
            try:
                self.check_mirror()
                data = self.record.append(event)
                self.mirror.publish(data, message, len(data.splitlines()) - 1)
            except Stop as e:
                raise Stop(REFUSED if e.code != TERMINAL else TERMINAL, f"recording {event['event']}: {e}")
            except Exception as e:
                raise Stop(REFUSED, f"recording {event['event']} failed ({type(e).__name__}: {e})")
            finally:
                self.record.unlock()
            return
        try:
            self.record.lock()
        except BaseException as e:
            try:
                self.record.mark("uncertain", key, role)
            except BaseException as m:
                raise Stop(TERMINAL, f"cannot take the record lock ({e}) nor mark {role} uncertain ({m}); "
                                     "the director must treat it as blocked")
            raise Stop(TERMINAL, f"cannot take the record lock ({type(e).__name__}: {e}); {role} is now blocked")
        try:
            try:
                self.check_mirror()
                self.record.absorb_markers(absorb_exclude)
                if spend:
                    self.spend_checks(key, role, event.get("freeze"))
                if gate is not None:
                    gate()                      # an eligibility rule re-checked on the fresh, locked state
                validated = self.record.raw()
            except GateRefusal:
                raise
            except BaseException:
                if spend:
                    raise                       # nothing spent: the refusal stands as raised
                self.record.mark("uncertain", key, role)
                raise
            if spend:
                try:
                    created = self.record.mark("attempt", key, role)
                except OSError as e:
                    raise Stop(REFUSED, f"cannot write the attempt marker ({e}); nothing spent")
                if not created:
                    raise Consumed(f"{role} for {key[:12]} has an attempt marker already")
            try:
                data = self.record.append(event, validated)
                self.mirror.publish(data, message, len(data.splitlines()) - 1)
            except BaseException as e:
                self.record.mark("uncertain", key, role)
                raise Stop(TERMINAL, f"uncertain {event['event']} ({type(e).__name__}: {e}); "
                                     f"{role} for {key[:12]} is blocked") from e
        finally:
            self.record.unlock()


# ----------------------------------------------------------------------------------------------------------
# run
# ----------------------------------------------------------------------------------------------------------

def read_list(ctx: Context, sumfile: str, digest: str, what: str, key: str, role: str) -> dict:
    """The local checksum list: readable, on the binding, well formed (else a break). No transport involved."""
    try:
        with open(os.path.expanduser(sumfile), "rb") as f:
            data = f.read()
    except OSError as e:
        raise Stop(REFUSED, f"cannot read the local {what} ({e}); nothing spent")
    if sha256_bytes(data) != digest:
        break_seal(ctx, key, role, f"{what} file does not hash to the pinned digest")
    try:
        entries = parse_sumfile(data, what)
    except Stop as e:
        break_seal(ctx, key, role, str(e))
    if what == "PG-SEAL.sha256" and MANIFEST_CIPHERTEXT not in entries:
        break_seal(ctx, key, role, f"PG-SEAL.sha256 does not list {MANIFEST_CIPHERTEXT}")
    return entries


def verify_remote(ctx: Context, want: dict, root: str, what: str, key: str, role: str) -> None:
    got, missing, unreadable = ctx.cluster.hash_files(root, list(want))
    altered = sorted(rel for rel, d in want.items() if rel in got and got[rel] != d)
    if altered:
        break_seal(ctx, key, role, f"{what}: {len(altered)} altered of {len(want)} files, first {altered[0]}")
    if unreadable:
        raise Stop(REFUSED, f"{what}: {len(unreadable)} unreadable path(s) on the cluster; nothing spent")
    if missing and len(missing) == len(want):
        raise Stop(REFUSED, f"{what}: none of the {len(want)} files exists under {root} (wrong or unmounted "
                            "storage?); nothing spent")
    if missing:
        break_seal(ctx, key, role, f"{what}: {len(missing)} missing of {len(want)} files, first {sorted(missing)[0]}")


def break_seal(ctx: Context, key: str, role: str, detail: str):
    """A confirmed break: the seal-wide marker first (durable even if the record cannot be written), then the line."""
    try:
        ctx.record.mark("break", key, "seal")
    except BaseException as e:
        detail += f"; the break marker could not be written ({e})"
    try:
        ctx.commit_event({"event": "break", "key": key, "role": role, "detail": detail},
                         f"[record] covfix: BREAK {key[:12]} ({role})", absorb_exclude=("break", key, "seal"))
    except Stop as e:
        detail += f"; and recording the break failed: {e}"
    raise Stop(TERMINAL, f"BREAK: {detail}")


def record_freeze_conflict(ctx: Context, conflict: FreezeConflict, role: str):
    """Director, 2026-11-23: refuse a freeze conflict and spend nothing, but append it (presented and bound digests),
    committed and pushed, so the attempt is visible; it is not a break (a configuration mistake must not burn a
    validation that is spent once)."""
    try:
        ctx.commit_event({"event": "freeze-mismatch-refused", "key": conflict.key, "role": role,
                          "presented": conflict.presented, "bound": conflict.bound},
                         f"[record] covfix: freeze mismatch refused {role} {conflict.key[:12]}", soft=True)
    except Stop as e:
        raise Stop(REFUSED, f"{conflict}; and recording the refusal failed: {e}")
    raise Stop(REFUSED, f"{conflict}; refused and recorded (no spend)")


def record_ruling(ctx: Context, key: str, ruling: str, role: str) -> None:
    n = unresolved_freeze_refusals(ctx.record.lines(), key)
    if n < FREEZE_MISMATCH_LIMIT:
        raise Stop(REFUSED, f"--freeze-mismatch-resolved given, but seal {key[:12]} has {n} unresolved refusals "
                            f"(fewer than {FREEZE_MISMATCH_LIMIT}); nothing to resolve")
    ctx.commit_event({"event": "ruling", "key": key, "role": "ruling", "detail": f"{ruling} clears {n} "
                      f"freeze-mismatch refusals (for {role})"},
                     f"[record] covfix: ruling {ruling} on {key[:12]}", soft=True)


def run_role(ctx: Context, role: str, seal_digest, freeze_digest, commitment, freeze_ruling=None) -> int:
    kind, frame_has_seed = ROLES[role]
    rcfg = ctx.cfg["roles"].get(role)
    if rcfg is None:
        raise Stop(ERROR, f"the role config has no entry for {role}")
    attempt = secrets.token_hex(16)
    if kind == "seal":
        for k in ("seal_file", "seal_root", "freeze_file", "freeze_root"):
            if not isinstance(ctx.cfg.get(k), str):
                raise Stop(ERROR, f"role config lacks {k!r}")
        extra = ["--covfix-attempt", attempt, "--covfix-seal-root", ctx.cfg["seal_root"],
                 "--covfix-freeze-root", ctx.cfg["freeze_root"]]
    else:
        extra = ["--covfix-attempt", attempt]
    command = launch_command(role, rcfg, extra)
    ctx.record.ensure_dir()
    if kind == "seal":
        key = ctx.pinned("seal_digest", seal_digest)
        freeze = ctx.pinned("freeze_digest", freeze_digest)
    else:
        key = ctx.pinned("commitment", commitment)
        freeze = None

    # 1. Local terminal states, then the mirror, then every spend condition. (Repeated under the lock.)
    ctx.local_checks(key, role)
    ctx.check_mirror()
    freeze_ruling = check_stop_id(freeze_ruling, "--freeze-mismatch-resolved")
    if freeze_ruling:
        if kind != "seal":
            raise Stop(ERROR, "--freeze-mismatch-resolved applies to the PV roles only")
        record_ruling(ctx, key, freeze_ruling, role)
    try:
        ctx.spend_checks(key, role, freeze)
    except FreezeConflict as conflict:
        record_freeze_conflict(ctx, conflict, role)

    # 2. The secrets, read and checked before the spend so a Keychain failure burns nothing.
    passphrase = check_hex64(ctx.kc.read("passphrase"), "passphrase")
    frame = bytearray(passphrase.encode("ascii") + b"\n")
    redact = [passphrase.encode("ascii")]
    if frame_has_seed:
        seed_base = parse_seed_base(ctx.kc.read("seed-base"))
        if commitment_digest(seed_base, check_hex64(ctx.kc.read("salt"), "salt")) != key:
            raise Stop(REFUSED, "the Keychain seed base and salt do not reproduce the published commitment")
        frame += str(seed_base).encode("ascii") + b"\n"
        redact.append(str(seed_base).encode("ascii"))

    # 3. The local lists (a break needs no transport), then the bound binary, the seal and the freeze on the cluster.
    if kind == "seal":
        seal_want = read_list(ctx, ctx.cfg["seal_file"], key, "PG-SEAL.sha256", key, role)
        freeze_want = read_list(ctx, ctx.cfg["freeze_file"], freeze, "P2-FREEZE.sha256", key, role)
    binary, want_bin = rcfg["binary"], rcfg["binary_sha256"]
    got_bin, _, _ = ctx.cluster.hash_files(os.path.dirname(binary), [os.path.basename(binary)])
    if got_bin.get(os.path.basename(binary)) != want_bin:
        raise Stop(REFUSED, f"the bound binary {binary} does not hash to the pinned sha256; nothing spent")
    if kind == "seal":
        verify_remote(ctx, seal_want, ctx.cfg["seal_root"], "PG-SEAL.sha256", key, role)
        verify_remote(ctx, freeze_want, ctx.cfg["freeze_root"], "P2-FREEZE.sha256", key, role)

    # 4. The spend: durable (attempt marker, fsync, commit, push, remote record verified) before any plaintext.
    spent = {"event": "spent", "key": key, "role": role, "binary_sha256": want_bin, "attempt": attempt}
    if freeze:
        spent["freeze"] = freeze
    try:
        ctx.commit_event(spent, f"[record] covfix: spent {role} {key[:12]}")
    except FreezeConflict as conflict:            # bound by a concurrent first spend after the pre-check
        record_freeze_conflict(ctx, conflict, role)

    # 5. A stop recorded while the spend was publishing wins over the launch.
    stops = [e for e in ctx.record.lines() if e["event"] in SEAL_WIDE]
    markers = ctx.record.markers()
    why = blocked(stops, markers, key, "-") or \
        (kind == "commitment" and blocked(stops, [], key, "pg-connect")) or \
        next((f"an uncertain marker for {role}" for k, kk, r in markers
              if k == "uncertain" and kk == key and r == role), None)
    if why:
        outcome, detail, res = "terminal", f"stopped before launch ({why})", None
    else:
        # 6. The launch. A crash, a dropped link, an undelivered frame or a missing receipt is terminal; no retry.
        try:
            res = ctx.cluster.launch(command, frame, attempt, redact)
        except BaseException as e:
            res, outcome, detail = None, "terminal", f"interrupted ({type(e).__name__})"
        if res is not None:
            echo = "; the task echoed a secret (redacted here)" if res.echoed else ""
            if res.rc == BREAK_RC and res.break_line and kind == "seal":
                outcome, detail = "break", f"the bound {role} reported a confirmed integrity break{echo}"
                try:
                    ctx.record.mark("break", key, "seal")
                except BaseException as e:
                    detail += f"; the break marker could not be written ({e})"
            elif res.echoed:
                outcome, detail = "terminal", f"rc {res.rc}{echo}"
            elif res.rc == 0 and res.delivered and res.receipt:
                outcome, detail = "completed", "rc 0, receipt"
            else:
                outcome, detail = "terminal", (f"rc {res.rc}" + ("" if res.delivered else ", frame not delivered")
                                               + ("" if res.receipt else ", no receipt"))
    for i in range(len(frame)):
        frame[i] = 0
    try:
        ctx.commit_event({"event": outcome, "key": key, "role": role, "detail": detail, "attempt": attempt},
                         f"[record] covfix: {outcome} {role} {key[:12]}",
                         absorb_exclude=("break", key, "seal") if outcome == "break" else None)
    except Stop as e:
        print(f"covfix: {role} {outcome} ({detail}), but its outcome line was not mirrored: {e}", file=sys.stderr)
        return TERMINAL
    print(f"covfix: {role} {outcome} ({detail})")
    return OK if outcome == "completed" else TERMINAL


# ----------------------------------------------------------------------------------------------------------
# reveal
# ----------------------------------------------------------------------------------------------------------

def check_stop_id(text, flag: str) -> str:
    if text is None:
        return None
    t = text.strip()
    if not STOP_ID.fullmatch(t) or SECRET_LIKE.search(t):
        raise Stop(REFUSED, f"{flag} must be a stop or ruling identifier (a letter, then letters, digits, . _ -; "
                            "no long hex or digit runs)")
    return t


def reveal(ctx: Context, seal_digest, commitment, after_stop, inflight_resolved) -> int:
    ctx.record.ensure_dir()
    key = ctx.pinned("seal_digest", seal_digest)
    commitment = ctx.pinned("commitment", commitment)
    after_stop = check_stop_id(after_stop, "--after-stop")
    inflight_resolved = check_stop_id(inflight_resolved, "--inflight-resolved")
    def gate():
        """Reveal's eligibility, from the current record and the pushed one; run before and again under the lock."""
        done = confirmed_end(ctx._remote_events, key, "pv-readout",
                             spent_attempts(ctx._remote_events, key, "pv-readout"))
        if not done and not after_stop:
            raise GateRefusal("PV's readout has no confirmed end (completed or break) in the pushed record; reveal "
                              "needs --after-stop <stop id>")
        busy = in_flight(ctx.record.lines(), key, ctx._remote_events)
        if busy and not inflight_resolved:
            raise GateRefusal(f"{', '.join(busy)} spent with no outcome in the pushed record (in flight?); reveal "
                              "needs --inflight-resolved <ruling id> once the director has ruled")
        return done, busy

    ctx.check_mirror()
    done, busy = gate()
    seed_base = parse_seed_base(ctx.kc.read("seed-base"))
    salt = check_hex64(ctx.kc.read("salt"), "salt")
    if commitment_digest(seed_base, salt) != commitment:
        raise Stop(TERMINAL, "the Keychain seed base and salt do not reproduce the published commitment")
    # The reveal line stops every PV role of the seal and pg-connect for good; it is recorded before any print.
    detail = f"after {done[-1]['event']} readout" if done else f"after stop {after_stop}"
    ctx.commit_event({"event": "reveal", "key": key, "role": "reveal", "commitment": commitment,
                      "detail": detail + (f"; in flight resolved by {inflight_resolved}" if busy else "")},
                     f"[record] covfix: reveal for {key[:12]}", gate=gate)
    print(f"seed_base={seed_base}")
    print(f"salt={salt}")
    return OK


# ----------------------------------------------------------------------------------------------------------
# synthetic-seal
# ----------------------------------------------------------------------------------------------------------

def synthetic_seal(kc: Keychain, out: str, gpg: str = "gpg") -> dict:
    """A dummy truth sealed exactly as PG seals products: a ciphertext per product, an encrypted manifest of
    plaintext sha256s, a decrypt round trip, no plaintext on disk, PG-SEAL.sha256 over the ciphertexts, and a
    dummy P2-FREEZE.sha256. Test or synthetic credentials only."""
    if kc.prefix == REAL_PREFIX:
        raise Stop(ERROR, "synthetic-seal refuses the real Keychain items")
    if os.path.exists(out):
        raise Stop(ERROR, f"{out} exists")
    passphrase = check_hex64(kc.read("passphrase"), "passphrase")
    ct_dir, fz_dir = os.path.join(out, "sealed"), os.path.join(out, "frozen")
    os.makedirs(ct_dir, mode=0o700)
    os.makedirs(fz_dir, mode=0o700)
    truth = json.dumps({"synthetic": True, "r_u": [1.0 + (secrets.randbelow(2001) - 1000) / 10000.0
                                                    for _ in range(64)]}).encode()
    products = {"synthetic-truth-u0.json": truth}
    manifest = {"products": {name: sha256_bytes(data) for name, data in products.items()}}
    for name, data in products.items():
        ct = gpg_run(GPG_ENCRYPT, passphrase, data, gpg)
        if sha256_bytes(gpg_run(GPG_DECRYPT, passphrase, ct, gpg)) != manifest["products"][name]:
            raise Stop(TERMINAL, f"round trip of {name} does not reproduce its plaintext sha256")
        with open(os.path.join(ct_dir, name + ".gpg"), "wb") as f:
            f.write(ct)
    del truth, products
    with open(os.path.join(ct_dir, "PG-MANIFEST.json.gpg"), "wb") as f:
        f.write(gpg_run(GPG_ENCRYPT, passphrase, json.dumps(manifest, sort_keys=True).encode(), gpg))
    seal_lines = "".join(f"{sha256_file(os.path.join(ct_dir, n))}  {n}\n" for n in sorted(os.listdir(ct_dir)))
    with open(os.path.join(out, "PG-SEAL.sha256"), "w") as f:
        f.write(seal_lines)
    with open(os.path.join(fz_dir, "synthetic-frozen.txt"), "w") as f:
        f.write("synthetic frozen candidate, no physics\n")
    with open(os.path.join(out, "P2-FREEZE.sha256"), "w") as f:
        f.write(f"{sha256_file(os.path.join(fz_dir, 'synthetic-frozen.txt'))}  synthetic-frozen.txt\n")
    return {"seal_digest": sha256_file(os.path.join(out, "PG-SEAL.sha256")),
            "freeze_digest": sha256_file(os.path.join(out, "P2-FREEZE.sha256")),
            "seal_root": ct_dir, "freeze_root": fz_dir}


# ----------------------------------------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------------------------------------

def main(argv=None) -> int:
    no_core_dumps()
    ap = argparse.ArgumentParser(prog="covfix_wrapper.py", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate", help="create the three Keychain items, never overwriting")
    g.add_argument("--keychain-prefix", default=REAL_PREFIX)
    c = sub.add_parser("commitment", help="print sha256(seed base ':' salt-hex)")
    c.add_argument("--keychain-prefix", default=REAL_PREFIX)
    for name in ("run", "reveal", "status"):
        p = sub.add_parser(name)
        p.add_argument("--config", required=True)
        p.add_argument("--config-sha256", required=True)
        if name != "status":
            p.add_argument("--seal-digest")
        if name == "run":
            p.add_argument("--role", required=True, choices=sorted(ROLES))
            p.add_argument("--freeze-digest")
            p.add_argument("--commitment")
            p.add_argument("--freeze-mismatch-resolved", help="a director ruling id clearing this seal's "
                                                               "freeze-mismatch refusals")
        if name == "reveal":
            p.add_argument("--commitment", required=True)
            p.add_argument("--after-stop")
            p.add_argument("--inflight-resolved")
    s = sub.add_parser("synthetic-seal", help="build a dummy sealed truth with test credentials")
    s.add_argument("--keychain-prefix", required=True)
    s.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "generate":
            print(generate(Keychain(a.keychain_prefix)))
            return OK
        if a.cmd == "commitment":
            kc = Keychain(a.keychain_prefix)
            print(commitment_digest(parse_seed_base(kc.read("seed-base")), check_hex64(kc.read("salt"), "salt")))
            return OK
        if a.cmd == "synthetic-seal":
            print(json.dumps(synthetic_seal(Keychain(a.keychain_prefix), a.out), indent=1, sort_keys=True))
            return OK
        ctx = Context(load_config(a.config, a.config_sha256))
        if a.cmd == "status":
            ctx.record.ensure_dir()
            for e in ctx.record.lines():
                print(json.dumps(e, sort_keys=True))
            print(f"markers: {ctx.record.markers()}")
            return OK
        if a.cmd == "reveal":
            return reveal(ctx, a.seal_digest, a.commitment, a.after_stop, a.inflight_resolved)
        return run_role(ctx, a.role, a.seal_digest, a.freeze_digest, a.commitment, a.freeze_mismatch_resolved)
    except Stop as e:
        print(f"covfix: {['OK', '', 'REFUSED', 'TERMINAL', 'ERROR'][e.code]}: {e}", file=sys.stderr)
        return e.code


if __name__ == "__main__":
    sys.exit(main())
