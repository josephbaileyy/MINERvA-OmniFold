# 2D closeout Stage C pilot: package DESIGN (P0, P1, P2, P2-G2, P3)

**CITABLE FOR:**
- the frozen pilot package: every check, envelope and threshold, every job and its walltime, the namespace,
  the launch order and the charge gate, fixed before any pilot job;
- the P2-G2 universe choice (`Flux:23`) and the Flux re-declarations, computed from inputs before any run.

**NOT CITABLE FOR:**
- any pilot result. Results go in `REPORT.md` after the jobs;
- production (S1–S5), a G2 repair, a July rebuild, adoption, claims or publication;
- compute authority. Jobs may be submitted only after the director's binding addendum to
  [`AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md`](../../../../AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md)
  is on `origin/main`.

| field | content |
|---|---|
| `Owner` | 2D closeout executor (2d closer), directed by the paper-tighten lane under [`AUTHORIZATION-20261012-2d-closeout-delegation.md`](../../../../AUTHORIZATION-20261012-2d-closeout-delegation.md) |
| `Grant` | [`AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md`](../../../../AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md) (file sha256 `136d6b49…`): ≤ 12.9 charged node-h, window to 2026-10-27; Stage B exit [`AUTHORIZATION-20261013-2d-closeout-stageB-exit.md`](../../../../AUTHORIZATION-20261013-2d-closeout-stageB-exit.md) (`bd4d34ab…`): EXIT CONDITIONAL on K1 and K2 |
| `Branch` / `Base` | `closeout/stagec-pilot-20261013` / `origin/main` `ca1bb536` |
| `Producer pin` | production driver `2d-unfolding/unfold_2d_omnifold_unbinned.py` sha256 `74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56` (`main` `ec2088a6`, PR #108, comment-only); helper `omnifold.py` `e96234124a31…` |
| `Namespace` | `/pscratch/sd/j/josephrb/2d-closeout-stageC-pilot-20261013/` (`repo/` the deployed package, `out/<job name>/`, `logs/`, `results/`, `preflight/`, `retries/`, `tmp/`) |
| `Manifest` | [`manifest.json`](manifest.json): every package file and every external pin with its sha256; its own digest is what the addendum binds |
| `Terminal outcomes` | P0 PASS/FAIL; P1 checks PASS/FAIL, σ ratio MEASURED; **K1** (P2) PASS/FAIL; **K2** (P2-G2) MATERIAL / NOT RESOLVED ABOVE TRAINER NOISE / NOT MATERIAL / INCONCLUSIVE; P3 MEASURED/INCONCLUSIVE |

## 1. What is frozen, and when

Everything in this file, `jobs.tsv`, the scripts and `p2g2/select_flux.json` is committed and verified before
any pilot job. No threshold, envelope, universe, replica count or job is changed after a pilot result is seen;
a change needs the director's decision recorded before the data it would affect (plan: "do not loosen the
tolerance after seeing a failure"). Login-node smoke tests on existing products (not pilot jobs) were run during
packaging; they are listed in §11.

## 2. Pins and inputs

| object | path | sha256 | checked |
|---|---|---|---|
| production driver | `$NS/repo/2d-unfolding/unfold_2d_omnifold_unbinned.py` | `74a4ed69…1167d56` | every job |
| helper (the driver's hard-coded import) | `/pscratch/…/MINERvA-OmniFold/unbinned_unfolding/python/omnifold.py` | `e96234124a31…` | every job |
| P1 diagnostic copy | `$NS/repo/2d-unfolding/driver_p1.py` (from `p1/driver_p1.py`) | see `manifest.json` | P1 jobs |
| P2-G2 diagnostic copy | `$NS/repo/2d-unfolding/driver_g2.py` (from `p2g2/driver_g2.py`) | `eb258cad…` | P2-G2 on jobs |
| miss-row override builder | `p2g2/build_miss_override.py` (P5's, unchanged) | `7f346e1a…` | P2-G2 on (seed 42) |
| CV omnifile (L0's input) | CFS `two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root` | `43f8cc16…` | P0, P1 jobs |
| flux MC file | `2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root` | `d40aea69…` | every job |
| flux universe file | `2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root`, passed **absolute** | `5eecae84…` | universe jobs |
| universe omnifile | `2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root` (171,117,087,867 B) | `220c479e…` (Stage B) | hashed once on a DTN by `preflight_uomni.sh` before B1; each universe job checks size, mtime and inode against that record |
| active lateral files | CFS `2d-closeout-stageC-inputs-20261012/active_universe_5d_standard_merged/` | their `SHA256SUMS` (SHA256 MATCH 2026-10-12) | each P3 job hashes its file |
| L0 reference | `/pscratch/…/xr-linux-20261011/L0/a1/XR-L0.root` | `75138024…` | analysis |
| July products | `uq/purity_newomni/…_pn_uni_<U>.root` (CV, NormDISCC_0, MaRES_0, Flux_0…99, Muon_Energy_MINOS_0/1, BeamAngleX_0/1) | in `analyze_pilot.py`, `select_flux.json` | analysis |
| `E_U` (cell mask) | `uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` | `4f5a1b6d…` | analysis |
| ML covariance (σ_ML) | `uq/seedscan_lgbm_ml/uq_covariance_ml.root` | `3b6b48ec…` | analysis |
| 1e-8 instrument | `state/next-preparation-20261009/xr-linux/xr/xr_compare.py`, `manifest/references.json` | `9e59c590…`, `af7d5a19…` | analysis |

The CV omnifile is not in the Stage C CFS copy; its own CFS copy (with `SHA256SUMS`, mode 0440) is used. The
universe omnifile and the July products exist only on `/pscratch`; they are hashed as above.

**Environment** (every job): `setup_salloc_env.sh` sourced before any `set -u`; `OMP_NUM_THREADS=64`,
`MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1`, `LOKY_MAX_CPU_COUNT` unset. LightGBM's thread count follows the CPU
affinity through joblib, so the CPU count, not `OMP_NUM_THREADS`, sets it: P0 and P1 request 64 CPUs (L0's
configuration); universe and lateral jobs request 128 (P5's and July's thread count, where P5 reproduced July
`MaRES_0` to 2.4e-13).

## 3. P0: producer bridge

| job | command (production driver 74a4ed69, CV omnifile, `--iters 5 --use-weights --estimator lgbm --bkg-mode purity --seed 42`) |
|---|---|
| `2dc_C_P0_default` | `--branch-select all` |
| `2dc_C_P0_derived` | `--branch-select derived` |

Checks (`analyze_pilot.py p0`), with the frozen XR instrument `xr_compare.compare()`:
- **P0-1:** `P0_default` vs `XR-L0.root` under the frozen 1e-8 criterion (max |x_new/x_ref − 1| ≤ 1e-8 over the
  205 frozen reported cells and their area-weighted integral; cell sets must match, else INCONCLUSIVE).
- **P0-2:** `P0_derived` vs `P0_default` under the same criterion. On the CV file `derived` deselects nothing
  the loaders read, so P0-2 is a plumbing check, not the first real-file equality (that is P2-EQ, §5).
- **Provenance:** `driverSha256` = `74a4ed69…`, `omnifoldHelperSha256` = `e9623412…`, and the runConfig values
  above.

**P0 = PASS** iff P0-1 and P0-2 PASS and provenance holds; **FAIL** if either comparison FAILs; otherwise
INCONCLUSIVE. Anything but PASS stops the pilot (record §3): no later batch is admitted (`launch.py` reads
`results/p0.json`).

## 4. Order, batches and the charge gate

**Order.** B0 (P0) runs first and alone. Every later batch requires `results/p0.json` = PASS.

| batch | jobs | precondition (checked by `launch.py`) |
|---|---|---|
| B0 | `P0_default`, `P0_derived` | none |
| B1 | `P2_NormDISCC0`, `P2_MaRES0`, `P2_Flux23`, `P2_MINOS0`, `P2_MINOS0def`, `P1_unit` | P0 PASS; universe preflight recorded |
| B2 | `G2_on` | P0 PASS; `out/2dc_C_P2_Flux23/xsec.root` exists (run *a* of P2-G2) |
| B3 (conditional) | `G2_off_s43`, `G2_on_s43` | P0 PASS; `results/g2_s42.json` routes MATERIAL or NOT RESOLVED ABOVE TRAINER NOISE |
| B4 | `P3_BeamAngleX0`, `P3_MINOS0` | P0 PASS |
| B5–B8 | P1 replicas, 15 jobs each: bootstrap seeds 1–5, 6–10, 11–15, 16–20, each × the three arms `fixed`, `joint`, `bkg` | P0 PASS; `results/p1_unit.json` b ≡ 1 control PASS |

Batches may overlap in time; the gate makes that safe. The K items (B1–B3) come before P1's replicas so that,
if costs run high, the gate's refusal falls on a P1 batch (a stop-and-report) rather than on K2.

**GATE** (director, 2026-10-13; `launch.py`). Before each batch:

> charges of COMPLETED (terminal) `2dc_C_*` jobs from `sacct` (ElapsedRaw × billing / 256)
> \+ the FULL enforced worst case of every `2dc_C_*` job still PENDING or RUNNING (billing × TimeLimit / 256)
> \+ the batch's enforced worst case
> ≤ **12.9** charged node-h. Otherwise **stop and report to the director**.

- A running job's partial charge is not its liability; in-flight jobs count at their full cap, so overlapping
  batches cannot jointly exceed the ceiling.
- Every `sacct` row since 2026-10-13 counts: cancelled, failed and timed-out jobs, retries and controls.
- An unreadable `sacct` is a refusal, never zero.
- The same gate is P2-G2's seed-43 pre-declared actual-charge check (§6).
- A refusal is a stop-and-report. It never shrinks a declared batch: P1 stays 20 + 20 + 20 unless the director
  records otherwise before data.

**Enforced worst case per job** (billing × cap / 256; shared QOS, billing = CPUs; [`jobs.tsv`](jobs.tsv)):

| jobs | CPUs | cap | per job | count | subtotal |
|---|---|---|---|---|---|
| `P0_default`, `P0_derived` | 64 | 00:25:00 | 0.1042 | 2 | 0.2083 |
| `P2_NormDISCC0`, `P2_MaRES0`, `P2_Flux23`, `P2_MINOS0` | 128 | 00:30:00 | 0.2500 | 4 | 1.0000 |
| `P2_MINOS0def` | 128 | 01:10:00 | 0.5833 | 1 | 0.5833 |
| `P1_unit` | 64 | 00:32:00 | 0.1333 | 1 | 0.1333 |
| `G2_on` | 128 | 00:50:00 | 0.4167 | 1 | 0.4167 |
| `G2_off_s43` (conditional) | 128 | 00:30:00 | 0.2500 | 1 | 0.2500 |
| `G2_on_s43` (conditional) | 128 | 00:50:00 | 0.4167 | 1 | 0.4167 |
| `P3_BeamAngleX0`, `P3_MINOS0` | 128 | 00:45:00 | 0.3750 | 2 | 0.7500 |
| `P1_{fixed,joint,bkg}_{01..20}` | 64 | 00:32:00 | 0.1333 | 60 | 8.0000 |
| **all 73 jobs** | | | | | **11.7583** (11.0917 without the conditional pair) |

**Worked example** (`python launch.py simulate median|cap`; batches in order, each after the previous ends):

| batch | gate at measured medians | charged | gate at caps | charged |
|---|---|---|---|---|
| B0 | 0.0000 + 0.2083 = 0.2083 OK | 0.1161 | 0.0000 + 0.2083 = 0.2083 OK | 0.2083 |
| B1 | 0.1161 + 1.7167 = 1.8328 OK | 0.9149 | 0.2083 + 1.7167 = 1.9250 OK | 1.7167 |
| B2 | 1.0310 + 0.4167 = 1.4477 OK | 0.2360 | 1.9250 + 0.4167 = 2.3417 OK | 0.4167 |
| B3 | 1.2670 + 0.6667 = 1.9337 OK | 0.3617 | 2.3417 + 0.6667 = 3.0083 OK | 0.6667 |
| B4 | 1.6287 + 0.7500 = 2.3787 OK | 0.3694 | 3.0083 + 0.7500 = 3.7583 OK | 0.7500 |
| B5 | 1.9981 + 2.0000 = 3.9981 OK | 0.8740 | 3.7583 + 2.0000 = 5.7583 OK | 2.0000 |
| B6 | 2.8721 + 2.0000 = 4.8721 OK | 0.8740 | 5.7583 + 2.0000 = 7.7583 OK | 2.0000 |
| B7 | 3.7460 + 2.0000 = 5.7460 OK | 0.8740 | 7.7583 + 2.0000 = 9.7583 OK | 2.0000 |
| B8 | 4.6200 + 2.0000 = 6.6200 OK | 0.8740 | 9.7583 + 2.0000 = 11.7583 OK | 2.0000 |
| **total** | | **5.494** (7.41 unused) | | **11.758** (1.142 unused) |

Medians used: P0 836 s (L0); P2 derived 905 s and G2 off 905 s (P5 off runs 776/1,034 s); P2 default 2,548 s
(July sweep median); G2 on 1,699 s (P5 on runs 1,470/1,928 s); P3 1,330 s (projection, §7); P1 839 s (VL170
median). Overlapping batches move charge from "completed" to "in-flight at cap", which is never smaller, so the
no-overlap walk is the lower edge of what the gate sees and the cap walk is its upper edge.

**Where the gate first refuses.** With every job at its cap and no retries, the full pilot, including the
conditional pair, fits with 1.142 node-h unused: the gate never refuses. A refusal therefore needs walltime
retries (§9). The first batch it would refuse is **B8** (P1 seeds 16–20), if retries before it have added more
than 1.142 node-h of caps, for example nine P1 retries at 0.1333 each, or three P3 retries at 0.375 plus one P1
retry. Without the conditional pair the margin at caps is 1.808.

## 5. P2 and K1: the July bridge

**Jobs** (production driver; universe omnifile; absolute `--flux-universe-file`; seed 42; 128 CPUs):

| job | universe | path | reference (July, same options, uncommitted revision) |
|---|---|---|---|
| `P2_NormDISCC0` | `NormDISCC:0` (null knob) | derived | `…_pn_uni_NormDISCC_0.root` `5819b46b…` |
| `P2_MaRES0` | `MaRES:0` | derived | `…_MaRES_0.root` `80e1e04e…` |
| `P2_Flux23` | `Flux:23` (also P2-G2's run *a*, §6) | derived | `…_Flux_23.root` `eb8414af…` |
| `P2_MINOS0` | `Muon_Energy_MINOS:0` | derived | `…_Muon_Energy_MINOS_0.root` `09828330…` |
| `P2_MINOS0def` | `Muon_Energy_MINOS:0` | `--branch-select all` | the same |

**K1 envelope** (frozen here, before P2 runs; Stage B §2.5: "no-op universes to the frozen 1e-8; others to an
envelope declared before P2 runs"):
- `NormDISCC_0`: the frozen 1e-8 criterion (XR instrument) against July `NormDISCC_0`.
- `MaRES_0`, `Flux_23`, `Muon_Energy_MINOS_0` (derived) and `Muon_Energy_MINOS_0` (default):
  **max over the 205 cells of |P2 − July| / σ_ML ≤ 0.01**, with σ_ML = √diag of the pinned ML covariance; cell
  sets must match (else INCONCLUSIVE). The 1e-8 verdict is also reported for each, descriptively.
- **K1 = PASS** iff all five comparisons PASS with provenance (driver `74a4ed69…`, helper, universe, seed 42,
  path, absolute flux file); **FAIL** iff all are evaluable and any FAILs; **INCONCLUSIVE** otherwise. Only PASS
  qualifies July (record: production only if K1 PASSES).

**Why 0.01 σ_ML.** K1 asks whether the July products are what the committed producer gives on the same inputs.
- Same inputs and seed give deterministic output: P5's run *a* (committed driver, derived path, 128 CPUs)
  reproduced July `MaRES_0` (uncommitted revision, default path) to 2.4e-13 relative, 2.2e-10 σ_ML.
- A change of trainer path moves cells by O(σ_ML): seed 43 vs seed 42 moved them by up to 8.7 σ_ML (P5).
- 0.01 σ_ML (median σ_ML/CV = 1.66e-3, so about 1.7e-5 relative) sits about eight orders above the measured
  agreement and about three below a trainer-path change, so a pass cannot come from lack of resolution (plan:
  "an inability to resolve a proposed tolerance is NO POWER, not PASS"), and floating-point differences that are
  immaterial against trainer noise do not fail it. The 1e-8 criterion is kept for the null knob, as Stage B wrote.

**K1 FAIL** (record §3): that line stops, the cause is diagnosed (which universes, by how much in σ_ML and
σ_band, the driver and helper changes since July, the background-universe branch), and reported to the
director. No rebuild is pre-committed; a July rebuild needs its own grant.

**P2-EQ, the first real-file equality of the selective read** (selective-I/O delivery REPORT §11):
`P2_MINOS0` (derived) vs `P2_MINOS0def` (all) under the frozen 1e-8 criterion. PASS clears `--branch-select
derived` for universe runs. FAIL is a failed identity (record §3): the derived line stops and is reported; K1's
derived comparisons are then not used for qualification until the director rules. P3 does not depend on P2-EQ
(it runs the default path, §7).

**Null check, MEASURED:** `P2_NormDISCC0` vs the July CV (`b8457af7…`), 1e-8 verdict and σ_ML shift, reported
with no pass/fail (Stage B §7: the null knob "reproduces July and CV"). Smoke on existing products: July
`NormDISCC_0` vs July CV agrees to 1e-8 (max 4.0e-10 σ_ML).

## 6. P2-G2 and K2: G2 in a Flux universe

**Selection** ([`p2g2/select_flux.py`](p2g2/select_flux.py) → [`p2g2/select_flux.json`](p2g2/select_flux.json),
sha256 `35ce6226…`, from inputs only, 2026-10-13, before any pilot job). The rule is the record's: the Flux
universe with the largest median |c_off − 1| over the 205 reported cells, c_off = `hOFCompleteness2D` of its
July product. Result: **`Flux:23`**, median 1.775%, **max 11.82%**. (A first run, `e20cfd48…`, keyed its inputs by
file name, which the repository's receipt gate rejects; the committed re-run keys them by role and is otherwise
value-identical: choice, ranking, cells, σ_band and σ_ML compared equal. The first output is kept on NERSC under
`select/superseded/`.)

| rank by median | universe | median \|c_off − 1\| | max |
|---|---|---|---|
| 1 | **Flux_23** | **1.775%** | 11.82% |
| 2 | Flux_83 | 1.743% | 8.31% |
| 3 | Flux_92 | 1.594% | 8.22% |
| 4 | Flux_95 | 1.575% | 10.97% |
| 5 | Flux_8 | 1.561% | 9.99% |

By max alone the order would start at Flux_91 (18.2%, median 0.28%); the record's measure is the median.
Flux_23's constraint weight is 5.4e-5 (mean 2.11, n_eff 19.06), so it barely enters the adopted weighted band:
K2 measures the size of the G2 mechanism where it is largest, not that universe's weight in the band.

**Same universe as P2's Flux case: yes.** Stage B §7 asks P2 for "one large Flux universe". `Flux_23` moves the
result by 8.4% (median over cells) from the July CV and has the largest G2 exposure, so one choice serves both,
and **`P2_Flux23` is P2-G2's run *a*** (production driver, seed 42, derived path, the same options as run *b*
apart from `--out` and `--miss-weight-override`, which G-p checks).

**Code** (pilot copy of the P5 package, named `2dc_C_G2_*`, pinned to `74a4ed69…`):
- [`p2g2/driver_g2.py`](p2g2/driver_g2.py) (`eb258cad…`) is the production driver at `74a4ed69…` with P5's
  reviewed patch applied; [`p2g2/patch.diff`](p2g2/patch.diff)'s body is byte-identical to P5's, and
  `driver_g2.py` differs from P5's `driver_p5.py` only in the corrected comment line 30.
- [`p2g2/build_miss_override.py`](p2g2/build_miss_override.py) is P5's (`7f346e1a…`), run with `--universe
  Flux:23`.
- [`p2g2/analyze_g2.py`](p2g2/analyze_g2.py) is `analyze_p5.py` with only the substitutions below; the routing
  and seed-43 logic are unchanged.

**Re-declared for `Flux:23`, frozen here:**

| quantity | P5 (`MaRES_0`) | P2-G2 (`Flux:23`) |
|---|---|---|
| σ_band | \|j0 − j1\|/2 (two-universe band) | per-cell weighted std of the July `Flux_0…99` `hXSec2D` about their weighted mean, with the ν-e + IMD constraint weights (the C04-repaired construction adopted as VL175); median σ_band/CV 3.75% |
| floor | σ_band ≥ 1e-3·CV: 188 of 205 cells | same rule: **205 of 205** cells |
| n_override (G-a) | 8,999,007 | 8,999,007: `nTruthOnlyMisses` of the omnifile, independent of the universe |
| G-c reference | July `MaRES_0` completeness, ≤ 1e-12 relative | July `Flux_23` completeness (`eb8414af…`), ≤ 1e-12 relative |
| G-b | max \|c_b − 1\| ≤ 1e-9 | unchanged |
| G-p | drivers `6be77c51…` / `f71b5759…` | drivers `74a4ed69…` / `eb258cad…`; helper `e9623412…` |
| new gates | — | `select_pinned` (select_flux.json `35ce6226…`, July Flux_23 `eb8414af…`); `select_matches` (universe and cells); G-u (both runConfigs: universe `Flux:23`, the absolute flux file) |
| bridge | \|a − July MaRES_0\|/σ_band | \|a − July Flux_23\|/σ_band |

**r1/r3 thresholds: unchanged at 0.10, 0.30 and 2** (record §2). Flux-specific consideration, written before
data: with this σ_band, σ_ML/σ_band has median 0.043 (max 0.29), so seed noise alone gives median r1 ≈ 0.04,
under the 0.10 clause, while a 3σ_ML excursion in the cell with the largest ratio gives max r1 ≈ 0.9, over the
0.30 clause. The r1 rule can therefore still hold on noise alone, and the routing then rests on r3 (noise-only
median ≈ 0.95), exactly as in P5. That is P5's logic, not a reason to change a threshold, so none is changed.

**Routing** (P5 DESIGN §6–7): r1 rule = median r1 > 0.10 over 205 cells, or max r1 > 0.30 over the floored
cells; MATERIAL iff the r1 rule holds and median r3 > 2; NOT RESOLVED ABOVE TRAINER NOISE iff it holds and median
r3 ≤ 2; NOT MATERIAL otherwise. A failed gate gives INCONCLUSIVE.

**Seed-43 confirmation** (conditional, P5 DESIGN §7). If seed 42 routes MATERIAL or NOT RESOLVED, B3 runs
`G2_off_s43` and `G2_on_s43` (seed 43, the seed-42 override sha-checked), **launched on the gate of §4 without a
further go-ahead**; the gate figures are reported. Then `analyze_g2.py … --tag _s43 --confirm`: CONFIRMED iff both
pairs are MEASURED and Pearson(z43, z42) ≥ 0.5 over the floored cells (z = d/σ_ML); final routing per P5's frozen
table. **The frozen row applies:** a failed, timed-out-twice or not-MEASURED pair gives INCONCLUSIVE, and K2 is then
INCONCLUSIVE (not seed-42-only).

**K2** = the final routing. NOT MATERIAL or NOT RESOLVED ABOVE TRAINER NOISE passes. **MATERIAL or INCONCLUSIVE does
not pass**: it goes to the director and from the director to Joseph before any production grant.

## 7. P3: laterals from the active files

| job | input (CFS, read-only, hashed in the job against `SHA256SUMS`) |
|---|---|
| `P3_BeamAngleX0` | `runEventLoopOmniFold_5D_MEFHC_active_BeamAngleX_0.root` (53,845,911,012 B, `38b9fc30…`) |
| `P3_MINOS0` | `runEventLoopOmniFold_5D_MEFHC_active_Muon_Energy_MINOS_0.root` (53,841,190,691 B, `f105f681…`) |

Command: the production driver on the active file with the L0 options, seed 42, **no `--universe`** (the
active file already is the universe: its plain branches carry the universe values, `hasActiveUniverse=1`), and
**`--branch-select all`**, so P3 does not depend on P2-EQ and runs the production-equivalent path.

**Outcome:** MEASURED (job COMPLETED, provenance holds), with the u_A cost and peak memory from `sacct`, or
INCONCLUSIVE. Comparisons are reported with **no pass/fail** (none is written for P3):
- `P3_MINOS0` vs `P2_MINOS0def` (same driver and path, dump-mode input) and vs July `Muon_Energy_MINOS_0`, in σ_ML
  and in σ_band = |MINOS_0 − MINOS_1|/2 (July pair). The active file's signal-tree truth weights differ from the
  dump on 8,525,527 reco-failing rows (the G2 mechanism), so equality is not expected.
- `P3_BeamAngleX0` vs July `BeamAngleX_0` (dump mode, not qualified, Stage B §2.7), in the same units; this is the
  first unfolded measurement of the beam-angle effect.

R4's closure reads (nine files) stay a production precondition; they are login-node reads, not P3 compute.

## 8. P1: statistical streams

Joseph's R5 (decision `3921dec4`): a three-stream seed-42 bootstrap, purity recomputed from the resampled data
and background. P1 measures its mechanism and cost; it is not a precision measurement (Stage B §7: with 20
replicas a per-cell σ ratio carries ≈ 16% unpaired error, so only the paired design can resolve the expected
≈ 3% median change). Details, judgment calls and test evidence: [`p1/README.md`](p1/README.md).

**Code.** [`p1/driver_p1.py`](p1/driver_p1.py) (`3056e625…`) is the production driver at `74a4ed69…` plus
[`p1/patch.diff`](p1/patch.diff) (12 hunks, +113/−7, mostly comments and help). With the new options off it is
bitwise the production path (test C1). It refuses `--closure`, the negweight modes and `--universe` with the new
options.
- `--bootstrap-streams three`: data (`default_rng(s)`), signal MC (`default_rng(s + 10⁷)`), both unchanged, plus
  background rows: `b_bkg = default_rng(s + 2·10⁷).poisson(1, 658,227)`, drawn over every `mc_background` entry
  before any selection. Arms are therefore paired by bootstrap seed.
- `--bootstrap-streams bkg`: the same draws, then data and MC factors set to 1 (so the streams stay identical
  across arms).
- Purity is recomputed from D\* (Σ b_data per reco cell) and B\* (Σ b_bkg·w·pot over the background loader's
  recorded rows, overflow rows included) through the production `build_measured_training_2d`, then multiplied by
  b_data as production does. D\*, B\* and the new training target are written under new names
  (`hDataRecoStar2D`, `hBkgRecoStar2D`, `hMeasTrainStar2D`) with a `p1Streams` record; production histogram names
  keep their un-resampled content. `n_fakes == 0` is asserted on the P1 path.
- `--unit-factors` (test only): all three factor vectors set to 1 through the new path: the b ≡ 1 control.

**Arms** (all on the CV omnifile with L0's argv and `--seed 42`):

| arm | driver | options | jobs |
|---|---|---|---|
| `fixed` | production `74a4ed69…` | `--bootstrap-seed N` (streams `both`, fixed purity: the VL170 law at seed 42) | `P1_fixed_01…20` |
| `joint` | `driver_p1.py` | `--bootstrap-seed N --bootstrap-streams three` | `P1_joint_01…20` |
| `bkg` | `driver_p1.py` | `--bootstrap-seed N --bootstrap-streams bkg` | `P1_bkg_01…20` |
| control | `driver_p1.py` | `--bootstrap-seed 1 --bootstrap-streams three --unit-factors` | `P1_unit` |

VL170 ran at GBDT seed 1, so the `fixed` arm is a new realization of the VL170 law at seed 42, not VL170 itself.

**Declared checks** (thresholds frozen here):

| check | where | rule | outcome |
|---|---|---|---|
| no-op, loader and `main()` level | login node, done in packaging (`p1/test_noop.py`, `test_rows_mapping.py`) | C1 options off bitwise = production; C2 `three --unit-factors` bitwise = central; C3 `bkg` changes only B\*, purity, training target and measured weights; C4 data/MC factors equal production's `both` | **PASS** (evidence in `p1/evidence/`) |
| **b ≡ 1 run-level control** | `P1_unit`, before any replica batch | the unit run vs `XR-L0.root` under the frozen 1e-8 criterion (XR instrument), with provenance | PASS/FAIL. A FAIL is a failed no-op control: P1 stops (record §3) |
| **bkg-only reco variance = Σw² of B** | login node, no unfold (`p1/bkgvar_check.py`), done in packaging | N = 2000 draws; per reco cell z_c = (s²_c − Σw²_c)/SE_c, SE_c = Σw²_c·√((2 + κ_c)/N), κ_c = Σw⁴_c/(Σw²_c)²; PASS iff max\|z_c\| ≤ 5 and pooled \|Σz_c/√n\| ≤ 3 | **PASS**: 205 cells, max\|z\| 3.15, pooled z 0.77 |
| paired σ ratios | `p1/analyze_p1.py` after B5–B8 | σ_joint/σ_fixed and σ_bkg/σ_fixed per reported cell (ddof 1), median over cells with a leave-one-replica-out jackknife SE (pairs by bootstrap seed) | **MEASURED**, no pass/fail |

Each replica is gated on its provenance (driver digest, runConfig seed 42, bootstrap seed, streams,
`unit_factors`, one shared omnifile and MC file, `p1Streams`); an arm with a missing or mismatched replica is
INCONCLUSIVE. The 20 + 20 + 20 counts are fixed (§4).

## 9. Walltimes, retries and failures

| job | projection basis (measured) | projection | cap = 1.5 × projection, rounded up |
|---|---|---|---|
| P0 | max u_CV 948 s (SB1 C) + 30 s hashing | 978 s | 1,467 s → **00:25:00** |
| P1 (all 61) | VL170 replica p99 1,267 s (300 replicas: median 839, p95 1,161, max 1,900) | 1,267 s | 1,901 s → **00:32:00** (also covers the observed max) |
| P2 derived, G2 off | max P5 off run 1,034 s | 1,034 s | 1,551 s → **00:30:00** |
| P2 default | max July sweep task 2,751 s | 2,751 s | 4,127 s → **01:10:00** |
| G2 on | max P5 on run 1,928 s (includes the override build) | 1,928 s | 2,892 s → **00:50:00** |
| P3 | max u_CV 948 s + full read of 50.1 GiB at the July sweep's worst rate, (2,751 − 778) s / 159.5 GiB = 12.4 s/GiB (621 s), + in-job hash of 54 GB at ≥ 0.4 GB/s (135 s) | 1,704 s | 2,556 s → **00:45:00** |

Every cap is under 12 h. P4's lesson (Stage B diagnostics §4.1): per-file smoke timings underestimated by 6–10×, so every basis here is a measured job of the same kind.

**Retries** (record §3). One walltime retry per job, at 1.5 × a projection re-measured from that job's own
partial progress (< 12 h), written to `retries/<name>.time` and submitted with `launch.py submit --retry <name>
--time <cap>` through the gate; partial output is moved, sha-verified, to `out/<name>.failed-<jobid>` first. An
out-of-memory kill is a diagnosed resource cause: one retry, on a full regular node if the shared allocation was
the cause, through the gate at that node's cap. Any other failure needs a diagnosed infrastructure cause. A
scientific result is never a reason to retry. A second failure is INCONCLUSIVE.

**Stops** (record §3): a P0 FAIL, a failed no-op control (P1 b ≡ 1), a failed identity (P2-EQ), a K1 FAIL, or a
gate refusal stops that line of work; diagnose and report to the director. No replacement product is built.

## 10. Deployment and launch (after the binding addendum only)

1. `git archive <package commit>` → `$NS/repo/` (`COPYFILE_DISABLE=1`); copy `p1/driver_p1.py` and
   `p2g2/driver_g2.py` into `$NS/repo/2d-unfolding/`; check every file against `manifest.json`.
2. `preflight_uomni.sh` on a data-transfer node (before B1): hash the universe omnifile, record its stat.
3. `python launch.py submit B0`; after the jobs end, `analyze_pilot.py p0 results/p0.json`.
4. On P0 PASS: B1; `analyze_pilot.py p2 results/p2.json`; `p1/analyze_p1.py` for the b ≡ 1 control →
   `results/p1_unit.json`.
5. B2; `analyze_g2.py out/2dc_C_P2_Flux23/xsec.root out/2dc_C_G2_on/xsec.root <override.json> <override.npz>
   results/g2_s42.json`. If it routes MATERIAL or NOT RESOLVED: B3 through the gate, then `--tag _s43 --confirm`.
6. B4; `analyze_pilot.py p3 results/p3.json`. B5–B8; `p1/analyze_p1.py`.
7. `REPORT.md`: K1 and K2 terminal outcomes, every `sacct` row, measured unit costs and peak memory (MaxRSS), and
   S1–S5 repriced with a ≥ 20% reserve; durable copies of results to CFS `m3246`, sha256 re-measured.

## 11. Smoke tests during packaging (login node, existing products; not pilot results)

- `select_flux.py` ran on the inputs (rc 0); output committed.
- `analyze_pilot.py` ran end to end with stand-in outputs (XR-L0 for P0, P5's run *a* for `P2_MaRES0`, July
  products for others): every verdict path executed; stand-ins correctly failed provenance (INCONCLUSIVE); P5's
  run *a* vs July `MaRES_0` gave 2.2e-10 σ_ML (E2 PASS); a seed-43 stand-in for `Flux23` gave E1 FAIL.
- `launch.py simulate` produced §4's table.
- P1: see `p1/README.md` (loader-level no-op controls and the background-variance check).

## 12. Limits

- K1 tests five universes; the other 182 July universes are qualified by inference from the same producer.
- K2 measures one Flux universe (largest median exposure, negligible constraint weight) at one or two seeds.
- σ_ML is the pinned LightGBM seed-scan σ and is not re-measured.
- P3's comparisons have no written criterion; its u_A cost is the measured outcome.
- The G1 = 0 census covered the dump and CV files, not the active files.
- Same-model caveat: the executor, the research agents, the P1 builder and the verifier are all Claude Opus 5.5.
