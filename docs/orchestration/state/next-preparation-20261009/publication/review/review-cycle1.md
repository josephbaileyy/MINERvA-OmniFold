# Focused re-review (cycle 1): repair batch `b7f4c065` (parent `2b4dc8ff`)

## Setup
- Worktree: `git worktree add --detach reviewer/wt2 b7f4c065`, at HEAD `b7f4c06589b6441759db319dba99b27bd31601bf`, parent `2b4dc8ff`.
- `git status --porcelain` was empty at the start (0 lines) and the end (0 lines). The worktree was removed and `worktree list` no longer shows it.
- Scope: `git diff [--word-diff] 2b4dc8ff b7f4c065` only. It touches 9 files, +30/−21 lines: KI-88, `app_statmethods`, `main_note` abstract, `paper_body`, `primer_body`, `sec_method`, `sec_results`, `publication/REPORT.md` §0 (one claimed path added before editing), and CLAIMS §H L4.
- Out of scope, and not touched: numbers in `values.tex`, figures, receipts, audits, `publication/release/preservation/`.
- Rendered checks: `pdftotext` on `review-pdfs2/` (sha256 prefixes: note 14dbda60, paper bf44d6ec, primer 129dcc3f). Page counts are note 123, primer 9, paper 11. No "??" appears. I also diffed the word multiset and the per-page word counts against the cycle-0 PDFs.

## Disposition of F1–F11

| id | status | evidence at `b7f4c065` |
|---|---|---|
| F1 | RESOLVED | `main_note.tex:49-51` now adds: "that uncertainty is computed with a different tree-learning implementation from the central value, and whether it describes the central value has not been measured." It renders in full. |
| F2 | RESOLVED | `sec_results.tex:145-146` prints "a combined median of 6.827 % (against the 6.871 % of the table)". `app_statmethods.tex:434-436` prints 6.827 %. My read of `rc_pairing.json.txt` gives 6.826880, which rounds to 6.827, matching P14 (6.8269). It no longer collides with the systematic row 6.830 %. No `6.83` remains in rendered note text. CLAIMS L2 and KI-88 keep 6.83 %, which is correct at that precision and not printed next to a table. |
| F3 | RESOLVED | `app_statmethods.tex:434` now reads "The relative entries divide by …". √Tr C is no longer included in that sentence. |
| F4 | RESOLVED | `app_statmethods.tex:1034-1037`: "with little central-value change" is gone. The new text says "The integrated agreement does not mean the bins agree: … differ by a median of 0.97 % per bin, 1.3 statistical standard deviations (§3.2)." It names seed 1 against exact, and both numbers match P02/rc (0.966, 1.2995). The paragraph still leads into "Iteration-count effects are negligible," and the table. |
| F5 | RESOLVED | `paper_body.tex:118-120` renders as "…exact-split scikit-learn [21] gradient boosting with an unpinned seed, and a purity-based background subtraction." This is supported by P01 ("seed unpinned"). CLAIMS §H L4 drops "now complete". It now says accurately that the article states the estimators, the unpinned seed and the unmeasured transfer, and that only the note records `random_state=None` and the unmeasured exact-split seed noise. |
| F6 | DECLINED-OK | The closeout §4 marked this optional. The paper's estimator disclosure is sufficient without it. |
| F7 | RESOLVED | `sec_method.tex:111-113` adds "(This follows from the launcher and driver revision; the run's own log was not found, and the product records no seed.)" This matches P01's evidence class and runtime_origin ("product records no backend, seed or revision"). |
| F8 | RESOLVED | The comment at `sec_method.tex:85-86` now says the driver revision `d1bc8813` "had no estimator option and always used the exact backend". That agrees with my cycle-0 read of `d1bc8813`. |
| F9 | RESOLVED | `app_statmethods.tex:396-399` adds that the blocks use seed 1 (bootstrap) and seed 42 (universes), and that "whether their covariances are consistent across that seed difference has not been measured". This is P07, stated correctly. See N1 for a nit next to it. |
| F10 | RESOLVED | KI-88's status is now "**OPEN 2026-10-09**", so the duplicated header is gone and the bold markers balance. The description now reads "The LightGBM seed-1 central and the exact central differ by a median 0.97 % per bin (1.3 per-bin σ of the `VL170` statistical block; max 12.5 %)". It stays OPEN. |
| F11 | RESOLVED | `primer_body.tex:140, 154-157`: "version(s)" is replaced by "implementation(s)" in all 6 places, and none remain. |

## Check for new errors
- **Block-sum grammar.** The rendered text reads "These three Monte Carlos are independent by construction. They use different LightGBM seeds (…), and whether … has not been measured. The block sum is (16) C_tot = C_ML + C_stat + C_syst. The comparison adds…". The sentence leads grammatically into the equation, the equation keeps its closing period, and its label is unchanged.
- **New number 6.827.** Correct, as shown under F2.
- **Paper layout.** Only page 2 changed its word count (725 → 729). The only word lost against cycle 0 is the intended "boosting,".
- **Primer.** The only words lost are the five "version*" forms.
- **Note.** Word losses are the intended edits ("6.83" ×2, "little", "change.", "giving", "construction,", "scale.", and so on), plus reflow artifacts:
  - one fewer repeated longtable header ("Cited/Record/Tag/continued");
  - hyphenation and tokenization splits ("point-cloud", math-subscript tokens). For example, the `CV,truth`/`CV,in-acc` strings occur 3 times in both builds.
  - No text is missing.

## New findings
- **N1 (NOTE).** `app_statmethods.tex:395`, unchanged text: "training-seed trials vary that seed". The antecedent is now the universes' pinned seed (42), but the trials use seeds 1–10. The new sentence just after it names seeds 1 and 42, so the mismatch is more visible than before. Suggested fix: "vary the GBDT seed (1–10)". It does not block.
- No MATERIAL or MINOR finding was introduced by the repair.

## Verdict
**PASS.** F1–F5 and F7–F11 are resolved, F6 is an acceptable decline, and the repair introduced no errors. The three surfaces are consistent about the frozen exact-split central, the LightGBM uncertainty ensembles and their seeds, the unpinned central seed (with its evidence class), and the unmeasured transfer. None of them claims publication readiness.

## Resources
- Wall time: about 5 min of tool time.
- CPU: under 0.005 core-h (git, pdftotext, grep, two small `python3 -I` reads; 1 thread).
- Disk: a temporary worktree (removed) and about 3 MB of text in `reviewer/txt2/`.
- No cluster, GPU, training or event loops. Nothing was edited, committed or messaged.
