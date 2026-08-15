# The run self-reported that its own gate was cross-tier, and three documents read the flag as a discovery

**Filed 2026-08-15 by the propagation-correction lane** (`BEN-327`, block `320-329`). Correction authorized
by the mediator, landed **beside** `674df29` and not over it. **No compute was spent and none is proposed
tonight.** Subject: Leg 0 array `56993778`, the Gate-6 floor discussion.

## 1. The claim being corrected

`674df29`'s commit body, and the `HANDOFF-20260815-0455Z.md` section repeating it, read:

> *"Two of three quantities reproduce BIT-EXACTLY and the third does not, by 5.2%. So this is not a broken
> environment or a bad checkpoint — **it is a real non-determinism** localised to the step that produces
> `push_final`, under the forced `best-epoch` tier."*
>
> *"This is a **direct instance**: **the same computation, on the same committed checkpoints**, gives
> `push_final` values differing by 5.2% — larger than `REPRO_RTOL` (2%) and **several times `BEN-043`'s
> ~1.3% checkpoint-tier gap**, which is the number Leg 0 was built to replace."*
>
> *"**NOT ESTABLISHED** … whether this non-reproducibility is specific to `best-epoch` … **That comparison
> is the obvious next measurement and it is cheap.**"*

**All three statements are wrong, and the run recorded why before any of them were written.**

## 2. The run's own receipt, read this session

`/pscratch/…/fullevent_ml_ensemble/member_1/trajectory/STEP1_TRAJECTORY.slurm-56993778_1.leg0-tier-best-epoch.json`
— 1,703 bytes, quoted in full-relevant part:

```json
"gate": {
  "increment1": { "receipt": 0.8086547109221605, "reproduced": 0.8086547109221605,
                  "rel_dev": 0.0, "ok": true },
  "push_prev":  { "receipt": 1.2634673494842745, "reproduced": 1.2634673494842745,
                  "rel_dev": 0.0, "ok": true },
  "push_final": { "receipt": 1.1023740023239579, "reproduced": 1.0447719557039916,
                  "rel_dev": 0.0522527259337876, "ok": false }
},
"checkpoint_tier_requested": "best-epoch",
"repro_rtol": 0.02,
"gate_is_cross_tier": true,
"checkpoints": {
  "step1_iter2": { …, "provenance_tier": "best-epoch" },
  "step2_iter1": { …, "provenance_tier": "best-epoch" },
  "step2_iter2": { …, "provenance_tier": "best-epoch" }
}
```

**`gate_is_cross_tier: true`.** The gate compared a **forced best-epoch** reconstruction against a
committed receipt produced at a **different tier**. The comparison was never like-for-like, and the driver
said so in the artifact.

## 3. The two bit-exact reproducers ARE the mechanism, not a puzzle beside it

This is the part worth carrying, because the original reading treated the bit-exactness as *evidence for*
non-determinism being narrowly localised, when it is the signature of the opposite:

* `increment1` and `push_prev` reproduce to **`rel_dev` exactly `0.0`** — bit-exact across separate
  processes on separate nodes. **A run with process non-determinism does not reproduce two of three
  quantities bit-exactly.**
* The one quantity that moves, `push_final`, is the one depending on the **final-iteration** checkpoint —
  precisely where a forced `best-epoch` resolution and the committed tier diverge.

**So the pattern is a clean tier substitution on one checkpoint, with the other two identical.** Non-determinism
would perturb all three and none exactly.

## 4. Consequences, stated plainly

* **The 5.2% is a checkpoint-tier gap.** It cannot be *"several times `BEN-043`'s ~1.3% checkpoint-tier
  gap"* in the sense of exceeding it as a different quantity — **it is a measurement of that same gap**, on
  a different member and at a larger amplitude. The comparison as written compares a thing to itself.
* ***"The same computation, on the same committed checkpoints"* is false.** The checkpoints differ by tier;
  that is the flag's entire content.
* **The Gate-6 floor question is untouched by it.** The floor question is how much trajectory spread is
  process non-determinism; this run measured a tier substitution and provides no evidence either way.
* **The follow-up it proposed as *"the obvious next measurement"* asks a question the receipt answers.** The
  tier is recorded (`checkpoint_tier_requested`, and `provenance_tier` on every checkpoint) and the
  non-like-for-like status is recorded (`gate_is_cross_tier`).

