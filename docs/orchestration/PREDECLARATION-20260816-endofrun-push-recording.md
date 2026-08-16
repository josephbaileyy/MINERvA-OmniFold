# PREDECLARATION 2026-08-16 — the end-of-run push, RECORDED, and what its 4-point series must show

**Written BEFORE any run carries the instrumentation.** No run is attached, authorized, or requested by
this document. Approved by the mediator as a zero-GPU code change; the 3-draw re-run that would have
exercised it was **proposed and DENIED the same day** (§6).

**Why this is predeclared at all, given no run is pending.** `BEN-361`: *a predeclared expectation is
worth its timestamp and nothing else.* The instrumentation lands now so that whatever run next carries it
— possibly weeks from now, possibly driven by a different lane for an unrelated reason — **cannot have the
reading of its new series chosen after the numbers are in hand.** That is the entire function of this file.

---

## 1. What changes, and the one thing it can see that nothing else could

`closure_foldforward_instrumented.py` now hooks **`RunStep2`** in addition to `RunStep1`, recording the
push `RunStep2(i)` *leaves*.

`Unfold` is `for i in range(start, niter): RunStep1(i); RunStep2(i); CompileModels(fixed=True)`
(`omnifold.py:172-177`), and `RunStep2` assigns `self.weights_push` at `:220`. The existing hook records
at the point of **consumption**, so with `niter=3` it sees the pushes left by initialisation,
`RunStep2(0)` and `RunStep2(1)`. **The push left by `RunStep2(2)` is consumed by nothing and recorded by
no row** — and it is the one that matters, because `closure_powered_truth_reweight.py:332-333` takes
`of.weights_push` *after* `Unfold()` returns, and `train_fullevent_nominal.py:576-577` computes the
nominal's fold-forward the same way. The nominal's `0.736746`, on which the whole `OI-71`/`OI-125`
argument rests, is an end-of-run scalar.

So the series goes from 3 points to 4: `init`, `RunStep2(0)`, `RunStep2(1)`, **`RunStep2(2)`**.

## 2. THE EXPECTATIONS, fixed now

**E1 — the overlap must be EXACT, and this is a gate, not a reading.** The push `RunStep2(i)` leaves *is*
the push `RunStep1(i+1)` consumes. Those rows must be **bit-equal** (`!=` on floats, not a tolerance),
`niter-1 = 2` pairs at `niter=3`. It holds for **both arms**, because the `RunStep1` row records the
**pre-correction** measurement — its record is appended before `if correct:` runs. **A disagreement means
one hook reads at the wrong moment and the end-of-run value cannot be trusted either.** Gated in the
wrapper (fail closed, no annotation written) *and* re-checked independently in the launcher's `G3`, which
does not take the wrapper's word for it.

**E2 — the recorded end-of-run value must be bit-identical to what the driver persists.** Only
`CompileModels(fixed=True)` runs between the last `RunStep2` and the driver's read, and it recompiles
models without touching `weights_push`. **Demonstrated, not reasoned:**
`test_the_final_capture_is_BIT_IDENTICAL_to_what_the_driver_persists`, with
`test_THE_ASSERTION_ABOVE_HAS_POWER_a_pre_delegation_capture_FAILS_it` proving a wrong-moment capture
fails the same assertion (`BEN-314`).

**E3 — for an arm-0 draw, the recorded end-of-run value is expected near `1.0109`, and agreement is NOT a
check.** `VL134` puts the arm-0 3-draw mean at `1.010878613` with `sd 0.000399`. A future arm-0 draw
should land within a few draw-sd of that. **This is a sanity expectation and nothing more.** Stated as a
prohibition because it is the mistake available here: **the driver takes no seed flag** (only
`--split-seed`; see `:23-24` of the launcher), so any later run is a **NEW SAMPLE** of the same
configuration. **A new recorded value CANNOT validate `VL134` and must not be reported as confirming it.**
If the two are ever printed together, they are two samples, not a measurement and its check.

**E4 — the recorded value is expected to DIFFER from the last `RunStep1` row by roughly `-3%`, and that
difference is the artefact, not a finding.** The last consumed row on the 2026-08-15 products was
`0.981165` against the end-of-run `≈1.0109`. **If a future run shows those two close together, that is the
surprising outcome** and it means the iteration structure changed, not that the instrumentation improved.

**E5 — `deviation_from_R` on the end-of-run row is a NEW quantity with no adopted threshold.** It is
recorded and reported. **Nothing passes or fails on it**, and no gate may be constructed from it in the
same document that first reports it.

## 3. What would make this instrumentation WRONG rather than uninformative

Declared so the failure is not later reframed as a result:

- **E1 fails** → one hook reads at the wrong moment. The run's fold-forward series is void, including the
  rows that previously looked fine.
- **The post-`RunStep2` record count ≠ `niter`** → the hook missed an iteration. Gated in both places.
- **More or fewer than exactly one row flagged `is_end_of_run_push`** → the flag is derived from
  `self.niter`, so this means the engine's loop bound is not what this instrumentation assumes.

All three fail closed and write no annotation.

## 4. What this does NOT do

- **It does not close `OI-125`.** `OI-125` is about the numbers already in the ledger, and those cannot be
  retroactively recorded. This changes what *future* runs can attest.
- **It does not retro-attest or modify the six 2026-08-15 receipts.** They remain the record, and
  `VL134` remains a **re-reduction of a persisted array** — verified twice to `1e-13`, which makes it
  reliable but still reader-computed. What a recorded value changes is *who* computed it.
- **It authorizes no run**, requests none, and moves no threshold. The five Gate-6 prohibitions at
  `19585b7` are untouched. Nothing becomes quotable.

## 5. Provenance of this change

Wrapper pin **move 3**, `0e1471ba → 7499814e`, in the same commit and documented at `:111-127` of the
launcher alongside moves 1 and 2. Driver, annealed-wrapper and engine pins byte-identical and untouched.
Landed **before** anything launches, together with the anneal attestation of `1b09a47` — a run wants both,
and the ordering is fixed here rather than left to whoever launches next.

## 6. The run that is NOT happening, recorded because the reasoning is the useful part

A 3-draw re-run (~6–12 GPU-h) was proposed to produce a recorded end-of-run scalar and **DENIED**. The
deciding fact is E3's: **the driver takes no seed flag, so a re-run is a new sample.** Its recorded scalar
would sit in the ledger beside `VL134` as a number a reader is tempted to compare and cannot. The gap it
targets is also thinner than "reconstruction vs recorded" suggests — `weights_push` is persisted by the
pinned driver, confirmed post-`Unfold()` at the site, and independently re-reduced to `1e-13` from two
different weight normalizations.

**So the instrumentation lands with no run attached, and the next run that happens for its own reasons
carries the value for free.** `6–12` GPU-h not spent.

## 7. Related

- `BEN-360` — the recorder captured the neighbouring quantity; this closes the specific gap it named.
- `BEN-361` — a predeclared pessimism is the least-checked claim. Hence §2's prohibitions.
- `BEN-314` — power-test the guard, or it is worse than none. Hence E2's paired failing control.
- `BEN-317` — the anneal attestation, `1b09a47`; the other half of what a future run needs.
- `VL134`–`VL140`, `OI-125` (narrowed, not closed), `OI-71` `G4`.
