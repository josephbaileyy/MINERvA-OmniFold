# agy's adversarial read of A2 and B3 at 135571b9: the dispositions

**The read.**
- Model: gemini-4-hydrogen-xhigh, run headless with `--sandbox` and `--dangerously-skip-permissions`.
- Inputs: 29 hashed copies of PG's own files at 135571b9, none from the blinded sets. files.sha256 is 0c3fae86…; the copies were unchanged after the read.
- Report sha256: ad79a8bbf55d4bf390a4f5e57a9956ef512401a55c8690e2ea56cf4676b65c78.
- Verdict: NO-GO, with 19 findings.

Per the relay-only rule, no reviewer wording is committed here. What follows is my restatement and what I did.

The director gave a GO on ten dispositions on 2026-11-24, with five changes. Those changes are folded in below:
- `.so` files from outside the roots are a STOP;
- run_gevgen_v3.sh's changed bytes went back to the director;
- every refusal carries a reason code;
- real-shape fixtures, plus four node checks;
- the blinding is unchanged.

## Why the tests passed

Four of the findings would have failed real runs. My stub fixtures encoded my own assumptions, so the tests could not see them. Each now has a test built on the real shape.

<!-- absence-ok: 'untested here' scopes this host's test coverage (macOS has no /proc); it is not a claim that a result does not exist -->
| # | Defect | Fix | Real-shape test |
|---|---|---|---|
| 13 | The real G2111a listing has no `genie_xsec` member. SciSoft's tarball starts at `genie_xsec/v3_04_00`. | members-check treats the container as a container. B2 creates it. | `RealShapes.test_the_real_listing_has_no_top_container_member_and_passes`; `Install.test_the_real_listing_installs` (the committed listing's names, types and targets) |
| 18a | `/proc/self/fd/9` is a magic link, and O_NOFOLLOW refuses it (ELOOP). | `tool-check --fd N` hashes the inherited descriptor and opens no path. | `test_proc_self_fd_is_a_magic_link`: **skipped on this host (macOS has no /proc), so untested here.** The node check `proc_fd_magic_link` covers it. |
| 18b | Slot 2's reduce reads CVMFS's spline, and nothing pinned it. | `trace-check --pin PATH=SHA`. pg_generate.sh passes PG_SPLINE_PINS' spline and README for every CVMFS tune. | `TraceGaps.test_slot2_reduce_at_its_real_cvmfs_path` (the real path) |
| 18c | ROOT's `openat(..., O_DIRECTORY)` on `$GENIE/lib` was gated as a read. | O_DIRECTORY opens are counted (`directories_opened`), not gated. | `test_a_real_directory_open_is_recorded_not_gated` (strace's real line format) |

## The four node checks (the director's item 4)

B3, the slot-1 public-seed replay, now also runs slot 2's traced reduce. That is an awk over CVMFS's spline, and nothing is generated for slot 2. It then runs `pg_verify.py shape-check`, and the replay needs all four checks true before slot 2 is generated:
- `real_members_listing`
- `proc_fd_magic_link`
- `directory_open_recorded`
- `slot2_reduce_real_path`

They are checked three times: by pg_replay.sh's replay.json, by pg-replay-g2111a.py's `replay_problems`, and by pg-node-launch.py's `payload_problems`.

## Dispositions

