# DECISION 2026-08-15 — the `OI-126` Exponential contrast will NOT be run

**Unanimous consensus under Joseph's grant of 2026-08-15** (*"anything for any length of time as long
as there is consensus that it is the best option"*, `451f053`). **Four of four: (0) do not run.**

| lane | vote | basis |
|---|---|---|
| lane A | **(0)** | §7's continuous-null assumption is contested and free to settle; publication risk is asymmetric so the status quo already errs safe |
| lane B | **(0)** | conceded §7 **against its own position**; `Poisson(1)` is the sampling distribution, not one variance-matched option |
| `Assistant` (instrument's designer) | **(0)** | conceded on the physics; **both outcomes support `C_stat`'s validity**, so the instrument cannot undermine what it was built to test |
| mediator | **(0)** | — |

**Cost avoided: 97.6 GPU-h** (n=15, both arms). **Nothing was run. No override module was ever written.**

## The load-bearing reason — §7, not ESS

**`Poisson(1)` is not a proxy for the sampling distribution; it IS the sampling distribution.**
A row here is one reconstructed event. Independent `Poisson(1)` row multiplicities reproduce the
**exact** distribution of every aggregate of those rows — a bin's total is `Poisson(n_bin)` exactly.
`Exponential(1)` gives `Gamma(n_bin, 1)`: right mean, right variance, **wrong distribution**, and
wrong precisely in the atom at zero.

The designer's own retraction, verbatim: *"My §7 claimed row-level Poisson zeros are 'not the same
object' as a bin observing zero counts. That is false… for a bin holding one row, `Poisson(1)` on
that row IS the bin observing zero counts, with probability `e^-1`. My distinction only survives in
bins with many rows — i.e. everywhere except the sparse cells the whole question is about."*

**Consequences, both conceded without qualification:**

1. **The contrast cannot license replacing `Poisson(1)` whatever it returns** — doing so would be
   choosing the noise model that yields the smaller covariance.
2. **Both outcomes support `C_stat`'s validity.** If the band collapses under `Exponential(1)`, the
   reading is *"the instability is driven by the zero atom"* — and the zero atom **is** counting
   noise. That is branch (a)'s conclusion. **The instrument could not have undermined the object it
   was built to test.**

## What is NOT the reason, recorded so it does not enter the record wrongly

Lane B additionally argued that both arms share an identical effective sample size — verified exactly
by the mediator, `E[w] = 1` and `E[w²] = Var + mean² = 2` for both, so `ESS = N/2` — and inferred that
the contrast is therefore blind to refit sensitivity. **That inference is wrong**, and the
`Assistant` lane refuted it while conceding the vote:

```
Poisson(1)      36.8% of rows ABSENT from training (weight exactly 0)
Exponential(1)   0.0% absent; 63.2% present but downweighted

P(Poisson empties a cell's measured support) = e^-n_rows
  n=1  0.367879    n=3  0.0497871    n=10  4.54e-05    n=20  2.06e-09
Exponential: exactly 0 for every n
```

**Dropping an event and downweighting it are not the same operation for a network trained on a
weighted loss.** ESS is one scalar functional; the estimator sees the vector. So matched ESS does
**not** imply both arms carry the estimator-fragility component equally.

## What replaces it, at zero cost

**Characterize the `67%` rather than adjudicating it** (lane B). The honest description is available
now: it is the spread of a **refit** estimator under **correct** measured-statistics resampling — so
it is the sampling uncertainty *of this estimator*, and an **upper bound** on how poorly the data
constrain the cross-section. More useful to a reader than either branch, and defensible under both.

## Future proposal, NOT authorized and runnability unchecked

To separate estimator fragility from information loss: **propagate the resampling through a FIXED
trained network rather than refitting per replica.** That removes the refit-sensitivity component by
construction and leaves pure information loss — **using `Poisson(1)`, the correct model, with no
`Exponential` anywhere.**

The designer's framing of the inversion: *"I tried to defeat a confound by substituting a wrong noise
model. The right move is to keep the correct noise model and remove the confound structurally."*

## Standing items this decision does NOT close

- **`OI-126` remains OPEN.** Track B states the fork; nothing here resolves it.
- **Lane C (PET) never ruled** on reduced-n diagnostic coherence, after two asks. **Silence was not
  read as permission** — a decision *not* to run needs no spec interpretation, but the next proposal
  of this shape will need that ruling.
- `OI-58` — quoting half discharged at `c7eb704`; the stamping defect stays open.
- `OI-81` — open, lane C's script.
