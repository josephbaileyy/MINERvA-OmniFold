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
  (Earlier versions documented `trailing-cell` and `orphan-tail`; both are now covered by `cells`
  and `torn-row`, because GFM runs a table to the next blank line rather than to the first line
  without a pipe.)

Usage:  probe-20260922-gfm-table-integrity.py [FILE ...]   (default: every .md changed since
        177af61b). Exit 0 clean, 1 defects found, 2 cannot look. `--since REV` changes the base.
"""
import os
import re
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
    lines = src.splitlines()
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
                for span in re.findall(r"`[^`]*`", raw):
                    if re.search(r"(?<!\\)\|", span):
                        out.append((ln + 1, "codespan-pipe", f"unescaped pipe in {span[:40]}"))
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
    # a header + delimiter pair that the parser did NOT turn into a table
    for ln in range(len(lines) - 1):
        if ln in code or ln in tabled:
            continue
        if "|" in lines[ln] and SEP.match(lines[ln + 1]) and not SEP.match(lines[ln]):
            out.append((ln + 1, "header-mismatch",
                        f"header has {len(cells(lines[ln]))} cells, delimiter {len(cells(lines[ln + 1]))}: "
                        "GFM does NOT render a table here"))
    return out, None


def main():
    args = sys.argv[1:]
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
