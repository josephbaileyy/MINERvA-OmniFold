# OUTCOME 2026-11-08: COV2D, the 2D covariance's held-out-tune coverage test, reads UNDER-COVERS at both tunes

**Recorded by** the director (paper-tighten lane), from the two committed score records. Each reading is the bound
code's own; the director only transcribes it. Arithmetic the director added is labelled as such.

**The design:** `state/measurement-paper/5d-community-20261024/COV2D-DECLARATION.md`, bound by COV2D-BINDING-1 and
COV2D-BINDING-2, with addenda A2–A5. The readout is phases N and S of `cov2d_readout.py` (addendum A4).

**The records:**

| tune | record | sha256 | code M | receipts |
|---|---|---|---|---|
| AR23 | `fd/receipts-cov2d/readout/AR23/score_AR23.json` | `fe5263e904f65892ce26b75fb279441230713c38675c2a3615c59d561c4f5ce1` | `ac25b665` (A4) | null #888, score #893 |
| G18 | `fd/receipts-cov2d/readout/G18/score_G18.json` | `849766942b3ecd9e6e72fd5db9d1a59815796b3f917875f8d0122b0c639088ec` | `b1d56e4f` (A5) | null #914, score #916 |

- **The two code versions.** AR23 ran at A4's M. That is allowed by A5 ruling 5: at ndf = 204 the Cholesky check that
  A5 changes is not reached.
