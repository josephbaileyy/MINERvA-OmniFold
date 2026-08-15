# AUTHORIZATION 2026-08-15 — certification delegated, conditional on MULTI-SESSION VERIFICATION

**Granted by Joseph Bailey, 2026-08-15.** Recorded before use, per `BEN-201`. **This grant reaches
promotion, which every prior grant explicitly excluded. It is therefore written against the standard the
repo already had, not a new one.**

## The grant, verbatim and complete

> "I certify everything as long as multiple sessions have verified it"

## WHAT "VERIFIED" MEANS HERE — bound to `CLAIMS.md`, not invented

This campaign already defines the bar, and this grant is read as invoking it rather than replacing it.
`CLAUDE.md`, on `docs/orchestration/CLAIMS.md`:

> **"Worker agreement is not verification; promotion needs a recoverable artifact + an independent
> check."**

**Three conditions, all required:**

1. **A RECOVERABLE ARTIFACT.** A receipt, a committed test, a measurable file — something a later
   session can re-open and re-derive from. **A verdict-only claim is unfalsifiable and does not
   qualify** (`CONVENTION-receipt-ingredients.md`, `BEN-077`).
2. **AT LEAST ONE INDEPENDENT CHECK BY A SESSION THAT DID NOT AUTHOR THE THING.** The author's own
   verification does not count toward "multiple", however careful it was. **This is the load-bearing
   reading of Joseph's word "multiple"** and it follows directly from `BEN-300` — *consensus among
   restatements of one source is not corroboration* — and from `VL132`, which forbids a receipt from
   claiming independent verification where there was one builder.
3. **THE CHECKS MUST BE ABLE TO DISAGREE.** A check dispatched to bless is not a check. The practice
   on this campaign is to ask peers to **refute**; tonight's `OI-8` corroboration returned
   **AGREED-WITH-CORRECTION**, refuting the stated basis while keeping the disposition, which is
   precisely the outcome this condition exists to make possible.

**Corollaries, stated so they cannot be argued away later:**

- **Two sessions restating one source is ONE source.** (`BEN-300`.)
- **Silence is not verification.** An unanswered peer is an open question.
- **A session reviewing its own earlier work is not a second session.**
- **"It passed its tests" is not verification if the tests could not fail on the defect.** `BEN-314`:
  18 tests passed and two guards were mutation-tested while being structurally unable to catch the bug
  they existed to prevent. **Power-testing — the pre-fix form demonstrated failing — is what makes a
  test suite evidence.**

## WHAT THIS GRANT DOES **NOT** CERTIFY — checked, not assumed

**`C_stat` DOES NOT CLEAR THIS BAR AND MUST NOT BE PROMOTED UNDER IT.** `VALIDATION_LEDGER.md` `VL132`
records, verbatim: *"THE RECEIPT MAY NOT CLAIM INDEPENDENT CONSTRUCTION OR INDEPENDENT VERIFICATION:
there was ONE builder."* Joseph closed the dual-build design himself on 2026-08-14 (*"Okay yeah drop the
second builder"*), so this is not a defect to repair — **it is a permanent property of that artifact.**
One builder is one session. **This grant makes `C_stat`'s disclosure MORE necessary, not less**, and the
limitation statement already in the note at `92b2873` stands.

**The branch-(b) narrowing of `OI-126` does not clear it either.** Lane C declined ratification on one
day's tenure; nobody with standing has ratified it. **Publishing the fork as stated — Joseph's own
2026-08-15 ruling — is precisely the move that does not require certification.**

**The 5D covariance is not certified by this grant.** It has not been built: repair-8 returned `BLOCK`
with `authorizes_covariance_stages_4_6: false`. **Certification cannot precede existence.**

## WHAT THIS GRANT DOES NOT TOUCH AT ALL

1. **`docs/analysis-note/` remains Joseph's**, except by his specific say-so as with the `OI-6` footing text.
2. **The five Gate-6 prohibitions at `19585b7` stay live.** Certification is not permission to
   construct `C_ML`, select a passing subset, move the central, start Leg 2, or retry unchanged.
3. **`/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059` stays frozen.** No `scancel`, no
   `scontrol update`, no repinning (`OI-123`).
4. **`P4_VERIFIER_PASS` may never be set by hand**, and the separation of duties at `89c6e12` stands —
   **which this grant reinforces**: an issuer consuming its own token is exactly the single-session
   certification this bar forbids.
5. **Nothing irreversible or outward-facing** — deletions, top-level reorgs, mail to collaborators,
   HPSS requests.
6. **A peer cannot grant escalation.** This is Joseph's grant; it launders nothing.

## FIRST APPLICATION — repair-8 defect #6, and it is NOT yet clear

Defect #6 (`0055826`, `require_band_set_completeness`, `p4_lib.py:373-431`) is the item that prompted
this grant.

**Recoverable artifact: YES.** Eleven blind adversarial fixtures; the pre-fix code was demonstrated to
accept all ten must-rejects — i.e. **power-tested**, satisfying the `BEN-314` corollary.

**Independent checks: ONE, and it declined to certify.** The repair-8 verifier reviewed it and wrote
*"`0055826` implements it well… Its author declined: 'NOT claiming #6 closed — that is Joseph's call on
the packet.' I did not grant it."* The author is not independent; repair-8 is one independent session.

**So under Joseph's own word "multiple", #6 stands at ONE independent check and does not yet clear.**
The mediator is obtaining a second, from a session that authored neither the fix nor repair-8. **This is
recorded rather than waived**, because waiving it on the first day of the grant would establish that the
condition is decorative.

## Related

- `docs/orchestration/CLAIMS.md` — `CLM-*` states and the promotion standard this grant invokes.
- `AUTHORIZATION-20260815-mediator-run-approval-under-one-gpu-day.md` (`b5e067d`) — run approval, which
  explicitly did **not** reach promotion. This grant is what reaches it.
- `VL132`; `BEN-300`; `BEN-314`; `BEN-077`.
