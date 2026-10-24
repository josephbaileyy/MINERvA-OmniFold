# Report: PV-2D, the 2D prior-variation (model-dependence) test (2026-10-23)

**By** the session "2d test", under [`DECLARATION.md`](DECLARATION.md) as bound by [`BINDING.md`](BINDING.md), for the
director under [`ASSIGNMENT.md`](ASSIGNMENT.md) and [`../../lanes/COMMON-RULES.md`](../../lanes/COMMON-RULES.md).

The real 2D (p_T, p_∥) data were unfolded with **the Tune v1 prior reweighted by each generator's shape relative to
GENIE CV**, for three generators (GENIE+MEC, NuWro and GiBUU), on the estimator of the quoted 2D central value E_U
(configuration (a)). The four data unfolds (nominal and three generators) were repeated on RE-2's refined estimator
(binding option (a)); the closures were not. The shift is
each unfold's per-cell change against the Tune v1 nominal, and h is the largest |shift| over the three generators.

**CITABLE FOR:**
- the size and location of the 2D result's response to these three prior shapes, on these two estimators, at seed 42;
- the two nominal controls and the positive control, with their declared rules.

**NOT CITABLE FOR:**
- a per-cell bias bound. Amendment 6's caveat holds here too (§4): h is evidence about model dependence at these
  vertices, not a per-cell bias bound;
- an uncertainty component or a covariance;
- any claim change, KNOWN_ISSUES disposition or publication change. Those are Joseph's, through the director;
- the 2D-versus-5D comparison, which is the director's.

## 0. Outcome

- **Controls.**
  - The nominal control passes on both estimators:
    - configuration (a) reproduces E_U to 1.4e-11 relative (rule < 1e-5);
    - the refined arm reproduces RE-1's D2 to 1.6e-12 (rule ≤ 1e-8).
  - **The positive control passes on its primary form:**
    - 127 cells have a closure bias above 1% at NuWro;
    - the correlation of shift with −bias is 0.878 (rule ≥ 0.7);
    - the slope is 1.15 (rule [0.67, 1.5]).

    The ρ² fallback was therefore not run. h carries the label "measured with a passed positive control".
- **Configuration (a) shifts.**

  | | median \|shift\| | p90 | max |
  |---|---:|---:|---:|
  | GENIE+MEC | 1.26% | 3.83% | 9.82% |
  | NuWro | 1.69% | 7.48% | 21.4% |
  | GiBUU | 1.85% | 5.28% | 10.5% |
  | **envelope h** | **3.00%** | **8.30%** | **21.4%** |
- **Against σ.**
  - Against the adopted σ_tot (Q = S5 + C_PL, per-cell median 6.45%):
    - the median per-cell h/σ_Q is 0.44;
    - h > σ_Q in 30 of the 205 cells (14.6%);
    - h > σ_Q/2 in 84 cells (41.0%).
  - Against the published per-bin uncertainties (median 6.85%):
    - the median h/σ is 0.45;
    - h > σ in 28 cells (13.7%).
- **Where h exceeds σ_Q.**
  - The 30 cells fall in three regions:
    - 6 at forward low p_T (p_T < 0.15 GeV/c, p_∥ < 6 GeV/c);
    - 14 at p_T 0.33–0.70 GeV/c and p_∥ ≥ 8 GeV/c;
    - 10 at p_T 0.55–1.50 GeV/c and p_∥ 1.5–8 GeV/c.
  - NuWro sets h in 20 of them, GiBUU in 9 and GENIE+MEC in 1.
  - **A post-hoc diagnostic (not declared; §5).** In its dominant vertex's r, 21 of the 30 sit beside a step of
    more than 0.1 drawn by the bound noise gate (a coarse-pooled or noisy cell on one side). 4 sit beside steps
    between two own-ratio cells only, and 5 beside no such step. The tail of h co-locates with the gate's
    piecewise-constant reweight. No run tested whether a smoother reweight would remove it.
  - **Post hoc (not the declared readout).** Without the 52 cells beside a construction-drawn step in any vertex:
    - h is 2.59 / 6.29 / 15.5% (median / p90 / max) in configuration (a), and 2.61 / 5.44 / 14.3% in the refined
      arm;
    - h > σ_Q holds in 9 and 6 of the remaining 153 cells, against 30 and 26 of 205.
  - **The positive control is weaker on those remaining cells (post hoc).** The PC's strength is concentrated in the
    cells beside construction steps.
    - On the 45 PC cells beside one: corr 0.946, slope 1.19.
    - On the other 82: corr 0.652, slope 1.00. That is below the declared 0.7 bar, had the rule been applied to that
      subset; it was not, and the declared PC PASS stands.
    - So the reduced h above is less well covered by the positive control than the declared h is.
- **Refined arm.** On RE-2's refined estimator, h is 3.13 / 7.55 / 21.0% (median / p90 / max), and h > σ_Q in 26
  cells. Per cell, the two arms' shifts differ by a median of 0.35–0.43% and at most 5.6% (§6). The refined arm has
  no positive control of its own.
