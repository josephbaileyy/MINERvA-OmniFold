# July 16 talk — 20-minute script

Main deck = slides 1–23 (backup B1–B10 behind the divider). Times are
cumulative targets; the deck's animated slides (3, 5, 7, 14, 17) have beat
buttons — the script marks each beat. The narration is about 1,900 words
(~14 minutes at 135 wpm), leaving roughly six minutes for animation beats,
figure reading, and transitions. If you're running long, the marked CUT
lines drop about two minutes without changing the argument.

Register note (2026-07-16 pass): use a technical, non-promotional register.
Define acronyms on first use, avoid appeals to authority or personal
credibility, and let the comparisons and validation results carry the claim.

---

## 1 · Title — 0:00 → 0:45

Thank you — my name is Joseph Bailey. I'm an undergraduate researcher at
Stanford, working with Ben Nachman. This analysis uses the public ME FHC
CC-inclusive data release; nothing shown required access to internal data.

One disclosure: AI-assisted tools were used in coding, systematics
bookkeeping, and documentation. All quoted results were checked through the
validation chain I will show.

The talk in one sentence: we deploy OmniFold, a machine-learning unfolding
method, on the MINERvA open data — first to reproduce the published
measurement, then to extend it to more dimensions than binned unfolding
can reach.

## 2 · Three parts, in order — 0:45 → 1:30

There are three parts.

First, the OmniFold event-reweighting procedure and its relation to binned
unfolding.

Second, reproduction: the existing ME FHC CC-inclusive double-differential
measurement, redone unbinned, quoted in the published bins.

Third, extension: dimensionality beyond two — E-available, q3, and W as new
axes on the same unfolded events — and a look toward a full-phase-space
measurement.

## 3 · Response-matrix scaling (animation) — 1:30 → 2:30

**[Beat 1]** Every binned measurement starts by freezing an observable and a
binning. Here is a toy: six hundred events, one dimension, sixty-four
response-matrix cells — each cell well populated.

**[Beat 2]** Add a second dimension and the cells multiply: four thousand.
Add a third: a quarter of a million cells — for the same six hundred events.
The occupancy per response-matrix cell falls rapidly even though the event
sample size is unchanged.

**[Beat 3]** Remove the grid. The same six hundred events can instead be
represented by their coordinates and paired truth–reco values. The scaling
problem comes from bin occupancy, not from the event count itself.

## 4 · Thirty measurements — 2:30 → 3:15

This survey contains thirty published MINERvA differential cross sections.
They use binned D'Agostini iterative Bayesian unfolding — IBU for short.
Twenty-nine report one or two simultaneous observables; the one
triple-differential measurement, the 2022 QE-like result in muon pT,
p-parallel, and summed proton kinetic energy, shows what a binned 3D
campaign takes.

This work is the red star: five observables unfolded simultaneously — muon
pT and p-parallel, E-available, q3, and W. The arrow above it indicates the
further step: point-cloud inputs replace the fixed list of scalars —
currently the reconstructed recoil system, with a full-event extension in
progress. I will come back to that at the end.

## 5 · Binned OmniFold gives the D'Agostini update (animation) — 3:15 → 4:15

The binned limit gives a direct correspondence with D'Agostini IBU. This
animation shows it.

**[Beat 1]** Each simulated event is one truth–reco pair — one dashed line
per event.

**[Beat 2]** Impose bins, at truth level and at reco level. Every event is
assigned to a bin at both; the pairing itself is untouched.

**[Beat 3]** Histogram the pairing: events on the same
truth-bin-to-reco-bin route merge into a single edge, and the line width
counts the pairs.

**[Beat 4]** The result is the migration matrix — the object D'Agostini IBU
iterates on. A response matrix is a histogram of the pairing, and the
correspondence carries through the full algorithm: with binned inputs, the
OmniFold update is algebraically the IBU update. With unbinned inputs, the
method keeps the pairs, and unfolding becomes the question of how much each
simulated event should count. Assigning weights to events is the problem
machine learning is used for here.

*(CUT if long: press "final" and state the last two sentences over the end
frame.)*

## 6 · The only ML ingredient — 4:15 → 5:15

Here is the single piece of machine learning in the whole method, stated
precisely, because "ML" can mean anything.

Train a classifier to separate data from simulation. p of data given x is
just that classifier's output. A classifier trained between two samples
estimates their density ratio — so the odds ratio, p over one-minus-p, is a
per-event weight. Where data and simulation are indistinguishable, the
weight is one. Where data is richer, above one; where simulation
over-populates, below.

Note what it is *not* doing: it isn't labeling events QE or resonant or DIS.
It answers exactly one question — in this region of feature space, how much
more or less data than simulation? Calibration checks are in backup B3.

