# REPORT The GENCMP addendum E2 paper round (2026-11-02)

**By** the paper rewrite lane (Claude), for the director.

**Under:**
- Joseph's decision `DECISION-20261102-joseph-cmodel-keep-carbon-state-effect.md` (#680), items 2–4;
- E2's merged report, `FD-GENCMP-AMENDMENT-E-ADDENDUM-E2-REPORT.md` (#683, `63493acdc`), §3, §4, §5 and §7;
- the director's work order of 2026-11-02.

**MEASURES:** nothing new. Every value comes from E2's committed readouts through `make_values_fived16.py`:
- `fd/gencmp-e2/rerun1/chi2/e2.json`, sha256 `0aa73ebf…`;
- `fd/gencmp-e2/rerun1/sens/x_e2_sens.out.txt`, sha256 `223f3f88…`.

**CANNOT AUTHORIZE:** a claim, a reading or a wording. The changed sentences go to Joseph through the director, with
before and after (below).

**Commits:**
- `8bcea1714`: the round;
- `ad9403f5d`: the review's fixes (`review.md`).

## What changed

| item | change | where |
|---|---|---|
| 1. measured statement | the paper's C_model target clause is followed by the signed change in the with-arm total χ² per prediction when C_model's NuWro and GiBUU shape ratios come from CH: GENIE CV −0.92, GENIE + MEC −5.56, NuWro +0.17, GiBUU −2.68. It uses no seed clause and not e2.json's `reading.sentence`. The note gives every arm and kind (new Table 22, `tab:fived16-gen-cmodel`) | `paper_body.tex:233`; `sec_fived16.tex:343` and the table after `tab:fived16-gen-target` |
| 2. GiBUU's rise | the paper, the note, `sec_joint` and the primer now attribute the rise to pairing the CH prediction with C_model's carbon NuWro and GiBUU shape ratios: with CH ratios, GiBUU's CH total is 45.10, below its carbon 45.49. The hydrogen-sample clause is **kept**, scoped "With the reported C_model" (see below) | `paper_body.tex:233`; `sec_fived16.tex:339`; `sec_joint.tex:309`; `primer_body.tex:305` |
| 3. readouts | the note's table gives χ² with C_model removed (×0), as reported (×1), doubled (×2) and with CH shape ratios, for the four predictions, both arms and both kinds. Its paragraph gives the per-cell σ change (whole matrix, R02 −9.4 %, −9.5 % without C_PL,5D; R12 +0.3 %; C_model's own σ/f at R02 0.1136 → 0.0968, and at R12, where it is small, 0.0051 → 0.0075, +47.8 %). The paper cites the removed and doubled readouts once, for scale | `sec_fived16.tex`; `paper_body.tex:233` |
| values | `make_values_fived16.py` pins `e2` and `e2sens` by sha256 and adds 140 keys: 132 `e2-` and 8 one-decimal carbon χ² (`g-{nuwro,gibuu}-carbon-*-chi2r1`). **No existing key changes** (`VALUES-CHECK.txt`). Its new `e2_values` asserts each fact the text states (listed after this table). It has six self-test plants, each refused by its own assertion | `make_values_fived16.py`; `values_fived16.tex` |
| layout | a `\clearpage` ends `sec_fived16.tex`, so Sec. 10.6's three tables precede Sec. 11 | `sec_fived16.tex` |

**What `e2_values` asserts:**
- E2's carbon χ² is Table IV's, to 1e-10 in both arms.
- The receipt's controls all PASS, and its χ² equal e2.json's.
- Only NuWro's and GiBUU's rows of S change, and both do.
- Every prediction's χ² moves, and every χ² falls from ×0 to ×2.
- The largest |Δ| is GENIE + MEC's shape-only χ² without C_PL,5D, and it is negative.
- Removing C_model raises GiBUU's total most.
- GiBUU's CH total with CH ratios lies below its carbon total.
- The σ cells, their signs, the cell shared by the two arms, and that R12 is small.

**Unchanged:**
- the reported covariance (C_model stays on carbon, decision item 1);
- Table IV and every other printed value;
- `main_paper.tex`, `main_note.tex` and `sec_execsummary.tex`.

## The hydrogen-sample clause: kept

- **Still true:** with the reported C_model, in the generators' own definitions, GiBUU's total is 44.19 with GENIE's
  hydrogen, 45.25 on carbon and 47.55 with its own hydrogen. `gencmp_values` asserts that order.
