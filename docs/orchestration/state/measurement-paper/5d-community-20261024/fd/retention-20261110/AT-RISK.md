# AT-RISK: the pscratch inputs of the pending declarations, and when each may be purged (2026-11-11)

**By** the valid-region lane (director-helper-2), for the director, who takes the remedy decision to Joseph.

**Under** the director's go of 2026-11-10 for a stat-only check (`receipts/retention_stat.sh` `08e2bd17…`, launcher
`receipts/ret_launch.sh` `5e81664a…`).

**MEASURES:** the size, access time and modification time of 11,165 explicit pscratch paths: every input named by the
pending declarations RPL, RPD-RECO, Tier 3, E96D and V-HALF-R that a committed record names by path.
- Each path was given once to `stat -c "%s %X %Y %n"`.
- No file's contents were read, no directory was listed, no access time moved, and nothing was written on the cluster.

**CANNOT AUTHORIZE:** a copy, an HPSS archive, a deletion, or any keep-alive. The director's ruling: "No keep-alive of
any kind ... the only remedies are copies (HPSS, or CFS from a login node) or regeneration". That decision is
Joseph's.

**CITABLE FOR:** that each listed file existed at 2026-11-11T01:42Z with the size and access time recorded, and the
exposure dates computed by the rule below.

**NOT CITABLE FOR:**
- that NERSC will purge a given file on a given date;
- any file's integrity (no digest was taken);
- the inputs not covered (§3).

## 1. The rule and the run

- **The exposure rule** is FD-CT-RETENTION.md §1's: NERSC says to "assume that any file not accessed within 8 weeks
  may be purged at any time" (`state/2d-closeout/preservation-20261014/REPORT.md:87-88`), and purging runs on a
  fullness threshold.
- **Exposed from** = the group's oldest access time + 8 weeks **(arithmetic, by `receipts/table.py` from the raw
  epochs)**.
- O_NOATIME reads, which every lane uses on these files, never refresh the clock. No file was touched to reset it:
  "Files are never touched to reset atime. NERSC policy forbids circumventing the purge"
  (`COV2D-SCOPING.md:246`).
- **The run:**
  - login27, the quietest of five surveyed (`receipts/login-survey.txt`: load 29.0 on 244 cores);
  - 2026-11-11T01:41:44Z to 01:43:04Z;
  - ssh rc 0, awk rc 0, script rc 0;
  - the staged copy at its approved sha256;
  - the remote side detached, with ServerAlive on both hops (`receipts/ret_launch.sh`).
- **The output** is `receipts/session.txt` (sha256 `92fd8887ba711f059d24f0a25a5dcba4f1349ca31f281612bef04327c0a9b7d0`): one FOUND or MISSING line per path, then the GROUP
  summaries.
- **The list.** `receipts/make_retention_list.py` built it from committed records at origin/main
  `65bbc9d032e149e3d9af27e2da9225771fe01354` (`receipts/list-built-at-main.txt`). It reproduces `all.tsv`
  (`receipts/all.tsv.sha256`), which is embedded in the stat script.
  - #1012's five groups come from its own `make_lists.py` (copied as `receipts/make_lists_1012.py`).
  - The AnaTuples come from the release's committed playlist lists (`data-survey-20261022/outputs/playlist-lists/`).

## 2. The result: all 11,165 present, 0 missing

