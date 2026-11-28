# RPD-RECO d2-predict and step0 (rpd_d2s0): the READY package on P0's records (2026-11-24)

**By** limitation-resolver, for the director's binding. Nothing here has run. The connect runs only on the director's
GO for its exact sha256, with cov2d's fresh ack.

**What it is.** The next two steps of the bound chain, in P0's login form:
- 0 node-h, with no job and no job-name family (FD-RPD-RECO-DECLARATION section 5; binding 1 ruling 3);
- `d2-predict`, the pre-data MC prediction, then `step0`, the MC-only axes and strata.

**What `d2-predict` measures for the c0 price, and what it does not.** It runs `aggregate` over all MC signal and
background rows, with 200 Poisson replicas and 5 weight variants, under the bound CLI, with real staging and NPZ
decompression. But it passes `bins=None` (`fd_rpd_reco.py:3108-3110`), so `axis_assignments` returns only the `step`
axis (`:2321-2322`). c0's actual pass uses step0's bins: all 23 axes (`:2756-2761`, `:2323-2350`).

So `d2-predict` measures real I/O, decompression and the Poisson draws at the real row count, with a 1-axis × 5-variant
bincount. It is **not** c0's full actual-pass workload, and its wall time divided by the 23-axis timing record is not
an overhead factor for c0. codex-school2's read found this. The director was told, and the c0 pricing basis is being
revised separately; the recommendation is a short MC-only harness timing `aggregate` with step0's bins after this
chain. Nothing in this package depends on that choice.

## The director's acceptance (2026-11-24) and how the package meets it

- **A new root,** `/pscratch/sd/j/josephrb/rpd-reco-d2s0-20261124`. The connect refuses if it exists.
- **P0's records as predecessors.**
  - The connect reads P0's `run/pins.json` (`52fc41f4…`) and `run/p0.json` (`8ed2faf7…`) in place, with O_NOATIME,
    and checks them against the committed P0 records. `p0.json` is committed; `pins.json` is checked through
    `pins.json.gz`, #1274.
  - Then `tools/d2s0_checks.py stage` copies each byte for byte into the new `run/`: an O_NOATIME read, the sha256
    checked, the destination created exclusively at mode 0600, then re-read and checked.
  - So the bound CLI's `require_predecessors` sees the pins → p0 chain (`fd_rpd_reco.py:2668-2691`): code `7302cc1d`,
    config `3b2afde4`, `dry_run` false, and each `predecessor_sha256`.
- **The config is unchanged:** P0's `3b2afde4`. `require_predecessors` compares it.
- **P0's supervisor, runner and fetch are carried over.**
  - `tools/p0_supervise.py` is byte-identical (`6ad0f68f`).
  - The runner and fetch are P0's, changed only as listed under "What changes from P0" below.
- **The iris balance** is read once in the connect output (`== 2b. iris`: `timeout 120 iris < /dev/null`). It is
  never a gate and never in a step record.

**The chain's budget (the director's check 1).** The bound code allows no dry run for these steps:
`require(not dry_run or step in {"pins", "p0"}, "DRY_RUN_SCOPE", ...)` (`fd_rpd_reco.py:3058-3062`). So each step runs
once, and each has its own 7200 s supervisor deadline, as the director allowed. This matches the CLI's own
per-invocation `check_wall_clock` against `wall_seconds` = 7200.

The predicted wall time at S × 1.5, with S = 3.879e-7 s per draw (`timing-20261106/timing.json`, `303850f7`) and the
code's measured margin of 1.5:

| step | Poisson draws (P0's `runtime_estimate`) | at S × 1.0 | at S × 1.5 | own deadline |
|---|---|---|---|---|
| `d2-predict` | 6,693,569,800 | 2,597 s | **3,895 s** | 7,200 s |
| `step0` | 0 | 0 s | **0 s** | 7,200 s |

- `step0`'s real cost is not in S. It decompresses both MC kinds as the sample iterator yields them, keeps the
  signal, and runs five weighted-quantile sorts over the selected signal rows (at most 32.8 M): four sets of deciles
  and the theta median. That should take minutes.
- `d2-predict`'s supervisor sends TERM at 7,170 s and KILL at 7,200 s. Other guards (the CLI's own wall check, RSS,
  a failed step) can stop the chain earlier.
