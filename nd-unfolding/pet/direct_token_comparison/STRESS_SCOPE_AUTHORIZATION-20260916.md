# Gate scope decision: the variable stress case is recorded, not gating

**Decided by Joseph on 16 September 2026**, in reply to the option set presented with
[the D1/D1b measurements](CROSSDEVICE_D1_RESULT-20260915.md). Verbatim:

> Choose option 1 for this frozen synthetic campaign. Keep the variable-case
> discrepancy recorded as a failed stress check, retain every other gate, and verify
> that every production batch uses the covered geometry. This approval does not extend
> to future variable-length or real-source training.
>
> Proceed through the remaining preflight, calibration, and authorized learning
> comparison within the existing resource limits. Don't ask again for this gate
> decision.
>
> My main question is practical: which approach gives better unfolding closure,
> stability, and compute cost on the same task? Finish the controlled token comparison,
> then identify what additional matched comparison is needed to compare our complete
> approach with Gregor's. Keep those conclusions separate, and don't treat numerical
> preflight agreement or information retention alone as evidence of better learning.

The preceding grant, also his, authorized "the diagnostic you recommend, necessary
implementation fixes that preserve the intended comparison, and bounded GPU
validation/calibration within the remaining resource ceilings," reserved scientific
design, acceptance criteria and resource ceilings for him, and stated the endpoint as
"a recommendation supported by matched learning results and compute costs, with
uncertainty and scope stated clearly."

## What changed, exactly

| element | before | after |
|---|---|---|
| `variable/{pooled,direct}` GPU gate | gating; a failure stops the run | **recorded as `FAILED-STRESS`**, does not stop the run |
| every other case/routing pair | gating | **unchanged, still gating** |
| tolerances `atol=1e-5, rtol=1e-4` | — | **unchanged** |
| key-bias exemption | as approved 15 September | **unchanged** |
| production batch geometry | unverified at runtime | **verified on every run** |

Implemented as:

- `amended_preflight.STRESS_ONLY_CASES = ("variable",)` — the exempt set is exactly
  the one case named, and a test pins that tuple.
- The stress case's gate call is wrapped so a failure is *recorded with its error and
  key-bias binding* and the run continues; all of its evidence is still written, so the
  discrepancy stays fully re-derivable rather than disappearing.
- The receipt verdict is `PASS-WITH-RECORDED-STRESS-FAILURE`, not `PASS`, whenever a
  stress case failed. The verdict word carries the result, because a correct caveat
  beside a green word does not survive being read alone.
- `check_stress_consistency` refuses, in both directions: a gated case failing, a
  failure the receipt does not declare, a bare `PASS` hiding a failure, and a stress
  verdict claimed with nothing failing.
- `run_typed_token_comparison.assert_covered_geometry` runs on the train and test
  splits of **every** production job and refuses any departure from the covered
  geometry: non-uniform slots per row, a width other than the validated one, any
  token-level mask, any disabled family, or declared counts disagreeing with packed
  slots. `select_inputs` additionally re-checks its carried slot total.

## Why checking the splits covers every batch

The covered-geometry properties are per-row, and a minibatch is a row subset, so
uniform counts over all rows imply uniform counts over any selection. That argument is
tested directly rather than asserted: a control selects several row subsets, runs them
through `select_inputs`, and requires the guard to pass with zero padded positions.

## Scope, stated as a boundary

This decision covers **this frozen synthetic campaign only**. It does not extend to
variable-length training, to real-source training, or to any future study that
constructs padded batches — in which case the `variable` discrepancy becomes live again
and needs its own decision. It is not a finding that the discrepancy is unimportant;
it is a finding that the frozen matrix never encounters it, verified at runtime.

It also remains true, and is not weakened by this decision, that the cross-device
discrepancy is **not** evidence that individual typed-object tokens are scientifically
worse. It is a float32 reproducibility property of longer attention sequences.

## Validation

- 69 tests + 10 subtests unchanged, and the adversarial gate suite grows from 25 to
  **40** with the 15 new stress-scope and geometry controls; every geometry control is
  built from the real producer and mutated, so a fixture cannot merely agree with the
  guard it tests.
- `evaluate_calibration.py`'s expected count and the coupled fixture in
  `nd-unfolding/tests/test_token_packing_preflight.py` were both updated; the count
  assertion exists in exactly those two places.

## Unchanged boundaries

No real-source reads, normalization or training, publication adoption, covariance,
statistical pairing, coverage claim or Gate-6 action. No producer or mentor messages.
Resource ceilings unchanged: 290 GPU-hours, 9,296 reserved CPU-hours including the
16-hour preparation allowance, 200 GiB. A technical failure stops dependent compute
with no retry and no seed replacement.
