# D-ID admission review: fresh read-only reviewer, fixed commit `9203add1`

The lane owner records this file. The reviewer's final message is reproduced below with its formatting
condensed (tables flattened into lists, markup escapes removed); the findings, quoted phrases, numbers
and verdicts are unchanged. The reviewer worked in a clean detached worktree at
`9203add14391b89877a1b960eeae3bbea41b63ce` and reported `status --porcelain --ignored` empty
afterwards. Its scratch code stays in the owner's session scratch and is not tracked. The dispositions
are in `REPORT.md` §8.

---

# D-ID admission review — commit `9203add1`

**(a)** Fixed commit `9203add14391b89877a1b960eeae3bbea41b63ce` (branch `study/d-id-20261009`), reviewed read-only in detached worktree `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/01e230cb-f1a0-4461-9ab4-a2c4c601601c/scratchpad/review-9203add1`. Diff vs base `a16d5786` touches only the four `d-id/` files. Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), fresh subagent; not cross-provider.

## (b) Findings

**M1 — MATERIAL. H2 rows are appended twice → the real run stops at A4.** `did.py:108` calls `s5p_converge.install()`, which patches `s5c_coverage.reported_functionals` to already return 185 rows (H2 included); `did.py:524–528` then stacks `h2_rows()` again → 217 rows/names (185 distinct). The real study-K traces have 185 columns (recorded through the same patched function; `s5p_stage2_analyze.trace_functionals` reads them that way), so `did.py:627–628` fails A4 (exit 4) before anything is computed. Demonstrated: after rewriting the fixture world's `k_b0_nominal`/`k_b0_gibuu` to the real 185-column layout, the driver returned rc 4 with `{'A4_trace_k_b0_nominal_width': {'fn_push': [200, 185]}}`. The test suite misses it because `test_did.py:305–321` builds stand-in traces from `d.names` (a fixture derived from the code under test). Repair: use `reported_functionals` as returned and assert 185 names equal to the study-K list; add a test with an independently built trace layout (operand names + `EW_all_ones`/`total_integrated`).

**M2 — MATERIAL. Branch-B convergence is per-run, but the frozen text says per-functional.** gbdt §6: "A T2 *functional* that has not converged … cannot count toward branch B"; D-ID §4.1: "Non-converged functionals enter with r_IBU(∞) = ∞". Code: `did.py:988` `np.full(idx.size, bool(inf["converged"]))` with the all-active-cell stopping test (`did.py:275–281`). One slow T2 cell anywhere (even outside every reported functional) removes every functional of that departure from B. Demonstrated on a 40-cell fixture with one near-degenerate cell outside three functionals: after 10⁵ iterations the run is not converged (max cell change 3.3e-9) while the functionals' last-step changes are 6e-12–1e-10, |r_IBU(∞)| ≤ 9e-7, σ_rel ≤ 0.43% — all three are excluded from B. With 5,184 T2 cells this is the likely real outcome, making B structurally unreachable. Repair (decide prospectively, as a recorded amendment, before the run): e.g. a functional counts as converged if |Δ(h_j·t)|/|h_j·t| < 1e-10 at the stop (keep the AM-18 stopping rule; record per-functional last-step change), or state explicitly in §4/§5 that B requires whole-grid convergence.

**M3 — MATERIAL. The 8 GiB RAM cap is neither enforced nor credibly accounted.** `limits.ram_bytes` is never read in `did.py`. Every stored trajectory retains its full problem (`did.py:775` `"pb"`: R, dense maps…) in `self.T` (~110 entries by end of stage 5; on my synthetic world one retained entry was 15 MiB at T2 and 109 MiB at T3; real sizes scale with nnz and occupied T3 cells). §7 sizes row arrays at "20.4 M rows", which is the signal pair-row subset. Measured scaling: at 4 M synthetic rows (58 B/row layout) the stage-1 peak was 1.01 GB (0.92 above the import baseline); if the real file has that layout, 1.548 GB ⇒ ~26–27 M rows and linear extrapolation ⇒ ~6–7 GB at stage 1, before stage-5 retention. Any exception other than CapReached/AdmissionFailure (MemoryError, the `ValueError` at `did.py:222–223`, LinAlgError) escapes `run()` (`did.py:1182–1196`), so `finish()` never runs and no decision/tables are written. Repair: keep only K/r in `self.T`; free the remaining `d[...]` row arrays after `histograms`; check peak RSS against `ram_bytes` in `Budget.check`; catch generic exceptions per stage, mark the stage failed, and always `finish()` once stage 1 completed.

**m1 — MINOR. A8 compares counts under different in-grid rules.** `rows_eligible` uses `s5e_geometry.in_grid` (upper edge excluded, `s5e_geometry.py:47–51`); `did.py:553–557` uses `flat_index` (inclusive). Any row exactly on an upper edge would spuriously stop the run at A8. Repair: count with `s5e_geometry.in_grid` for A8 and record the other count beside it.

**m2 — MINOR. "B-undeclarable" is reported even when B is unreachable.** In 2,336 of 3,000 random label sets without stage 4, the candidate share was below 1/2 yet the map was labelled B-undeclarable, which §11 maps to INCONCLUSIVE; `all_three_sets_small` (`did.py:1040`) then uses B = 0. Repair: record `b_reachable` (candidate share ≥ 0.5) and declare mixed when B is provably unreachable, or at least report it.

