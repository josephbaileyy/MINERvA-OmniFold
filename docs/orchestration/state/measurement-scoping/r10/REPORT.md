# R10 report: more reconstructed information on D-ID's binned setting (2026-10-24)

**By** the validation lane, for the director. This report records the result of [`DECLARATION.md`](DECLARATION.md), as
bound in [`BINDING.md`](BINDING.md) and amended in [`BINDING-AMENDMENT-1.md`](BINDING-AMENDMENT-1.md). The rule was
fixed before any output (DECLARATION §1) and was applied unchanged by `r10.py` `verdict` at the bound commit
`289a1ff755fe8c21aeef4f19aebe559cf7849bc1`.

**CITABLE FOR:**
- R10's verdict under the frozen rule, each configuration's state, and the numbers behind them;
- the descriptive readouts the declaration lists without a rule (the same role, the E_ν < 20 GeV GiBUU and nominal
  readout);
- the run's controls, compute, products and extraction join, including the duplicate count.

**NOT CITABLE FOR:**
- a STOP. R10 did not reach STOP, so DESIGN §9's stop condition is not met by this report;
- a PASS, or a GBDT run with the added features;
- any coverage or interval statement, or a statement about an unbinned estimator;
- any change to a claim. Claims are Joseph's.

All numbers come from [`outputs/r10_results.json`](outputs/r10_results.json) unless another source is named. Every
figure is a split-half figure at K = 5 on the J group (109 functionals) unless marked otherwise. **(inference)** marks a
reading beyond the rule.

## 1. Verdict: INCOMPLETE

**No configuration passes.** Of the 11 decisive configurations, none is PASS, 5 are FAIL and 6 are UNDETERMINED. There
is therefore no passing configuration to name with its twin, and no single narrow pass.

R10 is **INCOMPLETE** for two reasons, each sufficient under the rule on its own:
1. **The global null failed** (DECLARATION §4.3). `null3@f1`, a seeded uniform three-way split of every f = 1 cell,
   narrowed the J T2 width median from 0.2362 to 0.1467, a change of 0.0896 against a band of 0.0347. Its four
   residuals stayed inside their bands. The change is 2.6 × the band, not a near miss. **(inference)** It is the
   failure mode the declaration stated before the result (§4.3: "a null split can only narrow the widths").
2. **Six configurations are UNDETERMINED:** f2, f4 and C1–C4 at f = 2. Each one's null twin satisfies leg A, so the
   instrument reads noise as information at that occupancy. STOP needs every configuration to FAIL.

The verdict authorizes nothing. It is not a STOP and it is not a PASS.

## 2. How the rule reads each configuration

**The thresholds** (f = 1, split role):
- **Leg A**, width: J T2 width median ≤ 10% and p90 ≤ 25%, or median ≤ ½ × 0.2362 = **0.1181**.
- **Leg B**, residual: J median |r(5)| ≤ ⅔ × f = 1 at three or more of the four departures. The f = 1 values are GiBUU
  0.0862, W1 0.0507, W2 0.0089, W3 0.0523, so the cuts are 0.0574, 0.0338, 0.0059 and 0.0348.
- **The p90 clause cannot be met here.** The J T2 p90 is +∞ in every configuration and every twin: 13–15 of the 109
  J functionals have an infinite or non-finite width (an acceptance hole or a NaN, both counted as +∞), more than the 10% a finite p90 allows. Leg A is decided by
  the halving clause alone.

**Per configuration.** Ratios are X over f = 1 and X over its twin X̃, from `verdict` `per_config` `margin`. A ratio
below 1 means X is narrower, or has the smaller residual.