- **Still needed:**
  - Joseph's decision of 2026-11-01, item 1, requires the clause: "It also says the sign of the rise depends on the
    hydrogen sample (44.2 with GENIE's hydrogen)."
  - #680 revises the rise sentence, but it does not withdraw that requirement.
- **Rescoped:** its numbers, like the rise, are under the reported carbon C_model. So it now begins "With the reported
  C_model, the sign of the rise also depends …", after the new attribution.

## For the director: one wording choice

**The choice:** the decision record says the rise comes "mostly" from the pairing. The text says it "comes from" the
pairing, and in the paper that GiBUU's total "falls instead" when C_model's ratios are also from CH.

**Why:**
- The pairing's share is 47.78 − 45.10 = 2.68, against the 2.29 rise: 117 %, and 134 % without C_PL,5D.
- With target and C_model matched, the correction lowers GiBUU's total, 45.10 against 45.49.
- "Most" would leave part of the rise to GiBUU, and none is left. The review raised this (`review.md`, finding 3).

If the decision's word is wanted, the change is three words: "Most of", "mostly" and "most of".

## For Joseph: every changed sentence, before and after (as printed)

### The paper (page 9, Sec. V B)

**Before:**
> For GiBUU the correction raises the total χ² by 2.3, from 45 to 48 for 8 degrees of freedom, and lowers the
> shape-only χ² from 25 to 22; the sign of the rise depends on the hydrogen sample, since with GENIE's hydrogen in
> place of GiBUU's own the total is 44.2, against 45.3 on carbon and 47.5 with its own hydrogen (all in the
> generators' own definitions; GENIE's hydrogen sample is thin, so this spread is largely its noise; Ref. [14],
> Sec. 10.6).

**After:**
> For GiBUU the correction raises the total χ² by 2.3, from 45 to 48 for 8 degrees of freedom, and lowers the
> shape-only χ² from 25 to 22. That rise comes from pairing the CH prediction with C_model, whose NuWro and GiBUU
> shape ratios are from carbon (below): with those ratios also from CH, GiBUU's total falls instead, to 45.1,
> against 45.5 on carbon with the reported covariance. With the reported C_model, the sign of the rise also depends
> on the hydrogen sample: with GENIE's hydrogen in place of GiBUU's own the total is 44.2, against 45.3 on carbon and
> 47.5 with its own hydrogen (all in the generators' own definitions; GENIE's hydrogen sample is thin, so this spread
> is largely its noise; Ref. [14], Sec. 10.6).

