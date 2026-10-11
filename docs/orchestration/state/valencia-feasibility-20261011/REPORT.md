# Valencia multinucleon feasibility pilot for MINERvA ME-FHC: report

**Date 2026-10-11. Owner: this session (valencia-feasibility lane). Review status: see §11.**
Base: remote `main` `3892e769`. Frozen plan: [`PLAN.md`](PLAN.md), committed as `2492f16b` before any
scientific computation. This report authorizes nothing and adopts nothing.

## 1. Verdict: INCONCLUSIVE, blocked on one named external input

**The corrected Valencia calculation cannot be implemented faithfully from anything publicly
available.** Neither the corrected tensors nor the corrected exclusive sampler is released, so no
benchmark of the corrected model was possible (§3). This is a missing input, not a demonstrated
impossibility. The authors state that inclusion in event generators is under way. That rules out
NO-GO and also GO.

**Evaluating it would be cheap once the input exists.** A predecessor pilot in the same table format
(Valencia 2020 in NuWro 25.11.1) measured ≤ 0.13 ms of CPU per sampled event with nuclear transport at
the ME-FHC flux. It also measured Kish N_eff/N = 0.096, and 96.7% of the weighted rate inside the
truth signal (§5). Generating the four-configuration matched comparison (§7) needs at most about
0.25 core-hours, or 0.74 with a ×3 margin on the effective-statistics estimate. The memo assumed
83–833 core-hours. Detector-level work is the only potentially large cost, and it was not measured.

**The predecessor tables are only partly faithful to their own publication.** Against the authors'
published 1 GeV carbon values, the table route gives −10.4% for ν (B1, QUALIFIED) and +10.2% for ν̄
(B2, PASS). The ν̄/ν ratio is 0.276 against the published 0.225, under any tested energy-shift
convention. A corrected-versus-predecessor comparison could therefore not be read at the ≲10% level
until the conventions (V_ud, energy shift) are fixed with the authors (§4).

**What would turn this into a GO:** the authors provide the corrected per-channel tensor tables with
their conventions (§8). Then the table route can be benchmarked against their published curves and
run at negligible cost. A faithful **exclusive** prediction also needs their microscopic sampler, or
distributions for re-fitting NuWro's sampler; its cost is unknown. Obtaining either requires an
external request, which this authorization does not cover. That is Joseph's decision.

## 2. Scope, roles and resources actually used

Authorized: isolated implementation and a CPU pilot, capped at 10 core-hours (36,000 core-s) and
10,000 generated events in total. The caps were enforced before every launch by
[`code/pilot_run.py`](code/pilot_run.py). Each run had an append-only ledger entry, an event cap compiled
into NuWro (exit 97 at the cap) and `ulimit -t`.

| Resource | Used | Cap |
|---|---:|---:|
| Scientific CPU (all runs, integrator, analysis, diagnostics) | **124.2 core-s (0.034 core-h)** | 36,000 core-s |
| Generated events charged | **7,900** | 10,000 |
| of which: failed config run R0 (sampled nothing; charged its full allotment by the conservative rule) | 200 | — |
| Software builds (Pythia6 wrapper, NuWro ×3), recorded as setup rather than science | ≈ 2.5 core-min | — |
| GPU, cluster jobs, paid resources, detector simulation, fits, external messages | none | none |

Hardware: Apple M1 Pro (local), macOS 26 (Darwin 25.6.0), ROOT 6.36.00 (Homebrew), GCC/gfortran
15.2.0, Python 3.12.2, numpy 1.26.4. Per-run detail: [`logs/budget_ledger.jsonl`](logs/budget_ledger.jsonl).
No existing product was modified. The local memo was preserved byte-identical (SHA-256 `4f3da639…`) and
is not committed.

## 3. Implementation identity

