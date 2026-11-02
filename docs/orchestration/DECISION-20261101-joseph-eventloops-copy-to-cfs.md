# DECISION 2026-11-01 (later) — Joseph: copy the twelve per-playlist 5D event loops to CFS

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- Joseph asked: "how do we keep the per playlist event loop files if we need them".
- The twelve per-playlist `runEventLoopOmniFold_5D_<PL>_universes_full_bkgaware.root` files sum to 171,136,404,725
  bytes (159.4 GiB; `ls -l` on login37, 2026-11-01). They have no HPSS or CFS copy (`FD-CT-RETENTION.md` §2), and they are exposed to purge from
  2026-11-09.
- HPSS had 89.2 GiB free (`FD-CT-RETENTION.md` §3), too little to hold them.
- On login37 on 2026-11-01, `du -sh /global/cfs/cdirs/m3246/josephrb` read 3.6T. That is already above Joseph's
  3 TB rule for CFS (`compute-allocations` memory: "as long as I am under 3 TB it is fine").
- Their merge, `…_5D_MEFHC_universes_full_bkgaware.root` (171,117,093,365 bytes), is rebuilt
  from the twelve by the fast merge (`2d-unfolding/2D_OMNIFOLD_REFERENCE.md:104-108`), so it is not copied.
- No lane has named a step that reads these files. coverage-5b (`FD-1B-INV-DECLARATION.md` §8, #641) and
  limitation-resolver (#643) both said so.

> Keep the 12 per-playlist event-loop files (159.4 GiB, no copy anywhere, purge exposure from 11-09) by copying them to CFS? Your CFS area is already 3.6 TB, over your 3 TB rule, so this takes it to ~3.77 TB.

Joseph's answer, verbatim:

> Copy to CFS (Recommended)

sha256 of the text plus a final newline begins `cdd7157386fa4382`.

## What is decided

1. **The twelve files are copied** to `/global/cfs/cdirs/m3246/josephrb/eventloop-5d-bkgaware-preservation-20261101/`.
   - The copy is made on a login node (login37), with `nice -n 19` and no compute charge.
   - The source files' sha256 sums go in `SOURCE.SHA256SUMS`, and `sha256sum -c` against the copies is written to
     `VERIFY.txt`.
   - The script and its log are in the same directory (`copy.sh`, `copy.log`).
2. **The merge is not copied.** If it is needed, it is rebuilt from the twelve.
3. **CFS goes to about 3.8 TB.** Joseph accepted this, above his 3 TB rule, for this copy only.
4. **The pscratch originals are not deleted.** The copy's reads move their access times, as a legitimate use.
5. **The verification is below.**

## The copy, verified (login37, 2026-11-01)

- `copy.sh` ran from 18:48:20Z to 19:19:16Z. It printed `files=12`, `bytes=171136404725` and `verify_rc=0`.
- `VERIFY.txt` reads `OK` for all 12 files.
- The copies sum to 171,136,404,725 bytes, the same total as the sources.
- sha256 of the record files in the CFS directory:
  - `SOURCE.SHA256SUMS`: `c839668bd01abea4fbabe5d19a968e3f681bd69074e79957f1c1d99548de1d43`
  - `VERIFY.txt`: `777397473340b7fbdecfecf5272b2d8120f9e802f5dafe7818b436951f9f848c`
  - `copy.sh`: `1988c6a2c25f2cecfe2d9e2ad42d32530d62cc49510da82194ca595ec616daf9`
  - `copy.log`: `f21ce5295d793e387fb565f0d4556815169b5e41fd0c73504620d5afa1e781e6`
- After the copy, `du -sh /global/cfs/cdirs/m3246/josephrb` reads 3.8T.

Nothing is submitted, deposited or tagged.
