# rpd_flux3, job 61861637: the run's records (2026-11-23)

**By** limitation-resolver, under [`FD-RPD-RECO-BINDING-2-ADDENDUM-2.md`](../../../../FD-RPD-RECO-BINDING-2-ADDENDUM-2.md)
(merged 377a75ff), at M_F3 = `710f9e059c7b664a6b3c1d0e2ef99db80207f8dc`. This is the flux rerun on the sacct-only custody
described in [`../README.md`](../README.md).

**Result: COMPLETED, rc 0, in 8 min 51 s.** Each ruling-4 check holds, and **FLUX2 IDENTITY: 12/12 byte-identical**. The
products stay on pscratch.

- **CITABLE FOR:** the rerun's flux selection digest, its factor products' sha256, their identity with flux2's, and its
  custody records.
- **NOT CITABLE FOR:** any RPD-RECO result, or P0 READY, which is bound separately.

## Preconditions (ruling 2)

- **The bound files.** The launch ran from a worktree detached at M_F3. All six bound files hashed to the addendum's
  values there, and the `flux3-20261123/` tree at M_F3 equals the audited head 97b4805a.
- **cov2d's ack.** cov2d gave it at 2026-11-23T15:34:26Z. The ack file is cov2d's reply verbatim under the line
  `ACK-UTC 2026-11-23T15:34:26Z`. The launcher read it at age 46 s and copied it byte for byte into the session as
  [`connect/ack.txt`](connect/ack.txt) (sha256 `fa3faa69…`). cov2d had no job queued or running and no write in flight.
  It would start no cov2d or t2a job touching flux3's inputs or root until this job was reported finished, and it had
  no objection.
- **tier3-design's ack.** Given at 2026-11-23T15:33:50Z, verbatim in
  [`acks/tier3-design-ack.txt`](acks/tier3-design-ack.txt). It had no job in flight, its roots are disjoint, and it
  holds new job families touching these inputs.
- **The cert check.** The launcher read the cert as valid to 2026-11-24T05:57:28Z.
- **The run root.** Absent before the connect, per the survey below and the connect's own guard.
- **Fence mode.** Not run. The connect's sacct fence and `fence_overlap.py` both read CLEAR (below).

## The survey: [`survey/`](survey/)

The bound launcher (`rpd_flux3_launch.sh`, `91ae3a6a…`) ran in its `survey` mode at about 15:35Z:
`bash rpd_flux3_launch.sh survey <new empty dir> login05 login12 login21 login30`.

- It made one ssh session to saul, which ran `cat /proc/loadavg; nproc; test -e <root>` on each node.
- The root was absent on all four nodes.
- The 15-minute loads were 22.68, 36.54, 23.31 and 29.51, so login05 was chosen.

## The connect: [`connect/`](connect/) (login05, 15:35:19Z to 15:36:05Z)

The launcher ran with a new empty session directory and wrote its output beside it, as
[`connect/launcher.out.txt`](connect/launcher.out.txt). ssh rc 0, script rc 0.

- `node login05 staged sha256 0a50f7db…`, the bound connect.
- **Step 2, the sacct fence:** `sacct rows (14 days): 75; cov2d/t2a/rpd rows: 16`, `FENCE: clear`.
- **Step 3, the fresh clone:** `HEAD 6896e7871421469ce72c6b93188d2d1a55c82ec6; porcelain lines 0`, and 14 pin shas,
  each equal to the addendum's. They include custody `634670b3`, `test_fd_rpd_reco.py` `e1b92ef0`,
  `fd_rpd_reco_fence_mutation.py` `138bc5b4` and `fd_rpd_reco_mutation.py` `f2612369`.
- **Step 4, the config:** `sha256 d797183b… (expected d797183b…)`.
- **Step 5, the overlap fence:** `FENCE protected paths 36`, `staged originals 57`, the one allowed exception (the MAT
  MParamFiles NuE constraint, as in flux2), and `FENCE OVERLAP: CLEAR (allowed 1, stops 0)`.
