# Flux: our runtime flux against Valencia 2019, and what its high-energy tail explains (2026-11-24)

**By** the `ibu-chi-squared-issue` session (Claude Opus 5.5). It is part of the chain in [`../README.md`](../README.md).
Joseph asked for it after the variant test ([`../variants/`](../variants/README.md)). It runs locally, apart from two
read-only cluster steps (in Custody), with 0 node-h.

**Result (declared, [`fluxrw/`](fluxrw/)): FLUX-MAJOR at truth p‖ 40–60.** Reweighting our MC truth by the ratio of
Valencia 2019's constrained flux to MAT's runtime constrained flux, in true E_ν, closes 84 % of the shape gap between
shipped Tune v1 and our truth at p‖ 40–60, and 93 % at 20–40. It does not move the lowest pT row. It barely moves the
reco fold residual or the IBU distance. So the high-energy flux tail explains most of the *truth-level* difference from
the shipped model, but not the *reco-level* 40–60 excess.

## Background

The 2021 paper cites Valencia et al. 2019 (arXiv 1906.00111) for its ν-e flux constraint. The installed MAT, with
`SetNuEConstraint(true)` on ME playlists, loads `sorted_NuEConstraint_FHC_RHC_IMD.txt`, a combined FHC + RHC ν-e + IMD
constraint (`MINERvA101/MAT/PlotUtils/FluxReweighter.cxx:504-506`). The FHC-only `nu+e_ME_spectrum.txt` branch is
commented out, and the file is not installed.

## 1. First comparison: wrong histogram, not read ([`first/`](first/))

[`first/DECLARATION.txt`](first/DECLARATION.txt) (sha256 `e595f5c06b1f57e5e90b1511ff53f04d655b02f2b5c10208f6e091788a2b1327`) compared Valencia's table with a flux I rebuilt as the
constraint-weighted mean of Flux universes 0–99 of `flux-g4numiv6-pdg14-minervame{1D,1M,1N}_rearrangedUniverses.root`.
**That reconstruction is wrong**, so its numbers ([`first/score.out`](first/score.out)) are not a result:
- that file's `flux_E_unweighted` is MAT's *generation* flux, the denominator of the event weight;
- the reweighting flux comes from another file, and MAT constrains all 1000 universes before truncating to 100
  (`FluxReweighter.cxx:395-422`).

The error shows in the numbers: the first comparison's total is 1.185 × Valencia, and the archived record gives
unweighted/runtime = 1.19 (`../../s5p/gen5d/gen5d-fluxfix.json`). Codex-personal pointed out the error; I checked it
against the installed MAT source before accepting it.

The declared 2σ condition can't be evaluated either way. In the Valencia ancillary covariance, sqrt(diag) is 9–15 times
the flux values in the table, so the two are not in the same units.

## 2. The right comparison

`../../s5p/gen5d/gen5d-fluxfix.json` already records MAT's runtime flux. It is the POT-weighted `GetFluxReweighted(14)`
over the 12 ME FHC playlists, with the constraint on and 100 universes. Against Valencia's
`MINERvA_Flux_pdg14_500MeVBins.csv` (input sha256 values in [`inputs.sha256`](inputs.sha256)):

| E_ν (GeV) | MAT / Valencia |
|---|---|
| 0–100, absolute | 0.9959 |
| 10–20, shape (normalized over 2–20) | 0.996 |
| 20–30 | 0.956 |
| 30–50 | 0.888 |
| 50–100 | 0.887 |

## 3. Flux-reweight test ([`fluxrw/`](fluxrw/))

[`fluxrw/DECLARATION.txt`](fluxrw/DECLARATION.txt) (sha256 `9534a89cf7a826b55ef474f18b7cb4b5d9f097a62efea1dc5f03be22b16578cc`, hashed before computing). Script
[`fluxrw/fluxrw.py`](fluxrw/fluxrw.py), output [`fluxrw/run.log`](fluxrw/run.log). The test weights our truth and
response from [`../wstest/wsplit_a1.npz`](../wstest/) by r(E_ν) = Valencia/MAT, per E_ν bin. r is 1.00 to 1.02 below
20 GeV, 1.050 at 20–30, 1.129 at 30–50 and 1.130 above 50. Controls pass: C-CV ≤ 6e-14 and C-PHI.

| | before | after | κ (fraction closed) | reading |
|---|---|---|---|---|
| shipped/ours shape, truth p‖ 40–60 | +14.7 % | +2.4 % | 0.84 | **FLUX-MAJOR** |
| same, truth p‖ 20–40 | +10.2 % | +0.7 % | 0.93 | (descriptive) |
| same, truth pT 0–0.07 | +7.2 % | +7.8 % | −0.08 | **FLUX-MINOR** |
| reco fold residual S_COL | +0.100 | +0.095 | | descriptive |
| reco fold residual S_ROW | −0.064 | −0.065 | | descriptive |
| K=10 IBU distance to published | 0.961 | 0.955 | | descriptive |

**Limits.**
- r is set per gen5d band (0.5–2, 2–5, 5–10, 10–15, 15–20, 20–30, 30–50, 50–100 GeV), not per 0.5 GeV bin.
- Above 100 GeV, r takes the 50–100 value, because Valencia stops at 100 GeV.
- The reweight does not touch the background.
- It assumes the 2021 MC used Valencia 2019's flux, as the paper's citation suggests. The release does not show that
  directly.

**What it changes in the chain.**
- **Truth level.** The variant test's UPSTREAM reading now has a specific, quantified candidate: a flux tail above
  20 GeV that is 4–11 % lower in our MAT than in Valencia's release. This supports the analysis note's standing
  "FHC-only constraint file" hypothesis, at the level of the flux shape. It does not test which constraint file MINERvA
  used.
- **Reco level.** The 40–60 reco excess and the low-pT deficit remain open. Fixing the flux tail moves S_COL by only 5 %
  of its size, in line with the weight test's finding that truth-level fixes barely move the reco residual.

## Custody

Two read-only cluster steps on 2026-11-24, both 0 node-h, with nothing written on the cluster:
- `cat` of the three `MINERvA101/opt/lib/data/flux` pdg14 `_rearrangedUniverses` files and the constraint file. Their
  sha256 values match the repo's pins (`inputs.sha256`; `2d-unfolding/cov2d/cov2d.py` for the constraint).
- One Python dump with MAT loaded, on login02 in `/dev/shm`, with output to stdout only
  ([`first/dump_flux.py`](first/dump_flux.py)).

No protected root was opened. The arXiv files and `flux_dump.json` (9 MB) are not committed; their sha256 values are.
