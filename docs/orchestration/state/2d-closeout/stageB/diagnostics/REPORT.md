# 2D closeout Stage B diagnostics: P4 (G1 census) and P5 (G2 miss-row weighting) outcomes

**CITABLE FOR:**
- the terminal outcomes of the two Stage B diagnostics that the Stage B recipe's finality depends on
  ([`../REPORT.md`](../REPORT.md) §1, R10, §7): **P4 G1 census MEASURED, G1 = 0** and **P5 G2 miss-row weighting
  NOT RESOLVED ABOVE TRAINER NOISE**;
- the charged compute of every job under
  [`AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md`](../../../../AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md);
- the P4 walltime-retry deviation and the P5 cap re-pricing, with the director's decision;
- the finding that a G2 repair needs no new event loop;
- the C07′ determination (data-POT counting is not documented as a band, so it is disclosed as omitted);
- the per-category median relative σ of the adopted and the C04+X01-repaired rollups;
- the Stage C input copy to CFS.

**NOT CITABLE FOR:**
- any quotable uncertainty, covariance or budget. Every σ and every shift here is **DIAGNOSTIC, NOT QUOTABLE**;
- adoption of anything, a KI-85 lift, coverage or calibration (Joseph's decisions);
- an unfolded central-value shift from G1: f_S is a first-order reco-level proxy (P4 DESIGN §6). With G1 = 0
  the proxy and any unfolded shift are both zero, but that is because the class is empty, not because the
  proxy was validated;
- a measurement of G2 in any universe other than `MaRES_0`, or of trainer noise beyond seeds 42 and 43;
- Stage C compute authority.

| field | content |
|---|---|
| `Owner` | 2D closeout executor (2d closer), directed by the paper-tighten lane under [`AUTHORIZATION-20261012-2d-closeout-delegation.md`](../../../../AUTHORIZATION-20261012-2d-closeout-delegation.md) |
| `Grant` | [`AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md`](../../../../AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md) (file sha256 `ac1bce59…`), ceiling **3.0 charged node-h**; deviation [`AUTHORIZATION-20261012-2d-closeout-stageB-p4-retry.md`](../../../../AUTHORIZATION-20261012-2d-closeout-stageB-p4-retry.md) (main `6c37ce18`, PR #101, file sha256 `ccca0901…`) |
| `Recipe decisions` | `docs/publication/DECISION-20261012-joseph-2d-closeout-recipe.md` (main `3921dec4`): R2 build the repair (since ADOPTED as VL175); R5 three-stream seed-42 bootstrap with purity recomputed; C07′ band only if documented; G3 `NormDISCC` null |
| `Branch` / `Base` | `closeout/stageb-diagnostics-20261012` / `origin/main` `b456fa4d` |
| `Packages` | P4: [`p4/DESIGN.md`](p4/DESIGN.md) (reviewed, `bb255f03`); P5: [`p5/DESIGN.md`](p5/DESIGN.md) (reviewed, routing frozen before data, `bb4a4f2d`; caps re-priced before any P5 job ran, `e2bce8c2`) |
| `Terminal outcomes` | P4: MEASURED (implicates / does not implicate `E_U`) or INCONCLUSIVE. P5: MATERIAL, NOT RESOLVED ABOVE TRAINER NOISE, NOT MATERIAL, or INCONCLUSIVE |
| `Compute` | **1.2524 of 3.0 charged node-h** (§5, every job's `sacct` row) |
| `Reviewer` | §8 |

## 1. Answer

| diagnostic | outcome | consequence for the Stage B recipe |
|---|---|---|
| **P4, G1 census** (reco-in/truth-out gap class) | **MEASURED; below the pre-declared materiality bound.** nG1 = 0 over all 12 playlists (489 MC files), so the G1 class is **empty** in the production CV configuration. Every gate passed; the no-op control is IDENTICAL; all 12 outputs are IDENTICAL to the May production files on common branches | **G1 is not a defect.** `E_U` is not implicated; no G1 repair, no re-adoption. Stage B §2.10's "≈1.8% of reco entries" code comment does not describe the shipped configuration |
| **P5, G2 miss-row weighting** (`MaRES_0`) | seed 42: **MEASURED, NOT RESOLVED ABOVE TRAINER NOISE** (median r1 0.305 > 0.10, but median r3 0.96 ≤ 2). Seed-43 confirmation: **NOT CONFIRMED (Pearson 0.113 < 0.5)**. **Final: NOT RESOLVED ABOVE TRAINER NOISE** | **No G2 repair is triggered**: the pre-declared rule routes to a repair only on MATERIAL. G2 stays an approximation of unresolved size below LightGBM trainer noise, measured in `MaRES_0` only (Flux, with c − 1 up to 18%, is unmeasured). How the recipe carries it (disclosure, or a repair anyway) is the director's and Joseph's call; if repaired, it is re-unfolds only (§3.3) |

Both were declared before data (P4 DESIGN §6; P5 DESIGN §6–7, the seed-43 routing frozen by the director's
2026-10-12 ruling before any seed-42 result). No threshold or rule was changed after a result was seen.

## 2. P4: G1 census

**Configuration.** 12 single-playlist jobs of the reviewed patched binary (`d1a7cf34…`, census on, production CV
configuration) and one no-op control, `ctl1L`: the unpatched copy (`1ab7525e…`) on 1L. `ctl1L` is a control
and its charge counts toward the ceiling (§5). Scripts: [`p4/sbatch_p4.sh`](p4/sbatch_p4.sh),
[`p4/analyze_p4.py`](p4/analyze_p4.py) (`c22f73e1…`, byte-identical on NERSC).

**Result** ([`p4/result/result.json`](p4/result/result.json), sha256 `029055bb…`; analysis on NERSC
`login24`, 2026-10-13, rc 0, full set, so no SMOKE/SUBSET prefix):
- **Gates:** none failed. Binary sha256 equal to the reviewed ones; provenance rc 0 in every job; census
  `selftestN` = `nSelftestInjected` = 0; counter identity `nBkgSkipped` = `nBkgSkippedInReco` + `nG1` +
  `nG1DupKey` holds (20,498,013 = 20,498,013 + 0 + 0).
- **No-op control:** `ctl1L` vs `1L` **IDENTICAL** (strict).
- **Bridge to May production:** all 12 playlist main outputs are **IDENTICAL on common branches** to the May
  per-playlist files behind `E_U`'s omnifile. The census was therefore taken on `E_U`'s own input.
- **Pins:** `reported_cells.py` `2ddf7c9f…`, `E_U` `4f5a1b6d…`, repaired σ JSON `4e48f639…`.
- **Census totals** over 12 playlists: nTruthFail 243,719,647; nTruthFidFailStored 36,089,542
  (DupKey 158); `nSigLoopNoTruth` = `nSigLoopNoTruthPassReco` = 0; **nG1 = 0**, nG1DupKey 0, status 0/1/2 all 0,
  **wG1 = 0**.
- **Denominators:** S = 16,637,289.2, B = 560,873.6 (weighted, POT-scaled 0.21241), D = 4,091,707.
- **Materiality:** integral f_S = f_SB = f_D = 0 on the 224-cell grid; per-cell max f_S = 0; 0 cells with
  f_S ≥ σ_rel/3; 0 reported cells with S = 0.

**Power.** The analysis smoke on a self-test census (P4 DESIGN §4, review M2) exercised the non-empty path
(wG1 4,273.9, integral f_S 0.1405 against ≈ 1/7 expected) and the self-test gate fired as designed. A zero here
is therefore an empty class, not a blind census. Not exercised on real data: the status-1 mask path, since no
real G1 row exists (P4 DESIGN §6 item 3).

## 3. P5: G2 miss-row weighting (`MaRES_0`)

**Configuration.** Run *a*: the production driver (miss rows carry the CV proxy, then ÷ c). Run *b*:
`driver_p5.py` with the miss rows carrying their own `mc_truth_denom` `MaRES_0` weight (override built by
`build_miss_override.py`). Shared QOS, 128 CPUs, `OMP_NUM_THREADS=64`; `sbatch_p5.sh` `2b4689a7…`;
`analyze_p5.py` `8f37fd7f…` (byte-identical on NERSC).

### 3.1 Seed 42

[`p5/result/report_s42.json`](p5/result/report_s42.json), sha256 `0ae8ff5e…`. Inputs: a
`xsec_MaRES_0_off.root` `c0f02713…`, b `xsec_MaRES_0_on.root` `4d7e2f43…`, CV `4f5a1b6d…`, July j0 `80e1e04e…`
/ j1 `872715cc…`, ML `3b6b48ec…` (all paths in the JSON).

- **Gates:** all pass. G-a override ALL_PASS, n_override 8,999,007, sha matched; G-b max|c_b − 1| = 1.9e-14;
  G-c c_a vs July = 0.0; G-p provenance true; G-f all r1, r3 finite; ML pinned. **Outcome MEASURED.**
- **Bridge:** |a − July j0|/σ_band max 1.5e-9. Run *a* reproduces the July `MaRES_0` product.

| metric | median | p84 | max |
|---|---|---|---|
| c_off − 1 | 0.58% | 2.26% | 6.76% |
| relative change b/a | 0.16% | 0.60% | 2.81% |
| r1 = \|d\|/σ_band (205 cells) | **0.305** | 1.40 | 123.8 |
| r1 over the 188 floored cells (σ_band ≥ 1e-3·CV) | 0.276 | 0.98 | **7.37** |
| r2 = \|d\|/\|a − CV\| | 0.225 | 1.01 | 317.1 |
| r3 = \|d\|/σ_ML | **0.962** | 2.16 | 10.9 |

- σ_ML/σ_band median 0.299; integral relative change 2.9e-6.
- corr(d/a, c_off − 1): Pearson −0.056, Spearman −0.0004. The change does **not** track the completeness
  deviation, which G2's mechanism predicts it would if it were a coherent weighting effect.
- **Routing:** the r1 rule holds (median 0.305 > 0.10; floored max 7.37 > 0.30), and median r3 = 0.96 ≤ 2, so
  **NOT RESOLVED ABOVE TRAINER NOISE**: the shift is large against the band but not resolved above the
  LightGBM seed noise.

### 3.2 Seed-43 confirmation

**Trigger and check.** Seed 42 routed NOT RESOLVED, so DESIGN §7's conditional pair applied. The pre-declared
budget check on actual charges: P4 0.5290 + P5 seed-42 0.3756 = **0.9046** node-h actual (every `2dc_*` row,
§5), plus the pair's enforced **1.75** = **2.6546 ≤ 3.0: PASS** (margin 0.345). The director recomputed
0.9046 independently from `sacct` and gave the go-ahead (2026-10-13), with the conditions: routing,
thresholds and the r1 rule on d̄ stay frozen; if the pair fails or times out, P5 is final at seed-42-only NOT
RESOLVED, with no retry.

**Jobs.** `2dc_B5_off_s43` 59727563 (cap 01:30:00) and `2dc_B5_on_s43` 59727564 (cap 02:00:00), submitted
with the exact commands in DESIGN §7, after re-checking `sbatch_p5.sh` = `2b4689a7…` on NERSC.

**Result** ([`p5/result/report_s43.json`](p5/result/report_s43.json), sha256 `eb0f92b7…`; inputs a
`xsec_MaRES_0_off_s43.root` `33f35f8a…`, b `xsec_MaRES_0_on_s43.root` `ff6189a1…`, the same CV, July and ML
pins; analysis on NERSC 2026-10-13, rc 0):
- **Seed-43 gates:** all pass (G-a true; G-b 1.9e-14; G-c 0.0; G-p true; G-f true; ML pinned). **MEASURED.**
  Seed 43 on its own also routes NOT RESOLVED (median r1 0.411, floored max 10.1; median r3 1.23).
- **Confirmation over the 188 floored cells:** Pearson(z43, z42) = **0.113** (< 0.5), Spearman 0.213.
  **Verdict NOT CONFIRMED.**
- **Final routing** (DESIGN §7 row "NOT RESOLVED + NOT CONFIRMED"): **NOT RESOLVED ABOVE TRAINER NOISE.**
  The r1 rule on d̄ = (d42 + d43)/2 holds (median 0.302, floored max 4.87), but it is consulted only after
  CONFIRMED, so it does not enter the routing.

| metric | seed 42 | seed 43 |
|---|---|---|
| relative change b/a, median / max | 0.16% / 2.81% | 0.22% / 2.59% |
| r1 median (205 cells) / floored max | 0.305 / 7.37 | 0.411 / 10.10 |
| r3 median / p84 / max | 0.962 / 2.16 / 10.9 | 1.23 / 2.56 / 8.70 |
| integral relative change | 2.9e-6 | −1.6e-4 |
| corr(d/a, c_off − 1), Pearson / Spearman | −0.056 / −0.0004 | −0.009 / −0.006 |

**Reading (descriptive, not a routing input).** The on-minus-off shift is about the size seed noise alone
predicts (DESIGN §7: median r1 ≈ 0.28 from σ_ML/σ_band = 0.30), it is not reproduced from one seed to the next
(per-cell z correlation 0.11), and in neither seed does it track the completeness deviation that G2's mechanism
would drive. So no G2 effect was resolved in `MaRES_0`; the measurement cannot exclude one below trainer noise.
The seed-43 bridge |a − July|/σ_band (median 0.41, max 60) only shows that run *a* at seed 43 differs from the
seed-42 July product by trainer noise; the bridge is meaningful at seed 42 only, where it is 1.5e-9.

### 3.3 No new event loop for a G2 repair

The correct per-event universe truth weights of the miss rows are already in each universe omnifile's
`mc_truth_denom` tree (`w_truth_<band>_<idx>`), and `build_miss_override.py` attaches them exactly (G-a:
8,999,007 rows; G-b: c_b = 1 to 1.9e-14). **A G2 repair of any vertical universe is therefore re-unfolds
only.** This revises Stage B §7's contingency, "re-running ≈ 170 truth-weight-varying universes, 43–129
node-h, plus event loops", to the re-unfold cost alone (P5 DESIGN §2 gives the mechanism).

## 4. Deviations and pricing errors

### 4.1 P4 walltime: one retry under the director's decision

**Cause.** P4 DESIGN §5 priced walltime from the one-file login-node smoke ("1M's expected wall time is 98 ×
17–30 s ≈ 0.5–0.8 h, inside 2 h"). The job's truth and signal-reco loops scale with entries, not per file at
the smoke's rate: 1M took **5:04** (≈ 186 s per file). 1A timed out at 02:00:04; 1D, 1E, 1F, 1G and 1M were
projected to; no G1 number from any of them was read. The error hit every job the same way, so the retry
does not select on a result.

**Director's decision** (cross-session message, about 21:45Z 2026-10-12), quoted:

> P4 retry deviation: YES, with the conditions below. Cancel the doomed jobs now.
>
> I checked your facts with sacct at about 21:40Z and they match: 1A TIMEOUT at 02:00:04; 1B, 1C and 1L
> COMPLETED; 1D, 1E, 1F, 1G and 1M RUNNING; 1N, 1O, 1P, ctl1L and P5 PENDING.
>
> WHY THIS IS ALLOWED. The retry rule exists so that a result never selects a rerun. Here the cause is the
> pricing error in DESIGN §5, which hits every job the same way. The decision covers every timed-out job
> whatever its content, and no G1 number from any retried job has been read. The committed grant
> (AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md) already allows a walltime under 12 h per job and
> retries inside 3.0 node-h. So this is a deviation from your DESIGN's retry rule that stays within the grant,
> and I can make it as director. I'll also commit a short record of this decision to main and send you its
> path. Don't wait for it.
>
> (a) APPROVED: cancel 1D, 1E, 1F, 1G and 1M now, and the pending 1N.
>
> (b) APPROVED, WITH ONE CHANGE TO WALLTIME. 6 h is not safe for every job. From 1M's own rate (8% of 16.3 M
> in 18 min), its signal-reco loop alone takes about 3.75 h, before the background and data loops. 1N is
> unmeasured. So:
> - 1A, 1D, 1E, 1F and 1G get --time=06:00:00.
> - For 1M and 1N, set the walltime to 1.5 × a projection from measured rates, rounded up and capped at
>   11:30:00. Use 1M's signal-reco rate per entry, and 1A's or 1C's per-entry and per-data-file rates for the
>   background and data loops, scaled to each job's entry and file counts. Write the projection arithmetic in
>   the REPORT. If a projection exceeds 11:30, don't submit that job: report to me. Splitting it would change
>   the design.
> - Everything else stays identical, as you listed: the sha-checked binary, script, job names, 4 CPUs, 7600M.
>   Partial output goes to out/<tag>.failed-<jobid> by the recorded move. Don't read G1 numbers from partial
>   outputs.
>
> ONE RETRY ONLY. Any job that times out again, 1O, 1P and ctl1L included, is recorded INCONCLUSIVE for
> walltime. No further retry without asking me. A job that fails any other way follows the DESIGN rule
> unchanged.
>
> BUDGET. Recompute from actual sacct charges before each launch. Worst case is still under 3.0 with P5
> seed-42: 0.89, plus up to about 0.17 for the longer 1M and 1N caps, plus 1.25. The seed-43 pair keeps your
> declared check on actual charges at its launch; if it fails, stop and ask.
>
> P5 CHECK BEFORE IT STARTS. Was the walltime for 59713367 and 59713368 (1:00 and 1:30) priced from the same
> one-file smoke? If so, re-price it from 1A's or 1C's measured loop rates now. If either cap is short, cancel
> and resubmit it with the corrected cap (same rule: 1.5 × projection, under 12 h) before it runs, rather than
> retrying it after a TIMEOUT. Tell me which way it went.
>
> (c) APPROVED: record the deviation, its cause, this decision and the per-job walltimes in the diagnostics
> REPORT. Quote this message as the director's decision.
>
> Unchanged: if G1 implicates E_U, tell me at once.

The committed record is
[`AUTHORIZATION-20261012-2d-closeout-stageB-p4-retry.md`](../../../../AUTHORIZATION-20261012-2d-closeout-stageB-p4-retry.md)
(main `6c37ce18`, PR #101).

**Moves.** Partial outputs were moved, sha256-verified, to `out/<tag>.failed-<jobid>` before the retries
([`p4/retry/retry_moves.log`](p4/retry/retry_moves.log)): 1A (TIMEOUT), 1D, 1E, 1F, 1G, 1M (CANCELLED), 4
files each; 1N was cancelled before it started and had no output.

**Projection arithmetic** ([`p4/retry/project_walltime.py`](p4/retry/project_walltime.py) →
[`p4/retry/project_walltime.txt`](p4/retry/project_walltime.txt)).
- Model: elapsed = s + a·N_truth + b·N_sig [+ c·N_bkg + d·N_data for completed jobs], non-negative least
  squares over 9 points (1B, 1C, 1L completed; 1A, 1D, 1E, 1F, 1G, 1M partial, with their own progress
  counters). Fit: truth 0.216 min/M, signal-reco 8.508 min/M, rss 9.06.
- Signal rate used: max(fitted 8.508, 1M's own 6.280) = 8.508 min/M, the more conservative of the two; the
  director's message named 1M's rate.
- Post-signal (background + data) rate: the worst completed job, 1B, 8.23 min per M reco entries.
- Projection T = 0.216·N_truth + (8.508 + 8.23)·N_reco; cap = 1.5·T rounded up, ≤ 11:30.
- **1N's cap rests on a proxy, not a measurement.** 1N never ran, so its entry counts were scaled from its MC
  size (1.1027 TB) at 1A's entries per TB (the worst measured); 1O and 1P the same way.

| job | N_truth (M) | N_reco (M) | projected | ×1.5 | cap | actual | actual/projected | state |
|---|---|---|---|---|---|---|---|---|
| 1A | 22.19 | 7.60 | 2.20 h | 3.30 h | 6 h | 1:53 | 0.86 | COMPLETED |
| 1D | 33.58 | 11.36 | 3.29 h | 4.93 h | 6 h | 4:14 | **1.28** | COMPLETED |
| 1E | 28.12 | 9.50 | 2.75 h | 4.13 h | 6 h | 2:52 | 1.04 | COMPLETED |
| 1F | 39.08 | 12.91 | 3.74 h | 5.61 h | 6 h | 3:46 | 1.01 | COMPLETED |
| 1G | 32.46 | 10.94 | 3.17 h | 4.75 h | 6 h | 3:14 | 1.02 | COMPLETED |
| 1M | 50.44 | 16.32 | 4.73 h | 7.10 h | 8 h | 5:04 | 1.07 | COMPLETED |
| 1N (proxy) | 34.62 | 11.86 | 3.43 h | 5.15 h | 6 h | 2:44 | 0.80 | COMPLETED |
| 1O (proxy, first run) | 10.39 | 3.56 | 1.03 h | 1.55 h | 2 h | 0:46 | 0.75 | COMPLETED |
| 1P (proxy, first run) | 13.76 | 4.71 | 1.36 h | 2.05 h | 2 h | 1:05 | 0.80 | COMPLETED |

1P's 2 h cap was 1.46× its projection, below the 1.5 rule; the director accepted it because 1P kept its one
walltime retry. It was not needed. **No job timed out on its retry; nothing is INCONCLUSIVE for walltime.**
For Stage C pricing: the projection underestimated by up to 28% (1D), inside the 1.5 margin.

### 4.2 P5 caps re-priced before any P5 job ran

Under the director's "P5 CHECK BEFORE IT STARTS", the first P5 pair (59713367/8, 1:00 and 1:30) was confirmed
to have been priced from the same one-file smoke, and was cancelled while still PENDING (0 s charged). The
caps were re-priced from the measured full-read universe unfold (max 2,738 s in the July sweep, × 1.5 = 68
min): `off` 01:30:00, `on` 02:00:00 (adding the 5–10 min override build). Enforced worst case 1.75 node-h per
pair. P5 DESIGN §5 amendment; `sbatch_p5.sh` `fc3fbc95…` → `2b4689a7…` (`e2bce8c2`). Actual: off 12:56, on
32:08 (seed 42).

### 4.3 Recorded, not changed

`analyze_p5.py`'s docstring still says the seed-43 check uses "the pair's enforced 1.25 node-h". The DESIGN §5
amendment set it to 1.75 and the check in §3.2 used 1.75. The script's sha (`8f37fd7f…`) is pinned in the
reviewed package, so the stale docstring is recorded here and the script is left unchanged (director,
2026-10-13).

## 5. Compute

Charge = `ElapsedRaw` × billing / 256 (P4: 4 CPUs, 7600M ≤ 4 × 1905 MB, billing 4; P5: 128 CPUs, billing 128).
Every `2dc_*` job is listed; `sacct -X -u josephrb` since 2026-10-11 shows no other `2dc_*` job (the `xrl_*`
and `wclos5d` rows belong to other lanes). Raw rows: [`compute/sacct_charges.txt`](compute/sacct_charges.txt).

| job | id | state | elapsed | node-h |
|---|---|---|---|---|
| 1A (first) | 59713341_0 | TIMEOUT | 2:00:04 | 0.0313 |
| 1B | 59713345_1 | COMPLETED | 0:35:37 | 0.0093 |
| 1C | 59713348_2 | COMPLETED | 1:03:56 | 0.0166 |
| 1D (first) | 59713349_3 | CANCELLED | 1:09:01 | 0.0180 |
| 1E (first) | 59713353_4 | CANCELLED | 0:56:40 | 0.0148 |
| 1F (first) | 59713356_5 | CANCELLED | 0:55:27 | 0.0144 |
| 1G (first) | 59713358_6 | CANCELLED | 0:42:14 | 0.0110 |
| 1L | 59713360_7 | COMPLETED | 0:14:16 | 0.0037 |
| 1M (first) | 59713362_8 | CANCELLED | 0:20:42 | 0.0054 |
| 1N (first) | 59713363_9 | CANCELLED (pending) | 0 | 0 |
| 1O | 59713364_10 | COMPLETED | 0:46:26 | 0.0121 |
| 1P | 59713365_11 | COMPLETED | 1:05:07 | 0.0170 |
| ctl1L (control) | 59713366_12 | COMPLETED | 0:15:35 | 0.0041 |
| 1A (retry) | 59717845_0 | COMPLETED | 1:52:56 | 0.0294 |
| 1D (retry) | 59717848_3 | COMPLETED | 4:13:34 | 0.0660 |
| 1E (retry) | 59717850_4 | COMPLETED | 2:52:02 | 0.0448 |
| 1F (retry) | 59717852_5 | COMPLETED | 3:45:48 | 0.0588 |
| 1G (retry) | 59717855_6 | COMPLETED | 3:14:16 | 0.0506 |
| 1M (retry) | 59717856_8 | COMPLETED | 5:03:47 | 0.0791 |
| 1N (retry) | 59717858_9 | COMPLETED | 2:44:03 | 0.0427 |
| **P4 total** | | | | **0.5290** |
| B5_off, B5_on (first, pending) | 59713367, 59713368 | CANCELLED (pending) | 0 | 0 |
| B5_off seed 42 | 59717961 | COMPLETED | 0:12:56 | 0.1078 |
| B5_on seed 42 | 59717963 | COMPLETED | 0:32:08 | 0.2678 |
| B5_off seed 43 | 59727563 | COMPLETED | 0:17:14 | 0.1436 |
| B5_on seed 43 | 59727564 | COMPLETED | 0:24:30 | 0.2042 |
| **P5 total** | | | | **0.7233** |
| **grant total** | | | | **1.2524 of 3.0** |

All runs wrote only under `/pscratch/sd/j/josephrb/2d-closeout-stageB-diag-20261012/`. The production driver
and event loop on `main` are untouched.

## 6. Other Stage B items closed here

### 6.1 Stage C input copy to CFS

[`copy/copy_stageC_inputs.sh`](copy/copy_stageC_inputs.sh) on `dtn01`, 2026-10-12 16:05–16:16Z
([`copy/copy.log`](copy/copy.log)): the 10 active merged 5D files and the two Stage B npz files to
`/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-inputs-20261012/`, **SHA256 MATCH: 10 active + 2 npz**
(source and destination sums committed beside the log), 539 GB, CFS free after 18,992 GB (≥ 3 TB rule met),
destination made read-only. This closes Stage B §5's "active files durability" row.

### 6.2 C07′, data-POT counting: NOT DOCUMENTED, disclose as omitted

[`c07prime/DETERMINATION.md`](c07prime/DETERMINATION.md). Neither MAT nor the published analysis
(arXiv:2106.16210v4) defines a POT-counting band: the paper's only normalization term is the 1.4% target-nucleon
uncertainty (MAT `MnvNormalization.h:100-103`, `mass_scale_err = .014`), and MAT's `"POT_Scale"` is only a
plot-group label (`MnvPlotter.cxx:401-406`). The 2% POT-counting term of the NuMI flux prediction (Aliaga et al.,
arXiv:1607.00704 §IV) sits inside the flux band by convention. Under Joseph's C07′ rule the band is **omitted
with a disclosure**, which should say that the flux band carries the POT-counting term, so a separate band
would double-count it. Two links are inferred, not verified (the ME PPFX universes carrying that term; the ν-e
constraint absorbing it); see the determination.

### 6.3 Per-category median relative σ, adopted vs C04+X01-repaired

[`c04-grouped/group_medians.py`](c04-grouped/group_medians.py) (`7e02decc…`) →
[`c04-grouped/group_medians.json`](c04-grouped/group_medians.json) (`7927c51e…`); 205 reported cells, `E_U`
denominator, grouping by `analyze_universes.category_for_band` (what the Fig. 6/7 producer imports).
DIAGNOSTIC, NOT QUOTABLE.

| category | adopted | repaired |
|---|---|---|
| Flux | 4.993% | **3.655%** |
| Muon reconstruction | 3.366% | **3.421%** |
| Models | 1.479% | 1.479% |
| Normalization | 1.400% | 1.400% |
| Hadronic response | 0.758% | 0.758% |
| Statistical | 0.674% | 0.674% |
| universe total / combined | 6.830% / 6.869% | **6.043% / 6.084%** |

- **Grouping caveat:** the current grouping puts the flat 1.4% under Normalization. The note's App. A wording
  ("legacy": GENIE `Norm*` bands → Normalization, flat 1.4% → Models) gives Models 2.034% and Normalization
  0.081%; the JSON carries both, and the legacy one reproduces App. A.
- Only the `full_Flux` and `full_Muon_Energy_MINOS` diagonals change
  ([`c04-grouped/muon_check.py`](c04-grouped/muon_check.py), `7c208124…`); the per-cell muon-reconstruction σ
  ratio is median 0.992, range 0.886–1.128 (the median of the category rises while the per-cell median falls).
- The statistical block equals the VL170 boot300 one to 7.2e-14.

## 7. Updates made to the Stage B REPORT

Dated 2026-10-13 corrections in [`../REPORT.md`](../REPORT.md): the G1 and G2 rows of §1, R10 of §4, the G1/G2
rows of §5, the G2-repair contingency of §7, and §11's limits now cite this REPORT's outcomes. No other text
changed.

## 8. Independent review

Pending: one fresh read-only verifier on this commit (the grant's reviewer requirement). Its verdict and the repairs will be recorded here.

## 9. Limits

- P5 measures one vertical universe (`MaRES_0`) at seeds 42 and 43. Other truth-weight-varying universes (Flux
  up to 18% completeness deviation) are not measured; the routing does not extrapolate to them.
- σ_ML is the pinned LightGBM seed-scan σ; trainer noise for a single universe pair is taken from it, not
  re-measured.
- P4's status-1 mask path has no real-data exercise (no G1 row exists).
- The 1N, 1O and 1P walltime projections rest on a size proxy; all three finished inside their caps.
- Same-model caveat: the executor, the package reviewers and the verifier are all Claude Opus 5.5.
