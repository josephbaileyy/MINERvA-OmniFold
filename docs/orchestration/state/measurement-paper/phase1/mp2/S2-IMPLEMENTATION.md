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
| R13 | GENIE targets: "C12 rows tgt == 1000060120, H rows tgt == 2212" | the GENIE CH samples also carry **atomic-electron targets**, `tgt == 11`. **CC** events with `tgt == 11`, from the receipt (`harm_a/s2_harmonize.controls.json`, `targets_*`): CV main 1, CV supplement 8, MEC main 0, MEC supplement 17. *(Corrected 2026-10-22: the first version of this row gave entry counts, 35, 11 and 17, that no receipt carries.)* **As ruled in addendum 13 (R13, ruled differently):** they stay in the harmonized product, H_CH,an and control N, as frozen, and are **excluded** from G's training, V1 and V3 samples (target code 0; `mp2_s2_fit.py` `load()`) | The contract's target rule, and MP3-A's precedent. Found on the first run, when the code's two-target assertion stopped job 60101976 |

## Cost correction (FLAGGED)

The draft's S2-fit estimate (0.7–1.2 CPU node-h for 200 models) does not follow from its own units:
- 200 models × about 150 s is about 8.3 node-h serial at 64 threads, or about 2.1 node-h packed four per node with
  no slowdown.
- So S2 + S3 is more likely about 3.5–5.5 CPU node-h than 2–3.5.

Before the fits, one debug-QOS timing probe (2 models announced; **4 ran**, at 0.098 node-h, within the stated
≤ 0.1) measures the cost per model. The projection
then goes to the director before the 200 models are submitted. Phase 1 has charged 7.60 of its 35 CPU node-h.

## Status at writing

**First run** (code in `s2/code`). Job 60101976 wrote **no receipt**: it stopped on a `SystemExit` before writing one, and its cluster directory `s2/harm_a.failed-60101976/` holds no JSON. Only its log is committed (`s2-receipts/logs/`). Job 60101977's receipt is committed as `s2-receipts/harm_b.failed-60101977.s2_harmonize.json`. *(Corrected 2026-10-22: the first version said both runs' outputs were "kept".)*
- **60101975, the dump:** COMPLETED in 55 s. Eight samples written.
- **60101976, harmonize GENIE and NuWro:** FAILED with exit 1. The target assertion stopped it (R13).
- **60101977, harmonize GiBUU and Tune:** FAILED with exit 3. Control N passed (xsec 8.8e-15, sumw2 1.2e-14
  relative, nevt exact) and control A passed bitwise on both samples (913,859 C12 and 670,266 H native in-PS
  events). Z failed, as described above.
- **A provenance slip** (corrected 2026-10-22, addendum 13 D4).
  - The wrapper of 60101976 hashed `mp2_s2_harmonize.py` as `0c92db3b…` at job start. The file was re-copied into
    `s2/code` about 28 s later, as `9dbcde93…`, which 60101977 then recorded for its own run.
  - **Which version 60101976's interpreter read is unrecorded.** It is immaterial: the job produced only a failure,
    and its finding (R13) was reproduced under the immutable `code-v2` and `code-v3`.
  - **The difference between the two versions is shown, not asserted.** Both were rebuilt from the current file by
    reversing the recorded edits in order. Their sha256 match the recorded `0c92db3b…` and `9dbcde93…` exactly, and
    they are committed as `s2-receipts/d4/`. Their diff is one change inside `gibuu_file`, the 901/903 lepton-ID
    stop. 60101976 harmonized GENIE and NuWro only and never called `gibuu_file`.
  - Since then every submission runs an **immutable** snapshot (`s2/code-v<n>/`, read-only, with its sha256 list),
    passed as `CODE`. Addendum 13 makes this standing practice.

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
  *(Corrected after tranche A: only three steps ran together. Step 3 started at 04:38:29, when step 2 ended,
  because each step asked for 120 GiB against the job's 487802 MiB. The per-model figures stand; the 4-way
  concurrency the projection below assumed was never measured. See "Tranche A results".)*
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
     *(Inconsistent as written, as addendum 13 notes: 4 jobs × 45 min is 3.0 node-h, not 2.6. The 13th model wave
     per stream and the gate time were left out.)*

At PR #231 no production model had been trained. Only the four timing-probe models existed, in `fit_probe/`, and
nothing reads them.

## After binding addendum 13 (2026-10-22)

The rulings are in `../../BINDING-PHASE1-ADDENDUM-13.md`, with the reasoning in `../../ADDENDUM-13-ANALYSIS.md`.
Everything in this section was done before any production model was trained.

### Code-v5: the rulings, implemented

The snapshot is `s2/code-v5/`. The directory and its files are read-only, and `s2-receipts/code-v5.sha256` lists
them. It differs from v4 only in `mp2_s2_fit.py` (`91c2a64b…`) and `mp2_s2_job.sh` (`2b800af9…`).

