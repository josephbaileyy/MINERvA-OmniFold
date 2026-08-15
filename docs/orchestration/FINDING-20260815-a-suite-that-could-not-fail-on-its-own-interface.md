# A test suite that could not fail on the interface it existed to protect

**Filed 2026-08-15 by the executor lane** (block `310-319`). Row: `BEN-314`. Cost: job `57012031_3`,
`FAILED 1:0` at `00:02:05`, plus tasks `_4`/`_5` which will fail identically. Arm 0 (`_0`/`_1`/`_2`)
unaffected and healthy — see §5.

---

## 1. What happened

`closure_foldforward_instrumented.py`'s arm 1 rescales the engine's `weights_push` by a scalar
`R / ratio`. I wrote:

```python
self.weights_push = np.asarray(self.weights_push, np.float64) * factor
```

`weights_push` is **float32** (`omnifold.py:164,168`). The engine packs it into column 1 of `y_true`
(`omnifold.py:360`, `np.stack`), and `net.weighted_binary_crossentropy:13` does
`weights * tf.nn.sigmoid_cross_entropy_with_logits(...)` against **float32** logits. So it died inside
a `tf.function`:

```
TypeError: Input 'y' of 'Mul' Op has type float64 that does not match type float32 of argument 'x'
```

in **ITERATION 1 / RUNNING STEP 1** — the first point at which the corrected weights meet the loss.

## 2. The finding, which is not "add a cast"

**Eighteen tests passed. Both arm-1 guards were power-tested by mutation. None of them could have
caught this.**

They tested the correction's **arithmetic** against fixtures — scalar not per-cell, applied before
delegation, ratio equals `R` afterwards — and every one of those properties was in fact correct. The
defect was in the **interface**: the dtype of the object handed *back* to the engine.

> **A test suite that exercises your code without exercising the collaborator your code feeds cannot
> fail on a contract violation at that boundary.** Mutation testing does not rescue it either: I
> mutated the correction three ways and each mutation was caught, which measured the guards against
> *the arithmetic* and said nothing about the boundary the arithmetic's output crosses.

This is distinct from `BEN-310` (a measurement that could not move) and from `BEN-119` (a power test
covering the inputs rather than the evidence class). The axis here is **who else consumes your
output**, and the test for it is: *name the next function that touches this object, and call it.*

## 3. The aggravating detail: the trap was already written down

`closure_powered_truth_reweight.py`'s own docstring — the driver this module wraps, which I had read
and quoted the same day — says:

> **FLOAT32 INTO THE ENGINE.** `net.weighted_binary_crossentropy` does
> `weights * tf.nn.sigmoid_cross_entropy_with_logits(...)`, and the logits are float32, so a float64
> weight array dies inside a `tf.function` with `Input 'y' of 'Mul' Op has type float64` — a traceback
> that names Keras internals and not the caller. Measured on the first GPU smoke, 2026-08-05.

That driver even **fails closed** on the dtype of the two loader weight arrays. **Nothing checked
`weights_push`**, because it is engine-internal and until this module nothing outside the engine had
ever written to it. **This module is the first writer, so it is the first place the existing guard's
coverage gap could bite.** A documented trap plus a guard that covers the neighbouring object is
exactly the configuration in which a careful reader still walks in.

## 4. The remedy, in its executable form

Three tests, and the middle one is the transferable pattern:

| test | what it does |
|---|---|
| `test_correction_preserves_the_engine_weight_dtype` | asserts float32 survives the correction |
| `test_correction_preserves_whatever_dtype_it_was_given` | the general contract — *do not change it* — over float32 **and** float64, so it is not a hardcoded constant |
| **`test_corrected_weights_survive_the_ENGINES_OWN_loss`** | packs exactly as `omnifold.py:360` does and calls `net.weighted_binary_crossentropy`. **Not a fixture: the engine function whose `Mul` raised, with the array this module actually produces.** |
| `test_the_loss_really_does_reject_float64_so_the_test_above_has_power` | the loss genuinely refuses float64 — without this the test above could pass by the loss accepting anything |

And a fail-closed check at the point of correction, so a future edit that reintroduces the promotion
dies with a caller-named message instead of a Keras traceback.

**Power verified by re-introducing the exact original bug:** `8` tests turn red, including
`…survive_the_ENGINES_OWN_loss` and both dtype tests. The other two mutations (per-cell factor,
correction after delegation) still turn `7` and `4` red respectively, so nothing was weakened.

**Note on the tolerances**, because loosening one to make a test pass is its own defect (`BEN-072`).
Preserving float32 means the corrected ratio is exact only to float32 epsilon (`1.19e-07`; measured
deviation `1.4e-08`), so three assertions moved from `places=10` to `< 1e-6`. **The tolerance is set by
the representation, not by what passes** — a per-cell or mis-ordered correction deviates by
`O(0.1–1)`, and both mutations were re-run after the change to confirm the guards still fire.

## 5. What is NOT affected, stated plainly because "the array is failing" is the sentence that travels

**Arm 0 never applies the factor, and arm 0 is the run's primary product.** Tasks `_0`/`_1`/`_2` were
`RUNNING` at 30 / 29 / 11 minutes with task 0 already through iteration 1 step 2, and they are the half
that closes `OI-125` and supplies `OI-71`'s G4 recovery evaluation. **Only arm 1 is broken.**

Also validated *by* this failure: the traceback runs through `closure_powered_annealed_lr.py:105
RunModel`, which proves the composition works — the annealed subclass **is** in the MRO, so
`recorder → annealed → engine` is real and not merely intended. And the launcher's exit-code
discipline held: `FATAL: driver exited 1, which is neither 0 nor the declared 3`.

## 6. Two procedural notes

**I did not resubmit.** Arm 1 is 5.9 GPU-hours and Joseph's authorization was for one submission of a
specified design; a resubmit after a code change is a new submission and goes back to him.

**I deliberately did NOT copy the fixed file to the cluster while `_4` and `_5` were PENDING.** They
would then have started against different wrapper code than `_3` ran — two tasks of one array on two
code versions, with the array id as their only shared provenance and nothing in either receipt saying
which code produced it. The launcher's `G0` would not have caught it: `G0` pins the driver, the annealed
wrapper and the engine, **not this module.** Letting `_4`/`_5` fail as `_3` did costs ~4 minutes of GPU
and buys a consistent record. **That gap is worth closing** — a future version of this launcher should
pin the wrapper's own digest too, which is the same lesson as `BEN-312` one layer out: the thing that
verifies a run should name every object the run's behaviour depends on.

## 7. My own near-miss, recorded because it nearly cost the fix

Reverting the three mutations with `git checkout -- <file>` restored the file from the index — **wiping
the uncommitted fix along with the mutation.** Caught immediately because the dtype tests went red on
the next run. **On a file with uncommitted work, revert a mutation by reversing the exact edit, not by
`git checkout`** — and the reason the loss was visible at all is that a test existed for the thing that
was lost.
