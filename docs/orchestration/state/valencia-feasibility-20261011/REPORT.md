# Valencia multinucleon feasibility pilot for MINERvA ME-FHC: report

**Date 2026-10-11. Owner: this session (valencia-feasibility lane). Reviewed once (read-only, fresh context) with one correction pass applied; see §11 and [`REVIEW.md`](REVIEW.md). Then repaired once, under a separate allowance, for two named defects: the VA-sign convention (fixed) and the launcher's CPU bound (accounting improved; aggregate CPU enforcement still incomplete). See [`REPAIR.md`](REPAIR.md), which records one targeted review and one correction pass; its §R6 is the terminal disposition. The verdict is unchanged.**
Base: remote `main` `3892e769`. Frozen plan: [`PLAN.md`](PLAN.md), committed as `2492f16b` before any
scientific computation. This report authorizes nothing and adopts nothing.

## 1. Verdict: INCONCLUSIVE, blocked on one named external input

**The corrected Valencia calculation cannot be implemented faithfully from anything publicly
available.** Neither the corrected tensors nor the corrected exclusive sampler is released, so no
benchmark of the corrected model was possible (§3). This is a missing input, not a demonstrated
impossibility. The authors state that inclusion in event generators is under way. That rules out
NO-GO and also GO.

**Inclusive (table-route) evaluation would be cheap once the input exists; faithful exclusive
evaluation is still uncosted.**

- *Measured.* A predecessor pilot in the same table format (Valencia 2020 in NuWro 25.11.1) measured
  0.13 ms of CPU per sampled event, with nuclear transport, at the ME-FHC flux. This includes setup,
  so it is an upper bound on the per-event cost of that 4,000-event run on one core. It also measured Kish
  N_eff/N = 0.096, and 96.7% of the weighted rate inside the truth signal (§5).
- *Table-route generation.* MEC generation for the four-configuration comparison, using NuWro's
  parametrized nucleon sampler, extrapolates to ≈ 0.25 core-hours. That rises to ≈ 0.74 with a ×3
  margin on the effective statistics.
- *Full-model baseline.* A matched full-model NuWro baseline would add an extrapolated 4.7–237
  core-hours. The measured rate is 8.5 ms/trial; the unweighting factor is assumed (§7).
- *Status of these figures.* All core-hour figures are linear extrapolations from runs of 200–4,000
  events. They are **not certified bounds** (§7, REPAIR.md).
- *What remains uncosted.* The memo's 83–833 core-hour figure was for **faithful exclusive** generation
  with the corrected calculation. That cost is still **unknown**, because no exclusive sampler is
  available (§6, §8). Detector-level work was also not measured.

**The predecessor tables are only partly faithful to their own publication.** The integrator uses the
authors' convention: cos²θ_C sits inside W, as in Nieves et al. 2011, and NuWro and GENIE do the same.
Against the authors' published 1 GeV carbon values, the table route then gives −5.5% for ν (B1) and
+16.3% for ν̄ (B2). Both are now recorded **UNVALIDATED**.
- The VA sign is derived from the authors' conventions (metric, ε tensor, V−A current, W = W_s + iW_a).
  The contraction is verified against an independent Dirac trace **under the declared W12 encoding**.
- The mapping of the table column W12 to Im W^{12}, however, is not documented by the authors. It is
  corroborated by two generator implementations (§4; REPAIR.md §1).

Under that encoding:
- the symmetric part agrees with the published values to about 1–2%;
- the VA-interference part is about 12% low;
- the ν̄/ν ratio is 0.276 against the published 0.225, independent of V_ud and of any tested energy
  shift. A corrected-versus-predecessor comparison could therefore not be read at the
≲10% level for antineutrino-sensitive or VA-sensitive quantities. That changes only if the authors
regenerate both table sets with one code (§4, §8).

