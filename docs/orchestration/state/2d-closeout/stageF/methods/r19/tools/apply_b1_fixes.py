r"""usage: python3 -I apply_b1_fixes.py ANALYSIS_NOTE_DIR -- r19 b1: the fixes for the independent review (scratchpad
REVIEW-b1.md, ADOPT-AFTER-FIXES) and for agy's Q6.

- B1: K3's sentence regains its scope. "which is not corrected" was false while the paper's tests print their
  target-corrected evaluations, and it lost the note's "as run". It now names the comparison it is about, Sec. V A,
  which says that the comparison has no CH correction.
- B2: the Discussion's "three of them" regains its noun, which the Table I clause had carried.
- S1, and agy's Q6: the joint cells are the supported cells of the coarse grid, not all 243, and they are kept by the
  support rule, not "reported".
- S3: the cells paragraph points to the covariance in IV A (sec:cov16).
- S4: the scope paragraph keeps one sentence on the note's tests with the qualifiers that the protected abstract's
  claim needs: hybrid nulls, calibrated within the simulation model, not physical exclusions. The roadmap's note
  sentence shortens to match.

Every edit is an exact old -> new pair, whitespace-tolerant, that must match exactly once."""
import re, sys

D = sys.argv[1]
def pat(s): return re.compile(r"\s+".join(re.escape(w) for w in s.split()))
P = "paper_body.tex"
t = open(f"{D}/{P}", encoding="utf-8").read()
E = [
 ("B1", r"The NuWro and GiBUU comparisons contain a target difference of this kind, which is not corrected.",
  r"The NuWro and GiBUU comparisons contain a target difference of this kind, which the comparison of Sec.~\ref{sec:gen16} does not correct."),
 ("B2", r"Section~\ref{sec:limits} relates three of them to the unfolded result retaining part of its prior",
  r"Section~\ref{sec:limits} relates three of the validation findings to the unfolded result retaining part of its prior"),
 ("S1", r"The joint cells form a coarse $3^{5}$ grid in $(\pT,\pPar,\Eavail,q_{3},W)$ whose edges are the fine edges nearest the simulated tertiles.  A coarse cell is reported if its expected reconstructed signal and its truth weight at the data exposure are both at least 1000 events.  Of the coarse cells, \jtNcells{} pass.",
  r"A coarse $3^{5}$ grid in $(\pT,\pPar,\Eavail,q_{3},W)$ has as edges the fine edges nearest the simulated tertiles.  A coarse cell is kept if its expected reconstructed signal and its truth weight at the data exposure are both at least 1000 events.  Of the coarse cells, \jtNcells{} pass; these are the joint cells."),
 ("S3", r"and every reported cell passes the support rule.",
  r"and every reported cell passes the support rule. Its covariance is given in Sec.~\ref{sec:cov16}."),
 ("S4 scope", r"The sixteen-cell result of Sec.~\ref{sec:result16} also has total uncertainties, whose coverage is not validated.",
  r"The sixteen-cell result of Sec.~\ref{sec:result16} also has total uncertainties, whose coverage is not validated. The companion note also gives simulation-calibrated tests of the generator predictions; they test hybrid null hypotheses, are calibrated within the implemented simulation model, and are not physical exclusions of the generators."),
 ("S4 roadmap", r"the construction of the uncertainties, and simulation-calibrated tests of the generator predictions with their assumptions, and is cited below by section.",
  r"the construction of the uncertainties, and the tests with their assumptions, and is cited below by section."),
]
for k, old, new in E:
    m = list(pat(old).finditer(t))
    if len(m) != 1:
        sys.exit(f"{k}: {len(m)} matches")
    t = t[:m[0].start()] + new + t[m[0].end():]
open(f"{D}/{P}", "w", encoding="utf-8").write(t)
print("b1 fixes applied: %d edits" % len(E))
