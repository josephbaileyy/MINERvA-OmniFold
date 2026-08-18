# DETERMINATION — the anchor's confound: **KEEP `k = 0`, DECLARE IT, and the disposition is CONDITIONAL ON THE VERDICT'S DIRECTION**

**By:** lane C (PET), as `(B)`'s owner, on B's `j = 0` result. **There is a fourth option and it is the one
ruled.** Nothing spent, nothing submitted, `seed_offset_policy.py` untouched.

---

## 0. First, a correction to the premise — **it was flagged, in the ruling B is reproducing**

The dispatch says the predicate *"returned a result you did not flag."* `RULING-20260818` §1c, verbatim:

> *"**`k = 0` is EXEMPT and must be: it is dirty on two of the three ranges, and that is a property of the
> PUBLISHED ARCHIVE, not of the scan.** The exemption is the honest shape — the anchor differs structurally
> from every other member, this cannot be fixed without abandoning the anchor, and **it is a limitation of
> `M(ii)` to declare rather than a defect to repair.**"

**Both coincidences, the same two reasons, and the same conclusion.** Recorded because a determination built on
*"C missed this"* would route the next reader to the wrong document.

**What B genuinely added, and both are real:** *(1)* the **implementation** question — whether `build_plan`
enforces the predicate and how the exemption is expressed — which my §1c left as prose and which is a decision
rather than a default; and *(2)* **the sharper framing**, *is a spread measured against a confounded anchor
attributable?*, which my §1c answered by fiat (*"declare rather than repair"*) **without giving a reason.**
**§2 supplies the reason, and it is a better one than the fiat.** B was right not to set it as a default.

## 1. THE FOURTH OPTION EXISTS BECAUSE **THE SECOND ONE DOES NOT** — *"anchor differently"* is not available

> **A CLEAN ANCHOR IS NOT AN ANCHOR.** The anchor's entire function is that it reproduces the published product
> **exactly**. The published product HAS the two coincidences — production ran `--estimator-seed 1000` while
> throw 0's draw RNG is `default_rng(1000 + 0)`, and replica 42 draws Poisson weights from seed 42 with its
> estimator at 42. **So a run that lacks the coincidences is not the archive, and a run that reproduces the
> archive has them.** The confound and the anchoring are the same fact.

**Option 2 therefore does not cost a member — it costs the ANCHOR.** It yields a 49-member scan with no tie to
any published value, and `M(ii)` asks a question *about a published value*. **That is the one thing the design
cannot give up**, and it is why `(ii)` beat `(i)` in the first place: `(i)` was refused partly because
`S = 42` is not the archive. **Dropping `j = 0` re-imports the defect that ruling rejected.**

**Option 3 — *"rule the confound immaterial"* — is refused as stated**, because immateriality is a magnitude
claim and the magnitude is unmeasured. **§3 gives what is available instead: a bound, and a direction.**

## 2. THE RULING — **the DIRECTION is known even though the magnitude is not, and the direction decides it**

**Contaminating one member of an ensemble inflates the expected sample variance.** With `x_0 → x_0 + δ`, `δ`
independent of the offset structure and of variance `σ_δ²`:

```
E[s^2]  =  sigma^2  +  sigma_d^2 / n      >=  sigma^2
```

*(Simplified on lane A's key: `(1 − 1/n)/(n−1) = 1/n` identically — verified here at
`n = 2,3,6,20,50,100,1000`. **Same claim, and the simpler form makes the `1/n` scaling visible, which is why
`n = 6` is four times worse than `n = 50`.** A derived the whole result independently and confirmed all four
inflation figures by Monte Carlo over 200k trials.)*

> **So the anchor confound biases the measured `f` UPWARD — toward `UNMET`, AGAINST the negligibility claim
> the bar exists to test.** And that settles the disposition, because it is the opposite of the other bias in
> this measurement: **`c4(n)` biases the sd DOWNWARD, toward PASS, which is why §6 of the ruling requires it be
> corrected rather than declared.**
>
> **THE ASYMMETRY IS THE RULE: a bias toward the CONSERVATIVE verdict is DECLARABLE; a bias toward PASS must be
> CORRECTED.** A declared conservative bias cannot manufacture the answer anyone wants; an uncorrected
> pass-ward bias can. **This is the same asymmetry as `INCONCLUSIVE → NOT MET` in the ruling's §5, applied to a
> nuisance term instead of to a bound.**

**RULED, and the conditional is the substance of it.** ⚠ **THE CONDITIONAL IS NOW DISCHARGED IN BOTH BRANCHES BY MEASUREMENT — §3e. The table below is kept as written because it is the reasoning that made the measurement worth ordering, but the UNMET row's burden is MET:** the confound can move a decision boundary by `1.3 × 10⁻⁴` percentage points, so it cannot manufacture any verdict.

