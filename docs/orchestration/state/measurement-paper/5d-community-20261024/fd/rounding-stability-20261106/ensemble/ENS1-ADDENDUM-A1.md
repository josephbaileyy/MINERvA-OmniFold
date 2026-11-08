# ENS1 ADDENDUM A1: an edge-safe zone for the internal jitter (2026-11-08)

**For** audit by `coverage-5b-audit` and binding by the director. It amends the design that `ENS1-BINDING-1.md` bound and
the code that `ENS1-BINDING-2.md` bound at M = `53382844`. **Nothing has run under it.**

**Written by** the rounding-instability lane (`director-helper-3`), on the director's terms of 2026-11-08 (in
correspondence), after:
- stage 1's dry run, attempt 1, stopped (receipt #908);
- the read-only diagnosis confirmed the cause (receipt #909).

**CITABLE FOR:** the amended internal jitter, its margin argument, its population, and the rerun's terms.
**NOT CITABLE FOR:** any ENS1 reading or result.

## 1. What failed, and why (receipts #908, #909)

**The failure.** In stage 1's dry run (job 60983221), the bound runner's grid-membership guard refused all four tasks at
protocol seed 1 (`s5p_numerics.py:186-191`, exit 5). The `MCgen` rows that changed fine-grid cell numbered 2, 1, 2 and 1
for k = 1–4.

**The cause, confirmed at 0 node-h** with the guard's own `cell_membership` and the npz's edges:
- the counts reproduce exactly under protocol jitter 1 plus δ_k;
- protocol jitter 1 alone moves 0 rows;
- every moved row sits at the farther float32 neighbour of an edge that float32 cannot represent:
  - `MCgen` row 13803463, at q3 1.2;
  - row 15432031, at W 1.8;
  - row 28958138, at pt 0.4.

**§2.3 of the declaration is withdrawn** (§5). It said "the total move |δ_s + δ_k| is below one float32 spacing, so a
value off an edge cannot reach it". That holds only for edges float32 can represent. 21 of the npz's 55 edges are not
float32-representable.

## 2. The amendment: the edge zone

**The rule.** For a coordinate y on axis a, with r = round₃₂(y), s(r) = spacing₃₂(|r|), and E_a the inputs' own edges
for axis a:

  **zone(r) ⇔ there is an e ∈ E_a with |float64(r) − e| ≤ s(r),** and then **δ_k = 0** on that coordinate.

- **The draws are unchanged.** u_k ~ U(−½, ½) still comes from `default_rng(10000 + k)`, in the same fixed order, so δ_k
  is unchanged outside the zone.
- **The zone depends on the value alone,** not on u_k. So E_N is still one deterministic estimator.
- **The exact-edge rule is subsumed.** The bound design zeroed δ_k where round₃₂(y) equals round₃₂(e). Those values lie
  within 0.44 spacing of e, so they are inside the zone, and the separate line is removed. Its mutant, "grid edges moved",
  would now be equivalent, so it is retired; the zone's own mutants cover the case (§6).
- **The code:** `ensemble_estimator_probe.in_edge_zone` and `internal_step`. `internal_jitter` passes
  `inputs["edges"]`, the same list `s5p_numerics.cell_membership` hands to `s5e_trace.flat_index`.

**One edge definition.** The zone reads the edges from the inputs at call time, as the guard does. It reads them as
float64, as the guard does, and it has no table of its own. A REQUIRED mutant takes axis 0's edges for every axis, and
another takes the float32 rounding of the edges. Both are killed (§6).

**The guard stays unchanged** as the refusal backstop. Both stages still refuse on any change of membership (the
runner's guard in stage 1, the wrapper's check before each closure build in stage 2).

## 3. The margin, stated as an inequality

**The notation.** x is a float32 input coordinate on axis a, and s = s(x) = spacing₃₂(|x|), the value's own spacing.
**The zone uses s(r) for r = round₃₂(y), never the edge's spacing.** At a power of two the two differ by a factor of two,
and the value's spacing is the narrow one just below it.
- **The protocol step** is δ_s = u_s · s. It is 0 when x equals round₃₂(e) for an edge e (`s5e_trace.py:365-367`).
- **The internal step** is δ_k = u_k · s(r), where r = round₃₂(x + δ_s). It is 0 in the zone.
- **The draws:** both come from numpy's `Generator.uniform(−0.5, 0.5)`, whose samples lie in the half-open interval
  [−½, ½). Since s is a power of two, u · s is exact. So **−½ s ≤ δ < ½ s**: a step can reach −½ s exactly, but never +½ s.
- **The guard's bin** is `searchsorted(E_a, ·, side="right") − 1`, with the last edge inclusive. A value equal to an edge
  falls in the bin above it.
- **The float64 sums.** For |x| < 2²⁴ s, each float64 addition errs by at most ½ ulp₆₄ ≤ 2⁻²⁸ s, so the two additions
  together err by at most ε = 2⁻²⁷ s. That holds for every binade, including the subnormal range, where s = 2⁻¹⁴⁹ and
  |x| < 2²³ s.

**(i) The largest possible combined move.**
- |δ_s| ≤ ½ s, and x + δ_s rounds to x, or to the float32 just below x in two cases:
  - x is a power of two and δ_s ≤ −¼ s;
  - u_s = −½ exactly makes a tie that rounds to even.

  So s(r) ≤ s, and |δ_k| ≤ ½ s.
- **When r is that lower float32:** if x was within one spacing of an edge e below it (case (iii)(c), d ≥ 0.56 s), then
  r lies within s − d ≤ 0.44 s of e. So r is in the zone too, and δ_k = 0. The zone being computed on r rather than on x
  therefore never releases a coordinate that (iii) protects.
- **Upward,** δ_s + δ_k < s, strictly. **Downward,** δ_s + δ_k ≥ −s, with equality only at u_s = u_k = −½.
- With the float64 sums, **the final y′ lies in (x − s − ε, x + s + ε).** That bound, and not the observed 0.68–0.89 s, is
  the one the margin must beat.

**(ii) Outside the zone the combined move cannot cross an edge.** Outside the zone, every edge is more than s(x) from x.
For a float32 x, the nearest such value to an edge sits at least d_min from it. Computed over every edge of every axis,
each in the value's own spacing:

| axis | d_min outside the zone (own spacings) | power-of-two edges | edge at 0 |
|---|---|---|---|
| pt | 1.04 | 0.25, 1.0 | yes |
| pz | 2.00 | 2.0, 4.0, 8.0 | no |
| eavail | 1.20 | none | yes |
| q3 | 1.20 | 2.0 | yes |
| W | 1.20 | none | yes |

**d_min ≥ 1.04 s > s + ε** on every axis, so outside the zone y′ stays on x's side of every edge, and the cell is
unchanged.

- **The representable edges count** (the director's item 1). Take x = e − s, one spacing below a representable edge. It
  lies in the zone (d = s ≤ s), so δ_k = 0, and its protocol move is less than ½ s upward. It cannot reach e, where
  side='right' would change its cell.
- **Further out,** x = e − 2s is outside the zone, d = 2s, and its combined move upward is less than s + ε.
- **Downward onto e from above** is a landing in the same bin, because side='right' places e in the upper bin.
- **The binades** (the director's item 2). At a power-of-two edge e, the float32 just below it has s(x) = s(e)/2.
  - That value is in the zone (d = s(x)), and the next one down is outside (d = 2 s(x)). Both distances are measured in
    the narrow spacing, which is the one the steps use. This is why d_min on pz, whose edges include 2, 4 and 8, is 2.00.
  - If x is a power of two with r just below it, then s(r) = s/2. The combined move is then less than ¾ s + ε.
  - If x is in the zone through a representable edge, that edge is x itself (frozen) or a float32 neighbour of x.
  - If x is in the zone through a non-representable edge, its neighbours share one spacing (the next table), so x is not
    a power of two.
  - In every case (ii) or (iii) applies.
- **The zero edge** (the director's item 3). pt, eavail, q3 and W have an edge at 0.
  - The value 0 is on the edge, so it is frozen by both rules.
  - The smallest subnormal, 2⁻¹⁴⁹, is one spacing from 0. It is in the zone, so δ_k = 0, and its protocol step is
    u · 2⁻¹⁴⁹ ≥ −½ · 2⁻¹⁴⁹. That cannot reach 0.
  - Two and three subnormal spacings are outside the zone. They move by less than one subnormal spacing, and stay
    positive.
  - The jitter's scale near 0 is the subnormal spacing itself: steps of order 10⁻⁴⁵, which perturb nothing the fits can
    resolve. They are unchanged from the bound design.
  - Negative coordinates on the zero-edge axes (the −9999 truth sentinels) are far outside the grid. Their membership
    (−1) is unchanged by any step of order s.

**(iii) Inside the zone δ_k = 0, and the protocol move alone cannot cross.** A float32 x within one spacing of an edge e is
one of three cases:
- **(a)** e itself, when e is representable. δ_s = 0.
- **(b)** round₃₂(e), the nearer neighbour of a non-representable e. δ_s = 0, by the exact-edge rule.
- **(c)** any other float32 within one spacing of e, at distance d. Then d ≥ 0.56 s:
  - the farther neighbour of a non-representable edge lies 0.56–0.96 s away (the table below);
  - the float32 next to a representable edge lies d = s away, in its own spacing.

  The protocol move has |δ_s| ≤ ½ s + ε < 0.56 s, so it cannot reach e.

**The neighbours of the 21 non-representable edges** (diag.json, measured in each neighbour's own spacing):

| axis | non-representable edges | nearer neighbour (spacings) | farther neighbour (spacings) |
|---|---|---|---|
| pt | 8 of 15 | 0.04–0.44 | 0.56–0.96 |
| pz | 0 of 17 | — | — |
| eavail | 4 of 8 | 0.20 | 0.80 |
| q3 | 5 of 8 | 0.20–0.40 | 0.60–0.80 |
| W | 4 of 7 | 0.20–0.40 | 0.60–0.80 |

At every one of the 21 edges, the two neighbours share one spacing; no edge is within a spacing of a power of two.

**(iv) The guard's result is unchanged, for every input** (the director's item 4). By (ii) and (iii), no coordinate
changes cell:
- in stage 1, under protocol jitter plus δ_k;
- in stage 1, under protocol jitter alone, which matches the diagnosis's 0 and FD-STAB's 51 jitters;
- in stage 2, under δ_k alone, which is (ii) with δ_s = 0.

The guard stays as the backstop. The count is now also recorded: every product's `ens1` block carries `moved_rows`,
the guard's own `cell_membership` count per class, and each task logs it. The analysis stops (gate **E5**) unless every
product records 0 in every class. **The dry rerun's receipt must show 0 moved rows at all nine tasks.**

**Where the edges come from.** The edge lists used here are `project_cov_nd.AXIS_EDGES` at M. Their counts and their
non-representable sets equal the npz's (diag.json). **The rerun's connect rechecks every precondition of (ii) and (iii) on
the npz's own edges,** at 0 node-h under the sourced environment. It refuses unless all three hold:
- d_min > 1 + 2⁻²⁰ spacings on every axis;
- every non-representable edge's farther neighbour lies more than ½ + 2⁻²⁰ of its own spacing from the edge;
- no non-representable edge has a power of two as a float32 neighbour.

(The second and third conditions were added after RS1's read, as the audit's low on §3(iii)(c).)

**A harmless tie, for completeness** (also added after RS1's read). The float64 sum x + δ can round up to exactly
x + ½ s. That is still within the bound of (i), so it is covered.

**The zone's width is one spacing because of (i).** A REQUIRED mutant narrows it to ½ spacing, which leaves the farther
neighbours moving. Another widens it to 2 spacings, which zeroes coordinates outside the declared zone. A third makes
the boundary strict, which excludes exactly-one-spacing values. A fourth uses the edge's spacing in place of the
value's, which includes two-below-a-binade values. All four are killed (§6).

## 4. The population: part of the estimator's definition

These are the coordinates the zone takes out of the internal jitter, beyond the exact-edge values, counted on the base
input x (receipt #909, item 4: 0 < |x − e| ≤ s(x)):

| class | coordinates in the zone, not on an edge | of rows |
|---|---|---|
| MCgen | 104 | 32,849,103 |
| MCreco | 57 | 32,849,103 |
| measured | 15 | 4,091,707 |
| bkg_reco | 3 | 621,547 |

**Exact-edge values,** which were already unmoved: 293,319, 233,805, 48,171 and 11,516.

**The effect on the estimator.** E₉₆'s internal perturbation now leaves out 179 coordinates. They are on rows that the
fine grid places within a float32 spacing of a cell boundary. Everything else in E₉₆ (N, the seeds, the statistic and
the bars) is unchanged.

## 5. The withdrawal of §2.3, swept by claim

**The claim:** that the combined move cannot change membership, so the internal jitter preserves the grid. These are
the sites on main that state it or rely on it:
- **`ENS1-DECLARATION.md` §2.3** states it. It is struck in place, with a pointer to this addendum.
- **`ENS1-DECLARATION.md` §3.2** relies on it. "Every k of one truth must give the same `xtrue_flat` bitwise, since the
  internal jitter preserves grid membership". The reason is restated as "preserves it by construction (A1 §3)". The gate
  itself is unchanged.
- **`ensemble_estimator_probe.py`'s module docstring** describes the internal jitter. It now states the zone, and names
  §2.3 as withdrawn.
- **The tests:** no test asserted the claim. `test_a_move_across_the_grid_is_refused_before_the_build` tests the guard,
  which stays. The new tests in §6 assert the amended rule.
- **`ENS1-BINDING-1.md` and `ENS1-BINDING-2.md`** were checked and do not state it. The rebinding will cite this
  withdrawal.

**The sweep:** every ENS1 file on main was searched for the claim's terms ("cannot reach", "below one float32 spacing",
"total move", "preserves grid membership", "§2.3"), and every hit was read.

## 6. Tests and mutants

**The new tests** (`tests/test_ensemble_estimator.py`):
- **`EdgeZone`:**
  - the zone is one spacing, inclusive, and no wider;
  - each axis uses its own edges;
  - the float64 edges are used, not their float32 rounding;
  - the binade case: one float32 below the power-of-two edge 0.5 is in the zone, two below is out, and two below never
    crosses under protocol jitter plus δ_k over 200 seeds;
  - the zero edge: 0 and the smallest subnormal are in the zone; two and three subnormal spacings are out, they move, and
    they never cross below 0 over 200 seeds;
  - the internal jitter never moves a zone coordinate, and moves the rest.
- **`EdgeZoneEndToEnd`:** a lattice fixture with the non-representable edge 0.2 on axis 3, and 800 MC-truth rows at its
  farther neighbour.
  - It runs through the bound runner and its guard, at protocol seed 1 and k = 1–4.
  - Without the zone, it is refused at every k, with 11–17 rows moved, which reproduces attempt 1's failure.
  - With the zone, it passes.
- **The recorded count:**
  - every stability and F₆₄ product records `moved_rows` = 0 in every class;
  - the analysis stops on any nonzero record (gate E5).

**The REQUIRED mutants** (`tests/ensemble_estimator_mutation.py`), each killed by its named test:
- the zone removed;
- the zone at ½ spacing;
- the zone at 2 spacings;
- the boundary strict;
- the edge's spacing in place of the value's;
- axis 0's edges for every axis;
- the edges rounded to float32.

The E5 gate removed and `moved_rows` left unrecorded are also killed. The receipt is `receipts/mutation-receipt.txt`.

**Added after RS1's read, as audit fixes** (A1-C1 and A1-C2, coverage-5b-audit on #912). These are tests and harness
only, with no design or production-code change:
- **E5 at all three sites:** a nonzero count in any class, or a missing record, STOPs at stage 1, at the F₆₄ base and in
  stage 2.
- **The closure path** records its count.
- **The logged count's provenance:** it is nonzero with the zone disabled on the edge-0.2 fixture, so it compares the
  given coordinates with the jittered ones.
- **The last, inclusive edge:** values on it and one spacing either side are in the zone, two below are out, and none
  changes cell.

Their REQUIRED mutants are the audit's B16, B17, B18, B19, B14, B12 and B03.

## 7. The rerun: root, products and cost

- **A fresh root,** `/pscratch/sd/j/josephrb/ens1-a1-20261108`. Attempt 1's root, `/pscratch/sd/j/josephrb/ens1-20261107`,
  is left intact as evidence. Its five products are evidence by digest only (#908), and nothing in them is opened or
  analysed.
- **F₆₄ is recomputed in the fresh root** (the director's ruling). The rerun's receipt records a bitwise comparison of the
  new F₆₄'s `xsec_flat` and `xtrue_flat` with attempt 1's. F₆₄ carries no internal jitter, so the amendment should not
  touch it, and **a difference is a finding and STOPs**.
- **The cost:** attempt 1's 0.1586 node-h counts against stage 1's 55.0. The cap is unchanged. The rerun is again a 9-task
  dry run at `--time=0:45:00`, then the projection gate, then 6 shards after the director's go.
- **The chain:** coverage-5b-audit audits this addendum and its code, then the director rebinds with an M line, then the
  dry run is redone.
