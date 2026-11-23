# RPD-RECO: custody's COV2D fence reads sacct only (2026-11-23)

**Director-ordered** (2026-11-23, after the flux2 records PR #1248). Authored by the limitation-resolver lane. This is
code, plus one director-approved login-only sacct probe. P0 READY will bind these shas in a separate binding written
after this merges.

**The NERSC cert expires at 2026-11-23T22:00:33Z.** P0 needs Joseph's renewal if it runs after that.

## Why

Joseph's standing rule is "sacct, never squeue". Binding 2's custody prepare broke it: its COV2D fence ran
`squeue -u josephrb -h -o %i|%j|%T|%M|%l` (`fd_rpd_reco_custody.py:408` at 763ab4dd, sha256 `867822e3…`) before a
`sacct -j` read of two named jobs. That squeue ran read-only inside flux1 (job 61206960) and flux2 (job 61806073), and
both runs record it in `run/cov2d-fence.json`. No result rests on it, because the sacct read also ran. The director
ordered it removed before P0.

## The change

`cov2d_fence()` now makes two sacct reads, each with stdout and stderr together. Each has an explicit window that never
grows, because Perlmutter's sacct refuses a window that is too wide ("Too wide of a date range in query": a 60-day `-S`
was refused for tier3-design on 2026-11-23, and a 14-day one was accepted).

```
sacct -X -n -P -j 60909280,60911676 -S 2026-11-05T00:00:00 -E 2026-11-08T00:00:00 -o JobIDRaw,JobName,State
sacct -X -n -P -u josephrb -S <now - 14 days, local> -E now -o JobIDRaw,JobName,State
```

It is fail-closed in the pattern of `cov2d_fence.sh` rev 2 (3fbc9cbd, merged 7d5a98361). It refuses (CustodyRefused,
exit_code 3) when:
- either read exits non-zero;
- either read cannot be launched or decoded (OSError, UnicodeDecodeError). The STOP keeps every read's command and
  whatever output was already captured;
- any non-empty line of either read is not a 3-field row with a JobID matching `^[0-9]+([_+].*)?$` and a non-empty,
  unpadded JobName. This catches an error that sacct prints on stderr while exiting 0, a header, a truncated or
  extra-field row, a step id, and a padded or missing name;
- the named read is not exactly the two named jobs, 60909280 and 60911676 (cov2d-AR23_Tb and cov2d-AR23_Tc, run on
  2026-11-06), with both terminal. A missing, extra or repeated row, or another job in place of one, refuses;
- a cov2d* or t2a* row in the family read (matched case-insensitively) has a State whose first word is not in rev 2's closed terminal set
  (BOOT_FAIL, CANCELLED, COMPLETED, DEADLINE, FAILED, NODE_FAIL, OUT_OF_MEMORY, PREEMPTED, TIMEOUT). REVOKED, an empty
  State and any state not named refuse.

The named window is fixed and closed. If accounting ever purged the named jobs, that read would refuse. The family
start comes from `cov2d_family_start()`: now minus `COV2D_FAMILY_DAYS` (14) days, in local time, the zone sacct reads
`-S` in.

**Against the old fence:**
- Stricter: t2a* is fenced as well as cov2d* (the old prefix was `cov2d-`), stderr and malformed lines refuse, the named
  read must be exact, and REVOKED is no longer terminal.
- Weaker, which the rule forces: squeue's live view saw any queued or running cov2d- job, and sacct cannot see a job
  it omits. The docstring names those jobs: a family job still running since before the window, one pending since before
  it, a held job with no EligibleTime, and one slurmdbd has not yet recorded. cov2d's fresh ack at the connect covers
  them, as it does for rev 2.

