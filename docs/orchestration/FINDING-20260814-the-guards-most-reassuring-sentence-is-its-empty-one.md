# FINDING 2026-08-14 — the leakage guard's most reassuring sentence describes its only powerless statement

**BEN-250.** Lane D (verifier), from `OI-120(c)`. Independently reproduced line-by-line by the
mediator before this was written. Probe:
[`state/probe-oi120c-loader-purity-perturbation-20260814.py`](state/probe-oi120c-loader-purity-perturbation-20260814.py).

## The claim, and what it is worth

`assert_no_truth_leakage` is the campaign's guard against truth information reaching the reco leg
of the network input. It is called **in production**, on every `build_fullevent_loaders`
invocation, and therefore on every Gate-5 training run against the real publication input. It
proves three things. Its second and strongest-sounding statement is **PURITY**: rebuild
`event_reco` from the reco blocks alone and require an exact match.

**That statement cannot fail.** Not on a fixture, not on the real input, not in production.

## Measured

The producer, `fullevent_fps_dataloader.py:487-490`:

```python
rsub = _event_block(reco_blocks, feature_names, None)[rmask]
rmu = rsub.mean(0); rsd = rsub.std(0) + 1e-6
event_reco = _event_block(reco_blocks, feature_names, (rmu, rsd)); event_reco[~rmask] = 0.0
```

The checker, `:543-545`:

```python
raw = _event_block(reco_blocks, feature_names, None)
rmu = raw[rmask].mean(0); rsd = raw[rmask].std(0) + 1e-6
rebuilt = _event_block(reco_blocks, feature_names, (rmu, rsd)); rebuilt[~rmask] = 0.0
```

`rsub` **is** `raw[rmask]`. Same function, same inputs, same three lines. The assertion compares a
computation against a re-execution of itself.

And the two are six lines apart in the production caller — `event_reco` is built at `:1241` and
asserted at `:1247`, with nothing touching it in between.

## The part that made it survive

`:529`, describing the purity rebuild:

> *"Anything the truth arrays contributed would show up here."*

**It would not.** The rebuild never reads the truth arrays, and neither does the producer's reco
leg. The two agree because they are the same code — not because truth stayed out. A reader who
audits the guard by reading its docstring comes away with precisely the wrong impression, and
that is the mechanism by which a powerless check keeps its reputation for years.

> **Check:** for any assertion of the form *"recompute X and require a match"*, find the code that
> produced the X being passed in. If it is the code the assertion recomputes with, the assertion
> is an identity. Then read what the docstring claims it proves — **a false claim there is worse
> than no docstring**, because it converts an audit into a confirmation.

## What is NOT wrong here

**Statements 1 (schema) and 3 (dissimilarity on shared columns) have real power**, demonstrated on
real-object arrays: injecting truth `pT` into the reco leg fires the detector, and an all-NaN
`event_reco` fires the finiteness guard, both on a 2,000,000-event slice of the real NPZ. **The
guard is not worthless and must not be described as such.** Exactly one of its three statements is
empty, and it is the one whose name promises the most.

## What replaces it

Re-derivation cannot test purity when the input's provenance *is* the derivation. A **perturbation**
can, and needs no independent provenance at all:

> Run the production loader twice on the real input, identical except that a **truth** array is
> perturbed on the second pass, and require `event_reco` to be **bit-identical**.

Two passes differing only in the variable the claim says is irrelevant. It cannot pass by
construction. Smoke-tested at 200,000 events: the `P0` control (perturb a **reco** array) changes
`event_reco`, so the probe has demonstrated power; scaling and permuting `truth_scalars` leave it
bit-identical. The full-inventory run is `56943826`.

**`P0` is not optional.** Without a control that changes the hash, *"the hashes matched"* and *"my
perturbation never reached the loader"* are the same observation — which is this finding's own
failure mode, one level up.

## Family

- `BEN-173` — a positive control on one artifact and none on its sibling.
- `BEN-180` — a band tested only on the side the data is not on.
- `BEN-185` — a conditionally-skipped test reporting inside a passing suite.
- `BEN-186` — a check whose input was built by the code it re-derives with, **in a probe**.
- **`BEN-250`** — the same defect **in production**, in a named guard, with a docstring asserting
  the opposite.

`BEN-186` found the shape and scoped it to my own probe. This is the same shape in the shipped
code path, which is the difference between *"a verifier wrote a weak test"* and *"the campaign's
leakage guard has been carrying an empty statement on every training run."*
