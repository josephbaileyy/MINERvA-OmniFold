# Binding addendum 7: MP3-C (GiBUU on hydrogen) stopped at B3; a post-hoc bias check (2026-10-20)

**By** the paper-tighten lane, as director, under [`BINDING-PHASE1-20261019.md`](BINDING-PHASE1-20261019.md) §2.

**CITABLE FOR:** the ruling below.
**NOT CITABLE FOR:** any result. GiBUU's A7 decisions stand as frozen.

## What the session reported

GiBUU on hydrogen passed C0, C1′, B1 and B2. It **failed B3′**, the frozen GiBUU build's own sampling-closure check.
- The within-bin χ² is 248.8/148, p = 4.1e-7, against 167.0/148 on carbon.
- On hydrogen the event counts rise across each 0.5 GeV flux point between 1.5 and about 5 GeV. That breaks the test's
  premise of a constant keep probability within a point.
- The frozen build states that its r(E) reweight does not depend on the keep probability. That statement has not been
  tested.

## Ruling

1. **Under the frozen rule, no GiBUU-on-CH prediction is reported as having passed its gates.** That holds whatever
   follows.
2. **A post-hoc bias check of the premise (option b) is allowed, labelled post hoc.** It is declared, and its
   declaration committed or hashed, before it is computed:
   - **The alternative reweight:** within each flux point, a per-event weight that removes the measured within-point
     slope of the hydrogen keep probability. It is a linear fit in Eν to the existing counts, with the fit fixed in the
     declaration.
   - **The readout:** the per-cell hydrogen contribution under the frozen r(E) against the alternative, over the 72
     GiBUU-domain J cells, as Δ_c/σ_c with σ_c defined as in MP3-B. The effect on the CH-combined prediction is
     reported too.
   - **The acceptance:** |Δ_c/σ_c| ≤ 0.1 in every cell, with the maximum reported.
3. **If it passes,** the GiBUU-on-CH replay is computed with the frozen r(E), beside A7, under the label "B3 (sampling
   closure) failed on hydrogen; a post-hoc bias check of its premise passed at ≤ 0.1 σ_c". The replay under the
   alternative reweight is shown beside it.
4. **If it fails,** no GiBUU-on-CH number is reported. The size of the effect is reported, and the target correction
   waits for a sampling fix after the maintenance.
5. **The borrowed variant (c) is not run:** GiBUU on hydrogen did run.
6. **The deadline** is about 03:00 PDT on 2026-10-21; otherwise the check is deferred. It stays within the phase-1
   ceiling.
