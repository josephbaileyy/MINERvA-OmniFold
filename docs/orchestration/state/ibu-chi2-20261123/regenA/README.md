# Regeneration A: central-value comparisons on the paper's pT edges (2026-11-25)

**By** the `ibu-chi-squared-issue` session. It is part of the chain in [`../README.md`](../README.md).
- **Declaration:** [`DECLARATION.txt`](DECLARATION.txt) (085553b4…), committed before any output, at f37f49df.
- **Amendment:** [`AMENDMENT-A1.txt`](AMENDMENT-A1.txt) (077d57d5…), at f74ff551. It covers placement on login02, the
  clone, chi2_std's move to B, and the OLD staging.
- **GO:** the director's.

**Readings: [`READINGS.md`](READINGS.md)**, for journal-editor. On the paper's edges, E_R's χ² against the published
result is 434.89 / 205 = 2.121 (465.42 = 2.270 on our edges). The 185-cell shape χ² goes from 2.568 to 2.092. The
binned IBU check goes from 1.027 to 0.538 (Tier 1).

## How it ran

- **Where:** login02, 2026-11-25T05:37:18Z–05:40:27Z. Plain Python at nice 19, each producer under a 900 s timeout. It
  used 0 node-h, no Slurm and no srun, and wrote nothing to CFS
  ([`receipts/regenA_run.sh`](receipts/regenA_run.sh), sha256 ce0569128235d4056fdb03c0067eb57c74ad1ff320315b2114994684efcf3a71;
  log [`receipts/run.log`](receipts/run.log)).
- **Cost:** each producer took ≤ 8 s and ≤ 0.4 GB RSS.
- **Code:** a fresh clone of main at e766ee52 (contains #1318 and #1319). porcelain --ignored was 0 before and after.
- **Inputs, C-PINS:** equal before and after.
  - OLD: an O_NOATIME copy of partb/out/ER/xsec.root (a5c13fc3) in the lane's regenA/stage. cov2d's ack:
    > cov2d ack: ACK YES (Wed Nov 25 05:32:11 UTC 2026). Your plan for regenA is fine: one read-only O_NOATIME dd of partb/out/ER/xsec.root on login02 into your regenA/stage, re-hashed against pin a5c13fc3…, then chmod a-w. cov2d has no job, connect or write on that path or under 2d-closeout-re2, and none is planned before the covfix binding.
  - E: tier1/units_e/er.root (5171c7b8).
  - The release: cov_ptpl (6c6dce72), read from the producers' own ANC_DIR.
- **C-AXES:** PASS. The E input's hXSec2D pT and p‖ axes equal the release TH2D's.
- **C-GRID:** PASS. There are no cross-grid shape-χ² NOTE lines in any E log.

## C-OLD (OLD input against part C's committed receipts)

[`receipts/c_old.py`](receipts/c_old.py) → [`receipts/c_old.out`](receipts/c_old.out). Numbers are compared to 1e-9
relative; paths, hostnames and shas are ignored.

| product | reference (partc_r2/partc-r2/receipts/) | result |
|---|---|---|
| P1a chi2_paperonly | chi2_paperonly.txt | PASS, 39 numbers, max relative 0.0 |
| P1b pull_full | chi2_paperonly.txt (same producer and numbers) | PASS, 39 of 39 equal |
| P4 tension | figs/tension_report.txt | PASS, 394 numbers, 0.0 |
| P5 models | figs/model_comp_report.txt | PASS, 24 numbers, 0.0 |
| P6 tune receipt | receipt_model_chi2.json | PASS, 187 numbers, no key mismatch, 0.0 |
| P7 agreement windows | RECEIPT-agreement-windows.json | PASS, 20 numbers, 0.0 |
| P2 interior, P3 shape, P8 strip | — | **no OLD reference**: part C did not run them, so their E values are new |
| P9 Fig. 13 | — | figure, with no numerical OLD reference. The committed note PDFs are a later restyle |

## Stops, reruns and scope changes

- **P8, attempt 1: STOP, no reading.** Both OLD and E exited rc 1 with `OSError: Failed to open file` and an empty
  path, before any computation. The cause was my invocation: `--ours` takes `LABEL=ROOT[:HIST]`
  (strip_ratio_receipt.py:167-168). The logs are [`receipts/P8_attempt1_old_stderr.log`](receipts/P8_attempt1_old_stderr.log)
  and [`receipts/P8_attempt1_e_stderr.log`](receipts/P8_attempt1_e_stderr.log).
  - failed: `python3 strip_ratio_receipt.py --ours <input> --out <out>/strip_ratio_receipt.json`
  - rerun (director's GO, once): `python3 strip_ratio_receipt.py --ours er=<input>:hXSec2D --out <out>_P8b/strip_ratio_receipt.json`
  
  The rerun gave rc 0 for both, into fresh `out/old_P8b` and `out/e_P8b`. Shas: old 53c79a3ceb8b61db921087fb0d4cbc2a5382acbf5b2f173b9f16f16d68cca02d,
  e 302a4f88737c0a523130b37694ad7c623e9e288f01aac95c89cfb10cf2290f9a. The clone was still clean afterwards, and the
  inputs still matched their pins.
- **chi2_std → B** (amendment A1): part C's step passes `--omnifold-cov …:hCov_Q`, so it is the combined χ², a
  covariance product.
- **P10 → B:** the Figs. 6–7 takeaway's producer (`plot_uncertainty_fig6_7_style.py`) needs the covariance inputs to
  run.

## Files

`out/` holds every output: logs, reports, JSON receipts, ROOT and the figures. The fetched copy matches the remote
listing ([`receipts/out_remote.sha256`](receipts/out_remote.sha256), 86 files, written before the P8 rerun; the P8b shas
are above). [`SHA256SUMS`](SHA256SUMS) covers this directory.

**Disclosure (2026-11-25).** Commit c908169d (the READINGS place-column fix) was replaced by 16d8947d through a force-push, done in error, to amend its message: its trailer read "Checks: 24 passed" where that run passed 21. The tree is identical. The standing rule is merge commits only, with no force-push; a wrong trailer is corrected by a new commit, as this one is.

**Full precision for rounding-sensitive macros (journal-editor's request, 2026-11-25).** The P7 receipt stores
`median_bin_ratio` rounded to 4 decimals (agreement_windows_receipt.py:214), and E's 1.0075 sits on the 3-decimal
boundary that `\medianBinRatio` prints at. [`receipts/median_fullprec.py`](receipts/median_fullprec.py) recomputes it
with the producer's own definition (agreement_windows_receipt.py:141-148) from the same inputs →
[`receipts/median_fullprec.out`](receipts/median_fullprec.out). The control is that round(·, 4) equals the stored value:
PASS for both. E's median is 1.0074806014196405, which prints as **1.007** at 3 decimals; OLD's is 1.005357659335692
(1.005). Within 5 %: E 175/205 = 85.3659 % (85.4), OLD 178/205 = 86.8293 % (86.8). READINGS.md is unchanged.