| ruling | where it is implemented |
|---|---|
| R13: `tgt == 11` excluded from G's training, V1 and V3 samples; kept in products, H_CH,an and N | `load()`: the mask `ev["tgt"] != 0`; V3's G side uses the same mask |
| R10: the V1 gate is replica 0's Tune rows of fold 0 (both halves; ≤ 4M by `v1_split_seed`), weighted w_truth·w_G, against G's events of G-fold 0. The pooled V1 runs beside it, descriptive | `cmd_gates`: `V1`, and `V1_pooled_descriptive` |
| R7: the control is two disjoint random subsets of all of G's events (R13 applied), each the size of V1's G sample, drawn with `gvg_split_seed`; V1's protocol; n_estimators fixed to V1's best iteration | `v1_test` |
| R1b: the V1 and control `random_state` are `v1_split_seed` and `gvg_split_seed` | `v1_test` |
| R5b: the 3σ check runs over the χ² bins. Every excluded bin is listed with each side's share, and one-sided bins are flagged as support gaps | `chi2_shape` |
| R6: s is asserted equal across the replicas to ≤ 1e-12 relative (the job stops otherwise). s, ΣG, g0 and the identity s·k_T·f_CH,an are reported | `cmd_gates` (`R6`) |
| R9: the out-of-support row count and its w_truth share per J cell | `cmd_gates` (`R9`) |
| The iteration cap: n_estimators = 3000 as frozen; validation logloss recorded at 500, 1000, 2000, 2500, 2800 and 3000 trees in every fit. If V1's best iteration is ≥ 2800 it is reported "at the frozen capacity", and a descriptive V1 at 10000 trees runs beside it | `fit_one`, `v1_test` |
| **V2 and V3 verdicts held for Joseph:** statistics, p-values and pulls are computed for every replica and written **only** to `fit/sealed_v2v3_<G>_primary.json` (mode 0400). Its sha256 is in the gates file. No V2/V3 pass/fail is computed, and nothing about V2 or V3 is printed. The gates file reports V1 and V4 | `cmd_gates` |
| Production `--out` is `s2/fit/`, never `fit_probe/` | `mp2_s2_job.sh` (`FITDIR`) |

- **Each grant job** runs the `modgates` stage: the 50 models, then, only if every model step exited 0, the gates,
  on the same node.
- **End-to-end test.** Before the snapshot, `mp2_s2_fit.py` `91c2a64b…` ran `models` and `gates` on synthetic
  harmonize outputs: 60k Tune rows, 20k G events, and a **test-only** override to 60 trees. Everything worked:
  - all 50 models, then the gates;
  - V1's fold-0 sample sizes;
  - the R7 control sizes;
  - the R13 exclusion (197 events);
  - R6's s spread (4e-16);
  - the identity's net ratio against the real MCgen (0.9999999);
  - the sealed file, written at mode 0400;
  - no χ² or pull in the open gates file.

  The test's outputs are in `s2/tmp/fittest/` and are never read by anything. Its sealed file was not opened.

### R12: undecayed charmed hadrons (login node, 0 node-h; `s2-receipts/r12_d2_counts.json`)

Counted in the in-grid events that S2 uses, rate-weighted by each sample's own weight. A charmed hadron is any
|pdg| < 1e6 with a quark digit 4; for GiBUU, IDs 56–61 and 114–121.

| sample | in-grid events | with a charmed hadron in the final state | share of in-grid rate |
|---|---:|---:|---:|
| Tune v1 C+H | 31,658,399 | 0 | 0 |
| GENIE CV | 1,006,250 | 0 | 0 |
| GENIE MEC | 1,028,171 | 0 | 0 |
| NuWro-CH | 1,538,953 | 0 | 0 |
| **GiBUU-CH** | 1,580,042 | **4,470** | **7.90e-3** |

**The mismatch is 7.9e-3 of GiBUU's in-grid rate, above addendum 13's 1e-3.**
- Tune, GENIE and NuWro decay charm. GiBUU leaves Λ_c, Σ_c, D and D_s undecayed, so their energy, rest mass
  included, sits in E_other. That is a convention difference the classifier can learn.
- **The GiBUU fit is held** for the director's ruling, as addendum 13 R12 requires. GENIE CV, GENIE MEC and NuWro
  are not affected.

### D2: NuWro's three-muon events (login node, 0 node-h; same receipt)

- **The events:** 52 CC events (42 C12 main, 5 C12 supplement, 5 H main).
- **The primary:** in **all 52**, `post[0]` is the μ⁻, the primary.
- **The muon the frozen converter selects** (the last |pdg| = 13) is **never** `post[0]`. It is the μ⁺ in 34 events
  and a secondary μ⁻ in 18.
- **So in every one of the 52 the frozen NuWro converter, and the harmonized events that keep its convention, take a
  non-primary muon.**
- **Size:** 9 of the 52 are in the grid. Their share of NuWro's in-grid rate is **4.4e-6**, below addendum 13's
  1e-4, so there is no re-run.
