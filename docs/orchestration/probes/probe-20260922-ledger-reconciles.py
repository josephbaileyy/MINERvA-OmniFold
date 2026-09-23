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
reads what that parser renders as visible text: `text` and `code_inline` content, code blocks and --
for the TOTAL only -- the text of raw-HTML blocks with comments and tags removed (`<pre>` and
`<details>` are shown on GitHub; review #15b). Inline raw HTML is never read. Lines in the ledger's
section that begin with non-ASCII whitespace, after any ASCII spaces, are refused, because GitHub and
markdown-it disagree about them.
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
import hashlib
import html
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
# NO VERDICT rows are PINNED, not parsed. Rules reading the NOTE's wording drew findings in seven reviews
# (#11b, #12b, #13b, #14b, #15b, #16b, #17b), each refusing a correct death note or accepting a note reporting
# findings. (Review #9's finding was about the FINDINGS cell: any cell mentioning NO VERDICT now goes to the pin
# first, whatever else it holds; review #18b.) A sentence
# cannot be read for "does this report findings?" by pattern. This ledger has had one NO VERDICT row since
# review #2, so the guard accepts exactly the rows listed here, keyed by a digest of the whole row as
# rendered. A new NO VERDICT row, or any edit to a listed one, is REFUSED until a human reads it and adds it.
NOVERDICT_PINNED = {
    "ada8cecd111592ac": "agy #2, attempt 1 -- died on a session rate limit during its first action (section 1a)",
}


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


def non_ascii_ws_led(line):
    s = line.lstrip(" \t")
    return bool(s[:1]) and (s[0].isspace() or unicodedata.category(s[0]) in ("Zs", "Zl", "Zp"))


def html_text(block):
    """What a reader sees of a raw-HTML block: comments dropped, tags dropped, entities decoded."""
    return html.unescape(re.sub(r"<[^>]*>", " ", re.sub(r"<!--.*?-->", " ", block, flags=re.S)))


def noverdict_key(cells):
    """Digest of the WHOLE rendered row -- label, findings cell and note -- so that ANY edit to a pinned row is
    refused here."""
    return hashlib.sha256("\n".join(cells).encode("utf-8")).hexdigest()[:16]


def main() -> int:
    if not REPORT.exists():                                  # REGRESSION-ANCHOR:pre-report
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
    if not ledgers:                                          # REGRESSION-ANCHOR:pre-ledger
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
    # ⚠ split on "\n" ONLY, as the parser does: `splitlines()` also breaks at form feed, U+0085 and U+2028, so
    # a row led by one of those looked pipe-led here, and every later line number drifted off the parser's
    # map (review #15b). And look PAST leading ASCII spaces: " \u00a0| row" renders like "\u00a0| row".
    lines = text.split("\n")
    stop = min((x for x in heads if x > ledger_line), default=len(lines))
    odd = [n + 1 for n, l in enumerate(lines[start:stop], start)
           if non_ascii_ws_led(l)]                    # REGRESSION-ANCHOR:ws-classes
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
            # ⚠ a findings cell that MENTIONS "no verdict" goes to the pin FIRST, whatever else it holds. The pin
            # was once reached only by a digit-free cell, so "NO VERDICT (attempt 1)" was counted as a review
            # with 1 finding, never pinned, and passed once its TOTAL was updated (review #18b)
            # and the MENTION is read on letters alone: `no\s+verdict` let NO-VERDICT, NOVERDICT, NO_VERDICT and
            # `no<br>verdict` (whose tag `visible()` drops) through to the count (review #19b)
            if "noverdict" in re.sub(r"[\W_]+", "", cell.lower()):     # REGRESSION-ANCHOR:noverdict-first
                key = noverdict_key(cells)
                if key not in NOVERDICT_PINNED:                  # REGRESSION-ANCHOR:noverdict-pinned
                    unclassified.append(f"line {line}: NO VERDICT row not in NOVERDICT_PINNED (key {key}); read it, "
                                        "confirm it reports no findings, and pin it"); continue
                noverdict += 1; continue
            if len(nums) == 1 and int(nums[0]) >= 0:     # REGRESSION-ANCHOR:agy-count
                agys.append(int(nums[0])); continue
            unclassified.append(f"line {line}: {label[:40]} | {cell[:30]}"); continue
        unclassified.append(f"line {line}: {label[:40]} | {cell[:30]}")
    if unclassified:                                      # REGRESSION-ANCHOR:unclassified
        print("[ledger] CANNOT LOOK :: rendered ledger rows that could not be classified -- refusing "
              "rather than omitting them:")
        for u in unclassified:
            print(f"    {u}")
        return 2
    if not selves or not agys:                               # REGRESSION-ANCHOR:pre-rows
        print(f"[ledger] CANNOT LOOK :: parsed {len(selves)} self rows, {len(agys)} agy rows")
        return 2

    # the TOTAL, read from what is RENDERED -- never from comments, attributes or reference definitions
    # code blocks are VISIBLE: a stale TOTAL in a fenced or indented block is on the page (review #14b)
    # and so is text inside raw HTML that is not a comment -- `<pre>`, `<details>` (review #15b)
    shown = [visible(t) if t.type == "inline" else html_text(t.content) if t.type == "html_block" else t.content
             for t in toks if t.type in ("inline", "fence", "code_block", "html_block")]   # REGRESSION-ANCHOR:total-sources
    flat = re.sub(r"\s+", " ", " ".join(shown))
    hits = list(TOTAL.finditer(flat))
    if not hits:                                             # REGRESSION-ANCHOR:pre-total
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
    if rounds != list(range(1, len(rounds) + 1)):      # REGRESSION-ANCHOR:round-order
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
    checks = [("last self round", int(stated_last), rounds[-1]),   # REGRESSION-ANCHOR:last-round
              ("self total", int(stated_self), self_sum),                    # REGRESSION-ANCHOR:self-total
              ("independent total", int(stated_agy), agy_sum),               # REGRESSION-ANCHOR:agy-total
              ("grand total", int(stated_total), self_sum + agy_sum),        # REGRESSION-ANCHOR:grand-total
              ("self addend count", len(_ints(self_addends)), len(selves)),   # REGRESSION-ANCHOR:self-addend-count
              ("independent addend count", len(_ints(agy_addends)), len(agys))]   # REGRESSION-ANCHOR:agy-addend-count
    for label, stated, derived in checks:
        mark = "ok " if stated == derived else "MISMATCH"
        print(f"  {mark} {label:26s} stated={stated:<5d} derived from ledger={derived}")
        if stated != derived:                                # REGRESSION-ANCHOR:scalar-compare
            bad.append(f"{label}: stated {stated}, ledger says {derived}")
    if bad:                                                  # REGRESSION-ANCHOR:any-bad
        print("\n[ledger] FAIL :: the TOTAL line does not reconcile with its own table")
        for b in bad:
            print(f"    {b}")
        return 1
    print(f"\n[ledger] PASS :: {len(selves)} self rounds and {len(agys)} independent reviews "
          f"reconcile ({noverdict} recorded non-verdict row(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
