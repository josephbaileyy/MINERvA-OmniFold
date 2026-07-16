# July 16 talk — Q&A preparation

Written for a MINERvA collaboration-meeting audience: people who built the
D'Agostini/MAT machinery, the low-recoil conveners, the flux group, and the
data-preservation folks. Ordered by how likely the question is. Each answer
is meant to be spoken in ~30 seconds; backup-slide pointers in brackets.

---

## A. Regularization & method (the unfolding experts will start here)

**Q1. How do you choose the number of iterations? In IBU we have
regularization studies, L-curves, warping studies.**
Iteration count plays exactly the same role here — it *is* the
regularization, together with classifier capacity. We use five iterations
for everything shown. Doubling to ten moves the total cross section by
0.026%, coverage on 200 toys is 68.7% against the 68.27% Gaussian target,
and closure tests recover injected truth changes at five. So the choice is
in the flat region by every metric we track. [B4, slide 13]

**Q2. The T2K OmniFold paper iterated ~45 times. Why are you at 5?**
Their stopping criterion is tailored to their simulated-data studies and is
not feasible on real data; the recent Practical Guide to unbinned unfolding
quotes ~5 as typical. Our own scan says the answer stops moving at the
0.03% level past five — iterating further only adds variance.

**Q3. Isn't the result prior-dependent? You unfold with GENIE as the
starting simulation.**
Same prior dependence class as IBU, and we treat it the same way plus more:
closure under truth reweights and an alternate-model swap, a hidden-
resolution-variable test, and — the strongest one — a bottom-line test: a
fresh classifier trained to separate the unfolded ensemble from the target
can't do it (AUC 0.501, p = 0.17). For the full-phase-space extrapolation,
where prior dependence is the *dominant* concern, we bound it explicitly
with a multi-prior envelope (MnvTune / bare GENIE / NuWro). [slide 13, B10]

**Q4. Choosing bins after unfolding sounds like a recipe for
look-elsewhere / p-hacking.**
Two protections. The anchor analyses are pre-registered in effect — the 2D
reproduction uses the published binning, decided before we looked. And every
quoted comparison carries a covariance computed *for that binning* from the
same universe machinery, so re-binning never recycles a stale covariance.
The freedom is in presentation, not in the statistical statement.

**Q5. Why GBDTs? Everyone else uses deep networks for OmniFold.**
Deliberate. At ≤ ~10 scalar features, gradient-boosted trees are as accurate,
far cheaper, and much more stable to retrain — and stability matters because
the uncertainty budget includes retraining response. An independently tuned
Keras MLP run through the identical pipeline agrees to 1.008 in total cross
section. Deep networks only earn their cost for point-cloud inputs, which is
exactly where we use one (the PET study). [B3, B9]

**Q6. With binned inputs it "reduces to IBU" — exactly, or approximately?**
Exactly, in the sense that with indicator-function inputs and per-bin
weights, the two-step OmniFold update is algebraically the IBU update. It's
a theorem from the original OmniFold paper, and we verified it numerically
on our setup. [B1]

## B. Uncertainties & statistics (the MAT crowd)

**Q7. How does the statistical uncertainty of the data get in? Bootstrap?
And is the ML noise separated from it?**
Data statistics enter via bootstrap replicas of the unfold; ML training
stochasticity is a separate block, measured by seed *and* train/test-split
ensembles. The split-varied ML band is 1.24× the pure-seed band in 2D, and a
fixed-data estimator-seed scan reproduces 87.5% of the adopted 5D ML band —
so the ML term is genuine training stochasticity, and it stays a minor
(~3%) component of the budget. [B5]

**Q8. Which systematics did you propagate, and how do detector shifts that
move reco kinematics work in an unbinned unfold?**
All vertical universes from the data release reweight events and re-unfold.
Lateral universes — shifted reco kinematics — are re-dumped with shifted
inputs and re-unfolded per universe, since the classifier must see the
shifted features. The rebuilt 2D budget matches the published one: median
per-bin 6.87% vs 6.86%, same band ordering. [slide 12, B7]

**Q9. Your χ²/ndf of 3.66 against our covariance — is that agreement or
not?**
Per-bin, everything is sub-1σ (pulls: mean 0.09, RMS 0.60). The 3.66 comes
from correlated shape modes along the low-pT peak ridge — the full
covariance knows the bins move together, and our result rides the edge of
those modes; it is not a normalization tension (total σ ratio 1.011).
Including our own covariance gives 1.48. And one step deeper: the paper's
quoted covariance is stat-dominated in rank; when we swap only the
statistical block, the χ² structure follows it — anatomy in the note's
statistics appendix. [B6b]

**Q10. The stat uncertainty is ~100% correlated between your result and
ours — same data. Shouldn't the pulls be much narrower than unit Gaussian?**
Yes — and they are; that's exactly the right reading. Common data
fluctuations cancel in the difference, so the RMS of 0.60 is not "0.6σ of
statistical scatter," it's the method difference — regularization scheme,
unfolding model, ML stochasticity — measured against the published σ as a
yardstick. A unit-Gaussian pull was never the expectation. [B6b]

**Q11. Rank 201 of 205 bins — how do you invert that for a χ²?**
Truncated-spectral pseudo-inverse, retaining eigenvalues above 1e-10 of the
maximum, always quoted alongside per-bin pulls and a truncation-stability
scan. This is one of our three explicit questions to the collaboration — if
MAT has a preferred convention, we'll adopt it. [slide 22]

**Q12. What's in the ML uncertainty band that a binned analysis doesn't
have, and how big is it?**
Training stochasticity (seeds), train/test-split choice, and retraining
response under systematic shifts. In 2D it rides the bottom of the budget;
in 5D it's ~3% of the total. It is the additional term the method
introduces, and it is small. [B5, B7]

