# DECLARATION S1: configuration (e)'s 5D covariance on the 16 H2 cells (2026-10-24)

**By** the measurement session, at the director's request of 2026-10-24.
- **Status:** a draft for the director's review. The director binds it, and the compute needs Joseph's approval first.
- **Nothing here has run.** No universe, seed or assembly product exists.
- **Basis:**
  - [`S1-PLAN.md`](S1-PLAN.md) (PR #334, main `85568fd2`);
  - `DECISION-20261024-joseph-5d-community-standard-route.md`;
  - `DECISION-20261024-joseph-h2-16-cell-definition.md` (PR #335, main `46c81983`), which fixes the cells as R00–R15.

**CITABLE FOR:**
- the declared construction: every assembly choice, with its record;
- the jobs, caps and controls;
- the code and its tests.

**NOT CITABLE FOR:** any covariance value, any claim, or any authorization before the binding and Joseph's approval.

## 0. Summary

- **Inputs.** 175 per-universe (e) data unfolds plus a CV control:
  - 100 Flux universes;
  - 67 interaction-model universes in 33 bands (Rvp1pi is not run); <!-- absence-ok: a declared choice of this construction (choice 4), not a claim about the record -->
  - 8 weight-only detector universes, from the detector dump.

  They are added to the existing R bootstrap set A, the 10 R lateral unfolds and the (e) central value. **New:** an
  estimator-seed block of 80 data unfolds, 2D's C08.
- **Recipe.** The adopted 2D recipe, carried to the 5D cells:
  - every band MAT mean-centred, 1/N;
  - Flux weighted by the ν-e + IMD constraint (C04);
  - the MINOS muon-energy lateral flux-rescaled (X01);
  - Rvp1pi dropped;
  - normalization 1.4 %;
  - the seed main effect.

  Then C_model,5D is added, unscaled, beside the total.
- **Compute.** Four regular CPU jobs: pilot, P1, P2 and the seed block. **Total cap 15.5 CPU node-h; expected
  11.2–12.3.** No GPU, under 0.1 GB on pscratch, nothing on CFS.
  - That is 4.5 node-h above the S1 plan's 11.0, entirely the seed block. The plan priced it as option O2: 3 more
    seeds, 60 unfolds, cap 3.6. Here it is enlarged to 2D's five seeds: 4 more, 80 unfolds, cap 4.5 (§2, choice 9).
- **Code.** One new assembler and one gate script, with 18 tests: `nd-unfolding/s1_assemble.py`,
  `nd-unfolding/s1_controls.py` and `nd-unfolding/tests/test_s1_assemble.py`. The director asked for two small code
  changes; §5 says why there are six items, all in these two files.

## 1. Earlier reads of (e) data results

The ruling recorded in the H2 decision requires this list: every assembly choice is committed before any H2-level
quantity is computed from an (e) data product in this pipeline. No choice below uses any of these reads.

| when | what | where |
|---|---|---|
| 2026-09-26 to 2026-10-24 | the reads listed by the H2 definition: s5p Stage 1's H2 bootstrap widths, Stage 2's H2 h, RE-1's P5, Stage 0's H2 readouts, and the PV ladder's readouts | `state/measurement-scoping/pv-ladder/H2-DEFINITION-DECLARATION.md` §0 |
| 2026-10-24 | the S1 plan quoted the H2 data-bootstrap σ range from those records | `S1-PLAN.md` §5 item 8 |
| 2026-10-24 | the S1 plan's reviewer computed relative-difference summaries between the B0 sentinel-free data product and the (e) central value on the fine cells, with no cell formed and no value quoted | the review record behind PR #334 |
| 2026-10-24, for this declaration | sha256 of `data_b-_j-.npz`, `data_R.npz` and `k1_p5_rerun.npz`; product metadata keys (no `xsec_flat`); the 5D flux array against the X01 file's Φ_CV (an input, not a result) | login12 |
| 2026-10-24, this declaration's review | metadata only of `prior_R5fix_CV`, `data_b-_j-`, `data_b1_j101`, `data_b50_j150` and `lat_Muon_Energy_MINOS_0`; key, shape and dtype listings of `data_R`, `k1_p5_rerun` and `data_b-_j-`; the three G2 digests; the simulation-only bank-path denominators (§4, G1); `sacct` of jobs 58904837 and 58916065. No H2-level quantity was formed | the review record behind this PR |

## 2. The choices, each with its reason (simulation, records and the 2D precedent only)

| # | choice | declared | reason |
|---|---|---|---|
| 1 | **cells** | R00–R15 of `nd-unfolding/pv-ladder/readouts/h2_definition.json` (`b6790761…`), composed on `s5p_stage1_inspect.coarse_map(H2_EDGES)`. The fine map must hash to `930326a3…`, which this lane reproduced. Cell integrals are Σ_f x_f vol_f. No total row | the H2 decision, item 1, and its declaration §5. Box 17 is inside R09, boxes 2, 6, 10 and 14 are excluded, and support follows the fine map. The same integrals as C_model,5D, so the two add |
| 2 | **band centring** | MAT `CalcCovMx`: mean-centred, 1/N, for every universe band. Flux is weighted (choice 10) | the adopted 2D recipe: "every other band: MAT mean-centred, 1/N" (`state/2d-closeout/stageC/production/s5_rollup.py:14`), and z-cv's per-band blocks too (`docs/analysis-note/sec_5d.tex:622`). With CV centring, an asymmetric pair adds the common offset m mᵀ (`app_statmethods.tex:310-340`) |
| 3 | **lateral reference** | mean-centred over each band's two endpoints, so **no CV enters**. C_b = ¼ Δ Δᵀ, with Δ the endpoint difference | the same estimator (`app:pair`). The 2D recipe's lateral bands use "the adopted formula: mean-centred, 1/N, N = 2" (`state/2d-closeout/c04-repair/REPORT.md:69`, `s5_rollup.py:197-205`). The sentinel-row mismatch (`state/s5p/campaign-state.json:247`) therefore never arises, so no sentinel-free CV unfold or `--drop-sentinel-rows` path is needed |
| 4 | **Rvp1pi** | dropped, and not run | KI 92: Rvn1pi and Rvp1pi "encode the same shift … counting it twice" (`docs/analysis-note/sec_systematics.tex:226-230`). The quoted 2D block drops Rvp1pi (`s5_rollup.py:13, :79`) |
| 5 | **(a)'s inflation D** | omitted | D rescales (a)'s vertical block to its unified-throw diagonal (`sec_5d.tex:597-611`). That construction is (a)'s; the joint-throw inflation is limited to the five-axis (a) covariance (`sec_systematics.tex:285-292`); the 2D recipe has no D (`s5_rollup.py:9-18`). No (e) throw tooling exists (S1-PLAN O3) |
| 6 | **C_stat set** | s5p study N **set A**: `data_b{1..50}_j{101..150}.npz`, 50 refit-per-replica data bootstrap replicas with jitter; ddof 1 | its streams are data Poisson, MC Poisson(1) and template Poisson(1), with the refinement refit (`nd-unfolding/s5p_assemble.py:9-10`). That matches 2D's three-stream S1 (`s5_rollup.py:15`). The numerical component is ABSORBED in exactly this set (`state/s5p/contract-amendment-4-stage2-decisions.json:12`). Set B (100, no jitter) would need a separate C_num |
| 7 | **GEANT source** | the detector dump `s5p-20260926/bank_detector`, for all four weight-only detector bands | MinosEfficiency exists only there. The dump is the R-path rebuild, whose receipt reproduces 10 CV arrays (`detector-dump.json`). `s5p_nullexp.py:25-28` prefers it, and s5p's null experiments drew the detector bands from it (amendment 7). The bank's GEANT copies differ from it in `wr` (S1-PLAN §1 row 6), so one source is used for all four bands. Gate §4 G1 checks the bank path against it |
| 8 | **C_model combination** | C_model_abs = diag(f) · C_model,5D · diag(f), with f = (e)'s central value on R00–R15. C_total = C_e + C_model_abs. Both are written, and C_model is not mixed into any block | DECISION-20261024 item 3: unscaled, one fully correlated component per vertex, "reported beside the statistical and systematic covariance, and in the total". The H2 declaration's C_abs (§3.1) uses x = X_0 = P5, and gate G2 proves P5 = this f bitwise |
| 9 | **estimator-seed block (added)** | C_seed = the sample covariance (ddof 1), over estimator seeds 42, 45, 48, 51 and 54, of the per-seed mean of bootstrap replicas b = 1–20 (jitter 100 + b). Seed 42 is set A's b1–b20 | the 2D recipe adds the seed main effect (R7, C08: `s5_rollup.py:16-18`). For the refined estimator, "the seed main effect … has never been measured" (`RE2-PLAN.md`, P6). For (e) in 5D, no seed main-effect covariance on the data exists. s5e's data seed runs were B0 (`state/s5e/contract-amendment-1-diagnosis-execution.json:16`). Its R runs at estimator seed 43 are single-seed probes on pseudo experiments, not on data: K4 (`state/s5e/contract.json:73`, `cand-dev-tasks.tsv:25`) and A3 (`cand-assess-tasks.tsv:35`). RE-2's seeds were the same 45, 48, 51 and 54 (`RE2-DECLARATION-B.md:180`) <!-- absence-ok: git grep of 'seed (block|main effect)|estimator[- ]seed' over docs/orchestration/state/s5e, state/s5p and RECORD-20260927-s5p-stage2-exit.md at 2c8c1e4f; its hits are s5e's B0 data seed runs (amendment-1:16), amendment 3's seed-43 item, and the R seed-43 pseudo probes K4 and A3 named in this row; the RE-2 phrase quoted is RE2-PLAN.md P6 --> |
| 10 | **Flux weights (added)** | the first 100 `Flux` entries of `sorted_NuEConstraint_FHC_RHC_IMD.txt` (`e38ad7d2…`), with the block centred on the weighted mean | C04 (KI 95), adopted for 2D (`docs/publication/DECISION-20261012-joseph-adopt-2d-c04-repair.md`): MAT `CalcCovMx` with `GetUnivWgts`, which equal this file's first 100 entries exactly (`c04-repair/REPORT.md:53-59`). The weights are per PPFX universe, so they carry to 5D unchanged. This lane re-measured Σw = 211.012 and n_eff = 19.06, the recorded values |
| 11 | **MINOS lateral rescale (added)** | each `lat_Muon_Energy_MINOS_<i>` product × Φ_CV(pT) / Φ_MINOS,i(pT) per fine pT bin, using the recorded factors `minos_rescaled.npz` (`8912376e…`; 0.9995816 and 1.00466854, flat in pT) | X01 (KI 96), adopted for 2D. The 5D lateral dump asserts its flux equals the CV npz's (`nd-unfolding/s5p_input_dumps.py:166`), so the defect is present in 5D. The 5D flux equals the factors' Φ_CV **bitwise** on the same 14 pT bins (measured 2026-10-24), and the flux is a pure per-pT divisor (`nd-unfolding/xsec_nd.py:54-80`). So the 2D factors are exact here. Endpoint i ↔ MINOS universe i. The 2D recipe pairs the same active files that way (`s5_rollup.py:372-375`); for 5D the pairing rests on the endpoint files' names, `…_active_Muon_Energy_MINOS_<i>.root` (`state/s5p/s3-latdump-tasks.tsv:9-10`) **(inference)**. The 5D lateral dumps were deleted after use |

**Not included:** C_ML (specific to (a)'s split; S1-PLAN §4), the bounded envelope h, and C_num, which is absorbed
(choice 6).

## 3. Jobs, exactly

**Definitions.**
- `P=/pscratch/sd/j/josephrb`; `B=$P/s1-20261024`.
- `D=$B/deploy/<pin8>`: a clean clone of the binding commit. The pin is named in the binding.
- `T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024/s1`.
- `PK=$D/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh`.
- `PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"`.
- Every job runs on regular QOS on a CPU node, account m3246, exclusive, `--no-requeue` (in `PK`). **Never premium.**
- Every line runs through the deploy's `s5c_array.sh`: pinned-sha refusal, guarded run, inventory.
- **Resumption** comes from the tools' own per-product skip (`s5p_universe.py:213-215`, `s5p_numerics.py:179-181`).
  `s5c_array.sh`'s skip keys on `$OUT/<task>.npz`, which these tasks never write.
- The task tables are `s1/tasks-pilot.tsv`, `s1/tasks-prod.tsv` and `s1/tasks-seed.tsv` (sha256 in §6), generated
  from `s1_assemble.EXPECT`.

| job | command | lines | projected wall | limit | cap, CPU node-h | expected |
|---|---|---|---|---|---|---|
| **pilot** | `sbatch -A m3246 -q regular -C cpu -t 00:30:00 -J s1pilot -o $B/logs/%x_%j.out $PK $D <pin> $T/tasks-pilot.tsv $B/runs 32 56G 0 7 inherit` | 0: CV control; 1–5: Flux:0, Flux:99, 2p2h:0, MaCCQE:1, FrAbs_pi:0; 6–7: MinosEfficiency:0, GEANT_Neutron:1 (dump) | 1,370 s | 0:30 | **0.5** | 0.35–0.38 |
| **P1** | the same with `-t 05:15:00 -J s1prodA`, `$T/tasks-prod.tsv`, lines `0 7` | 0–7: 11 bank universes each | 15,070 s | 5:15 | **5.25** | 3.84–4.19 |
| **P2** | the same with `-J s1prodB`, lines `8 15` | 8–11: 11; 12–14: 10; 15: the 6 remaining detector universes | 15,070 s | 5:15 | **5.25** | 3.84–4.19 |
| **seed** | the same with `-t 04:30:00 -J s1seed`, `$T/tasks-seed.tsv`, lines `0 7` | seeds 45, 48, 51 and 54 × {b 1–10, b 11–20} | 12,890 s | 4:30 | **4.5** | 3.14–3.58 |
| **total** | | 8 + 168 + 80 = 256 unfolds | | | **15.5** | **11.2–12.3** |

**Bases** (S1-PLAN §2, **arithmetic**):
- a universe step wall is 1,256–1,370 s, and a float64 data step 1,132–1,289 s;
- 8 lanes × 32 CPUs × 56 GB fit a node. A comparable `s5p_universe` task used 18.95 GB (job 58916065). Set A's
  float64 steps peaked at 23.0–23.7 GB (job 58904837), which bounds the seed lanes;
- limits are ≥ 1.25 × the projection at the top of the range;
- caps are nodes × limit;
- expected values are the job walls at 1,256–1,370 s (universes) and 1,132–1,289 s (seed).

**Order and stop rules:**
1. **Before the pilot**, on login12 at 0 node-h: gates G1 and G2 (§4). A FAIL stops everything.
2. **Pilot.** Then gates G3 and G4, on the 7 universes and the CV control.
   - **Re-pricing:** if any pilot product's `seconds_load + seconds_unfold` exceeds 1,500 s, P1, P2 and the seed job
     are re-priced and re-bound before they are submitted.
3. **P1, P2 and seed** may run concurrently. Then gate G3 on all 175 universes and G5 on the four seeds.
4. **Assembly** (§3.1), when C_model,5D exists under its own binding.
5. **On every job:**
   - it is ledgered from `sacct` in `s1/LEDGER.tsv`;
   - a watcher cancels and reports any job past 1.25 × its projected wall, and survives the time the job pends;
   - any FAIL, non-COMPLETED state or non-zero exit stops and is reported. Nothing is resubmitted without the director.
6. **Storage.** Products go to `$B/runs/uni` and `$B/runs/seed`, about 95 KB each, so about 25 MB. Logs go to
   `$B/logs`. After G3 and G5, everything is copied to HPSS beside the Stage 0 tars, with `hsi hashcreate` and
   `hashverify` and a retrieval check. Nothing goes to CFS.

### 3.1 Assembly and readout: login node, 0 node-h

```bash
$PY $D/nd-unfolding/s1_assemble.py --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --inputs-npz $P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz \
  --central $P/s5p-20260926/runs/s2/num/data/data_b-_j-.npz --data-dir $P/s5p-20260926/runs/s2/num/data \
  --seed-dir $B/runs/seed --seed-tag S1seed --universe-dir $B/runs/uni --universe-tag S1 \
  --lateral-dir $P/s5p-20260926/runs/s3/latunf --x01 $P/2d-closeout-c04repair-20261012/build/minos_rescaled.npz \
  --flux-constraint $P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt \
  --cmodel <C_model,5D npz> --cmodel-sha256 <its committed digest> --cmodel-key <fractional key> --cmodel-abs-key <absolute key> \
  --inventory $D/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/INVENTORY.sha256 \
  --manifest $D/docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt \
  --detector-receipt $P/s5p-20260926/bank_detector/detector-dump.json --out $B/s1_assembly.npz
```

- **What it writes:**
  - `s1_assembly.npz`: f, U, every block, C_e, C_model_frac, C_model_abs, C_total and meta;
  - `s1_assembly.json`: the readout. Per cell, the relative σ of each component group (stat, flux, interaction,
    detector, lateral, normalization, seed, C_e, C_model, total); trace shares; eigenvalue extremes; the rank at
    10⁻¹².
- **What is committed:** the JSON goes under `s1/readout/` with the npz's sha256. The npz stays on pscratch and
  HPSS.
- **Its internal refusals:**
  - **digests:**
    - the definition and fine map;
    - `of_inputs_5d.npz`;
    - the central value, against `fb5cc679…` and the Stage 0 inventory;
    - each set-A replica, against the Stage 0 inventory;
    - each lateral, against the sf1 manifest;
    - every weight file a universe records: bank files against the sf1 manifest, detector files against the dump's
      receipt. The receipt is itself checked against the sf1 manifest (`c52dca58…`);
    - the X01 factors, the constraint file and C_model.
    The seed-block products are new, so their digests are recorded, not checked;
  - **filenames against metadata:** `bootstrap_seed`, `jitter_seed` and `coords` must match each replica's and seed
    product's filename;
  - the exact universe set (§4 G3), and each product's estimator and source;
  - **C_model:** it is 16 × 16 and symmetric, and diag(f) C_model diag(f) reproduces the builder's own absolute
    matrix to 10⁻¹² relative. That shows f = X_0 to 10⁻¹² relative wherever C_model is non-zero, and that the keys are not swapped;
  - C_e and C_total are PSD to −10⁻¹² of the largest diagonal;
  - it will not overwrite.
- **Not in the readout:** 2D also reported X02 and a clipped random-effects seed variance beside C08. This readout
  does not.
- **The four `<…>` fields** come from the C_model,5D builder's committed JSON (H2 declaration §3.1), which the 2d
  test lane owns. The binding fills them in. The assembly does not run before they exist.

## 4. Controls (gates)

`s1_controls.py` prints PASS or FAIL per check and **no cross-section value**. Only G1, which is simulation-only,
prints its deviations. Every gate exits 1 on any FAIL, and that is a STOP.

| gate | command (`$PY $D/nd-unfolding/s1_controls.py …`) | passes iff |
|---|---|---|
| **G1** bank-path denominator | `denominator --inputs-npz $P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz --bank $P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware --dump $P/s5p-20260926/bank_detector` | for each of the 6 GEANT universes, `s5p_universe.denominator(bank cv.npz, GEANT_*_tdw)` meets three conditions against both the dump's and the npz's CV `denom_nd`: the same support; the total within 10⁻⁹ relative; every cell within 10⁻³ relative. The bank's GEANT `tdw` are CV-equal, so this tests the denominator path 169 universes use. **The per-cell bound is measured, not exact** (below the table) |
| **G2** central = data_R = P5 | `central --central $P/s5p-20260926/runs/s2/num/data/data_b-_j-.npz --data-r $P/s5e-20260925/runs/cand/assess/data/data_R.npz --p5 $P/methods-paper/re1-20261022/out/5d/k1_p5_rerun.npz` | the digests are `fb5cc679…`, `361030f3…` and `e36f3b25…`, and the three `xsec_flat` are bitwise equal |
| **G3** universe products | `products --dir $B/runs/uni --tag S1 --universes <the line's list> --manifest $D/docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt --detector-receipt $P/s5p-20260926/bank_detector/detector-dump.json`; after production, the full list of 175 | each product exists. It carries schema `s5p-universe/1`; config R; capacity None; 5 iterations; estimator seed 42; three B0 estimators at 100/8/42; refinement 400/31/45; the input and background digests; 2,801 sentinel rows; tdw weights (bank) or denom_nd (dump), each with its manifest's or receipt's digest; and, for Flux, its own flux file. `xsec_flat` has 65,856 entries, all finite and ≥ 0 |
| **G4** matched-CV control | `cv --cv $B/runs/uni/S1_CV.npz --central $P/s5p-20260926/runs/s2/num/data/data_b-_j-.npz` | `xsec_flat` equal bitwise. The same path reproduced it at Stage 0 (`prior_R5fix_CV` = N1 base, C2) |
| **G5** seed products | `seeds --dir $B/runs/seed --tag S1seed --seed <s>` for s = 45, 48, 51, 54 | 20 products per seed. They carry schema `s5p-numerics/1`, B0 at s, refinement random_state s + 3, the input digests, and `bootstrap_seed`, `jitter_seed` and `coords` matching the filename (float64). They are finite and ≥ 0 |

**G1's per-cell bound, measured (simulation only, the review of 2026-10-24, login12).**
- **What was compared:** the bank-path denominator rebuilt from `cv.npz`'s `td_*` and the GEANT `tdw` (all six share
  sha256 `c0ae3c18…`), against the dump's `denom_nd` and the npz's CV `denom_nd`. Those two agree exactly.
- **Result:** the support is identical, 10,694 cells, and the totals agree to 3.5 × 10⁻¹². Per cell the maximum is
  4.098 × 10⁻⁴ relative, with 5,066 cells above 10⁻⁹, split 50.4 % low and 49.5 % high.
- **Reading:** events move between cells at bin edges. The bank's truth coordinates carry 2,801 NaN rows, which
  are dropped. No events are missing **(inference from the totals and the sign split)**.
- **Consequence:** the offset was measured with the CV-equal GEANT weights only. For another universe it scales with
  that universe's weights on the events that cross bin edges, so within a band it is nearly common **(inference)**.
  Mean-centring (choices 2 and 10) removes a common offset to first order; CV centring would not.
- **The bound:** 10⁻³ is set at 2.4× the measured maximum. It is not exact.

## 5. Code and tests

The director asked for two small changes, for the lateral reference and the C_model combination. Fixing the
choices from the records gives six items. All are in two new files, and `s5p_assemble.py`, which s5p's records
depend on, is left unchanged:

| item | where | why it is needed |
|---|---|---|
| (i) the 16-cell functional matrix, with both digests | `s1_assemble.fine_map`, `functional_matrix` | the cells changed after the plan (choice 1) |
| (ii) MAT mean-centring, with weights | `mat_cov` | choices 2, 3 and 10. `s5p_assemble.band_cov` centres on the CV |
| (iii) the lateral bands without a CV, and the X01 rescale | `main`, `x01_scale`, `pt_index` | choices 3 and 11. This replaces the plan's sentinel-free-CV option |
| (iv) the C_model combination | `model_abs`, `main` | choice 8 |
| (v) the seed block | `seed_block`, `main` | choice 9 |
| (vi) the exact universe set, estimator and source checks, input digests, and the gates | `universe_bands`, `check_meta`, `check_universe`, `load_manifest`, `require_listed`; `s1_controls.py` | Rvp1pi, GEANT source, §3.1, §4 |

**Tests** (`nd-unfolding/tests/test_s1_assemble.py`; 18 tests, all passing locally in 2.5 s; no real data):
- the fine map reproduces `930326a3…`, and a changed definition is refused, even with its file digest patched in;
- mean-centring cancels a common offset, while CV centring would not;
- the weighted block is MAT's formula, and uniform weights give the unweighted one;
- the constraint file is parsed in universe order, and a wrong digest is refused;
- X01 is applied per pT bin, and a flux one ulp off is refused;
- the seed block and the model combination;
- the universe set is exact: 175 in 38 bands, with a missing one, an Rvp1pi product or a `.partial-` file refused;
- the estimator and source checks: capacity, iterations, the refinement seed, the estimators, the digests, a
  detector band on bank weights, and a Flux universe without its flux. Weight provenance against the manifest and
  the receipt is tested, including one wrong digest;
- the finite gate (one negative entry and one NaN);
- the cv and central gates pass, and stop on a one-ulp or one-entry difference;
- the denominator gate: it passes a total-preserving ±5 × 10⁻⁴ per cell, and stops on ±2 × 10⁻³ or on a 10⁻⁸
  shift of the total;
- **end to end:** a synthetic assembly of 50 replicas, 175 universes, 10 laterals, 80 seed products and a C_model.
  - Every block is recomputed by hand, including X01 with a pT-varying scale and an independent pT index.
  - The totals add, and the readout's σ and trace shares are checked.
  - Each listed input is refused separately when it alone is missing from its manifest: the central value, one
    replica, the laterals, and the detector receipt.
  - A replica or seed product whose filename disagrees with its metadata is refused, by the assembler and by gate G5.
  - It refuses an empty manifest, swapped C_model keys, and an overwrite.
- **Mutations caught** (the review's and this lane's): CV-centring a band, the Flux block or the laterals; dropping, swapping or inverting the X01
  scale; removing the Flux weights; a wrong pT axis; dropping any one of the inventory, manifest, receipt or
  filename-vs-metadata refusals.
- The existing `test_s5p_assemble.py` still passes.

## 6. Pinned bytes

| item | sha256 |
|---|---|
| `nd-unfolding/s1_assemble.py` | `5ebe1a8ad68ca9de3343062e1835c899ba25c0f1c7e2d22156284567c00cb247` |
| `nd-unfolding/s1_controls.py` | `bfc8986e264eb5d0274c2d988862cd2544aec4e6f85d045336e1f381b1495f4f` |
| `nd-unfolding/tests/test_s1_assemble.py` | `a4bb69826f597d0e0a2cef88933fff1d908acca32932979c4df2d506c413a9b7` |
| `s1/tasks-pilot.tsv` | `6db31a3411771c00a67dcf3ccb56c20a9622209791449e76a0be22fbfff3ee0d` |
| `s1/tasks-prod.tsv` | `bb32d9180cdf64cef22ffa378591d86af7a65abaab263a3c9ab4840acee75896` |
| `s1/tasks-seed.tsv` | `4425a91e17b5480658691705e4e1a2194c69049fc48868da7ed035d8a09c2a4c` |
| `h2_definition.json`; fine map | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89`; `930326a3a7c0852d4047b5468d8ea3b63d046b896e4a4de1557e29f95102e18c` |
| `of_inputs_5d.npz`; `bkg_dump.npz` | `07fccc1a…`; `2addac8f…` (measured 2026-10-24) |
| central `data_b-_j-.npz`; `data_R.npz`; P5 `k1_p5_rerun.npz` | `fb5cc6798b97…`; `361030f3a3d1…`; `e36f3b25459e…` (measured 2026-10-24) |
| set A `data_b{1..50}_j{101..150}.npz` | each in `5d-design-20261023/stage0/INVENTORY.sha256` |
| laterals `lat_<band>_{0,1}_b-_j-.npz` | each in `state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt` |
| bank (701 files) | each in the same manifest; `cv.npz` `072643e1…` |
| detector dump (32 arrays) | each in `bank_detector/detector-dump.json` |
| flux integrals `flux_integral_universes_MEFHC.root` | `5eecae84…` |
| X01 factors `minos_rescaled.npz` | `8912376ef2a6cfce8bed515cc945d9d5778cf5c838154a685435c3c7ce25416d` (measured) |
| constraint file | `e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2` (measured) |
| C_model,5D | from its builder's committed JSON (§3.1) |

## 7. Unchanged and open

- **Unchanged:** no GPU; MP-2 stays held; no claim, target or endpoint changes; `s5p_assemble.py` is unchanged.
- **Open:**
  - **Joseph's approval** of 15.5 CPU node-h, which the director requests with this declaration. The seed block's
    4.5 can be approved separately. Without it, C_seed is omitted, and the paper states that the 5D seed main effect
    is unmeasured. <!-- absence-ok: a conditional future disclosure; the record of the absence is choice 9's citations -->
  - **C_model,5D**, under its own binding; the assembly waits for it.
  - **GiBUU's domain:** the H2 decision's open item. It affects C_model, not this construction.
