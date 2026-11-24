# rpd_d2s0, 2026-11-24 (login12): d2-predict STOPPED at C_E3

**By** limitation-resolver, under [`FD-RPD-RECO-BINDING-2-ADDENDUM-4.md`](../../../../FD-RPD-RECO-BINDING-2-ADDENDUM-4.md)
(merged 8abd6ce7), at M_D2S0 = `48537ff7a068ec06f8d431285116b4f5ae3b2ba0`. The package is described in
[`../README.md`](../README.md).

**Result: STOP.** `chain.rc` = `rc=4 cause=step-d2-predict`. `d2-predict` refused at the frozen energy control
**C_E3** after 6 min 42 s, and `step0` did not run.
- This is terminal under the addendum's ruling 7. It was reported to the director, and nothing was retried.
- The run took 0 node-h: login node only, with no job.

- **CITABLE FOR:** that d2s0 ran as bound and that d2-predict's C_E3 control failed, with the values in its STOP
  record.
- **NOT CITABLE FOR:** any RPD-RECO result or note wording. No prediction exists, and no data row was read.

## The refusal

From [`records/run/d2-predict.STOP.json`](records/run/d2-predict.STOP.json) (code `7302cc1d…`, config `3b2afde4…`):

> guard `C_E3`: "C_E3: q3 discrepancy 0.0012597542525496497, 0.030134546090343273 in 8:15"

- **The values.** In the p∥ stratum [8, 15), the weighted median of |q₃′/q₃ − 1| is 0.00126, within its gate of 0.002.
  The weighted 99th percentile is **0.030135**, over its gate of 0.03 by 0.45% of the gate.
- **The gate.**
  - `CE3_MEDIAN = 0.002` and `CE3_Q99 = 0.03` (`fd_rpd_reco.py:100-101`), applied in `evaluate_energy_controls`
    (`:935-941`).
  - The function takes the strata in order: 1.5:8, then 8:15, then 15:60. So [1.5, 8) passed C_E1 and C_E3, and
    [8, 15) passed C_E1 and failed C_E3. [15, 60] was not reached.
  - `d2-predict` reaches it through `prediction_controls` (`:2492-2494`).
- **The declaration** (FD-RPD-RECO-DECLARATION, the Eν section):
  - Eν comes from inverting W (the mean of the M_p and M_n values). This "departs from the scope's design, which priced
    an event-loop pass for Eν (scope §5, d2). The inversion costs 0 node-h. C-E3 is its check. If C-E3 fails, the
    event-loop route returns to the director, priced."
  - The controls are "each a STOP on failure", with "the weighted median |q₃′/q₃ − 1| ≤ 0.002, and the 99th
    percentile ≤ 0.03" in each stratum.
  - So this STOP is the declaration's pre-registered branch: the Eν route returns to the director, priced.
- **Blinding held.** `d2-predict` ran `data=False` with no `--prediction`. The refusal came from the MC energy
  controls, and no measured key was opened.
- **The supervisor** ([`records/sup-d2-predict.json`](records/sup-d2-predict.json)):
  - worker rc 4, no signal;
  - no deadline signal, not past the deadline;
  - no leftover, the group gone;
  - peak RSS 2,003,857,408 B (2.0 GB), against the 8e9 B cap.
- **The runner** ([`records/runner.out`](records/runner.out)) recorded STOP `d2-predict rc=4`, removed
  `/dev/shm/limres-rpd-flux1` and published `chain.rc`.

## Preconditions (ruling 3)

- **The bound files.** The launch ran from a worktree detached at 8abd6ce7. All ten bound sha256s re-hashed to the
  addendum's values there, including the runner from its heredoc (`9303b1cf…`).
- **cov2d's ack.** `ACK-UTC 2026-11-24T11:11:50Z` and cov2d's text, verbatim. The launcher read it at age 60 s and
  recorded it byte for byte as [`connect/ack.txt`](connect/ack.txt) (sha256 `e73ef34f…`).
