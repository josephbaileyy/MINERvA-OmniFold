# July 16 talk — 20-minute script

Main deck = slides 1–23 (backup B1–B10 behind the divider). Times are
cumulative targets; the deck's animated slides (3, 5, 7, 14, 17) have beat
buttons — the script marks each beat. Total spoken text ≈ 2,700 words
(~135 wpm → 20:00). If you're running long, the marked CUT lines drop
~2 minutes without touching the argument.

Register note (2026-07-16 pass): no "you/your" framing directed at the
audience, no slogans. State facts; let the numbers carry the emphasis.

---

## 1 · Title — 0:00 → 0:45

Thank you — my name is Joseph Bailey. I'm an undergraduate researcher at
Stanford, working with Ben Nachman. I should say up front that I am not a
MINERvA collaborator: everything in this talk is built on the public ME FHC
CC-inclusive data release, and nothing required access beyond what is
already published.

One note on the subtitle, stated explicitly: we used AI agents to help with
essentially every part of this analysis — code, systematics bookkeeping,
documentation. We have verified, and take full responsibility for, all of
the content.

The talk in one sentence: we deploy OmniFold, a machine-learning unfolding
method, on the MINERvA open data — first to reproduce the published
measurement, then to extend it to more dimensions than binned unfolding
can reach.

## 2 · Three parts, in order — 0:45 → 1:30

Three parts, in this order — the order matters, because each part is the
justification for the next.

First, a brief introduction to OmniFold. It is not exotic — it has been
deployed at ATLAS, CMS, LHCb, STAR, H1, ALEPH, and T2K.

Second, reproduction: the existing ME FHC CC-inclusive double-differential
measurement, redone unbinned, quoted in the published bins.

Third, extension: dimensionality beyond two — E-available, q3, and W as new
axes on the same unfolded events — and a look toward a full-phase-space
measurement.

## 3 · The dimensionality wall (animation) — 1:30 → 2:30

**[Beat 1]** Every binned measurement starts by freezing an observable and a
binning. Here is a toy: six hundred events, one dimension, sixty-four
response-matrix cells — each cell well populated.

**[Beat 2]** Add a second dimension and the cells multiply: four thousand.
Add a third: a quarter of a million cells — for the same six hundred events.
The response matrix runs out of statistics long before the event sample
does.

**[Beat 3]** Now remove the grid. The same six hundred events, treated as
events, are densely populated in three dimensions. The limit is bin
occupancy, not event count.

## 4 · Thirty measurements — 2:30 → 3:15

This limit is visible in the publication record. Here is every published
MINERvA differential cross section — thirty of them. Every one uses binned
D'Agostini iterative Bayesian unfolding, and every one is focused on one or
two simultaneous observables. That plateau is the wall from the last slide.

This work is the red star: five observables unfolded simultaneously — muon
pT and p-parallel, E-available, q3, and W. The arrow above it indicates the
further step: point-cloud inputs replace the fixed list of scalars —
currently the reconstructed recoil system, with a full-event extension in
progress. I will come back to that at the end.

## 5 · Binned, OmniFold reduces to IBU (animation) — 3:15 → 4:15

The way I find it clearest to conceptualize OmniFold is through its binned
limit: bin the inputs, and it reduces to D'Agostini IBU. This animation
shows the correspondence.

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

## 8 · Why this is not a black box — 7:15 → 8:15

Three points on why this is not a black box.

First — this is the previous slide's statement made precise — feed OmniFold
binned inputs and it reduces exactly to D'Agostini IBU. It is a strict
generalization of the method MINERvA already uses, with the histogram
removed.

Second, the learner is gradient-boosted decision trees. Deliberately simple,
robust, cheap to retrain — and cross-checked against an independent neural
network, which agrees at the one-percent level.

Third, backgrounds, fakes, misses, and efficiency are handled with the
standard bookkeeping — the same accounting as in the binned analyses,
carried as event weights. Details in backup.

## 9 · Adding an observable is adding a column — 8:15 → 9:00

The practical consequence. Binned: each new dimension multiplies
response-matrix cells, and the binning is frozen before the unfold.
Unbinned: each new observable is one more input column on the same events.
The unfolded result is a weighted event sample, so bins — and even
observables — are chosen *after* unfolding. This contrast is what the rest
of the talk uses.

## 10 · Reproduction — 9:00 → 10:30

Results, part one. The published ME FHC CC-inclusive double-differential
cross section in muon pT and p-parallel — Ruterbories et al., PRD 104. We
unfold unbinned, then bin at the very end into the published fourteen-by-
sixteen binning, and overlay the published points.

Total cross section ratio, OmniFold over published: one-point-zero-one-one.
Median per-bin ratio: one-point-zero-zero-six. Ninety-four percent of
reported bins within ten percent. Same data, same answer, through an
independent chain.

## 11 · Pulls and the full-covariance picture — 10:30 → 11:45