- **Step 6, the job:** job script sha256 `1b455cf2…`, `sbatch rc=0 jobid [61861637] 2026-11-23T15:36:05Z`.
- **scontrol** (ruling 3): JobName=rpd_flux3, Account=m3246, QOS=shared, TimeLimit=01:00:00,
  Partition=shared_milan_ss11, NumCPUs=9, MinMemoryNode=16G. These match the ruling.

## The job (`records/`)

The job waited about 36 minutes in the shared queue. It ran on nid004075 from 16:12:32Z to 16:21:18Z, and `job.rc` reads
`rc=0 cause=exit`.

- **sacct:** `61861637|rpd_flux3|COMPLETED|0:0|00:08:51|…|nid004075||10|16G|01:00:00`.
- **The charge (ruling 3):** 531 s at AllocCPUS 10 of 256 is 531 × 10 / (3600 × 256) = **0.0058 node-h**. sacct's
  AllocCPUS is the basis.
- **`job.out`:** shows the following, all on the node:
  - the copy at HEAD 6896e787, porcelain 0;
  - the 14 pins and config d797183b, rechecked;
  - `strace probe rc=0`, `wrapper rc=0`, `removed /dev/shm/limres-rpd-flux1 rc=0`.
- **`connect.log`** (the wrapper) records:
  - MAT setup with 6 scripts and 0 mismatches;
  - the real-MnvH1D check PASS;
  - custody prepare;
  - the missing-dependency check (below);
  - `flux-extract` PASS.
