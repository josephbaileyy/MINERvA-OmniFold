# COVFIX PG rehearsal plan (for the director's binding)

<!-- absence-ok: "no", "none" and "not" here state what this lane's own scripts do, checked by git grep at the head named below, not a claim that a result does not exist -->

- Code head: `4735c7df97e0170de2938db0fe1f32a3adeec91f` on `tunegen/pg-20261123`, accepted by the director for the
  rehearsal (2026-11-26).
- Joseph's go: "yes lets rehearse covfix since it only helps" (2026-11-26, relayed by the director).
- The rehearsal uses a synthetic seal only.
- Nothing below runs without the director's GO for that step. Each connect script's sha goes to the director before
  it runs.
- Every sha below is computed by `git show <commit>:<file> | shasum -a 256`.

## (1) The steps, in order

Paths below are relative to `docs/orchestration/state/2d-closeout/covfix-20261122/pg/`.

### B1, the probe (read-only)

- **Node:** a Perlmutter login node, reached over ssh from the laptop. No Slurm job.
- **Command** (from `probe/`):
  `python3 -I -S -B pg-probe-launch.py 1a73541025c219d501a91b9b43ba3e2def1623f172e55427a7cb29f984602dff`
  - pg-probe-launch.py: `4f34dc4197838c2bf5e861a152f98da11619451c57409ba44ef15d085b8157c5`.
  - pg-probe.py: `1a73541025c219d501a91b9b43ba3e2def1623f172e55427a7cb29f984602dff`.
  - The launcher hashes the probe's bytes, sends exactly those bytes on ssh's stdin, and runs them as
    `env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -`.
- **What it writes:**
  - On the laptop: `probe/pg-probe.out`, reserved with `O_CREAT|O_EXCL|O_NOFOLLOW`.
  - On NERSC: nothing under `/pscratch` or CFS. **One exception for the binding to allow:** the strace self-test and
    the gpg self-test each make a private temp directory under the login node's own `/tmp` (`pgst*` and
    `pgprobe*`, mode 700).
    - Both are removed before the probe ends. The gpg homedir and its socket directory must be absent (checked
      with `lstat`) at the end, or the probe STOPs.
    - The gpg passphrases and payload are throwaway random values (`secrets.token_hex(32)`, `os.urandom`). No
      COVFIX secret is involved.
- **STOP conditions:**
  - Identity: the hostname is not `login<NN>`, or `/pscratch`, `/global/common` or CVMFS is absent. In that case
    nothing is read.
  - CVMFS: the repository is not on its own non-local mount, its `user.fqrn` is wrong, or its xattrs are unreadable.
  - Pins: any pinned GENIE file, link or listing is missing, extra or different from its pin.
  - genie_xsec: one of the three qualifiers is missing, or a pinned spline or README differs, or a non-`gxspl-*`
    `.xml` file is in `data/`.
  - Tools: a tool's hash does not match its RPM digest, or strace's self-test trace is incomplete.
  - gpg: the socket directory is misplaced; the round trip, tamper check or wrong-passphrase check fails; or the
    agent or its directories survive.
  - The launcher's own checks: a receipt that is not exactly one final `PG-PROBE-RESULT` line, a verdict that does
    not match the exit code, or an incomplete record. These exit 4, or 5 before ssh.
- **Its output feeds B2.** B1 gives `xsec.dbconfig.sha256`, which the director pins.

### B2, the private product install (writes NERSC scratch)

- **Before it can run:**
  - pg-install-g2111a.py holds `DBCONFIG_SHA256 = None` at the head. It must be filled with the director's pin from
    B1's receipt.
  - That changes its bytes, so the filled file is committed and its sha goes to the director before B2 runs.
  - Its sha at the head, unfilled, is `64bf420feb7d6e4ef635a7a7b341a3de65810b7ae943bbc43564ddc12475e4e8`.
- **Node:** a login node. No Slurm job.
- **Command** (from `install/`): `python3 -I -S -B pg-node-launch.py pg-install-g2111a.py <sha of the filled file>`
  - pg-node-launch.py: `f539c767a06659dfb9714d9dea5267ff6dac50c03d02cdee7a9c34de3f1be3f5`.
- **What it writes:**
  - On NERSC: only `/pscratch/sd/j/josephrb/covfix-pg/products/`, which must not exist yet.
    - `dl/`: the tarball, removed after its members are written.
    - `genie_xsec/`: the members.
    - `.upsfiles/dbconfig`: a byte copy of CVMFS's.
    - Everything is then made read-only.
  - The download is SciSoft's `genie_xsec-3.04.00-noarch-G2111a00000-k250-e1000.tar.bz2`: https only
    (`--proto =https`), sha256 `ae159887…7590`, hashed through its descriptor.
  - On the laptop: `install/pg-install-g2111a.py.out`.
