# rpd_d2s0 for e1, 2026-11-27 (login02): d2-predict STOPPED at C_E3 with true Eν

**By** limitation-resolver, under [`../RPD-D2S0E1-BINDING.md`](../RPD-D2S0E1-BINDING.md) (#1415, merged 80e1a8a5), for
RPD-RECO amendment 1 ([`FD-RPD-RECO-DECLARATION-AMENDMENT-1.md`](../../../../FD-RPD-RECO-DECLARATION-AMENDMENT-1.md)).
The package is described in [`../README.md`](../README.md) (#1414).

**Result: STOP.**
- `chain.rc` = `rc=4 cause=step-d2-predict end=2026-11-27T04:52:51Z`.
- With true Eν from flux4's products, `d2-predict` refused at the frozen energy control **C_E3** after 7 min 31 s, and
  `step0` did not run.
- This is a finding, reported as it stands. The director accepted it on 2026-11-27, with nothing loosened and nothing
  resubmitted.
- The run took 0 node-h: login node only, with no job.

- **CITABLE FOR:** that d2s0e1 ran as bound and that d2-predict's C_E3 control failed with true Eν, with the values in
  its STOP record.
- **NOT CITABLE FOR:** any RPD-RECO result or note wording. No prediction exists, and no data row was read.

## The refusal

From [`records/run/d2-predict.STOP.json`](records/run/d2-predict.STOP.json) (code `12f68102…`, config `f92d034d…`):

> guard `C_E3`: "C_E3: q3 discrepancy 0.0009871258308031816, 0.0301471583174564 in 8:15"

`evaluate_energy_controls` (`fd_rpd_reco.py:971-1008` at S = 2415e8d6) takes the strata in order: 1.5:8, then 8:15,
then 15:60. In each it gates C_E1 (kinematic fraction ≥ `CE1_MIN` = 0.999), then C_E3 (weighted median ≤
`CE3_MEDIAN` = 0.002 and 99th percentile ≤ `CE3_Q99` = 0.03, `:99-101`). C-E2 is report-only, never a gate, and a
stratum's values are kept only in the results the step writes on success.

| p∥ stratum | C-E1 (≥ 0.999) | C-E3 median (≤ 0.002) | C-E3 99th percentile (≤ 0.03) | C-E2 |
|---|---|---|---|---|
| [1.5, 8) | PASS | PASS | PASS | report-only; not written (a STOP writes no results) |
| [8, 15) | PASS | **0.000987, PASS** | **0.030147, FAIL** (0.49% of the gate over) | not reached |
| [15, 60] | not reached | not reached | not reached | not reached |

**Against 11-24's inverted-Eν run** (`../../d2s0-20261124/run-20261124/`), in [8, 15):
- the median fell, 0.001260 → 0.000987;
- the 99th percentile did not: 0.030135 → 0.030147, from 0.45% to 0.49% of the gate over.

Amendment 1 §1 named the inversion's struck-nucleon mass term as a possible contributor and said only the bound run
could measure its effect. Removing it lowered the median but not the failing tail. Amendment 1 routes a C-E3 failure
back to the director. On 2026-11-27 the director ruled no new gate and no new formula yet. A read-only, MC-only
diagnostic of the [8, 15) tail comes first, declared before it runs.

**Blinding held.** `d2-predict` ran `data=False` with no `--prediction`. The refusal came from the MC energy controls,
and no measured key was opened.

## Preconditions (the binding)

- **The bound files.** The launch ran from a worktree detached at 80e1a8a5. All eight bound files and the runner (cut
  from the connect's heredoc, `7f7c7e15…`) hashed to the binding's values there.
- **The cert check.** `TZ=UTC ssh-keygen -L` at 04:41:40Z read the cert, renewed at 02:04Z, as valid to
  2026-11-28T02:05:18Z.
- **The three-lane ack file.** cov2d (04:41:55Z), tier3-design (04:42:01Z) and minerva-lib (04:42:12Z) each acked.
  Their replies are verbatim in [`acks/`](acks/) and under the three `ACK-UTC` lines of
  [`connect/ack.txt`](connect/ack.txt) (sha256 `b897dad7…`). The launcher read them at ages 31, 25 and 14 s.
- **ibu-chi** was told before the connect. Its OOFVC r3 post and fetch were disjoint.
- **END** went to cov2d, tier3-design and ibu-chi at about 05:03Z. minerva-lib asked not to be sent one.

## The connect: [`connect/`](connect/) (login02, 04:42:26Z to 04:45:18Z)

ssh rc 0, script rc 0.

- `node login02 staged sha256 e1b5084b…`, the bound connect.
- **Step 2, the sacct fence:** `sacct rows (14 days): 144; cov2d/t2a/rpd/geanttw rows: 19`, `FENCE: clear`.
- **Step 2b, iris** (recorded only, not a gate): m3246 charged 19,549.0 of 20,000.0 allocated.
- **Step 3, the clone:** `HEAD 2415e8d66d1a9160e724d426eaeb54d458d4b4f7; porcelain lines 0`, the 14 pins equal.
- **Step 4, the config:** `sha256 f92d034d… (expected f92d034d…)`.
- **Step 5, the in-place inputs:** `INPUTS: PASS (16 files, 0 bad)`. These are flux4's 14 records and products, and
  p0e1's `run/p0.json` `ab8d3600…` and `run/pins.json` `2a22bdbf…`. Both P0 records were then staged byte for byte
  into the new run directory (`STAGE: PASS`, twice).
- **Step 6, the retention record:** `STAT: PASS (40 files, 0 missing or different)`. The omnifiles' and the sidecar's
  atimes equal P0's record. The earliest purge exposure is 2026-12-30T11:38:24Z (the S1 dumps).
- **Step 7, the overlap fence:** `FENCE OVERLAP: CLEAR (allowed 1, stops 0)` over 70 staged originals.
- **Step 8:** the `/dev/shm` clone at S, porcelain 0, config `f92d034d…`.
- **Step 9, the runner:** sha256 `7f7c7e15…`, pid 769517 on login02 since 04:45:18Z. `/dev/shm` was handed over.

## The run (`records/`)

- **[`records/runner.out`](records/runner.out):** the runner at nice 19; `handoff.ok`; d2-predict's own 7200 s
  deadline; the STOP line; `removed /dev/shm/limres-rpd-flux1`.
- **[`records/sup-d2-predict.json`](records/sup-d2-predict.json):**
  - worker rc 4, no signal;
  - no deadline signal, not past the deadline;
  - no leftover, the group gone;
  - peak RSS 2,502,340,608 B (31% of the 8e9 B cap).
- **The price against the package's.** 7 min 31 s against the measured 6 min 42 s of 11-24, and 2.50 GB against
  2.00 GB. Both are within the step's 7200 s deadline and the cap.
- **The step's own estimate** (`planned_seconds` 2414.6 s with factor 10) is in the STOP record's
  `details.execution`.

## The fetch: [`fetch1/`](fetch1/) (login02, 05:00:31Z to 05:00:41Z, bound fetch `0853a029…`)

Script rc 12 and launcher rc 12: STOP, the fetch's exit for a terminal record with a nonzero rc. It reported:
- `chain.rc: rc=4 cause=step-d2-predict`;
- `run/staged: 38 files`;
- 14 files sent, 314,996 bytes;
- `TAR END tar rc=0 base64 rc=0`.

Untarred locally, each of the 14 matched its printed sha256.
- `records/` holds 12 of them.
- The other two, `run/p0.json` and `run/pins.json`, are byte copies of p0e1's records. They are already committed at
  `../../p0e1-20261126/run-20261127/records/run/` (`p0.json` plainly, `pins.json` gzipped) with the same sha256s:
  `ab8d3600…` and `2a22bdbf…`.

`fetch1/session.notar.out` and `fetch1/launcher.notar.out.txt` have the base64 tar block replaced by one line. The full
files had these sha256:
- `session.out`: `4403660773c682cf57cb4050bce70fc62f590d0f1910ffc25ddcb73e801bfd7a`;
- the launcher output: `d55c14e7af1c34ba14d4b9ddd266cdd2eff1339b723b4ad3247c782c7ccb07cd`.

## Left on pscratch

`/pscratch/sd/j/josephrb/rpd-reco-d2s0e1-20261127` holds the clone, the tools, the staged copies and the records.
`/dev/shm/limres-rpd-flux1` was removed by the runner. P0's root and flux4's lane stay, by the director's instruction,
until the diagnostic is decided.

[`SHA256SUMS`](SHA256SUMS) covers every file in this directory except itself.
