# REVIEW DISPOSITION — R7, `all_members_finite` is a footing failure

**THE RULING.** Joseph, 2026-09-19, verbatim:

> **R7** `all_members_finite`: a non-finite member is a footing failure (reject), not branch 2. Fix
> it test-first, get it cross-model reviewed (`agy`, *"Gemini 3.1 Pro (High)"*, `--sandbox`,
> read-only; check `git status` afterward), and commit it **BEFORE** the preregistration.

**CLASS:** implementation record. It grades nothing, adopts nothing, and authorizes no compute.

## 0. What was wrong, and why it had never bitten

`z_validator.Validity.branch2_failures()` listed `all_members_finite`. Branch 2 is **INCONCLUSIVE /
VACUOUS BASELINE VARIATION**, whose entire content is a **zero-spread** diagnosis: *the
estimator-seed knob never reached the estimator.* A `NaN`/`inf` in a member product is the opposite
failure — the arithmetic moved and then exploded — so branch 2 sent a reader to the seed-offset
plumbing to explain a numerical blow-up.

**It was unobservable while every build had one member**, because the other three branch-2 fields
are `False` for a single member and the branch was 2 either way. It first bites on the ≥ 2-member
campaign — which is exactly the run in which it would be read.

## 1. The fix, in three parts

| # | change | where |
|---|---|---|
| 1 | `all_members_finite` moves from `branch2_failures()` to `branch1_failures()` | `nd-unfolding/z_validator.py` |
| 2 | the builder **MEASURES** it instead of hardcoding `False`; the argument is **required, no default** | `nd-unfolding/z_build.py` |
| 3 | `SPEC` §3.7b's branch clauses corrected **inline, where the error is** (rev. 22 stays frozen) | `docs/orchestration/SPEC-20260906-…md` |

**Part 2 is not optional and the ruling implies it.** `build_validity` hardcoded
`all_members_finite=False` under the note *"member-campaign property: requires >= 2 members"*. That
note was already wrong — finiteness of a product is a per-member property, evaluable with one
member — and once the field became a **branch-1** field, a constant `False` would have reported
WRONG FOOTING on **every build forever** and put branch 3 out of reach by construction. Moving the
field without measuring it would have converted a ruling into a permanent block.

**The verdict computation moved below the assembly loop** so it has arrays to measure, and still
precedes the first `path.open("xb")`. The loop was split; nothing between the old and new positions
writes to disk.

## 2. Test-first, as ordered

Written before the fix: **8 tests** in `tests/test_z_validator.py`, **7** in
`tests/test_z_build_computed_acceptance.py`. Red-then-green was **measured, not assumed** — the
first run was `6 failed, 2 passed`, and the 2 that passed are the controls that must hold in *both*
directions (a vacuous baseline is still branch 2; it still cannot reach MET). On the builder side,
`10 failed, 10 passed`. After the fix: **193 passed, 2 skipped** across the three z suites.

**Whole-suite regression, measured both ways:** my tree `18 failed / 3332 passed`; **17 of the 18
fail identically at `62f89e04`**, and the eighteenth
(`test_pet_fullevent_nominal_launcher.py::DriverConfigGate::test_config_gate_only_cli_no_train`)
passes when run alone on my tree and is order-dependent, not mine. The one collection error
(`test_z_build.py`, `ROOT.__spec__ is None`) reproduces at `62f89e04` and that file passes
`22 passed, 2 skipped` on its own. **This change introduces no new failure.**

## 3. The cross-model review

Reviewer: **`agy`, "Gemini 3.1 Pro (High)", `--sandbox`, read-only**, different model family.

⚠ **Same deviation as the previous round, stated again:** headless mode cannot prompt for the
command permission, so the run needed `--dangerously-skip-permissions` **in addition to**
`--sandbox`.