<!-- absence-ok: 'does not exist' is a fact about macOS's bash 3.2 builtins, not a claim that a result does not exist -->
| # | Finding (restated) | Disposition |
|---|---|---|
| 1 | fchdir and clone are untracked, so the cwd can go stale. | `fchdir` is added to TRACE_SET in pg_verify, the probe and run_gevgen_v3.sh, and a successful fchdir is a STOP (`fchdir`). If any process other than the initial one changes directory, every relative watched open by such a process is a STOP (`cwd-unknown`). |
| 2 | Writes were detected anywhere in the line, and O_RDWR counted as a write. | Flags are read from the argument after the path, with quoted strings stripped. Only O_WRONLY is a write. O_CREAT opens are outputs only under W. |
| 3 | The result regex matched inside a quoted path. | The result is parsed with quoted strings stripped and anchored at the end of the line. |
| 4 | An unresumed call was dropped, and children's exits were ignored. | Any call left unfinished is a STOP (`unresumed`): a process's exit does not complete it. Any child that exits non-zero is a STOP (`child-exit`). This is the same in the probe's self-test. |
| 5 | Lexical `..` normalisation diverges from the kernel. | A watched path with a `..` component is a STOP (`dotdot`). |
| 6 | A numeric dirfd with a relative path bypassed the checks. | A watched name opened, stat'ed or read-linked against a directory descriptor is a STOP (`dirfd-relative`). |
| 7 | Manifest links were not checked on disk. | In trace-check and exe-check, realpath(p) must equal the manifest's resolution (`gated-mismatch`, `exe-not-manifest`). |
| 8 | LD_PRELOAD and compat libraries were ungated, and config in W or the private product was unflagged. | A `.so` read must have its real path under CVMFS or a system library directory, or be a matching gated file. Otherwise it is a STOP (`so-outside-roots`); the director ruled STOP, not record. LD_LIBRARY_PATH is recorded, and an entry outside those roots is a STOP (`ld-library-path`). LD_PRELOAD, LD_AUDIT, BASH_ENV and ENV set at entry refuse both drivers. A config-type file read under W with no matching pin is a STOP (`config-unpinned`): a `.rootrc` in the cwd is read by ROOT. A config-type file read under the private product is gated by its `genie_xsec` path (`gated-mismatch` unless it is a member). If the real node STOPs on a library, the inventory (path, sha, pid) goes to the director before any allowlist entry. |
| 9 | Other splines, non-XML probes, defining files by any pid, and UTF-8 escapes. | Another spline is a STOP (`other-spline`). Probes are listed for every gated or config basename. Defining files must be read by the initial process. Escapes decode as bytes. |
| 10 | Inherited env, PG_STRACE_FD 0/1/2, and awk unchecked. | Hooks refuse (as in #8). run_gevgen_v3.sh refuses an fd that is 0, 1, 2 or has a leading zero. awk must resolve to a root-owned file under /usr/bin or /bin that only root can write (`system-tool`). PG_TRACE_DIR was already refused if not an existing absolute path without `..`. |
| 11 | Probe: submounts, empty xattrs, the unpinned genie_xsec.table, and the data/ filter. | Every walk compares st_dev with the root's. Empty revision or root_hash is a STOP (`repo-xattr-empty`). Each CVMFS tune's `ups/genie_xsec.table` is pinned from the record. data/ names are an allowlist: README, isotopes.cfg, reduce_gxspl.awk, xsec_graphs.root and `gxspl-<name>.xml[.gz]`. |
| 12 | check_sockets allowed a writable /run/user/<uid> and linked sockets. | /run/user/<uid> must not be group- or world-writable, and a socket that is a link is a STOP. |
| 13 | B2: the container, .upsfiles, and the lexical scratch check. | See the table above. .upsfiles must be exactly one read-only dbconfig. The parent must be its own real path, on scratch. |
| 14 | B3 accepted an incomplete replay.json and ignored deleted.json. | `replay_problems`: the nine named checks, four spline opens, four gated lists and four real shapes, all present and true. `deleted_problems`: deleted.json holds genie_v3.gst.root and only the deletable names, each with a sha and a size. No event or status file may be left. (TMPDIR and the python3.11 pin were already fixed in 46740facf.) |
| 15 | The launchers validated no payload, and rpm_match 1 passed. | pg-node-launch.py parses the sent script's own constants and checks the receipt against them (`payload_problems`). The probe launcher requires `rpm_match is True` or None. |
| 16 | pg_generate: untracked files, $PRIV extras, the seedfree race, lax checks. | `--untracked-files=all`. $PRIV extras: members-check covers genie_xsec and .upsfiles. xargs runs as a job. On any exit, cleanup freezes and kills each job's whole process tree, waits for it, and only then runs seedfree. |
| 17 | mutrun: crash conversion, FAIL+ERROR, rc unchecked, `-I` omitted. | KILLED needs a FAIL and a non-zero exit. The three try/except→self.fail wrappers are gone. Every suite runs under `-I`. Each check returns a reason code. An unexpected exception becomes `internal-error: <type>`, which only the wrapper's own test expects. Each wrapper has a mutant that relabels the crash as another reason, and it is killed. |
| 18 | Defects masked by stubs. | See the table above. Also found while fixing: `mapfile` does not exist in macOS's bash 3.2, so the slot-2 pins were silently empty in the local run. The read loop is now portable, and an empty list for a CVMFS tune is a STOP. |
| 19 | The tests don't test what they claim. | Every refusal test now asserts its reason code, and each new rule has a test and a mutant (A2 134, probe 84, B2/B3 58). |

## Not tested on this host (stated, not hidden)
- **The ELOOP itself:** `/proc/self/fd/N` refusing O_NOFOLLOW needs Linux. It is covered on the node by `proc_fd_magic_link`.
- **st_dev on a final file or final directory:** a file that is itself a mount point, or a final directory on another mount, can't be made here without root. The walk's intermediate components and listed entries are tested, using macOS's own devfs and /System/Volumes/Data mounts.
- **The end anchor of the result regex:** quote stripping already removes the case it guards, so a mutant of the anchor alone would survive. No mutant is claimed for it.

## Not changed
- `GENIE_COMPAT`-style library paths: no separate rule. Any library read is subject to `so-outside-roots`.

# Round 3: agy's and codex-school's reads of 5f141f7a

**The reads.** Both read the same head, 5f141f7a, from the same staged inputs: the delta 46740facf..5f141f7a without
logs, and 20 PG files, none of them from the blinded sets. The copies were unchanged after each read.

| Read | Model | Report sha256 | Verdict |
|---|---|---|---|
| agy | gemini-4-hydrogen-xhigh | 16bbb74c6e579903116b4e2313f2d2d499c081eece3b779018a4bd3db7da6027 | NO-GO: 20 findings, 6 blockers; my 19 dispositions: 4 HOLD, 1 WRONG (#19), the rest INCOMPLETE |
| codex-school | gpt-6.2-sol, high effort | f23847ad2397a838ee7026d69f72be9b20b2aa4f873bc9010f08847e1e727946 | NO-GO: 18 findings, 4 blockers; 162,628 tokens |

The director ruled D1–D8, D3′ and the seed (RULINGS-A2.md, round 3) and gave a GO on every mechanical fix. One
regression was mine: in 5f141f7a an inline comment swallowed `and mcheck.get("pass") is True` (agy B5). That is the
third such case, so a test now scans every PG Python file for a comment that reads as code (`CommentScan`), and a
mutant covers the clause.

## Dispositions

<!-- absence-ok: "no test", "never" and "untested" here describe this host's test coverage or a rule, not a claim that a result does not exist -->
| Finding | What was wrong | Done (reason code; a test and a mutant each) |
|---|---|---|
| agy B1 | `/usr/bin/gpg` as a link to gpg2 STOPs the probe on SLES | the first regular-file candidate is taken; "no regular file among the candidates" |
| agy B2, codex 5 | `..` STOPs real `$ORIGIN/../lib` loads; chdir paths normalised lexically | D7: realpath of the directory on the node, under an allowed root (`dotdot-outside-roots`, `resolve-failed`); raw and resolved recorded |
| agy B3, codex 5 | children inherit the cwd; a CLONE_FS thread moves the initial process | after any traced chdir, every relative watched path is `cwd-unknown` |
| agy B4, codex 6 | O_CREAT without O_TRUNC under W read an existing file unchecked | an output needs O_TRUNC or O_EXCL, under W, and is never a config, xml or so name |
| agy B5 | shape-check passed a failed members check (my regression) | restored, with a mutant; `CommentScan` |
| agy B6, codex 14 | `kill -0` on a zombie stalled cleanup 30 s per job; survivors unchecked | zombies are not alive (`alive()`, tested on a real zombie). In practice bash reaps its own jobs and init its orphans, so the stall agy described doesn't arise in a run, and the TERM test can't distinguish the guard. Each job is reaped. D6 survivor scan (cwd under W): KILL, then a STOP if any survives. The cleanup says when the scan, not the tree walk, had to act, and the TERM test requires that it didn't |
| agy 1, codex 5 | (see B3) | |
| agy 2 | `..` in chdir bypassed | D7 covers every path |
| agy 7, codex 8 | duplicate config names gave a false search-order STOP; probes pooled | D4: read path = first existing path of GXMLPATH + search_dirs; probes are records, not rules |
| codex B3 | another tune's CommonParam.xml blessed by the global manifest | D4 (`search-order`); `gxmlpath` must be exactly the tune's data dir |
| codex B1 | exe-check bound a preflight, not the run; gntpc unchecked | D1: execve traced, every exec bound (`exec-unbound`); gntpc traced and checked per task |
| codex B2 | post-run hashes; the kernel follows links without readlink | D2: threat model stated; revision start = end (`revision`); `defining-link` = realpath(p) != p |
| codex B4 | O_PATH counted as an open; an open is not use | O_PATH excluded; D3′ reduce completeness (`reduce-incomplete`, `reduce-pair-absent`) and the coverage run (`coverage-built`, `coverage-unanswered`, `coverage-none`); any other data-dir read is `other-spline` |
| codex 7 | orphan resumptions, open-ended pids, undecodable lines passed | `resume-mismatch`, `no-terminal`, `undecodable`, `openat2-resolve`; the same rules in the probe's self-test |
| agy 9, codex 12 | extra products beside genie_xsec passed members-check | `members-top`: exactly .upsfiles and genie_xsec |
| agy 10 | ROOT config by lexical location, null hash accepted; a linked W | realpath under the repo, `root-config-unhashed`; W must be its own physical path |
| agy 11, codex 13 | an empty LD_LIBRARY_PATH entry is the cwd; not recorded | `ld-library-path-empty`; the value and awk's path are recorded |
| agy 12 | awk via a link from a writable directory | the path itself and its real path must both be under /usr/bin or /bin |
| agy 13 | B2 created a directory before refusing off scratch | every existing ancestor checked before any mkdir; nothing is written |
| agy 15, codex 15 | weak types; keys by count only; gated unchecked in the launcher | one exact, typed schema shared by B3's node script and the launcher (a test keeps them equal) |
| agy 8, codex 16 | genie root's own device; reported values not compared; RPM failure = absent | `genie-mount`; the launcher compares hashes, targets and listings with the pins; `rpm_status` recorded / not-owned / query-failed |
| agy 14, 19, codex 18 | FAIL+ERROR counted as KILLED; untested wrappers and codes | FAIL with any ERROR is INVALID; each CLI's crash is `internal-error: <type>`, tested; refusal tests assert codes |
| agy 16 | ignored files in the deploy | D8 |
| agy 17 | a missing or non-directory .upsfiles in check_tree | `upsfiles:` problems, checked before listing |
| agy 18 | octal escapes took 8 and 9 | only 0–7 |
| agy 19 | a benign helper exiting non-zero would STOP | kept as a STOP; if B3 hits one, the binary and args come to the director |
| agy 20 | PYTHONPATH and friends unchecked | PYTHONPATH, PYTHONSTARTUP and PYTHONUSERBASE refuse at entry |
| codex 9 | ROOT provenance not bound to a revision | revision start = end in every run; ROOT config hashed |
| codex 10 | strace builds lacking openat2 or faccessat2 | the probe's self-test runs the exact TRACE_SET, so B1 STOPs on such a build |
| codex 11 | the seed is in the traces | the seed proposal below |
| codex 17 | B3 kept event files on a STOP | D5: a trap deletes them on every exit |

## Proposal for cov2d: the seed (codex 11, with the director's ruling)

Every file below stays in W, and the published sums omit it (`pg_lib.SEED_BEARING`). `pg_lib.py publish` runs where the
seed is known, at the end of pg_generate.sh. It leak-scans the path and bytes of every other file in W for each seed,
as decimal (zero-padding contains it) and as hex in both cases, then writes `out/PG-PUBLISH-SHA256SUMS`. A hit is a
STOP that names no seed.

| Artifact | Why seed-bearing | Where it ends up | Checked by |
|---|---|---|---|
| `gntp.<seed>.ghep.root` | gevgen's name for the run | deleted by run_gevgen after gntpc; renamed `gntp.ghep.root` by seedfree if gntpc fails | seedfree per task and on every exit; `no_seed_in_any_name` tests |
| `genie-mcjob-<seed>.status` | gevgen's name for the run | renamed `gevgen.status` | the same |
| `gevgen.trace`, `gntpc.trace` | the opens of the two files above | stay in W | SEED_BEARING |
| `gevgen.log`, `gntpc.log`, `task.log`, `task.time` | the run number, the input name, `seed=`, the timed command | stay in W | SEED_BEARING |
| `run/queue.txt`, `seeds.json`, `out/PG-SHA256SUMS`, `out/logs/*` | the seeds, their hashes, conservative for logs | stay in W | SEED_BEARING |
| trace-check records | derived: W paths are kept out of the probe list | publishable | the leak scan |
| `genie_v3.gst.root`, `input-flux.root` | unknown: whether ROOT stores the run number in them | publishable | the leak scan; B3's deleted.json records `holds_public_seed` for each, from the node |

The proposal also covers binary encodings of the seed, which the scan does not search (ROOT compresses its files).
That one is for cov2d and the director.

## What this host cannot test, and where it is tested

- **The ELOOP itself:** `proc_fd_magic_link`, a B3 shape check.
- **A final directory on another mount:** `st_dev_final_dir`, a B3 host check (a positive control on /proc).
- **A file or directory that is itself a mount inside a walked root:** `no_submounts`, from /proc/self/mountinfo.
- **The end anchor of the result regex:** `result_anchor_real_strace`, the pinned strace's own line for a path holding
  `) = -1`.
<!-- absence-ok: 'no real mount or race reaches' scopes this host's test coverage of two guards (each is fault-injected and mutated), not a claim that a result does not exist -->
- **Two guards no real mount or race reaches on this host, which the director rules UNTESTED-ON-HOST, not
  equivalent:**
  - the probe's fstat check on a tool after its regular-file lstat (a race);
  - list_rel's final-directory device check, which here the entries check always catches first.
  Each is tested by fault injection (`test_a_tool_that_changes_after_its_lstat`,
  `test_a_final_directory_on_another_device`) and has its mutant. On the node, B1's probe records `mount_control`, a
  walk from / into /proc that must refuse; the launcher requires it.
- **The kill rule:** it is printed at the head of every mutants.log (mutrun.RULE).
- **GENIE's real behaviour, which the stubs assume:**
  - which execs occur;
  - that the initial process opens `$GENIE/lib` as a directory;
  - gntpc's config reads;
  - GXMLPATH being exactly the data directory;
  - the coverage log's lines.
  B3 STOPs on any surprise, and the director gets the inventory before any rule changes.
