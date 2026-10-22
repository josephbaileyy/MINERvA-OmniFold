# MP-2 S2: implementation readings, for the director's ruling before any fit (2026-10-22)

**By** the measurement session, under binding addenda 8 and 9 and the frozen feature contract
(`measurement-paper/phase1/mp2/feature_contract_draft.json`, sha256 `98141c2f…`).
**Written** before any S2 model was trained. Harmonization (no fit) ran first; see "Status" below.

**CITABLE FOR:** how the S2 code implements each point the frozen contract leaves open, and the cost correction.
**NOT CITABLE FOR:** any result. **None of these is a contract change.** Each is a reading of a point the contract
does not fix. Addendum 8 freezes the contract and requires "a committed record before the affected output exists".
This is that record. If the director rules a reading differently, the code changes before any model output exists.

**Code** (`measurement-paper/phase1/mp2/`):
- `mp2_s2_dump.py` (omnifold_py310) dumps the generator final states.
- `mp2_s2_harmonize.py` (root_6_28) runs the controls, then the harmonized events, the features, the CH products
  and H_CH,an.
- `mp2_s2_fit.py` (root_6_28, LightGBM 4.6) trains the models and runs gates V1–V4.
- `mp2_s2_job.sh` is the batch wrapper.

## Controls run before anything harmonized (fail-closed, exit 3)

| id | what | pass rule |
|---|---|---|
| H0 | `s5p_truths.fine_ratio` on each generator's frozen numerator and the frozen MnvTune truth reproduces A7's `ratios/nullsF/rho-<G>-F.npz` | bitwise; the JSON's three sha256 match |
| N | per-event weights c_e from the frozen chain, histogrammed on the frozen readers' native-convention scalars, reproduce the frozen CH product (GENIE `*_xsec5d_full`, MP3-B `nuwro_CH_xsec5d_full` k1, MP3-C `mp3c_fine_gibuu_frozen` `xsec_CH`) | nevt exactly; xsec and sumw2 ≤ 1e-10 relative (bitwise is not available: the frozen builds multiply after summing) |
| A | this study's readers against the frozen readers | bitwise on every shared stored value (GENIE dump vs RDataFrame; NuWro weight, cc, muon pz/1000 vs flat; GiBUU pt, pz, perweight, E_ν vs `extract_gibuu`); NuWro E_ν = in[0].t/1000 to 1e-12 relative |
| Z | ν along +z | GENIE pxv = pyv = 0 and NuWro in[0].x = in[0].y = 0 on every entry; GiBUU: H non-DIS events balance pT to ≤ 1 MeV |

**Z for GiBUU C12 cannot be checked.** The contract says "asserted per event, GiBUU included". GiBUU writes no
remnant, so C12 events cannot be balanced (preflight §8). Only an H check is possible.

**Z for GiBUU H was redefined after it failed on the first run. This is my own control, not a contract gate.**
- **First definition:** every non-DIS H event (production_ID ≠ 34) balances pT to ≤ 1 MeV. It failed in job
  60101977: 337 of 822,696 events, at most 91 MeV.
- **Diagnosis** (login node, all 80 H tasks; no job). Every one of the 337 is short **0.94 GeV of energy**
  (quantiles 0.1/0.5/0.9: −0.943, −0.941, −0.940 GeV). That is a final nucleon not written, as MP3-C's B1 saw
  (6 of 19,148). By production_ID: 2: 325; 21: 4; 31: 7; 19: 1. None of them balances energy.
- **Why the first definition was wrong.** A missing particle unbalances pT whatever the ν direction. A tilted ν
  unbalances pT **with energy balanced**. The first definition therefore mixed two causes.
- **Second definition** (code-v2): every H event whose energy balances (|ΣE_final − E_struck − E_ν| ≤ 1 MeV)
  balances pT to ≤ 1 MeV. It **failed** in job 60102169: 3,074 events, at most 227 MeV.
- **Second diagnosis** (login node, no job). The 3,074 are exactly the DIS events (production_ID 34) whose energy
  happens to balance. Every one is pT-unbalanced (706,827 DIS in all, 703,753 of them missing energy). By contrast,
  the 822,359 energy-balanced **non-DIS** events balance pT to at most 1.3e-6 GeV. Addendum 9 already records that
  GiBUU DIS final states do not conserve energy or momentum, for a cause not identified, so DIS events cannot test
  the ν direction. Excluding DIS was an oversight in both earlier definitions.
