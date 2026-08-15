# AUTHORIZATION 2026-08-15 — arm 1 of the fold-forward instrumented closure may be RESUBMITTED

**Granted by Joseph Bailey, 2026-08-15.** Recorded before it is used, per `BEN-201`.

## Why a fresh authorization was required at all

Joseph's consensus grant (`AUTHORIZATION-20260815-consensus-grant.md`, `451f053`) relaxes **cost**, not
**scope**, and the lane that wrote the fix stopped itself on exactly that boundary. `4e85f0e`'s own
commit body, verbatim:

> "NOTHING RESUBMITTED. Arm 1 is 5.9 GPU-h and Joseph authorized one submission of a specified design;
> a resubmit after a code change is a new submission and goes back to him."

**That self-arrest is the correct behaviour and is recorded here as such.** The mediator's reading —
that the *design* is unchanged and only a dtype defect was repaired, so this is arguably a repair
rather than a redesign — was **not** used to bypass the ask. It was put to Joseph, who authorized it
directly. A lane's own scope reservation is not for the mediator to reason away.

## The grant

Joseph was presented with three options (resubmit / resubmit-after-predeclaring / not tonight),
each with its cost and consequence, and selected **resubmit**.

**Authorized: one resubmission of arm 1, 3 draws, 5.9 GPU-h.** Nothing else.

## Measured state this authorization rests on

All verified by the mediator in the turn the authorization was given, not recalled.

`sacct -X -j 57012031`:

```
57012031_0|COMPLETED|0:0|01:56:11|2026-08-15T07:20:04     ARM 0
57012031_1|COMPLETED|0:0|01:56:02|2026-08-15T07:20:42     ARM 0
57012031_2|COMPLETED|0:0|01:57:06|2026-08-15T07:40:26     ARM 0
57012031_3|FAILED   |1:0|00:02:05|2026-08-15T05:46:16     ARM 1
57012031_4|FAILED   |1:0|00:01:57|2026-08-15T06:02:32     ARM 1
57012031_5|FAILED   |1:0|00:02:07|2026-08-15T06:02:42     ARM 1
```

**Arm 0 is complete, healthy, and untouched.** It is the run's primary product: it closes `OI-125` and
supplies `OI-71`'s `G4` recovery evaluation. **Only arm 1 broke**, on the float64/float32 promotion in
`net.weighted_binary_crossentropy:13`.

**The fix has never been exercised on the cluster.** `4e85f0e` is dated `2026-08-15T12:55:45Z`; the
first arm-1 task died at `12:46Z`.

**The `G0` gate is clear and needs no repin.** `sbatch_foldforward_instrumented_closure.sh:86-91`
declares four pins, and the wrapper pin already equals the fixed file:

```
pinned   ee269b09a1ab42059e54542b6b970068be3869d9c1066fe7cca7759676be621c
local    ee269b09a1ab42059e54542b6b970068be3869d9c1066fe7cca7759676be621c   identical
```

because `c6edc13` (`09:01:09 -0400`) added the pin **5m24s after** `4e85f0e` (`08:55:45 -0400`).
**No launcher change, no repin, and this is NOT `OI-123`/`BEN-270` territory.**

## THE BINDING CONDITION — copy order, and it is asymmetric

**Both files on the cluster are stale**, deliberately: the authoring lane withheld the hardened
launcher while `_4`/`_5` were pending so all three arm-1 tasks would fail identically. Measured on
`/pscratch` this turn:

```
closure_foldforward_instrumented.py        253f25c0…7351d57d   STALE
sbatch_foldforward_instrumented_closure.sh 19cb39b8…c069ca6a   STALE
```

| what is copied | outcome |
|---|---|
| **both** | `G0` passes on four digests, fix exercised, provenance intact. **The only clean path.** |
| **wrapper only** | the old launcher has **NO wrapper pin**, so it passes **silently while running changed code** — exactly the provenance hole `c6edc13` was written to close. |
| **launcher only** | `G0` **refuses** (`253f25c0…` ≠ `ee269b09…`), correctly and loudly. Safe. |

**So: copy the launcher first, or both together. NEVER the wrapper alone.** This condition is part of
the authorization, not advice.

**Confirm which version ran from the log line itself**, which is self-identifying:

```
old :  "G0 PASS  driver/annealed-wrapper/engine all match their recorded digests"            (3 pins)
new :  "G0 PASS  driver/annealed-wrapper/engine/instrumentation all match their digests"     (4 pins)
```

**A run whose log prints the 3-pin line has run the old launcher and its provenance is not intact.**

## What is NOT authorized

Everything else. Restated so no later reader has to infer it:

1. **Arm 0 is not to be re-run, touched, or superseded.** It is complete and is the primary product.
2. **No second attempt on a further code change** without a further authorization. This grant is one
   submission of the design as it stands at `4e85f0e` + `c6edc13`.
3. **The five Gate-6 prohibitions at `19585b7` are untouched** — `do_not_select_passing_subset`,
   `do_not_construct_C_ML`, `do_not_move_central`, `do_not_start_leg_2`, `do_not_retry_unchanged`.
4. **No promotion.** Nothing here designates any product quotable, and `P5A` stays unpromoted.
5. **Nothing into `docs/analysis-note/`.**
6. **`/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059` stays frozen.**
7. **No `scancel`, no `scontrol update`, no repinning of any receipt-bound launcher.**

## The consensus behind it

| lane | position |
|---|---|
| lane B | **launch arm 1, and nothing else**, conditional on Joseph's fresh authorization and on the `G0` question — both now satisfied |
| `Assistant` | `G0` **pinned and matching**; resubmit clean; flagged the copy-order hazard against its own withheld copy |
| lane A | **do not run** the *Leg 0 tier* item tonight; did not oppose arm 1, which is a different item |
| mediator | recommended yes; put it to Joseph rather than reading it into the standing grant |

## Related

- `AUTHORIZATION-20260815-consensus-grant.md` — the cost grant this does **not** rely on.
- `4e85f0e` — the dtype fix and `BEN-314`. `c6edc13` — the `G0` hardening that added the fourth pin.
- `OI-125` (closed by arm 0), `OI-71` `G4` (supplied by arm 0).
