#!/usr/bin/env python3
"""Write the label map of the short methods paper and its Supplement: each \\label, its document, its printed number
and its kind, read from the .aux files of a build, for the result package (limitation-resolver), which keys its
entries by label, not by number.

usage: make_label_map.py <paper.aux> <supplement.aux> <out.tsv>
Only labels the paper or the Supplement defines are listed; the note's labels (N-...) are not."""
import re
import sys
from pathlib import Path

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


def main(argv):
    pa, sa, out = argv
    rows = ["label\tdocument\tprinted\tkind"]
    for doc, aux in (("paper", pa), ("supplement", sa)):
        for lab, num in sorted(labels(aux).items(), key=lambda x: x[0]):
            kind = next((k for p, k in KIND if lab.startswith(p)), "other")
            if doc == "supplement" and kind == "table" and not num.startswith("S"):
                num = "S" + num
            rows.append(f"{lab}\t{doc}\t{num}\t{kind}")
    Path(out).write_text("\n".join(rows) + "\n")
    print(f"wrote {out}: {len(rows) - 1} labels")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
