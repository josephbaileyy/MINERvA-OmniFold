# Valencia multinucleon feasibility pilot: frozen plan

**Frozen 2026-10-11, before any scientific computation.** Base: remote `main`
`3892e769043cddebfd58ec19e1ab1a567eb01784`. Branch `study/valencia-feasibility-20261011`.
Source memo (local, uncommitted, preserved, not evidence):
`docs/research/MINERVA-MODEL-IMPROVEMENT-MEMO-20261011.md`, SHA-256
`4f3da639aa816eae1b097b5dd1b44695a218e1ac25213d32b5309053213a4e22`. Its deductions and cost figures
are treated as hypotheses.

## 1. Decision, roles and terminal outcomes

**Question.** Can the corrected Valencia multinucleon calculation (Sobczyk and Nieves, PRC 111,
025502 (2025), arXiv:2407.21587) be implemented faithfully and evaluated economically for MINERvA
ME-FHC? Improved data agreement is not a criterion.

**Roles.** Joseph owns the scientific decision. This session owns the pilot. At most one fresh
read-only reviewer may examine the frozen artifacts, with one focused correction pass inside the same
caps. Without one, results are labelled owner-checked.

**Terminal outcomes.**

- **GO**: an identified, faithful implementation of the corrected calculation is available or
  obtainable with a named, bounded step; benchmarks pass; measured throughput makes the later matched
  comparison affordable. GO means a larger study merits Joseph's consideration. It authorizes nothing.
- **NO-GO**: a faithful implementation is shown to be unobtainable, or measured cost or support makes
  a faithful evaluation unreasonable.
- **INCONCLUSIVE**: a required input is missing or a benchmark cannot be decided. The exact missing
  input is named.

## 2. Identity finding recorded before computation

Established from primary sources before this plan was written (details and links in the report):

| Object | Public implementation found | Status |
|---|---|---|
| Valencia 2011 inclusive 2p2h (PRC 83, 045501) | GENIE `data/evgen/hadron_tensors/nieves/HadTensor120-Nieves-*-20150210.dat`; NuWro `mec_kind=3` | Available. This is what the repository's GENIE+MEC comparison used. |
| Valencia 2020 exclusive 2p2h/3p3h (PRC 102, 024601) | NuWro 25.03 and later, `mec_kind=6`: per-channel (pp, np, pn, 3p3h) tensor tables plus a **parametrized** nucleon sampler fitted to the 2020 exclusive distributions (Prasad et al., PRD 111, 036032) | Available. Its paper excludes the 2025 correction (footnote 1). |
| 2025 corrected calculation (PRC 111, 025502) | None found: GENIE tables unchanged since 2018-10-29; NuWro `src/MEC_data` unchanged since 2025-03-11; no tables or code with the paper | **Not publicly available.** |
| 2026 exclusive study with the corrected model (PRD 114, 012002; arXiv:2603.28314) | Ran inside NEUT; no data or code availability statement | **Not publicly available.** |

Therefore the corrected calculation **cannot** be benchmarked or run in this pilot. The pilot runs the
**predecessor** (Valencia 2020 in NuWro 25.11.1, `mec_kind=6`) only to resolve the named
uncertainties below. It is labelled predecessor everywhere and is not a substitute for the corrected
model.

## 3. Named uncertainties the pilot may resolve

- **U1 throughput.** CPU seconds per generated event for a table-driven Valencia sampler with nuclear
  transport at the ME-FHC flux. The memo assumed 0.1–1 s, unmeasured.
- **U2 support.** Fraction of the flux-averaged predecessor 2p2h+3p3h rate from neutrino energies on
  the model's |q| < 1.2 GeV plateau, and the fraction of events near that hard cut.
- **U3 acceptance.** Weighted fraction inside the analysis truth signal
  (θμ < 20°, 1.5 < p∥ < 60 GeV, pT < 4.5 GeV).
- **U4 statistics.** Weight dispersion: Kish N_eff/N overall, in the signal, and per E_avail bin;
  trials per unweighted event, w_max/⟨w⟩.
