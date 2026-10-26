# DECISION 2026-10-26 — Joseph: approve the abstract change, and the build of the detector-response block C_resp

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The director put two items to Joseph:
1. **The abstract change** proposed in `state/2d-closeout/stageF/methods/r18/REPORT.md` ("For Joseph", item 1). One
   sentence moves from negative-first to measured-result form. No clause is removed.
2. **The species-response block C_resp** on R00–R15. This is option 3 of `state/measurement-scoping/assigned-uncertainties/U-PLAN.md`
   (PR #367), specified in `C-RESP-SPEC.md` (PR #365).
   - It is built on a login node at 0 node-h.
   - Joseph would see its per-cell size, and then decide whether it joins the reported total, before Stage G runs.
     The matrix is therefore never chosen after a data-against-generator comparison.

Joseph's answer, verbatim:

> yes I approve of the abstract change and you can build the detector response uncertainty

sha256 of the text plus a final newline begins `e44ee8cd05743f34`.

## What is decided

1. **The abstract change is approved,** as worded in r18's REPORT:
   - **from:** "Pseudo-experiments reveal background-subtraction bias, incomplete recovery of generator-sized truth
     changes, and statistical undercoverage at the tested truths";
   - **to:** "Pseudo-experiments measure a background-subtraction bias, a partial recovery of generator-sized truth
     changes, and statistical undercoverage at the tested truths".

   It lands as its own commit, with agy's agreement, a ledger row and the full build. No other abstract text changes.
2. **The C_resp build is approved:** once, as `C-RESP-SPEC.md` §6.2 gives it, under `state/measurement-scoping/assigned-uncertainties/C-RESP-BINDING.md`.
3. **The order:**
   - build;
   - readout committed;
   - Joseph decides whether C_resp joins the reported total;
   - Stage G's binding names the adopted matrix, with the other reported as a declared variant;
   - Stage G runs.

## Not changed

- No other abstract text, claim, `\pubhold`, data-availability or release text.
- No GPU and no premium QOS. Nothing is written to CFS.