**Before** (the paragraph's last sentence, unchanged):
> … those contributions come from the generators' samples in their own definitions, with NuWro and GiBUU on carbon,
> not from the predictions compared here.

**After** (one sentence added after it):
> Taking C_model's NuWro and GiBUU shape ratios from CH instead changes the total χ² by −0.92 for GENIE CV, −5.56
> for GENIE + MEC, +0.17 for NuWro and −2.68 for GiBUU; the size of C_model is not calibrated: doubling it changes
> them by −2.21, −5.21, −0.83 and −2.28, and removing it by +14.57, +32.45, +12.55 and +119.05 (Ref. [14],
> Sec. 10.6).

| value | key | source |
|---|---|---|
| 45.1 | `e2-with-gibuu-total-chr1` | e2.json `chi2.with.gibuu.total.CH` = 45.0980 |
| 45.5 | `g-gibuu-carbon-total-chi2r1` | defs.json, GiBUU carbon, analysis definitions, reported = 45.4884 (the note prints 45.49) |
| −0.92, −5.56, +0.17, −2.68 | `e2-with-*-total-dch` | e2.json `chi2.with.*.total`: CH − carbon |
| −2.21, −5.21, −0.83, −2.28 | `e2-with-*-total-dx2` | x_e2_sens.out.txt `chi2.with.*.total`: doubled − carbon |
| +14.57, +32.45, +12.55, +119.05 | `e2-with-*-total-dx0` | x_e2_sens.out.txt `chi2.with.*.total`: removed − carbon |
| "not calibrated" | — | `paper_body.tex:81`, "not a calibrated bound" |

### The note (Sec. 10.6, page 77; Table 22 on page 78)

**Before** (`sec_fived16.tex:339`):
> … in the sixteen-cell comparison GiBUU's total χ², on its eight cells, rises. That rise depends on the hydrogen
> sample: with GENIE CV's hydrogen in place of GiBUU's own, …

**After:**
> … in the sixteen-cell comparison GiBUU's total χ², on its eight cells, rises, because the CH prediction is paired
> with C_model's NuWro and GiBUU shape ratios from carbon (below). With the reported C_model, that rise also depends
> on the hydrogen sample: with GENIE CV's hydrogen in place of GiBUU's own, …

**Before** (`:343`): the C_model target clause, then "Table 22 gives the comparison in the generators' own
definitions …". A source comment recorded the effect as not measured.

**After:** the clause, then:
> Table 22 measures the effect of that target. There, NuWro's and GiBUU's shape ratios in C_model are taken from
> their CH combinations in the generators' own definitions (the "CH (generator)" rows of Table 21), with everything
> else fixed; the reported covariance keeps them on carbon. Under the reported covariance the total χ² changes by
> −0.92 (GENIE CV), −5.56 (GENIE + MEC), +0.17 (NuWro) and −2.68 (GiBUU). Over both matrices and both kinds, the
> largest change is −6.07, in GENIE + MEC's shape-only χ² without C_PL,5D. Only the NuWro and GiBUU components
> change, but every prediction's χ² moves, because the components enter one matrix. With the CH shape ratios,
> GiBUU's CH total is 45.10, below its carbon value of 45.49 with the reported covariance, so the rise described
> above comes from pairing the CH prediction with the carbon shape ratios. For the scale of C_model itself, whose
> size is not calibrated, the table also gives the χ² with C_model removed and doubled. Every χ² falls as C_model
> grows. Removing C_model raises GiBUU's total most, to 166.83 from 47.78. With the CH shape ratios, the reported
> per-cell σ falls in 15 of the 16 cells and rises in R12, by 0.3 %. It falls most in R02, where σ/f goes from
> 0.1405 to 0.1273 (−9.4 %; −9.5 % without C_PL,5D). C_model's own σ/f changes most in R02, from 0.1136 to 0.0968,
> and most in relative terms in R12, where it is small: from 0.0051 to 0.0075 (+47.8 %). This measures C_model's
> dependence on the target only: its definitions stay the generators' own, its coverage is still not validated, and
> GiBUU's CH shape ratio carries the hydrogen label of §11.9. The changes are those of these data; their statistical
> uncertainty, from the data entering the unfolds that build C_model, is not measured.
<!-- absence-ok: scoping statement about what E2 measures (FD-GENCMP-AMENDMENT-E-ADDENDUM-E2-REPORT.md sec. 4: no addendum declared input resampling), quoted from the note, not a claim that a result does not exist -->

**The new Table 22:**
- **Contents:** 32 χ² (×0, ×1, ×2, CH) and 16 Δ_CH ("from unrounded values"), for the four predictions, total and
  shape-only, with and without C_PL,5D.
- **Agreement:** every cell equals E2 report §3 and §5 as rounded. `VALUES-CHECK.txt` lists each key with its
  file:line.

**Sources of the note's paragraph:**
- the construction: E2 addendum §0, "GENCMP step A's CH combination in the generator definitions";
- the limits: E2 report §7, and §4 for the statistical uncertainty, waived as a scoping statement;
- the "only NuWro and GiBUU" sentence: E2 report §3, "What moves";
- the σ figures: x_e2_sens.out.txt, `sigma`.

### The note (Sec. 11.9, page 89, `sec_joint.tex:309`)

**Before:**
> … in the sixteen-cell comparison, GiBUU's total χ² on its eight cells rises with the correction (§10.6).

**After:**
> … in the sixteen-cell comparison, GiBUU's total χ² on its eight cells rises with the correction, because the
> corrected prediction is paired with C_model's NuWro and GiBUU shape ratios from carbon (§10.6).

### The primer (page 12)

**Before:**
> … correcting both predictions to the hydrocarbon target moves both toward the data (in a separate comparison on
> broader cells it raises GiBUU's overall mismatch slightly), …

**After:**
> … correcting both predictions to the hydrocarbon target moves both toward the data (on broader cells GiBUU's
> mismatch rises slightly, from an uncertainty built partly on carbon), …

The clause keeps its length because the primer's last page was full: a longer version moved its last reference onto a
16th page.

## Checks, on the final text (`ad9403f5d`, then the records commit)

| check | result |
|---|---|
| `make_values_fived16.py --check` and `--self-test` | PASS: 2630 values, 2 figures equal their sources. Each of the six E2 plants is refused by its own assertion (matched on the message) |
| `check_values.py` (`VALUES-CHECK.txt`) | PASS: all 2490 base keys print their base value; 140 keys are added (132 `e2-`, 8 `chi2r1`); the 64 `e2-` χ² keys equal their readout fields as printed. Planting one changed base value or one changed `e2-` value makes it FAIL |
| the ledger (`check_ledger.py`, base `63493acdc`) | 6 rows, 29 probes, 6 changed base sentences, 0 failures; self-test PASS |
| `build_all.sh` | PASS: paper 12 pp, note 133 pp (131 at the base: the new table and the `\clearpage`), primer 15 pp; no "??" and no "[PENDING" |
| layout | **Paper:** one overfull box, the base's (9.7 pt, Table III). The longer paragraph reflows pages 9–12, and the data-availability paragraph now runs from page 11 onto page 12. **Note:** Tables 21–23 number in the order the text cites them and precede Sec. 11 |
| the rater copy | `make_rater_copy.sh` on the clean tree at `ad9403f5d` exits 0 and writes the blinded copy ("data-availability heading in reading order"); holddiff PASS (only hold text differs) |
| `check_held.py --fact-held` (`CHECK-HELD.txt`) | 3 flags, all pre-existing: G1:paper-g-08, G1:paper-s-08, G1b:paper-s-07 |
| the two-direction review (`review.md`) | nothing false and no decision violated. Of 2 Medium and 8 Low, 9 are fixed and 1 is not changed, with a reason |
| `generate_manifest.py --check --at-sha HEAD` | see the `[manifest]` commit |
| local CI (`run_ci.py`) | see the PR |
| the reading copy | 17 pages, each new page followed by its base page: the paper's pages 9–12; the note's pages 77–78, then its new page 79 (Table 23); the note's page 89 (base 88); the primer's page 12 |

Nothing is submitted, deposited or tagged.
