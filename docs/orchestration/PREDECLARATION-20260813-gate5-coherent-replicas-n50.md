# PREDECLARATION 2026-08-13 — Gate 5, F7 coherent statistical replicas at N=50

**Written before any replica is submitted, and before the replica code path exists.** Nothing here was
chosen after seeing a spread.

## Authority, and WHY 50 — the sentence that is available now and unavailable later

Joseph, verbatim: **"sounds good, get N=50 up and running"**.

**The reasoning is the mediator's (`[CLAUDE]`-class), endorsed by him and not authored by him.** Recorded
so a referee is not told he chose 50 on grounds he never stated:

> Rank is not the criterion — 1431 bins is unreachable at any affordable N, and the rank-deficient GoF
> treatment is already disclosed under `OI-29`. The criterion is **precision on a subdominant component**:
> the fractional uncertainty on an estimated standard deviation is `1/√(2(N−1))`, giving **10.1% at N=50**
> against a model-dominated systematic budget. **N=100 buys 7.1% for double the compute**, on a term that is
> not driving the total.

**Verified arithmetic:** `1/√(2·49) = 0.10102` and `1/√(2·99) = 0.07107`. So 50 → 10.1%, 100 → 7.1%.

**This paragraph exists because it is the first objection a referee raises** — *was N chosen for a target
precision, or chosen after the spread looked acceptable?* **It is on the record before the first replica
runs, which is the only time that answer is worth anything.**

**Do not conflate this N with Gate 6's.** Gate 6's `N = 5` is *ensemble members averaged per step*; this
`N = 50` is *bootstrap replicas for the statistical component*. Different quantities, different
literatures, different conventions.

## WHAT MUST BE BUILT FIRST — this gate has no implementation

Measured, so nobody re-derives it:

- **The full-event driver cannot draw a replica.** `train_fullevent_nominal.py` has **no `--bootstrap-seed`
  argument**, and its single `bootstrap_seed=` occurrence (`:652`) writes `-1` into the dump to mark
  nominal-vs-replica. **Absence, not refusal.**
- **`train_fullevent_nominal.py:252` is NOT a replica guard** and must not be "fixed" to enable one. `rt`
  there is the **target receipt's** block, so the check keeps a replica's *target* out of the nominal. It
  fires in the opposite direction, and deleting it would remove a nominal protection while adding no replica
  capability.
- **The loader side is largely done and tested:** `bootstrap_seed` is in `build_fullevent_loaders`' signature
  (`:1077`), `validate_coherent_bootstrap` exists (`:750`), and D1's coherent dual-leg draw carries a real
  power test — `test_d1_dual_leg_weights.py:178` asserts *"the draw must actually zero some rows"*, so it
  cannot pass by drawing nothing.
- **`assert_refined_target_is_replica` (`:736`) has ZERO production callers.** All five call sites are in
  `tests/test_fullevent_gate2.py`. **The per-replica-target rule is specified, implemented, tested, and
  enforced by nothing.** Gate 5 is the path that must call it. **If the replica path is built without
  wiring it in, the suite still passes and the rule silently does not exist.**

### THE PINS CHANGE THE ARCHITECTURE, and this is the finding that most affects the plan

**`train_fullevent_nominal.py` is a LIVE PIN in `p3f-pet-gate4-launch-code-gate-20260812.json`**, and its
`sha256` matches the working tree exactly — verified this turn. So are `launcher`, `launcher_test`,
`validator`, `validator_test`, and 12 others: **17 pins, five of them tests.**

**Therefore adding `--bootstrap-seed` to the nominal driver costs a Gate-4 code-gate re-issue and
re-attestation of all 17 pins — not a one-line edit.**

**`fullevent_fps_dataloader.py` is NOT pinned.** So loader-side work, including wiring
`assert_refined_target_is_replica` into the production path, is free of the gate.

**Adopted architecture: the replica path gets its OWN driver and launcher; the pinned nominal driver is not
modified.** This follows the precedent already set in this repo —
`sbatch_pet_fullevent_nominal_annealed.sh` exists as a separate launcher for exactly this reason, and its
header records why reusing the canonical one was wrong. It keeps the nominal's guards, pins and receipts
intact, and it puts the replica-target guard on the path that actually needs it.

## THE PROCEDURE, per replica, in this order

Gate 5's own text fixes the ordering and it is not negotiable:

1. Enumerate complete ordered data / signal-MC / background-MC inventories **before** any training subset.
   Independent single-rank job; Horovod and distributed rank slicing prohibited.
2. Draw one **coherent** Poisson factor per inventory member from a persisted, replayable replica seed policy.
3. Apply data factors to data weights, signal factors everywhere signal MC is used, background factors to the
   negative background injection.
4. **Fresh Stay-Positive refinement for that replica, after applying background factors** — a
   negweight-refined target build **per replica**, enforced by `assert_refined_target_is_replica`. A nominal
   target can never stand in.
5. Select the training subset **without** redrawing, shortening or reindexing the full factors.
6. Reuse the exact applicable factors during full extraction and completeness/count construction.

**Two jobs per replica, necessarily:** the target build imports ROOT via `u2d.refine_stay_positive`, the
training needs TF, and **no Perlmutter interpreter carries both** — so ROOT target build, then TF training
consuming the precomputed target.

## COST, measured from `sacct` rather than estimated

| component | job measured | wall | allocation |
|---|---|---|---|
| negweight-refined target build | `56344268` | **00:55:32** | 256 CPU, 1 node, **no GPU** |
| full-event training | `56563761` | **06:00:36** | 32 CPU + 1×A100, 1 node |

**Per replica: 0.93 CPU node-hours + 6.01 GPU node-hours = 6.94 node-hours** across two allocation types.

**At N=50: 46.3 CPU node-hours + 300.5 GPU node-hours**, ≈ **35 h wall-clock at 10 concurrent**.

## THE CRITERION

**Branch PASS** — 50 of 50 replicas complete, each persisting full inventory hashes, seeds, factor hashes or
replayable factors, subset indices, train/extract identity checks, target/refinement telemetry and
completion status. `C_stat` is then centred on the accepted nominal as Gate 5 specifies.

**Branch BLOCK** — **a missing unit invalidates the replica; a missing replica invalidates the declared
ensemble manifest.** That is Gate 5's own rule and it is adopted verbatim: 49 of 50 is not a 49-replica
ensemble, it is an invalid manifest. **Partial completion is reported, never silently centred.**

**Branch UNRESOLVED** — the realized replica-to-replica spread does not exceed the production same-path
scatter `1.26775e-4`. Then the statistical component is below this configuration's reproducibility floor and
is reported as such, **not as a small value**.

**Reported as realized exceedance, not a fitted gaussian tail** (`BEN-025`): a 16-seed spread estimate once
inverted a correct ranking in this campaign at `p=0.093`, with the 48-seed answer inside the CI the whole
time. **With N=50 the realized distribution is available and there is no reason to fit one.**

## HELD — not launched, and the reason is not caution

**No replica is submitted until Session C reports on input integrity.** The scratch inputs are ~24% smaller
than the current open-data files of the same name — three of three checked, ratio 1.243–1.244 — and the
download path does a straight `xrdcp` with no skim step, so the copies are either a valid older production
or truncated.

**Spending ~300 GPU node-hours on inputs whose integrity is under active question is the exact waste the
redirect was meant to stop.** And if C returns *truncated*, the answer is not to rerun Gate 5 — **it is to
stop everything and re-download, because Gates 1–4 consumed the same inputs.** The implementation work above
costs no allocation and proceeds now; the launch waits on one ROOT read.
