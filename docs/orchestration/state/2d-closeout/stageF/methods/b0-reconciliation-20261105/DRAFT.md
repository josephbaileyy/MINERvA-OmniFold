# B0's reconciliation sentence: the drafting record (2026-11-05)

**Under** `DECISION-20261102-joseph-bias-and-stabilisation-routes.md` item 5, which leaves B0's reconciliation
sentence undecided. The director brings its wording to Joseph with the probe's outcome
(`OUTCOME-20261105-fd-stab-none-pass.md`), through a PRD-referee read.

**Status:** a draft for Joseph. **Nothing is committed to the paper or the note** before his answer.

## The sentences, after the PRD-referee read and the director's changes

They go in paper Sec. IV F, after "…so the estimator fails a data-stability requirement of at most 0.3 (median) and
1.0 (maximum) statistical standard deviations."

> The training-seed block of Sec. IV A is zero because, in the unfolds we ran, the result is bitwise independent of
> the training seed and of input row order; this is distinct from the sensitivity to rounding-level input changes
> quoted above. That sensitivity enters the reported statistical block by construction: each of its 50 bootstrap
> replicas refits the whole unfolding with its own rounding-level perturbation of the inputs. On the finer joint cells
> (this share was not measured on the 16 reported cells), the rounding spread is about 37% of the statistical variance
> and below a tenth of any total uncertainty (Ref. [14]); the quoted 2.6 statistical standard deviations is the
> largest shift, over 153 quantities (the joint cells, the (E_avail, W) cells and two totals) under two such
> perturbations of the data, not the typical one. A declared probe on simulated pseudo-data of two-fold cross-fitting
> and of two tree regularisations found no variant that met the data-stability requirement, so the estimator is
> unchanged (Ref. [14]).
> <!-- Search: (jitter|rounding) with (R00|R15|sixteen|16 cells|16-cell), git grep over docs/orchestration and nd-unfolding/*.json @ 5551cbbeb013 (the 16-cell hits construct the statistical block from jittered replicas, PROVENANCE-20261031-declaration-v-fd-16-cell-blocks.md :114, or quote this draft; VL155 measures the J cells and FD-STAB s5e's 153 functionals; none measures the rounding share on R00-R15) -->

## The read and the changes

The PRD-referee read is in `prd-read/` (the director's prompt and the reviewer's answer, verbatim, with
SHA256SUMS: answer `368e74d5…`). Its verdict is **USE REVISED**. The director ruled on its proposed text:

1. **Sentence 1:** the reviewer's wording, with "in the unfolds we ran" scoping the bitwise claim. It separates seed
   independence from rounding sensitivity.
2. **Sentence 2:** the reviewer's wording, with these changes:
   - "enters the reported statistical block by construction", with the 50-replica construction;
   - the 37 % is scoped to the joint cells. The reviewer's "(the ratio was not measured separately on the 16
     reported cells)" names a ratio that the sentence does not print. It reads "(this share was not measured on the
     16 reported cells)" instead, with the same scope and the same single caveat;
     <!-- Search: (jitter|rounding) with (R00|R15|sixteen|16 cells|16-cell), git grep over docs/orchestration and nd-unfolding/*.json @ 5551cbbeb013 (the 16-cell hits construct the statistical block from jittered replicas, PROVENANCE-20261031-declaration-v-fd-16-cell-blocks.md :114, or quote this draft; VL155 measures the J cells and FD-STAB s5e's 153 functionals; none measures the rounding share on R00-R15) -->
   - "the quoted 2.6 … is the largest shift, not the typical one", with the population the reviewer left in brackets
     taken from the record (ledger row 4).
3. **Sentence 3:** the lane's draft wording, kept. The director's prompt misstated fact 4. The record (fd_stab.json,
   verdict NONE_PASS) shows that no candidate met the stability bar at all. So "found no variant that met the
   data-stability requirement" is accurate, and stronger than the reviewer's "without worsening bias".

**Caveats:** only what the reviewer listed, the scope to the joint cells and "not the typical one", with no others.

## Ledger

| id | clause | source |
|---|---|---|
| B0-1 | the training-seed block is zero because, in the unfolds run, the result is bitwise independent of the seed and of row order | KNOWN_ISSUES.md row 80 ("Seeds and row order are inert (bitwise / ≤ 1.4e-10 σ)"); s5e `assess_receipt.json` (`84266e30…`) A3 `seed_and_permutation_max_over_sigma` (seed 43: 0.0; permutations 1.4e-10, 8.6e-11); the note's sec_fived16.tex :96 ("the unfolds at the other seeds are bitwise equal to the central one, so the measured training-seed block is zero in every cell"); S1-DECLARATION.md :69 (C_seed over seeds 42–54) |
| B0-2 | the statistical block's 50 replicas each refit the whole unfolding with their own rounding-level perturbation | S1-DECLARATION.md :66 ("`data_b{1..50}_j{101..150}.npz`, 50 refit-per-replica data bootstrap replicas with jitter"; "with the refinement refit") |
| B0-3 | on the joint cells the rounding spread is about 37 % of the statistical variance and below a tenth of any total; not measured on the 16 cells | VL155 (`state/s5p/stage2/stage2_receipt.json`, `0daa7cd8…`: "data rounding spread median 0.23% (J) inside the bootstrap (0.37%; consistency 1.02, absorbed)"); KI-80 ("≈ 37% of its variance … Relative to any total uncertainty (≥ 6%) it is below 0.1"); the note's sec_5d.tex :91 ("about 37% of the bootstrap variance and below a tenth of any total uncertainty"). The population measured is the J cells (VL155's "(J)"), which is why the sentence scopes the share to them |
| B0-4 | the 2.6 is the largest shift, over 153 quantities under two perturbations of the data | s5e `assess_receipt.json` A3 `data_rounding_probe_over_data_sigma`: max 2.5838 at J145, median 0.783, in data-bootstrap σ; `functional_names`: 153 (109 J, 42 EW, `EW_all_ones` and `total_integrated`); contract amendment 3 (`state/s5e/contract-amendment-3-candidate-R-and-assessment.json`): "the real data under R with edge-safe float32-ulp perturbations, seeds 1 and 2"; OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md §4 A3; the note's sec_5d.tex :91 ("a median of 0.8 and at most 2.6") |
| B0-5 | the probe found no variant that met the data-stability requirement, so the estimator is unchanged | OUTCOME-20261105-fd-stab-none-pass.md (verdict NONE_PASS: every candidate fails the bar, means of the median 0.528–0.861 and of the max 4.22–6.67 against 0.3 / 1.0); the readout `fd/receipts-stab-a1r/readout/readout-2/fd_stab.json` (`653356ae…`); FD-STAB-DECLARATION.md §6 ("No estimator change proceeds from this probe"). The outcome's rule, "No sentence may present [B2's lower spread] as an improvement found", is kept: the sentence gives no candidate's spread |

**The units.** "Statistical standard deviations" in the 2.6 clause is the real data's bootstrap σ: 100 replicas in s5e
A3 (`assess_receipt.json` `data.data_boot_replicas`), as in the sentence before it in IV F. The 37 % is of the s5p
bootstrap's variance on the J cells.

**Note counterparts,** after Joseph's answer:
- sec_fived16.tex :96: the jitter in the statistical replicas (B0-2);
- sec_5d.tex at the stability paragraph: the B4 outcome (B0-5).

The note already states B0-1, B0-3 and B0-4.
