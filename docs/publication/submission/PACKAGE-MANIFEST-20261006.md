# Submission package: manifest and remaining author inputs (2026-10-06)

**Status:** the package is assembled for Joseph's review. **Nothing has been submitted, deposited, tagged or sent.**
Those acts, and any message to coauthors, need Joseph's separate authorization (DECISION-20261006 item 6).

> **Update 2026-10-07 (paper-completion pass; `docs/publication/REVIEW-20261007-paper-completion.md`).**
> - **The article has changed since the versions in the table below.** The current sources are branch
>   `docs/prd-paper-completion-20261007` head `94b0042a`, delivered to main by the pass's PR.
> - **Local build:** `build_all.sh` PASS. Note 123 pp, primer 9 pp, paper 10 pp. `main_paper.pdf` sha256
>   `ce9ecf5b…`, one `\pubhold`.
> - **Review:** one fresh, read-only reviewer, two cycles, verdict READY WITH CHANGES. Every finding was applied
>   or recorded.
> - **Done in this pass:** inputs 1 and 2 of §4. The AI disclosure is in the Acknowledgments, with a pointer from
>   Sec. III. The author block is as approved.
> - **Not changed:** RC4.
> - **Standalone sync and both remote heads:** recorded in §1a below.
> - **Limitations stated in the article** are updated in §5.
> - **One scientific decision is open:** REVIEW-20261007 §5.

## 1d. Editorial and presentation pass (2026-10-08; branch `docs/prd-editorial-pass-20261008`, PR unmerged; supersedes §1c for the article text)

| component | identity |
|---|---|
| record | `docs/publication/EDITORIAL-20261008-prd-presentation-pass.md`: the APS/PRD sources, the five comparable papers, the before/after checklist, the remaining issues and the scope proposals for Joseph (§7) |
| article sources | the branch at `f4669b07`. No claim, number or approved wording changed; the release candidate (RC6) is unaffected. |
| revised PDF (local; not sent) | `../MINERvA-OmniFold-prd-editorial-pdf-20261008/MINERvA-OmniFold-PRD-article-editorial-f4669b07.pdf`, 11 pp, one `\pubhold` |
| standalone note repo | branch `sync-prd-editorial-pass-20261008` at `687b48ab`; standalone `main` unchanged at `e1af61e3` |
| follow-up (Joseph, 2026-10-08) | Figs. 1–3 redrawn by `make_figs.py` from the released arrays; AI disclosure names Claude Code, the Codex CLI and the model versions (record §9) |
| **release candidate** | **RC7** `27f0caba53c4bbf75310f6d94145ea872ebe77c6a6f55ef48298d95cbcee566e` (`docs/publication/release/RC7-README.md`, `RC7-SHA256SUMS.txt`): RC6 plus the new figure code; byte-reproducible from `8fa79cb1`; `VERIFY: PASS` from an empty directory; regenerates the printed figures byte for byte. Local only; not on CFS, not deposited, tagged or sent (record §10). |

## 1c. Release-audit corrections (2026-10-08; branch `fix/prd-release-audit-corrections-20261008`, PR unmerged; supersedes §1b for the release candidate)

| component | identity |
|---|---|
| corrections record | `docs/publication/corrections-20261008/RECORD-20261008-release-audit-corrections.md`: findings of audit `ea939701` rechecked, the article and note corrections, and the G1–G13 dispositions |
| **release candidate** | **RC6** `minerva-omnifold-article-release-rc6.tar.gz`, sha256 `71e2b7a4fc952ecd3494f75d4454f7add7ee01eb08aeb77ade5bc62d45c1461e` (`docs/publication/release/RC6-README.md`, `RC6-SHA256SUMS.txt`). It is byte-reproducible with `publication/release/build_rc.py` at its source commit (corrections record §9), and gives `VERIFY: PASS` from an empty directory with its `requirements.txt`. Local, plus a durable CFS copy; not deposited, tagged or sent. |
| RC5 (superseded) | `6784708827e8337c7d3f7774e0fb727c24613ed7eb0db4cadf101fc6413124be`, rebuildable from source commit `f82e6db76f20119450e7364ec2d9919c23c67db7`; kept on CFS (`rc5/`) |
| RC4 | unchanged, `46f801bf…`, preserved at `/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/rc4/` (verified) |
| supporting products | the same CFS directory: 16,239 files, 42.4 GB, every destination file verified against its source hash |
| article build and standalone sync | the corrections record §9 |
| coauthor-review PDF | the `0e7d9b1b` PDF in §1b predates these corrections. A PDF for coauthor review should be built from the corrections commit once Joseph accepts it. |

## 1b. Current versions and remote heads (2026-10-08, after PR #53; supersedes §1a)

