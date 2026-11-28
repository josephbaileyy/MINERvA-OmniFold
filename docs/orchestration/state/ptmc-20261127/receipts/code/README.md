# PTMC code: the tests, harnesses and mutation campaigns (2026-11-27/28)

All of this ran on the Mac and none of it touched NERSC. The tests and harnesses ran at the code branch's commit
`7859775b9` (`head.txt`), before main was merged in. Each mutation run names its own commit below.

## Tests and harnesses, on the final files

| record | what | result |
|---|---|---|
| `pytest.txt` | `test_ptmc.py` (pure, driver and runner tests on RE-2's fixture), `test_ptmc_score.py` (the scorer end to end on hand-made products) and `launch/test_launch.py` (the pilot's post and the D4 staging), with PyROOT 6.40 | 69 passed, rc 0 |
| `harness_remote.txt` | `launch/harness_remote.sh` in debian:bookworm-slim: every gate of `ptmc_remote.sh`, run against stubs with real dd, sha256sum, stat and tar | 88/88 |
| `harness_sbatch.txt` | `launch/harness_sbatch.sh`: the two sbatch files' unit coverage, failure propagation and refusals, one case per gate | 23/23 |
| `harness_launch.txt` | `launch/harness_launch.sh`: the Mac launcher's STOP paths, the stage mode's dtn01 route and the fetch's hash | 15/15 |

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
| `LIB_RELCLOSE_NAN` | **equivalent** | every non-finite operand already fails `rel_close` through the exact-zero rule or a NaN comparison, so the explicit finiteness test never changes an outcome |
| `SC_RANK_LITERAL` | **equivalent in production** | the literal 50 is the declared rank. At the test's scale it only loosens C-SHAPE, which the conditioning guard re-covers at the declared rank |

**Implied rule.** With L capped at (12.5 − pilot)/5, a projection over 11.5 node-h forces L/runtime ≤
(12.5 − p)/(11.5 − p) ≈ 1.09, which is below the 1.1 floor. So the floor rule implies the projection rule. The
director accepted the band where the floor STOPs under an 11.5 projection, t_R ≈ 780–800 s, as declared fail-closed.

**Run 4's survivors** (run 5 re-ran all eight):

| survivor | why it survived | what was done |
|---|---|---|
| `D4_SYMLINK_OK` | a symlink already fails in `copy_noatime`, so no case reached the regular-file check alone | test added: a FIFO source, which would otherwise copy as an empty file; killed in run 5 |
| `RUN_ROWS_FILE_PIN` | the only rows-pin test gave a wrong `--rows-sha256`, which the argument check already refuses | test added: altered rows bytes with the pinned argument; killed in run 5 |
| `RUN_PAIR_MASK`, `RUN_REFINE_DIGEST`, `RUN_COMP_AXES` | the fixture's units pass every control, and no test planted a defect at these checks | tests added: the capture is corrupted before the controls run (a false measured mask; a refined weight one ulp off; shifted completeness axes), and the unit must fail on exactly that control; each killed in run 5 |
| `RUN_ARGS_FINITE` | as above | test added: an infinite nucleon count zeroes every cell, so every `rel_close` control passes on exact zeros and only `extract_args_finite` fails the unit; killed in run 5 |
| `LIB_RELCLOSE_NAN`, `SC_RANK_LITERAL` | the equivalents above | — |
