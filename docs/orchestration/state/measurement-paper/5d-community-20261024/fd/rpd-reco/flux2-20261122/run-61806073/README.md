# rpd_flux2, job 61806073: the run's records (2026-11-22)

**By** limitation-resolver, under [`FD-RPD-RECO-BINDING-2-ADDENDUM-1.md`](../../../../FD-RPD-RECO-BINDING-2-ADDENDUM-1.md)
(merged 4404cef8), at M_F2 = `62ce018fdf32b5f6b7354ec2e617222ee470f955`. This is the config-only rerun of flux connect 1
described in [`../README.md`](../README.md).

**Result: COMPLETED, rc 0, in 4 min 11 s.** Each ruling-4 check holds (below). The products stay on pscratch.

- **CITABLE FOR:** the rerun's flux selection digest, its factor products' sha256, and its custody records.
- **NOT CITABLE FOR:** any RPD-RECO result, or P0 READY, which is bound separately.

## Preconditions (ruling 2)

- **The bound files:** the worktree was detached at M_F2, and all eight bound files re-hashed to the addendum's
  values.
- **cov2d's fresh ack:** given at 2026-11-22T23:28:48Z, 16 minutes before the connect. cov2d had no job queued,
  running or planned, the protected set and reads were unchanged, and it had no objection.
- **The cert check:** the launcher read the cert as valid to 2026-11-23T22:00:33Z.
- **The run root:** absent before the connect, per the survey below and the connect's own guard.
- **Fence mode:** not run. The connect's sacct fence and `fence_overlap.py` both read CLEAR (below).

## The survey: [`survey/`](survey/)

The bound launcher, `rpd_flux2_launch.sh` (`c744061e…`), ran in its own `survey` mode at about 23:25Z:
`bash rpd_flux2_launch.sh survey <new empty dir> login06 login21 login23 login27 login31`.

- The cert check passed first.
- Then one ssh session to saul ran, for each node, exactly:
  `echo "== $n"; ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $n 'cat /proc/loadavg; nproc;
  test -e /pscratch/sd/j/josephrb/rpd-reco-flux2-20261122 && echo ROOT-EXISTS || echo root-absent'`.
- Nothing was written, and no file was opened except `/proc/loadavg`.
- The root was absent on all five nodes. The 15-minute loads were 13.71, 29.67, 34.26, 40.57 and 5.49, and login31
  was chosen.

## A disclosed local refusal: [`connect-refused/`](connect-refused/)

The first connect attempt, at 2026-11-22T23:29:03Z, redirected the launcher's output into the session directory
itself (`… connect <dir> login31 > <dir>/launcher.out.txt`). The shell created that file first, so the launcher's first
guard (`rpd_flux2_launch.sh:13`) refused:
"STOP: …/connect is not a new empty directory", rc 9.

That guard comes before the cert check and before any ssh. So there was no ssh, no staging, no fence and no job, and
nothing was written on the cluster. `connect-refused/launcher.out.txt` is its whole record.

It was reported to the director. The director ruled that ruling 5 covers guards after the cluster is contacted, so
this was an operator error, and gave GO for one unchanged retry.

## The connect: [`connect/`](connect/) (login31, 23:29:45Z to 23:30:36Z)

The launcher ran with a new empty session directory, writing its output beside the directory. ssh rc 0, script rc 0.

- `node login31 staged sha256 7a362f34…`, which is the bound connect.
- **Step 2, the sacct fence:** `sacct rows (14 days): 102; cov2d/t2a/rpd rows: 15`, `FENCE: clear`.
- **Step 3, the fresh clone:** `HEAD 763ab4ddcea2d2d3dce56138f8aa7ae7fab4bbe6; porcelain lines 0`, and 11 pin shas,
  each equal to binding 2's.
- **Step 4, the config:** `sha256 7ebc2aa9… (expected 7ebc2aa9…)`.
- **Step 5, the overlap fence:** `FENCE protected paths 36`, `staged originals 57`, the one allowed exception, and
  `FENCE OVERLAP: CLEAR (allowed 1, stops 0)`.
- **Step 6, the job:** job script sha256 `5792108b…`, `sbatch rc=0 jobid [61806073] 2026-11-22T23:30:36Z`.
- **scontrol** (ruling 3): JobName=rpd_flux2, Account=m3246, QOS=shared, TimeLimit=01:00:00,
  Partition=shared_milan_ss11, NumCPUs=9, MinMemoryNode=16G.

## The job (`records/`)

The job ran on nid004078 from 23:37:03Z to 23:41:13Z, and `job.rc` reads `rc=0 cause=exit`.

