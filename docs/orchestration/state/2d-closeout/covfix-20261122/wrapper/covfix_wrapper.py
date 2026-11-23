#!/usr/bin/env python3
"""The director's wrapper for COVFIX's secret-bearing roles (COVFIX-DECLARATION ST4, sec. 3.4, sec. 4.2).

  generate        create the passphrase, the PG seed base and the salt in the macOS login Keychain, never on argv;
  commitment      print sha256(seed base ':' salt-hex), the value published before PG generates (sec. 4.2);
  run             run one secret-bearing role (pg-connect, pv-writer, pv-readout) through ST4's consumption record:
                  verify the seal and the freeze on the cluster, spend the role durably (attempt marker, append,
                  fsync, commit, push, verify the remote blob), and only then pipe the secrets into the bound
                  binary's stdin;
  reveal          print the seed base and salt after PV's readout, once they reproduce the commitment;
  synthetic-seal  build a dummy sealed truth with the same flags, for the end-to-end test of sec. 3.4;
  status          print the consumption record and markers (they hold no secret).

THE SECRETS go from `security find-generic-password -w` into this process's memory and then into the stdin of ssh
(no PTY), which hands them to salloc/srun, which forward stdin to the task. They are never written to a file, put
in an argument vector or the environment, or printed. `generate` feeds `security -i` on stdin for the same reason.

THE BINDING. The role config is sha-pinned in the binding, and it pins the campaign's digests too (`binding`:
commitment, seal_digest, freeze_digest). The digests given on the command line must equal them.

THE STDIN FRAME a bound binary receives (cov2d's PG and PV code must read exactly this, then EOF):
  pg-connect               b"<passphrase: 64 lowercase hex>\\n<seed base: ASCII decimal>\\n"
  pv-writer, pv-readout    b"<passphrase: 64 lowercase hex>\\n"
The salt never leaves this laptop before `reveal`. A bound binary that finds a confirmed integrity break (its
manifest, chain or inputs) exits BREAK_RC (66), which the wrapper records as a break of the whole seal.

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
import re
import secrets
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import time

OK, REFUSED, TERMINAL, ERROR = 0, 2, 3, 4
BREAK_RC = 66                          # a bound binary's exit status for a confirmed integrity break
EXEC_MISMATCH_RC = 86                  # the compute-side hash check of the bound binary failed

SECURITY = "/usr/bin/security"
ACCOUNT = "director"
REAL_PREFIX = "covfix-"
TEST_PREFIX_RE = re.compile(r"covfix-(test|synth)-(?:[a-z0-9]+-)?")
ITEMS = ("passphrase", "seed-base", "salt")
FORBID_REAL_ENV = "COVFIX_FORBID_REAL_KEYCHAIN"

# PG's seed base (sec. 4.2): tune u's task seed = base + 10_000*u + task index, u in {0, 1}. run_gevgen_v3.sh
# passes the seed to gevgen as both --seed and -r, so every task seed must stay below 2**31 - 1.
SEED_BASE_LO = 1_000_000_000
SEED_BASE_HI = 2_000_000_000          # exclusive
TUNE_STRIDE = 10_000
N_TUNES = 2
MAX_TASK_INDEX = 9_999                # cov2d confirms PG's task index < 10_000 for F1's pipeline
assert SEED_BASE_HI + TUNE_STRIDE * (N_TUNES - 1) + MAX_TASK_INDEX < 2**31 - 1, "seed range overflows int32"

HEX64 = re.compile(r"[0-9a-f]{64}")
STOP_TEXT = re.compile(r"[A-Za-z0-9 .,:;()'_/-]{1,200}")

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
EVENTS = ("spent", "completed", "terminal", "uncertain", "break", "reveal")
SEAL_WIDE = ("break", "reveal")       # events that stop every role of their key
MARK_KINDS = ("attempt", "uncertain", "break")
RECORD_NAME = "RECORD.jsonl"
LOCK_NAME = "LOCK"
LOCK_TIMEOUT_S = 10.0
GENESIS = "0" * 64


class Stop(Exception):
    """A refusal or a terminal stop, with the exit code it maps to."""

    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


class Consumed(Stop):
    """The role was spent, stopped or marked before: terminal, and no new marker is needed."""

    def __init__(self, message: str):
        super().__init__(TERMINAL, message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return sha256_bytes(f.read())


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fsync_dir(path: str) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


# ----------------------------------------------------------------------------------------------------------
# Keychain
# ----------------------------------------------------------------------------------------------------------

def check_prefix(prefix: str) -> str:
    if prefix == REAL_PREFIX:
        if os.environ.get(FORBID_REAL_ENV):
            raise Stop(ERROR, f"the real Keychain prefix {REAL_PREFIX!r} is forbidden here ({FORBID_REAL_ENV})")
        return prefix
    if TEST_PREFIX_RE.fullmatch(prefix):
        return prefix
    raise Stop(ERROR, f"Keychain prefix {prefix!r} is neither {REAL_PREFIX!r} nor covfix-test-*/covfix-synth-*")


def login_keychain(security: str = SECURITY) -> str:
    r = subprocess.run([security, "login-keychain"], stdin=subprocess.DEVNULL, capture_output=True, text=True)
    path = r.stdout.strip().strip('"')
    if r.returncode != 0 or not path.startswith("/") or any(c.isspace() for c in path):
        raise Stop(ERROR, "cannot resolve the login Keychain (or its path holds whitespace)")
    return path


class Keychain:
    """The three director-held items, service names <prefix><item>, account 'director', in the LOGIN Keychain
    (every call names it, so a changed default Keychain or search list cannot move them)."""

    def __init__(self, prefix: str, security: str = SECURITY, keychain: str | None = None):
        self.prefix = check_prefix(prefix)
        self.security = security
        self.keychain = keychain or login_keychain(security)

    def service(self, item: str) -> str:
        if item not in ITEMS:
            raise ValueError(item)
        return self.prefix + item

    def exists(self, item: str) -> bool:
        r = subprocess.run([self.security, "find-generic-password", "-s", self.service(item), "-a", ACCOUNT,
                            self.keychain], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        if r.returncode == 0:
            return True
        if r.returncode == 44:          # errSecItemNotFound
            return False
        raise Stop(ERROR, f"security find-generic-password exited {r.returncode} for {self.service(item)}")

    def read(self, item: str) -> str:
        r = subprocess.run([self.security, "find-generic-password", "-s", self.service(item), "-a", ACCOUNT, "-w",
                            self.keychain], stdin=subprocess.DEVNULL, capture_output=True)
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
        r = subprocess.run([self.security, "-i"], input=command.encode("ascii"), capture_output=True)
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
    present (never their values) and changes nothing."""
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
        except Stop as e:
            now = [i for i in ITEMS if kc.exists(i)]
            raise Stop(ERROR, f"{e}; the Keychain now holds {len(now)} of {len(ITEMS)} items "
                              f"({', '.join(now) or 'none'})")
    return "created"


