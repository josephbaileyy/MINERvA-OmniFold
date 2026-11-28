# Round 6 confirm read: codex-school on 8f6cab162..2a2bac64a, with proposed dispositions

## The read

- Reader: codex-school, gpt-6.2-sol, reasoning effort high, read-only sandbox, 225,629 tokens.
- Input: `files/`, hashed in `files.sha256`. It held:
  - the fix diff (code, tests, mutants and receipts);
  - round 5's confirm DISPOSITIONS, with its Outcome section;
  - the eight code files at 2a2bac64a;
  - GENIE R-3_04_00's AlgConfigPool.cxx, XmlParserUtils.cxx, RunOpt.cxx and Messenger.cxx.
- The 14 copies were unchanged after the read, and no file was added.
- Prompt: `prompt.txt`. Report: `codex-school-report.txt`, verbatim.
- Verdict: NO-GO, with 2 blockers, 7 major and 2 minor.

## The rule and how findings were checked

**The rule (the director).** A finding is blocking if it causes a false STOP of a correct run, or if it is a gate that
can miss something correct producers really emit.

**How each finding was checked.** Each finding was checked against the code at 2a2bac64a. Two sources were also
fetched to settle producer facts:
- GENIE R-3_04_00's `NtpWriter.cxx` (sha256 8293841d…);
- ROOT v6-28-00's `RZip.cxx`.

## Per-fix verdicts (codex)

- **Closed:** K2, K4, K11, F4, F13, F17 and F18.
- **Partly closed:** K1, K3, K6, K7, K8, K9, K12 and F12. The parts left open are the findings below.
- **K1 and the order of calls:** codex confirms that GENIE's real sequence passes: Messenger's basename walk, then
  its explicit walk, then AlgConfigPool's tuned walks, which re-probe the path they choose. Its confidence is high
  for the order the producer follows, and conditional for whether the deployed lists match, because the bundle had
  no `search_dirs` receipt.

## Blocking: each can STOP a correct run

| # | finding | verified | defect | proposed fix |
|---|---|---|---|---|
| R1 | 3 (part) | verified (code: pg_lib.py:525–543; GENIE NtpWriter.cxx:83–125) | **B3's control can STOP a correct run, depending on key order.** GENIE's `NtpWriter::Initialize` writes `NtpMCTreeHeader` (`runnu`, `runseed`: the public seed) first, at :117. Only then come the configuration and environment keys, and after them the event baskets. ROOT compresses only objects of more than 256 bytes, and the header's size is close to that. If the header is stored verbatim, the scan finds the seed there (`int32-object`) and breaks before any key has been inflated. That leaves `bytes_inflated == 0`, and both validators STOP. Our GHEP fixture put the run number in TTree bytes, so it never tested this. | Under `decode_all`, finish every key: no break. Then `bytes_inflated` and the hit kinds cover the whole file. Also record, for each seed hit, its object's class and whether it was inflated. The fixture's run number moves into a header key written before the tree, in both the stored and the compressed form. The object-local witness codex asks for (the seed found in an inflated object) is not required: if GENIE's header is stored verbatim, that would STOP every correct B3. B3 records which case occurs, and you decide then whether a compressed witness is needed. <!-- absence-ok: a statement about this lane's own test fixture, not about a result --> |
| R2 | 2 | verified (code: pg-replay-g2111a.py:252, new; pg_verify.py:1330, round 5, the same defect, not cited) | **A non-UTF-8 command name STOPs the run.** Both scanners read `/proc/PID/stat` as text, and Linux writes the command name as raw bytes. Text mode decodes them as UTF-8 or ASCII, so a byte sequence that is not valid there raises `UnicodeDecodeError`. That is a ValueError: a STOP in the runner, and an exception the drain's scan does not catch (it catches OSError and IndexError). Any visible process can trigger it, so this is unlikely on an exclusive compute node, but not impossible. | Read the file in binary mode and take the state after the last `b")"`, in both scanners. Add a test that feeds a non-UTF-8 name. |
| R3 | 1 | verified (code: pg_lib.py:321 against :421) | **A freed TBasket loses its class.** For a basket, ROOT's `fKeylen` includes the basket's own header fields. The live-key reader allows for this (`o - pos <= keylen`), but `_freed_record` requires equality. So a freed basket falls through to the header search and becomes `(free)`, where the 4-byte int32 rule applies. A chance match then STOPs: its probability is about the payload's bytes times the number of int32 patterns, divided by 2³². Whether correct producers ever leave a freed basket is not established: AutoSave frees TTree keys, not baskets. | For class `TBasket`, accept `keylen >=` the end of the strings and read the payload from the record's start plus `keylen`, as live keys do. Add a fixture with ROOT's basket header layout. |
| R4 | 5 | verified (code: pg_lib.py:242–274, :355; ROOT RZip.cxx:251–274) | **A false header STOPs the run when a codec module is missing.** In bytes that no freed record covers, any `ZS` or `L4` candidate with sizes in range raises `root-codec-unavailable` if `zstandard`, or `lz4` and `xxhash`, are missing. ROOT itself checks the method byte: ZL is 8, XZ is 0 and ZS is 1. L4 has no method check. | A candidate counts as a header only if its method byte is ROOT's for that tag. For L4, which ROOT does not check, a missing module stays a STOP. The rehearsal checklist gains a row: confirm on the node that `zstandard`, `lz4` and `xxhash` import. With them present, R4 cannot occur. |

