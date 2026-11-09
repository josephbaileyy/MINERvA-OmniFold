# LL5D: the realpath overlap check of LL5D's inputs against the band diagnosis's and FD-PRR's (2026-11-08)

**By** the `cov2d` session, under LL5D BINDING 2 (the director's ruling: before the first ll5d_ go, record a realpath
overlap check of LL5D's inputs against the band diagnosis and FD-PRR, which also run after ENS1, so they can be
sequenced). The director's go named `connect-ovl.sh` `7aa60812…` and `launch-ll5d.sh` `45f5055c…`.

- **MEASURES:** which files LL5D's calibration and gate jobs will read are the same files (device:inode of the
  realpath) as files the band diagnosis (`FD-1B-BAND-DIAGNOSIS-DECLARATION.md` §6) and FD-PRR (#937, §10.4) declare.
- **CANNOT AUTHORIZE:** any ll5d_ job; the sequencing, which is the director's.
- **0 node-h:** login02, no job, run 2026-11-08 20:16:43–20:17:03Z (`ovl.txt`). The launcher's ssh rc was 0.

## Result (`ovl.txt`)

| set | files keyed | missing |
|---|---:|---:|
| LL5D (the npz, the background dump, the pins file, the flux constraint, the staged flux table, F1's two bridged ratios, the staged S1 assembly, and every file in `bank_sweep_5d_bkgaware/` and `bank_detector/`: a superset of what LL5D reads) | 742 | 0 |
| the band diagnosis (the npz, the dump, `bank_detector/`, Part 1's `$V/stage` and `$V/unf`) | 780 | 0 |
| FD-PRR (the npz, the dump, the bank's `cv.npz`, the NuWro ratio, FD-STAB's control closures) | 22 | 0 |

- **LL5D ∩ the band diagnosis: 35 files.**
  - `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz`;
  - `/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz`;
  - the 33 files of `/pscratch/sd/j/josephrb/s5p-20260926/bank_detector/` (the 8 detector universes' weight sets and
    `detector-dump.json`).
  - The pins file is not among them: the band diagnosis's declared list does not name it.
- **LL5D ∩ FD-PRR: 3 files.** `of_inputs_5d.npz`, `bkg_dump.npz`, and
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/cv.npz`.
- **Every shared file is an input that all three read and none writes.** LL5D reads through O_NOATIME. The check
  establishes file identity for sequencing. It shows no write conflict.

## How it was read

- `connect-ovl.sh` (sha256 `7aa608124dd6869a8dbaaa3197feed4fcea72f3dbf6e12da033b8f4cbe30fed7`) ran on login02 through
  `bash -s`. It uses `realpath` and `stat -c '%d:%i'` only, and opens no input file.
- `launch-ll5d.sh` (`45f5055c4ae90395d6e96b5dcbdbcb8ca44a1247a1a6298a74bfd2aeeb3c46f2`) refused unless the local
  connect's sha256 was the go's. It read the ssh's rc unpiped.
- **Directory atimes:** listing `bank_sweep_5d_bkgaware/` and `bank_detector/` (`find -maxdepth 1`) moves those two
  directories' own atimes. No file atime moves. No lane uses those directories' atimes as a control (ENS1's #940 note
  says the same).
- **Scratch:** the key lists were written under `/dev/shm/josephrb-ll5d-ovl.b0ll2T` (umask 077), removed with
  `rm -rf` rc 0, and the closing listing showed none left.

## Files

`connect-ovl.sh`, `launch-ll5d.sh`, `ovl.txt`.
