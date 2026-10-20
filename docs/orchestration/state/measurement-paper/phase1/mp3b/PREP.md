# MP3-B preparation: NuWro on a free proton, combined 12:1 into NuWro on CH, beside A7

**By** the measurement session, 2026-10-19, under the frozen specification MP3-B
([`PLAN.md`](../../PLAN.md) §4.3; frozen by [`BINDING-PHASE1-20261019.md`](../../BINDING-PHASE1-20261019.md) §2, with D6).
**Tree:** worktree branch `measurement-paper/phase1-20261019` at `a30a1292`. The code is in `measurement-paper/phase1/mp3b/`.
**Status: PREPARED, NOT SUBMITTED.** Nothing has gone through sbatch, srun or salloc. The cluster work so far is
staging, plus two login-node preflights that are read-only (0 bytes written; see §6).

**CITABLE FOR:** the chain as it will run, the seeds, how each gate is computed, and the charge estimate. It also
records two facts about A7's frozen NuWro decision: the Holm-with-determinacy threshold, and the margin to it
(§5.3), both recomputed bitwise.
**NOT CITABLE FOR:** any MP3-B result, a re-grade of A7 (D6), or any claim.

## 1. Submission (on GO)

```
D=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3b      # staged 2026-10-19 (§7); code/ inputs/ logs/ only
# 1. re-verify the staged copies (must equal §7) and that no run directory exists
ssh saul.nersc.gov "cd $D && for f in code/* inputs/*; do echo \$(git hash-object \$f) \$f; done; ls -d gen out 2>&1"
# 2. look at my own queue (do not touch the SF-1 methods-lane jobs on m3246)
ssh saul.nersc.gov 'squeue -u josephrb -o "%.12i %.20j %.8T %.10q"'
# 3. submit: one job, QOS shared, 8 CPUs, 1:30:00 limit
ssh saul.nersc.gov "cd $D && sbatch code/mp3b_job.sh"
# 4. monitor and charge
ssh saul.nersc.gov "sacct -X -P -j <JOBID> -o JobID,State,ExitCode,ElapsedRaw,AllocTRES,QOS,Account,Start,End,NodeList"
#    charge = ElapsedRaw x billing / 256 / 3600
# 5. fetch the small outputs (not the .root files) into docs/.../phase1/mp3b/ and compare sha256 on both sides
```

`mp3b_job.sh` sets `-A m3246 -C cpu -q shared -c 8 -t 01:30:00`. It writes only under `$D`. It refuses to run if
`$D/gen` or `$D/out` exists. It does not use `set -u`, and every path in it is absolute (sbatch runs a copy of the
script).

## 2. Seeds and event counts (`measurement-paper/phase1/mp3b/SEEDS.txt`, declared before any run)

| sample | seed | events | card |
|---|---:|---:|---|
| H main | 63001 | 250,000 | the production card (`run_nuwro.sh`; `work_nuwro_p1/params.txt`) and flux `3d-unfolding/genie/flux_mefhc_numu_nuwro.root` (0.5–50 GeV), with only the target lines changed |
| H supp | 64001 | 25,000 | the frozen 50–100 GeV supplement card (`run_gen5d_supplement.sh nuwro`) and flux `gen5d_fluxfix/supp/flux_phi_t_50_100.root`, with only the target lines changed |

- **Target lines.** The C12 card has `nucleus_p = 6, nucleus_n = 6`. The H card has `nucleus_p = 1, nucleus_n = 0,
  nucleus_target = 0`, verbatim from the shipped `data/target/proton.txt`, as in the probe.
- **No seed is reused.** Seeds already in use: C12 production 21–28, C12 supplement 52001, timing runs 90001/90002,
  GENIE supplements 50001/51001, probe 9101.
- **No B4-remedy seed or factor is declared.** On a B4 FAIL the study stops (§4).
- **Measured: the probe's effective card differs from the production card in exactly** `random_seed`,
  `number_of_events`, `nucleus_p`, `nucleus_n` and `nucleus_target`. The probe and production `.par` dumps (every
  parameter NuWro ran with) were diffed. The run checks this again for both H samples (C0).