| verdict | disposition | why |
|---|---|---|
| **MET** | **STANDS**, with the confound declared and §3's bound quoted | The confound pushes `f` UP. A verdict of *small* reached **despite** an upward bias cannot have been manufactured by it. |
| **UNMET** | **NOT DECLARABLE until §3's two-step check is run** | Here the confound points the same way as the verdict, so it is a live alternative explanation. |
| **INCONCLUSIVE** | same as UNMET | Under §5 it resolves to NOT MET, so it inherits UNMET's burden. |

**Cost of the conditional: ZERO in the MET branch, and §3's check is zero-new-compute in the other two.** That
strictly dominates option 2 (which pays unconditionally *and* destroys the anchor) and option 3 (which is
indefensible in exactly the branch where it matters).

## 3. THE MAGNITUDE — a bound now, and a two-step check on products that ALREADY EXIST

**Bound, from §2's formula.** Percentage inflation of the measured sd — **exact for leg A (`f_agg`), and for
leg B (`f_med`) these are the CONSTANT-DISPLACEMENT case, which §3c proves is a FLOOR rather than a ceiling:**

| `σ_δ / σ` | `n = 6` | `n = 20` | **`n = 50`** | `n = 100` |
|---|---|---|---|---|
| **1.00** *(anchor displaced by the FULL per-member scatter)* | **8.01 %** | 2.47 % | **1.00 %** | 0.50 % |
| 0.50 | 2.06 % | 0.62 % | 0.25 % | 0.12 % |
| 0.25 | 0.52 % | 0.16 % | 0.06 % | 0.03 % |

> **⚠ THE ROW LABEL USED TO READ *"pessimistic"* AND THAT WAS WRONG FOR LEG B. Corrected on lane A's
> challenge — see §3c.** It is pessimistic in the displacement's SIZE and optimistic in its PATTERN, and only
> the first was stated. **The direction of the bias is unaffected, so the disposition in §2 does not move.**

> **At `n = 50`, a full-per-member-scatter displacement inflates the measured sd by `1.00 %` — twice `c4`'s
> `0.51 %` correction and in the safe direction.** *(And a fourth independent reason `n = 6` is the wrong grid: there the
> same confound is worth `8.01 %`, which would move a verdict on its own.)*

### 3a. ⚠ A CORRECTION TO MY OWN FIRST FRAMING OF THIS, CAUGHT BEFORE PUBLISHING — two different `σ`s

**My first draft closed the gap by pairing the bound above with an outlier test on the archive** (*is replica 42
unusual among the 100?*) and concluded *"the two arguments cover complementary regimes and leave no gap."*
**That was an asymmetric comparison — this lane's own most-repeated failure, and it nearly shipped inside a
document arguing about attributability:**

- the outlier test's `σ` is the **per-REPLICA scatter of one replica's contribution**;
- the inflation formula's `σ` is the **per-SCAN-MEMBER scatter of the block sum**.

**These differ by the LEVERAGE of one replica on the block sum — roughly `1/100` of `C_stat`'s share of a sum
that `C_syst` dominates.** Chaining them as if they were one quantity is the error, and the ratio is not a
detail: it is the whole conversion.

### 3b. So the check is TWO steps, and both are reads of existing products — **zero new compute**

1. **DISPLACEMENT, in replica units.** Rank replica 42's block contribution among the 100 in `boot_nd_5d`, and
   throw 0's among the 160 throw slabs. **Family-wise thresholds, so the test cannot fire on ordinary
   scatter:** flag at `|z| > 3.48` (100 draws, `α = 0.05`) / `|z| > 3.60` (160 draws). **The expected maximum
   `|z|` of `m` clean draws is `2.58` / `2.73`, which is the floor on what a one-member test can see** — stated
   because a test whose threshold sits below the clean maximum would flag something every time.
2. **LEVERAGE, converting step 1's units into scan-member units.** The sensitivity of the block sum to one
   replica and to one throw — `∂(block_sum)/∂(replica_i)`, computable from the same archived slabs.

**Only the PRODUCT of the two enters §3's table.** If step 1 finds replica 42 and throw 0 unremarkable, the
displacement is below the test's own resolution and step 2's leverage shrinks it further — **and the confound is
empirically immaterial for the price of reading files.** If step 1 flags either, we have learned the coincidence
matters, and that is worth knowing whatever the verdict.

**Both steps are cluster-side reads** (the products are on scratch — see §5), so they belong with `P-ANCHOR`
rather than being a second trip.

## 3c. AMENDMENT on lane A's second — **the median transfer, and my table's label was wrong**

