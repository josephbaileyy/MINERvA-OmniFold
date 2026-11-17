"""Style round 3's paper items on paper_body.tex (the director's approved order of 2026-11-12, items 1-7)."""
import sys

p = sys.argv[1]
s = open(p).read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:100], s.count(a))
    s = s.replace(a, b)


# 1. section 6.2 leads with its answer
rep("""Each coverage test in this section asks whether a covariance,""",
    """% Style round 3 (item 1): the section leads with its answer.
The two-dimensional covariance under-covers at both held-out tunes: none of the \\fvval{cov2d-ntoys} pseudo-experiments at either tune lies in the joint region (table~\\ref{tab:cov2d}). No reported interval has validated coverage (section~\\ref{sec:limitations}).

Each coverage test in this section asks whether a covariance,""")

# 1. section 5.3: one plain statement per finding, in place of the per-truth variant prose (prr is filled: both truths
# take the same class in PR-2a, PR-2b and every label, and PR-3 is "not" at both; values_fived16.tex fvc@prr-*)
a = s.index("At the GiBUU hybrid truth, the IBU at five iterations \\fvcase{prr-pr2a-gibuu}")
b = s.index("\\fvcase{prr-pr3-ibu}{not}{Neither a tested level nor the IBU at five iterations clears at these truths.}}", a)
b += len("\\fvcase{prr-pr3-ibu}{not}{Neither a tested level nor the IBU at five iterations clears at these truths.}}")
s = s[:a] + """% Style round 3 (items 1 and 2): the two truths' near-identical variant sentences are one statement each, as the filled
% classes read (fvc@prr-pr2a-*: less; prr-pr2b-*: falls; prr-label-obs-*, prr-label-impl-*: holds, the others not;
% prr-pr3-any and prr-pr3-ibu: not). The labels' wording ("a share specific to the implementation") stays in S8.2.
At both flagged truths, IBU at five iterations has a lower retained fraction than the five-observable estimator, by more than its threshold (\\fvval{prr-ibu-bar}), and its retained fraction falls by at least a fixed margin between five and 200 iterations. At both, the retained prior is sensitive to the observable set. No tested level of a setting, and not IBU at five iterations, removes the bias flag at either truth.""" + s[b:]
rep("""A tested level clears a flagged truth if the truth is no longer flagged under the criterion of section~\\ref{sec:strategy} applied to the noise-free pseudo-data.""",
    """A level removes a truth's bias flag if the truth is no longer flagged under the criterion of section~\\ref{sec:strategy} applied to the noise-free pseudo-data.""")

