#!/usr/bin/env python3
"""Mutation suite for probe-20260922-ledger-reconciles.py (the loop-ledger guard).

WHY THIS FILE EXISTS, AND WHY IT IS COMMITTED. The guard it tests has been defeated by
independent reviewers TWICE. Review #7 found it blind to a `⚠`-prefixed findings cell -- a format
used INSIDE the very table it parses. It was "hardened" by inspection. Review #8 then defeated the
hardened version four more ways, every one a fail-OPEN (exit 0 on a stale ledger).

Two rounds of hardening-by-inspection did not converge. This suite did.

⚠ AND THEN THE CLAIM ABOUT THIS SUITE WAS ITSELF THE NEXT DEFECT. `KNOWN_ISSUES` row 69 said the
guard "now carries a 13-case mutation suite ... all caught". It did not: the suite had been run in
a scratch directory and never committed, so the row prescribed a remedy ("do not ship a guard for a
format-bearing artifact without a mutation suite in that artifact's own formats") and claimed to
have applied it, while the tree contained no such file. Independent review #9 measured that. An
uncommitted result is not a result. Hence this file.

Run: python3 docs/orchestration/probes/probe-20260922-ledger-guard-mutations.py
Exit 0 = every defeating mutation was caught AND every control behaved. Exit 1 = a mutation
returned a PASS on a stale ledger, which is the failure this guard exists to prevent.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GUARD = HERE / "probe-20260922-ledger-reconciles.py"
REPORT = HERE.parent / "REPORT-20260922-review-residue.md"

# The live TOTAL sentence, matched by shape so this suite does not go stale every round.
TOTAL_RE = re.compile(r"\*\*TOTAL: self rounds 1[–-]\d+ = [0-9+]+ = (\d+);", re.S)


def _anchor(text):
    """The last self row -- where a new row would be appended."""
    rows = re.findall(r"^\| \d+ \(self\) \| \*\*\d+\*\* \|", text, re.M)
    if not rows:
        raise SystemExit("[mutations] CANNOT LOOK :: no self rows in the report")
    return rows[-1]


def run_guard(workdir):
    r = subprocess.run([sys.executable, str(workdir / "probes" / GUARD.name)],
                       capture_output=True, text=True)
    return r.returncode


def main() -> int:
    if not GUARD.exists() or not REPORT.exists():
        print("[mutations] CANNOT LOOK :: guard or report missing")
        return 2
    orig = REPORT.read_text(encoding="utf-8")
    anchor = _anchor(orig)
    m = TOTAL_RE.search(orig)
    if not m:
        print("[mutations] CANNOT LOOK :: no TOTAL sentence of the expected shape")
        return 2
    total_line = m.group(0)
    stale_total = total_line.replace(f"= {m.group(1)};", "= 9999;")

    # (label, mutated-text builder, acceptable exit codes)
    # 1 = refused with a named mismatch, 2 = refused as unparseable. Both are CLOSED.
    # 0 on a stale ledger is the fail-OPEN this suite exists to catch.
    CASES = [
        ("quoted-but-stale 2nd TOTAL, live one corrupted",
         lambda s: s.replace(total_line, "> (withdrawn) " + total_line + "\n\n" + stale_total, 1), (1, 2)),
        ("contradictory TOTAL appended after the live one",
         lambda s: s + "\n\n**TOTAL: self rounds 1-25 = 1+1 = 2; independent reviews = 1+1 = 2; TOTAL 999.**\n", (1, 2)),
        ("new agy row indented two spaces",
         lambda s: s.replace(anchor, anchor + "\n  | **agy #99 (independent)** | **6** | six |", 1), (1, 2)),
        ("new agy row indented with a tab",
         lambda s: s.replace(anchor, anchor + "\n\t| **agy #99 (independent)** | **6** | six |", 1), (1, 2)),
        ("self row whose first cell begins 'round'",
         lambda s: s.replace(anchor, anchor + "\n| round 99 (self) | **3** | three |", 1), (1, 2)),
        ("agy row whose cell MENTIONS 'NO VERDICT' beside an integer",
         lambda s: s.replace(anchor, anchor + "\n| **agy #99 (independent)** | **5** after a NO VERDICT retry | x |", 1), (1, 2)),
        ("agy cell carrying TWO integers",
         lambda s: s.replace(anchor, anchor + "\n| **agy #99 (independent)** | 5 of 9 | x |", 1), (1, 2)),
        ("agy cell with no integer and no NO VERDICT",
         lambda s: s.replace(anchor, anchor + "\n| **agy #99 (independent)** | pending | x |", 1), (1, 2)),
        # ⚠ this case caught a defect in THIS SUITE first: the original builder was
        # `anchor.replace("**", "", 2)`, which yields `| N (self) | 0 |` -- a perfectly VALID row.
        # The mutation never reached the guard, and the resulting exit 0 looked like a fail-open
        # in the guard. A mutation that does not mutate tests nothing. Rebuild the cell instead.
        ("self findings cell unparseable",
         lambda s: s.replace(anchor, re.sub(r"\| \*\*\d+\*\* \|$", "| none found |", anchor), 1), (1, 2)),
        ("an agy row deleted outright",
         lambda s: s.replace("| **agy #7 (independent)** |", "| xx |", 1), (1, 2)),
        ("TOTAL left stale after a real new review row",
         lambda s: s.replace(anchor, anchor + "\n| **agy #99 (independent)** | **6** | six |", 1), (1, 2)),
        ("a duplicated self row",
         lambda s: s.replace(anchor, anchor + "\n" + anchor, 1), (1, 2)),
        # --- review #9's six defeats. Three are one CLASS: any non-table line inside the block
        # truncated it, and every row below vanished. Review #8's "indented row" repair had fixed
        # the instance only.
        ("HTML comment inside the table + stale TOTAL",
         lambda s: s.replace(anchor, "<!-- note -->\n" + anchor, 1).replace(total_line, stale_total, 1), (1, 2)),
        ("whitespace-only line inside the table + stale TOTAL",
         lambda s: s.replace(anchor, "   \n" + anchor, 1).replace(total_line, stale_total, 1), (1, 2)),
        ("blockquote line inside the table + stale TOTAL",
         lambda s: s.replace(anchor, "> aside\n" + anchor, 1).replace(total_line, stale_total, 1), (1, 2)),
        ("decoy QUOTED ledger table above the live one",
         lambda s: s.replace("| round | findings | note |",
                             "| round | findings | note |\n|---|---|---|\n| 1 (self) | **0** | decoy |\n\n"
                             "| round | findings | note |", 1), (1, 2)),
        ("agy row reads **-13** while the TOTAL addend says 13",
         lambda s: s.replace("| **agy #8b (independent)** | **13** |",
                             "| **agy #8b (independent)** | **-13** |", 1), (1, 2)),
        ("a real review hidden behind a NO VERDICT cell",
         lambda s: s.replace(anchor, anchor + "\n| **agy #99 (independent)** | \u26a0 **NO VERDICT** \u2014 ended after finding six defects | x |", 1), (1, 2)),
        # controls: these must NOT refuse
        ("CONTROL untouched ledger", lambda s: s, (0,)),
    ]

    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        (work / "probes").mkdir()
        shutil.copy2(GUARD, work / "probes" / GUARD.name)
        target = work / REPORT.name

        failures = []
        for label, build, want in CASES:
            target.write_text(build(orig), encoding="utf-8")
            rc = run_guard(work)
            ok = rc in want
            print(f"  {'OK ' if ok else '*** FAIL-OPEN ***'} {label:56s} exit={rc} want={want}")
            if not ok:
                failures.append((label, rc, want))

    print()
    if failures:
        print(f"[mutations] FAIL :: {len(failures)} of {len(CASES)} case(s) behaved wrongly")
        for label, rc, want in failures:
            print(f"    {label}: exit {rc}, wanted one of {want}")
        return 1
    print(f"[mutations] PASS :: {len(CASES)} cases, every defeating shape refused, controls clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
