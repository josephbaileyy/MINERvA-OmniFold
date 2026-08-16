# A power test licenses ONE axis — and this fixture is numerically degenerate on the axis that matters

**`BEN-342`.** Peer session `B`, 2026-08-16, from the mediator's read of `67c94df` — the second
fold-forward instrument, written to close the hole `BEN-360` found in the first, applying `BEN-360`'s own
rule to it. **Read-only: nothing under `nd-unfolding/pet/` was modified.**

**THE INSTRUMENT IS CORRECT. This finding is about its test.** Stated first because the opposite reading
would be expensive: the end-of-run recorder records the like-for-like quantity, verified against the
definition rather than against its own reduction, and the verdict was `RECORDS-THE-RIGHT-QUANTITY`.

## What was checked, and how

`BEN-360`'s rule: *write down the definition of X from the artifact that ALREADY records it, and check the
instrument's output against THAT definition — not against your own reduction, which is guaranteed to agree
with itself.* The definition, from `nd-unfolding/pet/train_fullevent_nominal.py`:

```
:437  of.Unfold()
:553  push        = np.asarray(of.weights_push, dtype=np.float64)      # read AFTER Unfold()
:564  _reco_leg   = getattr(mc, "weight_reco", None)
:565  w_reco_leg  = mc.weight if _reco_leg is None else _reco_leg      # ":575 Step-1 space => reco leg"
:567  pass_reco_sub = np.asarray(mc.pass_reco).astype(bool)
:576  sum_w_push_reco = (w_reco_leg[pass_reco_sub] * push[pass_reco_sub]).sum()
:577  sum_w_reco      = w_reco_leg[pass_reco_sub].sum()
:667  fold_forward_reco_ratio = sum_w_push_reco / sum_w_reco
```

and the instrument's `_ff_reduce`, called from its new `RunStep2` hook, resolves the same leg by the same
rule (`self.mc_weight_reco` falling back to `self.mc.weight`, matching `omnifold.py:157-159`), reads
`self.weights_push` after `super().RunStep2(niter-1)`, masks by `self.mc.pass_reco`, and forms the same
quotient. **Timing holds too:** the loop is `RunStep1(i); RunStep2(i); CompileModels(fixed=True)`
(`omnifold.py:172-177`); `CompileModels` contains zero `weights_push` references, and the only other
assignment (`:433`) is inside `LoadStart()`, called at `:166` **before** the loop. So the captured array is
the array the driver reads.

## The finding: the bit-identity test cannot see the weight leg

`test_the_final_capture_is_BIT_IDENTICAL_to_what_the_driver_persists` is the load-bearing test, and it is
built the right way — `driver_ratio` is an **independently written** expression of the driver's formula,
applied at the driver's read point, not a call back into the recorder. It is paired with a power control,
`test_THE_ASSERTION_ABOVE_HAS_POWER_a_pre_delegation_capture_FAILS_it`, which shows a wrong-**moment**
capture failing.

**But the fixture's `RunStep2` assigns a UNIFORM push:**

```python
self.weights_push = np.full(self.weights_push.shape[0], 1.0 + 0.1 * (i + 1), dtype=np.float32)
```

and for a uniform push, `Σ(w·push)/Σw = push` **for any weight vector `w`**. Measured on that fixture
(`reco leg [1,2,3,4]`, `truth leg [1,1,1,1]`, `pass_reco [T,T,T,F]`):

| reduction | value |
|---|---|
| recorder's end-of-run row | `1.2999999523162842` |
| driver formula, **reco** leg (correct) | `1.2999999523162842` |
| driver formula, **truth** leg (the wrong one) | `1.2999999523162842` |

**Bit-identical. So the assertion would pass unchanged if `_ff_reduce` had used `mc.weight` instead of
`mc_weight_reco`.** The test has power over the moment and **none over the leg.**

**That is the axis this codebase already gets wrong.** `omnifold.py:189` uses the reco leg while `:209`
carries the comment *"TRUTH leg — deliberately `self.mc.weight`, NOT `self.mc_weight_reco`"*, and
`train_fullevent_nominal.py:575` needs *"Step-1 space => reco leg"* written down to keep them apart. A
leg substitution is the most likely way this instrument could have been wrong, and it is the one thing the
test cannot detect.

**The fix is one line and it is measured, not proposed.** Make the fixture push non-uniform — e.g.
`1.0 + 0.1*(i+1) + 0.01*np.arange(n)`:

| reduction | uniform push (as-is) | non-uniform push |
|---|---|---|
| reco leg | `1.3000000000` | `1.3133333333` |
| truth leg | `1.3000000000` | `1.3100000000` |
| legs distinguishable | **no** | **yes** |

**This is UNEXERCISED, not wrong.** The instrument uses the right leg; the test simply cannot tell. No
number in any artifact is affected.

## Rule

**`BEN-314` asks whether a test CAN fail. That is necessary and it is not sufficient — a single power
control licenses exactly the axis it perturbs and is silent on every other.** Here one control proves the
assertion catches a wrong *moment*, and a reader who sees "power-tested" reasonably concludes the
assertion is load-bearing in general. It is not.

1. **Enumerate the plausible-but-wrong variants before building the fixture** — wrong moment, wrong leg,
   wrong mask, wrong normalisation — and for each, ask whether the fixture's *numbers* would differ.
2. **Check the fixture's VALUES for degeneracy on each axis, not just the assertions for coverage.** A
   fixture whose numbers coincide under two different definitions cannot distinguish them however many
   assertions are added on top. Degenerate inputs — all-ones weights, uniform arrays, symmetric masks —
   are the usual cause, and they are chosen precisely because they make the arithmetic easy to read.
3. **Name the axis a control covers when claiming power.** *"Power-tested"* unqualified invites the
   generalisation this finding is about; *"power-tested against a wrong-moment capture"* does not.

## Second, smaller: an amplitude that does not re-derive (`BEN-361`'s shape)

The claim *"a ~105-draw-sd 'disagreement'"* appears in **three** places — the instrument at `:196` and
`:561`, and the test at `:564` — and does **not** re-derive from the operands the predeclaration supplies.
`PREDECLARATION-20260816-endofrun-push-recording.md:48` states `VL134`'s arm-0 3-draw mean
`1.010878613` with `sd 0.000399`. From the two quoted values:

```
gap                  0.981165 - 1.011418 = -0.030253
gap / sd             0.030253 / 0.000399 =  75.8 draw-sd
gap / (sd/sqrt(3))                       = 131.3
sd that would give 105                   =   0.000288   (stated nowhere)
```

**So `~105` matches neither plausible normalisation.** What *does* re-derive: the predeclaration's own
`E4` amplitude — *"differ … by roughly `-3%`"* — is **`-2.991%`**, correct; and the sign-flip claim is
true (`-0.018835` against `+0.011418`). **The un-derivable figure is in the code docstrings, not in the
predeclaration**, which is worth separating: the predeclared claim survived `BEN-361`'s check and the
prose around it did not.

**Related:** `BEN-360` (the rule applied here, and the reason this read happened), `BEN-314` (the
necessary-not-sufficient condition this sharpens), `BEN-361` (the amplitude check), `BEN-077` (why the
two definitions are quoted side by side rather than summarised).
