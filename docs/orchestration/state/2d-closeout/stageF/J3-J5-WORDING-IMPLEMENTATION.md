# Stage F: the provisional J3–J5 wording, written into the deliverables (implementation record)

**Implementer:** a Claude Opus 5.5 subagent of the paper-tighten lane (director), 2026-10-18, in the worktree branch
`stageF/j3-j5-wording-20261018` from `8f7dc962` (= `origin/main`). Governing records:
[`DECISION-20261018-joseph-2d-j3-j5-provisional.md`](../../../DECISION-20261018-joseph-2d-j3-j5-provisional.md) (binds
this work), [`DECISION-PACKET-J3-J6.md`](DECISION-PACKET-J3-J6.md) (items C1–C8, W1–W10, J5) and
[`DRAFT-disclosures.md`](DRAFT-disclosures.md) revision 3 (D0–D12).

**CITABLE FOR:** which deliverable lines carry the provisional J3–J5 wording, the source record each number is taken
from, the KI-85 row edit, the Sec. IV gate's new binding, and the scratch-copy build and gate results.
**NOT CITABLE FOR:** final wording (every choice is provisional until the review with Ben, DECISION-20261018 §2);
any outward act (J6), including the standalone `MINERvA-OmniFold-Analysis-Note` sync; a coverage, calibration or
validation statement; an independent review of this wording (the decision's follow-on step 2, not done here).

No number was computed for this change. Every printed number is a field of a committed record, at the printed
precision, and each site cites its record in a LaTeX comment. Line numbers below are those of this commit.

## 1. Summary

- **Markers:** all 84 `J[345] pending` occurrences (65 lines in 17 files) are resolved. `grep -n 'J[345] pending'
  docs/analysis-note/*.tex` now prints nothing. 87 comments of the form `% J3/J4 provisional (DECISION-20261018,
  packet <item>)` replace them; some sites were split.
- **Paper (§`sec:uq2d`):** D0 with the C2 comparison, D3 (training-seed block), D4 (G2), D5 with its Required clause
  verbatim, D2 (with the replica-mean offset), D1 in register (c) followed by the C3 sentence, and one pointer sentence
  to the note. The 6.87% clause is removed (W5). The learner dependence in §`sec:repro2d` gains its maximum (W6).
- **Note:** a new subsection §`sec:uq-2d-scope` ("Scope, conventions and limits of the 2D construction") carries D1,
  D12, D4, D6, D7, D9, the KI-90 sentence (W8) and D11. D2, D8, D10 KI-88 and KI-94 are in §`sec:uq-boot`; D3 in
  §`sec:uq-ml`; D10 KI-91, KI-93 and the laterals in §`sec:uq-2d-construction`; D5 in full in §`sec:uq-combine`;
  D0 and C2 in §`sec:results-uq`; W4 in the worked example of §`sec:chisq`.
- **Primer:** C2 (the integral, "the comparison goes the other way") and W5.
- **Macros (values.tex:146–154):** `\uqIntegral` 4.75, `\uqPaperIntegral` 4.61, `\uqSFiveMedian` 6.04, each with
  its receipt.
- **Gate:** `check_sec4_receipts.py` binds `\uqIntegral` to `budget_Q.json.gz` `Q.integral_sigma_pct`; a test is added.
- **J5:** `KNOWN_ISSUES.md` row 85's status cell gains the dated re-scope sentence; nothing else in the row changes.
- **Build:** rc 0; pages note 123 (120 before), primer 12, paper 11 (unchanged), PET note 26; 0 undefined references;
  both gates PASS; pytest 63 passed.

## 2. Per packet item

### J3, the claims

| item | decision | sites changed | sources cited |
|---|---|---|---|
| C1 | keep "uncertainty scale" | no text change; markers at `main_note.tex:56`, `sec_summary.tex:18` | — |
| C2 | quote both the per-bin median and the integral against the published values | `paper_body.tex:277–283`; `sec_results.tex:144–152` (and the sentence after, "and its integral larger"); `primer_body.tex:215–220`; `sec_execsummary.tex:26–30` | `stageF/rebuild/outputs/outA/budget_Q.json.gz` `Q.median_pct` 6.448, `Q.integral_sigma_pct` 4.755 (rebuild REPORT §3); `\uqPaper` 6.85 (`uqpaper-median-20261006`); `\uqPaperIntegral` 4.61, see §4 item 1 |
| C3 | replace "construction repairs" with the D1 list of what lies outside every block | `paper_body.tex:371–385` (the D1 list, then "Validated total intervals … require new inputs, namely …, and no coverage claim is made"); `sec_validation.tex:290–297` ("need new inputs (§`sec:uq-2d-scope`), which also lists what lies outside every block") | DECISION-20261014 §2 (the three missing inputs; no coverage claim); DECISION-20261017 §2 (G2, learner, C09/C10 in no block) |
| C4 | keep; the note takes D2's sentence | kept at `paper_body.tex:69`, `:356` ("Coverage of the total remains untested"), `:874`; `primer_body.tex:105`, `:236–239`; `sec_summary.tex:14–18`. D2 in the note: `sec_systematics.tex:108–126` | KNOWN_ISSUES 85; rebuild REPORT §3 |
| C5 | the note keeps the descriptive χ² register; the paper quotes no combined χ² | no change; checked: `paper_body.tex`, `main_paper.tex` and `primer_body.tex` print no `\chiCombined`, 0.964 or 0.987 | — |
| C6 | keep | no change (`paper_body.tex` §`sec:repro2d`, learner at the level of one unit of χ²/ndf) | — |
| C7 | keep the regularization scan and rescoring, labelled historical | `sec_results.tex:69–74` ("the historical regularization scan of the exact-split cross-check (on an earlier covariance)"); `app_statmethods.tex:822` (paragraph title "Regularization scans (historical; …)"); `sec_validation.tex:276` ("The rebuilt band, scored post hoc (historical).") | rebuild REPORT §6 |
| C8 | keep the abstract's construction sentence | no change; marker `main_note.tex:56` | — |

### J4, the disclosure wording

| item | decision | sites changed | sources cited |
|---|---|---|---|
| W1 | D1 register (c) | paper `paper_body.tex:371–385`; note `sec_systematics.tex:302–331` (§`sec:uq-2d-scope` "Endpoint"). Both: the preparation packet's first two sentences, then the director's list (G2, the learner dependence, the unfolding-model and regularization dependence, response departures) | DECISION-20261014 §2; DECISION-20261017 §2; Stage B REPORT §3 R8 (C09/C10, via DECISION-20261017) |
| W2 | append D5's Required clause verbatim | paper `paper_body.tex:323–326`; note `sec_systematics.tex:276–279` (verbatim, three sentences) | DRAFT-disclosures D5 (PR #145 clause) |
| W3 | D0–D5 in the paper; D9–D12 in the note only, with one paper pointer | paper: D0 `:277–283`, D3 `:298–304`, D4 `:305–313`, D5 `:314–334`, D2 `:336–362`, D1 `:371–380`; pointer `:383–385` (covers D6–D12). Note: D0 `sec_results.tex:144–152`; D2, D8, KI-88, KI-94 `sec_systematics.tex:93–127`; D3 `:152–172`; KI-93 `:194–200`; KI-91, laterals `:219–233`; D5 `:254–292`; D1, D12, D4, D6, D7, D9, KI-90, D11 `:299–425` | per site, in comments; §3 below |
| W4 | the note lists the alternative log-normal values beside 0.987 | `app_statmethods.tex:580–587` | rebuild REPORT §5 (1.197, 0.958, 0.963, 1.015; 0.987 only with the quoted definition) |
| W5 | drop the 6.87% clauses from paper and primer; the note's history appendix keeps the chain | removed from `paper_body.tex` (old l.278–280) and `primer_body.tex` (old l.215–216). The note: `sec_results.tex:156–158` keeps its clause, pointing to App. `app:history`; the executive summary keeps "which an earlier version omitted (§`sec:results-uq`)" without the number (§4 item 5). App. history unchanged | App. history errata (VL175 rows) |
| W6 | D3 with median and maximum | `paper_body.tex:233–240`; `sec_systematics.tex:159–162`; `sec_systematics.tex:313–316` | `docs/orchestration/receipts/2d-lgbm42-20261011/lgbm_central_metrics.out`, row `CV42_universe_file`: `med\|d vs E_C\|%` 0.983, `max\|d\|%` 12.18 (the note already printed both at `sec_method.tex:134`) |
| W7 | keep the flux sentence | kept at `paper_body.tex:292–294`, `primer_body.tex:212–214`, `sec_results.tex:153–155` | `budget_Q.json.gz` `bands.Flux.median_pct` 3.747 |
| W8 | the KI-90 note sentence | `sec_systematics.tex:386–399` | rebuild REPORT §2 |
| W9 | D11's two universes, note only | `sec_systematics.tex:400–425` | stageC/production/REPORT.md §3 (X03 table) |
| W10 | keep the legend labels | unchanged; markers at `sec_systematics.tex:61`, `app_statmethods.tex:301`, `:466`, `sec_results.tex:194`, `paper_body.tex:262` | — |

### J5, KI-85

`KNOWN_ISSUES.md` row id 85 (file line 75): the packet's draft status addition, dated 2026-10-18, with "(Joseph, J5,
provisional until the review with Ben; DECISION-20261018-joseph-2d-j3-j5-provisional.md)", is appended to the end of
the status cell. `git diff --word-diff` shows exactly that one insertion; the severity, failure, detail and `updated`
cells are unchanged (the `updated` cell still reads 2026-10-07, as instructed).

