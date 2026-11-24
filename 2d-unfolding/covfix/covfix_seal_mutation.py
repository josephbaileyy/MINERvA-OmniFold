"""Hand mutants for covfix_seal.py, covfix_pg.py and covfix_sealcheck.py: each must be killed by test_covfix_seal.py.

  python3 -B covfix_seal_mutation.py [--jobs N] [--only ID,ID]     one line per mutant; exit 0 only if all are killed

Each mutant runs in a fresh temp dir holding copies of the three modules and the tests (they import nothing else from
the repo), so nothing beside this file is touched. The unmutated copy must pass first. A run whose failure names no
test, or shows an import or discovery failure, is a HARNESS FAILURE, not a kill.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ("covfix_seal.py", "covfix_pg.py", "covfix_sealcheck.py", "test_covfix_seal.py")
S, P, K = "covfix_seal.py", "covfix_pg.py", "covfix_sealcheck.py"
MUTANTS = [
    ('frame-uppercase', S, '_PG_FRAME = re.compile(rb"([0-9a-f]{64})', '_PG_FRAME = re.compile(rb"([0-9a-fA-F]{64})'),
    # Lowering SEED_BASE_LO is equivalent (the frame regex [1-9][0-9]{9} already rejects < 1e9); the raised bound is not.
    ('seed-lo-raised', S, 'SEED_BASE_LO, SEED_BASE_HI = 1_000_000_000, 2_000_000_000', 'SEED_BASE_LO, SEED_BASE_HI = 1_000_000_001, 2_000_000_000'),
    ('seed-hi', S, 'SEED_BASE_LO, SEED_BASE_HI = 1_000_000_000, 2_000_000_000', 'SEED_BASE_LO, SEED_BASE_HI = 1_000_000_000, 2_000_000_001'),
    ('seed-limit-strict', S, 'if max(seeds) >= SEED_LIMIT:', 'if max(seeds) > SEED_LIMIT:'),
    ('u-stride', S, 'U_STRIDE = 10_000', 'U_STRIDE = 1_000'),
    ('n-tasks', S, 'N_TASKS = 7 ', 'N_TASKS = 6 '),
    ('no-force-mdc', S, '"--s2k-digest-algo", "SHA512", "--force-mdc")', '"--s2k-digest-algo", "SHA512")'),
    ('decrypt-symkey-cache', S, '"--no-symkey-cache", "--decrypt")', '"--decrypt")'),
    ('gpg-rc-ignored', S, '    if rc != 0:\n        raise Refusal(f"gpg exited', '    if False:\n        raise Refusal(f"gpg exited'),
    ('tools-relative-ok', S, 'if not os.path.isabs(p) or not os.path.isfile(p) or', 'if not os.path.isfile(p) or'),
    ('env-inherited', S, 'env = dict(GPG_ENV, GNUPGHOME=home)', 'env = dict(os.environ, GNUPGHOME=home)'),
    ('fds-not-closed', S, 'close_fds=True, pass_fds=(3,), preexec_fn', 'close_fds=False, preexec_fn'),
    ('core-not-limited', S, '        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))\n', ''),
    ('home-under-tmpdir', S, '    root = "/dev/shm" if os.path.isdir("/dev/shm") else "/tmp"\n', '    root = tempfile.gettempdir()\n'),
    ('scratch-root-ok', S, '    if scratch and _inside(root, scratch):\n', '    if False:\n'),
    ('home-max', S, 'GNUPG_HOME_MAX = 80', 'GNUPG_HOME_MAX = 800'),
    ('home-mode', S, '    os.chmod(home, 0o700)\n    if len(home)', '    os.chmod(home, 0o755)\n    if len(home)'),
    ('home-not-removed', S, '        shutil.rmtree(home, ignore_errors=True)\n        if os.path.lexists(home):', '        pass\n        if os.path.lexists(home):'),
    ('removal-unverified', S, '        if os.path.lexists(home):\n            raise Refusal("the GNUPGHOME could not be removed")', '        if False:\n            raise Refusal("the GNUPGHOME could not be removed")'),
    ('gpgconf-error-skips-removal', S, '        except (OSError, subprocess.SubprocessError):\n            pass\n', '        except KeyError:\n            pass\n'),
    ('symlink-allowed', S, '                raise Refusal("a non-regular entry (symlink or special file) in a sealed tree")', '                pass'),
    ('walk-errors-ignored', S, '    for dirpath, dirnames, filenames in os.walk(root, followlinks=False, onerror=_raise):', '    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):'),
    ('ids-from-zero', S, 'return [f"p{i:04d}" for i in range(1, n + 1)]', 'return [f"p{i:04d}" for i in range(n)]'),
    ('max-products', S, 'MAX_PRODUCTS = 9999', 'MAX_PRODUCTS = 99999'),
    ('manifest-no-paths', S, 'json.dumps({"products": hashes, "paths": paths}, sort_keys=True)', 'json.dumps({"products": hashes}, sort_keys=True)'),
    ('round-trip-skipped', S, '        if hashlib.sha256(back).hexdigest() != hashes[pid]:', '        if False:'),
    ('manifest-trip-skipped', S, '    if back != man_plain:', '    if False:'),
    ('seal-publishes-paths', S, '        cipher[pid + ".gpg"] = hashlib.sha256(ct).hexdigest()', '        cipher[rel + ".gpg"] = hashlib.sha256(ct).hexdigest()'),
    ('overwrite-ciphertext', S, '    with open(path, "xb") as f:', '    with open(path, "wb") as f:'),
    ('delete-follows-dir-link', S, '            if os.path.islink(p):\n                os.unlink(p)', '            if False:\n                os.unlink(p)'),
    ('scan-inverted', S, 'hexdigest() in plaintext_hashes:', 'hexdigest() not in plaintext_hashes:'),
    ('scan-skips-file-root', S, '        yield root\n        return\n', '        return\n'),
    ('nofollow-off', S, 'NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)', 'NOFOLLOW = 0'),
    ('regular-check-off', S, '        if not stat.S_ISREG(os.fstat(fd).st_mode):\n            raise Refusal("a sealed entry', '        if False:\n            raise Refusal("a sealed entry'),
    ('seal-dup-allowed', S, 'if not m or m.group(2) in out:', 'if not m:'),
    ('seal-noncanonical-ok', S, 'if MANIFEST_CT not in out or not ids or ids != product_ids(len(ids)) or \\', 'if MANIFEST_CT not in out or \\'),
    ('check-mismatch-inverted', S, 'hexdigest() != want[r])', 'hexdigest() == want[r])'),
    ('check-extra-ignored', S, '    extra = have - set(want)', '    extra = set()'),
    ('check-seal-file-counted', S, '    have = set(enumerate_files(sealed)) - {SEAL_FILE}', '    have = set(enumerate_files(sealed))'),
    ('reader-unlisted-break', S, '    if name not in seal_map:\n        raise Refusal("a requested name', '    if name not in seal_map:\n        raise Break("a requested name'),
    ('reader-missing-as-refusal', S, '        raise Break("a sealed ciphertext is missing") from e', '        raise Refusal("a sealed ciphertext is missing") from e'),
    ('reader-oserror-as-break', S, '        raise Refusal(f"a sealed ciphertext cannot be read', '        raise Break(f"a sealed ciphertext cannot be read'),
    ('reader-no-seal-sha', S, '    if hashlib.sha256(data).hexdigest() != seal_map[name]:', '    if False:'),
    ('manifest-dups-ok', S, 'json.loads(gpg_run(GPG_DECRYPT, passphrase, ct, tools), object_pairs_hook=_no_dup_pairs)', 'json.loads(gpg_run(GPG_DECRYPT, passphrase, ct, tools))'),
    ('manifest-hex-unchecked', S, '          and all(isinstance(h, str) and HEX64.fullmatch(h) for h in man["products"].values())', '          and True'),
    ('manifest-paths-unchecked', S, '          and all(_safe_rel(p) for p in man["paths"].values()))', '          and True)'),
    ('manifest-ids-unchecked', S, '          and set(man["products"]) == set(man["paths"]) == listed', '          and True'),
    ('manifest-not-json-refusal', S, '        raise Break("the manifest is not valid JSON") from e', '        raise Refusal("the manifest is not valid JSON") from e'),
    ('product-plain-unchecked', S, '    if hashlib.sha256(plain).hexdigest() != manifest["products"][pid]:', '    if False:'),
    ('product-unlisted-ok', S, '    if pid not in manifest["products"]:\n        raise Refusal', '    if False:\n        raise Refusal'),
    ('safe-rel-dotdot', S, '".." not in p.split("/"))', 'True)'),
    ('attempt-loose', P, 'ATTEMPT = re.compile(r"[0-9a-f]{32}")', 'ATTEMPT = re.compile(r"[0-9a-zA-Z]+")'),
    ('command-relative-ok', P, '          and os.path.isabs(spec["command"][0])\n', ''),
    ('command-sha-skipped', P, '    if file_sha256(resolved) != spec["command_sha256"]:', '    if False:'),
    ('tmpdir-keepable', P, '          and "TMPDIR" not in spec["env_keep"])', '          )'),
    ('env-not-scrubbed', P, '        env = {k: os.environ[k] for k in spec["env_keep"] if k in os.environ}', '        env = dict(os.environ)'),
    ('tmpdir-not-set', P, '        env["TMPDIR"] = str(workdir / "tmp")', '        pass'),
    ('workdir-not-empty-ok', P, '    if not workdir.is_dir() or any(workdir.iterdir()):', '    if not workdir.is_dir():'),
    ('sealed-exists-ok', P, '    if os.path.lexists(sealed):\n        raise', '    if False:\n        raise'),
    ('disjoint-unchecked', P, '    if cs._inside(str(s), str(w)) or cs._inside(str(w), str(s)):', '    if False:'),
    ('products-json-optional', P, '        ok = (summary["generation_rc0"] and summary["command_unchanged"] and summary["products_json"]', '        ok = (summary["generation_rc0"] and summary["command_unchanged"]'),
    ('products-dups-ok', P, ' and len(set(lst)) == len(lst)):', '):'),
    ('command-change-ignored', P, 'summary["command_unchanged"] = file_sha256(spec["resolved"]) == spec["command_sha256"]', 'summary["command_unchanged"] = True'),
    ('synthetic-skipped', P, '        if cs.gpg_run(cs.GPG_DECRYPT, passphrase, cs.gpg_run(cs.GPG_ENCRYPT, passphrase, SYNTHETIC, tools),\n                      tools) != SYNTHETIC:', '        if False:'),
    ('scratch-optional', P, '        if stmp is None:\n            raise cs.Refusal("SCRATCH', '        if False:\n            raise cs.Refusal("SCRATCH'),
    ('workdir-empty-unchecked', P, 'and summary["workdir_empty"] and not hits', 'and not hits'),
    ('spill-not-failing', P, ' and not hits and summary["sealed_scan_hits"] == 0)', ' and summary["sealed_scan_hits"] == 0)'),
    ('spill-not-removed', P, '"spills_removed": remove_verified(hits),', '"spills_removed": True,'),
    ('seed-scan-off', P, ' or any(s in data or s in name for s in seeds)', ''),
    ('snapshot-top-level-only', P, '    for dirpath, _, filenames in os.walk(root, followlinks=False, onerror=cs._raise):', '    for dirpath, _, filenames in [next(os.walk(root))]:'),
    ('final-check-skipped', P, '        if not cs.seal_check(sealed, s["seal_text"])["ok"]:', '        if False:'),
    ('trap-removed', P, '        if started and workdir.is_dir():', '        if False:'),
    ('trap-spills-off', P, 'summary["trap_spills_removed"] = remove_verified(hits)', 'summary["trap_spills_removed"] = True'),
    ('trap-delete-coupled', P, '                summary["trap_spills_removed"] = "failed"\n            try:\n                summary["trap_deleted"] = cs.delete_plaintext(workdir)', '                summary["trap_spills_removed"] = "failed"\n                return 1, summary\n            try:\n                summary["trap_deleted"] = cs.delete_plaintext(workdir)'),
    ('internal-error-leaks', P, 'summary["refused"] = "terminated" if isinstance(e, SystemExit) else "internal error"', 'summary["refused"] = str(e)'),
    ('sigterm-not-installed', P, '    old = signal.signal(signal.SIGTERM, _term)', '    old = signal.getsignal(signal.SIGTERM)'),
    ('receipt-on-failure', P, '    if rc == 0:\n        print(f"covfix-receipt', '    if rc in (0, 1):\n        print(f"covfix-receipt'),
    ('break-line-missing', P, '    elif rc == cs.BREAK_RC:', '    elif False:'),
    ('pin-ignored', K, '        if a.seal_sha256 is not None and rec["seal_sha256"] != a.seal_sha256:', '        if False:'),
    ('check-message-leaks', K, 'rec = {"ok": False, "refused": "the seal file or the sealed dir cannot be read"}', 'rec = {"ok": False, "refused": "x"}'),
]


def run_tests(d: Path) -> tuple[int, str]:
    env = dict(os.environ, OMP_NUM_THREADS="1")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_covfix_seal.py"], cwd=d, env=env,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, timeout=1200,
                       text=True)
    lines = r.stderr.splitlines()
    named = [ln for ln in lines if ln.startswith(("FAIL: ", "ERROR: "))]
    if r.returncode != 0 and (not named or any("_FailedTest" in ln for ln in named)):
        return -1, "HARNESS: " + (lines[-1] if lines else "no stderr")
    return r.returncode, (named[0] if named else (lines[-1] if lines else ""))


def one(m) -> tuple[str, str, str]:
    mid, f, old, new = m
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for name in FILES:
            shutil.copy2(HERE / name, d / name)
        if m[0] != "baseline":
            src = (d / f).read_text()
            if src.count(old) != 1:
                return mid, "NOT APPLIED", f"pattern occurs {src.count(old)} times"
            (d / f).write_text(src.replace(old, new))
        rc, why = run_tests(d)
    return mid, ("killed" if rc > 0 else "HARNESS FAILURE" if rc < 0 else "SURVIVED") if mid != "baseline" \
        else ("pass" if rc == 0 else "FAIL"), why


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--only", default="", help="comma-separated mutant ids (a partial rerun; the default runs all)")
    a = ap.parse_args()
    ids = [m[0] for m in MUTANTS]
    want = [x for x in a.only.split(",") if x]
    unknown = [x for x in want if x not in ids]
    if unknown:
        print(f"unknown mutant ids: {unknown}")
        return 2
    chosen = [m for m in MUTANTS if not want or m[0] in want]
    mid, status, why = one(("baseline", S, "", ""))
    print(f"baseline {status} {why}", flush=True)
    if status != "pass":
        return 2
    bad = []
    with ThreadPoolExecutor(a.jobs) as ex:
        for mid, status, why in ex.map(one, chosen):
            print(f"{mid}: {status} {why}", flush=True)
            if status != "killed":
                bad.append(mid)
    print(f"{len(chosen) - len(bad)}/{len(chosen)} killed; survived, harness or not applied: {bad}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