- **sacct:** `61806073|rpd_flux2|COMPLETED|0:0|00:04:11|…|nid004078||10|16G|01:00:00`.
- **The charge (ruling 3):** 251 s at AllocCPUS 10 of 256 is 251 × 10 / (3600 × 256) = **0.0027 node-h**. The job's
  environment shows `SLURM_CPUS_PER_TASK` 9 and `SLURM_JOB_CPUS_PER_NODE` 10. sacct's AllocCPUS is the basis.
- **`job.out`:** the copy at HEAD 763ab4dd, porcelain 0, the 11 pins and config 7ebc2aa9 rechecked on the node;
  `strace probe rc=0`; `wrapper rc=0`; `removed /dev/shm/limres-rpd-flux1 rc=0`.
- **`connect.log`** (#848's wrapper): MAT setup with 6 scripts and 0 mismatches; the real-MnvH1D check PASS; custody
  prepare; the missing-dependency check (below); `flux-extract` PASS.
- **`exception-stat-outer.txt`:** the NuE constraint's stat at 23:38:28Z and at 23:41:13Z is identical, atime_ns
  1794862761000000000 both times. `protected-read.json` is PASS: one stat-bracketed staging (23:39:27.98Z), both staged
  copies `e38ad7d2…`, and none of the 54 staged originals overlapping a protected path.

## Ruling 4: the digest and the null field

- **The digest.** `run/flux-extract.json` (schema `fd-rpd-reco-flux-extract/2`, status PASS, code_sha256 `7302cc1d…`)
  records `selection_sha256` = `75c2a1f4435494bf0e2c5bf4d27631781e65bd738c889c667183778e254792e8`.
  - That is the rerun's P0 form, and it differs from flux1's `1c716c12…` (flux1's own `selection_sha256`).
  - **Field names:** the addendum's "flux_selection_digest" is the function `fd_rpd_reco.flux_selection_digest`
    (`nd-unfolding/fd_rpd_reco.py:1155`, at 763ab4dd). It hashes the config's flux_root, flux_selection, inventory,
    flux_source, mat_dependencies and premise. The extract stores its value under the key `selection_sha256`.
- **The null field.** `common_units_convention_measured_at_P0` is null at `/premise` in `run/original-config.json`
  (sha256 7ebc2aa9, the bound config) and in `run/extract-config.json` (sha256 `24929f14…`, the extract's
  `config_sha256_at_extraction`).
- **Custody.** `run/flux-custody.json`, the trace-check's record, is status PASS.

## The factor products

The fetch printed all 12 sha256 (1A `c1e8a8d4…` through 1P `641e2555…`), each equal to the value
`flux-extract.json` records ("factor products recorded 12 differing 0"). They stay on pscratch under the run root.

**They are byte-identical to flux1's, 12 of 12.** That is what a config-only rerun should give, since the premise
booleans and the retention don't enter the factor computation. In the bound code:
- the premise booleans are read only by `p0()`'s P_F guard (`fd_rpd_reco.py:2160-2161`) and hashed by
  `flux_selection_digest` (`:1165`);
- retention is copied into the selection record (`:1150`), compared as a string by P0's `extracted_flux` (`:2036`),
  and hashed by the digest.

The 54 staged originals, paths and sha256, are also identical to flux1's ([`staged-originals.txt`](staged-originals.txt)
against `../../flux1-20261111/run-61206960/staged-originals.txt`).

## `run/missing-dependency.STOP.json`: an expected STOP, by design

The file is a STOP record inside a PASS run, so here is what it is.

1. **What writes it.** Custody's `missing_dependency_check` (`nd-unfolding/fd_rpd_reco_custody.py:1649-1742`, sha256
   867822e3, at 763ab4dd), which the wrapper calls before the real extract
   (`fd_rpd_reco_flux_connect.sh:39-41`). It is a negative control. The function:
   - runs only before the real extract, and refuses if `flux-extract.json` is already present;
   - withholds the run's own staged MPARAMFILES copy (renaming it to `*.negative-check-held`);
   - runs `flux-extract` under strace, then puts the file back;
   - **requires** that the extract refused with rc 4 and wrote `flux-extract.STOP.json` with guard `MAT_DATA_STAGE`,
     and classifies that trace;
   - then renames the refusal to `missing-dependency.STOP.json` (`:1727`) and writes
     `missing-dependency-check.json` with status PASS (`:1728-1741`).

   If the extract had not refused, or had refused at another guard, the `require` calls would have stopped the job
   there, before the real extract.
