# Outside review of the RE-2 integration wording, by agy (2026-10-24)

**Why.** Joseph asked that every changed sentence be in PRD style, and that each go to agy with its surrounding
paragraphs, which must agree before Joseph sees it (DECISION-20261024-joseph-adopt-re2-2d-refined.md item 3).

**How.**
- The 46 drafts of `../DRAFTS.md`, at the branch head `38ba99a4`, were split into four groups:
  - the paper, 7 drafts;
  - the primer, 3;
  - the note's appendices and front matter, 10;
  - the note body, 26.
- Each group went to agy (gemini-3.8-flash-high) with the PRD style guide (`style-guide-input.txt`, §4 of
  `register-prd-study/REPORT.md`). Each draft carried its old and new text, the paragraph before and after it, and its
  fact sources.
- **Two passes:**
  - **No tools** (`PROMPT-no-tools.txt`). A first attempt produced nothing: agy asked for a shell tool, which headless
    mode auto-denies. The rerun's prompt says to answer from the text.
  - **With tools** (`PROMPT-with-tools.txt`). This ran under `--sandbox --dangerously-skip-permissions`, as Joseph
    suggested, in an empty scratch directory, with web search allowed for comparisons with published PRD papers. It
    cited arXiv 1910.08658, 1911.09107, 2004.05434, 2102.03346, 2106.16210, 2108.12376, 2110.13372, 2301.03700,
    2310.06082 and 2504.06857. Its working directory was left empty.

**Verdicts** (`review-*.txt`, verbatim):

| group | no tools | with tools |
|---|---|---|
| paper | AGREE 7 | AGREE 7 |
| primer | AGREE 3 | AGREE 3 |
| appendix and front matter | AGREE 9, REVISE 1 (D05) | AGREE 10 |
| note body | AGREE 25, REVISE 1 (D30) | AGREE 25, REVISE 1 (D30) |

**What the director did with them.**
- **D30 was a real defect,** and both passes caught it. A draft provenance comment in `sec_method.tex` had swallowed
  "It has no matched covariance: no" into a LaTeX comment, so the printed sentence read as a fragment saying the
  opposite. The words are restored.
  - The repository's `swallowed_text.py`, run over the branch, found exactly this one new case. Its other flag,
    `values.tex:358`, is already on `main`.
  - A ledger row (X4b) now requires the sentence to print.
- **D05: accepted.** The no-tools pass asked to drop "and its legend set in sentence case" from the release-status
  paragraph, as bookkeeping. The with-tools pass agreed with D05 as written. The director took the cut, because the
  sentence still says RC7's plotting code was extended. Ledger row W10 was updated.
- **"Cannot verify" notes:** on regenerated numbers such as 0.141 % and 17.6 %. These are the V rows of `../ledger.tsv`,
  which `check_ledger.py` ties to `values_table.tsv`.

After these two changes, every draft has agy's agreement. The drafts then go to Joseph.
