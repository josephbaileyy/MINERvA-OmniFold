"""The backstop's 300-draw calibration (schema /1, job 60771025, at 02e71a0b) against later code (the director's
rulings of 2026-11-05, with the audit's G1-G3): is the code that produced its per-cell SDs unchanged?

Those SDs are rates(Rx)[t]["a"]["sd_per_cell"], where Rx comes from _one_set over the state that prepare(a) and
_worker_init build (calibrate_main at 02e71a0b): fd_1b_c2.CAL300_ROOTS. fd_1b_c2.code_closure walks every module-level
statement they reach, definitions and module glue alike (tuple assignments, bare method calls such as
EXPECT.update(...), imports, for/if blocks), across the repository's own modules, and gives each one's normalized
source text (cut by its own positions, docstrings cut out by span; no ast.unparse, no tokenize) and its sha256.

This script runs code_closure as itself, executed from fd_1b_c2.py's text with only the standard library, so the same
code runs under any interpreter; it prints sys.version. Not seen by the walk: names reached only through getattr or
strings; library code; and calibrate_main's own lines between the four roots (printed for reading).

    python3 cal300_code_check.py OLD NEW [--write-pins nd-unfolding/fd_1b_cal300_pins.json]
        compare the closure at OLD with the closure at NEW (both read from git); exit 0 only if they are equal but
        for the labels fd_1b_c2.CAL300_EXEMPT names. --write-pins writes the pins file c2check reads.
    python3 cal300_code_check.py --verify-tree
        recompute the closure from this working tree and compare it with the committed pins, as c2check does.
Run from the repository root.
"""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RECORD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/a2-1/calib-run/calibration.json"
RULING = "the director, 2026-11-05: n=st['n'] equals 02e71a0b's call at st['n'] = 300 (bitwise test in test_fd_1b_a21_e2e)"
C2 = Path("nd-unfolding/fd_1b_c2.py")


def c2_parts() -> dict:
    """code_closure, cal300_closure_diff (c2check's own comparison), CODE_DIRS, CAL300_ROOTS and CAL300_EXEMPT,
    executed from fd_1b_c2.py's own text (no import of fd_1b_c2, so no numpy)."""
    want = {"code_closure", "cal300_closure_diff", "CODE_DIRS", "CAL300_ROOTS", "CAL300_EXEMPT", "CAL300_PINS"}
    nodes = [n for n in ast.parse(C2.read_text()).body
             if (isinstance(n, ast.FunctionDef) and n.name in want)
             or (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in want for t in n.targets))]
    ns: dict = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(C2), "exec"), ns)
    assert want <= set(ns), want - set(ns)
    return ns


def git_loader(rev: str, dirs):
    def load(m):
        for d in dirs:
            r = subprocess.run(["git", "show", f"{rev}:{d}/{m}.py"], capture_output=True, text=True)
            if r.returncode == 0:
                return f"{d}/{m}.py", r.stdout
        return None
    return load


def tree_loader(dirs):
    def load(m):
        for d in dirs:
            f = Path(d) / f"{m}.py"
            if f.is_file():
                return f"{d}/{m}.py", f.read_text()
        return None
    return load


def key(e) -> tuple:
    return e["module"], e["file"], e["label"]


def compare(old: list, new: list, exempt) -> tuple:
    """Pair entries by (module, path, label) in order; rows of (state, label) and whether only exempt labels differ."""
    rows, ok = [], True
    groups = {}
    for side, es in (("old", old), ("new", new)):
        for e in es:
            groups.setdefault(key(e), {"old": [], "new": []})[side].append(e)
    for k in sorted(groups):
        o, n = groups[k]["old"], groups[k]["new"]
        label = f"{k[0]}.{k[2]}"
        for i in range(max(len(o), len(n))):
            if i >= len(o):
                rows.append(("ADDED", label)); ok = False
            elif i >= len(n):
                rows.append(("MISSING", label)); ok = False
            elif o[i]["text_sha256"] == n[i]["text_sha256"]:
                rows.append(("SAME", label))
            else:
                rows.append(("EXEMPT" if label in exempt else "CHANGED", label))
                ok &= label in exempt
    return rows, ok


