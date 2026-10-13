# P5 (G2 miss-row universe weights): independent review of the diagnostic patch

**Reviewer:** a fresh, read-only Claude session, 2026-10-12. **Same-model caveat:** I am the same model family as
the author, so shared blind spots are possible. This review is not independent in the sense of a different
reviewer type.
**Scope:** the untracked package `docs/orchestration/state/2d-closeout/stageB/diagnostics/p5/` in
`/Users/josephbailey/local-research/MINERvA-OmniFold-closeout-diag-20261012`, and its NERSC copy
`/pscratch/sd/j/josephrb/2d-closeout-stageB-diag-20261012/p5/`.
**Grant:** `AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md` at origin/main `3921dec4` (sha256
`ac1bce59…df008`, re-measured).
**Nothing was edited, committed, pushed or submitted.** `sacct` shows no `2dc_B5_*` job on 2026-10-12. My test
outputs are only under `review-p5/`.

## Verdict: APPROVE WITH CHANGES

- The patch is correct and approved. The alignment argument holds, the weight is the right one, `patch.diff` is
  the real diff, option-off behaves identically, the guards fire, and `--branch-select derived` works with the
  override.
- **Fix finding 1 (BLOCKER) before the first job.** The pre-declared MATERIAL rule sits below the seed-scale
  trainer-noise level, so a MATERIAL verdict could come from LightGBM's response alone. The fix touches only
  `analyze_p5.py` and DESIGN.md and needs no extra compute.
- Findings 2–4 are cheap pre-submission fixes.

## Findings

### 1. BLOCKER: the MATERIAL threshold is below the trainer-noise level, and DESIGN §7 contradicts Stage B §2.9

**Where:** `analyze_p5.py:22-25,101`; `DESIGN.md:111-113,125-127`.

**The claim.** DESIGN §7 says: "with fixed seeds and threads that response is the effect itself."

**What contradicts it.**
- Stage B §2.9 (A4 item 3) found that `NormNCRES` moves the training input by 6.3e-5 and the output by up to
  1.47%. It concludes that "instability and seed effects are not separable without a factorial design."
- Run b changes the miss-row weights by up to ×0.41 (summed ratio 0.93). So d = b − a contains G2's systematic
  effect plus the trainer's discrete path response.
- L0's 1.4e-11 reproducibility holds only at identical inputs. It bounds nothing here.

**I measured the scales on NERSC** (`review-p5/sig_band.py`, `review-p5/sig_ml.py`):
- July MaRES σ_band/CV over the 205 cells: median 6.0e-3, p10 1.1e-3, minimum 5.2e-5.
  - 17 cells are below 1e-3, 44 below 2e-3 and 88 below 5e-3.
- Seed-scan σ_ML/CV (`uq/seedscan_lgbm_ml/uq_covariance_ml.root`, hStd2D): median 1.66e-3, p90 5.6e-3.
- **σ_ML/σ_band(MaRES): median 0.30, p10 0.11, p90 1.75.**

**What that does to the rule.**
- If d were seed-scale noise, median r1 would be about 0.95 × 0.30 ≈ 0.28. That passes "median r1 > 0.10".
- "max r1 > 0.30 over floored cells" would also pass (p90 ratio 1.75).
- Both MATERIAL branches can therefore fire with no G2 effect. A false MATERIAL routes to a 43–129 node-h repair.

**Fix (no compute):**
- Add r3 = |d|/σ_ML per cell, using hStd2D from the seed-scan file. Record its sha256 in the report.
- Route MATERIAL only if the r1 rule holds **and** median r3 > 2 (or another bar declared now, before data).
- If r1 holds but r3 does not, report "NOT RESOLVED above trainer noise" (descriptive). The outcome stays
  MEASURED with its numbers.
- Pre-declare one structural metric: the Spearman correlation across cells between d/a and (c_a − 1). A real G2
  effect should follow the completeness pattern; trainer noise should not.
- Rewrite DESIGN §7 "No noise floor" to cite Stage B §2.9 and the measured σ_ML/σ_band.