2. **Its content.** schema `fd-rpd-reco-stop/1`, status STOP, step flux-extract, guard `MAT_DATA_STAGE`, message
   "MAT_DATA_STAGE: staged MAT dependency missing or changed", and code_sha256 7302cc1d. The run's file has sha256
   `9cbf4fbe…`, and the fetch's printed sha matches the committed copy.
3. **Against flux1.** flux1's run-61206960 holds the same file (sha256 `80c3cf88…`). Their sorted JSON differs only
   in run-specific fields:
   - the run root in `argv`;
   - the extract config's sha256 (`7b014d5c…` against `24929f14…`), in `argv` and `config_sha256`;
   - `SLURM_JOB_ID` (61206960 against 61806073), twice.

   Both runs' `missing-dependency-check.json` say PASS, with expected guard MAT_DATA_STAGE, returncode 4, the
   withheld path being the run's own staged NuE constraint, and the trace check PASS.
4. **Why the job ended PASS.** The STOP is the control's required outcome, not a guard on the run. The real
   `flux-extract` ran after it and ended PASS (`connect.log`). Custody's trace-check then ended PASS too:
   `run/flux-custody.json` is what `check_trace` writes (`fd_rpd_reco_custody.py:1605-1645`).

## Disclosed: binding 2's custody code calls squeue inside the job

`run/cov2d-fence.json`, custody prepare's own COV2D fence, shows `queue_stdout`
`61806073|rpd_flux2|RUNNING|2:04|1:00:00` with status PASS. In binding 2's custody code, that fence runs
`squeue -u josephrb -h -o %i|%j|%T|%M|%l` (`fd_rpd_reco_custody.py:408`) and then sacct (`:435`). It is a read-only
query on the compute node.

flux1 ran the same bound code, and its run README:80 records it. The addendum binds this code unchanged, so this rerun
did not alter it. The sacct-only rule applied to the flux2 package (connect, fetch and launcher, which contain no
squeue). This bound module was outside the package reads.

## The fetches: [`fetch1/`](fetch1/), [`fetch2/`](fetch2/) (login31, bound fetch `d8f780c9…`)

| fetch | time | result |
|---|---|---|
| `fetch1` | 23:39:11Z | `state [RUNNING]`, NOT FINISHED, script rc 10, launcher rc 10, nothing written |
| `fetch2` | 23:45:29Z to 23:45:55Z | script rc 0, launcher rc 0 |

The fetch judges the end from `job.rc` or a terminal sacct state. fetch1's launcher rc 10 is the fetch's own status,
carried by the launcher fix in [`../README.md`](../README.md).

`fetch2` reported:
- the 12 products recorded, 0 differing;
- the protected read PASS;
- C3 PASS: the private record at `.rpd-private/937360ea…/prestage.json`, sha256 `98b44e90…`, equal to its reference,
  owner-only, and the only entry;
- the redaction check: view NONE, with 0 fingerprint values in each file read;
- 30 files sent, 10,129,733 bytes;
- `TAR END tar rc=0 base64 rc=0`.

Untarred locally, every sent file and the two check outputs matched their printed sha256.

`fetch2/session.notar.out` and `fetch2/launcher.notar.out.txt` are the session and launcher outputs with the base64 tar
block replaced by one line, because `records/` holds those files. The full files had these sha256:
- `session.out`: `c06726f57c9966e2633a1770caaa607da71325970bfca9c66d6bb24bffed461a`;
- the launcher output: `e244781bf6e469b25b7c85196ce3169ae6f84e8e0709067f6f977abd907b4854`.

**`run/prestage.json` is held out of git, as in flux1.** It was sent with sha256
`8bcaa2297007af55dc0eee8e3c604748229a3978455081124350bac739a1c104` and 249,330 bytes. Its `dump_listing` names files
in the dump directory bare, and the receipt-artifact hook reads such names as missing deliverables. Its `files` content
is in `staged-originals.txt`, with 54 originals:
- 24 dumps from `/pscratch/sd/j/josephrb/fd-rpd-20261103/dumps`;
- 14 from `minerva_large_files/MATFluxAndReweightFiles`;
- the NuE constraint;
- 10 MAT and setup files under `/pscratch/sd/j/josephrb/MINERvA-OmniFold`;
- 5 files from the job's `/dev/shm` repository copy.

The original stays in the run directory on pscratch until a later deletion step.

## Left on pscratch

`/pscratch/sd/j/josephrb/rpd-reco-flux2-20261122` holds the factor products, the staged copies, the clone and the
private record. P0 READY, bound separately, reads the factor products from there.
