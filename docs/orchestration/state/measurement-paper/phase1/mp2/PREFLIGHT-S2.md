# MP-2 S2 preflight: the harmonization items of the frozen feature contract, measured

**By** the measurement session, 2026-10-20, under binding addendum 8, ruling (g). The frozen contract is
`measurement-paper/phase1/mp2/feature_contract_draft.json`, sha256 `98141c2f…`.

**Scope.** This is a report only. It has no gate and no threshold, fits nothing, computes no weight, and changes
nothing in the contract. Every item that would need a contract change is **FLAGGED** for the director in §7.

**Method.**
- Login-node reads only (saul): no job, 0 node-h, nothing written to CFS.
- CC events only, at most 100k per main sample and 20k per supplement. All energies are in MeV.
- Code: `measurement-paper/phase1/mp2/mp2_s2_preflight.py` (sha256 `68ff9da9…`, identical on the cluster) and
  `mp2_s2_preflight_gibuu_balance.py` (`6e9a634e…`).
- Output: `preflight/preflight_s2.json` (`882d5657…`), `preflight/gibuu_H_balance_task1001.txt` and
  `preflight/tune_lowE_photons_1A.txt`.

**Samples read.**

| sample | source | CC events read |
|---|---|---:|
| GENIE CV | first 100k gst entries | 73,874 |
| GENIE CV supplement | first 20k entries | 15,048 |
| GENIE MEC | first 100k gst entries | 74,775 |
| GENIE MEC supplement | first 20k entries | 15,038 |
| NuWro C12 | `nuwro_p1` | 99,987 |
| NuWro C12 supplement | `nuwro_supp` | 19,978 |
| NuWro H main | MP3-B chunks c01–c10, the `RESULT` attempts | 99,960 |
| NuWro H supplement | MP3-B chunks c01–c04 | 19,939 |
| GiBUU C12 | tasks 1–5 | 118,863 |
| GiBUU H | MP3-C tasks 1001–1006 | 114,732 |
| Tune v1 | 100k S1 rows of 1A (seed 2026102150) | 100,000 |

## 1. Codes outside the particle table, and nuclei

| sample | nuclei (pdg ≥ 1e9) | pseudo-particles (pdg ≥ 2e9) | other codes outside a standard PDG table |
|---|---|---|---|
| GENIE CV / MEC (gst `pdgf`) | 1000060120: 687 / 612 (the coherent recoil nucleus; hitnuc = 0) | none | none |
| GENIE supplements | 1000060120: 46 / 36 | none | none |
| NuWro (all four) | none | none | none |
| GiBUU | none in the final state (no remnant is written) | none | GiBUU IDs, not PDG codes; see §4 |
| Tune v1 (MAD `mc_FSPart`) | 1000060120, 1000080160, 1000130270: 1,158 | **2000000101 (GENIE "bindino"): 13,980** | none |

- The contract's exclusion of pdg ≥ 1e9 removes all of these.
- **The gst `pdgf` list does not contain the primary muon.** Of 73,874 CC events, 73,825 have no μ in `pdgf`; the rest
  carry 1–2 secondary muons. The primary lepton is gst `El/pxl/pyl/pzl`. NuWro's `post` and the MAD list each have
  exactly one muon per CC event.

## 2. Photons below 10 MeV (de-excitation)

| sample | photons | E < 10 MeV | events with one below 10 MeV |
|---|---:|---:|---:|
| GENIE CV / MEC | 5,421 / 5,408 | 4 / 4 | 4 / 4 |
| GENIE supplements (CV / MEC) | 5,383 / 5,290 | 4 / 9 | 4 / 9 |
| NuWro C12 / C12 supplement | 6,435 / 4,318 | 0 / 2 | 0 / 2 |
| NuWro H / H supplement | 5,040 / 4,309 | 3 / 3 | 3 / 3 |
| GiBUU C12 / H | **0 / 0** | 0 | 0 |
| **Tune v1** | 7,497 | **1,308** | **1,304 (1.3%)** |

- **Tune v1's low-energy photons are oxygen de-excitation lines.** In all of 1A (2,682,267 rows), 34,199 of the
  34,322 photons below 10 MeV are on Z = 8. On carbon there are 116 in 2,451,873 rows, and on H 5. The common energies
  are 6.18, 6.32, 7.03, 3.68 and 4.44 MeV. The contract's C+H training rule therefore removes them from training.
  They still sit in `MC_eavail` for the O rows, which keep r_h.
