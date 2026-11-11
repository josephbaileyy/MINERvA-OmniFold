# HPSS archive of the small and medium at-risk inputs: ten groups, 8,846 files, all verified (2026-11-11)

**By** the valid-region lane (director-helper-2), for the director.

**Under** Joseph's decision, relayed by the director on 2026-11-11: archive zero_loops, cpl, s1_cmodel_cresp_tables,
f0b, rpd_dumps, central and cstat, tier3_inputs, shared_inputs and prr to HPSS now. 1A is left to Joseph and Ben.
The director's GO was for exactly `hpss_atrisk.sh` `388cadb4`, `hpss_launch.sh` `296ea772` and `cov2d_fence.sh`
`16a2a5cd`.

**The result:** `ARCHIVE PASS: all ten groups archived, hash-verified and retrieval-checked`
(`cluster/logs/archive.log.txt:146`), rc 0 (`:148`).
- **Where:** `/home/j/josephrb/mnv-at-risk-20261111/`, as one `<group>.tar` per group with its `.idx`.
- **Size:** 10 tars, 11,781,843,456 bytes (**arithmetic**, from `cluster/logs/hsi-ls-after.txt`).

## What ran

- **The survey and fence.** The survey at 2026-11-11T02:44:21Z chose login27 (`connect/login-survey.txt`: loadavg
  12.04, 320G free in /dev/shm). The fence ran at 02:44:46Z: no cov2d or t2a job queued, 28 sacct rows in 14 days, none
  unended, `FENCE CLEAR` (`connect/fence.session.txt`).
- **The archive:** login27, 02:44:58Z to 02:54:35Z (`cluster/logs/archive.log.txt:1,148`). It was launched detached,
  staged at sha256 `388cadb42b723237ffd16df9652bd0f05a3bc1baae337db66f191692f834e5a5` (`connect/archive.session.txt`;
  the log's own line is `:2`).
  - The cluster's copy of the script is byte-identical to `connect/hpss_atrisk.sh` (`cmp`).
  - The script's code is `connect/hpss_atrisk.template.sh` with only its `LIST_SHA` line filled in. The list is
    embedded after `__LIST__` by `connect/make_hpss_script.py`.
- **The list:** the 8,846 FOUND rows of the ten groups in AT-RISK's stat output (`../receipts/session.txt`, sha256
  `92fd8887…`). The list's sha256 is `00e27576…`, and the run checked 8,846 rows at that sha (`:3`). Each group's
  count and bytes equal its GROUP line there.
- **The fetch** (`connect/fetch.session.txt`): `post.tar.gz` `0a0fbd58…` and the live `archive.log` `7be4f2d8…`.
  They were unpacked into an empty directory and read with `python3 -I`.

## Access times: htar never read pscratch

- **The constraint.** htar opens its inputs itself and has no O_NOATIME option. Archiving the pscratch paths would
  have set every source's atime to the archive time, refreshing the purge clock, which the director's ruling forbids.
- **What was done instead.** Each group was first copied file by file to `/dev/shm` by `os.open(O_RDONLY |
  O_NOATIME)`, hashing the bytes read.
  - Every file's size and mtime were required to equal AT-RISK's stat.
  - Its size, mtime and atime were required to be unchanged by the copy.
  - Any failure is a STOP; none occurred (`STAGE OK` for each group).
- **The archive and cleanup.** htar archived the /dev/shm copy, with the source's mode and mtime restored on it. The
  copy was then removed, and the work directory is gone (`:147`).
- **So the sources' atimes did not move.** AT-RISK's exposure dates for these pscratch copies are unchanged by this
  archive.

## Per group (`cluster/logs/`)

Each group passed all four steps:
1. stage, writing manifest `SHA256SUMS.<group>`;
2. `htar -Hcrc -Hverify=1`, with `HTAR: Verify complete. 0 total errors` and `HTAR SUCCESSFUL` (`htar-<group>.log.txt`);
3. `hsi hashcreate`, then `hsi hashverify`: `<tar>: (md5) OK` (`hashverify-<group>.log.txt`);
4. retrieval of the manifest (`cmp` equal) and of the group's smallest file, whose sha256 equals its manifest line
   (`archive.log.txt`, the `retrieved` lines).

