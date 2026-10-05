# Cross-device divergence diagnostic: specification and decision criteria

**CITABLE FOR:** the predeclared design and decision rules of this diagnostic.
**NOT CITABLE FOR:** any result — none exists when this file is written — and for no
representation, learning or adoption conclusion.

Written under the 15 September continuation grant, which authorizes "the diagnostic
you recommend, necessary implementation fixes that preserve the intended comparison,
and bounded GPU validation/calibration within the remaining resource ceilings," and
requires the diagnostic and its criteria to be specified before running it. It also
reserves changes to scientific design, acceptance criteria and resource ceilings for
Joseph.

## The question, stated so it cannot be answered by assumption

Job `58354898` stopped because, in the `variable/direct` case, the attention
`query/kernel` (`weight_24`) diverged between CPU and GPU by `1.443e-04` after one
Adam step and `1.548e-04` after two, against the unchanged `atol=1e-5, rtol=1e-4`.
Three other reached cases stayed within tolerance. See
[the terminal record](AMENDED_RESULT-20260915.md).

**What this does not yet distinguish.** A post-Adam weight difference can arise two
ways, and they have opposite consequences:

1. The forward/backward computation agrees across devices and the difference is Adam
   *amplifying* float32 rounding in a small-gradient coordinate. Adam's step is
   `lr * m̂ / (sqrt(v̂) + eps)`, so for a parameter whose gradient is small the ratio
   of weight difference to gradient difference can be very large. This is the same
   mechanism class already established and approved for the attention key bias.
2. The ragged/padded direct path genuinely computes something different across
   devices — a code-level defect in repacking, masking or reduction.

**Neither reading is evidence that individual typed-object tokens are scientifically
worse.** This is a numerical-reproducibility question about one implementation path.
Learning performance, closure and compute efficiency are measured by the paired
matrix, not here, and nothing in this diagnostic can substitute for them.

## Stage D1 — offline decomposition (no GPU, no allocation)

The amended preflight captures inputs, gradients, optimizer states, updates, four
`replay-{origin}-{device}` combinations and float64 replays *before* its assertions,
so the arrays that decided the failure survived it. D1 reads them back from the
preserved archive
(`local_validation/20260915-amended-failure/pet-amended-failure-20260915.tar.gz`,
SHA-256 `ad27ca25fe774665c93a06c1d66efbfe5b43f11f265c9ded4b39baf6ace0eb7d`, 243 files,
digest verified at both endpoints).

All four reached cases are measured, so the failing case has three passing controls
rather than being examined alone.

| id | measurement |
|---|---|
| M1 | Per-weight CPU-vs-GPU **gradient** agreement at steps 1 and 2 (`eager.npz`, `second.npz`) |
| M2 | **Common-operand Adam replay**: `replay-cpu-cpu` vs `replay-cpu-candidate`, and `replay-candidate-cpu` vs `replay-candidate-candidate`. Identical gradient operands, different device — isolates Adam arithmetic from gradient differences |
| M3 | **float64 bracketing**: does each native trajectory match the float64 replay driven by its own gradients? |
| M4 | **Token geometry**: token-position count and padded fraction per case (`*-tokens.npz`) |
| M5 | **Amplification ratio** per weight: post-Adam weight difference divided by gradient difference |

### Predeclared decision rule

Evaluated in order; the first branch whose condition holds is the verdict.

**Branch C — instrumentation or model problem.** If M3 fails, i.e. a float64 replay
driven by a trajectory's own gradients cannot reproduce that trajectory within the
unchanged tolerance. → **Stop.** Report; do not proceed to any GPU stage. A captured
trajectory we cannot re-derive is not a usable basis for any further inference.

**Branch B — materially different computation.** If M1 shows `weight_24` gradient
disagreement `> 1e-6` absolute at either step, **or** M2 shows any weight or slot
disagreeing by `> 1e-7` under identical operands. → The direct path's forward or
backward computation differs materially across devices, or Adam itself is not
device-stable. This is a probable code defect. → Remedy is an **implementation fix**,
inside the grant.

**Branch A — benign cross-device amplification.** If all of: M1 `weight_24` gradient
agreement `<= 1e-6`; M2 common-operand agreement `<= 1e-7` for every weight and slot;
M3 float64 bracketing holds; and prediction agreement `<= 1e-5` (already measured at
`8.34e-07`). → The computation agrees and the divergence is Adam amplification of
float32 gradient rounding, the established key-bias mechanism appearing in a second
parameter because the direct route sums over many more key positions. → This is **not**
a representation defect and **not** evidence against individual tokens.

Branch A splits by remedy, and the split decides who decides:

- **A-fix (inside the grant).** If M4 shows the divergence tracks the number of token
  positions and padded fraction, an implementation change that makes padded positions
  exactly inert reduces the rounding at its source without altering the intended
  mathematics. Specified as F1 below.
