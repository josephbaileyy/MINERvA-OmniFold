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

HOW IT READS THE LEDGER -- AND WHY IT STOPPED USING REGULAR EXPRESSIONS TO DO IT. Independent
reviewers defeated this guard SEVEN times (the history is in docs/known-issues/ISSUE-69). Every one
of those defeats had one cause: the guard used regexes to IMITATE how GitHub renders Markdown, and
each imitation left the next gap -- `**`-less cells, indentation, escaped pipes, HTML comments inside
code spans, HTML entities, link-reference definitions, title attributes, block boundaries. So it no
longer imitates. It PARSES the report with a CommonMark + GFM-table parser (markdown-it-py) and
reads what that parser renders as visible text: `text` and `code_inline` content and code blocks, never
raw HTML. Lines in the ledger's section that begin with non-ASCII whitespace are refused, because GitHub
and markdown-it disagree about them.
Cells are split by the parser, so an entity-encoded pipe stays inside its cell, as it does on
GitHub; comments, attributes and link-reference definitions never reach the visible text at all.

THREAT MODEL, STATED SO NOBODY OVERCLAIMS IT. This defends against ACCIDENTAL staleness: a ledger
row added without updating the TOTAL, a row lost when the table fragments, a hand-edited count. It is
not a proof that no deliberately constructed input can fool it -- markdown-it and GitHub's renderer
themselves differ on edge cases (a non-breaking-space line is one). The rendered ledger on GitHub is
the authority; this is a check against it.