## 3. Numbers newly printed, and their records

| value | where | record |
|---|---|---|
| 4.75% / 4.61% integral | paper, note, primer, exec summary | `budget_Q.json.gz` `Q.integral_sigma_pct` 4.755; 4.61: §4 item 1 |
| 6.04% (S5 total median) | paper, note results | `budget_Q.json.gz` `S5_total.median_pct` 6.041 |
| variance shares 0.87 / 0.83 | note results | `budget_Q.json.gz` `block_shares.universe` 0.871 / 0.828 |
| 0.06% per bin, ≈70% (71%) in variance; 0.30; 0.685; 0.076 | paper, note uq-ml | stageC/production/REPORT.md §3 (C08 0.057%, 4 dof, 71%; σ_c08/σ_ML 0.304; interaction/B 0.685; X02 0.0758) |
| 12.2% learner maximum | paper, note | `receipts/2d-lgbm42-20261011/lgbm_central_metrics.out` (12.18) |
| G2: 2 of 187, seeds 42/43, ≈3×, 1.28–1.29 | paper, note | DECISION-20261015-joseph-g2-carry §1–2; production REPORT §3 |
| D5: 7% (6.94 ± 0.41) at 8 GeV/c; 33.8 [1.8]; z < 0.7; 2.14/3.31/5.69; 1.24–3.36; 1.97; 1.8 dof; 5.4/34.5/9.9/21/9.9/17.1; 1.45/1.09; 34.8 → 1.97 | paper (rounded), note | period-unfold-20261014/REPORT.md; playlist-term/REPORT.md §2; COMBINATION-REPORT.md §2–3 |
| 0.26 σ offset; 1.001 nested ratio; 0.26 bkg-only | paper, note | rebuild REPORT §3; production REPORT §3 (1.0012; 0.263) |
| KI-93: 1.4e-11, five and seven | note | stageC/pilot/REPORT.md K1; production REPORT §2 (S4(ii) 7/7) |
| KI-91: 900 × 100, 5.5e-14, 0.245; 12 playlists | note | stageB/REPORT.md (§2.1); `s5.json` `checks.weights_*` |
| D9: 0.18 / 0.32; 0.084; 0.57; 0.17; −1.79 to 3.13; 0.28 | note | KNOWN_ISSUES J36; period-unfold REPORT (J36); `outputs/analysis.json` `comparisons.J36` |
| D12: 0.12–0.50%, 0.08–2.26 σ; 1.4% rank 1 | note | production REPORT §3 "Centring (R9)"; budget_Q bands |
| D11: 0.076; 1.24–1.33; 0.114/0.235; 0.266/0.220 | note | production REPORT §3 |
| D7: 2% | note | stageB/diagnostics/REPORT.md §6.2 |
| W4: 1.197, 0.958, 0.963, 1.015 | note | rebuild REPORT §5 |

