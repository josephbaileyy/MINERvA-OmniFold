# Overflow-representation experiment: specification

**CITABLE FOR:** the predeclared design of a synthetic overflow contrast, and the
measured semantics of the pinned upstream cap/aggregation code.
**NOT CITABLE FOR:** any learning result, any routing conclusion, any real-data or
publication adoption, any statement that one representation is better. No overflow
learning result exists at the time this file is written, by construction.

This specification is written and bound **before** any overflow learning result is
produced, as required by
[the continuation authorization](BEN_COMPARISON_AUTHORIZATION-20260915.md)
("must bind the upstream aggregation implementation, its cap semantics, a
high-multiplicity synthetic fixture, full/truncated/aggregate arms, common
initialization and training, declared targets, seeds, controls, acceptance criteria
and resource estimate before reading learning results").

It does not authorize itself. Execution additionally requires the calibration
resource gate to have passed and measured remaining headroom under the common
grant, and it must not shrink or replace the frozen 24-job primary matrix.

## 1. Why the primary matrix cannot answer this question

`nd-unfolding/pet/run_typed_token_comparison.py::make_fixture` builds **exactly four
objects per event** — one photon, one blob, two prongs — for every row, with fixed
per-object fields. The entire learnable conditional is injected as the two prongs'
`time` fields (`reco[row, 0]`, `reco[row, 1]`); every other typed field is the
constant `1.0`, and the event/generic blocks are independent noise with no access to
that conditional.

Therefore any cap `N >= 4` never binds and every arm is byte-identical, while a cap
`N < 4` deletes the signal-carrying prongs outright. The primary matrix measures
*routing under fixed information*; the overflow question is a *membership* question
decided before tokens reach attention. They are different experiments and this one
requires a new fixture.

## 2. Bound upstream semantics (measured, not paraphrased)

Pin `78ebc0d6af04a5b6ab8114a9560dcc9c2a0b99bb` of `gregorkrz/minerva-ml`. The three
files already recorded in [external-source-check.json](external-source-check.json)
were re-fetched and verified byte-identical to those recorded digests:

| file | recorded & measured sha256 | bytes |
|---|---|---|
| `src/dataset/preprocessing.py` | `8348a5d7ee6beec68f0a22a6e85830db6f988eb95edd76b5ac7394f6909d5880` | 35170 |
| `src/models/omnilearned/network.py` | `50162ae09fdc6e08ec2cdaa0ef24fc60c0e1f01e55206befebdbd224f065feea` | 21770 |
| `src/dataset/dataloader.py` | `55546b9a4681600c14cb021fdd22bff885a7004bc1f97acd4935a50f151a20e4` | 31098 |

Both endpoints are named: the digests recorded in this repository on 11 September and
the bytes served by `raw.githubusercontent.com` at that pin on 15 September agree.
This binds the *code*; it attests nothing about which configuration produced the
paper's runs, which remains unbound.

### 2.1 There are two mutually exclusive mechanisms, and aggregation is not the default

In `preprocessing.py`, the signature defaults are `max_objects=150`, `max_blobs=-1`,
`max_prongs=-1`. The two paths are selected as follows.

**Default path — energy-ordered truncation.** When `len(event_features) > max_objects
and max_blobs == -1 and max_prongs == -1`, all objects in the event are sorted by
`event_features[:, 3]` descending and only the top `max_objects` are kept. The
discarded objects are dropped from the token sequence *and* from the per-PID
energy-sum globals, because those sums are computed from `event_features` after the
truncation. Energy and multiplicity in the discarded tail are lost.

**Opt-in path — per-family aggregate overflow.** When `max_blobs > 0` *and*
`max_prongs > 0`, `max_objects` is ignored and each family is passed through
`aggregate_low_energy_blobs_from_four_momentum` with `n_keep=max_blobs`
(`aggregate_pid=6`) and `n_keep=max_prongs` (`aggregate_pid=7`) respectively.

So "Gregor's aggregate-overflow setup" is a **non-default, opt-in** configuration of
the pinned code. The pinned default is truncation. Our own implementation applies no
cap at all. Any report sentence that contrasts "ours" with "Gregor's" must say which
of his two paths it means.

### 2.2 Measured behaviour of the aggregation function

The function was extracted from the verified bytes and executed directly:

| n_objects | n_keep | output tokens | docstring predicts | ΣE in → out | aggregate PID present |
|---:|---:|---:|---:|---|---|
| 5 | 20 | 5 | 5 | 15.0 → 15.0 | no |
| 19 | 20 | 19 | 19 | 190.0 → 190.0 | no |
| 20 | 20 | 20 | 20 | 210.0 → 210.0 | no |
| 21 | 20 | **20** | **21** | 231.0 → 231.0 | yes |
| 30 | 20 | **20** | **21** | 465.0 → 465.0 | yes |
| 90 | 20 | **20** | **21** | 4095.0 → 4095.0 | yes |
| 21 | 5 | **5** | **6** | 231.0 → 231.0 | yes |

Four properties follow, and the experiment is designed around them:

1. **The docstring is off by one.** It claims a return of `min(n_keep+1, n_blobs)`,
   but when the cap binds the code keeps `n_keep - 1` objects individually plus one
   aggregate, returning exactly `n_keep`. The call-site `assert ... <= max_blobs` is
   what the code actually guarantees. Implement the code, not the docstring.
2. **Aggregation conserves total four-momentum exactly** (ΣE identical in every
   row above); truncation does not. This is the aggregate arm's core advantage and
   the sharpest prediction to test.
3. **The merged auxiliary block is a MEAN, not a sum.** `[dE/dx, x, y, z, t]` of the
   aggregate equals the arithmetic mean over the merged tail; verified numerically
   against `info[19:].mean(axis=0)`. So extensive information survives only in the
   four-momentum, while position/timing survive only as a centroid.
4. **Multiplicity leaves no explicit trace.** There is no count feature for how many
   objects were merged: 21, 30 and 90 objects all yield exactly 20 tokens. Tail
   multiplicity is recoverable only indirectly through the summed energy.

A fifth, minor fragility, recorded but not exercised: the function's signature
default is `aggregate_pid=7`, which is the *prong* aggregate code, so a future call
that omits the argument for blobs would silently label them as aggregated prongs.
Both present call sites pass the argument explicitly, so the pinned code is correct.

### 2.3 How to re-derive §2.2, and how far its controls reach

The table above is reproducible, not transcribed.
[verify_upstream_overflow_semantics.py](verify_upstream_overflow_semantics.py)
verifies the supplied file against the digest bound in
[external-source-check.json](external-source-check.json), then executes the upstream
function and asserts the six properties; the receipt is at
[local_validation/20260915-overflow-spec/upstream-semantics.json](local_validation/20260915-overflow-spec/upstream-semantics.json)
with verdict `UPSTREAM-SEMANTICS-AS-SPECIFIED`. Upstream code is not vendored, so the
operator supplies it and the probe refuses bytes that miss the digest, writing no
receipt when it refuses.

An assertion no mutation can break is untested rather than proven, so
[test_upstream_overflow_semantics.py](test_upstream_overflow_semantics.py) mutates the
upstream function and requires the targeted property to fail. The mutants are handed
directly to `measure`, bypassing the digest gate, because a mutant routed through that
gate is refused as a digest mismatch and never reaches the assertion under test.

Coverage, stated exactly: **five of the six properties are mutation-killed** —
`binding_output_equals_n_keep` and `docstring_is_off_by_one_when_binding` by removing
the `n_keep - 1` slice, `auxiliary_aggregate_is_tail_mean` by summing instead of
averaging the merged block, `total_energy_conserved` by averaging instead of summing
the merged four-momentum, and `inert_below_cap` by disabling both below-cap early
returns. `multiplicity_collapses_to_one_width` is **not independently killed**: it is
implied by `binding_output_equals_n_keep`, since a constant output width follows from
the output always equalling a fixed `n_keep`. It is therefore a derived restatement,
not an independent check, and must not be cited as one. Six tests pass with the
upstream file supplied and skip — not fail — without it.

Black, Ruff and strict mypy with `--platform linux` pass on both new files. The
formatter and linter were first run against already-accepted files in this directory
as a positive control, so their verdict on the new files reflects this repository's
style rather than a tool-version disagreement.

## 3. Arms

Three arms, applied as a membership transform *before* tokenization, with the
`direct` (individual-token) routing held fixed in all three. Routing is not varied
here; that is the primary matrix's variable.

| arm | transform at cap `N` |
|---|---|
| `full` | no cap; every object retained individually (our current behaviour) |
| `truncate` | upstream default: energy-sort descending, keep top `N`, drop the rest |
| `aggregate` | upstream opt-in: energy-sort descending, keep top `N-1`, append one token whose four-momentum is the **sum** and whose auxiliary block is the **mean** of the merged tail, with a distinct aggregate type code |

`full` is the information-preserving reference. `truncate` and `aggregate` must
reproduce the measured upstream semantics of §2.2 exactly, including the off-by-one
and the sum/mean split, and a unit test must pin each of those four properties
against the extracted upstream function.

## 4. The fixture, and the choice that must not be hidden

The result depends entirely on **where the signal sits relative to the energy
ordering**, because upstream always keeps the highest-energy objects and discards or
merges the low-energy tail. Choosing one signal placement would choose the answer.
So placement is a declared, varied factor with three regimes, and the result is
reported as a function of regime rather than as a single verdict.

Fixture: `rows` events; per event, object multiplicity drawn from a declared
distribution with a heavy tail so that the cap genuinely binds on a controlled
fraction of events (target: cap binds on ~50% of events, recorded exactly, never
tuned after seeing a score). Each object carries an energy field that defines the
ordering and a payload field that carries signal. Non-signal fields stay constant or
noise, as in the primary fixture.

| regime | target depends on | prediction |
|---|---|---|
| `R1` tail-extensive | the **sum** of the payload over the low-energy tail | `truncate` fails; `aggregate` largely recovers, because the summed four-momentum preserves the extensive quantity; `full` best or equal |
| `R2` tail-resolved | a **non-additive** function of the tail (per-object dispersion / extremum) | `truncate` fails; `aggregate` only partially recovers, because a sum plus a centroid cannot express it; `full` best |
| `R3` head-only (**negative control**) | only the top-`k` highest-energy objects, `k < N-1` | **all three arms tie** |

`R3` is load-bearing. Without it, a "`full` wins" result is indistinguishable from a
fixture rigged to punish any cap. `R3` is the direction-opposite control: it must
show the guard staying silent when the cap is harmless. If `R3` does **not** tie, the
fixture is invalid and no `R1`/`R2` conclusion may be reported.

The predictions above are predeclared hypotheses. They are recorded so that a result
matching them is not retrofitted and a result contradicting them cannot be quietly
reinterpreted; they are not evidence.

## 5. Common footing, seeds, controls

- Shared initialization: within a (regime, seed) cell all three arms are built from
  one construction sequence and must report identical parameter counts and identical
  initial-weight digests, verified as the primary matrix already verifies
  `parameters`, `initial_reco_sha256`, `initial_truth_sha256`.
- Shared training budget: identical rows, iterations, epochs per fit, batch size and
  optimizer across arms. Only the membership transform differs.
- Shared truth network and normalization: one frozen normalization; arms must report
  a common `code_sha256` / `truth_sha256` / `normalization_sha256` footing.
- Seeds: `17, 29, 43` per regime — three paired seeds, deliberately fewer than the
  primary matrix's eight, because this is a directional diagnostic and the budget is
  a remainder. Paired differences only; no cross-regime pooling.
- Controls, all required: (a) `R3` tie; (b) a cap `N` larger than every event's
  multiplicity must make all three arms numerically identical, proving the transform
  is inert when it does not bind; (c) the measured fraction of cap-binding events is
  recorded per regime; (d) an arm-label shuffle must destroy any claimed separation.
- Precision and determinism follow the bound `PRECISION_POLICY` unchanged.

## 6. Acceptance criteria

Per regime, over the three paired seeds, on the injected closure metric already used
by the primary reduction (`log_ratio_rmse` at the final iteration):

- **Validity gate (must pass first, else report nothing):** control (b) exact-identity
  holds; `R3` shows no arm separated by more than the seed spread; the recorded
  cap-binding fraction is non-zero in `R1`/`R2`.
- **Separation is reportable** for a pair of arms in a regime only if the paired
  difference has the same sign in all three seeds *and* its magnitude exceeds the
  within-arm seed spread. With three seeds this is a **directional** statement; no
  confidence interval and no significance is claimed, and the frozen primary
  criteria (`>5%` lower bound, `>=7/8` favourable seeds) are **not** reused here
  because three seeds cannot support them.
- Any other outcome is reported as **inconclusive**, which is not evidence that the
  representations are equivalent.
- A technical failure stops the remaining cells, preserves partial evidence and is
  reported exactly, with no retry and no seed replacement.

## 7. Resource estimate

Deliberately left as a formula, to be closed with measured numbers, because the
authorization requires a *measured* estimate and the only measurement of per-row cost
for this harness is the calibration allocation that has not yet returned.

Cells: 3 regimes x 3 arms x 3 seeds = **27** runs, each far smaller than a primary
job. Let `s` be calibration's measured per-fit second-per-row scaling from
[evaluate_calibration.py](evaluate_calibration.py) and `r` the chosen overflow rows.
The estimate is `27 * (fit + inference + overhead)(r)` extrapolated by the same
upper batch-count method that file already implements, plus its storage analogue.

Binding constraints, all of which must be satisfied by measured numbers before any
overflow compute is requested:

- It runs only from the headroom **remaining after** the frozen 24-job matrix is
  accounted for, inside the unchanged aggregate ceilings of 290 GPU-hours, 9,296
  reserved CPU-hours including the 16-hour preparation allowance, and 200 GiB.
- `rows` is chosen as the largest value that fits that measured remainder with the
  same 20% headroom margin, then frozen before execution.
- If the measured remainder cannot fund all 27 cells with that margin, the reduction
  is to **drop whole regimes in the order `R2`, then `R1`**, never to weaken a
  criterion, drop the `R3` control, or reduce seeds below three.
- No overflow compute is submitted while any primary-matrix allocation is queued or
  running; the grant forbids simultaneous PET allocations.

## 8. What this experiment cannot establish

It is synthetic. It measures whether a summed-plus-averaged overflow token recovers
what an energy-ordered cap discards, in a fixture whose signal placement we chose and
declared. It cannot establish a real-data representation winner, cannot supply a
publication adoption, covariance, statistical pairing or coverage claim, and cannot
resolve the outstanding source-semantic prerequisites — the photon/blob meaning and
calibration, prong hypotheses, shared objects and primary lepton, and the exact tuple
release and time range — which remain unresolved and are unaffected by any result
here. It also cannot bind which configuration produced the upstream paper's runs;
§2 binds the code, not the run.
