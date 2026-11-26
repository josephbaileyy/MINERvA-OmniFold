# EVW2D launch set

These scripts run EVW2D (`2d-unfolding/evw2d/evw2d.py`, merged in #1347 at 4d9147f9) once on Perlmutter. They follow
EVW5D's merged set (`fd/evw5d-20261125/launch/`). Nothing here runs before the director's EVW2D BINDING 1 and GO.

## Files

| file | where it runs | what it does |
|---|---|---|
| `evw2d_launch.sh` | the Mac | Checks the sshproxy certificate by command before every step (`TZ=UTC ssh-keygen -L` on the public certificate). `ssh-keygen` must succeed and the window must have begun. It must last 45 minutes more for the connect, and 15 for the post and cleanup. The first hop presents exactly that certificate (`CertificateFile`, `IdentityFile`, `IdentitiesOnly`), and `ssh -G` must show that it offers only that key and certificate. No key is read. Each remote script goes through `saul` to a named login node. That node stages it in a private `mktemp` file in `/dev/shm` and runs it only if its sha256 is the approved one. This remote wrapper deletes the copy after the script exits. `fetch` copies `post.tar.gz`, and `cleanup.tar.gz` when it exists. It tells an absent archive apart from an ssh failure. |
| `evw2d_connect.sh` | a login node | Claims the lane root by `mkdir`, with no `-p`. Clones `deploy_M` at M and `deploy_C` at C, and checks both are clean and carry the pinned bytes. Checks that `config.json` names this layout. Pre-checks the environment, with a real `O_NOATIME` open on `$SCRATCH`. Runs `evw2d.py stage` on the login node. Reads the staged omnifile through `/proc/self/fd/N` with ROOT and RDataFrame. Then it makes one `sbatch --hold` and saves the job id. `scontrol -o show job` must succeed (up to three tries) and show exactly this job, with TimeLimit 00:30:00, NumNodes `^1(-1)?$` and no array token. Only then is the job released. Any failure cancels it, except a release whose reply is lost. Then `scontrol` is asked again, up to three times; an answer is exit status 0 with at least one record. The job is kept if the answer is exactly one record, this job's, and it is no longer held: no `JobHeld*` reason in any state, and a nonzero priority if PENDING, SPECIAL_EXIT or REQUEUE_HOLD. Otherwise it is cancelled. If `scontrol` never answers, the job is kept and the connect exits 4 ("see sacct"): it passed the allocation check and may already have started. |
| `2d-unfolding/evw2d/sbatch_evw2d.sh` | the job | Checks the batch shell: name, no array, and `SLURM_JOB_NUM_NODES=1`. Checks `scontrol` for TimeLimit 00:30:00 and NumNodes `^1(-1)?$`, both checkouts, and the evw2d.py and config.json digests. Sets E_R's thread environment, then runs a print-only first srun step, with the wrapper step's options, that records the host, the CPU affinity (`os.sched_getaffinity` in `python3 -I -S`, which prints the whole `affinity=` line; GNU `nproc` honours `OMP_NUM_THREADS`, and a startup hook could print to stdout), `SLURM_JOB_NUM_NODES`, `SLURM_STEP_NUM_NODES` and `SLURM_STEP_ID`. It stops with a recorded reason unless the step's node count is `1` and its affinity 64. Then it runs one 64-CPU step of `evw2d.py run`. |
| `evw2d_post.sh` | a login node | Writes nothing until squeue answers without the job and sacct gives exactly one terminal allocation row. It then:<ul><li>checks the product set and SHA256SUMS in place;</li><li>runs `evw2d.accepted()` with run.json bound to the config digest and its `slurm_job` equal to the job id;</li><li>records stat lines (atime, mtime, size) after its last read, for the purge exposure;</li><li>tars the receipts.</li></ul>PASS needs COMPLETED, 0:0 and one node, and every receipt (a failed redirect counts) and the archive written. Only then, last, it publishes `post.pass` by rename. |
| `evw2d_cleanup.sh` | a login node | Runs only after its own GO, and only with a `post.pass` that names this job, the config digest and the current products' SHA256SUMS. `<lane>/stage` must be a real directory and both staged names regular files, not links. Runs `evw2d.py cleanup --out` (the declaration's §7) and keeps `deletions.tsv`. |
| `fill_pins.sh` | the Mac | Writes `bound/` and `PINS.txt` from the tool commit C, with every pin computed by command. It refuses unless `config.json` at C differs from the reviewed one (5fdb4c3f) only in the four binding fields, set to this layout. |