| X | state | leg A | leg B departures | X̃ leg A | width X/f1 | width X/X̃ | X̃ width/f1 | GiBUU X/f1 | W1 X/f1 | W2 X/f1 | W3 X/f1 | GiBUU X/X̃ | W1 X/X̃ | W2 X/X̃ | W3 X/X̃ |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| f2 | UNDETERMINED | yes | 0 | yes | 0.363 | 0.988 | 0.367 | 1.011 | 1.173 | 1.047 | 0.908 | 1.032 | 1.110 | 0.882 | 0.937 |
| f4 | UNDETERMINED | yes | 0 | yes | 0.135 | 0.984 | 0.137 | 0.990 | 1.324 | 2.992 | 1.194 | 1.001 | 1.070 | 1.112 | 0.960 |
| C1@f1 | FAIL | no | 0 | no | 0.648 | 0.963 | 0.674 | 0.920 | 0.963 | 1.106 | 0.937 | 0.920 | 0.968 | 1.127 | 0.976 |
| C2@f1 | FAIL | no | 0 | no | 0.600 | 0.952 | 0.631 | 0.996 | 0.975 | 0.987 | 0.906 | 1.018 | 0.967 | 0.911 | 0.954 |
| C3@f1 | FAIL | no | 0 | no | 0.717 | 0.933 | 0.769 | 0.984 | 0.995 | 0.983 | 0.987 | 0.994 | 0.993 | 0.931 | 1.054 |
| C4@f1 | FAIL | no | 0 | no | 0.589 | 0.909 | 0.647 | 0.899 | 0.958 | 0.987 | 0.953 | 0.927 | 0.947 | 0.916 | 1.049 |
| C1@f2 | UNDETERMINED | yes | 0 | yes | 0.264 | 0.936 | 0.282 | 0.997 | 1.190 | 1.485 | 0.766 | 1.030 | 1.137 | 0.984 | 0.888 |
| C2@f2 | UNDETERMINED | yes | 0 | yes | 0.237 | 0.947 | 0.250 | 0.993 | 1.152 | 1.558 | 0.924 | 1.026 | 1.113 | 1.086 | 1.042 |
| C3@f2 | UNDETERMINED | yes | 0 | yes | 0.289 | 0.998 | 0.290 | 1.043 | 1.065 | 1.306 | 0.843 | 1.046 | 0.988 | 0.858 | 0.915 |
| C4@f2 | UNDETERMINED | yes | 0 | yes | 0.244 | 0.974 | 0.251 | 0.882 | 1.180 | 1.272 | 0.919 | 0.956 | 1.199 | 0.834 | 1.045 |
| C2xC3@f1 | FAIL | yes | 0 | no | 0.469 | 0.913 | 0.514 | 0.978 | 0.947 | 1.017 | 0.917 | 1.004 | 0.973 | 0.873 | 0.940 |

- **Every twin's leg B count is 0**, so twins make configurations UNDETERMINED only through leg A.
- **C2xC3@f1** is the one configuration that meets leg A while its twin does not: X 0.1109, X̃ 0.1214, against the
  0.1181 cut. It FAILs on leg B, at 0 departures.
- **The closest approach to leg B's cut of 0.667** is C1@f2 at W3, 0.766. Its twin reaches 0.862 at W3. No
  configuration reaches the cut at any departure.

**The global null** (`verdict` `global_null`). The band is max(2 × |split − swap|, 1% × |split|) at f = 1.

| quantity | f1 split | f1 swap | band | `null3@f1` | \|null − split\| | within |
|---|---:|---:|---:|---:|---:|---|
| J T2 width median | 0.2362 | 0.2189 | 0.0347 | 0.1467 | 0.0896 | **no** |
| J median \|r(5)\|, GiBUU | 0.0862 | 0.0822 | 0.0080 | 0.0860 | 0.0002 | yes |
| W1 | 0.0507 | 0.0595 | 0.0176 | 0.0505 | 0.0002 | yes |
| W2 | 0.0089 | 0.0074 | 0.0030 | 0.0080 | 0.0009 | yes |
| W3 | 0.0523 | 0.0536 | 0.0026 | 0.0500 | 0.0022 | yes |

## 3. What the numbers say (inference)

These readings go beyond the rule. They change no state and no verdict.

- **Leg B alone excludes a PASS.** A PASS needs leg B at three or more departures, and every one of the 11
  configurations is at 0. So no configuration could have passed, whatever the global null or the twins had done. No
  split-role residual is cut by a third at any departure, at any recorded K (closest: C4@f1, GiBUU, K = 20, 0.669).