**A asked the right question: §2's algebra is about a variance, and `f_med` is a MEDIAN over 285 bins. Does
*"inflates `E[s²]`"* survive that?** My §6-of-the-ruling argument for `c4` relied on the multiplier being
**uniform**, and this is not one. **A tested it; I re-tested it independently rather than take it on relay.**

**IT SURVIVES, AND FOR A DIFFERENT REASON THAN `c4` DOES — A's distinction, adopted:**

> **`c4` survives a median because it is UNIFORM. This survives because it is UNIVERSAL.** A median is robust
> to a **minority** of contaminated arguments; here the displaced member is displaced **in every bin at once**,
> because it is one run. **So there is no clean majority for the median to fall back on.** *(And that is why
> quoting `c4`'s reasoning here — which the first draft of §2 did implicitly — would have reached the right
> answer by the wrong route.)*

**Measured independently. `n = 50`, 285 bins, 4000 trials, seed `20260818` — and the script ships tracked as
[`mii_anchor_confound_mc.py`](mii_anchor_confound_mc.py), so these either reproduce or they do not
(`CONVENTION-receipt-ingredients.md`, `BEN-077`):**

| displacement pattern | `E[d_b²]` | `f_med` inflation, mine | A's | trials in the UP direction |
|---|---|---|---|---|
| constant `d_b/σ_b = 1` | 1.000 | **0.99 %** | 0.99 % | 0.995 |
| uniform `0…2` | 1.333 | **1.32 %** | *1.46 %* | 1.000 |
| half 0 / half 2 | 2.000 | **1.95 %** | 1.94 % | 1.000 |
| lognormal, mean 1 | 1.284 | **1.23 %** | *1.34 %* | 1.000 |

**A's conclusion is confirmed — `uniform 0…2` lands at `1.32 %`, exactly the `E[d²] = 4/3` prediction — and it is a correction to my table: every non-constant pattern inflates `f_med`
MORE than the constant one, so my four figures are NOT upper bounds on `f_med`.** Safe direction, disposition
unchanged, **label wrong** — fixed above.

### 3c-i. A labels the reordering *"a hypothesis from three sampled configurations"*. It is a THEOREM, and here it is

**The inflation is governed by `E[d_b²]/n`, not by the pattern's shape.** Tested over six patterns spanning
`E[d²] ∈ [0.33, 8]`:

```
pattern            E[d^2]   predicted sqrt(1+E[d^2]/n)-1   measured   ratio
uniform 0..1       0.3333            0.33%                   0.34%    1.026
constant 1         1.0000            1.00%                   0.99%    0.994
lognormal mean 1   1.2840            1.28%                   1.23%    0.966
uniform 0..2       1.3333            1.32%                   1.32%    0.997
half 0 / half 2    2.0000            1.98%                   1.95%    0.986
half 0 / half 4    8.0000            7.70%                   7.16%    0.930
```

> **Then Jensen closes it: at fixed mean displacement `E|d_b| = m`, `E[d_b²] ≥ m²` with equality IF AND ONLY IF
> `d_b` is CONSTANT.** So among all patterns with the same mean displacement, **the constant one minimises
> `E[d²]` and therefore minimises the inflation.** **The constant-displacement figures are a FLOOR** — which
> removes the need to sample configurations at all.
>
> **⚠ BUT THE FLOOR IS EXACT ONLY FOR LEG A, AND FOR LEG B IT NEEDS A PRECONDITION I OMITTED — see §3c-iii,
> where it is exhibited failing.** Corrected the same day it was written.

### 3c-ii. TWO OF A's FOUR FIGURES DID NOT REPRODUCE — **RESOLVED: same model, different realisation, no defect on either side**

**`uniform 0…2`: mine `1.31 %`, A's `1.46 %`. `lognormal`: mine `1.23 %`, A's `1.34 %`.** My MC standard error
is `0.007 %`, so these are not noise. **Constant (`0.99 %`) and half-half (`1.95 %`) match exactly.**

**RESOLVED by lane A, and my own benign hypothesis was WRONG.** I had guessed `σ_b` varying against an absolute
`d_b`. A ran exactly my model — `σ_b = 1` for every bin, `ε ~ N(0,1)` per bin, `d_b` added to member 0 — so that
explanation is closed. **The cause is the REALISED second moment:**

```
pattern                  A's realised E[d^2]   A meas   C meas   inflation at A's realised E[d^2]
uniform 0..2                          1.5015    1.46%    1.32%   1.49%   <- matches A
half 0 / half 2                       2.0070    1.94%    1.95%   1.98%   <- matches both
lognormal(-0.35, 0.8)                 1.6521    1.34%     n/a    1.63%   (see 3c-iii: a TAIL effect)
```

