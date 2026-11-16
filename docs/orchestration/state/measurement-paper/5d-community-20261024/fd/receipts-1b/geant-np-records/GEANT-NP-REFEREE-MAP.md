# NOTE 2026-11-11: the GEANT_Neutron and GEANT_Proton control, mapped onto the committed records for the fresh referee's major 2

**By** the valid-region lane, at the director's ruling of 2026-11-11 (option 1). It is a records-only note: no job, no
unfold, and no new reading.

**For:**
- the fresh referee's major 2 and its §4 row on the GEANT4 neutron and proton discrepancies
  (`secondary-results/referee-methods-fresh-20261111/gpt.txt:23,93` @ `03037c3e`);
- `RESPONSE.md` row F2.2 (`methods-short-20261109/RESPONSE.md:230` @ `39d0ff8c`, the #977 branch), which helper-3 will
  point at this note.

**Withdrawn:** the 35-item split the director approved earlier the same day (signal-only, background-only and
half-amplitude arms). It re-measures the band diagnosis's channel split and scale test (§2 below). It was never pushed
or run.

**MEASURES:** nothing. Every value below is quoted from a committed record, by key path or line.

**CANNOT AUTHORIZE:**
- any job;
- any repair, or any change to the toys, gate D, M_d, the window, the reported covariance or κ;
- any paper or note sentence. The CITABLE and NOT CITABLE rows in §4 are #971's, with no new licence;
- Joseph's open item from #971 (`OUTCOME-20261109-band-diagnosis.md:74-75`): "whether a further study of these two
  bands is worth declaring". This note does not decide it.

**Records read:**
- **Part 1's readout:** `fd/receipts-1b/precheck-fd/p4/records/p4/readout.json`, sha256
  `8e05ca9bc2d0f2142b5c8d2bff28f05176c48f27454218390f09658344cea7b0` (#930). It is "Part 1's readout" below, with key
  paths in brackets.
- **The band diagnosis's readout:** `fd/receipts-1b/band-diag/p4/readout.json`, sha256
  `553c3dff2a6629450276ff1fca86a3d6a483b1780ae0fc3c6c0f4c0cba327a0a` (#970). It is "the band diagnosis's readout"
  below.
- `OUTCOME-20261108-1b-precheck-part1.md` and `OUTCOME-20261109-band-diagnosis.md` (#971).
- The code at main `03037c3e`. The five cited modules are byte-identical to `270508cb`.

## 1. The control and its departure

Part 1 compares two objects, each as a per-band block over the band's two universes, with F_src = √(E/B) per cell:
- **E:** the toys' pseudo-experiments, with the source factors on the pseudo-data;
- **B:** the same factors on the simulation side.

For two bands, rule S reads DEPARTS and rule K reads FAIL in the same cells
(`OUTCOME-20261108-1b-precheck-part1.md:41-42`; Part 1's readout [`bands/<band>/rule_S`]):

| band | cells outside [0.9, 1.1] | F_src there |
|---|---|---|
| GEANT_Neutron | R00 R02 R08 R09 R10 R11 | 1.201 1.398 0.863 2.237 0.775 0.701 |
| GEANT_Proton | R01 R05 R07 R08 | 1.166 1.248 1.123 1.101 |

The referee asks whether pseudo-data generation, simulation-side variation, truth definition and normalization represent
the same perturbation. They list "truth/reconstruction weights, flux denominators, simulation resampling and clipping"
(`gpt.txt:23`).

## 2. Each listed operation, against its record

| operation | what the record shows for these two bands | record |
|---|---|---|
| **truth weights** | A carries the dump's truth weights and B the CV's. F_side = √(B/A) is 1 within 6.04e-8 (neutron) and 1.56e-7 (proton) over every resolved cell. For comparison: GEANT_Pion 1.67e-8, MinosEfficiency 2.65e-9 | Part 1's readout [`bands/GEANT_*/factors/F_side`] over [`bands/GEANT_*/resolved/F_src`]; the band diagnosis's own computation, `FD-1B-BAND-DIAGNOSIS-DECLARATION.md:22-24` |
| **flux and denominator** | a universe changes the flux only for band "Flux". The dump's denominator equals the CV's for all 8 detector universes | `nd-unfolding/s5p_universe.py:116` @ `03037c3e`; Part 1's readout [`descriptive/detector_dump_equals_cv`] |
| **simulation resampling** | not part of either compared object. E is a derivation run (every Poisson draw at its mean, no streams). B takes the derivation CV experiment. The MC Poisson(1) streams enter only in the coverage toys | `nd-unfolding/fd_1b_toys.py:22`, `:344-345`; `nd-unfolding/fd_1b_inv.py:495-500` @ `03037c3e` |
| **clipping** | not exercised. The detector factors call `checked_ratio` without `clip_negative`, so a negative ratio refuses the run (`s5p_nullexp.py:152`). The per-universe clip belongs to the interaction-model cache only | `nd-unfolding/fd_1b_precheck_fd.py:106-107`; `nd-unfolding/fd_1b_toys.py:260-261`; `nd-unfolding/s5p_nullexp.py:112` @ `03037c3e` |
| **reconstruction weights** (signal reco and background) | the one operation present on both sides. **Inputs EQUAL:** for all 8 detector universes, the two sides carry the same factor on the same reco rows inside the window (n_differ 0, max_rel_diff 0.0, signal and background) | `OUTCOME-20261109-band-diagnosis.md:23` (P2, #965) |

<!-- absence-ok: "not part of", "not exercised" and "only" are statements about the cited code paths at 03037c3e, scoped to the derivation and Part 1 objects of the two GEANT bands; the Search line covers each site -->

Search: `grep -n -E 'clip_negative|mc_template_streams|expectation=True|if band == "Flux"' nd-unfolding/{fd_1b_toys,fd_1b_precheck_fd,fd_1b_inv,s5p_nullexp,s5p_universe}.py` @ `03037c3e`; `python3 -I` over Part 1's readout (8e05ca9b): max |F_side − 1| over each band's `resolved/F_src` cells.

**The two Part 1 comparisons are one comparison here.** In every κ-resolved cell of the four detector bands,
κ / (F_src · F_side) = 1 to 2.2e-16 in |ln| (`FD-1B-BAND-DIAGNOSIS-DECLARATION.md:22`). The band diagnosis records
rule K's FAIL as the same comparison as rule S's DEPARTS (`OUTCOME-20261109-band-diagnosis.md:22`, P1, #955).

## 3. What the band diagnosis measured beyond the inputs

**Seed.** SEED-STABLE in all 10 departing cells. F_src is identical across seeds 42–54, with the largest sd of ln F_src
4.4e-16 (`OUTCOME-20261109-band-diagnosis.md:24`).

**Scale.** F_src at ε = ½ / 1 / 2, with the factors raised to ε. The scale test reads MIXED in both bands; GEANT_Proton
R08 alone reads CONSTANT (`OUTCOME-20261109-band-diagnosis.md:25`, values at `:30-41`):

| band | cell | F_src (½ / 1 / 2) |
|---|---|---|
| GEANT_Neutron | R00 | 1.097 / 1.201 / 1.042 |
| | R02 | 1.027 / 1.398 / 0.994 |
| | R08 | 0.823 / 0.863 / 1.060 |
| | R09 | unresolved / 2.237 / 1.077 |
| | R10 | 0.779 / 0.775 / 1.047 |
| | R11 | 0.674 / 0.701 / 2.371 |
| GEANT_Proton | R01 | unresolved / 1.166 / 0.897 |
| | R05 | unresolved / 1.248 / 1.012 |
| | R07 | 1.018 / 1.123 / 1.020 |
| | R08 | 1.114 / 1.101 / 1.096 |

**Channels** (the band diagnosis's §4.6, descriptive; `FD-1B-BAND-DIAGNOSIS-DECLARATION.md:89`). "signal" applies the
factor to the signal reco weights only, with the background factor set to 1; "background" does the reverse. F_src at
seed 42 and ε = 1 in the departing cells is from the band diagnosis's readout
[`bands/<band>/channels/<signal|background>/F_src`, `…/resolved`]:

| band | cell | signal only | background only |
|---|---|---|---|
| GEANT_Neutron | R00 | 1.048 | unresolved |
| | R02 | 1.149 | unresolved |
| | R08 | 0.966 | unresolved |
| | R09 | 1.143 | unresolved |
| | R10 | 0.956 | unresolved |
| | R11 | 1.010 | unresolved |
| GEANT_Proton | R01 | unresolved | unresolved |
| | R05 | 1.173 | unresolved |
| | R07 | 1.015 | unresolved |
| | R08 | 1.006 | unresolved |

The background-only blocks are resolved in one cell of GEANT_Neutron (R14) and in no cell of GEANT_Proton
[`…/channels/background/resolved`]. The band diagnosis gives the channels no verdict role. #971 gives them no CITABLE
row.

## 4. What the records conclude, and what they license

**The mapping.** For these two bands, the two constructions match in every operation the referee lists:
- the truth weights, the flux and denominator, simulation resampling and clipping, on §2's records;
- the reco-level weights themselves (inputs EQUAL).

The departure is seed-stable. Whatever separates the two sides "lies inside the estimator, and the declared scale test
does not classify it" (`OUTCOME-20261109-band-diagnosis.md:69-71`). The channel split does not classify it either: it
is descriptive, and the background-only blocks sit at the noise floor. The question is narrowed and not answered. The
control stays restricted, and LL5D's primary reading excludes the two bands (`OUTCOME-20261109-band-diagnosis.md:72-73`).

**CITABLE FOR**, as #971 gives it (`OUTCOME-20261109-band-diagnosis.md:49-55`), with no new licence:
- **§4.3 EQUAL:** "the pseudo-data and the simulation side carry the same factor on the same reco rows inside the window,
  for every detector universe."
- **§4.2 SAME COMPARISON:** as a record of Part 1's committed products, in its licensed wording. On that record, rule
  K's FAIL is not separate evidence.
- **§4.5 MIXED:** the values in the table above, as values.
- From Part 1's outcome (`OUTCOME-20261108-1b-precheck-part1.md:56-58`), unchanged: "for band GEANT_Neutron the
  pseudo-experiments and the simulation side give blocks more than 10 % apart in σ in cells R00, R02, R08, R09, R10,
  R11", and the same sentence for GEANT_Proton in R01, R05, R07 and R08.

§2's four operations are listed with their record lines so that a reader can check each one. This note adds no
sentence licence for them. Whether F2's text may say that they are "measured inert" or "absent" is for the director, and
the wording is Joseph's.

**NOT CITABLE FOR**, as #971 gives it (`OUTCOME-20261109-band-diagnosis.md:57-65`):
- **A mechanism.** MIXED licenses no reading as a non-linearity (SCALES) or a first-order mismatch inside the estimator
  (CONSTANT). GEANT_Proton R08's CONSTANT is a value only.
- **§4.4 SEED-STABLE.** It licenses no sentence.
- **Anything inside the estimator** from §4.3, or HW's rows outside the window.
- **Coverage**, in any form, or that S1's detector block is right. Any repair. The truth dependence (item c).
- **Any paper or note sentence** without the PRD-referee read and Joseph.
- And from this note: the channel values, which are descriptive and carry no CITABLE row in #971.

**Unchanged:**
- Part 1's DEPARTS and FAIL, gate D's FAIL, Part 0 and 1B's rule (iii);
- LL5D's primary reading;
- Joseph's open item on a further study.

Nothing is submitted, deposited or tagged.
