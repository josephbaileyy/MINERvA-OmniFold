# Preservation facts for draft A: the 1B–1P MC against the public release, and storage (2026-10-14/15)

**Answer: ALL 448 IDENTICAL.**

Our 448 ME-FHC MC AnaTuples for playlists 1B–1P are byte-identical by adler32 to the current public MINERvA open-data
files, and every pair has equal size. A fresh download therefore reproduces them, as of 2026-10-14. The only MC that
cannot be re-obtained is our 41 Playlist 1A files: 706,929,079,280 B (0.707 TB, 658.4 GiB). They exist only on
`/pscratch`, and they become purge-eligible from 2026-12-09.

**CITABLE FOR:**
- adler32 byte identity of the 448 1B–1P MC files against the public files, as of 2026-10-14/15;
- the two 1A controls differing from the public files;
- the storage facts in §3, at the times given;
- the xattr side effect on three inputs (§1).

**NOT CITABLE FOR:**
- the checksums of the other 39 1A MC files. Only 2 were run, as controls;
- any Data file against the public release. Data was checked only against our own manifest, by name and bytes;
- the public files staying unchanged after 2026-10-14;
- any physics effect;
- a decision on the 3 TB rule, on HPSS space, or on sending draft A.

| field | content |
|---|---|
| `Context` | Joseph's approval of 2026-10-14 ([`../../../DECISION-20261014-joseph-2d-endpoint-and-open-items.md`](../../../DECISION-20261014-joseph-2d-endpoint-and-open-items.md) item 5): check by checksum that 1B–1P can be re-downloaded, re-measure the storage facts that draft A needs, then revise A |
| `Who` | A Claude Opus 5.5 subagent of the paper-tighten lane (director) measured this. The director re-counted `outputs/checksum_table.tsv`: 448 rows `1B-1P` MATCH, each with equal adler32 and equal local and remote size; 2 rows `1A-control` MISMATCH; 450 distinct remote values; 9,827,031,062,141 B read for the 448. The director also re-read the 3 TB rule wording (below) and the Stage C input copy record. The director wrote this REPORT |
| `Compute` | No Slurm job; 0 node-h. The remote checksum queries ran on `login29`. The local reads ran on `dtn01.nersc.gov`, as the 2026-10-09 sha256 sweep did, with 4 streams at nice 19 and ionice idle |
| `Evidence` | [`scripts/`](scripts/) and [`outputs/`](outputs/). The table is `outputs/checksum_table.tsv`, with its summary in `checksum_summary.json`; the storage facts are in `storage_facts.json`. Raw copies are on the cluster at `/pscratch/sd/j/josephrb/tmp-mc-checksums-20261014/` |

## 1. Method, and a side effect of the earlier probe

**`xrdadler32` was not used on the inputs.** It writes its result into the file's `user.XrdCks.adler32` extended
attribute. Later calls then return that cached value without reading the file: a 20 GB file "answered" in 0.05 s.

**The earlier Q2 probe left such attributes on three inputs.** That probe was
[`../stageD-inputs/q2-opendata-20261014/outputs/adler.sh`](../stageD-inputs/q2-opendata-20261014/outputs/adler.sh),
run at about 14:31Z on 2026-10-14. The three files are 1A `run00110001`, 1D `run00111100` and 1P `run00112000`
(`outputs/xattr_inventory.tsv`).
- Their ctimes moved.
- Their size, mtime and content are unchanged: all 489 MC files still equal `ANATUPLE-SHA256.tsv` on bytes and mtime.
- The attributes were left in place, since removing them would also modify the inputs.

**What was used instead.** `scripts/adler32_file.py` computes Python `zlib.adler32`. It opens each file read-only with
`O_NOATIME` and records the bytes read against the file size. It was validated three ways:
- on a random 123,456,789 B fixture, against `xrdadler32` (`db4887fc`);
- on an empty file;
- on 1P `run00112000`: it read all 20,328,781,801 B and gave `fdbb0df7`, the value already in `adler.txt`.