- **Proposed KNOWN_ISSUES row, for the director to land:** "LOW. NuWro flat converter (`nuwro_to_flat_5d.C`, 'last
  muon wins') takes a non-primary muon in CC events carrying a μ⁺μ⁻ pair: 52 of 2,374,491 CC events in the frozen
  NuWro C12 and the MP3-B H samples, with the primary always `post[0]`; 9 in the grid, 4.4e-6 of the in-grid rate.
  Affects the frozen NuWro product and MP-2's harmonized NuWro events equally; no re-run at this size
  (`phase1/mp2/S2-IMPLEMENTATION.md`, D2)."

### D1: what the record says (as addendum 13)

- Z for GiBUU, as finally defined, was redefined twice after failures. Each redefinition corrected a mis-specified
  population. The tolerance was unchanged, and the failing counts are kept.
- **Established:** ν ∥ +z on 822,359 complete non-DIS H events (max 1.3e-6 GeV).
- GiBUU C12 inherits this **by jobcard identity**, not by measurement (MP3-C C0). C12 and DIS events stay unmeasured
  for direction.
- The contract's per-event assertion is **not implementable** for GiBUU, and is recorded as such, not as passed.
- **Caveat** beside addendum 9 item 4: about 0.04% of non-DIS GiBUU-H events lack a low-KE final nucleon.
- The azimuthal-mean test that addendum 13 invites (report only) is not yet done.

### The maintenance window (addendum 8's "after the maintenance window")

- **Announced:** `maintenance_20261021`, from 10-21 06:00 to 10-27 23:00 PDT. It is no longer among the
  reservations (`scontrol show reservation`, 2026-10-22).
- **Measured return:** user jobs started again at **2026-10-21 17:28:57 PDT**. Source: `sacct -a -X`, the first
  start after 06:00, read 2026-10-22.
  - Starts per hour on 10-21: 365 at 17:00, 15 at 18:00, 11 at 19:00, 1,390 at 20:00, 4,046 at 21:00.
  - The only other start in the window, 4662497 at exactly 06:00:00, is read as the reservation's own boundary.
- **So:** every S2 job (from 2026-10-22 04:15 PDT) ran after Perlmutter's actual return.

### A second, harmless write into a snapshot

- My R12 login-node script imported from `s2/code-v4/` without `PYTHONDONTWRITEBYTECODE`. That created
  `code-v4/__pycache__/` (one `.pyc`) at 07:10 PDT.
- No `.py` changed: `sha256sum -c code-v4.sha256` gives 0 mismatches, and no job ran from v4 after the probe. The
  directory was removed.
- `code-v5/` is now read-only at the **directory** level too, so nothing can write into it.

### Production plan (tranche A)

- **Jobs:** one per generator. QOS regular, 1 node, `--time 1:30:00`. Stage `modgates`, F_primary, with the 50 tasks
  (k, h, f) in 4 concurrent streams of 13, 13, 12 and 12.
- **GENIE CV, GENIE MEC and NuWro** are submitted on this record. **GiBUU waits** for the R12 ruling.
- **Projected wall time per job, from the probe:** about 45 min (13 waves of about 157 s, about 3 min of load, and
  gates ≤ 8 min). That is about 0.75 CPU node-h per job and about 3.0 for tranche A.
- **Stop rule (addendum 13):**
  - a job past 56 min (1.25 × 45) is cancelled and reported;
  - before each further submission, the charged total plus the remaining jobs' projections must stay ≤ 3.5.

## Tranche A results (2026-10-22)

All three jobs ran code-v5 (`mp2_s2_fit.py` 91c2a64b, `mp2_s2_job.sh` 2b800af9) on regular QOS. Receipts are in
`s2-receipts/tranche-a/`:

- the two open gates files;
- every model's metadata (`tranche_a_model_meta.json`);
- the three job logs.

The sealed V2/V3 files are not copied, read or summarized here. Each gates file records only the sealed file's path
and sha256.

| job | generator | state | elapsed | CPU node-h | models | gates |
|---|---|---|---:|---:|---:|---|
| 60107470 | genie_cv | COMPLETED 0:0 | 479 s | 0.13306 | 50/50 | ran, rc 0 |
| 60107471 | genie_mec | COMPLETED 0:0 | 460 s | 0.12778 | 50/50 | ran, rc 0 |
| 60107472 | nuwro_ch | CANCELLED (stop rule, 3390 s) | 3397 s | 0.94361 | 49/50 | not run |
| | | | | **1.20445** | | |

Phase 1 now stands at 9.089 CPU node-h of its 35 (`../LEDGER.tsv`). Tranche A has 2.296 left of its 3.5.

### V1 and V4 (reported normally, addendum 13)

| generator | V1 AUC (R10 sample) | G-vs-G control | pass rule | V1 | V4, all 5 replicas | c (replicas 0–4) | best iteration min/median/max |
|---|---:|---:|---|---|---|---|---|
| genie_cv | 0.49723 | 0.50444 | AUC ≤ control + 0.005 | pass | pass | 1.0327–1.0336 | 29 / 41 / 64 |
| genie_mec | 0.49351 | 0.50133 | AUC ≤ control + 0.005 | pass | pass | 1.0700–1.0711 | 14 / 28 / 43 |

