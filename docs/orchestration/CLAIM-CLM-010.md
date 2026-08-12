# CLM-010 claim detail

## Original claim cell

The `niter` 2->3 switch is justified as REGULARIZATION, not merely as gate behaviour: on the B1 fold-forward rate closure the finite-iteration bias falls 3.8008% -> 2.1876% (factor 1.72) while the 48-seed spread is flat (sd 0.8153% -> 0.8444%, ratio 1.036). Bias down at fixed variance is the bias-variance statement; the 6/48 -> 0/48 exceedance at tol=0.05 is its consequence, not an independent argument. The measured means track the closed form `(1-a)^k (R-1)/R` (0.037318 / 0.021698 at k=2/3) to under 0.1 pp.

## Status history

VERIFIED-NUMERIC (**scalar scope only** — the reco-level rate closure, NOT the differential cross section)

## Evidence artifact

`state/p3f-pet-gate4-launch-code-gate-20260806.json` `seed_policy_change.measurement`; the four bound scan products `products/pet/b1_closure/closure_b1_rate_injection_scan{16,32}_measured_N240k{,_niter3}{,_seeds23plus}.json`; closed form derived at `B1-NORMALIZATION-FIX-DESIGN.md:329`

## Data/config hash

R=1.1240802949941018, a=0.4185618199216587, N=240000, epochs=8, seeds 7-54 both arms

## Commit

2b2e5f1 (switch)

## Slurm job(s)

56375160 (k=3 seeds 23-54); **56397442** (k=4 upper-bound arm, submitted 2026-08-06)

## Independent verifier

agy (separate provider account, effort high) reproduced the F-test/interval and endorsed niter=3 on statistics, physics and tolerance governance; the assembly of the two halves into one bias-variance statement is so far **single-source (this session)** and has NOT been independently checked

## Undated residual (i)

(i) **Scalar, not differential** — the publication-grade version needs per-bin closure residual and per-bin spread vs `k`; per-bin arrays come free from job 56381674 (`closure_powered_truth_reweight.py:302-303`). 

## 2026-08-06 — Residual (ii)

(ii) ~~**Argues `k>=3`, not `k=3`**~~ **RESOLVED 2026-08-06 by measurement.** The k=4 arm ran (`56400517` 16 seeds + `56400519` 32 seeds, both COMPLETED 0:0): mean deviation **0.014256**, sd **0.008023**, exceedance **0/48**. Paired on all 48 shared seeds the change is `-0.007620` (se 0.000915, t=-8.33, 95% CI [-0.009413, -0.005827]) and the **sd ratio is 0.9502 — the spread IS flat**. So this item's own condition is met and the record states it plainly: **the stopping point at `k=3` is set by cost and the literature default (`LITERATURE_NOTES.md:65`), NOT chosen by measurement — measurement prefers `k=4` and is deliberately overridden.** The override is justified separately: the D2 powered closure's 0.80 bar is unreachable at **any** k (validated dilution model: ideal recovery 0.6332 at k=3, 0.6629 at k=4, no k<=39 reaching 0.80, with the trained estimator measured 19.1% below that ideal), so `k=4` cannot rescue the FAIL and the switch would cost a queue position plus a full pin cascade. Note the closed form begins **under-predicting** at k=4 (0.014256 measured vs 0.012616), against 0.018 pp agreement at k=3. Full reasoning: `FINDING-20260806-niter4-decision.md`. Recommendation on record: adopt `k=4` opportunistically if any other cause forces a re-train. 

## 2026-08-06 — Supersession history

**SUPERSEDED IN PART 2026-08-06 by job 56381674:** the D2 powered closure at `niter=3` returned verdict=FAIL, recovery 0.5469 vs predeclared 0.80 (residual/gap 0.4531 vs 0.20), with normalization exact and shape recovery globally short (L1 ratio 0.6549). The scalar result below STANDS as stated — it is a rate-closure claim — but it must NOT be read as evidence that k=3 suffices for the differential cross section; the differential test failed. If the cause is too-few iterations for shape, this argues k>3. 

## Undated residual (iv)

(iv) Criterion is reco-space and data-computable, so it escapes the note's own objection to Huang's truth-level chi-square (`sec_method.tex:89-98`) — but that argument is mine, not a cited result. 

## 2026-08-09 / 2026-08-10 — Residual (v)

