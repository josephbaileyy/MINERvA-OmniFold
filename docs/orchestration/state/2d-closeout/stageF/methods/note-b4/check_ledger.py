#!/usr/bin/env python3
"""Check the b4 fact ledger against the worktree.

usage: check_ledger.py <worktree> [ledger.md] [--self-test]
N:file::text  must occur in docs/analysis-note/<file> (comment-stripped, whitespace-collapsed)
X:file::text  must NOT occur there
R:file::text  must occur in that records file (same directory)
Every MOVED row needs an X: and an R: probe; every KEEP row an N: probe.
Numeric audit: every numeric literal printed in before/<file> must still print in the worktree file, except the
multiset listed in NUMLOSS below (each loss is a ledger row).
--self-test plants a false N probe, a false X probe and an unlisted numeric loss and requires each to fail.
Exit 1 on any failure."""
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ["sec_validation.tex", "app_statmethods.tex", "app_guide.tex"]
NUMLOSS = {"sec_validation.tex": Counter({"2026": 1, "10": 2, "06": 1, "5": 1}),
           "app_statmethods.tex": Counter({"2026": 2, "10": 2, "11": 2, "50": 1, "205": 1}),
           "app_guide.tex": Counter()}
NUM = re.compile(r"(?<![\w.])\d+(?:\.\d+)?")


def printed(src: str) -> str:
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in src.splitlines())
    return re.sub(r"\s+", " ", src)


def run(wt: Path, ledger: Path, before: Path) -> int:
    d = wt / "docs/analysis-note"
    cache: dict[str, str] = {}

    def text(name: str) -> str:
        if name not in cache:
            cache[name] = printed((d / name).read_text())
        return cache[name]

    rows = probes = fails = 0
    for line in ledger.read_text().splitlines():
        if not line.startswith("| ") or line.startswith("| id ") or line.startswith("| file "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells) != 6:
            continue
        rid, _fact, _before, disp, _after, probe = cells
        rows += 1
        kinds = set()
        for p in probe.split(" && "):
            p = p.strip().strip("`")
            m = re.match(r"([NXR]):([\w.]+)::(.*)$", p)
            if not m:
                print(f"{rid}: MALFORMED probe {p!r}")
                fails += 1
                continue
            kind, fname, lit = m.group(1), m.group(2), re.sub(r"\s+", " ", m.group(3))
            kinds.add(kind)
            probes += 1
            present = lit in text(fname)
            if kind in "NR" and not present:
                print(f"{rid}: NOT FOUND in {fname}: {lit!r}")
                fails += 1
            if kind == "X" and present:
                print(f"{rid}: STILL PRINTS in {fname}: {lit!r}")
                fails += 1
        if disp.startswith("MOVED") and not {"X", "R"} <= kinds:
            print(f"{rid}: MOVED row needs X: and R: probes")
            fails += 1
        if disp.startswith("KEEP") and "N" not in kinds:
            print(f"{rid}: KEEP row without an N: probe")
            fails += 1
    numfails = 0
    for f in FILES:
        lost = Counter(NUM.findall(printed((before / f).read_text()))) - Counter(NUM.findall(text(f)))
        extra = lost - NUMLOSS[f]
        if extra:
            print(f"NUMERIC: {f} lost literals not in NUMLOSS: {dict(extra)}")
            numfails += 1
    print(f"ledger rows {rows}, probes {probes}, failures {fails}; numeric audit failures {numfails}")
    return 1 if fails or numfails else 0


def self_test(wt: Path, ledger: Path, before: Path) -> int:
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "ledger.md"
        bad.write_text(ledger.read_text() + "\n| Z1 | planted | -- | KEEP | -- | `N:sec_validation.tex::this sentence is not printed anywhere` |\n"
                       "| Z2 | planted | -- | KEEP | -- | `N:sec_validation.tex::Closure && X:sec_validation.tex::coverage` |\n")
        print("-- planted false N and X probes:")
        ok &= run(wt, bad, before) == 1
        fakewt = Path(tmp) / "wt"
        (fakewt / "docs/analysis-note").mkdir(parents=True)
        for f in FILES:
            t = (wt / "docs/analysis-note" / f).read_text()
            if f == "sec_validation.tex":
                t = t.replace("\\SI{1.69}{\\percent}", "\\SI{X}{\\percent}", 1)
            (fakewt / "docs/analysis-note" / f).write_text(t)
        for f in ("app_history.tex", "app_provenance.tex", "sec_method.tex"):
            (fakewt / "docs/analysis-note" / f).write_text((wt / "docs/analysis-note" / f).read_text())
        print("-- planted lost number (1.69):")
        ok &= run(fakewt, ledger, before) == 1
    print("SELF-TEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--self-test"]
    wt = Path(args[0])
    ledger = Path(args[1]) if len(args) > 1 else HERE / "ledger.md"
    before = HERE / "before"
    sys.exit(self_test(wt, ledger, before) if "--self-test" in sys.argv else run(wt, ledger, before))
