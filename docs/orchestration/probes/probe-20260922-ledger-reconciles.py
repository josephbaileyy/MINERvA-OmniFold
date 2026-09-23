#!/usr/bin/env python3
"""Assert that REPORT-20260922-review-residue.md's TOTAL line reconciles with its own ledger.

WHY THIS EXISTS. Independent adversarial reviews of one session repeatedly found the loop ledger's
hand-written totals, and the prose around them, stale. The cause is mechanical: each review must be
RECORDED, and recording it invalidates any hand-maintained sum of the table it was added to.

⚠ THIS DOCSTRING ONCE OVERSTATED THAT. It read "Six independent adversarial reviews ... found ...
every time, and almost nothing else". Both halves are false and BOTH WERE ALREADY WITHDRAWN at
KNOWN_ISSUES row 66 before this file was written -- the withdrawal reached the row and not the
instrument, which is row 66's own subject. "Almost nothing else": review #3 alone found a wrong
count in VL145, a logic bug in committed probe code, and a release-package sourcing defect.
"Every time": review #1 ran BEFORE this ledger existed (its fixes landed at 0d913d43 00:08:17;
the report was created at 6a411ed0 00:17:11). The counts live in the ledger; none is restated here.

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
# ⚠ THE FINDINGS CELL IS EXTRACTED AND THEN ADJUDICATED -- IT IS NOT PATTERN-RACED.
# An earlier version tried NOVERDICT_ROW and AGY_ROW as competing patterns. An agy row whose
# findings cell merely MENTIONED "NO VERDICT" (`| **5** after a NO VERDICT retry |`) matched
# neither as an integer nor cleanly as a no-verdict row, and was dropped SILENTLY -- the exact
# fail-open this file claims to have closed. So: take cell 2 whole, then decide.
#   exactly one integer      -> that is the count
#   no integer + "NO VERDICT" -> a recorded non-verdict, counted as such
#   anything else             -> REFUSE. Ambiguity is not zero.
# ⚠ CELLS ARE SPLIT ON UNESCAPED PIPES AND A SEPARATOR IS RECOGNISED BY SHAPE, NOT BY PREFIX.
# Review #10 defeated the previous version twice more. (a) `DATA_ROW`'s negative lookahead
# skipped any row whose FIRST CELL began `--`, so `| -- **agy #12 …** | **6** | …` -- which
# renders as an ordinary body row, since Markdown only honours a delimiter row in position 2 --
# vanished from every total at exit 0. That is the same silent-skip shape review #9 closed for
# non-table lines, surviving one layer down in the prefix test. (b) A backslash-escaped pipe in
# cell 1 shifted the cell window, so the count was read out of the wrong cell. Splitting on
# `(?<!\\)\|` and testing separator-ness by SHAPE (every cell is dashes/colons) closes both, and
# removes the `-{2,}` prefix special case entirely.
SELF_LABEL = re.compile(r"^\*{0,2}(\d+)\s*\(self", re.I)
AGY_LABEL = re.compile(r"^[^A-Za-z0-9]*agy\b", re.I)
SEP_CELL = re.compile(r"^:?-{2,}:?$")


def _cells(line):
    """Cells of a Markdown row, split on UNESCAPED pipes."""
    parts = re.split(r"(?<!\\)\|", line)
    if parts and not parts[0].strip():
        parts = parts[1:]
    if parts and not parts[-1].strip():
        parts = parts[:-1]
    return [c.strip() for c in parts]


TOTAL = re.compile(r"self rounds 1[–-](\d+)\s*=\s*([0-9+\s]+?)\s*=\s*(\d+);\s*"
                   r"independent reviews\s*=\s*([0-9+\s]+?)\s*=\s*(\d+);\s*TOTAL\s*(\d+)", re.S)


def main() -> int:
    if not REPORT.exists():
        print(f"[ledger] CANNOT LOOK :: no report at {REPORT}")
        return 2
    text = REPORT.read_text(encoding="utf-8")
    # ⚠ READ WHAT A READER SEES. Review #11b hid a reconciling TOTAL in an HTML comment beside a
    # visible stale one, and the guard read the hidden one. Comments are invisible when rendered,
    # so they are removed before anything is parsed -- a ledger row or TOTAL inside one does not exist.
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)

    # ⚠ THE BLOCK ENDS AT A BLANK LINE, NOT AT THE FIRST NON-TABLE LINE.
    # Review #9 defeated the previous rule three ways at once. It read "end at the first line that
    # does not start with `|`", so ANY interloper inside the table -- an HTML comment, a stray
    # whitespace-only line, a blockquote, a wrapped row -- silently truncated the block and every
    # row BELOW it vanished from all totals, returning PASS on a stale ledger. Review #8's
    # "indented row" defeat had been repaired by adding .strip(): the INSTANCE, not the CLASS. And
    # the class is native here -- ledger row 13 records this table FRAGMENTING into orphaned
    # single-row tables. So: the block runs to the first BLANK line, and anything inside it that is
    # not a table row is UNCLASSIFIABLE, which refuses.
    lines = text.splitlines()
    heads = [i for i, l in enumerate(lines)
             if l.strip().startswith("| round | findings | note |")]
    if not heads:
        print("[ledger] CANNOT LOOK :: no ledger header row")
        return 2
    if len(heads) > 1:
        # ⚠ a QUOTED earlier revision of this table, placed above the live one, was read as THE
        # ledger. The TOTAL sentence already refuses on multiplicity for exactly this reason; the
        # header must too, or the hazard is only closed one layer up.
        print(f"[ledger] CANNOT LOOK :: {len(heads)} ledger header rows at lines "
              f"{[i + 1 for i in heads]}; this tree RETRACTS BY QUOTING, so the first is not "
              f"authoritative. Refusing.")
        return 2
    h = heads[0]
    end = next((i for i in range(h + 1, len(lines)) if not lines[i].strip()), len(lines))
    block = [l.strip() for l in lines[h + 1:end]]

    # ⚠ AND NO LEDGER ROW MAY SURVIVE OUTSIDE THE BLOCK.
    # Ending the block at a blank line closed review #9's interloper class -- but a WHITESPACE-ONLY
    # line is blank, so it still truncated the table and orphaned every row beneath it at exit 0.
    # My own mutation suite caught that one. Rather than patch a third boundary rule, refuse
    # whenever a row that LOOKS like a ledger row appears anywhere outside the block: ledger row 13
    # records this table fragmenting into orphaned single-row tables, so orphans are a real event
    # here, not a hypothetical.
    # ⚠ The first version of this check matched only `**`-decorated labels, narrower than the in-block
    # parser: review #11b orphaned `| -- **agy …`, `| _agy …_`, `| [agy …](x)`, `| ***agy …***`,
    # `` | `agy …` `` and `| ***47 (self)*** |` below a whitespace-only line, and each passed at exit 0.
    # Strip ANY decoration from the first cell before testing the label.
    def _orphan(l):
        if not l.strip().startswith("|"):
            return False
        c = _cells(l.strip())
        lab = re.sub(r"^[\s*_`\[\]()~>⚠-]+", "", c[0]) if c else ""
        return bool(re.match(r"(\d+\s*\(self|agy\b)", lab, re.I))
    orphans = [l.strip()[:80] for i, l in enumerate(lines) if not (h < i < end) and _orphan(l)]
    if orphans:
        print("[ledger] CANNOT LOOK :: ledger-shaped row(s) OUTSIDE the ledger block -- the table "
              "has fragmented, or a row was orphaned by a blank/whitespace line. Refusing:")
        for o in orphans:
            print(f"    {o}")
        return 2

    selves, agys, unclassified, noverdict = [], [], [], 0
    for l in block:
        if not l.startswith("|"):
            unclassified.append(f"NOT A TABLE ROW: {l[:70]}")
            continue
        cells = _cells(l)
        if len(cells) >= 2 and all(SEP_CELL.match(c) for c in cells):
            continue                      # a genuine delimiter row: every cell is dashes/colons
        if len(cells) < 2:
            unclassified.append(f"FEWER THAN 2 CELLS: {l[:70]}")
            continue
        label, cell = cells[0], cells[1]
        nums = re.findall(r"-?\d+", cell)
        m = SELF_LABEL.match(label)
        if m:
            if len(nums) == 1 and int(nums[0]) >= 0:
                selves.append((int(m.group(1)), int(nums[0]))); continue
            unclassified.append(l[:90]); continue
        if AGY_LABEL.match(label):
            if len(nums) == 1 and int(nums[0]) >= 0:
                agys.append(int(nums[0])); continue
            if not nums and re.fullmatch(r"[\s*⚠_`()\[\]-]*no verdict[\s*⚠_`()\[\].-]*",
                                         cell, re.I):
                # ⚠ but a non-verdict row whose NOTE reports findings is not a non-verdict: review
                # #11b moved "ended after finding six defects" into the next cell and it passed.
                rest = " ".join(cells[2:])
                if re.search(r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
                             r"thirteen|fourteen|fifteen)\b[^|]{0,40}\b(findings?|defects?)\b", rest, re.I):
                    unclassified.append("NO VERDICT row whose note reports findings: " + l[:60]); continue
                noverdict += 1; continue
            unclassified.append(l[:90]); continue
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
    hits = list(TOTAL.finditer(flat))
    if not hits:
        print("[ledger] CANNOT LOOK :: no TOTAL line matching the expected shape")
        return 2
    if len(hits) > 1:
        print(f"[ledger] CANNOT LOOK :: {len(hits)} TOTAL sentences match; the first is not\n    authoritative. This tree RETRACTS BY QUOTING, so a quoted-but-stale TOTAL is\n    indistinguishable from the live one at this layer. Refusing.")
        for hh in hits:
            print(f"    {hh.group(0)[:110]}")
        return 2
    m = hits[0]

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
    print(f"\n[ledger] PASS :: {len(selves)} self rounds and {len(agys)} independent reviews "
          f"reconcile ({noverdict} recorded non-verdict row(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
