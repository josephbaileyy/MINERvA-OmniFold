# PREDECLARATION — D2 powered closure on the annealed-LR configuration (shape validation)

**Written and committed BEFORE the run.** Authorized by Joseph 2026-08-09/10
(`authorize_annealed_shape_validation`, option b). Purpose: settle whether the annealed learning rate
buys its normalization repair at the cost of shape recovery.

## The risk being tested, stated as a mechanism

The dead LR anneal (`KNOWN_ISSUES`, 2026-08-09) means every fit trains at full `self.LR = 1e-4`.
Restoring the intended anneal (`1e-4` for iteration 0, then `1e-5`) took the fold-forward deficit from
**−34.46% to −1.17%** (arm `warm_fixed_annealed_lr`, job `56534117`). The obvious worry is that it does so
by **under-updating**: a 10× smaller learning rate after iteration 0 moves the classifier less, which
would keep the normalization near its already-good iteration-1 value while failing to transport the
*shape* information that later iterations exist to add. Normalization would improve precisely because
less is happening.

The D2 powered closure measures exactly that. It injects a known truth-level tilt on one half of a
disjoint A/B split and asks how much of the induced spectrum displacement the estimator recovers —
`recovery = 1 − Σ_b|unfolded_b − target_b| / Σ_b|prior_b − target_b|`. It is a **shape** measure, over
cells, and it is insensitive to a pure normalization fix by construction (the criterion's own docstring
records that this is why it was chosen).

## The criterion — ADOPTED, UNCHANGED, NOT TOUCHED

    recovery >= f * ceiling = 0.80 * 0.618228 = 0.494582

This is the CLM-012 criterion adopted 2026-08-09. **No threshold is modified by this run.** The frozen
contract is read, not written.

**Baseline for comparison:** the nominal (warm model / fixed split, full-LR) powered closure measured
**recovery = 0.546853**, margin +0.052271 over the threshold.

## THE READING, FIXED IN ADVANCE

Let `rec_ann` be the annealed configuration's recovery, `rec_base = 0.546853`.

| Outcome | Reading |
|---|---|
| `rec_ann > rec_base + 0.02` | **REAL REPAIR.** The anneal fixes normalization *and* improves shape. Strongest possible result for the arm. |
| `|rec_ann − rec_base| <= 0.02` | **NO INFORMATION on shape.** Normalization repair is not paid for in shape, but shape is not improved either. The arm survives; it is a normalization fix with shape held. |
| `rec_ann < rec_base − 0.02` **and** `rec_ann >= 0.494582` | **TRADE-OFF CONFIRMED. ARM REJECTED** as a repair. It buys normalization with shape, which is the failure mode this run exists to detect. |
| `rec_ann < 0.494582` | **FAILS THE ADOPTED CRITERION OUTRIGHT.** Arm rejected, and more strongly. |

**The ±0.02 band is an ASSUMPTION, not a measurement, and is declared as such.** The powered closure has
never been repeated at fixed configuration, so its run-to-run floor is unmeasured. 0.02 absolute (~3.7%
relative) is a conservative scaling of the ~1.3% GPU floor that BEN-043 measured on the fold-forward
ratio. It is declared now so it cannot be chosen after seeing the number. Per BEN-025, a difference
inside this band **does not** overturn anything.

**A secondary quantity, recorded but NOT decision-bearing:** the closure's own fold-forward deviation
under the anneal. If shape holds and normalization also holds here, that is corroboration; it is not
part of the reading above.

## What this run does NOT authorize — stated because the temptation is real

**A clean shape result does NOT authorize touching `omnifold.py`.** Repairing the anneal in shared engine
code would change **every published number**, including everything Gate-4 was re-issued against on
2026-08-09. That promotion decision is separate, larger, and **Joseph's**. This run produces evidence for
that decision; it does not make it, and no part of this predeclaration should be read as pre-authorizing
it.

Also unchanged by any outcome: **Branch C stays closed** — no product is quoted while any leg is red.

## Governance

- Isolated non-publication namespace: `nd-unfolding/pet/annealed_shape_validation/`
- Every artifact carries `NONQUOTABLE-DIAGNOSTIC` in its filename
- A self-declaring rejection manifest via `pet_diagnostic_quarantine.build_diagnostic_manifest`, whose
  non-quotability is **proven** (recomputed physics, plus the laundered-copy power test), not asserted
