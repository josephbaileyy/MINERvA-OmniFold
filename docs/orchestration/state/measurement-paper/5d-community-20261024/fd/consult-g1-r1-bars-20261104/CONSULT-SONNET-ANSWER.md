**Recommendation: (c), a Monte Carlo null at the realized composition, with its rule and seed declared now.** I'd keep (b) as the pre-declared fallback. I did not run the (c) procedure on the real covariances, only generic ones.

**1. The objection is right.**
- k = 16·49/34 = 23.06.
- Under the stat-only null, P(T>35.89) = 0.1364 and P(T>26.30) = 0.3603.
- The Hartlap T is 15.06·F, giving 0.0164 and 0.0846. Its F quantiles are 29.39 and 46.09. All of these match your numbers.
- The cause is that 50 replicas in 16 dimensions gives an inverse with 34 effective dof. The Hartlap factor fixes the mean of T (it becomes about 16) but not the heavy F tail.
- I also simulated random 16×16 compositions (4000 draws each) with Δ ~ N(0, C_stat + C_univ) and C_univ estimated from 50 universes.
  - Raw T gives false "differ" at 0.128, 0.040, 0.032 and 0.048 for U/S scale 0, 0.3, 1 and 3. False "marginal or differ" is 0.356, 0.191, 0.166 and 0.205.
  - Even with U at 3× stat, the nominal bars stay inflated. The finite-universe C_univ is itself a noisy covariance estimate and adds its own Hotelling-type inflation.
  - Hartlap against the F quantiles gives (0.003, 0.051), (0.000, 0.023), (0.000, 0.029) and (0.002, 0.062).

**2. Comparison.**
- **(a) Keep the χ² bars.** This errs toward false "differ" and "marginal". It makes "agree" harder to earn, so it is unflattering to the paper. The cost is a false claim of algorithm dependence, which would need retracting.
- **(b) Hartlap T against the F quantiles.**
  - It is exact in the stat-only limit.
  - With large C_univ it is conservative, toward "agree". The false-"differ" rate drops to about 0, and "marginal or differ" falls to about 0.02–0.03.
  - It is not monotone in composition: at U = 3× stat it went slightly over nominal (0.062), because it ignores the noise in C_univ.
  - So (b) can err in either direction, though mostly toward "agree".
- **(c) Monte Carlo null.** It is calibrated by construction for whatever composition is realized, including the noise in C_univ, so it should have no systematic direction.
- **Hidden flattering direction in all options.** The null Δ ~ N(0, S+U) treats the universe differences as random scatter in Δ. In reality the two estimators respond to systematics almost identically, so Δ's systematic part is probably much smaller. When I drew Δ ~ N(0, S) only, with the same denominator, false "differ" fell to about 0 for (a) at moderate or large U and for (b) at every U. This makes all of (a)–(c) conservative toward "agree" in the realistic regime. Say so in the declaration.

**C_norm does not matter for the null.** C_norm is rank one along Δ. By Sherman–Morrison, T = T₀/(1 + 1.96×10⁻⁴·T₀), where T₀ uses C_stat + C_univ. That is a monotone transform that shrinks T by about 0.4% at T₀ = 36. It cannot change the null, and you can simulate it with each draw's own Δ* anyway.

**Can (c) be specified before any data? Yes.** The recipe has three parts.
- **Procedure.**
  - Draw Δ* ~ N(0, Ĉ_stat + Ĉ_univ).
  - Draw Ĉ_stat* as Wishart(49, Ĉ_stat)/49.
  - Draw Ĉ_univ* per band with its declared universe count, using the same mean-centred 1/N estimator.
  - Form T* with the exact production formula, including C_norm*.
  - Take the empirical 0.95 and 0.997 quantiles as the bars.
- **Fixed settings.** Use a fixed seed and at least 10⁶ draws (0.997 needs roughly 3000 tail events), and use the uncorrected T.
- **Order of operations.** Compute and commit the bars from the covariances before Δ is formed. The rule is then a function of data that excludes Δ, so there is no outcome-dependent choice.

**3. Main risks.**
- The plug-in uses estimated covariances as truth. This is exact in the stat-limit because T is pivotal there. With a large U it is second-order but not zero.
- The bars depend on the declared null for Δ (S+U versus S only). The null must be declared, because the choice moves the bars.
- If the real Δ has a smaller systematic component than assumed, the verdict leans toward "agree". Report the S-only bars as a labelled sensitivity.
