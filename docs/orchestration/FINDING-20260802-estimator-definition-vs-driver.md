# FINDING 2026-08-02 — the contract defines the nominal estimator with a batch size the driver does not use

*Found by the 2026-08-02 coverage survey, category 5 ("invariants with no executable check"), by
asking what enforces `batch 1024` and discovering the answer is nothing — and then that nothing
uses it either.*
*Status: CONFIRMED, and RESOLVED as **512** on 2026-08-02 — see "Which number wins" below. The
contract sentence is corrected; the plumbing is still owed and rides the Step 2b re-issue.*
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

## Which number wins: 512. Resolved 2026-08-02 by provenance, not by preference

The question "was 1024 ever run for the full-event estimator?" has a clean answer, and it is *no —
and it never could have been.*

**1024 is the recoil-only campaign's batch size.** It appears in exactly two places in the tree,
both on the quarantined recoil-only path: `minerva_pet_dataloader.py:360` and
`phase7_retrain_universe.py:153`. Nowhere else.

**The contract sentence predates the estimator it describes by five days.** `git log -S'batch 1024'`
puts it at `b7ba96f`, **2026-07-16**. `train_fullevent_nominal.py` did not exist until `ada72b0`,
**2026-07-21**. So the line could only have been describing the recoil-only configuration that
existed when it was written; it was never a decision about the full-event estimator, because there
was nothing to decide about yet.

**Every full-event training in the tree is 512**, and one of them is load-bearing:

* `train_fullevent_nominal.py:238` — the driver, since the day it was created
* `stress_closure_muon.py:95` — hardcoded
* `closure_fullevent_fps.py:73` — `--batch-size` default
* and therefore the **B-6 omitted-muon stress PASS this very gate records** (Delta job 20758087,
  2026-08-02) was produced at 512. Launching the nominal at 1024 would gate it on a closure run
  under a different optimization trajectory.

**No nominal precedent is being overridden.** Gate-4 is `PASS_CODE_ONLY` and Step 4 has never
launched, so the full-event nominal has not been trained at either value. There is no result to
preserve — only a definition to make true.

Decisive framing: this document is the one that quarantines the recoil-only lane ("recoil-only PET
UQ is NEVER attached to either"; "the recoil-only campaign's additive C_syst+C_retrain is a
QUARANTINED cross-check, never transferred"). A recoil-only *hyperparameter* reaching the
full-event estimator's own definition is exactly the leak this contract exists to prevent, arriving
by the one route it does not screen — prose.

The contract sentence was corrected to 512 on 2026-08-02. It is safe to correct alone because the
`.md` is not in the live receipt's `files`.

## Still owed: plumb it, at Step 2b

Correcting the sentence removes a contradiction; it does not create enforcement. `batch_size` should
get the same four-part treatment `niter`/`epochs`/`seed`/`subsample` already have:

1. a `NOMINAL_SEED_POLICY["batch_size"] = 512` entry,
2. a `--batch-size` CLI arg defaulted from it,
3. the `MultiFold(...)` call reading `args.batch_size` instead of the literal,
4. a `FROZEN["seed_policy"]["batch_size"]` key that `check_freeze` reads **from the artifact**.

Step 4 records it, so (4) needs the driver to persist it alongside the other seed-policy keys.
Without (4) this recurs: the sentence is true today and unguarded tomorrow.

**No rationale for 512 is recorded anywhere** — `ada72b0`'s message does not mention it. The
plausible reason is memory: a full event carries more tokens than a recoil cloud, so halving the
batch is the natural adjustment. That is a guess and is *not* written down; if the real reason was
something else, it belongs in the docstring when (1)–(4) land.

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