## Not blocking

None of these can STOP a correct run. Each either misses a sequence a correct producer does not emit, or is a
residual that a follow-up already covers.

| finding | disposition | reason |
|---|---|---|
| 4 (major) | **hardening; with R3, or a follow-up** | Verified (code: pg_lib.py:341–343). After a whole freed record, the search skips 4 bytes even when no freed record follows. In ROOT's layout, every record or gap in a free gap starts with its own 4-byte length, so no block header can begin there. If the next record does not parse, search from the record's end. |
| 6 (major) | **follow-up** | Verified (code: pg_verify.py:725–751). Explicit and basename probes are split without regard to trace order, and the explicit walk's phase is applied first. So a reversed or interleaved order can pass. GENIE's real order passes (codex), so this only misses a wrong producer. Proposed: consume the walks in trace order. |
| 7 (major) | **follow-up** | A tuned walk that ends in no read never binds the pid. This only misses a wrong producer: GENIE reads every file it finds. Proposed: let walks that end without a read bind too. |
| 8 (major) | **follow-up** | Verified (code). Quiet can be accepted up to one poll past 30 s, but it still needs two consecutive empty scans, so this is a looser deadline, not a correctness gap. A process that forks and exits between enumeration and inspection on two polls in a row would be missed: that is the residual of any snapshot scan, and C10 (containment at execution) covers it. After a STOP, the runner still sweeps W1's public-seed files. The run has already STOPped, and those files hold only the public seed. |
| 9 (major) | **follow-up (C10)** | Seed-bearing bytes could leave W by a write through a symlink that is unlinked before verification. A link made during the run is already a STOP (B10), and correct producers make none. What remains is a link that already existed in W, which is C10's enforcement at execution. Checklist: confirm that W's staged inputs contain no symlinks. |
| 10 (minor) | **hardening; with R1 (pg_replay.sh changes anyway)** | `ls` failing for any reason reads as "no GHEP". W1 is the replay's own directory, so a listing error there would break the steps before it. Proposed: glob with `nullglob`, after `[ -d "$W1" ]`. |
| 11 (minor) | **follow-up** | Nested subscripts escape F12's pattern. The wrapper's bytes are fixed by its sha (5c3fd520…), so no other wrapper can reach the check. |

## If R1–R4 are built

- Code changes:
  - pg_lib.py (R1, R3, R4, and 4);
  - pg_verify.py (R2);
  - pg-replay-g2111a.py (R2);
  - pg_replay.sh (R1's records, and 10);
  - pg-replay-g2111a.py and pg-node-launch.py (R1, if the validators read the per-hit record).
- Tests are written first, then all suites and every mutant run, with the anchors re-counted.
- run_gevgen_v3.sh is unchanged.

## Outcome (round 7, the director's ruling of 2026-11-26)

**Ruling.**
- R1–R4 are blocking, each a false STOP of a correct run. They are built as proposed.
- Codex 10 is built with R1, since pg_replay.sh changes anyway.
- Codex 4, 6, 7, 8, 9 and 11 go to `../../FOLLOWUPS.md`.
- No object-local witness rule: B3's `seed_objects` record shows whether GENIE's header is stored or compressed, and
  the director decides after that.
- After this round there are no more codex rounds on this package.

**Red check.** The final tests were run against 9222fa494's code (put in place from `git show`, then restored and
checked by sha). Every new test failed:
- covfix and verify: 10 failed. The 22 that passed are inherited round-5 and round-6 tests, plus
  `test_a_live_real_basket`, a guard: the live-key reader already handled a real basket.
