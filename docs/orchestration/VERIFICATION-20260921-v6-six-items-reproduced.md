# VERIFICATION 2026-09-21 — `V6`'s six unreproduced items, reproduced; `L7` closes, with two corrections

**CITABLE FOR:** the reproduction of six named values, the commands and artifacts they came from,
and the two claims that did **not** reproduce as stated.
**NOT CITABLE FOR:** any grade, any adoption, or any re-opening of clause (c). Nothing here changes
a disposition; it supplies the measurement `L7` said was missing.

Closes limitation **`L7`** of
[`REPORT-20260920-scalar5d-uncertainty-completion.md`](REPORT-20260920-scalar5d-uncertainty-completion.md):
*"`V6`'s six items have no second-lane reproduction."*

---

## 0. ⚠ WHAT KIND OF INDEPENDENCE THIS IS, STATED BEFORE THE RESULTS

**I authored none of these six findings.** They come from the 2026-09-18 clause-(c) assessment and
the 09-19 campaign, both before this session.

**But I am not independent of the campaign.** I spent 2026-09-20/21 on its closeout — the
corrections, the merges, the records. So this is independence of **these findings**, not of the
work around them.

That is the right kind of independence for what these are. The 09-18 assessor drew the line itself
and it is the line clause (c) turns on: *re-measuring a digest or a count is fine, because
independence is about **judgement**, not arithmetic.* **Every item below is arithmetic or a direct
artifact read.** None is a verdict, and this record reaches none.

## 1. The six

### (1) C4 — the jitter floor, job `58547629` — **REPRODUCED EXACTLY**

Read from the job's own log, `zdet-DIAGNOSTIC-20260918/c4_jitter_58547629.out`:

```
[cause4] jitter floor ||x_cv(s+7)-x_cv||^2 = 3.730946e-78  (= 2*sum sigma_jit^2); sqrt = 1.931566e-39
[cause4] PRINT-ONLY
[cause4] condition-3 guard PASSED
reported bins = 10694 of 65856 (predicate x_cv > 0; 55162 genuinely zero
```

All five claimed values match: `3.730946e-78`, `sqrt 1.931566e-39`, print-only, the condition-3
guard passing, and `10694 of 65856`.

### (2) C2 — the F7 margin — **REPRODUCED ARITHMETICALLY, from committed operands**

`shift / (k · floor)` with `floor = sqrt_tr / sqrt(N)`, `k = F7_FLOOR_MULTIPLE = 2.0`:

