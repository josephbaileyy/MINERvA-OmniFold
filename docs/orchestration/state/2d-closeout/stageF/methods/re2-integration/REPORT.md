# RE-2 integration into the note, paper and primer: report (2026-10-24)

**Status.** Joseph approved the wording on 2026-10-24 (`DECISION-20261024-joseph-approve-integration-wording-s1-compute-preserve.md`): "okay I like the new wording." The branch
`stageF/re2-integration-20261024` is merged to `main` with the open sites below closed ("Merge", at the end).
- The batch landed only after that approval (DECISION-20261024-joseph-adopt-re2-2d-refined.md item 3).
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

## Update: the refined figures and the tension-mode correction (2026-10-24)

- **Figures.** The writer installed the 16 refined 2D figures. Each was fetched read-only from `partc-r2` and checked
  against its committed `SHA256SUMS` line. Each has a `make_figures.sh` digest pin and a G row in the ledger. This
  resolves open site 2.
- **The tension modes** (open site 1, and an error the new figure exposed): the text and caption now say three of the
  six leading modes lie in the highest-p_∥ bins, at λ/λ_max ≲ 4×10⁻⁹. The other three are moderate-λ modes. Ledger rows
  W2-t1, W2-t2 and W2-t3 cite the refined `tension_report.txt`.
  - Value row `tens-73-chi2` keeps its value, 0.66. Its new-context anchor changed from "… The four leading mode" to
    "… Of the six leading mode", because that sentence changed.
- **The ledger:** PASS, with V 240, M 5, F 94 and G 16. The self-test also passes.
- **The second agy round:** AGREE 5 of 5 (see `agy-review/README.md`).

## Merge: the remaining open sites (2026-10-24, after Joseph's approval)

`origin/main` (`d5617470`) was merged in first. Two registry rows that cite `CATALOG.md` were repointed, and the
results index and manifest were regenerated. Then:

- **Draft markers.** The 24 source comments that marked a draft (`RE-2 integration Wn (DRAFT)`), and the `values.tex`
  block heading, now cite `DECISION-20261024-joseph-approve-integration-wording-s1-compute-preserve.md`. Nothing printed changed.
- **The label (f)** (open site 3). `ALIASES.tsv` registers "configuration (f)" for `a-refined-400-31`, citing
  `paper_body.tex:290`. `check_registry.py`'s label patterns now cover (a)–(f), so the printed (f) labels are checked:
  111 labels, each naming exactly one estimator. Its self-test plants a "configuration (f)" with the alias removed,
  and the check fires on it.
  - The summaries of `a-refined-400-31` and `a-central-lgbm` in `ESTIMATORS.tsv` now say which estimator is the
    adopted 2D one.
- **"In every dimension"** (open site 4). The wording you approved states the 2D and 5D facts only. The 5D route has
  moved to configuration (e), which uses refined negative weights (`DECISION-20261024-joseph-5d-community-standard-route.md`
  item 5). The source comments in `main_note.tex` and `app_negweight.tex` now say so. No printed change.
- **`app_history.tex`** (open site 5). The batch had written Q_R's values into the Replacement column of the rows
  struck on 2026-10-18, and into two bracketed 2026-10-18 notes, while those rows still named Q.
  - That broke the records document's no-loss proof: `check_note_records.py probe` failed P5 on three record
    paragraphs.
  - The file is now `main`'s, verbatim, plus one new paragraph and table, `app:history-qr` ("Superseded on 2026-10-24:
    Q by Q_R"). It gives each of those values with Q and with Q_R. The Q values are superseded, not retracted, so they
    are not struck, and the frozen `\dead` multiset (P3) is unchanged.
  - The ledger's 29 `hist-*` V rows now point at that table. The values and their table checks are unchanged.
- **The records-move ledger.** The batch also changed five posted sentences that `records-move-ledger.md` pins: rows
  L8, L17, L-thin-C07, L-thin-C20 and L-thin-C39. Their N: probes now quote the approved text, and each row says
  "probe updated for the RE-2 integration". `check_note_records.py probe` gives `RECORDS-MOVE :: PASS`, 0 failures.
- **`VALIDATION_LEDGER.md:1614`** (open site 7). A new top entry, VL177, records RO-FPS against the adopted `E_R`:
  3.069e-38 against the control's 3.073e-38, −0.14 %, which does not reproduce (RE2-PARTC-REPORT §8). The 2026-06-10
  entry is unchanged, now at lines 1624–1626. The source comments that cite it by line (`sec_fps.tex`, `values.tex`,
  `primer_body.tex`) were repointed.
- **`paper_validation_residual.pdf`** (open site 2's remainder). It was recropped from the installed refined
  `MEFHC_5iter_pull_full.pdf` (`3d108335…`), with `make_figures.sh`'s own `pdfcrop --bbox '0 0 432 360'`. pdfcrop's
  output is not byte-deterministic, so the crop has no pin. No deliverable includes it.
- **Not changed:** open sites 6 (non-printing source comments that cite purity sources), 8 (`\fpsAbove`) and 10
  ("eightfold"), as listed in `DRAFTS.md`.
- **The standalone note repository** (open site 9) is synchronized after the merge.