- **V4 detail:** ESS/N is 0.932–0.935 on every replica of both generators. max w_G/mean is ≤ 3.68, and no row is above
  50× the mean.
- **V1 provenance:** `at_frozen_capacity` is false for both generators. The V1 fits stopped early, at best
  iteration 3 for genie_cv and 1 for genie_mec, far below 2800, so no `V1_10000_descriptive` was owed.
  - The code fits each G-vs-G control at its V1 fit's best iteration, so the controls are also 3 and 1 trees.
  - A V1 pass here means a fresh classifier found no separation at all. It is not a small separation under the
    margin.
- **V1 pooled (descriptive, R10):** AUC is 0.49878 for genie_cv (control 0.50147) and 0.49903 for genie_mec
  (control 0.50066).
- **R6:** s varies across replicas by ≤ 4.5e-15 relative. The identity's net ratio is 1 − 1.7e-8 for genie_cv and
  1 + 8.7e-9 for genie_mec.
- **R9:** 18 Tune rows are outside support. That is 6.9e-7 of w_truth, in 3 of the 109 J cells (the largest
  share of a cell is 1.6e-5).
- **R13:** 9 genie_cv and 16 genie_mec events on tgt 0 are excluded from training.
- **S2 verdict for both generators:** not determined. It waits for the V2/V3 release.

The GENIE classifiers learn almost nothing. Validation loss bottoms out within 14–64 trees, compared with 1548–2998
for NuWro. In F_primary, GENIE CV and MEC are close to the GENIE-based Tune. This is a description, not a gate.

### NuWro: why it overran, and what the stop rule caught

- **Per model, as projected:** 49 models, wall time 91–162 s (median 148 s), best iteration 1548–2998 (median
  2710). 23 of the 49 are at or above 2800.
- **The concurrency was not as projected.** Each of the 4 concurrent model steps asked for `--mem=$((480/NG))G`,
  which is 120 GiB, for 480 GiB in total. The allocation is 487802 MiB, about 476 GiB. Slurm therefore held
  step 3 ("step creation temporarily disabled … Requested nodes are busy") until step 0 ended at 08:22:40. Step 3
  started at 08:23:57 and ran its 12 models one after another. It had finished 11 when the stop rule cancelled it.
  The missing model is k4h1f2.
- **The same serialization in every code-v5 run:**
  - in the probe (60102387: step 3 started 04:38:29, when step 2 ended);
  - in both GENIE jobs (60107470 step 3 at 07:39:28; 60107471 at 07:40:21).
- **Why GENIE didn't overrun:** its models take about 12 s, so the serialization cost under 3 min.
- **What this corrects:** my 45-min projection for tranche A rested on four concurrent streams that the probe never
  showed. The probe section above now says so.
- **Gates:** they did not run for NuWro, so no V1, V4 or sealed V2/V3 file exists for it.

### The fix: code-v6 (job script only)

- `mp2_s2_job.sh` 72920b23 sizes each model step from the job's own allocation:
  `--mem=$(( SLURM_MEM_PER_NODE × 95/100 / NG ))M`. That is 115852 MiB × 4, or 463411 MiB for a single step.
- It prints the split. It fails loudly if `SLURM_MEM_PER_NODE` is unset.
- The models peaked at 8.8 GiB resident, so 113 GiB per step leaves a wide margin.
- Every other file is byte-identical to code-v5 (`s2-receipts/code-v5.sha256` against `code-v6.sha256`; the diff is
  line 8 only).
- Snapshot: `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp2/s2/code-v6`, with the directory at 0555 and the
  files at 0440.
- **Not yet run:** the fix is unverified until a job shows four steps starting at the same time.
- `mp2_s2_fit.py models` skips any model file that already exists. A rerun therefore trains only what is missing
  and leaves the 49 NuWro models as they are.

### Proposed next jobs (not submitted: the stop rule says stop and report)

| step | job | projection | stop at (1.25×) | CPU node-h |
|---|---|---|---|---:|
| 0 | debug: 4 concurrent `srun --exact -c 64 --mem=<code-v6 split> sleep 60` steps; pass if all four start within 5 s | 2 min | 3 min | ≤ 0.04 |
| 1 | nuwro_ch `modgates` on code-v6, one group `4:1:2` (128 threads), then gates | about 3 min load + 3 min model + ≤ 15 min gates (two V1 fits that run to about 3000 trees, plus `V1_10000_descriptive` if the V1 fit reaches 2800) | 26 min (projected 21) | about 0.35 |
| 2 | gibuu_ch `modgates` on code-v6, after the R12 ruling | 13 waves × 157 s + 3 min load + ≤ 15 min gates, about 52 min | 65 min | about 0.87 |

