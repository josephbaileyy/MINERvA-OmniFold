# DETERMINATION — the surviving `OI-126` mechanism DIES BY AVAILABILITY: the band is not the MC-starved end

**Lane E, 2026-08-17.** The free availability check, run before Route B as the mediator argued
(correctly — a join over arrays that exist should precede four sites of build work that a null would
make unnecessary).

**Read-only. No training, no unfolding, no GPU, no `sbatch`, nothing inside the promoted arm. One
read-only python on a login node, 17 s.** Receipt `state/oi126-band-mc-occupancy-20260817.json`,
probe `state/probe-oi126-band-mc-occupancy-20260817.py`, cluster tmp files removed.

---

## The verdict

> **The amplifier the mechanism requires is located OUTSIDE the band, while the observed effect is
> confined TO the band. That is the opposite of the prediction, so the mechanism dies by
> availability — the same way the Jensen route died on 0 of 86 band cells.**

**C's premise is confirmed by measurement first, because the argument depends on it.** Poisson(1)
support thinning is uniform *in share*:

```
surviving distinct fraction   BAND 0.63205   OUTSIDE 0.63253   expected 1 - 1/e = 0.63212
```

Four decimals, both sides. So a band-confined effect needs a **local amplifier**, and the only one
available is MC sparsity: losing 36.8% of rows is harmless in a rich cell and severe in a thin one.

**Measured on the EXACT training population** — `mc_indices` from the replica artifact, 2,000,000 of
49,152,885 inventory rows — with the band taken as p∥ columns 10–15 (6–20 GeV) intersected with the
artifact's own `reported_bin_mask`:

| rows per cell | BAND (84 cells) | OUTSIDE (174 cells) |
|---|---|---|
| min | **42** | **1** |
| q25 | **912** | **421** |
| median | 2 382 | 5 506 |
| q75 | 4 739 | 17 652 |
| max | 22 273 | 52 840 |

**The band has NO starved cells and the region outside does.** Proportion of cells below a row count:

| threshold | BAND | OUTSIDE |
|---|---|---|
| < 100 rows | 4/84 = **4.8%** | 27/174 = **15.5%** |
| < 250 | 9/84 = 10.7% | 33/174 = 19.0% |
| < 500 | 15/84 = 17.9% | 45/174 = 25.9% |
| < 1000 | 23/84 = 27.4% | 51/174 = 29.3% |

**At every threshold starvation is more prevalent outside the band — 3.2× at the tightest.** The band
sits in the middle of the grid's occupancy range with a *truncated low tail*, which is exactly the
profile D's independent findings imply: highest acceptance (median `a_b` 0.859 vs 0.713), 26.5% of
reco-accepted truth mass, background share *between* the two control regions.

---

## THE MEDIAN SAYS THE OPPOSITE, AND THAT IS WHY THE NO-REDUCTION CONDITION EARNED ITS KEEP

**Band median 2 382 against outside 5 506 — the band is 2.3× SPARSER BY MEDIAN.** A median-only
report would have read *"band is the sparse end → mechanism plausible"* and sent someone to build
Route B.

**It would have been wrong, because the amplifier acts through the LOW TAIL, not the middle.** A cell
with 2 382 rows losing 36.8% is not in trouble; a cell with 1 row is. The band's low tail is *better*
than outside's on every measure — min 42 vs 1, q25 912 vs 421, and fewer sub-100 cells proportionally.

**Fifth instance today of a summary statistic standing in for a distribution, and the first one caught
BEFORE it propagated** — caught only because the dispatch forbade reducing before reporting. The
per-cell arrays are in the receipt under `NOT_REDUCED_per_cell_arrays`; nobody has to trust this
document's cut points.

---

## What the population choice does, stated because it flips the headline

A first pass used `pass_reco` as a proxy for the training subset, and on the **full 49.2M-row
inventory** the ordering inverts — band median 57 410 against 127 073, i.e. the band looks sparser.
**The full inventory is not what the estimator trains on.** The training population is `mc_indices`,
2 000 000 rows (the `train_events` cap), and that is what the table above uses.

**Both edge arrays were asserted equal to the loader's canonical grid before indexing** — `edges_pt`
and `edges_pparallel` out of the artifact against `fe.CANONICAL_*_EDGES` — because otherwise the cell
index this probe builds is not the index the artifact's mask addresses. Columns come from
`fe.SCALAR_COLS`; the flattening `cell = pt_bin * 19 + pp_bin` and the band definition are copied from
the committed `state/probe-oi126-band-Rpush-sigma-20260815.py:32,63`. **No binning was invented here.**

---

## What this does NOT establish

- **I did not reproduce the "63 band cells" count.** `reported_bin_mask` gives **258** quotable cells
  and **84** band-quotable; the 63 comes from a different quotable set (the 08-15 probe's 257). The
  conclusion is stated on 84/174 and the per-cell arrays are published, so anyone can re-cut it on the
  63. **Do not quote this as being about the 63 without redoing the intersection.**
- **This kills an AMPLIFIER, not the smoothness claim itself.** *"A trained network may not be a
  smooth functional of the empirical measure when a third of its support vanishes"* remains a coherent
  statement; what it now lacks is a reason for the failure to be **band-confined**, which is the whole
  signature it was recruited to explain.
- **It says nothing about the comparability argument**, which is external and untouched: the data
  factors are Poisson(1) too (`fullevent_fps_dataloader.py:621`), so the nominal still trains on the
  full inventory while every replica trains on a thinned one. **The 151 A100-h ensemble is still
  warranted on comparability grounds** — but a predeclaration for it must no longer claim the
  MC-thinning mechanism as its motivation, and *"nominal inside implies MC-thinning"* was already
  invalid.
- **One replica measured (`replica_00`).** Uniformity of share is a property of Poisson(1), and the
  occupancy is a property of the inventory rather than the draw, so neither depends on which replica —
  but I measured one, and a second is ~20 s if anyone wants it belt-and-braces.
