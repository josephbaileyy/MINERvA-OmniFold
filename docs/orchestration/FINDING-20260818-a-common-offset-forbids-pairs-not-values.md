# A common-offset scan's forbidden set is a condition on PAIRS of grid points, not a set of offset values — and the harm is aliasing between members, not loss of structure

**BEN-444.** Filed 2026-08-18 by the seconding lane (block `440-449`). **A correction, from the second party,
to a constraint lane C derived in
[`DETERMINATION-20260818-lanec-Bs-coherent-variation-is-an-offset.md`](DETERMINATION-20260818-lanec-Bs-coherent-variation-is-an-offset.md)**
(`34a5ba2a`, `BEN-461`). The determination is right that the constraint exists and right that it belongs in a
launcher assertion; **the set it names is under-inclusive and the harm it names is the wrong defect.** Caught
before anything was written — lane B was stopped mid-task.

## The setting, measured by lane B and not re-derived here

Two coherence groups, by estimator-seed baseline:

| group | legs | baseline |
|---|---|---|
| `g1` | `sweep_bank_5d`, `bootstrap_nd`, `seedscan_split` | **42** |
| `g2` | `unified_throw_cov`'s throws + block units + CV | **1000** |

Under `(ii)` — C's ruling, which this lane seconded — a coherent variation is **a common offset `k` from each
leg's own baseline**, chosen so that legs sharing noise keep sharing it and legs that do not keep not.

## What C got right, and it is the non-obvious half

**A common offset can never MERGE the groups.** `b1 + k == b2 + k ⟺ b1 == b2`, false for distinct baselines,
for every `k`. That disposes of the first thing a reader would worry about, and the determination says so.

## Defect 1 — the named set is the `k' = 0` special case

C's constraint: *exclude `k ∈ {+958, −958}`*, generalised as *"for any offset scan over groups with baselines
`{b_i}`, the forbidden offsets are `{b_i − b_j : i ≠ j}`."*

**The general collision condition is between two grid points, not one:**

```
g1@k == g2@k'   <=>   b1 + k == b2 + k'   <=>   k − k' == b2 − b1 == 958
```

**`{±958}` is exactly the case `k' = 0`** — collision with the **baseline** member only. Any two scanned
offsets differing by `958` collide, wherever they sit. Verified:

```
g1@k=1058 -> 1100 | g2@k= 100 -> 1100    COLLIDE   neither offset in {±958}
g1@k= 500 ->  542 | g2@k=-458 ->  542    COLLIDE   neither offset in {±958}
g1@k=2000 -> 2042 | g2@k=1042 -> 2042    COLLIDE   neither offset in {±958}

grid [0, 100, 500, 958, 1058, 1500]
  colliding pairs: (0, 958)  AND  (100, 1058)
  C's assertion flags:  (0, 958) only
```

> **CORRECT CONSTRAINT: no two scanned offsets may differ by any `b_i − b_j`.** Equivalently: over the whole
> grid, `{b_i + k}` contains no duplicate across distinct groups. Still one line to compute — over pairs
> rather than over values.

**Why this is not pedantry: `assert k not in (958, -958)` is worse than no assertion.** It passes a grid
containing `100` and `1058` and lets the aliasing through **with a guard's endorsement**. That is `BEN-405`'s
shape — a value legal arithmetically that destroys the property being measured — **arriving inside the guard
written against `BEN-405`'s shape**, which is the `BEN-333` family (the rule broken by the artifact asserting
it) one level in.

## Defect 2 — the harm is mis-described, and a wrong harm aims the debugging wrong

The determination says at `k = ±958` *"the two coherence groups land on each other's baseline values and the
structure the offset exists to preserve is destroyed."*

**Measured at `k = 958`: `g1 → 1000`, `g2 → 1958`. Distinct. The within-run co-variation structure is
INTACT.** Nothing about the run's internal correlation pattern changed.

What actually happens is that **`g1` at `k = 958` uses the seed `g2` used at `k = 0`** — so two *members of
the scan ensemble* share a realisation across different groups. **The defect is spurious aliasing BETWEEN
GRID POINTS, not destruction of structure WITHIN one.** For an `M(ii)` that estimates spread across the
ensemble, correlated members bias the spread — typically downward — which is a quieter failure than a broken
structure and shows up as a too-small uncertainty rather than as anything wrong.

**A failure message describing the wrong defect sends the next reader to the wrong place.** The assertion's
message must say *aliasing between grid points*, or a lane that trips it will go looking for a corrupted
correlation structure and find none.

## Defect 3 — the constraint's necessity rests on a premise the same document declines to rely on

**Both C's `±958` and this row's pairwise form are necessary only if a shared seed VALUE across DIFFERENT
legs actually produces correlated noise.** The determination's own lineage records that as unmeasured, as
`CONSIDERED-AND-DECLINED`:

> *"a shared seed initialises the same RNG state but consumes draws against different data — perhaps the
> perturbations decorrelate. **That is an empirical claim nobody has measured.**"*

**So: if the premise holds, C's set is under-inclusive and this row's is required. If it fails, the
constraint is unnecessary altogether.** Either way the determination **treats as a structural certainty the
same claim it elsewhere holds open** — and the mediator relayed it onward as a structural fact without
noticing, which is how the asymmetry propagates.

**Impose the constraint anyway.** Conservatism costs nothing here: excluding pairs from a scan grid is free,
and the failure it prevents is silent. **But state it as conditional on the unmeasured premise, not as a
property of the arithmetic** — the arithmetic gives you *which* offsets collide, and only the premise makes a
collision harmful.

## What is NOT claimed

- **The `(i)`/`(ii)` ruling is C's and stands** — seconded here on independent grounds, and C's derivation
  from the retired jitter term (*estimator noise is correlated between legs that share a seed and independent
  between legs that do not, so "coherent" names a co-variation STRUCTURE, not a seed VALUE*) is a derivation
  where this lane's *do not let measurability choose the specification* was a heuristic. **Nothing here
  reopens it.**
- **No claim that the aliasing was ever realised.** No scan has been run; the grid does not exist yet.
- **No launcher was written or edited by this lane**, and the determination is not edited — it should carry a
  pointer to this row rather than absorb it (write once, index elsewhere).

## Coda, and it is this lane's own defect

Deriving the block for this row, `BEN-445` appeared to be taken, and `FINDINGS.md`'s block row records
`440-449` as holding *"`440`–`443`, `445`"*. **`445` was never filed.** Its only occurrence in the repository
is a **synthetic row string inside this lane's own test fixture** —
`test_ben_filing_owner_check.py:59`, `"| BEN-445 | filed into the SECOND advertised block |"` — written as
test data for the check that distinguishes a *filed* id from a *mentioned* one.

**So a test fixture for the mention-versus-filing distinction was itself counted as a filing**, by a sweep
that did what `ben_filing_owner_check.py` exists to stop. The id is free; the block row overstates by one.
Recorded rather than quietly corrected, because the fixture is this lane's and the next such sweep will hit
it again.

## Cross-references

- `BEN-461` (lane C) — the `(ii)` OFFSET determination this corrects one constraint of.
- `BEN-405` — a parameter value legal arithmetically that destroys the property being measured. The class C
  correctly identified; this row is that class inside the guard against it.
- `BEN-333` — the rule broken by the artifact asserting it.
- `BEN-443` — a null disjunct invisible in a non-empty output. Same family: a check that returns a clean
  answer over an incomplete domain.
