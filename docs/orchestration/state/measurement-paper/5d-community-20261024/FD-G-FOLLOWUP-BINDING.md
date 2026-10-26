# Binding: G-FOLLOWUP, the R04 look and the correlation sensitivity of Stage G's χ² (2026-10-26)

**By** the paper-tighten lane, as director.

**Under:**
- Joseph's approval: `DECISION-20261026-joseph-fps-scope-r04-sensitivity-and-tex-reflow.md` §2 (PR #387);
- Stage G (`FD-G-REPORT.md`, PR #378) and G-DIAG (`FD-G-DIAG-REPORT.md`, PR #383).

**Binds** [`FD-G-FOLLOWUP-DECLARATION.md`](FD-G-FOLLOWUP-DECLARATION.md) with its amendment 1, merged in PR #388. Its file
sha256 begins `7fd1c8075fd16d38`.

**MEASURES:** nothing. It authorizes the declaration's deploy and its one run, at 0 node-h on a login node.

**CANNOT AUTHORIZE:**
- a change to the reported covariance, C_resp, κ, any cell or the Stage G readout;
- a p value on any shrunk comparison;
- a claim, a reading or printed wording, which are Joseph's;
- any Slurm job, GPU use, premium QOS or write to CFS.

## 1. The bound code

**The deploy pin** is `02bf756a453e52b2e96dc31bd6d3ebc34f4e0842`, main after PR #388.
- `B=/pscratch/sd/j/josephrb/fd-g-followup-20261026` and `D=$B/deploy/02bf756a`.

**At the PR head `2308fc81`, the director checked:**
- the §8 pins: `fd_g_followup.py` `820b67c2`, `test_fd_g_followup.py` `6697e63d`, `fd_g_diag.py` `241bfd02`;
- the declared test modules, locally with `-B`: **Ran 148 tests, OK**.

`fd_g_followup.py` and the declaration have the same digests at `main`.

## 2. Rulings

All fifteen §7 items are as relayed on 2026-10-26 and recorded in the declaration's amendment 1. Two of them changed
the code:
1. **The cells** are R04, R00, R01, R07, R08, R09, R10 and R14, chosen from G-DIAG's committed modes before the run.
   R07 and R14 lie above p_∥ 4.5, so GiBUU is not compared on R04, R07 or R14.
2. **The second family** shrinks interaction, flux, detector and lateral jointly.
   - Normalization is a single scale shared by every cell. Its full correlation is structural, so it stays unchanged,
     with stat, seed, C_model, C_resp and V_g.
   - A test holds normalization bit-identical, and a planted defect shows the test fires when normalization is put
     back.

## 3. Conditions

1. **Deploy and tests,** exactly as declared, with `<pin>` = `02bf756a…`.
   - `$B` must not exist beforehand.
   - It must show HEAD equal to the pin, porcelain 0 before and after, the §8 digests, and "Ran 148 tests". Anything
     else is a STOP.
2. **The run,** with the declared argv exactly, after step 1.
   - Exit 0 proceeds. Any other exit is a STOP, reported unrepaired.
   - G-DIAG's D0–D5, F0, R1–R4 and S0–S2 are part of the run. S0 reproduces Stage G's reported χ² to a relative
     10⁻¹⁰.
3. **No step is rerun or repaired** without the director.
4. **The report is `FD-G-FOLLOWUP-REPORT.md`, opened as a PR to the director.** It gives numbers only, with every
   record carrying its label.
   - It states item 5's search limit.
   - It states that G-DIAG reproduces from its own deploy `d02ce2f2`.
   - The results index is regenerated in-branch under the standing ruling, if the readout enters the population.
5. **Ledger:** rows in `fd/LEDGER.tsv`.
6. **Retention:** `fd-g-followup-20261026` joins the pscratch retention list.

The steps may start once this record is on `main`.

## Not changed

- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
