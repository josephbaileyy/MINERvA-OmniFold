# The arm whose instrumentation nothing pinned — and the anneal that no receipt attests

**Filed 2026-08-16 by the executor (`Assistant`) lane, against its own instrumentation.** Row:
`BEN-317`. Found while checking whether the wrapper defects this lane named on 2026-08-15 still stand
now that arm 0's numbers are in the ledger as `VL134`/`VL135`/`VL136` and arm 1's contrast is `VL138`.

**Nothing here overturns a number.** Two of the three gaps are closed by measurement in this finding and
the third is bounded but left open. It is filed because **all three were invisible from the receipts, and
two of them are load-bearing for a contrast that is now published in `VALIDATION_LEDGER.md`.**

---

## 1. Arm 0 ran the 3-pin launcher, and the old launcher printed no digests at all

`AUTHORIZATION-20260815-arm1-resubmit.md` supplied a self-identifying test — 3 pins means the old
launcher, 4 means the hardened one — and used it to decide whether the **resubmit** was clean. It was:
all three arm-1 logs are 4-pin and print four digests.

**Nobody applied the same test to arm 0.** Line 1 of all three arm-0 logs:

```
[ff-launch] G0 PASS  driver/annealed-wrapper/engine all match their recorded digests
```

**Three pins.** Arm 0 ran before `c6edc13` added the wrapper pin, which is expected and was known. What
was not stated is the consequence: **the wrapper pin is the one that covers the instrumentation, so arm 0
has no attestation of the instrumentation version it ran** — and the old launcher printed only the
summary line, **no per-file digests at all**, so arm 0's logs do not even record the three values they
did check.

**Arm 0 is not a throwaway.** It is the run `VL134`, `VL135` and `VL136` come from, and half of `VL138`.

## 2. Which wrapper arm 0 ran — established from its own products, not from the launcher

The timeline does not settle it. Arm 0 launched `2026-08-15T12:23:59Z`, and **two** versions already
existed: `948e2b07` (`b372069`, `05:58Z`) and `253f25c0` (`c5c360e`, `11:55Z`). `ee269b09` did not exist
until `12:55:45Z` and is excluded.

**The products discriminate, and this is a measurement rather than an inference.** `948e2b07`'s
`install_fold_forward_recorder(base)` had **no `correct` parameter at all**, so it wrote none of the
arm-labelling fields; `c5c360e` added them. Arm 0's report carries:

| field | arm 0's value | present in `948e2b07`? |
|---|---|---|
| `fold_forward_arm` | `arm0_instrumented_only` | **no — added at `c5c360e`** |
| `fold_forward_correction_applied` | `False` | **no — added at `c5c360e`** |
| `records[0].correction_requested` | `False` | **no — added at `c5c360e`** |
| `recovery_criteria_met` | `False`, **not renamed** | yes — renamed only at `b24cfefe` |
| any non-quotability `label` field | **absent** | added only at `b24cfefe` |

So the report's schema excludes `948e2b07` from below and `b24cfefe` from above, and the timeline excludes
`ee269b09`. **Arm 0 ran `253f25c0`.** Independently consistent: the authorization measured `253f25c0` as
the cluster copy, deliberately withheld while `_4`/`_5` were pending.

**`253f25c0` appears in exactly one tracked file** — the authorization — and there it is recorded as *the
stale copy to be replaced*, not as *the digest arm 0 ran*. **This finding is the first place that linkage
is written down.**

## 3. The two arms ran DIFFERENT instrumentation versions, and `VL138` survives it — measured

Arm 0 ran `253f25c0`; arm 1 ran `ee269b09`. **`VL138` is a contrast between them.**

`git diff c5c360e 4e85f0e` on the wrapper is **one hunk, 21 insertions, 1 deletion**, and every changed
line sits inside the `if correct:` block at `:141` — the dtype-preserving repair of `BEN-314`. **Arm 0
runs with `correct=False` and never enters that branch**, so on arm 0's execution path the two versions
are behaviourally identical.

**`VL138` is therefore not confounded by the version split.** That conclusion is now established; before
this finding it was neither established nor noticed, and it is exactly the shape that would have been
assumed correctly and cheaply — which is not the same as checked.

## 4. STILL OPEN: no receipt attests that the anneal took effect

All six runs were launched `--annealed` (`sbatch_foldforward_instrumented_closure.sh:157`) and the
composition is real: `closure_foldforward_instrumented.py:303-308` calls
`cpa.install_annealed_multifold()` and layers the recorder on top of the returned class.

**But the LR evidence is discarded.** `install_annealed_multifold()` returns
`(AnnealedMultiFold, fit_lr_records)`; the wrapper binds `lr_records` and never uses it except to write

```python
if lr_records is not None:
    rep["fold_forward_composed_with_annealed_arm"] = True
```

**That boolean records that the install function was CALLED. It does not record that any learning rate
changed** — it is `True` even if `fit_lr_records` is empty, which is the state
`closure_powered_annealed_lr.py:114-115` exists to fail closed on:

> `raise SystemExit("[annealed] no fit-time LR records: the interception never fired (fail closed)")`

