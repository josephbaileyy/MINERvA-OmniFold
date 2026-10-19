# Binding addendum 2: rulings R1–R5 for MP-1 S0 (2026-10-19)

**By** the paper-tighten lane, as director, under [`BINDING-PHASE1-20261019.md`](BINDING-PHASE1-20261019.md) §2
(MP1-A). The session reported its S0 findings by message, with the receipt
`phase1/mp1/receipts/s0_q0_g2_1A_mc_first20000.txt` (on its phase-1 branch): 20k entries of one 1A MC file,
read-only, 0 node-h.

These rulings come before any ±1σ pass and before any J-cell number, as the frozen specification requires.

**CITABLE FOR:** R1–R5 and the S0 grant.
**NOT CITABLE FOR:** any result.

## Findings, as reported

- **q0.** `MasterAnaDev_recoil_E` is a single-valued but nonlinear function F of the passive-corrected cluster sum pc.
  It is exactly 1.4996·pc below about 509 MeV, and nonlinear above.
- **The two MAT conventions:**
  - the legacy convention (adding the absolute `_id_err`) under-shifts by about 1.5×;
  - the fractional convention is exact in the linear region, and within −5.2% to +2.2% of the shift above it.
- **G2 passes.** The species pieces sum to the tracker and ECAL energies to 1e-15. Cross-talk is a component, but
  MAT's `ResponseSystematics.cxx:34` marks it "DO NOT USE".
- **The muon fuzz is not split by species.** Shifting species energies in absolute terms double-counts energy already
  removed as fuzz.
- **The named G1 reference has a different event set** from the lateral-only path: 2,679,264 entries against
  2,489,136.

## Rulings

| # | ruling |
|---|---|
| **R1, q0** | **F-propagation, q0′ = F(pc + Σ_s δ_s·pc_s).** The frozen rule selects the convention that "reproduces `MasterAnaDev_recoil_E` from its parts", and neither MAT convention passes it. F-propagation is the reading that does: the calorimetric calibration F is unchanged, and the response change acts on the visible energy it maps. This amends the candidate set, before any J-cell number exists. **Gate G0, new:** F is tabulated per playlist from the tuples' (pc, q0) pairs as a monotone piecewise-linear interpolant. It must reproduce q0 from pc to ≤ 1e-4 relative on held-out events, which means another MC file of the same playlist, for every playlist used. **On G0 failure:** the fractional convention, as a declared approximation with its measured bound (−5.2% to +2.2% of the shift, exact below about 509 MeV), recorded in the result. |
| **R2, muon fuzz** | **Pro-rata is primary:** E_avail′ = E_avail·(1 + Σ_s δ_s·E_s/(E_tracker + E_ecal)), which assumes the fuzz has the species composition of the total. At S0, on 1A, also report descriptively the two extremes: the fuzz is none of species s, or all of it, up to its size. The result states that the fuzz's species split is not known. |
| **R3, cross-talk** | **Out of the primary band**, following MAT's "DO NOT USE" (`ResponseSystematics.cxx:34`), as neutrons were excluded under MAT's convention (D1). It is reported **beside** the primary as a variant with cross-talk at 20%. The result states both. |
| **R4, G1** | **Primary:** a fresh δ = 0 1A pass with the unmodified binary, against the universe code at δ = 0; "equal", with the same source and libraries. **Secondary:** "equal" against W2b's existing `rrzero_1A`. **Also, as a report:** test the session's reading of the entry-count difference. The CV-selected subset of the full-universe production file should equal the lateral-only pass; check it at the event level. Add a sentence that the W2a review's "entry counts are equal" (`REVIEW-20261006-w2a-independent.md:16-19`) compared another pair, if the check shows that. |
| **R5, z seed key** | Approved as **0x4D31**, `default_rng([pseudo_seed, 0x4D31, i_s])`, with i_s = 1–5 for proton, meson, EM, other and cross-talk. Cross-talk's draws are used only in the variant. |

## Grant

- The S0 build, the δ = 0 pair, the proton and meson +1σ passes, G0, and the R2 extremes are granted within the phase-1
  ceiling (expected about 0.2–0.4 CPU node-h, on shared).
- The δ = 0 pair may run now: it does not depend on R1–R3.