- **`exception-stat-outer.txt`:** the NuE constraint's stat at 16:13:58Z and at 16:21:17Z is identical, with atime_ns
  1794862761000000000 both times (the same value as in flux2's run).
- **`protected-read.json`:** PASS, with one stat-bracketed staging (16:16:38.56Z). Both staged copies are `e38ad7d2…`.

## Ruling 4: the digest, the custody binding and the identity

- **The digest.** `run/flux-extract.json` (schema `fd-rpd-reco-flux-extract/2`, status PASS, code_sha256 `7302cc1d…`)
  records `selection_sha256` = `75c2a1f4435494bf0e2c5bf4d27631781e65bd738c889c667183778e254792e8`. That is the P0
  form the addendum requires, the same value as flux2's.
- **The custody binding.** `run/flux-custody.json`, status PASS, records:
  - `custody_code_sha256` = `634670b33af6900eb9feb2c01748b0f107950e110382780db37b874ab77160d8`, the sacct-only custody
    this rerun exists for;
  - `code_sha256` `7302cc1d…`;
  - `extract_sha256` `90445ece…`, equal to the fetched `flux-extract.json`.

  P0's `extracted_flux` (`fd_rpd_reco.py:1994-2013`) compares that custody sha with the custody module beside it at
  6896e787, which is `634670b3`.
- **The custody fence ran sacct only.** `run/cov2d-fence.json` records two sacct reads and status PASS:
  - `sacct_named`: `-j 60909280,60911676` over 2026-11-05 to 2026-11-08, both COMPLETED;
  - `sacct_family`: from 2026-11-09T08:16:31, 71 rows, 14 of them cov2d/t2a.

  No file in `records/` contains the string `squeue`. That includes both strace logs.
- **The null field.** `common_units_convention_measured_at_P0` is null at `/premise` in two places:
  - `run/original-config.json` (sha256 d797183b, the bound config);
  - `run/extract-config.json` (sha256 `7edcdb9c…`, the extract's `config_sha256_at_extraction`).

## The factor products: 12/12 byte-identical to flux2's

The fetch printed all 12 sha256 (1A `c1e8a8d4…` through 1P `641e2555…`), each equal to the value `flux-extract.json`
records ("factor products recorded 12 differing 0").

Step 2b then compared each with run-61806073's committed `flux-extract.json`:
- **`FLUX2 IDENTITY: 12/12 byte-identical`**;
- a local recheck of the two committed extracts agrees, 12 of 12, with the same product keys.

The custody change does not enter the factor computation, so this is the expected result. The products stay on
pscratch under the run root.

The 54 staged originals, paths and sha256, are identical to flux2's
([`staged-originals.txt`](staged-originals.txt) against `../../flux2-20261122/run-61806073/staged-originals.txt`).

## `run/missing-dependency.STOP.json`: an expected STOP, by design

This is the custody negative control described in flux2's run README: the extract must refuse with guard
`MAT_DATA_STAGE` when the staged NuE constraint is withheld. That section's line numbers refer to custody `867822e3`.

- `run/missing-dependency-check.json` reads PASS, with expected guard MAT_DATA_STAGE and returncode 4.
- The STOP file (sha256 `8e28c83d…`) has guard MAT_DATA_STAGE and code_sha256 7302cc1d.
- Its JSON differs from flux2's only in run-specific fields:
  - the run root in `argv`;
  - the extract config's sha256 (`24929f14…` against `7edcdb9c…`), in `argv` and `config_sha256`;
  - `SLURM_JOB_ID` (61806073 against 61861637), twice.

The real `flux-extract` ran after the control and ended PASS.

## The fetches: [`fetch1/`](fetch1/), [`fetch2/`](fetch2/), [`fetch3/`](fetch3/) (login05, bound fetch `40645b69…`)

| fetch | time | result |
|---|---|---|
| `fetch1` | 15:46:42Z | sacct rc 0, `state [PENDING]`, NOT FINISHED, script rc 10, launcher rc 10, nothing written |
| `fetch2` | 16:07:04Z | sacct rc 0, `state [PENDING]`, NOT FINISHED, script rc 10, launcher rc 10, nothing written |
| `fetch3` | 16:37:29Z to 16:37:49Z | sacct `COMPLETED`, `job.rc` present, script rc 0, launcher rc 0 |

`fetch3` reported:
- the 12 products recorded, 0 differing;
- `FLUX2 IDENTITY: 12/12 byte-identical`;
- the protected read PASS;
- C3 PASS: the private record at `.rpd-private/606c383e…/prestage.json` has sha256 `5684f3c8…`, equal to its reference.
  It is owner-only and the only entry;
- the redaction check PASS: view NONE, with 0 fingerprint values in each file read;
- 30 files sent, 10,120,150 bytes;
- `TAR END tar rc=0 base64 rc=0`.

The tar's 32 entries are all plain relative paths. Untarred locally, every sent file and the two check outputs (32 in
all) matched their printed sha256 under `shasum -c`.

`fetch3/session.notar.out` and `fetch3/launcher.notar.out.txt` are the session and launcher outputs with the base64 tar
block replaced by one line, because `records/` holds those files. The full files had these sha256:
- `session.out`: `17261ad10fa4345017053883cc09a66513e8da0fc05b5542c4954738d402b1ad`;
- the launcher output: `d7161b5bc9b0182bf9f20cb35f8f8cdd97786037f97cf79cf046edbd8afc45a1`.

**`run/prestage.json` is held out of git, as in flux1 and flux2.** It was sent with sha256
`d6ceda0750b1545fdebde2fe51e23e8bfbadd9c8f6fcf1b78d68862d8e1a0ad9` and 252,115 bytes. Its `dump_listing` names dump
files bare, and the receipt-artifact hook reads such names as missing deliverables. Its `files` content is in
`staged-originals.txt`. The original stays in the run directory on pscratch until a later deletion step.

## Left on pscratch

`/pscratch/sd/j/josephrb/rpd-reco-flux3-20261123` holds the factor products, the staged copies, the clone and the
private record. P0, rebuilt and bound separately, reads the factor products from there.

[`SHA256SUMS`](SHA256SUMS) covers every file in this directory except itself.