| Object | Public implementation | Identity evidence |
|---|---|---|
| Valencia 2011 inclusive 2p2h (Nieves et al., PRC 83, 045501) | GENIE `data/evgen/hadron_tensors/nieves/HadTensor120-Nieves-<nucleus>-{FullAll,Fullpn,DeltaAll,Deltapn}-20150210.dat` for C, O, Si, Ca, Fe, Ba, Pb; last changed by commit `689808ee6b` (2018-10-29). NuWro `mec_kind=3`. | The repository's GENIE+MEC comparison used this model, through GENIE 2.12.10c. |
| Valencia 2020 exclusive (Sobczyk, Nieves, Sánchez, PRC 102, 024601) | NuWro ≥ 25.03, `mec_kind=6`, `src/MEC_data/{C12,O16,Ca40}/*_{pp,np,pn,3p3h}.h`. Added in commit `bd312957b6` (2025-03-11), never changed since. Tag `NuWro_25_11_1` = `6ef4144b`. | Per-nucleon W00, W03, W11, W12, W33 on a 10 MeV grid to 1.2 GeV, upper-triangular, for the pp, np, pn and 3p3h channels. Nucleon kinematics come from a **parametrized** sampler, with (P, l) fitted to the 2020 exclusive distributions (Prasad et al., PRD 111, 036032, §III). That paper's footnote 1 states that the 2025 revision is not included. |
| **2025 correction** (Sobczyk and Nieves, PRC 111, 025502; arXiv:2407.21587 v1) | **None.** The arXiv record has no ancillary files. The TeX source (SHA-256 `d4163b6f…`) contains no data or code statement beyond "work is currently underway to include our predictions in Monte Carlo event generators". GENIE and NuWro tables are unchanged since before the paper. | Physics content, checked from the source: removal of the constant −k_F²/2M from the virtual-nucleon energy in the W N → N′π amplitude (§II B(c), Eq. 10). Also a local p_Δ²/M_Δ² factor in the Δ propagator, C₅ᴬ(0) about 20% larger, and Re Σ_Δ^eff varied over [−50, +30] ρ/ρ₀ MeV as the model uncertainty. S_NN ≈ 27 MeV (C) and 22 MeV (O); |q| < 1.2 GeV. |
| **2026 exclusive study** (Kasturi, Nieves, Sánchez, Sobczyk; arXiv:2603.28314; PRD 114, 012002) | **None.** It ran inside NEUT, with no availability statement. Its §VI says naive tabulation of the exclusive response is "prohibitively large", and proposes on-the-fly samplers or surrogates. | Fixed E_ν = 450, 650, 1000 MeV; ¹²C; S = 27.41 MeV. |
| GENIE ≥ 3.6 tunes, SuSAv2 | Present, but they are other models. None was substituted. | — |

The pilot therefore ran only the **predecessor**, and it is labelled as such throughout. It resolved
the cost, support, statistics and bookkeeping uncertainties that do not depend on the correction's
numbers. It is not a substitute for the corrected model.

## 4. Benchmarks: frozen before running, graded mechanically

An independent integrator, [`code/valencia_tensor_xsec.py`](code/valencia_tensor_xsec.py), builds
W^{μν} in the frame q ∥ z from the five tabulated components. It contracts W with an explicitly
constructed lepton tensor and integrates on the table grid. It shares with NuWro only the table values
and the declared NuWro energy-shift convention. The VA sign is fixed by requiring σ_ν > σ_ν̄. Grades
come from [`code/grade_benchmarks.py`](code/grade_benchmarks.py) and are recorded in
[`results/benchmarks.json`](results/benchmarks.json).

