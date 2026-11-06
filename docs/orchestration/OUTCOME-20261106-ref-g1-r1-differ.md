# OUTCOME 2026-11-06 — REF-G1, the 16-cell binned head-to-head: R1 reads "differ"

**Recorded by** the paper-tighten lane, as director.

**The record:** `state/measurement-paper/5d-community-20261024/fd/receipts-ref-g1/a1-read/readout.json`, sha256
`4db170d36cffa0be2aeb53926e94158ef4e5e2e1d88fa50dd29baeace8ed6fd7` (#820). It was produced by the bound reader at M'
`0bb9a1bf` (REF-G1-BINDING-2-A1), against bars.json `ba4b6985…` (committed before Δ was formed, #818), with the gibu1
product pinned at `683b4936…`. The director read it from main.

## The readings, as the record states them

**Every control passes.** G-draw (50 replicas), G-pair, G-CV, G-cells (max_rel 0.0), and **G-IBU1 bitwise** on ks, F_fold
and F_sub. The re-run is at IBU-1's 1/1/1 threads on 2 CPUs.

**R1, central agreement: `differ`.**
- T = 194.4. The calibrated bars, from T's own simulated null at the realized composition (Joseph's decision of
  2026-11-04), are 28.12 (0.95) and 39.04 (0.997). C_Δ is positive definite, with condition 3.7×10³.
- **Beside R1, read by nothing:**
  - the χ²₁₆ bars, 26.30 and 35.89;
  - the Hartlap T, 185.2, against F bars of 29.39 and 46.09;
  - the stat-only-null sensitivity, T = 3,464 against 44.6 and 69.4.
- **T exceeds every bar printed.**
- **The stated direction:** the null treats the paired universe differences as scatter in Δ. If the two estimators
  respond to systematics alike, the reading leans toward "agree". So the "differ" reading is not an artefact of that
  choice.
- **Per-cell (Δ/f_(e), read by nothing):** the largest are R11 +21 %, R06 −18 %, R05 +12 % and R03 −7 %. The pulls are
  R05 +4.8, R06 −3.5, R09 −2.1 and R11 +2.1. The rest are within ±1.3.
- **Δ grows with IBU's iteration count:** for example R06 is −2 % at K = 2, −18 % at K = 5 and −43 % at K = 20. Every
  other K and variant is printed and read by nothing; the reading is at K = 5, as declared.

**R2, closure bias (descriptive).**
- At the NuWro closure: "IBU worse", with the median |residual| ratio 2.98.
- At Tune v1, the simulation's own truth: "IBU better", a trivial closure where IBU's residual is 7×10⁻¹⁶.

**R3, precision (descriptive).** The median σ_IBU/σ_(e) over the 16 cells is 1.37, and the per-cell ratios run from 0.77 to
4.05. Same blocks on both sides; the carried blocks are excluded.

## What it licenses (REF-G1-DECLARATION.md §5)

- **R1 differ:** "the reported cells depend on the unfolding algorithm at the level of T", as a measured estimator
  dependence against T's calibrated null.
- **R1 differ does not license:**
  - switching to IBU;
  - adding the IBU–(e) difference as a systematic, which would be a new block and is Joseph's decision;
  - choosing cells, K or a background treatment after the read.
- **R2:** the per-truth readings, beside IBU-1's, and no coverage statement for either estimator.
- **R3:** the 16 ratios, descriptively, and not "OmniFold adds discrimination" (limitation 3 stands).

## What follows

- **Paper and note.** Any sentence goes through the paper lane, a PRD-referee read of the exact wording, and Joseph
  (binding 1 ruling 6). No text is drafted before his decision on the item below.
- **For Joseph, batched with the publication-scope decision:** whether the estimator dependence enters the result as an
  uncertainty, a stated limitation, or both. That is §5's "a new block, Joseph's decision".
- **Compute:** 0.225 of 5.0 CPU node-h.

Nothing is submitted, deposited or tagged.
