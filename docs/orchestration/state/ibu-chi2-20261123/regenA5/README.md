# Regeneration A5: the eigenmode numbers of appC:7 and records_r03:18 on the paper's pT edges (2026-11-25)

**By** the `ibu-chi-squared-issue` session. It is part of the chain in [`../README.md`](../README.md). Requested by
journal-editor; scope and GO from the director.
- **Amendment:** [`AMENDMENT-A5.txt`](AMENDMENT-A5.txt), committed at c83be213 before any run.
- **Runner revision:** [`AMENDMENT-A5-runner-r1.txt`](AMENDMENT-A5-runner-r1.txt). A reorder, so that OLD's controls
  gate E.
- **Run:** once, with [`receipts/a5_run.sh`](receipts/a5_run.sh) r1 (ca84ffce) under the director's GO. Laptop, 0 node-h.
  Producer module W at 06893b0a, clean.

## Controls: all PASS

From [`out/prerun.txt`](out/prerun.txt), [`out/c5_lit.out`](out/c5_lit.out) and the readouts.
- **C5-REP, OLD and E.** The reader reproduces regenA P4's committed `tension_report.txt` for each input, at its printed
  precision: 15 mode rows, the top-five fraction and the ten-smallest share.
- **C5-LIT, OLD.** All seven literals reproduce at their printed rounding.
- **C-PINS:** equal before and after.
- **The runner's status lines.** In `… || rc=1; echo "readout e rc=$?"`, the logged `$?` would be `rc=1`'s status if
  the readout failed. So E's status is taken from the runner's exit code, 0
  ([`out/runner_exit.txt`](out/runner_exit.txt)), and from [`out/readout_e.out`](out/readout_e.out) (C5-REP true), not
  from that line.

**The 4.7 is this residual's.** per_period_benchmark.py:415-420's abs_z is diagnose_tension's eigpull,
|u_k · (E_R − published)| / √λ_k. OLD's largest is 4.7466637, against the benchmark's 4.7466649, a relative
difference of 2.5e-7. The benchmark ran on another machine; A4's records note eigenvectors there agree only to rounding.

## Readings, for journal-editor

The places were checked by grep at main 91d18499. The wording is Joseph's.

| quantity | printed at | OLD (our edges) | paper's edges |
|---|---|---|---|
| ten smallest-λ modes' share of the distance | appC_supplementary.tex:7 "$9.6\%$"; records_r03_twod.tex:18 "\SI{9.6}{\percent}" | 9.63 % | **8.71 %** |
| of the five largest, how many lie in the smallest-λ tenth | records_r03_twod.tex:18 "two lie" | 2 | **1** |
| of the six leading, how many have more than half their Σu² at p∥ ≥ 20 | appC:7 "three are concentrated …"; records_r03:18 "the three in the highest-p∥ bins" | 3 [(a), (b), (d)] | **5** [(a), (c), (d), (e), (f)] |
| their λ/λ_max | appC:7 and records_r03:18 "≲ 4×10⁻⁹" | 3.5e-9, 4.3e-10, 6.6e-11 | 3.5e-9, **9.4e-9**, 4.3e-10, 6.7e-9, 6.6e-11, so ≲ 1×10⁻⁸ |
| the other modes' λ/λ_max | "between 4×10⁻⁶ and 6×10⁻⁵" | 5.6e-5, 4.5e-6, 6.0e-5 (three modes) | **5.6e-5** (one mode, (b)) |
| largest standardized component | records_r03:18 "$4.7$" | 4.7467 | **4.3941** (4.4) |
| the next nine | records_r03:18 "$3.4$--$3.8$" | 3.358–3.777 | **3.103–4.031** (3.1–4.0) |

**The modes on the paper's edges.** By rank (panel), with λ/λ_max, lam_rank, |z|, χ² contribution and the p∥ ≥ 20
share:

| rank | λ/λ_max | lam_rank | \|z\| | χ² | share |
|---|---|---|---|---|---|
| 0 (a) | 3.549e-09 | 23 | 4.394 | 19.31 | 0.843 |
| 1 (b) | 5.613e-05 | 118 | 4.031 | 16.25 | 0.000 |
| 2 (c) | 9.370e-09 | 28 | 3.635 | 13.21 | 0.974 |
| 3 (d) | 4.314e-10 | 9 | 3.493 | 12.20 | 0.992 |
| 4 (e) | 6.708e-09 | 27 | 3.403 | 11.58 | 0.946 |
| 5 (f) | 6.590e-11 | 2 | 3.355 | 11.26 | 1.000 |
| 6 | 4.829e-10 | 10 | 3.255 | 10.60 | 0.997 |
| 7 | 4.376e-05 | 115 | 3.210 | 10.30 | 0.000 |
| 8 | 3.773e-10 | 7 | 3.165 | 10.02 | 0.999 |
| 9 | 6.048e-05 | 121 | 3.103 | 9.63 | 0.000 |

The same eigenvectors appear on both grids. The published covariance does not change, so λ and u are fixed; our
residual reorders them. On the paper's edges, the moderate-λ modes with lam_rank 121 and 79 leave the top six, and
the one with lam_rank 118 rises to (b). The small-λ modes with lam_rank 28 and 27, at high p∥, enter. This agrees with A4's mode-map reading.

[`SHA256SUMS`](SHA256SUMS) covers this directory. Files named `*.out` are committed with `git add -f`.
