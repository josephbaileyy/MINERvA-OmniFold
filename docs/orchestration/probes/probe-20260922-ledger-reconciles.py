#!/usr/bin/env python3
"""Assert that REPORT-20260922-review-residue.md's TOTAL line reconciles with its own ledger.

WHY THIS EXISTS. Six independent adversarial reviews of one session found, between them, that the
loop ledger's hand-written totals and the prose around them were stale -- every time, and almost
nothing else. The cause is mechanical: each review must be RECORDED, and recording it invalidates
any hand-maintained sum of the table it was added to.

Correcting each stale copy after each review does not work; it was tried repeatedly and the next
review found the next copy. `KNOWN_ISSUES.md` row 65 states the general lesson -- an assurance a
later lane cannot re-run is not evidence, and the repo already owns instruments for exactly this
shape. So the totals are no longer defended by care; they are defended by this check.

Exit 0 = the stated totals equal the ledger's own column sums. Exit 1 = they do not, naming both.
Exit 2 = the ledger could not be parsed, which is a failure, not a pass.
"""
import re
import sys
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1] / "REPORT-20260922-review-residue.md"

SELF_ROW = re.compile(r"^\|\s*\*{0,2}(\d+)\s*\(self[^|]*\|\s*\*{0,2}(\d+)\*{0,2}\s*\|")
AGY_ROW = re.compile(r"^\|\s*\*{0,2}agy[^|]*\|\s*\*{0,2}(\d+)\*{0,2}\s*\|", re.I)
TOTAL = re.compile(r"self rounds 1[–-](\d+)\s*=\s*([0-9+\s]+?)\s*=\s*(\d+);\s*"
                   r"independent reviews\s*=\s*([0-9+\s]+?)\s*=\s*(\d+);\s*TOTAL\s*(\d+)", re.S)


def main() -> int:
    if not REPORT.exists():
        print(f"[ledger] CANNOT LOOK :: no report at {REPORT}")
        return 2
    text = REPORT.read_text(encoding="utf-8")

    selves = [(int(a), int(b)) for a, b in
              (m.groups() for m in (SELF_ROW.match(l) for l in text.splitlines()) if m)]
    agys = [int(m.group(1)) for m in
            (AGY_ROW.match(l) for l in text.splitlines()) if m]
    if not selves or not agys:
        print(f"[ledger] CANNOT LOOK :: parsed {len(selves)} self rows, {len(agys)} agy rows")
        return 2

    flat = re.sub(r"\s+", " ", text)
    m = TOTAL.search(flat)
    if not m:
        print("[ledger] CANNOT LOOK :: no TOTAL line matching the expected shape")
        return 2

    rounds = [n for n, _ in selves]
    bad = []
    if rounds != list(range(1, len(rounds) + 1)):
        bad.append(f"self rounds are not 1..N in order: {rounds}")
    if len(set(rounds)) != len(rounds):
        bad.append(f"DUPLICATED self rows: {rounds}")

    self_sum = sum(c for _, c in selves)
    agy_sum = sum(agys)
    stated_last, self_addends, stated_self, agy_addends, stated_agy, stated_total = m.groups()

    checks = [
        ("last self round", int(stated_last), rounds[-1]),
        ("self total", int(stated_self), self_sum),
        ("independent total", int(stated_agy), agy_sum),
        ("grand total", int(stated_total), self_sum + agy_sum),
        ("self addend count", len([x for x in self_addends.split("+") if x.strip()]), len(selves)),
        ("independent addend count", len([x for x in agy_addends.split("+") if x.strip()]), len(agys)),
    ]
    for label, stated, derived in checks:
        mark = "ok " if stated == derived else "MISMATCH"
        print(f"  {mark} {label:26s} stated={stated:<5d} derived from ledger={derived}")
        if stated != derived:
            bad.append(f"{label}: stated {stated}, ledger says {derived}")

    if bad:
        print("\n[ledger] FAIL :: the TOTAL line does not reconcile with its own table")
        for b in bad:
            print(f"    {b}")
        return 1
    print(f"\n[ledger] PASS :: {len(selves)} self rounds and {len(agys)} independent reviews reconcile")
    return 0


if __name__ == "__main__":
    sys.exit(main())
