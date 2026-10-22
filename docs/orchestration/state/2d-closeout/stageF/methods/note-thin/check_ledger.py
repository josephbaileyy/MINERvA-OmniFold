#!/usr/bin/env python3
"""Run every probe of ledger.md (records-citation thinning) against the worktree.

usage: check_ledger.py <worktree> [ledger.md] [--plant]
N:f::text  occurs in printed (comment-stripped, whitespace-collapsed) docs/analysis-note/<f>
X:f::text  does NOT occur there
R:f::text  occurs in printed docs/analysis-note/<f>, a records file (app_history, app_provenance, *_records)
Every row needs at least one probe. Also: the posted note's closure carries exactly the KEEP citations of
citations.md (19) and the base copies carry 71. --plant adds a false N:, X: and R: probe and requires all three to
fail. Exit 1 on any failure."""
import re
import sys
from pathlib import Path

args = [a for a in sys.argv[1:] if not a.startswith("--")]
wt = Path(args[0])
ledger = Path(args[1]) if len(args) > 1 else Path(__file__).with_name("ledger.md")
D = wt / "docs/analysis-note"
BASE = Path(__file__).with_name("base")
RECORDS = ("app_history.tex", "app_provenance.tex", "app_release_records.tex", "app_codebase_records.tex",
           "main_records.tex")
COMMENT = re.compile(r"(?<!\\)%[^\n]*")
cache = {}


def text(name, root=D):
    if (name, root) not in cache:
        cache[(name, root)] = re.sub(r"\s+", " ", COMMENT.sub("", (root / name).read_text()))
    return cache[(name, root)]


def run(rid, probe):
    m = re.match(r"([NXR]):([\w.]+)::(.*)$", probe, re.S)
    if not m:
        return f"{rid}: MALFORMED probe {probe!r}"
    kind, f, lit = m.groups()
    if kind == "R" and f not in RECORDS:
        return f"{rid}: R probe names {f}, which is not a records file"
    if not (D / f).exists():
        return f"{rid}: no file {f}"
    lit = re.sub(r"\s+", " ", lit).strip()
    found = lit in text(f)
    if kind in "NR" and not found:
        return f"{rid}: NOT FOUND in {f}: {lit[:90]!r}"
    if kind == "X" and found:
        return f"{rid}: STILL PRINTED in {f}: {lit[:90]!r}"
    return None


def closure_cites(root):
    seen, n = set(), 0

    def walk(name):
        nonlocal n
        if name in seen or not (root / name).exists():
            return
        seen.add(name)
        t = text(name, root)
        n += t.count(r"\cite{NoteRecords2026}")
        for inc in re.findall(r"\\(?:input|include)\{([^}]+)\}", t):
            walk(inc if inc.endswith(".tex") else inc + ".tex")
    walk("main_note.tex")
    return n


rows = probes = 0
fails = []
for line in ledger.read_text().splitlines():
    if not re.match(r"\| [FG]", line):
        continue
    cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip()[1:-1])]
    rid, probe = cells[0], cells[-1]
    rows += 1
    ps = [p.strip().strip("`") for p in probe.split(" && ") if p.strip().strip("`")]
    if not ps:
        fails.append(f"{rid}: row without a probe")
    for p in ps:
        probes += 1
        r = run(rid, p)
        if r:
            fails.append(r)
n_after, n_base = closure_cites(D), closure_cites(BASE)
print(f"posted-note citations of NoteRecords2026: base copies {n_base}, worktree {n_after}")
if (n_base, n_after) != (71, 19):
    fails.append(f"citation counts {n_base} -> {n_after}, expected 71 -> 19")
if "--plant" in sys.argv:
    planted = [run("PLANT-N", "N:sec_systematics.tex::match to $5.5\\times10^{-15}$"),
               run("PLANT-X", "X:sec_systematics.tex::(Ref.~\\cite{NoteRecords2026}, \\texttt{flux-index})"),
               run("PLANT-R", "R:app_history.tex::the Flux band was \\SI{4.98}{\\percent} without MAT's constraint")]
    ok = all(planted)
    for r in planted:
        print("  planted ->", r)
    print(f"plant test: {'PASS (all 3 planted probes fail)' if ok else 'FAIL (a planted probe passed)'}")
    if not ok:
        fails.append("plant test")
for f in fails:
    print(f)
print(f"ledger rows {rows}, probes {probes}, failures {len(fails)}")
sys.exit(1 if fails else 0)
