# P5 (G2 miss-row universe weights): focused re-review (round 1 of 2)

**Reviewer:** the same read-only Claude session that wrote `REVIEW.md` (sha256 `726a9e92…`), 2026-10-12.
**Same-model caveat:** I am the same model family as the author, and I also authored the findings being checked,
so I may be biased toward accepting my own fixes.

**Nothing was edited, committed, pushed or submitted.** `p5/out/` is empty and no `2dc_B5_*` job exists.
My new test files are only under `review-p5/`.

## Verdict: APPROVE WITH CHANGES

- All eight original findings are resolved, including the BLOCKER.
- **No new defect is found in the driver, the builder or the guards.** No guard blocks a legitimate first run.
- **`patch.diff` equals the real diff.**
- **One new MAJOR is in the conditional seed-43 rule (finding R1).** The `--confirm` verdict does not say which
  routing it confirms, and the NOT RESOLVED branch has no pre-declared outcome.
- R1 changes only text and logic in `analyze_p5.py` and DESIGN §7. It does not touch the seed-42 jobs.
- **The seed-42 pair may be submitted now.** Fix R1 before any seed-43 job and before the seed-42 routing is
  read. Fixing it is a mechanical edit; it needs no third full review.

## Resolution of the original findings

| # | finding | status | evidence |
|---|---|---|---|
| 1 | BLOCKER: noise-blind MATERIAL rule | **RESOLVED** (but see R1) | `analyze_p5.py:23-27,131,152-155`: r3 = \|d\|/σ_ML; MATERIAL needs the r1 rule **and** median r3 > 2, otherwise NOT RESOLVED or NOT MATERIAL. Correlation metric at `:143-144`. DESIGN §7 rewritten. σ_ML checked below. |
| 2 | NERSC deployment | **RESOLVED** | `p5/out/` exists (empty). `sbatch_p5.sh` and `analyze_p5.py` are deployed. All NERSC digests equal the local ones and `SHA256SUMS`. |
| 3 | walltime | **RESOLVED** | `on` jobs get 01:30:00, enforced by a TimeLimit guard (`sbatch_p5.sh:27-29`). |
| 4 | provenance and helper pin | **RESOLVED** | Helper sha256 pinned (`sbatch_p5.sh:44,58`). Gate G-p (`analyze_p5.py:116-122`) checks the driver digests, equal helper digests, runConfig equality apart from `out`/`miss_weight_override`, and that *a* has no override record. G-a now checks run *b*'s override sha256 against the npz. |
| 5 | non-finite values | **RESOLVED** | G-f (`:132`). r2 is not used for routing. |
| 6 | overwrite and job name | **RESOLVED** | `sbatch_p5.sh:26,45-48`. |
| 7 | producer-revision citations | **RESOLVED** | DESIGN §2, "Provenance caveat". |
| 8 | NITs | **RESOLVED** | Unreachable guard documented (DESIGN §3). C3 wording corrected (§4). `jcv` removed. npz omnifile realpath/size check added (`driver_p5.py` main hunk). |

## What I verified myself

**Diff and digests**
- `diff -u` of origin/main's driver (`6be77c51…`) against the new `driver_p5.py` equals `patch.diff` line for
  line, apart from its two header lines.
- Against the first round, the only change is the omnifile hunk: 5 lines and the hunk offsets.
- All seven package digests are equal locally, on NERSC and in `SHA256SUMS`.

**`os` scoping in `main()`.** The new local `import os` makes `os` local to all of `main()`.
- I grepped `main()` (lines 1380–2460): `os` is used only inside the `--miss-weight-override` block.
- The module has no top-level `os` import.
- So there is no `UnboundLocalError` in either mode.

**Omnifile guard logic**, replicated on NERSC (`review-p5/rr_checks.py`):
- the 1L npz is accepted for the 1L file and refused for the merged file;
- the author's 1B npz is accepted for 1B;
- the builder stores `os.path.realpath`, and the driver compares against `os.path.realpath`. The merged
  file's realpath is the plain `/pscratch/...` path. So a legitimate run passes.

**σ_ML input**
- The sha256 of `uq/seedscan_lgbm_ml/uq_covariance_ml.root` is `3b6b48ec…`, equal to the pin.
- `hCov2D_reported` is 205×205.
- √diag matches `hStd2D` taken in C order on the E_U > 0 mask to 3.3e-16. In Fortran order it is off by ~4e4.
  So the cell pairing is correct.
- σ_ML > 0 in every cell (min σ_ML/CV = 3.2e-4), so G-f cannot fail on σ_ML.
- Caveat: the histogram titles read "Poisson-bootstrap"; Stage B §2.9 cites this file as the seed scan. With 10
  seeds, each cell's σ_ML carries about 22% relative uncertainty.

**sbatch guards**
- `scontrol` prints `TimeLimit=HH:MM:SS` for limits under a day; I checked the field format on a live job. So
  `01:00:00` and `01:30:00` compare correctly.
- If `grep` finds no TimeLimit, `pipefail` exits the job. That fails closed.
- The job-name, seed and mode guards accept exactly the four documented submissions.

**No-op control with the new driver** (`f71b5759…` in `p5/repo`), on 1L:
- `test_noop.py` gives PASS. Its output is byte-identical to round 1 (`4819b507…`).
- `rev_checks.py` gives the same results as round 1:
  - derived option-off ≡ production;
  - on(derived) ≡ on(all);
  - the sim_pass=1 and length guards fire;
  - loader-level max |c − 1| = 7.3e-15 with the override, 0.103 without.

