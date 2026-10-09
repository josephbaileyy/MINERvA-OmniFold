# Agent A notes: rows D01-D06, M01-M03, V01-V21

Worktree: `$W` at `fec438db` (verified with
`git rev-parse HEAD`; `git status --short` was empty at start). I modified no repository file. Scratch outputs:
`agent-A-rows.tsv`, this file, `agentA/recheck_coverage.py`, `agentA/write_rows.py`, and `agentA/` (RC4 README and
fig-array manifest extracted from `rc4-tarball.tar.gz`).

Classes: RR 8 (V01-V07, V09); SO 13 (D01, D02, D04, D05, M02, V10, V11, plus M03, V16-V19, V21, which carry UP);
SO-NOINDEP 8 (D06, M01, V08, V12, V13, V14, V15, V20, of which 4 carry UP); ME 1 (D03). UP total: 10 (M03, V08, V12,
V15-V21). Exact per-row classes are in the TSV.

## Commands that bear on conclusions

### Local (read-only, in the worktree)
- Opened the paper sections at `paper_body.tex:55-240` and the provenance comments at `values.tex:1-140`.
- Opened the ledger rows and their introducing commits with `git log -S"| VLnnn |"`: VL149 eeb51f99 (:175), VL150
  55759309 (:176), VL151/152 c844277b (:161-162), VL153/154 5683e329 (:149-150), VL155 690ff304 (:136), VL169
  0f59faa9 (:58), VL170 1786b32f (:44), VL172 c40bd8c9 (:30), VL56 1ec042e9 (:846).
- Parsed these receipt JSONs with python3 and compared their values to the printed numbers:
  - `RECEIPT-2d-agreement-windows-20260821.json`
  - `receipt_model_chi2_2d.json` (:192, :196-197)
  - `recompute_2d_budget.json`, `boot_spreads.json`, `purity_datastream_check.json`
  - `uqpaper-median-20261006/paper_median.json`
  - `coverage-2d-20261005/interim_score.json`, `recompute/recompute_comparison.json`
  - `rescore_vl169_toys_vl170.json`
  - `s5c/d1/d1_summary.json`, `s5c/d1/bias_vs_adopted.json`
  - `s5n/stage1/dev_receipt.json`
  - `s5e/cand/assess_receipt.json`
  - `s5p/stage2/stage2_receipt.json`
  - `s5c/tier_s/interim_400.json`
  - `g2-gate1-all12-validation-20260719.json`
- `shasum -a 256` results:
  - `interim.npz` = 79c4dd6b, equal to its manifest.
  - `stage2_receipt.json` = 0daa7cd8, equal to VL155.
  - `interim_400.json` = aa574c17, equal to VL150.
  - The tracked paper-ancillary files `data_result` (02153e7a), `model_ptpl Tune_v1` (22231752) and `bin_mapping`
    (d21a41eb) equal the digests in the receipts.
- **Auditor recompute, my own code, from git-tracked inputs** (`python3 -I agentA/recheck_coverage.py $W`):
  - VL162 band: C1 0.679366, C2 0.912146, pull mean -0.0337, RMS 1.597 (V11 reproduced).
  - VL170 band: C1 0.780585, C2 0.976878 (V13 reproduced).
  - Median σ/mean from the tracked `vl170_band.json` is 0.67395% (V12 reproduced).
- Fifteen-fold (M03), from `d1_summary` split_F2 and the s5n high_W cells:
  - The ratio |purity|/|negweight| per highest-W cell ranges from 14.9 to 36.8.
  - The endpoint ratio 3.5/0.24 is 14.6, and the max/max ratio 4.11/0.234 is 17.6.
  - No receipt states the ratio.
- The RC4 fig_numbers output already in scratch (`out/fig_numbers.log`) reports [ok] for sigTwoD, sigTwoDpaper,
  ratioTot, binsTen, pullMean, pullRMS, chiPaper, uqPaper and n_reported=205. The RC4 manifest pins the source shas
  142a45b0 and 6c6dce72, plus code commit 556d6dde.

