# Handoff: PET finalists vs GBDT on existing outputs (result, 2026-10-05)

This is a cold-start handoff for the next session or owner. The governing scope is in this directory:
`GOAL-20261005-pet-gbdt-existing-outputs.txt` and `HANDOFF-20261005-pet-gbdt-existing-outputs.md` (preserved
byte-identical). The task is **complete**. Nothing was launched beyond the bounded local CPU fill-in.

## Durable identities

| item | identity |
|---|---|
| branch | `analysis/pet-gbdt-existing-outputs-20261005` (based on `origin/main` at `52a2f6dd`) |
| plan frozen before any fit | `5f9c5a99` (pushed 2026-10-05 18:12 UTC; first FB fit 18:13 UTC) |
| results commit | `2b62c017` |
| review | cycle 1 at `2b62c017`, repairs `53471b6a`; cycle 2 at `53471b6a`, final repairs in the next commit (`REVIEW_DISPOSITION-20261005.md`); closed |
| draft PR | #16 (https://github.com/josephbaileyy/MINERvA-OmniFold/pull/16), base `main`, not merged |
| PET source | `pet-final-design-20260925` at `bc356b0c0c5b56cb4877bdf2312d2d5dc6d1936d`. It is not on `main`; the code imports it from a checkout after a per-file blob check (`pgc_source.py`) |

## What was done

**Evidence manifest and compatibility:** `REPORT-20261005.md` §2.

**Exact-paired fill-in.** The matched study's scalar OmniFold (HGB `h1`, efficiency-corrected, `truth4_species`,
primary k = 7) ran on all 352 look-1 FB units of the finalists, at 5.306 charged / 4.422 CPU core-h, under the 8 core-h
ceiling.
- **Committed outputs:**
  - `results/gbdt_fb_compact.jsonl.gz`;
  - `results/comparison.json` (plot data);
  - figures in `results/figures/*.pdf|svg`;
  - `results/cpu_ledger.jsonl`.
- **Not committed:** the full per-task outputs, about 80 MB. They are reproducible from the task list.

**Exact DEV pairing from existing operands:** `results/dev_paired.json`.

**Cost model from measured per row-epoch rates:** `results/costs.json`, built by `pgc_costs.py` from
`results/timing/*.fits.jsonl`.

## Result in one paragraph

On identical events and scoring, both finalists beat this GBDT on the E_avail tilt endpoints. The lead is over this
GBDT OmniFold only: binned IBU and AUSSIE do better on the 1D tilt on DEV, and fail on hadron and generator cases.
- **E0:** +0.102 (H2) and +0.070 (L128) in R, with 2–3× lower E0 MSE. The GBDT's error is about 96 % bias.
- **E3:** +0.076 and +0.070.
- **Other PET leads:** most hadron-species reweightings. The muon-scale case's lead is mostly the tilt; its E8
  contrast is +0.016 / +0.028.
- **Level or small:** E4 topology (+0.055 and +0.012; level against GBDT k = 10) and E5.
- **PET worse:** on all three generator-model reweightings, by 0.12–0.25, and on the narrow bump.
- **GBDT robustness:** 0/224 moves-away units, B2 0.0033, maximum weight 5.6.
- **Uncertainties:** none can be compared.

**Recommended next action:** P0, ≤ 165 A100-h with stop conditions (`REPORT-20261005.md` §8). It covers data-scale
closures (dev, NuWro, null) with matched GBDT and IBU baselines, two diagnostic real-data nominals, and one 10 M-prior
timing run. It is **not launched** and needs Joseph's authorization. The scaled cost is 7.3 A100-h per data-scale
unfolding at a 2 M-row prior, and about 4× that at 10 M.

## Open items for the next owner

1. **Ledger row.** `LEDGER_ROW-PENDING.md` has the text. Append it with the next dense id after the PET integration's
   VL164–VL167, expected VL168. Until then the result is not live in the ledger sense.
2. **PR.** Merge only by owner decision. The code imports from `bc356b0c`, so the PET integration should land first or
   together.
3. **If P0 is authorized.**
   - The data-scale closure inputs need a builder: ≈ 9.6 M-row DEV pseudodata (≈ 4.0 M reco-passing, matching the
     data's 4.0 M signed signal events), a disjoint 2 M DEV prior, and the dev /
     null / NuWro distortions.
   - The real-data nominal needs the full-event negative-weight background target that already exists for the
     full-event schema (`VALIDATION_LEDGER.md` :1927-1946).
   - Re-measure the allocation and the queue before launch. The 56,132 node-h reading of 2026-10-05 13:26 is not
     current evidence.

## Things that will bite

- **Python environment.** `HistGradientBoosting.fit(X_val=…)` needs sklearn ≥ 1.7, and the base miniconda has 1.6.1.
  Use an isolated venv with sklearn 1.8.0, numpy 1.26.4 and Python 3.12.2; the matched-study refit control reproduces
  with |ΔR| = 0 there.
- **R2 is a muon-momentum scale, not an energy scale.** `pgc_fb` refuses an R case it cannot reproduce, and uses the
  PET path's `design_inputs.r2_scalars` for R2.
- **Figure formats.** `*.png` and `*.pdf` are gitignored repo-wide. The PDFs here were force-added by explicit path,
  as `gbdt_model_dependence` did.
- **Pushing.** A plain push of the results commit failed with "remote end hung up". `git -c http.postBuffer=524288000
  push` worked.
- **Disk.** The local scratch copies of the FB run arrays (about 35 GB) were deleted after use, except the FB0 sample.
  Re-fetch with `pgc_fetch.py runs`, which digest-checks every file.

## Integration into `main` (2026-10-05)

Merged on Joseph's instruction of 2026-10-05, after the PET integration (#15), through branch
`integrate/pet-gbdt-20261005`: a `--no-ff` merge of this branch at `4367030f`, then the ledger row appended as
**VL168** (open item 1 is done; item 2 is done). The study's files are unchanged apart from this note and the
appended-as note in `LEDGER_ROW-PENDING.md`. P0 remains not launched and unauthorized.

## Owner decision on P0 (2026-10-06)

**P0 is deferred until the PRD article is submitted.** Joseph replied "I agree with your recommendations for both" on
2026-10-06. That answers two recommendations the PET lane gave him the same day:
- "**Defer P0 until the article is submitted.** It doesn't serve this article; its natural time is when a PET-based
  measurement becomes the next question."
- "a CPU-only analysis of existing outputs to find why PET loses to GBDT by 0.12–0.25 on the NuWro and GiBUU generator
  reweightings."

The recommendation also noted that P0's two real-data PET nominals should be dropped or deferred while the article's
numerical headline is on hold. P0's design (§8 of `REPORT-20261005.md`) is unchanged and not launched. The CPU-only
diagnosis is in `nd-unfolding/pet/generator_diagnosis/`.
