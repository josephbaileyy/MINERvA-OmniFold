# RSN's HPSS archive: the run of 2026-11-12 (receipt)

**By** session tier3-design, under the director's go of 2026-11-12 for exactly `hpss_rsn.sh` `012a9618…` and
`hpss_rsn_launch.sh` `cd826dbd…` (kit rev 2, #1084 head `e304a7ee`; coverage-5b-audit's delta audit, GO at
`4b36fa09` and at `e304a7ee`).

**The result:** `ARCHIVE PASS: all three groups archived, hash-verified and every member re-read from HPSS`
(`cluster/logs/archive.log.txt:56`), rc 0 (`:58`).
- **Where:** `/home/j/josephrb/mnv-rsn-inputs-20261111/`, one `<group>.tar` per group with its `.idx`
  (`cluster/logs/archive.log.txt:48-53`).
- **Size:** three tars, 24,822,272 bytes, plus 40,824 bytes of `.idx` (**arithmetic**, from `:48-53`). Source bytes:
  24,749,106 (`:9`).
- **What:** the 67 files of `../hpss_rsn_list.tsv` (`0dafaac8…`), 36 in pvl_prep, 30 in pvl_products and 1 in
  cpl_block. Every source's sha256, read once by O_NOATIME, equals its committed pin (`:13`, `:24`, `:35`). Every
  member re-read from HPSS equals its manifest line and its pin (`:21`, `:32`, `:43`). hashverify is OK for each tar
  (`:19`, `:30`, `:41`).

## What ran, in the director's order

1. **The survey** (`connect/survey.session.txt`, 00:38:25Z) covered #1054's five login nodes. It chose **login27**:
   loadavg 0.60/0.47/0.46 and 352G free in /dev/shm (`:85`), the lowest 5- and 15-minute load. login05's 1-minute
   figure was lower (0.35) but its 15-minute was 1.78 (`:29`).
2. **The probe** (`connect/probe.session.txt`, login27, 00:38:46Z) met the full gate:
   - the tools: hsi, htar, hpssquota, timeout, setsid, sha256sum, python3 (`:3-9`);
   - `home rc=0` (`:16`);
   - `target rc=64` with `HPSS_ENOENT` (`:17-19`);
   - `$OUT` absent (`:20`);
   - `O_NOATIME True` (`:21`);
   - `slurm_job=''` (`:2`);
   - squeue showing only 61078463 (ll5d_gate_G18) and 61078506 (ll5d_gate_AR23), the two the director allowed (`:22-24`);
   - both stat passes `67 ok` with no `ZERO` (`:26-29`).

   `connect/probe.session.err.txt` holds only NERSC's login banner and names no source path (the director's k6 check).
3. **The archive** (`connect/archive.session.txt`): staged on login27 at sha256 `012a9618…`, run detached, script
   rc 0. The log ran from 00:39:07Z to 00:39:16Z (`cluster/logs/archive.log.txt:1,58`). The log's own lines give the
   script sha (`:2`) and the list sha with 67 rows (`:3`).
   - The setup checks ([RSN-6]) passed before `$OUT` existed: the tools (`:4`), the home (`:5`), the target (`:6`) and
     hpssquota (`:7-8`).
   - Quota preflight: free 55,587,614,228 bytes, which is Joseph's figure (62.7e9) or less, against 49,994,342 needed
     (`:9-10`).
   - `/dev/shm/josephrb-hpss-rsn` was removed (`:57`).
4. **The fetch** (`connect/fetch.session.txt`): `post.tar.gz` `919a6954…` and the live `archive.log` `b9f875e3…`.
   - The live log is `cluster/logs/archive.live.log.txt`. It is the tarred log plus one final line, the tarball's own
     sha256 `919a6954…` (`:59`), which equals the fetched file's.
   - Unpacked into an empty directory: the cluster's copy of the script is byte-identical to `../hpss_rsn.sh` (`cmp`;
     not committed again). `cluster/archive_list.tsv` is byte-identical to `../hpss_rsn_list.tsv`. The 67 manifest
     lines in `manifests/SHA256SUMS.*` equal the list's pins, row for row.

**Files.** `cluster/logs/` holds the script's logs: a `.log` gets a `.txt` suffix, as in #1054, since the repository
ignores `*.log`. `manifests/` holds the three SHA256SUMS and the three `stat.<group>.tsv` (size, mtime_ns, path).
`connect/` holds the four session outputs.

**Not touched.** Nothing was written outside `$OUT` (`/pscratch/sd/j/josephrb/hpss-rsn-20261111/`), the removed
/dev/shm stage and `$H`. No source was read plainly. The two LL5D gate jobs were running throughout; cov2d had
reported no overlap by path or inode.

**Earlier on 2026-11-12,** rev 1's stat-only probe on dtn01 (00:07:48Z) found no hsi, htar or hpssquota there and
STOPped before anything was written (`../README.md`).

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** these 67 files being on HPSS at `/home/j/josephrb/mnv-rsn-inputs-20261111/`, as of 2026-11-12T00:39Z,
  with every member re-read from HPSS and equal to its committed pin.
- **Not citable for:** a tested restore to pscratch, which was not done; any file outside the list; HPSS residency
  (tape or disk level) at any later date.
