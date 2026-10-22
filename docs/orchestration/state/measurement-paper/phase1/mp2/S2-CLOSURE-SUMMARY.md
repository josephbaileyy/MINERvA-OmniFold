# MP-2 S2: closure summary, per generator and per gate (2026-10-22)

**By** the measurement session, for the director to take to Joseph. Every S2 fit the contract allows has run.
**CITABLE FOR:** the S2 outcome for each generator and feature set, gate by gate, as released through verdict-v2.
**NOT CITABLE FOR:** why any gate failed. The power diagnostic and the cap and support facts below are descriptive.
They decide nothing. This record proposes no new fit, no change to a gate and no change to the contract.

**Sources.** Every number below is read from committed receipts in `s2-receipts/`, not transcribed:
- `closure_table.json` (sha256 `70bb024e…`), produced by `measurement-paper/phase1/mp2/mp2_s2_closure_table.py`
  (`20974fd7…`). It reads the eight `gates_*.json` and `verdict_v2v3_*.json` files and the 400 model metadata
  records, and records each file's sha256.
- `power_diag_primary.json`, `power_diag_fallback.json`, `power_diag_gibuu_primary.json` and
  `power_diag_gibuu_fallback.json`, from `mp2_s2_power_diag.py` (`1b573aa2…`).
- The jobs, their code and their costs are in `S2-IMPLEMENTATION.md` and `../LEDGER.tsv`.

## Outcome

**No generator is established.** GENIE CV, GENIE MEC, NuWro and GiBUU each failed S2 with F_primary, then failed it
again with their one F_fallback. The contract's order is (JSON `order`): "on failure, F_fallback (once, before S3);
failure again -> 'not established' for that G, A7's hybrid result stands". S3 unfolds with a G whose S2 passed
(contract §8), so S3 is not reachable. MP-2's next step is Joseph's decision.

- **F_primary** has 18 features: the 5 scalars, E_ν, five species energy sums, n_p, n_π±, and the leading
  particles.
- **F_fallback** has 11 features: the 5 scalars, E_ν, and the five species energy sums.
- **What every row shares:**
  - V2-fine, V2-J and V3 fail on all five replicas of all eight rows.
  - In V3, all four held-out distributions fail on every replica.
  - No V3 distribution was fail-closed; ndf ≥ 1 everywhere.
  - Blind ndf_fine is ≥ 3670 for every G (bar ≥ 200).
- **V1 and V4 pass for GENIE, and fail for NuWro and GiBUU.**

## Per G and per gate

Each gate must pass on all five replicas. Ranges are min–max over the replicas; "pass k/5" counts the replicas that
pass. V1 is one held-out fit (replica 0, R10) against its own G-vs-G control. The bars are those of addendum 14,
fixed by Joseph before any V2 or V3 statistic was read (`DECISION-20261022-joseph-mp2-gate-rules.md`).