| exposed from | group | needed by | files (missing) | bytes | oldest atime (UTC; epoch) |
|---|---|---|---:|---:|---|
| **2026-12-09** | `univ2d_per_playlist` | RPL (i) band size | 12 (0) | 171,136,616,965 | 2026-10-14 23:11; 1792019500 |
| **2026-12-15** | `anatuple_data_1B-1P` | RPL (ii-a) join | 1,565 (0) | 908,922,520,965 | 2026-10-20 14:38; 1792507094 |
| **2026-12-15** | `anatuple_data_1A` | RPL (ii-a) join | 253 (0) | 80,610,192,765 | 2026-10-20 15:26; 1792510015 |
| **2026-12-19** | `anatuple_mc_1A` | RPL (ii-a) join | 41 (0) | 706,929,079,280 | 2026-10-24 08:14; 1792829693 |
| **2026-12-19** | `anatuple_mc_1B-1P` | RPL (ii-a) join | 448 (0) | 9,827,031,062,141 | 2026-10-24 08:16; 1792829777 |
| **2026-12-23** | `s1_cmodel_cresp_tables` | V-HALF-R §3; Tier 2 (done) | 5 (0) | 2,282,491 | 2026-10-28 12:44; 1793191469 |
| **2026-12-25** | `zero_loops` | RPL (ii-a) | 12 (0) | 4,841,729,276 | 2026-10-30 08:36; 1793349376 |
| **2026-12-25** | `cpl` | V-HALF-R §3 (C_PL,5D) | 38 (0) | 3,898,100 | 2026-10-30 13:34; 1793367244 |
| **2026-12-26** | `f0b` | V-HALF-R steps 2-4 | 8,545 (0) | 1,581,514,109 | 2026-10-31 21:02; 1793480574 |
| **2026-12-30** | `rpd_dumps` | RPD-RECO; RPL (i), (ii-b) | 24 (0) | 1,577,462,973 | 2026-11-04 11:38; 1793792304 |
| **2026-12-31** | `tier3_inputs` | Tier 3 (FD-PRR's staged inputs, rho arrays) | 8 (0) | 2,164,723,453 | 2026-11-05 10:18; 1793873922 |
| **2026-12-31** | `cstat` | V-HALF-R §3 (C_stat) | 30 (0) | 2,821,266 | 2026-11-05 15:18; 1793891894 |
| **2026-12-31** | `central` | E96D A-D0/A-D1; V-HALF-R | 1 (0) | 95,564 | 2026-11-05 15:18; 1793891895 |
| **2027-01-03** | `shared_inputs` | E96D; Tier 3; V-HALF-R | 2 (0) | 1,564,455,221 | 2026-11-08 23:17; 1794179838 |
| **2027-01-04** | `prr` | Tier 3 (C-PAIR, C-P); V-HALF-R step 3 | 181 (0) | 33,324,255 | 2026-11-09 23:35; 1794267345 |

**Read with the table:**
- **1A is not replaceable from the release.**
  - 1A holds 787,539,272,045 bytes in all (data 80.6 GB + MC 706.9 GB) **(arithmetic)**.
  - The release's 1A is a reprocessing at 1.244× (MC) and 1.056× (data) the size, with the same file names
    (`data-survey-20261022/SURVEY.md:36`). So a purge of our 1A cannot be undone by re-downloading.
  - 1B–1P are identical by size, file for file, to the release (`SURVEY.md:35`), so they can be re-downloaded.
- **Other copies, from the records** (not re-measured here):
  - C_resp is on HPSS at `/home/j/josephrb/mnv-5d-cresp-20261026` (`FD-F0b-REPORT.md`);
  - the s5p A7 calibration products have HPSS and CFS copies (`FD-CT-RETENTION.md` §2, row 4C);
  - HPSS holds only the pooled non-bkgaware `runEventLoopOmniFold_MEFHC_universes_full.root`, not the 12 per-playlist
    2D universe files (FD-CT-RETENTION §2);
  - MP-1 S1, which includes the zero loops, has no HPSS or CFS copy (FD-CT-RETENTION §0, §2).
  <!-- absence-ok: each "no copy" here is FD-CT-RETENTION's own covering search (its §2 Search line), cited, not re-run -->
  - **Added 2026-11-11:** ten groups (zero_loops, cpl, s1_cmodel_cresp_tables, f0b, rpd_dumps, tier3_inputs, cstat,
    central, shared_inputs, prr) are on HPSS at `/home/j/josephrb/mnv-at-risk-20261111/`, verified, with the sources'
    atimes unmoved ([`hpss-20261111/README.md`](hpss-20261111/README.md)).
  - Every other group's copies were not checked.
- **HPSS space.**
  - **Joseph, 2026-11-11 (relayed by the director):** "HPSS usage is 449.3 GB of 512 GB", so about 62.7 GB is free.
    That is less than the 89.2 GiB FD-CT-RETENTION §3 measured on 2026-10-28, which this figure supersedes.
  - The 2D per-playlist universe files (171.1 GB) and 1A's AnaTuples (787.5 GB) do not fit **(arithmetic)**.
  - The small and medium groups Joseph has decided to archive (about 13 GB) do fit, with margin.

## 3. Not covered

These inputs are not named by path in the committed records, so they were not stat'ed:
- RPD-RECO d2's MAT flux files. RPD-RECO records their retention at its own P0 (`FD-RPD-RECO-DECLARATION.md:256`).
- V-HALF-R's pv-ladder C_model products, beyond those F0b reads, which are in `f0b`.

<!-- absence-ok: scoped to the committed records searched for paths while building the list -->

## 4. For the director

- **The first exposure is 2026-12-09:** the per-playlist 2D universe files that RPL (i)'s band-size read needs. The
  band-size read is approved in content and runs after RPL-BINDING-1, so it can finish well before.
- **Next, from 2026-12-15:** the AnaTuples RPL (ii-a)'s join would read, 1A among them. Then the zero loops, from
  2026-12-25.
- **The remedy is a copy** (HPSS, or CFS from a login node) **or regeneration,** and it is Joseph's decision. Nothing
  here copies, archives or touches any file.

Nothing is submitted, deposited or tagged.
