# Collaborator confirmation requests (ready to send)

The three open items in the analysis note that need a MINERvA/MAT collaborator
answer rather than further work on our side. Drafted 2026-06-12 so they can be
sent as-is (e.g. to the MAT maintainers / low-recoil conveners); answers slot
directly into the relevant note sections (`sec_eavailw`, `sec_systematics`).

---

**Subject: three quick confirmations for an OmniFold CC-inclusive ME analysis**

Dear all,

I am finalizing an unbinned (OmniFold) cross-section analysis of the ME FHC
CC-inclusive sample (2D muon kinematics reproduction of Ruterbories et al.,
plus 3D/4D/5D extensions in E_avail, q3, and W, with a full systematic
covariance). Three points where I'd like to confirm we are aligned with
collaboration practice:

1. **FrInel_pi exclusion.** The public MAT-MINERvA standard-systematics
   registry comments out GENIE `FrInel_pi` in both its vector and map builders,
   with the source comment that the knob should not currently be evaluated but
   should eventually be revisited
   ([vector builder, lines 36–38](https://github.com/MinervaExpt/MAT-MINERvA/blob/c20ad220e95f55b4ef2e9426c56dd2a3800f7533/universes/GenieSystematics.cxx#L36-L38);
   [map builder, lines 90–92](https://github.com/MinervaExpt/MAT-MINERvA/blob/c20ad220e95f55b4ef2e9426c56dd2a3800f7533/universes/GenieSystematics.cxx#L90-L92)).
   `git blame` traces those lines to the repository's initial public commit on
   2021-07-07
   ([commit `69e841e`](https://github.com/MinervaExpt/MAT-MINERvA/commit/69e841ef53e336090dee7db25b70b8562bae76dc));
   they remain unchanged on upstream `main` as of 2026-03-05. An independent
   `grwght1p` pass on our CV sample shows both pion-FSI dials are sub-percent on
   dsigma/dE_avail (FrInel_pi <= 0.74%, FrAbs_pi <= 0.82%), so the exclusion is
   immaterial for us either way — could you confirm that this historical
   guidance is still endorsed, so we can cite it as current collaboration
   practice?

2. **"Ours-only" chi^2 convention.** For generator comparisons we quote a
   goodness-of-fit using only OUR covariance (C_syst + C_stat + C_ML; rank 201
   of 205 bins in 2D), inverted via a truncated-spectral pseudo-inverse
   (retain lambda > 1e-10 lambda_max), led by per-bin pulls and a
   regularization scan. Is there published MINERvA / MAT-based precedent for
   this ours-only convention in unbinned or OmniFold-style analyses, or a
   preferred alternative?

3. **Publishing the first MINERvA 3D+ unfolded covariance.** There is no prior
   MINERvA 3D+ unfolding result to use as precedent. Our E_avail extension
   carries a full combined covariance over all 1431 reported 3D bins (rank
   247), with the same truncated-spectral GoF. Would the collaboration endorse
   publishing this full covariance and using this GoF treatment for its
   rank-deficient form?

Happy to share the analysis note (61 pp) or any of the validation artifacts.

Thanks,
Joseph

---

Status tracking: answers go into App. A items 2 (FrInel_pi), 4 (ours-only
chi^2), 5 (endorsement of the first 3D+ unfolded covariance); then
`docs/OPEN_ITEMS.md` item 1 closes.

---

## ANSWERS RECEIVED — 2026-08-02 (asked in person at the presentation, a few weeks prior)

Recorded as reported by Joseph. Not a written reply, so there is no citable
thread; treat these as verbal collaboration guidance and say so wherever the
note leans on them.

**1. FrInel_pi exclusion — CONFIRMED, and for a different reason than the source
comment gives.** The exclusion is still current practice. The stated reason is
**not** that the knob is individually broken: there is a set of dials with
overlapping / circularly dependent effects, and any *one* of them has to be
commented out to break the degeneracy. `FrInel_pi` is the one that happens to be
commented out.

That reframes what we may claim. The MAT source comment ("should not currently
be evaluated but should eventually be revisited") reads as a defect in that
knob; the real reason is a degeneracy among several, which makes the *choice* of
which to drop conventional rather than physical. Our own evidence is unaffected
and still does the work — the `grwght1p` pass shows FrInel_pi <= 0.74% and
FrAbs_pi <= 0.82% on dsigma/dE_avail, so the exclusion is immaterial for this
measurement either way. Cite the practice as endorsed, cite the degeneracy as
the reason, and do NOT repeat the source comment's implication that the knob is
individually suspect.

**2. Ours-only truncated-spectral chi^2 — CONFIRMED, precedent exists.** The
collaboration does the same truncated-spectral pseudo-inverse. This closes the
"published precedent" gap that `sec_summary.tex` and `app_statmethods.tex` both
list as a wanted paper-independent refinement. Note it was confirmed as
*practice*, not as a citation — if the note wants a reference rather than
"consistent with collaboration practice", that is a follow-up ask.

**3. First MINERvA 3D+ unfolded covariance — NOT RESOLVED, and it got more
complicated.** Reported answer: *"They do have the 3d unfolding result and they
want to keep in touch and hear how my progress is going."*

Two problems with treating that as an answer:

  * **The endorsement question was not answered.** We asked whether the
    collaboration would endorse publishing the full covariance over all 1431
    reported 3D bins (rank 247) and its rank-deficient GoF treatment. The reply
    is about having a result and staying in touch, not about endorsement.
  * **It may contradict the question's own premise.** The question asserts
    "There is no prior MINERvA 3D+ unfolding result to use as precedent." If the
    collaboration has a 3D unfolding result, that premise is false and the
    novelty claim built on it has to change. The sentence is ambiguous between
    *they have their own 3D unfolding result* (premise false, novelty claim
    moves) and *they have received/seen ours* (premise intact).

**DO NOT edit the novelty claim in either direction until this is disambiguated**
— guessing it "safe" by dropping "first" discards a real result if the second
reading is right, and leaving it discards a correctness obligation if the first
is. One clarifying question closes it: *is there a MINERvA 3D+ unfolded result,
published or internal, that predates ours, and if so what is it?*

Status: App. A items 2 and 4 close; item 5 stays open, narrowed. `OPEN_ITEMS.md`
item 1 is therefore PARTIALLY closed, not closed.
