# DIRECTOR REVIEW: 1B gate-D investigation, I0 and I2 reports (2026-11-01)

**By** the paper-tighten lane, as director.

**Reviews** [`FD-1B-INV-I0-REPORT.md`](FD-1B-INV-I0-REPORT.md), #645 (merged at `fdd8fb8b`), and
[`FD-1B-INV-I2-REPORT.md`](FD-1B-INV-I2-REPORT.md), #650 (merged at `da277773`, head `1cd16cab`). Both ran under
[`FD-1B-INV-BINDING.md`](FD-1B-INV-BINDING.md) (#644).

## 1. What the director re-derived

- **The readout's digest.** `fd/receipts-1b/inv/i2/i2.json` has sha256 `a9d3dc9c…`, the same as report §1.
- **The factors and attributions.** From that file's E, M, A, B and C per cell, recomputed outside `fd_1b_inv.py`:
  - √(E/M), F_src, F_prior and F_truth, per cell;
  - the attribution, by the dominant same-side out-of-window factor.
- **The result.** 14 H1, 1 H3 (R05), 0 H4 and 0 unresolved, with R06 in the window.
  - This equals the readout's `attribution` and `headline` in every cell.
  - Median F_prior is 2.72, and median √(B/M) is 1.654.
- **The audit.** `coverage-5b-audit` reproduced the same numbers independently on #650. Its R1 (H1's additivity
  prediction failed at the group level) is in the report's headline.

## 2. Ruling on the two routing deviations (report §1.1)

**The deviations.** In both, the report reached the director but not `coverage-5b-audit` before the next submission.

**Accepted as recorded deviations.** They change no number and no route:
- I0's REJECTED-in-every-cell sent the run to I2 under the declaration.
- `walls` PASS was the binding's own trigger for the bulk.
- The director had each report before each submission and raised no objection.

**From now on,** the audit receives each report before the next submission, not in parallel.

## 3. The independent consult

**The consult.** A fresh Sonnet session (not sol) reviewed both reports, the declaration, the binding, the stage-2
report and the paper's description, read-only. Its prompt and answer are verbatim in `FD-1B-INV-I2-CONSULT-PROMPT.txt`
and `FD-1B-INV-I2-CONSULT-ANSWER.txt`.

**The director agrees with its readings:**
- **O1 is a statement about the test.** It neither validates nor undermines the reported block. The coverage
  qualification stays.
- **The R00 and R05 caveat.** The interaction group carries only 0.57 and 0.36 of ρ²−1 there, so gate D's departure
  in those two cells is not explained by this investigation.
- **The labels overstate the data.** "F_prior" and "prior part" name the ratio √(B/A), which involves no prior, now
  that additivity has failed. "A ≈ C" overstates it: A lies 0.59 σ_A from C, with C/A median 0.48 and range 0.16–1.39.
- **"H3 refuted as the account"** is a statement about rule I2's attribution count. It is not a statement that the
  truth dependence is small. F_truth is outside the window in 15 of 16 cells.
- **Condition (a)'s question to Joseph** (var(r) against C_model) rests on the first-order algebra s ≈ −r + p, which
  I2 did not show. It goes to Joseph with that caveat and with both recommendations.

**The bound record stands.** These readings narrow how the result is quoted. They do not change the bound reading
"H1 → O1". The report stays as merged, and any later citation of it uses the wording above.

Nothing is submitted, deposited or tagged.
