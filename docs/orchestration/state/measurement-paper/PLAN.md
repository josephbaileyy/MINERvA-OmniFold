# Physics-measurement work, phase 0: the plan for MP-1 to MP-4

**By** the measurement session, 2026-10-19, under
[`HANDOFF-20261019.md`](HANDOFF-20261019.md) and
[`DECISION-20261019-joseph-methods-first-and-measurement-compute`](../../DECISION-20261019-joseph-methods-first-and-measurement-compute.md).
**Tree:** branch `measurement-paper/phase0-20261019` from `origin/main` `19b46af9`. Every `path:line` below refers to
that commit unless a receipt is named. Receipts are under [`phase0/receipts/`](phase0/receipts/); the compute ledger is
[`phase0/LEDGER.tsv`](phase0/LEDGER.tsv). Study code lives in a new directory, **`measurement-paper/`** at the repository
root (phase 0: `measurement-paper/phase0/`).

**CITABLE FOR:**
- the feasibility verdict, ranked routes, draft specifications, costs and dependencies of MP-1 to MP-4;
- the phase-0 receipts and the one probe result (P-MP3, job `60003966`).

**NOT CITABLE FOR:**
- any adopted specification (each draft below is frozen only when the director binds it in a committed record);
- any result for the paper, any claim (Joseph's), or any outward act;
- any change to A7, the s5p results, or the methods paper. A new test is a new campaign (HANDOFF §3).

**Phase-0 spend:** one debug job, **0.0172 charged CPU node-h and 0 GPU node-h** of the 15 / 5 granted. Everything else
was read-only login-node inspection or local reduction of committed tables (unbilled).

---

## 0. Summary

| item | verdict | recommended route | phase-1 cost, CPU node-h (M = measured basis, A = assumed) | needs from outside the session |
|---|---|---|---|---|
| **MP-1** response | **FEASIBLE, BOUNDED.** A MINERvA per-species simulated-response band can be drawn through the frozen null calibration through the existing lateral-band slot, without regenerating any null | MP1-A: proton, meson, EM and "other" ±1σ endpoints at the sizes MINERvA's own tuples apply, evaluated as `f + Σ z Δ` in the frozen calibration | **6–19** (M per endpoint, A count and retry); 0 GPU | the size ruling (the director's, for Joseph, under PM-1); QOS `shared` for phase 1 |
| **MP-2** hybrid nulls | **FEASIBLE ROUTE, GATES UNPROVEN.** A detector-level independent simulation is impossible here, but an event-level null (analysis-MC truth reweighted to each generator over full final states) is buildable from existing samples | MP2-A: cross-fitted classifier reweighting, then the hybridization residual Δ_hyb by Asimov, then (optionally) new null ensembles | **3–8** to Δ_hyb (A); **≈ 110–225** for new ensembles (A, scaled from M 207.899); GPU ≤ 2 (A) | none for S0–S3; a grant for S4 |
| **MP-3** C vs CH | **FEASIBLE, CHEAP.** NuWro runs on a free proton (probe: RES and DIS only, σ_H/σ_C per nucleon 0.642). GiBUU on hydrogen is supported in code but not yet run | MP3-A (GENIE CH vs C-only map over the 109 cells, existing samples) then MP3-B (NuWro H run, combined 12:1 → a NuWro-on-CH prediction) | **< 1** for A and B (M probe); GiBUU H ≤ 2 (A) | whether a CH-corrected prediction is reported beside A7's (director) |
| **MP-4** validated 5D uncertainties | **NO FEASIBLE ROUTE ON THE RECORD** at the frozen targets. One premise is untested: prior-free constrained intervals (one-at-a-time strict bounds, then prior-optimized). Its decisive diagnostic is local and cheap, and the expected outcome is negative | MP4-A: the P0-OSB diagnostic on the D-ID binned setting, with a frozen necessary condition | **0 node-h** (≈ 1–10 local core-h, A) | an interval that is not OmniFold's (director/Joseph); the T2 mapping amendment if it passes |

**Overall order (§6):** the zero-cost decisive steps first (MP4-A diagnostic, MP3-A map), then the cheap CPU steps (MP3-B,
MP1 S0–S2), then the classifier work (MP2 S0–S3). MP-1, MP-2 and MP-3 then feed **one** new joint-test campaign with one
ensemble production instead of three, if their gates pass. MP-4's phase 1 opens only on a P0-OSB pass.

---

## 1. Corrections to the evidence map and handoff found in phase 0

These do not change any ruling. They change what the plan may assume.

| # | the map/handoff says | measured | receipt |
|---|---|---|---|
| C1 | "GiBUU is not on CVMFS" (map §3(c); HANDOFF:57; Stage D REPORT:288) | GiBUU v2019 is at `/cvmfs/nova.opensciencegrid.org/externals/gibuu/v2019`, and the existing sample was made with it (`setup_gibuu.sh`). Stage D checked only larsoft `products/` | `phase0/receipts/mp3/08_cvmfs_gibuu.txt` |
| C2 | MAT neutron sizes "25/10/20%" (map §1(c)) | that is the header (`ParticleResponseDefaults.h:12-23`). The **tuples apply 10% to all three neutron bins**; `_id_err/_id` is constant per species on 3,000 1A MC entries: proton 3.5%, meson 5%, EM 3%, other 20%, xtalk 20%, muon 2.4%, neutron 10% | `phase0/receipts/mp1/values_1A_mc_data_first3000.txt` (lines 89-91 for neutrons) |
| C3 | "Per-nucleon normalization absorbs the bulk" of the target difference (`DESIGN-20260911-endpoint-B-generator-comparison-test.md:244`) | for ν_μ CC, hydrogen has no QE, 2p2h or coherent channel and no nuclear effects, and its per-nucleon σ is about 0.64 of carbon's. Per cell, dσ_C12/dσ_CH = (13/12)(1 − f_H). GENIE's existing CH sample gives C-only/CH per nucleon **1.083 in W0 (W < 1.1 GeV) and 0.978 in W1**, or +5.6% / −4.6% with the overall normalization removed | `docs/orchestration/state/inelastic-high-region-20261011/results/r5_genie_events.json` (`regions/W0`, `W1`); probe `phase0/receipts/probe-mp3/` |
| C4 | the target effect is "unquantified" (triage T:137) | it is quantified for GENIE per W bin (C3). The −0.25% at high-region REPORT:436 is the normalization-removed value on one functional (ρ_C), not the size of the effect | as C3 |
| C5 | NuWro's run is labelled "numu-on-CH" | `3d-unfolding/genie/sbatch_nuwro_mefhc.sh:15` mislabels it; the card is C12 (`run_nuwro.sh:32-34`) | `phase0/receipts/mp3/02_work_dirs_and_jobcard.txt` |
| C6 | `MAT`'s response band is the gap | correct, and more specific: our observables read `blob_recoil_E_tracker/ecal` (E_avail) and `MasterAnaDev_recoil_E` (q0) (`MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:185-193`, `:208-218`, `:227-240`), and neither passes through MAT's `GetCalRecoilEnergy()`, which MAT's response universe shifts. Re-enabling MAT's band would not move our observables | `phase0/receipts/mp1/MAT_ResponseSystematics_source.txt`; `systematics_and_particle_response_defaults.txt` |
| C7 | "the 10% target" for model dependence (map §4(a)) | the 10% is T1's total width (`state/s5p/contract-amendment-1-use-case-and-targets.json:38`); the model component's cap is T2's **5%** median (`:39`) | — |
| C8 | `s5p-20260926/lateral/` empty, so endpoint products unknown (MP-1 research) | the five lateral endpoint unfolds are under `s5p-20260926/runs/s3/latunf/`, and all five frozen null ensembles are on pscratch (1,365 / 1,366 / 1,343 / 1,351 / 1,751 files, about 1.3 GB) | `phase0/receipts/mp1/null_products_all_predictions.txt` |

