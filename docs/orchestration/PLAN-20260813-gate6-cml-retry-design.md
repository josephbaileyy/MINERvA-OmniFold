# Gate 6 (P5B.2, `C_ML`) — retry design after `BLOCK_GATE6_ML_ENSEMBLE`

**For Joseph's decision. Nothing here is executed, and nothing here constructs `C_ML`.**
Written by lane B 2026-08-13 against `19585b7` (merged to `39b0021`). Every number below was
recomputed this turn from the committed receipt or read out of the committed code; the arithmetic
check is reproduced in §2 so it can be contradicted.

Contract: `docs/PUBLICATION_COMPLETION_RUNBOOK.md` §"Packet P5B" item 2 — *no Poisson variation,
predeclared crossed seed design, compare against the P5A floor.* Blocking state:
`docs/orchestration/state/gate6-member-trajectories-result-56847059.json`, VL116–VL121.

All five prohibitions are honoured by every leg below: **no passing subset is selected, no `C_ML` is
constructed, the central does not move, Leg 2 does not start, and no leg is an unchanged retry.**
§4 states, per leg, exactly what changes and why that change addresses the observed failure —
which is what `do_not_retry_unchanged` requires before a retry is authorized.

---

## 1. The two prior questions, and why they come before "which seeds"

`do_not_retry_unchanged` is not satisfied by picking different seeds. Two properties of the
**measurement** have to be settled first, because both are cheaper than a training and both change
which members are actually failing.

### 1a. One of the four failures is smaller than a known systematic inside its own comparison

The metric is read at iterations 0, 1, 2 from checkpoints of **two different provenance tiers**.
`step1_increment_trajectory.py:155-162` (`ckpt`) prefers `..._final.weights.h5` when it exists and
falls back to the best-epoch file; the member inventory asserted by
`sbatch_gate6_member_trajectory_array.sh` is six best-epoch files (iterations 0,1,2 × steps 1,2)
**plus `_final` for iteration 2 only**. So:

| iteration | checkpoint tier actually used |
|---|---|
| 0 | best-epoch |
| 1 | best-epoch |
| 2 | `final` (BEN-043) |

The harness's own docstring bounds that gap: *"BEN-043 measured that gap at ~1.3% on the fold-forward
ratio -- far too small to blur a 1.124-versus-0.65 discrimination, which is why this measurement
survives the caveat. **It would NOT survive it if the question were a few-percent one.**"*

The Gate-6 question is a few-percent one. Per-member step sizes in `|value-1|`:

| member | dev @0,1,2 | step 0→1 (tier-clean) | step 1→2 (**crosses tiers**) | band excess | failure robust? |
|---|---|---:|---:|---:|---|
| 1 (42,0) | 0.519482, 0.124001, 0.019310 | −0.395481 | −0.104691 | −0.080690 | PASS |
| 2 (43,1) | 0.141819, 0.152498, 0.101483 | **+0.010679** | −0.051015 | +0.001483 | **yes** — monotonicity fails at the tier-clean step |
| 3 (44,2) | 0.056478, 0.041552, 0.042650 | −0.014926 | **+0.001098** | −0.057350 | **no** — see below |
| 4 (45,3) | 0.125205, 0.174153, 0.180208 | **+0.048948** | +0.006055 | +0.080208 | **yes** — tier-clean rise *and* band |
| 5 (46,4) | 0.238559, 0.228871, 0.246523 | −0.009688 | +0.017652 | +0.146523 | **yes** — band failure is decisive on its own |

**Member 3 fails Gate 6 on a `+0.001098` rise at the one step that crosses a checkpoint-tier
boundary carrying a measured ~1.3% systematic.** Its verdict is 12× smaller than the known
systematic in the comparison that produced it, and member 3 passes the band with 0.057 to spare.
Members 2, 4 and 5 fail for reasons that survive this: 2 and 4 rise at the tier-clean step, and 5's
band excess is nine times the systematic.

