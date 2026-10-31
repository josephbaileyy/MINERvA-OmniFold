# DECISION 2026-10-31 (later) — Joseph: OI-51 retires; the director designates OI-137's statistics owner; UD-002 keeps 135 MeV

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- The close-items triage
  ([`RECORD-20261031-close-items-waiting-joseph-triage.md`](RECORD-20261031-close-items-waiting-joseph-triage.md), #594)
  left Q3 (OI-51) and Q6 (OI-137).
- The register PR (#596) found UD-002 in `USER-DECISIONS.md:24` still marked NEEDS JOSEPH on 135 against 139.57 MeV.

> OI-51: the August reply to Ben (about HPSS vs CFS headroom). Retire the row either way?

Joseph's answer, verbatim:

> Retire it (Recommended)

sha256 of the text plus a final newline begins `bdac7abc93ad9db8`.

> OI-137: a ruling assigns statistics work (per-block declarations for the adopted 5D covariance, no compute) to a 'statistics owner' role no session holds. May the director designate a session for it?

Joseph's answer, verbatim:

> Yes, designate one (Recommended)

sha256 of the text plus a final newline begins `1fa97d43de952918`.

> UD-002: keep 135 MeV as the defined constant in the E_avail definition (the paper already says 'a defined constant of 135 MeV'; the alternative was 139.57 MeV)?

Joseph's answer, verbatim:

> Keep 135 MeV (Recommended)

sha256 of the text plus a final newline begins `2f53fcc2fb3a1160`.

## What is decided

1. **OI-51 retires.** Its message was written against August's numbers. Any future HPSS headroom request, with about
   66 GiB left, would be a new one.
2. **The director designates OI-137's "scalar-5D adoption/statistics owner" (Ruling 7).** The work is item (v): a
   declaration for each block of the adopted 5D covariance, and a recommendation back to Joseph. It needs no compute.
   - The designation is the session `coverage-5b-audit`, which audited and added the run-period block. It takes the
     role once its current work closes.
   - The work is read-only and comes to Joseph as a recommendation.
3. **UD-002 is DECIDED: 135 MeV stays the defined constant** in the E_avail definition, as the paper prints it ("a
   defined constant of 135 MeV").
4. **The close-items session** makes the register changes, including UD-002 in `USER-DECISIONS.md`. It also corrects
   the stale "OI-50/OI-55" pointer sentences beside `USER-DECISIONS.md:37` and `SESSION-WORKFLOW.md:159`.

## Not changed

- Every number and claim. Nothing is submitted, deposited or tagged.
