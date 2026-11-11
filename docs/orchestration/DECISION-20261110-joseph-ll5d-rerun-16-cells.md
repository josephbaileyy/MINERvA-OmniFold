# DECISION 2026-11-10 — Joseph: after the vi defect is fixed, the LL5D gates rerun on the sixteen reporting cells; a merged-cell LL5D run is conditional and later

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **Both LL5D gates STOPped** (jobs 61040163 and 61040235; receipts #1013 and #1014). Every reading was overridden to option (3) by fd_1b_c2's mismatch bound, because c2_vi reported 100 % of rows unmatched.
- **The diagnosis** (#1015) classifies this as an implementation defect, not a measured mismatch. vi keys rows on coordinates and weight together, and the two sides store the weight at different precisions (float64 and float32), so no key can match. It was reproduced locally with its controls. The fix is being drafted as amendment A1a.2.
- **The V-HALF-R rebinning draft** (#1016) asked which cells an LL5D rerun should test: (i) the 16 cells, (ii) merged cells, or (iii) both. An independent consult (codex-school gpt-6-astra, high, at `dec8b86c`; committed with #1016) recommended (i) now, with a merged run conditional and later. The director recommended the same.

## Joseph's answer, verbatim

> yes I agree

The director's question was whether the LL5D rerun after the precision fix should test the 16 cells the paper reports. The sha256 of the text plus a final newline begins `be0aac0f92f1ecb8`.

## What is decided

1. **The LL5D gates rerun on R00–R15**, the sixteen reporting cells, once amendment A1a.2 is audited and bound.
   - This is Joseph's decision on the relaunch after the STOP, under LL5D binding 2 ruling 5. It authorizes that rerun and nothing beyond it.
   - Its connect comes to the director with its sha256, as usual.
   - The price is about 22 node-h for the two gates, from the 2026-11-10 measured times, plus a calibration rerun if A1a.2 requires one. It stays inside LL5D's 148.0 node-h cap.
2. **A merged-cell LL5D run** is conditional. It is considered only if V-HALF-R is declared, bound and run, and only if a scientifically useful merged candidate survives. It would then carry separate claims and a declared comparison, with no selection of whichever passes. It needs its own decision.
3. **LL5D does not wait on rebinning.**

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the rerun's cell set and its authorization after A1a.2.
- **Not citable for:** any coverage result; any rebinning decision; the cause of the STOP beyond #1015's diagnosis.

Nothing is submitted, deposited or tagged.
