#!/usr/bin/env python3
"""No unowned open issue: every OPEN row of KNOWN_ISSUES.md has exactly one line in the blocker registry.

    probe-20260923-no-unowned-open-issue.py [--self-test | --mutations]

`--mutations` applies each single-change mutation in MUTATIONS to a copy of this file and requires the copy's
self-test to FAIL. A claim that "every mutation turns the self-test red" was twice made about a mutation set
that lived only in scratch space, so nobody could re-run it (reviews #22a, #23a); the set is committed here.

The goal condition Joseph added on 2026-09-23: every OPEN row is either fixed and closed with evidence, or
names a blocker. Blockers live in ONE plain file, `docs/known-issues/BLOCKERS.tsv`, one line per OPEN row:

    <id> TAB <D7 | JOSEPH | OWNER> TAB <free text>

Blank lines and lines beginning `#` are ignored. The check refuses (exit 1), listing each case:
  * an OPEN row with no registry line, or with more than one;
  * a registry line naming an id that is not an OPEN row (fixed, or absent from the index);
  * a registry line that is not exactly three tab-separated fields, or whose kind is not D7, JOSEPH or
    OWNER, or whose text is empty;
  * an index status that does not BEGIN, after any bold markers, with a plain status word -- OPEN, FIXED,
    CLOSED, RESOLVED, WONTFIX or RETRACTED -- ending, after any closing bold markers, at the end of the cell,
    whitespace, `. , : ; )`, an en dash or an em dash. So `FIXED-pending`, `FIXED?` and `**FIXED**-x` are
    refused, and so is `FIXED_ x`: an underscore closes the word only if one opened it (⚠ this said *"a dash other
    than a hyphen"*, but no other dash is accepted; review #31a). Markup before the word (`~~`, `<del>`, a backtick)
    is refused, not interpreted;
  * a status other than OPEN whose cell also shows `open` after the word, in any case (`two literals still open`,
    `reopened`), because a closed row may carry an open residual (review #31b). It reads the RENDERED text (text
    and code spans, entities decoded, soft hyphens and zero-width characters dropped), not a link's target, so it
    also FAILS CLOSED on prose such as `the index said OPEN` or a code span such as `open()`, which must be
    reworded (review #32b). A residual described in other words (`pending`, `remaining`) is not detected;
  * an index id that is not plain letters and digits, or used by more than one row;
  * any table whose rendered header is not exactly the index header
    (`id | severity | status | one-sentence failure | detail | updated`): the index holds index tables only;
  * an absent registry file;
  * raw-HTML table markup (`<table>`, `<tr>`, `<td>` …), which renders as a table but cannot be read (review #29b);
  * a line of the index that begins with `|` but was not parsed as part of any table -- a row cut off by a
    stray blank line, an indent or an unclosed code fence is otherwise never seen (reviews #24b, #26b). This
    FAILS CLOSED on a pipe-led line inside a code block, such as a shell pipeline, which must be rewritten.
    A cut-off row WITHOUT a leading pipe, or inside a blockquote, is not detected, and neither is a whole
    pipe-less table written straight after a list item; the index always uses leading pipes (reviews #28b, #30b).
Exit 0 = none of these. Exit 2 = it could not read the index, including an index with NO table carrying the
index header (⚠ that case was first listed among the exit-1 refusals; review #28a).

⚠ WHY A REGISTRY. The first versions read blocker lines written as Markdown, in detail files or index rows.
Independent reviews #21b, #22b and #23b found 6, 7 and 11 defects, most of them about which Markdown forms
a blocker could take (links, emphasis, strikethrough, `<del>`, hard breaks, a second issue's file cited in the
same cell, root-absolute links); the rest were about status vocabulary and self-test power. On the real index
the check was not exact at #21b's, #22b's or #23b's sha: at all three, row 54's status read `**FIXED 2026-08-19**
…; two literals still open` and was read as FIXED, needing no blocker, and at #21b's `DETECTION` also exempted a
row with an open residual (⚠ this said *"exact at #22b's and #23b's shas"* (review #31b), then named only
`DETECTION` at #21b's (review #32a)). The SURFACE was the main problem, so it was removed rather than patched a fourth time. (⚠ This said
*"every one about … Markdown forms"* and *"exact on the real index each time"*; review #24a.) Of each index row, only the id and status
cells are interpreted; every cell, like the rest of the file, is also scanned for table structure and raw-HTML
table markup, which is refused wherever it appears. (⚠ This said *"only the id and status cells are read"*
(review #30a), then that the rest of the file alone was scanned (review #31a).)
It does NOT judge whether a blocker is TRUE; a
human does.
"""
import os
import re
import subprocess
import sys

try:
    from markdown_it import MarkdownIt
except ImportError:
    print("[owned] CANNOT LOOK :: markdown-it-py is not installed")
    sys.exit(2)