- **Total:** charged 1.204 plus about 1.26 projected, about 2.47. That is within tranche A's 3.5.
- **Order:** step 1 runs only after step 0 passes, and step 2 only after the R12 ruling.

### Steps 0 and 1 (director-approved), and code-v7

- **Step 0, attempt 1 (60112440, debug, 4 s):** the test ran code-v6's memory expression and stopped at its own
  guard. Perlmutter leaves `SLURM_MEM_PER_NODE` unset when sbatch gives no `--mem`. code-v6 therefore could not
  run any `models` stage. It was never used for production.
- **code-v7:** the memory reader moves into a sourced file, `mp2_s2_slurm_mem.sh` (8be83253).
  - It returns `SLURM_MEM_PER_NODE` when that is set, and otherwise the `mem=` of the job's `AllocTRES` from
    `scontrol show job`, in MiB.
  - It exits 4 on a value it cannot parse.
  - Under bash, with a mocked scontrol, it reads 487802M → 487802, 476.36G → 487792 and 1T → 1048576, and returns
    exit 4 for `bogus` and for an empty value.
  - `mp2_s2_job.sh` (e84c9da4) sources it. The other 14 files are byte-identical to code-v6, and so to code-v5
    (`s2-receipts/code-v7.sha256`).
  - Snapshot: `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp2/s2/code-v7`, with the directory at 0555 and the
    files at 0440.
- **Step 0, attempt 2 (60112509, debug, 68 s): PASS.**
  - `mp2_s2_step0_concurrency.sh` (08ce14e2) sources the same reader from `$CODE`.
  - With `SLURM_MEM_PER_NODE` empty, it read 487802M from AllocTRES.
  - Its four `srun --exact -c 64 --mem=115852M` steps all started at 09:08:23 by sacct, within 30 ms in the log.
  - Receipts: `s2-receipts/tranche-a/logs/`.
- **Step 1 (60112561):** nuwro_ch `modgates`, F_primary, on code-v7, with the single task group `4:1:2`. Regular
  QOS, limit 40 min, cancelled by the watcher past 26 min.
  - COMPLETED 0:0 in 475 s (0.13194 CPU node-h), under the stop rule.
  - The log shows one model step of 463411M (95% of 487802M).
  - The model, k4h1f2, reached best iteration 2959 in 285 s at 128 threads. The gates then ran on all 50 models
    (`s2-receipts/tranche-a/`).

### NuWro F_primary: V1 and V4 fail (reported normally, addendum 13)

| gate | result | bar | verdict |
|---|---|---|---|
| V1 (R10 sample) | AUC 0.55325, G-vs-G control 0.50244 | AUC ≤ control + 0.005 | **fail** |
| V4, replicas 0–4 | ESS/N 0.0255–0.0557; max w_G/mean 12,274–25,923; share of rows above 50× the mean 1.21e-4–1.32e-4 | ESS/N ≥ 0.3 and max w_G/mean ≤ 50 | **fail on all five** |

- **V1 detail:** the V1 fit stopped at best iteration 30, and its control was fitted at 30. `at_frozen_capacity` is
  false.
- **V1 pooled (descriptive):** AUC 0.56640, against control 0.50040.
- **c:** 1.1378–1.1418.
- **R6:** s varies across replicas by ≤ 1.7e-15 relative. The identity's net ratio is 1 + 2.7e-10. g0 is 1.6e-3.
- **R9:** as for GENIE (18 rows, 6.9e-7). **R13:** 0 NuWro events on tgt 0.
- **S2 for NuWro on F_primary fails whatever V2/V3 show.** V1 and V4 both fail, and S2 needs every gate. The V2/V3
  statistics are sealed (`c07d4adf…`) and unread. They are released with the others under addendum 14, by the same
  script.
- **Next, under the contract's order (JSON `order`):** "on failure, F_fallback (once, before S3); failure again ->
  'not established' for that G, A7's hybrid result stands". Addendum 13 releases tranche B (≤ 2.3) "only after a
  reported F_primary failure for that G". This is that report.
  - **Not submitted:** NuWro F_fallback `modgates`, the same 50 tasks in 4 concurrent streams on a snapshot carrying
    code-v7's launcher.
  - **Projection:** 13 waves × about 150 s, plus about 3 min of load and ≤ 15 min of gates, is about 52 min. That is
    about 0.87 CPU node-h, with a stop at 65 min.
- **Context, descriptive only:** S0 had already seen V4 fail by a wide margin for NuWro C12 against Tune with full
  features (JSON `F_fallback` note). The fallback was declared for that reason, on response grounds.

## The V2/V3 release (binding addendum 14 §2)

### The verdict script

`measurement-paper/phase1/mp2/mp2_s2_verdict.py`, sha256
`6e6c1614ca5074a7fefdfc2b35a46306a0e2bff39e2b92dadc09c4bc0b1aad94`, revised after the independent review (below; the
first version, c088e126, was never run on study data): no refit, 0 node-h, root_6_28. It imports
`mp2_s2_fit.py` (91c2a64b, unchanged since code-v5) for the frozen bins, the 20-entry minimum and `chi2_shape`, so the
statistics are those the gates computed. In order:

