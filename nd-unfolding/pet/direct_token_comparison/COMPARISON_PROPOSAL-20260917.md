# Proposal: one bounded experiment to settle the PET representation choice

**CITABLE FOR:** a predeclared design, its decision rule, and its resource ceiling.
**NOT CITABLE FOR:** any result. Nothing here has been run. No compute was launched to
write it.

**For agreement by Joseph and Ben before execution.** Everything below is either a
measured number with a citation or a choice marked as a judgement for you to accept or
change. Two items need your decision and are marked **[DECIDE]**.

---

## 1. What we now know, and why it changes the question

The finished matrix measured pooled versus individual-object attention on a four-object
synthetic fixture and returned **no detectable accuracy difference**: median paired gain
+9.707%, mean +0.817%, sd **25.774** percentage points over 8 seeds, 95% interval
[-20.730%, +22.365%], paired *p* = 0.50. Cost was clean: **1.118x** training, **1.283x**
inference.

Two facts found while preparing this proposal explain that null and reframe the choice.

**(a) The treatment was one token in sixteen.** The model attends over 1 event token +
12 generic tokens + the typed tokens (`typed_token_comparison.py:178-185`). Pooled gives
3 family tokens, individual gives 4 objects, so the arms are **T = 16 versus T = 17**.
The 12 generic tokens and the event token are drawn from `rng.normal` and carry no
signal; the entire learnable target is the two prong `time` values
(`run_typed_token_comparison.py:70-107`). Pooling is `unsorted_segment_sum` over a
per-object MLP embedding (`typed_token_comparison.py:144-149`) — a deep-sets sum over
**two tokens that carry distinct `raw_pid` features**, which is close to sufficient for
this target. We powered an experiment to detect a one-token perturbation whose
information loss is near zero. The null is the expected result, not a surprise.

**(b) We already truncate, on the leg where it binds.** The production PET estimator's
clouds are "energy-ranked and truncated or zero-padded to 12 tokens"
(`docs/analysis-note/sec_pet.tex:56-57` at `66d35706`; the 12-token cardinality is
carried in code at `nd-unfolding/pet/typed_descriptor_source_smoke.py:34` and
`nd-unfolding/pet/validate_g2_npz_receipt.py:113`). The truth leg is comfortable — mean
cardinality **4.57**, **2.31%** of events at the cap, the twelfth constituent carrying
**0.09%** of retained truth energy (`sec_pet.tex:104-116`). The **reco leg is at the
cap**: mean **11.09** clusters in data, **11.15** in MC, against a cap of 12, with the
distributions "pil[ing] up at the cap" (`sec_pet.tex:156-165`). The note's
"essentially lossless" validation is for the truth cloud at $E_{\rm avail}$ scale.

So the four-object fixture was roughly representative of the **truth** leg (4 versus a
mean of 4.43-4.57) and omitted the **reco** leg entirely. This corrects my earlier
report sentence that "our implementation applies no cap at all"; that holds for the
comparison code, not for production.

The correction has been applied in `REPORT_FOR_BEN.md` and scoped in
`MATCHED_COMPARISON_LADDER-20260916.md`. One further site cannot be repaired in place:
`CROSSDEVICE_DIAGNOSTIC_SPECIFICATION-20260915.md:175` says "Our uncapped
representation" and is **hash-bound in `amended-manifest.json`**, so editing it would
break every launcher's verification. Read that sentence as scoped to the comparison
code; this paragraph is its correction of record.

## 2. What the fixture omitted, stated as testable gaps

| gap | fixture | reality |
|---|---|---|
| G1 multiplicity | exactly 1 photon / 1 blob / 2 prongs, every event | reco clouds mean 11.1, piling up against a cap of 12 |
| G2 cap pressure | no cap can bind, so truncation and aggregation are indistinguishable | truncation is live on the reco leg |
| G3 variable length | one fixed geometry; no padding, no mask, no variable width | multiplicity is a distribution from 1 to $\geq$ 25 |
| G4 compression ratio | pooling compresses 2 objects to 1 token | pooling would compress ~11 to 1 |

