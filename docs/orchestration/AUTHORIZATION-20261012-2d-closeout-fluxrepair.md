# AUTHORIZATION 2026-10-12 — 2D closeout: build the C04+X01-repaired 2D covariance (no re-unfold)

**Issued by** the paper-tighten lane under
[`AUTHORIZATION-20261012-2d-closeout-delegation.md`](AUTHORIZATION-20261012-2d-closeout-delegation.md) §3, on
Joseph's decision recorded in §1.

**CITABLE FOR:** building, recording and independently verifying a repaired version of the *adopted* 2D
covariance construction with two defects fixed (`KNOWN_ISSUES.md` 95 and 96, Stage B
`state/2d-closeout/stageB/`):
- **C04.** The Flux band is computed with MAT's per-universe ν-e+IMD constraint weights, i.e. a weighted
  `CalcCovMx` over the existing 100 flux-fixed universe outputs.
- **X01.** The two `Muon_Energy_MINOS` universes are divided by their own flux, `Φ_MINOS,u`, not by `Φ_CV`.
  This is an exact rescale of the existing outputs by `Φ_CV/Φ_MINOS,u`.

**NOT CITABLE FOR:**
- adoption of the product (§3);
- any other change to the construction: the July sweep, laterals, the Rvx1pi deduplication, the
  statistical ensemble, C_ML, G1 or G2;
- any re-unfold;
- coverage or a KI-85 lift;
- a publication change.

## 1. Joseph's decision, verbatim

The paper-tighten session asked: "The flux band in the quoted 2D uncertainty omits MAT's ν-e/IMD constraint
weights (confirmed independently). Repaired, the total median drops from 6.87% to about 6.09%, below the
published 6.85%. The repair needs no re-unfold. What should happen with the paper and note?" Option 1 read:

> I issue a small grant. The closer builds the repaired covariance (weighted CalcCovMx on the existing 100
> universe outputs, plus the MINOS-denominator fix) as a committed product with receipts and an
> independent check. You then adopt it and I re-quote 6.09% everywhere. Rest of Stage C continues later.

Joseph chose it on 2026-10-12. The answer text is `Build repair now (Recommended)`; SHA-256 with a final
newline is `b6b33d0ab5916a0debcfea424c4cc6a32e6e45e9d5ea7c6d706ca26acf2320f7`.

## 2. Bounds

| item | value |
|---|---|
| executor | 2D closeout executor (2d closer) |
| inputs | the adopted products only: the flux-fixed universe outputs and rollup (VL172, `uq/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170/`), the VL170 bootstrap, the ML block, `E_U` (`4f5a1b6d…`) as the central value, and MAT `35097b65`'s constraint weights; every input re-hashed |
| method | MAT-conformant weighted covariance for Flux (checked against MAT's own `CalcCovMx` / `GetTotalErrorMatrix` with weights, as the C04 verifier did); the exact MINOS rescale; every other block byte-identical |
| products | repaired universe+bootstrap combined covariance; block-sum budget (per band, per block, per-cell median, integral); combined χ² family against the paper with `E_U` (standard, log-normal, stat-subtracted, pulls); Fig. 6/7 band projections; a 205×205 export for the article's Fig. 1 band in the form of `receipts/2d-lgbm42-20261011/cov2d_blocks_205.npz` |
| controls | the unrepaired path reproduces the adopted 6.871 % and VL172/VL173 values exactly; MAT agreement to ≤ 1e-12 relative |
| compute | login node preferred; Slurm only if needed, **≤ 1.0 charged CPU node-h**, jobs ≤ 1 h, `2dc_C04_<tag>`, shared/regular QOS, CPU only |
| namespace | `/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/`; durable copies to CFS `m3246`, sha256 re-measured |
| record | `docs/orchestration/state/2d-closeout/c04-repair/REPORT.md`, with receipts, a ledger row and a fresh read-only independent verifier (own code, budget as plan §5) |
| window | until delivery, or 2026-10-19 |

## 3. Adoption and publication

Joseph adopts or rejects the verified product. If he adopts it, the paper-tighten lane re-quotes every
dependent number (values.tex macros, the note's tables, the article's Sec. IV B and Fig. 1, the primer),
with disclosures, and syncs the standalone repository. The executor does not edit deliverables.

The disclosure must state that the published flux block (4.01 % per-cell median) exceeds the repaired band
(3.65 %) for a reason not established from the release; the FHC-only constraint file is the leading
inference.
