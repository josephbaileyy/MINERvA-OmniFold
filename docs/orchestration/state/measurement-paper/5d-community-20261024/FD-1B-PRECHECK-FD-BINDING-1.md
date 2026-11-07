# BINDING: 1B pre-check, Part 1, the flux and detector groups (director, 2026-11-07)

**Binds** [`FD-1B-PRECHECK-FD-DECLARATION.md`](FD-1B-PRECHECK-FD-DECLARATION.md) and its code, as merged in PR #861 at
**M = `ed8f328fab52122112f54850d0078d79e81834c5`**. The module is `nd-unfolding/fd_1b_precheck_fd.py` (blob sha256
`7c3ffe86…`), with the tests in `nd-unfolding/tests/test_fd_1b_precheck_fd.py`.

**Under:**
- `DECISION-20261106-joseph-diagnoses-jinst-corrections.md` item 1.2, the coverage pre-check cause as a diagnosis only;
- the director's scope ruling of 2026-11-06: Part 0 (#858) first, then Part 1 for the flux and detector groups, with
  the additivity residual and the truth-dependence study excluded.

## What the director checked

- **The audit.** coverage-5b-audit's design GO, then its code GO at `ed8f328f`
  (https://github.com/josephbaileyy/MINERvA-OmniFold/pull/861#issuecomment-6700983511):
  - 16 of 16 of its single-site mutants killed;
  - the lane's receipt reproduces at 52 of 52, at three hash seeds;
  - the module unchanged since `7c3ffe86`;
  - its D1 text as ruled: F_truth is an attribution operand only, not studied.
- **The tests.** At M, the director ran `tests/test_fd_1b_precheck_fd.py` from a `git archive` of M (`-B`, own TMPDIR):
  42 passed.
- **The §2.1 flux key** is confirmed by the audit at 869dc269: A takes Φ_u, and B and Dnom take Φ_CV, each recorded in
  every product.

## Rulings

1. **The design is bound as declared at M:** rules S, F and K, the noise class, HF2 descriptive only, and §4.6's
   licences with D1's narrowing. In every outcome, 1B's rule (iii) and every earlier record stand.
2. **The steps and the price** are bound as in §7:
   - **P2, the pilot:** 8 items, 01:00:00, 1.0 node-h reserved. Its walls gate is read by coverage-5b-audit before
     the bulk.
   - **P3, the bulk:** 7 jobs at 02:30:00.
   - **The cap is 18.5 node-h,** with about 9.6 expected. `iris` is read before P2 and before P3.
   - A REPRICE from the pilot comes back to the director.
3. **The reads** follow §6:
   - staged O_NOATIME copies of the derivation and S1 products, the assembly, the constraint and the flux file;
   - the big inputs read in place by O_NOATIME, as I2's were;
   - a stat-only connect first;
   - staging gated on `cov2d_fence` logic exiting 0, which is now clear, with the result recorded.
4. **The order.** The earlier "after RPD-RECO's connect" is lifted: RPD-RECO is held on its own repair round, and the
   two don't share a resource. Part 1 may proceed now.
5. **Each connect** sends its sha256 to the director before launch, from a fresh clone at M with empty porcelain. ssh's
   rc is read unpiped, and each connect's receipt goes in as a PR.
6. **The report** gives the readings and the outcome per §4.6 with its licences, and the cost measured.

Nothing is submitted, deposited or tagged.
