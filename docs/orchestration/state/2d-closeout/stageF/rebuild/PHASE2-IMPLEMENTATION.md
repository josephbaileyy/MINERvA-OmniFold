# Stage F rebuild phase 2: implementation report (VL175 → Q in the deliverable sources)

**Implementer:** a Claude Opus 5.5 subagent of the paper-tighten lane (director), 2026-10-18, in the worktree branch
`stageF/rebuild-phase2-20261018` from `573b8cd0`. One fork of the same session edited `paper_body.tex`,
`main_paper.tex`, `primer_body.tex` and the Sec. IV gate; the implementer reviewed its diff and fixed one swallowed
sentence in it. Rules: [`PHASE2.md`](PHASE2.md); site map: [`PHASE2-INVENTORY.md`](PHASE2-INVENTORY.md); receipts:
[`REPORT.md`](REPORT.md) and [`outputs/`](outputs/).

**CITABLE FOR:** which deliverable source lines changed and why, by inventory row; the figure installs and their
digests; the gate changes; the scratch-copy build and gate results; the residual grep.
**NOT CITABLE FOR:** any claim (J3/R5), disclosure wording (J4: every `% J4 pending` / `% J3 pending` site is
unadopted), KI-85 (J5), a built or pushed PDF (B1–B5, J6), or the standalone note repository. The independent
review (PHASE2 §6.4) of `dab2ec2a` and the director's rulings on it are disposed in §7. No number was computed: every printed number is a phase-1 receipt field at the
sentence's printed precision, or a value already in the note.

## 1. Summary

- **Inventory rows:** all 205 rows of PHASE2-INVENTORY §2 have a disposition (§8; some rows are split, giving 217
  lines). By disposition: 143 changed, 50 unchanged with a reason, 24 J-marked only (after the review, §7: 144 / 50 / 23,
  since `app_statmethods.tex:487` changed). Most changed FACT and J lines also
  carry a `% J4 pending (Dn)` or `% J3 pending` comment.
- **By status (lines):** NUM 61 (57 changed, 4 J-marked: macro-only sites); FACT 38 changed; NR 17 (14 changed, 2
  unchanged, 1 J-marked); J 29 (11 changed by a factual qualifier, 17 J-marked, 1 unchanged); DER 1 changed (not
  printed); FIG 10 (9 changed, 1 unchanged); TOOL 19 (13 changed, 6 unchanged); OK 42 (40 unchanged, 2 J-marked).
- **Macros (values.tex):** `\uqMedian` 6.09 → 6.45, `\fluxBand` 3.65 → 3.75, `\chiCombined` 0.994 → 0.964,
  `\chiCombinedLog` 1.014 → 0.987, `\chiCombinedSubStat` 5.80 → 6.01; each comment names its receipt and keeps the
  history chain. No coverage macro changed.
- **Tables rebuilt:** tab:uq, tab:combine (both gain a run-period row), tab:band-medians, tab:variance-sources (gains a
  run-period row), the worked example, the audit table; the errata gains a 2026-10-18 block.
