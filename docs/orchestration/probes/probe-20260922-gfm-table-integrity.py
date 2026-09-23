#!/usr/bin/env python3
"""Sweep Markdown tables for rows GitHub-flavoured Markdown will render WRONG.

WHY THIS EXISTS. Two defects of this lane survived thirteen independent reviews and every self
round, because every check before this one read the SOURCE and none asked how it RENDERS:
  * a KNOWN_ISSUES row carried `|` inside backtick code spans. In a GFM table, backticks do NOT
    protect a pipe -- the row splits into extra cells, and GFM DISCARDS cells beyond the header's
    count, so the second half of the row (its repair note, its CHECK line and its date) silently
    vanished from the rendered table while reading perfectly in the source;
  * a BLOCKED-record row was torn across two physical lines. A table row cannot span lines, so the
    second line rendered as a NEW ROW of the table, its text crammed into the first cell. (⚠ This
    docstring said "rendered as a stray paragraph"; that was reasoned, not rendered -- GFM continues a
    table to the next blank line. Review #11b rendered it.)

Checks, per GFM table (a header row followed by a delimiter row):
  codespan-pipe -- an unescaped `|` INSIDE a backtick code span. Checked independently of the
                   count, because a row one cell short PLUS a code-span pipe has exactly the
                   header's count: that pair passed a count-only check and still rendered with the
                   column boundary inside the code span (found by self-round 30).
  cell-parity  -- a cell with an odd number of backticks or of `**` (outside code spans), which
                  strands a marker: it renders as literal asterisks or a backtick (⚠ this said it
                  "re-pairs everything after it"; rendered, it did not)
  header-mismatch -- the HEADER row's cell count differs from the delimiter row's. GFM then does not
                  recognise a table at all: every row below renders as plain text. (Missed by the
                  first version of this probe, which never examined the header; independent review
                  #11a found it in VALIDATION_LEDGER.md, where a code-span pipe in a header un-tabled
                  six rows.)
  cells        -- a body row whose CELL count (GFM semantics: one optional leading and trailing pipe
                  trimmed, then split on unescaped pipes) differs from the delimiter row's. Too many
                  and GFM DROPS the excess -- including text after a row's last pipe, which the first
                  version mislabelled a torn row; too few and it pads with empty cells.
  torn-row     -- a line inside a table with no leading pipe. GFM makes it a ROW of its own; the
                  usual cause is a row broken across two physical lines.
  unicode-ws   -- a line in or beside a table that begins (after any ASCII spaces) with non-ASCII
                  whitespace -- U+00A0, U+3000, a form feed, U+2028. GitHub and markdown-it render it
                  differently, so the probe cannot say which is right (reviews #14b, #15b).
  (Earlier versions documented `trailing-cell` and `orphan-tail`; both are now covered by `cells`
  and `torn-row`, because GFM runs a table to the next blank line rather than to the first line
  without a pipe.)

Usage:  probe-20260922-gfm-table-integrity.py [FILE ...]   (default: every .md changed since
        177af61b). Exit 0 clean, 1 defects found, 2 cannot look. `--since REV` changes the base.
        `--self-test` runs the committed SHAPES, each with the exact set of kinds it must produce.
"""
import os
import re
import unicodedata
import subprocess
import sys

try:
    from markdown_it import MarkdownIt
except ImportError:
    MarkdownIt = None

# ⚠ BLOCK STRUCTURE COMES FROM A PARSER, NOT FROM THIS FILE. Earlier versions hand-coded which lines
# end a table (blank line, heading, fence, list, HTML, thematic break) and review #13b found four places
# they diverged from GitHub: `#5 |` is not a heading (ATX needs a space), `<b>r</b> |` does not start an
# HTML block, a closing fence must match its opening fence's character and length, and an indented line
# after a table is not a row. markdown-it-py implements CommonMark's block rules; this probe asks it
# which source lines became which table rows, and compares each row's SOURCE cells with its RENDERED ones.
SEP = re.compile(r"^\s{0,3}\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$|^\s{0,3}\|\s*:?-+:?\s*\|?\s*$")


