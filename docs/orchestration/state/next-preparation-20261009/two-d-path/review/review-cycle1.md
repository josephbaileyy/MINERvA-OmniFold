# Focused re-review: two-d-path design record (after the repair batch)

| field | value |
|---|---|
| Reviewer | Claude Opus 5.5 (`claude-opus-5-5`), Claude Code subagent, read-only. I wrote the initial review and did not author the record. |
| Fixed commit | `0a2e0f41498ea0e456ae9df4dc847608f8b5fb87` (branch `prep/two-d-publication-path-20261009`). The repair is one commit on top of `ebcba79c`. |
| What changed | Four files: `REPORT.md`, `design_arith.py`, `design_arith.json`, and `review/review.md` (new). Operands, logs, `seed_mechanism_check.py` and `remote_reduce*.py` are unchanged. |
| Start / end (UTC) | 2026-10-10T05:41:32Z / 2026-10-10T05:46:48Z |
| Worktree | detached at `0a2e0f41` under the scratchpad. `git status --porcelain --untracked-files=all` was empty (0 lines) at start and at end. Removed with `git worktree remove`. |
| Resources | local CPU under 0.01 core-h, 2 threads. Scratch 108 KB in `review-scratch/` (`repro3.py`, `regen2.json`, `driver_d1bc.py`, partial copy of the initial review). No cluster access, jobs, GPU or training. |
| Owner tools run afterwards, for comparison only | `design_arith.py --self-test` PASS (16 checks). A regenerated JSON written to scratch is identical to the committed `design_arith.json`. |
| Preserved initial review | `review/review.md`, sha256 `a95a66ebc7658e24…`, as REPORT §12 states. The first 24 lines (header and verdict) diff byte-identical against my re-typed copy. I checked the other 95 lines by reading them line by line against the text I returned and found no difference, but I did not byte-diff them. |

## Verdict

**PASS WITH CHANGES.**
- F1–F23: 20 RESOLVED, 3 PARTIAL (F5, F6, F2), none UNRESOLVED. All the moved numbers reproduce.
- Two new MATERIAL defects remain, both fixable in text:
  - **N1:** stage T's "false-fail probability is 0" holds only under a degenerate null.
  - **N2:** XR's manifest leaves `--out` and the working directory unspecified. Read literally, "the central launcher's arguments unchanged" overwrites the quoted `E_C` product, and parallel runs would collide on the default output name.
- The L42 PASS and the XR PASS hold only once N2 is fixed in the pinned manifest. N2 must be fixed before any submission. N1 must be withdrawn before stage T is offered as a decision option.

## Status of F1–F23

