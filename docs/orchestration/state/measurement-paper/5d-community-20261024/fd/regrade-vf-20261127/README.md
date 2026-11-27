# REGRADE-VF: the bias and fluctuation split under C_rep with C_e^infl (receipt, tier3-design, 2026-11-27)

**Under:** REGRADE-VF-DECLARATION.md rev 1 (sha256 `48e6f198712123c5bbdcb31e1a243ccb86048e3a97e078e6af115640b972d0b3`, merged to main in #1427 at a0c6c6bb before any
number existed), and the director's GO for one local run of `regrade_vf.py` at sha256 `01fa8ceb08b9e2abe5ded0456e4d9e392060c83e708119e3248602e99322b9a0` (head 9f71d70b).

**MEASURES:** the declaration's §3 quantities and §4 readings at the four held-out-tune evaluations.
**CANNOT AUTHORIZE:** any change to a reported covariance; any note or paper wording (rewrite-helper drafts, Joseph
approves); a coverage or calibration statement; a validated size of C_e^infl or of C_rep; a cause; a p-value.
**NOT CITABLE FOR:** a test of C_e^infl's size. The fluctuation term is partly fixed by construction (§5 of the
declaration, repeated below).

## The run

- One local run: `python3 -I -B regrade_vf.py --out run/regrade_vf.json` under `env -i`, BLAS threads 1,
  python 3.12.2 numpy 1.26.4, from 2026-11-27T11:11:07Z to 2026-11-27T11:11:09Z. 0 node-h; nothing on NERSC.
- Printed statuses: g18/minus2, g18/all, ar23/minus2 and ar23/all all `done`; rc 0; stderr empty.
- **The record** `run/regrade_vf.json` (sha256 `9f0e46e7a8d1149c00dd4b7b00dd12bc3d4af2b1b8c8f36f086a1b621c6b3541`) was committed at da3506c2 before any number in it was
  read. `run/SHA256SUMS` lists the run's files.

## Controls (declaration §6): every one passed

- C-PIN: every input and the imported `regrade_crep.py` matched its sha256 (`regrade_crep.py` is checked before it is
  imported).
- C-A0: `r_chi2(E, C_T, C_add(T))` reproduced `regrade16.json`'s six fields at every evaluation with relative
  difference 0.0 (bit-equal).
- C-F, C-DF: 0.0. C-L: the rule (ii) builder reproduced `vf_block.npz`'s C_e_infl and B5D's L to below 1e-15.
- C-GAP, C-PSD, C-RANK (ndf 16 everywhere) and C-ID held at every evaluation and matrix. The values are in the record's
  `controls` blocks.

**An undeclared added guard (disclosed; accepted by the director on 2026-11-27):** C-FINITE stops an evaluation if
any operand is empty or not finite, or if `r_chi2` divides by zero. It is stricter than the declaration and changes no
declared quantity or reading on finite inputs (agy recheck, `reads/read2-agy-recheck-report.txt` §2). It came from
read 1's fail-closed findings.

## The numbers (generated from the record; per ndf; N = 300; bootstrap 2,000)

B is the debiased bias term, F the fluctuation term, τ the response and run-period term; M_full = B + F + τ.

| evaluation | matrix | B ± SE_boot | F ± SE_boot | SE_boot(B − F) | τ | M_full ± SE | (M_full − 1)/SE | shares B / F / τ |
|---|---|---|---|---|---|---|---|---|
| g18/minus2 (primary) | rule (i), primary | 0.336 ± 0.015 | 0.438 ± 0.009 | 0.017 | 0.137 | 0.910 ± 0.018 | -5.1 | 0.37 / 0.48 / 0.15 |
| g18/minus2 (primary) | rule (ii) | 0.484 ± 0.019 | 0.564 ± 0.012 | 0.021 | 0.149 | 1.198 ± 0.024 | 8.2 | 0.40 / 0.47 / 0.12 |
| g18/minus2 (primary) | before (C′, no DeltaC_e) | 0.746 ± 0.030 | 0.895 ± 0.022 | 0.035 | 0.177 | 1.818 ± 0.041 | 20.2 | 0.41 / 0.49 / 0.10 |
| ar23/minus2 (primary) | rule (i), primary | 0.517 ± 0.018 | 0.424 ± 0.010 | 0.019 | 0.135 | 1.076 ± 0.022 | 3.5 | 0.48 / 0.39 / 0.13 |
| ar23/minus2 (primary) | rule (ii) | 0.739 ± 0.025 | 0.545 ± 0.014 | 0.026 | 0.146 | 1.430 ± 0.030 | 14.5 | 0.52 / 0.38 / 0.10 |
| ar23/minus2 (primary) | before (C′, no DeltaC_e) | 1.505 ± 0.049 | 0.867 ± 0.025 | 0.050 | 0.171 | 2.544 ± 0.059 | 26.2 | 0.59 / 0.34 / 0.07 |
| g18/all | rule (i), primary | 0.336 ± 0.015 | 0.440 ± 0.009 | 0.017 | 0.137 | 0.913 ± 0.018 | -4.8 | 0.37 / 0.48 / 0.15 |
| g18/all | rule (ii) | 0.486 ± 0.020 | 0.565 ± 0.012 | 0.022 | 0.149 | 1.200 ± 0.025 | 8.0 | 0.40 / 0.47 / 0.12 |
| g18/all | before (C′, no DeltaC_e) | 0.749 ± 0.031 | 0.898 ± 0.023 | 0.036 | 0.176 | 1.824 ± 0.042 | 19.6 | 0.41 / 0.49 / 0.10 |
| ar23/all | rule (i), primary | 0.516 ± 0.018 | 0.425 ± 0.010 | 0.019 | 0.135 | 1.077 ± 0.021 | 3.6 | 0.48 / 0.39 / 0.13 |
| ar23/all | rule (ii) | 0.737 ± 0.025 | 0.544 ± 0.013 | 0.026 | 0.146 | 1.427 ± 0.030 | 14.4 | 0.52 / 0.38 / 0.10 |
| ar23/all | before (C′, no DeltaC_e) | 1.505 ± 0.050 | 0.867 ± 0.023 | 0.050 | 0.171 | 2.543 ± 0.060 | 25.8 | 0.59 / 0.34 / 0.07 |

