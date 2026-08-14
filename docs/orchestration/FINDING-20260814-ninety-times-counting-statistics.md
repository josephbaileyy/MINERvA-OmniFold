# FINDING 2026-08-14 — Ninety times counting statistics, and fifty members that all agreed

**`BEN-232`.** Lane C (PET), owner of Gate 5 / P5B.1 / `C_stat`.
**Status:** OPEN — `OI-92`, `CSTAT-O2`. Returns to Joseph. **Does not block building; blocks publishing.**
**Found:** while writing `SPEC-20260814-gate5-cstat-construction-v1.md`, not while looking for it.
**Evidence:** [`state/gate5-cstat-spec-measurements-20260814.json`](state/gate5-cstat-spec-measurements-20260814.json)
and the five scripts + verbatim stdout in
[`state/gate5-cstat-spec-measurements-20260814/`](state/gate5-cstat-spec-measurements-20260814/).

---

## The number

The Gate-5 N=50 coherent replica family exists for exactly one purpose: to produce `C_stat`, the
statistical covariance of the extracted cross section. Measured across the 14 published extractions:

| quantity | value |
|---|---|
| relative sd of `total_sigma_cm2_per_nucleon` across members | **4.478 %** |
| Poisson expectation, `n_data = 4,116,128` | **0.0493 %** |
| **ratio** | **≈ 90×** |
| Poisson expectation, `n_sig = 49,152,885` | 0.0143 % |
| (max − min) / mean | 18.187 % |
| median abs deviation / mean | 1.676 % |
| per-cell relative sd, median / max | 0.151 / 0.794 |

An integrated quantity over 4.1M data events cannot fluctuate by 4.5% from counting. And the
*distribution shape* is wrong independently of the width: median deviation 1.68% with `replica_08` at
**+9.96%** and `replica_09` at **−8.23%**. Counting statistics on millions of events produces a tight
gaussian, not a tight core with 8–10% tails.

## The cause

`grep` for `set_seed` across `nd-unfolding/` and `omnifold_nn/` returns **nothing**. No
`tf.random.set_seed`, no `np.random.seed`, no `TF_DETERMINISTIC_OPS` — not in
`train_fullevent_replica.py`, not in the extractor.

The `bootstrap_seed` plumbing that *is* present is extensive and correct, and that is precisely what
makes it misleading: `:150-153` threads the seed into the loader, `:157` and `:167-168` validate the
loader's bootstrap evidence carries it, `:319-321` enforces `bootstrap_seed == 50000 + replica_index`.
All of it governs **the draw and the provenance of the draw.** None of it governs **weight
initialization, batch shuffling, or GPU reduction order.**

So each of the 50 members differs from every other in **two** ways at once:

1. its Poisson draw — the intended axis, worth ~0.05%; and
2. free-running training stochasticity — unseeded, unmeasured, and plausibly the bulk of 4.5%.

The published matrix is therefore `C_stat + C_train + cross terms`. **The two are not separable from
this family**, because no two members share a draw and no member was ever repeated under a different
initialization. There is no lever in the existing 50 artifacts that holds one fixed while the other
varies.

## What I am *not* claiming

Not that `C_train` dominates. A second reading fits every number above: the iterative unfolding may
genuinely **amplify** the data fluctuation, and a network with enough capacity to fit per-replica noise
can amplify a 0.05% input by a large factor. If that is what is happening, the spread is legitimately
statistical, `C_stat` is the right name, and **the amplification factor is itself a significant result**
that belongs in the technote — arguably a more interesting one than the covariance.

Both readings are consistent with all of the evidence. I am not going to argue between them, because
arguing is the wrong instrument:

## `CSTAT-O2a` — the discriminating test, which is one measurement

**Re-train one replica index twice at the same `bootstrap_seed`, then extract both.**

The subtlety worth stating, because it is the way to get this wrong cheaply: **extraction is
deterministic given weights**, so repeating *extraction* measures exactly zero. The repeat must be of
**training**. Non-zero spread between two same-seed retrains is `C_train` with the draw held fixed,
measured directly. Three to five such pairs at ~14 min/task bound it well enough to state what fraction
of the published matrix is not statistical.

## Why this sat under fifty passing checks

