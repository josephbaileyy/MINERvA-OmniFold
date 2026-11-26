# Round 5 confirm read: codex-school on 63466b617..dc341d3f8, with proposed dispositions

**Read.**
- Reader: codex-school, gpt-6.2-sol, reasoning effort high, read-only sandbox, 681,859 tokens.
- Input: `files/`, hashed in `files.sha256`. It held the fix diff, the changed code files at dc341d3f8, the round-5
  DISPOSITIONS, and GENIE R-3_04_00's AlgConfigPool.cxx, XmlParserUtils.cxx, RunOpt.cxx and Messenger.cxx.
- The copies were unchanged after the read.
- Prompt: `prompt.txt`. Report: `codex-school-report.txt`, verbatim.
- Verdict: NO-GO, with 16 blockers, 1 major and 1 minor.

**Rule (the director).** A finding is blocking only if it could change a generated event, a recorded seed or
schema, or what a gate accepts. A deterministic false STOP on a correct run also counts.

**How each finding was checked.** Each was checked against the code at dc341d3f8 before it was disposed.
- "Verified (code)": confirmed by reading the cited lines.
- "Verified (run)": reproduced in memory.

## Blocking: proposed fixes

| # | finding | verified | defect | proposed fix |
|---|---|---|---|---|
| K1 | F1 | verified (code; Messenger.cxx:103, :132) | **False STOP on every correct run.** `Messenger::Configure` looks up `Messenger.xml` by basename. `SetPrioritiesFromXmlFile` then calls `GetXMLFilePath` again on the absolute path it chose. That is the explicit "dir//abs" walk. pg_verify's explicit branch requires every non-explicit probe before the read to be a successful re-probe of `p`. The basename walk's failed GXMLPATH probe breaks that rule, so `search-probes` fires. | In the explicit branch, the probes before the explicit walk may form complete basename walks (each fitting a list, by `walk_lists`) that end at `p`, or be re-probes of `p`. Add a fixture with Messenger's own sequence: basename walk, explicit walk, read. |
| K2 | F3 | verified (code; run_gevgen_v3.sh:93, pg-replay-g2111a.py:125, :196–198) | **Every correct B3 STOPs at the node runner.** The genie wrapper removes `gntp.<seed>.ghep.root` after gntpc, but `DELETABLE["t0"]` lists `gntp.ghep.root`, and `deleted_problems` requires those exact names. The install fixtures carried a t0 GHEP that the real producer never leaves. The driver's stub matches the real wrapper, so nothing linked the two. | Drop `gntp.ghep.root` from t0 in both validators. B3 checks that t0 has no GHEP after the wrapper; this is a recorded check. The coverage GHEPs (public seed, in their names and bytes) remain the decode's positive control (K6). Add a test that feeds the driver's actual `deleted.json` and `replay.json`, written by the stubbed run, through both validators. |
| K3 | F5 | verified (code; pg_lib.py:278–299, :357–374) | (i) In a free gap, a ROOT block whose codec is unavailable, whose checksum fails, or which has trailing bytes is skipped as "not a header". (ii) The live-key loop stops once the declared size is inflated and never checks that the blocks used all of the key's bytes, so a further compressed block in the key is never inflated. | (ii) Require `q == len(data)`: `fNbytes = fKeylen + the blocks`. (i) First parse the old key header kept in each gap: ROOT overwrites only its first 4 bytes. For each record identified this way, read its blocks strictly, as for a live key: any codec failure is a STOP, and its class is kept. In bytes that cannot be identified, keep the header search, but a well-formed header (known tag and method byte, sizes inside the gap) whose codec module is missing is a STOP. |
| K4 | F6 | verified (code; pg_lib.py:341, :382–389) | **The schema depends on free space.** A gap's inflated blocks come back as key `("(free)", "", "")`, and `root_schema` adds that to the key set. A B3 gst with no inflatable free block and a production gst with one, or the reverse, get different schemas. That can STOP publication of a correct run, because AutoSave counts differ with the event count. | `root_schema` skips the recovered blocks: schemas take live keys only. The leak scan still reads the recovered blocks. Under K3, a recovered block keeps its old key's class, so a freed TBasket is treated as a basket by the int32 rule. |
| K5 | F7 | verified (code; pg_lib.py:436) | **A zip member can escape the scan.** `z.read(name)` for each name in `namelist()` reads the last member of a duplicated name twice. The magic allowlist also passes a file in an unknown wrapper as raw bytes. | Iterate `infolist()` and read each `ZipInfo`. A duplicated name is a STOP. A `.gz` file must start with gzip's magic and a `.npz` file with zip's; otherwise it is a STOP. |
| K6 | F8 | verified (code; pg_lib.py:451–462; pg_replay.sh:111–121) | **B3's positive control can be vacuous.** A raw hit (`hit = "bytes"`) skips `root_keys`. ROOT writes the file name into the first key, so a coverage GHEP named with the public seed hits raw and is never decoded. The validators accept a `decoded` record with `bytes_inflated` 0. | `leak_scan` gains `decode_all`: B3's helper always decodes and records the codecs, bytes inflated and each kind of hit (`path`, `bytes`, `inflated`, `int32-object`). In production a raw hit stays an immediate STOP. Both validators require every coverage GHEP to have `bytes_inflated > 0` and an `inflated` hit. That is the control: the seed found in decoded bytes. |
| K7 | F10 | verified (code; pg_verify.py:1301–1305, :1325–1327, :1355–1361) | **The drain can certify an incomplete quiescence.** A `/proc/PID/stat` that cannot be read counts as a zombie and is skipped. One empty scan ends the drain, so a child forked after `listdir`, whose parent exits before `getsid`, is missed. | An unreadable state is checked by `getsid`: ProcessLookupError means gone; otherwise the process counts. Quiescence needs two consecutive empty scans, 0.5 s apart, inside the same 30 s deadline. On macOS (tests only), a failed lsof is a Fail. |
| K8 | F14 | verified (code; pg-replay-g2111a.py:237–252, :303–305) | The node runner KILLs the driver's session once, never waits for it to empty, and goes on to `leftovers()`. A straggler is recorded (`quiesced`) but is not a STOP. | `quiesce` KILLs, then rescans until the session is empty, needing two consecutive empty scans, for at most 30 s. A non-zero count, or a session that is not empty, is a STOP. `leftovers()` runs after that. |
| K9 | F2 (part) | verified (code; pg_verify.py:675, :695–698) | `walk_lists` accepts the untuned list for any read. Once the tune is configured, a lookup that skipped the tune directories, which GENIE would search first, passes `search-order` if the default config has the file. | The lists are bound per process: once that pid's walk follows the tuned list, a later walk on the untuned list is a STOP. The Messenger lookups come before the tune is configured (RunOpt, then AlgConfigPool), so the fixture keeps that order. |
| K10 | F11 | verified (run: ElementTree gives `'12'` for `1<!-- c -->2`) | A comment inside a knot's text is joined into one value by ElementTree. GENIE's libxml2 reader sees two text nodes. | Parse with comments kept (`TreeBuilder(insert_comments=True)`). A comment or processing instruction inside a `spline` element is a STOP, `spline-unparsable`. |
| K11 | F15 (part) | verified (run: an unfinished call, then a complete call on the same pid, then the resume: no problem raised) | One thread runs one syscall at a time. A complete call on a pid whose call is still pending is impossible in a real trace, but it passes. | A complete syscall record on a pid with a pending call is `resume-mismatch`. Both pg_verify and pg-probe are changed. |
| K12 | F16 | verified (code; pg_verify.py:526–530) | The write boundary for mkdir, mknod and truncate, and for opens, compares lexical paths. A symlinked directory already in W makes a path outside W look lexically inside it. The link ban (B10) covers only links made during the run. | Each write target's parent is resolved at check time: `realpath(dirname)` must lie under `realpath(W)`. A parent that no longer exists keeps its lexical path, because then no link sits on it. |