# ----------------------------------------------------------------------------------------------------------
# gpg, with the passphrase on fd 3 through an internal pipe (sec. 4.2 point 2)
# ----------------------------------------------------------------------------------------------------------

def gpg_run(argv, passphrase: str, payload: bytes, gpg: str = "gpg") -> bytes:
    """Run gpg with the pinned argv in a fresh, empty, private GNUPGHOME (no ambient gpg.conf can change where the
    plaintext goes or how an integrity failure exits). Returns stdout only after gpg exited 0."""
    argv = [gpg, *argv[1:]]
    home = tempfile.mkdtemp(prefix="cfxg", dir="/tmp" if os.path.isdir("/tmp") else None)
    os.chmod(home, 0o700)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GPG") and k != "GNUPGHOME"}
    env["GNUPGHOME"] = home
    r, w = os.pipe()
    try:
        try:
            os.write(w, passphrase.encode("ascii") + b"\n")
        finally:
            os.close(w)

        def child():               # runs after the std streams are set up and before fds are closed and exec
            if r != 3:
                os.dup2(r, 3)
            else:
                os.set_inheritable(3, True)
        try:
            # close_fds=False: Python's own descriptors are non-inheritable (PEP 446), so only 0-2 and fd 3 pass.
            p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 close_fds=False, preexec_fn=child, env=env)
        finally:
            os.close(r)
        out, err = p.communicate(payload)
    finally:
        subprocess.run(["gpgconf", "--homedir", home, "--kill", "gpg-agent"], capture_output=True, env=env)
        shutil.rmtree(home, ignore_errors=True)
    if p.returncode != 0:
        raise Stop(TERMINAL, f"gpg exited {p.returncode}: {err.decode(errors='replace').strip()[-300:]}")
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
# other failure (a permission error on the file or a parent, a directory) is UNREADABLE, which refuses.
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