## 7 · One iteration: reweight, then pull back (animation) — 5:15 → 7:15

This is the whole algorithm, on toy data.

**[Beat 1]** Step one: at reco level, train the classifier between data and
simulation, and reweight the simulated reco events to match data. The weight
is exactly the w from the previous slide.

**[Beat 2]** Step two: every simulated reco event is paired with its truth
event. Pull the weights back along that pairing. The truth ensemble shifts —
that is the unfolding step, and it used the simulation's own pairing, which
is exactly the information a response matrix contains.

**[Beat 3]** Iterate. The corrections shrink each pass — the same
regularizing structure as choosing the IBU iteration count.

**[Beat 4]** Four iterations in, the weighted truth ensemble lands on the
true spectrum it was never shown. Binning happens only now, at the very
end, into any chosen binning.

## 8 · Implementation checks — 7:15 → 8:15

Three implementation facts are useful here.

First, with binned inputs the OmniFold update is exactly the D'Agostini IBU
update. With unbinned inputs, the simulated truth–reco pairing is retained
event by event.

Second, the nominal learner is a gradient-boosted decision tree. An
independently trained neural network gives a total-cross-section ratio of
1.008 relative to the GBDT result.

Third, backgrounds, fakes, misses, and efficiency are handled with the
standard bookkeeping — the same accounting as in the binned analyses,
carried as event weights. Details in backup.

## 9 · Adding an observable as an input feature — 8:15 → 9:00

The practical consequence. Binned: each new dimension multiplies
response-matrix cells, and the binning is frozen before the unfold.
Unbinned: each observable included in training is one more input column on the
same events. The output is a weighted event sample, so reporting bins and
projections of those recorded features can be chosen afterward. A genuinely
new feature still requires retraining and validation. This contrast is what the
rest of the talk uses.

## 10 · Reproduction — 9:00 → 10:30

Results, part one. The published ME FHC CC-inclusive double-differential
cross section in muon pT and p-parallel — Ruterbories et al., PRD 104. We
unfold unbinned, then bin at the very end into the published fourteen-by-
sixteen binning, and overlay the published points.

Total cross section ratio, OmniFold over published: one-point-zero-one-one.
Median per-bin ratio: one-point-zero-zero-six. Ninety-four percent of
reported bins are within ten percent.

## 11 · Standardized differences and the covariance picture — 10:30 → 11:45

Quantified descriptively using the published per-bin uncertainties as a scale:
mean standardized difference 0.09, RMS 0.60, no structure across the plane.

The indicative distance using the paper's full covariance is 3.66 per bin. It
is driven by correlated shape modes along the low-pT peak ridge,
not normalization. Using the sum of the paper and OmniFold covariances gives
1.48, but the cross-covariance is unavailable because the two results share
data; neither number is a formal compatibility test. The mode-by-mode
breakdown is in backup B6b.

## 12 · Uncertainty budget, rebuilt — 11:45 → 12:45

The uncertainty propagation was implemented independently from the public
release. Flux, detector, and interaction-model universes are propagated
through the unfold, plus a separate ML-training term.

The rebuilt 2D budget lands at a median per-bin uncertainty of 6.87 percent
versus the published 6.86 — with the same band ordering. The ML contribution
is the line riding along the bottom.

## 13 · Validation — 12:45 → 13:45

Six stress tests, each targeting a different failure mode. Closure tests recover
injected truth changes, including a hidden resolution variable and an alternate
model. The existing 2D toys give a mean absolute standardized residual of 0.794,
close to the unit-normal value 0.798. That is a same-ensemble Gaussianity check,
not coverage: the MC bootstrap also fluctuates the stored truth reference, so a
valid independent-truth coverage test is still open.
Doubling the iteration count moves the total cross section by 0.026 percent.
An independent neural network reproduces the GBDT result at the one-percent
level. With binned inputs the update reduces to IBU — verified numerically.
And a descriptive bottom-line test moves from AUC 0.535 before unfolding to
0.501 afterward. It is not cross-fitted through the full OmniFold chain, so I
do not attach a calibrated p-value or claim statistical equivalence.

*(CUT if long: name only closure, the pull diagnostic, and the descriptive
classifier test.)*

## 14 · Marginalization check (animation) — 13:45 → 14:30

Results, part two: new dimensions. First, define the lower-dimensional
check.

**[Beat]** A higher-dimensional unfold, viewed in three axes. Integrating
out E-available is just summing the same weighted events — no re-unfold. The
resulting marginal can be compared directly with the 2D result just shown.

