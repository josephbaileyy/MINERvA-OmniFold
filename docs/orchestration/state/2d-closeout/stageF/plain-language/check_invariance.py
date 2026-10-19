#!/usr/bin/env python3
"""Plain-language pass (PLAIN-LANGUAGE.md §4): mechanical invariance of the rewritten deliverable sources.

For each deliverable it compares the base commit with the working tree:
  - the multiset of digit numerals in non-comment text;
  - the multiset of value macros (those defined in values.tex / values_inference.tex) used in non-comment text;
  - the multisets of \\cite keys, \\ref/\\eqref/\\autoref targets and \\label names;
  - the base's comment lines (every one must survive, possibly moved; additions are listed).
It also lists changed files outside the brief's scope. It prints every difference and exits 1 if there is any,
so a difference must be explained in the implementation record, never silently absorbed.

  python3 -I check_invariance.py <repo-root> <base-sha>
"""
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
BASE = sys.argv[2]
AN = "docs/analysis-note/"
DELIVERABLES = {
    "paper": ["main_paper.tex", "paper_body.tex"],
    "primer": ["main_primer.tex", "primer_body.tex"],
    "note": ["main_note.tex", "sec_execsummary.tex", "sec_summary.tex", "sec_systematics.tex",
             "sec_results.tex", "sec_validation.tex"],
}
IN_SCOPE = {AN + f for fs in DELIVERABLES.values() for f in fs}
# records of this pass may change too
RECORD_PREFIX = "docs/orchestration/"


def base_text(rel):
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE}:{rel}"], check=True,
                          capture_output=True, text=True).stdout


def split(text):
    body, comments = [], []
    for ln in text.splitlines():
        m = re.search(r"(?<!\\)%", ln)
        if m:
            body.append(ln[:m.start()])
            c = ln[m.start():].strip()
            if c.strip("% "):
                comments.append(c)
        else:
            body.append(ln)
    return "\n".join(body), comments


def value_macros():
    names = set()
    for f in ("values.tex", "values_inference.tex"):
        t = (ROOT / AN / f).read_text()
        names |= set(re.findall(r"\\(?:re)?newcommand\{?\\([A-Za-z]+)\}?", t))
    return names


VM = value_macros()


def features(text):
    body, comments = split(text)
    nums = Counter(re.findall(r"(?<![\\\w.])\d+(?:\.\d+)?", body))
    macros = Counter(m for m in re.findall(r"\\([A-Za-z]+)", body) if m in VM)
    cites = Counter(k.strip() for g in re.findall(r"\\cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", body)
                    for k in g.split(","))
    refs = Counter(k.strip() for g in re.findall(r"\\(?:eq|auto|page)?ref\{([^}]*)\}", body) for k in g.split(","))
    labels = Counter(re.findall(r"\\label\{([^}]*)\}", body))
    return {"numerals": nums, "value macros": macros, "cite keys": cites, "ref targets": refs,
            "labels": labels}, Counter(comments)


bad = False
for name, files in DELIVERABLES.items():
    old_f, new_f = {}, {}
    old_c, new_c = Counter(), Counter()
    for f in files:
        fo, co = features(base_text(AN + f))
        fn, cn = features((ROOT / AN / f).read_text())
        for k in fo:
            old_f[k] = old_f.get(k, Counter()) + fo[k]
            new_f[k] = new_f.get(k, Counter()) + fn[k]
        old_c += co
        new_c += cn
    print(f"== {name}")
    for k in old_f:
        lost = old_f[k] - new_f[k]
        gained = new_f[k] - old_f[k]
        if lost or gained:
            bad = True
            print(f"  [DIFF] {k}: lost {dict(lost)}  gained {dict(gained)}")
        else:
            print(f"  [SAME] {k} ({sum(old_f[k].values())})")
    lost_c = old_c - new_c
    if lost_c:
        bad = True
        print(f"  [DIFF] comment lines lost ({sum(lost_c.values())}):")
        for c in lost_c.elements():
            print(f"      {c}")
    else:
        print(f"  [SAME] comment lines: all {sum(old_c.values())} base lines survive")
    added_c = new_c - old_c
    if added_c:
        print(f"  [INFO] comment lines added ({sum(added_c.values())}):")
        for c in added_c.elements():
            print(f"      {c}")

changed = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-only", BASE, "--"], check=True,
                         capture_output=True, text=True).stdout.split()
untracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--others", "--exclude-standard"], check=True,
                           capture_output=True, text=True).stdout.split()
outside = [p for p in changed + untracked if p not in IN_SCOPE and not p.startswith(RECORD_PREFIX)]
print("== files changed outside scope")
if outside:
    bad = True
    for p in outside:
        print(f"  [DIFF] {p}")
else:
    print("  [SAME] none")
print("check_invariance:", "DIFFERENCES (each must be explained)" if bad else "ALL SAME")
sys.exit(1 if bad else 0)
