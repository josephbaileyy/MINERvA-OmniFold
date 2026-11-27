# Gemini read r1 of PR #1378: dispositions

The read is `out.txt` here: gemini-4-hydrogen-xhigh, read-only, inputs unchanged (`receipt.txt`). It read the head
362011d24428f848746a43fc126661708cffbbe1 and returned NO-GO. The director checked the main findings against the diff
and confirmed them on 2026-11-26. The fixes are in 446a777b6a301dd124adcc9cd18c3c7d97ff8243 (journal-editor). Every
changed sentence is a PROPOSAL for Joseph. The director accepted the fixes as proposals, including "the baseline
covariance" (C_rep with C_e in place of C_e^infl) as the one term for the earlier matrix, defined at first use.

| # | Finding | Disposition |
|---|---|---|
| 1 | sec5_multidim:103/106 contradict themselves and state the C_e-era picture | Fixed. Both eras are stated, and three sec5_multidim sentences are bound in LISTED_CLAIMS |
| 2 | records_r05_sixteen:244, quadrant thresholds | Comment only, left unedited (below) |
| 3 | records_r04_higherdim:463, PRR level counts | Fixed. Both eras' counts are given (new keys prr-ce-lev-*), with the q3 reference shift stated. A guard checks that q3 is flagged only at C25 and O2 under C_rep |
| 4 | records_r05_sixteen:149, f0b-nlisted | Comment only, left unedited (below) |
| 5 | appC:242 and sec_q3_fived16:91, flag persistence | Fixed. The persistence claim is restricted to the baseline covariance. Under C_rep the GiBUU hybrid stays flagged at every setting |
| 6 | the figures' captions name C_rep but the figures are C_e-era | Assigned to tier3-design's figure branch, merged into #1378 |
| 7 | appC:234 and :257, the residual qualifier and the unchanged bias | Fixed. "At the same residual" is restored, the bias is stated as unchanged, and R06's \|z\| without the run-period term is stated, and guarded, as below the threshold |
| 8 | sigratio's denominator | The denominator is named. Two options go to Joseph in the PR's before/after table. The text's own records_r05:171 site is a comment (below) |
| 9 | the C_e^infl definitions row dropped the coverage clause | Restored, with an absence-ok waiver |
| 10 | ΔC_e printed but undefined | Defined in the definitions row and in the diag caption |
| 11 | sub-block names used for whole test matrices | Fixed throughout with "the baseline covariance" and "C_rep" |
| 12 | records_r05_sixteen:403, e2-dmax | Comment only, left unedited (below) |
| 13 | appC:244 and sec_q3_fived16:91, IBU's q3 p and count | Fixed. Both eras: 0.011 and four, against 0.255 and two (new key prr-ce-ibu5-nnew-word) |
| 14 | QD's printed-only weakening | Fixed. The caption states ρ* under the baseline covariance, bound to the pinned C_e-era cr readout (crce) |
| 15 | RSN SM conclusion | Fixed: "so the fake-data conclusions hold under both constructions" |
| 16 | subscripts, and the PR-body bookkeeping | Fixed in the lines this PR adds. The PR body is updated with the head |

## The comment-only sites (findings 2, 4 and 12, and finding 8's records_r05:171 site)

<!-- absence-ok: what a compiled PDF prints at a pinned head, measured by the text search below; not a claim that a result does not exist -->
Lines 149, 171, 244 and 403 of `docs/analysis-note/records_r05_sixteen.tex` all begin
`% [lead-in, Option B] In the paragraph as the note printed it, this text followed: ...`. They are LaTeX comments that
quote the pre-rewrite text, and they print nothing. A text search of `main_records.pdf` built from the fixed tree (the
journal-editor lane's build_all run of 2026-11-26) finds 0 hits for each of their phrases: "exceeds the stated criteria
at", "below correlations of" and "raises the per-cell". The director confirmed on 2026-11-26 that they stay unedited,
because they record past text.

`vf_readings.py`'s `print_sites()` lists every `\fvval{}` occurrence in a .tex file, comment lines included. That is how
these four lines appeared as print sites in `vf_readings.md` sec. 2.

## Tidy-up (the director's list)

- `vf_readings.py` `print_sites()`, and any reading tool built on it, should skip LaTeX comment lines, so a commented
  quote is not reported as a print site.
