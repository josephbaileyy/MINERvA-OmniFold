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
