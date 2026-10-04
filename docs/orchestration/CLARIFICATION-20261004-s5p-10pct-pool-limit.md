# s5p (`OI-193`): the 10% pool limit and the 2026-10-04 extension — readings, measurements and the amendment needed

**CITABLE FOR:**
- the exact text of the 10% pool limit;
- how it was applied at activation;
- what it says, and does not say, about enlarging an existing pool;
- the measured result under each reading;
- the explicit amendment wording the owner can adopt to resolve it.

**NOT CITABLE FOR:** an amendment or a ruling. It is unresolved until the owner adopts one of the §4 texts. It changes
no scientific criterion. Requested by the owner on 2026-10-04: "My approval of the extension should not leave that
ambiguity unresolved."

## 1. The governing text, verbatim

- **Authorization §1**, from the owner's `/goal` text of 2026-09-26: "Each new pool is also capped at 10% of current
  uncommitted allocation after reservations. Reserve 20% for verification/repair."
- **Approved handoff** (`HANDOFF-20260926-precision-measurement-completion.md`, lines 105–108): "Each new pool is
  additionally capped at 10% of current uncommitted allocation after existing reservations. … Retain 20% of each new
  pool for verification/repairs".
- **How it was applied at activation** (authorization §4): campaign pool = min(a, b), where
  - (a) is the unspent cumulative envelope;
  - (b) is 10% of the uncommitted allocation after reservations.

  CPU: a = 310.184, b = 0.1 × (20,000 − 16,583.7 − 0.0) = 341.63, so the pool is **310.184**, bound by the envelope.

## 2. What the text does not settle

"Pool" here means the campaign's per-resource pool, and "new" means established for this successor campaign. Two
things are left open:
1. **Is an enlargement a "new pool"?** The text speaks of creating a pool, not of changing one.
2. **When is "current" measured?** At the pool's creation only, or again whenever the pool changes. If again, is it
   the whole pool that is compared, or only its unspent part?

The owner's 2026-10-04 decision explicitly changed the cumulative ceiling (345.27 → 376.52). It did not address the
10% clause.

## 3. Measurements and results

Measured 2026-10-04 at 04:41Z (`state/s5p/transition-r3/allocation-measurement-20261004T0441Z.txt`):
- m3246 allocated 20,000.0, charged 16,817.7;
- reservations about 32.75, all of them this campaign's 131 rows;
- **10% of uncommitted = 314.96.**

The pool's charges, open reservations included, are 262.619 − 35.086 ≈ 227.53.

| reading | quantity compared | value | limit | result |
|---|---|---:|---:|---|
| R1: a creation-time condition | the pool, set at activation | 310.184 (341.434 would also pass) | 341.63 (2026-09-26) | **passes** |
| R2: re-applied at enlargement, whole pool | the enlarged pool | 341.434 | 314.96 | **fails** by 26.47 |
| R3: re-applied at enlargement, unspent part | the pool minus charges and open reservations | about 113.9 | 314.96 | **passes** |
| R3′: the new grant treated as the new pool | the increment | 31.25 | 314.96 | **passes** |

**Consequence under R2.** The largest compliant pool would be 314.96. With 20% reserved (62.992) and the finished
stages at 38.5, production could be at most **213.468**: an extension of +3.82, not +25.

**When the question becomes material.** Production spend above the revision-6 allocation (209.647) is projected only
near the end of production, at a measured total of about 210–229 around 2026-10-06/08. Until then revision 7 changes
only the reservation headroom, not what is spent.

## 4. Amendment options for the owner (exact text to adopt one)

- **A1 (R1):** "For s5p, the 10% pool limit is a creation-time condition, satisfied at activation on 2026-09-26; the
  owner-approved 2026-10-04 enlargement is governed by the owner's decision and the cumulative ceiling it sets."
- **A2 (R3), recommended:** "For s5p, the 10% pool limit applies whenever a pool is created or enlarged. It is
  measured as the pool's unspent remainder (pool minus charges and open reservations) against current uncommitted
  allocation after reservations. The 2026-10-04 enlargement satisfies it (about 113.9 ≤ 314.96)."
- **A3 (R2):** "The limit applies to the whole enlarged pool." The extension then needs an explicit exception (it
  exceeds by 26.47). Without one, production must revert to the R2 maximum of 213.468 through a further budget
  revision, which would bring the projected `budget` stops back.

**Recommendation: A2.** It keeps the clause's purpose, bounding the campaign's future draw against what remains
available. It does so without double-counting spend that the uncommitted measurement has already removed.
A1 is equally consistent with the activation arithmetic. A3 reads the clause most literally, but compares spent hours
against an availability figure from which they have already been subtracted.

**Status until the owner adopts a text:** budget revision 7 stays in force, as the owner decided. The campaign
records 10% compliance as **UNRESOLVED**: R1, R3 and R3′ pass and R2 fails. A decision is needed before measured
production passes 209.647.
