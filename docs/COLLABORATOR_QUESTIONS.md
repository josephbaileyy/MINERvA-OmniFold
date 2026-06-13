# Collaborator confirmation requests (ready to send)

The three open items in the analysis note (App. A, `sec_openquestions.tex`)
that need a MINERvA/MAT collaborator answer rather than further work on our
side. Drafted 2026-06-12 so they can be sent as-is (e.g. to the MAT
maintainers / low-recoil conveners); answers slot directly into App. A.

---

**Subject: three quick confirmations for an OmniFold CC-inclusive ME analysis**

Dear all,

I am finalizing an unbinned (OmniFold) cross-section analysis of the ME FHC
CC-inclusive sample (2D muon kinematics reproduction of Ruterbories et al.,
plus 3D/4D/5D extensions in E_avail, q3, and W, with a full systematic
covariance). Three points where I'd like to confirm we are aligned with
collaboration practice:

1. **FrInel_pi exclusion.** MAT historically excludes the GENIE `FrInel_pi`
   dial from the standard band list. An independent `grwght1p` pass on our CV
   sample shows both pion-FSI dials are sub-percent on dsigma/dE_avail
   (FrInel_pi <= 0.74%, FrAbs_pi <= 0.82%), so the exclusion is immaterial for
   us either way — could you confirm the exclusion is still current MAT
   guidance, so we can cite it as such?

2. **"Ours-only" chi^2 convention.** For generator comparisons we quote a
   goodness-of-fit using only OUR covariance (C_syst + C_stat + C_ML; rank 201
   of 205 bins in 2D), inverted via a truncated-spectral pseudo-inverse
   (retain lambda > 1e-10 lambda_max), led by per-bin pulls and a
   regularization scan. Is there published MINERvA / MAT-based precedent for
   this ours-only convention in unbinned or OmniFold-style analyses, or a
   preferred alternative?

3. **Publishing a 3D+ systematic covariance.** Our E_avail extension carries a
   full combined covariance over all 1431 reported 3D bins (rank 247), with
   the same truncated-spectral GoF. Is there MINERvA precedent for publishing
   a 3D systematic covariance from the low-recoil samples, and would the
   collaboration endorse this GoF treatment for a rank-deficient covariance?

Happy to share the analysis note (61 pp) or any of the validation artifacts.

Thanks,
Joseph

---

Status tracking: answers go into App. A items 2 (FrInel_pi), 4 (ours-only
chi^2), 5 (3D covariance); then `docs/OPEN_ITEMS.md` item 1 closes.