**What would turn this into a GO:** the authors provide the corrected per-channel tensor tables with
their conventions (§8). Then the table route can be benchmarked against their published curves and
run at negligible cost. A faithful **exclusive** prediction also needs their microscopic sampler, or
distributions for re-fitting NuWro's sampler; its cost is unknown. Obtaining either requires an
external request, which this authorization does not cover. That is Joseph's decision.

## 2. Scope, roles and resources actually used

Authorized: isolated implementation and a CPU pilot, capped at 10 core-hours (36,000 core-s) and
10,000 generated events in total. Three controls applied to every campaign run:
- the launcher (`code/pilot_run.py` at `d75987e1`) refused a request that would exceed either cap given
  the ledger totals, and appended a ledger entry;
- NuWro carried a compiled event cap (exit 97);
- `ulimit -t` set a per-process CPU limit.

The repair (REPAIR.md §2) found that `ulimit -t` was **not an aggregate cap**:
- it is a per-process limit;
- macOS does not stop a process that ignores SIGXCPU, at either the soft or the hard limit (probe P1);
- the ledger was also read without a lock.

The charged CPU values still stand as measurements, for two reasons:
- the campaign's runs were sequential;
- any child that the job waited for is counted in the waited-children CPU. The NuWro executable's only
  process-creating import, `popen`, is reached only from NIWG plotting helpers. The ROOT libraries it
  links (`libCore`, `libCling`, `libMultiProc`) can create processes, so "no child process" is not
  established statically. Only a child that outlived NuWro unwaited would be missed; there is no
  evidence of one.

The per-run CPU limits were not certified bounds. The repaired launcher now reserves budget durably
under a lock, and it bounds a single-process job with a watchdog while the launcher runs. Aggregate CPU
enforcement is still incomplete (§9; REPAIR.md §R6). `pilot_run.py` is therefore **unsuitable for
any future authorization that requires a guaranteed aggregate CPU cap**. Such a run needs a separately
validated execution arrangement, preferably the project's guarded scheduler path. This limitation
does not invalidate the measured charges above.

| Resource | Used | Cap |
|---|---:|---:|
| Scientific CPU (all runs, integrator, analysis, diagnostics, review 16.6 s, correction-pass reruns) | **242.8 core-s (0.067 core-h)** | 36,000 core-s |
| Generated events charged (the reviewer and the correction pass generated none) | **7,900** | 10,000 |
| of which: failed config run R0 (sampled nothing; charged its full allotment by the conservative rule) | 200 | — |
| Software builds (Pythia6 wrapper, NuWro ×3), recorded as setup rather than science | ≈ 2.5 core-min | — |
| Repair (separate allowance; checks, probes and its review; no events, no NuWro execution) | see [`REPAIR.md`](REPAIR.md) and `logs/repair_ledger.jsonl` | 300 CPU-s |
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
| **2025 correction** (Sobczyk and Nieves, PRC 111, 025502; arXiv:2407.21587 v1) | **None.** The arXiv record has no ancillary files. The TeX source (SHA-256 `d4163b6f…`) contains no data or code statement beyond "work is currently underway to include our predictions in Monte Carlo event generators". GENIE and NuWro tables are unchanged since before the paper. | Physics content, checked from the source (§II B(c), Eq. 10). The constant −k_F²/2M was **missing** from the virtual-nucleon energy in the W N → N′π amplitude, which made the calculation inconsistent. The fix removes the term from all nucleon energies. Also a local p_Δ²/M_Δ² factor in the Δ propagator, C₅ᴬ(0) about 20% larger, and Re Σ_Δ^eff varied over [−50, +30] ρ/ρ₀ MeV as the model uncertainty. S_NN ≈ 27 MeV (C) and 22 MeV (O); |q| < 1.2 GeV. |
| **2026 exclusive study** (Kasturi, Nieves, Sánchez, Sobczyk; arXiv:2603.28314; PRD 114, 012002) | **None.** It ran inside NEUT, with no availability statement. Its §VI says naive tabulation of the exclusive response is "prohibitively large", and proposes on-the-fly samplers or surrogates. | Fixed E_ν = 450, 650, 1000 MeV; ¹²C; S = 27.41 MeV. |
| NuWro work in progress | Open NuWro PR #56 (fork `hprasad2419`, opened 2026-07-02). It adds a Pb208 grid for the **2020** model and empty (0-line) `src/mecevent_2025Valencia.{cc,h}` files. | An implementation of the 2025 model appears to be under way in NuWro. The PR contains no corrected tables or code. |
| GENIE ≥ 3.6 tunes, SuSAv2 | Present, but they are other models. None was substituted. | — |

