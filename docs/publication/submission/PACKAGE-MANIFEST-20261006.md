# Submission package: manifest and remaining author inputs (2026-10-06)

**Status:** the package is assembled for Joseph's review. **Nothing has been submitted, deposited, tagged or sent.**
Those acts, and any message to coauthors, need Joseph's separate authorization (DECISION-20261006 item 6).

## 1. Exact versions

| component | identity |
|---|---|
| article sources | `docs/analysis-note/main_paper.tex`, `paper_body.tex`, `values.tex`, `values_inference.tex`, `publication.bib`, `technote.bib`, `figures/` at canonical **main `4b21cef6`** (PR #29) |
| article PDF (local build of that tree) | `main_paper.pdf`, 9 pages, sha256 `d4f4ff2669a8727f81c2f367cc2280ece4adea7f359e14ac6e314903460319e5`; `build_all.sh` PASS, containment PASS |
| release candidate | **RC4** `minerva-omnifold-article-release-rc4.tar.gz`, sha256 `46f801bf05bbd18d1fcfe8c8bf5b0e361cd8e352211de641b434547be1680e88`; `verify_rc.py` gives PASS (README `docs/publication/release/RC4-README.md`, checksums `RC4-SHA256SUMS.txt`). It is local only. |
| product archive (internal) | `/global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006/`, 10,612 files, SHA256SUMS `1a72cb43…` (main `275b996d`) |
| standalone note repo | **synced** by the 2D lane from `4b21cef6`. `MINERvA-OmniFold-Analysis-Note` main is `cf449c30741ab31cb3f1ecafb840ed039801c793`; canonical main is `f46337701f14446f68ea0c1691e366ada92f0555`. Both were verified with `git ls-remote` by the publication lane, and the article sources are byte-equal to `4b21cef6`. Both repositories build PASS at 123 / 9 / 9 pp. |

## 2. Scientific and readiness record (internal; not for upload)

- `docs/publication/ARTICLE-READINESS-20261006.md`: the article's readiness, assessed separately. No scientific or
  provenance item remains open.
- `docs/publication/REVIEW-20261006-final-article.md`: the final independent review, two cycles, all findings resolved.
- `docs/publication/CLAIMS-20261005-claim-to-evidence.md` §D: the status of every claim.
- `docs/publication/DECISION-20261006-joseph-publication-approvals.md`: the approvals, plus addenda for VL170 and Fig. 2.
- `docs/publication/PRX-ASSESSMENT-20261006-final.md`: recommends PRD.
- The s5p campaign is terminal (`DELIVERY-20261006-s5p-campaign-terminal.md`). Its `publication_readiness` stays
  **NOT READY** by its own rule. This article's readiness is separate.

## 3. Drafted for the authors

- `COVER-LETTER-DRAFT.md`.
- `AI-DISCLOSURE-PROPOSED.md`. **This is required by APS policy, and the article has none yet.**

## 4. Inputs only the authors can supply (blocking for submission, not for review)

> **Status (note added 2026-10-08).** Inputs 1 and 2 were approved on 2026-10-06. The record is the last addendum of
> `docs/publication/DECISION-20261006-joseph-publication-approvals.md`. Per Joseph's sequencing, the disclosure goes
> into the article in the next paper pass, which has not happened. Inputs 3–6 remain open.

1. **The AI-use disclosure:** approve or rewrite the proposed text, and choose its placement in the article.
2. **Authors and metadata:** the author list (currently Bailey, Nachman), affiliations, ORCIDs, funding and any
   additional acknowledgments.
3. **Coauthor review** of the exact PDF above. Sending it is an external message, so it needs Joseph's
   authorization.
4. **The deposit:** its location, for example Zenodo or HEPData; the license (the inputs are CC0); and whether the
   ~2.3 GB product archive is also deposited. The article's one `\pubhold` (the deposit identifier) waits on this.
5. **Release tag** and **submission** (journal PRD; preprint server if wanted), each separately authorized.
6. **Cover-letter specifics:** submission history, and suggested or excluded referees.

## 5. Known, accepted limitations stated in the article

- No five-dimensional measurement with uncertainties.
- The rebuilt 2D statistical band has not been re-tested (KNOWN_ISSUES 84, 85).
- No recoil-response band in the calibration; the W2 sensitivity is exploratory.
- The Fig. 2 statement is descriptive, without a response-mismatch closure (Joseph, "Stands as written").
- The joint information adds no discrimination beyond matched coarse projections (W1).
- The release does not reproduce the 2D uncertainty, closure, bias, low-recoil, W2 or covariance-status numbers
  (listed in the RC4 README).
