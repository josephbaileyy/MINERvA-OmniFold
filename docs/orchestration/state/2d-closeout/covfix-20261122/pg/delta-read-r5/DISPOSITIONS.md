# Round 5: the codex-school and Sonnet 5.5 delta reads of 7415d0c4, and proposed dispositions

<!-- absence-ok: "not built", "never", "no test", "absent" and "not verified" here record dispositions, the state of the code and what this host can check, not a claim that a result does not exist -->

**Reads.**
- codex-school gpt-6.2-sol, effort high, sandbox read-only: NO-GO, 18 findings, 206,061 tokens.
- claude-personal claude-sonnet-5-5, tools Read, Grep and Glob: no blocker, 7 majors and 5 minors, 79,226 output
  tokens, $1.75 list.
- Both ran read-only from a copy of 32 files at 7415d0c4 (`INPUTS.sha256`), with stdin closed. The brief is
  `BRIEF.md` and holds no blinded set. Every input hashed equal before and after both reads.

**Blocking rule** (the director, as for EVW5D). A finding blocks if it could change a generated event, a recorded
seed or schema, or what a gate accepts. A deterministic false STOP of a correct run counts, because the gate then
rejects what it should accept. Everything else goes to the follow-ups list.

**Status.** Nothing below is built yet. These are proposals for the director's GO. "Verified" means I checked the
claim against the code, or against GENIE R-3_04_00's source fetched from GitHub. "Read" means I accept it from the
reader's description without reproducing it.

## Blocking: proposed fixes

