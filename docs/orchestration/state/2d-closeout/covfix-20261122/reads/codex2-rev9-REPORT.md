<!-- absence-ok: verbatim third-party read report -->
NO-GO

<!-- absence-ok: verbatim third-party read report -->
Setting aside the iris receipt, PG session, and passphrase, rev 9 needs four changes before binding. I verified all 19 diff hunks against both Git blob IDs. Line numbers below refer to the rev 9 declaration. I checked the A1 digest strings in the declaration. The underlying A1 and lateral products were outside the supplied review files. [Rev 9 declaration](/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/codex2-covfix9/inputs/COVFIX-DECLARATION.md)

<!-- absence-ok: verbatim third-party read report -->
## Minimum changes before binding

<!-- absence-ok: verbatim third-party read report -->
1. **BLOCKING — Finish the \(K_B\) fallback.** Lines 800–804 define \(F_A\) when \(K_A\) is omitted, but lines 866–876 still take the cut comparison and residual modes from \(K_A\). Use \(F_A\) as the reference fluctuation block and \(F_A+C_{\rm model,abs}(x_R)\) wherever the reference total is needed. State which kept span enters each comparison. This makes the unfunded branch executable and preserves the accepted correction as the reference if \(K_A\) later fails P2.
2. **BLOCKING — Use the sampled covariance consistently.** Lines 949–957 introduce \(V_+\), while lines 904–911 still define the expected spread from the unprojected difference \(V_F-U\). Define the sole Gaussian law with \(V_+\). Compute each expected spread as the mean of \(u_i^\top V_+u_i/\lambda_i^F\) over the relevant modes, times \((N-1)/N\). Use that formula in the \(K_B\) fit and in grading. Have an unusable fit denominator refuse \(K_B\) construction, and handle a zero \(V_+\) before the factor check divides by its norm. Use \(V_+\) in the cutoff and descriptive stress formulas too. **Lines 806–811, 904–911, 933–935, 949–972.**
3. **BLOCKING — Verify the invocation that produced each unfold.** The jobs now hash the actual pseudo-data and complete output, but line 654 still calls for the *bound* invocation’s digest. A job can copy that digest while launching with a wrong argument. Hash the executable and resolved argument vector actually launched, then compare that digest with the expected invocation for the ID under the existing freeze. Apply the same check to the two central unfolds. **Lines 651–663, 894–897.**
4. **BLOCKING — Make refusal apply to the readings it affects.** `FAILS` now precedes `REFUSED`, which fixes the cross-truth case. At a single truth, §6.2 still refuses the candidate wholesale while §6.4 requires every valid reading to be graded. A failed reference sampler check can therefore still suppress a valid total deficit. Specify that carry failure invalidates the readings that need that carry, an invalid SE refuses its own reading, and a reference failure refuses the readings that need the failed reference. Keep the §6.2 controls mandatory for `VALIDATED` and let an independently valid total deficit trigger the challenge. **Lines 949–960, 987–1005, 1029–1034.**

<!-- absence-ok: verbatim third-party read report -->
## Disposition of the rev 8 findings

<!-- absence-ok: verbatim third-party read report -->
The numbered rows follow the rev 8 report. They also identify where its separate defect list and binding actions landed. [Rev 8 report](/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/codex2-covfix9/inputs/codex2-rev8-REPORT.md)

