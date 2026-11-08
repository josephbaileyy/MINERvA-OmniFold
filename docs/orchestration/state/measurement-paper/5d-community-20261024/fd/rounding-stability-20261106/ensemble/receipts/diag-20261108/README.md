# ENS1 stage-1 dry attempt 1: the read-only diagnosis of the grid-guard refusal (2026-11-08)

**Recorded by** the rounding-instability lane (`director-helper-3`). This is the director's step 1 after the stop (receipt
#908). The diagnosis ran on a login node, at 0 node-h, with no fit, and opened no product. Attempt 1's root
`/pscratch/sd/j/josephrb/ens1-20261107` was not read or touched. **Verdict: CONFIRMED.**

**CITABLE FOR:**
- the cause of the refusal: the counts, the moved rows and their edges;
- the list of non-representable edges;
- the count of coordinates within one float32 spacing of an edge, which is the population a value-based zone would touch.

**NOT CITABLE FOR:**
- any ENS1 reading, gate or product value;
- the repair. That is ENS1 addendum A1, still to be written, audited and bound.

## How it ran

- **The connect:** `connect/ens1_diag_connect.sh`, sha256 `6103b4ff…`, byte-identical to the one sent. The launcher is
  `89e18dc6…`, and ssh rc was 0. It ran on login18, 2026-11-08T01:32:36Z–01:37:12Z, with rc 0.
- **The fence, under the director's ruling.** The fence passes only if every queued job is `rs1_*` or `ens1_*`; it
  refuses on any `cov2d-*` job or any name it doesn't recognise. The pinned connect only records the squeue, so the
  rule was applied from the Mac just before launch, by a read-only squeue at 01:32:27Z
  (`connect/prelaunch-squeue-director-rule.txt`). It listed only `60982139 rs1_a1 RUNNING`, so it passed. The connect's
  own squeue at 01:32:36Z matches (`connect/squeue-before.txt`).
- **The deploy:** a fresh clone at M = `53382844`, clean, with 4 blobs enforced: `ensemble_estimator_probe`,
  `s5p_numerics`, `s5c_unfold` and `s5e_trace`.
- **The script:** `ens1_diag.py`, sha256 `d4b5ba16…`. It was embedded in the connect and checked after it was written.
- **The environment:** it ran under the deploy's sourced environment, Python 3.11.14.
- **The reads:**
  - the npz and the bkg were read through O_NOATIME handles, and both digests equal the bound pins (`07fccc1a…`,
    `2addac8f…`);
  - their atime is unchanged across the run (`connect/stat-before.txt`, `stat-after.txt`);
  - the npz was loaded through the runner's own `s5c_unfold.load_inputs`.
- **Membership:** the guard's own `s5p_numerics.cell_membership` and `s5e_trace.flat_index`. These use the npz's edges,
  float64 coordinates, `searchsorted(side="right")` and an inclusive last edge, and the base is computed as the runner
  computes it.
- **The output:** `diag.json`, sha256 `91964280…`.

## What it found (`diag.json`)

**1. The counts reproduce the job exactly.**
- With protocol jitter 1 plus δ_k, the `MCgen` rows moved were 2, 1, 2 and 1 for k = 1–4, and 0 for `MCreco`, `measured`
  and `bkg_reco`.
- With protocol jitter 1 alone, 0 rows moved in every class.

**2. Every moved row sits at the farther float32 neighbour of a non-representable edge.** Three distinct `MCgen` rows
are involved:

| row | axis | x (float32) | edge | distance (spacings) | crossed at k (move, spacings) |
|---|---|---|---|---|---|
| 13803463 | q3 | 1.1999999285 | 1.2 | 0.6 below | 1 (+0.851), 3 (+0.678) |
| 15432031 | W | 1.8000000715 | 1.8 | 0.6 above | 1 (−0.788), 3 (−0.733), 4 (−0.813) |
| 28958138 | pt | 0.3999999762 | 0.4 | 0.8 below | 2 (+0.885) |

**3. 21 of the npz's 55 edges are not float32-representable:** pt 8 of 15, pz 0 of 17, eavail 4 of 8, q3 5 of 8, and W
4 of 7. For each one, the farther float32 neighbour lies 0.56–0.96 of a spacing from the edge, and the nearer neighbour
lies 0.04–0.44 from it. The per-edge list is in `edges_not_float32`.

**Why protocol jitter alone never crosses.** The nearer neighbour of an edge e is round₃₂(e) itself. The exact-edge rule
(`s5e_trace.jitter_coords`, and ENS1's `internal_step`) never moves a value equal to round₃₂(e). The farther neighbour
lies more than ½ spacing away. The protocol's move is less than ½ spacing, so it cannot reach e from either side. The
combined move is protocol plus internal, so it can reach just under one spacing, and it can cross from the farther
neighbour. This holds for all five axes' edges as listed. A1 has to state it as an inequality over that list.

**4. The population within one float32 spacing of an edge.** These are coordinates with 0 < |x − e| ≤ spacing₃₂(x) for
an edge e of their axis. Values exactly on an edge are counted separately.

| class | rows | coordinates (pt / pz / eavail / q3 / W) | coordinates on an edge |
|---|---|---|---|
| MCgen | 104 of 32,849,103 | 104 (32 / 39 / 2 / 11 / 20) | 293,319 |
| MCreco | 57 of 32,849,103 | 57 (17 / 20 / 3 / 2 / 15) | 233,805 |
| measured | 15 of 4,091,707 | 15 (5 / 7 / 0 / 1 / 2) | 48,171 |
| bkg_reco | 3 of 621,547 | 3 (0 / 2 / 0 / 0 / 1) | 11,516 |

This is a count, not a result. The pz coordinates sit one spacing from representable edges.

**Renames:** git ignores `*.log` and `*.out`, so those files carry a `.txt` suffix here. Their contents are unchanged.
