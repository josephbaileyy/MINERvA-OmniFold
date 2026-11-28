#!/usr/bin/env python3
"""Single-site planted mutants over the geanttw P0 package.

    python3 mutation.py [--jobs N] [--out mutation.out]      # run from anywhere

Each mutant changes ONE site in ONE file, in a scratch copy of this directory. Then the test file that owns the
source runs, and the mutant is KILLED if those tests fail, SURVIVED if they pass, TIMEOUT (not a kill) if they hang.

  - Python sources (dumpcmp.py, p0_check.py, geanttw_sacct.py, geanttw_provenance.py): every operator, keyword or verdict-literal TOKEN is flipped (found by
    Python's tokenizer, so nothing inside a string literal is touched): == <-> !=, < <-> >=, > <-> <=, `and` <-> `or`,
    `not` removed, True <-> False, "PASS" <-> "FAIL".
  - Shell sources (geanttw_evloop.sbatch, geanttw_build.sh, geanttw_connect.sh, geanttw_remote.sh): on every line that refuses or
    stops (an `exit [1-9]`, or a call of the bail/stop helpers), the exit or call is replaced by `true`; on those lines,
    on CHECK lines and on `if [[`/`[[` test lines, each `==`/`!=`/`-eq`/`-ne` is flipped.

The output lists every mutant with its file, line, operator and verdict, then the totals. Exit 0 iff every mutant
is killed.
"""
import argparse
import concurrent.futures as cf
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tokenize
from pathlib import Path

HERE = Path(__file__).resolve().parent
OWNER = {
    "dumpcmp.py": "tests/test_dumpcmp.py",
    "p0_check.py": "tests/test_p0_check.py",
    "geanttw_sacct.py": "tests/test_provenance_sacct.py",
    "geanttw_provenance.py": "tests/test_provenance_sacct.py",
    "geanttw_evloop.sbatch": "tests/test_shell_scripts.py",
    "geanttw_build.sh": "tests/test_shell_scripts.py",
    "geanttw_connect.sh": "tests/test_shell_scripts.py",
    "geanttw_remote.sh": ("tests/test_shell_scripts.py", "tests/test_p2p3_steps.py"),
    "p2_limits.py": "tests/test_p2_limits.py",
    "c2_check.py": "tests/test_c2_check.py",
    "p3_slim.py": "tests/test_p3_slim.py",
    "slim_tparams.py": "tests/test_p3_slim.py",
    "p3_readout.py": "tests/test_p3_readout.py",
    "geanttw_p3.sbatch": "tests/test_p3_sbatch.py",
}
PY_OPS = [
    (r"==", "!="), (r"!=", "=="), (r"(?<![<>=!])<(?![<=])", ">="), (r"(?<![<>=!-])>(?![>=])", "<="),
    (r"<=", ">"), (r">=", "<"), (r"\band\b", "or"), (r"\bor\b", "and"), (r"\bnot ", ""),
    (r"\bTrue\b", "False"), (r"\bFalse\b", "True"), (r'"PASS"', '"FAIL"'), (r'"FAIL"', '"PASS"'),
]
SH_EXIT = re.compile(r"\bexit [1-9]\b")
SH_OPS = [(r"==", "!="), (r"!=", "==")]
TIMEOUT = 1800   # a surviving shell mutant runs the whole suite (~8 min under 4-way load)


def python_sites(text):
    """Operator, keyword and verdict-literal TOKENS (Python's tokenizer), so text inside string literals is never
    mutated: a flipped word in a message is an equivalent mutant that proves nothing."""
    flips = {"==": "!=", "!=": "==", "<": ">=", ">": "<=", "<=": ">", ">=": "<", "and": "or", "or": "and",
             "True": "False", "False": "True", '"PASS"': '"FAIL"', '"FAIL"': '"PASS"'}
    lines = text.splitlines(keepends=True)
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type not in (tokenize.OP, tokenize.NAME, tokenize.STRING) or tok.string not in flips and tok.string != "not":
            continue
        (r, c), (r2, c2) = tok.start, tok.end
        if r != r2:
            continue
        if tok.string == "not":
            end = c2 + 1 if lines[r - 1][c2:c2 + 1] == " " else c2
            yield r, c, end, "", "not->del"
        else:
            yield r, c, c2, flips[tok.string], f"{tok.string}->{flips[tok.string]}"


