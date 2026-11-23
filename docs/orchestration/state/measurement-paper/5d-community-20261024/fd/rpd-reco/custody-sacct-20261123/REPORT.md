# RPD-RECO: custody's COV2D fence reads sacct only (2026-11-23)

**Director-ordered** (2026-11-23, after the flux2 records PR #1248). Authored by the limitation-resolver lane. This is
code only and nothing runs on the cluster. P0 READY will bind these shas in a separate binding written after this
merges.

## Why

Joseph's standing rule is "sacct, never squeue". Binding 2's custody prepare broke it: its COV2D fence ran
`squeue -u josephrb -h -o %i|%j|%T|%M|%l` (`fd_rpd_reco_custody.py:408` at 763ab4dd, sha256 `867822e3…`) before a
`sacct -j` read of two named jobs. That squeue ran read-only inside flux1 (job 61206960) and flux2 (job 61806073), and
both runs record it in `run/cov2d-fence.json`. No result rests on it, because the sacct read also ran. The director
ordered it removed before P0.

## The change

`cov2d_fence()` now makes one call, with stdout and stderr together:

```
sacct -X -n -P -u josephrb -S 2026-11-01T00:00:00 -E now -o JobIDRaw,JobName,State
```

It is fail-closed in the pattern of `cov2d_fence.sh` rev 2 (3fbc9cbd, merged 7d5a98361). It refuses (CustodyRefused,
exit_code 3) when:
- sacct exits non-zero;
- any non-empty line is not a 3-field row with a JobID matching `^[0-9]+([_+].*)?$`. This catches an error that sacct
  prints on stderr while exiting 0, a header, a truncated or extra-field row, and a step id;
- a cov2d* or t2a* row has a State whose first word is not in rev 2's closed terminal set (BOOT_FAIL, CANCELLED,
  COMPLETED, DEADLINE, FAILED, NODE_FAIL, OUT_OF_MEMORY, PREEMPTED, TIMEOUT). REVOKED, an empty State and any state
  not named refuse;
- either named job, 60909280 or 60911676 (cov2d-AR23_Tb and cov2d-AR23_Tc, submitted 2026-11-06), is missing or not
  terminal.

The fixed start, 2026-11-01, holds both named jobs. If accounting ever purged them, the named-job check would refuse.

**Against the old fence:**
- Stricter: t2a* is fenced as well as cov2d* (the old prefix was `cov2d-`), stderr and malformed lines refuse, and
  REVOKED is no longer terminal.
- Weaker, which the rule forces: squeue's live view saw any queued or running cov2d- job, and sacct cannot see a job
  it omits. The docstring names those jobs: a family job still running since before the start, one pending since before
  it, a held job with no EligibleTime, and one slurmdbd has not yet recorded. cov2d's fresh ack at the connect covers
  them, as it does for rev 2.

**The record** that prepare writes (`cov2d-fence.json`, or `cov2d-fence.STOP.json`) carries:
- `sacct_command`, `sacct_exit_code` and `sacct_output` (merged);
- `status` and `exit_code`;
- on PASS, `rows`, `cov2d_t2a_rows` and `terminal_states`;
- on STOP, `message`, with the offending line.

The `queue_*` keys are gone, along with `sacct_stdout` and `sacct_stderr`. The reads found no reader of any of them.

**Grep of the other modules P0 to d2 runs** (fd_rpd_reco.py, fd_rpd_inputs.py, fd_rpd_reco_prologue.py, fd_rpd.py,
fd_rpd_reco_flux_connect.sh, fd_rpd_reco_prologue_connect.sh, and RPL's rpl_scale_fit.py): there are no squeue,
sacct, scontrol or sbatch calls and no `-s` state filter. In custody, the `-s` at the strace call is strace's string
size. The squeue calls in the closed prologue campaigns' scripts (prologue-20261107 to prologue5-20261108,
pymon-fetch) are historical records, which P0 to d2 do not run. P0's own connect scripts are not yet written, and they
will be sacct-only from the start.

## Tests

