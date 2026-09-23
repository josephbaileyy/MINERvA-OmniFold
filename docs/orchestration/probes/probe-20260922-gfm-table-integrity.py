#!/usr/bin/env python3
"""Sweep Markdown tables for rows GitHub-flavoured Markdown will render WRONG.

WHY THIS EXISTS. Two defects of this lane survived thirteen independent reviews and every self
round, because every check before this one read the SOURCE and none asked how it RENDERS:
  * a KNOWN_ISSUES row carried `|` inside backtick code spans. In a GFM table, backticks do NOT
    protect a pipe -- the row splits into extra cells, and GFM DISCARDS cells beyond the header's
    count, so the second half of the row (its repair note, its CHECK line and its date) silently
    vanished from the rendered table while reading perfectly in the source;
  * a BLOCKED-record row was torn across two physical lines. A table row cannot span lines, so the
    second line fell out of the table and rendered as a stray paragraph.

Checks, per GFM table (a header row followed by a delimiter row):
  codespan-pipe -- an unescaped `|` INSIDE a backtick code span. Checked independently of the
                   count, because a row one cell short PLUS a code-span pipe has exactly the
                   header's count: that pair passed a count-only check and still rendered with the
                   column boundary inside the code span (found by self-round 30).
  cell-parity  -- a cell with an odd number of backticks or of `**` (outside code spans), which
                  strands a marker and re-pairs everything after it
  header-mismatch -- the HEADER row's cell count differs from the delimiter row's. GFM then does not
                  recognise a table at all: every row below renders as plain text. (Missed by the
                  first version of this probe, which never examined the header; independent review
                  #11a found it in VALIDATION_LEDGER.md, where a code-span pipe in a header un-tabled
                  six rows.)
  cells        -- a body row whose unescaped-pipe count differs from the header's
  trailing-cell -- text AFTER a body row's last pipe. GFM reads it as one more cell than the header
                  allows and DROPS it. (The first version called this "broken-row -- continued on the
                  next line"; review #11a showed the rows in question were complete rows whose final
                  clause was silently discarded.)
  orphan-tail  -- a non-table line directly after a table that ends with `|` (a row's torn-off half)

Usage:  probe-20260922-gfm-table-integrity.py [FILE ...]   (default: every .md changed since
        177af61b). Exit 0 clean, 1 defects found, 2 cannot look. `--since REV` changes the base.
"""
import re
import subprocess
import sys

SEP = re.compile(r"^\|(\s*:?-{3,}:?\s*\|)+\s*$")


def pipes(line):
    return len(re.findall(r"(?<!\\)\|", line))


def sweep(path):
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except (FileNotFoundError, UnicodeDecodeError) as e:
        return None, str(e)
    out, i = [], 0
    while i < len(lines) - 1:
        if lines[i].startswith("|") and SEP.match(lines[i + 1]):
            n, j = pipes(lines[i]), i + 2
            if n != pipes(lines[i + 1]):
                out.append((i + 1, "header-mismatch",
                            f"header has {pipes(lines[i])} pipes, delimiter {pipes(lines[i + 1])}: "
                            "GFM will not render this as a table"))
            for span in re.findall(r"`[^`]*`", lines[i]):
                if re.search(r"(?<!\\)\|", span):
                    out.append((i + 1, "codespan-pipe", f"unescaped pipe in header {span[:40]}"))
            while j < len(lines) and lines[j].startswith("|"):
                for span in re.findall(r"`[^`]*`", lines[j]):
                    if re.search(r"(?<!\\)\|", span):
                        out.append((j + 1, "codespan-pipe", f"unescaped pipe in {span[:40]}"))
                for ci, cell in enumerate(re.split(r"(?<!\\)\|", lines[j])[1:-1]):
                    if len(re.findall(r"(?<!\\)`", cell)) % 2:
                        out.append((j + 1, "cell-parity", f"odd backticks in cell {ci}"))
                    if len(re.findall(r"(?<!\\)\*\*", re.sub(r"`[^`]*`", "", cell))) % 2:
                        out.append((j + 1, "cell-parity", f"odd ** in cell {ci}"))
                if pipes(lines[j]) != n:
                    out.append((j + 1, "cells", f"{pipes(lines[j])} pipes vs header {n}"))
                tail = re.split(r"(?<!\\)\|", lines[j])[-1].strip()
                if tail:
                    out.append((j + 1, "trailing-cell", f"text after the last pipe is dropped: {tail[:40]!r}"))
                j += 1
            if (j < len(lines) and lines[j].strip() and not lines[j].startswith("|")
                    and lines[j].rstrip().endswith("|")):
                out.append((j + 1, "orphan-tail", "line after the table ends with a pipe"))
            i = j
        else:
            i += 1
    return out, None


def main():
    args = sys.argv[1:]
    base = "177af61b"
    if "--since" in args:
        k = args.index("--since"); base = args[k + 1]; del args[k:k + 2]
    files = args or [f for f in subprocess.run(
        ["git", "diff", "--name-only", f"{base}..HEAD"], capture_output=True, text=True
    ).stdout.split() if f.endswith(".md")]
    if not files:
        print("[gfm-tables] CANNOT LOOK :: no files"); return 2
    total = 0
    for f in files:
        found, err = sweep(f)
        if err:
            continue          # deleted in range, or binary
        for ln, kind, why in found:
            total += 1
            print(f"  {kind:12s} {f}:{ln}  {why}")
    print(f"\n[gfm-tables] {'FAIL' if total else 'PASS'} :: {total} defect(s) in {len(files)} file(s)")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
