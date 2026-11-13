"""The sentence pass on paper_body.tex, part 2: paragraph breaks at topic boundaries in paragraphs over 150 words
(no sentence is changed). The B0 span's paragraph and the draft-only \\pubhold are not split."""
import sys

p = sys.argv[1]
s = open(p).read()
STARTS = [
    "The findings apply to one OmniFold implementation on one data set",
    "Each cell's result is its cell-integrated cross section",
    "The median per-cell relative uncertainty is \\fvval{sigmed-reported}",
    "The dependence on the prior's generator shape is reported separately",
    "Two GENIE~v3 tunes, \\fvval{f1-tune-g18} and \\fvval{f1-tune-ar23}, were generated",
    "The bias is graded on Poisson pseudo-experiments",
    "An estimator meets the stability requirement when",
    "The two-dimensional result's integrated cross section is",
    "Removing the 1G--1M group, whose step is given",
    "On the sixteen reported cells, the reported estimator's bias at the same truth",
    "Figure~\\ref{fig:bias-cells} shows the per-cell bias",
    "At the other \\fvval{f0b-nunlisted} truths",
    "The simulated detector response is not varied in these tests.",
    "The second comes from the data.",
    "The study changes one setting at a time",
    "At the GiBUU hybrid truth, \\fvlist{",
    "The covariance of that comparison contains",
    "We report the ensemble average as a tested mitigation",
    "In $C_T$'s eigenbasis,",
    "The test uses the reported estimator.",
]
for a in STARTS:
    k = s.count(a)
    assert k == 1, (a, k)
    i = s.index(a)
    assert s[i - 1] in " \n", (a, repr(s[i - 3:i]))
    j = i - 1
    while s[j] == " ":
        j -= 1
    s = s[:j + 1] + "\n\n" + s[i:]
# the second five-observable test: the outcome cases start their own paragraph
a = "\\fvgroup{ll5d}{%\n\\fvcase{ll5d-campaign}{graded}{"
assert s.count(a) == 1
s = s.replace("carries over only if both matrices have 16 degrees of freedom.\n", "carries over only if both matrices have 16 degrees of freedom.\n\n", 1)
# the five checks: one paragraph per item
i = s.index("\\begin{enumerate}\n\\item Closure should include")
j = s.index("\\end{enumerate}", i)
blk = s[i:j]
s = s[:i] + blk.replace("\n\\item ", "\n\n\\item ") + s[j:]
open(p, "w").write(s)
print(len(STARTS) + 2, "splits")
