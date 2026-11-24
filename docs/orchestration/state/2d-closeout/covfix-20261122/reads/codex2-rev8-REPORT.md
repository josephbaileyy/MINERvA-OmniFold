<!-- absence-ok: verbatim third-party read report -->
NO-GO

<!-- absence-ok: verbatim third-party read report -->
Rev 8 is not ready to bind with the iris receipt, PG session, and passphrase set aside. The unfunded PX branch leaves \(K_B\)’s reference undefined, the spectral map and Gaussian draw are underspecified, and the custody chain does not yet verify the files actually unfolded and graded.

<!-- absence-ok: verbatim third-party read report -->
I verified all 17 diff hunks in memory against both Git blob IDs. No files were modified. Line numbers refer to [COVFIX-DECLARATION.md](/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/codex2-covfix8/inputs/COVFIX-DECLARATION.md).

<!-- absence-ok: verbatim third-party read report -->
## Rev 7 dispositions

<!-- absence-ok: verbatim third-party read report -->
The numbering follows the rev 7 report’s “Rev 6 fixes” table. The findings below also cover its separate list of binding changes.

<!-- absence-ok: verbatim third-party read report -->
| Item | Disposition | Rev 8 lines and evidence |
|---|---|---|
| **1. Drawn covariance** | **PARTLY CLOSED · BLOCKING** | **764–774, 839–846, 883–892.** The single Gaussian law is in. The full-space map, candidate-specific constituent blocks, and covariance actually sampled still need binding. |
| **2. Reference probabilities and cutoff error** | **CLOSED** | **864–881, 913–914.** The retained cutoff recipe uses the Gaussian reference, conservative endpoints, and sentinels. The nonzero-bias wording is corrected. |
| **3. Grading guard and operating claims** | **PARTLY CLOSED · MAJOR** | **299–309, 894–934, 1026–1031.** Band SEs, sample SD, approximate guard coverage, and the descriptive stress runs are in. The new SE refusal has no assigned outcome. The old testability and operating-rate objections are resolved. |
| **4. P2 and PV budget** | **PARTLY CLOSED · MAJOR** | **333–336, 613–615, 814–826, 894–905.** The wrapper test triggers repricing. Its own allocation and the cost of the remaining work at production size are still unaccounted for. |
| **5. Custody and manifests** | **PARTLY CLOSED · BLOCKING** | **582–615, 671–703, 709–716.** Ciphertext-only publication, pinned GPG flags, scoped cleanup, and the cooperative assumption are in. Verification of the actual inputs and outputs, including the central unfolds, is incomplete. |
| **6. Spent once** | **PARTLY CLOSED · MAJOR** | **213–215, 535–550.** Durable spend, original-seal identity, terminal uncertainty, and the role retry exclusion are in. The amendment provisions still give different deadlines. |
| **7. ST1 and PX** | **PARTLY CLOSED · BLOCKING** | **447–455, 468–506, 736–742.** The band-level variance treatment and unfunded stop are in. Acceptance inputs and eligibility, the W2 accounting conflict, and the reference after an unaccepted correction remain. |
| **8. Reservations and completeness** | **PARTLY CLOSED · MAJOR** | **522–533, 553–560, 599–607.** The cap and all-toys rule are explicit. A job name and submit window do not establish unique intent identity or a final charge. Complete products still need verification by expected ID. |
| **9. Outcomes** | **PARTLY CLOSED · MAJOR** | **940–980.** The no-PV and no-challenge rows, per-candidate disclosure, and qualified `UNRESOLVED` wording are in. The new unfunded sentence implies that acceptance ran, and the new `REFUSED` precedence can hide a baseline challenge. |
| **10. Toy law and A1 evidence** | **PARTLY CLOSED · MAJOR** | **266–272, 399–413, 430–437, 564–580.** The P1/PV placement conflict is **closed**. Pin the actual lateral inputs and full A1 map digests, and make the nominal rounding preflight explicit. The supplied Part C report is empty, so the existing “named deformations” wording is appropriate. |
| **11. Retained-space conventions** | **PARTLY CLOSED · MAJOR** | **284–297, 757–774, 855–867, 1004–1008.** The bias diagnostic now uses one whitening frame. Band edges and individual-mode decisions still need a common tie convention. |
| **12. Benchmark wording** | **CLOSED** | **234–236, 930–934.** The rank drop is correctly described. The illustration that needed the guarded-margin label is gone. |

<!-- absence-ok: verbatim third-party read report -->
## New rev 8 defects

