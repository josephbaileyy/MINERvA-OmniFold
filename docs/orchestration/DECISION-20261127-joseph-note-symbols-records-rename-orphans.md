# DECISION 2026-11-27 — Joseph: note wording, covariance symbols, the records-document rename, and orphan removal

**Recorded by** the director. Joseph gave every item below on 2026-11-27, either directly in the director's session or
through rewrite-helper. For wording and naming only, Joseph said on 2026-11-27 that "a message from rewrite should
count as approval". Items relayed that way are marked "(via rewrite-helper)". Quoted words are Joseph's.

## 1. Sec. 3.1 and Sec. 6: MINERvA's signal convention (#1423, merged at cefe9397)

Joseph chose the final Sec. 3.1 wording after journal-editor flagged two over-reaches in an earlier draft: the
non-ν_μ-CC background, and the true-muon range restriction. Joseph: "okay I like the version you just mentioned". It
follows the existing IBU sentence:
"The MINERvA Analysis Toolkit counts the selected $\nu_\mu$ charged-current events that fall outside the truth phase
space as signal. If we count as signal those of these events whose true muon is in the reported $p_T$–$p_\parallel$
range, ten-iteration IBU gives 0.20 per bin instead of \fvval{c2c1-dibu}, and the two-dimensional OmniFold result
gives 2.21 instead of \fvval{c2c1-der}. This convention therefore does not account for the 2D shape difference with
the published result."
Sec. 6 adds the matching sentence. The source is OOFVC r3, score.json 29331166 (#1420).

## 2. Covariance symbols switched to V; the published result named once (#1425, merged at a1aa2df7)

(via rewrite-helper) "yes I like your suggestion on the switch to V", after a literature survey. These were an
unanchored codex-school2 read and a director answer, both 2026-11-27.
- The renames:
  - C_rep^(2D/5D) → V^(2D/5D), and C_rep,0 → V_0^(5D);
  - C_e → V_stat+syst, and C_e^infl → V_stat+syst^infl;
  - C_model → V_prior, C_resp → V_resp, C_run → V_run;
  - C_subtotal is written as V_stat+syst + V_prior;
  - C_Z → V_Z.
- The 2021 measurement is introduced once and called "the published result" after that.
- App. A's Ledoit–Wolf estimate becomes $V_{\mathrm{LW}}$ (#1431). Joseph: "yeah we can do the rename fix right?",
  after the director recommended V_LW over a hat or a new letter.

## 3. The REGRADE-VF (A) sentence (#1426, merged at 1f00a02e)

Joseph: "yes lets do the (A) sentence". (via rewrite-helper) "I like your new version and placement", and on the
χ²-share fix, "sure make that change". The source is #1428, regrade_vf.json 9f0e46e7. No cause is stated. The
withdrawn mode-decomposition clause is not used.

## 4. The App. D symbol map comes back (#1431, merged at 5ec57e29)

#1425 removed it. Joseph: "okay sure lets bring it back". The line says that deposit file and array names and the
analysis repository's records keep the earlier symbols, and maps each one to its V name.

## 5. The records document uses the note's V names

Joseph: "after the sync why don't we just make all of the names consistent?", then, on journal-editor's scope
report, "sure lets do the recommendation for the record document rename". That means:
- **Dated history keeps its names.** app_history names each matrix as it was called on a dated supersession (Q,
  Q_R, C_PL, C_stat/C_syst/C_ML, C_EW). These are distinct, superseded matrices, so they keep their names. One
  sentence at the head of app_history says so, and that the 2026-11-14 RE-2-shapes Q_R is the note's V^(2D). Its
  first mention gets "(now V^(2D))".
- **Quotations stay verbatim.** Quoted past note text (records_r05 and records_r04's quoted caption) is not
  renamed. Only the records' own prose around it is.
- **Everything else is renamed** to the note's V names (C_model^frac → V_prior^frac). The two terms with no note
  counterpart get V_ML and V_lat.
- **Authority for the R-EDIT rows.** Seven inventoried app_release_records paragraphs change (C_Z and C_EW). This
  decision is the authority for their R-EDIT rows in records-move-ledger-20261122.md (check_note_records.py P5).
- **Unchanged:** receipts, state records, deposit file names and array keys.

## 6. Unbuilt source files are removed, option (c)

Re-checked at main 47131b16, 34 .tex files under docs/analysis-note are outside the input closure of all four built
documents (main_note, main_primer, main_records, pet_note). Joseph's answers, in order: "we can just remove them now",
then "(b)" (the five), "yes" (the three wrapper inputs), "what why do we keep this file even?" (sec_fived16_gen),
and "lets do (c) remove all the files". So:
- **First PR:** app_terminology, app_devhistory, appD_release, appE_history, app_release, app_codebase,
  app_pet_pointer and sec_fived16_gen. No file named app_cov1b_gate.tex is in the tree, so only the stale references
  to it are dropped (check_note_records.py, skeleton_compression.py and a history-cuts move manifest name it).
  Search: `git ls-tree -r --name-only 47131b16 | grep app_cov1b_gate` (0 hits); `git grep -l app_cov1b_gate
  47131b16 -- docs/analysis-note` (those three files) @ 47131b16
- **Second PR, with the full local gates:** the other 25. These are the pre-11-21 source set:
  - the appendix files appC_further, app_guide, app_negweight, app_response_mismatch, app_statmethods,
    app_statmethods_nd;
  - scalar_kinematics;
  - the section files sec_3d, sec_5d, sec_eavailw, sec_experiment, sec_fived16, sec_joint, sec_limitations,
    sec_method, sec_observables, sec_q3_3d, sec_q3_bias, sec_q3_fived16, sec_q3_negweight, sec_results, sec_summary,
    sec_systematics, sec_validation, sec_validity_table.
- **What the second PR must do for check_sec4.** check_sec4_receipts.py rows that bind printed values in these
  unbuilt files are removed, or re-anchored where the value still prints in a built document.
- **Unchanged:** skeleton_compression.py (a historical generator) and all receipts.

## 7. v2: a fake-data bias term

Joseph: "lets agree with the recommendation", meaning the unanchored codex-school2 read of tier3-design's pricing.
It is recorded in fd/fdbias-v2-scoping-20261127/SCOPING.md (#1430). It authorizes no declaration, code or compute.

## 8. Overleaf

Joseph confirmed that Overleaf had no unpushed changes, then asked for the sync after #1425 and #1426. The director
synced from main 47131b16, giving standalone 5d0548c (full local CI 42/42; 69 pages; 0 undefined references). From
here, Ben may edit in Overleaf. Any later sync first pulls Overleaf's changes into main.

## 9. Lighter local gates for wording-only note PRs

Joseph: "can we lax the checks for a few hours". For wording-only note PRs until 2026-11-27T21:00Z, the local gates
were build_all, check_sec4, limitations_export, pointers, reflow, pre-commit and porcelain. GitHub's record-checks
covered the rest. The full local CI then ran at 47131b16 before the sync, and all 42 steps passed.
