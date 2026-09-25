# RECEIPT 2026-09-25 — D3: one durable HPSS backup of the nine sole-copy scalar-5D objects

**CITABLE FOR:** which nine objects now have an HPSS copy, the archive path, per-object tape
residency, and a full restore from HPSS whose SHA-256 equals the recovery manifest's digests.
**NOT CITABLE FOR:** any scientific verification of these bytes, adoption, or a claim that the
restore read tape rather than HPSS disk cache (see §3). A checksum match says the bytes are the bytes.

Authority: Joseph's D3 in
[`AUTHORIZATION-20260924-scalar5d-campaign-activation.md`](AUTHORIZATION-20260924-scalar5d-campaign-activation.md)
row S8. Closes handoff dependency **D3** of
[`HANDOFF-20260924-preparation-for-scalar5d-campaign.md`](HANDOFF-20260924-preparation-for-scalar5d-campaign.md) §6.
Evidence (copied verbatim from the job's output directory, sealed by `SHA256SUMS`):
[`state/s5c/d3/`](state/s5c/d3/).

## 1. The job

| | |
|---|---|
| Slurm | `58855902`, `-q xfer -C cron`, `login16`, 2026-09-25T06:17:28Z → 06:41:29Z, `COMPLETED`, ElapsedRaw 1,444 s |
| admission | `nd-unfolding/s5c_meter.py`, stage `preservation`, reserved 0.094 CPU node-h (billing 2), measured 0.0031 |
| code | `nd-unfolding/s5c_hpss_backup.sh` at deploy `44a23a40` (clean clone at that commit) |
| object list | [`state/s5c/d3-nine-objects.tsv`](state/s5c/d3-nine-objects.tsv) — the nine `UNPRESERVED` rows of `state/RECOVERY-MANIFEST-20260924-trunk-external-artifacts.json` |
| archive | HPSS `mnv-scalar5d-solecopy-20260925/`, each object at its `/pscratch/sd/j/josephrb/`-relative path |
| size | 51,218,246,681 B (47.70 GiB) against D3's 64 GiB cap |

## 2. Per-object results

Every row: source size and SHA-256 re-measured on the original **before** anything was written
(`source-check.tsv`: 9/9 `yes`); `put` rc 0 (`put.tsv`); tape bytes at level 1 equal to the size
(`residency.tsv`); restored from HPSS to a fresh directory with rc 0 and SHA-256 equal to the
manifest (`restore.tsv`).

| object (relative to `/pscratch/sd/j/josephrb/`) | bytes | SHA-256 (manifest = source = restored) |
|---|---:|---|
| `MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/z-mean.npz` | 890,383,062 | `61b7a4939bd40459…` |
| `z2m-products/member_k000000/z-cv.npz` | 887,254,200 | `361090f94446260f…` |
| `z2m-products/member_k000000/z-mean.npz` | 887,371,441 | `6e2b8b32439b9979…` |
| `z2m-products/member_k001200/z-cv.npz` | 887,228,520 | `7e4636a33e490f48…` |
| `z2m-products/member_k001200/z-mean.npz` | 887,324,826 | `dbda36078c234655…` |
| `MINERvA-OmniFold/nd-unfolding/active_universe_5d/standard/candidate/std_final5_candidate.root` | 42,326,607,877 | `950f8cb15c5a0bd7…` |
| `MINERvA-OmniFold/nd-unfolding/uq_cov_mlsplit_5d.root` | 892,078,834 | `27b2e456f80e15d8…` |
| `MINERvA-OmniFold/nd-unfolding/uq_cov_stat_5d.root` | 891,732,011 | `6580016fa7136e6f…` |
| `MINERvA-OmniFold/nd-unfolding/uq_5d/z_precursor_20260914/unified_throw_cov_5d.root` | 2,668,265,910 | `09a029ed2a7de0ff…` |

Full digests are in `d3-nine-objects.tsv` and `restore.tsv`. The restored copies (51,218,295,833 B
by `du -sb`, including directories) were deleted from the campaign namespace after verification;
**the originals were never written, moved or deleted.**

## 3. What is and is not established

| claim | status |
|---|---|
| the nine objects exist in HPSS at the paths above | **measured** (`hsi ls -lR`, `hsi-ls-lR.txt`) |
| each is resident on tape at its full size | **measured** after `migrate -R -P`: level-1 `(tape)` bytes = size for 9/9 (`residency.tsv`; e.g. PV `AH106800` in `lsV-last.txt`) |
| a restore from HPSS reproduces the manifest SHA-256 | **measured**, 9/9 |
| that restore read **tape** rather than HPSS disk cache | **NOT established.** `purge -R` returned rc 0 after migration, but the 42.3 GB object restored at 509,877 KB/s (`get-std_final5_candidate.root.log`), faster than a typical single tape drive; a digest match cannot distinguish the two sources |
| HPSS quota after the backup | `hpssquota` read **300.20 GiB** both before and after the job (accounting lags writes). **Re-read 2026-09-25T08:04Z by the independent reviewer: 347.90 GiB = 300.20 + 47.70**, so the backup is now reflected in the quota instrument |

Two small evidence gaps, stated: the per-object `put-*.log`/`get-*.log` files are named by
basename, so the three `z-mean.npz` and two `z-cv.npz` logs overwrote one another (their rc and
digest rows in the `.tsv` files are per object and complete); and the job log's `migrate` line for
the trunk `z-mean.npz` reads *"migrated 0 bytes"* while `residency.tsv` shows it tape-resident at
full size (already migrated when the command reached it).

## 4. Consequence for the handoff

Handoff **D3 is closed**: the four rebuild inputs, `z-mean.npz` and the graded pair with its
`z-mean.npz` now have a durable, restore-verified HPSS copy. Together with the 48 objects the
preparation pass preserved, all 57 inventoried objects have a durable copy. The objects the
recovery manifest did **not** inventory (the L2 probe product, the ten endpoint unfolds, event-loop
inputs upstream of `central`/`support`/`active`) remain outside this receipt.
