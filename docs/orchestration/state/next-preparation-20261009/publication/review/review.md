# Independent review: keep-and-disclose correction, `5ac9706a..2b4dc8ff`

Reviewer: read-only and independent (did not author the work). Only commits up to `2b4dc8ff` were reviewed.

## 1. Setup

- Worktree: `git worktree add --detach .../scratchpad/reviewer/wt 2b4dc8ff`. HEAD was `2b4dc8ffbe7b8d0627a9848d6e5b50d9b8c0a6b6`. `git status --porcelain` was empty at the start (0 lines) and at the end (0 lines). Removed with `git worktree remove`, and `worktree list` no longer shows it.
- Commands used: `git diff [--word-diff] 5ac9706a 2b4dc8ff`, `git diff --stat`, `git show d1bc8813:<driver|launcher|helper>`, `git log -S/-G` (to trace the 0.28 % figure), and `grep` sweeps of `docs/analysis-note/*.tex` (excluding `archive/`).
- Rendered checks: `pdftotext` (with and without `-layout`) on the supplied PDFs (sha256 prefixes 50dfc6c6 note, d9cc50fd paper, 0b85c7da primer) and on the 5ac9706a baseline PDFs, followed by a per-page word count and a word-multiset diff.
- My own script (`reviewer/check_numbers.py`) reads `rc_pairing.json.txt`, `a/verification.md` and `a/pairings.tsv`. The 2D ROOT products are not on this machine, and cluster access is out of scope. Numbers were therefore checked against two independent sources, the A tables and the earlier reviewer's JSON. They were not recomputed from the ROOT products.
- Nothing was edited, committed or messaged. The only files written are in `reviewer/` (`txt/`, `check_numbers.py`, this file).

## 2. Findings

No MATERIAL defect was found. Findings in order of severity:

**F1 (MINOR): the note's abstract still says "reproduces … uncertainty scale" with no qualification.** `main_note.tex:47-49`: "reproduces the published double-differential cross section … including its spectrum and uncertainty scale." The same construction is now qualified in `sec_summary.tex:7-9` and in the executive summary (`sec_execsummary.tex:26`), but not in the note's most-read sentence. `main_note.tex` is not in the diff. To resolve: add a short qualifier (LightGBM ensembles; transfer unmeasured), or point to §3.2.

**F2 (MINOR): the newly added 6.83 % reads like the systematic-block entry 6.830 % printed directly beside it.**
- `sec_results.tex:143-146` and `app_statmethods.tex:432-434` add "against the quoted exact-split central value the same combined covariance gives 6.83 %".
- The tables right below or above them print the *systematic block* median as 6.830 % (`sec_results.tex:159`, `app_statmethods.tex:418`), with CV42 as the denominator.
- Those are two different objects (combined covariance over E_C, against universe block over CV42) that agree at the printed precision.
- The 6.83 % itself is correct: P14 gives 6.8269, and the earlier reviewer's JSON gives `blocksum_median_rel_pct_den_exact_central` 6.8269.
- To resolve: print 6.827 %, or name the object at the table, so a reader cannot read the new number as the table row.

**F3 (MINOR): "Both combined entries … They divide by …" also covers an absolute entry.** `app_statmethods.tex:431-432`. The two combined entries are √Tr C (3.220e-39, an absolute value) and 6.871 %. Only the per-bin median is a ratio. To resolve: "The relative entries divide by …".

**F4 (MINOR): a sentence predating the correction still implies backend equivalence from an integrated quantity.**
- `app_statmethods.tex:1031-1033`: "Changing the GBDT backend … (Σσ within 0.1 %) shifts paper-cov χ² by ∼1 unit *with little central-value change*."
- The correction now states, correctly, that the backend difference is a 0.97 % per-bin median, or 1.3 σ_stat, carried by no block. The pairing tables also count 126/205 bins above 1 σ_S.
- Ruling item (3) says not to imply that a small integrated difference proves equivalence. This sentence does exactly that, and the correction's sweep did not catch it.
- To resolve: replace "with little central-value change" with the measured per-bin statement (seed 1 vs exact), or cite §3.2.

**F5 (MINOR): the claims register calls the disclosure "now complete", but the article omits the seed provenance.**
- `CLAIMS-20261005-claim-to-evidence.md` §H row L4 says "DEMONSTRATED disclosure, now complete" and lists `random_state=None` among the disclosed facts.
- The paper (`paper_body.tex:116-130, 177-190`) never says that the 2D central's seed was unpinned, or that the exact-split estimator's own seed noise is unmeasured (P09b). It says only that the training-seed ensemble is LightGBM. The note does say both (`sec_method.tex:110-113`, `sec_systematics.tex:98-99`).
- The paper makes no false seed claim, so the ruling's mandatory items are met. The register's "complete" overstates what the article itself carries.
- To resolve: scope L4 to "the note", or add one clause to the paper.