---

## 2. MP-1: calorimetric (hadronic-recoil) response through the null calibration

### 2.1 Verdict: FEASIBLE, BOUNDED

**Receipts.**
- **Inputs exist (confirmed).** The MC AnaTuples carry per-species visible energy and MINERvA's per-species shift
  branches. One 1A MC file (tree `MasterAnaDev`, 4,102 branches) has 80 `blob_recoil_E_*` branches
  (`{tracker,ecal,hcal,nucl,od,…}_{p,meson,em,other,lown,midn,highn,xtalk,mu}`) and
  `part_response_recoil_allNonMuonClusters_<species>_{id,id_err,od,od_err}`. The species pieces sum exactly to
  `blob_recoil_E_tracker` and `_ecal` on 3,000 entries (`phase0/receipts/mp1/branches_1A_filtered.txt`,
  `values_1A_mc_data_first3000.txt`).
- **Data have the reco inputs but no species.** In the data file every species branch and every `_err` is zero, and all
  the energy sits in `_none_id`, so the variation goes on the simulated side only (same receipts).
- **The calibration has a slot for it.** The s5p calibration already carries five kinematic-shift detector bands not by
  per-event simulation but at evaluation: `out = f + Σ_b z_b Δ_b`, with Δ_b = (f(+1) − f(−1))/2 from real-data endpoint
  unfolds and z_b recorded per pseudo-experiment (`nd-unfolding/s5p_joint.py:105-121`). A recoil-response shift is also a
  shift of simulated reco kinematics, so it enters the same way. W2 instead varied the response used to unfold the
  data and kept the null: "the variation moves the data, not the null" (`publication/w2/W2B-REPORT-20261006.md:3-4`).
- **The frozen products survive** (C8).
- **A documented, non-invented size exists for four species.** MINERvA's tuples apply proton 3.5%, meson 5%, EM 3%, other
  20% (C2). These are values the collaboration's producer applied, and they match MAT's public header
  (`ParticleResponseDefaults.h:12-23`, public `MinervaExpt/MAT-MINERvA`) and, for p/π/e, the test-beam agreement of about
  3–4% (`literature/LIT-REPORT.md:369-375`, arXiv:1501.06431).

**Bounds on the verdict.**
- **PM-1.** The ruling does not use the words "documented source". It forbids "inventing a hadronic-energy shift or adding an arbitrary
  uncertainty" (`DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md:85`), asks for "the applicable upstream
  documentation where available" (`:79`), and reopens only for "a concrete missing physical uncertainty" (`:108`). Adopting
  the tuple sizes is the director's ruling for Joseph (HANDOFF:36-38). This plan proposes them; it does not adopt them.
- **Neutrons have no documented size.** The header says 25/10/20%, the tuples apply 10%, and MAT turns neutrons off by
  default because "Neutron Systematics is supposed to handled by Hadron Reweight systematics"
  (`ResponseSystematics.h:7-12`, in `phase0/receipts/mp1/MAT_ResponseSystematics_source.txt`). GEANT_Neutron is already in
  the calibration (A7:14). Neutron response stays outside MP-1 unless the director rules otherwise.
- **The q0 convention is unresolved.** MAT's legacy shift adds absolute `_id_err` energies. Σ `part_response_*_id` /
  `MasterAnaDev_recoil_E` has median 0.62 in the MC sample, so the legacy convention does not map onto our q0 one to one.
  MAT's newer fractional path (`ResponseSystematics.cxx:356-365`) fits it better. Step S0 settles this.
- **Completeness is not established** by any route here. Energy-dependent, resolution and correlated effects, and the
  collaboration's internal provenance (`cdcvs.fnal.gov/.../NX_systematics`, cited at `ParticleResponseDefaults.h:7`, not
  readable here), remain open.

### 2.2 Routes, ranked

| rank | route | would establish | would not establish | cost (CPU node-h) |
|---|---|---|---|---|
| 1 | **MP1-A. Per-species ±1σ endpoints as bands in the frozen calibration.** Four species (proton, meson, EM, other), endpoints ±1σ, a δ = 0 control, evaluated through the lateral slot over the frozen ensembles of all five nulls | the ten A7 tests recalibrated with a MINERvA per-species simulated-response band drawn through the null, to linear order — the paper's own remedy ("a response band drawn through the calibration", `docs/analysis-note/paper_body.tex:1100-1103`) | neutrons; completeness; nonlinear and energy-dependent response; validity beyond linear order (gate G3 tests it) | 9 endpoints × 0.633 [M, `W2B-REPORT:143-151`] = **5.7**; ×2 for one full retry; **≤ 19** with neutron bins if the director adds them |
| 2 | **MP1-B. Marginalized metric** W′ = W + Σ Δ_r Δ_rᵀ, from MP1-A's endpoints | a power-aware statistic | validity: A7 says the metric "sets power only", so this is a complement, never a replacement | 0 extra |
| 3 | **MP1-A-full. Event-level response-varied nulls.** Pseudo-data drawn from shifted source rows; needs a new `s5p_nullexp` mode | removes the linear surrogate | the same physics limits as MP1-A | ≈ 208 [M, `DELIVERY-20261006-s5p-campaign-terminal.md:97-105`] + endpoints ≈ **215–290**. Only if G3 fails |
| 4 | **MP1-D. An independent MINERvA hadronic-response reviewer** and/or sending the prepared question (`QUESTION-20260920-hadronic-response-coverage-for-eavail-w.md`, "PREPARED, NOT SENT", `:8`) | the only route to the internal provenance, neutron treatment and correlations; high-region REPORT:103 asks for it before a validation is designed | — | 0; **Joseph's act** |
| — | a species screen with the null frozen (data moved) | — | it repeats W2's limitation per species and costs the same as MP1-A, since all the cost is in the endpoints. **Dropped** | — |

