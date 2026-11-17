"""The PRD-read-for-flow batch on paper_body.tex (sentence-read/README.md): local fixes, no restructure."""
import sys

p = sys.argv[1]
s = open(p).read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:100], s.count(a))
    s = s.replace(a, b)


# a sentence that has sat on a comment line since 2c0f6c5d1, so never printed; section 4.2 promises two comparisons
rep("""OUTCOME-20261106-ref-c2c1-read.md (printed and read by nothing; no attribution licensed). The five-observable estimator, run on the two-dimensional inputs,""",
    """OUTCOME-20261106-ref-c2c1-read.md (printed and read by nothing; no attribution licensed).
The five-observable estimator, run on the two-dimensional inputs,""")
# section 1: the shape-difference clause
rep("""shows agreement in normalization and a correlated shape difference that accompanies the unfolding method on fixed inputs and whose mechanism has not been identified (section~\\ref{sec:bench}).""",
    """shows agreement in normalization and a correlated shape difference (section~\\ref{sec:bench}). On fixed inputs, a binned unfolding lies closer to the published shape, and the mechanism of the difference has not been identified.""")
# section 2
rep("""The check compares selected samples, not these inputs with the published analysis's""",
    """The check compares the selected samples of the two productions. It does not compare these inputs with those of the published analysis""")
# section 3.1: the referent of "These events"
rep("""These events carry""", """Events without a reconstructed partner carry""")
# section 3.2: dangling openings and orphan
rep("""These are the diagonal elements only.""", """Both figures are for the diagonal elements only.""")
rep("""It was added after the differences were observed and is constructed from the double ratios among the groups""",
    """The block was added after the differences were observed and is constructed from the double ratios among the groups""")
rep("""With three groups its size is poorly determined. \\ssec{S5}{supp:cov16} gives an illustrative interval on its size under a stated model, and that interval describes no uncertainty in the block's orientation.""",
    """With three groups its size is poorly determined. An illustrative interval on its size under a stated model is given in \\ssec{S5}{supp:cov16}, and that interval describes no uncertainty in the block's orientation.""")
# section 3.3: the count of distinct truths; the estimator copy (said in section 3.1 and table~1)
rep("""at all \\fvval{ens1-ntruths} distinct truths, graded and descriptive, since the Tune~v1 hybrid equals the prior.""",
    """at all \\fvval{ens1-ntruths} distinct truths, graded and descriptive. The Tune~v1 hybrid and the prior count once there, because they are equal.""")
rep("""The two-dimensional benchmark (section~\\ref{sec:bench}) concerns the two-observable estimator. The truth-recovery and stability findings (sections~\\ref{sec:prior} and~\\ref{sec:cov5d}) concern the five-observable estimator, whose rounding sensitivity is carried in its statistical uncertainty (section~\\ref{sec:cov5d}).""",
    """The estimator behind each finding is given in table~\\ref{tab:estimators}.""")
# the tunes' shared ingredients, once, where the tunes are introduced
rep("""were generated for these tests and held out of it. Each enters""",
    """were generated for these tests and held out of it. They share a quasielastic cross-section model, and \\fvval{f1-tune-g18} and the GENIE + MEC component of $C_{\\mathrm{model}}$ use Valencia-family MEC models. Each enters""")
rep("""The tunes share a quasielastic cross-section model, and \\fvval{f1-tune-g18} and the GENIE + MEC component of $C_{\\mathrm{model}}$ also use Valencia-family MEC models. These tests provide partial evidence""",
    """The held-out-tune tests provide partial evidence""")
rep("""\\fvval{f1-tune-g18} shares its 2p2h model family with one of $C_{\\mathrm{model}}$'s generators. The test's false-flag rate""",
    """The test's false-flag rate""")
rep("""The tunes are held out of the analysis but not independent of it: they share a quasielastic model, and \\fvval{f1-tune-g18} shares its 2p2h model family with one of the generators of $C_{\\mathrm{model}}$.""",
    """The tunes are held out of the analysis but not independent of it (section~\\ref{sec:strategy}).""")
# section 4.4: the compound subject
rep("""The statistical correlation, and that of four systematic terms that could not be evaluated directly, are bounded within a one-parameter family of valid covariances, with each such cross term taken as a common fraction, from zero to one, of its fully correlated value.""",
    """The statistical correlation and the correlations of four systematic terms that could not be evaluated directly are bounded within a one-parameter family of valid covariances. Each such cross term is taken as a common fraction, from zero to one, of its fully correlated value.""")
