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
