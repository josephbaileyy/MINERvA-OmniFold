#!/usr/bin/env python3
"""No unowned open issue: every OPEN row of KNOWN_ISSUES.md has exactly one line in the blocker registry.

    probe-20260923-no-unowned-open-issue.py [--self-test | --mutations]

Any other argument, or both together, exits 2: a mistyped `--mutation` once ran the live check and exited 0
(review #35b).

`--mutations` applies each single-change mutation in MUTATIONS to a copy of this file and requires the copy's
self-test to FAIL, after requiring the UNMUTATED self-test to pass; before Python 3.12 the f-string mutant counts as
red when it fails to COMPILE, and its self-test never runs (review #43b), and the nested-f-string mutant, whose
check runs only from 3.12, is SKIPPED and counted as skipped in the summary line (row 148; review #45a). Everything above MUTATIONS, main() included,
can be mutated; `mutations()` itself, below it, cannot, and its tally is checked only by reading it (review #36b).
It runs every child under clean_env(), so no mutant reaches the caller's repository (review #39b). A claim that "every mutation turns the self-test red" was twice made about a mutation set
that lived only in scratch space, so nobody could re-run it (reviews #22a, #23a); the set is committed here.

The goal condition Joseph added on 2026-09-23: every OPEN row is either fixed and closed with evidence, or
names a blocker. Blockers live in ONE plain file, `docs/known-issues/BLOCKERS.tsv`, one line per OPEN row:

    <id> TAB <D7 | JOSEPH | OWNER> TAB <free text>

Blank lines and lines beginning `#` are ignored. The check refuses (exit 1), listing each case:
  * an OPEN row with no registry line, or with more than one;
  * a registry line naming an id that is not an OPEN row (fixed, or absent from the index);
  * a registry line that is not exactly three tab-separated fields, or whose kind is not D7, JOSEPH or
    OWNER, or whose text is empty or only invisible characters (review #35b);
  * an index status that does not BEGIN, after any bold markers, with a plain status word -- OPEN, FIXED,
    CLOSED, RESOLVED, WONTFIX or RETRACTED -- ending, after any closing bold markers, at the end of the cell,
    whitespace, `. , : ; )`, an en dash or an em dash. So `FIXED-pending`, `FIXED?` and `**FIXED**-x` are
    refused, and so is `FIXED_ x`: an underscore closes the word only if one opened it (⚠ this said *"a dash other
    than a hyphen"*, but no other dash is accepted; review #31a). Markup before the word (`~~`, `<del>`, a backtick)
    is refused, not interpreted;
  * a status other than OPEN whose cell also shows `open` after the word, in any case (`two literals still open`,
    `reopened`), because a closed row may carry an open residual (review #31b). It reads the RENDERED text (text
    and code spans and rendered image alt text, entities decoded, soft hyphens and every other invisible format
    character dropped, and `\u03c3` read as `o`), not a link's target, so it
    also FAILS CLOSED on prose such as `the index said OPEN` or a code span such as `open()`, which must be
    reworded (review #32b). A residual described in other words (`pending`, `remaining`) is not detected;
  * a status other than OPEN that SHOWS a letter of a script other than Latin or Greek, or a format character:
    refused, not interpreted (reviews #43b, #44b). Punctuation, symbols, numbers, spaces, tabs and nonspacing and
    enclosing marks (Mn, Me) are allowed, and dropped before the open check; spacing marks (Mc) are refused (⚠ this
    said *"combining marks"*; review #45a). A Latin or Greek letter is allowed and READ: as its ASCII
    letter if NFKD reduces it to one (`\u00e9`, fullwidth, superscript), as o, p, e or n if its Unicode name makes it a
    form of one (`\u00f8`, `\u01dd`, `\u014b`, small capitals, Greek omicron, rho, epsilon, eta, nu, sigma), else as itself
    (`\u00df`, `\u03c7`, `\u0394`). A symbol or other letter shaped like one (`\u25cbpen`, `\ua74fpen`) is NOT seen (⚠ this
    once said a lone combining mark is refused; review #44b);
  * a row whose line holds, from its status cell on, a `|` inside a code span (an escaped `\\|` there is kept), link
    (text, target or title), image, autolink or HTML tag, as markdown-it parses it with the index's reference
    definitions, or a raw `|` inside `[...]`: FAILS CLOSED, since such a pipe may have cut the status and cannot be
    told apart from one that did. So a correct row holding such a span in a later cell, a search URL with `%7C`, or
    a lone backtick that pairs across cells is refused too, and must be rewritten (reviews #42b-#49b; four cleverer
    rules each missed a cut or refused a row in a new way). A `|` in plain prose or math, such as `P(a|b)`, in a row
    ALSO missing a cell is not detected: nothing is left open (review #45b);
  * an index id that is not plain letters and digits, or used by more than one row;
  * an index row whose severity is not one the index uses (CRITICAL, BLOCKER, HIGH, MEDIUM, LOW, TRAP; bold or
    any case, but no qualifier such as `HIGH (was MEDIUM)`), whose `updated` cell is empty (a row missing a cell
    shifts its status column), or that has MORE cells than the header, which the parser drops, or an unescaped
    `|` inside a code span: such a pipe always splits a cell (reviews #39b, #40b, #42b);
  * any table whose rendered header is not exactly the index header
    (`id | severity | status | one-sentence failure | detail | updated`): the index holds index tables only;
  * an absent registry file;
  * raw-HTML table markup (`<table>`, `<tr>`, `<td>` …), which renders as a table but cannot be read (review #29b);
  * a line of the index that begins with `|` but was not parsed as part of any table -- a row cut off by a
    stray blank line, an indent or an unclosed code fence is otherwise never seen (reviews #24b, #26b). This
    FAILS CLOSED on a pipe-led line inside a code block, such as a shell pipeline, which must be rewritten.
    Behind a quote or list marker a line counts only with three pipes, so prose such as `- |x| is abs` passes
    (review #43b). A cut-off row WITHOUT a leading pipe is not detected (⚠ this also said *"or inside a blockquote"*,
    detected since `82478c2b`; review #43b), and neither is a whole
    pipe-less table written straight after a list item; the index always uses leading pipes (reviews #28b, #30b).
Exit 0 = none of these. Exit 2 = it could not read the index, including an index with NO table carrying the
index header or one with no body rows (the problems found on the way are printed too; review #39b) (⚠ that case was first listed among the exit-1 refusals; review #28a), or when the index or the
registry is not UTF-8, is a directory, or is a symlink to nothing (these once raised or, for the symlink, counted
as an absent registry, exiting 1; reviews #34b, #35a). A registry that does not exist at all is the exit-1
refusal above. It checks the git work tree holding
the CURRENT DIRECTORY, not the one holding this file (review #34b), whatever GIT_DIR or GIT_WORK_TREE say; it
exits 2 when git cannot run (review #37b). The SELF-TEST needs git: without it the git-init report and every command check that needs a work
tree FAIL, exit 1 (⚠ this gave a count, *"four of the six"*, that the next command check made stale; review #40b), and `--mutations` exits 2 (⚠ `a3fc3486` called it green there; it raised; review #38a; ⚠ this said *"the
command checks FAIL"*; two do not; review #39a).

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
import unicodedata

try:
    from markdown_it import MarkdownIt
except ImportError:
    print("[owned] CANNOT LOOK :: markdown-it-py is not installed")
    sys.exit(2)

STATUSES = ("OPEN", "FIXED", "CLOSED", "RESOLVED", "WONTFIX", "RETRACTED")
# every severity the index has used, 3,273 rows over its history (review #39b): a row missing its severity cell shifted
# its status into the severity column and read `Fixed seeds…` as the status, hiding an OPEN row. A short row is also
# padded by the parser with an empty last cell, and no historical row has an empty `updated`
SEVERITIES = ("CRITICAL", "BLOCKER", "HIGH", "MEDIUM", "LOW", "TRAP")
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
# word does not hide it, nor does a soft hyphen or zero-width character (review #32b). INVISIBLE is EVERY Unicode
# format character (category Cf) plus every Default_Ignorable_Code_Point (Unicode 15.0 DerivedCoreProperties, listed
# below): a list of six missed U+200E and U+034F (#33b), and Cf alone missed variation selectors and fillers (#34b)
OPEN_WORD = re.compile(r"open", re.I)
# A closed status may SHOW only these characters: printable ASCII and the 12 others its 59 historical status cells use.
# (⚠ since superseded below: look-alike Latin and Greek letters are READ, Mn/Me marks allowed and DROPPED; format
# characters (Cf) stay REFUSED (⚠ this said invisibles were dropped; #46a); #45a)
# Look-alike letters, combining marks and invisible characters are refused, not interpreted: special cases for each
# (NFKC, a Cyrillic/Greek fold) kept missing the next one, and NFKC itself composed `open` + U+0303 away (review #43b)
STATUS_CHARS = set(map(chr, range(32, 127))) | set("\u2014\u2026\u2013\u00b1\u2225\u2212\u00b7\u03bb\u03c3\u00d7\u2248\u2264")
# ...widened by CLASS, since a set of 12 refused `→`, curly quotes, `≥` and `café` (self-found, 2026-09-24): any
# punctuation, symbol, number or space; and any letter that NFKD reduces to an ASCII letter (`é`, `ｏ`, `ᵒ`), which is
# then READ as that letter, so `opén` and `ｏｐｅｎ` still say open. Other letters, marks and format characters are refused
# (⚠ superseded below: Latin and Greek letters are READ; Mn/Me marks, including the Mn members of INVISIBLE, and U+2800
# are allowed and DROPPED; Cf and the Hangul fillers stay refused (⚠ this said "non-Cf invisibles"; #46a); #45b)
# a letter that reduces to no ASCII letter is READ by its Unicode name when it is a form of o, p, e or n (`ø`, `ǝ`, `ƥ`,
# `ŋ`, Greek omicron, rho, epsilon, eta, nu, sigma), so `øpen` still says open; refusing them refused `Løvås`, and every
# Greek letter but two refused `χ²`, `Δ` and `ν_μ` in a physics index (review #44b)
LOOKS = {"O": "o", "P": "p", "E": "e", "N": "n", "ENG": "n", "OMICRON": "o", "RHO": "p", "EPSILON": "e", "ETA": "n",
         "NU": "n", "SIGMA": "o"}


def letter_as(c):
    """The letter `c` reads as for the open check: an ASCII letter, "" for itself, or None if refused."""
    base = unicodedata.normalize("NFKD", c)[:1]
    if base.isascii() and base.isalpha():
        return base.lower()
    # the name of the NFKD base counts too: MICRO SIGN is Greek mu once decomposed
    words = (unicodedata.name(c, "") + " " + unicodedata.name(base, "")).replace("-", " ").split()
    if "LATIN" not in words and "GREEK" not in words:
        return None                        # other scripts' letters: refused, not interpreted (review #43b)
    hits = {LOOKS[w] for w in words if w in LOOKS}
    return hits.pop() if len(hits) == 1 else (None if hits else "")


def status_char_ok(c):
    cat = unicodedata.category(c)
    if c in STATUS_CHARS or c == "\t" or cat[0] in "PSN" or cat == "Zs" or cat in ("Mn", "Me"):   # marks: fold() drops them
        return True
    return cat[0] == "L" and letter_as(c) is not None


def fold(s):
    """Letters read as ASCII where they can be, nonspacing and enclosing marks (Mn, Me) and invisible characters
    dropped: what `open` is searched in. Spacing marks (Mc) are not dropped; status_char_ok() refuses them first
    (⚠ this said *"marks dropped"*; review #44a)."""
    # every mark and invisible character goes, not only those with a combining class: a variation selector or the
    # grapheme joiner (class 0) once kept `op` + mark + `en` from reading as open (self-found, 2026-09-24)
    # a letter is read BEFORE it is decomposed: `ŉ` (n after an apostrophe) reads as n, but its NFKD is a modifier
    # apostrophe and n, which once hid `opeŉ` (review #46b)
    out = []
    for ch in s:
        a = letter_as(ch) if unicodedata.category(ch)[0] == "L" else None
        for c in (a,) if a else unicodedata.normalize("NFKD", ch):
            if unicodedata.category(c) in ("Mn", "Me") or INVISIBLE.match(c):
                continue
            b = letter_as(c) if unicodedata.category(c)[0] == "L" else None
            out.append(b if b else c)
    return "".join(out)
# the quote and list markers in front of a row line are the parser's, not the row's (reviews #41b, #42b)
CONTAINER = re.compile(r"^(?:\s*(?:>|[-*+](?=\s)|\d{1,9}[.)](?=\s)))*\s*")
_DI = {c for a, b in ((0xAD, 0xAD), (0x34F, 0x34F), (0x61C, 0x61C), (0x115F, 0x1160), (0x17B4, 0x17B5), (0x180B, 0x180F),
                      (0x200B, 0x200F), (0x202A, 0x202E), (0x2060, 0x206F), (0x3164, 0x3164), (0xFE00, 0xFE0F),
                      (0xFEFF, 0xFEFF), (0xFFA0, 0xFFA0), (0xFFF0, 0xFFF8), (0x1BCA0, 0x1BCA3), (0x1D173, 0x1D17A),
                      (0xE0000, 0xE0FFF)) for c in range(a, b + 1)} | {0x2800}   # Braille blank renders blank too (#37b)
INVISIBLE = re.compile("[" + "".join(re.escape(chr(c)) for c in range(sys.maxunicode + 1)
                                     if unicodedata.category(chr(c)) == "Cf" or c in _DI) + "]")
HTML_TABLE = re.compile(r"<\s*/?\s*t(able|head|body|r|d|h)\b", re.I)
ID_RE = re.compile(r"^[\s*_]*([A-Za-z0-9]+)[\s*_]*$")
# An index table is one whose header, AS RENDERED, is exactly this. The first rule ("first header cell is `id`")
# dropped a whole table headed `**id**` -- GitHub shows headers bold anyway -- and skipped every row of a
# two-column `id | status` table, both silently (review #27b). ANY table whose rendered header is not exactly this
# is REFUSED -- the index file holds index tables only -- so the status column is always the third.
HEADER = ("id", "severity", "status", "one-sentence failure", "detail", "updated")


def pipe_spans(s, env=None):
    """How many code spans, links (text or target), images, autolinks and HTML tags markdown-it finds in `s` that hold
    a `|` -- a pipe the table split at, so a span that was cut. The parser, not a hand-written scan, decides: three
    versions of a backtick scan each missed an escape, an HTML tag, an autolink or a bracketed target (reviews
    #44b-#46b). A pipe escaped inside a code span is kept; in a link it cannot be told apart and is counted."""
    n, depth = 0, 0
    for tk in MD.parseInline(s, env or {})[0].children or []:
        href = (tk.attrs or {}).get("href", "") + (tk.attrs or {}).get("src", "") + (tk.attrs or {}).get("title", "")   # title too (#48b)
        if tk.type == "code_inline":
            n += bool(re.search(r"(?<!\\)\|", tk.content))
        elif tk.type == "html_inline":
            n += "|" in tk.content
        elif tk.type == "link_open":
            depth += 1
            n += "|" in href or "%7C" in href.upper()
        elif tk.type == "link_close":
            depth -= 1
        elif tk.type == "image":
            n += "|" in href or "%7C" in href.upper() or "|" in tk.content
        elif depth and "|" in tk.content:
            n += 1
    return n


def status_cut(src, env=None):
    """True if row line `src` holds, from its status cell on, a pipe inside a span: a code span (an escaped `\\|` there
    is kept), link (text, target or title), image, autolink or HTML tag, as markdown-it itself parses it with the
    index's reference definitions, or a raw `|` inside `[...]`. Such a pipe either split the status cell or cannot be
    told apart from one that did, so the row FAILS CLOSED and must be rewritten. Four cleverer rules -- a hand-written
    backtick scan, a span count from the cell's start against its end, a leftover opener, and both -- each missed cuts
    or refused correct rows in a new way (reviews #44b-#49b); across all 255 distinct row lines in the index's history
    this blunt rule refuses only two, row 69's 10-cell versions, which the extra-cells rule refuses anyway. Against
    the three oracles reviews #47a, #48b and #49a built (6,720, 781,612 and 1,412,346 constructed rows) it misses no
    cut, and fails closed on 684, 219,504 and 378,843 of them, the price of refusing every pipe-holding span."""
    pipes = [m.start() for m in re.finditer(r"(?<!\\)\|", src)]
    k = 2 if src.startswith("|") else 1
    if len(pipes) <= k:
        return False
    rest = src[pipes[k] + 1:]
    cell = src[pipes[k] + 1:pipes[k + 1] if len(pipes) > k + 1 else len(src)]
    # and a status cell ending inside a link target `](...` it never closes: a defined `[a]` once let the parser read
    # `[a](|[a](` as plain text around the pipe (review #49a's oracle); a code span holding `](` fails closed with it
    return (pipe_spans(rest, env) > 0 or bool(re.search(r"\[[^\[\]]*(?<!\\)\|[^\[\]]*\]", rest))
            or bool(re.search(r"\]\([^)]*$", cell.strip())))


def fstring_backslashes(src):
    """Line numbers of a backslash inside an f-string's braces, which Python before 3.12 cannot parse. Read by Python's
    own tokenizer, every prefix (F, rf, fr), nested f-strings too (reviews #43a, #44b). Before 3.12 the tokenizer has no
    f-string tokens, and source that compiled there has no such backslash anyway."""
    import io
    import tokenize
    hits, depth = [], 0
    if not hasattr(tokenize, "FSTRING_START"):
        return hits
    for tk in tokenize.generate_tokens(io.StringIO(src).readline):
        if tk.type == tokenize.FSTRING_START:
            depth += 1
        elif tk.type == tokenize.FSTRING_END:
            depth -= 1
        elif depth and "\\" in tk.string and (tk.type != tokenize.FSTRING_MIDDLE or depth > 1):
            hits.append(tk.start[0])
    return hits


def _rendered(inline):
    return " ".join("".join(c.content for c in (inline.children or []) if c.type in ("text", "code_inline")).split())


def _shown(inline):
    """The cell's visible text, pieces joined with NOTHING between them: `o*pe*n` shows as `open` (review #32b)."""
    return "".join(c.content if c.type != "image" else "".join(x.content for x in (c.children or []) if x.type in ("text", "code_inline"))
                   for c in (inline.children or []) if c.type in ("text", "code_inline", "image"))   # alt, rendered (#34b, #43b)


def index_rows(text):
    """(id source, status source, line, status inline token, rendered severity, rendered updated) for each body row of each table whose rendered header is exactly HEADER,
    plus a list of problems: any table whose rendered header is not exactly HEADER, and `|`-led lines outside every
    parsed table."""
    text = text[1:] if text.startswith("\ufeff") else text      # a BOM before a first table line hid the table (#34b)
    # markdown-it ends a line at a lone CR, `split("\n")` does not: two in a table shifted the numbering, and a cut-off
    # OPEN row after it fell on a "covered" line and passed (review #36b). Only for a string passed to check(): the
    # command reads through read_file(), whose universal newlines already convert every CR (⚠ first stated without
    # this scope; review #37b)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    env = {}                                   # the index's reference definitions, for status_cut() (#47b)
    toks, rows, problems, i = MD.parse(text, env), [], [], 0
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
                    # the parser DROPS cells beyond the header's six: an open residual after a pipe in a code span
                    # vanished from the status (review #40b); history has two 10-cell versions of row 69
                    # blockquote markers are the parser's, not the row's: a quoted index table was refused (#41b)
                    src = CONTAINER.sub("", lines[cur[0] - 1]).strip() if 0 < cur[0] <= len(lines) else ""
                    cells = len(re.findall(r"(?<!\\)\|", src)) + 1 - src.startswith("|") - bool(re.search(r"(?<!\\)\|$", src))
                    if cells > len(HEADER):
                        problems.append(f"line {cur[0]}: {cells} cells, more than the header's {len(HEADER)}; an "
                                        "unescaped `|` (in a code span too) splits a cell")
                    # a status cut short by a `|` ends inside a code span or link target (⚠ this said "or parenthesis":
                    # no parenthesis is checked; #45b): with a cell also missing,
                    # the count stayed six and the residual left the status unseen (review #42b). The status cell itself
                    # is checked, not the whole line, whose backticks pair across cells (review #43b)
                    # backtick RUNS are paired as CommonMark pairs them, equal length to equal length: a parity count
                    # missed ``a|b`` and refused ``a`b`` (review #44b). Brackets are not counted, since `[0, 1.5)` is an
                    # interval (⚠ superseded: `[` and `<` are read again, by status_cut(); #48b); an unclosed link TARGET at the cell's
    # end is refused (⚠ this sentence once stopped at
                    # "is"; #45a). All of this is now the parser's, below: a pipe in link TEXT is caught too, and only
                    # a pipe in plain prose or math, in a row also missing a cell, goes undetected (⚠ this said link text
                    # alone; #46a)
                    st = cur[1][2].content if len(cur[1]) > 2 else ""
                    # markdown-it itself decides (see pipe_spans); the hand-written scan and link regex are gone (#46b)
                    if cells <= len(HEADER) and status_cut(src, env):
                        problems.append(f"line {cur[0]}: from the status cell {st.strip()[:30]!r} on, a `|` sits inside a "
                                        "code span, link, image or HTML tag: it may have cut the status; rewrite it")
                    c = cur[1] + [None] * (6 - len(cur[1]))     # never shorter here; a mutant reads other tables
                    rows.append((c[0].content, c[2].content, cur[0], c[2],
                                 _rendered(c[1]) if c[1] else "", _rendered(c[5]) if c[5] else ""))
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
        bare = INVISIBLE.sub("", l)
        lead = CONTAINER.sub("", bare)
        # behind a quote or list marker a line is a row only with a row's pipes: `- |x| is abs` was refused (review #43b)
        if lead.startswith("|") and n not in covered and (lead == bare.lstrip() or len(re.findall(r"(?<!\\)\|", lead)) >= 3):
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
        if not INVISIBLE.sub("", body).strip():         # a text of only U+200B once owned a row (#35b)
            problems.append(f"{REGISTRY}:{n}: id {rid!r}: empty blocker text")   # every registry id prints with !r (#27a)
        reg.setdefault(rid, []).append((kind, body, n))
    return reg, problems


def check(index_text, registry_text):
    """`registry_text` None means the registry file is absent. Both that and an index with no parsed rows are
    problems HERE, where the self-test reaches them; they were once decided only in main() (review #27b)."""
    rows, problems = index_rows(index_text)
    if not rows:
        problems.append("no index rows parsed: no table has exactly the index header, or it has no body rows")
    if registry_text is None:
        problems.append(f"{REGISTRY} does not exist")
    reg, rp = read_registry(registry_text if registry_text is not None else "")
    problems += rp
    open_ids, seen = set(), {}
    for id_src, status_src, line, stok, sev, updated in rows:
        m = ID_RE.match(id_src)
        if not m:
            problems.append(f"line {line}: id {id_src.strip()[:20]!r} is not plain letters and digits")
            continue
        rid = m.group(1)
        seen.setdefault(rid, []).append(line)
        # two problems, and the row still read: one message for both, and a `continue`, once called a six-cell row
        # "not six cells" and its OPEN status "not OPEN" (review #40b)
        if sev.upper() not in SEVERITIES:
            problems.append(f"line {line}: id {rid}: severity {sev[:30]!r} is not one of {', '.join(SEVERITIES)}")
        if not updated:
            problems.append(f"line {line}: id {rid}: the updated cell is empty; a row missing a cell shifts its status")
        s = STATUS_RE.match(status_src)
        if not s or s.group("w").upper() not in STATUSES:
            problems.append(f"line {line}: id {rid}: status {status_src.strip()[:40]!r} does not begin with a plain "
                            f"status word ({', '.join(STATUSES)})")
            continue
        shown, w = _shown(stok).lstrip(), s.group("w")     # invisibles: DROPPED by fold() below (⚠ once "refused"; #44a)
        rest = shown[len(w):] if shown[:len(w)].upper() == w.upper() else shown
        rest = fold(rest)
        odd = sorted({c for c in _shown(stok) if not status_char_ok(c)})
        if s.group("w").upper() != "OPEN" and odd:
            problems.append(f"line {line}: id {rid}: status {status_src.strip()[:40]!r} shows characters the index does "
                            f"not use in a status ({', '.join(f'U+{ord(c):04X}' for c in odd[:4])}); write it in plain text")
            continue
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
        n = len([e for e in reg.get(rid, []) if e[0] in KINDS and INVISIBLE.sub("", e[1]).strip()])
        if n != 1:
            problems.append(f"id {rid}: OPEN with {n} registry line(s) in {REGISTRY}, not 1"
                            + (" (UNOWNED)" if n == 0 else ""))
    for rid, entries in sorted(reg.items()):
        if rid not in open_ids:
            where = "is not an id in the index" if rid not in seen else "is not OPEN"
            problems.append(f"{REGISTRY}:{entries[0][2]}: id {rid!r} {where}, but has a registry line")   # !r: a BOM shows (#26b)
    return problems, len(rows), len(open_ids)


def read_file(path, required):
    """(text, None); (None, None) if an optional file does not exist, not even as a symlink (a dangling symlink is
    unreadable, not absent; review #35a); or (None, reason) if it cannot be read as UTF-8.
    main() once let a non-UTF-8 or directory path raise, exiting 1 -- a refusal -- instead of 2 (review #34b)."""
    if not required and not os.path.lexists(path):
        return None, None
    try:
        with open(path, encoding="utf-8") as f:
            return f.read(), None
    except (OSError, UnicodeDecodeError) as e:
        return None, f"{path}: {e}"


MODES = {(): "live", ("--self-test",): "self-test", ("--mutations",): "mutations"}


def mode(argv):
    """The mode an argument list asks for, or None: an unknown or extra argument once ran the live check (#35b)."""
    return MODES.get(tuple(argv))


def clean_env(**extra):
    """This environment without any GIT_* variable except GIT_CEILING_DIRECTORIES. An exported GIT_DIR made the
    self-test's `git init` re-initialise the CALLER's repository -- from a linked worktree it set the shared config
    to bare -- and GIT_WORK_TREE redirected the live check away from the current directory (review #37b)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") or k == "GIT_CEILING_DIRECTORIES"}
    env.update(extra)
    return env


def toplevel():
    """(the work tree holding the current directory, None) or (None, why not). A missing `git` once raised, exit 1."""
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, env=clean_env())
    except OSError as e:
        return None, f"git cannot run: {e}"
    root = r.stdout.strip()
    return (root, None) if root else (None, "not inside a git work tree")


def git_init(path):
    """True if `git init` ran. A missing git raised here and crashed the self-test, exit 1 (review #38a)."""
    try:
        return subprocess.run(["git", "init", "-q"], cwd=path, capture_output=True, env=clean_env()).returncode == 0
    except OSError:
        return False


def run(root):
    """(exit status, lines) for the work tree at `root`: main()'s reading and verdict, above the mutation marker so
    that the self-test reaches them. main() once read the files itself, unpinned (review #35b)."""
    index, e1 = read_file(os.path.join(root, "KNOWN_ISSUES.md"), True)
    registry, e2 = read_file(os.path.join(root, REGISTRY), False)
    for e in (e1, e2):
        if e:
            return 2, [f"[owned] CANNOT LOOK :: {e}"]
    return decide(index, registry)


def decide(index_text, registry_text):
    """(exit status, lines to print) -- the whole verdict, above the mutation marker so that the self-test and
    `--mutations` reach it. main() once decided the exit status itself, unpinned (review #29b)."""
    problems, n_rows, n_open = check(index_text, registry_text)
    if not n_rows:     # the problems found on the way are printed too; they were once dropped (review #39b)
        return 2, [f"  {p}" for p in problems] + ["[owned] CANNOT LOOK :: no issue rows parsed"]
    out = [f"  {p}" for p in problems]
    out.append(f"\n[owned] {'FAIL' if problems else 'PASS'} :: {n_rows} rows, {n_open} OPEN, {len(problems)} problem(s)")
    return (1 if problems else 0), out


def self_test():
    head = "| id | severity | status | one-sentence failure | detail | updated |\n|---|---|---|---|---|---|\n"
    shapes = [  # (name, index rows, registry, problems wanted)
        ("OPEN row with one registry line", "| 1 | LOW | OPEN | x | d | u |\n", "1\tOWNER\tlane B\n", 0),
        ("OPEN row with no registry line", "| 1 | LOW | OPEN | x | d | u |\n", "", 1),
        ("OPEN row with two registry lines", "| 1 | LOW | OPEN | x | d | u |\n", "1\tOWNER\ta\n1\tD7\tb\n", 1),
        ("a registry line for a FIXED row", "| 1 | LOW | FIXED | x | d | u |\n", "1\tOWNER\ta\n", 1),
        ("a registry line for an id not in the index", "| 1 | LOW | FIXED | x | d | u |\n", "9\tOWNER\ta\n", 1),
        ("an unknown kind: malformed, and the row stays unowned", "| 1 | LOW | OPEN | x | d | u |\n", "1\tMAYBE\ta\n", 2),
        ("empty blocker text: malformed, and the row stays unowned", "| 1 | LOW | OPEN | x | d | u |\n", "1\tOWNER\t \n", 2),
        ("two fields, not three", "| 1 | LOW | OPEN | x | d | u |\n", "1\tOWNER lane B\n", 2),
        ("comments and blank lines are ignored", "| 1 | LOW | OPEN | x | d | u |\n", "# c\n\n1\tJOSEPH\tt\n", 0),
        ("status in bold with a qualifier", "| 1 | LOW | **OPEN — DO NOT FIX** | x | d | u |\n", "1\tD7\tt\n", 0),
        ("status FIXED: with a colon, in bold", "| 1 | LOW | **FIXED:** 2026 at `abc` | x | d | u |\n", "", 0),
        ("lowercase open still needs a line", "| 1 | LOW | open | x | d | u |\n", "", 1),
        ("status struck with ~~ is refused, not read", "| 1 | LOW | ~~OPEN~~ FIXED | x | d | u |\n", "", 1),
        ("status in <del> is refused", "| 1 | LOW | <del>FIXED</del> OPEN | x | d | u |\n", "", 1),
        ("status in a code span is refused", "| 1 | LOW | `FIXED` | x | d | u |\n", "", 1),
        ("status word unknown", "| 1 | LOW | PENDING | x | d | u |\n", "", 1),
        ("REOPENED is not OPEN", "| 1 | LOW | REOPENED | x | d | u |\n", "", 1),
        # counts that DIFFER under the mutation each pins (a count equal either way pins nothing)
        ("OPENED is not OPEN, and its registry line is stray", "| 1 | LOW | OPENED | x | d | u |\n", "1\tOWNER\ta\n", 2),
        ("lowercase open with its registry line", "| 1 | LOW | open | x | d | u |\n", "1\tOWNER\ta\n", 0),
        ("four fields, not three", "| 1 | LOW | OPEN | x | d | u |\n", "1\tOWNER\ta\tb\n", 2),
        ("a bold id is the same id", "| 1 | LOW | FIXED | x | d | u |\n| **1** | LOW | FIXED | y | d | u |\n", "", 1),
        ("an id with markup is refused", "| <span>1</span> | LOW | FIXED | x | d | u |\n", "", 1),
        ("an OPEN row in a SECOND table is checked",
         "| 1 | LOW | FIXED | x | d | u |\n\n## R\n\n" + head + "| 2 | LOW | OPEN | x | d | u |\n", "", 1),
        ("any non-index table is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\n| name | a | status |\n|---|---|---|\n| z | LOW | OPEN |\n", "", 1),
        # --- review #28b
        ("a near-index table headed Issue is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\n| Issue | severity | status | one-sentence failure | detail | updated |\n|---|---|---|---|---|---|\n| 74 | LOW | OPEN | x | d | u |\n", "", 1),
        ("a raw-HTML table is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\n<table><tr><td>74</td><td>OPEN</td></tr></table>\n", "", 1),
        ("status FIXED-pending is refused", "| 1 | LOW | FIXED-pending; OPEN | x | d | u |\n", "", 1),
        ("status Fixed? is refused", "| 1 | LOW | **Fixed?** No \u2014 still OPEN | x | d | u |\n", "", 1),
        ("status **FIXED**-pending is refused", "| 1 | LOW | **FIXED**-pending review; OPEN | x | d | u |\n", "", 1),
        ("status FIXED_pending is refused", "| 1 | LOW | FIXED_pending_ OPEN | x | d | u |\n", "", 1),
        # --- review #30b: the HTML rule's inline, upper-case and nested forms, and what it must NOT refuse
        ("an inline raw-HTML table in a paragraph is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\nSee: <table><tr><td>74</td><td>OPEN</td></tr></table>\n", "", 1),
        ("an upper-case raw-HTML table is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\n<TABLE><TR><TD>74</TD><TD>OPEN</TD></TR></TABLE>\n", "", 1),
        ("a raw-HTML table nested in a div is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\n<div>\n<table><tr><td>74</td></tr></table>\n</div>\n", "", 1),
        ("<td> in a code span is prose, not a table", "| 1 | LOW | FIXED | x | d | u |\n\nThe parser drops `<td>` cells.\n", "", 0),
        ("<td> in an HTML comment renders nothing", "| 1 | LOW | FIXED | x | d | u |\n\n<!-- <td> -->\n", "", 0),
        # --- review #32b: the open rule's case, substring and status coverage; what it reads; HTML in an index cell
        ("a FIXED status saying (reopened …) is refused", "| 1 | LOW | FIXED 2026-09-24 (reopened 2026-09-25) | x | d | u |\n", "", 1),
        ("a FIXED status saying residual OPEN is refused", "| 1 | LOW | FIXED \u2014 residual OPEN | x | d | u |\n", "", 1),
        *[(f"a {w} status saying still open is refused", f"| 1 | LOW | **{w} 2026-09-23** \u2014 two literals still open | x | d | u |\n", "", 1)
          for w in ("RESOLVED", "CLOSED", "WONTFIX", "RETRACTED")],
        ("a link TARGET naming OPEN is not read", "| 1 | LOW | FIXED (ruled at [OI-134](docs/OPEN_ITEMS.md)) | x | d | u |\n", "", 0),
        ("open() in a code span is refused (fail closed)", "| 1 | LOW | FIXED; `open()` now closes | x | d | u |\n", "", 1),
        *[(f"open hidden in the source ({s!r}) is refused", f"| 1 | LOW | FIXED; still {s} | x | d | u |\n", "", 1)
          for s in ("&#111;pen", "o*pe*n", "op<span></span>en", "op\u00aden", "op\u200ben")],
        ("raw-HTML table markup in an index cell is refused", "| 1 | LOW | FIXED | x | <table><tr><td>2</td></tr></table> | u |\n", "", 1),
        # --- review #34b: struck statuses, blank registry lines, default-ignorables and alt text, <thead>, a Unicode id
        ("a struck FIXED is refused", "| 1 | LOW | ~~FIXED 2026-09-01~~ still broken | x | d | u |\n", "", 1),
        ("a struck OPEN before FIXED is refused, and its registry line is stray", "| 1 | LOW | ~~OPEN 2026~~ FIXED | x | d | u |\n", "1\tOWNER\ta\n", 2),
        ("blocker text of only invisible characters is empty", "| 1 | LOW | OPEN | x | d | u |\n", "1\tOWNER\t\u200b\u2060\n", 2),
        ("a whitespace-only registry line is blank", "| 1 | LOW | OPEN | x | d | u |\n", "1\tOWNER\ta\n   \n", 0),
        *[(f"open hidden by U+{ord(c):04X} is refused", f"| 1 | LOW | FIXED; still op{c}en | x | d | u |\n", "", 1)
          for c in "\ufe0f\U000e0100\u3164\u115f\U000e0001"],
        ("image alt text saying open is refused", "| 1 | LOW | FIXED ![still open](x.png) | x | d | u |\n", "", 1),
        ("a stray <thead><th> is refused", "| 1 | LOW | FIXED | x | d | u |\n\n<thead><th>x</th></thead>\n", "", 1),
        ("a stray <tbody> is refused", "| 1 | LOW | FIXED | x | d | u |\n\n<tbody>\n", "", 1),
        ("a Unicode-letter id is refused", "| \u00e91 | LOW | FIXED | x | d | u |\n", "", 1),
        # --- review #33b: every invisible format character, not a list of six
        *[(f"open hidden by U+{ord(c):04X} is refused", f"| 1 | LOW | FIXED; still op{c}en | x | d | u |\n", "", 1)
          for c in "\u200c\u200d\u2060\ufeff\u200e\u200f\u2061\u034f"],
        *[(f"a row cut off after a U+{ord(c):04X} lead is refused", f"| 1 | LOW | FIXED | x | d | u |\n\n{c}| 2 | LOW | OPEN | x | d | u |\n", "", 1)
          for c in "\u200e\u200f"],
        ("a row cut off after a zero-width lead is refused", "| 1 | LOW | FIXED | x | d | u |\n\n\u200b| 2 | LOW | OPEN | x | d | u |\n", "", 1),
        # --- review #31b: a closed status that also says open; underscores that are not markup; the comment forms
        #     HTML5 closes early; the inputs that each surviving weakening broke. Review #31a: <td> in a fenced block
        ("a FIXED status saying two literals are still open is refused",
         "| 1 | LOW | **FIXED 2026-08-19** at `abc`; two literals still open, see the end | x | d | u |\n", "", 1),
        ("a FIXED status saying reopened is refused", "| 1 | LOW | FIXED (reopened \u2014 OPEN) | x | d | u |\n", "", 1),
        *[(f"status {s!r} is refused", f"| 1 | LOW | {s} | x | d | u |\n", "", 1) for s in ("FIXED__ x", "**FIXED__** x", "FIXED_ x")],
        *[(f"status {s!r} is read as FIXED", f"| 1 | LOW | {s} x | x | d | u |\n", "", 0)
          for s in ("**FIXED*", "*FIXED**", "***FIXED***", "_FIXED_", "**FIXED:**")],
        ("a raw-HTML table between two comments is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\n<!-- a --> <table><tr><td>2</td><td>OPEN</td></tr></table> <!-- b -->\n", "", 1),
        *[(f"a comment HTML5 ends early ({c!r}) does not hide a table", f"| 1 | LOW | FIXED | x | d | u |\n\n{c} <table><tr><td>2</td></tr></table> -->\n", "", 1)
          for c in ("<!-->", "<!--->", "<!-- a --!>")],
        ("a multi-line comment holding <td> renders nothing", "| 1 | LOW | FIXED | x | d | u |\n\n<!-- a\n<td> -->\n", "", 0),
        ("<track> is not table markup", "| 1 | LOW | FIXED | x | d | u |\n\n<video><track src=x></video>\n", "", 0),
        ("a stray <tr><td> is refused", "| 1 | LOW | FIXED | x | d | u |\n\n<tr><td>2</td></tr>\n", "", 1),
        ("a stray </table> is refused", "| 1 | LOW | FIXED | x | d | u |\n\n</table>\n", "", 1),
        ("<td> in a fenced code block is code, not a table", "| 1 | LOW | FIXED | x | d | u |\n\n```html\n<td>x</td>\n```\n", "", 0),
        ("an indented row directly under the table is refused",
         "| 1 | LOW | FIXED | x | d | u |\n    | 2 | LOW | OPEN | x | d | u |\n", "", 1),
        ("a bold OPEN id with its registry line", "| **1** | LOW | OPEN | x | d | u |\n", "1\tOWNER\ta\n", 0),
        ("a lower-case kind is refused, and the row stays unowned", "| 1 | LOW | OPEN | x | d | u |\n", "1\towner\ta\n", 2),
        ("a registry id in the wrong case owns nothing", "| J36 | LOW | OPEN | x | d | u |\n", "j36\tOWNER\ta\n", 2),
        ("a registry with two BOMs owns nothing", "| 1 | LOW | OPEN | x | d | u |\n", "\ufeff\ufeff1\tOWNER\ta\n", 2),
        # --- review #36b: boundaries pinned WITHOUT an `open` that the open rule would refuse anyway; a tab lead; lone CRs
        *[(f"status {s!r} is refused", f"| 1 | LOW | {s} | x | d | u |\n", "", 1)
          for s in ("FIXED-pending review", "FIXED?", "**FIXED**-x", "FIXED/pending", "FIXED' x", "FIXED!")],
        # --- review #39b: a row missing a cell; an index table with no body rows
        # --- review #40b: each severity pinned; a qualified severity is one problem and the row still counts; extra cells
        *[(f"severity {w} is accepted", f"| 1 | {w} | FIXED | x | d | u |\n", "", 0)
          for w in ("CRITICAL", "BLOCKER", "HIGH", "MEDIUM", "LOW", "TRAP", "**HIGH**", "High")],
        ("a qualified severity is one problem, and its OPEN row is still owned", "| 1 | HIGH (was MEDIUM) | OPEN | x | d | u |\n", "1\tOWNER\ta\n", 1),
        ("an escaped pipe in a code span stays in its cell", "| 1 | LOW | **FIXED** at `a \\| b` fine | x | d | u |\n", "", 0),
        ("more cells than the header is refused", "| 1 | LOW | **FIXED** at `abc` \u2014 `a | b` still open | x | d | u |\n", "", 1),
        # --- review #42b: look-alike letters; a code-span pipe with a missing cell; NBSP and em-space leads
        *[(f"open in look-alike letters ({s!r}) is refused", f"| 1 | LOW | FIXED; still {s} | x | d | u |\n", "", 1)
          for s in ("\uff4f\uff50\uff45\uff4e", "\u043epen", "&#65359;pen", "OPE\u039d")],
        # the extra-cells rule and the trailing-pipe regex, each pinned WITHOUT a code span, which the code-span rule
        # would refuse first (self-found, 2026-09-24)
        ("a plain pipe in a status is more cells, refused", "| 1 | LOW | FIXED a | b still open | x | d | u |\n", "", 1),
        ("a plain split ending in an escaped pipe is refused", "| 1 | LOW | FIXED a|b | x | d | u \\|\n", "", 1),
        ("a lone row in a list item is refused", "| 1 | LOW | FIXED | x | d | u |\n\n- | 2 | LOW | OPEN | x | d | u |\n", "", 1),
        ("a code-span pipe in a row missing a cell is refused", "| 1 | LOW | FIXED at `a|b` still open | d | 2026 |\n", "", 1),
        # --- review #43b: characters outside the status set; a cut-short status; prose behind a marker; alt emphasis
        *[(f"a closed status showing {s!r} is refused", f"| 1 | LOW | FIXED; still {s} | x | d | u |\n", "", 1)
          for s in ("ope\u0303n", "open\u0303", "\u1d0f\u1d18\u1d07\u0274", "\u0585pe\u0578", "op\u04bdn")],
        # --- review #44b: ordinary physics and names are accepted; look-alikes are READ; runs, targets, the rest
        *[(f"a closed status showing {s!r} is accepted", f"| 1 | LOW | FIXED {s} | x | d | u |\n", "", 0)
          for s in ("\u2014 \u03c7\u00b2/ndf now 1.1", "\u0394 = 0.3%", "5 \u00b5s", "\u03bd_\u03bc", "in [0, 1.5)", "in (0.5, 2]",
                    "a\tb", "man\u0153uvre", "L\u00f8v\u00e5s", "\u0303", "5\u00a02026", "at ``a`b``")],
        *[(f"open spelt {s!r} is read as open", f"| 1 | LOW | FIXED; still {s} | x | d | u |\n", "", 1)
          for s in ("\u00f8pen", "op\u01ddn", "o\u01a5en", "ope\u0272", "o\u03c1en", "op\u03b5n", "ope\u03b7")],
        ("a double-backtick pipe in a row missing a cell is refused", "| 1 | LOW | FIXED at ``a|b`` still open | d | 2026 |\n", "", 1),
        ("a link-target pipe in a row missing a cell is refused", "| 1 | LOW | FIXED at [OI-1](docs/a|b.md) still open | d | 2026 |\n", "", 1),
        ("an escaped backtick is not a run", "| 1 | LOW | FIXED; the \\` key | x | d | u |\n", "", 0),
        ("a numbered-list line holding a lone row is refused", "| 1 | LOW | FIXED | x | d | u |\n\n1. | 2 | LOW | OPEN | x | d | u |\n", "", 1),
        ("three pipes behind a marker make a row line", "| 1 | LOW | FIXED | x | d | u |\n\n- |a| and |b\n", "", 1),
        ("a Braille blank inside open is dropped, and open is seen", "| 1 | LOW | FIXED; still op\u2800en | x | d | u |\n", "", 1),
        ("a variation selector inside open is dropped, and open is seen", "| 1 | LOW | FIXED; still op\ufe0fen | x | d | u |\n", "", 1),
        # --- review #45b: a backslash inside a code span is literal; omicron; enclosing marks; circled letters
        *[(f"a code span holding a backslash, {s!r}, is closed", f"| 1 | LOW | FIXED; the {s} was dropped | x | d | u |\n", "", 0)
          for s in ("trailing `\\` launcher", "stray `\\\\` note")],
        ("a status cut after a backslash code span is refused", "| 1 | LOW | FIXED at `a\\` then `b|c` still open | d | 2026 |\n", "", 1),
        ("Greek omicron standing for o is read as open", "| 1 | LOW | FIXED; still \u03bfpen | x | d | u |\n", "", 1),
        ("an enclosing keycap mark is accepted", "| 1 | LOW | FIXED 1\ufe0f\u20e3 done | x | d | u |\n", "", 0),
        ("an enclosing circle inside open is dropped, and open is seen", "| 1 | LOW | FIXED; still op\u20dden | x | d | u |\n", "", 1),
        ("circled letters are read as open", "| 1 | LOW | FIXED; still \u24de\u24df\u24d4\u24dd | x | d | u |\n", "", 1),
        # --- review #46b: the parser decides what a pipe cut; `ŉ`; the coverage gaps
        *[(f"a status cut by a pipe in {k} is refused", f"| 1 | LOW | FIXED {s} still open | d | 2026 |\n", "", 1)
          for k, s in (("a span after an escaped backslash", "at C:\\\\`a|b`"), ("a span after an HTML tag", '<span title="`">x</span> `a|b`'),
                       ("a span after an autolink", "<https://x.org/`> `a|b`"), ("a link target with parentheses", "[w](https://e.org/U_(s)|x)"),
                       ("an angle-bracket link target", "[a](<f)g|h>)"), ("link text", "[a|b](x)"))],
        ("a status cut by a pipe inside an HTML tag is refused", '| 1 | LOW | FIXED <span title="a|b">x</span> still open | d | 2026 |\n', "", 1),
        ("a pipe span in a LATER cell fails closed", "| 1 | LOW | FIXED | x `a|b` y | u |\n", "", 1),
        ("a lone backtick in the status pairing with a later cell's fails closed", "| 1 | LOW | FIXED; don`t | x | see `y` | u |\n", "", 1),
        # --- review #47b: a LATER cell's backtick must not hide a cut; percent-encoded targets; reference links; images
        *[(f"a cut status with {k} in a later cell is refused", f"| 1 | LOW | FIXED at `a|b` still open | {c} | 2026 |\n", "", 1)
          for k, c in (("a code span", "see `x`"), ("a lone backtick", "don`t"), ("two spans", "`x` and `y`"))],
        ("an encoded pipe in a status link target fails closed", "| 1 | LOW | FIXED, see [q](https://e.org/?q=a%7Cb) | x | d | u |\n", "", 1),
        ("a cut image alt is refused", "| 1 | LOW | FIXED ![a|b](x.png) still open | d | 2026 |\n", "", 1),
        ("a cut image target is refused", "| 1 | LOW | FIXED ![a](x|y.png) still open | d | 2026 |\n", "", 1),
        ("a cut status in a row without a leading pipe is refused", "1 | LOW | FIXED at `a|b` still open | d | 2026\n", "", 1),
        ("an escaped pipe before the status is not a cell boundary", "| 1 | LOW | FIXED a\\|b at `c|d` still open | x | 2026 |\n", "", 1),
        # --- review #48b: a defined reference cannot hide a cut target; titles; the pinned pieces #48b found unpinned
        ("a cut link target is refused even when the reference is defined", "| 1 | LOW | FIXED, see [r](docs/a|b.md) still open | d | 2026 |\n\n[r]: docs/o.md\n", "", 1),
        ("a cut link title is refused", '| 1 | LOW | FIXED, see [n](docs/n.md "s 2 | 3") still open | d | 2026 |\n', "", 1),
        ("a cut image title is refused", '| 1 | LOW | FIXED ![n](x.png "s 2 | 3") still open | d | 2026 |\n', "", 1),
        ("an escaped pipe in a later code span is fine", "| 1 | LOW | FIXED x < 1 | f | `a \\| b` | u |\n", "", 0),
        ("a closed link before a less-than sign, with a later %7C link, fails closed", "| 1 | LOW | FIXED [a](b) x < 1 | f | see [q](x%7Cy) | u |\n", "", 1),
        ("a later %7C link fails closed whatever the status", "| 1 | LOW | FIXED at `x<y` | f | [q](x%7Cy) | u |\n", "", 1),
        # --- review #48a: a `<` or `[` in prose with a link in a LATER cell is not a cut
        *[(f"a status with {k} and a later link holding %7C fails closed", f"| 1 | LOW | FIXED; {s} | x | see [q](https://e.org/?q=a%7Cb) | u |\n", "", 1)
          for k, s in (("a less-than sign", "residual < 1%"), ("a bracketed tag", "[VL12]"), ("an interval", "in [0, 1.5)"))],
        ("a status with a less-than sign and a later autolink holding %7C fails closed", "| 1 | LOW | FIXED; residual < 1% | x | <https://e.org/?q=a%7Cb> | u |\n", "", 1),
        # --- review #49b: the count-tie cuts, a pipe in a reference label, a definition holding a pipe
        ("a cut through a link target holding a span is refused", "| 1 | LOW | FIXED [a](x|`y) still open | d `| 2026 |\n", "", 1),
        *[(f"a cut through {k} is refused", f"| 1 | LOW | FIXED {s} still open | 2026 |\n", "", 1)
          for k, s in (("an HTML attribute holding a span", '<span title="a | `b|c` d">x</span>'),
                       ("a link title holding a span", '[n](x "a | `b|c`")'), ("an image alt holding a span", "![a | `b|c` d](x.png)"))],
        ("a pipe in a reference label is refused", "| 1 | LOW | FIXED [a][r|s] still open | d | 2026 |\n\n[r|s]: http://x\n", "", 1),
        ("a status citing a definition that holds a pipe fails closed", '| 1 | LOW | FIXED, see [VL12] | x | d | u |\n\n[VL12]: V.md "VL12 | 2D"\n', "", 1),
        ("a cut reference link is refused", "| 1 | LOW | FIXED [a|b][r] still open | d | 2026 |\n\n[r]: http://x\n", "", 1),
        ("a two-cell row is refused, not a crash", "| 1 | LOW\n", "", 2),
        ("a code span holding `](` fails closed", "| 1 | LOW | FIXED; the parser splits on `](` now | x | d | u |\n", "", 1),
        ("a cut link target under a defined reference is refused", "| 1 | LOW | FIXED [a](|[a]( | x | u |\n\n[a]: http://x\n", "", 1),
        ("a closed span after an escaped backslash is fine", "| 1 | LOW | FIXED; path ends C:\\\\`x` fine | x | d | u |\n", "", 0),
        ("n after an apostrophe still says open", "| 1 | LOW | FIXED; still ope\u0149 | x | d | u |\n", "", 1),
        ("a ten-item list line holding a lone row is refused", "| 1 | LOW | FIXED | x | d | u |\n\n10. | 2 | LOW | OPEN | x | d | u |\n", "", 1),
        ("a dash without a space is not a list marker, so the line is prose", "| 1 | LOW | FIXED | x | d | u |\n\n-|a| b |c\n", "", 0),
        ("escaped pipes behind a marker are not a row's", "| 1 | LOW | FIXED | x | d | u |\n\n- |x\\| and \\|y\n", "", 0),
        ("an unmapped letter inside a word is not refused", "| 1 | LOW | FIXED; op\u0394en | x | d | u |\n", "", 0),
        ("sigma standing for o is read as open", "| 1 | LOW | FIXED; still \u03c3pen | x | d | u |\n", "", 1),
        # --- self-found: ordinary typography is accepted; letters reducing to ASCII are read as ASCII
        *[(f"a closed status showing {s!r} is accepted", f"| 1 | LOW | FIXED {s} | x | d | u |\n", "", 0)
          for s in ("\u2192 see ISSUE-75", "\u201cas designed\u201d", "\u2265 3 runs", "at caf\u00e9", "\u2018q\u2019", "\u2260 bug", "\u00b2", "1\u00bd h",
                    "Stra\u00dfe", "\u00e6ther", "\u0141\u00f3d\u017a", "nai\u0308ve")],
        *[(f"a closed status showing the look-alike {s!r} is refused", f"| 1 | LOW | FIXED {s}pen | x | d | u |\n", "", 1)
          for s in ("\u00f8", "\u0254", "\u0275")],
        ("open with a combining mark still says open", "| 1 | LOW | FIXED; still o\u0305pen | x | d | u |\n", "", 1),
        ("ope + eng is refused", "| 1 | LOW | FIXED; still ope\u014b | x | d | u |\n", "", 1),
        *[(f"open written {s!r} is still read as open", f"| 1 | LOW | FIXED; still {s} | x | d | u |\n", "", 1)
          for s in ("op\u00e9n", "\uff4f\uff50\uff45\uff4e", "\u1d52pen")],
        ("the historical status characters are accepted", "| 1 | LOW | FIXED \u2014 \u2026 \u2013 \u00b1 \u2225 \u2212 \u00b7 \u03bb \u03c3 \u00d7 \u2248 \u2264 | x | d | u |\n", "", 0),
        ("image alt with emphasis saying open is refused", "| 1 | LOW | FIXED ![still op*e*n](x.png) | x | d | u |\n", "", 1),
        ("an unclosed fence named in a detail cell is fine", "| 1 | LOW | FIXED | an unclosed ``` fence | see `a` | u |\n", "", 0),
        *[(f"a prose line {s!r} behind a marker is not a row", f"| 1 | LOW | FIXED | x | d | u |\n\n{s}\n", "", 0)
          for s in ("- |\u0394\u03c3| < 1% in every bin", "> |x| is abs", "* |x| is abs", "1. | a")],
        *[(f"a row cut off after a U+{ord(c):04X} lead is refused", f"| 1 | LOW | FIXED | x | d | u |\n\n{c}| 2 | LOW | OPEN | x | d | u |\n", "", 1)
          for c in "\u00a0\u2003"],
        # --- review #41b: the pipe count's edges; the updated rule still reads the row; CRLF through check()
        ("a split cell ending in an escaped pipe is refused", "| 1 | LOW | FIXED `a|b` | x | d | u \\|\n", "", 1),
        ("trailing spaces after a row are not a cell", "| 1 | LOW | FIXED | x | d | u |   \n", "", 0),
        ("an empty updated is one problem, and its OPEN row is still read", "| 1 | LOW | OPEN | x | d | |\n", "", 2),
        ("an updated cell of only a tag is empty", "| 1 | LOW | FIXED | x | d | <br> |\n", "", 1),
        ("a row missing its severity cell is refused, twice", "| 74 | OPEN | Fixed seeds are not reset | d | 2026-09-24 |\n", "", 2),
        ("an unknown severity is refused", "| 1 | SEVERE | FIXED | x | d | u |\n", "", 1),
        ("an empty updated cell is refused", "| 1 | LOW | FIXED | x | d | |\n", "", 1),
        ("a row cut off after a non-BMP invisible lead is refused", "| 1 | LOW | FIXED | x | d | u |\n\n\U000e0001| 2 | LOW | OPEN | x | d | u |\n", "", 1),
        ("a row cut off after a Braille-blank lead is refused", "| 1 | LOW | FIXED | x | d | u |\n\n\u2800| 2 | LOW | OPEN | x | d | u |\n", "", 1),
        ("a row cut off after a tab lead is refused", "| 1 | LOW | FIXED | x | d | u |\n\n\t| 2 | LOW | OPEN | x | d | u |\n", "", 1),
        ("lone CRs in a table do not hide a cut-off OPEN row",
         "| 1 | LOW | FIXED | x | d | u |\r| 3 | LOW | FIXED | y | d | u |\r| 4 | LOW | FIXED | z | d | u |\n\n| 99 | LOW | OPEN | x | d | u |\n", "", 1),
        # --- review #30b: each status boundary the real index uses, pinned
        *[(f"status boundary {s!r}", f"| 1 | LOW | {s} x | x | d | u |\n", "", 0)
          for s in ("**FIXED**", "__FIXED__", "FIXED.", "FIXED,", "FIXED;", "FIXED)", "FIXED\u2014pending", "FIXED\u2013pending")],
        ("a stray row plus a delimiter is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\n| 74 | LOW | OPEN | x | d | u |\n|---|---|---|---|---|---|\n", "", 1),
        ("a header beginning `id` but not `id` is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\n| id (x) | a | status |\n|---|---|---|\n| 2 | LOW | OPEN |\n", "", 1),
        # --- review #27b: index tables are recognised by their exact rendered header
        ("a bold **id** header is the index header", "", "", 1 - 1),
        ("a code `id` header is the index header", "", "", 0),
        ("a header with a doubled space is the index header", "", "", 0),
        ("a two-column id | status table is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\n| id | status |\n|---|---|\n| 74 | OPEN |\n", "", 1),
        ("a three-column id table is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\n| id | severity | status |\n|---|---|---|\n| 74 | LOW | OPEN |\n", "", 1),
        ("a header ID. is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\n| ID. | severity | status | one-sentence failure | detail | updated |\n|---|---|---|---|---|---|\n| 74 | LOW | OPEN | x | d | u |\n", "", 1),
        ("a header whose third column is not status is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\n| id | status | failure |\n|---|---|---|\n| 74 | OPEN | Closed form |\n", "", 1),
        ("no index table at all", None, "", 1),
        ("the registry file absent", "| 1 | LOW | FIXED | x | d | u |\n", None, 1),
        ("an indented comment line in the registry", "| 1 | LOW | OPEN | x | d | u |\n", "  # c\n1\tOWNER\ta\n", 0),
        # --- review #24b: the real index's letter ids and status words, and rows the parser would not see
        ("a letter id J36, OPEN with its line", "| J36 | LOW | OPEN | x | d | u |\n", "J36\tOWNER\ta\n", 0),
        *[(f"status {w} needs no line", f"| 1 | LOW | {w} 2026 | x | d | u |\n", "", 0)
          for w in ("CLOSED", "RESOLVED", "WONTFIX", "RETRACTED")],
        ("an id with trailing text is refused", "| 51 (reopened) | LOW | FIXED | x | d | u |\n", "", 1),
        ("spaces around the registry id and kind are accepted", "| 1 | LOW | OPEN | x | d | u |\n", " 1 \t OWNER \ta\n", 0),
        ("an upper-case ID header is still an index", "", "", 0),
        ("a row cut off by a blank line is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\n| 2 | LOW | OPEN | x | d | u |\n", "", 1),
        ("a pipe-led line inside a fenced code block is refused (fail closed)",
         "| 1 | LOW | FIXED | x | d | u |\n\n```sh\ngrep x f \\\n  | sort\n```\n", "", 1),
        ("an unclosed fence does not hide an OPEN row after it",
         "| 1 | LOW | FIXED | x | d | u |\n\n```\n\n" + head + "| 2 | LOW | OPEN | x | d | u |\n", "", 3),
        ("a BOM before a data line", "| 1 | LOW | OPEN | x | d | u |\n", "\ufeff1\tOWNER\ta\n", 0),
        ("a registry beginning with a UTF-8 BOM", "| 1 | LOW | OPEN | x | d | u |\n", "\ufeff# c\n1\tOWNER\ta\n", 0),
        ("a row cut off by an indent is refused",
         "| 1 | LOW | FIXED | x | d | u |\n\n    | 2 | LOW | OPEN | x | d | u |\n", "", 1),
        ("CRLF registry lines", "| 1 | LOW | OPEN | x | d | u |\n", "1\tOWNER\ta\r\n", 0),
    ]
    wrong = []
    # the exit status itself, through decide()
    one = head + "| 1 | LOW | OPEN | x | d | u |\n"
    fixed = head + "| 1 | LOW | FIXED | x | d | u |\n"
    exits = (("exit 0 when every OPEN row is owned", one, "1\tOWNER\ta\n", 0),
             ("exit 1 when an OPEN row is unowned", one, "", 1),
             ("exit 1 when the registry is absent", one, None, 1),
             ("exit 2 when no index table exists", "# none\n", "", 2),
             # --- review #34b: the live index has NO OPEN row, and no exit check had one without
             ("exit 0 when no row is OPEN", fixed, "", 0),
             ("exit 1 when an all-FIXED index hides a cut-off OPEN row", fixed + "\n| 2 | LOW | OPEN | x | d | u |\n", "", 1),
             ("exit 1 when an all-FIXED index has no registry", fixed, None, 1),
             ("exit 0 with a BOM before the first table line", "\ufeff" + one, "1\tOWNER\ta\n", 0))
    for name, doc, reg, want in exits:
        rc, _ = decide(doc, reg)
        if rc != want:
            wrong.append(f"{name}: wanted exit {want}, got {rc}")
    # the span helpers themselves, where a row-level shape cannot reach them (review #48b)
    for got, want, name in ((pipe_spans("`a \\| b`"), 0, "an escaped pipe in a code span is not a pipe span"),
                            (pipe_spans("[a](b) and `c`"), 0, "a closed link and a code span without pipes are none"),
                            (status_cut("| 1 | LOW | FIXED x < 1 and [0, 1.5) | f | d | u |"), False, "prose < and [ are no span"),
                            (status_cut("| 1 | LOW | FIXED [a][r|s] still open | d | 2026 |"), True, "a pipe in a reference label is refused")):
        if got != want:
            wrong.append(f"{name}: wanted {want!r}, got {got!r}")
    # lone CRs: the cut-off OPEN row must be reported AS a cut-off row. Unnormalised, the CR-joined line also trips the
    # extra-cells rule, so a problem COUNT stayed equal and pinned nothing (self-found, 2026-09-24)
    if not any("99" in x and "not part of any parsed table" in x for x in check(head + "| 1 | LOW | FIXED | x | d | u |\r"
               "| 3 | LOW | FIXED | y | d | u |\r| 4 | LOW | FIXED | z | d | u |\n\n| 99 | LOW | OPEN | x | d | u |\n", "")[0]):
        wrong.append("lone CRs: the cut-off OPEN row 99 is not reported as a row outside every table")
    # a quoted index table is read, not refused for its `>` (review #41b); a CRLF index through check() (review #41b)
    # no backslash inside an f-string's braces: Python before 3.12 cannot parse it, and the probe once exited 1 there (#42a)
    OWNED = "1\tOWNER\ta\n"
    # the whole file compiles with warnings as ERRORS: an invalid `\\|` escape in two docstrings once warned, and a later
    # Python makes that an error (self-found, 2026-09-24)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        try:
            with open(__file__, encoding="utf-8") as f:
                compile(f.read(), __file__, "exec")
        except SyntaxError as e:
            wrong.append(f"line {e.lineno}: the probe does not compile with warnings as errors: {e.msg}")
    # the whole file, by Python's own tokenizer (reviews #43a, #44b)
    with open(__file__, encoding="utf-8") as f:
        for n in fstring_backslashes(f.read()):
            wrong.append(f"line {n}: a backslash inside an f-string's braces, which Python before 3.12 cannot parse")
    import tokenize as _tk
    if hasattr(_tk, "FSTRING_START") and fstring_backslashes("x = f\"{f'a\\nb'}\"\n") != [1]:
        wrong.append("a nested f-string with a backslash inside the outer braces is not found")
    body = (head + "| 1 | LOW | OPEN | x | d | u |").split("\n")
    for lead in ("> ", ">> ", "> > ", ">  > ", ">\t"):          # every quote form CommonMark allows (review #42b)
        quoted = "".join(lead + x + "\n" for x in body)
        if len(check(quoted, "1\tOWNER\ta\n")[0]) != 0:
            wrong.append(f"a quoted index table led {lead!r} with an owned row: wanted 0 problems, got {check(quoted, OWNED)[0]}")
    listed = "- " + body[0] + "\n" + "".join("  " + x + "\n" for x in body[1:])
    if len(check(listed, "1\tOWNER\ta\n")[0]) != 0:
        wrong.append(f"an index table in a list item with an owned row: wanted 0 problems, got {check(listed, OWNED)[0]}")
    cut = "".join("> " + x + "\n" for x in (head + "| 1 | LOW | FIXED | x | d | u |").split("\n")) + ">\n> | 2 | LOW | OPEN | x | d | u |\n"
    if not any("not part of any parsed table" in x for x in check(cut, "")[0]):
        wrong.append(f"a quoted index with a cut-off OPEN row: wanted it reported, got {check(cut, '')[0]}")
    crlf = (head + "| 1 | LOW | OPEN | x | d | u |\n").replace("\n", "\r\n")
    if check(crlf, "1\tOWNER\ta\n")[1:] != (1, 1):
        wrong.append(f"a CRLF index through check(): wanted 1 row, 1 OPEN, got {check(crlf, OWNED)[1:]}")
    # an index table with no body rows still exits 2, and prints what it found on the way (review #39b)
    rc, out = decide(head + "\n| 2 | LOW | OPEN | x | d | u |\n", "")
    if rc != 2 or not any("not part of any parsed table" in x for x in out):
        wrong.append(f"an index table with no body rows: wanted exit 2 listing the cut-off row, got {rc}: {out}")
    import tempfile
    with tempfile.TemporaryDirectory() as td:     # read_file: exit 2 cases must not be exceptions (review #34b)
        bad = os.path.join(td, "latin1.md")
        with open(bad, "wb") as f:
            f.write(b"| caf\xe9 |\n")
        good = os.path.join(td, "ok.md")
        with open(good, "w", encoding="utf-8") as f:
            f.write("x")
        reads = (("a non-UTF-8 file cannot be read", bad, True, "err"), ("a directory cannot be read", td, True, "err"),
                 ("an absent required file cannot be read", os.path.join(td, "no"), True, "err"),
                 ("an absent optional file is None", os.path.join(td, "no"), False, "none"),
                 ("a UTF-8 file is read", good, True, "text"))
        for name, path, req, want in reads:
            try:
                text, err = read_file(path, req)
                got = "err" if err else "none" if text is None else "text"
            except Exception as e:           # a raise is a wrong answer here, not a crash of the self-test
                got = f"raised {type(e).__name__}"
            if got != want:
                wrong.append(f"{name}: wanted {want}, got {got}")
        # run(): the exit status of a whole work tree, as main() reports it (review #35b)
        def tree(name, index=None, registry=None, dir_registry=False, dangling=False):
            root = os.path.join(td, name)
            os.makedirs(os.path.join(root, os.path.dirname(REGISTRY)))
            for rel, data in (("KNOWN_ISSUES.md", index), (REGISTRY, registry)):
                if data is not None:
                    with open(os.path.join(root, rel), "wb") as f:
                        f.write(data)
            if dir_registry:
                os.mkdir(os.path.join(root, REGISTRY))
            if dangling:
                os.symlink(os.path.join(root, "nowhere"), os.path.join(root, REGISTRY))
            return root
        ok, fx = one.encode(), fixed.encode()
        runs = (("a tree with its OPEN row owned exits 0", tree("t0", ok, b"1\tOWNER\ta\n"), 0),
                ("a tree with no registry exits 1", tree("t1", fx), 1),
                ("a tree without an index exits 2", tree("t2", None, b""), 2),
                ("a tree with a non-UTF-8 index exits 2", tree("t3", b"| caf\xe9 |\n", b""), 2),
                ("a tree with a non-UTF-8 registry exits 2", tree("t4", fx, b"1\tOWNER\tcaf\xe9\n"), 2),
                ("a tree whose registry is a directory exits 2", tree("t5", fx, None, dir_registry=True), 2),
                ("a tree whose registry is a dangling symlink exits 2", tree("t6", fx, None, dangling=True), 2))
        for name, root, want in runs:
            try:
                rc = run(root)[0]
            except Exception as e:
                rc = f"raised {type(e).__name__}"
            if rc != want:
                wrong.append(f"{name}: wanted exit {want}, got {rc}")
        # main(): THIS file run as a command, so its dispatch and exit status are pinned too (review #36b)
        g0, g1 = tree("g0", ok, b"1\tOWNER\ta\n"), tree("g1", ok, b"")
        inited = [git_init(g0), git_init(g1)]
        if not all(inited):     # only a missing or failing git fires this, so no mutation pins it where git runs
            wrong.append("git cannot run here, so the command checks cannot build their work trees")
        # with no git on PATH, git_init() must say False, not raise (review #38a)
        saved_path = os.environ.get("PATH")     # None if unset: restored by removal (review #46b)
        os.environ["PATH"] = os.path.join(td, "no-bin")
        try:
            got = git_init(os.path.join(td, "t0"))
        except Exception as e:
            got = f"raised {type(e).__name__}"
        finally:
            os.environ.pop("PATH", None) if saved_path is None else os.environ.__setitem__("PATH", saved_path)
        if got is not False:
            wrong.append(f"git_init() with no git on PATH: wanted False, got {got}")
        # git init under a HOSTILE caller environment: an exported GIT_DIR must not reach it (review #37b). The bait is
        # a plain directory, so a leak creates bait/.git and harms nothing real. Its own tree `gb`, initialised ONLY
        # here, so that this check alone catches the leak: g0 and g1 once shared it, and the command checks caught it
        # first (review #38b)
        bait, gb = os.path.join(td, "bait"), tree("gb", ok, b"")
        os.mkdir(bait)
        saved = {k: os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE")}
        os.environ.update(GIT_DIR=os.path.join(bait, ".git"), GIT_WORK_TREE=bait)
        try:
            git_init(gb)
        finally:
            for k, v in saved.items():
                os.environ.pop(k) if v is None else os.environ.__setitem__(k, v)
        if os.path.exists(os.path.join(bait, ".git")):
            wrong.append("git init under an exported GIT_DIR: it reached the caller's repository, not the new tree")
        elif all(inited) and not os.path.isdir(os.path.join(gb, ".git")):   # no git: already reported (review #39b)
            wrong.append("git init under an exported GIT_DIR made no repository in the new tree")
        # `plain` sits INSIDE a work tree, `enc`, on every host, so the ceiling at `enc` is what keeps it outside; it
        # once mattered only where TMPDIR lay inside a repository (review #38b)
        enc = os.path.join(td, "enc")
        plain = os.path.join(enc, "plain")
        os.makedirs(plain)
        git_init(enc)
        base = clean_env(GIT_CEILING_DIRECTORIES=os.path.realpath(enc))
        # every GIT_* variable that redirects git, not only GIT_DIR and GIT_WORK_TREE (review #38b)
        hostile = dict(base, GIT_DIR=os.path.join(g0, ".git"), GIT_WORK_TREE=g0, GIT_OBJECT_DIRECTORY=os.path.join(td, "none"),
                       GIT_INDEX_FILE=os.path.join(td, "none"), GIT_COMMON_DIR=os.path.join(td, "none"))
        clis = (("the command exits 0 on an owned work tree", g0, [], base, 0, "[owned] PASS"),
                ("the command exits 1 on an unowned OPEN row", g1, [], base, 1, "(UNOWNED)"),
                ("the command exits 1 on an unowned row whatever GIT_DIR and GIT_WORK_TREE say", g1, [], hostile, 1, "(UNOWNED)"),
                ("the command exits 2 outside a work tree", plain, [], base, 2, "not inside a git work tree"),
                ("the command exits 2 when git cannot run", g0, [], dict(base, PATH=os.path.join(td, "no-bin")), 2, "git cannot run"),
                ("the command exits 1 run from a subdirectory of that work tree", os.path.join(g1, "docs"), [], base, 1, "(UNOWNED)"),
                ("the command exits 2 on an unknown argument", g0, ["--mutation"], base, 2, "usage"))
        for name, cwd, argv, env, want, text in clis:
            r = subprocess.run([sys.executable, os.path.abspath(__file__), *argv], cwd=cwd, capture_output=True, text=True, env=env)
            if r.returncode != want or text not in r.stdout:     # the exit AND its reason: two paths exit 2 (#37b)
                wrong.append(f"{name}: wanted exit {want} saying {text!r}, got {r.returncode}: {r.stdout.strip()[-80:]!r}")
    modes = (([], "live"), (["--self-test"], "self-test"), (["--mutations"], "mutations"), (["--mutation"], None),
             (["--selftest"], None), (["--self-test", "--mutations"], None), (["x"], None))
    for argv, want in modes:
        if mode(argv) != want:
            wrong.append(f"arguments {argv}: wanted mode {want}, got {mode(argv)}")
    for name, body, reg, want in shapes:
        if "upper-case ID" in name or "bold **id**" in name or "code `id`" in name or "doubled space" in name:
            h = (head.replace("| id |", "| ID |", 1) if "upper-case" in name else
                 head.replace("| id |", "| **id** |", 1) if "bold" in name else
                 head.replace("| id |", "| `id` |", 1) if "code" in name else
                 head.replace("one-sentence failure", "one-sentence  failure", 1))
            doc, reg = h + "| 1 | LOW | OPEN | x | d | u |\n", "1\tOWNER\ta\n"
        elif body is None:
            doc = "# no table here\n"
        else:
            doc = head + body
        try:
            got, _, _ = check(doc, reg)
        except Exception as e:                   # a crash in check() is a wrong answer, not a harness crash (#47b)
            wrong.append(f"{name}: check() raised {type(e).__name__}")
            continue
        if len(got) != want:
            wrong.append(f"{name}: wanted {want} problem(s), got {len(got)}: {got}")
    for w in wrong:
        print(f"  *** WRONG *** {w}")
    print(f"[owned self-test] {'FAIL' if wrong else 'PASS'} :: {len(shapes)} shapes, {len(exits)} exit, {len(reads)} read, "
          f"{len(runs)} work-tree, {len(clis)} command and {len(modes)} argument checks")   # all (#30a)
    return 1 if wrong else 0


def main():
    m = mode(sys.argv[1:])
    if m is None:
        print(f"[owned] usage: {os.path.basename(sys.argv[0])} [--self-test | --mutations]; got {sys.argv[1:]}")
        return 2
    if m == "self-test":
        return self_test()
    if m == "mutations":
        return mutations()
    root, why = toplevel()
    if not root:
        print(f"[owned] CANNOT LOOK :: {why}")
        return 2
    rc, out = run(root)
    print("\n".join(out))
    return rc


# (label, text in this file, replacement). Each must make the self-test fail. `--mutations` refuses (exit 2) if a
# text is not found exactly once, so a mutation cannot silently stop applying when the code moves.
MUTATIONS = [
    ('reference definitions not passed', '    return (pipe_spans(rest, env) > 0 or', '    return (pipe_spans(rest) > 0 or'),
    ('an invalid escape in a docstring', 'code span (an escaped `\\\\|` there is kept), link', 'code span (an escaped `\\|` there is kept), link'),
    # ("spans read from the whole line", "an image target pipe not counted") are RETIRED as equivalent under the blunt
    # rule: no span holds a pipe before the status, and a cut image target is caught as an unclosed `](` (#49)
    ('an unclosed link target at the cell end accepted', '            or bool(re.search(r"\\]\\([^)]*$", cell.strip())))', '            or False)'),
    # ("an image alt pipe not counted", "a pipe in link text not counted", "escaped pipes split cells in status_cut") are RETIRED
    # as equivalent under the blunt rule: the raw [...] check and any pipe span from the status on catch the same rows (#49)
    ('the raw bracket pipe not checked', ' or bool(re.search(r"\\[[^\\[\\]]*(?<!\\\\)\\|[^\\[\\]]*\\]", rest))', ''),
    ('link titles not read', ' + (tk.attrs or {}).get("title", "")   # title too', '   # title too'),
    ('escaped pipes in code spans counted', '            n += bool(re.search(r"(?<!\\\\)\\|", tk.content))', '            n += "|" in tk.content'),
    ('the link depth never closes', '        elif tk.type == "link_close":\n            depth -= 1', '        elif tk.type == "link_close":\n            pass'),
    ('a row without a leading pipe read as having one', '    k = 2 if src.startswith("|") else 1', '    k = 2'),
    ('the short-row guard off by one', '    if len(pipes) <= k:\n        return False', '    if len(pipes) < k:\n        return False'),
    ('the fold without NFKD', 'for c in (a,) if a else unicodedata.normalize("NFKD", ch):', 'for c in (a,) if a else (ch,):'),
    ('marks kept by the fold', '            if unicodedata.category(c) in ("Mn", "Me") or INVISIBLE.match(c):\n                continue\n', ''),
    ('invisibles kept by the fold', ' or INVISIBLE.match(c):\n                continue', ':\n                continue'),
    ('a pipe in a code span not counted', '            n += bool(re.search(r"(?<!\\\\)\\|", tk.content))', '            n += 0'),
    ('a pipe in an HTML tag not counted', '            n += "|" in tk.content\n        elif tk.type == "link_open":', '            n += 0\n        elif tk.type == "link_open":'),
    ('a pipe in a link target not counted', '            depth += 1\n            n += "|" in href or "%7C" in href.upper()', '            depth += 1'),
    ('the status cut not checked', 'if cells <= len(HEADER) and status_cut(src, env):', 'if False and status_cut(src, env):'),
    ('a letter decomposed before it is read', '        for c in (a,) if a else unicodedata.normalize("NFKD", ch):', '        for c in unicodedata.normalize("NFKD", ch):'),
    ('more list-number digits refused', '\\d{1,9}[.)](?=\\s)', '\\d[.)](?=\\s)'),
    ('a dash is a marker without a space', '[-*+](?=\\s)', '[-*+]'),
    ('Greek omicron not read as o', '"OMICRON": "o", ', ''),
    ('enclosing marks refused', 'cat in ("Mn", "Me"):   # marks', 'cat in ("Mn",):   # marks'),
    ('enclosing marks kept by the fold', '        if unicodedata.category(c) in ("Mn", "Me") or INVISIBLE.match(c):', '        if unicodedata.category(c) in ("Mn",) or INVISIBLE.match(c):'),
    ('letters not folded before the open check', '        rest = fold(rest)\n', '        rest = rest\n'),
    ('symbols and punctuation refused', ' or cat[0] in "PSN" or cat == "Zs" or cat in', ' or cat in'),
    ('any letter accepted', '    return cat[0] == "L" and letter_as(c) is not None', '    return cat[0] == "L"'),
    ("other scripts' letters read as themselves", '        return None                        # other scripts', '        return ""                          # other scripts'),
    ('look-alike letters read as themselves', '    return hits.pop() if len(hits) == 1 else (None if hits else "")', '    return ""'),
    ('combining marks refused', ' or cat == "Zs" or cat in ("Mn", "Me"):', ' or cat == "Zs":'),
    ('sigma not folded', ', "SIGMA": "o"}', '}'),
    ('a tab refused', ' or c == "\\t" or', ' or'),
    ("the NFKD base's name ignored", '(unicodedata.name(c, "") + " " + unicodedata.name(base, ""))', 'unicodedata.name(c, "")'),
    ('nested f-strings not searched', 'and (tk.type != tokenize.FSTRING_MIDDLE or depth > 1)', 'and tk.type != tokenize.FSTRING_MIDDLE'),
    # ("open matched case-sensitively") is RETIRED as equivalent: fold() lowercases every letter that can spell open,
    # those it reads as ASCII (⚠ this said *"every letter"*; Δ and Æ stay as they are; review #45a) (review #44b)
    ("the registry-count check dropped", "        if n != 1:\n", "        if False:\n"),
    ("more than one line accepted", "        if n != 1:\n", "        if n == 0:\n"),
    ("stray registry lines accepted", "        if rid not in open_ids:\n", "        if False:\n"),
    ("any kind accepted", "        if kind not in KINDS:\n", "        if False:\n"),
    ("empty text accepted", '        if not INVISIBLE.sub("", body).strip():', "        if False:"),
    ("invisible-only text accepted", 'if not INVISIBLE.sub("", body).strip():', 'if not body.strip():'),
    ("a fourth field accepted", "        if len(f) != 3:\n", "        if len(f) not in (3, 4):\n"),
    ("comment lines read as entries", 'line.lstrip().startswith("#")', 'False'),
    ("markup before the status word read through", 'STATUS_RE = re.compile(r"^\\s*(?:', 'STATUS_RE = re.compile(r"^[\\s~<>/a-z`]*(?:'),
    ("any closing marker after the word", '(?(u)[*_]*|\\**)(?=', '[*_]*(?='),
    ("open matched as a whole word only", 'OPEN_WORD = re.compile(r"open", re.I)', 'OPEN_WORD = re.compile(r"\\bopen\\b", re.I)'),
    ("only FIXED checked for open", '        if s.group("w").upper() != "OPEN" and OPEN_WORD.search', '        if s.group("w").upper() == "FIXED" and OPEN_WORD.search'),
    ("the status SOURCE read for open", 'shown, w = _shown(stok).lstrip(), s.group("w")', 'shown, w = status_src.lstrip(), s.group("w")'),
    # ("invisible characters kept") is RETIRED with the code it mutated; fold() drops them now (⚠ this said STATUS_CHARS
    # refuses them; 264 it matches are allowed and dropped; review #44a)
    ("shown pieces joined with a space", '    return "".join(c.content if c.type != "image"', '    return " ".join(c.content if c.type != "image"'),
    ("image alt text not read", 'if c.type in ("text", "code_inline", "image"))   # alt', 'if c.type in ("text", "code_inline"))   # alt'),
    ("index cells not scanned for HTML", '    for tk in toks:\n        bits', '    for tk in [x for x in toks if not (x.map and x.map[0] in covered)]:\n        bits'),
    ("invisibles as a fixed list of six", 'for c in range(sys.maxunicode + 1)\n                                     if unicodedata.category(chr(c)) == "Cf" or c in _DI)', 'for c in (0xAD, 0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF))'),
    ("format characters only, no default-ignorables", 'unicodedata.category(chr(c)) == "Cf" or c in _DI', 'unicodedata.category(chr(c)) == "Cf"'),
    ("invisibles from the BMP only", 'for c in range(sys.maxunicode + 1)\n', 'for c in range(0x10000)\n'),
    ("exit 0 while problems exist but none is OPEN", '    return (1 if problems else 0), out', '    return (1 if problems and n_open else 0), out'),
    ("exit 2 when no row is OPEN", '    if not n_rows:     # the problems', '    if not n_open:     # the problems'),
    ("markup, not letters, before the status word read through", 'STATUS_RE = re.compile(r"^\\s*(?:', 'STATUS_RE = re.compile(r"^[\\s~<>/`]*(?:'),
    ("a whitespace-only registry line read", 'if not line.strip() or line.lstrip().startswith("#")', 'if not line or line.lstrip().startswith("#")'),
    ("HTML_TABLE missing thead, tbody and th", 't(able|head|body|r|d|h)\\b", re.I)', 't(able|r|d)\\b", re.I)'),
    ("ids of any word character", 'ID_RE = re.compile(r"^[\\s*_]*([A-Za-z0-9]+)', 'ID_RE = re.compile(r"^[\\s*_]*(\\w+)'),
    ("a BOM before the index kept", '    text = text[1:] if text.startswith("\\ufeff") else text      # a BOM before a first', '    text = text      # a BOM before a first'),
    ("an undecodable file raises", '    except (OSError, UnicodeDecodeError) as e:\n        return None, f"{path}: {e}"', '    except OSError as e:\n        return None, f"{path}: {e}"'),
    ("an absent required file read as absent", '    if not required and not os.path.lexists(path):', '    if not os.path.lexists(path):'),
    ("registry read errors ignored", '    for e in (e1, e2):', '    for e in (e1,):'),
    ("the index read as optional", 'read_file(os.path.join(root, "KNOWN_ISSUES.md"), True)', 'read_file(os.path.join(root, "KNOWN_ISSUES.md"), False)'),
    ("a dangling symlink read as absent", 'and not os.path.lexists(path):', 'and not os.path.exists(path):'),
    ("unknown arguments run the live check", 'return MODES.get(tuple(argv))', 'return MODES.get(tuple(argv), "live")'),
    ("lone CRs kept", '    text = text.replace("\\r\\n", "\\n").replace("\\r", "\\n")\n', '    text = text\n'),
    # ("a tab lead hides a row") is RETIRED as equivalent: CONTAINER's `\s*` strips a tab too (review #43b)
    ("a status word ended by ? or -", '(?=$|[\\s.,:;)\\u2013\\u2014])")   # en dash', '(?=$|[\\s.,:;)\\u2013\\u2014?-])")   # en dash'),
    ("a status word ended by /", '(?=$|[\\s.,:;)\\u2013\\u2014])")   # en dash', '(?=$|[\\s.,:;)\\u2013\\u2014/])")   # en dash'),
    ("the live exit status dropped", '    print("\\n".join(out))\n    return rc\n', '    print("\\n".join(out))\n    return 0\n'),
    ("a usage error exits 0", '        return 2\n    if m == "self-test":', '        return 0\n    if m == "self-test":'),
    ("outside a work tree exits 0", 'CANNOT LOOK :: {why}")\n        return 2', 'CANNOT LOOK :: {why}")\n        return 0'),
    ("only GIT_DIR and GIT_WORK_TREE stripped", 'if not k.startswith("GIT_") or k == "GIT_CEILING_DIRECTORIES"}', 'if k not in ("GIT_DIR", "GIT_WORK_TREE")}'),
    ("the command checks' ceiling dropped", 'base = clean_env(GIT_CEILING_DIRECTORIES=os.path.realpath(enc))', 'base = clean_env()'),
    ("the two exit-2 reasons merged", 'return None, f"git cannot run: {e}"', 'return None, f"not inside a git work tree: {e}"'),
    ("a missing git crashes the self-test", '    except OSError:\n        return False', '    except ImportError:\n        return False'),
    # ("a failed git init unreported") is RETIRED: as `if False:` it also skipped both git_init() calls, so it went red
    # through the command checks, not its own; with the calls kept apart it cannot go red where git runs (self-found)
    ("GIT_* variables inherited", 'if not k.startswith("GIT_") or k == "GIT_CEILING_DIRECTORIES"}', 'if True}'),
    ("git init not isolated", 'cwd=path, capture_output=True, env=clean_env())', 'cwd=path, capture_output=True)'),
    ("the work-tree lookup not isolated", '["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, env=clean_env())', '["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)'),
    ("a missing git raises", '    except OSError as e:\n        return None, f"git cannot run: {e}"', '    except ImportError as e:\n        return None, f"git cannot run: {e}"'),
    ("Braille blank visible", ' | {0x2800}   # Braille', '   # Braille'),
    ("a zero-width lead hides a row", '        bare = INVISIBLE.sub("", l)\n', '        bare = l\n'),
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
    ("every BOM stripped", 'text = text[1:] if text.startswith("\\ufeff") else text      # a UTF-8 BOM', 'text = text.lstrip("\\ufeff")      # a UTF-8 BOM'),
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
    ("a malformed line owns its row", 'if e[0] in KINDS and INVISIBLE.sub("", e[1]).strip()])', "if True])"),
    ("invisible-only text owns its row", 'if e[0] in KINDS and INVISIBLE.sub("", e[1]).strip()])', "if e[0] in KINDS and e[1]])"),
    ("fenced blocks excused", '    lines, covered = text.split("\\n"), set()',
     '    lines, covered = text.split("\\n"), set()\n    covered.update(x for tk in toks if tk.type == "fence" and tk.map for x in range(*tk.map))'),
    ("a BOM not stripped", 'text = text[1:] if text.startswith("\\ufeff") else text      # a UTF-8 BOM', 'text = text      # a UTF-8 BOM'),
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
    ("no-rows exit 2 dropped", "    if not n_rows:     # the problems", "    if False:     # the problems"),
    ("no-rows problems dropped", 'return 2, [f"  {p}" for p in problems] + ["[owned] CANNOT LOOK', 'return 2, [] + ["[owned] CANNOT LOOK'),
    ("any severity accepted", '        if sev.upper() not in SEVERITIES:\n', '        if False:\n'),
    ("an empty updated accepted", '        if not updated:\n', '        if False:\n'),
    *[(f"severity {w} dropped", 'SEVERITIES = ("CRITICAL", "BLOCKER", "HIGH", "MEDIUM", "LOW", "TRAP")', 'SEVERITIES = ("CRITICAL", "BLOCKER", "HIGH", "MEDIUM", "LOW", "TRAP")'.replace(f'"{w}", ', "").replace(f', "{w}"', ""))
      for w in ("CRITICAL", "BLOCKER", "HIGH", "MEDIUM", "LOW", "TRAP")],
    ("blockquote markers counted as cells", 'CONTAINER.sub("", lines[cur[0] - 1]).strip()', 'lines[cur[0] - 1].strip()'),
    ("quote markers unstripped on the row-line scan", '        lead = CONTAINER.sub("", bare)\n', '        lead = bare.lstrip()\n'),
    ("prose behind a marker read as a row", 'and (lead == bare.lstrip() or len(re.findall(r"(?<!\\\\)\\|", lead)) >= 3):', ':'),
    ("any status character accepted", '        if s.group("w").upper() != "OPEN" and odd:', '        if False and odd:'),
    ("image alt read from its source", 'c.content if c.type != "image" else', 'c.content if True else'),
    ("only one quote marker stripped", 'CONTAINER = re.compile(r"^(?:\\s*(?:>|[-*+](?=\\s)|\\d{1,9}[.)](?=\\s)))*\\s*")', 'CONTAINER = re.compile(r"^\\s*(?:>\\s?)?")'),
    ("list markers not stripped", '(?:>|[-*+](?=\\s)|\\d{1,9}[.)](?=\\s))', '(?:>)'),
    ("an escaped trailing pipe counted", 'bool(re.search(r"(?<!\\\\)\\|$", src))', 'bool(re.search(r"\\|$", src))'),
    ("row whitespace kept", 'CONTAINER.sub("", lines[cur[0] - 1]).strip() if 0 < cur[0]', 'CONTAINER.sub("", lines[cur[0] - 1]).rstrip("\\n") if 0 < cur[0]'),
    ("CRLF left as CR plus LF", '    text = text.replace("\\r\\n", "\\n").replace("\\r", "\\n")\n', '    text = text.replace("\\r", "\\n")\n'),
    ("an empty updated skips the row", '            problems.append(f"line {line}: id {rid}: the updated cell is empty; a row missing a cell shifts its status")\n', '            problems.append(f"line {line}: id {rid}: the updated cell is empty; a row missing a cell shifts its status")\n            continue\n'),
    ("updated read from its source", '_rendered(c[5]) if c[5] else ""', 'c[5].content.strip() if c[5] else ""'),
    ("a backslash in an f-string's braces", "got {check(crlf, OWNED)[1:]}", "got {check(crlf, '1\\tOWNER\\ta\\n')[1:]}"),
    ("more cells than the header accepted", '            if cells > len(HEADER):', '            if False:'),
    ("the current directory taken as the work tree", '    root = r.stdout.strip()\n', '    root = os.getcwd() if r.stdout.strip() else ""\n'),
    ("rows outside tables unseen", '        if lead.startswith("|") and n not in covered and', '        if False and'),
]


def mutations():
    import tempfile
    src = open(__file__, encoding="utf-8").read()
    body = src[:src.index("# (label, text in this file, replacement).")]    # mutate the CODE, not this list
    alive, broken, skipped = [], [], []
    with tempfile.TemporaryDirectory() as td:
        # the UNMUTATED self-test must pass first: a failing one makes a mutant look red unless the wrong shape alone
        # would have killed it (self-found, 2026-09-24; ⚠ first said "every mutant"; review #36a)
        p = os.path.join(td, "m.py")
        open(p, "w", encoding="utf-8").write(src)
        # every child gets clean_env(): a mutant that removes the isolation ON PURPOSE otherwise ran `git init` against
        # the caller's GIT_DIR and set a linked worktree's shared config bare, while reporting PASS (review #39b)
        r = subprocess.run([sys.executable, p, "--self-test"], capture_output=True, text=True, env=clean_env())
        if r.returncode != 0 or "[owned self-test] PASS" not in r.stdout:
            print(f"[owned mutations] CANNOT LOOK :: the unmutated self-test does not pass (exit {r.returncode})")
            return 2
        for label, a, b in MUTATIONS:
            if body.count(a) != 1:
                broken.append(f"{label}: its text occurs {body.count(a)} times in the code, not once")
                continue
            p = os.path.join(td, "m.py")
            open(p, "w", encoding="utf-8").write(src.replace(a, b, 1))
            # the f-string mutant IS a syntax error before Python 3.12: there, failing to compile is the defect found,
            # not a crash of the harness, which once exited 2 on 3.9 (and would on Perlmutter's 3.11; self-found)
            # the tokenizer check runs only from 3.12, so its own mutants cannot go red earlier: SKIPPED and said so,
            # not counted as survivors (self-found, 2026-09-24)
            if label == "nested f-strings not searched" and sys.version_info < (3, 12):
                skipped.append(label)
                continue
            if label == "a backslash in an f-string's braces" and sys.version_info < (3, 12):
                try:
                    compile(src.replace(a, b, 1), p, "exec")
                except SyntaxError:
                    continue
            r = subprocess.run([sys.executable, p, "--self-test"], capture_output=True, text=True, env=clean_env())
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
          f"{len(MUTATIONS) - len(alive) - len(broken) - len(skipped)} turn the self-test red"
          + (f", {len(skipped)} skipped before Python 3.12" if skipped else ""))
    return 2 if broken else 1 if alive else 0


if __name__ == "__main__":
    raise SystemExit(main())
