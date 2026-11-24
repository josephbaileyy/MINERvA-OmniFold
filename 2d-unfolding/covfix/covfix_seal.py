"""COVFIX PG's generic seal (COVFIX-DECLARATION.md rev 11.4 section 4.2; COVFIX-BINDING-1 ruling 4: cov2d writes PG's
capture, encryption, seal check and content scan). Library; the bound binary is covfix_pg.py, the check covfix_sealcheck.py.

  read_frame        the fixed stdin frame: PG "<64 hex>\\n<decimal>\\n", PV "<64 hex>\\n", then EOF; anything else refused
  task_seeds        base + 10_000 u + i for i < N_TASKS; a computed seed at or above 2^31 - 1 is refused
  gpg_run           the declared gpg argv, the passphrase on fd 3 through an internal pipe, a fresh throwaway
                    GNUPGHOME per call: short and node-local (/dev/shm, or /tmp where there is none; never $SCRATCH or
                    $TMPDIR, whose long Lustre paths break gpg-agent's socket), under 80 characters, mode 700; gpg-agent
                    is killed with it and the directory removed, so ~/.gnupg is never created or touched;
                    stdout is returned only after gpg exited 0 (a non-zero exit, such as an MDC failure, is a refusal)
  seal              section 4.2 steps 1-3: plaintext sha256 of every file under the work dir (O_NOATIME where the
                    platform has it), each encrypted to <sealed>/<id>.gpg under an OPAQUE id (p0001, p0002, ... in
                    sorted relpath order), the encrypted manifest PG-MANIFEST.json.gpg = {"products": {id: plaintext
                    sha256}, "paths": {id: relpath}} ("products" is the format the wrapper's reference role reads), a
                    decrypt-and-hash round trip of every product and the manifest, and the public PG-SEAL.sha256
                    (ciphertext sha256 per id and of the manifest). No relpath from the work dir is ever published:
                    a file name can carry a seed (gevgen's genie-mcjob-<seed>.status)
  delete_plaintext  step 4
  content_scan      step 5: every regular file under the enumerated PG-owned paths (a path may be a file), hashed,
                    against the plaintext list; symlinks and special files are skipped, never followed
  seal_check        the ciphertexts against a PG-SEAL.sha256, with no decryption (exact set, exact bytes)
  read_ciphertext   the reader side (PG's own round trip excepted): a ciphertext's bytes, read once and checked
                    against PG-SEAL.sha256 by opaque id BEFORE any decryption (JE's round-3 rule). A missing listed file
                    or different bytes is a Break; any other open or read error (permission, I/O) is a Refusal, a role
                    failure, never a break
  open_manifest     the manifest through read_ciphertext, decrypted, and its ids checked equal to the seal's
  read_product      one product through read_ciphertext, decrypted, its plaintext sha256 checked against the manifest
                    (a mismatch is a Break; a gpg failure on bytes that matched the seal is a Refusal)

The plaintext hashes never leave memory except inside the encrypted manifest. Nothing here prints.
MEASURES: nothing. CANNOT AUTHORIZE: a connect, a seal's acceptance, or any reading of sealed content.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

GPG_ENCRYPT = ("gpg", "--batch", "--yes", "--pinentry-mode", "loopback", "--passphrase-fd", "3", "--no-symkey-cache",
               "--symmetric", "--cipher-algo", "AES256", "--s2k-digest-algo", "SHA512", "--force-mdc")
GPG_DECRYPT = ("gpg", "--batch", "--pinentry-mode", "loopback", "--passphrase-fd", "3", "--no-symkey-cache", "--decrypt")
BREAK_RC = 66
SEED_BASE_LO, SEED_BASE_HI = 1_000_000_000, 2_000_000_000      # [lo, hi)
SEED_LIMIT = 2 ** 31 - 1                                         # a computed seed must be below this
N_TASKS = 7                                                      # FD-F1-DECLARATION-AMENDMENT-2: 7 tasks per tune
U_STRIDE = 10_000
MANIFEST = "PG-MANIFEST.json"
SEAL_FILE = "PG-SEAL.sha256"
MAX_PRODUCTS = 9999
NOATIME = getattr(os, "O_NOATIME", 0)
_PG_FRAME = re.compile(rb"([0-9a-f]{64})\n([1-9][0-9]*)\n")
_PV_FRAME = re.compile(rb"([0-9a-f]{64})\n")


class Refusal(Exception):
    """A role-terminal refusal: this run stops, and no receipt is printed."""


class Break(Exception):
    """A confirmed integrity break: a ciphertext does not decrypt to its recorded plaintext."""


# ------------------------------------------------------------------------------------------------ frame and seeds
def read_frame(data: bytes, with_seed: bool) -> tuple[str, int | None]:
    m = (_PG_FRAME if with_seed else _PV_FRAME).fullmatch(data)
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
GNUPG_HOME_MAX = 80


def new_gnupg_home() -> str:
    """A fresh, empty, mode-700 GNUPGHOME on a short node-local path (gpg-agent's socket path must stay short)."""
    root = "/dev/shm" if os.path.isdir("/dev/shm") else "/tmp"
    home = tempfile.mkdtemp(prefix="cfx", dir=root)
    os.chmod(home, 0o700)
    if len(home) >= GNUPG_HOME_MAX:
        shutil.rmtree(home, ignore_errors=True)
        raise Refusal("the GNUPGHOME path is not short")
    return home


def gpg_run(argv: tuple, passphrase: str, payload: bytes, gpg: str = "gpg") -> bytes:
    """Run gpg with the declared argv; the passphrase reaches it on fd 3 only. Raises Refusal on a non-zero exit."""
    home = new_gnupg_home()
    env = {k: v for k, v in os.environ.items() if not k.startswith("GPG") and k != "GNUPGHOME"}
    env["GNUPGHOME"] = home
    r, w = os.pipe()
    try:
        try:
            os.write(w, passphrase.encode("ascii") + b"\n")
        finally:
            os.close(w)

        def child():
            if r != 3:
                os.dup2(r, 3)
            else:
                os.set_inheritable(3, True)
        try:
            p = subprocess.Popen([gpg, *argv[1:]], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, close_fds=False, preexec_fn=child, env=env)
        finally:
            os.close(r)
        out, _err = p.communicate(payload)
    finally:
        subprocess.run(["gpgconf", "--homedir", home, "--kill", "gpg-agent"], capture_output=True, env=env)
        shutil.rmtree(home, ignore_errors=True)
    if p.returncode != 0:
        raise Refusal(f"gpg exited {p.returncode}")
    return out


# ------------------------------------------------------------------------------------------------- files
def noatime_read(path: Path) -> bytes:
    fd = os.open(str(path), os.O_RDONLY | NOATIME)
    try:
        chunks = []
        while True:
            b = os.read(fd, 1 << 24)
            if not b:
                break
            chunks.append(b)
    finally:
        os.close(fd)
    return b"".join(chunks)


def enumerate_files(root: Path) -> list[str]:
    """Sorted relative paths of the regular files under root. A symlink or a special file is refused: it could name
    bytes outside the PG-owned tree."""
    root = Path(root)
    out = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for name in dirnames + filenames:
            st = os.lstat(os.path.join(dirpath, name))
            if stat.S_ISLNK(st.st_mode) or not (stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)):
                raise Refusal("a non-regular entry (symlink or special file) under the work dir")
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


