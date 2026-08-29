# DECISION 2026-08-30 — Joseph: accept the forward-only rehearsal, at `7ac0edec`, delegated

**CITABLE FOR:** the acceptance of `PROPOSAL-20260830-forward-only-rehearsal.md`, its deployment pin,
and the delegation of the sequence.
**NOT CITABLE FOR** any claim that the F-17(b) chain is FIT, that Gate 2 has moved, that leg 6 or the
M(ii) family may run, or that a covariance is adopted. None of those changed.

## What Joseph said, and the exact shape of it

**READ THE PROVENANCE BEFORE CITING THIS.** Joseph did not type this into the repository. It arrived
through an interactive Claude Code session on 2026-08-30. **The scope wording below is this lane's
drafting, ratified by him — it must not be quoted as his words.** What is his is the decision.

He was asked three questions: approve the six-step sequence as a unit; which of two shas to deploy;
and whether the deployment and its new freeze are delegated or reserved to him. His words, verbatim:

> *"I approve the six-steps and do you recommendation for the sha. Also, the sequence can work
> without me in the loop"*

## The three answers, as this lane reads them

1. **The six-step sequence of §9 of the proposal is APPROVED as a unit.**
2. **The deployment pin is `7ac0edec`** — this lane's recommendation, taken. Measured 2026-08-30: the
   only paths differing between the proposal's `32e403b8` and `7ac0edec` are three `.md` files and
   `MANIFEST.tsv`, with **zero `.py` or `.sh`**. Since `mnv_source_manifest.py:70` sets
   `SOURCE_SUFFIXES = (".py", ".sh")`, the source listing digest is **identical at both shas**, so
   this choice changes no measurement. It only means the deployed tree also carries the F-1(b)
   producer filing and the family authorization as documentation.
3. **The deployment and its new freeze are DELEGATED**, alongside the per-arm compute already covered
   by the standing 500 GPU-h / 500 CPU-h delegation. This lane had read the deployment as reserved,
   because §7.0.19's authority was `DECISION-20260824-joseph-deployment-freeze-until-f1b.md`, a
   Joseph decision, and a deployment mutation is neither a PASS/BLOCK nor a per-arm compute call.
   **He has now ruled otherwise, and that ruling governs.** The codex-school Codex session may carry
   the whole sequence.

## The limit of "without me in the loop"

**This lane's drafting, and the place a future session is most likely to over-read this decision.**
The delegation is scoped to **this sequence, the one enumerated in §9 of the proposal.** It is not a
general grant. It does **not** reach:

- Gate 2's own PASS/BLOCK for the `aa67c426` rehearsal, which remains FAIL and can never PASS.
- **Leg 6, or the M(ii) family.** `DECISION-20260830-joseph-mii-family-and-leg6.md` authorized those,
  and they remain gated behind Gate 2 and behind one member completing end to end.
- `C_ML`, Gate-6 compute, covariance construction or adoption, or any publication claim.
- The decisions still recorded as Joseph's elsewhere — `OI-75`, `OI-71`, `OI-131(a)`, the cause-3
  discharge judgement, and publication adoption.

## The gate this decision does NOT lift

**Step 4 of the approved sequence is conditional and stays conditional.** Its own words are *"if and
only if all three pass, submit the seven bounded arms"* — the three being a fresh independent
full-chain **FIT**, the readiness confirmation, and **Gate-1 PASS**.

The latest independent grade is `F17B-REPAIRED-CHAIN: NOT FIT` on finding `N1`, and the proposal
states that it "being writable does not convert that grade into FIT." Steps 1–2 remove `N1`'s
mechanism by replacing the stale deployed measurer; **step 3 is where a fresh reviewer — neither the
implementer nor `agy-capacity-probe` nor the grader of the 2026-08-28 round — decides whether the
chain is now FIT.** No submission may occur before that.

Approval changes no present gate and authorizes no action not named in the sequence.
