# s5p (`OI-193`): independent cross-check of the recovered lost seeds, frozen-S reading (2026-10-06)

**CITABLE FOR:**
- this lane's independent recomputation, with its own code, of the statistics of the 277 recovered lost seeds under
  the agreed frozen-S reading: identity, determinism, per-variant counts, the resolved claims and Holm decisions of
  the three families, the ruled labels, and power;
- its side-by-side agreement with the campaign's `frozen-s.json`.

**NOT CITABLE FOR:**
- any change to a primary decision, label, frozen product, B or rule: the recovery is report-only (owner decision 2);
- the union reading (`resolved-evaluate.json`), which this lane did not recompute;
- the scientific adequacy of the calibration.

Authority: owner decision 2, "Recover lost seeds" (`DECISION-20261005-s5p-recompute-extension-and-lost-seed-
recovery.md`, origin/main `d2fe7525`). Definitions agreed with the campaign before any product existed (handoff
§5.11, 2026-10-05). Reviewed procedure: `PROCEDURE-20261005-s5p-lost-seed-recovery.md` revision 5 (`51648245`).
This lane did not read the campaign's recovery tool.

## 1. What was run

- **Script:** `state/s5p/recompute/s5p_recompute_recovery_crosscheck.py` (sha256 `cc9ec91e510cec2e…`). It is
  report-side, not reviewed code, and changes nothing.
- **Statistics:** every one comes from the reviewed evaluator `s5p_recompute.py` at `02df81e6` (sha256
  `81b879ae…`, deployed in `code-ext/`): loading, surrogates, prediction-error draws, the shift S, `null_ensembles`,
  `rank_counts`, `holm_determined`, `robust_labels` and `power_of_set`.
- **Inputs:** this lane's terminal `recompute.json` (`final-ext`, `550a95fc…`), its own `seed-disposition.json`
  (`eb780ffa…`), the recovered products `$NS/recovery/recovery/{cal,pow}/`, and the determinism reruns
  `$NS/recovery/determinism/`.
- **Run:** login38, 2026-10-06, about 62 s, rc 0. Output `crosscheck.json` (sha256 `6ace7e0824cf2ae1…`),
  committed in `state/s5p/recompute/recovery-xcheck/`, byte-identical to the cluster file.
- **A first attempt was stopped and is not cited.** The script imported numpy before the module, so the module's
  single-thread BLAS pin did not take effect. That run was slow, it was stopped at the 50 min wrapper limit, and it
  wrote no output. The import order was fixed before the run reported here.

## 2. Checks, all passed (`failures: []`)

- **Identity:** for every null and power set, the recovered products are exactly this lane's lost seeds, finished,
  with no overlap with the retained products. Calibration: MnvTune 35, CV 34, MEC 57, NuWro 49, GiBUU 49. Power: P1
  7, P2 5, P3 5, P1g 1, P2g 7, P3g 28. The retained B equal the terminal B.
- **Determinism, checked independently:** for all 16 reruns, `xsec_flat` is bit-for-bit equal to the original
  product, and `pseudo_seed` and `nuisance_draw` are equal.
- **Reproduction:** every frozen per-variant count (claim and κ = 3 families) reproduces the terminal record. The
  retained-only power counts reproduce the terminal power.

## 3. Result (frozen S, report only)

- **`k_recovered` = 0 in every null, test and variant:** 62 cells, covering the claim variants and the κ = 3 members.
  No recovered draw reaches T_obs. The smallest margin T_obs − max recovered T is **4.6** (GENIE MEC shape, κ = 3
  member m1 = +3: 868.6 against 864.0). Next come 49.8 (CV shape, m1 = +3), 64.7 (MEC shape, m1 = +2, a claim
  variant) and 104.5 (CV shape, m1 = +2).
- **Resolved claims:** k' = k_frozen. B' = 1400 for MnvTune, CV, MEC and GiBUU, and 1800 for NuWro. The resolved claim
  p are smaller than the primary p (the same k with a larger B').
- **Resolved Holm with determinacy** (95% CP, family order): all ten tests are rejected in the primary family, the
  κ = 3 replace family and the keep-both family. The ruled labels are all "robust to the sub-fine residual".
  `primary_decisions_changed` and `ruled_labels_changed` are both empty.
- **Power** over the complete sets (n = 200 each), against the null's retained ensemble, conditional as before. It is
  in `crosscheck.json`.

**Reading.** All 277 lost experiments were recovered, with no residual, and none exceeds the observed statistic under
any frozen variant. So the missing-seed sensitivity is resolved under the frozen-S reading: every rejection holds on
the complete set. The recovery is report-only, and the primary decisions remain those of the frozen products.

## 4. Side-by-side with the campaign's `frozen-s.json`

The campaign's file is on origin/main `11a266c6`, `state/s5p/recovery/phaseC/frozen-s.json`, sha256 `9f4d985e…`. It
was read as data. Script: `recovery-xcheck/s5p_recompute_recovery_sidebyside.py`, output `xc-sidebyside.json`.
**856 of 856 compared quantities agree, 0 differ:**

| quantity | agree |
|---|---:|
| per-variant k_frozen, k_recovered, B, M, M_residual = 0, T_obs, max recovered T | 62 each |
| frozen (k, B) reproduced | 10 |
| complete-set claims k, B and p, three families | 60 |
| resolved decisions decision, k, B, p, threshold and interval, three families | 180 |
| ruled labels | 10 |
| power, retained and complete: n, M, power and intervals | 162 |

The campaign's headline is **confirmed**: k_rec = 0 everywhere, every decision unchanged, B' = 1400 (1800 for NuWro),
and the same closest margins.