STATUSES = ("OPEN", "FIXED", "CLOSED", "RESOLVED", "WONTFIX", "RETRACTED")
KINDS = ("D7", "JOSEPH", "OWNER")
REGISTRY = "docs/known-issues/BLOCKERS.tsv"
MD = MarkdownIt("commonmark").enable(["table"])
# bold markers, then the word, then any CLOSING bold markers, then a real boundary. `FIXED-pending review; OPEN` and
# `**Fixed?** No — still OPEN` once read as FIXED because any non-letter ended the word (review #29b), and
# `**FIXED**-pending` still did while `*` itself counted as a boundary (review #30a). An underscore may close the
# word only if one opened it: `FIXED__ x` and `FIXED_ x` render literally and were read as FIXED (review #31b)
STATUS_RE = re.compile(r"^\s*(?:(?P<u>[*_]*_[*_]*)|\**)(?P<w>[A-Za-z]+)(?(u)[*_]*|\**)(?=$|[\s.,:;)\u2013\u2014])")   # en dash too (#30b)
# a closed status whose cell ALSO says open: `**FIXED …**; two literals still open` was read as FIXED, needing no
# blocker, on the real index at reviews #21b's, #22b's and #23b's shas (review #31b; ⚠ this said it "passed with no
# registry line" at #22b's and #23b's, but no registry existed then; review #32a). Any case, anywhere after the word,
# `reopened` too, read in the RENDERED text: a link target is not read, but emphasis, a tag or an entity inside the
# word does not hide it, nor does a soft hyphen or zero-width character (review #32b)
OPEN_WORD = re.compile(r"open", re.I)
INVISIBLE = re.compile("[\u00ad\u200b\u200c\u200d\u2060\ufeff]")
HTML_TABLE = re.compile(r"<\s*/?\s*t(able|head|body|r|d|h)\b", re.I)
ID_RE = re.compile(r"^[\s*_]*([A-Za-z0-9]+)[\s*_]*$")
# An index table is one whose header, AS RENDERED, is exactly this. The first rule ("first header cell is `id`")
# dropped a whole table headed `**id**` -- GitHub shows headers bold anyway -- and skipped every row of a
# two-column `id | status` table, both silently (review #27b). ANY table whose rendered header is not exactly this
# is REFUSED -- the index file holds index tables only -- so the status column is always the third.
HEADER = ("id", "severity", "status", "one-sentence failure", "detail", "updated")


def _rendered(inline):
    return " ".join("".join(c.content for c in (inline.children or []) if c.type in ("text", "code_inline")).split())


def _shown(inline):
    """The cell's visible text, pieces joined with NOTHING between them: `o*pe*n` shows as `open` (review #32b)."""
    return "".join(c.content for c in (inline.children or []) if c.type in ("text", "code_inline"))


def index_rows(text):
    """(id source, status source, line, status inline token) for each body row of each table whose rendered header is exactly HEADER,
    plus a list of problems: any table whose rendered header is not exactly HEADER, and `|`-led lines outside every
    parsed table."""
    toks, rows, problems, i = MD.parse(text), [], [], 0
    lines, covered = text.split("\n"), set()
    # ⚠ NO line is excused for sitting in a code block. Excusing FENCED blocks (to stop refusing a shell pipeline,
    # review #25b) let one unclosed ``` hide every row after it -- markdown-it runs an unclosed fence to the end of
    # the file -- so an unowned OPEN row PASSED (review #26b). A false refusal is safe; a false pass is not.
    while i < len(toks):
        if toks[i].type != "table_open":
            i += 1
            continue
        if toks[i].map:
            covered.update(range(toks[i].map[0], toks[i].map[1]))
        header, cur, j = None, None, i + 1
        while toks[j].type != "table_close":
            tk = toks[j]
            if tk.type == "tr_open":
                cur = (tk.map[0] + 1 if tk.map else 0, [])
            elif tk.type == "inline" and cur is not None:
                cur[1].append(tk)
            elif tk.type == "tr_close" and cur is not None:
                if header is None:
                    header = tuple(_rendered(c).lower() for c in cur[1])
                    # EVERY table in the index must be an index table: one whose first cell did not begin `id`
                    # (`Issue`, `#`, empty), or a stray row read as a header, hid its OPEN rows (review #28b)
                    if header != HEADER:
                        problems.append(f"line {cur[0]}: a table that is not an index table (its header is not exactly "
                                        f"{' | '.join(HEADER)}): {' | '.join(header)[:60]!r}")
                elif header == HEADER:
                    rows.append((cur[1][0].content, cur[1][2].content, cur[0], cur[1][2]))
                cur = None
            j += 1
        i = j + 1
    # a raw-HTML table renders as a table but is not parsed as one, so its rows would go unseen: REFUSED (review #29b)
    for tk in toks:
        bits = [tk.content] if tk.type == "html_block" else [c.content for c in (tk.children or []) if c.type == "html_inline"]
        # a comment renders nothing (#30b); HTML5 also ends one at `<!-->`, `<!--->` and `--!>`, so a strip that ran
        # on to the next `-->` hid the table after them (review #31b). An unclosed comment is not stripped
        bits = [re.sub(r"<!--(?:-?>|.*?--!?>)", "", b, flags=re.S) for b in bits]
        if any(HTML_TABLE.search(b) for b in bits):
            problems.append(f"line {(tk.map[0] + 1) if tk.map else '?'}: raw-HTML table markup, which this check cannot read; "
                            "write the table in Markdown")
    for n, l in enumerate(lines):          # every `|`-led line must lie inside SOME parsed table (review #24b)
        if INVISIBLE.sub("", l).lstrip().startswith("|") and n not in covered:     # a zero-width lead too (#32b)
            problems.append(f"line {n + 1}: a table-row line that is not part of any parsed table: {l.strip()[:50]!r}")
    return rows, problems