<!-- absence-ok: verbatim third-party read report -->
| Rev 8 item | Rev 9 disposition |
|---|---|
| 1. Drawn covariance and spectral map | **PARTLY CLOSED · BLOCKING.** The full-space \(L\), candidate-specific blocks, full-matrix PSD check, and factor reconstruction are specified. The expected-spread formula still conflicts with the sampled covariance. Apply change 2. **806–838, 904–911, 949–960.** |
| 2. Reference probabilities and cutoff error | **CLOSED.** The fixed cutoff recipe, conservative endpoints, and sentinels are specified. **929–945.** |
| 3. Grading guard | **PARTLY CLOSED · BLOCKING.** Zero or nonfinite SE now refuses a reading. The same-truth precedence issue needs change 4. **331–341, 987–1005.** |
| 4. P2 and PV budget | **PARTLY CLOSED · MAJOR.** The test and production roles enter the ledger. The test’s own advance reservation and the production-size repricing still need the fix below. **238–240, 359–367, 572–580, 669–671.** |
| 5. Custody and manifests | **PARTLY CLOSED · BLOCKING.** Actual file hashes, output rehashing, central unfolds, seal and freeze pinning, seed encoding, and the GPG handoff and integrity gate are in. Apply change 3 to finish the chain. **634–666, 727–756.** |
| 6. Spent once | **CLOSED.** Both amendment rules use the first spend of the real PV seal. The spend remains durable and keyed by the original seal and role. **243–247, 582–599.** |
| 7. ST1 and PX | **PARTLY CLOSED · BLOCKING.** W2 is counted once, and the guarded mean of ratios, row-specific acceptance inputs, and eligible-band requirement are specified. The unfunded construction sentence is fixed. Apply change 1 to finish the fallback. **481–490, 503–546, 800–804, 866–876, 1020–1024.** |
| 8. Reservations and completeness | **PARTLY CLOSED · MAJOR.** Unique intents, active and terminal reconciliation, and reservations during charge uncertainty are specified. One verified product per ID is required. Reconcile this rule with retries as described below. **562–580, 604–608, 651–658.** |
| 9. Outcomes | **PARTLY CLOSED · MAJOR.** The unfunded outcome and cross-truth precedence are corrected. The incomplete-PV row still needs the fix below. Same-truth validity is covered by change 4. **987–1005, 1017–1049.** |
| 10. Toy law and A1 evidence | **CLOSED.** The full A1 digests are stated, the lateral products are designated for digest pinning at binding, and nominal rounding has a preflight. **431–445, 462–468, 618–625.** |
| 11. Retained-space conventions | **PARTLY CLOSED · MAJOR.** Construction and grading share a band-edge convention. The sign rule leaves the basis within an exactly tied eigenspace unspecified. Apply the basis fix below. **823–827, 924–926, 932–938.** |
| 12. Benchmark wording | **CLOSED.** The benchmark states the 205-to-204 rank drop, and the old guarded-margin illustration is gone. **266–268, 1007–1011.** |

<!-- absence-ok: verbatim third-party read report -->
## Rev 9 regressions and remaining nonblocking fixes

<!-- absence-ok: verbatim third-party read report -->
The new binding defects are covered above. The \(V_+\) insertion leaves conflicting formulas, and the per-reading rewrite leaves the scope of a same-truth refusal ambiguous.

<!-- absence-ok: verbatim third-party read report -->
- **MAJOR — Give the synthetic test an advance reservation.** Line 573 prices the synthetic allocation from its own measurement, while the ledger requires a reservation before submission. Set a fixed reservation for that test under the existing cap. Use its measurements and the 600-toy workload to reprice the production writer and readout before PV. **Lines 564–580, 669–671.**
- **MAJOR — Count accepted attempts in the chain.** A failed attempt can leave a chain record before an authorized retry produces a second record for the same ID. Use the existing ledger to exclude failed attempts from the consumable chain, then require exactly one verified product per ID from accepted attempts. **Lines 571, 604–608, 651–658.**
- **MAJOR — Fix the basis for exact eigenvalue ties.** Sign-fixing `eigh` output leaves rotations inside a tied eigenspace possible, and those rotations can change per-mode flags. Bind a canonical basis for exact ties, for example by projecting the ordered cell axes into the tied eigenspace and orthonormalizing in that order. **Lines 823–827, 932–938.**
- **MAJOR — Route every terminal stop before complete PV grades.** The revised ungraded rule covers integrity failures after PV starts, while ST5 can also terminate PV after exhausted retries. Make the ungraded condition cover every terminal stop before complete grades and rename the table row `none, PV ungraded`. **Lines 601–608, 1035–1036, 1049.**
- **MAJOR — Finalize grades before descriptive stress work.** The readout currently runs stress work before grading. Persist the verified grades after the required checks and scans, then run the descriptive work and report failed scenarios as omitted. **Lines 574, 660–666, 962–974.**
- **MINOR — Delete stale wording.** Remove “or k” from the P2 selection sentence and delete the reference to “size statements” in §6.5. The D1 zero-bias condition, D3 denominator guard, and omission rule are already fixed. **Lines 786–788, 967–974, 1007–1011.**