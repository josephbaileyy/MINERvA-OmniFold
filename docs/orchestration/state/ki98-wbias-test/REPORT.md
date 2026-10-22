# Report: the KI 98 W-bias confirming test (2026-10-22)

**By** the measurement session, under [`DECLARATION.md`](DECLARATION.md) (sha256 a941ea10…, merged in PR #224) as
bound in [`BINDING.md`](BINDING.md) (PR #225). **Verdict by the declared rule: UNDETERMINED.**

**CITABLE FOR:**
- the verdict UNDETERMINED under the declared rule, on the primary band (EW, W ≥ 3), with the numbers below;
- the measured R, D and SE of each arm for the reported functionals and bands;
- the descriptive 400-seed read of the existing tilt and nominal products;
- the compute charged (0.197 CPU node-h).

**NOT CITABLE FOR:**
- "the W-growing residual is the estimator's": the rule's ESTIMATOR branch did **not** fire;
- "the B/S change is excluded" as a verdict: the B/S CHANGE branch did not fire, but the rule has no exclusion branch;
- any mechanism, including the untested reading below;
- any coverage claim, other amplitudes, the q3 grid point, or nuisance settings away from nominal.

## Order and provenance

All times are PDT on 2026-10-22, re-measured from git and from the file mtimes on Perlmutter.
1. 02:18:24: the binding merge (5df6f96a).
2. 02:18:52: the scaled dump was written (`receipts/inputs/bkg_dump_x0.9.npz.receipt.json`).
   - sha256 ab204d13…;
   - bkg_w total 119132.37 → 107219.13;
   - bkg_nd agrees with the bkg_w-weighted histogram of bkg_reco to 0.0.
3. 02:19:05: jobs 60100087 and 60100088 were submitted (`receipts/submitted.txt`).
4. 02:19:23: the existing read finished (`receipts/existing.json`).
5. 03:41:53: both jobs started. They ended at 03:47:52 and 03:47:42.
6. 03:49:17: `ki98_read.py analyze` wrote `receipts/ki98.json` (sha256 89332703…). It exited with rc 0 and empty stderr.

**Tasks.** All 16 tasks logged `rc=0` (`receipts/logs/unf-task*.log`), and both jobs ended `COMPLETED 0:0`
(`receipts/sacct.txt`).

**Products.** The 16 products (180 KB each) are committed here as `receipts/ki98_*.npz`. Each was checked against
`receipts/PRODUCTS.sha256`, which was written on Perlmutter from `measurement-paper/ki98-wbias/unf/`. The digests also
appear in `ki98.json` → `products`. The guard inventories and env logs are in `receipts/unf/`.

**Analyze checks.**
- `failures` is empty: every product passed the declared meta checks (truth, amplitude, no-background flag, seed,
  split key, config, estimator seed, iterations, threads, code sha256, background-dump sha256, finiteness).
- The control `ki98_ctl_a_s204000` equals the existing `eavail_tilt_a0.2_s204000` bitwise in `xsec_flat`,
  `xtrue_flat` and `shape`.
- (b) and (c) share each seed's truth with (a).
- σ recomputed from the 200 replicas matches interim_400 to 3.0e-15 relative.
- The inputs carry their declared digests: contract d54fd7c9…, interim aa574c17…, bias_correction 6c49c66c….

No re-run was needed and no seeds were added.

## Result (primary band: EW, W ≥ 3)

k = 2.776. ρ is in units of the Tier-S statistical σ.

| quantity | value | SE | k·SE | rule test | outcome |
|---|---:|---:|---:|---|---|
| R_a | +2.287 | 0.721 | 2.002 | R_a > k·SE_a | **resolved** |
| R_c | +3.400 | 0.647 | 1.795 | B/S: \|R_c\| ≤ k·SE_c | fails |
| D_c = ρ_a − ρ_c | −1.113 | 0.206 | 0.572 | estimator: \|D_c\| ≤ k·SE_Dc | fails |
| R_b | +2.840 | 0.459 | 1.274 | estimator: R_b > k·SE_b | holds |
| D_b = ρ_a − ρ_b | −0.553 | 0.479 | 1.331 | estimator: \|D_b\| ≤ k·SE_Db | holds |

- **(c)** shows **neither** pattern. D_c is resolved, but it is **negative**: scaling the background by 0.9 raised the
  residual by 1.11σ (5.4 SE_Dc). The B/S hypothesis predicted a positive D_c with R_c near zero.
- **(b)** shows the **estimator pattern**. The residual persists with no background at all (R_b = +2.84 against its
  own no-background reference β_nb), and it does not differ from (a) within k·SE_Db.
- **Verdict** (rule step 3): ESTIMATOR needs (c) to show the estimator pattern, and B/S CHANGE needs (c) to show the
  B/S pattern. (c) shows neither, so the verdict is **UNDETERMINED**.
- **Secondary band** (EW, W 2.2–3): R_a = +0.898 (k·SE_a = 1.576) is not resolved on these five seeds, so it is
  UNDETERMINED as well. It is concordant in verdict and adds nothing.
- The primary resolution is narrow: R_a exceeds k·SE_a by 0.29. S_β (the d1 correction's own SE term, 0.284) is part of
  SE_a and SE_c, but not of SE_Dc.

## All reported functionals (`receipts/ki98.stdout`)

Five-seed means, with SE in parentheses.

| functional | R_a | R_c | R_b | D_c | D_b |
|---|---|---|---|---|---|
| EW9 | +1.55 (0.74) | +1.49 (0.71) | +1.52 (0.77) | +0.06 (0.06) | +0.03 (0.34) |
| EW10 | +1.88 (0.54) | +1.67 (0.53) | +2.19 (0.59) | +0.22 (0.10) | −0.30 (0.22) |
| EW16 | +2.05 (0.53) | +1.74 (0.56) | +2.39 (0.56) | +0.31 (0.12) | −0.34 (0.27) |
| EW17 | +2.93 (0.66) | +4.04 (0.61) | +3.23 (0.53) | −1.11 (0.19) | −0.30 (0.53) |
| J116 | +2.27 (0.82) | +2.24 (0.89) | +2.96 (0.84) | +0.04 (0.11) | −0.68 (0.34) |
| J224 | +2.83 (0.50) | +3.25 (0.47) | +3.51 (0.54) | −0.42 (0.08) | −0.68 (0.48) |
| total_integrated | −0.26 (0.42) | −0.51 (0.42) | −0.20 (0.32) | +0.26 (0.03) | −0.05 (0.18) |
| EW_all_ones | −0.54 (0.38) | −0.50 (0.37) | −0.34 (0.57) | −0.04 (0.03) | −0.20 (0.39) |
| band EW W < 1.4 | −0.26 (0.42) | −0.25 (0.42) | −0.30 (0.47) | −0.01 (0.03) | +0.03 (0.24) |
| band EW W 1.4–2.2 | +0.39 (0.46) | +0.30 (0.42) | +0.48 (0.35) | +0.09 (0.08) | −0.08 (0.39) |
| band EW W 2.2–3 | +0.90 (0.57) | +0.60 (0.59) | +1.65 (0.54) | +0.30 (0.12) | −0.75 (0.15) |
| **band EW W ≥ 3** | **+2.29 (0.72)** | **+3.40 (0.65)** | **+2.84 (0.46)** | **−1.11 (0.21)** | **−0.55 (0.48)** |
| band J W ≥ 2.2 | −0.21 (0.77) | −0.56 (0.76) | +0.08 (0.49) | +0.35 (0.04) | −0.29 (0.25) |

Descriptive notes (no rule attached):
- The sign of D_c is not uniform. It is positive and small in EW10 and EW16 (W 2.2–3) and negative in EW17 and J224.
  The primary band's D_c equals EW17's to the printed precision.
- All 153 functionals are in `ki98.json` → `functionals`.

## Separate read: the existing 400 seeds (`receipts/existing.json`, descriptive)

Tilt seeds are 204000–204399 and nominal seeds 200000–200399. Each cell gives ρ mean (SE), and e is the raw relative
bias f̂/f_true − 1.

| functional | tilt ρ | tilt e | nominal ρ | nominal e |
|---|---|---:|---|---:|
| EW9 | +1.354 (0.043) | +0.41% | −0.503 (0.043) | +0.15% |
| EW10 | +1.832 (0.040) | +0.95% | −0.530 (0.041) | +0.44% |
| EW16 | +2.014 (0.044) | +0.92% | −0.492 (0.045) | +0.45% |
| EW17 | +2.620 (0.053) | −2.95% | +0.233 (0.053) | −3.88% |
| J116 | +2.050 (0.046) | +0.42% | −0.329 (0.044) | −0.01% |
| J224 | +2.531 (0.047) | −0.36% | −0.523 (0.048) | −1.13% |
| total_integrated | −0.375 (0.042) | +0.26% | −0.618 (0.049) | +0.25% |
| EW_all_ones | −0.056 (0.046) | +0.08% | −0.350 (0.045) | +0.05% |
| band EW W < 1.4 | −0.055 (0.047) | +0.05% | −0.342 (0.046) | +0.02% |
| band EW W 1.4–2.2 | +0.482 (0.046) | +0.17% | −0.199 (0.049) | +0.09% |
| band EW W 2.2–3 | +0.895 (0.044) | +0.73% | −0.600 (0.044) | +0.45% |
| band EW W ≥ 3 | +2.080 (0.055) | −2.89% | +0.163 (0.055) | −3.58% |
| band J W ≥ 2.2 | −0.421 (0.043) | +0.70% | −0.672 (0.047) | +0.66% |

- These replace the diagnosis's inferred values (EW17 +2.60, EW10 +1.82), which they confirm to within 0.02.
- The five-seed R_a for the primary band (+2.29 ± 0.72) is consistent with the 400-seed +2.080 (0.055).
- The nominal ρ is not zero. It runs from about −0.2 to −0.7 in most functionals and is +0.163 in the primary band.
  So the d1 β (from 9 development experiments) does not fully match the 400-seed nominal mean. This is descriptive and
  is not part of the rule.

## An untested reading (offered as a question, not a finding)

- A smaller background raises the residual in the primary band. That is the opposite of the declared B/S hypothesis.
- One reading consistent with the sign: the purity method's own closure bias at W ≥ 3 (about −4% nominal, KI 75) grows
  with B/S. In (a), B/S is 1.11× nominal, so the nominal-B/S β under-corrects that negative bias and pulls (a)'s
  residual *down*; (c) restores nominal B/S and removes that offset.
- On that reading, the B/S change *masks* part of a positive residual rather than causing it.
- **Nothing here tests that.** The declaration excludes the mechanism, and adding seeds or arms after this result is
  not allowed.

## Compute

| job | name | QOS | state | elapsed | charged CPU node-h |
|---|---|---|---|---:|---:|
| 60100087 | ki98_n1 (lines 0–7) | regular | COMPLETED 0:0 | 359 s | 0.0997 |
| 60100088 | ki98_n2 (lines 8–15) | regular | COMPLETED 0:0 | 349 s | 0.0969 |
| **total** | | | | | **0.197** (cap 0.5) |

- Charge = ElapsedRaw × billing/256/3600, with billing = 256 (`LEDGER.tsv`).
- The existing read and the analyze ran on a login node, not in a job.
- Every output is on `$PSCRATCH`; nothing was written to CFS.