- **At fine binning the W2 residual sits at or near the split-half noise floor.** The nominal split-role residual measures
  split-half noise alone, with no departure. It grows with binning: f1 0.0044; f2 0.0060; C1–C4@f2 0.0067–0.0074;
  f4 0.0266 and its twin 0.0257. In f2, f4 and C1–C4@f2 that floor is already above W2's cut of 0.0059 (at f2 by only 0.7%: 0.00598 against
  0.00594). At f4, W2's
  residual (0.0267) equals the nominal floor (ratio 1.00), so its 2.99 × against f = 1 is noise, not a departure
  effect. At f2 and C1–C4@f2 the W2 residual is 1.56–1.90 × the floor: the noise is comparable, not dominant. GiBUU,
  W1 and W3 are well above the floor everywhere (at f4: floor 0.0266, GiBUU 0.0853, W1 0.0671, W3 0.0624). In all six
  f = 2 and f = 4 configurations both W1 and W2 grow against f = 1. Leg B's failure at W2 in these configurations
  therefore cannot be read as evidence about the added information.
  At f = 1 (C1–C4, C2 × C3) the floor is 0.0044–0.0055, and no departure is cut by a third there either.
- **The width gains are mostly occupancy.** Each configuration's width median is 0.909–0.998 × its own twin's, and the
  twins themselves narrow to 0.137–0.769 × f = 1. A null split at f = 1 alone narrows by 38%. The split-half Fisher
  width therefore reads finer binning as information whether or not the binning carries any, as DECLARATION §4.3
  argued from Cauchy–Schwarz. The margin over the twin (0.2–9%) is the part the twins do not explain, and the rule did
  not ask how large it must be.
- **Why INCOMPLETE and not STOP.** The configurations that FAIL are exactly those whose twin misses leg A. At f = 2
  and f = 4 every twin meets leg A by occupancy alone, so under this rule those six can only be UNDETERMINED. STOP was
  out of reach for them, independently of the added information.
- **What a decision would need.** Whether to treat this as DESIGN §9's stop condition, to change the instrument, or to
  leave R10 INCOMPLETE is the director's call. This report proposes no rule change.

## 4. Descriptive readouts (decide nothing)

**GiBUU restricted to E_ν < 20 GeV** (DECLARATION §6). 31,034,747 of the 32,849,103 rows have S1's `mc_incomingE`
below 20,000 MeV. Split role, J median |r(5)|, as a ratio to f = 1 within the same population; the full-population
ratio is beside it.

| config | GiBUU <20 GeV | GiBUU ratio to f1 (<20 GeV) | GiBUU ratio to f1 (full) | nominal <20 GeV | nominal ratio to f1 (<20 GeV) |
|---|---:|---:|---:|---:|---:|
| f1 | 0.0855 | 1.000 | 1.000 | 0.0044 | 1.000 |
| null3@f1 | 0.0855 | 1.000 | 0.998 | 0.0048 | 1.090 |
| f2 / f2~null | 0.0898 / 0.0876 | 1.050 / 1.024 | 1.011 / 0.980 | 0.0064 / 0.0056 | 1.461 / 1.265 |
| f4 / f4~null | 0.0860 / 0.0853 | 1.006 / 0.997 | 0.990 / 0.989 | 0.0256 / 0.0254 | 5.817 / 5.761 |
| C1@f1 / twin | 0.0789 / 0.0859 | 0.922 / 1.004 | 0.920 / 1.000 | 0.0050 / 0.0051 | 1.127 / 1.159 |
| C2@f1 / twin | 0.0840 / 0.0887 | 0.981 / 1.037 | 0.996 / 0.978 | 0.0046 / 0.0053 | 1.037 / 1.194 |
| C3@f1 / twin | 0.0853 / 0.0854 | 0.997 / 0.998 | 0.984 / 0.990 | 0.0046 / 0.0053 | 1.035 / 1.204 |
| C4@f1 / twin | 0.0772 / 0.0875 | 0.902 / 1.023 | 0.899 / 0.970 | 0.0044 / 0.0047 | 1.008 / 1.075 |
| C1@f2 / twin | 0.0893 / 0.0861 | 1.044 / 1.006 | 0.997 / 0.968 | 0.0055 / 0.0059 | 1.254 / 1.349 |
| C2@f2 / twin | 0.0884 / 0.0898 | 1.033 / 1.050 | 0.993 / 0.967 | 0.0071 / 0.0070 | 1.600 / 1.577 |
| C3@f2 / twin | 0.0909 / 0.0872 | 1.062 / 1.019 | 1.043 / 0.997 | 0.0071 / 0.0069 | 1.617 / 1.556 |
| C4@f2 / twin | 0.0839 / 0.0800 | 0.980 / 0.935 | 0.882 / 0.922 | 0.0064 / 0.0082 | 1.453 / 1.865 |
| C2xC3@f1 / twin | 0.0825 / 0.0881 | 0.964 / 1.030 | 0.978 / 0.974 | 0.0054 / 0.0052 | 1.225 / 1.191 |

