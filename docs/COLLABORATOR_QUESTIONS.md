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

## FOR THE LIVE GREGOR EXCHANGE ON E_avail — drafted 2026-08-14 (lane A, `OI-59`)

**Why this is here and not only in a message.** Joseph is in live correspondence with Gregor Kafka on
E_avail. The `OI-59` caveat is recorded where the number lives (`VALIDATION_LEDGER.md:1349-1367`), but the
*sendable* form existed only in a cross-session message — which is `BEN-201`'s shape: it vanishes when the
sessions holding it end.

**Two sentences, to hand him as-is:**

> Our bin-identical cross-check against Ascencio 2022 passes (full-covariance χ²/ndf = 1.68/2, p = 0.43;
> ours/theirs = 1.092 and 1.063 in the two common low-E_avail cells), but the two sides unfold to
> available-energy axes with different species content — their Eq. 1 admits every final-state particle except
> neutrons, while ours counts only protons, charged pions, neutral pions and photons, and so omits kaons, η,
> strange baryons, antibaryons **and e±** — and the offset that omission produces has the same sign and sits
> in exactly those two cells.
>
> We are not claiming the check fails: at p = 0.43 on 2 degrees of freedom it cannot separate a ~10%
> definitional offset from noise in either direction, which is precisely why we would rather put it in front
> of you now than quote the agreement as physical.

**A CARDINALITY TRAP WAS REMOVED FROM THE FIRST SENTENCE, and the reason is worth keeping.** The draft read
*"their Eq. 1 uses an open species list, ours a closed four-species one."* That is true of our list and
**wrong as a statement of the gap**: placed beside "open species list" in a sentence whose subject is the
Ascencio comparison, "four" reads as the size of the difference, and **against Ascencio the difference is
five species — the fifth being e±, which the open list includes and we exclude.** `docs/EAVAIL_DEFINITION.md`
§2 carries an explicit caution against exactly that construction (*"any count of 'four' here is a count
against Rodrigues, not against Ascencio"*). **The omitted species was the one that cuts against us**, which
is the failure mode that document exists to prevent, so the count is dropped and the species are named.
Caught by the mediator on review.

**If he asks about e± specifically**, the honest answer is that it is the one species where we differ from
**both** published conventions: Rodrigues 2016 explicitly includes *"neutral pion, electron, and photon total
energy"*, Ascencio's open list covers it, and `minerva-ml` includes it — so on e± `minerva-ml` matches the νμ
paper and we do not. Size is small (**1.462 MeV/signal event**, e⁻ 0.239 + e⁺ 1.223); it is the direction of
correctness that flipped, not a large number. Our exclusion follows `GENIEXSecExtract`'s
`abs(pdg)==11||abs(pdg)==13` *"don't count charged lepton"* branch, which was written for a νe analysis where
the primary electron **is** the charged lepton.

**What must NOT be said:** that the cross-check is retracted (it is not), or that the definitional offset is
demonstrated to explain the residual (it is an unexcluded alternative). The closing computation is specified
in `OI-59` and is **frozen** behind `OI-56` pending Joseph's reco-underflow repair decision.

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

**RESOLVED 2026-08-02 (clarified by Joseph):** MINERvA *does* have a 3D unfolding
publication, we already found and cite it, and there is nothing beyond that. So:

  * The question's premise --- "there is no prior MINERvA 3D+ unfolding result to
    use as precedent" --- **was wrong as written**, and any note text repeating it
    must be narrowed. What survives is the narrower and still-true claim: prior
    MINERvA multi-differential results used *binned* unfolding, and the novelty
    here is the *unbinned, simultaneously-unfolded* formulation plus the full
    3D+ unfolded **covariance**, which the prior publication does not provide.
    The note already states it that way in `sec_execsummary.tex` and
    `sec_summary.tex` (both cite `MINERvA:2022qe` and say "the methodological
    distinction is the unbinned, simultaneously-unfolded formulation") --- so the
    note is correct and it was this DOCUMENT's framing that was wrong.
  * **The endorsement question remains unanswered.** "Nothing beyond that" means
    no view was given on publishing the full 1431-bin covariance or its
    rank-deficient GoF treatment. That is still owed, and it is the part that
    actually gates App. A item 5.

Superseded guidance, kept so the reasoning is legible:
~~**DO NOT edit the novelty claim in either direction until this is disambiguated**~~
— guessing it "safe" by dropping "first" discards a real result if the second
reading is right, and leaving it discards a correctness obligation if the first
is. One clarifying question closes it: *is there a MINERvA 3D+ unfolded result,
published or internal, that predates ours, and if so what is it?*

Status: App. A items 2 and 4 close; item 5 stays open, narrowed. `OPEN_ITEMS.md`
item 1 is therefore PARTIALLY closed, not closed.
