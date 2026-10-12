# P5 — G2 miss-row universe weights: design (not run)

**Grant:** `AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md` (sha256 `ac1bce59…`), item P5.
**Status:** designed and smoke-tested on the login node (playlists 1B, and 1L by the reviewer).
- Review: [`review/REVIEW.md`](review/REVIEW.md) (sha256 `726a9e92…`), **APPROVE WITH CHANGES**. Every change it
  asked for, including the BLOCKER, is applied below.
- Re-review: [`review/REREVIEW.md`](review/REREVIEW.md) (sha256 `b93f869c…`), **APPROVE WITH CHANGES**. R1–R3
  are applied (§5, §7); per the re-review, they need no third full review.
- No Slurm job has been submitted.

## 1. Question

In dump mode, every universe weight of an appended truth-only miss row is the CV truth weight (the G2
proxy). For universes whose truth weights vary, the driver's completeness c then departs from 1:
- July `MaRES_0`: |c − 1| median 0.58%, max 6.76%.
- The driver divides each cell by c.

P5 asks whether that division reproduces the unfold in which the miss rows carry their correct universe
weight. It answers for one truth-weight-varying vertical universe.

## 2. The correct weights are in mc_truth_denom: no new event loop

**Finding (for the diagnostics REPORT).** No new event loop is needed for a G2 repair.
- The correct per-event universe truth weights of the miss rows are already in the universe omnifile's
  `mc_truth_denom` tree, as `w_truth_<band>_<idx>`.
- `build_miss_override.py` attaches them to the miss rows exactly.
- So a G2 repair of any vertical universe is re-unfolds only. This revises Stage B §7, which said "plus
  event loops".

**Mechanism.** At `origin/main` `3921dec4`, `runEventLoopOmniFold.cpp`:
- the truth loop fills `mc_truth_denom` (`:637`) and pushes the same event onto `truthDenomCache` (`:667`)
  in the same iteration;
- `AppendTruthOnlyMisses` (`:686`) walks the cache in order. It copies MC, MC_pz and w_truth as the same
  doubles, and sets every universe weight to w_truth (`:862-863`);
- `mc_truth_denom`'s own universe weights are filled by the truth loop (`:801-803`).

**Provenance caveat.** The July universe omnifile (mtime 2026-07-08) was written by an event-loop revision
that was never committed (Stage B §2.5), not by `3921dec4`.
- So the line citations explain the mechanism; they do not prove this file's layout.
- The alignment rests on the fail-closed empirical checks below. On a different layout they would fail,
  not pass silently.
- Example: `tail_proxy_weights` passing shows this file carries the KNOWN_ISSUES #12 fix. Before that fix,
  miss rows held uninitialised universe weights.

**Alignment.** The omnifile has no event-ID branches, so `build_miss_override.py` works per playlist
block, using the per-playlist files for the block sizes.
- Measured: all 12 playlists have equal entry counts in the two trees, summing to 32,849,103, with
  8,999,007 misses, equal to the merged file's `nTruthOnlyMisses`. `hadd` order is 1A…1P.
- The script matches the exact key (MC, MC_pz, w_truth) and requires, failing closed:
  1. tail rows have `sim_pass = 0`, `sim = −9999`, and proxy weights;
  2. truth keys are unique;
  3. every miss is found;
  4. matched truth indices are strictly increasing;
  5. the unmatched truth rows equal the reco-loop rows exactly, as multisets of (MC, MC_pz, w_truth,
     w_truth_<u>).
- 1B: all pass, 181,498 misses, summed true/proxy 0.932. 1L (reviewer): all pass, 111,605 misses, 0.933.
- Reco-loop rows that fail the selection also have `sim_pass = 0` (70,500 in 1B). They carry signal-loop
  weights and are not misses; their count is recorded, not checked.

## 3. Code (sha256; NERSC copies checked with `sha256sum -c`)

