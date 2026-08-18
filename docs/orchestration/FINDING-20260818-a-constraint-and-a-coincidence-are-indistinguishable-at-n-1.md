# The family validator is scoped to ONE RUN, and nobody could have noticed because there has only ever been one

**Lane E, 2026-08-18. `BEN-419`.** `validate_gate5_training_artifacts.py` is named and used as a
*population* instrument — it loops over 50 members and renders a family verdict. Its expectations include
three constants that name **one campaign run**:

```
:27  ARRAY_JOB_ID = "56857233"
:30  EXPECTED_HEAD = "b82ac63f9c5685c9cc05df059d2bbb4ae42d3258"
:33  EXPECTED_CODE = {replica_driver, nominal_driver_unmodified, loader}   # digests of that run's code
```

and they are load-bearing in five more places: `:176` compares the receipt's array job id to
`ARRAY_JOB_ID`, `:178` the runtime head to `EXPECTED_HEAD`, `:331-332` build the stdout/stderr paths from
the job id, `:338` asserts a log line containing it, `:365` filters `sacct` on it as a prefix, and `:430`
stamps it into the report.

**So the module cannot validate any campaign except `56857233` — a three-stream re-run included.** This
has been true since it was written.

## Why nobody saw it, and this is the finding

Lane D's formulation, which is better than mine:

> **A constraint and a coincidence are indistinguishable at N=1.**

There has only ever been one run of this campaign. Every use of the module was a use against that run, so
*"validates the Gate-5 family"* and *"validates run 56857233"* had identical extensions. Nothing in the code
distinguished them and no observation could have. The mis-scoping became visible only when a second run was
proposed — and then it was visible immediately.

This is the same shape as `BEN-258`'s third category one level up. That one is about a **guard** whose
input has only ever taken one value, so it cannot be known to work. This is about a **claim** whose
population has only ever had one member, so its scope cannot be known to be right.

## The distinguishing property, and it is mechanically usable

Lane C's, and it is the reusable half:

> **A pin naming a CODE STATE is reusable across runs. A pin naming a RUN is not.**

`EXPECTED_HEAD` and `EXPECTED_CODE` look similar and are not: a code-state pin says *"this ran against
these bytes"*, which any future run can also satisfy or fail meaningfully. A run-id pin says *"this is that
job"*, which no future run can satisfy at all. Measured across the tree, **10 modules carry
`EXPECTED_HEAD`/`EXPECTED_CODE`-style code-state pins and all are legitimately reusable.**

So the defect is **a name/scope mismatch, not hardcoding**: a module whose name claims a POPULATION while
its constants name an INSTANCE.

## The mechanical check, and why the obvious version is vacuous

C proposed: *any `*_family_*.py` carrying a run-id literal.* **Measured: the glob matches exactly one
tracked file — a test — and would flag zero. The defect is not in the glob at all**, because the
name-shape claiming a population here is the plural `_artifacts`, not the word `family`. A lexical rule
depends on filename discipline that does not exist.

The rule that fires is structural:

> **a module-level run-id literal used as an EQUALITY OPERAND inside a function that takes a member
> index.**

That separates a mis-scoped population validator from a legitimately single-purpose script. Measured over
tracked `.py`/`.sh`, five modules carry a module-level 7–9 digit run-id string and **only one is a
defect**:

| module | constant | verdict |
|---|---|---|
| `validate_gate5_training_artifacts.py` | `ARRAY_JOB_ID` | **the defect** — population instrument |
| `submit_gate5_extraction_r2_n50.sh` | `PREDECESSOR_JOB` | correct — a `--dependency` operand |
| `run_4d_throws_interactive.sh` | `JID` | correct — interactive one-shot |
| `sbatch_finalize_annealed_shape_validation.sh` | `SOURCE_JOB` | correct — one-shot |
| `state/_audit_gate3_source.py` | `JOB` | correct — one-shot |

**`reconcile_gate5_family.py` carries no run-id pin** — verified by AST, and it is the load-bearing
negative, because it is the other pinned reader in the ruling this arose from.

**A census caveat that cuts both ways.** A relayed count of 3 reached the right *conclusion* over a
population two short (it missed `PREDECESSOR_JOB` and `JID`, both `.sh`). My own sweep over-matched:
`NGLOBAL = 32849103` in `launch_phase7_final.sh` is a **throw count** passed to `bank_uthrow_5d`, not a
job id. **An 8-digit integer is not a type and "job id" is not a lexical category — grep over-matches AND
under-matches, and only reading resolves both.**

## What this does to the delegation question it arose from

The data-only product was going to wrap this validator and delegate to it. The obstacle everyone was
costing was the 55 check sites a data-only artifact cannot reach. **That was never the main obstacle**: the
module is inapplicable to a second run of *anything*, so the wrapper could not have delegated even for a
three-stream re-run.

The consolation is real, though, and it was found by importing rather than reasoning: **the module imports
cleanly and its expectations are module-level, so a replacement can compare against the same OBJECTS.**
Only `required_keys` is function-local. So the reimplementation is **71% of the control flow and 0% of the
constants**, and a drifted expectation cannot hide in the replacement — if the pinned constant moves, the
replacement moves with it.

## The check to steal

- When a module's name claims a population, **read its constants and ask which one they name**. If any
  names an instance, the module's scope is narrower than its name.
- For any invariant you rely on, ask **how many distinct values its population has ever taken**. At one,
  you have not tested the invariant; you have tested a coincidence.
- Prefer **structural** detection rules to lexical ones. A rule that depends on filename discipline
  inherits that discipline's failures, and the vacuity is invisible until you run it against the known
  case — so **always run a proposed detection rule against the defect that motivated it.**

**Cross-references.** `BEN-258` amendment 1 (a live guard never exercised), `BEN-426` (`bootstrap_seed`'s
under-dimensioned encoding, from the same ruling), `BEN-415`/`BEN-416`/`BEN-417` (the denominator family,
same session), `a-claim-about-code-is-dated` (a number true at its own scope, quoted at another).
