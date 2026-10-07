# PET point-cloud track (Workstream E)

The TensorFlow/point-cloud OmniFold engine, kept separate from the dimension-agnostic
GBDT/MLP N-D drivers at `nd-unfolding/` top level.

**Completed PET campaigns — start here.** Each campaign directory holds many dated proposals, results and
handoffs. The record named below is where each campaign ends; open it before quoting anything from that
directory. These are diagnostic, simulation-only studies, and none of them adopts a product. How the
deliverables use these records is mapped in
[`docs/analysis-note/PET_STUDY_SYNTHESIS.md`](../../docs/analysis-note/PET_STUDY_SYNTHESIS.md).

| campaign directory | where it ends |
|---|---|
| [`direct_token_comparison/`](direct_token_comparison/) | [`RECOMMENDATION-20260918.md`](direct_token_comparison/RECOMMENDATION-20260918.md); its pilot was not launched |
| [`configuration_comparison/`](configuration_comparison/) | `campaign_report.json` (`verdict` / `recommendation` fields); read the directory's README first |
| [`improvement_campaign/`](improvement_campaign/) | [`confirm/CONFIRM_RESULTS.md`](improvement_campaign/confirm/CONFIRM_RESULTS.md), then `REVIEW_DISPOSITION-ROUND2-20260925.md` |
| [`final_design/`](final_design/) | [`DECISION_RECORD-pet-final-design.md`](final_design/DECISION_RECORD-pet-final-design.md) (status line: TERMINAL) |
| [`gbdt_comparison/`](gbdt_comparison/) | [`REPORT-20261005.md`](gbdt_comparison/REPORT-20261005.md) and `REVIEW_DISPOSITION-20261005.md` |
| [`generator_diagnosis/`](generator_diagnosis/) | [`REPORT-20261006.md`](generator_diagnosis/REPORT-20261006.md) and `REVIEW_DISPOSITION-20261006.md` |

**Current typed-descriptor development:** PET remains diagnostic and
method-development. Read [TYPED_DESCRIPTOR_STATUS.md](TYPED_DESCRIPTOR_STATUS.md)
for the software state and next bounded task, and
[PRONG_BRANCH_SEMANTICS.md](PRONG_BRANCH_SEMANTICS.md) for reconstruction-side
definitions, their limitations and future object-representation implications.
The legacy workflow inventory below is not an instruction to resume training.

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
