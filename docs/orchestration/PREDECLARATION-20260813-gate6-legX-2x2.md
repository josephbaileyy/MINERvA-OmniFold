# Gate 6 Leg X — the `{42,46}×{0,4}` 2×2, read at iteration 2 only

**Fixed at 2026-08-13T22:2xZ, before either new cell exists and before any Leg X value is computed.**
Two of the four cells were trained on 2026-08-13 in array `56847059` and their iteration-2 values are
already committed, so this document is written knowing two of four cells. **That is stated up front
because it is the one respect in which this predeclaration is weaker than Leg F's**, where nothing but
draw 1 existed. What it fixes is the *rule* — the statistic, the reference scale, the threshold and its
provenance, and what a null result is allowed to mean — none of which can be derived from the two known
cells, because the reference scale comes from Leg F and Leg F is not finished.

**GATE 6 IS NOT UNBLOCKED BY THIS LEG, WHATEVER IT RETURNS.** All five prohibitions at `19585b7` are
live and untouched: `do_not_select_passing_subset`, `do_not_construct_C_ML`, `do_not_move_central`,
`do_not_start_leg_2`, `do_not_retry_unchanged`. Leg X is a diagnostic answering *seed-versus-estimator*.
It is **not** a step toward `C_ML`; constructing `C_ML` needs a separate decision from Joseph that he
has not made, and Gate 4's estimator-arm disposition blocks construction independently regardless.

## Authorization, verbatim

Joseph authorized the leg — relayed complete:

> [JOSEPH-VERBATIM] Yes yes to the other B decision

and then decided the readout, in answer to the question Lane B put to him after Leg F's first wave:

> [JOSEPH-VERBATIM] Sure, do iteration 2.

Both relayed by `personal-orchestrator`. **The sequencing was not lifted and is not lifted here: the
floor completes first.** That was Lane B's own argument and it still holds — a 2×2 with one run per cell
has one degree of freedom per effect and no internal error scale, so it has no error scale at all until
the floor supplies one. The launcher enforces this rather than trusting it (see *Execution*).

## Why the readout is restricted to iteration 2 — the restriction is what makes the design sound

**A reader six months from now will see an unreplicated 2×2 and assume nobody noticed. Someone did.**
Leg F's first wave measured the across-process spread at a *single fixed* seed pair `(42,0)`, and it is
not the same size at every iteration. As a fraction of the five-member spread `S_range[k]` (VL127):

| iteration | same-seed `F_range` (`n=3`, provisional) | `S_range` | fraction |
|---|---|---|---|
| 0 | `0.6794325534395745` | `0.7580408493406813` | **89.6%** |
| 1 | `0.1883387264806543` | `0.38136901675657797` | 49.4% |
| 2 | `0.0523993868023519` | `0.3480059774601819` | **15.1%** |

At iteration 0, process variation alone accounts for ~90% of the spread the five members showed. **A
2×2 read at iteration 0 would report seed main effects that are indistinguishable from process noise**,
and would do so with the same apparent precision as a real result — which is the failure mode, not the
absence of one. At iteration 2 the same-seed spread is 15.1%, and iteration 2 is where the Gate-6 band
applies and where Leg F's verdict is defined anyway. So restricting the readout is not a limitation
worked around; **it is the condition under which the 2×2 measures anything at all.**

The corollary, which is the honest half: **nothing here licenses an iteration-0 or iteration-1 claim
from Leg X.** Those values will be computed and persisted by the same trajectory script, and they must
be reported as ineligible for the effect estimates, not quietly omitted.

## The design

Four cells, `estimator_seed × subsample_seed`. **Two already exist and are not retrained.**

| cell | estimator | subsample | source | status |
|---|---|---|---|---|
| A | 42 | 0 | `fullevent_ml_ensemble/member_1`, array `56847059_1` | exists, `v[2] = 0.9806897311812962` |
| B | 46 | 4 | `fullevent_ml_ensemble/member_5`, array `56847059_5` | exists, `v[2] = 0.7534768706675813` |
| C | 42 | 4 | new training | to be run |
| D | 46 | 0 | new training | to be run |

Two new trainings, not four. Everything else in the policy is held at the members' values: `niter=3`,
`epochs=8`, `train_events=2000000`, `batch_size=512`, same input dump, same target, same code digests.

**Why this design and not the diagonal.** The executed member table `(42,0)…(46,4)` moves both seeds
together, so estimator initialization and training subsample are **perfectly confounded** and the
question *"is the trajectory property seed-specific, or a property of the estimator?"* is not merely
unanswered by it — it is unanswerable from it. Adding C and D breaks the confounding with the minimum
possible compute, because A and B are already paid for.