- **How the frozen 50–100 GeV supplement was made.** It was 100,000 C12 events, seed 52001. It used
  `run_gen5d_supplement.sh nuwro` with `setup_nuwro.sh` from `gen5d/code/` (sha256 `15007d6f…`, the same as
  `3d-unfolding/genie/setup_nuwro.sh`) and NuWro 21.09.1 e20:debug from CVMFS. It was converted with
  `gen5d/code/nuwro_to_flat_5d.C` (`01e89fb2…`). Its source records are `README-gen5d-fluxfix.md` round 2,
  `gen5d-fluxfix-2.json` and `supp/run_nuwro.out`. The H supplement repeats all of this. The only differences are
  the target lines, the seed and N = 25k, the spec's count.

## 3. The chain as it will run

**Generation.** The job sources three copies of `setup_nuwro.sh`, one per parallel task. Each copy keeps its
`nuwro_home_dbg` symlinks under `$D/env/<task>`. This is the probe's method, made safe for parallel tasks. The three
tasks run in parallel:
- **H main and H supp.** Each runs NuWro, then `nuwro_to_flat_5d.C`, the frozen gen5d copy, run in place.
- **Control C1.** The same macro re-converts the frozen C12 inputs `work_nuwro_p1/nuwro_p1.root` and
  `supp/nuwro/nuwro_supp.root`.

**Build** (`mp3b_build.py`, env `root_6_28`). The two frozen modules are staged copies: `gen5d_flux_reweight.py`
and `gen5d_flux_supplement.py`, sha256 `89863318…` and `ff7a2d0e…`, the same bytes that built the products.
`gen_to_xsec5d` is imported from the frozen export `gen5d/code/tree` (`81d94a95`, `1608acd5…`), and each import
path is asserted. The H samples run through the same statements as the C12 sample of the same energy range:
- **H main.** `g5.extract_nuwro([flat],[flat])` keeps the in-phase-space CC events. Its parity step compares the file
  with itself, because the H run has no older flat file to compare against. The event alignment is checked as
  `cmd_reweight` checks it. The weight is `r(E) = (phi_t/Phi_t)/phi_s`, with `gfr.flux_weights` on the production
  NuWro flux over `GEN_RANGE["nuwro"] = [0.5, 50]`. The prediction is `x = gfr.build_weighted_nuwro(...) = sum_bin
  w_e r_e / N_total`, with N_total = all events in the file.
- **H supp.** `sup.check_flux_file` requires the flux to equal phi_t × width bitwise. `r = int_50^100 phi_t / Phi_t`
  must be constant. The prediction is `build_weighted_nuwro(..., N_total)`, as `cmd_supplement` builds it.
- **Full H** = main + supp; sumw2 and nevt add. This is the frozen merge.
- **CH:** `x_CH = (12/13) x_C12 + (1/13) x_H` and `sumw2_CH = (12/13)² sumw2_C12 + (1/13)² sumw2_H`. `x_C12` is the
  frozen `nuwro_cv_xsec5d_full.npz` array as stored. Its rebuilt copy has to equal it bitwise (B2).
- **Outputs** under `$D/out/build/`: `nuwro_H_xsec5d_full.npz` and `nuwro_CH_xsec5d_full.npz` in the gen5d npz
  format, for reuse by MP-2, and `mp3b_fine_nuwro.npz`.

**Normalization: why the chain carries over to H unchanged.**
- **The frozen NuWro product** is `sum_bin w_e r_e / N_total`. The per-event weight `w_e` is NuWro's flux-averaged
  σ per target nucleon. There is no explicit /12 (`gen5d_flux_reweight.py:590-620`; `gen_to_xsec5d.extract_nuwro`;
  `nuwro_to_flat_5d.C:` "cm^2, per nucleon").
- **NuWro's free-target handling.** NuWro draws one target nucleon per event. For `p + n == 1` it sets `Eb = kf = 0`
  (`nucleus.cc:25-26`). It scales the ν–e (LEP) weight by `p/(p+n)` (`lepevent.cc:119`). For nucleus_p = 1 and
  nucleus_n = 0, "per nucleon" is therefore per proton, so the H product is per H nucleon, as the spec requires.
- **Probe evidence.** The probe's mean weight equals the sum of NuWro's own channel σ table (2.361e-38). Its ratio to
  C12, 0.642 per nucleon, is physically sensible.
- **No step uses a C12-specific constant.**
  - Event selection, r(E), N_total and the merge do not depend on the target.
  - The GENIE C12 graph enters only diagnostics (`range_limitation` and the normalization cross-check) and the
    sampling-test proxy (B3).
  - `nuwro_to_flat_5d.C` computes W with M_n for every generator and event. That is the definition of the observable,
    not a target constant (gen5d README deviation 3).
