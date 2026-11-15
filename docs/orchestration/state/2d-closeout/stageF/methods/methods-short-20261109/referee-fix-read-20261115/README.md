# Draft-side referee fixes: the meaning read (2026-11-15)

**What changed:** six paper_body.tex edits answering the codex referee report at 3d75ed5d4
(`~/codex-reports/referee-paper-3d75ed5d4….md`). The director split the paper side to director-helper-3. The edits:
- Minor 2: §3.2's traces are of C_model's fractional form.
- Minor 5: the χ² degrees-of-freedom convention is narrowed to total-distance comparisons, with the shape-only and
  coverage conventions stated.
- Minor 6: Table 4's recovery row names the supported (E_avail, W) cells and the residual relative to the changed
  truth.
- The conclusions' quadrant claim is scoped to the tested family of cross-covariances.
- Table 6's RMS is defined as that of b_c, relative to the prior cross section.

**The read:** `MEANING.txt`, an independent read-only subagent of `diff-as-read.txt`. Verdict DEFECT: §3.2's
fractional-trace denominators. That and one wording note are fixed; the disposition is at the end of MEANING.txt.
