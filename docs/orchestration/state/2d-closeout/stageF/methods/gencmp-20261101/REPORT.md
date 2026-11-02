# The GENCMP paper round: report (2026-11-01)

**Under:**
- `DECISION-20261101-joseph-gencmp-paper-adoption.md` (#651, main `dfa13737`), items 1–4 and 6;
- the director's rulings of 2026-11-01 on three consequences:
  1. the Stage G diagnostics are scoped this round, not recomputed (the director commissions their recompute as a GENCMP amendment);
  2. the abstracts' numbers follow Table IV through `\fvval`, with no word changed;
  3. `:42` is scoped to the sixteen-cell comparison.

**Result.** Items 1–4 and 6 are in and every check passes. Item 5 is held: `paper_body.tex`'s 2D-quadrant sentence is
unchanged. `main_paper.tex`, `main_note.tex` and `sec_execsummary.tex` are byte-identical to the base. Nothing is submitted,
deposited or tagged.

**Table IV is the paper's Table III.** The decision calls the generator table Table IV (`tab:gen16`). The PDF numbers it
III, since the 620 round removed Table I. The source and the label are the same table.

## What changed

**Item 1 (Q08, CH): Table IV and the ratio figure.**
- GENIE CV, GENIE + MEC, NuWro and GiBUU take step B's corner "CH, analysis definitions" (`defs.json` `table_2x2`), in
  both column groups, through `\fvval`. MINERvA Tune v1 is Stage G's, unchanged: it is already in the analysis
  definitions (MP-5 T3).
- NuWro and GiBUU carry "(CH)" in their labels.
- GiBUU's table note gives its hydrogen label in full:
  - corrected with GiBUU's own free-proton sample, at weight 1/13 per nucleon;
  - B3 failed on hydrogen;
  - the post-hoc bias check passed at ≤ 0.1σ_c, with σ_c defined;
  - 46 % of the hydrogen sample is DIS that does not conserve energy.
- `:232` gives:
  - the carbon values (NuWro 130, shape-only 113; GiBUU 45, 25);
  - GiBUU's rise of 2.3, from 45 to 48 for 8 ndf, and its shape-only fall from 25 to 22;
  - the rise's dependence on the hydrogen sample: 44.2 with GENIE's hydrogen, against 45.3 on carbon and 47.5 with its own (all in the generators' definitions; a thin sample, so largely its noise).
- `fig:ratio16` is redrawn by the new `nd-unfolding/fd_gencmp_figures.py`:
  - it runs `fd_g_figures.py`'s K0 and K1 on the with-block Stage G readouts, then puts in place the four predictions' g, g/f − 1, pulls and labels from `defs.json`;
  - G1 asserts that f and σ equal `defs.json`'s, and the cells and ndf are the same;
  - it then runs `fd_g_figures.py`'s own model, paint and K2–K8 unchanged.

  PDF `32a7557c`; sidecar `fd/gencmp/figures/fd_g_fig_ratio.json`.

**Item 2 (Q10): the analysis definitions.**
- "Unlike the analysis definitions …" gives way to the method sentence:
  - W with the struck nucleon's mass, or an average nucleon mass where the generator records no single struck nucleon;
  - the muon angle from the beam axis, each event's beam-direction offset sampled from the analysis simulation's distribution;
  - no cell moves by more than 0.07σ, 0.063 at most.
- **Ruling 3:** the old sentence's content stays as "Elsewhere …" for the descriptive comparisons of `sec:central`, which still use the generators' definitions on carbon.

**Item 3 (Q08): native NuWro.**
- One clause in the paper: "agrees with the combination within a tolerance fixed in advance (Σz² = 17.9 for 16 cells, largest |z| = 2.2, in the generators' own definitions)".
- **The note adds:**
  - the rule (Σz² < 32.0, no |z| > 3.5);
  - the analysis route (16.9, 2.2);
  - the native χ² (134.02 against 128.41);
  - the +2.1 % probe diagnostic, labelled "not a declared test".

**Item 4 (Q26, 3D): the note only** (`sec_fived16.tex`, after the sixteen-cell table).
- The quadrant sums lie 0.2–0.8 % below the three-observable central value, the largest 0.17 of the sixteen-cell σ.
- "This comparison is descriptive, not a test", since no 3D covariance is adopted.
- The two pT < 0.7 quadrants carry their unreported-box label (share ≤ 1.1 × 10⁻⁷).
- The 2D quadrant comparison is not printed (item 5).

**Item 6: the consequential edits.**
- **False sentences:**
  - `:42` "The predictions for carbon are …" is rewritten as the director's scoping sentence;
  - "per nucleon of their target" becomes "… of their target: CH, or carbon for NuWro and GiBUU outside the sixteen-cell comparison";
  - "… which the sixteen-cell comparison … does not correct" becomes "The comparisons of NuWro and GiBUU on carbon contain a target difference of this kind". The 8.3 % sentence stays;
  - `:232` "NuWro and GiBUU are on carbon, with no correction to CH" is replaced.
- **Regenerated:**
  - Table IV's values, caption and labels;
  - `fig:ratio16` and its caption;
  - the note's generator table: Table IV's values, without the C_total column, which is Stage G's only;
  - the note's per-cell table: Table IV's predictions;
  - a new note subsection, `sec:fived16-gen-target`, with:
    - the construction and the definitions;
    - the carbon-and-sensitivity table (carbon in both definitions, GENIE hydrogen, native);
    - Stage G's table, with its C_total column: the labelled row ruling 1 asks for.
- **Reconciled:**
  - `sec_joint.tex`: "On these cells both corrections move the prediction toward the data; in the sixteen-cell comparison, GiBUU's total χ² on its eight cells rises";
  - `primer_body.tex:305`: "In these tests … (in a separate comparison on broader cells it raises GiBUU's overall mismatch slightly)".
- **Scoped (ruling 1):** each has one scoping sentence or caption clause, with every value through `\fvval`, so the amendment's round drops one clause each:
  - the paper's sensitivity and flux-bootstrap paragraph ("of the reported value" becomes "of that χ²");
  - the note's sensitivities, bootstrap, eigenmode table, modes figure and R04 look.

  They print Stage G's names and χ² (`gs-` keys). make_values keeps the assertion that the bootstrap's χ² equals Stage G's, now against `gs-`.

**Item 8: the C_model clause (stated, not measured).** "Those contributions come from the generators' samples in their
own definitions, with NuWro and GiBUU on carbon, not from the predictions compared here" (paper `:232`; the note in
`sec:fived16-gen-target`).
- **Source:** `nd-unfolding/pv-ladder/config.json:58-65`, the frozen C12 products of the declaration's control A1.
- **Why not measured:** it needs the pscratch S1 assembly, so it is not 0 node-h from committed products. It belongs in the same amendment.
  <!-- absence-ok: states that this round did not measure it, and why (the input is on pscratch) -->

## The abstracts and the executive summary: every value, before → after

| key | main_paper.tex | main_note.tex | sec_execsummary.tex |
|---|---|---|---|
| `g-ext-chi2int-min16` (external, 16 cells) | 105 → **107** | 105 → **107** | 105 → **107** |
| `g-ext-chi2int-max16` | 224 → **229** | 224 → **229** | 224 → **229** |
| `g-gibuu-total-chi2int` | 45 → **48** | 45 → **48** | 45 → **48** |
| `g-gcv-total-ndf` | 16 → 16 | 16 → 16 | — |
| `g-gibuu-ncells-word` | eight → eight | eight → eight | — |
| `sigmed-reported` | 7.86 → 7.86 | 7.86 → 7.86 | 7.86 → 7.86 |

No word changes. Also through `\fvval`:
- the falls with the run-period block (`:259`): 3.6–30.5 % → 3.6–29.3 % (total), and 7.3–39.5 % → 7.4–40.4 % (shape-only);

## Every printed number, re-derived

`NUMBERS.txt` gives each new or changed key with the value it prints, the value re-derived from the readout and the
readout's file:line. It covers 81 keys, with 0 differences. `trace_numbers.py` does the re-derivation independently of
`make_values_fived16.py`. The review's script re-derived them a third time.

The principal lines:

| printed | value | source |
|---|---|---|
| Table IV, GENIE CV | 107 / 102; 111 / 110 | `defs.json:4471-4476` |
| Table IV, GENIE + MEC | 229 / 229; 278 / 264 | `defs.json:4495-4500` |
| Table IV, NuWro (CH) | 128 / 108; 181 / 181 | `defs.json:4541-4546` |
| Table IV, GiBUU (CH) | 48 / 22; 61 / 25 | `defs.json:4587-4592` |
| Table IV, MINERvA Tune v1 | 262 / 262; 330 / 311 (unchanged) | `fd/with-cpl/readout/fd_g_readout.json`, `fd/readout/fd_g_readout.json` |
| carbon, NuWro / GiBUU | 130 (113); 45 (25) | `defs.json:4519-4520`, `:4565-4566` |
| GiBUU's rise | 2.3 (47.78 − 45.49) | `defs.json:4587`, `:4565` |
| GENIE hydrogen / carbon / own, GiBUU (generator definitions) | 44.2 / 45.3 / 47.5 | `ch.json:1616`, `:1163`, `:1389` |
| native NuWro, generator route | Σz² 17.9, largest abs z 2.2 | `native.json:25-26` |
| native NuWro, analysis route | 16.9, 2.2 | `native.json:736-737` |
| the rule | 32.0 and 3.5 | `native.json:6` |
| the definitions bound | 0.063 (GENIE + MEC, R07) → 0.07 | `defs.json:1631` |
| five-draw spread | 0.052 (GiBUU CH, R08) | `defs.json:4415` |
| the probe diagnostic | +2.1 % | `receipts/d_projection.txt:8` |
| 3D | 0.2 (QA) – 0.8 (QB) %; 0.17 (QB) | `overlap.json:45`, `:96`, `:98` |
| QA's unreported share | 1.1 × 10⁻⁷ | `overlap.json:19` |
| GiBUU's label: 0.1σ_c, 46 % | | `defs.json:4452` |
| the weight 1/13 (from "12:1 per nucleon") | | `defs.json:3393` |

## Checks, on the final text (`4b5ec82ed`, and this report's commit)

| check | result |
|---|---|
| the ledger (`check_ledger.py`, base `dfa137370`, with `paper_body.tex` and `primer_body.tex` in the batch) | 13 rows, 66 probes, 21 changed base sentences, 0 failures; self-test PASS |
| `make_values_fived16.py --check` and `--self-test` | PASS: 2490 values, the readouts pinned, 2 figures equal their sources. Six new plants, each refused by its own guard |
| `build_all.sh` | PASS: all five PDFs (paper 12 pp, note 131 pp, primer 15 pp); no "??" and no "[PENDING" in either |
| layout | the paper's one overfull box (Table III, 9.7 pt) is the base's; a one-line page overflow that the first caption wording caused is gone |
| the two-direction review (`review.md`) | no High; 3 Medium and 6 Low, all fixed or documented; no number wrong |
| `check_held.py --fact-held` (`CHECK-HELD.txt`) | 3 flags, all pre-existing (G1:paper-g-08, G1:paper-s-08, G1b:paper-s-07), none of them this round's. The fourth earlier flag, G1b:paper-g-14, no longer fires; its source sentence is unchanged, and why its extracted text now matches was not investigated |
| the rater copy's holddiff | multiset VERDICT PASS (the same words); the ordered diff shows one "the" at a different reading-order position near the acknowledgment hold span, with no word added or lost; its cause in the extraction was not investigated |
| `generate_manifest.py --check --at-sha HEAD` | see the manifest commit |
| local CI | @CI@ |

**Not run:** agy and P1. The director named the checks of #638 (ledger, review, check_held, build_all).

## For the director and Joseph

- **The amendment.** When the recompute on Table IV's predictions lands, a second round:
  - drops the paper's one scoping sentence and the note's one scoping sentence and three caption clauses;
  - switches the `fb-`, `sens-` and `diag-` keys and the bootstrap's `gs-` χ²;
  - re-pins the modes figure;
  - can measure item 8 in the same pass.
- **":42 'Elsewhere'".** The decision removes the "Unlike the analysis definitions" sentence. Its content stays, scoped
  to the comparisons still made in the generators' definitions, because `sec:central`'s 3D and 4D comparisons use the
  frozen products. Without it, the paper would not describe those predictions' definitions at all.
- **"per nucleon of their target"** is scoped, not replaced with "of CH", for the same reason.
- **The primer** does not otherwise present the sixteen-cell comparison, so its reconciling clause says "a separate comparison on broader cells".