- **Compute.** 7.41 of the 17 CPU node-h cap. Ten jobs ran, all COMPLETED, each within its limit and none
  beyond 1.25× its projection.

## 1. What ran

| task | estimator | prior / pseudo-data | role | job | product sha256 |
|---|---|---|---|---|---|
| `data_tune_v1` | (a) | Tune v1 (r = 1) | NC, pilot, zero of the (a) shifts | 60175976 | `75b6d8e09e18619e…` |
| `data_genie_mec` | (a) | GENIE+MEC shape | vertex | 60182214 | `1d9d5fdab57a77d7…` |
| `data_nuwro` | (a) | NuWro shape | vertex; PC shift | 60182215 | `fbb98befd5c2e01f…` |
| `data_gibuu` | (a) | GiBUU shape | vertex | 60182216 | `d861eba7d6a5ce6b…` |
| `closure_tune_v1` | (a) | pseudo-data = MC (r = 1) | closure floor | 60182217 | `c7b9afa5956082b0…` |
| `closure_nuwro` | (a) | pseudo-data: the MC reweighted by NuWro's shape relative to GENIE CV | PC bias | 60182218 | `ebcc5a1e49bd2077…` |
| `data_ref_tune_v1` | refined | Tune v1 (r = 1) | NC_R, refined pilot, zero of the refined shifts | 60182219 | `f9da813cdfbcbcb3…` |
| `data_ref_genie_mec` | refined | GENIE+MEC shape | vertex | 60186225 | `72e3e44cc1227f9e…` |
| `data_ref_nuwro` | refined | NuWro shape | vertex | 60186226 | `ddec1c45fcbaae02…` |
| `data_ref_gibuu` | refined | GiBUU shape | vertex | 60186227 | `4bee262925d61a4a…` |

- **Deploys.**
  - Configuration (a) ran from a clean clone at `3631ea3f` (the bound pin).
  - The refined arm ran from a clean clone at `d67a5514`.
  - Both clones are on pscratch, and both were checked by the launcher (HEAD equal to the pin, no modified tracked
    files, no untracked files in the import directories).
- **Guard.** Every unfold ran through `nd-unfolding/mnv_guarded_run.py --expect-root <deploy>` (OI-136).
  - In all ten job logs, the guard's inventory lists one root: the job's own deploy (`deploy/repo` for the six (a)
    jobs, `deploy/repo-ref` for the four refined ones).
  - The modules `omnifold` and `pv2d_lib` load from it.
  - This is re-measured from the logs on pscratch; the logs are not committed.
- **Not run.** `data_nuwro_sq` and `closure_nuwro_sq` were not run: the primary positive control was powered, so
  the declared fallback rule did not trigger. <!-- absence-ok: scope of this lane's own runs; LEDGER.tsv lists every PV-2D job -->

## 2. The vertex reweights and the gate tiers

The reweights are the declared files (`DECLARATION.md` §3; `2d-unfolding/pv2d/ratios/`), unchanged. The binding asks for
each vertex's cells and share of the prior's truth weight in the three tiers, on the 205 reported cells:

| vertex | own ratio | coarse-cell ratio | r = 1 |
|---|---:|---:|---:|
| GENIE+MEC | 107 cells (86.52%) | 96 (13.44%) | 2 (0.04%) |
| NuWro | 108 (86.55%) | 95 (13.41%) | 2 (0.04%) |
| GiBUU | 45 (55.38%) | 100 (35.53%) | 60 (9.08%) |

GiBUU's 60 cells at r = 1 are 56 cells at p_∥ ≥ 10 GeV/c, off by definition (KNOWN_ISSUES 82), and 4 noisy cells.
The other two vertices' 2 cells at r = 1 are the θ = 20° corner cells the gate could not pool.

## 3. Controls

**Integrity.** `pv2d_analyze.py` checked every product before reading it, and refused on any failure:
- the ratio sha256;
- the driver and helper sha256 and the helper path, against the products' own deploy;
- the full `runConfig` against the declared settings;
- on data runs, that `hTruth2D`, `hEffNum` and `hOFTruthDenom2D` each equal r per cell against the nominal to 1e-9;
- that the completeness is unchanged to 1e-9;
- on closure runs, that `hTruthRew2D / hTruth2D` = r.

Every product passed.
- Both completeness guards (numpy and product) read 0.0 on the two nominal runs, and at most 4.5e-14 on the six vertex
  runs (GENIE+MEC 2.8e-14, NuWro 4.5e-14, GiBUU 2.7e-14, the same in both arms). This is far inside the 1e-9 guard,
  so the s5p denominator defect is absent.
- The closure runs record no completeness guard: the closure ratio reweights the pseudo-data and its truth, not the
  MC or its denominator.

**NC (configuration (a)).** `data_tune_v1` against E_U on the 205 cells: max |x/x_EU − 1| = **1.376e-11**, below
the 1e-5 rule. **PASS.** The match is not bitwise. Thread-order summation in LightGBM is a likely cause, but it was
not tested. <!-- absence-ok: marks a mechanism as conjecture within this lane's own work, not a claim about others' results -->

