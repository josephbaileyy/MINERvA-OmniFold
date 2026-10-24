# H2 definition, addendum: GiBUU's p_∥ domain for C_model,5D (2026-10-24, session "2d test")

**Status: for the director's review.**
- It addends `H2-DEFINITION-DECLARATION.md`, which is left unchanged; `DECISION-20261024-joseph-h2-16-cell-definition.md`
  cites that file's sha256.
- It answers that decision's open item "GiBUU's domain".
- Nothing is built. No (e) data product and no unfold product was opened.

**Recommendation: (i), keep 10 GeV/c.** Add a label for the 6–10 GeV/c deficit and for the difference from the paper's
6. Either way, the cell definition does not change (§4).

## 1. Where 6 and 10 come from

| value | first record | what the record says |
|---|---|---|
| **6 GeV/c** | s5p contract amendment 7, frozen 2026-09-28 (`state/s5p/contract-amendment-7-production-admission.json`, `family`) | The joint test's GiBUU domain is "the 72 of them [the 109 J cells] with p_parallel < 6 GeV/c (pz index <= 1)". The paper carries it as "whose sample lacks high-energy neutrinos" (`paper_body.tex:245-246`; `values_inference.tex:15`). |
| **10 GeV/c** | the PV-2D declaration, 2026-10-23 (`state/2d-closeout/stageF/methods/pv2d/DECLARATION.md:83-85`; `2d-unfolding/pv2d/config.json`, `pz_max`) | "GiBUU is defined on p_∥ < 10 GeV/c only (KNOWN_ISSUES 82)… above about 10 GeV/c its deficit is that cut". This rests on the flux-fix record, `state/s5p/gen5d/README-gen5d-fluxfix.md`: "Above about 10 GeV/c the deficit is the 20 GeV cut". The ladder copied it (`nd-unfolding/pv-ladder/config.json`, `pz_max` 10). |

**Why the 6 is an edge, not a measured bound.** Amendment 7 states the cut as a J index: J's p_∥ edges are 1.5, 3.5,
6 and 60. That J grid has no edge between 6 and 60, so its top p_∥ cell contains GiBUU's empty region above 20 GeV/c.
6 is therefore the last J edge that excludes it. This is an *inference* from the edges; the amendment gives no other
reason.

**GiBUU's E_ν coverage against the analysis flux.**
- **The cut:** GiBUU 2019's sample stops at E_ν = 20 GeV (`KNOWN_ISSUES` 82).
- **What is measured:** for two generators that cover E_ν to 50 GeV, the share of the flux-averaged in-phase-space CC
  cross section that comes from E_ν > 20 GeV, per p_∥ range. That share is what GiBUU cannot contain there.
- **How:** with the flux repair's own events and per-event weights (`gen5d_flux_reweight.py`, `KNOWN_ISSUES` 83), and
  the analysis rectangle with θ_μ < 20°.
- **Tool and output:** `nd-unfolding/pv-ladder/gibuu_enu_coverage.py` (sha256 `d9be5cf0…7a54`). It ran once on login
  node `saul` in 18 s, at 0 node-h. Its output is `readouts/gibuu_enu_coverage.json` (sha256 `9ee26883…813c`).

| p_∥ (GeV/c) | share of in-PS σ (GENIE CV) | E_ν > 20 GeV, GENIE CV | E_ν > 20 GeV, NuWro |
|---|---:|---:|---:|
| 1.5–4.5 | 48.9 % | 0.83 % | 0.77 % |
| 4.5–6 | 24.1 % | 1.28 % | 1.49 % |
| **6–10** | 19.1 % | **4.88 %** | **5.26 %** |
| 10–20 | 5.8 % | 43.3 % | 44.3 % |
| 20–60 | 2.3 % | 100 % | 100 % |

- **Control:** the combined p_∥ < 6 share is 0.98 % (GENIE) and 1.01 % (NuWro). That reproduces `KNOWN_ISSUES` 82's
  recorded "0.92–1.05 % of the p_∥ < 6 GeV/c part in the other generators".
- **So GiBUU's sample holds about 95 % of the cross section at 6–10 GeV/c,** against about 99 % below 6 and 56 % at
  10–20. The coverage falls off at 10, not at 6.

## 2. The 6–10 GeV/c slice on the 16 cells

**Tool and output.** `nd-unfolding/pv-ladder/gibuu_domain_cells.py` (sha256 `e883ad74…4fbc`) computes this from L-5D-PV's
frozen GiBUU reweight. Its output is `readouts/gibuu_domain_cells.json` (sha256 `855eeff6…60d0`).

**The slice and its tiers.** The slice is the fine cells whose upper p_∥ edge is in (6, 10]. It holds 19.4 % of the
prior's truth weight, all of it in the eight high-p_∥ cells. The tiers are those of GiBUU's noise gate.

