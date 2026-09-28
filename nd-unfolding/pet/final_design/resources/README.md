# Resource ledger (PET final-design study)

`RESOURCE_LEDGER.tsv` is regenerated from `sacct` by `ledger_from_sacct.py` (every job named `pfd-*`,
including the specialists' jobs) and summarized in `RESOURCE_LEDGER.summary.json`. Times in the TSV
and the summary's `end` are Perlmutter-local (US/Pacific). `gpu_hours` = elapsed × allocated A100s;
CPU node-hours = elapsed × billing / 256.

**Units against the allocation.** `iris` charges `m3246_g` in GPU-node-hours (one 4-A100 node-hour
per unit): the study's first 124 A100-hours (sacct, 2026-09-25 14:30 PT → 2026-09-26 01:44 PT)
correspond to ≈ 31 node-hours, and `iris` moved from 450.5 to 478.1 user-charged units over roughly
that window (with accounting lag). Project balance on 2026-09-26 08:45Z: `m3246_g` 121,397.8 of
180,000 charged (58,602 remaining); `m3246` (CPU) 16,579.9 of 20,000 (3,420 remaining).

Snapshots (append; never edit a past row):

| date (UTC) | study A100-h (sacct) | study CPU node-h | m3246_g project remaining | m3246 project remaining |
|---|---:|---:|---:|---:|
| 2026-09-25 21:48 (start) | 0 | 0 | 58,714 | 3,430 |
| 2026-09-26 08:45 | 123.9 | 0.23 | 58,602 | 3,420 |
| 2026-09-26 20:34 | 314.8 | 0.30 | 58,424 | 3,410 |
| 2026-09-27 14:14 | 683.1 | 0.50 | 58,123 | 3,385 |
| 2026-09-28 02:40 | 1,001.8 | 0.51 | 57,975 | 3,377 |

2026-09-26 20:34 UTC: study total 314.8 A100-hours over 331 jobs (running jobs counted to the snapshot time);
`iris` user-charged `m3246_g` 526.8 units (GPU node-hours), project charged 121,575.9 of 180,000; `m3246` CPU
project 16,589.5 of 20,000. Competing commitments measured the same day: the `s5p`/`s5e` lanes (same user) run
CPU `shared`/`interactive` jobs and one `gpu_shared` array; this study uses GPU `debug`/`interactive`/`shared` and
≤ 1 CPU debug node at a time for post-hoc/scoring. Reserve for final validation: coverage of one finalist at
N_cov 120 + D4c 60 ≈ 1,080 unfoldings ≈ 0.9–1.1 k A100-hours, well inside the S5 budget (2,200) and the project
balance.

2026-09-27 14:14 UTC: study total 683.1 A100-hours over 574 jobs (running jobs counted to the snapshot time); `iris`
user-charged `m3246_g` 621.6 units; project charged 121,877.4 of 180,000. Known losses: ~80 empty 35-s debug
rounds (2026-09-26 19:57–21:08Z, iteration estimate too large for a 30-min round), ~12 killed L128S1T24 debug
iterations (24-epoch iterations do not fit a debug round), four dev3N runs and the overlap lanes lost when an
interactive allocation ended early, the stopped X4 arm (partial). Remaining released work (blinded): ~430 look-1
FB rows of `s4f_a3`/`s4s_a3` plus the 3e extensions (~500 rows), at 1.5–1.8 A100-h per unfolding.