def seal(workdir: Path, sealed: Path, passphrase: str, gpg: str = "gpg") -> dict:
    """Section 4.2 steps 1-3 and 6's file. Returns {"hashes": {id: plaintext sha256}, "n_products", "seal_file"};
    the hashes are for the content scan only and are never written in plaintext. Raises Break on a round-trip
    mismatch."""
    workdir, sealed = Path(workdir), Path(sealed)
    rels = enumerate_files(workdir)
    if not rels:
        raise Refusal("the work dir holds no file to seal")
    ids = product_ids(len(rels))
    hashes, paths, cipher = {}, {}, {}
    for pid, rel in zip(ids, rels):
        plain = noatime_read(workdir / rel)
        hashes[pid], paths[pid] = hashlib.sha256(plain).hexdigest(), rel
        ct = gpg_run(GPG_ENCRYPT, passphrase, plain, gpg)
        _write_new(sealed / (pid + ".gpg"), ct)
        cipher[pid + ".gpg"] = hashlib.sha256(ct).hexdigest()
        del plain
    man_plain = json.dumps({"products": hashes, "paths": paths}, sort_keys=True).encode()
    man_ct = gpg_run(GPG_ENCRYPT, passphrase, man_plain, gpg)
    _write_new(sealed / (MANIFEST + ".gpg"), man_ct)
    cipher[MANIFEST + ".gpg"] = hashlib.sha256(man_ct).hexdigest()
    # step 3: the decrypt-and-hash round trip, from the bytes on disk
    for pid in ids:
        back = gpg_run(GPG_DECRYPT, passphrase, (sealed / (pid + ".gpg")).read_bytes(), gpg)
        if hashlib.sha256(back).hexdigest() != hashes[pid]:
            raise Break(f"{pid} does not reproduce its plaintext sha256")
        del back
    back = gpg_run(GPG_DECRYPT, passphrase, (sealed / (MANIFEST + ".gpg")).read_bytes(), gpg)
    if back != man_plain:
        raise Break("the manifest does not reproduce itself")
    seal_text = "".join(f"{h}  {name}\n" for name, h in sorted(cipher.items()))
    _write_new(sealed / SEAL_FILE, seal_text.encode())
    return {"hashes": hashes, "n_products": len(rels), "seal_file": str(sealed / SEAL_FILE)}