## What the cleanup removes

Exactly two files, and only through `evw2d.py cleanup`:
- `<lane>/stage/runEventLoopOmniFold_MEFHC.root`;
- `<lane>/stage/runEventLoopMC_MEFHC.root`.

These are the names `staged()` builds from the bound `config.json`. Each is removed only if it is the file that run.json's
`staged` record verified (inode, size, mtime, mode) with the pinned digest. Each removal gets a row in
`<lane>/deletions.tsv`. There is no glob. The products, anything under `<lane>/out` and directories are never removed.
Apart from that, the four remote scripts remove nothing. The only other removal is the launcher's remote wrapper deleting its own `mktemp` copy of the script in `/dev/shm`, by the path `mktemp` returned, after the script exits.

## Order

1. The binding commits `config.json` with `declaration_sha256`, `lane_root` (`/pscratch/sd/j/josephrb/evw2d-<yyyymmdd>`),
   `driver_tree.root` (`<lane>/deploy_M`) and `inputs.staging.root` (`<lane>/stage`). That commit is C.
2. `bash fill_pins.sh <C>` writes `bound/`, which is committed. The director binds `PINS.txt`.
3. GO, then the steps from the Mac:
   1. `bash bound/evw2d_launch.sh connect <new dir> loginNN`;
   2. after sacct shows the job ended, `bash bound/evw2d_launch.sh post <new dir> loginNN` (if accounting lags, it
      stops having written nothing, and is run again);
   3. `bash bound/evw2d_launch.sh fetch <new dir>`;
   4. only on a passing post and a separate GO, `cleanup` and `fetch` again.

Everything is written under the lane root, on `$SCRATCH`. CFS is only read, by evw2d.py's O_NOATIME copies.

## Tests