- **G18 needed A5.** G18's first phase S at A4's M was INVALID, with no reading produced (#890). It reran at A5's M,
  against a null recomputed there and shown equal in content to run 1's (#914).

Below, `[key]` is a key path in that tune's score record.

**The cost:** 0 node-h for both phases at both tunes (login nodes). The bulk products were made earlier, under
COV2D-BINDING-2.

## 1. The controls: all pass at both tunes

| control | AR23 | G18 |
|---|---|---|
| `stop`, `controls_failed` | [], [] | [], [] |
| §9.9 provenance on the 300 toys [`section_9_9`] | 300, problems [] | 300, problems [] |
| atime [`atime_checked`, `atime_moved`] | 304 checked, 0 moved | 304 checked, 0 moved |
| guarded opens with O_NOATIME [`open_audit`] | 316 of 316, 0 refused | 317 of 317, 0 refused |
| A5's reading rule (A5 M line, ruling 3) | not reached (ndf 204) | PASS for both grades: κ₂ 9.50 × 10¹¹ and 9.55 × 10¹¹; max_rel_diff 2.0 × 10⁻⁸ and 7.3 × 10⁻⁸, against tol 2.1 × 10⁻³ |

## 2. The verdict, per tune (declaration §5.2)

| | AR23 | G18 |
|---|---|---|
| **verdict** [`verdict`] | **UNDER-COVERS** | **UNDER-COVERS** |
| ndf [`grade.ndf`] | 204 | 205 |
| joint count in region, against k_J [`grade.joint_count`, `grade.k_joint`] | **0 of 300**, against 190 (flagged) | **0 of 300**, against 192 (flagged) |
| mean χ²/ndf [`grade.chi2_mean_over_ndf`] | 16.55 ± 0.17 | 24.17 ± 0.37 |
| flagged cells [`grade.flagged_cells`] | 29, 56 | 29 |
| test size under the null's law [`grade.size.per_truth_union_bound`] | 0.0348 | 0.0363 |

**The flagged cells,** by flat index i·16 + j (p_T bin i, p_∥ bin j). Each is attributed by the bound
`fd_1b_null.attribute` [`grade.attribution`]:

| tune | cell | p_T, p_∥ (GeV/c) | in-interval count, against k_c | s_c | pull mean (se) | pull sd (se) | driven by |
|---|---|---|---|---|---|---|---|
| AR23 | 29 | 0.07–0.15, 15–20 | 164, against 174 | 1.165 | −0.851 (0.037) | 0.636 (0.026) | **bias** |
| AR23 | 56 | 0.25–0.33, 6–7 | 148, against 174 | 1.316 | +1.039 (0.041) | 0.709 (0.029) | **bias** |
| G18 | 29 | 0.07–0.15, 15–20 | 148, against 175 | 1.347 | −0.964 (0.038) | 0.666 (0.027) | **bias** |

- **Cell 29 at AR23 is on AR23's weakened list** (§5.2), and its flag reads as any flag.
- **The leave-out-MEC variant** [`readouts.leave_out_mec`] changes no verdict. Under C_T⁻ the flagged cells are 29 and
  56 at AR23, and 29 and 30 at G18 (30: p_T 0.07–0.15, p_∥ 20–40). The joint count is 0 at both tunes. The record prints
  "no reading (the tune under-covers under C_T)", as §6 fixes it.

## 3. The descriptive readouts (§6): no verdict, no reading

| readout | AR23 | G18 |
|---|---|---|
| per-cell in-interval content, min / median / max (count / 300) | 0.493 / 0.763 / 1.000 | 0.493 / 0.730 / 1.000 |
| cells marked over-covering [`grade.over_covers`] | 90 of 205 | 67 of 205 |
| "passes, weakened by clipping" [`grade.weakened_pass`] | 53 cells; weakened share 0.263 | 10 cells; share 0.049 |
| spread alone, against C_T without C_model: p̂ min / median | 0.353 / 0.673 | 0.317 / 0.653 |
| bias \|mean error\|/σ_c: median / max; cells above 0.5 | 0.114 / 1.039; 6 | 0.092 / 0.964; 10 |
| realization check \|x̂_T − truth\|/σ_c: median / max | 0.111 / 0.967 | 0.116 / 0.794 |
| clipping reading (§6 (ii)): fires in | none (C2's prediction holds) | none (C2's prediction holds) |
| outlier cell 216 (p_T 2.5–4.5, p_∥ 6–7): flagged? \|R\| max / median in σ_c | no; 0.018 / 0 (15 toys undefined) | no; 0.021 / 0 (19 toys undefined) |
| coherent clipping offset Rᵀ C_T⁻¹ R: median / max | 1.20 / 6.67 (285 complete toys) | 1.23 / 6.98 (281 complete toys) |
| cross terms, max / median in data-stat σ [`cross_term`] | 0.052 / 0.0022 | 0.063 / 0.0022 |

**The predicted offset of the un-centred draws** [`readouts.predicted_offset`] is recorded in the products'
cross-section units, not in σ_c.
- **The director's arithmetic, not a field of the record:** dividing by √diag(C_T) from that tune's committed
  `blocks_<T>.npz` gives a median |offset|/σ_c of 0.25 (AR23) and 0.29 (G18), with a maximum of 2.19 (AR23) and 1.64 (G18).
  At the flagged cells it is −2.09 and +0.34 (AR23 29 and 56) and −0.15 (G18 29).
- **This draws no conclusion** about whether the offset explains any flag. The declaration fixes no such reading.

## 4. The test's limits (§5.2), stated beside the verdict

- **The false-flag rate** is at most 0.0348 (AR23) and 0.0363 (G18) per tune under the null's law, and below 0.10 over
  both tunes by the union bound. The toys depart from that law in known ways:
  - the Flux and pair-band draws are un-centred;
  - clipping truncates the shifts;
  - C08, C_model and the simulation-statistics part of C_stat are in C_T but not drawn, which can only lower the flag
    rate.
- **The resolution:** a per-cell deficit of about 0.10–0.13 in content, and about 0.08 jointly. Smaller deficits can
  pass.
- **One-sided.** Over-coverage is reported, not failed.
- **G18 shares its 2p2h model family** with one of the model term's generators.
- **The run-period block was not drawn.**

## CITABLE FOR

- **At each of two held-out GENIE v3 tunes** (AR23 and G18_10a_02_11b), with 300 pseudo-experiments each and the
  analysis procedure's 2D covariance remade at each tune's truth (model term included, run-period term excluded), the
  declared test reads **UNDER-COVERS**:
  - the joint in-region count is 0 of 300 at both tunes;
  - one cell (G18) and two cells (AR23) are flagged per cell, each attributed to bias;
  - the test's false-flag rate under its null's law is at most 0.036 per tune.
- **The flagged cells, their s_c, pull means and widths, and the per-tune χ²/ndf,** as tabulated above.
- **The descriptive readouts of §3,** as descriptions.

## NOT CITABLE FOR

- **Coverage of the reported intervals at the data's point** (Q_R is made at the data, not at T).
- **A coverage rate,** or any statement about truths unlike these two.
- **A cause of the joint under-coverage** or of any flag. That includes the director's offset arithmetic in §3, the
  conditioning of C_T, and the over-covering cells.
- **Anything about C_PL_R or C_model.** Neither is drawn.
- **Independence from the training rows:** "A held-out tune moves the truth, not the sample."
- **Replacing or removing the earlier fixed-truth failure** (VL162, `OUTCOME-20261005-2d-fixed-truth-coverage-fail.md`).
  It stays in the consolidated Limitations statement (#690 item 2). This result adds to it.
- **Any wording for the paper or the note.** That goes through the paper lane, a PRD-referee read and Joseph (§12).
- **The "both COVER" sentence of §13,** which is not available.

## What follows, as already fixed (§12)

- **The paper:** a neutral methods sentence stating the method, the facts (G18's shared 2p2h family; the result is about
  the procedure's covariance at those tunes, not the reported intervals at the data; the run-period block not drawn),
  and, for the under-cover outcome, the tune, the flagged cells, s_c, bias or width per cell, and the false-flag rate.
  It is drafted by the paper lane and read by a PRD referee and by Joseph before merge.
- **The note:** §12's list. The clipping rule with C2's and the toys' residuals, the outlier cell 216, the weakened
  cells and how each read, the ±1σ endpoint draws, the shared universes, the cross-term readout, the single realization,
  the toys' fixed simulation, C08, and §5.2's resolution.
- **Follow-up, recorded without interpretation:**
  - **Index conventions.** The record's `grade.attribution` keys (`R29`, `R56`) are positions in the 205-cell list,
    while `grade.flagged_cells` are flat indices. They coincide for these three cells (the director checked against
    C2's `efficiency.cells205`).
  - **The rule string.** `cholesky_check_minus.rule` prints C_T's formula string, while its κ₂ is computed from C_T⁻.
  - **The two A5 lows**, L-A5-a and L-A5-b, remain on the auditor's follow-up list.

Nothing is submitted, deposited or tagged.
