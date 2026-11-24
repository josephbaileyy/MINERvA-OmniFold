<!-- absence-ok: verbatim third-party read report -->
GO

<!-- absence-ok: verbatim third-party read report -->
Rev 11 is ready to bind once the iris receipt, PG session, and passphrase are in place. **Blocking changes required: none.** The \(K_B\) fit now has an explicit refusal rule, and PV publishes verified grades before the separate stress job starts. I verified all 13 diff hunks against both Git blob IDs. Line numbers refer to the [rev 11 declaration](/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/codex2-covfix11/inputs/COVFIX-DECLARATION.md).

<!-- absence-ok: verbatim third-party read report -->
## Rev 10 findings in rev 11

<!-- absence-ok: verbatim third-party read report -->
The table follows the [rev 10 report](/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/codex2-covfix11/inputs/codex2-rev10-REPORT.md). Its numbered and follow-up items are combined where they concern the same rule.

<!-- absence-ok: verbatim third-party read report -->
| Rev 10 item | Rev 11 disposition |
|---|---|
| \(K_B\) fit refusal and full-space spectral map | **CLOSED.** Each required fit input needs a successful carry, a successful PSD projection with \(L=I\), and a finite positive band denominator. Failure omits \(K_B\). The fewer-than-ten-mode exclusion remains explicit. **857–875, 886–896.** |
| PV finalization before stress | **CLOSED.** The readout persists grades, cleans up, scans, and publishes. The seal-free stress job starts afterward. **709–717.** |
| \(K_B\) fallback and ST1/PX | **CLOSED.** The fallback and residual comparison use \(F_A\) and \(K_{\rm ref}\). W2 is counted once, and PX acceptance uses the fixed inputs and band rule. **548–579, 851–855, 924–939.** |
| Sampled covariance and reference notation | **PARTLY CLOSED · MINOR.** The fit, cutoff draws, and D1–D3 use \(V_+\), and the undefined diagnostics are gone. The whitening explanation still says \(W V_{\rm drawn}W^\top\). Replace it with \(W V_+W^\top\). **896, 969–975, 997–999, 1013–1022, 1033–1038.** |
| Actual unfold invocation | **CLOSED.** The chain checks the executable and resolved arguments actually launched, including for the central unfolds. **696–708.** |
| Same-truth refusal and grading guard | **CLOSED.** An invalid SE refuses its own reading. Reference failure preserves a valid total deficit, and `FAILS` comes first. **364–374, 1053–1076.** |
| Reference probabilities and cutoff error | **CLOSED.** The fixed draw recipe, conservative endpoints, and sentinels remain specified. **997–1009.** |
| P2/PV budget and advance reservation | **CLOSED.** The synthetic test reserves 2.0 node-h in advance. Its measurements reprice the production writer and readout for 600 toys before PV submission. **616–618, 720–722.** |
| Custody and manifests | **CLOSED.** The writer manifest, freeze and seal digests, and output chain carry through under the agreed custody model. **679–714, 797–817.** |
| Spent once | **CLOSED.** Consumption remains durable and keyed by the original seal and role. The amendment deadline is the first real seal spend. **275–280, 627–643.** |
| Reservations, completeness, and attempt filtering | **CLOSED.** The chain now carries the ledger allocation ID, limits checks to accepted attempts, and requires exactly one verified product per expected ID. **606–625, 649–653, 696–707.** |
| Retained-space conventions and tied bases | **CLOSED.** Basis rotation is restricted to exact ties. The \(10^{-9}\) convention governs band assignment only. **877–887.** |
| Terminal outcomes | **CLOSED.** Every terminal stop before complete PV grades routes to `none, PV ungraded`. **1062–1063, 1100–1107, 1120.** |
| Toy law and A1 evidence | **CLOSED.** The A1 digest strings, lateral pinning, and nominal rounding preflight carry through. The underlying products were outside this review. **468–489, 505–510, 663–677.** |
| Benchmark and stale P2/§6.5 wording | **CLOSED.** The benchmark gives the 205-to-204 rank drop, and the obsolete selection and rate wording is gone. **299–301, 837–839, 1078–1082.** |
| ST6 trigger and live price summary | **CLOSED.** The atomic ledger gate is the hard stop at 409.22 node-h. §9 points to §3 for the estimate. **427–437, 620–625, 1168–1172.** |

<!-- absence-ok: verbatim third-party read report -->
## New defects in rev 11

<!-- absence-ok: verbatim third-party read report -->
- **MAJOR — Budget the separate stress job.** The new job has no phase or reservation in the price table, while the ledger requires every submission to fit both a phase cap and the campaign ceiling. Assign the job to PV for accounting, give it a bounded reservation under ST3/ST6, and record stress as omitted if the gate refuses it after grade publication. **390–401, 606–625, 715–717.**
- **MAJOR — Specify the seal-free handoff.** The stress job names its inputs, but the readout contract specifies only a summary JSON. Have the stress job reconstruct \(D_u\) and \(V_+\) from the verified central outputs and frozen candidate arrays. Pin those inputs to the published grade record and mark scenarios with unavailable inputs as omitted. **640, 707–717, 1013–1039.**
- **MINOR — Put attempt filtering before chain validation in the procedure.** The new accepted-record rule governs, but the preceding sentence still tells the readout to compare “every record.” Tell it to select accepted records by ledger allocation ID first, then run the missing, extra, and mismatch checks on that set. **699–706.**