- **The ν–e events** (dyn 12) are counted in N_total and are not CC, as in the C12 product.
- The run also prints a per-nucleon σ_H/σ_C12 sanity value after the gates. It is not a gate.

**Eval** (`mp3b_eval.py`). It uses `s5p_joint` and `s5p_inference` copies that are byte-identical to `4f5a613f`,
with `__file__` asserted. It reads `design.json`, `V-s3v.npz` (sha256 `35979ef7…`) and `joint-evaluate.json`
(`b9604502…`).

## 4. Controls and gates, in run order (each runs only if every earlier one passed)

| # | what is computed | pass rule | on fail |
|---|---|---|---|
| C0 | `.par` of each H sample against the frozen production `work_nuwro_p1/nuwro_p1.root.par` (main) and `supp/nuwro/nuwro_supp.root.par` (supp) | every differing key is one of {random_seed, number_of_events, nucleus_p, nucleus_n, nucleus_target}, and the H card carries the SEEDS values and (1, 0, 0) | exit 2, no gate is evaluated |
| C1 | flat trees produced here from the frozen C12 p1 and supplement files, against `gen5d/nuwro_flat5d/nuwro_flat5d_p1.root` and `supp/nuwro/nuwro_supp_flat5d.root` | all 12 branches bitwise and nTotal equal | exit 2 |
| **B1** | over CC events of both H flats: dyn counts and hitnuc counts. Also NuWro's own `<out>.root.txt` channel table | no CC event with dyn 0 (QEL), 6 (COH) or 8 (MEC); the table shows events 0 and σ 0 for those channels; hitnuc = 2212 for every CC event | exit 3; no CH prediction |
| **B2** | the frozen NuWro product rebuilt with `cmd_reweight`'s NuWro statements (8 flat files, extract_nuwro with the old-flat parity, r(E), `build_weighted_nuwro`) and `cmd_supplement`'s (r constant), then merged | `<50 GeV` and full `xsec_flat` and `sumw2_flat` bitwise equal to `nuwro_cv_xsec5d.npz` (`f5231637…`) and `nuwro_cv_xsec5d_full.npz` (`475a2871…`), both with the frozen merge operands and as rebuilt main + rebuilt supp. nevt is reported. J-cell μ and Var also bitwise in the eval | exit 3 |
| **B3** | the closure the frozen build recorded for the C12 supplement (`cmd_supplement`), applied to the H supplement: flux file = phi_t × width bitwise; r constant to 1e-12; `gfr.sampling_test` in proxy mode on the frozen populations (all CC; RES/DIS; QEL/COH/MEC, which is empty for H and recorded as such) | every non-empty population has across-bin and within-bin p ≥ 1e-3 and no event outside the generation bins: the frozen rule, which the C12 supplement met at p = 0.21/0.99, 0.20/0.98, 0.71/0.62. **σ proxy:** GENIE's H1 tot_cc graph is PRIMARY; the literal C12 proxy is reported. The same test on the H main sample is the chain's own STOP rule (`cmd_reweight` raises on it) and also stops the study | exit 3 |
| **B4** | J cells (all 109): `(1/13) sqrt(U² sumw2_H)` against `(12/13) sqrt(U² sumw2_C12)` | ratio ≤ 1/3 in every cell. Reported: the worst cell, cells with no or few H events, and the event factor that would meet the bound | exit 4: STOP and report, no readout (the remedy factor is not fixed) |

- **The B3 statistic is the frozen one.** Before B3, the job reproduces the frozen C12 main and supplement
  sampling-model statistics field by field (χ², ndf, p, n, pass), so the statistic B3 applies is shown to be the
  frozen statistic. In preflight this matched exactly (§6).
- **Gate order.** B1–B3 read only event-level and E_ν information. The H fine arrays are built after B3, and nothing
  cell-level is computed before the B3 verdict. B4 reads only H variances. The readout starts after B4 passes and
  after the eval controls (§5).

## 5. Readout (after B4; DESCRIPTIVE, not a re-grade; beside A7)

### 5.1 Eval controls

These are checked first, and the job stops if any fails:
- J-cell μ and Var of the rebuild equal `s5p_joint.prediction` bitwise.
- `s5p_joint.test_null` for NuWro equals `joint-evaluate.json`'s NuWro entry in full: T, every variant's p, k,
  medians, SDs and implied size, claim, robust, and jitter p.