| id | status | evidence |
|---|---|---|
| F1 | RESOLVED | §3.6 now states the three confounds: background treatment, the 2026-07-08 omnifile regeneration (with the script citation) and the driver revision. It says the mechanism is unknown and drops the double-count claim. The inflation formula is now 1/√(1−s) − 1 over cells with s < 1, and the s ≥ 1 cell is counted. The confound is carried into §3.5 ("validates nothing by itself") and §5. §11.2/§11.3 and the `pair_structure` docstring are restated. One residual: the s ≥ 1 cell is counted (`n_cells_ge_1`: 1) but not identified; it is reported index 126, cell (7,14). |
| F2 | PARTIAL (the spec resolves the confound; see N3) | §6 now specifies 0/1 multipliers on retained rows, a bin-mapper digest as a pre-run check, and full-data purity. The binning confound is gone. What the spec still does not state is in N3 (cross-half dependence) and N4 (POT scaling). |
| F3 | RESOLVED | A declared-family tier (236 functionals × 2 streams, m = 472) is the PASS basis and is priced at 303–1,131. The regional tier is labelled a narrower alternative for Joseph to decide, and §2 K2 is restated so that projections are tested as functionals. |
| F4 | RESOLVED | The regional tier is sized at the declared Bonferroni level, with verdict probabilities at κ = 1, 0.8, 1.25 and 0.63. n_eff is assumed and capped (3, 5). The interval is specified as a 98.75 % joint percentile bootstrap. NOTE: √(π/2) is the large-n factor for the sd of a median. For n = 3 and 5 my simulation gives 1.156 and 1.196, so the sizing is slightly conservative. |
| F5 | PARTIAL | The statistical arm is correctly removed and its weakness shown (0.43 / 0.84). But the T-syst replacement claim "false-fail probability is 0" is stronger than its operand (N1). |
| F6 | PARTIAL (resolved in structure; see N2 and N6) | X0′ (the `d1bc8813` blob, the revision of record in A `pairings.tsv` P01) is added, with its outcome rows and an L1 row. The X0-fail/X0′-fail row is honestly labelled "cannot be separated". The d1bc8813 driver imports only numpy, ROOT and the helper. Its `ohf.omnifold(...)` call is compatible with today's signature (new keywords have defaults, `estimator="exact"`). The guard runs a script inside `--expect-root`. So X0′ is sound in principle. The manifest gaps are in N2 and N6. |
| F7 | RESOLVED | X1 is named "a one-seed `P09b`" in §10's questions, run table and authorization. The record asks for a specific ruling and gives a fallback without X1. |
| F8 | RESOLVED | The cap is 6.375: 4 exact jobs × 30 h × 12/256, plus 3 LightGBM jobs × 0.25. That covers one rerun of each kind. Over-limit and missing runs are INCONCLUSIVE. The expected 2.83 is stated as a subtotal, with the departure from the convention made explicit. |
| F9 | RESOLVED | Every quoted price reproduces under one convention, and X's conservative figure uses as-run replicas. One residual is a stale JSON field (N5). |
| F10 | RESOLVED | §3.7 uses κ ≈ 0.63, giving 2 cells. |
| F11 | RESOLVED | The wall is now "median 14 min (544–1,900 s)", matching speed REPORT:82. `E_C_minus_CV42_median_rel_pct` = 0.9928 is a JSON field. |
| F12 | RESOLVED | Usefulness is INCONCLUSIVE, with half-width including B±. |
| F13 | RESOLVED | F is frozen as 16 GlobalIDs and `purity_newomni` is chosen. NOTE: §3.5 says the 62 % Flux change "must be inspected before use", but no fallback rule is frozen in case the inspection fails. |
| F14 | RESOLVED | The command syntax matches `mnv_guarded_run.py` `main()`: options, then a mandatory `--`, then the script, with the script inside expect-root. |
| F15 | RESOLVED | The accuracy row states the NO-GO. |
| F16 | RESOLVED | §6/§7/§15 say "partial; pair bands only; no rule for A". |
| F17 | RESOLVED | The "synthetic" qualifier appears in §2, §4, §5 and §11.3. |
| F18 | RESOLVED | The split term uses (1 + γ/4). The self-test is described as arithmetic only. |
| F19 | RESOLVED | S-b carries its own laterals; the route totals add only 6 B± unfolds plus the SD/SM runs. |
| F20 | RESOLVED | Both sweeps are given (1.4e-9 / 2.6e-9). |
| F21 | RESOLVED | The half-to-full extrapolation is stated for both streams (§6, §13). |
| F22 | RESOLVED | rms z 1.28 against a t₉ expectation of √(9/7) = 1.134 is disclosed, and the seed choice is stated as cost-based. |
| F23 | — | No action was needed. Operands are unchanged, so data hygiene is unchanged. |

## New findings

