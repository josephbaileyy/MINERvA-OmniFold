# E2: the note's sentences that rest only on unreleased records (2026-11-16)

**Under** DECISION-20261116-joseph-paper-batch.md item 7 (PR #1181).
- Current-result support, plus a compact timestamped decisions record, goes into the deposit.
- The superseded history is shortened, not deposited.
- The release-status narration is replaced by the deposit identifier, filled at the freeze.
- "a priori" becomes "No hyperparameter search was performed on data."

**The inventory:** `UNRELEASED-SUPPORT.md` (this directory), re-measured at branch base 1a112e277. That gives 34 sites: the 33 listed, plus `app_devhistory.tex:32`, a table row added since. Two release-narration sites with no citation are added: `sec_summary.tex:38` and the preservation sentence at `app_release.tex:54`.

**Categories** (the codex-school referee's, `abref/out.txt` E2):
- **(a)** current-result support: kept, record deposited;
- **(b)** timing, stopping, repair or provenance supporting current results: kept, record deposited as part of the decisions record;
- **(c)** superseded diagnostics or history: cut or shortened;
- **(d)** release-status narration: replaced by the deposit hold;
- **(e)** the unsupported "a priori".

**How the deposit is cited.** No sentence's citation key changes.
- Each repository record's bibliography entry now begins "Designated for inclusion in the Zenodo reproduction package, DOI **[Zenodo DOI pending deposit]**". This is the same hold the release appendix already prints for the DOI, so one replacement at the freeze fills every site. The entries are:
  - in technote.bib: UnfoldedWeightsESS2026, TwoDFollowup2026, ReleaseCandidate2026 and AnaTuplePreservation2026;
  - in publication.bib: JointTestRecord2026, JointTestKappa2026, JointTestRecovery2026, JointTestProjections2026 and JointTestRecoil2026.
- NoteRecords2026's "not posted" becomes "The entries cited in the analysis note are designated for inclusion in the Zenodo reproduction package, DOI [hold]". The deposit holds the cited entries, not the whole records document; see the deposit list below.

| # | site (at 1a112e277) | record | cat. | action |
|---|---|---|---|---|
| 1 | app_devhistory.tex:8 | [34] | b | kept; chronology of App. I's rows |
| 2 | app_devhistory.tex:32 | TwoDFollowup2026 | a | kept; the earlier 2D budget's defects, printed as the comparison of §uq-2d-scope |
| 3 | app_guide.tex:8 | [34] | a | reworded: "kept in the analysis's records document … and the entries cited are designated for inclusion in the Zenodo reproduction package" |
| 4 | app_negweight.tex:8 | [34] negweight-hpss | b | kept; a provenance limit |
| 5 | app_negweight.tex:122 | [34] bkg-mode-elimination | b | kept; provenance of the endpoint unfolds' mode |
| 6 | app_negweight.tex:126 | [34] oi6-oi8-oi126 | a | kept |
| 7 | app_negweight.tex:145 | [34] fps-battery | a | kept |
| 8 | app_release.tex:9 | ReleaseCandidate2026 | d | "Release status. RC7, a local release candidate …, has not been deposited or released under a publication tag." becomes "RC7. RC7 is a replay package with a README, SHA-256 checksums and a replay verifier." The status is now the Zenodo paragraph's DOI hold |
| 9 | app_release.tex:51 | JointTestKappa2026 | a | kept |
| 10 | app_release.tex:54 | AnaTuplePreservation2026 | a, d | checksum sentence kept. In the preservation sentence (Joseph: data preservation kept "for now"), only the clause the deposit makes false changes: "Neither the checksums nor the preservation copies are a public deposit" becomes "The preservation copies are not a public deposit, and neither they nor the checksums make …" |
| 11 | app_release.tex:61 | [34] identities already fixed | a | kept |
| 12 | app_statmethods.tex:362 | [34] superseded values | c | **cut**: "Nor is the exact-split cross-check's 1.47, computed with an earlier covariance …, evidence against them on its own." Limit (ii) stands on the quoted value. The exact-split values stay in the records (app_history.tex). Ledger L-thin-C22 → DROP |
| 13 | app_statmethods.tex:458 | [34] superseded values: retired material | c | **shortened**: "A split bootstrap of the earlier rebuilt bootstrap … separated the first two from an MC-statistics omission but not from the third, and it has not been repeated for the quoted statistical block." becomes "The split-bootstrap diagnostic used on the earlier rebuilt bootstrap has not been repeated for the quoted statistical block." (the meaning read's fix of a first form, "No test … separates these candidates", which overstated the absence) Ledger L-thin-C23 → DROP |
| 14 | app_statmethods.tex:565 | [34] superseded values: retired material | b | kept; the ML floor in force when the closure tests were graded |
| 15 | app_statmethods.tex:650 | [34] coverage-toys | c | **kept** (see "Unsure" below); the same-ensemble pull diagnostic, which the history restructure moved here (V2) |
| 16 | app_statmethods_nd.tex:12 | [34] rank-inversion | a | kept |
| 17 | sec_3d.tex:133 | [34] flux-repair | a | kept |
| 18 | sec_5d.tex:90 | [34] response-diagnostic | a | kept |
| 19 | sec_5d.tex:294 | [34] identities already fixed | a | kept |
| 20 | sec_5d.tex:360 | [34] z-cv-record | a | kept |
| 21 | sec_eavailw.tex:70 | [34] mp5-truth-axis | a | kept |
| 22 | sec_joint.tex:5 | JointTestRecord2026 | b | kept; the joint tests' specification and decisions |
| 23 | sec_joint.tex:224 | JointTestKappa2026 | a | kept |
| 24 | sec_joint.tex:239 | JointTestRecovery2026 | b | kept; the procedure fixed before the rerun |
| 25 | sec_joint.tex:254 | JointTestProjections2026 | a | kept |
| 26 | sec_joint.tex:289 | JointTestRecoil2026 | a | kept |
| 27 | sec_method.tex:15 | UnfoldedWeightsESS2026 | a | kept |
| 28 | sec_method.tex:48 | [34] 2d-central-value | b | kept; a provenance gap |
| 29 | sec_systematics.tex:121 | [34] july-sweep | a | kept |
| 30 | sec_systematics.tex:143 | [34] flux-index | a | kept |
| 31 | sec_systematics.tex:282 | TwoDFollowup2026 | a | kept |
| 32 | sec_systematics.tex:332 | [34] superseded values | a | kept; a bound on the current background-CV choice (see "Unsure") |
| 33 | sec_validation.tex:46 | TwoDFollowup2026 | a | kept |
| 34 | sec_validation.tex:137 | [34] coverage-fixed-truth | b | kept; the design specified before any toy |
| 35 | sec_summary.tex:38 | none | d | "A local release candidate exists, with checksums and a verifier …; **no release has been tagged or deposited**." becomes "App. \ref{app:release} describes the replay package, with its checksums and a verifier that recomputes and checks its results, and the Zenodo reproduction package (DOI [hold])." |
| 36 | sec_method.tex:150 | none | e | "The settings of the two OmniFold classifiers and the missed-event regressor were fixed *a priori*. No hyperparameter search was performed on data." becomes "No hyperparameter search for the two OmniFold classifiers or the missed-event regressor was performed on data." |

**Counts:** (a) 22, (b) 8, (c) 3 (2 changed, 1 kept), (d) 2, plus the shared row 10, (e) 1. In all, 36 rows, 5 of them changed text, plus the bibliography holds.

## The deposit list (filled at the freeze)

- **NoteRecords2026 entries cited by kept sentences:**
  - negweight-hpss, bkg-mode-elimination, oi6-oi8-oi126, fps-battery;
  - rank-inversion, flux-repair, response-diagnostic, z-cv-record, mp5-truth-axis;
  - 2d-central-value, july-sweep, flux-index, coverage-fixed-truth, coverage-toys;
  - the headings "identities already fixed", "superseded values" (row 32 only) and "superseded values: retired material" (row 14 only).
- **Repository records:** the nine bibliography entries above.
- **The compact timestamped decisions record** (rows of category b). The cited records already serve as it: JointTestRecord2026, JointTestRecovery2026 and the NoteRecords2026 entries of rows 1, 4, 5, 14, 28 and 34. A separate compiled record, if Joseph wants one, is a freeze item.

## Unsure (for the director)

- **Row 15.** The same-ensemble pull diagnostic is a superseded diagnostic (category c). The restructure kept it whole in the appendix. Cutting it is a larger cut than E2's sites, so it is kept, with its record deposited.
- **Row 32.** The bound on the background-CV choice is current support, but its record sits under the records' "superseded values" heading. That one entry must be deposited, or the sentence cut.
- **Row 14.** "The floor in force when the tests were graded" is kept as provenance. Its record is under "superseded values: retired material".
- **Row 10.** This is data preservation text. Only the clause about the checksums changed.