### Cluster (ssh saul.nersc.gov; read-only ls/stat/sha256sum/find/hsi ls; times are PDT)
1. `stat` and `sha256sum` on the 2D sources (stat was taken before the hash):
   - `2d_crossSection_omnifold_MEFHC_5iter.root`: 55,513 B, mtime 2026-05-19, atime 2026-10-06 09:14, sha
     142a45b0 MATCH.
   - `cov_ptpl_minerva_inclusive_6GeV.root`: atime 2026-10-06 09:20, sha 6c6dce72 MATCH.
   - `model_ptpl...Tune_v1.txt`: atime 2026-10-06.
2. CFS `/global/cfs/cdirs/m3246/josephrb/` holds `minerva-shutdown-stage` and `s5p-archive-20261006` (10,612
   SHA256SUMS lines covering runs/prod, recovery, stage7, gen5d and gen5d_fluxfix). It has no s5c/s5n/s5e runs and no
   s5p runs/s2.
3. CFS durable copies, each hashed on CFS:
   - `fig_products/2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root` 142a45b0 MATCH, and
     `minerva_paper_anc/cov_ptpl...root` 6c6dce72 MATCH.
   - Under `fig_products/2d-unfolding/uq/`: CV 4f5a1b6d, VL162 universe 62590df7 and ml 3b6b48ec, all MATCH.
   - `fig_products/3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root` 0dd94830, equal to pscratch.
   - `find -maxdepth 6 -name "*vl170*"` returns nothing.
4. pscratch VL170 products:
   - `bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root`: atime 2026-10-06 09:07, sha 71a75821 MATCH.
   - `universe_..._vl170`: atime 2026-10-06 09:06, sha 077912e3 MATCH.
   - `ki84-rebuild-20261006/replicas` has 600 files (boot100 atime 2026-10-06 09:12).
   - `coverage-2d-20261005/toys` has 200 files (toy100 atime 2026-10-05 12:59).
5. Projection `/pscratch/sd/j/josephrb/z2m-products/PROJ/cov_5d_to_eavailW_publication.root`: sha 835828bf MATCH.
   - Its durable copy is in `/global/homes/j/josephrb/evidence/repository-epochs/preparation-2026-09-24-bf34a12c/trunk-baseline/z2m-products/PROJ/`,
     sha 835828bf MATCH.
   - The 5D xsec 630306e2 in the same epoch also MATCHES.
   - (My first `ls` of `repository-epochs` was truncated by `head`. A full `ls -la` shows all seven epochs, including
     preparation, prepublication and simplification.)
6. Run directories, pscratch only. "Oldest file atime" is the earliest atime found by `find -printf %A+`:
   - `s5c-20260924/runs/d1`: 30 files, about 2026-09-25 (d1_split_s4.npz atime 2026-09-25 15:06).
   - `s5c-20260924/runs/s_valid`: 1,849 files, 2026-09-25 03:35.
   - `s5n-20260925/runs`: 649 files, dev 2026-09-26 02:57.
   - `s5e-20260925/runs/cand`: 726 files, 2026-09-25 20:19.
   - `s5p-20260926/runs/s2`: 923 files, 2026-09-26 09:40.
   - At the 8-week purge rule, the earliest of these become purge-eligible around **2026-11-20**. Some are already
     being refreshed by parallel auditors' reads, which my own sha256sum reads also do.
7. 4D/5D/input products:
   - `xsec_4d_MEFHC_5iter_lgbm.root` 1fb82508: pscratch only, atime 2026-10-03.
   - `of_inputs_5d.npz` (1.55 GB, mtime 2026-06-27): pscratch only. Bounded `find` on CFS and homes found no copy;
     HPSS `mnv-scalar5d-solecopy-20260925` holds other 5D files, not this one.
   - Merged 5D omnifile: pscratch 169,974,191,800 B (atime 2026-09-14). HPSS `mnv-quoted-products-20260812` shows the
     same size (`hsi -q ls -lR`). The tape copy's md5 hashverify PASS (36/36, 2026-08-20) is recorded in
     `docs/orchestration/RECEIPT-20260820-oi50-hashverify.md`.
