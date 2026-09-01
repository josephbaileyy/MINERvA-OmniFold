# RECORD 2026-09-01 — round 2 of the seven k=0 arms COMPLETED 374 of 374 with zero failures

**CITABLE FOR:** the tally in §1; the per-arm actuals in §2; the product verification in §3; and the
operand and deploy-tree facts in §4. **NOT CITABLE FOR:** any gate movement; discharge of any `F-*`
clause or quarantine cause; ratification of `OI-177`; adoption; a claim that Gate 2 can now pass; leg
6; or the M(ii) family. **Gate 2 remains FAIL and no scalar-5D covariance is adopted.**

## 1. The tally, which is the deliverable — an empty queue is not success

Run `k0-7ac0edec-20260830T000215Z`, round 2, submitted 2026-08-30T20:47:32–20:47:38Z, queue empty
2026-09-01T08:57:51Z. **Elapsed wall-clock: about 36 hours.**

| | |
|---|---:|
| declared tasks | **374** |
| **COMPLETED (distinct task identities)** | **374** |
| FAILED / CANCELLED / TIMEOUT / NODE_FAIL / OUT_OF_MEMORY / PREEMPTED | **0** |
| still queued or running | **0** |

**Counted as distinct `jobid_task` identities** with `.batch`/`.extern` step rows and array-bracket
rows excluded. That method matters: counting `sacct` ROWS gives 447 against 374 declared, because
`sacct` returns several rows per identity.

Round 1 of this same run died with six tasks failing in 8–15 s on `OI-179`. The only change between
the two was one exported variable, `MNV_ENV_SYSTEM_PREFIXES`, widened to three entries. **No code,
launcher or `MANIFEST` pin was altered.**

## 2. Per-arm actuals

Summed `Elapsed` over completed distinct identities, under §6's convention — GPU work in A100-hours,
CPU work in CPU task-hours, auxiliary cores on a GPU allocation not double-counted.

| arm | tasks | round-2 actual | `aa67c426` | §6 ceiling | verdict |
|---|---:|---:|---:|---:|---|
| 1 bootstrap `boot5dG` | 100/100 | **14.86** A100-h | 15.38 | 20 GPU | inside |
| 2 seed split `ssplit5d` | 24/24 | **5.83** CPU-h | 5.43 | 5 CPU | **OVER** |
| 3 detector `det5dBKG` | 19/19 | **13.76** A100-h | 13.88 | 20 GPU | inside |
| 4 sweep `sweep5dBKGrun` | 169/169 | **26.28** A100-h | 25.54 | 30 GPU | inside, 12.4% headroom |
| 5 uthrow run `uthrow5d_runF` | 40/40 | **49.11** CPU-h | 30.94 | 30 CPU | **OVER by 63.7%** |
| 6 uthrow block `uthrow5d_block` | 21/21 | **31.01** CPU-h | 30.01 | 30 CPU | **OVER** |
| 7 combine `uthrow5d_combF` | 1/1 | **0.58** CPU-h | 0.42 | 5 CPU | inside |
| | | **54.90 GPU / 86.53 CPU** | | 70 / 70 | **CPU SUM EXCEEDS 70** |

**Three facts here are new and they change `OI-177`, which is why they are recorded before anyone
ratifies anything.**

**(a) The GPU arms reproduced and the CPU arms did not.** Detector agreed to **0.9%** across two runs
at n=19 both times (13.88 → 13.76); bootstrap moved −3.4%; sweep +2.9%. Against that, **arm 5 moved
+58.7%** (30.94 → 49.11). A work-content explanation does not predict that asymmetry; contention does,
and §3c of the amendment records the throughput trace — six consecutive hourly deltas of +29, +31,
+70, +42, +3, +2, with `squeue` showing 2 tasks running and the rest on `Reason=Resources` while
`ArrayTaskThrottle` stood at 40, 10 and 24.

