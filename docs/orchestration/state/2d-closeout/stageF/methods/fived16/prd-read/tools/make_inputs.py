"""Build the blind rater inputs for the PRD-language read: plain text of the paper's new 5D subsections (Part 1) and
of its changed sentences (Part 2), every \\fvval resolved and every \\ref numbered from the built paper's .aux.
usage: make_inputs.py <analysis-note dir> <out dir>"""
import re
import sys

A, OUT = sys.argv[1:3]
vals = dict(re.findall(r"\\@namedef\{fv@([^}]*)\}\{(.*)\}$", open(A + "/values_fived16.tex").read(), re.M))
refs = dict(re.findall(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", open(A + "/main_paper.aux").read()))
refs = {k: v.replace("\\,", " ") for k, v in refs.items()}
nrefs = dict(re.findall(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", open(A + "/main_note.aux").read()))
newcmd = {}
for f in ("values.tex", "values_inference.tex"):
    newcmd.update(re.findall(r"\\newcommand\{\\(\w+)\}\{([^{}]*)\}", open(A + "/" + f).read()))
pb = open(A + "/paper_body.tex").read()


def tex2txt(s):
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\\fvval\{([^}]*)\}", lambda m: vals[m.group(1)], s)
    s = re.sub(r",? and \\fvpending\{[^}]*\}\.", ".", s)          # the covariance export, not yet landed
    s = re.sub(r"\\fvpending\{[^}]*\}\s*", "", s)                  # the ratio figure, not yet landed
    assert "fvpending" not in s, s
    s = re.sub(r"\\nsec\{([^}]*)\}", lambda m: "Ref. [14], Sec. " + nrefs[m.group(1)], s)   # as the PDF prints it
    s = re.sub(r"\\ref\{([^}]*)\}", lambda m: refs[m.group(1)], s)
    s = re.sub(r"\\SI\{([^}]*)\}\{\\percent\}", r"\1%", s)
    s = re.sub(r"\\(zprojCells|jtNcells)\{\}|\\(zprojCells|jtNcells)\b", lambda m: newcmd[m.group(1) or m.group(2)], s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"\1", s)
    rep = [(r"\pT", "p_T"), (r"\pPar", "p_∥"), (r"\Eavail", "E_avail"), (r"C_{\mathrm{total}}", "C_total"),
           (r"C_{\mathrm{resp}}", "C_resp"), (r"C_{\mathrm{model}}", "C_model"), (r"\chi^2", "χ²"), (r"\geq", " ≥ "),
           (r"\times", " × "), (r"E_\nu", "E_ν"), (r"\sigma", "σ"), (r"\pm", "±"), (r"\,\%", " %"), (r"\%", "%"),
           (r"\,", " "), ("~", " "), ("--", "–"), ("$", ""), (r"\ ", " ")]
    for a, b in rep:
        s = s.replace(a, b)
    s = re.sub(r"10\^\{(-?\d+)\}", r"10^\1", s)
    s = re.sub(r"\s+", " ", s).strip()
    assert "\\" not in s, s
    return s


part1 = []
for m in re.finditer(r"% FIVED16-BEGIN[^\n]*\n(.*?)% FIVED16-END", pb, re.S):
    blk = re.sub(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", "", m.group(1), flags=re.S)
    for para in re.split(r"\n\s*\n", blk):
        para = re.sub(r"\\label\{[^}]*\}", "", para).strip()
        if not para or para.startswith("%"):
            continue
        h = re.match(r"\\subsection\{([^}]*)\}", para)
        if h:
            sec = refs[re.search(r"\\label\{([^}]*)\}", m.group(1)).group(1)]
            part1.append(f"{sec}. {h.group(1)}")
            para = para[h.end():].strip()
        if para:
            part1.append(tex2txt(para))

# Part 2: each changed sentence of the existing text, with the heading it sits under
SITES = [("Introduction, Scope paragraph", r"The sixteen-cell result of Sec.~\ref{sec:result16} also has total uncertainties, whose coverage is not validated."),
         ("Estimators and validation design", r"The configuration-(a) five-observable central value and its covariance use the purity-based subtraction"),
         ("Normalization and closure", r"These cells are biased by up to"),
         ("Normalization and closure", r"This bias is not included in the uncertainties quoted for the configuration-(a) central value."),
         ("Generator-sized truth changes", r"No uncertainty quoted for the configuration-(a) central value includes the regularization bias"),
         ("Generator-sized truth changes", r"For the sixteen-cell result, the model term"),
         ("Coverage, a figure caption", r"(b) Configuration (e), the joint-test estimator, for three"),
         ("Covariance and estimator stability", r"The covariance of the configuration-(a) five-observable central value"),
         ("Covariance and estimator stability", r"We therefore quote no generator significance based on this covariance"),
         ("Covariance and estimator stability", r"The seed dependence of this five-observable covariance rests on one seed pair"),
         ("Application: comparison with generator predictions", r"Unfolded results can be compared with any prediction at truth level"),
         ("Conclusions, Limitations paragraph", r"The higher-dimensional results are central values without intervals of validated coverage"),
         ("Conclusions, Limitations paragraph", r"The sixteen-cell result also has total uncertainties, whose coverage is not validated;")]
flat = re.sub(r"\s+", " ", "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in pb.splitlines()))
part2 = []
for where, start in SITES:
    i = flat.index(start); assert flat.count(start) == 1, start
    j = i
    while True:                                   # the sentence ends at the first '. ' not inside braces
        j = flat.index(". ", j + 1) if flat.find(". ", j + 1) >= 0 else len(flat)
        seg = flat[i:j + 1]
        if seg.count("{") == seg.count("}") and not re.search(r"(Sec|Secs|Fig|Figs|Eq|Ref|e\.g|i\.e)\.$", seg):
            break
    part2.append(f"[{where}] " + tex2txt(seg))

ctx_src = pb[pb.index(r"\label{sec:uncertainty-status}"):pb.index("% FIVED16-BEGIN DECISION")]
ctx_src = re.sub(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", "", ctx_src.split("\n", 1)[1], flags=re.S)
ctx = [tex2txt(q) for q in re.split(r"\n\s*\n", ctx_src) if q.strip()]
head = ("CONTEXT (not to be judged). The two paragraphs of the paper's subsection V E that precede Part 1:\n\n"
        + "\n\n".join(ctx) + "\n\n" + "PART 1. Two subsections of the paper (tables omitted).\n\n" + "\n\n".join(part1) +
        "\n\nPART 2. Sentences elsewhere in the paper that refer to the result of Part 1, each with the section it is in.\n\n"
        + "\n\n".join(part2) + "\n")
open(OUT + "/excerpt.txt", "w").write(head)
print(head)
