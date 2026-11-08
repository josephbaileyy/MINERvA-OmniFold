# BINDING: the per-period 2D benchmark (director, 2026-11-07)

**Binds** [`DECLARATION.md`](DECLARATION.md) and its code, as merged in PR #868 (merge `03f9b5cb`), at
**M = `a7af2e614f2d65ca10d169e6d73582e83f9ecf1d`**.

| file | sha256 |
|---|---|
| `DECLARATION.md` | `9bc3921bc86b62813d8297e66012f1e941398ce641a67fc5f46fe6fa6cdd5961` |
| `per_period_benchmark.py` | `94fc5a3d23ffcdf6c16629aef328979f1940cfbc373cc0790761be75d331d70b` |
| `test_per_period_benchmark.py` | `8f3ccf8aa052d377e6a84e797a61efea4df2b0f8645c64bcc003ab1ea9ef68c0` |
| `INPUTS.sha256` | `9c05e5e1aa3d12d6782a23c0b5625ea63de429071667761b026366d92b6a3be0` |

The director re-hashed each file from M, and all four match.

**Under** `DECISION-20261106-joseph-plateau-next-work.md` item 1, at main `6d0aca7f`.

## What the director checked

**coverage-5b-audit's GO at rev 3**
(https://github.com/josephbaileyy/MINERvA-OmniFold/pull/868#issuecomment-6703416437):
- **N1 is closed.** The two declared noise models (`replica`, and `replica+seed` with δ′δ′ᵀ/2) are each unbiased in
  their own regime, by simulation, and a class is read only where both agree.
- **The R4 power arithmetic is confirmed.** "Differs" needs a step of at least 14.7 %, against the published
  step-ratio σ of 4.28 %.
- **Tests:** 51 tests OK, and 34 of 34 mutants killed.

## Rulings

1. **The design is bound as declared at M:**
   - the estimator is E_R, through RE-2 part B J8's existing period rows, with the refined control reproducing E_R to
     7.46e-12;
   - N = 10 replicas, and no E_U arm;
   - readings R1–R5, with R5 (A+B+C against A+C, exposure-weighted) primary;
   - the |z| bars, the eight controls, and §-licences in which no outcome names a cause or which period is right.
2. **The price is 0 node-h,** login-node steps only, `nice -n 19`.
3. **The steps are two connects:**
   - **Connect 1, the environment receipt:** the suite in root_6_28 / Python 3.11 on the pinned copy, plus a
     `load_all` smoke test on one real product's copy. Its receipt is committed as a PR.
   - **Connect 2, the read:** the cov2d fence check, then `copy` and `verify` as separate steps, then `read`. It runs
     only after connect 1's receipt reports PASS.

   Two connects, so that an environment failure can't be confused with a reading. Each connect's sha256 comes to the
   director before launch, from a fresh clone at M with empty porcelain. ssh's rc is read unpiped, and inputs are read
   through O_NOATIME.
4. **The report** is an outcome record with the readings and their licences. Any wording for the note or the paper
   comes later, through a referee read and Joseph.

Nothing is submitted, deposited or tagged.