## Not blocking

| finding | disposition | reason |
|---|---|---|
| F4 (B4) | **minor; hardening in this round** | Covered elsewhere. The gevgen trace check runs before gntpc's and is gated. It makes any `O_CREAT` without trunc, excl or freshness a write STOP in every pid (pg_verify.py:519). So the path `created_ghep` returns is one the gate has already accepted as a fresh output. Hardening: `created_ghep` also requires the creating pid to be the trace's initial process, which is gevgen. |
| F9 (B8) | **minor; follow-up** | Covered by Q1(c). `pin_hash` reads every manifest link's target against the manifest at the start and the end (pg_verify.py:1117–1124), so a retarget that lasts to either end is a STOP. One that reverts between them is the residual the director accepted in Q1. Hardening (record the resolved target with the trace receipt) goes to follow-ups. |
| F12 (B11) | **minor; fixed in this round** | `argv_problems` reads the pinned run_gevgen_v3.sh, whose bytes the deploy pin and the director's sha fix. `TUNE[0]=` would change an approved byte. The assignment pattern will still match subscripted and `+=` forms (`NAME(\[...\])?\+?=`). |
| F13 (B13) | **major; fixed in this round** | It fails closed. A prior record of the wrong shape raises outside the per-file handler, the helper returns 1, and the runner's `leftovers()` removes the files and STOPs. That is a STOP on a corrupted ledger, not on a correct run. Fix: a record that is not a dict of dicts is `_prior: "unreadable"`, and each `save()` writes a temporary file in the same directory, then `os.replace`. |
| F15 (thread exec) | **rejected** | strace's `+++ superseded by execve in pid N +++` follows a non-leader thread's exec. bash, gevgen and gntpc exec from single-threaded processes. Codex found no thread exec in the workload. The strict rule stays, and B1's and B3's real traces will show the form if it occurs. |
| F2 (staged messenger), B2 | **rejected** | The coverage messenger under W is a gated input: `Messenger_pg.xml` is in `GATED` and is hashed. GENIE's explicit walk on it can only fail (dir//W/... does not exist), and a read of any other path would be the read's own path, which is checked. <!-- absence-ok: a statement about a file path GENIE probes, not about a result --> |
| F17 (C19) | **major; fixed in this round** | A test gap. The C19 fixture asserts `result_anchor_real_strace` and skips when no strace is installed, instead of substituting Python. |
| F18 | **minor; fixed in this round** | The comment at pg_generate.sh:157 says what `ulimit -c 0` does: no ordinary core file. A piped core handler ignores the limit, and Q2 leaves the site's collectors out of scope; both are recorded in B1 and node-record. |