**F6 (NOTE): the paper never names the denominator of its 6.87 %.**
- `paper_body.tex:180-181` and the Fig. 1 caption (`paper_body.tex:171-172`, "independently reconstructed … median relative uncertainties") quote 6.87 % with no denominator.
- 6.87 % is relative to the LightGBM seed-42 central, which the paper never quotes; against the quoted central it is 6.83 %.
- The closeout §4 marked this as optional, and the paper's new sentences do disclose the estimator split. Recorded for the owner; it does not block.

**F7 (NOTE): the note asserts the evidence class of P01 as fact.**
- `sec_method.tex:110-112` says the central's "production launcher passed no seed, and the driver revision it ran had no seed option, so scikit-learn's `random_state` was `None`."
- P01 is VERIFIED from the revision of record plus a wall-time signature. Its runtime origin is UNAVAILABLE: the job 53116554 log was not found, and the helper was imported from the canonical `/pscratch` checkout, whose bytes were not recorded.
- I checked `d1bc8813`:
  - the driver has no `random_state`, `seed` or `estimator`;
  - the launcher passes `--iters 5 --use-weights` and paths only;
  - the helper builds `GradientBoostingClassifier(**{})`;
  - the helper's backend switch first appears in `baa0a76f` on 2026-05-19 14:38, after the run ended at 08:15.
- So the committed history supports the sentence. The caveat about executed bytes survives only in a source comment (`sec_method.tex:116-118`). A rendered "according to the revision of record (the run log was not found)" would match the evidence class exactly.

**F8 (NOTE): a source comment that predates the correction contradicts P01.** `sec_method.tex:85-86`, a comment that is not rendered: "the production launcher passes no `--estimator` flag and therefore takes the driver's default." At `d1bc8813` the driver had no such option at all. The new comment at line 118 already gets this right. To resolve: align line 85 with it.

**F9 (NOTE): the cross-seed block sum (P07) is not disclosed.**
- `app_statmethods.tex:394-396` says the three Monte Carlos are "independent by construction", and "training-seed trials vary that seed".
- The blocks use seed 1 (statistics), seed 42 (systematics) and seeds 1–10 (ML). P07 records that summing seed-1 statistics with seed-42 systematics is UNRESOLVED at the covariance level. The correction lists the seeds (`sec_method.tex:113-115`) but does not say this.
- This is outside the ruling's mandatory items, and the general "transfer unmeasured" statement does not cover it.

**F10 (NOTE): KNOWN_ISSUES row 88 has two cosmetic problems.**
- Its status cell (`KNOWN_ISSUES.md:78`) states "interim disposition: keep and disclose" twice: once in the bold header, once as the sentence "Interim disposition 2026-10-09 (Joseph)".
- The description cell, which predates the correction, says "The centrals differ by a median 0.97 %" without naming *which* LightGBM central (seed 1). The note, the paper and CLAIMS §H all name it.
- The row is OPEN and does not claim readiness, as required.

**F11 (NOTE): primer wording.** `primer_body.tex:154-156` calls LightGBM "a second, faster version" of the tree learner; it is a different implementation and algorithm (histogram splits), not a version. This is acceptable for the primer's register, and the substance is correct: about 1 % in a typical cell, transfer unmeasured, "not known to be wrong". The sentence "the main cause was found and removed" (`:165`) matches the paper's existing `paper_body.tex:193-195`.

**Ruling items checked and found satisfied (not findings):**
- (1) The established estimator difference is kept distinct from the unmeasured transfer. "Not a demonstration that the quoted uncertainty is wrong" (`sec_method.tex:95-96`) matches ASSESSMENT §8.
- (2) The "pinned seeds" sentence is replaced against P01 (`d1bc8813`), not against later driver defaults.
- (3) 0.97 % / 1.3 is labelled as LightGBM seed 1 vs exact, with σ = per-bin SD of the statistical (VL170) block. It is not attributed to seed 42. No integrated ratio is quoted.
- (4) The KI-85 diagnostic is described as same-event pseudo-data, "neither an independent-population coverage test nor a real-data calibration" (`paper_body.tex:203-208`). This matches the KI-85 row: "faithful on same-event pseudo-data … does not show that the band is calibrated for real data".
- (5) KI-88 is OPEN and records the interim disposition. PACKAGE-MANIFEST supersedes §2's "No scientific or provenance item remains open", and CLAIMS §H says "Not publication-ready".

**Removed 0.28 % sentence (`sec_systematics.tex`, base line 89-90): removing it was justified.**
- The sentence named no operand, and I could not trace it to any 2D product. Its earliest occurrence I found is `1ace91c3` (2026-06-04, prepublication index: "ensemble-mean CV (NTRIAL) shown to agree at 0.28%"); `AUDIT-FINDINGS-20260728.md:603` attributes it to the exact GBT being nearly deterministic.
- If "production single-run CV" means E_C, the measured per-bin median for the 10-seed LightGBM mean vs E_C is 0.99 % (5.15 σ_ML), which contradicts it. The integrated ratio (0.9999) does not match 0.28 % either.
- The replacement number is supported. The source comment (`sec_systematics.tex:100-104`) records the removal honestly.

