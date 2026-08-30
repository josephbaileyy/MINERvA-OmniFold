# RECORD 2026-08-30 — the `OI-179` remediation is CONFIRMED IN A REAL SCHEDULED JOB

**CITABLE FOR:** the measured fact that `mnv_env_pathcheck` branch (b) passes inside round-2 Slurm
jobs on both partitions; the four completed tasks and their products; and the confirmation this gives
the `OI-179` diagnosis. **NOT CITABLE FOR:** the rehearsal's outcome, which is NOT known — 4 of 374
tasks have finished (§3); any gate movement or `F-*` discharge; closure of `OI-179`, which stays
**OPEN** on defect 1; `OI-177` ratification; leg 6; the M(ii) family; or adoption. **Gate 2 remains
FAIL and no scalar-5D covariance is adopted.**

## 1. The question this answers, and only this

`OI-179` claimed round 1 died because the submission never declared `MNV_ENV_SYSTEM_PREFIXES`, that
the guard was correct, and that **no code needed to change**. That was an argument from three
artifacts. **It is now confirmed by successful remediation, which is stronger evidence than the
textual argument was**, because the prediction was falsifiable: declare the allowlist, change nothing
else, and the same launchers on the same deployment sha should start.

## 2. Measured — the guard passes, on both partitions

Round-1 failures were byte-identical across three arms on two partitions, so the matching positive has
to span partitions too. Every round-2 `.out` written by 21:38Z:

| log | pathcheck | entries | violations |
|---|---|---|---|
| `boot5dG_1_57753239.out` | **OK** | 47 | 0 |
| `boot5dG_2_57753239.out` | **OK** | 47 | 0 |
| `ssplit5d_1_57753243.out` | **OK** | 47 | 0 |
| `ssplit5d_2_57753243.out` | **OK** | 47 | 0 |

`boot5dG` ran on `shared_gpu_ss11` (`nid008356`), `ssplit5d` on `shared_milan_ss11`
(`nid004106`, `nid004122`) — **the two partitions that produced round 1's identical refusals.**

**Then they COMPLETED**, which is the part a passing guard alone would not establish:

| task | elapsed | state |
|---|---|---|
| `57753239_1` | `00:08:53` | **COMPLETED** `0:0` |
| `57753239_2` | `00:08:45` | **COMPLETED** `0:0` |
| `57753243_1` | `00:17:18` | **COMPLETED** `0:0` |
| `57753243_2` | `00:11:24` | **COMPLETED** `0:0` |

And they produced products. `nd-unfolding/mii/member_k000000/` went from **0 entries** at submission
to `boot_nd_5d/` and `seedscan_split_5d/` with **4 `.done` markers**, one per completed task.

**THE ENTRY COUNT, and the one thing here that is NOT explained.** Three measurements: **37** on the
login PATH with the guard unactivated, **46** in the activated login-node control, **47** inside every
job. The 37 → 46 step is the env root and conda prefix. **The 46 → 47 step is unexplained.** It is
consistent — identical across all four tasks and both partitions, so it is a login-node-versus-compute-node
difference and not per-job variance — and it is benign, since the verdict is OK either way. Recorded as
unexplained rather than glossed.

**Stderr is not empty and that is fine.** All four `.err` files carry only repeated sklearn
`UserWarning: X does not have valid feature names, but LGBMClassifier/LGBMRegressor was fitted with
feature names`. No errors. Its presence is positive evidence: the tasks are inside the LightGBM
reweighting, which is the science.

## 3. WHAT THIS DOES NOT SAY

**The rehearsal has not produced a result.** Four tasks of a **374-task** submission have finished
(100 + 24 + 19 + 40 + 21 + 169 + 1). Arms 3, 4 and 5 had not started; arms 6 and 7 are still on
`(Dependency)`. A run outcome is a separate record and is not owed by this one.

**`OI-179` STAYS OPEN.** Defect 3 is closed for this run only, by
`submission-environment-round2.txt`. Defect 2 is repaired at `b512760d`. **Defect 1 is untouched:**
`PACKET-20260823-round5-f2a-f17a-repair.md:122` still documents the two-entry line that measures
**rc 3** on `$HOME/bin`, so the next submitter who follows the packet verbatim still fails. Correcting
it is Joseph's call.

**No gate moves.** Even a complete successful run cannot turn this rehearsal's Gate 2 into **PASS**:
three of the six clauses at `327bc105` need producer filings that do not exist, and `F-17(b)`'s
`:1471` half is impossible here by construction. **`OI-177` remains OPEN and unratified** while arms
2, 5 and 6 run against its ceilings.

## 4. One latent issue observed and deliberately not acted on

Fitting with feature names and predicting without them is positionally safe today but would **silently
mask a column-reorder bug** if the arrays were ever permuted. It is pre-existing, unrelated to
`OI-179`, and mid-run is the wrong moment. Noted here so it is not lost; it needs its own row, and
this identity's `120-139 / 170-179` block is **exhausted**, so filing it requires a fresh ten-block.