def read_registry(text):
    """{id: [(kind, text, line)]} and a list of problems."""
    reg, problems = {}, []
    text = text[1:] if text.startswith("\ufeff") else text      # a UTF-8 BOM (#24b), stripped where a shape can pin it (#25b)
    for n, line in enumerate(text.split("\n"), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        f = line.split("\t")
        if len(f) != 3:
            problems.append(f"{REGISTRY}:{n}: {len(f)} tab-separated field(s), not 3: {line[:60]!r}")
            continue
        rid, kind, body = f[0].strip(), f[1].strip(), f[2].strip()
        if kind not in KINDS:
            problems.append(f"{REGISTRY}:{n}: id {rid!r}: kind {kind!r} is not one of {', '.join(KINDS)}")
        if not body:
            problems.append(f"{REGISTRY}:{n}: id {rid!r}: empty blocker text")   # every registry id prints with !r (#27a)
        reg.setdefault(rid, []).append((kind, body, n))
    return reg, problems


def check(index_text, registry_text):
    """`registry_text` None means the registry file is absent. Both that and an index with no parsed rows are
    problems HERE, where the self-test reaches them; they were once decided only in main() (review #27b)."""
    rows, problems = index_rows(index_text)
    if not rows:
        problems.append("no index rows parsed: no table has exactly the index header")
    if registry_text is None:
        problems.append(f"{REGISTRY} does not exist")
    reg, rp = read_registry(registry_text if registry_text is not None else "")
    problems += rp
    open_ids, seen = set(), {}
    for id_src, status_src, line, stok in rows:
        m = ID_RE.match(id_src)
        if not m:
            problems.append(f"line {line}: id {id_src.strip()[:20]!r} is not plain letters and digits")
            continue
        rid = m.group(1)
        seen.setdefault(rid, []).append(line)
        s = STATUS_RE.match(status_src)
        if not s or s.group("w").upper() not in STATUSES:
            problems.append(f"line {line}: id {rid}: status {status_src.strip()[:40]!r} does not begin with a plain "
                            f"status word ({', '.join(STATUSES)})")
            continue
        shown, w = INVISIBLE.sub("", _shown(stok)).lstrip(), s.group("w")
        rest = shown[len(w):] if shown[:len(w)].upper() == w.upper() else shown
        if s.group("w").upper() != "OPEN" and OPEN_WORD.search(rest):
            problems.append(f"line {line}: id {rid}: status {status_src.strip()[:40]!r} is closed but also says open; "
                            "give the residual its own OPEN row, or reword")
            continue
        if s.group("w").upper() == "OPEN":
            open_ids.add(rid)
    for rid, lines in seen.items():
        if len(lines) > 1:
            problems.append(f"id {rid} is used by {len(lines)} rows (lines {', '.join(map(str, lines))})")
    for rid in sorted(open_ids):
        # only a VALID line owns a row: a malformed one is reported, and once also counted as the owner (#24a)
        n = len([e for e in reg.get(rid, []) if e[0] in KINDS and e[1]])
        if n != 1:
            problems.append(f"id {rid}: OPEN with {n} registry line(s) in {REGISTRY}, not 1"
                            + (" (UNOWNED)" if n == 0 else ""))
    for rid, entries in sorted(reg.items()):
        if rid not in open_ids:
            where = "is not an id in the index" if rid not in seen else "is not OPEN"
            problems.append(f"{REGISTRY}:{entries[0][2]}: id {rid!r} {where}, but has a registry line")   # !r: a BOM shows (#26b)
    return problems, len(rows), len(open_ids)


def decide(index_text, registry_text):
    """(exit status, lines to print) -- the whole verdict, above the mutation marker so that the self-test and
    `--mutations` reach it. main() once decided the exit status itself, unpinned (review #29b)."""
    problems, n_rows, n_open = check(index_text, registry_text)
    if not n_rows:
        return 2, ["[owned] CANNOT LOOK :: no issue rows parsed"]
    out = [f"  {p}" for p in problems]
    out.append(f"\n[owned] {'FAIL' if problems else 'PASS'} :: {n_rows} rows, {n_open} OPEN, {len(problems)} problem(s)")
    return (1 if problems else 0), out


def self_test():
    head = "| id | severity | status | one-sentence failure | detail | updated |\n|---|---|---|---|---|---|\n"
    shapes = [  # (name, index rows, registry, problems wanted)
        ("OPEN row with one registry line", "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER\tlane B\n", 0),
        ("OPEN row with no registry line", "| 1 | L | OPEN | x | d | u |\n", "", 1),
        ("OPEN row with two registry lines", "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER\ta\n1\tD7\tb\n", 1),
        ("a registry line for a FIXED row", "| 1 | L | FIXED | x | d | u |\n", "1\tOWNER\ta\n", 1),
        ("a registry line for an id not in the index", "| 1 | L | FIXED | x | d | u |\n", "9\tOWNER\ta\n", 1),
        ("an unknown kind: malformed, and the row stays unowned", "| 1 | L | OPEN | x | d | u |\n", "1\tMAYBE\ta\n", 2),
        ("empty blocker text: malformed, and the row stays unowned", "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER\t \n", 2),
        ("two fields, not three", "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER lane B\n", 2),
        ("comments and blank lines are ignored", "| 1 | L | OPEN | x | d | u |\n", "# c\n\n1\tJOSEPH\tt\n", 0),
        ("status in bold with a qualifier", "| 1 | L | **OPEN — DO NOT FIX** | x | d | u |\n", "1\tD7\tt\n", 0),
        ("status FIXED: with a colon, in bold", "| 1 | L | **FIXED:** 2026 at `abc` | x | d | u |\n", "", 0),
        ("lowercase open still needs a line", "| 1 | L | open | x | d | u |\n", "", 1),
        ("status struck with ~~ is refused, not read", "| 1 | L | ~~OPEN~~ FIXED | x | d | u |\n", "", 1),
        ("status in <del> is refused", "| 1 | L | <del>FIXED</del> OPEN | x | d | u |\n", "", 1),
        ("status in a code span is refused", "| 1 | L | `FIXED` | x | d | u |\n", "", 1),
        ("status word unknown", "| 1 | L | PENDING | x | d | u |\n", "", 1),
        ("REOPENED is not OPEN", "| 1 | L | REOPENED | x | d | u |\n", "", 1),
        # counts that DIFFER under the mutation each pins (a count equal either way pins nothing)
        ("OPENED is not OPEN, and its registry line is stray", "| 1 | L | OPENED | x | d | u |\n", "1\tOWNER\ta\n", 2),
        ("lowercase open with its registry line", "| 1 | L | open | x | d | u |\n", "1\tOWNER\ta\n", 0),
        ("four fields, not three", "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER\ta\tb\n", 2),
        ("a bold id is the same id", "| 1 | L | FIXED | x | d | u |\n| **1** | L | FIXED | y | d | u |\n", "", 1),
        ("an id with markup is refused", "| <span>1</span> | L | FIXED | x | d | u |\n", "", 1),
        ("an OPEN row in a SECOND table is checked",
         "| 1 | L | FIXED | x | d | u |\n\n## R\n\n" + head + "| 2 | L | OPEN | x | d | u |\n", "", 1),
        ("any non-index table is refused",
         "| 1 | L | FIXED | x | d | u |\n\n| name | a | status |\n|---|---|---|\n| z | L | OPEN |\n", "", 1),
        # --- review #28b
        ("a near-index table headed Issue is refused",
         "| 1 | L | FIXED | x | d | u |\n\n| Issue | severity | status | one-sentence failure | detail | updated |\n|---|---|---|---|---|---|\n| 74 | L | OPEN | x | d | u |\n", "", 1),
        ("a raw-HTML table is refused",
         "| 1 | L | FIXED | x | d | u |\n\n<table><tr><td>74</td><td>OPEN</td></tr></table>\n", "", 1),
        ("status FIXED-pending is refused", "| 1 | L | FIXED-pending; OPEN | x | d | u |\n", "", 1),
        ("status Fixed? is refused", "| 1 | L | **Fixed?** No \u2014 still OPEN | x | d | u |\n", "", 1),
        ("status **FIXED**-pending is refused", "| 1 | L | **FIXED**-pending review; OPEN | x | d | u |\n", "", 1),
        ("status FIXED_pending is refused", "| 1 | L | FIXED_pending_ OPEN | x | d | u |\n", "", 1),
        # --- review #30b: the HTML rule's inline, upper-case and nested forms, and what it must NOT refuse
        ("an inline raw-HTML table in a paragraph is refused",
         "| 1 | L | FIXED | x | d | u |\n\nSee: <table><tr><td>74</td><td>OPEN</td></tr></table>\n", "", 1),
        ("an upper-case raw-HTML table is refused",
         "| 1 | L | FIXED | x | d | u |\n\n<TABLE><TR><TD>74</TD><TD>OPEN</TD></TR></TABLE>\n", "", 1),
        ("a raw-HTML table nested in a div is refused",
         "| 1 | L | FIXED | x | d | u |\n\n<div>\n<table><tr><td>74</td></tr></table>\n</div>\n", "", 1),
        ("<td> in a code span is prose, not a table", "| 1 | L | FIXED | x | d | u |\n\nThe parser drops `<td>` cells.\n", "", 0),
        ("<td> in an HTML comment renders nothing", "| 1 | L | FIXED | x | d | u |\n\n<!-- <td> -->\n", "", 0),
        # --- review #32b: the open rule's case, substring and status coverage; what it reads; HTML in an index cell
        ("a FIXED status saying (reopened …) is refused", "| 1 | L | FIXED 2026-09-24 (reopened 2026-09-25) | x | d | u |\n", "", 1),
        ("a FIXED status saying residual OPEN is refused", "| 1 | L | FIXED \u2014 residual OPEN | x | d | u |\n", "", 1),
        *[(f"a {w} status saying still open is refused", f"| 1 | L | **{w} 2026-09-23** \u2014 two literals still open | x | d | u |\n", "", 1)
          for w in ("RESOLVED", "CLOSED", "WONTFIX", "RETRACTED")],
        ("a link TARGET naming OPEN is not read", "| 1 | L | FIXED (ruled at [OI-134](docs/OPEN_ITEMS.md)) | x | d | u |\n", "", 0),
        ("open() in a code span is refused (fail closed)", "| 1 | L | FIXED; `open()` now closes | x | d | u |\n", "", 1),
        *[(f"open hidden in the source ({s!r}) is refused", f"| 1 | L | FIXED; still {s} | x | d | u |\n", "", 1)
          for s in ("&#111;pen", "o*pe*n", "op<span></span>en", "op\u00aden", "op\u200ben")],
        ("raw-HTML table markup in an index cell is refused", "| 1 | L | FIXED | x | <table><tr><td>2</td></tr></table> | u |\n", "", 1),
        ("a row cut off after a zero-width lead is refused", "| 1 | L | FIXED | x | d | u |\n\n\u200b| 2 | L | OPEN | x | d | u |\n", "", 1),
        # --- review #31b: a closed status that also says open; underscores that are not markup; the comment forms
        #     HTML5 closes early; the inputs that each surviving weakening broke. Review #31a: <td> in a fenced block
        ("a FIXED status saying two literals are still open is refused",
         "| 1 | L | **FIXED 2026-08-19** at `abc`; two literals still open, see the end | x | d | u |\n", "", 1),
        ("a FIXED status saying reopened is refused", "| 1 | L | FIXED (reopened \u2014 OPEN) | x | d | u |\n", "", 1),
        *[(f"status {s!r} is refused", f"| 1 | L | {s} | x | d | u |\n", "", 1) for s in ("FIXED__ x", "**FIXED__** x", "FIXED_ x")],
        *[(f"status {s!r} is read as FIXED", f"| 1 | L | {s} x | x | d | u |\n", "", 0)
          for s in ("**FIXED*", "*FIXED**", "***FIXED***", "_FIXED_", "**FIXED:**")],
        ("a raw-HTML table between two comments is refused",
         "| 1 | L | FIXED | x | d | u |\n\n<!-- a --> <table><tr><td>2</td><td>OPEN</td></tr></table> <!-- b -->\n", "", 1),
        *[(f"a comment HTML5 ends early ({c!r}) does not hide a table", f"| 1 | L | FIXED | x | d | u |\n\n{c} <table><tr><td>2</td></tr></table> -->\n", "", 1)
          for c in ("<!-->", "<!--->", "<!-- a --!>")],
        ("a multi-line comment holding <td> renders nothing", "| 1 | L | FIXED | x | d | u |\n\n<!-- a\n<td> -->\n", "", 0),
        ("<track> is not table markup", "| 1 | L | FIXED | x | d | u |\n\n<video><track src=x></video>\n", "", 0),
        ("a stray <tr><td> is refused", "| 1 | L | FIXED | x | d | u |\n\n<tr><td>2</td></tr>\n", "", 1),
        ("a stray </table> is refused", "| 1 | L | FIXED | x | d | u |\n\n</table>\n", "", 1),
        ("<td> in a fenced code block is code, not a table", "| 1 | L | FIXED | x | d | u |\n\n```html\n<td>x</td>\n```\n", "", 0),
        ("an indented row directly under the table is refused",
         "| 1 | L | FIXED | x | d | u |\n    | 2 | L | OPEN | x | d | u |\n", "", 1),
        ("a bold OPEN id with its registry line", "| **1** | L | OPEN | x | d | u |\n", "1\tOWNER\ta\n", 0),
        ("a lower-case kind is refused, and the row stays unowned", "| 1 | L | OPEN | x | d | u |\n", "1\towner\ta\n", 2),
        ("a registry id in the wrong case owns nothing", "| J36 | L | OPEN | x | d | u |\n", "j36\tOWNER\ta\n", 2),
        ("a registry with two BOMs owns nothing", "| 1 | L | OPEN | x | d | u |\n", "\ufeff\ufeff1\tOWNER\ta\n", 2),
        # --- review #30b: each status boundary the real index uses, pinned
        *[(f"status boundary {s!r}", f"| 1 | L | {s} x | x | d | u |\n", "", 0)
          for s in ("**FIXED**", "__FIXED__", "FIXED.", "FIXED,", "FIXED;", "FIXED)", "FIXED\u2014pending", "FIXED\u2013pending")],
        ("a stray row plus a delimiter is refused",
         "| 1 | L | FIXED | x | d | u |\n\n| 74 | L | OPEN | x | d | u |\n|---|---|---|---|---|---|\n", "", 1),
        ("a header beginning `id` but not `id` is refused",
         "| 1 | L | FIXED | x | d | u |\n\n| id (x) | a | status |\n|---|---|---|\n| 2 | L | OPEN |\n", "", 1),
        # --- review #27b: index tables are recognised by their exact rendered header
        ("a bold **id** header is the index header", "", "", 1 - 1),
        ("a code `id` header is the index header", "", "", 0),
        ("a header with a doubled space is the index header", "", "", 0),
        ("a two-column id | status table is refused",
         "| 1 | L | FIXED | x | d | u |\n\n| id | status |\n|---|---|\n| 74 | OPEN |\n", "", 1),
        ("a three-column id table is refused",
         "| 1 | L | FIXED | x | d | u |\n\n| id | severity | status |\n|---|---|---|\n| 74 | L | OPEN |\n", "", 1),
        ("a header ID. is refused",
         "| 1 | L | FIXED | x | d | u |\n\n| ID. | severity | status | one-sentence failure | detail | updated |\n|---|---|---|---|---|---|\n| 74 | L | OPEN | x | d | u |\n", "", 1),
        ("a header whose third column is not status is refused",
         "| 1 | L | FIXED | x | d | u |\n\n| id | status | failure |\n|---|---|---|\n| 74 | OPEN | Closed form |\n", "", 1),
        ("no index table at all", None, "", 1),
        ("the registry file absent", "| 1 | L | FIXED | x | d | u |\n", None, 1),
        ("an indented comment line in the registry", "| 1 | L | OPEN | x | d | u |\n", "  # c\n1\tOWNER\ta\n", 0),
        # --- review #24b: the real index's letter ids and status words, and rows the parser would not see
        ("a letter id J36, OPEN with its line", "| J36 | L | OPEN | x | d | u |\n", "J36\tOWNER\ta\n", 0),
        *[(f"status {w} needs no line", f"| 1 | L | {w} 2026 | x | d | u |\n", "", 0)
          for w in ("CLOSED", "RESOLVED", "WONTFIX", "RETRACTED")],
        ("an id with trailing text is refused", "| 51 (reopened) | L | FIXED | x | d | u |\n", "", 1),
        ("spaces around the registry id and kind are accepted", "| 1 | L | OPEN | x | d | u |\n", " 1 \t OWNER \ta\n", 0),
        ("an upper-case ID header is still an index", "", "", 0),
        ("a row cut off by a blank line is refused",
         "| 1 | L | FIXED | x | d | u |\n\n| 2 | L | OPEN | x | d | u |\n", "", 1),
        ("a pipe-led line inside a fenced code block is refused (fail closed)",
         "| 1 | L | FIXED | x | d | u |\n\n```sh\ngrep x f \\\n  | sort\n```\n", "", 1),
        ("an unclosed fence does not hide an OPEN row after it",
         "| 1 | L | FIXED | x | d | u |\n\n```\n\n" + head + "| 2 | L | OPEN | x | d | u |\n", "", 3),
        ("a BOM before a data line", "| 1 | L | OPEN | x | d | u |\n", "\ufeff1\tOWNER\ta\n", 0),
        ("a registry beginning with a UTF-8 BOM", "| 1 | L | OPEN | x | d | u |\n", "\ufeff# c\n1\tOWNER\ta\n", 0),
        ("a row cut off by an indent is refused",
         "| 1 | L | FIXED | x | d | u |\n\n    | 2 | L | OPEN | x | d | u |\n", "", 1),
        ("CRLF registry lines", "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER\ta\r\n", 0),
    ]
    wrong = []
    # the exit status itself, through decide()
    one = head + "| 1 | L | OPEN | x | d | u |\n"
    for name, doc, reg, want in (("exit 0 when every OPEN row is owned", one, "1\tOWNER\ta\n", 0),
                                 ("exit 1 when an OPEN row is unowned", one, "", 1),
                                 ("exit 1 when the registry is absent", one, None, 1),
                                 ("exit 2 when no index table exists", "# none\n", "", 2)):
        rc, _ = decide(doc, reg)
        if rc != want:
            wrong.append(f"{name}: wanted exit {want}, got {rc}")
    for name, body, reg, want in shapes:
        if "upper-case ID" in name or "bold **id**" in name or "code `id`" in name or "doubled space" in name:
            h = (head.replace("| id |", "| ID |", 1) if "upper-case" in name else
                 head.replace("| id |", "| **id** |", 1) if "bold" in name else
                 head.replace("| id |", "| `id` |", 1) if "code" in name else
                 head.replace("one-sentence failure", "one-sentence  failure", 1))
            doc, reg = h + "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER\ta\n"
        elif body is None:
            doc = "# no table here\n"
        else:
            doc = head + body
        got, _, _ = check(doc, reg)
        if len(got) != want:
            wrong.append(f"{name}: wanted {want} problem(s), got {len(got)}: {got}")
    for w in wrong:
        print(f"  *** WRONG *** {w}")
    print(f"[owned self-test] {'FAIL' if wrong else 'PASS'} :: {len(shapes)} shapes and 4 exit checks")   # both (#30a)
    return 1 if wrong else 0


# (label, text in this file, replacement). Each must make the self-test fail. `--mutations` refuses (exit 2) if a
# text is not found exactly once, so a mutation cannot silently stop applying when the code moves.
MUTATIONS = [
    ("the registry-count check dropped", "        if n != 1:\n", "        if False:\n"),
    ("more than one line accepted", "        if n != 1:\n", "        if n == 0:\n"),
    ("stray registry lines accepted", "        if rid not in open_ids:\n", "        if False:\n"),
    ("any kind accepted", "        if kind not in KINDS:\n", "        if False:\n"),
    ("empty text accepted", "        if not body:\n", "        if False:\n"),
    ("a fourth field accepted", "        if len(f) != 3:\n", "        if len(f) not in (3, 4):\n"),
    ("comment lines read as entries", 'line.lstrip().startswith("#")', 'False'),
    ("markup before the status word read through", 'STATUS_RE = re.compile(r"^\\s*(?:', 'STATUS_RE = re.compile(r"^[\\s~<>/a-z`]*(?:'),
    ("any closing marker after the word", '(?(u)[*_]*|\\**)(?=', '[*_]*(?='),
    ("open matched as a whole word only", 'OPEN_WORD = re.compile(r"open", re.I)', 'OPEN_WORD = re.compile(r"\\bopen\\b", re.I)'),
    ("open matched case-sensitively", 'OPEN_WORD = re.compile(r"open", re.I)', 'OPEN_WORD = re.compile(r"open")'),
    ("only FIXED checked for open", '        if s.group("w").upper() != "OPEN" and OPEN_WORD.search', '        if s.group("w").upper() == "FIXED" and OPEN_WORD.search'),
    ("the status SOURCE read for open", 'INVISIBLE.sub("", _shown(stok)).lstrip(), s.group("w")', 'INVISIBLE.sub("", status_src).lstrip(), s.group("w")'),
    ("invisible characters kept", 'INVISIBLE.sub("", _shown(stok)).lstrip(), s.group("w")', '_shown(stok).lstrip(), s.group("w")'),
    ("shown pieces joined with a space", 'return "".join(c.content for c in (inline.children or []) if c.type in ("text", "code_inline"))', 'return " ".join(c.content for c in (inline.children or []) if c.type in ("text", "code_inline"))'),
    ("index cells not scanned for HTML", '    for tk in toks:\n        bits', '    for tk in [x for x in toks if not (x.map and x.map[0] in covered)]:\n        bits'),
    ("a zero-width lead hides a row", 'if INVISIBLE.sub("", l).lstrip().startswith("|")', 'if l.lstrip().startswith("|")'),
    ("a closed status that says open accepted", '        if s.group("w").upper() != "OPEN" and OPEN_WORD.search', '        if False and OPEN_WORD.search'),
    ("comments closed only by -->", 'r"<!--(?:-?>|.*?--!?>)"', 'r"<!--.*?-->"'),
    ("a greedy comment strip", 'r"<!--(?:-?>|.*?--!?>)"', 'r"<!--(?:-?>|.*--!?>)"'),
    ("a comment strip without re.S", '"", b, flags=re.S) for b in bits]', '"", b) for b in bits]'),
    ("fenced code scanned for HTML", 'bits = [tk.content] if tk.type == "html_block"', 'bits = [tk.content] if tk.type in ("html_block", "fence", "code_block")'),
    ("HTML_TABLE without a word boundary", 't(able|head|body|r|d|h)\\b", re.I)', 't(able|head|body|r|d|h)", re.I)'),
    ("HTML_TABLE matching <table only", 't(able|head|body|r|d|h)\\b", re.I)', 't(able)\\b", re.I)'),
    ("HTML_TABLE matching opening tags only", 'HTML_TABLE = re.compile(r"<\\s*/?\\s*t', 'HTML_TABLE = re.compile(r"<\\s*t'),
    ("a table covering one line more", 'covered.update(range(toks[i].map[0], toks[i].map[1]))', 'covered.update(range(toks[i].map[0], toks[i].map[1] + 1))'),
    ("registry kinds upper-cased", 'rid, kind, body = f[0].strip(), f[1].strip(), f[2].strip()', 'rid, kind, body = f[0].strip(), f[1].strip().upper(), f[2].strip()'),
    ("registry ids upper-cased", 'rid, kind, body = f[0].strip(), f[1].strip(), f[2].strip()', 'rid, kind, body = f[0].strip().upper(), f[1].strip(), f[2].strip()'),
    ("ids without leading markers", 'ID_RE = re.compile(r"^[\\s*_]*(', 'ID_RE = re.compile(r"^\\s*('),
    ("every BOM stripped", 'text = text[1:] if text.startswith("\\ufeff") else text', 'text = text.lstrip("\\ufeff")'),
    # ("a status read as a prefix (OPENED as OPEN)") is RETIRED as equivalent: the lookahead after the word admits
    # no letter, so a prefix alternation must still capture the whole leading run of letters. The same holds with
    # the closing-marker part, which admits no letter either. Review #30a TESTED an earlier rule on 1,075,265 inputs
    # (⚠ once cited as proof, and for the rule after it; review #31a). The "20 inputs" first cited were never listed.
    ("status read case-sensitively", 's.group("w").upper() not in STATUSES', 's.group("w") not in STATUSES'),
    ("ids with markup accepted", 'ID_RE = re.compile(r"^[\\s*_]*([A-Za-z0-9]+)[\\s*_]*$")', 'ID_RE = re.compile(r"^.*?([A-Za-z0-9]+).*$")'),
    ("bold ids not merged", 'ID_RE = re.compile(r"^[\\s*_]*([A-Za-z0-9]+)[\\s*_]*$")', 'ID_RE = re.compile(r"^\\s*([*_]*[A-Za-z0-9]+[*_]*)\\s*$")'),
    ("duplicates unchecked", "        if len(lines) > 1:\n", "        if False:\n"),
    ("second table ignored", "        i = j + 1\n    # a raw-HTML table", "        break\n    # a raw-HTML table"),
    ("any table read as an index", '                elif header == HEADER:', '                elif len(cur[1]) >= 3:'),
    ("non-index tables unrefused", '                    if header != HEADER:', '                    if header != HEADER and header[:1] and header[0].startswith("id"):'),
    ("code spans dropped from the header", 'if c.type in ("text", "code_inline")).split())', 'if c.type in ("text",)).split())'),
    ("header whitespace not normalised", ' if c.type in ("text", "code_inline")).split())', ' if c.type in ("text", "code_inline")).split(" "))'),
    ("header compared as source, not rendered", 'header = tuple(_rendered(c).lower() for c in cur[1])', 'header = tuple(c.content.strip().lower() for c in cur[1])'),
    ("absent registry unreported", '    if registry_text is None:\n        problems.append', '    if False:\n        problems.append'),
    ("empty index unreported", '    if not rows:\n        problems.append', '    if False:\n        problems.append'),
    ("indented comments read as entries", 'line.lstrip().startswith("#")', 'line.startswith("#")'),
    ("letter ids refused", 'ID_RE = re.compile(r"^[\\s*_]*([A-Za-z0-9]+)[\\s*_]*$")', 'ID_RE = re.compile(r"^[\\s*_]*([0-9]+)[\\s*_]*$")'),
    *[(f"{w} dropped", 'STATUSES = ("OPEN", "FIXED", "CLOSED", "RESOLVED", "WONTFIX", "RETRACTED")', 'STATUSES = ("OPEN", "FIXED", "CLOSED", "RESOLVED", "WONTFIX", "RETRACTED")'.replace(f', "{w}"', "")) for w in ("CLOSED", "RESOLVED", "WONTFIX", "RETRACTED")],
    ("registry id unstripped", "rid, kind, body = f[0].strip(), f[1].strip()", "rid, kind, body = f[0], f[1].strip()"),
    ("registry kind unstripped", "rid, kind, body = f[0].strip(), f[1].strip()", "rid, kind, body = f[0].strip(), f[1]"),
    ("header case-sensitive", 'header = tuple(_rendered(c).lower() for c in cur[1])', 'header = tuple(_rendered(c) for c in cur[1])'),
    ("id with trailing text read", 'ID_RE = re.compile(r"^[\\s*_]*([A-Za-z0-9]+)[\\s*_]*$")', 'ID_RE = re.compile(r"^[\\s*_]*([A-Za-z0-9]+)")'),
    ("a malformed line owns its row", "if e[0] in KINDS and e[1]])", "if True])"),
    ("fenced blocks excused", '    lines, covered = text.split("\\n"), set()',
     '    lines, covered = text.split("\\n"), set()\n    covered.update(x for tk in toks if tk.type == "fence" and tk.map for x in range(*tk.map))'),
    ("a BOM not stripped", 'text = text[1:] if text.startswith("\\ufeff") else text', 'text = text'),
    ("inline HTML not scanned", 'else [c.content for c in (tk.children or []) if c.type == "html_inline"]', 'else []'),
    ("HTML tags matched case-sensitively", 'r"<\\s*/?\\s*t(able|head|body|r|d|h)\\b", re.I)', 'r"<\\s*/?\\s*t(able|head|body|r|d|h)\\b")'),
    ("HTML matched only at the start", '        if any(HTML_TABLE.search(b) for b in bits):', '        if any(HTML_TABLE.match(b) for b in bits):'),
    ("HTML comments scanned", '        bits = [re.sub(r"<!--(?:-?>|.*?--!?>)", "", b, flags=re.S) for b in bits]', '        bits = bits'),
    *[(f"status boundary {c!r} dropped", '(?=$|[\\s.,:;)\\u2013\\u2014])")', '(?=$|[\\s.,:;)\\u2013\\u2014])")'.replace(c, "", 1))
      for c in (".", ",", ";", ")", "\\u2013", "\\u2014")],
    ("closing bold markers not consumed", '(?P<w>[A-Za-z]+)(?(u)[*_]*|\\**)(?=$|', '(?P<w>[A-Za-z]+)(?=$|'),
    ("bold markers counted as a boundary", '(?(u)[*_]*|\\**)(?=$|[\\s.,:;)', '(?=$|[\\s*_.,:;)'),
    ("raw-HTML tables unrefused", '        if any(HTML_TABLE.search(b) for b in bits):', '        if False:'),
    ("status word ended by any non-letter", '(?(u)[*_]*|\\**)(?=$|[\\s.,:;)\\u2013\\u2014])")   # en dash', '(?![A-Za-z])")   # en dash'),
    ("exit 1 reported as 0", "    return (1 if problems else 0), out", "    return 0, out"),
    ("no-rows exit 2 dropped", "    if not n_rows:\n        return 2,", "    if False:\n        return 2,"),
    ("rows outside tables unseen", '        if INVISIBLE.sub("", l).lstrip().startswith("|") and n not in covered:', '        if False:'),
]


def mutations():
    import tempfile
    src = open(__file__, encoding="utf-8").read()
    body = src[:src.index("# (label, text in this file, replacement).")]    # mutate the CODE, not this list
    alive, broken = [], []
    with tempfile.TemporaryDirectory() as td:
        for label, a, b in MUTATIONS:
            if body.count(a) != 1:
                broken.append(f"{label}: its text occurs {body.count(a)} times in the code, not once")
                continue
            p = os.path.join(td, "m.py")
            open(p, "w", encoding="utf-8").write(src.replace(a, b, 1))
            r = subprocess.run([sys.executable, p, "--self-test"], capture_output=True, text=True)
            # KILLED only if the self-test ran and reported a failed shape: a SyntaxError prints no "Traceback"
            # and was once counted as red (review #24b)
            if r.returncode == 0:
                alive.append(label)
            elif "[owned self-test] FAIL" not in r.stdout:
                broken.append(f"{label}: the mutated file did not run its self-test to a FAIL (it crashed)")
    for x in broken:
        print(f"  ?? {x}")
    for x in alive:
        print(f"  *** SURVIVED *** {x}")
    print(f"[owned mutations] {'FAIL' if alive or broken else 'PASS'} :: {len(MUTATIONS)} mutations, "
          f"{len(MUTATIONS) - len(alive) - len(broken)} turn the self-test red")
    return 2 if broken else 1 if alive else 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    if "--mutations" in sys.argv:
        return mutations()
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    if not root:
        print("[owned] CANNOT LOOK :: not inside a git work tree")
        return 2
    os.chdir(root)
    try:
        index = open("KNOWN_ISSUES.md", encoding="utf-8").read()
    except OSError as e:
        print(f"[owned] CANNOT LOOK :: {e}")
        return 2
    registry = open(REGISTRY, encoding="utf-8").read() if os.path.exists(REGISTRY) else None
    rc, out = decide(index, registry)
    print("\n".join(out))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
