# OUTCOME — **(C) BLOCKED**. Steps 1–3 complete; PASS needs a member campaign that exceeds the cap

**Everything independent of the blocker is finished**, as (C) requires. What remains is blocked
**twice over**, and the second reason is unambiguous.

## Why PASS is unreachable — read from `z_validator.assess()`, not from docs

`scientific_acceptance = PASSING` requires `is_met` = `assessable and branch == 3`. Branch 3 requires
**both**:

| requirement | needs |
|---|---|
| `branch2_failures()` empty — `offsets_match_K`, `offset_declared_nonzero`, `product_digests_distinct`, `all_members_finite` | **≥ 2 members with distinct estimator-seed offsets** |
| all three leg statistics supplied and within boundary — `s_agg`, `s_med`, `s_proj` | **≥ 2 members** (each measures movement *across* members) |

A single build satisfies neither. `assess()` returns **branch 2, "INCONCLUSIVE / VACUOUS BASELINE
VARIATION"** — a genuine computed verdict, and never MET. That is not a defect: branch 2's own
docstring says a zero spread is evidence the knob never reached the estimator and **must never read
as MET**.

## Blocker 1 — the compute cap. **This one is decisive.**

The minimum additional production is **one further member**. Its enforced reservation is on record:
**`158.25` GPU / `262.00` CPU task-hours** (`AUTHORIZATION-20260918` §2 ruling 2).

> **`262.00` CPU task-hours against a **`100`** CPU task-hour cap — 2.6× over.** The goal says stop
> with (C) if the projection exceeds the cap. It does, before any GPU is counted.

## Blocker 2 — a reserved decision

Ruling 2 **declined** `k₁` and released that reservation, *"not to be re-proposed as part of the
required path."* Step 5's *"whatever production runs cause 3 and the null require"* could be read as
reopening it — cause 3 does require members — but **R1–R5 do not say so**, and R1 says *"change no
declared boundary or criterion value,"* which the leg set and the branch-2 validity fields are.
**The cap settles it either way**, so this is recorded rather than argued.

## What I did NOT do, and why

**No production run was submitted.** A single-member build is affordable (~0.3 CPU task-h) and would
demonstrate the computed path on real data — but it **cannot** produce (A) or (B): its branch is
foreseeably 2, which is neither PASS nor an assessable FAIL. It would also **freeze** the builder's
decision logic, `S` and `ε` under the hard rule, in exchange for a result known in advance. Spending
the one production slot on that is not a result; it is a receipt for a foregone conclusion.

**No preregistration (step 4).** It exists to precede a production submission. There is none.

## Compute spent on this goal: **zero task-hours**

Steps 1–3 and the ε declaration were entirely local: code, tests, a read-only cross-model review, and
measurements from already-persisted operands.

## What would unblock it — one decision, not more work

**Authorize the member campaign and raise the cap to cover it** (≥ 262 CPU + 158.25 GPU task-hours
for one additional member), **or** rule that cause 3's legs may be assessed on a basis that a single
member can satisfy — which would be a criterion change and is yours.

**Everything else is staged.** Acceptance is computed, `ε` is declared, the withheld set is empty,
and the first member already exists as `z-cv.npz`.
