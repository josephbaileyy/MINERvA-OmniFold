"""COVFIX PG's generic seal (COVFIX-DECLARATION.md rev 11.4 section 4.2; COVFIX-BINDING-1 ruling 4: cov2d writes PG's
capture, encryption, seal check and content scan). Library; the bound binary is covfix_pg.py, the check covfix_sealcheck.py.

  read_frame        the fixed stdin frame, exact length: PG "<64 hex>\\n<10-digit seed base>\\n" (76 bytes), PV
                    "<64 hex>\\n" (65 bytes); anything else is refused
  task_seeds        base + 10_000 u + i for i < N_TASKS; a computed seed at or above 2^31 - 1 is refused
  Tools             absolute paths of gpg and gpgconf, checked to be executable regular files
  gpg_run           the declared gpg argv, run from Tools' absolute path with a minimal environment; the passphrase on
                    fd 3 through an internal pipe; exactly fds 0-3 open in gpg (pass_fds); core dumps off; a fresh
                    throwaway GNUPGHOME per call, short and node-local (/dev/shm, else /tmp; never under $SCRATCH),
                    under 80 characters, mode 700, guarded from creation: gpg-agent is killed with it and the directory
                    removed, and a removal that cannot be confirmed is a role failure. ~/.gnupg is never touched.
                    stdout is returned only after gpg exited 0 (a non-zero exit, such as an MDC failure, is a refusal).
                    Encryption is uncompressed (--compress-algo none), so a ciphertext's size is its plaintext's plus
                    a constant: a fixed-width seed in a status or log text does not change it
  seal              section 4.2 steps 1-3 and 6's file: plaintext sha256 of every file under the work dir (O_NOATIME
                    where the platform has it), each encrypted to <sealed>/<id>.gpg under an opaque id (p0001, p0002,
                    ...) assigned over a CSPRNG permutation of the relpaths (assign_ids), so an id's position says
                    nothing about its relpath, which can carry a seed; the encrypted manifest PG-MANIFEST.json.gpg =
                    {"products": {id: plaintext sha256}, "paths": {id: relpath}}, a decrypt-and-hash round trip of
                    every product and the manifest, and the public PG-SEAL.sha256 (ciphertext sha256 by id). No work-dir
                    relpath is published.
  delete_plaintext  step 4, and the failure trap (never follows a link)
  content_scan      step 5: every regular file under the enumerated paths (or the path itself, if a file), hashed,
                    against the plaintext list; links and special files are not followed; a walk error refuses
  parse_seal /      the canonical sealed set: exactly p0001..pN.gpg and PG-MANIFEST.json.gpg, N >= 1; the check
  seal_check        compares every entry of the sealed dir (any name, PG-SEAL.sha256 excepted) with no decryption,
                    and reports only opaque names and counts
  read_ciphertext / the reader side: a ciphertext opened without following links (regular files only), read once, and
  open_manifest /   checked against PG-SEAL.sha256 BEFORE any decryption. A missing listed file or different bytes is a
  read_product      Break; any other open or read error is a role failure. The manifest's full schema is checked
                    (dicts, 64-hex hashes, safe relpaths, no duplicate keys, ids equal to the seal's). A request for an
                    id the manifest does not list is a role failure, not a break. open_manifest returns a
                    SealedManifest: its paths and hashes are seed-bearing, so it shows counts only, cannot be pickled,
                    copied or dumped, and is read through ids(), path(id) and sha256(id); read_product takes only it.
  publish_guard     the decryptor's side of the seed-bearing rulings: PV's writers pass every output through it, and
                    it refuses the exact seeds in any form, a manifest relpath's digit runs and any manifest hash

The plaintext hashes never leave memory except inside the encrypted manifest. Nothing here prints, and no message
names a work-dir entry.
MEASURES: nothing. CANNOT AUTHORIZE: a connect, a seal's acceptance, or any reading of sealed content.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import resource
import secrets
import shutil
import signal
import stat
import subprocess
import tempfile
from pathlib import Path

GPG_ENCRYPT = ("gpg", "--batch", "--yes", "--pinentry-mode", "loopback", "--passphrase-fd", "3", "--no-symkey-cache",
               "--symmetric", "--cipher-algo", "AES256", "--s2k-digest-algo", "SHA512", "--force-mdc",
               "--compress-algo", "none")
GPG_DECRYPT = ("gpg", "--batch", "--pinentry-mode", "loopback", "--passphrase-fd", "3", "--no-symkey-cache", "--decrypt")
BREAK_RC = 66
SEED_BASE_LO, SEED_BASE_HI = 1_000_000_000, 2_000_000_000      # [lo, hi): always 10 digits
SEED_LIMIT = 2 ** 31 - 1                                         # a computed seed must be below this
N_TASKS = 7                                                      # FD-F1-DECLARATION-AMENDMENT-2: 7 tasks per tune
U_STRIDE = 10_000
MANIFEST = "PG-MANIFEST.json"
MANIFEST_CT = MANIFEST + ".gpg"
SEAL_FILE = "PG-SEAL.sha256"
MAX_PRODUCTS = 9999
NOATIME = getattr(os, "O_NOATIME", 0)
NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
PG_FRAME_LEN, PV_FRAME_LEN = 76, 65
_PG_FRAME = re.compile(rb"([0-9a-f]{64})\n([1-9][0-9]{9})\n")
_PV_FRAME = re.compile(rb"([0-9a-f]{64})\n")
ID = re.compile(r"p[0-9]{4}")
HEX64 = re.compile(r"[0-9a-f]{64}")
GNUPG_HOME_MAX = 80
GPG_ENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C"}


class Refusal(Exception):
    """A role-terminal refusal: this run stops, and no receipt is printed."""


class Break(Exception):
    """A confirmed integrity break: the sealed set disagrees with its seal or its manifest."""


def _raise(e: OSError):
    raise Refusal(f"a directory walk failed ({type(e).__name__})") from e


# ------------------------------------------------------------------------------------------------ frame and seeds
def read_frame(data: bytes, with_seed: bool) -> tuple[str, int | None]:
    want = PG_FRAME_LEN if with_seed else PV_FRAME_LEN
    m = (_PG_FRAME if with_seed else _PV_FRAME).fullmatch(data) if len(data) == want else None
    if not m:
        raise Refusal("the stdin frame is malformed")
    seed = int(m.group(2)) if with_seed else None
    if with_seed and not SEED_BASE_LO <= seed < SEED_BASE_HI:
        raise Refusal("the seed base is outside [1e9, 2e9)")
    return m.group(1).decode("ascii"), seed


def task_seeds(base: int, tunes: list[str]) -> dict:
    """{"tunes": [{"u", "name", "task_seeds"}]}, u in list order; refused if any seed reaches 2^31 - 1."""
    out = []
    for u, name in enumerate(tunes):
        seeds = [base + U_STRIDE * u + i for i in range(N_TASKS)]
        if max(seeds) >= SEED_LIMIT:
            raise Refusal("a computed task seed is at or above 2^31 - 1")
        out.append({"u": u, "name": name, "task_seeds": seeds})
    return {"tunes": out}


# --------------------------------------------------------------------------------------------------------- gpg
class Tools:
    """gpg and gpgconf, pinned by sha256 in PG's binding (the director's ruling R1). Each path must be absolute, fully
    resolved (no link) and an executable regular file. Each binary is hashed through a file descriptor opened without
    following a link, at construction and again immediately before every exec; a mismatch is a STOP and a rebinding,
    never a fallback. RESIDUAL WINDOW (disclosed): the exec is by path, after the hash, so a write by this same account
    between the two would not be seen; section 4.2's cooperative assumption covers that account."""

    def __init__(self, gpg: str, gpgconf: str, gpg_sha256: str, gpgconf_sha256: str):
        for p in (gpg, gpgconf):
            if not os.path.isabs(p) or os.path.realpath(p) != p or not os.path.isfile(p) or not os.access(p, os.X_OK):
                raise Refusal("gpg and gpgconf must be absolute, resolved paths of executable files")
        for h in (gpg_sha256, gpgconf_sha256):
            if not (isinstance(h, str) and HEX64.fullmatch(h)):
                raise Refusal("gpg's and gpgconf's pins must be 64 lowercase hex")
        self.gpg, self.gpgconf = gpg, gpgconf
        self.pins = {gpg: gpg_sha256, gpgconf: gpgconf_sha256} if gpg != gpgconf else None
        if self.pins is None:
            raise Refusal("gpg and gpgconf must be different files")
        self.verify(gpg)
        self.verify(gpgconf)

    def verify(self, path: str) -> str:
        try:
            fd = os.open(path, os.O_RDONLY | NOFOLLOW)
            try:
                h = hashlib.sha256(_read_fd(fd)).hexdigest()
            finally:
                os.close(fd)
        except OSError as e:
            raise Refusal("gpg or gpgconf cannot be read") from e
        if h != self.pins[path]:
            raise Refusal("gpg or gpgconf is not its pinned sha256 (a STOP and a rebinding)")
        return path


