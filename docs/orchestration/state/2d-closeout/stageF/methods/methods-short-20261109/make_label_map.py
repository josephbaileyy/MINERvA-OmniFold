#!/usr/bin/env python3
"""Write the label map of the short methods paper and its Supplement: each \\label, its document, its printed number
and its kind, read from the .aux files of a build, for the result package (limitation-resolver), which keys its
entries by label, not by number.

usage: make_label_map.py <paper.aux> <supplement.aux> <out.tsv>   map an existing build's .aux files
       make_label_map.py                                             build the paper and the Supplement, write label-map.tsv
       make_label_map.py --check                                     exit 1 unless label-map.tsv is what a fresh build gives
Only labels the paper or the Supplement defines are listed; the note's labels (N-...) are not.

--check (2026-11-16, the director, from limitation-resolver's RP45, #1188): the map had gone stale since e3b99c82b (8 of
the 14 labels #981 names differed from a fresh build), so the draft's gate runs it, as make_paper_labels.py --check."""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTE = HERE.parents[5] / "analysis-note"
MAP = HERE / "label-map.tsv"

KIND = [("tab:", "table"), ("fig:", "figure"), ("eq:", "equation"), ("app:", "section"), ("sec:", "section"),
        ("supp:", "section")]


def labels(aux):
    out = {}
    for m in re.finditer(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", Path(aux).read_text(errors="replace")):
        lab, num = m.group(1), m.group(2)
        if lab.startswith("N-") or lab.endswith("@cref") or lab == "LastBibItem" or not num:
            continue
        out[lab] = num
    return out


def render(pa, sa):
    rows = ["label\tdocument\tprinted\tkind"]
    for doc, aux in (("paper", pa), ("supplement", sa)):
        for lab, num in sorted(labels(aux).items(), key=lambda x: x[0]):
            kind = next((k for p, k in KIND if lab.startswith(p)), "other")
            if doc == "supplement" and kind == "table" and not num.startswith("S"):
                num = "S" + num
            rows.append(f"{lab}\t{doc}\t{num}\t{kind}")
    return "\n".join(rows) + "\n"


def build():
    """The map of a fresh build of main_paper.tex and main_supplement.tex from the tracked files of the analysis note."""
    files = subprocess.run(["git", "ls-files", "-z", "."], cwd=NOTE, capture_output=True, check=True).stdout.split(b"\0")
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for f in (x.decode() for x in files if x):
            src = NOTE / f
            if src.is_file():
                (d / f).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, d / f)
        for doc in ("main_paper.tex", "main_supplement.tex"):
            r = subprocess.run(["latexmk", "-pdf", "-g", "-interaction=nonstopmode", "-halt-on-error", doc],
                               cwd=d, capture_output=True, text=True, errors="replace")
            if r.returncode != 0:
                sys.exit(f"make_label_map: {doc} did not build (rc {r.returncode})\n" + r.stdout[-1500:])
        return render(d / "main_paper.aux", d / "main_supplement.aux")


def main(argv):
    if argv == ["--check"]:
        text, cur = build(), (MAP.read_text() if MAP.exists() else "")
        if cur != text:
            diff = [l for l in text.splitlines() if l not in cur.splitlines()][:8]
            print(f"LABEL-MAP :: FAIL: {MAP.name} is not what a fresh build gives; rerun make_label_map.py. First fresh "
                  f"rows absent from the committed map: {diff}")
            return 1
        print(f"LABEL-MAP :: PASS: {MAP.name} equals a fresh build ({text.count(chr(10)) - 1} labels)")
        return 0
    if not argv:
        text = build()
        MAP.write_text(text)
        print(f"LABEL-MAP :: wrote {MAP.name}: {text.count(chr(10)) - 1} labels")
        return 0
    pa, sa, out = argv
    text = render(pa, sa)
    Path(out).write_text(text)
    print(f"wrote {out}: {text.count(chr(10)) - 1} labels")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
