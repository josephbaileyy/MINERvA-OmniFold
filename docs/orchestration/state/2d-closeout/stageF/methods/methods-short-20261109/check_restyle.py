#!/usr/bin/env python3
"""Check a restyled paper_body.tex / main_paper.tex against the base, so that a wording-only pass moves no claim.

usage: check_restyle.py <base-dir> <new-dir>     (each holds paper_body.tex and main_paper.tex; exit 1 on any failure)

Refuses, per file, any change to (comments stripped):
  - the multiset of \\fvval keys, of (\\fvcase key, class) pairs, and of \\fvgroup / \\fvgroupalt groups;
  - the multiset of \\cite keys, and the sets of \\label and \\ref targets (any \\ref-like macro);
  - every numeral the file prints (check_round.numerals): a numeral may not appear or disappear;
  - every other macro name used (a dropped or added \\pubhold, \\SI, \\ssec... is reported);
  - the protected text: Data availability (from its \\section* to the next \\section or \\end), the B0 sentences
    (DECISION-20261106-joseph-b0-reconciliation-sentence.md; paper_body's sec:cov5d sentences 3-5), RS1's licensed
    paragraph (the mechanism study), and every make_values LISTED_CLAIMS anchor and check_round ONCE sentence.
It reports, without failing, the sentences that changed, for the claim-by-claim read.
"""
import importlib.util
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cr = load(HERE / "check_round.py", "check_round")


def strip(t):
    return cr.strip_comments(t)


def inventory(t):
    s = strip(t)
    return {
        "fvval": Counter(re.findall(r"\\fvval\{([^}]+)\}", s)),
        "fvcase": Counter((k, c) for _, _, (k, c, _) in cr.macro_calls(s, "fvcase", 3)),
        "fvgroup": Counter(a[0] for _, _, a in cr.macro_calls(s, "fvgroup", 2)),
        "fvgroupalt": Counter(a[0] for _, _, a in cr.macro_calls(s, "fvgroupalt", 3)),
        "cite": Counter(k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", s) for k in c.split(",")),
        "label": Counter(re.findall(r"\\label\{([^}]+)\}", s)),
        "ref": Counter(re.findall(r"\\(?:ref\*?|eqref|nsec|napp|ssecc?|stab)\{([^}]+)\}", s)),
        "numerals": Counter(cr.numerals(t)),
        "macros": Counter(re.findall(r"\\([A-Za-z]+)", s)),
    }


def protected(base_main, base_body):
    """The protected spans, taken from the base so that the new files must contain them verbatim."""
    spans = []
    m = re.search(r"\\section\*\{Data availability\}.*?(?=\\section|\\end\{document\}|\\bibliography)", base_main, re.S)
    if m:
        spans.append(("Data availability", strip(m.group(0)).strip()))
    body = strip(base_body)
    i = body.find("The training-seed block of section~\\ref{sec:cov16} is zero because")
    j = body.find("not the typical one.", i)
    if i >= 0 and j > i:
        spans.append(("the B0 sentences", body[i:j + len("not the typical one.")]))
    i = body.find("A study of the mechanism specified in advance")
    j = body.find("\n", i)
    if i >= 0:
        spans.append(("RS1's paragraph", body[i:j].strip()))
    return spans


def anchors():
    mv = load(ROOT / "docs/analysis-note/make_values_fived16.py", "mv")
    out = []
    for c in getattr(mv, "LISTED_CLAIMS", []):
        a = c[1] if isinstance(c, (tuple, list)) and c[0] in ("paper_body.tex", "main_paper.tex") else None  # (file, anchor, kind)
        if isinstance(a, str):
            out.append(a)
    return out


def sentences(t):
    s = re.sub(r"\s+", " ", strip(t))
    return set(x.strip() for x in re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", s) if len(x.strip()) > 20)


def main(argv):
    base, new = Path(argv[1]), Path(argv[2])
    fails, report = [], []
    for f in ("paper_body.tex", "main_paper.tex"):
        b, n = (base / f).read_text(), (new / f).read_text()
        ib, inn = inventory(b), inventory(n)
        for k in ib:
            if ib[k] != inn[k]:
                lost, added = ib[k] - inn[k], inn[k] - ib[k]
                fails.append(f"{f}: {k} changed; lost {dict(lost)}; added {dict(added)}")
        sb, sn = sentences(b), sentences(n)
        report.append(f"{f}: {len(sb - sn)} sentences changed or removed, {len(sn - sb)} new")
    bm, bb = (base / "main_paper.tex").read_text(), (base / "paper_body.tex").read_text()
    nm, nb = strip((new / "main_paper.tex").read_text()), strip((new / "paper_body.tex").read_text())
    for name, span in protected(bm, bb):
        if span not in nm and span not in nb:
            fails.append(f"protected text changed: {name}")
    for a in anchors():
        if a not in nm and a not in nb:
            fails.append(f"a LISTED_CLAIMS anchor is gone: {a!r}")
    for s in cr.ONCE:
        if (nm + nb).count(s) != 1:
            report.append(f"ONCE sentence not printed exactly once (update check_round.ONCE if the change is approved): {s[:70]!r}")
    for r in report:
        print("REPORT", r)
    for x in fails:
        print("FAIL", x)
    print("CHECK-RESTYLE ::", "PASS" if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