A stat of all 489 MC files before and after the reads (size, mtime, atime, ctime) shows no change
(`outputs/mc_stat_pre_vs_post_diff.txt`).

**Remote side.** The remote values come from `xrdfs root://fndca1.fnal.gov:1095 query checksum`, with a 90 s timeout.
- A timeout or a malformed reply counts as an error, never as a checksum.
- A negative control, a file that does not exist, returned an error (rc 54).
- The value is the checksum dCache stores. dCache computed it; we did not.

## 2. Results

**Remote:** 450/450 returned, 0 errors (`login29`, 2026-10-14 23:12–23:17Z).

**Local:** 450/450 read in full, 0 errors (`dtn01`, 23:12Z to 00:19Z on 2026-10-15).

| population | files | verdict |
|---|---:|---|
| 1B–1P MC | 448 | **448 MATCH**, 0 mismatch, 0 error; sizes equal |
| 1A controls (`run00110000`, `run00110001`) | 2 | 2 MISMATCH, as expected (remote `b4118698` / `cd524740`; local `689b3b0e` / `cdb0621a`) |

## 3. Storage facts

- **HPSS (user `josephrb`).** 350.90 GiB of 512.00 GiB is used (68.5 %; `showquota --hpss` and `hsi du -s`, 57
  files). About 161.1 GiB is free. **The 1A MC (658.4 GiB) does not fit.**
- **CFS `/global/cfs/cdirs/m3246/josephrb`.** `du` gives 3,239,895,250,944 B: 3.240 TB, which is 2.947 TiB or
  3,017.4 GiB. That is up 505 GiB from 2026-10-09. The 2026-10-12 Stage C input copy (539 GB,
  [`../stageB/diagnostics/REPORT.md`](../stageB/diagnostics/REPORT.md) §6.1) accounts for the growth.
- **The rule.** Joseph's rule is "as long as I am under 3 TB it is fine", measured by `du` on this directory. In
  decimal TB the usage is **about 0.24 TB over**. In TiB it is 54.6 GiB under. The Stage B diagnostics record's "(≥ 3
  TB rule met)" checked free space on the file system, not our own usage. That was the wrong operand. Whether to act
  is Joseph's call.
- **Data on CFS.** All 1,818 Data files and 67 flux/parameter files are in the 2026-10-09 CFS copy, with names, bytes
  and mtimes equal to the manifest: 989,696,077,171 B. Their sha256 verification is in the 2026-10-09 and 2026-10-10
  records.
- **1A MC copies elsewhere.** None were found in our `/pscratch` (other than the originals), our home, our CFS area,
  HPSS or this laptop. A name search of the m3246 group CFS was still running at writing. It cannot be complete in
  any case, because 68 member subdirectories are permission-denied.
- **Purge exposure.** All 41 1A atimes fall on 2026-10-14, from today's reads. So the earliest 8-week eligibility is
  **2026-12-09**.
  - NERSC's documentation says purging runs when scratch reaches a fullness threshold. It adds that users should
    "assume that any file not accessed within 8 weeks may be purged at any time".
  - Our purge records show real purges, of flux and parameter files, on 2026-06-08 and 2026-08-03.
  - Our `/pscratch` usage is 16.77 of 20.00 TiB.

## 4. Limits

- **Strength of the checksum.** adler32 is a 32-bit checksum. With equal sizes it is strong evidence of identity for
  these files, but not a cryptographic proof. The public side publishes adler32 only. Our local sha256 values are in
  the manifest.
- **The group search.** Its m3246 part was still running at writing (`find1A/`). See §3.
- **The CFS measurement.** Only the block-byte `du` stands. The redundant GiB and apparent-size passes were stopped.
- **A leftover file.** A 123 MB test fixture remains at
  `/pscratch/sd/j/josephrb/tmp-mc-checksums-20261014/testfix/rand.bin`.