**NC_R (refined arm).** `data_ref_tune_v1` against RE-1's D2 (`d2_data_refined.npz`, `71ca3e5f…`): max relative
difference **1.624e-12**, against the 1e-8 rule. **PASS.** The refined vertices were submitted only after this,
and NC_R itself ran only after NC passed, as the binding requires.

**PC (configuration (a), NuWro).**
- shift = x(data, NuWro-shape prior)/x(data, Tune v1) − 1;
- bias = x(closure)/x_true − 1, where the closure's pseudo-data and x_true are the MC reweighted by NuWro's shape
  relative to GENIE CV.
- On the 127 cells with |bias| > 1% (rule: at least 20):
  - corr(shift, −bias) = **0.878** (rule ≥ 0.7);
  - the slope through the origin = **1.152** (rule [0.67, 1.5]).
- **PASS**, on the primary form.
- The closure bias at NuWro has median |bias| 1.34%, p90 5.26% and max 14.0% (cell 4: p_T 0–0.07, p_∥ 3.5–4.0).

**The closure floor** (`closure_tune_v1`, pseudo-data equal to the MC, against its own truth): median 1.8e-15,
p90 2.3e-15, max 1.4e-11 (cell 187). That closure returns the truth to rounding, so it has no power. This is why the positive control uses
the NuWro closure.

## 4. Shifts, the envelope and the comparison with σ (configuration (a))

| vertex | median \|shift\| | p90 | max (cell) | signed median | integrated total's shift |
|---|---:|---:|---|---:|---:|
| GENIE+MEC | 1.26% | 3.83% | 9.82% (74: p_T 0.33–0.40, p_∥ 8–9) | −0.19% | −1.5e-6 |
| NuWro | 1.69% | 7.48% | 21.4% (3: p_T 0–0.07, p_∥ 3.0–3.5) | +0.05% | +2.2e-4 |
| GiBUU | 1.85% | 5.28% | 10.5% (148: p_T 0.85–1.0, p_∥ 3.5–4.0) | −0.10% | +1.3e-4 |
| **h** | **3.00%** | **8.30%** | **21.4%** (3) | | |