def delete_plaintext(workdir: Path) -> int:
    """Step 4, and the failure trap: unlink every non-directory entry under the work dir (files, and any symlink or
    special entry, never followed), then remove its subdirectories deepest first; returns the count unlinked."""
    workdir = Path(workdir)
    n = 0
    for dirpath, dirnames, filenames in os.walk(workdir, topdown=False, followlinks=False):
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
    for dirpath, _, filenames in os.walk(root, followlinks=False):
        for name in filenames:
            p = Path(dirpath) / name
            if stat.S_ISREG(os.lstat(p).st_mode):
                yield p


def content_scan(paths: list[Path], plaintext_hashes: set[str]) -> list[str]:
    """Step 5: every regular file under each enumerated PG-owned path (or the path itself, if it is a file) whose
    sha256 is a plaintext hash. A missing path is skipped; symlinks and special files are not followed."""
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
    out = {}
    for line in text.splitlines():
        m = re.fullmatch(r"([0-9a-f]{64})  (\S.*)", line)
        if not m or m.group(2) in out:
            raise Refusal(f"a malformed or repeated {SEAL_FILE} line")
        out[m.group(2)] = m.group(1)
    if MANIFEST + ".gpg" not in out:
        raise Refusal(f"{SEAL_FILE} names no manifest")
    return out


def seal_check(sealed: Path, seal_text: str) -> dict:
    """The ciphertexts under ``sealed`` against a PG-SEAL.sha256's text: the same set of .gpg files and the same
    bytes. No decryption. Returns {"ok", "missing", "extra", "mismatched", "n"}."""
    want = parse_seal(seal_text)
    sealed = Path(sealed)
    have = {r for r in enumerate_files(sealed) if r.endswith(".gpg")}
    missing = sorted(set(want) - have)
    extra = sorted(have - set(want))
    mismatched = sorted(r for r in set(want) & have
                        if hashlib.sha256(noatime_read(sealed / r)).hexdigest() != want[r])
    return {"ok": not (missing or extra or mismatched), "missing": missing, "extra": extra, "mismatched": mismatched,
            "n": len(want)}


# ------------------------------------------------------------------------------------------------- reader side
def read_ciphertext(seal_root: Path, seal_map: dict, name: str) -> bytes:
    if name not in seal_map:
        raise Break("a requested ciphertext is not in the seal")
    try:
        data = noatime_read(Path(seal_root) / name)
    except FileNotFoundError as e:
        raise Break("a sealed ciphertext is missing") from e
    except OSError as e:
        raise Refusal(f"a sealed ciphertext cannot be read ({type(e).__name__})") from e
    if hashlib.sha256(data).hexdigest() != seal_map[name]:
        raise Break("a ciphertext is not its PG-SEAL sha256")
    return data


def open_manifest(seal_root: Path, seal_map: dict, passphrase: str, gpg: str = "gpg") -> dict:
    ct = read_ciphertext(seal_root, seal_map, MANIFEST + ".gpg")
    try:
        man = json.loads(gpg_run(GPG_DECRYPT, passphrase, ct, gpg))
    except ValueError as e:
        raise Break("the manifest is not JSON") from e
    ids = set(man.get("products", {})) if isinstance(man, dict) else set()
    listed = {k[:-len(".gpg")] for k in seal_map if k != MANIFEST + ".gpg"}
    if not (isinstance(man, dict) and set(man) == {"products", "paths"} and set(man["paths"]) == ids
            and ids == listed):
        raise Break("the manifest's ids are not the seal's")
    return man


def read_product(seal_root: Path, seal_map: dict, manifest: dict, pid: str, passphrase: str,
                 gpg: str = "gpg") -> bytes:
    ct = read_ciphertext(seal_root, seal_map, pid + ".gpg")
    plain = gpg_run(GPG_DECRYPT, passphrase, ct, gpg)
    if hashlib.sha256(plain).hexdigest() != manifest["products"][pid]:
        raise Break(f"{pid} does not decrypt to its manifest sha256")
    return plain
