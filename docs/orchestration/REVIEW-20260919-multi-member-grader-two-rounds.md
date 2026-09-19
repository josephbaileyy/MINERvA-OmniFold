# REVIEW DISPOSITION — `z_grade`, the multi-member campaign grader, two adversarial rounds

**CLASS:** implementation record. It grades nothing, adopts nothing, authorizes no compute.
**AUTHORITY:** Joseph's `A4` — *"Any change to decision logic, classification or grading that is
committed BEFORE the preregistration, cross-model reviewed (`agy`, "Gemini 3.1 Pro (High)",
`--sandbox`, read-only; check `git status` afterward), and that makes the criteria equally strict
or stricter."* Every change below is strictly stricter; the two places where the direction was
genuinely contested are argued explicitly in §5.

## 0. What was built, and the gap it closes

`z_validator.assess()` had existed for weeks, tested, with **no production caller that could reach
a leg**. `z_build` builds ONE member and passes `{}` statistics, so every production call returned
on the branch-2 validity check before consulting a statistic. `z_statistics` carried `s_agg`,
`s_med` and `s_proj` just as long, unreached. `boundary_readership.py` recorded the fact:
*"`assess` has no caller outside `tests/`."*

`nd-unfolding/z_grade.py` is that caller. It re-measures all nine `Validity` fields from the
members' own bytes, computes the three legs, binds the null to the graded member, and writes a
grading receipt. Supporting plumbing: `z_build` now records each member's **declared estimator-seed
offset**, read from the digest-verified throw source, into the product metadata.

## 1. Round one — 2 BLOCK, 4 MAJOR

| # | finding | disposition |
|---|---|---|
| 1 | **BLOCK** `identities_pass` ran only `gate_symmetry_psd`; §1.3b has more | **ACCEPTED** — widened, see §3 |
| 2 | **BLOCK** the grader passes a forged second member (perturb a copy by `1e-10`) | **ACCEPTED** — see §3 |
| 3 | **MAJOR** `printed_median`'s mask can have the right popcount and the wrong cells | **ACCEPTED** — the mask must now BE `x_cv > 0` |
| 4 | **MAJOR** `r_null` leaked beside a branch-1 verdict and could crash it | **ACCEPTED** — the null is a magnitude and is gated with the rest |
| 5 | **MAJOR** the offset is read blindly from `throw.npz` | **ACCEPTED** — see §3, round two closed it properly |
| 6 | **MINOR** `dropped == 0` is a tautology | **ACCEPTED** — replaced by column/row nonzero structure |
| 7 | **MINOR/NIT** test tautologies; excluding non-receiving destination cells | first fixed; second confirmed **forced**, not a loosening |

## 2. Round two — the fixes themselves reviewed

The second pass was asked one question above all: **which of these fixes are real?** It returned
`EFFECTIVE` on four, `COSMETIC` on two, and `PARTIAL and DECEPTIVE` on one. It was right three
times and overstated once, and the overstatement is recorded as carefully as the hits.

### 2a. `identities_pass` — **the reviewer's demonstration does not hold, and my test was still rigged**

> *"A completely discarded inflation (`g = 1` everywhere) STILL PASSES … The author fixed this by
> writing a rigged test … it sets `g = 0.5`, a deflated member."*

**The first clause is wrong and the second is right, and both are recorded.** Measured:

```
v_uni = [1,2,3], v_blk = [4,9,16]   ->   compute_g gives g = [1,1,1], pinned = none
```

An all-ones `g` is the **legitimate** output of `compute_g` wherever `v_uni <= v_blk`. Refusing it
would be a guard that fires on a correct run. So the domain check is not loosened by accepting it.

**But the test WAS rigged**, exactly as described: it set `g = 0.5` — a deflation — under the name
`test_an_UNINFLATED_member_does_not_pass_the_identities`, and my docstring asserted that the domain
conditions are what catch an uninflated member. **That claim was false.** Fixed by making the test
say what it tests (`test_a_DEFLATED_member_…`), adding
`test_an_ALL_ONES_g_is_ACCEPTED_and_that_is_correct` which measures the `compute_g` fact, and
adding `test_what_ACTUALLY_catches_a_discarded_inflation_is_the_reconstruction_block`.

**And the real limitation is now stated where it belongs:** `g` cannot be re-derived from the
product — `gate_g_reconstruction` needs `v_uni` and `v_blk`, which the product does not carry. What
stands between a discarded inflation and a pass is `z_receipt.validate_reconstruction_ran`, which
refuses a receipt that does not carry the gate's **measured residual inside a stated rtol**. A bare
boolean is refused there for the same reason it would be here.

### 2b. Distinctness — **COSMETIC, and the reviewer was right**

> *"It never verifies these strings against any real upstream file. Edit one character of
> `read_from.sha256` and the grader sees two strings differ."*

Correct. **A digest is evidence only when something re-computes it from the bytes.**
`Member.throw_source_on_disk()` now opens the throw product at the path the member names,
**re-hashes it**, and refuses both an absent file and a disagreement. Distinctness is therefore a
claim about two productions on disk, not about two strings a forger controls. Three tests, both
directions.

### 2c. `s_proj`'s residue — **PARTIAL is right; "deceptive" is not, and the claim was mine to fix**