## C. Backgrounds, efficiency, implementation

**Q13. How do you subtract backgrounds inside an unbinned unfold?**
Per-reco-bin purity weights derived from the simulation, applied to data
before the unfold — the unbinned analogue of the sideband-constrained
subtraction in the published analyses, validated with a negative-weight
cross-check (sub-2% RMS agreement). Worth saying plainly: *no* published OmniFold analysis has
solved in-unfold background subtraction more generally — we scanned the
literature — so we regard our treatment as a defensible middle ground and
say so in the note. [B2]

**Q14. Efficiency and acceptance — where do they enter?**
Same bookkeeping as always, carried as event weights: reconstructed signal
is accepted only if its truth key is in the authoritative truth tree,
truth-only events enter as native misses, and the efficiency correction is
applied in the cross-section extraction — completeness is 1 by construction,
so there's no double efficiency division. [B1b, B2]

**Q15. Which data product exactly, and could we reproduce this?**
The public ME FHC CC-inclusive release: four flat trees per playlist, twelve
ME playlists, flux and POT from the release. No internal MINERvA software.
The release was rich enough to carry a full independent re-analysis
including systematics — a data-preservation result in itself.

## D. Physics results (low-recoil conveners)

**Q16. The low-recoil dip-filling is known. What's actually new here?**
Three things. The method independence of the recovery — same physics from a
different unfolding paradigm. The dimensionality — E-available, q3, W
simultaneously with muon kinematics, which the binned analyses could not do.
And the localization: the residual that 2p2h does *not* explain concentrates
at high E-available and W above ~1.8 GeV — the DIS corner — consistently
against GENIE+MnvTune, bare GENIE, NuWro, and GiBUU.

**Q17. What significance do you put on that excess?**
None today, deliberately. The corrected 5D covariance exists, but this
plane's significances haven't been requoted against it, so the claim is
shape-level localization only. The number comes with the note, not the
talk. [B7, B7b]

**Q18. Did you compare with the low-q3 analysis (Ascencio et al.)?**
Yes — against their supplemental data, χ²/ndf = 1.68/2 on the comparable
projection. Consistent.

**Q19. GiBUU disagrees with everything — did you tune it?**
No tuning: native GiBUU 2019, default settings. It is the most deficient of
the four generators, about −22% integrated, and it underpredicts the same
DIS corner. Its presence is there to show the excess isn't an artifact of
the GENIE family.

## E. Outlook, practicalities, and the elephant

**Q20. What would the collaboration actually get from this — what's the
deliverable?**
A weighted-event data product: per-event truth kinematics plus OmniFold
weights, with a universe-resolved covariance recipe, so any binning or
observable within the 5D space inherits the full uncertainty treatment.
That's also my main ask today: which projections would you most want?

**Q21. You said AI agents helped with everything. Why should we trust it?**
The conclusions do not rest on who wrote the code; they rest on the
cross-checks. Every load-bearing number has an independent check that would
catch an error: the published-result reproduction, the rebuilt uncertainty
budget matching the published one, closure, coverage, an independent
classifier family, and the bottom-line two-sample test. We verified all of
it and take responsibility for it. AI assistance changed the speed of the
work, not the standard of evidence applied to it.

**Q22. Point-cloud unfolding of calorimeter clusters — how do you validate
something with no binned analogue? And is the muon in the cloud?**
The current result is deliberately scoped: a *recoil-only* point-cloud
representation cross-check. Step 1 takes the non-muon reconstructed recoil
clusters, step 2 the truth hadrons; muon kinematics enter only through
selection and downstream binning — the muon is absent from both
classifiers. Validation anchors are the same as everywhere else: its
marginals reproduce the scalar-pipeline results, with the identical
uncertainty-block machinery including a targeted retraining-response term.
One caveat we state ourselves: ordinary closure validates the machinery but
cannot test omitted muon dependence at fixed recoil. A muon-inclusive
full-event interface and an omitted-variable stress closure are in
progress; the nominal result and uncertainties will be repeated with them.
The 2D and scalar GBDT results are unaffected by this scoping. [B9]

**Q23. Full phase space: extrapolating into the dead region is just quoting
your prior, isn't it?**
In the never-reconstructed region, largely yes — which is why we report in
two tiers: measurement-dominated in-acceptance, prior-dominated
extrapolation with a multi-prior envelope as its uncertainty, never blended.
The pilot's interior anchor agrees with the restricted-phase-space result at
the percent level. The extended-fiducial result is labeled preliminary —
roughly 6% of the rate is opened but acceptance-supported, roughly 28% is
prior-dominated — with the final corrected uncertainties pending. [B10]

**Q23b. Earlier material called the point-cloud work "full phase space" /
"full event" — what changed?**
Terminology and scope, not numbers. The PET run itself is unchanged and its
agreement with the scalar pipeline stands; what changed is the label — the
classifiers see only the recoil system, so we now call it a recoil-only
representation cross-check and treat the full-event version as in-progress
work. The 2D reproduction and the scalar GBDT 3D/4D/5D results are not
involved in this correction at all.

---

## Three questions we are asking *them* (slide 22 — push if unanswered)

1. **FrInel_pi** exclusion from the standard band list — still current MAT
   guidance? (Immaterial for us — both pion-FSI dials ≤ 0.8% on
   dσ/dE_avail — we just want the citation right.)
2. **Ours-only χ² convention** for rank-deficient covariances — precedent or
   preferred alternative?
3. **Publishing a full 3D+ systematic covariance** (1431 bins, rank 247) —
   would the collaboration endorse it?

If a MAT maintainer or low-recoil convener is in the room, ask them to grab
you afterwards — answers slot directly into note App. A and close
OPEN_ITEMS #1.
