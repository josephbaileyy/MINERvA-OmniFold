# BINDING 2: 1B staged method coverage, stage 1 (director, 2026-11-02)

**Binds** stage 1 of [`FD-1B-STAGED-DECLARATION.md`](FD-1B-STAGED-DECLARATION.md), revision 2 (#664). Its code is in
[`FD-1B-STAGED-AMENDMENT-1.md`](FD-1B-STAGED-AMENDMENT-1.md), revision 3. The amendment is bound as merged in PR #673
at **M2 = `24c83ab839647dd5113847f3de11447eecd9c10e`** (PR head `ea7e0b59`, a merge of revision 3's `b1b3a867` with main).

**Under:**
- `DECISION-20261101-joseph-1b-staged-method-coverage.md` (#663);
- binding 1 (#667), whose gate is met:
  - **Stage 0 passed rule K.** κ is in [0.9, 1.1] in 16 of 16 cells, from 0.9757 (R01) to 1.0570 (R08)
    (`FD-1B-STAGED-STAGE0-REPORT`, #679, merged `b1fba4e3`). The director read κ from the committed
    `stage0/readout.json`.
  - **The audit acknowledged #679** on the PR (issuecomment-6577256203 and -6577480462).
  - **Joseph has been told of the PASS**, in the director's report of 2026-11-02, before S1-0's submission.

## The code bound (git blob digests at M2)

| blob | path |
|---|---|
| `74aa8daced207af0ea8e3b5e0d3136e5535f76a1` | `nd-unfolding/fd_1b_mc.py` |
| `0b08d17384642a6382f2c8069bd29fa2b0ef123f` | `nd-unfolding/tests/test_fd_1b_mc.py` |
| `71ca615a67dfbd098852dd713677ad3179617ff6` | `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/stage1/tables/make_stage1_tables.py` |
| `6ca37839374afa3fdf1c43c0ed6e13039409cad9` | `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/mutation_mc.py` |
| `3004edbcf6112c6d9813459f6b51bc88b70a6d2f` | `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/mutation_mc.out` |
| `1810161d53c6b849d0dce7fb506d88d551d89900` | `nd-unfolding/fd_1b_null.py` |
| `31a88850a7999884150fef402fb0f22cba9005ed` | `nd-unfolding/fd_1b_moded.py` |

- `fd_1b_mc.py` has sha256 `1a2f825fe4a7…`, unchanged since revision 2. Its tests have `e786b4d95fdb…`, and the
  mutation receipt reads 79 of 79 killed. Both are revision 3's, as the audit acknowledged them.
- The other bound modules (`fd_1b_score`, `s1_assemble`, `fd_1b_toys`, `fd_1b_inv`, `fd_1b_moded`, `fd_1b_null`) are
  byte-identical to main.

## What the director checked

- **The digests.** The sha256 of `fd_1b_mc.py` at M2 is `1a2f825f…`, and its tests' sha256 at the PR head is `e786b4d9…`.
- **The tests.** At `b1b3a867`, with its own TMPDIR, `python3 -B -m pytest` ran `test_fd_1b_mc.py`, `test_fd_1b_moded.py`
  and `test_fd_1b_null.py`: 118 passed.
- **The audit.**
  - `coverage-5b-audit` acknowledged revision 3. It met C1 with tests and receipt only.
  - It reproduced 118 tests, its 44 applicable mutants and `mutation_mc` 79/79.
  - It confirmed the acknowledgement carries to the merge head (issuecomment-6581671778).
  - Its B1–B4 and D1 are resolved.
- **The order.** The amendment's §4 sets it: stage-flux and receipt, then S1-0, then the bulk after the audit's
  acknowledgement, then `n1`, `null` and `readout` per truth.

## Rulings (amendment §5)

1. **What is bound.** `fd_1b_mc.py` and its generator are stage 1's code. The rules, truths, draws, thresholds and
   grading are declaration revision 2's. The code, tests and receipt are amendment revision 3's. §2 (i)–(v) are
   accepted as construction findings.
2. **The plug-in truth is included.**
   - **What it is.** It captures the unfolding's final truth weights at S1's data result. It must reproduce S1's central
     product bitwise (control (b)).
   - **The caps:** S1-0 1.0 node-h, plus the bulk with the plug-in at 72.0 node-h (1,578 items on 9 one-node jobs of
     8:00:00), for **73.0 node-h**.
   - **What it adds:** a data-like truth for the coverage reading, and M′ against M for the truth dependence.
   - **The decision's "only if cheap"** is met: 24 node-h is about 2% of the half-balance (1,030 node-h at connect 25).
   - **The balance check.** The connect re-reads the balance before S1-0. If 73.0 exceeds half of it, it stops, and the
     campaign goes to Joseph.
3. **N1's stop rests on the composite.**
   - **What stops:** the receipt's exact pass over the 900 declared draws, and the `n1` step on the toys' own record.
   - The single-universe ratios are descriptive only. The bound stays at 10. The lane and the audit agree.
4. **The receipt's cap stays at 250,000 rows per array** (`N1_CANDIDATE_CAP`), because changing it would change the
   bound code.
   - A stop on the cap fails closed at 0 node-h, and is then an amendment.
   - The first pass's `all_draws_rows_above` is reported with it.
5. **Where the receipt runs:** on a login node at `nice 19`, under `/usr/bin/time -v`.
   - **The fallback is pre-authorized here.** If NERSC's login limits end the receipt, it may run once as one regular
     CPU job, at `-t 01:00:00` and ≤ 1.0 node-h, from the same deploy at M2.
   - That job is outside the 73.0 cap and is reported with its `sacct` cost.
6. **Order and routing.**
   - S1-0's connect script and submission line go to the director first.
   - The bulk waits for three things: `walls` PASS, every S1-0 control, and the audit's written acknowledgement of
     S1-0's readout.
   - The audit gets each report before the next submission.
7. **Connects:**
   - regular CPU only, every job under 12 h;
   - from a fresh clone detached at M2, with empty porcelain;
   - writes only under a new pscratch directory, nothing to CFS;
   - every read through O_NOATIME, with the widened stat lists of §4;
   - the HPSS copies after `hpssquota`, once maintenance clears, with stage 0's two tars first.
8. **I0's and I2's `load_s1` atime hole** goes into the stage-1 report as an erratum line. Their numbers are
   digest-checked and unaffected.
9. **Every outcome goes to Joseph,** with the paper text of declaration §12. No covariance is inflated without him.

Nothing is submitted, deposited or tagged.