`assert_anneal_took_effect` is called only from that module's own `main()` (`:178`), which the wrapper
bypasses by design — it drives `cpt.main` instead. **So the one guard that could distinguish an annealed
run from an un-annealed one is present in the tree, wired into a path these six runs did not take.**
`BEN-312`'s family exactly: an assertion that looks like verification, satisfied by the thing it should
have caught. Measured consequences:

- **no `lr_proof` in any of the six receipts** — the only anneal-related key is that boolean;
- **no `[annealed] LR pattern VERIFIED` line in any of the six logs** — the only matches for
  `anneal|learning` across all twelve `.out`/`.err` files are the word "annealed" inside the `G0` line;
- **no test covers it** — none of the 29 tests in `test_closure_foldforward_recording.py` exercises the
  annealed composition, so the interception is not proven by the suite either.

### What bounds it, short of attesting it

**The band `VL136` passes against comes from runs whose anneal WAS proven.**
`state/annealed-shape-r2-terminal-56552326.json` carries `anneal_lr_proof: pass = True`, *"two fits at
9.999999747378752e-05"* for iteration 0 and *"four fits at 9.999999747378752e-06"* for iterations 1-2,
`records = 6` — the expected count at `niter=3`, two fits per iteration.

Against that run, arm 0 shows `h_prior`, `h_target` and `h_untilted` **bit-identical** (max abs cell
difference `0.0`), and its recovery mean sits **`0.535` declared draw-sd** from the three-run mean, inside
a band `1.557e-03` wide.

**So an un-annealed arm 0 would have had to land inside a narrow band set by proven-annealed runs by
coincidence.** That makes a wrong configuration unlikely and it is the right reason to keep reading the
numbers. **It is not attestation, and it must not be recorded as one:** the static spectra are bit-identical
because the *inputs and injection* match, which is independent of the learning rate, so the only quantity
carrying LR information in that comparison is the one with draw scatter.

**Disposition: a PROVENANCE gap, not a suspicion of a wrong configuration.** The claim "these runs were
annealed" currently rests on a boolean recording that a function was called.

## 5. The fix, not done and not authorized

**Two lines** in the wrapper, not one — `base_lr` is not a constant the wrapper holds. The module's own
`main()` derives it from the records at `:177`, `base_lr = max(r["learning_rate"] for r in lr_records)`,
then calls `assert_anneal_took_effect(lr_records, base_lr, start=0)` at `:178` and merges the return at
`:234`. The wrapper can do the same, plus a test that the interception survives the recorder being layered
on top.

**And the repair is weaker than it looks, which is worth knowing before it is scoped.** Deriving `base_lr`
from the records makes the assertion **partly self-referential**: it would catch an empty record list (the
interception never firing) and a wrong *pattern* — a fit at the base rate where the anneal was intended, or
the reverse — but it **cannot** catch a globally wrong learning rate, because whatever the highest observed
rate turns out to be becomes the standard the rest are judged against. `ANNEALED_LR = 1e-5` at `:47` is a
literal and is checked; the base rate is not. **That is still a large improvement over a boolean, and
naming its limit now is cheaper than discovering it in the receipt that claims closure.**

**Not implemented here.** The wrapper is pinned by the launcher's `G0` and a code change is a change to a
configuration whose six products are in the ledger; that is the mediator's and Joseph's call, not this
lane's. **It does not retro-attest the six runs either** — nothing can, short of a rerun.

## 6. The transferable part, and it is about the copy I was authorized to make

**The only direct evidence of arm 0's instrumentation version was the file on `/pscratch`, and the
authorized arm-1 resubmit overwrote it.** That copy was required by the authorization, the copy order was
the binding condition, and executing it was correct. **It also destroyed the last direct witness to what
arm 0 ran.**

It survives only because the digest was measured and written down in passing — the interlock
demonstration printed `253f25c0…` in its refusal message, and that landed in the authorization document.
**That was a by-product of testing the gate, not a decision to preserve provenance**, and if the copy had
been done in one clean step, as the "copy both" row of the authorization's own table recommends, the
digest would have gone unrecorded.

> **RULE: before overwriting any file on the cluster that a completed run's provenance depends on, record
> its digest in the same turn. A launcher that does not pin a file makes every later copy of that file a
> destructive act, and the run's own logs will not tell you what it ran.**

The general form is worse than the instance: **`G0`'s pin set defines what a run can prove about itself
after the fact**, so a file added to the pin map later leaves every earlier run permanently unattested on
that axis, and the earlier runs are exactly the ones already published.

## 7. Cross-reference

- `BEN-312` — an assertion that names its method and not its target. §4 is that shape: a boolean that
  names the composition and not the learning rate.
- `BEN-314` — the dtype defect whose repair is the single hunk in §3, and a suite that could not fail on
  the interface it protected. §4's "no test covers the annealed composition" is the same gap, still open.
- `BEN-315` — a claim about code inferred from structure. §3's conclusion could have been reached by
  assuming the diff was confined to `if correct:`; it is filed here because it was **diffed**.
- `BEN-077` — a receipt ships its ingredients. §4's boolean is an ingredient-free claim.
- `OI-125` — narrowed by `VL134`, and unaffected by any of this.
