#!/usr/bin/env python3
"""Check that every pointer from the paper into the Supplemental Material prints the right number (round 5).

paper_body.tex writes \\ssec{S<n>}{<label>}, \\ssecc{S<n>}{<label>}, \\stab{S<n>}{<label>} and \\sfig{S<n>}{<label>}. The printed number is
typed, because the paper does not read the Supplement's .aux; this check makes the typed number fail loudly if the
Supplement's order changes. A section label must be the n-th \\section of supplemental_body.tex (or a \\label inside
it); a table label must be the n-th table or xltabular environment's \\label, and a figure label the n-th figure's (\\sfig, the
interim round #1025 A1).

Content anchors (2026-11-16, the director, on a read-only Supplement pass: five pointers printed the right number into a
section that does not say what the pointer claims). ANCHORS below ties a pointer's sentence to text its target must
contain: a paper phrase that must occur exactly once, and for each (label, regex) pair the regex must match the text of
that label's own section or subsection (comments stripped, whitespace collapsed, case ignored). A row whose label is
None asserts instead that the sentence containing the phrase carries no Supplement pointer. A phrase that no longer
occurs fails, so a reworded pointer sentence must update its row.

usage: check_supp_pointers.py [--self-test]     (run from docs/analysis-note)
exit 0 only if every pointer agrees and there is at least one pointer.
"""
import re
import sys


TEXT = {}