This is the part I want a future agent to read, because the campaign's verification was not weak — it
was *thorough on the wrong axis*.

The Gate-5 family passed `FAMILY_COMPLETE_PASS` at full strength: 58 checks per target row, 50/50
targets, 50/50 trainings, zero failures, zero name mismatches, 50-of-50 distinct on target digests, all
three factor-hash streams, and weights digests, with 50 distinct `R` straddling the nominal. Every one
of those checks compared **the family against itself** or against a recorded expectation derived from
the same producer.

**The uncontrolled variable was uncontrolled identically in all fifty members**, so no comparison
*among* them could reveal it. Fifty-way unanimity is exactly what an unseeded network produces: every
member is stochastic in the same way, so every member agrees that this is normal.

What exposed it was one division by `sqrt(n_data)` — **a comparison against an external scale that
lives outside the campaign's artifacts entirely.** That scale was available from the first replica. It
cost one line and no compute.

This is `BEN-230`'s lesson arriving from the other direction. There, a receipt whose numbers all
re-derived was evidence of arithmetic and not of measurement. Here, a family whose members all agree is
evidence of *homogeneity* and not of *correctness*. **The generalisation: internal agreement, at any
count, has no power over a defect shared by every member.** Distinct hashes prove the draw is live; they
say nothing about whether the spread they produce means what its name says.

And the naming half is `BEN-149`'s shape — `train_fullevent_replica.py:112` copying a claim into a field
named for a measurement, one directory away in the same campaign. Same defect at a different scale: a
label asserting a property of its contents that nothing established. The field there was
`inputs_sha256_verified`. The label here is `C_stat`.

## The stake is a double-count, and it was not obvious until the sibling component was read

**Added after the first draft of this finding, which framed this as a naming problem. It is worse than
that.** `RUNBOOK:223-224` defines the sibling component: **"`C_ML`: no Poisson variation. Use a
predeclared crossed seed design and compare with the P5A floor."** That is training/seed variance **with
the draw held fixed** — which is *precisely* the quantity the unseeded network is injecting into `C_stat`.

So in `C_total = C_syst + C_stat + C_ml + C_retrain`, **`C_stat` as built already contains the `C_ML`
quantity, and the sum counts it twice.**

The reason this is damning rather than merely unlucky: **this campaign has already done exactly this
analysis for a different pair, and documented it.** `assemble_ctotal_bkgsub.py:10-20` carries an explicit
no-double-counting proof for `C_syst + C_retrain`, constructed by defining `C_retrain` relative to the
frozen map rather than to nominal, and it even names the shape that *would* have failed: *"Had `Delta_u`
been `x_retrain − CV` it WOULD double-count."* The rigour exists. **`C_stat + C_ML` is the one pair with
no such proof — and the difference is that the other overlaps were avoided *by construction*, whereas
this one was created *by omission*: a missing `set_seed`.**

It is contingent on which reading of the 4.478% holds, which is why one measurement settles both:

| if the spread is… | `C_stat + C_ML` | the name |
|---|---|---|
| training-dominated | **double-counts** | not `C_stat` alone |
| amplification-dominated | does not | `C_stat`, and the amplification is itself a result |

**And `CSTAT-O2a` is not merely a test — retraining one index twice at the same `bootstrap_seed` is a
one-point measurement of the `C_ML` quantity itself.** So it produces a number the `C_ML` component needs
regardless of how the naming question is answered, which is why it is worth running either way.

## Disposition

- **`OI-92` / `CSTAT-O2`** — open, WAITING-USER, Joseph's call.
- **The spec proceeds.** The construction is identical whatever the matrix is entitled to be called, so
  both builders can be written and tested now. `SPEC-…-v1.md` §8 states the issue and §12 lists it as a
  **publication** precondition, not a construction one.
- **Not fixed by C, and deliberately.** Adding `set_seed` would change the training driver *mid-family*
  and invalidate the 50 members already produced. The repair, if Joseph wants determinism, belongs with
  the next launch alongside `OI-57`/`OI-58` and the CODE_ROOT sync — the same queue as
  `train_fullevent_replica.py:112`, for the same reason.
- **Do not "fix" this by re-running the family with seeds.** That answers a different question. The
  measurement that resolves the *current* family is `CSTAT-O2a`, and it costs ~5 tasks.