- **GiBUU writes no photons at all.** Its π⁰ are stable in FinalEvents. See also §6.

## 3. Effect of each declared threshold

Counts are particles above / at or below the cut, and in brackets the number of events with at least one above.

| sample | p, KE > 100 | n, KE > 50 | π±, KE > 50 | γ, E > 10 | π⁰ | other |
|---|---|---|---|---|---:|---:|
| GENIE CV | 59,302 / 42,446 (44,530) | 51,037 / 19,801 (35,703) | 81,573 / 5,771 (50,398) | 5,417 / 4 | 43,978 | 9,350 |
| GENIE MEC | 60,942 / 45,494 (45,584) | 51,654 / 21,126 (36,114) | 80,430 / 5,589 (49,363) | 5,404 / 4 | 43,262 | 9,175 |
| NuWro C12 | 72,449 / 33,529 (62,833) | 41,072 / 15,833 (34,987) | 100,331 / 5,242 (65,703) | 6,435 / 0 | 57,652 | 11,885 |
| NuWro H | 80,230 / 7,194 (80,213) | 9,117 / 59 (9,116) | 132,468 / 5,879 (95,454) | 5,037 / 3 | 54,980 | 10,674 |
| GiBUU C12 | 129,641 / 92,641 (90,141) | 89,166 / 44,138 (56,317) | 104,284 / 5,824 (69,489) | 0 / 0 | 57,474 | 129,871* |
| GiBUU H | 98,705 / 4,501 (98,689) | 7,400 / 32 (7,393) | 137,124 / 6,224 (108,820) | 0 / 0 | 50,065 | 123,852* |
| Tune v1 | 80,763 / 71,243 (60,978) | 65,608 / 33,329 (45,662) | 98,580 / 7,342 (61,430) | 6,189 / 1,308 | 52,639 | 11,159 |

- The "other" species is mostly kaons and hyperons: K±, K⁰/K̄⁰, K_L, Λ, Σ.
- \*For GiBUU, "other" includes one muon per event under the contract's literal map (§4, FLAG 1).
- The supplements are in the JSON. GiBUU C12 has 1.24 final protons per event against GENIE's 0.68 at KE > 100 MeV.
  This is a model difference, not a harmonization item.

## 4. GiBUU ID → PDG map: every (ID, charge) seen in the final state

- **Mapped by the contract's map:**
  - (1, +1) → 2212 and (1, 0) → 2112;
  - (101, +1/0/−1) → π⁺/π⁰/π⁻;
  - (110, +1/0) → K⁺/K⁰ and (111, 0/−1) → K̄⁰/K⁻;
  - (32, 0) → Λ;
  - (33, ±1/0) → Σ.
  - ID 102 (η) was **not seen**.
- **Unmapped. The map's literal "anything else → other" applies to each of these.**

| (ID, charge) | GiBUU particle | C12 count | H count | under the literal map |
|---|---|---:|---:|---|
| **(902, −1)** | **μ⁻ (the primary lepton)** | **118,863 (1 per event)** | **114,732** | **"other": wrong; it should be the excluded muon (FLAG 1)** |
| (1, −1) | antiproton (GiBUU encodes antiparticles by charge sign here, not by a negative ID) | 16 | 14 | "other" (FLAG 2) |
| (53, −1/0) | Ξ | 24 | 39 | "other" |
| (56, +1) | Λ_c | 293 | 411 | "other" |
| (57, 0/+1/+2) | Σ_c | 71 | 91 | "other" |
| (114, 0/+1) | D | 92 | 62 | "other" |
| (118, +1) | D_s | 10 | 9 | "other" |
| (59, +1) | Ω_c (?) | 0 | 1 | "other" |

- No negative GiBUU ID was seen. The contract's "negative ID → antiparticle" clause never fires.

## 5. Struck-nucleon source

| sample | source (contract) | measured |
|---|---|---|
| GENIE CV | gst `hitnuc` | n 46,257, p 26,930, 0 (coherent) 687. H target (`tgt == 2212`): all 3,857 have p |
| GENIE MEC | gst `hitnuc` | n 45,583, p 26,358, 0 613, **2000000200: 717, 2000000201: 1,504 (nucleon-pair codes, MEC)** → default mass under the contract's "else" |
| NuWro C12 | `in[1].pdg` | n 67,200, p 31,996, **no `in[1]`: 791 (default)**. **3,318 events (3.3%) have 3 `in` particles (two struck nucleons, MEC): the contract takes `in[1]`'s mass** |
| NuWro H | `in[1].pdg` | all 99,960 are p |
| GiBUU C12 | the single perweight-0 nucleon row | **every event (118,863) has exactly one such row, including all 19,761 2p2h events (production_ID 35; 36 not seen)**. Charge 0: 65,878; +1: 52,985. **Events taking the default mass under the contract's mechanical rule: 0** |
| GiBUU H | the same | all 114,732 have one row, a proton; no 2p2h on H |
| Tune v1 (analysis) | `mc_targetNucleon` | n 59,050, p 35,739, 0: 1,159, 2000000200: 1,331, 2000000201: 2,721; the analysis applies the default mass to the last three. On Z = 1 all 5,038 have p |