`2d-unfolding/evw2d/test_evw2d_launch.py` (71 tests) covers the job script, the connect's allocation block (held
submission, scontrol status and retries, release), the launcher (certificate, approved bytes, fetch), the post, the
cleanup and `fill_pins.sh`. It stubs scontrol, srun, squeue, sacct, ssh, scp and ssh-keygen. The scontrol fixtures are
two records on main, read verbatim:
- a pending job with `NumNodes=1-1` (cov2d's connect log);
- a running job with `NumNodes=1` (xr-linux's `scontrol-job.txt`).

A 64-mutant check of the guards (`receipts/launch_mutation.py`) killed 64 of 64.

## Reads

Five codex-school reads (gpt-6.2-sol, effort high, read-only sandbox). The prompts, reports and receipts are in
`receipts/reads/`.

| read | verdict | fixed in |
|---|---|---|
| r1, the full set | NO-GO: four BLOCKING | r2 |
| r1b, the r2 fixes | NOT ALL HOLD | r3 |
| r1c, the r3 fixes | NOT ALL HOLD: the scripts' self-deletion broke the cleanup condition | r4: the scripts remove nothing |
| r1d, the r4 fixes | NOT ALL HOLD: two SHOULD-FIX items in the lost-release handling | r5 |
| r1e, the release block | ALL HOLD | |

Two findings are left as they are:
- `ssh -G` showing the same key under a symlinked alias stops the launcher. That is a false STOP, so it fails closed.
- `evw2d.py cleanup`, run directly, follows a linked staging root. The launch path never runs it that way:
  `evw2d_cleanup.sh` first checks that `<lane>/stage` is a real directory. evw2d.py stays byte-unchanged here, so this
  is a follow-up for evw2d.py.

## The HPSS copy and the deposit fetch (for EVW2D BINDING 2)

These steps follow the run accepted under BINDING 1 (job 62022231; the products' SHA256SUMS digest e60867ef;
receipts in `../receipts/run-20261126/`). They follow EVW5D's merged hpss and fetch-products steps. BINDING 1's bound
launcher stays as it is: these steps have their own launcher. Every step is bound to the SHA256SUMS digest, the
evw2d.done digest, the job and the config digest.

| file | where it runs | what it does |
|---|---|---|
| `evw2d_hpss.sh` | a login node | Before it writes anything:<ul><li>the lane and `out/` are real directories, and the six names are regular files, not links;</li><li>`post.pass` is exactly this job, config and products digest;</li><li>SHA256SUMS and evw2d.done have their bound digests;</li><li>deploy_C's evw2d.py is the approved bytes.</li></ul>A private snapshot gives every pin and the six-file list, and the checker passes on scratch. The checker executes the very bytes it hashed, then requires `evw2d.accepted()` and the digest, config and job bindings. /dev/shm must have room for the retrieval, and the HPSS directory must list cleanly with none of the archive's four names. Scratch is re-hashed before htar. Then:<ul><li>`htar -Hcrc -Hverify=1` writes a part name, followed by `hashcreate` and `hashverify`;</li><li>a full retrieval into a private `mktemp` directory in /dev/shm, with the pins, the counts and the checker on the retrieved copy;</li><li>scratch is re-hashed again, and the six names checked again as regular files;</li><li>`htar -tf` of the part archive must list every pinned name.</li></ul>Only when every check holds is the index renamed (`hsi mv`), then the archive, so the final `.tar` never appears without its index. Both final names must then list, or both are renamed back to the part name. Otherwise the part names stay, or the log says which names are where. The retrieved copy is removed by the pinned names only, then its directories by `rmdir`. Nothing on scratch is removed. Receipts go to `<lane>/hpss` and `hpss.tar.gz`. |
| `evw2d_deposit.sh` | the Mac | BINDING 1's certificate and credential checks, verbatim, before every step. The directory argument is resolved once to a physical path (CDPATH unset), and every write uses it. It has three modes:<ul><li>`hpss`: runs the approved `evw2d_hpss.sh` through the /dev/shm stager, with a 60-minute certificate margin;</li><li>`fetch`: copies `hpss.tar.gz`, then verifies its receipt. Its first line must name the approved `evw2d_hpss.sh`, the bound digests and the job, exactly. The log must show 6 of 6, the part archive's readback, the rename and `hpss rc=0`; its snapshot SHA256SUMS has the bound digest; and its pinned list is byte for byte the six rows that snapshot implies. Exit 5 if it is not verified;</li><li>`fetch-products`: copies the six files by scp into `<new dir>/out` and runs the checker on the Mac, which executes the approved evw2d.py's bytes.</li></ul>The fetch-products destination must be a new empty directory under `$HOME`, outside `/private/tmp`, `/tmp` and `/private/var`. |
| `fill_deposit_pins.sh` | the Mac | Writes `bound-deposit/` and its `PINS.txt`. HEAD is resolved once to a commit, and every input is read from that commit (`git show`), each a regular blob in its tree, never a symlink. The working copies of evw2d.py and the templates must hash equal to the commit's blobs. The lane, evw2d.py and config.json come from BINDING 1's `bound/PINS.txt`. The SHA256SUMS digest, the evw2d.done digest and the job come from the committed run receipts, cross-checked against their `accepted.json`, marker and post log. |

Tests: `2d-unfolding/evw2d/test_evw2d_deposit.py`. It stubs hsi, htar, hpssquota, ssh, scp, ssh-keygen, GNU stat and
df, uses a temporary HPSS directory, and runs the real `evw2d.accepted()` on a small accepted product set. The
fetch-products tests make and remove a directory under the real `$HOME`, because the step refuses temporary roots.

Some checks are layered, so a mutant of one alone survives, and those mutants are left out of the mutation check:
- in the retrieval, the pinned sums, the counts, `rmdir` and the checker each catch a corrupt or extra file;
- the snapshot comparison and the scratch re-hash both catch a changed marker;
- on the Mac, the SHA256SUMS digest is implied by the marker digest together with `accepted()`;
- the listing check repeats `accepted()`'s `present` check.

The codex-school reads are in `receipts/deposit/reads/`.
