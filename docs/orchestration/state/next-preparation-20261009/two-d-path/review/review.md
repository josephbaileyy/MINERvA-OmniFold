# Independent review: two-d-path design record (initial review)

| field | value |
|---|---|
| Reviewer | Claude Opus 5.5 (`claude-opus-5-5`), Claude Code subagent, read-only. I did not author the record. |
| Fixed commit | `ebcba79cbeb89bb7416c006d5c082b683b897c49` (branch `prep/two-d-publication-path-20261009`, base `a16d5786`) |
| Object | `docs/orchestration/state/next-preparation-20261009/two-d-path/` at that commit |
| Start / end (UTC) | 2026-10-10T05:17:32Z / 2026-10-10T05:32:45Z |
| Worktree | detached at `ebcba79c` under the scratchpad. `git status --porcelain --untracked-files=all` was empty (0 lines) at start and at end. Removed with `git worktree remove`. |
| Resources | local CPU well under 0.01 core-h (numpy/scipy, `OMP_NUM_THREADS=2`). Scratch 32 KB (`review-scratch/repro.py`, `repro2.py`, `regen.json`). No cluster access: the optional login-node spot-check was not used. No jobs, no GPU, no training. |
| Owner tools run afterwards, for comparison only | `design_arith.py --self-test` PASS. A regenerated `design_arith.json` written to scratch is identical to the committed one. |

## Verdict

**FAIL.** All of the record's arithmetic reproduces. But both of its PASS dispositions, "L42 complete for the declared claims" and "XR preregistration-ready", rest on defects:
- the split-sample width test is confounded as specified (F2);
- the criteria family does not match the claim family (F3);
- the regional-tier assurance is stated at the wrong level (F4);
- stage T would false-fail about half the time even if the transfer were perfect (F5);
- one XR outcome retires route X on a confounded result (F6);
- the XR authorization is mischaracterized and under-capped (F7, F8);
- the §3.6 interpretation contradicts the record's own §3.3 and omits a known input change (F1).

All of these can be repaired in one batch. None needs new compute.

## Findings

