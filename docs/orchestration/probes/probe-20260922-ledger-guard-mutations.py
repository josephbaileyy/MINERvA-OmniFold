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
Exit 0 = every case behaved as wanted, and (with --regressions) every refusal site found in the guard's
code is anchored, every anchor has a regression, and every regression changes some case's result without
crashing (only preconditions may fire through a traceback). See the harness comment in `main`.
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
    'R13 TOTALs read from inline text only, not code blocks (review #14b)': ('for t in toks if t.type in ("inline", "fence", "code_block", "html_block")]   # REGRESSION-ANCHOR:total-sources',
        'for t in toks if t.type in ("inline", "html_block")]'),
    # --- review #15b: checks the guard HAD, that no case pinned -- each could be deleted with the suite green
    'R14 a self cell with several numbers read by its first (review #15b)': ('if len(nums) == 1 and int(nums[0]) >= 0:     # REGRESSION-ANCHOR:self-count',
        'if nums:'),
    'R15 an agy cell with several numbers read by its first (review #15b)': ('if len(nums) == 1 and int(nums[0]) >= 0:     # REGRESSION-ANCHOR:agy-count',
        'if nums:'),
    'R16 self rounds not required to run 1..N (review #15b)': ('if rounds != list(range(1, len(rounds) + 1)):      # REGRESSION-ANCHOR:round-order',
        'if False:'),
    'R17 the self subtotal not compared (review #15b)': ('("self total", int(stated_self), self_sum),                    # REGRESSION-ANCHOR:self-total',
        ''),
    'R18 the independent subtotal not compared (review #15b)': ('("independent total", int(stated_agy), agy_sum),               # REGRESSION-ANCHOR:agy-total',
        ''),
    'R19 the grand TOTAL not compared (review #15b)': ('("grand total", int(stated_total), self_sum + agy_sum),        # REGRESSION-ANCHOR:grand-total',
        ''),
    'R20 only U+00A0 counted as non-ASCII whitespace (review #15b)': ('if non_ascii_ws_led(l)]                    # REGRESSION-ANCHOR:ws-classes',
        'if l[:1] == "\\u00a0"]'),
    'R21 TOTALs in raw-HTML blocks not read (review #15b)': ('for t in toks if t.type in ("inline", "fence", "code_block", "html_block")]   # REGRESSION-ANCHOR:total-sources',
        'for t in toks if t.type in ("inline", "fence", "code_block")]'),
    'R22 a NO VERDICT note never read as reporting (review #15b)': ('return any(p.search(note) for p in REPORTS)           # REGRESSION-ANCHOR:noverdict-notes',
        'return False'),
    # --- review #16a: three `checks` entries and two generic branches had no anchor, so the anchor sweep
    # could not see them and deleting any one left every case green
    'R23 the stated last self round not compared (review #16a)': ('checks = [("last self round", int(stated_last), rounds[-1]),   # REGRESSION-ANCHOR:last-round',
        'checks = ['),
    'R24 the self addend count not compared (review #16a)': ('("self addend count", len(_ints(self_addends)), len(selves)),   # REGRESSION-ANCHOR:self-addend-count',
        ''),
    'R25 the independent addend count not compared (review #16a)': ('("independent addend count", len(_ints(agy_addends)), len(agys))]   # REGRESSION-ANCHOR:agy-addend-count',
        ']'),
    'R26 a stated/derived mismatch not recorded (review #16a)': ('if stated != derived:                                # REGRESSION-ANCHOR:scalar-compare',
        'if False:'),
    'R27 recorded mismatches not acted on (review #16a)': ('if bad:                                                  # REGRESSION-ANCHOR:any-bad',
        'if False:'),
    'R28 "found N" read as a report whatever noun follows (review #16b)': ('rf"|\\s+(?:before|after|and|then|but|while|when|of|in|so)\\b")      # REGRESSION-ANCHOR:found-tail',
        'rf"|\\s+\\w")'),
    # PRECONDITIONS: without one, the guard CRASHES instead of refusing cleanly. Their regressions may fire
    # through a traceback only -- the one class allowed to (anchor names beginning `pre-`)
    'P1 a missing report not refused cleanly (review #16a)': ('if not REPORT.exists():                                  # REGRESSION-ANCHOR:pre-report',
        'if False:'),
    'P2 a report without a ledger table not refused cleanly (review #16a)': ('if not ledgers:                                          # REGRESSION-ANCHOR:pre-ledger',
        'if False:'),
    'P3 a ledger with no self rows not refused cleanly (review #16a)': ('if not selves or not agys:                               # REGRESSION-ANCHOR:pre-rows',
        'if False:'),
    'P4 a report with no TOTAL not refused cleanly (review #16a)': ('if not hits:                                             # REGRESSION-ANCHOR:pre-total',
        'if False:'),
}
# review #15b: dropping ONE finding-report pattern left the suite green. Each pattern, keyed by the
# example in its trailing comment, gets its own regression and its own case (NV_REPORTING below).
REPORT_TAGS = ['"six defects", "a dozen flaws"', '"found 6"', '"defects found: six"', '"found a defect"',
               '"two issues found"', '"findings: 3"', '"2 MEDIUM" (case-sensitive)']
