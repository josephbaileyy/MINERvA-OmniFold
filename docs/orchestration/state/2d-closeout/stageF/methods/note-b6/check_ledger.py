#!/usr/bin/env python3
"""Batch b6 (Secs. 6-8). Run every probe of ledger.md against the worktree's printed (comment-stripped, whitespace-collapsed) LaTeX.

usage: check_ledger.py <tree> [ledger.md] [--self-test] [--git=<repo>] [--base=<rev>]
  <tree> is a worktree or a scratch copy; BASE spans are read from <repo> (default <tree>) at <rev> (default origin/main).

Probe kinds (several per row, joined by ` && `):
  N:<file>::text      text must occur in docs/analysis-note/<file>
  S:<label>::text     text must occur inside the region that starts at \\label{<label>} and ends at the next
                      \\subsection or \\section, in whichever batch file (sec_results, sec_3d, sec_eavailw) holds
                      the label. This is the "the paper's pointer still lands on the fact" probe.
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
opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
self_test = "--self-test" in sys.argv
wt = Path(args[0])                      # the tree whose files are probed (a worktree or a scratch copy)
git_repo = Path(opts.get("git", args[0]))  # where BASE spans are read with git show (default: the same tree)
base_rev = opts.get("base", "origin/main")
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


FILES = ("sec_results.tex", "sec_3d.tex", "sec_eavailw.tex")


def region(label):
    for f in FILES:
        src = strip((D / f).read_text())
        i = src.find(r"\label{%s}" % label)
        if i < 0:
            continue
        m = re.compile(r"\\(sub)?section\{").search(src, i + 1)
        return re.sub(r"\s+", " ", src[i: m.start() if m else len(src)])
    return None


def base_span(rel, a, b):
    out = subprocess.run(["git", "-C", str(git_repo), "show", f"{base_rev}:docs/analysis-note/{rel}"],
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
    plants = ["| Z99 | planted | - | KEEP | `S:sec:eavail-definition::this sentence is printed nowhere` |",
              # true in sec:eavailw-definitions, false in the region the paper points to for the 135 MeV fact
              "| Z98 | planted | - | KEEP | `S:sec:eavail-definition::the information added by $W$ has not been measured` |",
              "| Z97 | planted | - | KEEP | `BASE:sec_results.tex::Every block is computed||6.410` |",  # an edited span
              "| Z96 | planted | - | REMOVED | `X:sec_3d.tex::so its materiality is not established` |",  # a kept guardrail
              "| Z95 | planted | - | KEEP | `N:sec_eavailw.tex::as their captions specify` |"]  # removed meta text
    for pl in plants:
        _, _, f = run([pl])
        print(f"SELF-TEST {pl[2:5]}: {'FIRED (good)' if f else 'SILENT (bad)'}")
        if not f:
            sys.exit(1)
    _, _, f = run(["| Z90 | control | - | KEEP | `S:sec:eavailw-definitions::the information added by $W$ has not been measured` |"])
    print(f"SELF-TEST control Z90 (true probe): {'SILENT (good)' if not f else 'FIRED (bad)'}")
    if f:
        sys.exit(1)
rows, probes, fails = run(lines)
print(f"ledger rows {rows}, probes {probes}, failures {fails}")
sys.exit(1 if fails else 0)
