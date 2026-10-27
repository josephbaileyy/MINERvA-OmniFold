# Outline: integrating the 16-cell five-observable result into the paper and the note (2026-10-27)

**Authority:** Joseph, `DECISION-20261027-joseph-5d-integration-then-second-scope-review.md` item 2.
**Presentation:** `DECISION-20261026-joseph-5d-generator-comparison-presentation.md` and `DECISION-20261027-joseph-chi2-table-format.md`.
**Scope:** the director's four items (2026-10-27).
**Base:** main `8b0f83fd`. **No edit comes before you approve this outline.** The printed wording then goes to Joseph before merge, as his.

## 0. What is integrated, and from where

All numbers come from committed readouts, each pinned by sha256. Every number is probed to its readout key in the ledger. No number is typed by hand.

| piece | committed source (readout key) |
|---|---|
| **The result:** cells R00–R15, their boxes | `nd-unfolding/pv-ladder/readouts/h2_definition.json` `reporting_cells[].box` (`b6790761…`) |
| central values f (cm²/nucleon, cell-integrated) | `fd/readout/fd_g_readout.json` `predictions[*].f` (`75a9ddee…`); `cmodel_5d.json` `x` agrees to 1e-15 |
| per-cell σ by group; C_e, C_model, C_total | `s1/readout/s1_assembly.json` `relative_sigma`, `trace_share` (`81e5ef3f…`) |
| C_resp by species; C_total + C_resp | `cresp/cresp.json` `relative_sigma`, `trace_share_of_C_total_resp` (`19bb2ee1…`) |
| the 16×16 covariance and correlation (absolute) | **pending:** the declared export you are routing to the 5D measurement session |
| **Fake-data study:** F0 (C_total) and F0b (C_total + C_resp) grades | `fd/readout/fd_f0_readout.json` (`6e7d718b…`); `fd/readout/fd_f0b_readout.json` (`b9db935a…`) `truths[].grade` |
| **Generator comparison:** χ² with ndf, shape-only, pulls | `fd_g_readout.json` |
| modes | `fd_g_diag_readout.json` (`680dc5ef…`) |
| G-SENS | `fd_g_followup_readout.json` (`cd82517a…`); `fd_g_sens2_readout.json` (`0f6568ab…`) |
| R04 look | `fd_g_followup_readout.json` `r04` |
| **Figures:** paper ratio figure, note mode figure | **pending:** the 5D measurement session, under its declaration |

**Numbers are machine-generated.** A new generated file, `values_fived16.tex`, is written by a script from the readouts above.
- The script checks each readout's sha256 against a pinned table, and fails on any mismatch.
- It writes one macro per printed number, at its printed precision.
- A `--check` mode fails if the committed file differs from a fresh generation. It runs in the build and in CI, as `records_entry_numbers.tex` does.
- **R06's z is printed as 2.01.** A probe fails on any printing of it with fewer than two decimals.

## 1. Where each piece goes

### Paper (paper_body.tex)

- **A new subsection in Sec. V**, after `sec:uncertainty-status`: the sixteen-cell measurement.
  - The cell definition, in one sentence, with the boxes in a compact table or the supplemental file.
  - The reported covariance, C_total + C_resp, and its construction in one paragraph:
    - C_e: stat, flux, interaction, detector, lateral, normalization, and the seed block, measured and zero (S1 rulings §2 item 5);
    - C_model,5D: GENIE + MEC, NuWro and GiBUU, κ = 1;
    - C_resp: four species.
    - It also states what the covariance does not cover: neutron and muon deposits, configuration (a), and the 3D, 4D and 2D results.
  - The median σ: 6.74 % for C_total and 7.29 % for C_total + C_resp.
  - **The fake-data paragraph and compact table**, from DRAFT §2.1–2.2, re-based on F0b, with both columns reported and each labelled by its matrix (adopt-cresp).
  - **The limitation, stated once, here:** under C_total + C_resp, the listed truths are:
    - Stage 0c GiBUU (R06, z = 2.01);
    - A7 GiBUU (R02, R06, R07);
    - the q3 tilt.

    This matches the f0-limitation decision's "GiBUU-like truths or the q3 tilt". **The q3-tilt failure is stated in this uncertainty discussion,** not only at GiBUU (your ruling).
