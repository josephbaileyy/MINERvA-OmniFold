# DECISION 2026-11-01 (later) — Joseph: keep 135 MeV as E_avail's defined constant

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **The question.** Joseph had asked "is it an issue that we dont match their e-avail"
  (`DECISION-20261101-joseph-abstracts-approved-and-event-loop-retention.md` item 3).
- **The director's answer,** from `docs/EAVAIL_DEFINITION.md` §1–§3:
  - There is no single published MINERvA E_avail. Rodrigues 2016 uses a closed species list; ours is that list
    without e±, inherited from MAT. Ascencio 2022 uses an open list, about +212 MeV/event from ours. arXiv:2312.16631
    Eq. 4 subtracts the charged-pion mass.
  - Every prediction in the paper uses our definition, so its comparisons are consistent, and the 2D comparison with
    published data does not involve E_avail.
  - Switching only the pion constant would still match no published definition.
- **The size and the independent read.**
  - The switch's measured first-order size is at most 0.21σ per cell and 0.42σ coherent (PR #622 §7).
  - The independent Sonnet read (`secondary-results/sonnet-consult-eavail-pricing-20261031/`) set the decision
    thresholds and asked that the departure sentence name the species differences.
  - The audit lane recommended keeping 135.

> With that, keep 135 MeV as the defined constant (the held sentence after Eq. 1 rewritten to name the published definitions' differences and quote the measured 0.21 sigma / 0.42 sigma)?

Joseph's answer, verbatim:

> Keep 135 (Recommended)

sha256 of the text plus a final newline begins `d13ef6f830671ea8`.

## What is decided

1. **UD-002 stands: 135 MeV remains the defined constant** of truth E_avail's charged-pion term. No code, product or
   number changes. The switch pricing (#622) merges as the record of what a switch would cost and why it was declined.
2. **The held departure sentence after Eq. (1)** (`DECISION-20261031-joseph-eavail-switch-pricing-and-edits.md`
   item 3) is rewritten by the paper rewrite lane, through the fact ledger and truth checks. It states:
   - that no single published E_avail definition exists;
   - how ours differs from the closest published definitions: the e± exclusion and the 4.57 MeV per charged pion,
     against the closed list and the charged-pion mass; and the additional species of the open list;
   - the measured size of the pion-constant departure: at most 0.21σ per cell and 0.42σ as one coherent shift, first
     order.

   It must not say or imply that the pion constant is the only departure. Joseph sees it in his next read.
3. **`docs/EAVAIL_DEFINITION.md` is corrected,** with its owner's review:
   - its six-site list becomes seven (#622 §1);
   - the materiality bracket of §3 gives way to step 0's measured size, with a pointer to #622 §7.

## Not changed

The E_avail definition, every number and product, the event-loop retention decision. Nothing is submitted, deposited
or tagged.
