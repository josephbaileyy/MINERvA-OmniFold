# REPORT: the cheap tier's 5A, the 2D run-period term on the 16 cells (2026-10-29)

**By** the measurement session (`coverage`), for the director.

**Under** [`FD-CT-READERS-BINDING-AMENDMENT-1.md`](FD-CT-READERS-BINDING-AMENDMENT-1.md) (PR #495), which binds
[`FD-CT-READERS-AMENDMENT-1.md`](FD-CT-READERS-AMENDMENT-1.md) (`45d470d7…`) at deploy pin `bb8dc101`, on
[`FD-CT-READERS-DECLARATION.md`](FD-CT-READERS-DECLARATION.md) (`0571c973…`) and its first binding. The first 5A run
stopped at the leak guard; that STOP and the diagnostic are in [`FD-CT-READERS-REPORT.md`](FD-CT-READERS-REPORT.md) §4.

**MEASURES:** the amendment's deploy and the one 5A run, as bound, with their receipts; every control's outcome; the
readout's numbers, copied from the committed readout by `make_5a_tables.py`.

**CANNOT AUTHORIZE, and draws no conclusion on:** a covariance component or any change to the reported matrix
C_total + C_resp, a cell, a readout or κ; a run-period effect in the hadronic variables; any claim, reading or printed
wording. C_PL,16 is printed beside the reported matrix, never in it (addendum §5.4).

**CITABLE FOR:** what 5A computed on the declared inputs, as bound, and that every refusing control passed.

**NOT CITABLE FOR:** any reading of these numbers; a 5D run-period block; whether the 2D period offsets depend on
E_avail, q3 or W.

**Receipts:** [`fd/receipts-ct/run-am1/`](fd/receipts-ct/run-am1/): `s1_deploy_am1.sh` (`aecdd16c…`) and
`s2_period_am1.sh` (`be6d5a23…`), which differ from the bound run's scripts only in `$B`, the pin and the amendment's
digest line; the cluster logs under `cluster/`. The readout is [`fd/readout/fd_ct_period.json`](fd/readout/fd_ct_period.json)
(`d7d518ac…`), equal to the sha256 its run printed.

## 0. Summary

- **Cost:** 0 node-h, on login37, with no Slurm job. Nothing went to CFS.
- **Deploy and tests** (binding §3 condition 1): all held (§1).
- **5A, `period`:** exit 0 in about 1 s. Controls S, P0 (eight checks), P1, P2 and P3 passed, and the P4 assertion held
  (§2). 3a and 4C were not rerun; their readouts stand as reported.

## 1. Deploy and tests

A clean clone at `bb8dc101898c79713a40aead51ed7980db4dc36e` into `$B/deploy/bb8dc101`,
`B=/pscratch/sd/j/josephrb/fd-ct-readers-am1-20261029`, on login37 at 2026-10-29T07:55:50Z (`cluster/deploy.log`).
<!-- absence-ok: `test -e $B` printed B-absent on login37 before the deploy, and s1_deploy_am1.sh exits 9 if $B exists; it reached its clone step (cluster/deploy.log) -->
`$B` did not exist beforehand. Every bound condition held:
- HEAD is the pin;
- 0 porcelain lines before the tests and 0 after;
- the amendment's §6 digests: `fd_ct_readers.py` `32e9b061…`, `test_fd_ct_readers.py` `9c543aee…`, `fd_f0_regrade.py`
  `0dfa722c…`, `s1_assemble.py` `b157250a…`, `s5p_stage1_inspect.py` `26569afc…`, `h2_definition.json` `b6790761…`;
  and the declaration `0571c973…` and amendment `45d470d7…`;
- `tests rc=0`, with "Ran 153 tests in 390.980s, OK" (`cluster/deploy-tests.log`).

## 2. 5A, `period`

**Run:** 10:11:17–10:11:18Z, against a projection of 60 s and a timeout of 75 s; exit 0 (`cluster/period.out`,
`walls.txt`). Every control passed:
- S;
- P0: the committed JSON names the npz; the fine grid's p_T and p_∥ edges are the 2D grid's; 205 distinct 2D cells;
  one entry per cell; e_X constant and summing to 1; Σ_X e_X g_X = 0; C_PL rebuilt equals the stored C_PL;
- P1: the central value integrates to S1's f;
- P2: the prior is MnvTune v1's on the fine grid;
- P3: every cell has positive weight on the 2D term's cells;
- P4 (an assertion): Σ_X e_X g_X,R = 0 and C_PL,16 is PSD of rank ≤ 2, for both weightings.

<!-- absence-ok: quotes the readout's own label verbatim (fd_ct_period.json labels.what), the declaration's scoping of 5A -->
**Its label, as written in the readout:** "a size under an untested assumption: the 2D period offset g_X does not depend on E_avail, q3 or W inside a (p_T, p_parallel) bin; only 5B can test it; built from the observed offsets, so it contains them by construction and cannot fail; not a 5D run-period block, and printed beside the reported matrix, not in it (LIMITATION-PLAN-ADDENDUM-20261028.md section 5.4)"

**C_PL,16 is a size under an untested assumption,** that the 2D period offset does not depend on E_avail, q3 or W
inside a (p_T, p_∥) bin. It contains the observed 2D offsets by construction, so it cannot fail. Only 5B can test the
assumption.
<!-- absence-ok: restates the declaration's own scoping (FD-CT-READERS-DECLARATION.md section 0, 5A) and binding section 3 condition 4's required label -->

**The weighting departs from the addendum** (binding ruling 6). The primary weighting is the (e) central value. The
addendum's scoping said "the cell's prior weight" (`LIMITATION-PLAN-ADDENDUM-20261028.md` §5.2). The reason: the
projection averages the 2D offsets over the pooled result's content in each footprint, and 2D's own construction used
x = E_U, the data. The choice was made while the tool was written, before any 5A quantity existed. MnvTune v1's prior
is the declared sensitivity, and is written beside it.

**u_R is written for the prior only** (ruling 9). For the central value it would be 1 − X_sup/f, a partial data
integral of the X/f − 1 form. Its extrapolated labels are written for both weightings.

**Weighting: central** (primary: the (e) central value's fine-cell contributions x_f vol_f). Rank of C_PL,16: 2. Trace share of C_PL,16 in C_total + C_resp + C_PL,16: 0.05412. Extrapolated cells (u_R > 0.1): none. 2D cells with negative weight, per cell: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0].

| cell | σ/f C_PL,16 | σ/f S_ref,16 | σ/f C_total + C_resp | ratio C_PL,16 / (C_total + C_resp) |
|---|---:|---:|---:|---:|
| R00 | 0.01346 | 0.00739 | 0.07097 | 0.1896 |
| R01 | 0.01375 | 0.00780 | 0.07095 | 0.1938 |
| R02 | 0.01430 | 0.00804 | 0.14004 | 0.1021 |
| R03 | 0.01361 | 0.00752 | 0.12637 | 0.1077 |
| R04 | 0.02597 | 0.01464 | 0.04203 | 0.6179 |
| R05 | 0.02235 | 0.01242 | 0.07475 | 0.2991 |
| R06 | 0.02573 | 0.01469 | 0.05891 | 0.4368 |
| R07 | 0.02451 | 0.01397 | 0.07977 | 0.3073 |
| R08 | 0.01878 | 0.01120 | 0.06255 | 0.3002 |
| R09 | 0.01977 | 0.01176 | 0.06265 | 0.3156 |
| R10 | 0.01932 | 0.01164 | 0.08592 | 0.2249 |
| R11 | 0.02517 | 0.01585 | 0.13686 | 0.1839 |
| R12 | 0.02348 | 0.01286 | 0.06632 | 0.3540 |
| R13 | 0.02420 | 0.01325 | 0.11071 | 0.2186 |
| R14 | 0.01981 | 0.01084 | 0.05265 | 0.3763 |
| R15 | 0.02310 | 0.01266 | 0.07941 | 0.2909 |

- σ/f of C_PL,16: median 0.02108 (0.01346–0.02597); of S_ref,16: median 0.01209 (0.00739–0.01585).
- The ratio to C_total + C_resp: median 0.2950 (0.1021–0.6179).

**Weighting: prior** (sensitivity: MnvTune v1's fine-cell contributions). Rank of C_PL,16: 2. Trace share of C_PL,16 in C_total + C_resp + C_PL,16: 0.05478. Extrapolated cells (u_R > 0.1): none. 2D cells with negative weight, per cell: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0].

| cell | σ/f C_PL,16 | σ/f S_ref,16 | σ/f C_total + C_resp | ratio C_PL,16 / (C_total + C_resp) | u_R |
|---|---:|---:|---:|---:|---:|
| R00 | 0.01321 | 0.00724 | 0.07097 | 0.1862 | 0.00000 |
| R01 | 0.01393 | 0.00799 | 0.07095 | 0.1963 | 0.00000 |
| R02 | 0.01406 | 0.00788 | 0.14004 | 0.1004 | 0.00000 |
| R03 | 0.01373 | 0.00761 | 0.12637 | 0.1087 | 0.00000 |
| R04 | 0.02618 | 0.01480 | 0.04203 | 0.6228 | 0.00000 |
| R05 | 0.02298 | 0.01284 | 0.07475 | 0.3075 | 0.00000 |
| R06 | 0.02597 | 0.01486 | 0.05891 | 0.4408 | 0.00000 |
| R07 | 0.02494 | 0.01425 | 0.07977 | 0.3127 | 0.00000 |
| R08 | 0.01873 | 0.01116 | 0.06255 | 0.2994 | 0.00000 |
| R09 | 0.01969 | 0.01170 | 0.06265 | 0.3142 | 0.00000 |
| R10 | 0.01913 | 0.01150 | 0.08592 | 0.2227 | 0.00000 |
| R11 | 0.02512 | 0.01582 | 0.13686 | 0.1836 | 0.00000 |
| R12 | 0.02374 | 0.01303 | 0.06632 | 0.3580 | 0.00000 |
| R13 | 0.02433 | 0.01333 | 0.11071 | 0.2197 | 0.00000 |
| R14 | 0.02002 | 0.01090 | 0.05265 | 0.3803 | 0.00000 |
| R15 | 0.02334 | 0.01283 | 0.07941 | 0.2939 | 0.00000 |

- σ/f of C_PL,16: median 0.02150 (0.01321–0.02618); of S_ref,16: median 0.01226 (0.00724–0.01582).
- The ratio to C_total + C_resp: median 0.2967 (0.1004–0.6228).

**Constants:** e = 0.5334, 0.2945, 0.1721 (PA, PB, PC); k = V2/(1 − V2) = 0.6691.

## 3. Ledger, walls and storage

| step | host | start (UTC) | end (UTC) | wall | projection | rc |
|---|---|---|---|---:|---:|---|
| deploy and tests (amendment 1) | login37 | 07:55:50 | 08:02:26 | 396 s | — | tests 0 |
| 5A `period` | login37 | 10:11:17 | 10:11:18 | ~1 s | 60 s | 0 |

All 0 node-h, no Slurm job. The rows are in `fd/LEDGER.tsv`. **Retention:** `$P/fd-ct-readers-am1-20261029/` (deploy
clone, logs, readout) joins the pscratch list.

## 4. Not changed

Every covariance, cell, readout and κ, and the reported matrix C_total + C_resp; 3a's and 4C's readouts;
`docs/analysis-note/**`. Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
