# PET point-cloud track (Workstream E)

The TensorFlow/point-cloud OmniFold engine, kept separate from the dimension-agnostic
GBDT/MLP N-D drivers at `nd-unfolding/` top level.

**Code**
- `dump_pointcloud_inputs.py` — builds `of_inputs_pc.npz` (per-hadron clouds) from the
  `runEventLoopOmniFold_PC_MEFHC.root` omnifile.
- `minerva_pet_dataloader.py` — vendored-OmniFold (`../../omnifold_nn`) DataLoader adapter;
  trains PET/MLP MultiFold; `--reweight-all` evaluates push weights on the full 32.8M gen
  cloud; `--closure` runs MC-reco-as-pseudodata.
- `pet_vs_gbdt.py` — PET-vs-GBDT comparison; `--absolute` extracts the real (non-area-
  normalized) cross section via `xsec_nd.extract_cross_section_nd`, reusing the frozen GBDT
  completeness.
- `sbatch_pet_{train,xsec,compare,smoke}.sh`, `sbatch_pc_downstream.sh`,
  `sbatch_refresh_pet_vs_gbdt.sh`, `run_pet_refresh_interactive.sh` — launchers. They
  `cd nd-unfolding` (so `of_inputs_pc.npz` and the shared N-D modules resolve) and invoke
  the scripts as `pet/<script>.py`.

**Imports** resolve via the absolute path `/pscratch/.../MINERvA-OmniFold/nd-unfolding`
inserted into `sys.path` (not `__file__`-relative), so the move into `pet/` is transparent
to sibling imports (`unfold_nd_omnifold_unbinned`, `xsec_nd`, `unfold_2d_omnifold_unbinned`).

**Products** land in `../products/pet/` (`pet_weights*.npz`, `xsec_4d_PET_*.root`,
`pet_vs_gbdt*.png`). Note `omnifold_nn_core.py` and `nn_{dump_inputs,run_from_npz}.py` are
the *scalar* NN-vs-GBDT cross-check (shared core) and intentionally stay at top level.