**Optional (director's call, about +0.25–0.8 node-h):** repeat the pair at `--seed 43`. Take G2 as the mean of
d42 and d43, and the instability as their half-difference.

### 2. MINOR: the NERSC deployment is incomplete, so a submission now would fail at launch

**Where:** `sbatch_p5.sh:9-10,50`.
- `/pscratch/.../p5/out` does not exist (`ls` measured). Slurm cannot open `--output`/`--error`, and
  `build_miss_override.py` writes the npz there too.
- `sbatch_p5.sh` and `analyze_p5.py` are not on NERSC yet. `p5/scripts/` holds only `build_miss_override.py` and
  `test_noop.py`.

**Fix:**
- `mkdir -p $NS/p5/out`, then copy both scripts.
- Record the sha256 of `sbatch_p5.sh` and `analyze_p5.py` in DESIGN §3, which currently says "see file".

### 3. MINOR: the 1 h walltime has little margin for the `on` job

**Where:** `sbatch_p5.sh:8`.
- I ran `build_miss_override.py` on 1L (383,848 rows): 7.2 s wall, including ROOT start-up. Scaled by rows
  (32.85M, about 85×), the merged-file build is about 5–10 min.
- The driver's derived-mode universe runtime is unmeasured (DESIGN §7). The July full-read upper bracket of
  2,355–2,738 s was measured at 128 threads; these jobs use 64.
- So the `on` job could exceed 60 min. A TIMEOUT burns 0.5 node-h and forces a retry.

**Fix:**
- Give the `on` job `--time=01:30:00`.
- Enforced worst case is then 0.5 + 0.75 = 1.25 node-h, inside P5's 1.5. With P4's 0.9 that is 2.15 of the 3.0
  ceiling.

### 4. MINOR: the analysis does not check run provenance, and the helper is unpinned

**Where:** `analyze_p5.py:62-75`; `sbatch_p5.sh:36-38`.
- The driver imports the OmniFold helper from a hard-coded shared path, `_OF_PY`
  (`/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python/omnifold.py`, `driver_p5.py:2111`). That
  checkout is at `32e403b8`, not the package's `git archive`.
  - Today the file's sha256 is `e9623412…8227a` = origin/main = the package copy.
  - A change to it between the two jobs would break the pairing silently.
- **Fix in `sbatch_p5.sh`:** add a `sha256sum -c` line for the helper.
- **Fix in `analyze_p5.py`:** read the `runConfig`, `driverSha256`, `omnifoldHelperSha256` and
  `p5MissWeightOverride` TNameds from both outputs, and require:
  - equal helper digests;
  - the expected driver digests;
  - runConfigs equal apart from `out` and `miss_weight_override`;
  - run b's override sha256 equal to `out/override_MaRES_0.npz`.
- This replaces the "checked by hand" note at `:75`. That hand check is redundant anyway, because the loader
  raises if an entry is not applied.

### 5. MINOR: the analysis can silently return NOT MATERIAL on NaN

**Where:** `analyze_p5.py:80,101`.
- A cell with σ_band = 0 (or |a − CV| = 0) gives inf or NaN. `np.median` of NaN is NaN, and `NaN > 0.10` is
  False, so the routing becomes NOT MATERIAL without warning. Today min σ_band/CV is 5.2e-5, so no zero exists.
- **Fix:** assert that every r1 and r3 is finite before routing, or report INCONCLUSIVE.

### 6. MINOR: no refuse-if-exists guard on the override outputs, and no job-name guard

**Where:** `sbatch_p5.sh:29,50`.
- The override npz and json are overwritten on re-submission.
- The 2dc_B5_ name relies on the command-line `--job-name`.
- **Fix:**
  - extend the `REFUSE` guard to `$NS/out/override_MaRES_0.{npz,json}` in `on` mode;
  - add `[ "$SLURM_JOB_NAME" = "2dc_B5_$MODE" ] || exit 4`.

### 7. MINOR: the alignment's code citations name the wrong producer revision

**Where:** `DESIGN.md:5,23-31`; `build_miss_override.py:4-11`.
- The July universe omnifile (mtime 2026-07-08 08:08) was written by the July event-loop revision, not by
  `3921dec4`. Stage B §2.5 says the July producer state was never committed.
- So the `3921dec4` line citations explain the mechanism; they do not prove the file's layout.
- The claim actually rests on the fail-closed empirical checks. Those checks would fail rather than pass silently
  on a different layout.
  - Example: `tail_proxy_weights` passing shows the file has the KNOWN_ISSUES #12 fix. Before that fix, miss rows
    held uninitialised universe weights.
- **Fix:** say this in DESIGN §2.

### 8. NIT

- **Unreachable guard** (`driver_p5.py`, patch hunk at `:774-782`). The guard "an entry left unapplied raises"
  can never fire: the override is applied before any `continue`, so `n_override == n_finite` always holds.
  Harmless, but DESIGN §3 should not count it as a tested guard.
- **Wording** (`test_noop.py:71-74`). `miss_kept` also includes the reco-loop rows with `sim_pass = 0` (70,500 in
  1B). C3 therefore proves "changed only on rows without reco", not "only on miss rows". The miss-only property
  comes from how the npz is built.
- **Unused load** (`analyze_p5.py:44,65`). `jcv` is loaded but never used.
- **Missing input check** (`driver_p5.py`, main hunk). The driver checks the npz's universe and `n_signal`, but not
  its `omnifile`/`omnifile_size` against `--omnifile`. `n_signal` makes a wrong file unlikely; checking the size
  would make it impossible.

## Answers to the review questions

1. **Alignment.** The argument is sound.
   - At `3921dec4`, `out->Fill()` (`:637`) and `outTruthDenomCache->push_back` (`:667`) run in the same iteration,
     after the dedup `continue`s. So cache order equals truth-row order.
   - `AppendTruthOnlyMisses` (`:686`) walks the cache in order. It copies `MC`, `MC_pz` and `w_truth` as the same
     doubles, and sets every `w_truth_*`/`w_reco_*` to `tde.w_truth` (`:862-863`).
   - Matching on exact float64 bit patterns is sound because the values are copied, not recomputed.
   - Ties fail closed: the uniqueness check stops the job.
   - For a mismatch to pass silently, a miss would have to bit-match a different truth row while its own truth
     row did not match. The complement multiset check, which includes `w_truth_MaRES_0`, would also have to
     balance by coincidence. I find no realistic route.
   - Playlist order and block sizes are checked indirectly by the per-block tail checks, and those fail closed.
   - I re-ran the builder on **1L**: all 11 checks PASS, with 111,605 misses aligned (summed true/proxy 0.933).
2. **Weight.** `w_truth_MaRES_0` from `mc_truth_denom` is the right weight.
   - The truth loop computes it as `model.GetWeight(*u, uEvt)`.
   - The complement check proves it is bitwise equal to the signal tree's `w_truth_MaRES_0` for every reco-loop
     event. So it has the same definition, measured, not assumed.
   - `w_reco` on miss rows is never used: `omnifold.py:250` uses `MCreco_weights` only on `MC_pass_reco_mask`.
     Setting it to the override keeps the proxy convention and changes nothing.
   - No other array needs changing. `pass_*` and the kinematics stay equal (C3), and purity and fakes use
     reco-passing rows only.
3. **Diff and option-off behaviour.**
   - `diff -u` of origin/main's driver (sha256 `6be77c51…21257`, re-measured) against `driver_p5.py` equals
     `patch.diff` line for line, apart from its two header lines.
   - The NERSC `repo/2d-unfolding` copies carry the same two digests.
   - With the flag off, `main()` differs only by `p5_kw = {}` and `p5_prov = None`. The patch draws no random
     numbers, so seeds and RNG streams are unchanged.
   - Loader C1 bitwise equality, plus inspection, therefore carries the run-level no-op.
   - The guards (sim_pass=1, length) fire; I tested both.
   - `--branch-select derived` works with the override and matches the direct call bitwise.
4. **Fairness of (a) vs (b).**
   - The two runs use the same options, the same `--seed 42` and `OMP_NUM_THREADS=64`.
   - LightGBM 4.6.0 has `n_jobs=None`, so it follows OpenMP.
   - The deterministic run-to-run noise is negligible. The training-path response is not (finding 1).
   - G-c is a valid inputs bridge: Stage B's reviewer rebuilt MaRES_0's c to 3.5e-14, so 1e-12 is reachable. It
     says nothing about training.
   - **c(b) ≈ 1 is the right expectation.** At loader level on 1L I measured max |c − 1| = 7.3e-15 with the
     override, against 0.103 without it.
5. **sbatch.**
   - Correct as written: account m3246, QOS shared, `constraint=cpu`, 128 CPUs (charged half a node), absolute
     paths, a positional mode instead of `--export`, no `set -u`, and the sha guards.
   - I tested that `set -eo pipefail` before sourcing `setup_salloc_env.sh` exits 0.
   - TMPDIR, the working directory and outputs all sit inside the namespace. The driver writes only `--out`.
   - Enforced worst case is 2 × 1 h × 0.5 = 1.0 node-h.
   - Needs findings 2, 3 and 6.
6. **Analysis.**
   - The metric definitions are fine.
   - The MEASURED/INCONCLUSIVE logic matches the grant.
   - The routing threshold needs finding 1 and the NaN guard in finding 5.
7. **No-op control, re-checked myself on 1L** (a different playlist from the author's 1B):
   - `test_noop.py` gives PASS: C1 and C2 bitwise, and C3 changed 25,749 rows, all without reco, with
     w_reco = w_truth.
   - My `rev_checks.py`, in derived mode, gives off ≡ production bitwise and on(derived) ≡ on(all). Both guards
     fire. Loader-level c is 1 to 7.3e-15 with the override, against 0.103 without it.

## What I verified myself (commands run, not quoted)

- origin/main = `3921dec4`; the grant's sha256 `ac1bce59…`; the production driver's sha256 `6be77c51…` at both
  origin/main and `3921dec4`.
- `patch.diff` equals the real diff; the NERSC `repo` driver digests match.
- Event-loop line citations at `3921dec4`: `:637`, `:667`, `:686`, `:803`, `:862-863`.
- The `omnifold.py` helper digests match (shared checkout, package copy and origin/main), and its use of
  `MCreco_weights` (pass-reco rows only).
- Input files and mtimes: the merged file is 171,117,087,867 B. The 12 block sizes sum to the merged size within
  0.01%, and every block mtime precedes the merged file's.
- I ran `build_miss_override.py`, `test_noop.py` and `rev_checks.py` on 1L.
- σ_band and σ_ML distributions (finding 1); the job-time scaling (finding 3); the env sourcing under `set -e`.
- Not verified: the merged-file build (it would take too long on a login node), and the derived-mode universe
  runtime.

## sha256 of reviewed files

| file | sha256 |
|---|---|
| DESIGN.md | `9f80e3259322c2f958318ab60540e709c102b3d5b510c4b856b1ec02a417007d` |
| driver_p5.py | `fe644228b27450a6e5712970253d548b73c7990dbb54200e68b5847c1cfdf6cf` |
| patch.diff | `eb82efa604dabf0e8719ba295dc795fb3dd7bec26185202f6770c4e7a4b2ebf5` |
| build_miss_override.py | `7f346e1af1688b6a43be540ef2a8c6f8456d76a1ea965613abce17263739296b` |
| test_noop.py | `cf9c9ecdd3df4af67be61081ee0f42c958340544efcf98d8d1b0d7ca4a006863` |
| sbatch_p5.sh | `2cc1ebbbfdabd1167a65989284db3abe01b1c50fb38a1fcafdb4c74d828022ab` |
| analyze_p5.py | `762158134a76eddcfc0c00970d33264e3cc5a5218a61816cd92d1e8387e454cf` |
| smoke/noop_1B_MaRES_0.json | `d4c8f2955234d6ffe24c9bf2704af1df449f1a79918ee016131fd0e4d948370c` |
| smoke/override_1B_MaRES_0.json | `8692a77ad20f3a6cd8ace310f0c3f2cd37e12a5aa848efba9f78cafe713d32b1` |
| (NERSC) smoke/override_1B_MaRES_0.npz | `52aeab905c5fc2688ee0a23686be3b7fe31dd5443739bb888da2e7bb00e999a3` |
| production `unfold_2d_omnifold_unbinned.py` (origin/main) | `6be77c51805547bac2d864ce77c7bc636607cf43194bd2f4ad1a7c14db621257` |
| `unbinned_unfolding/python/omnifold.py` (all three copies) | `e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a` |

**Reviewer artifacts** in `review-p5/`:

| file | sha256 prefix |
|---|---|
| `sig_band.py` | `d77b2cd1` |
| `sig_ml.py` | `b9faa8e7` |
| `rev_checks.py` | `5e4a1642` |
| `ov_1L.npz` | `6f0b9cdb` |
| `ov_1L.json` | `b07cdfe7` |
| `noop_1L.json` | `4819b507` |
| `rev_checks_1L.log` | `a67ddae4` |