Quantified: per-bin pulls against the published uncertainties — mean 0.09,
RMS 0.60, no structure across the plane.

Let me also state the full-covariance number before anyone asks. Against the
paper's full covariance alone, chi-squared per degree of freedom is 3.66 —
driven by correlated shape modes along the low-pT peak ridge, not
normalization; including our own covariance brings it to 1.48. The anatomy
of that number is in backup, and I'm happy to go through it in questions.

## 12 · Uncertainty budget, rebuilt — 11:45 → 12:45

Agreement in the central value is only half the reproduction. We did not
reuse the collaboration's error propagation — we rebuilt it. Flux, detector,
and interaction-model universes from the data release, propagated through
the unfold from scratch, plus an ML term that has no counterpart in a
binned analysis.

The rebuilt 2D budget lands at a median per-bin uncertainty of 6.87 percent
versus the published 6.86 — with the same band ordering. The ML contribution
is the line riding along the bottom.

## 13 · Validation — 12:45 → 13:45

Six stress tests, each with a number. Closure tests recover injected truth
changes, including a hidden resolution variable and an alternate model. Toy
coverage comes out at 68.7 percent against the Gaussian 68.27 target.
Doubling the iteration count moves the total cross section by 0.026 percent.
An independent neural network reproduces the GBDT result at the one-percent
level. With binned inputs the update reduces to IBU — verified numerically.
And a bottom-line test: a freshly trained classifier can no longer separate
the unfolded result from the target — AUC 0.501.

*(CUT if long: name only closure, coverage, and the bottom-line test.)*

## 14 · Marginalization (animation) — 13:45 → 14:30

Results, part two: new dimensions. First, the check that makes new
dimensions testable.

**[Beat]** A higher-dimensional unfold, viewed in three axes. Integrating
out E-available is just summing the same weighted events — no re-unfold. So
the marginal of the larger measurement must reproduce the 2D anchor just
validated. Every added dimension carries this built-in cross-check.

## 15 · The 5D unfold reproduces the anchor — 14:30 → 15:15

And it does, on data. Same events, three more columns: a simultaneous
five-dimensional unfold in pT, p-parallel, E-available, q3, and W.
Marginalized back to the published 2D binning, it reproduces the anchor —
pulls again sub-unit, no structure. The added dimensions do not subdivide
the event sample: they add input columns, not response-matrix cells.

## 16 · Re-finding the known low-recoil physics — 15:15 → 16:30

Now the physics content. The unfolded E-available spectrum, against
generators. Nothing on this slide is a new claim — deliberately: all
generators underpredict at low recoil, and adding Valencia 2p2h fills the
dip between the QE and Delta peaks. This is MINERvA's established low-recoil
result, recovered from the public data by a different unfolding method.
Recovering an established result with an independent method is the relevant
test of the method's credibility.

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

What I am *not* quoting is a significance. The corrected five-dimensional
covariance is in hand, but this plane's significances have not yet been
requoted against it, so the claim today is a localization, not a sigma.

## 19 · Outlook: point clouds — 18:15 → 18:50

Two directions, briefly. First: point-cloud inputs. A recoil-only
point-cloud cross-check is complete — a transformer takes the reconstructed
recoil clusters directly, with muon kinematics entering only through
selection and downstream binning, and it agrees with the scalar pipeline at
comparable precision. A muon-inclusive full-event extension and a dedicated
omitted-variable validation are in progress. This is the arrow above the
star on slide four; uncertainty numbers in backup B9.

## 20 · Outlook: full phase space — 18:50 → 19:20

Second: removing the muon angle and momentum cuts entirely. The unbinned
method extrapolates into the previously-cut region, with the prior
dependence bounded explicitly by an envelope of priors — pilot in backup
B10. This result is preliminary: roughly six percent of the rate is opened
but acceptance-supported, roughly twenty-eight percent is prior-dominated,
and the final corrected uncertainties are pending.

## 21 · Summary — 19:20 → 19:45

In summary: OmniFold assigns weights to simulated events rather than
operating on binned histograms, and it reduces to D'Agostini IBU in the
binned limit. It reproduces the published 2D result with an independently
rebuilt uncertainty budget. The same events then open E-available, q3, and
W — recovering the known low-recoil physics and localizing a residual
excess in the DIS corner.

Two questions for the collaboration, on the bottom of the slide: which
projections would be most useful, and what validation would be required at
publication level?

## 22 · Three technical questions — 19:45 → 20:00 *(can bleed into Q&A)*

Three technical questions where collaboration guidance resolves more than
we can compute on our own — FrInel_pi dial practice, the goodness-of-fit
convention for a rank-deficient covariance, and whether MINERvA would
endorse publishing a full 3D covariance. If anyone can speak to these today
or afterwards, that closes real items in the note.

## 23 · Note v1.0 — closing line

Finally: a frozen v1.0 of the analysis note goes up right after this talk —
link by email. Please send feedback directly to Ben and me; we aim to wrap
up in about a month. Thank you.

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