def _inside(path: str, root: str) -> bool:
    path, root = os.path.realpath(path), os.path.realpath(root)
    return path == root or path.startswith(root.rstrip("/") + "/")


def new_gnupg_home() -> str:
    """A fresh, empty, mode-700 GNUPGHOME on a short node-local path (gpg-agent's socket path must stay short), never
    under $SCRATCH."""
    root = "/dev/shm" if os.path.isdir("/dev/shm") else "/tmp"
    scratch = os.environ.get("SCRATCH")
    if scratch and _inside(root, scratch):
        raise Refusal("the GNUPGHOME root is under $SCRATCH")
    home = tempfile.mkdtemp(prefix="cfx", dir=root)
    try:
        os.chmod(home, 0o700)
        if len(home) >= GNUPG_HOME_MAX:
            raise Refusal("the GNUPGHOME path is not short")
    except BaseException:
        shutil.rmtree(home, ignore_errors=True)
        if os.path.lexists(home):
            raise Refusal("the GNUPGHOME could not be removed")
        raise
    return home


def _child_fd3(r: int):
    def child():
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        if r != 3:
            os.dup2(r, 3)
        else:
            os.set_inheritable(3, True)
    return child


GPGCONF_TIMEOUT_S = 10
SIGTERM_HOLD_BOUND_S = 15      # a held SIGTERM waits for: gpg's SIGKILL, gpgconf (at most GPGCONF_TIMEOUT_S) and the
                               # home's removal; below Slurm's default KillWait (30 s) before its SIGKILL


