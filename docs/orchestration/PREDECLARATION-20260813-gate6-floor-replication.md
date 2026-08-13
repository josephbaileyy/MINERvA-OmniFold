# Gate 6 Leg F — across-process floor at the fixed member-1 policy `(42,0)`

**Fixed at 2026-08-13T13:2xZ, before any new draw exists and before any floor value is computed.**
Authorized by Joseph via the mediator (*"Yes let B do it"*) as the inversion of the precondition in
`PREDECLARATION-20260813-gate6-member-trajectories.md`, which already names this control verbatim —
*"five total across-process draws of the fixed member-1 policy `(42,0)`, including four new runs with
persisted execution-environment identity"* — but gated it behind *"If all five pass."* The family did
not pass; the precondition is inverted, not removed, and the rest of that predeclaration stands.

**This is a MEASUREMENT, not a retry.** That is why it proceeds under `do_not_retry_unchanged`. All
five prohibitions at `19585b7` remain live and untouched: `do_not_select_passing_subset`,
`do_not_construct_C_ML`, `do_not_move_central`, `do_not_start_leg_2`, `do_not_retry_unchanged`.
**Gate 6 is not unblocked by this leg, whatever it returns.** Constructing `C_ML` needs a separate
decision from Joseph that he has not made, and Gate 4's estimator-arm disposition remains an
independent user decision that blocks construction regardless.

## The question, and why the existing five members cannot answer it

Members 2–5 failed the Gate-6 convergence rule and member 1 passed. Member 1 is also the carrier of
the adopted nominal's seed policy. That coincidence is `n=1` and is a **hypothesis, not a finding**.
The two readings it cannot distinguish:

- **seed-determined** — the trajectory is a reproducible function of the seed pair, so members 4 and 5
  represent real seed sensitivity;
- **process-determined** — the trajectory varies run-to-run at *fixed* seed, so member 1's PASS was a
  draw and the member-level criterion is measuring process variation.

Today the only across-process scale in the problem is `VL113 = 1.62987e-02` from **one pair**, against
which member 3's total deviation is `2.617x` and member 1's final is `1.185x`. The Gate-6 comparison
instead used the **within-process** floor `VL112 = 1.26775e-04`, which is `128.6x` smaller, for members
that trained in five separate Slurm tasks on five different nodes.

## Inventory

Five draws of the **identical** policy `estimator_seed=42, subsample_seed=0, niter=3, epochs=8,
train_events=2000000, batch_size=512` — read off member 1's own artifact this turn, not from a constant.

| draw | source | status |
|---|---|---|
| 1 | the EXISTING `fullevent_ml_ensemble/member_1` artifact, reused unmodified | already measured: `v = 0.9806897311812962` |
| 2–5 | four new trainings | to be run |

Draw 1 is **not retrained**, so no member artifact is written, moved or replaced by this leg. Its
committed trajectory value is the fifth data point.

## Reconciliation done before this declaration, so the draws are comparable to draw 1

Verified this turn against the cluster, because a floor measured under different conditions is not a
floor:

- **Input dump unchanged**: `G2_FPS_MEFHC_P12.npz`, `fa6b3463…f2a29625`, 9,897,374,636 B.
- **The target the members consumed is back at the canonical path, byte-identical.**
  `gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy` now hashes `544b2f6a…93d54c9` — the same
  digest as the archived `superseded-20260813-pre-gate5-rerun/` copy the Gate-6 trajectory read. This
  is the bit-identity gate that `NOTE.md` says the Gate-5-driven Gate-2 re-run had to pass, and it
  passed. **So no `--target-npy` override is needed and none is used.**
- **The two Gate-2 receipts differ only in timestamp.** Canonical `8b858622…` (2026-08-13T09:38:40Z)
  vs archived `336e8e27…` (2026-08-05T05:16:22Z), but every field the driver's `assert_target_provenance`
  binds is identical in both: `status=PASS`, `weights.sha256=544b2f6a…`, `size_bytes=18723004`,
  `step1_feed.rows=4680719`, `normalized_sum=1124080.587652125`,
  `estimator_fingerprint=pet-fullevent-fps-v1`, `target_mode=negweight-refined`,
  `refinement_is_learned_production=True`, `bootstrap_seed=None`,
  `step1_class_ratio=1.1240802949941018`, and the same `input_preflight` digest and size. The driver
  binds by content, not by receipt identity, so the newer receipt is used and both digests are recorded.
- **The training code is byte-identical to what the members ran**: `train_fullevent_nominal.py`
  `91144bee…`, `fullevent_fps_dataloader.py` `e1402370…`, `omnifold_nn/omnifold/omnifold.py`
  `3a2022b0…` — each matching the pin table `sbatch_gate6_member_trajectory_array.sh` verified at
  array `56847059`.
- **The loader was edited for Gate 5 and that edit is measurably inert on this path.**
  `step1_increment_trajectory.py:144-145` rebuilds each member's subsample with the *current* loader
  and fails closed unless it equals the artifact's stored `mc_indices`; all five members passed that
  gate at `56847059`, after the edit. So the current loader reproduces the exact training subsample.

## Fixed rule — the statistic

For draw `j` and iteration `k ∈ {0,1,2}`, read only the numeric field
`end_to_end_achieved_over_required` from `step1_increment_trajectory.py`, exactly as the member
control did, and write `v[j,k]`. Define `d[j,k] = |v[j,k] − 1|`.

The floor statistics, at each iteration `k`:

