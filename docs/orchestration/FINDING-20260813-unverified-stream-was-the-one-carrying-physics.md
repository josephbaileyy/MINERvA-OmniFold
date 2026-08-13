# FINDING 2026-08-13 — the one inventory stream verified nowhere was the one carrying the physics

**BEN-151.** Lane C (PET), during the first family reconciliation of the Gate-5 `C_stat` campaign
(target array `56857232`, training array `56857233`).

**One-line version:** three coherent Poisson factor streams per replica; two are replay-compared *and*
re-hashed at two separate stages, both fail-closed; the third is persisted nowhere and compared nowhere
— and the third is the one that generates the measured-side variance `C_stat` exists to quantify.

## What the code actually does, measured rather than summarised

Gate 5's F7 procedure draws one coherent Poisson(1) factor per member of three full inventories
*before* any training subset. `fullevent_fps_dataloader.py:614`:

```python
def coherent_bootstrap_factors(n_data, n_sig, n_bkg, seed):
    data_factor = np.random.default_rng(int(seed)).poisson(1.0, int(n_data)).astype(np.uint8)
    sig_factor  = mc_poisson_factor(int(n_sig), int(seed))        # rng(seed + 10_000_000)
    bkg_factor  = np.random.default_rng(int(seed) + 20_000_000).poisson(
        1.0, int(n_bkg)).astype(np.uint8)
    return data_factor, sig_factor, bkg_factor
```

### The signal and background streams are well guarded — this is not a story about sloppy code

**Target stage**, `build_fullevent_replica_target.py:215-222`, with a comment that states the intent:

```python
    # Replay the three full factor streams and prove the loader used their exact restrictions.
    data_factor, sig_factor, bkg_factor = fe.coherent_bootstrap_factors(
        n_data, n_sig, n_bkg, int(args.bootstrap_seed))
    if not np.array_equal(sig_factor[imc], np.asarray(bootstrap["sig_bootstrap_factor"])):
        raise SystemExit("[gate5-target] loader signal factors differ from canonical replay")
    if not np.array_equal(bkg_factor, np.asarray(bootstrap["bkg_bootstrap_factor"])):
        raise SystemExit("[gate5-target] loader background factors differ from canonical replay")
```

**Training stage**, `train_fullevent_replica.py` `validate_artifact`, independently and also fail-closed:
re-hashes the persisted full signal factor, asserts `sig_factor_full.shape == (n_sig,)`, asserts the
training subset is a true **restriction** of the full factor (`sig_factor_full[imc]` equals the stored
subset), and re-hashes the background factor. That subset-restriction assertion is exactly the
predeclaration's step 5 — *select without redrawing, shortening or reindexing* — enforced in code.

**So two of three streams are covered twice over, by two stages, both failing closed.**

### The data stream is covered nowhere, and the reason is structural

The loader's bootstrap telemetry dict, `fullevent_fps_dataloader.py:1328-1330`:

```python
    "n_bkg_full": int(n_bkg_full), "mc_indices": imc, "sig_bootstrap_factor": sig_factor[imc],
    ...
    "bkg_bootstrap_factor": (bkg_factor if has_bkg else None)}
```

`sig_bootstrap_factor` and `bkg_bootstrap_factor` are exposed. **There is no data equivalent.** So:

- the target stage *cannot* array-compare the data factors — the loader's value is not reachable, so
  this is not an omission someone chose;
- the training stage *cannot* re-hash them — they are not persisted;
- and the receipt's `bootstrap.data_factor_sha256` is therefore **the builder's own recomputation**,
  not a record of what the loader used.

**The comment says "the three full factor streams." The code checks two.**

## Why the two passing checks do not vouch for the third

This is the part that is easy to get wrong, and getting it wrong in the reassuring direction is the
whole hazard. The three streams are drawn from **independent** generators — `rng(seed)`,
`rng(seed + 10_000_000)`, `rng(seed + 20_000_000)`.

- A passing signal check proves agreement on `(seed, n_sig)`.
- A passing background check proves agreement on `(seed, n_bkg)`.
- **Neither constrains `n_data`.**

And `n_data` is the one free parameter that matters, because
`default_rng(seed).poisson(1.0, N)` is *prefix-consistent*: a smaller `N` yields a strict prefix of the
same stream. A truncated or mis-counted data inventory would therefore produce factors whose leading
values are all correct — the failure mode least likely to look like one.

So the exposure is **narrow, not zero**, and it should be described that way rather than either
dismissed or inflated.

## The lesson: this was a selection effect, not an oversight

Nobody decided to skip the data factors. The pattern is:

> **A value gets verified when something downstream consumes it as an array. The data factors are
> consumed as a *weight multiplier* and then discarded, so no downstream consumer ever needed the array
> — and so nothing ever had a reason to persist it, and therefore nothing could check it.**

The verification coverage followed the *data flow*, not the *physics importance*. Those two orderings
happened to be opposite here: the signal factors are heavily plumbed (subset restriction, extraction
replay, full-inventory length) and the data factors are the ones that actually move the measurement.

**The generalisable check:** for each quantity your uncertainty depends on, ask *what would have to be
persisted for this to be checkable at all* — before asking whether it is checked. A quantity that is
structurally unreachable will read, in every audit, exactly like a quantity nobody thought to audit.

## What closed it, and what remains open

Closed by independent measurement in
[`state/gate5-family-reconciliation-20260813.json`](state/gate5-family-reconciliation-20260813.json),
via `nd-unfolding/pet/reconcile_gate5_family.py`:

- All three streams re-drawn from each replica's declared seed and declared full inventory sizes,
  hashed under the receipts' own stated contract (`sha256(dtype || JSON(shape) || raw bytes)`).
  **16/16 replicas match on all three, data included.**
- `n_data` pinned independently: the builder's `bootstrap.n_data_full` equals the loader's own
  `runtime_target.n_data_rows` (`4,116,128`) in every receipt, and the loader hard-raises at
  `fullevent_fps_dataloader.py:950` if `data_factor.shape != (n_data_rows,)`.

**The residual, stated rather than dissolved:** this proves the recorded hash is the canonical draw for
the declared `(seed, n_data)`. It does **not** prove the loader used it. Only loader-side persistence
could, and that is one key in a dict — it belongs to the next launch, not to a live campaign.

### A note on the control, because it is invisible in a PASS

The reconciliation ran under numpy 2.3.5 while the campaign ran under TF 2.15's numpy. Had the
PCG64/poisson stream differed between them, **all three** redraws would have mismatched. Because signal
and background are independently verified upstream, their agreement proves the interpreter reproduces
the campaign's stream — which is what makes the data-factor comparison evidence rather than a coin
flip. Had *only* data mismatched, that would have been a campaign finding; had all three mismatched, a
finding about the interpreter and nothing else. **The two already-guarded streams functioned as the
control for the check on the unguarded one** — worth keeping as a pattern: when adding a check, look for
an already-verified neighbour to calibrate it against.

## Related

- `BEN-149` — a name that claims verification suppresses the check. Same campaign, adjacent mechanism:
  there the claim was in a field *name*; here it is in a *comment* ("the three full factor streams").
- `BEN-150` — the field-name collision found in the same reconciliation pass.
- `CONVENTION-receipt-ingredients.md` / `BEN-077` — ship the ingredients of every derived quantity.