**(inference)** Restricting GiBUU to its own energy range brings no residual near leg B's cut of 0.667. The lowest is
C4@f1, at 0.902. The nominal split-half floor grows with binning in the restricted population as in the full one.

**Other readouts in the results file:**
- the same role (everything from the full sample: f = 1 width median 0.2866, residuals equal to D-ID's);
- K = 1, 2, 3, 10, 20 and 200. **In the same role at K ≥ 10, many configurations are cut by more than a third at
  three or more departures, mostly together with their twins:** f4 and its twin at K = 10, 20 and 200 (f4 at K = 20:
  0.244, 0.256, 0.363, 0.523; its twin 0.259, 0.275, 0.361, 0.551), and all five f = 2 pairs at K = 200, in both X and twin. The
  exceptions run both ways: C4@f2 at K = 20 and C4@f1 at K = 200 are cut while their twins are not, and
  C2xC3@f1's twin is cut at K = 200 while C2xC3@f1 is not. **(inference)** The same role fits and tests on one
  sample, and the twins reproduce these cuts, so they read as occupancy and same-sample optimism. They enter no
  rule. No split-role residual is cut at any K;
- the EW and H2 groups and the T1 grid;
- finite-only width quantiles (`median_finite`, `p90_finite`) and the count of functionals at or below 10%
  (`n_le_10pct`).

**The sixth axis** (`variables`):

| variable | tertile edges | categories present | missing rows used | weight shares (bins 0, 1, 2, missing) |
|---|---|---|---:|---|
| C1 | 39, 110 | 0, 1, 2 | 0 | 0.335, 0.333, 0.332, 0 |
| C2 | 0.733, 0.956 | 0, 1, 2, 3 | 256 | 0.333, 0.333, 0.333, 7 × 10⁻⁶ |
| C3 | 1, 1 | 0, 2 | 0 | 0.812, 0, 0.188, 0 |
| C4 | 5, 14 | 0, 1, 2 | 0 | 0.372, 0.302, 0.326, 0 |

C3's two edges coincide at 1, so its middle bin is empty and it splits rows into ≤ 1 and > 1 tracked hadrons, as
DECLARATION §3 allows ("Ties stay together, so a bin may be empty").

## 5. Controls: all pass

- **K0** (rows): f = 1 equals D-ID's rows, and f = 2 and f = 4 hold the same rows on the grid.
- **K1** (D-ID reproduced): D-ID's committed T1 and T2 widths (183 functionals) and the K = 5 trajectory row are
  reproduced bitwise for all six weight sets. The six J medians are equal to D-ID's `results.json`.
- **K2** (generic path equals D-ID at f = 1): the split and same K = 5 residuals for all six weight sets, and the
  split and same widths at T1 and T2, bitwise.
- **Admission:** every check `r10.py` records (A1–A4, A7–A11) passes, including the event digest of `of_inputs_5d.npz`.
- **Twins:** every twin has the same number of occupied reco cells as its configuration (`n_reco_cells`). Exact
  per-cell occupancy is a property of `permuted_within`, tested synthetically (DECLARATION §5.5); it is not
  re-measured in the results file.
- **Controls-only, for the record:** run again at `289a1ff7` before X. Its controls and admission blocks are equal to
  the run at `b4b1136c`, and K1's J medians equal D-ID's committed values
  ([`receipts/controls-only-289a1ff7.json`](receipts/controls-only-289a1ff7.json),
  [`receipts/controls-only-b4b1136c.json`](receipts/controls-only-b4b1136c.json)).

**The extraction (X, job 60200309)** ([`receipts/r10_extract_receipt.json`](receipts/r10_extract_receipt.json)):
- All twelve playlists passed every admission control: row count, identity and truth equal to S1, truth bitwise equal
  to `MCgen`, and reco bitwise on the reco-passing rows. 32,849,103 rows were covered, `complete: true`.
- Every reco-passing row joined in every playlist, and the maximum vertex difference is 0.0 mm everywhere.
- **Duplicates:** the receipt counts 111 surplus reco-tree entries whose identity repeats another's within the same
  file (`duplicate_keys_within_file_all`, `r10_extract.py` `join_rows`), all in 1E, over the 51 files read there.
  The count is 0 in every other playlist, over the files its rows point to. The diagnosis of the first X
  ([`LEDGER-NOTES.md`](LEDGER-NOTES.md), [`BINDING-AMENDMENT-1.md`](BINDING-AMENDMENT-1.md)) places them in
  `MasterAnaDev_mc_AnaTuple_run00111353`.
- **Rows resolved by vertex: 1**, in 1E. **Unresolved: 0** in every playlist
  (`duplicated_rows_unresolved_by_vertex`). The amendment's condition for a complete extraction holds.
- **Guard:** the OI-136 loaded-checkout inventory shows one checkout root, the deploy at `289a1ff7`, with 4 modules
  ([`receipts/inventory/extract-60200309.jsonl`](receipts/inventory/extract-60200309.jsonl)). The guard's own line
  reads `verdict=EMPTY-REPOSITORY-ORIGIN-SET -- THE GUARD REFUSED NOTHING BECAUSE IT SAW NOTHING`, scoped to "THIS
  INTERPRETER ONLY" ([`receipts/task-extract-60200309.log`](receipts/task-extract-60200309.log)). It reads the same
  in X0 and the first X (their logs are on pscratch; see [`LEDGER-NOTES.md`](LEDGER-NOTES.md)):
  `r10_extract.py` imports no repository package, so the guard had nothing to refuse.

## 6. Compute

| job | where | wall | charge | against |
|---|---|---:|---:|---|
| X0 60195994 (debug) | Perlmutter | 148 s | 0.0411 CPU node-h | smoke, 1L |
| X 60196485 (regular) | Perlmutter | 1,320 s | 0.3667 CPU node-h | FAILED closed on 1E, exit 7 |
| X 60200309 (regular) | Perlmutter | 3,259 s | 0.9053 CPU node-h | 0.862 × the 3,781 s projection |
| controls-only, twice | local | 126 s, 123 s | 0 | — |
| Y | local | 1,953 s | 0 | 2,137 CPU-s = 0.59 core-h of the 16 cap (projected ≈ 3) |

- **Total: 1.3131 CPU node-h of the 4 granted.** No job passed 1.25 × its projection.
- **Y's memory:** peak RSS 4.92 GB against the 14 GiB cap (projected 9–11 GB). macOS reports a peak memory footprint
  of 9.26 GB ([`receipts/y-run.log`](receipts/y-run.log)).
- Every job is in [`LEDGER.tsv`](LEDGER.tsv), with the notes in [`LEDGER-NOTES.md`](LEDGER-NOTES.md). The sacct records
  are in [`receipts/`](receipts/).

## 7. Products

| product | sha256 |
|---|---|
| [`outputs/r10_results.json`](outputs/r10_results.json) | `dafcc55e6214fa655c33e9a2488e968a542ee958f86719559de50c3327277a49` |
| [`outputs/r10_tables.npz`](outputs/r10_tables.npz) | `a38f63327d302ac61307cde7d16b1abf83c829b8aedf901e49cb9ee0d779e491` |
| `r10_extra.npz`, on pscratch only (`/pscratch/sd/j/josephrb/r10-20261024/run2/extract/`), 2,365,138,466 bytes; the local copy Y read has the same size and sha256 ([`receipts/r10_extra.sha256.txt`](receipts/r10_extra.sha256.txt)) | `923e958a3def73bb44048052cac5ec933ae524b4fb66da052e22aa1fda63ae3d` |
| [`receipts/r10_extract_receipt.json`](receipts/r10_extract_receipt.json) | `3849b14373f9c5abb81593ed8873881c3b8a58b329768370216820c88200dec8` |
| [`receipts/inventory/extract-60200309.jsonl`](receipts/inventory/extract-60200309.jsonl) | `001e5669cd6c416ade862999de5414d40d32ac2f83a9991c0fcecce806ce164d` |

The code that produced them: `r10.py` sha256 `e2fedfcf…`, `config.json` `2366c41d…`, `r10_extract.py` `3b539d4a…`,
each recorded in its own receipt. Y ran in a detached worktree at `289a1ff7`, with no modified or untracked file
([`receipts/y-worktree-state.txt`](receipts/y-worktree-state.txt)). Every file in `receipts/` and `outputs/` is listed
in [`receipts/SHA256SUMS`](receipts/SHA256SUMS).

## 8. Review

An independent read-only reviewer checked this report against the results in both directions (nothing lost, nothing
strengthened): [`review-report.md`](review-report.md).