G4 is the one that matters for sensitivity. Pooled-versus-individual is a near-no-op at
2 objects and a genuine representational difference at 11.

## 3. The experiment

**One fixture, three arms, three regimes, one primary endpoint.**

The fixture is the existing producer with **one change**: the blob family draws a
multiplicity from a distribution matched to the reco-cluster cardinality (mean ~11,
tail past 12), instead of exactly one blob. Photons, prongs, the event token, the 12
generic tokens, normalization, the OmniFold chain and the seed discipline stay
byte-identical, so the new experiment differs from the finished one in exactly one
respect.

| arm | representation |
|---|---|
| **A pooled** | incumbent: sum within each family, 3 typed tokens (T = 16, constant) |
| **B individual** | every object its own token, no cap (T ~ 27 at mean multiplicity) |
| **C aggregate** | cap at 12 per family: keep the 11 highest-energy, append one token whose four-momentum is the summed tail and whose auxiliary block is the tail mean, with a distinct type code and — unlike upstream — an explicit merged count |

Arms A and C are the two production candidates; B is the information-retention ceiling
that says how much either one gives up. Upstream's `truncate` mode is **not** an arm: it
is already characterised (`OVERFLOW_SPECIFICATION-20260915.md` §2.2) and nobody proposes
adopting it — but C is measured against B, which bounds it.

Three signal-placement regimes, reused unchanged from that specification so they are not
re-implemented:

| regime | target depends on | prediction |
|---|---|---|
| **R1** tail-extensive | the **sum** of the payload over the low-energy tail | A ties B (a sum is sufficient); C recovers; separates C from truncation |
| **R2** tail-resolved | a **non-additive** function of the tail (dispersion or extremum) | B > A and B > C; this is the discriminating regime |
| **R3** head-only | only the top-*k* objects, *k* < 11 | **all three arms tie** |

R3 is load-bearing and non-negotiable: without it, "B wins" cannot be distinguished from
a fixture rigged to punish any compression. R1 doubles as a second negative control — if
A does *not* tie B under a purely extensive target, the fixture is wrong, because sum
pooling is provably sufficient there.

**Primary endpoint: R2 only.** R1 and R3 are controls and are reported descriptively. One
primary stratum, declared now, so there is no multiplicity-of-testing to argue about.

## 4. What "better" means

**Primary:** the paired per-seed **difference in final-iteration log-ratio RMSE** in
absolute units, arm minus incumbent, on the held-out split, at the last OmniFold
iteration — the same quantity `summarize_runs.py` already computes, with the ratio's
noisy denominator removed. The relative percentage is reported as a secondary,
interpretable figure.

**Margin.** An arm is better only if it beats the incumbent by more than a predeclared
margin $\delta$, because a gain smaller than the cost premium would not change the
production choice. **[DECIDE] I propose $\delta$ = 10% relative** (double the old 5%
threshold), justified by the measured cost premium of 12% training / 28% inference: a
sub-10% closure gain is not worth a 28% inference bill on a method-development
estimator. Lower $\delta$ if you disagree — §5 prices it.

**Safeguards unchanged.** Every existing check — normalization, ESS, tail-ESS, both truth
projections, cap diagnostics, absolute recovery $\leq$ 0.10, and the null-control mode —
carries over as-is. A safeguard failure invalidates its stratum and is never converted
into a verdict about a representation.

## 5. Statistical sensitivity, and why this is two stages

With the measured sd of **25.774** points, at 80% power and $\alpha$ = 0.05 two-sided:

| $\delta$ | n at sd 25.8 | at sd 18.0 | at sd 12.9 |
|---:|---:|---:|---:|
| 5% | 209 | 103 | 53 |
| 10% | **53** | 26 | **14** |
| 15% | 24 | 12 | 6 |

Two levers, in order of cost-effectiveness:

1. **Effect size (free).** R2 is designed so the representations differ materially. The
   old fixture's treatment was near-null by construction; this one is not.
2. **Variance reduction (cheap, and measurable before committing).** The 25.8 includes at
   least three components we have never separated: training stochasticity, fixture-draw
   noise, and the closure estimator's own finite-sample noise. The last two are fixable
   without more seeds — more test rows and more evaluation replicates cost seconds, not
   GPU-hours, whereas each seed costs a full paired job.