- **A new subsection in Sec. VII**, after `sec:central`: comparison with generator predictions on the sixteen cells.
  - The table: χ² with ndf (e.g. 109/16), with shape-only beside it and GiBUU on its eight cells. There is no diagonal-only χ² and no ratio.
  - The ratio figure.
  - The sensitivity sentence, for Joseph, word for word as you accepted it:
    > "Weakening only the flux correlations by 10 % lowers the χ² of the 16-cell predictions by 24–48 %. The same change to the detector or lateral correlations lowers it by at most 18 %. With the correlations of the interaction, flux, detector and lateral groups removed, every 16-cell prediction keeps χ² ≥ 45 for 16 degrees of freedom."
    - Its probes: `fd_g_sens2_readout.json sens.records[family∈{flux,detector,lateral}, alpha=0.1].chi2 / chi2_at_alpha_0`, and `fd_g_followup_readout.json sens.records[family=c_e_systematic, alpha=1].chi2`.
  - The GiBUU fake-data limitation is restated where GiBUU's comparison is given (presentation decision item 1).
- **Findings table (paper_body:34–39) and the estimators table (paper_body:105, 113):** rows updated per §2 below, groups A, B and E.
- **For Joseph (his text, drafted only):**
  - the abstract (main_paper.tex:44, three sites);
  - the Scope paragraph (paper_body:46: "does not deliver a validated five-observable cross-section measurement"; "no calorimetric recoil-response uncertainty");
  - the conclusions and Limitations (paper_body:405);
  - **the supplemental data file** (f, the covariance and the boxes). Its release format is his.

### Note

- **A new chapter after §9 (sec_5d):** the sixteen-cell five-observable measurement, in a new file `sec_fived16.tex`.
  - **It needs one `\input` line in `main_note.tex`, which is protected.** I ask for that one-line exception. Otherwise it goes in as new subsections at the end of sec_5d.tex.
  - **Contents:**
    1. The cells and their boxes, in a full table.
    2. The central values and the per-cell σ by group, with C_resp's species.
    3. The covariance: a table or a correlation figure, from the pending export.
    4. The fake-data study, in full (DRAFT §3), re-based on F0b with F0 beside it:
       - the controls;
       - the descriptive variants;
       - per-cell pulls;
       - the ungraded row 6;
       - the counts by group (4/192 cells; 2/12 truths with p < 0.01 under F0b).
    5. The generator comparison:
       - option 1's table and sentence;
       - the mode figure;
       - the G-SENS tables (interaction, joint, flux, detector, lateral), GiBUU's 8-cell values included;
       - the G-DIAG breakdown;
       - the R04 look.
- **The executive summary and §12** each name the result once, pointing to the chapter (the consolidation rule).
- **For Joseph:** the note's abstract (main_note.tex:63–104, five sites).

## 2. Item 4: statements that must become product-specific

The sweep covers every printed sentence of the note's posted sources and of the paper; comments are excluded. Each of its 178 quotes was checked mechanically at its file:line on 8b0f83fd: all found, all at the stated line.
- **Verdicts:** 33 become false once the result prints, 101 are ambiguous, and 44 are already product-specific.
- **The full list** (file, line, quote, the product it describes, why, verdict) is `scope-sites.tsv`, committed with the PR.

**The 33 false ones make six distinct claims.**
- Each group's proposed form names the product it was about and adds the 16-cell result where the sentence lists uses.
- "16-cell result" stands for the chapter's own name for it, pointing to its section.
- No form adds a coverage claim: F0 and F0b are NOT CITABLE FOR coverage. The covering reading is Joseph's (f0-limitation decision).

