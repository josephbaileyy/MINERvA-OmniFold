# OUTCOME: valid regions of the sixteen-cell result under V-ATLAS and V-PRIOR, with reading (3) descriptive only (2026-11-07)

**By:** the valid-region lane (session director-helper-2).

**Under:** [`BINDING-1.md`](state/2d-closeout/valid-region-20261107/BINDING-1.md) (#895). It binds
[`DECLARATION.md`](state/2d-closeout/valid-region-20261107/DECLARATION.md) rev 2 and its code at
M = `0687d6f2776b3ad691568f701de3aff166d9ca2a`.

**The read:** local, at M, at 0 node-h, with no cluster contact.
- rc 0, and all 11 controls PASS.
- The receipt is [`receipts/read/`](state/2d-closeout/valid-region-20261107/receipts/read/) (#897):
  `readout.json` sha256 `91bb604e3a62e2654e611750830e225061e5c0b0255b12455a23ac9be4eec84c`.
- Every number below is that file's value at the key path given, written `RO:<path>`.

**MEASURES:** for each of the 16 reporting cells, its class under two separately labelled validity rules:
- V-ATLAS: the ATLAS User Guide's thresholds applied per cell;
- V-PRIOR: the lane's operationalization of the advisor's "bias spread comparable to the prior spread".

Then, within the valid cells, the descriptive departures of the data from the simulation's prior.

**CITABLE FOR:**
- each cell's V-ATLAS and V-PRIOR class, with its inputs, as defined in the declaration;
- reading (3)'s printed quantities (r_c, z_c, r_Q, z_Q, the contrasts), each labelled **"computed after the pulls
  against the prior were seen (L4)"**;
- the record that the ATLAS User Guide states no prior-spread validity rule (declaration §1, re-runnable).

**NOT CITABLE FOR:**
- **coverage.** No interval is validated, and the fake-data tests grade bias, not coverage;
- **a measurement.** These are diagnostics of the estimator on committed products. No reported value changes;
- **any physics claim about the generators;**
- **the cause of any departure;**
- **V-PRIOR, or its threshold of 0.5, as ATLAS's,** or as the advisor's own formulation;
- **a non-valid cell as excluded, wrong or unreported;**
- **held-out truths;**
- **ATLAS guide item 5,** which is not met;
- **that the 2D mismodeling is localized in the extra dimensions, or that it is not,** in either direction;
- **reading (3) as a test.**

## 1. V-ATLAS (the guide's thresholds, per cell)

| rule | outcome |
|---|---|
| A1: mc_neff_truth ≥ 5,000 | met in all 16 cells. The smallest is 331,614 in R07 (`RO:readings/V-ATLAS/cells/R07/mc_neff_truth`). The n_eff is the simulation's weights', a disclosed deviation from ATLAS |
| A2: data stat σ/f < 0.15 | met in all 16 cells. The largest is 0.368 % in R05 (`RO:…/R05/stat_rel`) |
| A3: \|z\| ≤ 2 at all 12 graded truths, under the reported covariance | **fails in R02 and R06,** each from the A7 GiBUU hybrid truth alone: z = +4.19 (`RO:…/R02/z/A7_gibuu`) and +4.53 (`RO:…/R06/z/A7_gibuu`). Every other truth–cell pair has \|z\| ≤ 2. The next largest are 1.89 (A7 GiBUU, R07) and 1.76 (Stage 0c GiBUU, R06) |

**V-ATLAS-valid:** 14 cells, every cell except R02 and R06 (`RO:readings/V-ATLAS/valid`).

**Print-only:**
- **Without the GiBUU-family truths on the p_∥ ≥ 4.5 cells, R06 passes A3** (`RO:…/R06/print_only`). That is where
  GiBUU lacks its E_ν > 20 GeV events (FD-DIRECTOR-RULINGS §5).
- **R02 is on GiBUU's own domain and fails either way.** A3 stays as declared, with GiBUU on all 16 cells, as the
  audit required.
- **Per truth,** p < 0.01 for A7 GiBUU (5.3 × 10⁻²⁸) and q3 (9.1 × 10⁻⁶) (`RO:readings/V-ATLAS/per_truth`). A
  per-truth p is not assigned to cells.
- **Guide item 5 is not met** (`RO:readings/V-ATLAS/guide_item_5`).

## 2. V-PRIOR (ρ = S_b/S_g, valid ⇔ ρ < 0.5 in all four noise combinations; the lane's operationalization)

**V-PRIOR-valid:** 14 cells, every cell except R08 and R15 (`RO:readings/V-PRIOR/valid`).

**The noise combinations agree everywhere:** no cell is "unresolved (noise)". The four combinations agree in every
cell, and ρ differs across them by at most 0.012.

| cell | ρ, the 4 combinations | S_b (raw) | S_g (raw) | class |
|---|---|---|---|---|
| R08 | 0.522–0.534 | 0.0337 | 0.0645 | not valid |
| R15 | 0.564–0.565 | 0.0553 | 0.0981 | not valid |
| R10 | 0.444 | 0.0706 | 0.1590 | valid, the largest ρ among the valid cells |
| R02 | 0.421 | 0.1209 | 0.2873 | valid |

The other twelve cells have ρ ≤ 0.34; the largest is 0.340, in R12 (`RO:readings/V-PRIOR/cells/<cell>/rho`).

**Print-only sensitivity:**
- **At threshold 1/3:** R02, R10 and R12 also become not valid, leaving 11 valid cells.
- **At threshold 1:** all 16 cells are valid.
- **With the GiBUU-family truths on all 16 cells:** R06 also becomes not valid.

**The audit's LOW, stated as a limit.** GENIE CV and Tune v1 may share MC events. If so, their errors are
positively correlated, and the subtracted S_g,sub is over-subtracted, which pushes ρ up, toward "not valid". That
is conservative for validity. Since the raw and subtracted combinations agree in every cell, no class depends on the
subtraction.

## 3. Where the two rules differ

| set | cells |
|---|---|
| valid under both | R00, R01, R03, R04, R05, R07, R09, R10, R11, R12, R13, R14 (12 cells) |
| V-ATLAS only | R08, R15 |
| V-PRIOR only | R02, R06 |

The rules test different things:
- **V-ATLAS's failures** come from one truth's closure pull.
- **V-PRIOR's failures** come from the size of the bias spread relative to the generator spread.

This record draws no conclusion from the difference.

## 4. Reading (3): descriptive only (declaration §6, audit VR-1)

**Computed after the pulls against the prior were seen (L4). No class, no sentence, not a test.**

**The data's departure from the prior** (Tune v1), per quadrant and over all four cells
(`RO:readings/reading3/quadrants`):

| quadrant | p_T, p_∥ (GeV/c) | r_Q | σ_Q | z_Q |
|---|---|---|---|---|
| Q1 | < 0.7, < 4.5 | +0.099 | 0.075 | +1.32 |
| Q2 | < 0.7, ≥ 4.5 | +0.046 | 0.051 | +0.90 |
| Q3 | ≥ 0.7, < 4.5 | +0.170 | 0.062 | +2.73 |
| Q4 | ≥ 0.7, ≥ 4.5 | +0.212 | 0.066 | +3.19 |

The per-cell r_c and z_c for all 16 cells are at `RO:readings/reading3/per_cell`.

**The contrasts between valid cells within a quadrant,** which differ only in E_avail, q_3 or W:
- **The counts:** 18 contrasts under each rule (`RO:readings/reading3/rules/<rule>/n_contrasts`). Every one is
  listed with its axes and its 3σ resolved size in [`readout.txt`](state/2d-closeout/valid-region-20261107/receipts/read/readout.txt).
- **Under V-ATLAS,** the largest |z_ij| is 2.44, for R04 − R05 in Q2.
- **Under V-PRIOR,** the largest |z_ij| are 3.46 (R05 − R06) and 3.32 (R06 − R07), both in Q2.
  - Both involve R06, which is V-PRIOR-valid but not V-ATLAS-valid.
  - R06 − R07 differ only in W.
- **Multiplicity:** 18 contrasts per rule. Taken independently, the chance of at least one |z| ≥ 3 by chance is
  about 0.05.

These quantities carry no reading.

## 5. Limits

The declaration's L1–L5 hold:
- **L1:** V-ATLAS rests in practice on A3, since A1 and A2 are met everywhere.
- **L2:** ρ compares spreads over different sets.
- **L3:** each spread rests on few elements, 3–4 generators and 8–10 correlated truths.
- **L4:** reading (3) is not blind.
- **L5:** the quadrant is the coarsest two-dimensional region the 16 cells resolve.

**The audit's LOW** is in §2.

**V-PRIOR's source.** If Joseph learns of a specific source for the advisor's prior-spread metric, V-PRIOR is to be
amended before any paper use (BINDING-1 ruling 5).

## 6. Not changed

The reported result, R00–R15, every covariance block, every fake-data readout, the paper and the note are all
unchanged. Any wording comes later, through a referee read and Joseph. Nothing is submitted, deposited or tagged.
