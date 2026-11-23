#!/usr/bin/env python3
"""The director's wrapper for COVFIX's secret-bearing roles (COVFIX-DECLARATION ST4, sec. 3.4, sec. 4.2).

It does six things, and only these:

  generate     create the passphrase, the PG seed base and the salt in the macOS login Keychain, never on argv;
  commitment   print sha256(seed base ':' salt-hex), the value published before PG generates (sec. 4.2);
  run          run one secret-bearing role (pg-connect, pv-writer, pv-readout) through ST4's consumption record:
               verify the seal and the freeze on the cluster, spend the role durably (append, fsync, commit,
               push, verify the remote blob), and only then pipe the secrets into the bound binary's stdin;
  reveal       print the seed base and salt after PV's readout, once they reproduce the commitment;
  synthetic-seal  build a dummy sealed truth with the same flags, for the end-to-end test of sec. 3.4;
  status       print the consumption record (it holds no secret).

THE SECRETS go from `security find-generic-password -w` into this process's memory and then into the stdin of
ssh, which hands them to salloc/srun, which forwards stdin to the task. They are never written to a file, put in
an argument vector or the environment, or printed. `generate` feeds `security -i` on stdin for the same reason.

THE STDIN FRAME a bound binary receives (cov2d's PG and PV code must read exactly this, then EOF):
  pg-connect               b"<passphrase: 64 lowercase hex>\\n<seed base: ASCII decimal>\\n"
  pv-writer, pv-readout    b"<passphrase: 64 lowercase hex>\\n"
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
import re
import secrets
import shlex
import stat
import subprocess
import sys
import time

OK, REFUSED, TERMINAL, ERROR = 0, 2, 3, 4

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
    """The role was spent, stopped or marked uncertain before: terminal, and no new marker is needed."""

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


class Keychain:
    """The three director-held items, under service names <prefix><item>, account 'director'."""

    def __init__(self, prefix: str, security: str = SECURITY):
        self.prefix = check_prefix(prefix)
        self.security = security

    def service(self, item: str) -> str:
        if item not in ITEMS:
            raise ValueError(item)
        return self.prefix + item

    def exists(self, item: str) -> bool:
        r = subprocess.run([self.security, "find-generic-password", "-s", self.service(item), "-a", ACCOUNT],
                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode == 0:
            return True
        if r.returncode == 44:          # errSecItemNotFound
            return False
        raise Stop(ERROR, f"security find-generic-password exited {r.returncode} for {self.service(item)}")

    def read(self, item: str) -> str:
        r = subprocess.run([self.security, "find-generic-password", "-s", self.service(item), "-a", ACCOUNT, "-w"],
                           stdin=subprocess.DEVNULL, capture_output=True)
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
        command = f"add-generic-password -s {self.service(item)} -a {ACCOUNT} -w {value}\n"
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


def check_hex64(text: str, what: str) -> str:
    if not HEX64.fullmatch(text):
        raise Stop(REFUSED, f"the {what} is not 64 lowercase hex characters")
    return text


def commitment_digest(seed_base: int, salt_hex: str) -> str:
    """sec. 4.2: the seed base in ASCII decimal, one ':', the salt as 64 lowercase hex characters, no newline."""
    if not SEED_BASE_LO <= seed_base < SEED_BASE_HI:
        raise Stop(REFUSED, "the seed base is outside the documented range")
    check_hex64(salt_hex, "salt")
    return sha256_bytes(f"{seed_base}:{salt_hex}".encode("ascii"))


def generate(kc: Keychain) -> str:
    """Create all three items, or none. Returns 'created' or 'exists'."""
    if any(kc.exists(item) for item in ITEMS):
        return "exists"
    values = {
        "passphrase": secrets.token_hex(32),
        "seed-base": str(SEED_BASE_LO + secrets.randbelow(SEED_BASE_HI - SEED_BASE_LO)),
        "salt": secrets.token_hex(32),
    }
    done = []
    for item in ITEMS:
        try:
            kc.add(item, values[item])
        except Stop as e:
            raise Stop(ERROR, f"{e}; created {len(done)} of {len(ITEMS)} items ({', '.join(done) or 'none'})")
        done.append(item)
    return "created"


# ----------------------------------------------------------------------------------------------------------
# gpg, with the passphrase on fd 3 through an internal pipe (sec. 4.2 point 2)
# ----------------------------------------------------------------------------------------------------------

def gpg_run(argv, passphrase: str, payload: bytes, gpg: str = "gpg", env=None) -> bytes:
    argv = [gpg, *argv[1:]]
    r, w = os.pipe()
    try:
        os.write(w, passphrase.encode("ascii") + b"\n")
    finally:
        os.close(w)
    try:
        p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             pass_fds=(r, 3) if r != 3 else (3,), preexec_fn=(lambda: os.dup2(r, 3)) if r != 3 else None,
                             env=env)
    finally:
        os.close(r)
    out, err = p.communicate(payload)
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


class Cluster:
    def __init__(self, ssh_argv, host: str):
        if not ssh_argv or not host:
            raise Stop(ERROR, "the role config names no ssh program or host")
        self.ssh_argv = list(ssh_argv)
        self.host = host

    # Run under bash on the login node: one line per path, so a break needs positive evidence. A path that does
    # not exist prints covfix-missing; one that exists but cannot be hashed prints covfix-unreadable.
    HASH_SCRIPT = ('while IFS= read -r -d "" f; do if [ ! -e "$f" ]; then printf "covfix-missing %s\\n" "$f"; '
                   'elif ! sha256sum -- "$f"; then printf "covfix-unreadable %s\\n" "$f"; fi; done; '
                   f'echo {HASH_END}')

    def hash_files(self, root: str, rels):
        """(sha256 per relpath under root, set of relpaths that do not exist), computed on the cluster.
        Anything short of a complete, accounted-for answer is the link or the environment: REFUSED."""
        remote = f"cd -- {shlex.quote(root)} || exit {ROOT_MISSING_RC}; bash -c {shlex.quote(self.HASH_SCRIPT)}"
        r = subprocess.run([*self.ssh_argv, self.host, remote], input=b"".join(x.encode() + b"\0" for x in rels),
                           capture_output=True)
        if r.returncode == ROOT_MISSING_RC:
            raise Stop(REFUSED, f"remote root {root} does not exist; nothing spent")
        lines = r.stdout.decode("ascii", errors="replace").splitlines()
        if r.returncode != 0 or not lines or lines[-1] != HASH_END:
            raise Stop(REFUSED, f"hashing on {self.host} did not complete (rc {r.returncode}); nothing spent")
        got, missing, unreadable = {}, set(), set()
        for line in lines[:-1]:
            m = SUMLINE.fullmatch(line)
            if m:
                got[m.group(2)] = m.group(1)
            elif line.startswith("covfix-missing "):
                missing.add(line[len("covfix-missing "):])
            elif line.startswith("covfix-unreadable "):
                unreadable.add(line[len("covfix-unreadable "):])
        unaccounted = [x for x in rels if x not in got and x not in missing]
        if unreadable or unaccounted:
            raise Stop(REFUSED, f"hashing on {self.host}: {len(unreadable)} unreadable, {len(unaccounted)} "
                                "unaccounted path(s); nothing spent")
        return got, missing

    def launch(self, command: str, frame: bytearray) -> int:
        # Unbuffered, so the frame goes to the pipe in os.write calls here and no flush at close can fail.
        p = subprocess.Popen([*self.ssh_argv, self.host, command], stdin=subprocess.PIPE, bufsize=0)
        try:
            try:
                view = memoryview(frame)
                while view:
                    view = view[p.stdin.write(view):]
                view.release()
            except BrokenPipeError:
                pass            # the binary exited without reading; its exit status decides
            finally:
                for i in range(len(frame)):
                    frame[i] = 0
                p.stdin.close()
            return p.wait()
        except BaseException:
            p.kill()
            p.wait()
            raise


# ----------------------------------------------------------------------------------------------------------
# ST4's consumption record
# ----------------------------------------------------------------------------------------------------------

class Record:
    """Append-only, hash-chained JSON lines in a mode-700 directory, plus O_EXCL markers for uncertain spends."""

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

    def marker(self, key: str, role: str) -> str:
        return os.path.join(self.dir, f"UNCERTAIN-{key[:12]}-{role}")

    def mark_uncertain(self, key: str, role: str) -> None:
        try:
            fd = os.open(self.marker(key, role), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(fd, f"{key} {role} {utc_now()}\n".encode())
            os.fsync(fd)
            os.close(fd)
            dfd = os.open(self.dir, os.O_RDONLY)
            os.fsync(dfd)
            os.close(dfd)
        except FileExistsError:
            pass

    def markers(self) -> list:
        out = []
        for name in sorted(os.listdir(self.dir)):
            if name.startswith("UNCERTAIN-"):
                with open(os.path.join(self.dir, name)) as f:
                    fields = f.read().split()
                if len(fields) < 2 or not HEX64.fullmatch(fields[0]):
                    raise Stop(TERMINAL, f"uncertain marker {name} is unreadable")
                out.append((fields[0], fields[1]))
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
        dfd = os.open(self.dir, os.O_RDONLY)
        os.fsync(dfd)
        os.close(dfd)
        return self.raw()

    def absorb_markers(self) -> None:
        """Under the lock: turn each uncertain marker into a record line, so it reaches the chain and the mirror."""
        recorded = {(e["key"], e["role"]) for e in self.lines() if e["event"] == "uncertain"}
        for key, role in self.markers():
            if (key, role) not in recorded:
                self.append({"event": "uncertain", "key": key, "role": role, "detail": "from marker"})


def blocked(events, key: str, role: str):
    """Why (key, role) may not be spent, or None. Any line for the pair blocks it; a break blocks every role."""
    for e in events:
        if e["key"] == key and (e["role"] == role or e["event"] == "break"):
            return f"record line seq {e.get('seq')}: {e['event']} {e['role']}"
    return None


def bound_freeze(events, key: str):
    for e in events:
        if e["key"] == key and e.get("freeze"):
            return e["freeze"]
    return None


# ----------------------------------------------------------------------------------------------------------
# The mirror: one path, committed and pushed on a dedicated branch of a git worktree
# ----------------------------------------------------------------------------------------------------------

class Mirror:
    def __init__(self, cfg: dict):
        try:
            self.wt = os.path.expanduser(cfg["worktree"])
            self.rel = cfg["path"]
            self.remote = cfg["remote"]
            self.branch = cfg["branch"]
        except KeyError as e:
            raise Stop(ERROR, f"mirror config lacks {e}")
        self.hooks = bool(cfg.get("run_hooks", False))
        self.ident = ["-c", "user.name=director", "-c", "user.email=director@minerva-omnifold.invalid"]

    def git(self, *args, check=True, input=None):
        r = subprocess.run(["git", "-C", self.wt, *args], capture_output=True, input=input)
        if check and r.returncode != 0:
            raise Stop(REFUSED, f"git {' '.join(args[:2])} failed: {r.stderr.decode(errors='replace').strip()[-300:]}")
        return r

    @property
    def tracking(self) -> str:
        return f"refs/remotes/{self.remote}/{self.branch}"

    def preflight(self) -> None:
        head = self.git("symbolic-ref", "--short", "HEAD").stdout.decode().strip()
        if head != self.branch:
            raise Stop(REFUSED, f"mirror worktree is on {head!r}, not {self.branch!r}")
        if self.git("status", "--porcelain", "--", self.rel).stdout.strip():
            raise Stop(REFUSED, f"mirror path {self.rel} has uncommitted changes")

    def fetch(self) -> bytes | None:
        """Fetch the branch; return its mirrored record bytes, or None if the branch or the path does not exist."""
        ls = self.git("ls-remote", "--heads", self.remote, self.branch).stdout.strip()
        if not ls:
            return None
        self.git("fetch", "-q", self.remote, f"+refs/heads/{self.branch}:{self.tracking}")
        r = self.git("cat-file", "blob", f"{self.tracking}:{self.rel}", check=False)
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

    def publish(self, data: bytes, message: str) -> None:
        """Commit the record bytes, push, refetch, and require the remote blob to equal them."""
        dest = os.path.join(self.wt, self.rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        self.git("add", "--", self.rel)
        hooks = [] if self.hooks else ["-c", "core.hooksPath=/dev/null"]
        self.git(*hooks, *self.ident, "commit", "-q", "-m", message, "--", self.rel)
        self.git("push", "-q", self.remote, f"HEAD:refs/heads/{self.branch}")
        if self.fetch() is None or \
                self.git("rev-parse", f"{self.tracking}:{self.rel}").stdout.decode().strip() != git_blob_sha(data):
            raise Stop(TERMINAL, "the pushed mirror's blob does not equal the local record")


# ----------------------------------------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------------------------------------

def load_config(path: str, pinned: str) -> dict:
    with open(path, "rb") as f:
        data = f.read()
    if sha256_bytes(data) != check_hex64(pinned, "pinned config sha256"):
        raise Stop(REFUSED, "the role config's sha256 is not the pinned one")
    cfg = json.loads(data)
    for k in ("record_dir", "keychain_prefix", "ssh", "host", "mirror", "roles"):
        if k not in cfg:
            raise Stop(ERROR, f"role config lacks {k!r}")
    return cfg


class Context:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.record = Record(cfg["record_dir"])
        self.mirror = Mirror(cfg["mirror"])
        self.cluster = Cluster(cfg["ssh"], cfg["host"])
        self.kc = Keychain(cfg["keychain_prefix"], cfg.get("security", SECURITY))

    def check_mirror(self, events) -> None:
        """The mirror must be a prefix of the local record, and no version in its history may hold a line the
        local record lacks (a restored older copy)."""
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

    def commit_event(self, event: dict, message: str) -> None:
        """Lock, append, fsync, commit, push, verify. Any failure leaves an uncertain marker and is terminal."""
        key, role = event["key"], event["role"]
        try:
            self.record.lock()
        except OSError as e:
            self.record.mark_uncertain(key, role)
            raise Stop(TERMINAL, f"cannot take the record lock ({e}); {role} is now blocked as uncertain")
        try:
            self.record.absorb_markers()
            if event["event"] == "spent":
                why = blocked(self.record.lines(), key, role)
                if why:
                    raise Consumed(f"{role} for {key[:12]} is already consumed ({why})")
            data = self.record.append(event)
            self.mirror.publish(data, message)
        except Consumed:
            raise
        except Exception as e:
            self.record.mark_uncertain(key, role)
            raise Stop(TERMINAL, f"uncertain {event['event']} ({type(e).__name__}: {e}); "
                                 f"{role} for {key[:12]} is blocked")
        finally:
            self.record.unlock()


# ----------------------------------------------------------------------------------------------------------
# run
# ----------------------------------------------------------------------------------------------------------

def verify_list(ctx: Context, sumfile: str, digest: str, root: str, what: str, key: str, role: str) -> None:
    with open(os.path.expanduser(sumfile), "rb") as f:
        data = f.read()
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
    try:
        ctx.commit_event({"event": "break", "key": key, "role": role, "detail": detail},
                         f"[record] covfix: BREAK {key[:12]} ({role})")
    except Stop as e:
        detail += f"; and recording the break failed: {e}"
    raise Stop(TERMINAL, f"BREAK: {detail}")


def run_role(ctx: Context, role: str, seal_digest, freeze_digest, commitment) -> int:
    kind, frame_has_seed = ROLES[role]
    rcfg = ctx.cfg["roles"].get(role)
    if not rcfg:
        raise Stop(ERROR, f"the role config has no entry for {role}")
    ctx.record.ensure_dir()

    if kind == "seal":
        key = check_hex64(seal_digest or "", "seal digest")
        freeze = check_hex64(freeze_digest or "", "freeze digest")
    else:
        key = check_hex64(commitment or "", "commitment")
        freeze = None

    # 1. The record and its mirror, before anything else: a consumed role refuses without touching the cluster.
    events = ctx.record.lines()
    ctx.check_mirror(events)
    why = blocked(events, key, role)
    if why or os.path.exists(ctx.record.marker(key, role)):
        raise Consumed(f"{role} for {key[:12]} is already consumed ({why or 'uncertain marker'})")
    if freeze:
        bound = bound_freeze(events, key)
        if bound and bound != freeze:
            raise Stop(REFUSED, f"seal {key[:12]} is bound to freeze {bound[:12]}, not {freeze[:12]}")

    # 2. The secrets, read and checked before the spend so a Keychain failure burns nothing.
    passphrase = check_hex64(ctx.kc.read("passphrase"), "passphrase")
    frame = bytearray(passphrase.encode("ascii") + b"\n")
    if frame_has_seed:
        seed_base = parse_seed_base(ctx.kc.read("seed-base"))
        if commitment_digest(seed_base, check_hex64(ctx.kc.read("salt"), "salt")) != key:
            raise Stop(REFUSED, "the Keychain seed base and salt do not reproduce the published commitment")
        frame += str(seed_base).encode("ascii") + b"\n"

    # 3. The bound binary, then the seal and the freeze, hashed on the cluster.
    binary, want_bin = rcfg["binary"], check_hex64(rcfg["binary_sha256"], "binary sha256")
    got_bin, _ = ctx.cluster.hash_files(os.path.dirname(binary) or "/", [os.path.basename(binary)])
    if got_bin.get(os.path.basename(binary)) != want_bin:
        raise Stop(REFUSED, f"the bound binary {binary} does not hash to the pinned sha256; nothing spent")
    if kind == "seal":
        verify_list(ctx, ctx.cfg["seal_file"], key, ctx.cfg["seal_root"], "PG-SEAL.sha256", key, role)
        verify_list(ctx, ctx.cfg["freeze_file"], freeze, ctx.cfg["freeze_root"], "P2-FREEZE.sha256", key, role)

    # 4. The spend: durable (fsync, commit, push, remote blob verified) before any plaintext can exist.
    spent = {"event": "spent", "key": key, "role": role, "binary_sha256": want_bin}
    if freeze:
        spent["freeze"] = freeze
    ctx.commit_event(spent, f"[record] covfix: spent {role} {key[:12]}")

    # 5. The launch. A crash or a dropped link after this point is terminal for the role; there is no retry.
    try:
        rc = ctx.cluster.launch(rcfg["command"], frame)
    except BaseException as e:
        rc = f"interrupted ({type(e).__name__})"
    outcome = "completed" if rc == 0 else "terminal"
    try:
        ctx.commit_event({"event": outcome, "key": key, "role": role, "detail": f"rc {rc}"},
                         f"[record] covfix: {outcome} {role} {key[:12]}")
    except Stop as e:
        print(f"covfix: {role} {outcome} (rc {rc}), but its outcome line was not mirrored: {e}", file=sys.stderr)
        return TERMINAL
    print(f"covfix: {role} {outcome} (rc {rc})")
    return OK if rc == 0 else TERMINAL


# ----------------------------------------------------------------------------------------------------------
# reveal
# ----------------------------------------------------------------------------------------------------------

def reveal(ctx: Context, seal_digest: str, commitment: str, after_stop) -> int:
    ctx.record.ensure_dir()
    key = check_hex64(seal_digest or "", "seal digest")
    check_hex64(commitment or "", "commitment")
    events = ctx.record.lines()
    ctx.check_mirror(events)
    done = [e for e in events if e["key"] == key and e["role"] == "pv-readout"
            and e["event"] in ("completed", "terminal")]
    if not done and not (after_stop or "").strip():
        raise Stop(REFUSED, "PV's readout has no outcome line for this seal; reveal needs --after-stop '<stop>'")
    seed_base = parse_seed_base(ctx.kc.read("seed-base"))
    salt = check_hex64(ctx.kc.read("salt"), "salt")
    if commitment_digest(seed_base, salt) != commitment:
        raise Stop(TERMINAL, "the Keychain seed base and salt do not reproduce the published commitment")
    ctx.commit_event({"event": "reveal", "key": key, "role": "reveal",
                      "detail": f"after {done[-1]['event']} readout" if done else f"after stop: {after_stop}"},
                     f"[record] covfix: reveal for {key[:12]}")
    print(f"seed_base={seed_base}")
    print(f"salt={salt}")
    return OK


# ----------------------------------------------------------------------------------------------------------
# synthetic-seal
# ----------------------------------------------------------------------------------------------------------

def synthetic_seal(kc: Keychain, out: str, gpg: str = "gpg") -> dict:
    """A dummy truth sealed exactly as PG seals products: a ciphertext per product, an encrypted manifest of
    plaintext sha256s, a decrypt round trip, the plaintext deleted, PG-SEAL.sha256 over the ciphertexts, and a
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
