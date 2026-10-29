# DECISION 2026-10-29 — Joseph: settle OI-160 with a pre-declared tolerance run on unseen replicas

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The bound OI-160 reproduction
([`state/oi160-reproduction-20261029/REPORT.md`](state/oi160-reproduction-20261029/REPORT.md), PR #496) came back
**VOID** under its bitwise criterion. The corrected code did not reproduce itself bit for bit (K1 false): two runs of
the same code, input and seed differed by a median of 2.8 × 10⁻¹³ relative. Its distances, reported as descriptive only,
were:
- at about the run-to-run scale: corrected code vs the July replica, 3.4 × 10⁻¹³; old code vs the June replica,
  9.2 × 10⁻¹³;
- every cross pair: a median of 0.74 %.

No tolerance was declared, so none may be applied to these data after the fact. The director offered three options: a
pre-declared tolerance run on unseen replicas; accepting the descriptive pattern; or leaving OI-160 open.

The director asked:

> OI-160 came back VOID under its bitwise rule. How do you want to settle it?

Joseph's answer, verbatim, the only option he selected:

> Pre-declared tolerance run (Recommended)

sha256 of the text plus a final newline begins `7919401947f9ff50`.

## What is decided

1. **A new declaration settles OI-160.** The option offered read: "A new declaration fixes the tolerance from the
   measured noise floor (≈1e-13) before any data, applied to unseen replicas: a few seeds from each of the three July
   producers. About 12 CPU unfolds, ~0.6 node-h, under the standing approval."
   - The close-items session declares it, and the director binds it before anything runs.
   - The tolerance and the reading table are fixed in the declaration, from the noise floor K1 already measured. No
     replica it grades has been compared before.
   - Seed 1 and its three outputs are not regraded.
2. **It runs under the standing approval for jobs under 12 h:** CPU only, no GPU, no premium QOS, no write to CFS.
3. **The outcome goes to Joseph as a report.** Any change to `C_stat`, `C_ML` or the adopted trunk is a separate
   decision. `C_ML` is not in scope.

## Not changed

- `C_stat`, `C_ML`, the trunk, every receipt and product, and every published value.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