| Id | Result | Frozen tolerance | Grade |
|---|---|---|---|
| B0 quadrature, N vs 2N | 2×10⁻⁵ | ≤ 0.2% | **PASS** |
| B1 ν ¹²C 1 GeV, per nucleus, vs published 2020 "around 1.38" ×10⁻³⁸ cm² | 1.2368 (−10.4%) | PASS ≤ 7%, QUALIFIED ≤ 15% | **QUALIFIED** |
| B2 ν̄ ¹²C 1 GeV vs published "0.31" | 0.3417 (+10.2%) | PASS ≤ 12% | **PASS** |
| B3 NuWro weighted mean vs integrator, 1 GeV | 1.2670 ± 0.0238 per nucleus (+2.4%, 1.3 σ) | ≤ max(3σ_MC, 1%) = 5.8% | **PASS** |
| B4 channel fractions, NuWro vs integrator | pp 0.571 ± 0.014 vs 0.604; np+pn 0.181 ± 0.011 vs 0.163; 3p3h 0.248 ± 0.012 vs 0.233 (pulls −2.4, +1.6, +1.3) | each ≤ 3σ | **PASS** |
| B5 primary-vertex three-momentum balance | R1: max 3 eV. R2: 3 of 1,458 events above 1 keV (max 1.47 keV); all are 3p3h at 12–15 GeV, with \|Δp\| = 1.0×10⁻⁷ E_ν | ≤ 1 keV per event | **FAIL** (numerical; physically negligible) |

B4 uses the delta-method error of the weighted ratio estimator, the weighted-event analogue of the
plan's "binomial σ". B3 has 1.9% MC precision, so it cannot resolve the 5.2% V_ud² question below.

**Findings from the benchmarks.**

1. **V_ud convention is ambiguous.** NuWro's coupling constant (`jednostki.h:52`) is G_F without
   V_ud. GENIE's `TabulatedLabFrameHadronTensor::dSigma_dT_dCosTheta`, applied to the same author's
   2011 tensors, also uses `kGF2` without V_ud, although the Rosenbluth-form path in the same class
   (`dSigma_dT_dCosTheta_rosenbluth`) applies `CKM-Vud` explicitly. Two independent generator implementations therefore treat V_ud² as absorbed in the
   Valencia tables. The integrator's frozen convention included it. Without V_ud², B1 becomes −5.5%
   and B2 +16.3%. Neither convention puts both inside their PASS bands.
