# DECISION 2026-10-31 (later) — Joseph: price a switch of E_avail to the charged-pion mass; apply four editorial fixes from his read

**Recorded by** the paper-tighten lane, as director.

**What led to it.** Joseph read the paper through Sec. III and asked five things. An independent Sonnet referee read the
source. On 135 MeV the director corrected his own earlier framing (#603).
- OI-30's record finds that MINERvA's published E_avail (arXiv:2312.16631, Eq. 4) uses charged-pion kinetic energy,
  which is a 139.57 MeV subtraction.
- It finds our 135 MeV likely inherited from MAT, traced to the "MINERvA 101" tutorial.
- It finds that 135 is not a compatibility constraint with the published comparators.
- The departure is 4.57 MeV per charged pion.

> 135 MeV vs the charged-pion mass (139.57 MeV), now with the full provenance: what should we do?

Joseph's answer, verbatim:

> Price a switch to 139.57

sha256 of the text plus a final newline begins `22a571fa587c5e98`.

> Apply the four editorial fixes (split Eq. 1; tighten the W paragraph; keep 'fixed seed' but move '42' to the note; replace Table I with a paragraph)?

Joseph's answer, verbatim:

> Apply all four (Recommended)

sha256 of the text plus a final newline begins `422bc04f8081093e`.

## What is decided

1. **UD-002 is reopened for pricing, not yet reversed.** Until Joseph decides on the price, 135 MeV stays the defined
   constant.
   - A read-only lane estimates what redefining truth-level E_avail with 139.57 MeV would take: the products and
     results affected, the reruns, node-h with caps, wall time, and the downstream records and text.
   - It also estimates the size of the effect on the reported cells before any rerun, where that can be computed from
     committed truth-level information.
   - The estimate comes to Joseph with an independent recommendation.
2. **Four editorial fixes are applied to the paper,** through the fact ledger and truth checks. Nothing factual leaves
   the paper.
   - Eq. (1) is split across two lines under one number, breaking before the π⁰ term.
   - The reconstructed-W paragraph is tightened, keeping every fact.
   - The text keeps "fixed seed" for the two-observable estimator. The values "42" and "seed plus three" move to the
     note.
   - Table I is replaced by a paragraph giving what the two estimators share and which result each gives.
3. **The sentence after Eq. (1)** says plainly that the definition departs from MINERvA's published E_avail by 4.57 MeV
   per charged pion, and that every number uses 135 MeV, while 135 MeV stands.

## Not changed

- The E_avail definition, until Joseph decides on the price. Nothing is submitted, deposited or tagged.