- install: 3 failed (the node and launcher payload tables, and `session_pids` on a non-UTF-8 name).

The end-to-end `test_the_replay` failed with `bytes_inflated` 0, which reproduces R1 in the driver itself.

**As built.**
- **R1, `pg_lib.leak_scan`:**
  - With `decode_all`, every key is read.
  - `stats["seed_objects"]` lists each ROOT object the seed was found in, as `{class, inflated, kind}`.
  - In production the first hit still breaks.
- **R1, in the driver and the validators:**
  - `pg_replay.sh` records `seed_objects`.
  - Both validators type-check it (class a string, inflated a bool, kind `int32-object` or `inflated`), and the
    control needs at least one.
- **R2:** both scanners read `/proc/PID/stat` as bytes and take the state after the last `b")"`. `session_pids`
  gains a `proc` argument for the test, as `survivor_scan` already had.
- **R3:** a freed `TBasket` may have `fKeylen` longer than its strings. Its payload starts at the record's start
  plus `fKeylen`.
- **R4:** a gap candidate counts as a header only with ROOT's method byte: `METHOD = {ZL: 8, XZ: 0, ZS: 1}`, with
  none for L4. The checklist gains the imports, under both interpreters that run the scan.
- **Codex 10:** the driver runs `ls -A "$W1" || STOP` before `compgen -G "$W1/gntp.*.ghep.root" && STOP`.

**Fixture realism.**
- The GHEP fixture now follows GENIE's NtpWriter: the file's key, then `genie::NtpMCTreeHeader` (the seed as
  Long_t, twice), then the configuration and environment folders, a basket and the tree. It comes in two forms,
  with the header stored and with it compressed. The driver's round-trip test runs both.
- `_basket` writes ROOT's 19 bytes of basket fields inside `fKeylen`. The gst template's basket uses it.
- An object of a few tens of bytes grows under zlib, and the reader (like ROOT) then takes it as stored. The header
  fixture carries GENIE's directory strings, so it really compresses.

**Behaviour that changed.**
- A compressed header holding the int64 seed is listed twice in `seed_objects`, once as `int32-object` and once as
  `inflated`: the int64 is one of the STOP forms too.
- A stored header's int64 seed is also a raw `bytes` hit. That is the production STOP, as before.

**Receipts.** Every suite run writes its full log (the director's rule of round 7): `../../tune-support/tests-local.log`,
`../../probe/tests-local.log` and `../../install/tests-local.log`, beside each set's `mutants.log`.
- Suites (`test_covfix_pg.py`, `test_pg_verify.py`, `test_fd_f1.py`): 363 passed, 2 skipped (the final run, after the M343/M344 test fix).
- Probe tests: 63 run, OK (1 skipped). Install tests: 34 run, OK.
- Mutants, with all 577 anchors re-counted against their expected match counts (0 off):
  - probe: 108 of 108 killed; 0 invalid; 0 survived;
  - install: 117 of 117 killed; 0 invalid; 0 survived;
  - A2 (tune-support): 352 of 352 killed; 0 invalid; 0 survived (the final run). The run before the test fix gave 350 killed and 2 invalid (M343, M344), as below.

**Fixed during the receipts runs.**
- The end-to-end temp listing lacked `tpl-z.ghep.root`, so the A2 baseline was not clean. The listing was fixed.
- Install M79 and M85 (the node's and the launcher's "name and bytes not apart" case) survived at first. The test
  record carried no valid `seed_objects`, so a different check fired first and masked the one each mutant removes.
  Both cases now carry a valid seed object, and both mutants are killed.
- A2 M343 and M344 (R4) came back INVALID, not killed. Under each mutant the code raises the
  `root-codec-unavailable` STOP, which is a kill. But the test mocks `zstandard` missing, Python chained that
  `ModuleNotFoundError` into the traceback, and the runner's rule reads a line starting `ModuleNotFoundError` as a
  collection error. The test now reports a STOP there as a plain FAIL, raised outside the exception handler, so
  nothing is chained. Reproduced in a scratch copy: both mutants FAIL with no import line, and the unmutated test
  passes. The suites and all A2 mutants were then run again.