**(v) THE k=3 OVERRIDE'S STATED JUSTIFICATION EXPIRED ON 2026-08-09 AND NOBODY NOTICED, BECAUSE THE TWO CLAIMS LIVE IN DIFFERENT ROWS.** Raised by the oversight lane 2026-08-10 from this row's own text; verified here against `CLAIMS.md` and recomputed rather than relayed. This row justifies overriding a measurement that prefers `k=4` on the ground that *"the D2 powered closure's 0.80 bar is unreachable at **any** k … so `k=4` cannot rescue the FAIL."* **CLM-012 retired the 0.80 bar on 2026-08-09** (Joseph's decision; the criterion is now `recovery >= f × ceiling`). So the override stands on a premise that no longer exists. **This is not a reason to change `k`** — it is a reason the choice must be re-stated on current grounds, and the answer may well remain 3. What the current criterion actually says, from CLM-012's own k-series `0.4236/0.5642/0.6182/0.6441/0.6592/0.6691` at k=1..6: the bar at k=3 is `0.80 × 0.618228 = 0.4945824` and at k=4 is `0.80 × 0.6441 = 0.5152800`, so **the bar RISES by `0.0206976` going k=3→k=4** and `k=4` only helps if the estimator gains more than that. The measured `0.5126033` (finalizer `56562169`) clears the k=3 bar by `+0.0180209` and would **miss** the k=4 bar by `0.0026767` if the estimator gained nothing. Pointing the other way: CLM-010's own k=4 arm *improves* fold-forward (mean deviation `0.014256` vs `0.021876`, paired `−0.007620` on 48 shared seeds), and fold-forward is exactly the axis where the annealed production nominal now sits at margin `0.0144` against FROZEN's `0.05` where `0.0383` was expected. **Sequencing, and this is a judgement not a decision:** re-stating `k` should follow the code-path bisect, not precede it — with a 188×-production-scatter disagreement between the driver and diagnostic paths unexplained, a `k=4` result could not be attributed to `k` rather than to whatever makes those paths differ. Flagged to Joseph as a fourth item behind the bisect. **Nothing re-run, no pin touched, `niter` remains 3.** 

## 2026-08-11 — Residual (vi)

**(vi) RE-STATED 2026-08-11 ON CURRENT GROUNDS — CITATION REPAIR, NOT A RE-OPENING. THE ANSWER IS STILL k=3 AND THE REASON IS NEW.** Caveat (v) recorded that the override's stated justification cited the `0.80` bar CLM-012 retired on 08-09. Re-derived against the adopted criterion `recovery >= f × ceiling(k)` with CLM-012's own k-series, and against **three independent measured draws** of the annealed D2 closure (`56552326`, `56611837`, `56626305`; predeclared at `dcaddfd`): **THE DECIDING STATEMENT USES NO CENTRAL ESTIMATE, NO SPREAD AND NO DENOMINATOR —** `bar(k=3) = 0.80 × 0.618228 = 0.4945824`, `bar(k=4) = 0.80 × 0.6441 = 0.5152800`. `0.5126033` **PASS** (+0.0180209) / **FAIL at k=4** (−0.0026767); `0.5113773` **PASS** (+0.0167949) / **FAIL** (−0.0039027); `0.5129340` **PASS** (+0.0183516) / **FAIL** (−0.0023460). **All 3/3 clear the k=3 bar; all 0/3 clear the k=4 bar.** The worst draw clears k=3 by `+0.0167949`, which is `20.5` sd above it; the *best* draw misses k=4 by `−0.0023460`. **So moving to k=4 converts a pass into a fail at current estimator performance** — the bar rises `0.0206976` from k=3 to k=4 (CLM-012 (vii): the ceiling rises with k, and only upward) and the estimator would have to gain more than that, where measurement shows it gaining nothing. **The honest trade, stated rather than buried:** CLM-010's own k=4 arm is *better* on normalization — fold-forward mean deviation `0.014256` vs `0.021876`, a paired change of `−0.007620` on all 48 shared seeds — so `k=4` is not without merit; it is outvoted because shape is the physics and the D2 criterion is where shape is scored. The pin-cascade cost from the original reasoning also survives unchanged. **Provenance discipline:** `0.5126032761517403` remains the **cited artifact value** — the gate, the receipts and finalizer `56562169` (31/31) all cite it, and replacing a validated value with a better estimate would break a provenance chain to buy precision no decision needs. The three-run mean `0.5123048` with `sd 0.000820128` is recorded **alongside as the stability measurement**, not as a substitute. **Nothing is re-run, no pin is touched, no threshold moves, `niter` remains 3** — and because the deciding statement is a count of draws clearing a bar, this justification does not move if a fourth draw lands: it would have to fall *below* the bar, not merely shift a mean. Framing (citation repair, not re-opening) is Joseph's; the estimate-free form and the k=4-bar-exceeds-all-draws statement were sharpened by the oversight session.
