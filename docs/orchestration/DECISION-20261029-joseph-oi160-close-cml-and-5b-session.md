# DECISION 2026-10-29 — Joseph: OI-160 closes for C_stat, C_ML is checked the same way; 5B gets a fresh session

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **The OI-160 tolerance run** ([`state/oi160-tolerance-20261029/REPORT.md`](state/oi160-tolerance-20261029/REPORT.md),
  PR #506) read CORRECTED for all three producers of the 100 replicas behind `C_stat`.
  - Seeds 2, 3, 6, 40 and 85 were graded. The corrected code reproduced each stored replica to a maximum relative
    difference of 2.3 × 10⁻¹³ to 6.9 × 10⁻¹², against τ = 10⁻⁸. The old code missed each by 1.0.
  - The fresh same-code floor was 1.4 × 10⁻¹².
  - The ungraded seeds are covered by inference from their producer, and `55805463`'s verdict rests on one seed.
  - `C_ML` was out of scope.
- **The coverage session** asked for 5B to start in a fresh session, from its handoff (#505).

The director asked:

> OI-160 reads CORRECTED for all three producers. How should it close?

Joseph's answer, verbatim:

> Close; check C_ML too (Recommended)

sha256 of the text plus a final newline begins `372aff7f980a1cde`.

> 5B (the run-period cross-check, several days of development) needs a session. Will you open a fresh one from the coverage handoff (#505)?

Joseph's answer, verbatim:

> I'll open a fresh session (Recommended)

sha256 of the text plus a final newline begins `b7e1cac44165580b`.

## What is decided

1. **OI-160 closes for `C_stat`.** The trunk's `C_stat` rests on replicas written under the corrected seed contract,
   within the limits stated in its report. No change to `C_stat` follows.
2. **`C_ML` is checked the same way.**
   - The option offered read: "Run the same two-step check (bitwise, then tolerance) on the 24 seedscan_split replicas
     behind C_ML, about 0.5 node-h on CPU."
   - **The director's implementation note.** The first OI-160 run measured that the unfold is not bit-reproducible
     today (K1, about 10⁻¹³), so a bitwise step can only return VOID. The check is therefore run as one pre-declared
     tolerance run: τ is fixed in advance, and a fresh same-code floor control guards it. This is the second step of
     the two, the one that can decide. If Joseph wants the bitwise step run anyway, it is added by amendment.
   - The close-items session declares it and the director binds it, under the standing approval for jobs under 12 h:
     CPU only, no GPU, no write to CFS.
3. **5B starts in a fresh session that Joseph opens,** from `HANDOFF-20261029-coverage-session.md`. The current
   coverage session finishes 3b.

## Not changed

- `C_stat`, `C_ML`, the trunk, every receipt and product, and every published value.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
