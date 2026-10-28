r"""usage: python3 -I apply_b1n_fixes.py ANALYSIS_NOTE_DIR -- r19: fixes after the second review (scratchpad
REVIEW-b1n.md, ADOPT-AFTER-FIXES, no BLOCKING) and agy's second pass (r19/agy-b1n).
- agy Q4, review NIT: "Its covariance" -> "The result's covariance" (unclear antecedent).
- Review NITs: the coarse-grid sentence reads plainly; "These comparisons" after the K3 sentence becomes "The
  comparisons" (it was ambiguous).
- F5: N1's one spliced sentence is split back into the paper's two sentences.
- NIT: N4 says "With noise-free pseudo-data", the phrase of the sentence before it, not "In these noise-free studies".
Every edit is an exact old -> new pair that must match exactly once."""
import re, sys
D = sys.argv[1]
def pat(s): return re.compile(r"\s+".join(re.escape(w) for w in s.split()))
E = {"paper_body.tex": [
      ("Q4", r"Its covariance is given in Sec.~\ref{sec:cov16}.", r"The result's covariance is given in Sec.~\ref{sec:cov16}."),
      ("grid", r"has as edges the fine edges nearest the simulated tertiles.", r"has its edges at the fine edges nearest the simulated tertiles."),
      ("These", r"These comparisons of the predictions with the analysis definitions are given", r"The comparisons of the predictions with the analysis definitions are given")],
     "sec_joint.tex": [
      ("F5", r"without simulating each generator through the detector; for hypothesis tests the advantage is smaller.", r"without simulating each generator through the detector. For hypothesis tests the advantage is smaller.")],
     "sec_5d.tex": [
      ("N4", r"In these noise-free studies, thirty iterations reduce", r"With noise-free pseudo-data, thirty iterations reduce")]}
for f, edits in E.items():
    p = f"{D}/{f}"; t = open(p, encoding="utf-8").read()
    for k, old, new in edits:
        m = list(pat(old).finditer(t))
        if len(m) != 1: sys.exit(f"{f} {k}: {len(m)} matches")
        t = t[:m[0].start()] + new + t[m[0].end():]
    open(p, "w", encoding="utf-8").write(t)
print("b1n fixes applied")
