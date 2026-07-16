# July 16 talk — Q&A preparation

Written for a mixed MINERvA collaboration-meeting audience: some people will
know the D'Agostini/MAT machinery in detail, while others will know the
method but not the abbreviation IBU. Define it once as "D'Agostini iterative
Bayesian unfolding (IBU)." Questions are ordered by likely topic; each answer
is meant to be spoken in ~30 seconds. Backup-slide pointers are in brackets.

---

## A. Regularization & method (the unfolding experts will start here)

**Q1. How do you choose the number of iterations? In D'Agostini iterative
Bayesian unfolding (IBU) we have
regularization studies, L-curves, warping studies.**
Iteration count plays exactly the same role here — it *is* the
regularization, together with classifier capacity. We use five iterations
for everything shown. Doubling to ten moves the total cross section by
0.026%, and closure tests recover injected truth changes at five. The existing
2D toys provide a Gaussianity/pull diagnostic, not coverage, because their MC
bootstrap also fluctuates the stored truth reference. [B4, slide 13]

**Q2. The T2K OmniFold paper iterated ~45 times. Why are you at 5?**
Their stopping criterion was tailored to their simulated-data study and is
not the criterion used here. The recent Practical Guide to unbinned
unfolding quotes about five as typical, but our choice comes from our own
scan: the total cross section changes by 0.026% between five and ten, while
the three closure families pass at five.

**Q3. Isn't the result prior-dependent? You unfold with GENIE as the
starting simulation.**
The prior dependence is the same class of issue as in IBU. We test closure
under truth reweights, an alternate-model swap, and a hidden-resolution
variable. A separate descriptive two-sample test moves from AUC 0.535 before
unfolding to 0.501 afterward. It is not a calibrated goodness-of-fit test and
no p-value is quoted. For the
full-phase-space extrapolation,
where prior dependence is the *dominant* concern, we bound it explicitly
with a multi-prior envelope (MnvTune / bare GENIE / NuWro). [slide 13, B10]

**Q4. Choosing bins after unfolding sounds like a recipe for
look-elsewhere / p-hacking.**
Two protections. The 2D reproduction uses the published binning, fixed before
this comparison. A covariance-dependent statement is made only when a matching
validated covariance exists for that projection; otherwise the higher-dimensional
comparison is explicitly shape-level. Re-binning never recycles a stale covariance.

**Q5. Why use GBDTs instead of a neural network?**
At this feature count, gradient-boosted trees are inexpensive to retrain,
which matters because systematic studies require many complete unfolds.
An independently tuned
Keras MLP run through the identical pipeline agrees to 1.008 in total cross
section. A neural architecture is used for the variable-length point-cloud
study, where a fixed scalar feature table is not the input. [B3, B9]

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
fixed-data estimator-seed scan reproduces 87.5% of the candidate 5D ML band.
The final higher-dimensional budget remains gated on selection-complete
laterals. [B5]

**Q8. Which systematics did you propagate, and how do detector shifts that
move reco kinematics work in an unbinned unfold?**
All vertical universes from the data release reweight events and re-unfold.
Lateral universes — shifted reco kinematics — must be re-dumped with shifted
selection and inputs, then re-unfolded per universe. That contract is complete
for the finalized 2D result; the selection-complete higher-dimensional event
loops are still running. The rebuilt 2D budget matches the published one: median
per-bin 6.87% vs 6.86%, same band ordering. [slide 12, B7]

**Q9. Your χ²/ndf of 3.66 against our covariance — is that agreement or
not?**
Using the published per-bin uncertainty as a descriptive scale, everything is
sub-1σ (mean 0.09, RMS 0.60). The indicative 3.66-per-bin distance comes
from correlated shape modes along the low-pT peak ridge — the full
covariance knows the bins move together, and our result rides the edge of
those modes; it is not a normalization tension (total σ ratio 1.011).
Using the sum of our covariance and the paper covariance gives 1.48 as a
diagnostic, not a formal compatibility test, because the shared-data
cross-covariance is unavailable. And one step deeper: the paper's
quoted covariance is stat-dominated in rank; when we swap only the
statistical block, the χ² structure follows it — anatomy in the note's
statistics appendix. [B6b]

**Q10. The two results use the same data. Shouldn't their statistical
fluctuations be highly correlated and the pulls narrower than a unit
Gaussian?**
Yes; a unit-Gaussian pull is not the expectation for two analyses of the
same events. The RMS of 0.60 uses the published per-bin uncertainty only as
a scale for the observed method difference. Quantifying the cancellation
exactly would require the cross-covariance, which is not available. [B6b]

**Q11. Rank 201 of 205 bins — how do you invert that for a χ²?**
Truncated-spectral pseudo-inverse, retaining eigenvalues above 1e-10 of the
maximum, always quoted as an indicative distance alongside per-bin standardized
differences and a truncation-stability
scan. This is one of our three explicit questions to the collaboration — if
MAT has a preferred convention, we'll adopt it. [slide 22]

**Q12. What's in the ML uncertainty band that a binned analysis doesn't
have, and how big is it?**
Training stochasticity includes estimator seeds and train/test-split choice.
Response to a physical systematic belongs in that systematic's end-to-end
varied-and-retrained shift; it is not an independent ML covariance to add.
In finalized 2D the ML band rides the bottom of the budget. [B5, B7]

## C. Backgrounds, efficiency, implementation

