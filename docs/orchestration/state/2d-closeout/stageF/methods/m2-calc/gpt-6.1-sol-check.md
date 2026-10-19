**Verdict: CORRECT WITH CAVEATS.** The event inclusion and the Holm reduction are sound, and uniform calibration is worst case for the **any-stopping crossing bound**. The claimed **0.89α** is plausible, but the supplied script does not compute or certify it. The tighter **0.81α “as coded”** bound is not established by this script, and **0.844α** applies to the specified fixed grid, not automatically to the irregular production looks.

**1. The rejection-event inclusion is correct, with a precise interpretation of the stream.**

Write
\[
U_B=U_{.95}(K_B,B),
\qquad
E_c=\bigcup_{B=1}^{1999}\{U_B<c\}.
\]
Here \(U_{.95}\) is the upper endpoint of a two-sided 95% CP interval, equivalently a one-sided 97.5% upper confidence bound.

If a test is rejected at a Holm step with threshold \(c\), the code explicitly requires \(U_B<c\) at its terminal sample size. Consequently its rejection belongs to \(E_c\). This inclusion is pathwise; it does not require a stopping-time theorem.

None of the following defeats that inclusion:

- Ordering by \((k+1)/(B+1)\), including any tie-breaking.
- The “undetermined” branch: it prevents subsequent rejections.
- The “not rejected” branch: it also prevents subsequent rejections.
- Shared stopping between total and shape tests.
- Budget decisions made after seeing results.
- Continuing after an eligible stopping point.

The essential requirement is that every possible terminal calculation uses a prefix of an underlying eligible Bernoulli stream of length at most 1999.

For missing products, “nested available sets” is useful, but the statistical assumption must be sufficiently strong: conditional on the observed data and the relevant availability mechanism, the retained draws must admit an ordering in which their exceedance indicators remain iid Bernoulli(\(p\)). Outcome-independent retention can provide this. Merely identifying timeouts as the operational cause does not prove outcome independence.

For the max over variants, the baseline argument works if, at every relevant look:

1. the unshifted variant is included;
2. all variants use the same \(B\); and
3. \(K_{\rm claim}\ge K_0\).

Then
\[
U(K_{\rm claim},B)<c
\ \Longrightarrow\
U(K_0,B)<c.
\]
The shifted variants may be ensemble-dependent without invalidating this domination. If denominators or retained ensembles differ across variants, max-p selection alone does not establish this inequality.

**2. The Holm reduction is valid without independence and without ordering by \(U\).**

Suppose any true null is rejected. Consider the **first true null in the procedure’s ordering**. It must have been rejected, since the procedure cannot pass an earlier nonrejection or undetermined decision.

All hypotheses preceding it are false nulls, so its position \(i\), indexed from zero, satisfies
\[
i\le m-m_0.
\]
Its threshold therefore satisfies
\[
\frac{\alpha}{m-i}\le \frac{\alpha}{m_0}.
\]
Hence
\[
\{\text{at least one false rejection}\}
\subseteq
\bigcup_{j\in I_0}E_{j,\alpha/m_0},
\]
and
\[
\operatorname{FWER}
\le \sum_{j\in I_0}P(E_{j,\alpha/m_0})
\le m_0R(\alpha/m_0).
\]

This proof allows arbitrary dependence between tests, streams, orderings, and stopping decisions. Ordering by p-hat is harmless here because rejections form an initial segment and each rejection passes its own CP gate.

The derivation should use the crossing events \(E_{j,c}\) in this display, rather than leaving \(P(U_i<c)\) ambiguous about the random terminal sample size.

**3. Uniform \(p\) is worst case for the crossing event.**

Define
\[
g_c(p)=P_p(E_c)
\]
under an iid Bernoulli(\(p\)) stream.

Using common independent uniforms \(V_b\), construct
\[
X_b(p)=\mathbf1\{V_b\le p\}.
\]
Increasing \(p\) increases every cumulative count. Since \(U(k,B)\) increases with \(k\), \(E_c\) is a decreasing event under this coupling. Thus \(g_c(p)\) is nonincreasing.

If the null distribution \(F\) of \(p\) is super-uniform,
\[
F(t)\le t,
\]
then
\[
P(E_c)=\int g_c(p)\,dF(p)
\le \int_0^1g_c(p)\,dp
=:R(c).
\]

Thus the integral in the derivation is the appropriate **worst-case bound**, with equality under uniform calibration. It is not generally the actual probability under a conservative calibration.