def main(argv) -> int:
    ns = c2_parts()
    print(f"python {sys.version}")
    print(f"code_closure from {C2} sha256 {hashlib.sha256(C2.read_bytes()).hexdigest()}")
    if argv and argv[0] == "--verify-tree":
        raw = (C2.parent / ns["CAL300_PINS"]).read_bytes()
        pins = json.loads(raw)
        missing, added = ns["cal300_closure_diff"](pins, tree_loader(ns["CODE_DIRS"]))
        ok = not missing and not added
        print(f"pins file sha256 {hashlib.sha256(raw).hexdigest()}: {len(pins['closure'])} statements; "
              f"missing or changed {missing[:4]}; added {added[:4]}")
        print(f"CAL300-PINS-VERIFY :: {'MATCH' if ok else 'MISMATCH'} :: python {sys.version.split()[0]}")
        return 0 if ok else 1
    old_rev, new_rev = argv[0], argv[1]
    old = ns["code_closure"](git_loader(old_rev, ns["CODE_DIRS"]), ns["CAL300_ROOTS"])
    new = ns["code_closure"](git_loader(new_rev, ns["CODE_DIRS"]), ns["CAL300_ROOTS"])
    rows, ok = compare(old, new, ns["CAL300_EXEMPT"])
    for state, label in rows:
        print(f"{state:8s} {label}")
    mods = sorted({e["module"] for e in old})
    print(f"reached at OLD: {len(old)} statements in {len(mods)} modules: {' '.join(mods)}")
    print(f"definitions (def/class): {sum(1 for e in old if e['text'].startswith(('def ', 'class ', '@', 'async def ')))}; "
          f"other statements (glue, imports, constants): {sum(1 for e in old if not e['text'].startswith(('def ', 'class ', '@', 'async def ')))}")
    src = git_loader(old_rev, ns["CODE_DIRS"])("fd_1b_c2")[1]
    cm = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "calibrate_main")
    print("calibrate_main's lines between the roots at OLD (for reading):")
    for line in ast.get_source_segment(src, cm).splitlines():
        if any(k in line for k in ("prepare(", "_worker_init(", "_one_set", "state = ", "Rx[", "rates(", "a.sets")):
            print("   ", line.strip())
    if "--write-pins" in argv:
        out = Path(argv[argv.index("--write-pins") + 1])
        rec_sha = json.loads(Path(RECORD).read_text())["code_sha256"]["fd_1b_c2.py"]
        old_sha = hashlib.sha256(subprocess.run(["git", "show", f"{old_rev}:nd-unfolding/fd_1b_c2.py"],
                                                capture_output=True, check=True).stdout).hexdigest()
        assert rec_sha == old_sha, f"the 300-draw record's fd_1b_c2 ({rec_sha[:8]}) is not {old_rev}'s ({old_sha[:8]})"
        exempt = {}
        for e in new:
            k = f"{e['module']}.{e['label']}"
            if k in ns["CAL300_EXEMPT"]:
                exempt[k] = {"text_sha256": e["text_sha256"], "rev": new_rev, "ruling": RULING}
        doc = {"schema": "fd-1b-cal300-pins/2", "rev": old_rev, "record": RECORD, "record_fd_1b_c2_sha256": rec_sha,
               "roots": [".".join(r) for r in ns["CAL300_ROOTS"]],
               "closure": [{k: e[k] for k in ("module", "file", "label", "text_sha256")} for e in old], "exempt": exempt}
        out.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
        print(f"wrote {out} sha256 {hashlib.sha256(out.read_bytes()).hexdigest()}")
    verdict = "IDENTICAL" if all(r[0] == "SAME" for r in rows) else "IDENTICAL BUT THE EXEMPT" if ok else "CHANGED"
    print(f"CAL300-CODE-CHECK :: {verdict} :: {len(old)} statements reached from {len(ns['CAL300_ROOTS'])} roots :: "
          f"exempt {list(ns['CAL300_EXEMPT'])} :: old={old_rev} new={new_rev} :: python {sys.version.split()[0]}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
