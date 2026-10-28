r"""usage: python3 -I apply_r20.py ANALYSIS_NOTE_DIR -- register round r20, the paper's last (r20/outline.md, approved by
the director at e8ec4972 with conditions). Six passages, no structural change; the (c) sentences and Data Availability
untouched.

- R1, the five-iteration sentence: the result first, the pointer folded in. The metric and population are the note's:
  "the largest residual proxy over the development truth changes"; "None did, so five iterations were kept"
  (sec_5d.tex sec:gbdt-model-dependence).
- R2, the Limitations lead: "each stated with the result it qualifies". Not "in full", which would be a new claim
  (director, condition 1).
- R3, the scope sentence: positive form; "not to multidimensional OmniFold in general" kept.
- R4, the binned diagnostic: the result first, in the note's word, "agree" ("At five iterations the J-cell medians of
  the absolute residual agree: ...", sec_5d.tex), not "about the same" (condition 2). The scope sentences that follow,
  the out-of-scope sentence among them (DECISION-20261023 item 3b), are unchanged except "It covers" -> "The
  diagnostic covers".
- R5, the listing rule: "The bias at a truth is listed when ..."; the ungraded truths in their own sentence.
- R6, the note's-tests sentence: the note's words, "displaced far upward" and "the calibration reproduces the
  estimator's pull toward its prior" (sec_joint.tex sec:joint5d-results), condition 3.
Every edit is an exact old -> new pair, whitespace-tolerant, that must match exactly once."""
import re, sys
D = sys.argv[1]
def pat(s): return re.compile(r"\s+".join(re.escape(w) for w in s.split()))
p = f"{D}/paper_body.tex"; t = open(p, encoding="utf-8").read()
E = [
 ("R1", r"The joint-test estimator keeps five iterations because 10, 15, or 20 iterations did not reduce its model dependence, measured as the largest residual proxy over the truth changes used in its development.  The comparison and its values are given in \nsec{sec:gbdt-model-dependence}.",
  r"Ten, 15 or 20 iterations did not reduce the joint-test estimator's model dependence, measured as the largest residual proxy over the truth changes used in its development, so it keeps five (\nsec{sec:gbdt-model-dependence})."),
 ("R2", r"The limitations of these results are stated with the results they qualify, in Secs.~\ref{sec:method}--\ref{sec:result16}, and those of the calibrated tests in the companion note.  The principal ones are these.",
  r"The principal limitations, each stated with the result it qualifies (Secs.~\ref{sec:method}--\ref{sec:result16}; for the calibrated tests, the companion note), are these."),
 ("R3", r"\emph{Scope.} The findings are those of one OmniFold implementation on one data set, for the observables, configurations, and deformations tested, rather than of multidimensional OmniFold in general.",
  r"\emph{Scope.} The findings apply to the OmniFold implementation, data set, observables, configurations and deformations studied here, not to multidimensional OmniFold in general."),
 ("R4", r"In a binned, signal-only and noise-free diagnostic on the \jtNcells{} joint cells and the truth changes used to develop the estimator, with the detector response fixed at the simulation's, an exact binned iterative unfolding with five iterations leaves about the same median residual as the boosted-tree estimator.  It covers only",
  r"An exact binned iterative unfolding with five iterations gives median absolute residuals that agree with those of the boosted-tree estimator in a binned, signal-only and noise-free diagnostic on the \jtNcells{} joint cells and the truth changes used to develop the estimator, at the simulation's detector response.  The diagnostic covers only"),
 ("R5", r"A truth is listed when $p<\fvval{trig-p}$ or when a cell has $|z|>\fvval{trig-z}$. Table~\ref{tab:fd16} gives the results under the reported covariance and under $C_{\mathrm{total}}$ alone; \fvval{f0b-nungraded} further truths are ungraded and given in the note.",
  r"The bias at a truth is listed when $p<\fvval{trig-p}$ or when a cell has $|z|>\fvval{trig-z}$. Table~\ref{tab:fd16} gives the results under the reported covariance and under $C_{\mathrm{total}}$ alone. The note gives \fvval{f0b-nungraded} further, ungraded truths."),
 ("R6", r"The note's calibrated tests show the same pull: their null distributions for the external predictions are displaced upward by it, as the calibration reproduces (\nsec{sec:joint5d-results}).",
  r"In the note's calibrated tests, the same pull displaces the null distributions of the external predictions far upward, and the calibration reproduces it (\nsec{sec:joint5d-results})."),
]
for k, old, new in E:
    m = list(pat(old).finditer(t))
    if len(m) != 1:
        sys.exit(f"{k}: {len(m)} matches")
    t = t[:m[0].start()] + new + t[m[0].end():]
open(p, "w", encoding="utf-8").write(t); print("r20 applied: %d edits" % len(E))