The repository carries a deliberate tripwire,
`test_z_build_path.py::test_s_proj_has_no_UNSANCTIONED_caller`, armed for the moment `s_proj`
acquires a production caller. **`z_grade` fired it.** Its own message names the remedy: *"the guard
must move INTO `z_statistics.s_proj` — or this caller must route through `evaluate_a7`."*

Routing through `evaluate_a7` is **not available**: it returns `KAPPA_UNDECLARED`, so the cause-3
`s_proj` leg would be permanently unevaluable rather than guarded, and inventing `kappa` is
forbidden (Joseph, 2026-09-11).

So the guard moved: `z_statistics._require_baseline_is_resolvable`, called from `s_proj`, refusing
any functional whose `q = u'Cu` does not exceed the float64 round-off bound of computing it,
`gamma_{n+2} * (|u|'|C||u|)`. **Threshold-free** — its only inputs are machine epsilon and the
dimension — and **scale-invariant**, which the reviewer independently verified and which matters
because Z's covariances live at `~1e-38`.

> **The reviewer's substantive point stands: this closes the ROUND-OFF half, not the `kappa`
> half.** My docstrings said "the residue is CLOSED". That over-claimed and is corrected in all
> three places. What is added instead of a claim: `z_grade` now **measures and records every
> functional's Rayleigh quotient** `q_i / (||u_i||^2 * lambda_max(C_0))`, so a `kappa` declared
> later applies to a completed campaign without re-running it, and
> `test_the_kappa_HALF_of_the_residue_is_still_open_and_says_so` **demonstrates** the open half
> rather than describing it.

*"Deceptive" is rejected as a characterisation of the test inversion.* The inverted test asserts
exactly what it is named for and what it measures. The defect was in the surrounding **scope
claim**, which is a different thing and is what has been fixed.

### 2d. Preregistration bypass — **right, and it is a defect I had already quoted**

> *"`--preregistration` is granted a `default=None`. Drop the flag and every predeclaration check
> is skipped. Ironically, the author criticized this exact anti-pattern at
> `z_build_path.py:1109` — 'Suppression by omission needs no positive act, so it is EASIER than a
> flag' — yet committed it here."*

**Accepted without qualification.** The flag is now `required=True`. Two tests: the CLI refuses to
run without one, and a source assertion that the default cannot come back.

### 2e. `footing_ok` folds in code identity — **KEPT, with the reason recorded at the line**

The objection is that footing is the mathematical problem definition and code identity is revision
history. The alternative is worse in the direction that matters: members built by different code
are **not comparable**, so the campaign is inconclusive, and branch 1 is the only branch that
reports an inconclusive campaign *without a magnitude*. Branch 2 would call a builder mismatch a
VACUOUS BASELINE — the mischaracterisation `R7` corrected elsewhere this week. The reporting
concern is answered by naming it: `validity_evidence.code_identity` is its own block and
`footing.code_identity_agrees` says which sub-condition failed.

### 2f. `per_bin_movement` — the inconsistency was real

`printed_median` got the mask identity and `per_bin_movement` did not, so a spoofed mask would have
reported the movement **in the wrong grid bin**. It now takes `x_cv` and requires the same identity;
the production caller always supplies it, asserted by test.

### 2g. Confirmed EFFECTIVE by the second pass

`r_null` no longer leaks and `null_within=False` is correct when unmeasured; only `ZContractError`
is caught in the identity loop so a `MemoryError` crashes rather than reading as a failed identity;
the projection structure checks are non-vacuous and correct for a marginalization map.

## 3. What the grader refuses, in one list

- **fewer than two members** — R9, before any array is read
- **a member with no `member_identity`** — a product that cannot say which member it is
- **a member whose throw source is absent, or whose recorded digest does not re-hash**
- **a null file that is not the graded member's** — bound by sha256, by reproducing the receipt's
  `r_null`, and by mask equality
- **a `--declared-K`, graded offset or builder revision that disagrees with the preregistration**
- **any validity failure** — and then it reports **no magnitude at all**, statistics and null alike

## 4. Verification

- `tests/test_z_grade.py`: **64 tests**, every branch of `assess()` reached from real products
  built by the real `z_build`, both directions on every refusal.
- Whole-suite regression measured against `c88cb834`, no new failure.
- Reviewer wrote nothing: `HEAD` identical across both rounds; the tracked-modification set is
  exactly the files this change touches.
- ⚠ Same deviation as before, stated: headless mode needs `--dangerously-skip-permissions` in
  addition to `--sandbox`.

## 5. Where the direction was contested, and how it was resolved

Joseph's decision rule: *"if resolving it means doing MORE work, spending MORE compute within A1,
or applying a STRICTER standard, you are authorized. If resolving it would make passing EASIER,
cheaper, or more likely, STOP."*

1. **Fixing `printed_median`'s operand bug makes `s_med` computable at all**, which is trivially
   "more likely to pass" in the sense that a crash cannot pass. Judged **not** the rule's target:
   the bound is untouched at `5%`, the statistic is now the one the specification names, and the
   alternative is a criterion that cannot be evaluated on any real product. Recorded here so the
   call is visible.
2. **The `kappa` half of the residue cannot be closed**, and the two available routes both make
   the leg unevaluable rather than stricter. Resolved by closing what can be closed, recording the
   operand a later `kappa` would need, and carrying the rest as a **disclosed limitation**.

**Co-Authored-By: Claude Opus 5 (1M context)**