Note this cuts *against* a convenient conclusion as well as for one: it does not rescue members 2, 4
or 5, and it does not change the family verdict by itself, because one surviving failure still
blocks. It changes **how many** real failures there are — 3 not 4 — and that is what the retry has
to explain.

### 1b. The clause is hardest to pass for a member that has converged

`d[m,0] >= d[m,1] >= d[m,2]` has no tolerance. For a member whose metric has reached a stationary
value, the three readings are exchangeable and `P(non-increasing) = 1/6`; requiring it of all five
members gives roughly `(1/6)^5`. The exact number is not the point (real trajectories carry drift,
so the true probability is higher) — **the direction is: the clause penalises stationarity, and
stationarity is what convergence looks like.** Member 1 passes because it is still moving fast, from
0.519 to 0.019; every other member moves by at most 0.049 across the whole trajectory.

Related, and worth Joseph seeing before he judges the band: **the `0.10` band's provenance is a
diagnostic-label cut on a different iteration.** The predeclaration calls it "the existing trajectory
harness band", and the harness's only `0.10` is `step1_increment_trajectory.py:299`, an
`abs(it0[...] - 1.0) <= 0.10` test on **iteration 0** that selects between two *verdict strings*
(`BROKEN_AT_ITER0` vs `RIGHT_SIGN_AT_ITER0_INVERTS_LATER`). It was not derived as a physics tolerance
on the final iteration, and it is not calibrated against any measured floor.

---

## 2. What the metric is, checked rather than described

`end_to_end_achieved_over_required` **is** `mean_w_reco(push_k) / R`, exactly. From
`step1_increment_trajectory.py:236-257`, `required = R/base` and `e2e = m_push/base`, so
`e2e/required = m_push/R` and `base` cancels identically. Verified against all 15 committed values:
`end_to_end_achieved_over_required == 1 + push_dev_vs_R` to a worst deviation of **2.220e-16**, and
`absolute_deviation_from_one == |push_dev_vs_R|` to the same.

Two consequences.

1. **`R` is common to all five members**, so their values are directly comparable.
   `fullevent_fps_dataloader.py` states it at the `STEP1_MC_NORMALIZATION` definition — *"the class
   ratio IS R -- subsample-invariant, because the MC side is renormalized regardless of how many rows
   the `imc` draw took and R is built from the FULL inventory"* — and `step1_class_ratio` takes
   full-inventory sums, not the subsample. With one shared target npz and no bootstrap seed, all five
   members share `R = 1.1240802949941018`. **The five members therefore disagree about the overall
   normalization of the pushed weights by a factor of 1.461867** (finals `0.980690, 1.101483,
   1.042650, 0.819792, 0.753477`), spread `0.227213` in `|dev|` (VL111).
2. **The predeclaration's second witness is the first one again.** It required recording signed
   `push_dev_vs_R` *"so a monotone one-sided drift can be distinguished from two-sided scatter"*.
   Since the signed field is `metric − 1` identically, that instruction is satisfied trivially and
   adds no independent information. The distinction it asks for is real and worth having; it needs a
   different quantity, not this one. (Filed as BEN-122.)

One loose end, cheap to close and stated because it may be nothing: **member 1's iteration-1 value
`1.124000976719287` agrees with `R = 1.1240802949941018` to `7.06e-05` relative**, i.e.
`mean_w_reco(push_1) ≈ R²` to five significant figures. For a single unconstrained pair of numbers
that is roughly a 1-in-10⁴ coincidence, and the mechanism it would indicate — a class-ratio
normalization applied at two iterations instead of being absorbed at one — is checkable from the
committed trajectory JSONs at zero compute. It is an observation, not a claim; no other member shows
it, which is itself evidence against a universal double-application.

---

## 3. OI-15 is stale, and that removes the sequencing dependency

OI-15 reads *"The driver has no estimator-seed override and gate pins constrain edits"* with remedy
*"Add a receipt-bound estimator-seed control at the next authorized re-issue."*