## 4. Questions for the director, and what was not done

1. **The published 4.61% has no machine-readable receipt.** It is the value already in the note's worked example
   (`app_statmethods.tex`, §`sec:chisq`), stated as reproducing in
   `docs/publication/DECISION-20261012-joseph-adopt-2d-c04-repair.md` l.60–61 ("the code that gives 4.61 % for the
   paper") and in the VL175 commit `5b24ca2e`'s message. No committed JSON or log holds it (searched
   `docs/orchestration/state/2d-closeout/`, `receipts/2d-*`, `uqpaper-median-20261006`, `ki84-*`, the ledger).
   `\uqPaperIntegral` cites those records and is **not gate-bound**. A receipt would need a computation, which this
   task excluded.
2. **D1's reason and "no coverage claim".** Register (c) is the packet's two sentences plus the director's list; D1's
   must-carry list also requires the reason (the three missing inputs) and that no coverage claim is made. The paper
   carries them in the C3 sentence, worded from DECISION-20261014 §2; the note also keeps the director's draft's
   "goodness-of-fit values computed with it are indicative". Confirm this is within (c).
3. **`app_statmethods.tex:621–623`** still says the log-normal variant is "matching the paper's Table I correlated-flux
   normalization treatment". Review m8 (phase 2) dropped that attribution at the worked example only. I added "under
   the definition stated with the worked example above, on which the value depends" (W4) and left the attribution;
   whether it stands is a question.
