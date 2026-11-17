# Fix requested by the director, 2026-11-16: which figure shows which pseudo-experiments (sec_5d.tex, §9.3)

Not a cutdown row. From the director's cross-document check at paper `3d4d33144` and note `8342963c1`.

**Base:** `sec_5d.tex:78` at `8342963c1`, last sentence of the paragraph.

**Old:** "The pseudo-experiments of the paper's recovery figure, sixty for the development variant at the
GiBUU-to-GENIE E_avail shape and twenty for each of three shapes not used in the joint-test estimator's selection,
use seed sets that were not held out from the estimator's development."

**New:** "The sixty pseudo-experiments of the Supplement's recovery figure for the development variant,
configuration (d), at the GiBUU-to-GENIE E_avail shape, and the twenty for each of the three shapes not used in the
joint-test estimator's selection in the paper's recovery figure, which shows configuration (e), use seed sets that
were not held out from the estimator's development."

**Sources read at paper `3d4d33144`.**
- `paper_body.tex`, the caption of `fig:deformation` (the paper's recovery figure): "for the reported five-observable
  estimator, one panel per changed truth: NuWro E_avail, GENIE + MEC (E_avail,W) and NuWro (p_T,p_∥,E_avail) shapes and
  the GiBUU-to-GENIE E_avail shape … Markers: means over 20 pseudo-experiments".
- `supplemental_body.tex`, the caption of `fig:supp-lowcap` (the Supplement's first figure): the "configuration of the
  companion note's generator-sized-change study", "which differs from the reported five-observable estimator:
  GiBUU/GENIE E_avail shape, 60 pseudo-experiments". In this note that study's configuration is (d)
  (Table tab:estimators-matrix; §9.2).
The note has no label macro for a figure of the paper or of the Supplement, so both are named in words.

**Meaning read** (the editor's own, not an independent model's).
(a) Does the sentence still say what it said, or less? The claim is unchanged: the same two sets of
pseudo-experiments (sixty; twenty for each of three shapes) use seed sets that were not held out. What changes is
where each set is shown and which configuration it is. The sentence makes no statement about the paper figure's
fourth panel (configuration (e) at the GiBUU-to-GENIE shape), as before.
(b) Do antecedents and pointers hold? "the development variant" is the paragraph's own term; "(d)" and "(e)" are
defined in §3.2 and its table. "the three shapes not used in the joint-test estimator's selection" are the NuWro and
GENIE + MEC shapes of the paragraph "Unfolding-model dependence" below and of §9.4.