| id | severity | location | finding | evidence / reproduction | repair required |
|---|---|---|---|---|---|
| F1 | MATERIAL | §3.6; §5 "training randomness"; §11.2; §11.3; `design_arith.py` `pair_structure` docstring | The reading of the 36 non-reproducing pair bands as "a fresh estimator perturbation per run … internal randomness inside `C_U` that `C_ML` counts again" ("a measured double count", §5) goes beyond what the evidence supports, for four reasons. **(i) It contradicts §3.3/§11.3.** By the record's own mechanism, weight-only universe runs at fixed seed 42 share bin mappers, and LightGBM is deterministic (L5, L6 = 0). So the identified mechanism gives no per-run randomness. Non-reproducibility across sweeps is a deterministic response to different inputs, not seed noise. **(ii) The sweeps differ by more than background treatment.** The universe omnifile was regenerated after the adopted sweep ran. §3.1 compared only CV-level columns; universe-weight columns were never compared. **(iii) The noise estimate is incoherent.** In one cell it exceeds that cell's whole total variance. `sqrt(1+s)−1` treats noise as an addition to a total that already contains it. **(iv)** The double count against `C_ML` is asserted, not measured. | (ii) `operands/remote_reduce_pn.json` `file_stamps`: universe file mtime 2026-07-08T15:08Z; the adopted sweep's `MaRES_0` is dated 2026-05-27. `2d-unfolding/HANDOFF_bkg_negweight/run_negweight_covariance_analysis.sh:11-14` says the July rebuild was "on the freshly regenerated … omnifile" and that the comparison quantifies "the Jul-04 event-loop binary drift". (iii) My code: s = noise/σ_tot² has median 0.0252, p84 0.0628, max **1.087** at reported index 126, cell (7,14). There the noise is **5.5×** Σh² of the 36 bands. The correct inflation, 1/√(1−s)−1, gives median 1.27 %, p84 3.25 %, and is undefined at the max. The quoted "max 44 %" is not a bound. | Restate as "cross-sweep non-reproducibility of the pair deltas, confounded by background treatment, the July file regeneration and the driver revision; mechanism unknown". Remove "internal randomness", "C_ML counts again" and "measured double count" from §3.6, §5, §11.2 and §11.3. Drop the max, or report it as unbounded. Either compare universe-weight column digests or state them unverified. Carry the same confound into §3.5/§5's 1.021 σ_U ratio, which is used as the validation of the background model. |
| F2 | MATERIAL | §6 alternative 1 (SD/SM); §8 W-regional and W-cell | As described, the split-sample test compares a quantity that contains the seed (binning-sample) term against a fixed-seed bootstrap that excludes it. If the halves drop rows, LightGBM's 200,000-row bin sample changes per half. That is the same mechanism as a seed change (§3.3 L1–L4). So (U_A−U_B)²/2 includes `C_ML`-type variance, while the fixed-seed Poisson bootstrap does not (§3.3 L4). Separately, "fixed purity" does not say whether the full-sample or the per-half purity is used. A per-half purity makes κ̂ absorb 1/p. | Using full-size σ_ML²/σ_S² as a proxy, the expected bias κ̂ ≈ √(1+σ_ML²/σ_S²) is: median 1.010 and max 1.084 in the 15-cell family; median 1.035 in the 190-cell region; max 1.236 overall. That max (ln 0.212) exceeds the 205-cell acceptance of 0.167 in 3 cells. This agrees with A §2.4 item 4 (σ_ML/σ_S median 0.26, max 0.73). The purity median is 0.975 (A §2.3), so a per-half purity would give κ̂ ≈ 1.026 at the median and more in low-purity bins. | Specify `--data-split`/`--mc-split` as 0/1 weight masks on retained rows, so bin mappers are unchanged, and verify this with a bin-mapper digest. Otherwise add the seed term to the reference. State that both halves use the full-sample purity. |
| F3 | MATERIAL | §2 K1/K2; §8; §15 L42 row | The claim family and the validated family differ. K1 claims per-cell widths for 205 cells plus the integral; K2 claims the projections. The headline-priced regional tier tests 2 regional medians × 2 streams; the optional tier tests 15 cells × 2 streams. The integral has no width criterion (§13, "not measured"). K2's "validity inherited from K1" needs off-diagonal calibration, which per-cell diagonal tests do not supply. The PASS price (79–314) is for the tier that does not test the per-cell claim, which is the "reduce the claim to make validation cheap" pattern. | `design_arith.json` `split_sample.per_cell_all_205`: R = M = 535, m = 410. It is not priced. With 16 extra unfolds plus 3,210 SD/SM runs I estimate ≈ 301 (opt) to ≈ 1,124 (cons) admitted for L42. Including the integral and the 30 projections raises m to ≥ 472. | Either narrow K1/K2 explicitly to regional-median stat-width calibration and flag that as Joseph's decision, or adopt and price a tier over the declared family (205 + 1 + 30). |
| F4 | MATERIAL | §8 W-regional assurance column | The assurance is reported only as a 95 % half-width. The rule itself declares four tests at Bonferroni 0.0125. n_eff = 20 is impossible for a 15-cell region. No pass, inconclusive or fail probabilities are given, and the procedure for the "95 % interval of the median κ̂" is not specified. | My code: at the declared level with n_eff = 5, the half-width is 0.141. P(FAITHFUL \| κ = 1) per test is 0.853, and P(all four) is **0.53**. At 95 %: 0.953 per test, 0.825 for all four. Holding 0.975 per test needs R = M ≈ 145, which is about +25 % on the regional-opt price. | Compute the verdict probabilities at κ = 1, at the edges, and at the KI-85 size, all at the declared level. Size R = M from them. Cap n_eff at the region size. Specify the interval construction. |
| F5 | MATERIAL | §10 XR stage T tolerance | The η rule (max \|η\| ≤ 0.05, median ≤ 0.02) has no assurance. Even with a perfect transfer, the 50-replica noise in the top-f_s cell triggers it. | 4,000 simulated draws, stat replacement only, true ratio 1, 50 vs 300 replicas, f_s from the operands: P(max \|η\| > 0.05) = **0.48**. This is driven by the f_s = 0.574 cell, where sd(ln r̂) ≈ 0.109. | Before freezing, size the replicas or restrict η to the components it can resolve, and report the false-fail probability and the power. |
| F6 | MATERIAL | §10 outcome table | **(a)** The "X0 fail" row declares route X FAIL. But X0 runs today's driver (≥ `355174fe`), not the one `E_C` ran on. A failure cannot separate code drift from environment drift. This branch gets no diagnosis step, while the L0-fail row does. **(b)** There is no row for "L0 pass, L1 fail", so as tabled L1 changes no decision. | `E_C` was written 2026-05-19T15:15Z. `baa0a76f` (the estimator port) is 21:38Z the same day. Nine driver commits follow, including `983e3568` (flux 1/Φ normalization) and `cf8a4a67` (bkg-mode refactor). | Add an X0′ at the `E_C`-era revision (`d1bc8813`, or whichever revision the evidence pins). Or relabel the outcome "not reproducible by today's driver" and keep X INCONCLUSIVE pending diagnosis. Add the L1 row, or drop L1. |
| F7 | MATERIAL | §10 "Why this one"; Remaining authorization | "It is a reproduction, not a transfer measurement" is inaccurate for X1. X1 (exact backend `--seed 1` against `random_state=None`) is a one-seed instance of `P09b`. The governing records list `P09b` as part of option (b) "Measure the transfer", which the 2026-10-09 ruling prohibits. | DELIVERY §6 option (b) lists "`P03` … `P05` … and `P09b` (exact seed scan)". Speed `results/costs.json` lists it under `procedures.exact_transfer_measurement`. Speed REPORT:48 also lists `P09b`. The record does already ask Joseph for an explicit statement. | Name X1 as `P09b` (one seed), and ask Joseph to authorize that specifically against the transfer-measurement prohibition. |
| F8 | MATERIAL | §10 Remaining authorization; §8 missing results; §9 XR row | The ≤ 3.0 node-h cap covers exactly the four jobs (hard cap 2.9375). The admitted 2.77 includes a 5 % retry and a 10 % verification rerun, which cannot be realized as fractions of a 19 h exact job. §8 allows up to 3 reruns. The wall time of a single-threaded exact unfold at `-c 2` on the shared QOS is unmeasured (19.3 h was measured on a full node; the job limit is 26 h). | One exact rerun brings the cap to 4.16 (+41 %). Three reruns of each X job bring it to 10.25. | Raise the request to include at least one exact rerun (≈ 4.2), or declare "no rerun; a missing comparison is INCONCLUSIVE" and drop the overhead from the admitted figure. |
| F9 | MATERIAL (price > 10 %; no disposition changes) | §10 table; §4/§9 X cons | Several prices are quoted outside §9's own convention. "≈ 212 node-h" is the raw 300 × 0.7075. "≈ 6.7 node-h" is the raw packed figure. X_matched cons (2,964) uses packed exact replicas, while X complete cons uses the as-run rate. | Under the convention: 305.1 admitted instead of 212 (+44 %). 9.57 (packed) or 13.0 (the mem24G billing XR itself uses) instead of 6.7. X_matched cons with as-run replicas would be 11,005. | Quote every price as admitted under one convention, and use the same replica rate in both X conservative figures. |
| F10 | MINOR | §3.7 | The "KI-85-sized error" uses κ = 1.6, i.e. a band that is too narrow. KI-85 says the data-stream band is ≈ 1.6× too **wide** (κ ≈ 0.63). | `KNOWN_ISSUES.md` row 85. `mappings.total_sigma_ratio_if_stat_kappa_0.63` gives 2 cells > 5 %, not 11. The figure would be smaller still for the data stream alone. | Use κ ≈ 0.63, i.e. 2 cells. The conclusion only gets stronger. |
| F11 | MINOR | §4 table | "9–32 min" wall per L42 unfold is neither in an operand nor reproducible. "Median 0.99 % per bin" is correct but is not a field of the JSON, although the script's docstring says every figure is one. | Measured walls: 14.2 min (shared 64), 13.0 min (full node), 42.5 min (universe file). My value for the median: 0.993 %. | Source both figures or correct them. Add the 0.99 % to the JSON. |
| F12 | MINOR | §8 usefulness | "(pass)" overstates. The successor's §5 defines the half-width as (upper − lower)/2 with B counted, and B± is not computed. The record silently uses a half-width from σ_tot alone. | PROPOSAL-20261005 §5, "Width/usefulness". | Report INCONCLUSIVE until B± and the integral exist, or declare the changed definition. |
| F13 | MINOR | §8; §4 | The 15-cell family is computed from the seed-1 VL170 band and the adopted σ_U. With pn σ_U it is 16 cells, and the new seed-42 band will change f_s again. §4 also leaves the systematic sweep open ("`purity_newomni` or the adopted"). | My code: 15 cells (adopted) vs 16 (pn). Ordinal indices of the 15: [2, 11, 13, 14, 15, 31, 47, 63, 79, 95, 111, 143, 158, 173, 197]. | Freeze the GlobalID list and the choice of sweep now. |
| F14 | MINOR | §10 Runs | `nd-unfolding/mnv_guarded_run.py --require-provenance` is not a valid flag. The manifest is not runnable as written. | The guard's arguments are `--expect-root` (required), `--allow`, `--inventory`, `--label`. `--require-provenance` belongs to `fixed_truth_toy.py` and `ki85_compare.py`. | Give the exact launch command. |
| F15 | MINOR | §8 | Item 6 lists accuracy, and successor §5 has a bias criterion, but §8 has no accuracy row. | NO UNTOUCHED VALIDATION DOMAIN (§7) covers it, but §8 does not say so. | Add an accuracy row that states the NO-GO and its reason. |
| F16 | MINOR | §7; §15 empirical-coverage row | "A linearity test is what remains, and it is measured at zero compute" goes beyond the evidence. A is measured for the 42 pair bands only and has no criterion (§8 says "reported beside"). There is nothing for Flux or the multi-universe bands. | — | Say this is a measurement for the pair bands only, with no pass/fail rule. |
| F17 | MINOR | §2 seed row; §4; §11.3 | "The seed acts only through the binning sample" is stated without qualification. The evidence is synthetic (§3.3, §13). | — | Qualify it as "synthetic evidence" wherever it is used as a premise. |
| F18 | NOTE | §7; `log_ratio_se` | The self-test simulates iid χ², which is the formula's own assumption, so it cannot test the exchangeable-splits premise that §7 raises. The split term's kurtosis factor (1 + γ/2) should be (1 + γ/4) for a half-difference; this is conservative and negligible (SE 0.05032 vs 0.05040). Per-cell kurtosis in the 15 cells ranges −0.44 to 1.78, but from 100 toys (SE ≈ 0.5). | — | Describe the self-test as an arithmetic check only. |
| F19 | NOTE | §9 L42/X complete | C's S-b already includes "then 10 lateral unfolds", and the route totals add 10 more. | C `costs.json` S-b `what` field. The extra cost is ≈ 2.5–3.1 node-h for L42. | Remove the duplicate. |
| F20 | NOTE | §3.6 Rvn1pi/Rvp1pi | The two bands are equal in both sweeps, not only in the July sweep. | Maximum h-ratio deviation: 2.6e-9 (pn), 1.4e-9 (adopted). | Correct the sentence. |
| F21 | NOTE | §6 | The extrapolation from half size to full size is stated only for the MC stream. It applies equally to the data stream. | — | State it for both streams. |
| F22 | NOTE | `design_arith.json` `CV42_vs_seedscan_z` | rms 1.28 and max 4.25 are computed but not discussed. This bears on whether `C_ML` from seeds 1–10 describes seed 42. | — | Disclose it. Also state that seed 42 was chosen by matching cost (L1 68–191 vs 25–93), not by central values. On my reading the choice is not outcome-driven. |
| F23 | NOTE | Data hygiene | Clean. The operands hold only column digests, entry counts (data 4,119,797, already public in `VALIDATION_LEDGER.md:1524` and elsewhere), unfolded results, and MC-background ratios. The 4,091,707 in §6 comes from A §2.3. | Key scan of all four operand files. | None. |

