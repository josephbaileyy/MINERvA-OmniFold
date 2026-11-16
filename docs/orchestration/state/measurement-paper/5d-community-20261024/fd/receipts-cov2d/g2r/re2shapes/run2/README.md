# RE-2-shapes, run 2: RE2SHAPES PASS (2026-11-16T03:14–03:21Z)

**By** the `cov2d` session, under the director's "go fb7c2181 8631262d", given after coverage-5b-audit cleared rev 3
(package `../package/`, PKG `e7db5f22`). Run 1's C0 STOP is `../run1-stop/`. The lane draws no outcome.

**The split (the director's ruling 2):** the reported 2D covariance is `data_g2r.npz`'s C_new (D1; #981 ships it
bitwise). This run supplies the quantities derived from it in RE-2's own shapes: budget, medians, ROOT files, figures,
numbers. C1 shows that its Q equals C_new to within 1e-14 sqrt(C_ii C_jj) on every entry, and that the printed
numbers are identical at the spec's formats.

**CANNOT AUTHORIZE:** any paper, Supplement or note wording, or any adoption. The keys that use these files are the
director's helpers' to re-point.

## The run, as printed (`logs/connect.log.txt`; `launcher/launch-stdout.txt`)

- **Launch:** the launcher fence was clear; staged `8631262d…` DIGEST_MATCH; launched rc 0 at 03:14:37Z;
  `last line: DONE (polls=21 of 360)`. The staged files were removed.
- **Connect**, login02, 03:14:35–03:21:45Z, nproc 244, OMP_NUM_THREADS unset, B = 903fb78b, PKG = e7db5f22:
  - `fence (start) clear`: every query rc 0, rdx_s1_1A COMPLETED, squeue header only, 156 sacct rows none unended,
    marker absent;
  - partc-r2 SHA256SUMS OK (128 lines); deploy porcelain 0 at B; the 6 staged files OK (`stage.sha256.txt`).
- **C0:**
  - `arm identity rc=0` (03:15:55–03:18:51Z), `G2R-DRIVER mode=identity rollup_rc=0 redirected labels=0 calls=0`;
  - `c0 comparator rc=1` (its differences: SHA256SUMS and the receipt, both handled below);
  - `C0 PASS: lines 128/128 mkdtemp tmp6hw50588/tmp54xgxooz`, counts R1 1, bitwise 62, path-pairs 26, the three
    scratch rules 1 each, skipped PDF 22, skipped logs 14; `other []`, `extra []` (`c0-sums.json` `2d679760…`,
    `c0-determinism.json` `46730e69…`).
- **The g2r arm:**
  - `fence (before the g2r arm) clear`, with the same values;
  - `arm g2r rc=0` (03:18:58–03:21:39Z), `RUN COMPLETE (refined)`,
    `G2R-DRIVER mode=g2r rollup_rc=0 redirected labels=175 calls=175` (`g2r.g2r_driver.json.txt` `d5e8aa88…`; the two driver sidecars carry a `.txt` suffix, bytes unchanged, because their products_tsv path + sha256 pair would otherwise join the receipt binding inventory).
- **C1** (`c1.json` `bbac827e…`): `C1 PASS`, `c1 rc=0`:
  - (a) max_scaled 7.311559097428637e-16, n_above 0, worst (111, 127);
  - (i) per-entry max_rel 5.800344509600607e-13, 1880 entries above 1e-15, worst (69, 107);
  - (ii) max|dQ| / max|C_new| = 2.580856884329175e-16;
  - (iv) bitwise False;
  - (b) 14 rows, none failing; (c) 20 rows, none failing; (d) x and F equal partc-r2's;
  - universe_delta_scaled_rel 5.758541080103807e-14.
- `RE2SHAPES PASS: C0 PASS, g2r arm rc 0 with 175 redirects, C1 PASS`, DONE.
- **$A's HEAD** (the director's request, covering the audit's low): `receipts/receipt_model_chi2.json` repo_commit
  `ed3590ea245f23bd4c7d1f21e1dd4b6dd0fa558e` in both arms (c0 generated 03:18:01Z, g2r 03:20:49Z).

## Files

- `g2r/`: the g2r arm's tree, the set `partc_r2/partc-r2/` committed for partc-r2 (records, logs, small JSON and
  text), plus the two fig6/7 PDFs as print-ready inputs. `outA/budget_Q.json`, `s5/s5.json` and `outA/cov2d_Q_205.json`
  are committed gzipped (mtime 0), as partc-r2's were. File names inside `g2r/` are the run's own, as partc-r2's are.
  `g2r/SHA256SUMS` is the run's own list (re2c_run.sh:199-200): every member, including the fig6/7 PDFs and
  `./outA/budget_Q.json`'s uncompressed digest. `g2r/logs/steps.tsv` holds each step's full argv (for example the
  fig67 producer's title, ymax, ml-label and extra-block). The npz and ROOT products are not committed; their sha256
  values are in `g2r/SHA256SUMS`, `NODE-SHA256.txt` and `out.sha256.txt`:

| product | sha256 |
|---|---|
| `g2r/outA/cov2d_Q_205.npz` | `ff66b91d6d2c574a1786b057ce7566e8ed7184700a45b989fa41ae0eb8cb0295` |
| `g2r/outA/uq_adopted_covariance.root` | `8a5f693a80395e04b321e6df97cf614c1fb85eff5a0770f5f6f004e7ed8ddc6f` |
| `g2r/s5/production_cov.npz` | `1ee45dcd94ccb4e6340a6694bb0ce90c157f0b5c4bb81e18711d51e74a331d1b` |
| `g2r/combination/s5_plus_playlist.npz` | `81fdd16f58a113d48870f0e42548e301545cba23b50169811ffcd2fe1e5dc8ad` |
| `g2r/outA/budget_Q.json` (decompressed) | `7ed733c62433855cfe5943b6d28956f25c21f75230bd95a26c40b8435ec907d8` |

- **The files the D1 keys read** (director-helper-3): `g2r/outA/budget_Q.json.gz`, `g2r/combination/combination.json`
  (`fb9fe357…`), `g2r/cmodel/cmodel_R.json` (`0525217d…`), and `g2r/values_table.tsv` (`798b837c…`) or
  `values_table.json` (`c7403cdf…`). `g2r/periods/analysis.json` equals partc-r2's once the path pairs are applied
  (chi2_pz_marginal 34.42079993125393 in both): the periods step reads export_cov's work_cov, not the rollup.
- Top level: C0's and C1's records, both driver sidecars, `out.sha256.txt`, `stage.sha256.txt`, the connect's logs
  (`logs/`), C0's identity-arm SHA256SUMS and receipt (`c0/`), and `launcher/`.
- `NODE-SHA256.txt`: all 282 files in `$W` except the deploy clone, listed by sha256 and fetched O_NOATIME by
  `fetch_run2.py`. The 90 committed copies match it (the gzipped ones after decompression).

## Not for removal yet

`/pscratch/sd/j/josephrb/cov2d-re2shapes-20261115/` holds route A's npz and ROOT products above, which the next steps
read (Fig. 1 on the new Q, cr, xk). It stays until those are done and the products have an archive copy with its own
go. The identity tree `c0/` and the deploy clone can go with it then.