Hence **Stage 1**, a pilot that buys the number we need before we spend on n:

* 3 seeds x {R2, R3} x 3 arms.
* Decompose the per-seed variance: re-evaluate each trained model on independent test
  splits (no retraining), bootstrap the test set within each run, and repeat one seed
  with a different training seed on identical data.
* Measure the per-job cost at the new token count, and the R2 effect size.
* Confirm the R1/R3 ties and the cap-binding fraction.

**Stage 1 declares no winner.** Its outputs are sd, cost-per-job, and effect size.

**Gate, predeclared:** Stage 2 runs at the n that the *measured* sd and the agreed
$\delta$ require, **only if** that n fits the ceiling in §7, R3 ties, and R1 shows A
tying B. Otherwise we do not run Stage 2 and we report the question as unresolvable at
this budget. n is fixed by Stage 1 and **not** revised after Stage 2 results are seen.

## 6. A fair budget for both methods

Equal epochs is not the same as equal fairness, and the two answers can differ.

* **Matched optimisation:** identical epochs, iterations, batch size, initialization
  seeds and data order, as now. B and C get more tokens and therefore more compute at
  equal epochs — an advantage the incumbent does not get.
* **Equal tuning:** the same small predeclared grid, **6 trials per arm**, selected on a
  validation split **disjoint from the closure test set** and on validation loss, never
  on closure. No arm gets hand-tuning the others did not.
* **Iso-cost sensitivity, conditional:** if an arm wins the primary endpoint by between
  $\delta$ and 2$\delta$, re-run it at equal *wall-clock* rather than equal epochs. Only
  in that band can cost flip the decision, so we pay for this only when it can matter.

## 7. Resource cost and ceilings

Measured basis: the finished matrix ran **1990.75 s of wall per paired job** = **0.553
GPU-hours** (both arms, 1M train rows, 250k test, 5 epochs, 3 iterations, T = 16/17).
Attention cost grows with token count; at T ~ 27 for arm B, per-job cost should rise by
roughly 2x, and three arms instead of two adds ~1.5x.

| stage | jobs | estimate | **hard ceiling** |
|---|---:|---:|---:|
| Stage 1 pilot | 6 + free re-evaluations | ~12 GPU-h | **15 GPU-h** |
| Stage 2 (n = 14, R2 + R3) | 28 | ~56 GPU-h | **75 GPU-h** |
| reduction, closeout | CPU only | < 20 core-h | 100 core-h |
| storage | models + receipts | ~40 GiB | **100 GiB** |

**Total ceiling: 90 GPU-hours.** Headroom, measured today: the project has 60,049 of
180,000 GPU node-hours left (`iris project m3246`, 119,950.8 charged) and 3,490 of 20,000
CPU node-hours; pscratch is at **80.1%** (16.02 / 20.00 TiB), so the 100 GiB storage cap
matters and Stage 2 inputs must be built in-job rather than stored. The campaign's own
290 GPU-hour ceiling is untouched: all m3246_g GPU work since 2026-09-01 totals **14.8
device-hours over 35 jobs**, an upper bound on this campaign's usage. Note that the
"~229 GPU-hours remaining" line in `INFERENCE_BENCHMARK_SPECIFICATION-20260917.md` does
not reconcile with that measurement and should not be quoted; reconciling the campaign
ledger is a prerequisite below, not a blocker on agreeing this design.

If Stage 2 as sized does not fit, the response is to **drop R1, then reduce to one
regime pair**, never to weaken a criterion, drop R3, or cut seeds below the powered n.

## 8. Decision rule, including the inconclusive branch

Applied once, to the R2 primary endpoint, after Stage 2 completes:

1. **Adopt B or C** if its paired mean beats the incumbent, the 95% interval's lower
   bound exceeds $\delta$, the sign is consistent in at least 70% of seeds, every
   safeguard holds, R3 ties, and the conditional iso-cost check (if triggered) agrees in
   sign. Adoption means the production representation, not a publication claim.
