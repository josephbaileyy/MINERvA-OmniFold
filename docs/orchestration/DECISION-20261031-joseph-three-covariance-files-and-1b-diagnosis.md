# DECISION 2026-10-31 (late) — Joseph: ship three covariance files; diagnose 1B's gate D, then fork

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- Two items were open: PR #619's abstracts, which carry the run-period block C_PL,5D, and 1B, stopped at gate D
  (`FD-1B-STAGE2-REPORT.md`, #618).
- An independent Sonnet referee read both
  (`state/2d-closeout/stageF/methods/secondary-results/sonnet-consult-abstracts-1b-20261031/`), and the director
  agreed with it on every point.
- Three questions went to Joseph.

> Supplemental Material: ship three covariance files (reported, without the run-period block, and the block alone), labelled and hashed, in the repo (not deposited)?

Joseph's answer, verbatim:

> Yes, three files (Recommended)

sha256 of the text plus a final newline begins `52fa683433897b04`.

> 1B after gate D: run the free diagnosis first, with a pre-set fork (localized cause → redesign the toys and rerun the gate; otherwise stop 1B)?

Joseph's answer, verbatim:

> Diagnose, then fork (Recommended)

sha256 of the text plus a final newline begins `2342e0c7d41b0f57`.

> The two new abstracts: approve them with the referee's additions (add 'coverage not validated' to the paper abstract; mention the run-period component with the without-block 7.29%; state the fake-data thresholds plainly; '8 degrees of freedom' for GiBUU)?

Joseph's answer, verbatim:

> how feasible is validating the coverage

sha256 of the text plus a final newline begins `5cae59ad1c8ca44e`.

## What is decided

1. **The Supplemental Material carries three covariance files,** each labelled and hashed:
   - the reported total, C_total + C_resp + C_PL,5D, marked as the reported matrix;
   - the total without the block, C_total + C_resp;
   - C_PL,5D on its own.

   They are built from the 5B addition's committed products (`fd/with-cpl/data-product/`), with a README that says
   the files differ only by C_PL,5D. They stay in the repository. Nothing is deposited: release stays Joseph's.
2. **1B: a diagnosis of gate D at 0 node-h, then a fork fixed before any number is read.**
   - **Where:** a login node, from the 176 derivation products and S1's npz already on pscratch. No job runs.
   - **What:** per-band ratios within the interaction group; the raw shifts without the diag(f/x_T) carry; f/x_T
     against ρ_c per cell.
   - **First,** a declaration fixes the readouts, what counts as a localized cause, and a time-box. The director
     binds it before any of these numbers is read.
   - **The fork:**
     - a localized cause (named bands, or the carry) leads to an amendment that redesigns the toys and reruns gate D,
       declared, priced and bound;
     - otherwise, 1B stops.
   - **The [0.9, 1.1] window is not relaxed.**
   - **Disclosure:** the paper and note disclose the stopped attempt in every outcome. The matrix 1B tests stays the
     one without the run-period block, as its declaration fixed.
3. **The abstracts are not yet decided.** Joseph asked how feasible it is to validate coverage. The director
   answered:
   - no study can make the intervals cover at the GiBUU-like and q3-tilt truths, where the bias already exceeds the
     uncertainty;
   - 1B's best outcome is "no undercoverage detected at the study's sensitivity" at two GENIE v3 truths
     (`FD-1B-DECLARATION.md` §5.2);
   - a nested design costs about 1,800 node-h per truth (`LIMITATION-PLAN.md`).

   <!-- absence-ok: quotes the proposed abstract sentence; the sources for it are the 1B declaration and report cited above -->
   So "the coverage of the reported intervals has not been validated" holds in every outcome. The abstract question
   is put to Joseph again.

## Not changed

- The reported covariance, every number, and PR #619's text until Joseph approves whole abstracts.
- The 1B protocol, its windows and its matrix. Nothing is submitted, deposited or tagged.
