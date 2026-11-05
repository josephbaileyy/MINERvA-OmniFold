"""Does every binding-3 job line that runs fd_1b_mc, fd_1b_c2 or fd_1b_binning come through 1B's guarded launcher
(the director's ruling of 2026-11-05)? Two populations, each with its count printed so an empty one fails:
- every *.sh in this directory (b3/): binding 3's job and connect scripts, login-node steps included;
- every step row the stage 1 generator emits (fd_f1_lane.py runs each row's entry with the deploy as cwd).

A script line is parsed as a shell would split it (continuations joined, then shlex), not by a regex. Any token that
is a Python interpreter (python, python3, python3.11, a path to one, or "$PY") starts an invocation; the
interpreter's own options are skipped with their values (-X, -W, -c and -m take one; -c and -m end it, as does "-",
the stdin script). The next token is the script. An invocation whose script is a 1B entry module is UNGUARDED; one
whose script is the guard is GUARDED only if the guard's options (--declared, --root VALUE) are followed by "--"
and then a 1B entry module. A step row is GUARDED only if its entry is the guard, with the same shape.

    python3 -B guard_scan.py [TABLES_DIR ...]      (prints the counts; exit 0 only with none unguarded)
"""
from __future__ import annotations

import os
import re
import shlex
import sys
from pathlib import Path

ENTRIES = ("fd_1b_mc.py", "fd_1b_c2.py", "fd_1b_binning.py")
GUARD = "fd_1b_noatime_guard.py"
_INTERP = re.compile(r"^(\$\{?PY\}?|python(\d(\.\d+)?)?)$")
_VALUE_OPTS = {"-X", "-W", "-Q"}
_ENDING_OPTS = {"-c", "-m", "-"}


def logical_lines(text: str) -> list[str]:
    """Lines with backslash continuations joined; comment-only lines dropped."""
    out, cur = [], ""
    for raw in text.splitlines():
        if raw.rstrip().endswith("\\"):
            cur += raw.rstrip()[:-1] + " "
            continue
        cur += raw
        if cur.strip() and not cur.lstrip().startswith("#"):
            out.append(cur)
        cur = ""
    if cur.strip():
        out.append(cur)
    return out


def is_interpreter(tok: str) -> bool:
    return bool(_INTERP.match(os.path.basename(tok)))


def judge(tokens: list[str]) -> str | None:
    """'guarded', 'unguarded', or None (no 1B entry run) for a token list starting at its script."""
    if not tokens:
        return None
    script = os.path.basename(tokens[0])
    if script in ENTRIES:
        return "unguarded"
    if script != GUARD:
        return None
    i = 1
    while i < len(tokens) and tokens[i] != "--":
        if tokens[i] == "--declared":
            i += 1
        elif tokens[i] == "--root" and i + 1 < len(tokens):
            i += 2
        else:
            return "unguarded"                                # a malformed guard line guards nothing
    if i >= len(tokens) - 1 or os.path.basename(tokens[i + 1]) not in ENTRIES:
        return "unguarded"
    return "guarded"


def scan_line(line: str) -> list[str]:
    """The verdict of every Python invocation on one logical shell line that runs a 1B entry module."""
    try:
        toks = shlex.split(line, comments=True, posix=True)
    except ValueError:
        toks = line.split()                                    # an unbalanced quote: split plainly, still judged
    verdicts = []
    for k, t in enumerate(toks):
        if not is_interpreter(t):
            continue
        i = k + 1
        while i < len(toks) and toks[i].startswith("-"):
            if toks[i] in _ENDING_OPTS:
                i = len(toks)
                break
            i += 2 if toks[i] in _VALUE_OPTS else 1
        v = judge(toks[i:]) if i < len(toks) else None
        if v:
            verdicts.append(v)
    return verdicts


def scan_script(text: str) -> dict:
    out = {"guarded": 0, "unguarded": []}
    for line in logical_lines(text):
        for v in scan_line(line):
            if v == "guarded":
                out["guarded"] += 1
            else:
                out["unguarded"].append(line.strip()[:160])
    return out


def scan_rows(text: str) -> dict:
    """Step rows (lane, name, entry, args...): the entry must be the guard, guarding a 1B entry."""
    out = {"guarded": 0, "unguarded": []}
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("\t")
        v = judge(f[2:])
        if v == "guarded":
            out["guarded"] += 1
        elif v == "unguarded" or os.path.basename(f[2]) not in (GUARD,):
            out["unguarded"].append("\t".join(f[:4])[:160])
    return out


def main(argv) -> int:
    here = Path(__file__).resolve().parent
    bad = 0
    for sh in sorted(here.glob("*.sh")):
        r = scan_script(sh.read_text())
        bad += len(r["unguarded"])
        print(f"script {sh.name}: {r['guarded']} guarded, {len(r['unguarded'])} unguarded {r['unguarded'][:2]}")
    for d in argv:
        for t in sorted(Path(d).glob("*-steps.tsv")):
            r = scan_rows(t.read_text())
            bad += len(r["unguarded"])
            print(f"rows {t.name}: {r['guarded']} guarded, {len(r['unguarded'])} unguarded {r['unguarded'][:2]}")
    print(f"GUARD-SCAN :: {'NONE UNGUARDED' if not bad else f'{bad} UNGUARDED'}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
