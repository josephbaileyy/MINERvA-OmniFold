# App. I (app_devhistory.tex), the pass of 2026-11-15: cut log

**Under** the director's approval (2026-11-15) of the style-recheck plan, item C: "all of App. I". The recheck is
`note-style-recheck-6c38249bcf5c.md` (codex-school, style only), §2 "App. I: useful and selective, with gaps". The
director's earlier ruling widened App. I to consequential changes and exposures.

**Base:** `docs/analysis-note/app_devhistory.tex` at `80e8fb416307bb48c75e97fbb5c9c871c423fc69`. Each new row restates
the body at the cited place and adds no claim; each removed or shortened cell stays at the base sha, its ledger home.

## The changes

| id | where | old | new | source in the body |
|---|---|---|---|---|
| I1 | :8, the opening | "…superseded, stopped or changed during the analysis, where the change matters for reading a released result. Each row states what had already been seen when the change was made." | "…superseded, stopped or changed during the analysis, and choices made after results had been seen, where they matter for reading a released result. Where the body states it, each row gives what had already been seen when the change or choice was made; a dash means the note does not state it." (The recheck's alternative, "qualify the introductory promise": the seven dashes stay, because no cell may infer an absence of exposure.) | the director's widening ruling |
| I2 | :12, caption | "Superseded configurations and changed tests." | "Superseded configurations, changed tests and choices made after results had been seen." | as I1 |
| I3 | :29, the configuration-(a) 5D row | "…configuration~(a)"; "The five-observable central value"; "Not rebuilt: …"; "That result only; …" | "…configuration~(a), retained"; "The five-observable central value and its covariance"; "Retained, not rebuilt: …"; "That result, within the limits of Table~\ref{tab:result-status}; …" | sec_execsummary.tex:38 (Table 1's C_Z row); sec_5d.tex:294 |
| I4 | :32, the earlier 2D budget | outcome "Construction defects, each corrected in the quoted budget, among them [the three defects]"; applicability "Its printed values are unchanged; it remains a comparison for the flux weights (…) and the run-period step (…)" | outcome "Construction defects (§uq-2d-scope), each corrected in the quoted budget"; applicability "Printed uncorrected, as a comparison only: in §uq-2d-scope, for the flux weights (…) and for the run-period step (…)" | sec_systematics.tex:282–286 (the defects, "The values printed for the earlier budget were not changed"), :143, :166. Search for other uses: `grep -n -i 'earlier 2D budget\|earlier budget\|TwoDFollowup2026' *.tex` finds only these, App. I, primer_body.tex:130 (the primer's summary of the same defects) and sec_validation.tex:46 (the follow-up assessment, not the budget). |
| I5 | :44, D8 | the stabilization-probe row | removed (the recheck: nothing changed and the row supplies no exposure; the negative result stays in §9.3, sec_5d.tex:101) | sec_5d.tex:101 |
| I6 | :48, D10's label | "Coverage test of the sixteen-cell result" | "Staged coverage test of the sixteen-cell covariance rebuilt at each of the two tunes, stopped at its first stage" | sec_fived16.tex:283 |
| I7 | :51, D11's outcome | "It did not pass its first two tests and was not pursued further: Stage~0 failed its first part on both sets of cells and stopped, and in the reconstruction-information test no configuration met its residual requirement, a study that remains incomplete; …" | "Not pursued after its first two tests: Stage~0 failed its first part on both sets of cells and stopped; the reconstruction-information test, which remains incomplete, had no configuration meeting its residual requirement. …" (the distinction between the failed Stage 0 and the incomplete study is kept) | sec_fived16.tex:110–115 |
| I8 | :53, D12's label | "Coverage test at the two tunes for the covariance without the run-period block" | "…, stopped at a gate" | sec_fived16.tex:279 |
| I9 | :51, D11's "Already seen" | "--" | "The results of the route's first two tests, when $C_{\mathrm{model}}$ was adopted unscaled" (pass 1 of the read: the dash made I1's "a dash means the note does not state it" false for this row) | sec_fived16.tex:110 ("did not pass its first two tests and was not pursued further, after which $C_{\mathrm{model}}$ was adopted unscaled") |
| I10 | :54, D13's "Already seen" | "…were fixed before the measurements that decide them were computed, and none occurred" | "…were fixed before the measurements that decide them were computed, after the block's reported numbers had been read; two were not expected to fire, and none occurred" | ruling 2; sec_fived16.tex:196 (T9) |
| I11 | app_guide.tex:6 | "with the configurations and tests superseded or changed during the analysis (App.~…)" | "with the superseded configurations, changed tests and consequential choices made after results were seen (App.~…)" | ruling 3 |
| D13 | new | — | the run-period blocks C_PL and C_PL,5D: assigned after the period differences had been seen; built from them, so they contain them by construction; the containment gives no information on size or coverage; the sixteen-cell results with and without C_PL,5D; already seen: the period differences, and for C_PL,5D the conditions fixed before the measurements that decide them were computed, none occurring | sec_systematics.tex:166, :187; sec_fived16.tex:187, :196 (T8 of history-cuts/sec_fived16.md, whose records check is there) |
| D14 | new | — | the joint-test design: fixed before any production pseudo-experiment or observed statistic, with two data-informed elements; the budget extension decided during production so that the sequential rule could set the stop; no statistic, variant, threshold or stopping rule changed; the familywise bound holds whatever rule set the stop; already seen: descriptive per-cell residuals (the design's reviewers), observed claim p values in the monitoring output (the extension) | sec_joint.tex:126 |
| D15 | new | — | the matched coarse-projection comparison: no test meets its criterion, no evidence of additional discrimination; report-only, outside the Holm family, no decision changed; already seen: the five-dimensional outcomes, when it and its criterion were specified, before it ran | sec_joint.tex:134, :254 |

**Not done:**
- **The ES (sec_execsummary.tex:6) and the guide (app_guide.tex:6)** were left at first; the director's ruling 3 of
  2026-11-15 updated both (E4 in history-cuts/sec_execsummary.md; I11 above).

## Numbers and keys

`numdiff.py` on the base and new files, comments stripped:
- Removed: "42" (I4's defect list, "seed-42 reference"; the defect stays at sec_systematics.tex:282).
- Added: "2", "3", "5", which are only label, macro and symbol digits: `sec:fived16-pl`, `sec:joint5d-*`, `$C_{\mathrm{PL,5D}}$`, "2D" and "$3\times3$" (the last as printed at sec_joint.tex:254). No value is new.
- Value keys and macros: unchanged.

## Layout

The build of this commit puts the table on pp. 138–141 of main_note.pdf. In it, the lowest table text is at 706.5 pt
and the page number at 741.2 pt, while body pages 21–130 have a median lowest-word bottom of 713.5 pt. No row reaches
the footer: the footer intrusion the recheck saw on p. 139 is gone, because I5 removed a row and I4 and I7 shortened
two. The rendered pages were also checked by eye (pdftoppm -r 60, pp. 138–141).

## Meaning read (codex-school gpt-6.1-sol, high, read-only; the body passages each row restates attached)

- **Pass 1:** OVERALL FAIL on I1 only. D11's dash made "a dash means the note does not state it" false, because
  sec_fived16.tex:110 states that C_model was adopted unscaled after the route's first two tests. All other rows
  passed; every removed or shortened item was LEDGER. reads/app_devhistory-pass1.txt.
- **Pass 2, D11's cell filled (I9), each of the five remaining dashes checked against the body:** OVERALL PASS, with
  no FAILs. None of the five rows' body passages states what had been seen when the change was made; no NEEDED item
  lost. reads/app_devhistory-pass2.txt.

**Meaning read of the rulings (codex-school gpt-6.1-sol, high, read-only; rows E3, E4, T9, I10, I11 together, records attached):** pass 1 FAIL on E3 only (its first wording listed the seed-shift scale, which sec_5d.tex:344 assigns to the companion covariances); pass 2, E3 revised, OVERALL PASS with no FAILs and no NEEDED item lost. reads/rulings-pass1.txt, reads/rulings-pass2.txt.
