# Scratch cleanup, 2026-11-27

Joseph approved removing unused scratch data on 2026-11-27. The director relayed the approval, and Joseph confirmed it directly in the high-p∥ lane's session ("Delete both"). Two removals were made. Each kept only what is not already on main.

## Perlmutter: `/pscratch/sd/j/josephrb/precharge-testC-20261126/`

The removal ran in one connection (login10, 03:08:53–03:08:55Z), with the full record in `perlmutter-removal.log`:
1. lstat the root. It was a directory, not a symlink, and held no symlinks.
2. Write the manifest of all 106 files (path, size, sha256).
3. Check the 48 outputs against `../testC/inputs/fetched.sha256`. All 48 were OK.
4. Delete that one root by its literal path, with rm rc=0, and confirm it is gone.

The script refused to delete unless the check rc was 0 with 48 OK, the count was 106 files, and there were 0 symlinks.

Of the 106 files, these 104 are on main:
- the 48 outputs (`../testC/inputs/`, #1388);
- the 24 Slurm logs (`../testC/inputs/slurm/`, #1399);
- the 7 staged sources and `staged.sha256` (`../testC/`, #1380);
- `built.sha256` (`../testC/inputs/`).

The two that are not:
- **The binaries `measure` and `truth`.** Only their sha256 is kept, in `../testC/inputs/built.sha256` and in the manifest. `../testC/build.sh` rebuilds them from the committed sources in the archived MAT environment, though not necessarily bit-identical.
- **The 24 `.done` markers.** They were empty.

## Local: `~/cov2d-work/precharge-bvRAlb/`

This folder is in `~/cov2d-work`'s own repository, and that repository's other files were not touched. `bvRAlb-manifest.tsv` lists all 106 files with size, sha256 and status:
- **24 match.** These are the 12-playlist Data and MC event tables, 50,421,095 bytes, and each one's sha256 equals `../inputs/events/` on main. All 24 were removed by literal path at 03:09:25Z (`bvRAlb-removal.log`).
- **82 kept.** They are not event tables: scripts, interim and pilot outputs, and caches. Some may duplicate files elsewhere in the repository, but they were not compared and are left in place. The folder is now 1.8 MB.

No result changes.
