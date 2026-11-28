# (b) part 3: amendment A1 to the B5D declaration (tier3-design, 2026-11-24)

**Amends:** `blocks5d-20261124/B5D-DECLARATION.md` rev 1, sha256
`676c17fc5982a01c21f4c7feae2f6c8cd32b0b8ecdc69ec93882e5e30c0f0b1b`. That file is unchanged. Where this text and the
declaration differ, this text governs.

**Authority:** the director, by message on 2026-11-24: "Part 3: yes, write amendment A1, items 1–7 as you proposed."
The items come from the reads of the code at `c8834fd6` (agy on `gemini-4-hydrogen-xhigh`, and codex-school), saved
under `blocks5d-20261124/reads/`. The director binds A1 before the build runs.

**Nothing has been built.** No build code has read the fetched LL5D products (tar sha256 `13e53ec2…`). The amendment is
fixed before the build, and nothing is tuned on its output.

## 1. The cal-set cross-check is dropped

- §4's "The cal-set cross-check (printed, never entering f̂)" is removed, and the build does not compute it.
- The cal sets are not flux-only. Each cal experiment draws:
  - the interaction and detector universes;
  - a uniform flux universe;
  - Poisson counts;
  - a fresh half-MC split (`s5p_nullexp`, FD-PLAN).

  A comparison with S1's flux + stat σ would have read the other sources as a flux discrepancy.
- **This supersedes:**
  - the cal-set clause of the director's ruling (a) ("with F0's cal sets as a printed flux-only cross-check");
  - the same clause in B5D-BINDING-1's authority line.
- **The inputs that change use:**
  - `s1/readout/s1_assembly.json` is now read only for C-FLUX's `meta.flux_weights`;
  - B5D's own code reads only F's members' `r_*` arrays from `fd_f0b_experiments.npz`.
  - B-SEL's bound `prepare`, reused unchanged for b̂, the noise and R, loads the whole table, cal sets included. It looks
    up only the `r_<truth>` and `seed_<A7 truth>` arrays, so no cal value reaches any output.

## 2. The untested share of C_e is about 29%, and an active L rescales it
<!-- absence-ok: a scoping statement: the components of C_e that the toy ensembles do not draw, by construction -->

- §4's "about 17% of C_e's trace" is wrong: it divided by the relative C_total trace.
- On C_e's own relative trace, the laterals plus the normalization are **about 29%**. The calculation:
  - `s1_assembly.json`'s `trace_share` gives 0.1406 (lateral) + 0.0276 (normalization);
  - C_e's groups sum to 0.5804 of C_total (1 − C_model's 0.4196);
  - so the ratio is 0.2899.
- **An active L acts on all of C_e in band R's modes.** That includes parts the toys do not test:
  - the laterals and the normalization;
  - GEANT_Neutron and GEANT_Proton, absent from the primary `minus2` toys.

  An inflation of V_F therefore rescales these too.

## 3. Why the spent tunes enter, stated correctly

§4's "Why the spent tunes may enter here" is replaced by:
- **COVFIX's reason.** COVFIX excluded G18 and AR23 from its fitted factors because they were spent, not because they
  were sealed.
- **Here, the director's ruling (a) uses the spent tunes.** V_F's factors are fit on the only two available GENIE v3
  tunes. Part 1's selection (B-SEL) uses the same two tunes.
- **(b)'s held-out truths are PV's sealed truths.** They are not among the inputs here.

## 4. What f̂ measures

- **f̂_R is the toy spread relative to LL5D's rebuilt reference block.** It is not the ratio to the toys' exact sampling
  covariance.
- **The toys and D sample differently:**
  - **The toys:** each draws a clipped nature jointly over the universes and fresh Poisson counts at that nature, then
    unfolds with nominal MC.
  - **D:** it sums single-band universe blocks, which vary the unfolding MC on fixed mean pseudo-data, and a stat
    bootstrap of one nominal Poisson realization with coordinate jitter.
  - **The consequence:** joint clipping, and the stat terms that differ between the two, are not in D. A trigger can
    partly reflect this mismatch, not only a missing fluctuation.

## 5. What SE does not include

- The bootstrap holds D and its eigenbasis fixed at the full sample, as in COVFIX.
- So SE(f̂_R) leaves out the denominator's own sampling variance:
  - the Flux band's effective count, n_eff about 19;
  - the 50 stat replicas.
- The bootstrap resamples the toys only. Both truths' toys unfold with the same nominal MC, which it holds fixed, so
  SE(f̂_R) is conditional on that MC.

## 6. Bands are kept per ensemble

§4's measured factor is replaced by:
- **Each ensemble keeps or drops each band by its own D.** The rule is unchanged: a band with fewer than 4 kept modes is
  dropped.
- **f̂_R** is the mean of F̃_R over the primary ensembles that keep band R.
<!-- absence-ok: a method rule for a dropped band, not a claim that a result does not exist -->
- **If no primary ensemble keeps band R,** band R is not measured and φ_R = 1.
- **If no band is measured,** the build stops short of V_F, as in §4's unresolved case.
- **The bootstrap** applies the same rule in every replicate.

## 7. The adoption caveat on C_b

- C_b is fitted on nominal plus the three C_model vertex truths. Adding C_b alongside C_model can pay twice for the same
  model deviations.
- The adoption record goes to Joseph with the numbers, and names the formula proposed: C_b in addition to C_model, in
  its place, or another combination.
- This changes nothing in the build. Adoption stays Joseph's decision (§1).

## Implementation notes (within the declaration, no change of method)

The code (`nd-unfolding/b5d/b5d_build.py`) implements the declaration with A1:
- C-LEAK is a dimensional check, with no magnitude cutoff:
  - the build runs a second time with every absolute quantity it holds scaled by 2¹⁰: the LL5D products (U·xsec,
    U·xtrue), all of B-SEL's generator predictions g, and C_e (by 2²⁰). B-SEL's other outputs (b̂, the noise, R, the
    splits) are relative. Its closure products enter only through the ratio R and through its own check that closure_nuwro's xsec/xtrue − 1
    reproduces the bias;
  - every number outside C_b,abs and V_F must be unchanged, those two must scale by 2²⁰, and the records must have the
    same shape and types;
  - an absolute cross section anywhere else would move by 2¹⁰;
- LL5D's toy mean error is taken relative to T's cell integral, put into Tune v1 units through R (as β = b̂ ⊙ R), and
  printed against C_b;
- the declared Gram–Schmidt tie rule, as COVFIX's `covfix_core._canonical_tied` (null test relative to each
  projection), then the sign rule;
- L acts only on C_e's kept modes;
- C-PSD refuses an indefinite D, a non-finite C_b, or a C_e that is not positive semidefinite;
- C-FIN covers:
  - the `all` factors;
  - T's cell integrals (each must be positive);
  - the printed quadratics;
  - V_F;
- a zero-rank C_b prints its quadratic as null;
- every refusal, including B-SEL's and LL5D's own, exits 5 and writes nothing;
- the record carries its matrices' sha256. It is formed and checked whole, written and synced in a uniquely named hidden
  sibling directory, then renamed to the output atomically, refusing if the output exists in any form (macOS
  `renamex_np` RENAME_EXCL, Linux `renameat2` RENAME_NOREPLACE). The output's parent must exist. A kill before the
  rename can leave the hidden sibling, never a partial output. Syncing the parent after the rename is best effort: a
  failure there is a warning, since the record is already whole;
- for every band, reading and truth, the record prints the raw toy and reference traces on the band's kept modes,
  relative to T's cell integrals. An unresolved stop then still shows the size of the problem (the director, 2026-11-24).
