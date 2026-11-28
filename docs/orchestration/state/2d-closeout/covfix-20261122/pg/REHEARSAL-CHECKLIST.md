# PG rehearsal checklist: what the first real run's log must answer

<!-- absence-ok: "untested", "cannot" and "no line" here describe this host's test coverage and how to read a log, not a claim that a result does not exist -->

The director (2026-11-25) accepted two guards that this host cannot exercise, on condition that the first real run
shows whether each fired or was needed. Both log a count-only line to pg_generate.sh's stdout, which holds no seed and
no path under W. Read that stdout after the rehearsal and record each answer here, with the run's head sha.

| guard | code | log line if it fired | if no line |
|---|---|---|---|
| A job reaped only once it is dead (one in uninterruptible sleep cannot hang the cleanup) | `kill_tree` | `[pg] cleanup: a job is left unreaped, still alive after KILL`, and before it `[pg] cleanup: <n> processes of a tree outlived KILL by 15 s` | every tree ended within 15 s of KILL; the guard was not needed |
| The 30 s poll after KILL in the drain (`pg_verify.py drain`, the generation's session) | `drain` | `[pg] cleanup: <n> processes outlived their trees`, then `the survivors ended after <i> polls (0.5 s each, 30 s at most)` or `<n> survivors still alive 30 s after KILL` (a STOP) | no survivor outlived its tree; the poll was not needed |
| A process outside the run with its cwd in W (round 5) | `drain` | `[pg] cleanup: <n> processes outside this run have a cwd in W (not killed)` (a STOP) | none was there |
| Quiet means two empty scans in a row (round 6, K7) | `drain` | the `<i>` in `the survivors ended after <i> polls` includes the confirming scan | n/a |

For each line, record the step it follows (`[pg] ...: pass` or STOP), and for the poll, the `<i>` at which the
survivors ended.
On this host, `test_an_orphan_that_left_w_is_killed_by_its_group` exercises the drain's first two lines, and
`test_a_process_outside_the_run_with_its_cwd_in_w_stops_and_lives` the third row. `Round5Drain` exercises the 30 s
deadline with a simulated clock. The first row, and the 30 s STOP on a real kernel, are not exercised here.

Also record, from `W/out/node_check.json` (C3 and Q2, a record and never a gate): `hidepid`, `slurm_job`,
`all_cpus_allocated`, `other_user_processes`, `core_pattern` and `core_limit` (the job's, 0 after `ulimit -c 0`).
From `W/out/pin_hash_start.json` and `pin_hash_end.json` (Q1): `files`, `links` and `pass`.

| run | head | kill_tree | drain poll | node_check |
|---|---|---|---|---|
| (rehearsal) | | | | |

**B3 (round 6), from `run/deleted.json` and the driver's log:**
- `[replay] t0's GHEP removed by the wrapper: pass`.
- For each coverage GHEP: `decoded.hits` (expected to include `int32-object` or `inflated`), `bytes_inflated`, and
  `codecs`. GENIE writes its run number (the public seed, as Long_t) in `NtpMCTreeHeader`, the first key after the
  file's own (NtpWriter.cxx:117). Since round 7 the fixtures do the same, in both a stored and a compressed form.
  Whether the real GHEP stores the public seed (its run number) in decoded bytes is not confirmed on this host. If
  it does not, both validators STOP with "the control's seed was not found decoded", and the control must be
  redesigned before the generation.
- **Round 7 (R1), for the director's decision:** each coverage GHEP's `decoded.seed_objects`, as it stands. Expected:
  `genie::NtpMCTreeHeader`, with `inflated` false if ROOT stored the header verbatim (it compresses only objects of
  more than 256 bytes), or true if it compressed it. The director decides from this record whether a compressed
  witness is needed.
- The node runner's `quiesced` (expected 0) and `quiet` (expected true).

**Round 7 (round 6's confirm read, the director's ruling of 2026-11-26), on the node, before B3:**
- R4: `import zstandard, lz4.block, xxhash` exits 0 under both interpreters that run pg_lib's scan: B3's deletion
  helper (`/usr/bin/python3.11 -I`) and production's publish (`python3` after `source setup_salloc_env.sh`, the
  analysis environment). If it fails, a ZSTD or LZ4 block in any ROOT output that interpreter scans is a STOP
  (`root-codec-unavailable`). Record the three versions under each.
- Codex 9 (a follow-up, C10): W's staged inputs hold no symbolic links. Record the output of `find W -type l`, run
  after staging and before the run (expected empty).

| item | expected | recorded |
|---|---|---|
| `import zstandard, lz4.block, xxhash` (`/usr/bin/python3.11 -I`) | exit 0, with versions | |
| `import zstandard, lz4.block, xxhash` (the analysis environment's `python3`) | exit 0, with versions | |
| `find W -type l` after staging | empty | |
| each coverage GHEP's `seed_objects` | `genie::NtpMCTreeHeader`, `inflated` true or false | |

**Round 8 (B3 run 2's exe-check STOP; the director's rulings, 2026-11-26): the compat-lib shim.**
- **The home-filesystem risk.** libxxhash.so.0, which ROOT's libCore.so needs, has no provider on the node's system or on
  CVMFS (install/b3-diag/b3-xxhash.out). It is pinned at the analysis conda env's real file
  `/global/u2/j/josephrb/.conda/envs/root_6_28/lib/libxxhash.so.0.8.2` (sha256 69468b35…). That file is on home, not
  revision-tracked, and `conda` can change it. A change before or during a run fails closed, at pin-hash's start or
  end. No other lane is known to write to root_6_28; one that does must say so before the generation.
- Record from each run: `pin_hash_start.json` and `pin_hash_end.json` with the three shim libraries hashed and
  matching, and `revision_start.json` and `revision_end.json`'s `repos` for minerva.opensciencegrid.org (baseline
  revision 2719, root hash aa0fa0c9…), with `revision_compare.json`'s `repos` entry.

| item | expected | recorded |
|---|---|---|
| the three shim libraries in pin-hash at start and end | each matching its pin | |
| minerva's revision at start and end | recorded; if changed, the pinned libraries re-hashed | |

**Round 9 (B3 run 3's graphs trace-check STOP; the director's rulings, 2026-11-27): ROOT's interpreter.**
- Record from each traced ROOT program's check: every exec's `bound_by`; the interpreter family's execs are children
  bound "interpreter pin", and no other process exits nonzero. Any `interp-*`, `exec-unbound`, `child-exit` or
  `dotdot-outside-roots` is a STOP to bring back, not to pin around.

| item | expected | recorded |
|---|---|---|
| graphs, coverage, gevgen and gntpc trace checks | pass; the family bound "interpreter pin", children only | |
| allowed '..' directories | only `/`, `/usr/include/bits`, `/usr/x86_64-suse-linux/lib`, probes or directory opens | |

**Round 10 (B3 run 4's coverage STOP; Joseph's decision, 2026-11-27): D3′(ii) on the flux path, validated in run 5.**
- Record from coverage_check.json and coverage_check_slot2.json, and from both coverage_kept.json files (kept on
  every exit under the runner's flag). The rule gates the sealed G only after run 5 has passed on both tunes and the
  director has read the kept records.

| item | expected | recorded |
|---|---|---|
| slot 1 (G21_11a_00_000) and slot 2 (G18_02a_00_000) coverage checks | pass: per pair one driver, its inventory found and in the reduced spline, one sum spline of N blocks | |
| each driver's N ("using N knots") | the same for every pair (GMCJDriver.cxx:467 sets 100) | |
| inventory size per pair, both tunes | recorded | |
| kept records, both slots | 0600, their sha in deleted.json, the other records' counts by stream | |
| records of other streams inside a sum spline | none (each a STOP) | |
| the coverage log's bytes and lines | measured (DESIGN §3, cost) | |
| each coverage run's stderr (gevgen.err) | its sha256, bytes, and lines by ROOT's message forms; no GENIE record in it | |