## 15 · The 5D unfold reproduces the anchor — 14:30 → 15:15

And it does, on data. Same events, three more columns: a simultaneous
five-dimensional unfold in pT, p-parallel, E-available, q3, and W.
Marginalized back to the published 2D binning, it reproduces the anchor —
pulls again sub-unit, no structure. The added dimensions do not require an
explicit response-tensor subdivision: they enter the trained estimator as input
columns, with the corresponding support and uncertainty checks.

## 16 · Known low-recoil structure in the E-available marginal — 15:15 → 16:30

The unfolded E-available spectrum shows the established low-recoil
structure: the generators underpredict in this region, and adding Valencia
2p2h fills the dip between the QE and Delta peaks. This is not a new physics
claim. Its role here is as a cross-check of the higher-dimensional result.

## 17 · Localizing a discrepancy (animation) — 16:30 → 17:15

There is a residual the 2p2h tune does not explain, and this is where the
added dimensions become useful. **[Beat]** In one dimension, the residual is
broad — its origin cannot be identified. Open W — same weighted events, one
more column — and it resolves into a compact corner of the E-available–W
plane. These are toy shapes to show the logic; the next slide is the real
plane.

## 18 · The excess localizes — 17:15 → 18:15

Here it is in data — and let me be precise about the claim. At shape level,
the residual excess concentrates at high E-available *and* high W — the DIS
corner. High-E-available cells carry about two-thirds of the positive
excess, and most of that sits above W of 1.8 GeV. All four generators we
compared — GENIE with MnvTune, bare GENIE, NuWro, and GiBUU — underpredict
there.

What I am *not* quoting is a significance. The current five-dimensional
covariance is still a candidate until the selection-complete lateral
replacement lands, and this plane has not been requoted against a final
covariance. The claim today is a localization, not a sigma.

## 19 · Outlook: point clouds — 18:15 → 18:50

Two directions, briefly. First: point-cloud inputs. A recoil-only
point-cloud central-value cross-check is complete — a transformer takes the reconstructed
recoil clusters directly, with muon kinematics entering only through
selection and downstream binning. Its historical uncertainty total is
quarantined because nuisance and retraining responses need a joint covariance
and the detector sample was support-limited. A muon-inclusive full-event
extension and its fresh uncertainty budget are in progress. This is the arrow
above the star on slide four; backup B9 shows central values only.

## 20 · Outlook: full phase space — 18:50 → 19:20

Second: removing the muon angle and momentum cuts entirely. The unbinned
method extrapolates into the previously-cut region, with the prior
dependence bounded explicitly by an envelope of priors — pilot in backup
B10. This result is preliminary: roughly six percent of the rate is opened
but acceptance-supported, roughly twenty-eight percent is prior-dominated,
and the final corrected uncertainties are pending.

## 21 · Summary — 19:20 → 19:45

In summary: OmniFold assigns weights to simulated events. With binned
inputs, its update is the D'Agostini IBU update; with unbinned inputs, the
truth–reco pairing remains event-level. It reproduces the published 2D
result with an independently implemented uncertainty budget. Adding
E-available, q3, and W recovers the known low-recoil structure and localizes
a residual excess in the DIS corner.

Two questions for the collaboration, on the bottom of the slide: which
projections would be most useful, and what validation would be required at
publication level?

## 22 · Three technical questions — 19:45 → 20:00 *(can bleed into Q&A)*

Three technical questions remain: FrInel_pi dial practice, the
goodness-of-fit convention for a rank-deficient covariance, and publication
precedent for a full 3D covariance. Answers today or
afterwards would resolve specific open items in the note.

## 23 · Dated analysis-note draft — closing line

Finally: the last slide links an immutable 16 July snapshot of the analysis
note; I will also send the [same corrected PDF by
email](https://raw.githubusercontent.com/josephbaileyy/MINERvA-OmniFold/7e80fff/docs/jul-16-presentation/claude-design-package/analysis-note.pdf).
It distinguishes finalized 2D and central-value results from covariance work
that is still gated. Please send feedback directly to Ben and me; we aim to
wrap up in about a month. Thank you.

---

### Timing checkpoints (glance at the clock)

| After slide | Target |
|---|---|
| 4 (landscape) | 3:15 |
| 9 (columns) | 9:00 |
| 13 (validation) | 13:45 |
| 18 (excess) | 18:15 |
| 23 (close) | 20:00 |

Running >45 s behind at slide 9 → take both CUT lines (5 and 13).
Running >1 min behind at slide 13 → compress 19+20 to one sentence each
("two outlook directions: point-cloud inputs and full phase space — backups
B9 and B10") and let 22 move fully into Q&A.
