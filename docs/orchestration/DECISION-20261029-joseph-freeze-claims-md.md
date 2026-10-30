# DECISION 2026-10-29 — Joseph: freeze CLAIMS.md; OI-53 retires as moot

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The close-items session's read-only packet ([`DECISION-PACKET-20261029-oi53-clm-row-ownership.md`](DECISION-PACKET-20261029-oi53-clm-row-ownership.md), PR #513) measured that
the twelve `CLM-001..012` rows' UNASSIGNED owner blocks nothing.
- The hook and CI pass with them unassigned.
- `CLAIMS.md` last changed on 2026-08-18, and its twelve detail files are already ARCHIVAL.
- Lanes A–D have not committed since 08-19.
- The note cites CLM-010 and CLM-012 for the frozen niter=3 policy, and CLM-001..008 are PET claims, with PET
  diagnostic only.

It offered three options: freeze `CLAIMS.md` (A), assign owners (B), or leave it (C).

The director asked:

> OI-53: what should happen to the twelve CLM-001..012 claim rows that have no owner?

Joseph's answer, verbatim, the only option he selected:

> Freeze CLAIMS.md (Recommended)

sha256 of the text plus a final newline begins `19bf209dd8aa8b89`.

## What is decided

1. **`CLAIMS.md` is frozen,** LIVE → ARCHIVAL in `MANIFEST-overrides.tsv`. The option offered read: "mark CLAIMS.md
   archival … The note's citations of CLM-010/012 still resolve, no owners are needed, and OI-53 retires as moot."
2. **The close-items session carries it out:**
   - the override change;
   - a dated header line in `CLAIMS.md`, if the archival convention allows one;
   - OI-53's retirement, citing this record.
   Every citation of a CLM row must still resolve afterwards.
3. **No claim's content changes.** Freezing records the rows as they stand.

## Not changed

- Every CLM row's text, every note citation, and every claim.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