- **No engine edit.** The anneal is applied by a `MultiFold` subclass that overrides `CompileModel` at
  fit time only, mirroring the other lane's verified `diagnose_step1_annealed_lr.py`. `omnifold.py` is
  read-only for this run and its sha is recorded.
- **The anneal must be PROVEN to have taken effect**: every fit-time learning rate is read back off the
  optimizer and asserted against the intended `1e-4` (iteration 0) / `1e-5` (iterations > 0) pattern. A
  mismatch is a hard failure, so the run cannot silently report "annealing does not help" when the
  anneal never happened. This is the defect I flagged before the other lane's arm ran and they guarded
  it the same way.
- No promotion, no threshold change, no retry loosening.
- A `wakerctl` watch is armed at submission.

## Provenance of the numbers quoted above

- `rec_base = 0.546853`, threshold `0.494582`, ceiling `0.618228`, `f = 0.80` — `CLM-012`,
  `validate_pet_nominal_gate4.FROZEN["powered_closure"]`
- annealed fold-forward `−1.17%` (push `1.1109012166615733` vs `R = 1.1240802949941018`) — job `56534117`
- baseline fold-forward `−34.46%` (push `0.7367462501305516`) — job `56445883`

---

# AMENDMENT 1 — 2026-08-10, made while `56547490` is still `PENDING` (no result exists)

**Timing matters and is verifiable:** `sacct -j 56547490` reports `PENDING 00:00:00` at the time of writing.
This amendment reorders a reading before any number exists, which is the only condition under which
reordering is legitimate.

## (a) Joseph's correction: the ADOPTED D2 criterion is PRIMARY; the ±0.02 band is SECONDARY

He asked for the D2 powered closure specifically because it is already predeclared, adopted at threshold
`0.494582`, and independently re-derived — and observed that adjudicating this arm with a *fresh* criterion
resting on an *assumed* band would be the setup for instance five of BEN-077's own pattern. That is right,
and it is the sharper version of my own finding turned back on me.

**Clarification of fact, verified rather than asserted:** `56547490` **already runs the D2 powered
closure** — `closure_powered_annealed_lr.py` calls `closure_powered_truth_reweight.main()` directly. No
second job is required. The launcher as submitted also already evaluates the adopted threshold *before* the
band. What was mis-prioritised was **this document**, which led with the band. Corrected:

| Rank | Criterion | Source |
|---|---|---|
| **PRIMARY** | `recovery >= 0.494582` (`= f × ceiling`, `f = 0.80`, ceiling `0.618228`) | CLM-012 as adopted; `FROZEN["powered_closure"]` |
| SECONDARY | `recovery` vs baseline `0.546853`, band ±0.02 | this document's assumption, scaled from BEN-043's ~1.3% GPU floor |

**Both are reported. The PRIMARY decides.** If the two agree, the conclusion is robust to the choice of
criterion. **If they disagree, that disagreement is the finding** and it is reported as such, before any
promotion discussion — Joseph's instruction, and the right one.

`56547490` is **not** cancelled; it is the run.

## (b) A defect found while checking this — the closure carries its OWN copy of the RETIRED bar

`closure_powered_truth_reweight.py:105` hardcodes `RESIDUAL_OVER_GAP_MAX = 0.20`, i.e. `recovery >= 0.80`
— **the bar CLM-012 retired.** So the report's own `recovery_criteria_met` will read **FALSE** even when
the adopted criterion says PASS: the baseline's measured `0.546853` fails `0.80` and passes `0.494582`.

**Disposition — the closure is NOT edited.**

- Changing a threshold in a closure to make a check pass is the prohibited act, whatever the justification.
- It is also unnecessary: the **authoritative** evaluation is `validate_pet_nominal_gate4.check_powered_closure`,
  which reads `P["residual_over_gap_max"]` from `FROZEN` — the adopted value. The closure's flag is a
  self-report, not the gate.
- So the adopted criterion is evaluated **from the closure's raw `metrics.recovery`**, which is what the
  launcher does.

