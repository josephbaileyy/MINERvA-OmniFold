"""Hand mutants for covfix_seal.py, covfix_pg.py and covfix_sealcheck.py: each must be killed by test_covfix_seal.py.

  python3 -B covfix_seal_mutation.py [--jobs N]     one line per mutant; exit 0 only if all are killed

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
    ("frame-uppercase", S, '_PG_FRAME = re.compile(rb"([0-9a-f]{64})', '_PG_FRAME = re.compile(rb"([0-9a-fA-F]{64})'),
    ("seed-lo", S, "SEED_BASE_LO, SEED_BASE_HI = 1_000_000_000, 2_000_000_000",
     "SEED_BASE_LO, SEED_BASE_HI = 999_999_999, 2_000_000_000"),
    ("seed-hi", S, "SEED_BASE_LO, SEED_BASE_HI = 1_000_000_000, 2_000_000_000",
     "SEED_BASE_LO, SEED_BASE_HI = 1_000_000_000, 2_000_000_001"),
    ("seed-limit-strict", S, "if max(seeds) >= SEED_LIMIT:", "if max(seeds) > SEED_LIMIT:"),
    ("u-stride", S, "U_STRIDE = 10_000", "U_STRIDE = 1_000"),
    ("n-tasks", S, "N_TASKS = 7 ", "N_TASKS = 6 "),
    ("no-force-mdc", S, '"--s2k-digest-algo", "SHA512", "--force-mdc")', '"--s2k-digest-algo", "SHA512")'),
    ("decrypt-symkey-cache", S, '"--no-symkey-cache", "--decrypt")', '"--decrypt")'),
    ("gpg-rc-ignored", S, "    if p.returncode != 0:\n        raise Refusal", "    if False:\n        raise Refusal"),
    ("home-under-tmpdir", S, '    root = "/dev/shm" if os.path.isdir("/dev/shm") else "/tmp"\n',
     "    root = tempfile.gettempdir()\n"),
    ("home-max", S, "GNUPG_HOME_MAX = 80", "GNUPG_HOME_MAX = 800"),
    ("home-mode", S, "    os.chmod(home, 0o700)\n    if len(home)", "    os.chmod(home, 0o755)\n    if len(home)"),
    ("home-not-removed", S, "        shutil.rmtree(home, ignore_errors=True)\n    if p.returncode",
     "        pass\n    if p.returncode"),
    ("symlink-allowed", S, '                raise Refusal("a non-regular entry (symlink or special file) under the work dir")',
     "                pass"),
    ("ids-from-zero", S, 'return [f"p{i:04d}" for i in range(1, n + 1)]', 'return [f"p{i:04d}" for i in range(n)]'),
    ("max-products", S, "MAX_PRODUCTS = 9999", "MAX_PRODUCTS = 99999"),
    ("manifest-no-paths", S, 'json.dumps({"products": hashes, "paths": paths}, sort_keys=True)',
     'json.dumps({"products": hashes}, sort_keys=True)'),
    ("round-trip-skipped", S, "        if hashlib.sha256(back).hexdigest() != hashes[pid]:", "        if False:"),
    ("manifest-trip-skipped", S, "    if back != man_plain:", "    if False:"),
    ("seal-publishes-paths", S, '        cipher[pid + ".gpg"] = hashlib.sha256(ct).hexdigest()',
     '        cipher[rel + ".gpg"] = hashlib.sha256(ct).hexdigest()'),
    ("overwrite-ciphertext", S, '    with open(path, "xb") as f:', '    with open(path, "wb") as f:'),
    ("delete-follows-dir-link", S, "            if os.path.islink(p):\n                os.unlink(p)",
     "            if False:\n                os.unlink(p)"),
    ("scan-inverted", S, "hexdigest() in plaintext_hashes:", "hexdigest() not in plaintext_hashes:"),
    ("scan-skips-file-root", S, "        yield root\n        return\n", "        return\n"),
    ("seal-dup-allowed", S, "if not m or m.group(2) in out:", "if not m:"),
    ("seal-no-manifest-ok", S, '    if MANIFEST + ".gpg" not in out:\n        raise', '    if False:\n        raise'),
    ("check-mismatch-inverted", S, "hexdigest() != want[r])", "hexdigest() == want[r])"),
    ("check-extra-ignored", S, "    extra = sorted(have - set(want))", "    extra = []"),
    ("attempt-loose", P, 'ATTEMPT = re.compile(r"[0-9a-f]{32}")', 'ATTEMPT = re.compile(r"[0-9a-zA-Z]+")'),
    ("command-sha-skipped", P, '    if got != spec["command_sha256"]:', "    if False:"),
    ("tmpdir-keepable", P, '          and "TMPDIR" not in spec["env_keep"])', "          )"),
    ("env-not-scrubbed", P, '    env = {k: os.environ[k] for k in spec["env_keep"] if k in os.environ}',
     "    env = dict(os.environ)"),
    ("tmpdir-not-set", P, '    env["TMPDIR"] = str(workdir / "tmp")', "    pass"),
    ("workdir-not-empty-ok", P, "    if not workdir.is_dir() or any(workdir.iterdir()):", "    if not workdir.is_dir():"),
    ("sealed-exists-ok", P, "    if sealed.exists():\n        raise", "    if False:\n        raise"),
    ("products-json-optional", P, 'ok = summary["generation_rc0"] and summary["products_json"] and not hits',
     'ok = summary["generation_rc0"] and not hits'),
    ("receipt-on-failure", P, "    if rc == 0:\n        print(f\"covfix-receipt", "    if rc in (0, 1):\n        print(f\"covfix-receipt"),
    ("break-line-missing", P, "    elif rc == cs.BREAK_RC:", "    elif False:"),
    ("trap-removed", P, "        if started and workdir.is_dir():", "        if False:"),
    ("scratch-not-scanned", P, "[workdir, sealed, *[stmp / e for e in new]]", "[workdir, sealed]"),
    ("pin-ignored", K, '        if a.seal_sha256 is not None and rec["seal_sha256"] != a.seal_sha256:', "        if False:"),
    ('reader-unlisted-ok', S, '    if name not in seal_map:\n        raise Break', '    if False:\n        raise Break'),
    ('reader-missing-as-refusal', S, '        raise Break("a sealed ciphertext is missing") from e', '        raise Refusal("a sealed ciphertext is missing") from e'),
    ('reader-oserror-as-break', S, '        raise Refusal(f"a sealed ciphertext cannot be read', '        raise Break(f"a sealed ciphertext cannot be read'),
    ('reader-no-seal-sha', S, '    if hashlib.sha256(data).hexdigest() != seal_map[name]:', '    if False:'),
    ('manifest-not-json-refusal', S, '        raise Break("the manifest is not JSON") from e', '        raise Refusal("the manifest is not JSON") from e'),
    ('manifest-ids-unchecked', S, '            and ids == listed):', '            ):'),
    ('product-plain-unchecked', S, '    if hashlib.sha256(plain).hexdigest() != manifest["products"][pid]:', '    if False:'),
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
    a = ap.parse_args()
    mid, status, why = one(("baseline", S, "", ""))
    print(f"baseline {status} {why}", flush=True)
    if status != "pass":
        return 2
    bad = []
    with ThreadPoolExecutor(a.jobs) as ex:
        for mid, status, why in ex.map(one, MUTANTS):
            print(f"{mid}: {status} {why}", flush=True)
            if status != "killed":
                bad.append(mid)
    print(f"{len(MUTANTS) - len(bad)}/{len(MUTANTS)} killed; survived, harness or not applied: {bad}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