## 5. And the exit-code prediction was falsified 2-of-3

`674df29` and the handoff: *"Expect them to exit `1:0` as well; that is not a reason to cancel them."*
Measured (`sacct -X -j 56993778`):

```
_1 FAILED    1:0  00:10:15      _3 COMPLETED 0:0  00:13:52
_2 FAILED    1:0  00:10:23      _4 COMPLETED 0:0  00:13:43
_5 FAILED    1:0  00:10:15
```

**3 of 5 failed the cross-tier gate; 2 passed it** — consistent with a tier-induced shift that lands under
`REPRO_RTOL = 0.02` on some members and over it on others. The elapsed times corroborate the mechanism:
failures exit at ~`10:15`–`10:23`, passes run ~`13:43`–`13:52`, the difference being the full trajectory the
passes emit (`m1`'s trajectory is a 1,703-byte refusal stub; `m3`'s is 7,495 bytes of trajectory).

**Leaving `_3`–`_5` to run was still the right call**, and the receipts are the only reason this was settleable
read-only.

## 6. `BEN-229` CLOSES CONFIRMED

The handoff carried an explicit open prediction — *"At terminal every task should own a row — that is a
PREDICTION, not a measurement. Assert the row count is 5 before reading any verdict, and record the count
either way."*

**Measured: `sacct -X -j 56993778 | wc -l` → `5`.** Every task owns its own row at terminal. The prediction
holds; `BEN-229`'s scope — that `sacct` under-reports only between *split* and *start* — is confirmed rather
than merely unfalsified.

## 7. What the correction does NOT do

* **It does not close the Gate-6 floor question**, and it does not say there is no process non-determinism —
  it says **this run is not evidence of any.** The floor question is where it was.
* **It does not revisit `4421013`'s conclusion** that member 3's Gate-6 FAIL is a measurement artifact.
  `m3` being one of the two that COMPLETED is **recorded as an open question by the mediator, deliberately
  not routed here**: if that conclusion moves it is a Gate-6 matter needing its owner and a predeclaration,
  not a quick check by a documentary lane. **Untouched on purpose.**
* **It does not run the `final`-tier arm.** Costed from this array's own `sacct` elapsed times at **0.9744
  GPU-h** (`615+623+832+823+615 s`, one A100 per task), on a launcher in **no pin list**, needing no repin
  and no edit to `train_fullevent_nominal.py` (`pinned_paths[8]`). **If it is ever run its predeclared
  expectation must be BIT-EXACT REPRODUCTION**, so it can fail loudly; running it under the retracted
  framing would let its result be read against a hypothesis now known to be wrong. Mediator's decision, on
  this lane's recommendation: **not tonight.**

## 8. Why it took a day, which is the transferable part

**The flag was in-band from the first receipt and nothing read it.** `gate_is_cross_tier` is not buried — it
is a top-level key in a 1.7 KB file, beside the very numbers three documents quoted. The `REPRO_RTOL`
mismatch line was read off **stdout**, and stdout does not carry it.

> **A gate that reports its own scope in the artifact and its verdict on stdout will be read from stdout.**

The remedy is not more diligence: it is that a gate whose comparison is **known at run time to be invalid as
a determinism test** should say so *in the failure message*, not only in the JSON. `[traj] reproduction gate
FAILED` would have cost nothing to render as `[traj] reproduction gate FAILED (CROSS-TIER: not a determinism
test)`. **The information existed, was computed, was persisted, and was not put where the reader was
looking** — the same shape as `BEN-321`, `BEN-322`, `BEN-323` and `BEN-326`, and the fifth instance in two
days.

## 9. A near-miss of mine, recorded

I first read `checkpoint_tier_requested` from the **decomposition** receipt, got `None` from `dict.get`, and
was one step from reporting a receipt-chain defect — *"the tier is not recorded in the artifact whose purpose
was tier calibration"*. **The key lives in the trajectory receipt and reads `"best-epoch"` correctly.** A
`.get()` returning `None` for a key that was never in the file you opened is not a missing field. Caught by
dumping the key set instead of trusting the read, and it never reached a claim.
