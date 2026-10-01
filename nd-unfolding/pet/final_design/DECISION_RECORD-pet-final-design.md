# Decision record — PET final-design selection study (living; completed at delivery)

**Status: OPEN (look 1 decided 2026-09-30; coverage of H2S1T24 K5 pending).** This record lists every decision taken, its rule, its
evidence and its date; the terminal selection is filled in only from `analysis/decide.py` output on unblinded
final-bank scores (and `analysis/coverage.py` for §6.4). PET is diagnostic: nothing here is an adoption.

## Governing documents

| item | where |
|---|---|
| authorization (verbatim) | `docs/orchestration/AUTHORIZATION-20260925-pet-final-design.md` |
| scope (byte copy of the handoff) | `SCOPE-HANDOFF-20260925.md`, `GOAL-20260925-pet-final-design.txt` |
| protocol and frozen decision table | `PROTOCOL-20260925.md` §6 (+ Amendments 1, 2, 2b, 2c, 3a–3f, 4, 5) |
| finalist rule | `dev/FINALIST_RULE-20260926.md` (+ Addendum, correction, Addendum 2), `dev/apply_finalist_rule.py` |
| reviews | `REVIEW_DISPOSITION-{IMPL,STAT,SCOPE}-20260926.md` |

## Decisions so far (chronological)