- **Retired material (Q6, Q7, Q12):** a new `app_history` subsection, `app:history-vl175` ("The VL175 construction:
  retired material"), holds the ten-seed scan, the earlier (VL170) bootstrap (its split-bootstrap paragraph verbatim)
  and the other VL175-era values. `fig:seedscan` is removed; the figure is linked at `ae198cc1`, not reproduced.
- **Log-normal χ² definition** added beside its first quote (app_statmethods worked example): δ = ln x_ours − ln
  x_paper, C_ln = (TotalCov + C_tot)/(p_i p_j), both scaled by the paper's values (REPORT §5).
- **Q2:** `sec_results.tex:5–7` now states what `fig:xsec` draws, from the producers: our points carry the
  `hXSec2D` bin errors (projections: `hXSec_pt` / `hXSec_pz`), read by `plot_2d_threeway_fig13.py` `th2_to_array`
  and `plot_2d_cross_section.py` `plot_1d_projection`; the published points in the top panel carry
  √diag(`StatOnlyCovariance`) (`paper_arrays`). The old "Published points carry the published total covariance" was
  also false of the producer and is replaced in the same sentence.

## 2. Figures (PHASE2 §4)

Byte copies from `outputs/`; each destination digest re-measured after the copy.

| deliverable file | before | after (source) | check |
|---|---|---|---|
| `figures/paper_fig1_validation.pdf` | `49766e26…` | `82665808e99056b1f79754647d7640078dffe94fc667691a979a22769022a0fb` (`outputs/fig1/fig1_validation.pdf`) | equals `RUN-fig1.txt` output digest; no CFS entry (Fig. 1 ran locally) |
| `figures/MEFHC_fig6_7_uncertainty_pt.pdf` | `65db5b0b…` | `c12f37d5d8a39dfc16f38897ce708ff24f4428257a1fbdb644791a7020222d46` (`outputs/fig67/`) | equals `SHA256SUMS.cfs` |
| `figures/MEFHC_fig6_7_uncertainty_pz.pdf` | `4d659851…` | `e3bfb7273609d0c9399c28591da0fc01e706ce3769b11ea722fceb2541d5f323` (`outputs/fig67/`) | equals `SHA256SUMS.cfs` |
| `figures/uq_spread_2d.pdf` | `fa175255…` | `79d6b35fe81fe71c71738996090b27c2fded2d990bb9bbae670927fbf253a7cb` (`outputs/stat/`) | equals `SHA256SUMS.cfs` |
| `figures/uq_corr_2d.pdf` | `d6cf0adb…` | `42ea035f77b767b3d2d0dc3d2cbd57c9537f957e2ae39aef936a9eb373fc0d97` (`outputs/stat/`) | equals `SHA256SUMS.cfs` |
| `fig:seedscan` (`seedscan_spread_2d.pdf`, `seedscan_band_pt.pdf`) | — | not installed (Q6) | the figure environment is removed; the two files stay in `figures/`, included by no driver |

Captions: `fig:uqbands` lists the training-seed and run-period groups the producer draws (legend "Training seed",
"Run period", provisional, J4); `fig:bootstrap` says the spread is σ/`E_U`, labelled std/mean on the colour bar
(`plot_bootstrap_figs.py` on `block_stat.root`, `hRel2D` = √diag(stat)/`E_U`); the paper's Fig. 1 caption adds the
run-period block (fork).

## 3. Tooling and gates (PHASE2 §5, Q9)

- **`make_figures.sh`:** lines 54 and 57 (the VL172 recipe) are removed, with the comment block above them rewritten
  to name `rebuild/scripts/run_rebuild.sh` (and `make_fig1_q.py`) as the regeneration recipe. A new block
  `install_receipt_fig` copies the five §4 files from `docs/orchestration/state/2d-closeout/stageF/rebuild/outputs/`
  into `figures/`, refusing (exit 1) if the source or the copied file differs from its pinned sha256. It runs **after**
  the sync loop, so no older product under `$REPO/2d-unfolding` can overwrite them. The seed-scan producer line (58)
  is commented out (fig:seedscan left the note). The script is cluster-only (hardcoded `REPO`, root_6_28): it was not
  run; `bash -n` passes, and the install function was exercised in a scratch harness on the worktree outputs (a
  correct digest installs; a wrong digest refuses with rc 1).
- **`check_sec4_receipts.py`:** `receipt()` reads a `.json.gz` by suffix (`gzip.open`, text mode); `total_median()`
  reads `budget_Q.json.gz` `Q.median_pct`; `stat_median()` reads `budget_Q.json.gz` `stat.median_pct`; labels
  "total median uncertainty (Q)" and "statistical block median (Q, S1)"; the stat regex follows the new paper wording
  ("with a median statistical uncertainty of \SI{…}"); the rescoring row is kept (its sentence stays, naming the VL170
  band) and relabelled. The self-test gains `gzip_self_test()` (a gz receipt equals its plain twin; a missing gz
  raises), counted in the verdict.
- **`test_check_sec4_receipts.py`:** the 0.674 fixture becomes 0.684 → 0.694; new tests: gzip read by suffix (temp
  STATE, missing file raises) and the Q bindings (6.4479 / 0.6843).
- **`check_dead_containment.py`:** not changed. The errata's new `\dead{}` rows (70 → 97 uses) pass it.
- `publication/release/figs/make_figs.py` is left (Q11).

## 4. Build results (PHASE2 §6.1)

Scratch copy `scratchpad/buildcopy2/repo/docs/analysis-note/` (the tree without `archive/`, with
`repo/docs/orchestration/state` symlinked to the worktree's, the layout of the inventory's `buildcopy/`), local TeX
Live 2024, `bash build_all.sh`, on the final sources:

| check | result |
|---|---|
| `build_all.sh` | rc 0; each PDF "written by this run; no unresolved references" after one latexmk invocation |
| pages | note 120 (118 at `ae198cc1`), primer 12, paper 11, PET note 26 |
| undefined references / citations in the final logs | 0 / 0 / 0 / 0 |
| `check_dead_containment.py --self-test`, plain | PASS, PASS (strict; note 64/64 and PET note 5/5 struck literals; paper and primer 0 of 69) |
| `check_sec4_receipts.py --self-test`, plain | PASS (18 perturbations rejected, the gzip case included), PASS 14/14 (total median 6.45 vs 6.4479; stat median 0.684 vs 0.684334) |
| `pytest test_check_sec4_receipts.py test_build_all.py` (in the copy) | 62 passed (15 + 47) |

The containment `RESULT` line reads `head=unknown tree=unknown` in the scratch layout (no `tree_state.py` helper),
as in the inventory's run. The PDFs are not committed.

## 5. Residual grep (PHASE2 §6.2)

Over the four builds' `\input` closures (from each `.fls`), for the inventory's precisions (6.09, 6.090, 6.0898,
3.65, 3.655, 4.23, 0.994, 1.014, 5.80, 0.406, 0.048, 24.4, 2.91, 2.92, 0.674, 6.87, 6.058, 99.6): 55 hits. Line
numbers in this section are those of the edited tree.
- **Printed, in `app_history.tex`:** 34 (errata rows, the 2026-10-18 block, and the history subsection).
- **Printed, elsewhere (7), each with its status:**
  - 6.87 at `sec_execsummary.tex:26`, `sec_results.tex:151`, `paper_body.tex:272`, `primer_body.tex:215`: the
    "an earlier version quoted 6.87 %" history clauses, kept as written (Q8, J4 pending). 6.87 is VL172's value,
    not VL175's.
  - 0.048 and 0.406 at `app_statmethods.tex:678`: the §pull history clause, labelled "VL175 0.048 and 0.406"
    (inventory 616–627: "the history clause gains VL175"); struck in the errata.
  - 1.014 at `sec_validation.tex:142`: a false positive (the 4D q3 closure mean weight; inventory §2.9).
- **In LaTeX comments (14):** provenance chains in `values.tex` (0.994, 1.014, 5.80, 6.0898 as "was …"),
  `sec_results.tex` (6.0898, 6.87), `sec_execsummary.tex` (6.87), `paper_body.tex` (6.09, 0.674, 6.87) and
  `primer_body.tex` (6.09), and the two "99.6 %: no producer" notes.

An extended pass for the other retired values (6.043, 2.910, 2.917, 6.084, the band and group medians, 1.931,
0.166, 5.061, 0.0055, 4.99, 0.356, 2.40, 0.416, 2.55, 8.7, 252, 76.7, 1.07, 0.30, 0.18, 0.11, 0.37) found, outside
`app_history`, only unrelated tokens (5D/3D/eavail values, column widths, closure amplitudes) and three deliberate
historical prints: `sec_method.tex:93` (the earlier seed-1 band's 0.18 % / 0.30, named as such),
`app_statmethods.tex:604` (the exact-split 1.47 "against the earlier (VL172) covariance") and
`app_statmethods.tex:1025` (the 0.166 % floor "in force when the tests were graded", Q6).

## 6. Questions for the director, and what was not done

Sites left as written and marked, where a rule could not be applied without a new claim (line numbers at `ae198cc1`):
1. **`app_statmethods.tex:487`** "every reported pull lies within ±3 (§pull)": if this is the combined pull, Q3
   removed its support (no maximum in the Q receipts). Left, `% J3 pending` + QUESTION. **Resolved after review (m2, §7): removed.**
2. **`paper_body.tex:289–291`, `sec_validation.tex:286`** "validated total intervals … require … construction
   repairs (of §uq-2d-construction)": that section now records which findings Q's construction carries. Left,
   `% J3 pending`.
3. **Errata scope (Q8):** besides the five rows Q8 lists, five more 2026-10-18 rows strike the other replaced VL175
   values (6.043 / 2.910e-39 / 2.917e-39 / 6.084 / 6.058; six band medians; three group medians; 0.674 /
   1.931e-40; 63 %), following the VL175 commit's precedent. Containment stays green. Trim if Q8 meant only its list.
4. **Replica-mean offset:** the note body prints it as "a per-bin median of 4.43 standard errors of the mean"
   (`s5_copied.stat_centring_offset`; Q7 "centring per s5_copied") in `sec_systematics` and `sec_method`; the paper
   keeps it in a comment only (J4 register). Confirm the asymmetry.
5. **Judgements made under NUM/FACT, for review:** (a) `app_statmethods.tex:425` "over an order below both other
   blocks" became "the smallest block" (√Tr c08 / stat = 1.989e-41 / 1.984e-40, just under 10); (b)
   `app_statmethods.tex:711–715` the ours-only direct inverse 23.57 / 23.23 is for `E_U`, so its comparator became
   `\chiPaper` (was `\chiPaperExact`); (c) `app_statmethods.tex:408–415` "These three Monte Carlos are independent by
   construction" was removed (C08 shares its seed-42 replicas with S1, DESIGN §3.4) and replaced by that fact; (d) the
   new minimal C_PL paragraph in §uq-combine and the run-period rows of tab:variance-sources / tab:uq / tab:combine are
   construction statements from `playlist-term/DESIGN.md` §2, J4 (D5) for wording; (e) `result_status_rows.tex` rsD
   "Seed pairing of the statistical block unmeasured" was removed as false of Q.

Not done (out of scope or not possible here): the independent review (§6.4); any push, PR or the standalone
`MINERvA-OmniFold-Analysis-Note` sync (J6); running `make_figures.sh` (cluster-only); records outside the deliverables
(Q13: AGENTS.md, the 2D status file, claim tables); `make_figs.py` (Q11).

## 7. Independent review of `dab2ec2a` and its dispositions

The review (`phase2-review.md` in the director's scratchpad: 1 MATERIAL, 12 MINOR, 9 NOTE; a fresh read-only Claude
Opus 5.5 session) and the director's rulings on it are applied in the follow-up commit on this branch. Line numbers
below are at `dab2ec2a`.

| item | ruling | disposition |
|---|---|---|
| M1 abstract (`main_note.tex:50-52`), "implementation and training seed" | reviewer's wording; sweep every build | changed to "…the central value's tree-learning implementation, its universe and statistical blocks at the central value's training seed, and whether…"; `% J3 pending (D10 KI-88)`. Swept note, paper, primer, PET note, executive summary, summary and status table for a training-seed statement applied to the whole uncertainty: no other site. The remaining "same estimator / same tree learner / same LightGBM estimator" sentences (`sec_execsummary.tex:26`, `sec_summary.tex:13`, `sec_results.tex:156`, `paper_body.tex:187`, `primer_body.tex:105`) concern the estimator, which all blocks share. `primer_body.tex:232` and `paper_body.tex:301` concern only the statistical block, which is at seed 42. Unchanged |
| m1 "independently" | reviewer's fix | `sec_systematics.tex`: "Neither the rebuilt (VL170) band, which was only rescored post hoc, nor the statistical block quoted here has been independently tested."; `sec_summary.tex` made to match |
| m2 ±3 pull clause (`app_statmethods.tex:518`) | remove; restate only with a VL175 receipt | removed, together with its dangling `\ref{sec:pull}`; `% J4 pending (D2)`. Not restated: no committed receipt gives a maximum combined pull (`c04-repair/chi2/repaired_std.txt` and the Q logs print mean / rms only) |
| m3 "smaller than the published total" | scope to the per-bin median; `% J3 pending (D0)` | `sec_results.tex`: "Its per-bin median is smaller than the published total's"; primer: "a little smaller in the typical cell". The paper (`\uqMedian` vs `\uqPaper`, a median comparison) and the executive summary ("comparable", medians) needed no word change and carry the marker. No integral or trace comparison is printed; it appears only in the `sec_results` comment |
| m4 run-period block's estimator | paper to agree with the note as far as the record supports | paper: "the first three are LightGBM ensembles at the central value's estimator, and the fourth is built from LightGBM unfolds of three run periods". The comment cites `period-unfold-20261014/scripts/sbatch_period_unfold.sh:76` (`--estimator lgbm`, production driver `74a4ed69`) and REPORT §1 (the control reproduces `E_U` to 3.0e-13) |
| m5 seed-42 band "since been built" (`sec_method.tex:108-110`) | reviewer's fix | "a seed-42 statistical band has since been built, with three independent streams (data, signal and background simulation); it is the quoted statistical block"; `% J4 pending (D10 KI-88)` |
| m6 C08 "fixed inputs" / "seed noise only" | reviewer's fix | tab:variance-sources: "at matched inputs (the same 20 bootstrap replicas at each setting…)"; `sec_systematics`: "The block measures LightGBM seed variation, with the bootstrap × seed interaction at its 1/20 share"; J4 (D11) |
| m7 cross-terms and C_PL (`app_statmethods.tex:1141-1148`) | state only what is true; no new independence claim | "Among the first three, cross-terms are higher-order. The run-period block is built from separate unfolds of the same data, and its noise share is not subtracted (§uq-combine)"; `% J4 pending (D5)` |
| m8 log-normal definition | drop the Table I attribution; state the definition plainly | "The log-normal χ² uses δ_i = … and C^ln_ij = (TotalCov + C^tot)_ij/(x^paper_i x^paper_j); both covariances are scaled by the paper's values." The earlier Table I sentence in the limits paragraph is untouched (J4) |
| m9 dangling "ten-seed" | reviewer's fix | "The mean of the earlier ten-seed scan (App.~\ref{app:history-vl175}) differs from the exact-split cross-check…" |
| m10 rank 197 beside the earlier scan | name its covariance, or drop it | "(for Q, rank 197 above 10⁻¹⁰ λmax; the disclosed scan is of an earlier C^ours)" |
| m11 offset printed in the note, not the paper | keep the asymmetry | unchanged; recorded here |
| m12 4.1 % "ensemble error" | label it as the formula's value | `sec_systematics` and `app_statmethods`: "the Gaussian formula 1/√(2(N−1)) gives a relative standard error of about 4.1 %". The comments cite s5.json `numbers.stat.ensemble_rel_se_of_sigma` (= 1/√(2·299), production DESIGN §8) |
| NOTE 1 two cond conventions | every printed cond names its source and definition | the rank paragraph now defines cond as λmax over the smallest retained eigenvalue (`budget_Q.ranks`) and says every rank and cond of our blocks quoted below uses this definition. The 300-replica cond says "by the definition above". The script-convention cond (8.17e11) beside the direct-inverse χ² is removed, and the ours-only script's 5.624e12 is not printed (it is named in a comment) |
| NOTE 2 the paper's rank 120 threshold | — | no change: the threshold is already attached only to our value |
| NOTE 3 KI 91 wording | — | no change; the existing marker routes it to J4 |
| NOTE 4 fig:uqbands caption | apply | the caption adds "with the total and the published total" |
| NOTE 5 participation-ratio rank ≈1 | — | no change: the sentence names its object, the unweighted covariance |
| NOTE 6 gzip check counted as a perturbation | apply | `check_sec4_receipts.py` prints "gzip receipt: PASS (…)" on its own line and no longer counts it, so the self-test now reports 17 perturbations rejected |
| NOTE 7 no rollback on a refusal | — | no change: exit 1 is visible |
| NOTE 8 provenance pointer omits the laterals' source | apply | `variance-sources` now names the S3 re-unfolds of the `active_universe_5d_standard_merged` files (production DESIGN §3.2) |
| NOTE 9 judgement calls (a)–(e) | accepted by the reviewer | no change |

**Rebuild after the fixes** (fresh scratch copy `scratchpad/buildcopy2/`, same layout):
- `build_all.sh` rc 0. Every PDF is "written by this run; no unresolved references" after one latexmk invocation.
- The final logs show 0 undefined references or citations and 0 multiply-defined labels.
- Pages: note 120, primer 12, paper 11, PET note 26.
- Containment: SELF-TEST PASS, RESULT PASS (strict; note 64/64, PET note 5/5, paper and primer 0 of 69).
- Sec. IV: gzip receipt PASS, SELF-TEST PASS (17 perturbations rejected), real run PASS 14/14.
- `pytest test_check_sec4_receipts.py test_build_all.py`: 62 passed.
- A word-level diff of the printed (comment-stripped) text against `dab2ec2a` shows only the intended deletions.

**Unresolved:** none of the review items. Of the §6 questions, item 1 is resolved by m2. Item 2 (the "construction
repairs" clauses) was not part of the rulings and stays `% J3 pending`.

## 8. Disposition of every inventory row

Line numbers are at `ae198cc1`. "changed" lines that also carry a J marker say so in the note.

| site | status | disposition | note |
|---|---|---|---|
| `values.tex:126` | NUM | changed | \chiCombined 0.994 -> 0.964; comment names rebuild/outputs/chi2/chi2_Q_std.txt, history chain kept |
| `values.tex:127` | NUM | changed | \chiCombinedLog 1.014 -> 0.987; comment names chi2_Q_lognormal.txt and the definition |
| `values.tex:128` | NUM | changed | \chiCombinedSubStat 5.80 -> 6.01 (6.012), chi2_Q_substat.txt |
| `values.tex:129-130` | NUM(comment) | changed | provenance comment -> hCov_Q, rebuild phase 1 |
| `values.tex:133-135` | NUM | changed | \uqMedian 6.09 -> 6.45, budget_Q.json.gz Q.median_pct; coupled gate rebound (fork) |
| `values.tex:136-137` | OK | unchanged | \uqPaper is the published value |
| `values.tex:138` | NUM | changed | \fluxBand 3.65 -> 3.75, budget_Q bands.Flux.median_pct; 4.993 kept in comment as history |
| `values.tex:139` | OK | unchanged | \rhoFluxMuon 0.900 does not depend on Q (B.flux.rhoFluxMuon) |
| `values.tex:87-89` | OK | unchanged | paper-sigma-only pulls |
| `values.tex:97-119` | J(D2)/NR | J-marked | % J4 pending (D2) at the block header; values not recomputed |
| `values.tex:120-121` | J/NR | J-marked | % J4 pending (D2) |
| `values.tex:122-125` | OK | unchanged | paper-covariance chi2 |
| `sec_systematics.tex:1` | OK | unchanged | title |
| `sec_systematics.tex:4-6` | FACT | changed | four blocks named; J4 pending (D0, D5) |
| `sec_systematics.tex:7-10` | FACT | changed | universe and stat at seed 42, C08 five settings incl. 42; J4 pending (D10 KI-88) |
| `sec_systematics.tex:18-20` | FACT/NUM | changed | July sweep 44/187 as input; Rvp1pi dropped, 43 bands + norm (Q1: no rollup universe count printed) |
| `sec_systematics.tex:20-24` | FACT | changed | May truth-mismatch clause removed from the universe paragraph; laterals from selection-complete re-unfolds |
| `sec_systematics.tex:30-34` | NUM/NR | changed | MINOS 2.39, MinosEff 1.58, MINERvA 1.38 (budget_Q bands); "4.99 without them" removed (Q12, history) |
| `sec_systematics.tex:43-46` | FIG/J | changed | caption adds training-seed and run-period blocks; J4 pending (D5) labels provisional |
| `sec_systematics.tex:50-56` | NUM/NR | changed | macros update; 4.99 and ~1 % (VL-era) removed to App. history (Q12) |
| `sec_systematics.tex:56` | OK | unchanged | 1.4 % norm = B.bands.__Normalization_flat |
| `sec_systematics.tex:57-60` | NUM/NR | changed | MINOS integral sigma 0.31 (B 0.306); "0.11 -> 0.37" removed (no S5 before-value), history |
| `sec_systematics.tex:60-62` | NR | changed | "99.6 %" removed (no producer); the rank ~1 clause kept |
| `sec_systematics.tex:62-70` | OK | unchanged | rhoFluxMuon / cross block, independent of Q |
| `sec_systematics.tex:72-89` | FACT | changed | S1: seed 42, three streams, ddof-1 about replica mean; ensemble error 4.1 %; centring 4.43 sigma_mean; J4 pending (D2, D8, D10) |
| `sec_systematics.tex:79-81` | NUM | changed | "~2.55x in sqrt trace" -> sqrt-trace ratio 0.428 (B.paper_ratios; 2.34 not printed, derived) |
| `sec_systematics.tex:82-85` | NR | changed | C_data/StatOnly 0.356 moved to App. history-vl175 (Q7); pointer left |
| `sec_systematics.tex:85-89` | J/FACT | changed | qualifier: neither the VL170 band nor the quoted block is coverage-tested; KI-85 is J5 |
| `sec_systematics.tex:93-97` | FIG | changed | files installed from rebuild/outputs/stat/; caption sigma/E_U (std/mean on colour bar) |
| `sec_systematics.tex:101-115` | FACT/NR/J | changed | ML block -> C08 (5 triplets, rank 4, 0.057 %); 0.166, 1.24x, "five times" removed (Q5, Q6); learner sentence J4 pending (D3) |
| `sec_systematics.tex:120-127` | FIG/NR | changed | fig:seedscan removed (Q6); comment left |
| `sec_systematics.tex:131-139` | FACT | changed | May sweep named as the earlier budget's; July sweep quoted; J4 pending (D10 KI-93) |
| `sec_systematics.tex:141-147` | FACT | changed | adds: quoted block drops Rvp1pi (KI 92); J4 pending |
| `sec_systematics.tex:149-153` | FACT | changed | earlier budget did not propagate bkg stats; quoted stat block has a background stream; J4 pending (D8, D10 KI-94) |
| `sec_systematics.tex:153-155` | FACT | changed | laterals from selection-complete re-unfolds; PPFX index identity -> KI 91 record; J4 pending (D10 KI-91) |
| `sec_systematics.tex:155-156` | J | changed | "left the earlier printed budget unchanged" (tense, true); J4 pending |
| `sec_systematics.tex:160-163` | FACT | changed | block sum + C_PL; new minimal C_PL paragraph (playlist-term DESIGN §2), median 2.14 (B C_PL.median_pct); J4 pending (D5, D9) |
| `sec_systematics.tex:179-182` | OK | unchanged | generic |
| `sec_systematics.tex:186-238` | OK | unchanged | 5D products |
| `sec_results.tex:5-7` | FACT/Q2 | changed | error-bar sentence now states what fig:xsec draws (hXSec2D / hXSec_pt / hXSec_pz bin errors; published points sqrt diag StatOnly), pointing to fig:uqbands and tab:uq; J3 pending |
| `sec_results.tex:56-58` | NUM(macro) | changed | \chiCombined via values.tex (0.964) |
| `sec_results.tex:61-66` | NR/J | changed | "regularization scan" qualified as the exact-split cross-check's; NR comment; J3 pending |
| `sec_results.tex:85` | NUM(macro) | changed | tab:compare via \chiCombined |
| `sec_results.tex:135-142` | NUM(macro)/J | changed | \uqMedian / \fluxBand via macros (6.45 < 6.85 and 3.75 < 4.01 still hold); words left; J4 pending (D10) |
| `sec_results.tex:143-145` | J | J-marked | 6.87 % history clause kept as written (Q8); J4 pending |
| `sec_results.tex:145-147` | NUM/DER/J | J-marked | "under a tenth of sqrt(Tr)" remains true of Q (stat+C08 vs Q, not printed); J4 pending (D0, D5) |
| `sec_results.tex:147-150` | OK/J | unchanged | every block LightGBM at the central value's estimator: true of Q (C_PL from the same pipeline, control reproduces E_U) |
| `sec_results.tex:150-152` | NUM | changed | 6.058 -> 6.410 (B.Q_vs_EC.median_pct) |
| `sec_results.tex:153-156` | NUM(comment) | changed | comment names B.Q.median_pct and B.Q_vs_EC; VL175 chain kept |
| `sec_results.tex:158-178` | NUM/J | changed | tab:uq rebuilt: C08 5 / 1.99e-41 / 0.057; stat 300 / 1.98e-40 / 0.684; universe 43 bands+1 / 2.73e-39 / 5.969; new run-period row 3 / 8.34e-40 / 2.137; combined 2.87e-39 / 6.448; caption updated; row labels J4 pending |
| `sec_results.tex:179-210` | OK | unchanged | paper-sigma only |
| `sec_results.tex:237-238` | OK | unchanged | model chi2 use paper TotalCov only |
| `app_statmethods.tex:5` | J | J-marked | intro sentence true as written (the appendix discusses those estimators); J4 pending (D5) comment |
| `app_statmethods.tex:27-28` | OK | unchanged | N=300 > 205 full rank holds for S1 (rank 205 in budget_Q ranks) |
| `app_statmethods.tex:59-62` | FACT | changed | "three" -> "four variance sources" (run-period row added) |
| `app_statmethods.tex:75-78` | NUM/FACT | changed | ML row -> C08: 5 settings (s, s+1, s+2), s in {42,...,54}, 20 replicas each; median 0.057 |
| `app_statmethods.tex:79-82` | NUM/FACT | changed | bootstrap row: three streams (k, k+1e7, k+2e7), seed 42, N=300 ("Stage-1: N=50" dropped); median 0.684 |
| `app_statmethods.tex:83-86` | NUM/FACT | changed | universe row: July sweep 187/44, rollup 43 + norm (Q1); median 5.969 |
| `app_statmethods.tex:(new)` | FACT | changed | run-period row added (playlist-term DESIGN §2), median 2.137 |
| `app_statmethods.tex:87-90` | NUM/J | changed | MAT row -> the S5 MAT check: 3.4e-16 of the largest element (s5_copied.mat_agreement); a different check from 5.5e-17, stated as such |
| `app_statmethods.tex:91-94` | NUM/FACT | changed | block sum of the four blocks; median 6.448 |
| `app_statmethods.tex:97-98` | TOOL | unchanged | caption pointer to app_provenance (see app_provenance rows) |
| `app_statmethods.tex:102-119` | NR/NUM | changed | sec:seedscan body rewritten as C08 (equation, rank 4, 1/20 interaction share; 0.0025 / 0.057 / 1.989e-41); ten-seed values (0.0055, 0.166, 5.061e-41, 2.4 %, n=4->10) moved to App. history-vl175 (Q6); title and label kept |
| `app_statmethods.tex:121-162 (121-148)` | FACT | changed | "two sub-RNGs" -> three streams; seed flag comment --seed 42 / streams three; section title "Poisson bootstrap" unchanged (PET note \notesec) |
| `app_statmethods.tex:121-162 (150-162)` | NUM/NR | changed | S1: 0.061 / 0.684 / p84 1.712 / ensemble error 4.1 %; 50->300 convergence, "4.1x the training-seed value", playlist 1A 1.46 % moved to App. history-vl175 (Q7) |
| `app_statmethods.tex:164-179` | OK | unchanged | multinomial subsection title unchanged (PET note \notesec) |
| `app_statmethods.tex:183-193` | NUM/FACT | changed | July sweep 187/44; rollup 43 + norm; laterals from selection-complete re-unfolds |
| `app_statmethods.tex:216-232` | OK | unchanged | algebra |
| `app_statmethods.tex:255-278` | NUM/FACT | changed | tab:band-medians: 2.390/1.376/1.578/3.747/0.600/0.374/0.368; 43 bands + norm 5.969, 2.735e-39; caption -> Q universe block |
| `app_statmethods.tex:279` | NUM(comment) | changed | -> budget_Q bands / universe |
| `app_statmethods.tex:280-293` | NUM/J | changed | grouped medians 3.455/1.581/3.747/0.799/0.684/1.400 + Training seed 0.057, Run period 2.137; VL172->VL175 "rises although MINOS falls" sentence moved to history |
| `app_statmethods.tex:288-290` | NUM(comment) | changed | -> budget_Q groups.median_pct; VL175 comment kept |
| `app_statmethods.tex:358-360` | OK | unchanged | describes the paper |
| `app_statmethods.tex:375-385` | NUM/J | changed | the earlier byte-for-byte check kept as described (historical, explicit); "<= 1e-12 (VL175)" -> S5 check 3.4e-16 of largest element; J4 pending (D10) |
| `app_statmethods.tex:392` | NUM | changed | "120<140" -> 120 below our 137 (t = 1e-12) |
| `app_statmethods.tex:408-415` | FACT | changed | streams, five settings sharing seed-42 replicas with stat, run-period block; seeds matched; "independent by construction" removed (false of Q: C08 shares S1 replicas); J4 pending (D10, D11) |
| `app_statmethods.tex:416-421` | FACT | changed | eq:blocksum + C^PL |
| `app_statmethods.tex:425-426` | NUM/J | changed | "over an order below both other blocks" -> "the smallest block" (sqrt(Tr) ratio to stat is 9.98, so "over an order" no longer holds); J4 pending |
| `app_statmethods.tex:428-446` | NUM | changed | tab:combine: C08 1.989e-41/0.057, stat 1.984e-40/0.684, universe 2.735e-39/5.969, new run-period row 8.344e-40/2.137, combined 2.866e-39/6.448; S5-total row not added |
| `app_statmethods.tex:447-449` | NUM | changed | 6.090 -> 6.448 |
| `app_statmethods.tex:450-454` | NUM/FACT | changed | 6.058 -> 6.410; seeds matched (two at 42, C08 five incl. 42) |
| `app_statmethods.tex:455-456` | NUM | changed | 6.084 -> universe + stat 6.040 (B.universe_plus_stat.median_pct) |
| `app_statmethods.tex:457-460` | NUM(comment) | changed | -> budget_Q fields |
| `app_statmethods.tex:462-464` | J | changed | "flux-fixed product" -> "the blocks of the adopted covariance"; J4 pending |
| `app_statmethods.tex:487` | J | changed (review m2) | "every reported pull lies within +-3": support (sec:pull \|pull\|<3) removed by Q3 if this is the combined pull; QUESTION for director |
| `app_statmethods.tex:509-511` | OK | unchanged | generic |
| `app_statmethods.tex:515-524` | OK | unchanged | paper-only truncation scan |
| `app_statmethods.tex:532` | NUM | changed | 4.23 -> 4.75 (B.Q.integral_sigma_pct 4.755 at the printed 2 decimals) |
| `app_statmethods.tex:533` | NUM | changed | 6.090 -> 6.448 |
| `app_statmethods.tex:534-535` | NUM(macro) | changed | \chiCombined, \chiCombinedLog via values.tex; log-normal definition added beside the first quote (record §3) |
| `app_statmethods.tex:539-541` | DER/NR | changed | "about 63 %" removed (derived; 64 % not printed); exact-split 3.661 -> 1.472 removed (VL172, NR) |
| `app_statmethods.tex:561-563` | NR/J | changed | 1.47 qualified as the exact-split value against the earlier (VL172) covariance |
| `app_statmethods.tex:565-569` | FACT/J | changed | coverage test "an earlier statistical band"; seed sentence -> universe and stat blocks share the central value's seed; J4 pending (D2, D10) |
| `app_statmethods.tex:571-572` | NUM/J | J-marked | macro 0.987; "essentially identical" left; J4 pending (definition dependence) |
| `app_statmethods.tex:574-575` | NUM/DER | changed | "~2.5 / 2.55^2 ~ 6.5" -> ours is 0.428 of it in sqrt trace, "the square of that factor" in trace (no derived number printed) |
| `app_statmethods.tex:577-583` | NUM/NR | changed | rank 140->201 -> 137->205 (t = 1e-12); 252 -> direct-inverse 23.57 (ours_only_universe_plus_stat.txt); 252 to history |
| `app_statmethods.tex:585-607` | OK | unchanged | paper-only edge-bin table |
| `app_statmethods.tex:616-627` | NUM/J | changed | combined pull 0.042 / 0.398; composition -> paper + adopted covariance; history clause gains VL175 0.048/0.406 |
| `app_statmethods.tex:629-631` | NR | changed | "No reported bin has \|pull\|>3" removed (Q3) |
| `app_statmethods.tex:633-634` | OK | unchanged | paper-only pulls |
| `app_statmethods.tex:664-671` | OK | unchanged | paper-only shape chi2 |
| `app_statmethods.tex:677-683` | NUM | changed | C^ours + C^PL; rank 137/205, cond 4.93e11 at 1e-12 (123, 9.93e9 at 1e-10); 140 / 8.7e8 to history (Q4) |
| `app_statmethods.tex:685-689` | NR/NUM | changed | 99.6 % removed (no producer); 44 -> 43 bands |
| `app_statmethods.tex:690-692` | NUM | changed | "below our 140" -> 137 |
| `app_statmethods.tex:696-700` | NUM | changed | 204 / 1.0e12 -> 205 / 8.17e11 (B.ranks.universe_plus_stat); comment keeps the VL-era chain |
| `app_statmethods.tex:703` | NUM | changed | "rank 201" -> full rank (205) |
| `app_statmethods.tex:704-708` | NUM/DER | changed | 2.40 / 1.931e-40 / 5.8 -> ratio 0.428, 1.984e-40 vs 4.639e-40; "5.8-fold" -> "uniform per-mode effect" |
| `app_statmethods.tex:711-715` | NUM/NR | changed | 24.4 -> 23.57 (universe+stat, cond 8.17e11) and 23.23 (Q); comparator \chiPaper (both for E_U); 252 to history; J3 pending |
| `app_statmethods.tex:717-719` | FACT | changed | three streams (data, signal MC, background MC) |
| `app_statmethods.tex:724-726` | FACT | changed | split test attributed to the earlier (VL170) bootstrap, past tense, not repeated for S1 |
| `app_statmethods.tex:728-744` | NR | changed | split-bootstrap paragraph (1.07, 77/23, 0.95, 0.356, 0.416, 0.108, 0.46, 76.7) moved verbatim to App. history-vl175 (Q7); body keeps S1's 0.428 / 0.435 and the surviving caveat |
| `app_statmethods.tex:745-751` | NR | changed | 0.108, 0.46, 0.009, 76.7 moved verbatim with the split-bootstrap paragraph to App. history-vl175 (Q7) |
| `app_statmethods.tex:753-765` | J | changed | "What (ii) does and does not license" moved with the split test; its surviving statements (test cannot decide; the measured statement is the ratio) kept in the body; J4 pending (D2) |
| `app_statmethods.tex:767-771` | OK | unchanged | convention (1e-10) |
| `app_statmethods.tex:773-798` | NR | changed | regularization scan kept, qualified "on an earlier C^ours (not recomputed for the adopted covariance)"; J3 pending |
| `app_statmethods.tex:800-812` | NUM | changed | 1.931e-40 / 2.40x -> 1.984e-40 / 0.428 of the paper's; macros K14/K16 via values.tex |
| `app_statmethods.tex:814-819` | J | J-marked | block sum now includes C_PL; J4 pending |
| `app_statmethods.tex:830-837` | NUM | changed | "rank 201" -> 197 above 1e-10 (the truncation threshold; 205 at 1e-12 in comment) |
| `app_statmethods.tex:935-959` | OK | unchanged | paper-only estimator table |
| `app_statmethods.tex:983-988` | NR/J | changed | "0.166 % ML floor" kept, stated as the ten-seed floor in force when the tests were graded (Q6) |
| `app_statmethods.tex:1059-1063` | NUM/NR | changed | pulls 0.042/0.398; "0.166 % ML floor" -> 0.057 % training-seed block (receipt) over an order below systematics |
| `app_statmethods.tex:1072-1078` | FACT/NUM | changed | audit table: + C^PL row; C^syst July sweep (43 bands in rollup); C^stat seed 42 three streams; C^ML 5x20 |
| `app_statmethods.tex:1080-1083` | NUM | changed | pull RMS 0.398; combined median 6.448 |
| `app_statmethods.tex:1084-1087` | J(D2)/NR | J-marked | coverage rows unchanged; J4 pending (D2) |
| `app_statmethods.tex:1097-1102` | FACT/J | changed | four blocks; C08 averages the same 20 replicas per setting and includes the 1/20 interaction share ("pins the bootstrap" was false of Q); J4 pending (D11) |
| `app_statmethods.tex:1103-1107` | J | changed | adds that the quoted block is a different, untested ensemble; J4 pending (D2), KI-85 J5 |
| `sec_execsummary.tex:26` | NUM(macro)/J | J-marked | \uqMedian -> 6.45 via macro; 6.87 history literal kept (Q8); run-period not named: J4 pending (D5) |
| `sec_execsummary.tex:64` | OK | unchanged | 5D methodological |
| `sec_execsummary.tex:94` | FACT/J | changed | "the rebuilt, currently quoted band" -> rebuilt band not re-tested, quoted block (a different ensemble) untested; J4 pending (D2) |
| `result_status_rows.tex:12` | FACT/J | changed | rsB: stat/universe at the central seed, five-setting seed ensemble, run-period block; rsC: quoted block untested; rsD: "Seed pairing ... unmeasured" removed (false of Q); J4 pending (D0, D2, D5, D10) |
| `sec_summary.tex:8-16` | J | changed | qualifier: neither the rebuilt band nor the quoted block tested; J4 pending (D2) |
| `main_note.tex:49-52 (abstract)` | FACT/J | changed | abstract: "different tree-learning implementation" -> the central value's implementation and training seed; the "not measured" clause left; J3 pending (D10 KI-88) |
| `sec_method.tex:80-82` | FACT/J | changed | ensembles: universe, bootstrap, training-seed block, run-period unfolds, all LightGBM |
| `sec_method.tex:87-90` | FACT | changed | May-sweep truth-input clause removed (July sweep); J4 pending (D10 KI-93) |
| `sec_method.tex:90-98` | FACT/NR | changed | stat at seed 42, C08 five settings; offset 4.43 sigma_mean (B.s5_copied); seed-1 0.18 %/0.30 kept as the earlier band's; "pairing question stays open" removed; J4 pending (D10 KI-88) |
| `sec_method.tex:103-105` | FACT | changed | "that band has not been built" -> since built, the quoted statistical block |
| `sec_method.tex:128-129` | OK | unchanged | exact-split has no matched covariance: still true |
| `sec_method.tex:175-176` | OK | unchanged | training-seed variation band (C08) |
| `sec_validation.tex:213-222` | J/FACT | changed | "the production band" -> the band in production when it ran (VL162); J4 pending (D2) |
| `sec_validation.tex:226-258` | NR/J | unchanged | \covTwoD* results of the VL162 band (not a property of Q) |
| `sec_validation.tex:260-269` | FACT | changed | "the rebuilt band is the quoted one" -> rebuilt (VL170); the quoted block is S1; J4 pending (D2) |
| `sec_validation.tex:271-291` | NR/J | J-marked | rescoring of the VL170 band kept (states its object); J4 pending (D2, J5); "construction repairs" clause J3 pending + QUESTION |
| `sec_validation.tex:293-300` | J | J-marked | scope bullet true of the test; J4 pending (D2) |
| `sec_validation.tex:319-351` | NR | unchanged | same-ensemble pulls, historical diagnostic |
| `sec_validation.tex:142-146,203-204` | OK | unchanged | false positives (4D q3 closure) |
| `sec_intro.tex:47-49,69-72` | J | J-marked | generic; J4 pending (D5) |
| `app_provenance.tex:62-63,146-156` | NUM/pointer | changed | variance-sources pointers -> driver_p1.py (stageC/pilot/p1/), s5_rollup.py (stageC/production/), playlist_term.py (playlist-term/), build_q_products.py (stageF/rebuild/) -> uq_adopted_covariance.root:hCov_Q, the DECISION-20261017 record; old VL162/VL175 pointers named in a comment. No new provenance tag (not asked by PHASE2) |
| `app_provenance.tex:100-111` | J | changed | adds one sentence: the quoted statistical block (S1) was not scored by these toys; J4 pending (D2) |
| `app_codebase.tex:33-35` | J | changed | adds that the quoted training-seed block is built by the production rollup, not seedscan; J4 pending (D11) |
| `app_codebase.tex:25-27` | OK | unchanged | generic |
| `app_release.tex:15-17` | J/OK | unchanged | pre-existing (RC7 arrays lack cov_ours), true for VL175 and Q alike |
| `app_release.tex:30,34` | OK | unchanged | true of Q |
| `app_history.tex:23-64` | NUM/Q8 | changed | errata gains a 2026-10-18 block: the Q8 rows (6.09/6.090 -> 6.45/6.448; 3.65/3.655 -> 3.75/3.747; 0.994/1.014/5.80 -> 0.964/0.987/6.01; 4.23 -> 4.75; 0.048/0.406 -> 0.042/0.398) plus five rows beyond Q8's list (6.043, 2.910e-39, 2.917e-39, 6.084, 6.058; six band medians; three grouped medians; 0.674 / 1.931e-40; 63 %) - flagged for the director |
| `app_history.tex:48-52,55-57` | OK | unchanged | older "when struck" rows |
| `app_history.tex:92-98` | OK | unchanged | history |
| `app_history.tex:150-157` | J | changed | bracketed "[Superseded 2026-10-18: the quoted pair is 0.042/0.398 ...]" after the verbatim text |
| `app_history.tex:174-187` | NUM | changed | "[Superseded 2026-10-18: the quoted budget is 6.448 % (Q) ...]" appended |
| `app_history.tex:189-215` | OK | unchanged | history |
| `app_history.tex:340-346,373` | OK | unchanged | 3D historical budget |
| `app_history.tex:(new)` | NR(Q6,Q7,Q12) | changed | new subsubsection app:history-vl175: the ten-seed scan (10 seeds, 0.166, 1.24x, n=4->10, links to the figures at ae198cc1), the earlier (VL170) bootstrap (50->300, 4.1x, 1A 1.46 %, 2.55x, 0.356, 2.40/5.8, 252, 24.4, and the split-bootstrap paragraph verbatim), other VL175-era values (4.99, ~1 %, 0.11->0.37, 99.6, muon-reco sentence, 140/8.7e8, 204/1.0e12, 201, 63 %, 3.661->1.472) |
| `app_cstat.tex:47` | FACT/J | changed | "extends the scalar bootstrap's data/MC streams" -> the streams it had at the time; the quoted 2D block now has a background stream too; J4 pending (D8) |
| `app_cstat.tex:35, app_history_pet.tex:166` | TOOL(hazard) | unchanged | \notesec titles: both target subsection titles in app_statmethods.tex unchanged ("Poisson bootstrap", "Multinomial $\to$ independent Poisson bootstrap limit") |
| `paper_body.tex:58-60, 68 (58-60)` | OK | unchanged | macros not covariance-dependent |
| `paper_body.tex:58-60, 68 (68)` | J | J-marked | % J3 pending (D1, D2) |
| `paper_body.tex:185-186` | OK/J | J-marked | still true; comment: stat block now also at seed 42 (D10 KI-88) |
| `paper_body.tex:221-226` | OK | unchanged | paper-only macros |
| `paper_body.tex:229-230` | J | J-marked | learner 0.98 % kept; J4 pending (D3) |
| `paper_body.tex:239` | FIG | changed | figure file installed (82665808...); comment names it and the 6.45/6.85 inset |
| `paper_body.tex:240-249` | FACT/J | changed | caption block list adds run-period; J4 pending (D0, D5); "training-seed" is now C08 |
| `paper_body.tex:256-257` | FACT | changed | four blocks; the first three built with LightGBM; J4 pending (D0, D5) |
| `paper_body.tex:258-259` | NUM(macro) | changed | \uqMedian 6.45 via values.tex |
| `paper_body.tex:259-262` | J | J-marked | 6.87 % clause kept (Q8); J4 pending |
| `paper_body.tex:262-264` | NUM(macro)/J | changed | \fluxBand 3.75; J4 pending (D10) |
| `paper_body.tex:264-268` | FACT | changed | "different training seeds ... 0.30 (0.18 %)" -> systematic and statistical at the central seed, C08 five settings incl. it; 0.30/0.18 removed (VL170 seed-1 comparison); offset 4.43 sigma_mean only in a comment (J4) |
| `paper_body.tex:268-269` | J | J-marked | J4 pending (D1) |
| `paper_body.tex:271-275` | J/NR | J-marked | VL169 coverage sentences kept; J4 pending (D2); gate rows unchanged |
| `paper_body.tex:275-278` | FACT/NUM/TOOL | changed | "rebuilt band, now the quoted one, 0.674 %" -> the quoted block is a different 300-replica, seed-42, three-stream ensemble, median 0.684 % (B.stat.median_pct, gate-bound); neither it nor the rebuilt band tested; J4 pending (D2, D8, D10, J5) |
| `paper_body.tex:279-285` | NR | changed | rescoring kept, its object named ("against the rebuilt band"); gate row kept, relabelled (VL170) |
| `paper_body.tex:285-291` | FACT/J | changed | defects attributed to the earlier budget; quoted covariance uses a sweep without the mismatch and a background stream; "construction repairs" clause left, J3 pending + QUESTION |
| `paper_body.tex:292-306` | NUM(comments) | changed | Q provenance line; KI-88 seed-1 chain marked as VL170 |
| `paper_body.tex:338` | OK | unchanged | 5D bootstrap |
| `paper_body.tex:482-486` | OK | unchanged | 5D nuisance model |
| `paper_body.tex:765-768` | J | changed | "rebuilt ... band" -> "quoted ... statistical block"; J3 pending (D2) |
| `main_paper.tex:129-135` | J | J-marked | true of Q (Fig. 1 from cov2d_Q_205 via make_fig1_q.py and the release's make_figs.py); provenance comment; J4 pending |
| `main_paper.tex:136-155` | OK | unchanged | comments |
| `primer_body.tex:103-105` | FACT/J | changed | "rebuilt" -> "quoted" statistical band; J3 pending (D2) |
| `primer_body.tex:205-207` | NUM(macro)/J | J-marked | 6.45 < 6.85 still "a little smaller"; J4 pending (D5, D10) |
| `primer_body.tex:207-211` | J | J-marked | 6.87 clause kept (Q8) |
| `primer_body.tex:211-212` | OK/J | J-marked | J4 pending (D5) comment |
| `primer_body.tex:217-226` | FACT | changed | quoted bars built again at the central value's learner settings, not tested; J4 pending (D2, D10) |
| `primer_body.tex:— (run-period omission)` | J | J-marked | J4 pending (D5); no new claim text |
| `check_sec4_receipts.py:34-35` | TOOL | changed | receipt() reads .json.gz by suffix (gzip.open, text mode); BUDGET_Q constant |
| `check_sec4_receipts.py:44-47` | TOOL | changed | stat_median() -> budget_Q.json.gz stat.median_pct (0.6843) |
| `check_sec4_receipts.py:50-52` | TOOL | changed | total_median() -> budget_Q.json.gz Q.median_pct (6.4479) |
| `check_sec4_receipts.py:105` | TOOL | changed | label "total median uncertainty (Q)" |
| `check_sec4_receipts.py:106-110` | TOOL | unchanged | coverage rows (their sentences stay) |
| `check_sec4_receipts.py:113-117` | TOOL | changed | stat regex "with a median statistical uncertainty of \SI{...}" (new wording), label "statistical block median (Q, S1)"; rescoring row relabelled (VL170) |
| `check_sec4_receipts.py:self-test` | TOOL | changed | gzip_self_test(): gz equals its plain twin, a missing gz raises; counted in the self-test verdict |
| `test_check_sec4_receipts.py:35` | TOOL | changed | fixture 0.684 -> 0.694 |
| `test_check_sec4_receipts.py:(new)` | TOOL | changed | test_a_gzip_receipt_reads_by_suffix; test_the_q_bindings_read_the_committed_budget |
| `check_dead_containment.py` | TOOL | unchanged | not edited (PHASE2 §5); PASS with the new errata rows |
| `publication/release/figs/make_figs.py:10-12` | TOOL | unchanged | stale VL170/VL172 docstring left (Q11; pinned 9c4dbf24...) |
| `publication/release/figs/_data/fig_arrays.npz.manifest.json` | TOOL | unchanged | done in phase 1 (01f70c37) |
| `make_figures.sh:44-53` | TOOL | changed | comment rewritten for Q: figures come from rebuild/scripts/run_rebuild.sh (Fig. 1 make_fig1_q.py), installed by digest |
| `make_figures.sh:54` | TOOL | changed | VL172 recipe line (plot_uncertainty_fig6_7_style.py on *_vl170) removed |
| `make_figures.sh:56-57` | TOOL | changed | plot_bootstrap_figs.py on bootstrap_MEFHC_300_vl170 removed |
| `make_figures.sh:58` | TOOL/NR | changed | seedscan producer commented out (fig:seedscan left the note, Q6) |
| `make_figures.sh:142-149` | TOOL | changed | hazard closed: a new digest-checked install block runs AFTER the sync loop (refuses on a source or destination digest mismatch; tested both directions in a scratch harness) |
| `make_figures.sh:35-42` | OK | unchanged | central-value figures, unaffected by Q |
| `figures/paper_fig1_validation.pdf (49766e26, VL175)` | FIG | changed | 49766e26... -> 82665808... (rebuild/outputs/fig1/fig1_validation.pdf; RUN-fig1.txt digest; no CFS entry) |
| `figures/MEFHC_fig6_7_uncertainty_pt.pdf 65db5b0b, _pz.pdf 4d659851 (VL175) [pt]` | FIG | changed | 65db5b0b... -> c12f37d5... (= SHA256SUMS.cfs ./fig67/...) |
| `figures/MEFHC_fig6_7_uncertainty_pt.pdf 65db5b0b, _pz.pdf 4d659851 (VL175) [pz]` | FIG | changed | 4d659851... -> e3bfb727... (= SHA256SUMS.cfs) |
| `figures/uq_spread_2d.pdf fa175255, uq_corr_2d.pdf d6cf0adb (VL170) [spread]` | FIG | changed | fa175255... -> 79d6b35f... (= SHA256SUMS.cfs ./stat/...) |
| `figures/uq_spread_2d.pdf fa175255, uq_corr_2d.pdf d6cf0adb (VL170) [corr]` | FIG | changed | d6cf0adb... -> 42ea035f... (= SHA256SUMS.cfs) |
| `figures/seedscan_spread_2d.pdf ee72097b, seedscan_band_pt.pdf 47521d29` | FIG/NR | unchanged | no longer included by any driver (fig:seedscan removed); files left in place, linked from App. history at ae198cc1 |
| `figures/paper_validation_residual.pdf` | OK | unchanged | not included by any driver; paper-sigma only |
| `regularization scan` | NR | changed | see app_statmethods.tex:773-798 |

**Inventory §3 (checked and unaffected):** re-checked; none of those sites was edited.

**Same-model caveat:** director, implementer and fork are Claude Opus 5.5 on claude-school.
