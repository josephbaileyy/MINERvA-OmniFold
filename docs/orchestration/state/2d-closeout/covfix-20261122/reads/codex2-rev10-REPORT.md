<!-- absence-ok: verbatim third-party read report -->
NO-GO

<!-- absence-ok: verbatim third-party read report -->
Setting aside the iris receipt, PG session, and passphrase, rev 10 needs two changes before binding. I verified all 17 diff hunks against both blob IDs. Line numbers refer to [the rev 10 declaration](/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/codex2-covfix10/inputs/COVFIX-DECLARATION.md).

<!-- absence-ok: verbatim third-party read report -->
## Minimum changes before binding

<!-- absence-ok: verbatim third-party read report -->
1. **BLOCKING — Finish the \(K_B\) fit refusal rule.** Lines 840–855 and 948–953 specify what to do with a nonpositive denominator, but a failed PSD check can leave \(V_+\) undefined before there is a denominator to test. The per-reading refusal in lines 997–1005 and 1032–1040 governs grading and leaves the construction decision implicit. For each ensemble included in a fitted band, require a successful carry and PSD projection of \(F_A-U\) with \(L=I\), and a finite, positive \(F_{\mathrm{exp},R}\). If any required input fails, omit \(K_B\). Keep the existing exclusion for bands with fewer than ten modes.
2. **BLOCKING — Complete PV before optional stress work.** Lines 697–700 persist grades before stress work but leave publication contingent on the scans. A timeout or crash during stress can still prevent the scan and publication after the readout role has been spent (lines 617–624). End the secret-bearing readout after cleanup, scans, and publication of the grades. Omit stress work from that job. Any descriptive follow-on must leave the published grade usable and require no reopening of the seal.

<!-- absence-ok: verbatim third-party read report -->
## Rev 9 findings in rev 10

<!-- absence-ok: verbatim third-party read report -->
| Rev 9 binding item | Disposition |
|---|---|
| 1. \(K_B\) fallback | **CLOSED.** \(F_A\) and \(K_{\rm ref}\) cover the unfunded branch and preserve an accepted correction as the reference if \(K_A\) fails P2. The diagnostic and residual rule use the two total matrices with their own fluctuation-based cuts. **834–838, 903–918.** |
| 2. Sampled covariance | **PARTLY CLOSED · BLOCKING.** The Gaussian law, expected spreads, cutoff draws, and zero-matrix check use \(V_+\). The fit failure path needs change 1. The remaining descriptive formulas need the minor edit below. **840–855, 948–953, 976–978, 992–1017.** |
| 3. Actual unfold invocation | **CLOSED.** The executable digest and resolved arguments actually launched are checked against the freeze, including for the central unfolds. **682–692.** |
| 4. Same-truth refusal scope | **CLOSED.** Carry, reference, and reading-specific failures have explicit scope. A valid total deficit survives a reference failure and takes precedence. **1032–1055.** |

<!-- absence-ok: verbatim third-party read report -->
The following rows use the inherited numbering from [the rev 9 report](/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/codex2-covfix10/inputs/codex2-rev9-REPORT.md).

<!-- absence-ok: verbatim third-party read report -->
| Inherited item | Disposition |
|---|---|
| 1. Drawn covariance and spectral map | **PARTLY CLOSED · BLOCKING.** The full-space map and projected-covariance formula are in place. Apply change 1. **840–875, 948–953, 992–1005.** |
| 2. Reference probabilities and cutoff error | **CLOSED.** The fixed draw recipe, conservative endpoints, and sentinels carry through. **973–988.** |
| 3. Grading guard | **CLOSED.** A zero or nonfinite SE refuses its own reading. Valid deficits take precedence. **351–358, 1032–1055.** |
| 4. P2 and PV budget | **CLOSED.** The synthetic test has a 2.0 node-h advance reservation. Its measurements reprice the production writer and readout for 600 toys before PV submission. **602–611, 702–705.** |
| 5. Custody and manifests | **CLOSED.** The actual-invocation check completes the requested chain under the existing custody model. **674–696, 784–790.** |
| 6. Spent once | **CLOSED.** The durable original-seal-and-role spend and the amendment deadline carry through. **263–267, 613–629.** |
| 7. ST1 and PX | **CLOSED.** W2 is counted once, the acceptance inputs and band requirement are fixed, and the unfunded branch has a usable reference. **532–565, 834–838, 903–918.** |
| 8. Reservations and completeness | **PARTLY CLOSED · MAJOR.** Rev 10 excludes failed attempts, but the declared chain tuple has no attempt identifier. Key each record by the ledger’s existing allocation job ID and apply the missing, extra, and mismatch checks to accepted records. **592–601, 683–691.** |
| 9. Outcomes | **CLOSED.** Every terminal stop before complete grades routes to `none, PV ungraded`, including exhausted retries. **635–639, 1079–1099.** |
| 10. Toy law and A1 evidence | **CLOSED.** The A1 digest strings, lateral pinning requirement, and nominal rounding preflight carry through. The underlying products were outside this review. **454–475, 491–498, 650–656.** |
| 11. Retained-space conventions | **PARTLY CLOSED · MAJOR.** Ordered-axis Gram–Schmidt supplies the basis for a tie, but “a degenerate cluster” also refers to the preceding near-tie band rule. Restrict basis rotation to equal eigenvalues in both grading eigensystems. Use the \(10^{-9}\) convention only for band assignment. **336–349, 856–864, 972–985.** |
| 12. Benchmark wording | **CLOSED.** The benchmark gives the 205-to-204 rank drop. The old guarded-margin illustration remains gone. **286–288, 1057–1061.** |

<!-- absence-ok: verbatim third-party read report -->
Of the six separate rev 9 follow-ups, the advance reservation, terminal-outcome routing, and stale P2 and §6.5 wording are **CLOSED** at lines **602–604, 1085–1099, 820–822, and 1057–1061**. Attempt filtering and tied bases are **PARTLY CLOSED · MAJOR** as above. Grade finalization before stress is **PARTLY CLOSED · BLOCKING** under change 2.

<!-- absence-ok: verbatim third-party read report -->
## Other rev 10 defects

<!-- absence-ok: verbatim third-party read report -->
- **MAJOR — ST6 has two different triggers.** Lines 417–422 can be read as a stop based on projected remaining phase costs, while lines 608–611 give an atomic reservation gate. The distinction matters because the starting full estimate already exceeds the ceiling. Replace lines 421–422 with a reference to the ledger gate at **409.22 node-h** and its director escalation. Keep the estimate in the price table and the separate PX repricing rule.
- **MINOR — Finish the reference notation cleanup.** D1 and D3 still share \(a=\operatorname{tr}(V^+V_{\rm drawn})/\mathrm{ndf}\), although the draws use \(V_+\). If the descriptive scenarios are retained, use \(V_+\) in that trace and in the whitening explanation. Delete the print instruction for \(u,u_R\), whose definitions were removed. **948–954, 976–978, 992–994, 1012–1017.**
- **MINOR — Update the live price summary.** Section 9 still gives the rev 9 estimate of 408.6–409.2 node-h. Point it to §3 for the current estimate and retain the explicit 409.22 node-h ceiling. **385–393, 1147–1150.**