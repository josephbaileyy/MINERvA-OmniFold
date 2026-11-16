# RSN's HPSS archive kit, rev 2 (2026-11-12), for the director's go

**By** session tier3-design, at the director's ruling on RSN rev 2: "archive now, the ~25 MB: pv-ladder prep/,
products/ and cpl_block.npz", under hpss-20261111's discipline (#1054). Rev 2 follows the director's ruling of
2026-11-12: run on a login node, as #1054 did. **The archive has not run.** It runs only after coverage-5b-audit's
delta audit against rev 1 (`5542d5fe`), the director's go for these exact sha256s, and the probe below, while Joseph's
certificate is valid.
<!-- absence-ok: an operational status of this kit's own run (the archive was never started; the dtn01 probe record below), not a claim that a result does not exist -->

**Why rev 2.** Rev 1 (`5542d5fe`, merged in #1082 at `950656d5`) required a data-transfer node. The director's
stat-only probe on dtn01 (2026-11-12T00:07:48Z, ssh rc 0) found no `hsi`, `htar` or `hpssquota` on its
non-interactive PATH (`command -v` printed none of the three; `bash: line 1: hsi: command not found`). The archive was
not started, so OUT and H are unspent. #1054 ran on login27, where all three worked non-interactively
(`fd/retention-20261110/hpss-20261111/connect/archive.session.txt:2`, `cluster/logs/archive.log.txt:1`).

| file | sha256 | role |
|---|---|---|
| `hpss_rsn.sh` | `012a9618adf7e4b493700954747f5afd1ea4235907c1b2f794e754e2062311d8` | the archive script: the template with its list embedded (what runs) |
| `hpss_rsn_launch.sh` | `cd826dbde2acc571fab313c87d76c5be65df0dbaf2ca67589b14139d7ed49ab9` | the Mac-side launcher: survey, probe, archive and fetch modes, through saul to a loginNN |
| `hpss_rsn.template.sh` | `7aaa9a060e4acfa40f75fe46f7642954fb3b378bafd1652fe60f78fa2e2449a3` | the template; `make_hpss_script.py` fills in `LIST_SHA` and appends the list |
| `hpss_rsn_list.tsv` | `0dafaac8e3664875f496974fb79f73e319ada7647eb5106dbe6626cefa9d99c6` | 67 rows, group<TAB>sha256<TAB>path (unchanged from rev 1) |
| `make_hpss_script.py` | `d2f2a43a072c10621daa5d4fa3d81b64c7e84ee1b8643432a0315823b71780ee` | byte-identical to hpss-20261111's `connect/make_hpss_script.py` (unchanged) |
| `smoke.txt` | — | the local smoke run at these bytes (below) |

**What it archives.** 67 files, every one an explicit path with its committed sha256 pin:
- **pvl_prep:** pv-ladder's `prep/`, 36 files, pinned by `nd-unfolding/pv-ladder/prep-SHA256SUMS`;
- **pvl_products:** pv-ladder's `products/`, 30 files, pinned by the `products/` rows of
  `state/measurement-scoping/pv-ladder/receipts/SHA256SUMS`;
- **cpl_block:** `fd-ct-5b-addition-20261031/with/block/cpl_block.npz`, pinned by its output digest `d9aa32fd…` in
  CT-5B addition's `fd/receipts-ct/5b/addition/run/chain.json:626` (rev 1 credited F0b's `--extra-block-sha256`; F0b's
  step3.sh pins `cresp.npz`, so that citation was wrong: audit low k5).

The target is `/home/j/josephrb/mnv-rsn-inputs-20261111/`, one `<group>.tar` per group. The output goes to
`/pscratch/sd/j/josephrb/hpss-rsn-20261111/` (logs, manifests, `stat.<group>.tsv`). cov2d reported no overlap
between the 67 sources and anything its fence or the running LL5D gates read, by path and by inode (2026-11-12).

**The discipline, as #1054's.**
- Every source is read once by `os.open(O_RDONLY | O_NOATIME)` into `/dev/shm`, so htar never reads pscratch. The
  sources' atimes, and so their purge clocks, do not move.
- Size, mtime and atime must be unchanged by the copy, and the bytes read must equal the size.
- htar runs with `-Hcrc -Hverify=1`, followed by `hsi hashcreate` and `hashverify`.
- The quota preflight must pass, and the HPSS target must not exist, so nothing is overwritten.
- Any failure is a STOP (exit 8). Nothing is repaired or deleted.

**Six changes from #1054, each marked `[RSN]` in the template.** Changes 2, 3 and 5 are as audited in rev 1.
1. **(rev 2)** It refuses unless the host is a login node (`loginNN`) and no Slurm job is set. Rev 1 required a `dtnNN`.
2. Each file's sha256 must equal its committed pin, which is stronger than #1054's size and mtime check against a
   stat list. Size and mtime are recorded beside the manifest.
3. **Every member is re-read from HPSS:** `htar -xf` of the whole tar into `/dev/shm`, and each retrieved file's
   sha256 must equal its manifest line and its pin. #1054 retrieved only each group's smallest file.
4. It has no squeue fence in the script. The sources are only read, by O_NOATIME, never written, and cov2d has
   reported no overlap. Rev 1's reason, that a DTN is not a Slurm client, no longer holds on a login node, so the
   launcher's probe prints `squeue -u josephrb` before the archive, and the director's go is the fence.
