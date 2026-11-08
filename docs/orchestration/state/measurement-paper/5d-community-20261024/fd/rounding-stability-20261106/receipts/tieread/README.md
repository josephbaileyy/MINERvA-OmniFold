# RS1 dry run: the tie-invariance reading (coverage-5b-audit, 2026-11-07)

This is the reading that RS1-BINDING-2 ruling 2 asks for before RS1's full run. It is taken through real LightGBM,
on two products of the RS1 dry run (job 60970044, receipt PR #891).

**Order.** ENS1 had to be bound before this was read. ENS1-BINDING-1 merged on origin/main at `a47ba560` first. The
director then approved this connect: `connect_tieread.sh` sha256 `6e5935728b2303bb5a5ce9d56e8ef3e0d01488febf2b24806a3ad80250897951`
and `remote_tieread.sh` sha256 `080567e9966e3af92100bff218060fd549ac6f7caa07423c0c3fb641423f15ef`. Both files are
committed here, unchanged.

**CITABLE FOR:** what these two products show about tie invariance through real LightGBM, as described below.
**NOT CITABLE FOR:** any RS1 gate or reading (G1–G4, K1–K6, R0), which are made by `rounding_mechanism_analyze.py` on
the full run; a mechanism; anything about the real data.

## The connect (`tieread.out.txt`)

- **Where:** login05, 2026-11-07T18:40:44Z, 0 node-h. ssh's rc was 0, read unpiped.
- **The fence:** the embedded `cov2d_fence.sh` logic ran first: "no cov2d-* job queued or running".
- **The reads:** four files were copied with `dd iflag=noatime` into a new scratch directory. Their sha256s were
  compared with #891's `log-dry/SHA256SUMS` lines in a separate step (`sha256sum -c`): 4 of 4 OK.
  - V jitter 1: `runs/V/rs1_V_b-_j1.npz` and its `.trace.json.gz` sidecar;
  - A0's float64 seed-0 base: `runs/A0/rs1_A0_b-_j0.npz` and its sidecar.
- **The originals:** atime, mtime and size were identical before and after (`BEFORE` and `AFTER` lines).
- **The comparison** ran on the copies only, with omnifold_py310 under `-I`.
- **Cleanup:** the scratch directory was removed by its literal path.

## The reading

**xsec_flat**, V against the base, is not bitwise equal:
- 10,397 of 65,856 fine bins differ;
- the maximum relative difference is 2.97 × 10⁻⁹;
- the median relative difference among the differing bins is 4.28 × 10⁻¹⁰.

**The 15 recorded OmniFold fits** (5 iterations × clf1, clf2, reg, in recording order):
- **2 are identical apart from their split thresholds.** These are the first two in recording order; their roles
  were not printed.
- **13 differ beyond the thresholds.** The first difference is at fit 2 (role clf2), tree 0, node 3. It is a leaf:
  value 0.014322243460743978 (V) against 0.014322241727664248 (base), a relative difference of 1.2 × 10⁻⁷, with an
  identical leaf count of 3,990,552.

**The refinement tree** is identical apart from its split thresholds.

## What it supports, and its limit

- **The bin partition is preserved.** In the first two fits and in the refinement, the value-keyed jitter preserved
  LightGBM's bin partition through the real code: only the thresholds moved. That is RS1-DECLARATION §2 item 6's
  prediction.
- **The later fits are consistent with the declared exception.** Their first departure is a leaf value with an
  unchanged count, which is what changed training weights with the same partition would produce. That matches the
  exception declared in §2 item 6: the regressor predicts rows it did not train on, and its output feeds the
  later fits' weights. This is consistent with it, not a test of it.
- **The limit.** The comparison classified any non-threshold difference, leaf values included, as "structure
  differs". It therefore does not show whether the 13 later fits also change split features or counts. A
  split-versus-leaf breakdown per fit would need a second read with its own approval.
- **The scale.** The cross-section difference is at most 3 × 10⁻⁹ relative, about 10⁻⁶ of the protocol's jitter
  spread on this input. That spread is roughly 1.4 × 10⁻³ relative: FD-STAB's control median of 0.759 σ
  (`fd_stab.json`) times the median σ_rel of 0.19 % (range 0.07–0.67 %) over the 153 functionals
  (`state/s5e/cand/assess_receipt.json`, sha256 `84266e30…`). The reading therefore raises nothing against the full
  run. The go is the director's.