**The risk is misreading, and it is now recorded:** `recovery_criteria_met` in any powered-closure report
is computed against the retired 0.80 and **must not be read as the verdict**. Logged in `KNOWN_ISSUES`.

The irony is instructive and worth keeping: the same file states the principle it violates —
*"Two copies of a default is one of them going stale"* (line 230, about `early_stop`, which it correctly
reads off the engine's signature) — while hardcoding the recovery bar three lines from the top of its
constants block. Knowing a rule is not applying it, which is BEN-075's lesson in a different costume.

---

# AMENDMENT 2 — 2026-08-10. Record correction, and the output made self-declaring

## (a) Correcting the record on the D2 objection — Joseph's side, at his instruction

Joseph's 2026-08-10 objection asserted that `56547490` was **not** the D2 powered closure and that a
separate D2 run was needed. **That assertion was factually wrong** — the job runs
`closure_powered_truth_reweight.main()` via the annealed wrapper, and always did. He asked for the record
to be corrected on his side rather than mine, so it is recorded here plainly rather than absorbed.

**The substance held regardless, and it was the part that mattered:** the adopted criterion belongs in the
PRIMARY position and my ±0.02 assumed band in the SECONDARY — adjudicating this arm on a fresh criterion
resting on an assumed band would have been instance five of BEN-077. Amendment 1 made that change while
`sacct` reported `PENDING 00:00:00`, i.e. before any number existed, which is the only legitimate time to
reorder a reading.

## (b) The line-105 trap is now handled in the OUTPUT, and it reaches this job

`closure_powered_truth_reweight.py:105`'s `RESIDUAL_OVER_GAP_MAX = 0.20` is left alone — editing a
criterion inside a closure is the prohibited act. Instead the **emitted field is relabelled** so it cannot
be read as the verdict, which is labelling an output and breaks no prohibition. Same move as
`publication_gate_rejects_this` and `..._FIRST_LEG_ONLY_NOT_LIKE_FOR_LIKE`.

In `closure_powered_annealed_lr.py`, the annotation now:

- **renames** `recovery_criteria_met` → `recovery_criteria_met_AGAINST_RETIRED_0p80_BAR_NOT_THE_VERDICT`,
  preserving the value;
- adds `recovery_criteria_met_field_note` naming the retired bar, its source line, and the authoritative
  evaluator;
- adds `recovery_vs_adopted_criterion` with `recovery`, `adopted_threshold`, `f`, `ceiling`,
  `threshold_source`, `meets_adopted_criterion`, `margin`, and `is_this_the_verdict` — per the ingredients
  convention, so a reader can recompute the verdict rather than trust it.

**Checked before renaming, not assumed:** `recovery_criteria_met` is read by nothing — it appears only in
test fixtures and comments. `is_powered_closure` **is** read (`validate_pet_nominal_gate4.py:722`) and is
left untouched.

**Why this reaches `56547490` even though it is already submitted:** `sbatch` spools the batch script at
submit time, so editing the launcher would *not* affect this job — but the launcher invokes
`closure_powered_annealed_lr.py` by path, and that file is read when the job runs. The annotation lands.
Joseph's point that a mislabelled artifact is far harder to correct after citation than before existence is
the reason this was done now rather than at result time.

## (c) The engine pin — there was no hole. RETRACTED.

Joseph asked for `omnifold.py` to be pinned into the Gate-4 gate, on the strength of my scoping's claim
that it was not. **The claim was false.** The live gate `...-20260809.json` already pins
`estimator_engine_multifold` → `omnifold_nn/omnifold/omnifold.py` **and** `estimator_engine_net` →
`net.py`. An engine edit breaks the binding and the gate says so, which is the correct behaviour.

I asserted the absence **without running the check** — an earlier grep had looked for the *closure* driver,
found nothing, and I carried that conclusion to the engine. That is the BEN-027 failure exactly: a claim in
a status document not backed by a command run in the same turn, and it caused Joseph to direct a re-issue
that was not needed. A gate adding a redundant second pin on an already-pinned file was written and then
**reverted**; `...-20260809.json` is restored byte-identical from git and remains the single live gate with
17 pins. Retracted in `SCOPING-20260810-engine-rebaseline-cost.md` at the point of claim.

