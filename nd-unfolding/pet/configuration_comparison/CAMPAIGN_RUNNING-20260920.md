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

Launched 2026-09-20 at commit `994e4da2`, after both arms completed a closure
end to end (job 58605416: ours 147.8 s, his 160.5 s).

| job | stage | tasks | depends on |
|---|---|---:|---|
| 58605669 | gather his tokens, one per stage | 1 | — |
| 58605670 | tuning | 8 | `afterok` gather |
| 58605671 | pilot | 8 | `afterok` tuning |
| 58605672 | final | 16 | `afterok` pilot |

**Cost, re-derived**: 58.5 GPU-hours, 73.1 with the retry allowance, against a
1,000-hour ceiling. The earlier 366-hour figure was built on the real-data
nominal's row counts and does not describe this campaign; see
`closure_cost.py`.

One task is one (arm, seed). A **pair** is two adjacent tasks sharing a seed.
Stage dependencies are enforced by Slurm, not convention: tuning selects the
learning rate on the tuning split and the pilot sizes the final, so overlapping
them would leak the selection into the comparison.

**Cost**: 17.21 GPU-h per pair, ≈366 GPU-h for 17 pairs with 25 % retries,
against a 1,000-hour ceiling with ≈384 cumulative. Elapsed time is ~15 h for
tuning and days for the whole chain.

## 2a. What the join established, and one asymmetry it exposed

The first chained join **refused to launch**: data 100.00%, signal 59.51%. The
guard was right to stop and the number was measuring the wrong thing.

The MasterAnaDev AnaTuple has two trees. `MasterAnaDev` holds reconstructed
events — 402 rows for (run 110001, subrun 1), exactly what we built — and
`Truth` holds all 1132 generated ones. The signal inventory spans both. An event
that failed reconstruction has **no reconstructed object**, so no token can be
built from it; it enters the comparison through the truth leg. Requiring a built
input for it was a gate on a population that cannot satisfy it.

Measured on the real join:

| | |
|---|---:|
| unmatched **and** `pass_reco` | **0** |
| coverage of `pass_reco` rows | **20,573,521 / 20,573,521 = 100.0000 %** |
| unmatched rows, all `!pass_reco` | 19,899,656 |
| **matched** rows that are `!pass_reco` | **8,679,708** |

`mc_nthEvtInFile` is not a global index — it repeats about 156 times within a
run — so none of this was readable off the field names. It took opening the
original tuple and finding the second tree.

**The last row is the one that mattered.** Those 8.68 M events are in the reco
tree and fail the reco selection. The production loader zeroes its reco block
there, so our arm sees zeros — and his arm was keeping real reco content on
18 % of the signal leg. That is information ours does not have, and it would
have read as a method effect in his favour. Both arms are now zeroed on
`!pass_reco` by one implementation, `theirs_loader_substitution.zero_non_reco`,
called from both the gather and the driver.

The gate still fails closed, now on the right population: a missing `pass_reco`
row is an event his arm cannot see and ours can.

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

## 5. The batch-invariance question, answered: it was TF32

**Resolved 2026-09-20, job 58596282** (`isolate_batch_variance.py`, one
primitive at a time, both batch sizes, same rows).

| `NVIDIA_TF32_OVERRIDE` | what moves | matmul error / RMS |
|---|---|---:|
| `0` | **nothing** — every primitive exactly `0.0` | 1.0e-4 |
| `1` | `matmul`, `matmul_deep_8`, `sdpa` — median 6.4e-3, 100 % of rows | 1.7e-1 |

With TF32 off, matmul, SDPA, layernorm, softmax, the reductions, `erf`, `gelu`
and `tanh` are all **bit-identical** across batch 2048 and 256. With TF32 on,
exactly the three tensor-core operations move, at the scale of the unexplained
2.37e-3. Controls held in both directions: an elementwise add and multiply came
back exactly zero, and the batch-axis reduction moved.

**So the earlier rejection of TF32 was wrong, and wrong for a reason worth
keeping.** It rested on `NVIDIA_TF32_OVERRIDE=0` changing the deviation "by
nothing, to the digit" — but that test compared the path to *itself*, which
cannot distinguish "the override worked and TF32 was never the cause" from "the
override never reached the compiled path". Comparing against a float64 **answer**
separates them in one measurement: the override moves the matmul's error from
1.7e-1 to 1.0e-4 of the result's RMS, against 2.7e-6 predicted for true float32
and 1.1e-2 for TF32.

The campaign is unaffected — `sbatch_campaign.sh:52` already exports
`NVIDIA_TF32_OVERRIDE=0`, so the arms train on the batch-invariant arithmetic.
The frozen precision policy is now enforced by something that binds, and
verified by something that does not depend on the flag being honest.

## 6. Scope

PET remains diagnostic method development. Nothing here is a publication
adoption, a covariance, a systematic, a central-value change or a Gate-6 action;
nothing discharges `OI-71`; nothing has been sent to Ben, to Gregor or to anyone.
