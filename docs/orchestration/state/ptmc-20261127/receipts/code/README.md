# PTMC code: the tests, harnesses and mutation campaigns (2026-11-27/28)

All of this ran on the Mac and none of it touched NERSC. The tests and harnesses ran at the code branch's commit
`d43c670b1` (`head.txt`), before main was merged in. Each mutation run names its own commit below.

## Tests and harnesses, on the final files

| record | what | result |
|---|---|---|
| `pytest.txt` | `test_ptmc.py` (pure, driver and runner tests on RE-2's fixture), `test_ptmc_score.py` (the scorer end to end on hand-made products) and `launch/test_launch.py` (the pilot's post and the D4 staging), with PyROOT 6.40 | 95 passed, rc 0 |
| `harness_remote.txt` | `launch/harness_remote.sh` in debian:bookworm-slim: every gate of `ptmc_remote.sh`, run against stubs with real dd, sha256sum, stat and tar | 92/92 |
| `harness_sbatch.txt` | `launch/harness_sbatch.sh`: the two sbatch files' unit coverage, failure propagation and refusals, one case per gate | 26/26 |
| `harness_launch.txt` | `launch/harness_launch.sh`: the Mac launcher's STOP paths, the stage mode's dtn01 route, and the fetch's hashes against the remote digests | 16/16 |

## Mutation campaigns (`ptmc_mutation.py`)

Each mutant is one exact edit, run against the tests named for it. The records are JSON, committed as
`.json.txt` with their bytes unchanged, so the receipt-artifact check does not read the tests' tails as citations. Driver mutants regenerate `ptmc_driver.diff` and
make_tree's pin. Shell mutants run the docker harnesses.