- **A-criteria (Joseph's decision, not mine).** If no implementation fix removes it,
  the only remaining route is to accept a gradient-agreement-plus-replay criterion for
  this parameter in place of raw post-Adam equality. That is a change to **acceptance
  criteria** and is explicitly reserved. I will bring it as a concrete decision with
  measurements rather than applying it.

A monotone relationship in M4 across only four cases is weak evidence and will be
reported as suggestive, not established.

## Candidate implementation fix F1, and its acceptance test

Stated now so it cannot be reverse-engineered from whatever D1 returns.

**Observation to test, not an assumption:** in `typed_token_comparison.route_tokens`
the encoder output is zeroed at inactive slots (`tf.where(active[:, None], projected,
0.0)`), but `call` then applies `self.typed_projection`, a `Dense` **with bias**, to
the assembled cloud. A Dense maps an exactly-zero padded position to its *bias
vector*, not to zero. Padded positions therefore enter attention carrying `bias` and
are suppressed only by `attention_mask`. Masked keys contribute ~0 weight but their
products are still formed and summed, so they add rounding noise that grows with
padded width — and the `query/kernel` gradient is precisely a sum over key positions.

**F1:** apply the token mask again after the typed projection, so padded positions are
exactly zero entering attention.

**F1 is classified as an implementation fix, not a design change,** because padding is
already *defined* as inert — the README states the direct route "never truncates
objects" and padding is a per-batch artifact. F1 makes that definition true
numerically. I am recording this classification explicitly so it can be overruled: if
Joseph reads F1 as a design change, it needs his decision instead.

F1 may be used only if all of these hold, measured on CPU before any GPU stage:

| id | requirement |
|---|---|
| F1a | **Exactly inert where there is no padding.** For cases with uniform multiplicity, outputs, gradients and updated weights are bitwise identical before and after F1 |
| F1b | **Pooled route bitwise unchanged** in every case; pooled has no padding, so any change is a defect in F1 |
| F1c | For variable multiplicity, the CPU prediction change is reported as a measured number. A change far above the attention mask's own numerical floor would mean padding was *materially* affecting results before F1 — itself a defect, which I would report rather than absorb |
| F1d | The intended comparison is preserved: pooled and direct still receive identical information, with identical parameter counts and identical initial weights, verified as the existing gates verify them |
| F1e | The full local suite, including the 25 adversarial gate controls, still passes |

If F1a or F1b fails, F1 is wrong and is discarded rather than patched into passing.

## Stage D2 — bounded GPU validation, only if D1 permits

Runs only under Branch A-fix or Branch B with a fix in hand, and only after F1's
acceptance test passes on CPU.

- One allocation, unchanged profile: 1 A100, 32 reserved CPUs, 56 GiB, eight
  application CPUs, no simultaneous PET allocation, output bounded to 4 GiB.
- Required content: the full guarded suite, the original-sequence CPU initialization
  capture, the amended GPU preflight across **all eight** case/routing pairs, and the
  fresh-process reload. The previous run reached only four pairs; `empty` and `masked`
  remain unvalidated on GPU and a pass on four pairs is not a pass.
- **No acceptance criterion is relaxed.** The key-bias exemption stays exactly as
  approved; every other weight and every optimizer slot keeps raw post-Adam equality.
- If D2 passes, calibration follows in the same allocation as already authorized, and
  its evaluator decides the 20% headroom gates on measured seconds.
- A technical failure stops dependent compute, with no retry and no seed replacement.

## Stage D3 — the learning comparison, if every gate passes

Already authorized and unchanged: the frozen 24 jobs, ordinary/injected/shuffle ×
seeds `17, 29, 43, 59, 71, 89, 101, 113`, one million training and 250,000 test
events, three iterations, five epochs per fit, batch 1,024, both routing arms paired
inside each job, at most two full jobs concurrently, reduced by `summarize_runs.py`
under the frozen criteria with calibration excluded.

**The endpoint is a recommendation supported by matched learning results and compute
costs, with uncertainty and scope stated** — not a winner. Accordingly:

- Learning: the frozen paired criteria as implemented, including the `>5%` paired
  lower bound and `>=7/8` favourable seeds. `NO_PASS` may be inconclusive or a
  safeguard failure and is never a statement of inferiority.
- Compute: per-arm cost reported from the run receipts' own
  `reco_fit_seconds`/`truth_fit_seconds` plus measured allocation seconds, so the
  pooled and direct arms are compared on cost as well as closure. Retaining more
  information is expected to cost more; that is a measurement to report, not a
  penalty to assert.
- Uncertainty: the paired seed interval, stated as what it is — a synthetic
  seed-spread interval, not a physics uncertainty product.
- If the evidence is inconclusive, that is the reported outcome. No winner will be
  forced.

## Boundaries that this diagnostic does not move

- Information retention and performance stay distinct. Our uncapped representation
  retains strictly more information than either upstream cap path; that is an
  established implementation property and **not** a claim about learning, closure or
  compute efficiency. Whether compression helps in practice is a separate open
  question that this work does not answer.
- The cross-device preflight failure is a reproducibility fact about one code path. It
  does not establish that individual typed-object tokens are scientifically worse.
- Overflow findings remain established implementation properties only; the overflow
  contrast stays conditioned on measured calibration headroom.
- No real-source reads, normalization or training, publication adoption, covariance,
  statistical pairing, coverage claim or Gate-6 action. No producer or mentor messages.