2. **Keep A, declared equivalent** if the 95% interval lies entirely inside $\pm\delta$.
   This is a positive result the finished matrix could not produce, and the reason to
   power the study: it closes the question at a stated resolution, and pooling then wins
   on cost.
3. **Inconclusive, and closed at the achieved resolution** if the interval is wider than
   $\pm\delta$ — neither rejection nor equivalence. We report the resolution we achieved
   and default to the incumbent. We do **not** add seeds after seeing the result.
4. **Invalid** if R3 does not tie or R1 does not show A tying B. Then no R2 conclusion is
   reported at all, in any direction.

Cost never enters criteria 1-4. It is reported alongside, and only breaks a tie inside
the equivalence band.

## 9. Prerequisites

1. **The variable-length cross-device GPU gate. This is the blocker.** Varying
   multiplicity means padding and masking — exactly the geometry your 2026-09-16 decision
   exempted as a recorded stress failure, with the explicit condition that the exemption
   "does not extend to future variable-length or real-source training"
   (`STRESS_SCOPE_AUTHORIZATION-20260916.md`). Stage 1 cannot start until that gate either
   passes at the new geometry or is re-scoped by you on the evidence. Expect this to be
   the largest piece of preparatory work; the diagnostic in
   `CROSSDEVICE_D1_RESULT-20260915.md` measured the discrepancy but did not fix it.
2. **The reco-cluster multiplicity distribution.** The two means (11.09 / 11.15) are
   published in the note's caption, but the fixture needs the *shape*, including the
   pre-truncation tail. The stored P12 inputs are already truncated to 12, so the
   pre-truncation distribution requires the variable-length ROOT branch — a **counts-only**
   read, no kinematics. **[DECIDE]** authorise that counts-only read, or we use a
   predeclared synthetic multiplicity ladder (means 4, 11, 24) and make no
   representativeness claim. I recommend the counts-only read: it is cheap, and it is the
   only thing that makes "representative" a measured word rather than an assertion.
3. **Upstream semantics** are already bound and measured; no new dependency
   (`OVERFLOW_SPECIFICATION-20260915.md` §2, digests recorded).
4. **Campaign ledger reconciliation** for the 290 GPU-hour ceiling, per §7.
5. The frozen matrix stays frozen. No receipt, criterion or artifact of the finished
   comparison is modified, re-reduced or re-interpreted by any of this.

## 10. Separation from publication-critical work, and the one real dependency

This is diagnostic method development. Nothing proposed here is a publication
uncertainty product, no result of it enters a covariance, a systematic, or Gate-6, and
the synthetic findings stay distinct from real-data adoption.

There is, however, **one concrete dependency**, and it runs in the opposite direction
from the experiment:

* The note asserts that keeping the 12 highest-energy hadrons is "essentially lossless
  for $E_{\rm avail}$-scale observables", validated over 32.8M truth events
  (`sec_pet.tex:336-353`). That claim is about the **truth** cloud. The **reco** cloud
  sits at the cap and I found no equivalent validation cited for it. This is a
  note-side question that exists whether or not the experiment runs, and it should be
  checked by someone reading `POINTCLOUD_PROJECTION.md`, not inferred from a synthetic
  result.
* The note describes Gregor's representation as one where "prongs or blobs above their
  separate caps are combined into aggregate overflow tokens" (`sec_pet.tex:396-399`, at
  his pinned commit `af5d92ed`). Our measurement of that code found aggregation is
  **opt-in** and energy-ordered **truncation** is the default. That is a factual
  precision issue in an existing note sentence, independent of this proposal.

Neither of those is resolved by this experiment, and this experiment must not be cited
as resolving them. They are flagged because you asked me to identify concrete
dependencies, and these two are the only ones I found.

## 11. What this experiment still cannot establish

It compares three representations on a synthetic fixture whose multiplicity is matched
to the reco cloud. It does **not** compare our complete pipeline against Gregor's — that
is rung R6 of `MATCHED_COMPARISON_LADDER-20260916.md` and needs his architecture inside
our closure harness. It says nothing about real-data closure, and a Stage 2 adoption
verdict is a verdict about the production *representation*, still inside method
development.