## Fixed rule — the statistic

Read only numeric `end_to_end_achieved_over_required` at **iteration 2**, from each cell's
`STEP1_TRAJECTORY` receipt, exactly as Leg F and the member control did. Write `v[cell]`.

- **Estimator-seed main effect** (the PRIMARY quantity, because it is the estimator-initialization axis
  the question is about):
  `E_est = ½ · [ (v[D] − v[A]) + (v[B] − v[C]) ]`
- **Subsample main effect** (SECONDARY, reported, not verdicted):
  `E_sub = ½ · [ (v[C] − v[A]) + (v[B] − v[D]) ]`
- **Interaction** (SECONDARY, reported, not verdicted):
  `E_int = ½ · [ (v[B] − v[C]) − (v[D] − v[A]) ]`

**Exactly one effect carries a verdict.** Three effects tested at one threshold is three chances to
find something, and this design has no spare power to spend on that. `E_est` is named the primary here,
before any value exists, because it is the axis Joseph's question names.

## Fixed rule — the reference scale, which is the whole reason the floor runs first

Every cell is a single independent draw of the same pipeline, so with `σ` the across-process standard
deviation at iteration 2, `Var(E_est) = ¼(σ² + σ² + σ² + σ²) = σ²`. **Each of the three contrasts above
therefore has standard error exactly `σ`** — the same algebra for all three. `σ` is not available from
inside a 2×2 with one run per cell; it is `F_sd[2]` from Leg F, estimated from **five draws, so 4
degrees of freedom**.

- `σ̂ = F_sd[2]` from the COMPLETED Leg F, `n = 5`, per
  `PREDECLARATION-20260813-gate6-floor-replication.md`.
- **Substituted, not chosen.** The threshold multiplier below is fixed here; `σ̂` is whatever the closed
  floor returns. Lane B will not select the multiplier after seeing `σ̂`, and the floor's own verdict
  will already be committed before this leg is submitted.

## Fixed rule — the threshold and the verdict

**`E_est` is RESOLVED iff `|E_est| ≥ t_{0.975, 4} · σ̂ = 2.7764451051977987 · σ̂`.**

Provenance of the multiplier, so it is clearly not a number invented to fit: it is the two-sided 95%
Student-`t` critical value at **4** degrees of freedom, which is exactly the degrees of freedom `σ̂`
carries as a 5-draw sample standard deviation. A gaussian `1.96` would be wrong here and optimistic; a
round `2` would be both wrong and unmotivated.

Three-way and mutually exclusive:

1. **`ESTIMATOR_INIT_EFFECT_RESOLVED`** — `|E_est| ≥ 2.7764451051977987 · σ̂`. Reading: the iteration-2
   trajectory depends on estimator initialization by more than across-process noise. The property is
   at least partly seed-specific.
2. **`ESTIMATOR_INIT_EFFECT_NOT_RESOLVED_AT_MDE`** — `|E_est| < 2.7764451051977987 · σ̂`. Reading:
   **this design could not have detected an effect smaller than `MDE = 2.7764451051977987 · σ̂`, and
   that number is reported with the verdict.** It is *not* "there is no estimator-seed effect."
3. **`LEG_X_VOID`** — any validity clause below fails, or Leg F did not close with `n = 5` and a
   verdict. No effect is reported at all.

**Pre-registration is not statistical power (BEN-213).** Fixing this rule in advance stops a result
being read favourably; it says nothing about whether the result could have come out otherwise. That is
why branch 2 is named for its sensitivity rather than for a null, and why the MDE is mandatory output
rather than a footnote.

**Illustration only, with the PROVISIONAL `n=3` floor `F_sd[2] = 0.027009496234766995`:** the MDE would
be ≈ `0.075`, against a known A-vs-B iteration-2 difference of `0.2272`. So the design plausibly has
sensitivity to effects of the size already seen. **This is an illustration and not the rule** — the real
`σ̂` comes from the closed floor and will differ.

## A free sensitivity that is NOT a change to the approved design

Cell A is `(42,0)`, which is precisely the policy Leg F replicates. When Leg F closes, **five** values
of cell A exist at zero additional compute, and Leg F's first wave already shows member 1's single
value is not the cell's only plausible value.

- **PRIMARY, exactly as approved: one value per cell.** Cell A is `member_1`'s `0.9806897311812962`.
- **SECONDARY, reported alongside:** the same three effects recomputed with cell A as `v̄(42,0)`, the
  mean of Leg F's five draws (`Var(E) = 0.8σ²`, so `sd = 0.894σ`; the threshold is recomputed
  accordingly and stated).