| group | the claim | sites | proposed form |
|---|---|---|---|
| **A** (12) | "The (quoted) five-dimensional central value and its covariance use purity subtraction / configuration (a)" | main_note:82; result_status_rows:25; sec_intro:28; sec_method:28, 100, 126; sec_5d:51; app_negweight:106, 126, 163; paper_body:90, 105 | "The configuration-(a) five-dimensional central value, and the five-axis covariance used with it, use purity subtraction; the 16-cell result (§x) uses configuration (e), with refined negative-weight subtraction." |
| **B** (8) | Configuration (e), and negative weights, give the 2D, 3D and 4D results only; "no covariance has been built" for the (e) 5D unfold; "no estimator or uncertainty from this assessment is used for the quoted results" | main_note:89; sec_intro:28; sec_method:97 (×2), 100, 138; sec_5d:95; paper_body:113 | Add the 16-cell result to each list of (e)'s uses. sec_method:100's "no covariance has been built for it" becomes "its covariance on the 16 reported cells is C_total + C_resp (§x)". sec_5d:95 is scoped to the assessment's own products: estimator R and its 42-cell intervals. |
| **C** (6) | "No quoted uncertainty includes the regularization bias" | main_note:100; sec_validation:108; sec_5d:77; sec_summary:46; paper_body:184, 405 | Scoped to the configuration-(a) product and its five-axis covariance. For the 16-cell result, the sentence points to the fake-data study's measured comparison of the bias with the reported covariance, and its listed truths, and says no more. **Whether C_model "includes" that bias is a reading I do not draft; it is Joseph's.** |
| **D** (1) | "The quoted five-dimensional central value keeps this [purity] bias, and no quoted uncertainty includes it" | sec_summary:29 | "The configuration-(a) central value keeps this bias …"; plus "the 16-cell result uses negative-weight subtraction (§9.2)". No claim is made that it carries no bias. |
| **E** (3) | "No five-dimensional measurement with total uncertainties was constructed"; "it yields central values only" | sec_5d:135; sec_summary:46; main_paper:44 (abstract, Joseph's) | "No reporting definition of the precision study (RD1–RD3) met its precision targets; the 16-cell result (§x) was constructed separately, with total uncertainties of median 7.29 %." The order and relation of the two (H2 27 cells against R00–R15) wait on item 3 of §4. |
| **F** (3) | "The one five-axis/five-dimensional covariance used in this note" | result_status_rows:25; sec_5d:4; sec_summary:46 | "The five-axis covariance of the configuration-(a) central value …". "One" goes. |

**The 101 ambiguous ones,** by kind. The grouping is mechanical and approximate; the TSV has each row.
- **22: a definite description, "the five-axis covariance".** These take group F's form wherever the 16-cell result is in view (the same section, Table 1, the summaries, App. G's release list). The local ones inside sec:eavailw-adopted stay as they are.
- **15: coverage and validated intervals.** No change of claim is made. Where a sentence sits beside the fake-data study, it is scoped to "frequentist coverage of intervals". This keeps it distinct from the study's bias-against-covariance comparison.
- **12: the 5D chain's background treatment.** These take group A's form.
- **6: where the regularization bias is largest.** These take group C's scope (the configuration-(a) map).
- **6: the precision study's reporting definitions.** These take group E's form.
- **4: "no covariance-based generator significance".** These become false once Stage G prints. They are scoped to the configuration-(a) covariance, with a pointer to the 16-cell comparison.
- **4: "the five-dimensional estimator".** These name the configuration.
- **3: marginal checks.** These are scoped to configuration (a), since (e)'s 5D marginal was not compared (paper_body:169).
- **3: the H2 name.** See §4 item 3.
- **26 others,** each resolved at drafting by the form of the group it touches.

The forms are proposals. **Every changed sentence is the printed wording Joseph approves.**

