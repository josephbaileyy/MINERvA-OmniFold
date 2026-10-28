"""The d2 options put to the independent raters (DECISION-20261028-joseph-final-draft-d items 3, 4, 6 and 7), one
definition each: the same LaTeX feeds the rater inputs (make_battery.py) and any later edit, so nothing is retyped.

Each option has its site (file), the current text exactly as it is in the source (OLD, which must occur there once),
and its alternatives, in LaTeX, keyed by a neutral id. "K" is always the current text. The alternatives are drafts of
this lane's, except where SOURCE names the record they come from."""

ALIGN = {  # 3.4: one wording of the coverage limitation, used wherever it prints
    "q": "Which wording of the coverage limitation should the paper use, the same in its introduction and its abstract?",
    "forms": {"i": "Interval coverage has not been validated.",
              "ii": "The coverage of the intervals has not been validated.",
              "iii": "The coverage of the result's intervals has not been validated."},
    "context": "The sentence opens the paper's statement of its limitations, in the introduction and in the abstract.",
}

FLUX_OLD = (r"Weakening only the flux correlations by \fvval{sens-alpha-pct}\,\% lowers the $\chi^2$ of the 16-cell "
            r"predictions by \fvval{sens-flux-fall-lo}--\fvval{sens-flux-fall-hi}\,\%. The same change to the detector "
            r"or lateral correlations lowers it by at most \fvval{sens-detlat-fall-max}\,\%. With the correlations")
FLUX = {  # 4: keep both (K) or replace the alpha = 0.1 sentences with the band (R)
    "q": "Which form of this paragraph should the paper print?",
    "site": "paper_body.tex",
    "K": None,   # the paragraph as it prints (read from the source)
    "R": [(FLUX_OLD, r"With the correlations"),
          (r"not its sensitivity to incorrect correlations, which the weakening probes; they are not intervals",
           r"not its sensitivity to incorrect correlations; they are not intervals")],
    # under R, Sec. I's flux sentence keeps its numbers and points to the note, where the weakening still prints
    "R_sec1": [(r"\fvval{sens-flux-fall-lo}--\fvval{sens-flux-fall-hi}\,\% (Sec.~\ref{sec:gen16}).",
                r"\fvval{sens-flux-fall-lo}--\fvval{sens-flux-fall-hi}\,\% (\nsec{sec:fived16-gen}).")],
    "start": r"Weakening only the flux correlations by", "end": r"under the true correlations.",
}

O3 = {
    "q": "Which sentence should the paper print?",
    "site": "paper_body.tex",
    "K": r"We interpret the residual as regularization bias, because it persists over the tested iteration numbers and classifier capacities.",
    "Q": r"We interpret the residual as regularization bias, because it persists over the tested iteration numbers and classifier capacities, although no single cause is established.",
}

REL9 = {
    "q": "Which sentence should the companion note's release appendix print?",
    "site": "app_release.tex", "doc": "note",
    "K": r"It also regenerates, from packaged arrays, figures that the article cites from this note:",
    "D": r"It also regenerates, from packaged arrays, figures that the article cites from this note, directly or through its pointers:",
    "end": r"the one-dimensional generator projections.",
}

R14 = {  # SOURCE: prd-read/r2/inputs/proposals.tsv (round 2's R1-R4)
    "q": "Which set of phrasings should the companion note's release appendix print?",
    "site": "app_release.tex", "doc": "note",
    "pairs": [("the quoted closure, bias and covariance-status measurements.",
               "the quoted closure, bias and covariance-status measurements of the configuration-(a) central value."),
              ("the five-axis covariance used in this note and its", "the five-axis covariance of the configuration-(a) central value and its"),
              ("travel with the five-axis covariance used in this note", "travel with the five-axis covariance of the configuration-(a) central value"),
              ("The five-axis covariance used in this note is the file", "The five-axis covariance of the configuration-(a) central value is the file")],
}

DEPCAP = {
    "q": "Should the result table's caption end with this sentence?",
    "site": "paper_body.tex",
    "K": r"Quantitative comparisons need the full covariance (Sec.~\ref{sec:cov16}).",
    "D": r"Quantitative comparisons need the full covariance (Sec.~\ref{sec:cov16}). The cell definitions, measured vector, reported covariance and correlation matrix are given in machine-readable form in Ref.~[deposit].",
}

DA_TYPICAL = (r"The input data and simulation are the MINERvA open-data AnaTuples, released under CC0~\cite{MINERvA:OpenData}. "
              r"The sixteen-cell cross section, its covariance matrix and the cell definitions are provided as "
              r"machine-readable files in the Supplemental Material.")
DA = {  # 6: SOURCE for the typical form: d2/DA-SURVEY.md (the seven corpus measurement papers)
    "q": "Which Data Availability statement should the paper print?",
    "site": "main_paper.tex",
    "start": "The input data and simulation are the MINERvA open-data AnaTuples", "end": "release decision.}",
    "T": DA_TYPICAL,
}
DEPDA = {
    "q": "Should the Data Availability statement add this sentence?",
    "K": DA_TYPICAL,
    "D": DA_TYPICAL + r" The same quantities are prepared for deposit in a versioned repository, Ref.~[deposit].",
}

R11_AFTER = r"in every cell of the means and closures."
R11 = {
    "q": "Should the paragraph add this sentence?",
    "site": "paper_body.tex",
    "K": R11_AFTER,
    "C": R11_AFTER + r" In cell R11 at \fvval{f1-tune-g18}, the bias lies below the reported uncertainty only with $C_{\mathrm{model}}$ included.",
}

CONTROL = {  # a register control: Y is colloquial by construction; a rater that prefers it is not reading
    "q": "Which sentence should the paper print?",
    "X": r"The sixteen-cell result is compared with five generator predictions.",
    "Y": r"We went ahead and compared the sixteen-cell result with a bunch of generator predictions.",
}