- **If the two disagree in verdict, that disagreement IS the report**, and no reconciliation is
  attempted here. Joseph approved one run per cell; using replication that already exists for free at
  one cell is offered as a check on the primary, never as a substitute for it.

## Fixed rule — validity, separate from the verdict

Every clause is mandatory. Any failure ⇒ `LEG_X_VOID`; the leg does **not** proceed on the cells that
passed, because selecting a passing subset is the shape `do_not_select_passing_subset` forbids.

0. **Leg F closed with `n = 5`, all five draws valid, and a committed verdict.** Without it there is no
   `σ̂` and no threshold. Enforced by the launcher before any GPU work.
1. Slurm task `COMPLETED 0:0` with a completion marker, for each new cell.
2. `target_provenance` PASS against the canonical receipt, target `544b2f6a…`.
3. The **realized** `seed_policy` read off the produced artifact equals the cell's requested pair with
   `niter=3`, `epochs=8`, `train_events=2000000`, `batch_size=512` — from the artifact, never from the
   launch command.
4. `target.step1_class_ratio == 1.1240802949941018` **exactly**, in every cell including the two that
   already exist. `R` is subsample-invariant, so it must be common; verified for A and B this turn.
5. **`mc_indices` equality by subsample level, not globally.** Cells A and D share `subsample_seed=0`
   and must be array-equal to each other; C and B share `subsample_seed=4` and must be array-equal to
   each other; and the two levels must **differ**. A 2×2 whose subsample axis does not actually move is
   not a 2×2 — this clause is the positive control on the axis the design exists to separate. Measured
   this turn on the two existing cells: **`1,999,982` of `2,000,000` rows differ** between A and B, so
   the axis moves and the control is live rather than nominal.
6. Gate A/B PASS with exact MC-index and truth-normalization identity, and the within-job decomposition
   reproduction gate PASS, for each new cell.
7. Exactly eight `*.weights.h5` in each new cell's own isolated `w_nominal`, and no two cells sharing
   any output path.
8. Execution-environment identity persisted per new cell: host, Slurm ids, GPU identity, both HEADs and
   the executed code digests. Cells A and B predate this requirement and **do not** carry it; that
   asymmetry is recorded rather than waived, and it is one reason the floor — which does carry it — is
   the reference scale rather than the members.

## What this leg does NOT establish, stated so a later reader cannot borrow it

- **It does not license `C_ML`, move the central, start Leg 2, select a subset, or re-verdict any
  Gate-6 member** — including member 3, whose sole failing margin is `+0.001098`.
- **It does not support any claim at iteration 0 or 1.** Those values are computed and persisted; they
  are ineligible for the effect estimates by construction, for the reason given above.
- **It does not calibrate the best-epoch vs `_final` checkpoint-tier gap** (BEN-121). All cells read
  iteration 2 from `_final`, so the comparison is like-for-like and says nothing about that ~1.3%
  systematic. That is Leg 0, which is not authorized.
- **It does not measure `estimator_seed × subsample_seed` interaction with any power.** `E_int` is
  reported at the same standard error as the main effects, from one run per cell; a null interaction
  here is uninformative and must not be quoted as evidence of additivity.
- **A `NOT_RESOLVED` result does not show the trajectory is seed-independent.** It shows this design's
  MDE exceeded the effect, and the MDE is published with it.

## Execution — and the sequencing gate is code, not a promise

`nd-unfolding/pet/sbatch_pet_fullevent_legx_2x2_array.sh`, array tasks `1-2` (cell C then cell D), one
A100 per cell, four stages each: train, Gate A/B, pull/push decomposition, trajectory. Outputs are
cell-scoped under `fullevent_legx_2x2/cell_<est>_<sub>/`; no two tasks share a final path and each takes
a writer lock. Same fail-closed digest tables as Leg F.

**Before the module load and before any GPU work, the launcher refuses to run unless a Leg F result
receipt exists reporting `n = 5`, zero invalid draws, and a terminal `FLOOR_*` verdict.** *"Floor
first"* is Joseph's standing instruction and Lane B's own argument; a rule that depends on an operator
remembering it is a rule that will be forgotten by whichever session inherits this at 03:00. It is
therefore executable, and a test asserts it fires.

**`GATE5_CODE_ROOT` (`/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059`) is not touched** and a
test asserts it never becomes referenced. `/pscratch/sd/j/josephrb/gate6-reconcile-56834281` is read
only. **Gate 5 keeps priority on GPU slots**: this leg submits at `--nice=10000` and self-caps at `%1`,
and it will not be submitted while Leg F's own tasks are queued — `shared_gpu_ss11` is saturated and
queueing Leg X early to gain position would compete with Lane B's own floor and with Gate 5.
