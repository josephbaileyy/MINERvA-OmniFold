"""Build prd-read/r4/input.txt from the committed sources: every \\fvval{key} resolved from values_fived16.tex, the
LaTeX lightly converted. Nothing is typed by hand (an earlier hand-typed draft got two numbers wrong).
usage: python3 make_r4.py <worktree> <out>"""
import re, sys
W, out = sys.argv[1], sys.argv[2]
A = f"{W}/docs/analysis-note"
vals = dict(re.findall(r"\\@namedef\{fv@([^}]*)\}\{([^}]*)\}", open(f"{A}/values_fived16.tex").read()))
def src(f): return re.sub(r"\s+", " ", "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in open(f"{A}/{f}").read().splitlines()))
def plain(t):
    t = re.sub(r"\\fvval\{([^}]*)\}", lambda m: vals[m.group(1)], t)
    for a, b in [(r"$\chi^2$", "χ²"), (r"$\chi^2\geq", "χ² ≥ "), (r"\,\%", "%"), (r"\%", "%"), (r"~", " "), (r"--", "–"), (r"$\alpha$", "α"),
                 (r"\cite{MINERvA:2016iqn}", "[16]"), (r"\S\ref{sec:fived16-cov}", "§10.2")]:
        t = t.replace(a, b)
    labs = dict(re.findall(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", open(f"{A}/main_note.aux", encoding="latin-1").read()))
    t = re.sub(r"\\ref\{([^}]*)\}", lambda m: labs[m.group(1)], t)      # numbers from the build's .aux, not typed
    t = re.sub(r"\$([^$]*)\$", r"\1", t)
    return t.replace("$", "")              # an unpaired delimiter left by the inequality's replacement
def para(f, start, end):
    t = src(f); i = t.find(start); j = t.find(end, i)
    assert i >= 0 and j > i, (f, start)
    return t[i:j + len(end)]
pa = para("paper_body.tex", "Weakening only the flux correlations", "under the true correlations.")
na = para("sec_fived16.tex", "Weakening only the flux correlations", "under the true correlations.")
cut_p, cut_n = pa.find(" The flux correlations are themselves"), na.find(" The flux correlations are themselves")
p02 = para("paper_body.tex", "The validation studies assess the result", "generator-sized amounts.")
p02_old = ("The validation studies show how far the result can be trusted: the two-dimensional reproduction, the background "
           "subtraction, the recovery of generator-sized truth changes, a coverage test and a fake-data study of the "
           "estimator's bias. They ask whether the unfolding gives reliable multidimensional cross sections when the "
           "simulation mismodels the truth by generator-sized amounts.")   # the pre-round-3 text (prd-read/r3/agy/pairs.txt Q1 BEFORE)
txt = ("BACKGROUND. The paper reports a sixteen-cell, five-observable neutrino cross section with a covariance and compares "
       "five generator predictions with it through chi-squared. A new study rebuilt the covariance's flux block from bootstrap "
       "replicates of the 100 flux universes from which the flux correlations are estimated; the passages below add its result "
       "after an existing sensitivity paragraph. D1 is the paper's paragraph and D2 the note's; P02 is an earlier rewording of "
       "a sentence of the paper's introduction.\n\n"
       f"D1 (paper). OLD: {plain(pa[:cut_p])}\nNEW: {plain(pa)}\n\n"
       f"D2 (note). OLD: {plain(na[:cut_n])}\nNEW: {plain(na)}\n\n"
       f"P02 (paper). OLD: {p02_old}\nNEW: {plain(p02)}\n")
assert "\\fvval" not in txt and "\\" not in txt.replace("\\ ", ""), [m for m in re.findall(r"\\\w+", txt)][:5]
open(out, "w").write(txt)
print(len(txt.split()), "words")
