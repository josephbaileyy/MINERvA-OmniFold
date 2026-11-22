# RPD-RECO flux connect 1 products archived to HPSS: ARCHIVE PASS (2026-11-21)

**By** tier3-design, under the director's standing go of 2026-11-21, which relays Joseph's authorization ("I authorize
all the runs and compute you need to do …"), and per [`../ARCHIVE-PLAN.md`](../ARCHIVE-PLAN.md). One login node,
login25. No Slurm job, 0 node-h. Nothing deleted, nothing written to CFS.

**CANNOT AUTHORIZE:** removal of anything on pscratch, and any RPD-RECO step.

## The result

`ARCHIVE PASS: all 1 groups (flux1) archived, hash-verified and every member re-read from HPSS` (`logs/archive.log.txt`).
- **Target:** `/home/j/josephrb/mnv-rpd-reco-flux1-20261121/flux1.tar`, with its `.idx`.
- **Restore:** `cd / && htar -xf /home/j/josephrb/mnv-rpd-reco-flux1-20261121/flux1.tar`. The member names are the
  source paths without the leading "/".
- **Contents:** 13 files, 591,702,082 bytes, from `/pscratch/sd/j/josephrb/rpd-reco-flux-20261111/run/`: the factor
  products `flux-factors-{1A..1P}.npz` and `flux-extract.json`.
- **The 24 dumps** were already archived on 2026-11-11: group `rpd_dumps` of `/home/j/josephrb/mnv-at-risk-20261111/`,
  ARCHIVE PASS (`fd/retention-20261110/hpss-20261111/README.md`). They were not copied again.

## How it ran

All times are UTC.
- **Fence.** Acks at 10:35:59–10:36:02Z from cov2d, limitation-resolver and director-helper-3, all reporting no jobs.
  The connect ran by 10:37:14Z, inside 15 minutes of the oldest ack.
- **Survey (10:36:18Z).** Login nodes 38, 21, 25 and 05 were surveyed. login25 had the lowest load (22.04).
  See `session/survey.session.txt`.
- **Probe (10:36:42Z), read-only.** See `session/probe.session.txt`.
  - The tools were present and O_NOATIME is available.
  - The HPSS target did not exist (hsi rc 64).
  <!-- absence-ok: the archive's own pre-check record (hsi's not-found rc 64 for the new target), not a claim about a result -->
  - hpssquota read 460.72 GiB of 512 GiB.
  - Both stat passes found all 13 paths, none of size 0.
  - The only job in the queue was t3p_dry 61726250, PENDING.
- **Archive (10:36:51–10:37:14Z).** The script was `hpss_flux1.sh` (`d38dba5b…`), whose staged copy was checked on the
  node. See `session/archive.session.txt` and `logs/`.
  - list sha256 `c69a9d38…`, 13 rows;
  - preflight OK: free 55.1 GB against a need of 0.73 GB;
  - `STAGE OK flux1: 13 files, 591702082 bytes, every sha256 equal to its pin`, by O_NOATIME copy into /dev/shm, with
    stat recorded in `manifests/stat.flux1.tsv`;
  - htar rc 0;
  - hashcreate rc 0;
  - `hashverify … flux1.tar: (md5) OK`;
  - `RETRIEVE OK flux1: 13 members re-read from HPSS, every sha256 equal to its manifest line and pin`;
  - /dev/shm removed.
- **The fetch.** `post.tar.gz` (`ee200989…`) and the archive log, by scp through saul.
- **Laptop check.** `manifests/SHA256SUMS.flux1` (`e8fff1c3…`) against `../hpss_flux1_list.tsv`: 13 of 13 equal to
  their pins, no extra row. VERIFY PASS.

## Pins

The factor products' digests are those in the committed `../../run-61206960/records/run/flux-extract.json`.
`flux-extract.json`'s own digest is that committed copy's sha256, `f4855544…`.

`*.log` is gitignored, so the logs are committed as `*.log.txt`. `logs/hpss_rsn.sh.txt` is the kit's copy of the script
that ran, under the template's historical filename.