- The vertices are pure shape departures (κ preserves the prior's truth weight), and the integrated cross section
  moves by at most 0.022% (NuWro, 2.2e-4).
- h is set by NuWro in 88 cells, by GiBUU in 87 and by GENIE+MEC in 30.

**Median |shift| by tier.** The cells at r = 1 still move. Coupling between cells through the detector response is
the likely reason; it was not tested separately. <!-- absence-ok: marks a mechanism as conjecture within this lane's own work, not a claim about others' results -->

| vertex | own ratio | coarse-cell ratio | r = 1 |
|---|---:|---:|---:|
| GENIE+MEC | 1.25% | 1.14% | 3.34% (2 cells) |
| NuWro | 1.61% | 1.89% | 5.93% (2 cells) |
| GiBUU | 2.32% | 1.79% | 1.46% (60 cells) |

**h against σ.**

| reference | median σ | median h/σ | p90 h/σ | max h/σ | cells with h > σ | with h > σ/2 |
|---|---:|---:|---:|---:|---:|---:|
| adopted σ_tot, √diag(Q)/E_U | 6.45% | 0.44 | 1.24 | 2.74 | 30 (14.6%) | 84 (41.0%) |
| published per-bin, √diag(TotalCovariance)/x_paper | 6.85% | 0.45 | 1.23 | 2.58 | 28 (13.7%) | 86 (42.0%) |

Against the scalars, median h is 0.465 × 6.45% (the adopted median) and 0.437 × 6.87% (the superseded VL172 value,
secondary reference only).

**The 30 cells with h > σ_Q**, ordered by h/σ_Q (printed by `report_tables.py`). "Tier" is the dominant vertex's gate
tier in that cell. "Step beside it" is the post-hoc class of §5, in the dominant vertex's r.

| cell | p_T (GeV/c) | p_∥ (GeV/c) | h | σ_Q | σ_paper | dominant | its tier | step beside it (post hoc) |
|---:|---|---|---:|---:|---:|---|---|---|
| 109 | 0.47–0.55 | 15–20 | 12.3% | 4.5% | 5.5% | NuWro | coarse | gate |
| 108 | 0.47–0.55 | 10–15 | 12.8% | 5.1% | 5.0% | NuWro | coarse | gate |
| 107 | 0.47–0.55 | 9–10 | 16.7% | 6.7% | 8.4% | NuWro | coarse | gate |
| 3 | 0–0.07 | 3–3.5 | 21.4% | 8.9% | 8.6% | NuWro | coarse | gate |
| 110 | 0.47–0.55 | 20–40 | 12.3% | 5.3% | 5.0% | NuWro | coarse | gate |
| 148 | 0.85–1 | 3.5–4 | 10.5% | 5.3% | 4.9% | GiBUU | fine | generator |
| 2 | 0–0.07 | 2.5–3 | 10.8% | 6.6% | 8.1% | NuWro | coarse | gate |
| 90 | 0.4–0.47 | 8–9 | 10.8% | 6.6% | 8.6% | NuWro | fine | gate |
| 162 | 1–1.25 | 2.5–3 | 9.8% | 6.1% | 6.3% | GiBUU | noisy | gate |
| 91 | 0.4–0.47 | 9–10 | 10.6% | 6.6% | 8.0% | NuWro | coarse | gate |
| 17 | 0.07–0.15 | 2–2.5 | 15.5% | 9.8% | 7.4% | NuWro | fine | generator |
| 125 | 0.55–0.7 | 15–20 | 7.7% | 5.2% | 5.4% | NuWro | coarse | gate |
| 74 | 0.33–0.4 | 8–9 | 9.8% | 6.8% | 8.6% | GENIE+MEC | fine | gate |
| 126 | 0.55–0.7 | 20–40 | 8.0% | 5.7% | 4.9% | NuWro | coarse | gate |
| 93 | 0.4–0.47 | 15–20 | 6.3% | 4.5% | 5.6% | NuWro | coarse | none |
| 7 | 0–0.07 | 5–6 | 10.3% | 7.4% | 7.0% | NuWro | coarse | gate |
| 4 | 0–0.07 | 3.5–4 | 13.2% | 9.5% | 8.3% | NuWro | coarse | gate |
| 128 | 0.7–0.85 | 1.5–2 | 10.2% | 7.4% | 9.0% | NuWro | noisy | gate |
| 92 | 0.4–0.47 | 10–15 | 6.7% | 5.3% | 5.3% | NuWro | coarse | none |
| 179 | 1.25–1.5 | 3–3.5 | 9.8% | 7.7% | 7.5% | GiBUU | noisy | gate |
| 124 | 0.55–0.7 | 10–15 | 7.4% | 5.9% | 5.0% | NuWro | coarse | gate |
| 94 | 0.4–0.47 | 20–40 | 6.3% | 5.2% | 5.1% | NuWro | coarse | none |
| 118 | 0.55–0.7 | 4.5–5 | 5.9% | 4.9% | 4.7% | GiBUU | fine | gate |
| 184 | 1.25–1.5 | 6–7 | 10.1% | 8.6% | 10.0% | GiBUU | fine | generator |
| 5 | 0–0.07 | 4–4.5 | 10.5% | 9.2% | 7.9% | NuWro | coarse | none |
| 111 | 0.47–0.55 | 40–60 | 10.1% | 9.2% | 8.2% | NuWro | coarse | gate |
| 169 | 1–1.25 | 7–8 | 7.9% | 7.7% | 9.0% | GiBUU | coarse | gate |
| 166 | 1–1.25 | 4.5–5 | 6.4% | 6.3% | 6.4% | GiBUU | fine | generator |
| 129 | 0.7–0.85 | 2–2.5 | 5.9% | 5.9% | 6.1% | GiBUU | fine | none |
| 183 | 1.25–1.5 | 5–6 | 7.8% | 7.8% | 9.0% | GiBUU | fine | gate |

The dominant vertex among them is NuWro in 20, GiBUU in 9 and GENIE+MEC in 1.

**Amendment 6's caveat, measured in 2D.** On the 127 PC cells:
- |shift| ≥ |bias| holds in **61.4%**. This is the declared readout; 5D gave 52–78%;
- the median |shift + bias| / |bias| is **0.42** (post-hoc; 5D gave 0.30–0.52).

Both sit inside the 5D ranges. In 2D, as in 5D, h is evidence about model dependence at these vertices, **not a
per-cell bias bound** (`state/s5p/contract-amendment-6-review1-repairs.json`, `LOW_items.bound_wording`).

## 5. Post hoc: the tail of h sits beside steps in r

This section was not declared, and it decides nothing. This lane raised the pattern in its interim message, and the
director asked for it to be quantified descriptively from the existing products, with no new runs. The declared numbers in §0 and §4 stay the headline.

**One rule throughout** (`report_tables.classify_cell`, threshold 0.1). A cell is classified, in one vertex's r, by its
four grid neighbours whose r differs from its own by more than 0.1:
- **gate**: such a neighbour pair has a coarse-pooled or noisy (r = 1) cell on one side. The bound noise gate drew
  that boundary.
- **cut**: there is no gate pair, but some such pair has an "off" cell on the other side. That is an unreported
  cell, or GiBUU at p_∥ ≥ 10 GeV/c (KNOWN_ISSUES 82). A cut pair outranks a generator pair.
- **generator**: all such pairs are two own-ratio cells. The generator's shape drew the step.
- **none**: no neighbour differs by more than 0.1.

"Construction-drawn" means gate or cut.

**The pattern.** The largest shifts come in opposite-signed pairs across a step in r:
- NuWro cell 3 (+21.4%) and cell 4 (−13.2%) sit across the coarse boundary at p_∥ = 3.5 GeV/c, where NuWro's pooled
  r drops from 1.997 to 1.406.
- Cells 107–111 (+10 to +17%) and 124–126 (−7 to −8%) sit across the coarse boundary at p_T = 0.55 GeV/c, where r
  steps from 1.245 to 0.978.
- Cell 90 (−10.8%, its own ratio 0.958) and cell 91 (+10.6%, the coarse 1.245) sit across a tier boundary at
  p_∥ = 9 GeV/c.

**The count.** Of the 30 cells with h > σ_Q, classified in their dominant vertex's r:
- 21 gate;
- 0 cut;
- 4 generator;
- 5 none.

**Base rates and correlations:**
- Over all 205 cells, a step above 0.1 sits beside 2% of cells for GENIE+MEC, 28% for NuWro and 17% for GiBUU.
  A construction-drawn step sits beside 1%, 17% and 9%.
- Per vertex, |shift| correlates more with the largest local step in r than with |r − 1|:
  - GENIE+MEC 0.51 against 0.37;
  - NuWro 0.62 against 0.53;
  - GiBUU 0.46 against 0.19.

**h with and without the construction-step cells.** Per vertex, a cell is excluded if it is construction-drawn in that
vertex's r. For h, it is excluded if it is construction-drawn in any vertex's r. In brackets is the number excluded by
a cut step alone. That is one NuWro cell (145), beside two unreported cells, and it is not an h > σ_Q cell.

**Configuration (a): all 205 cells, and POST HOC without the cells beside a construction-drawn step > 0.1**

| | all cells: median / p90 / max | cells excluded (of them, by a cut alone) | post hoc, rest: median / p90 / max |
|---|---|---:|---|
| GENIE+MEC | 1.26% / 3.83% / 9.82% | 2 (0) | 1.25% / 3.78% / 7.33% |
| NuWro | 1.69% / 7.48% / 21.38% | 34 (1) | 1.42% / 4.97% / 15.51% |
| GiBUU | 1.85% / 5.28% / 10.48% | 19 (0) | 1.72% / 4.43% / 10.48% |
| envelope h | 3.00% / 8.30% / 21.38% | 52 (1) | 2.59% / 6.29% / 15.51% |

h > σ_Q: 30 of 205 on all cells; post hoc, 9 of 153 on the cells not beside a construction-drawn step (for h, a cell is excluded if it is beside one in any vertex).

**Refined arm: all 205 cells, and POST HOC without the cells beside a construction-drawn step > 0.1**

| | all cells: median / p90 / max | cells excluded (of them, by a cut alone) | post hoc, rest: median / p90 / max |
|---|---|---:|---|
| GENIE+MEC | 0.94% / 3.57% / 9.77% | 2 (0) | 0.93% / 3.55% / 6.26% |
| NuWro | 1.62% / 7.10% / 21.01% | 34 (1) | 1.25% / 3.91% / 14.32% |
| GiBUU | 1.78% / 5.13% / 10.81% | 19 (0) | 1.55% / 4.78% / 9.87% |
| envelope h | 3.13% / 7.55% / 21.01% | 52 (1) | 2.61% / 5.44% / 14.32% |

h > σ_Q: 26 of 205 on all cells; post hoc, 6 of 153 on the cells not beside a construction-drawn step (for h, a cell is excluded if it is beside one in any vertex).

**The positive control on the same two subsets** (configuration (a), the 127 PC cells):

| PC cells | n | corr(shift, −bias) | slope | \|shift\| ≥ \|bias\| |
|---|---:|---:|---:|---:|
| all (the declared PC) | 127 | 0.878 | 1.152 | 61% |
| beside a construction step in NuWro's r | 32 | 0.951 | 1.204 | 81% |
| not beside one in NuWro's r | 95 | 0.698 | 1.002 | 55% |
| beside one in any vertex's r | 45 | 0.946 | 1.188 | 73% |
| not beside one in any vertex's r | 82 | 0.652 | 1.003 | 55% |

**What this shows, and what it does not:**
- The tail of h (p90 and max) co-locates with the boundaries of the bound gate's piecewise-constant reweight. Without
  those cells, p90 falls from 8.30% to 6.29%, and the share of cells with h > σ_Q from 14.6% (30 of 205) to 5.9%
  (9 of 153). The median moves less, from
  3.00% to 2.59%.
- The shifts at those boundaries are this estimator's response to this declared prior, and the PC tracks them closely
  (corr 0.95 on the 45 PC cells beside a construction step).
- The PC's strength is concentrated there. On the 82 PC cells not beside one:
  - the correlation is 0.652 and the slope 1.00. The correlation is below the declared 0.7 bar, had that rule been
    applied to this subset; it was not, and the declared PC PASS stands;
  - |shift| ≥ |bias| holds in 55% of these cells, against 61% overall.
  - So the reduced h above is less well covered by the positive control than the declared h is, and it is not a
    replacement readout.
- Nothing here shows that the gate's boundaries *cause* the tail. A smoothed reweight (for example ρ interpolated
  across the coarse boundaries) would test that. It would need a new declaration and binding, and it is not run here.
  <!-- absence-ok: scope of this lane's own runs -->

