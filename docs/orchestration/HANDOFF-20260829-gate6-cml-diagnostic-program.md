# Handoff — Gate 6 `C_ML`: three gaps in the 2026-08-25 strategy, and one correction

*Written 2026-08-29. Continuation document. Assume the reader has none of this session's context.
Every value below was read from a committed artifact this session.*

---

## 1. Read this first, and treat it as governing

[`PET-GATE6-STRATEGY-20260825.md`](PET-GATE6-STRATEGY-20260825.md) is the strategy of record for PET
Gate-6 method development. It carries the scope statement, the eight-hypothesis evidence matrix
(H1–H9), the prospective convergence criterion, the code-path audit, the ranked prospective
experiments, the SC-1 predeclaration contract, and the running record of the PET-v2 equivalence
retries. **Read it before acting on anything here.** This document does not restate it, does not
re-rank its experiments, and does not supersede it.

In particular, do not reorder its ranking on the strength of this file. Its stated reason for putting
the fixed-draw equivalence test ahead of convergence tuning — *"tuning an estimator whose sampling
semantics remain open can optimize an object that is later redefined"* — is an argument this session
found no evidence against.

Gate 6 remains **BLOCKED**. The five prohibitions in
[`state/gate6-member-trajectories-result-56847059.json`](state/gate6-member-trajectories-result-56847059.json)
are live and unchanged: `do_not_select_passing_subset`, `do_not_construct_C_ML`, `do_not_move_central`,
`do_not_start_leg_2`, `do_not_retry_unchanged`. Nothing below unblocks it. Constructing `C_ML` needs a
separate decision from Joseph, and Gate 4's estimator-arm disposition blocks construction independently
regardless.

GAP 1 subsequently ran under its own predeclaration and conditional authorization. Its terminal
result is recorded in
[`state/gate6-full-inventory-result-57727774.json`](state/gate6-full-inventory-result-57727774.json).
No later section of this handoff may be read as reopening that completed measurement.

## 2. Gap 1 — the ensemble and the central value are not the same quantity

**This is the cheapest item in the file and it is a prerequisite for interpreting every ranked
experiment, because they all read normalization statistics.**

The five Leg-1 members and the four Leg F draws were scored on **their own 2M-event training
subsample**. `train_fullevent_nominal.py` re-reads `truth_scalars` from the dump, indexes it by `imc`,
and builds `central_vector` through `reporting_spectra(truth_scalars_sub, w_truth_leg, push,
pass_truth_sub)` — the subsample's `pass_truth` rows only. The adopted nominal is scored *after*
`extract_fullevent_fps.py` reweights the full 49,152,885-row signal inventory.

So every published comparison between a member trajectory and the nominal compares a subsample-scored
quantity against a full-inventory-scored one. `end_to_end_achieved_over_required`, the statistic the
whole Gate-6 rule is built on, is among them.

The fix needs **no retraining**: run the existing extraction path over the stored member checkpoints,
inference only. The inference contract the extractor needs is already persisted by the training driver
(`multifold_name`, `weights_folder`, `step1_checkpoint`, `step2_checkpoint`), and the driver's own
comment records why the event-feature normalization must come from the training subsample's statistic
rather than be re-derived at extraction — re-deriving it over 49.2M rows *"would feed the trained model
a differently-scaled input and produce a confident wrong answer with nothing to notice it."* Preserve
that, or the repair introduces the defect it is meant to remove.

This measurement is now terminal. GPU array `57727774` and its correlated CPU extraction array
`57727775` completed all five tasks with exit code `0:0`. The five full-inventory totals, in member
order, are `2.0448087237149787e-37`, `2.247077502840624e-37`,
`2.1376142198681958e-37`, `1.917341340982044e-37`, and
`1.8195098716407951e-37 cm2/nucleon`. Their mean is `2.0332703318093275e-37` and their range is
`4.2756763119982866e-38 cm2/nucleon`.

All five products contain 49,152,885 ordered full-inventory push rows and 285 finite spectrum cells,
with the same 262-cell reporting mask. The maximum shared-subsample relative deviation was
`1.1290585916586148e-4` against the frozen `1e-3` tolerance. All ten OI-136 stage inventories reported
exactly one checkout root and zero import violations. The GPU tasks used 3,969 seconds in aggregate,
or 1.1025 A100-hours of the 5 A100-hour allocation ceiling.

These numbers are a like-for-like diagnostic readout. They do not re-verdict a member and do not
select a subset. The five receipt prohibitions remain unchanged, Gate 6 remains blocked, and no
further compute is authorized by GAP 1 or by its terminal result.

## 3. Gap 2 — Leg X is predeclared, authorized, unrun, and absent from the strategy

