# REPORT: GENCMP amendment E, addendum E-A2: the corner figures redrawn without the hydrogen flags on the legend (2026-11-03 UTC)

**By** the limitation-resolver lane (Claude), for the director.

**Under** [`FD-GENCMP-AMENDMENT-E-BINDING.md`](FD-GENCMP-AMENDMENT-E-BINDING.md), addendum E-A2 (#710). That binding binds
[`FD-GENCMP-AMENDMENT-E-ADDENDUM-EA2.md`](FD-GENCMP-AMENDMENT-E-ADDENDUM-EA2.md) at M⁗ = `e1c0af3b`. The second attempt
ran under the director's ruling (a) of 2026-11-02, given by message after the first attempt.

**MEASURES:** the three redrawn figures and their sidecars, `fd_g_figures_check`'s verdict, and control D's.

**CANNOT AUTHORIZE:** a paper or caption edit. Under binding ruling 2, the paper lane re-pins `FIGURES` and drops the two
caption sentences.

**CITABLE FOR:** the three figures under `fd/gencmp-e/rerun1/chain/chdefs/with/figures-a2/`. Their plotted content is
amendment E's committed E-1 with-arm figures', apart from the legend and label texts.

**NOT CITABLE FOR:** any new number. Every readout and plotted value is unchanged, as control D checks.

## 1. Outcome

- **`fd_g_figures_check --prediction-set gencmp-chdefs`:** "OK: 498 checks, 0 failed, 3 sidecars".
- **Control D: PASS** on all three sidecars. The label texts changed are 2 (ratio), 1 (modes) and 2 (sens), and there
  is no other difference (`figures-a2/control_d.json`).
- **The drawn names,** read by eye from the PDFs: "NuWro 21.09: CH" and "GiBUU 2019: CH; $p_\parallel$ < 4.5 cells only"
  on the ratio legend. The modes panels' titles read "NuWro 21.09: CH" and "MINERvA Tune v1: prior (not an independent
  prediction)". Neither flag appears.

## 2. The run

- **`$R`** = `/pscratch/sd/j/josephrb/gencmp-ea2-20261102/`, on login37 (the script checks `hostname`), at 0 node-h.
- **Attempt 1** (`receipts/x_ea2.sh`, sha256 `2d46861d…`), from 2026-11-03T03:06:29Z:
  - A fresh clone at M⁗: HEAD = M⁗, and porcelain with `--ignored` was empty.
  - The 4 binding blobs matched (`receipts/deploy-blobs.txt`).
  - The environment was root_6_28: Python 3.11.14, matplotlib 3.10.8, numpy 1.26.4.
  - **It stopped at a pre-run test gate the lane had added, which the binding does not require.** The gate was
    `test_fd_gencmp_ea2`, `test_fd_gencmp_e` and `test_fd_g_figures`, and gave "Ran 101 tests, FAILED (errors=9)"
    (`logs/tests.log`).
  - All 9 errors are `test_fd_gencmp_e.StepCR`, each "No module named 'uproot'" in a ROOT-fixture writer. root_6_28 has
    no uproot. The other 92 passed.
  - No figure was drawn, and nothing was written outside `$R`.
- **Attempt 2** (`receipts/x_ea2_r2.sh`, sha256 `267ae458…`), 03:59:08–04:01:07Z, under the director's ruling (a):
  - the same clone, with HEAD, porcelain and the 4 blobs re-verified (`receipts/deploy-blobs-2.txt`);
  - the gate on `test_fd_gencmp_ea2` and `test_fd_g_figures` only: "Ran 58 tests, OK" (`logs/tests-2.log`);
  - then `fd_gencmp_ea2.py --out-dir $R/figures-a2`, rc 0 (`logs/ea2.out`, `ea2.err`);
  - porcelain after: 0 lines.
- **Reads.** Every input was a committed file in the run's own clone, and each was required at its committed digest by
  `fd_gencmp_ea2.py`. No pre-existing pscratch file was read.
- **The scripts** were staged in login37's `/dev/shm`, copied into `receipts/` and deleted. Their sha256 equal the
  lane's local copies.

## 3. Records

- `fd/gencmp-e/rerun1/chain/chdefs/with/figures-a2/`: the three PDFs and sidecars and `control_d.json`. Each equals its
  row in `fd/gencmp-e/a2/run/receipts/figures-a2.sha256`, checked after the copy.
- `fd/gencmp-e/a2/run/logs/` and `receipts/`: both attempts' logs, the deploy and environment records, and the scripts.
- **HPSS:** not needed. Every product is committed.

## 4. Deviation

The first attempt's gate was the lane's addition, and its suite choice did not suit root_6_28. The director ruled it not
a STOP under any binding rule and approved the rerun in the same `$R`.

Nothing is submitted, deposited or tagged.
