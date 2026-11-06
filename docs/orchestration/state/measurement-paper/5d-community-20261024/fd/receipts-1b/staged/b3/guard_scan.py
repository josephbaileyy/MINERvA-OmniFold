"""Does every binding-3 job line that runs fd_1b_mc, fd_1b_c2 or fd_1b_binning come through 1B's guarded launcher
(the director's ruling of 2026-11-05)? Two populations, each with its count printed so an empty one fails:
- every *.sh in this directory (b3/): binding 3's job and connect scripts, login-node steps included;
- every step row the stage 1 generator emits (fd_f1_lane.py runs each row's entry with the deploy as cwd).

A script line is parsed as a shell would split it (continuations joined, then shlex), not by a regex. Any token that
is a Python interpreter (python, python3, python3.11.14, a path to one, or a $PY... / $PYTHON... variable) starts an
invocation; the interpreter's own options are skipped with their values (-X, -W take one; -c, -m and "-", the stdin
script, end it). The next token is the script. An invocation whose script is a 1B entry module is UNGUARDED; one
whose script is the guard is GUARDED only if the guard's options (--declared, --root VALUE) are followed by "--"
and then a 1B entry module. A step row is GUARDED only if its entry is the guard, with the same shape.

Two rules close what an invocation parser cannot see (the auditor's review; the director's ruling, 2026-11-05):
- BY NAME: a line that names a 1B entry module anywhere (fd_1b_mc, fd_1b_c2 or fd_1b_binning, as .py, -m or a
  path, quoted or not) must be judged guarded and nothing else. The one exempt form is a sha256 manifest line
  ("<64 hex>  <path>"), which is data (a bound-blob list), not a command.
- INDIRECT FORMS are refused outright: `eval`, `bash|sh|zsh|dash -c`, and `source` or `.` of anything but a file
  of the deploy ("$DD/...").

    python3 -B guard_scan.py TABLES_DIR [...]      (prints the counts; exit 0 only with none unguarded and no
                                                   population empty)
"""
from __future__ import annotations

import os
import re
import shlex
import sys
from pathlib import Path

ENTRIES = ("fd_1b_mc.py", "fd_1b_c2.py", "fd_1b_binning.py")
GUARD = "fd_1b_noatime_guard.py"
_INTERP = re.compile(r"^(\$\{?PY(THON)?\w*\}?|python(\d+(\.\d+)*)?)$")
_NAMED = re.compile(r"\bfd_1b_(mc|c2|binning)\b")
_MANIFEST = re.compile(r"^\s*[0-9a-f]{64}\s+\S+\s*$")
_SHELLS = {"bash", "sh", "zsh", "dash"}
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
    toks = split(line)
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


def indirect(tokens: list[str]) -> str | None:
    """The first indirect form on a line, or None: eval, a shell's -c, or sourcing a file outside the deploy."""
    for k, t in enumerate(tokens):
        nxt = tokens[k + 1] if k + 1 < len(tokens) else ""
        if t == "eval":
            return "eval"
        if os.path.basename(t) in _SHELLS and nxt == "-c":
            return f"{os.path.basename(t)} -c"
        if t in ("source", ".") and nxt and not nxt.startswith(('$DD/', '"$DD/', '${DD}/')):
            return f"{t} {nxt}"
    return None


def split(line: str) -> list[str]:
    try:
        return shlex.split(line, comments=True, posix=True)
    except ValueError:
        return line.split()                                    # an unbalanced quote: split plainly, still judged


def scan_script(text: str) -> dict:
    """Every logical line judged: an indirect form, a line naming a 1B entry that is not wholly a guarded
    invocation, or an unguarded invocation is UNGUARDED (with its reason)."""
    out = {"guarded": 0, "unguarded": []}
    for line in logical_lines(text):
        why = indirect(split(line))
        v = scan_line(line)
        if not why:
            if "unguarded" in v:
                why = "an unguarded invocation"
            elif _NAMED.search(line) and not _MANIFEST.match(line) and not (v and set(v) == {"guarded"}):
                why = "names a 1B entry but is not a guarded invocation"
        if why:
            out["unguarded"].append(f"{why}: {line.strip()[:140]}")
        else:
            out["guarded"] += v.count("guarded")
    return out


def scan_rows(text: str) -> dict:
    """Step rows (lane, name, entry, args...): the entry must be the guard, guarding a 1B entry."""
    out = {"guarded": 0, "unguarded": []}
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("\t")
        v = judge(f[2:])
        if v == "guarded" and not indirect(f[2:]):
            out["guarded"] += 1
        else:
            out["unguarded"].append("\t".join(f[:4])[:160])
    return out


def main(argv) -> int:
    """Both populations must be non-empty, or the run fails (the auditor's B5): at least one *.sh in this directory with
    a positive total of guarded lines, and at least one TABLES_DIR, each existing and holding at least one *-steps.tsv
    with at least one row. An empty population prints its reason and exits 1, never "NONE UNGUARDED"."""
    here = Path(__file__).resolve().parent
    bad, empty = 0, []
    scripts = sorted(here.glob("*.sh"))
    if not scripts:
        empty.append(f"no *.sh in {here}")
    total = 0
    for sh in scripts:
        r = scan_script(sh.read_text())
        bad += len(r["unguarded"])
        total += r["guarded"]
        print(f"script {sh.name}: {r['guarded']} guarded, {len(r['unguarded'])} unguarded {r['unguarded'][:2]}")
    if scripts and total == 0:
        empty.append("the scripts hold no guarded 1B line")
    if not argv:
        empty.append("no TABLES_DIR given")
    for d in argv:
        tables = sorted(Path(d).glob("*-steps.tsv")) if Path(d).is_dir() else []
        if not tables:
            empty.append(f"no *-steps.tsv in {d}")
        for t in tables:
            r = scan_rows(t.read_text())
            bad += len(r["unguarded"])
            if r["guarded"] + len(r["unguarded"]) == 0:
                empty.append(f"{t.name} has no rows")
            print(f"rows {t.name}: {r['guarded']} guarded, {len(r['unguarded'])} unguarded {r['unguarded'][:2]}")
    for e in empty:
        print(f"EMPTY POPULATION: {e}")
    ok = not bad and not empty
    print(f"GUARD-SCAN :: {'NONE UNGUARDED' if ok else (f'{bad} UNGUARDED' if bad else 'AN EMPTY POPULATION')}"
          f"{f'; {len(empty)} empty' if empty and bad else ''}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