**⚠ SHARPENED AND PARTLY CORRECTED 2026-09-01, `AMENDMENT §3e`.** Two measurements were added after
this paragraph was written. **The strong evidence is the per-task FLOOR:** every arm with n>1
reproduces its fastest task to within ±6% across the two rounds (`33.0`→`34.7` min on arm 5) while the
CPU arms' medians move +22% to +75% — if each task were doing more work the fastest would slow too,
and it does not. **The complication is `TotalCPU`:** arm 5 consumed +50.4% more actual CPU time
(`1015.97`→`1528.40` h), so this is on-node interference that *burns* CPU, not queue waiting, and
"contention" above should be read in that narrower sense. **`TotalCPU` is therefore NOT the
contention-independent unit** §3c hoped for. **And arm 6's `+3.3%` in the table above is not
reproducibility** — R1 `39.4/52.2/518.3` against R2 `40.5/81.9/289.0` min are two unlike distributions
whose sums coincide.

**(b) The amendment's own projection was LOW.** §3b projected arm 5 at **46.3** CPU-h from 13 of 40
completed tasks; the true figure is **49.11**, so the partial-array projection understated by 5.7%.
Recorded because the projection was used to argue against ratifying, and it argued correctly but for a
slightly optimistic reason.

**(c) The CPU column now exceeds §6's declared sum of ceilings**, 86.53 against 70. Each arm is still
far inside the strictly-under-500 delegated thresholds, so no authority boundary is crossed — but the
§6 sum row is no longer descriptive of this rehearsal.

## 3. Products verified as READABLE, not merely marked

143 `.done` markers across the member namespace: `boot_nd_5d` 100, `seedscan_split_5d` 24, `uq_5d` 19.
The namespace was **empty at submission**.

`.npz` products opened and every member read — not merely opened, which is BEN-023's distinction:
**100 bootstrap, 24 seedscan, 61 `uq_5d` — 0 unreadable.**

**MY FIRST READ REPORTED TWO FAILURES AND MY READER WAS WRONG, NOT THE FILES.** Two `uq_5d` products
raised `ValueError: Object arrays cannot be loaded when allow_pickle=False`. That is a numpy *reader
default*, not corruption. Re-read with `allow_pickle=True`: **all 61 read, all 61 contain object
arrays, 0 genuinely unreadable.** A sample carries `xs` float64 `(4, 65856)` plus `throws`, `flux_u`,
`estimator_seed`, `draw_seed`, `est_seed_offset_declared`. Recorded because a reader misconfiguration
reported as a product defect is exactly the error class this campaign keeps filing.

`uthrow5d_combF`'s stderr is 9,178 bytes and contains **0** tracebacks and 0 violations — 30 sklearn
`feature names` warnings and ROOT `ReadRootmapFile` duplicate-dictionary notices.

## 4. The operand and the protected trees

**The canonical operand never moved for the entire ~36-hour run.** Porcelain **726** and status digest
`d429f0f3` at submission (three reads, 20:47:32/37/38Z) and identically at **2026-09-01T08:58Z**. So
the dashboard lane did not take the release `CLOSE-20260830` granted it, and no `F-17(a)` currency
question arises from drift during this run.

**The deploy tree is still frozen**: `/pscratch/sd/j/josephrb/k0r2/clean` detached at `7ac0edec`,
porcelain 0. §7.0.19 held.

## 5. WHAT THIS DOES NOT ESTABLISH

**A completed run is not a passed gate.** Gate 2 remains **FAIL** on the six clauses of the delegated
re-evaluation at `327bc105`; three of them need PRODUCER FILINGS that do not exist, and `F-17(b)`'s
`:1471` half is impossible for this rehearsal by construction. **No grading has been performed by this
lane and none is authorized by this record.** The `F-17(b)` post-path capture, which `OI-178` settled
as a filed finding rather than a block, has not been taken.

**No quarantine cause is discharged.** The counts stay **CAND `1 of 7`, QUOTED `0 of 7`**, and
`DECISION-20260831` fixed the subject of that work as the stamped candidate, not the July artifact.

**Nothing is adopted.** `values.tex` is untouched.