**Verified here: for 285 draws of `uniform(0,2)`, `sd(Ê[d²]) = 0.0706`, so A's `1.5015` is a `+2.38 σ` draw —
high, unremarkable, attainable.** And `1.49 %` is what the law gives at that realised moment, against A's
measured `1.46 %`. **Neither run has a defect.**

> **AND THE STRUCTURAL CAUSE IS SIMPLER THAN EITHER OF US SAID: A DREW ONE `d` ARRAY PER PATTERN AND HELD IT
> FIXED; MY SCRIPT REDRAWS IT EVERY TRIAL AND AVERAGES.** So A reports a single realisation and I report the
> expectation over realisations. That explains all four rows at once — A's half-half realised `2.0070` against a
> population `2.0000` and therefore agreed; its uniform realised `+2.4 σ` and therefore did not.
>
> **A's own diagnostic — *"the pattern that agrees is the DETERMINISTIC one, identical in both runs by
> construction"* — reaches the right conclusion by a reason that does not hold: in MY script `half 0 / half 2`
> is `np.where(rng.random(nb) < 0.5, …)`, i.e. randomly drawn, and its realised `E[d²]` has spread `±0.120`
> across trials — WIDER than `uniform(0,2)`'s `±0.071`, not tighter.** It agreed because both runs landed near
> the population value, not because either was deterministic. **A's conclusion is nevertheless established
> independently by the realised-moment arithmetic above, which needs no diagnostic at all.**

**AND THE FIX IS IN THE ARTIFACT, WHICH IS THE POINT.** `mii_anchor_confound_mc.py` now prints the **realised**
`E[d²]` and its spread beside every population value. **It cost A a hand reconstruction of a call order to find
this; it would have cost one glance.** *(A's note that my tracked-MC decision is what made the class visible is
accepted — and it cuts against me too: my own first draft's `0.0025 / −0.21 %` pair came from a scratch run at a
different stream position, which is the same defect one layer down.)*

### 3c-iii. ⚠ MY FLOOR OVER-CLAIMED, AND MY *"drift with `E[d²]`"* READING WAS A CONFOUND OF TWO AXES

**A's `lognormal` ratio of `0.82` at `E[d²] = 1.65` does not sit on my trend** — my table has `0.964` at `1.29`
and `0.986` at `2.00`. **So `0.82` is not "further along" my drift; it is a different axis.** Tested by matching
`E[d²]` at `1.65` and varying only the lognormal's `σ`:

```
sigma   E|d|     E[d^2]    pred    meas   ratio
  0.3  1.2288    1.6529   1.64%   1.63%   0.993
  0.5  1.1343    1.6544   1.64%   1.56%   0.954
  0.8  0.9333    1.6561   1.64%   1.30%   0.793   <- reproduces A's 0.82
  1.2  0.6256    1.6405   1.63%   0.81%   0.499
  1.6  0.3574    1.5250   1.51%   0.41%   0.274
```

> **At FIXED `E[d²]` the ratio spans `0.719`. So the ratio is set by the displacement pattern's CONCENTRATION,
> not by its second moment — and my *"drifts to `0.930` as `E[d²]` grows"* was an artifact of my six patterns
> happening to be ordered by BOTH axes.** A's number is confirmed *and* explained: `σ = 0.8` gives `0.793` here.

**AND THE SAME MECHANISM BREAKS MY FLOOR. Exhibited, all patterns at `E|d_b| = 1` EXACTLY and deterministic:**

```
pattern (E|d|=1)          E[d^2]   f_agg pred   f_med meas
constant 1                 1.000        1.00%        0.98%   <- the claimed floor
half 0 / half 2            1.993        1.97%        1.92%   above
1 bin in 5 at 5            5.000        4.88%        2.93%   above
1 bin in 20 at 20         21.053       19.21%        0.70%   BELOW  <-- FLOOR VIOLATED
1 bin in 285 at 285      285.000      158.84%        0.05%   BELOW  <-- FLOOR VIOLATED
```

> **So Jensen's ordering is EXACT for `f_agg` — it is a statement about `E[d²]` and `f_agg` is a function of
> `E[d²]` — and CONDITIONAL for `f_med`: it requires the displacement to reach a MAJORITY OF BINS. Concentrate
> the same mean displacement into a minority and the median becomes robust to it and lands BELOW the constant
> case, with `E[d²]` of 285 and an inflation of `0.05 %`.**
>
> **THAT PRECONDITION IS EXACTLY A's UNIVERSALITY CONDITION, WHICH IS WHY THE CORRECTION IS A's WIN AND NOT
> MINE.** I built a theorem on top of A's mechanism and dropped the mechanism's hypothesis on the way. **It
> APPLIES to this campaign's case for a PHYSICAL reason, not a mathematical one: one perturbed bootstrap replica
> moves the whole unfolded spectrum, not one cell.** A theorem plus a physical fact, and the second is the part
> a later lane would forget.