def gpg_run(argv: tuple, passphrase: str, payload: bytes, tools: Tools) -> bytes:
    """Run gpg with the declared argv; the passphrase reaches it on fd 3 only. Raises Refusal on a non-zero exit or
    on a GNUPGHOME whose removal cannot be confirmed. A SIGTERM that arrives meanwhile is held: gpg is SIGKILLed at
    once (or as soon as it starts), the agent and the home are cleaned up (gpgconf bounded by GPGCONF_TIMEOUT_S),
    and the SIGTERM is then delivered to the previous handler. The hold is bounded (SIGTERM_HOLD_BOUND_S)."""
    hold: dict | None = {"pending": [], "child": None}

    def record(signum, frame):
        hold["pending"].append(signum)
        if hold["child"] is not None:
            _kill(hold["child"])

    try:
        old = signal.signal(signal.SIGTERM, record)
    except ValueError:                                 # not the main thread: no handler to hold it
        old, hold = None, None
    try:
        return _gpg_run(argv, passphrase, payload, tools, hold)
    finally:
        if old is not None:
            signal.signal(signal.SIGTERM, old)
            if hold["pending"]:
                if callable(old):
                    old(signal.SIGTERM, None)
                elif old == signal.SIG_DFL:
                    os.kill(os.getpid(), signal.SIGTERM)