## The readings (declaration §4)

| evaluation | matrix | R-χ² | bias resolved | bias vs fluctuation |
|---|---|---|---|---|
| g18/minus2 | rule (i), primary | not shown | yes | fluctuation larger |
| g18/minus2 | rule (ii) | under-describes on average | yes | fluctuation larger |
| g18/minus2 | before (C′, no DeltaC_e) | under-describes on average | yes | fluctuation larger |
| ar23/minus2 | rule (i), primary | under-describes on average | yes | bias larger |
| ar23/minus2 | rule (ii) | under-describes on average | yes | bias larger |
| ar23/minus2 | before (C′, no DeltaC_e) | under-describes on average | yes | bias larger |
| g18/all | rule (i), primary | not shown | yes | fluctuation larger |
| g18/all | rule (ii) | under-describes on average | yes | fluctuation larger |
| g18/all | before (C′, no DeltaC_e) | under-describes on average | yes | fluctuation larger |
| ar23/all | rule (i), primary | under-describes on average | yes | bias larger |
| ar23/all | rule (ii) | under-describes on average | yes | bias larger |
| ar23/all | before (C′, no DeltaC_e) | under-describes on average | yes | bias larger |


**Carry-sensitive (declaration §4):** g18/minus2 and g18/all, in the R-χ² reading only. Under rule (i) the mean
χ²/ndf against C_rep is below 1 at G18 ("not shown"); under rule (ii) it is above 1 by more than 3 SE ("under-describes
on average"). At AR23 rules (i) and (ii) agree on every reading. The bias-resolved and bias-vs-fluctuation readings
agree between the two rules at all four evaluations.

**What the primary readings say (rule (i), g18/minus2 and ar23/minus2), descriptively:**
- The debiased bias term is resolved above zero at both tunes.
- At AR23 the bias term is larger than the fluctuation term; at G18 the fluctuation term is larger.
- R-χ²: "under-describes on average" at AR23 (by 3.5 SE, against a threshold of 3); "not shown" at G18.
- Against the pre-V_F matrix (before), C_e^infl lowers all three terms at every evaluation. The bias term falls by
  about two thirds at AR23 and about a half at G18.
- The `all` readings repeat the `minus2` readings; they share streams and are not independent.

## The circularity (declaration §5, unchanged)

These are the draws C_e^infl's factors were fitted to (B5D, spread only, from the centred errors). The bias term is a
fair reading of the mean error against the inflated matrix: its numerator ē never entered the factor, though the matrix
was scaled from the same draws' spread. The fluctuation term is partly fixed by construction, so its value below its
share is expected and is not a test of the matrix. None of this shows coverage or calibration of C_rep, or whether
the remaining excess is estimator bias or variance the draws do not contain (the laterals and normalization, C_model,
C_resp, the run period). A non-circular fluctuation check would need fresh pseudo-experiments at a truth the factor
never saw.

## Files

| file | what |
|---|---|
| `REGRADE-VF-DECLARATION.md` | the declaration (on main via #1427) |
| `regrade_vf.py`, `test_regrade_vf.py`, `mutants_regrade_vf.py` | driver, 100 tests, mutation runner |
| `receipts/tests.txt`, `receipts/mutation.txt` | 100 passed; 80/80 compiled mutants killed |
| `reads/read1-agy-*.txt` | read 1, agy gemini-4-hydrogen-xhigh (codex-school quota low; the director's fallback): NO-GO, all fixed |
| `reads/read2-agy-recheck-*.txt` | read 2, gemini-4-hydrogen-high: GO; N1–N3 fixed, N4 left (director: fine) |
| `run/` | the run: `regrade_vf.json`, stdout, stderr, rc, times, env, `SHA256SUMS` |
