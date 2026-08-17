# AUTHORIZATION 2026-08-17 — Joseph lifts the arm-0 prohibition

**Joseph Bailey, verbatim: *"You can run arm 0."***

Recorded by the mediator in the turn it was given.

## What this lifts

`AUTHORIZATION-20260815-arm1-resubmit.md` (`0fb56af`), **"What is NOT authorized", item 1**:

> **"Arm 0 is not to be re-run, touched, or superseded. It is complete and is the primary product."**

**That clause is lifted, and only that clause.** Items 2-7 of the same document stand unchanged:
no second attempt on a further code change without further authorization; the five Gate-6 prohibitions
at `19585b7`; no promotion; nothing into `docs/analysis-note/`;
`/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059` stays frozen; no `scancel`, no `scontrol update`,
no repinning of any receipt-bound launcher.

## Why an authorization was needed at all, since cost was never the obstacle

`AUTHORIZATION-20260815-mediator-run-approval-under-one-gpu-day.md` grants the mediator approval of any
run under **24 GPU-hours aggregated**, and is **calibrated on the 5.9 GPU-h arm-1 resubmit as its
precedent**. Arm 0 at 3 draws × ~1.96 h is the same order.

**So the obstacle was never the budget — it was a prohibition**, and a standing spend grant cannot lift
a specific prohibition. The mediator spent hours describing this to Joseph as *"needs a fresh
authorization"* without naming item 1, which made a real blocker read as paperwork. **Recorded because
the failure was in the reporting, not in the judgement.**

## What this does NOT authorize

- **It is not a decision that the run is worth making.** Joseph's grant requires a peer confirm/deny for
  any run the mediator approves, and lane B is adjudicating that at the time of writing. **A DENY on the
  merits stops it and goes back to Joseph** — permission to run is not an instruction to run.
- **It does not close `OI-125`.** `OI-125`'s own instruction stands: do not close it by citing
  `1.011418` **or** `1.010879`; both are reconstructions. A fresh run produces a **recorded** end-of-run
  scalar, which is what the item asks for — **but from a NEW SAMPLE.** The driver's `estimator_seed` is
  pinned from a frozen policy (`closure_powered_truth_reweight.py:260`), yet three draws of identical
  configuration measured sd `0.000820128`, so the mechanism is **training nondeterminism, not an unset
  seed.** The new scalar therefore **cannot validate `VL134`**, and that is the same ground on which the
  arm-1 re-run was denied (`BEN-334`).
- **It does not authorize superseding arm 0's existing products.** The existing arm-0 draws
  (`57012031_0/1/2`, all `COMPLETED 0:0`) are the basis of published reasoning. **Preserve before
  writing**, per the stages-4-6 lesson: a 742 KiB snapshot did not contain a 39.4 GiB object, and the
  rebuild came out 23,969 bytes different.

## OUTCOME: NOT RUN. Lane B returned a DENY on the merits, and the mediator is holding.

**The permission stands and was not withdrawn. The run is not being made.** Joseph's own grant requires
a peer confirm/deny for any run the mediator approves, and this document said before the answer arrived
that *permission to run is not an instruction to run*.

Lane B's grounds, both verified independently by the mediator before acceptance:

1. **Item 1 is protecting exactly this hazard, and arm 0 is WORSE than arm 1 for it.**
   `sbatch_foldforward_instrumented_closure.sh:27` — *"ARM 0 IS A HARD GATE ON READING ARM 1. If arm 0
   does not reproduce the existing draws, arm 1 is not read at all."* And `RESULT_2`'s 16.2σ delta is
   `arm1 − arm0` with arm 0 = `57012031`. **So a second arm-0 population would make the reproduction
   gate ambiguous AND re-base the one quantitative result the closure produced.** Item 1's three verbs —
   *"re-run, touched, or superseded"* — read like someone who had thought this through.
2. **What the run would buy cannot be bought.** The end-of-run scalar for `57012031` was not recorded at
   the time, and `67c94df`'s recorder cannot record it retroactively. **`OI-125`'s gap for the AUDITED
   products is permanently unclosable by compute.** A fresh run yields a fourth number about a
   population that did not exist when the question was asked.
3. **The recorder proves itself for free.** It is in the wrapper; the next closure run that happens for
   its own reason carries it at zero marginal cost. **Spending 5.9 GPU-h to manufacture an occasion for
   an instrument is the tail wagging the dog** — the same shape as the arm-1 proposal B withdrew.

**Disposition: `OI-125` closes DOCUMENTARILY, not by a run.** `67c94df` records the quantity for all
future runs; for the audited products the value is a reconstruction and must be cited as such, which
`BEN-360` already requires. That is a complete closure of a real gap — it simply is not a measurement.

**One correction B supplied to the mediator's framing:** arm 1 was denied for **redundancy** (it had
already run), not for sampling noise. Arm 0 does not share that ground — the recorder has genuinely
never been carried. It shares the **sampling** ground, and here sampling is sufficient on its own,
because `OI-125` asks about a specific prior population and a new sample cannot speak to it.

**Returned to Joseph.** The permission is his and remains open; the recommendation is not to use it.

## Preconditions before any submission

1. **A predeclaration**, committed before execution, stating what would count as success and what the
   run cannot establish — including the `VL134` limitation above, so it cannot be reconstructed after
   the fact (`BEN-361`).
2. **Peer confirm/deny**, per the standing grant.
3. **Write set enumerated BEFORE the ruling**, not reversibility asserted after (`BEN-346` and the
   stages-4-6 near-miss).
4. **The wrapper pin re-derived in the turn of submission** — it has moved four times in two days.
5. **The allocation id derived in the turn it is reported** (`BEN-303`): `57128458` is `TIMEOUT`;
   `57142574` is the live `claude-hold` and self-expires.

## Related

- `AUTHORIZATION-20260815-arm1-resubmit.md` (`0fb56af`) — the document whose item 1 this lifts.
- `AUTHORIZATION-20260815-mediator-run-approval-under-one-gpu-day.md` — the spend grant, which was never
  the constraint.
- `BEN-334` — the launcher already carried the denial of the arm-1 re-run.
- `BEN-360`, `BEN-361`, `OI-125` — why the end-of-run scalar is the quantity at issue.
