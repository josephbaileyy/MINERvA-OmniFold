# Binding: the measurement plan's phase 1 (the director's rulings and grant, 2026-10-19)

**By** the paper-tighten lane, as director, under
[`DECISION-20261019-joseph-methods-first-and-measurement-compute`](../../DECISION-20261019-joseph-methods-first-and-measurement-compute.md).
Joseph told the measurement session to take its decisions, compute included, from the director. **The plan under
review** is [`PLAN.md`](PLAN.md), PR #165, head `208943e0`, phase-0 charge 0.0172 CPU node-h. The director read it in
full, with its corrections C1–C8.

**CITABLE FOR:** the rulings D1–D3 and D5–D7, the frozen specifications, and the phase-1 grant.
**NOT CITABLE FOR:**
- any result;
- any claim (claims are Joseph's);
- D4 (Joseph's act);
- the combined campaign (step 4), which needs its own contract and grant.

Joseph may override any ruling here. Rulings D1 and D5 are flagged to him.

## 1. Rulings

| # | ruling |
|---|---|
| **D1** | **Sizes for MP-1.** The documented source is the per-species response the MINERvA tuples apply: proton 3.5%, meson 5%, EM 3%, other 20%, plus **cross-talk 20%** if S0 shows it is a component of our observables' energy sums (gate G2), which the PLAN's species-sum identity implies. These sizes are applied by MINERvA's producer, match MAT's public header, and for p, π and e agree with test beam (PLAN §2.1). That meets PM-1's condition of upstream documentation rather than an invented shift (`DECISION-20260919…:79, :85`). **Muon** (2.4%) is excluded: the calibration already carries the muon energy bands. **Neutrons are out** of the MP-1 bands, following MAT's own convention that neutron response is carried by the hadron-reweight systematics (`ResponseSystematics.h:7-12`). GEANT_Neutron is already in the calibration. The result states that neutron response and completeness (energy dependence, resolution, correlations) are not covered. *Flagged to Joseph: this is a size ruling under PM-1.* |
| **D2** | QOS `shared` is permitted for phase-1 event loops and other jobs smaller than a node. Regular and debug are also allowed; premium never. |
| **D3** | Allowed: `Model.symmetry` on W2b's existing rr0/rr1/rrzero products, as a report-only linearity diagnostic for the recoil direction. It draws no new δ, changes nothing in W2, and does not reopen W2's terminal rule. |
| **D5** | The P0-OSB diagnostic (MP4-A) may run under the lifted pause, locally (0 node-h). Whether a non-OmniFold interval may serve as a measurement-paper candidate is decided only on a PASS. It would be an estimator change, which is Joseph's call. *Flagged to Joseph.* |
| **D6** | CH-corrected generator predictions are reported **beside** the A7 values, labelled as such, and never in place of them. A7 is not re-graded. |
| **D7** | The phase-1 grant is in §3. |

## 2. Specifications frozen by this record

The PLAN's draft specifications are frozen at head `208943e0`, with the amendments below. Any further change needs a
new committed record **before** the affected output exists.

- **MP1-A (PLAN §2.3)** is frozen.
  - Amendment: the band set R is {proton, meson, EM, other}, plus cross-talk under D1's condition. Whether cross-talk is
    in is fixed by S0's G2 result, before any J-cell number.
  - The q0 convention is fixed at S0 by the rule the PLAN states.
  - The z-draw seed key must be named in the S0 report before S2.
- **MP3-A and MP3-B (PLAN §4.3)** are frozen.
  - MP3-C: only the GiBUU-on-hydrogen **probe** is granted (≤ 2.3 node-h). A GiBUU-on-CH production goes into the
    combined campaign's contract.
- **MP4-A (PLAN §5.3)** is frozen.
  - Amendment: "the 68% radius" means the one-at-a-time radius, ψ² = χ²₁ quantile at 0.6827 (≈ 1.00) in the
    whitened χ². This is the optimistic choice for a necessary condition, so a FAIL stays decisive.
  - The gating control and the PASS rule are as written.
- **MP2-A (PLAN §3.3)** is not frozen in full. S0 (the descriptive probe) and S1 (the aligned dump, admitted on the
  bitwise `MCgen` check) are granted. S2 and S3 need a committed **feature contract** that the director has reviewed
  before any fit: F, the harmonization rules, the model family and hyperparameters, the folds and seeds, the weight cap,
  the V1–V5 thresholds as drafted, the hydrogen treatment (MP-3 coupling), and the replay rule.

## 3. Grant (phase 1, PLAN §6 steps 1–3)

- **Ceiling:** at most **35 charged CPU node-h** and **3 GPU node-h** on `m3246` / `m3246_g`. Each job is under 12 h,
  on QOS regular, shared or debug.
- **Storage:** outputs under `/pscratch/sd/j/josephrb/measurement-paper/`, and nothing written to CFS. CFS stays at
  3.6 TB, over Joseph's 3 TB rule, until he decides.
- **Ledger:** every job id, with its `sacct` charge, in `phase1/LEDGER.tsv`. The session stops when the ceiling is
  reached and reports what it has.
- **Order:** as PLAN §6.
  - Step 1 (MP4-A, MP3-A) first, and each of its results is reported to the director when it exists.
  - Steps 2–3 proceed unless a gate fails. A gate failure is reported before any dependent step.
- **The combined campaign** (step 4, ≈ 110–225 node-h) needs its own predeclared contract and a separate grant,
  sized against the group pool at that time.

## 4. Records landed from the PLAN (§8)

- **KNOWN_ISSUES row 97 (new):** the target mismatch for NuWro and GiBUU, quantified for GENIE per W bin; open until
  MP-3 (owner: the measurement session).
- **Row 82:** a note that GiBUU v2019 is on CVMFS (C1).
- **Corrigenda:**
  - Stage D REPORT:288 ("GiBUU is not on CVMFS") is corrected by C1.
  - `DESIGN-20260911-endpoint-B…:244` ("per-nucleon normalization absorbs the bulk") is corrected by C3.

  Both are recorded here and in row 97. The historical texts are left as written.

## 5. For the methods paper

C3 and C4 replace "unquantified" in the methods paper's target caveat with GENIE's measured per-W-bin range: +8.3% (W0)
and −2.2% (W1) per nucleon, or +5.6% / −4.6% in shape. The source is
`docs/orchestration/state/inelastic-high-region-20261011/results/r5_genie_events.json`. That is the director's
integration item; this record makes no deliverable change.