| run | files | result |
|---|---|---|
| 1, `mutation-1.json.txt` (`mutation-1-log.txt`) | committed at `6f60e086a`, digests unchanged after | CONTROL PASS; 42/50 killed |
| 2, `mutation-2.json.txt` (`mutation-2-log.txt`) | committed at `f4aa13ca7`, after the survivors' tests and the conditioning guard | CONTROL PASS; 48/51 killed |
| 3, `mutation-3.json.txt` | committed at `27ce2ae22e`, after the pilot-post baseline fix | CONTROL PASS; PP_COUPLE, PP_STOP_AT, PP_FLOOR, PP_CAP_PER_NODE all killed |
| 4, `mutation-4.json.txt` (`mutation-4-log.txt`) | committed at `c6b4e434e`, after code-read-1's hardening: the fresh full campaign with one mutant per gate. Digests unchanged after | CONTROL PASS; 105/113 killed |
| 5, `mutation-5.json.txt` (`mutation-5-log.txt`) | committed at `7859775b9`, run 4's eight survivors after their tests. Digests unchanged after | CONTROL PASS; 6/8 killed, each by its own new test; the two survivors are the equivalents below |
| 6, `mutation-6.json.txt` (`mutation-6-log.txt`) | committed at `d43c670b1` (code-confirm-1's fixes), 2026-11-28 08:34:30Z to 09:13:03Z UTC: the 41 new mutants (one per new gate) and the 5 earlier mutants whose anchors the fixes changed. Digests unchanged after | CONTROL PASS; 45/46 killed, each by its own test; the survivor `SB_LANES_20` is an equivalent (below) |

**Run 1's eight survivors:**

| survivor | why it survived | what was done |
|---|---|---|
| `LIB_SUPPORT_UNWEIGHTED` | the support test used unit weights | test added: a zero-weight row drawing a positive factor |
| `LIB_SHAPE_LOO` | no case lost rank in a leave-one-out only | test added: a mode that only replica 0 carries |
| `DRV_STREAMS`, `DRV_UNIT_FACTORS` | the bootstrap block's second guard also refuses, so a non-zero exit alone could not tell the two apart | the test now requires the argument check's own message |
| `PP_COUPLE` | no case had a central without its coupling record | test added; run 2 then showed it still survived (next table) |
| `PP_STOP_AT` | the floor rule implies the projection rule (see below), so the STOP held either way | test added on the rule's own flag at a 12.0 node-h projection; killed in run 3 |
| `SC_RANK_LITERAL` | at the fixture's 12 rows, rank-50 roundoff modes pass pinv_rank's declared criterion | the director's ruling: the binding's conditioning guard, λ_r/λ₁ ≥ 1e-10 per arm, else STOP (`ptmc_lib.conditioning`, its own commit, with test and mutant `LIB_COND_FLOOR`) |
| `LIB_RELCLOSE_NAN` | equivalent, see below | — |

**Run 2's survivors:**

| survivor | why | what was done |
|---|---|---|
| `PP_COUPLE` | the negative tests' default sacct projected about 11.75 node-h, so they STOPped on the projection whatever was planted | the default is now the scoped, PROCEEDing timing, and a baseline test asserts it proceeds; killed in run 3 |
| `LIB_RELCLOSE_NAN` | **equivalent at the declared tolerances** | every non-finite operand already fails `rel_close` through the exact-zero rule or a NaN comparison, with one qualification (code-confirm-1's note): a finite value against an infinite reference gives \|a/b − 1\| = 1, which fails only because every declared tolerance is below 1. So the explicit finiteness test changes no outcome at those tolerances |
| `SC_RANK_LITERAL` | **equivalent in production** | the literal 50 is the declared rank. At the test's scale it only loosens C-SHAPE, which the conditioning guard re-covers at the declared rank |

**The floor and the projection rule are independent.** Runs 1–4 said here that the floor implies the projection
rule. That is wrong in general (code-confirm-1's note). With L capped at (12.5 − p)/5 node-h for a pilot of p node-h,
a projection over 11.5 forces L/runtime ≤ (12.5 − p)/(11.5 − p). That bound is below the 1.1 floor only for a small
pilot; it passes 1.1 once p exceeds 1.5 node-h. The reader's case: a 3,540 s pilot on 2 nodes (p = 1.97), t_R = 680 s
and a 3,470 s longest step give o = 70 s, a runtime of 6,870 s and L = 126 minutes. The floor passes
(600 × 126 = 75,600 ≥ 11 × 6,870 = 75,570), but the projection is 7,080 + 5 × 6,870 = 41,430 node-s, over the 41,400
STOP. `ptmc_pilot_post.py` checks both rules separately, so that run STOPs on the projection. `PP_STOP_AT` was killed in
run 3 by a test on the projection rule's own flag. The director accepted the other band, where the floor STOPs under an
11.5 projection (t_R ≈ 780–800 s), as declared fail-closed.

**Run 4's survivors** (run 5 re-ran all eight):

| survivor | why it survived | what was done |
|---|---|---|
| `D4_SYMLINK_OK` | a symlink already fails in `copy_noatime`, so no case reached the regular-file check alone | test added: a FIFO source, which would otherwise copy as an empty file; killed in run 5 |
| `RUN_ROWS_FILE_PIN` | the only rows-pin test gave a wrong `--rows-sha256`, which the argument check already refuses | test added: altered rows bytes with the pinned argument; killed in run 5 |
| `RUN_PAIR_MASK`, `RUN_REFINE_DIGEST`, `RUN_COMP_AXES` | the fixture's units pass every control, and no test planted a defect at these checks | tests added: the capture is corrupted before the controls run (a false measured mask; a refined weight one ulp off; shifted completeness axes), and the unit must fail on exactly that control; each killed in run 5 |
| `RUN_ARGS_FINITE` | as above | test added: an infinite nucleon count zeroes every cell, so every `rel_close` control passes on exact zeros and only `extract_args_finite` fails the unit; killed in run 5 |
| `LIB_RELCLOSE_NAN`, `SC_RANK_LITERAL` | the equivalents above | — |

## code-confirm-1 (codex-school2) and its fixes

The narrow confirm read (`gpt-6.2-sol`, high) of `168de3b72` found 13 of 39 findings fixed, with 15 blockers: 12
residual (B1–B12) and three new (B13, B14 and B15). The director ruled on scope. Commit `d43c670b1` fixes every
blocker and the listed PARTLY rows, each with one test and one mutant (run 6, below). Two parts are accepted residuals
by the director's ruling, under the campaign's threat model (mistakes and lasting changes, not a hostile actor on the
same account):

- **B7, the stager's descriptor race.** `ptmc_stage_d4.py` copies through REF-C2C1's own `copy_noatime`, as section 1
  declares. It checks each source's identity (device, inode, size, mtime) before and after the copy. Only a swap made
  and undone inside one copy could pass that check, and no mistake does that.
- **B8, import order.** The scorer imports its own `ptmc_lib` before `check_bytes` hashes it. Every sha check comes
  before any output is written, so an unverified module cannot write or change a record. The runner now hashes
  `ref_c2c1.py` and `oofvc_lib.py` before importing them.

The publication check (codex 19) was checked against the real file: the local copy of
`cov_ptpl_minerva_inclusive_6GeV.root`, whose sha256 is `PUB_SHA` (6c6dce72), holds `pt_pl_cross_section` as a TH2D
with 16 p∥ × 14 pT finite, increasing bins.

**Run 6's survivor:**

| survivor | why | what was done |
|---|---|---|
| `SB_LANES_20` | **equivalent** | it removes `replicas.sbatch`'s final requirement of exactly 20 successful lane records. The check sits behind `bad=1`: a lane that returns non-zero, or whose record line cannot be written, already fails the job. The lane list is now a literal (no `seq`, so no lane can be left out, which `SB_LANES_LITERAL`'s test kills). So no reachable run has all 199 unit outcomes 0 with fewer than 20 lane records. The check is kept as defence in depth |

Two harness kills (`SH_STAT_STATUS`, `SH_PILOT_T60`) have their failing line cut from the record's 1,500-character
tail. Re-applied to copies outside the repository, each failed exactly its own case: "stage: a failed stat of a source
STOPs" and "pilot: submitted on -N 2 -t 60, jobid recorded".