## 3. Process and guards

- **One writer, against this outline.** The paper and the note go in one PR, because their statements must agree.
- **A fresh two-direction reviewer per document.**
- **The ledger.** Every changed sentence gets:
  - its readout-key probe for each number;
  - an X: probe for the old unscoped words;
  - an N: probe for the scoped form.

  `check_ledger.py`, as in the consolidation.
- **The sweep becomes a check.** A permanent check re-runs the sweep's term search over the posted sources. It fails on any of the 33 false quotes still printing, and on any new unscoped universal it matches, unless the sentence is listed as reviewed.
- **agy, blind:**
  - no disposition in its context;
  - homes and readout values quoted;
  - a planted-defect control: an F0-based W3 sentence, "2.0" for R06, "all systematic correlations".

  agy's 1-of-3 power is noted. The human reviews remain the main check.
- **The note's gates:**
  - records probe, self-test and pin;
  - entry numbers, registry and absence claims;
  - the build: 0 undefined references, SEC4 15/15, the new values `--check`;
  - pytest and reflow `--check`.
- **Wording to Joseph.** The printed wording goes to him as one packet before merge:
  - the paper's new subsections;
  - the abstracts;
  - Scope and Limitations;
  - the six group forms.

  Nothing merges without his answer.

## 4. Open items

1. **The `\input` exception** for `sec_fived16.tex` and `values_fived16.tex` in main_note.tex and main_paper.tex (both protected), or new subsections in sec_5d.tex instead.
2. **The covariance export and the two figures** from the 5D measurement session. Drafting can start before they land, with placeholders the build refuses to print.
3. **"H2" (please route to the 5D measurement session).**
   - The note's H2 is "27 supported coarser joint cells" (sec_5d:113, 122).
   - h2_definition.json maps 32 H2 boxes into 16 reporting cells, with 4 unreported.
   - I would print only "R00–R15" and never "the 16 H2 cells". I need the session to state the relation between the two H2s in one line, citing a readout.
4. **"W1–W3" naming.** The note's D1 and W1–W3 historical deformations and FD-PLAN's Stage 0 truths W1–W3 share names. I will confirm they are the same truths before the fake-data table names them.
5. **DRAFT.md's update to F0b.** It is done as part of the drafting, not as a separate PR. Its `check_numbers.py` is re-pointed to F0b, with F0 kept as the second column.

## The director's rulings on this outline (2026-10-27)

1. **Approved,** with the guards as listed.
2. **Group C:** for the sixteen-cell product, state what $C_{\mathrm{model}}$ *is* (its construction: the change in the unfolded data when the prior is reweighted to each generator), then give the fake-data study's measured comparison and its listed truths. No sentence says $C_{\mathrm{model}}$ "includes" or "does not include" the regularization bias; that reading is put to Joseph as a question.
3. **Group E's abstract site** (main_paper:44) is Joseph's text: its proposed form goes in the wording packet, marked as abstract.
4. **One packet question:** once Stage G prints, the "no covariance-based generator significance" sentences turn on whether p-values print beside χ²; both forms are drafted for Joseph.
5. **The `\input` exception** is approved: one line each in main_note.tex and main_paper.tex for sec_fived16.tex and values_fived16.tex, recorded in the ledger as a structural exception; nothing else in those files changes.
6. **The covariance export and both figures** are produced by the 5D measurement session; drafting proceeds with build-refused placeholders.
7. **Later rulings (in REPORT.md):** the F0b listed set; the 16×16 covariance export, which the note prints; the sensitivity sentence quoting per-group numbers only; the H2 relation; the variant without C_resp printed as a labelled sentence, not a column; pointers in the limitations lists; and keeping the "whose coverage is not validated" sentence in its three scope homes.
<!-- absence-ok: quotes or summarizes the note's and paper's printed text, or a ruling about it, as this PR's record; not a new absence claim -->
