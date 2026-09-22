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

# ⚠ THE FINDINGS CELL IS MATCHED PERMISSIVELY, AND THE ROW SET IS ACCOUNTED FOR INDEPENDENTLY.
# The first version required the cell to begin with `**` or a digit. A `⚠`-prefixed cell -- a
# format THIS TABLE ALREADY USES (`| **agy #2, attempt 1** | ⚠ **NO VERDICT** |`) -- was invisible,
# so such a row vanished from every derived quantity AND from the ordering check, and the probe
# returned PASS on a ledger whose totals were wrong. An independent reviewer built exactly that
# case. A guard whose coverage rests on a formatting convention the guarded artifact already
# violates is not a guard, so:
#   * the findings cell may carry any leading decoration before its integer;
#   * every DATA ROW in the ledger block is counted separately, and a row the parsers cannot
#     classify is a REFUSAL, not a silent omission.
_CELL = r"[^|]*?\*{0,2}(\d+)\*{0,2}\s*\|"
SELF_ROW = re.compile(r"^\|\s*\*{0,2}(\d+)\s*\(self[^|]*\|" + _CELL)
AGY_ROW = re.compile(r"^\|\s*\*{0,2}agy[^|]*\|" + _CELL, re.I)
NOVERDICT_ROW = re.compile(r"^\|\s*\*{0,2}agy[^|]*\|[^|]*NO VERDICT[^|]*\|", re.I)
DATA_ROW = re.compile(r"^\|(?!\s*(?:round\b|-{2,}|:?-{2,}))")
TOTAL = re.compile(r"self rounds 1[–-](\d+)\s*=\s*([0-9+\s]+?)\s*=\s*(\d+);\s*"
                   r"independent reviews\s*=\s*([0-9+\s]+?)\s*=\s*(\d+);\s*TOTAL\s*(\d+)", re.S)


def main() -> int:
    if not REPORT.exists():
        print(f"[ledger] CANNOT LOOK :: no report at {REPORT}")
        return 2
    text = REPORT.read_text(encoding="utf-8")

    # the ledger block: from its header row to the first blank line after it
    lines = text.splitlines()
    try:
        h = next(i for i, l in enumerate(lines) if l.startswith("| round | findings | note |"))
    except StopIteration:
        print("[ledger] CANNOT LOOK :: no ledger header row")
        return 2
    end = next((i for i in range(h + 1, len(lines)) if not lines[i].startswith("|")), len(lines))
    block = lines[h + 1:end]

    selves, agys, unclassified, noverdict = [], [], [], 0
    for l in block:
        if not DATA_ROW.match(l):
            continue
        if re.match(r"^\|\s*:?-{2,}", l) or set(l.replace("|", "").strip()) <= set("-: "):
            continue
        m = SELF_ROW.match(l)
        if m:
            selves.append((int(m.group(1)), int(m.group(2)))); continue
        if NOVERDICT_ROW.match(l):
            noverdict += 1; continue
        m = AGY_ROW.match(l)
        if m:
            agys.append(int(m.group(1))); continue
        unclassified.append(l[:90])

    if unclassified:
        print("[ledger] CANNOT LOOK :: ledger rows the parser could not classify -- refusing "
              "rather than omitting them:")
        for u in unclassified:
            print(f"    {u}")
        return 2
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
    # ⚠ THE ADDENDS ARE COMPARED ELEMENTWISE, NOT JUST COUNTED AND SUMMED. A reviewer showed that
    # permuting the split (`3+0+0+…` -> `0+3+0+…`) kept the count and the sum and so passed, while
    # the per-round figures the report explicitly sends the reader to were wrong.
    def _ints(s_):
        return [int(x) for x in s_.split("+") if x.strip()]
    for label, stated_list, derived_list in (
            ("self addends", _ints(self_addends), [c for _, c in selves]),
            ("independent addends", _ints(agy_addends), agys)):
        if len(stated_list) == len(derived_list) and stated_list != derived_list:
            diff = [(i + 1, a, b) for i, (a, b) in enumerate(zip(stated_list, derived_list)) if a != b]
            print(f"  MISMATCH {label:26s} differs at {len(diff)} position(s): "
                  + ", ".join(f"#{i}: stated {a} vs ledger {b}" for i, a, b in diff[:5]))
            bad.append(f"{label} differ elementwise at {len(diff)} position(s)")
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
