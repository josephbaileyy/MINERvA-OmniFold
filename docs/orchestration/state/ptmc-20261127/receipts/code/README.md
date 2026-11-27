# PTMC code: the tests, harnesses and mutation campaigns (2026-11-27/28)

All of this ran on the Mac at the code branch's commit `27ce2ae22e` (`head.txt`), before main was merged in. None of
it touched NERSC.

## Tests and harnesses, on the final files

| record | what | result |
|---|---|---|
| `pytest.txt` | `test_ptmc.py` (pure, driver and runner tests on RE-2's fixture), `test_ptmc_score.py` (the scorer end to end on hand-made products) and `launch/test_launch.py` (the pilot's post and the D4 staging), with PyROOT 6.40 | 43 passed, rc 0 |
| `harness_remote.txt` | `launch/harness_remote.sh` in debian:bookworm-slim: every gate of `ptmc_remote.sh`, run against stubs with real dd, sha256sum, stat and tar | 40/40 |
| `harness_sbatch.txt` | `launch/harness_sbatch.sh`: the two sbatch files' unit coverage, failure propagation and refusals | 7/7 |
| `harness_launch.txt` | `launch/harness_launch.sh`: the Mac launcher's local STOP paths | 5/5 |

## Mutation campaigns (`ptmc_mutation.py`)

Each mutant is one exact edit, run against the tests named for it. The records are JSON, committed as
`.json.txt` with their bytes unchanged, so the receipt-artifact check does not read the tests' tails as citations. Driver mutants regenerate `ptmc_driver.diff` and
make_tree's pin. Shell mutants run the docker harnesses.

| run | files | result |
|---|---|---|
| 1, `mutation-1.json.txt` (`mutation-1-log.txt`) | committed at `6f60e086a`, digests unchanged after | CONTROL PASS; 42/50 killed |
| 2, `mutation-2.json.txt` (`mutation-2-log.txt`) | committed at `f4aa13ca7`, after the survivors' tests and the conditioning guard | CONTROL PASS; 48/51 killed |
| 3, `mutation-3.json.txt` | committed at `27ce2ae22e`, after the pilot-post baseline fix | CONTROL PASS; PP_COUPLE, PP_STOP_AT, PP_FLOOR, PP_CAP_PER_NODE all killed |

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
