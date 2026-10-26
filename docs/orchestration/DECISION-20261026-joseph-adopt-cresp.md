# DECISION 2026-10-26 — Joseph: adopt the species-response block C_resp into the 5D reported total

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- The C_resp readout is in `state/measurement-scoping/assigned-uncertainties/cresp/CRESP-REPORT.md` (PR #372,
  `cresp.json` `19bb2ee1…`, npz `4d8b5797…`).
- On R00–R15:
  - the summed C_resp has a median per-cell relative σ of 2.14 % (0.70–3.71 %);
  - C_total goes from 6.74 % to 7.29 %, with a σ ratio of 1.011–1.220 (median 1.048);
  - its trace share is 0.074.
- The director recommended adopting it as a named component, citing U-PLAN option 3 (PR #367) and the comparators'
  practice. The decision falls before any data-against-generator χ² on these cells (Stage G has not run).
  <!-- absence-ok: Stage G's run is gated on this record's binding; its absence is by construction of the order in DECISION-20261026-joseph-abstract-and-cresp-build.md item 3 -->

Joseph's answer, verbatim:

> yes adopt it

sha256 of the text plus a final newline begins `d635377666800be6`.

Joseph then asked:

> well, will it hurt the comparison with the minerva 2d publication?

sha256 of the text plus a final newline begins `166e4cc826df139e`.

The director answered no:
- C_resp is built on R00–R15 only and does not enter the 2D result or its covariance (`C-RESP-SPEC.md` §7).
- For 2D the block would be zero by construction. The 2D unfold reads only reconstructed p_T and p_∥
  (`2d-unfolding/unfold_2d_omnifold_unbinned.py:9`), and the selection reads no recoil. This is an inference from the
  code; no run has tested it.
- A larger 5D total can only ease the 5D-against-lower-dimension consistency checks.

## What is decided

1. **The 5D reported total on R00–R15 is C_total_resp = C_e + C_model,abs + C_resp,** with C_resp the summed block of
   proton, meson, EM and other at D1's sizes. Cross-talk is reported beside it and not summed. C_resp is a named
   component in the uncertainty breakdown.
   - **Where it is stated:** this record supersedes the "sensitivity variant, not adopted" labels of the C_resp
     records. Those records stay as they were written, and CRESP-REPORT.md gains a dated status line.
   - **What it covers:** what `C-RESP-SPEC.md` §7 states, and nothing more. The paper and the note state that scope
     when the 5D result is integrated.
2. **Stage G** reports its comparisons on C_total_resp + V_g as the adopted comparison. C_total + V_g, without C_resp,
   is reported beside it, labelled as the variant without the response block. The binding records that assignment.
3. **F0 consistency.** F0 graded the fake-data bias against C_total without C_resp. So that the fake-data table
   matches the reported uncertainty, the director has F0's grades recomputed against C_total_resp, as a declared
   addendum: 0 node-h, fake data only, F0's statistics and triggers unchanged.
   - Both sets are reported, each labelled with its matrix.
   - This does not reread the data against any generator.
4. **Preservation.** `cresp.npz` is not byte-reproducible, so it is copied to HPSS with hashverify and a retrieval
   check before Stage G runs.

## Not changed

- The 2D result and its covariance, C_model,5D, κ = 1, R00–R15, and the route decision.
- Claims and printed wording are Joseph's; integration of the 5D result is its own step.
- No GPU and no premium QOS. Nothing is written to CFS.