The pilot therefore ran only the **predecessor**, and it is labelled as such throughout. It resolved
the cost, support, statistics and bookkeeping uncertainties that do not depend on the correction's
numbers. It is not a substitute for the corrected model.

## 4. Benchmarks: frozen before running, graded mechanically

An independent integrator, [`code/valencia_tensor_xsec.py`](code/valencia_tensor_xsec.py), builds
W^{μν} in the frame q ∥ z from the five tabulated components. It contracts W with an explicitly
constructed lepton tensor and integrates on the table grid. It shares with NuWro only the table values
and the declared NuWro energy-shift convention.

The VA-interference sign now follows a fixed convention, derived in REPAIR.md §1 from the authors'
metric, ε₀₁₂₃ = +1, lepton tensor, V−A current and W = W_s + iW_a. It was checked against an explicit
Dirac trace. Before the repair, the sign was chosen by requiring σ_ν > σ_ν̄, i.e. from the data. That
rule happened to select the same sign, so no committed value changed (check C7, relative change
≤ 7×10⁻¹⁶).

The table column W12 is read as Im W^{12}. The authors do not document that encoding. NuWro's code transcribes the authors' own 2004 structure-function formula, in which W₃ = −i W^{xy}/|q| (Nieves, Amaro and Valverde, PRC 70, 055503; TeX lines 279–312), with w3 = W12/|q|. GENIE independently reads the corresponding column of the authors' 2015 tables as Im W^{xy}. Check C6
shows that the integrator equals NuWro's expression.

The integrator's coupling convention is the authors': G_F² with no extra V_ud, because the tensor contains cos²θ_C.
The plan did not fix that convention. The first committed version (`3b4d81b3`) wrongly multiplied by
V_ud² as well. The review caught it, and the grades below come from the corrected rerun; the old grades
are kept as a diagnostic column in `benchmarks.json`. Grades
come from [`code/grade_benchmarks.py`](code/grade_benchmarks.py) and are recorded in
[`results/benchmarks.json`](results/benchmarks.json).

