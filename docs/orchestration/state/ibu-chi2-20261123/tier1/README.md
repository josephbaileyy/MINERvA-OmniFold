# Tier 1 of option (i): E_R and its binned IBU on the paper's pT edges (2026-11-24)

**By** the `ibu-chi-squared-issue` session (Claude Opus 5.5). It is part of the chain in [`../README.md`](../README.md).
Joseph chose option (i) and asked for Tier 1 now ([`../grid-price/`](../grid-price/README.md)). The director gave GO
for the packaged run and for running it in an interactive allocation. Both rulings, and cov2d's ack for the staged
copies, are in [`acks.txt`](acks.txt). No shared code or product was changed.

## Result

**Controls pass. On the paper's pT edges (0.075 / 0.325 / 0.475), the binned IBU's χ²/205 against the published result
falls from 1.027 to 0.538 at K = 10.** At K = 5 it falls from 0.830 to 0.395. E_R's own distance falls only from 2.270
to 2.121.

| | OLD edges (ours) | paper's edges |
|---|---|---|
| D_IBU, K = 10 (the "IBU χ²/205 = 1.03") | 1.0266 | **0.5381** |
| D_IBU, K = 5 | 0.8299 | 0.3949 |
| D_ER (E_R, the refined OmniFold central value) | 2.2703 | 2.1214 |

Each D is χ²(ours − published)/205 under the published TotalCovariance, on the 205 reported cells
([`score_t1.py`](score_t1.py) → [`score.out`](score.out)). **On the published side, the values are the release TH2D
`pt_pl_cross_section` (sha256 6c6dce72…), compared cell by cell. No bin widths enter, and `bin_mapping.txt` is not
read** (the director's condition 4). On the paper's edges, our cells are the release axis's cells: the run's hXSec2D pT
axis equals the release TH2D's Y axis, a checked control.

What the numbers mean:
- **The binned IBU.** About half of its distance to the published result came from comparing different pT bins.
- **E_R.** Its distance is mostly something else. The edge change moves it 7 %. Its 2.27 is the estimator-level tension
  the note already reports (`sec3_twod.tex:36`), and that stays.
- These are the comparisons with the published result only. Our analysis grid is unchanged (option (i)).

## Controls (declared in [`DECLARATION.txt`](DECLARATION.txt), sha256 `8d845062f58a38a31e8ad0fcf6656bec663fcfe227a32c5bfc6daef4c56aac85`)

| control | value | limit | |
|---|---|---|---|
| C-UNITS: four done-markers | all PASS (c2's C-FILL, C-SIM, C-ROO) | PASS | pass |
| C-REF-OLD: OLD er hXSec2D vs committed E_R (a5c13fc3) | 7.9e-12 max relative | ≤ 1e-8 | pass |
| C-D-OLD | D_ER 2.27032, D_IBU(10) 1.02658 | 2.270, 1.0266 within 5e-4 | pass |
| C-COL: column sums OLD vs E | data exactly equal; er hUnfold2D 2.3e-13 relative | 0; ≤ 1e-6 | pass |
| E's pT axis equals the release TH2D's | yes | — | pass |

C-COL also confirms the expectation stated in the pricing record. On the production negweight-refined path, OmniFold's
unfolded counts in each p‖ column are identical (to 2e-13) whatever the interior pT edges. The training does not see
them.

## How it ran

- **Inputs** ([`stage.log`](stage.log)). The CV omnifile (43f8cc16…) and the flux file (d40aea69…) were copied by
  `dd iflag=noatime` on login02 into the lane's `tier1/stage/`, re-hashed against their pins, and set a-w. This
  followed the director's ruling and cov2d's ack. The job read only these copies, plus the libRooUnfold.so that config
  pins (0b34e1e3…, checked on disk).
- **Code.** Two fresh clean clones at M = 77d76cfc, REF-C2C1's deploy. Main's re2_driver.py no longer matches
  ref_c2c1's code pin, so M is the commit where the pins hold ([`prepare.sh`](prepare.sh) → [`prepare.out`](prepare.out)).
  - [`receipts/tier1_deploy_old.diff`](receipts/tier1_deploy_old.diff) changes config.json's staging root only.
  - [`receipts/tier1_deploy_e.diff`](receipts/tier1_deploy_e.diff) changes the staging root, re2_driver.py:44's three
    pT edges, and config.json's pin for the patched driver (677ac75f…).
  - ref_c2c1.py is unchanged in both (285dd138…).
  - The director checked the patch, and that ref_c2c1 takes its edges from re2_driver.PT_EDGES.
- **Jobs.**
  - The queued `ibuchi_rb` (61926143) and `ibuchi_t1` (61927615) were cancelled before starting, CANCELLED with Start
    None ([`cancel.txt`](cancel.txt)).
  - Interactive attempt 1 (61928077) refused itself on the login node before any work
    ([`receipts/logs_t1i_runner_attempt1_refused.log`](receipts/logs_t1i_runner_attempt1_refused.log)).
  - The runner's guard was then changed to an srun hostname check ([`t1i_runner_v1.sh`](t1i_runner_v1.sh) →
    [`t1i_runner_v2.sh`](t1i_runner_v2.sh), [`t1i_runner.diff`](t1i_runner.diff); accepted by the director).
  - Attempt 2, **`ibuchi_t1i` (61928141)**: COMPLETED 0:0, 10:33 wall
    ([`receipts/sacct_all.txt`](receipts/sacct_all.txt), [`receipts/logs_t1i_runner.log`](receipts/logs_t1i_runner.log)).
    All seven script and code hashes matched inside the allocation at 17:55:06Z.
- **Nodes.** Every compute step ran on **nid200013**, per each step's sacct NodeList:

  | step | wall |
  |---|---|
  | .0 hostname | — |
  | .1 c2_central_old | 3:35 |
  | .2 er_e | 9:33 |
  | .3 er_old | 9:44 |
  | .4 c2_central_e | 3:24 |
  | .5 rebuild | 0:26 |

  The C-REF-OLD control was met on that node.
- **Outputs.** The unit outputs (done-markers, npz, ROOT) are in [`units/`](units/), with shas equal to the job's
  printed list ([`receipts/logs_t1i_tier1.out`](receipts/logs_t1i_tier1.out)).
- **Charge.** One interactive node for 10:33, about 0.18 node-h, under the 1.0 cap. Attempt 1 used 6 s.

**Not in Tier 1:** `ibukt/signed_data` at K = 5/10, which is a separate follow-up.