## Per-fix verdicts that change no code

- B3, B10, B14, Q1, Q2: closed (codex).
- B16: M169 is closed. C19 is F17.
- Q3: the five syscalls are traced. The boundary is K12.

## Cost and order

- Rerun: all three suites and every mutant. Mutants are added for K1–K12 and for the F4, F12, F13 and F17 changes,
  and every anchor is re-counted after the edits.
- Bytes that change: pg_verify.py, pg_lib.py, pg_replay.sh, pg-replay-g2111a.py, pg-node-launch.py, pg-probe.py
  and pg_generate.sh (the comment).
- Unchanged: run_gevgen_v3.sh, whose sha stays 5c3fd520…

## Outcome (round 6, the director's GO of 2026-11-26)

**Scope.**
- The director's blocking rule: a false STOP of a correct run, or a gate that can miss something correct producers
  really emit.
- Built: K1, K2, K3, K4, K6, K7, K8, K9, K11 and K12, and the hardenings F4, F12, F13, F17 and F18.
- K5 and K10 are deferred to `../../FOLLOWUPS.md`, as are the optional gzip and zip magic checks.
- The rejections of F15 (thread exec) and F2/B2 (the staged messenger) stand.
- run_gevgen_v3.sh is unchanged (5c3fd520…).

**Red check.** The new tests were written first and run against the code at 8f6cab162. Every new test failed:
- verify: 8 failed;
- covfix: 11 failed;
- install: 8 failed;
- probe: 1 failed.

The passing tests in those runs were inherited ones.

**As built.**
- **K1:** Messenger's real sequence is a fixture: basename walk, explicit "dir//abs" walk, then the read. In the
  explicit branch, the probes before the walk may form whole basename walks that end at the read path, or be
  re-probes of that path.
- **K2:**
  - The driver's own `deleted.json` and `replay.json` from a stubbed run go through both validators.
  - t0 has no GHEP in `DELETABLE`.
  - B3 STOPs if the wrapper leaves `gntp.*.ghep.root` in t0.
