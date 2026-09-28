# s5p parallel tasks: factual pointers (2026-09-28)

**CITABLE FOR:** where the frozen specification, inputs and output routes are for three tasks other sessions may
run while s5p production (`OI-193`) runs. **NOT CITABLE FOR:** any result, grade, adoption or readiness; the
governing documents named below are.

**Rules for every session using this file.** Work in your own isolated worktree on your own branch (created from
the commit below). Do NOT modify `../MINERvA-OmniFold-s5p` (the campaign worktree), anything under
`docs/orchestration/state/s5p/`, or anything under `/pscratch/sd/j/josephrb/s5p-20260926/` (read-only inputs); do
not submit Slurm jobs named `s5p-*`; do not touch the shared checkout `../MINERvA-OmniFold`. Write cluster outputs
only under your own directory `/pscratch/sd/j/josephrb/s5p-parallel-<task>/`. Read `AGENTS.md` first.

## Authoritative source

- **Frozen admission commit: `4f5a613f`** (`origin/main` history). `55a41765` adds only a scheduling change (lane
  throttles; `nd-unfolding/s5p_requeue.py`); every other production byte is identical (the frozen design
  `docs/orchestration/state/s5p/prod/design.json` has the same sha256 at both, `404446eb...`).
- **Governing specification, in order of precedence (later supersedes the named parts of earlier):**
  `docs/orchestration/state/s5p/contract.json`; amendments 1 (targets T1-T7), 5 (joint design), 6, 6b, 8
  (repairs), **7 (the production admission, frozen)**: `docs/orchestration/state/s5p/contract-amendment-{1,5,6,6b,7,8}-*.json`;
  the owner exception `docs/orchestration/EXCEPTION-20260927-s5p-pilot-negative-rate-resubmission.md`; the reviews
  `docs/orchestration/REVIEW-20260927-s5p-{round1-stage2-exit-and-joint-design,round2-repairs-and-admission-draft,admission-confirmation}.md`;
  the scheduling change (incident 2026-09-28T20:50Z in `state/s5p/campaign-state.json`).
- Budget/authority: `docs/orchestration/AUTHORIZATION-20260926-precision-measurement-completion.md`.

## 1. Independent recomputation of the joint-inference p-values and decisions (Stage 6)

**Goal:** your own evaluator, written from the specification (amendment 7 `claims`, `calibration`,
`validation_and_assurance`, `power`; amendments 6/8 for the shift variants and the determinacy rule; amendment 5 for
the statistics). Do not import or copy `nd-unfolding/s5p_joint.py`, `s5p_inference.py` or `s5p_seqstop.py`
statistical logic; their docstrings describe the specification and may be read as such. Document ambiguities.

**Inputs (read-only):**

| what | route | schema |
|---|---|---|
| frozen design | `docs/orchestration/state/s5p/prod/design.json` | keys `nulls` (per null: `prediction`, `domain` (`pz_lt_6` or null), `calibration_glob`, `calibration_n` {`max`, `min`, `sequential_status`}, `surrogate_seed0`), `power` (per set: `glob`, `surrogate_seed0`, `n`, `null`), `process_shift` (per null: `path`, `sha256`, `mode` = `bias_aligned_upper`), `m1_shift` (per null: `path`, `sha256`, `kappa` = 2, `kappa_robust` = 3, or `none`), `shift_coefficients` [0, 0.5, 1], `alpha_family` 0.05, `lateral_endpoints` (5 bands x 2 unfold products), `data_jitters` (20), `data_central`, `stage1`, `s5c_contract`, `v_sha256`, `v_ensemble_glob`, `v_ensemble_n` 194 |
| calibration products | `/pscratch/sd/j/josephrb/s5p-20260926/runs/prod/cal/<null>/cal_<null>_s<seed>.npz` (exclude `*.partial-*`) | `xsec_flat` (65,856 fine cells, C order pT, p_par, E_avail, q3, W), `xtrue_flat`, `meta` (JSON: `pseudo_seed`, `nuisance_draw` {`flux`, `model` (34 bands), `detector`, `lateral_z` (5 bands), `normalization_z`, `weight_treatment`, `weight_diagnostics`}, `split_key`, `code_sha256`, ...) |
| power products | `/pscratch/sd/j/josephrb/s5p-20260926/runs/prod/pow/<P>_a1.0/pow_<P>_a1.0_s<seed>.npz` (P1-P3 at the MnvTune null, P1g-P3g at the GENIE CV null) | as above |
| sequential status | `/pscratch/sd/j/josephrb/s5p-20260926/runs/prod/status/<null>-B<B>.json`, `<null>-final.json` | `null`, `B`, `max`, `min`, `stop`, `reason` (`rule met for both tests`, `maximum reached`, `budget`, `batches exhausted`), `decisions`, `thresholds`, `design_sha256`, `v_sha256` |
| metric V | `/pscratch/sd/j/josephrb/s5p-20260926/stage3/V/V-s3v.npz` (sha256 `35979ef7...`, receipt `state/s5p/stage3/V/V-receipt.json`) | `V` (109 x 109), `names` (J cell ids) |
| process shift D | `/pscratch/sd/j/josephrb/s5p-20260926/stage3/f4/D16-<g>.npz` | `D_J` (109), `se_J`, `d_pairs` (16 x 109), `f_B_mean`, `names` |
| M1 residual | `/pscratch/sd/j/josephrb/s5p-20260926/stage3/m1/fine-minus-mid-<g>.npz` | `D_J` (109), ... |
| predictions | paths in `design.json` `nulls.*.prediction` | `xsec_flat`, `sumw2_flat`, `edges_<axis>` |
| J-cell map | `docs/orchestration/state/s5p/stage1/stage1_inspect.json` + `docs/orchestration/state/s5c/contract.json` (`measurement.partition_J.supported_cells`) | 109 supported cells of the 3^5 partition (edges `s5p_stage1_inspect.J_EDGES`); GiBUU domain = the 72 cells with p_par index <= 1 |

