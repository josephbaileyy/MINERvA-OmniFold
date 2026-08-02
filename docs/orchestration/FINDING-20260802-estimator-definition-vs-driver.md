# FINDING 2026-08-02 — the contract defines the nominal estimator with a batch size the driver does not use

*Found by the 2026-08-02 coverage survey, category 5 ("invariants with no executable check"), by
asking what enforces `batch 1024` and discovering the answer is nothing — and then that nothing
uses it either.*
*Status: CONFIRMED as a discrepancy. The RESOLUTION is a physics decision, not a code fix.*
*Severity: it is the definition of the estimator that launches at Step 4. Bounded — it changes the
optimization trajectory, not the observable schema.*

## Claim

`FULL_EVENT_FEATURE_CONTRACT.md:36` defines `pet-fullevent-fps-v1`:

> niter 2, epochs 8, **batch 1024**, Adam lr 1e-4, train subsample 2M.

`train_fullevent_nominal.py:238` — the bound `driver` of the live Gate-4 launch-code receipt —
calls:

```python
of = MultiFold(mf_name, m1, m2, data, mc, niter=int(args.niter),
               epochs=int(args.epochs), batch_size=512, ...)
```

Every other trainer in the tree agrees with the code, not the contract:
`stress_closure_muon.py:95` also hardcodes `batch_size=512`, and the fixture at
`tests/test_coupled_phi_guards.py:29` records `{"niter": 3, "epochs": 8, "batch_size": 512}`.

## Why nothing caught it

Four of the five numbers in that sentence are plumbed and frozen. The fifth is neither.

| contract term | CLI arg | in `NOMINAL_SEED_POLICY` | in Gate-4 `FROZEN["seed_policy"]` |
|---|---|---|---|
| niter 2 | `--niter` | yes | yes |
| epochs 8 | `--epochs` | yes | yes |
| subsample 2M | `--max-events` | yes | yes (`train_events`) |
| seed 42 | `--estimator-seed` | yes | yes (`estimator_seed`) |
| **batch 1024** | **no** | **no** | **no** |

So `check_freeze` cannot see batch size at all. A nominal run at 512 would validate as
`pet-fullevent-fps-v1` and the gate would report PASS, exactly as the contract's own sentence is
violated. This is the audit-B2 defect class one level out: not a check comparing FROZEN to FROZEN,
but a documented term of the estimator with no entry in FROZEN to compare against.

**Adam lr 1e-4 is in the same position, and currently correct by luck.** The driver never passes
`lr`, so it inherits `MultiFold.__init__`'s default (`omnifold_nn/omnifold/omnifold.py:57`,
`lr = 1e-4`). The contract sentence is true today only because a vendored default happens to
match it. `omnifold.py` *is* hash-bound by the live receipt as `estimator_engine_multifold`, so a
change upstream would be detected — as an unattributed hash move, not as "the contract's lr is now
false."

## It is not a throughput knob

`batch_size` sets `self.BATCH_SIZE`, which sets `num_steps_reco` / `num_steps_gen`
(`omnifold.py:131-132`), which are passed to `get_optimizer(num_steps)` and shape the learning-rate
schedule. 512 vs 1024 is a different optimization trajectory at the same seed, not the same answer
computed in different-sized chunks. It is not on the same footing as, say, an inference batch.

## What to do

**Do not patch either side unilaterally, and do not "fix" the contract by writing 512 into it.**
Two things follow:

1. **Decide which number is the nominal estimator.** The evidence favours 512 being the practice
   and the sentence being stale — three independent sites say 512 and nothing but that sentence
   says 1024 — but this is a decision about the published estimator and it is Joseph's, not a
   session's. Ask whether 1024 was ever run, or whether the sentence was written from an intended
   configuration that never landed.
2. **Whichever way it goes, plumb it.** `batch_size` should become a `NOMINAL_SEED_POLICY` entry, a
   `--batch-size` CLI arg defaulted from it, and a `FROZEN["seed_policy"]` key read from the
   artifact — the same four-part treatment niter/epochs/seed/subsample already get. That is the
   part that stops this recurring, and it is worth doing even if the answer is "512 was always
   right."

## Sequencing: this rides the 08-03 re-issue, it does not precede it

`train_fullevent_nominal.py` (`driver`) and `validate_pet_nominal_gate4.py` (`validator`) are both
bound by the live `p3f-pet-gate4-launch-code-gate-20260801b.json`. Editing either voids that
receipt, so this batches with the two items already owed there — the extractor `pass_truth` fix
(`FINDING-20260802-extractor-pass-truth-mask.md`) and the measured
`fold_forward_ratio_dev_max` — into **one** re-issue at RESTORE Step 2b rather than three.

`FULL_EVENT_FEATURE_CONTRACT.md` is *not* in that receipt's `files` (it is referenced only in
`reissue.why` prose), so the contract can be edited without voiding anything. The stale truth-cloud
KNN row was corrected on 2026-08-02 for that reason. **The batch line was deliberately left alone**
— unlike the KNN row, the code does not settle which side is wrong.
