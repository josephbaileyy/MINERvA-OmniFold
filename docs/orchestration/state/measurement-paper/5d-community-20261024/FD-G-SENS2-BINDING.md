# Binding: G-SENS2, the per-group split of the correlation sensitivity (2026-10-26)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261026-joseph-gsens-per-group-split.md` (PR #393), item 2, and G-FOLLOWUP as bound and
reported (`FD-G-FOLLOWUP-BINDING.md`, PR #389; `FD-G-FOLLOWUP-REPORT.md`, PR #392).

**Binds** [`FD-G-SENS2-DECLARATION.md`](FD-G-SENS2-DECLARATION.md), merged in PR #395. Its file sha256 begins
`2d064532ea98f307`.

**MEASURES:** nothing. It authorizes the declaration's deploy and its one run (`--part sens2`), at 0 node-h on a
login node.

**CANNOT AUTHORIZE:**
- a re-run of G-FOLLOWUP (§7 item 4 is declined, below);
- any change to a covariance, cell or readout;
- a p value;
- a claim, a reading or printed wording, which are Joseph's;
- any Slurm job, GPU use, premium QOS or write to CFS.

## 1. The bound code

**The deploy pin** is `3ed50ed5ad88d151254af46d5dbd23c7f65df256`, main after PR #395.
- `B=/pscratch/sd/j/josephrb/fd-g-sens2-20261026` and `D=$B/deploy/3ed50ed5`.

**At the PR head `de5470c6`, the director checked:**
- the §8 pins: `fd_g_followup.py` `ec8cbc68`, `test_fd_g_followup.py` `f57c58b4`, `fd_g_diag.py` `241bfd02`;
- the declared test modules, locally with `-B`: **Ran 174 tests, OK**.

`fd_g_followup.py` has the same digest at `main`.

## 2. Rulings on §7

1. **Both readings of the shares are kept,** each with `flux_ratio`:
   - each matrix's own top mode;
   - α = 0's mode followed into α = 0.1, with `overlap_abs`.

   The followed mode answers the question as asked. The own mode shows when the leading direction changes.
2. **The two identity records** are accepted as declared.
3. **H0's tolerance** is accepted as declared.
4. **The byte-for-byte re-run of G-FOLLOWUP is declined.**
   - The synthetic identity on six trees and H0's two recomputed records cover the refactor.
   - A second real run could differ in the last bits on another login node, and would then stop the step with no
     defect behind it.
5. **Seed** is unchanged, as in G-FOLLOWUP.
6. **No family repeats G-FOLLOWUP's.** The report sets the three new families beside G-FOLLOWUP's two, citing
   `cd82517a`.
7. **`shrunk_group_lambda_min`** of about −2 × 10⁻¹⁸ for the rank-deficient groups at α = 0 is reported, with the
   reason beside it.
8. **The argparse message and `--help` changes** are accepted.

## 3. Conditions

1. **Deploy and tests,** exactly as declared, with `<pin>` = `3ed50ed5…`.
   - `$B` must not exist beforehand.
   - It must show HEAD equal to the pin, porcelain 0 before and after, the §8 digests, and "Ran 174 tests". Anything
     else is a STOP.
2. **The run,** with the declared argv exactly. Exit 0 proceeds; any other exit is a STOP, reported unrepaired.
   - D0–D5, H0–H2 and S0–S2 are part of the run.
3. **No step is rerun or repaired** without the director.
4. **The report is `FD-G-SENS2-REPORT.md`, opened as a PR to the director.** It gives numbers only, every record
   with its label, and rulings 1, 6 and 7 applied.
   - The results index is regenerated in-branch under the standing ruling, if needed.
   - If the readout names files the receipt gate cannot resolve, the symlink-companion ruling of G-FOLLOWUP applies.
5. **Ledger** rows go in `fd/LEDGER.tsv`. **Retention:** `fd-g-sens2-20261026` joins the pscratch list.

The steps may start once this record is on `main`.

## Not changed

- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