**Verified it wrote nothing, three ways:** `HEAD` identical (`62f89e04` before and after); the
tracked and untracked `git status` sets identical; and the two files I did **not** touch afterwards
(`z_validator.py`, `tests/test_z_validator.py`) are **byte-identical** to the pre-review snapshot of
their diff — 8014 bytes both times.

**Result: NO BLOCK and NO MAJOR findings.** Three MINORs, three NITs. Dispositions are mine.

### 3.1 MINOR — the measured population is `expected`, not `parts`/`operands` → **ACCEPTED, and the claim is now MEASURED**

> *"Non-finite values in those upstream arrays do not result in a WRONG FOOTING verdict; instead,
> they fatally crash the build."*

**Correct, and the crash is the stronger behaviour, not the weaker one** — no product and no
receipt are produced at all. But "it fails closed" was an argument, not evidence, so it is now a
test: `gate_symmetry_psd` is asserted to raise `ZContractError` on both a `NaN` and an `inf`
component block. The case that *would* be a defect is a non-finite operand that **silently passes**,
and that is what the test excludes. The population stays `expected` deliberately: those are the
arrays the member *is*.

### 3.2 NIT — an empty array clears `np.all(np.isfinite(...))` → **FIXED**

The reviewer noted emptiness is blocked upstream by `n > 0`, which is why this is a NIT. Fixed
anyway, in one clause: the predicate is now `size > 0 and np.all(np.isfinite(...))`. **A finiteness
claim over zero elements is not a finiteness claim**, and relying on a distant guard for that is the
shape this campaign keeps paying for.

### 3.3 MINOR — the source-scanning regression test is whitespace-evadable → **FIXED**

> *"`all_members_finite = False` (with spaces) … successfully subverts the test while fully
> re-introducing the bug."*

**Right, and a regression test one space defeats is not one.** It now matches
`all_members_finite\s*=\s*(False|True)` and, separately, the dict-literal spelling
`"all_members_finite": False`.

### 3.4 MINOR — leaving *"missing"* in branch 2 half-fixes the error → **ACCEPTED; THE SPEC EDIT WAS WRONG AND IS REDONE**

My first correction split the conjunct *"any member is missing or non-finite"*, moving only the
non-finite half, on the reasoning that R7's letter reaches no further.

> **That version was wrong about the code, and the reviewer's objection is sound for a second
> reason he did not need.** Both halves are implemented by **one boolean** — an absent member cannot
> be finite — so moving the field moved both, and a SPEC that kept *missing* in branch 2 described
> behaviour no code has. Splitting them for real needs a **second `Validity` field**, which is a
> criterion change and **Joseph's to make**. The SPEC now says what the code does, and the fact that
> this is **one step beyond the ruling's letter is stated in the SPEC itself and routed to Joseph**
> rather than absorbed.

His independent reason is also recorded there: a missing member is *"a structural or pipeline
crash"*, and branch 2 would tell a reader the arithmetic succeeded and produced identical data when
in fact a job never ran.

### 3.5 NIT — `all_members_finite` sits visually among the branch-2 dataclass fields → **NOT ACTED ON, defended in place**

Reordering a dataclass silently repoints every positional construction. The comment at the field
says it grades as branch 1 and why the order is left alone. The reviewer acknowledged the defence.

### 3.6 What the review CONFIRMED

- **The move is exclusive.** Nothing else is reclassified; branch 2 drops to three entries cleanly.
- **The "unreachable branch 3" claim is true**, verified against `assess()`'s `if v1 or invalid:`
  short-circuit rather than taken from my docstring.
- **Both relocation invariants hold:** no byte reaches disk before the verdict, and the single
  `_token` is the one stamped into both variants' metadata.
- **`np.isfinite` is correct on `int64`** (`hRowIndex5D`).

## 4. What this record does not do

It does not grade a candidate, does not preregister anything, and does not authorize compute. The
preregistration is the **next** step in the order Joseph set, and R7 is committed **before** it, as
ruled.