| G | feature set | V1: AUC ≤ G-vs-G control + 0.005 | V4: ESS/N ≥ 0.3; max w/mean ≤ 50 | V2-fine: χ²/ndf ≤ 1.5 (ndf) | V2-J: max\|pull\| ≤ 3.497 | V3: min p_d > 0.0125 (largest p_d of any distribution) | S2 |
|---|---|---|---|---|---|---|---|
| GENIE CV | primary | 0.4972 (bar 0.5094): pass | 0.934; 3.06–3.68: pass 5/5 | 2.34–2.39 (3670): pass 0/5 | 6.29–6.80: pass 0/5 | 2.4e-08; 4 of 4 distributions fail: pass 0/5 | **fail** |
| GENIE CV | fallback | 0.4989 (bar 0.5094): pass | 0.933; 2.97–5.35: pass 5/5 | 2.23–2.37 (3670): pass 0/5 | 6.34–6.86: pass 0/5 | 1.1e-09; 4 of 4 distributions fail: pass 0/5 | **fail** |
| GENIE MEC | primary | 0.4935 (bar 0.5063): pass | 0.932–0.935; 2.55–3.57: pass 5/5 | 2.59–2.78 (3729): pass 0/5 | 5.81–5.93: pass 0/5 | 2.0e-06; 4 of 4 distributions fail: pass 0/5 | **fail** |
| GENIE MEC | fallback | 0.4967 (bar 0.5066): pass | 0.931–0.934; 2.83–4.65: pass 5/5 | 2.60–2.76 (3729): pass 0/5 | 5.58–5.75: pass 0/5 | 2.5e-07; 4 of 4 distributions fail: pass 0/5 | **fail** |
| NuWro | primary | 0.5533 (bar 0.5074): fail | 0.025–0.056; 12,274–25,923: pass 0/5 | 7.04–7.27 (4354): pass 0/5 | 33.38–34.22: pass 0/5 | 3.1e-197; 4 of 4 distributions fail: pass 0/5 | **fail** |
| NuWro | fallback | 0.5462 (bar 0.5078): fail | 0.065–0.104; 6,756–9,972: pass 0/5 | 5.96–6.26 (4354): pass 0/5 | 28.90–38.12: pass 0/5 | 6.2e-256; 4 of 4 distributions fail: pass 0/5 | **fail** |
| GiBUU | primary | 0.5663 (bar 0.5102): fail | 0.029–0.045; 7,718–17,804: pass 0/5 | 8.05–8.15 (4404): pass 0/5 | 33.81–34.41: pass 0/5 | 2.1e-126; 4 of 4 distributions fail: pass 0/5 | **fail** |
| GiBUU | fallback | 0.5524 (bar 0.5037): fail | 0.035–0.051; 12,936–20,220: pass 0/5 | 6.13–6.28 (4404): pass 0/5 | 31.77–32.51: pass 0/5 | 1.0e-134; 4 of 4 distributions fail: pass 0/5 | **fail** |

**V3 χ²/ndf per held-out distribution** (descriptive; the gate is p_d, above):

| G | feature set | neutron multiplicity, KE > 10 MeV | proton multiplicity, KE > 20 MeV | π⁰ count | neutron KE |
|---|---|---:|---:|---:|---:|
| GENIE CV | primary | 9.7–10.0 | 38.3–41.0 | 8.0–8.8 | 32.8–33.7 |
| GENIE CV | fallback | 12.6–12.9 | 51.5–55.6 | 9.1–10.0 | 34.4–34.8 |
| GENIE MEC | primary | 5.6–6.1 | 21.4–25.5 | 6.4–8.4 | 19.8–21.8 |
| GENIE MEC | fallback | 8.5–8.7 | 26.6–31.0 | 7.1–9.4 | 21.8–24.0 |
| NuWro | primary | 1,361–1,440 | 1,795–1,834 | 155–159 | 1,978–2,153 |
| NuWro | fallback | 2,711–2,776 | 6,835–7,248 | 200–207 | 1,687–1,760 |
| GiBUU | primary | 483–489 | 189–198 | 100–103 | 100–161 |
| GiBUU | fallback | 568–574 | 358–365 | 107–111 | 116–158 |

## Beside it, descriptive: the power diagnostic, the tree cap and the E_ν support