**Q13. How do you subtract backgrounds inside an unbinned unfold?**
Per-reco-bin purity weights derived from the simulation are applied to data
before the unfold. This preserves a non-negative classifier target and is
validated against an explicit negative-weight subtraction, with sub-2% RMS
agreement. The background estimate is therefore still binned at reco level;
we do not claim a fully unbinned background model. [B2]

**Q14. Efficiency and acceptance — where do they enter?**
Same bookkeeping as always, carried as event weights: reconstructed signal
is accepted only if its truth key is in the authoritative truth tree,
truth-only events enter as native misses, and the efficiency correction is
applied in the cross-section extraction — completeness is 1 by construction,
so there's no double efficiency division. [B1b, B2]

**Q15. Which data product exactly, and could we reproduce this?**
The public ME FHC CC-inclusive release: four flat trees per playlist, twelve
ME playlists, flux and POT from the release. No non-public MINERvA software.
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
the four generators, about −28% integrated, and it underpredicts the same
DIS corner. Its presence is there to show the excess isn't an artifact of
the GENIE family.

## E. Outlook, practicalities, and provenance

**Q20. What would the collaboration actually get from this — what's the
deliverable?**
A weighted-event data product: per-event truth kinematics plus OmniFold
weights, with a universe-resolved covariance recipe. Recorded truth features
can be projected into new reporting bins, but each projection still requires
the matching validated covariance and support checks.
That's also my main ask today: which projections would you most want?

**Q21. How was the AI-assisted work checked?**
No quoted result is accepted from tool output alone. The checks are the same
ones shown in the talk: reproduction of the published result, independent
uncertainty propagation, closure, iteration and pull diagnostics,
an independent classifier family, and a descriptive two-sample test. The analysis authors reviewed the code
and remain responsible for the claims. The disclosure describes the tools
used; it is not part of the evidence for the result.

**Q22. Point-cloud unfolding of calorimeter clusters — how do you validate
something with no binned analogue? And is the muon in the cloud?**
The current result is deliberately scoped: a *recoil-only* point-cloud
representation cross-check. Step 1 takes the non-muon reconstructed recoil
clusters, step 2 the truth hadrons; muon kinematics enter only through
selection and downstream binning — the muon is absent from both
classifiers. Validation anchors are the same as everywhere else: its
marginals reproduce the scalar-pipeline central values. Its historical
uncertainty total is quarantined because nuisance and retraining shifts need a
joint covariance and detector membership was support-limited. One caveat we state ourselves: ordinary closure validates the machinery but
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

**Q24. If the background estimate and final spectra use bins, in what sense
is this analysis unbinned?**
The unfolding map is learned from event-level coordinates and returns one
truth weight per simulated event; there is no response-matrix binning in the
OmniFold update. Two operations remain binned by design: the reco-level
purity estimate used for background subtraction, and the final presentation
of a cross section. Calling the unfold unbinned does not mean every auxiliary
estimate is unbinned. [B1b, B2]

**Q25. Did you compare OmniFold and D'Agostini IBU on exactly the same
inputs, rather than only comparing both with the paper?**
Yes, on the one-dimensional projections built from the same Phase-18 input.
IBU and the 2D OmniFold result agree at about the 1–2% level, and both track
the published projections at about the same level. We do not claim a
five-dimensional IBU comparison; constructing that sparse response matrix
is the scaling problem motivating this work.

**Q26. The published and OmniFold results use the same data. Can their two
covariances simply be added to obtain the 1.48 χ²/ndf?**
Not for a formal compatibility test. The data-statistical components are
correlated, and the cross-covariance is unavailable. We therefore quote
3.66 against the paper covariance as the primary full-covariance comparison
and show 1.48 from the covariance sum only as a diagnostic. A formal
difference test would require a joint bootstrap or another estimate of the
cross-covariance. [B6b]

**Q27. How do you know the classifier is not extrapolating in regions where
the simulation has no support?**
Inside the published phase space, native truth-only misses retain the truth
denominator, the global OmniFold-input completeness is one by construction,
and closure and the final two-sample test probe the populated support. The
full-muon-phase-space study is different: regions without reconstructed
support are labeled prior-dominated and reported separately with a
multi-prior envelope. We do not describe those regions as measured by data.
[B1b, B10]

**Q28. Are the pull and AUC 0.501 diagnostics independent of the choices used
to tune the method?**
They test different properties, but neither is an inferential test. The 2D pull
summary uses the same ensemble for centering and width estimation, and its
stored truth is MC-bootstrap-fluctuated, so I call it a Gaussianity check and
quote no coverage. The two-sample classifier
checks residual separability, but the weights are not cross-fitted through the
full pipeline, so it also has no calibrated p-value. Neither number selects the
model; iteration stability, closure, and the classifier-family cross-check are
reported separately. [slide 13,
B3–B5]

---

## Three questions we are asking *them* (slide 22 — push if unanswered)

1. **FrInel_pi** exclusion from the standard band list — still current MAT
   guidance? (Immaterial for us — the pion-FSI maxima are 0.74% and 0.82% on
   dσ/dE_avail — we just want the citation right.)
2. **Single-measurement-covariance χ² convention** for rank-deficient covariances — precedent or
   preferred alternative?
3. **Publishing a full 3D+ systematic covariance** (1431 bins, rank 247) —
   is there MINERvA precedent or a preferred release format?

If a MAT maintainer or low-recoil convener is in the room, ask them to grab
you afterwards — answers slot directly into note App. A and close
OPEN_ITEMS #1.
