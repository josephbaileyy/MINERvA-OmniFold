r"""usage: python3 -I apply_b3_fixes_b4.py ANALYSIS_NOTE_DIR -- r19: the b3 review's fixes (scratchpad REVIEW-b3.md,
ADOPT-AFTER-FIXES, no BLOCKING), agy-b3's two findings, and batch b4 (the Discussion).

b3 fixes:
- S1: the scope paragraph adds "They show no evidence of gain over matched coarse projections." The protected abstract
  still says it, and the body no longer did; the note prints it (main_note.tex:72; sec_joint.tex, the projections).
- S4: tab:result16 becomes a two-column table* at the top of a page, so it does not float past the Discussion: as a
  one-column float it was too tall and went to a float page after the Discussion (p. 10). As table* it sits at the top
  of p. 9, the earliest page free of earlier floats (Sec. V starts on p. 7).
- S5 and agy-b3 Q1: the caption's edge sentence says only what the note establishes: the outer edge of the analysis
  grid, "which contains every signal event", with a pointer to the note's binning section ("the truth grids are
  exhaustive", sec_method.tex). The former "a box that reaches it holds every signal event above its lower edge on
  that axis" was overbroad, because the box is bounded on the other axes.
- S6: the Limitations paragraph's range names the note for the note's tests. Its stale source-map comment is updated.
- agy-b3 Q2: T4's "the comparisons below" becomes "the comparison that follows", singular as in the base.
- NITs:
  - the caption defines the median row, and the table (now two-column) uses footnotesize with 4pt spacing (it was 3.5pt
    overfull);
  - Sec. III B gives q3 in GeV/c with pT and ppar, as the caption and the note do;
  - (c)'s band sentence says "with the flux variances kept" (the correlation variant).

b4, the Discussion (outline K8; review S3):
- The self-referential "Section VI relates three of the validation findings ..." leaves.
- "Two validation findings point to the unfolded result retaining part of its prior" leads the synthesis, and the
  note's calibrated tests follow as one sentence: they show the same pull. This is the outline's K8 ("keeps two
  results"), not move-pass A50's three.
- Stale comments are updated.
Every edit is an exact old -> new pair, whitespace-tolerant, that must match exactly once."""
import re, sys
D = sys.argv[1]
def pat(s): return re.compile(r"\s+".join(re.escape(w) for w in s.split()))
p = f"{D}/paper_body.tex"; t = open(p, encoding="utf-8").read()
E = [
 ("S1", r"and are not physical exclusions of the generators.",
  r"and are not physical exclusions of the generators. They show no evidence of gain over matched coarse projections."),
 ("S5/Q1", r"The largest edge on each axis is the outer edge of the analysis grid, so a box that reaches it holds every signal event above its lower edge on that axis.",
  r"The largest edge on each axis is the outer edge of the analysis grid, which contains every signal event (\nsec{sec:method-binning}). The last row gives the median over the cells."),
 ("NIT tabcolsep", "\\label{tab:result16}\n  \\centering\\scriptsize\\setlength{\\tabcolsep}{3pt}", "\\label{tab:result16}\n  \\centering\\footnotesize\\setlength{\\tabcolsep}{4pt}"),
 ("S6", r"The limitations of these results are stated with the results they qualify, in Secs.~\ref{sec:method}--\ref{sec:result16}.",
  r"The limitations of these results are stated with the results they qualify, in Secs.~\ref{sec:method}--\ref{sec:result16}, and those of the calibrated tests in the companion note."),
 ("S6 comment", r"% (1) Sec. IV B; (2) Sec. IV A; (3) Sec. V C; (4) Sec. V B; (5) Sec. V D; (6) Sec. VII A; (7) Sec. VII D (i);",
  r"% (r19: sections renumbered and Sec. VII D moved to the note, sec:joint5d-conditions; the map below is r18's) (1) Sec. IV B; (2) Sec. IV A; (3) Sec. V C; (4) Sec. V B; (5) Sec. V D; (6) Sec. VII A; (7) Sec. VII D (i);"),
 ("Q2", r"and the sixteen-cell result usable for the comparisons below.", r"and the sixteen-cell result usable for the comparison that follows."),
 ("NIT units", r"one interior edge per axis ($\pT$ \fvval{h2-mid-pt}, $\pPar$ \fvval{h2-mid-pz}~GeV/$c$, $\Eavail$ \fvval{h2-mid-eavail}, $q_3$ \fvval{h2-mid-q3}, $W$ \fvval{h2-mid-W}~GeV)",
  r"one interior edge per axis ($\pT$ \fvval{h2-mid-pt}, $\pPar$ \fvval{h2-mid-pz} and $q_3$ \fvval{h2-mid-q3}~GeV/$c$; $\Eavail$ \fvval{h2-mid-eavail} and $W$ \fvval{h2-mid-W}~GeV)"),
 ("NIT (c)", r"Bootstrapping these universes gives", r"Bootstrapping these universes, with the flux variances kept, gives"),
 ("b4 lead", r"with its covariance and generator comparison.  Section~\ref{sec:limits} relates three of the validation findings to the unfolded result retaining part of its prior, and lists the checks they show to be needed before unfolded intervals are interpreted.",
  r"with its covariance and generator comparison."),
 ("b4 comment 1", r"% The familywise bound conditioned on the calibration's exactness: M2-FWER-RECORD.md:11-14, :58-60.",
  r"% Register round r19 (variant B, K9): the familywise sentence left with the tests (note sec:joint5d-frozen; source M2-FWER-RECORD.md:11-14, :58-60)."),
 ("b4 synthesis", r"Three results point to the unfolded result retaining part of its prior.  The first is",
  r"Two validation findings point to the unfolded result retaining part of its prior.  The first is"),
 ("b4 K8", r"The third is the upward displacement of the external null distributions of the note's calibrated tests by the estimator's pull toward its prior, which the calibration reproduces (\nsec{sec:joint5d-results}).",
  r"The note's calibrated tests show the same pull: their null distributions for the external predictions are displaced upward by it, as the calibration reproduces (\nsec{sec:joint5d-results})."),
 ("b4 comment 2", r"% The common thread of Secs. V B, V C, V E and VII E in the body's own words;",
  r"% Register round r19 (b4; outline K8): two validation findings, then the note's tests in one sentence. The common thread of Secs. V B, V C, V E and VII E (r18 numbering) in the body's own words;"),
 ("b4 comment 3", r"% Each check is one of this paper's studies (Secs. IV-V); the calibration sentence is Sec. I's, whose condition is stated there and in Sec. VII C (register round r15; r18 moved it from Sec. VIII A).",
  r"% Each check is one of this paper's studies (Sec. IV after r19). Register round r19 (K13): the calibration sentence left with the tests; the note's N1 paragraph states it."),
]
for k, old, new in E:
    m = list(pat(old).finditer(t))
    if len(m) != 1:
        sys.exit(f"{k}: {len(m)} matches")
    t = t[:m[0].start()] + new + t[m[0].end():]
# S4: the result table as a two-column float
b = t.index("\\begin{table}[tb]\n  \\caption{The sixteen-cell cross section:"); e = t.index("\\end{table}", b)
assert "\\label{tab:result16}" in t[b:e]
t = t[:b] + "\\begin{table*}[t]" + t[b + len("\\begin{table}[tb]"):e] + "\\end{table*}" + t[e + len("\\end{table}"):]
open(p, "w", encoding="utf-8").write(t); print("b3 fixes and b4 applied: %d edits, the result table as table*" % len(E))
