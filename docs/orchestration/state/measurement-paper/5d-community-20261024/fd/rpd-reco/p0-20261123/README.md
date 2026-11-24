# RPD-RECO P0 (rpd_p0): the READY package, rebuilt on flux3's records (2026-11-23)

**By** limitation-resolver, for the director's P0 binding. Nothing here has run. The connect runs only on the
director's GO for its exact sha256, with cov2d's fresh ack.

P0 is **login-only at 0 node-h, with no job and no job-name family**. The authorities:
- FD-RPD-RECO-DECLARATION section 5: "Everything runs on a login node, with threads 1, nice 19 and O_NOATIME, from a
  fresh clone at the bound sha … No job, and nothing is written to CFS";
- BINDING-1 ruling 3.

**Why it was rebuilt.** The first P0 draft read flux2's records. Bound `fd_rpd_reco.py` (`7302cc1d`), in
`extracted_flux` (`:1994-2013`), requires the custody receipt's `custody_code_sha256` to equal the custody module
beside it. flux2's receipt binds `867822e3`, while the clone at 6896e787 carries the sacct-only `634670b3`.
- The director ruled (A): rerun the flux stage at 6896e787 (flux3).
- flux3 ran as job 61861637, and its records merged in #1264 (`1fdfe494`):
  - `custody_code_sha256` `634670b3`;
  - the selection digest `75c2a1f4`;
  - FLUX2 IDENTITY 12/12.
- This package reads flux3's records and products. The director accepted the P0 read findings 1–9 as fixes, and each
  is listed below.

## What P0 does, in order (one login node)