| file | role | sha256 |
|---|---|---|
| `driver_p5.py` | diagnostic copy of `2d-unfolding/unfold_2d_omnifold_unbinned.py` (`6be77c51…`) with `--miss-weight-override NPZ`, default off | `f71b5759bf01422fa8c6b6e5432885b34d1f127653df1165a0adb7527bdb12d2` |
| `patch.diff` | unified diff production → diagnostic copy (120 lines) | `e4ce8fba5635994687ac54a6479f30c108bf559c2f780fc42e2e392a15b4a89c` |
| `build_miss_override.py` | alignment and checks → `w_override` (NaN except on miss rows) | `7f346e1af1688b6a43be540ef2a8c6f8456d76a1ea965613abce17263739296b` |
| `test_noop.py` | loader-level controls C1–C3 | `cf9c9ecdd3df4af67be61081ee0f42c958340544efcf98d8d1b0d7ca4a006863` |
| `sbatch_p5.sh` | the jobs (NERSC `p5/sbatch_p5.sh`) | `fc3fbc95ec84ec8f55f32093f20731febf235adb77c3a8e53cc966c356dd730a` |
| `analyze_p5.py` | gates, metrics, routing (NERSC `p5/analyze_p5.py`) | `8f37fd7fe64ae5cb17517d71878d8a7e30595802847768a1eaa5ab1ea1fe8e65` |
| `dry_confirm.py` | synthetic dry run of the seed-43 routing branches (§7) | `55c4be53795e532b712ed6366490531a52425fed9721a59dac0ad885efa53ad0` |
| helper `unbinned_unfolding/python/omnifold.py` (the driver's `_OF_PY` import; pinned in `sbatch_p5.sh`) | — | `e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a` |

**The patch.**
- **Loader.** `collect_signal_arrays_2d` gains `miss_weight_override=None`. With an array, a finite entry
  replaces both w_truth and w_reco of that row, before the POT scale. A finite entry on a `sim_pass = 1`
  row raises; that guard was tested by the reviewer.
- **The "unapplied" guard is not tested.** A second guard, "an entry left unapplied raises", is
  unreachable: the override is applied before any `continue`. It is not counted as tested.
- **main().** The flag is checked against the npz's universe, entry count, omnifile realpath and
  omnifile size. The size check was added after review; its negative test on a size-tampered npz raised
  before any output. The run records `p5MissWeightOverride` (path, sha256) in its provenance.
- **Branch selection.** The flag needs no branch, so `--branch-select derived` is unchanged. The reviewer
  showed `on(derived)` ≡ `on(all)` bitwise at loader level.
- The production driver and event loop on `main` are untouched.

## 4. Controls

**Loader level** (`test_noop.py`): 1B rerun after the driver change gives PASS (`smoke/noop_1B_MaRES_0_r2.json`).
- That file is byte-identical to round 1 (`d4c8f295…`) and records no driver digest, so it cannot show which
  driver it ran with.
- The re-reviewer's 1L rerun with `f71b5759…` covers this: PASS, byte-identical to round 1.
- The 1B override-builder report is stored as `smoke/override_1B_MaRES_0.json.gz` (`gzip -n`; inner sha256
  `8692a77a…`, as pinned in `review/REVIEW.md`). It cites the untracked 1B event-loop ROOT file by name.
- **C1, no-op.** With the option off, the output is bitwise equal to the production loader on every
  array, in universe mode.
- **C2, identity plumbing.** An override equal to the stored proxy is bitwise equal to production.
- **C3, effect.** The real override changes `w_truth`/`w_reco` **only on rows without reco**: 40,948 in
  1B, summed ratio 0.708. There w_reco = w_truth, and every kinematic and pass array stays bitwise equal.
  The property "only on miss rows" comes from how the npz is built (§2), not from C3.

**Run level.**
- Run *a* is the production driver itself (`6be77c51…`, from a `git archive` of `3921dec4`).
- Run *b* differs from it only by the override, so C1–C3 carry the run-level no-op. The patch draws no
  random numbers.
- G-p (§6) checks that both outputs record equal settings and helper digests.

**Bridge to July (G-c).** Run *a*'s completeness must equal the July `MaRES_0` completeness to ≤ 1e-12.
Completeness depends only on weights, so this ties run *a* to the July inputs.

## 5. Runs, time limits and cost

| job | content | limit | enforced worst case |
|---|---|---|---|
| `2dc_B5_off` | production driver, `--universe MaRES:0`, seed 42 | 01:00:00 | 0.50 node-h |
| `2dc_B5_on` | `build_miss_override.py` (merged file, about 5–10 min), then `driver_p5.py --miss-weight-override` | **01:30:00** | 0.75 node-h |
| **P5 (seed 42)** | | | **1.25 node-h** |
| conditional `2dc_B5_off_s43` + `2dc_B5_on_s43` (§7) | the same pair at `--seed 43`, reusing the seed-42 override, sha256-checked | 01:00:00 / 01:30:00 | 1.25 node-h |

**Shared settings.** Both runs use shared QOS with 128 CPUs, charged half a node (charge = elapsed ×
128/256), and `OMP_NUM_THREADS=64` (L0's 64 LightGBM threads). Options: `--iters 5 --use-weights
--estimator lgbm --seed <42|43> --bkg-mode purity --branch-select derived` on the July universe omnifile
(`220c479e…`), with `baseline_flux/runEventLoopMC_MEFHC.root`.

**Expected cost.** About 0.25–0.8 node-h for the seed-42 pair.

**Ceiling check.** The grant's ceiling is 3.0:

| item | worst-case node-h |
|---|---|
| P4 | ≤ 0.41 |
| P5 | 1.25 |
| conditional seed-43 pair | 1.25 |
| **total** | **2.91** |

**Retry procedure** (written before any job). The grant allows one retry, and only after a diagnosed
infrastructure cause; a scientific result is never a reason. A retry:
1. records the failed job's `sacct` State, ExitCode, Elapsed and charge, and the diagnosed cause (node fault,
   filesystem, TIMEOUT from a scheduler stall, and so on) in the diagnostics REPORT;
2. moves the failed attempt aside rather than deleting it:
   - `out/xsec_MaRES_0_<mode><tag>.root`, if any;
   - for a seed-42 `on` job, `out/override_MaRES_0.{npz,json,npz.sha256}`;
   - all of it into `out/failed_<jobid>/`, with the move (paths, sha256 before and after) recorded in the
     REPORT;
3. resubmits the same command only if the actual `sacct` charges so far, plus the retried job's enforced
   worst case, stay within the 3.0 node-h ceiling.
Without step 2, `sbatch_p5.sh` refuses: it will not overwrite an output or an override.

**`sbatch_p5.sh` refuses** (exit 3/4) if:
- the job name is not `2dc_B5_<mode>[_s43]`;
- the job's TimeLimit is not 01:00:00 (off) or 01:30:00 (on);
- the output exists;
- in seed-42 `on` mode, the override npz/json/sha256 already exists;
- any pinned sha256 fails: driver, diagnostic copy, builder, or helper.

## 6. Outcome rules (`analyze_p5.py`; fixed before any data)

**MEASURED** requires all of:
- **G-a:** the override report passes with n_override = 8,999,007, and run *b*'s `p5MissWeightOverride`
  sha256 equals the npz's.
- **G-b:** max |c_b − 1| ≤ 1e-9. The reviewer measured 7.3e-15 at loader level with the override.
- **G-c:** c_a equals the July `MaRES_0` completeness to ≤ 1e-12 relative.
- **G-p:** `driverSha256` is *a* = `6be77c51…` and *b* = `f71b5759…`; `omnifoldHelperSha256` is equal in
  both and is `e9623412…`; `runConfig` is equal apart from `out` and `miss_weight_override`; *a* carries no
  override record.
- **G-f:** every r1 and r3 is finite, and the σ_ML file is pinned (`3b6b48ec…`).

Otherwise **INCONCLUSIVE**. A scientific result is never a reason to retry. A stand-in dry run on July
files, without provenance, returned INCONCLUSIVE as it should.

**Metrics** (reported, no pass/fail). d = b − a per cell, and:

| metric | definition |
|---|---|
| r1 | \|d\| / σ_band, with σ_band = \|j0 − j1\|/2 (July `MaRES` pair) |
| r2 | \|d\| / \|a − CV\|, with CV = `E_U` |
| r3 | \|d\| / σ_ML, with σ_ML = √diag of `uq/seedscan_lgbm_ml/uq_covariance_ml.root` `hCov2D_reported` |

Also reported:
- median, p84 and max of each;
- the integral change;
- the bridge |a − j0|/σ_band;
- **descriptive:** the Pearson and Spearman correlation across cells of d/a with (c_a − 1). G2 predicts
  the change tracks the completeness deviation; trainer noise should not.

**Routing** (descriptive):
- **r1 rule:** median r1 > 0.10 over the 205 cells, **or** max r1 > 0.30 over the cells with σ_band ≥
  1e-3 × CV (188 cells on the July pair).
- **MATERIAL** iff the r1 rule holds **and** median r3 > 2.
- **NOT RESOLVED ABOVE TRAINER NOISE** iff the r1 rule holds and median r3 ≤ 2. That is, the size
  criterion held and the noise criterion failed.
- **NOT MATERIAL** otherwise.
- MATERIAL routes to a G2 repair. By §2 that repair is re-unfolds only, about 170 universes × u_U,sel…u_U.

## 7. Trainer noise and the conditional seed-43 follow-up

**Why r3 is in the rule.** Run *b* retrains with changed truth weights: up to ×0.41 per event, summed
0.93. So d contains G2's systematic effect plus LightGBM's discrete training-path response.
- That response is not small. In Stage B §2.9, an input change of 6.3e-5 (`NormNCRES`) moved the output
  by up to 1.47%, so instability and seed effects are not separable without a factorial design.
- L0's 1.4e-11 reproducibility holds only at identical inputs and bounds nothing here.

**Measured scales** (reviewer, on NERSC):
- σ_band/CV over the 205 cells: median 6.0e-3, p10 1.1e-3, min 5.2e-5.
- σ_ML/CV: median 1.66e-3.
- **σ_ML/σ_band: median 0.30**, p10 0.11, p90 1.75. The dry run here gave 0.299.

**Consequence.** Seed-scale noise alone would give median r1 ≈ 0.28. That clears the r1 rule by itself,
hence the r3 > 2 requirement.

**Conditional seed-43 pair.** It runs only if the seed-42 routing is MATERIAL or NOT RESOLVED ABOVE
TRAINER NOISE, and only after both:
- a budget check: the **actual `sacct` charges** of every P4/P5 job so far, plus the pair's **enforced 1.25
  node-h**, must be ≤ 3.0;
- the director's go-ahead.

`analyze_p5.py --tag _s43 --confirm`:
- **refuses unless `--tag _s43`**, so seed 42 is never compared with itself;
- refuses when the seed-42 routing is NOT MATERIAL, since no pair is declared there;
- applies the same gates to seed 43;
- compares the pairs on **z = d / σ_ML per cell**, not raw d (raw d would weight cells with large cross
  sections), over the cells with σ_band ≥ 1e-3 × CV;
- gives:
  - **CONFIRMED** iff both pairs are MEASURED and Pearson(z43, z42) ≥ 0.5;
  - **INCONCLUSIVE** if either pair is not MEASURED or the correlation is not finite;
  - **NOT CONFIRMED** otherwise;
- reports Spearman alongside.

**Final routing (fixed before data):**

| seed-42 routing | seed-43 result | final routing |
|---|---|---|
| MATERIAL | CONFIRMED | MATERIAL |
| MATERIAL | NOT CONFIRMED | NOT RESOLVED ABOVE TRAINER NOISE |
| NOT RESOLVED ABOVE TRAINER NOISE | CONFIRMED | MATERIAL iff the r1 rule holds on d̄ = (d42 + d43)/2; otherwise NOT MATERIAL (coherent but below the size threshold) |
| NOT RESOLVED ABOVE TRAINER NOISE | NOT CONFIRMED | NOT RESOLVED ABOVE TRAINER NOISE |
| NOT MATERIAL | — | no seed-43 pair |
| any | INCONCLUSIVE | INCONCLUSIVE |

The third row is the director's ruling of 2026-10-12, frozen in this commit before any seed-42 result
was read.

**Why the third row can be MATERIAL.** A shift coherent across seeds that passes the r1 rule is a recipe bias,
whatever σ_ML is. Median r3 > 2 means median |d| > 0.6 σ_band, so a coherent bias of 0.1–0.6 σ_band
always lands in NOT RESOLVED at seed 42. This row is its only route to a decision. Requiring the r1 rule
on the seed mean d̄ makes the size test act on the coherent part: noise that inflated |d42| averages down.

**Dry run of these branches** (NERSC login node; `dry_confirm.py` calls `confirm()` on synthetic inputs, then
the CLI refusals; σ_band = 1, σ_ML = 0.3, 188 floored cells):

| input | r | median r1(d̄) | result |
|---|---|---|---|
| `--confirm` without `_s43` | — | — | refused |
| unknown tag | — | — | refused |
| seed 42 NOT MATERIAL | — | — | refused |
| constant z43 (0.1/0.3, and exact zero) | NaN | — | INCONCLUSIVE |
| either pair INCONCLUSIVE | — | — | INCONCLUSIVE |
| coherent, after MATERIAL | 0.997 | 0.200 | MATERIAL |
| noise, after MATERIAL | 0.072 | 0.139 | NOT RESOLVED |
| coherent and large, after NOT RESOLVED | 0.997 | 0.200 | MATERIAL |
| coherent and small, after NOT RESOLVED | 1.000 | 0.029 | NOT MATERIAL (coherent, below size) |
| coherent, d42 inflated by noise, after NOT RESOLVED | 0.523 | 0.056 (max 0.21) | NOT MATERIAL (coherent, below size) |
| noise, after NOT RESOLVED | 0.074 | 0.147 | NOT RESOLVED |

The first dry run of the flat case returned r = 0.000, not NaN: `corrcoef` of a constant vector is rounding
residue. `confirm()` now sets r to NaN when either z vector has zero spread.

## 8. Open points

- **Universe choice.** `MaRES_0` is a GENIE knob, where Stage B measured c − 1 up to 10%; the July product
  read here gives 6.76%. A large Flux universe (c − 1 up to 18%) would be a second case at the same cost,
  but it does not fit in the 3.0 ceiling alongside the conditional seed-43 pair.
- **Runtime.** The in-driver selective read is unmeasured on a universe job. The limits above bound it.
