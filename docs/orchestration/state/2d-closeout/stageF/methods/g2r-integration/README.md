# G2R integration: the note's Q_R-derived values moved to RE-2-shapes run 2 (C_new)

**By** director-helper-2 (the note lane), 2026-11-15.

**Under** `DECISION-20261114-joseph-d1-g2r-adopted.md` (Joseph: the rebuilt 2D covariance is adopted; item 3, every
dependent result is updated from the G2R records) and the director's rulings of 2026-11-15: re-key every printed
Q_R-derived value (a partial re-key would leave mixed products), each equal to the paper's key wherever both print;
the records document's dated 2026-10-24 column stays, and a new superseded entry is added; this ledger and checker
are the method.

**Sources.**
- OLD, RE-2 part C: `docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/`.
- NEW, RE-2-shapes run 2: `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/re2shapes/run2/g2r/`,
  merged at main d58d0d18 by #1167. Its own SHA256SUMS lists values_table.tsv (798b837c…), cmodel/cmodel_R.json
  (0525217d…) and ./outA/budget_Q.json (gunzip of the committed .gz, 7ed733c6…).

**Files.**
- `ANCHORS.tsv`: one row per printed value, giving the value's source (a values_table row, or a JSON key with
  scale and format) and an anchor of printed text that locates it.
  - 39 anchors are the RE-2 integration ledger's contexts that still print.
  - 10 are by hand: seven whose RE-2 context was later rewritten or repeats, \qrCmodelMedian, the C_model
    84th percentile, and its maximum (24.49 → 24.60, read from cmodel_R.json, not the table).
- `ledger.tsv`: 49 V rows, built from ANCHORS.tsv against the pre-G2R text. Each row has old and new printed values
  and old and new contexts.
- `g2r_ledger.py`: `build`, `apply`, `annotate` (the same-line source notes), `check` and `--self-test`. See its
  docstring.

**Commands.** From the repository root:
- `python3 docs/orchestration/state/2d-closeout/stageF/methods/g2r-integration/g2r_ledger.py check .` (PASS: 49 rows,
  2 products sha-checked, every posted file swept)
- `python3 …/g2r_ledger.py --self-test .` (a wrong new value and a stale old context each fail; the real ledger is
  silent)

**What changed.**
- **The 49 values:** app_statmethods.tex 31, sec_results.tex 4, sec_systematics.tex 8, values.tex 6 (\uqMedian,
  \chiCombined, \chiCombinedLog, \chiCombinedSubStat, \fluxBand, \qrCmodelMedian). numdiff shows exactly these swaps,
  and no line count moved.
- **The posted sweep:** no printed copy of an old value is left in any posted build (note, paper, primer, PET note).
  Searched: every old literal, digit-bounded, over the printed \input closure.
- **The paper:** this branch's values.tex is the note's. The draft paper is draft/methods-short, with its own
  values.tex, so nothing here changes what the paper prints. director-helper-3 has the six changed macros, so that
  its D1 commit sets the same values: \uqMedian 6.46, \chiCombined 0.943, \chiCombinedLog 0.959,
  \chiCombinedSubStat 6.95, \fluxBand 3.72, \qrCmodelMedian 7.93.
- **Same-line notes:** each source line that carries a re-keyed value ends with `% G2R: … ledger.tsv <rows>`. An
  older source comment on another line that cites RE-2 part C therefore reads as the earlier value.
- **check_sec4_receipts.py:** BUDGET_Q is repointed to run 2's budget, as the RE-2 integration repointed it before.
  Result: 17/17 PASS, self-test PASS.
- **app_statmethods.tex:347:** the five-definition recomputation is attributed to an earlier covariance. The quoted
  \chiCombined and \chiCombinedLog are stated to have no independent recomputation; run 2's check_rebuild checks only
  cell identity and fig6/7 (cov2d, 2026-11-15).
- **The records document (app_history.tex):** a new paragraph "Superseded on 2026-11-14", with seven rows. The
  2026-10-24 column copies the table above it. The new column is run 2's hist-* rows, placed at the RE-2 ledger's
  hist-* positions. Two parenthesized rounded forms (6.46, 3.72) are placed by hand, because their old value is a
  prefix of the full one. This is records addition L-g2r-1 in records-move-ledger.md, and L8's probe is re-pinned to
  0.389.

**Not changed:** the 25 hist-* values of the dated 2026-10-24 column, the paper's sources, and fig6/7 (a separate
commit).

**CITABLE FOR:** which note values were re-keyed, from which run-2 product, at which printed place.
**NOT CITABLE FOR:** any physics claim, or any value the ledger does not list.

**Meaning read of the two wording items (codex-school gpt-6.1-sol, high, read-only; reads/):**
- **Pass 1:** FAIL on both. N1's "only" omitted run 2's projection-equality check, and H1's "complete list" claim was unsupported.
- **Pass 2,** both revised: OVERALL PASS.