4. **Packet C7's line citation.** The packet cites "the post hoc rescoring (`app_statmethods.tex:786`, `:819`)". At
   `:786` the paragraph is the ours-only direct inverse for Q (23.57 / 23.23), not a rescoring; its historical values
   are already in App. `app:history-vl175`. I marked it C7 without a text change, and labelled the rescoring of the
   VL170 band "(historical)" in `sec_validation.tex`, where it is.
5. **Page-count trims, to keep page counts:**
   - executive summary (one page before, one line over after C2): the 6.87% value is dropped there, and the clause
     keeps its pointer to §`sec:results-uq`, which keeps the value; "(exact-split cross-check 3.66)" became
     "(exact-split 3.66)";
   - paper (12 pages, two references spilling, before the trims): the pointer sentence lists no examples; D5's draft
     sentence "With few period groups, its own size is poorly determined" is in the note only (the Required clause's
     "small number of groups" carries the limit in the paper); D4 names the two universes by kind ("a
     resonance-production and a flux universe") rather than by property.
6. **Primer:** no run-period (D5) or other D-item text was added; W3 places D0–D5 in the paper and D0–D12 in the note.
   The markers there are resolved as "not in the primer".
7. **Not done:** the independent review of this wording (DECISION-20261018 §2 step 2); the claims map update (R5) and
   the K1–K4 record updates (VL rows, AGENTS.md, the 2D status file, claim tables); the standalone
   `MINERvA-OmniFold-Analysis-Note` sync (J6); any push or PR.

## 5. Gate change

`check_sec4_receipts.py` gains `total_integral()` (`budget_Q.json.gz` `Q.integral_sigma_pct`) and a `CHECKS` row
binding `\uqIntegral` in `values.tex` at "round" precision (4.75 against 4.75498). The self-test perturbs it
automatically (18 perturbations rejected, from 17). `test_check_sec4_receipts.py` asserts the binding reads 4.7550 and
that a wrong macro (4.76) fails. `check_dead_containment.py` is unchanged.

## 6. Build (scratch copy, never the worktree)

`scratchpad/buildcopy3/repo/docs/analysis-note/` (the tree without `archive/`, with `repo/docs/orchestration/state`
symlinked to the worktree's: buildcopy2's layout), local TeX Live 2024, `bash build_all.sh`, on the committed sources:

| check | result |
|---|---|
| `build_all.sh` | rc 0; each of the four PDFs "written by this run; no unresolved references" after one latexmk invocation |
| pages | note 123 (120 before), primer 12 (12), paper 11 (11), PET note 26 (26) |
| undefined references / citations; multiply-defined labels | 0 in all four final logs |
| PET note `\notesec{}` targets | resolve (no title renamed; 0 undefined) |
| `check_dead_containment.py` (strict) | SELF-TEST PASS; RESULT PASS (note 64/64 and PET note 5/5 struck literals; paper and primer 0 of 69) |
| `check_sec4_receipts.py` | gzip receipt PASS; SELF-TEST PASS (18 perturbations rejected); PASS 15/15 |
| `pytest test_check_sec4_receipts.py test_build_all.py` (in the copy) | 63 passed |

PDF sha256: `main_note.pdf` `75570e27…`, `main_paper.pdf` `6a6087e6…`, `main_primer.pdf` `63d8177d…`,
`pet_note.pdf` `4f6d81de…`. The PDFs are not committed; copies are in the director's scratchpad
(`review-pdfs-20261018/`).

**Same-model caveat:** the director and this implementer are Claude Opus 5.5 on the claude-school account.
