# r22 Step 4 part 2: the 2D figure restyle installed (2026-11-01)

**Under:**
- STEP4-PLAN.md (R, T3, T6);
- fig-restyle-20261031/DECLARATION.md §5;
- BINDING.md, BINDING-A1.md and BINDING-A2.md;
- AMENDMENT-2.md §6;
- Joseph's "Install them" after his third look at `review-a2/` (the director, 2026-11-01).

**Result:** the eleven restyled figures are installed in the note and the primer, and the captions that describe them
are corrected. Every adoption check of STEP4-PLAN §3 passes. Nothing in the paper or the values files changes.

## What changed

**R, the install:**
- `make_figures.sh` installs the eleven from `fig-restyle-20261031/figs-a2/`, each digest-checked
  (`install_restyle_fig`). The RE-2 part C lines stay as dated comments.
- The eleven G rows of `re2-integration/ledger.tsv` are re-pointed (ruling 1: re-point, do not replace). They use a
  7-column form that names the copy's directory, pointing at `figs-a2/` and `run-a2/after/SHA256SUMS`.
- `fig-restyle-20261031/DIGESTS.tsv` gives each figure's RE-2 and restyled digests, with both SHA256SUMS entries.
- `re2-integration/check_ledger.py` gains `--figures`: the G rows and Fig. 1 only, with a two-way self-test. Its full
  run is stale on main, which this round reports and does not repair: its V, M and F rows record the RE-2
  integration's text of 2026-10-23, which later rounds rewrote, and one names a file the paper round removed.

**The captions** (`sec_results.tex`; `primer_body.tex`):
- **C1:** Fig. 7 says what its error bars are:
  - on this measurement, the weight statistics of the reweighted simulated sample, combined with the propagated bin
    error of the completeness ratio, which is one by construction. They are neither the data's statistical
    uncertainty nor the reported covariance;
  - on the published data, √diag of its statistical covariance;
  - the horizontal bars span the bins.
- **C2:** Figs. 9 and 10, and the body's error-bar paragraph, say the same.
- **C3:** Fig. 13 names the red circles, the black squares and the blue "GENIE 2.12.6 + MINERvA Tune v1" line, and
  says "Uncertainties are not drawn".
- **T3:** Fig. 14's panels are labelled (a) and (b), and the stale "no printed titles" clause is dropped.
- **T6:** the primer's Tune v1 curve is blue.

## Checks (STEP4-PLAN §3, and DECLARATION §5's)

| check | result |
|---|---|
| the ledger (`step4-install/check_ledger.py`, base `70eaad8fc`) | 6 rows, 18 probes, 5 changed base sentences, 0 failures. The paper and the values files stay byte-identical (PROTECTED) |
| the install's digests (`re2-integration/check_ledger.py --figures`) | LEDGER FIGURES :: PASS, with 16 G rows (11 of them re-pointed) and Fig. 1. The figures self-test PASSES both ways: a wrong pin, and a re-pointed row at the RE-2 directory, each fail |
| the two-direction review (`review.md`) | no false colour, marker, name or panel label. One Medium (the completeness term was named as an uncertainty) and three Lows are fixed; one Low, on a comment, is kept |
| agy's targeted read (`agy-read.md`, on the final text) | every difference listed is declared. The control caught 3 of 3 |
| `build_all.sh` | PASS, with all five PDFs and every gate |
| the 4.0 pt gate (check 7, the drawn sizes) | PASS in the bound run (`run-a2/CHECKS.txt`: 5.00–5.92 pt). The installed figures are those files, byte for byte (`figures/*.pdf` = `figs-a2/`, 11 of 11) |
| ASCII, on the new note and primer PDFs | no raw `_` or `^` in the text of the crops of note Figs. 7–14, nor in the installed fig13 that the primer prints. **Outside this round:** the primer page that prints fig13 also prints another figure, the extended-acceptance maps, whose axis labels read "p_T bin (extended)" and "p_\|\| bin (extended)". That figure is not one of the eleven and is unchanged |
| the re-crop record (`recrop/`, `figdiag.py` items, crops and measure on the new build) | for Figs. 7–14, each word-box minimum equals the dry run's "after" column of SIZE-MEASURES.tsv (fig13 2.35, the slices 2.06 and 2.08, the spectrum 2.19, Fig. 13 2.78, the maps 4.13, the pull 3.49). So the new note prints the restyled figures. This is a record only: that instrument does not measure matplotlib text (DECLARATION §5 item 4) |

## Not done here

- the departure sentence after Eq. (1), held by the director (#620 item 3);
- Joseph's four editorial fixes (#620), after #619 lands.
