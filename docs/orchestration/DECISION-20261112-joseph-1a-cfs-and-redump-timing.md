# DECISION 2026-11-12 — Joseph: the 1A CFS copy stays as it is; the paper does not wait for the F1.2(i) re-dump

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **The 1A CFS copy.** The 1A AnaTuples already have a copy on CFS. Whether to make it group-readable was an open
  item for Joseph.
- **The F1.2(i) re-dump.** The fresh referee round's F1.2(i) asks whether truth information outside the five features
  matters. Answering it needs an event-loop re-dump: neutrino energy, true vertex, leading-proton energy and event
  identity. The director approved it in principle on 2026-11-11 as its own lane after RSN, with a cap of 2.5 node-h,
  pilot included (`RSN-BINDING-1.md` ruling 6). Its declaration is PR #1090. The director had asked Joseph whether the
  methods paper (#977) should wait for its result, and recommended that it should not.

## Joseph's words, verbatim (2026-11-12)

> we don't need to make the 1A CFS copy group-readable.

(`e5dc576449d82281`)

> also we don't need to wait for the re-dump's result but we can fold the changes in if theres extra time.

(`13a8c0fcfcb8b314`). Each sha256 is of the text plus a final newline.

## What is decided

1. **The 1A CFS copy's permissions are not changed.** Nothing is done to it.
2. **The methods paper does not wait for the F1.2(i) re-dump.** The re-dump lane proceeds as approved: declaration,
   audit, binding, the 1A pilot, then the full set. If its results, including the C-BKG background-composition control,
   are ready before the paper is final, they are folded in through the usual value checks and reads. Otherwise the
   paper and the referee response describe the check as under way.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the two choices above, as Joseph's.
- **Not citable for:** any re-dump result; any change to the re-dump lane's design or price.

Nothing is submitted, deposited or tagged.