5. The /dev/shm headroom is twice the group's bytes plus 256 MiB.
6. **(rev 2, the director's ruling and audit low k2)** Every setup check runs before `$OUT` exists, so a setup
   failure cannot spend the one run:
   - `hsi`, `htar`, `hpssquota`, `timeout` and `sha256sum` must be on PATH;
   - `hsi -q "ls -d /home/j/josephrb"` must return rc 0;
   - the target check must return hsi's own not-found: rc 64 with `HPSS_ENOENT` in its output, as #1054's did
     (`cluster/logs/target-check.txt`, `archive.log.txt:4`). rc 0 means the target exists. Any other rc, including
     127 (no hsi) and 124 (no answer in 300 s), refuses. Rev 1 read every rc other than 0 and 124 as "absent";
   - `hpssquota` must return rc 0 with one "usage on HPSS" line, which the preflight then reads from the capture.
   A refusal prints `REFUSED (nothing written): <reason>` and exits 9.

**The launcher (rev 2).** Its hop is #1054's `hpss_launch.sh`: saul.nersc.gov, then the login node, with ServerAlive
15/8 on both hops. One setting differs. The inner hop uses `StrictHostKeyChecking=accept-new` where #1054 used `=no`
(the director's ruling, 2026-11-12). That settles audit low k4: a login-node key saul has not seen is accepted, so the
session does not fail at rc 255, but a changed key is refused, so the hop fails (rc 255, before anything runs) rather
than trusting it silently. Modes:
- `survey <dir> "<loginNN> ..."`: read-only; each node's loadavg, nproc and /dev/shm line, as #1054's
  `connect/login-survey.txt`. The node with the lowest load and ample /dev/shm is chosen.
- `probe <dir> <loginNN>`: read-only, on the chosen node. It prints the tools, /dev/shm, `hpssquota`, hsi's listing
  of the HPSS home and of the target, the `$OUT` path, O_NOATIME, `SLURM_JOB_ID` and `squeue -u josephrb`. It also
  runs, twice, `stat -c "%s %F %n"` over the 67 listed paths counted as `ok` or `ZERO` (the director's step 1b). The
  paths travel on stdin, and the launcher first checks the list's sha256.
- `archive <dir> <loginNN>`: the pinned `hpss_rsn.sh`, staged in `/dev/shm` and run only if its sha256 there equals
  `012a9618…`, detached as in #1054.
- `fetch <dir>`: scp of `$OUT/post.tar.gz` and `$OUT/logs/archive.log` through saul.

**Gate before the archive.** The probe must show every tool present, `home rc=0`, `target rc=64` with
`HPSS_ENOENT`, `$OUT` absent, `O_NOATIME True`, an empty `SLURM_JOB_ID`, only the jobs the director lists in
`squeue`, and both stat passes `67 ok` with no `ZERO`. Anything else is a STOP to the director.

**If a STOP comes after the setup checks (audit low k1).** The script creates `$OUT` just after the setup checks, and
`$H` after the quota preflight (`hsi mkdir`). A STOP after `$OUT` exists uses up OUT, and a STOP after `hsi mkdir`
uses up H too: the script refuses to start again while either exists. **Nothing is retried.** Recovery is a new kit
with new OUT and H constants, which means a new sha, a delta audit and the director's go. A partial H stays on HPSS,
and the next kit's README reports it. Neither is deleted.

**The smoke run (local, `smoke.txt`).** It used stubs for `hsi`, `htar`, `hpssquota` and `timeout`, synthetic
sources with real sha256 pins, and for the launcher stub `ssh` and `scp` that run each remote string locally and never
connect. macOS has no O_NOATIME. In the first case the sources' atimes were set older than their mtimes, so the plain
read moved atime and the script STOPped at the atime guard, as it must. The other cases neutralized only that
comparison.

| case | result |
|---|---|
| a read that moves atime | STAGE STOP at the first file |
| the pass path | `ARCHIVE PASS`; three tars; every member re-read and equal to its pin |
| a wrong pin in the second group | STAGE STOP there; the first group's tar stays and is reported |
| one byte corrupted on retrieval | RETRIEVE STOP ("1 differing") |
| a row count other than declared | STOP |
| an existing HPSS target | refused, nothing written (rc 9) |
| a dtn host, or a Slurm job set | refused, nothing written (rc 9) |
| no hsi on PATH | refused, nothing written (rc 9) |
| hsi home listing rc 1 | refused, nothing written (rc 9) |
| target check rc 1, 127, 124, or 64 without HPSS_ENOENT | refused, nothing written (rc 9) |
| hpssquota rc 2, or no usage line | refused, nothing written (rc 9) |
| launcher probe | 67 rows arrive on stdin; the two-hop quoting is intact |
| launcher archive | staged at `012a9618…` (macOS has no setsid, so the detached run stops there) |
| launcher with a dtn node, or a non-empty directory | refused (rc 9) |

**To run (after the audit and the go), in order:**
1. `bash hpss_rsn_launch.sh survey <new empty dir> "<loginNN> ..."`, then choose the node;
2. `bash hpss_rsn_launch.sh probe <new empty dir> <loginNN>`, and check the gate above;
3. `bash hpss_rsn_launch.sh archive <new empty dir> <loginNN>`;
4. `bash hpss_rsn_launch.sh fetch <new empty dir>`, then commit the fetched logs, manifests and `stat.*.tsv` as the
   receipt.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the kit and its local smoke behaviour.
- **Not citable for:** any archive having been made.