## New findings

### R1. MAJOR: the seed-43 verdict does not name its routing, and NOT RESOLVED has no outcome

**Where:** `analyze_p5.py:28-30,170-177`; `DESIGN.md:189-198`.

**The rule is well-defined as a computation.**
- d43 and d42 are on the same 205 cells in the same order.
- The σ_band ≥ 1e-3 × CV mask depends only on j0, j1 and CV, so it is the same for both seeds (188 cells).
- Under pure noise, r has SD ≈ 0.073 at n = 188. So r ≥ 0.5 is a ~7σ bar against a false confirmation. It
  confirms only when the coherent (G2) variance is at least about the noise variance.

**Three defects remain:**

1. **CONFIRMED is undefined after NOT RESOLVED.** The code returns CONFIRMED whenever both pairs are MEASURED
   and r ≥ 0.5, whatever the seed-42 routing was. DESIGN §7 says the pair "confirms MATERIAL", but the pair also
   runs after NOT RESOLVED ABOVE TRAINER NOISE, and no final routing is declared for that case.
   - This branch matters more than it looks. Median r3 > 2 means median |d| > 2σ_ML ≈ 0.6σ_band.
   - So a coherent G2 bias of 0.1–0.6σ_band, which is material for a systematic, always lands in NOT RESOLVED at
     seed 42.
   - Its only route to a decision is this undeclared branch.
2. **`--confirm` without `--tag _s43` compares seed 42 with itself.** That gives r = 1, so CONFIRMED.
3. **A NaN correlation becomes NOT CONFIRMED silently.** `np.corrcoef` returns NaN for zero-variance input.

**Fix, before any seed-43 job and before the seed-42 routing is read:**
- **Pre-declare the final routing table:**

  | seed-42 routing | seed-43 result | final routing |
  |---|---|---|
  | MATERIAL | CONFIRMED | MATERIAL |
  | MATERIAL | NOT CONFIRMED | NOT RESOLVED |
  | NOT RESOLVED | CONFIRMED | MATERIAL\* |
  | NOT RESOLVED | NOT CONFIRMED | NOT RESOLVED |

  \* My recommendation for the third row is MATERIAL: a seed-coherent shift that passes the r1 rule is a recipe
  bias whatever σ_ML is. That choice is the director's, but it must be written down before data.
- `--confirm` must refuse unless `--tag == "_s43"`.
- Treat a non-finite r as INCONCLUSIVE.
- Optionally, compute r on d/σ_ML (or d/a) instead of raw d. Raw d weights the result toward cells with a large
  cross section. Whichever is chosen, declare it now. Reporting Spearman alongside is cheap.

### R2. MINOR: an `on` job that fails after the build cannot be retried as written

**Where:** `sbatch_p5.sh:46-48`.
- Once `override_MaRES_0.{npz,json,sha256}` exist, a resubmitted seed-42 `on` job refuses with exit 3.
- That is fail-closed and arguably intended. But the retry procedure is not written down. For example: move the
  three files aside, then resubmit; or add a `reuse` mode that runs `sha256sum -c` like the seed-43 path.
- **Fix:** document it in DESIGN §5.

### R3. NIT

- **`smoke/noop_1B_MaRES_0_r2.json` is byte-identical to the round-1 file** (`d4c8f295…`). It records no driver
  digest, so it cannot show that it ran with `f71b5759…`.
  - My 1L rerun with `f71b5759…` covers this.
  - Future `test_noop.py` reports should record the sha256 of both drivers.
- **The ceiling table uses "P4 ≤ 0.41" worst-case**, which I did not verify (outside P5).
  - The 2.91 total leaves 0.09 node-h for retries.
  - The seed-43 gate's `sacct` budget check is the right control. It should use actual charges plus the pair's
    enforced 1.25.

## sha256 of re-reviewed files

| file | sha256 |
|---|---|
| DESIGN.md | `8e1843991e235b50fb6e82a6a63f4ac3f45061e4497561cbfaa1fec5562fa419` |
| driver_p5.py | `f71b5759bf01422fa8c6b6e5432885b34d1f127653df1165a0adb7527bdb12d2` |
| patch.diff | `e4ce8fba5635994687ac54a6479f30c108bf559c2f780fc42e2e392a15b4a89c` |
| analyze_p5.py | `33615b1f1816a2fe2ea6b07db057bfb338e13d13701347a1b182e1811da69cbf` |
| sbatch_p5.sh | `fc3fbc95ec84ec8f55f32093f20731febf235adb77c3a8e53cc966c356dd730a` |
| SHA256SUMS | `fceab800a4ba86fadcc76e24b47dc78057e1ae5cb79d8a9cbd4da6f4b727fdc2` |
| build_miss_override.py (unchanged) | `7f346e1af1688b6a43be540ef2a8c6f8456d76a1ea965613abce17263739296b` |
| test_noop.py (unchanged) | `cf9c9ecdd3df4af67be61081ee0f42c958340544efcf98d8d1b0d7ca4a006863` |
| smoke/noop_1B_MaRES_0_r2.json | `d4c8f2955234d6ffe24c9bf2704af1df449f1a79918ee016131fd0e4d948370c` |
| σ_ML input `uq_covariance_ml.root` | `3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9` |

**New reviewer artifacts** in `review-p5/`:

| file | sha256 prefix |
|---|---|
| `rr_checks.py` | `e635ee91` |
| `noop_1L_r2.json` | `4819b507` |
| `rev_checks_1L_r2.log` | `a67ddae4` |