- **Current definition** (code-v3): every **non-DIS** H event whose energy balances to 1 MeV balances pT to
  ≤ 1 MeV. Counted and reported, not tested: the events missing energy (by production_ID) and the energy-balanced
  DIS events with their pT failures.
- **Both redefinitions came after a failure.** Each rests on a measured cause, given above, and the failing
  numbers are kept. What the current check establishes: ν ∥ +z in GiBUU, from the non-DIS H events whose final
  state is complete. GiBUU C12 and GiBUU DIS events remain unchecked.
- **Caveats** (beside addendum 9's DIS caveat): GiBUU H non-DIS events with a final nucleon missing, about 0.04%;
  and GiBUU DIS final states that are inconsistent even when their energy balances.

**NuWro A, also relaxed after the first full run** (code-v2 → code-v3). The check "exactly one muon per CC event"
was a premise drawn from the preflight's subsample. It failed:
- CC events with **three** muons (μ⁻μ⁺μ⁻, so a dimuon pair; each such event has one μ⁺): 42 in C12 main, 5 in C12
  supplement, 5 in H main, 0 in H supplement.
- The binding check holds on every CC event: the last muon, which is the frozen converter's muon, reproduces the
  flat tree's pz bitwise.
- The check is now "at least one muon", with the muon-count table reported. The extra muons are excluded particles
  in every feature.

## Readings (R0–R13)

| # | the contract's text | the reading implemented | why |
|---|---|---|---|
| R0 | "E_avail is MAT's GetEAvailableTrue over the harmonized list"; elsewhere "photons below 10 MeV are dropped from every feature" | E_avail is MAT's function **as written**: γ E, π± E − 135 MeV, π⁰ E, p E − 938.27 MeV, with no threshold, on both sides (Tune = MCgen `MC_eavail`). The γ < 10 MeV drop and the species thresholds apply to the species sums and the leading-particle features | The contract names MAT's function and S1 C3 (bitwise `MC_eavail`); a threshold would make it a different function. On C+H the effect is negligible: 116 photons below 10 MeV in 2.45M C rows of 1A |
| R1 | "validation: 10% of each fold's training rows (seeded)" | 10% of **each class's** training rows, drawn with `default_rng([lgbm_random_state_k, h, f])` (V1: `[v1_split_seed, 1]`) | No validation seed is declared. Per-class keeps both classes in validation |
| R2 | "c fixed so that the in-grid C+H content Σ w_truth w_G equals its value under H_CH,an" | c_k = Σ w_truth r_an / Σ w_truth odds_k over the Tune C+H rows **inside the fine grid and G's E_ν support** (the rows w_G applies to); r_an = H_CH,an's ρ at the row's fine cell; one c per (G, replica) | Rows outside the support keep r_h and take no w_G |
| R3 | V2–V4 (no replica named) | V2, V3 and V4 are evaluated on **every** replica k = 0…4; the gate passes only if all five pass | Conservative; no choice among replicas |
| R4 | V1 (one classifier per G in the cost table, "8 V1 classifiers") | V1 on replica **k = 0** (by position), with its capacity-matched control | Matches the declared cost; k = 0 is chosen before any result |
| R5 | V3: four held-out distributions, "as V2" | bins: neutron multiplicity (KE > 10 MeV) and proton multiplicity (KE > 20 MeV) 0, 1, …, 9, ≥ 10; π⁰ count 0, …, 5, ≥ 6; per-neutron KE spectrum (all neutrons, each carrying its event's weight) [0, 10, 20, 50, 100, 200, 500, 1000, 2000, ∞) MeV | No bins are declared. The per-neutron bins treat the neutrons of one event as independent in sumw2 (stated) |
| R6 | V2 "closure … within the summed sumw2"; V3 "as V2" | **Shape closure.** The reweighted Tune C+H content is scaled to G's total over the fine grid. χ² = Σ (s T − G)² / (s² σ²_T + σ²_G) over the fine cells with ≥ 20 raw entries on both sides, ndf = cells − 1. The same scale applies to the J cells (109 supported), with the pull limit at 3. V3 does the same per distribution, ndf = bins used − 1, and no used bin beyond 3σ | The rate is not testable here. Tune's truth is per nucleon of the whole target mix, and the C+H rows' nucleon share is not in the inputs, so Tune C+H and G's CH product differ by an unknown constant. c fixes the rate to H_CH,an's |
| R7 | V1 control: "trained on G halves of the same sizes" | G's events are split in halves A and B with `gvg_split_seed`. A vs B follows the same protocol as V1 (50/50 train/test, 10% validation), with n_estimators fixed to V1's best iteration | Tune's side has up to 4M rows and G's about 1–2M, so "same sizes" as the V1 samples is not possible. The protocol and the capacity are matched |
| R8 | "G events get folds … keyed by fold_key_k + 1"; JSON: "G-fold = splitmix64(j XOR (fold_key_k + 1)) mod 5 over the generator event index j" | j is the entry's index in the declared file order (C12 main, C12 supplement, H main, H supplement; every entry, CC or not, the same index the ν-direction draw uses). The JSON's formula is taken literally: no `>> 1` for G; for Tune, `(splitmix64(i XOR fold_key_k) >> 1) mod 5` | The JSON is the frozen form |
| R9 | V4 "over the Tune C+H in-grid rows" | over the rows inside G's E_ν support (those carrying w_G); N is their row count | Outside the support w_G is undefined (r_h is kept) |
| R10 | V1 "G's held-out events" | all of G's events inside the grid and the support. Each Tune row is weighted by a model that did not see G's events of the row's own fold; a single classifier cannot keep that pairing | Stated as a limitation of V1's held-out property for G |
| R11 | the struck nucleon (addendum 9) | GENIE `hitnuc` (2112 or 2212, else the default mass, which covers 0 and the pair codes). NuWro: in[1].pdg when n_in = 2; the default mass when n_in = 3 (MEC pair) or n_in = 1. GiBUU: the single perweight-0 ID-1 row by charge, the default mass for production_ID 35 or 36 or when the row is not unique | Addendum 9 |
| R12 | GiBUU IDs not in the map | each (ID, charge) not mapped gets a code below 1e9 that is neither p, n, π, π⁰ nor γ, so it enters E_other, as "other". IDs 901 and 903 and negative IDs stop the job, since none was seen in the preflight and none is declared | Addendum 9 |
| R13 | GENIE targets: "C12 rows tgt == 1000060120, H rows tgt == 2212" | the GENIE CH samples also carry **atomic-electron targets**, `tgt == 11` (CV main: 35 of 2,000,000 entries; supplement 11; MEC main 17). They stay in G's events and the harmonized product, labelled target 0, and are not separated | They are part of GENIE's CH sample and of the frozen CH product (control N reproduces it with them). Found on the first run, when the code's two-target assertion stopped job 60101976 |

## Cost correction (FLAGGED)

The draft's S2-fit estimate (0.7–1.2 CPU node-h for 200 models) does not follow from its own units:
- 200 models × about 150 s is about 8.3 node-h serial at 64 threads, or about 2.1 node-h packed four per node with
  no slowdown.
- So S2 + S3 is more likely about 3.5–5.5 CPU node-h than 2–3.5.

Before the fits, one debug-QOS timing probe (2 models, ≤ 0.1 node-h) measures the cost per model. The projection
then goes to the director before the 200 models are submitted. Phase 1 has charged 7.60 of its 35 CPU node-h.

## Status at writing

**First run** (code in `s2/code`). Its outputs are kept as `harm_a.failed-60101976` and `harm_b.failed-60101977`.
- **60101975, the dump:** COMPLETED in 55 s. Eight samples written.
- **60101976, harmonize GENIE and NuWro:** FAILED with exit 1. The target assertion stopped it (R13).
- **60101977, harmonize GiBUU and Tune:** FAILED with exit 3. Control N passed (xsec 8.8e-15, sumw2 1.2e-14
  relative, nevt exact) and control A passed bitwise on both samples (913,859 C12 and 670,266 H native in-PS
  events). Z failed, as described above.
- **A provenance slip.** 60101976 started 28 s before `mp2_s2_harmonize.py` was re-copied into `s2/code`: it ran
  sha256 `0c92db3b…`, and the file changed under it. The change touched only the GiBUU reader, which that job never
  ran. Since then every submission runs an **immutable** snapshot (`s2/code-v<n>/`, read-only, with its sha256
  list), passed as `CODE`.

**Second run** (`s2/code-v2`, `code-v2.sha256`). Its outputs are kept as `harm_a.failed-60102168` and
`harm_b.failed-60102169`.
- **60102168:** GENIE CV and MEC passed every control and were harmonized. N: xsec 7.6e-13 and 5.3e-13, sumw2
  3.7e-13 and 6.3e-13 relative, nevt exact. A bitwise, Z zero, and H0 bitwise. NuWro passed N (7.3e-13) and stopped
  on A's muon count (above). FAILED with exit 3.
- **60102169:** GiBUU passed N and A, as on the first run, and stopped on Z's second definition (above). FAILED
  with exit 3.

**Third run** (`s2/code-v3`, `code-v3.sha256`; only `mp2_s2_harmonize.py` differs from v2):
- 60102311 (GENIE and NuWro) and 60102312 (GiBUU and Tune). Both COMPLETED 0:0.
- **Every control passed for every generator.**

### Harmonization results (third run; receipts in `s2-receipts/`)

| | entries | inside the phase space | inside the grid | W NaN (W² < 0) | CC at the default mass | in-grid rate (1e-38 cm² per CH nucleon) | H share | N control: xsec / sumw2 max rel |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| GENIE CV | 2,100,000 | 1,006,278 | 1,006,250 | 28 | 13,408 | 2.7644 | 0.0535 | 7.6e-13 / 3.7e-13 |
| GENIE MEC | 2,100,000 | 1,028,217 | 1,028,171 | 46 | 56,213 | 2.8754 | 0.0509 | 5.3e-13 / 6.3e-13 |
| NuWro-CH | 2,375,000 | 1,538,993 | 1,538,953 | 40 | 82,049 | 2.5894 | 0.0508 | 7.3e-13 / 4.2e-13 |
| GiBUU-CH | 3,433,890 | 1,584,128 | 1,580,042 | 605 | 321,667 | 2.1458 | 0.0472 | 8.8e-15 / 1.2e-14 |

- **Tune v1 C+H rows inside the grid:** 31,658,399, of which 1,632,529 are H. Another 1,187,903 rows on other
  nuclei are inside the grid; they keep r_h.
- **H_CH,an (A7's fine construction on the harmonized numerators).**
  - Resolved and fallback fine cells: GENIE CV 3,487 and 6,403; MEC 3,550 and 6,340; NuWro 4,143 and 5,747;
    GiBUU 4,121 and 5,694.
  - Coarse cells reverted to coarse: 0, 0, 0 and 3 (GiBUU).
  - Share of N in resolved fine cells: 0.948, 0.948, 0.958 and 0.906.
- **H0** (A7's F-null rho rebuilt bitwise) passed for all four.
- **The ν draw:** the median drawn beam angle is 1.05–1.06 mrad for every generator.

### Timing probe (60102387, debug)

- **Setup:** GiBUU, F_primary, k = 0, h = 0, folds 0–3. Four concurrent steps of 32 threads, writing to
  `fit_probe/`, which gates never read.
- **Per model:** fit 120–124 s and prediction 20–24 s, so 152–161 s. Up to 9.4 GB resident.
- **Training rows:** 3.6M Tune and 1.14M GiBUU.
- **Best iterations: 3000, 2997, 2973 and 2970.** Early stopping almost never fires before the frozen
  n_estimators = 3000, so the cap binds.
  - Flagged, not changed: n_estimators is frozen.
  - In all four models the validation minimum lies within the last 30 of the 3000 trees.

### Cost projection (measured basis), and the request

| item | basis | CPU node-h |
|---|---|---:|
| 200 models, F_primary | 50 per generator; 4 per node, about 160 s each, plus about 3 min of load per job | about 2.3 |
| gates, 4 × (V1 + control + V2–V4) | 2 fits of about 120 s at 128 threads each, plus histograms | about 0.3 |
| fallback (F_fallback), if F_primary fails | the same again for each generator affected (11 features: a little cheaper) | ≤ 2.3 |
| S3 (contract §8) | 4 × 7 Asimov unfolds and the replay | 0.8–1.7 |
| **S2 + S3** | | **about 3.4–4.3 without fallback; ≤ 6.6 with fallback on every G** |

- **Charged so far for S2:** 0.282 CPU node-h (8 jobs, `../LEDGER.tsv`). Phase 1 stands at 7.885 of its 35.
- **Requested of the director:**
  1. rulings on R0–R13 and on the two Z redefinitions;
  2. authority to submit the 200 F_primary models and the gates. That is about 2.6 CPU node-h, regular QOS
     (debug's 30 min is too short for 12–13 models per step), as 4 jobs of 1 node each, about 45 min per job.

**No production model has been trained.** Only the four timing-probe models exist, in `fit_probe/`, and nothing
reads them.
