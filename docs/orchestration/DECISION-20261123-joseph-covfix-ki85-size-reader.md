# DECISION 2026-11-23 — Joseph: the 2D covariance fix (COVFIX) supersedes KI 85's deferral, runs at full size as designed (two sealed tunes, N5 unconditional), and takes codex-school2 as its second reader

**Recorded by** the director. Joseph answered the director directly.

## What led to it

COVFIX is the 2D covariance fix that Joseph authorized for design on 2026-11-22, after an outside review's "Fix 1". Its
draft rev 4.1 is on branch `cov2d/covfix-decl-20261122` at `43b075c0a`, with declaration sha256 prefix `474dedb5`. §9 of
the draft names three decisions for Joseph:

1. **KI 85** (`KNOWN_ISSUES.md` row 85, OPEN, DEFERRED 2026-10-06) says:
   - the held-out-MC re-test is deferred until after the publication package and is not pre-registered;
   - no outcome changes the quoted band or any printed number before publication.

   COVFIX's cell N5 is that re-test, and its outcome A, a construction error found and fixed, would change a covariance.
2. **The campaign size.** As rev 4.1 has it, full and lean both validate on two sealed GENIE v3 tunes,
   G21_11b_00_000 and G18_02b_02_11b (G18_02a only as a fallback). These are the catalog's only model families distinct
   from the spent G18 and AR23. The sizes differ only in P1's toy counts. N5 runs unconditionally once KI 85 is
   superseded. Full is about 409 node-h at most and lean about 327. Only full is above half the balance (about 725.6
   node-h on 2026-11-22).
3. **A second independent reader.** Grok's credit is exhausted until 2026-11-27.

The director told Joseph:
- KI 85 is open, not done. The 2026-10-07 diagnostic was consistent with explanation (b): same-event pseudo-data
  under-scatter. Only the held-out-MC re-test separates (a) from (b).
- Superseding KI 85 allows a change. It does not commit any text to the paper: adoption of a covariance and every
  sentence about it stay Joseph's.

## Joseph's answers, verbatim

1. **Size.**
   - **First question.** The director first described the plan from its rev 0: "3 sealed validation tunes; N5 runs only
     if the nominal checks read off". Joseph chose "Full, N5 if triggered (Recommended)", sha256 prefix
     `23508f4e37721ebd`.
   - **The correction.** cov2d pointed out that rev 4.1 differs: two tunes, and N5 unconditional. The director
     corrected the description to Joseph and asked again.
   - **His re-confirmation,** the option he chose: "Full, as designed (Recommended)". The sha256 prefix is
     `afc0f0c8324e54b1`. **This answer governs.** The option read: "2 sealed tunes, full toy counts in the measurement
     phase, N5 always. About 409 node-h at most, the same total you approved."
2. **The second reader,** the option he chose: "Use codex-school2 (Recommended)". The sha256 begins `2fcd4885035d6386`.
3. **KI 85:**

   > supersede it but we could just do another zenodo release right?

   The sha256 begins `03cd6318ef7fdc32`. The director answered yes: Zenodo versions a record under one concept DOI, so
   a validated covariance change can go out as a new version, with the same tag, check and publish steps as the first.

## What this decides

1. **KI 85's two sentences are superseded for COVFIX.**
   - N5, the held-out-MC re-test, may be bound and run. Under rev 4.1 it runs unconditionally.
   - Outcome A may change the 2D covariance.
   - Any change enters the journal paper, or a later Zenodo version. The first Zenodo release is unaffected.
   - Adoption and wording remain Joseph's.
   - KI 85's row is updated to point here when N5 is bound.
2. **COVFIX runs at full size, as designed in rev 4.1.** That means two sealed validation tunes, full P1 toy counts, and
   N5 unconditional, at about 409 node-h at most. That is above half the balance, and Joseph has approved it. Each phase is still gated against its own cap from sacct, and
   the declaration's stop rules apply.
3. **codex-school2** is COVFIX's second independent reader for the declaration and its code reads, alongside agy, while
   Grok is out of credit.

Binding still requires the director's full read of the declaration and the other prerequisites in its §9: an iris
receipt, a fresh session for generating the validation tunes (PG), and the seal passphrase held by the director. No
compute runs before that binding.

**CITABLE FOR:** what Joseph decided. **NOT CITABLE FOR:** any result or coverage statement.