| component | identity |
|---|---|
| article sources | canonical **main `0e7d9b1b`** (merge of PR #53, which adds the report-only κ-scan sentence and its citation to Sec. VI.C) |
| canonical build at `0e7d9b1b` (detached worktree, clean tree) | `build_all.sh` rc 0, `RESULT :: PASS … head=0e7d9b1b tree=clean`, note 123 / primer 9 / paper 10 pp; Overleaf target rc 0, 10 pp, 0 undefined references. One `\pubhold` (deposit identifier). |
| **PDF for coauthor review** (local only; NOT sent) | `../MINERvA-OmniFold-coauthor-review-20261008/MINERvA-OmniFold-PRD-article-0e7d9b1b.pdf`, 10 pp, sha256 `20b2f77410e1499d3eacd5c47270ae43083e289f8202cf6b8535065222d015c0` (the canonical build above; the digest includes the build date). It shows the one red `[HOLD: …]` for the deposit identifier. Sending it is an external act for Joseph (input 3). |
| standalone note repo | synced from `0e7d9b1b`: standalone commit `2357c6c`, 2 files (`paper_body.tex`, `publication.bib`). The standalone equalled canonical `f9ca7de7` before the copy and equals `0e7d9b1b` after it, in every tracked file except `.gitignore` and `AGENTS.md` (checked with `cmp`). `build_all.sh` rc 0 at 123 / 9 / 10 pp; Overleaf target rc 0; `pdftotext` of all three PDFs identical to the canonical build. |
| remote heads (`git ls-remote`, 2026-10-08) | `MINERvA-OmniFold-Analysis-Note` main = **`2357c6ca4c3d5804dd22d409652128926abfa25d`** (fast-forward from `c26bf4fe`); `MINERvA-OmniFold` main = **`0e7d9b1b43e562470b76166cc3e5063c3589b90c`** before this record's own merge |
| pinned citations | `JointTestKappa2026` → `fbf682f9`, `JointTestRecoil2026` → `2926e39e`; both on main and both return HTTP 200 |
| release candidate | RC4 `46f801bf…`, unchanged. The κ-scan is recomputable from RC4's sufficient inputs with `publication/kappa/kappa_breakdown.py`, but it is not part of `verify_rc.py`; the article says so. |

## 1a. Versions and remote heads (2026-10-07, after PR #50; superseded by §1b)

| component | identity |
|---|---|
| article sources | canonical **main `f9ca7de7`** (merge of PR #50; the article head is `94b0042a`). `docs/analysis-note/` is unchanged by the record-only commit that adds this section. |
| local build at `f9ca7de7` (fresh detached worktree) | `build_all.sh` rc 0, `RESULT :: PASS … head=f9ca7de7 tree=clean`, note 123 / primer 9 / paper 10 pp; Overleaf target `latexmk -jobname=output main_paper.tex` rc 0, 10 pp, 0 undefined references. PDF digests include the build date and are not reproducible byte for byte. |
| standalone note repo | **synced** from `f9ca7de7` by the publication lane. Standalone commit `c26bf4f`, 4 files (`main_paper.tex`, `paper_body.tex`, `publication.bib`, `values_inference.tex`). Before the copy, the standalone equalled canonical `4b21cef6` in every tracked file except its own `.gitignore` and `AGENTS.md`, checked file by file with `cmp`; afterwards it equals `f9ca7de7` the same way. Standalone `build_all.sh` rc 0 at 123 / 9 / 10 pp (containment PASS; `head=unknown` is the documented fallback); Overleaf target rc 0, 10 pp; `pdftotext` of all three PDFs identical to the canonical build. |
| remote heads (`git ls-remote`, 2026-10-07) | `MINERvA-OmniFold-Analysis-Note` main = **`c26bf4fe04713b9e15bb3741e0b25a45b7dcfbe9`** (fast-forward from `cf449c30`); `MINERvA-OmniFold` main = **`f9ca7de7f82585c4ec48f0c44657d734243f372b`** before this record's own merge. |
| pinned citation | `JointTestRecoil2026` pins `2926e39e`. After the merge it is an ancestor of main, and the GitHub URL returns HTTP 200 (REVIEW-20261007 N1 closed). |
| release candidate | RC4 `46f801bf…`, unchanged |

## 1. Exact versions (2026-10-06; superseded for the article by §1a)

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
- `AI-DISCLOSURE-PROPOSED.md`. Required by APS policy. **Approved 2026-10-06 and in the article since 2026-10-07**
  (Acknowledgments, with a pointer from the method section).

## 4. Inputs only the authors can supply (blocking for submission, not for review)

> **Status (note added 2026-10-08; updated 2026-10-07 by the paper-completion pass).** Inputs 1 and 2 were approved
> on 2026-10-06 (last addendum of `docs/publication/DECISION-20261006-joseph-publication-approvals.md`) and are now
> **done in the article**:
> - the disclosure text verbatim, in the Acknowledgments, with a pointer from Sec. III;
> - the author block unchanged, as approved.
>
> ORCIDs and funding were not supplied; add them if wanted. Inputs 3–6 remain open.

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
- No recoil-response band in the calibration. The W2 sensitivity is exploratory and data-side only: the null was
  not varied, and species, energy and resolution effects and larger variations are untested. The matched
  (p_T, p∥) projection does not reject GENIE 2.12.10 CV (W1, post hoc).
- The sub-fine-grid residual is "unmeasured, potentially material" (amendment 8's frozen rule).
  - The κ = 2/3 variants rest on an assumed convergence rate in a proxy metric.
  - The tolerance beyond κ = 3 was evaluated report-only on 2026-10-08
    (`publication/kappa/RECORD-20261008-kappa-breakdown.md`): every decision holds up to κ ≈ 5.25. The article
    states this since 2026-10-08 (Sec. VI.C, report-only, as sensitivity along δ_M1 only).
- The Fig. 2 statement is descriptive, without a response-mismatch closure (Joseph, "Stands as written").
- The joint information adds no discrimination beyond matched coarse projections (W1).
- The release does not reproduce the 2D uncertainty, closure, bias, low-recoil, W2 or covariance-status numbers
  (listed in the RC4 README).