| group | files | source bytes | tar bytes (`hsi-ls-after.txt`) | manifest sha256 | PASS (`archive.log.txt`) |
|---|---:|---:|---:|---|---|
| s1_cmodel_cresp_tables | 5 | 2,282,491 | 2,289,664 | `e5ffe13a…` | `:21` |
| zero_loops | 12 | 4,841,729,276 | 4,841,755,648 | `c6c641ca…` | `:32` |
| cpl | 38 | 3,898,100 | 3,934,720 | `e97c197e…` | `:43` |
| f0b | 8,545 | 1,581,514,109 | 1,590,736,896 | `07d248ef…` | `:54` |
| rpd_dumps | 24 | 1,577,462,973 | 1,577,486,336 | `7638f94f…` | `:65` |
| tier3_inputs | 8 | 2,164,723,453 | 2,164,736,000 | `1402bc1f…` | `:76` |
| cstat | 30 | 2,821,266 | 2,849,280 | `360ae931…` | `:87` |
| central | 1 | 95,564 | 99,328 | `b501f7ec…` | `:98` |
| shared_inputs | 2 | 1,564,455,221 | 1,564,460,032 | `7c839d0a…` | `:109` |
| prr | 181 | 33,324,255 | 33,495,552 | `ffb84f75…` | `:120` |

**The manifests are the archived files' sha256s,** in `manifests/` as `digest  /pscratch/...`. Each is also the first
member of its tar. Restore with `cd / && htar -xf /home/j/josephrb/mnv-at-risk-20261111/<group>.tar`, since member
names are the paths without the leading `/`.

**Cross-checks against committed pins** (computed here with `python3 -I`):
- `SHA256SUMS.zero_loops` equals all 12 `ZERO_LOOPS` pins (`nd-unfolding/fd_ct_period_inputs.py:58`).
- `SHA256SUMS.rpd_dumps` equals `fd/rpd-reco/INPUTS.sha256` on all 24 paths, with the same path set.
- `SHA256SUMS.central` is `fb5cc679…`, (e)'s product as pinned in `fd/e96-data-20261110/E96D-DECLARATION.md`.
- `SHA256SUMS.shared_inputs` holds `of_inputs_5d.npz` `07fccc1a…` and `bkg_dump.npz` `2addac8f…`, as pinned there.

## HPSS space

- **Before:** `hpssquota` showed 449.25GiB of 512.00GiB (`cluster/logs/quota-before.txt`).
- **The preflight** took free = min(live 67,377,299,456 B, Joseph's 62.7e9 B) = 62,700,000,000 B, against a need of
  1.2 × 11,806,295,552 B = 14,167,554,662 B. `PREFLIGHT OK` (`:7-9`).
- **After:** `hpssquota` still showed 449.25GiB (`quota-after.txt`). HPSS usage accounting is not updated at once, so
  this is not a measurement of the archive's footprint. The footprint is the 11.78 GB of tars above plus 6,077,328
  bytes of index files (**arithmetic**, `hsi-ls-after.txt`).
- **Expected usage** is therefore about 460.2 GiB of 512 once the accounting catches up (**arithmetic**: 449.25 GiB +
  11.79e9 B ÷ 2³⁰). That expectation is not measured.
  <!-- absence-ok: a scoping statement about this record's own arithmetic projection, not a claim that a result does not exist -->

## Licence

**CITABLE FOR:** an HPSS copy of each of the ten groups' 8,846 files, at the listed paths, made 2026-11-11 and verified
by htar's CRC verify, hsi hashverify and a retrieval per group; the files' sha256 manifests; and that the archive did
not move the sources' access times.

**NOT CITABLE FOR:**
- any file outside these ten groups, 1A's AnaTuples and the 2D per-playlist universe files among them;
- a full retrieval test (one file and the manifest per group were retrieved);
- the HPSS usage after the archive (not yet reported by hpssquota);
- that NERSC will or will not purge the pscratch copies (their exposure dates in `../AT-RISK.md` stand).

Nothing is submitted, deposited or tagged.
