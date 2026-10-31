#!/usr/bin/env python3
"""The number probe of Option B (DECISION-20261031-joseph-chi2-table-option-b.md item 3): every printed number of a
table is its macro.

usage: python3 -I check_table_macros.py TEX LABEL VALUES PDF [--allow TEXT ...] [--self-test]
  1. In the source of the table with \\label{LABEL} in TEX, after removing each \\fvval{...}, the LaTeX structure
     (\\begin{tabular}{...}, \\multicolumn{N}, \\cmidrule(..){a-b}, \\label, \\caption's math subscripts) and every
     --allow text (e.g. "All 16 cells"), no digit may remain.
  2. The rendered table (pdftotext -layout of PDF, from the first --allow text, which must print once, to the first
     later line holding the last row's label and numbers) prints, in order, exactly the values VALUES gives the table's
     numeric \\fvval{} macros, in source order.
Exit 0 and print TABLE-MACROS :: PASS only if both hold. --self-test plants a typed number in the source and a changed
value in the rendering, each of which must fail, and checks the unplanted inputs pass."""
import re
import subprocess
import sys
from pathlib import Path


def table_src(tex, label):
    for m in re.finditer(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", tex, re.S):
        if "\\label{" + label + "}" in m.group(0):
            return m.group(0)
    raise SystemExit(f"no table with \\label{{{label}}}")


def values(vtex):
    return dict(re.findall(r"\\@namedef\{fv@([^}]*)\}\{([^}]*)\}", vtex))


def stray_digits(src, allow):
    body = src[src.index("\\begin{tabular}"):]
    s = re.sub(r"\\fvval\{[^}]*\}", "", body)
    s = re.sub(r"\\begin\{tabular\}\{[^}]*\}", "", s)
    s = re.sub(r"\\multicolumn\{\d+\}", "", s)
    s = re.sub(r"\\cmidrule(\([a-z]*\))?\{\d+-\d+\}", "", s)
    s = re.sub(r"_\{[^}]*\}", "", s)
    s = re.sub(r"\^\{?\d+\}?", "", s)  # math superscripts, as in $\chi^2$
    for a in allow:
        s = s.replace(a, "")
    return re.findall(r"\d+(?:\.\d+)?", s)


def numeric_macros(src, vals):
    body = src[src.index("\\begin{tabular}"):]
    out = []
    for k in re.findall(r"\\fvval\{([^}]*)\}", body):
        v = vals.get(k)
        if v is None:
            raise SystemExit(f"macro {k} not in the values file")
        if re.fullmatch(r"-?\d+(?:\.\d+)?", v):
            out.append((k, v))
    return out


def rendered_numbers(text, anchor, last_label):
    lines = text.splitlines()
    # the table starts at its own first block label (an --allow text found nowhere else) and ends at the first line
    # after it that holds the last row's label with numbers
    starts = [n for n, l in enumerate(lines) if anchor in l]
    if len(starts) != 1:
        raise SystemExit(f"anchor {anchor!r} printed {len(starts)} times; it must print once")
    i = starts[0]
    j = next(n for n, l in enumerate(lines) if n > i and last_label in l and re.search(r"\d", l.replace(last_label, "")))
    block = "\n".join(lines[i:j + 1])
    for lab in ("GENIE 2.12.10", "NuWro 21.09", "GiBUU 2019", "MINERvA Tune v1", "2.12.10", "21.09", "2019"):
        block = block.replace(lab, "")
    block = re.sub(r"All 16 cells|8-cell subset:?", "", block)
    return re.findall(r"-?\d+(?:\.\d+)?", block)


def check(src, vals, text, allow):
    fails = []
    s = stray_digits(src, allow)
    if s:
        fails.append(f"typed number(s) in the table source, outside a macro: {s}")
    want = [v for _, v in numeric_macros(src, vals)]
    labels = re.findall(r"\\fvval\{(label-[^}]*)\}", src)
    shown = lambda k: vals[k].replace("~", " ")  # a label macro's text as rendered
    got = rendered_numbers(text, allow[0], shown(labels[-1]))
    if got != want:
        fails.append(f"rendered numbers differ from their macros: printed {got}, macros {want}")
    return fails


def main():
    a = sys.argv[1:]
    tex, label, vfile, pdf = a[0], a[1], a[2], a[3]
    allow = [a[i + 1] for i, x in enumerate(a) if x == "--allow"]
    src = table_src(Path(tex).read_text(), label)
    vals = values(Path(vfile).read_text())
    text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    if "--self-test" in a:
        ok = not check(src, vals, text, allow)
        planted_src = src.replace("\\\\\n", " 99 \\\\\n", 1)
        ok &= bool(check(planted_src, vals, text, allow))
        k, v = numeric_macros(src, vals)[0]
        at = text.index(allow[0])  # plant inside the table's own block, not at an earlier mention of the same value
        planted_text = text[:at] + text[at:].replace(v, v + "1", 1)
        ok &= bool(check(src, vals, planted_text, allow))
        print("TABLE-MACROS SELF-TEST ::", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    fails = check(src, vals, text, allow)
    for f in fails:
        print("  FAIL", f)
    n = len(numeric_macros(src, vals))
    print("TABLE-MACROS ::", "PASS" if not fails else "FAIL", f"({label}: {n} numbers, each its macro)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