## Numbers reproduced (my code, from the committed operands and the speed and C JSONs)

| quantity | report | mine | match |
|---|---|---|---|
| f_s median / p90 / max | 0.0084 / 0.042 / 0.585 | 0.00845 / 0.04212 / 0.58493 | yes |
| cells with f_s ≥ 0.05 / ≥ 0.1 | 15 / 5 | 15 / 5 (16 with pn σ_U) | yes |
| `C_ML` share median | 0.0006 | 0.00061 | yes |
| E_C − CV42 in σ_tot, median / max | 0.136 / 1.46 | 0.1356 / 1.4590 | yes |
| seed1 − CV42 in σ_tot, median / max | 0.026 / 0.14 | 0.0259 / 0.1437 | yes |
| pn CV vs CV42, max relative | 1.4e-11 | 1.424e-11 | yes |
| E_C vs CV42, median relative | 0.99 % | 0.993 % | yes (not a field) |
| σ_U(pn)/σ_U(adopted) p16 / p50 / p84 / range | 0.985 / 1.021 / 1.055 / 0.70–1.20 | 0.9852 / 1.0209 / 1.0552 / 0.6955–1.1977 | yes |
| median σ_tot, pn / adopted | 6.94 % / 6.87 % | 6.937 / 6.871 | yes |
| p90 σ_tot | 11.6–11.9 % | 11.57 / 11.89 | yes |
| bands with reproducible A (≥ 0.75) | 6 (names) | 6, same names | yes |
| A corr range in the 36 bands; median h corr | −0.08 to 0.72; 0.60 | −0.0764 to 0.7195; 0.603 | yes |
| h corr of the dominant bands | 0.983 / 0.997 / 0.972 | 0.983 / 0.997 / 0.972 | yes |
| omitted displacement / σ_tot, median / p84 / max | 0.13 / 0.26 / 0.63 | 0.1304 / 0.2613 / 0.6347 | yes |
| quadrature addition, median / max | 0.85 % / 18 % | 0.847 % / 18.44 % | yes |
| noise inflation, median / p84 / max | 1.25 % / 3.1 % / 44 % | 1.250 % / 3.091 % / 44.47 % with the record's formula; correct formula gives 1.27 % / 3.25 % / undefined | arithmetic yes, formula no (F1) |
| stage-T tested share, median / min | 86 % / 24 % | 0.8613 / 0.2398 | yes |
| KI-85 mapping, κ_s = 1.6 → cells > 5 % | 11 | 11 (κ = 0.63 gives 2) | yes; wrong direction (F10) |
| κ at 0.63 (I68) / 0.92 (I95) | 1.116 / 1.120 | 1.11548 / 1.11954 | yes |
| coverage at κ = 0.8 and 1.25 | I68 0.789 → 0.576; I95 0.986 → 0.883 | 0.7887 / 0.5763; 0.9857 / 0.8831 | yes |
| stage-T bounds at κ = 0.95–1.05 | 0.659–0.707; 0.938–0.961 | 0.6591–0.7075; 0.9380–0.9609 | yes |
| W-cell, 15 × 2 streams | R = M = 399, accept 0.158 | 399, 0.15844, z_α 3.144 | yes |
| W-cell, 205 × 2 streams | R = M = 535 | 535, accept 0.1672 | yes |
| regional half-width at R = M = 100 (n_eff 20 / 5) | 0.055 / 0.111 | 0.0554 / 0.1108 (at 95 %; 0.0706 / 0.1412 at the declared Bonferroni level) | yes; level mismatch (F4) |
| toy kurtosis median | 0.02 | 0.0241 | yes |
| XR admitted (mem24G / packed / full node) | 2.77 / 2.08 / 55.7 | 2.7725 / 2.0845 / 55.69 | yes |
| XR cap by job limits | 2.94 | 2.9375 | yes |
| L42 band | 25.5–93.2 | 25.49 / 93.15 | yes |
| L1 sweep | 67.6–191.2 | 67.64 / 191.20 | yes |
| L42 complete, regional / per-cell | 79–314 / 232–871 | 79.44–314.17 / 231.86–871.20 | yes |
| X matched | 467–2,964 | 467.47 / 2,964.31 | yes (inconsistent cons basis, F9) |
| X complete, regional / per-cell | 1,059–28,136 / 2,776–77,939 | 1,058.8–28,135.9 / 2,776.1–77,939.0 | yes |
| X/L42 ratio | 13–90× | 13.3× / 89.6× | yes |
| stage T | 63–276 | 63.21 / 275.70 | yes |
| X sweep under SB1 | 180 / 765–2,677 | 180.29 / 764.89 / 2,677.13 | yes |
| SD/SM run counts | 600 / 2,394 | 600 / 2,394 | yes |
| storage | ≤ 0.15 GB | 2,394 × 55.5 KB ≈ 0.133 GB | yes |
| reserve convention | T/0.8 with ×1.15 inside | confirmed in my code (subtotal × 1.15 / 0.8) | yes |
| "≈ 212" / "≈ 6.7" | as quoted | raw 212.25 / 6.66; admitted 305.1 / 9.57–13.0 | raw yes, convention no (F9) |
| thread envelope | ≤ 5.8e-9, median 1.3e-12 | 5.828e-9 / 1.31e-12 (`compare_full.json`) | yes |

