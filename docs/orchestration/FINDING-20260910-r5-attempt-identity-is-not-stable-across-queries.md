# FINDING 2026-09-10 — the `R5` attempt identity is NOT stable across `sacct` queries, so an
# apparent 62-attempt "loss" is not a loss and the budget must NOT be increased

**CITABLE FOR:** the four measurements in §2 and the accounting rule in §4.
**NOT CITABLE FOR** any scientific scope decision, any Z ruling, any gate movement, or any claim
that attempts were purged. **This is an accounting-instrument finding and it is deliberately kept
apart from Z's scope questions** — nothing here changes what may be built, only how spend is read.

**Owner:** the `r5_meter` owner. **Filed by:** the Z orchestration lane, which found it while
re-measuring spend for a cost section and should not also adjudicate it.

## 1. What prompted it, and the claim that is now WITHDRAWN

`nd-unfolding/Z_CONSTRUCTION_PLAN.md` §5.1 (at `d147880f`) reported that `R5` spend **decreased**
`14.9756 → 14.4897` CPU task-h and `1888 → 1826` attempts over a closed window, and framed it as
attempts going missing. **The framing is withdrawn.** The aggregate difference is real; the
inference that attempts were lost is not supported, and §2 shows why.

## 2. THE RECONCILIATION, BY IDENTITY

Three raw captures are preserved in-tree; a fourth is not (§3):

| capture | when | rows | path |
|---|---|---:|---|
| **C1** | 2026-09-06 | `958` | `state/preflight-20260906-r5/sacct-r5-window-ALL-duplicates-8field.psv` |
| **C2** | 2026-09-07T01:54:09Z | `1,155` | `state/preflight-20260907-r5-followup/r5-window-preserved.psv` |
| **C3** | 2026-09-09T19:38:19Z | **NOT RETAINED** — digest only | `state/r5-meter-receipt.json`, `raw_sha256 03ee134d…` |
| **C4** | 2026-09-10T06:58:37Z | `1,827` | `state/r5-capture-20260910/…psv`, `sha256 415ed894…` |

**Comparing C2 and C4 on ONE job and ONE span**, so the populations match — job `57712764`, the
waker, `Start ≤ 2026-09-07T01:50:15`:

```
                        C2 (09-07)     C4 (09-10)
attempts                     1155           1177     (+1.9%)
ElapsedRaw sum             47,033 s       45,997 s   (-2.2%)
attempt ids (JobID,Start,End) in BOTH:  8
                          only in C2:  1147
                          only in C4:  1169
```

**And bucketed at 10-minute granularity over the 542 overlapping buckets:**

```
buckets with IDENTICAL row count    : 523 / 542   (96.5%)
buckets with IDENTICAL Start stamps :   1 / 542   ( 0.2%)
```

**So the aggregates reproduce to about 2% and the identities do not reproduce at all.** Sampled
rows show why — the same 5-minute requeue slot is reported with a different `Start`, `End` and
`ElapsedRaw` on each query (`12:00:07→12:00:14, 7 s` in C2; `12:00:24→12:00:33, 9 s` in C4).

## 3. WHAT FOLLOWS, AND WHAT DOES NOT

- **Attempts were NOT shown to disappear.** With an unstable key, a set difference measures the key,
  not the population. The 1,147 "only in C2" figure is an **artifact**, and so is the 62.
- **The union of captures is NOT a floor.** Unioning C1∪C2∪C4 gives `2,974` distinct "attempts"
  against ~`1,826` real ones — **double-counting the same executions under different stamps.** Do
  not sum captures.
- **The mechanism is NOT established.** Retention, a slurmdbd write path, or a requeue bookkeeping
  detail would each fit. **No mechanism is asserted here**; the observation is the finding.
- **⚠ IT TOUCHES THE METER'S OWN UNIT.** `r5_meter` identifies an attempt by `(JobID, Start)`
  (`r5_meter.py` docstring, `_calculate_spend:277`) and **fails closed** when two rows share
  `(JobID, Start)` but disagree on `End`/`ElapsedRaw`. If `Start` is unstable across queries, then
  (a) within one query the dedup is doing less than intended, and (b) the documented
  two-window concatenation path could fail closed on honest re-queries. **For the meter's owner to
  adjudicate, not this lane.**

## 4. THE ACCOUNTING RULE, UNTIL THE OWNER RULES

1. **Carry the MAXIMUM observed spend, never the latest.** As of today that is **`14.9756` CPU
   task-h** (C3) and **`0.0` GPU**, so headroom is **`≤ 485.02` CPU**. **A re-query returning a
   lower number does not release budget.**
2. **Never sum or union captures.**
3. **Quote spend with its measurement instant attached.** It is a timestamped observation of an
   external store, not accumulated state.
4. **Preserve the raw rows beside every receipt.** C3's are gone and only its digest survives, which
   is why the 09-09→09-10 step cannot be reconciled at all. C4 is preserved here for that reason.

**None of this is close to binding.** GPU `0.0 / 500`; CPU `≈15 / 500` under either reading. The
constraint on this campaign is the date and the open decisions — **and that conclusion is the same
under the conservative rule, which is why adopting the conservative rule costs nothing.**
