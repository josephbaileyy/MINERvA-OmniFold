# BINDING 1: 1B staged method coverage, stage 0 (κ) (director, 2026-11-02)

**Binds** stage 0 of [`FD-1B-STAGED-DECLARATION.md`](FD-1B-STAGED-DECLARATION.md) (revision 2) as merged in PR #664 at
**M = `b3705d4360520612842c4c819ac6f51041f274f2`** (PR head `cf0505d9e9c29c25921b67c49846eac57a0820be`). Stage 0 is §2: #655's κ-only option, carried
byte-identical from `55435ec0`.

**Under** `DECISION-20261101-joseph-1b-staged-method-coverage.md` (#663).

## The code bound (git blob digests at M)

| blob | path |
|---|---|
| `31a88850a7999884150fef402fb0f22cba9005ed` | `nd-unfolding/fd_1b_moded.py` (sha256 `420088436948d942…`) |
| `4f20d2c3631a671719a414793f53ecf9c5c6eb80` | `nd-unfolding/tests/test_fd_1b_moded.py` |
| `eadab245a1b2abf74cb55e4be2f56579c28aea10` | `fd/receipts-1b/moded/mutation.py` |
| `e6ef689279616926af7a26c40eb40f7297112771` | `fd/receipts-1b/moded/mutation.out` |

`fd_1b_inv.py` is unchanged, as bound by #644. `fd_1b_null.py` (`1810161d…`), its tests and receipts are on `main`, but
they are stage 1's code. This binding does not bind them; binding 2 does.

## What the director checked

- **The code:** `fd_1b_moded.py` at M has the same sha256 as at `55435ec0` (`420088436948d942…`).
- **The tests:** `python3 -B -m pytest tests/test_fd_1b_moded.py tests/test_fd_1b_null.py` at M, with its own TMPDIR,
  gave 57 passed.
- **The audit:** `coverage-5b-audit` acknowledged revision 2 for binding 1 (PR #664, issuecomment-6570700305). Before
  that it reran stage 0, the tests, `mutation_null` and `arith.out`.
- **The independent consult** is in `FD-1B-MODED-CONSULT-ANSWER.txt` (#660).

## Rulings

1. **Stage 0 is bound as §2 declares it.**
   - **The rule:** rule K on κ = √(Dnom / A_unc) per cell, in [0.9, 1.1].
   - **The grid check:** descriptive. A failure of its nominal-grid reproduction invalidates the grid part only.
   - **The cap:** the pilot D-0 at ≤ 1.0 node-h, then the bulk at ≤ 4.5 node-h, so **5.5 node-h**. The reservation is
     the cap.
   - **The Ddl option is excluded from stage 0.**
2. **The gate.**
   - **PASS (16 of 16):** stage 1 may proceed only after three things: the audit acknowledges stage 0's report, binding
     2 binds §11's code, and Joseph is told.
   - **PARTIAL (8 to 15):** stage 1 waits for Joseph (§14.2).
   - **FAIL (below 8):** the campaign stops and goes to Joseph.
   - **INVALID:** reported to the director, unrepaired.
3. **Routing.** The bulk is submitted only after `walls` PASS and the audit's written acknowledgement of D-0's
   readout. If no acknowledgement arrives within 2 h, the lane messages the director and does not submit. Each report
   reaches the audit before the next submission.
4. **Connects:**
   - regular CPU nodes only (`-q regular -C cpu`), with every job under 12 h;
   - from a fresh clone detached at M, with empty porcelain;
   - writes only under a new directory on pscratch, and nothing to CFS;
   - O_NOATIME for every pscratch read, with a moved atime reported and not restored;
   - the HPSS copy at the end, after `hpssquota`.
5. **Carried into binding 2, by the lane's proposal and the audit's assignment:**
   - **N1:** binding 2's first receipt bounds composite weights on rows with near-zero CV weight. A material count is
     an amendment.
   - **N2:** the scope sentence for cells where C_model is more than half of C_T, in §13 and in clause S.
   - **The §4.5 nit.**
6. **Keeping C_model inside the simulated null is accepted.** Both the lane and the audit agree on it, and so does
   the director. Without it, the rule would test zero bias, not whether C_T holds its content.

Nothing is submitted, deposited or tagged.