| Id | Result | Frozen tolerance | Grade |
|---|---|---|---|
| B0 quadrature, N vs 2N | 2×10⁻⁵ | ≤ 0.2% | **PASS** |
| B1 ν ¹²C 1 GeV, per nucleus, vs published 2020 "around 1.38" ×10⁻³⁸ cm² | 1.3044 (−5.5%) | PASS ≤ 7%, QUALIFIED ≤ 15% | **UNVALIDATED** (table W12 encoding not author-confirmed) |
| B2 ν̄ ¹²C 1 GeV vs published "0.31" | 0.3604 (+16.3%) | PASS ≤ 12%, QUALIFIED ≤ 25% | **UNVALIDATED** (table W12 encoding not author-confirmed) |
| B3 NuWro weighted mean vs integrator, 1 GeV | 1.2670 ± 0.0238 per nucleus vs 1.3044 (−2.9%, 1.6 σ; −2.6% after NuWro's −0.31% formula offset) | ≤ max(3σ_MC, 1%) = 5.5% | **PASS** |
| B4 channel fractions, NuWro vs integrator | pp 0.571 ± 0.014 vs 0.604; np+pn 0.181 ± 0.011 vs 0.163; 3p3h 0.248 ± 0.012 vs 0.233 (pulls −2.4, +1.6, +1.3) | each ≤ 3σ | **PASS** |
| B5 primary-vertex three-momentum balance | R1: max 3 eV. R2: 3 of 1,458 events above 1 keV (max 1.47 keV); all are 3p3h at 12–15 GeV, with \|Δp\| = 1.0×10⁻⁷ E_ν | ≤ 1 keV per event | **FAIL** (numerical; physically negligible) |

B4 uses the delta-method error of the weighted ratio estimator, the weighted-event analogue of the
plan's "binomial σ".

**B1/B2 status.** The B1/B2 status follows the repair's frozen rule. The tolerances are PLAN.md's,
unchanged. The superseded grades (PASS, QUALIFIED) are kept in `benchmarks.json` as
`grade_at_d75987e1_superseded`.

**B3/B4 stand.** NuWro and the integrator read W12 the same way (check C6), so B3 and B4 test the two
implementations against each other, not the encoding.

**Findings from the benchmarks.**

1. **The authors' papers fix the V_ud convention.** Nieves et al. 2011 (arXiv:1102.2777, TeX lines
   1275 and 1308) put cos²θ_C inside W^{μν}. The 2020 paper's prefactor is G²/4π² with no V_ud. NuWro
   (`jednostki.h:52`) and GENIE (`TabulatedLabFrameHadronTensor::dSigma_dT_dCosTheta`, `kGF2`) agree
   with the authors. The NuWro implementers' own paper writes G_F² cos²θ_C (Prasad et al.), which
   contradicts their code but not the authors. With the extra V_ud² that the first version wrongly
   applied, B1 would be −10.4% and B2 +10.2%.
   - *Where the gap sits* (under the distributor's W12 encoding). The symmetric part, (σ_ν + σ_ν̄)/2 ≈ 0.832 against the published 0.845,
     agrees to about 1.5%. The VA part, (σ_ν − σ_ν̄)/2 ≈ 0.472 against 0.535, is about 12% low.
   - *Caveat on that split.* The two beams use slightly different shifts, so this decomposition is
     approximate.
2. **The energy shift does not explain the gap.** A diagnostic varied the shift B in
   [`code/convention_sensitivity.py`](code/convention_sensitivity.py); results are in
   `logs/K-D5-convention.log`. In the authors' convention, B = 0 gives ν 1.453 (+5.3%) and ν̄ 0.411
   (+32%). B = 27.41 MeV (the corrected paper's carbon S) gives ν 1.219 (−11.7%) and ν̄ 0.319 (+3.0%).
   The ν̄/ν ratio stays at 0.262–0.283 against the published 0.225. Under the W12 encoding that NuWro
   uses, the VA-interference part of the distributed 2020 tables is weaker, relative to the symmetric part, than in the authors' published
   figure. It is a ~10% fidelity limitation of the predecessor implementation that the public material
   cannot resolve.
3. **NuWro's structure-function expression has a lepton-mass error.** It fails the covariant identity
   L_{μν}q^μq^ν = m_μ²(k·k′); the explicit contraction passes that identity and two others
   ([`code/algebra_check_covariant.py`](code/algebra_check_covariant.py)). Part of the cause is that
   NuWro's W4 term uses sin²θ where 2 sin²(θ/2) is required. GENIE's implementation uses the correct
   form, but this one term does not account for the whole difference. The integrated effect at 1 GeV is
   −0.31% (ν) and −1.1% (ν̄) ([`code/algebra_check_w4.py`](code/algebra_check_w4.py)).
4. **3p3h events do not conserve energy.** Every 3p3h event loses about 2.0–3.2 MeV at the primary
   vertex: 644 of 644 in R1 (2.09–3.10 MeV) and 594 in R2 (1.97–3.18 MeV); `logs/K-D6-3p3h-loss.log`.
   2p2h events conserve energy to within 2 eV.

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
| U1 throughput | ≤ 1.28×10⁻⁴ CPU-s per sampled event at the flux, setup included (0.512 s for 4,000). This is only an upper bound: the ~0.5 s setup jitter is larger than the per-event cost, and R2 with 4,000 events used less CPU than R0b with 200. Full NuWro CC model (R3, 1,000 trials, uniform channel mix): ≤ 8.5×10⁻³ s/trial. |
| U2 support | 99.6% of the flux-averaged rate comes from E_ν > 1.1 GeV, where |q| < 1.2 GeV makes the rate saturate. 86% comes from 3–10 GeV. 8.7 ± 0.8% comes from 1.1 < |q| < 1.2 GeV: the density does not vanish at the hard cut, so strength at |q| > 1.2 GeV is **absent**, not extrapolated. |
| U3 acceptance | 96.7 ± 0.5% of the weighted rate lies in the truth signal (θμ < 20°, 1.5 < p∥ < 60 GeV, pT < 4.5 GeV). |
| U4 statistics | 63.5% of trials have zero weight, because NuWro samples E′ uniformly up to E_ν while the tensor vanishes above |q| = 1.2 GeV. Kish N_eff/N = 0.096 and w_max/⟨w⟩ = 42; signal N_eff = 363. At 1 GeV the values are 0.53 and 5.6. Restricting the E′ proposal to ω ≤ 1.2 GeV + B would remove most zero-weight trials without changing the model. This was not done here. |
| U5 bookkeeping | Weighted means per event: ω = 489 MeV, T_p = 310 (63%), T_n = 106 (21.7%), pions 10 (2.1%). An unrecorded remainder of 63 MeV (12.8%) covers separation, residual excitation and recoil; NuWro records no residual nucleus and emits no de-excitation photons. Effective shift B = 16.827 MeV (ν, C), compared with S_NN ≈ 27 MeV in the corrected paper. After transport there are 2.10 protons and 1.05 neutrons per event. |
| U6 E_avail (repository Eq. 1, after transport) | Fraction of the predecessor MEC signal rate per bin: 0–0.1 GeV 18.5%; 0.1–0.2 GeV 20.7%; 0.2–0.4 GeV 28.0%; 0.4–0.8 GeV 30.4%; 0.8–1.5 GeV 2.4%; above 1.5 GeV 0. Signal N_eff per bin: 48, 55, 119, 161, 50. |

Scale, as context rather than a measurement of the corrected model:

- **NuWro σ̄.** 1.026 ± 0.050 ×10⁻³⁹ cm² per C nucleon, in the authors' convention (cos²θ_C inside W).
- **Integrator fold, as a diagnostic.** 1.125×10⁻³⁹ in the same convention, converged to 0.03%. NuWro
  is −8.8% (2.0σ) from it, uncorrected for the −0.31% formula offset. This was not a frozen benchmark.
  The MC error comes from Kish-limited, heavy-tailed weights.
- **Committed GENIE 2011 value.** GENIE's Valencia-2011 MEC contributes 1.099×10⁻³⁹ per CH nucleon in
  the 3D signal region (`s5p/gen5d/gen5d-fluxfix-3.json`, "after"). That sample is plain `gevgen
  Default+CCMEC` (`sbatch_gevgen_mec.sh`) with no MINERvA enhancement.
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
- **E_avail definition.** It is reproduced literally from the post-transport final state, as in
  `CVUniverse.h::GetEAvailableTrue`: proton kinetic energy with m_p = 938.27 MeV, charged pions at
  E − 135 MeV, π⁰ and γ at total energy, neutrons excluded. The first version used 938.272, a 2 keV
  difference per proton; the correction pass fixed it. Two
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
| MEC generation, 1% statistics per E_avail signal bin (10⁴ N_eff; limiting bin 0–0.1 GeV, 0.0119 N_eff per trial) | **measured** per-run throughput and Kish values, extrapolated linearly | 0.84 M trials/config, 3.4 M in total: **≈ 0.25 core-h (extrapolated)**; ≈ 0.74 core-h with a ×3 Kish margin (assumption) |
| Same at 2% (2,500 N_eff) | measured, extrapolated | ≈ 0.06 core-h; ≈ 0.19 with margin |
| Full-model NuWro baseline (QEL, RES, DIS, COH + predecessor MEC), generated once; 2 M events | 8.5 ms/trial **measured** (setup included); unweighting factor 1–50 **assumed** (the MEC channel alone measured w_max/⟨w⟩ = 42) | 4.7–237 core-h (extrapolated) |
| Conversion to the 3D/5D grids with the existing converters | prior production record: under ~2 min per step (`README-gen5d-fluxfix.md`) | negligible |
| Corrected microscopic exclusive sampler | no code available | **unknown** ("computationally expensive", Kasturi et al. §I) |
| Detector simulation and reconstruction for detector-level predictions (memo stage 3) | no measurement; MINERvA simulation not available in this environment | **unknown**. The memo's 10 CPU-s/event (8,333 core-h per 3 M events) remains an assumption. |
| Obtaining corrected tables | external request to the authors | outside this authorization |

**Extrapolated, not certified.** The core-hour figures are linear extrapolations of measured per-run
CPU. The measured runs were 4,000 MEC events and 1,000 full-model trials, on one Apple M1 Pro core. No
run approached these sizes, and none was executed under a certified aggregate CPU bound. They are
planning estimates, not caps.

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
supply the following. The NuWro developers are a possible second source: PR #56 suggests a 2025-model
implementation is in progress there.

1. **Corrected inclusive tensor tables:** W00, W03, W11, W12, W33 for the pp, np, pn and 3p3h channels,
   on the (q0, |q|) grid to |q| = 1.2 GeV, for ¹²C and ¹⁶O. Three variants are needed: Re Σ_Δ^eff = 0,
   −50 ρ/ρ₀ and +30 ρ/ρ₀ MeV. Preferably they would also send the 2020 tables regenerated with the same
   code, so the predecessor is matched.
2. **Their conventions:** confirmation that cos²θ_C stays inside W, as in Nieves et al. 2011; that the
   tabulated W12 is Im W^{12} = W_a^{12} in the convention of their `eq:lep` (ε₀₁₂₃ = +1); the energy shift (S_NN per channel versus a
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
  - B1 and B2 are UNVALIDATED, because the table W12 encoding is not author-confirmed. Their deviations
    are −5.5% and +16.3% against the frozen tolerances. B5 FAILs as frozen.
  - The coupling convention was set after the plan froze, by the review's citation of the authors'
    papers. The first committed grades used a double-counted V_ud².
  - The published comparison values are single rounded numbers ("around 1.38", "0.31").
- **Statistics.** The R2 statistical precision is modest: σ̄ ± 4.8%, and Kish estimates from heavy-tailed
  weights are uncertain. The flux-level NuWro-versus-integrator difference (−8.8%, 2.0σ) was not a
  frozen benchmark.
- **Throughput resolution.** It is an upper bound, because setup CPU (~0.5 s) dominates runs of
  this size. NuWro's unweighting efficiency for the full model was not measured. The §7 cost figures
  extrapolate these runs and are not certified bounds.
- **Table W12 encoding.** The VA sign is derived from the authors' conventions. That W12 = Im W^{12} in
  the distributed tables rests on NuWro's and GENIE's readings, which are consistent with the authors'
  2004 formula, but not on an author statement about the table column. B1 and B2 are therefore
  UNVALIDATED, and the "VA part ≈ 12% low" and ν̄/ν findings hold only under that encoding. §8 item 2
  asks the authors to confirm it.
- **Launcher: aggregate CPU enforcement incomplete.** The repaired launcher bounds a single-process
  job while it runs. If the launcher itself dies, its reservation stays charged and new launches are
  refused while the job lives. The orphaned job is then bounded only by the kernel RLIMIT_CPU, which
  holds only if the job leaves SIGXCPU at its default action (check L9).
  - **L9b demonstrates the failure.** An orphan ignoring SIGXCPU used 3.07 s of CPU against its
    2.5 s reservation and was still running when the test killed it. L9b "passes" by detecting this,
    which does not make it a budget-enforcement gate.
  - **Start-record window.** A SIGKILL of the launcher between `Popen` and the `start` record also
    leaves no live-orphan refusal.
  - **Consequence.** `pilot_run.py` is unsuitable wherever a guaranteed aggregate CPU cap is
    required (REPAIR.md §R6).
  
  Whether NuWro and ROOT run under the fork-denying
  sandbox, or leave SIGXCPU at default, was not executed (zero production compute). ROOT's libraries
  can fork, so the sandbox may make a NuWro run fail. That failure is closed and stays inside its
  reservation. The watchdog margin is an engineering margin, not a derived bound. It held with
  0.25 s of overshoot for one 10-thread job.
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

Repair checks: `python3 -I tests/check_va_convention.py $NUWRO/src results/repair/va_convention_checks.json`
and `python3 -I tests/test_pilot_run.py <scratch dir> results/repair/launcher_checks.json`, each run
through `code/repair_meter.py` (REPAIR.md). The campaign runs used the launcher at `d75987e1`. The
repaired launcher has been exercised only on synthetic jobs, never on NuWro. Do not use it to reproduce
or extend these runs under an authorization that requires a guaranteed aggregate CPU cap (§9).

The exact command lines of every run are in the ledger. The parameter files are in `inputs/`. The flux
copies (`phi_t.npz`, the ROOT histogram and its macro) are not committed; they are referenced by digest
and path.

## 11. Review

One fresh read-only reviewer examined the frozen commit `3b4d81b3` in a detached worktree. It used
16.6 CPU-s, generated no events and modified no file. It found no blocker, upheld the verdict and
reported two MAJOR and five MINOR findings. One focused correction pass followed; there was no second
review round. Findings and dispositions are in [`REVIEW.md`](REVIEW.md). The run logs are now committed;
the repository's `*.log` ignore rule had silently excluded them from `3b4d81b3`.

**Repair.** A later bounded repair (REPAIR.md) addressed two defects.
- **VA sign (fixed):** it had been chosen from the sign of the integrated interference. It is now
  fixed from the primary-source conventions, and the contraction is verified against an independent
  trace under the declared W12 encoding. No value changed. B1/B2 become UNVALIDATED pending author
  confirmation of the W12 encoding.
- **Launcher CPU bound (not fixed; accounting improved):** `ulimit -t` was not an aggregate bound.
  - *Added:* durable locked reservations, a single-process sandbox mode, and a watchdog that bounds
    the job while the launcher runs.
  - *Tested:* concurrency, crashes, interruption, child-process workloads and fail-closed ledgers.
  - *Still unenforced:* a job that ignores SIGXCPU and is orphaned by a launcher crash has no CPU
    bound; L9b demonstrates this. The `Popen`-to-`start`-record SIGKILL window also remains (§9).
  - *Status:* `pilot_run.py` is unsuitable for future authorizations that require a guaranteed
    aggregate cap.

The repair had one fresh, read-only, targeted review. It found no blocker, one MAJOR finding (a stale
B2 grade in §9) and MINOR findings. One correction pass followed (REPAIR.md R4; REVIEW.md). The
verdict is unchanged: INCONCLUSIVE.

## 12. Recommendation

Joseph should decide whether to request the §8 inputs from the Valencia authors. That would be an
external contact, which needs his authorization. An **unsent** draft request is in REPAIR.md §R7. It
separates the inputs needed for inclusive evaluation from those needed for E_avail predictions. Before any physics use, an **independent domain
expert** should validate an implementation of the corrected calculation. That means a nuclear theorist
outside the Valencia group, for the currents, energy conventions and channel overlap, and a generator
developer, for the tensor-to-event and exclusive-sampling consistency. The memo suggests Noemi Rocco
and Stephen Dolan as expertise matches. They have not been contacted, and their independence has not
been checked.
