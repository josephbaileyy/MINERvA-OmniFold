# RE-2 integration into the note, paper and primer: report (2026-10-24)

**Status.** On branch `stageF/re2-integration-20261024`, **not merged.**
- The batch lands only after Joseph approves the wording (DECISION-20261024-joseph-adopt-re2-2d-refined.md item 3).
- The writer (a subagent of the paper-tighten lane) prepared it, and the director reviewed it. The subagent's harness
  refused this report file, so the director wrote it from the writer's reply and the director's own checks.

**What it does.**
- **Values:** 240 printed values regenerated from `re2/run/partc_r2/partc-r2/values_table.tsv` by `apply_values.py`,
  198 of them changed at printed precision. Every control-PASS row that prints in a deliverable is applied. Not
  applied: the 8 new products, `\fpsAbove` (declared failure) and `ro-fps`, whose site is not a deliverable.
- **Fig. 1:** replaced by `71a2ea48…` (RE2-PARTC-A3-REPORT). `make_figures.sh` installs it with a digest check.
- **`check_sec4_receipts.py`:** repointed at `Q_R`'s `budget_Q.json.gz`.
- **Macros:** 6 new, among them `\cmodelMedian` 3.71, `\qrCmodelMedian` 7.90 and `\cmodelIntegral` 0.03.
- **Wording:** 46 drafts (D01–D46, `DRAFTS.md`) cover items W1–W10. The outside review is in `agy-review/`.

**Checks at the branch head** (after `origin/main` was merged in and the two review fixes made):
- **`build_all.sh`:** rc 0. All PDFs were built fresh, every gate passed, and Sec. IV gave 15/15. Paper 13 pp, note
  121 pp, primer 15 pp.
- **`check_ledger.py`:** PASS, with 240 V, 5 M and 90 F rows. Its `--self-test` PASSes: the three planted rows fail.
- **`main_paper.tex`:** unchanged. No changed line matches the protected patterns.
- **`swallowed_text.py`** against base `104c69a3`: one flag, `values.tex:358`, which is already on `main`.

**Two fixes from the outside review** (`agy-review/README.md`):
- **D30:** a draft comment had swallowed "It has no matched covariance: no". The words are restored, and ledger row X4b
  requires them to print.
- **D05:** the legend remark is dropped from the release-status paragraph.

**Open sites.** The writer listed ten (the end of `DRAFTS.md`). The ones that need a decision or more work before
merge:
1. **The tension-mode statement** ("λ/λmax ≲ 4×10⁻⁹") cannot be checked against the refined tension report. It is
   left as printed.
2. **The other 2D figures** are still the purity versions. Part C's refined versions are on pscratch and HPSS and
   are not yet committed.
3. **The registry** does not yet know the new label "(f) as (a), refined", and the summaries of `a-refined-400-31` and
   `a-central-lgbm` are stale.
4. **The "revisit in every dimension" wording** (DECISION-20261023 item 2) needs Joseph's reading, because 5D still
   uses purity. The 5D route has since moved to configuration (e).
5. **`app_history.tex`**'s rows describe Q in their other columns.
6. **`VALIDATION_LEDGER.md:1614`** is not edited.
7. **The standalone note repository** is not synchronized, as the decision requires.