- **U5 bookkeeping.** Primary-vertex four-momentum balance, the energy convention (NuWro's
  effective shift versus the corrected paper's two-nucleon separation energy), and the partition of
  energy transfer among protons, neutrons, pions and an unrecorded remainder after transport.
- **U6 E_avail.** Truth E_avail (repository Eq. 1) distribution of the predecessor sample in the
  analysis bins `[0, 0.1, 0.2, 0.4, 0.8, 1.5, 3, 100]` GeV.

## 4. Frozen benchmarks and tolerances

The table normalization and contraction are tested by an **independent integrator** written for this
pilot. It builds W^{μν} from the five tabulated components in the frame q ∥ z, contracts it with an
explicitly constructed lepton tensor, and integrates by quadrature. It shares only the table values
and the declared NuWro energy-shift convention with NuWro.

| Id | Comparison | Tolerance (frozen) | Justification |
|---|---|---|---|
| B0 | Quadrature convergence: integrator at grid N vs 2N | ≤ 0.2% | Numerical error must be small against B1–B3 |
| B1 | νμ ¹²C, E = 1 GeV, 2p2h+3p3h per nucleus, |q| < 1.2 GeV: integrator vs published Valencia 2020 value "around 1.38 × 10⁻³⁸ cm²" (arXiv:2407.21587, Sec. III, Fig. 8 text) | PASS ≤ 7%; QUALIFIED ≤ 15%; else FAIL | The published value is from the authors' code. The table route adds NuWro's energy-shift convention, 10 MeV grid interpolation and q ≥ 10 MeV. |
| B2 | ν̄μ ¹²C, same, vs published "0.31" | PASS ≤ 12%; QUALIFIED ≤ 25%; else FAIL | Interference-dominated small value; tests the sign and normalization of W12. Isoscalar target: same tensor for both beams. |
| B3 | νμ ¹²C, E = 1 GeV: NuWro weighted-event mean vs integrator | \|Δ\| ≤ max(3 σ_MC, 1%) | Same tables and convention; tests NuWro's sampler and normalization |
| B4 | Channel fractions (pp, np, pn, 3p3h): NuWro event counts vs integrator | each within 3 binomial σ | Channel bookkeeping |
| B5 | Primary vertex: p_ν + Σ p_in = p_μ + Σ p_out (three-momentum) | \|Δp\| ≤ 1 keV per event | Numerical conservation. The energy component is reported against the declared convention, not graded. |

B1/B2 test the predecessor tables only. **No benchmark of the corrected model is possible in this
pilot.** Recorded for a future implementer: the corrected model's published 1 GeV values are
1.69–2.39 (ν) and 0.50–0.62 (ν̄) × 10⁻³⁸ cm² across Re Σ_Δ^eff ∈ [+30, −50] ρ/ρ₀ MeV, with
|q| < 1.2 GeV.

## 5. Runs and budget

Authorized caps: **10 CPU core-hours (36,000 core-s) of scientific computation and 10,000 generated
events in total**, including setup integrations, failures, reviews and reruns. A generated event is
any call to NuWro's event sampler (`NuWro::makeevent`), including zero-weight trials. Integrator
quadrature points are not events, but integrator CPU counts against the CPU cap. Building software is
setup, not science; its CPU is recorded separately and reported.

| Run | Purpose | Events | CPU allotment |
|---|---|---:|---:|
| R0 | Smoke test, 1 GeV, ¹²C, MEC only, FSI on | 200 | 600 s |
| R1 | B3, B4, B5 at 1 GeV | 2,500 | 3,600 s |
| R2 | U1–U6 at the ME-FHC flux, ¹²C, MEC only | 4,000 | 7,200 s |
| Reserve | Failure, rerun, review, or one expansion that resolves a named uncertainty | 3,300 | remainder |

**Enforcement.** `code/pilot_run.py` reads the append-only ledger `logs/budget_ledger.jsonl`, refuses
to launch when ledger totals plus the request would exceed either cap, exports
`NUWRO_PILOT_EVENT_CAP` (an instrumentation patch makes NuWro exit with code 97 before sampling one
event more), sets `ulimit -t` to the run's CPU allotment, and appends the measured user+sys CPU and the
dumped event count after each run.

Flux: the corrected data flux `phi_t.npz` (SHA-256 `bbcbade3…`, bound in the committed
`docs/orchestration/state/s5p/gen5d/gen5d-fluxfix-2.json`), converted to a ROOT histogram whose bin
contents are density × width, because NuWro's `EnergyProfile::readHistRoot` treats contents as bin
probabilities. The sampled E_ν distribution of all trials is checked against the flux.

## 6. Out of scope

No corrected-model run, GPU, new paid resource, detector simulation, MINERvA fit, unfolding,
covariance construction, adoption or external contact. The later matched comparison (predecessor,
published nominal, and the Re Σ_Δ^eff = −50 and +30 ρ/ρ₀ MeV endpoints) is costed, not run.