| date (UTC) | decision | rule / basis | evidence |
|---|---|---|---|
| 2026-09-25 | banks DEV / FB / RB frozen; inference conditional on the banks | protocol §3 | `CAPACITY-20260925.md`, `banks/BANK_MANIFEST.json` |
| 2026-09-26 | E5 quartiles from DEV only | Amendment 1 | `analysis/provenance/` |
| 2026-09-26 | AUSSIE closed (12/12 matched losses) | protocol §5, bounded matched test | `scalar/SCALAR_AUSSIE_MATCHED-20260925.md` |
| 2026-09-26 | compact finalist H2S1 K = 5, anchors CTL K3 / C K3; FB rows released blinded | finalist rule, Amendment 2/2b | `dev/SCREENS-20260926.json` |
| 2026-09-26 | statistical corrections (interval √(1+1/B), calibrated C4, §6.6 order from the goal, look-2 carry, sizing) | Amendment 2c | `REVIEW_DISPOSITION-STAT-20260926.md` |
| 2026-09-26 | terminal practical default, cost at declared packing, N1 on E9 truth weights, E4/E5 sizing group, coverage order, futility, bank-effect bound, cost-part repair | Amendment 3a | `REVIEW_DISPOSITION-SCOPE-20260926.md` |
| 2026-09-26 | S-N1 at K\* (screen cases), completeness, between-design step in code; dev2Q ids and rows | rule Addendum + correction | `dev/apply_finalist_rule.py`, tests |
| 2026-09-26 | PET2-pretrained (P2preS1) fails S-N1 at K\* = 4 (step-1 weights 334–1,217) | rule Addendum item 2 | `results/` post-hoc, `DEVELOPMENT-20260926.md` |
| 2026-09-26 | sizing (provisional): n_F = 30; library E4/E5 draws 60; E4 NI a quantified limit (1,770 draws) | §8, 2c.6, 3a.4 | `sizing/SIZING-20260926.md` |
| 2026-09-26 | N2 failure of H2S1 K5 (0.095) and L128S1 K5 (0.091), located in the truth step; repair arm; S-N2 screen; re-freeze rule | Amendment 3b, rule Addendum 2 | `sizing/n2.json`, `DEVELOPMENT-20260926.md` |
| 2026-09-27 | S-N2 decided so far (repair arm, S3P seed runs, `sizing/n2_arm_partial.json`): L64S1 K\*=4 **0.057 FAIL**; L128S1E16 K\*=4 **0.071 FAIL** (0.071 at k=5); CS1 K\*=6 **0.054 FAIL** (0.100 at k=5); **H2S1T24 K\*=5 0.037 PASS** (0.042 at k=4; 0.092 at k=3); earlier H2S1 K5 0.095, L128S1 K5 0.091 FAIL | finalist-rule Addendum 2, Amendment 3b | `scored/s3n` (cluster), `dev/n2_table.py` |
| 2026-09-27 | PET2 learning-rate-policy arm closed: P2preA1 (annealed step 1) stable, development tilt 0.928 at k = 5, but proton topology ≤ 0.225 < 0.25 at every k; P2scrA1 ≤ 0.06; no PET2 design passes the four screens | finalist rule | `results/` post-hoc (dev2Q) |
| 2026-09-27 | S-N2 for the last designs: H2S1E16 0.074 FAIL; **L128S1T24 K\*=4 0.043 PASS** | rule Addendum 2 | `sizing/n2_all-20260927.json` |
| 2026-09-27 | ensemble fallback (X4) started early with unchanged entry condition, then stopped (not needed) | Amendment 3b-bis | `PROTOCOL` |
| 2026-09-27 | **compact finalist H2S1T24 K5** (supersedes H2S1 K5) | Amendment 3c | `dev/SCREENS-20260927.json` |
| 2026-09-27 | **large finalist L128S1T24 K4**; decision set {H2S1T24K5, L128S1T24K4}, m = 2; anchors CTL K3 / C K3; FB release FINAL 0–23 + library 21×8 (blinded); measured cost 1.77 / 1.49 A100-h per unfolding (compact not cheaper) | Amendment 3d | `runs/s4f_a3.tsv`, `runs/s4s_a3.tsv`, `resources/cost_t24-20260927.json` |
| 2026-09-27 | **n_F = 60** (capped; E0 NI needs ≈ 250 draws: quantified limit); FINAL 24–59 released | Amendment 3e | `sizing/sizing_final-20260927.json`, `runs/s4f_a3e.tsv` |
| 2026-09-27 | **N_LIB = 40** (E4-bound); D4c/D3 draws 0–39 used | Amendment 3f | `sizing/sizing_library-20260927.json`, `runs/s4s_a3e_n40.tsv` |
| 2026-09-30 23:02Z | **UNBLIND look 1**: all 944 look-1 rows COMPLETE with receipt digests (exit 0); 622 runs were resumed bit-exactly across Slurm jobs (listed) | Amendment 4, 2c.9, 2c.10 | `freeze/COMPLETENESS-look1.tsv`, `results/final/look1_segments.tsv` |
| 2026-09-30 | FB cost at the declared packing: H2S1T24 K5 median **1.768**, L128S1T24 K4 median **1.517** A100-h per unfolding (n = 352 each, none excluded); §6.5 cost path closed (compact not cheaper) | §6.7, 3a.2 | `resources/cost_fb_look1-20260930.json` |
| 2026-09-30 | **Look-1 decision.** L128S1T24 K4 **INELIGIBLE: B2 FAIL — point-decided, statistically unresolved** (D4d n down, mean E_avail residual − injected L1 **0.0122**, 95 % t interval 0.0064–0.0181, n = 8, vs ≤ 0.010; every other §6.1–6.3 rule PASS). H2S1T24 K5 passes every §6.1–6.3 rule (R_E0 0.895, LB 0.876; B2 **0.0097**, 0.0025–0.0169, **also statistically unresolved**; N1 max weight 90.2 ≤ 100); C1–C5 not yet assessed. Outcome **CONTINUE (coverage of H2S1T24 K5 pending)**; no rule returned a look-2 CONTINUE, so there is no look 2. B2 is not a sequential rule and look-1 verdicts are never re-decided (2c.4): the B2 difference between the two finalists is not resolved by this comparison (each interval crosses 0.010; paired, H2S1T24 lower on 7 of 8 draws), so the frozen point rule alone separates them. **Citable for:** L128S1T24 K4 is ineligible under the frozen rules. **Not citable for:** H2S1T24 being more robust than, or equivalent to, L128S1T24; overlapping intervals and a non-significant difference establish neither | §6.2 B2, 2c.4, 2c.5, §10 | `results/final/decision_look1.json`, `results/final/evidence_look1.json`, `results/final/scored_fb/` (B2 reproduced from the raw histograms) |
| 2026-09-30 | Provisional ranking **PROVISIONAL_SELECTED H2S1T24 K5** → its coverage runs first; L128S1T24's coverage cannot change the outcome (ineligible on B2) and is not run | 3a.5 | `results/final/decision_look1_provisional.json` |
| 2026-09-30 23:45Z | **Coverage release** for H2S1T24 K5 at its exact configuration: 720 development-tilt members (N_cov 120 × B 6; C1–C4) then 360 D4c-up members (60 × 6; C5), blinded until each group is complete; watcher lanes moved to coverage (stop 2026-10-10T22:00Z) | Amendment 5, §9, 3a.5 | `runs/s5c_a5_H2S1T24.tsv`, `runs/s5d_a5_H2S1T24.tsv` |
| 2026-10-01 | **B1 interpretation (report only; verdicts unchanged).** B1 PASSes for both finalists under its frozen independence-based bound (H2S1T24 2/224 units, CP upper 0.032; L128S1T24 1/224, 0.025). Under within-draw dependence the evidence is **insufficient** to establish a per-unit failure probability ≤ 0.10. The dependence-robust companion bounds a different estimand, the draw-level any-failure probability on the common panel (FB0–7, every declared case): H2S1T24 2/8 draws (CP upper 0.651), L128S1T24 1/8 (0.527); with 0/8 the bound would be 0.369, so this panel cannot establish the claim at any outcome; FB8–39 (D4c up and D3 +0.35 only) 0/32. This does **not** show that the per-unit or any per-case failure probability exceeds 0.10. `decide.py`'s replicate-cluster companion (2/40, 1/40) pools the two panels and is not a bound on full-library draw failure. **Citable for:** B1 PASS under the frozen independence-based bound. **Not citable for:** a dependence-aware per-unit failure probability ≤ 0.10, or for that probability exceeding 0.10 | §6.2 B1, 2c.5 | `results/final/b1_dependence_look1.json` (`analysis/b1_dependence.py`) |

## Pending decisions (filled at the time they are taken)

3. ~~UNBLIND amendment~~ (Amendment 4, 2026-09-30). 4. ~~Look-1 decisions~~ (2026-09-30, above; no look 2).
5. Coverage (§9, §6.4) for the provisionally preferred finalist first (3a.5); the other if required.
6. Terminal selection: SELECTED / UNRESOLVED_WITH_DEFAULT / NO_ELIGIBLE_DESIGN, with the executable configuration
   (config JSON, content hash, K, miss rule, uncertainty procedure B = 6), measured cost and limits.