### 2.3 Draft predeclared specification (MP1-A)

- **Estimand.** For each of the ten A7 hypotheses H0(G) (five predictions × total and shape), the Monte Carlo
  calibrated p-value and Holm decision with a per-species simulated-response band set R = {proton, meson, EM, other}
  added to the nuisance model. Reported beside, never replacing, the A7 values.
- **Method.**
  1. *S0 (prototype, 1A only).* A species response universe that scales each species' visible-energy contribution to
     E_avail (`blob_recoil_E_{tracker,ecal}_<s>`) and the corresponding share of q0, in both MAT conventions. It
     settles the q0 convention: the frozen choice is the one that reproduces `MasterAnaDev_recoil_E` from its parts.
  2. *S1 (endpoints).* For each s in R: event loop (12 playlists, one active universe per pass), merge, `s5p_input_dumps.py
     lateral`, real-data unfold with `s5p_numerics.py --construction data` (estimator R, 5 iterations), as W2b did. Plus
     one δ = 0 control.
  3. *S2 (evaluation).* Extend the design's `lateral_endpoints` with the four bands. Draw z_s ~ N(0,1) per frozen
     pseudo-experiment from a declared seed key (independent of the existing `0x4A01` jitter stream), species
     uncorrelated. Evaluate the frozen products with `s5p_joint evaluate` on a login node, and mirror the change in
     `s5p_recompute.py` (it refuses a band set that differs from the products', `:447-449`).
  4. *S3 (independent recompute).* The recompute lane reproduces every decision.
- **Acceptance gates, frozen before any evaluation output is seen.**
  - G1: the δ = 0 control reproduces the production 1A CV branches bit for bit.
  - G2: on selected events the species-sum identity holds (ratio 1 to 1e-6), with no double count of `_mu` or cross-talk.
  - G3 (linearity): per species, ‖f(+1) + f(−1) − 2 f(0)‖₂ ≤ 0.2 ‖f(+1) − f(−1)‖₂ over the J cells, at each null's data
    unfold. (W2b's T moved asymmetrically: MnvTune T_total 2856 at −4% and 2540 at +4% against 2813 at δ = 0,
    `W2B-REPORT:112`, so this gate can fail.)
  - G4: the recompute AGREEs on all ten decisions.
  - **On failure.** G1, G2 or G4: the result is "response band not propagated (gate Gx failed)", and A7 stands unchanged. G3:
    MP1-A is not reported as a calibrated result. MP1-A-full is priced and goes to the director.
  - **Reporting.** Whatever the decisions are, they are reported. There is no outcome threshold, no second size and no
    re-run after the result (as W2's terminal rule, `PACKET-20261005-publication-decision.md:312-316`).
- **Frozen before results:** the species set and sizes (the director's ruling), the q0 convention (from S0, before any
  J-cell number is computed), the endpoint construction, the seed key, the G3 tolerance, and the shas of the event-loop
  patch, `s5p_joint.py` and `s5p_recompute.py`.

### 2.4 Cost

| step | CPU node-h | basis | wall | storage (destination) |
|---|---:|---|---|---|
| S0 prototype, 4 passes of 1A | 0.2 on `shared`; ≈ 1.3 on `regular` packed in one node | M: 1A passes took 2,247–4,842 s at billing 10 (`publication/w2/w2b-results/LEDGER-w2.tsv`) | < 2 h | < 10 GB, pscratch |
| S1, 9 endpoints | 5.7 (11.4 with one full retry) | M per endpoint 0.633 (W2B §6: loops 1.7236 + dumps 0.0801 + unfolds 0.0945 for 3); A count | ≈ 1 day of queue | ≈ 85–150 GB pscratch (merged omnifiles about 4.84 GB each, `W2B:58`); deletable after the dumps |
| S2, S3 | 0 | login node, unbilled (W2B §6) | hours | < 1 GB |
| neutron bins (only if ruled in) | + 3.8 | A | | + 30–50 GB |

**QOS.** W2 ran on `--qos=shared` (`publication/w2/sbatch_w2b_evloop.sh:3`). The phase-0 grant names only regular and
debug. Debug's 30-minute MaxWall (`phase0/receipts/mp1/sacctmgr_qos.txt`) is shorter than a full-1A pass (37–81 min), and
on regular each single-pass job bills a whole node (≈ 1.35 node-h for the longest pass). **Phase 1 should permit `shared`
for the event loops, or the endpoints must be packed several per node.** That is the director's call.

### 2.5 Dependencies

- The size ruling under PM-1 (director, for Joseph), including whether neutrons are in or out.
- Optional and Joseph's act: the outside reviewer or the prepared question (MP1-D). Lack of a reply does not reopen PM-1
  (`DECISION-20260919…:83`).
- A reading the director may allow: `Model.symmetry` on W2b's existing rr0/rr1/rrzero products, to measure the
  surrogate's linearity in the recoil direction before S1. It reuses W2 data as a diagnostic and draws no new δ, but
  W2's rule ("No second δ after the result") makes it the director's decision.

---

## 3. MP-2: hybrid nulls close enough to the generators, or replaced

### 3.1 Verdict: FEASIBLE ROUTE, GATES UNPROVEN

**What cannot be done.** No MINERvA detector simulation is available here (`docs/orchestration/state/2d-closeout/stageD-inputs/REPORT.md:286`),
so independently simulated generator events at detector level, as the referee proposed, are out of reach.

**What can.**
- **The slot accepts any event-level truth weight.** The hybrid null multiplies the pseudo-data source weights by a
  per-event truth weight `r_h` (`nd-unfolding/s5p_nullexp.py:299`, applied at `:328`). Today that weight is
  `fine_ratio`'s ρ of the event's fine cell (`nd-unfolding/s5p_truths.py:165-205`, `:245-259`), on the
  14×16×7×7×6 = 65,856-cell grid (`nd-unfolding/s5p_stage1_inspect.py:38-44`). An event-level w_G drops into the same slot
  with no pipeline change.
- **The samples carry full final states.** The analysis MC's Truth tree has `mc_nFSPart`, `mc_FSPart{Px,Py,Pz,E,PDG}`
  and `mc_targetZ/A`. GENIE gst has `nf pdgf Ef pxf pyf pzf` plus multiplicities, NuWro has `post` arrays with weights,
  and GiBUU's `FinalEvents.dat` has per-particle ID, charge, weight and four-momentum (`phase0/receipts/mp2/02-…`, `03-…`,
  `04-…`).
- **About 5% of each generator's rate is in fallback cells** that carry Tune v1's shape at a coarser level than the fine
  grid: GENIE CV, NuWro and GiBUU resolve 94.7%, 95.3% and 95.5% of N (`ratios/nullsF/null-*-F.json` statistics, MP-2
  research).
- **The hybrid's composition limit is structural.** Refinement in 5D cannot reach the hadron composition at fixed 5D
  coordinates (triage T:138; `PLAIN-LANGUAGE-PASS2-REPORTS.md:394-402`). An event-level null over final-state features
  can.

**The blocking gap.** `of_inputs_5d.npz` (the s5p inputs) holds the 5 scalars only, with no event id. The PET truth cloud
`of_inputs_pc_fps.npz` (`part_gen`, 32,917,278 × 12 × 5) uses the full-phase-space truth gate, so its rows do not line up
with the 32,849,103 s5p rows (`phase0/receipts/mp2/04-…`, `05-…`). A new non-full-phase-space dump with final-state
particles, checked bitwise against `MCgen`, closes it.

### 3.2 Routes, ranked

| rank | route | would establish | would not establish | cost |
|---|---|---|---|---|
| 1 | **MP2-A. Event-level classifier null.** Fit w_G(x) = p/(1 − p) on harmonized full-event truth (muon kinematics, E_ν, per-species multiplicities and leading kinematics above thresholds, neutrons included), cross-fitted, and put w_G in the `r_h` slot | pseudo-data that are "G's final states passed through MINERvA's simulated response", which is what a detector simulation of G would give except for features outside x. Removes the finite-grid hybridization and the inherited hadron composition | the detector model (p(reco \| final state) is still MINERvA's GEANT model, the standard unfolding assumption and MP-1's subject); content outside x (nuclear remnant, de-excitation, tokens beyond any cap); support where Tune v1 has none | S0–S3: **3–8 CPU + ≤ 2 GPU node-h** (A); S4: **≈ 110–225 CPU** (A, scaled from M 207.899 for five nulls, `DELIVERY-20261006:100`) |
| 2 | **MP2-D. Δ_hyb by Asimov** inside MP2-A: noise-free unfolded J cells at the event-level null minus at the hybrid null, then replay the frozen claim rule with F + Δ_hyb as the κ scan did | a direct test of A7 condition (i) (`paper_body.tex:877-880`), whether the hybrid moved any decision | anything beyond the mean shift; it is a report, not a recalibration | ≈ 4 × (1 + K) unfolds at 0.03–0.06 each (M, `W2A-REPORT-20261006.md:29`) + replay ≈ 1 core-h → **≈ 1–2** |
| 3 | **MP2-C. Envelope of within-cell shapes** (other generators' shapes, or pre-registered warps) | a sensitivity study | a bound, unless the envelope is shown to contain G; composition only if the warps include it | ≈ 1–3 (A) |
| 4 | **MP2-B. Another refinement step plus the G6b rate measurement** | the per-halving rate that G6b asks for (`RECORD-20261008-release-audit-corrections.md:241`) | composition at fixed 5D coordinates, structurally. A "halving" is already a ≈ 10× change in cell count (6,480 merged vs 65,856 fine, `phase0/receipts/mp2/06-…`), and splitting again gives ≈ 2.1 M cells against ≈ 0.3 M effective generator events (`stageD-inputs/REPORT.md:271`). Any rate from three resolutions is an extrapolation | regeneration ≈ 21 (NuWro) + 43 (GENIE) core-h at the documented throughput (not receipts) + 1–2 node-h Asimovs + 100–208 for claim-bearing ensembles |

### 3.3 Draft predeclared specification (MP2-A with D)

- **Estimand.** H0′(G): the truth final-state distribution equals G's over a declared feature set F, flux-matched and in
  the analysis phase space, with MINERvA's simulated response conditional on F and the drawn bands. First readout: Δ_hyb(G)
  per J cell and the replayed decisions. Second, only under its own grant: the ten tests recalibrated with event-level
  nulls.
- **Method.**
  - *S0 (probe, ≤ 1 CPU or ≤ 0.5 GPU node-h).* On a subsample, fit Tune v1 truth against NuWro truth twice, on the 5 scalars
    alone and on full features. Measure the AUC gap against a G-vs-G split control, the variance of log w within fine
    cells, Kish ESS, the maximum weight and fit timing. Descriptive; it sizes S2.
  - *S1 (aligned dump).* One event-loop variant that writes the final-state particles for exactly the s5p truth-passing rows.
    Admission: the 5 scalars reproduce `MCgen` bitwise (≈ 0.76 node-h, M basis `W2A-REPORT:26`).
  - *S2 (reweighters).* Per G in {GENIE CV, GENIE MEC, NuWro-CH (from MP-3), GiBUU-CH or GiBUU with borrowed H}: K-fold
    cross-fitted classifier with its folds nested inside the s5p A/B split key (`s5c_pseudo.split_key_for`), so no event
    is weighted by a model trained on it. Frozen before fitting: features and their harmonization (pseudo-particles,
    nuclear remnant, spectator nucleons, thresholds), model family, hyperparameters, folds, seeds, weight cap.
  - *S3.* Δ_hyb by Asimov, and the replay.
  - *S4.* New ensembles: A7's machinery unchanged (estimator R, metric V, J cells, nuisances, Holm with determinacy), with
    only `r_h` replaced. Run inside the combined campaign of §6.
- **Acceptance gates for each G, frozen before S3.**
  - V1: held-out two-sample test of reweighted MC against G: AUC ≤ AUC(G vs G split) + 0.005.
  - V2: closure of the fine 5D and J marginals against `gen5d` within the products' `sumw2`, by χ²/ndf ≤ 1.5 and no J cell
    beyond 3σ.
  - V3: closure on held-out features not in x (at least neutron kinetic energy, proton multiplicity, π⁰ count).
  - V4: Kish ESS ≥ 0.3 N and maximum normalized weight ≤ 50.
  - V5: the spread of Δ_hyb across K classifier seeds is ≤ 0.2 of its magnitude, or ≤ 0.1 δ_fine.
  - **On failure.** The event-level null for that G is "not established", and A7's hybrid result stands for it. One
    predeclared fallback, a reduced feature set named in the contract, is allowed only before S3 is computed. There is
    no tuning after any S3 or S4 output.
- **Frozen before results:** F, the harmonization rules, the model and folds, V1–V5 thresholds, the replay rule, and the
  code shas.
- **Coupling to MP-3.** A classifier trained on Tune v1 (CH) against a C12-only generator learns the hydrogen events.
  NuWro and GiBUU must enter S2 on CH (MP-3), or the hydrogen events must be excluded from both sides by `mc_targetZ`.
  The contract must say which.

### 3.4 Cost

| step | CPU node-h | GPU node-h | basis | storage |
|---|---:|---:|---|---|
| S0 | ≤ 1 | ≤ 0.5 | A; LightGBM is already used in s5c (`nd-unfolding/s5c_unfold.py:175`) | < 5 GB pscratch |
| S1 | ≈ 0.8–1.5 (packed or `shared`) | 0 | M basis `W2A-REPORT:26` | a final-state dump ≈ 30–60 GB (A; the PET cloud at 12 tokens is the analogue), pscratch |
| S2 | ≤ 1 (LightGBM) | ≤ 1.5 (if a network is chosen: 36.55 µs/example at 12 tokens on one A100, `nd-unfolding/pet/configuration_comparison/CALIBRATION_RESULTS-20260918.md:22`) | A | < 10 GB |
| S3 | ≈ 1–2 | 0 | M per unfold, A count | < 5 GB |
| S4 | ≈ 110–225 | 0 | A, from M 207.899 for 7,176 experiments over five nulls (≈ 0.029 per experiment) | ≈ 1.5 GB per 1,350 products (C8), pscratch |

### 3.5 Dependencies

- MP-3 (the CH generator predictions) before S2 for NuWro and GiBUU.
- MP-1's bands ride on the same S4 ensembles (§6).
- G6b's provenance question for the 0.45–0.76 rate (`RECORD-20261008…:346`) stays with Joseph. MP2-D measures the
  residual directly and does not need that rate.

---

## 4. MP-3: carbon versus hydrocarbon for NuWro and GiBUU

### 4.1 Verdict: FEASIBLE, CHEAP

**Receipts.**
- **The data are per CH nucleon, hydrogen included** (`2d-unfolding/unfold_2d_omnifold_unbinned.py:41-44`). GENIE is
  generated on CH and normalized (σ_C12 + σ_H1)/13 (`3d-unfolding/genie/gen5d_flux_reweight.py:175-191`). NuWro runs on
  C12 only (`target_type=0, nucleus_p=6, nucleus_n=6`, `run_nuwro.sh:32-34`), because the mixed-target option crashed
  (`:6-8`), and it is normalized by NuWro's own per-C12-nucleon weight with no explicit /12
  (`gen5d_flux_reweight.py:619-620`). GiBUU runs with `target_Z=6, target_A=12`, `include2p2hQE=T`, `Enu_upper_cut=20`
  (`phase0/receipts/mp3/02_work_dirs_and_jobcard.txt`).
- **The effect is not small in GENIE** (C3): +8.3% (W0) and −2.2% (W1) per nucleon, and +5.6% / −4.6% in shape.
- **Probe P-MP3 (job `60003966`, debug, 62 s, 0.0172 node-h).** NuWro v21_09_1 (CVMFS e20-debug) with the ME-FHC
  flux, the shipped free-proton target (`data/target/proton.txt`: `nucleus_p=1, nucleus_n=0, nucleus_target=0`) and the
  production dyn switches, 20,000 events, with a paired C12 control on the production card
  (`phase0/receipts/probe-mp3/job-60003966.txt`, `flat5d-reduction.txt`):

  | | H | C12 |
  |---|---|---|
  | channels (CC) | RES 7,837, DIS 12,156; **QEL, COH, MEC = 0** | QEL 2,300, RES 3,991, DIS 12,886, COH 155, MEC 666 |
  | struck nucleon | proton only (19,993) | n 13,362, p 6,481, none 155 |
  | flux-averaged σ per nucleon | 2.361e-38 cm² | 3.679e-38 cm² |
  | fraction with W < 1.1 GeV | 0.00015 | 0.121 |
  | wall (20k events + 50k test events) | 30.5 s, 0.40 GB peak | 36.4 s, 0.42 GB |

  - **σ_H/σ_C per nucleon is 0.642.** So hydrogen's share of NuWro's CH rate would be f_H = 2.361 / (12 × 3.679 + 2.361) =
    **5.1%**, against GENIE's 5.35% (`r5_genie_events.json`). It is consistent in size, and it is not GENIE's number.
  - **The channel content is what free-proton ν_μ CC requires.** Both the probe and the source reading
    (`phase0/receipts/mp3/05-07_*.txt`) agree.
  - **Scope.** This is a total, flux-averaged quantity. No cell-level target effect was computed in phase 0.
- **GiBUU on hydrogen** is supported in code: A = 1 initialization, with density and Pauli switches forced off
  (`phase0/receipts/mp3/09-11_*.txt`). It is on CVMFS (C1). It has **not been run**.

### 4.2 Routes, ranked

| rank | route | would establish | would not establish | cost (CPU node-h) |
|---|---|---|---|---|
| 1 | **MP3-A. GENIE CH vs C-only map over the 109 J cells**, CV and MEC, from the existing CH samples split by target code (`code/r5_genie_events.py:128-141` with the J-cell map from `nd-unfolding/s5p_stage1_inspect.py:77,261`) | the size and sign of the target effect per reported cell, in GENIE's model, and the shift Δμ in units of each null's spread under the frozen metric V. GENIE MEC matters because NuWro and GiBUU both include 2p2h, which only carbon has | NuWro's or GiBUU's own physics | ≈ 0 (the existing reduction took 39 CPU-s, high-region `logs/budget_ledger.jsonl:9,11`); one debug job ≤ 0.1 |
| 2 | **MP3-B. NuWro H run, combined 12:1** into NuWro on CH: per cell dσ_CH = (12/13) dσ_C12 + (1/13) dσ_H, then the same converter chain (`extract_nuwro`, the flux-fix reweight, the 50–100 GeV supplement) | a true NuWro-on-CH 5D prediction, and its difference from the C12 prediction per cell | GiBUU's | generation ≈ 0.1 node-h (M: 20k in 30.5 s); converter chain ≤ 0.5 (A) |
| 3 | **MP3-C. GiBUU on hydrogen** (`target_Z=1, target_A=1`, 2p2h off, ≈ 12× numEnsembles), or, if it fails, **hydrogen borrowed from NuWro**, with the NuWro-H vs GENIE-H spread as its uncertainty | GiBUU on CH (own or mixed) | with borrowed H, GiBUU's own free-proton physics; the 20 GeV cap (KI 82) stays | probe ≤ 0.3; run ≤ 2 (A) |
| 4 | disclose only | — | — | 0. If chosen, the text should quote GENIE's measured per-W-bin range, not "unquantified" (C4) |

### 4.3 Draft predeclared specification (MP3-A then MP3-B)

- **Estimand.** Per J cell c and generator G ∈ {NuWro, GiBUU}: r_c(G) = μ_c(G on CH) / μ_c(G on C12), and its
  shape-normalized form. The joint-test readout is the frozen statistic evaluated at the CH prediction, replayed against
  the frozen null of G (a Δμ report), with a new null only inside the combined campaign (§6).
- **Method.** MP3-A as above (descriptive; sizes the effect before any NuWro run). MP3-B:
  - **The H run.** 250k events at 0.5–50 GeV plus 25k at 50–100 GeV, on the production card except the target lines.
    This is enough: hydrogen adds f_H·ε_H to a cell's relative MC error, and ≈ 130k already keeps that below a third of
    the carbon error where f_H ≤ 0.08 (MP-3 research §4).
  - **The combination** follows the per-cell formula in the route table, with variance (12/13)² Var_C + (1/13)² Var_H.
  - **The C12 part reuses the frozen NuWro product bit for bit.** The control rebuilds it and compares hashes.
- **Acceptance gates, frozen before any cell-level H output.**
  - B1: H channel content as in the probe: QEL = COH = MEC = 0, struck nucleon proton only.
  - B2: the rebuilt C12 product equals the frozen one bitwise.
  - B3: the flux-fix weight closure of the supplement matches the existing NuWro product's.
  - B4: the H contribution's statistical error per cell is ≤ 1/3 of the C12 contribution's in every reported cell.
  - **On failure.** B1–B3: no CH NuWro prediction is reported. B4: more H events, once, by a factor fixed in the contract.
  - **Reporting.** r_c is reported whatever it is.
- **Frozen before results:** the card, event counts and seeds, the converter shas, the combination formula, the
  replay rule.

### 4.4 Cost

| step | CPU node-h | basis | storage |
|---|---:|---|---|
| MP3-A | ≤ 0.1 | M (39 CPU-s) | < 1 GB |
| MP3-B generation | ≈ 0.1 (one node, < 10 min) | M (probe) | ≈ 0.3 GB root + flat, pscratch |
| MP3-B converter chain | ≤ 0.5 | A | < 1 GB |
| MP3-C GiBUU H probe + run | ≤ 2.3 | A | ≈ 2–5 GB |
| a new null per changed prediction, outside §6 | ≈ 35–40 per generator | A (`campaign-state.json:355,411,415`, as read by the MP-3 research) | ≈ 0.3 GB |

### 4.5 Dependencies

- **Whether a CH run counts as "fresh" does not matter for MP-3.** Stage D left the question open (`stageD-inputs/REPORT.md:288`).
  `PROPOSAL-20261005-scalar-measurement-successor.md:316-317` says "fresh seeds on a tested historical truth are not a new
  physical validation case", so a CH NuWro run is not fresh for Stage D, and MP-3 does not need it to be. Stage D's
  custodian rule (§7, `:295-297`) applies to untouched validation samples only.
- **The s5p contract forbids "re-grading any historical result"** (MP-3 research, `contract.json:94-99`). A CH-based result is
  reported beside A7, not in place of it.
- **MP-2's S2 needs MP3-B** (and MP3-C) for NuWro and GiBUU.

---

## 5. MP-4: a route to validated five-dimensional uncertainties

### 5.1 Verdict: NO FEASIBLE ROUTE ON THE RECORD at the frozen targets; one untested premise

**The frozen targets** (`state/s5p/contract-amendment-1-use-case-and-targets.json:38-42`, "not relaxed",
`RECORD-20260927-s5p-stage2-exit.md:146`):
- **T1.** Median total 68% half-width ≤ 10%, 90th percentile ≤ 25%.
- **T2.** On each development alternative, median |bias|/|departure| ≤ 0.25, and the model component's median ≤ 5%.
- **T3.** Numerical stability.
- **T4.** Coverage (one-sided Clopper–Pearson ≥ 0.60 and ≥ 0.90, Bonferroni).
- **T5.** Pull SD in [0.80, 1.25].
- **Scope.** RD1 is the 109 J cells and RD2 the 27 H2 cells. RD3 (EW) "can never fulfil the joint-5D objective".

**Why the record says the limit is intrinsic.**
- **The model component is out of reach.** Its medians are 12.0 / 9.6 / 13.4% (J / H2 / EW, `stage2-exit:127-131`), so T1
  is out of reach in J because the half-width is at least the component, and T2's 5% cap fails everywhere. Without the
  contaminated D1 vertex RD1 and RD2 still fail T2 through W3, "which does not involve h"
  (`state/s5p/contract-amendment-6-review1-repairs.json:17`).
- **More iterations or capacity do not help.** Iterations to 200 and capacity 400/31 change the residual by 3–8%
  (`stage2-exit:76-97`; `KNOWN_ISSUES.md:67`, row 77). At K = 5 the GBDT leaves the same residual as exact binned IBU, with
  an approximation share of 0.014 (`state/next-preparation-20261009/d-id/REPORT.md:432-440`, `:530-532`).
  "the regularization trades a large variance for the bias observed" (`:527-528`).
- **New receipt, the binned information floor.** This is a read-only reduction of D-ID's committed
  `outputs/tables.npz` (sha256 `2aab2270…`) by `measurement-paper/phase0/did_floor.py`, saved as
  `phase0/receipts/mp4/did_cr_floor.json`. The table gives the median Cramér–Rao 1σ relative width at nominal truth,
  signal-only and noise-free. D-ID's truth grids are named T1 (the J cells) and T2 (J split once). The names are D-ID's
  and collide with the target names:

  | reporting map | D-ID grid T1 (within-cell shape fixed by MC) | D-ID grid T2 (within-cell freedom) | acceptance holes at T2 |
  |---|---:|---:|---:|
  | J (RD1) | **11.3%** | 28.7% | 7 of 109 |
  | H2 (RD2) | 2.9% | 54.0% | 10 of 27 |
  | EW (RD3) | 3.2% | 43.1% | 11 of 39 |

  - In J, even the most optimistic unbiased binned estimator, with within-cell shapes supplied by the MC (itself a prior),
    has a median width above T1's 10%. Freeing the within-cell shape (grid T2) widens it to 29%.
  - This agrees with D-ID's own "T1 median is 11–13%" (`d-id/REPORT.md:424`).
  - D-ID names two loopholes it does not close (`:547-552`): unbinned information is not bounded by binned widths, and
    estimators that use constraints or priors are not excluded.

**Candidates, and why each is closed or open.**

| candidate | on the record | verdict at the frozen targets |
|---|---|---|
| (a) prior dependence carried as an uncertainty component | the s5p design itself: T1 counts h (`stage2-exit:124-135`) | T2 caps the component at 5%; measured 9.6–13.4%. h is not a per-cell bias bound (`amendment-6:44`), and no coverage test ever included it. **Closed** |
| (b) iterate to convergence / early stopping / bias correction | K to 200; the predeclared K rule picked 5 (`stage2-exit:111-119`); s5c's bias correction did not transfer (`OUTCOME-20260925-s5c-tier-s-futility-fail.md:47-48`); exact IBU at 10⁵ iterations drives cells to zero (`d-id/REPORT.md:553-555`) | variance rises toward the floor above (J ≥ 11–29%). **Closed** |
| (c) a neural or PET classifier instead of GBDT | the GBDT already matches exact IBU (`d-id:432-440`); PET is diagnostic only (AGENTS.md) | the classifier is not the bottleneck. **Closed** |
| (d) coarser or selected functionals | — | **excluded by Joseph** (DECISION-20261019 §1a) |
| (e) a constrained-subspace or Wiener-SVD-style "A_c" report | not tried as such | it changes the estimand to A_c·t, so it fails T2 by definition. **An estimand change is Joseph's call** |
| (f) Bayesian unfolding (FBU) | never tried | its posterior is prior-dominated in exactly these directions, with no coverage guarantee. **Not a route** |
| (g) **one-at-a-time strict bounds (OSB) and prior-optimized (PO) intervals** (Stanley, Patil and Kuusela, arXiv:2111.01091), mapped at `state/next-preparation-20261009/gbdt/REPORT.md:385-404` | **never run**: no solver was available, and the strict-bounds study was named in the 2026-10-10 pause, now lifted for this work (DECISION-20261019 §1a) | **the one open premise**. These intervals give coverage without a prior, and PO uses the prior only to shorten them. They attack D-ID's constraint loophole (positivity). They are "a different interval algorithm", "not a validated rescue of the GBDT", with empirical-only coverage in the rank-deficient regime and no published treatment of response-MC noise or background (`gbdt/REPORT.md:395-404`, `:438-439`) |

**The GBDT validation route is also financially closed for the CPU pool.** Validating a GBDT bootstrap-plus-universe
interval costs 8,710 to 80,916 admitted CPU node-h (`gbdt/REPORT.md:419-436`), against 2,327.8 left in the group CPU
pool (HANDOFF §4).

> **Correction, 2026-10-22 (approved by Joseph; recorded by the measurement session).** As first written, this
> paragraph said the route was "financially closed", comparing its cost only with the CPU pool. DECISION-20261019 §1b
> also records the `m3246_g` GPU pool at 46,226.0 node-h left on 2026-10-19, used at about 860 node-h a day. So:
> - the CPU pool cannot fund the route;
> - the GPU pool could in principle fund the statistical-only recipe (central + 30 bootstrap unfolds, 8,710 admitted
>   CPU node-h) if LightGBM runs on the GPU nodes' CPUs. That cost is **an unmeasured estimate**: a GPU node has 64
>   cores against a CPU node's 128, so roughly 2× the node-h, about 17,400. Whether the shared pool is spent this way
>   is Joseph's and Ben's decision;
> - the route remains **not recommended on the evidence**:
>   - development-scale departure coverage of 0.027, pooled 68%, for both the E_avail-shape and q3 departures
>     (`OUTCOME-20260925-s5n-stage1-development-fail.md:57-58`; s5e diagnosed this failure);
>   - KI 98 arm (b): the residual persists with no background at all, R_b = +2.84 (`state/ki98-wbias-test/REPORT.md:58-63`);
>   - D-ID: exact binned IBU leaves about the same residual (`d-id/REPORT.md` §11);
>   - MP4-A: FAIL (`phase1/mp4a/REPORT.md`).

### 5.2 Routes, ranked

| rank | route | would establish | would not establish |
|---|---|---|---|
| 1 | **MP4-A. P0-OSB diagnostic** (below), then phase 1 only on a pass | whether prior-free intervals with positivity can meet T1 on the J cells even in the optimistic case; on a FAIL, a negative feasibility verdict with receipts | a validated interval (a pass only permits phase 1) |
| 2 | MP4-E. a report of the joint 5D in an explicitly declared estimand (A_c), for Joseph | a precise statement of what is constrained | the frozen T2 |
| 3 | record the negative verdict now, without the diagnostic | — | D-ID's constraint loophole stays open |

### 5.3 Draft predeclared specification (MP4-A, the P0-OSB diagnostic)

- **Estimand.** For each reported J cell (RD1, 109) and H2 cell (RD2, 27): the OSB 68% interval half-width, relative to
  the nominal value, at D-ID truth grid T2 (5,184 cells), with positivity as the only constraint.
- **Method.**
  - **Inputs.** D-ID's admitted inputs, grid, response, functional rows and Fisher machinery (`d-id/did.py:208-261`, `:321`).
    The inputs file `of_inputs_5d.npz` measured 1,548,438,020 B on the cluster, the size D-ID admitted
    (`phase0/receipts/mp4/cluster_probe.txt`).
  - **Data and bound.** Noise-free nominal reco data y = R t. Whitened χ² ball at the 68% radius; min and max of each
    functional subject to t ≥ 0.
  - **Solver.** `scipy` (present locally, 1.15.2), using a Lagrangian search over `lsq_linear`. `cvxpy` is absent.
  - **Also reported, descriptively.** The same at grid T3 if it is tractable. The truth-rate share inside acceptance holes.
    The Cramér–Rao width with the reco binning refined 2× per axis, as a proxy for the unbinned loophole.
- **Gating control.** With positivity switched off, the OSB half-width must reproduce D-ID's committed T2 `sigma_rel` to
  1e-6 relative on every reported cell. If it does not, nothing else is read.
- **Acceptance (a necessary condition, frozen before any OSB number).**
  - **PASS.** On J at grid T2, the median relative half-width is ≤ 10% and the 90th percentile ≤ 25%.
  - **Optimism.** The case is optimistic (noise-free, signal-only, no s² slack, no background, no response noise), so a FAIL is decisive and a
    PASS only permits phase 1.
  - **On FAIL.** MP-4 is recorded as a negative feasibility verdict for RD1 at the frozen targets. Prior-free intervals
    fail T1 even here, and prior-including methods fail T2 on the measured component. The remaining loophole is unbinned
    information, sized by the refined-reco arm. H2 is reported descriptively; whether RD2 alone counts as "coarser" is
    Joseph's call.
  - **On PASS.** Phase 1 proposes binned noisy pseudo-experiments with background and response bootstraps and PO
    intervals, then a contract amendment mapping T2 onto intervals (no weaker than the original) before any validation
    result. The validation sizing is 4,404 experiments per case for J (`gbdt/REPORT.md:411-413`), at seconds per interval.
- **Frozen before results:** the grid, the radius, positivity as the sole constraint, the gating control's tolerance, the
  PASS rule, the solver and its convergence tolerance, the code sha.

### 5.4 Cost

| step | node-h | basis | storage |
|---|---:|---|---|
| P0-OSB | 0 (local) | A: ≈ 1–10 core-h for about 218 bounded solves. D-ID's own run was 0.806 core-h for the owner run, ≈ 1.5 in all, 4.65 GB peak (M, `d-id/REPORT.md:301-304`). **Tractability unconfirmed** | one read-only 1.55 GB copy, local scratch |
| phase 1 on PASS | ≈ 5–30 CPU (A; seconds per interval × ≈ 17,600 experiments × procedure) | A | < 50 GB |

### 5.5 Dependencies

- The director's grant to run strict bounds under the lifted pause.
- Whether an interval that is not OmniFold's fits the methods and measurement framing (director, then Joseph).
- On PASS: the T2 mapping amendment, before any validation result.
- The RD2 "coarser" question and any estimand change (MP4-E): Joseph's.

---

## 6. Overall order and the combined campaign

**Order.** The order puts cheap decisive steps first, so CPU is spent only where a gate has already passed. CPU is the
scarce side (HANDOFF §4).

| step | item | CPU node-h | GPU node-h | gates it opens |
|---|---|---:|---:|---|
| 1 | MP4-A P0-OSB (local) | 0 | 0 | MP-4 phase 1, or the negative verdict |
| 1 | MP3-A GENIE map (debug) | ≤ 0.1 | 0 | sizes MP3-B's importance |
| 2 | MP3-B NuWro H + converter chain; MP3-C GiBUU H probe | ≤ 2.9 | 0 | CH predictions for MP-2 S2 |
| 2 | MP1 S0 prototype; S1 endpoints; S2–S3 evaluation | 6–19 | 0 | the MP-1 result (frozen ensembles; no regeneration) |
| 3 | MP2 S0–S3 | 3–8 | ≤ 2 | Δ_hyb and the replay; whether S4 is needed |
| 4 | **one combined new joint-test campaign** (only if steps 2–3 pass their gates and Δ_hyb or the CH shift is material) | ≈ 110–225 | 0 | the measurement-grade tests |
| — | MP-4 phase 1 (only on P0-OSB PASS) | ≈ 5–30 | 0 | — |

**Phase-1 total before step 4: ≈ 12–30 CPU and ≤ 2 GPU node-h** (assumed, built on measured unit costs). Step 4 is a
separate grant.

**Why one campaign.** MP-2 changes the null source weights, and MP-3 changes the NuWro and GiBUU predictions, so either
one regenerates those nulls. MP-1's bands ride on whatever ensembles exist, through the evaluation slot. A single new
contract, with event-level nulls for the CH generator predictions and the response bands in evaluation, pays for one
ensemble production instead of three. It is a new campaign with its own predeclared contract (HANDOFF §3); A7 and the
methods paper stay as they are.

**Budget context.** The director keeps the measurement work within half the CPU pool remaining at each grant (DECISION-20261019
§1b), i.e. ≈ 1,160 of 2,327.8 today. Step 4's upper estimate is about a fifth of that. Re-measure `iris` before each grant.

**Storage.** Everything lands on pscratch under `/pscratch/sd/j/josephrb/measurement-paper/` (16.78 of 20 TiB used,
HANDOFF §4). Peak phase-1 use is ≈ 0.2–0.3 TB, falling to < 50 GB after the dumps. Nothing goes to CFS. The frozen s5p
null products (C8) date from 2026-09-26. Their pscratch copies are at purge risk if they go unread, and the archive copy
is on CFS (`stageD-inputs/REPORT.md:252-256`), so S2 of MP-1 should run before that matters.

---

## 7. Decisions this plan needs, and from whom

| # | decision | whose |
|---|---|---|
| D1 | adopt the tuple-applied per-species sizes (proton 3.5%, meson 5%, EM 3%, other 20%) as MP-1's documented source; neutrons in or out | the director, for Joseph, under PM-1 |
| D2 | permit QOS `shared` for phase-1 event loops (or require packing on regular) | the director |
| D3 | allow `Model.symmetry` on W2b's existing products as a linearity diagnostic (no new δ) | the director |
| D4 | send the prepared hadronic-response question or ask an outside reviewer | Joseph |
| D5 | run strict bounds under the lifted pause; accept a non-OmniFold interval as a candidate | the director, then Joseph |
| D6 | report CH-corrected generator predictions beside A7's | the director |
| D7 | grant phase 1 (steps 1–3, ≈ 12–30 CPU and ≤ 2 GPU node-h) and, later and separately, the combined campaign | the director |

## 8. Proposed rows for files this session does not edit

The director lands these if they agree.

- **KNOWN_ISSUES (new row).** The target mismatch for NuWro and GiBUU is quantified for GENIE per W bin: +8.3% (W0) to −2.2%
  (W1) per nucleon, and +5.6% / −4.6% in shape (C3). The existing per-nucleon normalization does not absorb it. This is
  open until MP-3.
- **KNOWN_ISSUES (KI 82 note).** GiBUU v2019 is on CVMFS (C1). Any route that needs a fresh GiBUU sample is not blocked
  by availability.
- **Stage D REPORT:288 (corrigendum, the director's lane).** "GiBUU is not on CVMFS" is wrong (C1).
- **`DESIGN-20260911-endpoint-B…:244` (corrigendum).** "Per-nucleon normalization absorbs the bulk" does not hold for the
  W0 and W1 bins (C3).

## 9. Phase-0 record

- **Jobs.** `60003966` only (`phase0/LEDGER.tsv`). Total **0.017222 CPU node-h, 0 GPU node-h**. Outputs are under
  `/pscratch/sd/j/josephrb/measurement-paper/phase0/mp3/`. Nothing was written to CFS.
- **Read-only work.** Branch listings and value reads of one 1A MC and one data AnaTuple, the MAT source, the CVMFS NuWro and
  GiBUU trees, the generator samples, the frozen null products, and the D-ID tables. Four research agents (Claude, this
  session's account) did these reads. Their reports were read to the end, and the claims carried here were re-checked
  against the files and receipts cited: C2, C3, C8, the lateral-slot code, `r_h` at `s5p_nullexp.py:299`, the recompute
  band check, the PM-1 lines, the T1–T5 definitions, the strict-bounds section, and the CR-floor reduction.
- **Not done, and why.**
  - MP-1's prototype universe needs new event-loop code, which belongs in a reviewed phase-1 step (S0).
  - MP-2's separability probe needs the aligned dump or a careful flux and phase-space harmonization, and is S0 of
    phase 1.
  - MP-4's P0-OSB is the decisive test itself, so it runs only after the director freezes §5.3.
- **Unconfirmed.**
  - The q0 response convention.
  - OSB tractability at grid T2.
  - All classifier timings.
  - GiBUU on hydrogen by execution.
  - The meaning of PDG code 2000000013 in the PET cloud.
  - The contents of MINERvA's internal NX_systematics page.

**Receipts** (`phase0/receipts/`):
- `mp1/`: branch lists, species values, MAT sources, QOS limits, null-product layout and counts.
- `mp2/`: the generator directory, the GiBUU, gst, NuWro and AnaTuple schemas, the PET cloud schema, the merged grid.
- `mp3/`: the jobcard and cards, the CVMFS NuWro and GiBUU trees, the NuWro and GiBUU source for free targets, the gen5d
  products, the timing records, the script shas.
- `mp4/`: the CR floor and the cluster size check.
- `probe-mp3/`: job `60003966`'s log, cards, NuWro cross-section tables, timing, the output shas, sacct, and the flat-tree
  reduction.