def _kill(p: subprocess.Popen) -> None:
    try:
        p.kill()
    except OSError:
        pass


def _gpg_run(argv: tuple, passphrase: str, payload: bytes, tools: Tools, hold: dict | None = None) -> bytes:
    home = new_gnupg_home()
    env = dict(GPG_ENV, GNUPGHOME=home)
    rc = None
    try:
        r, w = os.pipe()
        try:
            try:
                os.write(w, passphrase.encode("ascii") + b"\n")
            finally:
                os.close(w)
            p = subprocess.Popen([tools.verify(tools.gpg), *argv[1:]], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, close_fds=True, pass_fds=(3,), preexec_fn=_child_fd3(r),
                                 env=env)
            if hold is not None:
                hold["child"] = p
                if hold["pending"]:                    # a SIGTERM held before gpg started
                    _kill(p)
        finally:
            os.close(r)
        out, _err = p.communicate(payload)
        rc = p.returncode
    finally:
        agent_down = False
        try:
            try:
                agent_down = subprocess.run([tools.verify(tools.gpgconf), "--homedir", home, "--kill", "gpg-agent"],
                                            capture_output=True, env=env, timeout=GPGCONF_TIMEOUT_S).returncode == 0
            except (OSError, subprocess.SubprocessError, Refusal):
                pass
        finally:                                       # the home goes whatever the agent shutdown raised
            shutil.rmtree(home, ignore_errors=True)
        if os.path.lexists(home):
            raise Refusal("the GNUPGHOME could not be removed")
        if not agent_down:
            raise Refusal("the gpg-agent shutdown could not be confirmed")
    if rc != 0:
        raise Refusal(f"gpg exited {rc}")
    return out


# ------------------------------------------------------------------------------------------------- files
def _read_fd(fd: int) -> bytes:
    chunks = []
    while True:
        b = os.read(fd, 1 << 24)
        if not b:
            break
        chunks.append(b)
    return b"".join(chunks)


def noatime_read(path: Path) -> bytes:
    fd = os.open(str(path), os.O_RDONLY | NOATIME)
    try:
        return _read_fd(fd)
    finally:
        os.close(fd)


def regular_read(path: Path) -> bytes:
    """Open without following a link (O_NOFOLLOW), require a regular file, read once (O_NOATIME where available)."""
    fd = os.open(str(path), os.O_RDONLY | NOATIME | NOFOLLOW)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise Refusal("a sealed entry is not a regular file")
        return _read_fd(fd)
    finally:
        os.close(fd)


def enumerate_files(root: Path) -> list[str]:
    """Sorted relative paths of the regular files under root. A symlink or a special file is refused: it could name
    bytes outside the tree. A walk error refuses."""
    root = Path(root)
    out = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False, onerror=_raise):
        for name in dirnames + filenames:
            st = os.lstat(os.path.join(dirpath, name))
            if stat.S_ISLNK(st.st_mode) or not (stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)):
                raise Refusal("a non-regular entry (symlink or special file) in a sealed tree")
        out += [os.path.relpath(os.path.join(dirpath, f), root) for f in filenames]
    return sorted(out)


def _write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "xb") as f:
        f.write(data)


# ------------------------------------------------------------------------------------------------------- seal
def product_ids(n: int) -> list[str]:
    if n > MAX_PRODUCTS:
        raise Refusal(f"more than {MAX_PRODUCTS} products")
    return [f"p{i:04d}" for i in range(1, n + 1)]


_RNG = secrets.SystemRandom()