1. **Blind.** ndf_fine comes from raw counts only: Tune rows in G's support per fine cell, and G's `nevt_flat`. If it
   is < 200, the script prints STOP and exits 5 before the sealed file is opened.
2. **The seal.** The sealed file's sha256 must equal the one the gates file recorded, and its `stat` is taken before
   and after (asserted unchanged). The script never writes the sealed file.
3. **Proof that the weights are the sealed run's.** From `weights_<G>_<fset>.npz` and the harmonized arrays, the
   script recomputes V2-fine (χ², s, ndf), the 109 J pulls and the four V3 distributions in their frozen form. Each
   must equal the sealed value to ≤ 1e-12 relative, or the script stops.
4. **V3-n.** The neutron KE distribution is recomputed with the event-clustered variance Σ_e (n_e,b w_e)² on both
   sides. Contents and raw entry counts are unchanged.
5. **§2's rules, per replica, all five required:**
   - V2-fine: χ²/ndf ≤ 1.5.
   - V2-J: max |pull| ≤ 3.4970. Exactly 109 finite pulls are asserted, and the script recomputes the Šidák bar
     (3.49703) and asserts it equals 3.4970 to 5e-5.
   - V3: p_d = min(1, 2 min(p_χ, p_z)) with the Šidák p_z over d's used bins. It passes iff min p_d > 0.0125, and
     ndf < 1 fails closed. Holm-adjusted p's are reported.
6. **Output.** The script writes `verdict_v2v3_<G>_<fset>.json` at 0444 and never overwrites it. The file carries
   every bar, the seal's stat before and after, the across-replica correlation of the J pulls (descriptive), V1 and
   V4 from the gates file, and S2 = V1 ∧ V4 ∧ V2-fine ∧ V2-J ∧ V3.

`--harm` and `--contract` are explicit. They must equal the gates run's argv when that argv records them, as it does
in production (the gates file stores `sys.argv`). The harmonized inputs' sha256 are checked against the gates file's
`sources` either way.

### Tests (no study output)

- **`test_mp2_s2_verdict_units.py`** (local), against independent computations:
  - Holm against its step-down definition, 200 random draws, including "min p > 0.0125 ⇔ Holm rejects none";
  - the Šidák p against the direct formula;
  - the clustered variance against a brute-force double loop, and ≥ the per-entry sumw2;
  - the ndf < 1 fail-closed path.
- **One rounding note:** at the bar as written, 3.4970, the chance failure is 0.050005, not 0.05.
- **`test_mp2_s2_verdict_e2e.py`** (a Perlmutter login node, synthetic data in
  `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp2/s2/tmp/vtest`) ran `mp2_s2_fit.py` models and gates at 60
  trees, and then the verdict script:
  - **NCELLS = 0, 3 fine cells in each of the 109 J cells:** blind ndf_fine 326. The recomputation equalled the seal,
    109 pulls, the clustered variance was tagged, and the seal's stat was unchanged.
  - **Refused, as required:**
    - a second run (no overwrite);
    - weights perturbed by 1e-6 relative in one replica: "replica 3 V2-fine chi2: recomputed … differs from sealed …";
    - a one-byte edit to the seal: "sha256 differs from the gates file's record".
  - **NCELLS = 100:** blind ndf_fine 99, so STOP with exit 5 before the seal was opened.
  - The committed e2e file differs from the one that ran only in its docstring's second line. The verdict script is
    byte-identical to the tested copy.
- **A finding the tests made:** the gates file's `argv` is the caller's argv when gates run in-process. That is why
  `--harm` and `--contract` are explicit arguments rather than read from it.

### Revision after the independent review of PR #238

The director had the first version, c088e126, reviewed against addendum 14 §2 before any run. The review's blocking
finding was real: a NaN could produce a V3 PASS. `min(1, 2·NaN)` is 1, and `abs(a − b) > tol` is False for a NaN, so
the equality check against the seal accepted NaN. The fixes, in 6e6c1614:

- **Blocking: NaN.** `finite()` STOPs on any non-finite value, so a NaN or inf becomes neither PASS nor FAIL. It is
  applied to:
  - the inputs: G's xsec, sumw2 and nevt; Tune's w_truth; G's c; the fine widths; every replica's w_G and c; and the
    V3 values;
  - both sides of every recomputed-versus-sealed comparison;
  - V2-fine's χ²/ndf;
  - V3's χ², z_max, p_χ, p_z and p_d.
- **Should-fix.** For every V3 distribution, the frozen-form `max_abs_pull_used` and `n_bins_used` are now compared
  with the seal, as well as χ² and ndf.