class Cluster:
    def __init__(self, ssh_argv, host: str):
        if not ssh_argv or not host:
            raise Stop(ERROR, "the role config names no ssh program or host")
        # No PTY, ever: a forced terminal would echo the frame back on ssh's output.
        self.ssh_argv = [ssh_argv[0], "-T", "-o", "RequestTTY=no", *ssh_argv[1:]]
        self.host = host

    def hash_files(self, root: str, rels):
        """(sha256 per relpath under root, set of relpaths confirmed absent), computed on the cluster. Anything
        short of exactly one typed answer per path is the link or the environment: REFUSED."""
        remote = f"cd -- {shlex.quote(root)} || exit {ROOT_MISSING_RC}; bash -c {shlex.quote(HASH_SCRIPT)}"
        r = subprocess.run([*self.ssh_argv, self.host, remote], input=b"".join(x.encode() + b"\0" for x in rels),
                           capture_output=True)
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
        if sorted(seen) != sorted(rels) or unreadable:
            raise Stop(REFUSED, f"hashing on {self.host}: {len(unreadable)} unreadable path(s), "
                                f"{len(seen)} answers for {len(rels)} paths; nothing spent")
        return got, missing

    def launch(self, command: str, frame: bytearray) -> tuple:
        """(exit status, whether the whole frame reached ssh's stdin). The frame is written unbuffered and zeroed."""
        p = subprocess.Popen([*self.ssh_argv, self.host, command], stdin=subprocess.PIPE, bufsize=0)
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
            return p.wait(), delivered
        except BaseException:
            p.kill()
            p.wait()
            raise


def launch_command(role: str, rcfg: dict) -> str:
    """The remote command, built from the structured role config: launcher + the compute-side hash check + the
    bound binary + its arguments. PV roles must run on an exclusive node (salloc --exclusive, srun --exclusive)."""
    try:
        launcher, binary, args = list(rcfg["launcher"]), rcfg["binary"], list(rcfg.get("args", []))
        want = check_hex64(rcfg["binary_sha256"], "binary sha256")
    except (KeyError, TypeError) as e:
        raise Stop(ERROR, f"role config for {role} lacks or mistypes {e}")
    if not isinstance(binary, str) or not binary.startswith("/"):
        raise Stop(ERROR, f"role config for {role}: the binary must be an absolute path")
    if not all(isinstance(x, str) for x in launcher + args):
        raise Stop(ERROR, f"role config for {role}: launcher and args must be strings")
    if role != "pg-connect":
        names = [os.path.basename(x) for x in launcher]
        try:
            s, r = names.index("salloc"), names.index("srun")
        except ValueError:
            raise Stop(ERROR, f"{role} must run under salloc and srun")
        if not (s < r and "--exclusive" in launcher[s + 1:r] and "--exclusive" in launcher[r + 1:]):
            raise Stop(ERROR, f"{role} must run with salloc --exclusive and srun --exclusive")
    return shlex.join([*launcher, "bash", "-c", EXEC_CHECK, "covfix-exec", binary, want, *args])


# ----------------------------------------------------------------------------------------------------------
# ST4's consumption record
# ----------------------------------------------------------------------------------------------------------

