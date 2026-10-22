#!/usr/bin/env python3
"""Run every probe of ledger.md against the printed (comment-stripped, whitespace-collapsed) LaTeX source.

usage: check_ledger.py <worktree> [ledger.md] [--plant]

Probe kinds (several joined by ` && `):
  N:<file>::text   prints in this batch's <file> after the rewrite (main_note.tex: the abstract environment only)
  X:<file>::text   no longer prints in this batch's <file> (a removed false-as-read or incomplete statement)
  B:<file>::text   prints in the body file <file> (the support for a summary claim)
  P::text          prints in paper_body.tex;  MP::text  prints in the abstract of main_paper.tex
Rules: every row needs at least one N: probe; every row whose disposition is not META needs a B:, P: or MP: probe
(the support). Also checked: main_note.tex outside the abstract is byte-identical to origin/main, and
main_paper.tex and paper_body.tex are byte-identical to origin/main.
--plant adds three planted rows (a wrong N, a wrong X, a wrong B) and requires each to fail.
Exit 1 on any failure."""
import re, subprocess, sys
from pathlib import Path

args = [a for a in sys.argv[1:] if not a.startswith("--")]
plant = "--plant" in sys.argv
wt = Path(args[0]); ledger = Path(args[1] if len(args) > 1 else Path(__file__).with_name("ledger.md"))
D = wt / "docs/analysis-note"
BATCH = {"main_note.tex", "sec_execsummary.tex", "sec_intro.tex", "sec_fps.tex", "sec_summary.tex"}

def printed_of(src):
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in src.splitlines())
    return re.sub(r"\s+", " ", src)

def abstract(src):
    a = src.index("\\begin{abstract}"); b = src.index("\\end{abstract}")
    return src[a:b]

cache = {}
def text(key):
    if key not in cache:
        src = (D / key).read_text()
        if key == "main_note.tex":
            src = abstract(src)
        if key == "main_paper.tex":
            src = abstract(src)
        cache[key] = printed_of(src)
    return cache[key]

def run_row(rid, disp, probe):
    fails = []; kinds = set()
    for p in probe.split(" && "):
        p = p.strip().strip("`")
        m = re.match(r"(N|X|B):([\w.]+)::(.*)$", p) or re.match(r"(P|MP)()::(.*)$", p)
        if not m:
            fails.append(f"{rid}: MALFORMED probe {p!r}"); continue
        kind, f, lit = m.group(1), m.group(2), re.sub(r"\s+", " ", m.group(3))
        if kind == "P": f = "paper_body.tex"
        if kind == "MP": f = "main_paper.tex"
        if kind in "NX" and f not in BATCH:
            fails.append(f"{rid}: {kind} probe on a file outside the batch: {f}"); continue
        if kind == "B" and f in BATCH - {"sec_fps.tex"}:
            fails.append(f"{rid}: B probe must point into the body, not {f}"); continue
        kinds.add(kind)
        try:
            t = text(f)
        except FileNotFoundError:
            fails.append(f"{rid}: no such file {f}"); continue
        present = lit in t
        if kind == "X" and present:
            fails.append(f"{rid}: STILL PRINTED in {f}: {lit!r}")
        if kind != "X" and not present:
            fails.append(f"{rid}: NOT FOUND in {f}: {lit!r}")
    if "N" not in kinds:
        fails.append(f"{rid}: row without an N: probe")
    if not disp.startswith("META") and not (kinds & {"B", "P", "MP"}):
        fails.append(f"{rid}: row without a support probe (B:, P: or MP:)")
    return fails

rows = probes = 0; fails = []
for line in ledger.read_text().splitlines():
    if not line.startswith("| ") or line.startswith("| id ") or line.startswith("|---"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
    if len(cells) != 5:
        continue
    rid, fact, before, disp, probe = cells
    rows += 1; probes += probe.count(" && ") + 1
    fails += run_row(rid, disp, probe)

# protected text: outside the abstract of main_note.tex, and the paper sources
def git_show(path):
    return subprocess.run(["git", "-C", str(wt), "show", f"origin/main:docs/analysis-note/{path}"],
                          capture_output=True, text=True, check=True).stdout
base = git_show("main_note.tex"); now = (D / "main_note.tex").read_text()
cut = lambda s: (s[:s.index("\\begin{abstract}")], s[s.index("\\end{abstract}"):])
if cut(base) != cut(now):
    fails.append("PROTECTED: main_note.tex outside the abstract differs from origin/main")
for p in ("main_paper.tex", "paper_body.tex"):
    if git_show(p) != (D / p).read_text():
        fails.append(f"PROTECTED: {p} differs from origin/main")

if plant:
    planted = [
        ("PLANT-N", "KEEP", "N:sec_summary.tex::this sentence was never written && B:sec_5d.tex::Central values are reproducible only to this size."),
        ("PLANT-X", "KEEP", "X:sec_execsummary.tex::No other corrected five-dimensional covariance is used in its place. && B:sec_5d.tex::Central values are reproducible only to this size."),
        ("PLANT-B", "KEEP", "N:sec_summary.tex::Summary. && B:sec_5d.tex::the covariance passes its acceptance criteria"),
    ]
    ok = True
    for rid, disp, probe in planted:
        f = run_row(rid, disp, probe)
        print(f"  planted -> {f[0] if f else 'NO FAILURE'}")
        ok &= bool(f)
    print("plant test:", "PASS (all 3 planted probes fail)" if ok else "FAIL")
    if not ok:
        fails.append("plant test failed")

for f in fails:
    print(f)
print(f"ledger rows {rows}, probes {probes}, failures {len(fails)}")
sys.exit(1 if fails else 0)