## Source-fidelity spot checks (all at `a16d5786`)

| claim in the record | source | result |
|---|---|---|
| normalization constants and `hFlux_pt` | A §2.2 | matches |
| 4,091,707 in-phase-space data rows; purity median 0.975 | A §2.3 | matches |
| `P06`/`P07`/`P09b` content | A §3 table | matches; the classification of `P09b` is in F7 |
| [0.80, 1.25] tolerance; B's zero-disjoint count | B §9, §1 ground 1 | matches; the count is correctly scoped |
| S-b 1.3/23.8; Audit 1 at 1.4 %; C03/C05a/C06/C10/X01 | C §3, §5; `c/costs.json` | matches (S-b double count in F19) |
| P1 0.29–1.21 M; SB1 1.3, cap 2.0; balance 3,040.6; RSS 65–187 GB | speed `costs.json`, REPORT:22 | matches |
| ruling prohibitions | closeout §11 | matches; X1 characterization in F7 |
| KI-91 Pearson 0.96; KI-85 at 1.6× | `KNOWN_ISSUES.md` 91, 85 | 91 matches; 85's direction is reversed (F10) |
| Phase 18.2: 133 + 7 duplicates; c = 1; 205/224 paper bins | STATUS:219-221, 229-243 | matches |
| successor §5 usefulness thresholds | PROPOSAL §5 | thresholds match; the half-width definition differs (F12) |

## Not verified, and why

- **Whether the universe-weight columns differ between the May and July universe files.** The May file is not available. The confound in F1 rests on file mtimes and a tracked script comment, not on a digest comparison.
- **The cluster facts behind the operands** (e.g. that `purity_newomni` hXSec2D equals CV42's). I checked these only in the committed operand arrays (1.42e-11), not against the cluster files. I judged no single spot-check decisive for the findings above.
- **`seed_mechanism_check.py`.** I did not re-run it: LightGBM is not installed locally. I read the script and the logic of its checks.
- **sklearn tie-breaking at production scale, and the wall time and contention of a single-threaded exact unfold on the shared QOS.** Both are unmeasured anywhere.