class Record:
    """Append-only, hash-chained JSON lines in a mode-700 directory, plus O_EXCL markers.

    Markers: MARK-attempt-<key12>-<role> is created, fsynced, BEFORE a spend is appended, so a crash or failure at
    any later point leaves the role blocked; MARK-uncertain-<key12>-<role> records a lock failure;
    MARK-break-<key12>-seal is created before a break is recorded, so a break that cannot be appended still stops
    every role of the seal. Markers are never removed; each is absorbed into the chain at the next locked write."""

    def __init__(self, directory: str):
        self.dir = os.path.abspath(os.path.expanduser(directory))
        self.path = os.path.join(self.dir, RECORD_NAME)
        self._lock_fd = None

    def ensure_dir(self) -> None:
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir, mode=0o700)
        st = os.stat(self.dir)
        if stat.S_IMODE(st.st_mode) != 0o700 or st.st_uid != os.getuid():
            raise Stop(REFUSED, f"{self.dir} must be mode 700 and owned by this user")

    def raw(self) -> bytes:
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
            os.write(fd, f"{kind} {key} {role} {utc_now()}\n".encode())
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

    def append(self, event: dict) -> bytes:
        """Append one chained line and fsync the file and the directory. Caller holds the lock."""
        assert self._lock_fd is not None, "append without the lock"
        data = self.raw()
        lines = self.parse(data)
        prev = sha256_bytes(data.splitlines()[-1]) if lines else GENESIS
        ev = {"seq": len(lines), "prev": prev, "utc": utc_now(), **event}
        line = json.dumps(ev, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        fd = os.open(self.path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        try:
            if os.write(fd, line) != len(line):
                raise OSError("short write")
            os.fsync(fd)
        finally:
            os.close(fd)
        fsync_dir(self.dir)
        return self.raw()

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
            elif not any(e["key"] == key and e["role"] == role for e in events):
                self.append({"event": "uncertain", "key": key, "role": role, "detail": f"from {kind} marker"})
            events = self.lines()


def blocked(events, markers, key: str, role: str):
    """Why (key, role) may not be spent, or None. Any line or marker for the pair blocks it; a break or a reveal
    (line or marker) blocks every role of the key."""
    for e in events:
        if e["key"] == key and (e["role"] == role or e["event"] in SEAL_WIDE):
            return f"record line seq {e.get('seq')}: {e['event']} {e['role']}"
    for kind, k, r in markers:
        if k == key and (r == role or kind == "break"):
            return f"{kind} marker for {r}"
    return None


def bound_freeze(events, key: str):
    for e in events:
        if e["key"] == key and e.get("freeze"):
            return e["freeze"]
    return None


def writer_completed(events, key: str) -> bool:
    return any(e["key"] == key and e["role"] == "pv-writer" and e["event"] == "completed" for e in events)


# ----------------------------------------------------------------------------------------------------------
# The mirror: one path, committed and pushed on a dedicated branch of a git worktree
# ----------------------------------------------------------------------------------------------------------

class Mirror:
    """The record's mirror. Three guards against a restored or rewound history:
    - every version ever published stays reachable from a local ref refs/covfix/published/<seq>;
    - the remote branch is fetched WITHOUT force into refs/covfix/seen/<branch>, so a rewound or deleted remote
      branch fails the fetch (terminal) instead of silently replacing what was seen;
    - every version in any commit reachable from any ref is scanned for lines the local record lacks.
    The remote should also forbid force pushes and deletion of the branch (a host setting, outside this tool)."""

    def __init__(self, cfg: dict):
        try:
            self.wt = os.path.expanduser(cfg["worktree"])
            self.rel = cfg["path"]
            self.remote = cfg["remote"]
            self.branch = cfg["branch"]
        except KeyError as e:
            raise Stop(ERROR, f"mirror config lacks {e}")
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
        return f"refs/covfix/seen/{self.branch}"

    def preflight(self) -> None:
        head = self.git("symbolic-ref", "--short", "HEAD").stdout.decode().strip()
        if head != self.branch:
            raise Stop(REFUSED, f"mirror worktree is on {head!r}, not {self.branch!r}")
        if self.git("status", "--porcelain", "--", self.rel).stdout.strip():
            raise Stop(REFUSED, f"mirror path {self.rel} has uncommitted changes")

    def fetch(self) -> bytes | None:
        """Fetch the branch without force; return its mirrored record bytes, or None before the first publish."""
        had_seen = self.git("rev-parse", "-q", "--verify", self.seen, check=False).returncode == 0
        ls = self.git("ls-remote", "--heads", self.remote, self.branch).stdout.strip()
        if not ls:
            if had_seen:
                raise Stop(TERMINAL, f"the remote mirror branch {self.branch} was deleted after it was seen")
            return None
        incoming = f"refs/covfix/incoming/{self.branch}"
        r = self.git(*self.hooks, "fetch", "-q", self.remote, f"+refs/heads/{self.branch}:{incoming}", check=False)
        if r.returncode != 0:
            raise Stop(REFUSED, f"git fetch of the mirror failed: {r.stderr.decode(errors='replace').strip()[-300:]}")
        if had_seen and self.git("merge-base", "--is-ancestor", self.seen, incoming, check=False).returncode != 0:
            raise Stop(TERMINAL, f"the remote mirror branch {self.branch} was rewound (what was seen is not an "
                                 "ancestor of its tip)")
        self.git("update-ref", self.seen, incoming)
        r = self.git("cat-file", "blob", f"{self.seen}:{self.rel}", check=False)
        return r.stdout if r.returncode == 0 else None

    def history(self) -> list:
        """Every version of the mirrored record in any commit reachable from any ref."""
        revs = self.git("rev-list", "--all", "--", self.rel).stdout.decode().split()
        out = []
        for rev in revs:
            r = self.git("cat-file", "blob", f"{rev}:{self.rel}", check=False)
            if r.returncode == 0:
                out.append((rev, r.stdout))
        return out

    def publish(self, data: bytes, message: str, seq: int) -> None:
        """Commit the record bytes, push, refetch, require the remote blob to equal them, keep a published ref."""
        dest = os.path.join(self.wt, self.rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        self.git("add", "--", self.rel)
        self.git(*self.hooks, *self.ident, "commit", "-q", "-m", message, "--", self.rel)
        self.git(*self.hooks, "push", "-q", self.remote, f"HEAD:refs/heads/{self.branch}")
        if self.fetch() is None or \
                self.git("rev-parse", f"{self.seen}:{self.rel}").stdout.decode().strip() != git_blob_sha(data):
            raise Stop(TERMINAL, "the pushed mirror's blob does not equal the local record")
        self.git("update-ref", f"refs/covfix/published/{seq:06d}", "HEAD")


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
    for k in ("record_dir", "keychain_prefix", "ssh", "host", "mirror", "roles", "binding"):
        if k not in cfg:
            raise Stop(ERROR, f"role config lacks {k!r}")
    return cfg


class Context:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.record = Record(cfg["record_dir"])
        self.mirror = Mirror(cfg["mirror"])
        self.cluster = Cluster(cfg["ssh"], cfg["host"])
        self.kc = Keychain(cfg["keychain_prefix"], cfg.get("security", SECURITY), cfg.get("keychain"))

    def pinned(self, name: str, given) -> str:
        """A campaign digest from the pinned binding; the command-line value must equal it."""
        want = check_hex64(self.cfg["binding"].get(name), f"binding's {name}")
        if given != want:
            raise Stop(REFUSED, f"--{name.replace('_', '-')} is not the binding's {name}")
        return want

    def check_mirror(self) -> None:
        """The pushed mirror must be a prefix of the local record, and no version in its history may hold a line
        the local record lacks (a restored older copy)."""
        self.mirror.preflight()
        local = self.record.raw()
        remote = self.mirror.fetch()
        if remote is not None and not local.startswith(remote):
            raise Stop(TERMINAL, "the local record is not an extension of the pushed mirror (restored copy?)")
        local_lines = set(local.splitlines())
        for rev, blob in self.mirror.history():
            missing = [x for x in blob.splitlines() if x not in local_lines]
            if missing:
                raise Stop(TERMINAL, f"mirror commit {rev[:12]} holds {len(missing)} line(s) the local record "
                                     "lacks (restored copy?)")

    def spend_checks(self, key: str, role: str, freeze) -> None:
        """Every reason a spend of (key, role) is not allowed, read from the current record and markers."""
        events, markers = self.record.lines(), self.record.markers()
        why = blocked(events, markers, key, role)
        if why:
            raise Consumed(f"{role} for {key[:12]} is already consumed ({why})")
        if freeze:
            bound = bound_freeze(events, key)
            if bound and bound != freeze:
                raise Stop(REFUSED, f"seal {key[:12]} is bound to freeze {bound[:12]}, not {freeze[:12]}")
        if role == "pv-readout" and not writer_completed(events, key):
            raise Stop(REFUSED, f"pv-readout needs a completed pv-writer for seal {key[:12]}")

    def commit_event(self, event: dict, message: str, absorb_exclude=None) -> None:
        """Lock; absorb markers; for a spend, re-check the mirror and every spend condition UNDER the lock and
        create the attempt marker; then append, fsync, commit, push, verify. Any failure after the attempt marker
        leaves the role blocked, and is terminal."""
        key, role = event["key"], event["role"]
        try:
            self.record.lock()
        except BaseException as e:
            self.record.mark("uncertain", key, role)
            raise Stop(TERMINAL, f"cannot take the record lock ({type(e).__name__}: {e}); {role} is now blocked")
        try:
            try:
                self.record.absorb_markers(absorb_exclude)
                if event["event"] == "spent":
                    self.check_mirror()
                    self.spend_checks(key, role, event.get("freeze"))
            except BaseException:
                if event["event"] == "spent":
                    raise                       # nothing spent: the refusal stands as raised
                self.record.mark("uncertain", key, role)
                raise
            if event["event"] == "spent" and not self.record.mark("attempt", key, role):
                raise Consumed(f"{role} for {key[:12]} has an attempt marker already")
            try:
                data = self.record.append(event)
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

def verify_list(ctx: Context, sumfile: str, digest: str, root: str, what: str, key: str, role: str) -> None:
    try:
        with open(os.path.expanduser(sumfile), "rb") as f:
            data = f.read()
    except OSError as e:
        raise Stop(REFUSED, f"cannot read the local {what} ({e}); nothing spent")
    if sha256_bytes(data) != digest:
        break_seal(ctx, key, role, f"{what} file does not hash to the pinned digest")
    try:
        want = parse_sumfile(data, what)
    except Stop as e:
        break_seal(ctx, key, role, str(e))
    got, missing = ctx.cluster.hash_files(root, list(want))
    altered = sorted(rel for rel, d in want.items() if rel in got and got[rel] != d)
    if missing or altered:
        first = sorted(missing)[0] if missing else altered[0]
        break_seal(ctx, key, role, f"{what}: {len(missing)} missing and {len(altered)} altered of {len(want)} "
                                   f"files, first {first}")


def break_seal(ctx: Context, key: str, role: str, detail: str):
    """A confirmed break: the seal-wide marker first (durable even if the record cannot be written), then the line."""
    ctx.record.mark("break", key, "seal")
    try:
        ctx.commit_event({"event": "break", "key": key, "role": role, "detail": detail},
                         f"[record] covfix: BREAK {key[:12]} ({role})", absorb_exclude=("break", key, "seal"))
    except Stop as e:
        detail += f"; and recording the break failed: {e}"
    raise Stop(TERMINAL, f"BREAK: {detail}")


def run_role(ctx: Context, role: str, seal_digest, freeze_digest, commitment) -> int:
    kind, frame_has_seed = ROLES[role]
    rcfg = ctx.cfg["roles"].get(role)
    if not rcfg:
        raise Stop(ERROR, f"the role config has no entry for {role}")
    command = launch_command(role, rcfg)
    ctx.record.ensure_dir()

    if kind == "seal":
        for k in ("seal_file", "seal_root", "freeze_file", "freeze_root"):
            if not isinstance(ctx.cfg.get(k), str):
                raise Stop(ERROR, f"role config lacks {k!r}")
        key = ctx.pinned("seal_digest", seal_digest)
        freeze = ctx.pinned("freeze_digest", freeze_digest)
    else:
        key = ctx.pinned("commitment", commitment)
        freeze = None

    # 1. The record and its mirror, before anything else: a consumed role refuses without touching the cluster.
    #    (Repeated under the lock at the spend.)
    ctx.check_mirror()
    ctx.spend_checks(key, role, freeze)

    # 2. The secrets, read and checked before the spend so a Keychain failure burns nothing.
    passphrase = check_hex64(ctx.kc.read("passphrase"), "passphrase")
    frame = bytearray(passphrase.encode("ascii") + b"\n")
    if frame_has_seed:
        seed_base = parse_seed_base(ctx.kc.read("seed-base"))
        if commitment_digest(seed_base, check_hex64(ctx.kc.read("salt"), "salt")) != key:
            raise Stop(REFUSED, "the Keychain seed base and salt do not reproduce the published commitment")
        frame += str(seed_base).encode("ascii") + b"\n"

    # 3. The bound binary, then the seal and the freeze, hashed on the cluster.
    binary, want_bin = rcfg["binary"], rcfg["binary_sha256"]
    got_bin, _ = ctx.cluster.hash_files(os.path.dirname(binary), [os.path.basename(binary)])
    if got_bin.get(os.path.basename(binary)) != want_bin:
        raise Stop(REFUSED, f"the bound binary {binary} does not hash to the pinned sha256; nothing spent")
    if kind == "seal":
        verify_list(ctx, ctx.cfg["seal_file"], key, ctx.cfg["seal_root"], "PG-SEAL.sha256", key, role)
        verify_list(ctx, ctx.cfg["freeze_file"], freeze, ctx.cfg["freeze_root"], "P2-FREEZE.sha256", key, role)

    # 4. The spend: durable (attempt marker, fsync, commit, push, remote blob verified) before any plaintext exists.
    spent = {"event": "spent", "key": key, "role": role, "binary_sha256": want_bin}
    if freeze:
        spent["freeze"] = freeze
    ctx.commit_event(spent, f"[record] covfix: spent {role} {key[:12]}")

    # 5. The launch. A crash, a dropped link or an undelivered frame after this point is terminal; no retry.
    try:
        rc, delivered = ctx.cluster.launch(command, frame)
    except BaseException as e:
        rc, delivered = f"interrupted ({type(e).__name__})", False
    if rc == BREAK_RC and kind == "seal":
        ctx.record.mark("break", key, "seal")
        outcome, detail = "break", f"the bound {role} reported a confirmed integrity break (rc {BREAK_RC})"
    elif rc == 0 and delivered:
        outcome, detail = "completed", "rc 0"
    else:
        outcome, detail = "terminal", f"rc {rc}" + ("" if delivered else ", frame not delivered")
    try:
        ctx.commit_event({"event": outcome, "key": key, "role": role, "detail": detail},
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

def reveal(ctx: Context, seal_digest, commitment, after_stop) -> int:
    ctx.record.ensure_dir()
    key = ctx.pinned("seal_digest", seal_digest)
    commitment = ctx.pinned("commitment", commitment)
    ctx.check_mirror()
    events = ctx.record.lines()
    done = [e for e in events if e["key"] == key and e["role"] == "pv-readout"
            and e["event"] in ("completed", "terminal")]
    if after_stop is not None and not STOP_TEXT.fullmatch(after_stop.strip() or "-"):
        raise Stop(REFUSED, "--after-stop must name the stop in plain words (letters, digits, .,:;()'_/- only)")
    if not done and not (after_stop or "").strip():
        raise Stop(REFUSED, "PV's readout has no outcome line for this seal; reveal needs --after-stop '<stop>'")
    seed_base = parse_seed_base(ctx.kc.read("seed-base"))
    salt = check_hex64(ctx.kc.read("salt"), "salt")
    if commitment_digest(seed_base, salt) != commitment:
        raise Stop(TERMINAL, "the Keychain seed base and salt do not reproduce the published commitment")
    # The reveal line stops every PV role of the seal for good, and it is recorded before anything is printed.
    ctx.commit_event({"event": "reveal", "key": key, "role": "reveal", "commitment": commitment,
                      "detail": f"after {done[-1]['event']} readout" if done else f"after stop: {after_stop.strip()}"},
                     f"[record] covfix: reveal for {key[:12]}")
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
        if name == "reveal":
            p.add_argument("--commitment", required=True)
            p.add_argument("--after-stop")
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
            return reveal(ctx, a.seal_digest, a.commitment, a.after_stop)
        return run_role(ctx, a.role, a.seal_digest, a.freeze_digest, a.commitment)
    except Stop as e:
        print(f"covfix: {['OK', '', 'REFUSED', 'TERMINAL', 'ERROR'][e.code]}: {e}", file=sys.stderr)
        return e.code


if __name__ == "__main__":
    sys.exit(main())
