#!/usr/bin/env python3
"""Run every probe of ledger.md against the worktree's printed (comment-stripped, whitespace-collapsed) LaTeX.

usage: check_ledger.py <worktree> [ledger.md] [--self-test]

Probe kinds (several per row, joined by ` && `):
  N:<file>::text      text must occur in docs/analysis-note/<file>
  S:<label>::text     text must occur in sec_joint.tex inside the region that starts at \\label{<label>} and ends
                      at the next \\subsection (for a label placed after a \\paragraph: at the next \\paragraph or
                      \\subsection). This is the "the paper's pointer still lands on the fact" probe.
  X:<file>::text      text must NOT occur in <file>
  BASE:<file>::a||b   the raw bytes (comments and line breaks kept) from the first `a` to the next `b` must be
                      identical in origin/main and in the worktree (byte-identity of protected text)
Rows: every KEEP/COLLAPSED row needs at least one N: or S: probe; a REMOVED row needs an X: probe.
--self-test plants a row with a false probe and requires the checker to fail on it.
Exit 1 on any failure."""
import re
import subprocess
import sys
from pathlib import Path

args = [a for a in sys.argv[1:] if not a.startswith("--")]
self_test = "--self-test" in sys.argv
wt = Path(args[0])
ledger = Path(args[1]) if len(args) > 1 else Path(__file__).with_name("ledger.md")
D = wt / "docs/analysis-note"


def strip(src):
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in src.splitlines())
    return src


def printed(path):
    return re.sub(r"\s+", " ", strip(path.read_text()))


cache = {}


def text(key):
    if key not in cache:
        cache[key] = printed(D / key)
    return cache[key]


def region(label):
    src = strip((D / "sec_joint.tex").read_text())
    i = src.find(r"\label{%s}" % label)
    if i < 0:
        return None
    before = src[:i].rstrip()
    para = re.search(r"\\paragraph\{[^}]*\}\s*$", before) is not None
    stop = re.compile(r"\\(sub)?section\{|\\paragraph\{" if para else r"\\(sub)?section\{")
    m = stop.search(src, i + 1)
    return re.sub(r"\s+", " ", src[i: m.start() if m else len(src)])


def base_span(rel, a, b):
    out = subprocess.run(["git", "-C", str(wt), "show", f"origin/main:docs/analysis-note/{rel}"],
                         capture_output=True, text=True, check=True).stdout
    new = (D / rel).read_text()
    spans = []
    for s in (out, new):
        i = s.find(a)
        j = s.find(b, i + len(a)) if i >= 0 else -1
        spans.append(s[i: j + len(b)] if i >= 0 and j >= 0 else None)
    return spans


def run(lines):
    rows = fails = probes = 0
    for line in lines:
        if not line.startswith("| ") or line.startswith("| id ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells) != 5:
            continue
        rid, fact, before, disp, probe = cells
        rows += 1
        kinds = set()
        for p in probe.split(" && "):
            p = p.strip().strip("`")
            m = re.match(r"(N|S|X|BASE):([\w.:-]+)::(.*)$", p)
            if not m:
                print(f"{rid}: MALFORMED probe {p!r}"); fails += 1; continue
            kind, where, lit = m.groups()
            kinds.add(kind)
            probes += 1
            if kind == "BASE":
                a, b = lit.split("||")
                old, new = base_span(where, a, b)
                if old is None or old != new:
                    print(f"{rid}: BASE span differs or missing in {where}: {a!r}..{b!r}"); fails += 1
                continue
            lit = re.sub(r"\s+", " ", lit)
            if kind == "S":
                hay = region(where)
                if hay is None:
                    print(f"{rid}: label {where} not found"); fails += 1; continue
            else:
                hay = text(where)
            found = lit in hay
            if kind == "X" and found:
                print(f"{rid}: STILL PRINTED in {where}: {lit!r}"); fails += 1
            elif kind != "X" and not found:
                print(f"{rid}: NOT FOUND in {where}: {lit!r}"); fails += 1
        if disp.startswith(("KEEP", "COLLAPSED", "REWORDED")) and not kinds & {"N", "S", "BASE"}:
            print(f"{rid}: KEEP row without a positive probe"); fails += 1
        if disp.startswith("REMOVED") and "X" not in kinds:
            print(f"{rid}: REMOVED row without an X: probe"); fails += 1
    return rows, probes, fails


lines = ledger.read_text().splitlines()
if self_test:
    plants = ["| Z99 | planted | - | KEEP | `S:sec:joint5d-lost::this sentence is printed nowhere` |",
              "| Z98 | planted | - | KEEP | `S:sec:joint5d-lost::Computing time limits interrupted` && "
              "`S:sec:joint5d-ch::Computing time limits interrupted` |",  # true in one region, false in another
              "| Z97 | planted | - | KEEP | `BASE:sec_joint.tex::This section||joint` |",  # an edited span
              "| Z96 | planted | - | REMOVED | `X:sec_joint.tex::which has not been shown` |"]  # a kept guardrail
    for pl in plants:
        _, _, f = run([pl])
        print(f"SELF-TEST {pl[2:5]}: {'FIRED (good)' if f else 'SILENT (bad)'}")
        if not f:
            sys.exit(1)
    _, _, f = run(["| Z95 | control | - | KEEP | `S:sec:joint5d-lost::Computing time limits interrupted` |"])
    print(f"SELF-TEST control Z95 (true probe): {'SILENT (good)' if not f else 'FIRED (bad)'}")
    if f:
        sys.exit(1)
rows, probes, fails = run(lines)
print(f"ledger rows {rows}, probes {probes}, failures {fails}")
sys.exit(1 if fails else 0)