- **Minor:**
  - Bin indices outside [0, nb) STOP, both at the upper edge and in `clustered`, so nothing wraps into the next
    event's bin.
  - The files actually opened from the `--harm` paths are hashed and must equal their records. The events and Tune
    files are checked against the gates file's sources, path and sha256, and `harmonized_<G>.npz` against harmonize's
    own `s2_harmonize.json` outputs. The gen5d modules that give the fine widths are recorded through
    `gen5d_flux_reweight.code_files_of`.
  - The seal is read once: those bytes are hashed and parsed.
  - The overwrite check comes before the seal is opened, and the output is written with `O_EXCL`, then set to 0444.
  - A distribution with ndf < 1 is reported as "FAIL-CLOSED" (p_d none) and fails V3. It is not reported as p_d = 0.
  - `N_V3 == len(V3_BINS)` is asserted at import.
  - atime is recorded beside the seal's stat. It is not compared, because the read itself may move it.

**Tests of 6e6c1614.**
- **Units** (`test_mp2_s2_verdict_units.py`): all of the above, plus:
  - NaN and inf in `same` (5 cases) and in `v3_rule` (χ² and z_max), each a STOP;
  - an empty or NaN vector to `finite`, a STOP;
  - bin indices out of range in `clustered`, a STOP;
  - the FAIL-CLOSED label;
  - a 3-member V3 family, refused at import.
- **End to end** (`test_mp2_s2_verdict_e2e.py` a703d271, on Perlmutter; output in
  `s2-receipts/verdict-tests/e2e-6e6c1614.out`):
  - `--blind-only` exits 0 and writes no verdict.
  - The full run writes the verdict at 0444, with the seal's stat unchanged and four inputs hashed.
  - **Refused:**
    - a second run;
    - an existing verdict beside an unreadable (mode 000) seal, refused before the seal is opened;
    - weights perturbed by 1e-6;
    - a NaN weight;
    - a one-byte edit to the seal;
    - a NaN planted through `chi2_shape` into V2-fine's χ², a frozen V3 χ², a frozen V3 z_max, V3-n's χ² and V3-n's
      z_max, each a STOP.
  - The blind shortfall stops with exit 5, in both modes.
  - Both files ran byte-identical to the committed ones.

### The run (after this PR)

The script runs from a read-only snapshot,
`/pscratch/sd/j/josephrb/measurement-paper/phase1/mp2/s2/verdict-v2/`: code-v7 plus 6e6c1614, with its sha list in
`s2-receipts/verdict-v2.sha256`. (`verdict-v1/`, holding c088e126, is superseded and never ran.) It runs on a login
node, only after the director merges #233 and #238:

1. `--blind-only` for genie_cv, genie_mec and nuwro_ch. §2's ndf_fine ≥ 200 holds for "any G", so all three are
   checked before any verdict is read.
2. The full run for each, on F_primary. NuWro's F_fallback and GiBUU follow when their seals exist.

The seal stats were recorded before the run:
- `s2-receipts/sealed-stat-before-release.txt` (16:28Z);
- `s2-receipts/sealed-stat-atime-before-release.txt` (16:47Z), with atime. For all three seals, atime equals mtime
  equals ctime, so none has been read since it was written.

## R12: GiBUU's charm decayed (binding addendum 14 §4), code-v8

### The decayer: the PYTHIA6 branch of the ruling

- **Library and table** (a read-only research pass, receipts under `s2/tmp/charm-research/` with `SHA256SUMS.txt`).
  The frozen GENIE samples were made with GENIE 2.12.10 from larsoft CVMFS. Its UPS table requires pythia
  v6_4_28k gcc640-prof, and the log banner reads "PYTHIA version 6.426".
  - Library:
    `/cvmfs/larsoft.opensciencegrid.org/products/pythia/v6_4_28k/Linux64bit+3.10-2.17-gcc640-prof/lib/libPythia6.so`,
    sha256 `670555a4…`.
  - Table: its PYUPDA(1) dump has sha256 `6e0fbd89…`. Every charm parent's branching ratios sum to 1 within
    4.4e-16.
  - code-v8 asserts both hashes. The dump is taken in a child process, because a Fortran unit is not flushed while
    its process lives. The first in-process hash differed for that reason, and the assertion stopped it.
- **The ROOT fallback cannot run.** In TDatabasePDG's table (`pdg_table.txt` `ff74b737…`), 73.0% of Λc's
  branching ratio and 34.5% of Ds's go to quark and diquark final states, which phase space cannot hadronize. So
  only PYTHIA6 decays, or exclusion, remain.
- **Flags, as GENIE's `PythiaDecayer`:** MSTJ(22) = 1 and π0 stable (MDCY(π0,1) = 0), PYTHIA defaults otherwise.
  Each parent is placed alone in PYJETS with GiBUU's own four-momentum, its mass taken from E² − p², and PYEXEC
  cascades it. GENIE's charm events contain p, n, π, K±, K0L, γ, e, μ and ν, and no K0S, Λ or Σ. These decays
  give the same species.