| cell | slice share of the cell's prior | in the slice: own ratio / J-coarse pooled / r = 1 |
|---|---:|---|
| R04 | 46 % | 1 / 35 / 10 % |
| R05 | 28 % | 0 / 12 / 16 % |
| R06 | 36 % | 0 / 36 / 0 % |
| R07 | 32 % | 0 / 24 / 8 % |
| R12 | 43 % | 0 / 4 / 38 % |
| R13 | 30 % | 0 / 20 / 10 % |
| R14 | 29 % | 0 / 26 / 3 % |
| R15 | 36 % | 6 / 16 / 14 % |

The other eight cells (R00–R03, R08–R11) have no prior weight in the slice. Almost all GiBUU's reweighted weight in the
slice is J-coarse pooled. The J cell (p_∥ 6–60) pools only over its 6–10 part, because the rest is off.

## 3. The choice

**What the slice does to GiBUU's ratio.** The prior-weighted GiBUU/GENIE-CV ratio ρ on assigned cells is 0.832 below
6 GeV/c and 0.813 in the slice.
- **The flux artifact:** the E_ν > 20 GeV deficit is about 4 percentage points worse in the slice than below 6 (§1).
  That artifact enters ρ at that size.
- **Its effect on a cell's truth-level departure:** at most about 0.04 × 46 % ≈ 2 percentage points, in R04. This is an
  *estimate*.

**Option (ii), r = 1 at p_∥ ≥ 6, computed exactly from the frozen ratio file.**
- **Why exact:** the gate pools within J-coarse cells, and J has an edge at 6. So every ρ and label below 6 is what
  `pvl_ratios.py` would give with `pz_max = 6`. `pvl_lib.normalize` then resets k from 1.2059 to 1.2012.
- **Check:** the same call on the frozen labels reproduces the frozen GiBUU r to 1e-12; the script refuses otherwise.

GiBUU's truth-level departure d = Σ p r / Σ p − 1:

| cell | (i) p_∥ < 10 | (ii) p_∥ < 6 | change |
|---|---:|---:|---:|
| R04 | +11.5 % | +6.1 % | −5.3 pp |
| R05 | −7.7 % | −5.4 % | +2.3 pp |
| R06 | −32.9 % | −21.2 % | +11.8 pp |
| R07 | −23.6 % | −16.3 % | +7.4 pp |
| R12 | +2.9 % | +3.9 % | +1.0 pp |
| R13 | +10.8 % | +7.2 % | −3.6 pp |
| R14 | −2.8 % | +0.7 % | +3.5 pp |
| R15 | −15.1 % | −9.3 % | +5.9 pp |
| the other eight | | | −0.2 to −0.4 pp (through k only) |

**Recommendation: (i), keep 10. The reasons:**
1. **(ii) mostly removes GiBUU's model, not the artifact.** Its changes reach 11.8 pp, against an artifact of about
   2 pp at most. On 19.4 % of the prior it would replace GiBUU's shape with Tune v1's.
2. **10 is where the coverage fails, and 6 is a J-grid edge.** The coverage falls from about 95 % to 56 % across 10. The
   6 bounds the joint tests' cells, for a test of GiBUU's absolute prediction. Here the reweight uses GiBUU's shape
   relative to GENIE CV, renormalized over the assigned cells.
3. **(ii) changes a bound vertex and costs compute.**
   - It needs a new frozen reweight under the ladder's prep: `pvl_ratios.py --rung L-5D-PV` with GiBUU's `pz_max` set
     to 6, a new `prep-SHA256SUMS` entry and a new run pin. That costs CPU minutes. Its output must equal the r_ii
     above, which is a control.
   - It needs a new data unfold, `L-5D-PV_e_gibuu`, because the shift comes from the unfold. That is about one J5 step,
     an *estimate* of ≤ 0.25 CPU node-h from J5's 0.2253 for 5 steps run together on one node.
   - It also needs an amendment to the bound ladder declaration.
   - The NC and the NuWro PC are unaffected.

**The labels to carry with (i):**
- "GiBUU's shape is applied on p_∥ < 10 GeV/c. Above that the prior is unchanged."
- "At 6 ≤ p_∥ < 10 GeV/c GiBUU's sample lacks the E_ν > 20 GeV part, 4.9–5.3 % of the cross section there."
- "The paper's joint tests use the narrower p_∥ < 6 GeV/c."

**The paper's sentence** (`paper_body.tex:245-246`) needs no change for the joint tests. Where the paper describes
C_model,5D, it should state its GiBUU domain.

**If (ii) is chosen,** it changes the GiBUU vertex. The director takes that to Joseph.

## 4. The cell definition does not change either way

- **The rule did not involve GiBUU.** The merge rule (`h2_definition.py`, declaration §1) used the Tune v1 analysis
  MC's purity and support only, and read no generator prediction.
- **What (ii) would change:** only GiBUU's r, hence s_GiBUU. R00–R15, their order and the fine map stay as Joseph
  approved them: definition sha256 `b6790761…da89`, fine map sha256 `930326a3…e18c`.

**MEASURES:** generator E_ν coverage by p_∥; the slice's share and gate tiers on the 16 cells; GiBUU's truth-level
departure under (i) and (ii). **CANNOT AUTHORIZE:** GiBUU's domain, the vertex, or any claim.