- `F_range[k] = max_j v[j,k] − min_j v[j,k]`
- `F_sd[k]    = sample standard deviation of v[·,k]`, `ddof=1`

The reference scale, from the committed member values (VL116–VL120), in the same `v` form:

- `S_range[2] = 1.1014828481277632 − 0.7534768706675813 = 0.3480059774601819`

## Fixed rule — the verdict, three-way and mutually exclusive

Evaluated at `k = 2` only, because that is where the Gate-6 band applies:

1. **`FLOOR_SMALL_TRAJECTORY_IS_SEED_DETERMINED`** if `F_range[2] ≤ 0.05` **and** every draw has
   `d[j,2] ≤ 0.10`. The `0.05` is the **Gate-4 nominal fold-forward deviation bar** — a pre-existing
   scale in this problem that was not invented for this test. Reading: process variation is small
   against the member spread, member 1's PASS replicates, and members 4 and 5 are real seed sensitivity.
2. **`FLOOR_LARGE_TRAJECTORY_IS_PROCESS_DETERMINED`** if `F_range[2] ≥ 0.1740029887300910`
   (= `0.5 × S_range[2]`). Reading: at least half the observed five-member spread is reproducible at
   fixed seed, member 1's PASS was a draw, no seed can be expected to meet the band, and the defect is
   in the P5A nominal's reproducibility rather than in Gate 6.
3. **`FLOOR_INTERMEDIATE`** otherwise. Report `F_range[k]` and `F_sd[k]` for all three iterations and
   **attribute nothing.**

Both thresholds are absolute and fixed here. If the two conditions in branch 1 disagree — the range is
under `0.05` but some draw exceeds the band — the verdict is `FLOOR_INTERMEDIATE`, not branch 1.

## Fixed rule — validity, which is separate from the verdict

A draw is **INVALID INPUT** (not a failing member) unless all of these hold. Any invalid draw means
this leg reports `n < 5` and **reaches no verdict at all**; it does not proceed on the survivors,
because selecting a survivor set is the shape `do_not_select_passing_subset` forbids.

1. Slurm task `COMPLETED 0:0`, and a completion marker exists.
2. `target_provenance` PASS against the canonical receipt, with target `544b2f6a…`.
3. The **realized** `seed_policy` read off the produced artifact equals `(42,0)` with `niter=3`,
   `epochs=8`, `train_events=2000000`, `batch_size=512` — read from the artifact, never from the
   launch command.
4. `target.step1_class_ratio == 1.1240802949941018` **exactly**. `R` is subsample-invariant and shared,
   so any difference means a different target or a different inventory.
5. `mc_indices` **array-equal to member 1's**. `subsample_seed=0` is fixed across all draws, so every
   draw must train on the identical 2,000,000 rows. A draw that does not is not a same-policy replicate.
6. Gate A/B PASS with exact MC-index and truth-normalization identity, and the within-job
   decomposition reproduction gate PASS at `REPRO_RTOL`.
7. Exactly eight checkpoints in the draw's own isolated `w_nominal` directory, and no two draws sharing
   any output path.
8. Execution-environment identity persisted: host, Slurm job/array/task ids, GPU identity, and the
   code digests actually executed. This is the OI-15 residual and the thing an across-process floor
   exists to expose; a draw without it cannot serve as an across-process data point.

## What this leg does NOT establish, stated so a later reader cannot borrow it

- **It does not re-verdict any Gate-6 member.** It supplies a scale. Re-verdicting members against
  that scale — including member 3, whose only failing margin is `+0.001098` — is a separate decision.
- **It does not calibrate the checkpoint-tier gap.** All draws read iterations 0/1 from best-epoch and
  iteration 2 from `_final`, so `F_range` is a clean like-for-like *across processes* and says nothing
  about the ~1.3% best-epoch-vs-`_final` systematic (BEN-121). That is Leg 0, which is not authorized.
- **It does not attribute variance between estimator initialization and training subsample.** Both are
  held fixed here. That is Leg X, the `{42,46}×{0,4}` 2×2, authorized separately and sequenced after
  this leg because a 2×2 has one degree of freedom per main effect and no replication, so it has no
  internal error scale until this floor exists.
- **It does not license `C_ML`, move the central, start Leg 2, or select a subset.**

## Execution

`nd-unfolding/pet/sbatch_pet_fullevent_floor_replicate_array.sh`, array tasks 2–5, one A100 per draw,
four stages per task: train, Gate A/B, pull/push decomposition, trajectory. Outputs are draw-scoped
under `fullevent_floor_42_0/draw_${N}/`; no two tasks share a final path and each takes a writer lock.

**Gate 5 keeps priority on GPU slots.** Arrays `56857232`/`56857233` are live. Their pending tasks are
held by `JobArrayTaskLimit` and `aftercorr` — their own array cap and dependency, not by resource
scarcity — so Gate 5's throughput is bounded at ten concurrent regardless of this submission. This leg
still caps itself at **two concurrent tasks** (`%2`) and submits at **`--nice=10000`**, so Gate 5
outranks it at every scheduling decision. Cost of the self-cap: two waves instead of one, ~7 h instead
of ~3.5 h, landing well before Gate 5's ~19:20–20:10 PDT family.

`/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059` is `GATE5_CODE_ROOT` and is **not touched**.
`/pscratch/sd/j/josephrb/gate6-reconcile-56834281` is read only, for the pinned diagnostic scripts,
and is not written to.