| # | findings | verified | defect | proposed fix |
|---|---|---|---|---|
| B1 | C1, S6 | verified (AlgConfigPool.cxx:144-153, 273-280; XmlParserUtils.cxx:51-90) | **False STOP on every correct run.** `LoadMasterConfig` and `LoadSingleAlgConfig` call `AccessPathName` again on the path `GetXMLFilePath` chose, so a second run of probes starts mid-list and fires `search-probes`. The list also changes: the tune and CMC directories are added only once the tune is configured. So `Messenger.xml` and other early lookups walk a shorter list. | Two expected lists: before the tune (GXMLPATH, config, GNuMINtuple) and after it (with the tune and CMC directories). A walk may match either from its start. Successful re-probes of the selected path that follow the walk directly are accepted. A walk restarts at each probe of the list's head. Tests use the AlgConfigPool sequence. B3's real traces are the check. |
| B2 | C2 | verified (code) | A searched XML read with no probes passes. | A searched read needs a walk ending at it. The `EACCES`-as-absent part is rejected: `AccessPathName` treats EACCES as absent too, so the check matches GENIE. |
| B3 | C3 | verified (pg-replay-g2111a.py:242) | **Every correct B3 STOPs at the launcher.** The node runner keeps 7 fields of `replay.json`, and the launcher requires identity, execs, revision and gst_schema. | Send the whole validated `replay.json`. Test the runner's actual `PG-RESULT` through the launcher's `validate()`. |
| B4 | C4 | verified (`fresh()`) | One ENOENT blesses every later `O_CREAT` open of that name by the same process, because opens are not "last words". | An open consumes freshness. gntpc's GHEP input is bound to its task's own gevgen output (`--input`). The different-pid race is rejected: a process creating the file between the probe and the open is itself traced and checked. |
| B5 | C5 | verified (pg_lib.py:294-297) | A negative gap can jump the walk past `fEND`, skipping compressed bytes. Free records can keep old compressed objects. Inflation does not check that all input was consumed. | Every byte of [fBEGIN, fEND) must be a key or a gap, with no jump outside. Gap bytes are searched for ROOT block headers, and each one found is inflated and scanned. zlib, LZMA and ZSTD must consume exactly csize. LZ4's checksum is checked if xxhash is present; otherwise the root-codec-unavailable STOP applies. |
| B6 | C6, S3 | verified (code; hadd is conda ROOT 6.28, gntpc is CVMFS ROOT) | `*_ALL.gst.root` is written by hadd, which B3 never runs. A different StreamerInfo or key set would STOP publication only after the whole generation. | B3 also hadds its public gst under `anaenv` and records `gst` and `gst_merged`. `schema_problems` checks each published gst against its kind. Parsing branch and leaf declarations goes to follow-ups. |
| B7 | C7, S4, S5 | verified (leak_scan's `continue` on a path hit; gz not inflated; np.savez uncompressed) | (i) B3's control never decodes the gheps whose names carry the public seed. (ii) An int32 seed in a small non-basket object is lost in the chance count. (iii) The allowlisted `.xml.gz` splines are not inflated. | (i) Name and bytes are scanned separately, and B3 records both. (ii) int32 is a STOP in every object other than TBasket payloads, and is counted only in baskets. cov2d's condition on the confirm stands. (iii) Inflate gzip and every zip member. Any other compressed container is a STOP. |
| B8 | C8 (part), S7 | verified (sha_path O_NOFOLLOW) | On a revision change, gated entries are re-hashed by their lexical path, so a manifest symlink STOPs a correct run. | Re-hash gated entries by their recorded real path, and check that the link target is unchanged. **Rule question:** see Q1. |
| B9 | C9, S1, S2 | verified (GNU timeout calls setpgid unless `--foreground`; scan code) | Each task's `timeout` makes a new process group, so the group scan sees only xargs, `bash -c` and `time`. Any non-ancestor process with cwd in W is killed, including a parent's `tee`. The poll counts sleeps, a scanner failure passes, and new survivors are not signalled. | Scan by session (`os.getsid`). setsid gives one session, and timeout keeps it. Only that session's processes are killed. A process outside it with cwd in W is a STOP and is not killed. The drain uses a monotonic 30 s deadline and signals every survivor it finds. A failed enumeration is a STOP. The test's stub `timeout` calls setpgid and runs `cd /`. |
| B10 | C10, S8 | verified (code) | A successful `O_RDONLY\|O_TRUNC` outside W passes. A symlink created in W can point outside, so a later write to it leaves W. | O_TRUNC counts as a write. A successful symlink or link is a STOP, since no role makes one. mkdir and mknod go to follow-ups (Q3). |
| B11 | C12 | read; the argv half verified | A spline inside an XML comment passes the reduce check, and knots are not counted. A sealed-only `TUNE=` in the genie block passes `argv-check`. | Parse the splines with iterparse, which skips comments, and count actual knots. The genie block gets the coverage block's assignment rule. |
| B12 | C13 | read | Both validators accept a deletion record with empty coverage maps and arbitrary provenance strings. They never compare the deleted gst's schema with `gst_schema`. | Exact expected names per phase. `pinned_by` and `bound_by` from a fixed set. The deleted gst's schema must equal `gst_schema`. The same checks run on both sides. |
| B13 | C14, S10 | read; `-B` verified | B3's deletion helper aborts on a broken `deleted.json` or a non-OSError parse error, leaving later files undeleted. It runs without `-B`. The runner checks leftovers only after rc 0. | Catch every exception per file. Write the record before each unlink. Tolerate an unreadable earlier record, and note it. Add `-B`. The runner checks leftovers on every terminal path. |
| B14 | C16 | verified (pg_generate.sh:350-353) | `run/deploy-status-after.txt` is allowlisted but written after publication, so it is never scanned or listed. | Take `deploy_unchanged after` before publish. After publish, compare again without writing a file. |
| B15 | C17 | verified (`re.match`) | A terminal record with trailing text, or an event after a process's terminal record, passes. | Match terminal records exactly. Any event after a pid's terminal record, or an unfinished call overwritten before it resumes, is a STOP. strace's version is caught at B1: its self-test runs the full trace set. |
| B16 | C18 | verified | M169's anchor matched twice after my drain edit, so the stopped receipt would have marked it INVALID. The C19 Linux fixture never got the real strace that round 4's disposition promised. | M169's anchor is fixed and every anchor re-counted: 263, 100 and 74, all exact. The receipts rerun on these bytes. The C19 fixture opens the pinned strace on fd 3. |

## Questions for the director

- **Q1 (C8, S7's rule).** Codex: a re-hash after the run cannot show which revision's bytes GENIE read. A file could
  differ from its pin at revision A and return to it at B. The options:
  - (a) keep S7 and accept that residual;
  - (b) restore D2's strict equality, so any revision change is a STOP. That reopens Sonnet's round-4 operational
    false STOP.
  - (c) at the start, hash every pinned CVMFS file once more, so both ends are checked.

  I recommend (c): it is cheap, and with S7 it brackets the run.
- **Q2 (C15, C3's scope).** A crash can send argv or memory to the node's core handler outside W. Proposal: B1 and
  `node-record` record `/proc/sys/kernel/core_pattern` and the core limit, and pg_generate sets `ulimit -c 0`. The
  director's C3 threat model may already put privileged site collectors out of scope.
- **Q3 (S8).** mkdir, mknod, truncate, chmod and utimensat are not traced. Adding them changes the trace set and
  run_gevgen_v3.sh's sha again. I recommend tracing mkdir, mknod and truncate.

## Follow-ups (not blocking)

- C2: bind the traced launch's own environment, not the setup's GXMLPATH. pg_generate refuses GXMLPATHS and GALGCONF,
  and every launch inherits its shell.
- C11:
  - Bind each role to its exec epoch.
  - Allow dirfd-relative lookups and track cwd per process; today these STOP, which fails closed.
  - Replace `ROOT_GENIE_LIB` with a list (S9: it matches libEGL and misses libGenVector). The proposal is to allowlist
    the system-directory libraries B3 observes, confirmed with root-schemas.json.
- C6: compare parsed TTree branch and leaf declarations.
- C10: enforcing writes at execution (Landlock or a mount namespace). strace only verifies.
- C12: interaction strings in the coverage log carry no tune identity. The coverage run's argv and its spline read
  bind the tune.
- S9, S11 (a symlinked directory in W refused at publish), S12 (cosmetic).

## Rejected

- C9's "drain before the first final rename": each task renames only its own directory, after its own gevgen exits,
  by design.
- C2's EACCES (see B2), and C4's different-pid race (see B4).

## Outcome (the director's GO, 2026-11-25: all 16, Q1 (c), Q2 yes, Q3 yes)

<!-- absence-ok: "untestable", "not exercised", "skipped" and "no abort" here record this host's test coverage, not a claim that a result does not exist -->

All 16 blocking fixes are built as proposed, with Q1 (c), Q2 and Q3. The three rejections stand (the director
accepted them as reasoned). Where the director asked for fixtures from the real format:
- GENIE R-3_04_00's lookups (`Trace.xml`, `search_list`) are built from XmlParserUtils.cxx and AlgConfigPool.cxx at
  that tag. They are not a recorded trace. B3's real traces remain the check.
- The tests' `timeout` stub calls `setpgid(0, 0)` as coreutils' timeout.c does without `--foreground`.
- hadd's output name is read from `pg_generate.sh`. B3 now runs hadd itself.

**Order.** B1's fixture rebuild came after its code. For the rest the tests were written with the code. As the
check, every new test was run against 7415d0c4's code: the new verify, Generate, Leak5, Replay, probe and install
tests fail there. The exception is `test_hadds_output_is_the_merged_kind`, which checks a name that did not change.

**Built beyond the list, each with a test:**
- `_tstring` refuses a key whose names run past the file, which used to be a bare IndexError.
- An unparsable spline file is a named `spline-unparsable` Fail.
- `root-schemas.json` holds `gst` and `gst_merged`, both null.

**First receipts run: 6 survivors, each closed by a test.**
- Probe M103–M106 (core_pattern, after-terminal, terminal-malformed, unfinished-overwritten):
  - `ProbeRound5` sat after `if __name__ == "__main__"` in test_pg_probe.py.
  - The mutant runner runs that file as a script, so those tests never ran there. `-m unittest` did run them, which
    is why the suite looked green.
  - The block is now last.
- Install M69 (an exec's hash unchecked): no payload had an exec with a bad hash. The case "an exec without its
  hash" now does.
- A2 M231 (this shell's parents killed):
  - Under drain, the parent bash is outside the run's session, so it is never killed.
  - Without the skip, the parent counts as an outsider with its cwd in W. That is a false STOP on a correct run.
  - The test now runs a passing run and a failing run with the parent's cwd in W. Both must leave the parent alive
    and must not say "outside this run".
- A scratch run of only these six killed all six. The receipts in this commit are a full second run on the final
  bytes.

**Not exercised on this host:**
- The node runner's `quiesce` needs /proc.
- Writing the deletion record before each unlink needs an abort to be injected between them, and none can be.
- The Linux paths of `survivor_scan` (/proc). The tests run its ps/lsof path.
- The C19 Linux host fixture now opens a real program (strace where installed) on its descriptor, and is skipped on
  macOS.
- The mutant of `survivor_scan`'s real-path W is killed only where the temp directory sits behind a link, as on macOS.

**cov2d (2026-11-25).**
- No objection to C3 and C4 as built.
- The gen-spec has six keys: env_set and env_keep, and TMPDIR in neither list.
- README-pg.md's table carries this lane's split: env_set PG_DEPLOY_PIN and PATH=/usr/bin:/bin (GENIE_COMPAT and
  ROOT628_* only if used); env_keep HOME, SLURM_JOB_ID and SLURM_CPUS_ON_NODE.
- SCRATCH is in neither list. Only setup_salloc_env.sh reads it, for an overridden TMPDIR and an unused CODEX_HOME,
  and the driver tests run without it. cov2d's spill scan of `$SCRATCH/tmp` therefore stands as built.
