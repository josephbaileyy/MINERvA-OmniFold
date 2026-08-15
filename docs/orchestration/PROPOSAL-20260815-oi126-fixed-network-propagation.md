# FUTURE PROPOSAL — separate information loss from refit sensitivity with a FIXED network

**NOT AUTHORIZED. NOT COSTED. RUNNABILITY EXPLICITLY UNCHECKED.** Filed 2026-08-15 for whichever lane
next picks up `OI-126`. Originated by lane B, which declined to propose it; developed and endorsed by
the executor lane, which declines to cost it for the same reason. **Nobody has checked that it can be
run.**

## The question it answers, which the retired contrast could not

`OI-126`'s live fork is whether the band's `67%` replica spread reflects **information loss** — the
measured leg genuinely does not constrain that region — or **estimator fragility** — the refit moves
more than the information content warrants. `C_stat`'s validity as a *statistical* uncertainty depends
on which.

The retired `Exponential(1)` contrast
(`PREDECLARATION-20260815-oi126-exponential-contrast.md`, retired at `410af7a`) tried to separate them
by **changing the noise model**. That failed on physics: `Poisson(1)` row multiplicities reproduce the
**exact** sampling distribution of every aggregate, so it is not a proxy to be swapped — it is the
sampling distribution, and any replacement is a *wrong* model chosen for its answer.

## The inversion

**Keep `Poisson(1)`. Remove the confound structurally instead of substituting a model for it.**

Propagate the `Poisson(1)` resampling of the measured leg through a **FIXED, already-trained network**
— the nominal's — rather than refitting per replica.

```
current family :  resample measured leg  ->  REFIT  ->  extract   (both components present, entangled)
proposed arm   :  resample measured leg  ->  FIXED net ->  extract  (refit sensitivity removed BY
                                                                     CONSTRUCTION; what remains is
                                                                     information loss alone)
```

Then the comparison is **fixed-net spread vs the existing 50-replica refit spread**, both under the
correct noise model:

- **spreads comparable** → the `67%` is information loss. `C_stat` is a valid statistical uncertainty
  and the band's uncertainties are simply large.
- **fixed-net spread much smaller** → the excess is refit sensitivity, i.e. the estimator moving more
  than the data licenses. That is a defect in the *estimator*, not in the noise model, and it is
  actionable without ever choosing a noise model for its answer.

**Both outcomes are actionable, which is precisely what the retired contrast failed.**

## Why the executor lane believes it works, stated as an argument

Its validity rests on the one part of lane B's case that did **not** survive scrutiny. B argued the two
arms of the retired contrast were blind to refit sensitivity because their **effective sample sizes are
identical** — `E[w] = 1`, `E[w²] = 2`, so `ESS = N/2` for both, exactly. **The arithmetic is right and
the inference is wrong**: `ESS` is one scalar functional, and a learned estimator sees the vector.
`Poisson(1)` makes `36.8%` of rows *absent* from training; `Exponential(1)` makes `63%` present but
downweighted, and `P(Poisson empties a cell's measured support) = e^-n_rows` (`0.368` at one row,
`4.5e-05` at ten) against exactly `0` for `Exponential` at any `n`.

**That refutation is what makes this proposal work.** Refit sensitivity is real, is not captured by
`ESS`, and therefore **cannot be removed by any reweighting** — it can only be removed by not
refitting. Fixing the network does exactly that.

## What must be settled before it is proposed for real

**None of this is done, and the proposal should not be costed until it is.**

1. **Runnability.** Whether the extraction path accepts a fixed network with resampled measured weights
   at all, without touching a pinned file. **Unchecked.** The `[0,49]` namespace bound is in **three**
   files (`build_fullevent_replica_target.py:150`, `train_fullevent_replica.py:320`,
   `extract_fullevent_replica.py:443`) and `build_fullevent_loaders` has **no `data_factor` parameter** —
   both obstacles found while scoping the retired contrast, and both may or may not apply here.
2. **What "fixed network" means precisely** — the nominal's step-1 and step-2 models at which
   checkpoint tier, given `BEN-311`'s sibling-directory hazard and Leg 0's finding that the tier
   systematic is **bimodal** (bit-exact where best epoch equals final, percent-to-20% where it does
   not), not a smooth ~1.3%.
3. **Whether the comparison is coherent under the `C_stat` contract.** Lane C (PET) never ruled on the
   analogous question for the retired contrast. **A fixed-net arm is not a `C_stat` member and must not
   be keyed as one**, and whether its spread may be compared to the family's is a spec question, not a
   compute question.
4. **The predeclaration**, with a numeric two-sided boundary, `UNRESOLVED` non-defaulting, and the
   sizing derived from a **power** calculation rather than a half-width condition — the error corrected
   at `aa6585d`. The `sd` for sizing must come from the fixed-net arm's own draws or be declared
   borrowed.

## What it does not do

- It does not revisit whether `Poisson(1)` is correct. **It is**, and this proposal depends on that.
- It does not license replacing `C_stat`, moving the central, constructing `C_ML`, or selecting a
  subset. All five Gate-6 prohibitions at `19585b7` are untouched.
- It does not make the retired contrast worth running. **Nothing does**; see the retirement note.