In `nd-unfolding/tests/test_fd_rpd_reco.py`:
- **`_fence_run`** stubs `subprocess.run`. Any command but `sacct` fails the test, and every call is recorded.
- **`test_cov2d_fence_both_directions`** (the harness's REQUIRED_COV2D_FENCE selector) checks a PASS listing with
  "CANCELLED by N", TIMEOUT, an array id, a het id, an unrelated running job and a blank line. It requires exactly one
  call, the exact argv, and stderr merged into stdout. Then three refusals: a named job running, one missing, and
  sacct failing.
- **`test_cov2d_fence_refuses`** has 14 cases, each a STOP with exit_code 3, the matching message, and the output kept.
  They are: sacct fails; a stderr error with rc 0; 2-field and 4-field rows; a non-numeric JobID; a JobID with a digit
  but not numeric; a step id; a whitespace line; cov2d RUNNING; t2a PENDING; cov2d COMPLETING; t2a REVOKED; a family
  row with an empty State; and a named job RUNNING under another name.
- **`test_cov2d_fence_never_invokes_squeue`** is the static half: no string literal in the module is exactly
  "squeue". `_fence_run` is the invocation half.

## Receipts

| run | result | file |
|---|---|---|
| the full suite | **315 passed** (binding 2's 300, + 15) | `SUITE.txt` |
| the fence mutants (`tests/fd_rpd_reco_fence_mutation.py`, new) | **18 of 18 killed**; the unmodified copy passes first | `FENCE-MUTATIONS.txt`, `FENCE-MUTATIONS.json` |
| binding 2's harness (`tests/fd_rpd_reco_mutation.py`, unchanged) | **236 required, 236 executed, 236 killed; complete and all_killed true** | `MUTATIONS.txt`, `MUTATIONS.json` |
| black 26.10.1 / ruff 0.17.4 | clean on the three changed files | `STATIC-CHECKS.txt` |

The fence mutants are:
- stderr not merged, rc ignored;
- the user, `-S` or `-E` dropped;
- the blank-line skip broadened;
- the field count and JobID unchecked, or the JobID unanchored;
- the whole State compared instead of its first word;
- t2a dropped, or the family check skipped;
- PENDING or REVOKED added to the set, or TIMEOUT dropped from it;
- the named-job presence or terminal check skipped;
- squeue restored.

`MUTATIONS.json` is the harness's raw report (sha256 `6cea104b452915d5408447c6fd5dd2a005023f83f8638ce19ee339558fc3f087`,
recorded in its `receipt_annotation`) with #1069's two annotations added, as in stage-time-20261111.
`disposable_fixture_artifact_paths` lists the synthetic fixture names that the harness's test output prints. They are the
same 36 as stage-time's.

Each fence mutant runs the fence tests on a temporary copy, loaded through `FD_RPD_CUSTODY_MODULE`. Binding 2's
harness keeps its REQUIRED_COV2D_FENCE mutant, which replaces the fence's body with a PASS, and it is killed. All runs
were serial with the five thread caps at 1. `SOURCE-SHA256SUMS` holds the six files' sha256, equal before and after the
runs:
- `fd_rpd_reco_custody.py` `6af4cd792de98fa5a43120c038fa904c80ced0cb16403f4e2410f84ae41343f5`, was `867822e3…`;
- `tests/test_fd_rpd_reco.py` `bd7bd0388117b3a102f419d902ada4cad965296174721209f1eaba773f6d32f0`, was `671e1cdc…`;
- `tests/fd_rpd_reco_fence_mutation.py` `82f1f623391be19f48fc80728ef7c01d8650e2c43d7cb44cfe88528f294a4f3f`, new;
- unchanged: `fd_rpd_reco.py` `7302cc1d…`, `fd_rpd_inputs.py` `6e4ed0f1…` and `tests/fd_rpd_reco_mutation.py`
  `f2612369…`.

## Reads

The reports are under `~/codex-reports/note-measurement/reads/`:

| read | report | sha256 | verdict |
|---|---|---|---|
| Grok, the diff | `custody-sacct-20261123/grok/out.txt` | `5ebd5a104ce3801003d95271454611017f31eafd77819d7b5858d89233029d57` | GO |
| agy, the diff | `custody-sacct-20261123/agy/out.txt` | `5c74529fabdf3cc13aeb023f671f3f390fa8b1bb6b75c0a1f1e440512b4c1976` | GO |
| agy confirm of the fixes | `custody-sacct-delta1/out.txt` | `b198fe5e3e0ebc0d4d7348ec1c748dfdb861a51f00a27a608d31a90563b13e82` | GO |

Their non-blocking suggestions became fixes, all text-only, and the confirm checked them:
- Grok 1: the docstring's known-gap sentence now names a family job still running from before `-S`;
- Grok 2: the static test's docstring says what it proves and names `_fence_run` as the invocation check;
- agy 3: the start constant's comment notes that a purge fails closed.

The receipts above are at the bytes after those fixes.

Nothing is submitted, deposited or tagged.