- **K3:**
  - A live key must use all its bytes.
  - A free gap's freed records are parsed by their kept key header and read strictly, keeping their class.
  - In bytes no record covers, a well-formed header whose codec module is missing is a STOP.
- **K4:** schemas take live keys only.
- **K6:**
  - B3's leak scan decodes even after a raw hit, and records every kind of hit.
  - Both validators need each coverage GHEP's seed found in decoded bytes: `holds_seed`, `bytes_inflated > 0`, and an
    `inflated` or `int32-object` hit.
- **K7 and K8:**
  - pg_verify's drain needs two empty scans in a row, 0.5 s apart, within 30 s, and an unreadable state goes to
    `getsid`.
  - The node runner's `quiesce` does the same.
  - A straggler, or a session that does not empty, is a STOP before the files are swept.
- **K9:** the search list is bound per process. Once a pid's walk has followed the tuned list, an untuned walk is
  `search-phase`.
- **K11:** a complete call on a pid with a pending call is `resume-mismatch`, in pg_verify and in pg-probe.
- **K12:** a write's target is resolved against `realpath(W)`. For open and truncate this is the full path, because
  both follow the last link; for mkdir, mknod, rename, link and unlink it is the parent.
- **F4:** the GHEP that `created_ghep` names must be created by the trace's first process.
- **F12:** subscripted and `+=` assignments are matched.
- **F13:**
  - A prior record that is not a dict of dicts is `_prior: "unreadable"`.
  - Each save writes a temporary file, then calls `os.replace`.
- **F17:** C19 asserts `result_anchor_real_strace`, and skips without strace.
- **F18:** the core-file comment is reworded.

**Fixture realism fixes found while building.** Each was a gap in a test fixture, not in a producer. All are fixed.
- The gst template had no StreamerInfo, so `_schema_ok` could never pass on it.
- The GHEP template now stores the run number as an int64, as GHEP does.
- The install stub's run lost the driver's pid, so `quiesce` never saw its session. It now uses `RP._run`.

**Behaviour that changed.**
- Round 4's synthetic explicit lookup on the untuned list after the tune now STOPs (`search-phase`, K9).
- The drain takes one more poll before it is quiet (K7).
- Inflated bytes are counted before the int32-object check, so a control found as int32-object still shows its
  inflated bytes (K6).

**Mutants.**
- Eleven earlier mutants whose code this round rewrote were retargeted onto the new lines.
- Added this round: 24 in A2, 16 in install and 1 in probe.
- Every anchor was re-counted against the final bytes: 0 off.
- Install's first run left one survivor, M102 (a decode without its hits, in the launcher). A launcher test for it
  was added: t0's `input-flux.root` decoded without `hits`. Install's mutants were then all run again.

**Not testable on this host.** These are recorded in the rehearsal checklist.
- An interruption between the temporary write and the rename.
- `quiesce`'s /proc path on Linux. The tests use the ps fallback and injected scans.
- Whether a real coverage GHEP holds its run number in decoded bytes. If it does not, B3 STOPs at the control. This
  is a fail-closed check, not a pass.

**Receipts on the final bytes.**
- **Suites** (`tune-support/tests-local.log`): 333 passed, 2 skipped. The suites are test_covfix_pg, test_pg_verify
  and test_fd_f1.
- **Probe tests** (`probe/tests-local.log`): 63 run, OK, 1 skipped.
- **Install tests** (`install/tests-local.log`): 29 run, OK.
- **Mutants** (each set's `mutants.log`):
  - probe: 108 of 108 killed;
  - install: 106 of 106 killed;
  - A2: 340 of 340 killed.

  None were invalid. No code, test or mutant file changed after the A2 and probe runs began. Install's test file
  changed once (M102), and install's mutants were run again after it.
- **An unexplained run.** One earlier run of the suites reported "8 failed, 325 passed". Only its summary line was
  kept, so the failing tests are not known, and the cause is not established. None of this lane's own runs
  overlapped it. Another session's tests were running on this host at some point that day, at times not known. The
  suites read none of the docs edited during that run. Every later run passed in full: one under the 8-way mutant
  load, one alone, and the final one above. One A2 orphan test also failed once, then passed in each of six
  concurrent reruns.