def cells(line):
    """GFM cells of a SOURCE line: trim one leading and one trailing pipe, split on unescaped pipes."""
    t = line.strip()
    if t.startswith("|"):
        t = t[1:]
    if t.endswith("|") and not t.endswith("\\|"):
        t = t[:-1]
    return re.split(r"(?<!\\)\|", t)


def strip_code_spans(text):
    return re.sub(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", "", text)


def sweep(path):
    try:
        src = open(path, encoding="utf-8").read()
    except UnicodeDecodeError as e:
        return None, str(e)
    # "\n" ONLY, as the parser splits: `splitlines()` also breaks at form feed, U+0085 and U+2028, and every
    # line after one of those drifted off the parser's map (review #15b)
    lines = src.split("\n")
    toks = MarkdownIt("commonmark").enable(["table"]).parse(src)
    out, tabled, code = [], set(), set()
    for t in toks:
        if t.type in ("fence", "code_block", "html_block") and t.map:
            code.update(range(t.map[0], t.map[1]))
    k = 0
    while k < len(toks):
        if toks[k].type != "table_open":
            k += 1; continue
        ncol = None
        while toks[k].type != "table_close":
            t = toks[k]
            if t.type == "tr_open" and t.map:
                row, n_rendered, ln = [], 0, t.map[0]
                j = k + 1
                while toks[j].type != "tr_close":
                    if toks[j].type in ("th_open", "td_open"):
                        n_rendered += 1
                    if toks[j].type == "inline":
                        row.append(toks[j])
                    j += 1
                tabled.add(ln)
                # strip container prefixes the parser has already consumed: a table inside a
                # blockquote has `> ` on every line (a false positive in this probe's first parser-based
                # version, on a real CATALOG table)
                raw = re.sub(r"^\s{0,3}(>\s?)+", "", lines[ln])
                n_src = len(cells(raw))
                body = ncol is not None            # every row after the header
                if not body:
                    ncol = n_rendered              # the header row fixes the column count
                elif n_src > ncol:
                    out.append((ln + 1, "cells", f"{n_src} cells under {ncol} columns: GFM DROPS the excess"))
                elif n_src < ncol:
                    out.append((ln + 1, "cells", f"{n_src} cells under {ncol} columns: GFM pads with empty cells"))
                if body and not raw.lstrip().startswith("|"):
                    out.append((ln + 1, "torn-row", "a line with no leading pipe renders as a row of its own"))
                # a span is a backtick RUN closed by a run of the same length: "`[^`]*`" misread ``x|y``
                # as two empty spans and never saw its pipe
                for sm in re.finditer(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", raw):
                    if re.search(r"(?<!\\)\|", sm.group(2)):
                        out.append((ln + 1, "codespan-pipe", f"unescaped pipe in {sm.group(0)[:40]}"))
                src_cells = cells(raw)
                for ci, inl in enumerate(row):
                    shown = "".join(c.content for c in (inl.children or []) if c.type == "text")
                    rest = strip_code_spans(src_cells[ci]) if ci < len(src_cells) else ""
                    # a STRANDED marker: it renders literally AND the source has an unpaired one. A marker
                    # typed as a literal on purpose (TeX-style ``quotes'') renders literally too, but pairs
                    # evenly in the source; flagging every literal was this probe's own false positive
                    stranded_bold = "**" in shown and len(re.findall(r"(?<!\\)\*\*", rest)) % 2
                    stranded_tick = "`" in shown and len(re.findall(r"(?<!\\)`", rest)) % 2
                    if stranded_bold or stranded_tick:
                        out.append((ln + 1, "cell-parity", f"a stranded formatting marker renders literally in cell {ci}"))
            k += 1
        k += 1
    # a line that BEGINS with non-ASCII whitespace (U+00A0, U+3000, form feed...) near a table: GitHub and
    # markdown-it disagree about it -- GitHub renders a U+00A0-led row with an empty first cell and every cell
    # shifted right, and continues a table past a U+00A0-only line where markdown-it ends it (review #14b)
    for ln, l in enumerate(lines):
        s = l.lstrip(" \t")          # past ASCII spaces: " \u00a0| row" renders like "\u00a0| row" (review #15b)
        if ln in code or not s[:1]:
            continue
        if (s[0].isspace() or unicodedata.category(s[0]) in ("Zs", "Zl", "Zp")) and (
                "|" in l or any(abs(ln - t) <= 1 for t in tabled)):
            out.append((ln + 1, "unicode-ws", "a line near a table begins with non-ASCII whitespace; GitHub and "
                        "CommonMark parsers render it differently"))
    # a header + delimiter pair that the parser did NOT turn into a table -- including inside a blockquote,
    # whose `>` prefixes the first version never stripped (review #14b). Plain list items were already caught
    # before that change and `bare()` does not strip list markers (review #15a measured both)
    def bare(x):
        return re.sub(r"^\s{0,3}(>\s?)+", "", x).strip()
    for ln in range(len(lines) - 1):
        if ln in code or ln in tabled:
            continue
        if "|" in bare(lines[ln]) and SEP.match(bare(lines[ln + 1])) and not SEP.match(bare(lines[ln])):
            out.append((ln + 1, "header-mismatch",
                        f"header has {len(cells(bare(lines[ln])))} cells, delimiter {len(cells(bare(lines[ln + 1])))}: "
                        "GFM does NOT render a table here"))
    return out, None


# (name, source, the EXACT set of kinds the probe must report) -- judged against GitHub's renderer.
# ⚠ A yes/no expectation let `torn-row` and `codespan-pipe` be deleted with every shape still passing,
# because another kind fired on the same shape (review #15b). Each kind now has a shape that produces
# ONLY that kind, and `self_test` refuses if one does not.
SHAPES = [
    ("clean", "| a | b |\n|---|---|\n| 1 | 2 |\n", set()),
    ("code-span pipe", "| a | b |\n|---|---|\n| 1 | `x|y` |\n", {'cell-parity', 'cells', 'codespan-pipe'}),
    ("escaped pipe in a code span", "| a | b |\n|---|---|\n| 1 | `x\\|y` |\n", set()),
    ("text after the last pipe", "| a | b |\n|---|---|\n| 1 | 2 | tail\n", {'cells'}),
    ("too few cells (a documented warning)", "| a | b |\n|---|---|\n| 1 |\n", {'cells'}),
    ("no trailing pipe", "| a | b |\n|---|---|\n| 1 | 2\n", set()),
    ("heading right after", "| a | b |\n|---|---|\n| 1 | 2 |\n## h\n", set()),
    ("list right after", "| a | b |\n|---|---|\n| 1 | 2 |\n- x\n", set()),
    ("table in a fence", "```\n| a | b |\n|---|---|\n| 1 | 2 | 3 |\n```\n", set()),
    ("double-backtick span", "| a | b |\n|---|---|\n| 1 | ``a`b`` |\n", set()),
    ("header code-span pipe", "| a | `x|y` |\n|---|---|\n| 1 | 2 |\n", {'header-mismatch'}),
    ("stray bold", "| a | b |\n|---|---|\n| 1 | **x |\n", {'cell-parity'}),
    ("stray single backtick", "| a | b |\n|---|---|\n| 1 | `x |\n", {'cell-parity'}),
    ("TeX quotes, intended", "| a | b |\n|---|---|\n| 1 | ``before'' |\n", set()),
    ("'#5 |' row, excess dropped", "| a | b |\n|---|---|\n| 1 | 2 |\n#5 | x | y | DROPPED |\n", {'cells', 'torn-row'}),
    ("'<b>r</b> |' row, excess dropped", "| a | b |\n|---|---|\n| 1 | 2 |\n<b>r</b> | x | DROPPED |\n", {'cells', 'torn-row'}),
    ("4-backtick fence closed only by 4", "````\n```\n````\n| a | b |\n|---|---|\n| 1 | 2 | DROPPED |\n", {'cells'}),
    ("indented line after a table", "| a | b |\n|---|---|\n| 1 | 2 |\n    | not | a | row |\n", set()),
    ("table in a blockquote, clean", "> | a | b |\n> |---|---|\n> | 1 | 2 |\n", set()),
    ("table in a blockquote, excess", "> | a | b |\n> |---|---|\n> | 1 | 2 | X |\n", {'cells'}),
    ("U+00A0-led row", "| a | b | c |\n|---|---|---|\n\u00a0| x | 1 | note |\n", {'unicode-ws'}),
    ("U+00A0-only line inside a table", "| a | b |\n|---|---|\n| 1 | 2 |\n\u00a0\n| 3 | `p|q` |\n", {'unicode-ws'}),
    ("header mismatch inside a blockquote", "> | a | b | c |\n> |---|---|\n", {'header-mismatch'}),
    # --- review #15b: shapes that ISOLATE a kind, plus the whitespace classes the first fix missed
    ("torn row", "| a | b |\n|---|---|\n| 1 | 2 |\nx | y |\n", {'torn-row'}),
    ("double-backtick pipe, cell count matching", "| a | b | c |\n|---|---|---|\n| 1 | ``x|y`` |\n", {'codespan-pipe'}),
    ("form-feed-led row", "| a | b | c |\n|---|---|---|\n\x0c| x | 1 | note |\n", {'unicode-ws'}),
    ("U+2028-led row", "| a | b | c |\n|---|---|---|\n\u2028| x | 1 | note |\n", {'unicode-ws'}),
    ("one ASCII space then U+00A0", "| a | b | c |\n|---|---|---|\n \u00a0| x | 1 | note |\n", {'unicode-ws'}),
]


def self_test():
    import tempfile
    wrong = []
    with tempfile.TemporaryDirectory() as td:
        for name, src, want in SHAPES:
            f = os.path.join(td, "shape.md")
            open(f, "w", encoding="utf-8").write(src)
            found, err = sweep(f)
            got = None if err else {kind for _, kind, _ in found}
            if got != want:
                wrong.append(f"{name}: wanted {sorted(want)}, got {err or sorted(got)}")
    # every kind this file can emit needs a shape that produces it ALONE; otherwise deleting that check
    # leaves every shape passing
    emitted = set(re.findall(r'out\.append\(\(ln \+ 1, "([\w-]+)"', open(__file__, encoding="utf-8").read()))
    for kind in sorted(emitted - {k for *_, want in SHAPES if len(want) == 1 for k in want}):
        wrong.append(f"no shape isolates `{kind}`, so deleting that check would pass")
    for w in wrong:
        print(f"  *** WRONG *** {w}")
    print(f"[gfm-tables self-test] {'FAIL' if wrong else 'PASS'} :: {len(SHAPES)} shapes, "
          f"{len(emitted)} kinds each isolated by a shape" + (f"; {len(wrong)} wrong" if wrong else ""))
    return 1 if wrong else 0


def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        return 2 if MarkdownIt is None else self_test()
    base = "177af61b"
    if "--since" in args:
        k = args.index("--since"); base = args[k + 1]; del args[k:k + 2]
    # ⚠ RUN FROM THE REPOSITORY ROOT, whatever the caller's directory. `git diff --name-only` prints
    # root-relative paths; run from docs/orchestration/ the first version failed to open every file,
    # skipped each one silently, and printed PASS on 13 files it never read (review #11b).
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    if not root:
        print("[gfm-tables] CANNOT LOOK :: not inside a git work tree"); return 2
    here = os.getcwd()
    args = [os.path.relpath(os.path.abspath(a), root) for a in args]
    os.chdir(root)
    named = bool(args)
    # -z: `.split()` on newline output silently dropped every changed file with a space in its name
    files = args or [f for f in subprocess.run(
        ["git", "diff", "--name-only", "-z", base], capture_output=True, text=True
    ).stdout.split("\0") if f.endswith(".md")]
    if MarkdownIt is None:
        print("[gfm-tables] CANNOT LOOK :: markdown-it-py is not installed"); return 2
    if not files:
        print("[gfm-tables] CANNOT LOOK :: no files"); return 2
    total, unread = 0, []
    for f in files:
        if not os.path.exists(f):
            if named:          # a NAMED file that is not there was never read: that is not a pass
                unread.append(f)
            continue           # default mode: deleted in range, nothing to render
        if not os.path.isfile(f):
            unread.append(f); continue
        found, err = sweep(f)
        if err:
            unread.append(f); continue
        for ln, kind, why in found:
            total += 1
            print(f"  {kind:12s} {f}:{ln}  {why}")
    if unread:
        print(f"[gfm-tables] CANNOT LOOK :: could not read {unread} -- refusing rather than passing them")
        return 2
    print(f"\n[gfm-tables] {'FAIL' if total else 'PASS'} :: {total} defect(s) in {len(files)} file(s)")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