[`PREDECLARATION-20260813-gate6-legX-2x2.md`](PREDECLARATION-20260813-gate6-legX-2x2.md) fixes a 2×2,
`{42,46} × {0,4}`, read at iteration 2 only. Cells A `(42,0)` and B `(46,4)` already exist as
`fullevent_ml_ensemble/member_1` and `member_5`; cells C `(42,4)` and D `(46,0)` are two new trainings.
Joseph authorized it verbatim ("Yes yes to the other B decision"; readout settled by "Sure, do iteration
2"), sequenced behind Leg F completing. **Leg F is now terminal, so that precondition is satisfied.**

A text search of `PET-GATE6-STRATEGY-20260825.md` for *Leg X*, *2×2*, `(42,4)` and `(46,0)` returns
nothing. The strategy's H5 asks a broader version of the same question — *"replicate a changed policy
across processes and at least two seed policies"* — so Leg X may have been deliberately absorbed rather
than overlooked. **This session could not determine which, and a future session must not assume.**
Reconcile the two before spending: either Leg X runs as predeclared, or the strategy's H5 programme
supersedes it and that supersession is recorded.

Why it matters that this is decided rather than drifted into: Leg 1's seed table advances estimator seed
and subsample seed together — `(42,0) (43,1) (44,2) (45,3) (46,4)` — so estimator initialization and
training-sample choice are **perfectly confounded** in the only family that has been run. Leg X is the
smallest design that separates them.

Its power is already computed and is the reason to think before spending. From the Leg F receipt's
`LEG_X_MDE_DERIVED_FROM_THIS_FLOOR`: with one run per cell the standard error of every effect equals the
across-process sd, so Leg X resolves an estimator-init effect of **0.0696 or larger** at 95%
(`t_crit_0975_4df = 2.7764`), which is 20.0% of the member spread. It cannot resolve anything smaller,
and **a null result at that MDE is not evidence of no effect**. If the live question is "is the effect
small," Leg X as predeclared cannot answer it, and replicated cells — the strategy's ranked item 4 — are
the right instrument instead.

## 4. Gap 3 — reco-side truncation has never been measured

The strategy is about sampling semantics and optimization. Representation is outside it, and one
representation number is missing that costs no GPU to get.

Both clouds are truncated to the 12 highest-energy constituents. On the **truth** side this was
validated and is essentially lossless for available-energy-scale observables: mean multiplicity 4.57,
median cloud-vs-stored residual 0 MeV, the whole deficit confined to the small fraction of events that
reach the cap. **That result is truth-side only and does not transfer.** The reco cloud is a different
object — `CVUniverse::GetRecoClusters` returns the full `cluster_*` collection with
`cluster_isMuontrack != 0` dropped, and mean cluster multiplicity is **11.09 in data and 11.15 in MC**
against a cap of 12, so the reco distributions pile up at the cap.

Measure, from the untruncated dump: the fraction of clusters and of deposited cluster energy discarded
beyond rank 12, and its dependence on event kinematics. Do this before proposing any token-cap ablation
or typed-object work, since it decides whether either is worth running.

This is also the evidence base for the standing external question about why the estimator uses generic
calorimeter clusters rather than typed reconstructed objects. The defensible form of that answer is that
the cluster level is *upstream* of the reconstruction layer, so nothing is discarded by construction —
an argument the 12-token cap weakens and this measurement would either restore or retire.

## 5. Correction to the record

**Array `56847059` trains nothing.** Its 13–14 minute elapsed times are a *trajectory* pass over
already-written checkpoints, as
[`PREDECLARATION-20260813-gate6-member-trajectories.md`](PREDECLARATION-20260813-gate6-member-trajectories.md)
states explicitly. The Leg-1 training array was **`56834281`**. Real training cost at this policy is
**~3h15m per member** — Leg F's four fixed-policy draws ran 03:12:35, 03:15:09, 03:15:26 and 03:17:24,
and the strategy's own SC-1 estimate already uses the correct 3.25 h mean.

Recorded because the 14-minute figure is the first number a reader meets in the member-trajectory
receipt, and sizing a new arm from it understates the compute by roughly 14×.

## 6. Rejected alternatives — do not re-propose without new evidence

Several of these were proposed during this session and retired against committed evidence. They are
recorded so the next session does not spend on them.

- **Logit-cap saturation as the cause of the member spread.** `cap_saturation_frac = 0.0`. Excluded by
  name in [`FINDING-20260807-step1-under-achieves.md`](FINDING-20260807-step1-under-achieves.md) and
  repeated in every `p3f-pet-gate4-launch-code-gate-*` receipt since;
  `state/annealed-nominal-complete-56563761.json` records
  `cap_saturation_fraction_both_arms: 0.0`. A quantity that is zero everywhere cannot produce spread.
- **A biased train/validation split.** Excluded in the same finding.
- **The missing learning-rate anneal.** The fit-time anneal (base `1e-4` → `1e-5` from iteration 1, two
  base plus four annealed fits, implemented as a `MultiFold` subclass overriding `CompileModel` at fit
  time with no engine edit) was adopted as production policy on 2026-08-10 in `54a87978` — *before* the
  Leg-1 family trained on 08-13. The observed spread is what survives that fix, not what it would
  remove.
- **Step-1 class ratio as the cause of member-to-member spread.** It is tied to the full inventory and
  common across members, so it cannot vary between them. It remains worth understanding as a mechanism
  — `check_step1_class_ratio.py` carries a fail-closed self-check against the Gate-2 receipt's
  `raw_signed_sum = 4006528.6006158064` — but not as an explanation of dispersion.
- **Reading Leg X at iteration 0 or 1.** The Leg X predeclaration's provisional floor table gives the
  same-seed process spread as **89.6%** of the member spread at iteration 0 and 49.4% at iteration 1,
  against 15.1% at iteration 2. A 2×2 read at iteration 0 reports seed main effects indistinguishable
  from process noise, with the same apparent precision as a real result. Iteration-0 and -1 values will
  still be computed and persisted, and must be reported as ineligible rather than quietly omitted.
- **An unweighted 63%-subsample "effective statistics" nominal, as a bootstrap control.** Proposed and
  withdrawn this session: it does not reproduce a Poisson(1) bootstrap, because it omits multiplicity
  greater than one and the weight variance entirely. The strategy's fixed-draw weighted-versus-literal
  test (H8) is the faithful version and is already in flight.
- **Treating `FLOOR_INTERMEDIATE` as a soft pass.** The Leg F receipt lists this explicitly under
  `WHAT_NO_ONE_MAY_DO_WITH_THIS`. Neither predeclared branch fired and the outcome licenses nothing.

## 7. Deliberately left alone

- **Gate 4's estimator-arm disposition** — an independent user decision that blocks `C_ML` construction
  regardless of anything here.
- **`OI-126` and the `C_stat` band** — ruled 2026-08-20, pairing declined, PET demoted. Do not restart
  the completed containment, tail-geometry, target-factor, extraction or occupancy probes.
- **The 59 `OI-136` fail-open files** — route new compute through `nd-unfolding/mnv_guarded_run.py`; the
  sweep is not part of this work.
- **The PET-v2 retry-2 target non-reproducibility** — 1,141,467 rows differed with mean absolute row
  difference `5.15e-08` and `settled_cause: false`. A real loose end, but it belongs to the equivalence
  thread and is recorded there.
- **The Gate-6 convergence criterion itself.** The strategy's H1/H2 argue it is poorly calibrated — the
  `0.10` traces to an iteration-0 diagnostic-label branch in `step1_increment_trajectory.py` rather than
  a calibrated final tolerance. That analysis stands as written and changes no historical verdict; do
  not relitigate it here.

## 8. Status grid

| Item | Where | Status to confirm |
|---|---|---|
| Strategy of record | `PET-GATE6-STRATEGY-20260825.md` | Governing. Read before acting. |
| Leg 1 five-member ensemble | `state/gate6-member-trajectories-result-56847059.json` | Complete; `BLOCK_GATE6_ML_ENSEMBLE`. Trained in `56834281`, not `56847059`. |
| Leg F process floor | `state/gate6-floor-replication-result-56863958.json` | TERMINAL. `F_range = 0.0645`, `FLOOR_INTERMEDIATE`. Do not re-run. |
| Leg X 2×2 cells C, D | `PREDECLARATION-20260813-gate6-legX-2x2.md` | Not run. Authorized, precondition satisfied, absent from the strategy — reconcile first (§3). |
| Full-inventory member evaluation | section 2; `state/gate6-full-inventory-result-57727774.json` | TERMINAL. Five inference and five extraction tasks completed; diagnostic only. No re-verdict, `C_ML`, central movement, Leg 2, retry, publication claim, or further compute. |
| Reco truncation audit | §4 | Not run. No GPU required. |
| PET-v2 equivalence retry 3 | `state/pet-v2-fixed-draw-equivalence-changed-retry3-submission-57644535.json` | SUBMITTED 2026-08-27T06:51Z; target `57644535`, training `57644536`, eval `57644537`, validation `57644538`. Live state unknown here — observe before resubmitting. |
| Data-only `C_stat` smoke | `HANDOFF-20260819-lane-e-data-only-cstat-smoke-57266000.md` | Array `57266000` queued before the 08-19→26 maintenance; state unknown. Resubmission **not** pre-authorized. |

## 9. Before launching anything

Re-read `AGENTS.md` and the governing `OI-*` record; both outrank this file and the strategy. Confirm the
Gate-6 prohibitions by opening the receipt rather than trusting any summary of it. State, in the launch
record, both the quantity the run measures and what a terminal result cannot authorize. Route compute
through `nd-unfolding/mnv_guarded_run.py` (`OI-136`). Inspect `git status` afterwards.

`docs/orchestration/MANIFEST.tsv` carries one row per orchestration artifact. This file is not in it;
regenerate the manifest with its generator rather than hand-editing a row.