# 2. table 4: test (estimator in the name), principal finding, section; the interpretation key goes
i = s.index("\\label{tab:outcomes}")
a = s.index("\\begin{tabular*}", i)
b = s.index("\\end{table*}", i)
rows = r"""\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}>{\raggedright\arraybackslash}p{5.6cm}>{\raggedright\arraybackslash}p{10.6cm}r@{}} \toprule
Test & Principal finding & Sec. \\ \midrule
\multicolumn{3}{@{}l}{\textit{Benchmark against the published measurement}} \\
Comparison with the published $(\pT,\pPar)$ result (2D) & Integral ratio $\ratioTot$; descriptive $\chi^2/\mathrm{ndf}=\chiPaper$ (ndf $=205$) against a covariance of condition number $1.5\times10^{12}$ & \ref{sec:repro2d} \\
Binned IBU of the same two-dimensional inputs (2D) & Difference detected: $T=382.8$, above the null's maximum of 138.5; IBU lies closer to the published result; mechanism not resolved & \ref{sec:paired2d} \\
Sixteen-cell and two-dimensional quadrant sums (5D) & No difference detected: $\chi^2\leq\fvval{x-chi2-hi}$ for 4 degrees of freedom & \ref{sec:quad} \\
\addlinespace[3pt]
\multicolumn{3}{@{}l}{\textit{Recovery of controlled truth changes}} \\
Generator-sized truth changes (5D) & Median cell moves by \SIrange{\fvval{rec-w-fmed-lo}}{\fvval{rec-w-fmed-hi}}{\percent} of the change, individual cells from opposite to overshooting; most affected supported cell \SIrange{\fvval{rec-w-supmax-lo}}{\fvval{rec-w-supmax-hi}}{\percent}, up to \SI{\fvval{s5e-gibuu-ewmax}}{\percent} at the GiBUU-to-GENIE change & \ref{sec:departure} \\
Fake-data bias at \fvval{f0b-all-truths} graded truths (5D) & Bias threshold exceeded at the GiBUU hybrid truth and the synthetic $q_3$ tilt & \ref{sec:fd16} \\
Two held-out GENIE~v3 tunes (5D) & Bias criteria passed: $\chi^2=\fvval{f1-g18-chi2int}$ and \fvval{f1-ar23-chi2int} for 16 degrees of freedom; the tests are not independent & \ref{sec:fd16} \\
What changes the retained prior, at the two flagged truths (5D) & \fvgroup{prr}{A reduced setting raises $\rho$: \fvval{prr-pr1-increases}. No detected change: \fvval{prr-pr1-noeffect}. IBU at five iterations: $\rho<0$ at both} & \ref{sec:prr} \\
Binned IBU of the same data on the sixteen cells (5D) & Difference detected: $T=194.4$, above the null's 99.7th percentile of 39.04 & \ref{sec:ibu} \\
Per-cell bias at most half the truth's departure from the prior (5D) & \fvgroup{vhalf}{\fvval{vhalf-n-valid} of 16 cells pass, \fvval{vhalf-n-notvalid} fail, \fvval{vhalf-n-unresolved} unresolved} & \ref{sec:vhalf} \\
\addlinespace[3pt]
\multicolumn{3}{@{}l}{\textit{Reproducibility, stability and calibration}} \\
Rounding-level changes of the inputs (5D) & Stability requirement failed: shifts of a median \fvval{s5e-round-median} and at most \fvval{s5e-round-max} statistical standard deviations, against 0.3 and 1.0 & \ref{sec:cov5d} \\
Mechanism of the rounding spread, one pseudo-experiment (5D) & Ties among equal float32 values change the histogram bins & \ref{sec:cov5d} \\
Ensemble average of \fvval{ens1-n} fits (5D) & Meets the stability requirement, worse in bias at 1 of \fvval{ens1-ntruths} truths; variant not adopted & \ref{sec:cov5d} \\
Coverage of the two-dimensional covariance at two held-out tunes (2D) & Under-coverage: no pseudo-experiment of 300 in the joint region at either tune & \ref{sec:calib} \\
"""
old_ll5d = s[s.index("Second five-observable coverage test & 5D & ", a):]
old_ll5d = old_ll5d[:old_ll5d.index(" & \\fvgroupalt{ll5d}{Pending}")]
res = old_ll5d[len("Second five-observable coverage test & 5D & "):]
rows += "Second five-observable coverage test (5D) & " + res + " & \\ref{sec:ll5d} \\\\\n"
rows += r"""Run-period consistency (5D; 2D) & A step of $+\fvval{rp-pb-reco}\,\%$ at reconstruction level, against 1A--1F, present in the data before unfolding & \ref{sec:closure2d} \\ \bottomrule
\end{tabular*}
"""
s = s[:a] + rows + s[b:]
rep("""its principal result, its interpretation and the section that reports it. The interpretation words are defined below the table.}""",
    """its principal finding and the section that reports it. For the second five-observable coverage test the finding gives one entry for each tune and variant, the primary variant (without the GEANT4 neutron and proton bands) first. Criteria, thresholds and classes are in the supplementary material's section~S8.}""")

# 3. section 4.2: the iteration sweep is in S7
rep("""a binned IBU lies at $\\chi^{2}/\\mathrm{ndf}=\\fvval{c2c1-dibu}$ from the published result under its covariance at ten iterations, the published count and this comparison's primary setting (\\fvval{c2c1-dibu-mid-lo}--\\fvval{c2c1-dibu-mid-hi} for two to fifteen iterations, \\fvval{c2c1-dibu-k20} at twenty and \\fvval{c2c1-dibu-k1} at one), against \\fvval{c2c1-der} for the two-dimensional OmniFold result.""",
    """a binned IBU at ten iterations, the published count and this comparison's primary setting, lies at $\\chi^{2}/\\mathrm{ndf}=\\fvval{c2c1-dibu}$ from the published result under its covariance, against \\fvval{c2c1-der} for the two-dimensional OmniFold result (other iteration counts: \\ssec{S7}{supp:ibu}).""")