There is an important distinction: this monotonicity argument concerns **the crossing event \(E_c\)**. It does not automatically establish monotonicity of rejection under the particular frozen stopping rule, whose stopping sets also involve precision requirements and other thresholds. A uniform-\(p\) computation for that narrower event needs its own justification before being extended to every super-uniform distribution.

**4. The numbers are plausible, but their claimed scope exceeds the supplied computation.**

The scale of 0.89 is reasonable.

At fixed \(B=1999\), rejection at \(c=0.05\) requires roughly 80 or fewer exceedances. Under uniform mixing, \(K_B\) is uniform on \(\{0,\ldots,B\}\), so
\[
P(U(K_B,B)<c)=\frac{k_*(c,B)+1}{B+1},
\]
which is around \(0.04\), or around \(0.8c\).

Allowing crossing at earlier sample sizes increases that probability. A value near \(0.0445=0.89c\) is therefore entirely plausible. Repeated inspection does not, by itself, imply that this integrated probability must exceed \(c\).

However, the following qualifications matter:

| Claim | What the supplied script establishes |
|---|---|
| **0.81α for the production rule** | It computes a scalar stopping rule on fixed looks. It does not implement the production requirement that both tests permit stopping, or the actual irregular retained-product counts. |
| **0.844α for any stopping on the batch grid** | Its `adv` calculation targets the displayed grid \(200,400,\ldots,1800,1999\). Production looks with fewer completed products are not necessarily on this grid. |
| **0.89α for any stopping after any draw** | No every-draw calculation is present in the supplied script. The referenced additional scripts and outputs are absent. |

Shared stopping does not invalidate the universal crossing bound. It does mean that the scalar frozen-rule calculation is not a calculation of the actual shared stopping procedure, nor an established upper bound for it.

The displayed DP is appropriate for the fixed-grid crossing event. Truncation above \(K_{\max}=120\) is harmless if those counts cannot reject at any subsequent allowed sample size: cumulative counts cannot decrease.

But numerical quadrature is not an exact integral. For a rigorous numerical upper bound, one needs controlled integration error and a bound on the omitted tail. For the decreasing crossing integrand, for example,
\[
\int_h^1g_c(p)\,dp\le (1-h)g_c(h).
\]
Printing a tail endpoint alone does not constitute that certification.

Finally, a value rounded to **0.890** does not establish the literal inequality “≤0.89.” A certified upper bound or an upward-rounded constant is needed.

**5. The replacement sentence needs narrower wording and explicit assumptions.**

Its main overstatement is:

> “this has probability at most 0.89 times the threshold”

That sounds like a claim for arbitrary thresholds. The proposed Holm conclusion requires verification only at
\[
c\in\{0.05/j:j=1,\ldots,10\},
\]
but verification at those ten values does not establish a universal statement for every \(c\), or for arbitrary \(\alpha\).

The replacement is valid provided that:

- Each true null has a super-uniform baseline calibrated tail probability.
- Conditional on the observed data, its eligible baseline exceedances form an iid Bernoulli stream with that probability.
- Retention and availability preserve that stream model.
- Every terminal decision uses at most 1999 draws from that stream.
- Every rejection passes the stated CP upper-end gate.
- Variant aggregation is dominated by an included valid baseline as described above.
- The procedure stops rejecting at its first failed gate.
- The every-draw crossing probabilities have been bounded at **all ten required thresholds**, with numerical error accounted for.

A corrected sentence, **after the numerical bound has been certified**, would be:

> “A hypothesis is rejected only when the upper endpoint of its two-sided 95% Clopper–Pearson interval is below its Holm threshold. Assuming super-uniform baseline calibrated tail probabilities and conditionally iid pseudo-experiment exceedances, the probability of crossing this gate at any sample size up to 1999 is bounded by \(q c\) at each \(c=0.05/j\), \(j=1,\ldots,10\), where \(q\) is a verified numerical upper bound approximately equal to 0.89. The first-true-null Holm argument therefore gives FWER at most \(q\alpha\) for these ten tests at \(\alpha=0.05\), including adaptive budget stopping within this sampling model. No separate sequential validity is asserted for \((k+1)/(B+1)\).”

One additional statement should be corrected. The observed-count calculation
\[
P_{p=.005}(K_{1343}=0)\approx0.0012
\]
is a **fixed-sample likelihood calculation**. It is neither a conditional probability that an observed rejection is wrong nor an optional-stopping error bound. It cannot, alone, justify “at the observed counts the MC error is negligible.”

The structural any-stopping proof is sound. The exact **0.89α** constant remains numerically unverified from the supplied material; the tighter production-specific **0.81α** claim needs additional analysis.