8. G2 per-playlist: 12 ROOTs in `g2_fullevent/final` (1A is 9.42 GB, atime 2026-09-18). `G2_receipt_1A.json` sha
   906ce507 MATCHES the state JSON. On CFS, `g2_input/G2_FPS_MEFHC_P12_RECEIPT.json` records data=4,116,128 (the
   post-domain npz, not the printed 4.12 M population).
9. HPSS `mnv-quoted-products-20260812/2d-unfolding/uq` holds the VL162-era boot300, ml and universe files, with sizes
   equal to pscratch. It has no VL170 files.

## Consequential findings
- **No numeric mismatch** in any of my 30 rows: every printed value matches its receipt at the printed precision.
- **ME: D03** (⟨E_ν⟩ ≈ 6 GeV) has no repository receipt; it is a literature property and needs a citation.
- **Wording issues that are not mismatches:**
  - **V13:** the rescored C2 = 0.977, with interval [0.974, 0.980], lies above the 2σ nominal window
    [0.928, 0.972]. The paper says only that the 1σ fraction is above its window.
  - **V14:** the paper says "its cause is untested", but the KI-85 diagnostic (8eb40e5f, 2026-10-07) is recorded as
    consistent with closure-toy under-scatter. It is descriptive, and the decisive held-out test is still deferred.
  - **V19:** 16–31% holds for (E_avail,W) cells only (W3 over all functionals reaches 33.6%). It was measured with
    candidate R, not with the F2/N estimator that gave the 74%.
  - **M03:** "about fifteen-fold" is the conservative end of per-cell ratios 14.9–36.8. No receipt states the ratio.
- **Retyped literals:** 0.674, 97.7, 78.1, 95.4, 205, 4%, 0.3%, 1%, 1.4%, 74% and 16–31% are prose literals with no
  macro. All match their receipts today, but no build check binds them.
- **D05 population ambiguity:** the repository also carries mc_truth_denom = 49,906,108 for the same 12 playlists
  (the G2 full-schema production). The printed 32.8 M is the 5D/2D omnifile count, which an independent audit
  measured (AUDIT-FINDINGS-20260820:281).
- **M01:** no receipt binds the 2D production ROOT (sha 142a45b0, mtime 2026-05-19) to its classifier configuration,
  and the `--estimator` flag postdates the file (9006278b, 2026-05-28).
- **V15:** the 3D/4D/5D anchors exist only as June ledger prose and status docs. There is no VL id and no product
  digest; the 4D product is pscratch-only.
- **V21 record inconsistency:** OUTCOME-20260925-s5c-tier-s-futility-fail.md:43 gives nominal "1/2" (review round 4),
  while VL150 gives "0/2". The printed FAIL is unaffected.
- **Top preservation risks** (pscratch-only, earliest atime about 2026-09-25, so purge-eligible about 2026-11-20 if
  nobody reads them):
  1. The s5c runs/d1 and runs/s_valid products behind VL149 and VL150.
  2. The s5n runs behind VL151 and VL152, including the 74% and the "fifteen-fold" operands.
  3. The s5e runs/cand products behind VL154 (16–31%, a few SD).
  4. The s5p runs/s2 products behind VL155.
  5. The VL170 bootstrap covariance and its 300 replicas behind VL172 (6.87%, 0.674%). Their atime is 2026-10-06, and
     no copy exists on CFS or HPSS.
  6. `xsec_4d_MEFHC_5iter_lgbm.root` and `of_inputs_5d.npz`.
  - Every receipt for the 2D headline numbers names only pscratch paths, although verified CFS copies exist.
- **Purge-clock caveat:** every atime I report for a file I also hashed was recorded before the hash, except the 3D
  pscratch file, whose atime of 2026-10-08 01:03 is my own read. Parallel auditors are refreshing atimes, so atime
  does not show whether anyone needs a file.