# 4. section 7: the five checks, shorter; section 7.1 without reprinted numbers
i = s.index("\\begin{enumerate}\n\n\\item Closure should include")
j = s.index("\\end{enumerate}", i) + len("\\end{enumerate}")
s = s[:i] + r"""\begin{enumerate}
\item Closure should include the backgrounds (section~\ref{sec:closure}).
\item Generator-sized truth changes should be recovered, and the retained part of the prior measured (sections~\ref{sec:departure} and~\ref{sec:prr}).
\item Coverage should be tested at changed truths, jointly as well as per cell, with the joint statistic read in the covariance's eigenbasis (section~\ref{sec:calib}).
\item Robustness should be tested against rounding-level input changes as well as training seeds (section~\ref{sec:cov5d}).
\item Run periods should be compared before and after unfolding (section~\ref{sec:closure2d}).
\end{enumerate}
In this implementation, closure holds, and each of the other four checks finds a problem: part of the prior is retained, the two-dimensional covariance under-covers, the result is not stable under rounding, and a run-period step survives unfolding.""" + s[j:]
rep("""\\item \\emph{Estimator bias.} Recovery within the reported uncertainty, as graded on the sixteen reporting cells, is not achieved for every generator-sized truth change tested. At the four changes of figure~\\ref{fig:deformation}, the median unfolded $(\\Eavail,W)$ cell moves by \\SIrange{\\fvval{rec-w-fmed-lo}}{\\fvval{rec-w-fmed-hi}}{\\percent} of the injected change and up to \\fvval{rec-all-opp-max} of \\fvval{rec-g-n} supported cells with an injected change of magnitude above \\SI{\\fvval{rec-thr}}{\\percent} move opposite to it. The unfolded result retains part of its prior (section~\\ref{sec:prior}, table~\\ref{tab:outcomes}).""",
    """\\item \\emph{Estimator bias.} Recovery within the reported uncertainty, as graded on the sixteen reporting cells, is not achieved for every generator-sized truth change tested. The unfolded result retains part of its prior, and some $(\\Eavail,W)$ cells move opposite to a truth change (section~\\ref{sec:prior}).""")
rep("""have a diagonal fraction (section~\\ref{sec:data}) of only \\fvval{h2-lowstab-min}--\\fvval{h2-lowstab-max}.""",
    """have a low diagonal fraction (table~\\ref{tab:cells}).""")

# 5. the bias-alone statement's home is section 3.3
rep("""No reported interval has validated coverage. The fake-data tests assess only bias.""",
    """No reported interval has validated coverage. The fake-data tests grade bias only (section~\\ref{sec:strategy}).""")

# 6. sentence tics: "therefore" and "by construction" where the consequence is plain
rep("""The block therefore estimates the spread of a randomized procedure""", """The block estimates the spread of a randomized procedure""")
rep("""It therefore contains the differences by construction.""", """It contains these differences.""")
rep("""``Differ'' therefore means that""", """``Differ'' means that""")
rep("""changing only the unfolding method therefore brings the result""", """changing only the unfolding method brings the result""")
rep("""The five-observable result therefore agrees with the two-dimensional normalization""", """The five-observable result agrees with the two-dimensional normalization""")
rep("""The reported cells therefore depend on the unfolding algorithm:""", """The reported cells depend on the unfolding algorithm:""")
rep("""The test has two variants, correlated by construction: a primary one""", """The test has two correlated variants: a primary one""")

# 7. line items
rep("""The one playlist that predates the current release was checked against that release.""", """Playlist 1A predates the current release and was checked against it.""")
rep("""Two covariances are reported: the sixteen-cell result's, described first, and the two-dimensional result's four-block sum, described after it. The sixteen-cell covariance is""",
    """We report covariances for the sixteen-cell and two-dimensional results. The sixteen-cell covariance is""")
rep("""were generated for these tests and held out of the analysis.""", """were generated for these tests and were not used in developing the analysis.""")
rep("""divided by $\\sqrt{\\mathrm{diag}(C+N)}$, where $N$ is the noise covariance of the mean.""",
    """divided by $\\sqrt{\\mathrm{diag}(C+N)}$, where $N$ is the noise covariance of the mean. Like the residual, $C$ and $N$ are fractional covariances.""")
rep("""the sums differ by $\\fvval{x-dpct-min}$ to $\\fvval{x-dpct-max}$ per cent,""", """the sums differ by \\SIrange{\\fvval{x-dpct-min}}{\\fvval{x-dpct-max}}{\\percent},""")
# the usage-recommendation rule, glossed plainly at first use (the director, 2026-11-12)
rep("""The usage-recommendation rule is a per-cell bias-screening rule based on the usage recommendations of ref.~\\cite{ATLAS:2024jets}.""",
    """The usage-recommendation rule is a per-cell bias-screening rule adapted from ref.~\\cite{ATLAS:2024jets}.""")
open(p, "w").write(s)
print("round-3 batch applied")