This section is DESCRIPTIVE. It tests a hypothesis and changes no verdict. The diagnostic, approved by the director
at 0 node-h, tests the session's hypothesis that the GENIE classifiers stop early because the attainable gain is
below its own noise. It reads only what the S2 jobs wrote. Its definitions:
- **achieved gain:** ln 2 minus the best class-balanced validation log-loss, per model;
- **binned 5D JSD:** the Jensen–Shannon divergence between Tune C+H (in G's support) and G over the fine 5D cells,
  before and after reweighting Tune by each replica's w_G, with its statistical bias subtracted by half-sample
  splits (an approximation);
- **noise scale:** sqrt(2 JSD / n_eff), an order of magnitude, not a test.

| G | feature set | best iteration min / median / max | at ≥ 2800 of 3000 | achieved gain, median (nats) | binned 5D JSD before (debiased) | after reweighting, replicas 0–4 | noise scale | achieved / noise | after / noise |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| GENIE CV | primary | 29 / 41 / 64 | 0 of 50 | 0.0082 | 0.00418 | 0.00132–0.00135 | 0.00035 | 23 | 3.7–3.8 |
| GENIE CV | fallback | 28 / 37 / 67 | 0 of 50 | 0.0071 | 0.00418 | 0.00126–0.00128 | 0.00035 | 20 | 3.6–3.6 |
| GENIE MEC | primary | 14 / 28 / 43 | 0 of 50 | 0.0032 | 0.00330 | 0.00153–0.00158 | 0.00031 | 10 | 4.9–5.1 |
| GENIE MEC | fallback | 14 / 27 / 53 | 0 of 50 | 0.0029 | 0.00330 | 0.00148–0.00155 | 0.00031 | 9 | 4.8–5.0 |
| NuWro | primary | 1548 / 2747 / 2998 | 24 of 50 | 0.1137 | 0.00917 | 0.00719–0.00758 | 0.00044 | 257 | 16.3–17.2 |
| NuWro | fallback | 999 / 1903 / 3000 | 5 of 50 | 0.0885 | 0.00917 | 0.00570–0.00621 | 0.00044 | 201 | 12.9–14.1 |
| GiBUU | primary | 2617 / 2993 / 3000 | 49 of 50 | 0.1512 | 0.01097 | 0.01278–0.01295 | 0.00048 | 316 | 26.7–27.1 |
| GiBUU | fallback | 1597 / 2892 / 3000 | 30 of 50 | 0.1153 | 0.01097 | 0.01081–0.01123 | 0.00048 | 241 | 22.6–23.5 |

**Read narrowly:**
- **The hypothesis as stated is not supported.** The GENIE models' achieved gain is 9–23× the noise scale.
- **GENIE's residual stays above noise.** With either feature set, the reweighting removes 68–70% of GENIE CV's
  binned 5D JSD and 52–55% of GENIE MEC's. What remains is 3.6–5.1× the noise scale.
- **NuWro's** binned JSD falls by about 20% (primary) and 35% (fallback).
- **GiBUU's binned 5D JSD does not fall.**
  - It rises from 0.01097 to 0.0128–0.0130 with F_primary.
  - It is unchanged within 0.0003 with F_fallback.
  - Beside it, V4: ESS/N is 0.029–0.051 and max w/mean is 7,718–20,220.

**The 3000-tree cap** (the frozen n_estimators, which Joseph kept: `DECISION-20261022-joseph-mp2-gate-rules.md`):
- **GiBUU:** 49 of 50 F_primary models stop at ≥ 2800 trees, and 30 of 50 F_fallback models do. The cap binds for
  GiBUU.
- **NuWro:** 24 of 50 F_primary models and 5 of 50 F_fallback models reach ≥ 2800.
- **GENIE:** no model goes past 67 trees, and the V1 fits stop at 1–4 trees. The cap does not bind for GENIE.

**E_ν support (R9, descriptive):**
- **GiBUU** is generated for 0–20 GeV. 1,747,492 Tune rows lie outside it, 7.16% of Tune's w_truth. These rows keep
  r_h and are not reweighted. Their share is reported per J cell in the gates files.
- **GENIE and NuWro:** 18 rows, 6.9e-7 of w_truth.

## What this record does not decide

It does not decide whether S2's failure comes from:
- classifier power, or the tree cap for GiBUU;
- the feature sets;
- the support;
- a genuine disagreement between the generators and Tune C+H in the held-out final-state distributions.

It does not propose a further fit, a gate change or a contract change. Under the contract's order, each G's
F_fallback was its last.

## Compute

Phase 1 has used 11.033 of 35 CPU node-h (`../LEDGER.tsv`, ElapsedRaw × billing / 256 / 3600). Of that:
- tranche A: 1.990 of 3.5;
- tranche B: 1.159 of 2.3.

No S2 job used premium QOS. All 20 S2 jobs are in the ledger, on debug or regular (`regular_1`).
