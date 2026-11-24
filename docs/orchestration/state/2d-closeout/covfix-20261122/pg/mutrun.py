"""mutrun.py -- PG's mutant runner, with the director's kill rule (2026-11-24).

A mutant is (file, old, new, what, suite[, count]): `old` must occur exactly `count` times in `file` (default once)
and is replaced by `new` in a throwaway copy of the repository subset the suites read. Then:
- the copy must compile (compile() for .py, bash -n for .sh), or the mutant is INVALID;
- its suite runs under unittest, which reports an assertion failure as FAIL and any other exception as ERROR;
- KILLED only if at least one test FAILs, and the log names them; ERRORs alone, a timeout or a non-zero exit
  with no FAIL are INVALID, listed separately, and count against the receipt; a clean pass is SURVIVED.
Every suite must first pass clean on the unmutated copy, or nothing runs.
"""
import concurrent.futures
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[6]
PG = "docs/orchestration/state/2d-closeout/covfix-20261122"
G, N = "3d-unfolding/genie", "nd-unfolding"
SUITES = {
    "probe": (f"{PG}/pg/probe", [sys.executable, "-I", "-B", "test_pg_probe.py"]),
    "verify": (f"{N}/tests", [sys.executable, "-B", "-m", "unittest", "test_pg_verify"]),
    "generate": (f"{N}/tests", [sys.executable, "-B", "-m", "unittest", "test_covfix_pg"]),
    "install": (f"{PG}/pg/install", [sys.executable, "-I", "-B", "test_pg_install.py"]),
}
TIMEOUT_S = 900


def sandbox():
    tmp = Path(tempfile.mkdtemp(prefix="pg-mut-"))
    shutil.copytree(REPO / G, tmp / G, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(REPO / N / "pv-ladder", tmp / N / "pv-ladder", ignore=shutil.ignore_patterns("__pycache__"))
    for p in (REPO / N).iterdir():
        if p.is_file() and p.suffix in (".py", ".sh"):
            shutil.copy(p, tmp / N / p.name)
    (tmp / N / "tests").mkdir()
    for n in ("test_covfix_pg.py", "test_pg_verify.py"):
        shutil.copy(REPO / N / "tests" / n, tmp / N / "tests" / n)
    (tmp / PG).mkdir(parents=True)
    shutil.copy(REPO / PG / "COVFIX-DECLARATION.md", tmp / PG / "COVFIX-DECLARATION.md")
    for d in ("probe", "record", "install"):
        shutil.copytree(REPO / PG / "pg" / d, tmp / PG / "pg" / d, ignore=shutil.ignore_patterns("__pycache__"))
    return tmp


def run_suite(tmp, suite):
    d, cmd = SUITES[suite]
    env = dict(os.environ, PG_REPO_ROOT=str(tmp), PG_GIT_ROOT=str(REPO), PYTHONDONTWRITEBYTECODE="1")
    try:
        p = subprocess.run(cmd, cwd=tmp / d, capture_output=True, text=True, timeout=TIMEOUT_S, env=env)
    except subprocess.TimeoutExpired:
        return None, "", True
    return p.returncode, p.stdout + p.stderr, False


def classify(rc, out, timed_out):
    if timed_out:
        return "INVALID", "timeout"
    fails = re.findall(r"^FAIL: (\S+) \((\S+?)\)", out, re.M)
    errs = re.findall(r"^ERROR: (\S+) \((\S+?)\)", out, re.M)
    if fails:
        return "KILLED", ", ".join(sorted({n for n, _ in fails}))
    if errs:
        return "INVALID", "errors only: " + ", ".join(sorted({n for n, _ in errs}))
    if rc != 0:
        return "INVALID", f"exit {rc} with no FAIL"
    return "SURVIVED", ""


def compiles(path):
    if path.suffix == ".py":
        try:
            compile(path.read_text(), str(path), "exec")
            return True
        except SyntaxError:
            return False
    if path.suffix == ".sh":
        return subprocess.run(["bash", "-n", str(path)], capture_output=True).returncode == 0
    return True


def one(i, m):
    f, old, new, what, suite = m[:5]
    count = m[5] if len(m) > 5 else 1
    tmp = sandbox()
    try:
        src = (tmp / f).read_text()
        if src.count(old) != count:
            return "INVALID", f"M{i:02d} INVALID (not applicable: {src.count(old)} matches): {what} [{f}]"
        (tmp / f).write_text(src.replace(old, new))
        if not compiles(tmp / f):
            return "INVALID", f"M{i:02d} INVALID (does not compile): {what} [{f}]"
        status, detail = classify(*run_suite(tmp, suite))
        tail = f" by {detail}" if status == "KILLED" else f" ({detail})" if detail else ""
        return status, f"M{i:02d} {status}{tail}: {what} [{f}]"
    finally:
        shutil.rmtree(tmp)


def main(mutants, jobs=None):
    jobs = jobs or int(os.environ.get("PG_MUTANT_JOBS", "6"))
    tmp = sandbox()
    try:
        for suite in sorted({m[4] for m in mutants}):
            rc, out, to = run_suite(tmp, suite)
            status, detail = classify(rc, out, to)
            line = [ln for ln in out.strip().splitlines() if ln.startswith(("OK", "FAILED", "Ran "))]
            print(f"baseline {suite}: {'clean' if status == 'SURVIVED' else 'NOT CLEAN ' + detail} {line}")
            if status != "SURVIVED":
                return 1
    finally:
        shutil.rmtree(tmp)
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        results = list(ex.map(lambda a: one(*a), enumerate(mutants, 1)))
    for _, line in results:
        print(line)
    n = {s: sum(r == s for r, _ in results) for s in ("KILLED", "INVALID", "SURVIVED")}
    print(f"{n['KILLED']} of {len(mutants)} killed; {n['INVALID']} invalid; {n['SURVIVED']} survived")
    return 0 if n["KILLED"] == len(mutants) else 1
