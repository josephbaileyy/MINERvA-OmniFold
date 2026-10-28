r"""usage: python3 -I apply_r20_fixes.py ANALYSIS_NOTE_DIR -- r20: fixes for the review (scratchpad REVIEW-r20.md,
ADOPT-AFTER-FIXES, no BLOCKING) and agy (r20/agy/).
- S1 and agy Q2: R2 had narrowed "every limitation is stated with its result" to the principal ones. Now: "Each
  limitation is stated with the result it qualifies (...); the principal ones are these."
- S2 and agy Q3: R3 had lost "one implementation on one data set", which carries the generality. The base's frame is
  back, "The findings are those of one OmniFold implementation on one data set, ...", with "studied here" and "not
  of multidimensional OmniFold in general".
- R4, review NIT: split so that each qualifier attaches to the diagnostic, with "fixed at the simulation's" back
  (KEEP E9).
- R6, review NIT: "the same pull toward the prior", so that "pull" has its referent.
Kept, each the source's word (agy Q4-Q6): "absolute" (the note's "medians of the absolute residual"); "The bias at a
truth is listed" (Joseph's paragraph 297, "the bias is listed at ..."); "far upward" (the note's, and the base Sec.
VI's).
Every edit is an exact old -> new pair, whitespace-tolerant, that must match exactly once."""
import re, sys
D = sys.argv[1]
def pat(s): return re.compile(r"\s+".join(re.escape(w) for w in s.split()))
p = f"{D}/paper_body.tex"; t = open(p, encoding="utf-8").read()
E = [
 ("S1", r"The principal limitations, each stated with the result it qualifies (Secs.~\ref{sec:method}--\ref{sec:result16}; for the calibrated tests, the companion note), are these.",
  r"Each limitation is stated with the result it qualifies (Secs.~\ref{sec:method}--\ref{sec:result16}; for the calibrated tests, the companion note); the principal ones are these."),
 ("S2", r"\emph{Scope.} The findings apply to the OmniFold implementation, data set, observables, configurations and deformations studied here, not to multidimensional OmniFold in general.",
  r"\emph{Scope.} The findings are those of one OmniFold implementation on one data set, for the observables, configurations and deformations studied here, not of multidimensional OmniFold in general."),
 ("R4", r"An exact binned iterative unfolding with five iterations gives median absolute residuals that agree with those of the boosted-tree estimator in a binned, signal-only and noise-free diagnostic on the \jtNcells{} joint cells and the truth changes used to develop the estimator, at the simulation's detector response.",
  r"An exact binned iterative unfolding with five iterations gives median absolute residuals that agree with those of the boosted-tree estimator. The comparison is a binned, signal-only and noise-free diagnostic on the \jtNcells{} joint cells and the truth changes used to develop the estimator, with the detector response fixed at the simulation's."),
 ("R6", r"In the note's calibrated tests, the same pull displaces", r"In the note's calibrated tests, the same pull toward the prior displaces"),
]
for k, old, new in E:
    m = list(pat(old).finditer(t))
    if len(m) != 1: sys.exit(f"{k}: {len(m)} matches")
    t = t[:m[0].start()] + new + t[m[0].end():]
open(p, "w", encoding="utf-8").write(t); print("r20 fixes applied: %d edits" % len(E))