**That control already exists and is already receipt-bound.** `train_fullevent_nominal.py:335-336`
declares `--estimator-seed` and `--subsample-seed` as independent flags;
`sbatch_pet_fullevent_ml_ensemble.sh:111` passes both independently; and lines 114-128 of that
launcher re-read the **realized** `seed_policy` off the persisted artifact and fail closed if it
differs from what was requested — *"the two can differ and only the persisted record is evidence"*.
So no code gate has to be re-issued to vary the seeds, and none of the legs below needs OI-15's
remedy. The half of OI-15 that is still true is the second clause: gate pins do constrain edits, and
§4 respects that.

What is genuinely missing is different and smaller: **the products do not persist their execution
environment**, which the run log already names — *"host/GPU identity was recoverable only from
sidecar markers and logs"*. Since `train_fullevent_nominal.py` is `/files/driver/path` in the live
`p3f-pet-gate4-launch-code-gate-20260813.json`, editing it to add that would force a code-gate
re-issue plus re-attestation of every pin. The shape to copy instead is
`train_fullevent_replica.py:347-353`, which persists `slurm_job_id`, `slurm_array_job_id`,
`slurm_array_task_id`, `host` and `head_at_runtime` — written by a **new launcher into a sidecar
receipt**, which is the precedent `sbatch_pet_fullevent_ml_ensemble.sh:20-26` sets for exactly this
situation.

---

## 4. The design: three legs, strictly ordered

The ordering is forced, not stylistic. Leg X measures two main effects with one degree of freedom
each and **no replication**, so it has no internal error scale; Leg F is what supplies that scale.
Running X before F produces two numbers that cannot be judged. Leg 0 comes first because it is free
and can retire one of the four failures before either training leg is costed.

### Leg 0 — tier calibration. No training. Answers §1a.

Re-run the existing trajectory harness on the **existing five members**, forcing the iteration-2
reading to the best-epoch checkpoint, and compare against the committed `_final` reading. That is
five samples of the tier systematic **measured on the Gate-6 metric itself** rather than imported
from BEN-043's fold-forward ratio.

