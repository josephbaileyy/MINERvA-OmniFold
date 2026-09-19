# REVIEW DISPOSITION — steps 1–2, independent cross-model review

**Step 3.** Reviewer: `agy`, **Gemini 3.1 Pro (High)**, `--sandbox`, read-only, different model
family. **Verified it wrote nothing:** `HEAD` unchanged across the review and `git status` clean of
tracked modifications, checked before and after.

⚠ **One deviation from the route, stated:** headless mode cannot prompt for the command permission,
so the run needed `--dangerously-skip-permissions` **in addition to** `--sandbox`. The sandbox's
terminal restriction stayed on and the before/after `HEAD` + `git status` check is what actually
establishes it wrote nothing — which is why the route asks for that check.

**Result: NO BLOCK findings.** One MINOR, three NITs. Dispositions below are mine.

## 1. MINOR — `all_members_finite` sits in branch 2; it is a footing failure

**Reviewer's point:** `z_validator.py`'s `branch2_failures()` includes `all_members_finite`, but
branch 2 means *vacuous baseline variation* (zero spread). `NaN`/`inf` in a member is a numerical
footing failure, which is branch 1. Placing it in branch 2 mischaracterises a numerical explosion as
a lack of spread.

> **DISPOSITION: CORRECT, AND DELIBERATELY NOT ACTED ON. Routed to Joseph.**
> Two reasons, neither of them disagreement. It lives in `z_validator.py`, and **R1 scopes me to
> `z_build.py` and says "change no declared boundary or criterion value"** — moving a validity field
> between branches reclassifies a criterion. And it **changes no current outcome**: the other three
> branch-2 fields are `False` for any single-member build, so the branch is 2 either way. It would
> matter for a **multi-member** run with a non-finite member, where it would report "vacuous spread"
> instead of "wrong footing".

## 2. NIT — `cv_held_fixed`'s justification was overstated → **FIXED by making it true**

**Reviewer's point:** the comment claimed `reconstruct_null_ratio` establishes that `x_cv` and
`x_cv2` come from the same persisted CV. **It does not** — it compares whatever arrays it was
handed. The genuine cross-check, `x1 == central`, existed but was recorded **passively** in
`declared_cv_crosscheck` and **gated nothing**.

> **DISPOSITION: ACCEPTED, AND FIXED IN THE DIRECTION THAT REMOVES THE CLAIM RATHER THAN SOFTENS
> IT.** `cv_held_fixed` now gates on `np.array_equal(x1, central)` — the check the comment always
> cited. Tests both directions, including that a failed cross-check lands on **branch 1**, a footing
> failure, not branch 2. This is the same defect class this campaign has been counting: a field
> whose comment names evidence the code never consulted.

## 3. NIT — `digests_agree` was bound to matrix-maths gates → **FIXED**

**Reviewer's point:** `digests_agree=gates_ran` derived a digest boolean from band-partition and
symmetry gates. True that reaching the line implies hashes verified, but the binding is tangled.

> **DISPOSITION: ACCEPTED AND FIXED.** It now rests on `manifest_stamp`, an actual digest artifact
> in scope. Test asserts it is `False` when no stamp is present.

## 4. NIT — `_invalid_statistics` docstring too narrow for `s_proj`

**Reviewer's point:** it says every statistic is a relative change `|a−b|/b`; `s_proj` is a maximum
over `√(uᵀCu)` functionals. The **domain check is correct**; only the explanatory text overreaches.

> **DISPOSITION: CORRECT, NOT ACTED ON.** Documentation in `z_validator.py`, outside R1's scope, and
> changing it alters nothing executable. Recorded for the gated cleanup.

## What the review CONFIRMED, which is the part that mattered most

- **An empty `statistics` dict never lets a leg silently pass.** It either short-circuits on branch 2
  before any statistic is consulted, or — if a caller ever supplied fully-passing validity — **raises**
  `"A missing statistic is not a passing leg."` It cannot produce MET.
- **`acceptance_token()` is right** that a MET outcome with an out-of-bound null must be
  `NON-PASSING`: `assess_null` returns `aborts: True`, and downstream legs cannot rescue an aborted run.
- **The `n = 2` margin argument is sound** — it disclaims statistical confidence and rests on scale,
  which is legitimate for floating-point non-associativity on identical pinned inputs.
