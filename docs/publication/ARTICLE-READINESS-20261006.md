# Readiness of the PRD article, assessed separately (2026-10-06)

> **Current status (pointer added 2026-10-08; this record's text below is unchanged).** §5 is this record's latest
> state; the earlier sections are superseded where they disagree with it. Since §5:
> - the PR to main (`4b21cef6`, PR #29) and the standalone note sync are done, and the submission package is
>   assembled, per `submission/PACKAGE-MANIFEST-20261006.md` §1;
> - the 2D paragraph (`d31cdbb0`) and the `\uqPaper` fix (`8a50498a`) are on main, so the article has one `\pubhold`,
>   the deposit identifier;
> - Joseph approved package inputs 1–2 (the AI-use disclosure and the author details) in the last addendum of
>   `DECISION-20261006-joseph-publication-approvals.md`. The disclosure enters the article in the next paper pass,
>   which has not happened.
>
> - **2026-10-07, paper-completion pass** (`REVIEW-20261007-paper-completion.md`):
>   - the disclosure and author metadata are in the article;
>   - the joint-test conditions are scoped to the calibration model: the sub-fine residual is "unmeasured,
>     potentially material", and the ±4% is data-side only;
>   - the abstract and introduction are rewritten;
>   - one fresh review, two cycles, READY WITH CHANGES, all applied.
>
>   One scientific decision is open (that record's §5: accept as conditional, or authorize a report-only
>   κ-breakdown).
>
> What remains is package inputs 3–6: coauthor review, the deposit, the tag and submission, and the cover-letter
> specifics. Each needs Joseph's separate authorization.

**CITABLE FOR:**
- this article's readiness state against the paper-wide completion table
  (`CAMPAIGN-s5c-20260924-paper-wide-table.md`, main `9984a5fd`), row by row for the rows the article retains;
- what this lane re-measured;
- what remains, and who owns it.

**NOT CITABLE FOR:** s5p's `publication_readiness`, which stays NOT READY as recorded. Joseph's item 1 says
"Assess this article's readiness separately".

**Article state:**
- Branch `docs/publication-decision-20261005` at `90727b17` (or later); `build_all.sh` PASS, article 8 pp.
- Two `\pubhold` remain: the 2D-uncertainty paragraph (VL170 rebuild) and the deposit identifier.

## 1. Rows the article retains

| row | article content | paper-wide status (09-25, reconciled 10-06) | re-measured for the article | remaining for the article |
|---|---|---|---|---|
| R1 2D reproduction | Validation §, Fig. 1 | OPEN: operands untracked on purgeable scratch; no package object | unchanged | **package 2D operands with digests** (release) |
| R2 2D uncertainty | 6.87% median, coverage text | OPEN | **superseded:** VL170 adopted (Joseph, `af24a101`); the rollup is pending from the 2D lane | the 2D lane's rollup → update the paragraph |
| R3 Fig. 1 | Fig. 1 | OPEN: no figure digest or producing run | unchanged | figure digests and producing run (release) |
| R4/R5 3D, low-E_avail, 2p2h | Central-values § | OPEN: E_avail-definition OIs (`OI-30`/`OI-31`); prediction digests | R21-7 (Tune v1 in the low-E_avail set) is consistent: VL159 is the 3D comparison and includes Tune v1 | prediction digests (release); the `OI-30`/`OI-31` dispositions are owner items |
| R8 Ascencio "within 10%" | Central-values § | OPEN: CV level; the Ascencio file digest is not in the ledger | the article quotes only "within 10%" and no χ² | Ascencio digest in the release |
| R9 5D central value | Validation § | OPEN: per-object provenance | unchanged | release provenance |
| R10 localization map | Fig. 2 (descriptive) | OPEN: (a) comparator label; (b) response-mismatch closure not run; (c) R15 | **(a) fixed** (the caption names Tune v1). **(b) still not run** (`app_response_mismatch.tex:47-48`). The article states that the localization is descriptive and sits where the regularization bias is largest. | **(b) needs either the diagnostic or a recorded scope decision that the descriptive claim stands without it: a decision for Joseph (batch item A).** Comparator array in the release. |
| R11 Fig. 3 generator band | Fig. 3 | OPEN: prediction digests; GENIE-CV total mismatch | **(a) resolved:** the repaired GENIE-CV total is 2.76e-38 in both 3D and 5D (VL157; `sec_3d.tex:260-262`). The s5p reproduction harness regenerates the generator figures (tier B). | prediction files with version, config, flux and sha256 in the release |
| R12–R14 adopted covariance, seed statement | Uncertainty-status § | OPEN | R14(a) qualifier **present** ("products distinct from the adopted bytes") | none for the article text |
| R15 hadronic response | Detector-response condition | BLOCKED-EXTERNAL (question unsent) | Joseph **deferred** sending it (item 5). Under the PM-1 ruling, silence does not block. The article states the condition and the W2 sensitivity. | none |
| R16 joint inference | §VI, Table I, Fig. 4 | **closure met** (s5p delivery) | the article quotes the Stage-7 wording | none |
| R18 PET | one sentence | — | checked by both PET lanes | none |
| R20 release | Data availability | OPEN | **RC1 replays the joint tests, the recovery and W1 from an empty directory** (receipt `b2a54aa5`) | (i) extend the release to the article's other retained figures and numbers (Figs. 1–3; R1, R8–R11 operands); (ii) archive the ~2.3 GB of `/pscratch` products before purge; (iii) deposit and tag (separately authorized) |
| R21 consistency, builds, sync | all | OPEN: nine defects | of the nine: **1 fixed** (comparator); **2 fixed** in the article (versions stated); **6 fixed** (qualifier); **7 consistent**; **8 resolved** (repair); **3, 4, 5, 9** are note-side (`app_release`, `sec_eavailw`), owned by the note owners and not in the article | the article's own sync to the standalone repo (after the final review); note-side items go to the note owners |

## 2. Verdict

**NOT YET READY to request submission.** The scientific content is complete except the 2D-uncertainty update.

**Remaining before the submission package:**
1. The 2D lane's VL170 rollup, then the 2D paragraph (in progress).
2. **Release coverage of Figs. 1–3** and their numbers: operands, prediction files and comparator, each with a
   digest, plus a regeneration test. This is packaging under item 6. No compute allocation is needed, and the s5p
   harness already covers the generator figures.
3. **Archive the `/pscratch` products** that the deeper reproduction level needs (the s5p delivery §6 lists
   ~2.3 GB) before purge. This is a storage decision with an owner (see batch item B).
4. **R10(b):** a scope decision for the descriptive localization (batch item A).
5. One fresh independent review of the frozen article, claim table and release (PLAN §7).
6. The standalone note-repo sync of the article; coauthor review; then Joseph's separately authorized acts.

## 3. Updates after this assessment (2026-10-06)

- **2D paragraph:** done (`d31cdbb0`), from VL170/VL172. The article now has only the deposit-identifier hold.
- **Figs. 1–3 release:** covered on branch `release/article-figures-20261006` (`e2bcca33`). Every quoted number
  reproduces except `\uqPaper`, which is printed 6.86 and computed 6.8525. The 2D lane agrees it should be 6.85
  (CSV-rounding artefact). Its fix, `8a50498a`, is unpushed and awaits Joseph's ruling in its session. The
  article uses the macro and will print 6.85 after the merge.
- **Not yet covered by the figures release:** the VL161 E_ν ≥ 20 GeV shares (they need per-E_ν predictions) and
  R8 (Ascencio). Both are listed for RC2 or as release gaps.

## 4. After the final review's cycle 1 (2026-10-06)

- **Final review cycle 1:** NOT READY (3 blocking, 10 should-fix, 9 notes). Everything was repaired at `f81120be`.
  See `REVIEW-20261006-final-article.md`.
- **RC3:** tarball `7999d0940ce7206925733ed3f2580348f603e1157509927fd99c1bba7638de09` (18 files). `verify_rc.py`
  gives PASS: the joint tests, the recovery (a), W1, the Figs. 1–3 quoted numbers against `values.tex`, the
  regeneration of Figs. 1–3, and the regeneration of Fig. 4 (6.5 min wall time).
- **Product archive: DONE** by the s5p lane under Joseph's authorization ("CFS copy + manifest").
  - Location: `/global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006/`.
  - Contents: 10,612 files, 2,317,487,385 bytes.
  - The SHA256SUMS digest is `1a72cb43…`, verified by this lane on main `275b996d`.
  - Batch item B is resolved.
- **Still open:**
  - R10(b): the descriptive localization without a response-mismatch closure. This is batch item A for Joseph. The
    article now states the claim descriptively, says no closure has been run, and has removed it from the abstract.
  - The final review's cycle 2.
  - PR and merge, then the 2D lane's one standalone sync.
  - Coauthor review; Joseph's separately authorized acts.

## 5. After the final review (2026-10-06)

- **Final review:** cycle 2 READY WITH CHANGES, applied (`f5787b32`). RC4 `46f801bf…` gives VERIFY PASS.
- **R10(b):** Joseph ruled that the Fig. 2 statement "Stands as written" (DECISION-20261006 addendum).
- **No open scientific or provenance item remains for the article.** Next:
  1. PR to main; the 2D lane's single standalone sync;
  2. coauthor review (an external act; Joseph);
  3. the submission package;
  4. the deposit, tag and submission, which are separately authorized.