def assign_ids(rels: list[str]) -> dict[str, str]:
    """{id: relpath}, the ids p0001..pN over a CSPRNG permutation of the relpaths. Sorted relpaths can carry seed
    digits (gevgen names its outputs by the seed), and the ciphertext sizes by id are public. The mapping is written
    only into the encrypted manifest."""
    order = list(rels)
    _RNG.shuffle(order)
    return dict(zip(product_ids(len(order)), order))


def seal(workdir: Path, sealed: Path, passphrase: str, tools: Tools) -> dict:
    """Section 4.2 steps 1-3 and 6's file. Returns {"hashes": {id: plaintext sha256}, "n_products", "seal_text"};
    the hashes are for the content scan only and are never written in plaintext. Raises Break on a round-trip
    mismatch."""
    workdir, sealed = Path(workdir), Path(sealed)
    rels = enumerate_files(workdir)
    if not rels:
        raise Refusal("the work dir holds no file to seal")
    assigned = assign_ids(rels)
    hashes, paths, cipher = {}, {}, {}
    for pid, rel in assigned.items():
        plain = noatime_read(workdir / rel)
        hashes[pid], paths[pid] = hashlib.sha256(plain).hexdigest(), rel
        ct = gpg_run(GPG_ENCRYPT, passphrase, plain, tools)
        _write_new(sealed / (pid + ".gpg"), ct)
        cipher[pid + ".gpg"] = hashlib.sha256(ct).hexdigest()
        del plain
    man_plain = json.dumps({"products": hashes, "paths": paths}, sort_keys=True).encode()
    man_ct = gpg_run(GPG_ENCRYPT, passphrase, man_plain, tools)
    _write_new(sealed / MANIFEST_CT, man_ct)
    cipher[MANIFEST_CT] = hashlib.sha256(man_ct).hexdigest()
    for pid in assigned:                             # step 3: the round trip, from the bytes on disk
        back = gpg_run(GPG_DECRYPT, passphrase, regular_read(sealed / (pid + ".gpg")), tools)
        if hashlib.sha256(back).hexdigest() != hashes[pid]:
            raise Break(f"{pid} does not reproduce its plaintext sha256")
        del back
    back = gpg_run(GPG_DECRYPT, passphrase, regular_read(sealed / MANIFEST_CT), tools)
    if back != man_plain:
        raise Break("the manifest does not reproduce itself")
    seal_text = "".join(f"{h}  {name}\n" for name, h in sorted(cipher.items()))
    _write_new(sealed / SEAL_FILE, seal_text.encode())
    return {"hashes": hashes, "n_products": len(rels), "seal_text": seal_text}


def delete_plaintext(workdir: Path) -> int:
    """Step 4, and the failure trap: unlink every non-directory entry under the work dir (files, and any symlink or
    special entry, never followed), then remove its subdirectories deepest first; returns the count unlinked."""
    workdir = Path(workdir)
    n = 0
    for dirpath, dirnames, filenames in os.walk(workdir, topdown=False, followlinks=False, onerror=_raise):
        for name in filenames:
            os.unlink(os.path.join(dirpath, name))
            n += 1
        for name in dirnames:
            p = os.path.join(dirpath, name)
            if os.path.islink(p):
                os.unlink(p)
                n += 1
            else:
                os.rmdir(p)
    return n


def _regular_files(root: Path):
    st = os.lstat(root)
    if stat.S_ISREG(st.st_mode):
        yield root
        return
    if not stat.S_ISDIR(st.st_mode):
        return
    for dirpath, _, filenames in os.walk(root, followlinks=False, onerror=_raise):
        for name in filenames:
            p = Path(dirpath) / name
            if stat.S_ISREG(os.lstat(p).st_mode):
                yield p