- **STOP conditions:**
  - Identity fails, the root already exists, or its parent is not on `/pscratch`.
  - The pin is unfilled.
  - The tarball's sha differs; the download is then removed.
  - Pass 1 over the tarball: any member's name, type, link target or sha differs, or a member is missing or extra.
    Nothing is written in this pass.
  - dbconfig's sha differs from the pin.
  - The final re-check of the read-only tree finds any difference.
  - A STOP after step 1 leaves the root in place for the director to inspect. Nothing is retried.

### B3, the login-node replay of slot 1 (writes NERSC scratch)

- **Before it can run:**
  - **`3d-unfolding/genie/pg_pins.json` is filled first** (added 2026-11-26, after B3's first run STOPped with
    `pg_pins.json is not filled (R1)`; this plan had left the step out). pg_replay.sh and pg_generate.sh refuse while
    any pin is null or `system_tools` is empty. The director confirms each value from B1's receipt:
    - `strace_sha256`: `tools.strace.sha256`;
    - `dbconfig_sha256`: `xsec.dbconfig.sha256`, the same as B2's pin;
    - `system_tools`: `{tools.awk.path: tools.awk.sha256}`, the probe's gawk (RULINGS-A2.md, D1).
    `test_pg_pins_json_is_b1s_receipt` holds the file to B1's committed receipt. pg_pins.json is inside B3's
    archive, so the embed below is of the commit that holds the filled pins.
  - pg-replay-g2111a.py holds `COMMIT = None` and an empty archive at the head.
  - `python3 -I -B install/embed_archive.py 4735c7df97e0170de2938db0fe1f32a3adeec91f` fills in the commit, the
    archive's sha256, the blob pins and the archive itself. That commit must hold every file B3 runs, and it does: `git cat-file -e` finds all of embed_archive.py's `PATHS` at 4735c7df, and `git ls-tree -r` shows no link or submodule among them.
  - The filled file is committed. Its sha, and the archive's sha, go to the director before B3 runs.
  - embed_archive.py: `d5e2a13fe8c5cae5df5a7e0ef7011997c8bf5fc464aeff3f507d609bf63d41cc`.
  - pg-replay-g2111a.py at the head, unfilled: `e00c12e38650df7c7a172f5aeec53285f164341a5f6e32ecc58ca3f940c8996f`.
- **Node:** a login node, after B2. No Slurm job.
  - The driver runs under `nice -n 19` and `timeout 7200` (`WALL_CAP_S`).
  - It runs pg_generate.sh's checks before generation, then 100 events at the public seed 123456789. Each event is
    traced and trace-checked.
- **Command** (from `install/`): `python3 -I -S -B pg-node-launch.py pg-replay-g2111a.py <sha of the filled file>`
- **What it writes:**
  - On NERSC: only a fresh `/pscratch/sd/j/josephrb/covfix-pg/replay-<utc>/`, which must not exist yet. It holds:
    - `deploy/`: the archive, unpacked;
    - `tmp/`;
    - the replay's work, splines, graphs and records.
  - The public-seed event and status files are deleted unread, and `run/deleted.json` records them.
  - It reads, and does not write: `products/` from B2, CVMFS, and the flux at
    `/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix`.
  - On the laptop: `install/pg-replay-g2111a.py.out`.
