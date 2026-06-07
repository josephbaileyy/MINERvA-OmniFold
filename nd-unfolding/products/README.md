# Distilled cross-section products

Final products, organized by dimensionality of the unfold. The large ROOT/npz here are
gitignored data; the merged input omnifiles (`runEventLoopOmniFold_{4D,5D}_*.root`) and the
per-universe systematic banks stay at `nd-unfolding/` top level (they are unfold *inputs*,
not products).

- `4d/` — `xsec_4d_MEFHC_5iter_lgbm.root` (frozen d⁴σ/dpt·dpz·dEavail·dq3 GBDT product),
  `closure_4d_q3bump.root`.
- `5d/` — `xsec_5d_MEFHC_5iter_lgbm.root` (d⁵σ, +W axis, Workstream F),
  `closure_5d_Wbump.root`.
- `pet/` — PET point-cloud absolute cross section + weights + comparison plots
  (Workstream E): `xsec_4d_PET_absolute*.root`, `xsec_4d_PET_closure.root`,
  `pet_weights*.npz`, `pet_vs_gbdt*.png`.

3D products live in `../../3d-unfolding/`. Scripts reference these via the
`products/<dim>/<file>` relative paths (run from `nd-unfolding/`).