- **The ID map** comes from GiBUU 2019's `code/database/IdTable.f90` (sha256 `67b31fd5…`):
  - baryons: 56 Λc+, 57 Σc, 58 Σc*, 59 Ξc, 60 Ξc*, 61 Ωc;
  - mesons: 108 ηc, 109 J/ψ, 114 D (0: D0, +1: D+), 115 D̄, 116 D*, 117 D̄*, 118/119 Ds±, 120/121 Ds*±.

  Each PDG code is asserted against PYTHIA's own name (PYNAME) before use. A charm (ID, charge) pair outside the
  map has no decay, so the fallback applies.
- **An explicit reading of addendum 14 §4: Ξc is decayed as well.** GiBUU writes Ξc0 and Ξc+ (ID 59, 34 parents
  across the C12 and H samples). The ruling names Λc, Σc, D and Ds, but its intent is every charmed hadron, and
  R12's count rule covered IDs 56–61. The director confirmed this reading.
- **The random numbers:** `default_rng([2026102134, 0x4348])` gives one integer in [0, 9e8) per parent, in the
  declared order (C12 files, then H, each in event order and list order). It becomes MRPY(1), with MRPY(2) = 0, so
  PYTHIA is reseeded before every parent. The decay happens in the generator frame, before the rotation.
- **Fail-closed checks**, each recorded with its pass flag:
  - known codes;
  - the declared table;
  - BR sum = 1 to 1e-6 for every species PYTHIA decayed;
  - per-parent four-momentum to 1e-9 of the parent's E;
  - PYTHIA's error counter MSTU(23) unmoved;
  - no charm in any product;
  - every product species in Tune's C+H in-grid lists, which are read from all twelve S1 playlists at run time;
  - event four-momentum unchanged.

  If any check fails, the branch is the fallback: the lists stay as GiBUU wrote them, and the charm events are
  excluded from the training, V1 and V3 samples, as in R13. The branch comes from these flags alone.
- **What is reported, beside the harmonized product (descriptive):**
  - the parent mix and the product species;
  - the number of events changed and their in-grid rate share;
  - E_avail shift quantiles;
  - the c-weighted shifts of the five species sums;
  - the ratio of the in-grid rate, decayed to undecayed;
  - `harmonized_gibuu_ch_undecayed.npz`, the same harmonization without the decays, for the per-J-cell Δμ_c/σ_c
    readout beside A7.

### Tests (no study output; `s2-receipts/code-v8-tests/`, run against the code-v8 snapshot itself)

- **`test_mp2_s2_charm.py`**, real PYTHIA6, synthetic GiBUU lists. Six parents (Λc+, D0, D+, Σc++, Ds+, Ξc0)
  across four of six events. Results:
  - every check passed;
  - worst four-momentum residual 3.5e-16, worst BR deviation 4.4e-16 over 13 decayed species;
  - events without charm byte-identical, parents replaced in place, and the Ξ (ID 53, not charm) kept;
  - the same products on a second call;
  - an unknown code (61, +1) gives no decays;
  - a Tune species set without K0L fails the species check.
- **`test_mp2_s2_r12_smoke.py`**, real inputs: two C12 `FinalEvents.dat` (47,562 events, 164 charm parents) and one
  S1 playlist's Tune species (28 species). Results:
  - branch "decayed", every check passed;
  - E_avail rose in 162 events, median +3.23 GeV, maximum +9.70 GeV. Undecayed charm counts zero, which is
    KNOWN_ISSUES row 102.

### GENIE's charm, before the GiBUU fit (`s2-receipts/r12_genie_charm.json`, 0 node-h)

| generator | gst entries with `charm` | in-grid events with `charm` | share of the in-grid rate (Σ c) |
|---|---:|---:|---:|
| genie_cv | 21,279 of 2,100,000 | 12,908 of 1,006,250 | 1.334% |
| genie_mec | 20,721 of 2,100,000 | 12,456 of 1,028,171 | 1.225% |

GENIE makes charm, and decays all of it: no final state (`pdgf`) in any of the four gst files carries a charm
hadron, while `pdgi` does. So Tune's generator decays charm rather than making none. GiBUU's 0.79% undecayed
in-grid share is that difference. The readout script is `mp2_s2_r12_genie_charm.py`, and it checks the events
file's sha256 against harmonize's record.

### code-v8 and what runs next

- **Snapshot:** `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp2/s2/code-v8` (directory 0555, files 0440), sha
  list `s2-receipts/code-v8.sha256`. Relative to code-v7, it adds `mp2_s2_charm.py` (abc80109) and changes
  `mp2_s2_harmonize.py` (01168131) and `mp2_s2_job.sh` (0ba34f5c). The job script gains `HARM_FIRST`, a directory
  searched before harm_a and harm_b, so that GiBUU's re-harmonized files win for GiBUU only.
- **Then, approved in addendum 14 §7, in order:**
  1. GiBUU re-harmonization on debug: `harm c gibuu_ch` into `harm_c/`, about 0.03 node-h, with controls N, H0, A
     and Z and H_CH,an rebuilt.
  2. GiBUU `modgates` on code-v8 with `HARM_FIRST=$D/harm_c`, about 0.87 node-h, stopping at 65 min.
