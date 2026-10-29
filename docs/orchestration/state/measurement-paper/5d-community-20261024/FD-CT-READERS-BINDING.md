# Binding: the cheap tier's login-node readers 3a, 4C and 5A (2026-10-28)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261028-joseph-d2-approved-and-cheap-tier.md`, item 2: the cheap tier "runs first … under the
standing approval for jobs under 12 h, declared and bound as usual".

**Binds** [`FD-CT-READERS-DECLARATION.md`](FD-CT-READERS-DECLARATION.md), merged in PR #478. Its file sha256 begins
`0571c97372df3f59`.

**MEASURES:** nothing. It authorizes the declaration's deploy, its tests and its three runs, `recoil`, `chi2` and
`period`, on a login node at 0 node-h.

**CANNOT AUTHORIZE:**
- any covariance component, or any change to the reported matrix C_total + C_resp, a cell, a readout or κ. Every
  readout is printed beside the reported matrix, not in it, and adoption is Joseph's;
- a coverage, calibration or χ²-distribution statement, a p value or a tail fraction;
- a claim, a reading or printed wording, which are Joseph's;
- any Slurm job, GPU use, premium QOS or write to CFS;
- 3b, 5B, 1B or 4B, which have their own declarations or decisions.

## 1. The bound code

**The deploy pin** is `28ea789edd8e0211ac95d57957ba01b06380c862`, main after PR #478.
- `B=/pscratch/sd/j/josephrb/fd-ct-readers-20261028` and `D=$B/deploy/28ea789e`.

**At the PR head `bc09fdb1`, the director checked:**
- the §8 pins, all six: `fd_ct_readers.py` `cccc47aa`, `test_fd_ct_readers.py` `c68d412a`, `fd_f0_regrade.py`
  `0dfa722c`, `s1_assemble.py` `b157250a`, `s5p_stage1_inspect.py` `26569afc`, `h2_definition.json` `b6790761`. The
  last four are unchanged from the merge base. The PR's `nd-unfolding/` diff is the two new files only;
- the declared deploy set, locally with `-B` and a TMPDIR: **Ran 150 tests, OK**, rc 0, with 0 porcelain lines
  (including ignored files) after;
- on `main` after the merge, `fd_ct_readers.py` still `cccc47aa` and the declaration still `0571c973`.

## 2. Rulings on §7

1. **3a's reference is `rrzero`,** as declared. The shifts are W2b's own. σ/f uses S1's f, and the report says so
   beside |d|/σ.
2. **4C's primary weighting is the ν-e + IMD constraint weight,** F0's row-5 estimator. The unweighted values are
   written beside it.
3. **4C's matrices are (C_total + C_resp)/(f fᵀ) without V_g, and C_e/(f fᵀ).** No pair is added.
4. **4C writes no p value and no tail fraction,** with the key-allowlist test that enforces it, as the 3D binding ruled.
5. **4C's width ratio stays,** labelled descriptive. It is the per-cell form of the spread, not a calibration.
6. **5A's primary weighting is the central value,** with MnvTune v1's prior written beside it as the declared
   sensitivity.
   - The reason holds: 2D's own construction used x = E_U, the data, and the projection averages over the pooled
     result's content.
   - The timing is accepted as declared: the choice was made before any real 5A quantity existed, and only binning and
     the committed e_X were read.
   - The report states that this departs from the addendum's "the cell's prior weight" (§5.2), and why.
7. **The support rule and the 0.10 threshold are accepted,** fixed here before any value is read. R08–R11's footprint
   loss is reported per cell, as u_R for the prior and as the extrapolated labels for both weightings.
8. **Each readout is printed beside the reported matrix, never as a component** (addendum §5.4).
9. **u_R is written for the prior only.** The central value's u_R is a partial data integral of the X/f − 1 form and is
   not written; its extrapolated labels are.
10. **3a's in-span fraction is written in relative units,** with rank/16 beside it and the unit dependence stated in
    its label.

## 3. Conditions

1. **Deploy and tests,** exactly as §2.1, with `<pin>` = `28ea789edd8e0211ac95d57957ba01b06380c862`.
   - `$B` must not exist beforehand.
   - It must show HEAD equal to the pin, 0 porcelain lines before and after, the §8 digests, `tests rc=0` and
     "Ran 150 tests". Anything else is a STOP.
2. **The three runs,** with §2.2's argv exactly, in its order and under its timeouts (75 s, 375 s, 75 s). Exit 0
   proceeds. Any other exit is a STOP for that reader, reported unrepaired. As declared, a STOP in one does not stop the
   others.
3. **No step is rerun or repaired** without the director.
4. **The report is `FD-CT-READERS-REPORT.md`, opened as a PR to the director.** It gives numbers only, and every record
   with its label:
   - 3a: per cell, s₋, s₊, d and |d|/σ for C_resp and for C_total + C_resp, with the summaries; the quadratic forms, the
     in-span fraction with rank/16 beside it, and the curvature ratio. It labels 3a a data-side sensitivity at one
     coherent scale, not a mismatch closure and not a validation of C_resp;
   - 4C: per truth, matrix and cell set, the weighted and unweighted means and percentiles of both χ², beside
     χ²_ndf's; b̃'s own χ²; and the width-ratio summary. It restates §0's four disqualifiers beside the numbers, F0's
     failed offset control 7 first;
   - 5A: per weighting, σ/f of C_PL,16, S_ref,16 and C_total + C_resp, their ratio, the trace share, the rank, the
     extrapolated cells and the negative-weight counts; u_R for the prior. It labels C_PL,16 a size under an untested
     assumption that contains the observed offsets by construction, which only 5B can test;
     <!-- absence-ok: a label the report must print, restating the declaration's own scoping (FD-CT-READERS-DECLARATION.md section 0, 5A) -->
   - the ledger rows and the realized walls beside the projections;
   - no reading. The results index is regenerated in-branch under the standing ruling (a), if needed.
5. **Ledger** rows go in `fd/LEDGER.tsv`, as §9. **Retention:** `fd-ct-readers-20261028` joins the pscratch list.

The steps may start once this record is on `main`.

## Not changed

- Every covariance, cell, readout and κ, and the reported matrix C_total + C_resp.
- `docs/analysis-note/**`.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