- The κ_robust M1 nulls reproduce the frozen robustness p.
- `holm_determined` and `holm` on the frozen family reproduce the frozen `decisions`, `decisions_robust_kappa` and
  `holm_point`.
- An identity replay (μ := μ_C12) returns the frozen T, claim p and decisions.
- Exact equality is required everywhere, except Clopper–Pearson interval ends, which may differ by ≤ 1e-12 relative
  (the last ulp of `beta.ppf`); any such path is listed.

### 5.2 Per-cell quantities and their scales

- **Per cell:** r_c = μ_CH/μ_C12 and its shape form; f_H = (1/13) U x_H / μ_CH; the MC error of r (delta method).
- **Δ = μ_CH − μ_C12 over σ_c, three readings:**
  - (a) the SD (ddof 1) over NuWro's frozen B = 1751 ensemble of the evaluated J-cell result. PRIMARY, as MP3-A
    reading (a).
  - (b) √diag W.
  - (c) the SD of f − (μ_C12 + ε).
  - Also the shape Δ/σ.
- **Norms of Δ:**
  - ΔᵀW⁻¹Δ, with the frozen W = V + diag Var μ_C12. PRIMARY.
  - The same with W_CH, and with V alone.
  - Three shape forms. The PRIMARY one uses the Jacobian at the data.
- **Regions:** J W and E_avail regions, and fine W bins inside the reported cells.

### 5.3 The T replay

**What is computed.** The replay is the frozen `s5p_joint.statistics` at the data with μ = μ_CH:
- under the frozen W (PRIMARY) and under W_CH;
- against NuWro's frozen null, all 5 declared variants (0.0, 0.5, 1.0, m1±2), with the claim p = the largest over
  the variants;
- with the κ_robust p as well;
- in null SDs: the change, and the margin over the null median;
- with jitter-p stability;
- with a diagnostic null re-evaluated under W_CH, labelled as not the frozen null.

**A7's decision rule, read from the code and re-measured bitwise in preflight.**
- `joint-evaluate.json` `decisions` comes from `s5p_inference.holm_determined`. It runs on the ten claim p (each the
  largest over the variants), ordered by p. Step i compares the exact Clopper–Pearson 95% interval of k/B with
  α/(m − i), α = 0.05.
- The outcome is "rejected" if the interval lies wholly below that threshold, "not rejected" if it lies wholly
  above, and "undetermined" if it straddles. The procedure stops at the first test that is not rejected.
- NuWro shape is last in the order (claim k = 1, B = 1751, p = 0.00114). Its threshold is therefore 0.05.

**Where the threshold sits.** "Rejected" holds for claim k ≤ k* = 69. Equivalently, it holds for
**T_shape > T_crit = 8672.55**, the max over the five variant nulls of the 70th-largest value.

| NuWro (frozen) | T_obs | null median | null SD | margin over median | T_crit (Holm position) | **margin to T_crit** |
|---|---:|---:|---:|---:|---:|---:|
| shape | 9660.01 | 7110.29 | 890.03 | 2.86 SD | 8672.55 (α/1 = 0.05, k* = 69) | **1.11 SD** |
| total | 7427.14 | 6323.86 | 174.29 | 6.33 SD | 6953.94 (α/10 = 0.005, k* = 3) | 2.71 SD |

**The brief's "≈ 2.8 null SD" is the margin over the null median.** The decision is closer than that: a drop in
T_shape of 987.5 (1.11 null SD) would change NuWro shape from "rejected" to "undetermined".

**How "would cross" is decided.** The full replay runs `holm_determined` over the frozen family with NuWro's two
claims replaced. "Would cross" means NuWro shape's decision is no longer "rejected". The frozen W replay is PRIMARY;
W_CH and κ_robust are reported, and any change in the decisions of the ten tests is listed. If it crosses, that goes
in the first line of the final message.

## 6. Preflight (login node `login13`, read-only, run 2026-10-19)

**Build preflight** (21.6 s wall, file-system outputs 0). Each check passed:
- `card_control`: the probe H `.par` against production passes with exactly the five allowed keys. In the local
  tests a wrong seed, or the C12 card presented as H, is refused.
- `converter_control` passes (self-comparison).
- `gate_b1` on the probe gives CC dyn {2: 7837, 4: 12156} and hitnuc {2212: 19993}, and passes.
- **`rebuild_c12` (the B2 path):** the main, full and full-from-rebuilt-main xsec, sumw2 and nevt are all
  **bitwise**. The frozen sampling statistics (main and supplement) are **reproduced identically**, and the eight
  input flats match the frozen meta sha256.