**m3 — MINOR. §5 says background is "not present in the primary comparison", which is untrue for W2.** W2's comparator (AM-14) is the candidate-R assessment ensemble (`cand-assess-tasks.tsv` `aW2_*` with `--bkg-mode negweight-refined`; README line 54), with split MC, Poisson noise and per-experiment half-B truths; it enters the pool only through E2. Repair: state this and report the pooled shares with and without W2 beside the frozen outcome.

**m4 — MINOR. AM-2 relies on a recorded but ungated fact.** I verified r = 1 outside the grid for all five reweight paths (`eavail_ratio_weight`, `q3_given_eavail_w`, `ratio_weight`, `cond_weight`; their closed-edge masks match `flat_index`), but the driver only records `r_outside_grid_max_dev` (`did.py:577`) while using nominal b for every departure (`did.py:749`). Repair: gate it at exactly 0 in stage 1.

**m5 — MINOR. Amendment self-descriptions.** AM-15 changes §6's written formula F = Rᵀdiag(1/y)R (identical for the departure-weighted response, different by the binning bias for the nominal one); call it a correction, not a fill-in. AM-24 says "A6 proves each prefix"; A6 checks per-K medians at the receipt's K points, which together with the A4 file digest is adequate, but the wording should be changed.

**m6 — MINOR. C labels do not distinguish why σ = ∞.** Record per functional whether σ = ∞ comes from zero-efficiency cells (AM-3, an acceptance hole) or a numerical null mode, so C is not read as "weak response" in every case.

Checked and correct: AM-1 (asimov_same measures `pass_reco & pass_truth` signal rows; `omnifold_loop` restricts the MC side to `pass_truth`; the `s5e_trace` CLI refuses background variants for non-pseudo constructions; no background on either side for the traced comparators); AM-3 (zero-efficiency cell keeps its prior, σ = ∞); AM-11 key 798,985,164,084,644 = `split_key_for(301000)`; AM-12 (a = 1, as s5p `pow-P1_a1.0`); AM-14 W2 operands shape (20, 183); study-K weight names/amplitudes match `s2-conv-b0-tasks.tsv`; reco cells = nominal-occupied cells, equal to the receipt's var > 0 count; the driver calls no fit/unfold (no extension possible). `comparator.py` is unchanged since `31517ad7` (sha `f5374fe0…`), imported with a digest check, its constants used directly; the re-coded cuts (1e-12, 1e-6, 1.0) equal its defaults and are tested equal; no threshold, grid, departure, iteration limit or aggregation is changed.

## (c) Independently reproduced (own code; all agree)

- My EM vs `comparator.ibu` 1.6e-15, `did.ibu` vs reference 1.4e-15 (80 iterations); with a known term b and one zero-efficiency column, my EM vs `did.ibu` 2.3e-15 over 300 iterations, zero-efficiency cell exactly at prior; converged 23,657 iterations, error to truth 3.6e-7, stationarity 1e-10.
- Fisher 1.1e-16; CR σ ≤ 9e-13 vs did and ≤ 1.2e-13 vs comparator; singular case: σ = ∞ pattern identical, null fraction 4.8e-14; invisible share (7 of 15 modes weak) 0.0 vs did, 1.1e-11 vs comparator; σ with b agrees 1.7e-13 and all widths grow.
- T2 edges = `split_edges` (cells per axis 6,6,6,4,6 = 5,184); my cell-centre J map = `coarse_of_fine`; each of the 109 committed J rows is supported on exactly its J cell with weights = fine-bin volumes.
- `b_counted` vs my predicate vs `branch_outcome`: 0 mismatches in 3,000 trials; `declare` (stage 4 complete) = `branch_outcome` in 3,000/3,000; without stage 4 never folded into mixed/B.
- End to end through library functions: GBDT residual = 1.1 × exact IBU residual at exposure 1e8 → branch B (share 1.0; converged 911 iterations; r_∞ ≤ 6e-9; σ_rel ≤ 0.08%), trace reading `tracks`; GBDT frozen after K = 5 → B with `departs`; 5 × IBU → A; exposure 1e2 → C (σ_rel up to 81%).
- Owner suite: 22 passed (46.9 s wall, 77 s CPU, peak RSS 0.78 GB).
- Cost: `did.ibu` 6.4 ms/iteration at 2.9 M nnz, 13.6 ms at 5.7 M (T2 shape) ⇒ stage 4 worst case 1.6–3.4 core-h; whole run ~4–8 core-h worst case (stage 5 may hit the cap). The 7.04 core-h CPU cap is credible: the guard measures all threads via getrusage self+children, prices each unit before starting and checks every 1,000 iterations inside convergence (overrun ≤ ~14 s). The 8 GiB RAM cap is not credible until M3 is repaired.

No numerical disagreement; the one functional defect found is M1.

## (d) Verdict

**ADMIT-WITH-REPAIRS** (M1–M3); the owner gets one focused re-review. Branch-B route: adequately specified in rule and meaning once M2 is fixed. B is declared only by the coded rule and never folded into mixed; the trace reading uses only the receipt-verified prefixes (40/40/30/200) and frozen thresholds; the report states what B may and may not mean; the driver cannot extend s5p.

## (e) Resources

≈ 0.06 core-h CPU total, ≤ 2 threads. `git -C <worktree> status --porcelain --ignored` at the end: empty (exit 0); no `__pycache__` was created inside the worktree. Scratch code and synthetic files (≈ 0.3 GB) are in `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/01e230cb-f1a0-4461-9ab4-a2c4c601601c/scratchpad/reviewer-scratch/`, outside the worktree. The worktree is kept for the final numerical verification.
