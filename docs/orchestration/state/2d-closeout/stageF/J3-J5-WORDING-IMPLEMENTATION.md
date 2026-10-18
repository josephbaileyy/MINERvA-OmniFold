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
precision, and each site cites its record in a LaTeX comment. Line numbers in §1–§6 are those of `97cfdecc`; the
independent review of `97cfdecc` + `ec56f073` and its dispositions are in §7, which supersedes §6's build results.

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

## 7. Independent review of `97cfdecc` + `ec56f073`, and its dispositions

The review (`j3j5-review.md` in the director's scratchpad: a fresh read-only Claude Opus 5.5 subagent, APPROVE WITH
CHANGES, 4 MATERIAL, 13 MINOR, 8 NOTE) and the director's rulings on it (2026-10-18) are applied in the follow-up
commit on this branch. `ec56f073` (the director's) removed the Table I attribution of the log-normal χ², answering §4
item 3. Line numbers below are at the follow-up commit.

| item | ruling | disposition |
|---|---|---|
| M1 primer "construction repairs", "not been recalculated" | apply C3 at the primer; sweep all four builds | `primer_body.tex:114–136` rewritten for Q: the earlier budget's defects are named as found and removed (July sweep, Rvp1pi dropped, background stream, selection-complete laterals), the exclusions (miss-row weighting, learner, unfolding model), the split-sample sentence kept, the new inputs and "no coverage claim". The stale "matching flux variations need further verification" is removed (KI-91 established). Sweep: no "construction repairs", "not been recalculated" or "Table I correlated" in any of the four PDFs' text; `sec_method.tex:142` ("have not been recomputed", of exact-split studies) is true and kept |
| M2 KI-93 count | reviewer's counts, cite the records | `sec_systematics.tex:195–197`: "Seven of its universes, four of them also in the pilot, are reproduced to ≤1.4×10⁻¹¹ by the committed driver"; comment cites `stageC/pilot/REPORT.md` l.70–80 (K1: five comparisons, four universes) and `stageC/production/REPORT.md` l.65 (S4(ii) 7/7) |
| M3 C10 and independent-generator samples | requirement is C09's only; C10 an assumption | `sec_systematics.tex` §`sec:uq-2d-scope` third bullet: "…its regularization, whose estimate requires independent-generator samples, and departures of the detector response from its parametrized family, which we assume absent; neither is priced"; the separate assumption sentence is removed; comment cites Stage B REPORT §3 l.313–314 |
| M4 paper's 7% step | make the sentence true; note's wording, paper register | `paper_body.tex:317–319`: "one period group's unfolded p∥ distribution, taken relative to its own simulation, differs from that of the earliest periods by a step of about 7% near 8 GeV/c"; commented "Director factual correction 2026-10-18, review M4; Joseph to confirm at the Ben review" (6.94% double ratio vs 10.29% raw, period-unfold REPORT §2) |
| m1 `sec_validation.tex:91` | apply | "…and an untouched generator-truth domain for bias checks (§`sec:uq-2d-scope`)"; "the construction repairs in §`sec:uq-2d-construction`" removed |
| m2 paper G2 tightness | follow D4 | `paper_body.tex:308–310`: "…about three times the training-seed block; an effect below about twice that noise is not excluded, so the test is not tight, and the approximation is not corrected" |
| m3 antecedent | apply | "The quoted block's replica mean …" |
| m4 antecedent | apply | "We carry the effect of this inconsistency on the combined result as the run-period block …" |
| m5 paper D1 structure | apply | the list ends "…whose estimate would require independent-generator samples."; then "We assume the detector response varies only within its parametrized family."; the new-inputs sentence; "No coverage claim is made." on its own. W1(c)'s two sentences and the list's lead-in are unchanged |
| m6 primer rate vs uncertainty | apply | "For the uncertainty on the overall interaction rate the comparison goes the other way" |
| m7 KI-90 scope | apply | "…the check passes in every run of both consumers on the quoted covariance" |
| m8 "not measured" vs "tested" | apply | "…which is not measured beyond the weak test below" |
| m9 D11 inference labels and reason | apply | "(inferred)" and "(inferred from the medians)" placed per D11; "…they cannot be recomputed from the saved covariance products, and the verification compared only their inputs' digests" |
| m10 "first 150" | apply | "from a nested half (150) of the replicas" |
| m11 "flux-dominated" and "in the median bin" | apply | note `sec_results.tex:148–150`: "Its largest band is the flux, as in the publication; the systematic-universe block carries a median 0.87 of each bin's variance and 0.83 of the integral's"; paper: "dominates it bin by bin (a median 87% of the variance) and in the integral" |
| m12 J2 condition in the paper | one short clause | `paper_body.tex`, after the Required clause: "The block's own consistency check passes by construction; it is not a test." |
| m13 W4 "only" | apply | "of the five definitions recomputed, only this one reproduces χ²_log" |
| n1 a receipt for 4.61% | not applied | committing the reviewer's computation (4.6099%) as a receipt and gate binding is a new computed artifact, outside this task's no-computation rule; left for the director. `\uqPaperIntegral` stays cited to the worked example and DECISION-20261012 |
| n2, n3 | no change | n3 (W1(c) vocabulary) is the director's to raise with Joseph |
| n4 stale comment | remove | the "QUESTION for the director" comment at `app_statmethods.tex` is removed |
| n5 primer and the run-period finding | no change | Joseph's call (W3) |
| n6, n8 | no change | — |
| n7 hand Joseph the current note PDF | done | `review-pdfs-20261018/` replaced by the final build below |

**Source record.** `DRAFT-disclosures.md` is now revision 4: D10 (KI-93)'s count and D5's draft sentence on the 7% step
are corrected, with a dated note at the top naming findings M2 and M4. Nothing else in it changes, apart from the
title's revision number and date.

**Paper page count.** The fixes took the paper to 12 pages, with the last two references alone on page 12. To return
to 11 without cutting required content:
- "Subsets of the data taken in different run periods" became "Data from different run periods";
- the flux-constraint sentence and the replica-mean sentence were reworded;
- "the quoted covariance uses a sweep without that mismatch and propagates the background-simulation statistics as its
  own bootstrap stream" became "the quoted covariance is free of both" (the how is in the note);
- the rescoring sentence's parenthetical "(a post hoc diagnostic points to under-scatter of the closure
  pseudo-experiments, whose simulation-side fluctuation shares the band's resampling mechanism)" is now note-only.
  It is in `sec_validation.tex` §`sec:coverage` and KNOWN_ISSUES 85. It is not D2 must-carry, but it is pre-existing
  paper text, so the director may prefer 12 pages with it restored.

**Final build** (fresh scratch copy `scratchpad/buildcopy5/`, same layout):

| check | result |
|---|---|
| `build_all.sh` | rc 0; each PDF "written by this run; no unresolved references" after one latexmk invocation |
| pages | note 123, primer 12, paper 11, PET note 26; the executive summary keeps its page break |
| undefined references / citations; multiply-defined labels | 0 in all four logs |
| containment (strict) | SELF-TEST PASS; RESULT PASS (note 64/64, PET note 5/5; paper and primer 0 of 69) |
| Sec. IV | gzip receipt PASS; SELF-TEST PASS (18 perturbations rejected); PASS 15/15 |
| pytest (`test_check_sec4_receipts.py`, `test_build_all.py`) | 63 passed |

`review-pdfs-20261018/SHA256SUMS`:
- `main_note.pdf` `100c27b1d4d010d19cf42d017160eb7bf7ddb5ca752df0f2be720ae71c6f262f`
- `main_paper.pdf` `9cae2bc358bdd532ab22a9e501d088e6559d0138fc7849a9eb806e218204a783`
- `main_primer.pdf` `35805adf05617728dddc2ee41c1a64d4a0013c55c9729e5ae6c557cff859be7b`
- `pet_note.pdf` `f847fffbb17eae91b652e5857195ba4c1de75b19fc42088a5ff6c5ddedb42c2d`

**Same-model caveat:** the director and this implementer are Claude Opus 5.5 on the claude-school account.
