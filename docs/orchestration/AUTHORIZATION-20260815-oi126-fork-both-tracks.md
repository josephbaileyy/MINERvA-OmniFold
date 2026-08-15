# AUTHORIZATION 2026-08-15 — the `OI-126` fork: BOTH tracks, in parallel

**Granted by Joseph Bailey, 2026-08-15.** Recorded before either track spends, per `BEN-201`.

## The grant, verbatim and complete

Joseph's question, then his authorization:

> "Is it possible to do both?"

> "Yes I authorize both"

The two tracks presented to him, which is what "both" refers to:

- **Track B — publish `C_stat` with the `(a)`/`(b)` fork explicitly stated.** Unblocks PET now.
- **Track A — run the clean `Exponential(1)` vs `Poisson(1)` contrast**, ~39 GPU-h at n≈6 per arm,
  via the legitimate route: re-issue the dataloader binding, widen the diagnostic namespace, inject
  at the real seam. **No monkeypatch.**

## Why both, and why the ORDER inside "both" matters

The outcomes are **not symmetric**, and this was put to Joseph before he authorized:

- If the contrast returns **(a)** — genuine estimator instability — the published limitation is
  *confirmed*. A footnote becomes a measurement. Pure upside.
- If it returns **(b)** — `Poisson(1)` on the measured leg is not a valid statistical-uncertainty
  proxy — then `C_stat` was built the wrong way, and correcting that **after** publication is an
  erratum rather than a revision.

**So the contrast should finish before the paper freezes.** That is achievable: ~39 GPU-h with an
empty queue.

## The scheduling constraint that turned out to be fictional

The `Assistant` lane's prior recommendation was to sequence the re-issue *after Leg F terminates*.
**Leg F terminated 2026-08-14T09:02:08, over 24 hours before this authorization** — measured by
`sacct`, all four tasks `COMPLETED`:

```
56863958_2  COMPLETED  03:15:09  ended 2026-08-13T14:08:51
56863958_3  COMPLETED  03:15:26  ended 2026-08-13T14:16:55
56863958_4  COMPLETED  03:12:35  ended 2026-08-13T18:35:57
56863958_5  COMPLETED  03:17:24  ended 2026-08-14T09:02:08
```

`LIVE-STATE.md:29` rendered it as `**ACTIVE**: UNKNOWN=4`. The generator could not reach Slurm, got
`UNKNOWN`, and displayed that as a liveness claim. **Three sessions and the mediator propagated it.**
Lane A alone flagged the provenance correctly (*"quoted from the control plane's job list, not
measured"*) and the mediator relayed the caveat without acting on it. Cost of checking: one `sacct`
call. Filed with lane A; rendering fix authorized separately.

## Binding conditions on Track A

These were offered by the `Assistant` lane and accepted by the mediator BEFORE authorization; they
are not negotiable after seeing a number.

1. **Co-signed predeclaration before any code is written**, both key-holders on it.
2. **A numeric two-sided decision boundary fixed in code**, not chosen by eye afterwards. The
   `4.0` boundary is **retired**: it sat `0.403` from the measured `(a)` truth of `3.5969`, under a
   quarter of a sigma, so the Poisson arm itself crosses it on a large fraction of draws.
3. **`UNRESOLVED` is a real outcome and does NOT default to `(a)`.**
4. **The continuous-null assumption stated with its counterargument beside it** — that row-level
   Poisson zeros are not the same object as a bin genuinely observing zero events.
5. **The sizing caveat carried in the predeclaration, not buried:** n≈6 uses the *Poisson* arm's
   `sigma = 1.6091` for the *untested* arm, and `n` grows as `sigma^2`. Further, the re-centred
   boundary `2.298` is the midpoint of one **measured** mean (`3.5969`, n=50) and one **assumed**
   null (`1.0`). **The `(a)` hypothesis was anchored on a high draw; the `(b)` hypothesis is
   anchored on nothing.**
6. **The override's own identity recorded** in the diagnostic receipt — module digest, distribution
   name, and a hash of the realized float array — so the arm is self-describing. This is the
   `lr_proof` remedy applied in advance.
7. **The diagnostic claims no family membership** and constructs nothing quotable.

## Measured inputs this authorization rests on

| quantity | value | source |
|---|---|---|
| band `R_push` across 50 replicas | mean `3.5969`, sd `1.6091`, range `1.086`–`6.887` | `7ceb18c`, re-derived by mediator |
| `replica_00` | `5.0467` = **70th percentile, z = +0.90** — NOT typical | same |
| n at boundary `4.0` | `>= 62` to confirm (a) | mediator, this turn |
| n at boundary `2.298` | `>= 6` both sides | mediator, this turn |
| per-replica cost | `3.2550` GPU-h + `0.6633` CPU-node-h | `sacct`, `Assistant` lane |
| full Gate-5 re-issue (rejected) | ~163 GPU-h + ~2–4 agent-days | `sacct` + peer costing |

## Related

- `OI-126` — the fork. Not cleared by this authorization; Track A is what would clear it.
- `AUTHORIZATION-20260815-standing-compute-grant.md` — the two-key grant. **Track A exceeds the
  12 h per-item threshold and was NOT approved under it.** It was put to Joseph explicitly rather
  than decomposed into two sub-12 h arms, which the grant's per-item reading forbids.
- `BEN-341` — instruments that report the right number for the wrong reason.
