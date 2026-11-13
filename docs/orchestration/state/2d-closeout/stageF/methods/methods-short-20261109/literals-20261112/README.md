# Printed literals without a key: the sweep after #1132 (2026-11-12)

helper-2's D6 clean-environment test (#1132) found five printed literals that no builder checks. The director asked
for those to be keyed and for a sweep of the body and the Supplement.

**Keyed in the paper body** (make_values_fived16.py literal_values(); each value is asserted, and every source is
pinned in READOUTS):
- **Table 4:** T = 382.8 and 138.5 now print c2c1-T and c2c1-max, the keys §4.2 already uses. T = 194.4 and 39.04
  print ibu16-T and ibu16-q997.
- **§6.1, from VL155** (s5p/stage2/stage2_receipt.json 0daa7cd8, study_N/N1_data/J): 0.23 %, 0.37 %, and B0's
  "about 37 %" (median_absorption 0.369).
- **§6.1, the lower-capacity variant's 2.5:** s5e/cand/review2/r2_recompute.json c0f20299,
  assessment.B0_rounding_probe_diag.over_R_data_sigma_max 2.48.
- **§4.1 and Table 4, from RE-2's tension anatomy** (re2/.../tension_report.txt dee699e5): the condition number
  1.5×10¹², the 73 and 139 kept modes with χ² 136 and 285 (χ²/ndf × 205), and χ²_norm 0.04 against χ²_shape 465.
- **§6.1, RS1** (rs1_read.json 9938e168): the ratios 6.2×10⁻⁷ and 1.07×10⁻⁶, and K4's order 10⁻¹⁰ (D_P 4.1×10⁻¹¹ and
  1.2×10⁻¹⁰).

**Left as typed in the body, listed in `paper-numerals-before.txt`:**
- **Design constants and definitions:** the 0.3/1.0 requirement, 16, 20, 50, 153, 109, 42, 205, 300, 400/31, 100/8,
  135 MeV, the bin edges, 10 iterations, 1000 events, the generator versions, 6 GeV, the phase-space cuts, 14×16, the
  95 % CI, the LL5D sizes 0.025 and 0.08, and the Eavail factor 1.17.
- **One result with no record found:** §3.3's "The remaining cells contain 0.47 % of the expected signal". No
  committed record holds it. The director should name its source, or the sentence should drop the number.
- The exposure 1.057×10²¹ POT is a data constant (the note's value).

**The Supplement** (`supplement-decimals.txt`, 118 decimal literals) is journal-editor's to key.
