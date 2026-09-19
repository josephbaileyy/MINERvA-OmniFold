# The comparison is running. What it will produce, and how to read it.

**CITABLE FOR:** what was launched, under which frozen design, and what each
stage will emit.
**NOT CITABLE FOR:** any result. **At the time of writing no arm has been
trained and no recovery measured.** This document exists so that whoever reads
the output does not have to reconstruct the design from commit messages.

Supersedes `HANDOFF-20260920-complete-comparison.md`, whose §1 was retracted —
it declared an external blocker that did not exist.

---

## 1. What is running

| job | stage | tasks | depends on |
|---|---|---:|---|
| 58591372 | input build | 24 | — |
| 58592752 | join + launch | 1 | `afterany:58591372` |
| *(submitted by 58592752)* | tuning | 8 | join |
| | pilot | 8 | `afterok:` tuning |
| | final | 16 | `afterok:` pilot |

One task is one (arm, seed). A **pair** is two adjacent tasks sharing a seed.
Stage dependencies are enforced by Slurm, not convention: tuning selects the
learning rate on the tuning split and the pilot sizes the final, so overlapping
them would leak the selection into the comparison.

**Cost**: 17.21 GPU-h per pair, ≈366 GPU-h for 17 pairs with 25 % retries,
against a 1,000-hour ceiling with ≈384 cumulative. Elapsed time is ~15 h for
tuning and days for the whole chain.

## 2. What the comparison is, exactly

**The arms differ at step 1 only.** Step 2 is the production PET on the
production truth cloud for both arms. His vocabulary — blobs, prongs, photons,
dE/dx, positions, times — has no truth analogue, so "his configuration at step
2" is not something his paper determines. The consequence belongs in any
conclusion drawn: **this measures the reco-side representation and
architecture, and cannot speak to his configuration on the truth side.**

**The endpoint is a powered closure.** The measured leg is MC reco reweighted by
the ratified injection (truth `E_avail`, amplitude 0.35, clip 3.0, normalised to
preserve the rate). Real data is never unfolded.

**Recovery** is the fraction of injected L1 displacement recovered, 0 for an
estimator that does nothing and 1 for one that reaches the target, with
overshoot reported rather than clipped.

## 3. Three declared differences from his configuration

Any result carries these; they are in `build_theirs_inputs.DECLARED_DIFFERENCES`
with tests.

| difference | status |
|---|---|
| **muon presence** — his `get_muons` selects on the MINOS match; the slim carries no such flag, so `muon_E > 0` is used | the two agree only if positive energy implies a match. **Not established** |
| **prong dE/dx** — his key list names `prong_part_dEdXMean`, absent from our tuples; `prong_dEdXMean` substituted | **Not shown** to be the same quantity |
| **the cap split** — his is governed by `max_blobs`/`max_prongs`, values not in his repository; ours splits the budget in proportion to the event's multiplicities | **ours, not his** |

## 4. How to read the output

Each task writes `receipt.json` and `weights_*.npz` under
`campaign-20260920/<stage>/<arm>-seed<N>/`. **No task scores.** Scoring is a
separate pass over the frozen endpoint, deliberately, so that a run cannot be
re-scored until it reads well.

When all of `final` has landed:

1. score each arm-seed against the seven-bin `E_avail` endpoint;
2. compute the paired differences and the t interval, `n−1` df, **excluding the
   pilot observations** — the pilot chose `n`, and reusing it would make the
   interval conditional on its own width;
3. apply `selection_rule.decide` with the ratified thresholds (`f = 0.80`,
   `δ = 0.02`, `δ_switch = 0.04`, regional `0.60 ×` each region's own
   reference) and the regional safeguard on the (pT, p‖) cells;
4. report the low-acceptance band separately — 31.0 % of truth mass, 26.6 % of
   displacement — with each arm's recovery there beside its aggregate. Those
   events are **retained**, and the band is `low_acceptance`, not
   "unresolvable".

**Non-inferiority is not superiority.** If his arm scores better and ours is
retained under the switching policy, the report says exactly that.

## 5. One open question that does not block the campaign

The XLA-GPU path is **not batch-invariant at the 1e-3 level** with TF32
demonstrably disabled: the same compiled program differs from itself between
batch 2048 and 256, on the same rows, by a median 2.37e-3, while the same
comparison on CPU gives exactly 0.0. Two hypotheses were tested and rejected —
k-NN ties (the row profile shows 100 % of rows moving, not a few) and TF32
(`NVIDIA_TF32_OVERRIDE=0` changed the deviation by nothing, to the digit).

It bears on trusting the executed path. The next experiment is isolating it to
an operation; the transcendental approximations in `_gelu`'s `erf` and
`DynamicTanh`'s `tanh` are the candidates.

## 6. Scope

PET remains diagnostic method development. Nothing here is a publication
adoption, a covariance, a systematic, a central-value change or a Gate-6 action;
nothing discharges `OI-71`; nothing has been sent to Ben, to Gregor or to anyone.