SH_CALL = re.compile(r"(?:\|\||&&|\))\s*(bail|stop)\b")   # after ||, && or a case label
SH_DEF = re.compile(r"^\s*(bail|stop|say)\(\)")


def shell_sites(text):
    """Refusal sites: an `exit N` on a line, a call of the bail/stop helpers, and the comparisons on those lines
    and on the build's CHECK lines. The helpers' own definitions are skipped: neutralising one would disable
    every refusal at once, which proves nothing about any single guard."""
    for i, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("#") or SH_DEF.search(line):
            continue
        refusal = bool(SH_EXIT.search(line) or SH_CALL.search(line))
        if not (refusal or "CHECK" in line or line.lstrip().startswith(("if [[", "elif [[", "[[ "))):
            continue
        for m in SH_EXIT.finditer(line):
            yield i, m.start(), m.end(), "true", f"{m.group(0)}->true"
        for m in SH_CALL.finditer(line):
            yield i, m.start(1), m.end(1), "true", f"{m.group(1)}->true"
        for pat, rep in SH_OPS + [(r"-eq\b", "-ne"), (r"-ne\b", "-eq")]:
            for m in re.finditer(pat, line):
                yield i, m.start(), m.end(), rep, f"{m.group(0)}->{rep}"


def mutants():
    out = []
    for name in OWNER:
        text = (HERE / name).read_text()
        sites = python_sites(text) if name.endswith(".py") else shell_sites(text)
        for line, a, b, rep, op in sites:
            out.append((name, line, a, b, rep, op))
    return out


REPO = HERE.parents[4]


def run_one(mut):
    name, line, a, b, rep, op = mut
    with tempfile.TemporaryDirectory(prefix="geanttw-mut-") as td:
        work = Path(td) / "code"
        shutil.copytree(HERE, work, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "mutation.out",
                                                                  "linetrace*.txt"))
        p = work / name
        lines = p.read_text().splitlines(keepends=True)
        ln = lines[line - 1]
        lines[line - 1] = ln[:a] + rep + ln[b:]
        p.write_text("".join(lines))
        os.chmod(p, (HERE / name).stat().st_mode)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GEANTTW_REPO=str(REPO))
        try:
            owners = OWNER[name] if isinstance(OWNER[name], tuple) else (OWNER[name],)
            r = subprocess.run([sys.executable, "-m", "pytest", *owners, "-q", "-x", "-p", "no:cacheprovider"],
                               cwd=work, env=env, capture_output=True, text=True, timeout=TIMEOUT)
            verdict = "SURVIVED" if r.returncode == 0 else "KILLED"
        except subprocess.TimeoutExpired:
            verdict = "TIMEOUT"   # not a kill: counted with the survivors
    return name, line, op, verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--out", default=str(HERE / "mutation.out"))
    ap.add_argument("--only", help="restrict to one source file name")
    args = ap.parse_args()
    ms = [m for m in mutants() if not args.only or m[0] == args.only]
    # The positive control: each owner's tests must pass on an unmutated copy, run exactly as the mutants are.
    # Without it, a test that cannot run in the copy "kills" every mutant (a copy that could not find the repo did).
    for name in sorted({m[0] for m in ms}):
        n, _l, _o, v = run_one((name, 1, 0, 0, "", "control"))
        if v != "SURVIVED":
            print(f"CONTROL FAILED: {name}'s tests do not pass on an unmutated copy ({v}); no mutant is scored")
            sys.exit(2)
    results = []
    with cf.ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for res in ex.map(run_one, ms):
            results.append(res)
    lines = [f"{n}:{l} {op} {v}" for n, l, op, v in results]
    survived = [r for r in results if r[3] in ("SURVIVED", "TIMEOUT")]
    summary = [f"mutants {len(results)}; killed {len(results) - len(survived)}; not killed {len(survived)} (survived or timed out)"]
    for name in OWNER:
        rs = [r for r in results if r[0] == name]
        summary.append(f"  {name}: {len(rs)} mutants, {sum(r[3] == 'KILLED' for r in rs)} killed")
    Path(args.out).write_text("\n".join(lines + [""] + summary) + "\n")
    print("\n".join(summary))
    for r in survived:
        print(f"{r[3]} {r[0]}:{r[1]} {r[2]}")
    sys.exit(0 if not survived else 1)


if __name__ == "__main__":
    main()