- Each step's worker budget is 7,200 s. The startup handoff and the cleanup add a little time outside the two worker
  budgets, so the chain's wall time is about 4 h at most, on one login node, at 0 node-h.

**No measured key before the prediction is committed (the director's check 2).**
- `step0` streams `inputs.samples(data=False)` (`:2272`) and keeps signal only (`:2273-2274`).
- `samples()` yields only signal and background when `data` is false (`:772-774`). Only the data kind reads
  `"measured"` (`:825-826`).
- `d2-predict` calls `aggregate(..., data=False)` (`:3108-3110`). `aggregate` builds a data assignment only for a
  partition (`:2378-2382`), and none is passed.
- The backstop: `Inputs.key("measured")` calls `require_prediction()` (`:677-678`), which STOPs with
  `PREDICTION_COMMITTED` when no `--prediction` is given (`:689-693`). The runner never passes one.
- `c0`, the first step that opens data, will need `d2-predict.json` committed (its records PR, then the director's
  merge) and passed as `--prediction`.

## What changes from P0

[`tools/gen_d2s0.py`](tools/gen_d2s0.py) generates the connect (with the runner), fetch, launcher, fence copy and
expected values. It works from P0's bound package (M_P0 `13aee9c0`) and P0's committed records, by counted
replacements, each input asserted at its sha256; a rerun reproduces every output byte for byte.

**The connect** (diff against P0's bound `6a1bed95`, blobs aside):
- the root;
- the header;
- the checks tool, now `d2s0_checks.py` (P0's plus `stage`);
- the expected values, now `d2s0_expected.json`: P0's 14 inputs plus P0's two run records;
- the fence copy (`WRITE_ROOTS` only), and the three digests;
- `== 2b. iris` after the sacct fence;
- the stage loop after the input check;
- the record names `inputs-check.txt`, `stat-d2s0.txt` and `chain.rc`, and the runner name.

The sacct fence, clone, pins, config, overlap fence, `/dev/shm` copy, startup handoff, traps and cleanup are P0's,
byte for byte.

**The runner:**
- the header;
- the deadline is set in `step()`, per step (it was one deadline for the whole chain);
- the CLI step name is passed as `"$label"`. P0's `"${label%%-*}"` stripped a `-dry` suffix, and it would turn
  `d2-predict` into `d2`;
- the steps are `step d2-predict "$R/run"` and `step step0 "$R/run"`, after a check that P0's two records are in
  `run/`;
- the banner and the done line.

**The fetch and launcher:** names, the root and the pinned digests only. The fetch keeps P0's handling of `dry/`;
this chain writes no `dry/`, so that handling never fires.

**The checks tool:** P0's, plus `stage`. Its verdict lines read `INPUTS:` and `STAT:` (P0's read `P0 INPUTS:` and
`P0 STAT:`).

## Files

| file | sha256 |
|---|---|
| `production-config.ready.json` (P0's, unchanged) | `3b2afde495d630cc44df730e3e1acf12e0c332953e9fa298fa979f2e2e39b057` |
| `rpd_d2s0_connect.sh` | `8bf94bb0244bf341c2fd883a03e01b22a3fffea32131d41834819012e8e4f783` |
| `rpd_d2s0_fetch.sh` | `55227af2fa4d0a4b526e2224ee6736b8cfdb5aea1c16bcfb698abefcfd79b287` |
| `rpd_d2s0_launch.sh` | `e2bde947866807baf7a5ee92c5ec3842e9c6e96f68abc58e74fc08a92b426e61` |
| `tools/d2s0_checks.py` | `d3ff48f98cd797434c213730b9cf6b8bae6904be2b352f499efa1bb29086a506` |
| `tools/d2s0_expected.json` | `17a13256bac006c87703249989d4504af3144523a4797b95a51ee4a88699b509` |
| `tools/fence_overlap.py` | `33ba39c3ac65e5ca0c6f1c1657fb41a6edbda4af11b94bc3242892774b1c4e21` |
| `tools/p0_supervise.py` (P0's, unchanged) | `6ad0f68fb309a7b83adc0f65ed709e5e2412e650e115075fe41ebbc7a070134f` |
| `tools/gen_d2s0.py` | `a6899040f97d9fe0a647c1dd65d903276422e75a35effe61b9cbb2804955ad7c` |
| the runner (written by the connect) | `9303b1cfc0a6e5c26ad40abcd8f2ae6f321846b0611a92d93d954d7070f72c44` |

## Tests (local; nothing is contacted)

<!-- absence-ok: test-case descriptions (an empty run list, a missing record), not claims that a result does not exist -->
| test | result |
|---|---|
| `tests/test_sacct_fence.sh` | 24 checks, 17/17 mutants killed (the block cut from this connect; P0's, byte for byte) |
| `tests/test_launch.sh` | 23 cases, 13/13 mutants killed |
| `tests/test_connect_start.sh` | 4 cases, 6/6 mutants killed (the startup handoff, with real processes and signals) |
| `tests/test_runner.sh` | 25 cases, 25/25 mutants killed: P0's cases recast for the two steps, plus: no `--dry-run` passed and the CLI step names `d2-predict` and `step0` (mutant `step-name-truncated`, P0's `${label%%-*}`); P0's p0.json missing from `run/` (STOP, rc 9; mutant `predecessors-unchecked`); two 3 s steps under a 4 s deadline each, which pass only with per-step deadlines (mutant `deadline-shared`); `d2predict-skipped` |
| `tests/test_fetch.sh` | 20 cases, 12/12 mutants killed (the archive's member list compared exactly) |
| `tests/test_d2s0_checks.py` | 9 passed: P0's six (with the expected values now 16 inputs, P0's two records equal to the committed P0 records and p0.json's predecessor) and the stage mode (a byte-exact copy at mode 0600; never overwrites; a wrong sha256, a missing source and no O_NOATIME write nothing; the O_NOATIME flag used; the CLI form) |
| `tests/test_p0_supervise.py` | 17 passed (P0's tests of the unchanged supervisor) |
| the overlap fence | `FENCE OVERLAP: CLEAR (allowed 1, stops 0)` over 57 staged originals, with the new write root |

**The squeue grep:** the connect, the fetch, the launcher and the decoded payloads contain no `squeue`.

## Reads

The reports are under `~/codex-reports/note-measurement/reads/d2s0-20261124/`. Grok's account is out of credit, so
codex-school2 reads in its place.

| read | report | sha256 | verdict |
|---|---|---|---|
| agy | `agy/out.txt` | `3de5bda7cbefa8abfbf8b4d2aedbac846cad57ba68204300bd3d86d2ffaed8b4` | GO |
| codex-school2 | `codex2/out.txt` | `69648cfc813e2b5a48905490004d4aaa9a9221a01cbca2df4ad84d0e77e13fa6` | FIX |

**codex-school2's one blocking finding** concerned this README's description, not the scripts. `d2-predict` passes
`bins=None` and bincounts only the `step` axis, so it is not c0's 23-axis actual pass and cannot give c0's overhead
factor. The description above is corrected. The director chose (2026-11-24) to price c0 from a separate MC-only harness
that times `aggregate` with step0's bins, after this chain's records.

Its non-blocking notes were all taken:
- `step0`'s five sorts and its background decompression;
- the budget wording;
- the stage tool's cleanup docstring and its guarded `unlink`;
- the checks tool's labels;
- the inert `dry/` handling, noted above.

It also confirmed:
- the generator reproduces every output byte for byte;
- the bound CLI admits the staged chain: `require_predecessors` passes on the committed bytes, and `d2-predict` plans
  2,150.82 s, under 7,200 s;
- staging stays outside the input roots;
- no measured key is opened;
- the per-step deadlines, the step names and `chain.rc` work together.

The scripts changed after the reads only by the checks tool's labels and its cleanup guard, which changed its embedded
blob and the connect and launcher digests. Every suite was rerun on the final bytes.

## Before the connect

1. The director's binding, at the merged commit and these shas.
2. cov2d's ack no older than 6 h, saved as the ack file, and tier3-design's ack. director-helper-3's IBUB lane has been
   given the d2s0 write roots to protect.
3. A valid cert: Joseph renewed it to 2026-11-25T01:36:35Z, and the launcher's check is the authority.
4. Then `bash rpd_d2s0_launch.sh connect <new dir> <login node> <ack file>`, with the output written beside the session
   directory. Fetch from the runner's node until DONE or STOP.
5. Then the records PR. `d2-predict.json` must be committed before c0, the first step that reads data.