- **tier3-design's ack.** At 11:11:34Z, verbatim in [`acks/tier3-design-ack.txt`](acks/tier3-design-ack.txt).
  tier3-design's q0 extract had ended at 08:16:44Z, so the two shared no window.
- **The cert check.** The launcher read the cert as valid to 2026-11-25T01:36:35Z.
- **The run root.** Absent on all four surveyed nodes, and by the connect's own guard.

## The survey: [`survey/`](survey/)

On login05, login12, login21 and login30:
- the root was absent on all four;
- the 15-minute loads were 14.62, 12.42, 98.93 and 17.82, so login12 was chosen.

## The connect: [`connect/`](connect/) (login12, 11:12:57Z to 11:14:16Z)

ssh rc 0, script rc 0. The launcher's output was written beside the session directory.

- `staged sha256 8bf94bb0…`, the bound connect.
- **The sacct fence:** `sacct rows (14 days): 81; cov2d/t2a/rpd rows: 17`, `FENCE: clear`.
- **iris** (connect output only): `m3246 … 19381.0 20000.0`, so 619.0 node-h remained for all users at that time.
- **The clone:** HEAD 6896e787, porcelain 0, with the 14 pins. The config is `3b2afde4…`.
- **The tools:** `d2s0_checks.py` `d3ff48f9…`, `d2s0_expected.json` `17a13256…` and `p0_supervise.py` `6ad0f68f…`,
  each equal.
- **The inputs:** `INPUTS: PASS (16 files, 0 bad)`, covering flux3's 14 inputs and P0's two run records.
- **The staging:** `STAGE: PASS` for `pins.json` `52fc41f4…` and `p0.json` `8ed2faf7…`, from P0's `run/` to d2s0's
  `run/`.
- **The retention record:** `STAT: PASS (27 files, 0 missing or different)`. The earliest purge exposure is
  2026-12-30T11:38:24Z.
- **The overlap fence:** `FENCE OVERLAP: CLEAR (allowed 1, stops 0)` over 57 staged originals.
- **The `/dev/shm` copy:** HEAD 6896e787, porcelain 0, config `3b2afde4…`.
- **The runner:** `9303b1cf…`, pid 1389816 on login12 since 11:14:16Z, with `/dev/shm` handed over.

## The fetch: [`fetch1/`](fetch1/) (login12, 11:42:51Z to 11:42:52Z, bound fetch `55227af2…`)

Script rc 12, launcher rc 12: STOP, the fetch's exit for a terminal record with a nonzero rc. It reported:
- `chain.rc: rc=4 cause=step-d2-predict end=2026-11-24T11:20:59Z`, state STOP;
- `run/staged: 38 files`, which stay on pscratch;
- 14 files sent, 210,419 bytes, `TAR END tar rc=0 base64 rc=0`.

Untarred locally, all 14 matched their printed sha256.

**Two of the 14 are not committed again:** `run/pins.json` and `run/p0.json`, the connect's staged copies of P0's
records.
- Each matched its printed sha256: `52fc41f4…` and `8ed2faf7…`.
- Those are byte-identical to P0's committed records. They are `p0-20261123/run-20261124/records/run/p0.json`, and
  `pins.json.gz`, which decompresses to `pins.json`.
- Committing the plain `pins.json` again would also re-trip the receipt-artifact hook's bare-name check.

`fetch1/session.notar.out` and `fetch1/launcher.notar.out.txt` are the outputs with the base64 tar block replaced by
one line. The full files had these sha256:
- `session.out`: `5b1bdcc4980b2a080e4687822ec0ae55e976bf2af197ddb8ef71077020b1fd89`;
- the launcher output: `02da13a5b447668393662392997c2c8b06d54e4957017fe4b0fb8b5057831de0`.

## Left on pscratch

`/pscratch/sd/j/josephrb/rpd-reco-d2s0-20261124` holds the clone, the tools, the staged copies (`run/staged`) and the
`.pgid` file. The runner removed `/dev/shm/limres-rpd-flux1` on login12.

[`SHA256SUMS`](SHA256SUMS) covers every file in this directory except itself.
