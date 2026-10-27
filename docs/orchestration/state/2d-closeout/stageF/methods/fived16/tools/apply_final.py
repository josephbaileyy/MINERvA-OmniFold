"""Apply the final-draft changes (director, 2026-10-27, after the PRD read). Each old string must occur exactly once."""
import sys
E = {"paper_body.tex": [
 ("C02", r", of which the study's \fvval{h2-nsupported} coarser cells are the supported ones; each supported box", r": each supported box"),
 ("C03", r"Its model term differs from the study's envelope: there, the largest shift of a cell over five generator-sized truth changes, added linearly to the half-width; here, a covariance built from three generator shifts.",
         r"Unlike the envelope of Sec.~\ref{sec:uncertainty-status}, its model term is a covariance built from three generator shifts."),
 ("C04", r"normalization uncertainties of configuration~(e), a training-seed term measured to be zero, and $C_{\mathrm{model}}$.", r"normalization uncertainties of configuration~(e) and $C_{\mathrm{model}}$."),
 ("C05", r"it is generator-shape model dependence, unscaled and not a calibrated bound, and its coverage", r"it represents unscaled generator-shape dependence, not a calibrated bound, and its coverage"),
 ("C08", r"and it does not enter the generator tests of Sec.~\ref{sec:joint} or the paper's other results.", r"and it enters only this result, its fake-data tests and its comparison in Sec.~\ref{sec:gen16}."),
 ("C10", r"compared with the covariance without that generator's component, so that no such truth is compared with a covariance that includes its own generator's component; ", r"compared with the covariance without that generator's component; "),
 ("C11", r"\fvval{f0b-nungraded} further truths, whose offset correction failed its control, are ungraded and given in the note.", r"\fvval{f0b-nungraded} further truths are ungraded (given in the note)."),
 ("C06", r"or when a cell has $|z|>\fvval{trig-z}$. Table~\ref{tab:fd16}", r"or when a cell has $|z|>\fvval{trig-z}$. These are not held-out truths. Table~\ref{tab:fd16}"),
 ("Q5", r"the bias stays within the reported uncertainty by both criteria: no cell beyond", r"the bias passes both criteria: no cell beyond"),
 ("C14", r"with shape-only $\chi^2$ beside it; no diagonal-only $\chi^2$ is formed.", r"with shape-only $\chi^2$ beside it."),
 ("C18", r"Because $C_{\mathrm{model}}$ is built from shifts toward GENIE + MEC, NuWro and GiBUU, each relative to GENIE CV, those comparisons use a covariance built in part from the compared generator, and the GENIE CV comparison does through that reference.",
         r"The GENIE + MEC, NuWro and GiBUU comparisons use covariance contributions derived from those generators; GENIE CV enters as their common reference."),
 ("C21", r"No uncertainty quoted for the configuration-(a) central value includes the regularization bias, and its five-observable covariance omits it.", r"The uncertainties of the configuration-(a) central value omit the regularization bias."),
 ("C22", r"unscaled and not a calibrated bound, and Sec.~\ref{sec:result16} gives the fake-data study's measured comparison of the estimator's bias with the reported covariance.",
         r"unscaled and not a calibrated bound; Sec.~\ref{sec:result16} reports the fake-data tests of the estimator's bias."),
 ("C23", r"The seed dependence of this five-observable covariance rests on one seed pair, and the spread over seed pairs has not been measured.", r"The seed dependence of this five-observable covariance was studied with only one seed pair."),
 ("C24", r"The higher-dimensional results are central values without intervals of validated coverage, and no uncertainty quoted for the configuration-(a) five-observable central value includes its regularization bias (Sec.~\ref{sec:departure}).",
         r"The higher-dimensional central values lack intervals of validated coverage, and the uncertainties of the configuration-(a) five-observable central value omit its regularization bias (Sec.~\ref{sec:departure})."),
 ("C25", r"whose coverage is not validated; Sec.~\ref{sec:result16} gives the fake-data study's measured comparison of the estimator's bias with its reported covariance.",
         r"whose coverage is not validated; Sec.~\ref{sec:result16} reports the fake-data tests of the estimator's bias."),
], "sec_fived16.tex": [
 ("Q5", r"the bias stays within the reported uncertainty by both criteria: no cell beyond", r"the bias passes both criteria: no cell beyond"),
]}
for f, edits in E.items():
    t = open(f).read()
    for k, old, new in edits:
        n = t.count(old)
        if n != 1:
            sys.exit(f"{f} {k}: found {n} times")
        t = t.replace(old, new)
    open(f, "w").write(t)
    print(f, len(edits), "edits")
