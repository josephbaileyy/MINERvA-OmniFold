"""Build prd-read/r5/input.txt, step (c)'s 1A sentences: OLD from BASE (git show), NEW from the worktree, every
\\fvval{key} resolved from values_fived16.tex and every \\ref from the builds' .aux files. Nothing is typed by hand.
usage: python3 make_r5.py <worktree> <base-rev> <out>"""
import re, subprocess, sys
W, BASE, out = sys.argv[1], sys.argv[2], sys.argv[3]
A = f"{W}/docs/analysis-note"
vals = dict(re.findall(r"\\@namedef\{fv@([^}]*)\}\{([^}]*)\}", open(f"{A}/values_fived16.tex").read()))
labs = {}
for aux in ("main_note.aux", "main_paper.aux"):   # paper labels win: the paper's items use the paper's numbering
    labs.update(re.findall(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", open(f"{A}/{aux}", encoding="latin-1").read()))


def strip(s):
    return re.sub(r"\s+", " ", "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in s.splitlines()))


def cur(f):
    return strip(open(f"{A}/{f}").read())


def base(f):
    return strip(subprocess.run(["git", "-C", W, "show", f"{BASE}:docs/analysis-note/{f}"], capture_output=True,
                                text=True, check=True).stdout)


def plain(t):
    t = re.sub(r"\\fvval\{([^}]*)\}", lambda m: vals[m.group(1)], t)
    t = re.sub(r"\\ref\{([^}]*)\}", lambda m: labs[m.group(1)].replace("\\,", " "), t)
    for a, b in [(r"$\chi^2$", "χ²"), (r"$\chi^{2}$", "χ²"), (r"$C_{\mathrm{model}}$", "C_model"), (r"$q_{3}$", "q3"), (r"\chi^2", "χ²"), (r"\leq", "≤"),
                 (r"\_", "_"), (r"\sigma", "σ"), (r"\emph{", "{"), (r"\texttt{", "{"), (r"\S", "§"), ("~", " "), ("--", "–"), (r"\%", "%")]:
        t = t.replace(a, b)
    t = re.sub(r"\$([^$]*)\$", r"\1", t).replace("{", "").replace("}", "")
    return t


def para(t, start, end):
    i = t.find(start); j = t.find(end, i)
    assert i >= 0 and j > i, (start, end)
    return t[i:j + len(end)]


P, Pb = cur("paper_body.tex"), base("paper_body.tex")
MP, MPb = cur("main_paper.tex"), base("main_paper.tex")
MN, MNb = cur("main_note.tex"), base("main_note.tex")
N = cur("sec_fived16.tex")
l1o = para(Pb, "The coverage of its intervals has not been validated", "synthetic $q_{3}$ tilt (Sec.~\\ref{sec:result16}).")
# after the round (the forms applied), the same items as they now print: "applied" mode, for agy's second pass
l1s = "The coverage of its intervals has not been validated" if "The coverage of its intervals" in P else "Interval coverage has not been validated"
l1n = para(P, l1s, "synthetic $q_{3}$ tilt (Sec.~\\ref{sec:fd16}).")
a1o = para(MPb, "The coverage of the intervals has not been validated", ".")
a1n = para(MP, "The coverage of the intervals has not been validated", ".")   # the sentence: no period inside it
a2o = para(MNb, "The coverage of the result's intervals has not been validated", ".")
a2n = para(MN, "The coverage of the result's intervals has not been validated", ".")   # the sentence: no period inside it
h1 = (para(P, "Two truths are held out:", "the width of the intervals.") if "Two truths are held out:" in P
      else para(P, "Two GENIE~v3 tunes,", "so interval widths cannot be tested."))
h2 = para(N, "Two truths are held out of the analysis:", "the detector response is not probed.")
p02 = para(P, "The validation studies assess the result", "generator-sized amounts.")
# P02's OLD is round 4's, the pre-round-3 text, read from r4's committed input rather than retyped
p02_old = re.search(r"^P02 \(paper\)\. OLD: (.*)$", open(f"{W}/docs/orchestration/state/2d-closeout/stageF/methods/fived16/prd-read/r4/input.txt").read(), re.M).group(1)
txt = ("BACKGROUND. The paper reports a sixteen-cell, five-observable neutrino cross section with a covariance. Its "
       "intervals' coverage has not been validated. A new study unfolded pseudo-data at two GENIE v3 tunes that no part "
       "of the analysis used, to test the estimator's bias against the reported covariance; it is a bias test, not a "
       "coverage test. The items below add its result. L1 is a sentence of the paper's introduction, A1 and A2 the "
       "paper's and the note's abstract sentence, H1 a new paragraph of the paper's fake-data section (OLD: none) and H2 "
       "the note's (OLD: none). P02 is an earlier rewording of a sentence of the paper's introduction, as it now prints.\n\n"
       f"L1 (paper). OLD: {plain(l1o)}\nNEW: {plain(l1n)}\n\n"
       f"A1 (paper abstract). OLD: {plain(a1o)}\nNEW: {plain(a1n)}\n\n"
       f"A2 (note abstract). OLD: {plain(a2o)}\nNEW: {plain(a2n)}\n\n"
       f"H1 (paper). OLD: (none)\nNEW: {plain(h1)}\n\n"
       f"H2 (note). OLD: (none)\nNEW: {plain(h2)}\n\n"
       f"P02 (paper). OLD: {p02_old}\nNEW: {plain(p02)}\n")
left = [m for m in re.findall(r"\\\w+", txt)]
assert "\\fvval" not in txt and not left, left[:5]
open(out, "w").write(txt)
print(len(txt.split()), "words")
