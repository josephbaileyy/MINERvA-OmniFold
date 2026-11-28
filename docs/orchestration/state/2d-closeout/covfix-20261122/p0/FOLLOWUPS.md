# COVFIX P0: follow-ups carried forward (cov2d, 2026-11-23)

These are the non-blocking items from P0's code reads (`reads/p0-r4-dispositions.md`, and earlier rounds where noted).
The director accepted them on 2026-11-23 for the P2/PV work, where `covfix_core` is reused. Each item is closed in the
P2/PV code chain, with its own test and mutant, or explicitly kept with a reason.

## covfix_core (reused by P2 and PV)

1. **evr refusal reasons.** The evr diagnostic should give a basis failure (a tied-space Gram–Schmidt refusal) a
   different refusal reason from an empty kept set, and report 0 only for an actual empty set. (codex-school2 r4 NB2)
2. **A portable tie regression.** The test of the tied-space rank order should inject an exactly tied eigensystem
   through `eig_basis`, so its assertion never skips on platforms where LAPACK does not return an exact tie. (codex r4
   NB3)
3. **evr subspace comparison.** For ranks whose exact-tie partitions differ, compare projectors over a common enclosing
   rank interval, in addition to listing the unmatched ranks. (codex r3 NB1, agy r4 NB1)
4. **The disclosed conventions.** Keep printing them, and state them in the P2/PV declarations' code notes:
   - GS_NULL = 100 ε, a relative null test;
   - OUTSIDE_SPAN = 1e-6, REGRADE's threshold, printed in the record;
   - asymmetry printed, not barred. (agy fresh-eyes NB1, NB2, NB4)

## Driver patterns, to copy into the P2/PV drivers

5. **A0's grader refusal.** Wrap the legacy grader call (`fd_1b_null.chi2_nonnull`) so a grader refusal becomes the
   named A0 STOP. Test it with a positive-definite covariance and an injected refusal. (codex r4 NB1)
6. **Input tests:**
   - a digest mismatch on an otherwise valid payload, for every pinned input;
   - a printed-not-barred frame mismatch that still completes;
   - the exact expected set of paths for the single-read spy. (codex r4 NB4)
7. **Receipts:**
   - excerpts of the producer lines for any laptop-copy digest (here, the G2R blocks);
   - mutation tracebacks kept, so a named fixture error can be told apart from a detection. (codex r4 NB5)
8. **Digests from receipts.** Consider parsing laptop-copy digests from their receipt files rather than repeating them
   as literals. (agy r3 NB1, r4 NB2)

## From the director's acceptance of P0 (2026-11-23, after #1268 merged at 7868a1f15)

9. **A band-wise subspace angle,** printed and read by nothing, in the P2/PV readout. P0 found the declared all-span
   reading trivially 0° at both tunes, because K0 carried and C_T each keep all 205 modes. The declared all-span angle
   stays as defined.
10. **The carry disclosure in the PV readout's §7 sentences.** P0 measured the carry approximation as material at the
    spent tunes:

    | tune | M under K0 carried | M under remade C_T |
    |---|---|---|
    | G18 | 21.7 | 24.2 |
    | AR23 | 19.1 | 16.5 |

    The R1 eigenvalue ratios average 1.6–1.7. Every §7 sentence the PV readout prints must carry §2's disclosure, that
    COVFIX tests "the reported covariance carried in relative form", not COV2D's remake.