## 6. The refined arm (binding option (a))

The refined arm uses RE-2's estimator: configuration (a) with `--bkg-mode negweight-refined` and the 400/31
refinement classifier, `random_state` 45. It is unfolded on the same three reweights. Its zero is `data_ref_tune_v1`,
which reproduces D2 to 1.6e-12 (§3). Its σ comparisons use the same adopted σ_Q (√diag(Q)/E_U) and the same published
σ, because no refined covariance is adopted.

| vertex | median \|shift\| | p90 | max (cell) | signed median | integrated total's shift |
|---|---:|---:|---|---:|---:|
| GENIE+MEC | 0.94% | 3.57% | 9.77% (74) | −0.14% | +1.3e-4 |
| NuWro | 1.62% | 7.10% | 21.0% (3) | −0.02% | +1.7e-4 |
| GiBUU | 1.78% | 5.13% | 10.8% (162: p_T 1.0–1.25, p_∥ 2.5–3.0) | −0.26% | +1.9e-4 |
| **h** | **3.13%** | **7.55%** | **21.0%** (3) | | |

- **Against σ.**

  | reference | median h/σ | p90 h/σ | max h/σ | cells with h > σ | with h > σ/2 |
  |---|---:|---:|---:|---:|---:|
  | adopted σ_tot (Q) | 0.43 | 1.12 | 2.67 | 26 (12.7%) | 85 (41.5%) |
  | published per-bin | 0.42 | 1.11 | 2.49 | 23 (11.2%) | 80 (39.0%) |

  Against the scalars, median h is 0.485 × 6.45% and 0.456 × 6.87%.
