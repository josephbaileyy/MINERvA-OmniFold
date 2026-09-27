# Decision record — PET final-design selection study (living; completed at delivery)

**Status: OPEN.** No final-bank quantity has been scored. This record lists every decision taken, its rule, its
evidence and its date; the terminal selection is filled in only from `analysis/decide.py` output on unblinded
final-bank scores (and `analysis/coverage.py` for §6.4). PET is diagnostic: nothing here is an adoption.

## Governing documents

| item | where |
|---|---|
| authorization (verbatim) | `docs/orchestration/AUTHORIZATION-20260925-pet-final-design.md` |
| scope (byte copy of the handoff) | `SCOPE-HANDOFF-20260925.md`, `GOAL-20260925-pet-final-design.txt` |
| protocol and frozen decision table | `PROTOCOL-20260925.md` §6 (+ Amendments 1, 2, 2b, 2c, 3a, 3b) |
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

## Pending decisions (filled at the time they are taken)

3. UNBLIND amendment (completeness manifest).
4. FINAL / library decisions per §6.1–6.3, §6.5, §6.6 (look 1; look 2 if CONTINUE), with bank-effect bounds.
5. Coverage (§9, §6.4) for the provisionally preferred finalist first (3a.5); the other if required.
6. Terminal selection: SELECTED / UNRESOLVED_WITH_DEFAULT / NO_ELIGIBLE_DESIGN, with the executable configuration
   (config JSON, content hash, K, miss rule, uncertainty procedure B = 6), measured cost and limits.