# a REGRESSION-ANCHOR with no regression is a check nothing tests; `--regressions` refuses one
ANCHOR_RE = re.compile(r"REGRESSION-ANCHOR:([\w-]+)")


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


# one note per REPORTS pattern, each matched by THAT pattern alone, so dropping any one pattern fails a case
NV_REPORTING = ("six defects in the guard", "found 6 before the session died", "defects found: six",
                "found a defect in the guard", "two issues found", "findings: 3", "2 MEDIUM, 1 LOW")


def unanchored_sites(src):
    """Refusal sites of the guard, found in its CODE, whose governing condition carries no anchor."""
    lines, out = src.split("\n"), []
    ind = lambda s: len(s) - len(s.lstrip())
    for i, l in enumerate(lines):
        s = l.strip()
        if s in ("return 1", "return 2") or s.startswith("bad.append("):
            need = ind(l)
            for j in range(i - 1, -1, -1):
                lj = lines[j]
                if not lj.strip() or ind(lj) >= need:
                    continue
                need = ind(lj)
                if re.match(r"\s*(if|elif)\b", lj):
                    if "REGRESSION-ANCHOR:" not in lj:
                        out.append((j + 1, lj.strip()))
                    break
                if re.match(r"\s*def\b", lj):
                    out.append((i + 1, s + " (no governing if)"))
                    break
    k = next((i for i, l in enumerate(lines) if l.strip().startswith("checks = [")), None)
    if k is None:
        out.append((0, "no `checks = [` list found"))
    else:
        for i in range(k, len(lines)):
            if "REGRESSION-ANCHOR:" not in lines[i]:
                out.append((i + 1, lines[i].strip()))
            if lines[i].rstrip().split("#")[0].rstrip().endswith("]"):
                break
    return out


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
        # --- review #15b: a hand-edited count, one number at a time. Each is caught by exactly one check
        ("only the grand TOTAL stale", re.sub(r"(; TOTAL )(\d+)", lambda mm: mm.group(1) + str(int(mm.group(2)) - 1), orig, count=1), (1, 2)),
        ("only the independent subtotal stale", re.sub(r"= (\d+)(; TOTAL )", lambda mm: f"= {int(mm.group(1)) - 1}" + mm.group(2), orig, count=1), (1, 2)),
        ("only the self subtotal stale", orig.replace(total_line, re.sub(r"= (\d+);", lambda mm: f"= {int(mm.group(1)) - 1};", total_line, count=1), 1), (1, 2)),
        ("a self round's label mistyped (5 -> 50)", orig.replace("\n| 5 (self) |", "\n| 50 (self) |", 1), (1, 2)),
        ("an agy cell reading '14 of 20'", orig.replace(agy0, agy0.replace("**14**", "**14 of 20**", 1), 1), (1, 2)),
        ("a self cell reading '3 of 5'", orig.replace("\n| 1 (self) | **3** |", "\n| 1 (self) | **3 of 5** |", 1), (1, 2)),
        *[(f"a real row led by {name}", orig.replace(agy0, lead + agy0, 1), (1, 2))
          for name, lead in (("a form feed", "\x0c"), ("U+0085", "\x85"), ("U+2028", "\u2028"), ("U+3000", "\u3000"),
                             ("U+2003", "\u2003"), ("one ASCII space then U+00A0", " \u00a0"))],
        *[(f"a NO VERDICT note reporting findings: {note}",
           orig.replace(nv_row, re.sub(r"\|[^|]*\|\s*$", "| " + note + " |", nv_row), 1), (1, 2))
          for note in NV_REPORTING],
        ("CONTROL a NO VERDICT note reporting ZERO findings",
         orig.replace(nv_row, re.sub(r"\|[^|]*\|\s*$", "| 0 findings reported because it never started |", nv_row), 1), (0,)),
        ("a stale TOTAL in a <pre> block", orig.replace(total_line, total_line + "\n\n<pre>\n" + stale_total.replace("**", "") + "\n</pre>\n\n", 1), (1, 2)),
        ("a stale TOTAL in <details> with no blank lines",
         orig.replace(total_line, total_line + "\n\n<details><summary>an earlier revision</summary>\n" + stale_total.replace("**", "") + "\n</details>\n\n", 1), (1, 2)),
        ("CONTROL a stale TOTAL inside an HTML comment BLOCK is ignored",
         orig.replace(total_line, total_line + "\n\n<!--\n" + stale_total.replace("**", "") + "\n-->\n\n", 1), (0,)),
        # --- review #16a: each isolates a check the anchor sweep could not see
        ("the TOTAL's last self round one short", re.sub(r"(self rounds 1[–-])(\d+)", lambda mm: mm.group(1) + str(int(mm.group(2)) - 1), orig, count=1), (1, 2)),
        ("two self addends merged (count short, sum unchanged)", orig.replace("= 3+0+0+1+", "= 3+0+1+", 1), (1, 2)),
        ("two independent addends merged (count short, sum unchanged)", orig.replace("14+9+7+11", "23+7+11", 1), (1, 2)),
        ("the report is absent", None, (2,)),
        ("the ledger table's header renamed away", orig.replace("| round | findings | note |", "| round | count | note |", 1), (2,)),
        # ⚠ every row the guard would read as a self row, including `**10 (self)**`: the first version of this case
        # matched only a bare label, left row 10 behind, and so never reached the precondition it names
        ("every self row removed", "\n".join(l for l in orig.split("\n") if not re.match(r"^\|\s*\W*\d+\s*\(self", l)), (1, 2)),
        ("the TOTAL sentence removed", orig.replace(total_line, "", 1), (2,)),
        *[(f"CONTROL a NO VERDICT death note naming a count of something else: {note[:34]}",
           orig.replace(nv_row, re.sub(r"\|[^|]*\|\s*$", "| " + note + " |", nv_row), 1), (0,))
          for note in ("found one file unreadable and stopped", "reported 3 minutes in that the session was rate-limited",
                       "flagged 1 file as unreadable, then died")],
        # --- review #16b: ORDINARY staleness that only the addend counts catch -- a zero-finding row added,
        # the TOTAL left alone, so every sum still agrees
        ("an unrecorded agy row with 0 findings", after(r_last_agy, "| **agy #99 (independent)** | **0** | clean |"), (1, 2)),
        ("an unrecorded self round with 0 findings", after(anchor, "| 99 (self) | **0** | clean |"), (1, 2)),
        ("CONTROL untouched ledger", orig, (0,)),
    ]
    # ⚠ A MUTATION THAT DOES NOT MUTATE TESTS NOTHING, and this suite has shipped three of them.
    # Assert the text actually changed before trusting any verdict derived from it.
    inert = [label for label, text, want in cases
             if text == orig and not label.startswith("CONTROL")]
    absent_base = [label for label, text, want in cases if text is not None and "(self)" not in text]
    if [x for x in absent_base if x != "every self row removed"]:
        raise SystemExit("[mutations] CANNOT LOOK :: a case lost every self row by accident: " + "; ".join(absent_base))
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
            if text is None:                  # the report is ABSENT
                target.unlink(missing_ok=True)
            else:
                target.write_text(text, encoding="utf-8")
            r = subprocess.run([sys.executable, str(g)], capture_output=True, text=True)
            rc = r.returncode
            # a CRASH is not a refusal: exit 1 from a traceback satisfies every (1, 2) case by accident
            crashed = "Traceback" in r.stderr
            ok = rc in want and not crashed
            if verbose:
                print(f"  {'OK ' if ok else '*** WRONG ***'} {label:58s} exit={rc} want={want}")
            if not ok:
                wrong.append((label, rc, want, crashed))
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
        for label, rc, want, crashed in wrong:
            print(f"    {label}: exit {rc}{' (TRACEBACK)' if crashed else ''}, wanted one of {want}")
        return 1
    print(f"[mutations] PASS :: {len(cases)} cases, every defeating shape refused, control clean")

    if "--regressions" in sys.argv:
        # ⚠ WHAT THIS HARNESS ASSERTS. It patches the guard one line at a time and re-runs the suite.
        #  * Every refusal site in the guard's CODE must carry an anchor (`unanchored_sites`), and every
        #    anchor must have a regression. The anchors alone were a list, and missed three checks (#16a).
        #  * Every regression must be LOAD-BEARING: it changes some case's result without crashing,
        #    either OPEN (a refusal case now passes) or CLOSED (a CONTROL now refuses). Only a
        #    precondition (`pre-` anchor) may fire through a traceback alone.
        #  * A REDUNDANT regression FAILS the harness, where it once did not. Every check but a
        #    precondition is now pinned by a case that fails when that check alone is deleted.
        #    (An earlier version accepted redundancy as defence in depth; review #15b showed that let
        #    five checks go unpinned.)
        print("\n--- REGRESSION HARNESS: which guard lines are load-bearing? ---")
        load_bearing, redundant, skipped = [], [], []
        regs = dict(REGRESSIONS)
        for tag in REPORT_TAGS:
            line = next((l for l in src.splitlines() if l.rstrip().endswith("# " + tag)), None)
            if line is None:
                skipped.append(f"REPORTS pattern {tag}"); continue
            pat = line.strip()
            if pat.startswith("REPORTS = ["):
                pat = pat[len("REPORTS = ["):]
            pat = re.split(r"\s+#\s", pat, maxsplit=1)[0].strip()
            regs[f"R-REPORTS {tag} pattern dropped (review #15b)"] = (pat, 're.compile(r"(?!x)x"),' if pat.endswith(",") else 're.compile(r"(?!x)x")]')
        untested = sorted(set(ANCHOR_RE.findall(src)) - {a for new_, _ in regs.values() for a in ANCHOR_RE.findall(new_)})
        # ⚠ review #16a: the anchors are a LIST, and three checks were not on it. So the refusal sites are
        # ENUMERATED FROM THE CODE: every `return 1`, `return 2` and `bad.append(` is governed by the nearest
        # enclosing `if`/`elif`, which must carry an anchor, and so must every entry of the `checks` list
        for site in unanchored_sites(src):
            skipped.append(f"line {site[0]}: `{site[1][:60]}` governs a refusal and carries no REGRESSION-ANCHOR")
        for a in untested:
            skipped.append(f"REGRESSION-ANCHOR:{a} has no regression, so nothing tests that check")
        for label, (new_, old_) in regs.items():
            # ⚠ a regression that does not COMPILE makes the guard crash, and a crash exits nonzero, which every
            # refusal case accepts: it "fires" through the controls and looks load-bearing. The first per-pattern
            # regressions did exactly that (a comment kept in the pattern closed the list early)
            if new_ in src:
                try:
                    compile(src.replace(new_, old_, 1), GUARD.name, "exec")
                except SyntaxError as e:
                    print(f"  ?? {label:58s} SKIPPED -- the patched guard does not compile ({e.msg})")
                    skipped.append(label)
                    continue
            if new_ not in src:
                print(f"  ?? {label:58s} SKIPPED -- anchor absent, the guard moved")
                skipped.append(label)
                continue
            w = run_suite(src.replace(new_, old_, 1), cases, verbose=False)
            # ⚠ review #16a: a regression that only makes the guard CRASH still "fired", so a broken patch
            # looked load-bearing. Only a precondition (`pre-` anchor) may fire through tracebacks alone;
            # every other regression must make some case FAIL OPEN -- a clean wrong exit, no traceback
            pre = any(a.startswith("pre-") for a in ANCHOR_RE.findall(new_))
            fired = w if pre else [x for x in w if not x[3]]
            kind = "LOAD-BEARING" if fired else ("CRASH-ONLY  " if w else "redundant   ")
            (load_bearing if fired else redundant).append(label)
            # ⚠ review #16b: "load-bearing" meant "some result changes", not "some case fails OPEN" as this
            # comment once said. Both directions are printed: OPEN = a refusal case now passes; CLOSED = a
            # CONTROL now refuses. A line pinned only by CLOSED guards against over-strictness, not staleness
            opened = sum(1 for x in fired if 0 not in x[2] and x[1] == 0)
            closed = sum(1 for x in fired if x[2] == (0,))
            print(f"  {kind} {label:58s} {len(fired)} case(s) fire (open {opened}, closed {closed})"
                  + (f", {len(w) - len(fired)} only by crashing" if len(w) > len(fired) else ""))
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
        # ⚠ review #15b: "12 of 12 load-bearing" was true while five checks had no regression at all. Every
        # check now has one (the anchor sweep above), and a REDUNDANT one is a check no case pins: the suite
        # would stay green if it were deleted. That is now a failure, not a remark.
        if redundant:
            print(f"[regressions] FAIL :: {len(redundant)} regression(s) are redundant -- deleting that check "
                  "leaves every case green, so no case pins it:")
            for u in redundant:
                print(f"    {u}")
            return 1
        print(f"[regressions] PASS :: all {len(load_bearing)} regressions are load-bearing, and every "
              "REGRESSION-ANCHOR in the guard has one")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
