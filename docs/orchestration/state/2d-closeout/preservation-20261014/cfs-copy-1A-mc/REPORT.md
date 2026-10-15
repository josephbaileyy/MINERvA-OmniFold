# CFS copy of the 41 Playlist 1A MC AnaTuples (2026-10-15)

**Result: COPIED AND VERIFIED, 41 of 41.** The older-processing 1A MC files, which are no longer public, now have
a non-purged copy on CFS. Every destination file equals `ANATUPLE-SHA256.tsv` by sha256, bytes and mtime.

**CITABLE FOR:**
- the location and integrity of the CFS copy of the 41 1A MC files;
- draft A no longer being needed for these files.

**NOT CITABLE FOR:**
- the 1A Data files. They are in the 2026-10-09 CFS copy (`prd-release-preservation-20261008/`), see
  [`../REPORT.md`](../REPORT.md);
- a tape copy. There is none of these files;
- any physics result.

| field | content |
|---|---|
| `Authority` | Joseph, 2026-10-14, after the director reported the group and personal CFS figures: "yes you can copy them" |
| `Who` | The paper-tighten lane (director) wrote and ran the script and wrote this record |
| `Compute` | No Slurm job; 0 node-h. `rsync` and `sha256sum` ran on `dtn01.nersc.gov` at nice 19 / ionice idle, 2026-10-15T03:50:05Z to 05:01:56Z |
| `Evidence` | [`scripts/copy_1A_mc_to_cfs.sh`](scripts/copy_1A_mc_to_cfs.sh); [`outputs/`](outputs/): `1A_mc.sha256.tsv` (the 41 manifest rows), `verify.tsv`, `verify_summary.txt`, `dst_du.txt`, `rsync.rc`, `start.txt`, `done.txt` |

## 1. What was done

- **Source:** `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1A/`, 41 files, read only.
- **Destination:** `/global/cfs/cdirs/m3246/josephrb/mc-1A-preservation-20261014/MC/StandardMC/Playlist1A/`.
  The script refused to run if the destination already existed. It did not exist.
- **Copy:** `rsync -a --files-from` with the 41 manifest paths. Mtimes were preserved, nothing was deleted, and
  `rsync` exited 0 with an empty stderr (0 bytes on the cluster; `*.err` is gitignored).
- **Manifest:** `publication/release/preservation/anatuple-checksums/ANATUPLE-SHA256.tsv`, at sha256
  `913e004d538c6d47932ba5a343d382d2a599be1c6f143ab64f49ccbd40bdf7b1`, last changed in `2a077a82`.
- **Verification:** the script read every destination file in full on CFS with `sha256sum`, and compared the
  digest, `stat` size and mtime with the manifest row. **OK = 41, MISMATCH = 0.** The bytes sum to 706,929,079,280.
- **Afterwards:** the tree was made read-only (`chmod -R a-w`). `du` gives 706,929,397,760 B (0.707 TB) in blocks.

## 2. Consequences

- **Purge exposure.** The scratch originals still become purge-eligible from 2026-12-09. The CFS copy is now the
  durable one.
- **Draft A** (the NERSC HPSS request) is superseded for these files and was never sent. It is marked in the draft
  file.
- **Joseph's CFS area** is now about 3.947 TB: the 2026-10-14 `du` of 3,239,895,250,944 B plus this copy. That is
  over his "under 3 TB" rule, by his decision. The plan he was given:
  - remove the Stage C input backup `2d-closeout-stageC-inputs-20261012/` (538,486,940,672 B) after the closeout,
    which brings the area to about 3.41 TB;
  - decide the PET folders with Ben: `mnv-p3f-pet-fullevent-final/` (1,134,999,732,224 B; the only copy) and
    `pet-studies-20261006/` (422,878,122,496 B).

  Folder sizes come from per-folder `du -s --block-size=1` on dtn01, 2026-10-15. They sum to 3,239,895,249,920 B.
- **The m3246 group** used 83,502 of 102,400 GB on CFS (`prjquota`, 2026-10-15, before this copy).

## 3. Limits

- **Ownership and permissions.** `rsync -a` kept the source group `josephrb` and mode `r--r-----` on the files. So
  other m3246 members, Ben included, cannot read them. Making them group-readable would take
  `chgrp -R m3246` plus `chmod g+rX` by Joseph's account. That is not done, and it is Joseph's choice.
- **Single copy.** CFS has no tape copy of these files. NERSC CFS snapshots are short-term, not an archive.
