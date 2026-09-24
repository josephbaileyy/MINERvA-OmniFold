#!/usr/bin/env python3
"""No unowned open issue: every OPEN row of KNOWN_ISSUES.md has exactly one line in the blocker registry.

    probe-20260923-no-unowned-open-issue.py [--self-test | --mutations]

Any other argument, or both together, exits 2: a mistyped `--mutation` once ran the live check and exited 0
(review #35b).

`--mutations` applies each single-change mutation in MUTATIONS to a copy of this file and requires the copy's
self-test to FAIL, after requiring the UNMUTATED self-test to pass. Everything above MUTATIONS, main() included,
can be mutated; `mutations()` itself, below it, cannot, and its tally is checked only by reading it (review #36b). A claim that "every mutation turns the self-test red" was twice made about a mutation set
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
    and code spans and image alt text, entities decoded, soft hyphens and every other invisible format character dropped), not a link's target, so it
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
index header (⚠ that case was first listed among the exit-1 refusals; review #28a), or when the index or the
registry is not UTF-8, is a directory, or is a symlink to nothing (these once raised or, for the symlink, counted
as an absent registry, exiting 1; reviews #34b, #35a). A registry that does not exist at all is the exit-1
refusal above. It checks the git work tree holding
the CURRENT DIRECTORY, not the one holding this file (review #34b).

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
_DI = {c for a, b in ((0xAD, 0xAD), (0x34F, 0x34F), (0x61C, 0x61C), (0x115F, 0x1160), (0x17B4, 0x17B5), (0x180B, 0x180F),
                      (0x200B, 0x200F), (0x202A, 0x202E), (0x2060, 0x206F), (0x3164, 0x3164), (0xFE00, 0xFE0F),
                      (0xFEFF, 0xFEFF), (0xFFA0, 0xFFA0), (0xFFF0, 0xFFF8), (0x1BCA0, 0x1BCA3), (0x1D173, 0x1D17A),
                      (0xE0000, 0xE0FFF)) for c in range(a, b + 1)}
INVISIBLE = re.compile("[" + "".join(re.escape(chr(c)) for c in range(sys.maxunicode + 1)
                                     if unicodedata.category(chr(c)) == "Cf" or c in _DI) + "]")
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
    return "".join(c.content for c in (inline.children or []) if c.type in ("text", "code_inline", "image"))   # alt (#34b)


def index_rows(text):
    """(id source, status source, line, status inline token) for each body row of each table whose rendered header is exactly HEADER,
    plus a list of problems: any table whose rendered header is not exactly HEADER, and `|`-led lines outside every
    parsed table."""
    text = text[1:] if text.startswith("\ufeff") else text      # a BOM before a first table line hid the table (#34b)
    # markdown-it ends a line at a lone CR, `split("\n")` does not: two in a table shifted the numbering, and a cut-off
    # OPEN row after it fell on a "covered" line and passed (review #36b)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
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
        if not INVISIBLE.sub("", body).strip():         # a text of only U+200B once owned a row (#35b)
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
        # --- review #34b: struck statuses, blank registry lines, default-ignorables and alt text, <thead>, a Unicode id
        ("a struck FIXED is refused", "| 1 | L | ~~FIXED 2026-09-01~~ still broken | x | d | u |\n", "", 1),
        ("a struck OPEN before FIXED is refused, and its registry line is stray", "| 1 | L | ~~OPEN 2026~~ FIXED | x | d | u |\n", "1\tOWNER\ta\n", 2),
        ("blocker text of only invisible characters is empty", "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER\t\u200b\u2060\n", 2),
        ("a whitespace-only registry line is blank", "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER\ta\n   \n", 0),
        *[(f"open hidden by U+{ord(c):04X} is refused", f"| 1 | L | FIXED; still op{c}en | x | d | u |\n", "", 1)
          for c in "\ufe0f\U000e0100\u3164\u115f\U000e0001"],
        ("image alt text saying open is refused", "| 1 | L | FIXED ![still open](x.png) | x | d | u |\n", "", 1),
        ("a stray <thead><th> is refused", "| 1 | L | FIXED | x | d | u |\n\n<thead><th>x</th></thead>\n", "", 1),
        ("a stray <tbody> is refused", "| 1 | L | FIXED | x | d | u |\n\n<tbody>\n", "", 1),
        ("a Unicode-letter id is refused", "| \u00e91 | L | FIXED | x | d | u |\n", "", 1),
        # --- review #33b: every invisible format character, not a list of six
        *[(f"open hidden by U+{ord(c):04X} is refused", f"| 1 | L | FIXED; still op{c}en | x | d | u |\n", "", 1)
          for c in "\u200c\u200d\u2060\ufeff\u200e\u200f\u2061\u034f"],
        *[(f"a row cut off after a U+{ord(c):04X} lead is refused", f"| 1 | L | FIXED | x | d | u |\n\n{c}| 2 | L | OPEN | x | d | u |\n", "", 1)
          for c in "\u200e\u200f"],
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
        # --- review #36b: boundaries pinned WITHOUT an `open` that the open rule would refuse anyway; a tab lead; lone CRs
        *[(f"status {s!r} is refused", f"| 1 | L | {s} | x | d | u |\n", "", 1)
          for s in ("FIXED-pending review", "FIXED?", "**FIXED**-x", "FIXED/pending", "FIXED' x", "FIXED!")],
        ("a row cut off after a tab lead is refused", "| 1 | L | FIXED | x | d | u |\n\n\t| 2 | L | OPEN | x | d | u |\n", "", 1),
        ("lone CRs in a table do not hide a cut-off OPEN row",
         "| 1 | L | FIXED | x | d | u |\r| 3 | L | FIXED | y | d | u |\r| 4 | L | FIXED | z | d | u |\n\n| 99 | L | OPEN | x | d | u |\n", "", 1),
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
    fixed = head + "| 1 | L | FIXED | x | d | u |\n"
    exits = (("exit 0 when every OPEN row is owned", one, "1\tOWNER\ta\n", 0),
             ("exit 1 when an OPEN row is unowned", one, "", 1),
             ("exit 1 when the registry is absent", one, None, 1),
             ("exit 2 when no index table exists", "# none\n", "", 2),
             # --- review #34b: the live index has NO OPEN row, and no exit check had one without
             ("exit 0 when no row is OPEN", fixed, "", 0),
             ("exit 1 when an all-FIXED index hides a cut-off OPEN row", fixed + "\n| 2 | L | OPEN | x | d | u |\n", "", 1),
             ("exit 1 when an all-FIXED index has no registry", fixed, None, 1),
             ("exit 0 with a BOM before the first table line", "\ufeff" + one, "1\tOWNER\ta\n", 0))
    for name, doc, reg, want in exits:
        rc, _ = decide(doc, reg)
        if rc != want:
            wrong.append(f"{name}: wanted exit {want}, got {rc}")
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
        for g in (g0, g1):
            subprocess.run(["git", "init", "-q"], cwd=g, capture_output=True)
        plain = os.path.join(td, "plain")
        os.mkdir(plain)
        clis = (("the command exits 0 on an owned work tree", g0, [], 0),
                ("the command exits 1 on an unowned OPEN row", g1, [], 1),
                ("the command exits 2 outside a work tree", plain, [], 2),
                ("the command exits 2 on an unknown argument", g0, ["--mutation"], 2))
        for name, cwd, argv, want in clis:
            rc = subprocess.run([sys.executable, os.path.abspath(__file__), *argv], cwd=cwd, capture_output=True).returncode
            if rc != want:
                wrong.append(f"{name}: wanted exit {want}, got {rc}")
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
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    if not root:
        print("[owned] CANNOT LOOK :: not inside a git work tree")
        return 2
    rc, out = run(root)
    print("\n".join(out))
    return rc


# (label, text in this file, replacement). Each must make the self-test fail. `--mutations` refuses (exit 2) if a
# text is not found exactly once, so a mutation cannot silently stop applying when the code moves.
MUTATIONS = [
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
    ("open matched case-sensitively", 'OPEN_WORD = re.compile(r"open", re.I)', 'OPEN_WORD = re.compile(r"open")'),
    ("only FIXED checked for open", '        if s.group("w").upper() != "OPEN" and OPEN_WORD.search', '        if s.group("w").upper() == "FIXED" and OPEN_WORD.search'),
    ("the status SOURCE read for open", 'INVISIBLE.sub("", _shown(stok)).lstrip(), s.group("w")', 'INVISIBLE.sub("", status_src).lstrip(), s.group("w")'),
    ("invisible characters kept", 'INVISIBLE.sub("", _shown(stok)).lstrip(), s.group("w")', '_shown(stok).lstrip(), s.group("w")'),
    ("shown pieces joined with a space", 'return "".join(c.content for c in (inline.children or []) if c.type in ("text", "code_inline", "image"))', 'return " ".join(c.content for c in (inline.children or []) if c.type in ("text", "code_inline", "image"))'),
    ("image alt text not read", 'if c.type in ("text", "code_inline", "image"))   # alt', 'if c.type in ("text", "code_inline"))   # alt'),
    ("index cells not scanned for HTML", '    for tk in toks:\n        bits', '    for tk in [x for x in toks if not (x.map and x.map[0] in covered)]:\n        bits'),
    ("invisibles as a fixed list of six", 'for c in range(sys.maxunicode + 1)\n                                     if unicodedata.category(chr(c)) == "Cf" or c in _DI)', 'for c in (0xAD, 0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF))'),
    ("format characters only, no default-ignorables", 'unicodedata.category(chr(c)) == "Cf" or c in _DI', 'unicodedata.category(chr(c)) == "Cf"'),
    ("invisibles from the BMP only", 'for c in range(sys.maxunicode + 1)\n', 'for c in range(0x10000)\n'),
    ("exit 0 while problems exist but none is OPEN", '    return (1 if problems else 0), out', '    return (1 if problems and n_open else 0), out'),
    ("exit 2 when no row is OPEN", '    if not n_rows:\n        return 2', '    if not n_open:\n        return 2'),
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
    ("a tab lead hides a row", 'if INVISIBLE.sub("", l).lstrip().startswith("|")', 'if INVISIBLE.sub("", l).lstrip(" ").startswith("|")'),
    ("a status word ended by ? or -", '(?=$|[\\s.,:;)\\u2013\\u2014])")   # en dash', '(?=$|[\\s.,:;)\\u2013\\u2014?-])")   # en dash'),
    ("a status word ended by /", '(?=$|[\\s.,:;)\\u2013\\u2014])")   # en dash', '(?=$|[\\s.,:;)\\u2013\\u2014/])")   # en dash'),
    ("the live exit status dropped", '    print("\\n".join(out))\n    return rc\n', '    print("\\n".join(out))\n    return 0\n'),
    ("a usage error exits 0", '        return 2\n    if m == "self-test":', '        return 0\n    if m == "self-test":'),
    ("outside a work tree exits 0", 'not inside a git work tree")\n        return 2', 'not inside a git work tree")\n        return 0'),
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
    ("no-rows exit 2 dropped", "    if not n_rows:\n        return 2,", "    if False:\n        return 2,"),
    ("rows outside tables unseen", '        if INVISIBLE.sub("", l).lstrip().startswith("|") and n not in covered:', '        if False:'),
]


def mutations():
    import tempfile
    src = open(__file__, encoding="utf-8").read()
    body = src[:src.index("# (label, text in this file, replacement).")]    # mutate the CODE, not this list
    alive, broken = [], []
    with tempfile.TemporaryDirectory() as td:
        # the UNMUTATED self-test must pass first: a failing one makes a mutant look red unless the wrong shape alone
        # would have killed it (self-found, 2026-09-24; ⚠ first said "every mutant"; review #36a)
        p = os.path.join(td, "m.py")
        open(p, "w", encoding="utf-8").write(src)
        r = subprocess.run([sys.executable, p, "--self-test"], capture_output=True, text=True)
        if r.returncode != 0 or "[owned self-test] PASS" not in r.stdout:
            print(f"[owned mutations] CANNOT LOOK :: the unmutated self-test does not pass (exit {r.returncode})")
            return 2
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


if __name__ == "__main__":
    raise SystemExit(main())