- **STOP conditions:**
  - Identity fails, or the replay directory already exists.
  - The archive's sha differs. Nothing is then written.
  - The unpacked tree holds a link, an absolute name or a `..`, or any blob differs from its pin, or a file is
    missing or extra.
  - The driver's rc is not 0, or it hits the 7200 s cap.
  - Any of pg_generate.sh's pre-generation checks fails. These cover:
    - the pins and the CVMFS revision;
    - the reduce's completeness and the argv check;
    - each traced config and spline open against its pin;
    - the coverage run, and the leak scan of the public-seed GHEP (R1's control);
    - the drain and quiesce.
  - The launcher's payload check fails: nine named checks, four spline opens, four real shapes and the deleted-file
    record must all be present and true.
- **Its record feeds the generation's time bound** (section 3), through the driver's `[replay] start` and
  `[replay] done` timestamps. It also fills REHEARSAL-CHECKLIST.md's rows that B3 can answer, including
  `seed_objects`.
- **A risk to check first:** the flux directory `s5p-20260926/gen5d_fluxfix` is from September. If pscratch's
  purge has removed it, B3 STOPs at make-flux. This fails closed, but it would waste the step. None of B1–B3 checks
  for it beforehand, so a read-only `ls` before B3 needs its own GO.

### G, the synthetic-seal generation (only if the binding includes it)

- **Node:** one exclusive Perlmutter CPU node, in one Slurm job. This is the only Slurm job in the plan.
- **Command:** this lane does not run it.
  - cov2d's bound PG binary runs it, through the director's wrapper, as
    `cd W && TMPDIR=W/tmp pg_generate.sh --workdir W --seeds W/seeds.json < /dev/null`.
  - pg_generate.sh: `a6cdf3df09864f1e6acd4bd162e2414f113e7cb12d2289377dfe1d0d523d0051`. The binary verifies this
    sha.
  - run_gevgen_v3.sh: `5c3fd52059a8fb344af154d1af6b9fb8d0a23fc8baf66bfa0377e1447d22890b`.
- **What it writes:** everything is under W: `W/run/`, `W/out/`, `W/tmp/` and `W/PRODUCTS.json`.
  - I propose that the binding sets W to `/pscratch/sd/j/josephrb/covfix-pg/rehearsal-<utc>/`.
  - Nothing is written into the deploy, and nothing goes to CFS.
  - What leaves W is decided by the parent, from `W/out/PG-PUBLISH-SHA256SUMS` (allowlisted and leak-scanned).
- **STOP conditions:**
  - Exit 2: a refusal before any step. Causes:
    - bad arguments;
    - a cwd that is not W, or a `TMPDIR` that is not W/tmp at mode 700;
    - an existing `W/out`, `W/run` or `W/PRODUCTS.json`;
    - a deploy that is not `PG_DEPLOY_PIN`, or one with a modified tracked file;
    - a hook variable that is set.
  - Exit 1: a failed step. The steps are:
    - seeds.json's rule;
    - pins, revision, the reduce, spline-check and graphs;
    - the coverage runs;
    - any of the 14 gevgen tasks (each killed at 5115 s), the flux-check and hadd;
    - convert with its sampling test, and prep;
    - the gntpc traces, the revision compare and seedfree;
    - the drain: survivors 30 s after KILL, or a foreign process with its cwd in W;
    - the leak scan.
  - On any STOP, the publication set is withdrawn.

## (2) The synthetic seal, and no real secret

- **Where the seal comes from:** cov2d's side.
  - This lane never makes, sees or handles a seal, a passphrase or the seeds (the director's standing rule).
  - pg_generate.sh reads seeds only from `W/seeds.json`, which the bound binary writes from the seal.
  - README-pg.md says pg_generate.sh "needs no network, no passphrase and no GNUPGHOME: encryption is the parent's."
  - For the rehearsal, cov2d supplies a synthetic seal and its synthetic seeds. They must follow seeds.json's rule
    (`pg_lib.load_seeds`):
    - u0's first seed is in [1e9, 2e9);
    - seeds are consecutive within a tune;
    - u1's first seed is u0's plus 10,000;
    - every seed is below 2³¹ − 1.
- **No real COVFIX secret and no Keychain item:**
  - `git grep` at 4735c7df finds no `security`, `keychain`, `find-generic-password` or `add-generic-password` call
    in any of this lane's scripts. Those scripts are: pg_generate.sh, pg_lib.py, pg_verify.py, pg_replay.sh,
    run_gevgen_v3.sh, and every .py under `probe/` and `install/`.
  - The only passphrases anywhere are B1's gpg self-test values: random, made on the node, and never stored.
  - B2 and B3 use no seed but the public seed 123456789.
  - Whether the bound binary or the wrapper touches the Keychain when it makes a synthetic seal is cov2d's, and the
    binding's, to state. I can't check it: those files are outside my reads.

## (3) The generation's --time and node-h bound

- **Source:** F1b's budget receipt.
  - `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/run/cluster/gate3/budget3.json`.
  - That is under `receipts-f1`, not COV2D. It is the file pg_generate.sh's `TO=5115` cites.
  - F1b′'s actual job: `fd/receipts-f1/run/cluster/logs/fd_f1b3_60436278.out`.
- **Values in the receipt:**
  - 14 tasks of 160,000 events at once (7 per tune), in 1 wave.
  - Per-task timeout `5115` s.
  - Projected task wall `1704.7` s; projected job wall `2604.7` s.
  - F1b′'s time limit `00:55:00`; worst case `2.225` node-h.
  - Projected memory `308,216,608` KiB of `499,509,248` KiB, against a 75 % limit.
- **F1b′'s measured job** (60436278):
  - start 11:03:45Z, generation done 11:20:48Z, end 11:22:16Z: **1111 s** in all.
  - Its longest task's `/usr/bin/time` wall was **1022.8 s**.
- **What F1b′ does not measure for PG:**
  - pg_generate.sh adds steps that F1b′'s job did not run. For each of two tunes: the reduce, spline-check, graphs,
    a traced one-event coverage run, and a traced gntpc per task.
  - It also adds the leak scan, the drain (at most 30 s), products and publish.
  - PG's tunes (G21_11a_00_000, G18_02a_00_000) are not the tunes F1b′ measured (G18_10a_02_11b, AR23_20i_00_000).
    So the per-event time and the RSS of about 21.9 GB per process are carried over, not measured.
  - An out-of-memory kill or a timeout is a STOP: it fails closed.
- **Proposed bound:** `--time 02:00:00` on 1 node, so **at most 2.0 node-h**, with one attempt and no automatic
  retry.
  - The generation wave is capped at 5115 s (1.42 h) by the per-task timeout.
  - That leaves 2085 s (34.75 min) for every other step. F1b′'s whole job took 1111 s, including its generation.
- **Before the job is submitted, check the bound against B3's record:**
  - B3's `[replay] start`/`done` interval covers the pre-generation steps for one tune, plus 100 traced events, on
    a login node at nice 19.
  - If twice that interval, plus 1.25 × 1022.8 s, plus 600 s for conversion, prep and publish, exceeds 7200 s, the
    bound is raised. That needs the director's new GO, with the numbers.
  - I don't propose F1b′'s `00:55:00`. A single task that ran to its 5115 s timeout would already pass it.

## (4) What cov2d's side must have landed first

These are pg_generate.sh's contract with its parent (README-pg.md, "Contract" and "Environment it needs"). I can't
check cov2d's state, so each item is for the binding to confirm.

1. **The bound PG binary.** It runs pg_generate.sh as a subprocess, verifies its sha (`a6cdf3df…`) and gives it:
   - cwd W, and `TMPDIR=W/tmp` (existing, mode 0700, the user's own);
   - stdin `/dev/null`, with stdout and stderr captured;
   - the scrubbed environment README-pg.md lists, including `PG_DEPLOY_PIN` set first, and none of `LD_PRELOAD`,
     `LD_AUDIT`, `BASH_ENV`, `ENV`, `PYTHONPATH`, `PYTHONSTARTUP`, `PYTHONUSERBASE`, `GXMLPATHS` or `GALGCONF`;
   - one exclusive CPU node.
2. **The synthetic seal and its seeds.json writer,** following the rule in section 2. Plus how the binary keeps the
   seal's passphrase away from Slurm's records: no seed or secret in the sbatch line, `--comment`, the job name or
   the environment (RULINGS-A2.md, C3).
3. **A deploy on NERSC at the pinned commit,** clean (no modified tracked file), whose `run_gevgen_v3.sh` is
   `5c3fd520…`. `PG_DEPLOY_PIN` must be that deploy's full commit sha.
   - The deploy must hold this head's pg_generate.sh, pg_lib.py, pg_verify.py and run_gevgen_v3.sh, and
     `setup_salloc_env.sh`.
4. **The director's wrapper,** installed (the memory records the 2026-11-24 reinstall from #1340's merge; the binding
   should give the current sha).
5. **What leaves W:** the parent's export reads `W/out/PG-PUBLISH-SHA256SUMS` only. `W/out/PG-SHA256SUMS` and
   `W/run/` are seed-bearing and stay sealed.
6. **B2 must have passed** (`products/` in place and read-only). For G, B3 should pass first, both for the time
   check in section 3 and as the forecast of the binary's own pre-generation checks.

## Order and the GO points

1. **B1.** Then the director pins the dbconfig sha.
2. **The B2 fill.** It is committed, and its sha goes to the director. **Then B2.**
3. **The pg_pins.json fill,** from B1's receipt, on the director's confirm. It is committed.
4. **The B3 embed** of the commit that holds the filled pins. It is committed, and its sha and the archive's sha go to the director. Before it,
   optionally, a read-only `ls` of the flux directory, with its own GO. **Then B3.**
5. **The time check** against B3's record (section 3).
6. **The root-schemas.json fill:** `gst` and `gst_merged` from B3's replay.json `gst_schema` and
   `gst_merged_schema`, on the director's confirm. pg_generate.sh refuses while either is null. Then cov2d's items
   (section 4) are confirmed, and G's `PG_DEPLOY_PIN` is a commit that holds both fills.
7. **G,** under the binding.

After each step, the receipt and the REHEARSAL-CHECKLIST.md rows it answers are committed.