Implementation conventions you must reproduce to agree numerically (they are part of the frozen design; state if you
consider any unjustified): the surrogate noise on each experiment's J cells is drawn with
`numpy.random.default_rng([pseudo_seed, 0x4A01])`; the prediction's finite-MC residual of each simulated experiment
with `default_rng([surrogate_seed0, pseudo_seed, 0x4A02])`; lateral surrogate = sum_b z_b (f(end 1) - f(end 0))/2;
normalization x (1 + 0.014 z); rounding noise N(0, s_num^2) with s_num the SD of the 20 data jitters (ddof 1).

**Production's own output to compare against (when it exists):** `/pscratch/sd/j/josephrb/s5p-20260926/stage7/joint/joint-evaluate.json`
and its committed copy `docs/orchestration/state/s5p/stage7/joint/joint-evaluate.json`, from
`PYTHONPATH=nd-unfolding python3 nd-unfolding/s5p_joint.py evaluate --design docs/orchestration/state/s5p/prod/design.json --v /pscratch/sd/j/josephrb/s5p-20260926/stage3/V/V-s3v.npz --out <route>`
(run by the campaign after every null has a `-final.json`). Terminal condition: all five `<null>-final.json` exist
and no Slurm job named `s5p-s5p_cal_*` or `s5p-s5p_pow_*` (for example `s5p-s5p_pow_p1_a1p0`) is queued.

**Your outputs:** your branch (evaluator, tests, handoff with the exact final command and any missing inputs);
cluster scratch `/pscratch/sd/j/josephrb/s5p-parallel-recompute/`; a report of every p-value and decision
(ten tests: 5 nulls x {total, shape}; Holm with determinacy; the kappa = 3 robustness flag; power per set at 0.05 and
0.005, rank and determined) compared with production. Agreement verifies the calculation, not the adequacy of the
calibration.

## 2. Analysis-Note synchronization

- **Source:** `docs/analysis-note/` at the newest `origin/main` commit. The s5p commits touching it are `908ecce5`
  (note, primer and paper generator claims corrected to the flux-repaired predictions, VL156-VL160) and `b1e6e3b9`
  (amendment 8's L7 textual corrections); the regenerated generator figures/numbers are `f5ed4704` (receipts under
  `docs/orchestration/state/s5p/stage7/generator-context/`). Nothing of the joint result is in the deliverables yet
  (the campaign adds it at Stage 7 and syncs again).
- **Target:** the standalone repo `/Users/josephbailey/local-research/MINERvA-OmniFold-Analysis-Note`; its newest
  commit (measured 2026-09-28) is `b1410fc` (`[sync] s5e (OI-192) ...`), i.e. none of the s5p changes are synced.
- **Contract:** the analysis-note section of `AGENTS.md` and the precedent
  `docs/orchestration/state/s5c/deliv/R21-fix-plan.md:384-416`: copy the sources, run `bash build_all.sh` in the
  standalone checkout (three PDFs plus the containment check), commit `[sync] ... from MINERvA-OmniFold <sha>`, push,
  and record both remote heads. Run the build in the source tree first; record its exit code and page counts
  rather than assuming earlier ones.

## 3. Reproduction harness

- **Scope that is final now:** the flux-repaired generator predictions and their deliverable figures/numbers
  (receipts `state/s5p/gen5d/gen5d-fluxfix{,-2,-3}.json`; `state/s5p/stage7/generator-context/generator-context-receipt.json`,
  `eavail-marginal-ratios.json`; ledger `VL156`-`VL160`); the pre-freeze numbers (`state/s5p/stage3/prefreeze/`,
  `stage3/{f2,f4,m1}/`, `stage3/V/V-receipt.json`); the envelope (`state/s5p/stage3/envelope-receipt.json`).
- **Producers:** `3d-unfolding/genie/gen5d_flux_reweight.py`, `gen5d_flux_supplement.py`, `gen5d_mode_components.py`,
  `gen5d_to_rootpreds.py`; the figure producers listed (with their working directories) in `docs/analysis-note/make_figures.sh`; `nd-unfolding/s5p_pairdiff.py`,
  `s5p_prefreeze.py`, `s5p_envelope.py`, `s5p_joint.py build-v`.
- **Requirement (handoff Stage 7):** from a fresh checkout with no private paths (cluster data paths declared in one
  config), separate (a) replay of stored statistics (recompute the committed numbers from the stored products,
  compare digests/values) from (b) full regeneration (re-run producers into a new directory); report what reproduces
  bitwise, what to tolerance, and what cannot be regenerated (e.g. the generator event samples).
