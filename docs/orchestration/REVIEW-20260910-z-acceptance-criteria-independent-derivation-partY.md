# PART Y — cause-3 amendment Part A at `f00e4bee`: BLOCK on one line — the interception point is optional

**Owner:** independent-assessment lane. **Subject:** `f00e4bee`. **Supersedes:** Part X's assessment of
`1b7db825`, which does not carry forward. **No grade assigned.** Consequential only.

## VERDICT

> **BLOCK — one consequential issue, and the fix is one line.** The clause's **content, destination and
> derivation are all correct**, and it **does** travel on refused outcomes — verified by execution. But
> **`evaluate_a7`'s `build_path` is keyword-optional with a `None` default**, so the default call grades
> with **no narrowing at all**. The discipline it cites was copied at the function level and broken at
> the signature level.
>
> Part X's two issues are **both discharged**, and the designer improved on the destination I offered.

---

## Y.1 — THE BLOCK: THE NARROWING IS DERIVED AND UNSUPPRESSIBLE — *GIVEN* A BUILD PATH

`conditional_scope_statement(path: BuildPath) -> Optional[str]` (`:726-737`) is sound: one parameter,
derived from `path.blocks_are_shared`, no assert-or-suppress channel. **That much verifies.**

**But the interception point is optional.** `:753` —

    def evaluate_a7(cov_by_offset, projection_M, *, declared_K, c_scale, kappa, build_path=None, …)

and `:25` of the body —

    scope = conditional_scope_statement(build_path) if build_path is not None else None

**Measured by execution:** `evaluate_a7({0: I, 1: 1.01·I}, I, declared_K=(0,1), c_scale=1.0,
kappa=1e-12)` — the default call, no `build_path` — returns **`state=GRADED`,
`scope_statement=None`.**

**The cited model does not have this property, and that is the whole of the difference.**
`z_validator.assess(leg_set: LegSet, statistics: dict, validity: Validity)` (`:217`) takes `leg_set`
**positionally and required**; `:224` derives `correlation_leg_present = leg_set.sees_correlations`.
**There is no way to call `assess` without a leg set**, which is exactly why `sees_correlations` cannot
be bypassed. `build_path` is keyword with a `None` default, so the analogy holds inside
`conditional_scope_statement` and fails at the call site.

**A second, narrower reachability of the same gap**, also measured: a **non-member** build path is
accepted alongside a **multi-offset** `declared_K` and grades with `scope_statement=None` —

    build_path.is_member = False   declared_K = (0, 1)   ->   state=GRADED, scope_statement=None

A non-member run produces **one** covariance; two offsets require member runs. So those two
declarations are inconsistent, nothing checks the pair, and the result grades unnarrowed.

**This is the third instance of one shape in this module's history**, and naming it is more useful
than the instance: Part U — a population selected by a line window; Part V — a coverage flag absent on
one branch, `.get` → `False`; and now a scope statement absent by default. **Each time the thing
exists, is correct, and the path that matters does not reach it.** The fix is one line — make
`build_path` required, or refuse when it is `None` and `len(declared_K) > 1` — **and which is not
mine to choose.**

## Y.2 — DISCHARGED, AND THE DESIGNER IMPROVED ON WHAT I OFFERED

**Part X §X.1 is discharged, and better than I proposed.** I listed `_DIAGONAL_ONLY_SCOPE` as one of
three available hosts. **The designer rejected it, correctly**: `z_validator.py:237/276/282` all key
the statement on `correlation_leg_present`, which is **orthogonal to block sharing** — so the clause
would have appeared when no correlation leg was declared and vanished when one was. **The wrong
trigger entirely, and I would have accepted a worse destination than the one built.** Deriving from
**block source** is right, because block sharing is precisely what makes the test conditional.

**And it travels on refusals, which I verified by execution rather than by reading** — "returned on
every outcome" was the claim, and the claim is true:

| A-7 outcome | `s_proj` | `scope_statement` |
|---|---|---|
| `GRADED` | value | present, non-`None` |
| `DEGENERATE_FUNCTIONAL` (routed to branch 1, *INCONCLUSIVE / WRONG FOOTING*) | `None` | **present, non-`None`** |

The three return sites (`:75-76`, `:84-85`, `:88-90`) all carry `scope`, computed at `:25` **before**
any guard. The `require(...)` paths raise rather than return, so they carry no scope — **and that is
correct**: a raise is not an outcome, so there is no result to mis-license.

**Part X §X.2 is discharged.** The frame is withdrawn, the dates are verified independently, and the
ask is now a **narrowing of the declared subject** — a contract change, the designer's to argue, with
§A.6's pricing as the argument. The `git log -S` caveat it attaches is the right one and is in my own
notes.

**And `W5` is tightened on the inertness I identified**: `cause3_agg` and `cause3_med` force
non-passing; **`cause3_corr` forces nothing.** *"All three"* implied a guard that is not there.

## Y.3 — SUITES, CONTROL FIRST

| suite | result |
|---|---|
| `test_z_validator` **[control]** | **136 passed** |
| `test_z_build_path` | **80 passed**, no skips |
| `test_z_contract` | **56 passed, 1 skipped** — the pre-existing lightgbm skip |

Matches the relayed figures.

## Y.4 — NOT ASSESSED

- **Part B / `κ`** — the reviewer's, whole. Its value is withdrawn; `B.1`, `B.3`'s floor and `B.4` stand.
- **`ec5f0b99`**, **`6d959ab3`** — frozen, reviewer's.
- **`S2`** — still held.
- **The 80 tests' power** — the reviewer's; I verified they run and pass. The eight new scope tests
  include a power arm per the relay, which I have not independently confirmed.
- **Still open:** `A-6(a)`, `A-6(b)`, the excluded producing execution, the three-or-four block
  population.