### 3c-iv. So A's *"the Jensen result retires my contribution"* is WRONG, and the record should say so

**A asked that its contribution be recorded as retired. It is not, and over-claiming against oneself corrupts
the record in the same way as over-claiming for oneself.**

> **Jensen ORDERS patterns by `E[d²]`. It says nothing whatever about whether a MEDIAN inflates at all** — and
> §3c-iii shows the ordering itself fails for `f_med`. **A's MC established that the direction survives the
> median. That result is load-bearing for leg B, is not derivable from Jensen, and supplied the precondition my
> theorem needed.**
>
> **What Jensen retires is one sub-claim — *"non-constant inflated more in three sampled configurations"* — and
> only within the majority-of-bins regime.** A's framing traded a live result for a retired one. **The
> arrangement is the reverse: A's mechanism is the foundation and my theorem is the conditional refinement on
> top of it.**

## 3d. THE ASYMMETRY, in A's general form — **adopted verbatim, with its condition**

> **A bias is DECLARABLE when its sign is certain and points toward the stricter verdict; it must be CORRECTED
> when its sign is certain and points toward the lenient one; and when its sign is UNCERTAIN it must be BOUNDED
> before any verdict is read.**

**Both of §2's cases depend on the sign being CERTAIN rather than estimated** — here `σ_δ² ≥ 0` for every
realisation, so the increment cannot reverse. **The third case does not arise here, and naming it is what makes
the first two a RULE instead of a pair of decisions.** *(A's, and it is better than my two-case form.)*

### 3d-i. But the sign is certain **in EXPECTATION**, not per realisation — and here is why that is subsumed

**`E[s²]` inflates; a single realised `s` can still fall below its uncontaminated value.** If that happened, a
`MET` could in principle be partly manufactured by the confound. **Measured, constant pattern, `n = 50`, 4000
trials:**

```
P(the confound pushes f_med DOWN) = 0.0055      worst downward excursion seen = -0.33%
percentiles of the inflation: 0.5% -> -0.01%   2.5% -> +0.26%   50% -> +0.98%   97.5% -> +1.73%
```

*(From the tracked script. An earlier draft of this section quoted `0.0025` and `-0.21%` from a scratch run
whose RNG stream was consumed in a different order — same seed, different draws. **The document now quotes the
version that ships**, which is the only one a reader can check.)*

> **And the margin the decision actually has at `n = 50` is `16.8 %`** — leg B's `MET` threshold is `2.28 %`
> against a `2.74 %` bar. **A sub-`1 %` realisation excursion cannot move a verdict across a `16.8 %` gap**, so
> the caveat is real, stated, and already covered by the bound §2 requires be quoted. **`MET → STANDS` is
> unaffected, and A's reading of it is right: it is the strongest branch precisely because it needs no magnitude
> at all.**

## 3e. **THE CHECK RAN. Both legs NULL, and the conditional of §2 is DISCHARGED — UNCONDITIONALLY, which I did not expect**

**Batch `57215459`, 1 m 34 s, `EXIT=0`, no flags.** B's script unmodified, run by the mediator against the
repo's own product trees. **Family sizes are the specified ones — `m = 100` and `m = 160` — so the printed
thresholds ARE the test §3b specified**, which was B's open caveat and does not arise.

### 3e-i. Step 1, displacement: both coincidence sites are not merely un-flagged, they are TYPICAL

| site | `max|z|` | flag at | expected max of `m` clean | more central than |
|---|---|---|---|---|
| replica 42 | **`0.3090`** | 3.48 | 2.58 | **`24.3 %`** of clean draws |
| throw 0 | **`0.7336`** | 3.60 | 2.73 | `53.7 %` of clean draws |

> **A clean normal draw has median `|z| = 0.6745`. So replica 42 sits BELOW the median `|z|` of its own family
> and throw 0 barely above it.** Neither is an outlier on any reading, let alone at the family-wise threshold.
> **This is the branch §3b named: *"if replica 42 and throw 0 are unremarkable, the displacement is below the
> test's own resolution and the leverage shrinks it further."***

*(`statistics_agree` is set on SIGN only — the weaker predicate, as B flagged. Here the magnitudes agree too:
`z_total_xsec = −0.3090` against `z_deviation_norm = −0.2426` for replica 42, and the two coincide at `−0.7336`
for throw 0. **So the choice of summary statistic is not load-bearing and needs no ruling** — recorded because
the mediator surfaced the flag as weak rather than letting it stand as strong.)*

### 3e-ii. Step 2, the conversion — **and it is the whole content, exactly as §3a said**

```
replica 42   z x relative_leverage = 0.3090 x 6.9815e-04 = 2.1570e-04
throw 0      z x relative_leverage = 0.7336 x 2.8052e-03 = 2.0580e-03
                        combined, independent (quadrature)  delta = 2.0693e-03
                        combined, perfectly correlated      delta = 2.2737e-03
```

**The two sit in DIFFERENT legs — `C_stat` and `C_syst` — driven by different streams, so independence is the
expected case; the correlated value is carried as the bracket** because a correlation nobody measured should not
be assumed away. **It changes nothing below: the bracket is `10 %` wide on `δ` and the conclusion has four
orders of margin.**

### 3e-iii. ⚠ AND THE ANSWER IS *f*-INDEPENDENT, WHICH IS STRONGER THAN THE CONDITIONAL I WROTE

**I expected to have to say *"immaterial provided `f` is not tiny."* The quadrature form removes the proviso:**

```
f_obs^2 = f^2 + delta^2/n      delta^2/n = 8.5638e-08      <- no f in it
```

| | leg B (`2.74 %`) | leg A (`4.15 %`) |
|---|---|---|
| confound's share of `bar²` | **`0.01141 %`** | `0.00497 %` |
| effective bar | `2.7400 % → 2.7398 %` | `4.1500 % → 4.1499 %` |
| shift of the `n = 50` UNMET boundary | **`1.3 × 10⁻⁴` percentage points** | — |
| shift of the `n = 50` MET boundary | `1.9 × 10⁻⁴` percentage points | — |

> **`δ²/n` carries no `f`, so the confound's contribution to `f_obs²` is a CONSTANT. The verdict cannot be
> manufactured at ANY value of `f`** — not "provided `f` is large," which is what §2's UNMET row was hedging
> against. **Expressed in the units of §3's table: the measured `δ` is `σ_δ/σ = 0.0755` at the bar, giving
> `0.0057 %` inflation against the `1.00 %` the pessimistic row used — a factor of `175` below it.**

> **AND THE LEG-B STEP RESTS ON THE CLAIM I DOWNGRADED THIS MORNING, which is the pleasing part.** Quadrature is
> exact for `f_agg` and only approximate for `f_med` — and §3c-iii measured the direction of that approximation:
> **the `f_agg` form OVER-estimates `f_med`'s inflation in every regime tested (ratios `≤ 1`).** So applying it
> to leg B is conservative. **The result whose over-reach cost me a theorem is what licenses using its formula
> here.**

### 3e-iv. WHAT I ASK FOR INSTEAD OF AN INDEPENDENT RE-RUN

**The mediator flags that it ordered the run and is not an independent party to it, and offers a re-run by a
lane that did not. I decline that and ask for something cheaper and stronger.**

> **A null is the CONVENIENT result here, and re-running the same script with a different hand does not test the
> thing that matters: whether the instrument CAN fire.** `EXIT=0, FLAGS: none` is produced identically by *"no
> displacement"* and by *"a check that cannot detect one."*
>
> **ASKED: a POSITIVE CONTROL. Inject a synthetic displacement into replica 42's slab — `5 σ` of the replica
> scatter — and require `max|z| > 3.48` and a non-null flag.** Then the null means what it says. **This is the
> standing rule that a filter needs a test in the direction it acts, and it is the fourth time today it has been
> the right ask.** *(Independence of the runner is worth much less than falsifiability of the instrument: I can
> read the script, and I cannot read a `FLAGS: none` that was never able to be anything else.)*

**Disposition: with a passing positive control, `M(ii)`'s anchor confound is EMPIRICALLY IMMATERIAL and the
declaration in §2 becomes a footnote with a number attached rather than a live caveat. Without one, the null is
un-interpretable and §2's conditional stays live.** Nothing else in this determination changes.

## 4. `build_plan` — **WIRE THE PREDICATE, and express the exemption as a COINCIDENCE ALLOWLIST, not as `j != 0`**

**Wire it.** B is right that wiring it un-exempted would make the driver refuse the ruled grid, and right not
to choose. **The choice is:**

> **The exemption names the TWO KNOWN COINCIDENCES — `(g1, bootstrap[1,100])` and `(g2, uthrow[1000,1159])`,
> each with where it was measured — and permits those two and nothing else. It does NOT skip member `0`.**

> **⚠ AS WRITTEN THIS KEY LEAKS, AND B FOUND IT. RULED IN B's FAVOUR — see §4a. The key must carry the SEED
> VALUE and the OFFSET too.** A `(group, range)` key is matched by any `k` that lands that group in that range,
> and non-zero such `k` exist: `42 + 58 = 100 ∈ [1,100]` and `1000 + 159 = 1159 ∈ [1000,1159]`. **So my
> allowlist would have exempted members `k = 58` and `k = 159` — an under-specified predicate passing the case
> it was written to reject, which is `BEN-405`'s shape for the third time in this thread and the second time
> inside a guard I wrote against it.**

**The difference is the only thing that makes the guard worth wiring.** A `j != 0` skip passes *any* coincidence
at the anchor, including one introduced later by widening an array or adding a leg. **An allowlist of two
FAILS the moment a third appears** — and a third appearing is exactly the event nobody would otherwise notice,
because the anchor is the member everyone has already agreed is special.

> **This is *a filter needs a test in the direction it acts*: the exemption is a NARROWING, so it gets a test
> that it does NOT fire — a fixture with a third coincidence at `j = 0` that the predicate must still reject.**
> Without that test, widening the exemption later looks free.

## 4a. RULING on B's `(group, range, SEED VALUE)` narrowing — **ADOPTED, and I add a fourth conjunct**

**B is right and my `(group, range)` key was defective.** Adopted:

> **KEY: `(group, range, seed value, k == 0)`. All four. The exemption fires only for
> `(g1, bootstrap[1,100], 42, k=0)` and `(g2, uthrow[1000,1159], 1000, k=0)`.**

**Why the seed value closes the leak:** `42 + k = 42` only at `k = 0`, and `1000 + k = 1000` only at `k = 0`, so
pinning the value pins the anchor **given the current baselines** — and if a baseline ever moves, the exemption
becomes unreachable and the predicate FAILS at the anchor, **which is the correct behaviour: a changed baseline
means a new archive whose coincidences must be re-derived, not inherited.**

**Why I add `k == 0` on top, even though it is redundant today:** the value-pins-the-anchor argument *depends on
the baselines*. If `g1`'s baseline ever became `1000`, then `(g1, …, 42)` would be reachable at `k = −958`.
**Contrived, and the conjunct costs one term and one test.**

> **THE GENERAL RULE, and it is what both of my defective versions violated: AN EXEMPTION'S KEY MUST CARRY EVERY
> COORDINATE THAT MAKES IT LEGITIMATE.** This one is legitimate because *this group*, in *this range*, at *this
> seed value*, at *the anchor*. **Four facts, four conjuncts. A redundant conjunct in a NARROWING fails safe —
> which is the opposite of a redundant conjunct in a widening, and is why the asymmetry is worth stating rather
> than trimming to the minimal sufficient key.**

**And this is NOT the `j != 0` skip I refused:** a skip is `k == 0` ALONE. The conjunction with three other
terms means a third coincidence appearing at the anchor still fails the predicate, which was the whole point.

**B's two leak assertions stand either way and should be kept** — they are tests of the narrowing in the
direction it acts, which is what makes the fourth conjunct cheap to add rather than an act of faith.

## 5. B's implementation notes, and its sharpening — **accepted, one of them against my own text**

- **Range table with per-entry provenance, never a threshold: ADOPTED.** And the test that a caller-supplied
  range changes the answer is the right guard — it is what stops the table being decorative.
- **The PET-family band ABSENT AND NAMED AS ABSENT is the correct call and I withdraw any implication
  otherwise.** My ruling checked `[50000, 50049]` and said so; **B has not measured it, and an unmeasured range
  in a provenance-carrying table is worse than a named hole.** *(Consequence worth stating: `k = 2000`'s failure
  is therefore currently un-caught. It is not the ruled grid, so nothing is exposed — but a later lane widening
  the step needs the band measured first, and that is a task, not a caveat.)*
- **B's sharpening, accepted verbatim: *"the anchor is free" and "the anchor is clean" are different claims and
  only the first was established.*** Both appear in my ruling — freeness in §3, dirtiness in §1c — **separately,
  with neither leaning on the other**, so no argument of mine used the conflation. **But the distinction is
  worth being explicit and B is right that the `(ii)`-over-`(i)` cost argument rests on freeness alone**, which
  is all cost needs. **And per `P-ANCHOR`, freeness is not established either yet.**

## 6. `P-ANCHOR` — **unanswered, and the consequence of failure is worse than one member**

**B refuses to report it as a pass, correctly.** All six archived product paths are absent from the checkout and
untracked (scratch), and of the tracked receipt evidence only `receipt_construction_contract_5d.json` covers a
leg (`uq_5d/unified_throw_cov_5d.root`) — **`boot_nd_5d`, `seedscan_split_5d` and `universe_sweep` are named by
no tracked receipt. One leg of four.**

> **And the failure mode is not *"the anchor costs a member."* By §1, THERE IS NO CLEAN ANCHOR TO BUY.** If the
> archive's products cannot be read, the anchor must be **re-produced** — which reproduces its coincidences,
> because they are the archive's — **so a failed `P-ANCHOR` costs a member AND leaves the confound exactly where
> it was.** The conditional in §2 is unaffected; the pricing is not. **Every figure in the ruling's §3 moves up
> one member, as stated there.**

## 7. Ceiling versus allocation — **they bind on DIFFERENT AXES, both readings are true, and neither supersedes**

| `n` | GPU node-h | % of remaining GPU | CPU node-h | % of remaining CPU |
|---|---|---|---|---|
| 6 | 49.1 | 0.08 % | 108.1 | 2.70 % |
| 20 | 186.4 | 0.29 % | 410.8 | 10.25 % |
| **50** | **480.7** | **0.75 %** | **1,059.4** | **26.42 %** |

*(B's fresh figures: 9.81 GPU node-h and 21.62 CPU node-h per member; 64,119.5 GPU and 4,009.1 CPU node-hours
remaining.)*

> **Joseph's CEILING binds on GPU** — `200 / 39.223` → 6 members — **and the REMAINING ALLOCATION binds on
> CPU**, where `n = 50` is `26.4 %` against `0.75 %` on GPU. **A ceiling and an allocation are different
> objects.** My ruling's §3 framed GPU as binding because **that is the axis Joseph's number is denominated in
> and he is the one deciding**; B's framing is the right one for what the campaign can absorb. **Both belong in
> what goes to him: he is approving a ceiling, and the thing being consumed is CPU.**

## 8. Scope

- **RULED: `k = 0` stays in the grid; the confound is DECLARED; the disposition is CONDITIONAL on the verdict's
  direction** (§2). MET stands; UNMET/INCONCLUSIVE requires §3b first.
- **RULED: `build_plan` wires the predicate with a two-entry coincidence ALLOWLIST**, plus the narrowing test
  that it does not fire (§4). **B implements — its module.**
- **REFUSED: option 2** (no clean anchor exists) **and option 3 as stated** (immateriality is a magnitude claim;
  §3 gives a bound and a direction instead).
- **CORRECTED, mine, before publishing: §3a's two `σ`s.** The outlier test and the inflation bound are in
  different units and the leverage between them is the whole conversion.
- **NOT RULED: `P-ANCHOR`.** A cluster-side read, B's to report, and §6 states what a failure costs.
- **AMENDED on lane A's second (`BEN-444`, `2254be5c`):** the algebra simplified to `σ² + σ_δ²/n`; the
  median transfer argued from UNIVERSALITY rather than from `c4`'s uniformity; **my table relabelled — the
  figures are a FLOOR on `f_med`, not a ceiling**; A's three-case asymmetry adopted verbatim; the
  reordering upgraded from hypothesis to theorem by Jensen; and two of A's four MC figures reported as
  NOT reproducing, with the conclusion unaffected (§3c-ii).
- **AMENDED AGAIN, 2026-08-18, and TWO OF THE THREE ARE CORRECTIONS TO ME:** the eight-number
  disagreement is RESOLVED (A drew one `d` array and held it; I redraw per trial — A's `uniform(0,2)`
  realised a `+2.4 σ` second moment, and **my own benign hypothesis about `σ_b` was wrong**); **my
  Jensen floor over-claimed** and is conditional on A's universality hypothesis for `f_med`, exhibited
  failing in §3c-iii; **my *"drift with `E[d²]`"* reading was a two-axis confound** and the ratio is a
  concentration effect; and **A's claim that Jensen retires its own contribution is refused** (§3c-iv).
- **§2's CONDITIONAL DISCHARGED by measurement (§3e), and UNCONDITIONALLY**: `δ²/n = 8.56e-8` carries no
  `f`, so the confound shifts a decision boundary by `1.3e-4` percentage points at any `f`. **Contingent
  on a POSITIVE CONTROL (§3e-iv), which I ask for in preference to an independent re-run.**
- **RULED for B on the allowlist key (§4a): `(group, range, seed value, k == 0)`.** My `(group, range)`
  form leaked at `k = 58` and `k = 159` — B found it, and it is `BEN-405`'s shape inside my own guard
  against `BEN-405`'s shape.
- **AUTHORIZED: nothing.** §3b is a read of existing products and needs no grant; everything else is still
  Joseph's.

*Second sought: B on §4's allowlist and on whether §3b's two steps are readable from the archived slabs as they
stand; A on §2's direction argument, which is the load-bearing claim here and is one line of algebra that either
holds or does not.*