**Scope (`git diff --stat`): no out-of-scope changes.**
- 17 files: 10 under `docs/analysis-note/`, `KNOWN_ISSUES.md` (row 88 only), CLAIMS §H, the PACKAGE-MANIFEST note, CATALOG (+1 row), MANIFEST-overrides (+1 row), the regenerated MANIFEST.tsv (the new row plus inbound/consumer columns on 4 rows), and `publication/REPORT.md` (§0 only).
- No change to `values.tex`, figures, receipts, audits or `publication/release/preservation/`.
- No printed number, band, adoption or gate changed. No LightGBM re-quote, transfer measurement, N2 or KI-85 lift is claimed.

**Rendering: no defects.**
- No "??" in any of the three PDFs, new or base.
- Page counts are unchanged (note 123, paper 11, primer 9).
- Every changed passage renders as written, with its references resolving: "§3.2" (`sec:method-config`), "§4.3", "Sec. III", "Sec. IV".
- A word-multiset diff against the base shows only the intended removals and line-break hyphenation splits. The paper text that pdftotext reordered after a float move ("response-mismatch closure", "integrated data-to-prediction", "weight-based detector bands") is present exactly once in both PDFs.
- Paper page word counts shift by at most about 90 words per page through float reflow. I saw no evidence of an empty or overfull page.

## 3. Numbers

Verdict key: OK = matches its evidence after rounding to the printed precision.

| claim (file) | source | my read (own script) | verdict |
|---|---|---|---|
| 0.97 % median per-bin \|Δ\|/E_C, LightGBM seed 1 vs exact (note, paper, KI-88, CLAIMS) | P02; verification.md:100; rc "seed1 vs exact" | 0.9660 → 0.97 | OK; the denominator (E_C) is implicit, but "differ from the exact-split" reads correctly |
| max 12.5 % (`sec_method`) | verification.md:100; rc | 12.4969 → 12.5 | OK |
| 1.3 σ, per-bin median, σ = √diag C_S of VL170 (note, paper) | P02; rc `over_sigS` | 1.2995 → 1.3 | OK; denominator named ("statistical (bootstrap) block") |
| 0.99 % median, 10-seed LightGBM mean vs exact (`sec_systematics`) | verification.md:101; rc "seedmean vs exact" | 0.9873 → 0.99 | OK |
| "about five times" σ_ML (`sec_systematics`) | P09a (5.1); verification.md:107 (5.15); rc 5.147 | 5.147 | OK |
| 6.83 % block sum over E_C (`sec_results`, `app_statmethods`, CLAIMS) | P14; rc | 6.8269 → 6.83 | OK (see F2) |
| 6.87 % / 6.871 % over CV42 | P14; verification.md:85; rc | 6.8707 | OK; the denominator is now named in the note |
| seeds 1 (bootstrap), 42 (universes + matched CV), 1–10 (ML) | A §2.1; P02, P04, P08 | as stated | OK |
| `random_state=None`; launcher passed no seed; driver had no seed option | P01; `git show d1bc8813` (driver, launcher, helper) | confirmed in committed bytes | OK; the executed-bytes caveat appears only in a comment (F7) |
| "no exact-split bootstrap, universe sweep or seed scan exists" | A §6; P03, P05, P09b UNRESOLVED | as stated | OK |
| "no block carries this difference" | A §5 item 3 | as stated | OK |
| integrated ratio 0.9999 | `a/logs/check_a_output.txt` (A only) | not quoted anywhere | OK (correctly omitted) |

## 4. Verdict

**PASS WITH CHANGES.**

The paper, note and primer now agree on four points:
- The quoted 2D central is exact-split scikit-learn gradient boosting with an unpinned seed (note). The bootstrap, universe and training-seed ensembles are LightGBM, at seeds 1, 42 and 1–10.
- The estimator difference is stated as established, and the covariance transfer as unmeasured, not as wrong.
- The 0.97 % / 1.3 σ_stat comparison is correctly attributed (seed 1 vs exact, with the VL170 denominator) and is not used to claim equivalence.
- No surface claims that disclosure achieves publication readiness. KNOWN_ISSUES 88 stays open, and CLAIMS and PACKAGE-MANIFEST say the package is not ready.

The "pinned seeds" correction matches P01 and `d1bc8813`. Every added number traces to verified evidence, and the scope is clean.

Changes before calling the surfaces fully consistent:
- **F1:** the note's abstract still says the uncertainty scale is "reproduced" without the qualifier.
- **F4:** `app_statmethods.tex:1033` ("little central-value change") still implies backend equivalence.
- **F2, F3:** wording that invites confusing or misreading the denominators.
- **F5:** CLAIMS §H "now complete" overstates what the article itself discloses about seed provenance.

None of these changes a number or requires new evidence.

## 5. Resources

- Wall time: about 9 minutes of tool time (13:15–13:24 PDT), plus reading.
- CPU: well under 0.01 core-hour (git, grep, pdftotext, one small Python script; at most 1 thread per command).
- Disk: a temporary worktree (removed) and about 3 MB of text extracts in `reviewer/txt/`.
- No cluster, GPU, training or event loops.