Exit 0 = the stated totals equal the ledger's own column sums. Exit 1 = they do not, naming both.
Exit 2 = the ledger could not be read, which is a failure, not a pass.
"""
import re
import sys
import unicodedata
from pathlib import Path

try:
    from markdown_it import MarkdownIt
except ImportError:
    print("[ledger] CANNOT LOOK :: markdown-it-py is not installed")
    sys.exit(2)

REPORT = Path(__file__).resolve().parents[1] / "REPORT-20260922-review-residue.md"
MD = MarkdownIt("commonmark").enable(["table"])
VISIBLE = ("text", "code_inline")                      # REGRESSION-ANCHOR:visible-types
TOTAL = re.compile(r"self rounds 1[\u2013-](\d+)\s*=\s*([0-9+\s]+?)\s*=\s*(\d+);\s*"
                   r"independent reviews\s*=\s*([0-9+\s]+?)\s*=\s*(\d+);\s*TOTAL\s*(\d+)", re.S)
NUM = (r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|"
       r"sixteen|seventeen|eighteen|nineteen|twenty|dozen|score)")
WORD = r"(findings?|defects?|problems?|bugs?|flaws?|faults?|mistakes?)"
# ⚠ a count must MODIFY a finding-word. The first versions paired any number with any finding-word in a
# window, so a correct note -- "a rate-limit error 2 minutes in", "no defects reported" -- was refused
# (review #14b). `errors?` and `issues?` are gone: they are how a review's death is described.
REPORTS = [re.compile(rf"\b{NUM}\s+(?:\w+\s+){{0,2}}{WORD}\b", re.I),               # "six defects", "a dozen flaws"
           re.compile(rf"\b(found|reported|flagged|flagging|reporting|finding)\s+{NUM}\b", re.I),   # "found 6"
           re.compile(rf"\b{WORD}\s+(found|reported)\s*:?\s*{NUM}\b", re.I)]              # "defects found: six"


def visible(inline):
    """What a reader sees of one inline token: parsed text and code, never raw HTML."""
    out = []
    for c in inline.children or []:
        if c.type in VISIBLE:
            out.append(c.content)
        elif c.type in ("softbreak", "hardbreak"):
            out.append(" ")
    t = "".join(out)
    # format characters (U+2060 and friends) are invisible: a reader sees the digits either side joined
    return "".join(ch for ch in t if unicodedata.category(ch) != "Cf").strip()   # REGRESSION-ANCHOR:cf-strip


def reports_findings(note):
    """True if the note asserts a count OF findings -- not merely a number near a finding-word."""
    return any(p.search(note) for p in REPORTS)           # REGRESSION-ANCHOR:noverdict-notes


def main() -> int:
    if not REPORT.exists():
        print(f"[ledger] CANNOT LOOK :: no report at {REPORT}")
        return 2
    text = REPORT.read_text(encoding="utf-8")
    toks = MD.parse(text)

    # every table, as (header cells, [(row cells, source line)])
    tables, i = [], 0
    while i < len(toks):
        if toks[i].type == "table_open":
            header, rows, cur, line = None, [], None, None
            while toks[i].type != "table_close":
                t = toks[i]
                if t.type == "tr_open":
                    cur, line = [], (t.map[0] + 1 if t.map else None)
                elif t.type == "inline" and cur is not None:
                    cur.append(visible(t))
                elif t.type == "tr_close":
                    if header is None:
                        header = cur
                    else:
                        rows.append((cur, line))
                    cur = None
                i += 1
            tables.append((header or [], rows, i))
        i += 1
    ledgers = [t for t in tables if [c.lower() for c in t[0][:3]] == ["round", "findings", "note"]]
    if not ledgers:
        print("[ledger] CANNOT LOOK :: no rendered table with the ledger header")
        return 2
    if len(ledgers) > 1:                                  # REGRESSION-ANCHOR:header-multiplicity
        print(f"[ledger] CANNOT LOOK :: {len(ledgers)} rendered ledger tables; a quoted earlier revision "
              "is indistinguishable from the live one. Refusing.")
        return 2
    header, rows, end_tok = ledgers[0]

    # ⚠ a line in the ledger's section that BEGINS with Unicode whitespace (U+00A0, U+3000, form feed...)
    # is read one way by markdown-it and another by GitHub: a row led by U+00A0 renders on GitHub with an
    # empty first cell and every cell shifted right, and a line of only U+00A0 continues the table on
    # GitHub where markdown-it ends it (review #14b). This guard cannot know which, so it refuses.
    heads = [t.map[0] for t in toks if t.type == "heading_open" and t.map]
    ledger_line = rows[0][1] or 0
    start = max((x for x in heads if x <= ledger_line), default=0)
    stop = min((x for x in heads if x > ledger_line), default=len(text.splitlines()))
    odd = [n + 1 for n, l in enumerate(text.splitlines()[start:stop], start)
           if l[:1] and l[0] not in " \t" and (l[0].isspace() or unicodedata.category(l[0]) == "Zs")]
    if odd:                                               # REGRESSION-ANCHOR:unicode-ws
        print(f"[ledger] CANNOT LOOK :: line(s) {odd[:8]} in the ledger's section begin with non-ASCII "
              "whitespace, which GitHub and this parser render differently. Refusing.")
        return 2

    # orphans: ledger-shaped text AFTER the ledger and before the next heading -- a fragment of the
    # table, cut off by a blank line or a block the parser ended it at. Other sections' tables are not
    # suspects (review #13b: a legitimate table elsewhere mentioning a reviewer must not block commits).
    orphans, j = [], end_tok + 1
    while j < len(toks) and toks[j].type != "heading_open":
        t = toks[j]
        # an INDENTED or fenced code block after the table is visible too: a tab-indented row placed
        # after the last ledger row parses as code, and was missed while only inline text was scanned
        # (caught by this suite the moment a self row became the table's last row)
        if t.type in ("inline", "code_block", "fence"):
            for piece in re.split(r"\s*\n\s*", t.content):
                # a pipe-led line is a would-be row: look anywhere in its FIRST cell; any other line
                # must BEGIN with a ledger label (prose after the ledger may mention a reviewer)
                row_like = piece.lstrip().startswith("|")
                first = re.split(r"(?<!\\)\|", piece.strip().lstrip("|"))[0] if row_like else piece
                lab = re.sub(r"<[^>]+>", " ", first)
                lab = re.sub(r"[*_`\[\]()~>#\u26a0-]", " ", lab).strip()
                if (re.search if row_like else re.match)(r"(\b\d+\s+self\b|\bagy\b)", lab, re.I):
                    orphans.append(piece[:80])
        j += 1
    if orphans:                                           # REGRESSION-ANCHOR:orphans
        print("[ledger] CANNOT LOOK :: ledger-shaped text OUTSIDE the rendered ledger table -- the table "
              "has fragmented. Refusing:")
        for o in orphans:
            print(f"    {o}")
        return 2

    selves, agys, unclassified, noverdict = [], [], [], 0
    for cells, line in rows:
        if len(cells) < 2:
            unclassified.append(f"line {line}: fewer than 2 cells"); continue
        label, cell = cells[0], cells[1]
        nums = re.findall(r"-?\d+", cell)
        m = re.match(r"^(\d+)\s*\(self", label, re.I)
        if m:
            if len(nums) == 1 and int(nums[0]) >= 0:     # REGRESSION-ANCHOR:self-count
                selves.append((int(m.group(1)), int(nums[0]))); continue
            unclassified.append(f"line {line}: {label[:40]} | {cell[:30]}"); continue
        if re.search(r"\bagy\b", label, re.I):
            if len(nums) == 1 and int(nums[0]) >= 0:     # REGRESSION-ANCHOR:agy-count
                agys.append(int(nums[0])); continue
            if not nums and re.fullmatch(r"[\s\u26a0()\[\]-]*no verdict[\s\u26a0().-]*", cell, re.I):
                if reports_findings(" ".join(cells[2:])):
                    unclassified.append(f"line {line}: NO VERDICT row whose note reports findings"); continue
                noverdict += 1; continue
            unclassified.append(f"line {line}: {label[:40]} | {cell[:30]}"); continue
        unclassified.append(f"line {line}: {label[:40]} | {cell[:30]}")
    if unclassified:                                      # REGRESSION-ANCHOR:unclassified
        print("[ledger] CANNOT LOOK :: rendered ledger rows that could not be classified -- refusing "
              "rather than omitting them:")
        for u in unclassified:
            print(f"    {u}")
        return 2
    if not selves or not agys:
        print(f"[ledger] CANNOT LOOK :: parsed {len(selves)} self rows, {len(agys)} agy rows")
        return 2

    # the TOTAL, read from what is RENDERED -- never from comments, attributes or reference definitions
    # code blocks are VISIBLE: a stale TOTAL in a fenced or indented block is on the page (review #14b)
    shown = [visible(t) if t.type == "inline" else t.content for t in toks
             if t.type in ("inline", "fence", "code_block")]   # REGRESSION-ANCHOR:total-sources
    flat = re.sub(r"\s+", " ", " ".join(shown))
    hits = list(TOTAL.finditer(flat))
    if not hits:
        print("[ledger] CANNOT LOOK :: no rendered TOTAL sentence of the expected shape")
        return 2
    if len(hits) > 1:                                     # REGRESSION-ANCHOR:total-multiplicity
        print(f"[ledger] CANNOT LOOK :: {len(hits)} rendered TOTAL sentences; a quoted-but-stale one is "
              "indistinguishable from the live one. Refusing.")
        for hh in hits:
            print(f"    {hh.group(0)[:110]}")
        return 2
    m = hits[0]
    rounds = [n for n, _ in selves]
    bad = []
    if rounds != list(range(1, len(rounds) + 1)):
        bad.append(f"self rounds are not 1..N in order: {rounds}")
    self_sum, agy_sum = sum(c for _, c in selves), sum(agys)
    stated_last, self_addends, stated_self, agy_addends, stated_agy, stated_total = m.groups()
    def _ints(s_):
        return [int(x) for x in s_.split("+") if x.strip()]
    for label, stated_list, derived_list in (("self addends", _ints(self_addends), [c for _, c in selves]),
                                             ("independent addends", _ints(agy_addends), agys)):
        if len(stated_list) == len(derived_list) and stated_list != derived_list:   # REGRESSION-ANCHOR:elementwise
            diff = [(k + 1, a, b) for k, (a, b) in enumerate(zip(stated_list, derived_list)) if a != b]
            print(f"  MISMATCH {label:26s} differs at {len(diff)} position(s): "
                  + ", ".join(f"#{k}: stated {a} vs ledger {b}" for k, a, b in diff[:5]))
            bad.append(f"{label} differ elementwise at {len(diff)} position(s)")
    checks = [("last self round", int(stated_last), rounds[-1]),
              ("self total", int(stated_self), self_sum),
              ("independent total", int(stated_agy), agy_sum),
              ("grand total", int(stated_total), self_sum + agy_sum),
              ("self addend count", len(_ints(self_addends)), len(selves)),
              ("independent addend count", len(_ints(agy_addends)), len(agys))]
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
