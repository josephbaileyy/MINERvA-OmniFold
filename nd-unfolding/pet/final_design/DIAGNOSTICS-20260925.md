# Locating the proton/neutron failure (study stage S0/S1, development evidence)

PET is diagnostic method development; simulation only. **Everything here is development evidence**
on already-exposed events (the predecessor's FINAL pool-F replicates 0–11 and STRESS pool-T replicates
0–1, two replicates per stress case); it may shape what is tested later and is never confirmatory.

## 1. Instruments

- `diagnostics/posthoc_iterations.py` over the predecessor's 81 completed PILOT/FINAL/STRESS runs
  (their per-iteration `pull`/`push` arrays), job 58879830, code `3071883d`→`HEAD` of this branch at the
  time (see git log). For every iteration it measures, against the ORACLE (the exact distortion evaluated
  on the prior's own truth, so prior/pseudodata sampling differences drop out):
  step-1 detector closure (pulled prior reco vs oracle-weighted prior reco, in reco `E_avail`, number of
  stored clusters, stored-cluster energy sum), step-2 projection (truth observables over selected events
  weighted by pull and by push), missed-event extrapolation (push over truth-passing, reco-failing
  events), truncated-cloud species classes and joint `E_avail` × species histograms, weight tails and
  ESS. Two self-checks run on every run: the oracle scored against itself recovers exactly, and the
  analyzer's `E_avail` recovery against the pseudodata truth reproduces the predecessor's committed
  `scores.json` to 1e-9 (all 81 runs pass). A first pass (job 58879616) omitted the MC truth weight at
  truth level; it is superseded and unused.
- Per-row simulation features (`row_features.npz` sha256 `6b1168c8…`): species counts over the stored
  12-token truth cloud (**truncated-cloud counts**), stored reco cluster count and energy sum.
- Summaries: `diagnostics/summarize_posthoc.py`; the per-run JSON are preserved with the study's run
  outputs.

## 2. Near-zero injections make the `E_avail` recovery ratio unstable

The multiplicity distortions barely move the scored `E_avail` marginal:

| case | injected L1 on the seven `E_avail` bins | same, development tilt |
|---|---:|---:|
| D4c protons ×1.3 | 0.026 | 0.273 |
| D4d neutrons ×1.3 | 0.011 | 0.273 |

Under D4d every estimator except B returns essentially the prior (residual L1 ≈ injected L1 ≈ 0.011);
C@10's "moves away" there (R = −0.086) is an `E_avail` shift of order 0.001 L1, inside the finite-sample
floor (≈ 0.004). B's D4d failure is real: residual 0.024 = 2.2 × the injection, the top `E_avail` bin
pushed up by +0.011 against an injected −0.005. Under D4c, C@10's residual (0.031) is smaller in absolute
terms than its residual under the development tilt (0.059); what fails is the direction of a small shift,
and — below — the absence of the topology correction itself. This is why the study's decision table scores
multiplicity changes on the species distributions they change (E4) and uses absolute tolerances for
near-zero `E_avail` injections (B2).

## 3. The detector step does not transmit the multiplicity change

Recoveries against the oracle, mean of the two replicates (`stress-*-T{0,1}-D4c_p_up`):

| quantity | CTL k=1 / 3 / 10 | B k=1 / 3 / 10 | C k=1 / 3 / 10 |
|---|---|---|---|
| step 1: stored-cluster count | +0.57 / +0.72 / +0.78 | +0.65 / +0.75 / +0.83 | +0.57 / +0.74 / +0.81 |
| step 1: stored-cluster energy sum (deciles) | −0.16 / −0.37 / −0.39 | +0.81 / +0.82 / +0.83 | −0.16 / −0.45 / −0.44 |
| step 1: reco `E_avail` | +0.52 / +0.16 / −0.15 | +0.26 / +0.51 / +0.44 | +0.52 / −0.11 / −0.49 |
| pull over selected: proton class | +0.01 / +0.02 / +0.05 | +0.11 / +0.22 / +0.49 | +0.01 / +0.03 / +0.08 |
| push over selected: proton class | +0.01 / +0.02 / +0.04 | +0.06 / +0.18 / +0.46 | +0.01 / +0.03 / +0.08 |
| push over missed: proton class | +0.00 / +0.01 / +0.03 | +0.03 / +0.10 / +0.23 | +0.01 / +0.03 / +0.07 |
| push, all: joint `E_avail` × proton class | +0.00 / +0.01 / +0.03 | +0.04 / +0.13 / +0.32 | +0.01 / +0.02 / +0.06 |

(Injected L1: stored-cluster count 0.036, energy-sum deciles 0.062, reco `E_avail` 0.023, proton class
0.36, joint 0.36.) The final truth weights stay nearly flat: ESS/n 0.99–1.00 and 99.9th percentile ≈ 1.1–1.3
for CTL and C at every k, and `push/oracle` by proton class ≈ (1.55, 1.21, 0.95, 0.55) for 0/1/2/3+ protons —
the push is close to 1 while the exact weight spans about 0.6–1.8. B reaches ESS/n 0.94 and moves the
3+-proton class to 0.75 of its oracle weight by k = 10.

**Where the first deterioration occurs (D4c).** At the detector step: from iteration 1 the baseline step-1
classifier gets the stored-cluster energy sum wrong (residual 0.072 > injection 0.062), and its reco `E_avail`
closure then worsens monotonically from iteration 2 (residual 0.011 → 0.026 CTL, → 0.034 C by k = 10). For C
this is accompanied by a growing missed-event residual in `E_avail` (0.015 → 0.032). Step 2 projects what it
receives faithfully (push over selected ≈ pull over selected for C). The locus is therefore **the detector-level
ratio**, not an extrapolation of a correctly learned truth ratio; missed-event extrapolation and iteration
compound it. B, whose step 1 receives whole-event reco summaries, closes the cluster-energy distribution
(0.81) and transmits part of the proton topology (0.49 by k = 10 over selected events) — and that same
channel is what moves `E_avail` the wrong way under D4d.

**D4d (neutrons, identifiability 5.4 × null).** Step 1 moves reco `E_avail` the wrong way from iteration 1
for every estimator (pull over selected `E_avail` R ≈ −0.56 for CTL/C, −0.80 for B). CTL's and C's step 2
return ≈ 1 at k ≤ 3; B transmits the reco-energy change and its truth step attributes it to `E_avail`
(push `E_avail` R −1.16 at k = 10). This is the hidden-variable pattern: extra reco energy from neutrons is,
under the prior's reco–truth correlation, explained by higher `E_avail`.

## 4. Why the detector step cannot see it: the reco cloud is capped

On a pool-F replicate (250,687 selected events): the stored reco cloud holds its maximum 12 clusters in
**85.5 %** of selected events (26.9 % below 0.2 GeV reco `E_avail`, 89.3 % in 0.2–0.8 GeV, **100 %** above
0.8 GeV); the stored clusters' energy sum is a median 0.38 of the event's reco `E_avail` (10th–90th percentile
0.18–0.70; this ratio mixes calorimetric calibration with truncation and does not by itself measure the dropped
energy). The truth cloud is capped in only 2.8 % of events. The detector step's particle cloud is truncated for
most events, so whole-event detector summaries (pre-cap reco `E_avail`, reco `q3`, stored-cluster count/energy)
carry information the tokens do not.

## 5. Bounded interventions

(appended when complete: `diagnostics/step2_fixed_target.py`, 19 fits listed in
`runs/step2_interventions.txt` — truth-level learnability of the exact multiplicity weights with raw PDG,
one-hot PDG, one-hot plus truncated-cloud counts, one-hot plus true `E_avail`/`q3`; efficiency-corrected vs
carry; 8 vs 24 epochs; and step 2 given the real iteration-1 pull of the predecessor's C and B runs.)

## 6. What this does and does not establish

It locates, on two replicates per case, the first deterioration under the proton change in the detector
step, and shows that the multiplicity change is essentially not transmitted by the baseline representation.
It does not prove a mechanism: the capped cloud and the classifier's training budget are both candidate
causes, separated by the representation (H1 vs H2), capacity (L64/L128, PET2) and optimization-effort
experiments of stage S1/S2. Truth-level learnability (section 5) tests whether the truth step could represent
the correction if it were transmitted.