# the per-period readings move from section 4.1 to section 4.3, which they concern; the back-pointer goes
a = s.index("Removing the 1G--1M group, whose step is given in section~\\ref{sec:closure2d}, leaves")
b = s.index("cause of the step (\\ssecc{S6}{supp:cov2d}).", a) + len("cause of the step (\\ssecc{S6}{supp:cov2d}).")
moved = s[a:b]
s = s[:a].rstrip() + "\n" + s[b:]
moved = moved.replace("Removing the 1G--1M group, whose step is given in section~\\ref{sec:closure2d}, leaves this distance",
                      "Removing the 1G--1M group leaves the distance to the published result of section~\\ref{sec:repro2d}")
rep("""The effect of the 1G--1M step on the distance to the published result is given with that distance (section~\\ref{sec:repro2d}).""", moved)
# section 5.1: the orphan sentence folds into its paragraph, with one verdict verb
rep("""On the sixteen reported cells, the reported estimator's bias at the same truth satisfies both criteria under the reported covariance, with a largest $|z|$ of \\fvval{f0b-stage0c_gibuu-zmax}, and meets the flagging criterion without $C_{\\mathrm{PL,5D}}$ (section~\\ref{sec:fd16}).""",
    """On the sixteen reported cells, the reported estimator is not flagged at the GiBUU-to-GENIE truth under the reported covariance, with a largest $|z|$ of \\fvval{f0b-stage0c_gibuu-zmax}. It is flagged without $C_{\\mathrm{PL,5D}}$ (section~\\ref{sec:fd16}).""")
i = s.index("On the sixteen reported cells, the reported estimator is not flagged at the GiBUU-to-GENIE truth")
j = i - 1
while s[j] in " \n":
    j -= 1
s = s[:j + 1] + " " + s[i:]
# section 5.1: the W-shapes paragraph repeats the median clause of the opening
rep("""The median cell moves by \\SIrange{\\fvval{rec-w-fmed-lo}}{\\fvval{rec-w-fmed-hi}}{\\percent} of the injected change, and of the supported cells""",
    """Of the supported cells""")
# section 5.2a: the notation defined in place
rep("""$|b_c|\\leq0.5\\,|d_c|$ in the notation of section~\\ref{sec:prr},""",
    """$|b_c|\\leq0.5\\,|d_c|$, with the bias $b_c$ and the departure $d_c$ both relative to the prior cross section (section~\\ref{sec:prr}),""")
# section 5.3: rho defined before its results; the lead paragraph and table 4 follow the study's definition
a = s.index("% Fresh referee read on 283f3044 (RESPONSE.md rows G6, Gm4, Gs5)")
t4 = s.index("% T1-1: the essentials of the Supplement's tab:prr-rho", a)
t4e = s.index("\\end{table}\n", t4) + len("\\end{table}\n")
lead = s[a:t4e]
s = s[:a] + s[t4e:]
k = s.index("A tested level clears a flagged truth if the truth is no longer flagged")
k = s.index("\n", k) + 1
lead = lead.replace("its retained fraction $\\rho$, defined below, is", "its retained fraction $\\rho$ is")
s = s[:k] + "\n" + lead + s[k:]
# section 6.2: the dangling "It"; the conditional-test list; the restricted test's referents
rep("""\nIt under-covers at both tunes.""", """\nThe two-dimensional covariance under-covers at both tunes.""")
rep("""These are conditional tests of covariance adequacy: the systematic parameters are drawn from their bands' discrete or Gaussian laws, the covariance is rebuilt once at each tune and then held fixed, the lateral uncertainties are represented by a surrogate, the nominal Gaussian content is replaced by a content matched to the draws, some terms are included in the covariance without being drawn and others are left out, and the truths are gated, normalized shape deformations from two tunes""",
    """These are conditional tests of covariance adequacy. Besides the matched content above, (i) the systematic parameters are drawn from their bands' discrete or Gaussian laws, (ii) the covariance is rebuilt once at each tune and then held fixed, (iii) a surrogate represents the lateral uncertainties, (iv) some terms are included in the covariance without being drawn and others are left out, and (v) the truths are gated, normalized shape deformations from two tunes""")
rep("""The two constructions match in each operation checked, and what separates them lies inside the estimator and is unclassified (\\ssec{S8.4}{supp:study-cov1}). Excluding them defines a restricted test""",
    """The pseudo-experiment and simulation-side constructions match in each operation checked, and what separates their blocks for these bands lies inside the estimator and is unclassified (\\ssec{S8.4}{supp:study-cov1}). Excluding the two bands defines a restricted test""")
rep(""" The data result remains an illustration. % absence-ok""", """ % absence-ok""")
# verdict verbs
rep("""Both tunes satisfy the bias criteria:""", """Both tunes pass the bias criteria:""")
open(p, "w").write(s)
print("PRD batch applied")
