#!/usr/bin/env python3
"""Run every probe of the batch-0 ledger against the printed (comment-stripped, whitespace-collapsed) note source.

usage: check_ledger.py <worktree> [ledger.md] [--self-test]

  N:<file>::<text>   must occur in docs/analysis-note/<file>   (the new wording prints)
  X:<file>::<text>   must NOT occur in docs/analysis-note/<file> (the old wording no longer prints)
Several probes in one cell are joined by ` && `. Table cells escape a literal `|` as `\\|`.
Every row must carry at least one N: probe, and every row whose before-text differs from its after-text and is not
an insertion must carry an X: probe. Exit 1 on any failure.

--self-test plants two bad probes (an N: probe for text that does not print and an X: probe for text that does) in a
copy of the ledger and requires the check to fail on exactly those two rows.
"""
import re
import sys
import tempfile
from pathlib import Path

NOTE = "docs/analysis-note"


def printed(path: Path) -> str:
    src = path.read_text()
    src = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in src.splitlines())
    return re.sub(r"\s+", " ", src)


def cells(line: str) -> list[str]:
    body = line.strip()
    assert body.startswith("|") and body.endswith("|")
    parts = re.split(r"(?<!\\)\|", body[1:-1])
    return [p.strip().replace("\\|", "|") for p in parts]


def check(wt: Path, ledger: Path) -> tuple[int, int, int, list[str]]:
    cache: dict[str, str] = {}

    def text(f: str) -> str:
        if f not in cache:
            cache[f] = printed(wt / NOTE / f)
        return cache[f]

    rows = probes = 0
    fails: list[str] = []
    for line in ledger.read_text().splitlines():
        if not (line.startswith("| G") or line.startswith("| S11 ")):
            continue
        c = cells(line)
        if len(c) != 7:
            fails.append(f"malformed row ({len(c)} cells): {line[:80]}")
            continue
        rid, loc, terms, before, after, probe, note = c
        rows += 1
        kinds = set()
        for p in probe.split(" && "):
            p = p.strip().strip("`")
            m = re.match(r"([NX]):([\w.]+)::(.*)$", p, re.S)
            if not m:
                fails.append(f"{rid}: MALFORMED probe {p[:80]!r}")
                continue
            kind, f, lit = m.group(1), m.group(2), re.sub(r"\s+", " ", m.group(3))
            kinds.add(kind)
            probes += 1
            present = lit in text(f)
            if kind == "N" and not present:
                fails.append(f"{rid} {loc}: NOT FOUND in {f}: {lit[:100]!r}")
            if kind == "X" and present:
                fails.append(f"{rid} {loc}: STILL PRINTS in {f}: {lit[:100]!r}")
        if "N" not in kinds:
            fails.append(f"{rid}: row without a presence (N:) probe")
        if "X" not in kinds and before not in after:
            fails.append(f"{rid}: changed row without an absence (X:) probe")
    return rows, probes, len(fails), fails


def self_test(wt: Path, ledger: Path) -> int:
    lines = ledger.read_text().splitlines()
    idx = [i for i, l in enumerate(lines) if l.startswith("| G")]
    if len(idx) < 2:
        print("LEDGER SELF-TEST :: FAIL (fewer than two rows)")
        return 1
    a, b = idx[0], idx[len(idx) // 2]
    ca, cb = cells(lines[a]), cells(lines[b])
    # plant 1: an N: probe for text that cannot print; plant 2: an X: probe for the row's own (printing) after-text
    ca[5] = ca[5] + " && `N:" + ca[1].split(":")[0] + "::THIS SENTENCE WAS NEVER WRITTEN INTO THE NOTE`"
    cb[5] = cb[5] + " && `X:" + cb[1].split(":")[0] + "::" + cb[4] + "`"
    esc = lambda c: "| " + " | ".join(x.replace("|", "\\|") for x in c) + " |"
    lines[a], lines[b] = esc(ca), esc(cb)
    with tempfile.TemporaryDirectory() as d:
        bad = Path(d) / "ledger.md"
        bad.write_text("\n".join(lines) + "\n")
        rows, probes, nf, fails = check(wt, bad)
    hit = {f.split(" ")[0].rstrip(":") for f in fails}
    want = {ca[0], cb[0]}
    if nf == 2 and hit == want:
        print(f"LEDGER SELF-TEST :: PASS (2 planted bad probes, rows {sorted(want)}, both fail; nothing else fails)")
        return 0
    print(f"LEDGER SELF-TEST :: FAIL (expected failures on {sorted(want)}, got {nf}: {fails[:4]})")
    return 1


def main(argv: list[str]) -> int:
    wt = Path(argv[1])
    rest = [a for a in argv[2:] if not a.startswith("--")]
    ledger = Path(rest[0]) if rest else Path(__file__).with_name("ledger.md")
    if "--self-test" in argv:
        return self_test(wt, ledger)
    rows, probes, nf, fails = check(wt, ledger)
    for f in fails:
        print(f)
    print(f"ledger rows {rows}, probes {probes}, failures {nf}")
    return 1 if nf else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