- **Who sets h.** NuWro sets h in 79 cells, GiBUU in 92 and GENIE+MEC in 34.
- **The two arms side by side** (per-cell Δshift = refined − (a)):

  | vertex | (a) median / p90 / max | refined median / p90 / max | median \|Δshift\| | max \|Δshift\| |
  |---|---|---|---:|---:|
  | GENIE+MEC | 1.26% / 3.83% / 9.82% | 0.94% / 3.57% / 9.77% | 0.37% | 5.60% |
  | NuWro | 1.69% / 7.48% / 21.38% | 1.62% / 7.10% / 21.01% | 0.43% | 3.92% |
  | GiBUU | 1.85% / 5.28% / 10.48% | 1.78% / 5.13% / 10.81% | 0.35% | 3.24% |
  | envelope h (Δh) | 3.00% / 8.30% / 21.38% | 3.13% / 7.55% / 21.01% | 0.43% | 3.92% |

  σ_Q: median h/σ (a) 0.439, refined 0.426; h > σ in 14.6% vs 12.7% of cells; h > σ/2 in 41.0% vs 41.5%.

  σ_paper: median h/σ (a) 0.453, refined 0.421; h > σ in 13.7% vs 11.2% of cells; h > σ/2 in 42.0% vs 39.0%.

- **Reading.**
  - The refined arm's response to the prior is the same in pattern and close in size to configuration (a)'s.
  - h peaks at cell 3 in both arms (21.0% against 21.4%).
  - Excluding the same 52 construction-step cells (post hoc) reduces the tail in both: h > σ_Q falls from 26 to 6
    here (12.7% → 3.9%), and from 30 to 9 in (a) (14.6% → 5.9%) (§5).
  - Its own PC was not run, as declared. The (a) positive control shows that this design sees a bias. That the
    refined estimator responds the same way is an inference from these per-cell agreements, not a separate
    control. <!-- absence-ok: scope of this lane's positive control, per DECLARATION §5 and BINDING -->

## 7. Compute

| arm | jobs | charged CPU node-h |
|---|---:|---:|
| configuration (a): pilot, 3 vertices, 2 closures | 6 | 4.2617 |
| refined: pilot, 3 vertices | 4 | 3.1439 |
| **total** | **10** | **7.4056** |

- **Projections and limits.**
  - The pilot was projected at 60 min (limit 1:15) and ran 44.3 min.
  - The arm (a) vertex runs were projected at the pilot's 44.3 min (limit 0:56) and ran 45.9–47.7 min.
  - The closures were projected at 1.6 × 44.3 = 70.9 min (limit 1:29) and ran 31.8 and 39.2 min.
  - The refined pilot was submitted with a 1:03 limit. Its projection was not written into a record before
    submission. By this session's account, the limit was set as 1.25 × about 50 min: the arm (a) pilot plus an
    allowance for the 400-tree refinement classifier. The ledger's 50.4 min is reconstructed as limit/1.25 and is
    marked so. It ran 48.4 min.
  - The refined vertices were projected at the refined pilot's 48.4 min (limit 1:01). They ran 45.1–47.7 min.
- **Total.** The charged total is 7.41 of the 17 cap. Charge is elapsed × billing/256; every job billed 256, one
  exclusive CPU node. Every job was submitted with `--qos=regular` on m3246; sacct records it as `regular_1`.
- **Storage.** All products, logs and inventories are under `/pscratch/sd/j/josephrb/pv2d-20261023/`. Every job's
  output paths (`--out`, logs, `TMPDIR`) point there. That nothing was written to CFS is inferred from those
  paths, not measured.
