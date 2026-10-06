# Run log: PET vs GBDT existing-output comparison

All times are UTC on 2026-10-05.

| when | what | result | record |
|---|---|---|---|
| 15:59–16:05 | Copied `reco_scalars` (inventory byte range) and `row_features.npz` read-only from Perlmutter | digests verified | `pgc_fetch.py` |
| 16:09 | Control: PET re-score of `S4F-H2S1T24K5-FB0` k = 5 | PASS, 952 values, max \|diff\| 1.1e-16 | `results/controls/control_pet_rescore.json` |
| 16:10 | Control: matched-study refit (F0 dev, efficiency-corrected, `truth4_species`, seed 1) | PASS: inputs identical, \|ΔR\| = 0 at k = 1–10; 0.018 core-h | `results/controls/control_matched_repro.json` |
| 18:12 | Plan frozen and pushed | `5f9c5a99` | `PLAN-20261005.md` |
| 18:13–19:32 | Fill-in: 344 tasks; 8 R2 tasks refused by the R2 guard before any fit | 0 failures among fits | `results/cpu_ledger.jsonl` |
| (note) | The runner's input-wait change was edited before launch and committed as `44d135c2` at 18:13:09, about 7 s after the first fit started (18:13:02). Owner's statement, not recorded by any artifact: the executed bytes are those of `44d135c2`, with no edit between launch and commit. The runlog does not record the runner commit. The later R2 repair does not change `pgc_fb` behaviour for non-R2 cases (independently checked in review cycle 1) | — | git log; review cycle 1 finding 14 |
| 19:33–19:36 | R2 repair (the PET path's `r2_scalars`, blob-pinned) and retry of the 8 R2 tasks | 8 written; total charged 5.306 core-h, 4.422 CPU core-h; no budget stop | `results/runlog.jsonl` |
| 19:40 | Reductions, DEV re-scoring, cost model, figures | 23/23 cases complete; 0 integrity problems | `results/` |
