# History restructure, §3 (sec_method.tex): cut log

**Under** DECISION-20261113-joseph-note-n4-n5-role.md, the addendum recording Joseph's go of 2026-11-13 for the
note-history restructure.

**The rule:** history stays in the note only if removing it would change a reader's understanding of the reported
object, its reproducibility, its evidential independence or its limitations. Everything else goes to the ledger. Each
"fixed before" names its object, and "declared" alone is replaced.

**Referee:** codex-school gpt-6.1-sol, style only, at 4836da13. For §3 it gave "20–30 %, compress, chiefly §3.2", and
named two passages: its items 1 and 2.

**Base:** `docs/analysis-note/sec_method.tex` at `62cea568dd1377fb49b1070faf71a522180237da`. Line numbers below are the
base's. Every removed passage stays in the commit history at that sha and line, which is its ledger home, and the
records its source comments cite stay where they are.

**Outcome for §3:** one change, C6. Five other proposed compressions, C1–C5, were reverted after the meaning read
(below). Each would have removed a fact the rule keeps, on reproducibility or limitations. §3's remaining history is
disclosure, reproducibility identity or applicability, and it stays.

## The change made

| id | base line | old text | new text | ledger home |
|---|---|---|---|---|
| C6 | :103 | "The exact-split central value was the quoted 2D central value until 2026-10-11; studies labeled \emph{exact-split} use it and have not been recomputed." | "Studies labeled \emph{exact-split} use that cross-check, an earlier quoted 2D central value, and have not been repeated for the quoted estimator." (referee item 2: the applicability disclosure stays, the calendar date goes) | 62cea568d:sec_method.tex:103; docs/publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md (cited at :111) |

## Proposed and reverted (the meaning read's FAIL; the text stays as at base)

| id | base line | proposed | why it was reverted (meaning read, first pass) |
|---|---|---|---|
| C1 | :48 | "Two regenerations, with one driver and one input and differing only in the seed, reproduce … to $\lesssim2\times10^{-11}$, so the difference is attributable to the seed." → "Matched reruns attribute this difference to the training seed." (referee item 1) | It drops the controls ("one driver and one input … only in the seed") and the tolerance that establish the attribution's reproducibility. |
| C2 | :48 | Join the two reproduction sentences, with "from its recorded run configuration" | Recording a run's configuration and reproducing from that record are different claims, so the join strengthened the provenance. |
| C3 | :48 | "the cheaper of the two costed ways …" → "the cheaper way …" | It drops that exactly two costed ways were compared, and what was costed. |
| C4 | :79 | Cut "The reseeded run's median agrees … but the agreement is coincidental." | Both 0.18 % medians still print, so cutting it loses a limitation on reading their agreement as corroboration. |
| C5 | :100 | Cut configuration (e)'s "It was selected before the joint-test design was fixed" as a repeat of :150 | It is not a repeat. Its subject is the joint-test estimator; :150's is the refinement classifier. |

**Kept as they are, because each is a disclosure, reproducibility identity or applicability qualifier the rule keeps:**
- "LightGBM was chosen for the central value after both comparisons with the publication were known, so that the
  central value and its covariance share an estimator." (:79)
- "The change was decided on that closure test, before the rebuilt result's distance from the published result was
  computed, and the rebuilt result was adopted after that distance was known." (:103)
- "…they were produced before the purity bias was found and the refinement was developed." (:103)
- The exact-split paragraph's "Its seed was not fixed, and its run log was not found" (:79).
- The iteration paragraph's "That is the movement of that diagnostic for that cross-check" (:160).

**Not changed:** "fixed \emph{a priori}" (:150) is not "fixed before" with an unnamed object, but it does not say
before what. Naming the object needs a record I have not read, so it goes to the director. No "declared" occurs in §3's
printed text.

**Numbers and keys:** `numdiff.py` on the base and new files, comments stripped:
- Removed: only the date 2026-10-11, in C6.
- Added: none.
- Value keys and macros: unchanged.