**The connect** (`rpd_p0_connect.sh`):
1. It refuses off a login node, or if the root `/pscratch/sd/j/josephrb/rpd-reco-p0-20261123` exists.
2. **The sacct fence:** flux3's tightened block, byte for byte. Any unended cov2d*, t2a* or rpd* job refuses, as do
   an empty or padded JobName or a blank State (finding 8). This tightens flux2's block.
   - **The `ibuchi_` family** (Joseph's ibu-chi-squared-issue session, announced 2026-11-23) is deliberately not
     added. The director agreed to leave it out:
     - its writes, `/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/` and its own `/dev/shm`, are disjoint from P0's;
     - it declares no reads of flux3's root or the dumps;
     - P0's input checks compare sha256 or bytes and inode, which another job's plain read of a shared MAT file
       cannot change.

     Keeping the block byte-identical to flux3's keeps its tested equivalence.
3. **A fresh clone** at `S = 6896e7871421469ce72c6b93188d2d1a55c82ec6`, with HEAD and porcelain checked and the 14
   pins. They are flux3's pins: custody `634670b3…`, `tests/test_fd_rpd_reco.py` `e1b92ef0…`,
   `tests/fd_rpd_reco_fence_mutation.py` `138bc5b4…` and `tests/fd_rpd_reco_mutation.py` `f2612369…` (finding 7).
   The generator checks each one equal at S through `git show`.
4. **The config,** written from the script and checked against its sha256.
5. **The in-place inputs:** `tools/p0_checks.py inputs` reads flux3's extract, custody record and 12 factor
   products under `/pscratch/sd/j/josephrb/rpd-reco-flux3-20261123/run/` with O_NOATIME. It compares their sha256
   with the committed run-61861637 records, held in `tools/p0_expected.json`. A missing file, a missing O_NOATIME
   flag or any difference STOPs before anything is staged.
6. **The retention record:** `tools/p0_checks.py stat` stats (never opens) the three selected gen2thin files and the
   24 dumps, and records bytes, atime, mtime and inode in `stat-p0.txt`. It prints the earliest purge exposure
   (oldest atime + 56 d), and STOPs if a file is missing or its bytes or inode differ from S1's.
7. **The overlap fence** (`tools/fence_overlap.py`, write roots the P0 root and `/dev/shm/limres-rpd-flux1`).
8. The clone is copied to `/dev/shm/limres-rpd-flux1/repo`, the path the config binds, with HEAD, porcelain and pins
   rechecked and the config copied beside it.
9. **The startup handoff** (finding 3):
   - the runner is started as `setsid nohup nice -n 19 "$PY" -I -B -c '<reset SIGINT; exec bash runner>'`, which
     execs `bash <root>/rpd_p0_runner.sh` in the same process. Resetting SIGINT matters because a background job
     started with job control off inherits SIGINT as ignored, and bash cannot trap an inherited ignored signal;
   - the connect waits up to 30 s for `runner.pid` and checks that it names the started process and that it is
     alive;
   - it then gives up ownership (`started=1`), and only after that writes `handoff.ok`. If `handoff.ok` is not
     written (a failure, or a signal in between), the runner finds no handoff and cleans up itself, so there is no
     moment when both or neither own the tree.

   Until `started=1` the connect owns `/dev/shm/limres-rpd-flux1`. On any STOP, or on TERM, INT or HUP, it stops a
   started runner (TERM, then KILL after 5 s). It signals both the group and the process, so a child is reached even
   before `setsid` has made the group, and it uses `$!` in the instant before `spid` is set. It then reaps the runner
   and removes the tree, checked. Before the handoff the runner has started no supervisor or worker.

**The runner** (`rpd_p0_runner.sh`, written by the connect):
- It writes `runner.pid` (pid, host, `/proc` start time, UTC time) and checks that it runs at nice 19.
- It starts no step without `handoff.ok`. If the file is not there within 60 s, it removes the tree itself and stops
  (rc 8).
- It computes **one monotonic deadline**, 7200 s after the handoff, for the whole chain (finding 2). The deadline is
  checked before each step and again after the last. The probe answers 10 (passed) or 11 (not passed); any other
  answer, for example a Python failure, is its own STOP (`clock-check`, rc 4), never read as either.
- Then it runs `pins --dry-run` and `p0 --dry-run` into `<root>/dry`, and then `pins` and `p0` into `<root>/run`.
  Any failure STOPs before the next step.
- Each step runs under **`tools/p0_supervise.py`**:
  - The worker runs in its own session and process group, and the supervisor stays outside it.
  - **The fork gate:** the supervisor forks the worker itself. The child calls `setsid`, and on Linux sets
    `PR_SET_PDEATHSIG` SIGKILL (checking `prctl`'s return and that its parent is still the supervisor). It then waits
    for one byte on a pipe before it execs. The supervisor sends that byte only after the child leads its own group
    and `sup-<step>.json.pgid` holds the group id, and only if the deadline has not passed by then. The child checks
    the deadline again after the byte arrives, immediately before it execs. So:
    - no worker process exists before its group can be found;
    - a release that arrives after the deadline never starts the work, even after a pause between the supervisor's
      check and its write. Such a step is reaped after the deadline, a wall-cap STOP;
    - a narrower window remains, between the child's own final check and `execvp`. Work started in it is ended by
      the supervisor's KILL at the deadline, and the step is reaped as `past_deadline`, a wall-cap STOP;
    - if the supervisor dies first, the child exits without running anything.
  - Each pass of its loop reads the clock, sends any due signal, and polls the worker. It then reads the clock again,
    loops at once if an event came due during the poll, and otherwise sleeps only until the next event (at most
    0.2 s). The group gets TERM 30 s before the deadline and KILL at the deadline, once each; the deadline KILL also
    consumes a pending forwarded escalation. A worker reaped at or after the deadline never counts as clean.
  - After reaping the worker, it kills anything left in the group and waits (up to 10 s) until the group is gone.
  - Signal delivery and group existence are kept apart:
    - `killpg` answers sent, absent (ESRCH) or denied (EPERM);
    - `deadline_signalled` counts only a sent signal;
    - EPERM means a live member that cannot be signalled, except on macOS, where it is the answer for a zombie-only
      group.
  - It records `sup-<step>.json`, last:

    | field | meaning |
    |---|---|
    | `rc` | the worker's rc |
    | `signal` | the signal that ended the worker, if any |
    | `deadline_signalled` | whether a deadline TERM or KILL was actually delivered to the group |
    | `past_deadline` | whether the worker was reaped at or after the deadline |
    | `forwarded` | a signal forwarded from the runner |
    | `leftover_group_killed` | whether anything was left in the group |
    | `group_gone` | whether the group was empty before the record was written |
    | `peak_rss_bytes` | the peak RSS, from `ru_maxrss` |

- The runner STOPs in these cases:

  | case | rc |
  |---|---|
  | a delivered deadline signal, a worker that outlived the deadline, or a chain that ends after it | 7 |
  | a kill from outside the supervisor | 4 |
  | a nonzero rc | 4 |
  | a leftover process, or a group still alive after the supervisor's KILL | 4 |
  | an unreadable peak RSS, or one over 8e9 B | 4 |
  | no supervisor record, with the deadline passed (the supervisor refused to start, exit 2) | 7 |
  | no supervisor record otherwise (the supervisor was killed) | 4, after the step's group is killed from its `.pgid` file and awaited |

  This replaces GNU `timeout`, whose 124 and 137 could not tell a deadline from an outside kill.
- A TERM or INT to the runner is forwarded to the supervisor **as TERM**, and the supervisor forwards it to the step's
  group and reaps it; the runner still exits 130 for INT.
  - TERM is used for both because bash starts the supervisor with SIGINT ignored, so an INT sent before the
    supervisor's handler exists would be lost. A TERM at that moment ends the supervisor before it has forked a
    worker.
  - In the instant before the supervisor's pid is recorded, the runner uses `$!`.
- On every exit it can catch, the runner does three things in order:
  - it kills a live step group and waits for it. The group counts as gone only when `kill -0` answers "No such
    process". EPERM, or any other error, counts as alive. The one exception is the permission-denied message on
    macOS, the supervisor's rule. If the group
    survives, `/dev/shm/limres-rpd-flux1` is **kept**, since a live member may still use it, and a clean run ends
    rc 6;
  - otherwise it removes `/dev/shm/limres-rpd-flux1` and **checks that it is gone**. A run that would end rc 0 ends
    rc 6 if it is not;
  - it publishes `p0.rc` (`rc=N cause=C end=T`), last. The time is read and format-checked first, and the write and
    rename are checked. A failed publication is reported, and a clean run then exits rc 6.
- An uncatchable kill writes no `p0.rc`. The fetch then reports the runner gone and the cleanup unverified. Recovery
  after such a death is a manual step on that node.

**`-B` on every Python call** (finding 5): the connect's checks, fence and launch wrapper, and the runner's
supervisor, deadline checks, record reads and the worker. The generator asserts this. P0 alone takes it; flux3's
package did not. The connect's two input checks also run at nice 19, like the runner.

**The write boundary:** P0 writes under its root and `/dev/shm/limres-rpd-flux1`.
- `TMPDIR` is the root from the moment it exists (step 3), so bash's heredoc spools stay inside it.
- The fetch has no heredoc or here-string. It parses `/proc/<pid>/stat` into an array with globbing off, and compares
  the command line through a `/dev/fd` process substitution, so it writes nothing beyond its own launcher copy.
- Two exceptions are accepted, inherited from the approved flux launcher pattern: the launcher's own
  `/dev/shm/rpd-p0-<mode>.<pid>.sh` copy, which the scripts delete, and the inner ssh hop's known_hosts behavior.

**The fetch** (`rpd_p0_fetch.sh`, finding 6):
- **A well-formed `p0.rc` is authoritative,** from any login node, with or without `runner.pid`: DONE (exit 0) or
  STOP (12). Well-formed means:
  - no NUL byte, checked on the file's bytes before the shell reads it (shell command substitution would drop one);
  - exactly one line, `rc=N cause=C end=T`;
  - C made of `[A-Za-z0-9_.-]`;
  - T a real UTC time, checked by a GNU `date -d` round trip.

  Anything else exits 9 and sends nothing.
- With no `p0.rc`, on the runner's node:
  - RUNNING (exit 10) requires two things: `/proc/<pid>/stat` shows the start time recorded in `runner.pid`, and
    `/proc/<pid>/cmdline` equals `bash\0<root>/rpd_p0_runner.sh\0` byte for byte (`cmp`).
  - It also requires `p0.rc` to be still absent after that probe.
  - A reused pid, another command, a longer path, or an extra (even empty) argument does not count.
  - Otherwise `p0.rc` is read again, since the runner may have finished in between. If it is still absent, the runner
    is gone (exit 11).
- Elsewhere, or with neither `p0.rc` nor `runner.pid`, it exits 9.
- When DONE, STOP or gone, it sends a base64 tar of these, with sha256:
  - `runner.pid`, `runner.out`, `runner-steps.txt`, `p0.rc`, `handoff.ok`;
  - `stat-p0.txt`, `flux3-inputs.txt`, `fence-overlap.txt`;
  - the runner and the config;
  - `sup-*.json`, and every `*.json` in `dry/` and `run/`.
- The staged copies stay on pscratch.

**The launcher** (`rpd_p0_launch.sh`) is flux3's, renamed and re-pinned, with flux3's ack guard (finding 4):
- `connect` takes cov2d's ack file. Its first line must be `ACK-UTC <time>`, a real UTC time at most 6 h old and at
  most 5 min ahead, and non-empty ack text must follow.
- The file is copied byte for byte into the session as `ack.txt`, and that copy is what is validated.
- The ack stays in the local session record. The director ruled that no ack-only ssh step is needed.
- Fence mode stays refused.

## What P0 reads, and its memory (finding 1)

The first README said P0 reads only the extract JSON. That was wrong:
- `pinned_flux_factors` (`fd_rpd_reco.py:2060-2097`, called at `:2189`) stages O_NOATIME copies of the 12 factor
  products and loads each playlist's four factor arrays together;
- p0 also reads `pass_reco` from each dump, and `runtime_estimate` reads `w_reco` and `bkg_w`.

[`rss-estimate/`](rss-estimate/) measures that pattern at full scale:
- the fixture: 12 playlists, each the size of the largest playlist (5,916,895 MC rows), with a 106 MB factor product
  the size of `flux-factors-1M.npz`;
- the result (`RESULT.txt`): **peak RSS 0.189 GB**, against 0.035 GB for importing numpy alone, about 42 times below
  the 8e9 B cap. It was measured on macOS (arm64, numpy 1.26.4).

The director accepted it and kept the 8e9 B guard.

## The config

`production-config.ready.json` (`3b2afde4…`) is flux3's `d797183b` with exactly two leaves changed, which the
generator checks:
- `flux_extract/sha256`: null → `90445ece147213fae5ffa08ed93d91f3e781e6983991a352241c2585b478a659`;
- `flux_custody/sha256`: null → `226c7a68d4be002f17a0500c5452ca4521550cc0cfd725788bb16ebe59dcd266`.

Those are the sha256s of run-61861637's `records/run/flux-extract.json` and `flux-custody.json`. The bound
`flux_selection_digest`, computed with `fd_rpd_reco.py` at S, stays `75c2a1f4…` and equals the extract's
`selection_sha256`. The generator also checks the committed custody receipt: status PASS, `custody_code_sha256`
`634670b3…`, `code_sha256` `7302cc1d…`, and `extract_sha256` equal to the extract's digest. S1's retention strings
are unchanged.

## Files

[`tools/gen_p0.py`](tools/gen_p0.py) generates the config, the expected values, the fence copy, the connect (with the
runner), the fetch and the launcher. It reads flux3's committed package, run-61861637's records and S1's survey log.
Blocks lifted from flux3's scripts are asserted present before counted replacements, and a rerun reproduces every
output byte for byte.

| file | sha256 |
|---|---|
| `production-config.ready.json` | `3b2afde495d630cc44df730e3e1acf12e0c332953e9fa298fa979f2e2e39b057` |
| `rpd_p0_connect.sh` | `6a1bed9547b7a462b3ccdbbe05c34f322a27980be085d2996eb89950a25da678` |
| `rpd_p0_fetch.sh` | `12626af6f6ff5d765b602ebd0f012f2e3d6f8d3f1fa60969b0f8bd4d4e022b6a` |
| `rpd_p0_launch.sh` | `b70998fffa5de0f585ef3e60e24b17c7ba166bc10e718d13187e424928e4e366` |
| `tools/fence_overlap.py` | `23d0ffc7bf89a4b81a33b081fa7377401dec33634372d5ed5b106bee6c4fd22b` |
| `tools/p0_checks.py` | `93d0de8bda48a00eeba4edab306590146f5c1d807bed701be021bdfb0b864fcc` |
| `tools/p0_supervise.py` | `6ad0f68fb309a7b83adc0f65ed709e5e2412e650e115075fe41ebbc7a070134f` |
| `tools/p0_expected.json` | `bb175e948fff89fc1e3097b0aaf5107e5e796bc05e1f4892e0d00b07b2a5b6b6` |
| `tools/gen_p0.py` | `07395b1d4f9e6e94fc2dda858ba318b9f707ac90b436def5a0fa33e9c1b0d1bf` |
| the runner (written by the connect) | `3ef4abad4f05a8ef9fb5319c6d463d72e5ecabb3bed75defa74c712a28df07c4` |

The connect embeds five files as base64: the config, `p0_checks.py`, `p0_expected.json`, `p0_supervise.py` and the
fence copy. Each decodes to the sha256 above, and the connect checks each digest on the node.

## Tests (local; nothing is contacted)

<!-- absence-ok: test-case descriptions (a worker that must not run, an empty run list), not claims that a result does not exist -->
| test | result |
|---|---|
| `tests/test_sacct_fence.sh` | flux3's test, on the block cut from this connect: **24 checks, 17/17 mutants killed** |
| `tests/test_launch.sh` | flux3's test, renamed: **23 cases, 13/13 mutants killed** (the ack guard, exit status, cert check, fence mode) |
| `tests/test_connect_start.sh` | the connect's preamble and step 9 against a stub runner, launched through the connect's own SIGINT-reset wrapper, with real processes and signals: **4 cases, 6/6 mutants killed**. Cases: the normal handoff; a delayed startup (the runner and its TERM-ignoring child stopped, the tree removed); a `runner.pid` naming another process; SIGTERM to the connect while it waits |
| `tests/test_runner.sh` | the runner, cut from the connect, with the real supervisor, real processes and signals, and a stub worker: **25 cases, 22/22 mutants killed**. Cases: all pass in order at nice 19; each step failing; an outside SIGKILL; a leftover group member; RSS over a cap; the wall cap; no handoff; not at nice 19; TERM to the runner mid-step (forwarded, the worker gone, the step not completed); SIGINT to a runner started by the connect's wrapper (rc 130, the step not completed); the supervisor killed mid-step (its group killed from the `.pgid` file); with a fake supervisor, a `past_deadline` record (rc 7), a surviving group (rc 4), a last step ending after the deadline (the final check, rc 7), no record with the group still alive after KILL (a forced `kill -0`: the tree kept), no record with `kill -0` answering EPERM on Linux (the tree kept), no record with an unexpected `kill -0` error on macOS (the tree kept), a supervisor that exits 2 without a record after the deadline (rc 7), and a failing deadline probe (its own STOP, rc 4); a clean run whose UTC time cannot be read (rc 6); a `p0.rc` that cannot be published (rc 6); a tree that cannot be removed (rc 6) |
| `tests/test_fetch.sh` | the fetch with a fake `/proc` and a GNU `date -d` stand-in: **20 cases, 12/12 mutants killed**. Cases: DONE with the decoded archive's member list equal to the send list (an exact line); DONE without `runner.pid`; STOP from another node; a malformed `p0.rc` (no end time, two lines, a trailing blank line, a NUL byte, a cause with a space, February 30); RUNNING; a reused pid; another command; a longer path; the exact command line plus an empty argument; gone; `p0.rc` published while a dead runner's `/proc` is probed, and while a live runner's command line is compared; another node; neither file; no root |
| `tests/test_p0_checks.py` | 6 passed: inputs PASS, DIFF, MISSING, no O_NOATIME, the flag used; stat; the committed expected values equal run-61861637's records |
| `tests/test_p0_supervise.py` | 17 passed, real signals: a clean exit (the `.pgid` file written); a nonzero rc; the deadline TERM (within 0.5 s); KILL at the deadline when TERM is ignored (within 0.5 s); an outside kill (not a deadline kill); a forwarded TERM; its escalation to KILL; a leftover group member killed; the worker outside the supervisor's session and group; a worker reaped after the deadline is never clean (a controlled clock); the `.pgid` file recovers the group after the supervisor is SIGKILLed; the fork gate (a supervisor killed as it publishes the `.pgid` runs no worker; mutation-checked by removing the gate); the gate never releases a worker into an expired step (a controlled clock, rc 127, nothing run; mutation-checked); the child refuses a release that arrives after the deadline (a real clock and a paused release write, rc 127, nothing run; mutation-checked); EPERM is neither delivery nor absence on Linux, and absence on macOS; a passed deadline starts nothing; usage |
| the overlap fence | on this config with a clean checkout at S: `FENCE OVERLAP: CLEAR (allowed 1, stops 0)` over 57 staged originals (`tests/fence_overlap_real_config.out.txt`) |

The outputs are in `tests/*.out.txt`.

**The squeue grep:** none of these contain `squeue`: the connect, the fetch, the launcher, and the five decoded
payloads. The generator asserts it for the scripts.

**Not exercised locally:**
- Linux `setsid`, GNU `nice`, GNU `date -d`, `/proc` and `PR_SET_PDEATHSIG` themselves. The tests stand in for them:
  a `setsid(2)` stub, a niceness stub, a `date -d` stand-in, a fake `/proc`, and the runner's `.pgid` recovery
  (which works without PDEATHSIG).
- The bound CLI. Its real steps run first as the dry runs on the node.

## Reads

The reports are under `~/codex-reports/note-measurement/reads/`. Grok's account is out of credit, so codex-school2 reads
in its place. Every blocking finding was taken as a fix; the README sections above describe the result.

| read | report | sha256 | verdict |
|---|---|---|---|
| agy, the rebuilt package | `p0-rebuild-20261123/agy/out.txt` | `22abcc7b10ac7ca0346d4212185ac860388aca813d9c4d14a1aa422c7d12faf6` | GO |
| codex-school2, the rebuilt package | `p0-rebuild-20261123/codex2/out.txt` | `1f85010cc542db2fe5ee859bd2350ebedf327760052c7aa75286dab7e92f8a53` | FIX |
| agy, confirm 1 | `p0-rebuild-delta1/agy/out.txt` | `298932c1f93d706016df7dd165887376634e93986856ceaba09dcb80adf46960` | GO |
| codex-school2, confirm 1 | `p0-rebuild-delta1/codex2/out.txt` | `95f47cdf9a0ae6b348c939510592c537bf27522458f5abe2b693010d40087a90` | FIX |
| agy, confirm 2 | `p0-rebuild-delta2/agy/out.txt` | `f31f3ab775de397a46a8151a89f172b4ad8d77736605476d8d7f1f10b8ce9ed4` | GO |
| codex-school2, confirm 2 | `p0-rebuild-delta2/codex2/out.txt` | `b0e500633181aa6f33682ef0466cd11b13dffb9cac20a73d6a5298a3b2e01fea` | FIX |
| codex-school2, confirm 3 | `p0-rebuild-delta3/codex2/out.txt` | `2a3583a4aecb98c184fc541f90c902b63850b00bbfe5a4436ead68c3f691a627` | FIX |
| codex-school2, confirm 4 | `p0-rebuild-delta4/codex2/out.txt` | `abf3b10ca7da603eb29132aec4c3eb8b36b3cb6c6c732ae27149421af78fa1c3` | GO |

What codex-school2's blocking findings were, by round:
- **the package:** a deadline that could be overrun; an orphan when the supervisor died; signal and ownership gaps in
  the startup handoff; a loose fetch identity check;
- **confirm 1:** the clock read before the sleep; a worker able to fork before its group was recorded; EPERM read as
  "gone"; a lost early SIGINT; an unchecked time in `p0.rc`; a NUL byte in `p0.rc`;
- **confirm 2:** a release into an expired step; EPERM still conflated in the runner and in signal delivery;
- **confirm 3:** a release arriving after the deadline, refused only by the parent; a missing record past the deadline
  read as rc 4.

Confirm 4 (GO) had non-blocking notes, all taken after it, with every suite rerun:
- a failed deadline probe is its own STOP: distinct exit codes 10 and 11, and a new case and mutant;
- the fork-gate guarantee is scoped to a late release, and the remaining window is named;
- the supervisor's late-release test asserts that its paused write ran;
- the macOS case forces `uname` to Darwin.

## Before the connect

1. The director's P0 binding, at the merged commit and these shas.
2. cov2d's ack no older than 6 h, saved as the ack file, and tier3-design's ack.
3. A valid cert: Joseph renewed it to 2026-11-24T05:57:28Z, and the launcher's check is the authority.
4. Then `bash rpd_p0_launch.sh connect <new dir> <login node> <ack file>`, with the output written beside the session
   directory.
5. Fetch from the runner's node until it reports DONE or STOP.
