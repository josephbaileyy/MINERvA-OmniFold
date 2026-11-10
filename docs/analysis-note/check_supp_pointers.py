#!/usr/bin/env python3
"""Check that every pointer from the paper into the Supplemental Material prints the right number (round 5).

paper_body.tex writes \\ssec{S<n>}{<label>}, \\ssecc{S<n>}{<label>}, \\stab{S<n>}{<label>} and \\sfig{S<n>}{<label>}. The printed number is
typed, because the paper does not read the Supplement's .aux; this check makes the typed number fail loudly if the
Supplement's order changes. A section label must be the n-th \\section of supplemental_body.tex (or a \\label inside
it); a table label must be the n-th table environment's \\label, and a figure label the n-th figure's (\\sfig, the
interim round #1025 A1).

usage: check_supp_pointers.py [--self-test]     (run from docs/analysis-note)
exit 0 only if every pointer agrees and there is at least one pointer.
"""
import re
import sys


def supp_maps(body):
    body = "\n".join(re.sub(r"(?<!\\)%.*$", "", ln) for ln in body.split("\n"))
    secs, n = {}, 0
    for part in re.split(r"(?=\\section\{)", body):
        if not part.startswith("\\section{"):
            continue
        n += 1
        for lab in re.findall(r"\\label\{([^}]+)\}", part):
            secs.setdefault(lab, n)
    tabs = {}
    for k, env in enumerate(re.findall(r"\\begin\{table\}.*?\\end\{table\}", body, flags=re.S), 1):
        for lab in re.findall(r"\\label\{([^}]+)\}", env):
            tabs[lab] = k
    figs = {}
    for k, env in enumerate(re.findall(r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}", body, flags=re.S), 1):
        for lab in re.findall(r"\\label\{([^}]+)\}", env):
            figs[lab] = k
    return secs, tabs, figs


def check(paper, body):
    secs, tabs, figs = supp_maps(body)
    paper = "\n".join(re.sub(r"(?<!\\)%.*$", "", ln) for ln in paper.split("\n"))
    ptrs = re.findall(r"\\(ssecc?|stab|sfig)\{S(\d+)\}\{([^}]+)\}", paper)
    errs = []
    for kind, num, lab in ptrs:
        want = {"stab": tabs, "sfig": figs}.get(kind, secs).get(lab)
        if want is None:
            errs.append(f"{kind}{{S{num}}}{{{lab}}}: label not in the Supplement")
        elif int(num) != want:
            errs.append(f"{kind}{{S{num}}}{{{lab}}}: the Supplement numbers it S{want}")
    if not ptrs:
        errs.append("no Supplement pointer found in paper_body.tex")
    return ptrs, errs


if "--self-test" in sys.argv:
    body = ("\\section{A}\\label{supp:a}\n\\section{B}\\label{supp:b}\n\\begin{table}\\label{tab:x}\\end{table}\n"
            "\\begin{figure}\\label{fig:y}\\end{figure}\n\\begin{figure}\\label{fig:z}\\end{figure}\n")
    ok, e1 = check("\\ssec{S2}{supp:b} \\stab{S1}{tab:x} \\sfig{S2}{fig:z}", body)
    _, e5 = check("\\sfig{S1}{fig:z}", body)
    _, e6 = check("\\sfig{S1}{tab:x}", body)
    _, e2 = check("\\ssec{S1}{supp:b}", body)
    _, e3 = check("\\stab{S1}{tab:missing}", body)
    _, e4 = check("no pointers", body)
    assert not e1 and e2 and e3 and e4 and e5 and e6, (e1, e2, e3, e4, e5, e6)
    print("self-test: PASS")
    sys.exit(0)
ptrs, errs = check(open("paper_body.tex", encoding="utf-8").read(),
                   open("supplemental_body.tex", encoding="utf-8").read())
for e in errs:
    print("FAIL", e)
print(f"{len(ptrs)} Supplement pointers checked, {len(errs)} failures")
sys.exit(1 if errs else 0)
