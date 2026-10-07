# W2b report: recoil-response sensitivity of the ten joint-test rejections ([date])

**CITABLE FOR:** whether each of the ten frozen rejections survives a ±4% coherent scale of the simulated
reconstructed recoil, evaluated against the frozen null ensembles; and the δ = 0 control.
**NOT CITABLE FOR:** an uncertainty, a validated response prescription, a revised primary decision, or
completeness of the response model. δ = 0.04 is a **labelled exploratory sensitivity** (Joseph 2026-10-06, item 4).

**Authority:** `docs/publication/DECISION-20261006-joseph-publication-approvals.md` item 4; the W2a review
(`docs/publication/w2/REVIEW-20261006-w2a-independent.md`, CLEARS WITH CHANGES) and its C1–C3.
**Code:** branch `study/w2-recoil-response-20261006` at [sha]; reviewed binary mod md5 `f3e9c97b…`.

## 1. What was varied, stated with the result (review F6)

- The simulated reconstructed recoil is scaled by s = 0.96 and s = 1.04 in two places. One is reco E_avail
  (`NewEavail()`, a linear sum of tracker and ECAL blob energies × 1.17, so the scale is exact). The other is the
  calibrated reco energy transfer `<tree>_recoil_E` that enters reco q3 and W.
- These two are scaled **separately, by the same factor**. A real response difference would act on the
  calorimetric response before calibration, and per particle species. MAT's per-particle response map is not used
  (it is commented out in the source). This single coherent scale is a simplification, acceptable only under the
  exploratory label.
- Data, truth, weights and selection are unchanged. The variation moves the data side, not the null. For strongly
  non-central nulls (λ = 318–6,344) the size of that approximation is unmeasured. "Robust" means "not removed by
  this data-side variation".

## 2. How the implementation was verified, and a limit of that check (review F2)

- The W2a comparer checks q0 through the identity q3² + W² = (q0 + M)². That identity **cannot see the Q² term**:
  a defect that moved Q² and W together would pass it.
- The reviewer's independent check closes that gap. It predicted q3 from the muon kinematics with
  E_ν = E_μ + s·q0, and matched within 2.5e-10 GeV on every passing smoke row, including the rows clipped to W = 0.
- The full-1A shifted outputs match the production 1A CV omnifile in every unshifted branch. Reco E_avail = s ×
  production to 2.3e-16.

## 3. Execution (C1, C2, C3)

[Jobs, limits, ledger rows, merges (1A…1P order), dump and unfold digests, the deploys used: dump `c1cba7bf`,
unfold `4e4b4f56`, evaluate `e9372b75`.]

## 4. δ = 0 control

[Bitwise against `data_b-_j-.npz` (`fb5cc679…`), or the fallback: each claim p within the frozen
`observed_jitter_p` [min, max] and Holm decisions equal to the frozen ones. A FAIL stops W2b here, with no
robustness statement.]

## 5. Result

| test | frozen | −4% | +4% | robust at δ = 0.04 |
|---|---|---|---|---|
[ten rows from `w2b-decision.json`]

[Stated with §1. A non-robust test narrows every claim about that prediction to "not robust to a 4% recoil-response
variation". If all are robust: "tested at δ = 0.04", and the amendment-7 completeness caveat still stands.]

## 6. Cost

[Ledger total against 8.0; W2a 0.0985.]

## 7. Not verified

[Carried from W2a, plus anything new.]