def content_scan(paths: list[Path], plaintext_hashes: set[str]) -> list[str]:
    """Step 5: every regular file under each enumerated path (or the path itself, if it is a file) whose sha256 is a
    plaintext hash. A missing path is skipped; links and special files are not followed; a walk error refuses."""
    hits = []
    for root in paths:
        root = Path(root)
        if not os.path.lexists(root):
            continue
        for p in _regular_files(root):
            if hashlib.sha256(noatime_read(p)).hexdigest() in plaintext_hashes:
                hits.append(str(p))
    return hits


# ------------------------------------------------------------------------------------------------- seal check
def parse_seal(text: str) -> dict:
    """The canonical PG-SEAL.sha256: one "<64 hex>  <name>" line per entry, the names exactly p0001..pN.gpg (N >= 1)
    and PG-MANIFEST.json.gpg."""
    out = {}
    for line in text.splitlines():
        m = re.fullmatch(r"([0-9a-f]{64})  (\S+)", line)
        if not m or m.group(2) in out:
            raise Refusal(f"a malformed or repeated {SEAL_FILE} line")
        out[m.group(2)] = m.group(1)
    ids = sorted(k[:-4] for k in out if k != MANIFEST_CT)
    if MANIFEST_CT not in out or not ids or ids != product_ids(len(ids)) or \
            any(not (k == MANIFEST_CT or (k.endswith(".gpg") and ID.fullmatch(k[:-4]))) for k in out):
        raise Refusal(f"{SEAL_FILE} is not a canonical set (p0001..pN.gpg and the manifest)")
    return out


def _public(names) -> list[str]:
    return sorted(n for n in names if n == MANIFEST_CT or (n.endswith(".gpg") and ID.fullmatch(n[:-4])))


def seal_check(sealed: Path, seal_text: str) -> dict:
    """The sealed dir against a canonical seal, with no decryption: its own PG-SEAL.sha256 must be a regular file with
    exactly seal_text's bytes; every other root entry must be a regular file of the set, with its listed bytes. The dir
    is flat: a subdirectory, link or special entry is an extra. Only opaque names are reported; other extras are
    counted."""
    want = parse_seal(seal_text)
    sealed = Path(sealed)
    regular, other = set(), 0
    for name in os.listdir(sealed):
        if stat.S_ISREG(os.lstat(sealed / name).st_mode):
            regular.add(name)
        else:
            other += 1
    index_ok = SEAL_FILE in regular and regular_read(sealed / SEAL_FILE) == seal_text.encode("ascii")
    have = regular - {SEAL_FILE}
    missing = sorted(set(want) - have)
    extra = have - set(want)
    mismatched = sorted(r for r in set(want) & have if hashlib.sha256(regular_read(sealed / r)).hexdigest() != want[r])
    return {"ok": index_ok and not (missing or extra or mismatched or other), "index_ok": index_ok,
            "missing": missing, "extra": _public(extra), "extra_other": len(extra) - len(_public(extra)) + other,
            "mismatched": mismatched, "n": len(want)}


# ------------------------------------------------------------------------------------------------- reader side
def _read_in_dir(root: Path, name: str) -> bytes:
    """Open name relative to a directory descriptor of root (root itself not a link), never following a link, and
    read it once as a regular file."""
    dfd = os.open(str(root), os.O_RDONLY | os.O_DIRECTORY | NOFOLLOW)
    try:
        fd = os.open(name, os.O_RDONLY | NOATIME | NOFOLLOW, dir_fd=dfd)
    finally:
        os.close(dfd)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise Refusal("a sealed entry is not a regular file")
        return _read_fd(fd)
    finally:
        os.close(fd)


def read_ciphertext(seal_root: Path, seal_map: dict, name: str) -> bytes:
    if name not in seal_map or not (name == MANIFEST_CT or (name.endswith(".gpg") and ID.fullmatch(name[:-4]))):
        raise Refusal("a requested name is not in the seal")
    try:
        data = _read_in_dir(Path(seal_root), name)
    except FileNotFoundError as e:
        raise Break("a sealed ciphertext is missing") from e
    except OSError as e:
        raise Refusal(f"a sealed ciphertext cannot be read ({type(e).__name__})") from e
    if hashlib.sha256(data).hexdigest() != seal_map[name]:
        raise Break("a ciphertext is not its PG-SEAL sha256")
    return data


