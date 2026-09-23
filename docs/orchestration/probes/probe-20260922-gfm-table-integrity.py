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

# GFM's delimiter row: optional leading/trailing pipe, each cell ":?-+:?", at least one pipe.
SEP = re.compile(r"^\s{0,3}\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$|^\s{0,3}\|\s*:?-+:?\s*\|?\s*$")
# a line that starts another block ends a GFM table; so does a blank line
BLOCK_START = re.compile(r"^\s{0,3}(#|```|~~~|>|[-*+]\s|\d+[.)]\s)")


def cells(line):
    """GFM cells: trim ONE leading and ONE trailing pipe, then split on UNESCAPED pipes.

    A pipe inside a code span still splits a cell in GFM unless it is escaped, so no special case
    for code spans is needed to COUNT cells -- only to explain why a count is wrong."""
    t = line.strip()
    if t.startswith("|"):
        t = t[1:]
    if t.endswith("|") and not t.endswith("\\|"):
        t = t[:-1]
    return re.split(r"(?<!\\)\|", t)


def sweep(path):
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except UnicodeDecodeError as e:
        return None, str(e)
    out, i = [], 0
    while i < len(lines) - 1:
        if "|" in lines[i] and SEP.match(lines[i + 1]) and not SEP.match(lines[i]):
            ncol, j = len(cells(lines[i + 1])), i + 2
            if len(cells(lines[i])) != ncol:
                out.append((i + 1, "header-mismatch",
                            f"header has {len(cells(lines[i]))} cells, delimiter {ncol}: GFM will NOT render a table"))
            for span in re.findall(r"`[^`]*`", lines[i]):
                if re.search(r"(?<!\\)\|", span):
                    out.append((i + 1, "codespan-pipe", f"unescaped pipe in header {span[:40]}"))
            # the body runs to a blank line or another block -- NOT to the first line without a pipe:
            # GFM makes a pipe-less line into a ROW (self-round 29's torn tail rendered as a new row)
            while j < len(lines) and lines[j].strip() and not BLOCK_START.match(lines[j]):
                row = lines[j]
                n = len(cells(row))
                if not row.strip().startswith("|"):
                    out.append((j + 1, "torn-row", "a line with no leading pipe inside a table renders as its own row"))
                if n > ncol:
                    out.append((j + 1, "cells", f"{n} cells under {ncol} columns: GFM DROPS the excess"))
                elif n < ncol:
                    out.append((j + 1, "cells", f"{n} cells under {ncol} columns: GFM pads with empty cells"))
                for span in re.findall(r"`[^`]*`", row):
                    if re.search(r"(?<!\\)\|", span):
                        out.append((j + 1, "codespan-pipe", f"unescaped pipe in {span[:40]}"))
                for ci, cell in enumerate(cells(row)):
                    if len(re.findall(r"(?<!\\)`", cell)) % 2:
                        out.append((j + 1, "cell-parity", f"odd backticks in cell {ci}"))
                    if len(re.findall(r"(?<!\\)\*\*", re.sub(r"`[^`]*`", "", cell))) % 2:
                        out.append((j + 1, "cell-parity", f"odd ** in cell {ci}"))
                j += 1
            i = j
        else:
            i += 1
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
    files = args or [f for f in subprocess.run(
        ["git", "diff", "--name-only", f"{base}..HEAD"], capture_output=True, text=True
    ).stdout.split() if f.endswith(".md")]
    if not files:
        print("[gfm-tables] CANNOT LOOK :: no files"); return 2
    total, unread = 0, []
    for f in files:
        if not os.path.exists(f):
            continue          # deleted in range: nothing to render
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