<!-- absence-ok: verbatim third-party read report -->
- **BLOCKING — The unfunded branch cannot build \(K_B\) as written.** ST1 says to omit \(K_A\) and continue with \(K_B\), but §5.2 defines \(F_A\), the cut comparison, and the residual reference through \(K_A\). Define the reference as the accepted corrected matrix when one exists and \(K_0\) otherwise. Use that reference throughout §5.2, even if an accepted \(K_A\) later fails P2. Give the unfunded finding its own sentence reporting the reproduced defect and that acceptance did not run. **Lines 480–483, 736–742, 801–812, 943–946.**
- **BLOCKING — The Gaussian covariance control can pass a wrong sampler.** C-PSD on a space selected for positive eigenvalues cannot detect negative modes outside it. The sample check sees only diagonal variances in that basis. A sampler with the same variances and wrong correlations can pass it and change the joint cutoff. Check C-PSD on the full carried matrix, specify treatment of tolerated negative and small positive eigenvalues, and verify that the actual sampling factor reconstructs the declared covariance within a fixed numerical tolerance. Use that covariance for \(F_{\rm exp}\), the cutoff draws, and the stress runs. The 0.05 check can remain a marginal sampling check. **Lines 839–846, 868–870, 883–892.**
- **MAJOR — `REFUSED` can erase an observed baseline challenge.** If \(K_0\) has a valid deficit at one truth and a refusal at the other, the first row of §6.4 makes Part 2 unchallenged. Derive the challenge from any valid per-truth \(K_0\) deficit and print any refusal alongside it. Route a refusal that prevents a required reading explicitly, including zero or nonfinite SE, and distinguish phase-terminal integrity failures from candidate-level refusals. Extend the ungraded row to cover PV that starts but ends without complete grades. **Lines 306, 553–560, 918–928, 951–970.**
- **MAJOR — The new chain can attest to an input the job never checked.** Copying the pseudo-data digest from the writer manifest does not verify the file passed to the unfold. Have the job hash the actual input and complete output, and record the expected truth and toy ID plus the bound invocation digest. Have the readout compare against the authenticated manifest and freeze, rehash the output it consumes, and require exactly one complete product per expected ID. Apply the same rule to the two central unfolds that determine \(D_u\). Pin the original PG seal at PG close and the freeze at P2, so both are available for the PV binding. This uses the single existing writer manifest. **Lines 584–607, 702–703, 829–832.**
- **MINOR — The descriptive and scope text still has gaps.** D1 lost its explicit zero-bias condition, and D3 lost the positive-denominator guard. Restore those two conditions and print undefined scenarios as omitted. Delete the remaining flag-size claim in prose while retaining the fixed cutoff recipe. Remove the live references to a \(k\) rule. **Lines 498–500, 725–729, 879–881, 899–905, 930–934.**

<!-- absence-ok: verbatim third-party read report -->
## Remaining minimum changes before binding

<!-- absence-ok: verbatim third-party read report -->
Apply the fixes above and close these surviving items.

<!-- absence-ok: verbatim third-party read report -->
1. **BLOCKING — Bind one spectral map and one block decomposition.** Use \(L=I+\sum_{R\ {\rm active}}(\sqrt{\phi_R}-1)P_R\) and delete the separate rank-wise “Applied” prescription. Use \(L=I\) for \(K_0\) and \(K_A\), with each candidate’s own constituents. If \(K_B\)’s fit targets the spread graded in P2 and PV, pool \(F_R/F_{{\rm exp},R}\) against the reference, with the finite-\(N\) correction applied once. **Lines 741–774, 839–846.**
2. **BLOCKING — Finish the funded PX acceptance rule.** Delete first-time W2 from the PX cost list. Before binding a funded correction, specify the reused or redrawn inputs for each firing row. Define the guarded quantity as the mean of the per-mode ratios, resolving the conflicting \(\bar A_R/\bar B\) notation. Require at least one eligible acceptance band and `covers` in every eligible band. **Lines 447–463, 468–506.**
3. **MAJOR — Close the remaining custody details in the existing wrapper.** Specify the seed-and-salt encoding and the stdin-to-GPG-fd-3 handoff. Require successful integrity verification before a decrypted product is used. Make the first spend for the real PV seal the deadline for the narrow executability exception, and use that deadline in both rules. **Lines 213–215, 535–550, 582–585, 671–697.**
4. **MAJOR — Make the existing cap and completeness rules executable.** Persist a unique intent before submitting. Reconcile it against active and terminal jobs, and retain its reservation while acceptance or final charge is uncertain. Require one verified complete product per expected P1 or PX ID. Reprice the synthetic allocation and the production-size writer and readout under the existing cap. Keep descriptive stress-run failures from blocking a completed grade. **Lines 328–361, 522–560, 613–615, 894–905.**
5. **MAJOR — Pin the toy inputs and mode conventions.** Bind the five lateral endpoint differences, their orientation and carry, and the full A1 map digests. Check the nominal rowwise rounding refusal before paid toy submission. Use one band-edge convention across construction and grading, with a deterministic basis for tied modes where individual flags decide a bar. **Lines 266–272, 284–297, 430–437, 570–575, 757–774, 864–878.**