- `h_sample` runs on the probe H (main path) and on the frozen C12 supplement (supp path, H1 proxy) as code
  exercises. Their verdicts were not printed.

**Eval preflight** (28.5 s, outputs 0, numpy 1.26.4, scipy 1.16.3). The NuWro `test_null` matches the frozen entry
**bitwise**. The robust nulls, the Holm decisions (both kinds) and `holm_point` all match **bitwise**. The identity
replay matches as well.

**Not exercised:**
- the ROOT macro's run inside the job, which is the probe's command;
- the NuWro runs in parallel;
- the readout on a real H product. Keeping it unrun keeps H cell-level numbers unseen until after the gates.

## 7. Staged files (`$D`, staged by tar from the worktree; `git hash-object` identical on both sides)

| staged | blob | source |
|---|---|---|
| `code/mp3b_job.sh` | `aebcff0e` | worktree `measurement-paper/phase1/mp3b/` |
| `code/mp3b_build.py` | `218ba8e6` | 〃 |
| `code/mp3b_eval.py` | `91a663db` | 〃 |
| `code/mp3b_preflight.py` | `48c210ed` | 〃 |
| `code/SEEDS.txt` | `93476d64` | 〃 |
| `code/gen5d_flux_reweight.py` | `02700d40` (sha256 `89863318…` = `gen5d_fluxfix/code/`) | `3d-unfolding/genie/` |
| `code/gen5d_flux_supplement.py` | `b8251ca5` (`ff7a2d0e…` = `gen5d_fluxfix/code/`) | 〃 |
| `code/s5p_joint.py`, `s5p_inference.py`, `s5p_stage1_inspect.py` | `51d3424f`, `f42e0e20`, `b6aee05d` (= `4f5a613f`) | `nd-unfolding/` |
| `inputs/design.json`, `s5c_contract.json`, `joint-evaluate.json` | `5c30ba87`, `28125d96`, `daf92651` | `docs/orchestration/state/s5p/prod/`, `s5c/`, `s5p/stage7/joint/` |

**Used in place, read-only** (sha256 recorded by the job in `gen/input_sha256.txt`):
- `gen5d/code/nuwro_to_flat_5d.C` (`01e89fb2…`);
- `3d-unfolding/genie/setup_nuwro.sh` (`15007d6f…`);
- `flux_mefhc_numu_nuwro.root` (`1d016921…`);
- `supp/flux_phi_t_50_100.root` (`6fd4a62f…`);
- the frozen NuWro products and flat files;
- NuWro's 1751 calibration products;
- `V-s3v.npz`, the D16 and M1 shift files.

## 8. Charge estimate

- **Wall time.** The probe generated 20k H events, with 50k test events, in 30.5 s.
  - H main, 250k, should take 4–8 min.
  - H supp, 25k, about 1 min.
  - The C1 re-conversions take 1–2 min and run in parallel.
  - Build plus eval take about 1 min (preflight 22 s + 28 s).
  - **Expected wall: 10–15 min.**
- **Charge.** On `shared` with 8 CPUs (billing 8, as MP3-A): **≈ 0.005–0.008 CPU node-h**. The 1:30:00 limit caps
  it at 0.047. The brief allows ≤ 1 and PLAN ≤ 0.6 for generation plus the chain. 0 GPU.
- **Storage.** About 0.4 GB on pscratch (two NuWro root files, flats, products). Nothing goes to CFS.

## 9. Decisions flagged

Each is computed both ways where it matters, and labelled.
1. **B3 σ proxy.** The PRIMARY proxy is GENIE's H1 graph, the target-matched analogue of the frozen C12 proxy. The
   literal C12 proxy is reported but does not gate. The free poly3(log E) factor absorbs most of the difference.
2. **The B3-style test is also applied to the H main sample.** It is the frozen chain's own STOP rule
   (`cmd_reweight`).
3. **The replay with W_CH** is compared with the frozen null, whose metric is W_C12. A diagnostic null re-evaluated
   with W_CH is shown beside it and labelled as not the frozen null.
4. **T_crit is computed at NuWro's frozen Holm positions.** The full `holm_determined` replay is authoritative,
   since the positions can move.
5. **B4 uses the gen5d sumw2 convention** (normalization constants treated as exact). A cell with no H event has an
   estimated H error of 0; such cells are listed.
6. **The combination uses the frozen C12 arrays.** These are bitwise the rebuild if B2 passes.
