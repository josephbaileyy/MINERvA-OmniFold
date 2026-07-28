# Brief: audit EXECUTOR (has tool + cluster access)

Written 2026-07-28. Companion to `start-audit-planner.md` — **read that file's
"HARD CONSTRAINTS" and "Do not mistake gate names for evidence strength" sections
first; they apply here unchanged and are not repeated.** This file adds only what
an executing session needs and a planning session does not.

## The one rule that matters most

Before and after any sweeping edit:

```bash
python3 docs/orchestration/verify_hash_bindings.py
# expect: resolved 92 / 88 OK / 4 known pre-existing drift / ALL BINDINGS INTACT
```

A new mismatch is a **stop**, not a thing to fix by updating the hash. Six gate
bindings were voided this way on 2026-07-28 with the suite still green.

## Frozen-file map (as of 2026-07-28)

Do **not** edit these without deliberately re-running the owning gate and
re-issuing its receipt:

| File | Frozen by |
|---|---|
| `nd-unfolding/pet/fullevent_fps_dataloader.py` | Gate-2 canonical runtime PASS |
| `nd-unfolding/pet/gate2_target_runtime.py` | Gate-2 canonical runtime PASS |
| `nd-unfolding/pet/train_fullevent_nominal.py` | Gate-4 launch-code gate |
| `nd-unfolding/pet/validate_pet_nominal_gate4.py` | Gate-4 launch-code gate |
| `nd-unfolding/tests/test_p3f_pet_fullevent_launcher.py` | Gate-3 launch-code gate |
| `nd-unfolding/pet/sbatch_p3f_pet_fullevent_evloop_array.sh` | Gate-3 launch-code gate |
| `nd-unfolding/pet/dump_pointcloud_inputs.py` | G2 dump receipt |

**Note the coupling:** the Gate-2 receipt binds the loader *and* the validator
together, so patching either voids both. Any Gate-2 change is a two-file
re-issue.

Four bindings are *already* drifted and deliberately left alone as submit-time
provenance (`wakerctl.py`, `test_wakerctl.py`, `sbatch_dump_g2_mefhc.sh`,
`gate2_queue_hedge_controller.sh`). They are allow-listed in the verifier. Do not
"fix" them.

Known-not-frozen, so free to edit: `fps_build_publication_manifest.py`,
`tests/test_fps_cli_integration.py`, `tests/conftest.py`,
`make_synthetic_g2_fullevent.py`, `closure_fullevent_fps.py`,
`floor_gpu_nondeterminism.py`, and everything under `docs/`.

## Test baseline

`python -m pytest nd-unfolding/tests -q` → **7 failed, 333 passed, 1 skipped**
(verified 2026-07-28, off-Perlmutter).