- **Records.** Per-job rows are in [`LEDGER.tsv`](LEDGER.tsv). Product paths and sha256 are in
  [`receipts/products.tsv`](receipts/products.tsv).

## 8. Reproduction

The readouts are committed beside the tool, in `2d-unfolding/pv2d/readouts/`:

| file | sha256 |
|---|---|
| `nc_a.json` (NC, configuration (a)) | `07d841e0421c2cb4…` |
| `readout_a.json` (configuration (a): NC, PC, shifts, h, σ comparisons) | `6a0e75f1897b9003…` |
| `nc_ref.json` (NC_R) | `8f0e9aeb9d694c24…` |
| `readout_ref.json` (refined arm: NC_R, shifts, h, σ comparisons) | `d220abaac4c651f6…` |

Each was produced on a Perlmutter login node, in the deploy's `setup_salloc_env.sh` environment, with:

```
python3 $D/nd-unfolding/mnv_guarded_run.py --expect-root $D [--allow $B/deploy/repo] --label pv2d:<x> -- \
    $D/2d-unfolding/pv2d/pv2d_analyze.py --arm {a|refined} [--nc-only] \
    --products $B/{run|run-ref}/products --products-deploy $B/deploy/{repo|repo-ref} --out $B/readouts/<x>.json
```

- `B=/pscratch/sd/j/josephrb/pv2d-20261023` and `D=$B/deploy/repo-ref`.
- The readout records every input's sha256 (E_U, Q, the paper covariance, the flux file, D2), the omnifile's size
  and mtime, and the products-deploy HEAD.

**`report_tables.py`** prints the following (lightly edited for layout; the values are unchanged):
- the tier tables (§2, §4);
- the amendment-6 measures (§4);
- the 30-cell table (§4);
- all of §5's tables and counts (the r values in its "pattern" bullets were read from the ratio files directly);
- the arm comparison (§6).

The command is `python3 2d-unfolding/pv2d/report_tables.py --projections 2d-unfolding/pv2d/ratios/projections.json
--readout-a 2d-unfolding/pv2d/readouts/readout_a.json --readout-ref 2d-unfolding/pv2d/readouts/readout_ref.json`.
- It reads only committed files.
- It refuses unless every ratio file's sha256 equals `projections.json`'s, `projections.json` equals the readouts'
  `ratios_projection_sha256`, and the arms are "a" and "refined".
- The per-vertex shift tables and the h-against-σ tables in §4 and §6 are the readouts' own summary fields.
- `test_pv2d.ReportTablesOnCommittedReadouts` pins, against the committed files:
  - the exclusion counts (2 / 34 / 19 / 52) and the cut-only 1;
  - h > σ_Q both ways (30 / 9, 26 / 6);
  - the 21 / 0 / 4 / 5 classes;
  - the PC subset n and correlations.

## 9. Deviations, not done and limitations

**Deviations from the bound declaration** (none changes a number):
1. **The readout's declared `flux_universe_file`.**
   - The first readout of the pilot refused it: the check declared the value None, but the producer records its
     default path `baseline_flux/flux_integral_universes_MEFHC.root`, which E_U also used.
   - The check was corrected at `f7768a7f`. The run was right and the check was wrong.
   - By this session's own account, no NC value had been read before the correction. The refused readout wrote no
     output file.
2. **`--products-deploy`.**
   - The readout runs from the refined deploy (`d67a5514`), but arm (a)'s products were made by the `3631ea3f`
     deploy.
   - The readout now takes the expected driver and helper sha256 and the helper path from the products' own deploy,
     and records that deploy's HEAD. That is `3631ea3f` in `readout_a.json` and `d67a5514` in `readout_ref.json`.
   - The change was committed at `d67a5514`, before any readout used it.
   - The check is unchanged in strength. It compares against the deploy that made the products, and it refuses a
     dirty one.
3. **The refined arm's code** (`870b2813`) was added after the binding, under option (a), before any refined job:
   - `--pv2d-refine-400-31` in the lane's own driver copy;
   - task mode `prior_ref`;
   - `--arm refined` in the readout.

   The refined driver's sha256 is `be016f87546a11be…`.
4. **The refined pilot's projection** was not recorded before submission (§7). The job ran inside it.
5. **`report_tables.py` and §5 are post hoc.** This lane raised §5's pattern in its interim message, and the director asked for it to be quantified. Nothing
   in it changes a declared readout or verdict.

**Deviations from the assignment, accepted by the binding** (`BINDING.md` §1–2):
- **The vertex convention.** The Tune v1 prior is reweighted by each generator's shape relative to GENIE CV, not
  reweighted to the generator itself.
- **The noise gate and coarse pooling.** A cell keeps its own ratio at ≤ 5% statistical error; otherwise it takes the
  pooled s5p coarse-cell ratio; otherwise r = 1.
- **GiBUU is used on p_∥ < 10 GeV/c only.** At p_∥ ≥ 10 GeV/c its r = 1 (KNOWN_ISSUES 82).

