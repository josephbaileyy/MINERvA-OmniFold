# D1: the meaning read of the adopted 2D covariance's paper changes (2026-11-16)

**What it read:** prep/d1-cnew-20261114 at 44eefd942, against the draft (the three-dot diff). That covers the printed
sentences and values that D1 changes:
- §3.2's correction clause, and the deletion of §7.1's approximation item;
- S6.1's comparison sentence;
- the T2A top-32 shares;
- every C_new-dependent key;
- Figure 1;
- the macro guard.

The reader was an independent general-purpose subagent, read-only.

**Verdict: MINOR. No defect in D1's content:**
- §3.2's clause matches COV2D-G2R-DECLARATION.md §10's VALID row, and it holds for all 185 universes (§1).
- Nothing printed still states the uncorrected approximation.
- S6.1's values are data_g2r's [0], and its "same joint counts and flagged cells" is true of the old and new score
  records.
- The top-32 shares recompute as 1.207 % and 0.663 %.
- Every changed value comes from a C_new record: q2d-sigma 6.46/4.76; qr-cmodel 7.93; fluxband 3.72; cov2d-chi2ndf;
  t2a; re2comb 33.8/2.60; x-chi2-hi 1.24, rounded up; cr.
- No pre-D1 value is printed, apart from re2per-chi2-pz (34.4), which is labelled "against the earlier two-dimensional
  budget" on purpose.
- Figure 1 is 1ead58a2, and its inset reads 6.46 %.
- The guard covers every covariance-dependent macro the paper prints.

**Notes and their disposition:**
- **The merge conflict with the draft's B8 (supplemental_body.tex S6):** resolved in 823632d34 as B8's wording with D1's
  key q2d-qr-cmodel-med. \qrCmodelMedian no longer appears.
- **The macro list was fixed:** it now also covers rhoFluxMuon, nwSystRatio and covTwoD*. None is printed.
- **For the note lane:** sec_systematics.tex :218 and :237 still say the approximation "is not corrected". The §10 row
  replaces the covariance in the note as well. Sent to director-helper-2.
- **S6.1's comparison sentence reads abruptly** after the comparator sentences. It is correct; the placement was
  journal-editor's, and the note is passed on.