All 7 failures are one root cause: the absent
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/omnifold_nn/omnifold/dataloader.py`.
**They should all pass on Perlmutter**, so the post-restore expectation is 0
failed. `tests/conftest.py` additionally skips
`test_p3f_pet_fullevent_launcher.py` via `collect_ignore` only while its frozen
absolute path is absent — that skip lifts automatically on Perlmutter and the test
must then pass.

One test deliberately branches by platform:
`test_cli_pub_builder_receipt_gate_still_closes_when_endpoints_valid` accepts
either of two gate messages, because `fps_verify_merged_receipt.REPO` is a
hardcoded `/pscratch` literal — `verify()` raises off-Perlmutter but succeeds on
it. Do not tighten it to one message.

## Cluster facts

**Perlmutter** — in maintenance until **2026-08-03 22:00 PT**. `/pscratch` returns
with Perlmutter, *not* with the DTNs (shared-facility group returned ~07-29).
Account `m3246`; CFS `/global/cfs/cdirs/m3246/josephrb`. The **only** copy of
`G2_FPS_MEFHC_P12.npz` (9,897,374,636 B, sha `fa6b3463…a29625`) is on purgeable
`/pscratch` with no backup — see `RESTORE-2026-08-03.md` Step 1.

**NCSA Delta** — account `bhvk`, user `jbailey2`.

- `ssh delta` reuses a ControlMaster (`~/.ssh/config` `Host delta` block,
  `ControlPath ~/.ssh/cm-delta`). If the master dies, re-auth needs Duo 2FA and
  must be run interactively by the user.
- Balances measured 2026-07-28 via `accounts`: **814 GPU-hr of 1000**, **2395
  CPU-hr of 3000**. Allocation **end date is not in Slurm** — `accounts` is a perl
  wrapper over association data and `sacctmgr` returns empty `grptresmins`. It is
  in the ACCESS portal. Don't burn time probing for it.
- Repo checkout: `/u/jbailey2/MINERvA-OmniFold`, **11 commits behind
  origin/main** as of 2026-07-28. Its `closure_fullevent_fps.py` and
  `make_synthetic_g2_fullevent.py` are byte-identical to main (verified by
  sha256); they only *look* modified/untracked because the adding commits are not
  pulled. **`git pull` before running anything.**
- Container: `/u/jbailey2/tf215.sif`. **The filename lies — it is TF 2.14.0**
  (verified 2026-07-28). NGC `tensorflow:24.01-tf2-py3`: horovod 0.28.1, sklearn
  1.2.0, numpy 1.24.4, **no ROOT**.
- Nodes: `gpuA100x4` 64 cores / 257,630 MiB (251.6 GiB); `cpu` 128 cores / same
  memory. There are ~2 TB nodes in the `full` partition (incl. `gpu:h200:8`) if a
  memory ceiling turns out to be the blocker.
- Scratch: `/scratch/bhvk/jbailey2`. Runbook: `nd-unfolding/PET_TRAINING_ON_DELTA.md`.

## HARD BARS — things that are not allowed to be done

1. **No publication nominal on Delta, ever — not even after data is staged.** The
   container has no ROOT and `u2d.refine_stay_positive` (the canonical
   Stay-Positive refiner the negweight-refined nominal requires) imports ROOT at
   module load. Delta can only produce the purity control or an injected sklearn
   refinement, and the latter self-reports
   `refinement_is_learned_production=False`. Any P5A nominal runs on Perlmutter
   under TF 2.15.
2. **No extension or promotion of the recoil-only (`xps2`) path** as a full-event
   product — barred by `docs/OPEN_ITEMS.md`; KNOWN_ISSUES #19.
3. **No third GPU-nondeterminism floor repeat.** Bounded at 4.6% of the 4.4833%
   bar; binning *suppresses* it ~5.9× (per-event L1/sum 0.2060% → per-bin
   0.0349%). Decomposing node-vs-kernel on a 0.2% effect buys nothing.
4. **`--bkg-mode purity` is a labeled control, never the nominal.** Never harvest
   a synthetic-fixture run as physics evidence; its verdict line is tagged
   `[SYNTHETIC FIXTURE - PLUMBING ONLY, NOT THE P5A RECEIPT]` for that reason.
5. **Never hand-edit a receipt sha256.**

## Priority work item: the host-RAM measurement

**Status as of 2026-07-28: designed, not submitted.** On the 08-03 critical path,
CPU-only, no GPU hours. Do this before any GPU rehearsal — if it confirms the
projection, the fix is a code change and a GPU wall-clock number for the current
loader is worthless.

**What is being tested.** `fullevent_fps_dataloader.py:520-521` materializes the
full 49.15M-row `part_gen` before `[imc]` subsamples it, `build_truth_cloud`
stacks to (n,12,8) through several full-size temporaries, and `rank`/`size` only
reach `DataLoader` at `:612` — after the clouds are built. So all 4 MPI ranks
hold full copies. Projected construction peak ~78 GiB/rank → **~310 GiB against a
251.6 GiB node**.

**Design.**

1. Generate fixtures with **`--tokens 12`** (NOT the default 40 — the real dump
   has 12 slots) at `--n-sig` ∈ {2M, 5M, 10M, 20M}, with data/bkg scaled to the
   real dump's ratios: `n_data ≈ 0.0837 × n_sig`, `n_bkg ≈ 0.0115 × n_sig`
   (from real inventory 49,152,885 / 4,116,128 / 564,591).
2. For each, call `build_fullevent_loaders` with
   `max_events = round(0.8138 × n_sig)` — the same 40M/49.15M ratio as the real
   nominal — so the materialize-then-subset pattern is reproduced at every scale.
3. Record peak RSS per rung (`resource.getrusage(RUSAGE_SELF).ru_maxrss`).
   Single-process is sufficient and much cheaper: ranks are symmetric at the peak
   because sharding happens after construction. Multiply by 4 for the node total.
4. Fit peak RSS vs `n_sig` (expect near-linear), extrapolate to 49.15M, compare
   `4 ×` that against 251.6 GiB.
5. Confirm the ×4 assumption once with a real 4-rank run at a small rung (2M).

Runs in the container on a `cpu` node. Budget ~1-2 h on modest cores (tens of
CPU-hr of the 2395). **Report the measured numbers, not a verdict on the
projection alone** — and if it comes out under the ceiling, say so plainly rather
than defending the estimate.

## Other pending items

- **Gate-2 units resolution** (frozen files; a two-file re-issue) —
  `RESTORE-2026-08-03.md` Step 2.
- **p3f launcher `#SBATCH --output=`/`--error=`** absolute paths
  (`sbatch_p3f_pet_fullevent_evloop_array.sh:12-13`) — frozen by Gate-3, so a
  re-issue, not an edit.
- **Delta product durability** — push `pet_weights_fps_xps2_delta_s101.npz` (sha
  `9a09125f…`) and `_rep.npz` (sha `85b595b2…`, 266,046,028 B) from Delta `$HOME`
  to `/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/results/`. ~532 MB,
  ~76 GPU-hr to regenerate, currently single-copy. Needs only the DTNs.

## Reporting

Append run outcomes to `docs/orchestration/RUNS.tsv` (13 columns) and narrative to
`nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`. Both are **append-only** — never rewrite
history. A result is live only once its receipt/summary/ledger commit is pushed.
State plainly when something failed or was skipped.
