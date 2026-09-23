#!/usr/bin/env python3
"""Mutation suite for probe-20260922-ledger-reconciles.py (the loop-ledger guard).

WHY THIS FILE EXISTS. The guard it tests has been defeated by independent reviewers repeatedly; the count is not
restated here, where it went stale twice, but lives in docs/known-issues/ISSUE-69.

⚠ AND THE FIRST VERSION OF THIS SUITE DID NOT CONVERGE EITHER. Review #10 measured it: the suite
stayed GREEN under three deliberate regressions of the guard, including review #9's own headline
class. Its cases placed the interloper ABOVE the last row and also injected a stale TOTAL, so the
arithmetic mismatch satisfied the assertion under both the repaired and the regressed guard. A
mutation that passes under the regression it was written for tests nothing. Its `_anchor()` also
returned a REGEX PREFIX rather than a whole row, so nine mutations spliced into the middle of the
last ledger row, and its "row deleted" case only rewrote a cell.

So this file now has two layers:
  * MUTATIONS -- each defeating shape must be REFUSED (exit 1 or 2) by the current guard, and each
    case labelled CONTROL must PASS (exit 0). One control is a CORRECT ledger that only an escape-aware
    parser reads right, so it discriminates in the direction a refusal-only case cannot.
  * REGRESSIONS (`--regressions`) -- the guard is deliberately patched back to each historical
    defect, and the suite must FAIL. A suite that cannot fail is not evidence that it passed.

Run: python3 docs/orchestration/probes/probe-20260922-ledger-guard-mutations.py [--regressions]
Exit 0 = every case behaved as wanted, and (with --regressions) the suite FAILED under at least one
patched-back defect -- i.e. it can fail. It does NOT mean every regression is detected: a regression
can be REDUNDANT (a later guard layer also closes its shape), and the harness says which.
⚠ An earlier version of this docstring claimed "every regression detected" and that the harness
"patches the guard back to EACH historical defect"; review #11b showed both false. The regression
list is a set of defects reviewers actually found, not all of them, and it grows when one is missed.
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

# ⚠ the WHOLE sentence: an earlier pattern stopped at the self-round total, so the "hidden in a comment"
# case hid only a prefix and tested something other than its label (review #12b)
TOTAL_RE = re.compile(r"\*\*TOTAL: self rounds 1[–-]\d+ = [0-9+]+ = (\d+);\s*independent reviews =\s*[0-9+]+ = \d+; TOTAL \d+\.\*\*", re.S)

# Each regression rewrites the guard back to a defect a reviewer actually found.
REGRESSIONS = {
    'R1 raw HTML counted as visible text (reviews #11b, #12b, #13b)': ('VISIBLE = ("text", "code_inline")                      # REGRESSION-ANCHOR:visible-types',
        'VISIBLE = ("text", "code_inline", "html_inline", "html_block")'),
    'R2 invisible format characters not removed (review #13b)': ('return "".join(ch for ch in t if unicodedata.category(ch) != "Cf").strip()   # REGRESSION-ANCHOR:cf-strip',
        'return t.strip()'),
    'R3 duplicate ledger table allowed (review #9)': ('if len(ledgers) > 1:                                  # REGRESSION-ANCHOR:header-multiplicity',
        'if False:'),
    'R4 no orphan check (self-round 30, reviews #11b, #12b)': ('if orphans:                                           # REGRESSION-ANCHOR:orphans',
        'if False:'),
    'R5 unclassifiable rows omitted instead of refused (review #8)': ('if unclassified:                                      # REGRESSION-ANCHOR:unclassified',
        'if False:'),
    'R6 the sign of a count stripped, so -13 reads as 13 (review #9)': ('nums = re.findall(r"-?\\d+", cell)',
        'nums = re.findall(r"\\d+", cell)'),
    'R8 TOTAL multiplicity allowed (review #8)': ('if len(hits) > 1:                                     # REGRESSION-ANCHOR:total-multiplicity',
        'if False:'),
    'R9 addends compared by count and sum only (review #7)': ('if len(stated_list) == len(derived_list) and stated_list != derived_list:   # REGRESSION-ANCHOR:elementwise',
        'if False:'),
    'R10 NO VERDICT accepted anywhere in the cell (review #9)': ('re.fullmatch(r"[\\s\\u26a0()\\[\\]-]*no verdict[\\s\\u26a0().-]*", cell, re.I)',
        're.search("no verdict", cell, re.I)'),
    'R11 a NO VERDICT note may report findings (reviews #11b, #12b, #13b)': ('if reports_findings(" ".join(cells[2:])):',
        'if False:'),
    'R12 non-ASCII-whitespace-led lines not refused (review #14b)': ('if odd:                                               # REGRESSION-ANCHOR:unicode-ws',
        'if False:'),
    'R13 TOTALs read from inline text only, not code blocks (review #14b)': ('if t.type in ("inline", "fence", "code_block")]   # REGRESSION-ANCHOR:total-sources',
        'if t.type in ("inline",)]'),
}


def _last_self_row(text):
    """The WHOLE last self row -- not a prefix. A truncated anchor splices mid-row."""
    rows = [l for l in text.splitlines() if re.match(r"^\|\s*\*{0,2}\d+\s*\(self", l)]
    if not rows:
        raise SystemExit("[mutations] CANNOT LOOK :: no self rows in the report")
    return rows[-1]


def _last_table_row(text):
    """The LAST row of the ledger table, whatever kind it is.

    ⚠ Position-sensitive cases (an interloper line, an orphaned row) must be placed after THIS, not
    after the last self row: once agy rows follow the last self row, an interloper inserted there
    truncates REAL rows, and the case then refuses on arithmetic under the fixed guard and the broken
    one alike. Review #11b's regression runs exposed that: the orphan cases tested nothing.
    """
    lines = text.splitlines()
    h = next(i for i, l in enumerate(lines) if l.strip().startswith("| round | findings | note |"))
    j = h + 1
    while j < len(lines) and lines[j].strip():
        j += 1
    return lines[j - 1]


def _ledger_bounds(text):
    """(lines, header index, index one past the table's last row) of the ledger table."""
    L = text.split("\n")
    h = next(i for i, l in enumerate(L) if l.strip().startswith("| round | findings | note |"))
    e = h + 1
    while e < len(L) and L[e].strip():
        e += 1
    return L, h, e


def _first_agy_row(text):
    rows = [l for l in text.splitlines() if re.match(r"^\|\s*\*{0,2}agy", l, re.I)]
    if not rows:
        raise SystemExit("[mutations] CANNOT LOOK :: no agy rows in the report")
    return rows[0]


def build_cases(orig):
    anchor = _last_self_row(orig)
    tail = _last_table_row(orig)
    agy0 = _first_agy_row(orig)
    r46 = next(l for l in orig.splitlines() if re.match(r"^\| 46 \(self\)", l))
    nv_row = next(l for l in orig.splitlines() if re.search(r"NO VERDICT", l) and re.match(r"^\|\s*\*{0,2}agy", l, re.I))
    one_digit_agy = next(l for l in orig.splitlines()
                         if re.match(r"^\|\s*\*{0,2}agy", l, re.I) and re.search(r"\|\s*\*\*\d\*\*\s*\|", l))
    r_last_agy = [l for l in orig.splitlines() if re.match(r"^\|\s*\*{0,2}agy", l, re.I)][-1]
    m = TOTAL_RE.search(orig)
    if not m:
        raise SystemExit("[mutations] CANNOT LOOK :: no TOTAL sentence of the expected shape")
    total_line, stale_total = m.group(0), m.group(0).replace(f"= {m.group(1)};", "= 9999;")
    NEW = "| **agy #99 (independent)** | **6** | an unrecorded review |"

    def after(row, extra):
        return orig.replace(row, row + "\n" + extra, 1)

    cases = [
        # --- review #10's two new shapes
        ("first cell begins '--' (renders as a body row)", after(anchor, "| -- **agy #99 (independent)** | **6** | x |"), (1, 2)),
        ("escaped pipe shifts the cell window", after(anchor, "| **agy #99 (independent)** \\| x | **6** | y |"), (1, 2)),
        ("an all-dash row at the end of the table", after(anchor, "| - | - | - |"), (1, 2)),
        # --- review #9's class, in the DISCRIMINATING placement: unrecorded row BELOW the interloper
        ("unrecorded review BELOW an HTML comment in the table", after(anchor, "<!-- aside -->\n" + NEW), (1, 2)),
        ("unrecorded review BELOW a blockquote in the table", after(tail, "> aside\n" + NEW), (1, 2)),
        ("unrecorded review BELOW a whitespace-only line", after(tail, "   \n" + NEW), (1, 2)),
        # --- a decoy table directly ABOVE the live one: caught by the orphan check, because the live rows fall
        # in the decoy's section. It does NOT reconcile; the reconciling case that R3 alone catches is below
        ("a decoy ledger table above the live one",
         orig.replace("| round | findings | note |",
                      "| round | findings | note |\n|---|---|---|\n| 1 (self) | **14** | decoy |\n\n"
                      "| round | findings | note |", 1), (1, 2)),
        # --- addends permuted: sums agree, order does not. Only an elementwise check sees this.
        ("self addends PERMUTED (sum unchanged)",
         orig.replace("= 3+0+0+1+", "= 0+3+0+1+", 1), (1, 2)),
        # ⚠ this case did not mutate on its first outing: the TOTAL sentence WRAPS as
        # "independent reviews =\n14+9+7+...", so an anchor of "= 14+9+7+" matched nothing and the
        # unchanged document passed, looking like a guard fail-open. Third instance in this file's
        # history of a mutation that does not mutate. Anchor inside the addend run instead, and
        # assert the substitution actually happened (below).
        ("independent addends PERMUTED (sum unchanged)",
         orig.replace("14+9+7+11", "9+14+7+11", 1), (1, 2)),
        # --- sign, multiplicity, stale totals
        ("agy row reads a NEGATIVE count", orig.replace(agy0, agy0.replace("**14**", "**-14**", 1), 1), (1, 2)),
        ("quoted stale TOTAL above a corrupted live one",
         orig.replace(total_line, "> (withdrawn) " + total_line + "\n\n" + stale_total, 1), (1, 2)),
        ("second contradictory TOTAL appended",
         orig + "\n\n**TOTAL: self rounds 1-27 = 1+1 = 2; independent reviews = 1+1 = 2; TOTAL 999.**\n", (1, 2)),
        # --- row-level corruption
        ("a real agy row DELETED outright", orig.replace(agy0 + "\n", "", 1), (1, 2)),
        ("a self row duplicated verbatim", after(anchor, anchor), (1, 2)),
        ("agy cell MENTIONS 'NO VERDICT' beside an integer",
         after(anchor, "| **agy #99 (independent)** | **5** after a NO VERDICT retry | x |"), (1, 2)),
        ("agy cell carries TWO integers", after(anchor, "| **agy #99 (independent)** | 5 of 9 | x |"), (1, 2)),
        ("agy cell has no integer and no NO VERDICT", after(anchor, "| **agy #99 (independent)** | pending | x |"), (1, 2)),
        ("self findings cell unparseable",
         orig.replace(anchor, re.sub(r"(\| \d+ \(self\) \|)[^|]*\|", r"\1 none found |", anchor, count=1), 1), (1, 2)),
        ("new agy row indented two spaces", after(anchor, "  " + NEW), (1, 2)),
        ("new agy row indented with a tab", after(anchor, "\t" + NEW), (1, 2)),
        ("TOTAL left stale after a real new review row", after(anchor, NEW), (1, 2)),
        # --- review #11b: orphan shapes the first orphan check was too narrow to see
        *[(f"orphan below a whitespace line: {lab[:26]}", orig.replace(tail, tail + "\n   \n" + lab, 1), (1, 2))
          for lab in ("| -- **agy #99 (independent)** | **6** | x |", "| \u26a0 **agy #99 (independent)** | **6** | x |",
                      "| _agy #99_ | **6** | x |", "| [agy #99](x.md) | **6** | x |",
                      "| ***agy #99*** | **6** | x |", "| `agy #99` | **6** | x |", "| ***99 (self)*** | **3** | x |")],
        # restored: dropped when the suite was rebuilt at review #10b, which left the NO VERDICT sink
        # with no discriminating case at all (review #11b's R9 came back "redundant")
        ("a real review hidden inside a NO VERDICT findings cell",
         after(anchor, "| **agy #99 (independent)** | \u26a0 **NO VERDICT** \u2014 ended after finding six defects | x |"), (1, 2)),
        ("NO VERDICT row whose NOTE reports findings",
         after(anchor, "| **agy #99 (independent)** | NO VERDICT | ended after finding six defects |"), (1, 2)),
        ("reconciling TOTAL hidden in an HTML comment, visible one stale",
         orig.replace(total_line, "<!-- " + total_line + " -->\n\n" + stale_total, 1), (1, 2)),
        # --- DISCRIMINATING in the other direction: a CORRECT ledger that a naive cell split misreads.
        # Review #11b showed the "escaped pipe" case above refuses under both the fixed and the broken
        # split, so it tested nothing; this one PASSES only if escaped pipes are honoured.
        ("CONTROL correct ledger with an escaped pipe in a label",
         orig.replace(agy0, agy0.replace("(independent)**", "(independent)** \\| retry 9", 1), 1), (0,)),
        # --- review #12b: the guard's sixth defeat, and two false refusals
        # a CONTROL, deliberately: with the markers inside code spans nothing is hidden, so a correct
        # ledger must PASS; the guard's old comment-stripping swallowed the row between them (R13)
        ("CONTROL comment markers inside code spans hide nothing",
         orig.replace(r46, r46[:-1] + " `<!--` |", 1).replace(r_last_agy, r_last_agy[:-1] + " `-->` |", 1), (0,)),
        ("an HTML entity that renders as a different count",
         orig.replace(agy0, re.sub(r"\*\*(\d+)\*\*", lambda mm: "**&#" + str(48 + int(mm.group(1)) % 10) + ";**", agy0, count=1), 1), (1, 2)),
        ("reconciling TOTAL hidden in a link reference definition, visible one stale",
         orig.replace(total_line, "[//]: # (" + total_line.replace("**", "") + ")\n\n" + stale_total, 1), (1, 2)),
        *[(f"orphan below a whitespace line: {lab[:22]}", orig.replace(tail, tail + "\n   \n" + lab, 1), (1, 2))
          for lab in ("| <b>agy #99</b> | **6** | x |", "| **99** (self) | **3** | x |",
                      "| #99 (self) | **3** | x |", "| review agy #99 | **6** | x |")],
        *[(f"NO VERDICT row whose note says: {note}", after(tail, f"| **agy #99 (independent)** | NO VERDICT | {note} |"), (1, 2))
          for note in ("died after reporting sixteen defects", "found 6 problems", "defects found: six")],
        ("CONTROL a heading directly after the table", orig.replace(tail, tail + "\n## An aside", 1), (0,)),
        ("CONTROL a blockquote directly after the table", orig.replace(tail, tail + "\n> an aside", 1), (0,)),
        # CONTROLS that discriminate the "read what a reader sees" layers: a CORRECT ledger carrying
        # something a reader cannot see must PASS. Refusal-only cases could not tell these layers
        # from the TOTAL-multiplicity check, so R11/R14/R15 reported "redundant" (review #12b).
        ("CONTROL a stale TOTAL hidden in an HTML comment is ignored",
         orig.replace(total_line, total_line + "\n\n<!-- " + stale_total + " -->", 1), (0,)),
        # ⚠ a reference definition must stand ALONE: an earlier version of this case left the rest of the
        # paragraph on the same line, so it was not a definition at all but VISIBLE text -- and the old
        # regex guard "passed" it by deleting text a reader could see (found by the parser rewrite)
        ("CONTROL a stale TOTAL hidden in a link reference definition is ignored",
         orig.replace(total_line, total_line + "\n\n[//]: # (" + stale_total.replace("**", "") + ")\n\n", 1), (0,)),
        ("CONTROL a single-digit count written as an HTML entity reads as that digit",
         orig.replace(one_digit_agy, re.sub(r"\*\*(\d)\*\*", lambda mm: "**&#" + str(48 + int(mm.group(1))) + ";**", one_digit_agy, count=1), 1), (0,)),
        # --- review #13b: the guard's seventh defeat, and two false refusals
        ("an entity-encoded pipe in a label hides a changed count",
         orig.replace(r_last_agy, re.sub(r"\|\s*\*\*(\d+)\*\*\s*\|", lambda mm: "&#124; **" + mm.group(1) + "** | **" + str(int(mm.group(1)) + 1) + "** |", r_last_agy, count=1), 1), (1, 2)),
        ("a final row starting with an HTML tag and no pipe", orig.replace(tail, tail + "\n<b>agy #99 (independent)</b> | **9** | x", 1), (1, 2)),
        ("a final row starting '#99 (self)' with no pipe", orig.replace(tail, tail + "\n#99 (self) | **2** | x", 1), (1, 2)),
        *[(f"visible TOTAL made unreadable, reconciling one hidden in {where}",
           after(tail, "| **agy #99 (independent)** | **9** | x |").replace(total_line, total_line.replace("1\u2013", "1\u2013\u2060", 1) + hide, 1), (1, 2))
          for where, hide in (("a multi-line link reference", "\n\n[//]: # (hidden\nTOTAL 999)\n\n"),
                              ("a title attribute", '\n\n<a title="TOTAL 999"></a>\n\n'))],
        *[(f"NO VERDICT row whose note says: {note}", after(tail, f"| **agy #99 (independent)** | NO VERDICT | {note} |"), (1, 2))
          for note in ("died after flagging 5 bugs", "a dozen flaws reported before the rate limit")],
        ("CONTROL a visible TOTAL carrying an invisible U+2060 still reads", orig.replace(total_line, total_line.replace("1\u2013", "1\u2013\u2060", 1), 1), (0,)),
        ("CONTROL a bullet list directly after the table", orig.replace(tail, tail + "\n- an aside", 1), (0,)),
        ("CONTROL an ordered list directly after the table", orig.replace(tail, tail + "\n1. an aside", 1), (0,)),
        ("CONTROL a reviewer-keyed table in another section", orig + "\n\n## Appendix\n\n| reviewer | scope |\n|---|---|\n| agy #12b | instruments |\n", (0,)),
        # R1's discriminating control: INLINE html. A comment on its own line is a block token that never
        # reaches the inline text, so only a mid-paragraph comment can show raw HTML leaking into the
        # visible text (review #13b showed "redundant" is not to be taken on trust)
        ("CONTROL a stale TOTAL inside an INLINE html comment is ignored",
         orig.replace(total_line, total_line + " <!-- " + stale_total.replace("**", "") + " -->", 1), (0,)),
        # indentation AFTER the table's true last row parses as a code block, not a row -- tested in both
        # positions on purpose: this suite first caught the gap only because a self row happened to
        # become the table's last row
        ("new agy row tab-indented after the table's last row", after(tail, "\t" + NEW), (1, 2)),
        ("new agy row indented four spaces after the table's last row", after(tail, "    " + NEW), (1, 2)),
        # --- review #14b
        # R3's discriminating case: a RECONCILING snapshot of the ledger in an earlier section, while the live
        # ledger gains an unrecorded row. Only table multiplicity can refuse this; the orphan check cannot,
        # because the snapshot's section ends before the live table begins.
        ("a reconciling snapshot of the ledger in an earlier section, live ledger stale",
         (lambda L, h, e: "\n".join(L[:e] + ["| **agy #99 (independent)** | **6** | unrecorded |"] + L[e:]).replace(
             "## 1. ", "## 0. A quoted earlier revision\n\n" + "\n".join(L[h:e]) + "\n\n## 1. ", 1))(*_ledger_bounds(orig)), (1, 2)),
        ("new agy row tab-indented in the MIDDLE of the table", after(agy0, "\t" + NEW), (1, 2)),
        ("new agy row indented four spaces in the MIDDLE of the table", after(agy0, "    " + NEW), (1, 2)),
        ("a real row led by a non-breaking space", orig.replace(agy0, "\u00a0" + agy0, 1), (1, 2)),
        ("a line of only a non-breaking space inside the table, then an unrecorded row",
         after(agy0, "\u00a0\n| **agy #99 (independent)** | **6** | x |"), (1, 2)),
        ("a stale TOTAL in a fenced code block", orig.replace(total_line, total_line + "\n\n```\n" + stale_total.replace("**", "") + "\n```\n\n", 1), (1, 2)),
        ("a stale TOTAL in an indented code block", orig.replace(total_line, total_line + "\n\n    " + stale_total.replace("**", "").replace("\n", " ") + "\n\n", 1), (1, 2)),
        *[(f"CONTROL a NO VERDICT note that reports no findings: {note[:30]}",
           orig.replace(nv_row, re.sub(r"\|[^|]*\|\s*$", "| " + note + " |", nv_row), 1), (0,))
          for note in ("died on a session rate-limit error 2 minutes into its first action",
                       "produced no findings; attempt 2 is the real review",
                       "rate-limited before one file was read; no defects reported")],
        ("CONTROL untouched ledger", orig, (0,)),
    ]
    # ⚠ A MUTATION THAT DOES NOT MUTATE TESTS NOTHING, and this suite has shipped three of them.
    # Assert the text actually changed before trusting any verdict derived from it.
    inert = [label for label, text, want in cases
             if text == orig and not label.startswith("CONTROL")]
    if inert:
        raise SystemExit("[mutations] CANNOT LOOK :: these cases did not change the document, so "
                         "their result is meaningless: " + "; ".join(inert))
    return cases


def run_suite(guard_src, cases, verbose):
    """Returns the list of cases that behaved WRONGLY under this guard source."""
    wrong = []
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        (work / "probes").mkdir()
        g = work / "probes" / GUARD.name
        g.write_text(guard_src, encoding="utf-8")
        target = work / REPORT.name
        for label, text, want in cases:
            target.write_text(text, encoding="utf-8")
            rc = subprocess.run([sys.executable, str(g)], capture_output=True, text=True).returncode
            ok = rc in want
            if verbose:
                print(f"  {'OK ' if ok else '*** WRONG ***'} {label:58s} exit={rc} want={want}")
            if not ok:
                wrong.append((label, rc, want))
    return wrong


def main() -> int:
    if not GUARD.exists() or not REPORT.exists():
        print("[mutations] CANNOT LOOK :: guard or report missing")
        return 2
    orig = REPORT.read_text(encoding="utf-8")
    src = GUARD.read_text(encoding="utf-8")
    cases = build_cases(orig)

    wrong = run_suite(src, cases, verbose=True)
    print()
    if wrong:
        print(f"[mutations] FAIL :: {len(wrong)} of {len(cases)} case(s) behaved wrongly")
        for label, rc, want in wrong:
            print(f"    {label}: exit {rc}, wanted one of {want}")
        return 1
    print(f"[mutations] PASS :: {len(cases)} cases, every defeating shape refused, control clean")

    if "--regressions" in sys.argv:
        # ⚠ WHAT THIS HARNESS DOES AND DOES NOT ASSERT.
        # It patches the guard back to each historical defect and re-runs the suite. A regression
        # that makes some case fail open is LOAD-BEARING: that line is the only thing closing its
        # shape. A regression under which every case still refuses is REDUNDANT: the shape is
        # closed by a later layer too (the orphan-row check covers several). Redundancy is defence
        # in depth, not a suite defect -- the earlier version of this harness called it FAIL, which
        # would have pushed me to weaken the guard to make a test go green.
        # The real assertion is the weaker, honest one: THE SUITE MUST BE ABLE TO FAIL AT ALL.
        # A suite that passes under every possible breakage is not evidence that it passed.
        print("\n--- REGRESSION HARNESS: which guard lines are load-bearing? ---")
        load_bearing, redundant, skipped = [], [], []
        for label, (new_, old_) in REGRESSIONS.items():
            if new_ not in src:
                print(f"  ?? {label:58s} SKIPPED -- anchor absent, the guard moved")
                skipped.append(label)
                continue
            w = run_suite(src.replace(new_, old_, 1), cases, verbose=False)
            fired = w          # a CONTROL that fails under a regression also proves the suite can fail
            kind = "LOAD-BEARING" if fired else "redundant   "
            (load_bearing if fired else redundant).append(label)
            print(f"  {kind} {label:58s} {len(fired)} case(s) fire")
        print()
        if skipped:
            print(f"[regressions] FAIL :: {len(skipped)} regression anchor(s) no longer exist in "
                  f"the guard, so this harness is silently not testing them:")
            for u in skipped:
                print(f"    {u}")
            return 1
        if not load_bearing:
            print("[regressions] FAIL :: the suite stayed green under EVERY regression, so it "
                  "cannot fail and its PASS above is not evidence.")
            return 1
        print(f"[regressions] PASS :: the suite can fail ({len(load_bearing)} load-bearing, "
              f"{len(redundant)} redundant -- redundant means a later layer also closes that shape)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