2. **The energy shift does not explain the gap.** A diagnostic varied the shift B in
   [`code/convention_sensitivity.py`](code/convention_sensitivity.py); results are in
   `logs/D5-convention.log`. With B = 0, ν gives 1.377, matching the published value, but ν̄ gives
   0.389 (+26%). At B = 27.41 MeV (the corrected paper's carbon S) ν gives 1.156 and ν̄ 0.303. The
   ν̄/ν ratio stays at 0.262–0.283 against the published 0.225. The VA-interference part of the
   distributed 2020 tables is weaker, relative to the symmetric part, than in the authors' published
   figure. It is a ~10% fidelity limitation of the predecessor implementation that the public material
   cannot resolve.
3. **NuWro's structure-function expression has a lepton-mass error.** It fails the covariant identity
   L_{μν}q^μq^ν = m_μ²(k·k′); the explicit contraction passes that identity and two others
   ([`code/algebra_check_covariant.py`](code/algebra_check_covariant.py)). Part of the cause is that
   NuWro's W4 term uses sin²θ where 2 sin²(θ/2) is required. GENIE's implementation uses the correct
   form, but this one term does not account for the whole difference. The integrated effect at 1 GeV is
   −0.31% (ν) and −1.1% (ν̄) ([`code/algebra_check_w4.py`](code/algebra_check_w4.py)).
4. **3p3h events do not conserve energy.** Every 3p3h event loses 2.5–3.2 MeV at the primary vertex
   (644 of 644 in R1). 2p2h events conserve energy to within 2 eV.

A reproduction test for future corrected tables, from the TeX source: at 1 GeV, ¹²C, |q| < 1.2 GeV, the
corrected model gives ν 1.69 (+30 ρ/ρ₀ MeV) to 2.39 (−50 ρ/ρ₀ MeV) ×10⁻³⁸ cm². For ν̄ it gives 0.50 to
0.62. The nominal Re Σ = 0 value is not printed in the text.

## 5. Pilot measurements (predecessor, ¹²C, MEC only, NuWro transport)

R2 used 4,000 sampled events at the corrected ME-FHC data flux. The flux is `phi_t.npz`
(SHA-256 `bbcbade3…`, bound in the committed `s5p/gen5d/gen5d-fluxfix-2.json`). It was converted to a
ROOT histogram with contents = density × width, because NuWro samples bin contents as probabilities;
the integral matches Φ_t = 6.243343377×10⁻⁴ m⁻²/POT exactly. Sampled E_ν against the flux:
χ² = 121.4/99 (p = 0.063), with no events outside 0–100 GeV. Full output:
[`results/R2/analysis.json`](results/R2/analysis.json).

| Uncertainty | Measurement |
|---|---|
| U1 throughput | ≤ 1.28×10⁻⁴ CPU-s per sampled event at the flux, setup included (0.512 s for 4,000). ≈ 5.7×10⁻⁵ s/event setup-subtracted at 1 GeV. Full NuWro CC model (R3, 1,000 trials, uniform channel mix): 8.5×10⁻³ s/trial. |
| U2 support | 99.6% of the flux-averaged rate comes from E_ν > 1.1 GeV, where |q| < 1.2 GeV makes the rate saturate. 86% comes from 3–10 GeV. 8.7 ± 0.8% comes from 1.1 < |q| < 1.2 GeV: the density does not vanish at the hard cut, so strength at |q| > 1.2 GeV is **absent**, not extrapolated. |
| U3 acceptance | 96.7 ± 0.5% of the weighted rate lies in the truth signal (θμ < 20°, 1.5 < p∥ < 60 GeV, pT < 4.5 GeV). |
| U4 statistics | 63.5% of trials have zero weight, because NuWro samples E′ uniformly up to E_ν while the tensor vanishes above |q| = 1.2 GeV. Kish N_eff/N = 0.096 and w_max/⟨w⟩ = 42; signal N_eff = 363. At 1 GeV the values are 0.53 and 5.6. Restricting the E′ proposal to ω ≤ 1.2 GeV + B would remove most zero-weight trials without changing the model. This was not done here. |
| U5 bookkeeping | Weighted means per event: ω = 489 MeV, T_p = 310 (63%), T_n = 106 (21.7%), pions 10 (2.1%). An unrecorded remainder of 63 MeV (12.8%) covers separation, residual excitation and recoil; NuWro records no residual nucleus and emits no de-excitation photons. Effective shift B = 16.827 MeV (ν, C), compared with S_NN ≈ 27 MeV in the corrected paper. After transport there are 2.10 protons and 1.05 neutrons per event. |
| U6 E_avail (repository Eq. 1, after transport) | Fraction of the predecessor MEC signal rate per bin: 0–0.1 GeV 18.5%; 0.1–0.2 GeV 20.7%; 0.2–0.4 GeV 28.0%; 0.4–0.8 GeV 30.4%; 0.8–1.5 GeV 2.4%; above 1.5 GeV 0. Signal N_eff per bin: 48, 55, 119, 161, 50. |

Scale, as context rather than a measurement of the corrected model:

- **NuWro σ̄.** 1.026 ± 0.050 ×10⁻³⁹ cm² per C nucleon, in NuWro's convention without V_ud.
- **Integrator fold, as a diagnostic.** 1.066×10⁻³⁹ with V_ud² and 1.125×10⁻³⁹ without; the fold is
  converged to 0.03%. NuWro differs by −3.8% (0.8σ) and −8.5% (1.9σ) respectively.
- **Committed GENIE 2011 value.** GENIE's Valencia-2011 MEC contributes 1.099×10⁻³⁹ per CH nucleon in
  the 3D signal region (`s5p/gen5d/gen5d-fluxfix-3.json`, "after").
- **Comparison.** The 2020 table route gives ≈ 0.92–1.00×10⁻³⁹ CH-equivalent, so the two are the
  same scale.

## 6. Applicability to ME-FHC

- **Flux and energy support.** The model is defined only for |q| < 1.2 GeV, as is the corrected
  paper's Fig. 8. GENIE's 2011 tables share the cut, so a predecessor/corrected comparison is matched
  in support. Neither describes multinucleon strength above the cut. Any ME-FHC statement must say it
  covers the |q| < 1.2 GeV component only.
- **Target mixture.** NuWro selects a table by proton number. H has no MEC (`nuwro.cc:397`,
  `A() <= 1`), which is correct. Z ≤ 6 uses ¹²C, 7–12 uses ¹⁶O and > 12 uses ⁴⁰Ca, per nucleon. For the
  reference tracker composition, C (88.51%) and O (2.50%) have direct tables and H (8.18%) is correctly
  zero. Ti, Cl, Al and Si (0.81% together) use the Ca proxy. The corrected paper shows only C and O.
- **E_avail definition.** It is reproducible exactly from the post-transport final state: proton
  kinetic energy, charged pions at E − 135 MeV, π⁰ and γ at total energy, neutrons excluded. Two
  generator limitations bias it low. NuWro emits no nuclear de-excitation photons, although Eq. 1
  counts photons. And the 21.7% of ω carried by neutrons and the 12.8% unrecorded remainder are
  invisible by construction. The pilot computed true ω and |q| from the lepton. No analysis estimator
  (such as the repository's truth W) was involved.
- **Transport versus detector.** All quantities are truth after NuWro's cascade. No detector response
  was applied.
- **Reweighting.**
  - *Within NuWro's model*, nucleon kinematics depend only on (ω, |q|), the channel and the fixed
    (P, l) sampler. Swapping tensors is therefore exactly a per-event, channel-wise inclusive weight
    on common support. Each configuration's own energy convention must be used in its weight.
  - *Faithful corrected exclusive distributions* are not available that way. The (P, l) parameters
    were fitted to the 2020 model. Kasturi et al. (§III, §IV.2) find that the corrected exclusive dynamics give a harder
    leading nucleon and a softer subleading one than the inclusive ("democratic") prescription, and that this
    survives the NEUT cascade. A
    faithful exclusive prediction needs new generation with the authors' sampler, or a re-fit of
    (P, l) to their corrected distributions.
  - *The existing Tune v1 detector MC* (GENIE 2.12.6 Valencia 2011 with MINERvA's enhancement) could
    be inclusively reweighted to corrected tensors where its support overlaps. That would first remove
    the enhancement, and it requires the corrected tables. It cannot introduce 3p3h multiplicity or
    corrected sharing, because GENIE's pair decay gives two nucleons isotropically.

## 7. Cost of the later matched-predecessor comparison (not executed)

Four MEC configurations on ¹²C, truth level with transport: the 2020 predecessor, the corrected
nominal, and the corrected Re Σ_Δ^eff = −50 and +30 ρ/ρ₀ MeV endpoints. All numbers come from
[`code/cost_model.py`](code/cost_model.py) and are recorded in [`results/cost.json`](results/cost.json).

| Item | Basis | Cost |
|---|---|---|
| MEC generation, 1% statistics per E_avail signal bin (10⁴ N_eff; limiting bin 0–0.1 GeV, 0.0119 N_eff per trial) | **measured** throughput and Kish values | 0.84 M trials/config, 3.4 M in total: **≤ 0.25 core-h**; ≤ 0.74 core-h with a ×3 Kish margin (assumption) |
| Same at 2% (2,500 N_eff) | measured | ≤ 0.06 core-h; ≤ 0.19 with margin |
| Full-model NuWro baseline (QEL, RES, DIS, COH + predecessor MEC), generated once; 2 M events | 8.5 ms/trial **measured**; unweighting factor 1–10 **assumed** | 4.7–47 core-h |
| Conversion to the 3D/5D grids with the existing converters | prior production record: under ~2 min per step (`README-gen5d-fluxfix.md`) | negligible |
| Corrected microscopic exclusive sampler | no code available | **unknown** ("computationally expensive", Kasturi et al. §I) |
| Detector simulation and reconstruction for detector-level predictions (memo stage 3) | no measurement; MINERvA simulation not available in this environment | **unknown**. The memo's 10 CPU-s/event (8,333 core-h per 3 M events) remains an assumption. |
| Obtaining corrected tables | external request to the authors | outside this authorization |

Precision is adequate at this cost. GENIE's 2011 MEC is 7–10% of the CV+MEC density in each bin below
0.8 GeV (committed `compare_mec_eavail-log.txt`). Using the published 1 GeV values as a proxy, the
corrected endpoints differ by ~35% of the MEC rate, or ≈ 3% of a bin, and corrected nominal versus
predecessor by ≈ 4%. A 1% MEC-sample precision contributes ≈ 0.1% to the bin. Nothing here establishes
the sign or size of the corrected model's E_avail effect at ME-FHC.

Cross-hardware caveat: throughput was measured on one Apple M1 Pro core. Per-core speed on a
Perlmutter CPU node may differ by a small factor. That factor is assumed, not measured, and does not
change the conclusion.

## 8. The exact missing input

To make a faithful corrected-model pilot possible, the Valencia authors (Sobczyk, Nieves) would need to
supply the following.

1. **Corrected inclusive tensor tables:** W00, W03, W11, W12, W33 for the pp, np, pn and 3p3h channels,
   on the (q0, |q|) grid to |q| = 1.2 GeV, for ¹²C and ¹⁶O. Three variants are needed: Re Σ_Δ^eff = 0,
   −50 ρ/ρ₀ and +30 ρ/ρ₀ MeV. Preferably they would also send the 2020 tables regenerated with the same
   code, so the predecessor is matched.
2. **Their conventions:** whether V_ud² is included; the energy shift (S_NN per channel versus a
   NuWro-style B) and the variable the tensor is evaluated at; the per-nucleon versus per-nucleus
   normalization; and the antineutrino and isospin treatment.
3. **Their 1 GeV and energy-dependent σ values**, for the table route to reproduce, for example the
   Fig. 8 curves as numbers.
4. **For exclusive fidelity:** the exclusive sampler used in arXiv:2603.28314, or its exclusive
   distributions in a form that allows re-fitting NuWro's (P, l) sampler, with their cost.

## 9. Limitations

- **Predecessor only.** No corrected-model number was computed. The throughput carries over to
  corrected tables only if they share the format; that is an assumption, plausible because only the
  tensor values change.
- **Benchmarks.**
  - B1 is QUALIFIED and B5 FAILs as frozen.
  - The published comparison values are single rounded numbers ("around 1.38", "0.31").
  - The V_ud convention is inferred from two generator implementations, not from the authors.
- **Statistics.** The R2 statistical precision is modest: σ̄ ± 4.8%, and Kish estimates from heavy-tailed
  weights are uncertain. The flux-level NuWro-versus-integrator difference (−3.8% or −8.5%, by
  convention) is within 2σ and was not a frozen benchmark.
- **Throughput resolution.** It is an upper bound, because setup CPU (~0.5 s) dominates runs of
  this size. NuWro's unweighting efficiency for the full model was not measured.
- **Model and detector coverage.** NuWro emits no de-excitation photons and records no residual
  nucleus. Only ¹²C was run. No detector response, background, unfolding or covariance was involved,
  and nothing here concerns data agreement.
- **Instrumentation side effect.** The patch's unused weighted-tree file could not be created, because
  NuWro prefixes `weighted.` to an absolute path. This printed a ROOT `SysError` with rc = 0 and did
  not affect the dumps.

## 10. Reproduction

Sources:
- NuWro: `https://github.com/NuWro/nuwro`, tag `NuWro_25_11_1` (`6ef4144ba190c277bfb3a9b5d16116bd68864683`).
- Pythia6 wrapper: `https://github.com/luketpickering/ROOTEGPythia6` (`feb7c7eb8d368aee20bf1cb01f1bbfb9cfaeb6b5`).
- Instrumentation patch (event cap and dump only; no physics change):
  [`code/nuwro-pilot-instrumentation.patch`](code/nuwro-pilot-instrumentation.patch), SHA-256
  `e6421098…`. Patched binary SHA-256 `d9b658b5…`, rebuilt after the dump-unit fix; the R0b dump came
  from the earlier binary and is converted by `analyze_dump.py`.
- Table files (SHA-256): C12_pp `4c4a2fc2…`, C12_np `34fb9080…`, C12_pn `bcac99b4…`,
  C12_3p3h `98432620…`; `mecevent_2020Valencia.cc` `996c8177…`.

```bash
# build (macOS; SDKROOT needed by gfortran)
export SDKROOT=$(xcrun --show-sdk-path) ROOTSYS=$(root-config --prefix)
git clone https://github.com/luketpickering/ROOTEGPythia6 && (cd ROOTEGPythia6 && mkdir build && cd build \
  && cmake .. -DROOTEGPythia6_Pythia6_BUILTIN=ON && make install)
export ROOTEGPythia6_ROOT=$PWD/ROOTEGPythia6/build/Darwin
git clone --branch NuWro_25_11_1 https://github.com/NuWro/nuwro && cd nuwro
patch -p0 < .../code/nuwro-pilot-instrumentation.patch   # paths are src/nuwro.cc{.orig,}
GF=$(dirname $(gfortran -print-file-name=libgfortran.dylib))
make bin/nuwro LDFLAGS="\$(shell \${ROOTSYS}/bin/root-config --libs) -L$ROOTEGPythia6_ROOT/lib \
  -Wl,-rpath,$ROOTEGPythia6_ROOT/lib -lEGPythia6 -lPythia6 -lGeom -lMinuit -L$GF -Wl,-rpath,$GF -lgfortran"
# flux: copy phi_t.npz from /pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/ and check sha256 bbcbade3...
python3 -I code/make_flux_root.py inputs/phi_t.npz inputs/flux_mefhc_phi_t.root
# every step goes through the ledger, e.g.
python3 -I code/pilot_run.py --ledger logs/budget_ledger.jsonl --run-id R2-mefhc-flux --events 4000 \
  --cpu-seconds 7200 --workdir results/R2 --dump results/R2/dump.txt --log logs/R2-mefhc-flux.log \
  -- $NUWRO/bin/nuwro -i inputs/params-R2.txt -o results/R2/R2.root
python3 -I code/analyze_dump.py results/R2/dump.txt --flux-npz inputs/phi_t.npz --json-out results/R2/analysis.json
python3 -I code/valencia_tensor_xsec.py --nuwro-src $NUWRO/src --energies 1000 --beam nu --n-sub 8
python3 -I code/flux_fold.py $NUWRO/src inputs/phi_t.npz 8 results/integrator-C12-nu-fluxfold-n8-g72.json 72
python3 -I code/grade_benchmarks.py && python3 -I code/cost_model.py
```

The exact command lines of every run are in the ledger. The parameter files are in `inputs/`. The flux
copies (`phi_t.npz`, the ROOT histogram and its macro) are not committed; they are referenced by digest
and path.

## 11. Review

See [`REVIEW.md`](REVIEW.md) if present. If it is absent, these results are **owner-checked** only.

## 12. Recommendation

Joseph should decide whether to request the §8 inputs from the Valencia authors. That would be an
external contact, which needs his authorization. Before any physics use, an **independent domain
expert** should validate an implementation of the corrected calculation. That means a nuclear theorist
outside the Valencia group, for the currents, energy conventions and channel overlap, and a generator
developer, for the tensor-to-event and exclusive-sampling consistency. The memo suggests Noemi Rocco
and Stephen Dolan as expertise matches. They have not been contacted, and their independence has not
been checked.
