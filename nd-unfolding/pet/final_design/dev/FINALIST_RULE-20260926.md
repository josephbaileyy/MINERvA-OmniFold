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

## Addendum (2026-09-26 ~18:30Z; before the large slot is chosen, before any dev2Q run started, and before any per-design pull-weight tail or any PET2 k = 4 weight tail was tabulated)

Prompted by the independent scientific-scope review (findings Q2-a, Q2-c, Q2-e and "implement the
between-design step"). Disclosed motivation: P2preS1 was seen to reach step-1 weights ≈ 5.5 × 10⁵ at
k = 5 (development tilt −2.4) while passing the four screens at k = 4.

1. **Completeness.** A k counts only when every screen is measured on the manifests' 2 event draws;
   a k beyond a design's run length (its configs' `iterations`) is neither evidence nor incompleteness.
   A package is chosen only when none of its members is incomplete (Amendment 2). `L128H2E16`
   (2 learning-curve runs, no D1 −0.35/D4d rows, both left incomplete at k = 2 because 16-epoch fits do not
   fit the debug queue) is not a screen candidate; the 16-epoch large candidate is `L128S1E16`.
2. **S-N1 at K\* only**, applied to every design: the frozen §6.3 N1 thresholds on the development runs'
   post-hoc weight tails at k = K\* — max over all the design's runs of the truth-passing push weight
   and of the selected-event pull weight ≤ 100, no non-positive weight, median over the F runs of the
   push ESS/n ≥ 0.20 and of its 99.9th percentile ≤ 10 (the ESS is of the push alone: a stated proxy of
   N1's prior-truth-weight × push). A design passing the four screens at K\* but failing S-N1 does not
   pass; K\* is not re-searched (no screening at K\* + 1, which would tailor the rule to the observed
   failure).
3. **Between-design step** (as the rule states, now in code, `apply_finalist_rule.choose`): package
   membership (compact: H1, H2, H2S1, CS1, H2S1E16; large: L64\*, L128\*, P2pre\*, P2scr\*); highest
   development tilt at K\*; designs within 0.02 of it are tied; ties broken by the lower D4d residual at
   K\*, then by the lower per-unfolding cost (charged A100-hours at the design's declared packing, the
   §6.7 clarification of Amendment 3); fallback = fewest failed screens (S-N1 counting as one).
   The challenger condition (passes everything; differs from both finalists in detector
   representation or truth step) is reported; it is necessary, not sufficient, for a third finalist.
4. **PET2 learning-rate-policy arm (stage dev2Q)** gets its own ids `P2preA1`/`P2scrA1` (PET2 step 1
   with C's annealed schedule, 1e-5 after the first iteration; H2S1's constant truth step) — the matched
   counterpart of our PET's H2 (annealed) / H2S1 (constant) pair — and the D1 −0.35 rows the screen set
   requires (16 runs; the 12 configs first committed under the colliding ids `P2preS1`/`P2scrS1` were never
   run and are replaced by content-identical configs). It was added after the constant-rate divergence was
   seen; it is a rule candidate like every other large design.

The compact finalist stays as frozen by Amendment 2 (H2S1, K = 5); for the compact package the
addendum's outputs (S-N1 at K\*, the between-design step) are reported for information only.

**Correction to addendum item 2 (2026-09-26 ~18:45Z, after the recomputed development tables were read).**
S-N1's population was "all the design's runs". The dev1 designs (H1, H2, H2S1, CS1) also ran response and
generator cases (R1 ×1.05, D1 +0.35, D2, D5) that the larger designs never ran, so the screen compared unequal
populations: H2S1's only weight above 100 (step-1 max 119 at k = 5) is in its R1 ×1.05 response case. S-N1 is
evaluated on the four screen cases every design ran (F draws, D1 −0.35, D4c up, D4d up). Disclosed effect: no
large design ran any other case, so the large-slot inputs are unchanged; for the (information-only) compact
package H2S1 passes S-N1 at K\* = 5 on the matched population. The R1 step-1 weight growth is reported with the
response results.

## Addendum 2 (2026-09-26 ~20:15Z, protocol Amendment 3b; before any run of the N2 repair arm)

**S-N2** (Amendment 3b item 3): at K\* only, after the four screens and S-N1, the pooled within-draw
estimator-seed sd of `R_E0` on the S3P seed runs (DEV draws 0–1, ≥ 4 seeds) ≤ 0.05 (§6.3 N2's threshold),
computed by `dev/n2_table.py` through `decide.Rules.N2`. An unmeasured N2 at K\* makes the design incomplete.
New candidates `H2S1T24` (compact) and `L128S1T24` (large): 24-epoch truth step. The rule is re-applied to both
packages with S-N2 (Amendment 3b item 4).