**Not done.**
- **The ρ² fallback.** It was not needed.
- **No noise-only run.** The fine cells' residual generator noise (median 1.9–3.4% per cell, ≤ 5% by construction)
  enters each shift, and it is not separated from it. As declared (§10): the OmniFold response to high-frequency
  structure in the prior is largest where resolution is poorest, so h may include a noise term of up to about that
  size in those cells. <!-- absence-ok: scope of this lane's own runs -->
- **The positive control is at NuWro only.** It was not run on the refined arm, as declared. That arm has no PC of its
  own, and its h carries the label "refined arm: no positive control of its own (the PC ran on configuration (a))".
  <!-- absence-ok: scope of this lane's positive control, per DECLARATION §5 and BINDING -->
- **The 2D-versus-5D comparison** is the director's.

**Limitations.**
- One seed (42) and one learner per arm, so there is no coverage statement.
- h is a sensitivity over three vertices, not a hull bound and not a covariance.
- The omnifile is identified by size and mtime, not hashed (as declared).
- The ratio errors assume independent samples. That is conservative if GENIE+MEC shares events with GENIE CV (as
  declared, §9).
- KNOWN_ISSUES 82: GiBUU has no E_ν > 20 GeV, so GiBUU is used only on p_∥ < 10 GeV/c.
- KNOWN_ISSUES 83: the flux repairs are reweights, not regenerations, with no E_ν > 100 GeV.
  - For GENIE+MEC and NuWro, the GENIE-CV reference cancels the defect to first order.
  - For GiBUU it does not cancel, because GiBUU reads its own flux. The GiBUU ratio therefore carries whatever
    remains in the repaired GENIE CV reference: the absent E_ν > 100 GeV, and the reweight-not-regeneration caveat.
    The flux repair is the main mitigation, and the p_∥ < 10 GeV/c restriction limits the region further.
    (KNOWN_ISSUES 83's "contaminated" refers to the earlier GiBUU/GENIE departure built on the unrepaired GENIE.)
- The tail of h co-locates with the gate's boundaries, and the PC is weaker away from them (§5).

## 10. Review

An independent read-only reviewer (a fresh subagent) was given this report as its subject, plus the records, code
and committed readouts. It reviewed `b6f63dc7` in both directions and recomputed independently. A confirmation pass
on `4785902f` found every fix adequate. It raised 3 new minor items and 7 nits (wording, attribution, test gaps),
which are addressed in the following commit.
- It recomputed every number it could from the committed JSON with its own code. Everything matched: digests,
  controls, tiers, both arms' shift and σ tables, the 30-cell table, the §5 diagnostics, the director's exclusion
  counts, the arm comparison and the ledger arithmetic.
- It found no blocker, 4 major findings, 12 minor and 6 nits. All are addressed in this revision:
  - **Major.**
    - The completeness-guard values were misquoted (now quoted per run, §3).
    - Causal wording in the post-hoc section is now descriptive: "co-locates".
    - The PC was not reported on the post-hoc subsets, which shows it weaker away from the steps (§0, §5).
    - An unsupported claim that the median is "less exposed", based on tier medians (replaced by the exclusion
      figures).
  - **Minor.**
    - The closure floor's p90 is added.
    - The assignment-level deviations are listed (§9).
    - Two declared limitations are restored: the noise term and the ratio-error independence.
    - KNOWN_ISSUES 83's cancellation is scoped to GENIE+MEC and NuWro.
    - The closure's description now follows the binding's convention.
    - §5 uses one rule throughout, with gate and cut steps separated. Of the 30 h > σ_Q cells, the earlier 19/6/5
      by largest step became 21/0/4/5.
    - The reproduction text says which tables `report_tables.py` prints.
    - The ledger marks the refined pilot's projection as reconstructed.
    - Deviation 2 names which HEAD each readout records.
    - The tests now cover the union rule, the tier mapping and every pair class, plus a pinned regression on the
      committed readouts (39 tests after the confirmation pass).
  - **Nits.**
    - The subtotal rounding is fixed.
    - The integrated-shift maximum is now 0.022%.
    - The QOS name is given as recorded (`regular_1`).
    - Two unmeasured mechanisms are marked as conjecture. <!-- absence-ok: marks a mechanism as conjecture within this lane's own work, not a claim about others' results -->
    - "The same unfolds" is scoped to the four data unfolds.
    - `report_tables.py` now checks its inputs.
- **Unverifiable from the repository**, as it noted:
  - the launcher's clean-clone checks;
  - the module inventories (re-measured from the pscratch logs for this revision, §1);
  - the order of submission (consistent with the ledger's start times);
  - that no NC value was read before deviation 1's correction;
  - that the committed `nc_a.json` is the artifact that gated the vertex jobs. It has no timestamp, and it was
    written by the readout code at `7e15ad4a`;
  - the refined deploy's state at the moment of submission (the readout records it at readout time; the products'
    driver `be016f87` is unchanged between `870b2813` and `d67a5514`);
  - that nothing went to CFS (inferred from the output paths, §7).