**The disposition of that gap** (the director's ruling on codex-school2's blocking finding 1, 2026-11-23): "a held job
with no EligibleTime, or slurmdbd lag, can be omitted by sacct. Under the standing ban on squeue that gap is closed by
protocol, through cov2d's fresh connect-time ack, not by this code." Custody `prepare` stays sacct-only. P0's launcher,
written with the P0 READY package, enforces the protocol in code:
- it requires an `ack.txt` holding cov2d's ack verbatim, with a first line `ACK-UTC <ISO time>`;
- it refuses if the file is missing or malformed, or if the ack is more than 6 h before launch;
- it copies the file into the run records.

**The record** that prepare writes (`cov2d-fence.json`, or `cov2d-fence.STOP.json`) carries:
- `sacct_named` and `sacct_family`, each with `command`, `exit_code` and `output` (merged), or `error` if the read
  could not run;
- `status` and `exit_code`;
- on PASS, `family_rows`, `cov2d_t2a_rows` and `terminal_states`;
- on STOP, `message`, which names the read and the offending line.

The old `queue_*`, `sacct_stdout` and `sacct_stderr` keys are gone. The reads found no reader of any of them.

**Grep of the other modules P0 to d2 runs** (fd_rpd_reco.py, fd_rpd_inputs.py, fd_rpd_reco_prologue.py, fd_rpd.py,
fd_rpd_reco_flux_connect.sh, fd_rpd_reco_prologue_connect.sh, and RPL's rpl_scale_fit.py): there are no squeue,
sacct, scontrol or sbatch calls and no `-s` state filter. In custody, the `-s` at the strace call is strace's string
size. The squeue calls in the closed prologue campaigns' scripts (prologue-20261107 to prologue5-20261108,
pymon-fetch) are historical records, which P0 to d2 do not run. P0's own connect scripts are not yet written, and they
will be sacct-only from the start.

## The real-sacct probe: [`probe/`](probe/)

The director's rule as of 2026-11-23: a new or changed sacct query runs once for real, read-only, before it is
embedded.

- [`probe/gen_probe.py`](probe/gen_probe.py) (`d9a09f46…`) loads custody, stubs `subprocess.run` to capture the two
  commands `cov2d_fence()` builds, and writes [`probe/custody_sacct_probe.sh`](probe/custody_sacct_probe.sh)
  (`d2f49b8d…`) from them, byte for byte. The one value computed on the node is the family `-S`, with the same
  arithmetic.
- The probe prints each read's rc and output and exits 0 only if both exit 0.
- [`probe/probe_launch.sh`](probe/probe_launch.sh) (`214367c6…`) is the approved `e1_survey_launch.sh` (24dddd72) with
  only the remote script's name and the header changed.
- The director gave GO after reading all three.

**The run** ([`probe/run-20261123/`](probe/run-20261123/)): login30, 2026-11-23T05:45:40Z, launcher rc 0, ssh rc 0.
The launcher's stdout is `launcher.out.txt`, and the session log is `survey.log.txt` (sha256 `0f99cd04…`; the repo
ignores `*.log`; the bytes are the same).

- The named read: rc 0, exactly `60909280|cov2d-AR23_Tb|COMPLETED` and `60911676|cov2d-AR23_Tc|COMPLETED`.
- The family read (`-S 2026-11-08T21:45:40`): rc 0, 76 rows (59 COMPLETED, 16 FAILED, 1 TIMEOUT), with no error text
  and no malformed line. The cov2d* rows are 14 cov2dg2r-* jobs, all COMPLETED, and there are no t2a* rows.
- Custody's own parser, fed the two outputs through the test stub, gives PASS, exit_code 0, both named jobs
  COMPLETED, family_rows 76 and cov2d_t2a_rows 14. That holds at the probe's source bytes (`6f529d89…`) and at this
  PR's final bytes (`634670b3…`).
- The later round-2 fixes changed parsing and error handling, not either command. Regenerating the probe from the final
  custody changes only the comment line that names the source sha. The two commands are byte-identical, so the probe
  stands.

The director accepted the result as settling the windows for P0.

