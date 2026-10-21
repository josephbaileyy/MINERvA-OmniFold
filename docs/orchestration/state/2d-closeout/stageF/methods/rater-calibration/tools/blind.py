"""Blind a pdftotext dump: keep abstract + body, drop front matter, acknowledgments, references.

usage: python3 -I blind.py IN OUT --start REGEX [--refs REGEX] [--cut START END]... [--drop REGEX]...
  --start  first kept line (the abstract's first line); everything before it is dropped.
  --refs   first line of the reference list; it and everything after are dropped, except
           sections named with --keep-after (e.g. appendices placed after the references).
  --cut    drop from the line matching START up to (not including) the line matching END.
  --drop   drop any single line matching REGEX (stamps, DOIs, page numbers, e-mail footnotes).
Generic drops always applied: arXiv stamps, DOI lines, PACS lines, bare page numbers.
Every removed block is reported so the cut can be audited.
"""
import argparse
import re
import sys

GENERIC = [r"^\s*arXiv:\d{4}\.\d{4,5}(v\d+)?\b.*$", r"(?i)^\s*(doi|https?://doi\.org)\S*.*$",
           r"(?i)^\s*PACS\b.*$"]


def first(lines, rx, lo=0):
    for i in range(lo, len(lines)):
        if re.search(rx, lines[i]):
            return i
    sys.exit(f"FAIL: no line matches {rx!r} at or after line {lo + 1}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--start", required=True); ap.add_argument("--start-after", action="store_true",
                    help="keep from the line AFTER the --start match"); ap.add_argument("--refs")
    ap.add_argument("--keep-after", action="append", default=[], nargs=2, metavar=("START", "END"))
    ap.add_argument("--cut", action="append", default=[], nargs=2)
    ap.add_argument("--drop", action="append", default=[])
    a = ap.parse_args()
    text = open(a.inp, encoding="utf-8").read()
    # page numbers: a bare number on the first line of a page, or the last non-blank line before a page break
    text, n1 = re.subn(r"\f[ \t]*\d{1,3}[ \t]*\n", "\f\n", text)
    text, n2 = re.subn(r"\n[ \t]*\d{1,3}[ \t]*\n(?=\s*\f)", "\n", text)
    print(f"page numbers dropped: {n1} at page top, {n2} at page bottom")
    lines = text.replace("\f", "\n").split("\n")
    keep = [True] * len(lines)
    s = first(lines, a.start) + (1 if a.start_after else 0)
    for i in range(s):
        keep[i] = False
    print(f"front matter dropped: lines 1-{s} ({' | '.join(l for l in lines[:s] if l.strip())[:300]})")
    if a.refs:
        r = first(lines, a.refs, s)
        saved = []
        for ks, ke in a.keep_after:
            i0 = first(lines, ks, r)
            i1 = first(lines, ke, i0 + 1) if ke != "EOF" else len(lines)
            saved.append((i0, i1))
        for i in range(r, len(lines)):
            if not any(i0 <= i < i1 for i0, i1 in saved):
                keep[i] = False
        print(f"references dropped from line {r + 1} ({lines[r][:80]!r}); kept after refs: {saved}")
    for cs, ce in a.cut:
        i0 = first(lines, cs, s)
        i1 = first(lines, ce, i0 + 1) if ce != "EOF" else len(lines)
        for i in range(i0, i1):
            keep[i] = False
        print(f"cut lines {i0 + 1}-{i1}: {' '.join(lines[i0:i1])[:200]!r}...")
    nd = 0
    for i, l in enumerate(lines):
        if keep[i] and any(re.search(rx, l) for rx in GENERIC + a.drop):
            keep[i] = False; nd += 1
            print(f"  drop line {i + 1}: {l[:100]!r}")
    out = "\n".join(l for i, l in enumerate(lines) if keep[i])
    out = re.sub(r"\n{3,}", "\n\n", out).strip() + "\n"
    open(a.out, "w", encoding="utf-8").write(out)
    print(f"single-line drops: {nd}; words in={len(' '.join(lines).split())} out={len(out.split())}")


if __name__ == "__main__":
    main()
