You are an independent statistics consultant. Give a recommendation; do not edit any files. You may run python/scipy to check numbers. Work only from the facts below. Do not read or write anything under /Users/josephbailey/local-research/MINERvA-OmniFold.

CONTEXT. A pre-declared cross-check compares two unfolding estimators, binned IBU and OmniFold configuration (e), at 16 reporting cells. Δ = f_IBU − f_(e). Its covariance is C_Δ = C_stat + C_univ + C_norm:
- C_stat: the sample covariance (ddof 1) of 50 paired bootstrap-replica differences Δ_b, in 16 dimensions;
- C_univ: from paired systematic-universe differences, by mean-centred 1/N estimators per band (a finite universe count per band);
- C_norm = (0.014 Δ)(0.014 Δ)^T.

Reading R1: T = Δ^T C_Δ^{-1} Δ, ndf 16.
- The declared bars are χ²₁₆ quantiles: T ≤ 26.30 "agree"; 26.30–35.89 "marginal"; T > 35.89 "differ".
- The reading uses the UNCORRECTED T. A Hartlap-corrected T, with C_stat ÷ 32/49, is reported only as a sensitivity.

What each outcome licenses:
- "agree": "a binned unfolding … agrees with the reported result within their paired uncertainty";
- "marginal": T and the pulls, with no direction;
- "differ": "the reported cells depend on the unfolding algorithm at the level of T".

No data have been read; the declaration is not yet bound.

THE AUDITOR'S OBJECTION. In the stat-dominated limit, T's null is Hotelling's: 16·49/34 · F(16,34) = 23.06 F(16,34), not χ²₁₆.
- Under the null, "differ" fires with probability 0.136, against the nominal 0.003, and "marginal or differ" with 0.36, against 0.05.
- With the Hartlap-corrected T: 0.016 and 0.085.
- The exact F-based quantiles of the Hartlap T in the stat-only limit are 29.39 (0.95) and 46.09 (0.997).
- The real rates lie between these and the nominal ones, depending on how large the universe and norm blocks are against stat.

The auditor's proposed fixes:
- (i) bars calibrated to T's own null at the realized block composition, declared now;
- (ii) minimally, the Hartlap T against the F-based quantiles.

The director has independently reproduced these numbers with scipy.

QUESTIONS.
1. Is the objection right? Check the numbers.
2. Compare the options. Say which errs toward a false "agree" (the flattering direction for the paper) and which toward a false "differ". Options:
   - (a) keep the χ² bars;
   - (b) Hartlap T against the F quantiles;
   - (c) a Monte Carlo null calibration at the realized composition, fixed now;
   - anything better you see.
   In particular: when C_univ and C_norm are large, is (b) conservative, toward "agree"? Can (c) be specified now, before any data, without a data-dependent choice? Note that it would use the realized covariances but not Δ.
   C_norm depends on Δ itself. Does that matter for the null?
3. Give one recommended option, with a two-sentence reason, plus its main risk.

Keep the answer under 500 words.