| id | severity | location | finding | evidence | required repair |
|---|---|---|---|---|---|
| N1 | MATERIAL (conditional stage, not in XR's request) | §10 stage T "Assurance"; `design_arith.json` `stage_T.T_syst_false_fail_if_transfer_exact` = 0.0 | "Both backends are deterministic … so a perfect transfer gives η = 0 exactly and the false-fail probability is 0." That is true only under a null in which the exact and LightGBM deltas are identical universe by universe. Two different estimators cannot meet that null: their CV centrals already differ by a median 0.136 σ_tot, up to 1.46. The decision-relevant null is "the widths transfer within tolerance". Under it, η carries estimator-specific scatter from 10 Flux throws and 3 single pairs, and §3.6 shows such scatter exists for LightGBM. Determinism removes run-to-run noise, not between-estimator scatter. XR also does not establish determinism of exact universe-file runs: it tests a CV reproduction and one seed. Separately, the PASS / INCONCLUSIVE / FAIL precedence is ambiguous when η passes but the jackknife straddles the edge. | Logic, plus the operands cited. No assurance computation exists for the non-degenerate null. | Withdraw "false-fail 0" or restrict it explicitly to the identical-delta null. State that the false-fail rate under a width-equivalence null is unquantified (as the power already is). Fix the precedence of the three verdicts. |
| N2 | MATERIAL (manifest) | §10 run table and Launch | **(i)** X0 is "the central launcher's arguments unchanged". The launcher passes `--out ${DOCS}/2d_crossSection_omnifold_MEFHC_5iter.root`, which is `E_C` itself. The parenthetical argument list omits `--out`, so a literal reading overwrites the irreplaceable quoted product. **(ii)** Without `--out`, X0, X0′ and X1 all write the default `2d_crossSection_omnifold.root` in the same working directory. A 20–30 h parallel schedule would collide. **(iii)** X0′ is "run from" the record directory, but `--mcfile baseline_flux/…` is relative, so the working directory must be `2d-unfolding/` with the driver given by absolute path. **(iv)** The deployment procedure checks for no *pending* jobs, but a *running* job on the canonical tree is also exposed to the checkout move. Cleanliness is verified after the move, not before. | `2d-unfolding/sbatch_unfold_2d_MEFHC.sh` (`XSEC_OUT`, `--out`). Default `--out` in both drivers (`d1bc8813:611`, HEAD:1059). | Give each run an explicit, distinct `--out` under the XR record directory, plus a pre-run refusal if any output path equals `E_C`'s. State the working directory and absolute driver paths. Require `squeue` to show no pending **or running** job on the tree, and `git status --porcelain` to be empty **before** the move. |
| N3 | MINOR | §6 SD/SM | With 0/1 masks the halves share bin mappers built from all rows. LightGBM's row-count constraint (`min_child_samples`) also counts zero-weight rows of the other half. So U_A and U_B are weakly dependent through the other half's feature values, and the Bernoulli independence of the *samples* does not make the *estimates* independent. The bootstrap reference has the same structure, so the comparison is consistent as a conditional design. But "(U_A − U_B)²/2 measures the half-exposure sampling variance with no resampling model" is stated without that conditioning. | LightGBM defaults; `omnifold.py` `fit(..., sample_weight=…)` with retained rows. | Add one sentence: the split measures variance conditional on shared bin mappers and row-count constraints, which is the same conditioning as the fixed-seed bootstrap. |
| N4 | MINOR | §6 SD/SM normalization | One `pot_scale = data_pot/mc_pot` scales the signal MC, the background template and the truth denominators (driver `get_pot_scales`, `fill_bkg_reco_2d`, l.713–724), and the cross section divides by the data POT (l.893–941). The helper does not normalize class totals (`reweight` = p/(1−p)). The spec ("POT/2", "MC POT/2") does not say which roles change. For SM, halving `mc_pot` globally would double the background template. That is harmless only if the purity is computed before masking, which the spec implies but does not bind. | Driver lines cited. | State, per stream, the exposure used for (a) signal-MC scaling, (b) background/purity (full exposure, pre-mask), (c) completeness (c ≡ 1 from masked `mc_signal_reco` truth) and (d) the final division. Add each to the equivalence test. |
| N5 | MINOR | `design_arith.json` `costs.XR_stage_T.admitted_range` | The field is [63.2, 292.9]: it still adds the 50 exact replicas. The report quotes 15.3–227.8 (universe unfolds only), consistent with removing the statistical arm. JSON and report disagree on a field the report says it quotes from. | `design_arith.py` `costs()` still sums `t_boot` into `admitted_range`. | Drop `boot50` from the range, or rename the field. |
| N6 | MINOR | §10 outcome table | X1 uses today's driver; the `d1bc8813` driver has no `--seed` option (A P01). In the "X0 fail, X0′ pass" case, X1 says nothing about seed dependence of the pinned E_C-era path, yet the row says "X remains possible, pinned to `d1bc8813`". | A `pairings.tsv` P01: "driver has no backend/seed option". | In that row, say that `P09b` for the pinned path stays open. |
| N7 | NOTE | §3.4 | "Every run of either driver therefore imports that checkout's helper." This holds only because `_OF_PY` is not already on `sys.path` (the insert is conditional) and no other `omnifold` module precedes it. `omnifold_nn/omnifold/` exists in the repo. | Driver lines 1720–1722; `git ls-files`. | Treat the guard inventory's resolved origin as the evidence, which the manifest already records. |

## Numbers reproduced (my code, `review-scratch/repro3.py`, from the committed operands and speed `costs.json`)

| quantity | report | mine | match |
|---|---|---|---|
| declared family: m, R = M, accept | 472, 540, 0.168 | 472, 540, 0.16765 | yes |
| per-cell F (m = 32) | (JSON) 401, 0.1588 | 401, 0.15876 | yes |
| regional sized R = M; P(all four FAITHFUL \| κ = 1) | 239; 0.95 | 239; 0.9503 | yes |
| regional κ = 0.63: P(FAIL-low), F / rest | ≥ 0.995 | 0.9950 / 0.99997 | yes |
| regional κ = 0.8 and 1.25: P(FAITHFUL), INCONCLUSIVE | 0.006, 0.988 | 0.0062, 0.9875 | yes |
| regional at R = 100: P(all four) | 0.13 | 0.1335 (0.996 with n_eff 10/20) | yes |
| stage-T T-stat P(FAITHFUL \| κ = 1), F / rest | 0.43 / 0.84 | 0.4323 / 0.8354 | yes |
| family F GlobalIDs (0-based, pT·16 + p∥) | [1, 2, 11, 13, 14, 15, 31, 47, 63, 79, 95, 111, 143, 159, 179, 216] | identical, 16 cells | yes |
| nonrep share: median / p84 / cells with s ≥ 1 | 2.5 % / 6.3 % / 1 | 0.02515 / 0.06277 / 1 | yes |
| inflation 1/√(1−s) − 1, median / p84 | 1.27 % / 3.25 % | 1.2736 % / 3.2468 % | yes |
| XR expected subtotal; hard cap; full-node figure | 2.83; 6.375; 58.1 | 2.8339; 6.375; 58.05 | yes |
| L42 complete, declared (3,240 runs) | 303 – 1,131 | 302.9 – 1,130.8 | yes |
| L42 complete, regional (1,434 runs) | 149 – 570 | 149.4 – 570.0 | yes |
| X matched; with packed replicas | 467 – 11,005; 1,052 – 2,964 | 467.5 – 11,005.4; 1,052.1 – 2,964.3 | yes |
| X complete, declared / regional | 3,576 – 101,147 / 1,848 – 51,011 | 3,576.4 – 101,147.1 / 1,847.6 – 51,010.9 | yes |
| X / L42 ratio | 11.8–89× | 11.81–89.45 (declared); 12.36–89.49 (regional) | yes |
| stage T (16 universe unfolds) | 15.3 – 227.8 | 15.34 – 227.84 | yes (the JSON field differs, N5) |
| fallbacks: band on universe file; 10-seed exact scan | 305.1; 9.6 / 13.0 | 305.11; 9.573 / 13.013 | yes |
| storage, declared tier | ≈ 0.19 GB | 3,240 × 55.5 KB = 0.18 GB (0.194 at 0.06 MB/run) | yes |
| E_C vs CV42 median relative | 0.99 % | 0.9928 % | yes |

## Not verified, and why

- **Behaviour on the cluster.** Whether `--mem 24G` at `-c 2` finishes a single-threaded exact unfold within 30 h. Whether the `d1bc8813` blob runs end to end against today's helper and the renamed input files (A P01 records the `MEHFC` names, with content identical). Whether today's driver refuses to overwrite an existing output. Nothing was run on the cluster; these are N2-adjacent and belong in XR's own preflight.
- **The `--data-split` / `--mc-split` implementation.** It does not exist yet. N3 and N4 are about its specification, not its behaviour.
- **Helper drift between `d1bc8813` and today.** The record relies on A's static argument; I did not re-derive it. The helper has three later commits, including `541dd48c` "WIP: pre-shutdown snapshot", and its `omnifold()` signature is backward-compatible.
- **The remaining 95 lines of `review/review.md`.** Compared by reading, not by byte diff (see header).
