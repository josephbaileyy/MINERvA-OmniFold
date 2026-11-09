# OUTCOME 2026-11-09: the GEANT_Neutron and GEANT_Proton band diagnosis. Inputs EQUAL; departures seed-stable; the scale test reads MIXED in both bands, so no mechanism is licensed

**Recorded by** the director (paper-tighten lane), for Joseph, from the committed receipts.

**The design:** `state/measurement-paper/5d-community-20261024/FD-1B-BAND-DIAGNOSIS-DECLARATION.md`, bound by
`FD-1B-BAND-DIAGNOSIS-BINDING-1.md` at M = `83ac32fb`, with addenda A1 (the P2/P3 fence after ENS1, #958) and A2 (P3 as
4 jobs × 7 lanes × 4 items, #962). **Under** `DECISION-20261108-joseph-5d-coverage-and-parallel-studies.md` item 2: a
diagnosis only, in parallel; it does not gate LL5D and cannot change its primary reading.

**The question** (from `OUTCOME-20261108-1b-precheck-part1.md`): in Part 1, bands GEANT_Neutron (cells R00 R02 R08 R09
R10 R11) and GEANT_Proton (R01 R05 R07 R08) depart, rule S and rule K, with no cause licensed. Is that a defect of the
inputs, seed noise, a non-linearity, or a first-order mismatch inside the estimator?

**The records** (all under `fd/receipts-1b/band-diag/`): P0 #944, P1 #955, P2 #965, P3 #968, P4 #970; readout.json sha256
`553c3dff2a6629450276ff1fca86a3d6a483b1780ae0fc3c6c0f4c0cba327a0a`. coverage-5b-audit read P2's readout and P3's table and
connects before P3 ran (#965 comment 6729650677).

## The readings, as the records state them

| step | reading | record |
|---|---|---|
| §4.2, HK | SAME COMPARISON in all four detector bands (a record of Part 1's products, not a test) | P1, #955 |
| §4.3, inputs | **EQUAL**: for all 8 detector universes, n_differ 0 and max_rel_diff 0.0, for signal and background | P2, #965 |
| §4.4, seed | **SEED-STABLE** in all 10 departing cells; F_src identical across seeds 42–54 (max sd of ln F_src 4.4e-16) | P4, #970 |
| §4.5, scale | **MIXED** in both bands (GEANT_Proton R08 alone reads CONSTANT) | P4, #970 |
| §4.6, descriptive | the signal and background channels, and the reference bands' F_src(ε) | P4, #970 |

**§4.5's values** (F_src at ε = ½ / 1 / 2; p_up, p_down):

| band | cell | F_src (½ / 1 / 2) | p_up | p_down |
|---|---|---|---:|---:|
| GEANT_Neutron | R00 | 1.097 / 1.201 / 1.042 | −2.149 | 0.991 |
| | R02 | 1.027 / 1.398 / 0.994 | −∞ | 3.655 |
| | R08 | 0.823 / 0.863 / 1.060 | −∞ | −0.398 |
| | R09 | unresolved / 2.237 / 1.077 | −3.440 | — |
| | R10 | 0.779 / 0.775 / 1.047 | −∞ | 0.029 |
| | R11 | 0.674 / 0.701 / 2.371 | −∞ | −0.148 |
| GEANT_Proton | R01 | unresolved / 1.166 / 0.897 | −∞ | — |
| | R05 | unresolved / 1.248 / 1.012 | −4.244 | — |
| | R07 | 1.018 / 1.123 / 1.020 | −2.531 | 2.688 |
| | R08 | 1.114 / 1.101 / 1.096 | −0.063 | −0.167 |

p_up is −∞ where F_src at ε = 2 returns to or crosses 1.

**Controls:** every one passed. The P2 rebuilds are bitwise over 14 items; seed 42's F_src and resolution equal Part 1's;
the 73 shared sources' stat is byte-identical at every step (P1's baseline `7986e2bf`, through P4); 126 products.
**Cost:** 3.74 of the 9.0 CPU node-h cap.

## CITABLE FOR (FD-1B-BAND-DIAGNOSIS-DECLARATION.md §4.7)

- **§4.3 EQUAL:** "the pseudo-data and the simulation side carry the same factor on the same reco rows inside the window,
  for every detector universe."
- **§4.2 SAME COMPARISON:** as a record of Part 1's committed products, in its licensed wording; on that record, rule K's
  FAIL is not separate evidence.
- **§4.5 MIXED:** the values in the table above, as values.

## NOT CITABLE FOR

- **A mechanism.** MIXED licenses no reading as a non-linearity (SCALES) or a first-order mismatch inside the estimator
  (CONSTANT); GEANT_Proton R08's CONSTANT is a value only.
- **§4.4 SEED-STABLE:** §4.7 has no CITABLE FOR row for it; it only admitted the cells to §4.5. It is recorded here as the
  record's reading and licenses no sentence.
- **Anything inside the estimator** from §4.3, or HW's rows outside the window.
- **Coverage**, in any form, or that S1's detector block is right; any repair; the truth dependence (item c).
- **Any paper or note sentence** without the PRD-referee read and Joseph.

## What it changes, and what stands

- **The question narrows, and is not answered.** The inputs are not the cause (EQUAL), and seed noise is not
  (SEED-STABLE). Whatever separates the two sides for these bands lies inside the estimator, and the declared scale test
  does not classify it.
- **Unchanged, in every outcome:** Part 1's record, gate D's FAIL, Part 0, 1B's rule (iii), and LL5D's primary reading
  (the test without these two bands). No outcome here is a coverage statement.
- **For Joseph, not decided here:** whether a further study of these two bands is worth declaring. The director does not
  recommend one now: LL5D's primary reading already excludes them, and the referees' items do not turn on them.

Nothing is submitted, deposited or tagged.