def supp_maps(body):
    TEXT.clear()
    body = "\n".join(re.sub(r"(?<!\\)%.*$", "", ln) for ln in body.split("\n"))
    secs, n = {}, 0
    for part in re.split(r"(?=\\section\{)", body):
        if not part.startswith("\\section{"):
            continue
        n += 1
        # a label inside a subsection is numbered "n.m" (the referee recheck, 2026-11-11: the pointer pattern used to
        # match only whole numbers, so every subsection pointer such as \ssec{S9.4}{...} went unchecked)
        for m, sub in enumerate(re.split(r"(?=\\subsection\{)", part)):
            for lab in re.findall(r"\\label\{([^}]+)\}", sub):
                secs.setdefault(lab, f"{n}.{m}" if m else str(n))
                # a section's own label gets the whole section's text; a subsection's, the subsection's
                TEXT.setdefault(lab, part if (m == 0 or lab in re.findall(r"\\label\{([^}]+)\}", part.split("\\subsection{")[0])) else sub)
    tabs = {}
    # an xltabular (a table that breaks across pages, numbered as a table; Tables S9 and S10, 2026-11-12) counts in order
    envs = [m.group(0) for m in re.finditer(r"\\begin\{(table|xltabular)\}.*?\\end\{\1\}", body, flags=re.S)]
    for k, env in enumerate(envs, 1):
        for lab in re.findall(r"\\label\{([^}]+)\}", env):
            tabs[lab] = k
    figs = {}
    for k, env in enumerate(re.findall(r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}", body, flags=re.S), 1):
        for lab in re.findall(r"\\label\{([^}]+)\}", env):
            figs[lab] = k
    return secs, tabs, figs


# (paper phrase regex, [(target label, regex the target's text must contain), ...]); label None: no pointer in the sentence
ANCHORS = [
    (r"without reweighting events \(\\ssec\{S5\}\{supp:cov16\}\)", [("supp:cov16", r"beam angle"), ("supp:cov16", r"rather than reweighting")]),
    (r"universe weights too\.", [(None, None)]),
    (r"The two-dimensional covariance \(\\ssec\{S6\}\{supp:cov2d\}\) is the sum of four blocks",
     [("supp:cov2d", r"systematic-universe, statistical, training-seed and run-period blocks")]),
    (r"the dependence on the regularization", [(None, None)]),
    (r"called the joint cells \(\\ssec\{S8\.7\}\{supp:joint\}\)", [("supp:joint", r"support rule")]),
    (r"contribute only to the total", [(None, None)]),
    # The hold's ensemble-average row (S4.4 and S8) moved with the record inventory to the cover sheet HOLD-INVENTORY.md
    # (the director, relaying Joseph 2026-11-16); check_hold_inventory.py's ANCHORS ties it to its targets.
]


def check_anchors(paper, anchors=None):
    """Errors for ANCHORS rows: a phrase not found exactly once, a target lacking its text, or a pointer where none belongs."""
    errs = []
    flat = re.sub(r"\s+", " ", paper)
    for phrase, wants in (ANCHORS if anchors is None else anchors):
        hits = list(re.finditer(phrase, flat))
        if len(hits) != 1:
            errs.append(f"anchor /{phrase}/: found {len(hits)} times in the paper, not once (reworded? update its row)")
            continue
        for lab, rx in wants:
            if lab is None:
                h = hits[0]
                s0 = max(flat.rfind(". ", 0, h.start()), 0)
                s1 = h.end() if flat[h.end() - 1] == "." else flat.find(". ", h.end())  # a phrase may end its sentence
                sent = flat[s0:s1 if s1 >= 0 else len(flat)]
                if re.search(r"\\(ssecc?|stab|sfig)\{", sent):
                    errs.append(f"anchor /{phrase}/: its sentence carries a Supplement pointer, and none belongs there")
                continue
            body = re.sub(r"\s+", " ", TEXT.get(lab, ""))
            if not body:
                errs.append(f"anchor /{phrase}/: target {lab} has no text in the Supplement")
            elif not re.search(rx, body, flags=re.I):
                errs.append(f"anchor /{phrase}/: target {lab} does not contain /{rx}/")
    return errs


def check(paper, body, anchors=()):
    secs, tabs, figs = supp_maps(body)
    paper = "\n".join(re.sub(r"(?<!\\)%.*$", "", ln) for ln in paper.split("\n"))
    ptrs = re.findall(r"\\(ssecc?|stab|sfig)\{S(\d+(?:\.\d+)?)\}\{([^}]+)\}", paper)
    errs = []
    for kind, num, lab in ptrs:
        want = {"stab": tabs, "sfig": figs}.get(kind, secs).get(lab)
        if want is None:
            errs.append(f"{kind}{{S{num}}}{{{lab}}}: label not in the Supplement")
        elif (num != want if kind in ("ssec", "ssecc") else int(num) != want):
            errs.append(f"{kind}{{S{num}}}{{{lab}}}: the Supplement numbers it S{want}")
    if not ptrs:
        errs.append("no Supplement pointer found in paper_body.tex")
    return ptrs, errs + check_anchors(paper, anchors)


if "--self-test" in sys.argv:
    body = ("\\section{A}\\label{supp:a}\n\\section{B}\\label{supp:b}\n\\subsection{B1}\\label{supp:b1}\n\\subsection{B2}\\label{supp:b2}\n"
            "\\begin{table}\\label{tab:x}\\end{table}\n"
            "\\begin{figure}\\label{fig:y}\\end{figure}\n\\begin{figure}\\label{fig:z}\\end{figure}\n")
    _, s1 = check("\\ssec{S2.2}{supp:b2}", body)
    _, s2 = check("\\ssec{S2.1}{supp:b2}", body)
    assert not s1 and s2, (s1, s2)
    ok, e1 = check("\\ssec{S2}{supp:b} \\stab{S1}{tab:x} \\sfig{S2}{fig:z}", body)
    _, e5 = check("\\sfig{S1}{fig:z}", body)
    _, e6 = check("\\sfig{S1}{tab:x}", body)
    _, e2 = check("\\ssec{S1}{supp:b}", body)
    _, e3 = check("\\stab{S1}{tab:missing}", body)
    _, e4 = check("no pointers", body)
    assert not e1 and e2 and e3 and e4 and e5 and e6, (e1, e2, e3, e4, e5, e6)
    body2 = ("\\begin{table}\\label{tab:a}\\end{table}\n\\begin{xltabular}{x}{y}\\caption{c}\\label{tab:b}\\\\ r \\end{xltabular}\n"
             "\\begin{table}\\label{tab:c}\\end{table}\n")
    _, e7 = check("\\stab{S2}{tab:b} \\stab{S3}{tab:c}", body2)
    _, e8 = check("\\stab{S2}{tab:c}", body2)
    assert not e7 and e8, (e7, e8)
    # content anchors (2026-11-16): a target that holds the text passes; one that lacks it, a reworded phrase, and a
    # pointer in a sentence that must carry none each fail
    body3 = "\\section{A}\\label{supp:a}\nThe beam angle is shifted.\n\\section{B}\\label{supp:b}\nNothing here.\n"
    an = [(r"shifts \(\\ssec\{S1\}\{supp:a\}\)", [("supp:a", r"beam angle")])]
    _, a1 = check("It shifts (\\ssec{S1}{supp:a}).", body3, an)
    _, a2 = check("It shifts (\\ssec{S1}{supp:a}).", body3, [(an[0][0], [("supp:b", r"beam angle")])])
    _, a3 = check("It moves (\\ssec{S1}{supp:a}).", body3, an)
    neg = [(r"carry weights too\.", [(None, None)])]
    _, a4 = check("They carry weights too. Next (\\ssec{S1}{supp:a}).", body3, neg)
    _, a5 = check("They carry weights too (\\ssec{S1}{supp:a}). Next.", body3, [(r"carry weights too", [(None, None)])])
    assert not a1 and a2 and a3 and not a4 and a5, (a1, a2, a3, a4, a5)
    print("self-test: PASS")
    sys.exit(0)
ptrs, errs = check(open("paper_body.tex", encoding="utf-8").read(),
                   open("supplemental_body.tex", encoding="utf-8").read(), ANCHORS)
for e in errs:
    print("FAIL", e)
print(f"{len(ptrs)} Supplement pointers checked, {len(ANCHORS)} content anchors, {len(errs)} failures")
sys.exit(1 if errs else 0)
