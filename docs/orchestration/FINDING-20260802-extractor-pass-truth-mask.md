# FINDING 2026-08-02 — the full-event extractor omits the `pass_truth` mask, and its own guard blocks it

*Found by execution on its first-ever run: NCSA Delta slurm 20778127, synthetic fixture.*
*Status: CONFIRMED, mechanism isolated. Touches a Gate-4-bound file → fix is a receipt re-issue.*
*Severity: BLOCKS the extraction step of P5A. Physics output is unaffected; the gate is not.*

## Claim

`nd-unfolding/pet/extract_fullevent_fps.py :: reweight_full_inventory` evaluates the trained
step-2 model on **every** signal row —

```python
out[lo:hi] = of.reweight((gen_cloud, evt), model2, batch_size=batch_size)
```

— with no `pass_truth` mask. The engine does not do that. `MultiFold.RunStep2`
(`omnifold_nn/omnifold/omnifold.py:203-205`) pins off-acceptance rows to exactly 1:

```python
new_weights = np.ones_like(self.weights_push)
new_weights[self.mc.pass_gen] = self.reweight(...)[self.mc.pass_gen]
self.weights_push = new_weights
```

So the two passes disagree on every `pass_truth == False` row by construction: the training pass
holds 1.0, the full pass holds whatever the classifier returns.

`check_subsample_agreement` then compares the two over their shared rows and fails closed. Its own
docstring calls that cross-check the thing "without which the pass is unfalsifiable" — correct, and
as written it fires on a **correct** result.

## Evidence

First execution of the extractor, on a 60,000-row synthetic `g2-fullevent-v1` fixture
(Delta 20778127, `tf215.sif`, worktree at `0e19f66`):

```
[extract] the full-inventory reweight disagrees with the training pass on the 6000 shared rows:
          max relative deviation 9.655e-01 > 0.001.
```

Mechanism confirmed directly against the two artifacts:

```
fixture rows 60000   pass_truth True 59365   False 635      (1.06%)
subsample     6000   !pass_truth in subsample 71
driver weights_push on !pass_truth rows: unique [1.]        <- the engine's pin
driver weights_push on  pass_truth rows: 1.3379 .. 1.9723   <- classifier range
```

71 rows held at 1.0 against classifier output in 1.34–1.97 gives a max relative deviation of
≈0.97, which is the 9.655e-01 reported. Nothing else is required to explain it.

## What is and is not broken

**The cross section is not affected.** `xsec_from_push` histograms
`(w_truth * push)[pass_truth]` and `completeness_2d` selects on `pass_truth`, so the unmasked
values never enter the result. This is a plumbing defect, not a physics one.

**The gate is affected, and that is the blocker.** The extractor exits non-zero before writing
`w_push`, so the extraction step of P5A cannot complete whenever the training subsample contains a
single `pass_truth == False` row.

**Whether the real dump trips it is NOT established.** The synthetic fixture carries 1.06%
`pass_truth == False`. The G2 signal inventory may be all-`pass_truth` — `mc_truth_denom` equals
`mc_signal_reco` (49,906,108) in `g2-gate1-all12-validation-20260719.json`, which is consistent
with, but does not prove, no off-gate rows. **Do not assume it passes on the real dump**, and note
the failure mode is asymmetric: if there are no such rows the guard is silently vacuous, and if
there are, the extractor refuses to run.

**A third consumer would be misled either way.** `w_push_full.npz` is persisted over
`arange(N)`; on off-gate rows it holds classifier output where every other artifact in the campaign
holds the engine's 1.0. Any future reader that does not re-apply `pass_truth` inherits the
discrepancy silently.

## Fix

One line, in `reweight_full_inventory`: initialize `out = np.ones(n, np.float64)` and assign only
the `pass_truth` rows of each chunk, mirroring `RunStep2`. That makes `w_push` the engine's own
convention over the full inventory and makes `check_subsample_agreement` a real check rather than a
guaranteed failure.

**Do not patch it in isolation.** `extract_fullevent_fps.py` is sha256-bound by the LIVE Gate-4
receipt `state/p3f-pet-gate4-launch-code-gate-20260801b.json`, so editing it voids that gate.
RESTORE Step 2's Gate-2 target rebuild already forces another Gate-4 re-issue for a physics reason,
and this belongs in that batch — together with the stress-closure push telemetry
(`p3f-pet-gate4-launch-code-gate-20260801b.json :: closure_evidence_recorded.omitted_muon_stress
.power_note`). Both are recorded so neither goes stale the way B-6's status did.

## Why this was worth catching before 08-03

The extractor was added 2026-08-01 (`dfef335`), 579 lines, marked *"code only; never run"*, and it
is the only full-event extraction path in the repo (J02 found there was none at all). Its first
execution would otherwise have been on 08-03, after the Gate-2 target rebuild and after an
8-hour GPU nominal, on the one dump that cannot be regenerated cheaply.

**The Gate-4 driver itself passed the same run** — stage 2 of 20778127 took the 13-feature loader
(`dfef335`) and the Step 2b persistence block (`5410ab0`) through PET, MultiFold and the save path
end to end for the first time, and produced a well-formed weights npz. That is also new
information: the driver had never executed anywhere either, because it calls
`build_fullevent_loaders` with no `refine_fn` override and therefore imports ROOT through the
learned Stay-Positive refiner. The smoke run injected an sklearn refiner, which self-reports
`refinement_is_learned_production=False` — exactly what Gate-4's target-provenance check refuses,
so the run cannot be mistaken for a publication result.