## Under ruling (A), 2026-11-14 (row C7)

| id | base line (4a997b89d) | old text | new text | ledger home |
|---|---|---|---|---|
| C7 | :192 | "every event in the declared truth sample enters" | "every event in the specified truth sample enters" (a method use: no timing) | 4a997b89d:sec_method.tex:192 |

**Still not changed: :150's "fixed \emph{a priori}".** A record that the classifiers' settings were fixed before
any training would let it name its object. The search found none: `git grep -i 'fixed a priori|no hyperparameter
search|hyperparameters.*before'` over docs/orchestration and docs/*.md finds only other studies' seeds and the
paper's own sentence. By the director's ruling it stays, and it is listed as open in UNRELEASED-SUPPORT.md.

## The Development-history appendix (App.~\ref{app:devhistory}, `app_devhistory.tex`)

**New, placed last** so that no other appendix letter moves. It has the referee's six columns:

| row | from | content |
|---|---|---|
| D1 | :79, :103 | exact-split (b): an earlier quoted 2D central value, replaced by LightGBM. Studies labeled exact-split are not repeated. Both comparisons with the publication had been seen. |
| D2 | :103, Table 4 | purity-subtracted 2D central value and covariance (a), rebuilt with (f) after the 2D closure test with backgrounds. The purity-subtracted 2D comparisons use (a). Decided before the distance was computed, and adopted after it was known. The first pass said "Kept only for the purity-subtracted comparisons", which the read failed as unsupported exclusivity; it is reworded to Table 4's own statement. |
| D3 | :103 | the 5D central value and five-axis covariance, configuration (a): not rebuilt, and produced before the purity bias was found. |

Each row restates the body and adds no claim. The guide to the appendices gains one clause pointing to it.

## Disclosure checklist (the director's list, plus any found here)

| disclosure | in §3? | survives |
|---|---|---|
| the 2D adoption after the published distance was known | yes, :79 and :103 | ✓ both sentences unchanged, and in D1 and D2 |
| the post-observation run-period term | no (§4, §10) | — |
| reused samples and seeds | no (§9, §11) | — |
| the invalid q3 deformation | no (§9) | — |
| the stopped coverage tests | no (§5, §9, §10) | — |
| the data-informed joint-test design and budget extension | no (§11). §3's two "selected before the joint-test design was fixed" sentences (:100, :150) stay | ✓ |
| the missing response uncertainty | no (§10) | — |
| the generator-sample problems | no (§10, App. C) | — |
| the target-correction sensitivity | no (§11) | — |
| also found: the 5D central value predates the purity bias | yes, :103 | ✓ unchanged, and in D3 |

## Statements whose only support is an unreleased record

- **:48** "…reproduces it to $1.4\times10^{-11}$, and so does a regeneration whose run configuration is recorded
  (Ref.~[34], 2d-central-value)". Ref. [34] is NoteRecords2026, "Internal record of the MINERvA-OmniFold repository, not
  posted" (technote.bib:1014-1019). This is the referee's Ref. [34].
- **:15 (§3.1)**, the configuration-(e) effective-sample-size sentence: it cites `UnfoldedWeightsESS2026` (Ref. [31]).
  Whether that record is released is for the director to check. It is not changed here.

## Meaning read (codex-school, gpt-6.1-sol, high, read-only; the old and new section, this log and the appendix)

- **First pass, on C1–C6 and D1–D3:** OVERALL FAIL (C1, C2, C3, C4, C5, D2). C6, D1 and D3 passed, and no
  after-results disclosure disappeared. Its reasons are in the reverted table above. All five C rows were reverted and
  D2 was reworded.
- **Second pass, on the revised section:** OVERALL PASS. C6, C1–C5 reverted (the printed text is identical outside C6), D1–D3 supported, and no disclosure lost.
- Both passes' prompts and answers: `history-cuts/reads/sec_method-pass1.txt` and `-pass2.txt`.
