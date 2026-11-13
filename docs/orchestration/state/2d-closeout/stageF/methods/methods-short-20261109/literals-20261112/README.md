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
- **§3.3's "0.47 % of the expected signal" is keyed after all (the director's pointer, 2026-11-13):** the source is
  jt-unsup-share, computed from s5c/b1/partition_scan_2.json (7b49b52d) level H3. It is the 243 coarse cells'
  expected reconstructed signal outside the support rule (s5p_stage1_inspect.py:49, :273: both the reco signal and the
  truth weight ≥ 1000), over the total. The asserts reproduce M4-DEFINITIONS.md:218's 109 supported cells and 25
  unsupported cells with signal. The pinned stage1_inspect.json holds only the 109 reported J cells, so it cannot give
  the share.
- The exposure 1.057×10²¹ POT is a data constant (the note's value).

**The Supplement** (`supplement-decimals.txt`, the 118 decimal literals before keying; journal-editor, 2026-11-13):
- **Keyed:** make_values_fived16.py `supp_literal_values()` holds 107 keys, each asserted against a pinned record. It
  reuses existing keys where the quantity is the same (rp-pb-unf, cov1b-win-*, prr-floor, prr-tq). The 0.69 of the
  132-direction reading stays typed for #981's quote Q23; check_round.py LITERAL_KEYS asserts it equals pp-dbar.
- **Prose-only sources** (the director's ruling B): VALIDATION_LEDGER.md and 2D_OMNIFOLD_STUDY_STATUS.md are read
  through exact text anchors, each required to match once. These working documents are not sha-pinned.
- **The published flux median** is computed from the release files (cov_ptpl_..._flux.txt a2ba53fd, the data result
  and bin_mapping.txt) and asserted against stageB/verify-c04-x01/VERIFICATION.md:130's 4.014 %.
- **Corrections the record check found** (the director's rulings A1-A5 and D, 2026-11-13): S6.2's 4.8 is now 4.7;
  S7's 46.09 is paired with the Hartlap-corrected T; S2's 0.15 % is now the weighted 0.086 %; S4.1's refined range
  covers the same six cells as the purity range; S4.2's signed total is given with its sample; S7 says "at or below".
- **Left as typed:** `supplement-constants.txt` lists the 50 typed decimals that remain: 49 design constants (cuts, bin edges, definitions, levels,
  thresholds, versions, input uncertainties) and that quoted 0.69. `check_supplement_constants.py <worktree>` fails on any typed decimal
  that it does not list. Table column widths are excluded.