**Ruling (g) versus the mechanical rule (FLAG 3).** Ruling (g) says GiBUU 2p2h events take the default mass. The
contract's mechanical rule (single row, else default) gives them **the single row's mass**, because each 2p2h event
has exactly one perweight-0 row. Implementing (g) needs the rule keyed on production_ID ∈ {35, 36}: 19,761 of 118,863
C12 events (16.6%) in this subsample. **NuWro MEC events (n_in = 3) raise the same question.** GENIE and Tune v1 put
2p2h at the default mass by construction.

## 6. ν along +z

| sample | check | result |
|---|---|---|
| GENIE (all four files) | gst `pxv`, `pyv` | **0 nonzero** in every CC event read |
| NuWro (all four) | `in[0].x`, `in[0].y` | **0 nonzero** |
| GiBUU | no ν vector in FinalEvents. Proxy: \|Σ pT(final) − pT(perweight-0 row)\| per event | **H, non-DIS (production_ID 2, 19, 21, 26, 30, 31): exactly 0** in every event of task 1001, and Σpz and ΣE balance against E_ν. This confirms ν ∥ +z. C12 cannot be checked this way (the remnant is not written) |

**GiBUU DIS events do not balance (FLAG 4).** On H, every production_ID 34 event (8,773 of 19,080 in task 1001) has a
median pT imbalance of 31 MeV, a median energy deficit of 45 MeV and a median longitudinal deficit of 35 MeV (90th
percentile pT: 165 MeV). DIS is 46% of the GiBUU-H subsample (52,910 of 114,732).
- Some final-state particles are not written for DIS events. Photons are one candidate: GiBUU writes none (§2).
- This touches the E_avail feature as harmonized (a missing γ or π⁰ lowers it) and, equally, the frozen GiBUU
  product's E_avail.
- It is not a ν-direction failure: energy is missing too.

## 7. FLAGGED for the director (no change applied)

1. **The GiBUU muon (ID 902) is not in the contract's map.** Literally, it becomes "other" and enters E_other in
   every GiBUU event. The intended treatment is presumably 902 → 13, excluded like every other muon. This needs a
   one-line contract amendment.
2. **GiBUU antinucleons are (1, −1), not negative IDs.** They become "other" under the literal map; there were 16
   (C12) and 14 (H). The same amendment could map them to −2212.
3. **2p2h struck-nucleon mass.** Ruling (g) and the mechanical rule disagree for GiBUU (§5). NuWro's two-nucleon MEC
   events (3.3% of C12) take `in[1]`'s mass under the frozen rule. Should they take the default mass, consistent with
   (g), GENIE and the analysis?
4. **GiBUU DIS final states lose energy.** The median is 45 MeV on H (§6). The cause (unwritten photons, or something
   else) is unidentified. It affects the GiBUU features and the frozen GiBUU product alike.
5. **The gst `pdgf` list excludes the primary lepton** (§1). This is consistent with the contract, which excludes
   muons and takes the muon from the lepton branches. The S2 code must read the lepton from `El/pxl/pyl/pzl`. This is
   noted, not a change.

## 8. Not checked

- Events beyond the subsamples: the GENIE and NuWro files beyond the first 100k entries, GiBUU tasks beyond 5, and
  the NuWro-H chunks beyond c10.
- The C12 ν direction for GiBUU.
- Whether GENIE 2.12.10's gst omits de-excitation photons on C, or C simply has none: only 116 low-energy photons
  appear on C even in the MAD lists, which use GENIE in MINERvA's build.

**Held out of git:** `preflight/preflight_s2.json` (sha256 `882d5657…`). It cites the GENIE input samples by bare name, and
`verify_receipt_artifacts.py` reads those as MISSING before it consults off-area directories, as with the four receipts
already held (director ruling, option i). It is kept in the session worktree; the tables in this report restate it.
