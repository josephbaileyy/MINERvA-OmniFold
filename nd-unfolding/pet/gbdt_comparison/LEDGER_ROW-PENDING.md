# Validation-ledger row for this study: numbered at integration

**Appended (2026-10-05):** integrated into `main` with PR #16's merge, as **VL168** in `VALIDATION_LEDGER.md` (the next dense id after the PET integration's VL164–VL167). The section below is the text as appended, with `VL-NEXT` replaced by `VL168`; the row is live in the ledger.

`VALIDATION_LEDGER.md` ids must be dense (`whose_row.py --check-ledger-ids`). On `main` at `52a2f6dd` the last id is
VL163. The PET final-design integration has claimed **VL164–VL167** for its four rows
(`pet-final-design-20260925` at `bc356b0c`, decision record § Review).

This branch therefore adds no ledger row. Adding VL164 would collide with that claim, and VL168 would leave a gap that
the hook refuses. When this branch is integrated after the PET rows, append the section below with the next dense id
(expected **VL168**) and replace `VL-NEXT`.

Until then the result is recorded here and in `REPORT-20261005.md`, but it is not live in the ledger sense.

---

## 2026-10-05 PET finalists vs GBDT on existing outputs: exact-paired, exploratory

Source: [report](nd-unfolding/pet/gbdt_comparison/REPORT-20261005.md).
- Plan frozen at `5f9c5a99` before any fit.
- PET operands at `bc356b0c`.
- 352 new GBDT fits on the look-1 final-bank units, with local CPU 5.31 core-h charged.
- Simulation only. PET stays diagnostic. `NO_ELIGIBLE_DESIGN` and every frozen verdict are unchanged.

| ID | measurement | verified value | disposition |
|---|---|---|---|
| VL-NEXT | Paired per FB draw on identical events, targets and scorer (look-1 units): PET finalists H2S1T24 K5 and L128S1T24 K4 against the matched study's scalar OmniFold (HGB h1, efficiency-corrected, `truth4_species`, k = 7 from DEV `kF0`). Exploratory, conditional on the banks, unadjusted 95 % t intervals | **E0:** H2 − GBDT +0.102 [0.084, 0.119]; L128 − GBDT +0.070 [0.051, 0.089] (n = 60). **E3:** +0.076, +0.070. **E4:** +0.055 [0.035, 0.075], +0.012 [−0.007, 0.031] (n = 40). **E5:** +0.009, +0.013 (level). **E0 ΣMSE ×10⁴:** 3.33 / 5.26 / 9.78. **Generator reweightings (D5 NuWro, NuWro′, GiBUU; n = 8):** PET worse by 0.12–0.25. **Moves-away units:** 2, 1, 0 of 224. **B2 D4d n down:** 0.0097 / 0.0122 / 0.0033 | **EXPLORATORY.** Not a ranking of the finalists, not an uncertainty or coverage comparison, not an adoption. Citable for: on these banks and at this scale, the point-estimate differences above against this GBDT. Not citable for: PET or GBDT being best, any real-data or uncertainty statement |
