# DECISION 2026-09-19 — Joseph reverses `AUTHORIZATION-20260918` §2 ruling 2 (`k₁` decline)

**CITABLE FOR:** the authorization of **exactly one** additional cause-3 member, at the stated
reservation, for the computed-acceptance goal only.
**NOT CITABLE FOR:** any second member, any other campaign, a gate movement, an adoption, or a
standing relaxation of the `k₁` decline outside this goal. Gate 2 remains **FAIL**; no scalar-5D
covariance is adopted.

## 1. The ruling, in Joseph's own words

> **R6** I reverse `AUTHORIZATION-20260918` §2 ruling 2 **for this goal only**. The premise *"nothing
> required needs `N`"* no longer holds: computed acceptance requires **≥ 2 members for branch 3**.
> Authorized: **exactly ONE additional member** with a **distinct, declared, nonzero estimator-seed
> offset**, at the priced reservation of **262.00 CPU / 158.25 GPU task-hours**, admitted through the
> **normal campaign check**. Record this reversal as superseding ruling 2, citing this goal.

Accompanying rulings from the same message, recorded because they bound what this authorization may
be used for:

- **R9** — *"Cause 3 is NOT to be assessed on a one-member basis."*
- **R8** — only a product whose production **follows the preregistration commit** may be graded PASS
  or put forward for adoption, and **its** `r_null` must be measured in its own production.
- **Compute cap:** **280 CPU + 165 GPU task-hours in total.** An infrastructure failure may be
  resubmitted identically within the cap.

## 2. What it supersedes, and what the reversal turns on

`AUTHORIZATION-20260918-d-resource-required-deliverable-path.md` §2 ruling 2 declined `k₁` and
released the reservation, on the ground that *"nothing required needs `N`, and `N` is what that
campaign buys."*

**That premise was true when it was written and is now false, and the thing that changed is in this
repository, not in the physics.** On 2026-09-19 `scientific_acceptance` stopped being a hardcoded
literal and became a value computed by `z_validator.assess()` (`ad2af264`, R1). `PASSING` requires
`is_met` — `assessable and branch == 3` — and branch 3 requires `branch2_failures()` to be empty
**and** all three cause-3 leg statistics (`s_agg`, `s_med`, `s_proj`) to be computable. Every one of
those needs **two or more members with distinct estimator-seed offsets**. So the required deliverable
does now need `N`, at `N = 2`.

Ruling 2's own sentence — *"not to be re-proposed as part of the required path"* — is what makes this
a **reversal by the decider** rather than a re-proposal by this lane.

The superseded ruling and its §6 release are annotated **inline in the authorization itself**, with
their original text left intact, per the rev.-22 freeze convention: *corrections go inline where the
error is.*

## 3. Scope, stated narrowly so it cannot be inherited

| | |
|---|---|
| how many members | **exactly one** additional |
| what it must carry | a **distinct, declared, nonzero** estimator-seed offset |
| reservation | **262.00 CPU / 158.25 GPU** task-hours, priced as **enforced cap × tasks** |
| admission | the **normal campaign check** (`lib_r5_admission.sh` / `r5_meter.py`), re-measured immediately before submission |
| total cap for the goal | **280 CPU + 165 GPU** task-hours |
| lifetime | **this goal only.** Outside it, ruling 2 stands as written |
| what it does NOT authorize | a second additional member; re-running the `k = 0` anchor; any estimator pinning (ruling 8 stays reserved); adoption; any outward-facing act |

## 4. ⚠ IT WAS NOT SUBMITTED, AND ONE MEMBER TURNS OUT NOT TO BE ENOUGH

Recorded here rather than only in the outcome file, because a reader who finds this authorization
first must not conclude that the campaign is merely pending.

**Measured before admission:** neither existing `k = 0` object can serve as the anchor of a gradable
two-member campaign, and they fail for **two different reasons**, so no single existing member has
both properties the anchor needs. The census is
[`EVIDENCE-20260919-cause3-member-eligibility-census.md`](EVIDENCE-20260919-cause3-member-eligibility-census.md);
the disposition is
[`OUTCOME-20260919-cause3-anchor-has-no-eligible-member.md`](OUTCOME-20260919-cause3-anchor-has-no-eligible-member.md).

Making the anchor eligible requires re-running the `k = 0` member under current code — **a second
additional member**, which this authorization does not grant and which the cap does not cover
(`524.00` CPU / `316.50` GPU against `280` / `165`). **Nothing was submitted; zero task-hours were
spent.**

**Co-Authored-By: Claude Opus 5 (1M context)**