## Tests

In `nd-unfolding/tests/test_fd_rpd_reco.py`:
- **`_fence_run`** stubs `subprocess.run`. Any command but `sacct` fails the test. The read with `-j` gets the named
  output and the other read gets the family output, and every call is recorded.
- **`test_cov2d_fence_both_directions`** (the harness's REQUIRED_COV2D_FENCE selector) checks a PASS listing with
  "CANCELLED by N", TIMEOUT, an array id, a het id, an unrelated running job and a blank line. It requires:
  - exactly two calls, with the exact argv of each;
  - stderr merged into stdout in both;
  - the family start 14 days before a fixed clock.

  Then three named-read refusals: a named job running, one missing, and sacct failing.
- **`test_cov2d_fence_refuses`** has 22 cases, each a STOP with exit_code 3 and the matching message:
  - either read failing;
  - a stderr "Too wide" line with rc 0;
  - 2-field and 4-field rows, a non-numeric JobID, a JobID with a digit but not numeric, a step id, a whitespace line,
    and a malformed named read;
  - cov2d RUNNING, t2a PENDING, cov2d COMPLETING, t2a REVOKED, and a family row with an empty State;
  - a padded job name, an empty job name, and an uppercase family name (COV2D-UPPER RUNNING);
  - a named job RUNNING, a named job repeated, an extra job in the named read, and another job in place of a named one.
- **`test_cov2d_fence_launch_error_keeps_the_first_read`**: an OSError, and then a UnicodeDecodeError, on the family
  read each give a STOP that keeps the named read's output and the family read's command and error.
- **`test_cov2d_fence_module_has_no_squeue_literal`** is the static half: no string literal in the module has a word
  equal to "squeue" or ending in "/squeue". `_fence_run` is the invocation half.

## Receipts

| run | result | file |
|---|---|---|
| the full suite | **324 passed** (binding 2's 300, + 24) | `SUITE.txt` |
| the fence mutants (`tests/fd_rpd_reco_fence_mutation.py`, new) | **24 of 24 killed**, each by a named fence test; the unmodified copy passes first | `FENCE-MUTATIONS.txt`, `FENCE-MUTATIONS.json` |
| binding 2's harness (`tests/fd_rpd_reco_mutation.py`, unchanged) | **236 required, 236 executed, 236 killed; complete and all_killed true** | `MUTATIONS.txt`, `MUTATIONS.json` |
| black 26.10.1 / ruff 0.17.4 | clean on the three changed files | `STATIC-CHECKS.txt` |

The fence mutants are:
- stderr not merged, rc ignored;
- the user dropped, the named window dropped, or the family start or end dropped;
- the family window widened to 60 days;
- the blank-line skip broadened;
- the field count and JobID unchecked, or the JobID unanchored;
- the whole State compared instead of its first word;
- t2a dropped, or the family check skipped;
- PENDING or REVOKED added to the set, or TIMEOUT dropped from it;
- the named count, presence or terminal check skipped;
- the name check skipped, or the family match made case-sensitive;
- launch errors left uncaught;
- squeue restored.

Each fence mutant runs the fence tests on a temporary copy, loaded through `FD_RPD_CUSTODY_MODULE`. Only pytest exit 1
counts as KILLED. Any other non-zero exit is ERROR and fails the run, and the failing test's name is recorded for each
mutant. Binding 2's harness
keeps its REQUIRED_COV2D_FENCE mutant, which replaces the fence's body with a PASS, and it is killed.

`MUTATIONS.json` is the harness's raw report (sha256 `06acee946ebf1fb844718b2269116819c38afa2067bc8ee4e2dc8108914440d2`,
recorded in its `receipt_annotation`) with #1069's two annotations added, as in stage-time-20261111.
`disposable_fixture_artifact_paths` lists the synthetic fixture names that the harness's test output prints. They are the
same 36 as stage-time's.

All runs were serial with the five thread caps at 1. `SOURCE-SHA256SUMS` holds the six files' sha256, equal before and
after the runs:
- `fd_rpd_reco_custody.py` `634670b33af6900eb9feb2c01748b0f107950e110382780db37b874ab77160d8`, was `867822e3…`;
- `tests/test_fd_rpd_reco.py` `e1b92ef0927e285534f131b73376563f207340556ead7f4e60310b356ac395ba`, was `671e1cdc…`;
- `tests/fd_rpd_reco_fence_mutation.py` `138bc5b4340307788b694692ad971ea3b861260eb29b328b264efe680f6b1ff2`, new;
- unchanged: `fd_rpd_reco.py` `7302cc1d…`, `fd_rpd_inputs.py` `6e4ed0f1…` and `tests/fd_rpd_reco_mutation.py`
  `f2612369…`.

## Reads

The reports are under `~/codex-reports/note-measurement/reads/`.

Round 1 read the single-read version:

| read | report | sha256 | verdict |
|---|---|---|---|
| Grok | `custody-sacct-20261123/grok/out.txt` | `5ebd5a104ce3801003d95271454611017f31eafd77819d7b5858d89233029d57` | GO |
| agy | `custody-sacct-20261123/agy/out.txt` | `5c74529fabdf3cc13aeb023f671f3f390fa8b1bb6b75c0a1f1e440512b4c1976` | GO |
| agy confirm of the text fixes | `custody-sacct-delta1/out.txt` | `b198fe5e3e0ebc0d4d7348ec1c748dfdb861a51f00a27a608d31a90563b13e82` | GO |

Their suggestions became text fixes, which are carried into round 2:
- Grok 1: the docstring's known gaps;
- Grok 2: the static test's docstring;
- agy 3: a purge fails closed.

Round 2 read the whole diff against main after the two-read redesign. Grok's account was out of credit (HTTP 402), so
codex-school2 read in its place:

| read | report | sha256 | verdict |
|---|---|---|---|
| agy, the two-read diff | `custody-sacct-r2/agy/out.txt` | `bc8034fb6bd81216449d186277b346feda8fb0145666a3780d9d1f494a84a771` | GO |
| codex-school2, the two-read diff | `custody-sacct-r2/codex2/out.txt` | `3172944f0ead40c50fd50a3a44f50a6ccdaaf130d6d66663de3938847a600ec3` | FIX |
| codex-school2 confirm of its fixes | `custody-sacct-delta2/codex2/out.txt` | `117f9061137e7a3dab717b8cf7b94be5c935ef568209c86994a6b998d5e2f520` | GO |
| agy confirm of the last test-only delta | `custody-sacct-delta3/out.txt` | `0c4699c71dbf5206718d5dbb918c6c34006f100090ff5cfb11d15b8df1be1292` | GO |

codex-school2's findings:
- **Blocking 2** (a padded or empty JobName passed, for example `61| cov2d-active|RUNNING`): fixed. The name must be
  non-empty and unpadded, and the family match is case-insensitive.
- **Non-blocking 4** (a launch or decode error dropped the earlier read's record): fixed.
- **Non-blocking 5** (the static test's name and docstring): fixed.
- **Non-blocking 6** (the harness counted any non-zero exit as a kill): fixed. Only rc 1 is KILLED, and test names are
  recorded.
- **Blocking 1** (omitted jobs): ruled by the director as protocol, above.
- **Non-blocking 3** (14 days plus seconds): left as is, by the director's acceptance. flux2's connect read about
  14 d 15 h without refusal, and a new form would need a new probe.

agy's suggestions:
- the stale "exactly one call" docstring, already fixed;
- widening the static squeue check to path forms, done.

codex-school2's confirm added two nits, both done: the docstring names the launch-error test's own stub, and the
harness passes `--color=no`.

Nothing is submitted, deposited or tagged.