def _no_dup_pairs(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError("a duplicate key")
        d[k] = v
    return d


def _safe_rel(p) -> bool:
    return (isinstance(p, str) and p not in ("", ".") and not p.startswith("/") and "\x00" not in p
            and os.path.normpath(p) == p and ".." not in p.split("/"))


class SealedManifest:
    """The decrypted PG manifest, as open_manifest returns it. Its paths and plaintext hashes are seed-bearing: gevgen
    names its outputs by the seed, and the seed space can be searched against a seed-bearing file's hash (the
    director's rulings of 2026-11-25). So it never shows them: repr and str give counts only; pickling, copying,
    json.dumps, subscripting, iteration and vars() raise TypeError; it is read-only. Access is explicit: ids(),
    path(id) and sha256(id)."""
    __slots__ = ("_products", "_paths")

    def __init__(self, products: dict, paths: dict):
        object.__setattr__(self, "_products", dict(products))
        object.__setattr__(self, "_paths", dict(paths))

    def __setattr__(self, name, value):
        raise AttributeError("a SealedManifest is read-only")

    def __delattr__(self, name):
        raise AttributeError("a SealedManifest is read-only")

    def __reduce_ex__(self, protocol):
        raise TypeError("a SealedManifest is seed-bearing: it cannot be pickled or copied")

    def __repr__(self) -> str:
        return f"<SealedManifest: {len(self._products)} products>"

    __str__ = __repr__

    def __len__(self) -> int:
        return len(self._products)

    def __contains__(self, pid) -> bool:
        return pid in self._products

    def ids(self) -> list[str]:
        return sorted(self._products)

    def _known(self, pid: str) -> None:
        if pid not in self._products:
            raise Refusal("a requested id is not in the manifest")

    def path(self, pid: str) -> str:
        self._known(pid)
        return self._paths[pid]

    def sha256(self, pid: str) -> str:
        self._known(pid)
        return self._products[pid]


def open_manifest(seal_root: Path, seal_map: dict, passphrase: str, tools: Tools) -> SealedManifest:
    ct = read_ciphertext(seal_root, seal_map, MANIFEST_CT)
    try:
        man = json.loads(gpg_run(GPG_DECRYPT, passphrase, ct, tools), object_pairs_hook=_no_dup_pairs)
    except ValueError as e:
        raise Break("the manifest is not valid JSON") from e
    listed = {k[:-4] for k in seal_map if k != MANIFEST_CT}
    ok = (isinstance(man, dict) and set(man) == {"products", "paths"}
          and isinstance(man["products"], dict) and isinstance(man["paths"], dict)
          and set(man["products"]) == set(man["paths"]) == listed
          and all(isinstance(h, str) and HEX64.fullmatch(h) for h in man["products"].values())
          and all(_safe_rel(p) for p in man["paths"].values())
          and len(set(man["paths"].values())) == len(man["paths"]))
    if not ok:
        raise Break("the manifest's schema or ids are not the seal's")
    return SealedManifest(man["products"], man["paths"])


def read_product(seal_root: Path, seal_map: dict, manifest: SealedManifest, pid: str, passphrase: str,
                 tools: Tools) -> bytes:
    if not isinstance(manifest, SealedManifest):
        raise Refusal("read_product takes the SealedManifest that open_manifest returns")
    if pid not in manifest:
        raise Refusal("a requested id is not in the manifest")
    ct = read_ciphertext(seal_root, seal_map, pid + ".gpg")
    plain = gpg_run(GPG_DECRYPT, passphrase, ct, tools)
    if hashlib.sha256(plain).hexdigest() != manifest.sha256(pid):
        raise Break(f"{pid} does not decrypt to its manifest sha256")
    return plain


PUBLISH_REFUSAL = "publish_guard: the output carries a seed, a sealed path's digit run or a sealed hash"
DIGIT_RUN = re.compile(r"[0-9]{10,}")
RANGE_TOKEN = re.compile(rb"(?<![0-9])0*([1-9][0-9]{9})(?![0-9])")


def publish_guard(data: bytes | str, manifest: SealedManifest, seeds: list[int] | None,
                  published: dict[str, bytes] | None = None, allowlist: list[str] | None = None) -> bytes | str:
    """Every byte PV publishes passes here first (the director's ruling 4 of 2026-11-25). Nothing publishes at PG, so
    the caller is PV's decrypt-and-write step, which opens the manifest; none exists yet. It refuses, with a fixed
    message that names nothing:
      - each given seed in any form: decimal (so also zero-padded) and hex in either case (so also 0x-prefixed or
        zero-padded);
      - every run of 10 or more digits in a manifest relpath component (gevgen's seed-named files);
      - every manifest plaintext hash's hex, in either case and at any offset.
    `seeds` is the exact, non-empty list of int seeds. None selects the fallback instead: any 10-digit decimal in
    [SEED_BASE_LO, SEED_LIMIT), zero-padded or not, which also refuses an epoch timestamp.
    The one exemption (the director's ruling of 2026-11-25, for a published sums file): `published` maps each file
    published alongside `data` (manifest relpath -> its bytes) and `allowlist` is the export allowlist's globs ('*'
    crosses '/'); they come together. Each published file must match the allowlist and be in the manifest, and its
    sha256 is recomputed here and must equal its manifest entry, or the call is refused. Only those recomputed hashes
    may then appear in `data`; every other manifest hash still refuses. Returns `data` unchanged."""
    if not (isinstance(data, (bytes, str)) and isinstance(manifest, SealedManifest) and (seeds is None or (
            isinstance(seeds, list) and seeds and all(type(s) is int and s >= 0 for s in seeds)))):
        raise Refusal("publish_guard takes bytes or str, a SealedManifest, and a non-empty list of int seeds or None")
    exempt = set()
    if published is not None or allowlist is not None:
        if not (isinstance(published, dict) and published and isinstance(allowlist, list) and allowlist and
                all(isinstance(g, str) and g for g in allowlist) and
                all(isinstance(r, str) and isinstance(v, bytes) for r, v in published.items())):
            raise Refusal("publish_guard takes the published files (relpath -> bytes) and the export allowlist "
                          "together, both non-empty")
        by_path = {manifest.path(pid): pid for pid in manifest.ids()}
        for rel, body in published.items():
            if not any(fnmatch.fnmatchcase(rel, g) for g in allowlist):
                raise Refusal("publish_guard: a file published alongside is outside the export allowlist")
            if rel not in by_path:
                raise Refusal("publish_guard: a file published alongside is not in the manifest")
            h = hashlib.sha256(body).hexdigest()
            if h != manifest.sha256(by_path[rel]):
                raise Refusal("publish_guard: a file published alongside does not hash to its manifest entry")
            exempt.add(h)
    b = data.encode() if isinstance(data, str) else data
    low = b.lower()
    needles = set()
    for s in seeds or []:
        needles |= {str(s).encode(), f"{s:x}".encode()}
    for pid in manifest.ids():
        for comp in manifest.path(pid).split("/"):
            needles |= {m.encode() for m in DIGIT_RUN.findall(comp)}
        if manifest.sha256(pid) not in exempt:
            needles.add(manifest.sha256(pid).encode())
    hit = any(n in low for n in needles)
    if not hit and seeds is None:
        hit = any(SEED_BASE_LO <= int(m.group(1)) < SEED_LIMIT for m in RANGE_TOKEN.finditer(b))
    if hit:
        raise Refusal(PUBLISH_REFUSAL)
    return data