- **Changes:** a `--checkpoint-tier {auto,best-epoch,final}` control on
  `step1_increment_trajectory.py`, defaulting to `auto` (today's behaviour). That file is **not** in
  the Gate-4 code gate's pin list — verified against
  `p3f-pet-gate4-launch-code-gate-20260813.json`, whose `files` block names 19 distinct paths and
  does not include it — so this is a code change with **no gate re-issue**, only a new launcher pin, because
  the trajectory launcher hardcodes its sha256 (`48f8353d…`).
- **Cost:** inference only. The five completed trajectory tasks ran 13:44–14:00 each; five in
  parallel, well under one wall hour, no training.
- **Reads:** committed checkpoints and the hash-bound archived target `544b2f6a…`. No new artifact
  enters the ensemble.
- **Decides:** whether member 3's FAIL is a measurement artifact. If the measured tier gap on this
  metric exceeds `0.001098`, member 3's monotonicity verdict is not evidence and the family has three
  real failures, not four. **Member 3 is not thereby promoted, selected, or removed** — the family
  still blocks on 2, 4 and 5. This changes the fault description the retry must explain.

### Leg F — the floor, at n=5. Answers the peer's question directly.

Five across-process draws of the **fixed member-1 policy `(42,0)`**: member 1 exists, so four new
trainings, each with execution-environment identity persisted per §3.

This is the control the repo already predeclared. `PREDECLARATION-20260813-gate6-member-trajectories.md`
names it verbatim — *"five total across-process draws of the fixed member-1 policy `(42,0)`, including
four new runs with persisted execution-environment identity"* — but gated it behind *"If all five
pass."* **The design change I am proposing is to invert that precondition, and it is the one thing
here that needs Joseph's explicit sign-off**, because it authorizes work the predeclaration's failing
branch did not license.

The argument for inverting it: the floor is not a reward for passing, it is the scale that makes any
of these numbers interpretable, and the failure is exactly when you need it. Today the comparison
floor is VL112's **within-process** `1.26775e-04`, while the members were trained in five separate
Slurm tasks on five different nodes. The across-process floor is VL113, `1.62987e-02` — **129× larger,
and known from a single pair** (`n=1`, "structural"). The runbook itself only asks for one repeat
(P5A: *"Run one matched GPU-floor repeat before interpreting ensemble spreads"*), so `n=1` is
contract-compliant and still cannot support the inference being asked of it. At `n=1` a floor has
~76% relative uncertainty on its own scale; member 3's total deviation (0.0427) is 2.6× it and
member 1's final (0.0193) is 1.2× it.

- **Changes:** the seed policy is held **fixed** and the process is varied — the opposite axis from
  the blocked run. Not a retry of it: it measures a different quantity (reproducibility at fixed
  policy) on a policy whose member passed.
- **Cost:** 4 trainings. The five Gate-6 members took 02:59:03–03:05:15 each on one A100, `shared`
  QoS, so ≈12 GPU-h, one wall wave under 4 h, plus four ~14 min trajectory tasks. Each job is a
  single job under 12 h.
- **Needs:** a new launcher. `sbatch_pet_fullevent_ml_ensemble.sh` hard-refuses any `MID` outside
  1..5 (*"a sixth member is not authorized"*) and refuses to rerun over a `.done` marker, both
  correctly. Same-policy replicates need their own output namespace and their own file, per that
  launcher's own "why a new launcher" reasoning. **`train_fullevent_nominal.py` is not touched.**
- **Decides — and this is the clean binary.** If the five same-seed draws cluster near member 1's
  −0.019, the trajectory is **seed-determined**: members 4 and 5 are real seed sensitivity, `C_ML`
  would be legitimately large, and the question becomes whether the estimator is publishable with
  that ML uncertainty. If instead the five same-seed draws scatter across anything like the observed
  0.227 range, the trajectory is **not a property of the seed at all** — member 1's PASS was a draw,
  no seed can be expected to meet the band, and the defect is in the P5A nominal's reproducibility,
  not in Gate 6. **Both outcomes are decision-relevant and neither is good news**; they route to
  different owners, which is why this is the first thing to run.

I want to be plain about the status of the framing that motivates this leg. That member 1 is both
the only converged member and the carrier of the adopted nominal's `(42,0)` policy is `n=1`: it is a
**hypothesis this leg tests**, not a finding, and it should not be repeated as more than that.

### Leg X — a 2×2 crossed sub-factorial. Answers "estimator or subsample", and only after F.

The executed design is **diagonal**, not crossed: `(42,0), (43,1), (44,2), (45,3), (46,4)` moves both
seeds together, so estimator initialization and training subsample are perfectly confounded and no
attribution is possible from these five members however they are analysed.

The launcher anticipated this and rejected the alternative on cost —
*"'CROSSED' MEANS FIVE INDEPENDENT MEMBERS, NOT A FACTORIAL SCAN. A factorial of five values on two
axes is 25 members, which is not what N=5 means and is not authorized."* That reasoning is right
about a full 5×5 and the dichotomy it draws is the thing to correct: **a 2×2 on the existing extreme
cells is four members, two of which already exist.** Cross `{42,46} × {0,4}`: `(42,0)` is member 1
(best, −0.019) and `(46,4)` is member 5 (worst, −0.247); the two new cells are `(42,4)` and `(46,0)`.
That asks whether the pass-to-worst-failure difference travels with the estimator seed or with the
subsample, at maximum contrast, for **two trainings — fewer members than the design already run.**

I should also say what the diagonal design is *not* wrong for. For estimating `C_ML` as a covariance,
i.i.d. draws of the whole seed vector are a legitimate estimator of the joint variance, and the
diagonal gives that. Its cost is purely interpretive: it cannot attribute variance to a source. That
attribution is not needed to *build* `C_ML` and is indispensable to explain why the family *failed*.
Different purposes; the launcher's choice was defensible for the first and is inadequate for the
second.

- **Cost:** 2 trainings ≈ 6 GPU-h, one wall wave under 4 h, plus two ~14 min trajectory tasks.
- **Interpretation depends on Leg F** for the error scale, and on Leg F's outcome for whether it is
  worth running at all: if F shows the trajectory is process-determined, Leg X is measuring noise on
  both axes and should be cancelled, not run.

---

## 5. Cost, and what it does not buy

| leg | new trainings | GPU-h | wall | answers |
|---|---:|---:|---:|---|
| 0 — tier calibration | 0 | 0 | <1 h | is member 3's FAIL an artifact |
| F — floor at n=5, fixed (42,0) | 4 | ≈12 | ≈4 h | seed-determined or process-determined |
| X — 2×2 `{42,46}×{0,4}` | 2 | ≈6 | ≈4 h | estimator init vs training subsample |
| **total** | **6** | **≈18** | **3 waves** | |

Every wave is a single job under 12 h. **None of this constructs `C_ML`, and none of it is sufficient
to.** ~~Gate 4's estimator-arm disposition is an independent user decision that blocks construction
regardless of how these legs come out — stated in the predeclaration, the receipt
(`gate4_user_disposition_remains_independent: true`), the ledger and the status file, and repeated
here so nobody reads a green Leg F as an unblock.~~

**STRUCK 2026-08-14 BY ITS OWN AUTHOR — the disposition was already closed when I wrote this, and the
receipt I cited does not say what I made it say.** Measured this turn: the arm was selected
2026-08-13 (`AUTHORIZATION-20260813-gate4-estimator-disposition.md:12`, Joseph verbatim *"Okay do the
annealed"*) and `56563761` was promoted to canonical at `6b68d12`, `2026-08-13T02:52:32Z`
(`state/p3f-pet-gate4-nominal-promotion-56563761.json`, `verdict: PROMOTED`) — **9 h 51 m before this
sentence was committed** (`17dfe94`, 12:54 UTC). And
`gate4_user_disposition_remains_independent: true` is a **scope**-independence field, the only Gate-4
mention in that receipt; *"blocks construction"* is mine, not its. **The conclusion of this section
is unchanged and is now better supported:** none of these legs constructs `C_ML`, because the live
blocker is `family_verdict BLOCK_GATE6_ML_ENSEMBLE` with `passing_members [1]`
(`state/gate6-member-trajectories-result-56847059.json:109-118`) plus two missing inputs —
`combine_cml_bkgsub.py:75` needs a nominal *extraction* product (`extraction_run: false`, and
extraction is unauthorized) and `--expect 12` crossed members against Leg 1's five. `BEN-244`.

## 6. What Joseph is being asked to decide

1. **Invert the predeclaration's precondition** so the `(42,0)` floor replication is licensed by the
   *failing* branch. This is the only item that authorizes work the predeclaration currently forbids;
   everything else is downstream of it.
2. **Leg 0's code change** — a `--checkpoint-tier` flag on a file with no gate pin, plus a new
   launcher pin. Cheap, no re-issue, and it may retire one of the four failures before either
   training leg is costed.
3. **Whether the `0.10` band and the zero-tolerance monotonicity clause are re-derived** before any
   retry, given §1b: the band came from a label cut on a different iteration, and the clause is
   hardest to pass for a converged member. A retry against unchanged clauses can fail for the same
   non-physical reasons.
4. **Sequencing:** run Leg 0 and Leg F, then decide on Leg X from F's outcome — rather than
   authorizing all three now.

Not asked, and deliberately: no member is selected or excluded, no `C_ML` is built, the central does
not move, Leg 2 does not start, and no retired margin is quoted anywhere above.