| operand | value | source |
|---|---|---|
| `joint_mean_shift_norm` | `1.878696733368378e-38` | `VALIDATION_LEDGER.md`, corrected J28 |
| `sqrt_tr_unified` | `4.443673650575504e-38` | same |
| `N` | `160` | same |
| `k` | `2.0` | `uq_math.py:143` |

    floor  = 3.513032e-39
    ratio  = 5.347792          (the ledger's VERIFIED-NUMERIC "5.35x")
    margin = ratio / k = 2.673896     <-- the recorded 2.6739 / 2.673896, EXACT

The two derived figures also reproduce exactly: the multiplier that would have had to fail is
`(2.673896 − 1)·sqrt(318) = 29.85`, and *"clears the strictest candidate by 2.29×"* is
`2.673896 / 1.168 = 2.2893`.

> ⚠ **AND I READ THAT LAST PHRASE WRONG FIRST.** I computed *"clears by"* as `(ratio − 1)/margin`
> and got **9.96×**, not 2.29×. The recorded quantity is **ratio ÷ the upper band edge**. Both are
> defensible readings of the English; only one is the number. Recorded because the phrase *"clears
> it by 2.29×"* will be re-derived by someone else, and they have a 50% chance of my error.

### (3) NULL — the like-for-like `r_null` — **REPRODUCED**

| | value | artifact |
|---|---|---|
| P0 like-for-like | `4.431129925843213e-14` | `zdet-DIAGNOSTIC-20260918/cv_divergence_DIAGNOSTIC_r2.json` |
| historical | `4.4520002137582904e-14` | `uq_5d/z_pilot_20260916_a5/*.json` (`r_null`) |
| relative difference | **0.469%** | computed |

`V6` states the stability as *"0.5%"*. `0.469%` rounds to it. **They are the same claim**, and the
two-significant-figure form is what was quoted.

### (4) The seven boundaries and `s_proj` — **THREE REPRODUCE, ONE IS SUPERSEDED, ONE MOVED**

| sub-claim | result |
|---|---|
| all seven boundaries `read_by_production: no` | **REPRODUCED** — `boundary_readership.py` prints `no` for all seven |
| `z_validator.py` has no `__main__` | **REPRODUCED** — 0 occurrences |
| `s_proj` is implemented code | **REPRODUCED** — but at **`z_statistics.py:319`**, not `:203` |
| `z_validator.assess` has no caller outside `tests/` | ⚠ **NO LONGER TRUE** |

> ### ⚠ TWO CORRECTIONS, AND NEITHER IS A DEFECT IN THE ORIGINAL
>
> **`assess()` now HAS production callers** — `z_build.py:762` and `z_grade.py:616`. The claim was
> true when written on 2026-09-18 and was **overtaken by events on 09-19**, when `z_grade` became
> the first production caller. That is not drift: it is the trigger
> `test_s_proj_has_no_UNSANCTIONED_caller` exists to fire on, and it **did** fire. Anyone reading
> `V6` item 4 as current state would conclude the assessor has never run in production, which is
> now false.
>
> **`s_proj` is at `z_statistics.py:319`.** `:203` is cited by `V6`, by `OPERATIVE-SHEET` §2 and by
> `evaluate_a7`'s docstring. The function exists and is the right one; the line moved. A `file:line`
> citation is dated the moment the file is edited — cite the symbol, or pin the line to a sha.

### (5) `run_m1_projection.sh` passed `--run-class` zero times — **CONFIRMED**

Measured across four revisions, which is what makes it a historical claim rather than a current one:

| revision | occurrences of `--run-class` |
|---|---|
| `5be86f55^` | **0** |
| `5be86f55` | 2 |
| `c34553e5` | 3 |
| `HEAD` | 3 |

The absence is real, and `5be86f55` is exactly where the repair landed — the same commit the
variant guard arrived in.

### (6) Job `58549890`'s two-direction control — **REPRODUCED, and it is R3's own incident**

From `zdet-DIAGNOSTIC-20260918/m1_control_58549890.out`:

    rc=3   rc=3                            <- leg A, two genuine refusals
    rc=139 rc=139 rc=139 rc=139            <- leg B, four SEGFAULTS
    CONTROL FAILED: B4_CONTROL_publication_from_CV_variant was expected to PRODUCE

**The answer to `V6`'s question — "whether its arms discriminate" — is: leg A's do, leg B's never
executed.** `rc=3` is distinct from `rc=139` and from the expected produce, and the control
correctly reported `CONTROL FAILED` rather than counting a crash as a refusal.

⚠ **This is the artifact behind the rule.** The earlier checker at this site tested `rc == 0` and
reported these four `139`s as refusals. The log above is what that looked like once the checker
named a crash as a crash.

## 2. Disposition

**`L7` is closed as to reproduction.** Six items, six reproductions, from artifacts and committed
operands rather than from report.

⚠ **What that does and does not mean.** `V6` never doubted these values — its own words were *"none
of these is doubted; none was reached from where I sat."* So this closes a **reachability** gap, not
a **credibility** one, and it does not retroactively make the clause-(c) verification complete at
the time it was written. `L6` — verification followed adoption — is untouched and still stands.

**Two live consequences, neither of them a re-grade:**

1. **`V6` item 4's `assess()` sub-claim must not be quoted as current.** It describes 2026-09-18.
2. **`z_statistics.py:203` should be re-cited** wherever it appears — `OPERATIVE-SHEET` §2, `V6`,
   `evaluate_a7`'s docstring. The line is now 319 and will move again.

**Co-Authored-By: Claude Opus 5 (1M context)**
