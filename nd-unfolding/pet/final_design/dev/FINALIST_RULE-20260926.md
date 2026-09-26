# Development finalist-selection rule (committed 2026-09-26, before any dev2S, dev2T or PET2 recovery was inspected)

Development evidence only (DEV bank). The rule turns the S1/S2 development results into the ≤ 3
finalists that the "FB release" amendment will freeze (PROTOCOL-20260925 §8 stage S3). At the time
of writing, the committed development results inspected are dev1 (H1, H2, H2S1, CS1; 2 event draws
per case), dev2L (L64H2, L128H2 at 8 epochs) and the step-2 interventions; dev2S (L64S1, L128S1,
H2S1E16), dev2T (L128S1E16) and the PET2 runs (P2preS1, P2scrS1) were running and **not inspected**.

## Development screens (per design and iteration count k, means over the available event draws)

Proxies of the frozen decision table on development events, used only to choose finalists:

| screen | quantity | pass |
|---|---|---|
| S-B2 | D4d (neutrons ×1.3) `E_avail` residual L1 vs the pseudodata truth | ≤ 0.021 (injected 0.011 + 0.010) |
| S-U4 | D4c (protons ×1.3) joint `E_avail` × proton-class recovery vs the oracle | ≥ 0.25 |
| S-U3 | D1 −0.35 recovery | ≥ 0.50 |
| S-U1 | development-tilt recovery (F draws) | ≥ 0.60 (development margin above the 0.556 floor) |

## Choice of the iteration count

For each design, `K*` = the smallest k in {2, …, 6} (or its run length) at which all four screens pass;
if several k pass, the smallest k whose development-tilt recovery is within 0.02 of the best passing k.
Fewer iterations win ties: more iterations are not presumed safer.

## Finalists

1. **Compact package** (our PET at its original 47,041-parameter step 1): among the compact designs
   passing all screens at their `K*`, the one with the highest development-tilt recovery; ties (within
   0.02) broken by the lower D4d residual, then lower cost.
2. **Large/pretrained package**: among the larger step-1 designs (L64*, L128*, P2pre*, P2scr*) passing all
   screens, the one with the highest development-tilt recovery (ties as above). If PET2-pretrained and
   PET2-scratch both pass, the pretraining contrast is reported regardless of which is chosen.
3. **Challenger**: none from the algorithmic alternatives (AUSSIE closed by its matched test,
   `scalar/SCALAR_AUSSIE_MATCHED-20260925.md`; scalar methods fail S-U4 by construction — no topology
   in their truth inputs). A third PET design enters only if it passes all screens and differs from both
   finalists in representation or truth step.
4. **Anchors** (FINAL only, E0–E3): CTL at k = 3 and C at k = 3.

If no compact design passes, the compact finalist is the one failing the fewest screens (the failure is
carried into the final eligibility test, not waived); likewise for the large package. A package with no
passing and no near-passing design is recorded as closed with its development evidence.
